# -*- coding: utf-8 -*-
"""螺栓拧紧力矩选型页。"""

from PyQt5.QtWidgets import (QCheckBox, QComboBox, QDialog,
                             QDoubleSpinBox, QFormLayout, QFrame,
                             QHBoxLayout, QLabel, QMessageBox, QPushButton,
                             QTableWidget, QTableWidgetItem, QTabWidget,
                             QVBoxLayout, QWidget)

from core.torque import (TYPES, grades, materials, scenario, sizes,
                         torque, wrench_range)
from core.torque_data import (FINE_THREAD_PITCH, SCENARIOS,
                             TORQUE_COEFFICIENT, calc_fine_thread_torque)
from core import torque_store


class TorquePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 22, 28, 22)
        root.setSpacing(14)
        title = QLabel('螺栓拧紧力矩工具')
        title.setStyleSheet('font-size:22px;font-weight:bold;color:#163a5f;')
        sub = QLabel('按螺栓类型、规格、强度等级和装配场景查询推荐力矩；'
                     '单位 N·m。')
        sub.setStyleSheet('color:#666;font-size:12px;')
        root.addWidget(title)
        root.addWidget(sub)

        self.query_page = QWidget()
        body = QHBoxLayout(self.query_page)
        body.setSpacing(18)
        left = QFrame()
        left.setFixedWidth(520)
        left.setObjectName('torque_input')
        left.setStyleSheet('#torque_input{background:#fff;'
                           'border:1px solid #c9d2dc;border-radius:6px;}')
        lv = QVBoxLayout(left)
        lv.setContentsMargins(18, 16, 18, 16)
        lv.setSpacing(12)
        lv.addWidget(self._label('选型参数', 16, '#1f4e79', True))
        form = QFormLayout()
        form.setHorizontalSpacing(14)
        form.setVerticalSpacing(10)
        self.type_box = QComboBox()
        for key, name in TYPES.items():
            self.type_box.addItem(name, key)
        self.type_box.currentIndexChanged.connect(self._type_changed)
        form.addRow(self._label('螺栓类型'), self.type_box)
        self.size_box = QComboBox()
        self.size_box.currentIndexChanged.connect(self._size_changed)
        form.addRow(self._label('规格'), self.size_box)
        self.grade_box = QComboBox()
        form.addRow(self._label('强度等级'), self.grade_box)
        self.material_box = QComboBox()
        self.material_row = self._label('材料')
        form.addRow(self.material_row, self.material_box)
        self.scenario_box = QComboBox()
        self.scenario_box.addItems(list(SCENARIOS.keys()))
        form.addRow(self._label('装配场景'), self.scenario_box)
        self.k_box = QComboBox()
        for name, value in TORQUE_COEFFICIENT.items():
            self.k_box.addItem(name, value)
        form.addRow(self._label('摩擦系数 K'), self.k_box)
        self.fine = QCheckBox('细牙螺纹')
        form.addRow(self._label('螺纹'), self.fine)
        self.unit_box = QComboBox()
        for name, factor in [('N·m', 1.0), ('kgf·m', 0.1019716),
                             ('lbf·ft', 0.737562)]:
            self.unit_box.addItem(name, factor)
        self.unit_box.currentIndexChanged.connect(self.calculate)
        form.addRow(self._label('显示单位'), self.unit_box)
        lv.addLayout(form)
        row = QHBoxLayout()
        self.calc_btn = QPushButton('查询力矩')
        self.calc_btn.setProperty('class', 'b-print')
        self.calc_btn.setMinimumHeight(34)
        self.calc_btn.setMinimumWidth(120)
        self.calc_btn.clicked.connect(self.calculate)
        row.addWidget(self.calc_btn)
        row.addStretch(1)
        lv.addLayout(row)
        lv.addStretch(1)
        body.addWidget(left)

        right = QFrame()
        right.setObjectName('torque_result')
        right.setStyleSheet('#torque_result{background:#f5f8fb;'
                            'border:1px solid #c9d2dc;border-radius:6px;}')
        rv = QVBoxLayout(right)
        rv.setContentsMargins(24, 20, 24, 20)
        rv.setSpacing(10)
        rv.addWidget(self._label('推荐拧紧力矩', 16, '#1f4e79', True))
        self.recommended = QLabel('—')
        self.recommended.setStyleSheet(
            'font-size:40px;font-weight:bold;color:#163a5f;')
        rv.addWidget(self.recommended)
        self.unit = QLabel('N·m')
        self.unit.setStyleSheet('font-size:13px;color:#777;')
        rv.addWidget(self.unit)
        self.range = QLabel('')
        self.range.setStyleSheet('font-size:15px;color:#333;')
        rv.addWidget(self.range)
        self.detail = QLabel('')
        self.detail.setWordWrap(True)
        self.detail.setStyleSheet('font-size:13px;color:#555;')
        rv.addWidget(self.detail)
        self.wrench = QLabel('')
        self.wrench.setWordWrap(True)
        self.wrench.setStyleSheet(
            'font-size:13px;color:#1f4e79;background:#eef4fa;'
            'padding:8px;border-radius:4px;')
        rv.addWidget(self.wrench)
        self.preload = QLabel('')
        self.preload.setWordWrap(True)
        self.preload.setStyleSheet('font-size:12px;color:#555;')
        rv.addWidget(self.preload)
        self.formula = QLabel('估算式：T = K·F·d，F ≈ 0.65·σy·As；')
        self.formula.setWordWrap(True)
        self.formula.setStyleSheet('font-size:11px;color:#777;')
        rv.addWidget(self.formula)
        rv.addStretch(1)
        body.addWidget(right, 1)
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(
            'QTabWidget::pane{border:1px solid #c9d2dc;background:#fff;}'
            'QTabBar::tab{padding:6px 16px;background:#f5f7fa;'
            'border:1px solid #c9d2dc;border-bottom:none;margin-right:2px;}'
            'QTabBar::tab:selected{background:#fff;color:#1f4e79;font-weight:bold;}')
        self.tabs.addTab(self.query_page, '力矩查询')
        self.tabs.addTab(self._build_formula(), '公式说明')
        self.tabs.addTab(self._build_records(), '个人记录')
        root.addWidget(self.tabs, 1)
        self._refresh_options()
        if self.size_box.findText('M12') >= 0:
            self.size_box.setCurrentText('M12')
        if self.grade_box.findText('8.8') >= 0:
            self.grade_box.setCurrentText('8.8')
        self.calculate()

    @staticmethod
    def _label(text, size=13, color='#333', bold=False):
        label = QLabel(text)
        label.setStyleSheet('font-size:%dpx;color:%s;%s'
                            % (size, color, 'font-weight:bold;' if bold else ''))
        return label

    def _current_type(self):
        return self.type_box.currentData()

    def _refresh_options(self):
        bolt_type = self._current_type()
        self.size_box.blockSignals(True)
        self.size_box.clear()
        self.size_box.addItems(sizes(bolt_type))
        self.size_box.blockSignals(False)
        self._size_changed()

    def _size_changed(self):
        bolt_type = self._current_type()
        size = self.size_box.currentText()
        self.grade_box.clear()
        self.grade_box.addItems(grades(bolt_type, size))
        if self.grade_box.findText('8.8') >= 0:
            self.grade_box.setCurrentText('8.8')
        self.material_box.clear()
        mats = materials(bolt_type, size)
        self.material_box.addItems(mats)
        is_tap = bolt_type == 'self_tap'
        self.fine.setVisible(not is_tap)
        self.fine.setEnabled(not is_tap)
        self.grade_box.setEnabled(not is_tap)
        self.material_box.setVisible(is_tap)
        self.material_row.setVisible(is_tap)

    def _type_changed(self):
        self._refresh_options()

    def calculate(self):
        bolt_type = self._current_type()
        size = self.size_box.currentText()
        grade = self.grade_box.currentText()
        material = self.material_box.currentText()
        name = self.scenario_box.currentText()
        fine = self.fine.isChecked() and bolt_type != 'self_tap'
        if fine:
            diameter = size.lstrip('M')
            candidates = [k for k in FINE_THREAD_PITCH
                          if k.startswith('M%s×' % diameter)]
            raw = (calc_fine_thread_torque(grade, candidates[0], bolt_type)
                   if candidates else None)
        else:
            raw = torque(bolt_type, size, grade, material)
        if raw is None:
            self.recommended.setText('无数据')
            self.range.setText('')
            self.detail.setText('当前类型/规格/等级组合没有标准力矩值。')
            self.wrench.setText('')
            return None
        res = scenario(raw, name)
        if res is None:
            self.recommended.setText('无数据')
            return None
        vmin, vrec, vmax, note = res
        k = self.k_box.currentData() or 0.2
        factor = k / 0.2
        vmin, vrec, vmax = (round(vmin * factor, 1),
                            round(vrec * factor, 1),
                            round(vmax * factor, 1))
        unit_factor = self.unit_box.currentData() or 1.0
        unit_name = self.unit_box.currentText()
        self.recommended.setText('%.2f' % (vrec * unit_factor))
        self.unit.setText(unit_name)
        self.range.setText('范围：%.2f – %.2f %s'
                           % (vmin * unit_factor, vmax * unit_factor, unit_name))
        self.detail.setText(
            '类型：%s　规格：%s%s　等级：%s\n场景：%s　%s'
            % (TYPES.get(bolt_type, ''), size,
               ' 细牙' if fine else '', grade or material, name,
               note + '；K=%.2f' % k))
        self.wrench.setText('扳手量程建议：%.1f – %.1f %s'
                            % (max(0.1, vrec * 0.6) * unit_factor,
                               vrec * 1.5 * unit_factor, unit_name))
        d_mm = 0.0
        try:
            d_mm = float(size.lstrip('M').split('×')[0])
        except Exception:
            pass
        if d_mm > 0:
            preload_n = vrec / (k * d_mm / 1000.0)
            self.preload.setText('按 K=%.2f 估算预紧力约 %.0f N' % (k, preload_n))
        else:
            self.preload.setText('')
        self.last_result = {
            'thread_type': bolt_type, 'spec': size,
            'grade_material': grade or material, 'source': 'table',
            't_min': vmin, 't_rec': vrec, 't_max': vmax,
            'scenario': name, 'note': '细牙' if fine else ''}
        return vrec

    def _build_formula(self):
        page = QWidget()
        root = QVBoxLayout(page)
        root.setContentsMargins(18, 14, 18, 14)
        root.setSpacing(10)
        text = QLabel(
            '<h3 style="color:#1f4e79">拧紧力矩公式</h3>'
            '<p><b>T = K · F · d</b></p>'
            '<p>T：拧紧力矩（N·m）　K：综合摩擦系数　F：预紧力（N）　'
            'd：螺纹公称直径（m）</p>'
            '<p><b>F ≈ 0.65 · σy · As</b>（约 65% 屈服预紧）</p>'
            '<p>As = π/4 · ((d2 + d3) / 2)²，d2/d3 为螺纹中径/小径。</p>'
            '<p>K 参考：干燥钢对钢 0.20；润滑 0.15；生锈/镀锌 0.25；'
            '不锈钢 0.25。细牙螺纹按应力面积比修正。</p>'
            '<p style="color:#667085">查表值为标准/经验推荐，实际装配还应考虑'
            '螺纹润滑、工具校准、被连接件刚度和重复使用次数。</p>')
        text.setWordWrap(True)
        text.setStyleSheet('font-size:13px;color:#333;')
        root.addWidget(text)
        row = QHBoxLayout()
        self.calc_f = QDoubleSpinBox()
        self.calc_f.setRange(1, 1e7)
        self.calc_f.setValue(20000)
        self.calc_f.setSuffix(' N')
        self.calc_d = QDoubleSpinBox()
        self.calc_d.setRange(1, 500)
        self.calc_d.setValue(12)
        self.calc_d.setSuffix(' mm')
        self.calc_k = QDoubleSpinBox()
        self.calc_k.setRange(0.05, 0.5)
        self.calc_k.setSingleStep(0.01)
        self.calc_k.setValue(0.2)
        for lab, w in [('预紧力 F', self.calc_f), ('直径 d', self.calc_d),
                       ('摩擦系数 K', self.calc_k)]:
            row.addWidget(QLabel(lab))
            row.addWidget(w)
        btn = QPushButton('计算')
        btn.clicked.connect(self._formula_calc)
        row.addWidget(btn)
        row.addStretch(1)
        root.addLayout(row)
        self.formula_result = QLabel('')
        self.formula_result.setStyleSheet(
            'font-size:18px;font-weight:bold;color:#163a5f;')
        root.addWidget(self.formula_result)
        root.addStretch(1)
        self._formula_calc()
        return page

    def _formula_calc(self):
        t = self.calc_k.value() * self.calc_f.value() * self.calc_d.value() / 1000.0
        self.formula_result.setText('T = %.1f N·m' % t)
        return t

    def _build_records(self):
        page = QWidget()
        root = QVBoxLayout(page)
        root.setContentsMargins(0, 10, 0, 0)
        self.records = QTableWidget(0, 7)
        self.records.setHorizontalHeaderLabels(
            ['时间', '类型', '规格', '等级/材料', '推荐力矩', '场景', '备注'])
        self.records.verticalHeader().setVisible(False)
        self.records.setEditTriggers(QTableWidget.NoEditTriggers)
        self.records.setSelectionBehavior(QTableWidget.SelectRows)
        self.records.horizontalHeader().setStretchLastSection(True)
        self.records.setStyleSheet(
            'QTableWidget{background:#fff;border:1px solid #d6dee7;'
            'font-size:12px;} QHeaderView::section{background:#eef3f8;'
            'padding:4px;font-weight:bold;}')
        root.addWidget(self.records, 1)
        row = QHBoxLayout()
        for text, slot in [('保存当前结果', self._save_record),
                           ('删除选中', self._delete_record),
                           ('刷新', self._refresh_records)]:
            btn = QPushButton(text)
            btn.setMinimumHeight(30)
            btn.clicked.connect(slot)
            row.addWidget(btn)
        row.addStretch(1)
        root.addLayout(row)
        self._refresh_records()
        return page

    def _refresh_records(self):
        rows = torque_store.list_records()
        self.records.setRowCount(len(rows))
        for i, r in enumerate(rows):
            vals = [r.get('created_at', ''), r.get('thread_type', ''),
                    r.get('spec', ''), r.get('grade_material', ''),
                    '%.1f N·m' % (r.get('t_rec') or 0),
                    r.get('scenario', ''), r.get('note', '')]
            for j, value in enumerate(vals):
                item = QTableWidgetItem(str(value))
                if j == 0:
                    item.setData(256, r.get('id'))
                self.records.setItem(i, j, item)
        self.records.resizeColumnsToContents()

    def _save_record(self):
        if not getattr(self, 'last_result', None):
            self.calculate()
        if not getattr(self, 'last_result', None):
            QMessageBox.information(self, '提示', '当前没有有效结果')
            return
        d = self.last_result
        torque_store.add_record(
            d['thread_type'], d['spec'], d['grade_material'], 'table',
            d['t_rec'], d['t_min'], d['t_max'], d['scenario'], d['note'])
        self._refresh_records()
        self.tabs.setCurrentIndex(2)

    def _delete_record(self):
        row = self.records.currentRow()
        if row < 0:
            return
        rec_id = self.records.item(row, 0).data(256)
        torque_store.delete_record(rec_id)
        self._refresh_records()

