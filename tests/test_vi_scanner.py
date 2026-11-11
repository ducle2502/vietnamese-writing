#!/usr/bin/env python3
"""Bộ kiểm thử đơn vị cho quy tắc, chế độ lọc, câu dài vòng vo và xử lý `.docx` của `vi_scanner`."""

from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from typing import ClassVar

TESTS_DIR = Path(__file__).resolve().parent
ROOT = TESTS_DIR.parent
SCRIPTS_DIR = ROOT / "scripts"
for _dir in (str(SCRIPTS_DIR), str(TESTS_DIR)):
    if _dir not in sys.path:
        sys.path.insert(0, _dir)

from fixtures_100 import BENCHMARK_100_FIXTURES  # noqa: E402
from vi_scanner import (  # noqa: E402
    ViScanner,
    extract_docx_text_and_meta,
    main,
    profile_text,
)


class TestViScannerRulesAndProfiles(unittest.TestCase):
    scanner: ClassVar[ViScanner]

    @classmethod
    def setUpClass(cls) -> None:
        cls.scanner = ViScanner()

    def test_benchmark_100_fixtures_precision_recall_zero_fpr(self) -> None:
        """Kiểm tra toàn bộ 100 mẫu độc lập đạt Precision = 1.0, Recall = 1.0, FPR = 0.0%."""
        tp = fp = tn = fn = 0
        failures: list[str] = []
        for fid, target_rule, profile, expected_pos, text in BENCHMARK_100_FIXTURES:
            report = self.scanner.scan_text(text, profile=profile)
            found_ids = {f.rule_id for f in report.findings}
            if expected_pos:
                if target_rule in found_ids:
                    tp += 1
                else:
                    fn += 1
                    failures.append(f"{fid}: Bỏ sót {target_rule} (chỉ thấy {found_ids})")
            elif not found_ids:
                tn += 1
            else:
                fp += 1
                failures.append(f"{fid} ({profile}): Báo nhầm {found_ids}")

        self.assertEqual(failures, [], "Lỗi trên bộ 100 mẫu:\n" + "\n".join(failures))
        self.assertEqual((tp, tn, fp, fn), (50, 50, 0, 0))

    def test_default_scan_outputs_100_percent_all_profiles(self) -> None:
        """Mặc định không truyền profile phải chạy ở chế độ `all` và xuất tín hiệu mọi nhóm."""
        sample = (
            "Hãy cùng chúng tôi đi sâu vào khám phá trong bài viết hôm nay! "
            "Phương pháp này được sử dụng rộng rãi, quy trình được thực hiện tự động "
            "và kết quả được ghi nhận hàng ngày. "
            "Anh Hùng ơi, bên mình cần đẩy mạnh công tác tuyên truyền ngay."
        )
        rep_all = self.scanner.scan_text(sample)
        self.assertEqual(rep_all.profile, "all")
        all_ids = {f.rule_id for f in rep_all.findings}
        for expected_id in ("VIS-AI-004", "VIS-TRANS-002", "VIS-CLICHE-001", "VIS-TONE-001"):
            self.assertIn(expected_id, all_ids)
        for f in rep_all.findings:
            self.assertGreaterEqual(len(f.applicable_profiles), 1)

    def test_group6_voice_lexical_and_structure_rules(self) -> None:
        """Kiểm tra các quy tắc từ vựng sai nghĩa, từ mượn, giọng sồn sã và bảng số liệu Nhóm 6."""
        r_bad_lex = self.scanner.scan_text("Hồ sơ dự án thực chứng này cho máy tính ghép để tìm dòng in đúp.")
        self.assertIn("VIS-LEX-001", {f.rule_id for f in r_bad_lex.findings})
        r_good_phil = self.scanner.scan_text(
            "Bài viết phân tích trường phái chủ nghĩa thực chứng trong triết học thế kỷ XIX."
        )
        self.assertNotIn("VIS-LEX-001", {f.rule_id for f in r_good_phil.findings})

        r_rev = self.scanner.scan_text("Đơn vị gửi thư điện tử xin dùng workaround trước giờ cutover.")
        self.assertIn("VIS-LEX-002", {f.rule_id for f in r_rev.findings})
        r_nat = self.scanner.scan_text(
            "Đơn vị gửi email kèm tài liệu pdf đăng trên website chính thức.", profile="audit_report"
        )
        self.assertEqual(r_nat.findings_count, 0)

        r_tone = self.scanner.scan_text(
            "Anh Khoa ơi, báo cáo ghi nhận sự nỗ lực rất lớn của nhóm nhưng vẫn còn rủi ro sát sườn.",
            profile="audit_report",
        )
        self.assertIn("VIS-TONE-001", {f.rule_id for f in r_tone.findings})

        r_meta = self.scanner.scan_text(
            "Bước ngoặt tư duy: Hồ sơ thứ nhất lệch 5 triệu, sang hồ sơ thứ hai thiếu 5 triệu.",
            profile="social_media",
        )
        self.assertIn("VIS-STRUCT-001", {f.rule_id for f in r_meta.findings})

        doc_struct = (
            "## 1. Hồ Sơ Dự Án Chọn Lọc\n### 1.1. Mục con duy nhất\n"
            "- Xem chi tiết tại [tài liệu gốc](file:///d:/Experiment/vietnamese-writing/README.md).\n\n"
            "| Khách hàng | Số dư |\n| --- | --- |\n| Bạn A | 100 |\n| Khách B | 200 |\n| Tổng cộng | 250 |\n"
        )
        struct_hits = [
            f for f in self.scanner.scan_text(doc_struct, profile="general").findings if f.rule_id == "VIS-STRUCT-002"
        ]
        self.assertGreaterEqual(len(struct_hits), 4)
        for f in struct_hits:
            self.assertNotIn("file:///", f.matched_text)

    def test_lengthy_and_roundabout_sentences_heavily_penalized(self) -> None:
        """Kiểm tra `VIS-LEN-001` phạt nặng câu dài quá ngưỡng, câu nối đuôi nhiều dấu phẩy và dẫn dắt vòng vo."""
        run_on = (
            "Thông qua việc rà soát toàn bộ 180 hồ sơ giải ngân tại 6 chi nhánh khu vực miền Trung trong quý II "
            "năm 2026, đoàn kiểm toán nội bộ ghi nhận quy trình thẩm định tài sản bảo đảm vẫn qua bốn bước ký nháy "
            "thủ công trên giấy tờ rời rạc, làm kéo dài thời gian xử lý trung bình thêm 7 ngày làm việc."
        )
        rep_run_on = self.scanner.scan_text(run_on, profile="audit_report")
        len_hits = [f for f in rep_run_on.findings if f.rule_id == "VIS-LEN-001"]
        self.assertEqual(len(len_hits), 1)
        self.assertEqual(len_hits[0].severity, "error")
        self.assertGreaterEqual(len_hits[0].weight, 1.8)
        self.assertGreaterEqual(rep_run_on.error_count, 1)
        self.assertTrue(any("> 35 từ" in w for w in rep_run_on.stylometry.get("canh_bao", [])))

        comma_chain = (
            "Đơn vị tiếp nhận hồ sơ vay vốn của khách hàng cá nhân, kiểm tra lịch sử trả nợ trên hệ thống, "
            "đối chiếu bảng lương sao kê sáu tháng, gửi tờ trình sang bộ phận thẩm định giá, chờ trưởng phòng "
            "phê duyệt hạn mức, rồi mới chuyển hồ sơ sang bộ phận giải ngân cuối ngày."
        )
        rep_comma = self.scanner.scan_text(comma_chain, profile="general")
        self.assertIn("VIS-LEN-001", {f.rule_id for f in rep_comma.findings})

        for roundabout_sample in (
            "Liên quan đến vấn đề đối chiếu công nợ cuối quý, chi nhánh cần khóa sổ trước 17 giờ.",
            "Không thể phủ nhận một điều rằng chi phí vận tải biển quý IV đã tăng 14,5%.",
            "Phòng kế toán bổ sung hai nhân sự với mục đích nhằm rút ngắn thời gian duyệt chứng từ.",
            (
                "Việc các bộ phận nghiệp vụ tại chi nhánh liên tục trì hoãn đối chiếu chứng từ gốc với sổ cái "
                "kế toán suốt ba tháng đã dẫn đến chênh lệch 420 triệu đồng."
            ),
        ):
            rep_rb = self.scanner.scan_text(roundabout_sample, profile="general")
            self.assertIn("VIS-LEN-001", {f.rule_id for f in rep_rb.findings}, roundabout_sample)

        legal_44w = (
            "Căn cứ Điều 301 Luật Thương mại năm 2005, mức phạt đối với vi phạm nghĩa vụ hợp đồng "
            "hoặc tổng mức phạt đối với nhiều vi phạm do các bên thỏa thuận, nhưng không quá 8% giá trị "
            "nghĩa vụ bị vi phạm."
        )
        self.assertEqual(self.scanner.scan_text(legal_44w, profile="legal").findings_count, 0)
        self.assertEqual(self.scanner.scan_text(legal_44w, profile="general").error_count, 1)
        rep_legal_all = self.scanner.scan_text(legal_44w, profile="all")
        self.assertIn("legal", rep_legal_all.findings[0].exempt_profiles)

        legal_50w = (
            "Căn cứ Điều 301 Luật Thương mại năm 2005, mức phạt đối với vi phạm nghĩa vụ hợp đồng hoặc tổng mức "
            "phạt đối với nhiều vi phạm do các bên thỏa thuận trong hợp đồng, nhưng không quá 8% giá trị phần "
            "nghĩa vụ hợp đồng bị vi phạm trong kỳ thanh toán."
        )
        self.assertEqual(self.scanner.scan_text(legal_50w, profile="legal").error_count, 1)

    def test_table_cell_length_and_cli_hard_fail(self) -> None:
        """Câu vượt 35 từ trong văn xuôi hoặc ô bảng phải làm cả `scan` lẫn `profile` trả mã lỗi 1 ngay."""
        prose_38w = (
            "Đoàn kiểm toán nội bộ rà soát hồ sơ tín dụng tại sáu chi nhánh khu vực miền Trung trong quý hai "
            "để đối chiếu chứng từ giải ngân thực tế với báo cáo sao kê tài khoản thanh toán."
        )
        self.assertEqual(self.scanner.scan_text(prose_38w, profile="audit_report").error_count, 1)

        bad_table = (
            f"Số liệu đã khóa.\n\n| Hạng mục | Nhận định chi tiết |\n| :--- | :--- |\n| Tín dụng | {prose_38w} |\n"
        )
        rep_tbl = self.scanner.scan_text(bad_table, profile="audit_report")
        self.assertIn("VIS-LEN-001", {f.rule_id for f in rep_tbl.findings})
        self.assertTrue(any("> 35 từ" in w for w in profile_text(bad_table)["stylometry"]["canh_bao"]))

        clean_table = (
            "Đã khóa sổ.\n\n"
            "| Cột 1 | Cột 2 | Cột 3 | Cột 4 |\n| :--- | :--- | :--- | :--- |\n"
            "| Chi nhánh Hà Nội khớp đủ 120 hồ sơ gốc. | Đà Nẵng khớp đủ 85 chứng từ kho quỹ. "
            "| Cần Thơ hoàn tất đối chiếu 64 tài khoản. "
            "| • Đã thu đủ 12 hồ sơ gốc<br>• Đã ký biên bản bàn giao kho quỹ<br>"
            "• Đã lưu trữ bản quét trên hệ thống |\n"
        )
        docx_bullet_row = (
            "| 1 | • Đã thu đủ 12 hồ sơ gốc; • Đã ký biên bản kho quỹ; • Đã lưu trữ bản quét trên hệ thống |\n"
        )
        self.assertEqual(self.scanner.scan_text(clean_table, profile="all").findings_count, 0)
        self.assertEqual(self.scanner.scan_text(docx_bullet_row, profile="audit_report").findings_count, 0)
        self.assertFalse(any("> 35 từ" in w for w in profile_text(clean_table)["stylometry"]["canh_bao"]))

        with tempfile.TemporaryDirectory() as tmp:
            bad_md = Path(tmp) / "overlong.md"
            bad_md.write_text(bad_table, encoding="utf-8")
            ok_md = Path(tmp) / "clean.md"
            ok_md.write_text(clean_table, encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(main(["scan", str(bad_md), "--fail-on", "error"]), 1)
                self.assertEqual(main(["profile", str(bad_md), "--json"]), 1)
                self.assertEqual(main(["scan", str(ok_md)]), 0)
                self.assertEqual(main(["profile", str(ok_md), "--json"]), 0)

    def test_generalized_tone002_lex001_and_unblocked_metaphors(self) -> None:
        """Kiểm tra họ quy tắc tổng quát `VIS-TONE-002`, `VIS-LEX-001` và ẩn dụ bắt ngay `1/doc`."""
        pos_cases = (
            ("VIS-TONE-002", "audit_report", "### 4. Lỗi tồn đọng: phát lộ thêm lỗ hổng chốt chặn số dư", "phát lộ"),
            ("VIS-TONE-002", "general", "Hai đợt diễn tập hé lộ thêm sai lệch phân quyền.", "cho thấy"),
            ("VIS-TONE-002", "audit_report", "Đợt kiểm thử liên tục sập kết nối API và sập RestAPI.", "sập"),
            ("VIS-TONE-002", "general", "Tỷ lệ đạt giậm chân tại chỗ với vỏn vẹn 04/30 chỉ tiêu.", "giậm chân"),
            ("VIS-LEX-001", "audit_report", "Tiến độ cập nhập báo cáo sát nhập vẫn dậm chân ở mức 15%.", "cập nhật"),
            ("VIS-LEX-001", "general", "Nhóm hiện thực giao thức theo hợp đồng API và cọ sát thực tiễn.", "implement"),
            ("VIS-RHET-003", "audit_report", "Quy trình này là kim chỉ nam và viên đá tảng của đơn vị.", "ẩn dụ"),
            ("VIS-CLICHE-004", "general", "Giải pháp không màu mè cho đội vận hành kho.", ""),
        )
        for rid, prof, text, hint_sub in pos_cases:
            hits = [f for f in self.scanner.scan_text(text, profile=prof).findings if f.rule_id == rid]
            self.assertTrue(hits, f"Bỏ sót {rid} trên: {text}")
            if hint_sub:
                self.assertIn(hint_sub, hits[0].suggestion_vi.casefold())

        neg_cases = (
            ("marketing", "Hãng xe vừa hé lộ mẫu sedan điện mới cho mùa lễ hội."),
            ("social_media", "Phiên bản thử nghiệm mới lộ diện sáng nay trên diễn đàn."),
            ("audit_report", "Đợt diễn tập làm bộc lộ rõ rủi ro lộ mã tài sản liên đơn vị."),
            ("audit_report", "Tài khoản thanh toán đang bị đóng băng theo yêu cầu phong tỏa."),
            ("academic", "Nghiên cứu phân tích cuộc khủng hoảng tài chính năm 2008."),
            ("general", "Tảng đá ngầm trồi lên mặt nước sau đợt sập giàn giáo bến cảng."),
            ("legal", "Các bên ký hợp đồng dịch vụ dựa trên khung pháp lý hiện hành."),
            ("audit_report", "Quản trị viên mở khóa tài khoản sau khi xác minh nguyên nhân cốt lõi."),
        )
        for prof, text in neg_cases:
            rep = self.scanner.scan_text(text, profile=prof)
            self.assertEqual(rep.findings_count, 0, f"Bắt nhầm ({prof}): {text} -> {rep.findings}")


class TestViScannerSupersetAndDocx(unittest.TestCase):
    scanner: ClassVar[ViScanner]

    @classmethod
    def setUpClass(cls) -> None:
        cls.scanner = ViScanner()

    def test_v2_1_superset_viet_humanize_and_technical_calques(self) -> None:
        """Kiểm tra 18 chỉ số stylometry, từ dịch can kỹ thuật, xoay vòng động từ bảng và chú thích cây thư mục."""
        sample_doc = (
            '<img src="a.svg" alt="Giao diện terminal của ứng dụng hiển thị kết quả quét '
            'dải mạng nội bộ và trạng thái cổng TCP trên 5 thiết bị">\n'
            "<table><tr><td><b>01</b> A</td><td><b>02</b> B</td></tr>"
            "<tr><td><b>03</b> C</td><td><b>04</b> D</td></tr></table>\n\n"
            "Hệ thống áp dụng khung hợp đồng cho các phân hệ.\n"
            "Nhóm thiết lập khung vận hành cho toàn bộ dịch vụ và không cần cài thêm thư viện ngoài.\n"
            "Trưởng nhóm khóa hợp đồng kèm khung chạy sẵn và hỗ trợ lọc dữ liệu.\n"
            "Tài liệu docs/architecture.md mô tả chi tiết cấu trúc, còn ADR-0001 ghi lại lý do chọn.\n\n"
            "```text\nproject/\n"
            "└── include/  # Các tệp khai báo lớp và giao kèo dữ liệu dùng chung giữa 5 thành viên trong nhóm\n```\n\n"
            "| Mã | Công việc lập trình |\n| --- | --- |\n| TV1 | Khóa tệp header chung |\n"
            "| TV2 | Xây dựng lớp thiết bị |\n| TV3 | Hiện thực lớp kiểm tra |\n"
            "| TV4 | Lập trình bộ quét mạng |\n| TV5 | Phát triển phần lưu trữ |\n"
        )
        rep = self.scanner.scan_text(sample_doc, profile="all")
        self.assertEqual(len(rep.stylometry), 18)
        rule_ids = {f.rule_id for f in rep.findings}
        for rid in ("VIS-LEX-001", "VIS-TRANS-005", "VIS-STRUCT-001", "VIS-FMT-005", "VIS-STRUCT-002"):
            self.assertIn(rid, rule_ids)
        matched_all = " | ".join(f.matched_text for f in rep.findings)
        for phrase in (
            "khung hợp đồng",
            "khung vận hành",
            "khóa hợp đồng",
            "giao kèo dữ liệu",
            "hỗ trợ lọc",
            "ghi lại lý do chọn",
            "Xoay vòng động từ",
        ):
            self.assertIn(phrase, matched_all)

    def test_v2_2_dhdna_evidence_and_gatekeeper_profile(self) -> None:
        """Kiểm tra các quy tắc kỷ luật bằng chứng DHDNA và phân loại giọng `DIRECT_EXECUTIVE_GATEKEEPER`."""
        bad_evidence_doc = (
            "Sự cố lúc 10:40 gây sập toàn tuyến khi đội ngũ trực chiến 24/7.\n\n"
            "Trong mẫu khảo sát, 84,9% giao dịch được ghi nhận hoàn thành, kể cả trường hợp còn vướng mắc.\n\n"
            "Nhóm hỗ trợ đã đóng lỗi bằng cách hướng dẫn lại thao tác trên bảng theo dõi.\n\n"
            "Có 06 bút toán lệch tự triệt tiêu nhau nên tổng chênh lệch bằng 0.\n\n"
            "Tỷ lệ hoàn thành chung đạt 91,5%.\n"
        )
        rep_ev = self.scanner.scan_text(bad_evidence_doc, profile="audit_report")
        self.assertIn("VIS-TONE-001", [f.rule_id for f in rep_ev.findings])
        self.assertGreaterEqual(sum(1 for f in rep_ev.findings if f.rule_id == "VIS-STRUCT-002"), 4)

        gatekeeper_doc = (
            "Đến ngày 30/09/2026, dự án chưa đủ cơ sở phê duyệt đưa vào vận hành chính thức.\n\n"
            "Thực trạng và bằng chứng. Có 3.009/6.196 nội dung đạt yêu cầu, tương đương 48,6%. "
            "Đây là số liệu do đơn vị tự báo cáo, chưa được kiểm tra độc lập. "
            "Ở trang sau, bảng tổng hợp lại ghi 3.100/7.477 nội dung đạt yêu cầu.\n\n"
            "Giới hạn của kết luận. Các trạng thái họp bàn hoặc đang trình chỉ phản ánh tiến độ, "
            "mới dừng ở hoạt động trung gian và không được xem là hoàn thành khi chưa có đầu ra kiểm chứng. "
            "Hiện còn 12 hạng mục quá hạn 62 ngày.\n\n"
            "Kiến nghị kiểm toán. Chỉ phê duyệt vận hành khi đóng hết lỗi nghiêm trọng. "
            "Nếu điều kiện chặn chưa đạt trước 48 giờ, cần giảm phạm vi hoặc dời ngày vận hành "
            "vì khách hàng có thể bị tính sai số dư.\n"
        )
        prof = profile_text(gatekeeper_doc, label="gatekeeper_sample")
        self.assertEqual(prof["voice_archetype"]["code"], "DIRECT_EXECUTIVE_GATEKEEPER")
        dm = prof["dhdna_voice_metrics"]
        self.assertGreaterEqual(dm["ranh_gioi_bang_chung_d12"], 2)
        self.assertGreaterEqual(dm["cong_chan_dieu_kien_d6"], 2)
        self.assertGreaterEqual(dm["tach_hoat_dong_trung_gian_d1"], 2)
        self.assertGreaterEqual(dm["neo_thoi_gian_tre_han_d11"], 2)
        self.assertGreaterEqual(dm["nhan_doan_ket_thuc_dau_cham"], 3)
        self.assertEqual(dm["ung_vien_lech_mau_so"].get("nội dung"), ["6.196", "7.477"])

    @staticmethod
    def _write_sample_docx(docx_path: Path) -> None:
        core_xml = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
            'xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/">'
            "<dc:title>Báo cáo tổng hợp diễn tập Đợt 2</dc:title>"
            "<dc:creator>Kiểm toán viên</dc:creator></cp:coreProperties>"
        )
        doc_xml = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>'
            '<w:p><w:pPr><w:pStyle w:val="Heading1"/></w:pPr>'
            "<w:r><w:t>Báo cáo giám sát diễn tập Đợt 6</w:t></w:r></w:p>"
            "<w:p><w:r><w:t>Có 138/213 đơn vị gửi báo cáo đánh giá đúng hạn, tương đương 64,8%.</w:t></w:r></w:p>"
            "<w:tbl><w:tr>"
            "<w:tc><w:p><w:r><w:t>STT</w:t></w:r></w:p></w:tc>"
            "<w:tc><w:p><w:r><w:t>Báo cáo đơn vị</w:t></w:r></w:p></w:tc>"
            "<w:tc><w:p><w:r><w:t>Nhận định độc lập</w:t></w:r></w:p></w:tc>"
            "</w:tr><w:tr>"
            "<w:tc><w:p><w:r><w:t>1</w:t></w:r></w:p></w:tc>"
            "<w:tc><w:p><w:r><w:t>Đã thực hiện kiểm tra -> dùng workaround</w:t></w:r></w:p></w:tc>"
            "<w:tc><w:p><w:r><w:t>Quá hạn 15 ngày, chưa có đầu ra kiểm chứng.</w:t></w:r></w:p></w:tc>"
            "</w:tr></w:tbl></w:body></w:document>"
        )
        with zipfile.ZipFile(docx_path, "w") as zf:
            zf.writestr("docProps/core.xml", core_xml)
            zf.writestr("word/document.xml", doc_xml)

    def test_v2_2_docx_template_mismatch_and_ignore_cols(self) -> None:
        """Kiểm tra đọc tệp `.docx`, phát hiện lệch kỳ `Title` và lọc cột bảng `--ignore-table-cols`."""
        with tempfile.TemporaryDirectory() as tmp:
            docx_path = Path(tmp) / "sample_report.docx"
            self._write_sample_docx(docx_path)

            txt_ig, meta = extract_docx_text_and_meta(docx_path, ignore_cols={2})
            self.assertIsNotNone(meta["template_title_mismatch"])
            self.assertNotIn("workaround", txt_ig)

            out_scan = Path(tmp) / "scan_docx.json"
            cli_args = [
                "scan",
                str(docx_path),
                "--profile",
                "audit_report",
                "--ignore-table-cols",
                "2",
                "--fail-on",
                "never",
                "--json",
                "--output",
                str(out_scan),
            ]
            with contextlib.redirect_stdout(io.StringIO()):
                rc_scan = main(cli_args)
            self.assertEqual(rc_scan, 0)
            scan_data = json.loads(out_scan.read_text(encoding="utf-8"))
            self.assertEqual(scan_data["findings_count"], 1)
            self.assertGreater(scan_data["weighted_density_score"], 0.0)
            self.assertEqual(scan_data["category_breakdown"], {"VOICE_AND_STRUCTURE": 1})
            self.assertIn("Đợt 2", scan_data["findings"][0]["matched_text"])

    def test_extended_41_rules_and_vocab_trie_gates(self) -> None:
        """Kiểm tra 10 quy tắc mở rộng, cụm thống kê theo đoạn và bộ lọc ngữ cảnh Hán-Việt / khẩu hiệu."""
        new_rule_samples = (
            ("VIS-AI-006", "Hãy thử tưởng tượng một hệ thống tự khóa sổ mỗi tối mà không cần đối chiếu."),
            ("VIS-AI-007", "Dù bạn là sinh viên, nhân viên hay lãnh đạo, bạn đều dùng được biểu mẫu này."),
            ("VIS-RHET-006", "Hơn cả một bảng tính, đây là người bạn đồng hành của phòng tài chính."),
            ("VIS-RHET-007", "Tưởng chừng chỉ là sai lệch nhỏ, nhưng đó là cảnh báo cho toàn bộ quy trình."),
            ("VIS-FMT-006", "Không ngoại lệ. Không trì hoãn. Không thỏa hiệp."),
            ("VIS-TRANS-006", "Kết quả của đợt kiểm tra của bộ phận vận hành của chi nhánh đã có."),
            ("VIS-TRANS-007", "Mặc dù chứng từ đã khớp nhưng kế toán vẫn rà lại thêm một lượt."),
            ("VIS-TRANS-008", "Đề xuất đến từ nhóm vận hành giúp giảm 15% thời gian chờ."),
            ("VIS-TRANS-009", "Biểu mẫu nằm trong ngăn lưu trữ bên trong tủ hồ sơ tầng hai."),
            ("VIS-TRANS-010", "Báo cáo mang tính chiến lược và mang tính định hướng cho năm 2027."),
        )
        for expected_rid, text in new_rule_samples:
            found = {f.rule_id for f in self.scanner.scan_text(text, profile="general").findings}
            self.assertIn(expected_rid, found, f"Bỏ sót {expected_rid} trên mẫu: {text}")

        self.assertEqual(
            self.scanner.scan_text(new_rule_samples[0][1], profile="marketing").findings_count,
            0,
        )
        self.assertEqual(
            self.scanner.scan_text(new_rule_samples[4][1], profile="audit_report").findings_count,
            0,
        )
        self.assertEqual(
            self.scanner.scan_text(
                "Tuy nhiên, 138/213 đơn vị của doanh nghiệp đã khóa sổ kế toán.", profile="general"
            ).findings_count,
            0,
        )
        clustered_adj = "Phương án mới linh hoạt, bền vững và tối ưu cho dây chuyền đóng gói."
        fmt_hits = [
            f for f in self.scanner.scan_text(clustered_adj, profile="general").findings if f.rule_id == "VIS-FMT-004"
        ]
        self.assertEqual(len(fmt_hits), 1)
        self.assertEqual(fmt_hits[0].matched_text, "linh hoạt, bền vững và tối ưu")
        convert_sample = "Bất quá nhân gia chỉ là một cái kế toán mới vào doanh nghiệp làm việc."
        conv_findings = [
            f
            for f in self.scanner.scan_text(convert_sample, profile="translation").findings
            if f.rule_id == "VIS-LEX-001"
        ]
        self.assertGreaterEqual(len(conv_findings), 1)
        self.assertNotRegex(conv_findings[0].suggestion_vi, r"\d+\)")

    def test_match_description_suggestion_coherence(self) -> None:
        """Đảm bảo `matched_text`, `description_vi` và `suggestion_vi` khớp nhau trên mọi nhánh quy tắc."""
        f_semi = self.scanner.scan_text("Chi nhánh đã khóa sổ; chứng từ gốc đã lưu kho.", profile="general").findings[0]
        self.assertIn("chấm phẩy", f_semi.suggestion_vi)
        f_dash = self.scanner.scan_text("Dự án này — vốn kéo dài hai quý — đã hoàn tất.", profile="general").findings[0]
        self.assertIn("gạch ngang", f_dash.suggestion_vi)

        f_rb = self.scanner.scan_text(
            "Liên quan đến vấn đề đối chiếu công nợ, chi nhánh khóa sổ lúc 17 giờ.", profile="general"
        ).findings[0]
        self.assertNotIn("tách thành 2–3 câu", f_rb.suggestion_vi)
        long_plain = (
            "Đoàn kiểm toán rà soát hồ sơ vay vốn của khách hàng doanh nghiệp tại sáu chi nhánh miền Trung "
            "trong quý hai để đối chiếu chứng từ giải ngân thực tế với báo cáo sao kê ngân hàng thương mại "
            "và biên bản nghiệm thu kho bãi của đơn vị."
        )
        f_long = next(
            f for f in self.scanner.scan_text(long_plain, profile="general").findings if f.rule_id == "VIS-LEN-001"
        )
        self.assertIn("tách thành 2–3 câu", f_long.suggestion_vi)
        self.assertNotIn("rào đón", f_long.suggestion_vi)

        rep_fmt2 = self.scanner.scan_text(self.scanner.rules["VIS-FMT-002"].bad_example, profile="general")
        hit_fmt2 = next(f for f in rep_fmt2.findings if f.rule_id == "VIS-FMT-002")
        self.assertIn(" ... ", hit_fmt2.matched_text)
        self.assertFalse(hit_fmt2.matched_text.startswith("."))

        checks = (
            ("Nguồn https://example.com?utm_source=chatgpt.com nhé.", "VIS-AI-002", "utm_source"),
            ("Bảng tính vô tình bỏ quên 3 giao dịch cuối ngày.", "VIS-TRANS-005", "vô tri"),
            ("Đơn vị thực hiện kiểm tra 20 hồ sơ giải ngân.", "VIS-CLICHE-002", "tiến hành/thực hiện"),
            ("Nhóm vận hành booking lịch họp với đối tác.", "VIS-LEX-002", "chêm từ ngoại lai"),
            ("Tác giả chắp bút bản thảo đầu tiên năm 2024.", "VIS-LEX-001", "chấp bút"),
        )
        for sample, rid, expected_sub in checks:
            hits = [f for f in self.scanner.scan_text(sample, profile="all").findings if f.rule_id == rid]
            self.assertTrue(hits, f"Thiếu {rid} trên mẫu: {sample}")
            self.assertIn(expected_sub, hits[0].suggestion_vi)

    def test_zero_false_positives_on_curated_vocab_edge_cases(self) -> None:
        """Không bắt nhầm cụm tiếng Việt tự nhiên sau khi chuẩn hóa toàn bộ 2.011 dòng `vocab.csv`."""
        clean_samples = (
            "Đoàn kiểm tra đọc kỹ hồ sơ từ đầu đến cuối trước khi ký biên bản.",
            "Các đơn vị xác nhận sẵn sàng vận hành hệ thống thanh toán mới.",
            "Bộ phận tiếp nhận 15 đơn từ khiếu nại và chạy một vòng đối soát trên bản nguyên bản.",
            "Đây là yếu điểm chiến lược trên tuyến giao thông huyết mạch phía Bắc.",
            "Số liệu phải tuyệt đối khớp. Đây là khâu trọng yếu của kỳ khóa sổ. Kế toán rà kỹ lưỡng từng dòng.",
        )
        for text in clean_samples:
            rep = self.scanner.scan_text(text, profile="all")
            self.assertEqual(rep.findings_count, 0, f"Bắt nhầm trên câu sạch: {text} -> {rep.findings}")
        bad_yd = self.scanner.scan_text("Đơn vị cần khắc phục yếu điểm lớn nhất trong khâu lưu trữ.", profile="all")
        self.assertIn("VIS-LEX-001", {f.rule_id for f in bad_yd.findings})


if __name__ == "__main__":
    unittest.main()
