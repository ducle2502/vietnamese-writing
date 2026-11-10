# Lịch sử phiên bản (Changelog)

Mọi thay đổi đáng chú ý của dự án được ghi nhận tại tệp này theo định dạng [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) và quy tắc đánh số phiên bản [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.0] - 2026-11-10

### Thêm mới (Added)

- Tích hợp trọn vẹn 100% tập mẫu P0/P1/P2 và 18 chỉ số nhịp học (`stylometry`) của `viet-humanize` vào báo cáo quét JSON của [scripts/vi_scanner.py](scripts/vi_scanner.py).
- Mở rộng `SemanticMasker` để quét xuyên vào bên trong bảng Markdown, bảng HTML và phần chú thích tiếng Việt sau dấu `#` trong cây thư mục (`├──`, `└──`), đồng thời tự động che phần tiếng Anh sau neo `<a id="english"></a>` trong tài liệu song ngữ.
- Bổ sung bộ nhận diện từ dịch can kỹ thuật (`khung hợp đồng`, `khung vận hành`, `khóa hợp đồng`, `giao kèo dữ liệu`, `khung chạy sẵn`, `hiện thực lớp`, `di chuyển vệt sáng`, `túi chứa dữ liệu`, `Kỹ sư giao thức mạng`), lỗi xoay vòng động từ đồng nghĩa đầu cột bảng (`VIS-FMT-005`), thuộc tính `alt` ảnh nhồi từ khóa (`> 12` từ), hộp HTML quảng cáo `01` đến `04` trùng lặp và lỗi bọc dấu nháy ngược quanh từ tiếng Việt thường (`VIS-STRUCT-002`).

## [2.0.0] - 2026-11-10

### Thêm mới (Added)

- Chuẩn hóa repo thành gói kỹ năng đa nền tảng (`SKILL.md`, `AGENTS.md`, `package.json`, `.claude-plugin/`, `.cursor-plugin/`, `evals/evals.json`).
- Mở rộng công cụ [scripts/vi_scanner.py](scripts/vi_scanner.py) lên 30 quy tắc chia thành 6 nhóm (`VIS-AI`, `VIS-RHET`, `VIS-FMT`, `VIS-TRANS`, `VIS-CLICHE` cùng nhóm `VIS-LEX`, `VIS-TONE`, `VIS-STRUCT`).
- Hỗ trợ 7 nhóm văn bản (`general`, `audit_report`, `academic`, `legal`, `marketing`, `social_media`, `translation`) với chế độ quét mặc định `--profile all` xuất đủ 100% tín hiệu kèm danh sách nhóm áp dụng và nhóm miễn trừ.
- Bổ sung lớp che chắn vùng không quét (`SemanticMasker`) giữ nguyên tọa độ dòng và cột cho khối code, mã nội dòng, đường dẫn liên kết và câu trích dẫn trong ngoặc kép.
- Bổ sung lệnh `verify` kiểm tra bảo toàn 6 nhóm dữ kiện (số liệu, phủ định, điều kiện, mức chắc chắn, đường dẫn và nguồn trích dẫn) cùng lệnh `check-maintenance` nhắc lịch rà soát từ mượn định kỳ.
- Thiết lập quy trình kiểm thử tự động [ci.yml](.github/workflows/ci.yml) trên Ubuntu, macOS và Windows cùng bộ hơn 100 mẫu kiểm thử độc lập tại [tests/test_vi_scanner.py](tests/test_vi_scanner.py).

### Thay đổi (Changed)

- Gỡ bỏ toàn bộ hằng số gắn cứng theo dự án riêng lẻ, chỉ duy trì hai tập từ tiếng Anh đã quen dùng (`UNIVERSAL_NATURALIZED_LOANWORDS` và `WORKPLACE_TECH_LOANWORDS`) kèm cơ chế nạp quy tắc ngoài qua `--custom-rules`.
- Viết lại toàn bộ biểu thức chính quy theo hướng khớp một lượt, ngăn lỗi treo máy trên văn bản dài.
