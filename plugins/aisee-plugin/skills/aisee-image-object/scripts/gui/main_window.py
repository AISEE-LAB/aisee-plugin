"""Main window for aisee:image-object."""

from __future__ import annotations

from pathlib import Path
import sys

SCRIPT_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from export_runner import export_region_variant, export_variant
from extract_object import extract_object
from gui.components import set_button_variant
from inpaint_runner import inpaint_background_isolated
from mask_ops import create_bboxes_mask_file
from model_registry import list_profiles, resolve_profile
from rembg_runner import remove_background_region
from source_state import (
    add_operation,
    find_by_id,
    load_state,
    next_id,
    relpath,
    save_state,
    upsert_model_record,
    utc_now,
    workspace_path,
)
from workspace import init_or_load_image_project


class MainWindow:
    def __init__(self, *, workspace: str | None = None):
        from PySide6.QtWidgets import (
            QComboBox,
            QCheckBox,
            QFrame,
            QHBoxLayout,
            QLabel,
            QMainWindow,
            QMessageBox,
            QProgressBar,
            QSizePolicy,
            QSpinBox,
            QSplitter,
            QStatusBar,
            QVBoxLayout,
            QWidget,
        )

        from gui.asset_panel import AssetPanel
        from gui.asset_model import build_asset_records, find_first_object
        from gui.app_icon import load_app_icon
        from gui.components import FlowLayout, create_button, create_control_shelf
        from gui.recent_files import load_recent_records, save_recent_record
        from gui.preview_render import (
            render_canvas_composite_preview,
            render_canvas_preview,
            render_preview,
            render_region_preview,
            render_region_thumbnail,
            render_thumbnail,
        )
        from gui.source_canvas import SourceCanvas
        from gui.theme import apply_theme

        class _Window(QMainWindow):
            pass

        class _AutoHeightFrame(QFrame):
            def __init__(self, *, minimum_height: int, parent=None):
                super().__init__(parent)
                self._minimum_height = minimum_height

            def event(self, event):
                from PySide6.QtCore import QEvent

                handled = super().event(event)
                if event.type() in {QEvent.Resize, QEvent.Show, QEvent.LayoutRequest}:
                    self.sync_height_for_width()
                return handled

            def sync_height_for_width(self):
                layout = self.layout()
                if not layout or not layout.hasHeightForWidth():
                    return
                next_height = max(self._minimum_height, layout.heightForWidth(self.width()))
                if self.minimumHeight() == next_height:
                    return
                self.setMinimumHeight(next_height)
                self.updateGeometry()

        self.window = _Window()
        self.window.setWindowTitle("aisee 图片对象处理")
        self.window.setMinimumSize(1220, 720)
        icon = load_app_icon()
        if not icon.isNull():
            self.window.setWindowIcon(icon)
        self.workspace = Path(workspace) if workspace else None
        self.state = None
        self.asset_records = []
        self._progress_dialog = None
        self._active_batch = None
        self._is_processing = False
        self._build_asset_records = build_asset_records
        self._find_first_object = find_first_object
        self._render_preview = render_preview
        self._render_canvas_preview = render_canvas_preview
        self._render_canvas_composite_preview = render_canvas_composite_preview
        self._render_thumbnail = render_thumbnail
        self._render_region_thumbnail = render_region_thumbnail
        self._render_region_preview = render_region_preview
        self._load_recent_records = load_recent_records
        self._save_recent_record = save_recent_record

        root = QWidget()
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(12, 12, 12, 8)
        root_layout.setSpacing(10)

        top_nav = QFrame()
        top_nav.setObjectName("TopNav")
        header = QHBoxLayout(top_nav)
        header.setContentsMargins(14, 10, 14, 10)
        header.setSpacing(10)
        app_title = QLabel("aisee 图片对象处理")
        app_title.setProperty("role", "title")
        self.workspace_label = QLabel("未打开图片")
        self.workspace_label.setProperty("role", "muted")
        self.workspace_label.setWordWrap(True)
        self.workspace_label.setMinimumWidth(0)
        self.workspace_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        self.recent_combo = QComboBox()
        self.recent_combo.setMinimumWidth(180)
        self.recent_combo.setMaximumWidth(300)
        self.recent_combo.setToolTip("选择最近打开的图片项目；默认启动时会打开上一次图片")
        self.open_button = create_button("打开图片", variant="primary")
        self.reload_button = create_button("刷新")
        header.addWidget(app_title)
        header.addWidget(self.workspace_label, 1)
        header.addWidget(QLabel("最近"))
        header.addWidget(self.recent_combo)
        header.addWidget(self.open_button)
        header.addWidget(self.reload_button)
        root_layout.addWidget(top_nav)

        self.region_button = create_button("框选", variant="primary")
        self.add_region_button = create_button("添加", variant="primary")
        self.region_picker_button = create_button("放大")
        self.confirm_regions_button = create_button("切出", variant="primary")
        self.clear_regions_button = create_button("清空")
        self.region_button.setToolTip("开始或结束在左侧原图上框选区域")
        self.add_region_button.setToolTip("把当前可调整选框加入待切出列表")
        self.region_picker_button.setToolTip("打开放大框选窗口")
        self.confirm_regions_button.setToolTip("确认切出所有待确认选框")
        self.clear_regions_button.setToolTip("清空当前选框和待确认选框")
        self.mask_button = create_button("生成透明素材")
        self.cutout_button = create_button("生成透明素材")
        self.region_line_width = QSpinBox()
        self.region_line_width.setRange(1, 12)
        self.region_line_width.setValue(2)
        self.region_line_width.setToolTip("设置左侧框选区域和拖拽框的线条粗细")
        self.region_aspect = QComboBox()
        self.region_aspect.addItems(["自由", "1:1", "4:3", "3:4", "16:9", "9:16"])
        self.export_button = create_button("导出素材")
        self.repair_button = create_button("标记抹除")
        self.detail_button = create_button("放大查看")
        self.process_button = create_button("处理素材")
        self.mark_button = create_button("设为选用")
        self.delete_button = create_button("删除素材")

        splitter = QSplitter()
        self.source_canvas = SourceCanvas()
        self.source_canvas.on_pending_changed = self.update_pending_region_controls

        left_panel = QFrame()
        left_panel.setObjectName("SourceBlock")
        left_panel.setMinimumWidth(760)
        left_panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(14, 14, 14, 14)
        left_layout.setSpacing(10)
        source_shelf, source_controls = create_control_shelf()
        source_shelf.setFixedHeight(50)
        region_shelf, region_controls = create_control_shelf()
        region_shelf.setFixedHeight(54)
        source_title = QLabel("SOURCE")
        source_title.setProperty("role", "eyebrow")
        source_hint = QLabel("原图框选与同位置核对")
        source_hint.setProperty("role", "muted")
        self.source_view_mode = QComboBox()
        self.source_view_mode.addItems(["原图", "同位置预览"])
        self.source_view_mode.setMinimumWidth(128)
        self.source_zoom = QComboBox()
        self.source_zoom.addItems(["适应", "100%", "200%", "400%"])
        self.source_zoom.setCurrentText("适应")
        self.source_zoom.setMinimumWidth(104)
        self.preview_hide_boxes = QCheckBox("隐藏框线")
        self.region_button.setMinimumWidth(76)
        self.add_region_button.setMinimumWidth(76)
        self.region_picker_button.setMinimumWidth(76)
        self.confirm_regions_button.setMinimumWidth(76)
        self.clear_regions_button.setMinimumWidth(76)
        for button in (
            self.region_button,
            self.add_region_button,
            self.region_picker_button,
            self.confirm_regions_button,
            self.clear_regions_button,
        ):
            button.setFixedHeight(34)
        self.region_line_width.setFixedWidth(64)
        self.region_line_width.setFixedHeight(34)
        self.region_aspect.setFixedWidth(96)
        self.region_aspect.setFixedHeight(34)
        source_controls.addWidget(source_title)
        source_controls.addWidget(source_hint)
        source_controls.addWidget(QLabel("显示"))
        source_controls.addWidget(self.source_view_mode)
        source_controls.addWidget(QLabel("缩放"))
        source_controls.addWidget(self.source_zoom)
        source_controls.addWidget(self.preview_hide_boxes)
        source_controls.addStretch(1)
        line_label = QLabel("线宽")
        line_label.setProperty("role", "muted")
        aspect_label = QLabel("比例")
        aspect_label.setProperty("role", "muted")
        region_controls.addWidget(self.region_button)
        region_controls.addWidget(self.add_region_button)
        region_controls.addWidget(self.region_picker_button)
        region_controls.addWidget(self.confirm_regions_button)
        region_controls.addWidget(self.clear_regions_button)
        region_controls.addSpacing(8)
        region_controls.addWidget(line_label)
        region_controls.addWidget(self.region_line_width)
        region_controls.addWidget(aspect_label)
        region_controls.addWidget(self.region_aspect)
        region_controls.addStretch(1)
        left_layout.addWidget(source_shelf)
        left_layout.addWidget(region_shelf)
        left_layout.addWidget(self.source_canvas.widget(), 1)

        right_panel = QFrame()
        right_panel.setObjectName("AssetBlock")
        right_panel.setMinimumWidth(420)
        right_panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(14, 14, 14, 14)
        right_layout.setSpacing(10)
        self.selected_asset_label = QLabel("未选择素材")
        self.selected_asset_label.setProperty("role", "muted")

        self.preview_mode = QComboBox()
        self.preview_mode.addItems(["画布定位", "素材细节", "原图", "Mask", "Alpha", "Cutout"])
        self.preview_mode.setCurrentText("画布定位")
        self.preview_background = QComboBox()
        self.preview_background.addItems(["棋盘格", "白底", "黑底"])
        self.preview_background.setCurrentText("棋盘格")
        self.preview_zoom = QComboBox()
        self.preview_zoom.addItems(["适应", "100%", "200%", "400%"])
        self.preview_zoom.setCurrentText("适应")

        task_strip = QFrame()
        task_strip.setObjectName("TaskStrip")
        task_strip.setFixedHeight(36)
        task_layout = QHBoxLayout(task_strip)
        task_layout.setContentsMargins(12, 8, 12, 8)
        task_layout.setSpacing(10)
        task_title = QLabel("TASKS")
        task_title.setProperty("role", "eyebrow")
        self.task_status_label = QLabel("空闲")
        self.task_status_label.setProperty("role", "muted")
        self.task_progress = QProgressBar()
        self.task_progress.setRange(0, 1)
        self.task_progress.setValue(0)
        self.task_progress.setTextVisible(False)
        task_layout.addWidget(task_title)
        task_layout.addWidget(self.task_status_label)
        task_layout.addWidget(self.task_progress, 1)
        right_layout.addWidget(task_strip)

        self.asset_panel = AssetPanel(title="素材列表")

        action_strip = _AutoHeightFrame(minimum_height=92)
        action_strip.setObjectName("ActionStrip")
        action_strip.setMinimumHeight(92)
        self.action_strip = action_strip
        action_root = QVBoxLayout(action_strip)
        action_root.setContentsMargins(12, 10, 12, 10)
        action_root.setSpacing(8)
        action_summary = QHBoxLayout()
        action_summary.setContentsMargins(0, 0, 0, 0)
        action_summary.setSpacing(8)
        action_title = QLabel("ACTIONS")
        action_title.setProperty("role", "eyebrow")
        self.action_context_label = QLabel("选择素材后显示可用动作")
        self.action_context_label.setProperty("role", "muted")
        self.action_context_label.setWordWrap(False)
        self.selection_scope_label = QLabel("未选择")
        self.selection_scope_label.setProperty("role", "muted")
        action_summary.addWidget(action_title)
        action_summary.addWidget(self.action_context_label, 1)
        action_summary.addWidget(self.selected_asset_label)
        action_summary.addWidget(self.selection_scope_label)
        action_root.addLayout(action_summary)
        action_layout = FlowLayout(margins=(0, 0, 0, 0), spacing=8)
        for button, width in (
            (self.export_button, 76),
            (self.repair_button, 104),
            (self.detail_button, 96),
            (self.process_button, 112),
            (self.mark_button, 92),
            (self.delete_button, 92),
        ):
            button.setMinimumWidth(width)
        action_root.addLayout(action_layout)
        action_layout.addWidget(self.repair_button)
        action_layout.addWidget(self.process_button)
        action_layout.addWidget(self.mark_button)
        action_layout.addWidget(self.delete_button)
        action_layout.addWidget(self.detail_button)
        right_layout.addWidget(action_strip)
        right_layout.addWidget(self.asset_panel.widget(), 1)

        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setChildrenCollapsible(False)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)
        splitter.setSizes([980, 620])
        root_layout.addWidget(splitter, 1)

        self.window.setCentralWidget(root)
        self.window.setStatusBar(QStatusBar())
        apply_theme(self.window)
        self.open_button.clicked.connect(self.choose_workspace)
        self.reload_button.clicked.connect(self.load_workspace)
        self.recent_combo.activated.connect(self.open_recent_image)
        self.asset_panel.list_widget.currentItemChanged.connect(self.preview_selected_asset)
        self.asset_panel.category_filter.currentTextChanged.connect(self.update_asset_selection_label)
        self.asset_panel.list_widget.itemSelectionChanged.connect(self.preview_selected_asset)
        self.asset_panel.list_widget.itemDoubleClicked.connect(self.open_detail_viewer)
        self.region_button.clicked.connect(self.toggle_region_mode)
        self.add_region_button.clicked.connect(self.add_pending_region)
        self.region_picker_button.clicked.connect(self.open_region_picker)
        self.confirm_regions_button.clicked.connect(self.confirm_pending_regions)
        self.clear_regions_button.clicked.connect(self.clear_pending_regions)
        self.region_line_width.valueChanged.connect(self.source_canvas.set_region_line_width)
        self.region_aspect.currentTextChanged.connect(self.update_region_aspect)
        self.source_view_mode.currentTextChanged.connect(self.update_source_canvas_display)
        self.source_zoom.currentTextChanged.connect(self.source_canvas.set_zoom)
        self.process_button.clicked.connect(self.process_selected_assets)
        self.cutout_button.clicked.connect(self.extract_cutout_from_selected_mask)
        self.export_button.clicked.connect(self.export_selected_object)
        self.repair_button.clicked.connect(self.repair_selected_background)
        self.detail_button.clicked.connect(self.open_detail_viewer)
        self.mark_button.clicked.connect(self.toggle_selected_flag)
        self.delete_button.clicked.connect(self.delete_selected_assets)
        self.preview_mode.currentTextChanged.connect(self.preview_selected_asset)
        self.preview_background.currentTextChanged.connect(self.preview_selected_asset)
        self.preview_hide_boxes.toggled.connect(self.preview_selected_asset)
        self.refresh_recent_combo()
        self.update_region_aspect()
        self.update_pending_region_controls()
        self.update_action_states()
        from PySide6.QtCore import QTimer

        QTimer.singleShot(0, self.action_strip.sync_height_for_width)

        if self.workspace:
            try:
                self.load_workspace()
            except Exception as exc:
                QMessageBox.warning(self.window, "加载失败", str(exc))

    def __getattr__(self, name):
        return getattr(self.window, name)

    def load_workspace(self):
        if not self.workspace:
            return
        self.state = load_state(self.workspace)
        source = self.state.get("source", {})
        original = source.get("original_path") or source.get("path") or "source.png"
        image_name = Path(original).name
        self.workspace_label.setText(f"图片：{image_name}\n保存位置：{self._compact_path(self.workspace)}")
        self.workspace_label.setToolTip(f"图片：{image_name}\n保存位置：{self.workspace}")
        self._save_recent_record(workspace=self.workspace, image=original)
        self.refresh_recent_combo()

        self.asset_records = self._build_asset_records(self.state)
        self._ensure_thumbnails()
        save_state(self.workspace, self.state)
        self.asset_records = self._build_asset_records(self.state)
        self.asset_panel.set_assets(self.asset_records, self.workspace)
        if self.asset_panel.list_widget.count() and self.asset_panel.list_widget.currentRow() < 0:
            self.asset_panel.list_widget.setCurrentRow(0)
        self.update_source_canvas_display()
        self.preview_selected_asset()
        self.window.statusBar().showMessage("已加载图片")

    def refresh_recent_combo(self) -> None:
        current_workspace = str(self.workspace) if self.workspace else ""
        self.recent_combo.blockSignals(True)
        self.recent_combo.clear()
        self.recent_combo.addItem("选择最近打开", "")
        for item in self._load_recent_records():
            workspace = item.get("workspace", "")
            if not workspace:
                continue
            image_name = Path(item.get("image") or workspace).name
            self.recent_combo.addItem(image_name, workspace)
            if workspace == current_workspace:
                self.recent_combo.setCurrentIndex(self.recent_combo.count() - 1)
        self.recent_combo.blockSignals(False)

    def _compact_path(self, path: str | Path, *, max_chars: int = 92) -> str:
        text = str(path)
        if len(text) <= max_chars:
            return text
        head = max_chars // 2 - 2
        tail = max_chars - head - 3
        return f"{text[:head]}...{text[-tail:]}"

    def open_recent_image(self, index: int) -> None:
        from PySide6.QtWidgets import QMessageBox

        workspace = self.recent_combo.itemData(index)
        if not workspace:
            return
        if not Path(workspace).exists():
            QMessageBox.warning(self.window, "无法打开", f"最近打开记录不存在：{workspace}")
            self.refresh_recent_combo()
            return
        self.workspace = Path(workspace)
        self._load_workspace_preserving_geometry()

    def _ensure_thumbnails(self) -> None:
        source = self._source_image_path()
        for collection in ("regions", "masks", "objects", "backgrounds", "exports", "enhanced"):
            for item in self.state.get(collection, []):
                if item.get("thumbnail"):
                    continue
                item_id = item.get("id")
                if not item_id:
                    continue
                output = self.workspace / "preview-cache" / f"thumb_{item_id}.png"
                if collection == "regions":
                    bbox = item.get("bbox")
                    if not bbox:
                        continue
                    self._render_region_thumbnail(source, output, bbox=bbox)
                else:
                    path = item.get("path")
                    if not path:
                        continue
                    self._render_thumbnail(workspace_path(self.workspace, path), output)
                item["thumbnail"] = relpath(output, self.workspace)

    def choose_workspace(self):
        from PySide6.QtWidgets import QFileDialog, QMessageBox

        selected, _ = QFileDialog.getOpenFileName(
            self.window,
            "打开图片",
            "",
            "图片文件 (*.png *.jpg *.jpeg *.webp *.bmp *.tif *.tiff);;所有文件 (*)",
        )
        if not selected:
            return
        try:
            self.workspace, self.state, created = init_or_load_image_project(selected)
            self._load_workspace_preserving_geometry()
            self.window.statusBar().showMessage("已创建图片项目" if created else "已加载图片项目")
        except Exception as exc:
            QMessageBox.warning(self.window, "打开图片失败", str(exc))

    def _load_workspace_preserving_geometry(self) -> None:
        from PySide6.QtCore import QTimer

        geometry = self.window.geometry()
        maximized = self.window.isMaximized()
        fullscreen = self.window.isFullScreen()
        self.load_workspace()
        if maximized or fullscreen:
            return

        def restore() -> None:
            self.window.setGeometry(geometry)

        QTimer.singleShot(0, restore)

    def preview_selected_asset(self, *args):
        from PySide6.QtWidgets import QMessageBox

        if not self.workspace or not self.state:
            return
        try:
            self.update_source_canvas_display()
            self.update_asset_selection_label()
            selected = self.asset_panel.current_asset()
            status = f"当前素材：{selected.label} {selected.item_id}" if selected else "未选择素材"
            self.window.statusBar().showMessage(status)
        except Exception as exc:
            QMessageBox.warning(self.window, "素材选择失败", str(exc))

    def update_source_canvas_display(self, *args) -> None:
        from PySide6.QtGui import QPixmap
        from PySide6.QtWidgets import QMessageBox

        if not self.workspace or not self.state:
            return
        try:
            pixmap_path = self._source_image_path()
            selected = self.asset_panel.current_asset()
            if self.source_view_mode.currentText() == "同位置预览" and selected:
                canvas_path = self.workspace / "preview-cache" / "left-position-preview.png"
                pixmap_path = self._render_position_preview(canvas_path)
            self.source_canvas.set_pixmap(QPixmap(str(pixmap_path)))
            show_regions = not (
                self.source_view_mode.currentText() == "同位置预览" and self.preview_hide_boxes.isChecked()
            )
            self.source_canvas.set_regions(self.state.get("regions", []) if show_regions else [])
            self.source_canvas.set_zoom(self.source_zoom.currentText())
        except Exception as exc:
            QMessageBox.warning(self.window, "左侧预览失败", str(exc))

    def update_region_aspect(self, *args) -> None:
        mode = self.region_aspect.currentText()
        ratios = {
            "1:1": 1.0,
            "4:3": 4 / 3,
            "3:4": 3 / 4,
            "16:9": 16 / 9,
            "9:16": 9 / 16,
        }
        ratio = ratios.get(mode)
        self.source_canvas.set_aspect_ratio(ratio)

    def update_asset_selection_label(self) -> None:
        selected_records = self._selected_assets()
        selected = self.asset_panel.current_asset()
        if len(selected_records) > 1:
            counts = self._asset_counts(selected_records)
            summary = "、".join(f"{label} {count}" for label, count in counts)
            self.selected_asset_label.setText(f"已选 {len(selected_records)} 个")
            self.selection_scope_label.setText(summary)
        elif selected:
            self.selected_asset_label.setText(f"{selected.label} {selected.item_id}")
            self.selection_scope_label.setText("单个素材")
        else:
            self.selected_asset_label.setText("未选择素材")
            self.selection_scope_label.setText("未选择")
        self.update_action_states()

    def update_action_states(self) -> None:
        selected_records = self._selected_assets()
        compatible = self._compatible_assets(selected_records)
        export_available = False
        base_available = bool(selected_records)
        single_available = len(selected_records) == 1
        repair_available = single_available and selected_records[0].collection in {"regions", "objects", "backgrounds"}
        object_count = len([record for record in compatible["exportables"] if record.collection == "objects"])
        region_count = len([record for record in compatible["exportables"] if record.collection == "regions"])
        background_count = len([record for record in compatible["exportables"] if record.collection == "backgrounds"])

        if object_count and not region_count and not background_count:
            self.export_button.setText("导出透明素材")
        elif region_count and not object_count and not background_count:
            self.export_button.setText("导出区域图")
        elif background_count and not object_count and not region_count:
            self.export_button.setText("导出修补图")
        else:
            self.export_button.setText("导出素材")

        self.mask_button.setVisible(False)
        self.mask_button.setEnabled(False)
        self.cutout_button.setVisible(False)
        self.cutout_button.setEnabled(False)
        self.export_button.setEnabled(export_available)
        self.export_button.setVisible(export_available)
        self.repair_button.setEnabled(repair_available)
        self.repair_button.setVisible(repair_available)
        self.detail_button.setEnabled(single_available)
        self.detail_button.setVisible(single_available)
        self.process_button.setEnabled(base_available)
        self.process_button.setVisible(base_available)
        self.mark_button.setEnabled(base_available)
        self.mark_button.setVisible(base_available)
        self.delete_button.setEnabled(base_available)
        self.delete_button.setVisible(base_available)
        selected_count = len([record for record in selected_records if record.item.get("selected")])
        self.mark_button.setText("取消选用" if selected_count == len(selected_records) and selected_records else "设为选用")

        self.process_button.setToolTip("编辑素材属性；框选区域可直接使用，勾选透明背景时会生成透明素材")
        self.export_button.setToolTip("导出选中的区域图、透明素材或抹除结果")
        self.repair_button.setText("标记抹除")
        self.repair_button.setToolTip("打开当前素材图，在图上继续框出真正要从背景中抹除的内容")
        self.detail_button.setToolTip("放大查看当前单个素材")
        self.mark_button.setToolTip("批量切换选用/未选标识")
        self.delete_button.setToolTip("删除选中的框选区域、透明素材或处理结果")

        primary_button = None
        if base_available:
            primary_button = self.process_button
        if repair_available:
            context = "可处理素材属性，也可打开素材图标记需要抹除的内容"
        elif export_available:
            primary_button = self.export_button
            count = len(compatible["exportables"])
            context = f"选中 {count} 个素材：导出是交付文件，可设置格式、圆角和留白"
        elif base_available:
            context = "可处理素材属性、切换选用标识或删除素材"
        else:
            context = "先在素材列表选择框选区域、透明素材或处理结果"

        for button in (
            self.export_button,
            self.repair_button,
            self.detail_button,
            self.process_button,
            self.mark_button,
            self.delete_button,
        ):
            self._set_button_variant(button, "primary" if button is primary_button else "secondary")
        if self._is_processing:
            self.process_button.setEnabled(False)
            self.export_button.setEnabled(False)
            self.repair_button.setEnabled(False)
            self.mark_button.setEnabled(False)
            self.delete_button.setEnabled(False)
            self.region_button.setEnabled(False)
            self.add_region_button.setEnabled(False)
            self.region_picker_button.setEnabled(False)
            self.confirm_regions_button.setEnabled(False)
            self.clear_regions_button.setEnabled(False)
            self.open_button.setEnabled(False)
            self.reload_button.setEnabled(False)
            context = "后台任务处理中，当前可以查看素材；完成后会自动刷新列表"
        else:
            self.region_button.setEnabled(True)
            self.add_region_button.setEnabled(True)
            self.region_picker_button.setEnabled(True)
            self.update_pending_region_controls()
            self.open_button.setEnabled(True)
            self.reload_button.setEnabled(True)
        self.action_context_label.setText(context)
        self.action_strip.sync_height_for_width()

    def _selected_assets(self):
        return self.asset_panel.selected_assets()

    def _asset_counts(self, records) -> list[tuple[str, int]]:
        order = ["框选区域", "透明素材", "抹除结果", "导出结果", "优化"]
        counts = {}
        for record in records:
            counts[record.label] = counts.get(record.label, 0) + 1
        return [(label, counts[label]) for label in order if label in counts]

    def _compatible_assets(self, records) -> dict[str, list]:
        return {
            "regions": [record for record in records if record.collection == "regions"],
            "masks": [record for record in records if record.collection == "masks"],
            "exportables": [record for record in records if record.collection in {"regions", "objects", "backgrounds"}],
            "erasables": [record for record in records if record.collection in {"regions", "objects", "backgrounds"}],
        }

    def _reserve_ids(self, collection: str, prefix: str, count: int) -> list[str]:
        max_index = 0
        for item in self.state.get(collection, []):
            item_id = str(item.get("id", ""))
            if not item_id.startswith(f"{prefix}_"):
                continue
            try:
                max_index = max(max_index, int(item_id.rsplit("_", 1)[1]))
            except (IndexError, ValueError):
                continue
        return [f"{prefix}_{index:03d}" for index in range(max_index + 1, max_index + count + 1)]

    def _set_button_variant(self, button, variant: str) -> None:
        set_button_variant(button, variant)

    def _begin_progress(self, title: str, label: str, *, total: int = 0):
        from PySide6.QtCore import Qt
        from PySide6.QtWidgets import QApplication, QProgressDialog

        progress = QProgressDialog(label, "", 0, max(0, total), self.window)
        progress.setWindowTitle(title)
        progress.setCancelButton(None)
        progress.setWindowModality(Qt.ApplicationModal)
        progress.setMinimumDuration(0)
        progress.setValue(0)
        progress.show()
        QApplication.processEvents()
        self._progress_dialog = progress
        return progress

    def _update_progress(self, value: int, label: str | None = None) -> None:
        from PySide6.QtWidgets import QApplication

        progress = self._progress_dialog
        if not progress:
            return
        if label:
            progress.setLabelText(label)
        progress.setValue(value)
        QApplication.processEvents()

    def _end_progress(self) -> None:
        from PySide6.QtWidgets import QApplication

        progress = self._progress_dialog
        self._progress_dialog = None
        if progress:
            progress.close()
            QApplication.processEvents()

    def _start_background_batch(self, title: str, tasks: list[dict], on_finished) -> None:
        from PySide6.QtCore import QThread, Qt
        from PySide6.QtWidgets import QMessageBox
        from gui.task_runner import BatchUiBridge, BatchWorker

        if not tasks:
            return
        if self._is_processing:
            QMessageBox.information(self.window, "任务正在处理", "当前已有处理任务在运行，请等待完成后再开始新的处理。")
            return

        worker = BatchWorker(tasks)
        bridge = BatchUiBridge(self)
        thread = QThread(self.window)
        worker.moveToThread(thread)
        self._active_batch = {
            "title": title,
            "thread": thread,
            "worker": worker,
            "bridge": bridge,
            "on_finished": on_finished,
            "total": len(tasks),
        }
        self._is_processing = True
        self.task_progress.setRange(0, 0)
        self.task_status_label.setText(f"{title}：{len(tasks)} 个任务处理中")
        self.update_action_states()

        thread.started.connect(worker.run)
        worker.progress.connect(bridge.handle_progress, Qt.QueuedConnection)
        worker.finished.connect(bridge.handle_finished, Qt.QueuedConnection)
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(bridge.deleteLater)
        thread.finished.connect(self._clear_background_batch)
        thread.finished.connect(thread.deleteLater)
        thread.start()

    def _handle_task_progress(self, done: int, total: int, label: str) -> None:
        remaining = max(total - done, 0)
        if label.startswith("正在处理") and done < total:
            self.task_progress.setRange(0, 0)
        else:
            self.task_progress.setRange(0, max(total, 1))
            self.task_progress.setValue(done)
        self.task_status_label.setText(f"{label}，剩余 {remaining} 个")

    def _finish_background_batch(self, results: list[dict]) -> None:
        from PySide6.QtWidgets import QMessageBox

        batch = self._active_batch
        if not batch:
            return
        title = batch["title"]
        on_finished = batch["on_finished"]
        try:
            on_finished(results)
            self.task_status_label.setText(f"{title}：已完成")
        except Exception as exc:
            QMessageBox.warning(self.window, f"{title}失败", str(exc))
            self.task_status_label.setText(f"{title}：处理失败")

    def _clear_background_batch(self) -> None:
        self._active_batch = None
        self._is_processing = False
        self.task_progress.setRange(0, 1)
        self.task_progress.setValue(0)
        self.update_action_states()

    def select_previous_asset(self) -> None:
        self._select_asset_by_offset(-1)

    def select_next_asset(self) -> None:
        self._select_asset_by_offset(1)

    def _select_asset_by_offset(self, offset: int) -> None:
        count = self.asset_panel.list_widget.count()
        if count <= 0:
            return
        current = self.asset_panel.list_widget.currentRow()
        if current < 0:
            current = 0
        self.asset_panel.list_widget.setCurrentRow((current + offset) % count)

    def _current_right_preview_path(self) -> Path:
        selected = self.asset_panel.current_asset()
        if not selected:
            return self._source_image_path()
        mode = self.preview_mode.currentText()
        if mode == "画布定位":
            output = self.workspace / "preview-cache" / "right-position-preview.png"
            return self._render_position_preview(output)
        if mode == "素材细节":
            output = self.workspace / "preview-cache" / "right-detail-preview.png"
            return self._render_preview(
                self._preview_path_for_asset(selected),
                output,
                mode=self._effective_preview_mode(),
                background=self.preview_background.currentText(),
            )
        return self._resolve_preview_path()

    def _resolve_preview_path(self) -> Path:
        selected = self.asset_panel.current_asset()
        mode = self.preview_mode.currentText()
        if mode == "原图" or selected is None:
            return self._source_image_path()
        return self._preview_path_for_asset(selected, mode=mode)

    def _preview_path_for_asset(self, record, *, mode: str | None = None) -> Path:
        mode = mode or self.preview_mode.currentText()
        if record.collection == "regions":
            if record.item.get("thumbnail"):
                return workspace_path(self.workspace, record.item["thumbnail"])
            return self._source_image_path()

        if mode == "Mask" and record.collection == "objects":
            mask_id = record.item.get("mask_id")
            if mask_id:
                mask = find_by_id(self.state, "masks", mask_id)
                return workspace_path(self.workspace, mask["path"])

        return workspace_path(self.workspace, record.path)

    def _detail_path_for_asset(self, record) -> Path:
        if record.collection == "regions":
            bbox = record.item.get("bbox")
            if bbox:
                return self._crop_source_context(record.item_id, bbox, prefix="detail_context")
            return self._source_image_path()
        return self._preview_path_for_asset(record)

    def _effective_preview_mode(self) -> str:
        selected = self.asset_panel.current_asset()
        mode = self.preview_mode.currentText()
        if mode not in {"画布定位", "素材细节"}:
            return mode
        if selected and selected.collection == "masks":
            return "Mask"
        return "Cutout"

    def _render_position_preview(self, output: Path) -> Path:
        selected_assets = self._selected_assets()
        if len(selected_assets) <= 1:
            selected = selected_assets[0] if selected_assets else self.asset_panel.current_asset()
            if selected:
                return self._render_single_position_preview(output, selected)
        overlays = self._position_preview_overlays()
        if not overlays:
            return self._source_image_path()
        return self._render_canvas_composite_preview(
            self._source_image_path(),
            output,
            overlays=overlays,
            background=self.preview_background.currentText(),
            show_boxes=not self.preview_hide_boxes.isChecked(),
        )

    def _render_single_position_preview(self, output: Path, selected) -> Path:
        if selected.collection in {"regions", "objects", "masks"}:
            return self._render_canvas_preview(
                self._source_image_path(),
                output,
                asset_path=None if selected.collection == "regions" else self._preview_path_for_asset(selected),
                bbox=self._bbox_for_record(selected),
                mode="Mask" if selected.collection == "masks" else self._effective_preview_mode(),
                background=self.preview_background.currentText(),
                show_box=not self.preview_hide_boxes.isChecked(),
            )
        overlay = self._position_overlay_for_record(selected)
        if not overlay:
            return self._source_image_path()
        return self._render_canvas_composite_preview(
            self._source_image_path(),
            output,
            overlays=[overlay],
            background=self.preview_background.currentText(),
            show_boxes=not self.preview_hide_boxes.isChecked(),
        )

    def _position_preview_overlays(self) -> list[dict]:
        selected_assets = self._selected_assets()
        overlays = []
        for record in selected_assets:
            overlay = self._position_overlay_for_record(record)
            if overlay:
                overlays.append(overlay)
        overlays.sort(key=lambda item: 0 if item.get("kind") == "background" else 1)
        return overlays

    def _position_overlay_for_record(self, record) -> dict | None:
        bbox = self._bbox_for_record(record)
        if record.collection == "regions":
            return {"kind": "region", "bbox": bbox, "asset_path": None} if bbox else None
        if record.collection == "objects":
            return {"kind": "asset", "bbox": bbox, "asset_path": self._preview_path_for_asset(record)}
        if record.collection == "backgrounds":
            return {"kind": "background", "bbox": bbox, "asset_path": self._preview_path_for_asset(record)}
        if record.collection == "masks":
            return {"kind": "mask", "bbox": bbox, "asset_path": self._preview_path_for_asset(record, mode="Mask")}
        return None

    def _bbox_for_record(self, record) -> list[int] | None:
        bbox = record.item.get("bbox")
        if bbox:
            return bbox
        if record.collection == "objects":
            mask_id = record.item.get("mask_id")
            if mask_id:
                try:
                    mask = find_by_id(self.state, "masks", mask_id)
                    return mask.get("bbox")
                except KeyError:
                    return None
        if record.collection == "backgrounds":
            for key, collection in (("region_ids", "regions"), ("object_ids", "objects"), ("mask_ids", "masks")):
                for item_id in record.item.get(key, []):
                    try:
                        item = find_by_id(self.state, collection, item_id)
                    except KeyError:
                        continue
                    item_bbox = item.get("bbox")
                    if item_bbox:
                        return item_bbox
        return None

    def _source_image_path(self) -> Path:
        return workspace_path(self.workspace, self.state["source"].get("path", "source.png"))

    def _selected_bbox(self) -> list[int] | None:
        selected = self.asset_panel.current_asset()
        if not selected:
            return None
        bbox = selected.item.get("bbox")
        if bbox:
            return bbox
        mask_id = selected.item.get("mask_id")
        if mask_id:
            try:
                mask = find_by_id(self.state, "masks", mask_id)
                return mask.get("bbox")
            except KeyError:
                return None
        return None

    def _selected_mask_id(self) -> str | None:
        selected = self.asset_panel.current_asset()
        if not selected:
            return None
        return self._mask_id_for_record(selected)

    def _mask_id_for_record(self, record) -> str | None:
        if record.collection == "masks":
            return record.item_id
        if record.collection == "objects":
            return record.item.get("mask_id")
        return None

    def _selected_region(self):
        selected = self.asset_panel.current_asset()
        if selected and selected.collection == "regions":
            return selected
        return None

    def apply_preview_zoom(self, *args):
        return None

    def process_selected_assets(self):
        from PySide6.QtWidgets import QMessageBox

        selected_assets = self._selected_assets()
        if not selected_assets:
            QMessageBox.warning(self.window, "无法处理素材", "请先选择一个素材。")
            return
        if all(record.collection == "regions" for record in selected_assets):
            self.generate_mask_from_selected_region()
            return
        if len(selected_assets) == 1:
            self.rename_selected_asset()
            return
        QMessageBox.information(
            self.window,
            "暂不支持批量处理",
            "多选透明素材或处理结果时，当前可批量设为选用或删除；属性处理请先选择单个素材。",
        )

    def generate_mask_from_selected_region(self):
        from PySide6.QtWidgets import QMessageBox
        from gui.dialogs import RegionMaskSettingsDialog

        if not self.workspace or not self.state:
            QMessageBox.warning(self.window, "无法处理素材", "请先打开图片。")
            return
        selected_regions = self._compatible_assets(self._selected_assets())["regions"]
        if not selected_regions:
            QMessageBox.warning(self.window, "无法处理素材", "请先选择一个或多个框选区域。")
            return

        default_label = selected_regions[0].item.get("label") or selected_regions[0].item_id
        if len(selected_regions) > 1:
            default_label = f"批量区域 {len(selected_regions)} 个"
        dialog = RegionMaskSettingsDialog(self.window, profiles=list_profiles(), default_label=default_label)
        if not dialog.exec():
            return
        settings = dialog.values()
        for selected in selected_regions:
            if len(selected_regions) == 1 and settings["name"]:
                selected.item["label"] = settings["name"]
            selected.item["notes"] = settings["notes"]
            selected.item["selected"] = settings["selected"]
            selected.item["export_defaults"] = settings["export_defaults"]
        add_operation(
            self.state,
            "update-region-assets",
            params={
                "items": [record.item_id for record in selected_regions],
                "selected": settings["selected"],
                "generate_transparent": settings["generate_transparent"],
            },
        )
        save_state(self.workspace, self.state)
        if not settings["generate_transparent"]:
            last_id = selected_regions[-1].item_id
            self.load_workspace()
            self._select_asset_by_id(last_id)
            self.window.statusBar().showMessage(f"已更新 {len(selected_regions)} 个框选区域素材")
            return

        profile = resolve_profile(settings["profile"])

        source_path = self._source_image_path()
        mask_ids = self._reserve_ids("masks", "mask", len(selected_regions))
        object_ids = self._reserve_ids("objects", "obj", len(selected_regions))
        tasks = []

        def make_task(selected, mask_id: str, object_id: str | None):
            bbox = list(selected.item["bbox"])
            region_id = selected.item_id
            region_label = selected.item.get("label", "")

            def run_task() -> dict:
                last_error: Exception | None = None
                model_updates = []
                for model in profile.models:
                    output = self.workspace / "masks" / f"{mask_id}.png"
                    try:
                        result = remove_background_region(
                            source_path,
                            output,
                            model=model,
                            bbox=bbox,
                        )
                    except Exception as exc:
                        last_error = exc
                        model_updates.append(
                            {
                                "backend": profile.backend,
                                "model": model,
                                "profile": profile.name,
                                "status": "failed",
                                "message": str(exc),
                            }
                        )
                        continue

                    mask_item = {
                        "id": mask_id,
                        "path": relpath(result["mask_path"], self.workspace),
                        "source": "rembg-region",
                        "region_id": region_id,
                        "bbox": result["bbox"],
                        "region_bbox": result["region_bbox"],
                        "model": model,
                        "notes": settings["notes"],
                    }
                    selected_id = mask_id
                    object_item = None
                    object_output = self.workspace / "cutouts" / f"{object_id}.png"
                    extract_result = extract_object(
                        source_path,
                        workspace_path(self.workspace, mask_item["path"]),
                        object_output,
                        crop=True,
                    )
                    object_item = {
                        "id": object_id,
                        "path": relpath(object_output, self.workspace),
                        "mask_id": mask_item["id"],
                        "bbox": extract_result["bbox"],
                        "size": extract_result["size"],
                        "name": settings["name"] if len(selected_regions) == 1 else region_label,
                        "intent": settings["intent"],
                        "notes": settings["notes"],
                        "region_id": region_id,
                        "selected": settings["selected"],
                        "export_defaults": settings["export_defaults"],
                    }
                    selected_id = object_item["id"]
                    model_updates.append({"backend": profile.backend, "model": model, "profile": profile.name})
                    return {
                        "status": "ok",
                        "selected_id": selected_id,
                        "mask": mask_item,
                        "object": object_item,
                        "model_updates": model_updates,
                        "operation": {
                            "name": "remove-bg-region",
                            "params": {"region_id": region_id, "profile": profile.name, "model": model, "bbox": bbox},
                            "outputs": [mask_item["path"]],
                        },
                    }
                return {
                    "status": "failed",
                    "region_id": region_id,
                    "error": str(last_error) if last_error else "没有可用模型",
                    "model_updates": model_updates,
                    "operation": {
                        "name": "remove-bg-region",
                        "status": "failed",
                        "params": {"region_id": region_id, "profile": profile.name, "bbox": bbox},
                        "message": str(last_error) if last_error else "没有可用模型",
                    },
                }

            return run_task

        for selected, mask_id, object_id in zip(selected_regions, mask_ids, object_ids):
            tasks.append({"label": selected.item_id, "run": make_task(selected, mask_id, object_id)})

        def finish(results: list[dict]) -> None:
            created_ids = []
            errors = []
            for result in results:
                for update in result.get("model_updates", []):
                    upsert_model_record(self.state, **update)
                if result.get("status") == "ok":
                    mask_item = result["mask"]
                    self.state["masks"].append(mask_item)
                    add_operation(
                        self.state,
                        result["operation"]["name"],
                        params=result["operation"]["params"],
                        outputs=result["operation"]["outputs"],
                    )
                    object_item = result.get("object")
                    if object_item:
                        self.state["objects"].append(object_item)
                        add_operation(
                            self.state,
                            "extract-object",
                            params={"mask": mask_item["id"], "crop": True},
                            outputs=[object_item["path"]],
                        )
                    created_ids.append(result["selected_id"])
                else:
                    errors.append(f"{result.get('region_id', result.get('label', '任务'))}: {result.get('error', '处理失败')}")
                    operation = result.get("operation", {})
                    add_operation(
                        self.state,
                        operation.get("name", "remove-bg-region"),
                        status=operation.get("status", "failed"),
                        params=operation.get("params", {}),
                        message=operation.get("message", result.get("error", "处理失败")),
                    )
            save_state(self.workspace, self.state)
            self.load_workspace()
            if created_ids:
                self._select_asset_by_id(created_ids[-1])
                self.window.statusBar().showMessage(f"已生成 {len(created_ids)} 个透明素材")
            if errors:
                QMessageBox.warning(self.window, "部分透明素材生成失败", "\n".join(errors[:5]))

        self._start_background_batch("生成透明素材", tasks, finish)

    def extract_cutout_from_selected_mask(self):
        from PySide6.QtWidgets import QMessageBox
        from gui.dialogs import CutoutSettingsDialog

        if not self.workspace or not self.state:
            QMessageBox.warning(self.window, "无法生成透明素材", "请先打开图片。")
            return
        selected_masks = self._compatible_assets(self._selected_assets())["masks"]
        if not selected_masks:
            QMessageBox.warning(self.window, "无法生成透明素材", "请先选择一个或多个可处理素材。")
            return

        default_label = selected_masks[0].item.get("label") or selected_masks[0].item.get("region_id") or selected_masks[0].item_id
        if len(selected_masks) > 1:
            default_label = f"批量素材 {len(selected_masks)} 个"
        dialog = CutoutSettingsDialog(self.window, default_label=default_label)
        if not dialog.exec():
            return
        settings = dialog.values()
        created = []
        errors = []
        self._begin_progress("生成透明素材", "准备生成透明素材...", total=len(selected_masks))
        try:
            for index, selected in enumerate(selected_masks, start=1):
                self._update_progress(index - 1, f"正在生成 {index}/{len(selected_masks)}：{selected.item_id}")
                try:
                    object_item = self._create_cutout_from_mask_item(
                        selected.item,
                        name=settings["name"] if len(selected_masks) == 1 else selected.item.get("region_id", selected.item_id),
                        intent=settings["intent"],
                        notes=settings["notes"],
                        crop=settings["crop"],
                    )
                    created.append(object_item)
                except Exception as exc:
                    errors.append(f"{selected.item_id}: {exc}")
                self._update_progress(index, f"已生成 {index}/{len(selected_masks)}")
        finally:
            self._end_progress()

        save_state(self.workspace, self.state)
        self.load_workspace()
        if created:
            self._select_asset_by_id(created[-1]["id"])
            self.window.statusBar().showMessage(f"已生成 {len(created)} 个透明素材")
        if errors:
            QMessageBox.warning(self.window, "部分透明素材生成失败", "\n".join(errors[:5]))

    def _create_cutout_from_mask_item(
        self,
        mask_item: dict,
        *,
        name: str = "",
        intent: str = "",
        notes: str = "",
        crop: bool = True,
    ) -> dict:
        object_id = next_id(self.state, "objects", "obj")
        output = self.workspace / "cutouts" / f"{object_id}.png"
        result = extract_object(
            self._source_image_path(),
            workspace_path(self.workspace, mask_item["path"]),
            output,
            crop=crop,
        )
        item = {
            "id": object_id,
            "path": relpath(output, self.workspace),
            "mask_id": mask_item["id"],
            "bbox": result["bbox"],
            "size": result["size"],
            "name": name,
            "intent": intent,
            "notes": notes,
        }
        if mask_item.get("region_id"):
            item["region_id"] = mask_item["region_id"]
        self.state["objects"].append(item)
        add_operation(
            self.state,
            "extract-object",
            params={"mask": mask_item["id"], "crop": crop},
            outputs=[item["path"]],
        )
        return item

    def export_selected_object(self):
        from PySide6.QtWidgets import QMessageBox
        from gui.dialogs import ExportSettingsDialog

        if not self.workspace or not self.state:
            QMessageBox.warning(self.window, "无法导出", "请先打开图片。")
            return
        selected_assets = self._compatible_assets(self._selected_assets())["exportables"]
        if not selected_assets:
            fallback = self._find_first_object(self.asset_records)
            selected_assets = [fallback] if fallback else []
        if not selected_assets:
            QMessageBox.warning(self.window, "无法导出", "当前图片没有可导出的框选区域、透明素材或抹除结果。")
            return

        dialog = ExportSettingsDialog(
            self.window,
            title=f"导出 {len(selected_assets)} 个素材" if len(selected_assets) > 1 else f"导出 {selected_assets[0].label} {selected_assets[0].item_id}",
            defaults=selected_assets[0].item.get("export_defaults", {}),
        )
        if not dialog.exec():
            return
        settings = dialog.values()
        export_ids = self._reserve_ids("exports", "export", len(selected_assets))
        tasks = []

        def make_task(selected, export_id: str):
            def run_task() -> dict:
                output_format = settings["format"]
                output_path = self.workspace / "exports" / f"{export_id}.{output_format}"
                if selected.collection == "regions":
                    result = export_region_variant(
                        self._source_image_path(),
                        output_path,
                        bbox=selected.item["bbox"],
                        transparent=settings["transparent"],
                        background=None,
                        corner_radius=settings["corner_radius"],
                        padding=settings["padding"],
                        crop_mode=settings["crop_mode"],
                        output_format=output_format,
                    )
                else:
                    result = export_variant(
                        workspace_path(self.workspace, selected.path),
                        output_path,
                        transparent=settings["transparent"],
                        background=None,
                        corner_radius=settings["corner_radius"],
                        padding=settings["padding"],
                        crop_mode=settings["crop_mode"],
                        output_format=output_format,
                    )
                item = {
                    "id": export_id,
                    "path": relpath(result["path"], self.workspace),
                    "size": result["size"],
                    "transparent": result["transparent"],
                    "background": result["background"],
                    "corner_radius": result["corner_radius"],
                    "padding": result["padding"],
                    "crop_mode": result["crop_mode"],
                    "format": result["format"],
                    "notes": "GUI 导出",
                }
                if selected.collection == "regions":
                    item["region_id"] = selected.item_id
                    item["bbox"] = result.get("bbox", selected.item.get("bbox"))
                elif selected.collection == "objects":
                    item["object_id"] = selected.item_id
                elif selected.collection == "backgrounds":
                    item["background_id"] = selected.item_id
                return {"status": "ok", "item": item}

            return run_task

        for selected, export_id in zip(selected_assets, export_ids):
            tasks.append({"label": selected.item_id, "run": make_task(selected, export_id)})

        def finish(results: list[dict]) -> None:
            created = []
            errors = []
            for result in results:
                if result.get("status") == "ok":
                    item = result["item"]
                    self.state["exports"].append(item)
                    created.append(item)
                    add_operation(self.state, "export-variant", params=item, outputs=[item["path"]])
                else:
                    errors.append(f"{result.get('label', '任务')}: {result.get('error', '导出失败')}")
            save_state(self.workspace, self.state)
            self.load_workspace()
            if created:
                self._select_asset_by_id(created[-1]["id"])
            self.window.statusBar().showMessage(f"已导出 {len(created)} 个素材")
            if errors:
                QMessageBox.warning(self.window, "部分素材导出失败", "\n".join(errors[:5]))

        self._start_background_batch("导出素材", tasks, finish)

    def repair_selected_background(self):
        from PySide6.QtWidgets import QMessageBox
        from gui.dialogs import ErasePickerDialog, RepairSettingsDialog

        if not self.workspace or not self.state:
            QMessageBox.warning(self.window, "无法抹除", "请先打开图片。")
            return
        selected_assets = self._selected_assets()
        if len(selected_assets) != 1:
            QMessageBox.warning(self.window, "无法抹除", "请先选择一个素材，再标记要抹除的内容。")
            return
        selected = selected_assets[0]
        try:
            context = self._erase_context_for_asset(selected)
        except Exception as exc:
            QMessageBox.warning(self.window, "无法打开素材", str(exc))
            return

        picker = ErasePickerDialog(
            self.window,
            image_path=str(context["image_path"]),
            title=f"当前素材：{selected.label} {selected.item_id}",
            line_width=self.region_line_width.value(),
        )
        if not picker.exec():
            return
        local_bboxes = picker.bboxes()
        if not local_bboxes:
            QMessageBox.warning(self.window, "没有抹除标记", "请先在素材图上框出需要抹除的内容。")
            return
        dialog = RepairSettingsDialog(self.window)
        if not dialog.exec():
            return
        settings = dialog.values()
        mask_id = next_id(self.state, "masks", "mask")
        bg_id = next_id(self.state, "backgrounds", "bg")
        target_path = Path(context["image_path"])

        def run_task() -> dict:
            mask_output = self.workspace / "masks" / f"{mask_id}.png"
            output = self.workspace / "backgrounds" / f"{bg_id}.png"
            mask_result = create_bboxes_mask_file(target_path, mask_output, bboxes=local_bboxes)
            try:
                result = inpaint_background_isolated(
                    target_path,
                    mask_output,
                    output,
                    method=settings["method"],
                    device=settings["device"],
                )
            except Exception as exc:
                if not settings["fallback"]:
                    return {"status": "failed", "asset_id": selected.item_id, "error": str(exc)}
                try:
                    result = inpaint_background_isolated(
                        target_path,
                        mask_output,
                        output,
                        method="opencv-telea",
                    )
                    result["fallback_from"] = "lama"
                    result["fallback_reason"] = str(exc)
                except Exception as fallback_exc:
                    return {"status": "failed", "asset_id": selected.item_id, "error": str(fallback_exc)}

            mask_item = {
                "id": mask_id,
                "path": relpath(mask_output, self.workspace),
                "source": "marked-erase",
                "asset": {"collection": selected.collection, "id": selected.item_id},
                "bbox": mask_result["bbox"],
                "bboxes": mask_result["bboxes"],
                "notes": "GUI 基于素材标记抹除自动生成",
                "internal": True,
            }

            item = {
                "id": bg_id,
                "path": relpath(output, self.workspace),
                "scope": {"type": selected.collection, "ids": [selected.item_id]},
                "erase_bboxes": mask_result["bboxes"],
                "mask_ids": [mask_id],
                "source_asset_path": relpath(target_path, self.workspace),
                "method": result["method"],
                "backend": result.get("backend"),
                "device": result.get("device"),
                "iopaint_bin": result.get("iopaint_bin"),
                "config_path": result.get("config_path"),
                "radius": result.get("radius"),
            }
            if selected.collection == "regions":
                item["region_ids"] = [selected.item_id]
            elif selected.collection == "objects":
                item["object_ids"] = [selected.item_id]
            elif selected.collection == "backgrounds":
                item["background_ids"] = [selected.item_id]
            if "fallback_from" in result:
                item["fallback_from"] = result["fallback_from"]
                item["fallback_reason"] = result["fallback_reason"]
            return {"status": "ok", "mask": mask_item, "item": item}

        def finish(results: list[dict]) -> None:
            created = []
            errors = []
            for result in results:
                if result.get("status") == "ok":
                    mask_item = result["mask"]
                    self.state["masks"].append(mask_item)
                    add_operation(
                        self.state,
                        "create-marked-erase-mask",
                        params={
                            "asset": mask_item["asset"],
                            "bbox": mask_item["bbox"],
                            "bboxes": mask_item["bboxes"],
                        },
                        outputs=[mask_item["path"]],
                    )
                    item = result["item"]
                    self.state["backgrounds"].append(item)
                    created.append(item)
                    add_operation(self.state, "inpaint-background", params=item, outputs=[item["path"]])
                else:
                    errors.append(f"{result.get('asset_id', result.get('label', '任务'))}: {result.get('error', '抹除失败')}")
            save_state(self.workspace, self.state)
            self.load_workspace()
            if created:
                self._select_asset_by_id(created[-1]["id"])
                self.window.statusBar().showMessage(f"已基于当前素材的 {len(local_bboxes)} 个标记完成抹除")
            if errors:
                QMessageBox.warning(
                    self.window,
                    "抹除失败",
                    "\n".join(errors[:5]) + ("\n\n如需生成低质量候选，可勾选“允许低质量 fallback”。" if not settings["fallback"] else ""),
                )

        self._start_background_batch("标记抹除", [{"label": selected.item_id, "run": run_task}], finish)

    def _erase_context_for_asset(self, record) -> dict:
        if record.collection == "regions":
            bbox = record.item.get("bbox")
            if not bbox:
                raise ValueError("当前框选区域没有 bbox。")
            image_path = self._crop_source_context(record.item_id, bbox)
            return {"image_path": image_path}
        if record.collection == "objects":
            return {"image_path": workspace_path(self.workspace, record.path)}
        if record.collection == "backgrounds":
            return {"image_path": workspace_path(self.workspace, record.path)}
        raise ValueError("该素材类型不支持标记抹除。")

    def _crop_source_context(self, item_id: str, bbox: list[int], *, prefix: str = "erase_context") -> Path:
        try:
            from PIL import Image
        except ImportError as exc:
            raise RuntimeError("需要安装 Pillow 才能打开框选素材。") from exc
        output = self.workspace / "preview-cache" / f"{prefix}_{item_id}.png"
        output.parent.mkdir(parents=True, exist_ok=True)
        with Image.open(self._source_image_path()).convert("RGBA") as source:
            x1, y1, x2, y2 = [int(value) for value in bbox]
            source.crop((x1, y1, x2, y2)).save(output)
        return output

    def _select_asset_by_id(self, item_id: str) -> None:
        for index in range(self.asset_panel.list_widget.count()):
            item = self.asset_panel.list_widget.item(index)
            record = item.data(self.asset_panel._qt_user_role)
            if record and record.item_id == item_id:
                self.asset_panel.list_widget.setCurrentItem(item)
                return

    def toggle_region_mode(self):
        enabled = not self.source_canvas.region_mode
        self.source_canvas.set_region_mode(enabled)
        self.region_button.setText("结束" if enabled else "框选")
        self.window.statusBar().showMessage("拖拽左侧原图创建待确认选框，可移动后统一确认切出" if enabled else "已关闭框选")
        self.update_pending_region_controls()

    def update_pending_region_controls(self, count: int | None = None) -> None:
        if count is None:
            count = self.source_canvas.pending_count()
        has_current = self.source_canvas.current_region_exists()
        has_pending = count > 0
        self.add_region_button.setEnabled(has_current and not self._is_processing)
        self.confirm_regions_button.setEnabled(has_pending and not self._is_processing)
        self.clear_regions_button.setEnabled(has_pending and not self._is_processing)
        self.confirm_regions_button.setText(f"切出({count})" if has_pending else "切出")

    def add_pending_region(self) -> None:
        if self.source_canvas.add_current_region():
            self.window.statusBar().showMessage("已添加选框，可继续拖拽创建新的选框")
        else:
            self.window.statusBar().showMessage("请先拖拽创建一个当前选框")
        self.update_pending_region_controls()

    def clear_pending_regions(self) -> None:
        self.source_canvas.clear_pending_regions()
        self.window.statusBar().showMessage("已清空待确认选框")

    def confirm_pending_regions(self) -> None:
        from PySide6.QtWidgets import QMessageBox

        if not self.workspace or not self.state:
            return
        bboxes = self.source_canvas.pending_bboxes()
        if not bboxes:
            QMessageBox.information(self.window, "没有待确认选框", "请先框选一个或多个区域。")
            return
        created = []
        try:
            for bbox in bboxes:
                created.append(self._add_region_from_bbox(bbox))
        except Exception as exc:
            QMessageBox.warning(self.window, "确认切出失败", str(exc))
            return
        self.source_canvas.clear_pending_regions(notify=False)
        self.load_workspace()
        if created:
            self._select_asset_by_id(created[-1]["id"])
        self.update_pending_region_controls(0)
        self.window.statusBar().showMessage(f"已确认切出 {len(created)} 个区域")

    def open_region_picker(self):
        from PySide6.QtWidgets import QMessageBox
        from gui.dialogs import RegionPickerDialog

        if not self.workspace or not self.state:
            QMessageBox.warning(self.window, "无法放大框选", "请先打开图片。")
            return

        dialog_holder = {"dialog": None}

        def add_region(bbox: list[int]) -> None:
            try:
                region = self._add_region_from_bbox(bbox)
                if dialog_holder["dialog"]:
                    dialog_holder["dialog"].set_regions(self.state.get("regions", []))
                self.window.statusBar().showMessage(f"已创建区域：{region['id']}")
            except Exception as exc:
                QMessageBox.warning(self.window, "区域创建失败", str(exc))

        dialog = RegionPickerDialog(
            self.window,
            image_path=str(self._source_image_path()),
            regions=self.state.get("regions", []),
            line_width=self.region_line_width.value(),
            aspect_ratio=self.source_canvas.aspect_ratio,
            on_region_created=add_region,
        )
        dialog_holder["dialog"] = dialog
        dialog.exec()
        self.load_workspace()

    def create_region_from_bbox(self, bbox: list[int]) -> None:
        from PySide6.QtWidgets import QMessageBox

        if not self.workspace or not self.state:
            return
        try:
            region = self._add_region_from_bbox(bbox)
        except Exception as exc:
            QMessageBox.warning(self.window, "区域创建失败", str(exc))
            return
        self.load_workspace()
        self._select_asset_by_id(region["id"])
        self.window.statusBar().showMessage(f"已创建区域：{region['id']}")

    def _add_region_from_bbox(self, bbox: list[int]) -> dict:
        region_id = next_id(self.state, "regions", "region")
        thumb_path = self.workspace / "preview-cache" / f"thumb_{region_id}.png"
        defaults = {
            "transparent": True,
            "corner_radius": 0,
            "padding": 0,
            "crop_mode": "bbox",
            "format": "png",
        }
        self._render_region_thumbnail(self._source_image_path(), thumb_path, bbox=bbox)
        region = {
            "id": region_id,
            "type": "bbox",
            "bbox": bbox,
            "label": region_id,
            "notes": "",
            "thumbnail": relpath(thumb_path, self.workspace),
            "created_at": utc_now(),
            "export_defaults": defaults,
        }
        self.state["regions"].append(region)
        add_operation(
            self.state,
            "create-region",
            params={"bbox": bbox, "label": region["label"], "export_defaults": region["export_defaults"]},
            outputs=[region["thumbnail"]],
        )
        save_state(self.workspace, self.state)
        return region

    def open_detail_viewer(self, *args):
        from PySide6.QtWidgets import QMessageBox
        from gui.dialogs import DetailViewer

        if not self.workspace or not self.state:
            return
        assets = list(self.asset_records)
        if not assets:
            QMessageBox.warning(self.window, "无法放大查看", "当前没有可查看的素材。")
            return
        selected = self.asset_panel.current_asset()
        current_index = 0
        if selected:
            for index, record in enumerate(assets):
                if record.collection == selected.collection and record.item_id == selected.item_id:
                    current_index = index
                    break

        def resolve_path(record):
            return self._detail_path_for_asset(record)

        try:
            DetailViewer(
                self.window,
                assets=assets,
                current_index=current_index,
                workspace=self.workspace,
                resolve_path=resolve_path,
            ).exec()
        except Exception as exc:
            QMessageBox.warning(self.window, "无法放大查看", str(exc))

    def rename_selected_asset(self):
        from PySide6.QtWidgets import QMessageBox
        from gui.dialogs import AssetSettingsDialog

        selected = self.asset_panel.current_asset()
        if not selected:
            QMessageBox.warning(self.window, "无法编辑", "请先选择一个素材。")
            return
        current_label = selected.item.get("label") or selected.item.get("name") or selected.item_id
        dialog = AssetSettingsDialog(
            self.window,
            title="处理素材",
            label=current_label,
            notes=selected.item.get("notes", ""),
            selected=bool(selected.item.get("selected")),
            defaults=selected.item.get("export_defaults", {}),
        )
        if not dialog.exec():
            return
        values = dialog.values()
        if selected.collection == "objects":
            selected.item["name"] = values["label"]
        else:
            selected.item["label"] = values["label"]
        selected.item["notes"] = values["notes"]
        selected.item["selected"] = values["selected"]
        selected.item["export_defaults"] = values["export_defaults"]
        add_operation(
            self.state,
            "update-asset-settings",
            params={"collection": selected.collection, "id": selected.item_id},
        )
        save_state(self.workspace, self.state)
        self.load_workspace()
        self._select_asset_by_id(selected.item_id)

    def toggle_selected_flag(self):
        from PySide6.QtWidgets import QMessageBox

        selected_assets = self._selected_assets()
        if not selected_assets:
            QMessageBox.warning(self.window, "无法标记", "请先选择一个或多个素材。")
            return
        should_select = not all(record.item.get("selected") for record in selected_assets)
        for record in selected_assets:
            record.item["selected"] = should_select
        add_operation(
            self.state,
            "toggle-selected-assets",
            params={
                "selected": should_select,
                "items": [{"collection": record.collection, "id": record.item_id} for record in selected_assets],
            },
        )
        save_state(self.workspace, self.state)
        last_id = selected_assets[-1].item_id
        self.load_workspace()
        self._select_asset_by_id(last_id)

    def delete_selected_assets(self):
        from PySide6.QtWidgets import QMessageBox

        selected_assets = self._selected_assets()
        if not selected_assets:
            QMessageBox.warning(self.window, "无法删除", "请先选择一个或多个素材。")
            return
        answer = QMessageBox.question(
            self.window,
            "删除素材",
            f"确定删除选中的 {len(selected_assets)} 个素材吗？生成文件也会一并删除。",
        )
        if answer != QMessageBox.Yes:
            return
        removed = []
        for record in selected_assets:
            collection = self.state.get(record.collection, [])
            self.state[record.collection] = [item for item in collection if item.get("id") != record.item_id]
            for key in ("path", "thumbnail"):
                value = record.item.get(key)
                if not value:
                    continue
                try:
                    workspace_path(self.workspace, value).unlink(missing_ok=True)
                except OSError:
                    pass
            removed.append({"collection": record.collection, "id": record.item_id})
        add_operation(self.state, "delete-assets", params={"items": removed})
        save_state(self.workspace, self.state)
        self.load_workspace()
        self.window.statusBar().showMessage(f"已删除 {len(removed)} 个素材")
