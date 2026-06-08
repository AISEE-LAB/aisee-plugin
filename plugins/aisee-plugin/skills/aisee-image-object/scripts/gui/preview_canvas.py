"""Preview canvas with selectable background modes."""

from __future__ import annotations


class PreviewCanvas:
    def __init__(self):
        from PySide6.QtCore import Qt
        from PySide6.QtWidgets import QGraphicsPixmapItem, QGraphicsScene, QGraphicsView

        self.view = QGraphicsView()
        self.view.setDragMode(QGraphicsView.ScrollHandDrag)
        self.view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.view.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.view.setAlignment(Qt.AlignCenter)
        self.scene = QGraphicsScene(self.view)
        self.view.setScene(self.scene)
        self.pixmap_item = QGraphicsPixmapItem()
        self.scene.addItem(self.pixmap_item)

    def widget(self):
        return self.view

    def set_pixmap(self, pixmap) -> None:
        self.pixmap_item.setPixmap(pixmap)
        self.scene.setSceneRect(self.pixmap_item.boundingRect())
        self.fit()

    def fit(self) -> None:
        if not self.pixmap_item.pixmap().isNull():
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
