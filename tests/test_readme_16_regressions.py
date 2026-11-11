#!/usr/bin/env python3
"""Kiểm thử hồi quy khóa chặt 16 nhóm lỗi README cũ, các biến thể tổng quát hóa và ngữ cảnh đa nghĩa."""

from __future__ import annotations

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path
from typing import ClassVar

TESTS_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = TESTS_DIR.parent / "scripts"
for _dir in (str(SCRIPTS_DIR), str(TESTS_DIR)):
    if _dir not in sys.path:
        sys.path.insert(0, _dir)

from vi_scanner import ViScanner, main  # noqa: E402

_LEGACY_README_SNAPSHOT = (
    "## Tổng quan\n\n"
    "- **Bắt đúng cấu trúc dịch thô, câu dài vòng vo và khuôn mẫu máy móc.** "
    "Công cụ không cấm từ Hán - Việt máy móc. Thay vào đó, 42 quy tắc trong "
    "[scripts/vi_scanner.py](scripts/vi_scanner.py) chỉ ra câu rào đón chatbot, "
    'bị động dịch sát (*"được thực hiện bởi"*), danh từ hóa và nhãn in đậm lặp khuôn. '
    "Quy tắc `VIS-LEN-001` chặn cứng câu vượt `35` từ (`45` từ ở văn bản pháp lý) "
    "kể cả trong ô bảng, kèm gợi ý sửa sát từng nhánh lỗi.\n"
    "- **Quét đủ 100% tín hiệu kèm miễn trừ theo 7 ngữ cảnh.** "
    "Lệnh `scan` mặc định chạy ở chế độ `all` và xuất toàn bộ tín hiệu trên 7 nhóm văn bản "
    "(`general`, `audit_report`, `academic`, `legal`, `marketing`, `social_media`, `translation`). "
    "Nhờ hai trường `applicable_profiles` và `exempt_profiles` trên từng kết quả, "
    "câu bị động chuẩn mực trong hợp đồng pháp lý hoặc trích dẫn học thuật không bị ép sửa sai ngữ cảnh.\n"
    "- **Che chắn vùng mã lệnh và đối soát bảo toàn dữ kiện.** "
    "Lớp `SemanticMasker` bỏ qua khối code, mã nội dòng, đường dẫn URL và lời trích dẫn trong ngoặc kép "
    "mà vẫn giữ nguyên số dòng, số cột. Sau khi biên tập, lệnh `verify` đối chiếu bản gốc với bản sửa "
    "để chặn lỗi làm rơi con số, từ phủ định, điều kiện hoặc mức độ chắc chắn.\n"
    "- **Phân biệt từ mượn quen dùng với lối chêm từ lửng lơ.** "
    "Bộ lọc âm vị bắt từ tiếng Anh chêm giữa câu nhưng tự cho qua nhóm từ quen dùng "
    "(`email`, `web`, `file`, `video`, `team`, `deadline`, `server`, `kpi`). "
    "Lệnh `check-maintenance` tự động nhắc lịch rà soát danh sách này theo quý.\n"
    "- **Đọc trực tiếp tệp `.docx` và lập hồ sơ giọng văn (`DHDNA` & `Stylometry`).** "
    "Hai lệnh `scan` và `profile` đọc thẳng tệp Word `.docx` bằng thư viện chuẩn, "
    "cho phép dùng `--ignore-table-cols` để bỏ qua cột bảng trích lục của bên thứ ba. "
    "Máy quét cũng phát hiện lỗi sót tiêu đề kỳ cũ trong thuộc tính tệp (`template_title_mismatch`), "
    "cảnh báo lệch mẫu số giữa các trang và xếp loại giọng văn theo 4 mẫu chuẩn.\n\n"
    "Nếu muốn tải trực tiếp mã nguồn và chạy thử ngay công cụ quét bằng `Python 3.11+`:\n\n"
    "| Nhóm mã | Tên nhóm quy tắc | Số quy tắc | Lỗi câu chữ trọng tâm |\n"
    "|---|---|---|---|\n"
    "| `VIS-AI-001..007` | Tín hiệu sinh văn của AI | `7` | Câu rào đón/kết thúc kiểu chatbot, "
    'mở bài vĩ mô (*"Trong bối cảnh..."*), ép tưởng tượng giả định (*"Hãy thử tưởng tượng..."*), '
    'câu điều kiện bao sân (*"Dù bạn là..."*) và chỗ trống nhắc điền chưa xóa. |\n'
    "| `VIS-RHET-001..007` | Tu từ phóng đại và dàn ý lộ liễu | `7` | "
    'Cặp đòn bẩy (*"không chỉ... mà còn"*), đối lập giả kịch tính (*"tưởng chừng... nhưng"*), '
    'tự khen tầm vóc (*"đóng vai trò then chốt"*), ẩn dụ dịch sát và dẫn nguồn không tên. |\n'
    "| `VIS-TRANS-001..010` | Cấu trúc dịch sát từ tiếng Anh | `10` | "
    'Câu bị động dịch từ *by*, danh từ hóa, cặp liên từ sóng đôi lặp dày và lặp *"mang tính"*. |\n'
    "| `VIS-LEX` | Từ vựng và giọng văn | `7` | "
    "Chặn cứng câu dài quá `35` từ, chặn giọng giật gân và khẩu ngữ sồn sã (`rủi ro sát sườn`). |\n\n"
    "## Cách sử dụng dòng lệnh\n"
)

_USER_16_CASES: tuple[tuple[str, str], ...] = (
    (
        "01_lap_tu_gan_nhau",
        "Bắt đúng cấu trúc dịch thô, câu dài vòng vo và khuôn mẫu máy móc. Công cụ không cấm từ Hán - Việt máy móc.",
    ),
    ("02_bi_dong_dich_sat", "Công cụ chỉ ra câu rào đón và bị động dịch sát trong báo cáo."),
    ("03_nhan_in_dam_lap_khuon", "Tránh viết danh sách gắn nhãn in đậm lặp khuôn ở đầu dòng."),
    ("04_chan_cung", "Quy tắc này chặn cứng mọi câu vượt ngưỡng quy định."),
    ("05_sua_sat", "Báo cáo trả về gợi ý sửa sát từng nhánh lỗi cụ thể."),
    ("06_mien_tru", "Hệ thống quét đủ tín hiệu kèm miễn trừ theo từng ngữ cảnh."),
    ("07_chuan_muc", "Câu bị động chuẩn mực trong văn bản vẫn được giữ lại."),
    ("08_che_chan_doi_soat", "Che chắn vùng mã lệnh và đối soát bảo toàn dữ kiện sau khi sửa."),
    ("09_loi_chem_tu_lung_lo", "Bộ lọc phân biệt từ quen dùng với lối chêm từ lửng lơ."),
    ("10_ky_cu", "Máy quét phát hiện lỗi sót tiêu đề kỳ cũ trong thuộc tính tệp."),
    ("11_chay_thu_ngay", "Nếu muốn tải mã nguồn và chạy thử ngay công cụ trên máy cá nhân."),
    (
        "12_mo_bai_vi_mo_bao_san_nhac_dien",
        'Bắt mở bài vĩ mô ("Trong bối cảnh..."), ép tưởng tượng giả định ("Hãy thử tưởng tượng..."), '
        'câu điều kiện bao sân ("Dù bạn là...") và chỗ trống nhắc điền chưa xóa.',
    ),
    ("13_cap_don_bay_doi_lap_tam_voc", "Cặp đòn bẩy, đối lập giả kịch tính, tự khen tầm vóc."),
    ("14_lien_tu_song_doi_lap_day", "Tránh dùng cặp liên từ sóng đôi lặp dày trong đoạn văn."),
    ("15_son_sa", "Không dùng khẩu ngữ sồn sã trong báo cáo trình ban điều hành."),
    ("16_cach_su_dung_dong_lenh", "## Cách sử dụng dòng lệnh"),
)

_GENERALIZED_VARIANTS: tuple[str, ...] = (
    "Bản thảo viết rất vòng vo ở phần đầu. Nhóm biên tập vẫn diễn đạt vòng vo ở phần kết.",
    (
        "- **Mục một.** Câu thứ nhất đủ bốn từ.\n"
        "- **Mục hai.** Câu thứ hai đủ bốn từ.\n"
        "- **Mục ba.** Câu thứ ba đủ bốn từ."
    ),
    "Hệ thống khóa cứng tham số cấu hình và ép cứng định dạng đầu ra.",
    "Tài liệu hướng dẫn viết sát từng mục trong biểu mẫu.",
    "Các đoạn văn lặp đều cùng một kiểu mở câu.",
    "Số liệu đợt cũ và tháng cũ chưa được cập nhật lên bảng theo dõi.",
    "Mô-đun này che chắn khối dữ liệu nhạy cảm và kiểm tra bảo toàn ngữ nghĩa.",
    "Người viết cần tránh lối trộn từ và chêm tiếng Anh ngoại lai lửng lơ.",
    "Đoạn dẫn nhập mở đầu vĩ mô kèm khuôn bao sân và ô nhắc điền còn sót.",
    "Dự án này là bệ phóng và chất xúc tác cho quá trình mở rộng thị phần.",
    "Tải gói cài đặt để trải nghiệm ngay các tính năng mới.",
    "## Bảng nội dung\n\nNội dung chi tiết.",
    "## Các vấn đề đã biết\n\nDanh sách hạn chế.",
)

_CLEAN_COUNTERFACTUALS: tuple[tuple[str, str], ...] = (
    ("general", "Hợp đồng quy định rõ điều khoản miễn trừ trách nhiệm khi xảy ra sự kiện bất khả kháng."),
    ("general", "Cơ quan đại diện hưởng quyền miễn trừ ngoại giao và miễn trừ thuế theo điều ước quốc tế."),
    ("audit_report", "Đoàn kiểm toán đối chiếu hồ sơ theo Chuẩn mực Kiểm toán Việt Nam và chuẩn mực kế toán VAS 02."),
    ("audit_report", "Tỷ lệ đòn bẩy tài chính và đòn bẩy nợ của doanh nghiệp giảm từ 2,4 xuống 1,8 lần."),
    ("academic", "Thí nghiệm đo lực tác dụng lên cánh tay đòn bẩy theo nguyên lý đòn bẩy cơ học."),
    ("general", "Chủ nhà bước ra cổng đon đả chào hỏi sồn sã đoàn khách mới đến."),
    ("general", "Đội thi công đổ bê tông ép cứng nền đất và siết chặt ốc vít bản lề."),
    ("general", "Hệ thống tự động mở khóa tài khoản sau khi người dùng xác thực hai lớp."),
    ("marketing", "Khám phá ngay bộ sưu tập mùa thu với ưu đãi giảm 20% tại cửa hàng!"),
    (
        "audit_report",
        "Thực trạng và bằng chứng. Có 12/20 hồ sơ đạt yêu cầu (60%).\n\n"
        "Nguyên nhân kiểm soát. Đơn vị chưa đối chiếu chéo chứng từ gốc.\n\n"
        "Kiến nghị kiểm toán. Yêu cầu rà soát lại 8 hồ sơ còn thiếu trước ngày 30/11.",
    ),
)


class TestReadme16AndGeneralizedRootCauses(unittest.TestCase):
    scanner: ClassVar[ViScanner]

    @classmethod
    def setUpClass(cls) -> None:
        cls.scanner = ViScanner()

    def test_legacy_readme_snapshot_fails_all_reported_spots(self) -> None:
        """Bản chụp nguyên văn README cũ phải báo lỗi ở toàn bộ 16 nhóm vị trí đã nêu (>= 28 cảnh báo)."""
        rep = self.scanner.scan_text(_LEGACY_README_SNAPSHOT, profile="all")
        self.assertGreaterEqual(rep.warning_count, 28)
        matched = [f.matched_text.casefold() for f in rep.findings]
        expected_substrings = (
            "- **bắt đúng",
            "máy móc",
            "bị động dịch sát",
            "lặp khuôn",
            "chặn cứng",
            "sửa sát",
            "miễn trừ",
            "chuẩn mực",
            "che chắn vùng",
            "đối soát bảo toàn",
            "lối chêm từ",
            "kỳ cũ",
            "chạy thử ngay",
            "mở bài vĩ mô",
            "ép tưởng tượng giả định",
            "câu điều kiện bao sân",
            "chỗ trống nhắc điền",
            "cặp đòn bẩy",
            "đòn bẩy",
            "đối lập giả kịch tính",
            "tự khen tầm vóc",
            "liên từ sóng đôi",
            "lặp dày",
            "sồn sã",
            "## cách sử dụng dòng lệnh",
        )
        for exp in expected_substrings:
            self.assertTrue(any(exp in m for m in matched), f"Bỏ sót '{exp}' trên README cũ: {matched}")

    def test_each_of_16_user_cases_fails_cli_warning_gate(self) -> None:
        """Từng mẫu trong 16 lỗi người dùng nêu phải kích hoạt cảnh báo và trả mã thoát CLI bằng 1."""
        with tempfile.TemporaryDirectory() as tmp:
            sample_file = Path(tmp) / "case.md"
            for case_id, text in _USER_16_CASES:
                rep = self.scanner.scan_text(text, profile="general")
                self.assertGreaterEqual(rep.warning_count, 1, f"Mẫu {case_id} không sinh warning: {rep.findings}")
                sample_file.write_text(text + "\n", encoding="utf-8")
                with contextlib.redirect_stdout(io.StringIO()):
                    rc = main(["scan", str(sample_file), "--profile", "general", "--fail-on", "warning"])
                self.assertEqual(rc, 1, f"CLI không trả mã lỗi 1 cho {case_id}")

    def test_generalized_unseen_variants_and_clean_counterfactuals(self) -> None:
        """Các biến thể cùng họ gốc lỗi phải bị bắt và các ngữ cảnh chuyên môn hợp lệ phải sạch lỗi."""
        for variant in _GENERALIZED_VARIANTS:
            rep = self.scanner.scan_text(variant, profile="general")
            self.assertGreaterEqual(rep.warning_count, 1, f"Bỏ lọt biến thể tổng quát: {variant}")

        for prof, clean_text in _CLEAN_COUNTERFACTUALS:
            rep = self.scanner.scan_text(clean_text, profile=prof)
            self.assertEqual(rep.findings_count, 0, f"Báo nhầm ({prof}): {clean_text} -> {rep.findings}")


if __name__ == "__main__":
    unittest.main()
