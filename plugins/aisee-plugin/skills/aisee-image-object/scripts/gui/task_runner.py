"""Background task runner for GUI batch operations."""

from __future__ import annotations

from traceback import format_exc
from typing import Callable

from PySide6.QtCore import QObject, Signal, Slot


class BatchWorker(QObject):
    """Run sequential image-processing tasks off the GUI thread."""

    progress = Signal(int, int, str)
    finished = Signal(object)

    def __init__(self, tasks: list[dict]):
        super().__init__()
        self.tasks = tasks

    @Slot()
    def run(self) -> None:
        total = len(self.tasks)
        results = []
        for index, task in enumerate(self.tasks, start=1):
            label = str(task.get("label") or f"任务 {index}")
            self.progress.emit(index - 1, total, f"正在处理 {index}/{total}：{label}")
            try:
                runner: Callable[[], dict] = task["run"]
                result = runner()
            except Exception as exc:  # pragma: no cover - defensive UI safety
                result = {
                    "status": "failed",
                    "label": label,
                    "error": str(exc),
                    "traceback": format_exc(),
                }
            results.append(result)
            self.progress.emit(index, total, f"已完成 {index}/{total}：{label}")
        self.finished.emit(results)


class BatchUiBridge(QObject):
    """Deliver worker signals to the GUI thread before touching widgets."""

    def __init__(self, owner):
        super().__init__()
        self.owner = owner

    @Slot(int, int, str)
    def handle_progress(self, done: int, total: int, label: str) -> None:
        self.owner._handle_task_progress(done, total, label)

    @Slot(object)
    def handle_finished(self, results: object) -> None:
        self.owner._finish_background_batch(results)
