"""Quy tắc vệ sinh trình bày tài liệu, tiêu đề, bảng số liệu và kỷ luật bằng chứng (`VIS-STRUCT-002`)."""

from __future__ import annotations

import math
import re as stdlib_re
from typing import TYPE_CHECKING

from _vi_algo_rules import VI_DIACRITIC_RE
from _vi_context_and_echo import check_calque_heading, check_prose_proximity_echo
from _vi_masker import SemanticMasker, make_finding
from _vi_types import Finding, Profile, RuleDefinition, _ScanBuffer

if TYPE_CHECKING:
    from collections.abc import Sequence

_PAREN_STRIP_RE = stdlib_re.compile(r"\([^)]*\)")
_CURRENCY_UNIT_RE = stdlib_re.compile(r"(?i)\b(?:đồng|đ|vnd|tr|triệu|tỷ)\b")
_PARSE_NUM_RE = stdlib_re.compile(r"^[+-]?\d+(?:[.,]\d+)*$")
_THOUSAND_DOT_NUM_RE = stdlib_re.compile(r"^[+-]?\d{1,3}(?:\.\d{3})+$")

_QUICK_HYGIENE_CHECKS: tuple[tuple[stdlib_re.Pattern[str], str, tuple[str, ...] | None], ...] = (
    (
        stdlib_re.compile(r"[\u200b\u200c\u200d\ufeff]"),
        "Xóa ký tự khoảng trắng ẩn (zero-width space / BOM) gây lệch lề danh sách.",
        None,
    ),
    (stdlib_re.compile(r"\*\*\*\*"), "Xóa dấu in đậm bị chồng `****`.", None),
    (stdlib_re.compile(r"#(?:REF|VALUE|NAME|N/A)!"), "Xóa lỗi công thức bảng tính bị rò rỉ ra văn bản.", None),
    (
        stdlib_re.compile(r"(?i)\bthiếu\s+-\s*\d"),
        "Bỏ dấu trừ sau chữ 'Thiếu' (viết 'Còn thiếu X%' thay vì 'Thiếu -X%').",
        None,
    ),
    (
        stdlib_re.compile(r"->"),
        "Thay mũi tên ASCII `->` trong câu văn xuôi bằng từ nối nhân quả hoặc thứ tự tự nhiên.",
        ("general", "audit_report", "academic", "legal", "social_media", "translation"),
    ),
    (
        stdlib_re.compile(r"(?m)(?:^[^;\n]*;){2,}"),
        "Tách câu có nhiều dấu chấm phẩy `;` liên tiếp thành các câu ngắn độc lập.",
        ("general", "marketing", "social_media", "translation"),
    ),
    (
        stdlib_re.compile(r"[🚀💡✨🎯🔥📌✅⭐🌟💪🎉👉⚡🔍📊🏆💎🌈]"),
        "Gỡ emoji trang trí kiểu bài mẫu AI khỏi văn bản chuyên môn/kỹ thuật.",
        ("general", "audit_report", "academic", "legal", "translation"),
    ),
)

_VI_HYGIENE_CHECKS: tuple[tuple[stdlib_re.Pattern[str], str, tuple[str, ...] | None], ...] = (
    (
        stdlib_re.compile(r"\b\d+\.\d+%"),
        "Dùng dấu phẩy cho số thập phân phần trăm trong tiếng Việt (ví dụ: '59,9%' thay vì '59.9%').",
        ("general", "audit_report", "academic", "legal", "translation"),
    ),
    (
        stdlib_re.compile(r"\([A-Za-zÀ-ỹĐđ0-9\s,+/-]{2,60}=[A-Za-zÀ-ỹĐđ0-9\s,+/%-]{1,60}\)"),
        "Diễn đạt phép tính trong ngoặc đơn bằng lời tự nhiên ('tương ứng', 'gồm') thay vì dấu `=`.",
        ("audit_report", "social_media"),
    ),
    (
        stdlib_re.compile(r"(?:“[^”\n]{1,25}”[^.\n]{0,40}){2,}“[^”\n]{1,25}”"),
        "Gỡ dấu ngoặc kép cong '“...”' bọc quanh các từ khóa thông thường không phải lời trích dẫn.",
        ("general", "audit_report", "academic", "legal", "translation"),
    ),
    (
        stdlib_re.compile(
            r"(?i)\b(?:hoàn\s+thành|thực\s+hiện\s+được|đạt\s+yêu\s+cầu|thành\s+công)[^.;!\n]{0,60}"
            r"\b(?:kể\s+cả|bao\s+gồm\s+cả|gộp\s+cả|tính\s+cả)\s+(?:các\s+)?"
            r"(?:trường\s+hợp|giao\s+dịch|hạng\s+mục|nội\s+dung|kịch\s+bản|phiếu|hồ\s+sơ)\s+"
            r"(?:còn\s+|đang\s+|có\s+)?(?:lỗi|vướng\s+mắc|tồn\s+đọng|khiếm\s+khuyết|chưa\s+đạt)\b"
        ),
        (
            "Tách riêng tỷ lệ hoàn thành không lỗi và tỷ lệ còn lỗi/vướng mắc, "
            "không cộng gộp mục còn lỗi vào chỉ số hoàn thành."
        ),
        ("general", "audit_report", "academic", "legal"),
    ),
    (
        stdlib_re.compile(
            r"(?i)\b(?:đã\s+đóng\s+lỗi|đánh\s+dấu\s+(?:đã\s+)?(?:xử\s+lý|hoàn\s+thành)|"
            r"chuyển\s+trạng\s+thái\s+(?:hoàn\s+thành|đã\s+xử\s+lý)|xác\s+nhận\s+hoàn\s+thành)\s+"
            r"(?:bằng\s+cách|thông\s+qua\s+việc|nhờ\s+việc|sau\s+khi|do\s+đã|qua\s+việc)\s+"
            r"(?:nhắc\s+lại|hướng\s+dẫn\s+lại|phản\s+hồi\s+trên\s+(?:bảng|hệ\s+thống)|"
            r"gửi\s+email\s+nhắc|họp\s+bàn|đang\s+trình|trình\s+xin\s+ý\s+kiến)\b"
        ),
        (
            "Không tính hoạt động trung gian (nhắc lại, hướng dẫn lại, đang trình, họp bàn) "
            "là đã hoàn thành hoặc đã đóng lỗi khi chưa có đầu ra kiểm chứng."
        ),
        ("general", "audit_report", "academic", "legal"),
    ),
    (
        stdlib_re.compile(
            r"(?i)\b(?:bù\s+trừ\s+(?:đúng\s+)?nhau|tự\s+triệt\s+tiêu\s+nhau)[^.;!\n]{0,50}"
            r"\b(?:nên|do\s+đó|vì\s+vậy)\s+"
            r"(?:tổng\s+chênh\s+lệch\s+bằng\s+0|không\s+còn\s+sai\s+lệch|đảm\s+bảo\s+khớp\s+đúng|hoàn\s+toàn\s+cân\s+đối)\b"
        ),
        (
            "Tổng chênh lệch ròng bằng 0 do bù trừ qua lại không chứng minh dữ liệu khớp đúng ở cấp giao dịch đơn lẻ; "
            "cần đối soát theo tổng giá trị tuyệt đối của chênh lệch."
        ),
        ("general", "audit_report", "academic", "legal"),
    ),
)

_BARE_PCT_RE = stdlib_re.compile(
    r"(?i)\b(?:tỷ\s+lệ|mức\s+độ)\s+(?:hoàn\s+thành|nghiệm\s+thu|khắc\s+phục\s+dứt\s+điểm)\s+"
    r"(?:chung\s+)?(?:đạt|là|ở\s+mức)\s+\d+(?:[.,]\d+)?%\s*[.!]"
)
_RATIO_SLASH_RE = stdlib_re.compile(r"\b\d+(?:[.,]\d+)*\s*/\s*\d+(?:[.,]\d+)*\b")
_TOTAL_DENOM_RE = stdlib_re.compile(r"(?i)\b(?:trên|trong)\s+tổng\s+số\s+\d")
_MD_HEADING_RE = stdlib_re.compile(r"^(#{1,6})\s+(.+?)\s*$")
_HEADING_WORD_RE = stdlib_re.compile(r"[A-Za-zÀ-ỹĐđ]{2,}")
_LIST_BULLET_RE = stdlib_re.compile(r"^\s*(?:[-*•◦–]|\d+[.)])\s+")
_COLON_RATIO_TIME_RE = stdlib_re.compile(r"\b\d{1,2}:\d{2}\b|\b\d+:\d+\b")
_NUMBERED_SUBHEADING_RE = stdlib_re.compile(r"^\d+(?:\.\d+)+")
_TABLE_SEP_CHARS_RE = stdlib_re.compile(r"^[\s|:\-+]+$")
_TABLE_PRONOUN_RE = stdlib_re.compile(r"(?i)\b(?:bạn|mình|tôi|chúng ta)\b")
_ALT_ATTR_RE = stdlib_re.compile(r'\balt=["\']([^"\'\n]+)["\']')
_ALT_DASH_TAGLINE_RE = stdlib_re.compile(r"\s+[-–—]\s+")
_PROMO_GRID_HTML_RE = stdlib_re.compile(
    r"(?is)<table\b[\s\S]{0,1200}(?:<b>|`|\*\*)0?1(?:</b>|`|\*\*)"
    r"[\s\S]{0,800}(?:<b>|`|\*\*)0?2(?:</b>|`|\*\*)"
    r"[\s\S]{0,800}(?:<b>|`|\*\*)0?3(?:</b>|`|\*\*)"
)
_TREE_COMMENT_RE = stdlib_re.compile(r"[├└│][──\s]*\S+.*?#\s*(.+)$")
_BACKTICK_META_LINE_RE = stdlib_re.compile(
    r"(?i)\b(?:tránh|cấm|không|thay vì|ví dụ|dấu hiệu|cách viết|sai|lỗi|VIS-\w+)\b"
)
_BACKTICK_SPAN_RE = stdlib_re.compile(r"`([^`\n]+)`")
_CODE_TOKEN_HINT_RE = stdlib_re.compile(r"[/_.*<>\\=+-]|\b(?:[A-Z]{2,}|\d+)\b")


def _parse_table_number(cell: str) -> float | None:
    cleaned = _CURRENCY_UNIT_RE.sub("", _PAREN_STRIP_RE.sub("", cell).strip()).strip()
    if not cleaned or not _PARSE_NUM_RE.match(cleaned):
        return None
    if _THOUSAND_DOT_NUM_RE.match(cleaned):
        return float(cleaned.replace(".", ""))
    return float(cleaned.replace(",", "."))


def _run_pattern_hygiene_checks(
    rule: RuleDefinition,
    buf: _ScanBuffer,
    prof: Profile | None,
    checks: Sequence[tuple[stdlib_re.Pattern[str], str, tuple[str, ...] | None]],
    gates: Sequence[bool] | None = None,
) -> list[Finding]:
    findings: list[Finding] = []
    active_gates = gates if gates is not None else (True,) * len(checks)
    for (pat, advice, sub_profs), gate_ok in zip(checks, active_gates, strict=True):
        if not gate_ok or (prof is not None and sub_profs is not None and prof.value not in sub_profs):
            continue
        m = pat.search(buf.masked_prose)
        if m:
            raw_hit = buf.raw_text[m.start() : m.end()]
            findings.append(
                make_finding(
                    rule,
                    buf,
                    m.start(),
                    repr(raw_hit) if m.group(0).strip() == "" else raw_hit,
                    custom_suggestion=advice,
                    override_profiles=sub_profs,
                )
            )
    return findings


def _check_prose_and_pct_hygiene(
    rule: RuleDefinition, buf: _ScanBuffer, prof: Profile | None, *, has_vi: bool
) -> list[Finding]:
    findings = _run_pattern_hygiene_checks(rule, buf, prof, _QUICK_HYGIENE_CHECKS)
    if not has_vi:
        return findings

    prose_lower = buf.masked_prose_lower
    vi_gates = (
        "%" in buf.masked_prose,
        "=" in buf.masked_prose,
        "“" in buf.masked_prose,
        any(k in prose_lower for k in ("kể cả", "bao gồm cả", "gộp cả", "tính cả")),
        any(k in prose_lower for k in ("đóng lỗi", "đánh dấu", "chuyển trạng thái", "xác nhận hoàn thành")),
        any(k in prose_lower for k in ("bù trừ", "triệt tiêu")),
    )
    findings.extend(_run_pattern_hygiene_checks(rule, buf, prof, _VI_HYGIENE_CHECKS, gates=vi_gates))

    if "%" in buf.masked_prose and (prof is None or prof == Profile.AUDIT_REPORT):
        for p_start, _, p_chunk in buf.para_spans:
            if "%" not in p_chunk:
                continue
            m_bp = _BARE_PCT_RE.search(p_chunk)
            if m_bp and not _RATIO_SLASH_RE.search(p_chunk) and not _TOTAL_DENOM_RE.search(p_chunk):
                abs_off = p_start + m_bp.start()
                findings.append(
                    make_finding(
                        rule,
                        buf,
                        abs_off,
                        buf.raw_text[abs_off : p_start + m_bp.end()].strip(),
                        custom_suggestion=(
                            "Nêu kèm 'Tử số/Mẫu số (Tỷ lệ %)' khi chốt tỷ lệ hoàn thành hoặc nghiệm thu "
                            "để tránh hiệu ứng phóng đại mẫu số nhỏ."
                        ),
                        override_profiles=("audit_report",),
                    )
                )
                break
    return findings


def _find_orphan_subheading(
    rule: RuleDefinition, buf: _ScanBuffer, headings: Sequence[tuple[int, int, str]]
) -> Finding | None:
    num_headings = len(headings)
    for idx, (lvl, _, h_txt) in enumerate(headings):
        direct_children: list[tuple[int, str]] = []
        for next_idx in range(idx + 1, num_headings):
            next_lvl, next_off, next_txt = headings[next_idx]
            if next_lvl <= lvl:
                break
            if next_lvl == lvl + 1:
                direct_children.append((next_off, next_txt))
        if len(direct_children) == 1:
            child_off, child_txt = direct_children[0]
            if _NUMBERED_SUBHEADING_RE.match(child_txt):
                return make_finding(
                    rule,
                    buf,
                    child_off,
                    child_txt,
                    custom_suggestion=(
                        f"Mục '{h_txt}' chỉ có duy nhất một mục con '{child_txt}'; nên bỏ cấp tiêu đề con lẻ loi này."
                    ),
                )
    return None


def _check_headings_and_colon_lists(rule: RuleDefinition, buf: _ScanBuffer, *, has_vi: bool) -> list[Finding]:
    findings: list[Finding] = []
    headings: list[tuple[int, int, str]] = []
    offset = 0
    for ln in buf.masked_full.splitlines(keepends=True):
        m_h = _MD_HEADING_RE.match(ln)
        if m_h:
            h_text = m_h.group(2)
            headings.append((len(m_h.group(1)), offset, h_text))
            calque_h = check_calque_heading(rule, buf, offset, buf.raw_text[offset : offset + len(ln)])
            if calque_h is not None:
                findings.append(calque_h)
            words = _HEADING_WORD_RE.findall(_PAREN_STRIP_RE.sub("", h_text))
            if (
                has_vi
                and len(words) >= 4
                and not h_text.isupper()
                and sum(1 for w in words if w[0].isupper() and not w.isupper()) >= max(4, math.ceil(len(words) * 0.8))
            ):
                findings.append(
                    make_finding(
                        rule,
                        buf,
                        offset,
                        ln.strip(),
                        custom_suggestion=(
                            "Chỉ viết hoa chữ cái đầu câu và danh từ riêng trong tiêu đề tiếng Việt, "
                            "không viết hoa đầu mỗi chữ kiểu tiếng Anh."
                        ),
                    )
                )
        elif _LIST_BULLET_RE.match(ln) and _COLON_RATIO_TIME_RE.sub("", ln).count(":") >= 2:
            findings.append(
                make_finding(
                    rule,
                    buf,
                    offset,
                    ln.strip()[:100],
                    custom_suggestion=(
                        "Không đặt từ 2 dấu hai chấm `:` trở lên trong cùng một mục liệt kê; "
                        "hãy đưa nhãn phụ vào ngoặc đơn."
                    ),
                )
            )
        offset += len(ln)

    orphan = _find_orphan_subheading(rule, buf, headings)
    if orphan is not None:
        findings.append(orphan)
    return findings


def _extract_markdown_table_blocks(raw_text: str) -> list[list[tuple[int, str]]]:
    table_blocks: list[list[tuple[int, str]]] = []
    curr_tbl: list[tuple[int, str]] = []
    offset = 0
    for ln in raw_text.splitlines(keepends=True):
        s = ln.strip()
        if "|" in s and (s.startswith("|") or len(s.split("|")) >= 3):
            curr_tbl.append((offset, s))
        else:
            if len(curr_tbl) >= 3:
                table_blocks.append(curr_tbl)
            curr_tbl = []
        offset += len(ln)
    if len(curr_tbl) >= 3:
        table_blocks.append(curr_tbl)
    return table_blocks


def _check_single_markdown_table(
    rule: RuleDefinition, buf: _ScanBuffer, tbl: Sequence[tuple[int, str]]
) -> list[Finding]:
    findings: list[Finding] = []
    data_rows = [
        (off, [c.strip() for c in row.strip("|").split("|")]) for off, row in tbl if not _TABLE_SEP_CHARS_RE.match(row)
    ]
    if len(data_rows) < 3:
        return findings

    if any(_parse_table_number(c) is not None for _, cells in data_rows[1:] for c in cells[1:]):
        for r_off, cells in data_rows[1:]:
            m_p = _TABLE_PRONOUN_RE.search(" ".join(cells))
            if m_p:
                findings.append(
                    make_finding(
                        rule,
                        buf,
                        r_off,
                        m_p.group(0),
                        custom_suggestion=(
                            "Không đưa đại từ nhân xưng (bạn, mình, tôi, chúng ta) vào bên trong bảng số liệu."
                        ),
                    )
                )
                break

    last_off, last_cells = data_rows[-1]
    if last_cells and last_cells[0].lower().startswith("tổng cộng"):
        body_rows = data_rows[1:-1]
        for col_i in range(1, len(last_cells)):
            tot = _parse_table_number(last_cells[col_i])
            if tot is None:
                continue
            vals = [_parse_table_number(r_cells[col_i]) for _, r_cells in body_rows if col_i < len(r_cells)]
            if vals and all(v is not None for v in vals):
                expected = round(sum(v for v in vals if v is not None), 4)
                if round(tot, 4) != expected:
                    findings.append(
                        make_finding(
                            rule,
                            buf,
                            last_off,
                            last_cells[col_i],
                            custom_suggestion=(
                                f"Dòng 'Tổng cộng' cột {col_i + 1} ghi {tot:g} "
                                f"nhưng tổng các dòng thành phần bằng {expected:g}."
                            ),
                        )
                    )
    return findings


def _check_tree_comments_and_backticks(
    rule: RuleDefinition, buf: _ScanBuffer, no_en_text: str, pre_html_masked: str
) -> list[Finding]:
    findings: list[Finding] = []
    if "├" in no_en_text or "└" in no_en_text:
        offset = 0
        for ln in no_en_text.splitlines(keepends=True):
            m_tree_cmt = _TREE_COMMENT_RE.search(ln)
            if m_tree_cmt:
                cmt_text = m_tree_cmt.group(1).strip()
                alnum_words = [w for w in cmt_text.split() if any(c.isalnum() for c in w)]
                if VI_DIACRITIC_RE.search(cmt_text) and len(alnum_words) > 10:
                    findings.append(
                        make_finding(
                            rule,
                            buf,
                            offset,
                            f"# {cmt_text[:70]}",
                            custom_suggestion=(
                                "Chú thích `#` trong cây thư mục quá dài (> 10 từ); "
                                "chỉ nên ghi cụm danh từ ngắn 2–8 từ thay vì nhồi cả câu thuyết minh vào sơ đồ cây."
                            ),
                        )
                    )
            offset += len(ln)

    if "`" in pre_html_masked:
        offset = 0
        for ln in pre_html_masked.splitlines(keepends=True):
            if "`" in ln and not _BACKTICK_META_LINE_RE.search(ln):
                vi_backticks = [
                    m.group(0)
                    for m in _BACKTICK_SPAN_RE.finditer(ln)
                    if 2 <= len(m.group(1)) <= 35
                    and VI_DIACRITIC_RE.search(m.group(1))
                    and not _CODE_TOKEN_HINT_RE.search(m.group(1))
                ]
                if len(vi_backticks) >= 3:
                    findings.append(
                        make_finding(
                            rule,
                            buf,
                            offset,
                            ", ".join(vi_backticks[:4]),
                            custom_suggestion=(
                                "Không bọc dấu backtick (`...`) quanh các từ tiếng Việt thông thường; "
                                "chỉ dùng backtick cho tên tệp, lệnh hoặc mã nguồn."
                            ),
                        )
                    )
            offset += len(ln)
    return findings


def _check_markup_trees_and_backticks(rule: RuleDefinition, buf: _ScanBuffer, *, has_vi: bool) -> list[Finding]:
    if not any(tok in buf.raw_text for tok in ("alt=", "<table", "<TABLE", "├", "└", "`")):
        return []
    findings: list[Finding] = []
    no_en_text = SemanticMasker.mask_frontmatter_and_english(buf.raw_text)
    pre_html_masked = SemanticMasker.mask_code_blocks_raw(no_en_text)

    if has_vi and "alt=" in pre_html_masked:
        for m_alt in _ALT_ATTR_RE.finditer(pre_html_masked):
            alt_val = m_alt.group(1).strip()
            w_count = len(alt_val.split())
            if w_count > 12 or (w_count >= 7 and _ALT_DASH_TAGLINE_RE.search(alt_val)):
                findings.append(
                    make_finding(
                        rule,
                        buf,
                        m_alt.start(),
                        buf.raw_text[m_alt.start() : m_alt.end()][:100],
                        custom_suggestion=(
                            "Thuộc tính alt của ảnh quá dài hoặc kèm khẩu hiệu quảng cáo; "
                            "chỉ nên ghi ngắn gọn 2–6 từ nêu tên hình."
                        ),
                    )
                )
    if "<table" in pre_html_masked.lower():
        m_promo_grid = _PROMO_GRID_HTML_RE.search(pre_html_masked)
        if m_promo_grid:
            findings.append(
                make_finding(
                    rule,
                    buf,
                    m_promo_grid.start(),
                    "<table>...01...02...03...",
                    custom_suggestion=(
                        "Bảng HTML gắn nhãn 01–04 kiểu trang quảng cáo lặp lại bảng chức năng chi tiết; "
                        "nên xóa hộp tóm tắt trùng lặp này."
                    ),
                )
            )
    findings.extend(_check_tree_comments_and_backticks(rule, buf, no_en_text, pre_html_masked))
    return findings


def run_document_and_table_hygiene(rule: RuleDefinition, buf: _ScanBuffer, prof: Profile | None) -> list[Finding]:
    has_vi = bool(VI_DIACRITIC_RE.search(buf.masked_prose))
    findings = _check_prose_and_pct_hygiene(rule, buf, prof, has_vi=has_vi)
    findings.extend(check_prose_proximity_echo(rule, buf, prof))
    findings.extend(_check_headings_and_colon_lists(rule, buf, has_vi=has_vi))
    for tbl in _extract_markdown_table_blocks(buf.raw_text):
        findings.extend(_check_single_markdown_table(rule, buf, tbl))
    findings.extend(_check_markup_trees_and_backticks(rule, buf, has_vi=has_vi))
    return findings
