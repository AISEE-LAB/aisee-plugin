#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

from validate_svg import validate_svg


def optimize(text: str) -> str:
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    text = re.sub(r"<metadata\b.*?</metadata>", "", text, flags=re.I | re.S)
    text = re.sub(r"<\?xml[^>]*>\s*", "", text, flags=re.I)
    text = re.sub(r">\s+<", "><", text)
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Basic SVG cleanup without external dependencies.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--allow-unsafe", action="store_true")
    parser.add_argument("--report")
    args = parser.parse_args()

    in_path = Path(args.input)
    out_path = Path(args.out)
    if not in_path.exists():
        print(f"Error: input not found: {in_path}", file=sys.stderr)
        return 1
    if out_path.exists() and not args.force:
        print(f"Error: output exists: {out_path} (use --force)", file=sys.stderr)
        return 1

    input_report = validate_svg(in_path)
    if not input_report["ok"] and not args.allow_unsafe:
        print(json.dumps(input_report, ensure_ascii=False, indent=2, sort_keys=True), file=sys.stderr)
        print("Error: input SVG failed validation; use --allow-unsafe only for isolated analysis.", file=sys.stderr)
        return 2

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(optimize(in_path.read_text(encoding="utf-8")), encoding="utf-8")
    print(f"Wrote {out_path}")

    output_report = validate_svg(out_path)
    report = {
        "input": str(in_path),
        "output": str(out_path),
        "inputValidation": input_report,
        "outputValidation": output_report,
        "ok": output_report["ok"],
    }

    if args.report:
        report_path = Path(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(f"Wrote {report_path}")

    if not output_report["ok"]:
        print(json.dumps(output_report, ensure_ascii=False, indent=2, sort_keys=True), file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
