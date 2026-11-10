# vietnamese-writing

Bộ kỹ năng (`SKILL.md`) và công cụ dòng lệnh (`vi_scanner.py` bản 2.0) giúp Agent viết, biên tập và kiểm tra tiếng Việt tự nhiên, rõ ý mà vẫn giữ nguyên dữ kiện gốc.

## Tính năng chính

1. Bộ 30 quy tắc chia làm 6 nhóm: tách biệt rõ câu rào đón và khuôn mẫu của AI (`VIS-AI`), lối nói phóng đại (`VIS-RHET`), định dạng và nhịp đoạn máy móc (`VIS-FMT`), cấu trúc dịch từng chữ từ tiếng Anh sang tiếng Việt (`VIS-TRANS`), sáo ngữ hành chính hoặc quảng cáo đặt sai chỗ (`VIS-CLICHE`), cùng nhóm lỗi dùng sai từ Hán - Việt, từ tự chế ngô nghê, giọng sồn sã và lỗi bảng số liệu (`VIS-LEX`, `VIS-TONE`, `VIS-STRUCT`).
2. Quét mặc định đủ mọi ngữ cảnh (`--profile all`) xuất 100% tín hiệu trên cả 7 nhóm văn bản (`general`, `audit_report`, `academic`, `legal`, `marketing`, `social_media`, `translation`) kèm nhãn nhóm áp dụng và nhóm được miễn để Agent tự đối chiếu ngữ cảnh. Hỗ trợ lọc riêng từng nhóm khi chạy kiểm thử tự động.
3. Bảo vệ vùng không quét và đối soát dữ kiện (`SemanticMasker`) giúp bỏ qua khối code, mã nội dòng, đường dẫn liên kết và câu trích dẫn trong ngoặc kép mà vẫn giữ đúng số dòng, số cột. Lệnh `verify` kiểm tra bảo toàn số liệu, từ phủ định, từ điều kiện, mức độ chắc chắn, đường dẫn và trích dẫn trước và sau khi sửa.
4. Không gắn cứng dữ liệu dự án và chạy nhanh nhờ chỉ dùng thư viện chuẩn Python 3.11+ (tự nhận `google-re2` nếu có), biểu thức chính quy chạy một lượt không gây treo máy (ReDoS).

## Cách sử dụng nhanh

```bash
# Quét mặc định (xuất đủ 100% tín hiệu của mọi nhóm văn bản)
python vi_scanner.py scan BAI_VIET.md

# Xuất JSON cho Agent đọc và biên tập
python vi_scanner.py scan BAI_VIET.md --json

# Lọc riêng cho một nhóm văn bản cụ thể (ví dụ: báo cáo kiểm toán/quản trị)
python vi_scanner.py scan BAO_CAO.md --profile audit_report

# Đối soát bảo toàn số liệu, phủ định và điều kiện trước - sau biên tập
python vi_scanner.py verify BAN_GOC.md BAN_SAU_SUA.md

# Kiểm tra hạn rà soát định kỳ danh sách từ tiếng Anh quen dùng
python vi_scanner.py check-maintenance

# Chạy kiểm thử tự động (100+ mẫu kiểm thử độc lập)
python vi_scanner.py selftest
python -m unittest discover -s tests -v
```

## Cài đặt làm kỹ năng cho Agent

Sao chép hoặc tạo liên kết thư mục repo này vào thư mục `skills/vietnamese-writing` của Agent (Antigravity, Claude Code, Cursor, Codex). Agent sẽ đọc [SKILL.md](SKILL.md), sử dụng `vi_scanner.py` để rà câu chữ và tra cứu ngoại lệ tại [references/loanwords-and-exceptions.md](references/loanwords-and-exceptions.md).

## Lưu ý bảo trì định kỳ

Danh sách từ tiếng Anh đã quen dùng trong tiếng Việt (`UNIVERSAL_NATURALIZED_LOANWORDS` và `WORKPLACE_TECH_LOANWORDS` ở đầu tệp [vi_scanner.py](vi_scanner.py)) là phần từ vựng duy nhất cần rà soát và cập nhật hàng quý hoặc hàng năm theo biến động thực tế của ngôn ngữ đi làm.
