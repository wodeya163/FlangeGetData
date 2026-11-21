# -*- coding: utf-8 -*-
"""重量计算页：左侧参数输入，右侧结果。"""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QComboBox, QDoubleSpinBox, QFormLayout,
                             QFrame, QHBoxLayout, QLabel, QPushButton,
                             QStackedWidget, QTabWidget, QVBoxLayout,
                             QWidget)

from core.weight import (DENSITY_STEEL, ELBOW_MATERIALS, angle_tee_weight,
                         bend_tee_weight, elbow_weight,
                         large_radius_elbow_weight, pipe_weight, tee_weight)
from drawspec.weight_elbow import build_elbow_weight_spec
from drawspec.weight_tee import build_tee_weight_spec
from drawspec.weight_pipe import build_pipe_weight_spec
from drawspec.renderer import render_pixmap

KINDS = {
    'pipe': '直管重量',
    'elbow': '弯头重量',
    'tee': '三通重量',
}


class WeightPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('weight_page')
        self.kind = 'pipe'
        self._forms = {}
        self._inputs = {}

        root = QVBoxLayout(self)
        root.setContentsMargins(28, 22, 28, 22)
        root.setSpacing(14)
        title = QLabel('重量计算')
        title.setStyleSheet('font-size:22px;font-weight:bold;color:#163a5f;')
        sub = QLabel('参数全部手动输入；单位：外径/壁厚/半径/长度 mm，'
                     '直管长度 m，密度 kg/m³。')
        sub.setStyleSheet('color:#666;font-size:12px;')
        root.addWidget(title)
        root.addWidget(sub)

        body = QHBoxLayout()
        body.setSpacing(18)

        left = QFrame()
        left.setObjectName('weight_input')
        left.setFixedWidth(520)
        left.setStyleSheet(
            '#weight_input{background:#fff;border:1px solid #c9d2dc;'
            'border-radius:6px;}')
        lv = QVBoxLayout(left)
        lv.setContentsMargins(18, 16, 18, 16)
        lv.setSpacing(12)
        self.form_title = QLabel('直管重量')
        self.form_title.setStyleSheet(
            'font-size:16px;font-weight:bold;color:#1f4e79;')
        lv.addWidget(self.form_title)
        self.stack = QStackedWidget()
        self.stack.addWidget(self._build_pipe())
        self.stack.addWidget(self._build_elbow())
        self.stack.addWidget(self._build_tee())
        lv.addWidget(self.stack)
        price_row = QHBoxLayout()
        price_row.addWidget(self._label('公斤单价（元/kg）'))
        self.unit_price = self._spin(0.0, 1e6, suffix=' 元/kg')
        self.unit_price.setRange(0.0, 1e6)
        price_row.addWidget(self.unit_price)
        price_row.addStretch(1)
        lv.addLayout(price_row)
        self.tee_price = self.unit_price
        btns = QHBoxLayout()
        self.calc_btn = QPushButton('计算')
        self.calc_btn.setProperty('class', 'b-print')
        self.calc_btn.setMinimumHeight(34)
        self.calc_btn.setMinimumWidth(100)
        self.calc_btn.clicked.connect(self.calculate)
        reset = QPushButton('重置')
        reset.setProperty('class', 'b-exp')
        reset.setMinimumHeight(34)
        reset.setMinimumWidth(100)
        reset.clicked.connect(self.reset)
        btns.addWidget(self.calc_btn)
        btns.addWidget(reset)
        btns.addStretch(1)
        lv.addLayout(btns)
        body.addWidget(left)

        result = QFrame()
        result.setObjectName('weight_result')
        result.setStyleSheet(
            '#weight_result{background:#f5f8fb;border:1px solid #c9d2dc;'
            'border-radius:6px;}')
        rv = QVBoxLayout(result)
        rv.setContentsMargins(24, 20, 24, 20)
        rv.setSpacing(10)
        self.preview = QLabel('')
        self.preview.setFixedHeight(240)
        self.preview.setAlignment(Qt.AlignCenter)
        self.preview.setStyleSheet(
            'background:#fff;border:1px solid #d6dee7;border-radius:4px;')
        rv.addWidget(self.preview)
        rv.addWidget(self._label('计算结果', 16, '#1f4e79', bold=True))
        self.mass = QLabel('—')
        self.mass.setStyleSheet(
            'font-size:52px;font-weight:bold;color:#163a5f;')
        self.mass.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        rv.addWidget(self.mass)
        self.unit = QLabel('质量 kg')
        self.unit.setStyleSheet('color:#777;font-size:13px;')
        rv.addWidget(self.unit)
        rv.addSpacing(8)
        self.volume = QLabel('')
        self.volume.setStyleSheet('font-size:14px;color:#333;')
        rv.addWidget(self.volume)
        self.detail = QLabel('')
        self.detail.setWordWrap(True)
        self.detail.setStyleSheet('font-size:13px;color:#555;')
        rv.addWidget(self.detail)
        self.formula = QLabel('')
        self.formula.setWordWrap(True)
        self.formula.setStyleSheet(
            'font-size:13px;color:#1f4e79;background:#eef4fa;'
            'padding:8px;border-radius:4px;')
        rv.addWidget(self.formula)
        self.price_result = QLabel('')
        self.price_result.setWordWrap(True)
        self.price_result.setStyleSheet(
            'font-size:15px;font-weight:bold;color:#1a7f37;'
            'background:#eef7f0;padding:8px;border-radius:4px;')
        self.price_result.setVisible(False)
        rv.addWidget(self.price_result)
        rv.addStretch(1)
        body.addWidget(result, 1)
        root.addLayout(body, 1)
        self.show_kind('pipe')

    @staticmethod
    def _label(text, size=13, color='#333', bold=False):
        label = QLabel(text)
        label.setStyleSheet(
            'font-size:%dpx;color:%s;%s'
            % (size, color, 'font-weight:bold;' if bold else ''))
        return label

    def _spin(self, value, maximum=1e7, decimals=3, suffix=''):
        box = QDoubleSpinBox()
        box.setRange(0.001, maximum)
        box.setDecimals(decimals)
        box.setValue(value)
        box.setSuffix(suffix)
        box.setKeyboardTracking(False)
        box.setMinimumWidth(190)
        return box

    def _form(self, fields, key=None):
        page = QWidget()
        form = QFormLayout(page)
        form.setContentsMargins(0, 0, 0, 0)
        form.setHorizontalSpacing(14)
        form.setVerticalSpacing(10)
        key = key or self.kind
        self._inputs[key] = {}
        for field in fields:
            key_name, label, value, maximum, suffix = field[:5]
            box = self._spin(value, maximum, suffix=suffix)
            self._inputs[key][key_name] = box
            form.addRow(self._label(label), box)
        return page

    def _spin_allow_zero(self, value, maximum=1e7, decimals=3, suffix=''):
        box = QDoubleSpinBox()
        box.setRange(0.0, maximum)
        box.setDecimals(decimals)
        box.setValue(value)
        box.setSuffix(suffix)
        box.setKeyboardTracking(False)
        box.setMinimumWidth(190)
        return box

    def _build_pipe(self):
        self.kind = 'pipe'
        return self._form([
            ('od', '外径 D (mm)', 60.3, 10000, ' mm'),
            ('wall', '壁厚 S (mm)', 3.91, 500, ' mm'),
            ('length', '长度 L (m)', 1.0, 100000, ' m'),
            ('density', '密度 (kg/m³)', DENSITY_STEEL, 30000, ''),
        ])

    def _build_elbow(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        self.elbow_tabs = QTabWidget()
        self.elbow_tabs.setStyleSheet(
            'QTabWidget::pane{border:1px solid #d6dee7;background:#fff;}'
            'QTabBar::tab{padding:5px 18px;background:#f5f7fa;'
            'border:1px solid #d6dee7;border-bottom:none;margin-right:2px;}'
            'QTabBar::tab:selected{background:#fff;color:#1f4e79;'
            'font-weight:bold;}')
        self.elbow_tabs.addTab(
            self._form([
                ('od', '外径 D (mm)', 60.3, 10000, ' mm'),
                ('wall', '壁厚 S (mm)', 3.91, 500, ' mm'),
                ('radius', '弯曲半径 R (mm)', 90.0, 20000, ' mm'),
                ('angle', '弯曲角度 (°)', 90.0, 360, ' °'),
                ('density', '密度 (kg/m³)', DENSITY_STEEL, 30000, ''),
            ], key='elbow'), '标准弯头')
        self.elbow_tabs.addTab(self._build_large_elbow(), '大曲率弯头')
        self.elbow_tabs.currentChanged.connect(self._elbow_tab_changed)
        layout.addWidget(self.elbow_tabs)
        note = QLabel('标准弯头按中心线弧长计算；大曲率弯头可另加两端直段，'
                      '并按材质密度计算。')
        note.setStyleSheet('font-size:11px;color:#777;')
        note.setWordWrap(True)
        layout.addWidget(note)
        return page

    def _build_large_elbow(self):
        page = QWidget()
        form = QFormLayout(page)
        form.setContentsMargins(0, 6, 0, 0)
        form.setHorizontalSpacing(14)
        form.setVerticalSpacing(8)
        self.large_material = QComboBox()
        self.large_material.addItems(list(ELBOW_MATERIALS.keys()))
        self.large_material.currentIndexChanged.connect(self._large_material_changed)
        form.addRow(self._label('弯头材质'), self.large_material)
        self.large_density = QLabel('')
        self.large_density.setStyleSheet('color:#1f4e79;font-size:12px;')
        form.addRow(self._label('密度'), self.large_density)
        self._inputs['elbow_large'] = {}
        fields = [
            ('od', '外径 D (mm)', 60.3, 10000, ' mm'),
            ('wall', '壁厚 S (mm)', 3.91, 500, ' mm'),
            ('radius', '弯曲半径 R (mm)', 180.9, 30000, ' mm'),
            ('angle', '弯曲角度 (°)', 90.0, 360, ' °'),
            ('tangent1', '入口直段 L1 (mm)', 0.0, 10000, ' mm'),
            ('tangent2', '出口直段 L2 (mm)', 0.0, 10000, ' mm'),
        ]
        for key, label, value, maximum, suffix in fields:
            box = (self._spin_allow_zero(value, maximum, suffix=suffix)
                   if key.startswith('tangent') else
                   self._spin(value, maximum, suffix=suffix))
            self._inputs['elbow_large'][key] = box
            form.addRow(self._label(label), box)
        hint = QLabel('大曲率通常 R≥3D；R 较小时可按标准弯头计算。')
        hint.setStyleSheet('font-size:11px;color:#777;')
        hint.setWordWrap(True)
        form.addRow(self._label(''), hint)
        self._large_material_changed()
        return page

    def _large_material_changed(self, *_):
        name = self.large_material.currentText()
        self.large_density.setText('%g kg/m³' % ELBOW_MATERIALS.get(name, 0))

    def _elbow_tab_changed(self, *_):
        if self.kind != 'elbow':
            return
        self.mass.setText('—')
        self.volume.setText('')
        self.detail.setText('')
        self.formula.setText('')
        self.update_preview()

    def _build_tee(self):
        self.kind = 'tee'
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        self.tee_tabs = QTabWidget()
        self.tee_tabs.setStyleSheet(
            'QTabWidget::pane{border:1px solid #d6dee7;background:#fff;}'
            'QTabBar::tab{padding:5px 14px;background:#f5f7fa;'
            'border:1px solid #d6dee7;border-bottom:none;margin-right:2px;}'
            'QTabBar::tab:selected{background:#fff;color:#1f4e79;'
            'font-weight:bold;}')
        self.tee_tabs.addTab(
            self._form([
                ('od_main', '主管外径 D主 (mm)', 60.3, 10000, ' mm'),
                ('od_branch', '支管外径 D支 (mm)', 60.3, 10000, ' mm'),
                ('wall', '壁厚 S (mm)', 3.91, 500, ' mm'),
                ('main_length', '主管长度 L主 (mm)', 200.0, 100000, ' mm'),
                ('branch_length', '支管长度 L支 (mm)', 100.0, 100000, ' mm'),
                ('density', '密度 (kg/m³)', DENSITY_STEEL, 30000, ''),
            ], key='tee'), '标准三通')
        self.tee_tabs.addTab(
            self._form([
                ('od_main', '主管外径 D主 (mm)', 60.3, 10000, ' mm'),
                ('od_branch', '支管外径 D支 (mm)', 60.3, 10000, ' mm'),
                ('wall', '壁厚 S (mm)', 3.91, 500, ' mm'),
                ('main_length', '主管长度 L主 (mm)', 200.0, 100000, ' mm'),
                ('branch_height', '支管高度 H支 (mm)', 100.0, 100000, ' mm'),
                ('angle', '支管夹角 θ (°)', 45.0, 179.0, ' °'),
                ('density', '密度 (kg/m³)', DENSITY_STEEL, 30000, ''),
            ], key='tee_angle'), '斜三通')
        self.tee_tabs.addTab(
            self._form([
                ('od_main', '主管外径 D主 (mm)', 60.3, 10000, ' mm'),
                ('od_branch', '支管外径 D支 (mm)', 60.3, 10000, ' mm'),
                ('wall', '壁厚 S (mm)', 3.91, 500, ' mm'),
                ('main_length', '主管长度 L主 (mm)', 200.0, 100000, ' mm'),
                ('branch_length', '支管直段 L直 (mm)', 100.0, 100000, ' mm'),
                ('bend_radius', '支管弯曲半径 R (mm)', 90.0, 20000, ' mm'),
                ('bend_angle', '支管弯曲角度 (°)', 90.0, 360, ' °'),
                ('density', '密度 (kg/m³)', DENSITY_STEEL, 30000, ''),
            ], key='tee_bend'), '弯三通')
        self.tee_tabs.currentChanged.connect(self._tee_tab_changed)
        layout.addWidget(self.tee_tabs)
        hint = QLabel('标准三通按支管中心线长度；斜三通按支管高度/夹角换算斜长；'
                      '弯三通按直段 + 弯弧计算。公斤单价留空或 0 时不计算金额。')
        hint.setStyleSheet('font-size:11px;color:#777;')
        hint.setWordWrap(True)
        layout.addWidget(hint)
        return page

    def _tee_tab_changed(self, *_):
        if self.kind != 'tee':
            return
        self.mass.setText('—')
        self.volume.setText('')
        self.detail.setText('')
        self.formula.setText('')
        self.price_result.setText('')
        self.price_result.setVisible(False)
        self.update_preview()

    def show_kind(self, kind):
        self.kind = kind if kind in KINDS else 'pipe'
        index = {'pipe': 0, 'elbow': 1, 'tee': 2}[self.kind]
        self.stack.setCurrentIndex(index)
        self.form_title.setText(KINDS[self.kind])
        self.mass.setText('—')
        self.volume.setText('')
        self.detail.setText('')
        self.formula.setText('')
        self.price_result.setText('')
        self.price_result.setVisible(False)
        if self.kind in ('pipe', 'elbow', 'tee'):
            self.preview.setVisible(True)
            self.update_preview()
        else:
            self.preview.clear()
            self.preview.setVisible(False)

    def _large_elbow_selected(self):
        return getattr(self, 'elbow_tabs', None) is not None and \
            self.elbow_tabs.currentIndex() == 1

    def update_preview(self):
        if self.kind not in ('pipe', 'elbow', 'tee'):
            return
        if self.kind == 'pipe':
            vals = {k: b.value() for k, b in self._inputs['pipe'].items()}
            spec = build_pipe_weight_spec(vals['od'], vals['wall'],
                                          vals['length'], vals['density'])
        elif self.kind == 'elbow' and self._large_elbow_selected():
            vals = {k: b.value()
                    for k, b in self._inputs['elbow_large'].items()}
            density = ELBOW_MATERIALS.get(
                self.large_material.currentText(), DENSITY_STEEL)
            spec = build_elbow_weight_spec(
                vals['od'], vals['wall'], vals['radius'], vals['angle'],
                density, kind='大曲率弯头',
                tangent1=vals['tangent1'], tangent2=vals['tangent2'])
        elif self.kind == 'tee':
            idx = self.tee_tabs.currentIndex()
            keys = ('tee_angle' if idx == 1 else
                    'tee_bend' if idx == 2 else 'tee')
            vals = {k: b.value() for k, b in self._inputs[keys].items()}
            if idx == 1:
                spec = build_tee_weight_spec(
                    '斜三通', vals['od_main'], vals['od_branch'],
                    vals['wall'], vals['main_length'],
                    vals['branch_height'], vals['angle'],
                    vals['bend_radius'] if 'bend_radius' in vals else 0,
                    vals['density'])
            elif idx == 2:
                spec = build_tee_weight_spec(
                    '弯三通', vals['od_main'], vals['od_branch'],
                    vals['wall'], vals['main_length'],
                    vals['branch_length'], 90, vals['bend_radius'],
                    vals['density'])
            else:
                spec = build_tee_weight_spec(
                    '标准三通', vals['od_main'], vals['od_branch'],
                    vals['wall'], vals['main_length'],
                    vals['branch_length'], 90, 0, vals['density'])
        else:
            vals = {k: b.value() for k, b in self._inputs['elbow'].items()}
            spec = build_elbow_weight_spec(
                vals['od'], vals['wall'], vals['radius'], vals['angle'],
                vals['density'], kind='标准弯头')
        if spec is None:
            self.preview.clear()
            return
        pm = render_pixmap(spec)
        self.preview.setVisible(True)
        self.preview.setPixmap(pm.scaled(660, 230, Qt.KeepAspectRatio,
                                         Qt.SmoothTransformation))

    def reset(self):
        self.unit_price.setValue(0.0)
        if self.kind == 'elbow' and self._large_elbow_selected():
            self.large_material.setCurrentIndex(0)
            for key, value in dict(od=60.3, wall=3.91, radius=180.9,
                                   angle=90.0, tangent1=0.0,
                                   tangent2=0.0).items():
                self._inputs['elbow_large'][key].setValue(value)
        elif self.kind == 'tee':
            idx = self.tee_tabs.currentIndex()
            if idx == 1:
                defaults = dict(od_main=60.3, od_branch=60.3, wall=3.91,
                                main_length=200.0, branch_height=100.0,
                                angle=45.0, density=DENSITY_STEEL)
                key = 'tee_angle'
            elif idx == 2:
                defaults = dict(od_main=60.3, od_branch=60.3, wall=3.91,
                                main_length=200.0, branch_length=100.0,
                                bend_radius=90.0, bend_angle=90.0,
                                density=DENSITY_STEEL)
                key = 'tee_bend'
            else:
                defaults = dict(od_main=60.3, od_branch=60.3, wall=3.91,
                                main_length=200.0, branch_length=100.0,
                                density=DENSITY_STEEL)
                key = 'tee'
            for k, value in defaults.items():
                self._inputs[key][k].setValue(value)
        else:
            defaults = {
                'pipe': dict(od=60.3, wall=3.91, length=1.0,
                             density=DENSITY_STEEL),
                'elbow': dict(od=60.3, wall=3.91, radius=90.0, angle=90.0,
                              density=DENSITY_STEEL),
                'tee': dict(od_main=60.3, od_branch=60.3, wall=3.91,
                            main_length=200.0, branch_length=100.0,
                            density=DENSITY_STEEL),
            }
            for key, value in defaults[self.kind].items():
                self._inputs[self.kind][key].setValue(value)
        self.show_kind(self.kind)

    def _with_price(self, res):
        """公共公斤单价：新增重量子页统一调用，价格随质量自动计算。"""
        price = self.unit_price.value()
        res['price'] = res['mass'] * price if price > 0 else None
        return res

    def calculate(self):
        try:
            if self.kind == 'pipe':
                values = {key: box.value()
                          for key, box in self._inputs['pipe'].items()}
                res = self._with_price(pipe_weight(
                    values['od'], values['wall'], values['length'],
                    values['density']))
            elif self.kind == 'elbow' and self._large_elbow_selected():
                values = {key: box.value()
                          for key, box in self._inputs['elbow_large'].items()}
                density = ELBOW_MATERIALS.get(
                    self.large_material.currentText(), DENSITY_STEEL)
                res = self._with_price(large_radius_elbow_weight(
                    values['od'], values['wall'], values['radius'],
                    values['angle'], values['tangent1'],
                    values['tangent2'], density))
                res['detail'] = ('材质：%s（%g kg/m³）\n%s'
                                  % (self.large_material.currentText(),
                                     density, res['detail']))
            elif self.kind == 'elbow':
                values = {key: box.value()
                          for key, box in self._inputs['elbow'].items()}
                res = self._with_price(elbow_weight(**values))
            elif self.kind == 'tee':
                idx = self.tee_tabs.currentIndex()
                keys = ('tee_angle' if idx == 1 else
                        'tee_bend' if idx == 2 else 'tee')
                values = {key: box.value()
                          for key, box in self._inputs[keys].items()}
                price = self.unit_price.value()
                if idx == 1:
                    res = angle_tee_weight(
                        values['od_main'], values['od_branch'],
                        values['wall'], values['main_length'],
                        values['branch_height'], values['angle'],
                        values['density'], price)
                elif idx == 2:
                    res = bend_tee_weight(
                        values['od_main'], values['od_branch'],
                        values['wall'], values['main_length'],
                        values['branch_length'], values['bend_radius'],
                        values['bend_angle'], values['density'], price)
                else:
                    res = tee_weight(
                        values['od_main'], values['od_branch'],
                        values['wall'], values['main_length'],
                        values['branch_length'], values['density'], price)
            else:
                values = {key: box.value()
                          for key, box in self._inputs['tee'].items()}
                res = tee_weight(**values)
        except ValueError as exc:
            self.mass.setText('参数错误')
            self.volume.setText('')
            self.detail.setText(str(exc))
            self.formula.setText('')
            self.price_result.setText('')
            self.price_result.setVisible(False)
            return None
        self.mass.setText('%.2f' % res['mass'])
        self.volume.setText('体积：%.6f m³' % res['volume'])
        self.detail.setText(res['detail'])
        self.formula.setText(res['formula'])
        if self.kind in ('pipe', 'elbow', 'tee') and 'price' in res:
            if res.get('price') is None:
                self.price_result.setText('采购价格：未填写单价')
                self.price_result.setStyleSheet(
                    'font-size:15px;color:#777;background:#f2f4f7;'
                    'padding:8px;border-radius:4px;')
            else:
                self.price_result.setText(
                    '采购价格：%.2f 元（单价 %.2f 元/kg）'
                    % (res['price'], self.unit_price.value()))
                self.price_result.setStyleSheet(
                    'font-size:15px;font-weight:bold;color:#1a7f37;'
                    'background:#eef7f0;padding:8px;border-radius:4px;')
            self.price_result.setVisible(True)
        if self.kind in ('pipe', 'elbow', 'tee'):
            self.update_preview()
        return res
