# Reconstructed from bytecode by split_decompile.py
# personal_ui.relaxed.pyc

'''
个人库 UI（V2.2）
- PersonalCompareCard  三页签结果区内嵌的「智能 vs 个人」对比卡片
- PersonalTab          个人库管理页签（扭矩记录 + 自定义材料）
- RecordDialog / MaterialDialog / ImportDialog
依赖 torque_ui 的样式常量（由 MainWindow 延迟导入, 避免循环引用）。
'''
import os
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFrame, QComboBox, QPushButton, QLineEdit, QTableWidget, QTableWidgetItem, QDialog, QFormLayout, QDoubleSpinBox, QFileDialog, QMessageBox, QHeaderView, QDialogButtonBox, QRadioButton, QPlainTextEdit, QAbstractItemView, QStackedWidget, QMenu
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QBrush
import personal_store as PS
import personal_excel as PX
import torque_data as TD
from torque_ui import BG, FG, ACCENT, ACCENT_H, BORDER, CARD, TEXT_G, SUCCESS, WARN, DANGER, CARD_H, COMBO_STYLE, PRESET_BTN_STYLE, CARD_STYLE
_BTN = f'''\nQPushButton {{\n    background: {CARD_H}; color: {FG}; border: 1px solid {BORDER};\n    border-radius: 6px; padding: 6px 14px; font-size: 12px;\n}}\nQPushButton:hover {{ border: 1px solid {ACCENT}; color: {ACCENT}; }}\n'''
_TABLE = f'''\nQTableWidget {{\n    background: {CARD}; color: {FG}; border: 1px solid {BORDER};\n    border-radius: 8px; gridline-color: {BORDER}; font-size: 12px;\n}}\nQTableWidget::item {{ padding: 4px; }}\nQTableWidget::item:selected {{ background: {CARD_H}; color: {ACCENT}; }}\nQHeaderView::section {{\n    background: {CARD_H}; color: {TEXT_G}; border: none;\n    border-bottom: 1px solid {BORDER}; padding: 6px; font-size: 12px;\n}}\n'''

def _fmt(v):
    if v in (None, ''):
        return '—'
    if None(v, float):
        return f'''{v:.1f}'''
    return None(v)
class NumItem:
    '''带数值权重的表格项: 显示原文, 排序按数值 (V2.5 列头排序用)。'''

    def __init__(self, text, val):
        super().__init__(text)
        self._val = float('-inf') if not val is not None else float(val)
    def __lt__(self, other):
        ov = getattr(other, '_val', None)
        if not ov is not None:
            return super().__lt__(other)
        return None._val < ov
    __classcell__ = None
class PersonalCompareCard:
    '''update_match(智能推荐值, 螺纹类型, 规格, 等级材质) 后自动刷新。'''

    def __init__(self, on_save_cb, parent):
        super().__init__(parent)
        self.setObjectName('card')
        self.setStyleSheet(CARD_STYLE)
        self.on_save_cb = on_save_cb
        self._ctx = None
        v = QVBoxLayout(self)
        v.setContentsMargins(14, 10, 14, 10)
        v.setSpacing(6)
        head = QHBoxLayout()
        title = QLabel('★ 个人库对比')
        title.setStyleSheet(f'''color: {ACCENT}; font-size: 13px; font-weight: bold;''')
        head.addWidget(title)
        head.addStretch()
        self.match_lbl = QLabel('')
        self.match_lbl.setStyleSheet(f'''color: {TEXT_G}; font-size: 11px;''')
        head.addWidget(self.match_lbl)
        self.save_btn = QPushButton('＋ 存入当前查询')
        self.save_btn.setStyleSheet(_BTN)
        self.save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_btn.clicked.connect(self._save_current)
        head.addWidget(self.save_btn)
        self.manage_btn = QPushButton('管理个人库')
        self.manage_btn.setStyleSheet(_BTN)
        self.manage_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        head.addWidget(self.manage_btn)
        v.addLayout(head)
        self.body = QHBoxLayout()
        self.body.setSpacing(8)
        v.addLayout(self.body)
        self.setMinimumHeight(130)
        self.update_match(None, '', '', None)
    def clear_body(self):
        pass


    def _chip(self, bg, border, title, value, sub, val_color):
        box = QFrame()
        box.setStyleSheet(f'''QFrame {{ background: {bg}; border: 1px solid {border}; border-radius: 8px; }}''')
        bv = QVBoxLayout(box)
        bv.setContentsMargins(10, 6, 10, 6)
        bv.setSpacing(1)
        t = QLabel(title)
        t.setStyleSheet(f'''color: {TEXT_G}; font-size: 11px; border: none; background: transparent;''')
        val = QLabel(value)
        val.setStyleSheet(f'''color: {val_color}; font-size: 17px; font-weight: bold; border: none; background: transparent;''')
        s = QLabel(sub)
        s.setStyleSheet(f'''color: {TEXT_G}; font-size: 10px; border: none; background: transparent;''')
        bv.addWidget(t)
        bv.addWidget(val)
        bv.addWidget(s)
        box.setMinimumHeight(76)
        return box
    def update_match(self, smart_rec, thread_type, spec, grade_material, cur_scenario):
        self._ctx = (thread_type, spec, grade_material, smart_rec)
        self.clear_body()
        if smart_rec:
            pass
        has_ctx = bool(spec)
        self.save_btn.setVisible(has_ctx)
        if not has_ctx:
            self.match_lbl.setText('选择参数后显示个人库对比')
            tip = QLabel('—')
            tip.setStyleSheet(f'''color: {TEXT_G}; font-size: 12px;''')
            self.body.addWidget(tip)
            self.body.addStretch()
            return None
        rows = None

        try:
            rows = PS.match_records(thread_type, spec, None, limit = 3)
        except Exception:
            rows = []

        if not rows:
            self.match_lbl.setText('个人库暂无此规格记录')
            tip = QLabel('录入试验值/工艺卡后, 这里会与智能值并排对比')
            tip.setWordWrap(True)
            tip.setStyleSheet(f'''color: {TEXT_G}; font-size: 11px;''')
            self.body.addWidget(tip)
            self.body.addStretch()
            return None
        None.match_lbl.setText(f'''已匹配个人记录 {len(rows)} 条''')
        self.body.addWidget(self._chip(CARD_H, BORDER, '智能推荐 (底账)', f'''{smart_rec:.1f}''', 'T=K·F·d', ACCENT_H))
        for r in rows:
            diff = ((r['t_rec'] - smart_rec) / smart_rec) * 100 if smart_rec else 0
            col = SUCCESS if abs(diff) <= 10 else WARN
            sign = '+' if diff >= 0 else ''
            sub = f'''较智能值 {sign}{diff:.1f}%'''
            if cur_scenario:
                if not r.get('scenario'):
                    pass
                if '' == cur_scenario:
                    sub = '◎场景匹配 · ' + sub
            if r.get('note'):
                sub = r['note'][:12] + ' · ' + sub
            if not r.get('created_at'):
                pass
            date = ''[:10]
            self.body.addWidget(self._chip(CARD_H, col, f'''个人·{r['source']} {r['grade_material']}''', f'''{r['t_rec']:.1f}''', sub, col))
            self.body.addStretch()
            return None
    def _save_current(self):
        pass
    # WARNING: Decompyle incomplete
    __classcell__ = None
class CustomTorqueBox:
    '''填入实测/工艺扭矩 → 反算预紧力、屈服占比、与智能引用值差异。
    数据仅入个人库, 不参与也不修改智能底账。'''

    def __init__(self, on_saved_cb, parent):
        super().__init__(parent)
        self.on_saved_cb = on_saved_cb
        self._ctx = None
        v = QVBoxLayout(self)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(6)
        row = QHBoxLayout()
        lbl = QLabel('我的实测/工艺扭矩:')
        lbl.setStyleSheet(f'''color: {TEXT_G}; font-size: 12px;''')
        self.edit = QLineEdit()
        self.edit.setPlaceholderText('填入你自己的扭矩值 (N·m)…')
        self.edit.setStyleSheet(f'''QLineEdit {{ background: {CARD_H}; color: {FG}; border: 1px solid {BORDER}; border-radius: 6px; padding: 4px 8px; }}''')
        self.edit.setMinimumHeight(32)
        self.edit.setMaximumWidth(170)
        self.edit.textChanged.connect(self._recalc)
        row.addWidget(lbl)
        row.addWidget(self.edit)
        self.save_btn = QPushButton('存为个人记录')
        self.save_btn.setStyleSheet(_BTN)
        self.save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_btn.setVisible(False)
        self.save_btn.clicked.connect(self._save)
        row.addWidget(self.save_btn)
        row.addStretch()
        v.addLayout(row)
        self.analysis = QLabel('')
        self.analysis.setWordWrap(True)
        self.analysis.setStyleSheet(f'''color: {TEXT_G}; font-size: 12px;''')
        v.addWidget(self.analysis)
    def update_ctx(self, **kw):
        if not kw:
            pass
        self._ctx = None
        self.save_btn.setVisible(bool(kw.get('smart_rec')))
        self._recalc()
    def _recalc(self):
        if not self._ctx:
            self.analysis.setText('先在上方选择要引用的智能查询 (或直接切到智能页签选好参数)')
            self.analysis.setStyleSheet(f'''color: {TEXT_G}; font-size: 12px;''')
            return None
        txt = None.edit.text().strip().replace(',', '')
        if not txt:
            self.analysis.setText(f'''智能引用 {self._ctx.get('smart_rec', 0):.1f} N·m | 填入你的值即可反算对比''')
            self.analysis.setStyleSheet(f'''color: {TEXT_G}; font-size: 12px;''')
            return None

        try:
            t_val = float(txt)
        except ValueError:
            self.analysis.setText('⚠ 数值格式不对, 请填数字')
            self.analysis.setStyleSheet(f'''color: {DANGER}; font-size: 12px;''')
            return None

        if t_val <= 0:
            self.analysis.setText('⚠ 扭矩应为正数')
            self.analysis.setStyleSheet(f'''color: {DANGER}; font-size: 12px;''')
            return None
        c = None._ctx
        parts = [
            f'''你的 {t_val:.1f} N·m''']
        smart = c.get('smart_rec')
        if smart:
            diff = ((t_val - smart) / smart) * 100
            sign = '+' if diff >= 0 else ''
            parts.append(f'''较智能引用 {smart:.1f} {sign}{diff:.1f}%''')
        import re
        import math
        if not c.get('k_val'):
            pass
        k = 0.2
        if not c.get('size_str'):
            pass
        m = re.match('M(\\d+)(?:×([\\d.]+))?', '')
        if m and k > 0:
            d = int(m.group(1))
            F = t_val * 1000 / (k * d)
            parts.append(f'''预紧≈{F / 1000:.1f} kN''')
            sigma = c.get('sigma_y')
            if sigma:
                p = float(m.group(2)) if m.group(2) else TD._coarse_pitch(d)
                As = (math.pi / 4) * (d - 0.9382 * p) ** 2
                y = (F / (sigma * As)) * 100
                if y >= 65:
                    pass
                elif y >= 50:
                    pass

                col = SUCCESS
                if y >= 65:
                    pass
                elif y >= 50:
                    pass

                flag = ''
                parts.append(f'''占屈服 {y:.0f}%{flag}''')
                self.analysis.setStyleSheet(f'''color: {col}; font-size: 12px; font-weight: bold;''')
            elif c.get('thread_type') == '自攻':
                parts.append('(自攻螺钉无σy模型, 按经验值对照)')
        self.analysis.setText('   |   '.join(parts))
    def _save(self):
        if not self._ctx:
            return None

        try:
            t_val = round(float(self.edit.text().strip().replace(',', '')), 1)
        except ValueError:
            return None

        if t_val <= 0:
            return None
        c = None._ctx
        if not c.get('thread_type'):
            pass
        if not c.get('spec'):
            pass
        if not c.get('grade_material'):
            pass
        if not c.get('scenario'):
            pass
        preset = dict(thread_type = '粗牙', spec = '', grade_material = ''.lstrip('★'), t_rec = t_val, scenario = '')
        dlg = RecordDialog(self.window(), preset = preset)
    # WARNING: Decompyle incomplete
    __classcell__ = None
class RecordDialog:
    '''新增/编辑扭矩记录。edit_row 为 dict 时是编辑模式。'''

    def __init__(self, parent, edit_row, preset):
        super().__init__(parent)
        self.setWindowTitle('编辑个人记录' if edit_row else '新增个人记录')
        self.setMinimumWidth(420)
        self.setStyleSheet(f'''QDialog {{ background: {BG}; color: {FG}; }} QLabel {{ color: {FG}; }}''')
        self.edit_row = edit_row
        form = QFormLayout(self)
        form.setSpacing(8)
        self.thread_combo = QComboBox()
        self.thread_combo.addItems(list(PS.THREAD_TYPES))
        self.spec_edit = QLineEdit()
        self.spec_edit.setPlaceholderText('M12 / M12×1.5 / ST4.2')
        self.grade_edit = QLineEdit()
        self.grade_edit.setPlaceholderText('8.8 / 10.9 / 304不锈钢 …')
        self.grade_hint = QComboBox()
        self.grade_hint.addItem('▼ 快选: 标准等级/自定义材料')
        (lambda .0: [ g for g in .0 ])(TD.GRADES['hex']())
        for m in PS.list_materials():
            self.grade_hint.addItem('★' + m['name'])
            self.source_combo = QComboBox()
            self.source_combo.addItems(list(PS.SOURCES))
            self.rec_spin = QDoubleSpinBox()
            self.rec_spin.setRange(0.1, 99999)
            self.rec_spin.setDecimals(1)
            self.min_spin = QDoubleSpinBox()
            self.min_spin.setRange(0, 99999)
            self.min_spin.setDecimals(1)
            self.max_spin = QDoubleSpinBox()
            self.max_spin.setRange(0, 99999)
            self.max_spin.setDecimals(1)
            for sp in (self.rec_spin, self.min_spin, self.max_spin):
                sp.setSuffix(' N·m')
                self.auto_fill = QPushButton('按智能区间比 0.85/1.15 自动补')
                self.auto_fill.setStyleSheet(_BTN)
                self.scenario_combo = QComboBox()
                self.scenario_combo.addItem('')
                self.scenario_combo.addItems(list(TD.SCENARIOS.keys()))
                self.note_edit = QLineEdit()
                for label, w in (('螺纹类型', self.thread_combo), ('规格', self.spec_edit), ('等级或材质', self.grade_hint), ('等级或材质(手填)', self.grade_edit), ('来源', self.source_combo), ('推荐力矩', self.rec_spin), ('最小力矩', self.min_spin), ('最大力矩', self.max_spin), ('', self.auto_fill), ('适用场景(可空)', self.scenario_combo), ('备注', self.note_edit)):
                    if label:
                        form.addRow(label, w)
                        continue
                    form.addRow(w)
                    self.grade_hint.currentIndexChanged.connect(self._grade_quick)
                    self.auto_fill.clicked.connect(self._auto_range)
                    None((lambda t = None: self.thread_combo.setToolTip('自攻规格形如 ST4.2; 细牙须带螺距')))
                    if edit_row:
                        r = edit_row
                        self.thread_combo.setCurrentText(r['thread_type'])
                        self.spec_edit.setText(r['spec'])
                        self.grade_edit.setText(r['grade_material'])
                        self.source_combo.setCurrentText(r['source'])
                        self.rec_spin.setValue(r['t_rec'])
                        if not r['t_min']:
                            pass
                        self.min_spin.setValue(0)
                        if not r['t_max']:
                            pass
                        self.max_spin.setValue(0)
                        if not r.get('scenario'):
                            pass
                        self.scenario_combo.setCurrentText('')
                        if not r.get('note'):
                            pass
                        self.note_edit.setText('')
                    elif preset:
                        p = preset
                        if not p.get('thread_type'):
                            pass
                        self.thread_combo.setCurrentText('粗牙')
                        if not p.get('spec'):
                            pass
                        self.spec_edit.setText('')
                        if not p.get('grade_material'):
                            pass
                        self.grade_edit.setText('')
                        if not p.get('t_rec'):
                            pass
                        self.rec_spin.setValue(10)
                        if not p.get('t_min'):
                            if not p.get('t_rec'):
                                pass
                        self.min_spin.setValue(round(10 * 0.85, 1))
                        if not p.get('t_max'):
                            if not p.get('t_rec'):
                                pass
                        self.max_spin.setValue(round(10 * 1.15, 1))
                        if not p.get('scenario'):
                            pass
                        self.scenario_combo.setCurrentText('')
        bb = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        bb.accepted.connect(self._accept)
        bb.rejected.connect(self.reject)
        form.addRow(bb)
    def _grade_quick(self, idx):
        if idx <= 0:
            return None
        txt = None.grade_hint.itemText(idx).lstrip('★')
        self.grade_edit.setText(txt)
    def _auto_range(self):
        self.min_spin.setValue(round(self.rec_spin.value() * 0.85, 1))
        self.max_spin.setValue(round(self.rec_spin.value() * 1.15, 1))
    def _accept(self):
        spec = self.spec_edit.text().strip().upper()
        if not spec:
            QMessageBox.warning(self, '缺规格', '请填写规格')
            return None
        gm = None.grade_edit.text().strip()
        if not gm:
            QMessageBox.warning(self, '缺等级', '请填写等级或材质')
            return None
        if (None.min_spin.value() >= self.rec_spin.value() or self.max_spin.value() > 0) and self.max_spin.value() <= self.rec_spin.value():
            QMessageBox.warning(self, '区间错误', '应满足 最小 < 推荐 < 最大')
            return None
        None.accept()
    def result_data(self):
        return dict(thread_type = self.thread_combo.currentText(), spec = self.spec_edit.text().strip().upper(), grade_material = self.grade_edit.text().strip(), source = self.source_combo.currentText(), t_rec = round(self.rec_spin.value(), 1), t_min = round(self.min_spin.value(), 1) if self.min_spin.value() > 0 else None, t_max = round(self.max_spin.value(), 1) if self.max_spin.value() > 0 else None, scenario = self.scenario_combo.currentText(), note = self.note_edit.text().strip())
    __classcell__ = None
class MaterialDialog:
    '''新增/编辑自定义材料。edit_row 为 dict 时是编辑模式。'''

    def __init__(self, parent, edit_row):
        super().__init__(parent)
        self.setWindowTitle('编辑自定义材料' if edit_row else '新增自定义材料')
        self.setMinimumWidth(380)
        self.setStyleSheet(f'''QDialog {{ background: {BG}; color: {FG}; }} QLabel {{ color: {FG}; }}''')
        self.edit_row = edit_row
        form = QFormLayout(self)
        form.setSpacing(8)
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText('如 304不锈钢 / 10B21')
        self.sy_spin = QDoubleSpinBox()
        self.sy_spin.setRange(50, 3000)
        self.sy_spin.setDecimals(0)
        self.sy_spin.setSuffix(' MPa')
        self.sb_spin = QDoubleSpinBox()
        self.sb_spin.setRange(0, 5000)
        self.sb_spin.setDecimals(0)
        self.sb_spin.setSuffix(' MPa')
        self.sb_spin.setSpecialValueText('未填')
        self.note_edit = QLineEdit()
        form.addRow('材料名称', self.name_edit)
        form.addRow('屈服强度 σy', self.sy_spin)
        form.addRow('抗拉强度 σb', self.sb_spin)
        form.addRow('备注', self.note_edit)
        hint = QLabel('提示: 添加后出现在各页签「等级」下拉框(★开头), 力矩按 T=K·F·d 实时计算')
        hint.setWordWrap(True)
        hint.setStyleSheet(f'''color: {TEXT_G}; font-size: 11px;''')
        form.addRow(hint)
        if edit_row:
            self.name_edit.setText(edit_row['name'])
            self.sy_spin.setValue(edit_row['sigma_y'])
            if edit_row['sigma_b']:
                self.sb_spin.setValue(edit_row['sigma_b'])
            if not edit_row.get('note'):
                pass
            self.note_edit.setText('')
        bb = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        bb.accepted.connect(self._accept)
        bb.rejected.connect(self.reject)
        form.addRow(bb)
    def _accept(self):
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, '缺名称', '请填写材料名称')
            return None
        None.accept()
    def result_data(self):
        return dict(name = self.name_edit.text().strip(), sigma_y = self.sy_spin.value(), sigma_b = self.sb_spin.value() if self.sb_spin.value() > 0 else None, note = self.note_edit.text().strip())
    __classcell__ = None
class ImportDialog:

    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle('Excel 导入个人扭矩记录')
        self.setMinimumSize(560, 460)
        self.setStyleSheet(f'''QDialog {{ background: {BG}; color: {FG}; }} QLabel {{ color: {FG}; }}''')
        self.stack = QStackedWidget(self)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(14, 14, 14, 14)
        lay.addWidget(self.stack)
        p1 = QWidget()
        v1 = QVBoxLayout(p1)
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText('选择 .xlsx 文件…')
        pick = QPushButton('浏览…')
        pick.setStyleSheet(_BTN)
        pick.clicked.connect(self._pick)
        row = QHBoxLayout()
        row.addWidget(self.path_edit)
        row.addWidget(pick)
        v1.addLayout(row)
        self.rb_append = QRadioButton('增量追加 — 现有记录保留, 新记录插入')
        self.rb_rebuild = QRadioButton('覆盖重建 — 清空个人记录后全部重灌 (自动备份最近 3 份)')
        self.rb_append.setChecked(True)
        for rb in (self.rb_append, self.rb_rebuild):
            rb.setStyleSheet(f'''color: {FG}; font-size: 12px;''')
            v1.addWidget(rb)
            v1.addStretch()
            tip = QLabel('没有模板? 关闭后先到个人库页签点「生成模板」。')
            tip.setStyleSheet(f'''color: {TEXT_G}; font-size: 11px;''')
            v1.addWidget(tip)
            bb1 = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            bb1.accepted.connect(self._load_file)
            bb1.rejected.connect(self.reject)
            v1.addWidget(bb1)
            p2 = QWidget()
            v2 = QVBoxLayout(p2)
            self.summary_lbl = QLabel('')
            self.summary_lbl.setStyleSheet(f'''color: {FG}; font-size: 13px; font-weight: bold;''')
            v2.addWidget(self.summary_lbl)
            self.table = QTableWidget(0, len(PX.HEADERS))
            self.table.setHorizontalHeaderLabels(PX.HEADERS)
            self.table.setStyleSheet(_TABLE)
            self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
            self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
            v2.addWidget(self.table)
            self.err_box = QPlainTextEdit()
            self.err_box.setReadOnly(True)
            self.err_box.setMaximumHeight(90)
            self.err_box.setStyleSheet(f'''QPlainTextEdit {{ background: {CARD}; color: {DANGER}; border: 1px solid {BORDER}; font-size: 11px; }}''')
            v2.addWidget(self.err_box)
            bb2 = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            bb2.accepted.connect(self._do_import)
            bb2.rejected.connect(self.reject)
            v2.addWidget(bb2)
            self.stack.addWidget(p1)
            self.stack.addWidget(p2)
            self._ok_rows = []
            self.imported = 0
            return None
    def _pick(self):
        (path, _) = QFileDialog.getOpenFileName(self, '选择 Excel', '', 'Excel (*.xlsx);;所有文件 (*)')
        if path:
            self.path_edit.setText(path)
            return None
    def _load_file(self):
        path = self.path_edit.text().strip()
        if not path:
            QMessageBox.warning(self, '缺文件', '请先选择 Excel 文件')
            return None

        try:
            (raw_rows, errs) = PX.parse_import(path)
        except Exception:
            e = None
            QMessageBox.critical(self, '读取失败', str(e))
            e = None
            del e
            return None
            e = None
            del e

        (ok_rows, verrs) = PX.validate_all(raw_rows)
        errs += verrs
        self._ok_rows = ok_rows
        mode = 'rebuild' if self.rb_rebuild.isChecked() else 'append'
        self._mode = mode
        self.summary_lbl.setText(f'''共 {len(raw_rows)} 行: 可导入 {len(ok_rows)} 行 ({'覆盖重建' if mode == 'rebuild' else '增量追加'}), 错误 {len(errs)} 行''')
        self.table.setRowCount(0)
        for rec in ok_rows:
            r = self.table.rowCount()
            self.table.insertRow(r)
            vals = [
                rec['thread_type'],
                rec['spec'],
                rec['grade_material'],
                rec['source'],
                _fmt(rec['t_min']),
                f'''{rec['t_rec']:.1f}''',
                _fmt(rec['t_max']),
                rec['scenario'],
                rec['note']]
            for c, v in enumerate(vals):
                self.table.setItem(r, c, QTableWidgetItem(str(v)))
                if not (lambda .0: [ f'''第{ln}行: {msg}''' for ln, msg in .0 ])(errs()):
                    pass
        '\n'.join('校验全部通过')
        self.stack.setCurrentIndex(1)
    def _do_import(self):
        if not self._ok_rows:
            QMessageBox.warning(self, '无可导入行', '没有通过校验的行, 请检查错误列表')
            return None
        None.backup_db('import')
        (ok, errs) = PS.import_records(self._ok_rows, self._mode)
        self.imported = ok
        if errs:
            QMessageBox.warning(self, '部分失败', f'''成功 {ok} 行, 失败 {len(errs)} 行''')
        else:
            QMessageBox.information(self, '导入完成', f'''成功导入 {ok} 条记录 (已自动备份)''')
        self.accept()
    __classcell__ = None
class PersonalTab:
    '''个人库管理: 自定义材料 + 扭矩记录。refresh_cb 在数据变化后回调(供对比卡联动)。'''
    REC_COLS = [
        '螺纹',
        '规格',
        '等级/材质',
        '来源',
        '最小',
        '推荐',
        '最大',
        'vs智能',
        '场景',
        '备注',
        '日期',
        'ID']

    def __init__(self, parent_window, refresh_cb):
        super().__init__()
        self.parent_window = parent_window
        self.refresh_cb = refresh_cb
        self.setStyleSheet(f'''QWidget {{ background: {BG}; }}''')
        self.layout = QHBoxLayout(self)
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(14, 14, 14, 14)
        self._left_host = QWidget()
        self._left_host.setMaximumWidth(415)
        self._left_col = QVBoxLayout(self._left_host)
        self._left_col.setContentsMargins(0, 0, 0, 0)
        self._left_col.setSpacing(10)
        memo_card = QFrame()
        memo_card.setObjectName('card')
        memo_card.setStyleSheet(CARD_STYLE)
        mv0 = QVBoxLayout(memo_card)
        mv0.setContentsMargins(14, 10, 14, 10)
        mv0.setSpacing(6)
        head0 = QHBoxLayout()
        t0 = QLabel('[备忘录] 手动记录工作台')
        t0.setStyleSheet(f'''color: {ACCENT}; font-size: 14px; font-weight: bold;''')
        head0.addWidget(t0)
        head0.addStretch()
        self.ref_refresh_btn = QPushButton('↻ 刷新引用')
        self.ref_refresh_btn.setStyleSheet(_BTN)
        self.ref_refresh_btn.clicked.connect(self._refresh_ref)
        self.ref_bring_btn = QPushButton('带入为新记录底稿')
        self.ref_bring_btn.setStyleSheet(_BTN)
        self.ref_bring_btn.clicked.connect(self._bring_in)
        head0.addWidget(self.ref_refresh_btn)
        head0.addWidget(self.ref_bring_btn)
        mv0.addLayout(head0)
        hint0 = QLabel('手动记录与智能计算完全分开 — 这里的数据只属于你。快选「类型/规格/等级」就地出智能参考值, 或点「刷新引用」带入左侧智能页签当前查询; 两者互不干扰, 取最近一次操作')
        hint0.setWordWrap(True)
        hint0.setStyleSheet(f'''color: {TEXT_G}; font-size: 11px;''')
        mv0.addWidget(hint0)
        qrow1 = QHBoxLayout()
        q0 = QLabel('快选:')
        q0.setStyleSheet(f'''color: {TEXT_G}; font-size: 12px;''')
        self.qs_thread = QComboBox()
        self.qs_thread.setStyleSheet(COMBO_STYLE)
        self.qs_thread.addItems([
            '粗牙',
            '细牙',
            '自攻'])
        self.qs_spec = QComboBox()
        self.qs_spec.setStyleSheet(COMBO_STYLE)
        self.qs_spec.setEditable(True)
        qrow1.addWidget(q0)
        qrow1.addWidget(self.qs_thread)
        qrow1.addWidget(QLabel('规格'))
        qrow1.addWidget(self.qs_spec, 1)
        mv0.addLayout(qrow1)
        qrow2 = QHBoxLayout()
        self.qs_grade = QComboBox()
        self.qs_grade.setStyleSheet(COMBO_STYLE)
        self.qs_grade.setEditable(True)
        self.qs_base_lbl = QLabel('')
        self.qs_base_lbl.setStyleSheet(f'''color: {ACCENT_H}; font-size: 12px; font-weight: bold;''')
        self.qs_base_lbl.setWordWrap(True)
        qrow2.addWidget(QLabel('等级/材质'))
        qrow2.addWidget(self.qs_grade, 1)
        qrow2.addWidget(self.qs_base_lbl, 1)
        mv0.addLayout(qrow2)
        self.qs_thread.currentIndexChanged.connect(self._qs_thread_changed)
        self.qs_spec.currentTextChanged.connect(self._qs_changed)
        self.qs_grade.currentTextChanged.connect(self._qs_changed)
        self._qs_ready = False
        self._fill_qs_grade()
        self._fill_qs_spec()
        self.ref_lbl = QLabel('智能引用: (切到智能页签选好参数后, 这里显示当前查询)')
        self.ref_lbl.setWordWrap(True)
        self.ref_lbl.setStyleSheet(f'''color: {ACCENT_H}; font-size: 12px; font-weight: bold;''')
        mv0.addWidget(self.ref_lbl)
        self.my_box = CustomTorqueBox(on_saved_cb = self._changed)
        mv0.addWidget(self.my_box)
        self._qs_ready = True
        self._qs_changed()
        self._left_col.addWidget(memo_card)
        mat_card = QFrame()
        mat_card.setObjectName('card')
        mat_card.setStyleSheet(CARD_STYLE)
        mv = QVBoxLayout(mat_card)
        mv.setContentsMargins(14, 10, 14, 10)
        head = QHBoxLayout()
        t1 = QLabel('自定义材料参数')
        t1.setStyleSheet(f'''color: {ACCENT}; font-size: 14px; font-weight: bold;''')
        head.addWidget(t1)
        head.addStretch()
        self.mat_add = QPushButton('＋ 新增材料')
        self.mat_add.setStyleSheet(_BTN)
        self.mat_edit = QPushButton('编辑')
        self.mat_edit.setStyleSheet(_BTN)
        self.mat_del = QPushButton('删除')
        self.mat_del.setStyleSheet(_BTN)
        for b in (self.mat_add, self.mat_edit, self.mat_del):
            head.addWidget(b)
            mv.addLayout(head)
            hint = QLabel('自定义材料会出现在外六角/内六角页签的「等级」下拉(★开头), 力矩按 T=K·F·d 实时计算')
            hint.setStyleSheet(f'''color: {TEXT_G}; font-size: 11px;''')
            mv.addWidget(hint)
            self.mat_table = QTableWidget(0, 4)
            self.mat_table.setHorizontalHeaderLabels([
                '材料名称',
                'σy (MPa)',
                'σb (MPa)',
                '备注'])
            self.mat_table.setStyleSheet(_TABLE)
            self.mat_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.mat_table.setSelectionBehavior(QAbstractItemView.SelectRows)
            self.mat_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
            self.mat_table.setMaximumHeight(150)
            None((lambda row = None, col = None: self._mat_edit()))
            mv.addWidget(self.mat_table)
            self._left_col.addWidget(mat_card)
            self._left_col.addStretch()
            self.layout.addWidget(self._left_host)
            self.mat_add.clicked.connect(self._mat_add)
            self.mat_edit.clicked.connect(self._mat_edit)
            self.mat_del.clicked.connect(self._mat_del)
            rec_card = QFrame()
            rec_card.setObjectName('card')
            rec_card.setStyleSheet(CARD_STYLE)
            rv = QVBoxLayout(rec_card)
            rv.setContentsMargins(14, 10, 14, 10)
            head2 = QHBoxLayout()
            t2 = QLabel('个人扭矩记录')
            t2.setStyleSheet(f'''color: {ACCENT}; font-size: 14px; font-weight: bold;''')
            head2.addWidget(t2)
            head2.addStretch()
            self.search_edit = QLineEdit()
            self.search_edit.setPlaceholderText('搜索规格/等级/备注…')
            self.search_edit.setStyleSheet(f'''QLineEdit {{ background: {CARD_H}; color: {FG}; border: 1px solid {BORDER}; border-radius: 6px; padding: 5px 8px; }}''')
            self.search_edit.setMinimumWidth(120)
            self.search_edit.setMaximumWidth(220)
            self.search_edit.textChanged.connect(self.refresh_records)
            self.type_filter = QComboBox()
            self.type_filter.setStyleSheet(COMBO_STYLE)
            self.type_filter.addItem('全部类型')
            self.type_filter.addItems(list(PS.THREAD_TYPES))
            self.type_filter.setMaximumWidth(130)
            self.src_filter = QComboBox()
            self.src_filter.setStyleSheet(COMBO_STYLE)
            self.src_filter.addItem('全部来源')
            self.src_filter.addItems(list(PS.SOURCES))
            self.src_filter.setMaximumWidth(130)
            self.type_filter.currentIndexChanged.connect(self.refresh_records)
            self.src_filter.currentIndexChanged.connect(self.refresh_records)
            head2.addWidget(self.search_edit)
            head2.addWidget(self.type_filter)
            head2.addWidget(self.src_filter)
            rv.addLayout(head2)
            self.stats_lbl = QLabel('')
            self.stats_lbl.setStyleSheet(f'''color: {TEXT_G}; font-size: 11px;''')
            rv.addWidget(self.stats_lbl)
            self.rec_table = QTableWidget(0, len(self.REC_COLS))
            self.rec_table.setHorizontalHeaderLabels(self.REC_COLS)
            self.rec_table.setStyleSheet(_TABLE)
            self.rec_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
            self.rec_table.setSelectionBehavior(QAbstractItemView.SelectRows)
            self.rec_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
            self.rec_table.setColumnHidden(len(self.REC_COLS) - 1, True)
            self.rec_table.setMinimumHeight(200)
            self.rec_table.setSortingEnabled(True)
            None((lambda row = None, col = None: self._rec_edit()))
            self.rec_table.setContextMenuPolicy(Qt.CustomContextMenu)
            self.rec_table.customContextMenuRequested.connect(self._rec_menu)
            rv.addWidget(self.rec_table)
            btns = QHBoxLayout()
            for text, cb in (('＋ 新增记录', self._rec_add), ('编辑', self._rec_edit), ('⧉ 克隆', self._rec_clone), ('删除', self._rec_del), ('⬆ Excel 导入', self._rec_import), ('⬇ 导出 Excel', self._rec_export), ('生成模板', self._rec_template)):
                b = QPushButton(text)
                b.setStyleSheet(_BTN)
                b.clicked.connect(cb)
                btns.addWidget(b)
                btns.addStretch()
                self.count_lbl = QLabel('')
                self.count_lbl.setStyleSheet(f'''color: {TEXT_G}; font-size: 11px;''')
                btns.addWidget(self.count_lbl)
                rv.addLayout(btns)
                self.layout.addWidget(rec_card, 1)
                self.refresh_materials()
                self.refresh_records()
                self._refresh_ref()
                return None
    def _refresh_ref(self):
        '''刷新智能引用行 + 手填反算上下文 (进入个人库页签或手动刷新时)。'''
        ctx = None

        try:
            w = self.parent_window
            ctx = w.current_smart_ctx() if w and hasattr(w, 'current_smart_ctx') else None
        except Exception:
            ctx = None

        self._ref_ctx = ctx
    # WARNING: Decompyle incomplete
    def _bring_in(self):
        '''把当前智能引用一键带入为新记录底稿 (推荐值预填, 用户改成自己的实测值)。'''
        ctx = getattr(self, '_ref_ctx', None)
        if not ctx:
            QMessageBox.information(self, '暂无引用', '请先到智能页签(外六角/内六角/自攻)选好参数, 再回来刷新引用')
            return None
        if not ctx['grade_material']:
            pass
        if not ctx.get('scenario'):
            pass
        preset = None(thread_type = ctx['thread_type'], spec = ctx['spec'], grade_material = ''.lstrip('★'), t_rec = ctx['smart_rec'], t_min = round(ctx['smart_rec'] * 0.85, 1), t_max = round(ctx['smart_rec'] * 1.15, 1), scenario = '')
        dlg = RecordDialog(self, preset = preset)
    # WARNING: Decompyle incomplete
    def _fill_qs_grade(self):
        tt = self.qs_thread.currentText()
        self.qs_grade.blockSignals(True)
        self.qs_grade.clear()
        if tt == '自攻':
            mats = set()
            for vals in TD.SELF_TAPPING.values():
                mats.update(vals.keys())
                self.qs_grade.addItems(sorted(mats))
        self.qs_grade.addItems(list(TD.GRADES['hex']))
        (lambda .0: [ '★' + m['name'] for m in .0 ])(PS.list_materials()())
        self.qs_grade.blockSignals(False)
    def _fill_qs_spec(self):
        tt = self.qs_thread.currentText()
        self.qs_spec.blockSignals(True)
        self.qs_spec.clear()
        if tt == '自攻':
            self.qs_spec.addItems(TD.SIZES['self_tap'])
        elif tt == '细牙':
            self.qs_spec.addItems(TD.FINE_THREAD_HEX)
        else:
            self.qs_spec.addItems(TD.SIZES['hex'])
        self.qs_spec.blockSignals(False)
        self._qs_changed()
    def _qs_thread_changed(self):
        self._fill_qs_grade()
        self._fill_qs_spec()
    def _qs_changed(self):
        '''快选任一项变化 → 就地算底账参考, 同时作为手填反算/带入底稿的上下文。'''
        if not getattr(self, '_qs_ready', False):
            return None
        tt = None.qs_thread.currentText()
        spec = self.qs_spec.currentText().strip().upper()
        gm = self.qs_grade.currentText().strip()
        if not spec or gm:
            self.qs_base_lbl.setText('')
            return None
        (base, why) = None.smart_baseline(tt, spec, gm)
        if not base:
            self.qs_base_lbl.setText(f'''→ 无底账参考 ({why})''')
            return None
        None.qs_base_lbl.setText(f'''→ 智能底账参考 {base:.1f} N·m''')
        g = gm.lstrip('★')
        mat = PS.get_material(g)
        if mat:
            sigma_y = mat['sigma_y']
        elif tt != '自攻':
            sigma_y = TD.get_yield_strength(g)
        else:
            sigma_y = None
        self._ref_ctx = dict(page = '快选', thread_type = tt, spec = spec, grade_material = g, sigma_y = sigma_y, size_str = spec, k_val = 0.2, smart_rec = base, scenario = '')
        self.ref_lbl.setText(f'''快选参考: {tt} {spec} · {gm} · 底账 {base:.1f} N·m''')
    # WARNING: Decompyle incomplete
    def refresh_materials(self):
        mats = PS.list_materials()
        self.mat_table.setRowCount(0)
        for m in mats:
            r = self.mat_table.rowCount()
            self.mat_table.insertRow(r)
            self.mat_table.setItem(r, 0, QTableWidgetItem(m['name']))
            self.mat_table.setItem(r, 1, QTableWidgetItem(f'''{m['sigma_y']:.0f}'''))
            self.mat_table.setItem(r, 2, QTableWidgetItem(_fmt(m['sigma_b'])))
            if not m.get('note'):
                pass
            self.mat_table.setItem(r, 3, QTableWidgetItem(''))
            self.mat_table.item(r, 0).setData(Qt.UserRole, m['id'])
            return None
    def _sel_mat_id(self):
        r = self.mat_table.currentRow()
        if r < 0:
            return None
        it = None.mat_table.item(r, 0)
        return it.data(Qt.UserRole) if it else None
    def _mat_add(self):
        dlg = MaterialDialog(self)
        if dlg.exec():
            d = dlg.result_data()

            try:
                PS.add_material(d['name'], d['sigma_y'], d['sigma_b'], d['note'])
            except Exception:
                e = None
                QMessageBox.warning(self, '新增失败', str(e))
                e = None
                del e
                return None
                e = None
                del e

            self._changed()
            return None
    def _mat_edit(self):
        pass


    def _mat_del(self):
        mid = self._sel_mat_id()
        if not mid is not None:
            QMessageBox.information(self, '未选择', '请先在表格中选择一条材料')
            return None
        if None.question(self, '确认删除', '删除后使用该材料的记录仍保留(等级列不变)。确认?') != QMessageBox.Yes:
            return None
        None.delete_material(mid)
        self._changed()
    (COL_MIN, COL_REC, COL_MAX, COL_DIFF, COL_ID) = (4, 5, 6, 7, 11)

    def refresh_records(self):
        rows = PS.list_records(self.search_edit.text().strip(), '' if self.type_filter.currentIndex() <= 0 else self.type_filter.currentText(), '' if self.src_filter.currentIndex() <= 0 else self.src_filter.currentText())
        self.rec_table.setSortingEnabled(False)
        self.rec_table.setRowCount(0)
        for rec in rows:
            r = self.rec_table.rowCount()
            self.rec_table.insertRow(r)
            if not rec.get('scenario'):
                pass
            if not rec.get('note'):
                pass
            if not rec.get('created_at'):
                pass
            vals = [
                rec['thread_type'],
                rec['spec'],
                rec['grade_material'],
                rec['source'],
                _fmt(rec['t_min']),
                f'''{rec['t_rec']:.1f}''',
                _fmt(rec['t_max']),
                None,
                '',
                '',
                ''[:10],
                rec['id']]
            for c, v in enumerate(vals):
                if c == self.COL_DIFF:
                    continue
                if c in (self.COL_MIN, self.COL_REC, self.COL_MAX) and v not in (None, '', '—'):
                    self.rec_table.setItem(r, c, NumItem(str(v), float(v)))
                    continue
                self.rec_table.setItem(r, c, QTableWidgetItem('' if not v is not None else str(v)))
                (base, _why) = PS.smart_baseline(rec['thread_type'], rec['spec'], rec['grade_material'])
                d = self._diff_item(base, rec['t_rec'])
                self.rec_table.setItem(r, self.COL_DIFF, d)
                self.rec_table.setSortingEnabled(True)
                self.count_lbl.setText(f'''共 {len(rows)} 条记录''')
                self._update_stats()
                return None
    _diff_item = (lambda base, t_rec: pass)()

    def _update_stats(self):
        s = PS.stats_summary()
        self.stats_lbl.setText(f'''📊 记录 {s['n_records']} 条 · 覆盖规格 {s['n_specs']} 种 · 自定义材料 {s['n_materials']} 种''' + f''' · 最近录入 {s['latest']}''' if s['latest'] else '')
    def _sel_rec_id(self):
        r = self.rec_table.currentRow()
        if r < 0:
            return None
        it = None.rec_table.item(r, len(self.REC_COLS) - 1)
        return int(it.text()) if it else None
    def _rec_menu(self, pos):
        '''记录表右键菜单: 编辑 / 克隆 / 删除 (V2.5)。'''
        menu = QMenu(self)
        menu.setStyleSheet(f'''QMenu {{ background: {CARD}; color: {FG}; border: 1px solid {BORDER}; }}QMenu::item:selected {{ background: {CARD_H}; color: {ACCENT}; }}''')
        menu.addAction('✎ 编辑', self._rec_edit)
        menu.addAction('⧉ 克隆为新记录', self._rec_clone)
        menu.addAction('🗑 删除', self._rec_del)
        menu.exec(self.rec_table.viewport().mapToGlobal(pos))
    def _rec_clone(self):
        '''克隆选中记录: 带出全部字段作底稿 (同系列规格只改规格和数值)。'''
        rid = self._sel_rec_id()
        if not rid is not None:
            QMessageBox.information(self, '未选择', '请先在表格中选择一条要克隆的记录')
            return None
        row = None.get_record(rid)
        if not row:
            return None
        if not row['t_min']:
            pass
        if not row['t_max']:
            pass
        if not row.get('scenario'):
            pass
        if not row.get('note'):
            pass
        preset = None(thread_type = row['thread_type'], spec = row['spec'], grade_material = row['grade_material'], source = row['source'], t_rec = row['t_rec'], t_min = row['t_rec'] * 0.85, t_max = row['t_rec'] * 1.15, scenario = '', note = '')
        dlg = RecordDialog(self, preset = preset)
        dlg.setWindowTitle('克隆为新记录')
    # WARNING: Decompyle incomplete
    def _rec_add(self):
        dlg = RecordDialog(self)
    # WARNING: Decompyle incomplete
    def _rec_edit(self):
        rid = self._sel_rec_id()
        if not rid is not None:
            QMessageBox.information(self, '未选择', '请先在表格中选择一条记录')
            return None
        row = None.get_record(rid)
        if not row:
            return None
        dlg = None(self, edit_row = row)
    # WARNING: Decompyle incomplete
    def _rec_del(self):
        rid = self._sel_rec_id()
        if not rid is not None:
            QMessageBox.information(self, '未选择', '请先在表格中选择一条记录')
            return None
        if None.question(self, '确认删除', '删除该条个人记录?') != QMessageBox.Yes:
            return None
        None.delete_record(rid)
        self._changed()
    def _rec_import(self):
        if not PX.HAS_OPENPYXL:
            QMessageBox.warning(self, '缺组件', '当前环境缺少 openpyxl, 无法导入 Excel')
            return None
        dlg = None(self)
        if dlg.exec() or dlg.imported:
            self._changed()
            return None
        return None
    def _rec_export(self):
        if not PX.HAS_OPENPYXL:
            QMessageBox.warning(self, '缺组件', '当前环境缺少 openpyxl, 无法导出')
            return None
        (path, _) = None.getSaveFileName(self, '导出 Excel', '个人扭矩记录.xlsx', 'Excel (*.xlsx)')
        if not path:
            return None
        n = None.export_records(path)
        QMessageBox.information(self, '导出完成', f'''已导出 {n} 条记录''')
    def _rec_template(self):
        (path, _) = QFileDialog.getSaveFileName(self, '生成导入模板', '个人扭矩记录模板.xlsx', 'Excel (*.xlsx)')
        if not path:
            return None
        None.make_template(path)
        QMessageBox.information(self, '模板已生成', f'''已生成: {os.path.basename(path)}\n按模板填好后用「Excel 导入」''')
    def _changed(self):
        self.refresh_materials()
        self.refresh_records()
        if self.refresh_cb:
            self.refresh_cb()
            return None
    __classcell__ = staticmethod
    return staticmethod

