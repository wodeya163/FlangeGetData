# -*- coding: utf-8 -*-
"""螺栓连接校核页：预紧、摩擦、剪切、承压与安全系数。"""

from PyQt5.QtWidgets import (QComboBox, QDoubleSpinBox, QFormLayout,
                             QFrame, QHBoxLayout, QLabel, QPushButton,
                             QSpinBox, QVBoxLayout, QWidget)

SCENARIOS = {
    '法兰盘密封': (8, '喷砂-钢', 0),
    '支架连接': (4, '手工除锈-钢', 0),
    '盖板固定': (4, '轧制表面-钢', 0),
    '螺纹盲孔': (1, '涂防锈漆-钢', 1),
}

from ui.bolt_schematic import BoltSchematic

from core.bolt_calc import (BOLT_MATERIALS, BOLT_SIZES,
                            FRICTION_COEFFICIENTS, PLATE_MATERIALS,
                            calculate_bolt_joint, calculate_screw_joint)


class BoltJointPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 22, 28, 22)
        root.setSpacing(14)
        title = QLabel('螺栓连接校核')
        title.setStyleSheet('font-size:22px;font-weight:bold;color:#163a5f;')
        sub = QLabel('按预紧力、摩擦传力、螺栓抗拉/抗剪、板承压/撕裂计算，'
                     '输出安全系数和失效模式。')
        sub.setStyleSheet('color:#666;font-size:12px;')
        root.addWidget(title)
        root.addWidget(sub)

        body = QHBoxLayout()
        body.setSpacing(18)
        left = QFrame()
        left.setFixedWidth(520)
        left.setObjectName('bolt_input')
        left.setStyleSheet('#bolt_input{background:#fff;'
                           'border:1px solid #c9d2dc;border-radius:6px;}')
        lv = QVBoxLayout(left)
        lv.setContentsMargins(18, 16, 18, 16)
        lv.setSpacing(12)
        lv.addWidget(self._label('连接参数', 16, '#1f4e79', True))
        form = QFormLayout()
        form.setHorizontalSpacing(14)
        form.setVerticalSpacing(8)
        self.scene_box = self._combo(['自定义'] + list(SCENARIOS.keys()))
        self.scene_box.currentIndexChanged.connect(self._scene_changed)
        self.mode_box = self._combo(['螺栓连接', '螺纹盲孔'])
        self.mode_box.currentIndexChanged.connect(self._mode_changed)
        self.size_box = self._combo(list(BOLT_SIZES.keys()))
        self.grade_box = self._combo(list(BOLT_MATERIALS.keys()))
        self.plate_box = self._combo(list(PLATE_MATERIALS.keys()))
        self.friction_box = self._combo(list(FRICTION_COEFFICIENTS.keys()))
        self.thickness = self._spin(8.0, 500.0, ' mm')
        self.fx = self._spin(1000.0, 1e7, ' N')
        self.fy = self._spin(2000.0, 1e7, ' N')
        self.moment = self._spin(0.0, 1e8, ' N·mm')
        self.n_bolts = QSpinBox()
        self.n_bolts.setRange(1, 64)
        self.n_bolts.setValue(4)
        self.n_surfaces = QSpinBox()
        self.n_surfaces.setRange(1, 4)
        self.n_surfaces.setValue(1)
        self.edge = self._spin(20.0, 5000.0, ' mm')
        self.engagement = self._spin(0.0, 500.0, ' mm')
        for box, name in ((self.size_box, 'M12'), (self.grade_box, '8.8'),
                          (self.plate_box, 'Q235')):
            if box.findText(name) >= 0:
                box.setCurrentText(name)
        for label, widget in [
            ('常用场景', self.scene_box),
            ('连接类型', self.mode_box),
            ('螺栓规格', self.size_box), ('强度等级', self.grade_box),
            ('板材料', self.plate_box), ('摩擦面', self.friction_box),
            ('板厚', self.thickness), ('轴向力 Fy', self.fy),
            ('横向力 Fx', self.fx), ('偏心弯矩 M', self.moment),
            ('螺栓数量', self.n_bolts), ('摩擦面数', self.n_surfaces),
            ('边距', self.edge),
            ('螺纹旋合深度（0=自动）', self.engagement),
        ]:
            form.addRow(self._label(label), widget)
        lv.addLayout(form)
        row = QHBoxLayout()
        btn = QPushButton('校核')
        btn.setProperty('class', 'b-print')
        btn.setMinimumHeight(34)
        btn.setMinimumWidth(100)
        btn.clicked.connect(self.calculate)
        row.addWidget(btn)
        row.addStretch(1)
        lv.addLayout(row)
        self.scene_hint = QLabel('')
        self.scene_hint.setWordWrap(True)
        self.scene_hint.setStyleSheet('font-size:11px;color:#666;')
        lv.addWidget(self.scene_hint)
        lv.addStretch(1)
        body.addWidget(left)

        right = QFrame()
        right.setObjectName('bolt_result')
        right.setStyleSheet('#bolt_result{background:#f5f8fb;'
                            'border:1px solid #c9d2dc;border-radius:6px;}')
        rv = QVBoxLayout(right)
        rv.setContentsMargins(24, 20, 24, 20)
        rv.setSpacing(9)
        rv.addWidget(self._label('校核结果', 16, '#1f4e79', True))
        self.status = QLabel('—')
        self.status.setStyleSheet(
            'font-size:34px;font-weight:bold;color:#163a5f;')
        rv.addWidget(self.status)
        self.safety = QLabel('')
        self.safety.setStyleSheet('font-size:15px;font-weight:bold;')
        rv.addWidget(self.safety)
        self.schematic = BoltSchematic()
        rv.addWidget(self.schematic)
        self.detail = QLabel('')
        self.detail.setWordWrap(True)
        self.detail.setStyleSheet('font-size:13px;color:#333;')
        rv.addWidget(self.detail)
        self.modes = QLabel('')
        self.modes.setWordWrap(True)
        self.modes.setStyleSheet('font-size:12px;color:#555;')
        rv.addWidget(self.modes)
        self.warn = QLabel('')
        self.warn.setWordWrap(True)
        self.warn.setStyleSheet('font-size:12px;color:#a15c00;')
        rv.addWidget(self.warn)
        rv.addStretch(1)
        body.addWidget(right, 1)
        root.addLayout(body, 1)
        self._mode_changed()

    @staticmethod
    def _label(text, size=13, color='#333', bold=False):
        label = QLabel(text)
        label.setStyleSheet('font-size:%dpx;color:%s;%s'
                            % (size, color, 'font-weight:bold;' if bold else ''))
        return label

    @staticmethod
    def _combo(items):
        box = QComboBox()
        box.addItems(items)
        return box

    def _spin(self, value, maximum, suffix):
        box = QDoubleSpinBox()
        box.setRange(0.0, maximum)
        box.setDecimals(3)
        box.setValue(value)
        box.setSuffix(suffix)
        box.setKeyboardTracking(False)
        box.setMinimumWidth(190)
        return box

    def _scene_changed(self):
        name = self.scene_box.currentText()
        if name not in SCENARIOS:
            return
        n, friction, mode = SCENARIOS[name]
        self.mode_box.setCurrentIndex(mode)
        self.n_bolts.setValue(n)
        if self.friction_box.findText(friction) >= 0:
            self.friction_box.setCurrentText(friction)

    def _mode_changed(self):
        screw = self.mode_box.currentIndex() == 1
        self.friction_box.setEnabled(not screw)
        self.n_surfaces.setEnabled(not screw)
        self.engagement.setEnabled(screw)
        if screw:
            self.n_bolts.setValue(1)
            self.n_bolts.setEnabled(False)
        else:
            self.n_bolts.setEnabled(True)
        self.scene_hint.setText(
            '螺纹盲孔：螺钉拧入零件螺纹孔，按螺纹啮合、螺钉强度、'
            '板承压/撕裂校核。' if screw else
            '螺栓连接：按预紧、摩擦传力、螺栓强度、板承压/撕裂校核。')

    def calculate(self):
        try:
            if self.mode_box.currentIndex() == 1:
                res = calculate_screw_joint(
                    self.size_box.currentText(), self.grade_box.currentText(),
                    self.plate_box.currentText(), self.thickness.value(),
                    self.fx.value(), self.fy.value(), self.moment.value(),
                    self.n_bolts.value(), self.edge.value(),
                    self.engagement.value() or None)
            else:
                res = calculate_bolt_joint(
                    self.size_box.currentText(), self.grade_box.currentText(),
                    self.plate_box.currentText(), self.thickness.value(),
                    self.friction_box.currentText(), self.fx.value(),
                    self.fy.value(), self.moment.value(),
                    self.n_bolts.value(), self.n_surfaces.value(),
                    self.edge.value(), None)
        except Exception as exc:
            self.status.setText('参数错误')
            self.safety.setText('')
            self.detail.setText(str(exc))
            self.modes.setText('')
            self.warn.setText('')
            return None
        self.schematic.set_data(self.n_bolts.value(),
                                self.mode_box.currentIndex() == 1,
                                self.fx.value(), self.fy.value(),
                                self.moment.value())
        ok = res.safety_factor >= 1.0
        self.status.setText('通过' if ok else '不通过')
        self.status.setStyleSheet(
            'font-size:34px;font-weight:bold;color:%s;'
            % ('#1a7f37' if ok else '#c0392b'))
        self.safety.setText('最小安全系数 %.2f' % res.safety_factor)
        if self.mode_box.currentIndex() == 1:
            self.detail.setText(
                '预紧力 %.0f N　螺纹拧出力 %.0f N\n'
                '螺钉抗拉 %.0f N\n板承压 %.0f N　板撕裂 %.0f N'
                % (res.preload, res.thread_stripping_force,
                   res.screw_tension_capacity, res.plate_bearing_capacity,
                   res.plate_tearout_capacity))
            sf = res.details.get('safety_factors', {})
            fmap = {'screw_yield': '螺钉屈服', 'thread_stripping': '螺纹拧出',
                    'plate_bearing': '板承压', 'plate_tearout': '板撕裂'}
            self.modes.setText(
                '失效模式：%s\n螺纹拧出 %.2f　螺钉屈服 %.2f\n'
                '板承压 %.2f　板撕裂 %.2f'
                % (fmap.get(res.failure_mode, res.failure_mode),
                   sf.get('thread_stripping', 0),
                   sf.get('screw_yield', 0), sf.get('plate_bearing', 0),
                   sf.get('plate_tearout', 0)))
        else:
            d = res.details
            self.detail.setText(
                '预紧力 %.0f N　摩擦承载力 %.0f N\n'
                '螺栓抗拉 %.0f N　抗剪 %.0f N\n'
                '板承压 %.0f N　板撕裂 %.0f N'
                % (res.preload, res.friction_force,
                   res.bolt_tension_capacity, res.bolt_shear_capacity,
                   res.plate_bearing_capacity, res.plate_tearout_capacity))
            sf = d.get('safety_factors', {})
            fmap = {'friction': '摩擦', 'bolt_yield': '螺栓屈服',
                    'separation': '分离', 'bolt_shear': '螺栓剪切',
                    'plate_bearing': '板承压', 'plate_tearout': '板撕裂'}
            self.modes.setText(
                '失效模式：%s\n摩擦 %.2f　螺栓屈服 %.2f　分离 %.2f\n'
                '螺栓剪切 %.2f　板承压 %.2f　板撕裂 %.2f'
                % (fmap.get(res.failure_mode, res.failure_mode),
                   sf.get('friction', 0),
                   sf.get('bolt_yield', 0), sf.get('separation', 0),
                   sf.get('bolt_shear', 0), sf.get('plate_bearing', 0),
                   sf.get('plate_tearout', 0)))
        warns = res.details.get('warnings') or []
        self.warn.setText('\n'.join(warns) if warns else '无布局警告')
        return res
