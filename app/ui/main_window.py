"""主窗口：无边框圆角外壳 + 侧边导航 + 页面堆栈。"""
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (QWidget, QFrame, QVBoxLayout, QHBoxLayout,
                               QLabel, QPushButton, QButtonGroup,
                               QStackedWidget, QGraphicsDropShadowEffect)
from PySide6.QtGui import QIcon, QKeySequence, QShortcut
from PySide6.QtCore import Qt

from app import __version__
from app.core.paths import resource_path
from app.ui.titlebar import TitleBar
from app.pages.db_meter_page import DbMeterPage
from app.pages.countdown_page import CountdownPage
from app.pages.settings_page import SettingsPage


class NavButton(QPushButton):
    def __init__(self, text: str):
        super().__init__(text)
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(42)


class MainWindow(QWidget):
    hide_to_tray_requested = Signal()

    def __init__(self, store, manager):
        super().__init__()
        self.store = store
        self.manager = manager
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowSystemMenuHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(1000, 680)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(14, 14, 14, 14)
        self.outer = outer
        root = QFrame()
        root.setObjectName("Root")
        self.root = root
        shadow = QGraphicsDropShadowEffect(root)
        shadow.setBlurRadius(28)
        shadow.setOffset(0, 6)
        shadow.setColor(Qt.black)
        from PySide6.QtGui import QColor
        shadow.setColor(QColor(0, 0, 0, 42))
        root.setGraphicsEffect(shadow)
        outer.addWidget(root)

        box = QVBoxLayout(root)
        box.setContentsMargins(0, 0, 0, 0)
        box.setSpacing(0)

        self.titlebar = TitleBar()
        self.titlebar.minimize_requested.connect(self.showMinimized)
        self.titlebar.close_requested.connect(self.hide_to_tray)
        box.addWidget(self.titlebar)

        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)

        # 侧边栏
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        self.sidebar = sidebar
        sidebar.setFixedWidth(198)
        sb = QVBoxLayout(sidebar)
        sb.setContentsMargins(14, 14, 14, 14)
        sb.setSpacing(8)
        brand_row = QHBoxLayout()
        brand_icon = QLabel()
        brand_icon.setFixedSize(26, 26)
        brand_icon.setPixmap(QIcon(resource_path("assets/app.ico")).pixmap(26, 26))
        brand = QLabel("教学助手")
        brand.setObjectName("Brand")
        brand_row.addWidget(brand_icon)
        brand_row.addWidget(brand)
        sb.addLayout(brand_row)
        sb.addSpacing(8)

        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)
        self.page_db = DbMeterPage(store)
        self.page_cd = CountdownPage(store, manager)
        self.page_set = SettingsPage(store, manager)
        pages = [("　分贝测量仪", self.page_db),
                 ("　倒计时", self.page_cd),
                 ("　设置", self.page_set)]
        self.stack = QStackedWidget()
        for i, (name, w) in enumerate(pages):
            btn = NavButton(name)
            btn.clicked.connect(lambda _=False, idx=i: self.stack.setCurrentIndex(idx))
            self.nav_group.addButton(btn, i)
            sb.addWidget(btn)
            self.stack.addWidget(w)
        self.nav_group.button(0).setChecked(True)
        sb.addStretch()
        foot = QLabel(f"高二17班 · v{__version__}")
        foot.setObjectName("SideFooter")
        sb.addWidget(foot)

        body.addWidget(sidebar)
        body.addWidget(self.stack, 1)
        box.addLayout(body, 1)

        # 分贝仪全屏
        self.page_db.fullscreen_requested.connect(self.set_meter_fullscreen)
        self._meter_fullscreen = False
        esc = QShortcut(QKeySequence(Qt.Key_Escape), self)
        esc.activated.connect(self._esc_exit_fullscreen)

    def _esc_exit_fullscreen(self):
        if self._meter_fullscreen:
            self.page_db.set_fullscreen(False)

    def set_meter_fullscreen(self, on: bool):
        self._meter_fullscreen = on
        if on:
            # 释放固定尺寸，铺满整块屏幕
            self.setMinimumSize(0, 0)
            self.setMaximumSize(16777215, 16777215)
            self.outer.setContentsMargins(0, 0, 0, 0)
            self.root.setStyleSheet("#Root{border-radius:0px;}")
            self.titlebar.hide()
            self.sidebar.hide()
            self.hide()
            self.setAttribute(Qt.WA_TranslucentBackground, False)
            self.showFullScreen()
        else:
            self.showNormal()
            self.titlebar.show()
            self.sidebar.show()
            self.outer.setContentsMargins(14, 14, 14, 14)
            self.root.setStyleSheet("")
            self.setAttribute(Qt.WA_TranslucentBackground, True)
            self.setFixedSize(1000, 680)
            self.show()

    def hide_to_tray(self):
        self.hide()
        self.hide_to_tray_requested.emit()

    def shutdown(self):
        self.page_db.shutdown()
