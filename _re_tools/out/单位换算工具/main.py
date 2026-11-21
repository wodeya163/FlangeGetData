# Reconstructed from bytecode by split_decompile.py
# main.pyc

'''
单位换算工具 — UI 模块（v3.5）
21类单位：分类标签网格（3行×7列）→ 单位按钮网格（点击进入该单位换算）→ 大字体结果区
v3.2：输入容错、点单位名反转、复制全部、历史记录、窗口可拖高
v3.3：5 套主题即点即换
v3.4：分类改标签网格；新增导热系数/比热容/热膨胀系数/动力粘度/运动粘度/转速
v3.4.1：主题切换改标题栏色圆点（5 个）
v3.5：换肤改为就地刷新（不重建窗口、不闪新窗）；单位下拉改为按钮网格（选择区与
      换算区分开，点击按钮进入该单位换算）；结果区字体加大（值 16px/输入 20px）
'''
import sys
import re
import math
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QComboBox, QFrame, QLineEdit, QScrollArea, QVBoxLayout, QPushButton, QMenu, QGridLayout
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QClipboard
from unit_data import CATEGORIES, CAT_ORDER, CHIP_LABELS, convert, parse_dms, format_dms, ANGLE_DMS_IDX, _load_config, _save_config, THEMES, THEME_ORDER, DEFAULT_THEME, get_theme_key, set_theme_key
from hardness_data import RANGES as HARDNESS_RANGES
VERSION = 'v3.5'
DATA_SOURCE = 'GB/T 80000 + ISO 80000'
BG = '#0f0f14'
CARD_BG = '#1a1a24'
ACCENT = '#6c5ce7'
ACCENT_H = '#a29bfe'
TEXT_W = '#f0f0f0'
TEXT_G = '#8a8a9a'
BORDER = '#2a2a3a'
WARN = '#fdcb6e'
INPUT_BG = '#12121e'
ROW_ALT = '#151520'
COPIED = '#2ecc71'
WM = '#555566'
CARD_STYLE = f'''QFrame#card {{ background: {CARD_BG}; border: 1px solid {BORDER}; border-radius: 8px; }}'''
_FULLWIDTH_TRANS = str.maketrans('０１２３４５６７８９．，＋－ｅＥ', '0123456789.,+-eE')
_COMMA_GROUP_RE = re.compile('^-?\\d{1,3}(?:,\\d{3})+(?:\\.\\d+)?$')

def _parse_number(text):
    '''容错解析数值：全角→半角、千分位逗号剥离；拒绝 nan/inf。失败返回 None'''
    t = text.strip().translate(_FULLWIDTH_TRANS)
    if _COMMA_GROUP_RE.match(t):
        t = t.replace(',', '')
    if not t:
        return None

    try:
        v = float(t)
    except ValueError:
        return None

    if not math.isfinite(v):
        return None
    return v
def _build_styles():
    '''按当前模块级颜色 token 重建输入框样式（主题切换时重调）'''
    global INPUT_STYLE
    INPUT_STYLE = f'''\n    QLineEdit {{\n        background: {INPUT_BG}; color: {TEXT_W}; border: 1px solid {BORDER};\n        border-radius: 6px; padding: 4px 14px; font-size: 20px; font-weight: bold;\n    }}\n    QLineEdit:focus {{ border-color: {ACCENT}; }}\n'''
_build_styles()
_THEME_TOKENS = ('BG', 'CARD_BG', 'ACCENT', 'ACCENT_H', 'TEXT_W', 'TEXT_G', 'BORDER', 'WARN', 'INPUT_BG', 'ROW_ALT', 'COPIED', 'WM')

def _apply_theme(key):
    '''把主题 token 覆盖到模块级颜色并重建样式（只改内存，持久化走 set_theme_key）'''
    t = THEMES.get(key) or THEMES[DEFAULT_THEME]
    for k in _THEME_TOKENS:
        globals()[k] = t[k]
    _build_styles()
class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        _apply_theme(get_theme_key())
        self.setWindowTitle('单位换算工具')
        self.setFixedWidth(520)
        self.setMinimumHeight(600)
        self.resize(520, 700)
        self.setStyleSheet(f'''background: {BG};''')
        self.current_cat = 'pressure'
        self.from_idx = 0
        self._result_labels = []
        self._unit_btns = []
        c = QWidget()
        self.setCentralWidget(c)
        self._title = QLabel(f'''单位换算  {VERSION}''', c)
        self._title.setGeometry(0, 5, 520, 24)
        self._title.setAlignment(Qt.AlignCenter)
        self._title.setStyleSheet(f'''color: {TEXT_W}; font-size: 15px; font-weight: bold;''')
        cur = get_theme_key()
        self._swatches = { }
        for i, key in enumerate(THEME_ORDER):
            b = QPushButton(c)
            b.setFixedSize(20, 20)
            b.setToolTip('切换主题：' + THEMES[key]['label'])
            b.setCursor(Qt.PointingHandCursor)
            sel = key == cur
            ring = f'''2px solid {TEXT_W}''' if sel else f'''1px solid {BORDER}'''
            hover = '' if sel else f'''QPushButton:hover {{ border: 2px solid {TEXT_W}; }}'''
            b.setStyleSheet(f'''QPushButton {{ background: {THEMES[key]['ACCENT']}; border-radius: 10px; border: {ring}; }} {hover}''')
            b.clicked.connect(lambda _, k=key: self._on_swatch(k))
            b.setGeometry(389 + i * 24, 7, 20, 20)
            self._swatches[key] = b
        self._chip_on = f'''QPushButton {{ background: {ACCENT}; color: #ffffff; border: 1px solid {ACCENT}; border-radius: 4px; font-size: 11px; font-weight: bold; }}'''
        self._chip_off = f'''QPushButton {{ background: {CARD_BG}; color: {TEXT_G}; border: 1px solid {BORDER}; border-radius: 4px; font-size: 11px; }}QPushButton:hover {{ color: {ACCENT_H}; border-color: {ACCENT}; }}'''
        self._chips = { }
        panel = QWidget(c)
        panel.setGeometry(15, 32, 490, 78)
        grid = QGridLayout(panel)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(3)
        for i, key in enumerate(CAT_ORDER):
            b = QPushButton(CHIP_LABELS[key], panel)
            b.setCheckable(True)
            b.setFixedSize(67, 24)
            b.setToolTip(CATEGORIES[key]['name'])
            b.setCursor(Qt.PointingHandCursor)
            b.setStyleSheet(self._chip_off)
            b.clicked.connect(lambda _, k=key: self._on_chip(k))
            self._chips[key] = b
            grid.addWidget(b, i // 7, i % 7)
        self._sep1 = QFrame(c)
        self._sep1.setGeometry(15, 114, 490, 1)
        self._sep1.setStyleSheet(f'''background: {BORDER};''')
        self._unit_btn_on = f'''QPushButton {{ background: {ACCENT}; color: #ffffff; border: 1px solid {ACCENT}; border-radius: 4px; font-size: 11px; font-weight: bold; }}'''
        self._unit_btn_off = f'''QPushButton {{ background: {CARD_BG}; color: {TEXT_W}; border: 1px solid {BORDER}; border-radius: 4px; font-size: 11px; }}QPushButton:hover {{ border-color: {ACCENT}; color: {ACCENT_H}; }}'''
        self._unit_panel = QWidget(c)
        self._unit_panel.setGeometry(15, 120, 490, 78)
        self._unit_grid = QGridLayout(self._unit_panel)
        self._unit_grid.setContentsMargins(0, 0, 0, 0)
        self._unit_grid.setSpacing(3)
        self._sep2 = QFrame(c)
        self._sep2.setGeometry(15, 202, 490, 1)
        self._sep2.setStyleSheet(f'''background: {BORDER};''')
        self.input_field = QLineEdit(c)
        self.input_field.setGeometry(15, 208, 490, 40)
        self.input_field.setStyleSheet(INPUT_STYLE)
        self.input_field.setPlaceholderText('输入数值')
        self.input_field.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.input_field.textChanged.connect(self._update)
        self.input_field.setMaxLength(16)
        self.input_field.editingFinished.connect(self._persist_state)
        self.hint_label = QLabel('', c)
        self.hint_label.setGeometry(15, 258, 295, 14)
        self.hint_label.setStyleSheet(f'''color: {TEXT_G}; font-size: 9px;''')
        btn_style = f'''QPushButton {{ background: {CARD_BG}; color: {TEXT_G}; border: 1px solid {BORDER}; border-radius: 4px; font-size: 10px; }}QPushButton:hover {{ color: {ACCENT_H}; border-color: {ACCENT}; }}'''
        self.btn_copy_all = QPushButton('复制全部', c)
        self.btn_copy_all.setGeometry(377, 256, 62, 20)
        self.btn_copy_all.setStyleSheet(btn_style)
        self.btn_copy_all.setCursor(Qt.PointingHandCursor)
        self.btn_copy_all.setToolTip('把当前所有换算结果复制为多行文本')
        self.btn_copy_all.clicked.connect(self._copy_all)
        self.btn_history = QPushButton('🕘 历史', c)
        self.btn_history.setGeometry(443, 256, 62, 20)
        self.btn_history.setStyleSheet(btn_style)
        self.btn_history.setCursor(Qt.PointingHandCursor)
        self.btn_history.setToolTip('最近 10 次换算，点击恢复')
        self.btn_history.clicked.connect(self._show_history)
        self._scroll = QScrollArea(c)
        self._scroll.setGeometry(15, 276, 490, 388)
        self._scroll.setWidgetResizable(True)
        self._scroll.setStyleSheet('QScrollArea { border: none; background: transparent; }')
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        result_widget = QWidget()
        result_widget.setStyleSheet('background: transparent;')
        self.result_layout = QVBoxLayout(result_widget)
        self.result_layout.setContentsMargins(0, 0, 8, 0)
        self.result_layout.setSpacing(2)
        self._scroll.setWidget(result_widget)
        self._wm = QLabel(f'''{DATA_SOURCE}  |  GB/T 1172-1999 (硬度)  |  仅供参考''', c)
        self._wm.setGeometry(0, 678, 520, 16)
        self._wm.setAlignment(Qt.AlignCenter)
        self._wm.setStyleSheet(f'''color: {WM}; font-size: 9px;''')
        self._switch_cat('pressure')
        self._restore_state()
        return None
    def resizeEvent(self, e):
        '''高度可拖：结果区跟随拉伸（v3.2），默认 700 高时与初始布局完全一致'''
        super().resizeEvent(e)
        h = self.height()
        self._scroll.setGeometry(15, 276, 490, h - 276 - 36)
        self._wm.setGeometry(0, h - 22, 520, 16)
    def _restore_state(self):
        cfg = _load_config()
        st = cfg.get('last_state')
        if not isinstance(st, dict):
            return None
        cat = st.get('cat')
        if cat in CAT_ORDER:
            self._switch_cat(cat)
            from_idx = st.get('from_idx')
            units = CATEGORIES[cat]['units']
            if isinstance(from_idx, int) and 0 <= from_idx < len(units):
                self.from_idx = from_idx
                self._style_unit_btns()
            text = st.get('text')
            if isinstance(text, str):
                self.input_field.setText(text)
                return None
    def _persist_state(self):
        entry = {
            'cat': self.current_cat,
            'from_idx': self.from_idx,
            'text': self.input_field.text() }
        cfg = _load_config()
        cfg['last_state'] = entry
        if entry['text'].strip():
            hist = cfg.get('history')
            if not isinstance(hist, list):
                hist = []
            hist = [h for h in hist if h != entry]
            hist.insert(0, entry)
            cfg['history'] = hist[:10]
        try:
            _save_config(cfg)
        except Exception:
            return None
    def _on_chip(self, key):
        '''点击分类标签：切分类（v3.4）'''
        if key == self.current_cat or key not in CAT_ORDER:
            return None
        self._switch_cat(key)
        self._persist_state()
    def _on_unit_btn(self, idx):
        '''点击单位按钮：进入该单位的换算（v3.5）'''
        if idx == self.from_idx or not 0 <= idx < len(self._unit_btns):
            return None
        self.from_idx = idx
        self._style_unit_btns()
        self._update()
        self._persist_state()
    def _switch_cat(self, key):
        self.current_cat = key
        for k, b in self._chips.items():
            sel = k == key
            b.setChecked(sel)
            b.setStyleSheet(self._chip_on if sel else self._chip_off)
        units = CATEGORIES[key]['units']
        self.from_idx = 0
        self._rebuild_unit_btns()
        self._rebuild_result_rows()
        self.hint_label.setText('')
        self._update()
    def _rebuild_unit_btns(self):
        '''按当前分类重建单位按钮网格（5列，最多14个单位=3行）'''
        while self._unit_grid.count():
            item = self._unit_grid.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        self._unit_btns = []
        units = CATEGORIES[self.current_cat]['units']
        for i, u in enumerate(units):
            b = QPushButton(u['name'].split(' (')[0], self._unit_panel)
            b.setCheckable(True)
            b.setFixedSize(94, 24)
            b.setToolTip(u['name'])
            b.setCursor(Qt.PointingHandCursor)
            b.clicked.connect(lambda _, idx=i: self._on_unit_btn(idx))
            self._unit_btns.append(b)
            self._unit_grid.addWidget(b, i // 5, i % 5)
        self._style_unit_btns()
    def _style_unit_btns(self):
        '''同步单位按钮选中态（选中=ACCENT底白字）'''
        for i, b in enumerate(self._unit_btns):
            sel = i == self.from_idx
            b.setChecked(sel)
            b.setStyleSheet(self._unit_btn_on if sel else self._unit_btn_off)
    def _rebuild_result_rows(self):
        '''根据当前分类重建结果行'''
        while self.result_layout.count():
            item = self.result_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        self._result_labels = []
        units = CATEGORIES[self.current_cat]['units']
        for i, u in enumerate(units):
            row = QFrame()
            row.setFixedHeight(34)
            bg = ROW_ALT if i % 2 == 0 else CARD_BG
            row.setStyleSheet(f'''QFrame {{ background: {bg}; border-radius: 4px; }}''')
            lbl_name = QLabel(u['name'], row)
            lbl_name.setGeometry(10, 6, 215, 22)
            lbl_name.setStyleSheet(f'''color: {TEXT_G}; font-size: 13px;''')
            lbl_name.setCursor(Qt.PointingHandCursor)
            lbl_name.setToolTip('点击：以该单位为源反向换算')
            lbl_name.mousePressEvent = lambda _, i=i: self._set_source(i)
            lbl_val = QLabel('—', row)
            lbl_val.setGeometry(225, 4, 235, 26)
            lbl_val.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            lbl_val.setStyleSheet(f'''color: {TEXT_W}; font-size: 16px; font-weight: bold;''')
            lbl_val.setCursor(Qt.PointingHandCursor)
            lbl_val.mousePressEvent = lambda _, v=lbl_val: self._copy_value(v)
            self._result_labels.append((lbl_name, lbl_val))
            self.result_layout.addWidget(row)
        self.result_layout.addStretch()
    def _update(self):
        text = self.input_field.text().strip()
        from_idx = self.from_idx
        if not 0 <= from_idx < len(self._result_labels):
            return None
        is_dms_input = self.current_cat == 'angle' and from_idx == ANGLE_DMS_IDX
        if not text:
            for _, lbl in self._result_labels:
                lbl.setText('—')
            self.hint_label.setText('点击结果可复制')
            return None
        if is_dms_input:
            value = parse_dms(text)
            if value is None:
                for _, lbl in self._result_labels:
                    lbl.setText('—')
                self.hint_label.setText('度分秒格式：35°30′15″ 或 35°30.5′ 或 35.5')
                self.hint_label.setStyleSheet(f'''color: {WARN}; font-size: 9px;''')
                return None
        else:
            value = _parse_number(text)
            if value is None:
                for _, lbl in self._result_labels:
                    lbl.setText('—')
                self.hint_label.setText('请输入有效数字')
                self.hint_label.setStyleSheet(f'''color: {WARN}; font-size: 9px;''')
                return None
        units = CATEGORIES[self.current_cat]['units']
        from_name = units[from_idx]['name']
        from_short = from_name.split(' (')[0]
        if self.current_cat == 'hardness':
            type_keys = ['HRC', 'HV', 'HBW', 'HS']
            ht = type_keys[from_idx]
            lo, hi = HARDNESS_RANGES[ht]
            if value < lo or value > hi:
                self.hint_label.setText(f'''⚠ 超出 {ht} 有效范围 ({lo}~{hi})''')
                self.hint_label.setStyleSheet(f'''color: {WARN}; font-size: 9px;''')
            else:
                self.hint_label.setText(f'''{ht} 有效范围：{lo} ~ {hi}  |  点击结果可复制''')
                self.hint_label.setStyleSheet(f'''color: {TEXT_G}; font-size: 9px;''')
        else:
            self.hint_label.setText('点击结果可复制')
        for i, (name_lbl, val_lbl) in enumerate(self._result_labels):
            if i == from_idx:
                if is_dms_input:
                    val_lbl.setText(f'''{format_dms(value)}  (当前)''')
                else:
                    val_lbl.setText(f'''{self._fmt(value)}  (当前)''')
                val_lbl.setStyleSheet(f'''color: {ACCENT_H}; font-size: 16px; font-weight: bold;''')
                continue
            (result, fmt) = convert(value, self.current_cat, from_idx, i)
            if result is None:
                val_lbl.setText('— 无数据')
                val_lbl.setStyleSheet(f'''color: {TEXT_G}; font-size: 16px;''')
                continue
            val_lbl.setText(fmt)
            val_lbl.setStyleSheet(f'''color: {TEXT_W}; font-size: 16px; font-weight: bold;''')
    def _copy_value(self, lbl):
        text = lbl.text().split('  ')[0].strip()
        if text:
            if text not in ('—', '无效', '— 无数据'):
                clipboard = QApplication.clipboard()
                clipboard.setText(text)
                lbl.setText(f'''{text}   ✓已复制''')
                lbl.setStyleSheet(f'''color: {COPIED}; font-size: 16px; font-weight: bold;''')
                QTimer.singleShot(1200, self._update)
                return None
    def _set_source(self, idx):
        '''点击结果行单位名：该单位变源单位，并把该行当前值填回输入框（反向换算）'''
        if not 0 <= idx < len(self._result_labels):
            return None
        shown = self._result_labels[idx][1].text()
        val = shown.replace('  (当前)', '').replace('   ✓已复制', '').strip()
        if not val or val in ('—', '— 无数据'):
            return None
        if idx != self.from_idx and 0 <= idx < len(self._unit_btns):
            self.from_idx = idx
            self._style_unit_btns()
        self.input_field.setText(val)
        self.input_field.setFocus()
    def _copy_all(self):
        '''复制全部结果为多行文本'''
        lines = []
        for name_lbl, val_lbl in self._result_labels:
            v = val_lbl.text().replace('  (当前)', '').replace('   ✓已复制', '').replace('— 无数据', '').strip()
            if v and v != '—':
                lines.append(f'''{name_lbl.text()}  =  {v}''')
        if not lines:
            return None
        QApplication.clipboard().setText('\n'.join(lines))
        self.hint_label.setText(f'''已复制全部 {len(lines)} 行结果 ✓''')
        self.hint_label.setStyleSheet(f'''color: {COPIED}; font-size: 9px;''')
        QTimer.singleShot(1500, self._update)
    def _show_history(self):
        '''弹出最近 10 次换算菜单，点击恢复'''
        cfg = _load_config()
        hist = cfg.get('history')
        if not isinstance(hist, list) or not hist:
            self.hint_label.setText('暂无历史记录')
            return None
        menu = QMenu(self)
        menu.setStyleSheet(f'''
            QMenu {{ background: {CARD_BG}; color: {TEXT_W}; border: 1px solid {BORDER}; }}
            QMenu::item {{ padding: 5px 18px; }}
            QMenu::item:selected {{ background: {ACCENT}; }}
        ''')
        for h in hist[:10]:
            if not isinstance(h, dict) or h.get('cat') not in CAT_ORDER:
                continue
            units = CATEGORIES[h['cat']]['units']
            idx = h.get('from_idx')
            uname = units[idx]['name'].split(' (')[0] if isinstance(idx, int) and 0 <= idx < len(units) else '?'
            act = menu.addAction(f'''{CATEGORIES[h['cat']]['name']} · {h.get('text', '')} {uname}''')
            act.setData(h)
        chosen = menu.exec(self.btn_history.mapToGlobal(self.btn_history.rect().bottomLeft()))
        if chosen is None:
            return None
        h = chosen.data()
        self._switch_cat(h['cat'])
        fi = h.get('from_idx')
        units = CATEGORIES[h['cat']]['units']
        if isinstance(fi, int) and 0 <= fi < len(units) and fi != self.from_idx:
            self.from_idx = fi
            self._style_unit_btns()
        self.input_field.setText(h.get('text', ''))
        self._update()
        self._persist_state()
    def _on_swatch(self, key):
        '''点击主题色圆点：就地换肤，不重建窗口（v3.5）'''
        if key in THEME_ORDER:
            if key != get_theme_key():
                set_theme_key(key)
                _apply_theme(key)
                self._style_all()
                return None
        else:
            return None
        return None
    def _style_all(self):
        '''就地换肤：按当前模块级 token 重刷全部控件样式（不重建窗口，v3.5）'''
        self.setStyleSheet(f'''background: {BG};''')
        self._title.setStyleSheet(f'''color: {TEXT_W}; font-size: 15px; font-weight: bold;''')
        cur = get_theme_key()
        for k, b in self._swatches.items():
            sel = k == cur
            ring = f'''2px solid {TEXT_W}''' if sel else f'''1px solid {BORDER}'''
            hover = '' if sel else f'''QPushButton:hover {{ border: 2px solid {TEXT_W}; }}'''
            b.setStyleSheet(f'''QPushButton {{ background: {THEMES[k]['ACCENT']}; border-radius: 10px; border: {ring}; }} {hover}''')
        self._chip_on = f'''QPushButton {{ background: {ACCENT}; color: #ffffff; border: 1px solid {ACCENT}; border-radius: 4px; font-size: 11px; font-weight: bold; }}'''
        self._chip_off = f'''QPushButton {{ background: {CARD_BG}; color: {TEXT_G}; border: 1px solid {BORDER}; border-radius: 4px; font-size: 11px; }}QPushButton:hover {{ color: {ACCENT_H}; border-color: {ACCENT}; }}'''
        for k, b in self._chips.items():
            b.setStyleSheet(self._chip_on if b.isChecked() else self._chip_off)
        self._unit_btn_on = f'''QPushButton {{ background: {ACCENT}; color: #ffffff; border: 1px solid {ACCENT}; border-radius: 4px; font-size: 11px; font-weight: bold; }}'''
        self._unit_btn_off = f'''QPushButton {{ background: {CARD_BG}; color: {TEXT_W}; border: 1px solid {BORDER}; border-radius: 4px; font-size: 11px; }}QPushButton:hover {{ border-color: {ACCENT}; color: {ACCENT_H}; }}'''
        self._style_unit_btns()
        self.input_field.setStyleSheet(INPUT_STYLE)
        self._sep1.setStyleSheet(f'''background: {BORDER};''')
        self._sep2.setStyleSheet(f'''background: {BORDER};''')
        btn_style = f'''QPushButton {{ background: {CARD_BG}; color: {TEXT_G}; border: 1px solid {BORDER}; border-radius: 4px; font-size: 10px; }}QPushButton:hover {{ color: {ACCENT_H}; border-color: {ACCENT}; }}'''
        self.btn_copy_all.setStyleSheet(btn_style)
        self.btn_history.setStyleSheet(btn_style)
        self._wm.setStyleSheet(f'''color: {WM}; font-size: 9px;''')
        self._rebuild_result_rows()
        self._update()
    def _fmt(self, val):
        if val == 0:
            return '0'
        a = abs(val)
        if a >= 1e15:
            return f'''{val:.0f}'''
        if a >= 1e12:
            return f'''{val:.1f}'''
        if a >= 1e9:
            return f'''{val:.2f}'''
        if a >= 1e6:
            return f'''{val:.3f}'''
        if a >= 1e4:
            return f'''{val:.4f}'''
        if a >= 100:
            return f'''{val:.4f}'''.rstrip('0').rstrip('.')
        if a >= 1:
            return f'''{val:.6f}'''.rstrip('0').rstrip('.')
        if a >= 0.01:
            return f'''{val:.8f}'''.rstrip('0').rstrip('.')
        if a >= 0.0001:
            return f'''{val:.10f}'''.rstrip('0').rstrip('.')
        return f'''{val:.15f}'''.rstrip('0').rstrip('.')
_win = None

def _launch():
    global _win
    _win = MainWindow()
    _win.show()
def main():
    app = QApplication(sys.argv)
    app.setFont(QFont('Microsoft YaHei', 10))
    _launch()
    sys.exit(app.exec())
if __name__ == '__main__':
    main()
