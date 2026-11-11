## Tóm tắt thay đổi

<!-- Mô tả ngắn gọn thay đổi trong 1 đến 3 câu. -->

## Issue liên quan

<!-- Ví dụ: Closes #1 -->

## Hạng mục tác động

- [ ] `SKILL.md` / `AGENTS.md` (Hướng dẫn cho Agent)
- [ ] `data/vocab.csv` / `data/grammar.csv` (Bảng từ vựng và quy tắc chuẩn `UTF-8 BOM`)
- [ ] `scripts/` (Bộ máy quét `vi_scanner`, `SemanticMasker` hoặc `verify`)
- [ ] `references/` (`rule-catalog.md`, `voice-and-argument-patterns.md`, `loanwords-and-exceptions.md`)
- [ ] `tests/` / `evals/evals.json`
- [ ] `README.md` / `CONTRIBUTING.md` / `CHANGELOG.md` / `.github/`

## Danh mục kiểm tra trước khi gộp

- [ ] Không ghi cố định tên hệ thống, mã bảng hay con số đặc thù của dự án nội bộ vào mã nguồn
- [ ] Đã giữ đồng bộ nội dung giữa `data/`, `scripts/vi_scanner.py`, `SKILL.md`, `AGENTS.md`, `README.md` và `references/`
- [ ] Chạy `ruff check scripts tests`, `ruff format --check scripts tests` và `mypy scripts tests` đạt `0` lỗi
- [ ] Chạy `python -B scripts/vi_scanner.py selftest` và `python -B -m pytest -v` đạt 100%
- [ ] Chạy `python -B scripts/vi_scanner.py scan` trên toàn bộ 9 tệp `.md` trong repo đạt `0` lỗi
