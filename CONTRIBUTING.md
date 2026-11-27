# Hướng dẫn đóng góp (Contributing)

Tài liệu hướng dẫn thiết lập môi trường, nguyên tắc thêm quy tắc vào [scripts/vi_scanner.py](scripts/vi_scanner.py), cách sửa hai bảng CSV và các bước kiểm tra bắt buộc trước khi mở Pull Request.

## 1. Yêu cầu môi trường

Công cụ chạy trên thư viện chuẩn của `Python 3.11+` ở Windows, macOS và Linux (nếu có sẵn `google-re2`, bộ quét tự dùng để tăng tốc). Khi phát triển mã nguồn, cài thêm `mypy`, `pytest` và `ruff` theo cấu hình tại [pyproject.toml](pyproject.toml) để kiểm tra kiểu tĩnh, định dạng và chạy bộ kiểm thử.

```bash
git clone https://github.com/ducle2502/vietnamese-writing.git
cd vietnamese-writing
python -m pip install "mypy>=1.11" "pytest>=8.0" "ruff>=0.8"
python -B scripts/vi_scanner.py selftest
python -B -m pytest -v
```

> Lưu ý: Truyền thêm cờ `-B` (`python -B`) khi chạy lệnh cục bộ để Python không sinh thư mục `__pycache__` trong cây thư mục.

## 2. Nguyên tắc thiết kế quy tắc mới

Mỗi quy tắc mới trong [scripts/vi_scanner.py](scripts/vi_scanner.py) cần đáp ứng 4 yêu cầu sau:

1. Không ghi cố định dữ liệu nội bộ: Tuyệt đối không đưa tên hệ thống, mã bảng riêng, tên phòng ban hay số liệu dự án vào mã nguồn chung. Các quy tắc đặc thù của riêng tổ chức phải nạp qua tham số `--custom-rules <tệp.json>`.
2. Khớp tuyến tính an toàn: Biểu thức chính quy không chứa lượng từ lồng nhau gây treo máy trên văn bản dài. Mọi quy tắc phải qua bài kiểm thử chuỗi lặp hơn `200.000` ký tự dưới `500 ms` trong [tests/test_repo_and_limits.py](tests/test_repo_and_limits.py).
3. Phân định rõ ngữ cảnh ngoại lệ (`exempt_profiles`): Một câu có thể gượng gạo trong tin bài chung (`general`) nhưng hoàn toàn hợp lệ trong hợp đồng pháp lý (`legal`) hay bài báo khoa học (`academic`). Khai báo rõ `applicable_profiles` và `exempt_profiles`.
4. Ví dụ sửa mẫu phải tự qua máy quét: Mọi `better_example` của quy tắc mới phải đạt `0` lỗi ở chế độ `all` và bảo toàn đủ số liệu, phủ định, điều kiện so với `bad_example`.

## 3. Quy trình cập nhật từ vựng và quy tắc trên CSV

Toàn bộ từ vựng và quy tắc nằm tại [data/vocab.csv](data/vocab.csv) và [data/grammar.csv](data/grammar.csv) (chuẩn `UTF-8 BOM` mở trực tiếp trong Microsoft Excel không lỗi dấu tiếng Việt):

1. Thêm, sửa, tắt (`status=disabled`) hoặc xóa từ mượn (`loanword_universal`, `loanword_workplace`), cụm dịch ngược hoặc chêm từ ngoại lai (`reverse_calque`) và cụm văn mẫu (`banned_phrase`) trong [data/vocab.csv](data/vocab.csv). Mọi dòng `reverse_calque` và `banned_phrase` phải kèm gợi ý sửa ngắn gọn, khớp lỗi ở cột `replacement_hint`.
2. Bật hoặc tắt quy tắc, chỉnh trọng số, nhóm áp dụng hay thêm regex mới trong [data/grammar.csv](data/grammar.csv). Khi cập nhật bảng CSV bằng công cụ tự động, ghi qua Python với `encoding="utf-8-sig"` để giữ nguyên 3 byte BOM.
3. Chạy `python -B scripts/vi_scanner.py selftest` và `python -B scripts/vi_scanner.py check-maintenance` để kiểm tra cú pháp CSV và hạn rà soát từ mượn.

## 4. Kiểm tra bắt buộc trước khi gửi Pull Request

Khi sửa bảng CSV, mã nguồn hoặc tài liệu, giữ đồng bộ giữa [data/](data/), [scripts/vi_scanner.py](scripts/vi_scanner.py), [SKILL.md](SKILL.md), [AGENTS.md](AGENTS.md), [README.md](README.md) và thư mục [references/](references/). Trước khi mở Pull Request, chạy đủ các lệnh sau:

```bash
ruff check scripts tests
ruff format --check scripts tests
mypy scripts tests
python -B scripts/vi_scanner.py selftest
python -B -m pytest -v
python -B scripts/vi_scanner.py scan SKILL.md AGENTS.md README.md CONTRIBUTING.md CHANGELOG.md .github/PULL_REQUEST_TEMPLATE.md references/rule-catalog.md references/voice-and-argument-patterns.md references/loanwords-and-exceptions.md references/pattern-bank.md references/sentence-craft-and-syntax.md --fail-on any --json
```
