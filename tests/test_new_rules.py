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
from _vi_types import ALL_PROFILES  # noqa: E402
from fixtures_extra import AUDIT_AND_CALQUE_FIXTURES, NEW_RULE_FIXTURES, PRESENTATION_FIXTURES  # noqa: E402
from vi_scanner import DEFAULT_GRAMMAR_CSV, DEFAULT_VOCAB_CSV, ViScanner, verify_text  # noqa: E402

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
        for code, rule_id, profile, expected, text in (
            *NEW_RULE_FIXTURES,
            *PRESENTATION_FIXTURES,
            *AUDIT_AND_CALQUE_FIXTURES,
        ):
            rep = self.scanner.scan_text(text, profile=profile)
            hit = any(f.rule_id == rule_id for f in rep.findings)
            self.assertEqual(hit, expected, f"{code} ({rule_id}, {profile}) -> {[f.rule_id for f in rep.findings]}")

    def test_all_new_rules_are_loaded_and_active(self) -> None:
        """Mười ba rule mới (v2.3.0 đến v2.4.0) phải nạp đủ, bật và hợp lệ."""
        new_ids = {
            "VIS-RHET-008",
            "VIS-RHET-009",
            "VIS-RHET-010",
            "VIS-FMT-007",
            "VIS-FMT-008",
            "VIS-STRUCT-003",
            "VIS-STRUCT-004",
            "VIS-TONE-003",
            "VIS-TRANS-011",
            "VIS-TRANS-012",
            "VIS-TRANS-013",
            "VIS-TRANS-014",
            "VIS-TRANS-015",
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
        self.assertEqual(statuses.count("verified"), 51)
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
        self.assertEqual(len(rows), 2197)
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


_CALQUE_12_PAIRS: tuple[tuple[set[str], str, str], ...] = (
    (
        {"VIS-TRANS-005"},
        "Xem Tóm tắt điều hành ở trang 1 trước khi đọc phụ lục.",
        "Xem phần Tóm tắt ở trang 1 trước khi đọc phụ lục.",
    ),
    (
        {"VIS-TRANS-015"},
        "Báo cáo tuân thủ nghiêm ngặt kỷ luật bằng chứng và hàng rào nghiệp vụ.",
        "Báo cáo giữ đúng nguyên tắc chứng cứ và giới hạn kiểm soát nghiệp vụ.",
    ),
    (
        {"VIS-TRANS-015"},
        "Dự án phải vượt qua cổng kiểm định mới được nghiệm thu.",
        "Dự án phải qua bước kiểm tra bắt buộc mới được nghiệm thu.",
    ),
    (
        {"VIS-LEX-001"},
        "Cần đánh giá dưới góc độ rủi ro nhằm tối đa hóa hiệu quả.",
        "Cần đánh giá thẳng mức rủi ro để nâng cao hiệu quả kiểm soát.",
    ),
    (
        {"VIS-TONE-003"},
        "Chính sách này đã lỗi thời so với pháp luật hiện hành.",
        "Chính sách này chưa được cập nhật theo thông tư có hiệu lực từ ngày 01/07/2026.",
    ),
    (
        {"VIS-TONE-003"},
        "Kết quả đối chiếu 100% cho thấy đơn vị cố tình che giấu lỗi.",
        "Trong 30 hồ sơ chọn kiểm tra thuộc kỳ báo cáo, 6 hồ sơ thiếu biên bản giải trình.",
    ),
    (
        {"VIS-RHET-010"},
        "Nhiều người có thể cho rằng mức lỗi 3% là nhỏ, nhưng điều này không có nghĩa là hệ thống an toàn.",
        "Tỷ lệ lỗi là 3% trên tổng mẫu kiểm tra nhưng đều rơi vào giao dịch hạch toán cuối ngày.",
    ),
    (
        {"VIS-RHET-010"},
        "Bố cục cân đối là ngôn ngữ của niềm tin quản trị.",
        "Bố cục nhất quán giúp lãnh đạo tra cứu số liệu nhanh hơn.",
    ),
    (
        {"VIS-STRUCT-004", "VIS-RHET-003"},
        "Đối chiếu WP-04 và EV-19, mục này nêu các mảnh ghép còn thiếu.",
        "Đối chiếu nhật ký hệ thống ngày 14/11/2026, mục này nêu bốn phần việc còn thiếu.",
    ),
    (
        {"VIS-STRUCT-004"},
        "Hàm này được bổ sung nhằm thay thế cách tiếp cận cũ dùng hai vòng lặp.",
        "Hàm dùng bảng băm để tra cứu trực tiếp, giảm độ phức tạp xuống hằng số.",
    ),
    (
        {"VIS-LEX-001", "VIS-CLICHE-001"},
        "Tổ kiểm toán thực hiện tự kiểm định để đảm bảo tính minh bạch.",
        "Tổ kiểm toán tự rà soát lại số liệu nhằm công khai rõ căn cứ tính toán.",
    ),
    (
        {"VIS-RHET-003"},
        "Hệ thống cần một bàn đạp vững chắc để tạo đà bứt phá cuối năm.",
        "Hệ thống cần hoàn tất kiểm thử tải trước khi mở rộng giao dịch cuối năm.",
    ),
)


class TestCalquesAndAuditExtras(unittest.TestCase):
    scanner: ClassVar[ViScanner]

    @classmethod
    def setUpClass(cls) -> None:
        cls.scanner = ViScanner()

    def test_12_bad_good_calque_pairs(self) -> None:
        """Đủ 12 cặp câu mẫu Bad -> Good từ đặc tả mới phải bắt đúng lỗi và sửa về 0 lỗi."""
        for expected_rules, bad, good in _CALQUE_12_PAIRS:
            found_bad = {f.rule_id for f in self.scanner.scan_text(bad, profile="all").findings}
            self.assertTrue(expected_rules.issubset(found_bad), f"Thiếu {expected_rules} trong: {bad} ({found_bad})")
            rep_good = self.scanner.scan_text(good, profile="all")
            self.assertEqual(rep_good.findings_count, 0, f"Báo nhầm trên câu sửa: {good} -> {rep_good.findings}")

    def test_10_must_not_trigger_and_literal_metaphors(self) -> None:
        """Đủ 10 ca chống báo nhầm và 7 ẩn dụ dùng theo nghĩa đen vật lý phải sạch 0 lỗi."""
        clean_cases: tuple[str, ...] = (
            "Hội đồng kỷ luật lao động quyết định hình thức xử lý kỷ luật nhân sự theo nội quy.",
            "Công ty đang xử lý vướng mắc liên quan đến hàng rào kỹ thuật thương mại khi xuất khẩu.",
            "Khu vực công trường đã lắp đặt hàng rào chắn bảo vệ công nhân vào ban đêm.",
            "Hệ thống đã kết nối cổng thanh toán điện tử và cổng thông tin nội bộ đúng tiến độ.",
            "Tường lửa mạng đã chặn 140 lượt truy cập trái phép từ địa chỉ ngoài.",
            "Đường truyền viễn thông tại chi nhánh bị gián đoạn 12 phút lúc 09:15.",
            "Nhóm kỹ thuật đã tái lập máy chủ dự phòng trong 25 phút sau diễn tập.",
            "Quy định nội bộ số 12/QĐ-HĐTV đã hết hiệu lực kể từ ngày 01/01/2026 theo Thông tư số 02/2026/TT-NHNN.",
            "Trong nhật ký thử tải ghi nhận mã lỗi HTTP 504 tại điểm cuối API.",
            "Luật Doanh nghiệp phân định rõ tư cách pháp nhân của công ty mẹ và công ty con.",
            "Thợ sửa xe đạp thay bàn đạp và dây phanh trước giờ xuất phát.",
            "Kỹ sư thi công hai trụ cột bê tông chịu lực cho công trình cầu.",
            "Nhân viên tháo nút thắt dây thừng buộc kiện hàng trên bến bãi.",
            "Ghế làm việc có chỗ dựa lưng điều chỉnh độ nghiêng theo chiều cao.",
            "Ảnh X-quang ghi nhận một điểm sáng nhỏ ở góc trên bên phải màn hình.",
            "Đội xây dựng đổ bê tông đặt nền móng cho nhà máy mới.",
            "Trẻ nhỏ chơi trò chơi xếp hình ghép đủ mảnh ghép cuối cùng.",
        )
        for text in clean_cases:
            rep = self.scanner.scan_text(text, profile="all")
            self.assertEqual(rep.findings_count, 0, f"Báo nhầm: {text} -> {rep.findings}")

    def test_cross_rule_dedup_and_baseline_profiles(self) -> None:
        """Cụm trùng chuỗi không nổ kép xuyên rule và 8 rule chuẩn tối thiểu chạy đủ trên 7 profile."""
        for phrase in (
            "điểm chạm khách hàng",
            "nhằm mục đích nâng cao",
            "góp phần nâng cao nhận thức",
            "tái cấu trúc toàn diện",
            "ở cốt lõi của nó",
        ):
            rep = self.scanner.scan_text(f"Báo cáo nêu rõ {phrase} trong kỳ kiểm tra.", profile="all")
            non_algo = [
                f for f in rep.findings if not self.scanner.rules[f.rule_id].regex_or_algorithm.startswith("ALGO:")
            ]
            self.assertEqual(len(non_algo), 1, f"Nổ kép trên {phrase!r}: {non_algo}")

        baseline_ids = (
            "VIS-FMT-008",
            "VIS-TRANS-012",
            "VIS-TRANS-013",
            "VIS-TRANS-014",
            "VIS-TRANS-015",
            "VIS-TONE-003",
            "VIS-RHET-010",
            "VIS-STRUCT-004",
        )
        all_set = frozenset(ALL_PROFILES)
        for rid in baseline_ids:
            self.assertEqual(self.scanner.rules[rid].profiles, all_set, f"{rid} chưa phủ đủ 7 profile")

    def test_audit_extras_para_density_cv_and_table_overlap(self) -> None:
        """Kiểm tra mật độ đoạn, CV câu thấp trên văn bản dài và lặp tóm tắt bảng biểu."""
        dense_doc = (
            "Đoạn một có câu thứ nhất. Câu thứ hai ngắn gọn. Câu thứ ba mở rộng.\n\n"
            "Đoạn hai có câu thứ nhất. Câu thứ hai ngắn gọn. Câu thứ ba mở rộng.\n\n"
            "Đoạn ba có câu thứ nhất. Câu thứ hai ngắn gọn. Câu thứ ba mở rộng.\n"
        )
        audit_hits = [f.matched_text for f in self.scanner.scan_text(dense_doc, profile="audit_report").findings]
        self.assertTrue(any("câu/đoạn > 2,5" in m for m in audit_hits), audit_hits)
        gen_hits = [f.matched_text for f in self.scanner.scan_text(dense_doc, profile="general").findings]
        self.assertFalse(any("câu/đoạn > 2,5" in m for m in gen_hits))

        uniform_30 = "\n\n".join(
            f"Nhóm kiểm toán ghi nhận mục kiểm tra thứ {i} đã đối chiếu xong chứng từ gốc tại chi nhánh."
            for i in range(1, 32)
        )
        cv_hits = [f.matched_text for f in self.scanner.scan_text(uniform_30, profile="audit_report").findings]
        self.assertTrue(any("CV câu=" in m for m in cv_hits), cv_hits)

        dup_summary = (
            "Chi nhánh hoàn thành kiểm tra chứng từ công nợ khách hàng, rà soát quy trình phê duyệt "
            "giải ngân và đối chiếu số dư tài khoản kho bạc trong quý hai năm nay.\n\n"
            "| Hạng mục | Kết quả kiểm tra |\n| --- | --- |\n"
            "| Chứng từ công nợ khách hàng | Chi nhánh hoàn thành kiểm tra trong quý hai |\n"
            "| Quy trình phê duyệt giải ngân | Rà soát đầy đủ hồ sơ quý hai năm nay |\n"
            "| Số dư tài khoản kho bạc | Đối chiếu khớp số dư cuối quý hai |\n"
        )
        dup_hits = [f.matched_text for f in self.scanner.scan_text(dup_summary, profile="audit_report").findings]
        self.assertTrue(any("Chi nhánh hoàn thành" in m for m in dup_hits), dup_hits)

    def test_5_spec_calques_trigger_lex001(self) -> None:
        """Năm cụm dịch spec tiếng Anh mới thêm phải kích hoạt VIS-LEX-001."""
        samples = (
            "Chỉ áp dụng khi người dùng có yêu cầu tường minh.",
            "Bước này là đường mặc định khi đọc dữ liệu.",
            "Hệ thống trả về nhãn dự phòng khi thiếu dữ kiện.",
            "Máy quét bỏ qua phần mã nội dòng trong câu văn.",
            "Công cụ dùng bóc tách tất định để đọc tệp Word.",
        )
        for text in samples:
            hits = {f.rule_id for f in self.scanner.scan_text(text, profile="all").findings}
            self.assertIn("VIS-LEX-001", hits, f"Bỏ sót VIS-LEX-001 trên: {text}")

    def test_canh_bao_domain_calque_and_exemptions(self) -> None:
        """Cụm ghép 'cảnh báo + lĩnh vực' kích hoạt VIS-TRANS-015 nhưng động từ dẫn mệnh đề phải sạch."""
        bad_cases = (
            "Cảnh báo pháp lý trước 30/11 và các chỉ đạo chính tháng 11/2026",
            "Đơn vị gửi cảnh báo tuân thủ và cảnh báo vận hành trong quý IV.",
            "Cảnh báo bảo mật trước kỳ nâng cấp tháng 11/2026.",
            "Cảnh báo hệ thống trước 30/11.",
            "Đơn vị gửi cảnh báo dữ liệu chưa được xác minh.",
        )
        for text in bad_cases:
            findings = [f for f in self.scanner.scan_text(text, profile="all").findings if f.rule_id == "VIS-TRANS-015"]
            self.assertTrue(findings, f"Bỏ sót VIS-TRANS-015 trên: {text}")
            self.assertIn("cảnh báo + lĩnh vực", findings[0].suggestion_vi)

        clean_cases = (
            "Bộ phận kỹ thuật cảnh báo hệ thống có thể quá tải vào cuối tuần.",
            "Kiểm toán nội bộ đã cảnh báo dữ liệu khách hàng chưa được mã hóa.",
            "Đoàn kiểm tra cảnh báo quy trình phê duyệt còn lỏng lẻo.",
            "Giám đốc cảnh báo kế toán trưởng về sai sót chứng từ.",
            "Ứng dụng tự động đối soát công nợ và gửi cảnh báo đơn trễ hạn.",
            "Đài khí tượng phát tin cảnh báo bão số 3 và cảnh báo sớm lũ quét.",
            "Lưu ý pháp lý trước hạn 30/11 và các chỉ đạo trọng tâm tháng 11/2026.",
        )
        for text in clean_cases:
            rep = self.scanner.scan_text(text, profile="all")
            self.assertEqual(rep.findings_count, 0, f"Báo nhầm trên: {text} -> {rep.findings}")

    def test_collocation_and_ktnb_vocab_entries(self) -> None:
        """Các mục từ mới phải kích hoạt đúng quy tắc và bản viết lại đạt 0 lỗi."""
        pairs = (
            ("VIS-LEX-001", "Cần giữ đều thói quen kiểm tra sổ sách.", "Cần duy trì thói quen kiểm tra sổ sách."),
            (
                "VIS-CLICHE-004",
                "Nhóm hướng dẫn cầm tay chỉ việc cho người mới.",
                "Nhóm hướng dẫn từng bước cho người mới.",
            ),
            ("VIS-STRUCT-001", "Bài học cần nêu rõ mục tiêu đầu ra.", "Bài học cần nêu rõ kết quả đạt được."),
            ("VIS-CLICHE-003", "Kỹ sư chạy thử dry-run trước khi triển khai.", "Kỹ sư chạy thử trước khi triển khai."),
            ("VIS-LEX-001", "Ban quản lý cần khóa phạm vi dự án.", "Ban quản lý cần xác định phạm vi dự án."),
            (
                "VIS-LEX-001",
                "Báo cáo phân loại theo bậc tự khai của đơn vị.",
                "Báo cáo phân loại theo trạng thái đơn vị tự khai.",
            ),
            ("VIS-TRANS-015", "Quy trình bổ sung cổng kiểm tra bắt buộc.", "Quy trình bổ sung bước kiểm tra bắt buộc."),
            (
                "VIS-LEX-002",
                "Bộ phận tín dụng họp room vào sáng thứ hai.",
                "Bộ phận tín dụng họp về hạn mức tín dụng sáng thứ hai.",
            ),
        )
        for rule_id, bad, good in pairs:
            hits = [f for f in self.scanner.scan_text(bad, profile="all").findings if f.rule_id == rule_id]
            self.assertTrue(hits, f"Thiếu {rule_id} trên: {bad}")
            if rule_id == "VIS-LEX-002":
                self.assertIn("tránh chêm từ ngoại lai", hits[0].suggestion_vi.casefold())
            rep_good = self.scanner.scan_text(good, profile="all")
            self.assertEqual(rep_good.findings_count, 0, f"Báo nhầm trên: {good} -> {rep_good.findings}")

    def test_verify_text_lexical_negation_softening(self) -> None:
        """verify_text cảnh báo dịu phủ định từ vựng nhưng vẫn chặn rơi phủ định và đổi động từ khuyết thiếu."""
        res1 = verify_text("Quy định trái luật và thiếu hồ sơ.", "Quy định chưa phù hợp với quy định và chưa đủ hồ sơ.")
        self.assertTrue(res1["passed"])
        self.assertEqual(res1["errors"], [])
        self.assertEqual(len(res1["warnings"]), 1)

        self.assertFalse(verify_text("Đơn vị không gửi báo cáo.", "Đơn vị gửi báo cáo.")["passed"])
        self.assertFalse(verify_text("Hồ sơ đạt yêu cầu.", "Hồ sơ chưa đạt yêu cầu.")["passed"])
        self.assertFalse(verify_text("Đơn vị phải báo cáo đúng hạn.", "Đơn vị cần báo cáo đúng hạn.")["passed"])

    def test_khoang_trong_abstract_vs_physical(self) -> None:
        """Cụm 'khoảng trống' trừu tượng báo VIS-LEX-001 trên mọi profile, ngữ cảnh vật lý phải sạch."""
        bad_cases = (
            "Báo cáo chỉ ra khoảng trống kiểm soát và khoảng trống pháp lý cần lấp đầy.",
            "Còn tồn tại khoảng trống dữ liệu trong hồ sơ.",
        )
        for prof in ("all", "marketing"):
            for text in bad_cases:
                findings = self.scanner.scan_text(text, profile=prof).findings
                hits = [f for f in findings if f.rule_id == "VIS-LEX-001"]
                self.assertTrue(hits, f"Bỏ sót VIS-LEX-001 ({prof}) trên: {text}")
        clean = "Cần chừa khoảng trống 2 cm ở lề trang giấy trước khi đóng quyển."
        rep = self.scanner.scan_text(clean, profile="all")
        self.assertEqual(rep.findings_count, 0, f"Báo nhầm nghĩa vật lý: {rep.findings}")


if __name__ == "__main__":
    unittest.main()
