<a id="top"></a>

<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./assets/banner-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="./assets/banner-light.svg">
  <img alt="vietnamese-writing" src="./assets/banner-dark.svg" width="100%">
</picture>

<br>

[![CI](https://github.com/ducle2502/vietnamese-writing/actions/workflows/ci.yml/badge.svg)](https://github.com/ducle2502/vietnamese-writing/actions/workflows/ci.yml) ![Python](https://img.shields.io/badge/python-3.11%2B-0969da?style=flat-square&labelColor=161b22) ![Rules](https://img.shields.io/badge/rules-51%20%286%20groups%29-3fb950?style=flat-square&labelColor=161b22) [![License](https://img.shields.io/badge/license-MIT-58a6ff?style=flat-square&labelColor=161b22)](./LICENSE)

[Tổng quan](#tổng-quan) · [Cài đặt nhanh](#cài-đặt-nhanh) · [6 nhóm quy tắc](#6-nhóm-quy-tắc-và-7-ngữ-cảnh-văn-bản) · [Dòng lệnh](#chạy-từ-dòng-lệnh) · [Cấu trúc thư mục](#cấu-trúc-thư-mục) · [Giới hạn phạm vi](#giới-hạn-phạm-vi)

</div>

**vietnamese-writing** là gói kỹ năng (`SKILL.md`) đi kèm công cụ dòng lệnh [scripts/vi_scanner.py](scripts/vi_scanner.py). Bộ công cụ giúp AI Agent viết, biên tập và tự kiểm tra tiếng Việt rõ chủ thể mà không làm lệch dữ kiện gốc. Công cụ chạy trực tiếp trên `Python 3.11+` với thư viện chuẩn, không cần cài thêm gói bên ngoài.

## Tổng quan

Công cụ không cấm từ Hán - Việt một cách cực đoan. Thay vào đó, 51 quy tắc trong [scripts/vi_scanner.py](scripts/vi_scanner.py) chỉ ra câu rào đón chatbot, câu bị động dịch từng chữ (*"được thực hiện bởi"*), danh từ hóa và danh sách gắn nhãn in đậm rập khuôn. Quy tắc `VIS-LEN-001` báo lỗi ngay khi gặp câu vượt `35` từ (`45` từ ở văn bản pháp lý) kể cả trong ô bảng, kèm gợi ý sửa cụ thể cho từng nhánh lỗi.

Lệnh `scan` mặc định chạy ở chế độ `all` và xuất toàn bộ tín hiệu trên 7 nhóm văn bản (`general`, `audit_report`, `academic`, `legal`, `marketing`, `social_media`, `translation`). Nhờ hai trường `applicable_profiles` và `exempt_profiles` trên từng kết quả, câu bị động hợp lệ trong hợp đồng pháp lý hoặc trích dẫn học thuật không bị ép sửa sai ngữ cảnh.

Lớp `SemanticMasker` bỏ qua khối code, mã nội dòng, đường dẫn URL và lời trích dẫn trong ngoặc kép khi quét mà vẫn giữ nguyên số dòng, số cột. Sau khi biên tập, lệnh `verify` đối chiếu bản gốc với bản sửa để chặn lỗi làm rơi con số, từ phủ định, điều kiện hoặc mức độ chắc chắn. Bộ lọc âm vị cũng bắt từ tiếng Anh chêm tùy tiện giữa câu nhưng tự cho qua nhóm từ đã quen dùng (`email`, `web`, `file`, `video`, `team`, `deadline`, `server`, `kpi`), kèm lệnh `check-maintenance` nhắc lịch rà soát định kỳ theo quý.

Agent chuyển tệp nguồn sang `TEN_GOC.raw.md` kèm `TEN_GOC.raw.meta.json` trước khi quét. Lệnh `scan` và `profile` nhận Markdown thô cùng tệp UTF-8. Riêng `.docx`, công cụ tự bóc tách tất định trước khi quét. Bộ chuyển đổi dùng `markitdown`, `liteparse`, `docling` hoặc `pandoc` cho định dạng khác. `vision` chỉ là phương án dự phòng và phải ghi `deterministic=false` cùng `needs_review=true`. Máy quét phát hiện lỗi sót tiêu đề kỳ trước trong thuộc tính tệp (`template_title_mismatch`) và cảnh báo lệch mẫu số giữa các trang. Lệnh `profile` xếp loại giọng văn theo bốn kiểu chính và một nhãn dự phòng tại [references/voice-and-argument-patterns.md](references/voice-and-argument-patterns.md).

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

Tải trực tiếp mã nguồn và chạy kiểm tra trên `Python 3.11+`:

```bash
git clone https://github.com/ducle2502/vietnamese-writing.git
cd vietnamese-writing
python -B scripts/vi_scanner.py selftest
python -B scripts/vi_scanner.py scan SKILL.md
```

## 6 nhóm quy tắc và 7 ngữ cảnh văn bản

Chi tiết toàn bộ 51 mã quy tắc cùng ví dụ câu lỗi và câu viết lại nằm tại [references/rule-catalog.md](references/rule-catalog.md):

| Nhóm mã | Tên nhóm quy tắc | Số quy tắc | Lỗi câu chữ trọng tâm |
|---|---|---|---|
| `VIS-AI-001..007` | Tín hiệu sinh văn của AI | `7` | Câu rào đón/kết thúc kiểu chatbot, mở bài chung chung (*"Trong bối cảnh..."*), bắt hình dung tình huống giả (*"Hãy thử tưởng tượng..."*), câu gom mọi nhóm người đọc (*"Dù bạn là..."*) và `placeholder` chưa điền. |
| `VIS-RHET-001..009` | Tu từ phóng đại và dàn ý lộ liễu | `9` | Cấu trúc *"không chỉ... mà còn"*, *"hơn cả X, đây là Y"*, cặp vế tạo kịch tính giả (*"tưởng chừng... nhưng"*), tự khen phóng đại (*"đóng vai trò then chốt"*), ẩn dụ sáo rỗng và dẫn nguồn không tên. |
| `VIS-FMT-001..008` | Định dạng và nhịp đoạn máy móc | `8` | Danh sách đóng khuôn `**Nhãn:**` hoặc `**Nhãn.**`, từ nối đầu câu dày đặc, lạm dụng gạch ngang dài (`—`), xếp chồng tính từ khen ngợi, chia đều đoạn văn hoặc chuỗi 3 câu cụt kiểu khẩu hiệu. |
| `VIS-TRANS-001..014` | Dịch từng chữ từ tiếng Anh | `14` | Câu bị động dịch từ *by* (*"được phê duyệt bởi"*), danh từ hóa (*"sự sụt giảm của"*), chuỗi sở hữu *"của... của... của"*, lặp lại dày đặc cặp quan hệ từ, *"đến từ"* chỉ nguồn gốc trừu tượng và lặp *"mang tính"*. |
| `VIS-CLICHE-001..005` | Sáo ngữ hành chính và quảng cáo | `5` | Nhét động từ rỗng (*"tiến hành việc kiểm tra"*), khẩu hiệu thiếu đầu ra, cụm từ trùng nghĩa, lời kêu gọi kiểu quảng cáo và chồng nhiều lớp từ rào đón. |
| `VIS-LEX` · `VIS-TONE` · `VIS-STRUCT` · `VIS-LEN` | Từ vựng, giọng văn, độ dài câu và kỷ luật bằng chứng | `8` | Báo lỗi ngay câu dài quá `35` từ (`45` từ ở văn bản pháp lý, tính cả ô bảng), câu nối nhiều dấu phẩy và mở câu vòng vo (`VIS-LEN-001`). Bắt lỗi sai từ Hán - Việt (`thực chứng`), sai chính tả vỏ ngữ âm (`sồn sã`, `chỉnh chu`, `cập nhập`, `sát nhập`), dịch thô (`khung hợp đồng`, `hiện thực lớp`) và dịch ngược (`thư điện tử`). Đồng thời chặn giọng giật gân (`phát lộ`, `vạch trần`, `sập API`, `vỏn vẹn`), khẩu ngữ suồng sã (`rủi ro sát sườn`), lặp từ gần nhau và lỗi kỷ luật số liệu. |

## Chạy từ dòng lệnh

Agent chuyển tệp nguồn sang `TEN_GOC.raw.md` trước khi quét. Với `.docx`, lệnh `scan` và `profile` tự bóc tách tất định nên vẫn truyền thẳng tệp Word được.

```bash
# 1. Quét bản Markdown thô vừa nhận (chế độ 'all' xuất đủ 100% tín hiệu của cả 7 nhóm văn bản)
python -B scripts/vi_scanner.py scan TEN_GOC.raw.md

# 2. Quét báo cáo và bỏ qua cột bảng trích lục bên thứ ba
python -B scripts/vi_scanner.py scan TEN_GOC.raw.md --profile audit_report --ignore-table-cols 2,3

# 3. Lập hồ sơ 18 chỉ số nhịp câu (stylometry) và 14 chỉ số kỷ luật lập luận DHDNA
python -B scripts/vi_scanner.py profile TEN_GOC.raw.md --ignore-table-cols 2,3 --json

# 4. Đối chiếu số liệu, phủ định, điều kiện và trích dẫn trước - sau khi sửa
python -B scripts/vi_scanner.py verify TEN_GOC.raw.md BAN_SUA.md

# 5. Kiểm tra hạn rà soát định kỳ danh sách từ tiếng Anh quen dùng
python -B scripts/vi_scanner.py check-maintenance

# 6. Chạy bộ kiểm thử tự động (100+ mẫu kiểm thử độc lập, giới hạn mã nguồn và cấu trúc Skill)
python -B -m pytest -v
```

## Cấu trúc thư mục

| Đường dẫn | Vai trò |
|---|---|
| [SKILL.md](SKILL.md) | Hướng dẫn chính cho AI Agent (kèm phần khai báo đầu tệp chuẩn `YAML frontmatter`). |
| [AGENTS.md](AGENTS.md) | Quy tắc rút gọn khi mở trực tiếp thư mục dự án. |
| [data/vocab.csv](data/vocab.csv) · [data/grammar.csv](data/grammar.csv) | Bảng `2.089` mục từ vựng và `51` quy tắc ngữ pháp chuẩn `UTF-8 BOM`, mở và chỉnh sửa trực tiếp bằng Excel. |
| [scripts/vi_scanner.py](scripts/vi_scanner.py) | Công cụ dòng lệnh quét Markdown thô, bóc tách `.docx` tất định, lập hồ sơ giọng văn DHDNA và đối soát dữ kiện. |
| [references/rule-catalog.md](references/rule-catalog.md) | Bảng tra cứu chi tiết 51 quy tắc kèm dấu hiệu nhận diện và cách viết lại. |
| [references/voice-and-argument-patterns.md](references/voice-and-argument-patterns.md) | Bốn kiểu giọng chính, nhãn dự phòng, 12 chiều DHDNA, quy trình biên tập và sổ tay bảy phần. |
| [references/loanwords-and-exceptions.md](references/loanwords-and-exceptions.md) | Quy trình cập nhật danh sách từ tiếng Anh quen dùng và ngoại lệ của 7 nhóm văn bản. |
| [references/pattern-bank.md](references/pattern-bank.md) | Ngân hàng tổng hợp 50 cấu trúc, 500 khuôn câu và 12 bộ lọc regex. |
| [evals/evals.json](evals/evals.json) | Bộ kịch bản kiểm thử hành vi biên tập thực tế cho Agent. |
| [tests/](tests/) | Bộ kiểm thử `pytest` (100+ mẫu đối chứng, hồi quy 16 họ lỗi, giới hạn mã `[tool.code_limits]` và cấu trúc gói kỹ năng). |
| [pyproject.toml](pyproject.toml) | Cấu hình kiểm tra kiểu tĩnh `mypy`, độ phức tạp mã nguồn với `ruff` và giới hạn kích thước `[tool.code_limits]`. |
| [CONTRIBUTING.md](CONTRIBUTING.md) · [CHANGELOG.md](CHANGELOG.md) | Hướng dẫn đóng góp quy tắc mới và lịch sử phiên bản. |

## Giới hạn phạm vi

- Mọi tín hiệu từ [scripts/vi_scanner.py](scripts/vi_scanner.py) chỉ đánh dấu chỗ câu chữ gượng gạo, sáo rỗng hoặc dịch sát cần đọc lại. Tuyệt đối không dùng kết quả này để kết luận văn bản do con người hay AI viết.
- Kỹ năng này hướng tới câu tiếng Việt rõ nghĩa, hợp người đọc và giữ nguyên dữ kiện gốc. Công cụ không chèn lỗi chính tả hay phương ngữ giả tạo để lách trình dò tự động.
- Nếu người dùng chỉ dán hợp đồng, báo cáo hoặc tài liệu để hỏi nội dung bên trong, Agent giữ nguyên văn bản gốc và trả lời thẳng câu hỏi.

## Giấy phép

Phát hành theo giấy phép [MIT](LICENSE).
