# Reconstructed from bytecode by split_decompile.py
# torque_ui.relaxed.pyc

'''

螺栓拧紧力矩工具 V2.0 数据校准版

依据 T=K·F·d 紧固通则式 (F=0.65σy·As, 基准 K=0.20) | σy: GB/T 3098.1 | 螺距: GB/T 193 | 自攻: GB/T 5280

'''
import sys
import os
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QTabWidget, QInputDialog, QComboBox, QFrame, QPushButton, QScrollArea, QVBoxLayout, QHBoxLayout, QLineEdit, QDialog, QButtonGroup, QRadioButton, QGroupBox, QTextEdit, QSizePolicy, QSpacerItem, QMessageBox, QGraphicsDropShadowEffect, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap, QFont, QIcon
from PySide6.QtCore import Qt, QSize, QRectF, QProcess, QTimer
from PySide6.QtGui import QFont, QPainter, QPen, QColor, QPainterPath, QBrush
import torque_data as TD
from theme import get_palette, build_style as _theme_build_style, load_theme_name, save_theme_name, THEME_ORDER
_p = get_palette()
BG = _p['BG']
FG = _p['TEXT']
ACCENT = _p['ACCENT']
ACCENT_H = _p['ACCENT_H']
BORDER = _p['BORDER']
CARD = _p['CARD']
TEXT_G = _p['TEXT2']
SUCCESS = _p['GREEN']
WARN = _p['ORANGE']
DANGER = _p['RED']
CARD_H = _p['CARD_H']
(GREEN, ORANGE, RED, TEXT, TEXT2) = (SUCCESS, WARN, DANGER, FG, TEXT_G)

def _tab_icon(name):
    '''加载 Tab 图标 (优先 32px, 回退 24px)'''
    base = os.path.join(os.path.dirname(__file__), 'assets', 'tab_icons')
    for size in (32, 24, 48):
        p = os.path.join(base, f'''{name}_{size}.png''')
        if os.path.exists(p):

            return None, QIcon(p)
        return QIcon()
STYLESHEET = []['\nQWidget { background: '][f'''{BG}''']['; color: '][f'''{FG}''']['; font-family: "Microsoft YaHei","SimHei",sans-serif; font-size: 13px; }\nQScrollArea { border: none; background: transparent; }\nQScrollBar:vertical { background: '][f'''{BG}''']['; width: 8px; }\nQScrollBar::handle:vertical { background: '][f'''{BORDER}''']['; border-radius: 4px; min-height: 30px; }\nQScrollBar::handle:vertical:hover { background: '][f'''{ACCENT}''']['; }\nQLabel { background: transparent; }\nQTextEdit { background: '][f'''{CARD}''']['; color: '][f'''{FG}''']['; border: 1px solid '][f'''{BORDER}''']['; border-radius: 6px; padding: 8px; font-family: "Consolas","Courier New",monospace; }\nQTabWidget::pane { border: none; background: '][f'''{BG}''']['; }\nQTabBar::tab { background: '][f'''{CARD}''']['; color: '][f'''{TEXT_G}''']['; border: 1px solid '][f'''{BORDER}''']['; border-bottom: none; border-top-left-radius: 8px; border-top-right-radius: 8px; padding: 8px 16px; margin-right: 2px; font-size: 13px; }\nQTabBar::tab:hover { background: '][f'''{BORDER}''']['; color: '][f'''{FG}''']['; }\nQTabBar::tab:selected { background: '][f'''{BG}''']['; color: '][f'''{ACCENT_H}''']['; border-color: '][f'''{ACCENT}''']([]['\nQWidget { background: '][f'''{BG}''']['; color: '][f'''{FG}''']['; font-family: "Microsoft YaHei","SimHei",sans-serif; font-size: 13px; }\nQScrollArea { border: none; background: transparent; }\nQScrollBar:vertical { background: '][f'''{BG}''']['; width: 8px; }\nQScrollBar::handle:vertical { background: '][f'''{BORDER}''']['; border-radius: 4px; min-height: 30px; }\nQScrollBar::handle:vertical:hover { background: '][f'''{ACCENT}''']['; }\nQLabel { background: transparent; }\nQTextEdit { background: '][f'''{CARD}''']['; color: '][f'''{FG}''']['; border: 1px solid '][f'''{BORDER}''']['; border-radius: 6px; padding: 8px; font-family: "Consolas","Courier New",monospace; }\nQTabWidget::pane { border: none; background: '][f'''{BG}''']['; }\nQTabBar::tab { background: '][f'''{CARD}''']['; color: '][f'''{TEXT_G}''']['; border: 1px solid '][f'''{BORDER}''']['; border-bottom: none; border-top-left-radius: 8px; border-top-right-radius: 8px; padding: 8px 16px; margin-right: 2px; font-size: 13px; }\nQTabBar::tab:hover { background: '][f'''{BORDER}''']['; color: '][f'''{FG}''']['; }\nQTabBar::tab:selected { background: '][f'''{BG}''']['; color: '][f'''{ACCENT_H}''']['; border-color: '][f'''{ACCENT}''']['; font-weight: bold; }\n'])
COMBO_STYLE = f'''\n    QComboBox {{ background: {CARD}; color: {FG}; border: 1px solid {BORDER};\n        border-radius: 6px; padding: 0 28px 0 12px; font-size: 13px; min-height: 30px; }}\n    QComboBox:hover {{ border-color: {ACCENT}; }}\n    QComboBox::drop-down {{ border: none; width: 28px; }}\n    QComboBox::down-arrow {{\n        image: url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAR0lEQVR4nGNgGAWMyEHQ1TXrP7FBUlaWBtbLhE2QWM0YBpADmNAFCLkCXZ6JGEX4xJkYKARMuCTQbcPlKiYGWoMuEtLGEAUAsU0RVRoUWYwAAAAASUVORK5CYII=);\n        width: 12px; height: 12px; right: 8px; }}\n    QComboBox QAbstractItemView {{ background: {CARD}; color: {FG};\n        border: 1px solid {BORDER}; selection-background-color: {ACCENT}; padding: 4px; }}\n'''
PRESET_BTN_STYLE = f'''\n    QPushButton {{\n        background: {CARD}; color: {TEXT_G}; border: 1px solid {BORDER};\n        border-radius: 6px; padding: 5px 12px; font-size: 12px;\n    }}\n    QPushButton:hover {{ border-color: {ACCENT}; color: {ACCENT_H}; }}\n    QPushButton:checked {{ background: {ACCENT}; color: white; border-color: {ACCENT}; }}\n'''
CARD_STYLE = f'''QFrame#card {{ background: {CARD}; border: 1px solid {BORDER}; border-radius: 10px; }}'''
import personal_store as PS
import personal_ui
UNITS = [
    ('N·m', 1),
    ('kgf·m', 0.10197),
    ('lbf·ft', 0.73756)]

def fmt_t(v, u_idx, dec):
    (name, f) = UNITS[u_idx]
    return f'''{round(v * f, dec)} {name}'''
WRENCH_RANGES = [
    5,
    10,
    20,
    50,
    100,
    200,
    300,
    500,
    1000,
    2000]

def wrench_range_suggest(vmax_n):
    '''量程需覆盖最大值 1.1 倍 (目标值落在量程 20%~80% 为佳)'''
    need = vmax_n * 1.1
    for r in WRENCH_RANGES:
        if r >= need:

            return None, r
        return None
class ScenarioCard:
    '''工况场景选择 + 结果显示'''

    def __init__(self, on_change_cb):
        super().__init__()
        self.on_change_cb = on_change_cb
        self.setObjectName('card')
        self.setStyleSheet(CARD_STYLE)
        self.setMinimumHeight(120)
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(14, 12, 14, 12)
        title_row = QHBoxLayout()
        title = QLabel('[场景] 工况场景')
        title.setStyleSheet(f'''color: {ACCENT}; font-size: 14px; font-weight: bold;''')
        title_row.addWidget(title)
        title_row.addStretch()
        self.scenario_desc = QLabel('')
        self.scenario_desc.setStyleSheet(f'''color: {TEXT_G}; font-size: 11px;''')
        self.scenario_desc.setWordWrap(True)
        title_row.addWidget(self.scenario_desc)
        layout.addLayout(title_row)
        self.scenario_combo = QComboBox()
        self.scenario_combo.setStyleSheet(COMBO_STYLE)
        self.scenario_combo.setMinimumWidth(200)
        for s in TD.SCENARIOS:
            self.scenario_combo.addItem(s)
            self.scenario_combo.currentTextChanged.connect(self._on_scenario_changed)
            layout.addWidget(self.scenario_combo)
            self.scenario_result = QLabel('')
            self.scenario_result.setStyleSheet(f'''color: {SUCCESS}; font-size: 13px; font-weight: bold; padding: 4px 0;''')
            self.scenario_result.setWordWrap(True)
            layout.addWidget(self.scenario_result)
            self.ov_btn = QPushButton('▾ 全部场景对应扭矩')
            self.ov_btn.setStyleSheet(f'''QPushButton {{ background: transparent; color: {ACCENT}; border: none; font-size: 11px; padding: 0; text-align: left; }}''')
            self.ov_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self.ov_btn.clicked.connect(self._toggle_overview)
            layout.addWidget(self.ov_btn)
            self.ov_label = QLabel('')
            self.ov_label.setStyleSheet(f'''color: {TEXT_G}; font-size: 11px;''')
            self.ov_label.setWordWrap(True)
            self.ov_label.setVisible(False)
            layout.addWidget(self.ov_label)
            self._on_scenario_changed()
            return None
    def _on_scenario_changed(self):
        scenario = self.scenario_combo.currentText()
        s = TD.SCENARIOS.get(scenario, { })
        self.scenario_desc.setText(s.get('desc', ''))
        self.on_change_cb(scenario)
    def get_scenario(self):
        return self.scenario_combo.currentText()
    def _toggle_overview(self):
        vis = not self.ov_label.isVisible()
        self.ov_label.setVisible(vis)
        self.ov_btn.setText('▴ 收起场景一览' if vis else '▾ 全部场景对应扭矩')
    def update_overview(self, vrec_base, u_idx):
        '''刷新全部场景一览 (基于未乘场景系数的推荐值, 随 K/规格变化)。'''
        if not vrec_base is not None:
            self.ov_label.setText('')
            return None
        parts = TD.SCENARIOS.items()()
        self.ov_label.setText('   |   '.join(parts))
    def update_result(self, vmin, vmax, vrec, note, grade, size_str, k_val, bolt_type, u_idx, sigma_y):
        """更新场景结果。
            vmin/vmax/vrec: 场景调整后的值
            grade: 强度等级 (如 '8.8')
            size_str: 规格字符串 (如 'M6', 'M8×1')
            k_val: 实际摩擦系数
            sigma_y: 屈服强度 MPa (★自定义材料直接传入; 缺省按标准等级查)
            """
        if not vmin is not None:
            self.scenario_result.setText('无数值')
            self.scenario_result.setStyleSheet(f'''color: {TEXT_G}; font-size: 13px;''')
            return None
        yield_pct = None
        pct_txt = ''
        flag = ''
        col = SUCCESS
        if grade and size_str and vrec > 0:
            import re
            import math
            m = re.match('M(\\d+)(?:×([\\d.]+))?', size_str)
            if m:
                d = int(m.group(1))
                sigma = sigma_y if sigma_y else TD.get_yield_strength(grade)
                if sigma and d > 0 and k_val > 0:
                    p = float(m.group(2)) if m.group(2) else TD._coarse_pitch(d)
                    As = (math.pi / 4) * (d - 0.9382 * p) ** 2
                    F_preload = vrec * 1000 / (k_val * d)
                    F_yield = sigma * As
                    yield_pct = round((F_preload / F_yield) * 100)
                    if yield_pct >= 65:
                        flag = ' ⚠接近屈服,有滑丝/断裂风险'
                        col = DANGER
                    elif yield_pct >= 50:
                        flag = ' (偏高)'
                        col = WARN
                    else:
                        flag = ''
                        col = SUCCESS
                    pct_txt = f'''  (预紧约{yield_pct}%螺栓屈服{flag})'''
        self.scenario_result.setText(f'''场景推荐: {fmt_t(vrec, u_idx)}{pct_txt}  |  {note}''')
        self.scenario_result.setStyleSheet(f'''color: {col}; font-size: 13px; font-weight: bold;''')
    __classcell__ = None
class HexTab:
    bolt_kind = 'hex'

    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(14, 14, 14, 14)
        preset_layout = QHBoxLayout()
        preset_layout.addWidget(QLabel('常用规格:'))
        self.preset_btns = []
        for size in ('M6', 'M8', 'M10', 'M12', 'M16', 'M20'):
            btn = QPushButton(size)
            btn.setCheckable(True)
            btn.setStyleSheet(PRESET_BTN_STYLE)
            None((lambda checked = None, s = None: self._preset_clicked(s)))
            preset_layout.addWidget(btn)
            self.preset_btns.append(btn)
            preset_layout.addStretch()
            self.layout.addLayout(preset_layout)
            param_card = QFrame()
            param_card.setObjectName('card')
            param_card.setStyleSheet(CARD_STYLE)
            row0 = QHBoxLayout()
            row0.setSpacing(12)
            row0.setContentsMargins(14, 6, 14, 2)
            row0.addWidget(QLabel('螺纹:'))
            self.thread_combo = QComboBox()
            self.thread_combo.setStyleSheet(COMBO_STYLE)
            self.thread_combo.setMinimumWidth(80)
            self.thread_combo.addItems([
                '粗牙',
                '细牙'])
            self.thread_combo.currentIndexChanged.connect(self._on_thread_changed)
            row0.addWidget(self.thread_combo)
            row0.addStretch()
            row1 = QHBoxLayout()
            row1.setSpacing(12)
            row1.setContentsMargins(14, 4, 14, 4)
            lbl_size = QLabel('规格:')
            lbl_size.setMinimumHeight(30)
            lbl_size.setAlignment(Qt.AlignVCenter)
            row1.addWidget(lbl_size)
            self.size_combo = QComboBox()
            self.size_combo.setStyleSheet(COMBO_STYLE)
            self.size_combo.setMinimumWidth(140)
            self.size_combo.currentIndexChanged.connect(self._on_size_combo_changed)
            row1.addWidget(self.size_combo)
            self.pitch_lbl = QLabel('螺距:')
            self.pitch_lbl.setVisible(False)
            row1.addWidget(self.pitch_lbl)
            self.pitch_combo = QComboBox()
            self.pitch_combo.setStyleSheet(COMBO_STYLE)
            self.pitch_combo.setMinimumWidth(90)
            self.pitch_combo.currentIndexChanged.connect(self._update)
            self.pitch_combo.setVisible(False)
            row1.addWidget(self.pitch_combo)
            row1.addStretch()
            row2 = QHBoxLayout()
            row2.setSpacing(12)
            row2.setContentsMargins(14, 4, 14, 10)
            row2.addWidget(QLabel('等级:'))
            self.grade_combo = QComboBox()
            self.grade_combo.setStyleSheet(COMBO_STYLE)
            self.grade_combo.setMinimumWidth(80)
            self.grade_combo.addItems(TD.GRADES['hex'])
        idx = TD.GRADES['hex'].index('8.8') if '8.8' in TD.GRADES['hex'] else 0
        self.grade_combo.setCurrentIndex(idx)
        self.grade_combo.currentIndexChanged.connect(self._update)
        row2.addWidget(self.grade_combo)
        row2.addWidget(QLabel('摩擦K:'))
        self.k_combo = QComboBox()
        self.k_combo.setStyleSheet(COMBO_STYLE)
        self.k_combo.setMinimumWidth(200)
        self._k_values = list(TD.TORQUE_COEFFICIENT.values())
        self._custom_k = None
        self._k_prev_idx = 0
        self.k_combo.addItems(list(TD.TORQUE_COEFFICIENT.keys()) + [
            '自定义 K 值…'])
        self.k_combo.currentIndexChanged.connect(self._on_k_changed)
        row2.addWidget(self.k_combo)
        row2.addStretch()
        self._reload_custom_grades()
        param_layout = QVBoxLayout(param_card)
        param_layout.setSpacing(0)
        param_layout.setContentsMargins(0, 0, 0, 0)
        param_layout.addLayout(row0)
        param_layout.addLayout(row1)
        param_layout.addLayout(row2)
        self.layout.addWidget(param_card)
        self.scenario_card = None((lambda s = None: self._update()))
        self.layout.addWidget(self.scenario_card)
        self.cmp_card = personal_ui.PersonalCompareCard(on_save_cb = self._save_to_personal)
        None((lambda : self.parent_window.goto_personal_tab()))
        self.layout.addWidget(self.cmp_card)
        res_card = QFrame()
        res_card.setObjectName('card')
        res_card.setStyleSheet(CARD_STYLE)
        res_layout = QVBoxLayout(res_card)
        res_layout.setSpacing(8)
        res_layout.setContentsMargins(16, 16, 16, 16)
        std_title = QLabel('[计算] 理论拧紧扭矩')
        std_title.setStyleSheet(f'''color: {TEXT_G}; font-size: 12px; font-weight: bold;''')
        res_layout.addWidget(std_title)
        std_note = QLabel('按 T=K·F·d 生成 (F=0.65σy·As, 基准 K=0.20), 细牙按 As 比推算')
        std_note.setStyleSheet(f'''color: {TEXT_G}; font-size: 11px;''')
        res_layout.addWidget(std_note)
        row1 = QHBoxLayout()
        lbl_rec = QLabel('推荐力矩')
        lbl_rec.setStyleSheet(f'''color: {TEXT_G}; font-size: 13px;''')
        row1.addWidget(lbl_rec)
        row1.addStretch()
        self.val_rec = QLabel('- N·m')
        self.val_rec.setMinimumHeight(54)
        self.val_rec.setStyleSheet(f'''color: {ACCENT_H}; font-size: 32px; font-weight: bold;''')
        row1.addWidget(self.val_rec)
        res_layout.addLayout(row1)
        row_minmax = QHBoxLayout()
        self.val_min = QLabel('-')
        self.val_min.setStyleSheet(f'''color: {FG}; font-size: 16px;''')
        row_minmax.addWidget(QLabel('最小力矩:'))
        row_minmax.addWidget(self.val_min)
        row_minmax.addStretch()
        self.val_max = QLabel('-')
        self.val_max.setStyleSheet(f'''color: {FG}; font-size: 16px;''')
        row_minmax.addWidget(QLabel('最大力矩:'))
        row_minmax.addWidget(self.val_max)
        res_layout.addLayout(row_minmax)
        row_pre = QHBoxLayout()
        lbl_pre = QLabel('预紧力 (推荐扭矩下):')
        lbl_pre.setStyleSheet(f'''color: {TEXT_G}; font-size: 12px;''')
        row_pre.addWidget(lbl_pre)
        row_pre.addStretch()
        self.val_preload = QLabel('-')
        self.val_preload.setStyleSheet(f'''color: {FG}; font-size: 18px; font-weight: bold;''')
        row_pre.addWidget(self.val_preload)
        res_layout.addLayout(row_pre)
        row_tools = QHBoxLayout()
        row_tools.addWidget(QLabel('单位:'))
        self.unit_combo = QComboBox()
        self.unit_combo.setStyleSheet(COMBO_STYLE)
        (lambda .0: [ u[0] for u in .0 ])(UNITS())
        self.unit_combo.currentIndexChanged.connect(self._update)
        row_tools.addWidget(self.unit_combo)
        row_tools.addStretch()
        self.copy_btn = QPushButton('复制结果')
        self.copy_btn.setMinimumHeight(32)
        self.copy_btn.setStyleSheet(PRESET_BTN_STYLE)
        self.copy_btn.clicked.connect(self._copy_result)
        row_tools.addWidget(self.copy_btn)
        res_layout.addLayout(row_tools)
        self.k_hint = QLabel('')
        self.k_hint.setWordWrap(True)
        self.k_hint.setStyleSheet(f'''color: {WARN}; font-size: 11px; font-weight: bold;''')
        self.k_hint.setVisible(False)
        res_layout.addWidget(self.k_hint)
        s1 = QFrame()
        s1.setFrameShape(QFrame.HLine)
        s1.setStyleSheet(f'''background: {BORDER}; max-height: 1px;''')
        res_layout.addWidget(s1)
        row4 = QHBoxLayout()
        self.grade_info = QLabel('')
        self.grade_info.setStyleSheet(f'''color: {TEXT_G}; font-size: 11px;''')
        row4.addWidget(self.grade_info)
        row4.addStretch()
        self.estimate_lbl = QLabel('')
        self.estimate_lbl.setStyleSheet(f'''color: {TEXT_G}; font-size: 11px;''')
        row4.addWidget(self.estimate_lbl)
        res_layout.addLayout(row4)
        self.tip = QLabel('选择参数后自动显示力矩值')
        self.tip.setAlignment(Qt.AlignCenter)
        self.tip.setStyleSheet(f'''color: {TEXT_G}; font-size: 12px; padding-top: 4px;''')
        res_layout.addWidget(self.tip)
        self.disc = QLabel('外六角: 紧固通则式生成, F=0.65σy·As, 基准 K=0.20, 细牙按 As 比推算 | 前提: 有效啮合长度≥1d')
        self.fine_warn = QLabel('')
        self.fine_warn.setAlignment(Qt.AlignCenter)
        self.fine_warn.setStyleSheet(f'''color: {WARN}; font-size: 11px; font-weight: bold;''')
        res_layout.addWidget(self.fine_warn)
        self.disc.setAlignment(Qt.AlignCenter)
        self.disc.setStyleSheet(f'''color: {WARN}; font-size: 11px;''')
        res_layout.addWidget(self.disc)
        self.layout.addWidget(res_card)
        self.layout.addStretch()
        self._on_thread_changed()
        self._update()
    def _preset_clicked(self, size):
        for btn in self.preset_btns:
            btn.setChecked(btn.text() == size)
            idx = self.size_combo.findText(size)
            if idx >= 0:
                self.size_combo.setCurrentIndex(idx)
                return None
            return None
    def _reload_custom_grades(self):
        '''把个人库自定义材料追加进等级下拉 (★前缀), 数据变化后重建。'''
        cur = self.grade_combo.currentText()
        for i in range(self.grade_combo.count() - 1, -1, -1):
            if self.grade_combo.itemText(i).startswith('★'):
                self.grade_combo.removeItem(i)
            for m in PS.list_materials():
                self.grade_combo.addItem('★' + m['name'])
                idx = self.grade_combo.findText(cur)
                if idx >= 0:
                    self.grade_combo.setCurrentIndex(idx)
                    return None
                return None
    def _save_to_personal(self, thread_type, spec, grade_material, smart_rec):
        '''把当前智能查询结果作为底稿存入个人库。'''
        if not grade_material:
            pass
        preset = dict(thread_type = thread_type, spec = spec, grade_material = ''.lstrip('★'), t_rec = smart_rec, scenario = self.scenario_card.get_scenario())
        dlg = personal_ui.RecordDialog(self.parent_window, preset = preset)
    # WARNING: Decompyle incomplete
    def _fine_diameters(self, lst):
        seen = []
        for s in lst:
            d = s.split('×')[0]
            if d not in seen:
                seen.append(d)
            return seen
    def _repopulate_pitch(self, fine_list):
        d = self.size_combo.currentText()
        pitches = fine_list()
        self.pitch_combo.blockSignals(True)
        self.pitch_combo.clear()
        self.pitch_combo.addItems(pitches)
        self.pitch_combo.blockSignals(False)
    def _current_size_str(self):
        if self.thread_combo.currentText() == '细牙':
            return f'''{self.size_combo.currentText()}×{self.pitch_combo.currentText()}'''
        return None.size_combo.currentText()
    def _on_size_combo_changed(self):
        if self.thread_combo.currentText() == '细牙':
            self._repopulate_pitch(TD.FINE_THREAD_HEX)
        self._update()
    def _on_thread_changed(self):
        '''切换螺纹类型: 细牙=选直径+独立螺距下拉'''
        fine = self.thread_combo.currentText() == '细牙'
        self.pitch_lbl.setVisible(fine)
        self.pitch_combo.setVisible(fine)
        self.size_combo.blockSignals(True)
        self.size_combo.clear()
        if fine:
            self.size_combo.addItems(self._fine_diameters(TD.FINE_THREAD_HEX))
        else:
            self.size_combo.addItems(TD.SIZES['hex'])
        self.size_combo.blockSignals(False)
        if fine:
            self._repopulate_pitch(TD.FINE_THREAD_HEX)
        self._update()
    def _on_k_changed(self):
        pass


    def _copy_result(self):
        k_show = self._custom_k if self._custom_k else self._k_values[self.k_combo.currentIndex()]
        txt = f'''{self._current_size_str()} {self.grade_combo.currentText()} K={k_show}: 推荐 {self.val_rec.text()} / 最小 {self.val_min.text()} / 最大 {self.val_max.text()} / 预紧力 {self.val_preload.text()}'''
        QApplication.clipboard().setText(txt)
        self.copy_btn.setText('已复制 ✓')
        None(None, (lambda : self.copy_btn.setText('复制结果')))
    def _update(self):
        if not hasattr(self, 'val_rec'):
            return None
        size = None._current_size_str()
        grade = self.grade_combo.currentText()
        is_fine = self.thread_combo.currentText() == '细牙'
        custom_mat = PS.get_material(grade[1:]) if grade.startswith('★') else None
        if custom_mat:
            t = TD.calc_torque_from_sigma(custom_mat['sigma_y'], size)
        elif is_fine:
            t = TD.calc_fine_thread_torque(grade, size)
        else:
            t = TD.get_torque('hex', size, grade)
        if not t[0] is not None:
            self.val_rec.setText('- N·m')
            self.val_min.setText('-')
            self.val_max.setText('-')
            self.val_preload.setText('-')
            self.k_hint.setVisible(False)
            self.grade_info.setText('')
            self.estimate_lbl.setText('')
            self.tip.setText('无数值')
            self.scenario_card.update_result(None, None, None, '', 0)
            self.scenario_card.update_overview(None, self.unit_combo.currentIndex())
            self.cmp_card.update_match(None, '', '', None)
            self._smart_ctx = None
            if is_fine:
                self.disc.setText(f'''细牙{size} 无粗牙基准数据(粗牙表覆盖M6~M48),无法计算''')
                self.fine_warn.setText('')
            return None
        (vmin, vrec, vmax) = None
        k_val = self._custom_k if self._custom_k else self._k_values[self.k_combo.currentIndex()]
        k_ratio = k_val / 0.2
        vmin_r = round(vmin * k_ratio, 1)
        vrec_r = round(vrec * k_ratio, 1)
        vmax_r = round(vmax * k_ratio, 1)
        u = self.unit_combo.currentIndex()
        self.val_rec.setText(fmt_t(vrec_r, u))
        self.val_min.setText(fmt_t(vmin_r, u))
        self.val_max.setText(fmt_t(vmax_r, u))

        try:
            d_mm = int(size.split('×')[0][1:])
            F_pre = vrec_r * 1000 / (k_val * d_mm)
            self.val_preload.setText(f'''≈ {F_pre / 1000:.1f} kN''')
        except Exception:
            self.val_preload.setText('-')

        if abs(k_val - 0.2) > 1e-09:
            if k_val < 0.2:
                pct_f = round((0.2 / k_val - 1) * 100)
                pct_t = round((1 - k_val / 0.2) * 100)
                self.k_hint.setText(f'''⚠ 低摩擦(K={k_val}): 扭矩应较基准降 {pct_t}%; 若仍按 K=0.20 的扭矩拧, 预紧力将暴涨约 {pct_f}% —— 润滑螺栓务必按本页数值''')
            else:
                pct_t = round((k_val / 0.2 - 1) * 100)
                self.k_hint.setText(f'''⚠ 高摩擦(K={k_val}): 扭矩需较基准增 {pct_t}% 才能达到同等预紧力, 注意防拧断''')
            self.k_hint.setVisible(True)
        else:
            self.k_hint.setVisible(False)
        if custom_mat:
            sb = custom_mat.get('sigma_b')
            self.grade_info.setText(f'''个人自定义 σy={custom_mat['sigma_y']:.0f}MPa''' + f''' | σb={sb:.0f}MPa''' if sb else '')
        else:
            sigma_y = TD.get_yield_strength(grade)
            sigma_t = TD.get_tensile_strength(grade)
            if sigma_y:
                self.grade_info.setText(f'''屈服{sigma_y}MPa | 抗拉{sigma_t}MPa''')
        if custom_mat:
            self.estimate_lbl.setText('')
        else:

            try:
                mm = int(size.split('×')[0][1:])
                est = TD.estimate_torque(grade, mm, k_val)
                if is_fine:
                    self.estimate_lbl.setText(f'''经验公式估算: {est} N·m (计算值)''')
                else:
                    self.estimate_lbl.setText(f'''经验公式估算: {est} N·m''')
            except:
                self.estimate_lbl.setText('')

            if is_fine:
                self.disc.setText(f'''细牙{size} 力矩基于GB/T 193螺距+公式计算(计算值),建议对照标准原文核验''')
                self.fine_warn.setText('⚠ 细牙螺纹: 力矩按应力面积比推算(略高于同径粗牙), 建议对照标准原文')
            else:
                self.disc.setText('外六角: 紧固通则式生成, F=0.65σy·As, 基准 K=0.20, 细牙按 As 比推算 | 前提: 有效啮合长度≥1d')
                self.fine_warn.setText('')
        adj_t = (vmin_r, vrec_r, vmax_r)
        scenario = self.scenario_card.get_scenario()
        result = TD.apply_scenario(adj_t, scenario)
        if result:
            (svmin, svrec, svmax, note) = result
            self.scenario_card.update_result(svmin, svmax, svrec, note, grade, size, k_val, 'hex', self.unit_combo.currentIndex(), sigma_y = custom_mat['sigma_y'] if custom_mat else None)
        if vrec_r > 500:
            self.tip.setText('!! 大力矩,必须使用扭力扳手')
            self.tip.setStyleSheet(f'''color: {DANGER}; font-size: 12px;''')
        elif vrec_r > 100:
            self.tip.setText('建议使用扭力扳手')
            self.tip.setStyleSheet(f'''color: {WARN}; font-size: 12px;''')
        elif vrec_r > 20:
            self.tip.setText('建议使用扭力扳手或定扭矩扳手')
            self.tip.setStyleSheet(f'''color: {TEXT_G}; font-size: 12px;''')
        else:
            self.tip.setText('普通扳手即可,注意手感控制')
            self.tip.setStyleSheet(f'''color: {SUCCESS}; font-size: 12px;''')
        wr = wrench_range_suggest(vmax_r)
        if wr:
            self.tip.setText(self.tip.text() + f''' | 扳手量程建议 0~{wr} N·m''')
        self.scenario_card.update_overview(vrec_r, self.unit_combo.currentIndex())
        self.cmp_card.update_match(vrec_r, '细牙' if is_fine else '粗牙', size, grade, cur_scenario = self.scenario_card.get_scenario())
        self._smart_ctx = dict(page = '外六角螺栓' if self.bolt_kind == 'hex' else '内六角螺钉', thread_type = '细牙' if is_fine else '粗牙', spec = size, grade_material = grade, sigma_y = custom_mat['sigma_y'] if custom_mat else TD.get_yield_strength(grade), size_str = size, k_val = k_val, smart_rec = vrec_r, scenario = self.scenario_card.get_scenario())
    __classcell__ = None
class SocketTab:
    bolt_kind = 'socket'

    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(14, 14, 14, 14)
        preset_layout = QHBoxLayout()
        preset_layout.addWidget(QLabel('常用规格:'))
        self.preset_btns = []
        for size in ('M6', 'M8', 'M10', 'M12', 'M16', 'M24'):
            btn = QPushButton(size)
            btn.setCheckable(True)
            btn.setStyleSheet(PRESET_BTN_STYLE)
            None((lambda checked = None, s = None: self._preset_clicked(s)))
            preset_layout.addWidget(btn)
            self.preset_btns.append(btn)
            preset_layout.addStretch()
            self.layout.addLayout(preset_layout)
            param_card = QFrame()
            param_card.setObjectName('card')
            param_card.setStyleSheet(CARD_STYLE)
            row0 = QHBoxLayout()
            row0.setSpacing(12)
            row0.setContentsMargins(14, 6, 14, 2)
            row0.addWidget(QLabel('螺纹:'))
            self.thread_combo = QComboBox()
            self.thread_combo.setStyleSheet(COMBO_STYLE)
            self.thread_combo.setMinimumWidth(80)
            self.thread_combo.addItems([
                '粗牙',
                '细牙'])
            self.thread_combo.currentIndexChanged.connect(self._on_thread_changed)
            row0.addWidget(self.thread_combo)
            row0.addStretch()
            row1 = QHBoxLayout()
            row1.setSpacing(12)
            row1.setContentsMargins(14, 4, 14, 4)
            lbl_size = QLabel('规格:')
            lbl_size.setMinimumHeight(30)
            lbl_size.setAlignment(Qt.AlignVCenter)
            row1.addWidget(lbl_size)
            self.size_combo = QComboBox()
            self.size_combo.setStyleSheet(COMBO_STYLE)
            self.size_combo.setMinimumWidth(140)
            self.size_combo.currentIndexChanged.connect(self._on_size_combo_changed)
            row1.addWidget(self.size_combo)
            self.pitch_lbl = QLabel('螺距:')
            self.pitch_lbl.setVisible(False)
            row1.addWidget(self.pitch_lbl)
            self.pitch_combo = QComboBox()
            self.pitch_combo.setStyleSheet(COMBO_STYLE)
            self.pitch_combo.setMinimumWidth(90)
            self.pitch_combo.currentIndexChanged.connect(self._update)
            self.pitch_combo.setVisible(False)
            row1.addWidget(self.pitch_combo)
            row1.addStretch()
            row2 = QHBoxLayout()
            row2.setSpacing(12)
            row2.setContentsMargins(14, 4, 14, 10)
            row2.addWidget(QLabel('等级:'))
            self.grade_combo = QComboBox()
            self.grade_combo.setStyleSheet(COMBO_STYLE)
            self.grade_combo.setMinimumWidth(80)
            self.grade_combo.addItems(TD.GRADES['socket'])
        idx = TD.GRADES['socket'].index('8.8') if '8.8' in TD.GRADES['socket'] else 0
        self.grade_combo.setCurrentIndex(idx)
        self.grade_combo.currentIndexChanged.connect(self._update)
        row2.addWidget(self.grade_combo)
        row2.addWidget(QLabel('摩擦K:'))
        self.k_combo = QComboBox()
        self.k_combo.setStyleSheet(COMBO_STYLE)
        self.k_combo.setMinimumWidth(200)
        self._k_values = list(TD.TORQUE_COEFFICIENT.values())
        self._custom_k = None
        self._k_prev_idx = 0
        self.k_combo.addItems(list(TD.TORQUE_COEFFICIENT.keys()) + [
            '自定义 K 值…'])
        self.k_combo.currentIndexChanged.connect(self._on_k_changed)
        row2.addWidget(self.k_combo)
        row2.addStretch()
        self._reload_custom_grades()
        param_layout = QVBoxLayout(param_card)
        param_layout.setSpacing(0)
        param_layout.setContentsMargins(0, 0, 0, 0)
        param_layout.addLayout(row0)
        param_layout.addLayout(row1)
        param_layout.addLayout(row2)
        self.layout.addWidget(param_card)
        self.scenario_card = None((lambda s = None: self._update()))
        self.layout.addWidget(self.scenario_card)
        self.cmp_card = personal_ui.PersonalCompareCard(on_save_cb = self._save_to_personal)
        None((lambda : self.parent_window.goto_personal_tab()))
        self.layout.addWidget(self.cmp_card)
        res_card = QFrame()
        res_card.setObjectName('card')
        res_card.setStyleSheet(CARD_STYLE)
        res_layout = QVBoxLayout(res_card)
        res_layout.setSpacing(8)
        res_layout.setContentsMargins(16, 16, 16, 16)
        std_title = QLabel('[计算] 理论拧紧扭矩')
        std_title.setStyleSheet(f'''color: {TEXT_G}; font-size: 12px; font-weight: bold;''')
        res_layout.addWidget(std_title)
        std_note = QLabel('内六角螺钉力矩参考, 粗牙查表, 细牙按应力面积比推算')
        std_note.setStyleSheet(f'''color: {TEXT_G}; font-size: 11px;''')
        res_layout.addWidget(std_note)
        row1 = QHBoxLayout()
        lbl_rec = QLabel('推荐力矩')
        lbl_rec.setStyleSheet(f'''color: {TEXT_G}; font-size: 13px;''')
        row1.addWidget(lbl_rec)
        row1.addStretch()
        self.val_rec = QLabel('- N·m')
        self.val_rec.setMinimumHeight(54)
        self.val_rec.setStyleSheet(f'''color: {ACCENT_H}; font-size: 32px; font-weight: bold;''')
        row1.addWidget(self.val_rec)
        res_layout.addLayout(row1)
        row_minmax = QHBoxLayout()
        self.val_min = QLabel('-')
        self.val_min.setStyleSheet(f'''color: {FG}; font-size: 16px;''')
        row_minmax.addWidget(QLabel('最小力矩:'))
        row_minmax.addWidget(self.val_min)
        row_minmax.addStretch()
        self.val_max = QLabel('-')
        self.val_max.setStyleSheet(f'''color: {FG}; font-size: 16px;''')
        row_minmax.addWidget(QLabel('最大力矩:'))
        row_minmax.addWidget(self.val_max)
        res_layout.addLayout(row_minmax)
        row_pre = QHBoxLayout()
        lbl_pre = QLabel('预紧力 (推荐扭矩下):')
        lbl_pre.setStyleSheet(f'''color: {TEXT_G}; font-size: 12px;''')
        row_pre.addWidget(lbl_pre)
        row_pre.addStretch()
        self.val_preload = QLabel('-')
        self.val_preload.setStyleSheet(f'''color: {FG}; font-size: 18px; font-weight: bold;''')
        row_pre.addWidget(self.val_preload)
        res_layout.addLayout(row_pre)
        row_tools = QHBoxLayout()
        row_tools.addWidget(QLabel('单位:'))
        self.unit_combo = QComboBox()
        self.unit_combo.setStyleSheet(COMBO_STYLE)
        (lambda .0: [ u[0] for u in .0 ])(UNITS())
        self.unit_combo.currentIndexChanged.connect(self._update)
        row_tools.addWidget(self.unit_combo)
        row_tools.addStretch()
        self.copy_btn = QPushButton('复制结果')
        self.copy_btn.setMinimumHeight(32)
        self.copy_btn.setStyleSheet(PRESET_BTN_STYLE)
        self.copy_btn.clicked.connect(self._copy_result)
        row_tools.addWidget(self.copy_btn)
        res_layout.addLayout(row_tools)
        self.k_hint = QLabel('')
        self.k_hint.setWordWrap(True)
        self.k_hint.setStyleSheet(f'''color: {WARN}; font-size: 11px; font-weight: bold;''')
        self.k_hint.setVisible(False)
        res_layout.addWidget(self.k_hint)
        s1 = QFrame()
        s1.setFrameShape(QFrame.HLine)
        s1.setStyleSheet(f'''background: {BORDER}; max-height: 1px;''')
        res_layout.addWidget(s1)
        row4 = QHBoxLayout()
        self.grade_info = QLabel('')
        self.grade_info.setStyleSheet(f'''color: {TEXT_G}; font-size: 11px;''')
        row4.addWidget(self.grade_info)
        row4.addStretch()
        self.estimate_lbl = QLabel('')
        self.estimate_lbl.setStyleSheet(f'''color: {TEXT_G}; font-size: 11px;''')
        row4.addWidget(self.estimate_lbl)
        res_layout.addLayout(row4)
        self.tip = QLabel('选择参数后自动显示力矩值')
        self.tip.setAlignment(Qt.AlignCenter)
        self.tip.setStyleSheet(f'''color: {TEXT_G}; font-size: 12px; padding-top: 4px;''')
        res_layout.addWidget(self.tip)
        self.disc = QLabel('内六角: 紧固通则式生成, F=0.65σy·As, 基准 K=0.20, 细牙按 As 比推算 | 前提: 有效啮合长度≥1d')
        self.fine_warn = QLabel('')
        self.fine_warn.setAlignment(Qt.AlignCenter)
        self.fine_warn.setStyleSheet(f'''color: {WARN}; font-size: 11px; font-weight: bold;''')
        res_layout.addWidget(self.fine_warn)
        self.disc.setAlignment(Qt.AlignCenter)
        self.disc.setStyleSheet(f'''color: {WARN}; font-size: 11px;''')
        res_layout.addWidget(self.disc)
        self.layout.addWidget(res_card)
        self.layout.addStretch()
        self._on_thread_changed()
        self._update()
    def _preset_clicked(self, size):
        for btn in self.preset_btns:
            btn.setChecked(btn.text() == size)
            idx = self.size_combo.findText(size)
            if idx >= 0:
                self.size_combo.setCurrentIndex(idx)
                return None
            return None
    def _reload_custom_grades(self):
        '''把个人库自定义材料追加进等级下拉 (★前缀), 数据变化后重建。'''
        cur = self.grade_combo.currentText()
        for i in range(self.grade_combo.count() - 1, -1, -1):
            if self.grade_combo.itemText(i).startswith('★'):
                self.grade_combo.removeItem(i)
            for m in PS.list_materials():
                self.grade_combo.addItem('★' + m['name'])
                idx = self.grade_combo.findText(cur)
                if idx >= 0:
                    self.grade_combo.setCurrentIndex(idx)
                    return None
                return None
    def _save_to_personal(self, thread_type, spec, grade_material, smart_rec):
        '''把当前智能查询结果作为底稿存入个人库。'''
        if not grade_material:
            pass
        preset = dict(thread_type = thread_type, spec = spec, grade_material = ''.lstrip('★'), t_rec = smart_rec, scenario = self.scenario_card.get_scenario())
        dlg = personal_ui.RecordDialog(self.parent_window, preset = preset)
    # WARNING: Decompyle incomplete
    def _fine_diameters(self, lst):
        seen = []
        for s in lst:
            d = s.split('×')[0]
            if d not in seen:
                seen.append(d)
            return seen
    def _repopulate_pitch(self, fine_list):
        d = self.size_combo.currentText()
        pitches = fine_list()
        self.pitch_combo.blockSignals(True)
        self.pitch_combo.clear()
        self.pitch_combo.addItems(pitches)
        self.pitch_combo.blockSignals(False)
    def _current_size_str(self):
        if self.thread_combo.currentText() == '细牙':
            return f'''{self.size_combo.currentText()}×{self.pitch_combo.currentText()}'''
        return None.size_combo.currentText()
    def _on_size_combo_changed(self):
        if self.thread_combo.currentText() == '细牙':
            self._repopulate_pitch(TD.FINE_THREAD_SOCKET)
        self._update()
    def _on_thread_changed(self):
        '''切换螺纹类型: 细牙=选直径+独立螺距下拉'''
        fine = self.thread_combo.currentText() == '细牙'
        self.pitch_lbl.setVisible(fine)
        self.pitch_combo.setVisible(fine)
        self.size_combo.blockSignals(True)
        self.size_combo.clear()
        if fine:
            self.size_combo.addItems(self._fine_diameters(TD.FINE_THREAD_SOCKET))
        else:
            self.size_combo.addItems(TD.SIZES['socket'])
        self.size_combo.blockSignals(False)
        if fine:
            self._repopulate_pitch(TD.FINE_THREAD_SOCKET)
        self._update()
    def _on_k_changed(self):
        pass


    def _copy_result(self):
        k_show = self._custom_k if self._custom_k else self._k_values[self.k_combo.currentIndex()]
        txt = f'''{self._current_size_str()} {self.grade_combo.currentText()} K={k_show}: 推荐 {self.val_rec.text()} / 最小 {self.val_min.text()} / 最大 {self.val_max.text()} / 预紧力 {self.val_preload.text()}'''
        QApplication.clipboard().setText(txt)
        self.copy_btn.setText('已复制 ✓')
        None(None, (lambda : self.copy_btn.setText('复制结果')))
    def _update(self):
        if not hasattr(self, 'val_rec'):
            return None
        size = None._current_size_str()
        grade = self.grade_combo.currentText()
        is_fine = self.thread_combo.currentText() == '细牙'
        custom_mat = PS.get_material(grade[1:]) if grade.startswith('★') else None
        if custom_mat:
            t = TD.calc_torque_from_sigma(custom_mat['sigma_y'], size)
        elif is_fine:
            t = TD.calc_fine_thread_torque(grade, size, bolt_type = 'socket')
        else:
            t = TD.get_torque('socket', size, grade)
        if not t[0] is not None:
            self.val_rec.setText('- N·m')
            self.val_min.setText('-')
            self.val_max.setText('-')
            self.val_preload.setText('-')
            self.k_hint.setVisible(False)
            self.grade_info.setText('')
            self.estimate_lbl.setText('')
            self.tip.setText('无数值')
            self.scenario_card.update_result(None, None, None, '', 0)
            self.scenario_card.update_overview(None, self.unit_combo.currentIndex())
            self.cmp_card.update_match(None, '', '', None)
            self._smart_ctx = None
            if is_fine:
                self.disc.setText(f'''细牙{size} 无粗牙基准数据,无法计算''')
                self.fine_warn.setText('')
            return None
        (vmin, vrec, vmax) = None
        k_val = self._custom_k if self._custom_k else self._k_values[self.k_combo.currentIndex()]
        k_ratio = k_val / 0.2
        vmin_r = round(vmin * k_ratio, 1)
        vrec_r = round(vrec * k_ratio, 1)
        vmax_r = round(vmax * k_ratio, 1)
        u = self.unit_combo.currentIndex()
        self.val_rec.setText(fmt_t(vrec_r, u))
        self.val_min.setText(fmt_t(vmin_r, u))
        self.val_max.setText(fmt_t(vmax_r, u))

        try:
            d_mm = int(size.split('×')[0][1:])
            F_pre = vrec_r * 1000 / (k_val * d_mm)
            self.val_preload.setText(f'''≈ {F_pre / 1000:.1f} kN''')
        except Exception:
            self.val_preload.setText('-')

        if abs(k_val - 0.2) > 1e-09:
            if k_val < 0.2:
                pct_f = round((0.2 / k_val - 1) * 100)
                pct_t = round((1 - k_val / 0.2) * 100)
                self.k_hint.setText(f'''⚠ 低摩擦(K={k_val}): 扭矩应较基准降 {pct_t}%; 若仍按 K=0.20 的扭矩拧, 预紧力将暴涨约 {pct_f}% —— 润滑螺栓务必按本页数值''')
            else:
                pct_t = round((k_val / 0.2 - 1) * 100)
                self.k_hint.setText(f'''⚠ 高摩擦(K={k_val}): 扭矩需较基准增 {pct_t}% 才能达到同等预紧力, 注意防拧断''')
            self.k_hint.setVisible(True)
        else:
            self.k_hint.setVisible(False)
        if custom_mat:
            sb = custom_mat.get('sigma_b')
            self.grade_info.setText(f'''个人自定义 σy={custom_mat['sigma_y']:.0f}MPa''' + f''' | σb={sb:.0f}MPa''' if sb else '')
        else:
            sigma_y = TD.get_yield_strength(grade)
            sigma_t = TD.get_tensile_strength(grade)
            if sigma_y:
                self.grade_info.setText(f'''屈服{sigma_y}MPa | 抗拉{sigma_t}MPa''')
        if custom_mat:
            self.estimate_lbl.setText('')
        else:

            try:
                mm = int(size.split('×')[0][1:])
                est = TD.estimate_torque(grade, mm, k_val)
                if is_fine:
                    self.estimate_lbl.setText(f'''经验公式估算: {est} N·m (计算值)''')
                else:
                    self.estimate_lbl.setText(f'''经验公式估算: {est} N·m''')
            except:
                self.estimate_lbl.setText('')

            if is_fine:
                self.disc.setText(f'''细牙{size} 力矩基于GB/T 193螺距+公式计算(计算值),建议对照标准原文核验''')
                self.fine_warn.setText('⚠ 细牙螺纹: 力矩按应力面积比推算(略高于同径粗牙), 建议对照标准原文')
            else:
                self.disc.setText('内六角螺钉力矩参考 DIN 912 / ISO 4762 (K≈0.20), 粗牙查表, 细牙按应力面积比推算 | 前提: 有效啮合长度≥1d')
                self.fine_warn.setText('')
        adj_t = (vmin_r, vrec_r, vmax_r)
        scenario = self.scenario_card.get_scenario()
        result = TD.apply_scenario(adj_t, scenario)
        if result:
            (svmin, svrec, svmax, note) = result
            self.scenario_card.update_result(svmin, svmax, svrec, note, grade, size, k_val, 'socket', self.unit_combo.currentIndex(), sigma_y = custom_mat['sigma_y'] if custom_mat else None)
        if vrec_r > 500:
            self.tip.setText('!! 大力矩,必须使用扭力扳手')
            self.tip.setStyleSheet(f'''color: {DANGER}; font-size: 12px;''')
        elif vrec_r > 100:
            self.tip.setText('建议使用扭力扳手')
            self.tip.setStyleSheet(f'''color: {WARN}; font-size: 12px;''')
        elif vrec_r > 20:
            self.tip.setText('建议使用扭力扳手或定扭矩扳手')
            self.tip.setStyleSheet(f'''color: {TEXT_G}; font-size: 12px;''')
        else:
            self.tip.setText('普通扳手即可,注意手感控制')
            self.tip.setStyleSheet(f'''color: {SUCCESS}; font-size: 12px;''')
        wr = wrench_range_suggest(vmax_r)
        if wr:
            self.tip.setText(self.tip.text() + f''' | 扳手量程建议 0~{wr} N·m''')
        self.scenario_card.update_overview(vrec_r, self.unit_combo.currentIndex())
        self.cmp_card.update_match(vrec_r, '细牙' if is_fine else '粗牙', size, grade, cur_scenario = self.scenario_card.get_scenario())
        self._smart_ctx = dict(page = '外六角螺栓' if self.bolt_kind == 'hex' else '内六角螺钉', thread_type = '细牙' if is_fine else '粗牙', spec = size, grade_material = grade, sigma_y = custom_mat['sigma_y'] if custom_mat else TD.get_yield_strength(grade), size_str = size, k_val = k_val, smart_rec = vrec_r, scenario = self.scenario_card.get_scenario())
    __classcell__ = None
class SelfTapTab:

    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(14, 14, 14, 14)
        preset_layout = QHBoxLayout()
        preset_layout.addWidget(QLabel('常用规格:'))
        self.preset_btns = []
        for size in ('ST2.9', 'ST3.5', 'ST4.2', 'ST4.8', 'ST5.5', 'ST6.3'):
            btn = QPushButton(size)
            btn.setCheckable(True)
            btn.setStyleSheet(PRESET_BTN_STYLE)
            None((lambda checked = None, s = None: self._preset_clicked(s)))
            preset_layout.addWidget(btn)
            self.preset_btns.append(btn)
            preset_layout.addStretch()
            self.layout.addLayout(preset_layout)
            param_card = QFrame()
            param_card.setObjectName('card')
            param_card.setStyleSheet(CARD_STYLE)
            row1 = QHBoxLayout()
            row1.setSpacing(12)
            row1.setContentsMargins(14, 6, 14, 2)
            lbl_size = QLabel('规格:')
            lbl_size.setMinimumHeight(30)
            lbl_size.setAlignment(Qt.AlignVCenter)
            row1.addWidget(lbl_size)
            self.size_combo = QComboBox()
            self.size_combo.setStyleSheet(COMBO_STYLE)
            self.size_combo.setMinimumWidth(90)
            self.size_combo.currentIndexChanged.connect(self._on_size_changed)
            row1.addWidget(self.size_combo)
            row1.addStretch()
            row2 = QHBoxLayout()
            row2.setSpacing(12)
            row2.setContentsMargins(14, 4, 14, 10)
            row2.addWidget(QLabel('底材:'))
            self.mat_combo = QComboBox()
            self.mat_combo.setStyleSheet(COMBO_STYLE)
            self.mat_combo.setMinimumWidth(200)
            row2.addWidget(self.mat_combo)
            row2.addStretch()
            param_layout = QVBoxLayout(param_card)
            param_layout.setSpacing(0)
            param_layout.setContentsMargins(0, 0, 0, 0)
            param_layout.addLayout(row1)
            param_layout.addLayout(row2)
            self.layout.addWidget(param_card)
            self.scenario_card = None((lambda s = None: self._update()))
            self.layout.addWidget(self.scenario_card)
            self.cmp_card = personal_ui.PersonalCompareCard(on_save_cb = self._save_to_personal)
            None((lambda : self.parent_window.goto_personal_tab()))
            self.layout.addWidget(self.cmp_card)
            res_card = QFrame()
            res_card.setObjectName('card')
            res_card.setStyleSheet(CARD_STYLE)
            res_layout = QVBoxLayout(res_card)
            res_layout.setSpacing(8)
            res_layout.setContentsMargins(16, 16, 16, 16)
            row1 = QHBoxLayout()
            lbl_rec = QLabel('推荐拧紧力矩')
            lbl_rec.setStyleSheet(f'''color: {TEXT_G}; font-size: 13px;''')
            row1.addWidget(lbl_rec)
            row1.addStretch()
            self.val_rec = QLabel('- N·m')
            self.val_rec.setMinimumHeight(54)
            self.val_rec.setStyleSheet(f'''color: {ACCENT_H}; font-size: 32px; font-weight: bold;''')
            row1.addWidget(self.val_rec)
            res_layout.addLayout(row1)
            s1 = QFrame()
            s1.setFrameShape(QFrame.HLine)
            s1.setStyleSheet(f'''background: {BORDER}; max-height: 1px;''')
            res_layout.addWidget(s1)
            row2 = QHBoxLayout()
            lbl_min = QLabel('最小力矩:')
            lbl_min.setStyleSheet(f'''color: {TEXT_G}; font-size: 12px;''')
            row2.addWidget(lbl_min)
            row2.addStretch()
            self.val_min = QLabel('-')
            self.val_min.setStyleSheet(f'''color: {FG}; font-size: 18px; font-weight: bold;''')
            row2.addWidget(self.val_min)
            res_layout.addLayout(row2)
            row3 = QHBoxLayout()
            lbl_max = QLabel('最大力矩:')
            lbl_max.setStyleSheet(f'''color: {TEXT_G}; font-size: 12px;''')
            row3.addWidget(lbl_max)
            row3.addStretch()
            self.val_max = QLabel('-')
            self.val_max.setStyleSheet(f'''color: {FG}; font-size: 18px; font-weight: bold;''')
            row3.addWidget(self.val_max)
            res_layout.addLayout(row3)
            s2 = QFrame()
            s2.setFrameShape(QFrame.HLine)
            s2.setStyleSheet(f'''background: {BORDER}; max-height: 1px;''')
            res_layout.addWidget(s2)
            self.tip = QLabel('选择参数后自动显示力矩值')
            self.tip.setAlignment(Qt.AlignCenter)
            self.tip.setStyleSheet(f'''color: {TEXT_G}; font-size: 12px; padding-top: 4px;''')
            res_layout.addWidget(self.tip)
            self.disc = QLabel('自攻螺钉力矩为行业经验值, 仅供参考, 实际以工艺验证为准 | 前提: 啮合深度满足标准要求')
            self.disc.setAlignment(Qt.AlignCenter)
            self.disc.setStyleSheet(f'''color: {WARN}; font-size: 11px;''')
            res_layout.addWidget(self.disc)
            self.layout.addWidget(res_card)
            self.layout.addStretch()
            self.size_combo.addItems(TD.SIZES['self_tap'])
            self._on_size_changed()
            return None
    def _preset_clicked(self, size):
        for btn in self.preset_btns:
            btn.setChecked(btn.text() == size)
            idx = self.size_combo.findText(size)
            if idx >= 0:
                self.size_combo.setCurrentIndex(idx)
                return None
            return None
    def _reload_custom_grades(self):
        '''把个人库自定义材料追加进等级下拉 (★前缀), 数据变化后重建。'''
        cur = self.grade_combo.currentText()
        for i in range(self.grade_combo.count() - 1, -1, -1):
            if self.grade_combo.itemText(i).startswith('★'):
                self.grade_combo.removeItem(i)
            for m in PS.list_materials():
                self.grade_combo.addItem('★' + m['name'])
                idx = self.grade_combo.findText(cur)
                if idx >= 0:
                    self.grade_combo.setCurrentIndex(idx)
                    return None
                return None
    def _save_to_personal(self, thread_type, spec, grade_material, smart_rec):
        '''把当前智能查询结果作为底稿存入个人库。'''
        if not grade_material:
            pass
        preset = dict(thread_type = thread_type, spec = spec, grade_material = ''.lstrip('★'), t_rec = smart_rec, scenario = self.scenario_card.get_scenario())
        dlg = personal_ui.RecordDialog(self.parent_window, preset = preset)
    # WARNING: Decompyle incomplete
    def _on_size_changed(self):
        size = self.size_combo.currentText()
        mat_dict = TD.SELF_TAPPING.get(size, { })
        self.mat_combo.blockSignals(True)
        self.mat_combo.clear()
        for group_name in ('钢', '铝', '塑料'):
            materials = TD.SELF_TAP_MATERIAL_GROUPS.get(group_name, [])
            for mat in materials:
                if mat in mat_dict:
                    self.mat_combo.addItem(f'''[{group_name}] {mat}''')
                self.mat_combo.blockSignals(False)
                self._update()
                return None
    def _update(self):
        if not hasattr(self, 'val_rec'):
            return None
        size = None.size_combo.currentText()
        mat_text = self.mat_combo.currentText()
        material = mat_text.split('] ')[-1] if '] ' in mat_text else mat_text
        t = TD.get_torque('self_tap', size, material = material)
        if not t[0] is not None:
            self.val_rec.setText('- N·m')
            self.val_min.setText('-')
            self.val_max.setText('-')
            self.tip.setText('无数值')
            self.scenario_card.update_result(None, None, None, '', 0)
            self.scenario_card.update_overview(None, 0)
            self._smart_ctx = None
            return None
        (vmin, vrec, vmax) = None
        self.val_rec.setText(f'''{vrec} N·m''')
        self.val_min.setText(f'''{vmin} N·m''')
        self.val_max.setText(f'''{vmax} N·m''')
        scenario = self.scenario_card.get_scenario()
        result = TD.apply_scenario(t, scenario)
        if result:
            (svmin, svrec, svmax, note) = result
            self.scenario_card.update_result(svmin, svmax, svrec, note)
        self.scenario_card.update_overview(vrec, 0)
        self.cmp_card.update_match(vrec, '自攻', self.size_combo.currentText(), self.mat_combo.currentText(), cur_scenario = scenario)
        self._smart_ctx = dict(page = '自攻螺钉', thread_type = '自攻', spec = self.size_combo.currentText(), grade_material = material, sigma_y = None, size_str = self.size_combo.currentText(), k_val = None, smart_rec = vrec, scenario = scenario)
        if vrec > 5:
            self.tip.setText('建议使用扭力螺丝刀或定扭矩工具')
            self.tip.setStyleSheet(f'''color: {WARN}; font-size: 12px;''')
        elif vrec > 2:
            self.tip.setText('建议使用定扭矩电动螺丝刀')
            self.tip.setStyleSheet(f'''color: {TEXT_G}; font-size: 12px;''')
        else:
            self.tip.setText('注意控制力度,防止滑牙或底材破裂')
            self.tip.setStyleSheet(f'''color: {SUCCESS}; font-size: 12px;''')
        self.disc.setText('自攻螺钉力矩为行业经验值, 仅供参考, 实际以工艺验证为准 | 前提: 啮合深度满足标准要求')
        self.disc.setStyleSheet(f'''color: {WARN}; font-size: 11px;''')
    __classcell__ = None
class FormulaTab:

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(14, 14, 14, 14)
        title = QLabel('[计算] 拧紧力矩计算器 + 公式参考')
        title.setStyleSheet(f'''color: {ACCENT}; font-size: 18px; font-weight: bold; padding-bottom: 6px;''')
        self.layout.addWidget(title)
        calc_card = QFrame()
        calc_card.setObjectName('card')
        calc_card.setStyleSheet(CARD_STYLE)
        cv = QVBoxLayout(calc_card)
        cv.setContentsMargins(14, 10, 14, 10)
        cv.setSpacing(6)
        cv.addWidget(QLabel('按公式计算 (输入规格参数, 结果即时刷新):'))
        row_in = QHBoxLayout()
        row_in.setSpacing(10)

        def _labeled_input(label, placeholder, default):
            box = QVBoxLayout()
            lab = QLabel(label)
            lab.setStyleSheet(f'''color: {TEXT_G}; font-size: 11px;''')
            edit = QLineEdit()
            edit.setMinimumHeight(32)
            edit.setPlaceholderText(placeholder)
            edit.setText(default)
            edit.setStyleSheet(f'''QLineEdit {{ background: {CARD_H}; color: {FG}; border: 1px solid {BORDER}; border-radius: 6px; padding: 4px 8px; }}''')
            edit.textChanged.connect(self._calc_update)
            box.addWidget(lab)
            box.addWidget(edit)
            return (box, edit)
        (grade_box, self.calc_grade) = _labeled_input('等级 8.8/10.9/12.9', '8.8', '8.8')
        (d_box, self.calc_d) = _labeled_input('公称直径 d (mm)', '如 10', '10')
        (p_box, self.calc_p) = _labeled_input('螺距 p (mm, 0=粗牙自动)', '留空=粗牙', '')
        (k_box, self.calc_k) = _labeled_input('扭矩系数 K', '0.15~0.25', '0.20')
        for b in (grade_box, d_box, p_box, k_box):
            row_in.addLayout(b)
            cv.addLayout(row_in)
            self.calc_result = QLabel('')
            self.calc_result.setStyleSheet(f'''color: {SUCCESS}; font-size: 14px; font-weight: bold; padding: 4px 0;''')
            self.calc_result.setWordWrap(True)
            cv.addWidget(self.calc_result)
            self.calc_warn = QLabel('')
            self.calc_warn.setStyleSheet(f'''color: {WARN}; font-size: 11px;''')
            self.calc_warn.setWordWrap(True)
            cv.addWidget(self.calc_warn)
            self.layout.addWidget(calc_card)
            self._calc_update()
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setMinimumHeight(400)
            content = QWidget()
            content_layout = QVBoxLayout(content)
            content_layout.setSpacing(12)
            content_layout.setContentsMargins(0, 0, 0, 0)
            formulas = [
                ('⚠ 适用前提（必读）', '本工具数据基于以下前提条件:\n\n1. 螺纹有效啮合长度足够（通常≥1d，d=螺纹公称直径）\n2. 螺栓处于弹性工作范围内（预紧力<屈服强度）\n3. 被连接件刚度合理，不会因拧紧产生过大变形\n4. 螺纹精度符合标准（6g/6H或6h/6H）\n5. 摩擦系数已知且与所选K值匹配\n\n如有效啮合长度不足，可能发生螺纹滑牙/剥落，\n此时按本工具推荐值拧紧存在安全风险。\n\n数据来源: 按 T=K·F·d 紧固通则式生成, 外部公开力矩表族 (Verlinde/ISO 898-1 系) 仲裁 M6~M24 互差<5%'),
                ('基本公式', 'T = K × F × d\n\nT = 拧紧力矩 (N·m)\nK = 扭矩系数(与摩擦、润滑相关)\nF = 预紧力 (N)\nd = 螺纹公称直径 (mm)'),
                ('预紧力计算', 'F = 0.65 × σy × As\n\nσy = 屈服强度 (MPa)\nAs = 螺纹应力面积 (mm², 精确中径式)\n0.65 = 预紧力利用率 (常用区间 0.5~0.7σy 取中偏上限, 与 ISO 898-1 系公开力矩表锚点一致)'),
                ('应力面积(粗牙)', 'As = π/4 × (d - 0.9382p)²\n\np = 螺距 (mm)\n例: M10×1.5 → As = π/4 × (10 - 0.9382×1.5)² ≈ 58.0 mm²'),
                ('扭矩系数 K', 'K ≈ 0.20  干燥钢对钢\nK ≈ 0.15  润滑表面\nK ≈ 0.25  生锈/镀锌表面\nK ≈ 0.25  不锈钢\n\n注: K值受多种因素影响, 精确值需通过试验确定'),
                ('强度等级对照', '4.6 → 屈服240MPa 抗拉400MPa\n5.6 → 屈服300MPa 抗拉500MPa\n6.8 → 屈服480MPa 抗拉600MPa\n8.8 → 屈服640MPa 抗拉800MPa\n10.9 → 屈服940MPa 抗拉1040MPa\n12.9 → 屈服1100MPa 抗拉1220MPa'),
                ('工况场景说明', '标准推荐值(K=0.20档上限)约占螺栓屈服载荷75%\n场景系数作用于推荐值 (推荐档预紧约65%屈服):\n一般连接: 系数0.75 → 约49%屈服\n重要承载: 系数0.9 → 约59%屈服\n密封连接: 系数0.45 → 约29%屈服(防压碎密封)\n软材连接: 系数0.4 → 约26%屈服(铝/铜/塑料)\n薄壁连接: 系数0.5 → 约33%屈服(防变形)\n高温/振动: 系数0.95 → 约62%屈服(需防松)\n\n注: 屈服占比 = 预紧力/屈服载荷, 预紧力由T=K×F×d反算'),
                ('注意事项', '1. 本工具为理论估算, 不可直接作为安全件图纸/工艺依据\n2. 粗牙数据按通则式生成 (F=0.65σy·As, K=0.20), 细牙按 As 比推算\n3. 细牙螺纹+润滑工况对拧紧扭矩非常敏感, 必要时应做拧紧试验\n4. 安全关键连接(起重/高压/刹车)请按 VDI2230 完整计算\n5. 实际力矩受摩擦系数、润滑状态、温度等影响\n6. 重要连接应通过试验确定最佳力矩')]
            for title_text, content_text in formulas:
                card = QFrame()
                card.setMinimumHeight(80)
                card.setStyleSheet(f'''background: {CARD}; border: 1px solid {BORDER}; border-radius: 10px; padding: 14px;''')
                card_layout = QVBoxLayout(card)
                card_layout.setSpacing(4)
                card_layout.setContentsMargins(14, 10, 14, 10)
                t = QLabel(f'''<b>{title_text}</b>''')
                t.setStyleSheet(f'''color: {ACCENT}; font-size: 14px;''')
                card_layout.addWidget(t)
                c = QLabel(content_text)
                c.setWordWrap(True)
                c.setStyleSheet(f'''color: {FG}; font-size: 12px; font-family: \'Consolas\', monospace;''')
                card_layout.addWidget(c)
                content_layout.addWidget(card)
                content_layout.addStretch()
                scroll.setWidget(content)
                self.layout.addWidget(scroll)
                return None
    def _calc_update(self):
        '''计算器: T = K·F·d, F = 0.65·σy·As, As = π/4·((d2+d3)/2)² (精确中径式)'''
        import math

        try:
            grade = self.calc_grade.text().strip()
            d = float(self.calc_d.text())
            k = float(self.calc_k.text())
            p_txt = self.calc_p.text().strip()
            sigma_y = TD.YIELD_STRENGTH.get(grade)
            if not sigma_y is not None:
                self.calc_result.setText('等级请填 8.8 / 10.9 / 12.9')
                self.calc_warn.setText('')
                return None
            if None in ('', '0'):
                p = TD._coarse_pitch(int(d)) if d == int(d) else None
                p_note = '粗牙' if p else ''
                if not p is not None:
                    self.calc_result.setText('螺距未填且直径非整数, 无法确定粗牙螺距')
                    self.calc_warn.setText('')
                    return None
            p = float(p_txt)
            p_note = f'''螺距 {p}'''
            as_mm2 = (math.pi / 4) * (d - 0.9382 * p) ** 2
            F = 0.65 * sigma_y * as_mm2
            T = k * F * d / 1000
            self.calc_result.setText(f'''{grade} 级 | {p_note} | As={as_mm2:.1f} mm² | 预紧力 F={F:,.0f} N | 拧紧力矩 T={T:.1f} N·m''')
            warns = []
            if not  <= 0.1, k or 0.1, k <= 0.3:
                pass

            warns.append('K 常见范围 0.15(润滑)~0.25(干态/镀锌), 当前取值少见, 请核实')
            if p_txt not in ('', '0') and d == int(d) and p > TD._coarse_pitch(int(d)):
                warns.append('螺距大于粗牙螺距? 粗牙本身就是最大螺距, 请确认')
            if F > 0.85 * sigma_y * as_mm2:
                warns.append('预紧力已超 85% 屈服载荷(理论上限), 安全关键连接按 VDI2230 校核')
            self.calc_warn.setText('⚠ ' + '; '.join(warns) if warns else '')
            return None
        except ValueError:
            self.calc_result.setText('等待完整输入…')
            self.calc_warn.setText('')
            return None
    __classcell__ = None
class SettingsDialog:
    '''设置: 主题选择, 点击即存, 重启生效(打包版提示手动重开)'''

    def __init__(self, parent):
        super().__init__(parent)
        THEMES = THEMES
        _ORDER = THEME_ORDER
        import theme
        self.setWindowTitle('设置')
        self.setMinimumWidth(440)
        self.setMinimumHeight(460)
        self.setStyleSheet(f'''QDialog {{ background: {BG}; }}''')
        current = load_theme_name()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(8)
        title = QLabel('🎨 界面主题')
        title.setStyleSheet(f'''font-size:15px; font-weight:bold; color:{TEXT};''')
        layout.addWidget(title)
        self._group = QButtonGroup(self)
        self._rows = []
        for idx, name in enumerate(_ORDER):
            pal = THEMES[name]
            row = QFrame()
            row.setCursor(Qt.CursorShape.PointingHandCursor)
            rl = QHBoxLayout(row)
            rl.setContentsMargins(12, 8, 12, 8)
            rl.setSpacing(8)
            rb = QRadioButton(name)
            rb.setCursor(Qt.CursorShape.PointingHandCursor)
            self._group.addButton(rb, idx)
            rl.addWidget(rb)
            rl.addStretch()
            for key in ('BG', 'CARD', 'ACCENT', 'GREEN', 'ORANGE', 'RED'):
                chip = QFrame()
                chip.setFixedSize(20, 20)
                chip.setStyleSheet(f'''QFrame {{ background:{pal[key]}; border:1px solid {BORDER}; border-radius:4px; }}''')
                rl.addWidget(chip)
                layout.addWidget(row)
                self._rows.append((row, rb, name))
                None((lambda on = None, r = None, b = None: self._style_row(r, b, on)))
                self._style_row(row, rb, name == current)
                self._group.buttonClicked.connect(self._on_pick)
        frozen_hint = '（打包版保存后需手动重新打开工具）' if getattr(sys, 'frozen', False) else '（开发版会立即重启）'
        self.hint = QLabel(f'''点击主题立即保存; 切换主题需重新打开工具生效 {frozen_hint}''')
        self.hint.setStyleSheet(f'''color:{TEXT_G}; font-size:11px;''')
        layout.addWidget(self.hint)
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self.restart_btn = QPushButton('保存主题' if getattr(sys, 'frozen', False) else '保存并立即重启')
        self.restart_btn.setFixedHeight(34)
        self.restart_btn.clicked.connect(self._save_and_restart)
        btn_row.addWidget(self.restart_btn)
        close_btn = QPushButton('关闭')
        close_btn.setFixedHeight(34)
        close_btn.setStyleSheet(f'''\n            QPushButton {{ background:{CARD_H}; color:{TEXT_G}; border:1px solid {BORDER}; }}\n            QPushButton:hover {{ border:1px solid {ACCENT}; color:{ACCENT}; }}\n        ''')
        close_btn.clicked.connect(self.reject)
        btn_row.addWidget(close_btn)
        layout.addLayout(btn_row)
    def _style_row(self, row, rb, on):
        if on:
            row.setStyleSheet(f'''QFrame {{ background:{CARD_H}; border:2px solid {ACCENT}; border-radius:8px; }}QFrame QRadioButton {{ color:{ACCENT}; font-size:13px; font-weight:bold; background:transparent; }}''')
            rb.setChecked(True)
            return None
        None.setStyleSheet(f'''QFrame {{ background:{CARD}; border:1px solid {BORDER}; border-radius:8px; }}QFrame QRadioButton {{ color:{FG}; font-size:13px; background:transparent; }}''')
    def _current_name(self):
        _ORDER = THEME_ORDER
        import theme
        return _ORDER[self._group.checkedId()]
    def _on_pick(self, btn):
        save_theme_name(self._current_name())
        self.hint.setText(f'''✓ 已保存「{self._current_name()}」, 重启后生效''')
    def _save_and_restart(self):
        save_theme_name(self._current_name())
        if getattr(sys, 'frozen', False):
            QMessageBox.information(self, '主题已保存', f'''主题已保存为「{self._current_name()}」。\n打包版请手动重新打开工具以生效。''')
            QApplication.instance().quit()
            return None
        None.startDetached(sys.executable, [
            os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app.py')])
        QApplication.instance().quit()
    __classcell__ = None
class MainWindow:
    _wrap_scroll = (lambda w: pass)()

    def __init__(self):
        super().__init__()
        self.setWindowTitle('螺栓拧紧力矩工具 V2.5')
        self.setMinimumSize(900, 780)
        self.resize(1150, 840)
        self.setStyleSheet(STYLESHEET)
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(14, 10, 14, 4)
        title_lbl = QLabel('螺栓拧紧力矩工具')
        title_lbl.setStyleSheet(f'''font-size:15px; font-weight:bold; color:{ACCENT}; background:transparent;''')
        top_bar.addWidget(title_lbl)
        top_bar.addStretch()
        gear_btn = QPushButton('⚙ 设置')
        gear_btn.setFixedHeight(30)
        gear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        gear_btn.setStyleSheet(f'''\n            QPushButton {{\n                background:{CARD}; color:{FG}; border:1px solid {BORDER};\n                border-radius:15px; font-size:13px; font-weight:bold; padding:0 14px;\n            }}\n            QPushButton:hover {{ border:1px solid {ACCENT}; color:{ACCENT}; background:{CARD_H}; }}\n        ''')
        gear_btn.setToolTip('设置(主题等)')
        gear_btn.clicked.connect(self._show_settings)
        top_bar.addWidget(gear_btn)
        main_layout.addLayout(top_bar)
        self.tabs = QTabWidget()
        self._last_smart_index = 0
        self.tabs.setMinimumHeight(580)
        self.tabs.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.tabs.setIconSize(QSize(28, 28))
        self.hex_tab = HexTab(self)
        self.socket_tab = SocketTab(self)
        self.selftap_tab = SelfTapTab(self)
        self.formula_tab = FormulaTab()
        self.personal_tab = personal_ui.PersonalTab(self, refresh_cb = self.on_personal_changed)
        self.tabs.addTab(self._wrap_scroll(self.hex_tab), _tab_icon('hex_bolt'), '外六角螺栓')
        self.tabs.addTab(self._wrap_scroll(self.socket_tab), _tab_icon('socket_cap'), '内六角螺钉')
        self.tabs.addTab(self._wrap_scroll(self.selftap_tab), _tab_icon('self_tap'), '自攻螺钉')
        self.tabs.addTab(self._wrap_scroll(self.formula_tab), _tab_icon('formula'), '计算/公式')
        self.tabs.addTab(self._wrap_scroll(self.personal_tab), _tab_icon('book'), '个人库')
        self.tabs.currentChanged.connect(self._on_tab_changed)
        main_layout.addWidget(self.tabs)
        footer = QWidget()
        footer.setMinimumHeight(44)
        footer.setStyleSheet(f'''background: {CARD}; border-top: 1px solid {BORDER};''')
        footer_layout = QVBoxLayout(footer)
        footer_layout.setContentsMargins(14, 4, 14, 4)
        footer_layout.setSpacing(2)
        info = QLabel('数据来源: 紧固通则式计算 (σy: GB/T 3098.1, 螺距: GB/T 193) | 公开力矩表族交叉核对')
        info.setStyleSheet(f'''color: {TEXT_G}; font-size: 11px;''')
        info.setAlignment(Qt.AlignCenter)
        footer_layout.addWidget(info)
        disclaimer = QLabel('⚠ 前提: 有效啮合长度≥1d | 理论估算, 不可直接作为安全件图纸/工艺依据')
        disclaimer.setStyleSheet(f'''color: {TEXT_G}; font-size: 11px;''')
        disclaimer.setAlignment(Qt.AlignCenter)
        disclaimer.setWordWrap(True)
        footer_layout.addWidget(disclaimer)
        main_layout.addWidget(footer)
    def on_personal_changed(self):
        '''个人库数据变化后: 重建各页签自定义材料项 + 刷新对比卡。'''
        for tab in (self.hex_tab, self.socket_tab):
            tab._reload_custom_grades()
            for tab in (self.hex_tab, self.socket_tab, self.selftap_tab):
                tab._update()
                return None
    def goto_personal_tab(self):
        '''跳转到个人库页签 (V2.5 修复: 页签页是 _wrap_scroll 容器,
            必须用 index 跳转, setCurrentWidget(裸 personal_tab) 会静默失效)。'''
        self.tabs.setCurrentIndex(4)
    def _on_tab_changed(self, *_):
        '''切页签联动 (V2.4): 记住最后停留的智能页签; 进个人库时刷新引用行。'''
        i = self.tabs.currentIndex()
        if i in (0, 1, 2):
            self._last_smart_index = i
        if i == 4 or hasattr(self.personal_tab, '_refresh_ref'):
            self.personal_tab._refresh_ref()
            return None
        return None
    def current_smart_ctx(self):
        '''最后停留智能页签的查询上下文 (供个人库备忘录引用); 无则 None。'''
        tab = {
            0: self.hex_tab,
            1: self.socket_tab,
            2: self.selftap_tab }.get(getattr(self, '_last_smart_index', 0))
        return getattr(tab, '_smart_ctx', None) if tab else None
    def _show_settings(self):
        dlg = SettingsDialog(self)
        dlg.exec()
    __classcell__ = None

