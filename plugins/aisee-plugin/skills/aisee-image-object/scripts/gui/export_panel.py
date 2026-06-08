"""Chinese export option panel."""

from __future__ import annotations


class ExportPanel:
    def __init__(self):
        from PySide6.QtWidgets import QCheckBox, QComboBox, QSpinBox
        from gui.components import create_button, create_form_layout, create_panel, create_section_header

        self.group, layout = create_panel(object_name="ExportPanel")
        layout.addLayout(create_section_header("EXPORT", "透明背景、圆角与格式"))
        form = create_form_layout()
        self.transparent = QCheckBox("透明")
        self.transparent.setChecked(True)
        self.corner_radius = QSpinBox()
        self.corner_radius.setRange(0, 512)
        self.padding = QSpinBox()
        self.padding.setRange(0, 1024)
        self.crop_mode = QComboBox()
        self.crop_mode.addItems(["bbox", "original-canvas", "square"])
        self.format = QComboBox()
        self.format.addItems(["png", "webp", "jpg"])
        self.export_button = create_button("导出变体", variant="primary")
        form.addRow("透明背景", self.transparent)
        form.addRow("圆角", self.corner_radius)
        form.addRow("留白", self.padding)
        form.addRow("裁切模式", self.crop_mode)
        form.addRow("格式", self.format)
        layout.addLayout(form)
        layout.addWidget(self.export_button)

    def widget(self):
        return self.group
