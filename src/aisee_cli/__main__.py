"""Aisee CLI scaffold."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from aisee_cli import __version__
from aisee_cli.context_pack import build_context_pack, resolve_project_root


def main() -> int:
    parser = argparse.ArgumentParser(prog="aisee")
    parser.add_argument("--version", action="store_true", help="print version")
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("doctor")
    subparsers.add_parser("bootstrap")
    subparsers.add_parser("sources")
    subparsers.add_parser("index")
    context_parser = subparsers.add_parser("context")
    context_subparsers = context_parser.add_subparsers(dest="context_command")
    pack_parser = context_subparsers.add_parser("pack")
    pack_parser.add_argument("--change", required=True, help="OpenSpec change name")
    pack_parser.add_argument("--for", dest="target", required=True, help="context target")
    pack_parser.add_argument("--json", action="store_true", help="output JSON")
    subparsers.add_parser("id")
    subparsers.add_parser("flow")
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

    print(json.dumps({
        "status": "planned",
        "command": args.command,
        "message": "Aisee CLI scaffold is initialized; implementation pending."
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
