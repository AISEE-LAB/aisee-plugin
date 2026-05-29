#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET


RISK_PATTERNS = {
    "script_tag": re.compile(r"<\s*script\b", re.I),
    "event_handler": re.compile(r"\son[a-z]+\s*=", re.I),
    "foreign_object": re.compile(r"<\s*foreignObject\b", re.I),
    "external_reference": re.compile(r"""(?:href|xlink:href)\s*=\s*['"]https?://""", re.I),
    "javascript_reference": re.compile(r"""(?:href|xlink:href)\s*=\s*['"]\s*javascript:""", re.I),
    "external_css_url": re.compile(r"""(?:url\(\s*['"]?https?://|@import\s+['"]https?://)""", re.I),
    "iframe_object_embed": re.compile(r"<\s*(iframe|object|embed)\b", re.I),
    "base64_embed": re.compile(r"data:[^;]+;base64,", re.I),
}


PRESENTATION_ATTRS = {
    "fill",
    "stroke",
    "stop-color",
    "flood-color",
    "lighting-color",
}


def _local_name(tag: str) -> str:
    return tag.split("}", 1)[-1].lower()


def validate_svg(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    report = {
        "file": str(path),
        "ok": True,
        "errors": [],
        "warnings": [],
        "hasViewBox": False,
        "hasWidth": False,
        "hasHeight": False,
        "hasTitle": False,
        "hasDesc": False,
        "ariaHidden": False,
        "usesCurrentColor": False,
        "colorCount": 0,
        "risks": [],
    }

    for name, pattern in RISK_PATTERNS.items():
        if pattern.search(text):
            report["risks"].append(name)

    if report["risks"]:
        report["ok"] = False
        report["errors"].append("Potentially unsafe SVG content found.")

    try:
        root = ET.fromstring(text)
    except ET.ParseError as exc:
        report["ok"] = False
        report["errors"].append(f"Invalid XML: {exc}")
        return report

    tag = _local_name(root.tag)
    if tag != "svg":
        report["ok"] = False
        report["errors"].append("Root element is not <svg>.")

    report["hasViewBox"] = "viewBox" in root.attrib
    report["hasWidth"] = "width" in root.attrib
    report["hasHeight"] = "height" in root.attrib
    report["ariaHidden"] = root.attrib.get("aria-hidden", "").lower() == "true"

    colors = set()
    for node in root.iter():
        name = _local_name(node.tag)
        if name == "title":
            report["hasTitle"] = True
        elif name == "desc":
            report["hasDesc"] = True

        for attr, value in node.attrib.items():
            attr_name = attr.split("}", 1)[-1]
            if attr_name in PRESENTATION_ATTRS:
                normalized = value.strip()
                if normalized == "currentColor":
                    report["usesCurrentColor"] = True
                if normalized and normalized not in {"none", "transparent", "currentColor"}:
                    colors.add(normalized)

    report["colorCount"] = len(colors)

    if not report["hasViewBox"]:
        report["warnings"].append("Missing viewBox.")
    if report["hasWidth"] and report["hasHeight"]:
        report["warnings"].append("Fixed width/height present; verify intended use.")
    if not report["ariaHidden"] and not (report["hasTitle"] and report["hasDesc"]):
        report["warnings"].append("Semantic SVG should include <title> and <desc>, or mark decorative SVG with aria-hidden=\"true\".")
    if report["colorCount"] > 8:
        report["warnings"].append("Many distinct presentation colors found; verify this is intended for a reusable SVG asset.")

    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate SVG structure and security.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--report")
    args = parser.parse_args()

    path = Path(args.input)
    if not path.exists():
        print(f"Error: input not found: {path}", file=sys.stderr)
        return 1

    report = validate_svg(path)
    rendered = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True)
    print(rendered)

    if args.report:
        report_path = Path(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(rendered + "\n", encoding="utf-8")
        print(f"Wrote {report_path}", file=sys.stderr)

    return 0 if report["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
