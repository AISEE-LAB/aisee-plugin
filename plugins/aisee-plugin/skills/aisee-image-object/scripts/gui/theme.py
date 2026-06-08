"""Apple-inspired restrained theme for the image-object desktop GUI."""

from __future__ import annotations

from pathlib import Path


def apply_theme(window) -> None:
    from PySide6.QtGui import QFont

    chevron_path = (Path(__file__).resolve().parent / "assets" / "chevron-down.svg").as_posix()
    window.setFont(QFont("Helvetica Neue"))
    window.setStyleSheet(
        """
        QWidget {
            background: #f5f5f7;
            color: #1d1d1f;
            font-family: "Helvetica Neue", "Arial";
            font-size: 14px;
        }

        QLabel {
            background: transparent;
        }

        QMainWindow {
            background: #f5f5f7;
        }

        QDialog {
            background: #f5f5f7;
        }

        QLabel[role="eyebrow"] {
            font-family: "Menlo", "Monaco";
            font-size: 11px;
            font-weight: 600;
            letter-spacing: 1px;
            text-transform: uppercase;
        }

        QLabel[role="title"] {
            font-size: 22px;
            font-weight: 600;
            letter-spacing: -0.2px;
        }

        QLabel[role="muted"] {
            font-size: 13px;
            font-weight: 400;
            color: #6e6e73;
        }

        QFrame#TopNav {
            background: #fbfbfd;
            border-bottom: 1px solid #e0e0e0;
        }

        QFrame#SourceBlock {
            background: #f5f5f7;
            border: none;
            border-radius: 0;
        }

        QFrame#AssetBlock {
            background: #f5f5f7;
            border: none;
            border-radius: 0;
        }

        QFrame#SurfacePanel,
        QFrame#ControlShelf,
        QFrame#ActionStrip,
        QFrame#TaskStrip,
        QFrame#AssetStrip,
        QFrame#ToolPanel,
        QFrame#ExportPanel,
        QFrame#DialogPanel {
            background: #fbfbfd;
            border: 1px solid #e0e0e0;
            border-radius: 18px;
        }

        QLabel#DialogPreview {
            background: #f5f5f7;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 8px;
        }

        QGraphicsView,
        QListWidget,
        QScrollArea {
            background: #fbfbfd;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
        }

        QListWidget#AssetGrid {
            background: transparent;
            border: none;
            border-radius: 0;
        }

        QListWidget::item {
            border-radius: 6px;
            padding: 6px;
            margin: 2px;
        }

        QListWidget::item:hover {
            background: #f5f5f7;
        }

        QListWidget::item:selected {
            background: #0066cc;
            color: #fbfbfd;
        }

        QScrollBar:horizontal {
            background: #f0f0f0;
            border: none;
            height: 8px;
            margin: 0;
            border-radius: 4px;
        }

        QScrollBar::handle:horizontal {
            background: #c7c7cc;
            min-width: 32px;
            border-radius: 4px;
        }

        QScrollBar::add-line:horizontal,
        QScrollBar::sub-line:horizontal {
            width: 0;
            border: none;
        }

        QScrollBar:vertical {
            background: #f0f0f0;
            border: none;
            width: 8px;
            margin: 0;
            border-radius: 4px;
        }

        QScrollBar::handle:vertical {
            background: #c7c7cc;
            min-height: 32px;
            border-radius: 4px;
        }

        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {
            height: 0;
            border: none;
        }

        QPushButton {
            background: #fbfbfd;
            color: #1d1d1f;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 5px 14px 6px 14px;
            min-height: 22px;
            font-weight: 480;
        }

        QPushButton[variant="primary"] {
            background: #0066cc;
            color: #fbfbfd;
            border: 1px solid #0066cc;
            border-radius: 16px;
            padding-left: 18px;
            padding-right: 18px;
        }

        QPushButton[variant="secondary"] {
            background: #fbfbfd;
            color: #1d1d1f;
            border: 1px solid #e0e0e0;
        }

        QPushButton:hover:enabled {
            border: 1px solid #0066cc;
            color: #0066cc;
        }

        QPushButton[variant="primary"]:hover:enabled {
            background: #0071e3;
            color: #fbfbfd;
            border: 1px solid #0071e3;
        }

        QPushButton:pressed:enabled {
            padding-top: 6px;
            padding-bottom: 5px;
        }

        QPushButton:disabled {
            background: #f5f5f7;
            color: #7a7a7a;
            border: 1px solid #e5e5e5;
        }

        QComboBox,
        QSpinBox,
        QDoubleSpinBox,
        QLineEdit,
        QTextEdit {
            background: #fbfbfd;
            color: #1d1d1f;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            min-height: 28px;
            padding: 2px 10px;
        }

        QComboBox {
            padding: 2px 28px 2px 10px;
        }

        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 26px;
            border: none;
            background: transparent;
        }

        QComboBox::down-arrow {
            image: url("__CHEVRON_PATH__");
            width: 12px;
            height: 12px;
        }

        QComboBox QAbstractItemView {
            background: #fbfbfd;
            color: #1d1d1f;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 4px;
            selection-background-color: #0066cc;
            selection-color: #fbfbfd;
        }

        QComboBox:focus,
        QSpinBox:focus,
        QDoubleSpinBox:focus,
        QLineEdit:focus,
        QTextEdit:focus {
            border: 1px solid #0071e3;
        }

        QSpinBox::up-button,
        QSpinBox::down-button,
        QDoubleSpinBox::up-button,
        QDoubleSpinBox::down-button {
            width: 18px;
            border: none;
            background: transparent;
        }

        QTextEdit {
            padding: 8px 12px;
        }

        QCheckBox {
            background: transparent;
            spacing: 8px;
        }

        QProgressDialog {
            background: #fbfbfd;
            color: #1d1d1f;
            border: 1px solid #e0e0e0;
            border-radius: 18px;
        }

        QProgressDialog QLabel {
            color: #1d1d1f;
            padding: 8px 4px;
        }

        QProgressBar {
            background: #f5f5f7;
            border: 1px solid #e0e0e0;
            border-radius: 7px;
            height: 14px;
            text-align: center;
            color: #6e6e73;
        }

        QProgressBar::chunk {
            background: #0066cc;
            border-radius: 6px;
        }

        QStatusBar {
            background: #f5f5f7;
            border-top: 1px solid #e0e0e0;
        }

        QSplitter::handle {
            background: #f5f5f7;
        }

        QSplitter::handle:horizontal {
            width: 10px;
        }
        """.replace("__CHEVRON_PATH__", chevron_path)
    )
