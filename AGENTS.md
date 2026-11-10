# vietnamese-writing

Áp dụng khi viết, biên tập hoặc kiểm tra tiếng Việt. Hướng dẫn đầy đủ nằm tại [SKILL.md](SKILL.md).

## Nguyên tắc sử dụng

1. Xác định rõ người đọc, quan hệ xưng hô và nhóm văn bản (`general`, `audit_report`, `academic`, `legal`, `marketing`, `social_media`, `translation`) trước khi viết hoặc sửa. Không tự ý sửa lại khi người dùng chỉ dán văn bản để hỏi nội dung.
2. Đưa kết luận và số liệu lên đầu câu hoặc đầu đoạn. Ưu tiên chủ thể chỉ người, đơn vị cụ thể đi với động từ trực tiếp.
3. Bảo toàn nguyên vẹn số liệu, ngày tháng, từ phủ định, từ chỉ điều kiện, từ chỉ mức độ chắc chắn, đường dẫn, khối mã lệnh và nguồn trích dẫn.
4. Tránh 4 lỗi sửa quá tay gồm vặn câu tuần tự để né máy quét, hạ giọng sồn sã trong văn bản trình duyệt, tự bịa từ trái thực tế đi làm và làm rơi từ hạn định mức chắc chắn.

## Công cụ kiểm tra trong repo

Chạy từ thư mục gốc của kỹ năng khi rà soát tệp dài hoặc bảo trì bộ quy tắc:

```bash
python scripts/vi_scanner.py scan TEP_CAN_RA.md --json
python scripts/vi_scanner.py verify BAN_GOC.md BAN_SAU_SUA.md
python scripts/vi_scanner.py check-maintenance
python -m unittest discover -s tests -v
```

Khi cập nhật quy tắc trong [scripts/vi_scanner.py](scripts/vi_scanner.py), giữ đồng bộ nội dung giữa [SKILL.md](SKILL.md), [README.md](README.md), [references/rule-catalog.md](references/rule-catalog.md) và [references/loanwords-and-exceptions.md](references/loanwords-and-exceptions.md), sau đó chạy lại bộ kiểm thử đơn vị và quét chính các tệp `.md` trong repo.
