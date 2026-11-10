## Tóm tắt thay đổi

<!-- Mô tả ngắn gọn thay đổi trong 1 đến 3 câu. -->

## Issue liên quan

<!-- Ví dụ: Closes #1 -->

## Hạng mục tác động

- [ ] `SKILL.md` / `AGENTS.md` (Hướng dẫn cho Agent)
- [ ] `scripts/vi_scanner.py` (Quy tắc quét, `SemanticMasker`, `verify` hoặc danh sách từ mượn)
- [ ] `references/` (`rule-catalog.md`, `loanwords-and-exceptions.md`)
- [ ] `tests/test_vi_scanner.py` / `evals/evals.json`
- [ ] `README.md` / `CONTRIBUTING.md` / `CHANGELOG.md` / `.github/`

## Danh mục kiểm tra trước khi gộp

- [ ] Không gắn cứng tên hệ thống, mã bảng hay con số đặc thù của dự án nội bộ vào mã nguồn
- [ ] Đã đồng bộ nội dung giữa `scripts/vi_scanner.py`, `SKILL.md`, `README.md` và `references/`
- [ ] Chạy `python -B scripts/vi_scanner.py selftest` và `python -B -m unittest discover -s tests -v` đạt 100%
- [ ] Chạy `python -B scripts/vi_scanner.py scan` trên toàn bộ các tệp `.md` trong repo đạt `0` lỗi
