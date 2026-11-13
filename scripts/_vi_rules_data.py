"""Trình nạp quy tắc ngữ pháp (`data/grammar.csv`) và từ vựng (`data/vocab.csv`) chuẩn UTF-8 BOM cho Excel."""

from __future__ import annotations

import collections
import csv
import datetime as dt
import functools
import io
import re as stdlib_re
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

from _vi_phrase_matcher import PhraseEntry, PhraseTrie, build_vocab_entry, sanitize_hint
from _vi_types import (
    ALL_PROFILES,
    LOANWORDS_REVIEW_META,
    MaintenanceReport,
    Profile,
    RuleDefinition,
    Severity,
    ThresholdSpec,
    VocabCatalog,
    compile_rule_regex,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

DATA_DIR: Path = Path(__file__).resolve().parent.parent / "data"
DEFAULT_VOCAB_CSV: Path = DATA_DIR / "vocab.csv"
DEFAULT_GRAMMAR_CSV: Path = DATA_DIR / "grammar.csv"

_VOCAB_REQUIRED_COLS: tuple[str, ...] = ("term", "kind", "rule_id", "replacement_hint", "status", "note")
_GRAMMAR_REQUIRED_COLS: tuple[str, ...] = (
    "rule_id",
    "status",
    "category",
    "pattern_type",
    "regex_or_algo",
    "severity",
    "weight",
    "profiles",
    "threshold",
    "exceptions",
    "description_vi",
    "bad_example",
    "better_example",
    "source_url",
    "evidence_strength",
)
_ACTIVE_TOKENS: frozenset[str] = frozenset({"", "active", "1", "true", "yes", "on"})
_DISABLED_TOKENS: frozenset[str] = frozenset({"disabled", "inactive", "0", "false", "no", "off"})
_VALID_SOURCE_STATUSES: frozenset[str] = frozenset({"verified", "missing", "internal"})
_VALID_VOCAB_KINDS: frozenset[str] = frozenset(
    {"loanword_universal", "loanword_workplace", "reverse_calque", "banned_phrase"}
)
_KNOWN_ALGO_TOKENS: frozenset[str] = frozenset(
    {
        "ALGO:BOLD_COLON_LIST_STREAK_MIN_3",
        "ALGO:PARAGRAPH_CV_AND_OPENING_MONOTONY",
        "ALGO:LOANWORD_AND_FOREIGN_TOKEN_CHECK",
        "ALGO:DOCUMENT_AND_TABLE_HYGIENE",
        "ALGO:LENGTHY_AND_ROUNDABOUT_SENTENCE",
        "ALGO:STACCATO_FRAGMENT_STREAK_MIN_3",
        "ALGO:FAKE_ROADMAP_AND_OBVIOUS_EXPLAINER",
        "ALGO:SOV_CLAUSE_ORDER_REVIEW",
    }
)
_META_ESCAPE_RE: stdlib_re.Pattern[str] = stdlib_re.compile(r"([.^$*+?{}\[\]\\|()])")


@dataclass(slots=True)
class _VocabAccumulator:
    universal: set[str] = field(default_factory=set)
    workplace: set[str] = field(default_factory=set)
    reverse_terms: list[str] = field(default_factory=list)
    reverse_hints: dict[str, str] = field(default_factory=dict)
    banned_by_rule: dict[str, list[str]] = field(default_factory=lambda: collections.defaultdict(list))
    phrase_hints: dict[tuple[str, str], str] = field(default_factory=dict)
    trie_entries: list[PhraseEntry] = field(default_factory=list)


def _normalize_space_key(text: str) -> str:
    return " ".join(text.split()).casefold()


def phrase_to_regex_branch(phrase: str) -> str:
    """Biên dịch cụm từ văn bản thuần sang nhánh biểu thức chính quy an toàn neo từ."""
    clean = " ".join(phrase.split())
    if not clean:
        raise ValueError("Cụm từ trong vocab.csv không được để trống.")
    tokens = clean.split(" ")
    parts: list[str] = []
    for idx, tok in enumerate(tokens):
        is_last = idx == len(tokens) - 1
        if not is_last and tok.endswith(","):
            parts.append(_META_ESCAPE_RE.sub(r"\\\1", tok[:-1]) + r",\s*")
        else:
            parts.append(_META_ESCAPE_RE.sub(r"\\\1", tok) + ("" if is_last else r"\s+"))
    prefix = r"\b" if clean[0].isalnum() else ""
    suffix = r"\b" if clean[-1].isalnum() else ""
    return f"{prefix}{''.join(parts)}{suffix}"


def _read_csv_rows(path: Path, required_cols: tuple[str, ...]) -> list[tuple[int, dict[str, str]]]:
    raw = path.read_text(encoding="utf-8-sig")
    first_ln = next((ln for ln in raw.splitlines() if ln.strip()), "")
    delim = ";" if first_ln.count(";") > first_ln.count(",") else ","
    reader = csv.DictReader(io.StringIO(raw), delimiter=delim)
    if reader.fieldnames is None:
        raise ValueError(f"{path.name}: Tệp CSV rỗng hoặc thiếu dòng tiêu đề cột.")
    reader.fieldnames = [h.strip() for h in reader.fieldnames]
    missing = [c for c in required_cols if c not in reader.fieldnames]
    if missing:
        raise ValueError(f"{path.name}: Thiếu cột bắt buộc: {', '.join(missing)}")
    rows: list[tuple[int, dict[str, str]]] = []
    first_col = required_cols[0]
    for raw_row in reader:
        cleaned = {k: (v or "").strip() for k, v in raw_row.items() if k is not None}
        if not any(cleaned.values()) or cleaned.get(first_col, "").startswith("#"):
            continue
        rows.append((reader.line_num, cleaned))
    return rows


def _normalize_status(raw: str, label: str) -> str:
    low = raw.lower()
    if low in _ACTIVE_TOKENS:
        return "active"
    if low in _DISABLED_TOKENS:
        return "disabled"
    raise ValueError(f"{label}: Trạng thái {raw!r} không hợp lệ (chỉ nhận active hoặc disabled).")


def _register_vocab_row(row: dict[str, str], label: str, acc: _VocabAccumulator) -> None:
    if _normalize_status(row["status"], label) != "active":
        return
    term = " ".join(row["term"].split())
    kind = row["kind"].lower()
    rid = row["rule_id"]
    hint = sanitize_hint(row["replacement_hint"])
    note = row["note"]
    if not term:
        raise ValueError(f"{label}: Cột 'term' không được để trống.")
    if kind not in _VALID_VOCAB_KINDS:
        raise ValueError(f"{label}: Giá trị kind={row['kind']!r} không hợp lệ ({sorted(_VALID_VOCAB_KINDS)}).")
    if kind == "loanword_universal":
        acc.universal.add(term.lower())
    elif kind == "loanword_workplace":
        acc.workplace.add(term.lower())
    elif kind == "reverse_calque":
        acc.reverse_terms.append(term)
        acc.trie_entries.append(
            build_vocab_entry(term=term, kind=kind, rule_id="VIS-LEX-002", raw_hint=hint, note=note)
        )
        if hint:
            acc.reverse_hints[_normalize_space_key(term)] = hint
    else:
        if not rid:
            raise ValueError(f"{label}: Cụm banned_phrase {term!r} bắt buộc khai báo 'rule_id'.")
        acc.banned_by_rule[rid].append(term)
        acc.trie_entries.append(build_vocab_entry(term=term, kind=kind, rule_id=rid, raw_hint=hint, note=note))
        if hint:
            acc.phrase_hints[(rid, _normalize_space_key(term))] = hint


def load_vocab_catalog(vocab_path: Path = DEFAULT_VOCAB_CSV) -> VocabCatalog:
    """Nạp bảng từ vựng `vocab.csv` và biên dịch sẵn cây tiền tố `PhraseTrie` tuyến tính O(N)."""
    acc = _VocabAccumulator()
    for line_no, row in _read_csv_rows(vocab_path, _VOCAB_REQUIRED_COLS):
        _register_vocab_row(row, f"{vocab_path.name}:{line_no}", acc)

    banned_map = {
        rid: tuple(sorted(set(terms), key=lambda s: (-len(s), s))) for rid, terms in acc.banned_by_rule.items()
    }
    univ = frozenset(acc.universal)
    work = frozenset(acc.workplace)
    return VocabCatalog(
        universal_loanwords=univ,
        workplace_loanwords=work,
        all_allowed_loanwords=univ | work,
        reverse_calque_re=None,
        reverse_calque_hints=acc.reverse_hints,
        banned_phrases_by_rule=banned_map,
        phrase_hints=acc.phrase_hints,
        phrase_trie=PhraseTrie(acc.trie_entries),
    )


def _resolve_rule_pattern(rid: str, raw_expr: str, vocab_phrases: Sequence[str], label: str) -> str:
    if raw_expr.startswith("ALGO:"):
        if raw_expr not in _KNOWN_ALGO_TOKENS:
            raise ValueError(f"{label}: Thuật toán {raw_expr!r} của {rid} không tồn tại.")
        if vocab_phrases:
            raise ValueError(f"{label}: Quy tắc thuật toán {rid} không nhận banned_phrase từ vocab.csv.")
        return raw_expr

    if raw_expr in ("", "VOCAB"):
        if not vocab_phrases:
            raise ValueError(f"{label}: Quy tắc {rid} đặt 'VOCAB' nhưng không có cụm từ đang bật trong vocab.csv.")
        return "VOCAB"

    try:
        compile_rule_regex(raw_expr)
    except stdlib_re.error as exc:
        raise ValueError(f"{label}: Biểu thức regex lỗi ở quy tắc {rid}: {exc}") from exc
    return raw_expr


def _parse_profiles(raw_profiles: str, label: str) -> frozenset[Profile]:
    if not raw_profiles or raw_profiles.lower() == "all":
        return frozenset(ALL_PROFILES)
    try:
        profs = frozenset(Profile(p.strip()) for p in raw_profiles.split("|") if p.strip())
    except ValueError as exc:
        raise ValueError(f"{label}: Nhóm văn bản không hợp lệ trong {raw_profiles!r}.") from exc
    if not profs:
        raise ValueError(f"{label}: Cột 'profiles' không có nhóm văn bản hợp lệ.")
    return profs


def _parse_grammar_row(row: dict[str, str], label: str, vocab: VocabCatalog) -> RuleDefinition:
    rid = row["rule_id"]
    if not rid:
        raise ValueError(f"{label}: Cột 'rule_id' không được để trống.")
    status = _normalize_status(row["status"], label)
    raw_expr = row["regex_or_algo"]
    phrases = vocab.banned_phrases_by_rule.get(rid, ())
    resolved_expr = (
        raw_expr
        if status == "disabled" and raw_expr in ("", "VOCAB") and not phrases
        else _resolve_rule_pattern(rid, raw_expr, phrases, label)
    )
    try:
        sev = Severity((row["severity"] or "warning").lower())
        weight = float((row["weight"] or "0.6").replace(",", "."))
        thresh = ThresholdSpec.parse(row["threshold"] or "1/doc")
    except ValueError as exc:
        raise ValueError(f"{label}: Sai định dạng severity/weight/threshold của {rid}: {exc}") from exc

    exc_raw = row["exceptions"]
    exceptions = tuple(e.strip() for e in exc_raw.split("|") if e.strip() and e.strip().lower() != "none")
    profs = _parse_profiles(row["profiles"], label)
    prof_ex = {Profile(e.removeprefix("profile:")) for e in exceptions if e.startswith("profile:")}
    pat_type = row["pattern_type"] or ("dictionary" if raw_expr in ("", "VOCAB") else "regex")
    source_status = (row.get("source_status") or "missing").strip().lower()
    if source_status not in _VALID_SOURCE_STATUSES:
        raise ValueError(f"{label}: source_status={source_status!r} không hợp lệ ({sorted(_VALID_SOURCE_STATUSES)}).")
    return RuleDefinition(
        rule_id=rid,
        category=row["category"] or "CUSTOM",
        pattern_type=pat_type,
        description_vi=row["description_vi"],
        regex_or_algorithm=resolved_expr,
        severity=sev,
        weight=weight,
        profiles=profs - prof_ex,
        threshold=thresh,
        exceptions=exceptions,
        bad_example=row["bad_example"],
        better_example=row["better_example"],
        source_url=row["source_url"],
        evidence_strength=row["evidence_strength"] or "custom",
        source_status=source_status,
        status=status,
    )


def load_rule_bundle(
    vocab_path: Path = DEFAULT_VOCAB_CSV,
    grammar_path: Path = DEFAULT_GRAMMAR_CSV,
) -> tuple[list[RuleDefinition], VocabCatalog]:
    """Nạp đồng bộ cặp tệp `vocab.csv` và `grammar.csv` kèm kiểm tra chéo mã quy tắc."""
    vocab = load_vocab_catalog(vocab_path)
    rules: list[RuleDefinition] = []
    seen_ids: set[str] = set()
    for line_no, row in _read_csv_rows(grammar_path, _GRAMMAR_REQUIRED_COLS):
        label = f"{grammar_path.name}:{line_no}"
        rule = _parse_grammar_row(row, label, vocab)
        if rule.rule_id in seen_ids:
            raise ValueError(f"{label}: Trùng mã quy tắc {rule.rule_id!r} trong {grammar_path.name}.")
        seen_ids.add(rule.rule_id)
        rules.append(rule)

    orphan_ids = sorted(set(vocab.banned_phrases_by_rule) - seen_ids)
    if orphan_ids:
        raise ValueError(
            f"{vocab_path.name}: Cụm banned_phrase trỏ tới rule_id chưa khai báo trong {grammar_path.name}: "
            f"{', '.join(orphan_ids)}"
        )
    return rules, vocab


@functools.lru_cache(maxsize=4)
def _cached_default_bundle(
    vocab_resolved: Path,
    grammar_resolved: Path,
) -> tuple[tuple[RuleDefinition, ...], VocabCatalog]:
    rules, vocab = load_rule_bundle(vocab_resolved, grammar_resolved)
    return tuple(rules), vocab


DEFAULT_VOCAB: VocabCatalog = _cached_default_bundle(DEFAULT_VOCAB_CSV.resolve(), DEFAULT_GRAMMAR_CSV.resolve())[1]
UNIVERSAL_NATURALIZED_LOANWORDS: frozenset[str] = DEFAULT_VOCAB.universal_loanwords
WORKPLACE_TECH_LOANWORDS: frozenset[str] = DEFAULT_VOCAB.workplace_loanwords
ALL_ALLOWED_LOANWORDS: frozenset[str] = DEFAULT_VOCAB.all_allowed_loanwords


def build_default_rules() -> list[RuleDefinition]:
    rules, _ = _cached_default_bundle(DEFAULT_VOCAB_CSV.resolve(), DEFAULT_GRAMMAR_CSV.resolve())
    return list(rules)


def check_loanwords_maintenance(
    today: dt.date | None = None,
    vocab_path: Path | None = None,
) -> MaintenanceReport:
    vocab = load_vocab_catalog(vocab_path) if vocab_path is not None else DEFAULT_VOCAB
    ref_date = today or dt.datetime.now(tz=dt.UTC).date()
    last_reviewed = dt.date.fromisoformat(LOANWORDS_REVIEW_META["last_reviewed"])
    days_elapsed = max(0, (ref_date - last_reviewed).days)
    rec_days = LOANWORDS_REVIEW_META["recommended_interval_days"]
    max_days = LOANWORDS_REVIEW_META["max_interval_days"]
    return {
        "last_reviewed": LOANWORDS_REVIEW_META["last_reviewed"],
        "today": ref_date.isoformat(),
        "days_since_review": days_elapsed,
        "recommended_interval_days": rec_days,
        "max_interval_days": max_days,
        "due_for_quarterly_review": days_elapsed >= rec_days,
        "overdue_annual_review": days_elapsed >= max_days,
        "universal_loanwords_count": len(vocab.universal_loanwords),
        "workplace_tech_loanwords_count": len(vocab.workplace_loanwords),
        "note": LOANWORDS_REVIEW_META["note"],
    }
