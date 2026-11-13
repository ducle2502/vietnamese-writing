#!/usr/bin/env python3
"""Kiểm thử chín quy tắc mới, ngưỡng trình bày và năm mã giọng văn."""

from __future__ import annotations

import csv
import io
import sys
import tempfile
import unittest
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar, cast

TESTS_DIR = Path(__file__).resolve().parent
ROOT = TESTS_DIR.parent
SCRIPTS_DIR = ROOT / "scripts"
for _dir in (str(SCRIPTS_DIR), str(TESTS_DIR)):
    if _dir not in sys.path:
        sys.path.insert(0, _dir)

from _vi_docx_dhdna import _classify_voice_archetype, profile_text  # noqa: E402
from fixtures_extra import NEW_RULE_FIXTURES, PRESENTATION_FIXTURES  # noqa: E402
from vi_scanner import DEFAULT_GRAMMAR_CSV, DEFAULT_VOCAB_CSV, ViScanner  # noqa: E402

if TYPE_CHECKING:
    from _vi_types import DhdnaVoiceMetrics, StylometryReport


def _stylo(mean: float, cv: float, sentences: int = 8) -> StylometryReport:
    return cast("StylometryReport", {"dai_cau_tb": mean, "bien_dong_do_dai_cau_cv": cv, "so_cau": sentences})


def _metrics(**overrides: int | float) -> DhdnaVoiceMetrics:
    base = {
        "ranh_gioi_bang_chung_d12": 0,
        "cong_chan_dieu_kien_d6": 0,
        "tach_hoat_dong_trung_gian_d1": 0,
        "tieu_de_hai_ve_doi_sanh": 0,
        "tam_giac_doi_chung_da_nguon": 0,
        "mat_do_so_tren_1000_tu": 0.0,
        "nhan_bang_chung": 0,
        "cau_truc_phan_luong_nguoi_doc": 0,
    }
    base.update(overrides)
    return cast("DhdnaVoiceMetrics", base)


class TestNewRules(unittest.TestCase):
    scanner: ClassVar[ViScanner]

    @classmethod
    def setUpClass(cls) -> None:
        cls.scanner = ViScanner()

    def test_new_rule_fixtures(self) -> None:
        """Mỗi mẫu dương tính bắt đúng rule đích và mẫu âm tính không bắt nhầm rule đó."""
        for code, rule_id, profile, expected, text in (*NEW_RULE_FIXTURES, *PRESENTATION_FIXTURES):
            rep = self.scanner.scan_text(text, profile=profile)
            hit = any(f.rule_id == rule_id for f in rep.findings)
            self.assertEqual(hit, expected, f"{code} ({rule_id}, {profile}) -> {[f.rule_id for f in rep.findings]}")

    def test_all_new_rules_are_loaded_and_active(self) -> None:
        """Chín rule mới phải có trong bundle, đang bật và có trạng thái nguồn hợp lệ."""
        new_ids = {
            "VIS-RHET-008",
            "VIS-RHET-009",
            "VIS-FMT-007",
            "VIS-FMT-008",
            "VIS-STRUCT-003",
            "VIS-TRANS-011",
            "VIS-TRANS-012",
            "VIS-TRANS-013",
            "VIS-TRANS-014",
        }
        self.assertTrue(new_ids.issubset(self.scanner.rules))
        for rid in new_ids:
            rule = self.scanner.rules[rid]
            self.assertEqual(rule.status, "active")
            self.assertIn(rule.source_status, {"verified", "missing", "internal"})

    def test_source_status_column_and_counts(self) -> None:
        """CSV grammar có cột source_status và chỉ dùng ba giá trị đã khai báo."""
        raw = DEFAULT_GRAMMAR_CSV.read_text(encoding="utf-8-sig")
        rows = list(csv.DictReader(io.StringIO(raw)))
        self.assertIn("source_status", rows[0])
        statuses = [r["source_status"] for r in rows]
        self.assertEqual(set(statuses), {"verified", "missing"})
        self.assertEqual(statuses.count("verified"), 47)
        self.assertEqual(statuses.count("missing"), 4)
        for row in rows:
            if not row["source_url"]:
                self.assertEqual(row["source_status"], "missing", row["rule_id"])

    def test_alt_and_mermaid_threshold_is_two_to_eight(self) -> None:
        """`alt` và nhãn Mermaid đúng 8 chữ thì qua, 9 chữ mới bị gắn cờ."""
        eight = 'Ảnh minh họa giao diện. <img src="a.svg" alt="Một hai ba bốn năm sáu bảy tám">'
        nine = 'Ảnh minh họa giao diện. <img src="a.svg" alt="Một hai ba bốn năm sáu bảy tám chín">'
        self.assertFalse(
            any(f.rule_id == "VIS-STRUCT-002" for f in self.scanner.scan_text(eight, profile="general").findings)
        )
        self.assertTrue(
            any(f.rule_id == "VIS-STRUCT-002" for f in self.scanner.scan_text(nine, profile="general").findings)
        )

    def test_legacy_grammar_csv_without_source_status_still_loads(self) -> None:
        """CSV kiểu 2.2.0 thiếu cột `source_status` vẫn nạp được và mặc định `missing`."""
        legacy = (
            "rule_id;status;category;pattern_type;regex_or_algo;severity;weight;profiles;"
            "threshold;exceptions;description_vi;bad_example;better_example;source_url;evidence_strength\n"
            "VIS-CUSTOM-COMPAT;active;CUSTOM;regex;(?i)\\bcấm\\b;warning;0,5;all;1/doc;none;"
            "Quy tắc cũ;;;;medium\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            grammar_path = Path(tmp) / "grammar.csv"
            grammar_path.write_text(legacy, encoding="utf-8-sig")
            vocab_path = Path(tmp) / "vocab.csv"
            vocab_path.write_text(
                "term;kind;rule_id;replacement_hint;status;note\n",
                encoding="utf-8-sig",
            )
            scanner = ViScanner(vocab_path=vocab_path, grammar_path=grammar_path)
            self.assertEqual(len(scanner.rules), 1)
            self.assertEqual(scanner.rules["VIS-CUSTOM-COMPAT"].source_status, "missing")

    def test_vocab_number_is_stable(self) -> None:
        """Số mục từ phải khớp bảng đã công bố và không có term trùng."""
        raw = DEFAULT_VOCAB_CSV.read_text(encoding="utf-8-sig")
        rows = list(csv.DictReader(io.StringIO(raw)))
        self.assertEqual(len(rows), 2089)
        keys = [" ".join(r["term"].split()).casefold() for r in rows]
        self.assertEqual(len(keys), len(set(keys)))


class TestVoiceArchetypes(unittest.TestCase):
    def test_five_codes_and_fallback_warning(self) -> None:
        """Bốn kiểu chính, nhãn đa người đọc và cảnh báo nhịp đều trả đúng mã."""
        direct = _classify_voice_archetype(
            _stylo(20.0, 0.5),
            _metrics(ranh_gioi_bang_chung_d12=3, cong_chan_dieu_kien_d6=2),
        )
        self.assertEqual(direct["code"], "DIRECT_EXECUTIVE_GATEKEEPER")
        self.assertEqual(direct["warnings"], [])

        multi = _classify_voice_archetype(
            _stylo(24.0, 0.5),
            _metrics(nhan_bang_chung=1, cau_truc_phan_luong_nguoi_doc=1),
        )
        self.assertEqual(multi["code"], "MULTI_READER_ASSURANCE")

        balanced = _classify_voice_archetype(_stylo(24.0, 0.5), _metrics(tieu_de_hai_ve_doi_sanh=2))
        self.assertEqual(balanced["code"], "BALANCED_COMPARATIVE_SUPERVISORY")

        technical = _classify_voice_archetype(_stylo(18.0, 0.5), _metrics(mat_do_so_tren_1000_tu=40.0))
        self.assertEqual(technical["code"], "TECHNICAL_RCA_ASSURANCE")

        clean = _classify_voice_archetype(_stylo(24.0, 0.5), _metrics())
        self.assertEqual(clean["code"], "CLEAN_GENERAL_VIETNAMESE")
        self.assertEqual(clean["warnings"], [])

        monotone = _classify_voice_archetype(_stylo(30.0, 0.5), _metrics())
        self.assertEqual(monotone["code"], "CLEAN_GENERAL_VIETNAMESE")
        self.assertEqual(monotone["warnings"], ["BUREAUCRATIC_OR_MONOTONE_DRAFT"])

    def test_profile_generates_multi_reader_from_labels(self) -> None:
        """Văn bản có nhãn bằng chứng và phân cấp người đọc phải sinh mã đa người đọc."""
        doc = (
            "Kết luận cấp A cho Hội đồng quản trị.\n\n"
            "[FACT] Có 12/20 hồ sơ đạt yêu cầu.\n\n"
            "[GAP] Chưa nhận được biên bản đối chiếu.\n\n"
            "Kết luận cấp B cho Ban điều hành.\n"
        )
        report = profile_text(doc, label="multi_reader")
        self.assertEqual(report["voice_archetype"]["code"], "MULTI_READER_ASSURANCE")


if __name__ == "__main__":
    unittest.main()
