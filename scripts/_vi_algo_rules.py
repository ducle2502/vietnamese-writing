"""Bộ miễn trừ ngôn ngữ học/ngữ cảnh và các quy tắc thuật toán về nhịp câu, từ mượn, độ dài & diễn đạt vòng vo."""

from __future__ import annotations

import math
import re as stdlib_re
from typing import TYPE_CHECKING

from _vi_masker import SemanticMasker, make_finding, sentence_around
from _vi_phrase_matcher import PhraseHit, select_first_reverse_calque, tokenize_prose
from _vi_rules_data import DEFAULT_VOCAB
from _vi_types import Finding, Profile, RuleDefinition, VocabCatalog, _ScanBuffer

if TYPE_CHECKING:
    from collections.abc import Sequence

VI_DIACRITIC_RE = stdlib_re.compile(
    r"[àáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ"
    r"ÀÁẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬÈÉẺẼẸÊẾỀỂỄỆÌÍỈĨỊÒÓỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÙÚỦŨỤƯỨỪỬỮỰỲÝỶỸỴĐ]"
)

_EX_YEAR_RE = stdlib_re.compile(r"\b(?:19|20)\d{2}\b")
_EX_PCT_RE = stdlib_re.compile(r"\b\d+(?:[.,]\d+)?%")
_EX_AI003_GROWTH_RE = stdlib_re.compile(r"(?i)ngày càng\s+(?:phát triển|biến đổi)")
_EX_19XX_RE = stdlib_re.compile(r"\b1\d{3}\b")
_EX_RHET003_RE = stdlib_re.compile(
    r"(?i)(?:\b\d+\s*(?:m|km|cm|mm|hải lý)\b|\bthế kỷ\s+[ivx]+\b|\b1\d{3}\b|"
    r"\b(?:tàu thuyền|hàng hải|mực nước biển|dệt|tơ tằm|khung cửi)\b)"
)
_EX_RHET004_RE = stdlib_re.compile(r"(?i)^từ\s+(?:ngày|tháng|năm|quý|đợt|lần|mức|khoảng|số|\d+)")
_EX_RHET005_TAIL_RE = stdlib_re.compile(r"^\s*(?:\(|\[|theo\s+[A-ZÀ-ỸĐ])")
_EX_ATTRIB_HEAD_RE = stdlib_re.compile(r"(?i)^(?:nhiều\s+nghiên\s+cứu|các\s+nghiên\s+cứu|các\s+chuyên\s+gia|báo\s+cáo)")
_EX_TRANS001_RE = stdlib_re.compile(r"(?i)\bđược\s+xác định\s+bởi\s+công thức\b")
_EX_LEX001_RE = stdlib_re.compile(r"(?i)\b(?:chủ nghĩa|triết học|trường phái)\s+thực chứng\b")
_SENT_EXEMPT_PATTERNS: dict[str, stdlib_re.Pattern[str]] = {
    "VIS-RHET-002": _EX_19XX_RE,
    "VIS-RHET-003": _EX_RHET003_RE,
    "VIS-TRANS-001": _EX_TRANS001_RE,
    "VIS-LEX-001": _EX_LEX001_RE,
}
_LINGUISTIC_EXEMPT_RULES: frozenset[str] = frozenset(
    {
        "VIS-AI-003",
        "VIS-RHET-004",
        "VIS-RHET-005",
        "VIS-CLICHE-001",
        "VIS-CLICHE-004",
        "VIS-TRANS-005",
        "VIS-TRANS-007",
        *_SENT_EXEMPT_PATTERNS,
    }
)

_EX_MKT_PRAISE_RE = stdlib_re.compile(r"(?i)\b(?:minh\s+chứng\s+sống\s+động|vai\s+trò\s+then\s+chốt)\b")
_EX_LEGAL_CLAUSE_RE = stdlib_re.compile(
    r"(?i)\b(?:điều|khoản|mục|chương|nghị định|thông tư|luật|bộ luật|hợp đồng)\s+(?:số\s+)?\d+"
)
_EX_LEGAL_GLOSSARY_RE = stdlib_re.compile(r"(?i)\b(?:giải thích từ ngữ|bên a|bên b)\b")
_EX_LEGAL_AGENCY_RE = stdlib_re.compile(r"(?i)\b(?:luật\s+thương mại|bộ luật\s+dân sự|đại lý\s+thương mại|ủy thác)\b")
_LEGAL_SENT_PATTERNS: dict[str, stdlib_re.Pattern[str]] = {
    "VIS-RHET-001": _EX_LEGAL_CLAUSE_RE,
    "VIS-CLICHE-002": _EX_LEGAL_AGENCY_RE,
}

_EXEMPT_OPENERS: frozenset[str] = frozenset({"điều", "bước", "phần", "giai", "mục", "chương", "khoản", "nhóm"})
_LINE_PREFIX_STRIP_RE = stdlib_re.compile(r"^\s*(?:[-*•◦–>#]|\d+[.)])+\s*")
_VI_ALPHA_WORD_RE = stdlib_re.compile(r"[A-Za-zÀ-ỹĐđ]+")
_LEADING_VI_WORD_RE = stdlib_re.compile(r"^[A-Za-zÀ-ỹĐđ]+")
_MD_SEP_ROW_RE = stdlib_re.compile(r"^\|[\s:\-|]+\|$")
_TABLE_SYNONYM_VERBS: frozenset[str] = frozenset(
    {"khóa", "thiết", "xây", "hiện", "lập", "phát", "tính", "soạn", "cấu", "triển"}
)

_RAW_TECH_ID_RE = stdlib_re.compile(
    r"\b(?:[A-Z]{2,}(?:_[A-Z0-9]{2,})+|[A-Z]{2,}(?:\.[A-Z0-9]{2,}){2,})\b"
    r"|\b(?:INNER\s+JOIN|LEFT\s+JOIN|FULL\s+OUTER\s+JOIN|COALESCE|VLOOKUP|GROUP\s+BY)\b"
    r"|\b(?:COUNT|SUM|ABS)\s*\("
)
_LOWER_ASCII_WORD_RE = stdlib_re.compile(r"(?<![A-Za-z0-9_./-])[a-z]{4,25}(?![A-Za-z0-9_./-])")
_EN_PHONOTACTIC_RE = stdlib_re.compile(
    r"(?:[fjwz]|^(?:bl|br|cl|cr|dr|fl|fr|gl|gr|pl|pr|sc|sk|sl|sm|sn|sp|st|sw|tw|wr)"
    r"|(?:ck|ct|ft|ld|lp|lt|mp|nd|nk|nt|pt|rd|rk|rt|sh|sk|sp|st|xt)s?$"
    r"|(?:tion|sion|ment|ness|able|ible|ship|line|back|over|down|flow|work|book|list|test|load|lock|scan|point|terface|ning)s?$)"
)

_HR_LINE_RE = stdlib_re.compile(r"^\s*[-*_]{3,}\s*$")
_BR_TAG_RE = stdlib_re.compile(r"(?i)<br\s*/?>")
_SENT_BOUNDARY_RE = stdlib_re.compile(
    r"[.!?…]+(?:[*_)\"”’\]])*\s+|\||;\s*(?=[•◦*-]|\d+[.)]\s)"
    r"|\n[ \t]*\n+|\n(?=[ \t]*(?:[-*•◦–>]|\d+[.)])[ \t]+)|:\s*\n"
)
_SENT_LEAD_STRIP_RE = stdlib_re.compile(r"^(?:\s*(?:[-*•◦–>]|\d+[.)])\s+)?[\s*_([>]*")
_SENT_WORD_RE = stdlib_re.compile(r"[0-9A-Za-zÀ-ỹĐđ]+(?:[.,/-][0-9A-Za-zÀ-ỹĐđ]+)*")
_CLAUSE_COMMA_RE = stdlib_re.compile(r"(?<!\d),(?!\d)(?![^(\n]*\))")
_NON_LEGAL_PROFILES = ("general", "audit_report", "academic", "marketing", "social_media", "translation")
_ROUNDABOUT_PHRASE_RE = stdlib_re.compile(
    r"(?i)(?:(?:^|[,;]\s*)thông\s+qua\s+việc\s+[a-zà-ỹđ]+"
    r"|\b(?:liên\s+quan\s+đến|xoay\s+quanh|đối\s+với)\s+(?:vấn\s+đề|câu\s+chuyện|nội\s+dung\s+về)\b"
    r"|(?:^|[,;]\s*)đối\s+với\s+việc\s+(?:thực\s+hiện|triển\s+khai|áp\s+dụng|xử\s+lý|kiểm\s+tra|rà\s+soát|quản\s+lý|vận\s+hành|sử\s+dụng|xây\s+dựng|tổ\s+chức)\b"
    r"|(?:^|[,;]\s*)trên\s+cơ\s+sở\s+(?:việc|những\s+kết\s+quả\s+đã|các\s+nội\s+dung\s+đã)\b"
    r"|\b(?:xuất\s+phát\s+từ|dựa\s+trên)\s+(?:một\s+)?thực\s+tế\s+(?:là|rằng)\b"
    r"|\bthực\s+tế\s+cho\s+thấy\s+một\s+điều\s+(?:là|rằng)\b"
    r"|\b(?:nhằm\s+mục\s+đích\s+để|với\s+mục\s+đích\s+nhằm|với\s+mục\s+tiêu\s+nhằm|để\s+có\s+thể\s+(?:tiến\s+hành|thực\s+hiện)|nhằm\s+hướng\s+(?:tới|đến)\s+việc)\b"
    r"|\b(?:không\s+thể\s+phủ\s+nhận\s+(?:một\s+điều\s+)?rằng|dễ\s+dàng\s+nhận\s+thấy\s+(?:một\s+điều\s+)?(?:là|rằng)|cần\s+(?:phải\s+)?(?:nhấn\s+mạnh|lưu\s+ý)\s+một\s+điều\s+(?:là|rằng)|có\s+một\s+thực\s+tế\s+không\s+thể\s+(?:phủ\s+nhận|chối\s+cãi)\s+(?:là|rằng)|điều\s+đáng\s+nói\s+ở\s+đây\s+là)\b)"
)
_BLOATED_VIEC_OPENER_RE = stdlib_re.compile(
    r"(?i)^việc\s+(?:\S+\s+){13,35}?(?:đã|đang|sẽ|vẫn|cũng|làm|giúp|gây|khiến|dẫn\s+đến|mang\s+lại|tạo\s+ra|đòi\s+hỏi|cho\s+thấy)\b"
)
_SUBORDINATE_HINGE_RE = stdlib_re.compile(
    r"(?i)\b(?:mặc\s+dù|tuy\s+rằng|bên\s+cạnh\s+việc|song\s+song\s+với\s+việc|"
    r"kết\s+hợp\s+với\s+việc|đồng\s+thời\s+với\s+việc|trong\s+quá\s+trình\s+(?:thực\s+hiện|triển\s+khai)|"
    r"qua\s+đó\s+góp\s+phần|từ\s+đó\s+dẫn\s+đến\s+việc|kéo\s+theo\s+việc)\b"
)


def _is_direct_slice_exempt(rule_id: str, target_text: str, start: int, end: int) -> bool:
    matched = target_text[start:end].strip()
    low = matched.casefold()
    if rule_id == "VIS-RHET-004":
        return bool(_EX_RHET004_RE.match(matched))
    if rule_id == "VIS-RHET-005":
        return bool(_EX_RHET005_TAIL_RE.match(target_text[end : end + 45]))
    if rule_id in ("VIS-CLICHE-001", "VIS-CLICHE-004") and _EX_ATTRIB_HEAD_RE.match(matched):
        return bool(_EX_RHET005_TAIL_RE.match(target_text[end : end + 45]))
    if rule_id == "VIS-TRANS-005":
        return low.startswith("hỗ trợ ") and target_text[end : end + 2] == ", "
    return rule_id == "VIS-TRANS-007" and low.startswith("tuy nhiên")


def is_linguistically_exempt(rule_id: str, target_text: str, start: int, end: int) -> bool:
    """Các trường hợp miễn trừ phổ quát về mặt ngôn ngữ học (không gắn tên riêng dự án)."""
    if rule_id not in _LINGUISTIC_EXEMPT_RULES:
        return False
    if _is_direct_slice_exempt(rule_id, target_text, start, end):
        return True
    sent = sentence_around(target_text, start, end)
    if rule_id == "VIS-AI-003":
        return bool(
            _EX_YEAR_RE.search(sent)
            and _EX_PCT_RE.search(sent)
            and not _EX_AI003_GROWTH_RE.search(target_text[start:end])
        )
    pat = _SENT_EXEMPT_PATTERNS.get(rule_id)
    return bool(pat and pat.search(sent))


def is_profile_exempt(rule_id: str, target_text: str, start: int, end: int, prof: Profile | None) -> bool:
    """Miễn trừ riêng theo từng nhóm văn bản cụ thể khi người dùng truyền `--profile` đơn lẻ."""
    if prof is None:
        return False
    sliced = target_text[start:end].strip()
    if rule_id == "VIS-FMT-003" and sliced == ";" and prof in (Profile.AUDIT_REPORT, Profile.ACADEMIC, Profile.LEGAL):
        return True
    if rule_id == "VIS-RHET-003" and prof in (Profile.MARKETING, Profile.SOCIAL_MEDIA):
        return len(sliced.split()) <= 3 or bool(_EX_MKT_PRAISE_RE.search(sliced))
    if prof != Profile.LEGAL:
        return False
    pat = _LEGAL_SENT_PATTERNS.get(rule_id)
    return bool(
        (_EX_LEGAL_GLOSSARY_RE.search(target_text) if rule_id == "VIS-FMT-001" else False)
        or (pat and pat.search(sentence_around(target_text, start, end)))
    )


def _check_paragraph_cv(rule: RuleDefinition, buf: _ScanBuffer) -> Finding | None:
    para_spans = [
        (s, e, p)
        for s, e, p in buf.para_spans
        if not p.lstrip().startswith(("#", "|", "-", "*", "•")) and len(p.split()) >= 5
    ]
    if len(para_spans) < rule.threshold.min_paras or rule.threshold.cv_max is None:
        return None
    lengths = [len(p.split()) for _, _, p in para_spans]
    mean_len = sum(lengths) / len(lengths)
    if mean_len <= 0:
        return None
    cv = math.sqrt(sum((x - mean_len) ** 2 for x in lengths) / len(lengths)) / mean_len
    if cv >= rule.threshold.cv_max:
        return None
    return make_finding(
        rule,
        buf,
        para_spans[0][0],
        f"[CV={cv:.3f} < {rule.threshold.cv_max} trên {len(para_spans)} đoạn]",
        custom_suggestion="Thay đổi độ dài câu và đoạn theo mạch ý thực tế, tránh chia đoạn đều như khuôn đúc.",
    )


def _check_consecutive_openers(rule: RuleDefinition, buf: _ScanBuffer) -> Finding | None:
    openers: list[tuple[int, str]] = []
    offset = 0
    for ln in buf.masked_full.splitlines(keepends=True):
        if not ln.strip().startswith(("|", "#")):
            clean_ln = _LINE_PREFIX_STRIP_RE.sub("", ln).strip()
            words = _VI_ALPHA_WORD_RE.findall(clean_ln)
            if len(words) >= 4 and len(words[0]) >= 3:
                first = words[0].casefold()
                if first not in _EXEMPT_OPENERS:
                    openers.append((offset, first))
        offset += len(ln)
    for i in range(len(openers) - 2):
        w0 = openers[i][1]
        if w0 == openers[i + 1][1] == openers[i + 2][1]:
            return make_finding(
                rule,
                buf,
                openers[i][0],
                f"Lặp từ mở đầu x3: '{w0}'",
                custom_suggestion="Đổi chủ ngữ mở đầu từng câu thay vì lặp cùng một từ ở 3 câu liên tiếp.",
            )
    return None


def _find_rotated_verb_column(body: Sequence[tuple[int, list[str]]]) -> tuple[int, list[str]] | None:
    num_cols = max(len(cells) for _, cells in body)
    for col_idx in range(1, num_cols):
        first_words: list[str] = []
        for _, cells in body:
            if col_idx < len(cells):
                m_lead = _LEADING_VI_WORD_RE.match(cells[col_idx])
                if m_lead and m_lead.group(0).casefold() in _TABLE_SYNONYM_VERBS:
                    first_words.append(m_lead.group(0).casefold())
        if len(first_words) >= 4 and len(set(first_words)) >= 4:
            return col_idx, first_words
    return None


def _check_table_verb_rotation(rule: RuleDefinition, buf: _ScanBuffer) -> list[Finding]:
    findings: list[Finding] = []
    table_rows: list[tuple[int, list[str]]] = []
    offset = 0
    for ln in [*buf.raw_text.splitlines(keepends=True), "\n"]:
        s = ln.strip()
        if s.startswith("|") and s.endswith("|") and not _MD_SEP_ROW_RE.match(s):
            table_rows.append((offset, [c.strip() for c in s.strip("|").split("|")]))
        else:
            if len(table_rows) >= 5:
                body = table_rows[1:]
                rotated = _find_rotated_verb_column(body)
                if rotated is not None:
                    col_idx, first_words = rotated
                    findings.append(
                        make_finding(
                            rule,
                            buf,
                            body[0][0],
                            f"Xoay vòng động từ đầu cột {col_idx + 1}: {', '.join(first_words[:5])}",
                            custom_suggestion=(
                                "Trong bảng kỹ thuật hoặc bảng phân công, bỏ động từ dẫn đầu "
                                "và ghi thẳng tên tệp, lớp hoặc đầu việc."
                            ),
                        )
                    )
            table_rows = []
        offset += len(ln)
    return findings


def run_monotony_rule(rule: RuleDefinition, buf: _ScanBuffer, _prof: Profile | None) -> list[Finding]:
    findings: list[Finding] = []
    cv_finding = _check_paragraph_cv(rule, buf)
    if cv_finding is not None:
        findings.append(cv_finding)
    opener_finding = _check_consecutive_openers(rule, buf)
    if opener_finding is not None:
        findings.append(opener_finding)
    findings.extend(_check_table_verb_rotation(rule, buf))
    return findings


def _find_foreign_word_finding(
    rule: RuleDefinition, buf: _ScanBuffer, prof: Profile | None, vocab: VocabCatalog = DEFAULT_VOCAB
) -> Finding | None:
    if not VI_DIACRITIC_RE.search(buf.masked_prose):
        return None
    checked_non_en: set[str] = set()
    for m_word in _LOWER_ASCII_WORD_RE.finditer(buf.masked_prose):
        word = m_word.group(0).lower()
        if word in checked_non_en or word in vocab.universal_loanwords:
            continue
        if word == "request" and buf.masked_prose[max(0, m_word.start() - 6) : m_word.start()].lower().endswith(
            "pull "
        ):
            continue
        if not _EN_PHONOTACTIC_RE.search(word):
            checked_non_en.add(word)
            continue
        if not VI_DIACRITIC_RE.search(sentence_around(buf.masked_prose, m_word.start(), m_word.end())):
            continue
        if word in vocab.all_allowed_loanwords:
            if prof is None or prof == Profile.AUDIT_REPORT:
                advice = (
                    f"Từ '{word}' thông dụng ở công sở nhưng nên cân nhắc Việt hóa nếu trình cấp quản trị."
                    if prof is None
                    else f"Cân nhắc diễn đạt '{word}' bằng tiếng Việt chuẩn trong báo cáo kiểm toán/quản trị."
                )
                return make_finding(
                    rule,
                    buf,
                    m_word.start(),
                    buf.raw_text[m_word.start() : m_word.end()],
                    custom_suggestion=advice,
                    override_profiles=("audit_report",),
                )
            continue
        return make_finding(
            rule,
            buf,
            m_word.start(),
            buf.raw_text[m_word.start() : m_word.end()],
            custom_suggestion=(
                f"Từ tiếng Anh '{word}' chưa nằm trong nhóm từ quen dùng; nên diễn đạt bằng tiếng Việt phù hợp."
            ),
        )
    return None


def run_loanword_and_jargon_rule(
    rule: RuleDefinition,
    buf: _ScanBuffer,
    prof: Profile | None,
    vocab: VocabCatalog = DEFAULT_VOCAB,
    rev_hits: Sequence[PhraseHit] | None = None,
) -> list[Finding]:
    findings: list[Finding] = []
    candidates = (
        rev_hits if rev_hits is not None else vocab.phrase_trie.scan_all(tokenize_prose(buf.masked_prose_lower))[1]
    )
    m_rev = select_first_reverse_calque(candidates, buf.masked_prose, prof)
    if m_rev is not None:
        raw_hit = buf.raw_text[m_rev.start() : m_rev.end()]
        hint = m_rev.entry.hint
        if m_rev.entry.is_code_mixing:
            advice = f"Tránh chêm từ ngoại lai lửng lơ; nên diễn đạt bằng tiếng Việt: '{hint}'."
        else:
            advice = (
                f"Giữ nguyên từ thông dụng đã quen dùng ({hint}) thay vì dịch từng chữ."
                if hint
                else "Giữ nguyên từ thông dụng đã quen dùng (email, pull request, repo, web) thay vì dịch từng chữ."
            )
        findings.append(make_finding(rule, buf, m_rev.start(), raw_hit, custom_suggestion=advice))
    if prof in (None, Profile.AUDIT_REPORT, Profile.SOCIAL_MEDIA):
        m_tech = _RAW_TECH_ID_RE.search(buf.masked_prose)
        if m_tech:
            findings.append(
                make_finding(
                    rule,
                    buf,
                    m_tech.start(),
                    buf.raw_text[m_tech.start() : m_tech.end()],
                    custom_suggestion=(
                        "Diễn đạt tên bảng hoặc phép tính kỹ thuật bằng ngôn ngữ nghiệp vụ dễ hiểu cho người đọc."
                    ),
                    override_profiles=("audit_report", "social_media"),
                )
            )
    foreign_finding = _find_foreign_word_finding(rule, buf, prof, vocab)
    if foreign_finding is not None:
        findings.append(foreign_finding)
    return findings


def _prepare_length_prose(buf: _ScanBuffer) -> str:
    """Che ngoặc kép, dòng kẻ bảng, tiêu đề và sơ đồ cây nhưng giữ nguyên độ dài gốc."""
    masked = SemanticMasker.QUOTED_SPEECH_RE.sub(
        lambda m: "".join("\n" if ch == "\n" else " " for ch in m.group(0)),
        buf.masked_full,
    )
    if "<br" in buf.raw_text.lower():
        chars = list(masked)
        for m_br in _BR_TAG_RE.finditer(buf.raw_text):
            if chars[m_br.start()] == " ":
                chars[m_br.start()] = "|"
        masked = "".join(chars)
    out: list[str] = []
    for ln in masked.splitlines(keepends=True):
        st = ln.strip()
        is_skip = SemanticMasker.MD_TABLE_SEP_RE.match(st) or st.startswith("#") or _HR_LINE_RE.match(ln)
        if is_skip or any(ch in ln for ch in ("├", "└", "│")):
            out.append("".join("\n" if ch == "\n" else " " for ch in ln))
        else:
            out.append(ln)
    return "".join(out)


def _iter_prose_sentences(prose_buf: str) -> list[tuple[int, str]]:
    spans: list[tuple[int, str]] = []
    pos = 0
    for m in _SENT_BOUNDARY_RE.finditer(prose_buf):
        spans.append((pos, prose_buf[pos : m.start()]))
        pos = m.end()
    spans.append((pos, prose_buf[pos:]))

    results: list[tuple[int, str]] = []
    for raw_start, raw_chunk in spans:
        m_lead = _SENT_LEAD_STRIP_RE.match(raw_chunk)
        shift = m_lead.end() if m_lead else 0
        trimmed = raw_chunk[shift:].rstrip()
        if trimmed:
            results.append((raw_start + shift, trimmed))
    return results


def _find_roundabout_hit(sent_text: str, wc: int, prof: Profile | None) -> tuple[int, str, bool] | None:
    """Trả về `(offset_trong_cau, nhan_loi, chi_ap_dung_ngoai_phap_ly)` nếu phát hiện cấu trúc vòng vo."""
    m_rb = _ROUNDABOUT_PHRASE_RE.search(sent_text)
    if m_rb:
        raw_frag = " ".join(m_rb.group(0).lstrip(",; ").split())
        return m_rb.start(), f"cụm dẫn dắt vòng vo '{raw_frag}'", False
    if prof != Profile.LEGAL:
        m_viec = _BLOATED_VIEC_OPENER_RE.match(sent_text)
        if m_viec:
            return 0, "mở câu danh từ hóa cồng kềnh bằng 'Việc ...'", True
    if wc >= 30:
        hinges = list(_SUBORDINATE_HINGE_RE.finditer(sent_text))
        if len(hinges) >= 3:
            return hinges[0].start(), f"chồng {len(hinges)} mệnh đề rào đón/phụ thuộc trong một câu", False
    return None


def _format_bloat_suggestion(reasons: Sequence[str], *, has_len: bool, has_rb: bool) -> str:
    if has_len and has_rb:
        act = "Hãy cắt bỏ cụm mở đầu vòng vo và tách thành 2–3 câu ngắn độc lập (15–25 từ/câu), mỗi câu một chủ thể."
    elif has_len:
        act = (
            "Hãy tách thành 2–3 câu ngắn độc lập (15–25 từ/câu) hoặc chuyển danh sách dài sang gạch đầu dòng, "
            "mỗi câu một chủ thể và một động từ chính."
        )
    else:
        act = "Hãy cắt bỏ cụm mở đầu vòng vo, đưa thẳng chủ thể và động từ chính lên đầu câu."
    return f"Phát hiện {'; '.join(reasons)}. {act}"


def _evaluate_sentence_bloat(
    rule: RuleDefinition,
    buf: _ScanBuffer,
    sent_start: int,
    sent_text: str,
    prof: Profile | None,
) -> Finding | None:
    wc = len(_SENT_WORD_RE.findall(sent_text))
    if wc < 5 or not VI_DIACRITIC_RE.search(sent_text):
        return None
    word_limit = 45 if prof == Profile.LEGAL else 35
    over_length = wc > word_limit
    clause_commas = len(_CLAUSE_COMMA_RE.findall(sent_text))
    comma_sprawl = prof != Profile.LEGAL and wc >= 28 and clause_commas >= 5 and (wc / (clause_commas + 1)) >= 4.5
    has_len = over_length or comma_sprawl
    rb_hit = _find_roundabout_hit(sent_text, wc, prof)
    if not (has_len or rb_hit):
        return None

    base_w = max(
        min(2.5, round(1.0 + 0.04 * (wc - word_limit), 2)) if over_length else 1.0,
        min(2.0, round(1.0 + 0.12 * (clause_commas - 4), 2)) if comma_sprawl else 1.0,
    )
    if rb_hit and has_len:
        weight = min(2.5, round(base_w + 0.25, 2))
    else:
        weight = (1.15 if wc >= 30 else 1.0) if rb_hit else base_w

    reasons: list[str] = []
    if over_length:
        reasons.append(f"câu dài {wc} từ (vượt ngưỡng {word_limit} từ)")
    elif comma_sprawl:
        reasons.append(f"câu {wc} từ nối {clause_commas + 1} vế bằng dấu phẩy")
    if rb_hit:
        reasons.append(rb_hit[1])

    hit_off = sent_start + (rb_hit[0] if rb_hit and not has_len else 0)
    raw_snippet = " ".join(buf.raw_text[hit_off : sent_start + len(sent_text)].split())[:100]
    exempt_legal = prof is None and wc <= 45 and (rb_hit is None or rb_hit[2])
    finding = make_finding(
        rule,
        buf,
        hit_off,
        f"[{wc} từ] {raw_snippet}" if has_len else raw_snippet,
        custom_suggestion=_format_bloat_suggestion(reasons, has_len=has_len, has_rb=rb_hit is not None),
        override_profiles=_NON_LEGAL_PROFILES if exempt_legal else None,
    )
    finding.weight = weight
    return finding


def run_lengthy_and_roundabout_rule(rule: RuleDefinition, buf: _ScanBuffer, prof: Profile | None) -> list[Finding]:
    """Phạt nặng câu quá dài, câu nối đuôi nhiều dấu phẩy và cấu trúc mở câu vòng vo (`VIS-LEN-001`)."""
    prose_buf = _prepare_length_prose(buf)
    findings: list[Finding] = []
    for sent_start, sent_text in _iter_prose_sentences(prose_buf):
        finding = _evaluate_sentence_bloat(rule, buf, sent_start, sent_text, prof)
        if finding is not None:
            findings.append(finding)
    return findings
