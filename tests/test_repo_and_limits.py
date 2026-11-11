#!/usr/bin/env python3
"""Bộ kiểm thử an toàn dữ kiện, hiệu năng thuật toán, giới hạn độ dài mã nguồn và cấu trúc repo."""

from __future__ import annotations

import contextlib
import csv
import dataclasses
import datetime as dt
import hashlib
import io
import json
import re
import statistics
import sys
import tempfile
import time
import unittest
import zipfile
from pathlib import Path
from typing import ClassVar

TESTS_DIR = Path(__file__).resolve().parent
ROOT = TESTS_DIR.parent
SCRIPTS_DIR = ROOT / "scripts"
for _dir in (str(SCRIPTS_DIR), str(TESTS_DIR)):
    if _dir not in sys.path:
        sys.path.insert(0, _dir)

from check_code_limits import check_file_limits, check_repo_limits, load_code_limits  # noqa: E402
from vi_scanner import (  # noqa: E402
    DEFAULT_GRAMMAR_CSV,
    DEFAULT_VOCAB_CSV,
    UNIVERSAL_NATURALIZED_LOANWORDS,
    WORKPLACE_TECH_LOANWORDS,
    SemanticMasker,
    ViScanner,
    _build_newline_offsets,
    _extract_regex_anchors,
    check_loanwords_maintenance,
    extract_docx_text_and_meta,
    main,
    verify_text,
)

_MD_DOCS: tuple[Path, ...] = (
    ROOT / "SKILL.md",
    ROOT / "AGENTS.md",
    ROOT / "README.md",
    ROOT / "CONTRIBUTING.md",
    ROOT / "CHANGELOG.md",
    ROOT / ".github" / "PULL_REQUEST_TEMPLATE.md",
    ROOT / "references" / "rule-catalog.md",
    ROOT / "references" / "voice-and-argument-patterns.md",
    ROOT / "references" / "loanwords-and-exceptions.md",
)


class TestScannerSafetyAndRepoQuality(unittest.TestCase):
    scanner: ClassVar[ViScanner]

    @classmethod
    def setUpClass(cls) -> None:
        cls.scanner = ViScanner()

    def test_semantic_invariants_and_verify_safety(self) -> None:
        """Mọi ví dụ sửa mẫu trong 42 quy tắc phải bảo toàn dữ kiện gốc và bắt đúng lỗi mục tiêu."""
        self.assertEqual(len(self.scanner.rules), 42)
        for rule in self.scanner.rules.values():
            if rule.rule_id == "VIS-FMT-005":
                continue
            bad_hits = {f.rule_id for f in self.scanner.scan_text(rule.bad_example, profile="all").findings}
            self.assertIn(rule.rule_id, bad_hits, f"bad_example của {rule.rule_id} không kích hoạt chính nó")
            inv_bad = SemanticMasker.extract_invariants(rule.bad_example)
            inv_better = SemanticMasker.extract_invariants(rule.better_example)
            if not inv_bad["numbers"] and inv_better["numbers"]:
                inv_better = {**inv_better, "numbers": []}
            ok, errs = SemanticMasker.validate_invariants(inv_bad, inv_better, strict_negations_and_modals=False)
            self.assertTrue(ok, f"Rule {rule.rule_id} làm lệch dữ kiện mẫu: {errs}")

        self.assertFalse(
            verify_text(
                "Phương án này có thể giảm 15% thời gian chờ nếu lưu lượng ổn định.",
                "Phương án này giảm 15% thời gian chờ nếu lưu lượng ổn định.",
            )["passed"]
        )
        self.assertFalse(
            verify_text(
                "Chạy lệnh `python scripts/vi_scanner.py scan a.md` ngày 10/11/2026.",
                "Chạy lệnh `python scripts/vi_scanner.py scan b.md` ngày 10/11/2026.",
            )["passed"]
        )

    def test_redos_linear_time_on_210k_chars(self) -> None:
        """Chuỗi tấn công lặp trên 210.000 ký tự phải quét xong dưới 500 ms."""
        adversarial = ("Trong bối cảnh nền kinh tế số " * 7200) + "!"
        self.assertGreater(len(adversarial), 210_000)
        t0 = time.perf_counter()
        _ = self.scanner.scan_text(adversarial)
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        self.assertLess(elapsed_ms, 500.0, f"Quét quá chậm ({elapsed_ms:.1f} ms), nghi ngờ ReDoS!")

    def test_maintenance_schedule_and_cli(self) -> None:
        """Kiểm tra cơ chế nhắc rà soát hàng quý/năm cho danh sách từ tiếng Anh quen dùng."""
        self.assertFalse(check_loanwords_maintenance(dt.date(2026, 12, 1))["due_for_quarterly_review"])
        due_q = check_loanwords_maintenance(dt.date(2027, 3, 1))
        self.assertTrue(due_q["due_for_quarterly_review"])
        self.assertFalse(due_q["overdue_annual_review"])
        self.assertTrue(check_loanwords_maintenance(dt.date(2027, 12, 1))["overdue_annual_review"])

        with tempfile.TemporaryDirectory() as tmp:
            sample = Path(tmp) / "clean.md"
            sample.write_text("Doanh thu quý IV đạt 120 tỷ đồng, tăng 10% so với kế hoạch.\n", encoding="utf-8")
            out_json = Path(tmp) / "report.json"
            with contextlib.redirect_stdout(io.StringIO()):
                rc = main(["scan", str(sample), "--json", "--output", str(out_json)])
            self.assertEqual(rc, 0)
            parsed = json.loads(out_json.read_text(encoding="utf-8"))
            self.assertEqual((parsed["profile"], parsed["findings_count"]), ("all", 0))

    def test_algorithms_data_structures_and_docx_xml_safety(self) -> None:
        """Kiểm tra tìm kiếm nhị phân dòng/cột, cửa sổ trượt MATTR, bộ lọc neo regex và chặn XML XXE."""
        self.assertEqual((len(UNIVERSAL_NATURALIZED_LOANWORDS), len(WORKPLACE_TECH_LOANWORDS)), (63, 114))

        multi_line = "Báo cáo quý I\n\nĐoạn tiếng Việt có dấu: 59,92% — đạt yêu cầu.\nDòng cuối"
        nl_offsets = _build_newline_offsets(multi_line)
        for off in range(len(multi_line) + 1):
            last_nl = multi_line.rfind("\n", 0, off)
            exp_col = off + 1 if last_nl == -1 else off - last_nl
            self.assertEqual(
                ViScanner._offset_to_line_col(multi_line, off, nl_offsets),
                (multi_line.count("\n", 0, off) + 1, exp_col),
            )
            nl_pos = multi_line.find("\n", off)
            self.assertEqual(
                ViScanner._line_end_offset(multi_line, off, nl_offsets),
                len(multi_line) if nl_pos == -1 else nl_pos,
            )

        words = [f"tu_{i % 7}" for i in range(65)]
        expected_mattr = statistics.mean(len(set(words[i : i + 12])) / 12.0 for i in range(len(words) - 11))
        self.assertAlmostEqual(ViScanner._compute_sliding_mattr(words, window=12), expected_mattr, places=12)

        unanchored = ViScanner()
        unanchored._rule_anchors.clear()
        for rid, rule in self.scanner.rules.items():
            if not rule.regex_or_algorithm.startswith("ALGO:") and rule.regex_or_algorithm != "VOCAB":
                self.assertTrue(_extract_regex_anchors(rule.regex_or_algorithm), f"Rule {rid} thiếu neo literal")
            r_fast = self.scanner.scan_text(rule.bad_example, profile="all")
            r_raw = unanchored.scan_text(rule.bad_example, profile="all")
            self.assertEqual(
                [(f.rule_id, f.line, f.col) for f in r_fast.findings],
                [(f.rule_id, f.line, f.col) for f in r_raw.findings],
            )

        with tempfile.TemporaryDirectory() as tmp:
            bad_docx = Path(tmp) / "xxe_attempt.docx"
            xxe_xml = (
                '<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE foo [<!ENTITY xxe "secret">]>'
                '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
                "<w:body><w:p><w:r><w:t>Nội dung</w:t></w:r></w:p></w:body></w:document>"
            )
            with zipfile.ZipFile(bad_docx, "w") as zf:
                zf.writestr("word/document.xml", xxe_xml)
            with self.assertRaises(ValueError):
                extract_docx_text_and_meta(bad_docx)

    def test_code_limits_and_modularity_enforcement(self) -> None:
        """Đảm bảo 100% mã nguồn tuân thủ `[tool.code_limits]` và trình kiểm tra bắt đúng vi phạm giả lập."""
        self.assertEqual(check_repo_limits(ROOT), [])
        strict_cfg = dataclasses.replace(
            load_code_limits(ROOT / "pyproject.toml"),
            max_file_lines=5,
            max_function_lines=2,
            max_object_literal_items=2,
        )
        with tempfile.TemporaryDirectory() as tmp:
            sample_py = Path(tmp) / "tiny.py"
            sample_py.write_text(
                "ITEMS = [1, 2, 3]\ndef f():\n    a = 1\n    b = 2\n    return a + b\n# pad\n",
                encoding="utf-8",
            )
            errs = check_file_limits(sample_py, "tiny.py", strict_cfg)
            self.assertEqual(len(errs), 3)

    def test_skill_repo_structure_manifests_and_self_lint(self) -> None:
        """Kiểm tra cấu trúc chuẩn Skill repo, liên kết nội bộ và tự quét sạch toàn bộ tài liệu."""
        for req_rel in (
            "SKILL.md",
            "LICENSE",
            "AGENTS.md",
            "pyproject.toml",
            "data/vocab.csv",
            "data/grammar.csv",
            "scripts/vi_scanner.py",
            "scripts/check_code_limits.py",
            "references/rule-catalog.md",
            "references/loanwords-and-exceptions.md",
            "assets/banner-dark.svg",
            "assets/banner-light.svg",
            ".github/workflows/ci.yml",
            ".github/PULL_REQUEST_TEMPLATE.md",
        ):
            self.assertTrue((ROOT / req_rel).exists(), f"Thiếu {req_rel}")

        fm_match = re.match(r"\A---\n([\s\S]+?)\n---\n", (ROOT / "SKILL.md").read_text(encoding="utf-8"))
        self.assertIsNotNone(fm_match)
        for manifest_rel in (
            "package.json",
            ".claude-plugin/plugin.json",
            ".claude-plugin/marketplace.json",
            ".cursor-plugin/plugin.json",
        ):
            self.assertEqual(
                json.loads((ROOT / manifest_rel).read_text(encoding="utf-8"))["name"], "vietnamese-writing"
            )

        link_re = re.compile(r"\[[^\]]+\]\(([^)#\s]+)")
        for doc_path in _MD_DOCS:
            txt = doc_path.read_text(encoding="utf-8")
            for m in link_re.finditer(txt):
                target = m.group(1)
                if "://" not in target and not target.startswith("mailto:"):
                    self.assertTrue((doc_path.parent / target).resolve().exists(), f"Hỏng link {target}")
            rep = self.scanner.scan_text(txt, profile="all")
            self.assertEqual(rep.findings_count, 0, f"{doc_path.name}: {rep.findings}")
            self.assertEqual(rep.stylometry.get("canh_bao", []), [], f"{doc_path.name}: {rep.stylometry}")

        for rule in self.scanner.rules.values():
            self.assertEqual(self.scanner.scan_text(rule.better_example, profile="all").findings_count, 0, rule.rule_id)

        vap_txt = (ROOT / "references" / "voice-and-argument-patterns.md").read_text(encoding="utf-8")
        for ln in vap_txt.splitlines():
            if ln.startswith('| "'):
                for cell in [c.strip().strip('"') for c in ln.strip().strip("|").split("|")[1:]]:
                    self.assertEqual(self.scanner.scan_text(cell, profile="all").findings_count, 0, cell)

    def test_zero_hardcoded_project_leaks_in_repo(self) -> None:
        """Đảm bảo không còn mã băm hay số liệu nội bộ cũ rò rỉ trong bất kỳ tệp nào của repo."""
        forbidden_sha256 = {
            "de5361d8112f0dde7953be6b17d6b77a3b045f4cc4c7de3b3f4795c0804c4972",
            "c46de749138d2338c289accea4b71af71cce21ca378e42cf73273c1a1fb00e7b",
            "55b3da6b0f5d7a66861544492455a146aac5c3f2bd6810969bad7756d43c9a99",
            "bd3dcf25ed023afb49c1ad1f154f4eeb7d8e51087718fc5cbc284ba556683280",
            "d9947bbf8f34c7bd1f3739112048993f8253f1cabe6f8441736d6ca2e78d9252",
            "3ec20fe6b71dc063cbbd7c283c606c30fe10577857c34d2563f61400b49078ad",
        }
        for csv_path in (DEFAULT_VOCAB_CSV, DEFAULT_GRAMMAR_CSV):
            self.assertTrue(csv_path.read_bytes().startswith(b"\xef\xbb\xbf"), f"{csv_path.name} thiếu UTF-8 BOM")
        tracked = [
            *_MD_DOCS,
            ROOT / "pyproject.toml",
            *(ROOT / "data").glob("*.csv"),
            *SCRIPTS_DIR.glob("*.py"),
            *TESTS_DIR.glob("*.py"),
        ]
        for fpath in tracked:
            content = fpath.read_text(encoding="utf-8-sig")
            for tok in set(re.findall(r"[A-Za-z0-9_./-]+", content)):
                self.assertNotIn(hashlib.sha256(tok.lower().encode("utf-8")).hexdigest(), forbidden_sha256, fpath.name)
            self.assertNotRegex(content, r"\b212\s+đơn vị kinh doanh\b|\b226\s+đơn vị\b")


class TestCsvCrudAndRowInvariants(unittest.TestCase):
    def test_excel_csv_crud_vocab_and_grammar(self) -> None:
        """Kiểm tra thêm/sửa/tắt/xóa quy tắc trên CSV kiểu Excel (BOM, dấu `;`, số thập phân `,`)."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_dir = Path(tmp)
            vocab_csv = tmp_dir / "vocab.csv"
            grammar_csv = tmp_dir / "grammar.csv"
            vocab_csv.write_text(
                "term;kind;rule_id;replacement_hint;status;note\n"
                "duckdb;loanword_universal;VIS-LEX-002;;active;Cho phép toàn cục\n"
                "cơ sở dữ liệu con vịt;reverse_calque;VIS-LEX-002;DuckDB;TRUE;Dịch ngược\n"
                "siêu phẩm tối thượng;banned_phrase;VIS-CUSTOM-001;Bỏ từ tán dương;1;Cụm mới\n"
                "cụm đã tắt;banned_phrase;VIS-CUSTOM-001;;FALSE;Đã tắt\n",
                encoding="utf-8-sig",
            )
            grammar_csv.write_text(
                "rule_id;status;category;pattern_type;regex_or_algo;severity;weight;profiles;"
                "threshold;exceptions;description_vi;bad_example;better_example;source_url;evidence_strength\n"
                "VIS-LEX-002;active;VOICE_AND_STRUCTURE;morphological_lexical;"
                "ALGO:LOANWORD_AND_FOREIGN_TOKEN_CHECK;info;0,45;all;1/doc;none;Từ mượn;;;;medium\n"
                "VIS-CUSTOM-001;active;CUSTOM;dictionary;VOCAB;warning;0,85;audit_report|general;"
                "1/doc;none;Cấm từ phóng đại nội bộ;;;;custom\n"
                "VIS-DISABLED-001;0;CUSTOM;regex;(?i)\\bcấm\\b;error;1,0;all;1/doc;none;Đã tắt;;;;custom\n",
                encoding="utf-8-sig",
            )
            custom_scanner = ViScanner(vocab_path=vocab_csv, grammar_path=grammar_csv)
            self.assertEqual(set(custom_scanner.rules), {"VIS-LEX-002", "VIS-CUSTOM-001"})
            rep = custom_scanner.scan_text(
                "Báo cáo lưu trên duckdb, tránh gọi cơ sở dữ liệu con vịt hay siêu phẩm tối thượng hoặc cụm đã tắt.",
                profile="audit_report",
            )
            by_id = {f.rule_id: f for f in rep.findings}
            self.assertEqual(set(by_id), {"VIS-LEX-002", "VIS-CUSTOM-001"})
            self.assertIn("DuckDB", by_id["VIS-LEX-002"].suggestion_vi)
            self.assertEqual(by_id["VIS-CUSTOM-001"].suggestion_vi, "Bỏ từ tán dương")
            self.assertAlmostEqual(by_id["VIS-CUSTOM-001"].weight, 0.85)

            bad_vocab = tmp_dir / "bad_vocab.csv"
            bad_vocab.write_text(
                "term,kind,rule_id,replacement_hint,status,note\n"
                "siêu phẩm tối thượng,banned_phrase,VIS-CUSTOM-001,,active,\n"
                "x,banned_phrase,VIS-MISSING,,active,\n",
                encoding="utf-8-sig",
            )
            with self.assertRaisesRegex(ValueError, "VIS-MISSING"):
                ViScanner(vocab_path=bad_vocab, grammar_path=grammar_csv)

    def test_vocab_and_grammar_csv_row_count_and_hint_coherence(self) -> None:
        """Bảo toàn nguyên vẹn 2.011 dòng `vocab.csv`, 42 quy tắc `grammar.csv` và chất lượng `replacement_hint`."""
        vocab_raw = DEFAULT_VOCAB_CSV.read_text(encoding="utf-8-sig")
        self.assertEqual(len(vocab_raw.splitlines()), 2012)
        vocab_rows = list(csv.DictReader(io.StringIO(vocab_raw)))
        self.assertEqual(len(vocab_rows), 2011)

        grammar_raw = DEFAULT_GRAMMAR_CSV.read_text(encoding="utf-8-sig")
        self.assertEqual(len(grammar_raw.splitlines()), 53)
        grammar_rows = list(csv.DictReader(io.StringIO(grammar_raw)))
        self.assertEqual(len(grammar_rows), 42)
        self.assertTrue(all(r["status"] == "active" for r in grammar_rows))

        seen_terms: set[str] = set()
        bad_meta_re = re.compile(r":\s|[()+]|[\u4e00-\u9fff]|[\u0400-\u04ff]")
        trailing_fn_re = re.compile(r"[A-Za-zÀ-ỹĐđ.!?]\s*\d{1,3}$")
        for row in vocab_rows:
            self.assertEqual(row["status"], "active")
            t_key = " ".join(row["term"].split()).casefold()
            self.assertNotIn(t_key, seen_terms, f"Trùng term_key: {t_key}")
            seen_terms.add(t_key)
            self.assertIsNone(bad_meta_re.search(row["term"]), f"Term lẫn chú thích: {row['term']}")
            if row["kind"] in ("banned_phrase", "reverse_calque"):
                hint = row["replacement_hint"].strip()
                self.assertTrue(hint, f"Thiếu replacement_hint cho: {row['term']}")
                self.assertNotEqual(t_key, hint.casefold(), f"Hint trùng term: {row['term']}")
                self.assertIsNone(trailing_fn_re.search(hint), f"Dính số chân trang PDF: {hint}")


if __name__ == "__main__":
    unittest.main()
