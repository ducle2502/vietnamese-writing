#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""vi_scanner.py (v2.0.0) - Công cụ rà lỗi câu chữ máy móc, sáo rỗng và dịch thô tiếng Việt.

Nguyên tắc thiết kế:
1. Chỉ chỉ ra vị trí câu chữ cần người viết hoặc Agent đọc lại. Công cụ không đoán ai là tác giả và không chấm phần trăm văn bản do AI tạo.
2. Không tự ý sửa tệp gốc. Khi biên tập phải giữ nguyên số liệu, từ phủ định, điều kiện, mức độ chắc chắn, đường dẫn, khối mã lệnh và nguồn trích dẫn.
3. Chạy nhanh bằng thư viện chuẩn Python 3.11+ (tự dùng google-re2 nếu máy có sẵn), không dùng biểu thức lặp lồng nhau gây treo máy (ReDoS).
4. Mặc định lệnh `scan` chạy và xuất đủ 100% tín hiệu của tất cả 7 nhóm văn bản (`--profile all`), kèm nhãn nhóm áp dụng để Agent tự chọn lọc theo ngữ cảnh.

Cách dùng:
  python scripts/vi_scanner.py scan FILE.md
  python scripts/vi_scanner.py scan FILE.md --json
  python scripts/vi_scanner.py scan FILE.md --profile audit_report
  python scripts/vi_scanner.py verify TRUOC.md SAU.md
  python scripts/vi_scanner.py list-rules
  python scripts/vi_scanner.py check-maintenance
  python scripts/vi_scanner.py selftest
"""
from __future__ import annotations

import argparse
import collections
from dataclasses import asdict, dataclass, field
import datetime as dt
from enum import StrEnum
import hashlib
import json
import math
from pathlib import Path
import re as stdlib_re
import sys
import time
from typing import Any, Sequence

try:
    import re2 as regex_engine  # type: ignore[import-not-found]
    USING_RE2 = True
except ImportError:
    import re as regex_engine
    USING_RE2 = False

VERSION = "2.0.0"
SCHEMA_VERSION = "2.0.0"

# ============================================================================
# DANH SÁCH TỪ TIẾNG ANH ĐÃ QUEN DÙNG TRONG TIẾNG VIỆT (CẦN CẬP NHẬT ĐỊNH KỲ)
# Lưu ý vận hành: Đây là danh sách từ vựng duy nhất được duy trì trong mã nguồn
# để tránh bắt nhầm các từ mượn đã đi vào giao tiếp bình thường. Cần rà soát và
# cập nhật định kỳ hàng quý hoặc hàng năm qua lệnh `check-maintenance`.
# ============================================================================
LOANWORDS_REVIEW_META: dict[str, Any] = {
    "last_reviewed": "2026-11-10",
    "cadence": "quarterly_or_annual",
    "recommended_interval_days": 90,
    "max_interval_days": 365,
    "note": (
        "Rà soát hàng quý hoặc hàng năm: bổ sung từ tiếng Anh đã quen dùng rộng rãi "
        "mà nếu dịch sang tiếng Việt sẽ gây ngô nghê, và gỡ bỏ từ chỉ dùng trong "
        "nhóm hẹp."
    ),
}

# Nhóm 1: Từ đã nhập tịch sâu, dùng tự nhiên trong mọi loại văn bản (kể cả báo cáo, pháp lý)
UNIVERSAL_NATURALIZED_LOANWORDS: frozenset[str] = frozenset({
    "email", "web", "website", "internet", "wifi", "video", "logic",
    "logistics", "container", "chatbot", "vaccine", "virus", "vitamin",
    "camera", "radar", "laser", "taxi", "bus", "metro", "hotel", "resort",
    "villa", "plastic", "diesel", "gas", "dollar", "usd", "vnd", "eur",
    "jpy", "gbp", "gmt", "utc", "iso", "ieee", "apa", "doi", "isbn", "issn",
    "url", "http", "https", "html", "xml", "json", "csv", "pdf", "qr", "otp",
    "usb", "sim", "pin", "erp", "crm", "gdp", "cpi", "fdi", "oda", "sme",
    "vat", "vas", "ifrs", "kpi",
})

# Nhóm 2: Từ công sở, truyền thông và kỹ thuật thông dụng (hợp lệ ở văn bản chung,
# mạng xã hội, học thuật, dịch thuật; riêng báo cáo quản trị cấp cao nên cân nhắc người đọc)
WORKPLACE_TECH_LOANWORDS: frozenset[str] = frozenset({
    "app", "file", "folder", "link", "code", "bug", "team", "leader",
    "mentor", "slide", "word", "excel", "powerpoint", "online", "offline",
    "livestream", "podcast", "blog", "post", "marketing", "sale", "sales",
    "pr", "seo", "okr", "cv", "profile", "portfolio", "feedback", "review",
    "trend", "top", "fan", "show", "game", "workshop", "webinar", "startup",
    "freelancer", "remote", "hybrid", "deadline", "target", "plan", "brief",
    "concept", "layout", "design", "font", "logo", "banner", "poster",
    "slogan", "menu", "combo", "voucher", "serum", "ai", "it", "ram", "cpu",
    "gpu", "api", "sql", "cloud", "server", "client", "module", "plugin",
    "widget", "token", "prompt", "agent", "model", "dataset", "benchmark",
    "regex", "linter", "cli", "sdk", "ide", "git", "repo", "commit",
    "branch", "merge", "push", "pull",
})


class Profile(StrEnum):
    GENERAL = "general"
    AUDIT_REPORT = "audit_report"
    ACADEMIC = "academic"
    LEGAL = "legal"
    MARKETING = "marketing"
    SOCIAL_MEDIA = "social_media"
    TRANSLATION = "translation"


ALL_PROFILES: tuple[Profile, ...] = tuple(Profile)


class Severity(StrEnum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass(frozen=True, slots=True)
class ThresholdSpec:
    per_doc: int | None = None
    per_para: int | None = None
    per_1000_words: float | None = None
    cv_max: float | None = None
    min_paras: int = 4

    @classmethod
    def parse(cls, raw: str) -> ThresholdSpec:
        per_doc: int | None = None
        per_para: int | None = None
        per_1000w: float | None = None
        cv_max: float | None = None
        min_paras = 4
        for part in raw.split(";"):
            part = part.strip()
            if not part:
                continue
            if part.endswith("/doc"):
                per_doc = int(part.removesuffix("/doc"))
            elif part.endswith("/para"):
                per_para = int(part.removesuffix("/para"))
            elif part.endswith("/1000w"):
                per_1000w = float(part.removesuffix("/1000w"))
            elif part.startswith("CV<"):
                cv_str, paras_str = part.split("/")
                cv_max = float(cv_str.removeprefix("CV<"))
                min_paras = int(paras_str.removesuffix("paras"))
        return cls(
            per_doc=per_doc,
            per_para=per_para,
            per_1000_words=per_1000w,
            cv_max=cv_max,
            min_paras=min_paras,
        )


@dataclass(frozen=True, slots=True)
class RuleDefinition:
    rule_id: str
    category: str
    pattern_type: str
    description_vi: str
    regex_or_algorithm: str
    severity: Severity
    weight: float
    profiles: frozenset[Profile]
    threshold: ThresholdSpec
    exceptions: tuple[str, ...]
    bad_example: str
    better_example: str
    source_url: str
    evidence_strength: str
    status: str = "active"

    @property
    def exempt_profiles(self) -> tuple[str, ...]:
        return tuple(p.value for p in ALL_PROFILES if p not in self.profiles)


@dataclass(slots=True)
class Finding:
    rule_id: str
    category: str
    severity: str
    weight: float
    line: int
    col: int
    matched_text: str
    context: str
    description_vi: str
    suggestion_vi: str
    applicable_profiles: list[str]
    exempt_profiles: list[str]
    evidence_strength: str


@dataclass(slots=True)
class ScanReport:
    schema_version: str
    scanner_version: str
    profile: str
    word_count: int
    paragraph_count: int
    findings_count: int
    error_count: int
    warning_count: int
    info_count: int
    findings_per_1000_words: float
    weighted_density_score: float
    category_breakdown: dict[str, int]
    elapsed_ms: float
    maintenance_due: bool
    disclaimer: str
    semantic_invariants_summary: dict[str, int]
    findings: list[Finding] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, indent=indent)


class SemanticMasker:
    """Che các vùng không được phép bắt lỗi (khối code, mã nội dòng, đích liên kết,
    câu trích dẫn nguyên văn trong ngoặc kép) bằng khoảng trắng cùng độ dài để giữ
    chính xác số dòng và số cột trên tệp gốc; đồng thời trích xuất 6 nhóm dữ kiện
    cần bảo toàn khi biên tập.
    """

    FRONTMATTER_RE = stdlib_re.compile(r"\A---\s*\n[\s\S]*?\n---\s*(?:\n|$)")
    CODE_BLOCK_RE = stdlib_re.compile(r"```[\s\S]*?```")
    INLINE_CODE_RE = stdlib_re.compile(r"`[^`\n]+`")
    QUOTED_SPEECH_RE = stdlib_re.compile(r'"[^\n"]{10,300}"|“[^\n”]{10,300}”')
    MD_LINK_TARGET_RE = stdlib_re.compile(r"(\]\()([^)\n]+)(\))")
    HTML_COMMENT_RE = stdlib_re.compile(r"<!--[\s\S]*?-->")
    HTML_IMG_RE = stdlib_re.compile(
        r"</?(?:img|picture|source|div|p|table|tr|td|th|br|a|details|summary)(?:\s+[^>]+|\s*)>",
        stdlib_re.IGNORECASE,
    )
    BARE_URL_RE = stdlib_re.compile(r"(?:https?|file)://[^\s)\">]+")

    @staticmethod
    def _blank_span(raw: str) -> str:
        return "".join("\n" if ch == "\n" else " " for ch in raw)

    @classmethod
    def _blank_match(cls, match: stdlib_re.Match[str]) -> str:
        return cls._blank_span(match.group(0))

    @classmethod
    def mask_code_and_quotes(cls, text: str, mask_quotes: bool = True) -> str:
        masked = cls.FRONTMATTER_RE.sub(cls._blank_match, text)
        masked = cls.CODE_BLOCK_RE.sub(cls._blank_match, masked)
        masked = cls.INLINE_CODE_RE.sub(cls._blank_match, masked)
        masked = cls.HTML_COMMENT_RE.sub(cls._blank_match, masked)
        masked = cls.HTML_IMG_RE.sub(cls._blank_match, masked)
        if mask_quotes:
            masked = cls.QUOTED_SPEECH_RE.sub(cls._blank_match, masked)
        return masked

    @classmethod
    def mask_preserve_offsets(cls, text: str, mask_quotes: bool = True) -> str:
        masked = cls.mask_code_and_quotes(text, mask_quotes=mask_quotes)
        masked = cls.MD_LINK_TARGET_RE.sub(
            lambda m: m.group(1) + cls._blank_span(m.group(2)) + m.group(3),
            masked,
        )
        masked = cls.BARE_URL_RE.sub(cls._blank_match, masked)
        return masked

    @staticmethod
    def flatten_markdown_tables_preserve_lines(masked_text: str) -> str:
        """Thay vách ngăn `|` của bảng Markdown bằng khoảng trắng để quét câu chữ
        bên trong ô bảng mà không làm lệch số dòng, số cột."""
        out_lines: list[str] = []
        for line in masked_text.splitlines(keepends=True):
            stripped = line.strip()
            if stripped.startswith("|") and stripped.endswith("|"):
                if stdlib_re.match(r"^\|[\s:\-|]+\|$", stripped):
                    out_lines.append("".join("\n" if c == "\n" else " " for c in line))
                    continue
                out_lines.append(line.replace("|", " "))
            else:
                out_lines.append(line)
        return "".join(out_lines)

    @classmethod
    def extract_invariants(cls, text: str) -> dict[str, list[str]]:
        return {
            "numbers": stdlib_re.findall(r"\b\d+(?:[.,/]\d+)*%?\b", text),
            "negations": [
                w.lower()
                for w in stdlib_re.findall(
                    r"(?i)\b(?:không|chưa|chẳng|chớ|miễn|cấm|phi|vô)\b", text
                )
            ],
            "conditionals": [
                w.lower()
                for w in stdlib_re.findall(
                    r"(?i)\b(?:nếu|trừ khi|miễn là|trong trường hợp|với điều kiện)\b",
                    text,
                )
            ],
            "modals": [
                w.lower()
                for w in stdlib_re.findall(
                    r"(?i)\b(?:có thể|phải|bắt buộc|ước tính|khoảng|dự kiến|tối đa|tối thiểu)\b",
                    text,
                )
            ],
            "urls": [
                u.split("?utm_source=")[0]
                for u in stdlib_re.findall(r"(?:https?|file)://[^\s)\">]+", text)
            ],
            "citations": stdlib_re.findall(
                r"\([A-ZÀ-ỸĐ][^()\n]{2,50},\s*\d{4}[a-z]?\)|\[\d+(?:,\s*\d+)*\]",
                text,
            ),
            "code_blocks": cls.CODE_BLOCK_RE.findall(text),
            "inline_code": cls.INLINE_CODE_RE.findall(text),
            "frontmatter": cls.FRONTMATTER_RE.findall(text),
        }

    @classmethod
    def validate_rewrite_safety(
        cls,
        original: str,
        rewritten: str,
        strict_negations_and_modals: bool = False,
    ) -> tuple[bool, list[str]]:
        inv_orig = cls.extract_invariants(original)
        inv_rewr = cls.extract_invariants(rewritten)
        errors: list[str] = []

        hard_keys = (
            "numbers",
            "urls",
            "conditionals",
            "citations",
            "code_blocks",
            "inline_code",
            "frontmatter",
        )
        labels = {
            "numbers": "Sai lệch số liệu/ngày tháng",
            "urls": "Sai lệch đường dẫn URL",
            "conditionals": "Thay đổi từ chỉ điều kiện",
            "citations": "Mất hoặc đổi nguồn trích dẫn",
            "code_blocks": "Khối mã lệnh bị sửa đổi",
            "inline_code": "Mã nội dòng bị sửa đổi",
            "frontmatter": "Frontmatter bị sửa đổi",
        }
        for key in hard_keys:
            if sorted(inv_orig[key]) != sorted(inv_rewr[key]):
                c_before = collections.Counter(inv_orig[key])
                c_after = collections.Counter(inv_rewr[key])
                removed = sorted((c_before - c_after).elements())
                added = sorted((c_after - c_before).elements())
                errors.append(f"{labels[key]}: mất={removed} | thêm={added}")

        if strict_negations_and_modals:
            for key, label in (
                ("negations", "Thay đổi từ phủ định"),
                ("modals", "Thay đổi từ chỉ mức độ chắc chắn"),
            ):
                if sorted(inv_orig[key]) != sorted(inv_rewr[key]):
                    c_before = collections.Counter(inv_orig[key])
                    c_after = collections.Counter(inv_rewr[key])
                    removed = sorted((c_before - c_after).elements())
                    added = sorted((c_after - c_before).elements())
                    errors.append(f"{label}: mất={removed} | thêm={added}")

        return (len(errors) == 0, errors)


def check_loanwords_maintenance(today: dt.date | None = None) -> dict[str, Any]:
    ref_date = today or dt.date.today()
    last_reviewed = dt.date.fromisoformat(LOANWORDS_REVIEW_META["last_reviewed"])
    days_elapsed = max(0, (ref_date - last_reviewed).days)
    rec_days = int(LOANWORDS_REVIEW_META["recommended_interval_days"])
    max_days = int(LOANWORDS_REVIEW_META["max_interval_days"])
    due = days_elapsed >= rec_days
    overdue = days_elapsed >= max_days
    return {
        "last_reviewed": LOANWORDS_REVIEW_META["last_reviewed"],
        "today": ref_date.isoformat(),
        "days_since_review": days_elapsed,
        "recommended_interval_days": rec_days,
        "max_interval_days": max_days,
        "due_for_quarterly_review": due,
        "overdue_annual_review": overdue,
        "universal_loanwords_count": len(UNIVERSAL_NATURALIZED_LOANWORDS),
        "workplace_tech_loanwords_count": len(WORKPLACE_TECH_LOANWORDS),
        "note": LOANWORDS_REVIEW_META["note"],
    }


def build_default_rules() -> list[RuleDefinition]:
    raw_rules = [
        # =====================================================================
        # NHÓM 1: AI_META_AND_STAGING (5 quy tắc)
        # =====================================================================
        (
            "VIS-AI-001", "AI_META_AND_STAGING", "regex",
            "Câu mở đầu hoặc kết thúc kiểu chatbot và lời tự xưng mô hình ngôn ngữ còn sót lại.",
            r"(?i)\b(?:tất nhiên rồi!?\s+dưới đây là|chắc chắn rồi!?\s+dưới đây là|hy vọng\s+(?:bài viết|thông tin|nội dung|câu trả lời|phân tích|chia sẻ)\s+này\s+(?:sẽ\s+)?hữu ích(?:\s+(?:cho|với)\s+bạn)?|hãy cho tôi biết nếu bạn\s+(?:cần thêm|muốn chỉnh sửa|có câu hỏi)|đừng ngần ngại\s+(?:hỏi|liên hệ)|chúc bạn một ngày\s+tốt lành|là một mô hình ngôn ngữ(?:\s+AI)?|as an ai language model)\b",
            Severity.ERROR, 1.0,
            "general|audit_report|academic|legal|marketing|social_media|translation",
            "1/doc", "direct_quotes|code_block",
            "Chắc chắn rồi! Dưới đây là bản phân tích chi tiết về doanh thu quý III năm 2025 đạt 450 tỷ đồng. Hy vọng thông tin này hữu ích cho bạn.",
            "Doanh thu quý III năm 2025 đạt 450 tỷ đồng.",
            "https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing", "strong",
        ),
        (
            "VIS-AI-002", "AI_META_AND_STAGING", "regex",
            "Chỗ trống nhắc điền chưa xóa ([Điền...]) hoặc tham số theo dõi nguồn chatbot trong đường dẫn.",
            r"(?i)(?:\[\s*(?:chèn|điền|insert|thêm)\s+[^\]]{2,50}\]|utm_source=(?:chatgpt\.com|perplexity|claude|openai))",
            Severity.ERROR, 1.0,
            "general|audit_report|academic|legal|marketing|social_media|translation",
            "1/doc", "code_block",
            "Công ty [Chèn tên công ty vào đây] đã ký hợp đồng trị giá 12 tỷ đồng (nguồn: https://example.com/report?utm_source=chatgpt.com).",
            "Công ty đã ký hợp đồng trị giá 12 tỷ đồng (nguồn: https://example.com/report).",
            "https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing", "strong",
        ),
        (
            "VIS-AI-003", "AI_META_AND_STAGING", "regex",
            "Mở bài công thức ('Trong bối cảnh/kỷ nguyên ... ngày càng phát triển/biến đổi').",
            r"(?i)\b(?:trong\s+(?:bối cảnh|kỷ nguyên|thời đại)\s+[^,.;:!?\n]{3,60}\s+(?:ngày càng\s+(?:phát triển|biến đổi|phức tạp|sâu rộng|mạnh mẽ|sôi động)|hiện nay|ngày nay)|với sự phát triển không ngừng của\s+[^,.;:!?\n]{3,50})\b",
            Severity.WARNING, 0.6,
            "general|audit_report|academic|legal|translation",
            "1/doc;2/1000w", "quoted_speech|dated_quantitative_context",
            "Trong bối cảnh nền kinh tế số ngày càng phát triển mạnh mẽ, ngân hàng đã giảm 15% chi phí vận hành năm 2025.",
            "Ngân hàng đã giảm 15% chi phí vận hành năm 2025 nhờ số hóa quy trình.",
            "https://github.com/blader/humanizer/blob/main/SKILL.md", "strong",
        ),
        (
            "VIS-AI-004", "AI_META_AND_STAGING", "regex",
            "Câu dẫn dắt vòng vo ('Hãy cùng khám phá/tìm hiểu', 'Câu hỏi đặt ra là... Câu trả lời là').",
            r"(?i)\b(?:hãy cùng\s+(?:chúng tôi\s+)?(?:đi sâu vào\s+)?(?:khám phá|tìm hiểu(?:\s+chi tiết)?|mổ xẻ)\s+trong\s+bài viết|câu hỏi đặt ra là[^?\n]{3,60}\?\s*câu trả lời\s+(?:ngắn gọn\s+)?là)\b",
            Severity.INFO, 0.4,
            "general|audit_report|academic|legal|translation",
            "1/doc", "profile:marketing|profile:social_media",
            "Hãy cùng chúng tôi đi sâu vào khám phá trong bài viết dưới đây về 3 nguyên nhân khiến lợi nhuận giảm 8%.",
            "Có 3 nguyên nhân chính khiến lợi nhuận giảm 8%.",
            "https://github.com/blader/humanizer/blob/main/SKILL.md", "medium",
        ),
        (
            "VIS-AI-005", "AI_META_AND_STAGING", "regex",
            "Kết bài tóm tắt gượng kèm lời hứa hẹn tương lai chung chung ('Tóm lại... hứa hẹn mở ra kỷ nguyên mới').",
            r"(?i)\b(?:(?:tóm lại|nhìn chung|xét cho cùng|tựu trung(?:\s+lại)?),\s+[^.\n]{5,90}\s+(?:hứa hẹn\s+(?:sẽ\s+)?mở ra|mở ra\s+một\s+(?:kỷ nguyên|chương)\s+mới|tương lai\s+(?:tươi sáng|rộng mở))|chặng đường phía trước còn dài)\b",
            Severity.WARNING, 0.7,
            "general|audit_report|academic|legal|marketing|translation",
            "1/doc", "quoted_speech",
            "Tóm lại, dự án nâng cấp trạm biến áp 110kV giúp tăng 30% công suất cấp điện, hứa hẹn sẽ mở ra một kỷ nguyên mới đầy tươi sáng cho ngành điện địa phương.",
            "Dự án nâng cấp trạm biến áp 110kV giúp tăng 30% công suất cấp điện cho địa phương.",
            "https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing", "strong",
        ),
        # =====================================================================
        # NHÓM 2: AI_RHETORICAL_INFLATION (5 quy tắc)
        # =====================================================================
        (
            "VIS-RHET-001", "AI_RHETORICAL_INFLATION", "regex",
            "Mẫu câu đòn bẩy 'Không chỉ (đơn thuần) là X, mà (còn/chính) là Y' hoặc lặp dày cụm phủ định bắc cầu.",
            r"(?i)\b(?:(?:đây\s+|nó\s+|điều này\s+)?không\s+(?:chỉ\s+)?(?:đơn thuần|phải chỉ|đơn giản)\s+là\s+[^,.;:\n]{3,60},\s*mà\s+(?:còn\s+|chính\s+)?là\s+(?:một\s+)?[^,.;:\n]{3,65}|không\s+chỉ\s+[^,.;:!?\n]{3,60}\s+mà\s+còn\b)",
            Severity.WARNING, 0.65,
            "general|audit_report|academic|legal|marketing|social_media|translation",
            "1/para;2/1000w", "legal_clause_citation",
            "Hệ thống ERP mới không chỉ đơn thuần là một phần mềm quản lý, mà còn là một cuộc cách mạng thay đổi tư duy vận hành của 500 nhân sự.",
            "Hệ thống ERP mới giúp 500 nhân sự chuẩn hóa quy trình quản lý và vận hành.",
            "https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing", "strong",
        ),
        (
            "VIS-RHET-002", "AI_RHETORICAL_INFLATION", "regex",
            "Lời khen phóng đại tầm vóc ('đóng vai trò then chốt/sống còn', 'đánh dấu bước ngoặt lịch sử', 'minh chứng sống động').",
            r"(?i)\b(?:đóng\s+(?:một\s+)?vai trò\s+(?:vô cùng\s+|cực kỳ\s+)?(?:then chốt|sống còn|tối quan trọng)|đánh dấu\s+(?:một\s+)?bước ngoặt\s+(?:mang tính\s+)?(?:lịch sử|thời đại)|là\s+(?:một\s+)?minh chứng\s+(?:sống động|hùng hồn)\s+cho)\b",
            Severity.WARNING, 0.6,
            "general|audit_report|academic|legal|translation",
            "1/para;2/1000w", "profile:marketing|historical_year_19xx",
            "Việc lắp đặt thêm 2 máy chủ dự phòng đóng một vai trò vô cùng then chốt và là minh chứng sống động cho cam kết bảo mật của công ty.",
            "Công ty lắp đặt thêm 2 máy chủ dự phòng để đảm bảo an toàn dữ liệu.",
            "https://arxiv.org/abs/2406.07016", "strong",
        ),
        (
            "VIS-RHET-003", "AI_RHETORICAL_INFLATION", "dictionary",
            "Ẩn dụ hoa mỹ dịch sát từ tiếng Anh của AI ('tấm thảm đa sắc', 'bức tranh toàn cảnh', 'ngọn hải đăng dẫn đường', 'đi sâu khám phá bản chất').",
            r"(?i)\b(?:tấm thảm\s+(?:đa sắc|phong phú|rực rỡ)|bức tranh\s+toàn cảnh(?:\s+đầy\s+biến động)?|ngọn hải đăng\s+(?:dẫn đường|soi sáng)|chìa khóa\s+(?:vàng|vạn năng)(?:\s+mở ra\s+cánh cửa)?|đi sâu\s+vào\s+khám phá\s+bản chất|kim chỉ nam\s+cho\s+mọi|tảng băng\s+chìm)\b",
            Severity.WARNING, 0.7,
            "general|audit_report|academic|legal|marketing|social_media|translation",
            "1/doc", "literal_physical_measurement_or_craft",
            "Báo cáo kiểm toán này phác họa bức tranh toàn cảnh đầy biến động và là ngọn hải đăng dẫn đường cho hội đồng quản trị trong năm 2026.",
            "Báo cáo kiểm toán này tổng hợp các rủi ro tài chính để hội đồng quản trị lập kế hoạch năm 2026.",
            "https://arxiv.org/abs/2406.07016", "strong",
        ),
        (
            "VIS-RHET-004", "AI_RHETORICAL_INFLATION", "regex",
            "Ghép gượng hai đầu mút lệch loại ('Từ những [A] cho đến các [B], tất cả đều...').",
            r"(?i)\btừ\s+(?:những\s+|các\s+)?[^,.;:\n]{4,55}\s+cho\s+đến\s+(?:những\s+|các\s+)?[^,.;:\n]{4,55},\s*(?:tất cả\s+đều|mọi\s+thứ\s+đều|không\s+gì\s+có thể)\b",
            Severity.INFO, 0.45,
            "general|audit_report|academic|legal|translation",
            "1/para;2/1000w", "numeric_or_date_range",
            "Từ những dòng mã nguồn nhỏ bé cho đến các chiến lược kinh doanh vĩ mô, tất cả đều cần được kiểm thử trước ngày 15/10.",
            "Cả mã nguồn lẫn quy trình nghiệp vụ đều cần được kiểm thử trước ngày 15/10.",
            "https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing", "medium",
        ),
        (
            "VIS-RHET-005", "AI_RHETORICAL_INFLATION", "regex",
            "Dẫn nguồn chung chung không tên ('Các chuyên gia cho rằng', 'Nhiều nghiên cứu chỉ ra rằng') mà thiếu trích dẫn cụ thể.",
            r"(?i)\b(?:các\s+chuyên gia(?:\s+hàng đầu|\s+trong ngành)?(?:\s+đều)?\s+(?:cho rằng|nhận định rằng|khẳng định rằng)|nhiều\s+nghiên cứu(?:\s+khoa học)?(?:\s+đã)?\s+(?:chỉ ra|cho thấy)\s+rằng|báo cáo\s+ngành\s+chỉ ra\s+rằng)\b",
            Severity.WARNING, 0.65,
            "general|audit_report|academic|legal|translation",
            "1/para;2/1000w", "followed_by_citation",
            "Nhiều nghiên cứu đã chỉ ra rằng việc chậm thanh toán công nợ quá 30 ngày làm giảm 12% điểm tín dụng doanh nghiệp.",
            "Việc chậm thanh toán công nợ quá 30 ngày làm giảm 12% điểm tín dụng doanh nghiệp.",
            "https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing", "strong",
        ),
        # =====================================================================
        # NHÓM 3: AI_STRUCTURAL_AND_FORMATTING (5 quy tắc)
        # =====================================================================
        (
            "VIS-FMT-001", "AI_STRUCTURAL_AND_FORMATTING", "statistical_structural",
            "Danh sách từ 3 mục liên tiếp trở lên mở đầu bằng '**Nhãn in đậm:**' rồi giải thích lặp khuôn.",
            "ALGO:BOLD_COLON_LIST_STREAK_MIN_3",
            Severity.WARNING, 0.6,
            "general|audit_report|academic|legal|social_media|translation",
            "1/doc", "legal_glossary_definition",
            "- **Bảo mật dữ liệu:** Bảo mật dữ liệu được nâng cao nhờ mã hóa AES-256.\n- **Tốc độ xử lý:** Tốc độ xử lý tăng 20%.\n- **Chi phí vận hành:** Chi phí vận hành giảm 10%.",
            "Bản cập nhật áp dụng mã hóa AES-256, tăng 20% tốc độ xử lý và giảm 10% chi phí vận hành.",
            "https://github.com/blader/humanizer/blob/main/SKILL.md", "strong",
        ),
        (
            "VIS-FMT-002", "AI_STRUCTURAL_AND_FORMATTING", "dictionary_statistical",
            "Đặt quá nhiều từ nối sách vở ở đầu câu ('Hơn nữa,', 'Thêm vào đó,', 'Bên cạnh đó,', 'Ngoài ra,', 'Mặt khác,').",
            r"(?i)(?:^|[.!?]\s+)(?:hơn nữa|thêm vào đó|bên cạnh đó|ngoài ra|mặt khác|đồng thời|theo đó|qua đó|từ đó),\s+",
            Severity.WARNING, 0.55,
            "general|audit_report|academic|legal|marketing|social_media|translation",
            "3/para;8/1000w", "none",
            "Doanh thu quý I tăng 5%. Hơn nữa, chi phí bán hàng giảm 2%. Thêm vào đó, tỷ lệ khách hàng quay lại đạt 60%. Bên cạnh đó, công ty đã mở thêm 3 chi nhánh.",
            "Trong quý I, doanh thu tăng 5%, chi phí bán hàng giảm 2%, tỷ lệ khách quay lại đạt 60% và công ty mở thêm 3 chi nhánh.",
            "https://arxiv.org/abs/2406.07016", "strong",
        ),
        (
            "VIS-FMT-003", "AI_STRUCTURAL_AND_FORMATTING", "statistical_regex",
            "Lạm dụng dấu gạch ngang dài ('—') nối mệnh đề kiểu tiếng Anh thay vì dùng dấu phẩy hoặc ngoặc đơn.",
            r"[^\s—]—[^\s—]|\s—\s",
            Severity.INFO, 0.35,
            "general|audit_report|academic|legal|translation",
            "2/para;5/1000w", "literary_dialogue_lines",
            "Dự án này—vốn được phê duyệt từ tháng 3/2025—đã vượt tiến độ 12 ngày—một kết quả đáng ghi nhận.",
            "Dự án này (được phê duyệt từ tháng 3/2025) đã vượt tiến độ 12 ngày.",
            "https://github.com/blader/humanizer/blob/main/SKILL.md", "medium",
        ),
        (
            "VIS-FMT-004", "AI_STRUCTURAL_AND_FORMATTING", "regex",
            "Ghép 3 tính từ hoặc động từ khen ngợi theo nhịp văn mẫu ('nhanh chóng, chính xác và hiệu quả').",
            r"(?i)\b(?:nhanh chóng,\s*chính xác\s*và\s*hiệu quả|sáng tạo,\s*đột phá\s*và\s*bền vững|toàn diện,\s*sâu sắc\s*và\s*triệt để|linh hoạt,\s*minh bạch\s*và\s*tối ưu)\b",
            Severity.INFO, 0.4,
            "general|audit_report|academic|legal|translation",
            "1/para;3/1000w", "profile:marketing",
            "Quy trình đối soát hóa đơn mới giúp xử lý dữ liệu nhanh chóng, chính xác và hiệu quả cho 1.200 giao dịch mỗi ngày.",
            "Quy trình đối soát hóa đơn mới xử lý 1.200 giao dịch mỗi ngày.",
            "https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing", "medium",
        ),
        (
            "VIS-FMT-005", "AI_STRUCTURAL_AND_FORMATTING", "statistical_nlp",
            "Các đoạn văn liên tiếp dài bằng nhau như đúc khuôn (CV < 0,15 trên >= 4 đoạn) hoặc 3 câu liền nhau mở đầu cùng một từ.",
            "ALGO:PARAGRAPH_CV_AND_OPENING_MONOTONY",
            Severity.INFO, 0.3,
            "general|academic|marketing|translation",
            "CV<0.15/4paras", "profile:legal|profile:audit_report",
            "Đoạn 1 dài 20 từ.\n\nĐoạn 2 dài 20 từ.\n\nĐoạn 3 dài 20 từ.\n\nĐoạn 4 dài 20 từ.",
            "Gộp hoặc tách đoạn theo mạch ý thực tế thay vì chia đều số câu mỗi đoạn.",
            "https://arxiv.org/abs/2405.03206", "weak",
        ),
        # =====================================================================
        # NHÓM 4: TRANSLATIONESE_EN_VI (5 quy tắc)
        # =====================================================================
        (
            "VIS-TRANS-001", "TRANSLATIONESE_EN_VI", "regex",
            "Câu bị động dịch sát từ tiếng Anh 'được/bị + động từ + bởi + chủ thể'.",
            r"(?i)\b(?:được|bị)\s+[a-zà-ỹđ]+(?:\s+[a-zà-ỹđ]+){0,2}\s+bởi\s+(?:các|những|một|nhiều|mọi|chính|ông|bà|anh|chị|nhóm|đội ngũ|công ty|tổ chức|hội đồng|ban|phòng|đơn vị|người|khách hàng|nhà\s+nghiên cứu|chuyên gia|hệ thống|phần mềm|tham số)\b",
            Severity.WARNING, 0.75,
            "general|audit_report|academic|legal|marketing|social_media|translation",
            "1/para;2/1000w", "mathematical_formula_definition",
            "Báo cáo tài chính năm 2025 đã được phê duyệt bởi hội đồng quản trị vào ngày 10/01/2026.",
            "Hội đồng quản trị đã phê duyệt báo cáo tài chính năm 2025 vào ngày 10/01/2026.",
            "https://vi.wikipedia.org/wiki/Cao_Xu%C3%A2n_H%E1%BA%A1o", "strong",
        ),
        (
            "VIS-TRANS-002", "TRANSLATIONESE_EN_VI", "dictionary_statistical",
            "Lặp dày chữ 'được' trước động từ trung tính ('được thực hiện', 'được sử dụng', 'được tiến hành') làm câu nặng nề.",
            r"(?i)\bđược\s+(?:thực hiện|sử dụng|tiến hành|áp dụng|xem là|coi là|cho là|ghi nhận|thiết kế|xây dựng|phát triển|thu thập|gửi)\b",
            Severity.WARNING, 0.55,
            "general|marketing|social_media|translation",
            "3/para;10/1000w", "profile:legal|profile:audit_report|profile:academic",
            "Phương pháp này được sử dụng để đo độ trễ trên 50 máy chủ, thử nghiệm được tiến hành tự động và kết quả được ghi nhận vào nhật ký.",
            "Nhóm kỹ thuật dùng phương pháp này để đo độ trễ trên 50 máy chủ, chạy thử nghiệm tự động và ghi kết quả vào nhật ký.",
            "https://journal.hcmue.edu.vn/index.php/hcmuejos/article/download/2116/2100/2115", "strong",
        ),
        (
            "VIS-TRANS-003", "TRANSLATIONESE_EN_VI", "regex",
            "Biến động từ thành cụm danh từ dịch sát 'sự/việc + động từ + của + chủ thể'.",
            r"(?i)\b(?:sự|việc|quá trình)\s+(?:tăng trưởng|sụt giảm|thay đổi|phát triển|cải thiện|tham gia|xuất hiện|thực hiện|triển khai|hoàn thành|kiểm tra|đối chiếu|đối soát|chuyển đổi|xử lý|chậm trễ|thiếu hụt)\s+của\s+(?:các|những|một|nhiều|hệ thống|công ty|doanh nghiệp|ngân hàng|khách hàng|thị trường|dự án|nhân viên|người dùng|đơn vị|bộ phận)\b",
            Severity.WARNING, 0.65,
            "general|audit_report|marketing|social_media|translation",
            "2/para;5/1000w", "profile:legal",
            "Sự sụt giảm của thị trường bất động sản trong quý II đã dẫn đến việc thay đổi của dự án giải ngân.",
            "Vì thị trường bất động sản quý II sụt giảm, ngân hàng đã điều chỉnh dự án giải ngân.",
            "http://luanan.nlv.gov.vn/luanan?a=d&d=TTbFqWrAWCgC2003.1.6", "strong",
        ),
        (
            "VIS-TRANS-004", "TRANSLATIONESE_EN_VI", "regex",
            "Lặp cụm 'một cách + tính từ' dịch từ trạng từ đuôi '-ly' của tiếng Anh.",
            r"(?i)\bmột\s+cách\s+(?:đáng kể|nhanh chóng|hiệu quả|rõ rệt|rõ ràng|tích cực|tiêu cực|toàn diện|triệt để|nghiêm trọng|mạnh mẽ|sâu sắc|tự nhiên|dễ dàng|chính xác|tự động|độc lập|linh hoạt|tối ưu)\b",
            Severity.INFO, 0.45,
            "general|audit_report|academic|legal|marketing|social_media|translation",
            "2/para;4/1000w", "single_occurrence_allowed",
            "Chi phí nguyên vật liệu đã tăng một cách đáng kể (22%), ảnh hưởng một cách nghiêm trọng đến biên lợi nhuận ròng.",
            "Chi phí nguyên vật liệu tăng mạnh (22%), làm giảm biên lợi nhuận ròng.",
            "https://vi.wikipedia.org/wiki/Cao_Xu%C3%A2n_H%E1%BA%A1o", "medium",
        ),
        (
            "VIS-TRANS-005", "TRANSLATIONESE_EN_VI", "regex",
            "Chủ ngữ giả ('Nó là... để', 'Có một sự... trong việc'), đại từ quan hệ dịch thô ('nơi mà', 'điều mà'), câu cụt chủ ngữ hoặc gán tâm lý người cho vật vô tri.",
            r"(?i)(?:\bnó\s+(?:thì\s+)?là\s+(?:rất\s+|khá\s+|cực kỳ\s+|vô cùng\s+)?(?:quan trọng|cần thiết|bắt buộc|khó khăn|dễ dàng|hữu ích|tốt hơn)\s+(?:cho\s+\S+\s+)?để\s+|\bcó\s+một\s+sự\s+(?:gia tăng|sụt giảm|thay đổi|khác biệt|chậm trễ)\s+(?:lớn\s+|đáng kể\s+)?trong\s+việc\b|(?:[—–-]\s*nơi(?:\s+mà)?\b|,\s*(?:nơi mà|điều mà|cái mà|người mà|việc mà)\b)|^\s*(?:đúc kết từ|dẫn đến việc|xuất phát từ việc)\s+[^.!?\n]{5,60}|\b(?:phép cộng|phép tính|báo cáo|bảng dữ liệu|bảng tính|con số|dòng tổng|biểu đồ)\s+(?:[a-zà-ỹđ]+\s+){0,3}(?:vô tình|kết luận nhầm|tưởng nhầm|quên mất|chủ quan|bỏ quên|hiểu lầm)\b)",
            Severity.WARNING, 0.8,
            "general|audit_report|academic|legal|marketing|social_media|translation",
            "1/doc", "none",
            "Nó là rất cần thiết để kiểm tra lại toàn bộ 150 hợp đồng vì có một sự chậm trễ đáng kể trong việc bàn giao mặt bằng.",
            "Cần kiểm tra lại toàn bộ 150 hợp đồng vì tiến độ bàn giao mặt bằng đang chậm trễ đáng kể.",
            "https://vi.wikipedia.org/wiki/Cao_Xu%C3%A2n_H%E1%BA%A1o", "strong",
        ),
        # =====================================================================
        # NHÓM 5: BUREAUCRATIC_AND_SEO_CLICHE (5 quy tắc)
        # =====================================================================
        (
            "VIS-CLICHE-001", "BUREAUCRATIC_AND_SEO_CLICHE", "regex",
            "Khẩu hiệu hành chính hoặc kiến nghị chung chung thiếu chủ thể và đầu ra cụ thể.",
            r"(?i)\b(?:đẩy mạnh\s+công tác\s+tuyên truyền|tăng cường\s+hơn nữa\s+công tác\s+quản lý|triển khai\s+đồng bộ\s+và\s+quyết liệt\s+các\s+giải pháp|nâng cao\s+nhận thức\s+và\s+trách nhiệm\s+của\s+các\s+cấp|cần\s+đẩy nhanh\s+tiến độ\s+thực hiện|cần\s+quan tâm\s+chỉ đạo\s+sâu sát|không\s+lượng hóa\s+được)\b",
            Severity.INFO, 0.5,
            "general|audit_report|academic|marketing|social_media|translation",
            "1/para;2/1000w", "profile:legal|direct_quote",
            "Để giảm tỷ lệ lỗi sản phẩm xuống dưới 1%, nhà máy cần đẩy mạnh công tác tuyên truyền và triển khai đồng bộ và quyết liệt các giải pháp kỹ thuật.",
            "Để giảm tỷ lệ lỗi sản phẩm xuống dưới 1%, nhà máy cần đào tạo lại quy trình vận hành máy CNC và kiểm tra chất lượng đầu ra theo ca.",
            "https://thuvienphapluat.vn/van-ban/Bo-may-hanh-chinh/Nghi-dinh-30-2020-ND-CP-cong-tac-van-thu-436532.aspx", "strong",
        ),
        (
            "VIS-CLICHE-002", "BUREAUCRATIC_AND_SEO_CLICHE", "regex",
            "Né động từ 'là', 'có' hoặc chèn động từ rỗng ('đóng vai trò như là một', 'sở hữu tính năng vượt trội', 'tiến hành việc').",
            r"(?i)\b(?:đóng\s+vai trò\s+như\s+là\s+một|hoạt động\s+với\s+tư cách\s+là\s+một|được\s+biết\s+đến\s+như\s+là\s+một(?:\s+trong\s+những)?|sở hữu\s+(?:những\s+|các\s+)?(?:tính năng|ưu điểm)\s+vượt trội|(?:tiến hành|thực hiện)\s+việc\s+(?:kiểm tra|đối chiếu|đối soát|so sánh|rà soát|xử lý|đánh giá|xác nhận|lưu lại))\b",
            Severity.INFO, 0.45,
            "general|audit_report|academic|legal|translation",
            "1/para;3/1000w", "legal_commercial_agency",
            "Module thanh toán này hoạt động với tư cách là một cổng trung gian và sở hữu những tính năng vượt trội giúp xử lý 500 giao dịch/giây.",
            "Module thanh toán này là cổng trung gian xử lý 500 giao dịch/giây.",
            "https://github.com/blader/humanizer/blob/main/SKILL.md", "medium",
        ),
        (
            "VIS-CLICHE-003", "BUREAUCRATIC_AND_SEO_CLICHE", "dictionary",
            "Ghép thừa hai từ trùng nghĩa ('hoàn toàn tuyệt đối', 'tương lai sắp tới', 'nguyên nhân chính cốt lõi', 'kết quả cuối cùng đạt được').",
            r"(?i)\b(?:hoàn toàn\s+tuyệt đối|tương lai\s+sắp tới|nguyên nhân\s+chính\s+cốt lõi|kết quả\s+cuối cùng\s+đạt được|tối ưu(?:\s+hóa)?\s+tốt nhất|kế hoạch\s+dự kiến\s+sắp tới|phối hợp\s+cùng\s+nhau|cải thiện\s+tốt hơn)\b",
            Severity.INFO, 0.4,
            "general|audit_report|academic|legal|marketing|social_media|translation",
            "1/para;2/1000w", "none",
            "Nguyên nhân chính cốt lõi khiến dự án chậm 14 ngày là do nhà thầu phụ chưa bàn giao bản vẽ trong tương lai sắp tới.",
            "Nguyên nhân cốt lõi khiến dự án chậm 14 ngày là do nhà thầu phụ chưa bàn giao bản vẽ.",
            "https://github.com/btford/write-good", "medium",
        ),
        (
            "VIS-CLICHE-004", "BUREAUCRATIC_AND_SEO_CLICHE", "regex",
            "Mở bài câu khách kiểu SEO hoặc câu chốt giật gân một dòng ('Bạn đã bao giờ tự hỏi', 'Tất tần tật những điều bạn cần biết', 'Hãy đọc lại câu này').",
            r"(?i)\b(?:bạn\s+đã\s+bao giờ\s+tự\s+hỏi|tất tần tật\s+những\s+(?:điều|gì)\s+bạn\s+cần\s+biết(?:\s+về)?|bí quyết\s+không\s+thể\s+bỏ\s+qua(?:\s+để)?|hãy\s+nghĩ\s+mà\s+xem|hãy\s+đọc\s+lại\s+câu\s+này)\b",
            Severity.WARNING, 0.6,
            "general|audit_report|academic|legal|translation",
            "1/doc", "profile:marketing|profile:social_media",
            "Bạn đã bao giờ tự hỏi làm thế nào để kiểm toán hàng tồn kho? Dưới đây là tất tần tật những điều bạn cần biết về quy trình kiểm kê theo chuẩn VAS 02.",
            "Tài liệu này hướng dẫn quy trình kiểm kê hàng tồn kho theo chuẩn mực kế toán VAS 02.",
            "https://github.com/blader/humanizer/blob/main/SKILL.md", "strong",
        ),
        (
            "VIS-CLICHE-005", "BUREAUCRATIC_AND_SEO_CLICHE", "regex",
            "Ghép chồng nhiều từ rào đón làm câu mơ hồ ('có thể có khả năng sẽ', 'dường như có vẻ như là').",
            r"(?i)\b(?:có thể\s+có\s+khả năng\s+(?:sẽ|là)|dường như\s+có\s+vẻ\s+(?:như\s+)?là|ở\s+một\s+(?:góc độ|mức độ)\s+nhất định\s+nào\s+đó\s+có thể(?:\s+được\s+xem\s+là)?)\b",
            Severity.WARNING, 0.55,
            "general|audit_report|academic|legal|marketing|social_media|translation",
            "1/para;2/1000w", "none",
            "Khoản phải thu 3,2 tỷ đồng này dường như có vẻ như là có thể có khả năng sẽ trở thành nợ xấu trong quý IV.",
            "Khoản phải thu 3,2 tỷ đồng này có thể trở thành nợ xấu trong quý IV.",
            "https://github.com/blader/humanizer/blob/main/SKILL.md", "strong",
        ),
        # =====================================================================
        # NHÓM 6: VOICE_AND_STRUCTURE (5 quy tắc thực chiến từ lịch sử biên tập)
        # =====================================================================
        (
            "VIS-LEX-001", "VOICE_AND_STRUCTURE", "regex",
            "Dùng sai nghĩa từ Hán - Việt ('thực chứng', 'nhận thức luận') hoặc tự chế từ trái cách gọi thực tế khi đi làm.",
            r"(?i)\b(?:góc nhìn\s+thực chứng|hồ sơ\s+(?:dự án\s+)?thực chứng|ngôn ngữ\s+[^,.;:!?\n]{0,20}thực chứng|bằng chứng\s+thực chứng|kiểm toán\s+thực chứng|phản biện\s+thực chứng|nhận thức luận|mục tra cứu\s+nguyên tử|đơn vị\s+nguyên tử|in đúp|chép\s+(?:thiếu|thừa)\s+tiền|bản chốt sổ\s+cố định|tài liệu\s+trượt|khớp\s+(?:nhau\s+|tới\s+)?từng đồng|bỏ sót\s+sạch|vừa khít\s+bù|(?:dùng|cho)\s+máy(?:\s+tính)?\s+(?:đối chiếu|ghép)|máy tính\s+sẽ\s+trừ|kiểm tra\s+tự động\s+đối soát|điều gì\s+vẫn\s+có thể\s+sai|dấu ấn\s+công việc|điểm cốt lõi\s+vận hành|đọc nhanh\s+trước khi\s+vào)\b",
            Severity.WARNING, 0.7,
            "general|audit_report|academic|marketing|social_media|translation",
            "1/doc", "philosophy_positivism_term",
            "Hồ sơ dự án thực chứng này dùng máy tính đối chiếu để bắt lỗi in đúp và kiểm tra tự động đối soát 100% giao dịch.",
            "Hồ sơ dự án dựa trên bằng chứng này chạy đối soát tự động 100% giao dịch để phát hiện dòng bị lặp.",
            "https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing", "strong",
        ),
        (
            "VIS-LEX-002", "VOICE_AND_STRUCTURE", "morphological_lexical",
            "Dịch ngược từ tiếng Anh đã quen dùng ('thư điện tử', 'yêu cầu kéo') hoặc chêm từ tiếng Anh chuyên ngành chưa Việt hóa.",
            "ALGO:LOANWORD_AND_FOREIGN_TOKEN_CHECK",
            Severity.INFO, 0.45,
            "general|audit_report|social_media|translation",
            "1/doc", "naturalized_loanwords_allowlist",
            "Nhóm vận hành gửi thư điện tử xin thực hiện cutover và dùng workaround cho các blocker còn tồn đọng.",
            "Nhóm vận hành gửi email xin chuyển đổi sang hệ thống mới và dùng cách xử lý tạm thời cho các lỗi chặn đứng còn tồn đọng.",
            "https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing", "medium",
        ),
        (
            "VIS-TONE-001", "VOICE_AND_STRUCTURE", "regex",
            "Lệch giọng văn trang trọng: chào sồn sã, dùng khẩu ngữ/kịch tính hóa, tự khoe xếp loại hoặc khen xã giao dư thừa.",
            r"(?i)(?:(?:^|[.!?]\s+)(?:anh|chị|sếp)\s+[a-zà-ỹđ]+\s+ơi\s*[,!]|\b(?:rủi ro\s+sát sườn|cố\s+bấm nút|cố đấm\s+ăn xôi|nhắm mắt\s+đưa chân|vỡ trận|vỡ trần|tê liệt\s+hoàn toàn|tử huyệt|quả bom\s+nổ chậm|gót chân\s+achilles|chữa cháy\s+tạm thời|vá víu|đắp chiếu|cưỡi ngựa\s+xem hoa|đánh trống\s+bỏ dùi|làm cho có|tốt nghiệp\s+loại giỏi|xếp loại\s+very good|ghi nhận\s+(?:sự\s+)?(?:nỗ lực|cố gắng)\s+(?:rất lớn|đáng kể|không ngừng)\s+của)\b)",
            Severity.WARNING, 0.65,
            "audit_report|academic|legal",
            "1/doc", "none",
            "Anh Minh ơi, nếu vẫn cố bấm nút vận hành thì doanh nghiệp sẽ đối mặt rủi ro sát sườn làm tê liệt hoàn toàn hệ thống.",
            "Kính gửi anh Minh, nếu đưa hệ thống vào vận hành khi chưa đủ điều kiện, doanh nghiệp có nguy cơ gián đoạn giao dịch trên diện rộng.",
            "https://thuvienphapluat.vn/van-ban/Bo-may-hanh-chinh/Nghi-dinh-30-2020-ND-CP-cong-tac-van-thu-436532.aspx", "strong",
        ),
        (
            "VIS-STRUCT-001", "VOICE_AND_STRUCTURE", "regex",
            "Tự thuyết minh bố cục bài viết, để lộ nhãn khung dàn ý nội bộ hoặc vặn câu tuần tự để né máy quét.",
            r"(?i)(?:\b(?:để tránh\s+trùng lặp|tách biệt\s+với\s+mục|khác với\s+mục\s+\d|mục này\s+được\s+thiết kế|được\s+trình bày\s+theo\s+cấu trúc|(?:bảng|sơ đồ|nội dung)\s+dưới đây\s+(?:sẽ\s+)?(?:trình bày|mô tả|tổng hợp|minh họa)|vướng mắc\s+ở\s+cách\s+\d+|chuyển sang\s+cách\s+\d+|điểm\s+bị\s+kẹt|điểm\s+gãy\s+cụ thể|bước ngoặt\s+tư duy|ví dụ\s+nhẩm tay|câu hỏi\s+vặn ngược|phản xạ\s+bản năng|câu hỏi\s+gỡ rối|biểu hiện\s+bề mặt|nguyên nhân\s+gốc\s+ở\s+tầm\s+cơ chế|hồ sơ\s+thứ nhất[^.!?\n]{3,80}sang\s+hồ sơ\s+thứ hai)\b|^\s*(?:điểm nghẽn|hướng xử lý|bài học rút ra|yêu cầu kiểm soát|căn cứ thực tế)\s*:)",
            Severity.WARNING, 0.65,
            "general|audit_report|academic|social_media",
            "1/doc", "none",
            "Để tránh trùng lặp với mục trước, bảng dưới đây sẽ trình bày chi tiết 3 rủi ro thanh khoản.",
            "Phần này đối chiếu trực tiếp 3 rủi ro thanh khoản trong quý IV.",
            "https://github.com/blader/humanizer/blob/main/SKILL.md", "strong",
        ),
        (
            "VIS-STRUCT-002", "VOICE_AND_STRUCTURE", "structural_hygiene",
            "Lỗi trình bày tiêu đề (Title Case kiểu Anh, mục con đơn độc), ký tự ẩn, mũi tên ASCII hoặc sai lệch bảng số liệu.",
            "ALGO:DOCUMENT_AND_TABLE_HYGIENE",
            Severity.WARNING, 0.6,
            "general|audit_report|academic|legal|marketing|social_media|translation",
            "1/doc", "code_block",
            "### Hồ Sơ Dự Án Chọn Lọc\nTỷ lệ đạt 59,9% -> Thiếu -40,1%.",
            "### Hồ sơ dự án chọn lọc\nTỷ lệ đạt 59,9%, còn thiếu 40,1%.",
            "https://github.com/vale-cli/vale", "strong",
        ),
    ]

    catalog: list[RuleDefinition] = []
    for item in raw_rules:
        (
            rid, cat, ptype, desc, pat, sev, weight,
            prof_str, thresh_str, exc_str, bad_ex, bet_ex, url, strength,
        ) = item
        profs = frozenset(Profile(p) for p in prof_str.split("|"))
        thresh = ThresholdSpec.parse(thresh_str)
        excs = tuple(e for e in exc_str.split("|") if e != "none")
        catalog.append(
            RuleDefinition(
                rule_id=rid,
                category=cat,
                pattern_type=ptype,
                description_vi=desc,
                regex_or_algorithm=pat,
                severity=sev,
                weight=weight,
                profiles=profs,
                threshold=thresh,
                exceptions=excs,
                bad_example=bad_ex,
                better_example=bet_ex,
                source_url=url,
                evidence_strength=strength,
            )
        )
    return catalog


class ViScanner:
    """Máy quét câu chữ tiếng Việt v2.0.0.
    Mặc định `profile="all"` chạy và xuất đủ 100% tín hiệu của cả 7 nhóm văn bản.
    """

    VERSION = VERSION
    SCHEMA_VERSION = SCHEMA_VERSION
    DISCLAIMER = (
        "Công cụ vi_scanner chỉ chỉ ra các vị trí câu chữ máy móc, sáo rỗng hoặc "
        "dịch sát cần người viết đọc lại. Kết quả này KHÔNG suy đoán tác giả và "
        "KHÔNG kết luận văn bản do AI tạo ra."
    )

    _VI_DIACRITIC_RE = stdlib_re.compile(
        r"[àáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ"
        r"ÀÁẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬÈÉẺẼẸÊẾỀỂỄỆÌÍỈĨỊÒÓỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÙÚỦŨỤƯỨỪỬỮỰỲÝỶỸỴĐ]"
    )
    _REVERSE_LOANWORD_RE = stdlib_re.compile(
        r"(?i)\b(?:thư\s+điện\s+tử|yêu\s+cầu\s+kéo|kho\s+mã\s+nguồn|mạng\s+toàn\s+cầu|trình\s+duyệt\s+mạng)\b"
    )
    _RAW_TECH_ID_RE = stdlib_re.compile(
        r"\b(?:[A-Z]{2,}(?:_[A-Z0-9]{2,})+|[A-Z]{2,}(?:\.[A-Z0-9]{2,}){2,})\b"
        r"|\b(?:INNER\s+JOIN|LEFT\s+JOIN|FULL\s+OUTER\s+JOIN|COALESCE|VLOOKUP|GROUP\s+BY)\b"
        r"|\b(?:COUNT|SUM|ABS)\s*\("
    )
    _LOWER_ASCII_WORD_RE = stdlib_re.compile(r"(?<![A-Za-z0-9_./-])[a-z]{4,25}(?![A-Za-z0-9_./-])")
    _EN_PHONOTACTIC_RE = stdlib_re.compile(
        r"(?:[fjwz]"
        r"|^(?:bl|br|cl|cr|dr|fl|fr|gl|gr|pl|pr|sc|sk|sl|sm|sn|sp|st|sw|tw|wr)"
        r"|(?:ck|ct|ft|ld|lp|lt|mp|nd|nk|nt|pt|rd|rk|rt|sh|sk|sp|st|xt)$"
        r"|(?:tion|sion|ment|ness|able|ible|ship|line|back|over|down|flow|work|book|list|test|load|lock|scan)$)"
    )
    _BOLD_COLON_BULLET_RE = stdlib_re.compile(
        r"^\s*(?:[-*•◦–]|\d+[.)])\s+(?:\*\*[^*\n]{2,65}?:\*\*|\*\*[^*\n]{2,65}?\*\*\s*:)"
    )
    _BRIDGE_NEGATION_RE = stdlib_re.compile(
        r"(?i)\b(?:chưa\s+đồng nghĩa\s+với|không\s+đồng nghĩa\s+với|không\s+có\s+nghĩa\s+là|không\s+phải\s+là\s+hai\s+cực\s+đối\s+lập)\b"
    )

    def __init__(
        self,
        rules: list[RuleDefinition] | None = None,
        extra_rules: list[RuleDefinition] | None = None,
    ) -> None:
        merged = list(rules or build_default_rules())
        if extra_rules:
            merged.extend(extra_rules)
        self.rules: dict[str, RuleDefinition] = {
            r.rule_id: r for r in merged if r.status == "active"
        }
        self._compiled: dict[str, Any] = {}
        for rid, rule in self.rules.items():
            if not rule.regex_or_algorithm.startswith("ALGO:"):
                self._compiled[rid] = regex_engine.compile(
                    rule.regex_or_algorithm, regex_engine.MULTILINE
                )

    @classmethod
    def load_custom_rules(cls, path: Path) -> list[RuleDefinition]:
        raw_data = json.loads(path.read_text(encoding="utf-8-sig"))
        items = raw_data if isinstance(raw_data, list) else raw_data.get("rules", [])
        out: list[RuleDefinition] = []
        for idx, entry in enumerate(items, 1):
            profs_raw = entry.get("profiles")
            profs = (
                frozenset(Profile(p) for p in profs_raw)
                if profs_raw
                else frozenset(ALL_PROFILES)
            )
            out.append(
                RuleDefinition(
                    rule_id=str(entry.get("rule_id") or f"CUSTOM-{idx:03d}"),
                    category=str(entry.get("category") or "CUSTOM"),
                    pattern_type="regex",
                    description_vi=str(entry["description_vi"]),
                    regex_or_algorithm=str(entry["regex"]),
                    severity=Severity(entry.get("severity", "warning")),
                    weight=float(entry.get("weight", 0.6)),
                    profiles=profs,
                    threshold=ThresholdSpec.parse(str(entry.get("threshold", "1/doc"))),
                    exceptions=(),
                    bad_example=str(entry.get("bad_example", "")),
                    better_example=str(entry.get("better_example", "")),
                    source_url=str(entry.get("source_url", "custom")),
                    evidence_strength=str(entry.get("evidence_strength", "custom")),
                )
            )
        return out

    @staticmethod
    def _offset_to_line_col(text: str, offset: int) -> tuple[int, int]:
        line = text.count("\n", 0, offset) + 1
        last_nl = text.rfind("\n", 0, offset)
        col = (offset + 1) if last_nl == -1 else (offset - last_nl)
        return line, col

    @staticmethod
    def _context_at(text: str, start: int, end: int, radius: int = 65) -> str:
        s = max(0, start - radius)
        e = min(len(text), end + radius)
        return " ".join(text[s:e].replace("\n", " ").split())

    @staticmethod
    def _paragraph_spans(text: str) -> list[tuple[int, int, str]]:
        spans: list[tuple[int, int, str]] = []
        pos = 0
        for m in stdlib_re.finditer(r"\n\s*\n", text):
            chunk = text[pos : m.start()]
            if chunk.strip():
                spans.append((pos, m.start(), chunk))
            pos = m.end()
        tail = text[pos:]
        if tail.strip():
            spans.append((pos, len(text), tail))
        return spans

    @staticmethod
    def _sentence_around(text: str, start: int, end: int) -> str:
        left = max(text.rfind(".", 0, start), text.rfind("\n", 0, start))
        right_dot = text.find(".", end)
        right_nl = text.find("\n", end)
        candidates = [x for x in (right_dot, right_nl) if x != -1]
        right = min(candidates) if candidates else len(text)
        return text[left + 1 : right]

    def _is_linguistically_exempt(
        self, rule_id: str, target_text: str, start: int, end: int
    ) -> bool:
        """Các trường hợp miễn trừ về mặt ngôn ngữ học phổ quát (không gắn tên riêng dự án)."""
        sent = self._sentence_around(target_text, start, end)
        matched = target_text[start:end]

        if rule_id == "VIS-AI-003":
            if (
                stdlib_re.search(r"\b(?:19|20)\d{2}\b", sent)
                and stdlib_re.search(r"\b\d+(?:[.,]\d+)?%", sent)
                and not stdlib_re.search(r"(?i)ngày càng\s+(?:phát triển|biến đổi)", matched)
            ):
                return True
        elif rule_id == "VIS-RHET-002":
            if stdlib_re.search(r"\b1\d{3}\b", sent):
                return True
        elif rule_id == "VIS-RHET-003":
            if stdlib_re.search(
                r"(?i)(?:\b\d+\s*(?:m|km|cm|mm|hải lý)\b|\bthế kỷ\s+[ivx]+\b|\b(?:tàu thuyền|hàng hải|mực nước biển|dệt|tơ tằm|khung cửi)\b)",
                sent,
            ):
                return True
        elif rule_id == "VIS-RHET-004":
            if stdlib_re.match(
                r"(?i)^từ\s+(?:ngày|tháng|năm|quý|đợt|lần|mức|khoảng|số|\d+)",
                matched.strip(),
            ):
                return True
        elif rule_id == "VIS-RHET-005":
            tail = target_text[end : end + 45]
            if stdlib_re.match(r"^\s*(?:\(|\[|theo\s+[A-ZÀ-ỸĐ])", tail):
                return True
        elif rule_id == "VIS-TRANS-001":
            if stdlib_re.search(r"(?i)\bđược\s+xác định\s+bởi\s+công thức\b", sent):
                return True
        elif rule_id == "VIS-LEX-001":
            if stdlib_re.search(r"(?i)\b(?:chủ nghĩa|triết học|trường phái)\s+thực chứng\b", sent):
                return True
        return False

    def _is_profile_exempt(
        self, rule_id: str, target_text: str, start: int, end: int, prof: Profile | None
    ) -> bool:
        """Miễn trừ riêng theo từng nhóm văn bản cụ thể (chỉ lọc khi người dùng truyền `--profile` đơn lẻ)."""
        if prof is None:
            return False
        sent = self._sentence_around(target_text, start, end)
        if rule_id == "VIS-RHET-001" and prof == Profile.LEGAL:
            if stdlib_re.search(
                r"(?i)\b(?:điều|khoản|mục|chương|nghị định|thông tư|luật|bộ luật|hợp đồng)\s+(?:số\s+)?\d+",
                sent,
            ):
                return True
        if rule_id == "VIS-FMT-001" and prof == Profile.LEGAL:
            if stdlib_re.search(r"(?i)\b(?:giải thích từ ngữ|bên a|bên b)\b", target_text):
                return True
        if rule_id == "VIS-CLICHE-002" and prof == Profile.LEGAL:
            if stdlib_re.search(
                r"(?i)\b(?:luật\s+thương mại|bộ luật\s+dân sự|đại lý\s+thương mại|ủy thác)\b",
                sent,
            ):
                return True
        return False

    def _make_finding(
        self,
        rule: RuleDefinition,
        raw_text: str,
        offset: int,
        matched_text: str,
        custom_suggestion: str | None = None,
        override_profiles: list[str] | None = None,
    ) -> Finding:
        line, col = self._offset_to_line_col(raw_text, offset)
        end = min(len(raw_text), offset + max(1, len(matched_text)))
        suggestion = custom_suggestion or (
            f"Viết gọn và trực tiếp hơn (ví dụ: '{rule.better_example}')"
            if rule.better_example
            else rule.description_vi
        )
        app_profs = override_profiles or [p.value for p in ALL_PROFILES if p in rule.profiles]
        ex_profs = [p.value for p in ALL_PROFILES if p.value not in app_profs]
        return Finding(
            rule_id=rule.rule_id,
            category=rule.category,
            severity=rule.severity.value,
            weight=rule.weight,
            line=line,
            col=col,
            matched_text=matched_text[:120],
            context=self._context_at(raw_text, offset, end),
            description_vi=rule.description_vi,
            suggestion_vi=suggestion,
            applicable_profiles=app_profs,
            exempt_profiles=ex_profs,
            evidence_strength=rule.evidence_strength,
        )

    def _run_bold_colon_list_rule(
        self, rule: RuleDefinition, raw_text: str, masked_prose: str, prof: Profile | None
    ) -> list[Finding]:
        if self._is_profile_exempt(rule.rule_id, masked_prose, 0, len(masked_prose), prof):
            return []
        lines = masked_prose.splitlines(keepends=True)
        streak = 0
        streak_start_offset = 0
        offset = 0
        for ln in lines:
            stripped = ln.strip()
            if not stripped:
                offset += len(ln)
                continue
            if self._BOLD_COLON_BULLET_RE.match(ln):
                if streak == 0:
                    streak_start_offset = offset
                streak += 1
                if streak == 3:
                    sample = raw_text[streak_start_offset : offset + len(ln)].strip().splitlines()[0]
                    return [
                        self._make_finding(
                            rule,
                            raw_text,
                            streak_start_offset,
                            sample,
                            "Bỏ nhãn in đậm đầu dòng và viết thành câu hoàn chỉnh mở đầu bằng chủ ngữ cụ thể.",
                        )
                    ]
            else:
                streak = 0
            offset += len(ln)
        return []

    def _run_monotony_rule(
        self, rule: RuleDefinition, raw_text: str, masked_prose: str
    ) -> list[Finding]:
        findings: list[Finding] = []
        para_spans = [
            (s, e, p)
            for s, e, p in self._paragraph_spans(masked_prose)
            if not p.lstrip().startswith(("#", "|", "-", "*", "•"))
            and len(p.split()) >= 5
        ]
        if len(para_spans) >= rule.threshold.min_paras and rule.threshold.cv_max is not None:
            lengths = [len(p.split()) for _, _, p in para_spans]
            mean_len = sum(lengths) / len(lengths)
            if mean_len > 0:
                variance = sum((x - mean_len) ** 2 for x in lengths) / len(lengths)
                cv = math.sqrt(variance) / mean_len
                if cv < rule.threshold.cv_max:
                    findings.append(
                        self._make_finding(
                            rule,
                            raw_text,
                            para_spans[0][0],
                            f"[CV={cv:.3f} < {rule.threshold.cv_max} trên {len(para_spans)} đoạn]",
                            "Thay đổi độ dài câu và đoạn theo mạch ý thực tế, tránh chia đoạn đều như khuôn đúc.",
                        )
                    )

        # Kiểm tra 3 dòng/câu liên tiếp mở đầu bằng cùng một từ khóa
        openers: list[tuple[int, str, str]] = []
        offset = 0
        for ln in masked_prose.splitlines(keepends=True):
            clean_ln = stdlib_re.sub(r"^\s*(?:[-*•◦–>#]|\d+[.)])+\s*", "", ln).strip()
            words = stdlib_re.findall(r"[A-Za-zÀ-ỹĐđ]+", clean_ln)
            if len(words) >= 4 and len(words[0]) >= 3 and words[0].casefold() != "điều":
                openers.append((offset, words[0].casefold(), clean_ln))
            offset += len(ln)
        for i in range(len(openers) - 2):
            w0, w1, w2 = openers[i][1], openers[i + 1][1], openers[i + 2][1]
            if w0 == w1 == w2:
                findings.append(
                    self._make_finding(
                        rule,
                        raw_text,
                        openers[i][0],
                        f"Lặp từ mở đầu x3: '{w0}'",
                        "Đổi chủ ngữ mở đầu từng câu thay vì lặp cùng một từ ở 3 câu liên tiếp.",
                    )
                )
                break
        return findings

    def _run_loanword_and_jargon_rule(
        self, rule: RuleDefinition, raw_text: str, masked_prose: str, prof: Profile | None
    ) -> list[Finding]:
        findings: list[Finding] = []
        # 1. Dịch ngược từ tiếng Anh đã nhập tịch
        m_rev = self._REVERSE_LOANWORD_RE.search(masked_prose)
        if m_rev:
            findings.append(
                self._make_finding(
                    rule,
                    raw_text,
                    m_rev.start(),
                    raw_text[m_rev.start() : m_rev.end()],
                    "Giữ nguyên từ thông dụng đã quen dùng (email, pull request, repo, web) thay vì dịch từng chữ.",
                )
            )

        # 2. Mã bảng/hàm kỹ thuật thô lọt vào văn xuôi quản trị hoặc mạng xã hội
        if prof in (None, Profile.AUDIT_REPORT, Profile.SOCIAL_MEDIA):
            m_tech = self._RAW_TECH_ID_RE.search(masked_prose)
            if m_tech:
                findings.append(
                    self._make_finding(
                        rule,
                        raw_text,
                        m_tech.start(),
                        raw_text[m_tech.start() : m_tech.end()],
                        "Diễn đạt tên bảng hoặc phép tính kỹ thuật bằng ngôn ngữ nghiệp vụ dễ hiểu cho người đọc.",
                        override_profiles=["audit_report", "social_media"],
                    )
                )

        # 3. Từ tiếng Anh viết thường chưa Việt hóa nằm giữa câu tiếng Việt có dấu
        if not self._VI_DIACRITIC_RE.search(masked_prose):
            return findings
        strict_allowlist = UNIVERSAL_NATURALIZED_LOANWORDS
        broad_allowlist = UNIVERSAL_NATURALIZED_LOANWORDS | WORKPLACE_TECH_LOANWORDS

        for m_word in self._LOWER_ASCII_WORD_RE.finditer(masked_prose):
            token = m_word.group(0).lower()
            if not self._EN_PHONOTACTIC_RE.search(token):
                continue
            sent = self._sentence_around(masked_prose, m_word.start(), m_word.end())
            if not self._VI_DIACRITIC_RE.search(sent):
                continue

            if token in strict_allowlist:
                continue
            if token in broad_allowlist:
                if prof == Profile.AUDIT_REPORT or prof is None:
                    if prof is None:
                        findings.append(
                            self._make_finding(
                                rule,
                                raw_text,
                                m_word.start(),
                                raw_text[m_word.start() : m_word.end()],
                                f"Từ '{token}' thông dụng ở công sở nhưng nên cân nhắc Việt hóa nếu trình cấp quản trị.",
                                override_profiles=["audit_report"],
                            )
                        )
                    else:
                        findings.append(
                            self._make_finding(
                                rule,
                                raw_text,
                                m_word.start(),
                                raw_text[m_word.start() : m_word.end()],
                                f"Cân nhắc diễn đạt '{token}' bằng tiếng Việt chuẩn trong báo cáo kiểm toán/quản trị.",
                                override_profiles=["audit_report"],
                            )
                        )
                    break
                continue

            findings.append(
                self._make_finding(
                    rule,
                    raw_text,
                    m_word.start(),
                    raw_text[m_word.start() : m_word.end()],
                    f"Từ tiếng Anh '{token}' chưa nằm trong nhóm từ quen dùng; nên diễn đạt bằng tiếng Việt phù hợp.",
                )
            )
            break
        return findings

    @staticmethod
    def _parse_table_number(cell: str) -> float | None:
        cleaned = stdlib_re.sub(r"\([^)]*\)", "", cell).strip()
        cleaned = stdlib_re.sub(r"(?i)\b(?:đồng|đ|vnd|tr|triệu|tỷ)\b", "", cleaned).strip()
        if not cleaned or not stdlib_re.match(r"^[+-]?\d+(?:[.,]\d+)*$", cleaned):
            return None
        # Định dạng nghìn tiếng Việt: 1.200.000
        if stdlib_re.match(r"^[+-]?\d{1,3}(?:\.\d{3})+$", cleaned):
            return float(cleaned.replace(".", ""))
        return float(cleaned.replace(",", "."))

    def _run_document_and_table_hygiene(
        self, rule: RuleDefinition, raw_text: str, masked_full: str, masked_prose: str, prof: Profile | None
    ) -> list[Finding]:
        findings: list[Finding] = []
        has_vi = bool(self._VI_DIACRITIC_RE.search(masked_prose))

        # 1. Ký tự khoảng trắng ẩn, lỗi công thức, chồng dấu sao, mũi tên ASCII, phủ định kép
        quick_checks: list[tuple[stdlib_re.Pattern[str], str, list[str] | None]] = [
            (
                stdlib_re.compile(r"[\u200b\u200c\u200d\ufeff]"),
                "Xóa ký tự khoảng trắng ẩn (zero-width space / BOM) gây lệch lề danh sách.",
                None,
            ),
            (
                stdlib_re.compile(r"\*\*\*\*"),
                "Xóa dấu in đậm bị chồng `****`.",
                None,
            ),
            (
                stdlib_re.compile(r"#(?:REF|VALUE|NAME|N/A)!"),
                "Xóa lỗi công thức bảng tính bị rò rỉ ra văn bản.",
                None,
            ),
            (
                stdlib_re.compile(r"(?i)\bthiếu\s+-\s*\d"),
                "Bỏ dấu trừ sau chữ 'Thiếu' (viết 'Còn thiếu X%' thay vì 'Thiếu -X%').",
                None,
            ),
            (
                stdlib_re.compile(r"->"),
                "Thay mũi tên ASCII `->` trong câu văn xuôi bằng từ nối nhân quả hoặc thứ tự tự nhiên.",
                ["general", "audit_report", "academic", "legal", "social_media", "translation"],
            ),
            (
                stdlib_re.compile(r"(?m)(?:^[^;\n]*;){2,}"),
                "Tách câu có nhiều dấu chấm phẩy `;` liên tiếp thành các câu ngắn độc lập.",
                ["general", "marketing", "social_media", "translation"],
            ),
        ]
        if has_vi:
            quick_checks.append(
                (
                    stdlib_re.compile(r"\b\d+\.\d+%"),
                    "Dùng dấu phẩy cho số thập phân phần trăm trong tiếng Việt (ví dụ: '59,9%' thay vì '59.9%').",
                    ["general", "audit_report", "academic", "legal", "translation"],
                )
            )
            quick_checks.append(
                (
                    stdlib_re.compile(r"\([A-Za-zÀ-ỹĐđ0-9\s,+/-]{2,60}=[A-Za-zÀ-ỹĐđ0-9\s,+/%-]{1,60}\)"),
                    "Diễn đạt phép tính trong ngoặc đơn bằng lời tự nhiên ('tương ứng', 'gồm') thay vì dấu `=`.",
                    ["audit_report", "social_media"],
                )
            )

        for pat, advice, sub_profs in quick_checks:
            if prof is not None and sub_profs is not None and prof.value not in sub_profs:
                continue
            m = pat.search(masked_prose)
            if m:
                findings.append(
                    self._make_finding(
                        rule,
                        raw_text,
                        m.start(),
                        repr(raw_text[m.start() : m.end()]) if m.group(0).strip() == "" else raw_text[m.start() : m.end()],
                        advice,
                        override_profiles=sub_profs,
                    )
                )

        # 2. Tiêu đề tiếng Việt viết hoa từng chữ kiểu tiếng Anh (Title Case) & mục con đơn độc
        headings: list[tuple[int, int, str]] = []
        offset = 0
        for ln in masked_full.splitlines(keepends=True):
            m_h = stdlib_re.match(r"^(#{1,6})\s+(.+?)\s*$", ln)
            if m_h:
                level = len(m_h.group(1))
                h_text = m_h.group(2)
                headings.append((level, offset, h_text))
                h_check = stdlib_re.sub(r"\([^)]*\)", "", h_text)
                words = stdlib_re.findall(r"[A-Za-zÀ-ỹĐđ]{2,}", h_check)
                if (
                    has_vi
                    and len(words) >= 4
                    and not h_text.isupper()
                    and sum(1 for w in words if w[0].isupper() and not w.isupper()) >= max(4, math.ceil(len(words) * 0.8))
                ):
                    findings.append(
                        self._make_finding(
                            rule,
                            raw_text,
                            offset,
                            ln.strip(),
                            "Chỉ viết hoa chữ cái đầu câu và danh từ riêng trong tiêu đề tiếng Việt, không viết hoa đầu mỗi chữ kiểu tiếng Anh.",
                        )
                    )
            # Kiểm tra dòng danh sách có từ 2 dấu `:` trở lên
            elif stdlib_re.match(r"^\s*(?:[-*•◦–]|\d+[.)])\s+", ln):
                cleaned_ln = stdlib_re.sub(r"\b\d{1,2}:\d{2}\b|\b\d+:\d+\b", "", ln)
                if cleaned_ln.count(":") >= 2:
                    findings.append(
                        self._make_finding(
                            rule,
                            raw_text,
                            offset,
                            ln.strip()[:100],
                            "Không đặt từ 2 dấu hai chấm `:` trở lên trong cùng một mục liệt kê; hãy đưa nhãn phụ vào ngoặc đơn.",
                        )
                    )
            offset += len(ln)

        # Kiểm tra tiêu đề con đơn độc (ví dụ H2 có đúng 1 H3 bên dưới)
        for idx, (lvl, h_off, h_txt) in enumerate(headings):
            direct_children: list[tuple[int, str]] = []
            for next_lvl, next_off, next_txt in headings[idx + 1 :]:
                if next_lvl <= lvl:
                    break
                if next_lvl == lvl + 1:
                    direct_children.append((next_off, next_txt))
            if len(direct_children) == 1:
                child_off, child_txt = direct_children[0]
                if stdlib_re.match(r"^\d+(?:\.\d+)+", child_txt):
                    findings.append(
                        self._make_finding(
                            rule,
                            raw_text,
                            child_off,
                            child_txt,
                            f"Mục '{h_txt}' chỉ có duy nhất một mục con '{child_txt}'; nên bỏ cấp tiêu đề con lẻ loi này.",
                        )
                    )
                    break

        # 3. Kiểm tra đại từ nhân xưng và phép cộng dòng 'Tổng cộng' trong bảng
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

        pronoun_re = stdlib_re.compile(r"(?i)\b(?:bạn|mình|tôi|chúng ta)\b")
        for tbl in table_blocks:
            data_rows = [
                (off, [c.strip() for c in row.strip("|").split("|")])
                for off, row in tbl
                if not stdlib_re.match(r"^[\s|:\-+]+$", row)
            ]
            if len(data_rows) < 3:
                continue
            has_numeric_cell = any(
                self._parse_table_number(c) is not None
                for _, cells in data_rows[1:]
                for c in cells[1:]
            )
            if has_numeric_cell:
                for r_off, cells in data_rows[1:]:
                    joined = " ".join(cells)
                    m_p = pronoun_re.search(joined)
                    if m_p:
                        findings.append(
                            self._make_finding(
                                rule,
                                raw_text,
                                r_off,
                                m_p.group(0),
                                "Không đưa đại từ nhân xưng (bạn, mình, tôi, chúng ta) vào bên trong bảng số liệu.",
                            )
                        )
                        break

            last_off, last_cells = data_rows[-1]
            if last_cells and last_cells[0].lower().startswith("tổng cộng"):
                body_rows = data_rows[1:-1]
                for col_i in range(1, len(last_cells)):
                    tot = self._parse_table_number(last_cells[col_i])
                    if tot is None:
                        continue
                    vals = [
                        self._parse_table_number(r_cells[col_i])
                        for _, r_cells in body_rows
                        if col_i < len(r_cells)
                    ]
                    if vals and all(v is not None for v in vals):
                        expected = round(sum(v for v in vals if v is not None), 4)
                        if round(tot, 4) != expected:
                            findings.append(
                                self._make_finding(
                                    rule,
                                    raw_text,
                                    last_off,
                                    last_cells[col_i],
                                    f"Dòng 'Tổng cộng' cột {col_i + 1} ghi {tot:g} nhưng tổng các dòng thành phần bằng {expected:g}.",
                                )
                            )
        return findings

    def scan_text(
        self,
        text: str,
        profile: Profile | str = "all",
        active_rule_ids: set[str] | None = None,
    ) -> ScanReport:
        t0 = time.perf_counter()
        is_all = str(profile).lower() == "all"
        prof: Profile | None = None if is_all else (
            profile if isinstance(profile, Profile) else Profile(str(profile))
        )

        masked_no_code = SemanticMasker.mask_code_and_quotes(text, mask_quotes=True)
        masked_full = SemanticMasker.mask_preserve_offsets(text, mask_quotes=True)
        masked_prose = SemanticMasker.flatten_markdown_tables_preserve_lines(masked_full)

        words = stdlib_re.findall(r"\S+", masked_prose)
        word_count = max(len(words), 1)
        para_spans = self._paragraph_spans(masked_prose)
        findings: list[Finding] = []

        for rid, rule in self.rules.items():
            if active_rule_ids is not None and rid not in active_rule_ids:
                continue
            if prof is not None and prof not in rule.profiles:
                continue

            if rule.regex_or_algorithm == "ALGO:BOLD_COLON_LIST_STREAK_MIN_3":
                findings.extend(self._run_bold_colon_list_rule(rule, text, masked_prose, prof))
                continue
            if rule.regex_or_algorithm == "ALGO:PARAGRAPH_CV_AND_OPENING_MONOTONY":
                findings.extend(self._run_monotony_rule(rule, text, masked_prose))
                continue
            if rule.regex_or_algorithm == "ALGO:LOANWORD_AND_FOREIGN_TOKEN_CHECK":
                findings.extend(self._run_loanword_and_jargon_rule(rule, text, masked_prose, prof))
                continue
            if rule.regex_or_algorithm == "ALGO:DOCUMENT_AND_TABLE_HYGIENE":
                findings.extend(
                    self._run_document_and_table_hygiene(rule, text, masked_full, masked_prose, prof)
                )
                continue

            # VIS-AI-002 cần quét trên văn bản chưa che URL để bắt `utm_source=chatgpt.com`
            target_text = masked_no_code if rid == "VIS-AI-002" else masked_prose
            if rid == "VIS-FMT-003":
                target_text = "\n".join(
                    (" " * len(ln)) if ln.lstrip().startswith("—") else ln
                    for ln in target_text.splitlines()
                )
            elif rid == "VIS-FMT-004":
                # Che dấu phẩy thập phân để không nhận nhầm số liệu thành danh sách 3 vế
                target_text = stdlib_re.sub(r"(?<=\d),(?=\d)", ".", target_text)

            compiled_re = self._compiled[rid]
            valid_matches = [
                m
                for m in compiled_re.finditer(target_text)
                if not self._is_linguistically_exempt(rid, target_text, m.start(), m.end())
                and not self._is_profile_exempt(rid, target_text, m.start(), m.end(), prof)
            ]

            # Riêng VIS-RHET-001 kiểm tra thêm mật độ cụm phủ định bắc cầu >= 3 lần/bài
            if rid == "VIS-RHET-001" and not valid_matches:
                bridge_hits = list(self._BRIDGE_NEGATION_RE.finditer(target_text))
                if len(bridge_hits) >= 3:
                    first_b = bridge_hits[0]
                    findings.append(
                        self._make_finding(
                            rule,
                            text,
                            first_b.start(),
                            text[first_b.start() : first_b.end()].strip(),
                            "Lặp quá nhiều cụm phủ định bắc cầu ('chưa đồng nghĩa với', 'không có nghĩa là'); hãy đổi sang câu khẳng định trực tiếp.",
                        )
                    )
                continue

            if not valid_matches:
                continue

            triggered_match: Any = None
            thresh = rule.threshold
            if thresh.per_para is not None:
                for p_start, p_end, _ in para_spans:
                    in_para = [m for m in valid_matches if p_start <= m.start() < p_end]
                    if len(in_para) >= thresh.per_para:
                        triggered_match = in_para[0]
                        break
                if (
                    triggered_match is None
                    and thresh.per_1000_words is not None
                    and word_count >= 250
                    and (len(valid_matches) * 1000.0 / word_count) >= thresh.per_1000_words
                ):
                    triggered_match = valid_matches[0]
            elif thresh.per_doc is not None:
                if len(valid_matches) >= thresh.per_doc:
                    triggered_match = valid_matches[0]
            else:
                triggered_match = valid_matches[0]

            if triggered_match is not None:
                raw_slice = text[triggered_match.start() : triggered_match.end()].strip()
                findings.append(
                    self._make_finding(rule, text, triggered_match.start(), raw_slice)
                )

        findings.sort(key=lambda f: (f.line, f.col, f.rule_id))
        elapsed_ms = round((time.perf_counter() - t0) * 1000, 3)
        findings_per_1kw = round((len(findings) / word_count) * 1000, 2)
        weighted_score = round(sum(f.weight for f in findings), 3)
        invariants = SemanticMasker.extract_invariants(text)
        inv_summary = {k: len(v) for k, v in invariants.items()}
        cat_counts = dict(collections.Counter(f.category for f in findings))
        maint = check_loanwords_maintenance()

        return ScanReport(
            schema_version=self.SCHEMA_VERSION,
            scanner_version=self.VERSION,
            profile="all" if is_all else prof.value,  # type: ignore[union-attr]
            word_count=word_count,
            paragraph_count=len(para_spans),
            findings_count=len(findings),
            error_count=sum(1 for f in findings if f.severity == Severity.ERROR.value),
            warning_count=sum(1 for f in findings if f.severity == Severity.WARNING.value),
            info_count=sum(1 for f in findings if f.severity == Severity.INFO.value),
            findings_per_1000_words=findings_per_1kw,
            weighted_density_score=weighted_score,
            category_breakdown=cat_counts,
            elapsed_ms=elapsed_ms,
            maintenance_due=bool(maint["due_for_quarterly_review"]),
            disclaimer=self.DISCLAIMER,
            semantic_invariants_summary=inv_summary,
            findings=findings,
        )


# ============================================================================
# HÀM TƯƠNG THÍCH VÀ ĐỐI SOÁT DỮ KIỆN TRƯỚC / SAU BIÊN TẬP
# ============================================================================
def verify_text(before: str, after: str) -> dict[str, Any]:
    ok, errors = SemanticMasker.validate_rewrite_safety(
        before, after, strict_negations_and_modals=True
    )
    inv_b = SemanticMasker.extract_invariants(before)
    inv_a = SemanticMasker.extract_invariants(after)
    deltas: dict[str, dict[str, list[str]]] = {}
    for key in inv_b:
        cb = collections.Counter(inv_b[key])
        ca = collections.Counter(inv_a[key])
        removed = sorted((cb - ca).elements())
        added = sorted((ca - cb).elements())
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


def read_utf8(path: Path | str) -> str:
    if str(path) == "-":
        return sys.stdin.read()
    return Path(path).read_text(encoding="utf-8-sig")


def print_scan_report(report: ScanReport, label: str) -> None:
    print(f"Tệp: {label} | Chế độ lọc: {report.profile}")
    print(
        f"Từ: {report.word_count} | Đoạn: {report.paragraph_count} | "
        f"Tổng tín hiệu: {report.findings_count} "
        f"(Lỗi: {report.error_count}, Cảnh báo: {report.warning_count}, Gợi ý: {report.info_count}) | "
        f"Mật độ: {report.findings_per_1000_words}/1.000 từ | Thời gian: {report.elapsed_ms} ms"
    )
    if report.maintenance_due:
        print(
            "[NHẮC BẢO TRÌ] Danh sách từ tiếng Anh quen dùng (NATURALIZED_EN_LOANWORDS) "
            "đã đến kỳ rà soát hàng quý. Chạy `python scripts/vi_scanner.py check-maintenance` để xem chi tiết."
        )
    for idx, f in enumerate(report.findings, 1):
        profs_txt = (
            "mọi nhóm văn bản"
            if not f.exempt_profiles
            else f"áp dụng: {', '.join(f.applicable_profiles)} | miễn: {', '.join(f.exempt_profiles)}"
        )
        print(
            f"\n#{idx} [{f.severity.upper()}] {f.rule_id} ({f.category}) "
            f"dòng {f.line}:{f.col}"
        )
        print(f"  Ngữ cảnh: {profs_txt}")
        print(f"  Khớp: {f.matched_text!r}")
        print(f"  Vấn đề: {f.description_vi}")
        print(f"  Hướng sửa: {f.suggestion_vi}")
    print(f"\n{report.disclaimer}")


def selftest() -> int:
    scanner = ViScanner()
    dirty = (
        "Chắc chắn rồi! Dưới đây là bản phân tích. "
        "Giải pháp này không chỉ đơn thuần là công cụ, mà còn là ngọn hải đăng dẫn đường. "
        "Báo cáo được phê duyệt bởi hội đồng vào ngày 10/01/2026."
    )
    clean = (
        "Hội đồng quản trị đã phê duyệt báo cáo tài chính năm 2025 vào ngày 10/01/2026. "
        "Doanh thu quý IV đạt 128 tỷ đồng, tăng 14,5% so với cùng kỳ năm trước."
    )
    rep_all = scanner.scan_text(dirty)
    rep_clean = scanner.scan_text(clean)
    assert rep_all.profile == "all"
    assert rep_all.findings_count >= 3, f"Kỳ vọng >= 3 lỗi, nhận {rep_all.findings_count}"
    assert rep_clean.findings_count == 0, f"Báo nhầm trên câu sạch: {rep_clean.findings}"
    assert not verify_text("Tỷ lệ đạt 59,92% ngày 25/09/2026.", "Tỷ lệ đạt 60% ngày 25/09/2026.")["passed"]
    assert verify_text("Tỷ lệ đạt 59,92% ngày 25/09/2026.", "Ngày 25/09/2026, tỷ lệ đạt 59,92%.")["passed"]
    print("SELFTEST: PASS")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="vi_scanner",
        description="Công cụ rà lỗi câu chữ máy móc, sáo rỗng, dịch thô tiếng Việt và đối soát dữ kiện.",
    )
    p.add_argument("--version", action="version", version=VERSION)
    sub = p.add_subparsers(dest="command", required=True)

    profile_choices = ["all", *[pr.value for pr in ALL_PROFILES]]
    scan_p = sub.add_parser("scan", help="Quét tệp UTF-8 (mặc định xuất đủ 100%% các nhóm văn bản)")
    scan_p.add_argument("file", nargs="?", default="-", help="Đường dẫn tệp UTF-8 hoặc '-' để đọc stdin")
    scan_p.add_argument(
        "--profile",
        choices=profile_choices,
        default="all",
        help="Mặc định 'all' xuất đủ 100%% tín hiệu mọi nhóm; chọn 1 nhóm cụ thể khi cần lọc hẹp.",
    )
    scan_p.add_argument("--custom-rules", type=Path, help="Tệp JSON chứa quy tắc bổ sung riêng")
    scan_p.add_argument("--json", action="store_true", help="Xuất kết quả JSON ra stdout")
    scan_p.add_argument("--output", type=Path, help="Ghi kết quả JSON ra tệp")
    scan_p.add_argument(
        "--fail-on",
        choices=["any", "warning", "error", "never"],
        default="any",
        help="Mức tín hiệu trả mã thoát 1 (mặc định: any)",
    )

    ver_p = sub.add_parser("verify", help="Đối soát dữ kiện và từ phủ định/điều kiện trước - sau biên tập")
    ver_p.add_argument("before", type=Path)
    ver_p.add_argument("after", type=Path)
    ver_p.add_argument("--json", action="store_true")
    ver_p.add_argument("--output", type=Path)

    list_p = sub.add_parser("list-rules", help="Liệt kê danh mục 30 quy tắc hiện có")
    list_p.add_argument("--profile", choices=profile_choices, default="all")
    list_p.add_argument("--json", action="store_true")

    maint_p = sub.add_parser(
        "check-maintenance",
        help="Kiểm tra hạn rà soát định kỳ hàng quý/năm cho danh sách từ tiếng Anh quen dùng",
    )
    maint_p.add_argument("--today", help="Ngày kiểm tra dạng YYYY-MM-DD (mặc định hôm nay)")
    maint_p.add_argument("--json", action="store_true")

    sub.add_parser("selftest", help="Chạy bài tự kiểm tra nhanh")
    return p


def main(argv: Sequence[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

    args = build_parser().parse_args(argv)
    try:
        if args.command == "selftest":
            return selftest()

        if args.command == "check-maintenance":
            ref = dt.date.fromisoformat(args.today) if args.today else None
            info = check_loanwords_maintenance(ref)
            if args.json:
                print(json.dumps(info, ensure_ascii=False, indent=2))
            else:
                status = (
                    "QUÁ HẠN NĂM"
                    if info["overdue_annual_review"]
                    else ("ĐẾN KỲ RÀ SOÁT QUÝ" if info["due_for_quarterly_review"] else "ĐANG TRONG HẠN")
                )
                print(f"TRẠNG THÁI DANH SÁCH TỪ MƯỢN: {status}")
                print(f"  Lần rà soát gần nhất: {info['last_reviewed']} ({info['days_since_review']} ngày trước)")
                print(
                    f"  Số từ hiện có: {info['universal_loanwords_count']} từ phổ thông mọi ngữ cảnh + "
                    f"{info['workplace_tech_loanwords_count']} từ công sở/kỹ thuật"
                )
                print(f"  Ghi chú: {info['note']}")
            return 1 if info["overdue_annual_review"] else 0

        if args.command == "list-rules":
            scanner = ViScanner()
            rules = [
                r
                for r in scanner.rules.values()
                if args.profile == "all" or Profile(args.profile) in r.profiles
            ]
            if args.json:
                payload = [
                    {
                        "rule_id": r.rule_id,
                        "category": r.category,
                        "severity": r.severity.value,
                        "weight": r.weight,
                        "profiles": [p.value for p in ALL_PROFILES if p in r.profiles],
                        "exempt_profiles": list(r.exempt_profiles),
                        "description_vi": r.description_vi,
                    }
                    for r in rules
                ]
                print(json.dumps(payload, ensure_ascii=False, indent=2))
            else:
                for r in rules:
                    print(f"{r.rule_id} [{r.severity.value}] ({r.category}): {r.description_vi}")
            return 0

        if args.command == "scan":
            extra = ViScanner.load_custom_rules(args.custom_rules) if args.custom_rules else None
            scanner = ViScanner(extra_rules=extra)
            text = read_utf8(args.file)
            report = scanner.scan_text(text, profile=args.profile)
            payload = report.to_json(indent=2)
            if args.output:
                args.output.write_text(payload, encoding="utf-8")
            if args.json:
                print(payload)
            else:
                print_scan_report(report, str(args.file))

            if args.fail_on == "never":
                return 0
            if args.fail_on == "error":
                return 1 if report.error_count > 0 else 0
            if args.fail_on == "warning":
                return 1 if (report.error_count + report.warning_count) > 0 else 0
            return 1 if report.findings_count > 0 else 0

        if args.command == "verify":
            result = verify_text(read_utf8(args.before), read_utf8(args.after))
            payload = json.dumps(result, ensure_ascii=False, indent=2)
            if args.output:
                args.output.write_text(payload, encoding="utf-8")
            if args.json:
                print(payload)
            else:
                print("KẾT QUẢ ĐỐI SOÁT:", "ĐẠT (PASS)" if result["passed"] else "LỆCH DỮ KIỆN (FAIL)")
                for err in result["errors"]:
                    print(f"  - {err}")
                print(result["note"])
            return 0 if result["passed"] else 1
    except (OSError, UnicodeError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"LỖI: {exc}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
