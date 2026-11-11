"""Lõi điều phối máy quét `ViScanner` cho `vi_scanner`."""

from __future__ import annotations

import collections
import json
import re as stdlib_re
import time
from typing import TYPE_CHECKING, ClassVar

from _vi_algo_rules import (
    is_linguistically_exempt,
    is_profile_exempt,
    run_bold_colon_list_rule,
    run_lengthy_and_roundabout_rule,
    run_loanword_and_jargon_rule,
    run_monotony_rule,
)
from _vi_docx_dhdna import compute_sliding_mattr, compute_stylometry
from _vi_hygiene_rules import run_document_and_table_hygiene
from _vi_masker import (
    SemanticMasker,
    _extract_regex_anchors,
    build_scan_buffer,
    line_end_offset,
    make_finding,
    offset_to_line_col,
)
from _vi_rules_data import (
    DEFAULT_GRAMMAR_CSV,
    DEFAULT_VOCAB,
    DEFAULT_VOCAB_CSV,
    build_default_rules,
    check_loanwords_maintenance,
    load_rule_bundle,
    load_vocab_catalog,
)
from _vi_types import (
    ALL_PROFILES,
    SCHEMA_VERSION,
    VERSION,
    Finding,
    Profile,
    RuleDefinition,
    ScanReport,
    Severity,
    ThresholdSpec,
    VocabCatalog,
    _CompiledRegex,
    _RegexMatch,
    _ScanBuffer,
    compile_rule_regex,
)

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence
    from pathlib import Path

_BRIDGE_NEGATION_RE = stdlib_re.compile(
    r"(?i)\b(?:chưa\s+đồng nghĩa\s+với|không\s+đồng nghĩa\s+với|"
    r"không\s+có\s+nghĩa\s+là|không\s+phải\s+là\s+hai\s+cực\s+đối\s+lập)\b"
)
_DECIMAL_COMMA_RE = stdlib_re.compile(r"(?<=\d),(?=\d)")
_ALGO_RUNNERS: dict[str, Callable[[RuleDefinition, _ScanBuffer, Profile | None], list[Finding]]] = {
    "ALGO:BOLD_COLON_LIST_STREAK_MIN_3": run_bold_colon_list_rule,
    "ALGO:PARAGRAPH_CV_AND_OPENING_MONOTONY": run_monotony_rule,
    "ALGO:LOANWORD_AND_FOREIGN_TOKEN_CHECK": run_loanword_and_jargon_rule,
    "ALGO:DOCUMENT_AND_TABLE_HYGIENE": run_document_and_table_hygiene,
    "ALGO:LENGTHY_AND_ROUNDABOUT_SENTENCE": run_lengthy_and_roundabout_rule,
}


def _select_triggered_matches(
    valid_matches: Sequence[_RegexMatch],
    para_spans: Sequence[tuple[int, int, str]],
    word_count: int,
    thresh: ThresholdSpec,
) -> list[_RegexMatch]:
    """Lọc kết quả vượt ngưỡng bằng thuật toán hai con trỏ tuyến tính O(P + M)."""
    if thresh.per_para is not None:
        triggered: list[_RegexMatch] = []
        m_idx = 0
        n_matches = len(valid_matches)
        for p_start, p_end, _ in para_spans:
            while m_idx < n_matches and valid_matches[m_idx].start() < p_start:
                m_idx += 1
            start_idx = m_idx
            while m_idx < n_matches and valid_matches[m_idx].start() < p_end:
                m_idx += 1
            if (m_idx - start_idx) >= thresh.per_para:
                triggered.extend(valid_matches[start_idx:m_idx] if thresh.per_para == 1 else [valid_matches[start_idx]])
        if (
            not triggered
            and thresh.per_1000_words is not None
            and word_count >= 250
            and (len(valid_matches) * 1000.0 / word_count) >= thresh.per_1000_words
        ):
            triggered.append(valid_matches[0])
        return triggered
    if thresh.per_doc is not None:
        if len(valid_matches) >= thresh.per_doc:
            return list(valid_matches) if thresh.per_doc == 1 else [valid_matches[0]]
        return []
    return list(valid_matches)


def _prepare_rule_target_text(rid: str, buf: _ScanBuffer) -> str:
    target_text = buf.masked_no_code if rid == "VIS-AI-002" else buf.masked_prose
    if rid == "VIS-FMT-003" and "—" in target_text:
        return "\n".join((" " * len(ln)) if ln.lstrip().startswith("—") else ln for ln in target_text.splitlines())
    if rid == "VIS-FMT-004" and "," in target_text:
        return _DECIMAL_COMMA_RE.sub(".", target_text)
    return target_text


def _build_regex_findings(
    rule: RuleDefinition,
    buf: _ScanBuffer,
    triggered: Sequence[_RegexMatch],
    phrase_hints: dict[tuple[str, str], str],
) -> list[Finding]:
    rid = rule.rule_id
    findings: list[Finding] = []
    seen_lines: set[int] = set()
    last_line_end = -1
    for tm in triggered:
        if tm.start() <= last_line_end:
            continue
        last_line_end = line_end_offset(buf.raw_text, tm.start(), buf.nl_offsets)
        ln_no, _ = offset_to_line_col(buf.raw_text, tm.start(), buf.nl_offsets)
        if ln_no in seen_lines:
            continue
        seen_lines.add(ln_no)
        raw_slice = buf.raw_text[tm.start() : tm.end()].strip()
        override_profs: Sequence[str] | None = (
            ("general", "marketing", "social_media", "translation")
            if rid == "VIS-FMT-003" and raw_slice == ";"
            else None
        )
        hint = phrase_hints.get((rid, " ".join(raw_slice.split()).casefold()))
        findings.append(
            make_finding(rule, buf, tm.start(), raw_slice, custom_suggestion=hint, override_profiles=override_profs)
        )
    return findings


class ViScanner:
    """Máy quét câu chữ tiếng Việt v2.2.0 (mặc định `profile="all"` xuất đủ 100% tín hiệu của 7 nhóm)."""

    VERSION: ClassVar[str] = VERSION
    SCHEMA_VERSION: ClassVar[str] = SCHEMA_VERSION
    DISCLAIMER: ClassVar[str] = (
        "Công cụ vi_scanner chỉ chỉ ra các vị trí câu chữ máy móc, sáo rỗng, dịch sát hoặc dài dòng "
        "cần người viết đọc lại. Kết quả này KHÔNG suy đoán tác giả và KHÔNG kết luận văn bản do AI tạo ra."
    )

    _offset_to_line_col = staticmethod(offset_to_line_col)
    _line_end_offset = staticmethod(line_end_offset)
    _compute_sliding_mattr = staticmethod(compute_sliding_mattr)
    compute_stylometry = staticmethod(compute_stylometry)

    def __init__(
        self,
        rules: list[RuleDefinition] | None = None,
        extra_rules: list[RuleDefinition] | None = None,
        *,
        vocab_path: Path | None = None,
        grammar_path: Path | None = None,
    ) -> None:
        if rules is not None:
            merged = list(rules)
            self.vocab: VocabCatalog = load_vocab_catalog(vocab_path) if vocab_path is not None else DEFAULT_VOCAB
        elif vocab_path is not None or grammar_path is not None:
            merged, self.vocab = load_rule_bundle(vocab_path or DEFAULT_VOCAB_CSV, grammar_path or DEFAULT_GRAMMAR_CSV)
        else:
            merged = build_default_rules()
            self.vocab = DEFAULT_VOCAB
        if extra_rules:
            merged.extend(extra_rules)
        self.rules: dict[str, RuleDefinition] = {r.rule_id: r for r in merged if r.status == "active"}
        self._compiled: dict[str, _CompiledRegex] = {
            rid: compile_rule_regex(rule.regex_or_algorithm)
            for rid, rule in self.rules.items()
            if not rule.regex_or_algorithm.startswith("ALGO:")
        }
        self._rule_anchors: dict[str, tuple[str, ...]] = {
            rid: ((*anchors, "chưa") if rid == "VIS-RHET-001" and anchors else anchors)
            for rid, rule in self.rules.items()
            if not rule.regex_or_algorithm.startswith("ALGO:")
            for anchors in (_extract_regex_anchors(rule.regex_or_algorithm),)
        }

    @classmethod
    def load_custom_rules(cls, path: Path) -> list[RuleDefinition]:
        raw_data = json.loads(path.read_text(encoding="utf-8-sig"))
        items = raw_data if isinstance(raw_data, list) else raw_data.get("rules", [])
        out: list[RuleDefinition] = []
        for idx, entry in enumerate(items, 1):
            profs_raw = entry.get("profiles")
            profs = frozenset(Profile(p) for p in profs_raw) if profs_raw else frozenset(ALL_PROFILES)
            out.append(
                RuleDefinition(
                    rule_id=str(entry.get("rule_id") or f"CUSTOM-{idx:03d}"),
                    category=str(entry.get("category") or "CUSTOM"),
                    pattern_type="regex",
                    description_vi=str(entry["description_vi"]),
                    regex_or_algorithm=str(entry["regex"]),
                    severity=Severity(entry.get("severity", "warning")),
                    weight=float(entry.get("weight", 0.6)),
                    profiles=profs,
                    threshold=ThresholdSpec.parse(str(entry.get("threshold", "1/doc"))),
                    exceptions=(),
                    bad_example=str(entry.get("bad_example", "")),
                    better_example=str(entry.get("better_example", "")),
                    source_url=str(entry.get("source_url", "custom")),
                    evidence_strength=str(entry.get("evidence_strength", "custom")),
                )
            )
        return out

    def _collect_valid_regex_matches(
        self,
        rule: RuleDefinition,
        target_text: str,
        nl_offsets: Sequence[int],
        prof: Profile | None,
    ) -> list[_RegexMatch]:
        rid = rule.rule_id
        thresh = rule.threshold
        single_hit_per_line = (thresh.per_para == 1 and thresh.per_1000_words is None) or thresh.per_doc == 1
        text_len = len(target_text)
        valid_matches: list[_RegexMatch] = []
        valid_line_end = -1
        for m in self._compiled[rid].finditer(target_text):
            if single_hit_per_line and m.start() <= valid_line_end:
                continue
            if not is_linguistically_exempt(rid, target_text, m.start(), m.end()) and not is_profile_exempt(
                rid, target_text, m.start(), m.end(), prof
            ):
                valid_matches.append(m)
                if single_hit_per_line:
                    valid_line_end = line_end_offset(target_text, m.start(), nl_offsets)
                    if valid_line_end >= text_len - 1:
                        break
        return valid_matches

    def _scan_regex_rule(self, rule: RuleDefinition, buf: _ScanBuffer, prof: Profile | None) -> list[Finding]:
        rid = rule.rule_id
        anchors = self._rule_anchors.get(rid, ())
        if anchors:
            lower_haystack = buf.masked_no_code_lower if rid == "VIS-AI-002" else buf.masked_prose_lower
            if not any(sub in lower_haystack for sub in anchors):
                return []
        target_text = _prepare_rule_target_text(rid, buf)
        valid_matches = self._collect_valid_regex_matches(rule, target_text, buf.nl_offsets, prof)

        if rid == "VIS-RHET-001" and not valid_matches:
            bridge_hits = list(_BRIDGE_NEGATION_RE.finditer(target_text))
            if len(bridge_hits) >= 3:
                first_b = bridge_hits[0]
                return [
                    make_finding(
                        rule,
                        buf,
                        first_b.start(),
                        buf.raw_text[first_b.start() : first_b.end()].strip(),
                        custom_suggestion=(
                            "Lặp quá nhiều cụm phủ định bắc cầu ('chưa đồng nghĩa với', 'không có nghĩa là'); "
                            "hãy đổi sang câu khẳng định trực tiếp."
                        ),
                    )
                ]
            return []
        if not valid_matches:
            return []

        triggered = _select_triggered_matches(valid_matches, buf.para_spans, buf.word_count, rule.threshold)
        return _build_regex_findings(rule, buf, triggered, self.vocab.phrase_hints)

    def _run_rule(self, rule: RuleDefinition, buf: _ScanBuffer, prof: Profile | None) -> list[Finding]:
        if rule.regex_or_algorithm == "ALGO:LOANWORD_AND_FOREIGN_TOKEN_CHECK":
            return run_loanword_and_jargon_rule(rule, buf, prof, self.vocab)
        algo_runner = _ALGO_RUNNERS.get(rule.regex_or_algorithm)
        return algo_runner(rule, buf, prof) if algo_runner is not None else self._scan_regex_rule(rule, buf, prof)

    def prepend_docx_title_mismatch(
        self, report: ScanReport, raw_text: str, core_title: str, mismatch_note: str
    ) -> None:
        """Gắn cảnh báo lệch thuộc tính Title của tệp `.docx` lên đầu báo cáo và cập nhật chỉ số."""
        finding = make_finding(
            self.rules["VIS-STRUCT-002"],
            build_scan_buffer(raw_text),
            0,
            core_title or "docProps/core.xml",
            custom_suggestion=mismatch_note,
        )
        report.findings.insert(0, finding)
        report.findings_count = len(report.findings)
        report.error_count = sum(1 for f in report.findings if f.severity == Severity.ERROR.value)
        report.warning_count = sum(1 for f in report.findings if f.severity == Severity.WARNING.value)
        report.info_count = sum(1 for f in report.findings if f.severity == Severity.INFO.value)
        report.findings_per_1000_words = round((len(report.findings) / max(report.word_count, 1)) * 1000, 2)
        report.weighted_density_score = round(sum(f.weight for f in report.findings), 3)
        report.category_breakdown = dict(collections.Counter(f.category for f in report.findings))

    def scan_text(
        self,
        text: str,
        profile: Profile | str = "all",
        active_rule_ids: set[str] | None = None,
    ) -> ScanReport:
        t0 = time.perf_counter()
        prof: Profile | None = (
            None
            if str(profile).lower() == "all"
            else (profile if isinstance(profile, Profile) else Profile(str(profile)))
        )
        buf = build_scan_buffer(text)
        findings: list[Finding] = []
        for rid, rule in self.rules.items():
            if (active_rule_ids is not None and rid not in active_rule_ids) or (
                prof is not None and prof not in rule.profiles
            ):
                continue
            findings.extend(self._run_rule(rule, buf, prof))
        findings.sort(key=lambda f: (f.line, f.col, f.rule_id))
        elapsed_ms = round((time.perf_counter() - t0) * 1000, 3)
        prose_only = "\n".join(
            ln for ln in buf.masked_full.splitlines() if not (ln.strip().startswith("|") and ln.strip().endswith("|"))
        )
        return ScanReport(
            schema_version=self.SCHEMA_VERSION,
            scanner_version=self.VERSION,
            profile="all" if prof is None else prof.value,
            word_count=buf.word_count,
            paragraph_count=len(buf.para_spans),
            findings_count=len(findings),
            error_count=sum(1 for f in findings if f.severity == Severity.ERROR.value),
            warning_count=sum(1 for f in findings if f.severity == Severity.WARNING.value),
            info_count=sum(1 for f in findings if f.severity == Severity.INFO.value),
            findings_per_1000_words=round((len(findings) / buf.word_count) * 1000, 2),
            weighted_density_score=round(sum(f.weight for f in findings), 3),
            category_breakdown=dict(collections.Counter(f.category for f in findings)),
            elapsed_ms=elapsed_ms,
            maintenance_due=check_loanwords_maintenance()["due_for_quarterly_review"],
            disclaimer=self.DISCLAIMER,
            semantic_invariants_summary={k: len(v) for k, v in SemanticMasker.extract_invariants(text).items()},
            stylometry=compute_stylometry(prose_only),
            findings=findings,
        )
