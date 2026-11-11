#!/usr/bin/env python3
"""vi_scanner.py (v2.2.0) - Điểm vào công khai cho công cụ quét câu chữ, câu dài vòng vo và đo giọng văn tiếng Việt."""

from __future__ import annotations

import sys
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from _vi_cli import (  # noqa: E402
    build_parser,
    main,
    print_profile_report,
    print_scan_report,
    selftest,
)
from _vi_docx_dhdna import (  # noqa: E402
    extract_docx_text_and_meta,
    profile_text,
    read_utf8,
)
from _vi_masker import (  # noqa: E402
    SemanticMasker,
    _build_newline_offsets,
    _extract_regex_anchors,
    filter_markdown_table_columns,
    parse_ignore_cols,
    verify_text,
)
from _vi_rules_data import (  # noqa: E402
    ALL_ALLOWED_LOANWORDS,
    DEFAULT_GRAMMAR_CSV,
    DEFAULT_VOCAB_CSV,
    UNIVERSAL_NATURALIZED_LOANWORDS,
    WORKPLACE_TECH_LOANWORDS,
    build_default_rules,
    check_loanwords_maintenance,
    load_rule_bundle,
    load_vocab_catalog,
)
from _vi_scanner_core import ViScanner  # noqa: E402
from _vi_types import (  # noqa: E402
    ALL_PROFILES,
    LOANWORDS_REVIEW_META,
    SCHEMA_VERSION,
    USING_RE2,
    VERSION,
    Finding,
    Profile,
    RuleDefinition,
    ScanReport,
    Severity,
    ThresholdSpec,
    VocabCatalog,
)

__all__ = [
    "ALL_ALLOWED_LOANWORDS",
    "ALL_PROFILES",
    "DEFAULT_GRAMMAR_CSV",
    "DEFAULT_VOCAB_CSV",
    "LOANWORDS_REVIEW_META",
    "SCHEMA_VERSION",
    "UNIVERSAL_NATURALIZED_LOANWORDS",
    "USING_RE2",
    "VERSION",
    "WORKPLACE_TECH_LOANWORDS",
    "Finding",
    "Profile",
    "RuleDefinition",
    "ScanReport",
    "SemanticMasker",
    "Severity",
    "ThresholdSpec",
    "ViScanner",
    "VocabCatalog",
    "_build_newline_offsets",
    "_extract_regex_anchors",
    "build_default_rules",
    "build_parser",
    "check_loanwords_maintenance",
    "extract_docx_text_and_meta",
    "filter_markdown_table_columns",
    "load_rule_bundle",
    "load_vocab_catalog",
    "main",
    "parse_ignore_cols",
    "print_profile_report",
    "print_scan_report",
    "profile_text",
    "read_utf8",
    "selftest",
    "verify_text",
]

if __name__ == "__main__":
    raise SystemExit(main())
