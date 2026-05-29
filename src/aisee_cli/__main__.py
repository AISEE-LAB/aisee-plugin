"""Aisee CLI scaffold."""

from __future__ import annotations

import argparse
import json

from aisee_cli import __version__


def main() -> int:
    parser = argparse.ArgumentParser(prog="aisee")
    parser.add_argument("--version", action="store_true", help="print version")
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("doctor")
    subparsers.add_parser("bootstrap")
    subparsers.add_parser("sources")
    subparsers.add_parser("index")
    subparsers.add_parser("context")
    subparsers.add_parser("id")
    subparsers.add_parser("flow")
    args = parser.parse_args()

    if args.version:
        print(f"aisee {__version__}")
        return 0

    print(json.dumps({
        "status": "planned",
        "command": args.command,
        "message": "Aisee CLI scaffold is initialized; implementation pending."
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
