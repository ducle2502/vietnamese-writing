# Lịch sử phiên bản (Changelog)

Mọi thay đổi đáng chú ý của dự án được ghi nhận tại tệp này theo định dạng [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) và quy tắc đánh số phiên bản [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.2.0] - 2026-11-10

### Thêm mới (Added)

- Bổ sung lệnh `profile` trong [scripts/vi_scanner.py](scripts/vi_scanner.py). Lệnh này đo tất định 18 chỉ số nhịp câu (`stylometry`), 12 chỉ số kỷ luật lập luận theo khung `DHDNA v2.0`, bộ dò xung đột mẫu số (`ung_vien_lech_mau_so`) và nhận diện tự động 4 kiểu giọng văn chức năng.
- Bổ sung trình đọc trực tiếp tệp Word `.docx` bằng thư viện chuẩn (`zipfile` + `xml.etree.ElementTree`). Hỗ trợ cờ `--ignore-table-cols` để loại trừ cột bảng trích lục của bên thứ ba và kiểm tra lỗi sót tiêu đề kỳ cũ (`template_title_mismatch`).
- Bổ sung các kiểm tra tất định về kỷ luật số liệu và bằng chứng trong `VIS-STRUCT-002` và `VIS-TONE-001`. Công cụ phát hiện lỗi gộp mục còn lỗi vào tỷ lệ hoàn thành, đóng lỗi bằng hướng dẫn trung gian, dùng bù trừ ròng kết luận không sai lệch, chốt tỷ lệ hoàn thành thiếu `Tử số/Mẫu số` và từ ngữ kịch tính hiện trường.
- Thêm tài liệu [references/voice-and-argument-patterns.md](references/voice-and-argument-patterns.md) tổng hợp 4 kiểu giọng văn chức năng, 6 kỷ luật dẫn số liệu và bảng chuyển ngữ quản trị.

## [2.1.0] - 2026-11-10

### Thêm mới (Added)

- Tích hợp 100% tập mẫu P0/P1/P2 và 18 chỉ số nhịp học (`stylometry`) của `viet-humanize` vào báo cáo JSON của [scripts/vi_scanner.py](scripts/vi_scanner.py).
- Mở rộng `SemanticMasker` để quét bên trong bảng Markdown, bảng HTML và chú thích tiếng Việt sau dấu `#` trong cây thư mục (`├──`, `└──`). Tự động che phần tiếng Anh sau neo `<a id="english"></a>` trong tài liệu song ngữ.
- Bổ sung bộ nhận diện từ dịch can kỹ thuật (`khung hợp đồng`, `khung vận hành`, `khóa hợp đồng`, `giao kèo dữ liệu`, `khung chạy sẵn`, `hiện thực lớp`). Bắt thêm lỗi xoay vòng động từ đầu cột bảng (`VIS-FMT-005`), thuộc tính `alt` ảnh nhồi từ khóa, chú thích cây thư mục quá `10` từ, hộp HTML `01` đến `04` trùng lặp và bọc dấu nháy ngược quanh từ tiếng Việt thường (`VIS-STRUCT-002`).

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
