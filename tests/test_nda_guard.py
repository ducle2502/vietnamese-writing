#!/usr/bin/env python3
"""Kiểm tra NDA: không ghi tên đơn vị, dự án hoặc khách hàng vào tệp được track."""

from __future__ import annotations

import os
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENV_NAME = "VIETNAMESE_WRITING_NDA_TERMS"


def _tracked_files() -> list[Path]:
    git_exe = shutil.which("git")
    if git_exe is None:
        return [p for p in ROOT.rglob("*") if p.is_file() and "raw" not in p.parts and ".git" not in p.parts]
    try:
        out = subprocess.run(  # noqa: S603
            [git_exe, "ls-files", "-z"],
            cwd=ROOT,
            capture_output=True,
            check=True,
            text=True,
            encoding="utf-8",
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        return [p for p in ROOT.rglob("*") if p.is_file() and "raw" not in p.parts and ".git" not in p.parts]
    return [ROOT / rel for rel in out.split("\0") if rel and not rel.startswith("raw/")]


class TestNdaGuard(unittest.TestCase):
    def test_tracked_files_do_not_contain_forbidden_names(self) -> None:
        """Đọc danh sách tên cấm từ biến môi trường ngoài repo và bỏ qua khi chưa đặt."""
        terms_path = os.environ.get(ENV_NAME)
        if not terms_path:
            self.skipTest(f"Chưa đặt {ENV_NAME}; bỏ qua kiểm tra NDA.")
        terms = [
            line.strip().casefold()
            for line in Path(terms_path).read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        ]
        if not terms:
            self.skipTest("Danh sách NDA rỗng.")
        hits: list[str] = []
        for path in _tracked_files():
            try:
                text = path.read_text(encoding="utf-8", errors="ignore").casefold()
            except OSError:
                continue
            hits.extend(str(path.relative_to(ROOT)) for term in terms if term in text)
        hits = sorted(set(hits))
        self.assertEqual(
            hits,
            [],
            "Phát hiện tên cấm trong tệp được track: " + "; ".join(hits),
        )


if __name__ == "__main__":
    unittest.main()
