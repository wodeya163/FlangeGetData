# Reconstructed from bytecode by split_decompile.py
# theme.pyc

'''主题系统: 多主题调色板 + 全局样式构建 + 主题持久化

主题名保存在 ~/.ToleranceTool/config.json 的 "theme" 字段,
切换后需重启应用生效(SettingsDialog 提供立即重启)。
'''
import os
import json
THEMES = {
    '暗夜蓝': {
        'BG': '#0f0f14',
        'CARD': '#1a1a24',
        'CARD_H': '#22222e',
        'BORDER': '#2a2a3a',
        'TEXT': '#e0e0e8',
        'TEXT2': '#8888a0',
        'ACCENT': '#6c8cff',
        'ACCENT_H': '#5a7aee',
        'ACCENT_P': '#4a6ade',
        'GREEN': '#5cd68a',
        'ORANGE': '#f0a050',
        'PURPLE': '#b06cff',
        'RED': '#ff6b6b' },
    '墨玉黑': {
        'BG': '#0a0a0a',
        'CARD': '#151515',
        'CARD_H': '#1f1f1f',
        'BORDER': '#2d2d2d',
        'TEXT': '#eaeaea',
        'TEXT2': '#8c8c8c',
        'ACCENT': '#00c896',
        'ACCENT_H': '#00b184',
        'ACCENT_P': '#009a73',
        'GREEN': '#4ade80',
        'ORANGE': '#fbbf24',
        'PURPLE': '#a78bfa',
        'RED': '#f87171' },
    '清爽白': {
        'BG': '#f5f6fa',
        'CARD': '#ffffff',
        'CARD_H': '#eceef5',
        'BORDER': '#d8dbe6',
        'TEXT': '#2a2d3a',
        'TEXT2': '#7a7f92',
        'ACCENT': '#3b6ef5',
        'ACCENT_H': '#2f5cd9',
        'ACCENT_P': '#244bbd',
        'GREEN': '#16a34a',
        'ORANGE': '#d97706',
        'PURPLE': '#7c3aed',
        'RED': '#dc2626' },
    '护眼米': {
        'BG': '#f3efe4',
        'CARD': '#fbf8ef',
        'CARD_H': '#eae4d3',
        'BORDER': '#d5cbb4',
        'TEXT': '#3a352a',
        'TEXT2': '#8a8271',
        'ACCENT': '#2f7d5c',
        'ACCENT_H': '#276a4e',
        'ACCENT_P': '#1f5740',
        'GREEN': '#2f9e5f',
        'ORANGE': '#c07a1e',
        'PURPLE': '#6d5aa8',
        'RED': '#c04848' } }
DEFAULT_THEME = '暗夜蓝'
THEME_ORDER = [
    '暗夜蓝',
    '墨玉黑',
    '清爽白',
    '护眼米']
_PALETTE_KEYS = ('BG', 'CARD', 'CARD_H', 'BORDER', 'TEXT', 'TEXT2', 'ACCENT', 'GREEN', 'ORANGE', 'RED')
_APP_DIR = os.path.join(os.path.expanduser('~'), '.TorqueTool')
os.makedirs(_APP_DIR, exist_ok = True)
CONFIG_PATH = os.path.join(_APP_DIR, 'config.json')

def load_theme_name():

    try:
        f = open(CONFIG_PATH, 'r', encoding = 'utf-8-sig')
        cfg = json.load(f)

        try:
            None(None, None)
        with None:
            if not None:

                try:

                    try:
                        name = cfg.get('theme')
                        if name in THEMES:
                            return name
                    except Exception:
                        pass

                    return DEFAULT_THEME
def save_theme_name(name):
    if name not in THEMES:
        return None
    cfg = None

    try:
        f = open(CONFIG_PATH, 'r', encoding = 'utf-8-sig')
        cfg = json.load(f)

        try:
            None(None, None)
        with None:
            if not None:

                try:

                    try:
                        pass
                    except Exception:
                        pass

                    cfg['theme'] = name
                    f = open(CONFIG_PATH, 'w', encoding = 'utf-8')
                    json.dump(cfg, f, ensure_ascii = False, indent = 2)
                    None(None, None)
                    return None
                    with None:
                        if not None:
                            pass
def get_palette(name):
    '''返回主题调色板 dict; 无参时用当前已保存主题'''
    return THEMES[name] if name in THEMES else THEMES[load_theme_name()]
def unpack(p):
    '''按固定顺序解包调色板 → 10 个常量, 供模块级绑定'''
    return (lambda .0 = None: for k in .0:
p[k]None)(_PALETTE_KEYS())
def build_style(p):
    '''由调色板构建应用全局 QSS'''
    return []['\nQMainWindow, QWidget { background-color:'][f'''{p['BG']}''']['; color:'][f'''{p['TEXT']}''']['; }\nQLabel { color:'][f'''{p['TEXT']}''']['; background:transparent; }\nQLineEdit {\n    background:'][f'''{p['CARD']}''']['; border:1px solid '][f'''{p['BORDER']}''']['; border-radius:6px;\n    padding:8px 12px; color:'][f'''{p['TEXT']}''']['; font-size:16px;\n    selection-background-color:'][f'''{p['ACCENT']}'''][';\n}\nQLineEdit:focus { border:1px solid '][f'''{p['ACCENT']}''']['; }\nQComboBox {\n    background:'][f'''{p['CARD']}''']['; border:1px solid '][f'''{p['BORDER']}''']['; border-radius:6px;\n    padding:8px 12px; color:'][f'''{p['TEXT']}''']['; font-size:13px; min-height:22px;\n}\nQComboBox:hover { border:1px solid '][f'''{p['ACCENT']}''']['; }\nQComboBox::drop-down { border:none; width:24px; }\nQComboBox QAbstractItemView {\n    background:'][f'''{p['CARD']}''']['; border:1px solid '][f'''{p['BORDER']}''']['; color:'][f'''{p['TEXT']}'''][';\n    selection-background-color:'][f'''{p['ACCENT']}''']['; padding:4px;\n}\nQPushButton {\n    background:'][f'''{p['ACCENT']}''']['; color:white; border:none; border-radius:6px;\n    padding:10px; font-size:14px; font-weight:bold;\n}\nQPushButton:hover { background:'][f'''{p['ACCENT_H']}''']['; }\nQPushButton:pressed { background:'][f'''{p['ACCENT_P']}''']['; }\nQGroupBox {\n    background:'][f'''{p['CARD']}''']['; border:1px solid '][f'''{p['BORDER']}''']['; border-radius:8px;\n    margin-top:14px; padding:14px 10px 10px 10px;\n    font-size:12px; color:'][f'''{p['TEXT2']}''']['; font-weight:bold;\n}\nQGroupBox::title { subcontrol-origin:margin; left:16px; padding:0 6px; }\nQScrollArea { border:none; background:transparent; }\nQTabWidget::pane {\n    border: 1px solid '][f'''{p['BORDER']}'''][';\n    border-radius: 6px;\n    background: transparent;\n}\nQTabBar::tab {\n    background: '][f'''{p['CARD']}'''][';\n    border: 1px solid '][f'''{p['BORDER']}'''][';\n    border-bottom: none;\n    border-top-left-radius: 6px;\n    border-top-right-radius: 6px;\n    padding: 8px 20px;\n    color: '][f'''{p['TEXT2']}'''][';\n    font-size: 13px;\n    margin-right: 2px;\n}\nQTabBar::tab:selected {\n    background: '][f'''{p['CARD_H']}'''][';\n    color: '][f'''{p['ACCENT']}'''][';\n    font-weight: bold;\n    border: 1px solid '][f'''{p['ACCENT']}'''][';\n    border-bottom: 1px solid '][f'''{p['CARD_H']}'''][';\n}\nQScrollBar:vertical { background:transparent; width:6px; }\nQScrollBar::handle:vertical { background:'][f'''{p['BORDER']}''']['; border-radius:3px; min-height:30px; }\nQScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height:0px; }\nQRadioButton, QCheckBox { spacing:8px; background:transparent; }\nQRadioButton::indicator, QCheckBox::indicator {\n    width:18px; height:18px;\n    border:2px solid '][f'''{p['BORDER']}''']['; background:'][f'''{p['CARD_H']}'''][';\n    border-radius:9px;\n}\nQCheckBox::indicator { border-radius:4px; }\nQRadioButton::indicator:hover, QCheckBox::indicator:hover { border:2px solid '][f'''{p['ACCENT']}''']['; }\nQRadioButton::indicator:checked {\n    border:2px solid '][f'''{p['ACCENT']}'''][';\n    background: qradialgradient(cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5,\n        stop:0 '][f'''{p['ACCENT']}'''][', stop:0.45 '][f'''{p['ACCENT']}'''][', stop:0.55 '][f'''{p['CARD_H']}'''][', stop:1 '][f'''{p['CARD_H']}'''][');\n}\nQCheckBox::indicator:checked { border:2px solid '][f'''{p['ACCENT']}''']['; background:'][f'''{p['ACCENT']}''']([]['\nQMainWindow, QWidget { background-color:'][f'''{p['BG']}''']['; color:'][f'''{p['TEXT']}''']['; }\nQLabel { color:'][f'''{p['TEXT']}''']['; background:transparent; }\nQLineEdit {\n    background:'][f'''{p['CARD']}''']['; border:1px solid '][f'''{p['BORDER']}''']['; border-radius:6px;\n    padding:8px 12px; color:'][f'''{p['TEXT']}''']['; font-size:16px;\n    selection-background-color:'][f'''{p['ACCENT']}'''][';\n}\nQLineEdit:focus { border:1px solid '][f'''{p['ACCENT']}''']['; }\nQComboBox {\n    background:'][f'''{p['CARD']}''']['; border:1px solid '][f'''{p['BORDER']}''']['; border-radius:6px;\n    padding:8px 12px; color:'][f'''{p['TEXT']}''']['; font-size:13px; min-height:22px;\n}\nQComboBox:hover { border:1px solid '][f'''{p['ACCENT']}''']['; }\nQComboBox::drop-down { border:none; width:24px; }\nQComboBox QAbstractItemView {\n    background:'][f'''{p['CARD']}''']['; border:1px solid '][f'''{p['BORDER']}''']['; color:'][f'''{p['TEXT']}'''][';\n    selection-background-color:'][f'''{p['ACCENT']}''']['; padding:4px;\n}\nQPushButton {\n    background:'][f'''{p['ACCENT']}''']['; color:white; border:none; border-radius:6px;\n    padding:10px; font-size:14px; font-weight:bold;\n}\nQPushButton:hover { background:'][f'''{p['ACCENT_H']}''']['; }\nQPushButton:pressed { background:'][f'''{p['ACCENT_P']}''']['; }\nQGroupBox {\n    background:'][f'''{p['CARD']}''']['; border:1px solid '][f'''{p['BORDER']}''']['; border-radius:8px;\n    margin-top:14px; padding:14px 10px 10px 10px;\n    font-size:12px; color:'][f'''{p['TEXT2']}''']['; font-weight:bold;\n}\nQGroupBox::title { subcontrol-origin:margin; left:16px; padding:0 6px; }\nQScrollArea { border:none; background:transparent; }\nQTabWidget::pane {\n    border: 1px solid '][f'''{p['BORDER']}'''][';\n    border-radius: 6px;\n    background: transparent;\n}\nQTabBar::tab {\n    background: '][f'''{p['CARD']}'''][';\n    border: 1px solid '][f'''{p['BORDER']}'''][';\n    border-bottom: none;\n    border-top-left-radius: 6px;\n    border-top-right-radius: 6px;\n    padding: 8px 20px;\n    color: '][f'''{p['TEXT2']}'''][';\n    font-size: 13px;\n    margin-right: 2px;\n}\nQTabBar::tab:selected {\n    background: '][f'''{p['CARD_H']}'''][';\n    color: '][f'''{p['ACCENT']}'''][';\n    font-weight: bold;\n    border: 1px solid '][f'''{p['ACCENT']}'''][';\n    border-bottom: 1px solid '][f'''{p['CARD_H']}'''][';\n}\nQScrollBar:vertical { background:transparent; width:6px; }\nQScrollBar::handle:vertical { background:'][f'''{p['BORDER']}''']['; border-radius:3px; min-height:30px; }\nQScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height:0px; }\nQRadioButton, QCheckBox { spacing:8px; background:transparent; }\nQRadioButton::indicator, QCheckBox::indicator {\n    width:18px; height:18px;\n    border:2px solid '][f'''{p['BORDER']}''']['; background:'][f'''{p['CARD_H']}'''][';\n    border-radius:9px;\n}\nQCheckBox::indicator { border-radius:4px; }\nQRadioButton::indicator:hover, QCheckBox::indicator:hover { border:2px solid '][f'''{p['ACCENT']}''']['; }\nQRadioButton::indicator:checked {\n    border:2px solid '][f'''{p['ACCENT']}'''][';\n    background: qradialgradient(cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5,\n        stop:0 '][f'''{p['ACCENT']}'''][', stop:0.45 '][f'''{p['ACCENT']}'''][', stop:0.55 '][f'''{p['CARD_H']}'''][', stop:1 '][f'''{p['CARD_H']}'''][');\n}\nQCheckBox::indicator:checked { border:2px solid '][f'''{p['ACCENT']}''']['; background:'][f'''{p['ACCENT']}''']['; }\nQRadioButton::indicator:disabled, QCheckBox::indicator:disabled { opacity:0.4; }\n'])

