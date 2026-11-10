# Lịch sử phiên bản (Changelog)

Mọi thay đổi đáng chú ý của dự án được ghi nhận tại tệp này theo định dạng [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) và quy tắc đánh số phiên bản [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-11-10

### Thêm mới (Added)

- Chuẩn hóa repo thành gói kỹ năng đa nền tảng (`SKILL.md`, `AGENTS.md`, `package.json`, `.claude-plugin/`, `.cursor-plugin/`, `evals/evals.json`).
- Mở rộng công cụ [scripts/vi_scanner.py](scripts/vi_scanner.py) lên 30 quy tắc chia thành 6 nhóm (`VIS-AI`, `VIS-RHET`, `VIS-FMT`, `VIS-TRANS`, `VIS-CLICHE` cùng nhóm `VIS-LEX`, `VIS-TONE`, `VIS-STRUCT`).
- Hỗ trợ 7 nhóm văn bản (`general`, `audit_report`, `academic`, `legal`, `marketing`, `social_media`, `translation`) với chế độ quét mặc định `--profile all` xuất đủ 100% tín hiệu kèm danh sách nhóm áp dụng và nhóm miễn trừ.
- Bổ sung lớp che chắn vùng không quét (`SemanticMasker`) giữ nguyên tọa độ dòng và cột cho khối code, mã nội dòng, đường dẫn liên kết và câu trích dẫn trong ngoặc kép.
- Bổ sung lệnh `verify` kiểm tra bảo toàn 6 nhóm dữ kiện (số liệu, phủ định, điều kiện, mức chắc chắn, đường dẫn và nguồn trích dẫn) cùng lệnh `check-maintenance` nhắc lịch rà soát từ mượn định kỳ.
- Thiết lập quy trình kiểm thử tự động [ci.yml](.github/workflows/ci.yml) trên Ubuntu, macOS và Windows cùng bộ hơn 100 mẫu kiểm thử độc lập tại [tests/test_vi_scanner.py](tests/test_vi_scanner.py).

### Thay đổi (Changed)

- Gỡ bỏ toàn bộ hằng số gắn cứng theo dự án riêng lẻ; chỉ duy trì hai tập từ tiếng Anh đã quen dùng (`UNIVERSAL_NATURALIZED_LOANWORDS` và `WORKPLACE_TECH_LOANWORDS`) kèm cơ chế nạp quy tắc ngoài qua `--custom-rules`.
- Viết lại toàn bộ biểu thức chính quy theo hướng khớp một lượt, ngăn lỗi treo máy trên văn bản dài.
