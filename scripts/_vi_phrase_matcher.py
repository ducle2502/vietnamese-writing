"""Cây tiền tố từ vựng O(N) (`PhraseTrie`) và quy tắc nhịp câu cụt (`VIS-FMT-006`) cho `vi_scanner`."""

from __future__ import annotations

import re as stdlib_re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from _vi_masker import make_finding, sentence_around
from _vi_regex_anchors import safe_lower_preserve_len

if TYPE_CHECKING:
    from collections.abc import Sequence

    from _vi_types import Finding, Profile, RuleDefinition, _RegexMatch, _ScanBuffer

_TOKEN_RE: stdlib_re.Pattern[str] = stdlib_re.compile(r"\w+|[^\w\s]")
_PARA_GAP_RE: stdlib_re.Pattern[str] = stdlib_re.compile(r"\n[ \t]*\n")
_TRAILING_FOOTNOTE_RE: stdlib_re.Pattern[str] = stdlib_re.compile(r"(?<=[A-Za-zÀ-ỹĐđ.!?])\s*\d{1,3}$")
_VI_CHAR_RE: stdlib_re.Pattern[str] = stdlib_re.compile(r"[à-ỹđÀ-ỸĐ]")

_CONVERT_UNAMBIGUOUS: frozenset[str] = frozenset(
    {
        "bất quá",
        "cư nhiên",
        "hạ khứ",
        "hảo cảm",
        "một cái nha hoàn",
        "nhân gia",
        "sở hữu nhân",
        "tiểu tâm dực dực",
        "tử tâm",
        "vuốt mông ngựa",
        "xào mực",
        "ăn dưa",
        "ăn giấm",
        "đánh gãy lời",
    }
)
_CONVERT_CTX_RE: stdlib_re.Pattern[str] = stdlib_re.compile(
    r"(?i)\b(?:bất\s+quá|cư\s+nhiên|nhân\s+gia|hạ\s+khứ|sở\s+hữu\s+nhân|thập\s+phần|"
    r"tiểu\s+tâm\s+dực\s+dực|một\s+cái\s+(?:nha\s+hoàn|nhân|kế\s+toán|giáo\s+sư|bác\s+sĩ)|"
    r"tỷ\s+như|mỗ\s+(?:nam|nữ)|(?:nàng|hắn|ta|ngươi)\s+đích)\b"
)
_NUMERIC_SLANG_LEAD_RE: stdlib_re.Pattern[str] = stdlib_re.compile(
    r"(?i)(?:đồ|thằng|con|kẻ|quá|đỉnh|cười|chế\s+độ|làm\s+việc|kiểu)\s+$"
)
_BAN_CHI_EXEMPT_TAIL_RE: stdlib_re.Pattern[str] = stdlib_re.compile(r"(?i)^\s*(?:đạo|huy)\b")
_BANG_QUANG_LEAD_RE: stdlib_re.Pattern[str] = stdlib_re.compile(r"(?i)(?:thái\s+độ|vẻ|đứng|sống)\s+$")
_BANG_QUANG_TAIL_RE: stdlib_re.Pattern[str] = stdlib_re.compile(r"(?i)^\s*(?:trước|với)\b")
_NHAN_PREFIX_RE: stdlib_re.Pattern[str] = stdlib_re.compile(r"(?i)(?:xác|ghi|chấp|công|thừa)\s+$")
_YEU_DIEM_BAD_RE: stdlib_re.Pattern[str] = stdlib_re.compile(
    r"(?i)\b(?:khắc\s+phục|sửa\s+chữa|nhược\s+điểm|hạn\s+chế|bộc\s+lộ|che\s+giấu|chí\s+mạng|chết\s+người)\b"
)
_SENT_START_PREFIX_RE: stdlib_re.Pattern[str] = stdlib_re.compile(r"(?:^|[.!?…\n])(?:\s*(?:[-*•◦–>]|\d+[.)]))*\s*$")
_DIRECT_HOMOGRAPH_TERMS: frozenset[str] = frozenset(
    {"bộ vệ sinh", "sở vệ sinh", "tổ hạng mục", "phân tử sinh học", "ý vị trứ", "lợi dụng nguyên liệu"}
)
_POLYSEMOUS_CONVERT_TERMS: frozenset[str] = frozenset(
    {
        "cua đồng",
        "điềm tâm",
        "đại gia",
        "đơn từ",
        "khả năng di truyền",
        "làm sao vậy",
        "lão tử",
        "một khắc",
        "một vòng",
        "nam nhân",
        "nguyên bản",
        "người gia",
        "nhãn lực",
        "phúc tướng",
        "quân cơ",
        "rượu đỏ",
        "tẩu tử",
        "thoát đơn",
        "từ mở rộng",
    }
)

_PAREN_MASK_RE: stdlib_re.Pattern[str] = stdlib_re.compile(r"\([^()\n]{1,260}\)")
_STACCATO_SPLIT_RE: stdlib_re.Pattern[str] = stdlib_re.compile(r"(?<=[.!?…])\s+")
_STACCATO_WORD_RE: stdlib_re.Pattern[str] = stdlib_re.compile(r"[0-9A-Za-zÀ-ỹĐđ]+(?:[.,/-][0-9A-Za-zÀ-ỹĐđ]+)*")
_NON_PROSE_PARA_RE: stdlib_re.Pattern[str] = stdlib_re.compile(r"^\s*(?:[#|>—\"“]|[-*•◦–]\s|\d+[.)]\s)")
_BOLD_COLON_BULLET_RE: stdlib_re.Pattern[str] = stdlib_re.compile(
    r"^\s*(?:[-*•◦–]|\d+[.)])\s+(?:\*\*[^*\n]{2,65}?:\*\*|\*\*[^*\n]{2,65}?\*\*\s*:)"
)
_EX_LEGAL_GLOSSARY_RE: stdlib_re.Pattern[str] = stdlib_re.compile(r"(?i)\b(?:giải thích từ ngữ|bên a|bên b)\b")


def sanitize_hint(raw_hint: str) -> str:
    """Loại bỏ số chú thích chân trang PDF dính cuối chuỗi gợi ý nhưng giữ nguyên số liệu hợp lệ."""
    cleaned = " ".join(raw_hint.split())
    return _TRAILING_FOOTNOTE_RE.sub("", cleaned).strip() if cleaned else ""


@dataclass(frozen=True, slots=True)
class PhraseEntry:
    rule_id: str
    term_key: str
    hint: str
    is_reverse_calque: bool = False
    is_code_mixing: bool = False
    requires_cluster: bool = False
    requires_convert_ctx: bool = False
    is_numeric_slang: bool = False
    sentence_initial_only: bool = False


@dataclass(frozen=True, slots=True)
class PhraseHit:
    pos: int
    end_pos: int
    entry: PhraseEntry

    def start(self) -> int:
        return self.pos

    def end(self) -> int:
        return self.end_pos


@dataclass(frozen=True, slots=True)
class GroupedSpanMatch:
    pos: int
    end_pos: int
    display_text: str
    custom_hint: str | None = None

    def start(self) -> int:
        return self.pos

    def end(self) -> int:
        return self.end_pos


@dataclass(frozen=True, slots=True)
class TokenizedProse:
    words: tuple[str, ...]
    starts: tuple[int, ...]
    ends: tuple[int, ...]
    has_space_after: tuple[bool, ...]
    same_para_next: tuple[bool, ...]


@dataclass(slots=True)
class _TrieNode:
    edges: dict[tuple[str, bool], _TrieNode] = field(default_factory=dict)
    entries: list[PhraseEntry] = field(default_factory=list)


def tokenize_prose(lower_text: str) -> TokenizedProse:
    matches = list(_TOKEN_RE.finditer(lower_text))
    n = len(matches)
    if n == 0:
        return TokenizedProse((), (), (), (), ())
    words = tuple(m.group(0) for m in matches)
    starts = tuple(m.start() for m in matches)
    ends = tuple(m.end() for m in matches)
    has_space = (*(starts[i + 1] > ends[i] for i in range(n - 1)), False)
    same_para = (*(not _PARA_GAP_RE.search(lower_text, ends[i], starts[i + 1]) for i in range(n - 1)), False)
    return TokenizedProse(words, starts, ends, has_space, same_para)


def _needs_convert_context(term_key: str, word_count: int, note: str, *, is_bulk_ai: bool) -> bool:
    if is_bulk_ai:
        return False
    if term_key in _POLYSEMOUS_CONVERT_TERMS:
        return True
    if ("đồng hình dị nghĩa" in note or "nhóm 08" in note) and term_key not in _DIRECT_HOMOGRAPH_TERMS:
        return True
    if "Từ lậm convert" in note and term_key not in _CONVERT_UNAMBIGUOUS:
        return True
    return word_count == 1 and not term_key.isdigit() and bool(_VI_CHAR_RE.search(term_key) or "!" in term_key)


def build_vocab_entry(
    *,
    term: str,
    kind: str,
    rule_id: str,
    raw_hint: str,
    note: str,
) -> PhraseEntry:
    term_key = " ".join(term.split()).casefold()
    hint = sanitize_hint(raw_hint)
    words = term_key.split(" ")
    is_bulk_ai = note.startswith(("Cụm văn mẫu AI", "Khuôn câu AI cố định"))
    needs_conv = _needs_convert_context(term_key, len(words), note, is_bulk_ai=is_bulk_ai)
    if kind == "reverse_calque":
        return PhraseEntry(
            rule_id="VIS-LEX-002",
            term_key=term_key,
            hint=hint,
            is_reverse_calque=True,
            is_code_mixing="nhóm 14" in note,
            requires_convert_ctx=needs_conv,
            is_numeric_slang=term_key.isdigit(),
        )
    sent_init = is_bulk_ai and rule_id == "VIS-FMT-002"
    buzz_group = rule_id == "VIS-CLICHE-001" and any(g in note for g in ("nhóm 04", "nhóm 11", "nhóm 12"))
    max_cl_words = 5 if buzz_group else 3
    has_conj = "," in term_key or " và " in term_key
    req_cluster = is_bulk_ai and not sent_init and not has_conj and len(words) <= max_cl_words
    return PhraseEntry(
        rule_id=rule_id,
        term_key=term_key,
        hint=hint,
        requires_cluster=req_cluster,
        requires_convert_ctx=needs_conv,
        is_numeric_slang=term_key.isdigit(),
        sentence_initial_only=sent_init,
    )


def _check_special_rev_term(key: str, prose_text: str, start: int, end: int, prof: Profile | None) -> bool | None:
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


def is_valid_phrase_hit(
    entry: PhraseEntry,
    prose_text: str,
    start: int,
    end: int,
    prof: Profile | None,
) -> bool:
    special = _check_special_rev_term(entry.term_key, prose_text, start, end, prof)
    if special is not None:
        return special
    if entry.sentence_initial_only:
        at_start = start == 0 or bool(_SENT_START_PREFIX_RE.search(prose_text[max(0, start - 10) : start]))
        has_comma = len(entry.term_key.split()) > 3 or prose_text[end : end + 2].startswith(",")
        return at_start and has_comma
    if entry.is_numeric_slang:
        lead = prose_text[max(0, start - 18) : start]
        return bool(_NUMERIC_SLANG_LEAD_RE.search(lead) or prose_text[end : end + 3].startswith("!"))
    if entry.requires_convert_ctx:
        return bool(_CONVERT_CTX_RE.search(sentence_around(prose_text, start, end)))
    return True


class PhraseTrie:
    """Cây tiền tố băm theo token giúp quét hàng nghìn cụm từ `vocab.csv` trong thời gian tuyến tính O(N)."""

    __slots__ = ("_root",)

    def __init__(self, entries: Sequence[PhraseEntry] = ()) -> None:
        self._root: dict[str, _TrieNode] = {}
        for entry in entries:
            self.add(entry)

    def add(self, entry: PhraseEntry) -> None:
        tok_matches = list(_TOKEN_RE.finditer(entry.term_key))
        if not tok_matches:
            return
        first = tok_matches[0].group(0)
        node = self._root.get(first)
        if node is None:
            node = _TrieNode()
            self._root[first] = node
        for idx in range(len(tok_matches) - 1):
            had_space = tok_matches[idx + 1].start() > tok_matches[idx].end()
            edge_key = (tok_matches[idx + 1].group(0), had_space)
            nxt = node.edges.get(edge_key)
            if nxt is None:
                nxt = _TrieNode()
                node.edges[edge_key] = nxt
            node = nxt
        node.entries.append(entry)

    def scan_all(self, tokens: TokenizedProse) -> tuple[dict[str, list[PhraseHit]], list[PhraseHit]]:
        by_rule: dict[str, list[PhraseHit]] = {}
        rev_hits: list[PhraseHit] = []
        words = tokens.words
        root = self._root
        for i in range(len(words)):
            node = root.get(words[i])
            if node is not None:
                self._collect_from_index(i, node, tokens, by_rule, rev_hits)
        return by_rule, rev_hits

    @staticmethod
    def _collect_from_index(
        i: int,
        node: _TrieNode,
        tokens: TokenizedProse,
        by_rule: dict[str, list[PhraseHit]],
        rev_hits: list[PhraseHit],
    ) -> None:
        words = tokens.words
        n = len(words)
        best_by_rule: dict[str, PhraseHit] = {}
        best_rev: PhraseHit | None = None
        j = i
        while True:
            for ent in node.entries:
                hit = PhraseHit(tokens.starts[i], tokens.ends[j], ent)
                if ent.is_reverse_calque:
                    best_rev = hit
                else:
                    best_by_rule[ent.rule_id] = hit
            if j + 1 >= n or not tokens.same_para_next[j]:
                break
            nxt = node.edges.get((words[j + 1], tokens.has_space_after[j]))
            if nxt is None and words[j] == ",":
                nxt = node.edges.get((words[j + 1], True))
            if nxt is None:
                break
            node = nxt
            j += 1

        if best_rev is not None:
            rev_hits.append(best_rev)
        for rid, hit in best_by_rule.items():
            by_rule.setdefault(rid, []).append(hit)


def select_first_reverse_calque(
    rev_hits: Sequence[PhraseHit],
    prose_text: str,
    prof: Profile | None,
) -> PhraseHit | None:
    for hit in rev_hits:
        if is_valid_phrase_hit(hit.entry, prose_text, hit.pos, hit.end_pos, prof):
            return hit
    return None


def filter_non_overlapping_hits(hits: Sequence[PhraseHit]) -> list[PhraseHit]:
    out: list[PhraseHit] = []
    last_end = -1
    for h in hits:
        if h.pos >= last_end:
            out.append(h)
            last_end = h.end_pos
    return out


def _build_cluster_group_match(
    para_hits: Sequence[PhraseHit],
    raw_text: str,
    rid: str,
) -> _RegexMatch | None:
    if rid == "VIS-FMT-004":
        for i in range(len(para_hits) - 2):
            h1, h3 = para_hits[i], para_hits[i + 2]
            span = raw_text[h1.pos : h3.end_pos] if raw_text else ""
            if (h3.end_pos - h1.pos) <= 85 and not any(ch in ".!?…\n" for ch in span):
                disp = " ".join(span.split()) if span else h1.entry.term_key
                return GroupedSpanMatch(
                    h1.pos,
                    h3.end_pos,
                    disp,
                    "Tránh ghép bộ 3 tính từ khen ngợi theo nhịp văn mẫu; hãy thay bằng chỉ tiêu định lượng cụ thể.",
                )
        return None
    if not raw_text:
        return para_hits[0]
    top = para_hits[:3]
    disp = " ... ".join(" ".join(raw_text[h.pos : h.end_pos].split()) for h in top)
    return GroupedSpanMatch(
        top[0].pos,
        top[-1].end_pos,
        disp,
        f"Tránh dồn nhiều từ ngữ khuôn mẫu trong cùng một đoạn ({disp}); hãy thay bằng hành động và số liệu cụ thể.",
    )


def filter_statistical_cluster_hits(
    hits: Sequence[PhraseHit],
    para_spans: Sequence[tuple[int, int, str]],
    *,
    raw_text: str = "",
    rid: str = "",
    min_cluster: int = 3,
) -> list[_RegexMatch]:
    """Giữ trực tiếp cụm dài cố định; cụm ngắn `requires_cluster` chỉ kích hoạt khi lặp `>= min_cluster` trong đoạn."""
    strong: list[_RegexMatch] = [h for h in hits if not h.entry.requires_cluster]
    short_hits = [h for h in hits if h.entry.requires_cluster]
    if len(short_hits) < min_cluster:
        return strong
    idx = 0
    n_short = len(short_hits)
    for p_start, p_end, _ in para_spans:
        while idx < n_short and short_hits[idx].pos < p_start:
            idx += 1
        s_idx = idx
        while idx < n_short and short_hits[idx].pos < p_end:
            idx += 1
        if (idx - s_idx) >= min_cluster:
            grp = _build_cluster_group_match(short_hits[s_idx:idx], raw_text, rid)
            if grp is not None:
                strong.append(grp)
    strong.sort(key=lambda m: m.start())
    return strong


def _find_staccato_offset_in_para(p_start: int, para_text: str) -> tuple[int, int] | None:
    if _NON_PROSE_PARA_RE.match(para_text):
        return None
    lines = [ln.strip() for ln in para_text.splitlines() if ln.strip()]
    if len(lines) >= 3 and all(len(ln.split()) < 8 for ln in lines):
        return None
    masked_para = _PAREN_MASK_RE.sub(lambda m: " " * len(m.group(0)), para_text)
    streak = 0
    streak_off = 0
    pos = 0
    for m_sp in [*_STACCATO_SPLIT_RE.finditer(masked_para), None]:
        seg_end = m_sp.start() if m_sp is not None else len(masked_para)
        seg = masked_para[pos:seg_end].strip()
        wc = len(_STACCATO_WORD_RE.findall(seg))
        is_frag = 1 <= wc < 6 and bool(_VI_CHAR_RE.search(seg)) and seg[-1] in ".!?…"
        if is_frag:
            if streak == 0:
                lead_ws = len(masked_para[pos:seg_end]) - len(masked_para[pos:seg_end].lstrip())
                streak_off = p_start + pos + lead_ws
            streak += 1
            if streak >= 3:
                raw_end = p_start + seg_end
                return streak_off, raw_end - streak_off
        else:
            streak = 0
        if m_sp is not None:
            pos = m_sp.end()
    return None


def run_bold_colon_list_rule(rule: RuleDefinition, buf: _ScanBuffer, prof: Profile | None) -> list[Finding]:
    if prof is not None and prof.value == "legal" and _EX_LEGAL_GLOSSARY_RE.search(buf.masked_prose):
        return []
    streak = 0
    streak_start_offset = 0
    offset = 0
    for ln in buf.masked_prose.splitlines(keepends=True):
        if not ln.strip():
            offset += len(ln)
            continue
        if _BOLD_COLON_BULLET_RE.match(ln):
            if streak == 0:
                streak_start_offset = offset
            streak += 1
            if streak == 3:
                sample = buf.raw_text[streak_start_offset : offset + len(ln)].strip().splitlines()[0]
                return [
                    make_finding(
                        rule,
                        buf,
                        streak_start_offset,
                        sample,
                        custom_suggestion=(
                            "Bỏ nhãn in đậm đầu dòng và viết thành câu hoàn chỉnh mở đầu bằng chủ ngữ cụ thể."
                        ),
                    )
                ]
        else:
            streak = 0
        offset += len(ln)
    return []


def run_staccato_fragment_rule(rule: RuleDefinition, buf: _ScanBuffer, prof: Profile | None) -> list[Finding]:
    """Bắt chuỗi >= 3 câu cực ngắn liên tiếp (< 6 từ/câu) dùng làm khẩu hiệu giả triết lý (`VIS-FMT-006`)."""
    if prof is not None and prof not in rule.profiles:
        return []
    for p_start, _, para_text in buf.para_spans:
        res = _find_staccato_offset_in_para(p_start, para_text)
        if res is not None:
            off, span_len = res
            snippet = " ".join(buf.raw_text[off : off + span_len].split())
            return [make_finding(rule, buf, off, snippet)]
    return []
