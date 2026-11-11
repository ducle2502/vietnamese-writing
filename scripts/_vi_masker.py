"""Bộ che ngữ nghĩa `SemanticMasker`, tra cứu dòng/cột nhị phân và đối soát 6 nhóm dữ kiện."""

from __future__ import annotations

import bisect
import collections
import hashlib
import re as stdlib_re
from typing import TYPE_CHECKING, ClassVar

from _vi_regex_anchors import _extract_regex_anchors, resolve_regex_suggestion, safe_lower_preserve_len
from _vi_types import (
    ALL_PROFILES,
    VERSION,
    Finding,
    InvariantDelta,
    RuleDefinition,
    VerifyReport,
    _ScanBuffer,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

_safe_lower_preserve_len = safe_lower_preserve_len

_PARA_BREAK_RE: stdlib_re.Pattern[str] = stdlib_re.compile(r"\n\s*\n")
_VI_COMMENT_CHAR_RE: stdlib_re.Pattern[str] = stdlib_re.compile(r"[à-ỹđÀ-ỸĐ]")
_INV_NUMBERS_RE: stdlib_re.Pattern[str] = stdlib_re.compile(r"\b\d+(?:[.,/]\d+)*%?\b")
_INV_NEGATIONS_RE: stdlib_re.Pattern[str] = stdlib_re.compile(r"(?i)\b(?:không|chưa|chẳng|chớ|miễn|cấm|phi|vô)\b")
_INV_CONDITIONALS_RE: stdlib_re.Pattern[str] = stdlib_re.compile(
    r"(?i)\b(?:nếu|trừ khi|miễn là|trong trường hợp|với điều kiện)\b"
)
_INV_MODALS_RE: stdlib_re.Pattern[str] = stdlib_re.compile(
    r"(?i)\b(?:có thể|phải|bắt buộc|ước tính|khoảng|dự kiến|tối đa|tối thiểu)\b"
)
_INV_CITATIONS_RE: stdlib_re.Pattern[str] = stdlib_re.compile(
    r"\([A-ZÀ-ỸĐ][^()\n]{2,50},\s*\d{4}[a-z]?\)|\[\d+(?:,\s*\d+)*\]"
)
_HARD_INVARIANT_LABELS: tuple[tuple[str, str], ...] = (
    ("numbers", "Sai lệch số liệu/ngày tháng"),
    ("urls", "Sai lệch đường dẫn URL"),
    ("conditionals", "Thay đổi từ chỉ điều kiện"),
    ("citations", "Mất hoặc đổi nguồn trích dẫn"),
    ("code_blocks", "Khối mã lệnh bị sửa đổi"),
    ("inline_code", "Mã nội dòng bị sửa đổi"),
    ("frontmatter", "Frontmatter bị sửa đổi"),
)
_STRICT_INVARIANT_LABELS: tuple[tuple[str, str], ...] = (
    ("negations", "Thay đổi từ phủ định"),
    ("modals", "Thay đổi từ chỉ mức độ chắc chắn"),
)


def _build_newline_offsets(text: str) -> tuple[int, ...]:
    """Xây mảng vị trí ký tự xuống dòng tăng dần trong O(N) để tra cứu dòng/cột O(log L)."""
    offsets: list[int] = []
    pos = text.find("\n")
    while pos != -1:
        offsets.append(pos)
        pos = text.find("\n", pos + 1)
    return tuple(offsets)


def offset_to_line_col(text: str, offset: int, nl_offsets: Sequence[int] | None = None) -> tuple[int, int]:
    if nl_offsets is not None:
        idx = bisect.bisect_left(nl_offsets, offset)
        line = idx + 1
        col = (offset + 1) if idx == 0 else (offset - nl_offsets[idx - 1])
        return line, col
    line = text.count("\n", 0, offset) + 1
    last_nl = text.rfind("\n", 0, offset)
    col = (offset + 1) if last_nl == -1 else (offset - last_nl)
    return line, col


def line_end_offset(text: str, offset: int, nl_offsets: Sequence[int]) -> int:
    idx = bisect.bisect_left(nl_offsets, offset)
    return nl_offsets[idx] if idx < len(nl_offsets) else len(text)


def context_at(text: str, start: int, end: int, radius: int = 65) -> str:
    s = max(0, start - radius)
    e = min(len(text), end + radius)
    return " ".join(text[s:e].replace("\n", " ").split())


def paragraph_spans(text: str) -> list[tuple[int, int, str]]:
    spans: list[tuple[int, int, str]] = []
    pos = 0
    for m in _PARA_BREAK_RE.finditer(text):
        chunk = text[pos : m.start()]
        if chunk.strip():
            spans.append((pos, m.start(), chunk))
        pos = m.end()
    tail = text[pos:]
    if tail.strip():
        spans.append((pos, len(text), tail))
    return spans


def sentence_around(text: str, start: int, end: int) -> str:
    left = max(text.rfind(".", 0, start), text.rfind("\n", 0, start))
    right_dot = text.find(".", end)
    right_nl = text.find("\n", end)
    candidates = [x for x in (right_dot, right_nl) if x != -1]
    right = min(candidates) if candidates else len(text)
    return text[left + 1 : right]


def make_finding(
    rule: RuleDefinition,
    buf: _ScanBuffer,
    offset: int,
    matched_text: str,
    *,
    custom_suggestion: str | None = None,
    override_profiles: Sequence[str] | None = None,
) -> Finding:
    line, col = offset_to_line_col(buf.raw_text, offset, buf.nl_offsets)
    end = min(len(buf.raw_text), offset + max(1, len(matched_text)))
    default_fb = f"Viết gọn hơn (ví dụ: '{rule.better_example}')" if rule.better_example else rule.description_vi
    suggestion = custom_suggestion or resolve_regex_suggestion(rule.rule_id, matched_text) or default_fb
    app_profs = (
        list(override_profiles)
        if override_profiles is not None
        else [p.value for p in ALL_PROFILES if p in rule.profiles]
    )
    app_set = frozenset(app_profs)
    ex_profs = [p.value for p in ALL_PROFILES if p.value not in app_set]
    return Finding(
        rule_id=rule.rule_id,
        category=rule.category,
        severity=rule.severity.value,
        weight=rule.weight,
        line=line,
        col=col,
        matched_text=matched_text[:120],
        context=context_at(buf.raw_text, offset, end),
        description_vi=rule.description_vi,
        suggestion_vi=suggestion,
        applicable_profiles=app_profs,
        exempt_profiles=ex_profs,
        evidence_strength=rule.evidence_strength,
    )


class SemanticMasker:
    """Che các vùng không được phép bắt lỗi bằng khoảng trắng cùng độ dài và đối soát 6 nhóm dữ kiện."""

    FRONTMATTER_RE: ClassVar[stdlib_re.Pattern[str]] = stdlib_re.compile(r"\A---\s*\n[\s\S]*?\n---\s*(?:\n|$)")
    ENGLISH_SECTION_RE: ClassVar[stdlib_re.Pattern[str]] = stdlib_re.compile(
        r"<a\s+(?:id|name)=[\"']english[\"']\s*>\s*</a>[\s\S]*$",
        stdlib_re.IGNORECASE,
    )
    CODE_BLOCK_RE: ClassVar[stdlib_re.Pattern[str]] = stdlib_re.compile(r"```[\s\S]*?```")
    INLINE_CODE_RE: ClassVar[stdlib_re.Pattern[str]] = stdlib_re.compile(r"`[^`\n]+`")
    QUOTED_SPEECH_RE: ClassVar[stdlib_re.Pattern[str]] = stdlib_re.compile(r'"[^\n"]{1,600}"|“[^\n”]{1,600}”')
    MD_LINK_TARGET_RE: ClassVar[stdlib_re.Pattern[str]] = stdlib_re.compile(r"(\]\()([^)\n]+)(\))")
    HTML_COMMENT_RE: ClassVar[stdlib_re.Pattern[str]] = stdlib_re.compile(r"<!--[\s\S]*?-->")
    HTML_CODE_TAG_RE: ClassVar[stdlib_re.Pattern[str]] = stdlib_re.compile(
        r"<code\b[^>]*>[\s\S]*?</code>", stdlib_re.IGNORECASE
    )
    HTML_KBD_TAG_RE: ClassVar[stdlib_re.Pattern[str]] = stdlib_re.compile(
        r"<kbd\b[^>]*>[\s\S]*?</kbd>", stdlib_re.IGNORECASE
    )
    HTML_IMG_RE: ClassVar[stdlib_re.Pattern[str]] = stdlib_re.compile(
        r"</?(?:img|picture|source|div|p|table|thead|tbody|tfoot|tr|td|th|br|hr|a|"
        r"details|summary|kbd|sub|sup|span|b|i|u|strong|em|figure|figcaption)"
        r"(?:\s+[^>]+|\s*)>",
        stdlib_re.IGNORECASE,
    )
    BARE_URL_RE: ClassVar[stdlib_re.Pattern[str]] = stdlib_re.compile(r"(?:https?|file)://[^\s)\">]+")
    MD_TABLE_SEP_RE: ClassVar[stdlib_re.Pattern[str]] = stdlib_re.compile(r"^\|[\s:\-|]+\|$")

    @staticmethod
    def _blank_span(raw: str) -> str:
        return "".join("\n" if ch == "\n" else " " for ch in raw)

    @classmethod
    def _blank_match(cls, match: stdlib_re.Match[str]) -> str:
        return cls._blank_span(match.group(0))

    @classmethod
    def _blank_quote_match(cls, match: stdlib_re.Match[str]) -> str:
        raw = match.group(0)
        return cls._blank_span(raw) if len(raw) >= 12 else raw

    @classmethod
    def _blank_code_block(cls, match: stdlib_re.Match[str]) -> str:
        """Che khối code nhưng giữ lại phần chú thích tiếng Việt sau dấu `#` trong cây thư mục (`├──`, `└──`)."""
        raw = match.group(0)
        out: list[str] = []
        for line in raw.splitlines(keepends=True):
            if ("├" in line or "└" in line or "│" in line) and "#" in line:
                hash_idx = line.index("#")
                comment_part = line[hash_idx:]
                if _VI_COMMENT_CHAR_RE.search(comment_part):
                    out.append((" " * hash_idx) + cls.INLINE_CODE_RE.sub(cls._blank_match, comment_part))
                    continue
            out.append(cls._blank_span(line))
        return "".join(out)

    @classmethod
    def mask_frontmatter_and_english(cls, text: str) -> str:
        masked = cls.FRONTMATTER_RE.sub(cls._blank_match, text) if text.startswith("---") else text
        if "<a" in masked or "<A" in masked:
            return cls.ENGLISH_SECTION_RE.sub(cls._blank_match, masked)
        return masked

    @classmethod
    def mask_code_blocks_raw(cls, text: str) -> str:
        return cls.CODE_BLOCK_RE.sub(cls._blank_match, text) if "```" in text else text

    @classmethod
    def mask_code_and_quotes(cls, text: str, *, mask_quotes: bool = True) -> str:
        masked = cls.mask_frontmatter_and_english(text)
        if "```" in masked:
            masked = cls.CODE_BLOCK_RE.sub(cls._blank_code_block, masked)
        if "`" in masked:
            masked = cls.INLINE_CODE_RE.sub(cls._blank_match, masked)
        if "<" in masked:
            if "<!--" in masked:
                masked = cls.HTML_COMMENT_RE.sub(cls._blank_match, masked)
            masked = cls.HTML_CODE_TAG_RE.sub(cls._blank_match, masked)
            masked = cls.HTML_KBD_TAG_RE.sub(cls._blank_match, masked)
            masked = cls.HTML_IMG_RE.sub(cls._blank_match, masked)
        if mask_quotes and ('"' in masked or "“" in masked):
            masked = cls.QUOTED_SPEECH_RE.sub(cls._blank_quote_match, masked)
        return masked

    @classmethod
    def mask_urls_and_links(cls, masked_text: str) -> str:
        masked = (
            cls.MD_LINK_TARGET_RE.sub(
                lambda m: m.group(1) + cls._blank_span(m.group(2)) + m.group(3),
                masked_text,
            )
            if "](" in masked_text
            else masked_text
        )
        return cls.BARE_URL_RE.sub(cls._blank_match, masked) if "://" in masked else masked

    @classmethod
    def mask_preserve_offsets(cls, text: str, *, mask_quotes: bool = True) -> str:
        masked = cls.mask_code_and_quotes(text, mask_quotes=mask_quotes)
        return cls.mask_urls_and_links(masked)

    @classmethod
    def flatten_markdown_tables_preserve_lines(cls, masked_text: str) -> str:
        """Thay vách ngăn `|` của bảng Markdown bằng khoảng trắng để quét câu chữ không lệch dòng/cột."""
        if "|" not in masked_text:
            return masked_text
        out_lines: list[str] = []
        for line in masked_text.splitlines(keepends=True):
            stripped = line.strip()
            if stripped.startswith("|") and stripped.endswith("|"):
                if cls.MD_TABLE_SEP_RE.match(stripped):
                    out_lines.append("".join("\n" if c == "\n" else " " for c in line))
                    continue
                out_lines.append(line.replace("|", " "))
            else:
                out_lines.append(line)
        return "".join(out_lines)

    @classmethod
    def extract_invariants(cls, text: str) -> dict[str, list[str]]:
        lower_text = safe_lower_preserve_len(text)
        return {
            "numbers": _INV_NUMBERS_RE.findall(text),
            "negations": _INV_NEGATIONS_RE.findall(lower_text),
            "conditionals": _INV_CONDITIONALS_RE.findall(lower_text),
            "modals": _INV_MODALS_RE.findall(lower_text),
            "urls": ([u.split("?utm_source=")[0] for u in cls.BARE_URL_RE.findall(text)] if "://" in text else []),
            "citations": (_INV_CITATIONS_RE.findall(text) if ("(" in text or "[" in text) else []),
            "code_blocks": cls.CODE_BLOCK_RE.findall(text) if "```" in text else [],
            "inline_code": cls.INLINE_CODE_RE.findall(text) if "`" in text else [],
            "frontmatter": (cls.FRONTMATTER_RE.findall(text) if text.startswith("---") else []),
        }

    @staticmethod
    def diff_multiset(before_items: Sequence[str], after_items: Sequence[str]) -> tuple[list[str], list[str]]:
        """So sánh hai đa tập hợp trong thời gian O(N) bằng bảng băm Counter."""
        c_before = collections.Counter(before_items)
        c_after = collections.Counter(after_items)
        if c_before == c_after:
            return [], []
        removed = sorted((c_before - c_after).elements())
        added = sorted((c_after - c_before).elements())
        return removed, added

    @classmethod
    def validate_invariants(
        cls,
        inv_orig: dict[str, list[str]],
        inv_rewr: dict[str, list[str]],
        *,
        strict_negations_and_modals: bool = False,
    ) -> tuple[bool, list[str]]:
        errors: list[str] = []
        checks = (
            (*_HARD_INVARIANT_LABELS, *_STRICT_INVARIANT_LABELS)
            if strict_negations_and_modals
            else _HARD_INVARIANT_LABELS
        )
        for key, label in checks:
            removed, added = cls.diff_multiset(inv_orig[key], inv_rewr[key])
            if removed or added:
                errors.append(f"{label}: mất={removed} | thêm={added}")
        return (len(errors) == 0, errors)

    @classmethod
    def validate_rewrite_safety(
        cls,
        original: str,
        rewritten: str,
        *,
        strict_negations_and_modals: bool = False,
    ) -> tuple[bool, list[str]]:
        inv_orig = cls.extract_invariants(original)
        inv_rewr = cls.extract_invariants(rewritten)
        return cls.validate_invariants(
            inv_orig,
            inv_rewr,
            strict_negations_and_modals=strict_negations_and_modals,
        )


def build_scan_buffer(text: str) -> _ScanBuffer:
    masked_no_code = SemanticMasker.mask_code_and_quotes(text, mask_quotes=True)
    masked_full = SemanticMasker.mask_urls_and_links(masked_no_code)
    masked_prose = SemanticMasker.flatten_markdown_tables_preserve_lines(masked_full)
    return _ScanBuffer(
        raw_text=text,
        masked_no_code=masked_no_code,
        masked_no_code_lower=safe_lower_preserve_len(masked_no_code),
        masked_full=masked_full,
        masked_prose=masked_prose,
        masked_prose_lower=safe_lower_preserve_len(masked_prose),
        nl_offsets=_build_newline_offsets(text),
        para_spans=tuple(paragraph_spans(masked_prose)),
        word_count=max(len(masked_prose.split()), 1),
    )


def verify_text(before: str, after: str) -> VerifyReport:
    inv_b = SemanticMasker.extract_invariants(before)
    inv_a = SemanticMasker.extract_invariants(after)
    ok, errors = SemanticMasker.validate_invariants(inv_b, inv_a, strict_negations_and_modals=True)
    deltas: dict[str, InvariantDelta] = {}
    for key, before_items in inv_b.items():
        removed, added = SemanticMasker.diff_multiset(before_items, inv_a[key])
        if removed or added:
            deltas[key] = {"removed": removed, "added": added}
    return {
        "version": VERSION,
        "passed": ok,
        "errors": errors,
        "changes": deltas,
        "before_sha256": hashlib.sha256(before.encode("utf-8")).hexdigest(),
        "after_sha256": hashlib.sha256(after.encode("utf-8")).hexdigest(),
        "note": (
            "Kiểm tra 6 nhóm dữ kiện (số liệu, phủ định, điều kiện, mức độ chắc chắn, "
            "đường dẫn/mã lệnh, trích dẫn). Nếu cố ý lược bỏ từ rào đón thừa như "
            "'có thể có khả năng', hãy giải trình rõ."
        ),
    }


def parse_ignore_cols(raw: str | None) -> set[int]:
    if not raw:
        return set()
    return {int(p) for raw_p in raw.split(",") if (p := raw_p.strip()).isdigit() and int(p) >= 1}


def filter_markdown_table_columns(text: str, ignore_cols: set[int]) -> str:
    """Xóa nội dung các cột bảng được chỉ định bằng khoảng trắng cùng độ dài để giữ nguyên dòng/cột."""
    if not ignore_cols:
        return text
    out_lines: list[str] = []
    in_table = False
    row_idx = 0
    for line in text.splitlines(keepends=True):
        stripped = line.strip()
        if stripped.startswith("|") and stripped.endswith("|"):
            row_idx = 0 if not in_table else (row_idx + 1)
            in_table = True
            if SemanticMasker.MD_TABLE_SEP_RE.match(stripped) or row_idx == 0:
                out_lines.append(line)
                continue
            parts = line.split("|")
            for col_1based in ignore_cols:
                if 1 <= col_1based <= len(parts) - 2:
                    parts[col_1based] = " " * len(parts[col_1based])
            out_lines.append("|".join(parts))
        else:
            in_table = False
            row_idx = 0
            out_lines.append(line)
    return "".join(out_lines)


__all__ = [
    "SemanticMasker",
    "_build_newline_offsets",
    "_extract_regex_anchors",
    "_safe_lower_preserve_len",
    "build_scan_buffer",
    "context_at",
    "filter_markdown_table_columns",
    "line_end_offset",
    "make_finding",
    "offset_to_line_col",
    "paragraph_spans",
    "parse_ignore_cols",
    "sentence_around",
    "verify_text",
]
