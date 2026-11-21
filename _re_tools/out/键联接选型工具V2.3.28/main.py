# Reconstructed from bytecode by split_decompile.py
# main.relaxed.pyc

'''键联接选型工具 v1.0
Tab1: 智能选型 — 输入轴径+工况→推荐键类型
Tab2: 平键选型 — GB/T 1096-2003, 强度校核
Tab3: 半圆键选型 — GB/T 1099.1-2003
Tab4: 楔键选型 — GB/T 1564/1565-2003
Tab5: 花键选型 — GB/T 1144-2001 矩形花键
'''
import sys
import os
import re
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QTabWidget, QTextEdit, QFrame, QGroupBox, QGridLayout, QMessageBox, QScrollArea, QDialog, QFileDialog, QListWidget, QListWidgetItem, QSpacerItem, QSizePolicy, QStackedWidget, QTableWidget, QTableWidgetItem, QHeaderView
from PySide6.QtCore import Qt, QRect, Signal
from PySide6.QtGui import QFont, QColor, QPainter, QPixmap, QPalette
sys.path.insert(0, os.path.dirname(__file__))
from key_data import VERSION, DATA_SOURCE, get_parallel_key, get_keyway_depth, get_woodruff_key, get_spline, recommend_key_type, calc_parallel_key_strength, calc_parallel_key_strength_shear, calc_woodruff_strength, calc_spline_strength, calc_taper_strength, select_key_length, estimate_hub_width, recommend_woodruff, recommend_spline, KEY_LENGTH_SERIES, ALLOWABLE_STRESS, KEY_TYPES, auto_design, build_design_report, calc_torque_from_power, PARALLEL_FITS, KEY_TOL, suggest_fit, TYPE_TRAITS
from dialogs import WelcomeDialog, LockDialog, is_first_run, is_unlocked, _load_config, _save_config
from drawing import KeySectionFigure, MarginBar, SplineFigure, WoodruffFigure, TaperFigure, FigurePanel
import keylib as KL
import sqlite3

def repolish(w):
    '''objectName 变更后强制重刷 QSS（否则选择器样式不生效）'''
    w.style().unpolish(w)
    w.style().polish(w)
def parse_float(text, name):
    '''统一输入解析：失败抛带字段名的 ValueError（调用方统一弹窗）'''

    try:
        v = float(text)
    except (TypeError, ValueError):
        raise ValueError(f'''「{name}」请输入有效数字''')

    return v
from key_data import THEMES, THEME_ORDER, get_theme_key, set_theme_key
DISCLAIMER = '⚠ 仅供参考，不作为最终设计依据。\n数据来源：GB/T 1096/1099.1/1564/1565/1144/1095 + 机械设计手册推荐值（许用应力取区间下限）。\n实际选型须结合工况、安全系数、加工精度等由专业工程师校核。'
DISCLAIMER_UI = '⚠ 仅供参考，不作为最终设计依据；数据来源：GB/T 1096/1099.1/1564/1565/1144/1095 + 机械设计手册推荐值，实际选型须由专业工程师校核'
CJK_FONT_CHAIN = [
    'Microsoft YaHei',
    '微软雅黑',
    'Noto Sans CJK SC',
    'Source Han Sans SC',
    'WenQuanYi Micro Hei',
    'SimHei',
    'Heiti SC',
    'sans-serif']

def cjk_font(size, bold):
    '''中文字体回退链（2026-10-02，K24）：按可用字体族依次回退，
    全部缺失时退回 Qt 默认字体——避免写死某一字体导致数字/汉字渲染成方块。'''
    QFontDatabase = QFontDatabase
    import PySide6.QtGui

    try:
        fams = set(QFontDatabase.families())
    except Exception:
        fams = set()

    for fam in CJK_FONT_CHAIN:
        if fam in fams:
            f = QFont(fam, size)
            f.setBold(bold)

            return None, f
    f.setPointSize(size)
    f.setBold(bold)
    return f
def margin_note(ratio):
    '''利用率裕度提示（2026-10-02 新增）：85%~100% 之间提示余量偏小。
    只陈述余量，不下指令、不作判定——是否调整由使用者决定。'''

    try:
        r = float(ratio)
    except (TypeError, ValueError):
        return ''

    if r >= 100:
        return ''
    if None >= 85:
        return f'''（余量约 {100 - r:.0f}%，偏小；如需更大裕度，可考虑加长键长或选大规格）'''
def confirm_dup(parent, conn, mark):
    '''入库前查重（2026-10-02，K23）：同标记已存在则如实告知，由使用者决定是否再存。
    不替使用者拍板，也不静默覆盖。'''

    try:
        dup = KL.list_specs(conn, mark)()
    except Exception:
        return True

    if not dup:
        return True
    ans = (lambda .0 = None: [ s for s in .0 if s['mark'] == mark ]).question(parent, '库中已有相同规格', f'''零件库中已有「{mark}」。\n仍要再存一条吗？''', QMessageBox.Yes | QMessageBox.No)
    return ans == QMessageBox.Yes
def build_qss(key):
    '''全局 QSS —— 所有控件样式集中在此，换肤只需重新 setStyleSheet'''
    T = THEMES[key]
    return []['\n    QMainWindow, QDialog {\n        background: '][f'''{T['BG']}'''][';\n    }\n    QLabel {\n        background: transparent;\n        color: '][f'''{T['TEXT_W']}'''][';\n        font-size: 15px;\n    }\n    QLabel#dim { color: '][f'''{T['TEXT_G']}''']['; font-size: 13px; }\n    QLabel#groupTitle { font-size: 15px; font-weight: bold;\n        color: '][f'''{T['TEXT_W']}''']['; background: transparent; }\n    QFrame#card {\n        background: '][f'''{T['CARD_BG']}'''][';\n        border: 1px solid '][f'''{T['BORDER']}'''][';\n        border-radius: 8px;\n    }\n    QLabel#result {\n        color: '][f'''{T['TEXT_W']}'''][";\n        font-size: 15px;\n        font-family: Consolas, 'Microsoft YaHei', 'Noto Sans CJK SC', sans-serif;\n        padding: 12px;\n        background: "][f'''{T['CARD2']}'''][';\n        border: 1px solid '][f'''{T['BORDER']}'''][';\n        border-radius: 6px;\n    }\n    QLabel#resultPlain {\n        color: '][f'''{T['TEXT_G']}'''][';\n        font-size: 15px;\n        padding: 12px;\n        background: '][f'''{T['CARD_BG']}'''][';\n        border: 1px solid '][f'''{T['BORDER']}'''][';\n        border-radius: 8px;\n    }\n    QTextEdit {\n        color: '][f'''{T['TEXT_W']}'''][';\n        background: '][f'''{T['CARD2']}'''][';\n        border: 1px solid '][f'''{T['BORDER']}'''][";\n        border-radius: 6px;\n        font-family: Consolas, 'Microsoft YaHei', 'Noto Sans CJK SC', sans-serif;\n        font-size: 13px;\n    }\n    QLineEdit, QComboBox {\n        background: "][f'''{T['CARD2']}'''][';\n        color: '][f'''{T['TEXT_W']}'''][';\n        border: 1px solid '][f'''{T['BORDER']}'''][';\n        border-radius: 4px;\n        padding: 7px 10px;\n        font-size: 16px;\n        min-height: 24px;\n    }\n    QLineEdit:focus, QComboBox:focus { border: 1px solid '][f'''{T['ACCENT']}''']['; }\n    QComboBox::drop-down {\n        subcontrol-origin: padding;\n        subcontrol-position: center right;\n        width: 28px;\n        border: none;\n    }\n    QComboBox::down-arrow {\n        image: url(data:image/png;base64,'][f'''{ARROW_B64}'''][');\n        width: 12px; height: 12px;\n    }\n    QComboBox QAbstractItemView {\n        background: '][f'''{T['CARD2']}'''][';\n        color: '][f'''{T['TEXT_W']}'''][';\n        border: 1px solid '][f'''{T['BORDER']}'''][';\n        selection-background-color: '][f'''{T['ACCENT']}'''][';\n        font-size: 16px;\n    }\n    QPushButton#primary {\n        background: '][f'''{T['ACCENT']}'''][';\n        color: white;\n        border: none;\n        border-radius: 4px;\n        padding: 9px 22px;\n        font-size: 15px;\n        font-weight: bold;\n    }\n    QPushButton#primary:hover { background: '][f'''{T['HOVER']}''']['; }\n    QPushButton#ghost {\n        background: transparent;\n        color: '][f'''{T['TEXT_W']}'''][';\n        border: 1px solid '][f'''{T['BORDER']}'''][';\n        border-radius: 4px;\n        padding: 9px 22px;\n        font-size: 15px;\n    }\n    QPushButton#ghost:hover { border-color: '][f'''{T['ACCENT']}''']['; color: '][f'''{T['ACCENT_H']}''']['; }\n    QPushButton:disabled {\n        background: transparent;\n        color: '][f'''{T['TEXT_G']}'''][';\n        border: 1px solid '][f'''{T['BORDER']}'''][';\n    }\n    /* 折叠开关/行内小按钮（2026-10-01 页面精简）：比 ghost 矮一半，不撑版面 */\n    QPushButton#mini {\n        background: transparent;\n        color: '][f'''{T['ACCENT_H']}'''][';\n        border: 1px solid '][f'''{T['BORDER']}'''][';\n        border-radius: 4px;\n        padding: 1px 10px;\n        font-size: 13px;\n    }\n    QPushButton#mini:hover { border-color: '][f'''{T['ACCENT']}''']['; }\n    QFrame#modeCard {\n        background: '][f'''{T['CARD2']}'''][';\n        border: 1px solid '][f'''{T['BORDER']}'''][';\n        border-radius: 12px;\n    }\n    QFrame#modeCard:hover { border: 1px solid '][f'''{T['ACCENT']}''']['; }\n    QLabel#cardIcon { font-size: 26px; background: transparent; }\n    QLabel#cardTitle { font-size: 19px; font-weight: bold;\n        color: '][f'''{T['TEXT_W']}''']['; background: transparent; }\n    QLabel#cardDesc { font-size: 14px; color: '][f'''{T['TEXT_G']}''']['; background: transparent; }\n    QLabel#cardFeat { font-size: 13px; color: '][f'''{T['TEXT_G']}''']['; background: transparent; }\n    QLabel#cardGo { font-size: 14px; font-weight: bold;\n        color: '][f'''{T['ACCENT_H']}''']['; background: transparent; }\n    QTabWidget::pane {\n        border: 1px solid '][f'''{T['BORDER']}'''][';\n        border-radius: 6px;\n        background: '][f'''{T['CARD_BG']}'''][';\n    }\n    QTabBar::tab {\n        background: '][f'''{T['CARD2']}'''][';\n        color: '][f'''{T['TEXT_G']}'''][';\n        border: 1px solid '][f'''{T['BORDER']}'''][';\n        border-bottom: none;\n        border-radius: 6px 6px 0 0;\n        padding: 8px 12px;\n        margin-right: 2px;\n        font-size: 14px;\n    }\n    QTabBar::tab:selected {\n        background: '][f'''{T['CARD_BG']}'''][';\n        color: '][f'''{T['ACCENT_H']}'''][';\n        font-weight: bold;\n        border-bottom: 2px solid '][f'''{T['ACCENT']}'''][';\n    }\n    QTabBar::tab:hover { color: '][f'''{T['TEXT_W']}''']['; }\n    QScrollArea { background: transparent; border: none; }\n    QListWidget {\n        background: '][f'''{T['CARD_BG']}'''][';\n        color: '][f'''{T['TEXT_W']}'''][';\n        border: 1px solid '][f'''{T['BORDER']}'''][';\n        border-radius: 6px;\n        font-size: 14px;\n        padding: 4px;\n    }\n    QListWidget::item { padding: 5px 6px; border-radius: 4px; }\n    QListWidget::item:selected {\n        background: '][f'''{T['ACCENT']}'''][';\n        color: white;\n    }\n    QListWidget::item:hover:!selected { background: '][f'''{T['CARD2']}''']['; }\n    QScrollBar:vertical, QScrollBar:horizontal {\n        background: transparent; width: 10px; height: 10px;\n    }\n    QScrollBar::handle {\n        background: '][f'''{T['BORDER']}''']['; border-radius: 5px; min-height: 24px;\n    }\n    QScrollBar::handle:hover { background: '][f'''{T['TEXT_G']}''']['; }\n    QScrollBar::add-line, QScrollBar::sub-line { height: 0; width: 0; }\n    QScrollBar::add-page, QScrollBar::sub-page { background: transparent; }\n    QPushButton#swatch {\n        min-width: 20px; max-width: 20px;\n        min-height: 20px; max-height: 20px;\n        border-radius: 10px;\n        border: 2px solid transparent;\n    }\n    QPushButton#swatch:hover { border: 2px solid '][f'''{T['ACCENT_H']}''']['; }\n    QPushButton#swatch:checked {\n        border: 2px solid '][f'''{T['TEXT_W']}'''][';\n    }\n    QLabel#footer { color: '][f'''{T['TEXT_G']}''']['; font-size: 11px; }\n    QLabel#title { font-size: 18px; font-weight: bold; color: '][f'''{T['TEXT_W']}''']([]['\n    QMainWindow, QDialog {\n        background: '][f'''{T['BG']}'''][';\n    }\n    QLabel {\n        background: transparent;\n        color: '][f'''{T['TEXT_W']}'''][';\n        font-size: 15px;\n    }\n    QLabel#dim { color: '][f'''{T['TEXT_G']}''']['; font-size: 13px; }\n    QLabel#groupTitle { font-size: 15px; font-weight: bold;\n        color: '][f'''{T['TEXT_W']}''']['; background: transparent; }\n    QFrame#card {\n        background: '][f'''{T['CARD_BG']}'''][';\n        border: 1px solid '][f'''{T['BORDER']}'''][';\n        border-radius: 8px;\n    }\n    QLabel#result {\n        color: '][f'''{T['TEXT_W']}'''][";\n        font-size: 15px;\n        font-family: Consolas, 'Microsoft YaHei', 'Noto Sans CJK SC', sans-serif;\n        padding: 12px;\n        background: "][f'''{T['CARD2']}'''][';\n        border: 1px solid '][f'''{T['BORDER']}'''][';\n        border-radius: 6px;\n    }\n    QLabel#resultPlain {\n        color: '][f'''{T['TEXT_G']}'''][';\n        font-size: 15px;\n        padding: 12px;\n        background: '][f'''{T['CARD_BG']}'''][';\n        border: 1px solid '][f'''{T['BORDER']}'''][';\n        border-radius: 8px;\n    }\n    QTextEdit {\n        color: '][f'''{T['TEXT_W']}'''][';\n        background: '][f'''{T['CARD2']}'''][';\n        border: 1px solid '][f'''{T['BORDER']}'''][";\n        border-radius: 6px;\n        font-family: Consolas, 'Microsoft YaHei', 'Noto Sans CJK SC', sans-serif;\n        font-size: 13px;\n    }\n    QLineEdit, QComboBox {\n        background: "][f'''{T['CARD2']}'''][';\n        color: '][f'''{T['TEXT_W']}'''][';\n        border: 1px solid '][f'''{T['BORDER']}'''][';\n        border-radius: 4px;\n        padding: 7px 10px;\n        font-size: 16px;\n        min-height: 24px;\n    }\n    QLineEdit:focus, QComboBox:focus { border: 1px solid '][f'''{T['ACCENT']}''']['; }\n    QComboBox::drop-down {\n        subcontrol-origin: padding;\n        subcontrol-position: center right;\n        width: 28px;\n        border: none;\n    }\n    QComboBox::down-arrow {\n        image: url(data:image/png;base64,'][f'''{ARROW_B64}'''][');\n        width: 12px; height: 12px;\n    }\n    QComboBox QAbstractItemView {\n        background: '][f'''{T['CARD2']}'''][';\n        color: '][f'''{T['TEXT_W']}'''][';\n        border: 1px solid '][f'''{T['BORDER']}'''][';\n        selection-background-color: '][f'''{T['ACCENT']}'''][';\n        font-size: 16px;\n    }\n    QPushButton#primary {\n        background: '][f'''{T['ACCENT']}'''][';\n        color: white;\n        border: none;\n        border-radius: 4px;\n        padding: 9px 22px;\n        font-size: 15px;\n        font-weight: bold;\n    }\n    QPushButton#primary:hover { background: '][f'''{T['HOVER']}''']['; }\n    QPushButton#ghost {\n        background: transparent;\n        color: '][f'''{T['TEXT_W']}'''][';\n        border: 1px solid '][f'''{T['BORDER']}'''][';\n        border-radius: 4px;\n        padding: 9px 22px;\n        font-size: 15px;\n    }\n    QPushButton#ghost:hover { border-color: '][f'''{T['ACCENT']}''']['; color: '][f'''{T['ACCENT_H']}''']['; }\n    QPushButton:disabled {\n        background: transparent;\n        color: '][f'''{T['TEXT_G']}'''][';\n        border: 1px solid '][f'''{T['BORDER']}'''][';\n    }\n    /* 折叠开关/行内小按钮（2026-10-01 页面精简）：比 ghost 矮一半，不撑版面 */\n    QPushButton#mini {\n        background: transparent;\n        color: '][f'''{T['ACCENT_H']}'''][';\n        border: 1px solid '][f'''{T['BORDER']}'''][';\n        border-radius: 4px;\n        padding: 1px 10px;\n        font-size: 13px;\n    }\n    QPushButton#mini:hover { border-color: '][f'''{T['ACCENT']}''']['; }\n    QFrame#modeCard {\n        background: '][f'''{T['CARD2']}'''][';\n        border: 1px solid '][f'''{T['BORDER']}'''][';\n        border-radius: 12px;\n    }\n    QFrame#modeCard:hover { border: 1px solid '][f'''{T['ACCENT']}''']['; }\n    QLabel#cardIcon { font-size: 26px; background: transparent; }\n    QLabel#cardTitle { font-size: 19px; font-weight: bold;\n        color: '][f'''{T['TEXT_W']}''']['; background: transparent; }\n    QLabel#cardDesc { font-size: 14px; color: '][f'''{T['TEXT_G']}''']['; background: transparent; }\n    QLabel#cardFeat { font-size: 13px; color: '][f'''{T['TEXT_G']}''']['; background: transparent; }\n    QLabel#cardGo { font-size: 14px; font-weight: bold;\n        color: '][f'''{T['ACCENT_H']}''']['; background: transparent; }\n    QTabWidget::pane {\n        border: 1px solid '][f'''{T['BORDER']}'''][';\n        border-radius: 6px;\n        background: '][f'''{T['CARD_BG']}'''][';\n    }\n    QTabBar::tab {\n        background: '][f'''{T['CARD2']}'''][';\n        color: '][f'''{T['TEXT_G']}'''][';\n        border: 1px solid '][f'''{T['BORDER']}'''][';\n        border-bottom: none;\n        border-radius: 6px 6px 0 0;\n        padding: 8px 12px;\n        margin-right: 2px;\n        font-size: 14px;\n    }\n    QTabBar::tab:selected {\n        background: '][f'''{T['CARD_BG']}'''][';\n        color: '][f'''{T['ACCENT_H']}'''][';\n        font-weight: bold;\n        border-bottom: 2px solid '][f'''{T['ACCENT']}'''][';\n    }\n    QTabBar::tab:hover { color: '][f'''{T['TEXT_W']}''']['; }\n    QScrollArea { background: transparent; border: none; }\n    QListWidget {\n        background: '][f'''{T['CARD_BG']}'''][';\n        color: '][f'''{T['TEXT_W']}'''][';\n        border: 1px solid '][f'''{T['BORDER']}'''][';\n        border-radius: 6px;\n        font-size: 14px;\n        padding: 4px;\n    }\n    QListWidget::item { padding: 5px 6px; border-radius: 4px; }\n    QListWidget::item:selected {\n        background: '][f'''{T['ACCENT']}'''][';\n        color: white;\n    }\n    QListWidget::item:hover:!selected { background: '][f'''{T['CARD2']}''']['; }\n    QScrollBar:vertical, QScrollBar:horizontal {\n        background: transparent; width: 10px; height: 10px;\n    }\n    QScrollBar::handle {\n        background: '][f'''{T['BORDER']}''']['; border-radius: 5px; min-height: 24px;\n    }\n    QScrollBar::handle:hover { background: '][f'''{T['TEXT_G']}''']['; }\n    QScrollBar::add-line, QScrollBar::sub-line { height: 0; width: 0; }\n    QScrollBar::add-page, QScrollBar::sub-page { background: transparent; }\n    QPushButton#swatch {\n        min-width: 20px; max-width: 20px;\n        min-height: 20px; max-height: 20px;\n        border-radius: 10px;\n        border: 2px solid transparent;\n    }\n    QPushButton#swatch:hover { border: 2px solid '][f'''{T['ACCENT_H']}''']['; }\n    QPushButton#swatch:checked {\n        border: 2px solid '][f'''{T['TEXT_W']}'''][';\n    }\n    QLabel#footer { color: '][f'''{T['TEXT_G']}''']['; font-size: 11px; }\n    QLabel#title { font-size: 18px; font-weight: bold; color: '][f'''{T['TEXT_W']}''']['; }\n    '])
def _make_arrow_png():
    '''生成16x16灰色三角下拉箭头 PNG base64'''
    Image = Image
    import PIL
    import io
    import base64
    img = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    px = img.load()
    for y in range(4, 12):
        x_start = 8 - (y - 4) // 2
        x_end = 8 + (y - 4) // 2 + 1
        for x in range(max(0, x_start), min(16, x_end)):
            px[(x, y)] = (150, 150, 150, 255)
            buf = io.BytesIO()
            img.save(buf, format = 'PNG')
            return base64.b64encode(buf.getvalue()).decode()
ARROW_B64 = _make_arrow_png()

def styled_combo(items):
    '''创建下拉框（样式由全局 QSS 统一驱动）'''
    combo = QComboBox()
    combo.addItems(items)
    combo.setCursor(Qt.CursorShape.PointingHandCursor)
    return combo
def styled_input(placeholder, width):
    '''创建输入框（样式由全局 QSS 统一驱动）'''
    le = QLineEdit()
    le.setPlaceholderText(placeholder)
    le.setFixedWidth(width)
    return le
def styled_button(text, primary):
    '''创建按钮（样式由全局 QSS 统一驱动）'''
    btn = QPushButton(text)
    btn.setObjectName('primary' if primary else 'ghost')
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    return btn
def mini_button(text):
    '''行内小按钮（折叠开关等，2026-10-01）：高度约 ghost 的一半，不撑版面'''
    btn = styled_button(text, primary = False)
    btn.setObjectName('mini')
    return btn
class _WrapLabel:
    '''带 wordWrap 且高度随宽度自适应的 QLabel。

    修复：QScrollArea(widgetResizable) 内嵌套 QFrame 时，QLabel 的
    heightForWidth 不传播到外层 sizeHint，文字会被裁切/叠压。
    inset：stylesheet padding/边框占用的横向宽度（实际换行宽度比控件窄，
    按全宽算行数会少算行 → 文字溢出叠压）；
    pad：stylesheet padding/边框占用的纵向高度补偿。
    '''

    def __init__(self, text, dim, pad, inset):
        super().__init__(text)
        self.setWordWrap(True)
        self._pad = pad
        self._inset = inset
        if dim:
            self.setObjectName('dim')
            return None
    def resizeEvent(self, e):
        super().resizeEvent(e)
        w = max(20, self.width() - self._inset)
        self.setMinimumHeight(self.heightForWidth(w) + self._pad)
    __classcell__ = None
class SmartTab:

    def __init__(self):
        super().__init__()
        self._shared_conn = None
        self._last_d = None
        self._last_text = ''
        self._build_ui()
        self._update_placeholder()
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        input_frame = QFrame()
        input_frame.setObjectName('card')
        input_col = QVBoxLayout(input_frame)
        input_col.setContentsMargins(12, 10, 12, 10)
        input_col.setSpacing(8)
        top_row = QHBoxLayout()
        top_row.setSpacing(10)
        top_row.addWidget(QLabel('轴径 d (mm):'))
        self.d_input = styled_input('例: 30', 150)
        top_row.addWidget(self.d_input)
        top_row.addSpacing(10)
        top_row.addWidget(QLabel('传递扭矩 T (N·m):'))
        self.t_input = styled_input('例: 50', 150)
        top_row.addWidget(self.t_input)
        top_row.addStretch()
        self.query_btn = styled_button('智能推荐')
        self.query_btn.clicked.connect(self._do_query)
        top_row.addWidget(self.query_btn)
        input_col.addLayout(top_row)
        self._adv_open = False
        self.adv_btn = mini_button('更改参数 ▾')
        self.adv_btn.clicked.connect(self._toggle_adv)
        self.adv_btn.setToolTip('展开可改：载荷性质、轮毂材料、轴向移动、对中要求、轴向力、轮毂宽度')
        self.adv_sum = QLabel('')
        adv_row = QHBoxLayout()
        adv_row.setSpacing(10)
        adv_row.addWidget(self.adv_btn)
        adv_row.addWidget(self.adv_sum)
        adv_row.addStretch()
        input_col.addLayout(adv_row)
        self.adv_panel = QWidget()
        input_layout = QGridLayout(self.adv_panel)
        input_layout.setContentsMargins(0, 2, 0, 0)
        input_layout.setSpacing(8)
        input_layout.addWidget(QLabel('载荷性质:'), 0, 0)
        self.load_combo = styled_combo([
            '静载荷',
            '轻微冲击',
            '冲击'])
        input_layout.addWidget(self.load_combo, 0, 1)
        input_layout.addWidget(QLabel('轮毂材料:'), 0, 2)
        self.material_combo = styled_combo([
            '钢',
            '铸铁'])
        input_layout.addWidget(self.material_combo, 0, 3)
        input_layout.addWidget(QLabel('需要轴向移动:'), 1, 0)
        self.axial_combo = styled_combo([
            '否',
            '是'])
        input_layout.addWidget(self.axial_combo, 1, 1)
        input_layout.addWidget(QLabel('对中性要求:'), 1, 2)
        self.precision_combo = styled_combo([
            '一般',
            '高'])
        input_layout.addWidget(self.precision_combo, 1, 3)
        input_layout.addWidget(QLabel('需承受轴向力:'), 2, 0)
        self.axforce_combo = styled_combo([
            '否',
            '是'])
        self.axforce_combo.setToolTip('楔键可同时承受单向轴向力；选「是」时工具会重新评估楔键适用性')
        input_layout.addWidget(self.axforce_combo, 2, 1)
        input_layout.addWidget(QLabel('轮毂宽度 B (mm，可空):'), 2, 2)
        self.hub_input = styled_input('空 = 按 4×键宽估', 150)
        self.hub_input.setToolTip('键长受轮毂宽度约束；填了它，键长/强度设计按真实毂宽算，留空则按键宽 4 倍估算')
        input_layout.addWidget(self.hub_input, 2, 3)
        input_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum), 0, 4)
        self.adv_panel.setVisible(False)
        input_col.addWidget(self.adv_panel)
        for c in (self.load_combo, self.material_combo, self.axial_combo, self.precision_combo, self.axforce_combo):
            c.currentTextChanged.connect(self._sync_adv_summary)
            self.hub_input.textChanged.connect(self._sync_adv_summary)
            self._sync_adv_summary()
            layout.addWidget(input_frame)
            self.out_host = QWidget()
            self.out_host.setObjectName('outHost')
            self.out_host.setStyleSheet('QWidget#outHost{background:transparent;}')
            self.out_layout = QVBoxLayout(self.out_host)
            self.out_layout.setContentsMargins(0, 0, 0, 0)
            self.out_layout.setSpacing(8)
            placeholder = QLabel('查询步骤：① 填轴径与工况 → ② 点「智能推荐」\n\n给出：推荐键型与完整方案（规格·标记·槽深·配合公差带）、四种键型在当前工况下的适用性对比矩阵、强度校核，并可一键把推荐方案存入零件库\n\n示例：轴径 45 mm、扭矩 200 N·m、轻微冲击 → 推荐 A 型普通平键')
            placeholder.setWordWrap(True)
            placeholder.setAlignment(Qt.AlignLeft | Qt.AlignTop)
            placeholder.setObjectName('resultPlain')
            self.out_layout.addWidget(placeholder)
            self.out_layout.addStretch()
            out_scroll = QScrollArea()
            out_scroll.setWidgetResizable(True)
            out_scroll.setFrameShape(QFrame.NoFrame)
            out_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            out_scroll.setStyleSheet('QScrollArea{background:transparent;border:none;}')
            out_scroll.setWidget(self.out_host)
            layout.addWidget(out_scroll, 1)
            return None
    def _toggle_adv(self):
        self._adv_open = not (self._adv_open)
        self.adv_panel.setVisible(self._adv_open)
        self.adv_btn.setText('收起参数 ▴' if self._adv_open else '更改参数 ▾')
    def _adv_values(self):
        return {
            'load': self.load_combo.currentText(),
            'material': self.material_combo.currentText(),
            'axial': self.axial_combo.currentText(),
            'precision': self.precision_combo.currentText(),
            'axforce': self.axforce_combo.currentText(),
            'hub': self.hub_input.text().strip() }
    def _sync_adv_summary(self, *a):
        '''收起状态也要能一眼看到当前工况；有改动→变色提示，避免"改了却忘了" '''
        v = self._adv_values()
        parts = [
            v['load'],
            v['material'],
            '需轴向移动' if v['axial'] == '是' else '无轴向移动',
            '高对中' if v['precision'] == '高' else '一般对中',
            '需承受轴向力' if v['axforce'] == '是' else '无轴向力']
        if v['hub']:
            parts.append('毂宽 %s mm' % v['hub'])
        if not v['load'] != '静载荷' and v['material'] != '钢' and v['axial'] != '否' and v['precision'] != '一般' and v['axforce'] != '否':
            pass
        changed = bool(v['hub'])
        th = THEMES[get_theme_key()]
        self.adv_sum.setText('已改工况：' if changed else '默认工况：' + ' · '.join(parts))
        self.adv_sum.setStyleSheet('color:%s;' % th['ACCENT_H'] if changed else th['TEXT_G'])
    VERDICT_TXT = {
        'suit': '✔ 适用',
        'ok': '○ 可用',
        'no': '✘ 不适用' }

    def _clear_output(self):
        pass


    def _toggle_compare(self):
        '''键型对比矩阵：默认收起，点开才占版面（页面精简）'''
        self._cmp_open = not getattr(self, '_cmp_open', False)
        self.compare_table.setVisible(self._cmp_open)
        self.compare_btn.setText(self._cmp_label(self._cmp_open))
    def _cmp_label(self, open_):
        '''对比开关文案：按本次实际参与的键型数报数（不同工况推荐条数不同）'''
        return '键型对比（%d 种）%s' % (getattr(self, '_cmp_n', 0), '▴' if open_ else '▾')
    def _mk_result_card(self, top, mark, kv_rows, why_lines, weak, badge):
        '''选型结果卡（2026-10-01 呈现重做）：说人话、分层次。

            ① 一句话结论（键型 + 状态徽章）② 规格标记大字 ③ 加工参数两列表
            ④ 为什么是它。沿用固定行不换行纪律（防 heightForWidth 叠压），
            技术长句放 tooltip 不刷屏。W8g/W8h 锁定标题文案。
            '''
        th = THEMES[get_theme_key()]
        frame = QFrame()
        frame.setStyleSheet(f'''QFrame{{background:{th['CARD2']!s};border:1px solid {th['BORDER']!s};border-radius:8px;}}''')
        v = QVBoxLayout(frame)
        v.setContentsMargins(14, 10, 14, 10)
        v.setSpacing(4)
        trow = QWidget()
        h = QHBoxLayout(trow)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(10)
        title = QLabel(f'''推荐方案：{top['name']!s}　{'⚠ 强度不足' if weak else '✔ 适用'!s}''')
        tf = cjk_font(12)
        tf.setBold(True)
        title.setFont(tf)
        if weak:
            title.setStyleSheet('color:%s;' % th['DANGER'])
        h.addWidget(title)
        if badge:
            (btxt, bcol) = badge
            bl = QLabel(btxt)
            bl.setStyleSheet('color:%s;' % bcol)
            bf = cjk_font(10)
            bf.setBold(True)
            bl.setFont(bf)
            h.addStretch()
            h.addWidget(bl)
        v.addWidget(trow)
        if mark:
            mk = QLabel(mark)
            mf = cjk_font(13)
            mf.setBold(True)
            mk.setFont(mf)
            mk.setStyleSheet('color:%s;' % th['ACCENT_H'])
            v.addWidget(mk)
        if kv_rows:
            g = QGridLayout()
            g.setHorizontalSpacing(18)
            g.setVerticalSpacing(2)
            g.setContentsMargins(0, 1, 0, 1)
            for r, item in enumerate(kv_rows):
                lab = QLabel(item[0])
                lab.setStyleSheet('color:%s;' % th['TEXT_G'])
                g.addWidget(lab, r, 0)
                valw = QLabel(item[1])
                if len(item) > 2:
                    valw.setToolTip(item[2])
                g.addWidget(valw, r, 1)
                v.addLayout(g)
                if why_lines:
                    head = QLabel('为什么是它')
                    head.setStyleSheet('color:%s;' % th['TEXT_G'])
                    v.addWidget(head)
                    for seg in why_lines:
                        v.addWidget(QLabel(seg))
                        return frame
    _plain_stress = (lambda ratio: pass)()
    _chain_row = (lambda s: pass)()

    def _mk_strength_card(self, T, rows, foot):
        '''强度校核卡（2026-10-01 呈现重做）：每个候选方案一行，
            结果说人话（百分比/倍数），精确数值放悬停提示。'''
        th = THEMES[get_theme_key()]
        frame = QFrame()
        frame.setObjectName('strengthCard')
        frame.setStyleSheet(f'''QFrame{{background:{th['CARD_BG']!s};border:1px solid {th['BORDER']!s};border-radius:8px;}}''')
        v = QVBoxLayout(frame)
        v.setContentsMargins(14, 9, 14, 9)
        v.setSpacing(4)
        head = QLabel('按扭矩 %g N·m 逐级试算' % T / 1000)
        hf = cjk_font(11)
        hf.setBold(True)
        head.setFont(hf)
        v.addWidget(head)
        for short, ok, plain, tip in rows:
            row = QWidget()
            rh = QHBoxLayout(row)
            rh.setContentsMargins(8, 0, 0, 0)
            rh.setSpacing(10)
            icon = QLabel('✅' if ok else '❌')
            rh.addWidget(icon)
            name = QLabel(short)
            rh.addWidget(name)
            rh.addStretch()
            res = QLabel(plain)
            res.setStyleSheet('color:%s;' % th['GREEN'] if ok else th['DANGER'])
            fnt = cjk_font(10)
            fnt.setBold(True)
            res.setFont(fnt)
            rh.addWidget(res)
            row.setToolTip(tip)
            v.addWidget(row)
            if foot:
                (ftxt, fcol) = foot
                fl = QLabel('校核结论：' + ftxt)
                fl.setStyleSheet('color:%s;' % fcol)
                fnt2 = cjk_font(10)
                fnt2.setBold(True)
                fl.setFont(fnt2)
                v.addWidget(fl)
        return frame
    def _mk_compare_table(self, recs, weak_type):
        '''对比矩阵：键型 × 当前工况适用性 + 通用属性'''
        cols = [
            '键型',
            '当前工况',
            '定心精度',
            '承载能力',
            '装拆便利',
            '轴向固定',
            '相对成本']
        t = QTableWidget(len(recs), len(cols))
        t.setHorizontalHeaderLabels(cols)
        t.verticalHeader().setVisible(False)
        t.setEditTriggers(QTableWidget.NoEditTriggers)
        t.setSelectionMode(QTableWidget.NoSelection)
        t.setAlternatingRowColors(True)
        t.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        t.horizontalHeader().setStretchLastSection(True)
        th = THEMES[get_theme_key()]
        verdict_color = {
            'suit': QColor(th['GREEN']),
            'ok': QColor(th['WARN']),
            'no': QColor(th['DANGER']) }
        for r, rec in enumerate(recs):
            traits = TYPE_TRAITS.get(rec['type'], ('-', '-', '-', '-', '-'))
            if weak_type is not None:
                pass
            is_weak_top = rec['type'] == weak_type
            verdict_txt = '适用 / ⚠强度不足' if is_weak_top else self.VERDICT_TXT[rec['verdict']]
            vals = [
                rec['name'],
                verdict_txt] + list(traits)
            for c, val in enumerate(vals):
                it = QTableWidgetItem(val)
                if c == 1:
                    it.setForeground(verdict_color['ok' if is_weak_top else rec['verdict']])
                    f = it.font()
                    f.setBold(True)
                    it.setFont(f)
                t.setItem(r, c, it)
                t.setToolTip('通用属性列提炼自机械设计手册·轴上零件周向定位方法表；当前工况列由你填写的条件判定')
                t.verticalHeader().setDefaultSectionSize(30)
                t.setMinimumHeight(t.rowCount() * 30 + 42)
                return t
    def _mk_top_figure(self, top, d, hub_w, design):
        '''按推荐键型生成联接示意图（数据不全/无键长时返回 None，不硬凑）'''

        try:
            if top['type'] in ('parallel', 'guided'):
                (b, h) = get_parallel_key(d)
                if not b:
                    return None
                (t1, t2) = None(d)
                hub_use = hub_w if hub_w else estimate_hub_width(b)
                ch = design['chosen'] if not design is None else None
                L = ch['L'] if ch is None and ch.get('kind') == 'parallel' else select_key_length(b, hub_use)
                if not L is None or t1:
                    return None
                fig = None()
                fig.set_params(d, b, h, t1, t2, L, hub_use, mark = '键 %g×%g×%g' % (b, h, L))
                return fig
            if None['type'] == 'taper':
                (b, h) = get_parallel_key(d)
                if not b:
                    return None
                hub_use = None(b)
                L = select_key_length(b, hub_use, 'taper')
                if not L is not None:
                    return None
                fig = None()
                fig.set_params(d, b, h, L, hub_use, hook = False, mark = '键 %g×%g GB/T 1564-2003' % (b, L))
                return fig
            if None['type'] == 'woodruff':
                wk = get_woodruff_key(d)
                if not wk:
                    return None
                (code, b, h, d1) = None[0]
                fig = WoodruffFigure()
                fig.set_params(d, b, h, d1, code = code)
                return fig
            if None['type'] == 'spline':
                sp = get_spline(d)
                if not sp:
                    return None
                (spec, N, d_sm, D, B) = None[0]
                fig = SplineFigure()
                fig.set_params(N, d_sm, D, B, mark = spec)
                return fig
        except Exception:
            return None
            return None
    def _mk_action_row(self, top_rec):
        row_w = QWidget()
        h = QHBoxLayout(row_w)
        h.setContentsMargins(0, 0, 0, 0)
        btn_lib = styled_button('把推荐方案存入零件库')
        None((lambda _ = None, r = None: self._save_to_lib(r)))
        btn_copy = styled_button('复制结果', primary = False)
        btn_copy.clicked.connect(self._copy_result)
        h.addWidget(btn_lib)
        h.addWidget(btn_copy)
        h.addStretch()
        return row_w
    def _save_to_lib(self, rec):
        '''把首推方案写入零件库（由推荐键型构造完整规格）'''
        d = self._last_d

        try:
            if rec['type'] in ('parallel', 'guided'):
                (b, h) = get_parallel_key(d)
                if not b:
                    raise ValueError(f'''轴径 {d}mm 无对应平键规格（GB/T 1096 覆盖 >6~500mm）''')
                (t1, t2) = get_keyway_depth(d)
                L = select_key_length(b, estimate_hub_width(b))
                if not L is not None:
                    raise ValueError('毂宽按经验估算后仍选不出标准键长，请到平键页手工确认')
                mark = f'''键 {b:g}×{h:g}×{L:g}'''
                if not confirm_dup(self, self._lib_conn(), mark):
                    return None
                if not t1:
                    pass
                if not t2:
                    pass
                sid = None.add_spec(self._lib_conn(), mark, d, b, h, L, 0, 0, key_type = '平键', std_ref = 'GB/T 1096-2003', note = '智能选型推荐方案')
            elif rec['type'] == 'taper':
                (b, h) = get_parallel_key(d)
                if not b:
                    raise ValueError(f'''轴径 {d}mm 无对应楔键截面''')
                L = select_key_length(b, estimate_hub_width(b), 'taper')
                if not L is not None:
                    raise ValueError('选不出标准键长，请到楔键页手工确认')
                mark = f'''键 {b:g}×{L:g}'''
                if not confirm_dup(self, self._lib_conn(), mark):
                    return None
                sid = None.add_spec(self._lib_conn(), mark, d, b, h, L, 0, 0, key_type = '楔键', std_ref = 'GB/T 1564-2003', note = '智能选型推荐方案')
            elif rec['type'] == 'woodruff':
                wk = get_woodruff_key(d)
                if not wk:
                    raise ValueError(f'''轴径 {d}mm 无对应半圆键规格''')
                (code, b, h, d1) = wk[0]
                mark = f'''键 {b:g}×{d1:g}'''
                if not confirm_dup(self, self._lib_conn(), mark):
                    return None
                sid = None.add_spec(self._lib_conn(), mark, d, b, h, 0, 0, 0, key_type = '半圆键', std_ref = 'GB/T 1099.1-2003', note = f'''智能选型推荐方案（型号 {code}）''')
            else:
                sp = get_spline(d)
                if not sp:
                    raise ValueError(f'''轴径 {d}mm ±2mm 内无对应矩形花键规格（GB/T 1144）''')
                (spec, N, d_sm, D, B) = sp[0]
                mark = spec
                sid = KL.add_spec(self._lib_conn(), spec, d_sm, B, 0, 0, 0, 0, key_type = '花键', std_ref = 'GB/T 1144-2001', note = '智能选型推荐方案')
        except ValueError:
            e = None
            QMessageBox.warning(self, '无法存入', str(e))
            e = None
            del e
            return None
            e = None
            del e

        QMessageBox.information(self, '已存入零件库', f'''标记「{mark}」已存入零件库。\n\n在「零件库 → 规格管理」中可查看示意图并补充供应商/备注。''')
    def _lib_conn(self):
        return self._shared_conn
    def _copy_result(self):
        if getattr(self, '_last_text', ''):
            QApplication.clipboard().setText(self._last_text)
            return None
    def _update_placeholder(self):
        pass
    def _do_query(self):
        pass

    __classcell__ = staticmethod
    return staticmethod
class DesignTab:

    def __init__(self):
        super().__init__()
        self._last_auto = None
        self._last_params = None
        self._build_ui()
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)
        input_frame = QFrame()
        input_frame.setObjectName('card')
        g = QGridLayout(input_frame)
        g.setSpacing(10)
        g.addWidget(QLabel('扭矩来源:'), 0, 0)
        self.src_combo = styled_combo([
            '直接输扭矩',
            '功率 P + 转速 n'])
        self.src_combo.currentIndexChanged.connect(self._on_src_change)
        g.addWidget(self.src_combo, 0, 1)
        self.lbl_t = QLabel('扭矩 T (N·m):')
        g.addWidget(self.lbl_t, 0, 2)
        self.t_input = styled_input('例: 200', 150)
        g.addWidget(self.t_input, 0, 3)
        self.lbl_p = QLabel('功率 P (kW):')
        g.addWidget(self.lbl_p, 1, 0)
        self.p_input = styled_input('例: 7.5', 150)
        g.addWidget(self.p_input, 1, 1)
        self.lbl_n = QLabel('转速 n (r/min):')
        g.addWidget(self.lbl_n, 1, 2)
        self.n_input = styled_input('例: 960', 150)
        g.addWidget(self.n_input, 1, 3)
        g.addWidget(QLabel('轴径 d (mm):'), 2, 0)
        self.d_input = styled_input('例: 45', 150)
        g.addWidget(self.d_input, 2, 1)
        g.addWidget(QLabel('轮毂宽度 (mm):'), 2, 2)
        self.hub_input = styled_input('例: 70', 150)
        g.addWidget(self.hub_input, 2, 3)
        g.addWidget(QLabel('轮毂材料:'), 3, 0)
        self.mat_combo = styled_combo([
            '钢',
            '铸铁'])
        g.addWidget(self.mat_combo, 3, 1)
        g.addWidget(QLabel('载荷性质:'), 3, 2)
        self.load_combo = styled_combo([
            '静载荷',
            '轻微冲击',
            '冲击'])
        g.addWidget(self.load_combo, 3, 3)
        g.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum), 0, 4)
        layout.addWidget(input_frame)
        btn_row = QHBoxLayout()
        self.design_btn = styled_button('自动设计')
        self.design_btn.clicked.connect(self._do_design)
        btn_row.addWidget(self.design_btn)
        self.report_btn = styled_button('生成设计计算书', primary = False)
        self.report_btn.setEnabled(False)
        self.report_btn.clicked.connect(self._do_report)
        btn_row.addWidget(self.report_btn)
        self.copy_btn = styled_button('复制计算书', primary = False)
        self.copy_btn.setEnabled(False)
        self.copy_btn.clicked.connect(self._do_copy)
        btn_row.addWidget(self.copy_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)
        self.result_scroll = QScrollArea()
        self.result_scroll.setWidgetResizable(True)
        self.result_scroll.setFrameShape(QFrame.NoFrame)
        self.result_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.result_scroll.setStyleSheet('QScrollArea{background:transparent;border:none;}')
        out_host = QWidget()
        out_host.setObjectName('designOutHost')
        out_host.setStyleSheet('QWidget#designOutHost{background:transparent;}')
        ov = QVBoxLayout(out_host)
        ov.setContentsMargins(0, 0, 0, 0)
        ov.setSpacing(8)
        self.result_label = QLabel('设计步骤：① 选扭矩来源（直接输扭矩 / 功率+转速）→ ② 填轴径与毂宽 → ③ 点「自动设计」\n\n示例：扭矩 200 N·m、轴径 45 mm、毂宽 70 mm → 自动选出键并校核强度，不够时自动升级方案（改键型 / 加长 / 双键）\n\n设计结果与可复制的计算书将显示在此处')
        self.result_label.setWordWrap(True)
        self.result_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.result_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        self.result_label.setObjectName('resultPlain')
        ov.addWidget(self.result_label)
        self.fig_panel = FigurePanel(title = '联接示意图')
        ov.addWidget(self.fig_panel)
        self.report_box = QTextEdit()
        self.report_box.setReadOnly(True)
        self.report_box.setVisible(False)
        self.report_box.setFont(QFont('Consolas', 10))
        self.report_box.setFixedHeight(420)
        ov.addWidget(self.report_box)
        ov.addStretch()
        self.result_scroll.setWidget(out_host)
        layout.addWidget(self.result_scroll, 1)
        self._on_src_change()
    def _on_src_change(self):
        by_power = self.src_combo.currentIndex() == 1
        self.lbl_t.setVisible(not by_power)
        self.t_input.setVisible(not by_power)
        self.lbl_p.setVisible(by_power)
        self.p_input.setVisible(by_power)
        self.lbl_n.setVisible(by_power)
        self.n_input.setVisible(by_power)
    def _get_T_nmm(self):
        if self.src_combo.currentIndex() == 1:
            P = parse_float(self.p_input.text(), '功率 P')
            n = parse_float(self.n_input.text(), '转速 n')
            if P <= 0 or n <= 0:
                raise ValueError('功率/转速必须为正数')
            return calc_torque_from_power(P, n)
        return None(self.t_input.text(), '扭矩 T') * 1000
    def _do_design(self):
        pass


    def _do_report(self):
        if not self._last_auto:
            return None
        (d, T, hub, material, load) = None._last_params
        report = build_design_report(d, T, hub, material, load, self._last_auto)
        self.report_box.setPlainText(report)
        self.result_label.setVisible(False)
        self.report_box.setVisible(True)
        self.copy_btn.setEnabled(True)
    def _do_copy(self):
        QApplication.clipboard().setText(self.report_box.toPlainText())
        QMessageBox.information(self, '已复制', '设计计算书已复制到剪贴板')
    __classcell__ = None
class ParallelKeyTab:

    def __init__(self):
        super().__init__()
        self._build_ui()
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)
        input_frame = QFrame()
        input_frame.setObjectName('card')
        g = QGridLayout(input_frame)
        g.setSpacing(10)
        g.addWidget(QLabel('轴径 d (mm):'), 0, 0)
        self.d_input = styled_input('例: 30', 120)
        g.addWidget(self.d_input, 0, 1)
        g.addWidget(QLabel('轮毂宽度 (mm):'), 0, 2)
        self.hub_input = styled_input('例: 50', 120)
        g.addWidget(self.hub_input, 0, 3)
        g.addWidget(QLabel('传递扭矩 T (N·m):'), 1, 0)
        self.t_input = styled_input('例: 50', 120)
        g.addWidget(self.t_input, 1, 1)
        g.addWidget(QLabel('轮毂材料:'), 1, 2)
        self.mat_combo = styled_combo([
            '钢',
            '铸铁'])
        g.addWidget(self.mat_combo, 1, 3)
        g.addWidget(QLabel('载荷性质:'), 2, 0)
        self.load_combo = styled_combo([
            '静载荷',
            '轻微冲击',
            '冲击'])
        g.addWidget(self.load_combo, 2, 1)
        g.addWidget(QLabel('键型号:'), 2, 2)
        self.type_combo = styled_combo([
            'A型(圆头)',
            'B型(方头)',
            'C型(单圆头)'])
        g.addWidget(self.type_combo, 2, 3)
        g.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum), 0, 4)
        layout.addWidget(input_frame)
        btn_row = QHBoxLayout()
        query_btn = styled_button('查询键尺寸 + 强度校核')
        query_btn.clicked.connect(self._do_query)
        btn_row.addWidget(query_btn)
        save_lib_btn = styled_button('存入零件库', primary = False)
        save_lib_btn.clicked.connect(self._save_to_library)
        btn_row.addWidget(save_lib_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)
        self.result_label = QLabel('输入参数后查询。\n\n示例：轴径 45、毂宽 50 → 键 14×9×45（GB/T 1096），附挤压 / 剪切强度校核与径向 + 轴向双视图')
        self.result_label.setWordWrap(True)
        self.result_label.setObjectName('resultPlain')
        result_scroll = QScrollArea()
        result_scroll.setWidgetResizable(True)
        result_scroll.setFrameShape(QFrame.NoFrame)
        result_scroll.setStyleSheet('QScrollArea{background:transparent;border:none;}')
        content = QWidget()
        content.setObjectName('resultContent')
        content.setStyleSheet('QWidget#resultContent{background:transparent;}')
        v = QVBoxLayout(content)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(10)
        self.figure = KeySectionFigure()
        self.figure.setVisible(False)
        v.addWidget(self.figure)
        self.bar_p = MarginBar()
        self.bar_p.setVisible(False)
        v.addWidget(self.bar_p)
        self.bar_s = MarginBar()
        self.bar_s.setVisible(False)
        v.addWidget(self.bar_s)
        v.addWidget(self.result_label)
        v.addStretch()
        result_scroll.setWidget(content)
        layout.addWidget(result_scroll, 1)
    def _do_query(self):

        try:
            d = parse_float(self.d_input.text(), '轴径')
            T = parse_float(self.t_input.text(), '扭矩') * 1000 if self.t_input.text().strip() else 0
            _b0 = get_parallel_key(d)[0]
            if self.hub_input.text().strip():
                pass
            elif _b0:
                pass

            hub_w = d
        except ValueError:
            e = parse_float(self.hub_input.text(), '轮毂宽度')
            QMessageBox.warning(self, '输入错误', str(e))
            e = None
            del e
            return None
            e = None
            del e

        QMessageBox.warning(self, '输入错误', '轴径范围 0~500mm')
        return None
        if T < 0 or hub_w <= 0:
            QMessageBox.warning(self, '输入错误', '扭矩不能为负、轮毂宽度必须为正')
            return None
        self.load_combo.currentText() = None if not  < 0, d or 0, d <= 500 else parse_float(self.hub_input.text(), '轮毂宽度').mat_combo.currentText()
        (b, h) = get_parallel_key(d)
        if not b:
            self.result_label.setText(f'''轴径 {d}mm 超出平键标准范围''')
            return None
        (t1, t2) = None(d)
        key_l = select_key_length(b, hub_w)
        lines = []
        lines.append('━━━ GB/T 1096-2003 平键选型结果 ━━━')
        lines.append(f'''''')
        lines.append(f'''轴径: {d}mm''')
        lines.append(f'''键截面: b×h = {b}×{h} mm''')
        lines.append(f'''键槽深度: 轴槽 t1={t1}mm, 毂槽 t2={t2}mm''')
        if not key_l is not None:
            lines.append(f'''轮毂宽度: {hub_w}mm → 选不出标准键长（毂宽过小，建议 ≥ 键宽 {b}mm + 8mm）''')
        else:
            lines.append(f'''轮毂宽度: {hub_w}mm → 建议键长 L = {key_l}mm''')
        lines.append(f'''''')
        type_names = {
            'A型(圆头)': 'A',
            'B型(方头)': 'B',
            'C型(单圆头)': 'C' }
        type_code = type_names.get(self.type_combo.currentText(), 'A')
        head = '' if type_code == 'A' else type_code
        if not key_l is not None:
            mark = f'''键{head} {b}×{h}×L(键长待定) GB/T 1096-2003'''
        else:
            mark = f'''键{head} {b}×{h}×{key_l} GB/T 1096-2003'''
        lines.append(f'''标记示例: {mark}''')
        lines.append(f'''''')
        if not T > 0 and key_l is None:
            res = calc_parallel_key_strength(d, b, h, key_l, T, material, load_type)
            shear = calc_parallel_key_strength_shear(d, b, key_l, T)
            lines.append('━━━ 强度校核 ━━━')
            rel_p = '≤' if res['safe'] else '＞'
            lines.append(f'''挤压强度: σp = {res['sigma_p']} MPa  {rel_p} [{res['allowable']}] MPa''')
            lines.append(f'''  接触高度 k = {res['k']}mm, 工作长度 l = {res['l']}mm''')
            lines.append(f'''  结果: {'✓ 满足' if res['safe'] else '✗ 强度不足!'}  (利用率 {res['ratio']}%)''' + margin_note(res['ratio']))
            lines.append(f'''''')
            rel_s = '≤' if shear['safe'] else '＞'
            lines.append(f'''剪切强度: τ = {shear['tau']} MPa  {rel_s} [{shear['allowable']}] MPa''')
            lines.append(f'''  结果: {'✓ 满足' if shear['safe'] else '✗ 强度不足!'}  (利用率 {shear['ratio']}%)''' + margin_note(shear['ratio']))
            lines.append(f'''''')
            if not res['safe']:
                lines.append('⚠ 挤压强度不足，建议：')
                lines.append(f'''  1. 增加键长（当前{key_l}mm）''')
                lines.append('  2. 采用双键180°布置（按1.5个键校核）')
                lines.append('  3. 改用花键联接')
            elif T > 0:
                lines.append('（键长未定，强度校核跳过——请加大轮毂宽度后重查）')
                lines.append(f'''''')
        lines.append('')
        lines.append(DISCLAIMER)
        self.result_label.setText('\n'.join(lines))
        self.result_label.setObjectName('result')
        repolish(self.result_label)
        self._last = dict(d = d, b = b, h = h, t1 = t1, t2 = t2, L = key_l, type_code = type_code, hub_w = hub_w)
        if not key_l is None:
            self.figure.set_params(d, b, h, t1, t2, key_l, hub_w, mark = '键 %g×%g×%g' % (b, h, key_l))
            self.figure.setVisible(True)
        else:
            self.figure.setVisible(False)
        if not T > 0 and key_l is None:
            self.bar_p.set_value('挤压 σp', res['sigma_p'], res['allowable'])
            self.bar_s.set_value('剪切 τ', shear['tau'], shear['allowable'])
            self.bar_p.setVisible(True)
            self.bar_s.setVisible(True)
            return None
        None.bar_p.setVisible(False)
        self.bar_s.setVisible(False)
    def _save_to_library(self):
        if not getattr(self, '_last', None):
            QMessageBox.information(self, '提示', '请先执行一次查询')
            return None
        q = None._last
        if not q.get('L'):
            QMessageBox.information(self, '键长未定', '本次查询未选出标准键长（毂宽过小），暂不存库；请加大轮毂宽度后重新查询再存')
            return None
        if None['type_code'] == 'A':
            mark = f'''键 {q['b']}×{q['h']}×{q['L']} GB/T 1096-2003'''
        else:
            mark = f'''键{q['type_code']} {q['b']}×{q['h']}×{q['L']} GB/T 1096-2003'''
        _conn = KL.connect()

        try:
            dup = KL.list_specs(_conn, mark)()
            if dup:
                ans = QMessageBox.question(self, '可能重复', f'''零件库中已有「{mark}」，\n仍要再存一条吗？''', QMessageBox.Yes | QMessageBox.No)
                if ans != QMessageBox.Yes:
                    _conn.close()
                    return None

                try:
                    KL.add_spec(_conn, mark, q['d'], q['b'], q['h'], q['L'], q['t1'], q['t2'], '平键', 'GB/T 1096-2003', None, f'''由平键查询页存入（轴径{q['d']}）''')

                    try:
                        pass
                    except ValueError:
                        e = None
                        QMessageBox.warning(self, '保存失败', str(e))

                        try:
                            e = None
                            del e
                            _conn.close()
                            return None
                            e = None
                            del e

                            try:
                                _conn.close()
                            except:
                                _conn.close()

                            QMessageBox.information(self, '已保存', f'''「{mark}」已存入零件库''')
                            return None
    __classcell__ = None
class WoodruffKeyTab:

    def __init__(self):
        super().__init__()
        self._build_ui()
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)
        input_frame = QFrame()
        input_frame.setObjectName('card')
        g = QGridLayout(input_frame)
        g.setSpacing(10)
        g.addWidget(QLabel('轴径 d (mm):'), 0, 0)
        self.d_input = styled_input('例: 20', 120)
        g.addWidget(self.d_input, 0, 1)
        g.addWidget(QLabel('传递扭矩 T (N·m):'), 0, 2)
        self.t_input = styled_input('例: 10', 120)
        g.addWidget(self.t_input, 0, 3)
        g.addWidget(QLabel('轮毂材料:'), 1, 0)
        self.mat_combo = styled_combo([
            '钢',
            '铸铁'])
        g.addWidget(self.mat_combo, 1, 1)
        g.addWidget(QLabel('载荷性质:'), 1, 2)
        self.load_combo = styled_combo([
            '静载荷',
            '轻微冲击',
            '冲击'])
        g.addWidget(self.load_combo, 1, 3)
        g.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum), 0, 4)
        layout.addWidget(input_frame)
        btn_row = QHBoxLayout()
        query_btn = styled_button('查询半圆键 + 强度校核')
        query_btn.clicked.connect(self._do_query)
        btn_row.addWidget(query_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)
        self.result_label = QLabel('输入参数后查询。\n\n示例：轴径 20 → 命中半圆键 2.5×3.7×10、5×9×22 等多个规格，全部列出供选择；查询结果附强度校核')
        self.result_label.setWordWrap(True)
        self.result_label.setObjectName('resultPlain')
        result_scroll = QScrollArea()
        result_scroll.setWidgetResizable(True)
        result_scroll.setFrameShape(QFrame.NoFrame)
        result_scroll.setStyleSheet('QScrollArea{background:transparent;border:none;}')
        content = QWidget()
        content.setObjectName('resultContent')
        content.setStyleSheet('QWidget#resultContent{background:transparent;}')
        cv = QVBoxLayout(content)
        cv.setContentsMargins(0, 0, 0, 0)
        cv.addWidget(self.result_label)
        self.fig_panel = FigurePanel(title = '联接示意图')
        cv.addWidget(self.fig_panel)
        cv.addStretch()
        result_scroll.setWidget(content)
        layout.addWidget(result_scroll, 1)
    def _do_query(self):

        try:
            d = parse_float(self.d_input.text(), '轴径')
            T = parse_float(self.t_input.text(), '扭矩') * 1000 if self.t_input.text().strip() else 0
        except ValueError:
            e = None
            QMessageBox.warning(self, '输入错误', str(e))
            e = None
            del e
            return None
            e = None
            del e

        if not  < 0, d or 0, d <= 500:
            pass

        QMessageBox.warning(self, '输入错误', '轴径范围 0~500mm')
        return None
        if T < 0:
            QMessageBox.warning(self, '输入错误', '扭矩不能为负')
            return None
        self.load_combo.currentText() = None.mat_combo.currentText()
        keys = recommend_woodruff(d)
        if not keys:
            self.result_label.setText(f'''轴径 {d}mm 无匹配的半圆键规格''')
            self.fig_panel.set_figure(None)
            return None
        lines = None
        lines.append('━━━ GB/T 1099.1-2003 半圆键选型结果 ━━━')
        lines.append(f'''''')
        lines.append(f'''轴径: {d}mm''')
        lines.append(f'''''')
        lines.append(f'''{'键号':<15} {'b':>5} {'h':>5} {'d1':>5}  适用轴径''')
        lines.append(f'''{'───────────────'} {'─────'} {'─────'} {'─────'}  {'───────────────'}''')
        for k in keys:
            lines.append(f'''{k['code']:<15} {k['b']:>5} {k['h']:>5} {k['d1']:>5}  {k['d_range']}''')
            if T > 0:
                lines.append(f'''''')
                lines.append('━━━ 强度校核（试算规格见下） ━━━')
                best = keys[-1]
                res = calc_woodruff_strength(d, best['b'], best['h'], best['d1'], T, material, load_type)
                lines.append(f'''键号: {best['code']}''')
                lines.append(f'''挤压应力: σp = {res['sigma_p']} MPa  {'≤' if res['safe'] else '＞'} [{res['allowable']}] MPa''')
                lines.append(f'''接触高度 k = {res['k']}mm, 工作长度 l ≈ {res['l']}mm''')
                lines.append(f'''  工作长度 l ≈ d1/2 = {res['l']}mm（半圆弦长近似，GB/T 1099.1 半圆键）''')
                lines.append(f'''结果: {'✓ 满足' if res['safe'] else '✗ 强度不足!'}  (利用率 {res['ratio']}%)''' + margin_note(res['ratio']))
        lines.append('')
        lines.append(DISCLAIMER)
        self.result_label.setText('\n'.join(lines))
        self.result_label.setObjectName('result')
        repolish(self.result_label)
        wk_show = best if T > 0 else keys[0]
        fig = WoodruffFigure()
        fig.set_params(d, wk_show['b'], wk_show['h'], wk_show['d1'], code = wk_show['code'])
        self.fig_panel.set_figure(fig, summary = '键号 %s（b×h×d1）' % wk_show['code'])
    __classcell__ = None
class TaperKeyTab:

    def __init__(self):
        super().__init__()
        self._build_ui()
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)
        input_frame = QFrame()
        input_frame.setObjectName('card')
        g = QGridLayout(input_frame)
        g.setSpacing(10)
        g.addWidget(QLabel('轴径 d (mm):'), 0, 0)
        self.d_input = styled_input('例: 30', 120)
        g.addWidget(self.d_input, 0, 1)
        g.addWidget(QLabel('轮毂宽度 (mm):'), 0, 2)
        self.hub_input = styled_input('例: 50', 120)
        g.addWidget(self.hub_input, 0, 3)
        g.addWidget(QLabel('传递扭矩 T (N·m):'), 1, 0)
        self.t_input = styled_input('例: 50', 120)
        g.addWidget(self.t_input, 1, 1)
        g.addWidget(QLabel('轮毂材料:'), 1, 2)
        self.mat_combo = styled_combo([
            '钢',
            '铸铁'])
        g.addWidget(self.mat_combo, 1, 3)
        g.addWidget(QLabel('楔键类型:'), 2, 0)
        self.type_combo = styled_combo([
            '普通楔键(A型)',
            '普通楔键(B型)',
            '钩头楔键'])
        g.addWidget(self.type_combo, 2, 1)
        g.addWidget(QLabel('载荷性质:'), 2, 2)
        self.load_combo = styled_combo([
            '静载荷',
            '轻微冲击',
            '冲击'])
        g.addWidget(self.load_combo, 2, 3)
        g.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum), 0, 4)
        layout.addWidget(input_frame)
        btn_row = QHBoxLayout()
        query_btn = styled_button('查询楔键 + 强度校核')
        query_btn.clicked.connect(self._do_query)
        btn_row.addWidget(query_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)
        self.result_label = QLabel('输入参数后查询。\n\n示例：轴径 45 → 楔键截面 14×9（GB/T 1564），自动选键长并校核；1:100 斜度打紧后靠摩擦传递扭矩')
        self.result_label.setWordWrap(True)
        self.result_label.setObjectName('resultPlain')
        result_scroll = QScrollArea()
        result_scroll.setWidgetResizable(True)
        result_scroll.setFrameShape(QFrame.NoFrame)
        result_scroll.setStyleSheet('QScrollArea{background:transparent;border:none;}')
        content = QWidget()
        content.setObjectName('resultContent')
        content.setStyleSheet('QWidget#resultContent{background:transparent;}')
        cv = QVBoxLayout(content)
        cv.setContentsMargins(0, 0, 0, 0)
        cv.addWidget(self.result_label)
        self.fig_panel = FigurePanel(title = '联接示意图')
        cv.addWidget(self.fig_panel)
        cv.addStretch()
        result_scroll.setWidget(content)
        layout.addWidget(result_scroll, 1)
    def _do_query(self):

        try:
            d = parse_float(self.d_input.text(), '轴径')
            T = parse_float(self.t_input.text(), '扭矩') * 1000 if self.t_input.text().strip() else 0
            _b0 = get_parallel_key(d)[0]
            if self.hub_input.text().strip():
                pass
            elif _b0:
                pass

            hub_w = d
        except ValueError:
            e = parse_float(self.hub_input.text(), '轮毂宽度')
            QMessageBox.warning(self, '输入错误', str(e))
            e = None
            del e
            return None
            e = None
            del e

        QMessageBox.warning(self, '输入错误', '轴径范围 0~500mm')
        return None
        if T < 0 or hub_w <= 0:
            QMessageBox.warning(self, '输入错误', '扭矩不能为负、轮毂宽度必须为正')
            return None
        self.load_combo.currentText() = None if not  < 0, d or 0, d <= 500 else parse_float(self.hub_input.text(), '轮毂宽度').mat_combo.currentText()
        key_type = self.type_combo.currentText()
        (b, h) = get_parallel_key(d)
        if not b:
            self.result_label.setText(f'''轴径 {d}mm 超出楔键标准范围''')
            self.fig_panel.set_figure(None)
            return None
        key_l = None(b, hub_w, 'taper_hook' if '钩头' in key_type else 'taper')
        lines = []
        lines.append('━━━ GB/T 1564/1565-2003 楔键选型结果 ━━━')
        lines.append(f'''''')
        lines.append(f'''轴径: {d}mm''')
        lines.append(f'''键截面: b×h = {b}×{h} mm (斜度 1:100)''')
        if not key_l is not None:
            lines.append(f'''轮毂宽度: {hub_w}mm → 选不出标准键长（毂宽过小，建议 ≥ 键宽 {b}mm + 8mm）''')
        else:
            lines.append(f'''轮毂宽度: {hub_w}mm → 建议键长 L = {key_l}mm''')
        lines.append(f'''''')
        if '钩头' in key_type:
            mark = f'''键 {b}×{key_l} GB/T 1565-2003''' if not key_l is None else f'''键 {b}×L(键长待定) GB/T 1565-2003'''
        elif 'B型' in key_type:
            pass

        head = ''
        mark = f'''键{head} {b}×{key_l} GB/T 1564-2003''' if not key_l is None else f'''键{head} {b}×L(键长待定) GB/T 1564-2003'''
        lines.append(f'''标记示例: {mark}''')
        lines.append(f'''''')
        lines.append('特点:')
        lines.append('  • 上下面为工作面，1:100斜度')
        lines.append('  • 靠摩擦力传递扭矩，可承受单方向轴向力')
        lines.append('  • 对中性较差，不宜用于高速精密传动')
        lines.append('  • 装配后接触面积应≥70%')
        if not T > 0 and key_l is None:
            res = calc_taper_strength(d, b, key_l, T, material, load_type)
            lines.append(f'''''')
            lines.append('━━━ 强度校核（楔键标准公式） ━━━')
            lines.append(f'''σp = 12T/[b·l·(6μd+b)], μ={res['mu']}''')
            lines.append(f'''挤压应力: σp = {res['sigma_p']} MPa  {'≤' if res['safe'] else '＞'} [{res['allowable']}] MPa''')
            lines.append(f'''工作长度 l = {res['l']}mm''')
            lines.append(f'''结果: {'✓ 满足' if res['safe'] else '✗ 强度不足!'}  (利用{res['ratio']:.1f}%)''' + margin_note(res['ratio']))
        lines.append('')
        lines.append(DISCLAIMER)
        self.result_label.setText('\n'.join(lines))
        self.result_label.setObjectName('result')
        repolish(self.result_label)
        if not key_l is not None:
            self.fig_panel.set_figure(None)
            return None
        hook = 'B' in key_type
        fig = TaperFigure()
        fig.set_params(d, b, h, key_l, hub_w, hook = hook, mark = mark)
        self.fig_panel.set_figure(fig, summary = '钩头楔键' if hook else '普通楔键' + ' %g×%g，L=%g mm' % (b, h, key_l))
    __classcell__ = None
class SplineTab:

    def __init__(self):
        super().__init__()
        self._build_ui()
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)
        input_frame = QFrame()
        input_frame.setObjectName('card')
        g = QGridLayout(input_frame)
        g.setSpacing(10)
        g.addWidget(QLabel('轴径 d (mm):'), 0, 0)
        self.d_input = styled_input('例: 42', 120)
        g.addWidget(self.d_input, 0, 1)
        g.addWidget(QLabel('传递扭矩 T (N·m):'), 0, 2)
        self.t_input = styled_input('例: 100', 120)
        g.addWidget(self.t_input, 0, 3)
        g.addWidget(QLabel('轮毂材料:'), 1, 0)
        self.mat_combo = styled_combo([
            '钢',
            '铸铁'])
        g.addWidget(self.mat_combo, 1, 1)
        g.addWidget(QLabel('载荷性质:'), 1, 2)
        self.load_combo = styled_combo([
            '静载荷',
            '轻微冲击',
            '冲击'])
        g.addWidget(self.load_combo, 1, 3)
        g.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum), 0, 4)
        self._adv_open = False
        adv_row = QHBoxLayout()
        self.adv_btn = mini_button('更改参数 ▾')
        self.adv_btn.clicked.connect(self._toggle_adv)
        self.adv_btn.setToolTip('展开可改：定心方式、齿面热处理')
        self.adv_sum = QLabel('')
        self.adv_sum.setObjectName('hint')
        adv_row.addWidget(self.adv_btn)
        adv_row.addWidget(self.adv_sum)
        adv_row.addStretch()
        g.addLayout(adv_row, 2, 0, 1, 4)
        self.adv_panel = QWidget()
        ag = QGridLayout(self.adv_panel)
        ag.setContentsMargins(0, 0, 0, 0)
        ag.setSpacing(10)
        ag.addWidget(QLabel('定心方式:'), 0, 0)
        self.center_combo = styled_combo([
            '小径定心',
            '大径定心',
            '齿侧定心'])
        ag.addWidget(self.center_combo, 0, 1)
        ag.addWidget(QLabel('齿面热处理:'), 0, 2)
        self.heat_combo = styled_combo([
            '未热处理',
            '已热处理'])
        self.heat_combo.setToolTip('花键许用压强按齿面是否热处理分档（成大先《联接与紧固》表4.3-29）')
        ag.addWidget(self.heat_combo, 0, 3)
        self.adv_panel.setVisible(False)
        g.addWidget(self.adv_panel, 3, 0, 1, 4)
        for c in (self.center_combo, self.heat_combo):
            c.currentTextChanged.connect(self._sync_adv_summary)
            self._sync_adv_summary()
            layout.addWidget(input_frame)
            btn_row = QHBoxLayout()
            query_btn = styled_button('查询花键 + 强度校核')
            query_btn.clicked.connect(self._do_query)
            btn_row.addWidget(query_btn)
            btn_row.addStretch()
            layout.addLayout(btn_row)
            self.result_label = QLabel('输入参数后查询。\n\n示例：小径 36 → 矩形花键 8×36×40×7（GB/T 1144 轻系列），附齿面挤压强度校核')
            self.result_label.setWordWrap(True)
            self.result_label.setObjectName('resultPlain')
            result_scroll = QScrollArea()
            result_scroll.setWidgetResizable(True)
            result_scroll.setFrameShape(QFrame.NoFrame)
            result_scroll.setStyleSheet('QScrollArea{background:transparent;border:none;}')
            content = QWidget()
            content.setObjectName('resultContent')
            content.setStyleSheet('QWidget#resultContent{background:transparent;}')
            cv = QVBoxLayout(content)
            cv.setContentsMargins(0, 0, 0, 0)
            cv.addWidget(self.result_label)
            self.fig_panel = FigurePanel(title = '联接示意图')
            cv.addWidget(self.fig_panel)
            cv.addStretch()
            result_scroll.setWidget(content)
            layout.addWidget(result_scroll, 1)
            return None
    def _toggle_adv(self):
        self._adv_open = not (self._adv_open)
        self.adv_panel.setVisible(self._adv_open)
        self.adv_btn.setText('收起参数 ▴' if self._adv_open else '更改参数 ▾')
    def _sync_adv_summary(self, *a):
        '''折叠面板收起时，一行摘要如实反映当前值（改动过才标出来）'''
        center = self.center_combo.currentText()
        heat = self.heat_combo.currentText()
        if not center != '小径定心':
            pass
        changed = heat != '未热处理'
        self.adv_sum.setText('已改：' if changed else '默认：' + f'''{center}／{heat}''')
    def _do_query(self):

        try:
            d = parse_float(self.d_input.text(), '轴径')
            T = parse_float(self.t_input.text(), '扭矩') * 1000 if self.t_input.text().strip() else 0
        except ValueError:
            e = None
            QMessageBox.warning(self, '输入错误', str(e))
            e = None
            del e
            return None
            e = None
            del e

        if not  < 0, d or 0, d <= 500:
            pass

        QMessageBox.warning(self, '输入错误', '轴径范围 0~500mm')
        return None
        if T < 0:
            QMessageBox.warning(self, '输入错误', '扭矩不能为负')
            return None
        self.load_combo.currentText() = None.mat_combo.currentText()
        center = self.center_combo.currentText()
        splines = recommend_spline(d)
        if not splines:
            self.result_label.setText(f'''轴径 {d}mm 附近无匹配的矩形花键规格''')
            self.fig_panel.set_figure(None)
            return None
        heat = None.heat_combo.currentText()
        lines = []
        lines.append('━━━ GB/T 1144-2001 矩形花键（轻系列）选型结果 ━━━')
        lines.append(f'''''')
        lines.append(f'''轴径: {d}mm, 定心方式: {center}, 齿面: {heat}''')
        lines.append(f'''''')
        lines.append(f'''{'规格':<18} {'齿数N':>6} {'小径d':>6} {'大径D':>6} {'键宽B':>6}''')
        lines.append(f'''{'──────────────────'} {'──────'} {'──────'} {'──────'} {'──────'}''')
        for sp in splines:
            lines.append(f'''{sp['spec']:<18} {sp['N']:>6} {sp['d']:>6} {sp['D']:>6} {sp['B']:>6}''')
            if T > 0:
                lines.append(f'''''')
                lines.append('━━━ 强度校核（试算规格见下） ━━━')
                best = splines[0]
                res = calc_spline_strength(d, best['N'], best['d'], best['D'], best['B'], T, material, load_type, heat = heat)
                lines.append(f'''规格: {best['spec']}（轻系列）''')
                lines.append(f'''工作齿高: h = {res['h']}mm = (D−d)/2''')
                lines.append(f'''结合长度: l = {res['l']}mm（未填毂宽时按 4×键宽 B 估算）''')
                lines.append(f'''平均直径: d_m = {res['d_m']}mm = (D+d)/2''')
                lines.append(f'''载荷不均系数: ψ = {res['psi']}''')
                lines.append(f'''挤压应力: p = {res['sigma_p']} MPa  {'≤' if res['safe'] else '＞'} [{res['allowable']}] MPa''')
                lines.append(f'''许用取值: {res['allow_src']}；口径=静联接/{heat}/使用情况「{res['usage']}」（由载荷性质映射）''')
                lines.append(f'''结果: {'✓ 满足' if res['safe'] else '✗ 强度不足!'}  (利用{res['ratio']:.1f}%)''' + margin_note(res['ratio']))
        lines.append('')
        lines.append(DISCLAIMER)
        self.result_label.setText('\n'.join(lines))
        self.result_label.setObjectName('result')
        repolish(self.result_label)
        sp_show = best if T > 0 else splines[0]
        fig = SplineFigure()
        fig.set_params(sp_show['N'], sp_show['d'], sp_show['D'], sp_show['B'], mark = sp_show['spec'])
        self.fig_panel.set_figure(fig, summary = '规格 %s（轻系列）' % sp_show['spec'])
    __classcell__ = None
class SpecCard:
    '''库总览卡片：一条规格 = 一张卡（键型徽标 + 标记 + 关键尺寸）'''
    clicked = Signal(int)
    KT_COLOR = {
        '平键': 'ACCENT',
        '半圆键': 'GREEN',
        '楔键': 'ORANGE',
        '花键': 'ACCENT_H' }

    def __init__(self, s, parent):
        super().__init__(parent)
        self.spec_id = s['id']
        self.setObjectName('card')
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip('点击进入规格管理并选中此记录')
        th = THEMES[get_theme_key()]
        if not s['key_type']:
            pass
        color = th[self.KT_COLOR.get('平键', 'ACCENT')]
        v = QVBoxLayout(self)
        v.setContentsMargins(12, 10, 12, 10)
        v.setSpacing(5)
        head = QHBoxLayout()
        if not s['key_type']:
            pass
        badge = QLabel('平键')
        badge.setFont(cjk_font(8, bold = True))
        badge.setStyleSheet('QLabel{color:#fff;background:%s;border-radius:8px;padding:1px 8px;}' % color)
        head.addWidget(badge)
        head.addStretch()
        std_lbl = QLabel(s['std_ref'])
        std_lbl.setObjectName('dim')
        head.addWidget(std_lbl)
        v.addLayout(head)
        mark = QLabel(s['mark'])
        mark.setFont(cjk_font(12, bold = True))
        mark.setWordWrap(True)
        v.addWidget(mark)
        if s['key_type'] == '花键':
            params = f'''小径 d={s['d']:g}  齿宽 B={s['b']:g}'''
        else:
            segs = [
                f'''d={s['d']:g}''',
                f'''b={s['b']:g}''']
            if s['h']:
                segs.append(f'''h={s['h']:g}''')
            if s['L']:
                segs.append(f'''L={s['L']:g}''')
            params = '  '.join(segs)
        p_lbl = QLabel(params)
        p_lbl.setObjectName('dim')
        v.addWidget(p_lbl)
        if s['note']:
            note = QLabel(s['note'])
            note.setObjectName('dim')
            note.setWordWrap(True)
            v.addWidget(note)
            return None
    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.clicked.emit(self.spec_id)
        super().mouseReleaseEvent(e)
    __classcell__ = None
class OverviewTab:
    '''库总览：统计条 + 卡片墙，直观查看自己录入的全部规格'''
    request_open_spec = Signal(int)

    def __init__(self, lib_tab):
        super().__init__()
        self.lib = lib_tab
        self._build_ui()
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(15, 15, 15, 15)
        root.setSpacing(10)
        tip = QLabel('这里是你录入的全部规格总览，点任意卡片可进入「规格管理」编辑')
        tip.setObjectName('dim')
        root.addWidget(tip)
        self.stat_row = QHBoxLayout()
        self.stat_row.setSpacing(8)
        root.addLayout(self.stat_row)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setStyleSheet('QScrollArea{background:transparent;border:none;}')
        self.cards_host = QWidget()
        self.cards_host.setObjectName('cardsHost')
        self.cards_host.setStyleSheet('QWidget#cardsHost{background:transparent;}')
        self.grid = QGridLayout(self.cards_host)
        self.grid.setSpacing(10)
        self.scroll.setWidget(self.cards_host)
        root.addWidget(self.scroll, 1)
    def refresh(self):
        specs = KL.list_specs(self.lib.conn)
        counts = { }
        for s in specs:
            if not s['key_type']:
                pass
            kt = '平键'
            counts[kt] = counts.get(kt, 0) + 1
            if self.stat_row.count():
                it = self.stat_row.takeAt(0)
                if it.widget():
                    it.widget().hide()
                    it.widget().deleteLater()
                if not self.stat_row.count():
                    th = THEMES[get_theme_key()]
                    stat_defs = (lambda .0: [ (kt, n, SpecCard.KT_COLOR.get(kt, 'ACCENT')) for kt, n in .0 ]) + counts.items()()
                    for name, n, ckey in stat_defs:
                        card = QFrame()
                        card.setObjectName('card')
                        cv = QVBoxLayout(card)
                        cv.setContentsMargins(12, 6, 12, 6)
                        cv.setSpacing(0)
                        num = QLabel(str(n))
                        num.setFont(cjk_font(14, bold = True))
                        num.setAlignment(Qt.AlignCenter)
                        cv.addWidget(num)
                        lbl = QLabel(name)
                        lbl.setObjectName('dim')
                        lbl.setAlignment(Qt.AlignCenter)
                        cv.addWidget(lbl)
                        card.setMaximumWidth(110)
                        self.stat_row.addWidget(card)
                        self.stat_row.addStretch()
                        if self.grid.count():
                            it = self.grid.takeAt(0)
                            if it.widget():
                                it.widget().hide()
                                it.widget().deleteLater()
                            if not self.grid.count():
                                for i, s in enumerate(specs):
                                    card = SpecCard(s)
                                    card.clicked.connect(self.request_open_spec)
                                    self.grid.addWidget(card, i // 3, i % 3)
                                    for col in range(3):
                                        self.grid.setColumnStretch(col, 1)
        self.grid.setRowStretch(len(specs) // 3 + 1 if len(specs) % 3 else 0, 1)
        if not specs:
            empty = QLabel('还没有录入任何规格。\n\n切到「规格管理」页签 → 新增规格 → 只填轴径 → 按标准自动填充，录好的规格会出现在这里。')
            empty.setObjectName('dim')
            empty.setAlignment(Qt.AlignCenter)
            self.grid.addWidget(empty, 0, 0, 1, 3)
            return None
        return self.grid.count()
    __classcell__ = None
class LibraryTab:
    STD_DISPLAY = {
        'GB/T 1096-2003': 'GB/T 1096',
        'GB/T 1564-2003': 'GB/T 1564',
        'GB/T 1099.1-2003': 'GB/T 1099.1',
        'GB/T 1144-2001': 'GB/T 1144' }
    STD_STORE = {
        'GB/T 1096': 'GB/T 1096-2003',
        'GB/T 1564': 'GB/T 1564-2003',
        'GB/T 1099.1': 'GB/T 1099.1-2003',
        'GB/T 1144': 'GB/T 1144-2001' }

    def __init__(self):
        super().__init__()
        self.conn = KL.connect()
        self._spec_id = None
        self._loading = False
        self._mark_user_edited = False
        self._build_ui()
        None((lambda : setattr(self, '_mark_user_edited', True)))
        self.refresh_all()
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(15, 15, 15, 15)
        root.setSpacing(10)
        tools = QHBoxLayout()
        self.search_input = styled_input('搜索标记/备注/标准…', 190)
        self.search_input.textChanged.connect(self.refresh_list)
        tools.addWidget(self.search_input)
        self.type_filter = QComboBox()
        self.type_filter.addItems([
            '全部类型',
            '平键',
            '半圆键',
            '楔键',
            '花键'])
        self.type_filter.currentIndexChanged.connect(self.refresh_list)
        tools.addWidget(QLabel('键型筛选:'))
        tools.addWidget(self.type_filter)
        tools.addStretch()
        for text, slot in (('导出CSV', self._export_csv), ('备份库', self._backup), ('恢复库', self._restore)):
            b = styled_button(text, primary = False)
            b.clicked.connect(slot)
            tools.addWidget(b)
            root.addLayout(tools)
            body = QHBoxLayout()
            body.setSpacing(10)
            tip = QLabel('新手三步：① 左下「新增规格」 → ② 只填「轴径」 → ③ 点「按标准自动填充」，其余尺寸自动算出，最后「另存为新规格」入库')
            tip.setObjectName('dim')
            tip.setWordWrap(True)
            root.addWidget(tip)
            left = QVBoxLayout()
            self.listw = QListWidget()
            self.listw.setFixedWidth(210)
            self.listw.currentRowChanged.connect(self._on_select)
            left.addWidget(self.listw)
            row = QHBoxLayout()
            b_new = styled_button('新增规格')
            b_new.clicked.connect(self._new_blank)
            b_del = styled_button('删除', primary = False)
            b_del.clicked.connect(self._delete_current)
            row.addWidget(b_new)
            row.addWidget(b_del)
            left.addLayout(row)
            body.addLayout(left)
            detail_scroll = QScrollArea()
            detail_scroll.setWidgetResizable(True)
            detail_scroll.setFrameShape(QFrame.NoFrame)
            detail_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            detail_scroll.setStyleSheet('QScrollArea{background:transparent;border:none;}')
            self.detail = QWidget()
            self.detail.setObjectName('libDetail')
            self.detail.setStyleSheet('QWidget#libDetail{background:transparent;}')
            v = QVBoxLayout(self.detail)
            v.setContentsMargins(0, 0, 0, 0)
            v.setSpacing(8)
            self.figure = KeySectionFigure()
            self.figure.setMinimumHeight(340)
            self.spline_figure = SplineFigure()
            self.fig_stack = QStackedWidget()
            self.fig_stack.addWidget(self.figure)
            self.fig_stack.addWidget(self.spline_figure)
            self.fig_stack.setMaximumHeight(430)
            v.addWidget(self.fig_stack)
            base_frame = QFrame()
            base_frame.setObjectName('card')
            bv = QVBoxLayout(base_frame)
            bv.setSpacing(6)
            t1_lbl = QLabel('① 基本信息（先选键型，必填只有轴径）')
            t1_lbl.setObjectName('groupTitle')
            bv.addWidget(t1_lbl)
            bg = QGridLayout()
            bg.setSpacing(6)
            self.f = { }
            bg.addWidget(QLabel('键型:'), 0, 0)
            self.f['key_type'] = QComboBox()
            self.f['key_type'].addItems([
                '平键',
                '半圆键',
                '楔键',
                '花键'])
            self.f['key_type'].setFixedWidth(110)
            self.f['key_type'].setToolTip('选择这条记录属于哪类键；「按标准自动填充」会按所选键型查对应标准')
            bg.addWidget(self.f['key_type'], 0, 1)
            bg.addWidget(QLabel('轴径 d (mm):'), 0, 2)
            self.f['d'] = styled_input('必填，例: 45', 120)
            bg.addWidget(self.f['d'], 0, 3)
            b_fill = styled_button('按标准自动填充')
            b_fill.setToolTip('按所选键型查对应标准（平键GB/T 1096、楔键GB/T 1564、半圆键GB/T 1099.1、花键GB/T 1144），由轴径自动算尺寸')
            b_fill.clicked.connect(self._auto_fill)
            bg.addWidget(b_fill, 0, 4)
            bg.addWidget(QLabel('标记:'), 1, 0)
            self.f['mark'] = styled_input('留空 = 自动生成', 130)
            bg.addWidget(self.f['mark'], 1, 1, 1, 3)
            bg.setColumnStretch(5, 1)
            bv.addLayout(bg)
            v.addWidget(base_frame)
            form_frame = QFrame()
            form_frame.setObjectName('card')
            fv2 = QVBoxLayout(form_frame)
            fv2.setSpacing(6)
            t2_lbl = QLabel('② 尺寸与属性（自动填充，特殊件可手改）')
            t2_lbl.setObjectName('groupTitle')
            fv2.addWidget(t2_lbl)
            g = QGridLayout()
            g.setSpacing(6)
            for key, label, ph in enumerate((('b', '键宽 b', '自动'), ('h', '键高 h', '自动'), ('L', '键长 L', '自动'), ('t1', '轴槽深 t1', '自动'), ('t2', '毂槽深 t2', '自动'))):
                g.addWidget(QLabel(label + ':'), i // 3, (i % 3) * 2)
                le = styled_input(ph, 96)
                self.f[key] = le
                g.addWidget(le, i // 3, (i % 3) * 2 + 1)
                g.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum), 0, 6)
                g.addWidget(QLabel('参照标准:'), 2, 0)
                self.f['std'] = styled_combo([
                    '自定义',
                    'GB/T 1096',
                    'GB/T 1564',
                    'GB/T 1099.1',
                    'GB/T 1144'])
                g.addWidget(self.f['std'], 2, 1)
                g.addWidget(QLabel('材料:'), 2, 2)
                self.f['mat'] = QComboBox()
                self.f['mat'].setEditable(True)
                self.f['mat'].setMinimumWidth(100)
                g.addWidget(self.f['mat'], 2, 3)
                g.addWidget(QLabel('备注:'), 3, 0)
                self.f['note'] = styled_input('选填，例: 减速器输出轴', 200)
                g.addWidget(self.f['note'], 3, 1, 1, 3)
                fv2.addLayout(g)
                v.addWidget(form_frame)
                save_row = QHBoxLayout()
                b_save = styled_button('保存修改')
                b_save.clicked.connect(self._save_edit)
                b_asnew = styled_button('另存为新规格', primary = False)
                b_asnew.clicked.connect(self._save_new)
                save_row.addWidget(b_save)
                save_row.addWidget(b_asnew)
                save_row.addStretch()
                v.addLayout(save_row)
                None(None, None, None, None, None, (lambda : self._rm_link('supplier')))
                None(None, None, None, None, None, (lambda : self._rm_link('customer')))
                dwg_frame = QFrame()
                dwg_frame.setObjectName('card')
                dv = QVBoxLayout(dwg_frame)
                dv.setSpacing(6)
                dwg_t = QLabel('⑤ 关联图纸（选填）')
                dwg_t.setObjectName('groupTitle')
                dv.addWidget(dwg_t)
                dv.addWidget(QLabel('只记录图纸文件在本机的位置（不复制文件），双击列表项即可打开。'))
                self.list_dwg = QListWidget()
                self.list_dwg.setMaximumHeight(80)
                dv.addWidget(self.list_dwg)
                drow = QHBoxLayout()
                b_add = styled_button('添加图纸…', primary = False)
                b_add.clicked.connect(self._add_drawing)
                b_open = styled_button('打开', primary = False)
                b_open.clicked.connect(self._open_drawing)
                b_rm = styled_button('移除', primary = False)
                b_rm.clicked.connect(self._rm_drawing)
                drow.addWidget(b_add)
                drow.addWidget(b_open)
                drow.addWidget(b_rm)
                drow.addStretch()
                dv.addLayout(drow)
                v.addWidget(dwg_frame)
                v.addStretch()
                detail_scroll.setWidget(self.detail)
                body.addWidget(detail_scroll, 1)
                root.addLayout(body, 1)
                return None
    def _mk_assoc(self, v, title, desc, attr, add_slot, rm_slot):
        '''创建关联区：combo 存 self.attr+"_cmb"，列表存 self.attr+"_list" '''
        frame = QFrame()
        frame.setObjectName('card')
        fv = QVBoxLayout(frame)
        fv.setSpacing(6)
        tt = QLabel(title)
        tt.setObjectName('groupTitle')
        fv.addWidget(tt)
        fv.addWidget(QLabel(desc))
        row = QHBoxLayout()
        combo = QComboBox()
        combo.setEditable(True)
        combo.setFixedWidth(130)
        row.addWidget(combo)
        b_add = styled_button('关联', primary = False)
        b_add.clicked.connect(add_slot)
        row.addWidget(b_add)
        b_rm = styled_button('解除选中', primary = False)
        b_rm.clicked.connect(rm_slot)
        row.addWidget(b_rm)
        row.addStretch()
        fv.addLayout(row)
        lw = QListWidget()
        lw.setMaximumHeight(70)
        fv.addWidget(lw)
        v.addWidget(frame)
        setattr(self, attr + '_cmb', combo)
        setattr(self, attr + '_list', lw)
        return frame
    def refresh_all(self):
        self._load_rosters()
        self.refresh_list()
    def _load_rosters(self):
        for combo, items in ((self.sup_cmb, KL.list_suppliers(self.conn)), (self.cus_cmb, KL.list_customers(self.conn))):
            cur = combo.currentText()
            combo.clear()
            combo.addItem('')
            for r in items:
                combo.addItem(r['name'])
                if cur:
                    i = combo.findText(cur)
                    combo.setCurrentIndex(i if i >= 0 else 0)
            mats = KL.list_materials(self.conn)
            cur = self.f['mat'].currentText()
            self.f['mat'].clear()
            self.f['mat'].addItems([
                ''] + mats)
            if cur:
                self.f['mat'].setCurrentText(cur)
                return None
            return None
    def refresh_list(self):
        '''重建列表；若当前选中规格仍存在则保持选中并重载详情'''
        kw = self.search_input.text().strip()
        keep_id = self._spec_id
        self.listw.blockSignals(True)
        self.listw.clear()
        specs = KL.list_specs(self.conn, kw, self.type_filter.currentText() if self.type_filter.currentIndex() else '')
        (new_row, kept) = (-1, None)
        for i, s in enumerate(specs):
            tag = '［标］' if s['std_ref'] != '自定义' else ''
            if not s['key_type']:
                pass
            it = QListWidgetItem(f'''【{'平键'}】{tag}{s['mark']}''')
            it.setData(Qt.ItemDataRole.UserRole, s['id'])
            self.listw.addItem(it)
            if s['id'] == keep_id:
                kept = s
                new_row = i
            if not kept is None:
                self.listw.setCurrentRow(new_row)
        self.listw.blockSignals(False)
        if not kept is None:
            self._load_spec(kept)
            return None
        self._spec_id = None
        self._clear_detail()
    def _clear_detail(self):
        self._spec_id = None
        self._mark_user_edited = False
        for le in self.f.values():
            if isinstance(le, QLineEdit):
                le.clear()
            self.f['key_type'].setCurrentText('平键')
            self.figure.clear()
            self.sup_list.clear()
            self.cus_list.clear()
            self.list_dwg.clear()
            return None
    def _on_select(self, row):
        if row < 0 or self._loading:
            return None
        item = None.listw.item(row)
        if not item:
            return None
        sid = None.data(Qt.ItemDataRole.UserRole)
        s = KL.get_spec(self.conn, sid) if sid else None
        if not s:
            return None
        None._load_spec(s)
    def _load_spec(self, s):
        '''按记录回填详情（唯一入口，_spec_id 以 id 为准）'''
        self._spec_id = s['id']
        self._loading = True
        self._mark_user_edited = True

        try:
            for key, val in (('mark', s['mark']), ('d', s['d']), ('b', s['b']), ('h', s['h']), ('L', s['L']), ('t1', s['t1']), ('t2', s['t2'])):
                if val in (None, 0) and key != 'd':
                    pass
                elif not val is None:
                    pass

                str(val(''))
                self.f['d'].setText(str(s['d']))
            self.f['std'].setCurrentText(self.STD_DISPLAY.get(s['std_ref'], s['std_ref']) if s['std_ref'] in self.STD_DISPLAY or s['std_ref'] == '自定义' else '自定义')
            self.f['key_type'].setCurrentText(s['key_type'] if s['key_type'] in ('平键', '半圆键', '楔键', '花键') else '平键')
            if not s['material_name']:
                pass
            self.f['mat'].setCurrentText('')
            if not s['note']:
                pass
            self.f['note'].setText('')
            self._loading = False
        except:
            self._loading = False

        self._update_figure(s)
        self._refresh_links()
        self._refresh_drawings()
    def _update_figure(self, s):
        if s['key_type'] == '花键':
            self.fig_stack.setCurrentWidget(self.spline_figure)
            if not s['mark']:
                pass
            mm = re.match('^\\s*(\\d+)\\s*[×x]\\s*(\\d+(?:\\.\\d+)?)\\s*[×x]\\s*(\\d+(?:\\.\\d+)?)\\s*[×x]\\s*(\\d+(?:\\.\\d+)?)\\s*$', '')
            if mm:
                self.spline_figure.set_params(int(mm.group(1)), float(mm.group(2)), float(mm.group(3)), float(mm.group(4)), mark = s['mark'])
            else:
                self.spline_figure.clear()
            return None
        None.fig_stack.setCurrentWidget(self.figure)
        if not s['t1']:
            pass
        t1 = s['h'] / 2
        if not s['t2']:
            pass
        t2 = s['h'] / 2
        if not s['L']:
            pass
        L = s['b'] * 3
        mark = s['mark']
        if s['std_ref'] == '自定义':
            mark += '  (自定义规格)'
        self.figure.set_params(s['d'], s['b'], s['h'], t1, t2, L, max(L, s['d']), mark = mark)
    def _refresh_links(self):
        pass


    def _refresh_drawings(self):
        self.list_dwg.clear()
        if not self._spec_id:
            return None
        for r in None.list_drawings(self.conn, self._spec_id):
            self.list_dwg.addItem(f'''{os.path.basename(r['path'])}''' + f''' rev{r['rev']}''' if r['rev'] else '' + f'''   [{r['path']}]''')
            return None
    def _form_values(self):

        try:
            if not self.f['h'].text():
                pass
            if not self.f['L'].text():
                pass
            if not self.f['t1'].text():
                pass
            if not self.f['t2'].text():
                pass
            return dict(mark = self.f['mark'].text().strip(), d = float(self.f['d'].text()), b = float(self.f['b'].text()), h = float(0), L = float(0), t1 = float(0), t2 = float(0), std_ref = self.STD_STORE.get(self.f['std'].currentText(), self.f['std'].currentText()), note = self.f['note'].text().strip(), mat_name = self.f['mat'].currentText().strip(), key_type = self.f['key_type'].currentText())
        except ValueError:
            raise ValueError('轴径/键宽/键高需为有效数字')
    def _save_new(self):

        try:
            vals = self._form_values()
        except ValueError:
            e = None
            QMessageBox.warning(self, '输入错误', str(e))
            e = None
            del e
            return None
            e = None
            del e

        if not vals['mark']:
            QMessageBox.warning(self, '输入错误', '标记不能为空')
            return None
        if not None(self, self.conn, vals['mark']):
            return None

        try:
            mid = KL.ensure_material(self.conn, vals['mat_name']) if vals['mat_name'] else None
            sid = KL.add_spec(self.conn, vals['mark'], vals['d'], vals['b'], vals['h'], vals['L'], vals['t1'], vals['t2'], vals['key_type'], vals['std_ref'], mid, vals['note'])
        except ValueError:
            e = None
            QMessageBox.warning(self, '校验未通过', str(e))
            e = None
            del e
            return None
            e = None
            del e

        self._spec_id = sid
        self.refresh_list()
        QMessageBox.information(self, '已保存', f'''已存入零件库（#{sid}）''')
    def _save_edit(self):
        if not self._spec_id:
            QMessageBox.information(self, '提示', '请先在左侧选择一条规格')
            return None

        try:
            vals = self._form_values()
        except ValueError:
            e = None
            QMessageBox.warning(self, '输入错误', str(e))
            e = None
            del e
            return None
            e = None
            del e

        err = KL.validate_spec(vals['d'], vals['b'], vals['h'], vals['L'], vals['t1'], vals['t2'], vals['key_type'])
        if err:
            QMessageBox.warning(self, '校验未通过', err)
            return None
        mid = KL.ensure_material(self.conn, vals['mat_name']) if None['mat_name'] else None
        KL.update_spec(self.conn, self._spec_id, mark = vals['mark'], d = vals['d'], b = vals['b'], h = vals['h'], L = vals['L'], t1 = vals['t1'], t2 = vals['t2'], std_ref = vals['std_ref'], material_id = mid, note = vals['note'], key_type = vals['key_type'])
        self.refresh_list()
    def _delete_current(self):
        if not self._spec_id:
            QMessageBox.information(self, '提示', '请先在左侧选择一条规格')
            return None
        if None.question(self, '确认删除', '删除该规格及其全部关联记录？', QMessageBox.Yes | QMessageBox.No) != QMessageBox.Yes:
            return None
        None.delete_spec(self.conn, self._spec_id)
        self.refresh_list()
    def _new_blank(self):
        self._clear_detail()
        self.f['std'].setCurrentText('自定义')
        self.f['d'].setFocus()
    def _set_mark_auto(self, text):
        '''自动填充写入标记：覆盖旧自动值，但用户手改过的标记不覆盖；
            写入后视为「新的自动值」（下次自动填充可继续覆盖）'''
        if not self.f['mark'].text().strip() or self._mark_user_edited:
            self.f['mark'].setText(text)
            self._mark_user_edited = False
            return None
    def _auto_fill(self):
        '''按所选键型由轴径一键填充尺寸明细（新手只需填轴径）
            - 平键 GB/T 1096：b/h/t1/t2/L 全自动
            - 楔键 GB/T 1564：截面尺寸与平键相同（TAPER_KEY_TABLE），1:100 斜度
              只影响槽深——楔键槽深无独立查表数据，t1/t2 留空由用户手填
            - 半圆键 GB/T 1099.1：b/h 自动，标记用 b×d1；同一轴径可能命中多个
              规格，默认填第一个并提示；半圆键槽深按所选规格查表，暂无数据留空
            - 花键 GB/T 1144：标记用规格 N×d×D×B，b 填键宽 B，d 填小径
            '''

        try:
            d = parse_float(self.f['d'].text(), '轴径')
        except ValueError:
            e = None
            QMessageBox.warning(self, '请先填轴径', str(e))
            e = None
            del e
            return None
            e = None
            del e

        kt = self.f['key_type'].currentText()
        if kt == '平键':
            (b, h) = get_parallel_key(d)
            if not b:
                QMessageBox.warning(self, '超出标准范围', '轴径 %gmm 超出平键标准范围（GB/T 1096 覆盖 6~500mm）' % d)
                return None
            (t1v, t2v) = None(d)
            L = select_key_length(b, estimate_hub_width(b))
            self.f['b'].setText('%g' % b)
            self.f['h'].setText('%g' % h)
            if not L is None:
                self.f['L'].setText('%g' % L)
            else:
                self.f['L'].clear()
            self.f['t1'].setText('%g' % t1v)
            self.f['t2'].setText('%g' % t2v)
            self.f['std'].setCurrentText('GB/T 1096')
            if not L is None:
                self._set_mark_auto('键 %g×%g×%g' % (b, h, L))
            else:
                self._set_mark_auto('键 %g×%g×(键长待定)' % (b, h))
            if not L is not None:
                QMessageBox.information(self, '键长需手填', '按 4×键宽 估算的毂宽选不出标准键长，键长已留空——请手填后修改标记')
            return None
        if None == '楔键':
            (b, h) = get_parallel_key(d)
            if not b:
                QMessageBox.warning(self, '超出标准范围', '轴径 %gmm 超出楔键标准范围（GB/T 1564 截面同 GB/T 1096）' % d)
                return None
            L = None(b, estimate_hub_width(b), 'taper')
            self.f['b'].setText('%g' % b)
            self.f['h'].setText('%g' % h)
            if not L is None:
                self.f['L'].setText('%g' % L)
            else:
                self.f['L'].clear()
            self.f['t1'].clear()
            self.f['t2'].clear()
            self.f['std'].setCurrentText('GB/T 1564')
            if not L is None:
                self._set_mark_auto('键 %g×%g' % (b, L))
            else:
                self._set_mark_auto('键 %g×(键长待定)' % b)
            return None
        if None == '半圆键':
            rs = get_woodruff_key(d)
            if not rs:
                QMessageBox.warning(self, '超出标准范围', '轴径 %gmm 无匹配的半圆键规格（GB/T 1099.1 适用轴径 3~38mm）' % d)
                return None
            (code, b, h, d1) = None[0]
            self.f['b'].setText('%g' % b)
            self.f['h'].setText('%g' % h)
            self.f['L'].clear()
            self.f['t1'].clear()
            self.f['t2'].clear()
            self.f['std'].setCurrentText('GB/T 1099.1')
            self._set_mark_auto('键 %g×%g' % (b, d1))
            if len(rs) > 1:
                self('多个规格可选', '轴径 %gmm 命中 %d 个半圆键规格（%s），已填第一个「%s」，如需其它规格请手改', d % (len(rs), '、'.join, (lambda .0: pass# WARNING: Decompyle incomplete
    )(rs()), code))
            return None
        rs = None(d)
        if not rs:
            QMessageBox.warning(self, '超出标准范围', '小径 %gmm 无匹配的花键规格（GB/T 1144 轻系列）' % d)
            return None
        (spec, N, d_small, D, B) = None[0]
        self.f['b'].setText('%g' % B)
        self.f['h'].clear()
        self.f['L'].clear()
        self.f['t1'].clear()
        self.f['t2'].clear()
        self.f['std'].setCurrentText('GB/T 1144')
        self._set_mark_auto(spec)
        QMessageBox.information(self, '已按花键填充', '规格 %s（齿数 %d，大径 %gmm）已填入；键宽 B 已填，键高/键长/槽深不适用于花键' % (spec, N, D))
    def _add_link(self, table):
        if not self._spec_id:
            QMessageBox.information(self, '提示', '请先选择一条规格')
            return None
        combo = self.sup_cmb if None == 'supplier' else self.cus_cmb
        name = combo.currentText().strip()
        if not name:
            QMessageBox.information(self, '提示', '请输入或选择名称')
            return None
        pid = None.ensure_roster(self.conn, table, name)
        KL.link_partner(self.conn, self._spec_id, table, pid)
        self._load_rosters()
        self._refresh_links()
    def _rm_link(self, table):
        pass


    def _add_drawing(self):
        if not self._spec_id:
            QMessageBox.information(self, '提示', '请先选择一条规格')
            return None
        (path, _) = None.getOpenFileName(self, '选择图纸文件', '', '图纸 (dwg dxf pdf png jpg);;所有文件 (*.*)')
        if not path:
            return None

        try:
            KL.add_drawing(self.conn, self._spec_id, path)
        except FileNotFoundError:
            e = None
            QMessageBox.warning(self, '文件不存在', str(e))
            e = None
            del e
            return None
            e = None
            del e

        self._refresh_drawings()
    def _open_drawing(self):
        item = self.list_dwg.currentItem()
        if not item:
            return None
        full = item.text().split('[', 1)[1].rstrip(']') if None in item.text() else item.text()
        if not self._spec_id:
            pass
        for r in KL.list_drawings(self.conn, 0):
            if r['path'] == full:
                KL.open_drawing(r['path'])
            else:
                except (FileNotFoundError, OSError):
                    e = None
                    QMessageBox.warning(self, '无法打开', str(e))
                    e = None
                    del e
                except:
                    e = None
                    del e
                return None
            return None
    def _rm_drawing(self):
        item = self.list_dwg.currentItem()
        if not item:
            return None
        full = None.text().split('[', 1)[1].rstrip(']')
        if not self._spec_id:
            pass
        for r in KL.list_drawings(self.conn, 0):
            if r['path'] == full:
                KL.delete_drawing(self.conn, r['id'])

            self._refresh_drawings()
            return None
    def _export_csv(self):
        (path, _) = QFileDialog.getSaveFileName(self, '导出 CSV', '零件库.csv', 'CSV (*.csv)')
        if not path:
            return None

        try:
            n = KL.export_csv(self.conn, path)
        except OSError:
            e = None
            QMessageBox.warning(self, '导出失败', str(e))
            e = None
            del e
            return None
            e = None
            del e

        QMessageBox.information(self, '已导出', f'''共导出 {n} 条规格 → {path}''')
    def _backup(self):
        (path, _) = QFileDialog.getSaveFileName(self, '备份库文件', 'keylib_backup.db', 'SQLite (*.db)')
        if not path:
            return None
        None.backup_db(self.conn, path)
        QMessageBox.information(self, '已备份', f'''备份完成 → {path}''')
    def _restore(self):
        if QMessageBox.question(self, '确认恢复', '将用所选备份文件覆盖当前零件库，当前数据会丢失，继续？', QMessageBox.Yes | QMessageBox.No) != QMessageBox.Yes:
            return None
        (path, _) = None.getOpenFileName(self, '选择备份文件', '', 'SQLite (*.db)')
        if not path:
            return None

        try:
            KL.restore_db(path)
        except (FileNotFoundError, sqlite3.Error):
            e = None
            QMessageBox.warning(self, '恢复失败', str(e))
            e = None
            del e
            return None
            e = None
            del e

        self.conn = KL.connect()
        self.refresh_all()
        QMessageBox.information(self, '已恢复', '零件库已从备份恢复')
    __classcell__ = None
class ModeCard:
    '''首页区域卡片：整卡可点击进入对应功能区'''
    clicked = Signal()

    def __init__(self, icon, title, desc, feats):
        super().__init__()
        self.setObjectName('modeCard')
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 22, 24, 18)
        lay.setSpacing(10)
        head = QHBoxLayout()
        icon_lbl = QLabel(icon)
        icon_lbl.setObjectName('cardIcon')
        title_lbl = QLabel(title)
        title_lbl.setObjectName('cardTitle')
        head.addWidget(icon_lbl)
        head.addWidget(title_lbl)
        head.addStretch()
        lay.addLayout(head)
        desc_lbl = QLabel(desc)
        desc_lbl.setObjectName('cardDesc')
        desc_lbl.setWordWrap(True)
        lay.addWidget(desc_lbl)
        for f in feats:
            fl = QLabel('·  ' + f)
            fl.setObjectName('cardFeat')
            fl.setWordWrap(True)
            lay.addWidget(fl)
            lay.addStretch()
            go = QHBoxLayout()
            go.addStretch()
            go_lbl = QLabel('进入 →')
            go_lbl.setObjectName('cardGo')
            go.addWidget(go_lbl)
            lay.addLayout(go)
            return None
    def mouseReleaseEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mouseReleaseEvent(e)
    __classcell__ = None
class HomeTab:

    def __init__(self):
        super().__init__()
        self._build_ui()
    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(28, 22, 28, 22)
        outer.addStretch(1)
        title = QLabel(f'''键联接选型工具 {VERSION}''')
        title.setObjectName('title')
        title.setAlignment(Qt.AlignCenter)
        outer.addWidget(title)
        sub = QLabel('数据来源：GB/T 1095/1096/1099.1/1564/1565/1144 + 机械设计手册')
        sub.setObjectName('dim')
        sub.setAlignment(Qt.AlignCenter)
        outer.addWidget(sub)
        outer.addSpacing(18)
        zones = QHBoxLayout()
        zones.setSpacing(24)
        self.zone_smart = ModeCard('📐', '智能选型', '按工况计算推荐：输入轴径·扭矩·材料，自动给出键型、规格与强度校核。', [
            '智能选型：工况一键推荐 + 强度校核',
            '设计助手：由功率/扭矩反算设计方案',
            '平键 / 半圆键 / 楔键 / 花键：查表 + 剖面图'])
        self.zone_lib = ModeCard('🗃', '零件库', '个人规格数据库：管理自己录入的键规格与往来信息。', [
            '自定义规格入库 + 实时预览图',
            '供应商 / 客户 / 材料关联管理',
            '关联图纸路径 · 导出 CSV · 备份恢复'])
        zones.addWidget(self.zone_smart, 1)
        zones.addWidget(self.zone_lib, 1)
        outer.addLayout(zones)
        outer.addSpacing(12)
        tip = QLabel('点击区域进入 · 页签栏左端「首页」随时返回')
        tip.setObjectName('dim')
        tip.setAlignment(Qt.AlignCenter)
        outer.addWidget(tip)
        outer.addStretch(1)
    __classcell__ = None
class MainWindow:

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f'''键联接选型工具 {VERSION}''')
        self.setMinimumSize(780, 640)
        self.resize(960, 900)
        self._theme_key = get_theme_key()
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(12, 10, 12, 8)
        main_layout.setSpacing(8)
        head = QHBoxLayout()
        head.setSpacing(6)
        title = QLabel(f'''键联接选型工具 {VERSION}''')
        title.setObjectName('title')
        title.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        head.addWidget(title)
        head.addStretch()
        head.addWidget(QLabel('主题'))
        self._swatches = []
        for key in THEME_ORDER:
            btn = QPushButton()
            btn.setObjectName('swatch')
            btn.setCheckable(True)
            btn.setFixedSize(22, 22)
            btn.setToolTip(THEMES[key]['label'])
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet('QPushButton#swatch { background: %s; }' % THEMES[key]['SWATCH'])
            None((lambda _ = None, k = None: self._apply_theme(k)))
            self._swatches.append((key, btn))
            head.addWidget(btn)
            main_layout.addLayout(head)
            self.tabs = QTabWidget()
            self.design_tab = DesignTab()
            self.parallel_tab = ParallelKeyTab()
            self.woodruff_tab = WoodruffKeyTab()
            self.taper_tab = TaperKeyTab()
            self.spline_tab = SplineTab()
            self.lib_tab = LibraryTab()
            self.overview_tab = OverviewTab(self.lib_tab)
            self.smart_tab = SmartTab()
            self.smart_tab._shared_conn = self.lib_tab.conn
            self.home_tab = HomeTab()
            self._smart_pages = [
                ('智能选型', self.smart_tab),
                ('设计助手', self.design_tab),
                ('平键', self.parallel_tab),
                ('半圆键', self.woodruff_tab),
                ('楔键', self.taper_tab),
                ('花键', self.spline_tab)]
            self._mode = None
            self.tabs.addTab(self.home_tab, '首页')
            self.tabs.currentChanged.connect(self._on_tab_changed)
            None((lambda : self._set_mode('smart')))
            None((lambda : self._set_mode('lib')))
            self.overview_tab.request_open_spec.connect(self._open_spec_from_overview)
            main_layout.addWidget(self.tabs, 1)
            self._sync_tabbar()
            footer = QLabel(f'''数据来源: {DATA_SOURCE}  |  仅供参考，以标准原文为准  |  {VERSION}''')
            footer.setObjectName('footer')
            footer.setAlignment(Qt.AlignCenter)
            main_layout.addWidget(footer)
            self._apply_theme(self._theme_key)
            return None
    def _open_spec_from_overview(self, spec_id):
        '''库总览点卡片 → 切到规格管理页签并选中该记录'''
        self.tabs.setCurrentWidget(self.lib_tab)
        for row in range(self.lib_tab.listw.count()):
            it = self.lib_tab.listw.item(row)
            if it.data(Qt.ItemDataRole.UserRole) == spec_id:
                self.lib_tab.listw.setCurrentRow(row)
                return None
            return None
    def _set_mode(self, mode):
        '''挂载对应区的页签组；已在同区则仅切换当前页'''
        if mode == self._mode:
            self.tabs.setCurrentWidget(self.overview_tab if mode == 'lib' else self.smart_tab)
            return None
        None.tabs.blockSignals(True)
        if self.tabs.count() > 1:
            self.tabs.removeTab(1)
            if self.tabs.count() > 1 or mode == 'lib':
                self.tabs.addTab(self.overview_tab, '库总览')
                self.tabs.addTab(self.lib_tab, '规格管理')
                self.tabs.setCurrentWidget(self.overview_tab)
            else:
                for name, wgt in self._smart_pages:
                    self.tabs.addTab(wgt, name)
                    self.tabs.setCurrentWidget(self.smart_tab)
                    self.tabs.blockSignals(False)
                    self._mode = mode
                    self._sync_tabbar()
                    if mode == 'lib':
                        self.lib_tab.refresh_all()
                        self.overview_tab.refresh()
                        return None
                    return self.tabs.count() > 1
    def _sync_tabbar(self):
        self.tabs.tabBar().setVisible(self.tabs.currentWidget() is not self.home_tab)
    def _on_tab_changed(self, i):
        self._sync_tabbar()
        if self.tabs.widget(i) is self.lib_tab:
            self.lib_tab.refresh_all()
            return None
        if None.tabs.widget(i) is self.overview_tab:
            self.overview_tab.refresh()
            return None
    def _apply_theme(self, key):
        '''就地换肤：全局 QSS 重设，窗口实例不变'''
        if key not in THEMES:
            return None
        self._theme_key = None
        set_theme_key(key)
        self.setStyleSheet(build_qss(key))
        T = THEMES[key]
        app = QApplication.instance()
        if not app is None:
            pal = app.palette()
            pal.setColor(QPalette.Window, QColor(T['BG']))
            pal.setColor(QPalette.WindowText, QColor(T['TEXT_W']))
            pal.setColor(QPalette.Base, QColor(T['CARD_BG']))
            pal.setColor(QPalette.AlternateBase, QColor(T['CARD2']))
            pal.setColor(QPalette.Button, QColor(T['CARD2']))
            pal.setColor(QPalette.ButtonText, QColor(T['TEXT_W']))
            pal.setColor(QPalette.Text, QColor(T['TEXT_W']))
            pal.setColor(QPalette.ToolTipBase, QColor(T['CARD2']))
            pal.setColor(QPalette.ToolTipText, QColor(T['TEXT_W']))
            pal.setColor(QPalette.Highlight, QColor(T['ACCENT']))
            pal.setColor(QPalette.HighlightedText, QColor('#ffffff'))
            pal.setColor(QPalette.PlaceholderText, QColor(T['TEXT_G']))
            for grp in (QPalette.Disabled,):
                pal.setColor(grp, QPalette.WindowText, QColor(T['TEXT_G']))
                pal.setColor(grp, QPalette.Text, QColor(T['TEXT_G']))
                pal.setColor(grp, QPalette.ButtonText, QColor(T['TEXT_G']))
                app.setPalette(pal)
                for k, btn in self._swatches:
                    btn.setChecked(k == key)
                    return None
    __classcell__ = None
def main():
    app = QApplication(sys.argv)
    app.setFont(cjk_font(10))
    if is_first_run():
        welcome = WelcomeDialog()
        welcome.exec()
    if not is_unlocked():
        lock = LockDialog()
        if lock.exec() != QDialog.Accepted:
            sys.exit(0)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
if __name__ == '__main__':
    main()
    return None
