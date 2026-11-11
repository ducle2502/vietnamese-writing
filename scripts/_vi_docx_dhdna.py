"""Đọc an toàn tệp `.docx`, đo 18 chỉ số nhịp học (`stylometry`) và lập hồ sơ giọng văn `DHDNA`."""

from __future__ import annotations

import collections
import hashlib
import math
import re as stdlib_re
import statistics
import sys
import xml.etree.ElementTree as ET
import zipfile
import zlib
from pathlib import Path
from typing import TYPE_CHECKING, Any

from _vi_masker import SemanticMasker, _safe_lower_preserve_len, filter_markdown_table_columns
from _vi_types import VERSION, DhdnaVoiceMetrics, DocxMetadata, ProfileReport, StylometryReport, VoiceArchetype

if TYPE_CHECKING:
    from collections.abc import Sequence

_DOCX_NS: dict[str, str] = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "dc": "http://purl.org/dc/elements/1.1/",
    "cp": "http://schemas.openxmlformats.org/package/2006/metadata/core-properties",
    "dcterms": "http://purl.org/dc/terms/",
}
_DOCX_W_NS = _DOCX_NS["w"]
_DOCX_W_P = f"{{{_DOCX_W_NS}}}p"
_DOCX_W_TBL = f"{{{_DOCX_W_NS}}}tbl"
_DOCX_W_T = f"{{{_DOCX_W_NS}}}t"
_DOCX_W_TAB_OR_BR: frozenset[str] = frozenset({f"{{{_DOCX_W_NS}}}tab", f"{{{_DOCX_W_NS}}}br"})
_DOCX_W_VAL = f"{{{_DOCX_W_NS}}}val"
_DOCX_HEADING_STYLE_RE = stdlib_re.compile(r"(?i)^heading\s*([1-6])$")
_DOCX_TITLE_WAVE_RE = stdlib_re.compile(r"(?i)\b(đợt|kỳ|quý|tháng)\s+(\d+|[ivx]+)\b")
_MAX_DOCX_XML_BYTES = 64 * 1024 * 1024
_FORBIDDEN_XML_DECL_RE = stdlib_re.compile(rb"(?i)<!(?:DOCTYPE|ENTITY)\b")

_PARA_BREAK_RE = stdlib_re.compile(r"\n\s*\n")
_SENT_SPLIT_NL_RE = stdlib_re.compile(r"[.!?…]+(?:[*_)\"”’\]])*\s+|\n+")
_SENT_SPLIT_INLINE_RE = stdlib_re.compile(r"[.!?…]+(?:[*_)\"”’\]])*\s+")
_TBL_SENT_SPLIT_RE = stdlib_re.compile(r"[.!?…]+(?:[*_)\"”’\]])*\s+|\||;\s*(?=[•◦*-]|\d+[.)]\s)")
_SENT_WORD_TOKEN_RE = stdlib_re.compile(r"[0-9A-Za-zÀ-ỹĐđ]+(?:[.,/-][0-9A-Za-zÀ-ỹĐđ]+)*")
_VI_DIAC_RE = stdlib_re.compile(r"[à-ỹđÀ-ỸĐ]")
_VI_ALPHA_WORD_RE = stdlib_re.compile(r"[A-Za-zÀ-ỹĐđ]+")
_PARTICLES_RE = stdlib_re.compile(r"(?i)\b(?:nhé|nhỉ|nha|thôi|đấy|đâu|sao|chứ|hả|ạ|ơi|hen|nghen|vậy|thế)\b[!.?…]?")
_FORMAL_CONN_RE = stdlib_re.compile(
    r"(?i)\b(?:tuy nhiên|do đó|vì vậy|hơn nữa|ngoài ra|bên cạnh đó|mặt khác|"
    r"đồng thời|tóm lại|nhìn chung|cụ thể là|theo đó|qua đó)\b"
)
_COLLOQ_CONN_RE = stdlib_re.compile(
    r"(?i)\b(?:nhưng mà|thế là|vậy nên|cơ mà|thật ra|nói thật|nghĩ xem|thử hỏi|chứ còn gì)\b"
)
_HAN_VIET_ADMIN_RE = stdlib_re.compile(
    r"(?i)\b(?:triển khai|thực hiện|tiến hành|tối ưu hóa|hiện đại hóa|đồng bộ hóa|đa dạng hóa|"
    r"toàn diện|chuyên sâu|vượt trội|then chốt|bứt phá|kiến tạo|nâng tầm|hiện diện|tọa lạc|"
    r"sở hữu|mang lại|đáp ứng|nhằm mục đích|trong bối cảnh|trên cơ sở|với tư cách)\b"
)
_TU_LAY_RE = stdlib_re.compile(
    r"(?i)\b(?:lúng túng|rườm rà|mập mờ|lặp đi lặp lại|dài dòng|ngắn gọn|rõ ràng|tự nhiên|"
    r"mượt mà|khô khan|cứng nhắc|sáo rỗng|lẻ tẻ|rải rác|chầm chậm|nhanh nhanh|vội vàng|thong thả)\b"
)
_PUNCT_CHAR_RE = stdlib_re.compile(r"[.,;:!?…—–\-()\"'“”]")

_NUM_TOKEN_RE = stdlib_re.compile(r"\b\d+(?:[.,/]\d+)*%?\b")
_PCT_TOKEN_RE = stdlib_re.compile(r"\b\d+(?:[.,]\d+)?%")
_PCT_PAIRED_RE = stdlib_re.compile(
    r"(?i)\b\d+(?:[.,]\d+)*\s*/\s*\d+(?:[.,]\d+)*\b"
    r"|\b\d+(?:\.\d+)*\s+(?:đơn vị|hồ sơ|mục|nội dung|phiếu|bản ghi|giao dịch|kịch bản|"
    r"hành trình|chỉ đạo|hợp đồng|lượt|mẫu|khách hàng|tài khoản|bút toán|nhiệm vụ|"
    r"văn bản|tờ trình|báo cáo|khoản|tình huống)\b"
)
_DHDNA_EVIDENCE_RE = stdlib_re.compile(
    r"(?i)\b(?:chưa\s+(?:có|đủ|nhận\s+được)\s+(?:bằng\s+chứng|cơ\s+sở|căn\s+cứ|hồ\s+sơ|dữ\s+liệu)|"
    r"tự\s+báo\s+cáo|chưa\s+(?:được\s+)?kiểm\s+(?:tra|chứng)\s+độc\s+lập|"
    r"giả\s+định\s+tạm\s+thời|giới\s+hạn\s+của\s+kết\s+luận|không\s+suy\s+diễn\s+trạng\s+thái)\b"
)
_DHDNA_GATEKEEPING_RE = stdlib_re.compile(
    r"(?i)\b(?:chỉ\s+(?:ghi\s+nhận|xác\s+nhận|phê\s+duyệt|nghiệm\s+thu|đóng\s+lỗi|chấp\s+thuận)\s+khi|"
    r"không\s+được\s+(?:xem|tính|coi)\s+là\s+(?:hoàn\s+thành|kết\s+quả)|"
    r"điều\s+kiện\s+(?:chặn|tiên\s+quyết|bắt\s+buộc)|"
    r"nếu\s+[^.\n]{3,60}\s+chưa\s+đạt[^.\n]{0,40}\s+(?:phải|cần)\s+(?:dời|giảm\s+phạm\s+vi|dừng))\b"
)
_DHDNA_INTERMEDIATE_RE = stdlib_re.compile(
    r"(?i)\b(?:hoạt\s+động\s+trung\s+gian|đầu\s+ra\s+kiểm\s+chứng|"
    r"chỉ\s+phản\s+ánh\s+tiến\s+độ|chưa\s+chứng\s+minh\s+[^.\n]{1,35}\s+sản\s+phẩm\s+cuối\s+cùng)\b"
)
_DHDNA_TEMPORAL_DELAY_RE = stdlib_re.compile(
    r"(?i)\b(?:quá\s+hạn\s+\d+\s+ngày|lùi\s+(?:hạn\s+)?\d+\s+ngày|"
    r"còn\s+\d+\s+ngày\s+đến\s+hạn|kéo\s+dài\s+\d+\s+(?:ngày|giờ)|trước\s+\d+\s+giờ|t-\d+h)\b"
)
_DHDNA_TRIANGULATION_RE = stdlib_re.compile(
    r"(?i)\b(?:trong\s+khi\s+[^.\n]{2,50}\s+ghi\s+nhận|"
    r"so\s+với\s+(?:số\s+liệu|báo\s+cáo)\s+của|"
    r"tuy\s+nhiên\s+(?:nhật\s+ký|thực\s+tế|kết\s+quả\s+đối\s+chiếu)\s+ghi\s+nhận)\b"
)
_TWO_PART_HEADING_RE = stdlib_re.compile(r"(?i),\s*(?:nhưng|tuy\s+nhiên|trong\s+khi)\s+")
_PERIOD_LEADIN_RE = stdlib_re.compile(
    r"(?m)^\s*(?:Cơ\s+sở\s+kết\s+luận|Giới\s+hạn\s+của\s+kết\s+luận|Điều\s+kiện\s+thay\s+đổi\s+ý\s+kiến|"
    r"Thực\s+trạng(?:\s+và\s+bằng\s+chứng)?|Yêu\s+cầu(?:\s+cần\s+đạt)?|Nguyên\s+nhân(?:\s+kiểm\s+soát)?|"
    r"Rủi\s+ro(?:\s+và\s+ảnh\s+hưởng)?|Kiến\s+nghị(?:\s+kiểm\s+toán)?)\.\s+"
)
_SINGLE_CO_THE_RE = stdlib_re.compile(r"(?i)\bcó\s+thể\b")
_STACKED_HEDGING_RE = stdlib_re.compile(
    r"(?i)\b(?:có\s+thể\s+có\s+khả\s+năng|dường\s+như\s+có\s+vẻ|khả\s+năng\s+có\s+thể)\b"
)
_DENOM_RATIO_RE = stdlib_re.compile(
    r"(?i)\b(\d+(?:[.,]\d+)*)\s*/\s*(\d+(?:[.,]\d+)*)\s+([a-zà-ỹđ]+(?:\s+[a-zà-ỹđ]+)?)\b"
)
_DENOM_HEAD_NOUNS: frozenset[str] = frozenset(
    {"đơn", "nội", "hợp", "chỉ", "hành", "kịch", "phiếu", "mục", "bản", "tình", "khoản"}
)


def _safe_parse_docx_xml(zf: zipfile.ZipFile, member: str) -> ET.Element:
    """Đọc XML từ kho lưu trữ `.docx` với giới hạn kích thước giải nén và chặn khai báo DTD/ENTITY."""
    info = zf.getinfo(member)
    if info.file_size > _MAX_DOCX_XML_BYTES:
        msg = f"Thành phần XML '{member}' vượt ngưỡng an toàn ({info.file_size} byte)."
        raise ValueError(msg)
    raw = zf.read(member)
    if len(raw) > _MAX_DOCX_XML_BYTES or _FORBIDDEN_XML_DECL_RE.search(raw):
        msg = f"Thành phần XML '{member}' chứa khai báo DTD/ENTITY hoặc vượt ngưỡng kích thước."
        raise ValueError(msg)
    # Đã khóa kích thước giải nén và loại trừ hoàn toàn khai báo DOCTYPE/ENTITY trước khi phân tích
    return ET.fromstring(raw)  # noqa: S314


def _read_docx_core_props(zf: zipfile.ZipFile, meta: DocxMetadata) -> None:
    if "docProps/core.xml" not in zf.namelist():
        return
    try:
        core_root = _safe_parse_docx_xml(zf, "docProps/core.xml")
    except ET.ParseError:
        return
    t_el = core_root.find("dc:title", _DOCX_NS)
    c_el = core_root.find("dc:creator", _DOCX_NS)
    m_el = core_root.find("dcterms:modified", _DOCX_NS)
    meta["core_title"] = (t_el.text or "").strip() if t_el is not None else ""
    meta["creator"] = (c_el.text or "").strip() if c_el is not None else ""
    meta["modified"] = (m_el.text or "").strip() if m_el is not None else ""


def _extract_docx_para_text(p_elem: ET.Element) -> tuple[str, int]:
    lvl = 0
    p_pr = p_elem.find("w:pPr", _DOCX_NS)
    if p_pr is not None:
        p_style = p_pr.find("w:pStyle", _DOCX_NS)
        if p_style is not None:
            m_h = _DOCX_HEADING_STYLE_RE.match(p_style.attrib.get(_DOCX_W_VAL, ""))
            if m_h:
                lvl = int(m_h.group(1))
    chunks: list[str] = []
    for node in p_elem.iter():
        if node.tag == _DOCX_W_T and node.text:
            chunks.append(node.text)
        elif node.tag in _DOCX_W_TAB_OR_BR:
            chunks.append(" ")
    return " ".join("".join(chunks).split()), lvl


def _extract_docx_table_md(tbl_elem: ET.Element, ignore_cols: set[int]) -> str:
    rows_md: list[str] = []
    for r_idx, tr in enumerate(tbl_elem.findall("w:tr", _DOCX_NS)):
        cells: list[str] = []
        for c_idx, tc in enumerate(tr.findall("w:tc", _DOCX_NS), 1):
            if r_idx >= 1 and c_idx in ignore_cols:
                cells.append("")
                continue
            p_texts = [
                pt.replace("|", "/") for p_el in tc.findall("w:p", _DOCX_NS) if (pt := _extract_docx_para_text(p_el)[0])
            ]
            cells.append("; ".join(p_texts))
        if any(c.strip() for c in cells):
            rows_md.append("| " + " | ".join(cells) + " |")
            if len(rows_md) == 1:
                rows_md.append("| " + " | ".join("---" for _ in cells) + " |")
    return "\n".join(rows_md)


def _detect_docx_title_mismatch(core_title: str, blocks: Sequence[str]) -> str | None:
    if not core_title:
        return None
    m_title_wave = _DOCX_TITLE_WAVE_RE.search(core_title)
    if not m_title_wave:
        return None
    unit_name = m_title_wave.group(1).lower()
    title_num = m_title_wave.group(2).upper()
    m_body_wave = stdlib_re.search(rf"(?i)\b{stdlib_re.escape(unit_name)}\s+(\d+|[ivx]+)\b", "\n".join(blocks[:8]))
    if m_body_wave and m_body_wave.group(1).upper() != title_num:
        return (
            f"Thuộc tính Title của tệp .docx ghi '{core_title}' ({unit_name} {title_num}) "
            f"nhưng tiêu đề văn bản là {unit_name} {m_body_wave.group(1).upper()} "
            "(nguy cơ sót số liệu từ tệp mẫu kỳ trước)."
        )
    return None


def extract_docx_text_and_meta(path: Path, ignore_cols: set[int] | None = None) -> tuple[str, DocxMetadata]:
    """Đọc trực tiếp tệp `.docx` bằng thư viện chuẩn và chuyển sang định dạng Markdown chuẩn."""
    meta: DocxMetadata = {
        "core_title": "",
        "creator": "",
        "modified": "",
        "paragraph_blocks": 0,
        "table_blocks": 0,
        "template_title_mismatch": None,
    }
    ig = ignore_cols or set()
    blocks: list[str] = []
    with zipfile.ZipFile(path, "r") as zf:
        _read_docx_core_props(zf, meta)
        root = _safe_parse_docx_xml(zf, "word/document.xml")
        body = root.find("w:body", _DOCX_NS)
        if body is None:
            return "", meta
        for child in body:
            if child.tag == _DOCX_W_P:
                txt, lvl = _extract_docx_para_text(child)
                if txt:
                    meta["paragraph_blocks"] += 1
                    blocks.append(f"{'#' * lvl} {txt}" if lvl > 0 else txt)
            elif child.tag == _DOCX_W_TBL:
                tbl_md = _extract_docx_table_md(child, ig)
                if tbl_md:
                    meta["table_blocks"] += 1
                    blocks.append(tbl_md)
    meta["template_title_mismatch"] = _detect_docx_title_mismatch(meta["core_title"], blocks)
    return "\n\n".join(blocks), meta


def read_utf8(path: Path | str, ignore_cols: set[int] | None = None) -> str:
    if str(path) == "-":
        return filter_markdown_table_columns(sys.stdin.read(), ignore_cols or set())
    p = Path(path)
    if p.suffix.lower() == ".docx":
        return extract_docx_text_and_meta(p, ignore_cols=ignore_cols)[0]
    return filter_markdown_table_columns(p.read_text(encoding="utf-8-sig"), ignore_cols or set())


def compute_sliding_mattr(tokens: Sequence[str], window: int = 50, step: int = 10) -> float:
    """Tính MATTR bằng cửa sổ trượt Counter trong thời gian tuyến tính O(N)."""
    n_toks = len(tokens)
    if n_toks == 0:
        return 0.0
    if n_toks < window:
        return len(set(tokens)) / n_toks

    counts: collections.Counter[str] = collections.Counter(tokens[:window])
    inv_win = 1.0 / window
    ratios: list[float] = [len(counts) * inv_win]
    for start in range(step, n_toks - window + 1, step):
        prev = start - step
        for out_tok in tokens[prev:start]:
            new_c = counts[out_tok] - 1
            if new_c == 0:
                del counts[out_tok]
            else:
                counts[out_tok] = new_c
        for in_tok in tokens[prev + window : start + window]:
            counts[in_tok] += 1
        ratios.append(len(counts) * inv_win)
    return statistics.mean(ratios)


def max_table_sentence_words(masked_full: str) -> int:
    """Đo độ dài câu lớn nhất (theo số từ) bên trong các ô bảng Markdown/docx."""
    max_wc = 0
    for ln in masked_full.splitlines():
        st = ln.strip()
        if st.startswith("|") and st.endswith("|") and not SemanticMasker.MD_TABLE_SEP_RE.match(st):
            for seg in _TBL_SENT_SPLIT_RE.split(st):
                if _VI_DIAC_RE.search(seg):
                    max_wc = max(max_wc, len(_SENT_WORD_TOKEN_RE.findall(seg)))
    return max_wc


def _sentence_length_stats(lengths: Sequence[int], *, max_table_sent: int = 0) -> tuple[float, float, float, list[str]]:
    warnings: list[str] = []
    mean_len = statistics.mean(lengths) if lengths else 0.0
    cv = (statistics.pstdev(lengths) / mean_len) if len(lengths) >= 3 and mean_len else 0.0
    if len(lengths) >= 4 and cv < 0.30:
        warnings.append(f"Độ dài câu quá đều (CV={cv:.2f} < 0.30) — thiếu nhịp câu ngắn xen câu dài.")
    if mean_len > 28:
        warnings.append(f"Câu trung bình khá dài ({mean_len:.1f} âm tiết) — nên tách bớt mệnh đề phụ.")
    max_len = max(max(lengths, default=0), max_table_sent)
    if max_len > 35:
        warnings.append(f"Có câu dài tới {max_len} từ (> 35 từ) — cần tách thành các câu ngắn độc lập.")
    skew = 0.0
    if len(lengths) >= 5 and cv > 0:
        std = statistics.pstdev(lengths)
        skew = sum(((x - mean_len) / std) ** 3 for x in lengths) / len(lengths)
    return mean_len, cv, skew, warnings


def _punct_entropy_and_zlib(sample_prose: str, prose: str) -> tuple[float, float]:
    puncts = _PUNCT_CHAR_RE.findall(sample_prose)
    if puncts:
        p_counts = collections.Counter(puncts)
        total_p = len(puncts)
        entropy = -sum((c / total_p) * math.log2(c / total_p) for c in p_counts.values())
    else:
        entropy = 0.0
    encoded = prose.encode("utf-8") if prose else b" "
    comp_ratio = len(zlib.compress(encoded)) / max(len(encoded), 1)
    return entropy, comp_ratio


def compute_stylometry(masked_prose: str, *, max_table_sent: int = 0) -> StylometryReport:
    """Tính 18 chỉ số nhịp học (`stylometry`) kèm cảnh báo câu quá dài hoặc nhịp đều."""
    sample_prose = masked_prose[:30000]
    prose = "\n".join(ln.strip() for ln in sample_prose.splitlines() if ln.strip() and not ln.lstrip().startswith("#"))
    lengths = [wc for s in _SENT_SPLIT_NL_RE.split(prose) if (wc := len(_SENT_WORD_TOKEN_RE.findall(s))) >= 2]
    paras = [p.strip() for p in _PARA_BREAK_RE.split(sample_prose) if p.strip() and not p.lstrip().startswith("#")]
    para_sent_counts = [
        sum(1 for s in _SENT_SPLIT_INLINE_RE.split(p) if len(_SENT_WORD_TOKEN_RE.findall(s)) >= 2) for p in paras
    ]
    para_w_lens = [len(p.split()) for p in paras if len(p.split()) >= 5]

    mean_len, cv, skew, warnings = _sentence_length_stats(lengths, max_table_sent=max_table_sent)
    para_cv = (
        statistics.pstdev(para_w_lens) / statistics.mean(para_w_lens)
        if len(para_w_lens) >= 3 and statistics.mean(para_w_lens)
        else 0.0
    )
    tokens = [t for t in _VI_ALPHA_WORD_RE.findall(_safe_lower_preserve_len(prose)) if len(t) > 1]
    punct_entropy, comp_ratio = _punct_entropy_and_zlib(sample_prose, prose)
    han_viet_admin = len(_HAN_VIET_ADMIN_RE.findall(prose))

    return {
        "so_cau": len(lengths),
        "so_doan": len(paras),
        "cau_trung_binh_doan": round(statistics.mean(para_sent_counts), 2) if para_sent_counts else 0.0,
        "dai_cau_tb": round(mean_len, 1),
        "bien_dong_do_dai_cau_cv": round(cv, 2),
        "lech_do_dai_cau_skew": round(skew, 2),
        "bien_dong_do_dai_doan_cv": round(para_cv, 2),
        "ty_le_tu_rieng_ttr_am_tiet": round((len(set(tokens)) / len(tokens)) if tokens else 0.0, 2),
        "mattr_cua_so_50": round(compute_sliding_mattr(tokens), 2),
        "so_dau_cham_than": sample_prose.count("!"),
        "tro_tu_cuoi_cau": len(_PARTICLES_RE.findall(prose)),
        "lien_tu_hinh_thuc": len(_FORMAL_CONN_RE.findall(prose)),
        "tu_noi_khau_ngu": len(_COLLOQ_CONN_RE.findall(prose)),
        "han_viet_hanh_chinh_tren_1000": round((han_viet_admin / max(len(tokens), 1)) * 1000.0, 1),
        "tu_lay": len(_TU_LAY_RE.findall(prose)),
        "entropy_dau_cau_bit": round(punct_entropy, 2),
        "do_nen_zlib": round(comp_ratio, 2),
        "canh_bao": warnings,
    }


def _detect_denominator_drift(masked_all_text: str) -> dict[str, list[str]]:
    denom_map: dict[str, set[str]] = collections.defaultdict(set)
    for m_ratio in _DENOM_RATIO_RE.finditer(masked_all_text):
        denom_val = m_ratio.group(2)
        denom_digits = denom_val.replace(".", "").replace(",", "")
        if not denom_digits.isdigit() or int(denom_digits) < 50:
            continue
        noun_phrase = m_ratio.group(3).lower().strip()
        if noun_phrase.split()[0] in _DENOM_HEAD_NOUNS:
            denom_map[noun_phrase].add(denom_val)
    return {k: sorted(v) for k, v in denom_map.items() if len(v) >= 2}


def _compute_dhdna_metrics(
    masked_full: str, prose_only_text: str, masked_all_text: str, total_wc: int
) -> DhdnaVoiceMetrics:
    num_per_1k = round((len(_NUM_TOKEN_RE.findall(masked_all_text)) * 1000.0) / total_wc, 1)
    raw_sents = [s.strip() for s in _SENT_SPLIT_NL_RE.split(prose_only_text) if len(s.strip().split()) >= 2]
    pct_sents = [s for s in raw_sents if _PCT_TOKEN_RE.search(s)]
    paired_pct = sum(1 for s in pct_sents if _PCT_PAIRED_RE.search(s))
    headings = [ln.lstrip("#").strip() for ln in masked_full.splitlines() if ln.lstrip().startswith("#")]
    return {
        "mat_do_so_tren_1000_tu": num_per_1k,
        "tong_so_ty_le_phan_tram": len(pct_sents),
        "ty_le_phan_tram_kem_tu_mau": round(paired_pct / len(pct_sents), 2) if pct_sents else 1.0,
        "ranh_gioi_bang_chung_d12": len(_DHDNA_EVIDENCE_RE.findall(masked_all_text)),
        "cong_chan_dieu_kien_d6": len(_DHDNA_GATEKEEPING_RE.findall(masked_all_text)),
        "tach_hoat_dong_trung_gian_d1": len(_DHDNA_INTERMEDIATE_RE.findall(masked_all_text)),
        "neo_thoi_gian_tre_han_d11": len(_DHDNA_TEMPORAL_DELAY_RE.findall(masked_all_text)),
        "tam_giac_doi_chung_da_nguon": len(_DHDNA_TRIANGULATION_RE.findall(masked_all_text)),
        "tieu_de_hai_ve_doi_sanh": sum(1 for h in headings if ":" in h and _TWO_PART_HEADING_RE.search(h)),
        "nhan_doan_ket_thuc_dau_cham": len(_PERIOD_LEADIN_RE.findall(prose_only_text)),
        "tu_tinh_thai_don_co_the": len(_SINGLE_CO_THE_RE.findall(masked_all_text)),
        "chong_tu_rao_don": len(_STACKED_HEDGING_RE.findall(masked_all_text)),
        "ung_vien_lech_mau_so": _detect_denominator_drift(masked_all_text),
    }


def _classify_voice_archetype(stylo: StylometryReport, dm: DhdnaVoiceMetrics) -> VoiceArchetype:
    mean_sent = stylo["dai_cau_tb"]
    sent_cv = stylo["bien_dong_do_dai_cau_cv"]
    gatekeeper_hits = dm["ranh_gioi_bang_chung_d12"] + dm["cong_chan_dieu_kien_d6"] + dm["tach_hoat_dong_trung_gian_d1"]
    if 12.0 <= mean_sent <= 26.0 and sent_cv >= 0.40 and gatekeeper_hits >= 5:
        return {
            "code": "DIRECT_EXECUTIVE_GATEKEEPER",
            "description_vi": (
                "Giọng Kiểm toán / Quản trị Trực diện: câu ngắn cô đọng, biên độ nhịp câu rộng, "
                "mở đoạn bằng kết luận, khóa chặt ranh giới bằng chứng (D12) và cổng điều kiện (D6)."
            ),
        }
    if dm["tieu_de_hai_ve_doi_sanh"] >= 2 or dm["tam_giac_doi_chung_da_nguon"] >= 3:
        return {
            "code": "BALANCED_COMPARATIVE_SUPERVISORY",
            "description_vi": (
                "Giọng Giám sát Đối sánh Hai chiều: tiêu đề hai vế đối lập "
                "(điểm đạt được vs điểm nghẽn), tam giác đối chứng đa nguồn và cặp Tử số/Mẫu số (%)."
            ),
        }
    if dm["mat_do_so_tren_1000_tu"] >= 35.0 and mean_sent <= 20.0:
        return {
            "code": "TECHNICAL_RCA_ASSURANCE",
            "description_vi": (
                "Giọng Bảo đảm Kỹ thuật & Truy vết Nguyên nhân gốc: "
                "câu ngắn giàu thông số kỹ thuật, khung giờ và phân rã cơ chế."
            ),
        }
    if mean_sent > 28.0 or (sent_cv < 0.30 and stylo["so_cau"] >= 6):
        return {
            "code": "BUREAUCRATIC_OR_MONOTONE_DRAFT",
            "description_vi": (
                "Bản nháp hành chính câu dài hoặc nhịp đều: cần tách câu mở đầu nêu kết luận ngắn (6-14 từ) "
                "và gọt bỏ cụm danh từ hóa/rào đón."
            ),
        }
    return {
        "code": "CLEAN_GENERAL_VIETNAMESE",
        "description_vi": "Văn xuôi tiếng Việt mạch lạc, nhịp câu cân đối.",
    }


def profile_text(
    text: str,
    label: str = "-",
    docx_meta: DocxMetadata | dict[str, Any] | None = None,
    ignore_cols: set[int] | None = None,
) -> ProfileReport:
    """Đo tất định 18 chỉ số nhịp câu (`stylometry`) và 12 chỉ số kỷ luật lập luận / bằng chứng `DHDNA`."""
    masked_full = SemanticMasker.mask_preserve_offsets(text, mask_quotes=True)
    prose_only_text = "\n".join(
        ln for ln in masked_full.splitlines() if not (ln.strip().startswith("|") and ln.strip().endswith("|"))
    )
    masked_all_text = SemanticMasker.flatten_markdown_tables_preserve_lines(masked_full)
    stylo = compute_stylometry(prose_only_text, max_table_sent=max_table_sentence_words(masked_full))
    total_wc = max(len(masked_all_text.split()), 1)
    dhdna_metrics = _compute_dhdna_metrics(masked_full, prose_only_text, masked_all_text, total_wc)
    return {
        "version": VERSION,
        "file": label,
        "sha256_16": hashlib.sha256(text.encode("utf-8")).hexdigest()[:16],
        "word_count_total": total_wc,
        "word_count_prose": len(prose_only_text.split()),
        "ignored_table_cols": sorted(ignore_cols) if ignore_cols else [],
        "docx_metadata": docx_meta or {},
        "stylometry": stylo,
        "dhdna_voice_metrics": dhdna_metrics,
        "voice_archetype": _classify_voice_archetype(stylo, dhdna_metrics),
    }
