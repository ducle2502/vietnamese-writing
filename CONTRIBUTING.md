# Hướng dẫn đóng góp (Contributing)

Hướng dẫn thiết lập môi trường, nguyên tắc viết quy tắc mới cho [scripts/vi_scanner.py](scripts/vi_scanner.py), cách cập nhật bảng CSV và các bước kiểm tra bắt buộc trước khi mở Pull Request.

## 1. Yêu cầu môi trường

Công cụ chạy trực tiếp trên thư viện chuẩn của `Python 3.11+` ở cả Windows, macOS và Linux (nếu máy có sẵn `google-re2`, bộ quét tự dùng để tăng tốc). Khi phát triển mã nguồn, cài thêm `mypy` và `ruff` theo cấu hình trong [pyproject.toml](pyproject.toml) để kiểm tra kiểu tĩnh, định dạng và giới hạn độ phức tạp mã nguồn.

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

1. Không gắn cứng dữ liệu nội bộ: Tuyệt đối không đưa tên hệ thống, mã bảng riêng, tên phòng ban hay số liệu dự án vào mã nguồn mặc định. Các quy tắc đặc thù của riêng từng tổ chức phải nạp qua cờ `--custom-rules <tệp.json>`.
2. Khớp tuyến tính an toàn: Biểu thức chính quy không được chứa lượng từ lồng nhau gây treo máy trên văn bản dài. Mọi quy tắc mới phải vượt qua bài kiểm thử chuỗi độc hại hơn 200.000 ký tự dưới `500 ms` trong [tests/test_vi_scanner.py](tests/test_vi_scanner.py).
3. Phân định rõ nhóm văn bản miễn trừ (`exempt_profiles`): Một cấu trúc câu có thể gượng gạo trong tin bài chung (`general`) nhưng lại hợp lệ trong văn bản pháp lý (`legal`) hoặc học thuật (`academic`). Luôn khai báo rõ `applicable_profiles` và `exempt_profiles`.
4. Câu ví dụ sửa (`better_example`) phải tự vượt qua máy quét: Mọi chuỗi `better_example` trong quy tắc mới phải đạt `0` lỗi khi quét ở chế độ `all`. Câu sửa cũng phải giữ nguyên toàn bộ số liệu, từ phủ định và điều kiện so với `bad_example`.

## 3. Quy trình cập nhật quy tắc và từ vựng trên CSV

Toàn bộ từ vựng và quy tắc mặc định nằm tại hai tệp [data/vocab.csv](data/vocab.csv) và [data/grammar.csv](data/grammar.csv) (mã hóa `UTF-8 BOM` để mở và lưu trực tiếp trong Microsoft Excel mà không lỗi dấu tiếng Việt):

1. Thêm, sửa, tắt (`status=disabled`) hoặc xóa từ mượn (`loanword_universal`, `loanword_workplace`), cụm dịch ngược hoặc chêm từ ngoại lai (`reverse_calque`) và cụm văn mẫu cần tránh (`banned_phrase`) trong [data/vocab.csv](data/vocab.csv). Mọi dòng `reverse_calque` và `banned_phrase` đều phải có gợi ý sửa ngắn gọn, khớp lỗi tại cột `replacement_hint`.
2. Bật/tắt quy tắc, chỉnh trọng số, nhóm áp dụng hoặc thêm biểu thức chính quy mới trong [data/grammar.csv](data/grammar.csv), đồng thời cập nhật ngày `last_reviewed` trong `LOANWORDS_REVIEW_META` khi rà soát định kỳ theo [references/loanwords-and-exceptions.md](references/loanwords-and-exceptions.md).
3. Chạy `python -B scripts/vi_scanner.py selftest` và `python -B scripts/vi_scanner.py check-maintenance` để kiểm tra cú pháp CSV và hạn rà soát từ mượn.

## 4. Kiểm tra bắt buộc trước khi gửi Pull Request

Khi sửa bảng CSV, mã nguồn hoặc tài liệu, hãy giữ đồng bộ giữa [data/](data/) và [scripts/vi_scanner.py](scripts/vi_scanner.py). Đồng thời cập nhật khớp [SKILL.md](SKILL.md), [AGENTS.md](AGENTS.md), [README.md](README.md) cùng thư mục [references/](references/). Trước khi tạo Pull Request, hãy chạy đủ các lệnh kiểm tra sau:

```bash
ruff check scripts tests
ruff format --check scripts tests
mypy scripts tests
python -B scripts/check_code_limits.py
python -B scripts/vi_scanner.py selftest
python -B -m unittest discover -s tests -v
python -B scripts/vi_scanner.py scan SKILL.md AGENTS.md README.md CONTRIBUTING.md CHANGELOG.md .github/PULL_REQUEST_TEMPLATE.md references/rule-catalog.md references/voice-and-argument-patterns.md references/loanwords-and-exceptions.md --fail-on any --json
```
