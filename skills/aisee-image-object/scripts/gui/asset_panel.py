"""Workspace asset list panel."""

from __future__ import annotations


class AssetPanel:
    def __init__(self, *, title: str = "素材", max_height: int | None = None):
        from PySide6.QtCore import QSize, Qt
        from PySide6.QtWidgets import (
            QAbstractItemView,
            QAbstractScrollArea,
            QComboBox,
            QHBoxLayout,
            QLabel,
            QListView,
            QListWidget,
            QSizePolicy,
        )
        from gui.components import create_panel, create_section_header

        self.group, layout = create_panel(object_name="AssetStrip", max_height=max_height, spacing=10)
        self.group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(8)
        header.addLayout(create_section_header("ASSETS", title))
        header.addWidget(QLabel("分类"))
        self.category_filter = QComboBox()
        self.category_filter.addItems(["全部", "选用", "框选区域", "透明素材", "抹除结果", "导出结果", "优化"])
        header.addWidget(self.category_filter)
        layout.addLayout(header)

        class AssetListWidget(QListWidget):
            def resizeEvent(list_self, event):
                super().resizeEvent(event)
                list_self.owner._update_grid_size()

        self.list_widget = AssetListWidget()
        self.list_widget.owner = self
        self.list_widget.setObjectName("AssetGrid")
        self._qt_user_role = Qt.UserRole
        self._all_records = []
        self._workspace = None
        self.list_widget.setViewMode(QListWidget.IconMode)
        self.list_widget.setFlow(QListView.LeftToRight)
        self.list_widget.setWrapping(True)
        self.list_widget.setIconSize(QSize(132, 96))
        self.list_widget.setGridSize(QSize(176, 146))
        self.list_widget.setResizeMode(QListWidget.Adjust)
        self.list_widget.setSizeAdjustPolicy(QAbstractScrollArea.AdjustIgnored)
        self.list_widget.setMovement(QListWidget.Static)
        self.list_widget.setSpacing(10)
        self.list_widget.setUniformItemSizes(True)
        self.list_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.list_widget.setMinimumHeight(360)
        self.list_widget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.list_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.list_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        layout.addWidget(self.list_widget)
        self.category_filter.currentTextChanged.connect(self._apply_filter)

    def widget(self):
        return self.group

    def set_items(self, items: list[str]) -> None:
        self.list_widget.clear()
        self.list_widget.addItems(items)

    def set_assets(self, records, workspace=None) -> None:
        self._all_records = list(records)
        self._workspace = workspace
        self._apply_filter()

    def _apply_filter(self) -> None:
        from PySide6.QtGui import QIcon
        from PySide6.QtWidgets import QListWidgetItem

        self.list_widget.clear()
        category = self.category_filter.currentText()
        records = [
            record
            for record in self._all_records
            if category == "全部"
            or (category == "选用" and record.item.get("selected"))
            or record.label == category
        ]
        for record in records:
            name = record.item.get("name") or record.item.get("label") or record.item_id
            prefix = "[选用] " if record.item.get("selected") else ""
            label = f"{prefix}{record.label}\n{name}"
            item = QListWidgetItem(label)
            thumbnail = record.item.get("thumbnail")
            if thumbnail and self._workspace:
                item.setIcon(QIcon(str(__import__("pathlib").Path(self._workspace) / thumbnail)))
            item.setToolTip(record.display)
            item.setData(self._qt_user_role, record)
            self.list_widget.addItem(item)
        self._update_grid_size()

    def _update_grid_size(self) -> None:
        from PySide6.QtCore import QSize

        width = max(1, self.list_widget.viewport().width())
        min_cell = 138
        columns = max(1, width // min_cell)
        cell_width = max(min_cell, (width - 12) // columns)
        icon_width = max(88, min(148, cell_width - 30))
        icon_height = int(icon_width * 0.70)
        self.list_widget.setIconSize(QSize(icon_width, icon_height))
        self.list_widget.setGridSize(QSize(cell_width, icon_height + 50))

    def current_asset(self):
        item = self.list_widget.currentItem()
        if not item:
            return None
        return item.data(self._qt_user_role)

    def selected_assets(self):
        records = []
        for item in self.list_widget.selectedItems():
            record = item.data(self._qt_user_role)
            if record:
                records.append(record)
        current = self.current_asset()
        if current and not records:
            records.append(current)
        return records
