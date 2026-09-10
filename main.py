"""高二17班教学助手 —— 程序入口。"""
import sys

from PySide6.QtCore import Qt, QSharedMemory
from PySide6.QtGui import QIcon, QFont, QAction
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu

from app.core.paths import resource_path, DISPLAY_NAME
from app.core.store import Store
from app.core import autostart
from app.widgets.desktop_widget import WidgetManager
from app.ui.style import QSS
from app.ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName(DISPLAY_NAME)
    app.setQuitOnLastWindowClosed(False)  # 关窗后驻留托盘
    app.setWindowIcon(QIcon(resource_path("assets/app.ico")))
    app.setFont(QFont("Microsoft YaHei UI", 10))
    app.setStyleSheet(QSS)

    # 单实例，避免重复驻留；先 attach+detach 清理上次崩溃残留的段
    shared = QSharedMemory("Class17Assistant_single_instance")
    if shared.attach():
        shared.detach()
    if not shared.create(1):
        sys.exit(0)

    store = Store()
    manager = WidgetManager(store)
    win = MainWindow(store, manager)

    # ---------- 系统托盘 ----------
    tray = QSystemTrayIcon(QIcon(resource_path("assets/app.ico")))
    tray.setToolTip(DISPLAY_NAME)
    menu = QMenu()
    act_show = QAction("打开主界面")
    act_attach = QAction("一键贴到桌面")
    act_detach = QAction("收回全部挂件")
    act_auto = QAction("开机自启")
    act_auto.setCheckable(True)
    act_auto.setChecked(autostart.is_enabled())
    act_quit = QAction("退出")
    for a in (act_show, act_attach, act_detach):
        menu.addAction(a)
    menu.addSeparator()
    menu.addAction(act_auto)
    menu.addSeparator()
    menu.addAction(act_quit)
    tray.setContextMenu(menu)

    def show_window():
        win.showNormal()
        win.raise_()
        win.activateWindow()

    def on_tray_activated(reason):
        if reason == QSystemTrayIcon.DoubleClick:
            show_window()

    def toggle_autostart(on):
        if not autostart.set_enabled(on) and on:
            act_auto.setChecked(False)

    act_show.triggered.connect(show_window)
    act_attach.triggered.connect(manager.attach_all)
    act_detach.triggered.connect(manager.detach_all)
    act_auto.toggled.connect(toggle_autostart)
    tray.activated.connect(on_tray_activated)
    tray.show()

    _first_hide = {"done": False}

    def on_hide_to_tray():
        if not _first_hide["done"]:
            _first_hide["done"] = True
            tray.showMessage(DISPLAY_NAME, "已最小化到右下角托盘，桌面挂件继续运行")

    win.hide_to_tray_requested.connect(on_hide_to_tray)

    def quit_app():
        win.shutdown()
        manager.shutdown()
        tray.hide()
        app.quit()

    act_quit.triggered.connect(quit_app)
    app.aboutToQuit.connect(lambda: (store.save_countdowns(), store.save_settings()))

    # 恢复桌面挂件
    manager.restore()

    # --autostart：开机自启时仅驻留托盘与挂件，不弹主窗口
    if "--autostart" not in sys.argv:
        win.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
