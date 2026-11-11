"""Kiểm tra ngữ cảnh từ đa nghĩa, lỗi lặp từ gần nhau và tiêu đề dịch thô cho `vi_scanner`."""

from __future__ import annotations

import re as stdlib_re
from typing import TYPE_CHECKING

from _vi_masker import make_finding, sentence_around
from _vi_regex_anchors import safe_lower_preserve_len

if TYPE_CHECKING:
    from _vi_phrase_matcher import PhraseEntry
    from _vi_types import Finding, Profile, RuleDefinition, _ScanBuffer

_VI_CHAR_RE: stdlib_re.Pattern[str] = stdlib_re.compile(r"[à-ỹđÀ-ỸĐ]")
_PROSE_WORD_RE: stdlib_re.Pattern[str] = stdlib_re.compile(r"[A-Za-zÀ-ỹĐđ0-9]+")
_ECHO_SENT_SPLIT_RE: stdlib_re.Pattern[str] = stdlib_re.compile(
    r"[.!?…]+(?:[*_)\]\s]+)|;\s+|\n(?=[ \t]*(?:[-*•◦–>]|\d+[.)])[ \t]+)"
)
_BULLET_STRIP_RE: stdlib_re.Pattern[str] = stdlib_re.compile(r"^\s*(?:[-*•◦–>]|\d+[.)])\s+")
_CONTRAST_BRIDGE_RE: stdlib_re.Pattern[str] = stdlib_re.compile(r"(?i)\b(?:mà|nhưng|chứ\s+không|hay)\b")
_NON_LEGAL_PROFILES: tuple[str, ...] = (
    "general",
    "audit_report",
    "academic",
    "marketing",
    "social_media",
    "translation",
)

_BAN_CHI_EXEMPT_TAIL_RE: stdlib_re.Pattern[str] = stdlib_re.compile(r"(?i)^\s*(?:đạo|huy)\b")
_BANG_QUANG_LEAD_RE: stdlib_re.Pattern[str] = stdlib_re.compile(r"(?i)(?:thái\s+độ|vẻ|đứng|sống)\s+$")
_BANG_QUANG_TAIL_RE: stdlib_re.Pattern[str] = stdlib_re.compile(r"(?i)^\s*(?:trước|với)\b")
_NHAN_PREFIX_RE: stdlib_re.Pattern[str] = stdlib_re.compile(r"(?i)(?:xác|ghi|chấp|công|thừa)\s+$")
_YEU_DIEM_BAD_RE: stdlib_re.Pattern[str] = stdlib_re.compile(
    r"(?i)\b(?:khắc\s+phục|sửa\s+chữa|nhược\s+điểm|hạn\s+chế|bộc\s+lộ|che\s+giấu|chí\s+mạng|chết\s+người)\b"
)

_SON_SA_VALID_CTX_RE: stdlib_re.Pattern[str] = stdlib_re.compile(
    r"(?i)\b(?:chào(?:\s+hỏi)?|đón(?:\s+tiếp)?|tiếp\s+đón|bắt\s+chuyện|hỏi\s+thăm|vồn\s+vã|đon\s+đả|niềm\s+nở)\b"
)
_MIEN_TRU_VALID_LEAD_RE: stdlib_re.Pattern[str] = stdlib_re.compile(
    r"(?i)(?:quyền|điều\s+khoản|thỏa\s+thuận|cam\s+kết|chế\s+định|cơ\s+chế|hưởng)\s+$"
)
_MIEN_TRU_VALID_TAIL_RE: stdlib_re.Pattern[str] = stdlib_re.compile(
    r"(?i)^\s*(?:trách\s+nhiệm|nghĩa\s+vụ|thuế|ngoại\s+giao|lãnh\s+sự|pháp\s+lý|hình\s+sự|truy\s+cứu|bồi\s+thường)\b"
)
_CHUAN_MUC_VALID_TAIL_RE: stdlib_re.Pattern[str] = stdlib_re.compile(
    r"(?i)^\s*(?:kiểm\s+toán|kế\s+toán|báo\s+cáo\s+tài\s+chính|đạo\s+đức|hành\s+nghề|nghề\s+nghiệp|"
    r"quốc\s+tế|quốc\s+gia|pháp\s+lý|kỹ\s+thuật|chuyên\s+môn|ngành|vas|ifrs|ias|isa|iso|coso|basel)\b"
)
_DON_BAY_VALID_LEAD_RE: stdlib_re.Pattern[str] = stdlib_re.compile(
    r"(?i)(?:tỷ\s+lệ|hệ\s+số|cánh\s+tay|nguyên\s+lý|điểm\s+tựa|cơ\s+học)\s+$"
)
_DON_BAY_VALID_TAIL_RE: stdlib_re.Pattern[str] = stdlib_re.compile(
    r"(?i)^\s*(?:tài\s+chính|nợ|kinh\s+doanh|hoạt\s+động|tín\s+dụng|vốn|vật\s+lý)\b"
)
_LITERAL_METAPHOR_CTX: dict[str, stdlib_re.Pattern[str]] = {
    "bệ phóng": stdlib_re.compile(r"(?i)\b(?:tên\s+lửa|vệ\s+tinh|tàu\s+vũ\s+trụ|quân\s+sự|pháo)\b"),
    "chất xúc tác": stdlib_re.compile(r"(?i)\b(?:phản\s+ứng|hóa\s+học|enzyme|nhiệt\s+độ|dung\s+môi|kết\s+tủa)\b"),
    "chèo lái": stdlib_re.compile(r"(?i)\b(?:thuyền|tàu|ghe|xuồng|sông|biển|mái\s+chèo|sóng)\b"),
    "mở khóa": stdlib_re.compile(
        r"(?i)^\s*(?:tài\s+khoản|màn\s+hình|thiết\s+bị|điện\s+thoại|thẻ|cổng|cửa|két|ổ\s+khóa|phiên)\b"
    ),
    "ươm mầm": stdlib_re.compile(r"(?i)\b(?:hạt\s+giống|cây\s+con|vườn\s+ươm|nông\s+nghiệp|gieo\s+trồng|đất)\b"),
}
_PHYSICAL_RIGID_CTX_RE: stdlib_re.Pattern[str] = stdlib_re.compile(
    r"(?i)\b(?:ốc\s+vít|bu\s+lông|bê\s+tông|khớp\s+nối|bản\s+lề|trục|vật\s+liệu|nền\s+đất|khung\s+sắt|vách)\b"
)
_BAO_TOAN_VALID_CTX_RE: stdlib_re.Pattern[str] = stdlib_re.compile(
    r"(?i)\b(?:định\s+luật\s+bảo\s+toàn|bảo\s+toàn\s+(?:vốn|năng\s+lượng|khối\s+lượng|động\s+lượng|điện\s+tích))\b"
)

_EXEMPT_TAIL_BIGRAMS: frozenset[str] = frozenset(
    {
        "tỷ đồng",
        "triệu đồng",
        "nghìn đồng",
        "ngàn đồng",
        "phần trăm",
        "năm trước",
        "kỳ trước",
        "quý trước",
        "tháng trước",
        "tuần trước",
        "ngày làm",
        "làm việc",
        "yêu cầu",
        "quy định",
        "hệ thống",
        "dữ liệu",
        "báo cáo",
        "hồ sơ",
        "đơn vị",
        "giao dịch",
        "khách hàng",
    }
)
_ECHO_MODIFIER_BIGRAMS: frozenset[str] = frozenset(
    {
        "máy móc",
        "vòng vo",
        "rườm rà",
        "sáo rỗng",
        "gượng gạo",
        "cứng nhắc",
        "nặng nề",
        "lủng củng",
        "lửng lơ",
        "rập khuôn",
        "mơ hồ",
        "chung chung",
        "dài dòng",
        "lan man",
        "rối rắm",
        "chặt chẽ",
        "kỹ lưỡng",
        "mượt mà",
        "trơn tru",
        "linh hoạt",
        "nhanh chóng",
        "nghiêm trọng",
        "triệt để",
        "đồng bộ",
        "quyết liệt",
        "khách quan",
        "toàn diện",
        "sâu sắc",
        "rõ rệt",
        "mạnh mẽ",
        "vượt trội",
        "tối ưu",
        "tự nhiên",
        "chuẩn xác",
        "kịp thời",
        "khẩn trương",
        "cẩn thận",
        "tỉ mỉ",
        "sơ sài",
        "qua loa",
        "tùy tiện",
        "vội vàng",
    }
)
_CALQUE_HEADING_RE: stdlib_re.Pattern[str] = stdlib_re.compile(
    r"(?i)^(?:"
    r"cách\s+sử\s+dụng(?:\s+(?:dòng\s+lệnh|cli|terminal|công\s+cụ|lệnh|api|thư\s+viện|phần\s+mềm|script|cơ\s+bản|nâng\s+cao))?"
    r"|sử\s+dụng\s+(?:dòng\s+lệnh|cli|terminal|cơ\s+bản|nâng\s+cao)"
    r"|bảng\s+nội\s+dung"
    r"|(?:các\s+)?thực\s+hành\s+tốt\s+nhất"
    r"|(?:các\s+)?vấn\s+đề\s+đã\s+biết"
    r"|tại\s+sao\s+lại\s+là\s+\S.*"
    r"|làm\s+thế\s+nào\s+để\s+\S.*"
    r")$"
)
_MARKDOWN_DECOR_RE: stdlib_re.Pattern[str] = stdlib_re.compile(r"[`*_~]+")


def is_lex001_context_exempt(target_text: str, start: int, end: int) -> bool:
    """Kiểm tra ngữ cảnh hợp lệ cho các nhánh biểu thức chính quy của `VIS-LEX-001`."""
    sent = sentence_around(target_text, start, end)
    low_hit = " ".join(target_text[start:end].split()).casefold()
    if "thực chứng" in low_hit:
        return bool(stdlib_re.search(r"(?i)\b(?:chủ\s+nghĩa|triết\s+học|trường\s+phái)\s+thực\s+chứng\b", sent))
    if low_hit.endswith(" cứng"):
        return bool(_PHYSICAL_RIGID_CTX_RE.search(sent))
    if "bảo toàn" in low_hit:
        return bool(_BAO_TOAN_VALID_CTX_RE.search(sent))
    return False


def _check_legacy_homograph(key: str, prose_text: str, start: int, end: int, prof: Profile | None) -> bool | None:
    res: bool | None = None
    if key == "ban chỉ":
        res = not bool(_BAN_CHI_EXEMPT_TAIL_RE.match(prose_text[end : end + 12]))
    elif key == "kho mã nguồn":
        res = "thư mục" not in safe_lower_preserve_len(sentence_around(prose_text, start, end))
    elif key == "khuyến mãi":
        res = prof is None or prof.value in ("audit_report", "legal")
    elif key == "góa phụ":
        res = prose_text[max(0, start - 6) : start].casefold().endswith("nam ")
    elif key == "bàng quang":
        res = bool(
            _BANG_QUANG_LEAD_RE.search(prose_text[max(0, start - 15) : start])
            or _BANG_QUANG_TAIL_RE.match(prose_text[end : end + 12])
        )
    elif key == "nhận sẵn sàng":
        res = not bool(_NHAN_PREFIX_RE.search(prose_text[max(0, start - 8) : start]))
    elif key == "yếu điểm":
        res = bool(_YEU_DIEM_BAD_RE.search(sentence_around(prose_text, start, end)))
    return res


def _check_polysemy_term(key: str, sent: str, lead: str, tail: str, prof: Profile | None) -> bool | None:
    res: bool | None = None
    if key == "sồn sã":
        res = not bool(_SON_SA_VALID_CTX_RE.search(sent))
    elif key == "miễn trừ":
        res = (
            False
            if (prof is not None and prof.value == "legal")
            else not bool(_MIEN_TRU_VALID_LEAD_RE.search(lead) or _MIEN_TRU_VALID_TAIL_RE.match(tail))
        )
    elif key == "chuẩn mực":
        res = not bool(_CHUAN_MUC_VALID_TAIL_RE.match(tail))
    elif key == "đòn bẩy":
        res = not bool(_DON_BAY_VALID_LEAD_RE.search(lead) or _DON_BAY_VALID_TAIL_RE.match(tail))
    elif key.endswith(" cứng"):
        res = not bool(_PHYSICAL_RIGID_CTX_RE.search(sent))
    elif key in _LITERAL_METAPHOR_CTX:
        target = tail if key == "mở khóa" else sent
        res = not bool(_LITERAL_METAPHOR_CTX[key].search(target))
    return res


def check_contextual_vocab_hit(
    entry: PhraseEntry, prose_text: str, start: int, end: int, prof: Profile | None
) -> bool | None:
    """Lọc ngữ cảnh cho từ đồng hình, từ đa nghĩa pháp lý/kế toán và ẩn dụ sáo rỗng."""
    key = entry.term_key
    legacy = _check_legacy_homograph(key, prose_text, start, end, prof)
    if legacy is not None:
        return legacy
    sent = sentence_around(prose_text, start, end)
    return _check_polysemy_term(key, sent, prose_text[max(0, start - 28) : start], prose_text[end : end + 38], prof)


def check_calque_heading(rule: RuleDefinition, buf: _ScanBuffer, offset: int, raw_line: str) -> Finding | None:
    """Bắt các tiêu đề Markdown dịch thô từ tài liệu tiếng Anh (`Usage`, `Table of Contents`, `Best Practices`)."""
    stripped = raw_line.strip()
    if not stripped.startswith("#"):
        return None
    title_body = _MARKDOWN_DECOR_RE.sub("", stripped.lstrip("#").strip())
    title_norm = " ".join(title_body.split())
    if not _CALQUE_HEADING_RE.match(title_norm):
        return None
    return make_finding(
        rule,
        buf,
        offset,
        stripped,
        custom_suggestion=(
            "Tiêu đề mục dịch từng chữ từ tài liệu tiếng Anh; "
            "hãy đổi sang cụm động từ hoặc danh từ tự nhiên ('Chạy từ dòng lệnh', 'Mục lục', 'Nguyên tắc thực hành')."
        ),
    )


def _find_tail_echo_in_para(p_start: int, para_text: str) -> tuple[int, int, str] | None:
    pos = 0
    prev_tail = ""
    for m_sp in [*_ECHO_SENT_SPLIT_RE.finditer(para_text), None]:
        seg_end = m_sp.start() if m_sp is not None else len(para_text)
        raw_seg = para_text[pos:seg_end]
        m_bul = _BULLET_STRIP_RE.match(raw_seg)
        shift = m_bul.end() if m_bul else 0
        toks = [(m.group(0).casefold(), m.start(), m.end()) for m in _PROSE_WORD_RE.finditer(raw_seg[shift:])]
        if len(toks) >= 4:
            tail = f"{toks[-2][0]} {toks[-1][0]}"
            if (
                tail == prev_tail
                and _VI_CHAR_RE.search(tail)
                and tail not in _EXEMPT_TAIL_BIGRAMS
                and not any(ch.isdigit() for ch in tail)
            ):
                base = p_start + pos + shift
                return base + toks[-2][1], base + toks[-1][2], tail
            prev_tail = tail
        else:
            prev_tail = ""
        if m_sp is not None:
            pos = m_sp.end()
    return None


def _find_modifier_echo_in_para(p_start: int, para_text: str) -> tuple[int, int, str] | None:
    toks = [(m.group(0).casefold(), m.start(), m.end()) for m in _PROSE_WORD_RE.finditer(para_text)]
    seen_at: dict[str, tuple[int, int]] = {}
    for idx in range(len(toks) - 1):
        bg = f"{toks[idx][0]} {toks[idx + 1][0]}"
        if bg not in _ECHO_MODIFIER_BIGRAMS:
            continue
        prev = seen_at.get(bg)
        if prev is not None and 2 <= (idx - prev[0]) <= 14:
            between = para_text[prev[1] : toks[idx][1]]
            if not ("\n" in between and _BULLET_STRIP_RE.search(between)) and not _CONTRAST_BRIDGE_RE.search(between):
                return p_start + toks[idx][1], p_start + toks[idx + 1][2], bg
        seen_at[bg] = (idx, toks[idx + 1][2])
    return None


def _extract_table_row_cells(row_offset: int, row_line: str) -> list[tuple[int, str]]:
    cells: list[tuple[int, str]] = []
    c_pos = 0
    for part in row_line.split("|"):
        if part.strip():
            cells.append((row_offset + c_pos, part))
        c_pos += len(part) + 1
    return cells


def _iter_echo_units(buf: _ScanBuffer) -> list[tuple[int, str]]:
    units: list[tuple[int, str]] = []
    for p_start, p_end, _ in buf.para_spans:
        full_para = buf.masked_full[p_start:p_end]
        if full_para.lstrip().startswith("#"):
            continue
        if "|" not in full_para:
            units.append((p_start, full_para))
            continue
        pos = 0
        for ln in full_para.splitlines(keepends=True):
            st = ln.strip()
            if st.startswith("|") and st.endswith("|") and any(c.isalpha() for c in st):
                units.extend(_extract_table_row_cells(p_start + pos, ln))
            pos += len(ln)
    return units


def check_prose_proximity_echo(rule: RuleDefinition, buf: _ScanBuffer, prof: Profile | None) -> list[Finding]:
    """Bắt lỗi điệp cụm 2 chữ cuối hai câu liền kề hoặc lặp từ ghép miêu tả trong phạm vi 14 từ (`VIS-STRUCT-002`)."""
    if prof is not None and prof.value == "legal":
        return []
    findings: list[Finding] = []
    for u_start, u_text in _iter_echo_units(buf):
        hit = _find_tail_echo_in_para(u_start, u_text) or _find_modifier_echo_in_para(u_start, u_text)
        if hit is not None:
            abs_start, abs_end, phrase = hit
            findings.append(
                make_finding(
                    rule,
                    buf,
                    abs_start,
                    " ".join(buf.raw_text[abs_start:abs_end].split()),
                    custom_suggestion=(
                        f"Lặp cụm '{phrase}' ở hai vị trí quá gần nhau làm nhịp câu nặng và đơn điệu; "
                        "hãy lược bớt hoặc đổi cấu trúc ở câu sau."
                    ),
                    override_profiles=_NON_LEGAL_PROFILES,
                )
            )
    return findings
