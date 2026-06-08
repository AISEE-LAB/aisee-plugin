"""Chinese tool panel widgets."""

from __future__ import annotations


class ToolPanel:
    def __init__(self):
        from PySide6.QtWidgets import QCheckBox, QComboBox
        from gui.components import create_button, create_form_layout, create_panel, create_section_header

        self.group, layout = create_panel(object_name="ToolPanel")
        layout.addLayout(create_section_header("TOOLS", "模型选择与基础处理"))
        form = create_form_layout()
        self.model_profile = QComboBox()
        self.model_profile.addItems(["quality", "fast", "product", "portrait", "anime", "compat"])
        form.addRow("模型 profile", self.model_profile)
        layout.addLayout(form)
        self.remove_bg_button = create_button("去背景", variant="primary")
        self.segment_button = create_button("生成透明素材")
        self.extract_button = create_button("生成透明素材")
        self.repair_background_button = create_button("抹除区域")
        self.allow_opencv_fallback = QCheckBox("允许低质量 fallback")
        self.allow_opencv_fallback.setChecked(False)
        layout.addWidget(self.remove_bg_button)
        layout.addWidget(self.segment_button)
        layout.addWidget(self.extract_button)
        layout.addWidget(self.repair_background_button)
        layout.addWidget(self.allow_opencv_fallback)

    def widget(self):
        return self.group
