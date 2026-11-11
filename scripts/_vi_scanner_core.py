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
    run_lengthy_and_roundabout_rule,
    run_loanword_and_jargon_rule,
    run_monotony_rule,
)
from _vi_docx_dhdna import compute_sliding_mattr, compute_stylometry, max_table_sentence_words
from _vi_hygiene_rules import run_document_and_table_hygiene
from _vi_masker import (
    SemanticMasker,
    _extract_regex_anchors,
    build_scan_buffer,
    line_end_offset,
    make_finding,
    offset_to_line_col,
)
from _vi_phrase_matcher import (
    GroupedSpanMatch,
    PhraseHit,
    filter_non_overlapping_hits,
    filter_statistical_cluster_hits,
    is_valid_phrase_hit,
    run_bold_colon_list_rule,
    run_staccato_fragment_rule,
    tokenize_prose,
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
_LEAD_SENT_PUNCT_RE = stdlib_re.compile(r"^[.!?…]+\s+")
_SENT_SEP_CHARS = frozenset(".!?…\n")
_AI007_ROLE_LIST_RE = compile_rule_regex(
    r"(?i)\b(?:dù|cho\s+dù|bất\s+kể)\s+bạn\s+là\s+[^.;:!?\n]{2,90},\s*(?:bạn|nội\s+dung|bài\s+viết|hướng\s+dẫn)\b"
)
_ALGO_RUNNERS: dict[str, Callable[[RuleDefinition, _ScanBuffer, Profile | None], list[Finding]]] = {
    "ALGO:BOLD_COLON_LIST_STREAK_MIN_3": run_bold_colon_list_rule,
    "ALGO:PARAGRAPH_CV_AND_OPENING_MONOTONY": run_monotony_rule,
    "ALGO:LOANWORD_AND_FOREIGN_TOKEN_CHECK": run_loanword_and_jargon_rule,
    "ALGO:DOCUMENT_AND_TABLE_HYGIENE": run_document_and_table_hygiene,
    "ALGO:LENGTHY_AND_ROUNDABOUT_SENTENCE": run_lengthy_and_roundabout_rule,
    "ALGO:STACCATO_FRAGMENT_STREAK_MIN_3": run_staccato_fragment_rule,
}


def _clean_match_slice(m: _RegexMatch, raw_text: str) -> tuple[int, str]:
    if isinstance(m, GroupedSpanMatch):
        return m.start(), m.display_text
    raw_chunk = raw_text[m.start() : m.end()]
    if len(raw_chunk) == 3 and raw_chunk[1] == "—":
        return m.start() + 1, "—"
    m_lead = _LEAD_SENT_PUNCT_RE.match(raw_chunk)
    if m_lead is not None:
        return m.start() + m_lead.end(), " ".join(raw_chunk[m_lead.end() :].split())
    return m.start(), " ".join(raw_chunk.split())


def _group_repeated_matches(
    matches: Sequence[_RegexMatch],
    raw_text: str,
    custom_hint: str | None = None,
) -> GroupedSpanMatch:
    top = matches[:3]
    first_off, _ = _clean_match_slice(top[0], raw_text)
    parts = [_clean_match_slice(m, raw_text)[1] for m in top]
    disp = " ... ".join(p for p in parts if p)
    return GroupedSpanMatch(first_off, top[-1].end(), disp, custom_hint)


def _select_para_threshold_matches(
    valid_matches: Sequence[_RegexMatch],
    para_spans: Sequence[tuple[int, int, str]],
    word_count: int,
    thresh: ThresholdSpec,
    raw_text: str = "",
) -> list[_RegexMatch]:
    assert thresh.per_para is not None  # noqa: S101
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
            para_slice = valid_matches[start_idx:m_idx]
            triggered.extend(
                para_slice
                if thresh.per_para == 1
                else [_group_repeated_matches(para_slice, raw_text) if raw_text else para_slice[0]]
            )
    if (
        not triggered
        and thresh.per_1000_words is not None
        and word_count >= 250
        and (len(valid_matches) * 1000.0 / word_count) >= thresh.per_1000_words
    ):
        triggered.append(_group_repeated_matches(valid_matches, raw_text) if raw_text else valid_matches[0])
    return triggered


def _has_same_sentence_pair(valid_matches: Sequence[_RegexMatch], raw_text: str) -> _RegexMatch | None:
    for idx in range(len(valid_matches) - 1):
        gap = raw_text[valid_matches[idx].end() : valid_matches[idx + 1].start()]
        if not any(ch in _SENT_SEP_CHARS for ch in gap):
            return _group_repeated_matches(valid_matches[idx : idx + 2], raw_text) if raw_text else valid_matches[idx]
    return None


def _select_triggered_matches(
    valid_matches: Sequence[_RegexMatch],
    para_spans: Sequence[tuple[int, int, str]],
    word_count: int,
    thresh: ThresholdSpec,
    *,
    rule_id: str = "",
    raw_text: str = "",
) -> list[_RegexMatch]:
    """Lọc kết quả vượt ngưỡng bằng thuật toán hai con trỏ tuyến tính O(P + M)."""
    if thresh.per_para is not None:
        triggered = _select_para_threshold_matches(valid_matches, para_spans, word_count, thresh, raw_text)
        if not triggered and rule_id == "VIS-TRANS-010" and len(valid_matches) >= 2:
            pair_hit = _has_same_sentence_pair(valid_matches, raw_text)
            return [pair_hit] if pair_hit is not None else []
        return triggered
    if thresh.per_doc is not None:
        return (
            (list(valid_matches) if thresh.per_doc == 1 else [valid_matches[0]])
            if len(valid_matches) >= thresh.per_doc
            else []
        )
    if thresh.per_1000_words is not None:
        dense = (len(valid_matches) * 1000.0 / max(word_count, 1)) >= thresh.per_1000_words
        return list(valid_matches) if dense else []
    return list(valid_matches)


def _prepare_rule_target_text(rid: str, buf: _ScanBuffer) -> str:
    target_text = buf.masked_no_code if rid == "VIS-AI-002" else buf.masked_prose
    if rid == "VIS-FMT-003" and "—" in target_text:
        return "\n".join((" " * len(ln)) if ln.lstrip().startswith("—") else ln for ln in target_text.splitlines())
    if rid == "VIS-FMT-004" and "," in target_text:
        return _DECIMAL_COMMA_RE.sub(".", target_text)
    return target_text


_MAX_RULE_HITS_PER_LINE = 12


def _merge_non_overlapping_matches(
    primary: Sequence[_RegexMatch], secondary: Sequence[_RegexMatch]
) -> list[_RegexMatch]:
    out: list[_RegexMatch] = []
    last_end = -1
    for m in sorted([*primary, *secondary], key=lambda x: (x.start(), -x.end())):
        if m.start() >= last_end:
            out.append(m)
            last_end = m.end()
    return out


def _resolve_match_hint(
    tm: _RegexMatch, norm_key: tuple[str, str], phrase_hints: dict[tuple[str, str], str]
) -> str | None:
    if isinstance(tm, GroupedSpanMatch):
        return tm.custom_hint
    if isinstance(tm, PhraseHit):
        return tm.entry.hint or phrase_hints.get(norm_key)
    return phrase_hints.get(norm_key)


def _build_regex_findings(
    rule: RuleDefinition, buf: _ScanBuffer, triggered: Sequence[_RegexMatch], phrase_hints: dict[tuple[str, str], str]
) -> list[Finding]:
    rid = rule.rule_id
    findings: list[Finding] = []
    line_counts: dict[int, int] = {}
    last_hit_end = -1
    for tm in triggered:
        hit_start, raw_slice = _clean_match_slice(tm, buf.raw_text)
        ln_no, _ = offset_to_line_col(buf.raw_text, hit_start, buf.nl_offsets)
        if hit_start < last_hit_end or line_counts.get(ln_no, 0) >= _MAX_RULE_HITS_PER_LINE:
            continue
        line_counts[ln_no] = line_counts.get(ln_no, 0) + 1
        last_hit_end = tm.end()
        ov_profs = (
            ("general", "marketing", "social_media", "translation")
            if rid == "VIS-FMT-003" and raw_slice == ";"
            else None
        )
        hint = _resolve_match_hint(tm, (rid, " ".join(raw_slice.split()).casefold()), phrase_hints)
        findings.append(
            make_finding(rule, buf, hit_start, raw_slice, custom_suggestion=hint, override_profiles=ov_profs)
        )
    return findings


class ViScanner:
    """Máy quét câu chữ tiếng Việt v2.2.0 (mặc định `profile="all"` xuất đủ 100% tín hiệu của 7 nhóm)."""

    VERSION: ClassVar[str] = VERSION
    SCHEMA_VERSION: ClassVar[str] = SCHEMA_VERSION
    DISCLAIMER: ClassVar[str] = (
        "Công cụ vi_scanner chỉ đánh dấu các vị trí câu chữ máy móc, sáo rỗng, dịch sát hoặc dài dòng "
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
            if not rule.regex_or_algorithm.startswith("ALGO:") and rule.regex_or_algorithm != "VOCAB"
        }
        self._rule_anchors: dict[str, tuple[str, ...]] = {
            rid: ((*anchors, "chưa") if rid == "VIS-RHET-001" and anchors else anchors)
            for rid, rule in self.rules.items()
            if rid in self._compiled
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
        self, rule: RuleDefinition, target_text: str, nl_offsets: Sequence[int], prof: Profile | None
    ) -> list[_RegexMatch]:
        rid = rule.rule_id
        thresh = rule.threshold
        cap_line = (thresh.per_para == 1 and thresh.per_1000_words is None) or thresh.per_doc == 1
        text_len = len(target_text)
        valid_matches: list[_RegexMatch] = []
        cur_line_end = -1
        cur_line_hits = 0
        for m in self._compiled[rid].finditer(target_text):
            if cap_line and m.start() <= cur_line_end and cur_line_hits >= _MAX_RULE_HITS_PER_LINE:
                continue
            if is_linguistically_exempt(rid, target_text, m.start(), m.end()) or is_profile_exempt(
                rid, target_text, m.start(), m.end(), prof
            ):
                continue
            valid_matches.append(m)
            if not cap_line:
                continue
            if m.start() > cur_line_end:
                cur_line_end = line_end_offset(target_text, m.start(), nl_offsets)
                cur_line_hits = 1
            else:
                cur_line_hits += 1
                if cur_line_hits >= _MAX_RULE_HITS_PER_LINE and cur_line_end >= text_len - 1:
                    break
        if rid == "VIS-AI-007" and not valid_matches:
            valid_matches.extend(
                m
                for m in _AI007_ROLE_LIST_RE.finditer(target_text)
                if not is_profile_exempt(rid, target_text, m.start(), m.end(), prof)
            )
        return valid_matches

    def _collect_valid_vocab_matches(
        self, rid: str, raw_hits: Sequence[PhraseHit], target_text: str, buf: _ScanBuffer, prof: Profile | None
    ) -> list[_RegexMatch]:
        if not raw_hits:
            return []
        filtered = [
            h
            for h in raw_hits
            if is_valid_phrase_hit(h.entry, target_text, h.pos, h.end_pos, prof)
            and not is_linguistically_exempt(rid, target_text, h.pos, h.end_pos)
            and not is_profile_exempt(rid, target_text, h.pos, h.end_pos, prof)
        ]
        if not filtered:
            return []
        non_overlapping = filter_non_overlapping_hits(filtered)
        return filter_statistical_cluster_hits(non_overlapping, buf.para_spans, raw_text=buf.raw_text, rid=rid)

    def _scan_regex_rule(
        self, rule: RuleDefinition, buf: _ScanBuffer, prof: Profile | None, vocab_hits: Sequence[PhraseHit] = ()
    ) -> list[Finding]:
        rid = rule.rule_id
        target_text = _prepare_rule_target_text(rid, buf)
        valid_matches: list[_RegexMatch] = []
        if rid in self._compiled:
            anchors = self._rule_anchors.get(rid, ())
            lower_haystack = buf.masked_no_code_lower if rid == "VIS-AI-002" else buf.masked_prose_lower
            if not anchors or any(sub in lower_haystack for sub in anchors):
                valid_matches = self._collect_valid_regex_matches(rule, target_text, buf.nl_offsets, prof)
        if vocab_hits:
            v_matches = self._collect_valid_vocab_matches(rid, vocab_hits, target_text, buf, prof)
            if v_matches:
                valid_matches = _merge_non_overlapping_matches(valid_matches, v_matches)

        if rid == "VIS-RHET-001" and not valid_matches:
            bridge_hits = list(_BRIDGE_NEGATION_RE.finditer(target_text))
            if len(bridge_hits) >= 3:
                grp = _group_repeated_matches(
                    bridge_hits,
                    buf.raw_text,
                    "Lặp quá nhiều cụm phủ định bắc cầu ('chưa đồng nghĩa với', 'không có nghĩa là'); "
                    "hãy đổi sang câu khẳng định trực tiếp.",
                )
                return [make_finding(rule, buf, grp.start(), grp.display_text, custom_suggestion=grp.custom_hint)]
            return []
        if not valid_matches:
            return []

        triggered = _select_triggered_matches(
            valid_matches, buf.para_spans, buf.word_count, rule.threshold, rule_id=rid, raw_text=buf.raw_text
        )
        return _build_regex_findings(rule, buf, triggered, self.vocab.phrase_hints)

    def _run_rule(
        self,
        rule: RuleDefinition,
        buf: _ScanBuffer,
        prof: Profile | None,
        vocab_hits: Sequence[PhraseHit] = (),
        rev_hits: Sequence[PhraseHit] = (),
    ) -> list[Finding]:
        if rule.regex_or_algorithm == "ALGO:LOANWORD_AND_FOREIGN_TOKEN_CHECK":
            return run_loanword_and_jargon_rule(rule, buf, prof, self.vocab, rev_hits=rev_hits)
        algo_runner = _ALGO_RUNNERS.get(rule.regex_or_algorithm)
        if algo_runner is not None:
            return algo_runner(rule, buf, prof)
        return self._scan_regex_rule(rule, buf, prof, vocab_hits=vocab_hits)

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
        vocab_by_rule, rev_hits = self.vocab.phrase_trie.scan_all(tokenize_prose(buf.masked_prose_lower))
        findings: list[Finding] = []
        for rid, rule in self.rules.items():
            if (active_rule_ids is not None and rid not in active_rule_ids) or (
                prof is not None and prof not in rule.profiles
            ):
                continue
            findings.extend(self._run_rule(rule, buf, prof, vocab_hits=vocab_by_rule.get(rid, ()), rev_hits=rev_hits))
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
            stylometry=compute_stylometry(prose_only, max_table_sent=max_table_sentence_words(buf.masked_full)),
            findings=findings,
        )
