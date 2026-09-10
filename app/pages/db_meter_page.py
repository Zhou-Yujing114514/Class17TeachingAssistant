"""读书分贝测量仪页面。"""
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QProgressBar, QFrame)

from app.core.audio_meter import AudioMeter, band_of


class DbMeterPage(QWidget):
    def __init__(self, store, parent=None):
        super().__init__(parent)
        self.store = store
        self.meter = AudioMeter()
        self.meter.failed.connect(self._on_failed)
        self.peak = 0.0
        self.average = 0.0
        self._has_avg = False

        root = QVBoxLayout(self)
        root.setContentsMargins(30, 24, 30, 24)
        root.setSpacing(16)

        title = QLabel("读书分贝测量仪")
        title.setObjectName("PageTitle")
        sub = QLabel("采集麦克风声音，实时显示朗读分贝，帮助把握读书音量")
        sub.setObjectName("PageSub")
        root.addWidget(title)
        root.addWidget(sub)

        card = QFrame()
        card.setObjectName("SoftCard")
        card_lay = QVBoxLayout(card)
        card_lay.setContentsMargins(34, 30, 34, 28)
        card_lay.setSpacing(18)

        # 大数值
        num_row = QHBoxLayout()
        num_row.setAlignment(Qt.AlignCenter)
        self.lbl_num = QLabel("—")
        self.lbl_num.setStyleSheet(
            "font-size: 76px; font-weight: 800; color:#12A8E4;")
        unit = QLabel("dB")
        unit.setStyleSheet("font-size: 22px; color:#6B7684; font-weight:600;")
        unit.setContentsMargins(6, 34, 0, 0)
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
        stat.addWidget(self.lbl_peak)
        stat.addStretch()
        stat.addWidget(self.lbl_avg)
        card_lay.addLayout(stat)

        ctrl = QHBoxLayout()
        ctrl.setAlignment(Qt.AlignCenter)
        self.btn = QPushButton("开始测量")
        self.btn.setObjectName("Primary")
        self.btn.setFixedWidth(160)
        self.btn.clicked.connect(self.toggle)
        ctrl.addWidget(self.btn)
        card_lay.addLayout(ctrl)

        hint = QLabel("* 数值为基于麦克风电平的估算分贝，不同设备略有差异，"
                      "可在「设置」中调整校准偏移。")
        hint.setObjectName("Hint")
        hint.setWordWrap(True)
        card_lay.addWidget(hint)

        root.addWidget(card)
        root.addStretch()

        self.timer = QTimer(self)
        self.timer.setInterval(40)
        self.timer.timeout.connect(self._tick)

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
        self.lbl_band.setStyleSheet(
            f"font-size:15px; color:{color}; font-weight:700;")

    def _on_failed(self, msg: str):
        self._stop()
        self.lbl_band.setText("麦克风不可用")
        self.lbl_num.setText("—")

    def shutdown(self):
        self._stop()
