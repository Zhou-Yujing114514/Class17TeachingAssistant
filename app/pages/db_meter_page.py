"""读书分贝测量仪页面。"""
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QProgressBar, QFrame)

from app.core.audio_meter import AudioMeter, band_of

MOTTO = "读书读得越响，分数考的越高"


class DbMeterPage(QWidget):
    # 请求进入/退出全屏（由主窗口接管窗口状态）
    fullscreen_requested = Signal(bool)

    def __init__(self, store, parent=None):
        super().__init__(parent)
        self.store = store
        self.meter = AudioMeter()
        self.meter.failed.connect(self._on_failed)
        self.peak = 0.0
        self.average = 0.0
        self._has_avg = False
        self.is_fullscreen = False

        self.root = QVBoxLayout(self)
        self.root.setContentsMargins(30, 24, 30, 24)
        self.root.setSpacing(16)

        # 标题行：标题 + 全屏按钮
        head = QHBoxLayout()
        self.title = QLabel("读书分贝测量仪")
        self.title.setObjectName("PageTitle")
        head.addWidget(self.title)
        head.addStretch()
        self.btn_fs = QPushButton("进入全屏")
        self.btn_fs.setObjectName("Ghost")
        self.btn_fs.setCursor(Qt.PointingHandCursor)
        self.btn_fs.clicked.connect(self.toggle_fullscreen)
        head.addWidget(self.btn_fs)
        self.root.addLayout(head)

        sub = QLabel("采集麦克风声音，实时显示朗读分贝，帮助把握读书音量")
        sub.setObjectName("PageSub")
        self.sub = sub
        self.root.addWidget(sub)

        # 大字格言
        self.motto = QLabel(MOTTO)
        self.motto.setObjectName("Motto")
        self.motto.setAlignment(Qt.AlignCenter)
        self.root.addWidget(self.motto)

        self.root.addSpacing(4)

        card = QFrame()
        card.setObjectName("SoftCard")
        card_lay = QVBoxLayout(card)
        card_lay.setContentsMargins(34, 30, 34, 28)
        card_lay.setSpacing(18)
        self.card = card
        self.card_lay = card_lay

        # 大数值
        num_row = QHBoxLayout()
        num_row.setAlignment(Qt.AlignCenter)
        self.lbl_num = QLabel("—")
        self.lbl_num.setStyleSheet(
            "font-size: 76px; font-weight: 800; color:#12A8E4;")
        unit = QLabel("dB")
        unit.setStyleSheet("font-size: 22px; color:#6B7684; font-weight:600;")
        unit.setContentsMargins(6, 34, 0, 0)
        self.unit = unit
        num_row.addWidget(self.lbl_num)
        num_row.addWidget(unit)
        card_lay.addLayout(num_row)

        self.lbl_band = QLabel("点击下方按钮开始")
        self.lbl_band.setAlignment(Qt.AlignCenter)
        self.lbl_band.setStyleSheet("font-size:15px; color:#485463; font-weight:600;")
        card_lay.addWidget(self.lbl_band)

        self.bar = QProgressBar()
        self.bar.setRange(30, 100)
        self.bar.setValue(30)
        self.bar.setFormat("")
        self.bar.setFixedHeight(16)
        card_lay.addWidget(self.bar)

        stat = QHBoxLayout()
        self.lbl_peak = QLabel("峰值 —")
        self.lbl_avg = QLabel("平均 —")
        for w in (self.lbl_peak, self.lbl_avg):
            w.setStyleSheet("color:#6B7684; font-size:13px;")
        self.lbl_peak.setAlignment(Qt.AlignCenter)
        self.lbl_avg.setAlignment(Qt.AlignCenter)
        stat.addWidget(self.lbl_peak)
        stat.addStretch()
        stat.addWidget(self.lbl_avg)
        card_lay.addLayout(stat)

        ctrl = QHBoxLayout()
        ctrl.setAlignment(Qt.AlignCenter)
        self.btn = QPushButton("开始测量")
        self.btn.setObjectName("Primary")
        self.btn.setFixedWidth(160)
        self.btn.setCursor(Qt.PointingHandCursor)
        self.btn.clicked.connect(self.toggle)
        ctrl.addWidget(self.btn)
        card_lay.addLayout(ctrl)

        hint = QLabel("* 数值为基于麦克风电平的估算分贝，不同设备略有差异，"
                      "可在「设置」中调整校准偏移。")
        hint.setObjectName("Hint")
        hint.setWordWrap(True)
        hint.setAlignment(Qt.AlignCenter)
        self.hint = hint
        card_lay.addWidget(hint)

        self.root.addWidget(card)
        self.root.addStretch()

        self.timer = QTimer(self)
        self.timer.setInterval(40)
        self.timer.timeout.connect(self._tick)

        # Esc 退出全屏（页面级，主窗口也有一份兜底）
        self.esc = QShortcut(QKeySequence(Qt.Key_Escape), self)
        self.esc.activated.connect(lambda: self.set_fullscreen(False))

    # ---------- 全屏 ----------
    def toggle_fullscreen(self):
        self.set_fullscreen(not self.is_fullscreen)

    def set_fullscreen(self, on: bool):
        if on == self.is_fullscreen:
            return
        self.is_fullscreen = on
        if on:
            self.root.setContentsMargins(60, 40, 60, 40)
            self.root.setSpacing(26)
            self.title.setStyleSheet("font-size:32px; font-weight:700; color:#18222e;")
            self.card_lay.setContentsMargins(60, 50, 60, 44)
            self.card_lay.setSpacing(34)
            self.motto.setStyleSheet(
                "font-size: 46px; font-weight: 800; color:#0E93C9;"
                "letter-spacing:2px; padding:10px 0;")
            self.lbl_num.setStyleSheet(
                "font-size: 190px; font-weight: 800; color:#12A8E4;")
            self.unit.setStyleSheet(
                "font-size: 46px; color:#6B7684; font-weight:600;")
            self.unit.setContentsMargins(12, 92, 0, 0)
            self.bar.setFixedHeight(30)
            self.btn.setFixedWidth(240)
            self.btn.setStyleSheet("padding:14px 22px; font-size:18px;")
            self.lbl_peak.setStyleSheet("color:#6B7684; font-size:20px;")
            self.lbl_avg.setStyleSheet("color:#6B7684; font-size:20px;")
            self.sub.hide()
            self.hint.hide()
            self.btn_fs.setText("退出全屏 (Esc)")
            self.btn_fs.setStyleSheet("padding:10px 20px; font-size:15px;")
        else:
            self.root.setContentsMargins(30, 24, 30, 24)
            self.root.setSpacing(16)
            self.title.setStyleSheet("")
            self.card_lay.setContentsMargins(34, 30, 34, 28)
            self.card_lay.setSpacing(18)
            self.motto.setStyleSheet("")
            self.lbl_num.setStyleSheet(
                "font-size: 76px; font-weight: 800; color:#12A8E4;")
            self.unit.setStyleSheet(
                "font-size: 22px; color:#6B7684; font-weight:600;")
            self.unit.setContentsMargins(6, 34, 0, 0)
            self.bar.setFixedHeight(16)
            self.btn.setFixedWidth(160)
            self.btn.setStyleSheet("")
            self.lbl_peak.setStyleSheet("color:#6B7684; font-size:13px;")
            self.lbl_avg.setStyleSheet("color:#6B7684; font-size:13px;")
            self.sub.show()
            self.hint.show()
            self.btn_fs.setText("进入全屏")
            self.btn_fs.setStyleSheet("")
        self.fullscreen_requested.emit(on)

    # ---------- 测量 ----------
    def toggle(self):
        if self.meter.running:
            self._stop()
        else:
            if self.meter.start():
                self.peak = 0.0
                self._has_avg = False
                self.btn.setText("停止测量")
                self.timer.start()

    def _stop(self):
        self.meter.stop()
        self.timer.stop()
        self.btn.setText("开始测量")
        self.lbl_num.setText("—")
        self.lbl_band.setText("已停止")
        self.bar.setValue(30)

    def _tick(self):
        db = self.meter.estimated_db(self.store.settings["db_offset"])
        self.lbl_num.setText(f"{db:.0f}")
        # 峰值保持并缓慢回落
        self.peak = max(self.peak - 0.06, db)
        if not self._has_avg:
            self.average = db
            self._has_avg = True
        else:
            self.average = 0.97 * self.average + 0.03 * db
        self.lbl_peak.setText(f"峰值 {self.peak:.0f} dB")
        self.lbl_avg.setText(f"平均 {self.average:.0f} dB")
        self.bar.setValue(int(max(30, min(100, db))))
        band = band_of(db)
        self.lbl_band.setText(band)
        color = {"很安静": "#94a3b8", "轻声": "#38bdf8", "朗读适宜": "#22c55e",
                 "偏响": "#f59e0b", "过响": "#ef4444"}.get(band, "#485463")
        big = self.is_fullscreen
        self.lbl_band.setStyleSheet(
            f"font-size:{'32px' if big else '15px'}; color:{color}; font-weight:700;")

    def _on_failed(self, msg: str):
        self._stop()
        self.lbl_band.setText("麦克风不可用")
        self.lbl_num.setText("—")

    def shutdown(self):
        self._stop()
