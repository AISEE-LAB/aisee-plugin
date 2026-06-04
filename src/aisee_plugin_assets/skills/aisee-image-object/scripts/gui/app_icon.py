"""Shared GUI application icon loader."""

from __future__ import annotations

from pathlib import Path


APP_ICON_PATH = Path(__file__).resolve().parents[2] / "assets" / "app-icon.svg"


def load_app_icon():
    from PySide6.QtGui import QIcon

    if not APP_ICON_PATH.exists():
        return QIcon()
    return QIcon(str(APP_ICON_PATH))
