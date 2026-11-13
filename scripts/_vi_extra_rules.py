"""Quy tắc thủ công có kiểm soát: lộ trình giả, bảng hiển nhiên, kịch bản hù dọa và trật tự SOV."""

from __future__ import annotations

import re as stdlib_re
from typing import TYPE_CHECKING

from _vi_masker import make_finding

if TYPE_CHECKING:
    from collections.abc import Iterator

    from _vi_types import Finding, Profile, RuleDefinition, _ScanBuffer

_ROADMAP_HEADING_RE: stdlib_re.Pattern[str] = stdlib_re.compile(
    r"(?im)^#{1,6}[^\n]*\b(?:tiến\s+độ|lộ\s+trình|cột\s+mốc|milestone)\b[^\n]*$"
)
_G1_TO_G4_RE: stdlib_re.Pattern[str] = stdlib_re.compile(r"(?is)\bG1\b.{0,500}?\bG2\b.{0,500}?\bG3\b.{0,500}?\bG4\b")
_OBVIOUS_HEADING_RE: stdlib_re.Pattern[str] = stdlib_re.compile(
    r"(?im)^#{1,6}[^\n]*\b(?:diễn\s+giải|giải\s+thích)\s+"
    r"(?:trạng\s+thái|điều\s+hiển\s+nhiên|khái\s+niệm\s+cơ\s+bản)\b[^\n]*$"
)
_RISK_SCARE_RE: stdlib_re.Pattern[str] = stdlib_re.compile(
    r"(?i)\bnếu\s+không\s+có\b[^\n.]{0,110}\b(?:rủi\s+ro|nguy\s+cơ|sẽ\s+gặp)\b"
)
_SENTENCE_BOUNDARY_RE: stdlib_re.Pattern[str] = stdlib_re.compile(r"(?<=[.!?…])\s+")
_SOV_FINAL_TOKENS: frozenset[str] = frozenset({"chưa", "chưa?", "rồi", "rồi?", "không", "không?", "xong", "xong?"})


def _roadmap_hit(text: str) -> int | None:
    for hm in _ROADMAP_HEADING_RE.finditer(text):
        window = text[hm.end() : hm.end() + 700]
        if _G1_TO_G4_RE.search(window):
            return hm.start()
    return None


def _obvious_table_hit(text: str) -> int | None:
    for hm in _OBVIOUS_HEADING_RE.finditer(text):
        window = text[hm.end() : hm.end() + 500]
        if stdlib_re.search(r"(?m)^\s*\|[^\n]*\|", window):
            return hm.start()
    return None


def _iter_sentence_spans(text: str) -> Iterator[tuple[int, str]]:
    start = 0
    for boundary in _SENTENCE_BOUNDARY_RE.finditer(text):
        yield start, text[start : boundary.start()]
        start = boundary.end()
    yield start, text[start:]


def run_fake_roadmap_rule(rule: RuleDefinition, buf: _ScanBuffer, _prof: Profile | None) -> list[Finding]:
    """Gắn cờ lộ trình giả, bảng hiển nhiên và kịch bản hù dọa (`VIS-STRUCT-003`)."""
    findings: list[Finding] = []
    text = buf.masked_no_code
    if "G1" in text:
        pos = _roadmap_hit(text)
        if pos is not None:
            hint = "Bảng tiến độ G1–G4 sáo rỗng không có mốc kiểm chứng; hãy xóa hoặc thay bằng mốc số liệu."
            findings.append(make_finding(rule, buf, pos, hint, custom_suggestion=hint))
    if "#" in text and ("diễn giải" in text.casefold() or "giải thích" in text.casefold()):
        pos = _obvious_table_hit(text)
        if pos is not None:
            hint = "Bảng giải thích lại điều người đọc đã thấy; hãy xóa để tránh lặp hai tầng."
            findings.append(make_finding(rule, buf, pos, hint, custom_suggestion=hint))
    if "nếu không có" in text.casefold():
        m_risk = _RISK_SCARE_RE.search(text)
        if m_risk is not None:
            hint = "Câu hù dọa 'nếu không có... sẽ gặp rủi ro' thay bằng điều kiện và hệ quả cụ thể."
            findings.append(make_finding(rule, buf, m_risk.start(), hint, custom_suggestion=hint))
    return findings


def run_sov_review_rule(rule: RuleDefinition, buf: _ScanBuffer, _prof: Profile | None) -> list[Finding]:
    """Gắn cờ câu dài dồn động từ xuống cuối để biên tập viên rà trật tự SOV (`VIS-TRANS-014`)."""
    if not any(token in buf.masked_prose_lower for token in ("chưa", "rồi", "không", "xong")):
        return []
    findings: list[Finding] = []
    for start, sentence in _iter_sentence_spans(buf.masked_prose):
        if len(sentence.split()) < 28:
            continue
        markers = sum(
            sentence.count(marker) for marker in (" mà ", " rằng ", " thì ", " sau khi ", " trước khi ", " đã ")
        )
        tail = stdlib_re.findall(r"[0-9A-Za-zÀ-ỹĐđ?]+", sentence)[-1].casefold()
        if markers >= 3 and tail in _SOV_FINAL_TOKENS:
            findings.append(
                make_finding(
                    rule,
                    buf,
                    start,
                    " ".join(sentence.split())[:100],
                    custom_suggestion=(
                        "Câu dài dồn động từ xuống cuối; hãy tách hai vế hoặc đưa động từ chính lên đầu câu."
                    ),
                )
            )
            if len(findings) == 3:
                break
    return findings
