# Hướng dẫn đóng góp (Contributing)

Tài liệu này hướng dẫn cách thiết lập môi trường, nguyên tắc thêm quy tắc mới vào [scripts/vi_scanner.py](scripts/vi_scanner.py), cách cập nhật danh sách từ mượn và quy trình kiểm tra trước khi mở Pull Request.

## 1. Yêu cầu môi trường

Dự án chỉ sử dụng thư viện chuẩn của `Python 3.11+` khi chạy trên Windows, macOS và Linux, không yêu cầu cài đặt gói phụ thuộc bên ngoài (nếu máy có cài sẵn `google-re2`, bộ quét sẽ tự động nhận diện). Khi phát triển mã nguồn, cài thêm `mypy` và `ruff` theo cấu hình tại [pyproject.toml](pyproject.toml) để kiểm tra kiểu tĩnh, định dạng và giới hạn độ phức tạp thuật toán.

```bash
git clone https://github.com/ducle2502/vietnamese-writing.git
cd vietnamese-writing
python -m pip install "mypy>=1.11" "ruff>=0.8"
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

## 3. Quy trình cập nhật quy tắc và từ vựng trên CSV

Toàn bộ từ vựng và quy tắc mặc định nằm tại hai tệp [data/vocab.csv](data/vocab.csv) và [data/grammar.csv](data/grammar.csv) (mã hóa `UTF-8 BOM` để mở và lưu trực tiếp trong Microsoft Excel mà không lỗi dấu tiếng Việt):

1. Thêm, sửa, tắt (`status=disabled`) hoặc xóa từ mượn (`loanword_universal`, `loanword_workplace`), cụm dịch ngược (`reverse_calque`) và cụm từ cấm (`banned_phrase`) trong [data/vocab.csv](data/vocab.csv).
2. Bật/tắt quy tắc, chỉnh trọng số, nhóm áp dụng hoặc thêm biểu thức chính quy mới trong [data/grammar.csv](data/grammar.csv), đồng thời cập nhật ngày `last_reviewed` trong `LOANWORDS_REVIEW_META` khi rà soát định kỳ theo [references/loanwords-and-exceptions.md](references/loanwords-and-exceptions.md).
3. Chạy `python -B scripts/vi_scanner.py selftest` và `python -B scripts/vi_scanner.py check-maintenance` để xác nhận cú pháp CSV và trạng thái bảo trì hợp lệ.

## 4. Kiểm tra bắt buộc trước khi gửi Pull Request

Mọi thay đổi đối với quy tắc quét hoặc tài liệu hướng dẫn đều phải giữ đồng bộ giữa [scripts/vi_scanner.py](scripts/vi_scanner.py), [SKILL.md](SKILL.md), [AGENTS.md](AGENTS.md), [README.md](README.md) và thư mục [references/](references/). Trước khi tạo Pull Request, hãy chạy đủ các lệnh kiểm tra sau:

```bash
ruff check scripts tests
ruff format --check scripts tests
mypy scripts tests
python -B scripts/check_code_limits.py
python -B scripts/vi_scanner.py selftest
python -B -m unittest discover -s tests -v
python -B scripts/vi_scanner.py scan SKILL.md AGENTS.md README.md CONTRIBUTING.md CHANGELOG.md references/rule-catalog.md references/voice-and-argument-patterns.md references/loanwords-and-exceptions.md --json
```
