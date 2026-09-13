"""倒计时数据与设置的本地持久化（JSON）。"""
import json
import uuid
import datetime as dt

from PySide6.QtCore import QObject, Signal

from .paths import app_data_dir

DEFAULT_SETTINGS = {
    "db_offset": 94,            # 分贝估算偏移（dBFS -> 估算 dB）
    "widget_font_size": 44,     # 桌面挂件字号（最小 44px，可往大调）
    "neon_period_s": 7.0,       # 霓虹颜色流动一周的秒数
    "dark_outline": True,       # 挂件文字暗色描边衬底
    "default_color_mode": "neon",
    "default_color": "#00E5FF",
    "auto_attach_on_start": True,
}


def new_countdown(name: str, target_iso: str, precision: str = "second"):
    return {
        "id": uuid.uuid4().hex[:8],
        "name": name,
        "target": target_iso,
        "precision": precision,          # day / second
        "color_mode": "neon",            # neon / custom
        "color": DEFAULT_SETTINGS["default_color"],
        "attached": False,               # 是否贴到桌面
        "x": None,
        "y": None,
    }


class Store(QObject):
    countdowns_changed = Signal()
    settings_changed = Signal()

    def __init__(self):
        super().__init__()
        d = app_data_dir()
        self.cd_path = d / "countdowns.json"
        self.set_path = d / "settings.json"
        self.countdowns = []
        self.settings = dict(DEFAULT_SETTINGS)
        self._load()

    # ---------- IO ----------
    def _load(self):
        try:
            data = json.loads(self.cd_path.read_text("utf-8"))
            if isinstance(data, list):
                merged = []
                for item in data:
                    base = new_countdown(item.get("name", "事件"),
                                         item.get("target", dt.datetime.now().isoformat()))
                    base.update({k: v for k, v in item.items() if k in base})
                    merged.append(base)
                self.countdowns = merged
        except (FileNotFoundError, ValueError):
            pass
        try:
            user_set = json.loads(self.set_path.read_text("utf-8"))
            if isinstance(user_set, dict):
                self.settings.update({k: v for k, v in user_set.items()
                                      if k in DEFAULT_SETTINGS})
        except (FileNotFoundError, ValueError):
            pass

    def save_countdowns(self):
        tmp = self.cd_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.countdowns, ensure_ascii=False, indent=2), "utf-8")
        tmp.replace(self.cd_path)

    def save_settings(self):
        tmp = self.set_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.settings, ensure_ascii=False, indent=2), "utf-8")
        tmp.replace(self.set_path)

    # ---------- countdown CRUD ----------
    def get(self, cd_id: str):
        for cd in self.countdowns:
            if cd["id"] == cd_id:
                return cd
        return None

    def add(self, cd: dict):
        self.countdowns.append(cd)
        self.save_countdowns()
        self.countdowns_changed.emit()
        return cd

    def update_card(self, cd_id: str, **fields):
        cd = self.get(cd_id)
        if not cd:
            return
        cd.update({k: v for k, v in fields.items() if k in cd})
        self.save_countdowns()
        self.countdowns_changed.emit()

    def remove(self, cd_id: str):
        self.countdowns = [c for c in self.countdowns if c["id"] != cd_id]
        self.save_countdowns()
        self.countdowns_changed.emit()

    # ---------- settings ----------
    def set_setting(self, key, value, emit=True):
        if key in self.settings:
            self.settings[key] = value
            self.save_settings()
            if emit:
                self.settings_changed.emit()
