"""Giao diện dòng lệnh (CLI), trình in báo cáo và tự kiểm tra nhanh cho `vi_scanner`."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
import zipfile
from pathlib import Path
from typing import TYPE_CHECKING, Any

from _vi_docx_dhdna import extract_docx_text_and_meta, profile_text, read_utf8
from _vi_masker import parse_ignore_cols, verify_text
from _vi_rules_data import check_loanwords_maintenance
from _vi_scanner_core import ViScanner
from _vi_types import (
    ALL_PROFILES,
    VERSION,
    DocxMetadata,
    Profile,
    ProfileReport,
    RuleSummaryItem,
    ScanReport,
)

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence


def print_profile_report(prof_data: ProfileReport) -> None:
    st = prof_data["stylometry"]
    dm = prof_data["dhdna_voice_metrics"]
    va = prof_data["voice_archetype"]
    print(f"HỒ SƠ GIỌNG VĂN (DHDNA & STYLOMETRY): {prof_data['file']} (SHA256[:16]={prof_data['sha256_16']})")
    print(
        f"  Tổng số từ: {prof_data['word_count_total']} "
        f"(Văn xuôi: {prof_data['word_count_prose']} từ, {st.get('so_doan', 0)} đoạn, "
        f"TB {st.get('cau_trung_binh_doan', 0)} câu/đoạn)"
    )
    print(
        f"  Nhịp câu: {st.get('so_cau', 0)} câu | TB {st.get('dai_cau_tb', 0)} từ/câu "
        f"(CV={st.get('bien_dong_do_dai_cau_cv', 0)}) | MATTR-50={st.get('mattr_cua_so_50', 0)}"
    )
    print(
        f"  Mật độ số liệu: {dm['mat_do_so_tren_1000_tu']}/1.000 từ | "
        f"Tỷ lệ % kèm Tử/Mẫu số: {int(dm['ty_le_phan_tram_kem_tu_mau'] * 100)}%"
    )
    print(
        f"  Chỉ dấu DHDNA: Ranh giới bằng chứng (D12)={dm['ranh_gioi_bang_chung_d12']} | "
        f"Cổng chặn (D6)={dm['cong_chan_dieu_kien_d6']} | "
        f"Tách hoạt động trung gian (D1)={dm['tach_hoat_dong_trung_gian_d1']} | "
        f"Neo trễ hạn (D11)={dm['neo_thoi_gian_tre_han_d11']}"
    )
    print(
        f"  Cấu trúc: Nhãn đoạn dấu chấm={dm['nhan_doan_ket_thuc_dau_cham']} | "
        f"Tiêu đề 2 vế={dm['tieu_de_hai_ve_doi_sanh']} | "
        f"Đối chứng đa nguồn={dm['tam_giac_doi_chung_da_nguon']} | "
        f"Tình thái 'có thể'={dm['tu_tinh_thai_don_co_the']} (chồng rào đón={dm['chong_tu_rao_don']})"
    )
    if dm["ung_vien_lech_mau_so"]:
        print(f"  [CẢNH BÁO MẪU SỐ] Các cụm có nhiều mẫu số khác nhau: {dm['ung_vien_lech_mau_so']}")
    mismatch = (prof_data.get("docx_metadata") or {}).get("template_title_mismatch")
    if mismatch:
        print(f"  [CẢNH BÁO TỆP MẪU] {mismatch}")
    print(f"  Nhận diện giọng văn: [{va['code']}] {va['description_vi']}")


def print_scan_report(report: ScanReport, label: str) -> None:
    print(f"Tệp: {label} | Chế độ lọc: {report.profile}")
    print(
        f"Từ: {report.word_count} | Đoạn: {report.paragraph_count} | "
        f"Tổng tín hiệu: {report.findings_count} "
        f"(Lỗi: {report.error_count}, Cảnh báo: {report.warning_count}, Gợi ý: {report.info_count}) | "
        f"Mật độ: {report.findings_per_1000_words}/1.000 từ | Thời gian: {report.elapsed_ms} ms"
    )
    if report.stylometry:
        st = report.stylometry
        print(
            f"Nhịp câu: {st.get('so_cau', 0)} câu | TB {st.get('dai_cau_tb', 0)} từ/câu "
            f"(CV={st.get('bien_dong_do_dai_cau_cv', 0)}) | MATTR={st.get('mattr_cua_so_50', 0)} | "
            f"Hán-Việt hành chính={st.get('han_viet_hanh_chinh_tren_1000', 0)}/1.000 từ"
        )
        for w in st.get("canh_bao", []):
            print(f"  [NHỊP HỌC] {w}")
    if report.maintenance_due:
        print(
            "[NHẮC BẢO TRÌ] Danh sách từ tiếng Anh quen dùng đã đến kỳ rà soát hàng quý. "
            "Chạy `python scripts/vi_scanner.py check-maintenance` để xem chi tiết."
        )
    for idx, f in enumerate(report.findings, 1):
        profs_txt = (
            "mọi nhóm văn bản"
            if not f.exempt_profiles
            else f"áp dụng: {', '.join(f.applicable_profiles)} | miễn: {', '.join(f.exempt_profiles)}"
        )
        print(f"\n#{idx} [{f.severity.upper()}] {f.rule_id} ({f.category}) dòng {f.line}:{f.col} (w={f.weight})")
        print(f"  Ngữ cảnh: {profs_txt}")
        print(f"  Khớp: {f.matched_text!r}")
        print(f"  Vấn đề: {f.description_vi}")
        print(f"  Hướng sửa: {f.suggestion_vi}")
    print(f"\n{report.disclaimer}")


def _require(*, ok: bool, message: str) -> None:
    if not ok:
        raise RuntimeError(message)


def selftest() -> int:
    scanner = ViScanner()
    dirty = (
        "Chắc chắn rồi! Dưới đây là bản phân tích. "
        "Giải pháp này không chỉ đơn thuần là công cụ, mà còn là ngọn hải đăng dẫn đường. "
        "Báo cáo được phê duyệt bởi hội đồng vào ngày 10/01/2026."
    )
    clean = (
        "Hội đồng quản trị đã phê duyệt báo cáo tài chính năm 2025 vào ngày 10/01/2026. "
        "Doanh thu quý IV đạt 128 tỷ đồng, tăng 14,5% so với cùng kỳ năm trước."
    )
    rep_all = scanner.scan_text(dirty)
    rep_clean = scanner.scan_text(clean)
    _require(ok=rep_all.profile == "all", message="Chế độ mặc định của scan_text phải là 'all'.")
    _require(ok=rep_all.findings_count >= 3, message=f"Kỳ vọng >= 3 lỗi, nhận {rep_all.findings_count}")
    _require(ok=rep_clean.findings_count == 0, message=f"Báo nhầm trên câu sạch: {rep_clean.findings}")
    _require(
        ok=not verify_text("Tỷ lệ đạt 59,92% ngày 25/09/2026.", "Tỷ lệ đạt 60% ngày 25/09/2026.")["passed"],
        message="verify_text phải phát hiện sai lệch số liệu.",
    )
    _require(
        ok=verify_text("Tỷ lệ đạt 59,92% ngày 25/09/2026.", "Ngày 25/09/2026, tỷ lệ đạt 59,92%.")["passed"],
        message="verify_text phải cho qua khi số liệu và ngày tháng được bảo toàn.",
    )
    prof = profile_text(clean, label="selftest")
    _require(ok=prof["stylometry"]["so_cau"] == 2, message="Kỳ vọng đếm đúng 2 câu văn xuôi.")
    _require(ok="dhdna_voice_metrics" in prof, message="Thiếu trường dhdna_voice_metrics.")
    print("SELFTEST: PASS")
    return 0


def _add_scan_and_profile_parsers(sub: Any, profile_choices: Sequence[str]) -> None:
    scan_p = sub.add_parser("scan", help="Quét tệp UTF-8 hoặc .docx (mặc định xuất đủ 100%% các nhóm văn bản)")
    scan_p.add_argument("files", metavar="file", nargs="*", default=["-"], help="Một hoặc nhiều tệp hoặc '-' (stdin)")
    scan_p.add_argument("--profile", choices=profile_choices, default="all")
    scan_p.add_argument("--ignore-table-cols", default="", help="Các cột bảng (từ 1, ví dụ '2,3') cần bỏ qua")
    scan_p.add_argument("--custom-rules", type=Path, help="Tệp JSON chứa quy tắc bổ sung riêng")
    scan_p.add_argument("--json", action="store_true", help="Xuất kết quả JSON ra stdout")
    scan_p.add_argument("--output", type=Path, help="Ghi kết quả JSON ra tệp")
    scan_p.add_argument("--fail-on", choices=["any", "warning", "error", "never"], default="any")

    prof_p = sub.add_parser("profile", help="Đo 18 chỉ số nhịp câu (stylometry) và 12 chỉ số giọng văn DHDNA")
    prof_p.add_argument("file", nargs="?", default="-")
    prof_p.add_argument("--ignore-table-cols", default="")
    prof_p.add_argument("--json", action="store_true")
    prof_p.add_argument("--output", type=Path)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="vi_scanner",
        description="Công cụ rà lỗi câu chữ máy móc, câu dài vòng vo, đo hồ sơ giọng văn DHDNA và đối soát dữ kiện.",
    )
    p.add_argument("--version", action="version", version=VERSION)
    sub = p.add_subparsers(dest="command", required=True)
    profile_choices = ["all", *[pr.value for pr in ALL_PROFILES]]
    _add_scan_and_profile_parsers(sub, profile_choices)

    ver_p = sub.add_parser("verify", help="Đối soát dữ kiện và từ phủ định/điều kiện trước - sau biên tập")
    ver_p.add_argument("before", type=Path)
    ver_p.add_argument("after", type=Path)
    ver_p.add_argument("--json", action="store_true")
    ver_p.add_argument("--output", type=Path)

    list_p = sub.add_parser("list-rules", help="Liệt kê danh mục 41 quy tắc hiện có")
    list_p.add_argument("--profile", choices=profile_choices, default="all")
    list_p.add_argument("--json", action="store_true")

    maint_p = sub.add_parser("check-maintenance", help="Kiểm tra hạn rà soát định kỳ danh sách từ mượn")
    maint_p.add_argument("--today", help="Ngày kiểm tra dạng YYYY-MM-DD (mặc định hôm nay)")
    maint_p.add_argument("--json", action="store_true")

    sub.add_parser("selftest", help="Chạy bài tự kiểm tra nhanh")
    return p


def _load_cli_input(file_arg: str, ignore_cols: set[int]) -> tuple[str, DocxMetadata | dict[str, Any]]:
    if file_arg != "-" and Path(file_arg).suffix.lower() == ".docx":
        return extract_docx_text_and_meta(Path(file_arg), ignore_cols=ignore_cols)
    return read_utf8(file_arg, ignore_cols=ignore_cols), {}


def _cmd_check_maintenance(args: argparse.Namespace) -> int:
    info = check_loanwords_maintenance(dt.date.fromisoformat(args.today) if args.today else None)
    if args.json:
        print(json.dumps(info, ensure_ascii=False, indent=2))
    else:
        status = (
            "QUÁ HẠN NĂM"
            if info["overdue_annual_review"]
            else ("ĐẾN KỲ RÀ SOÁT QUÝ" if info["due_for_quarterly_review"] else "ĐANG TRONG HẠN")
        )
        print(f"TRẠNG THÁI DANH SÁCH TỪ MƯỢN: {status}")
        print(f"  Lần rà soát gần nhất: {info['last_reviewed']} ({info['days_since_review']} ngày trước)")
        print(
            f"  Số từ hiện có: {info['universal_loanwords_count']} từ phổ thông mọi ngữ cảnh + "
            f"{info['workplace_tech_loanwords_count']} từ công sở/kỹ thuật"
        )
        print(f"  Ghi chú: {info['note']}")
    return 1 if info["overdue_annual_review"] else 0


def _cmd_list_rules(args: argparse.Namespace) -> int:
    scanner = ViScanner()
    rules = [r for r in scanner.rules.values() if args.profile == "all" or Profile(args.profile) in r.profiles]
    if args.json:
        rule_items: list[RuleSummaryItem] = [
            {
                "rule_id": r.rule_id,
                "category": r.category,
                "severity": r.severity.value,
                "weight": r.weight,
                "profiles": [p.value for p in ALL_PROFILES if p in r.profiles],
                "exempt_profiles": list(r.exempt_profiles),
                "description_vi": r.description_vi,
            }
            for r in rules
        ]
        print(json.dumps(rule_items, ensure_ascii=False, indent=2))
    else:
        for r in rules:
            print(f"{r.rule_id} [{r.severity.value}] ({r.category}): {r.description_vi}")
    return 0


def _cmd_profile(args: argparse.Namespace) -> int:
    ig_cols = parse_ignore_cols(args.ignore_table_cols)
    file_str = str(args.file)
    text, docx_meta = _load_cli_input(file_str, ig_cols)
    prof_data = profile_text(text, label=file_str, docx_meta=docx_meta, ignore_cols=ig_cols)
    payload = json.dumps(prof_data, ensure_ascii=False, indent=2)
    if args.output:
        args.output.write_text(payload, encoding="utf-8")
    if args.json:
        print(payload)
    else:
        print_profile_report(prof_data)
    return 0


def _scan_exit_code(report: ScanReport, fail_on: str) -> int:
    if fail_on == "never":
        return 0
    if fail_on == "error":
        return 1 if report.error_count > 0 else 0
    if fail_on == "warning":
        return 1 if (report.error_count + report.warning_count) > 0 else 0
    return 1 if report.findings_count > 0 else 0


def _scan_single_target(scanner: ViScanner, file_str: str, profile: str, ig_cols: set[int]) -> ScanReport:
    text, docx_meta_scan = _load_cli_input(file_str, ig_cols)
    report = scanner.scan_text(text, profile=profile)
    mismatch_note = docx_meta_scan.get("template_title_mismatch")
    if isinstance(mismatch_note, str) and mismatch_note:
        core_title = str(docx_meta_scan.get("core_title") or "docProps/core.xml")
        scanner.prepend_docx_title_mismatch(report, text, core_title, mismatch_note)
    return report


def _cmd_scan(args: argparse.Namespace) -> int:
    ig_cols = parse_ignore_cols(args.ignore_table_cols)
    extra = ViScanner.load_custom_rules(args.custom_rules) if args.custom_rules else None
    scanner = ViScanner(extra_rules=extra)
    targets: list[str] = [str(f) for f in (args.files or ["-"])]
    reports = [_scan_single_target(scanner, target, str(args.profile), ig_cols) for target in targets]
    payload = (
        reports[0].to_json(indent=2)
        if len(reports) == 1
        else json.dumps(
            [{"file": target, **rep.to_dict()} for target, rep in zip(targets, reports, strict=True)],
            ensure_ascii=False,
            indent=2,
        )
    )
    if args.output:
        args.output.write_text(payload, encoding="utf-8")
    if args.json:
        print(payload)
    else:
        for idx, (target, rep) in enumerate(zip(targets, reports, strict=True)):
            if idx > 0:
                print("\n" + "=" * 72)
            print_scan_report(rep, target)
    return max(_scan_exit_code(rep, str(args.fail_on)) for rep in reports)


def _cmd_verify(args: argparse.Namespace) -> int:
    result = verify_text(read_utf8(args.before), read_utf8(args.after))
    payload = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.write_text(payload, encoding="utf-8")
    if args.json:
        print(payload)
    else:
        print("KẾT QUẢ ĐỐI SOÁT:", "ĐẠT (PASS)" if result["passed"] else "LỆCH DỮ KIỆN (FAIL)")
        for err in result["errors"]:
            print(f"  - {err}")
        print(result["note"])
    return 0 if result["passed"] else 1


def main(argv: Sequence[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

    args = build_parser().parse_args(argv)
    handlers: dict[str, Callable[[argparse.Namespace], int]] = {
        "check-maintenance": _cmd_check_maintenance,
        "list-rules": _cmd_list_rules,
        "profile": _cmd_profile,
        "scan": _cmd_scan,
        "verify": _cmd_verify,
    }
    try:
        if args.command == "selftest":
            return selftest()
        handler = handlers.get(str(args.command))
        return handler(args) if handler is not None else 2
    except (OSError, UnicodeError, ValueError, KeyError, json.JSONDecodeError, zipfile.BadZipFile) as exc:
        print(f"LỖI: {exc}", file=sys.stderr)
        return 2
