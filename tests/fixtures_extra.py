# ruff: noqa: E501
"""Bộ mẫu bổ sung cho chín quy tắc mới (`TF-X-01` đến `TF-X-26`) và ngưỡng trình bày."""

from __future__ import annotations

from typing import TypeAlias

BenchmarkFixture: TypeAlias = tuple[str, str, str, bool, str]

# fmt: off
NEW_RULE_FIXTURES: tuple[BenchmarkFixture, ...] = (
    ("TF-X-01", "VIS-RHET-008", "general", True, "Thay vì chỉ dựa vào quảng cáo truyền thống, doanh nghiệp cần khai thác tiếp thị đa kênh. Điều này rất quan trọng vì doanh thu quý III đạt 450 tỷ đồng."),
    ("TF-X-02", "VIS-RHET-008", "academic", False, "Doanh nghiệp chuyển 40% ngân sách sang tiếp thị đa kênh. Doanh thu quý III đạt 450 tỷ đồng."),
    ("TF-X-03", "VIS-RHET-009", "general", True, "Mỗi phương pháp đều có điểm mạnh và điểm yếu riêng, nên lựa chọn nào cũng hợp lý. Việc bạn băn khoăn chính là minh chứng cho chiều sâu nội tâm hiếm có."),
    ("TF-X-04", "VIS-RHET-009", "marketing", False, "Bộ sưu tập mùa thu dùng vải lanh thoáng mát và có 5 màu cơ bản."),
    ("TF-X-05", "VIS-FMT-007", "general", True, "Huyện có 56.000 dân, từ đó khẳng định tiềm năng khu vực."),
    ("TF-X-06", "VIS-FMT-007", "general", False, "Huyện có 56.000 dân, tập trung 70% quanh khu công nghiệp dệt may."),
    ("TF-X-07", "VIS-FMT-008", "social_media", True, "Chi phí thuê bao rất thấp. Và phần tuyệt vời nhất? Bạn không cần biết lập trình."),
    ("TF-X-08", "VIS-FMT-008", "general", False, "Chi phí thuê bao thấp và nhân viên tự cài đặt được mà không cần biết lập trình."),
    ("TF-X-09", "VIS-STRUCT-003", "general", True, "## Tiến độ và tài liệu\n\n| Mốc | Trạng thái |\n| --- | --- |\n| G1 | Đang thực hiện |\n| G2 | Kế hoạch |\n| G3 | Ghép chu kỳ |\n| G4 | Kiểm chứng |"),
    ("TF-X-10", "VIS-STRUCT-003", "general", False, "## Trạng thái\n\nBản phát hành 2.3.0 đã chạy 120 bài kiểm thử."),
    ("TF-X-11", "VIS-TRANS-011", "general", True, "Chỗ ngồi phòng họp đã bị đặt xong. Cánh cửa xe bị đóng sầm lại."),
    ("TF-X-12", "VIS-TRANS-011", "legal", False, "Hồ sơ đề nghị cấp phép được thực hiện theo quy định tại Điều 43."),
    ("TF-X-13", "VIS-TRANS-012", "general", True, "Tôi cho bạn nộp học phí. Việc học đối với cậu ta mà nói rất quan trọng."),
    ("TF-X-14", "VIS-TRANS-012", "general", False, "Tôi nộp học phí cho bạn. Việc học rất quan trọng với cậu ta."),
    ("TF-X-15", "VIS-TRANS-013", "translation", True, "Vương phi Lan Lăng mặc niệm đích biểu tình, rồi thương tâm địa khóc rống."),
    ("TF-X-16", "VIS-TRANS-013", "translation", False, "Vương phi Lan Lăng giữ vẻ mặt lạnh lùng, rồi khóc nức nở."),
    ("TF-X-17", "VIS-TRANS-014", "translation", True, "Cái báo cáo mà trưởng phòng bảo ngày mai trước 9 giờ sáng phải nộp lên ban giám đốc sau khi rà soát lại toàn bộ số liệu tháng trước đã viết xong chưa?"),
    ("TF-X-18", "VIS-TRANS-014", "translation", False, "Cậu viết xong bản báo cáo chưa? Trưởng phòng dặn nộp cho ban giám đốc trước 9 giờ sáng mai."),
    ("TF-X-23", "VIS-AI-003", "general", True, "Sự bùng nổ của trí tuệ nhân tạo trong những năm gần đây khiến chi phí hạ tầng tăng."),
    ("TF-X-24", "VIS-AI-004", "general", True, "Khi nói đến chuyển đổi số, nhiều đơn vị bỏ qua dữ liệu gốc."),
)

PRESENTATION_FIXTURES: tuple[BenchmarkFixture, ...] = (
    ("TF-X-19", "VIS-STRUCT-002", "general", True, 'Ảnh minh họa giao diện công cụ. <img src="a.svg" alt="Giao diện terminal của ứng dụng hiển thị kết quả quét dải mạng nội bộ và trạng thái cổng TCP trên năm thiết bị">'),
    ("TF-X-20", "VIS-STRUCT-002", "general", False, 'Ảnh minh họa giao diện công cụ. <img src="a.svg" alt="Giao diện Network Monitor">'),
    ("TF-X-21", "VIS-STRUCT-002", "general", True, 'Ảnh minh họa luồng xử lý.\n\n```mermaid\nflowchart LR\n  A -->|"User commands and callbacks through the whole terminal interface"| B\n```'),
    ("TF-X-22", "VIS-STRUCT-002", "general", False, 'Ảnh minh họa luồng xử lý.\n\n```mermaid\nflowchart LR\n  A -->|"User actions"| B\n```'),
    ("TF-X-25", "VIS-STRUCT-002", "general", True, 'Ảnh minh họa luồng xử lý.\n\n```mermaid\nflowchart LR\n  A -->|Nhãn cạnh rất dài gồm nhiều từ mô tả toàn bộ luồng| B\n```'),
    ("TF-X-26", "VIS-STRUCT-002", "general", False, 'Ảnh minh họa. <img src="a.svg" alt="Sơ đồ luồng dữ liệu - bản 2">'),
)
# fmt: on
