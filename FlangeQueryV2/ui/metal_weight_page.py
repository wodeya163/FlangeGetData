# -*- coding: utf-8 -*-
"""金属材料重量计算页（板材/棒材/管材/角钢/槽钢/工字钢）。"""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QComboBox, QDoubleSpinBox, QFormLayout,
                             QFrame, QHBoxLayout, QLabel, QPushButton,
                             QSpinBox, QVBoxLayout, QWidget)

from core.metal_weight import (CHANNEL_TABLE, IBEAM_TABLE, MATERIALS,
                               SHAPES, UNIT_TO_CM, calculate)

RESULT_FACTORS = [('kg', 1.0), ('g', 1000.0), ('t', 0.001)]


class MetalWeightPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.unit = 'mm'
        self.dim_widgets = {}
        self.result = None
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 20, 28, 20)
        root.setSpacing(10)
        root.addWidget(self._label('金属材料重量', 22, '#163a5f', True))
        root.addWidget(self._label(
            '板材、圆棒、方棒、六角棒、圆管、方管、角钢，以及 GB/T 706 '
            '槽钢/工字钢；16 种金属与自定义密度。', 12, '#666'))

        body = QHBoxLayout()
        body.setSpacing(16)
        left = QFrame()
        left.setFixedWidth(510)
        left.setStyleSheet('#metal_input{background:#fff;border:1px solid #c9d2dc;'
                           'border-radius:6px;}')
        left.setObjectName('metal_input')
        lv = QVBoxLayout(left)
        lv.setContentsMargins(16, 14, 16, 14)
        lv.setSpacing(8)
        lv.addWidget(self._label('计算参数', 16, '#1f4e79', True))
        top = QFormLayout()
        top.setHorizontalSpacing(12)
        top.setVerticalSpacing(6)
        self.shape = QComboBox()
        for shape in SHAPES:
            self.shape.addItem(shape['name'], shape['id'])
        self.shape.currentIndexChanged.connect(self._shape_changed)
        self.material = QComboBox()
        for mid, name, density in MATERIALS:
            self.material.addItem('%s（%.2f）' % (name, density), mid)
        self.material.addItem('自定义材料', 'custom')
        self.material.currentIndexChanged.connect(self._material_changed)
        self.unit_box = QComboBox()
        for name, factor in (('mm', 0.1), ('cm', 1.0), ('m', 100.0)):
            self.unit_box.addItem(name, name)
        self.unit_box.currentIndexChanged.connect(self._unit_changed)
        self.result_unit = QComboBox()
        for name, factor in RESULT_FACTORS:
            self.result_unit.addItem(name, name)
        self.result_unit.currentIndexChanged.connect(self.calculate)
        self.qty = QSpinBox()
        self.qty.setRange(1, 99999)
        self.qty.setValue(1)
        self.price = QDoubleSpinBox()
        self.price.setRange(0, 1e6)
        self.price.setDecimals(2)
        self.price.setValue(0)
        self.price.setSuffix(' 元/kg')
        for label, w in [('型材', self.shape), ('材质', self.material),
                         ('尺寸单位', self.unit_box), ('结果单位', self.result_unit),
                         ('数量', self.qty),
                         ('公斤单价（元/kg，可选）', self.price)]:
            top.addRow(self._label(label), w)
        lv.addLayout(top)

        self.custom_row = QWidget()
        crow = QHBoxLayout(self.custom_row)
        crow.setContentsMargins(0, 0, 0, 0)
        crow.addWidget(self._label('自定义密度'))
        self.custom_density = QDoubleSpinBox()
        self.custom_density.setRange(0.1, 30.0)
        self.custom_density.setDecimals(3)
        self.custom_density.setValue(7.85)
        self.custom_density.setSuffix(' g/cm³')
        crow.addWidget(self.custom_density, 1)
        self.custom_row.setVisible(False)
        lv.addWidget(self.custom_row)

        lv.addWidget(self._label('截面尺寸', 13, '#1f4e79', True))
        self.dim_form = QFormLayout()
        self.dim_form.setHorizontalSpacing(12)
        self.dim_form.setVerticalSpacing(6)
        lv.addLayout(self.dim_form)

        self.hint = QLabel('')
        self.hint.setWordWrap(True)
        self.hint.setStyleSheet('font-size:11px;color:#777;')
        lv.addWidget(self.hint)
        lv.addStretch(1)
        buttons = QHBoxLayout()
        calc = QPushButton('计算')
        calc.setProperty('class', 'b-print')
        calc.setMinimumHeight(34)
        calc.clicked.connect(self.calculate)
        reset = QPushButton('重置')
        reset.setProperty('class', 'b-exp')
        reset.setMinimumHeight(34)
        reset.clicked.connect(self.reset)
        buttons.addWidget(calc)
        buttons.addWidget(reset)
        buttons.addStretch(1)
        lv.addLayout(buttons)
        body.addWidget(left)

        right = QFrame()
        right.setObjectName('metal_result')
        right.setStyleSheet('#metal_result{background:#f5f8fb;'
                            'border:1px solid #c9d2dc;border-radius:6px;}')
        rv = QVBoxLayout(right)
        rv.setContentsMargins(22, 18, 22, 18)
        rv.setSpacing(9)
        rv.addWidget(self._label('计算结果', 16, '#1f4e79', True))
        row = QHBoxLayout()
        self.mass = QLabel('—')
        self.mass.setStyleSheet(
            'font-size:44px;font-weight:bold;color:#163a5f;')
        row.addWidget(self.mass)
        self.mass_unit = QLabel('')
        self.mass_unit.setStyleSheet('font-size:14px;color:#777;')
        row.addWidget(self.mass_unit, 0, Qt.AlignBottom)
        row.addStretch(1)
        rv.addLayout(row)
        self.material_line = QLabel('')
        self.material_line.setStyleSheet('font-size:13px;color:#333;')
        rv.addWidget(self.material_line)
        rv.addWidget(self._divider())
        self.total = QLabel('')
        self.per_meter = QLabel('')
        self.volume = QLabel('')
        for w in (self.total, self.per_meter, self.volume):
            w.setStyleSheet('font-size:13px;color:#333;')
            w.setWordWrap(True)
            rv.addWidget(w)
        rv.addWidget(self._divider())
        self.formula = QLabel('')
        self.formula.setWordWrap(True)
        self.formula.setStyleSheet(
            'font-size:13px;color:#1f4e79;background:#eef4fa;'
            'padding:8px;border-radius:4px;')
        rv.addWidget(self.formula)
        self.detail = QLabel('')
        self.detail.setWordWrap(True)
        self.detail.setStyleSheet('font-size:12px;color:#555;')
        rv.addWidget(self.detail)
        self.price_line = QLabel('')
        self.price_line.setWordWrap(True)
        self.price_line.setStyleSheet(
            'font-size:15px;font-weight:bold;color:#1a7f37;'
            'background:#eef7f0;padding:8px;border-radius:4px;')
        rv.addWidget(self.price_line)
        rv.addStretch(1)
        body.addWidget(right, 1)
        root.addLayout(body, 1)
        self._shape_changed()

    @staticmethod
    def _label(text, size=13, color='#333', bold=False):
        lab = QLabel(text)
        lab.setStyleSheet('font-size:%dpx;color:%s;%s'
                          % (size, color, 'font-weight:bold;' if bold else ''))
        return lab

    @staticmethod
    def _divider():
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet('color:#d6dee7;')
        return line

    def _shape(self):
        sid = self.shape.currentData()
        return next(s for s in SHAPES if s['id'] == sid)

    def _clear_dim_form(self):
        while self.dim_form.rowCount():
            self.dim_form.removeRow(0)
        self.dim_widgets = {}

    def _shape_changed(self, *_):
        shape = self._shape()
        self._clear_dim_form()
        unit_name = self.unit_box.currentData()
        factor = UNIT_TO_CM['mm'] / UNIT_TO_CM[unit_name]
        for param in shape['params']:
            key, label = param[0], param[1]
            if len(param) > 2 and param[2] == 'select':
                box = QComboBox()
                table = CHANNEL_TABLE if shape['table'] == 'channel' else IBEAM_TABLE
                for spec, (name, kgm) in table.items():
                    box.addItem('%s　%s' % (spec, name), spec)
                default_spec = shape['defaults'].get('spec', '')
                idx = box.findData(default_spec)
                if idx >= 0:
                    box.setCurrentIndex(idx)
            else:
                box = QDoubleSpinBox()
                box.setRange(0.001, 1e7)
                box.setDecimals(3)
                box.setValue(shape['defaults'].get(key, 1.0) * factor)
                box.setSuffix(' ' + unit_name)
                box.setKeyboardTracking(False)
            self.dim_widgets[key] = box
            self.dim_form.addRow(self._label(label), box)
        if shape.get('table'):
            self.hint.setText('槽钢/工字钢按 GB/T 706 理论重量，钢材基准密度 7.85 g/cm³；'
                              '其他材质按密度换算。')
        elif shape['id'] in ('round-tube', 'square-tube'):
            self.hint.setText('壁厚需小于外径/外边长的一半。')
        elif shape['id'] == 'angle':
            self.hint.setText('角钢按 (A+B−t)×t 的简化截面计算。')
        else:
            self.hint.setText('尺寸单位切换时，已输入的尺寸会自动换算。')
        self._clear_result()

    def _material_changed(self, *_):
        self.custom_row.setVisible(self.material.currentData() == 'custom')

    def _unit_changed(self, *_):
        new = self.unit_box.currentData()
        if new == self.unit:
            return
        factor = UNIT_TO_CM[self.unit] / UNIT_TO_CM[new]
        for box in self.dim_widgets.values():
            if isinstance(box, QDoubleSpinBox):
                box.blockSignals(True)
                box.setValue(box.value() * factor)
                box.setSuffix(' ' + new)
                box.blockSignals(False)
        self.unit = new
        self._clear_result()

    def _clear_result(self):
        self.mass.setText('—')
        self.mass_unit.setText('')
        self.material_line.setText('')
        self.total.setText('')
        self.per_meter.setText('')
        self.volume.setText('')
        self.price_line.setText('')
        self.formula.setText('')
        self.detail.setText('')

    def reset(self):
        self.qty.setValue(1)
        self.price.setValue(0)
        self.material.setCurrentIndex(0)
        self.unit_box.setCurrentIndex(0)
        self.unit = 'mm'
        self._shape_changed()

    def calculate(self):
        dims = {}
        for key, box in self.dim_widgets.items():
            if isinstance(box, QComboBox):
                dims[key] = box.currentData()
            else:
                dims[key] = box.value()
        try:
            res = calculate(
                self.shape.currentData(), self.material.currentData(), dims,
                self.unit_box.currentData(), self.qty.value(),
                self.price.value(),
                self.custom_density.value()
                if self.material.currentData() == 'custom' else None)
        except ValueError as exc:
            self._clear_result()
            self.mass.setText('参数错误')
            self.detail.setText(str(exc))
            return None
        self.result = res
        factor = dict(RESULT_FACTORS)[self.result_unit.currentData()]
        self.mass.setText('%.3f' % (res['mass'] * factor))
        self.mass_unit.setText(self.result_unit.currentData())
        self.material_line.setText('%s　%s　密度 %.2f g/cm³'
                                   % (res['shape'], res['material'],
                                      res['density']))
        self.total.setText('总重量：%.3f kg（%d 件）'
                           % (res['total'], res['quantity']))
        self.per_meter.setText('每米重量：%.3f kg/m' % res['per_meter'])
        self.volume.setText('体积：%.6f m³' % res['volume'])
        if res['price'] is None:
            self.price_line.setText('采购价格：未填写公斤单价')
        else:
            self.price_line.setText('采购价格：%.2f 元（单价 %.2f 元/kg）'
                                    % (res['price'], self.price.value()))
        self.formula.setText(res['formula'])
        self.detail.setText(res['detail'])
        return res
