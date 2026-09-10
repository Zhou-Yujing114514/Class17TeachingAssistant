"""特定时刻倒计时页面：多卡片、精度切换、颜色、贴到桌面。"""
import datetime as dt

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QScrollArea, QFrame, QDialog,
                               QLineEdit, QDateTimeEdit, QRadioButton,
                               QColorDialog, QButtonGroup, QMessageBox)

from app.core.store import new_countdown
from app.core.countdown_util import parse_target, format_countdown


class NewCountdownDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("新建倒计时")
        self.setFixedSize(420, 300)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 22, 24, 20)
        lay.setSpacing(12)

        lay.addWidget(QLabel("事件名称"))
        self.edit_name = QLineEdit()
        self.edit_name.setPlaceholderText("例如：期中考试")
        lay.addWidget(self.edit_name)

        lay.addWidget(QLabel("目标时刻"))
        self.dt = QDateTimeEdit()
        self.dt.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.dt.setCalendarPopup(True)
        default = dt.datetime.now() + dt.timedelta(days=7)
        self.dt.setDateTime(default.replace(hour=8, minute=0, second=0))
        lay.addWidget(self.dt)

        lay.addWidget(QLabel("显示精度"))
        row = QHBoxLayout()
        self.rb_sec = QRadioButton("精确到秒")
        self.rb_day = QRadioButton("精确到天")
        self.rb_sec.setChecked(True)
        row.addWidget(self.rb_sec)
        row.addWidget(self.rb_day)
        row.addStretch()
        lay.addLayout(row)
        lay.addStretch()

        btns = QHBoxLayout()
        btns.addStretch()
        cancel = QPushButton("取消")
        cancel.setObjectName("Ghost")
        ok = QPushButton("创建")
        ok.setObjectName("Primary")
        cancel.clicked.connect(self.reject)
        ok.clicked.connect(self._accept)
        btns.addWidget(cancel)
        btns.addWidget(ok)
        lay.addLayout(btns)

    def _accept(self):
        name = self.edit_name.text().strip()
        if not name:
            QMessageBox.information(self, "提示", "请填写事件名称")
            return
        if self.dt.dateTime().toPython() <= dt.datetime.now():
            QMessageBox.information(self, "提示", "目标时刻需要在未来")
            return
        self.accept()

    def data(self):
        return {
            "name": self.edit_name.text().strip(),
            "target": self.dt.dateTime().toPython().isoformat(),
            "precision": "day" if self.rb_day.isChecked() else "second",
        }


class CountdownCard(QFrame):
    def __init__(self, cd, store, manager, on_changed, parent=None):
        super().__init__(parent)
        self.cd = cd
        self.store = store
        self.manager = manager
        self.on_changed = on_changed
        self.setObjectName("Card")
        self.setMinimumHeight(150)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(20, 16, 20, 16)
        lay.setSpacing(10)

        top = QHBoxLayout()
        self.lbl_name = QLabel()
        self.lbl_name.setStyleSheet("font-size:16px; font-weight:700;")
        self.lbl_target = QLabel()
        self.lbl_target.setObjectName("Hint")
        top.addWidget(self.lbl_name)
        top.addStretch()
        top.addWidget(self.lbl_target)
        lay.addLayout(top)

        self.lbl_left = QLabel()
        self.lbl_left.setStyleSheet("font-size:19px; color:#0E93C9; font-weight:700;")
        lay.addWidget(self.lbl_left)

        ctrl = QHBoxLayout()
        self.group = QButtonGroup(self)
        self.btn_day = QPushButton("精确到天")
        self.btn_sec = QPushButton("精确到秒")
        for b in (self.btn_day, self.btn_sec):
            b.setObjectName("Ghost")
            b.setCheckable(True)
            self.group.addButton(b)
        self.btn_day.clicked.connect(lambda: self._set_precision("day"))
        self.btn_sec.clicked.connect(lambda: self._set_precision("second"))

        self.btn_neon = QPushButton("动态霓虹")
        self.btn_neon.setObjectName("Ghost")
        self.btn_neon.setCheckable(True)
        self.btn_neon.clicked.connect(lambda: self._set_color("neon"))
        self.btn_custom = QPushButton("自定义颜色")
        self.btn_custom.setObjectName("Ghost")
        self.btn_custom.clicked.connect(self._pick_color)

        self.btn_attach = QPushButton("贴到桌面")
        self.btn_attach.setObjectName("Primary")
        self.btn_attach.clicked.connect(self.toggle_attach)
        self.btn_del = QPushButton("删除")
        self.btn_del.setObjectName("DangerGhost")
        self.btn_del.clicked.connect(self._delete)

        for b in (self.btn_day, self.btn_sec, self.btn_neon,
                  self.btn_custom, self.btn_attach, self.btn_del):
            ctrl.addWidget(b)
        ctrl.addStretch()
        lay.addLayout(ctrl)
        self.sync()

    def _set_precision(self, mode):
        self.store.update_card(self.cd["id"], precision=mode)

    def _set_color(self, mode):
        self.store.update_card(self.cd["id"], color_mode=mode)

    def _pick_color(self):
        col = QColorDialog.getColor(QColor(self.cd.get("color", "#00E5FF")),
                                   self, "选择挂件颜色")
        if col.isValid():
            self.store.update_card(self.cd["id"], color_mode="custom",
                                   color=col.name().upper())

    def toggle_attach(self):
        cid = self.cd["id"]
        if cid in self.manager.widgets:
            self.manager.detach(cid)
        else:
            self.store.update_card(cid, attached=True)
            self.cd["attached"] = True
            idx = self.store.countdowns.index(self.cd)
            self.manager.attach(self.cd, idx)

    def _delete(self):
        if QMessageBox.question(self, "删除", f"确定删除「{self.cd['name']}」？") \
                != QMessageBox.Yes:
            return
        self.manager.detach(self.cd["id"], update_store=False)
        self.store.remove(self.cd["id"])
        self.on_changed()

    def refresh_text(self):
        target = parse_target(self.cd["target"])
        self.lbl_left.setText(
            format_countdown(target, self.cd["precision"], self.cd["name"]))

    def sync(self):
        self.cd = self.store.get(self.cd["id"]) or self.cd
        self.lbl_name.setText(self.cd["name"])
        t = parse_target(self.cd["target"])
        self.lbl_target.setText("目标时刻：" + t.strftime("%Y-%m-%d %H:%M:%S"))
        self.btn_day.setChecked(self.cd["precision"] == "day")
        self.btn_sec.setChecked(self.cd["precision"] == "second")
        self.btn_neon.setChecked(self.cd.get("color_mode") == "neon")
        attached = self.cd["id"] in self.manager.widgets
        self.btn_attach.setText("收回挂件" if attached else "贴到桌面")
        self.refresh_text()


class CountdownPage(QWidget):
    def __init__(self, store, manager, parent=None):
        super().__init__(parent)
        self.store = store
        self.manager = manager
        self.cards = []

        root = QVBoxLayout(self)
        root.setContentsMargins(30, 24, 30, 18)
        root.setSpacing(14)

        head = QHBoxLayout()
        col = QVBoxLayout()
        title = QLabel("特定时刻倒计时")
        title.setObjectName("PageTitle")
        sub = QLabel("可建多个倒计时，并把卡片以霓虹挂件嵌入桌面壁纸层")
        sub.setObjectName("PageSub")
        col.addWidget(title)
        col.addWidget(sub)
        head.addLayout(col)
        head.addStretch()
        btn_all = QPushButton("一键全部贴到桌面")
        btn_all.setObjectName("Ghost")
        btn_all.clicked.connect(self.manager.attach_all)
        btn_new = QPushButton("新建倒计时")
        btn_new.setObjectName("Primary")
        btn_new.clicked.connect(self._new)
        head.addWidget(btn_all)
        head.addWidget(btn_new)
        root.addLayout(head)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.host = QWidget()
        self.card_layout = QVBoxLayout(self.host)
        self.card_layout.setContentsMargins(2, 4, 8, 4)
        self.card_layout.setSpacing(12)
        self.card_layout.addStretch()
        self.scroll.setWidget(self.host)
        root.addWidget(self.scroll)

        self.empty = QLabel("还没有倒计时，点右上角「新建倒计时」开始")
        self.empty.setAlignment(Qt.AlignCenter)
        self.empty.setStyleSheet("color:#9aa5b1; font-size:14px;")
        self.card_layout.insertWidget(0, self.empty)

        self.store.countdowns_changed.connect(self.rebuild)
        self.manager.widgets_changed.connect(self.rebuild)
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self._tick)
        self.timer.start()
        self.rebuild()

    def _new(self):
        dlg = NewCountdownDialog(self.window())
        if dlg.exec() == QDialog.Accepted:
            d = dlg.data()
            cd = new_countdown(d["name"], d["target"], d["precision"])
            self.store.add(cd)

    def rebuild(self):
        for card in self.cards:
            card.setParent(None)
            card.deleteLater()
        self.cards = []
        self.empty.setVisible(not self.store.countdowns)
        for cd in self.store.countdowns:
            card = CountdownCard(cd, self.store, self.manager, self.rebuild)
            self.card_layout.insertWidget(self.card_layout.count() - 1, card)
            self.cards.append(card)

    def _tick(self):
        for card in self.cards:
            card.refresh_text()
