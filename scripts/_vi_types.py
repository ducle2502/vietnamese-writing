"""Kiểu dữ liệu tĩnh và hằng số phiên bản cho gói `vi_scanner`."""

from __future__ import annotations

import json
import re as stdlib_re
from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import TYPE_CHECKING, Any, Protocol, TypedDict, cast

if TYPE_CHECKING:
    from collections.abc import Iterator

try:
    import re2 as _re2_engine  # type: ignore[import-not-found]

    USING_RE2 = True
except ImportError:
    _re2_engine = None
    USING_RE2 = False

VERSION = "2.2.0"
SCHEMA_VERSION = "2.2.0"


class _RegexMatch(Protocol):
    def start(self) -> int: ...
    def end(self) -> int: ...


class _CompiledRegex(Protocol):
    def finditer(self, string: str, /) -> Iterator[_RegexMatch]: ...


def compile_rule_regex(pattern: str) -> _CompiledRegex:
    if _re2_engine is not None:
        return cast("_CompiledRegex", _re2_engine.compile(pattern, _re2_engine.MULTILINE))
    return stdlib_re.compile(pattern, stdlib_re.MULTILINE)


class LoanwordsReviewMeta(TypedDict):
    last_reviewed: str
    cadence: str
    recommended_interval_days: int
    max_interval_days: int
    note: str


class MaintenanceReport(TypedDict):
    last_reviewed: str
    today: str
    days_since_review: int
    recommended_interval_days: int
    max_interval_days: int
    due_for_quarterly_review: bool
    overdue_annual_review: bool
    universal_loanwords_count: int
    workplace_tech_loanwords_count: int
    note: str


class StylometryReport(TypedDict):
    so_cau: int
    so_doan: int
    cau_trung_binh_doan: float
    dai_cau_tb: float
    bien_dong_do_dai_cau_cv: float
    lech_do_dai_cau_skew: float
    bien_dong_do_dai_doan_cv: float
    ty_le_tu_rieng_ttr_am_tiet: float
    mattr_cua_so_50: float
    so_dau_cham_than: int
    tro_tu_cuoi_cau: int
    lien_tu_hinh_thuc: int
    tu_noi_khau_ngu: int
    han_viet_hanh_chinh_tren_1000: float
    tu_lay: int
    entropy_dau_cau_bit: float
    do_nen_zlib: float
    canh_bao: list[str]


class InvariantDelta(TypedDict):
    removed: list[str]
    added: list[str]


class VerifyReport(TypedDict):
    version: str
    passed: bool
    errors: list[str]
    changes: dict[str, InvariantDelta]
    before_sha256: str
    after_sha256: str
    note: str


class DocxMetadata(TypedDict):
    core_title: str
    creator: str
    modified: str
    paragraph_blocks: int
    table_blocks: int
    template_title_mismatch: str | None


class DhdnaVoiceMetrics(TypedDict):
    mat_do_so_tren_1000_tu: float
    tong_so_ty_le_phan_tram: int
    ty_le_phan_tram_kem_tu_mau: float
    ranh_gioi_bang_chung_d12: int
    cong_chan_dieu_kien_d6: int
    tach_hoat_dong_trung_gian_d1: int
    neo_thoi_gian_tre_han_d11: int
    tam_giac_doi_chung_da_nguon: int
    tieu_de_hai_ve_doi_sanh: int
    nhan_doan_ket_thuc_dau_cham: int
    tu_tinh_thai_don_co_the: int
    chong_tu_rao_don: int
    ung_vien_lech_mau_so: dict[str, list[str]]


class VoiceArchetype(TypedDict):
    code: str
    description_vi: str


class ProfileReport(TypedDict):
    version: str
    file: str
    sha256_16: str
    word_count_total: int
    word_count_prose: int
    ignored_table_cols: list[int]
    docx_metadata: DocxMetadata | dict[str, Any]
    stylometry: StylometryReport
    dhdna_voice_metrics: DhdnaVoiceMetrics
    voice_archetype: VoiceArchetype


class RuleSummaryItem(TypedDict):
    rule_id: str
    category: str
    severity: str
    weight: float
    profiles: list[str]
    exempt_profiles: list[str]
    description_vi: str


LOANWORDS_REVIEW_META: LoanwordsReviewMeta = {
    "last_reviewed": "2026-11-10",
    "cadence": "quarterly_or_annual",
    "recommended_interval_days": 90,
    "max_interval_days": 365,
    "note": (
        "Rà soát hàng quý hoặc hàng năm tại data/vocab.csv: bổ sung từ tiếng Anh đã quen dùng rộng rãi "
        "mà nếu dịch sang tiếng Việt sẽ gây ngô nghê, và gỡ bỏ từ chỉ dùng trong nhóm hẹp."
    ),
}


@dataclass(frozen=True, slots=True)
class VocabCatalog:
    universal_loanwords: frozenset[str]
    workplace_loanwords: frozenset[str]
    all_allowed_loanwords: frozenset[str]
    reverse_calque_re: stdlib_re.Pattern[str] | None
    reverse_calque_hints: dict[str, str]
    banned_phrases_by_rule: dict[str, tuple[str, ...]]
    phrase_hints: dict[tuple[str, str], str]


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
        for raw_part in raw.split(";"):
            part = raw_part.strip()
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
    stylometry: StylometryReport | dict[str, Any] = field(default_factory=dict)
    findings: list[Finding] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, indent=indent)


@dataclass(frozen=True, slots=True)
class _ScanBuffer:
    raw_text: str
    masked_no_code: str
    masked_no_code_lower: str
    masked_full: str
    masked_prose: str
    masked_prose_lower: str
    nl_offsets: tuple[int, ...]
    para_spans: tuple[tuple[int, int, str], ...]
    word_count: int
