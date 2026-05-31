"""Aisee CLI scaffold."""

from __future__ import annotations

import argparse
from pathlib import Path

from aisee_cli import __version__
from aisee_cli.author_check import build_author_check
from aisee_cli.change import build_change_inspect
from aisee_cli.change_checks import build_archive_check, build_verify_check
from aisee_cli.context_pack import build_context_pack
from aisee_cli.id_registry import activate_id, check_registry, deprecate_id, next_id, reserve_ids
from aisee_cli.index import build_index
from aisee_cli.lookup import get_id, trace_id
from aisee_cli.output import error_response, exit_code_for, print_json
from aisee_cli.project import resolve_project_root
from aisee_cli.sources import add_source, check_sources, list_sources, remove_source


def main() -> int:
    parser = argparse.ArgumentParser(prog="aisee")
    parser.add_argument("--version", action="store_true", help="print version")
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("doctor")
    subparsers.add_parser("bootstrap")
    sources_parser = subparsers.add_parser("sources")
    sources_subparsers = sources_parser.add_subparsers(dest="sources_command")
    sources_list_parser = sources_subparsers.add_parser("list")
    sources_list_parser.add_argument("--json", action="store_true", help="output JSON")
    sources_check_parser = sources_subparsers.add_parser("check")
    sources_check_parser.add_argument("--json", action="store_true", help="output JSON")
    sources_check_parser.add_argument("--fail-on-blocker", action="store_true", help="return non-zero when blockers exist")
    sources_add_parser = sources_subparsers.add_parser("add")
    sources_add_parser.add_argument("--scope", required=True, help="source scope")
    sources_add_parser.add_argument("--type", required=True, help="source type")
    sources_add_parser.add_argument("--path", required=True, help="source path")
    sources_add_parser.add_argument("--template", help="source template")
    sources_add_parser.add_argument("--parser", help="source parser")
    sources_add_parser.add_argument("--json", action="store_true", help="output JSON")
    sources_remove_parser = sources_subparsers.add_parser("remove")
    sources_remove_parser.add_argument("--scope", required=True, help="source scope")
    sources_remove_parser.add_argument("--type", required=True, help="source type")
    sources_remove_parser.add_argument("--path", required=True, help="source path")
    sources_remove_parser.add_argument("--json", action="store_true", help="output JSON")
    index_parser = subparsers.add_parser("index")
    index_parser.add_argument("--json", action="store_true", help="output JSON")
    index_parser.add_argument("--fail-on-blocker", action="store_true", help="return non-zero when blockers exist")
    change_parser = subparsers.add_parser("change")
    change_subparsers = change_parser.add_subparsers(dest="change_command")
    inspect_parser = change_subparsers.add_parser("inspect")
    inspect_parser.add_argument("change", help="OpenSpec change name")
    inspect_parser.add_argument("--json", action="store_true", help="output JSON")
    author_check_parser = change_subparsers.add_parser("author-check")
    author_check_parser.add_argument("change", help="OpenSpec change name")
    author_check_parser.add_argument("--json", action="store_true", help="output JSON")
    verify_check_parser = change_subparsers.add_parser("verify-check")
    verify_check_parser.add_argument("change", help="OpenSpec change name")
    verify_check_parser.add_argument("--json", action="store_true", help="output JSON")
    verify_check_parser.add_argument("--fail-on-blocker", action="store_true", help="return non-zero when blockers exist")
    archive_check_parser = change_subparsers.add_parser("archive-check")
    archive_check_parser.add_argument("change", help="OpenSpec change name")
    archive_check_parser.add_argument("--json", action="store_true", help="output JSON")
    archive_check_parser.add_argument("--fail-on-blocker", action="store_true", help="return non-zero when blockers exist")
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
    id_check_parser.add_argument("--fail-on-blocker", action="store_true", help="return non-zero when blockers exist")
    id_next_parser = id_subparsers.add_parser("next")
    id_next_parser.add_argument("--scope", required=True, help="ID scope")
    id_next_parser.add_argument("--type", required=True, help="ID type")
    id_next_parser.add_argument("--json", action="store_true", help="output JSON")
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
    id_deprecate_parser = id_subparsers.add_parser("deprecate")
    id_deprecate_parser.add_argument("id", help="full ID, for example auth:FR-001")
    id_deprecate_parser.add_argument("--replaced-by", action="append", default=[], help="replacement full ID")
    id_deprecate_parser.add_argument("--reason", required=True, help="deprecation reason")
    id_deprecate_parser.add_argument("--json", action="store_true", help="output JSON")
    subparsers.add_parser("flow")
    gaps_parser = subparsers.add_parser("gaps")
    gaps_parser.add_argument("--change", required=True, help="OpenSpec change name")
    gaps_parser.add_argument("--json", action="store_true", help="output JSON")
    trace_parser = subparsers.add_parser("trace")
    trace_parser.add_argument("id", help="full ID to trace")
    trace_parser.add_argument("--json", action="store_true", help="output JSON")
    get_parser = subparsers.add_parser("get")
    get_parser.add_argument("id", help="full ID to get")
    get_parser.add_argument("--json", action="store_true", help="output JSON")
    args = parser.parse_args()

    if args.version:
        print(f"aisee {__version__}")
        return 0

    if args.command == "context" and args.context_command == "pack":
        try:
            root = resolve_project_root(Path.cwd())
            pack = build_context_pack(root, args.change, args.target)
        except ValueError as error:
            print_json(error_response(str(error)), stderr=True)
            return 2
        print_json(pack)
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
        print_json(result)
        return 0

    if args.command == "change" and args.change_command == "inspect":
        root = resolve_project_root(Path.cwd())
        result = build_change_inspect(root, args.change)
        print_json(result)
        return 0

    if args.command == "change" and args.change_command == "author-check":
        root = resolve_project_root(Path.cwd())
        result = build_author_check(root, args.change)
        print_json(result)
        return 0

    if args.command == "change" and args.change_command == "verify-check":
        root = resolve_project_root(Path.cwd())
        result = build_verify_check(root, args.change)
        print_json(result)
        return exit_code_for(result, fail_on_blocker=args.fail_on_blocker)

    if args.command == "change" and args.change_command == "archive-check":
        root = resolve_project_root(Path.cwd())
        result = build_archive_check(root, args.change)
        print_json(result)
        return exit_code_for(result, fail_on_blocker=args.fail_on_blocker)

    if args.command == "sources":
        root = resolve_project_root(Path.cwd())
        try:
            if args.sources_command in {None, "list"}:
                result = list_sources(root)
                print_json(result)
                return 0
            if args.sources_command == "check":
                result = check_sources(root)
                print_json(result)
                return exit_code_for(result, fail_on_blocker=args.fail_on_blocker)
            if args.sources_command == "add":
                result = add_source(root, args.scope, args.type, args.path, args.template, args.parser)
                print_json(result)
                return 0
            if args.sources_command == "remove":
                result = remove_source(root, args.scope, args.type, args.path)
                print_json(result)
                return 0
        except ValueError as error:
            print_json(error_response(str(error)), stderr=True)
            return 2

    if args.command == "index":
        root = resolve_project_root(Path.cwd())
        result = build_index(root, write_cache=True)
        print_json(result)
        return exit_code_for(result, fail_on_blocker=args.fail_on_blocker)

    if args.command == "id":
        root = resolve_project_root(Path.cwd())
        try:
            if args.id_command == "check":
                result = check_registry(root)
            elif args.id_command == "next":
                result = next_id(root, args.scope, args.type)
            elif args.id_command == "reserve":
                result = reserve_ids(root, args.scope, args.type, args.count)
            elif args.id_command == "activate":
                result = activate_id(root, args.id, args.owner, args.title)
            elif args.id_command == "deprecate":
                result = deprecate_id(root, args.id, args.replaced_by, args.reason)
            else:
                result = {
                    "status": "planned",
                    "command": args.command,
                    "message": "Use one of: check, next, reserve, activate, deprecate.",
                }
        except ValueError as error:
            print_json(error_response(str(error)), stderr=True)
            return 2
        print_json(result)
        fail_on_blocker = bool(getattr(args, "fail_on_blocker", False))
        return exit_code_for(result, fail_on_blocker=fail_on_blocker)

    if args.command == "trace":
        root = resolve_project_root(Path.cwd())
        try:
            result = trace_id(root, args.id)
        except ValueError as error:
            print_json(error_response(str(error)), stderr=True)
            return 2
        print_json(result)
        return 0

    if args.command == "get":
        root = resolve_project_root(Path.cwd())
        try:
            result = get_id(root, args.id)
        except ValueError as error:
            print_json(error_response(str(error)), stderr=True)
            return 2
        print_json(result)
        return 0

    print_json({
        "status": "planned",
        "command": args.command,
        "message": "Aisee CLI scaffold is initialized; implementation pending."
    })
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
