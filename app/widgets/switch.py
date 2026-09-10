"""简约 iOS 风格开关。"""
from PySide6.QtCore import Signal, Qt, QPropertyAnimation, Property
from PySide6.QtGui import QPainter, QColor
from PySide6.QtWidgets import QWidget


class Switch(QWidget):
    toggled = Signal(bool)

    def __init__(self, checked=False, parent=None):
        super().__init__(parent)
        self.setFixedSize(46, 26)
        self.setCursor(Qt.PointingHandCursor)
        self._checked = checked
        self._x = 24.0 if checked else 3.0
        self._anim = QPropertyAnimation(self, b"knob_x", self)
        self._anim.setDuration(140)

    def isChecked(self):
        return self._checked

    def setChecked(self, value: bool, emit=False):
        value = bool(value)
        if value == self._checked:
            return
        self._checked = value
        self._anim.stop()
        self._anim.setStartValue(self._x)
        self._anim.setEndValue(24.0 if value else 3.0)
        self._anim.start()
        if emit:
            self.toggled.emit(value)

    def get_knob_x(self):
        return self._x

    def set_knob_x(self, v):
        self._x = float(v)
        self.update()

    knob_x = Property(float, get_knob_x, set_knob_x)

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.setChecked(not self._checked, emit=True)

    def paintEvent(self, _e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        track = QColor("#12A8E4") if self._checked else QColor("#d4dbe3")
        p.setPen(Qt.NoPen)
        p.setBrush(track)
        p.drawRoundedRect(0, 0, self.width(), self.height(), 13, 13)
        p.setBrush(QColor("#ffffff"))
        p.drawEllipse(int(self._x), 3, 20, 20)
