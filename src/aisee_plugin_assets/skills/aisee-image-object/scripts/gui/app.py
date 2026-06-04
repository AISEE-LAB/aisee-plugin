#!/usr/bin/env python3
"""PySide6 GUI entry for aisee:image-object."""

from __future__ import annotations

import argparse
import os
import signal
import sys


def run(workspace: str | None = None, image: str | None = None) -> int:
    os.environ.setdefault("KMP_WARNINGS", "0")

    try:
        from PySide6.QtCore import QTimer
        from PySide6.QtWidgets import QApplication
    except ImportError:
        print("PySide6 未安装，无法启动图形界面。请安装 PySide6，或使用 CLI 处理图片。", file=sys.stderr)
        return 2

    from gui.main_window import MainWindow
    from gui.app_icon import load_app_icon
    from gui.recent_files import last_recent_workspace
    from gui.theme import apply_theme
    from workspace import init_or_load_image_project

    app = QApplication.instance() or QApplication(sys.argv)
    interrupted = {"value": False}

    def request_quit(signum, frame):
        interrupted["value"] = True
        app.quit()

    signal.signal(signal.SIGINT, request_quit)
    signal.signal(signal.SIGTERM, request_quit)
    signal_timer = QTimer()
    signal_timer.timeout.connect(lambda: None)
    signal_timer.start(100)
    app._aisee_signal_timer = signal_timer

    icon = load_app_icon()
    if not icon.isNull():
        app.setWindowIcon(icon)
    apply_theme(app)
    if image:
        workspace_path, _, _ = init_or_load_image_project(image)
        workspace = str(workspace_path)
    if not image and not workspace:
        workspace = last_recent_workspace()
    window = MainWindow(workspace=workspace)
    window.show()
    exit_code = int(app.exec())
    return 130 if interrupted["value"] else exit_code


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="aisee:image-object 图形界面")
    parser.add_argument("--image", default=None, help="要打开的图片路径")
    parser.add_argument("--workspace", default=None, help="已有图片项目目录")
    args = parser.parse_args(argv)
    return run(args.workspace, image=args.image)


if __name__ == "__main__":
    raise SystemExit(main())
