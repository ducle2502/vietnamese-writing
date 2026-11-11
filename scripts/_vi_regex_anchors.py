"""Trích xuất tập chuỗi con bắt buộc (`anchor literals`) từ biểu thức chính quy để lọc sơ bộ O(N) ở mức C."""

from __future__ import annotations

import re as stdlib_re

_REGEX_META_CHARS: frozenset[str] = frozenset(".^$*+?{}[]\\|()")
_REGEX_QUANT_RE: stdlib_re.Pattern[str] = stdlib_re.compile(r"(?:[*+?]\??|\{\d+(?:,\d*)?\}\??)")
_INLINE_FLAG_PREFIX_RE: stdlib_re.Pattern[str] = stdlib_re.compile(r"^\(\?[im]+\)")


def safe_lower_preserve_len(text: str) -> str:
    """Hạ chữ thường bảo toàn 100% độ dài chuỗi và vị trí ký tự (xử lý ngoại lệ Unicode U+0130)."""
    if "\u0130" in text:
        text = text.replace("\u0130", "i")
    return text.lower()


def _quantifier_info(expr: str, pos: int) -> tuple[int, bool]:
    m = _REGEX_QUANT_RE.match(expr, pos)
    if not m:
        return pos, False
    q = m.group(0)
    is_opt = q[0] in "*?" or q.startswith(("{0,", "{0}"))
    return m.end(), is_opt


def _skip_char_class(expr: str, open_idx: int) -> int:
    idx = open_idx + 1
    n = len(expr)
    while idx < n and expr[idx] != "]":
        idx += 2 if expr[idx] == "\\" else 1
    return min(idx + 1, n)


def _find_matching_paren(expr: str, open_idx: int) -> int:
    depth = 1
    idx = open_idx + 1
    n = len(expr)
    in_cls = False
    while idx < n and depth > 0:
        ch = expr[idx]
        if ch == "\\":
            idx += 2
            continue
        if in_cls:
            if ch == "]":
                in_cls = False
        elif ch == "[":
            in_cls = True
        elif ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        idx += 1
    return idx


def _split_top_level_pipes(expr: str) -> list[str]:
    parts: list[str] = []
    cur: list[str] = []
    depth = 0
    in_cls = False
    idx = 0
    n = len(expr)
    while idx < n:
        ch = expr[idx]
        if ch == "\\":
            cur.append(expr[idx : idx + 2])
            idx += 2
            continue
        if in_cls:
            if ch == "]":
                in_cls = False
        elif ch == "[":
            in_cls = True
        elif ch == "(":
            depth += 1
        elif ch == ")":
            depth = max(0, depth - 1)
        elif ch == "|" and depth == 0:
            parts.append("".join(cur))
            cur.clear()
            idx += 1
            continue
        cur.append(ch)
        idx += 1
    parts.append("".join(cur))
    return parts


def _flush_best_literal(cur_lit: list[str], best_lit: str) -> str:
    candidate = "".join(cur_lit)
    cur_lit.clear()
    return candidate if len(candidate) > len(best_lit) else best_lit


def _consume_regex_atom(seq: str, idx: int) -> tuple[str | None, int, bool]:
    ch = seq[idx]
    n = len(seq)
    if ch == "\\" and idx + 1 < n:
        nxt = seq[idx + 1]
        next_i, is_opt = _quantifier_info(seq, idx + 2)
        if nxt in _REGEX_META_CHARS and not is_opt:
            return safe_lower_preserve_len(nxt), next_i, (next_i > idx + 2)
        return None, next_i, True
    if ch in _REGEX_META_CHARS:
        next_i, _ = _quantifier_info(seq, idx)
        return None, max(idx + 1, next_i), True
    next_i, is_opt = _quantifier_info(seq, idx + 1)
    if is_opt:
        return None, next_i, True
    return safe_lower_preserve_len(ch), next_i, (next_i > idx + 1)


def _merge_group_anchors(best_group_set: set[str] | None, inner: str) -> set[str] | None:
    if inner.startswith(("?=", "?!", "?<")):
        return best_group_set
    inner = inner.removeprefix("?:")
    if inner.startswith("?"):
        return best_group_set
    g_set = _extract_anchor_set(inner)
    if g_set and (best_group_set is None or len(g_set) < len(best_group_set)):
        return g_set
    return best_group_set


def _extract_seq_anchors(seq: str) -> set[str] | None:
    best_lit = ""
    best_group_set: set[str] | None = None
    cur_lit: list[str] = []
    idx = 0
    n = len(seq)
    while idx < n:
        ch = seq[idx]
        if ch == "[":
            best_lit = _flush_best_literal(cur_lit, best_lit)
            idx, _ = _quantifier_info(seq, _skip_char_class(seq, idx))
            continue
        if ch == "(":
            best_lit = _flush_best_literal(cur_lit, best_lit)
            close_end = _find_matching_paren(seq, idx)
            next_i, is_opt = _quantifier_info(seq, close_end)
            if not is_opt:
                best_group_set = _merge_group_anchors(best_group_set, seq[idx + 1 : close_end - 1])
            idx = next_i
            continue
        lit_ch, idx, breaks_after = _consume_regex_atom(seq, idx)
        if lit_ch is None:
            best_lit = _flush_best_literal(cur_lit, best_lit)
        else:
            cur_lit.append(lit_ch)
            if breaks_after:
                best_lit = _flush_best_literal(cur_lit, best_lit)
    best_lit = _flush_best_literal(cur_lit, best_lit).strip()
    if len(best_lit) >= 2 or best_lit in ("—", ";", "["):
        return {best_lit}
    return best_group_set


def _extract_anchor_set(expr: str) -> set[str] | None:
    cleaned = _INLINE_FLAG_PREFIX_RE.sub("", expr)
    branches = _split_top_level_pipes(cleaned)
    if len(branches) == 1:
        return _extract_seq_anchors(branches[0])
    acc: set[str] = set()
    for branch in branches:
        sub = _extract_anchor_set(branch)
        if not sub:
            return None
        acc.update(sub)
    return acc


def _extract_regex_anchors(pattern: str) -> tuple[str, ...]:
    """Trích xuất tập chuỗi con bắt buộc (anchor literals) từ cây cú pháp regex."""
    anchors = _extract_anchor_set(pattern)
    return tuple(sorted(anchors)) if anchors else ()
