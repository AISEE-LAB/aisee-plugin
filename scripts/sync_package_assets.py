"""Deprecated package asset sync entrypoint.

Aisee plugin content is distributed from the GitHub marketplace plugin.
The PyPI package is CLI-only and no longer mirrors skills, references,
schema packs, team knowledge templates, or plugin metadata into
``src/aisee_plugin_assets``.
"""

from __future__ import annotations


def main() -> int:
    print("Package asset sync is deprecated; plugin content is distributed from GitHub marketplace.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
