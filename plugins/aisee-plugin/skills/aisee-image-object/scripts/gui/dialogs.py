"""Action dialogs for the aisee:image-object GUI."""

from __future__ import annotations

from gui.components import (
    create_button,
    create_dialog_buttons,
    create_dialog_preview,
    create_dialog_shell,
    create_form_layout,
    create_section_header,
)


class ExportSettingsDialog:
    def __init__(self, parent=None, *, title: str = "导出当前素材", defaults: dict | None = None):
        from PySide6.QtWidgets import QCheckBox, QComboBox, QDialog, QSpinBox

        defaults = defaults or {}
        self.dialog = QDialog(parent)
        root, panel = create_dialog_shell(
            self.dialog,
            eyebrow="EXPORT",
            title=title,
            subtitle="设置透明背景、圆角、留白和交付格式。",
        )
        form = create_form_layout()
        self.transparent = QCheckBox("透明")
        self.transparent.setChecked(bool(defaults.get("transparent", True)))
        self.corner_radius = QSpinBox()
        self.corner_radius.setRange(0, 512)
        self.corner_radius.setValue(int(defaults.get("corner_radius", 0)))
        self.padding = QSpinBox()
        self.padding.setRange(0, 1024)
        self.padding.setValue(int(defaults.get("padding", 0)))
        self.crop_mode = QComboBox()
        self.crop_mode.addItems(["bbox", "original-canvas", "square"])
        self.crop_mode.setCurrentText(str(defaults.get("crop_mode", "bbox")))
        self.format = QComboBox()
        self.format.addItems(["png", "webp", "jpg"])
        self.format.setCurrentText(str(defaults.get("format", "png")))
        form.addRow("透明背景", self.transparent)
        form.addRow("圆角", self.corner_radius)
        form.addRow("留白", self.padding)
        form.addRow("裁切模式", self.crop_mode)
        form.addRow("格式", self.format)
        panel.addLayout(form)
        root.addWidget(create_dialog_buttons(self.dialog))

    def exec(self) -> bool:
        return bool(self.dialog.exec())

    def values(self) -> dict:
        return {
            "transparent": self.transparent.isChecked(),
            "corner_radius": self.corner_radius.value(),
            "padding": self.padding.value(),
            "crop_mode": self.crop_mode.currentText(),
            "format": self.format.currentText(),
        }


class RepairSettingsDialog:
    def __init__(self, parent=None):
        from PySide6.QtWidgets import QCheckBox, QComboBox, QDialog

        self.dialog = QDialog(parent)
        root, panel = create_dialog_shell(
            self.dialog,
            eyebrow="INPAINT",
            title="抹除设置",
            subtitle="对刚才标记的内容进行背景修补，默认使用 LaMa；低质量 fallback 需要手动开启。",
        )
        form = create_form_layout()
        self.method = QComboBox()
        self.method.addItems(["lama"])
        self.device = QComboBox()
        self.device.addItems(["cpu", "mps", "cuda"])
        self.fallback = QCheckBox("允许低质量 OpenCV fallback")
        self.fallback.setChecked(False)
        form.addRow("方法", self.method)
        form.addRow("设备", self.device)
        form.addRow("Fallback", self.fallback)
        panel.addLayout(form)
        root.addWidget(create_dialog_buttons(self.dialog))

    def exec(self) -> bool:
        return bool(self.dialog.exec())

    def values(self) -> dict:
        return {
            "method": self.method.currentText(),
            "device": self.device.currentText(),
            "fallback": self.fallback.isChecked(),
        }


class RegionMaskSettingsDialog:
    def __init__(self, parent=None, *, profiles: list[dict], default_label: str = ""):
        from PySide6.QtWidgets import QCheckBox, QComboBox, QDialog, QLineEdit, QSpinBox, QTextEdit

        self.dialog = QDialog(parent)
        root, panel = create_dialog_shell(
            self.dialog,
            eyebrow="ASSET",
            title="处理框选区域",
            subtitle="框选区域本身可直接作为素材使用；勾选透明背景时会调用模型去背景生成透明素材。",
        )
        form = create_form_layout()
        self.name = QLineEdit(default_label)
        self.intent = QLineEdit()
        self.notes = QTextEdit()
        self.notes.setMaximumHeight(90)
        self.selected = QCheckBox("选用")
        self.transparent = QCheckBox("需要透明背景")
        self.transparent.setChecked(False)
        self.corner_radius = QSpinBox()
        self.corner_radius.setRange(0, 512)
        self.corner_radius.setValue(0)
        self.padding = QSpinBox()
        self.padding.setRange(0, 1024)
        self.padding.setValue(0)
        self.crop_mode = QComboBox()
        self.crop_mode.addItems(["bbox", "original-canvas", "square"])
        self.format = QComboBox()
        self.format.addItems(["png", "webp", "jpg"])
        self.profile = QComboBox()
        for profile in profiles:
            self.profile.addItem(str(profile["name"]))
        self.profile.setCurrentText("quality")
        self.profile.setEnabled(False)
        self.transparent.toggled.connect(self.profile.setEnabled)
        form.addRow("素材名称", self.name)
        form.addRow("用途", self.intent)
        form.addRow("备注", self.notes)
        form.addRow("标识", self.selected)
        form.addRow("透明背景", self.transparent)
        form.addRow("圆角", self.corner_radius)
        form.addRow("留白", self.padding)
        form.addRow("裁切模式", self.crop_mode)
        form.addRow("格式", self.format)
        form.addRow("模型 profile", self.profile)
        panel.addLayout(form)
        root.addWidget(create_dialog_buttons(self.dialog))

    def exec(self) -> bool:
        return bool(self.dialog.exec())

    def values(self) -> dict:
        return {
            "profile": self.profile.currentText(),
            "name": self.name.text().strip(),
            "intent": self.intent.text().strip(),
            "notes": self.notes.toPlainText().strip(),
            "selected": self.selected.isChecked(),
            "generate_transparent": self.transparent.isChecked(),
            "auto_extract": True,
            "export_defaults": {
                "transparent": self.transparent.isChecked(),
                "corner_radius": self.corner_radius.value(),
                "padding": self.padding.value(),
                "crop_mode": self.crop_mode.currentText(),
                "format": self.format.currentText(),
            },
        }


class CutoutSettingsDialog:
    def __init__(self, parent=None, *, default_label: str = ""):
        from PySide6.QtWidgets import QCheckBox, QDialog, QLineEdit, QTextEdit

        self.dialog = QDialog(parent)
        root, panel = create_dialog_shell(
            self.dialog,
            eyebrow="CUTOUT",
            title="生成透明素材",
            subtitle="从当前中间结果生成可导出的透明素材。",
        )
        form = create_form_layout()
        self.name = QLineEdit(default_label)
        self.intent = QLineEdit()
        self.notes = QTextEdit()
        self.notes.setMaximumHeight(90)
        self.crop = QCheckBox("按对象范围裁切")
        self.crop.setChecked(True)
        form.addRow("素材名称", self.name)
        form.addRow("用途", self.intent)
        form.addRow("备注", self.notes)
        form.addRow("裁切", self.crop)
        panel.addLayout(form)
        root.addWidget(create_dialog_buttons(self.dialog))

    def exec(self) -> bool:
        return bool(self.dialog.exec())

    def values(self) -> dict:
        return {
            "name": self.name.text().strip(),
            "intent": self.intent.text().strip(),
            "notes": self.notes.toPlainText().strip(),
            "crop": self.crop.isChecked(),
        }


class MetadataDialog:
    def __init__(self, parent=None, *, title: str = "素材信息", label: str = "", notes: str = ""):
        from PySide6.QtWidgets import QDialog, QLineEdit, QTextEdit

        self.dialog = QDialog(parent)
        root, panel = create_dialog_shell(
            self.dialog,
            eyebrow="METADATA",
            title=title,
            subtitle="给素材补充可读名称和处理备注。",
        )
        form = create_form_layout()
        self.label = QLineEdit(label)
        self.notes = QTextEdit(notes)
        self.notes.setMaximumHeight(120)
        form.addRow("名称", self.label)
        form.addRow("备注", self.notes)
        panel.addLayout(form)
        root.addWidget(create_dialog_buttons(self.dialog))

    def exec(self) -> bool:
        return bool(self.dialog.exec())

    def values(self) -> dict:
        return {"label": self.label.text().strip(), "notes": self.notes.toPlainText().strip()}


class AssetSettingsDialog:
    def __init__(
        self,
        parent=None,
        *,
        title: str = "编辑素材",
        label: str = "",
        notes: str = "",
        selected: bool = False,
        defaults: dict | None = None,
    ):
        from PySide6.QtWidgets import QCheckBox, QComboBox, QDialog, QLineEdit, QSpinBox, QTextEdit

        defaults = defaults or {}
        self.dialog = QDialog(parent)
        root, panel = create_dialog_shell(
            self.dialog,
            eyebrow="ASSET",
            title=title,
            subtitle="编辑素材名称、选用标识和后续处理属性。",
        )
        form = create_form_layout()
        self.label = QLineEdit(label)
        self.selected = QCheckBox("选用")
        self.selected.setChecked(bool(selected))
        self.transparent = QCheckBox("透明")
        self.transparent.setChecked(bool(defaults.get("transparent", True)))
        self.corner_radius = QSpinBox()
        self.corner_radius.setRange(0, 512)
        self.corner_radius.setValue(int(defaults.get("corner_radius", 0)))
        self.padding = QSpinBox()
        self.padding.setRange(0, 1024)
        self.padding.setValue(int(defaults.get("padding", 0)))
        self.crop_mode = QComboBox()
        self.crop_mode.addItems(["bbox", "original-canvas", "square"])
        self.crop_mode.setCurrentText(str(defaults.get("crop_mode", "bbox")))
        self.format = QComboBox()
        self.format.addItems(["png", "webp", "jpg"])
        self.format.setCurrentText(str(defaults.get("format", "png")))
        self.notes = QTextEdit(notes)
        self.notes.setMaximumHeight(100)
        form.addRow("名称", self.label)
        form.addRow("标识", self.selected)
        form.addRow("透明背景", self.transparent)
        form.addRow("圆角", self.corner_radius)
        form.addRow("留白", self.padding)
        form.addRow("裁切模式", self.crop_mode)
        form.addRow("格式", self.format)
        form.addRow("备注", self.notes)
        panel.addLayout(form)
        root.addWidget(create_dialog_buttons(self.dialog))

    def exec(self) -> bool:
        return bool(self.dialog.exec())

    def values(self) -> dict:
        return {
            "label": self.label.text().strip(),
            "notes": self.notes.toPlainText().strip(),
            "selected": self.selected.isChecked(),
            "export_defaults": {
                "transparent": self.transparent.isChecked(),
                "corner_radius": self.corner_radius.value(),
                "padding": self.padding.value(),
                "crop_mode": self.crop_mode.currentText(),
                "format": self.format.currentText(),
            },
        }


class RegionSettingsDialog:
    def __init__(
        self,
        parent=None,
        *,
        preview_path: str,
        bbox: list[int],
        label: str = "",
        defaults: dict | None = None,
    ):
        from PySide6.QtCore import Qt
        from PySide6.QtGui import QPixmap
        from PySide6.QtWidgets import (
            QCheckBox,
            QComboBox,
            QDialog,
            QLabel,
            QLineEdit,
            QSpinBox,
            QTextEdit,
        )

        defaults = defaults or {}
        self.dialog = QDialog(parent)
        root, panel = create_dialog_shell(
            self.dialog,
            eyebrow="REGION",
            title="确认框选区域",
            subtitle="先核对框选范围，再设置该区域后续导出的默认属性。",
            width=720,
            height=760,
        )

        preview = create_dialog_preview()
        pixmap = QPixmap(preview_path)
        if pixmap.isNull():
            preview.setText("无法加载区域预览")
        else:
            preview.setPixmap(pixmap.scaled(560, 340, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        panel.addWidget(preview)

        form = create_form_layout()
        self.label = QLineEdit(label)
        self.notes = QTextEdit()
        self.notes.setMaximumHeight(80)
        self.transparent = QCheckBox("透明")
        self.transparent.setChecked(bool(defaults.get("transparent", True)))
        self.corner_radius = QSpinBox()
        self.corner_radius.setRange(0, 512)
        self.corner_radius.setValue(int(defaults.get("corner_radius", 0)))
        self.padding = QSpinBox()
        self.padding.setRange(0, 1024)
        self.padding.setValue(int(defaults.get("padding", 0)))
        self.crop_mode = QComboBox()
        self.crop_mode.addItems(["bbox", "original-canvas", "square"])
        self.crop_mode.setCurrentText(str(defaults.get("crop_mode", "bbox")))
        self.format = QComboBox()
        self.format.addItems(["png", "webp", "jpg"])
        self.format.setCurrentText(str(defaults.get("format", "png")))

        form.addRow("区域范围", QLabel(f"{bbox[0]}, {bbox[1]}, {bbox[2]}, {bbox[3]}"))
        form.addRow("名称", self.label)
        form.addRow("备注", self.notes)
        form.addRow("透明背景", self.transparent)
        form.addRow("圆角", self.corner_radius)
        form.addRow("留白", self.padding)
        form.addRow("裁切模式", self.crop_mode)
        form.addRow("格式", self.format)
        panel.addLayout(form)
        root.addWidget(create_dialog_buttons(self.dialog))

    def exec(self) -> bool:
        return bool(self.dialog.exec())

    def values(self) -> dict:
        return {
            "label": self.label.text().strip(),
            "notes": self.notes.toPlainText().strip(),
            "export_defaults": {
                "transparent": self.transparent.isChecked(),
                "corner_radius": self.corner_radius.value(),
                "padding": self.padding.value(),
                "crop_mode": self.crop_mode.currentText(),
                "format": self.format.currentText(),
            },
        }


class DetailViewer:
    def __init__(
        self,
        parent=None,
        *,
        assets: list,
        current_index: int,
        workspace,
        resolve_path,
    ):
        from PySide6.QtCore import QSize, Qt
        from PySide6.QtGui import QIcon, QPixmap
        from PySide6.QtWidgets import (
            QAbstractItemView,
            QComboBox,
            QDialog,
            QGraphicsPixmapItem,
            QGraphicsScene,
            QGraphicsView,
            QHBoxLayout,
            QLabel,
            QListView,
            QListWidget,
            QListWidgetItem,
        )

        self.dialog = QDialog(parent)
        self.assets = list(assets)
        self.current_index = max(0, min(current_index, len(self.assets) - 1)) if self.assets else 0
        self.workspace = workspace
        self.resolve_path = resolve_path
        root, panel = create_dialog_shell(
            self.dialog,
            eyebrow="DETAIL",
            title="放大查看",
            subtitle="居中查看当前素材，底部可切换其他素材。",
            width=1180,
            height=820,
        )

        toolbar = QHBoxLayout()
        toolbar.setContentsMargins(0, 0, 0, 0)
        toolbar.setSpacing(8)
        self.title_label = QLabel("未选择素材")
        self.title_label.setProperty("role", "muted")
        self.previous_button = create_button("上一张")
        self.next_button = create_button("下一张")
        self.zoom = QComboBox()
        self.zoom.addItems(["适应", "100%", "200%", "400%", "自定义"])
        self.zoom.setCurrentText("适应")
        close_button = create_button("关闭")
        toolbar.addWidget(self.title_label, 1)
        toolbar.addWidget(QLabel("缩放"))
        toolbar.addWidget(self.zoom)
        toolbar.addWidget(self.previous_button)
        toolbar.addWidget(self.next_button)
        toolbar.addWidget(close_button)
        panel.addLayout(toolbar)

        class DetailGraphicsView(QGraphicsView):
            def __init__(view_self, owner):
                super().__init__()
                view_self.owner = owner

            def resizeEvent(view_self, event):
                super().resizeEvent(event)
                if view_self.owner.zoom.currentText() == "适应":
                    view_self.owner._apply_zoom()

            def wheelEvent(view_self, event):
                if event.modifiers() & Qt.ControlModifier:
                    delta = event.angleDelta().y()
                    if delta:
                        view_self.owner._zoom_by(1.15 if delta > 0 else 1 / 1.15)
                    event.accept()
                    return
                super().wheelEvent(event)

        self.view = DetailGraphicsView(self)
        self.view.setObjectName("DetailCanvas")
        self.view.setDragMode(QGraphicsView.ScrollHandDrag)
        self.view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.view.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.view.setAlignment(Qt.AlignCenter)
        self.scene = QGraphicsScene(self.view)
        self.view.setScene(self.scene)
        self.pixmap_item = QGraphicsPixmapItem()
        self.scene.addItem(self.pixmap_item)
        panel.addWidget(self.view, 1)

        filmstrip_header = create_section_header("THUMBNAILS", "其他素材")
        panel.addLayout(filmstrip_header)
        self.filmstrip = QListWidget()
        self.filmstrip.setObjectName("DetailFilmstrip")
        self.filmstrip.setViewMode(QListWidget.IconMode)
        self.filmstrip.setFlow(QListView.LeftToRight)
        self.filmstrip.setWrapping(False)
        self.filmstrip.setIconSize(QSize(96, 72))
        self.filmstrip.setGridSize(QSize(132, 104))
        self.filmstrip.setResizeMode(QListWidget.Adjust)
        self.filmstrip.setMovement(QListWidget.Static)
        self.filmstrip.setSpacing(8)
        self.filmstrip.setSelectionMode(QAbstractItemView.SingleSelection)
        self.filmstrip.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.filmstrip.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.filmstrip.setMaximumHeight(134)
        panel.addWidget(self.filmstrip)

        close_button.clicked.connect(self.dialog.accept)
        self.previous_button.clicked.connect(self.previous)
        self.next_button.clicked.connect(self.next)
        self.zoom.currentTextChanged.connect(self._apply_zoom)
        self.filmstrip.currentRowChanged.connect(self.set_current_index)
        self._populate_filmstrip()
        self.set_current_index(self.current_index)

    def _populate_filmstrip(self) -> None:
        from pathlib import Path

        from PySide6.QtGui import QIcon
        from PySide6.QtWidgets import QListWidgetItem

        self.filmstrip.clear()
        for record in self.assets:
            name = record.item.get("name") or record.item.get("label") or record.item_id
            item = QListWidgetItem(f"{record.label}\n{name}")
            thumbnail = record.item.get("thumbnail")
            if thumbnail:
                item.setIcon(QIcon(str(Path(self.workspace) / thumbnail)))
            item.setToolTip(record.display)
            self.filmstrip.addItem(item)

    def set_current_index(self, index: int) -> None:
        from PySide6.QtGui import QPixmap

        if not self.assets:
            return
        if index < 0 or index >= len(self.assets):
            return
        self.current_index = index
        if self.filmstrip.currentRow() != index:
            self.filmstrip.setCurrentRow(index)
        record = self.assets[index]
        image_path = self.resolve_path(record)
        pixmap = QPixmap(str(image_path))
        self.pixmap_item.setPixmap(pixmap)
        self.scene.setSceneRect(self.pixmap_item.boundingRect())
        self._apply_zoom()
        self.title_label.setText(f"{record.label} {record.item_id}")
        self.previous_button.setEnabled(len(self.assets) > 1)
        self.next_button.setEnabled(len(self.assets) > 1)

    def _fit_current(self) -> None:
        if hasattr(self, "pixmap_item") and not self.pixmap_item.pixmap().isNull():
            self.view.fitInView(self.pixmap_item, __import__("PySide6.QtCore", fromlist=["Qt"]).Qt.KeepAspectRatio)

    def _apply_zoom(self) -> None:
        if self.zoom.currentText() == "适应":
            self._fit_current()
            return
        if self.zoom.currentText() == "自定义":
            return
        value = self.zoom.currentText().rstrip("%")
        if not value.isdigit():
            return
        self.view.resetTransform()
        self.view.scale(int(value) / 100.0, int(value) / 100.0)

    def _zoom_by(self, factor: float) -> None:
        if not hasattr(self, "pixmap_item") or self.pixmap_item.pixmap().isNull():
            return
        current_scale = max(0.01, self.view.transform().m11())
        next_scale = min(8.0, max(0.1, current_scale * factor))
        self.view.scale(next_scale / current_scale, next_scale / current_scale)
        self.zoom.blockSignals(True)
        self.zoom.setCurrentText("自定义")
        self.zoom.blockSignals(False)

    def previous(self) -> None:
        if self.assets:
            self.set_current_index((self.current_index - 1) % len(self.assets))

    def next(self) -> None:
        if self.assets:
            self.set_current_index((self.current_index + 1) % len(self.assets))

    def exec(self) -> bool:
        return bool(self.dialog.exec())


class RegionPickerDialog:
    def __init__(
        self,
        parent=None,
        *,
        image_path: str,
        regions: list[dict],
        line_width: int,
        aspect_ratio: float | None = None,
        on_region_created,
    ):
        from PySide6.QtGui import QPixmap
        from PySide6.QtWidgets import QComboBox, QDialog, QHBoxLayout, QLabel
        from gui.source_canvas import SourceCanvas

        self.dialog = QDialog(parent)
        self.on_region_created = on_region_created
        self._regions = list(regions)
        root, panel = create_dialog_shell(
            self.dialog,
            eyebrow="PICK REGIONS",
            title="放大框选区域",
            subtitle="在大画布上连续拖拽创建区域，关闭后素材列表会保留所有新区域。",
            width=1180,
            height=820,
        )

        toolbar = QHBoxLayout()
        toolbar.setContentsMargins(0, 0, 0, 0)
        toolbar.setSpacing(8)
        hint = QLabel("已开启框选模式")
        hint.setProperty("role", "muted")
        self.size_label = QLabel("0*0")
        self.size_label.setProperty("role", "muted")
        self.count_label = QLabel("待确认 0 个")
        self.count_label.setProperty("role", "muted")
        self.zoom = QComboBox()
        self.zoom.addItems(["适应", "100%", "200%", "400%"])
        add_button = create_button("添加选框", variant="primary")
        confirm_button = create_button("确认切出", variant="primary")
        clear_button = create_button("清空选框")
        close_button = create_button("完成", variant="primary")
        add_button.clicked.connect(self.add_current)
        confirm_button.clicked.connect(self.confirm_pending)
        clear_button.clicked.connect(self.clear_pending)
        close_button.clicked.connect(self.dialog.accept)
        toolbar.addWidget(hint)
        toolbar.addWidget(self.size_label)
        toolbar.addWidget(self.count_label)
        toolbar.addStretch(1)
        toolbar.addWidget(QLabel("缩放"))
        toolbar.addWidget(self.zoom)
        toolbar.addWidget(clear_button)
        toolbar.addWidget(add_button)
        toolbar.addWidget(confirm_button)
        toolbar.addWidget(close_button)
        panel.addLayout(toolbar)

        self.canvas = SourceCanvas()
        self.canvas.set_region_line_width(line_width)
        self.canvas.set_aspect_ratio(aspect_ratio)
        self.canvas.set_pixmap(QPixmap(image_path))
        self.canvas.set_regions(regions)
        self.canvas.set_region_mode(True)
        self.canvas.on_region_preview = self._handle_region_preview
        self.canvas.on_pending_changed = self._handle_pending_changed
        self.zoom.currentTextChanged.connect(self.canvas.set_zoom)
        panel.addWidget(self.canvas.widget(), 1)

    def _handle_region_preview(self, bbox: list[int] | None) -> None:
        if not bbox:
            self.size_label.setText("0*0")
            return
        self.size_label.setText(f"{max(0, bbox[2] - bbox[0])}*{max(0, bbox[3] - bbox[1])}px")

    def _handle_pending_changed(self, count: int) -> None:
        self.count_label.setText(f"待确认 {count} 个")

    def clear_pending(self) -> None:
        self.canvas.clear_pending_regions()

    def add_current(self) -> None:
        self.canvas.add_current_region()

    def confirm_pending(self) -> None:
        bboxes = self.canvas.pending_bboxes()
        for bbox in bboxes:
            self.on_region_created(bbox)
        self.canvas.clear_pending_regions()

    def set_regions(self, regions: list[dict]) -> None:
        self._regions = list(regions)
        self.canvas.set_regions(self._regions)

    def exec(self) -> bool:
        return bool(self.dialog.exec())


class ErasePickerDialog:
    def __init__(
        self,
        parent=None,
        *,
        image_path: str,
        title: str,
        line_width: int,
    ):
        from PySide6.QtGui import QPixmap
        from PySide6.QtWidgets import QComboBox, QDialog, QHBoxLayout, QLabel
        from gui.source_canvas import SourceCanvas

        self.dialog = QDialog(parent)
        root, panel = create_dialog_shell(
            self.dialog,
            eyebrow="ERASE",
            title="标记抹除内容",
            subtitle="在当前素材图上框出真正需要抹除的内容。只会处理这里新标记的区域，不会直接抹除整个素材。",
            width=1180,
            height=820,
        )

        toolbar = QHBoxLayout()
        toolbar.setContentsMargins(0, 0, 0, 0)
        toolbar.setSpacing(8)
        hint = QLabel(title)
        hint.setProperty("role", "muted")
        self.size_label = QLabel("0*0")
        self.size_label.setProperty("role", "muted")
        self.count_label = QLabel("待抹除 0 个")
        self.count_label.setProperty("role", "muted")
        self.zoom = QComboBox()
        self.zoom.addItems(["适应", "100%", "200%", "400%"])
        add_button = create_button("添加标记", variant="primary")
        clear_button = create_button("清空")
        close_button = create_button("开始抹除", variant="primary")
        add_button.clicked.connect(self.add_current)
        clear_button.clicked.connect(self.clear)
        close_button.clicked.connect(self.dialog.accept)
        toolbar.addWidget(hint)
        toolbar.addWidget(self.size_label)
        toolbar.addWidget(self.count_label)
        toolbar.addStretch(1)
        toolbar.addWidget(QLabel("缩放"))
        toolbar.addWidget(self.zoom)
        toolbar.addWidget(add_button)
        toolbar.addWidget(clear_button)
        toolbar.addWidget(close_button)
        panel.addLayout(toolbar)

        self.canvas = SourceCanvas()
        self.canvas.set_region_line_width(line_width)
        self.canvas.set_pixmap(QPixmap(image_path))
        self.canvas.set_region_mode(True)
        self.canvas.on_region_preview = self._handle_region_preview
        self.canvas.on_pending_changed = self._handle_pending_changed
        self.zoom.currentTextChanged.connect(self.canvas.set_zoom)
        panel.addWidget(self.canvas.widget(), 1)

    def _handle_region_preview(self, bbox: list[int] | None) -> None:
        if not bbox:
            self.size_label.setText("0*0")
            return
        self.size_label.setText(f"{max(0, bbox[2] - bbox[0])}*{max(0, bbox[3] - bbox[1])}px")

    def _handle_pending_changed(self, count: int) -> None:
        self.count_label.setText(f"待抹除 {count} 个")

    def clear(self) -> None:
        self.canvas.clear_pending_regions()

    def add_current(self) -> None:
        self.canvas.add_current_region()

    def bboxes(self) -> list[list[int]]:
        return self.canvas.pending_bboxes()

    def exec(self) -> bool:
        return bool(self.dialog.exec())
