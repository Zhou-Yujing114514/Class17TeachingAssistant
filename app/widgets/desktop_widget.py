"""桌面嵌入挂件：无底透明、动态霓虹/自定义颜色文字，可拖动、右键设置。"""
import math
import datetime as dt

from PySide6.QtCore import (Qt, QObject, Signal, QTimer, QVariantAnimation,
                            QPoint, QRectF)
from PySide6.QtGui import QFont, QFontMetrics, QPainterPath, QPen, QColor, QPainter
from PySide6.QtWidgets import QWidget, QMenu, QColorDialog

from app.core import desktop_embed
from app.core.countdown_util import parse_target, remaining

PAD = 16  # 内边距下限（实际按字号放大，给霓虹光晕留足空间）


class DesktopCountdownWidget(QWidget):
    detach_requested = Signal(str)
    precision_changed = Signal(str, str)
    color_changed = Signal(str, str, str)
    position_saved = Signal(str, int, int)

    def __init__(self, cd: dict, settings: dict, parent=None):
        flags = (Qt.FramelessWindowHint | Qt.WindowStaysOnBottomHint
                 | Qt.Tool | Qt.WindowDoesNotAcceptFocus)
        super().__init__(None, flags)
        self.cd = cd
        self.settings = settings
        self._name = cd["name"]
        self._value = ""
        self._arrived = False
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFocusPolicy(Qt.NoFocus)
        self.setContextMenuPolicy(Qt.DefaultContextMenu)

        # 霓虹色相流动
        self.hue = 190
        self.anim = QVariantAnimation(self)
        self.anim.setStartValue(0)
        self.anim.setEndValue(360)
        self.anim.setLoopCount(-1)
        self.anim.valueChanged.connect(self._on_hue)
        self.apply_settings(settings)
        self.anim.start()

        self._drag_offset = None
        self.refresh_text()

    # ---------- 外观 ----------
    def apply_settings(self, settings: dict):
        self.settings = settings
        self.anim.setDuration(int(float(settings.get("neon_period_s", 7.0)) * 1000))
        # 挂件数字行字号：最小 44px，可继续调大
        self._value_size = max(44, int(settings.get("widget_font_size", 44)))
        self._rebuild_paths()

    def _fonts(self):
        f_name = QFont("Microsoft YaHei UI")
        f_name.setPixelSize(max(26, int(self._value_size * 0.6)))
        f_name.setBold(True)
        f_val = QFont("Microsoft YaHei UI")
        f_val.setPixelSize(self._value_size)
        f_val.setBold(True)
        return f_name, f_val

    def _on_hue(self, v):
        self.hue = int(v)
        self.update()

    def update_card(self, cd: dict):
        self.cd = cd
        self.refresh_text()

    def refresh_text(self):
        target = parse_target(self.cd["target"])
        total, arrived, d, h, m, s = remaining(target)
        self._arrived = arrived
        raw_name = self.cd["name"]
        if arrived:
            # 已到：名称行只显示事件名，数值行显示「已到」
            self._name = raw_name
            self._value = "已到"
        else:
            self._name = f"距离{raw_name}还有："
            if self.cd.get("precision") == "day":
                self._value = f"{math.ceil(total / 86400)} 天"
            else:
                self._value = f"{d}天 {h:02d}时 {m:02d}分 {s:02d}秒"
        self._rebuild_paths()

    def _rebuild_paths(self):
        f_name, f_val = self._fonts()
        fm_name, fm_val = QFontMetrics(f_name), QFontMetrics(f_val)
        name_text = self._name
        val_text = self._value if self._value else "0"
        self._p_name = QPainterPath()
        self._p_name.addText(0, 0, f_name, name_text)
        self._p_val = QPainterPath()
        self._p_val.addText(0, 0, f_val, val_text)

        # 用字体度量计算尺寸（QPainterPath.boundingRect 不含霓虹光晕，会裁边）
        name_w = fm_name.horizontalAdvance(name_text)
        val_w = fm_val.horizontalAdvance(val_text)
        name_h = fm_name.height()
        val_h = fm_val.height()
        # 光晕最粗 0.30em，半边 0.15em；内边距按字号放大并留抗锯齿余量
        self._m = max(PAD, int(self._value_size * 0.24) + 3)
        self._gap = max(8, int(self._value_size * 0.22))
        self._text_w = max(name_w, val_w)
        w = self._text_w + self._m * 2
        h = name_h + self._gap + val_h + self._m * 2

        # 绘制原点（文字基线位置），两行各自水平居中
        self._x_name = self._m + (self._text_w - name_w) / 2
        self._x_val = self._m + (self._text_w - val_w) / 2
        self._y_name = self._m + fm_name.ascent()
        self._y_val = self._m + name_h + self._gap + fm_val.ascent()

        old_right = self.x() + self.width()
        old_bottom = self.y() + self.height()
        self.setFixedSize(int(w), int(h))
        # 右锚定：数字变宽时向左生长，避免右上角跳动
        if self.isVisible():
            self.move(int(old_right - w), int(old_bottom - h))
        self.update()

    def _current_color(self) -> QColor:
        if self.cd.get("color_mode") == "custom":
            c = QColor(self.cd.get("color", "#00E5FF"))
            return c if c.isValid() else QColor("#00E5FF")
        return QColor.fromHsv(self.hue % 360, 235, 255)

    def paintEvent(self, _e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.TextAntialiasing)
        # 名称行（白色）与数值行（霓虹色），各自水平居中
        p.save()
        p.translate(self._x_name, self._y_name)
        if self.settings.get("dark_outline", True):
            p.setPen(QPen(QColor(0, 0, 0, 90), 1.4))
            p.setBrush(Qt.NoBrush)
            p.drawPath(self._p_name)
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(255, 255, 255, 235))
        p.drawPath(self._p_name)
        p.restore()

        p.save()
        p.translate(self._x_val, self._y_val)
        color = self._current_color()
        # 霓虹光晕：两层粗描边
        for width, alpha in ((self._value_size * 0.30, 70),
                             (self._value_size * 0.14, 150)):
            glow = QColor(color)
            glow.setAlpha(alpha)
            pen = QPen(glow, width)
            pen.setJoinStyle(Qt.RoundJoin)
            p.setPen(pen)
            p.setBrush(Qt.NoBrush)
            p.drawPath(self._p_val)
        if self.settings.get("dark_outline", True):
            p.setPen(QPen(QColor(0, 0, 0, 80), 1.1))
            p.drawPath(self._p_val)
        p.setPen(Qt.NoPen)
        p.setBrush(color)
        p.drawPath(self._p_val)
        p.restore()

    # ---------- 拖动 ----------
    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self._drag_offset = e.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, e):
        if self._drag_offset is not None and e.buttons() & Qt.LeftButton:
            self.move(e.globalPosition().toPoint() - self._drag_offset)

    def mouseReleaseEvent(self, e):
        if self._drag_offset is not None:
            self._drag_offset = None
            self.position_saved.emit(self.cd["id"], self.x(), self.y())

    # ---------- 右键菜单 ----------
    def contextMenuEvent(self, e):
        menu = QMenu(self)
        act_day = menu.addAction("精确到天")
        act_sec = menu.addAction("精确到秒")
        act_day.setCheckable(True)
        act_sec.setCheckable(True)
        (act_day if self.cd.get("precision") == "day" else act_sec).setChecked(True)
        menu.addSeparator()
        act_neon = menu.addAction("颜色：动态霓虹")
        act_custom = menu.addAction("颜色：自定义…")
        act_neon.setCheckable(True)
        act_neon.setChecked(self.cd.get("color_mode") == "neon")
        menu.addSeparator()
        act_back = menu.addAction("收回挂件")
        chosen = menu.exec(e.globalPos())
        if chosen is act_day:
            self.precision_changed.emit(self.cd["id"], "day")
        elif chosen is act_sec:
            self.precision_changed.emit(self.cd["id"], "second")
        elif chosen is act_neon:
            self.color_changed.emit(self.cd["id"], "neon", self.cd.get("color", "#00E5FF"))
        elif chosen is act_custom:
            col = QColorDialog.getColor(QColor(self.cd.get("color", "#00E5FF")),
                                       self, "选择挂件文字颜色")
            if col.isValid():
                self.color_changed.emit(self.cd["id"], "custom", col.name().upper())
        elif chosen is act_back:
            self.detach_requested.emit(self.cd["id"])


class WidgetManager(QObject):
    widgets_changed = Signal()

    def __init__(self, store):
        super().__init__()
        self.store = store
        self.widgets = {}
        self.parents = {}
        self.tick = QTimer(self)
        self.tick.setInterval(1000)
        self.tick.timeout.connect(self._tick_all)
        self.tick.start()
        # 资源管理器重启后自动重新贴入壁纸层
        self.guard = QTimer(self)
        self.guard.setInterval(4000)
        self.guard.timeout.connect(self._guard_reattach)
        self.guard.start()
        store.countdowns_changed.connect(self._on_data_changed)
        store.settings_changed.connect(self._on_settings_changed)

    # ---------- 挂载 / 收回 ----------
    def attach(self, cd: dict, default_index: int = 0):
        if cd["id"] in self.widgets:
            return
        w = DesktopCountdownWidget(cd, self.store.settings)
        w.detach_requested.connect(self.detach)
        w.precision_changed.connect(
            lambda cid, prec: self.store.update_card(cid, precision=prec))
        w.color_changed.connect(
            lambda cid, mode, color: self.store.update_card(cid, color_mode=mode, color=color))
        w.position_saved.connect(
            lambda cid, x, y: self.store.update_card(cid, x=x, y=y))
        self.widgets[cd["id"]] = w

        pos = self._initial_pos(w, cd, default_index)
        w.move(*pos)
        w.show()
        hwnd = int(w.winId())
        parent = desktop_embed.embed_into_wallpaper(hwnd)
        if not parent:
            desktop_embed.send_to_bottom(hwnd)
        self.parents[cd["id"]] = parent
        self.widgets_changed.emit()

    def detach(self, cd_id: str, update_store=True):
        w = self.widgets.pop(cd_id, None)
        self.parents.pop(cd_id, None)
        if w:
            w.close()
            w.deleteLater()
        if update_store and self.store.get(cd_id):
            self.store.update_card(cd_id, attached=False)
        self.widgets_changed.emit()

    def attach_all(self):
        for i, cd in enumerate(self.store.countdowns):
            if cd["id"] not in self.widgets:
                self.store.update_card(cd["id"], attached=True)
                cd["attached"] = True
                self.attach(cd, i)

    def detach_all(self):
        for cid in list(self.widgets.keys()):
            self.detach(cid)

    def restore(self):
        """开机/启动时恢复上次贴在桌面的挂件。"""
        attached = [c for c in self.store.countdowns if c.get("attached")]
        for i, cd in enumerate(attached):
            self.attach(cd, i)

    def _initial_pos(self, w, cd, index):
        if cd.get("x") is not None and cd.get("y") is not None:
            return int(cd["x"]), int(cd["y"])
        from PySide6.QtWidgets import QApplication
        screen = QApplication.primaryScreen().availableGeometry()
        x = screen.right() - w.width() - 26
        y = screen.top() + 16 + index * (w.height() + 14)
        return x, y

    # ---------- 定时刷新 / 守护 ----------
    def _tick_all(self):
        for cid, w in list(self.widgets.items()):
            cd = self.store.get(cid)
            if cd:
                w.update_card(cd)

    def _on_data_changed(self):
        live = {c["id"]: c for c in self.store.countdowns}
        # 删除的卡片同步关闭挂件
        for cid in list(self.widgets.keys()):
            if cid not in live:
                w = self.widgets.pop(cid, None)
                self.parents.pop(cid, None)
                if w:
                    w.close()
        # 内容更新
        for cid, w in self.widgets.items():
            w.update_card(live[cid])

    def _on_settings_changed(self):
        for w in self.widgets.values():
            w.apply_settings(self.store.settings)

    def _guard_reattach(self):
        if not desktop_embed.IS_WIN:
            return
        for cid, w in list(self.widgets.items()):
            parent = self.parents.get(cid, 0)
            if parent and not desktop_embed.parent_alive(parent):
                new_parent = desktop_embed.embed_into_wallpaper(int(w.winId()))
                self.parents[cid] = new_parent

    def shutdown(self):
        self.tick.stop()
        self.guard.stop()
        for w in self.widgets.values():
            w.close()
        self.widgets.clear()
