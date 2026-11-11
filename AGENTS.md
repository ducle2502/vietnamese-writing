# vietnamese-writing

Áp dụng khi viết, biên tập hoặc kiểm tra tiếng Việt. Hướng dẫn đầy đủ nằm tại [SKILL.md](SKILL.md).

## Nguyên tắc sử dụng

1. Xác định rõ người đọc, quan hệ xưng hô và nhóm văn bản (`general`, `audit_report`, `academic`, `legal`, `marketing`, `social_media`, `translation`) trước khi viết hoặc sửa. Không tự ý sửa lại khi người dùng chỉ dán văn bản để hỏi nội dung.
2. Đưa kết luận và số liệu lên đầu câu hoặc đầu đoạn. Ưu tiên chủ thể chỉ người, đơn vị cụ thể đi với động từ trực tiếp. Giữ mỗi câu văn xuôi và ô bảng tối đa `35` từ (`45` từ với văn bản pháp lý). Hễ vượt ngưỡng, cả `scan` lẫn `profile` báo lỗi ngay và bắt buộc tách câu trước khi bàn giao.
3. Bảo toàn nguyên vẹn số liệu, ngày tháng, từ phủ định, từ chỉ điều kiện, từ chỉ mức độ chắc chắn, đường dẫn, khối mã lệnh và nguồn trích dẫn.
4. Tránh 5 lỗi sửa quá tay: đếm tuần tự, hạ giọng sồn sã, tự bịa từ, rơi mức chắc chắn và xoay vòng động từ đầu ô bảng.

## Tự quét và kiểm tra trong repo

Sau khi viết mới hoặc biên tập (trừ hội thoại ngắn 1 đến 2 câu), luôn tự quét lại đầu ra từ thư mục gốc trước khi bàn giao:

```bash
python -B scripts/vi_scanner.py scan TEP_VUA_VIET.md --json
python -B scripts/vi_scanner.py profile TEP_VUA_VIET.md --json
python -B scripts/vi_scanner.py verify BAN_GOC.md BAN_SAU_SUA.md
python -B scripts/vi_scanner.py check-maintenance
ruff check scripts tests
ruff format --check scripts tests
mypy scripts tests
python -B scripts/check_code_limits.py
python -B -m unittest discover -s tests -v
```

Khi cập nhật quy tắc trong [data/vocab.csv](data/vocab.csv), [data/grammar.csv](data/grammar.csv) hoặc [scripts/vi_scanner.py](scripts/vi_scanner.py), giữ đồng bộ nội dung giữa [SKILL.md](SKILL.md), [README.md](README.md) và ba tệp tham chiếu ([rule-catalog.md](references/rule-catalog.md), [voice-and-argument-patterns.md](references/voice-and-argument-patterns.md), [loanwords-and-exceptions.md](references/loanwords-and-exceptions.md)). Hai tệp [data/vocab.csv](data/vocab.csv) và [data/grammar.csv](data/grammar.csv) bắt buộc giữ nguyên 3 byte `UTF-8 BOM` ở đầu tệp. Luôn ghi hai tệp CSV này qua Python với `encoding="utf-8-sig"`, không dùng công cụ sửa văn bản thuần của IDE để tránh mất BOM lúc chốt duyệt. Sau đó, chạy lại bộ kiểm thử đơn vị và quét chính các tệp `.md` trong repo.
