"""Quy tắc thủ công có kiểm soát, khử trùng chồng chéo xuyên quy tắc và kiểm tra cấu trúc kiểm toán."""

from __future__ import annotations

import collections
import re as stdlib_re
from typing import TYPE_CHECKING

from _vi_docx_dhdna import compute_stylometry
from _vi_masker import make_finding
from _vi_types import Profile

if TYPE_CHECKING:
    from collections.abc import Iterator, Mapping, Sequence

    from _vi_types import Finding, RuleDefinition, StylometryReport, _ScanBuffer

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
_SEV_PRIORITY: dict[str, int] = {"error": 3, "warning": 2, "info": 1}

_TBL_SEP_RE: stdlib_re.Pattern[str] = stdlib_re.compile(r"^[\s|:\-+]+$")
_HR_OR_EMPTY_RE: stdlib_re.Pattern[str] = stdlib_re.compile(r"^\s*(?:[-*_]{3,})?\s*$")
_CONTENT_TOKEN_RE: stdlib_re.Pattern[str] = stdlib_re.compile(r"[a-zà-ỹđ]{3,}")
_STANDALONE_CIT_RE: stdlib_re.Pattern[str] = stdlib_re.compile(
    r"(?i)\btheo\s+(?:thông\s+báo|văn\s+bản|công\s+văn|quyết\s+định|tờ\s+trình)\s+số\s+[0-9A-Za-zÀ-ỹĐđ./-]+"
)
_CIT_TOPIC_TAIL_RE: stdlib_re.Pattern[str] = stdlib_re.compile(
    r"(?i)\b(?:về(?:\s+việc)?|quy\s+định|hướng\s+dẫn|phê\s+duyệt|ban\s+hành|sửa\s+đổi|bổ\s+sung|thay\s+thế|v/v)\b"
)
_CHECKLIST_NOTE_LEAD_RE: stdlib_re.Pattern[str] = stdlib_re.compile(r"(?i)^(?:có|một\s+phần|chưa\s+có)\s+vì\b")
_OVERLAP_STOPWORDS: frozenset[str] = frozenset(
    {
        "bảng",
        "bằng",
        "cần",
        "cho",
        "chỉ",
        "chưa",
        "của",
        "cùng",
        "các",
        "câu",
        "còn",
        "đây",
        "đều",
        "đến",
        "để",
        "đó",
        "được",
        "dưới",
        "hai",
        "hãy",
        "hoặc",
        "hơn",
        "khi",
        "khiến",
        "không",
        "làm",
        "lại",
        "một",
        "mục",
        "nào",
        "này",
        "nên",
        "nếu",
        "người",
        "nhiều",
        "như",
        "nhưng",
        "những",
        "phải",
        "qua",
        "sau",
        "tại",
        "thành",
        "theo",
        "trên",
        "trong",
        "trước",
        "từng",
        "vào",
        "vẫn",
        "việc",
        "với",
    }
)


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


def _finding_sort_key(finding: Finding) -> tuple[int, int, int, int, str]:
    is_not_error = 0 if finding.severity == "error" else 1
    return (
        is_not_error,
        -len(finding.matched_text),
        -_SEV_PRIORITY.get(finding.severity, 0),
        finding.col,
        finding.rule_id,
    )


def _dedup_line_findings(line_items: Sequence[Finding]) -> list[Finding]:
    kept_items: list[Finding] = []
    kept_spans: list[tuple[int, int]] = []
    for item in sorted(line_items, key=_finding_sort_key):
        start = item.col
        end = start + max(len(item.matched_text), 1)
        if not any(start < ke and ks < end for ks, ke in kept_spans):
            kept_items.append(item)
            kept_spans.append((start, end))
    return kept_items


def deduplicate_overlapping_findings(
    findings: Sequence[Finding],
    rules: Mapping[str, RuleDefinition],
) -> list[Finding]:
    """Khử nổ kép khi hai quy tắc khác nhau (regex/từ vựng) trùng vùng trên cùng một dòng."""
    if len(findings) <= 1:
        return list(findings)
    out: list[Finding] = []
    by_line: dict[int, list[Finding]] = collections.defaultdict(list)
    for finding in findings:
        rule = rules.get(finding.rule_id)
        if rule is not None and rule.regex_or_algorithm.startswith("ALGO:"):
            out.append(finding)
        else:
            by_line[finding.line].append(finding)
    for line_items in by_line.values():
        out.extend(_dedup_line_findings(line_items) if len(line_items) > 1 else line_items)
    return out


def _audit_stylometry_extras(
    rule: RuleDefinition, buf: _ScanBuffer, prof: Profile | None, stylo: StylometryReport | None = None
) -> list[Finding]:
    if prof not in (None, Profile.AUDIT_REPORT):
        return []
    need_density = prof == Profile.AUDIT_REPORT and len(buf.para_spans) >= 3
    need_cv = buf.word_count >= 100
    if not (need_density or need_cv):
        return []
    if stylo is None:
        prose_only = "\n".join(
            ln for ln in buf.masked_full.splitlines() if not (ln.strip().startswith("|") and ln.strip().endswith("|"))
        )
        stylo = compute_stylometry(prose_only, max_table_sent=0)
    findings: list[Finding] = []
    anchor = buf.para_spans[0][0] if buf.para_spans else 0
    if need_density and stylo["so_doan"] >= 3 and stylo["cau_trung_binh_doan"] > 2.5:
        avg_s = stylo["cau_trung_binh_doan"]
        findings.append(
            make_finding(
                rule,
                buf,
                anchor,
                f"[Trung bình {avg_s:.2f} câu/đoạn > 2,5]",
                custom_suggestion=(
                    "Đoạn văn trong báo cáo kiểm toán quá dày; hãy tách đoạn về mức tối đa 2 câu để đọc lướt nhanh."
                ),
                override_profiles=("audit_report",),
            )
        )
    if need_cv and stylo["so_cau"] >= 30 and stylo["bien_dong_do_dai_cau_cv"] < 0.35:
        cv = stylo["bien_dong_do_dai_cau_cv"]
        findings.append(
            make_finding(
                rule,
                buf,
                anchor,
                f"[CV câu={cv:.2f} < 0,35 trên {stylo['so_cau']} câu]",
                custom_suggestion="Nhịp độ dài câu đều kiểu máy; hãy xen câu chốt ngắn 5–8 từ trước chuỗi số liệu.",
                override_profiles=("audit_report",),
            )
        )
    return findings


def _content_tokens(text: str) -> set[str]:
    return {w for w in _CONTENT_TOKEN_RE.findall(text.casefold()) if w not in _OVERLAP_STOPWORDS}


def _iter_markdown_tables(lines: Sequence[str]) -> Iterator[tuple[int, str]]:
    idx = 0
    n_lines = len(lines)
    while idx < n_lines:
        st = lines[idx].strip()
        if st.startswith("|") and st.endswith("|"):
            end_idx = idx
            data_rows: list[str] = []
            while end_idx < n_lines and (cur := lines[end_idx].strip()).startswith("|") and cur.endswith("|"):
                if not _TBL_SEP_RE.match(cur):
                    data_rows.append(cur)
                end_idx += 1
            if len(data_rows) >= 3:
                yield idx, " ".join(data_rows)
            idx = end_idx
        else:
            idx += 1


def _preceding_prose_block(lines: Sequence[str], tbl_idx: int) -> tuple[int, str] | None:
    pos = tbl_idx - 1
    while pos >= 0 and _HR_OR_EMPTY_RE.match(lines[pos]):
        pos -= 1
    collected: list[str] = []
    first_idx = pos
    while pos >= 0:
        st = lines[pos].strip()
        if not st or _HR_OR_EMPTY_RE.match(st) or st.startswith(("#", "|")):
            break
        collected.append(st.lstrip("> "))
        first_idx = pos
        pos -= 1
    if not collected:
        return None
    collected.reverse()
    return first_idx, " ".join(collected)


def _check_summary_table_overlap(rule: RuleDefinition, buf: _ScanBuffer) -> list[Finding]:
    if "|" not in buf.masked_full:
        return []
    lines = buf.masked_full.splitlines(keepends=True)
    line_starts: list[int] = []
    running = 0
    for ln in lines:
        line_starts.append(running)
        running += len(ln)
    findings: list[Finding] = []
    for tbl_idx, tbl_text in _iter_markdown_tables(lines):
        preceding = _preceding_prose_block(lines, tbl_idx)
        if preceding is None:
            continue
        prose_idx, prose = preceding
        if len(prose.split()) < 18:
            continue
        p_tokens = _content_tokens(prose)
        if len(p_tokens) < 8:
            continue
        t_tokens = _content_tokens(tbl_text)
        if len(p_tokens & t_tokens) / len(p_tokens) >= 0.60:
            findings.append(
                make_finding(
                    rule,
                    buf,
                    line_starts[prose_idx],
                    " ".join(prose.split())[:100],
                    custom_suggestion=(
                        "Khối tóm tắt lặp lại >= 60% nội dung bảng ngay bên dưới; hãy bỏ phần lặp hai tầng."
                    ),
                    override_profiles=("audit_report", "general"),
                )
            )
    return findings


def _check_standalone_citations(rule: RuleDefinition, buf: _ScanBuffer, prof: Profile | None) -> list[Finding]:
    if prof not in (None, Profile.AUDIT_REPORT) or "số " not in buf.masked_prose_lower:
        return []
    findings: list[Finding] = []
    for m_cit in _STANDALONE_CIT_RE.finditer(buf.masked_prose):
        tail = buf.masked_prose[m_cit.end() : m_cit.end() + 70]
        m_stop = stdlib_re.search(r"[,.;!?\n]", tail)
        clause_tail = tail[: m_stop.start()] if m_stop else tail
        if not _CIT_TOPIC_TAIL_RE.search(clause_tail):
            findings.append(
                make_finding(
                    rule,
                    buf,
                    m_cit.start(),
                    buf.raw_text[m_cit.start() : m_cit.end()],
                    custom_suggestion=(
                        "Trích dẫn văn bản chỉ nêu số hiệu cộc lốc; hãy bổ sung ngắn gọn chủ đề văn bản ngay trong câu."
                    ),
                    override_profiles=("audit_report",),
                )
            )
    return findings


def _check_checklist_notes(rule: RuleDefinition, buf: _ScanBuffer) -> list[Finding]:
    if "|" not in buf.masked_full or "vì" not in buf.masked_full.casefold():
        return []
    findings: list[Finding] = []
    offset = 0
    for ln in buf.masked_full.splitlines(keepends=True):
        st = ln.strip()
        if st.startswith("|") and st.endswith("|") and not _TBL_SEP_RE.match(st):
            cells = [c.strip().lstrip("*_ ") for c in st.strip("|").split("|")]
            bad_cell = next((c for c in cells[1:] if _CHECKLIST_NOTE_LEAD_RE.match(c)), None)
            if bad_cell is not None:
                findings.append(
                    make_finding(
                        rule,
                        buf,
                        offset,
                        bad_cell[:80],
                        custom_suggestion=(
                            "Ô ghi chú bảng kiểm không mở bằng 'Có vì / Một phần vì / Chưa có vì'; "
                            "hãy đi thẳng vào lý do trong một câu."
                        ),
                    )
                )
        offset += len(ln)
    return findings


def check_audit_structure_extras(
    rule: RuleDefinition, buf: _ScanBuffer, prof: Profile | None, stylo: StylometryReport | None = None
) -> list[Finding]:
    """Kiểm tra mật độ đoạn, CV câu, lặp bảng tóm tắt, trích dẫn cộc lốc và mở đầu ghi chú bảng kiểm."""
    findings = _audit_stylometry_extras(rule, buf, prof, stylo=stylo)
    findings.extend(_check_summary_table_overlap(rule, buf))
    findings.extend(_check_standalone_citations(rule, buf, prof))
    findings.extend(_check_checklist_notes(rule, buf))
    return findings
