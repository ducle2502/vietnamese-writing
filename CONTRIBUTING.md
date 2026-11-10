# Hướng dẫn đóng góp (Contributing)

Tài liệu này hướng dẫn cách thiết lập môi trường, nguyên tắc thêm quy tắc mới vào [scripts/vi_scanner.py](scripts/vi_scanner.py), cách cập nhật danh sách từ mượn và quy trình kiểm tra trước khi mở Pull Request.

## 1. Yêu cầu môi trường

Dự án chỉ sử dụng thư viện chuẩn của `Python 3.11+` trên Windows, macOS và Linux, không yêu cầu cài đặt gói phụ thuộc bên ngoài (nếu máy có cài sẵn `google-re2`, bộ quét sẽ tự động nhận diện).

```bash
git clone https://github.com/ducle2502/vietnamese-writing.git
cd vietnamese-writing
python -B scripts/vi_scanner.py selftest
python -B -m unittest discover -s tests -v
```

> Lưu ý: Luôn truyền cờ `-B` (`python -B`) khi chạy lệnh cục bộ để Python không sinh thư mục `__pycache__` làm bẩn cây thư mục.

## 2. Nguyên tắc thiết kế quy tắc mới

Mỗi quy tắc trong [scripts/vi_scanner.py](scripts/vi_scanner.py) phải thỏa mãn 4 điều kiện:

1. Không gắn cứng dữ liệu nội bộ: Tuyệt đối không đưa tên hệ thống nội bộ, mã bảng riêng, tên phòng ban hoặc số liệu của một dự án cụ thể vào mã nguồn mặc định. Các quy tắc đặc thù của riêng từng tổ chức phải nạp qua cờ `--custom-rules <tệp.json>`.
2. Khớp tuyến tính an toàn: Biểu thức chính quy không được chứa lượng từ lồng nhau gây treo máy trên văn bản dài. Mọi quy tắc mới phải vượt qua bài kiểm thử chuỗi độc hại hơn 200.000 ký tự dưới `500 ms` trong [tests/test_vi_scanner.py](tests/test_vi_scanner.py).
3. Phân định rõ nhóm văn bản miễn trừ (`exempt_profiles`): Một cấu trúc câu có thể gượng gạo trong tin bài chung (`general`) nhưng lại hợp lệ trong văn bản pháp lý (`legal`) hoặc học thuật (`academic`). Luôn khai báo rõ `applicable_profiles` và `exempt_profiles`.
4. Câu ví dụ sửa (`better_example`) phải tự vượt qua máy quét: Mọi chuỗi `better_example` trong quy tắc mới phải đạt `0` lỗi khi quét ở chế độ `all` và giữ nguyên toàn bộ số liệu, từ phủ định, điều kiện so với `bad_example`.

## 3. Quy trình cập nhật từ mượn định kỳ

Hai danh sách `UNIVERSAL_NATURALIZED_LOANWORDS` và `WORKPLACE_TECH_LOANWORDS` tại đầu tệp [scripts/vi_scanner.py](scripts/vi_scanner.py) được rà soát định kỳ 180 ngày một lần theo hướng dẫn tại [references/loanwords-and-exceptions.md](references/loanwords-and-exceptions.md):

1. Bổ sung từ mới vào đúng tập hợp theo chữ thường và giữ thứ tự bảng chữ cái.
2. Cập nhật hằng số `LOANWORD_LAST_REVIEWED` về ngày thực hiện (`YYYY-MM-DD`).
3. Chạy `python -B scripts/vi_scanner.py check-maintenance` để xác nhận trạng thái bảo trì hợp lệ.

## 4. Kiểm tra bắt buộc trước khi gửi Pull Request

Mọi thay đổi đối với quy tắc quét hoặc tài liệu hướng dẫn đều phải giữ đồng bộ giữa [scripts/vi_scanner.py](scripts/vi_scanner.py), [SKILL.md](SKILL.md), [AGENTS.md](AGENTS.md), [README.md](README.md) và thư mục [references/](references/). Trước khi tạo Pull Request, hãy chạy đủ 3 lệnh kiểm tra sau:

```bash
python -B scripts/vi_scanner.py selftest
python -B -m unittest discover -s tests -v
python -B scripts/vi_scanner.py scan SKILL.md AGENTS.md README.md CONTRIBUTING.md CHANGELOG.md references/rule-catalog.md references/loanwords-and-exceptions.md --json
```
