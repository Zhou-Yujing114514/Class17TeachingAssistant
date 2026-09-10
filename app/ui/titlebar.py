"""自研圆角窗口标题栏（无最大化，仅最小化/关闭，整条可拖动）。"""
from PySide6.QtCore import Qt, Signal, QPoint
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from app.core.paths import resource_path, DISPLAY_NAME


class WinButton(QPushButton):
    def __init__(self, text: str, obj_name: str = "WinBtn"):
        super().__init__(text)
        self.setObjectName(obj_name)
        self.setFixedSize(42, 28)
        self.setCursor(Qt.ArrowCursor)


class TitleBar(QWidget):
    minimize_requested = Signal()
    close_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("TitleBar")
        self.setFixedHeight(44)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(14, 0, 8, 0)
        lay.setSpacing(8)

        icon = QLabel()
        icon.setFixedSize(20, 20)
        ico = QIcon(resource_path("assets/app.ico"))
        icon.setPixmap(ico.pixmap(20, 20))
        title = QLabel(DISPLAY_NAME)
        title.setObjectName("TitleText")

        self.btn_min = WinButton("—")
        self.btn_close = WinButton("✕", "BtnClose")
        self.btn_min.clicked.connect(self.minimize_requested.emit)
        self.btn_close.clicked.connect(self.close_requested.emit)

        lay.addWidget(icon)
        lay.addWidget(title)
        lay.addStretch()
        lay.addWidget(self.btn_min)
        lay.addSpacing(4)
        lay.addWidget(self.btn_close)

        self._press_pos = None

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self._press_pos = e.globalPosition().toPoint()

    def mouseMoveEvent(self, e):
        if self._press_pos is not None and e.buttons() & Qt.LeftButton:
            win = self.window()
            delta = e.globalPosition().toPoint() - self._press_pos
            win.move(win.pos() + delta)
            self._press_pos = e.globalPosition().toPoint()

    def mouseReleaseEvent(self, _e):
        self._press_pos = None

    def mouseDoubleClickEvent(self, _e):
        # 故意留空：不提供最大化
        return
