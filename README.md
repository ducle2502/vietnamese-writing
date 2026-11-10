# vietnamese-writing

Kỹ năng chuẩn (`SKILL.md`) kèm công cụ dòng lệnh (`scripts/vi_scanner.py` bản 2.0) giúp AI Agent viết, biên tập và kiểm tra tiếng Việt tự nhiên, rõ ý mà vẫn bảo toàn nguyên vẹn dữ kiện gốc.

## Cấu trúc thư mục chuẩn Skill

```text
vietnamese-writing/
├── SKILL.md                             # Hướng dẫn chính cho Agent (kèm YAML frontmatter)
├── AGENTS.md                            # Quy tắc ngắn gọn khi mở trực tiếp thư mục
├── LICENSE                              # Giấy phép MIT
├── README.md                            # Hướng dẫn cài đặt và sử dụng
├── scripts/
│   └── vi_scanner.py                    # Máy quét câu chữ và đối soát dữ kiện (Python 3.11+)
├── references/
│   ├── rule-catalog.md                  # Bảng tra cứu 30 mã quy tắc và cách viết lại
│   └── loanwords-and-exceptions.md      # Quy trình cập nhật từ mượn và ngoại lệ 7 nhóm văn bản
├── .claude-plugin/                      # Cấu hình cài đặt cho Claude Code
├── .cursor-plugin/                      # Cấu hình cài đặt cho Cursor
└── tests/
    └── test_vi_scanner.py               # Bộ 100+ mẫu kiểm thử độc lập và kiểm tra gói kỹ năng
```

## Cách cài đặt cho Agent

```bash
# Cài qua skills.sh CLI (hỗ trợ Claude Code, Cursor, Codex, Antigravity...)
npx skills add ducle2502/vietnamese-writing

# Cài qua Skills Manager CLI
skills-manager-cli skills install https://github.com/ducle2502/vietnamese-writing.git

# Hoặc tải trực tiếp vào thư mục skills của Agent
git clone https://github.com/ducle2502/vietnamese-writing.git ~/.gemini/config/skills/vietnamese-writing
```

## Tính năng chính

1. Bộ 30 quy tắc chia làm 6 nhóm: tách biệt rõ câu rào đón và khuôn mẫu của AI (`VIS-AI`), lối nói phóng đại (`VIS-RHET`), định dạng và nhịp đoạn máy móc (`VIS-FMT`), cấu trúc dịch từng chữ từ tiếng Anh sang tiếng Việt (`VIS-TRANS`), sáo ngữ hành chính hoặc quảng cáo đặt sai chỗ (`VIS-CLICHE`), cùng nhóm lỗi dùng sai từ Hán - Việt, từ tự chế ngô nghê, giọng sồn sã và lỗi bảng số liệu (`VIS-LEX`, `VIS-TONE`, `VIS-STRUCT`).
2. Quét mặc định đủ mọi ngữ cảnh (`--profile all`) xuất 100% tín hiệu trên cả 7 nhóm văn bản (`general`, `audit_report`, `academic`, `legal`, `marketing`, `social_media`, `translation`) kèm nhãn nhóm áp dụng và nhóm được miễn để Agent tự đối chiếu ngữ cảnh. Hỗ trợ lọc riêng từng nhóm khi chạy kiểm thử tự động.
3. Bảo vệ vùng không quét và đối soát dữ kiện (`SemanticMasker`) giúp bỏ qua khối code, mã nội dòng, đường dẫn liên kết và câu trích dẫn trong ngoặc kép mà vẫn giữ đúng số dòng, số cột. Lệnh `verify` kiểm tra bảo toàn số liệu, từ phủ định, từ điều kiện, mức độ chắc chắn, đường dẫn và trích dẫn trước và sau khi sửa.
4. Không gắn cứng dữ liệu dự án và chạy nhanh nhờ chỉ dùng thư viện chuẩn Python 3.11+ (tự nhận `google-re2` nếu có), biểu thức chính quy chạy một lượt không gây treo máy (ReDoS).

## Cách sử dụng dòng lệnh

```bash
# Quét mặc định (xuất đủ 100% tín hiệu của mọi nhóm văn bản)
python scripts/vi_scanner.py scan BAI_VIET.md

# Xuất JSON cho Agent đọc và biên tập
python scripts/vi_scanner.py scan BAI_VIET.md --json

# Lọc riêng cho một nhóm văn bản cụ thể (ví dụ: báo cáo kiểm toán/quản trị)
python scripts/vi_scanner.py scan BAO_CAO.md --profile audit_report

# Đối soát bảo toàn số liệu, phủ định và điều kiện trước và sau biên tập
python scripts/vi_scanner.py verify BAN_GOC.md BAN_SAU_SUA.md

# Kiểm tra hạn rà soát định kỳ danh sách từ tiếng Anh quen dùng
python scripts/vi_scanner.py check-maintenance

# Chạy kiểm thử tự động (100+ mẫu kiểm thử độc lập và kiểm tra cấu trúc Skill)
python scripts/vi_scanner.py selftest
python -m unittest discover -s tests -v
```

## Lưu ý bảo trì định kỳ

Danh sách từ tiếng Anh đã quen dùng trong tiếng Việt (`UNIVERSAL_NATURALIZED_LOANWORDS` và `WORKPLACE_TECH_LOANWORDS` ở đầu tệp [scripts/vi_scanner.py](scripts/vi_scanner.py)) là phần từ vựng duy nhất cần rà soát và cập nhật hàng quý hoặc hàng năm theo hướng dẫn tại [references/loanwords-and-exceptions.md](references/loanwords-and-exceptions.md).
