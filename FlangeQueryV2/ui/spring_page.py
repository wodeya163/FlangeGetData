# -*- coding: utf-8 -*-
"""弹簧设计页：压缩、拉伸、扭转弹簧设计校核。"""

import os

from PyQt5.QtWidgets import (QCheckBox, QComboBox, QDoubleSpinBox,
                             QFileDialog, QFormLayout, QFrame, QHBoxLayout,
                             QLabel, QPushButton, QStackedWidget, QTableWidget,
                             QTableWidgetItem, QVBoxLayout, QWidget)

from core.spring_data import MATERIALS
from core.spring_calc import (design_compression, design_tension,
                              design_torsion)
from core.spring_export import export_compression

CARD_QSS = ('#spring_input{background:#fff;border:1px solid #c9d2dc;'
            'border-radius:6px;}')
RESULT_QSS = ('#spring_result{background:#f5f8fb;'
              'border:1px solid #c9d2dc;border-radius:6px;}')
HINT_QSS = 'font-size:12px;color:#666;'


def _label(text, size=13, color='#333', bold=False):
    lab = QLabel(text)
    lab.setStyleSheet('font-size:%dpx;color:%s;%s'
                      % (size, color, 'font-weight:bold;' if bold else ''))
    return lab


def _spin(value, maximum, suffix='', decimals=2):
    box = QDoubleSpinBox()
    box.setRange(0.0, maximum)
    box.setDecimals(decimals)
    box.setValue(value)
    box.setSuffix(suffix)
    box.setKeyboardTracking(False)
    box.setMinimumWidth(180)
    return box


def _table(headers):
    table = QTableWidget(0, len(headers))
    table.setHorizontalHeaderLabels(headers)
    table.verticalHeader().setVisible(False)
    table.setEditTriggers(QTableWidget.NoEditTriggers)
    table.setSelectionMode(QTableWidget.NoSelection)
    table.horizontalHeader().setStretchLastSection(True)
    table.setStyleSheet('QTableWidget{background:#fff;border:1px solid #d6dee7;'
                        'font-size:12px;} QHeaderView::section{background:#eef3f8;'
                        'padding:4px;font-weight:bold;}')
    return table


def _rows(table, rows):
    table.setRowCount(len(rows))
    for i, row in enumerate(rows):
        for j, value in enumerate(row):
            table.setItem(i, j, QTableWidgetItem(str(value)))
    table.resizeColumnsToContents()


class SpringPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.result = None
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 18, 28, 18)
        root.setSpacing(10)
        head = QHBoxLayout()
        head.addWidget(_label('弹簧设计', 22, '#163a5f', True))
        head.addSpacing(20)
        head.addWidget(QLabel('类型'))
        self.kind = QComboBox()
        self.kind.addItems(['压缩弹簧', '拉伸弹簧', '扭转弹簧'])
        self.kind.currentIndexChanged.connect(self._switch)
        head.addWidget(self.kind)
        head.addStretch(1)
        root.addLayout(head)
        self.subtitle = QLabel(
            '按 GB/T 23935-2009 估算线径、中径、有效圈数、刚度、'
            '应力和稳定性；结果供方案比较。')
        self.subtitle.setStyleSheet(HINT_QSS)
        root.addWidget(self.subtitle)

        body = QHBoxLayout()
        body.setSpacing(16)
        left = QFrame()
        left.setFixedWidth(500)
        left.setStyleSheet(CARD_QSS)
        lv = QVBoxLayout(left)
        lv.setContentsMargins(16, 14, 16, 14)
        lv.setSpacing(8)
        lv.addWidget(_label('输入参数', 16, '#1f4e79', True))

        self.material = QComboBox()
        for i, item in enumerate(MATERIALS):
            self.material.addItem(item['name'], i)
        self.material.currentIndexChanged.connect(self._material_info)
        self.material_info = QLabel('')
        self.material_info.setWordWrap(True)
        self.material_info.setStyleSheet(HINT_QSS)
        mform = QFormLayout()
        mform.setHorizontalSpacing(12)
        mform.setVerticalSpacing(6)
        mform.addRow(_label('材料'), self.material)
        lv.addLayout(mform)
        lv.addWidget(self.material_info)
        self.load = QComboBox()
        for text, key in [('静载荷', 'static'), ('有限寿命', 'finite'),
                          ('无限寿命', 'infinite')]:
            self.load.addItem(text, key)
        lv.addWidget(self._row('载荷类型', self.load))

        self.stack = QStackedWidget()
        self._build_force_form()
        self._build_torque_form()
        lv.addWidget(self.stack)

        opt = QFormLayout()
        opt.setHorizontalSpacing(12)
        opt.setVerticalSpacing(6)
        self.c_user = _spin(0.0, 30.0, '', 1)
        self.dmax = _spin(0.0, 5000.0, ' mm', 1)
        self.high = QCheckBox('动载荷取许用应力上限')
        opt.addRow(_label('旋绕比 C（0=自动）'), self.c_user)
        opt.addRow(_label('最大外径 Dmax（0=不限）'), self.dmax)
        opt.addRow(_label(''), self.high)
        lv.addLayout(opt)

        btn = QPushButton('设计校核')
        btn.setProperty('class', 'b-print')
        btn.setMinimumHeight(34)
        btn.clicked.connect(self.calculate)
        lv.addWidget(btn)
        exp = QHBoxLayout()
        self.export_stl = QPushButton('导出 STL')
        self.export_step = QPushButton('导出 STEP')
        for b in (self.export_stl, self.export_step):
            b.setStyleSheet('background:#fff;border:1px solid #c9d2dc;'
                            'border-radius:4px;padding:4px 10px;')
            b.setMinimumHeight(30)
            exp.addWidget(b)
        exp.addStretch(1)
        self.export_stl.clicked.connect(lambda: self._export('stl'))
        self.export_step.clicked.connect(lambda: self._export('step'))
        lv.addLayout(exp)
        self.export_status = QLabel('')
        self.export_status.setStyleSheet(HINT_QSS)
        self.export_status.setWordWrap(True)
        lv.addWidget(self.export_status)
        lv.addStretch(1)
        body.addWidget(left)

        right = QFrame()
        right.setStyleSheet(RESULT_QSS)
        rv = QVBoxLayout(right)
        rv.setContentsMargins(18, 16, 18, 16)
        rv.setSpacing(8)
        rv.addWidget(_label('设计结果', 16, '#1f4e79', True))
        self.headline = QLabel('—')
        self.headline.setStyleSheet(
            'font-size:30px;font-weight:bold;color:#163a5f;')
        rv.addWidget(self.headline)
        self.status = QLabel('')
        self.status.setStyleSheet('font-size:14px;font-weight:bold;')
        rv.addWidget(self.status)
        self.table = _table(['项目', '结果'])
        self.table.setMinimumHeight(280)
        rv.addWidget(self.table, 1)
        self.notes = QLabel('')
        self.notes.setWordWrap(True)
        self.notes.setStyleSheet('font-size:12px;color:#8a5a00;')
        rv.addWidget(self.notes)
        body.addWidget(right, 1)
        root.addLayout(body, 1)
        self._material_info()
        self._switch()

    def _row(self, text, widget):
        box = QWidget()
        lay = QHBoxLayout(box)
        lay.setContentsMargins(0, 0, 0, 0)
        lab = _label(text)
        lab.setMinimumWidth(110)
        lay.addWidget(lab)
        lay.addWidget(widget, 1)
        return box

    def _build_force_form(self):
        page = QWidget()
        form = QFormLayout(page)
        form.setContentsMargins(0, 0, 0, 0)
        form.setHorizontalSpacing(12)
        form.setVerticalSpacing(6)
        self.f2 = _spin(100.0, 1e7, ' N')
        self.f1 = _spin(20.0, 1e7, ' N')
        self.stroke = _spin(20.0, 1e6, ' mm')
        for label, widget in [('最大工作负荷 F2', self.f2),
                              ('最小工作负荷 F1', self.f1),
                              ('工作行程', self.stroke)]:
            form.addRow(_label(label), widget)
        self.stack.addWidget(page)

    def _build_torque_form(self):
        page = QWidget()
        form = QFormLayout(page)
        form.setContentsMargins(0, 0, 0, 0)
        form.setHorizontalSpacing(12)
        form.setVerticalSpacing(6)
        self.m2 = _spin(10000.0, 1e9, ' N·mm')
        self.m1 = _spin(1000.0, 1e9, ' N·mm')
        self.angle = _spin(30.0, 100000.0, ' °')
        for label, widget in [('最大扭矩 M2', self.m2),
                              ('最小扭矩 M1', self.m1),
                              ('工作扭转角 φ', self.angle)]:
            form.addRow(_label(label), widget)
        self.stack.addWidget(page)

    def _material_info(self, *_):
        item = MATERIALS[self.material.currentData()]
        self.material_info.setText(
            '%s　%s / %s　G=%.0f MPa　E=%.0f MPa　温度 %s'
            % (item['std'], item['name'], item['group'],
               item['G'], item['E'], item['temp']))

    def _switch(self):
        self.stack.setCurrentIndex(1 if self.kind.currentIndex() == 2 else 0)
        self.calculate()

    def calculate(self):
        idx = self.material.currentData()
        if idx is None:
            return None
        material = MATERIALS[idx]
        load = self.load.currentData()
        use_high = self.high.isChecked()
        c_user = self.c_user.value() or None
        dmax = self.dmax.value() or None
        try:
            if self.kind.currentIndex() == 2:
                r = design_torsion(
                    self.m2.value(), self.m1.value(), self.angle.value(),
                    material, load, c_user, dmax, use_high)
            elif self.kind.currentIndex() == 1:
                r = design_tension(
                    self.f2.value(), self.f1.value(), self.stroke.value(),
                    material, load, c_user, dmax, use_high)
            else:
                r = design_compression(
                    self.f2.value(), self.f1.value(), self.stroke.value(),
                    material, load, c_user, dmax, use_high)
        except (ValueError, ZeroDivisionError, TypeError) as exc:
            self.headline.setText('参数错误')
            self.status.setText('')
            _rows(self.table, [('错误', str(exc))])
            self.notes.setText('')
            return None
        self.result = r
        self._render(r)
        return r

    def _export(self, ext):
        if not self.result or self.result.get('type') != 'compression':
            self.export_status.setText('三维导出目前仅支持压缩弹簧。')
            return None
        default = os.path.join(os.path.expanduser('~'),
                               'spring_%gx%g.%s' % (
                                   self.result['d'], self.result['D'], ext))
        filt = 'STL (*.stl)' if ext == 'stl' else 'STEP (*.step *.stp)'
        path, _ = QFileDialog.getSaveFileName(
            self, '导出弹簧三维模型', default, filt)
        if not path:
            return None
        try:
            export_compression(self.result, path)
            self.export_status.setText('已导出：%s（%.1f KB）'
                                       % (path, os.path.getsize(path) / 1024.0))
            self.export_status.setStyleSheet('font-size:12px;color:#1a7f37;')
            return path
        except Exception as exc:
            self.export_status.setText('导出失败：%s' % exc)
            self.export_status.setStyleSheet('font-size:12px;color:#c0392b;')
            return None

    def _render(self, r):
        kind = r['type']
        self.headline.setText('d=%.2f　D=%.2f mm' % (r['d'], r['D']))
        if kind == 'torsion':
            rows = [
                ('线径 d', '%.2f mm' % r['d']),
                ('中径 D', '%.2f mm' % r['D']),
                ('旋绕比 C', '%.2f' % r['C']),
                ('有效圈数 n', '%.1f' % r['n']),
                ('实际扭转角', '%.2f°（需求 %.2f°）'
                 % (r['angle_actual'], r['angle'])),
                ('实际扭转刚度', '%.2f N·mm/°' % r['k_torque_actual']),
                ('最大弯曲应力', '%.2f / %.2f MPa'
                 % (r['sigma_max'], r['sigma_allow'])),
                ('弯曲安全系数', '%.2f' % r['safety']),
                ('试验扭矩 Ts', '%.0f N·mm' % r['Ts']),
            ]
            if r.get('fatigue_safety') is not None:
                rows.append(('疲劳安全系数', '%.2f' % r['fatigue_safety']))
            ok = r['safety'] >= 1.1
        else:
            rows = [
                ('线径 d', '%.2f mm' % r['d']),
                ('中径 D', '%.2f mm' % r['D']),
                ('旋绕比 C', '%.2f' % r['C']),
                ('有效圈数 n', '%.1f（总圈数 %.1f）' % (r['n'], r['n1'])),
                ('刚度 F′', '%.3f N/mm' % r['k']),
                ('自由高度 H0', '%.2f mm' % r['H0']),
                ('最大切应力 τmax', '%.2f / %.2f MPa'
                 % (r['tau_max'], r['tau_allow'])),
                ('切应力安全系数', '%.2f' % r['safety']),
            ]
            if kind == 'compression':
                rows += [('节距 t', '%.2f mm' % r['pitch']),
                         ('压并高度 Hb', '%.2f mm' % r['Hb']),
                         ('可压缩量 fmax', '%.2f mm' % r['f_max'])]
            if r.get('fatigue_safety') is not None:
                rows.append(('疲劳安全系数', '%.2f' % r['fatigue_safety']))
            ok = r['safety'] >= 1.1
        _rows(self.table, rows)
        self.status.setText('通过（安全系数 ≥ 1.1）' if ok else '安全系数不足')
        self.status.setStyleSheet(
            'font-size:14px;font-weight:bold;color:%s;'
            % ('#1a7f37' if ok else '#c0392b'))
        notes = []
        for key in ('stability_note', 'c_note', 'fatigue_note',
                    'tension_note', 'arm_note', 'H0_note'):
            value = r.get(key)
            if value:
                notes.append(value)
        notes += r.get('geometry_notes') or []
        notes += r.get('warnings') or []
        notes += r.get('ts_notes') or []
        self.notes.setText('\n'.join(notes))
        enabled = kind == 'compression'
        self.export_stl.setEnabled(enabled)
        self.export_step.setEnabled(enabled)
        if not enabled:
            self.export_status.setText('三维导出仅支持压缩弹簧。')
        else:
            self.export_status.setText('可导出 STL；STEP 需要 CadQuery/OCP 环境。')
