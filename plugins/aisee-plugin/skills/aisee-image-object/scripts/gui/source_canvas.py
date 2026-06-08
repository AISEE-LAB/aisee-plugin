"""Source image canvas."""

from __future__ import annotations


class _RegionGraphicsView:
    pass


class SourceCanvas:
    def __init__(self):
        from PySide6.QtCore import QPointF, QRectF, Qt, QVariantAnimation
        from PySide6.QtGui import QColor, QBrush, QPen
        from PySide6.QtWidgets import (
            QLabel,
            QGraphicsPixmapItem,
            QGraphicsRectItem,
            QGraphicsScene,
            QGraphicsView,
            QSizePolicy,
        )

        class PendingRectItem(QGraphicsRectItem):
            def __init__(item_self, owner, x, y, width, height):
                super().__init__(0, 0, width, height)
                item_self.owner = owner
                item_self.saved = False
                item_self._resize_handle = None
                item_self._press_scene_pos = None
                item_self._press_scene_rect = None
                item_self.setPos(x, y)
                item_self.setAcceptHoverEvents(True)

            def itemChange(item_self, change, value):
                if change == item_self.GraphicsItemChange.ItemPositionChange:
                    return item_self.owner._clamped_pending_pos(item_self, value)
                if change == item_self.GraphicsItemChange.ItemPositionHasChanged:
                    item_self.owner._notify_pending_changed()
                    item_self.owner._show_region_size_hint(item_self.sceneBoundingRect())
                if change == item_self.GraphicsItemChange.ItemSelectedHasChanged:
                    item_self.owner._refresh_pending_style()
                return super().itemChange(change, value)

            def hoverMoveEvent(item_self, event):
                item_self.setCursor(item_self.owner._cursor_for_handle(item_self._handle_at(event.pos())))
                super().hoverMoveEvent(event)

            def mousePressEvent(item_self, event):
                if event.button() == item_self.owner._qt.LeftButton:
                    handle = item_self._handle_at(event.pos())
                    if handle:
                        item_self._resize_handle = handle
                        item_self._press_scene_pos = event.scenePos()
                        item_self._press_scene_rect = item_self.mapRectToScene(item_self.rect())
                        event.accept()
                        return
                super().mousePressEvent(event)

            def mouseMoveEvent(item_self, event):
                if item_self._resize_handle:
                    delta = event.scenePos() - item_self._press_scene_pos
                    item_self.owner._resize_pending_item(item_self, item_self._press_scene_rect, delta, item_self._resize_handle)
                    event.accept()
                    return
                super().mouseMoveEvent(event)

            def mouseReleaseEvent(item_self, event):
                if item_self._resize_handle:
                    item_self._resize_handle = None
                    item_self._press_scene_pos = None
                    item_self._press_scene_rect = None
                    item_self.owner._hide_region_size_hint()
                    item_self.owner._notify_pending_changed()
                    event.accept()
                    return
                super().mouseReleaseEvent(event)
                item_self.owner._hide_region_size_hint()

            def _handle_at(item_self, point):
                rect = item_self.rect()
                threshold = item_self.owner._handle_threshold()
                left = abs(point.x() - rect.left()) <= threshold
                right = abs(point.x() - rect.right()) <= threshold
                top = abs(point.y() - rect.top()) <= threshold
                bottom = abs(point.y() - rect.bottom()) <= threshold
                inside_x = rect.left() - threshold <= point.x() <= rect.right() + threshold
                inside_y = rect.top() - threshold <= point.y() <= rect.bottom() + threshold
                if top and left:
                    return "top-left"
                if top and right:
                    return "top-right"
                if bottom and left:
                    return "bottom-left"
                if bottom and right:
                    return "bottom-right"
                if left and inside_y:
                    return "left"
                if right and inside_y:
                    return "right"
                if top and inside_x:
                    return "top"
                if bottom and inside_x:
                    return "bottom"
                return None

        class CanvasView(QGraphicsView):
            def __init__(view_self, owner):
                super().__init__()
                view_self.owner = owner
                view_self.drag_start = None
                view_self.drag_rect_item = None

            def mousePressEvent(view_self, event):
                if view_self.owner.region_mode and not view_self.owner.pixmap_item.pixmap().isNull():
                    if view_self.owner._pending_item_at(event.position().toPoint()) is not None:
                        super().mousePressEvent(event)
                        event.accept()
                        return
                    view_self.drag_start = view_self.mapToScene(event.position().toPoint())
                    view_self.drag_rect_item = QGraphicsRectItem()
                    pen = QPen(QColor("#0066cc"), view_self.owner.region_line_width, Qt.DashLine)
                    pen.setCosmetic(True)
                    view_self.drag_rect_item.setPen(pen)
                    view_self.owner.scene.addItem(view_self.drag_rect_item)
                    event.accept()
                    return
                super().mousePressEvent(event)

            def mouseMoveEvent(view_self, event):
                if view_self.owner.region_mode and view_self.drag_start and view_self.drag_rect_item:
                    current = view_self.mapToScene(event.position().toPoint())
                    rect = view_self.owner._drag_rect(view_self.drag_start, current)
                    view_self.drag_rect_item.setRect(rect)
                    view_self.owner._show_region_size_hint(rect)
                    view_self.owner._notify_region_preview(rect)
                    event.accept()
                    return
                super().mouseMoveEvent(event)

            def mouseReleaseEvent(view_self, event):
                if view_self.owner.region_mode and view_self.drag_start:
                    current = view_self.mapToScene(event.position().toPoint())
                    rect = view_self.owner._drag_rect(view_self.drag_start, current)
                    if view_self.drag_rect_item:
                        view_self.owner.scene.removeItem(view_self.drag_rect_item)
                    view_self.drag_start = None
                    view_self.drag_rect_item = None
                    view_self.owner._hide_region_size_hint()
                    view_self.owner._notify_region_preview(None)
                    bbox = view_self.owner._clamped_bbox(rect)
                    if bbox:
                        view_self.owner.set_current_region(bbox)
                    event.accept()
                    return
                super().mouseReleaseEvent(event)

            def wheelEvent(view_self, event):
                if event.modifiers() & Qt.ControlModifier:
                    delta = event.angleDelta().y()
                    if delta:
                        view_self.owner.zoom_by(1.15 if delta > 0 else 1 / 1.15)
                    event.accept()
                    return
                super().wheelEvent(event)

        self.view = CanvasView(self)
        self.view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.view.setDragMode(QGraphicsView.ScrollHandDrag)
        self.view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.view.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.view.setAlignment(Qt.AlignCenter)
        self.scene = QGraphicsScene(self.view)
        self.view.setScene(self.scene)
        self.pixmap_item = QGraphicsPixmapItem()
        self.scene.addItem(self.pixmap_item)
        self.size_hint_label = QLabel(self.view.viewport())
        self.size_hint_label.setStyleSheet(
            "background: #fbfbfd; color: #1d1d1f; border: 1px solid #0066cc; "
            "border-radius: 6px; padding: 3px 7px; font-size: 12px;"
        )
        self.size_hint_label.hide()
        self.region_items = []
        self.pending_items = []
        self.current_item = None
        self.regions = []
        self.region_line_width = 2
        self.region_mode = False
        self.on_region_created = None
        self.on_region_preview = None
        self.on_pending_changed = None
        self.aspect_ratio = None
        self._rect_item_cls = QGraphicsRectItem
        self._pending_rect_item_cls = PendingRectItem
        self._view_cls = QGraphicsView
        self._pen = QPen
        self._brush = QBrush
        self._color = QColor
        self._qt = Qt
        self._point_cls = QPointF
        self._rectf_cls = QRectF
        self._animation_cls = QVariantAnimation
        self._animations = []
        self._zoom_scale = 1.0

    def widget(self):
        return self.view

    def set_pixmap(self, pixmap) -> None:
        self.pixmap_item.setPixmap(pixmap)
        self.scene.setSceneRect(self.pixmap_item.boundingRect())
        self._hide_region_size_hint()
        self.fit()
        self.set_regions([])
        self.clear_pending_regions(notify=False)

    def fit(self) -> None:
        if not self.pixmap_item.pixmap().isNull():
            self._zoom_scale = 1.0
            self.view.fitInView(
                self.pixmap_item,
                __import__("PySide6.QtCore", fromlist=["Qt"]).Qt.KeepAspectRatio,
            )

    def set_zoom(self, zoom: str) -> None:
        if zoom == "适应":
            self.fit()
            return
        value = zoom.rstrip("%")
        if not value.isdigit():
            return
        scale = int(value) / 100.0
        self.view.resetTransform()
        self.view.scale(scale, scale)
        self._zoom_scale = scale

    def zoom_by(self, factor: float) -> None:
        if self.pixmap_item.pixmap().isNull():
            return
        next_scale = min(8.0, max(0.1, self._zoom_scale * factor))
        factor = next_scale / self._zoom_scale
        self.view.scale(factor, factor)
        self._zoom_scale = next_scale

    def set_region_mode(self, enabled: bool) -> None:
        self.region_mode = enabled
        self.view.setDragMode(self._view_cls.NoDrag if enabled else self._view_cls.ScrollHandDrag)

    def set_region_line_width(self, width: int) -> None:
        self.region_line_width = max(1, int(width))
        self.set_regions(self.regions)
        self._refresh_pending_style()

    def set_aspect_ratio(self, ratio: float | None) -> None:
        self.aspect_ratio = ratio if ratio and ratio > 0 else None

    def set_regions(self, regions: list[dict]) -> None:
        self.regions = list(regions)
        for item in self.region_items:
            self.scene.removeItem(item)
        self.region_items = []
        for region in regions:
            bbox = region.get("bbox")
            if not bbox or len(bbox) != 4:
                continue
            x1, y1, x2, y2 = [int(value) for value in bbox]
            rect_item = self._rect_item_cls(x1, y1, max(1, x2 - x1), max(1, y2 - y1))
            pen = self._pen(self._color("#0066cc"), self.region_line_width)
            pen.setCosmetic(True)
            rect_item.setPen(pen)
            self.scene.addItem(rect_item)
            self.region_items.append(rect_item)

    def _create_pending_item(self, bbox: list[int], *, saved: bool):
        x1, y1, x2, y2 = [int(value) for value in bbox]
        rect_item = self._pending_rect_item_cls(self, x1, y1, max(1, x2 - x1), max(1, y2 - y1))
        rect_item.saved = saved
        rect_item.setFlag(rect_item.GraphicsItemFlag.ItemIsMovable, True)
        rect_item.setFlag(rect_item.GraphicsItemFlag.ItemIsSelectable, True)
        rect_item.setFlag(rect_item.GraphicsItemFlag.ItemSendsGeometryChanges, True)
        rect_item.setCursor(self._qt.OpenHandCursor)
        rect_item.setZValue(12 if saved else 20)
        self.scene.addItem(rect_item)
        rect_item.setSelected(True)
        self._refresh_pending_style()
        self._animate_pending_region(rect_item)
        return rect_item

    def set_current_region(self, bbox: list[int]) -> None:
        if self.current_item:
            self.scene.removeItem(self.current_item)
        self.current_item = self._create_pending_item(bbox, saved=False)
        self._notify_pending_changed()

    def add_current_region(self) -> bool:
        if not self.current_item:
            return False
        self.current_item.saved = True
        self.current_item.setZValue(12)
        self.pending_items.append(self.current_item)
        self.current_item = None
        self._refresh_pending_style()
        self._notify_pending_changed()
        return True

    def add_pending_region(self, bbox: list[int]) -> None:
        self.set_current_region(bbox)
        self.add_current_region()

    def clear_pending_regions(self, *, notify: bool = True) -> None:
        for item in self._selection_items():
            self.scene.removeItem(item)
        self.pending_items = []
        self.current_item = None
        if notify:
            self._notify_pending_changed()

    def pending_bboxes(self) -> list[list[int]]:
        bboxes = []
        for item in self._selection_items():
            bbox = self._clamped_bbox(item.rect().translated(item.pos()))
            if bbox:
                bboxes.append(bbox)
        return bboxes

    def pending_count(self) -> int:
        return len(self.pending_items) + (1 if self.current_item else 0)

    def current_region_exists(self) -> bool:
        return self.current_item is not None

    def _selection_items(self):
        return [*self.pending_items, *([self.current_item] if self.current_item else [])]

    def _pending_pen(self):
        pen = self._pen(self._color("#ff8a00"), self.region_line_width, self._qt.SolidLine)
        pen.setCosmetic(True)
        return pen

    def _current_pen(self):
        pen = self._pen(self._color("#0066cc"), self.region_line_width + 1, self._qt.SolidLine)
        pen.setCosmetic(True)
        return pen

    def _selected_pending_pen(self):
        pen = self._pen(self._color("#0066cc"), self.region_line_width + 1, self._qt.SolidLine)
        pen.setCosmetic(True)
        return pen

    def _refresh_pending_style(self) -> None:
        for item in self._selection_items():
            if item is self.current_item:
                item.setPen(self._current_pen())
                item.setBrush(self._brush(self._color(0, 102, 204, 46)))
            else:
                item.setPen(self._selected_pending_pen() if item.isSelected() else self._pending_pen())
                item.setBrush(self._brush(self._color(0, 102, 204, 42 if item.isSelected() else 24)))

    def _animate_pending_region(self, item) -> None:
        item.setOpacity(0.25)
        animation = self._animation_cls(self.view)
        animation.setStartValue(0.25)
        animation.setEndValue(1.0)
        animation.setDuration(160)
        animation.valueChanged.connect(lambda value, rect_item=item: rect_item.setOpacity(float(value)))
        animation.finished.connect(lambda anim=animation: self._animations.remove(anim) if anim in self._animations else None)
        self._animations.append(animation)
        animation.start()

    def _pending_item_at(self, view_pos):
        scene_pos = self.view.mapToScene(view_pos)
        for item in self.scene.items(scene_pos):
            if item in self._selection_items():
                return item
        return None

    def _clamped_pending_pos(self, item, next_pos) -> QPointF:
        image_rect = self.pixmap_item.boundingRect()
        item_rect = item.rect()
        min_x = image_rect.left() - item_rect.left()
        min_y = image_rect.top() - item_rect.top()
        max_x = image_rect.right() - item_rect.right()
        max_y = image_rect.bottom() - item_rect.bottom()
        return self._point_cls(
            min(max(next_pos.x(), min_x), max_x),
            min(max(next_pos.y(), min_y), max_y),
        )

    def _resize_pending_item(self, item, start_rect, delta, handle: str) -> None:
        rect = self._rect_from_handle(start_rect, delta, handle)
        rect = self._clamped_resize_rect(rect)
        item.setPos(rect.left(), rect.top())
        item.setRect(0, 0, rect.width(), rect.height())
        self._show_region_size_hint(rect)
        self._notify_pending_changed()

    def _rect_from_handle(self, rect, delta, handle: str):
        next_rect = self._rectf_cls(rect)
        if "left" in handle:
            next_rect.setLeft(next_rect.left() + delta.x())
        if "right" in handle:
            next_rect.setRight(next_rect.right() + delta.x())
        if "top" in handle:
            next_rect.setTop(next_rect.top() + delta.y())
        if "bottom" in handle:
            next_rect.setBottom(next_rect.bottom() + delta.y())
        return next_rect.normalized()

    def _clamped_resize_rect(self, rect):
        image_rect = self.pixmap_item.boundingRect()
        min_size = 4
        left = min(max(rect.left(), image_rect.left()), image_rect.right() - min_size)
        top = min(max(rect.top(), image_rect.top()), image_rect.bottom() - min_size)
        right = max(min(rect.right(), image_rect.right()), left + min_size)
        bottom = max(min(rect.bottom(), image_rect.bottom()), top + min_size)
        return self._rectf_cls(left, top, right - left, bottom - top)

    def _handle_threshold(self) -> float:
        scale = max(0.05, self.view.transform().m11())
        return max(4.0, 10.0 / scale)

    def _cursor_for_handle(self, handle: str | None):
        if handle in {"top-left", "bottom-right"}:
            return self._qt.SizeFDiagCursor
        if handle in {"top-right", "bottom-left"}:
            return self._qt.SizeBDiagCursor
        if handle in {"left", "right"}:
            return self._qt.SizeHorCursor
        if handle in {"top", "bottom"}:
            return self._qt.SizeVerCursor
        return self._qt.OpenHandCursor

    def _show_region_size_hint(self, rect) -> None:
        bbox = self._clamped_bbox(rect)
        if not bbox:
            self._hide_region_size_hint()
            return
        width = max(0, bbox[2] - bbox[0])
        height = max(0, bbox[3] - bbox[1])
        self.size_hint_label.setText(f"{width} x {height}px")
        self.size_hint_label.adjustSize()
        x = bbox[0]
        y = bbox[1] - 8
        point = self.view.mapFromScene(float(x), float(y))
        label_width = self.size_hint_label.width()
        label_height = self.size_hint_label.height()
        viewport = self.view.viewport().rect()
        next_x = min(max(6, point.x()), max(6, viewport.width() - label_width - 6))
        next_y = point.y() - label_height
        if next_y < 6:
            next_y = min(viewport.height() - label_height - 6, self.view.mapFromScene(float(bbox[0]), float(bbox[3])).y() + 6)
        self.size_hint_label.move(next_x, max(6, next_y))
        self.size_hint_label.show()

    def _hide_region_size_hint(self) -> None:
        self.size_hint_label.hide()

    def _notify_pending_changed(self) -> None:
        if self.on_pending_changed:
            self.on_pending_changed(self.pending_count())

    def _clamped_bbox(self, rect) -> list[int] | None:
        image_rect = self.pixmap_item.boundingRect()
        clipped = rect.intersected(image_rect)
        if clipped.width() < 4 or clipped.height() < 4:
            return None
        return [
            int(round(clipped.left())),
            int(round(clipped.top())),
            int(round(clipped.right())),
            int(round(clipped.bottom())),
        ]

    def _drag_rect(self, start, current):
        from PySide6.QtCore import QPointF, QRectF

        if not self.aspect_ratio:
            return QRectF(start, current).normalized()
        dx = current.x() - start.x()
        dy = current.y() - start.y()
        if abs(dx) < 1 or abs(dy) < 1:
            return QRectF(start, current).normalized()
        width = abs(dx)
        height = abs(dy)
        if width / height > self.aspect_ratio:
            width = height * self.aspect_ratio
        else:
            height = width / self.aspect_ratio
        end = QPointF(
            start.x() + width * (1 if dx >= 0 else -1),
            start.y() + height * (1 if dy >= 0 else -1),
        )
        return QRectF(start, end).normalized()

    def _notify_region_preview(self, rect) -> None:
        if not self.on_region_preview:
            return
        bbox = self._clamped_bbox(rect) if rect is not None else None
        self.on_region_preview(bbox)
