<a id="top"></a>

<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./assets/banner-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="./assets/banner-light.svg">
  <img alt="vietnamese-writing" src="./assets/banner-dark.svg" width="100%">
</picture>

<br>

[![CI](https://github.com/ducle2502/vietnamese-writing/actions/workflows/ci.yml/badge.svg)](https://github.com/ducle2502/vietnamese-writing/actions/workflows/ci.yml) ![Python](https://img.shields.io/badge/python-3.11%2B-0969da?style=flat-square&labelColor=161b22) ![Rules](https://img.shields.io/badge/rules-41%20%286%20groups%29-3fb950?style=flat-square&labelColor=161b22) [![License](https://img.shields.io/badge/license-MIT-58a6ff?style=flat-square&labelColor=161b22)](./LICENSE)

[Tổng quan](#tổng-quan) · [Cài đặt nhanh](#cài-đặt-nhanh) · [6 nhóm quy tắc](#6-nhóm-quy-tắc-và-7-ngữ-cảnh-văn-bản) · [Dòng lệnh](#cách-sử-dụng-dòng-lệnh) · [Cấu trúc thư mục](#cấu-trúc-thư-mục) · [Giới hạn phạm vi](#giới-hạn-phạm-vi)

</div>

**vietnamese-writing** là gói kỹ năng (`SKILL.md`) đi kèm công cụ dòng lệnh [scripts/vi_scanner.py](scripts/vi_scanner.py), giúp AI Agent viết, biên tập và tự kiểm tra tiếng Việt tự nhiên, rõ chủ thể mà không làm lệch dữ kiện gốc. Công cụ chạy trực tiếp trên `Python 3.11+` với thư viện chuẩn, không cần cài thêm gói bên ngoài.

## Tổng quan

- **Bắt đúng cấu trúc dịch thô, câu dài vòng vo và khuôn mẫu máy móc.** Thay vì cấm từ Hán - Việt một cách máy móc, 41 quy tắc trong [scripts/vi_scanner.py](scripts/vi_scanner.py) chỉ ra câu rào đón kiểu chatbot, cấu trúc bị động dịch từng chữ (*"được thực hiện bởi"*), cụm danh từ hóa nặng nề và nhãn in đậm lặp khuôn. Quy tắc `VIS-LEN-001` phạt nặng câu văn xuôi quá dài hoặc mở câu vòng vo, còn hệ thống gợi ý luôn bám sát từng nhánh lỗi vừa bắt được.
- **Quét đủ 100% tín hiệu kèm miễn trừ theo 7 ngữ cảnh.** Lệnh `scan` mặc định chạy ở chế độ `all` và xuất toàn bộ tín hiệu trên 7 nhóm văn bản (`general`, `audit_report`, `academic`, `legal`, `marketing`, `social_media`, `translation`). Nhờ hai trường `applicable_profiles` và `exempt_profiles` trên từng kết quả, câu bị động chuẩn mực trong hợp đồng pháp lý hoặc trích dẫn học thuật không bị ép sửa sai ngữ cảnh.
- **Che chắn vùng mã lệnh và đối soát bảo toàn dữ kiện.** Lớp `SemanticMasker` bỏ qua khối code, mã nội dòng, đường dẫn URL và lời trích dẫn trong ngoặc kép mà vẫn giữ nguyên số dòng, số cột. Sau khi biên tập, lệnh `verify` đối chiếu bản gốc với bản sửa để chặn lỗi làm rơi con số, từ phủ định, điều kiện hoặc mức độ chắc chắn.
- **Phân biệt từ mượn quen dùng với lối chêm từ lửng lơ.** Bộ lọc âm vị nhận diện từ tiếng Anh chêm giữa câu tiếng Việt nhưng tự động cho qua nhóm từ đã quen dùng hàng ngày (`email`, `web`, `file`, `video`, `team`, `deadline`, `server`, `kpi`), đồng thời nhắc lịch rà soát định kỳ qua lệnh `check-maintenance`.
- **Đọc trực tiếp tệp `.docx` và lập hồ sơ giọng văn (`DHDNA` & `Stylometry`).** Hai lệnh `scan` và `profile` đọc thẳng tệp Word `.docx` bằng thư viện chuẩn, cho phép dùng `--ignore-table-cols` để bỏ qua cột bảng trích lục của bên thứ ba. Máy quét cũng phát hiện lỗi sót tiêu đề kỳ cũ trong thuộc tính tệp (`template_title_mismatch`), cảnh báo lệch mẫu số giữa các trang và xếp loại giọng văn theo 4 mẫu chuẩn tại [references/voice-and-argument-patterns.md](references/voice-and-argument-patterns.md).

## Cài đặt nhanh

Bạn có thể cài trực tiếp kỹ năng này vào Claude Code, Cursor, Codex, Antigravity hoặc chạy độc lập từ dòng lệnh trong vòng 1 phút:

```bash
# Cài qua skills.sh CLI (hỗ trợ Claude Code, Cursor, Codex, Antigravity)
npx skills add ducle2502/vietnamese-writing

# Cài qua Skills Manager CLI
skills-manager-cli skills install https://github.com/ducle2502/vietnamese-writing.git

# Cài qua pi
pi install git:github.com/ducle2502/vietnamese-writing
```

Nếu muốn tải trực tiếp mã nguồn và chạy thử ngay công cụ quét bằng `Python 3.11+`:

```bash
git clone https://github.com/ducle2502/vietnamese-writing.git
cd vietnamese-writing
python -B scripts/vi_scanner.py selftest
python -B scripts/vi_scanner.py scan SKILL.md
```

## 6 nhóm quy tắc và 7 ngữ cảnh văn bản

Chi tiết toàn bộ 41 mã quy tắc cùng ví dụ câu lỗi và câu viết lại nằm tại [references/rule-catalog.md](references/rule-catalog.md):

| Nhóm mã | Tên nhóm quy tắc | Số quy tắc | Các lỗi trọng tâm được chỉ ra |
|---|---|---|---|
| `VIS-AI-001..007` | Tín hiệu sinh văn của AI | `7` | Câu rào đón/kết thúc kiểu chatbot, mở bài vĩ mô (*"Trong bối cảnh..."*), ép tưởng tượng giả định (*"Hãy thử tưởng tượng..."*), câu điều kiện bao sân (*"Dù bạn là..."*) và chỗ trống nhắc điền chưa xóa. |
| `VIS-RHET-001..007` | Tu từ phóng đại và dàn ý lộ liễu | `7` | Cặp đòn bẩy (*"không chỉ... mà còn"*, *"hơn cả X, đây là Y"*), đối lập giả kịch tính (*"tưởng chừng... nhưng"*), tự khen tầm vóc (*"đóng vai trò then chốt"*), ẩn dụ dịch sát và dẫn nguồn không tên. |
| `VIS-FMT-001..006` | Định dạng và nhịp đoạn máy móc | `6` | Danh sách đóng khuôn `**Nhãn:**`, từ nối đầu câu dày đặc, lạm dụng gạch ngang dài (`—`), xếp chồng tính từ khen ngợi, chia đều đoạn văn hoặc chuỗi 3 câu cực ngắn kiểu khẩu hiệu. |
| `VIS-TRANS-001..010` | Cấu trúc dịch sát từ tiếng Anh | `10` | Câu bị động dịch từ *by* (*"được phê duyệt bởi"*), danh từ hóa (*"sự sụt giảm của"*), chuỗi sở hữu *"của... của... của"*, cặp liên từ sóng đôi lặp dày, *"đến từ"* chỉ nguồn gốc trừu tượng, *"ở trong... bên trong"* và lặp *"mang tính"*. |
| `VIS-CLICHE-001..005` | Sáo ngữ hành chính và quảng cáo | `5` | Nhét động từ rỗng (*"tiến hành việc kiểm tra"*), khẩu hiệu thiếu đầu ra, cụm từ trùng nghĩa, câu khách kiểu quảng cáo và chồng nhiều lớp từ rào đón. |
| `VIS-LEX` · `VIS-TONE` · `VIS-STRUCT` · `VIS-LEN` | Từ vựng, giọng văn, độ dài câu và kỷ luật bằng chứng | `6` | Phạt nặng câu dài quá `45` từ (`55` từ với văn bản pháp lý), câu nối đuôi nhiều dấu phẩy và dẫn dắt vòng vo (`VIS-LEN-001`). Bắt lỗi dùng sai từ Hán - Việt (`thực chứng`, `yếu điểm`), sai chính tả (`chỉnh chu`, `chắp bút`), lậm văn phong truyện dịch thô, dịch ngược từ quen dùng (`thư điện tử`), chêm tiếng Anh lửng lơ (`booking lịch`), giọng kịch tính hóa (`sập toàn tuyến`), gộp mục còn lỗi vào tỷ lệ hoàn thành và lệch tổng bảng số liệu. |

## Cách sử dụng dòng lệnh

```bash
# 1. Quét mặc định (chế độ 'all' xuất đủ 100% tín hiệu của cả 7 nhóm văn bản)
python -B scripts/vi_scanner.py scan BAI_VIET.md

# 2. Quét trực tiếp tệp Word .docx và bỏ qua cột bảng trích lục bên thứ ba
python -B scripts/vi_scanner.py scan BAO_CAO.docx --profile audit_report --ignore-table-cols 2,3

# 3. Lập hồ sơ 18 chỉ số nhịp câu (stylometry) và 12 chỉ số kỷ luật lập luận DHDNA
python -B scripts/vi_scanner.py profile BAO_CAO.docx --ignore-table-cols 2,3 --json

# 4. Đối soát bảo toàn số liệu, phủ định, điều kiện và trích dẫn trước - sau khi sửa
python -B scripts/vi_scanner.py verify BAN_GOC.md BAN_SAU_SUA.md

# 5. Kiểm tra hạn rà soát định kỳ danh sách từ tiếng Anh quen dùng
python -B scripts/vi_scanner.py check-maintenance

# 6. Chạy bộ kiểm thử tự động (100+ mẫu kiểm thử độc lập và kiểm tra cấu trúc Skill)
python -B -m unittest discover -s tests -v
```

## Cấu trúc thư mục

| Đường dẫn | Vai trò |
|---|---|
| [SKILL.md](SKILL.md) | Hướng dẫn chính cho AI Agent (kèm phần khai báo đầu tệp chuẩn `YAML frontmatter`). |
| [AGENTS.md](AGENTS.md) | Quy tắc rút gọn khi mở trực tiếp thư mục dự án. |
| [data/vocab.csv](data/vocab.csv) · [data/grammar.csv](data/grammar.csv) | Bảng `2.011` mục từ vựng và `41` quy tắc ngữ pháp chuẩn `UTF-8 BOM`, mở và chỉnh sửa trực tiếp bằng Excel. |
| [scripts/vi_scanner.py](scripts/vi_scanner.py) | Công cụ dòng lệnh quét văn bản, lập hồ sơ giọng văn DHDNA, đọc `.docx` và đối soát dữ kiện. |
| [scripts/check_code_limits.py](scripts/check_code_limits.py) | Trình kiểm tra giới hạn độ dài tệp, hàm, lớp và cấu trúc dữ liệu theo `[tool.code_limits]`. |
| [references/rule-catalog.md](references/rule-catalog.md) | Bảng tra cứu chi tiết 41 quy tắc kèm dấu hiệu nhận diện và cách viết lại. |
| [references/voice-and-argument-patterns.md](references/voice-and-argument-patterns.md) | Bốn kiểu giọng văn chức năng, 6 kỷ luật dẫn số liệu/bằng chứng và bảng chuyển ngữ quản trị. |
| [references/loanwords-and-exceptions.md](references/loanwords-and-exceptions.md) | Quy trình cập nhật danh sách từ tiếng Anh quen dùng và ngoại lệ của 7 nhóm văn bản. |
| [evals/evals.json](evals/evals.json) | Bộ kịch bản kiểm thử hành vi biên tập thực tế cho Agent. |
| [tests/test_vi_scanner.py](tests/test_vi_scanner.py) | Bộ kiểm thử đơn vị (100+ mẫu đối chứng, kiểm tra đồng bộ gợi ý sửa, chống treo máy và kiểm tra gói kỹ năng). |
| [pyproject.toml](pyproject.toml) | Cấu hình kiểm tra kiểu tĩnh `mypy`, độ phức tạp mã nguồn với `ruff` và giới hạn kích thước `[tool.code_limits]`. |
| [CONTRIBUTING.md](CONTRIBUTING.md) · [CHANGELOG.md](CHANGELOG.md) | Hướng dẫn đóng góp quy tắc mới và lịch sử phiên bản. |

## Giới hạn phạm vi

- Mọi tín hiệu từ [scripts/vi_scanner.py](scripts/vi_scanner.py) chỉ đánh dấu những chỗ câu chữ gượng gạo, sáo rỗng hoặc dịch sát cần đọc lại, tuyệt đối không dùng để kết luận văn bản do con người hay AI viết.
- Kỹ năng này hướng tới câu tiếng Việt rõ nghĩa, hợp người đọc và giữ nguyên dữ kiện gốc, không chèn lỗi chính tả hay phương ngữ giả tạo để lách công cụ dò tự động.
- Nếu người dùng chỉ dán hợp đồng, báo cáo hoặc tài liệu để hỏi nội dung bên trong, Agent giữ nguyên văn bản gốc và trả lời thẳng câu hỏi.

## Giấy phép

Phát hành theo giấy phép [MIT](LICENSE).
