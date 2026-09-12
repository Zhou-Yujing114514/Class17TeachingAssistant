"""全局 QSS（简约白底 + 校徽蓝点缀）。"""

ACCENT = "#12A8E4"
ACCENT_DARK = "#0E93C9"
ACCENT_SOFT = "#E6F6FD"
TEXT = "#1F2937"
SUBTEXT = "#6B7684"
BORDER = "#E7ECF1"

QSS = f"""
* {{
    font-family: "Microsoft YaHei UI", "微软雅黑", "Segoe UI", sans-serif;
    color: {TEXT};
    outline: none;
}}
#Root {{
    background: #ffffff;
    border-radius: 14px;
    border: 1px solid {BORDER};
}}
#TitleBar {{
    background: transparent;
}}
#TitleText {{
    color: #2b3440;
    font-size: 13px;
    font-weight: 600;
    letter-spacing: 0.5px;
}}
#WinBtn {{
    background: transparent;
    border: none;
    border-radius: 8px;
    color: #5b6675;
    font-size: 14px;
}}
#WinBtn:hover {{ background: #eef2f6; color: #22303e; }}
#BtnClose {{ background: transparent; border: none; border-radius: 8px;
    color: #5b6675; font-size: 14px; }}
#BtnClose:hover {{ background: #E81123; color: #ffffff; }}

#Sidebar {{
    background: #f7f9fb;
    border-right: 1px solid {BORDER};
    border-bottom-left-radius: 14px;
}}
#Brand {{
    color: {ACCENT_DARK};
    font-size: 15px;
    font-weight: 700;
    padding: 6px 8px;
}}
NavButton {{
    text-align: left;
    padding: 11px 14px;
    border: none;
    border-radius: 10px;
    background: transparent;
    color: #485463;
    font-size: 14px;
}}
NavButton:hover {{ background: #edf2f6; }}
NavButton:checked {{
    background: {ACCENT_SOFT};
    color: {ACCENT_DARK};
    font-weight: 700;
}}
#SideFooter {{ color: #9aa5b1; font-size: 11px; padding-left: 10px; }}

#PageTitle {{ font-size: 22px; font-weight: 700; color: #18222e; }}
#PageSub {{ color: {SUBTEXT}; font-size: 12.5px; }}
#Motto {{
    font-size: 26px;
    font-weight: 800;
    color: {ACCENT_DARK};
    letter-spacing: 1px;
    padding: 4px 0 2px;
}}

QFrame#Card {{
    background: #ffffff;
    border: 1px solid {BORDER};
    border-radius: 12px;
}}
QFrame#SoftCard {{
    background: #f7fafc;
    border: 1px solid #edf1f5;
    border-radius: 12px;
}}

QPushButton#Primary {{
    background: {ACCENT};
    color: white;
    border: none;
    border-radius: 9px;
    padding: 9px 18px;
    font-size: 13.5px;
    font-weight: 600;
}}
QPushButton#Primary:hover {{ background: {ACCENT_DARK}; }}
QPushButton#Primary:disabled {{ background: #b9e2f4; }}

QPushButton#Ghost {{
    background: #f1f5f9;
    color: #334155;
    border: 1px solid #e4eaf0;
    border-radius: 9px;
    padding: 8px 14px;
    font-size: 13px;
}}
QPushButton#Ghost:hover {{ background: #e7eef4; }}
QPushButton#Ghost:checked {{ background: {ACCENT_SOFT}; color: {ACCENT_DARK};
    border-color: {ACCENT}; font-weight: 700; }}

QPushButton#DangerGhost {{
    background: #fff5f5; color: #d33; border: 1px solid #f3d4d4;
    border-radius: 9px; padding: 8px 14px; font-size: 13px;
}}
QPushButton#DangerGhost:hover {{ background: #ffe8e8; }}

QLineEdit, QDateTimeEdit, QSpinBox, QDoubleSpinBox, QComboBox {{
    background: #f6f8fa;
    border: 1px solid #dde3ea;
    border-radius: 8px;
    padding: 7px 10px;
    font-size: 13px;
    selection-background-color: {ACCENT};
}}
QLineEdit:focus, QDateTimeEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {{
    border: 1px solid {ACCENT};
    background: #ffffff;
}}
QComboBox::drop-down {{ border: none; width: 22px; }}
QComboBox QAbstractItemView {{
    background: #ffffff; border: 1px solid #dde3ea;
    border-radius: 8px; selection-background-color: {ACCENT_SOFT};
    selection-color: {ACCENT_DARK}; padding: 4px;
}}

QProgressBar {{
    background: #edf1f5;
    border: none;
    border-radius: 8px;
    height: 16px;
    text-align: center;
    color: #566273;
    font-size: 11px;
}}
QProgressBar::chunk {{
    border-radius: 8px;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #34d399, stop:0.55 #fbbf24, stop:1 #ef4444);
}}

QScrollArea {{ border: none; background: transparent; }}
QScrollBar:vertical {{ background: transparent; width: 10px; margin: 2px; }}
QScrollBar::handle:vertical {{ background: #cfd8e0; border-radius: 5px; min-height: 30px; }}
QScrollBar::handle:vertical:hover {{ background: #b3c0cc; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QScrollBar:horizontal {{ background: transparent; height: 10px; margin: 2px; }}
QScrollBar::handle:horizontal {{ background: #cfd8e0; border-radius: 5px; min-width: 30px; }}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; }}

QCheckBox {{ font-size: 13px; spacing: 8px; }}
QRadioButton {{ font-size: 13px; spacing: 6px; }}
QLabel#Hint {{ color: {SUBTEXT}; font-size: 12px; }}
"""
