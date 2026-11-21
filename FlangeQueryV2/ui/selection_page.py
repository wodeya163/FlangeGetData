# -*- coding: utf-8 -*-
"""选型工具页：左侧树由主窗口提供，本页负责中间输入/右侧结果。"""

import os
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QComboBox, QDoubleSpinBox,
                             QFormLayout, QFrame, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QScrollArea, QTableWidget,
                             QTableWidgetItem,
                             QStackedWidget, QVBoxLayout, QWidget)

_COMPAT = os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), 'compat')
if _COMPAT not in sys.path:
    sys.path.insert(0, _COMPAT)
from vendor.tolerance.ui.main_window import MainWindow as ToleranceWindow

from core.unit_convert import (category_names, convert, format_value,
                               formula, unit_labels)
from core.unit_data import format_dms, parse_dms
from ui.key_page import KeyPage
from ui.bolt_page import BoltJointPage
from ui.bearing_page import BearingPage
from ui.gear_page import GearPage
from ui.spring_page import SpringPage
from ui.torque_page import TorquePage

TOOLS = [
    ('gear', '齿轮参数',
     '齿轮几何参数、跨棒距、齿厚、强度与 STP 相关计算。'),
    ('unit', '单位换算',
     '21 类工程单位：长度/面积/体积/质量/力/压力/扭矩/角度/密度/温度/'
     '热学/粘度/转速/速度/流量/功率/能量/硬度。'),
    ('spring', '弹簧设计',
     '弹簧刚度、应力、圈数、变形与尺寸校核。'),
    ('tolerance', '公差',
     'IT 公差、极限偏差、形位公差与表面粗糙度查询。'),
    ('key', '键联接选型',
     '平键/半圆键尺寸、键长与挤压/剪切校核。'),
    ('bolt', '螺栓连接校核',
     '螺栓组受力、预紧、强度与疲劳校核。'),
    ('torque', '螺栓拧紧力矩',
     '预紧力、拧紧力矩、摩擦系数与扭矩换算。'),
    ('bearing', '轴承选型',
     '轴承寿命、当量动载荷、转速与选型校核。'),
]

TOOL_INFO = {key: (name, desc) for key, name, desc in TOOLS}


class SelectionPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('selection_page')
        self.kind = 'unit'
        self._building = False

        root = QVBoxLayout(self)
        root.setContentsMargins(28, 22, 28, 22)
        root.setSpacing(14)
        title = QLabel('选型工具')
        title.setStyleSheet('font-size:22px;font-weight:bold;color:#163a5f;')
        self.subtitle = QLabel('')
        self.subtitle.setStyleSheet('color:#666;font-size:12px;')
        root.addWidget(title)
        root.addWidget(self.subtitle)

        self.body_widget = QWidget()
        body = QHBoxLayout(self.body_widget)
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(18)
        left = QFrame()
        left.setFixedWidth(520)
        left.setStyleSheet(
            '#sel_input{background:#fff;border:1px solid #c9d2dc;'
            'border-radius:6px;}')
        left.setObjectName('sel_input')
        lv = QVBoxLayout(left)
        lv.setContentsMargins(18, 16, 18, 16)
        lv.setSpacing(12)
        self.form_title = QLabel('单位换算工具')
        self.form_title.setStyleSheet(
            'font-size:16px;font-weight:bold;color:#1f4e79;')
        lv.addWidget(self.form_title)
        self.stack = QStackedWidget()
        self.stack.addWidget(self._build_unit())
        self.stack.addWidget(self._build_placeholder())
        lv.addWidget(self.stack)
        self.calc_btn = QPushButton('换算')
        self.calc_btn.setProperty('class', 'b-print')
        self.calc_btn.setMinimumHeight(34)
        self.calc_btn.setMinimumWidth(100)
        self.calc_btn.clicked.connect(self.calculate)
        self.swap_btn = QPushButton('交换')
        self.swap_btn.setProperty('class', 'b-print')
        self.swap_btn.setMinimumHeight(34)
        self.swap_btn.clicked.connect(self._swap)
        self.copy_btn = QPushButton('复制结果')
        self.copy_btn.setMinimumHeight(34)
        self.copy_btn.setStyleSheet('background:#fff;border:1px solid #c9d2dc;'
                                    'border-radius:4px;padding:4px 12px;')
        self.copy_btn.clicked.connect(self._copy_result)
        btnrow = QHBoxLayout()
        btnrow.addWidget(self.calc_btn)
        btnrow.addWidget(self.swap_btn)
        btnrow.addWidget(self.copy_btn)
        btnrow.addStretch(1)
        lv.addLayout(btnrow)
        body.addWidget(left)

        result = QFrame()
        result.setObjectName('sel_result')
        result.setStyleSheet(
            '#sel_result{background:#f5f8fb;border:1px solid #c9d2dc;'
            'border-radius:6px;}')
        rv = QVBoxLayout(result)
        rv.setContentsMargins(24, 20, 24, 20)
        rv.setSpacing(10)
        self.result_title = self._label('换算结果', 16, '#1f4e79', True)
        rv.addWidget(self.result_title)
        self.value = QLabel('—')
        self.value.setStyleSheet(
            'font-size:40px;font-weight:bold;color:#163a5f;')
        rv.addWidget(self.value)
        self.value_unit = QLabel('')
        self.value_unit.setStyleSheet('color:#777;font-size:13px;')
        rv.addWidget(self.value_unit)
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
        self.all_table = QTableWidget(0, 2)
        self.all_table.setHorizontalHeaderLabels(['单位', '数值'])
        self.all_table.verticalHeader().setVisible(False)
        self.all_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.all_table.setSelectionMode(QTableWidget.NoSelection)
        self.all_table.horizontalHeader().setStretchLastSection(True)
        self.all_table.setMinimumHeight(220)
        self.all_table.setStyleSheet('QTableWidget{background:#fff;'
                                     'border:1px solid #d6dee7;'
                                     'font-size:12px;}'
                                     'QHeaderView::section{background:#eef3f8;'
                                     'padding:4px;font-weight:bold;}')
        self.all_table.cellClicked.connect(self._pick_all)
        rv.addWidget(self.all_table, 1)
        body.addWidget(result, 1)
        root.addWidget(self.body_widget, 1)
        self.vendor_host = QWidget()
        self.vendor_layout = QVBoxLayout(self.vendor_host)
        self.vendor_layout.setContentsMargins(0, 0, 0, 0)
        self.vendor_host.hide()
        self.tolerance_window = None
        root.addWidget(self.vendor_host, 1)
        self.key_page = KeyPage()
        self.key_page.hide()
        root.addWidget(self.key_page, 1)
        self.torque_page = TorquePage()
        self.torque_page.hide()
        root.addWidget(self.torque_page, 1)
        self.bolt_page = BoltJointPage()
        self.bolt_page.hide()
        root.addWidget(self.bolt_page, 1)
        self.gear_page = GearPage()
        self.gear_page.hide()
        root.addWidget(self.gear_page, 1)
        self.spring_page = SpringPage()
        self.spring_page.hide()
        root.addWidget(self.spring_page, 1)
        self.bearing_page = BearingPage()
        self.bearing_page.hide()
        root.addWidget(self.bearing_page, 1)
        self.show_kind('unit')

    @staticmethod
    def _label(text, size=13, color='#333', bold=False):
        label = QLabel(text)
        label.setStyleSheet('font-size:%dpx;color:%s;%s'
                            % (size, color, 'font-weight:bold;' if bold else ''))
        return label

    def _build_unit(self):
        page = QWidget()
        form = QFormLayout(page)
        form.setContentsMargins(0, 0, 0, 0)
        form.setHorizontalSpacing(14)
        form.setVerticalSpacing(10)
        self.category = QComboBox()
        self.category.addItems(category_names())
        self.category.currentTextChanged.connect(self._category_changed)
        form.addRow(self._label('类别'), self.category)
        self.amount = QDoubleSpinBox()
        self.amount.setRange(-1e12, 1e12)
        self.amount.setDecimals(6)
        self.amount.setValue(1.0)
        self.amount.setKeyboardTracking(False)
        form.addRow(self._label('数值'), self.amount)
        self.dms_edit = QLineEdit()
        self.dms_edit.setPlaceholderText('例如 35°30′15″，也可直接输入 35.5')
        self.dms_edit.setVisible(False)
        self.dms_label = self._label('度分秒')
        self.dms_label.setVisible(False)
        form.addRow(self.dms_label, self.dms_edit)
        self.from_unit = QComboBox()
        self.to_unit = QComboBox()
        form.addRow(self._label('从'), self.from_unit)
        form.addRow(self._label('到'), self.to_unit)
        self.from_unit.currentTextChanged.connect(self._unit_changed)
        self._fill_units('长度')
        return page

    def _build_placeholder(self):
        self.placeholder = QLabel('')
        self.placeholder.setWordWrap(True)
        self.placeholder.setStyleSheet(
            'font-size:14px;color:#555;line-height:1.8;')
        self.placeholder.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        return self.placeholder

    def _fill_units(self, category, preferred=None):
        items = unit_labels(category)
        self._building = True
        for box in (self.from_unit, self.to_unit):
            box.clear()
            box.addItems(items)
        from_index = 0
        if preferred:
            for i, label in enumerate(items):
                if label == preferred or label.startswith(preferred + ' '):
                    from_index = i
                    break
        self.from_unit.setCurrentIndex(from_index)
        self.to_unit.setCurrentIndex(1 if len(items) > 1 else 0)
        self._building = False
        self._toggle_dms()

    def _short_text(self, name):
        return name.split(' ')[0].split(' (')[0]

    def _toggle_dms(self):
        dms = ('角度' == self.category.currentText() and
               self.from_unit.currentText().startswith('度分秒'))
        self.dms_edit.setVisible(dms)
        self.dms_label.setVisible(dms)

    def _unit_changed(self, *_):
        if self._building:
            return
        self._toggle_dms()
        self.calculate()

    def _category_changed(self, category):
        if self._building:
            return
        self._fill_units(category)
        if category == '硬度':
            self.amount.setValue(30.0)
        self.calculate()

    def show_kind(self, kind):
        self.kind = kind
        name, desc = TOOL_INFO.get(kind, ('选型工具', ''))
        self.form_title.setText(name)
        self.subtitle.setText(desc)
        self.body_widget.hide()
        self.vendor_host.hide()
        for page in (self.key_page, self.torque_page, self.bolt_page,
                     self.gear_page, self.spring_page, self.bearing_page):
            page.hide()
        self.calc_btn.hide()
        if kind == 'tolerance':
            self.vendor_host.show()
            self._ensure_tolerance()
            self._label_result('选型结果')
            return
        pages = {'key': self.key_page, 'torque': self.torque_page,
                 'bolt': self.bolt_page, 'gear': self.gear_page,
                 'spring': self.spring_page, 'bearing': self.bearing_page}
        if kind in pages:
            pages[kind].show()
            self._label_result('选型结果')
            return
        self.body_widget.show()
        if kind == 'unit':
            self.stack.setCurrentIndex(0)
            self.calc_btn.setText('换算')
            self.calc_btn.show()
            self._label_result('换算结果')
            self.calculate()
        else:
            self.stack.setCurrentIndex(1)
            self.placeholder.setText(
                '%s\n\n当前阶段：已完成选型工具页签与列表框架。\n'
                '该工具将按独立页面移植，参数、公式和结果区在后续阶段接入。'
                % name)
            self._label_result('选型结果')
            self.value.setText('—')
            self.value_unit.setText('')
            self.detail.setText('')
            self.formula.setText('')

    def _label_result(self, text):
        self.result_title.setText(text)

    def _ensure_tolerance(self):
        if self.tolerance_window is not None:
            return
        window = ToleranceWindow()
        widget = window.takeCentralWidget()
        if widget is None:
            widget = window.centralWidget()
        if widget is None:
            widget = window
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setWidget(widget)
        self.vendor_layout.addWidget(scroll)
        self.tolerance_window = window
        try:
            from core.tolerance_ocr import ToleranceOCRController
            self.tolerance_ocr = ToleranceOCRController(window, widget)
            window.set_ocr_controller(self.tolerance_ocr)
        except Exception:
            self.tolerance_ocr = None

    def _swap(self):
        a = self.from_unit.currentText()
        b = self.to_unit.currentText()
        try:
            result = convert(self.amount.value(), self.category.currentText(), a, b)
            self.amount.setValue(result)
        except ValueError:
            pass
        self.from_unit.setCurrentText(b)
        self.to_unit.setCurrentText(a)
        self.calculate()

    def _copy_result(self):
        QApplication.clipboard().setText(
            self.value.text() + ' ' + self.to_unit.currentText())

    def _pick_all(self, row, col):
        item = self.all_table.item(row, 0)
        if item is not None:
            self.to_unit.setCurrentText(item.text())
            self.calculate()

    def _fill_all(self, value, category, from_unit, to_unit):
        self.all_table.setRowCount(0)
        for label in unit_labels(category):
            try:
                result = convert(value, category, from_unit, label)
            except ValueError:
                result = None
            if result is None:
                shown = '—'
            elif label.startswith('度分秒'):
                shown = format_dms(result)
            else:
                shown = format_value(result)
            row = self.all_table.rowCount()
            self.all_table.insertRow(row)
            self.all_table.setItem(row, 0, QTableWidgetItem(label))
            self.all_table.setItem(row, 1, QTableWidgetItem(shown))
        self.all_table.resizeColumnsToContents()

    def calculate(self):
        if self.kind != 'unit':
            return None
        category = self.category.currentText()
        value = self.amount.value()
        if not self.dms_edit.isHidden():
            raw = self.dms_edit.text().strip()
            if raw:
                parsed = parse_dms(raw)
                if parsed is None:
                    self.value.setText('参数错误')
                    self.detail.setText('度分秒格式无法解析')
                    self.formula.setText('')
                    return None
                value = parsed
        try:
            result = convert(value, category,
                             self.from_unit.currentText(),
                             self.to_unit.currentText())
        except ValueError as exc:
            self.value.setText('参数错误')
            self.value_unit.setText('')
            self.detail.setText(str(exc))
            self.formula.setText('')
            return None
        if self.to_unit.currentText().startswith('度分秒'):
            shown = format_dms(result)
        else:
            shown = format_value(result)
        self.value.setText(shown)
        self.value_unit.setText(self.to_unit.currentText())
        self.detail.setText('%g %s → %s' % (
            value, self._short_text(self.from_unit.currentText()),
            self._short_text(self.to_unit.currentText())))
        self.formula.setText(formula(category, self.from_unit.currentText(),
                                     self.to_unit.currentText()))
        self._fill_all(value, category, self.from_unit.currentText(),
                       self.to_unit.currentText())
        return result
