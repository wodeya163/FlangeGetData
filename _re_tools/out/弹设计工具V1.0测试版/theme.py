# Reconstructed from bytecode by split_decompile.py
# theme.relaxed.pyc

'''SpringTool 外观主题（token 化，可切换）。

建立背景（2026-10-02）：用户反馈工具「没有质感」，且旧实现把颜色常量硬编码在
spring_ui.py 与 dialogs.py 两个模块顶部（BG/CARD/BORDER/TEXT/TEXT2/ACCENT/…），
改配色等于改代码，无法换肤。本模块把颜色、圆角、字号收敛成 token，主题可切换、
可持久化，后续 KeyTool / BearingTool / MaterialToolbox 可照同一份结构平移。

设计纪律（沿用用户 2026-10-01 三条前提，不因换肤而破坏）：
· 换肤只换 token，不改布局、不新增面板 → 界面复杂度不上升
· 主题名与说明只做客观描述，禁用绝对化措辞（如「最佳/最优」）
· 新增主题必须过 _theme_test.py：token 完整性 + WCAG 对比度 + 持久化回读
'''
import os
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton
REQUIRED_TOKENS = [
    'bg',
    'card',
    'card2',
    'border',
    'text',
    'text2',
    'accent',
    'accent_hover',
    'accent_text',
    'green',
    'orange',
    'red',
    'disabled_bg',
    'disabled_text',
    'font',
    'radius']
_FONT = '"Microsoft YaHei UI", "Microsoft YaHei"'
THEMES = {
    'industrial': {
        'label': '工业暗夜（黄铜）',
        'desc': '深炭底 + 黄铜色强调，对比偏暖，长时间看参数时眼睛负担较小',
        'bg': '#131519',
        'card': '#1b1e24',
        'card2': '#23272f',
        'border': '#2f343e',
        'text': '#e9ebee',
        'text2': '#9aa3b2',
        'accent': '#e0a33e',
        'accent_hover': '#f0b457',
        'accent_text': '#17191d',
        'green': '#6fcf97',
        'orange': '#f0a04b',
        'red': '#ef6b6b',
        'disabled_bg': '#2a2f37',
        'disabled_text': '#7a8391',
        'font': _FONT,
        'radius': '8px' },
    'paper': {
        'label': '晨光纸感（浅色）',
        'desc': '浅米底 + 白卡片 + 靛蓝强调，接近打印出来的校核单，适合截图与投影',
        'bg': '#f4f2ec',
        'card': '#ffffff',
        'card2': '#ffffff',
        'border': '#d6d2c6',
        'text': '#23201b',
        'text2': '#6b6558',
        'accent': '#1f5f8b',
        'accent_hover': '#17496b',
        'accent_text': '#ffffff',
        'green': '#1c6e46',
        'orange': '#9a5f16',
        'red': '#a92f2e',
        'disabled_bg': '#ded9cd',
        'disabled_text': '#6b6659',
        'font': _FONT,
        'radius': '6px' },
    'blueprint': {
        'label': '工程蓝图（深蓝）',
        'desc': '深蓝底 + 青色强调，接近工程图纸配色，线条与数值边界较清楚',
        'bg': '#0e1620',
        'card': '#14202d',
        'card2': '#1b2a3a',
        'border': '#25394d',
        'text': '#dce8f2',
        'text2': '#8ba3ba',
        'accent': '#35b6d9',
        'accent_hover': '#4bc9ea',
        'accent_text': '#06202a',
        'green': '#5fd39a',
        'orange': '#f0a752',
        'red': '#ff7b7b',
        'disabled_bg': '#1e2b39',
        'disabled_text': '#6f8599',
        'font': _FONT,
        'radius': '8px' },
    'graphite': {
        'label': '石墨极简（中性灰）',
        'desc': '低饱和灰阶，强调色接近白，界面里几乎只剩参数与结果本身',
        'bg': '#1a1a1a',
        'card': '#242424',
        'card2': '#2e2e2e',
        'border': '#3b3b3b',
        'text': '#ededed',
        'text2': '#a2a2a2',
        'accent': '#cfd6dd',
        'accent_hover': '#e2e8ee',
        'accent_text': '#141414',
        'green': '#8dc98d',
        'orange': '#e0a95c',
        'red': '#e88383',
        'disabled_bg': '#333333',
        'disabled_text': '#7d7d7d',
        'font': _FONT,
        'radius': '6px' } }
DEFAULT = 'industrial'
_current = DEFAULT

def names():
    return list(THEMES.keys())
def label_of(name):
    return THEMES.get(name, THEMES[DEFAULT])['label']
def current_name():
    return _current if _current in THEMES else DEFAULT
def current():
    return THEMES[current_name()]
def token(key):
    return current()[key]
def is_valid(name):
    return name in THEMES
def _config_path():
    '''配置文件路径。

    优先沿用 dialogs.CONFIG_PATH（测试会整体替换它做目录隔离），取不到时按
    dialogs 的同一套规则推导：SPRINGTOOL_HOME 环境变量 → ~/.SpringTool/config.json。
    主题与解锁状态共用同一个配置文件，重置初态时一并清除。
    '''

    try:
        import dialogs
        p = getattr(dialogs, 'CONFIG_PATH', None)
        if p:
            return p
    except Exception:
        p = None

    base = os.environ.get('SPRINGTOOL_HOME') or os.path.join(os.path.expanduser('~'), '.SpringTool')
    return os.path.join(base, 'config.json')
def load_saved():
    '''读出已保存的主题名；文件不存在或主题名失效时返回 None。'''

    try:
        import json
        with open(_config_path(), 'r', encoding='utf-8-sig') as f:
            cfg = json.load(f)
        name = cfg.get('theme')
    except (OSError, ValueError):
        return None
    return name if is_valid(name) else None
def save(name):
    '''把主题名写进配置文件（合并写入，不影响 first_run / unlocked 等字段）。'''
    import json
    if not is_valid(name):
        return False
    path = _config_path()
    cfg = { }

    try:
        with open(path, 'r', encoding='utf-8-sig') as f:
            cfg = json.load(f)
    except (OSError, ValueError):
        cfg = { }
    cfg['theme'] = name
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
    except OSError:
        return False
    return True
def set_theme(name):
    '''切换当前主题并落盘；主题名无效时不切换，返回是否成功。'''
    global _current
    if not is_valid(name):
        return False
    _current = None
    save(name)
    return True
def init_from_config():
    '''启动时调用：读已保存主题，没有就用默认。'''
    global _current
    saved = load_saved()
    _current = saved if saved else DEFAULT
    return _current
def qss(t, for_dialog):
    '''生成全局样式表。

    for_dialog=True 时输出更精简的一条（对话框背景与文字），避免对话框里
    出现主窗口的 GroupBox 规则影响布局。
    '''
    if not t:
        pass
    t = current()
    r = t['radius']
    common = []['\n        QDialog { background: '][f'''{t['bg']}''']['; }\n        QWidget { background: '][f'''{t['bg']}''']['; color: '][f'''{t['text']}'''][';\n                   font-family: '][f'''{t['font']}''']['; font-size: 13px; }\n        QLabel { color: '][f'''{t['text']}''']['; background: transparent; }\n        QLineEdit, QComboBox, QDoubleSpinBox {\n            background: '][f'''{t['card2']}''']['; color: '][f'''{t['text']}'''][';\n            border: 1px solid '][f'''{t['border']}''']['; border-radius: '][f'''{r}'''][';\n            padding: 5px 10px; min-height: 26px;\n            selection-background-color: '][f'''{t['accent']}'''][';\n            selection-color: '][f'''{t['accent_text']}'''][';\n        }\n        QLineEdit:focus, QComboBox:focus, QDoubleSpinBox:focus {\n            border-color: '][f'''{t['accent']}'''][';\n        }\n        QComboBox QAbstractItemView {\n            background: '][f'''{t['card']}''']['; color: '][f'''{t['text']}'''][';\n            border: 1px solid '][f'''{t['border']}'''][';\n            selection-background-color: '][f'''{t['accent']}'''][';\n            selection-color: '][f'''{t['accent_text']}'''][';\n        }\n        QPushButton {\n            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,\n                stop:0 '][f'''{t['accent_hover']}'''][', stop:1 '][f'''{t['accent']}'''][');\n            color: '][f'''{t['accent_text']}''']['; border: none; border-radius: '][f'''{r}'''][';\n            padding: 8px 18px; font-weight: bold;\n        }\n        QPushButton:hover { background: '][f'''{t['accent_hover']}''']['; }\n        QPushButton:disabled {\n            background: '][f'''{t['disabled_bg']}''']['; color: '][f'''{t['disabled_text']}'''][';\n        }\n        QCheckBox { color: '][f'''{t['text']}''']['; spacing: 8px; }\n        QScrollArea { border: none; background: transparent; }\n        QScrollBar:vertical { background: '][f'''{t['bg']}''']['; width: 10px; margin: 0; }\n        QScrollBar::handle:vertical {\n            background: '][f'''{t['border']}''']['; border-radius: 5px; min-height: 24px;\n        }\n        QToolTip {\n            background: '][f'''{t['card']}''']['; color: '][f'''{t['text']}'''][';\n            border: 1px solid '][f'''{t['border']}''']([]['\n        QDialog { background: '][f'''{t['bg']}''']['; }\n        QWidget { background: '][f'''{t['bg']}''']['; color: '][f'''{t['text']}'''][';\n                   font-family: '][f'''{t['font']}''']['; font-size: 13px; }\n        QLabel { color: '][f'''{t['text']}''']['; background: transparent; }\n        QLineEdit, QComboBox, QDoubleSpinBox {\n            background: '][f'''{t['card2']}''']['; color: '][f'''{t['text']}'''][';\n            border: 1px solid '][f'''{t['border']}''']['; border-radius: '][f'''{r}'''][';\n            padding: 5px 10px; min-height: 26px;\n            selection-background-color: '][f'''{t['accent']}'''][';\n            selection-color: '][f'''{t['accent_text']}'''][';\n        }\n        QLineEdit:focus, QComboBox:focus, QDoubleSpinBox:focus {\n            border-color: '][f'''{t['accent']}'''][';\n        }\n        QComboBox QAbstractItemView {\n            background: '][f'''{t['card']}''']['; color: '][f'''{t['text']}'''][';\n            border: 1px solid '][f'''{t['border']}'''][';\n            selection-background-color: '][f'''{t['accent']}'''][';\n            selection-color: '][f'''{t['accent_text']}'''][';\n        }\n        QPushButton {\n            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,\n                stop:0 '][f'''{t['accent_hover']}'''][', stop:1 '][f'''{t['accent']}'''][');\n            color: '][f'''{t['accent_text']}''']['; border: none; border-radius: '][f'''{r}'''][';\n            padding: 8px 18px; font-weight: bold;\n        }\n        QPushButton:hover { background: '][f'''{t['accent_hover']}''']['; }\n        QPushButton:disabled {\n            background: '][f'''{t['disabled_bg']}''']['; color: '][f'''{t['disabled_text']}'''][';\n        }\n        QCheckBox { color: '][f'''{t['text']}''']['; spacing: 8px; }\n        QScrollArea { border: none; background: transparent; }\n        QScrollBar:vertical { background: '][f'''{t['bg']}''']['; width: 10px; margin: 0; }\n        QScrollBar::handle:vertical {\n            background: '][f'''{t['border']}''']['; border-radius: 5px; min-height: 24px;\n        }\n        QToolTip {\n            background: '][f'''{t['card']}''']['; color: '][f'''{t['text']}'''][';\n            border: 1px solid '][f'''{t['border']}''']['; padding: 4px 6px;\n        }\n    '])
    if for_dialog:
        return common
    return []['\n        QDialog { background: '][f'''{t['bg']}''']['; }\n        QWidget { background: '][f'''{t['bg']}''']['; color: '][f'''{t['text']}'''][';\n                   font-family: '][f'''{t['font']}''']['; font-size: 13px; }\n        QLabel { color: '][f'''{t['text']}''']['; background: transparent; }\n        QLineEdit, QComboBox, QDoubleSpinBox {\n            background: '][f'''{t['card2']}''']['; color: '][f'''{t['text']}'''][';\n            border: 1px solid '][f'''{t['border']}''']['; border-radius: '][f'''{r}'''][';\n            padding: 5px 10px; min-height: 26px;\n            selection-background-color: '][f'''{t['accent']}'''][';\n            selection-color: '][f'''{t['accent_text']}'''][';\n        }\n        QLineEdit:focus, QComboBox:focus, QDoubleSpinBox:focus {\n            border-color: '][f'''{t['accent']}'''][';\n        }\n        QComboBox QAbstractItemView {\n            background: '][f'''{t['card']}''']['; color: '][f'''{t['text']}'''][';\n            border: 1px solid '][f'''{t['border']}'''][';\n            selection-background-color: '][f'''{t['accent']}'''][';\n            selection-color: '][f'''{t['accent_text']}'''][';\n        }\n        QPushButton {\n            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,\n                stop:0 '][f'''{t['accent_hover']}'''][', stop:1 '][f'''{t['accent']}'''][');\n            color: '][f'''{t['accent_text']}''']['; border: none; border-radius: '][f'''{r}'''][';\n            padding: 8px 18px; font-weight: bold;\n        }\n        QPushButton:hover { background: '][f'''{t['accent_hover']}''']['; }\n        QPushButton:disabled {\n            background: '][f'''{t['disabled_bg']}''']['; color: '][f'''{t['disabled_text']}'''][';\n        }\n        QCheckBox { color: '][f'''{t['text']}''']['; spacing: 8px; }\n        QScrollArea { border: none; background: transparent; }\n        QScrollBar:vertical { background: '][f'''{t['bg']}''']['; width: 10px; margin: 0; }\n        QScrollBar::handle:vertical {\n            background: '][f'''{t['border']}''']['; border-radius: 5px; min-height: 24px;\n        }\n        QToolTip {\n            background: '][f'''{t['card']}''']['; color: '][f'''{t['text']}'''][';\n            border: 1px solid '] + f'''\n        QMainWindow {{ background: {t['bg']}; }}\n        QGroupBox {{\n            background: {t['card']};\n            border: 1px solid {t['border']}; border-radius: {r};\n            margin-top: 12px; padding-top: 12px;\n        }}\n        QGroupBox::title {{\n            subcontrol-origin: margin; left: 12px; padding: 0 6px;\n            color: {t['text2']}; font-weight: bold;\n        }}\n        QGroupBox#resultCard {{ border-left: 3px solid {t['accent']}; }}\n    '''
def contrast(hex1, hex2):
    '''WCAG 相对亮度对比度（1~21）。供 _theme_test.py 校验可读性。'''

    def lum(h):
        h = h.lstrip('#')
        c = (0, 2, 4)()
        c = c()
        return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
    b = lum(hex2)
    a = lum(hex1)
    lo = min(a, b)
    hi = max(a, b)
    return (hi + 0.05) / (lo + 0.05)
class ThemeDialog(QDialog):
    '''外观主题选择。

    只切换配色，不改变任何计算行为与数据。选中即生效并落盘，下次启动沿用。
    '''
    SWATCH_KEYS = ('bg', 'card', 'accent', 'text', 'orange')

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('外观主题')
        self.setFixedSize(470, 330)
        t = current()
        self.setStyleSheet(qss(t, for_dialog = True))
        root = QVBoxLayout(self)
        root.setSpacing(10)
        root.setContentsMargins(22, 18, 22, 18)
        self.title_lbl = QLabel('外观主题')
        self.title_lbl.setStyleSheet(f'''color: {t['text']}; font-size: 15px; font-weight: bold;''')
        root.addWidget(self.title_lbl)
        self.note = QLabel('只切换界面配色，不影响计算与数据；选择后立即生效，并记住本次选择。')
        self.note.setWordWrap(True)
        self.note.setStyleSheet(f'''color: {t['text2']}; font-size: 12px;''')
        root.addWidget(self.note)
        self.combo = QComboBox()
        for key in names():
            self.combo.addItem(THEMES[key]['label'], key)
        self.combo.setCurrentIndex(names().index(current_name()))
        root.addWidget(self.combo)
        sw_row = QHBoxLayout()
        self.swatches = []
        for _ in self.SWATCH_KEYS:
            sw = QLabel()
            sw.setFixedSize(58, 30)
            sw_row.addWidget(sw)
            self.swatches.append(sw)
        sw_row.addStretch()
        root.addLayout(sw_row)
        self.desc = QLabel()
        self.desc.setWordWrap(True)
        self.desc.setMinimumHeight(56)
        self.desc.setAlignment(Qt.AlignmentFlag.AlignTop)
        root.addWidget(self.desc)
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        close_btn = QPushButton('关闭')
        close_btn.clicked.connect(self.accept)
        btn_row.addWidget(close_btn)
        root.addLayout(btn_row)
        self.combo.currentIndexChanged.connect(self._on_pick)
        self._on_pick(self.combo.currentIndex())
        return None
    def _on_pick(self, idx):
        key = self.combo.itemData(idx)
        if key not in THEMES:
            return None
        t = THEMES[key]
        self.desc.setText(t['desc'])
        self.desc.setStyleSheet(f'''color: {t['text2']}; font-size: 12px; padding: 8px; background: {t['card']}; border: 1px solid {t['border']}; border-radius: {t['radius']};''')
        self.note.setStyleSheet(f'''color: {t['text2']}; font-size: 12px;''')
        self.title_lbl.setStyleSheet(f'''color: {t['text']}; font-size: 15px; font-weight: bold;''')
        for sw, tk in zip(self.swatches, self.SWATCH_KEYS):
            sw.setStyleSheet(f'''background: {t[tk]}; border: 1px solid {t['border']}; border-radius: 4px;''')
        if key != current_name():
            self.setStyleSheet(qss(t, for_dialog = True))
            set_theme(key)
            parent = self.parent()
            if parent is not None:
                if hasattr(parent, 'apply_theme'):
                    parent.apply_theme(key)
                    return None
                return None
            return None
        return None

