# -*- coding: utf-8 -*-
"""主题系统: 多主题调色板 + 全局样式构建 + 主题持久化

主题名保存在 ~/.ToleranceTool/config.json 的 "theme" 字段,
切换后需重启应用生效(SettingsDialog 提供立即重启)。
"""
import os
import json

# ─── 主题定义 ───
# 键: BG 主背景 / CARD 卡片 / CARD_H 卡片悬停 / BORDER 边框
#     TEXT 主文字 / TEXT2 次要文字 / ACCENT 强调色
#     GREEN 间隙/成功 / ORANGE 过渡/警告 / RED 过盈/错误
THEMES = {
    "暗夜蓝": {
        "BG": "#0f0f14", "CARD": "#1a1a24", "CARD_H": "#22222e",
        "BORDER": "#2a2a3a", "TEXT": "#e0e0e8", "TEXT2": "#8888a0",
        "ACCENT": "#6c8cff", "ACCENT_H": "#5a7aee", "ACCENT_P": "#4a6ade",
        "GREEN": "#5cd68a", "ORANGE": "#f0a050", "PURPLE": "#b06cff",
        "RED": "#ff6b6b",
    },
    "墨玉黑": {
        "BG": "#0a0a0a", "CARD": "#151515", "CARD_H": "#1f1f1f",
        "BORDER": "#2d2d2d", "TEXT": "#eaeaea", "TEXT2": "#8c8c8c",
        "ACCENT": "#00c896", "ACCENT_H": "#00b184", "ACCENT_P": "#009a73",
        "GREEN": "#4ade80", "ORANGE": "#fbbf24", "PURPLE": "#a78bfa",
        "RED": "#f87171",
    },
    "清爽白": {
        "BG": "#f5f6fa", "CARD": "#ffffff", "CARD_H": "#eceef5",
        "BORDER": "#d8dbe6", "TEXT": "#2a2d3a", "TEXT2": "#7a7f92",
        "ACCENT": "#3b6ef5", "ACCENT_H": "#2f5cd9", "ACCENT_P": "#244bbd",
        "GREEN": "#16a34a", "ORANGE": "#d97706", "PURPLE": "#7c3aed",
        "RED": "#dc2626",
    },
    "FlangeQuery": {
        "BG": "#f5f8fb", "CARD": "#ffffff", "CARD_H": "#eef3f8",
        "BORDER": "#c9d2dc", "TEXT": "#17202a", "TEXT2": "#667085",
        "ACCENT": "#1f4e79", "ACCENT_H": "#163a5f", "ACCENT_P": "#0f2d4a",
        "GREEN": "#1a7f37", "ORANGE": "#a15c00", "PURPLE": "#6c5ce7",
        "RED": "#c0392b",
    },
    "护眼米": {
        "BG": "#f3efe4", "CARD": "#fbf8ef", "CARD_H": "#eae4d3",
        "BORDER": "#d5cbb4", "TEXT": "#3a352a", "TEXT2": "#8a8271",
        "ACCENT": "#2f7d5c", "ACCENT_H": "#276a4e", "ACCENT_P": "#1f5740",
        "GREEN": "#2f9e5f", "ORANGE": "#c07a1e", "PURPLE": "#6d5aa8",
        "RED": "#c04848",
    },
}

DEFAULT_THEME = "FlangeQuery"
THEME_ORDER = ["FlangeQuery", "清爽白", "护眼米"]

_PALETTE_KEYS = ("BG", "CARD", "CARD_H", "BORDER", "TEXT", "TEXT2",
                 "ACCENT", "GREEN", "ORANGE", "RED")

# ─── 配置文件(与 dialogs.py 同一路径, 但独立读写避免循环导入) ───
_APP_DIR = os.path.join(os.path.expanduser('~'), '.ToleranceTool')
os.makedirs(_APP_DIR, exist_ok=True)
CONFIG_PATH = os.path.join(_APP_DIR, 'config.json')


def load_theme_name():
    return "FlangeQuery"
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8-sig') as f:
            cfg = json.load(f)
        name = cfg.get("theme")
        if name in THEMES:
            return name
    except Exception:
        pass
    return DEFAULT_THEME


def save_theme_name(name):
    if name not in THEMES:
        return
    cfg = {}
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8-sig') as f:
            cfg = json.load(f)
    except Exception:
        pass
    cfg["theme"] = name
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


def get_palette(name=None):
    """返回主题调色板 dict; 无参时用当前已保存主题"""
    return THEMES[name] if name in THEMES else THEMES[load_theme_name()]


def unpack(p):
    """按固定顺序解包调色板 → 10 个常量, 供模块级绑定"""
    return tuple(p[k] for k in _PALETTE_KEYS)


def build_style(p):
    """由调色板构建应用全局 QSS"""
    return f"""
QMainWindow, QWidget {{ background-color:{p['BG']}; color:{p['TEXT']}; }}
QLabel {{ color:{p['TEXT']}; background:transparent; }}
QLineEdit {{
    background:{p['CARD']}; border:1px solid {p['BORDER']}; border-radius:6px;
    padding:8px 12px; color:{p['TEXT']}; font-size:16px;
    selection-background-color:{p['ACCENT']};
}}
QLineEdit:focus {{ border:1px solid {p['ACCENT']}; }}
QComboBox {{
    background:{p['CARD']}; border:1px solid {p['BORDER']}; border-radius:6px;
    padding:8px 12px; color:{p['TEXT']}; font-size:13px; min-height:22px;
}}
QComboBox:hover {{ border:1px solid {p['ACCENT']}; }}
QComboBox::drop-down {{ border:none; width:24px; }}
QComboBox QAbstractItemView {{
    background:{p['CARD']}; border:1px solid {p['BORDER']}; color:{p['TEXT']};
    selection-background-color:{p['ACCENT']}; padding:4px;
}}
QPushButton {{
    background:{p['ACCENT']}; color:white; border:none; border-radius:6px;
    padding:10px; font-size:14px; font-weight:bold;
}}
QPushButton:hover {{ background:{p['ACCENT_H']}; }}
QPushButton:pressed {{ background:{p['ACCENT_P']}; }}
QGroupBox {{
    background:{p['CARD']}; border:1px solid {p['BORDER']}; border-radius:8px;
    margin-top:14px; padding:14px 10px 10px 10px;
    font-size:12px; color:{p['TEXT2']}; font-weight:bold;
}}
QGroupBox::title {{ subcontrol-origin:margin; left:16px; padding:0 6px; }}
QScrollArea {{ border:none; background:transparent; }}
QTabWidget::pane {{
    border: 1px solid {p['BORDER']};
    border-radius: 6px;
    background: transparent;
}}
QTabBar::tab {{
    background: {p['CARD']};
    border: 1px solid {p['BORDER']};
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    padding: 8px 20px;
    color: {p['TEXT2']};
    font-size: 13px;
    margin-right: 2px;
}}
QTabBar::tab:selected {{
    background: {p['CARD_H']};
    color: {p['ACCENT']};
    font-weight: bold;
    border: 1px solid {p['ACCENT']};
    border-bottom: 1px solid {p['CARD_H']};
}}
QScrollBar:vertical {{ background:transparent; width:6px; }}
QScrollBar::handle:vertical {{ background:{p['BORDER']}; border-radius:3px; min-height:30px; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height:0px; }}
QRadioButton, QCheckBox {{ spacing:8px; background:transparent; }}
QRadioButton::indicator, QCheckBox::indicator {{
    width:18px; height:18px;
    border:2px solid {p['BORDER']}; background:{p['CARD_H']};
    border-radius:9px;
}}
QCheckBox::indicator {{ border-radius:4px; }}
QRadioButton::indicator:hover, QCheckBox::indicator:hover {{ border:2px solid {p['ACCENT']}; }}
QRadioButton::indicator:checked {{
    border:2px solid {p['ACCENT']};
    background: qradialgradient(cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5,
        stop:0 {p['ACCENT']}, stop:0.45 {p['ACCENT']}, stop:0.55 {p['CARD_H']}, stop:1 {p['CARD_H']});
}}
QCheckBox::indicator:checked {{ border:2px solid {p['ACCENT']}; background:{p['ACCENT']}; }}
QRadioButton::indicator:disabled, QCheckBox::indicator:disabled {{ opacity:0.4; }}
"""
