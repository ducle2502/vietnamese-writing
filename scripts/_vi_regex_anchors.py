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


_RULE_FALLBACK_SUGGESTIONS: dict[str, str] = {
    "VIS-AI-003": "Cắt bỏ cụm mở màn 'Trong bối cảnh/kỷ nguyên...'; mở câu trực tiếp bằng chủ thể và số liệu chính.",
    "VIS-AI-004": "Bỏ câu dẫn dắt hoặc tự hỏi tự đáp kiểu văn mẫu; nêu thẳng luận điểm hoặc kết quả chính.",
    "VIS-AI-005": "Cắt bỏ lời kết hứa hẹn tương lai chung chung; khép lại bằng kết quả thực tế hoặc bước tiếp theo.",
    "VIS-AI-006": "Bỏ câu mở đầu 'Hãy thử tưởng tượng/hình dung...'; đi thẳng vào tình huống thực tế hoặc số liệu.",
    "VIS-AI-007": "Bỏ câu gom mọi nhóm người đọc 'Dù bạn là...'; nêu trực tiếp công dụng hoặc đối tượng sử dụng chính.",
    "VIS-RHET-001": "Bỏ cấu trúc 'Không chỉ là X, mà còn là Y'; nêu thẳng chức năng hoặc tác động thực tế.",
    "VIS-RHET-002": "Thay cụm tán dương phóng đại bằng tác động thực tế hoặc con số đo kiểm được.",
    "VIS-RHET-004": "Bỏ khung liệt kê hai đầu mút 'Từ [A] cho đến [B], tất cả đều...'; gọi tên thẳng đối tượng.",
    "VIS-RHET-005": "Nêu rõ tên tổ chức, tác giả và năm công bố, hoặc bỏ cụm 'Các chuyên gia/Nhiều nghiên cứu'.",
    "VIS-RHET-006": "Bỏ khung nâng tầm 'Hơn cả X, đây là Y' / 'Không phải X, mà chính là Y'; mô tả thẳng chức năng.",
    "VIS-RHET-007": "Giảm lặp khung 'Tưởng chừng/Thoạt nhìn..., nhưng...'; trình bày thẳng sự việc và số liệu.",
    "VIS-FMT-002": "Lược bớt từ nối đầu câu lặp lại liên tiếp hoặc gộp các ý cùng chiều thành một câu gọn.",
    "VIS-FMT-006": "Gộp chuỗi câu cụt kiểu khẩu hiệu thành câu hoàn chỉnh có đủ chủ ngữ, vị ngữ và điều kiện.",
    "VIS-TRANS-002": "Giảm mật độ bị động 'được + động từ' trong đoạn; chuyển sang câu chủ động nêu rõ ai làm gì.",
    "VIS-TRANS-003": "Đổi cụm danh từ hóa 'sự/việc + động từ + của + chủ thể' sang chủ thể + động từ trực tiếp.",
    "VIS-TRANS-004": "Lược bớt cụm 'một cách + tính từ' lặp lại trong đoạn; dùng động từ mạnh hoặc trạng từ ngắn gọn.",
    "VIS-TRANS-006": "Rút gọn chuỗi sở hữu 'của... của... của...' bằng cách bỏ từ 'của' trung gian hoặc đảo chủ ngữ.",
    "VIS-TRANS-007": "Giảm lặp cặp liên từ đóng khung 'mặc dù... nhưng', 'bởi vì... nên'; chỉ giữ một liên từ chính.",
    "VIS-TRANS-008": "Thay 'đến từ' (dịch sát 'from') bằng 'của', 'do ... phát triển', hoặc đưa chủ thể lên đầu câu.",
    "VIS-TRANS-009": "Bỏ từ chỉ vị trí bị lặp ('ở trong... bên trong'); thay một vế bằng quan hệ sở hữu 'của'.",
    "VIS-TRANS-010": "Thay cụm 'mang tính + danh/tính từ' lặp lại bằng tính từ trực tiếp hoặc chỉ tiêu cụ thể.",
    "VIS-CLICHE-005": "Chỉ giữ một từ chỉ khả năng ('có thể' hoặc 'dự kiến') thay vì ghép chồng nhiều từ rào đón.",
    "VIS-TONE-001": "Đổi sang giọng văn trung tính, trang trọng phù hợp với văn bản trình duyệt; bỏ từ khẩu ngữ.",
    "VIS-TONE-002": (
        "Tránh từ ngữ điều tra hình sự, cổ văn hoặc báo chí giật gân; "
        "dùng động từ trung tính ('phát hiện', 'ghi nhận')."
    ),
    "VIS-STRUCT-001": "Xóa lời tự thuyết minh bố cục hoặc nhãn dàn ý nội bộ; đi thẳng vào nội dung phân tích của mục.",
}
_TONE002_SUBSTR_HINTS: tuple[tuple[tuple[str, ...], str], ...] = (
    (
        ("vỏn vẹn",),
        "Bỏ từ bình phẩm cảm tính 'vỏn vẹn'; ghi thẳng con số kèm 'chỉ đạt' hoặc 'chỉ có'.",
    ),
    (
        ("dậm chân", "giậm chân"),
        "Tránh thành ngữ 'giậm chân tại chỗ/ở mức' (và lỗi 'dậm chân'); ghi thẳng 'chưa tăng' hoặc 'giữ nguyên ở mức'.",
    ),
    (
        ("sập ",),
        "Tránh từ kịch tính 'sập' cho sự cố kỹ thuật; mô tả đúng hiện tượng ('mất kết nối', 'ngừng phản hồi', 'lỗi').",
    ),
    (
        ("tê liệt", "vỡ trận", "khủng hoảng"),
        "Tránh gắn nhãn kịch tính ('tê liệt', 'vỡ trận', 'khủng hoảng'); nêu rõ phạm vi và thời gian gián đoạn.",
    ),
    (
        ("phơi bày", "hé lộ", "lộ diện", "trồi lên"),
        "Tránh động từ gợi sự/báo chí cho báo cáo, dữ liệu hoặc lỗi; dùng 'cho thấy', 'ghi nhận' hoặc 'phát sinh'.",
    ),
)
_LEX001_SUBSTR_HINTS: tuple[tuple[tuple[str, ...], str], ...] = (
    (
        ("thực chứng",),
        "Từ 'thực chứng' chỉ trường phái triết học; hãy thay bằng 'dựa trên bằng chứng' hoặc 'thực tế'.",
    ),
    (
        ("hiện thực",),
        "Tránh dịch sát 'implement' thành 'hiện thực'; dùng 'viết', 'lập trình' hoặc 'xây dựng'.",
    ),
    (
        ("khung ",),
        "Tránh dịch từng chữ 'framework/frame/harness' thành 'khung ...'; nêu thẳng quy trình, bộ mã hoặc giao diện.",
    ),
    (
        ("hợp đồng ", "giao kèo "),
        "Tránh dịch sát 'data/API/module contract'; thay bằng 'đặc tả API/dữ liệu' hoặc 'quy ước giao diện'.",
    ),
    (
        ("cọ sát",),
        "Sai chính tả phụ âm 's/x'; viết đúng là 'cọ xát' (ví dụ: 'cọ xát thực tế').",
    ),
    (
        ("phục vụ", "dò ", "máy"),
        "Thay cụm dịch sát kỹ thuật bằng động từ tiếng Việt tự nhiên ('kiểm thử', 'quét cổng', 'đối chiếu tự động').",
    ),
    (
        (" cứng",),
        "Tránh khẩu ngữ dịch sát 'chặn/khóa/ép/gắn cứng'; dùng 'báo lỗi ngay', 'từ chối ngay' hoặc 'ghi cố định'.",
    ),
    (
        ("dịch sát", " sát"),
        "Không cắt cụt từ nối ('bị động dịch sát', 'sửa sát'); viết rõ 'câu bị động dịch từng chữ', 'bám sát'.",
    ),
    (
        ("lặp ",),
        "Tránh từ ghép tự chế ('lặp khuôn', 'lặp dày', 'lặp đều'); dùng 'rập khuôn', 'lặp lại dày đặc'.",
    ),
    (
        (" cũ",),
        "Danh từ chỉ chu kỳ thời gian ('kỳ', 'đợt', 'quý', 'tháng') đi với 'trước', không ghép với 'cũ'.",
    ),
    (
        ("che chắn", "bảo toàn"),
        "Tránh dịch thô 'masking/invariant' thành 'che chắn vùng', 'đối soát bảo toàn'; mô tả thẳng thao tác.",
    ),
    (
        ("lối ", "lửng lơ"),
        "Bỏ lối gọi tên văn vẻ giả tạo ('lối chêm từ', 'chêm ... lửng lơ'); dùng 'chêm tiếng Anh tùy tiện'.",
    ),
    (
        (
            "vĩ mô",
            "giả định",
            "bao sân",
            "nhắc điền",
            "đòn bẩy",
            "kịch tính",
            "biện chứng",
            "tầm vóc",
            "sóng đôi",
            "sử dụng",
        ),
        "Thay thuật ngữ dịch thô hoặc tự chế kiểu AI bằng tiếng Việt tự nhiên, phổ thông.",
    ),
)
_TRANS005_PREFIX_HINTS: tuple[tuple[tuple[str, ...], str], ...] = (
    (("nó ", "có một sự"), "Bỏ chủ ngữ giả ('Nó là...', 'Có một sự...'); đưa chủ ngữ thực và động từ lên đầu câu."),
    (("—", "–", "-", ","), "Tránh nối mệnh đề bằng đại từ quan hệ dịch sát ('nơi mà', 'điều mà'); hãy tách câu."),
    (("đúc kết từ", "dẫn đến việc", "xuất phát từ việc"), "Thêm chủ thể rõ ràng trước động từ thay vì mở câu lơ lửng."),
    (("vẫn ",), "Bỏ bớt một chữ 'vẫn' bị lặp trong cùng vế câu."),
    (("báo ",), "Đặt từ 'nhầm' ngay sau động từ 'báo' (ví dụ: 'báo nhầm mất kết nối' hoặc 'báo lỗi nhầm')."),
    (("giới hạn thời gian",), "Diễn đạt tự nhiên hơn (ví dụ: 'ngưỡng thời gian chờ cố định' hoặc 'thời hạn tối đa')."),
    (("một cách ",), "Bỏ cụm dịch sát 'một cách + tính từ kỹ thuật'; dùng trạng ngữ tự nhiên ('nhất quán')."),
    (("và không", "nên ", "không cần", "không phải"), "Viết gọn thành 'chỉ dùng thư viện chuẩn' hoặc nêu điều kiện."),
    (("hỗ trợ ",), "Thay 'hỗ trợ + động từ' bằng động từ trực tiếp (ví dụ: 'cho phép lọc...' hoặc 'lọc, tìm kiếm')."),
)


def _resolve_trans_or_lex_hint(rid: str, low: str) -> str | None:
    out: str | None = None
    if rid == "VIS-TRANS-001":
        if " bởi" in low:
            out = "Đổi sang câu chủ động: đưa chủ thể thực hiện lên trước động từ và bỏ 'được/bị ... bởi'."
        elif "/" in low:
            out = "Tránh ghép gộp động từ bằng dấu gạch chéo kiểu bị động; hãy tách rõ thao tác chủ động."
        else:
            out = "Đổi sang câu chủ động: bỏ chữ 'được/bị' và đặt chủ thể thực hiện lên trước động từ."
    elif rid == "VIS-TRANS-005":
        out = next(
            (msg for prefixes, msg in _TRANS005_PREFIX_HINTS if low.startswith(prefixes)),
            "Không gán hành vi tâm lý ('vô tình', 'bỏ quên', 'tưởng nhầm') cho bảng biểu, con số vô tri.",
        )
    elif rid == "VIS-LEX-001":
        out = next(
            (msg for keys, msg in _LEX001_SUBSTR_HINTS if any(k in low for k in keys)),
            "Thay cụm từ sai nghĩa, sai chính tả hoặc dịch sát bằng cách diễn đạt tiếng Việt chuẩn xác.",
        )
    elif rid == "VIS-TONE-002":
        out = next((msg for keys, msg in _TONE002_SUBSTR_HINTS if any(k in low for k in keys)), None)
    return out


def resolve_regex_suggestion(rid: str, matched_text: str) -> str | None:
    """Trả về lời khuyên sửa lỗi khớp trực tiếp với nhánh regex vừa bắt được."""
    low = " ".join(matched_text.split()).casefold()
    out: str | None = None
    if rid == "VIS-FMT-003":
        out = (
            "Tránh nối vế câu bằng dấu chấm phẩy kiểu tiếng Anh; hãy tách thành câu riêng hoặc dùng dấu phẩy."
            if ";" in low
            else "Tránh chèn dấu gạch ngang dài để ngắt ý kiểu tiếng Anh; hãy dùng dấu phẩy, ngoặc đơn hoặc tách câu."
        )
    elif rid == "VIS-AI-001":
        if "mô hình ngôn ngữ" in low or "language model" in low:
            out = "Xóa câu tự xưng là mô hình ngôn ngữ AI và đi thẳng vào nội dung chính."
        elif any(k in low for k in ("thuộc quyền", "phạm vi được phép", "phòng lab", "sự cho phép")):
            out = "Bỏ câu rào đón đạo đức/pháp lý tự phát nếu tài liệu không yêu cầu cảnh báo tuân thủ riêng."
        else:
            out = "Xóa câu chào mời, khen ngợi hoặc kết thúc xã giao kiểu chatbot; đi thẳng vào nội dung chính."
    elif rid == "VIS-AI-002":
        out = (
            "Xóa tham số theo dõi nguồn chatbot ('?utm_source=...') khỏi đường dẫn."
            if "utm_source=" in low
            else "Điền thông tin thực tế hoặc xóa hẳn chỗ trống chưa điền còn sót trong bản thảo."
        )
    elif rid == "VIS-CLICHE-002":
        if low.startswith(("tiến hành ", "thực hiện ")):
            out = "Bỏ động từ rỗng 'tiến hành/thực hiện'; dùng thẳng động từ chính phía sau ('kiểm tra', 'đối soát')."
        elif any(k in low for k in ("vai trò", "tư cách", "biết đến như", "xem như", "coi như", "hiện diện như")):
            out = "Thay cụm vòng vo ('đóng vai trò như là một', 'được xem như là một') bằng động từ 'là' trực tiếp."
        else:
            out = "Thay cụm tán dương chung chung bằng thông số đo đếm được hoặc mô tả chức năng cụ thể."
    return out or _resolve_trans_or_lex_hint(rid, low) or _RULE_FALLBACK_SUGGESTIONS.get(rid)
