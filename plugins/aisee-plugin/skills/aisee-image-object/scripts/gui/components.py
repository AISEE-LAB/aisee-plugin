"""Reusable GUI components for the image-object workbench."""

from __future__ import annotations


class FlowLayout:
    """A lightweight wrapping layout for compact toolbar controls."""

    def __new__(cls, *args, **kwargs):
        from PySide6.QtCore import QPoint, QRect, QSize, Qt
        from PySide6.QtWidgets import QLayout

        class _FlowLayout(QLayout):
            def __init__(
                self,
                parent=None,
                *,
                margins: tuple[int, int, int, int] = (0, 0, 0, 0),
                spacing: int = 8,
            ):
                super().__init__(parent)
                self._items = []
                self.setContentsMargins(*margins)
                self.setSpacing(spacing)

            def __del__(self):
                while self.count():
                    self.takeAt(0)

            def addItem(self, item):
                self._items.append(item)

            def count(self):
                return len(self._items)

            def itemAt(self, index):
                if 0 <= index < len(self._items):
                    return self._items[index]
                return None

            def takeAt(self, index):
                if 0 <= index < len(self._items):
                    return self._items.pop(index)
                return None

            def expandingDirections(self):
                return Qt.Orientations(Qt.Orientation(0))

            def hasHeightForWidth(self):
                return True

            def heightForWidth(self, width):
                return self._do_layout(QRect(0, 0, width, 0), test_only=True)

            def setGeometry(self, rect):
                super().setGeometry(rect)
                self._do_layout(rect, test_only=False)

            def sizeHint(self):
                return self.minimumSize()

            def minimumSize(self):
                size = QSize()
                for item in self._visible_items():
                    size = size.expandedTo(item.minimumSize())
                margins = self.contentsMargins()
                size += QSize(margins.left() + margins.right(), margins.top() + margins.bottom())
                return size

            def _visible_items(self):
                for item in self._items:
                    widget = item.widget()
                    if widget is not None and not widget.isVisible():
                        continue
                    yield item

            def _do_layout(self, rect, *, test_only):
                margins = self.contentsMargins()
                effective = rect.adjusted(margins.left(), margins.top(), -margins.right(), -margins.bottom())
                x = effective.x()
                y = effective.y()
                line_height = 0
                spacing = self.spacing()

                for item in self._visible_items():
                    hint = item.sizeHint()
                    next_x = x + hint.width() + spacing
                    if line_height > 0 and next_x - spacing > effective.right():
                        x = effective.x()
                        y = y + line_height + spacing
                        next_x = x + hint.width() + spacing
                        line_height = 0
                    if not test_only:
                        item.setGeometry(QRect(QPoint(x, y), hint))
                    x = next_x
                    line_height = max(line_height, hint.height())

                return y + line_height - rect.y() + margins.bottom()

        return _FlowLayout(*args, **kwargs)


def create_section_header(eyebrow: str, subtitle: str, trailing_widget=None):
    from PySide6.QtWidgets import QHBoxLayout, QLabel

    layout = QHBoxLayout()
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(10)
    title = QLabel(eyebrow)
    title.setProperty("role", "eyebrow")
    hint = QLabel(subtitle)
    hint.setProperty("role", "muted")
    layout.addWidget(title)
    layout.addWidget(hint)
    layout.addStretch(1)
    if trailing_widget is not None:
        layout.addWidget(trailing_widget)
    return layout


def create_panel(
    *,
    object_name: str = "SurfacePanel",
    margins: tuple[int, int, int, int] = (12, 10, 12, 10),
    spacing: int = 8,
    max_height: int | None = None,
):
    from PySide6.QtWidgets import QFrame, QVBoxLayout

    frame = QFrame()
    frame.setObjectName(object_name)
    if max_height:
        frame.setMaximumHeight(max_height)
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(*margins)
    layout.setSpacing(spacing)
    return frame, layout


def create_control_shelf(
    *,
    object_name: str = "ControlShelf",
    margins: tuple[int, int, int, int] = (10, 8, 10, 8),
    spacing: int = 8,
):
    from PySide6.QtWidgets import QFrame, QHBoxLayout

    frame = QFrame()
    frame.setObjectName(object_name)
    layout = QHBoxLayout(frame)
    layout.setContentsMargins(*margins)
    layout.setSpacing(spacing)
    return frame, layout


def create_flow_shelf(
    *,
    object_name: str = "ControlShelf",
    margins: tuple[int, int, int, int] = (10, 8, 10, 8),
    spacing: int = 8,
):
    from PySide6.QtWidgets import QFrame

    frame = QFrame()
    frame.setObjectName(object_name)
    layout = FlowLayout(frame, margins=margins, spacing=spacing)
    return frame, layout


def create_command_bar(eyebrow: str, hint: str):
    from PySide6.QtWidgets import QLabel

    frame, layout = create_control_shelf(object_name="ActionStrip")
    title = QLabel(eyebrow)
    title.setProperty("role", "eyebrow")
    context = QLabel(hint)
    context.setProperty("role", "muted")
    layout.addWidget(title)
    layout.addWidget(context)
    layout.addStretch(1)
    return frame, layout, context


def create_form_layout():
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QFormLayout

    form = QFormLayout()
    form.setContentsMargins(0, 0, 0, 0)
    form.setHorizontalSpacing(14)
    form.setVerticalSpacing(12)
    form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
    form.setFormAlignment(Qt.AlignTop)
    return form


def create_button(text: str, *, variant: str = "secondary"):
    from PySide6.QtWidgets import QPushButton

    button = QPushButton(text)
    button.setProperty("variant", variant)
    return button


def restyle_button(button, variant: str) -> None:
    button.setProperty("variant", variant)
    button.style().unpolish(button)
    button.style().polish(button)


def set_button_variant(button, variant: str) -> None:
    if button.property("variant") == variant:
        return
    restyle_button(button, variant)


def create_dialog_buttons(
    dialog,
    *,
    ok_text: str = "确认",
    cancel_text: str = "取消",
    include_cancel: bool = True,
):
    from PySide6.QtWidgets import QDialogButtonBox

    flags = QDialogButtonBox.Ok | QDialogButtonBox.Cancel if include_cancel else QDialogButtonBox.Ok
    buttons = QDialogButtonBox(flags)
    ok_button = buttons.button(QDialogButtonBox.Ok)
    ok_button.setText(ok_text)
    restyle_button(ok_button, "primary")
    if include_cancel:
        cancel_button = buttons.button(QDialogButtonBox.Cancel)
        cancel_button.setText(cancel_text)
        restyle_button(cancel_button, "secondary")
    buttons.accepted.connect(dialog.accept)
    buttons.rejected.connect(dialog.reject)
    return buttons


def create_dialog_shell(
    dialog,
    *,
    eyebrow: str,
    title: str,
    subtitle: str,
    width: int = 560,
    height: int | None = None,
):
    from PySide6.QtWidgets import QLabel, QVBoxLayout

    dialog.setWindowTitle(title)
    dialog.resize(width, height or 420)

    root = QVBoxLayout(dialog)
    root.setContentsMargins(24, 24, 24, 24)
    root.setSpacing(16)

    eyebrow_label = QLabel(eyebrow)
    eyebrow_label.setProperty("role", "eyebrow")
    title_label = QLabel(title)
    title_label.setProperty("role", "title")
    subtitle_label = QLabel(subtitle)
    subtitle_label.setProperty("role", "muted")
    subtitle_label.setWordWrap(True)
    root.addWidget(eyebrow_label)
    root.addWidget(title_label)
    root.addWidget(subtitle_label)

    panel, panel_layout = create_panel(
        object_name="DialogPanel",
        margins=(14, 12, 14, 12),
        spacing=10,
    )
    root.addWidget(panel)
    return root, panel_layout


def create_dialog_preview():
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QLabel

    preview = QLabel()
    preview.setObjectName("DialogPreview")
    preview.setAlignment(Qt.AlignCenter)
    preview.setMinimumHeight(220)
    return preview
