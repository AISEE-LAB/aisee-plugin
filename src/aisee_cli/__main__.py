"""Aisee CLI scaffold."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from aisee_cli import __version__
from aisee_cli.context_pack import build_context_pack, resolve_project_root
from aisee_cli.id_registry import activate_id, check_registry, reserve_ids


def main() -> int:
    parser = argparse.ArgumentParser(prog="aisee")
    parser.add_argument("--version", action="store_true", help="print version")
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("doctor")
    subparsers.add_parser("bootstrap")
    subparsers.add_parser("sources")
    subparsers.add_parser("index")
    change_parser = subparsers.add_parser("change")
    change_subparsers = change_parser.add_subparsers(dest="change_command")
    inspect_parser = change_subparsers.add_parser("inspect")
    inspect_parser.add_argument("change", help="OpenSpec change name")
    inspect_parser.add_argument("--json", action="store_true", help="output JSON")
    context_parser = subparsers.add_parser("context")
    context_subparsers = context_parser.add_subparsers(dest="context_command")
    pack_parser = context_subparsers.add_parser("pack")
    pack_parser.add_argument("--change", required=True, help="OpenSpec change name")
    pack_parser.add_argument("--for", dest="target", required=True, help="context target")
    pack_parser.add_argument("--json", action="store_true", help="output JSON")
    id_parser = subparsers.add_parser("id")
    id_subparsers = id_parser.add_subparsers(dest="id_command")
    id_check_parser = id_subparsers.add_parser("check")
    id_check_parser.add_argument("--json", action="store_true", help="output JSON")
    id_reserve_parser = id_subparsers.add_parser("reserve")
    id_reserve_parser.add_argument("--scope", required=True, help="ID scope")
    id_reserve_parser.add_argument("--type", required=True, help="ID type")
    id_reserve_parser.add_argument("--count", type=int, default=1, help="number of IDs to reserve")
    id_reserve_parser.add_argument("--json", action="store_true", help="output JSON")
    id_activate_parser = id_subparsers.add_parser("activate")
    id_activate_parser.add_argument("id", help="full ID, for example auth:FR-001")
    id_activate_parser.add_argument("--owner", required=True, help="owner document path")
    id_activate_parser.add_argument("--title", required=True, help="ID title")
    id_activate_parser.add_argument("--json", action="store_true", help="output JSON")
    subparsers.add_parser("flow")
    gaps_parser = subparsers.add_parser("gaps")
    gaps_parser.add_argument("--change", required=True, help="OpenSpec change name")
    gaps_parser.add_argument("--json", action="store_true", help="output JSON")
    args = parser.parse_args()

    if args.version:
        print(f"aisee {__version__}")
        return 0

    if args.command == "context" and args.context_command == "pack":
        try:
            root = resolve_project_root(Path.cwd())
            pack = build_context_pack(root, args.change, args.target)
        except ValueError as error:
            print(json.dumps({"status": "error", "message": str(error)}, ensure_ascii=False, indent=2), file=sys.stderr)
            return 2
        print(json.dumps(pack, ensure_ascii=False, indent=2))
        return 0

    if args.command == "gaps":
        root = resolve_project_root(Path.cwd())
        pack = build_context_pack(root, args.change, "aisee-verify")
        result = {
            "schema_version": pack["schema_version"],
            "change": pack["change"],
            "result": summarize_gaps(pack["gaps"]),
            "gaps": pack["gaps"],
            "guardrails": pack["guardrails"],
            "meta": {
                "command": f"aisee gaps --change {args.change} --json",
                "source_context_target": "aisee-verify",
            },
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    if args.command == "change" and args.change_command == "inspect":
        root = resolve_project_root(Path.cwd())
        pack = build_context_pack(root, args.change, "aisee-verify")
        parsed = pack["facts"]["parsed"]
        derived = pack["facts"]["derived"]
        result = {
            "schema_version": pack["schema_version"],
            "change": pack["change"],
            "schema": parsed["schema"],
            "artifacts": parsed["schema"]["artifacts"],
            "task_state": derived["task_state"],
            "paths": {
                "code": derived["code_paths"],
                "tests": derived["test_paths"],
            },
            "gaps": summarize_gaps(pack["gaps"]),
            "meta": {
                "command": f"aisee change inspect {args.change} --json",
                "source_context_target": "aisee-verify",
            },
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    if args.command == "id":
        root = resolve_project_root(Path.cwd())
        try:
            if args.id_command == "check":
                result = check_registry(root)
            elif args.id_command == "reserve":
                result = reserve_ids(root, args.scope, args.type, args.count)
            elif args.id_command == "activate":
                result = activate_id(root, args.id, args.owner, args.title)
            else:
                result = {
                    "status": "planned",
                    "command": args.command,
                    "message": "Use one of: check, reserve, activate.",
                }
        except ValueError as error:
            print(json.dumps({"status": "error", "message": str(error)}, ensure_ascii=False, indent=2), file=sys.stderr)
            return 2
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    print(json.dumps({
        "status": "planned",
        "command": args.command,
        "message": "Aisee CLI scaffold is initialized; implementation pending."
    }, ensure_ascii=False, indent=2))
    return 0


def summarize_gaps(gaps: list[dict[str, object]]) -> dict[str, int | str]:
    blocker = sum(1 for gap in gaps if gap.get("severity") == "blocker")
    risk = sum(1 for gap in gaps if gap.get("severity") == "risk")
    info = sum(1 for gap in gaps if gap.get("severity") == "info")
    status = "blocked" if blocker else ("risk" if risk else "clear")
    return {
        "status": status,
        "blocker": blocker,
        "risk": risk,
        "info": info,
        "total": len(gaps),
    }


if __name__ == "__main__":
    raise SystemExit(main())
