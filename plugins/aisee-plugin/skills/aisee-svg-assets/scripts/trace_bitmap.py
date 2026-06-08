#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Any


PRESETS = {
    "icon-color": {
        "colormode": "color",
        "mode": "spline",
        "filter_speckle": 4,
        "color_precision": 6,
        "layer_difference": 16,
        "corner_threshold": 60,
        "length_threshold": 4.0,
        "max_iterations": 10,
        "splice_threshold": 45,
    },
    "icon-bw": {
        "colormode": "binary",
        "mode": "spline",
        "filter_speckle": 4,
        "color_precision": 6,
        "layer_difference": 16,
        "corner_threshold": 60,
        "length_threshold": 4.0,
        "max_iterations": 10,
        "splice_threshold": 45,
    },
    "logo": {
        "colormode": "color",
        "mode": "spline",
        "filter_speckle": 2,
        "color_precision": 8,
        "layer_difference": 12,
        "corner_threshold": 70,
        "length_threshold": 3.5,
        "max_iterations": 12,
        "splice_threshold": 45,
    },
    "illustration": {
        "colormode": "color",
        "mode": "spline",
        "filter_speckle": 8,
        "color_precision": 6,
        "layer_difference": 20,
        "corner_threshold": 50,
        "length_threshold": 5.0,
        "max_iterations": 10,
        "splice_threshold": 45,
    },
}


def _die(message: str) -> None:
    print(f"Error: {message}", file=sys.stderr)
    raise SystemExit(1)


def _try_python_vtracer(inp: Path, out: Path, options: dict[str, Any]) -> bool:
    try:
        import vtracer  # type: ignore
    except Exception:
        return False

    kwargs = dict(options)
    kwargs["input_path"] = str(inp)
    kwargs["output_path"] = str(out)

    # vtracer Python builds have used slightly different argument names. Try
    # the common path first, then fall through to CLI if the binding rejects it.
    try:
        vtracer.convert_image_to_svg_py(**kwargs)
        return True
    except TypeError:
        try:
            vtracer.convert_image_to_svg_py(str(inp), str(out), **options)
            return True
        except Exception as exc:
            print(f"Warning: python vtracer failed: {exc}", file=sys.stderr)
            return False
    except Exception as exc:
        print(f"Warning: python vtracer failed: {exc}", file=sys.stderr)
        return False


def _to_cli_flag(key: str) -> str:
    return "--" + key.replace("_", "-")


def _run_cli_vtracer(inp: Path, out: Path, options: dict[str, Any]) -> bool:
    exe = shutil.which("vtracer")
    if not exe:
        return False

    cmd = [exe, "--input", str(inp), "--output", str(out)]
    for key, value in options.items():
        cmd.extend([_to_cli_flag(key), str(value)])
    subprocess.run(cmd, check=True)
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Trace bitmap images to SVG using VTracer.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--preset", choices=sorted(PRESETS), default="icon-color")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--report")
    args = parser.parse_args()

    inp = Path(args.input)
    out = Path(args.out)
    if not inp.exists():
        _die(f"input not found: {inp}")
    if inp.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp"}:
        _die("input must be PNG, JPG, JPEG, or WebP")
    if out.exists() and not args.force:
        _die(f"output exists: {out} (use --force)")
    if out.suffix.lower() != ".svg":
        _die("output path must end with .svg")

    out.parent.mkdir(parents=True, exist_ok=True)
    options = PRESETS[args.preset]

    method = None
    if _try_python_vtracer(inp, out, options):
        method = "python-vtracer"
    elif _run_cli_vtracer(inp, out, options):
        method = "vtracer-cli"
    else:
        _die(
            "VTracer is not installed. Prefer `pip install vtracer`; "
            "fallback for CLI-only use: `cargo install vtracer`."
        )

    print(f"Wrote {out}")
    report = {
        "input": str(inp),
        "output": str(out),
        "preset": args.preset,
        "method": method,
        "options": options,
        "ok": True,
    }

    if args.report:
        report_path = Path(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(f"Wrote {report_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
