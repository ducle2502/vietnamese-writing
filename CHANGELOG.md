# Lịch sử phiên bản (Changelog)

Tệp này ghi lại các thay đổi chính của dự án theo chuẩn [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) và quy tắc đánh số phiên bản [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.3.0] - 2026-11-13

### Thêm mới (Added)

- Thêm chín quy tắc: `VIS-RHET-008`, `VIS-RHET-009`, `VIS-FMT-007`, `VIS-FMT-008`, `VIS-STRUCT-003`, `VIS-TRANS-011`, `VIS-TRANS-012`, `VIS-TRANS-013` và `VIS-TRANS-014`.
- Thêm cột `source_status` cho `grammar.csv` với ba giá trị `verified`, `missing`, `internal`, không tự gán `internal`.
- Bổ sung `references/pattern-bank.md` tổng hợp khuôn câu AI và dịch thô, mở rộng `references/voice-and-argument-patterns.md` với quy trình biên tập và sổ tay giọng văn.
- Phân loại giọng văn sinh thêm `MULTI_READER_ASSURANCE` khi có ít nhất `2` nhãn bằng chứng hoặc cấu trúc phân luồng người đọc.
- Thêm metric đếm nhãn bằng chứng và cấu trúc phân luồng người đọc vào hồ sơ DHDNA.

### Thay đổi (Changed)

- `BUREAUCRATIC_OR_MONOTONE_DRAFT` không còn là mã riêng, nhánh `CLEAN_GENERAL_VIETNAMESE` trả mã này trong `warnings`.
- Đặt trần `8` chữ cho `alt` và nhãn Mermaid, khuyến nghị `2–8` chữ.
- Bổ sung từ vựng AI, `convert` và ngữ cảnh kiểm toán, `vocab.csv` tăng lên `2.089` mục.

### Sửa lỗi (Fixed)

- Tách kiểm tra tiêu đề, `alt` và nhãn Mermaid khỏi các quy tắc văn xuôi để tránh dương tính giả.
- Bổ sung nguồn công khai cho tám rule từng thiếu `source_url`, giữ `missing` cho bốn rule chưa xác định được nguồn.

## [2.2.0] - 2026-11-10

### Thêm mới (Added)

- Bổ sung lệnh `profile` trong [scripts/vi_scanner.py](scripts/vi_scanner.py). Lệnh mới tính 18 chỉ số nhịp câu (`stylometry`), 12 chỉ số kỷ luật lập luận (`DHDNA v2.0`), phát hiện lệch mẫu số (`ung_vien_lech_mau_so`) và xếp loại 4 kiểu giọng văn chức năng.
- Bổ sung trình đọc tệp Word `.docx` bằng thư viện chuẩn (`zipfile` + `xml.etree.ElementTree`). Người dùng có thể truyền `--ignore-table-cols` để bỏ qua cột trích lục của bên thứ ba và kiểm tra lỗi sót tiêu đề kỳ trước (`template_title_mismatch`).
- Mở rộng `VIS-STRUCT-002` và `VIS-TONE-001` để rà kỷ luật số liệu và bằng chứng. Máy quét bắt lỗi gộp mục còn vướng mắc vào tỷ lệ hoàn thành, đóng lỗi bằng hướng dẫn trung gian và dùng bù trừ ròng kết luận khớp đúng. Bộ quét cũng chặn lỗi chốt tỷ lệ thiếu `Tử số/Mẫu số` và từ kịch tính hiện trường.
- Bổ sung quy tắc `VIS-TONE-002` bắt họ động từ điều tra/cổ văn (`phát lộ`, `phát giác`, `bại lộ`, `vạch trần`) và mẫu câu kịch tính hóa sự cố hoặc con số (`sập API`, `vỏn vẹn`, `giậm chân tại chỗ`).
- Khái quát hóa khung ngữ pháp dịch từng chữ của `VIS-LEX-001` (`hiện thực + <danh từ>`, `khung + <danh từ>`, `hợp đồng/giao kèo + <danh từ>`) và bổ sung họ lỗi chính tả công sở (`cập nhập`, `sát nhập`, `dậm chân`, `xoay sở`, `xuất sứ`).
- Thêm [references/voice-and-argument-patterns.md](references/voice-and-argument-patterns.md) tổng hợp 4 kiểu giọng văn chức năng, 6 kỷ luật dẫn số liệu và bảng chuyển ngữ quản trị.

### Thay đổi (Changed)

- Hạ trần độ dài câu `VIS-LEN-001` xuống `35` từ (`45` từ với văn bản pháp lý) và quét cả câu trong ô bảng. Cả hai lệnh `scan` và `profile` đều trả mã lỗi `1` ngay khi gặp câu vượt ngưỡng.

### Sửa lỗi (Fixed)

- Gỡ ngưỡng gom cụm ẩn (`>= 3` lần/đoạn) trên các ẩn dụ dịch sát không mơ hồ của `VIS-RHET-002`, `VIS-RHET-003`, `VIS-CLICHE-002` và `VIS-CLICHE-004` để bắt ngay từ lần xuất hiện đầu tiên.
- Chuẩn hóa `2.057` mục từ tại [data/vocab.csv](data/vocab.csv), mở rộng kiểm tra lặp từ sát nhau, tiêu đề dịch từng chữ và chuyển kiểm tra giới hạn mã sang `pytest` tại [tests/test_code_limits.py](tests/test_code_limits.py). Gợi ý `suggestion_vi` nay khớp trực tiếp với từng nhánh biểu thức chính quy, cụm lặp vượt ngưỡng và bộ 3 tính từ khen ngợi.

## [2.1.0] - 2026-11-10

### Thêm mới (Added)

- Tích hợp 100% tập mẫu P0/P1/P2 và 18 chỉ số nhịp câu (`stylometry`) của `viet-humanize` vào báo cáo JSON của [scripts/vi_scanner.py](scripts/vi_scanner.py).
- Mở rộng `SemanticMasker` để quét bên trong bảng Markdown, bảng HTML và chú thích tiếng Việt sau dấu `#` trong cây thư mục (`├──`, `└──`), đồng thời tự che phần tiếng Anh sau neo `<a id="english"></a>` trong tài liệu song ngữ.
- Bổ sung bộ nhận diện cụm dịch từng chữ trong tài liệu kỹ thuật (`khung hợp đồng`, `khung vận hành`, `khóa hợp đồng`, `giao kèo dữ liệu`, `khung chạy sẵn`, `hiện thực lớp`). Máy quét kiểm tra thêm lỗi xoay vòng động từ đầu cột bảng (`VIS-FMT-005`), thuộc tính `alt` ảnh nhồi từ khóa, chú thích cây thư mục quá `10` từ, hộp HTML `01` đến `04` trùng lặp và bọc dấu nháy ngược quanh từ tiếng Việt thường (`VIS-STRUCT-002`).

## [2.0.0] - 2026-11-10

### Thêm mới (Added)

- Chuẩn hóa repo thành gói kỹ năng đa nền tảng (`SKILL.md`, `AGENTS.md`, `package.json`, `.claude-plugin/`, `.cursor-plugin/`, `evals/evals.json`).
- Mở rộng công cụ [scripts/vi_scanner.py](scripts/vi_scanner.py) lên 30 quy tắc chia thành 6 nhóm (`VIS-AI`, `VIS-RHET`, `VIS-FMT`, `VIS-TRANS`, `VIS-CLICHE` cùng nhóm `VIS-LEX`, `VIS-TONE`, `VIS-STRUCT`).
- Hỗ trợ 7 nhóm văn bản (`general`, `audit_report`, `academic`, `legal`, `marketing`, `social_media`, `translation`) với chế độ quét mặc định `--profile all` xuất đủ 100% tín hiệu kèm danh sách nhóm áp dụng và nhóm không áp dụng.
- Bổ sung bộ tách riêng vùng không quét (`SemanticMasker`) giữ nguyên tọa độ dòng và cột cho khối code, mã nội dòng, đường dẫn liên kết và câu trích dẫn trong ngoặc kép.
- Bổ sung lệnh `verify` đối chiếu 6 nhóm dữ kiện gốc (số liệu, phủ định, điều kiện, mức chắc chắn, đường dẫn và nguồn trích dẫn) cùng lệnh `check-maintenance` nhắc lịch rà soát từ mượn định kỳ.
- Thiết lập quy trình kiểm thử tự động [ci.yml](.github/workflows/ci.yml) trên Ubuntu, macOS và Windows cùng bộ hơn 100 mẫu kiểm thử độc lập tại [tests/test_vi_scanner.py](tests/test_vi_scanner.py).

### Thay đổi (Changed)

- Gỡ bỏ toàn bộ hằng số ghi cố định theo dự án riêng lẻ, chỉ duy trì hai tập từ tiếng Anh đã quen dùng (`UNIVERSAL_NATURALIZED_LOANWORDS` và `WORKPLACE_TECH_LOANWORDS`) kèm cơ chế nạp quy tắc ngoài qua `--custom-rules`.
- Viết lại toàn bộ biểu thức chính quy theo hướng khớp một lượt, ngăn lỗi treo máy trên văn bản dài.
