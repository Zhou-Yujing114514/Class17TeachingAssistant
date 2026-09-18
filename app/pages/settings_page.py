"""设置页：开机自启、分贝校准、桌面挂件外观。"""
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QSpinBox, QDoubleSpinBox, QComboBox,
                               QPushButton, QFrame, QColorDialog, QScrollArea)

from app.widgets.switch import Switch
from app.core import autostart
from app import __version__


class _Section(QFrame):
    def __init__(self, title: str):
        super().__init__()
        self.setObjectName("Card")
        self.lay = QVBoxLayout(self)
        self.lay.setContentsMargins(22, 18, 22, 18)
        self.lay.setSpacing(12)
        t = QLabel(title)
        t.setStyleSheet("font-size:15px; font-weight:700;")
        self.lay.addWidget(t)

    def row(self, text: str, widget, hint: str = ""):
        h = QHBoxLayout()
        lab = QLabel(text)
        lab.setMinimumWidth(150)
        h.addWidget(lab)
        h.addWidget(widget)
        h.addStretch()
        self.lay.addLayout(h)
        if hint:
            hh = QLabel(hint)
            hh.setObjectName("Hint")
            hh.setWordWrap(True)
            self.lay.addWidget(hh)


class SettingsPage(QWidget):
    def __init__(self, store, manager, parent=None):
        super().__init__(parent)
        self.store = store
        self.manager = manager
        s = store.settings

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        inner = QWidget()
        root = QVBoxLayout(inner)
        root.setContentsMargins(30, 24, 30, 24)
        root.setSpacing(14)
        title = QLabel("设置")
        title.setObjectName("PageTitle")
        root.addWidget(title)

        # 通用
        sec1 = _Section("通用")
        self.sw_auto = Switch(autostart.is_enabled())
        self.sw_auto.toggled.connect(self._toggle_autostart)
        sec1.row("开机自动启动", self.sw_auto,
                 "开启后开机会自动后台运行，并恢复贴在桌面上的挂件")
        root.addWidget(sec1)

        # 分贝
        sec2 = _Section("读书分贝测量仪")
        self.sp_offset = QSpinBox()
        self.sp_offset.setRange(60, 130)
        self.sp_offset.setSuffix(" dB")
        self.sp_offset.setValue(int(s["db_offset"]))
        self.sp_offset.valueChanged.connect(
            lambda v: self.store.set_setting("db_offset", int(v)))
        sec2.row("校准偏移", self.sp_offset,
                 "估算分贝 = 麦克风电平 + 偏移；整体偏小就调大，偏大就调小")
        root.addWidget(sec2)

        # 桌面挂件
        sec3 = _Section("桌面挂件")
        self.sp_font = QSpinBox()
        self.sp_font.setRange(44, 120)
        self.sp_font.setSingleStep(2)
        self.sp_font.setSuffix(" px")
        self.sp_font.setValue(max(44, int(s["widget_font_size"])))
        self.sp_font.valueChanged.connect(
            lambda v: self.store.set_setting("widget_font_size", int(v)))
        sec3.row("文字字号", self.sp_font,
                 "桌面挂件数字行字号，最小 44px，可继续调大；名称行按比例缩放")

        self.cmb_weight = QComboBox()
        self.cmb_weight.addItems(["细（推荐）", "标准", "粗"])
        self.cmb_weight.setCurrentIndex(int(s.get("widget_font_weight", 0)))
        self.cmb_weight.currentIndexChanged.connect(
            lambda v: self.store.set_setting("widget_font_weight", int(v)))
        sec3.row("字体粗细", self.cmb_weight,
                 "霓虹挂件文字粗细：细更清爽、光晕层次清晰；粗更有力量感")

        self.sp_neon = QDoubleSpinBox()
        self.sp_neon.setRange(1.0, 20.0)
        self.sp_neon.setSingleStep(0.5)
        self.sp_neon.setSuffix(" 秒")
        self.sp_neon.setValue(float(s["neon_period_s"]))
        self.sp_neon.valueChanged.connect(
            lambda v: self.store.set_setting("neon_period_s", float(v)))
        sec3.row("霓虹流动周期", self.sp_neon, "颜色流转一圈所需时间，数值越大越慢")

        self.sw_outline = Switch(bool(s["dark_outline"]))
        self.sw_outline.toggled.connect(
            lambda v: self.store.set_setting("dark_outline", bool(v)))
        sec3.row("浅色壁纸衬底描边", self.sw_outline,
                 "在白色等浅色壁纸上加一圈淡暗描边，保证文字清晰")

        self.cmb_mode = QComboBox()
        self.cmb_mode.addItems(["动态霓虹", "自定义固定颜色"])
        self.cmb_mode.setCurrentIndex(0 if s["default_color_mode"] == "neon" else 1)
        self.cmb_mode.currentIndexChanged.connect(self._mode_changed)
        sec3.row("默认颜色方案", self.cmb_mode)

        color_row = QHBoxLayout()
        self.btn_color = QPushButton("选择默认颜色")
        self.btn_color.setObjectName("Ghost")
        self.swatch = QLabel()
        self.swatch.setFixedSize(26, 26)
        self._refresh_swatch(s["default_color"])
        self.btn_color.clicked.connect(self._pick_default_color)
        color_row.addWidget(self.btn_color)
        color_row.addWidget(self.swatch)
        color_row.addStretch()
        sec3.lay.addLayout(color_row)

        btn_apply = QPushButton("应用颜色到全部挂件")
        btn_apply.setObjectName("Ghost")
        btn_apply.clicked.connect(self._apply_all)
        sec3.lay.addWidget(btn_apply)
        root.addWidget(sec3)

        # 关于
        sec4 = _Section("关于")
        about = QLabel("高二17班教学助手\n"
                       f"版本 v{__version__}　为课堂教学打造的小工具集")
        about.setObjectName("Hint")
        sec4.lay.addWidget(about)
        root.addWidget(sec4)
        root.addStretch()

        scroll.setWidget(inner)
        outer.addWidget(scroll)

    def _toggle_autostart(self, on: bool):
        ok = autostart.set_enabled(on)
        if not ok and on:
            self.sw_auto.setChecked(False)

    def _mode_changed(self, idx):
        self.store.set_setting("default_color_mode",
                               "neon" if idx == 0 else "custom")

    def _pick_default_color(self):
        col = QColorDialog.getColor(QColor(self.store.settings["default_color"]),
                                   self, "选择默认颜色")
        if col.isValid():
            name = col.name().upper()
            self._refresh_swatch(name)
            self.store.set_setting("default_color", name)

    def _refresh_swatch(self, hex_color):
        self.swatch.setStyleSheet(
            f"background:{hex_color}; border:1px solid #d0d7de; border-radius:6px;")

    def _apply_all(self):
        mode = self.store.settings["default_color_mode"]
        color = self.store.settings["default_color"]
        for cd in self.store.countdowns:
            self.store.update_card(cd["id"], color_mode=mode, color=color)
