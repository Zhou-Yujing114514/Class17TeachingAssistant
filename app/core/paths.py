"""路径与资源工具。"""
import os
import sys
from pathlib import Path

APP_NAME = "Class17Assistant"
DISPLAY_NAME = "高二17班教学助手"


def app_data_dir() -> Path:
    """应用数据目录（Windows: %APPDATA%/Class17Assistant）。"""
    base = os.environ.get("APPDATA")
    if base:
        p = Path(base) / APP_NAME
    else:
        p = Path.home() / ".config" / APP_NAME
    p.mkdir(parents=True, exist_ok=True)
    return p


def resource_path(rel: str) -> str:
    """兼容 PyInstaller 解包目录的资源绝对路径。"""
    base = getattr(sys, "_MEIPASS", None)
    root = Path(base) if base else Path(__file__).resolve().parents[2]
    return str(root / rel)
