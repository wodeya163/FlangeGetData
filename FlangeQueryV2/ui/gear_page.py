# -*- coding: utf-8 -*-
"""齿轮参数工具：几何、配对、模数、M 值、齿厚、强度与精度。"""

import os

from PyQt5.QtWidgets import (QCheckBox, QComboBox, QDoubleSpinBox,
                             QFileDialog, QFormLayout, QFrame, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QScrollArea,
                             QSpinBox,
                             QStackedWidget, QTableWidget, QTableWidgetItem,
                             QTabWidget, QVBoxLayout, QWidget)

from core.gear import (MODULE_FIRST, MODULE_SECOND, bevel_gear,
                       helical_gear, nearest_module, pair_center_distance,
                       spur_gear)
from core.gear_m_value import (calc_m_value_simple,
                               calc_roller_diameter,
                               solve_x_from_m_value)
from core.gear_tooth_thickness import calc_k_from_z, convert_tooth_thickness
from core.gear_strength import calc_zhang_xuemeng, get_material_list
from core.gear_stp import find_python, generate as generate_step

CARD_QSS = ('QFrame#gcard{background:#fff;border:1px solid #c9d2dc;'
            'border-radius:6px;}')
TITLE_QSS = 'font-size:16px;font-weight:bold;color:#1f4e79;'
LABEL_QSS = 'font-size:13px;color:#333;'
HINT_QSS = 'font-size:12px;color:#666;'


def _card():
    frame = QFrame()
    frame.setObjectName('gcard')
    frame.setStyleSheet(CARD_QSS)
    return frame


def _title(text):
    label = QLabel(text)
    label.setStyleSheet(TITLE_QSS)
    return label


def _spin(value, low, high, decimals=3, suffix='', step=1.0):
    box = QDoubleSpinBox()
    box.setRange(low, high)
    box.setDecimals(decimals)
    box.setSingleStep(step)
    box.setValue(value)
    box.setSuffix(suffix)
    box.setKeyboardTracking(False)
    box.setMinimumWidth(170)
    return box


def _int_spin(value, low=1, high=1000, suffix=''):
    box = QSpinBox()
    box.setRange(low, high)
    box.setValue(value)
    box.setSuffix(suffix)
    box.setKeyboardTracking(False)
    box.setMinimumWidth(170)
    return box


def _combo(items):
    box = QComboBox()
    box.addItems(items)
    box.setMinimumWidth(170)
    return box


def _form_row(form, label, widget):
    lab = QLabel(label)
    lab.setStyleSheet(LABEL_QSS)
    form.addRow(lab, widget)


def _table(headers, height=190):
    table = QTableWidget(0, len(headers))
    table.setHorizontalHeaderLabels(headers)
    table.verticalHeader().setVisible(False)
    table.setEditTriggers(QTableWidget.NoEditTriggers)
    table.setSelectionMode(QTableWidget.NoSelection)
    table.horizontalHeader().setStretchLastSection(True)
    table.setMinimumHeight(height)
    table.setMaximumHeight(height + 40)
    table.setStyleSheet('QTableWidget{background:#fff;border:1px solid #d6dee7;'
                        'font-size:12px;} QHeaderView::section{background:#eef3f8;'
                        'border:none;padding:4px;font-weight:bold;}')
    return table


def _set_rows(table, rows):
    table.setRowCount(len(rows))
    for r, row in enumerate(rows):
        for c, value in enumerate(row):
            table.setItem(r, c, QTableWidgetItem(str(value)))
    table.resizeColumnsToContents()


def _scroll(widget):
    area = QScrollArea()
    area.setWidgetResizable(True)
    area.setFrameShape(QFrame.NoFrame)
    area.setWidget(widget)
    return area


class BasicGearPage(QWidget):
    """直齿圆柱、斜齿圆柱、直齿锥齿轮几何。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 14, 16, 14)
        root.setSpacing(10)
        head = QHBoxLayout()
        head.addWidget(_title('基本齿轮参数'))
        head.addStretch(1)
        head.addWidget(QLabel('类型'))
        self.kind = _combo(['直齿圆柱齿轮', '斜齿圆柱齿轮', '直齿锥齿轮'])
        self.kind.currentIndexChanged.connect(self._switch)
        head.addWidget(self.kind)
        root.addLayout(head)

        self.stack = QStackedWidget()
        self.inputs = {}
        self._build_spur()
        self._build_helical()
        self._build_bevel()
        self.stack.setMaximumHeight(340)
        root.addWidget(self.stack)

        row = QHBoxLayout()
        btn = QPushButton('计算')
        btn.setProperty('class', 'b-print')
        btn.setMinimumHeight(34)
        btn.clicked.connect(self.calculate)
        row.addWidget(btn)
        self.hint = QLabel('')
        self.hint.setStyleSheet(HINT_QSS)
        row.addWidget(self.hint, 1)
        root.addLayout(row)

        self.result = _table(['参数', '数值'], 280)
        root.addWidget(self.result)
        self._switch()

    def _page(self):
        page = QWidget()
        form = QFormLayout(page)
        form.setHorizontalSpacing(14)
        form.setVerticalSpacing(8)
        self.stack.addWidget(page)
        return page, form

    def _build_spur(self):
        _, form = self._page()
        self.inputs['spur'] = {}
        for key, label, value in [
                ('m', '模数 m (mm)', 3.0), ('z', '齿数 z', 20),
                ('alpha', '压力角 α (°)', 20.0),
                ('ha', '齿顶高系数', 1.0), ('c', '顶隙系数', 0.25),
                ('x', '变位系数 x', 0.0)]:
            widget = _int_spin(value) if key == 'z' else _spin(
                value, 0.0, 1000.0, 3)
            self.inputs['spur'][key] = widget
            _form_row(form, label, widget)

    def _build_helical(self):
        _, form = self._page()
        self.inputs['helical'] = {}
        for key, label, value in [
                ('mn', '法向模数 mn (mm)', 3.0), ('z', '齿数 z', 20),
                ('beta', '螺旋角 β (°)', 15.0),
                ('alpha', '法向压力角 αn (°)', 20.0),
                ('ha', '齿顶高系数', 1.0), ('c', '顶隙系数', 0.25),
                ('x', '法向变位系数 xn', 0.0)]:
            widget = _int_spin(value) if key == 'z' else _spin(
                value, 0.0, 1000.0, 3)
            self.inputs['helical'][key] = widget
            _form_row(form, label, widget)

    def _build_bevel(self):
        _, form = self._page()
        self.inputs['bevel'] = {}
        for key, label, value in [
                ('z1', '小轮齿数 z1', 20), ('z2', '大轮齿数 z2', 30),
                ('m', '大端模数 m (mm)', 3.0),
                ('b', '齿宽 b (mm)', 16.0),
                ('alpha', '压力角 α (°)', 20.0),
                ('sigma', '轴交角 Σ (°)', 90.0)]:
            widget = (_int_spin(value) if key in ('z1', 'z2')
                      else _spin(value, 0.0, 1000.0, 3))
            self.inputs['bevel'][key] = widget
            _form_row(form, label, widget)

    def _switch(self):
        self.stack.setCurrentIndex(self.kind.currentIndex())
        self.calculate()

    def calculate(self):
        kind = ['spur', 'helical', 'bevel'][self.kind.currentIndex()]
        v = {k: w.value() for k, w in self.inputs[kind].items()}
        try:
            if kind == 'spur':
                r = spur_gear(v['m'], int(v['z']), v['alpha'], v['ha'],
                              v['c'], v['x'])
                rows = [('分度圆 d', '%.3f mm' % r['d']),
                        ('齿顶圆 da', '%.3f mm' % r['da']),
                        ('齿根圆 df', '%.3f mm' % r['df']),
                        ('基圆 db', '%.3f mm' % r['db']),
                        ('齿距 p', '%.3f mm' % r['p']),
                        ('分度圆齿厚 s', '%.3f mm' % r['s']),
                        ('全齿高 h', '%.3f mm' % r['h'])]
                self.hint.setText('最近标准模数：%s mm' % nearest_module(v['m']))
            elif kind == 'helical':
                r = helical_gear(v['mn'], int(v['z']), v['beta'],
                                 v['alpha'], v['ha'], v['c'], v['x'])
                rows = [('分度圆 d', '%.3f mm' % r['d']),
                        ('齿顶圆 da', '%.3f mm' % r['da']),
                        ('齿根圆 df', '%.3f mm' % r['df']),
                        ('端面模数 mt', '%.3f mm' % r['mt']),
                        ('端面压力角 αt', '%.3f °' % r['alpha_t']),
                        ('当量齿数 zv', '%.2f' % r['zv']),
                        ('全齿高 h', '%.3f mm' % r['h'])]
                self.hint.setText('最近标准模数：%s mm' % nearest_module(v['mn']))
            else:
                r = bevel_gear(int(v['z1']), int(v['z2']), v['m'], v['b'],
                               v['alpha'], sigma=v['sigma'])
                rows = [('分度圆锥角 δ1', '%.3f °' % r['delta1']),
                        ('分度圆锥角 δ2', '%.3f °' % r['delta2']),
                        ('外锥距 R', '%.3f mm' % r['R']),
                        ('分度圆 d1', '%.3f mm' % r['d1']),
                        ('分度圆 d2', '%.3f mm' % r['d2']),
                        ('齿顶高 ha', '%.3f mm' % r['ha']),
                        ('齿根高 hf', '%.3f mm' % r['hf'])]
                self.hint.setText('齿宽应不大于 R/3；当前 b/R=%.3f' %
                                  (v['b'] / r['R']))
            _set_rows(self.result, rows)
            return r
        except (ValueError, ZeroDivisionError) as exc:
            _set_rows(self.result, [('错误', str(exc))])
            self.hint.setText('')
            return None


class PairGearPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 14, 16, 14)
        root.setSpacing(10)
        head = QHBoxLayout()
        head.addWidget(_title('配对齿轮中心距'))
        head.addStretch(1)
        head.addWidget(QLabel('类型'))
        self.kind = _combo(['直齿圆柱齿轮', '斜齿圆柱齿轮'])
        head.addWidget(self.kind)
        root.addLayout(head)
        card = _card()
        form = QFormLayout(card)
        form.setContentsMargins(16, 14, 16, 14)
        form.setVerticalSpacing(8)
        self.m = _spin(3.0, 0.01, 1000, 3, ' mm')
        self.z1 = _int_spin(20)
        self.z2 = _int_spin(40)
        self.beta = _spin(0.0, -45, 45, 2, ' °')
        self.x1 = _spin(0.0, -5, 5, 3)
        self.x2 = _spin(0.0, -5, 5, 3)
        for label, widget in [('模数 m', self.m), ('小轮齿数 z1', self.z1),
                              ('大轮齿数 z2', self.z2),
                              ('螺旋角 β', self.beta), ('变位 x1', self.x1),
                              ('变位 x2', self.x2)]:
            _form_row(form, label, widget)
        root.addWidget(card)
        row = QHBoxLayout()
        btn = QPushButton('计算')
        btn.setProperty('class', 'b-print')
        btn.setMinimumHeight(34)
        btn.clicked.connect(self.calculate)
        row.addWidget(btn)
        self.hint = QLabel('')
        self.hint.setStyleSheet(HINT_QSS)
        row.addWidget(self.hint, 1)
        root.addLayout(row)
        self.result = _table(['项目', '数值'], 150)
        root.addWidget(self.result)
        root.addStretch(1)
        self.calculate()

    def calculate(self):
        kind = 'helical' if self.kind.currentIndex() == 1 else 'spur'
        try:
            a, ap, ratio = pair_center_distance(
                kind, self.m.value(), self.z1.value(), self.z2.value(),
                self.beta.value(), self.x1.value(), self.x2.value())
            _set_rows(self.result, [
                ('标准中心距 a', '%.3f mm' % a),
                ('实际中心距 a′', '%.3f mm' % ap),
                ('传动比 i', '%.4f' % ratio)])
            self.hint.setText('i = z2 / z1；斜齿按端面模数计算。')
            return {'a': a, 'a_p': ap, 'ratio': ratio}
        except (ValueError, ZeroDivisionError) as exc:
            _set_rows(self.result, [('错误', str(exc))])
            return None


class ModulePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 14, 16, 14)
        root.setSpacing(10)
        root.addWidget(_title('标准模数（GB/T 1357-2008）'))
        filt = QHBoxLayout()
        filt.addWidget(QLabel('筛选'))
        self.filter = QLineEdit()
        self.filter.setPlaceholderText('输入模数，如 3 或 2.5')
        self.filter.textChanged.connect(self._filter)
        filt.addWidget(self.filter, 1)
        root.addLayout(filt)
        self.table = QTableWidget(max(len(MODULE_FIRST), len(MODULE_SECOND)), 2)
        self.table.setHorizontalHeaderLabels(['第一系列（优先）', '第二系列'])
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setStyleSheet('QTableWidget{background:#fff;'
                                 'border:1px solid #d6dee7;font-size:13px;}'
                                 'QHeaderView::section{background:#eef3f8;'
                                 'padding:5px;font-weight:bold;}')
        for i in range(self.table.rowCount()):
            if i < len(MODULE_FIRST):
                self.table.setItem(i, 0,
                                   QTableWidgetItem(str(MODULE_FIRST[i])))
            if i < len(MODULE_SECOND):
                self.table.setItem(i, 1,
                                   QTableWidgetItem(str(MODULE_SECOND[i])))
        root.addWidget(self.table, 1)
        note = QLabel('优先选用第一系列；第二系列仅在必要时使用。')
        note.setStyleSheet(HINT_QSS)
        root.addWidget(note)

    def _filter(self, text):
        text = text.strip()
        for row in range(self.table.rowCount()):
            show = not text
            for col in range(2):
                item = self.table.item(row, col)
                if item and text in item.text():
                    show = True
            self.table.setRowHidden(row, not show)


class MValuePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 14, 16, 14)
        root.setSpacing(10)
        root.addWidget(_title('M 值（跨棒距）计算'))
        tip = QLabel('用于齿轮加工与检验；支持外齿轮/内齿轮，已知 M 值可反求变位系数。')
        tip.setStyleSheet(HINT_QSS)
        root.addWidget(tip)
        card = _card()
        form = QFormLayout(card)
        form.setContentsMargins(16, 14, 16, 14)
        form.setVerticalSpacing(6)
        self.z = _int_spin(20)
        self.mn = _spin(3.0, 0.01, 100, 3, ' mm')
        self.alpha = _spin(20.0, 1, 45, 2, ' °')
        self.x = _spin(0.0, -5, 5, 4)
        self.dp = _spin(5.0, 0.1, 100, 3, ' mm')
        self.beta = _spin(0.0, -45, 45, 2, ' °')
        self.internal = QCheckBox('内齿轮')
        self.target = _spin(66.5, 0.1, 10000, 4, ' mm')
        for label, widget in [('齿数 z', self.z), ('法向模数 mn', self.mn),
                              ('法向压力角 αn', self.alpha),
                              ('变位系数 x', self.x), ('量棒直径 dp', self.dp),
                              ('螺旋角 β', self.beta), ('', self.internal),
                              ('目标 M 值（反求用）', self.target)]:
            _form_row(form, label, widget)
        root.addWidget(card)
        row = QHBoxLayout()
        for text, slot in [('推荐量棒', self.recommend),
                           ('计算 M 值', self.calculate),
                           ('由 M 反求 x', self.inverse)]:
            btn = QPushButton(text)
            btn.setProperty('class', 'b-print')
            btn.setMinimumHeight(32)
            btn.clicked.connect(slot)
            row.addWidget(btn)
        row.addStretch(1)
        root.addLayout(row)
        self.result = _table(['项目', '数值'], 130)
        root.addWidget(self.result)
        self.hint = QLabel('')
        self.hint.setStyleSheet(HINT_QSS)
        root.addWidget(self.hint)
        self.calculate()

    def recommend(self):
        self.dp.setValue(calc_roller_diameter(self.mn.value(),
                                               self.alpha.value()))

    def calculate(self):
        try:
            m = calc_m_value_simple(
                self.z.value(), self.mn.value(), self.alpha.value(),
                self.x.value(), self.dp.value(), self.beta.value(),
                self.internal.isChecked())
            _set_rows(self.result, [
                ('跨棒距 M', '%.4f mm' % m),
                ('量棒直径 dp', '%.3f mm' % self.dp.value()),
                ('齿轮类型', '内齿轮' if self.internal.isChecked()
                 else '外齿轮')])
            self.hint.setText('')
            return m
        except ValueError as exc:
            _set_rows(self.result, [('错误', str(exc))])
            return None

    def inverse(self):
        try:
            x, m = solve_x_from_m_value(
                self.z.value(), self.mn.value(), self.alpha.value(),
                self.dp.value(), self.target.value(), self.beta.value(),
                self.internal.isChecked())
            if x is None:
                _set_rows(self.result, [('结果', '无有效解，请检查 M 值')])
                return None
            self.x.setValue(x)
            _set_rows(self.result, [('变位系数 x', '%.4f' % x),
                                    ('复核 M', '%.4f mm' % m)])
            return x
        except ValueError as exc:
            _set_rows(self.result, [('错误', str(exc))])
            return None


class ToothPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 14, 16, 14)
        root.setSpacing(10)
        root.addWidget(_title('齿厚换算'))
        tip = QLabel('公法线 W、跨棒距 M、法向弧齿厚 sn 互算；W 输入大于 0 时按 W 反求。')
        tip.setStyleSheet(HINT_QSS)
        root.addWidget(tip)
        card = _card()
        form = QFormLayout(card)
        form.setContentsMargins(16, 14, 16, 14)
        form.setVerticalSpacing(6)
        self.z = _int_spin(20)
        self.mn = _spin(3.0, 0.01, 100, 3, ' mm')
        self.alpha = _spin(20.0, 1, 45, 2, ' °')
        self.x = _spin(0.0, -5, 5, 4)
        self.dp = _spin(5.0, 0.1, 100, 3, ' mm')
        self.beta = _spin(0.0, -45, 45, 2, ' °')
        self.k = _int_spin(0, 0, 100)
        self.w = _spin(0.0, 0.0, 10000, 4, ' mm')
        for label, widget in [('齿数 z', self.z), ('法向模数 mn', self.mn),
                              ('法向压力角 αn', self.alpha),
                              ('变位系数 x', self.x), ('量棒直径 dp', self.dp),
                              ('螺旋角 β', self.beta),
                              ('跨齿数 k（0=自动）', self.k),
                              ('已知公法线 W（可选）', self.w)]:
            _form_row(form, label, widget)
        root.addWidget(card)
        row = QHBoxLayout()
        btn = QPushButton('计算')
        btn.setProperty('class', 'b-print')
        btn.setMinimumHeight(32)
        btn.clicked.connect(self.calculate)
        row.addWidget(btn)
        row.addStretch(1)
        root.addLayout(row)
        self.result = _table(['项目', '数值'], 180)
        root.addWidget(self.result)
        self.hint = QLabel('')
        self.hint.setStyleSheet(HINT_QSS)
        root.addWidget(self.hint)
        self.calculate()

    def calculate(self):
        z = self.z.value()
        mn = self.mn.value()
        alpha = self.alpha.value()
        beta = self.beta.value()
        k = self.k.value() or calc_k_from_z(z, alpha, beta)
        try:
            if self.w.value() > 0:
                r = convert_tooth_thickness(
                    z, mn, alpha, None, self.dp.value(), beta,
                    W=self.w.value(), k=k)
            else:
                r = convert_tooth_thickness(
                    z, mn, alpha, self.x.value(), self.dp.value(), beta,
                    k=k)
            if 'error' in r:
                raise ValueError(r['error'])
            self.x.setValue(float(r['x']))
            self.k.setValue(int(r['k']))
            _set_rows(self.result, [
                ('变位系数 x', '%.4f' % r['x']),
                ('跨齿数 k', '%d' % r['k']),
                ('公法线 Wk', '%.4f mm' % r['W']),
                ('法向弧齿厚 sn', '%.4f mm' % r['sn']),
                ('端面弧齿厚 st', '%.4f mm' % r['st']),
                ('跨棒距 M', '%.4f mm' % r.get('M', 0))])
            self.hint.setText('')
            return r
        except (ValueError, ZeroDivisionError) as exc:
            _set_rows(self.result, [('错误', str(exc))])
            return None


class StrengthPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 14, 16, 14)
        root.setSpacing(10)
        root.addWidget(_title('齿轮强度校核'))
        tip = QLabel('按 GB/T 10063 / GB/T 3480 简化计算接触与弯曲强度，结果供方案比较。')
        tip.setStyleSheet(HINT_QSS)
        root.addWidget(tip)
        card = _card()
        form = QFormLayout(card)
        form.setContentsMargins(16, 14, 16, 14)
        form.setVerticalSpacing(5)
        self.z1 = _int_spin(20)
        self.z2 = _int_spin(40)
        self.mn = _spin(3.0, 0.01, 100, 3, ' mm')
        self.alpha = _spin(20.0, 1, 45, 2, ' °')
        self.beta = _spin(0.0, -45, 45, 2, ' °')
        self.b = _spin(20.0, 0.1, 1000, 2, ' mm')
        self.x1 = _spin(0.0, -5, 5, 3)
        self.x2 = _spin(0.0, -5, 5, 3)
        self.t1 = _spin(10.0, 0.01, 100000, 2, ' N·m')
        self.n1 = _spin(1440.0, 1, 100000, 0, ' r/min')
        self.mat1 = QComboBox()
        self.mat2 = QComboBox()
        for key, desc in get_material_list():
            self.mat1.addItem(desc, key)
            self.mat2.addItem(desc, key)
        if self.mat2.count() > 1:
            self.mat2.setCurrentIndex(1)
        self.load = QComboBox()
        for text, key in [('均匀平稳', 'uniform'), ('轻度冲击', 'light'),
                          ('中等冲击', 'medium'), ('严重冲击', 'heavy')]:
            self.load.addItem(text, key)
        for label, widget in [('小轮齿数 z1', self.z1),
                              ('大轮齿数 z2', self.z2),
                              ('法向模数 mn', self.mn),
                              ('法向压力角 αn', self.alpha),
                              ('螺旋角 β', self.beta), ('齿宽 b', self.b),
                              ('变位 x1', self.x1), ('变位 x2', self.x2),
                              ('小轮转矩 T1', self.t1),
                              ('小轮转速 n1', self.n1),
                              ('小轮材料', self.mat1), ('大轮材料', self.mat2),
                              ('载荷类型', self.load)]:
            _form_row(form, label, widget)
        root.addWidget(card)
        row = QHBoxLayout()
        btn = QPushButton('校核')
        btn.setProperty('class', 'b-print')
        btn.setMinimumHeight(32)
        btn.clicked.connect(self.calculate)
        row.addWidget(btn)
        self.status = QLabel('')
        self.status.setStyleSheet('font-size:14px;font-weight:bold;')
        row.addWidget(self.status, 1)
        root.addLayout(row)
        self.result = _table(['项目', '计算值', '许用/安全系数'], 150)
        root.addWidget(self.result)
        self.hint = QLabel('')
        self.hint.setWordWrap(True)
        self.hint.setStyleSheet(HINT_QSS)
        root.addWidget(self.hint)
        self.calculate()

    def calculate(self):
        try:
            r = calc_zhang_xuemeng(
                self.t1.value(), self.z1.value(), self.z2.value(),
                self.mn.value(), self.alpha.value(), self.beta.value(),
                self.b.value(), self.x1.value(), self.x2.value(),
                self.mat1.currentData(), self.mat2.currentData(),
                precision_grade=7, load_type=self.load.currentData(),
                n1=self.n1.value())
            contact = r.get('contact', {})
            b1 = r.get('bending1', {})
            b2 = r.get('bending2', {})
            ok = (contact.get('result') == 'PASS' and
                  b1.get('result') == 'PASS' and b2.get('result') == 'PASS')
            self.status.setText('✓ 通过' if ok else '✗ 不通过')
            self.status.setStyleSheet(
                'font-size:14px;font-weight:bold;color:%s;'
                % ('#1a7f37' if ok else '#c0392b'))
            _set_rows(self.result, [
                ('接触 σH', '%.2f MPa' % contact.get('sigma_H', 0),
                 '许用 %.0f MPa / SH %.2f'
                 % (contact.get('sigma_H_allow', 0),
                    contact.get('SH', 0))),
                ('弯曲(小) σF1', '%.2f MPa' % b1.get('sigma_F', 0),
                 'SF=%.2f' % b1.get('SF', 0)),
                ('弯曲(大) σF2', '%.2f MPa' % b2.get('sigma_F', 0),
                 'SF=%.2f' % b2.get('SF', 0))])
            notes = (r.get('factors') or {}).get('KHb_notes') or []
            pair_notes = (r.get('factors') or {}).get('pair_notes') or []
            self.hint.setText('；'.join(notes + pair_notes))
            return r
        except (ValueError, ZeroDivisionError) as exc:
            _set_rows(self.result, [('错误', str(exc), '')])
            self.status.setText('参数错误')
            self.hint.setText('')
            return None


class TolerancePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 14, 16, 14)
        root.setSpacing(10)
        root.addWidget(_title('齿轮精度等级与公差项目'))
        note = QLabel('公差值需按 GB/T 10095.1 公式及标准原文系数计算；'
                      '下表为等级选用参考。')
        note.setStyleSheet('font-size:12px;color:#a15c00;')
        root.addWidget(note)
        row = QHBoxLayout()
        grades = _table(['等级', '典型用途'], 160)
        _set_rows(grades, [
            ('0~2', '测量齿轮、精密仪器'),
            ('3~5', '航空、精密机床齿轮'),
            ('6~7', '机床、汽车变速箱（常用）'),
            ('8~9', '一般机械、农机'),
            ('10~12', '低速粗糙传动')])
        items = _table(['代号', '公差项目'], 160)
        _set_rows(items, [
            ('Fp', '齿距累积总偏差'),
            ('fpt', '单个齿距偏差'),
            ('Fα', '齿廓总偏差'),
            ('Fβ', '螺旋线总偏差'),
            ('Fr', '径向跳动')])
        row.addWidget(grades, 1)
        row.addWidget(items, 1)
        root.addLayout(row)
        info = QLabel('· 精度等级数字越小精度越高（0 最高，12 最低）\n'
                      '· 常用等级：汽车 6~7 级，农机 8~9 级，机床 5~6 级\n'
                      '· 齿轮副一般按较重要的一方选取，并核对标准原文')
        info.setStyleSheet(HINT_QSS)
        root.addWidget(info)
        root.addStretch(1)


class STPPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 14, 16, 14)
        root.setSpacing(10)
        root.addWidget(_title('STP 生成'))
        self.env = QLabel('')
        self.env.setStyleSheet(HINT_QSS)
        root.addWidget(self.env)
        card = _card()
        form = QFormLayout(card)
        form.setContentsMargins(16, 14, 16, 14)
        form.setVerticalSpacing(6)
        self.mode = _combo(['直齿圆柱齿轮', '斜齿圆柱齿轮'])
        self.m = _spin(3.0, 0.01, 100, 3, ' mm')
        self.z = _int_spin(20)
        self.b = _spin(20.0, 0.1, 1000, 2, ' mm')
        self.bore = _spin(10.0, 0.0, 500, 2, ' mm')
        self.alpha = _spin(20.0, 1, 45, 2, ' °')
        self.beta = _spin(0.0, -45, 45, 2, ' °')
        self.x = _spin(0.0, -5, 5, 3)
        self.ha = _spin(1.0, 0.1, 2, 2)
        self.c = _spin(0.25, 0, 1, 2)
        for label, widget in [('类型', self.mode), ('模数 m', self.m),
                              ('齿数 z', self.z), ('齿宽 b', self.b),
                              ('轴孔直径', self.bore),
                              ('压力角 α', self.alpha),
                              ('螺旋角 β', self.beta), ('变位系数 x', self.x),
                              ('齿顶高系数', self.ha), ('顶隙系数', self.c)]:
            _form_row(form, label, widget)
        root.addWidget(card)
        path_row = QHBoxLayout()
        path_row.addWidget(QLabel('输出文件'))
        self.path = QLineEdit()
        self.path.setText(os.path.join(os.path.expanduser('~'), 'gear.step'))
        path_row.addWidget(self.path, 1)
        browse = QPushButton('浏览…')
        browse.setProperty('class', 'b-print')
        browse.clicked.connect(self._browse)
        path_row.addWidget(browse)
        root.addLayout(path_row)
        row = QHBoxLayout()
        btn = QPushButton('生成 STP')
        btn.setProperty('class', 'b-print')
        btn.setMinimumHeight(34)
        btn.clicked.connect(self.generate)
        row.addWidget(btn)
        self.status = QLabel('')
        self.status.setWordWrap(True)
        self.status.setStyleSheet(HINT_QSS)
        row.addWidget(self.status, 1)
        root.addLayout(row)
        self.hint = QLabel(
            '说明：CadQuery/OCP 已安装到独立 Python 3.12 环境；'
            '生成时由该环境建模并导出 STEP。首次生成需要几秒到几十秒。')
        self.hint.setWordWrap(True)
        self.hint.setStyleSheet(HINT_QSS)
        root.addWidget(self.hint)
        root.addStretch(1)
        python = find_python(False)
        if python:
            self.env.setText('CadQuery 环境：%s' % python)
            self.env.setStyleSheet('font-size:12px;color:#1a7f37;')
        else:
            self.env.setText('未找到 CadQuery/OCP：请设置 FLANGE_CADQUERY_PYTHON '
                             '或安装 _cadquery_env。')
            self.env.setStyleSheet('font-size:12px;color:#c0392b;')

    def _browse(self):
        path, _ = QFileDialog.getSaveFileName(
            self, '保存 STEP', self.path.text(), 'STEP (*.step *.stp)')
        if path:
            self.path.setText(path)

    def generate(self):
        path = self.path.text().strip()
        if not path:
            self.status.setText('请先指定输出文件。')
            return None
        if not path.lower().endswith(('.step', '.stp')):
            path += '.step'
            self.path.setText(path)
        params = {'m': self.m.value(), 'z': self.z.value(),
                  'b': self.b.value(), 'bore': self.bore.value(),
                  'alpha': self.alpha.value(), 'beta': self.beta.value(),
                  'x': self.x.value(), 'ha_star': self.ha.value(),
                  'c_star': self.c.value()}
        mode = 'helical' if self.mode.currentIndex() == 1 else 'spur'
        self.status.setText('正在生成，请稍候…')
        try:
            generate_step(mode, params, path)
            self.status.setText('已生成：%s（%.1f KB）'
                                % (path, os.path.getsize(path) / 1024.0))
            self.status.setStyleSheet('font-size:12px;color:#1a7f37;')
            return path
        except Exception as exc:
            self.status.setText('生成失败：%s' % exc)
            self.status.setStyleSheet('font-size:12px;color:#c0392b;')
            return None


class GearPage(QWidget):
    """齿轮参数工具主页面：按原版页签组织。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 18, 28, 18)
        root.setSpacing(10)
        title = QLabel('齿轮参数工具')
        title.setStyleSheet('font-size:22px;font-weight:bold;color:#163a5f;')
        sub = QLabel('圆柱齿轮/锥齿轮几何、配对、模数、M 值、齿厚与强度校核。')
        sub.setStyleSheet('color:#666;font-size:12px;')
        root.addWidget(title)
        root.addWidget(sub)
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(
            'QTabWidget::pane{border:1px solid #c9d2dc;background:#fff;}'
            'QTabBar::tab{padding:6px 14px;background:#f5f7fa;'
            'border:1px solid #c9d2dc;border-bottom:none;margin-right:2px;}'
            'QTabBar::tab:selected{background:#fff;color:#1f4e79;'
            'font-weight:bold;}')
        self.basic = BasicGearPage()
        self.pair = PairGearPage()
        self.module = ModulePage()
        self.m_value = MValuePage()
        self.tooth = ToothPage()
        self.strength = StrengthPage()
        self.tolerance = TolerancePage()
        self.stp = STPPage()
        for page, name in [(self.basic, '基本参数'), (self.pair, '配对齿轮'),
                           (self.module, '标准模数'), (self.m_value, 'M值计算'),
                           (self.tooth, '齿厚换算'), (self.strength, '强度校核'),
                           (self.tolerance, '精度查询'), (self.stp, 'STP生成')]:
            if name in ('基本参数', 'M值计算', '齿厚换算', '强度校核'):
                page = _scroll(page)
            self.tabs.addTab(page, name)
        root.addWidget(self.tabs, 1)
        self.basic.calculate()

    def calculate(self):
        """兼容原齿轮页调用：计算基本参数页。"""
        return self.basic.calculate()
