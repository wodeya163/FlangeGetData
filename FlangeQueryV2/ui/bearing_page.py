# -*- coding: utf-8 -*-
"""轴承选型页：深沟球选型、指定型号校核与类型指南。"""

from PyQt5.QtWidgets import (QCheckBox, QComboBox, QDoubleSpinBox,
                             QFormLayout, QFrame, QHBoxLayout, QLabel,
                             QPushButton, QScrollArea, QTableWidget,
                             QTableWidgetItem, QTabWidget, QVBoxLayout, QWidget)

from core.bearing import check, recommend
from core.bearing_data_table import DEEP_GROOVE
from core.bearing_guide import type_guide
from core.bearing_variants import variant_guide
from ui.bearing_library import BearingLibraryTab

CARD_QSS = ('#bearing_input{background:#fff;border:1px solid #c9d2dc;'
            'border-radius:6px;}')
RESULT_QSS = ('#bearing_result{background:#f5f8fb;border:1px solid #c9d2dc;'
              'border-radius:6px;}')
HINT_QSS = 'font-size:12px;color:#666;'


def _label(text, size=13, color='#333', bold=False):
    lab = QLabel(text)
    lab.setStyleSheet('font-size:%dpx;color:%s;%s'
                      % (size, color, 'font-weight:bold;' if bold else ''))
    return lab


def _spin(value, maximum, suffix):
    box = QDoubleSpinBox()
    box.setRange(0.001, maximum)
    box.setDecimals(2)
    box.setValue(value)
    box.setSuffix(suffix)
    box.setKeyboardTracking(False)
    box.setMinimumWidth(180)
    return box


def _table(headers, height=180):
    table = QTableWidget(0, len(headers))
    table.setHorizontalHeaderLabels(headers)
    table.verticalHeader().setVisible(False)
    table.setEditTriggers(QTableWidget.NoEditTriggers)
    table.setSelectionMode(QTableWidget.NoSelection)
    table.horizontalHeader().setStretchLastSection(True)
    table.setMinimumHeight(height)
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


class BearingPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 18, 28, 18)
        root.setSpacing(10)
        root.addWidget(_label('轴承选型工具', 22, '#163a5f', True))
        root.addWidget(_label('深沟球轴承选型、指定型号校核，以及按工况推荐轴承类型。',
                              12, '#666'))
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(
            'QTabWidget::pane{border:1px solid #c9d2dc;background:#fff;}'
            'QTabBar::tab{padding:6px 16px;background:#f5f7fa;'
            'border:1px solid #c9d2dc;border-bottom:none;margin-right:2px;}'
            'QTabBar::tab:selected{background:#fff;color:#1f4e79;'
            'font-weight:bold;}')
        self.tabs.addTab(self._build_select(), '选型计算')
        self.tabs.addTab(self._build_guide(), '类型指南')
        self.tabs.addTab(self._build_variants(), '变体与后缀')
        self.tabs.addTab(BearingLibraryTab(), '三维模型库')
        root.addWidget(self.tabs, 1)

    def _build_select(self):
        page = QWidget()
        body = QHBoxLayout(page)
        body.setContentsMargins(0, 10, 0, 0)
        body.setSpacing(16)
        left = QFrame()
        left.setFixedWidth(500)
        left.setStyleSheet(CARD_QSS)
        lv = QVBoxLayout(left)
        lv.setContentsMargins(16, 14, 16, 14)
        lv.setSpacing(8)
        lv.addWidget(_label('选型参数', 16, '#1f4e79', True))
        form = QFormLayout()
        form.setHorizontalSpacing(12)
        form.setVerticalSpacing(8)
        self.mode = QComboBox()
        self.mode.addItems(['自动选型', '指定型号校核'])
        self.mode.currentIndexChanged.connect(self._mode_changed)
        self.code_box = QComboBox()
        self.code_box.addItems(sorted(DEEP_GROOVE.keys()))
        self.code_box.setEnabled(False)
        self.fr = _spin(2.0, 10000, ' kN')
        self.fa = _spin(0.5, 10000, ' kN')
        self.rpm = _spin(1500, 100000, ' rpm')
        self.target = _spin(20000, 1000000, ' h')
        self.lube = QComboBox()
        self.lube.addItems(['grease', 'oil'])
        self.bore = QDoubleSpinBox()
        self.bore.setRange(0, 500)
        self.bore.setDecimals(0)
        self.bore.setValue(0)
        self.bore.setSpecialValueText('不限')
        self.bore.setSuffix(' mm')
        for label, widget in [
                ('模式', self.mode), ('指定型号', self.code_box),
                ('径向载荷 Fr', self.fr), ('轴向载荷 Fa', self.fa),
                ('转速', self.rpm), ('目标寿命', self.target),
                ('润滑', self.lube), ('内径筛选', self.bore)]:
            form.addRow(_label(label), widget)
        lv.addLayout(form)
        btn = QPushButton('计算')
        btn.setProperty('class', 'b-print')
        btn.setMinimumHeight(34)
        btn.clicked.connect(self.calculate)
        lv.addWidget(btn)
        lv.addStretch(1)
        body.addWidget(left)

        right = QFrame()
        right.setStyleSheet(RESULT_QSS)
        rv = QVBoxLayout(right)
        rv.setContentsMargins(18, 16, 18, 16)
        rv.setSpacing(8)
        rv.addWidget(_label('计算结果', 16, '#1f4e79', True))
        self.code = QLabel('—')
        self.code.setStyleSheet(
            'font-size:34px;font-weight:bold;color:#163a5f;')
        rv.addWidget(self.code)
        self.status = QLabel('')
        self.status.setStyleSheet('font-size:15px;font-weight:bold;')
        rv.addWidget(self.status)
        self.detail = QLabel('')
        self.detail.setWordWrap(True)
        self.detail.setStyleSheet('font-size:13px;color:#333;')
        rv.addWidget(self.detail)
        rv.addWidget(_label('候选型号', 13, '#1f4e79', True))
        self.alt = _table(['型号', '尺寸 d×D×B', 'L10h', '结果'], 180)
        rv.addWidget(self.alt, 1)
        body.addWidget(right, 1)
        return page

    def _build_guide(self):
        page = QWidget()
        root = QVBoxLayout(page)
        root.setContentsMargins(0, 10, 0, 0)
        root.setSpacing(8)
        card = QFrame()
        card.setStyleSheet(CARD_QSS)
        form = QFormLayout(card)
        form.setContentsMargins(16, 14, 16, 14)
        form.setHorizontalSpacing(12)
        form.setVerticalSpacing(6)
        self.g_load = QComboBox()
        self.g_load.addItem('轻载', 'light')
        self.g_load.addItem('中等载荷', 'medium')
        self.g_load.addItem('重载', 'heavy')
        self.g_load.addItem('冲击载荷', 'impact')
        self.g_load.setCurrentIndex(1)
        self.g_dir = QComboBox()
        for text, key in [('纯径向', 'pure_radial'), ('径向为主', 'radial_main'),
                          ('轴向为主', 'axial_main'), ('纯轴向', 'pure_axial')]:
            self.g_dir.addItem(text, key)
        self.g_dir.setCurrentIndex(1)
        self.g_speed = QComboBox()
        for text, key in [('低速', 'low'), ('中速', 'medium'), ('高速', 'high')]:
            self.g_speed.addItem(text, key)
        self.g_speed.setCurrentIndex(1)
        self.g_align = QCheckBox('需要调心')
        self.g_space = QComboBox()
        for text, key in [('空间不限', 'free'), ('径向受限', 'radial_limited'),
                          ('轴向受限', 'axial_limited')]:
            self.g_space.addItem(text, key)
        self.g_impact = QCheckBox('有冲击')
        for label, widget in [('载荷', self.g_load), ('方向', self.g_dir),
                              ('转速', self.g_speed), ('', self.g_align),
                              ('空间', self.g_space), ('', self.g_impact)]:
            form.addRow(_label(label), widget)
        root.addWidget(card)
        row = QHBoxLayout()
        btn = QPushButton('推荐类型')
        btn.setProperty('class', 'b-print')
        btn.setMinimumHeight(32)
        btn.clicked.connect(self.guide)
        row.addWidget(btn)
        row.addStretch(1)
        root.addLayout(row)
        self.guide_table = _table(['类型', '标准', '得分', '适用场景'], 300)
        root.addWidget(self.guide_table, 1)
        self.guide_note = QLabel('按载荷、方向、转速、调心、空间和冲击综合评分。')
        self.guide_note.setStyleSheet(HINT_QSS)
        root.addWidget(self.guide_note)
        self.guide()
        return page

    def _build_variants(self):
        page = QWidget()
        root = QVBoxLayout(page)
        root.setContentsMargins(0, 10, 0, 0)
        root.setSpacing(8)
        row = QHBoxLayout()
        row.addWidget(_label('型号'))
        self.variant_code = QComboBox()
        self.variant_code.addItems(sorted(DEEP_GROOVE.keys()))
        self.variant_code.currentTextChanged.connect(self._variant_changed)
        row.addWidget(self.variant_code)
        self.variant_dims = QLabel('')
        self.variant_dims.setStyleSheet(HINT_QSS)
        row.addWidget(self.variant_dims)
        row.addStretch(1)
        root.addLayout(row)
        info = QLabel('')
        info.setWordWrap(True)
        info.setStyleSheet('font-size:13px;color:#333;background:#fff;'
                           'border:1px solid #d6dee7;padding:10px;')
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setWidget(info)
        root.addWidget(scroll, 1)
        self.variant_info = info
        self._variant_changed()
        return page

    def _variant_changed(self):
        v = variant_guide(self.variant_code.currentText())
        if not v:
            self.variant_info.setText('无该型号变体数据')
            return
        d, D, B, cr, c0, ng, no = v['dims']
        self.variant_dims.setText('%d×%d×%d mm　Cr=%.2f kN　C0r=%.2f kN'
                                  % (d, D, B, cr, c0))
        parts = ['<h3 style="color:#1f4e79">%s 变体速查</h3>'
                 % self.variant_code.currentText()]
        parts.append('<b style="color:#1f4e79">密封形式</b><br>'
                     + '<br><br>'.join(v['seals']))
        parts.append('<b style="color:#1f4e79">材料</b><br>'
                     + '<br><br>'.join(v['materials']))
        parts.append('<b style="color:#1f4e79">游隙</b><br>'
                     + '<br><br>'.join(v['clearances']))
        parts.append('<b style="color:#1f4e79">组合示例</b><br>'
                     + '<br>'.join(v['examples']))
        parts.append('<span style="color:#667085">%s</span>' % v['suffix'])
        self.variant_info.setText('<br><br>'.join(parts))

    def _mode_changed(self):
        self.code_box.setEnabled(self.mode.currentIndex() == 1)
        self.calculate()

    def calculate(self):
        fr, fa = self.fr.value(), self.fa.value()
        rpm, target = self.rpm.value(), self.target.value()
        lube = self.lube.currentText()
        if self.mode.currentIndex() == 1:
            code = self.code_box.currentText()
            try:
                res = check(code, fr, fa, rpm, target, lube)
            except ValueError as exc:
                self._error(str(exc))
                return None
            hits = []
        else:
            hits = recommend(fr, fa, rpm, target, lube,
                             int(self.bore.value()) or None)
            if not hits:
                self._error('无匹配型号，请放宽寿命、转速或内径')
                return None
            res = check(hits[0]['code'], fr, fa, rpm, target, lube)
        self.code.setText(res['code'])
        self.status.setText('通过' if res['pass'] else '不通过')
        self.status.setStyleSheet(
            'font-size:15px;font-weight:bold;color:%s;'
            % ('#1a7f37' if res['pass'] else '#c0392b'))
        self.detail.setText(
            'd×D×B：%d × %d × %d mm\n'
            'Cr=%.2f kN　C0r=%.2f kN\n'
            '当量动载荷 P=%.2f kN，e=%.3f，Y=%.3f\n'
            'L10h=%.0f h　目标 %.0f h\n'
            'P0=%.2f kN　S0=%.2f'
            % (res['d'], res['D'], res['B'], res['Cr'], res['C0r'],
               res['P'], res['e'], res['y'], res['L10h'], target,
               res['P0'], res['S0']))
        rows = []
        for h in hits[:8]:
            rows.append((h['code'], '%d×%d×%d' % (h['d'], h['D'], h['B']),
                         '%.0f h' % h['L10h'], '候选'))
        if not rows:
            rows = [(res['code'], '%d×%d×%d' % (res['d'], res['D'], res['B']),
                     '%.0f h' % res['L10h'], '指定')]
        _rows(self.alt, rows)
        return res

    def _error(self, text):
        self.code.setText('无匹配')
        self.status.setText(text)
        self.status.setStyleSheet('font-size:15px;color:#c0392b;')
        self.detail.setText('')
        _rows(self.alt, [])

    def guide(self):
        result = type_guide(
            self.g_load.currentData(), self.g_dir.currentData(),
            self.g_speed.currentData(), self.g_align.isChecked(),
            self.g_space.currentData(), self.g_impact.isChecked())
        rows = []
        for item, score in result:
            rows.append((item['name'], item['gb'], '%.1f' % score,
                         '；'.join(item['scene'][:2])))
        _rows(self.guide_table, rows)
        return result
