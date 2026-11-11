#!/usr/bin/env python3
"""Kiểm tra giới hạn độ dài tệp, hàm, lớp và cấu trúc dữ liệu khai báo tại `[tool.code_limits]`."""

from __future__ import annotations

import ast
import fnmatch
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

DEFAULT_ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True, slots=True)
class CodeLimitsConfig:
    paths: tuple[str, ...]
    max_file_lines: int
    max_function_lines: int
    max_class_lines: int
    max_class_methods: int
    max_class_attributes: int
    max_object_literal_items: int
    data_module_globs: tuple[str, ...]
    max_data_object_literal_items: int


def load_code_limits(pyproject_path: Path) -> CodeLimitsConfig:
    raw = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    cfg = raw.get("tool", {}).get("code_limits", {})
    return CodeLimitsConfig(
        paths=tuple(cfg.get("paths", ("scripts", "tests"))),
        max_file_lines=int(cfg.get("max_file_lines", 500)),
        max_function_lines=int(cfg.get("max_function_lines", 55)),
        max_class_lines=int(cfg.get("max_class_lines", 260)),
        max_class_methods=int(cfg.get("max_class_methods", 15)),
        max_class_attributes=int(cfg.get("max_class_attributes", 20)),
        max_object_literal_items=int(cfg.get("max_object_literal_items", 65)),
        data_module_globs=tuple(cfg.get("data_module_globs", ())),
        max_data_object_literal_items=int(cfg.get("max_data_object_literal_items", 120)),
    )


def _span_lines(node: ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef) -> int:
    start = min((node.lineno, *(d.lineno for d in node.decorator_list)))
    end = node.end_lineno or node.lineno
    return end - start + 1


def _collect_init_self_attrs(fn_node: ast.FunctionDef | ast.AsyncFunctionDef) -> set[str]:
    attrs: set[str] = set()
    for sub in ast.walk(fn_node):
        targets: Sequence[ast.expr] = ()
        if isinstance(sub, ast.Assign):
            targets = sub.targets
        elif isinstance(sub, ast.AnnAssign):
            targets = (sub.target,)
        for tgt in targets:
            if isinstance(tgt, ast.Attribute) and isinstance(tgt.value, ast.Name) and tgt.value.id == "self":
                attrs.add(tgt.attr)
    return attrs


def _count_class_members(cls_node: ast.ClassDef) -> tuple[int, int]:
    methods = 0
    attrs: set[str] = set()
    for item in cls_node.body:
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
            methods += 1
            if item.name == "__init__":
                attrs.update(_collect_init_self_attrs(item))
        elif isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
            attrs.add(item.target.id)
        elif isinstance(item, ast.Assign):
            attrs.update(t.id for t in item.targets if isinstance(t, ast.Name))
    return methods, len(attrs)


def _check_class_node(cls_node: ast.ClassDef, rel_posix: str, cfg: CodeLimitsConfig) -> list[str]:
    errors: list[str] = []
    cls_lines = _span_lines(cls_node)
    if cls_lines > cfg.max_class_lines:
        errors.append(
            f"{rel_posix}:{cls_node.lineno}: Lớp '{cls_node.name}' dài {cls_lines} dòng "
            f"(vượt ngưỡng {cfg.max_class_lines})."
        )
    methods, attr_count = _count_class_members(cls_node)
    if methods > cfg.max_class_methods:
        errors.append(
            f"{rel_posix}:{cls_node.lineno}: Lớp '{cls_node.name}' có {methods} phương thức "
            f"(vượt ngưỡng {cfg.max_class_methods})."
        )
    if attr_count > cfg.max_class_attributes:
        errors.append(
            f"{rel_posix}:{cls_node.lineno}: Lớp '{cls_node.name}' có {attr_count} thuộc tính "
            f"(vượt ngưỡng {cfg.max_class_attributes})."
        )
    return errors


def _literal_size(node: ast.AST) -> tuple[str, int] | None:
    if isinstance(node, (ast.List, ast.Tuple, ast.Set)):
        return type(node).__name__.lower(), len(node.elts)
    if isinstance(node, ast.Dict):
        return "dict", len(node.keys)
    return None


def check_file_limits(file_path: Path, rel_posix: str, cfg: CodeLimitsConfig) -> list[str]:
    source = file_path.read_text(encoding="utf-8")
    errors: list[str] = []
    line_count = len(source.splitlines())
    if line_count > cfg.max_file_lines:
        errors.append(f"{rel_posix}:1: Tệp dài {line_count} dòng (vượt ngưỡng {cfg.max_file_lines}).")

    tree = ast.parse(source, filename=rel_posix)
    is_data_mod = any(fnmatch.fnmatch(rel_posix, pat) for pat in cfg.data_module_globs)
    lit_cap = cfg.max_data_object_literal_items if is_data_mod else cfg.max_object_literal_items

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            fn_lines = _span_lines(node)
            if fn_lines > cfg.max_function_lines:
                errors.append(
                    f"{rel_posix}:{node.lineno}: Hàm '{node.name}' dài {fn_lines} dòng "
                    f"(vượt ngưỡng {cfg.max_function_lines})."
                )
        elif isinstance(node, ast.ClassDef):
            errors.extend(_check_class_node(node, rel_posix, cfg))
        else:
            lit_info = _literal_size(node)
            if lit_info is not None and lit_info[1] > lit_cap:
                kind, count = lit_info
                lineno = getattr(node, "lineno", 1)
                errors.append(f"{rel_posix}:{lineno}: Literal '{kind}' chứa {count} phần tử (vượt ngưỡng {lit_cap}).")
    return errors


def check_repo_limits(root: Path = DEFAULT_ROOT) -> list[str]:
    cfg = load_code_limits(root / "pyproject.toml")
    violations: list[str] = []
    for rel_dir in cfg.paths:
        target = root / rel_dir
        if not target.exists():
            continue
        files = [target] if target.is_file() else sorted(target.rglob("*.py"))
        for py_file in files:
            rel_posix = py_file.relative_to(root).as_posix()
            violations.extend(check_file_limits(py_file, rel_posix, cfg))
    return violations


def main(argv: Sequence[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
    root = Path(argv[0]).resolve() if argv else DEFAULT_ROOT
    violations = check_repo_limits(root)
    if violations:
        for v in violations:
            print(v, file=sys.stderr)
        return 1
    print("CODE_LIMITS: PASS (0 vi phạm về độ dài tệp, hàm, lớp và cấu trúc dữ liệu)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
