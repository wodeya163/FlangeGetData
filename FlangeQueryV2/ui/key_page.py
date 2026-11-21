# -*- coding: utf-8 -*-
"""键联接智能选型页（按原工具截图布局）。"""

import csv
import json
import math
from datetime import datetime

from PyQt5.QtCore import (Qt, QRect, QRectF, QPointF, QSettings,
                         pyqtSignal)
from PyQt5.QtGui import (QColor, QFont, QPageLayout, QPageSize,
                         QPainter, QPen, QPdfWriter)
from PyQt5.QtPrintSupport import QPrintPreviewDialog, QPrinter
from PyQt5.QtWidgets import (QApplication, QComboBox, QDoubleSpinBox,
                             QDialog, QDialogButtonBox, QFileDialog,
                             QMessageBox, QTableWidget, QTableWidgetItem,
                             QTextBrowser,
                             QFormLayout, QFrame, QGridLayout,
                             QHBoxLayout, QLabel, QLineEdit, QListWidget,
                             QPushButton,
                             QScrollArea,
                             QTabWidget, QVBoxLayout, QWidget)

from core.key_tolerance import format_tolerance_rows
from core.key_select import (KEY_LENGTH_SERIES, KEY_MATERIALS,
                             VERDICT_LABEL, check,
                             keyway_depth,
                             parallel_check_manual, recommend_key_type,
                             woodruff_options,
                             smart_design, spline_check, taper_check,
                             woodruff_check)

INK = QColor('#17202a')
BLUE = QColor('#6c5ce7')


class KeyDrawing(QWidget):
    """键联接剖面示意图，按键型切换。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(360)
        self.kind = 'parallel'
        self.spec = None
        self.set_data(12, 8, 40, 5, 3.3, 40)

    def set_data(self, b, h, L, t1, t2, d, kind='parallel', spec=None):
        self.b, self.h, self.L = b, h, L
        self.t1, self.t2, self.d = t1, t2, d
        self.kind = kind
        self.spec = spec
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        p.fillRect(self.rect(), QColor('#ffffff'))
        if self.kind == 'spline':
            self._draw_spline(p)
        elif self.kind == 'taper':
            self._draw_taper(p)
        elif self.kind == 'woodruff':
            self._draw_woodruff(p)
        else:
            self._draw_flat(p)

    def _font(self, p, size=12):
        f = QFont('Microsoft YaHei')
        f.setPixelSize(size)
        p.setFont(f)
        p.setPen(QColor('#555'))

    def _draw_flat(self, p):
        w, h = self.width(), self.height()
        cx, cy = w / 2, 165
        r = min(100, h * 0.27)
        ks = r / (self.d / 2)
        p.setPen(QPen(INK, 2))
        p.setBrush(QColor('#f3f5f8'))
        p.drawEllipse(QRectF(cx - r, cy - r, 2 * r, 2 * r))
        p.setBrush(QColor('#ffffff'))
        p.drawEllipse(QRectF(cx - r * 0.52, cy - r * 0.52,
                             r * 1.04, r * 1.04))
        bw = max(18, self.b * ks)
        depth = max(10, self.t1 * ks)
        p.setPen(QPen(INK, 1.8))
        p.setBrush(QColor('#ffffff'))
        p.drawRect(QRectF(cx - bw / 2, cy - r, bw, depth))
        p.setBrush(BLUE)
        p.drawRect(QRectF(cx - bw / 2, cy - r + depth - self.h * ks,
                           bw, self.h * ks))
        self._font(p)
        p.drawText(QRectF(cx - 80, cy - r - 24, 160, 20),
                   Qt.AlignCenter, 'b=%g' % self.b)
        p.drawText(QRectF(cx - 100, cy + 34, 200, 20),
                   Qt.AlignCenter, 'd−t1=%g' % (self.d - self.t1))
        ax, ay = 55, h - 85
        aw, ah = max(140, w * 0.24), 50
        p.setPen(QPen(INK, 2))
        p.setBrush(QColor('#f3f5f8'))
        p.drawRect(QRectF(ax, ay, aw, ah))
        p.setBrush(BLUE)
        p.drawRect(QRectF(ax + aw * 0.32, ay - 11, aw * 0.36, 13))
        self._font(p)
        p.drawText(QRectF(ax + aw * 0.72, ay - 17, 80, 18),
                   Qt.AlignLeft | Qt.AlignVCenter, 't2=%g' % self.t2)

    def _draw_spline(self, p):
        w, h = self.width(), self.height()
        cx, cy = w / 2, 170
        r = min(100, h * 0.27)
        spec = self.spec or {}
        N = int(spec.get('N', 8))
        p.setPen(QPen(INK, 2))
        p.setBrush(QColor('#eef4fb'))
        p.drawEllipse(QRectF(cx - r, cy - r, 2 * r, 2 * r))
        p.setBrush(QColor('#ffffff'))
        p.drawEllipse(QRectF(cx - r * 0.58, cy - r * 0.58,
                             r * 1.16, r * 1.16))
        p.setBrush(BLUE)
        for i in range(N):
            a = 2 * math.pi * i / N
            x = cx + (r - 4) * math.cos(a)
            y = cy + (r - 4) * math.sin(a)
            p.drawRect(QRectF(x - 7, y - 3.5, 14, 7))
        self._font(p, 13)
        p.setPen(QColor('#17202a'))
        p.drawText(QRectF(cx - 160, 24, 320, 24), Qt.AlignCenter,
                   '矩形花键 %s' % spec.get('spec', ''))
        p.drawText(QRectF(cx - 180, cy + r + 18, 360, 22), Qt.AlignCenter,
                   'N=%d　d=%g　D=%g　B=%g' % (
                       N, spec.get('d', self.d), spec.get('D', 0),
                       spec.get('B', self.b)))

    def _draw_taper(self, p):
        w, h = self.width(), self.height()
        cx, cy = w / 2, 170
        r = min(100, h * 0.27)
        ks = r / (self.d / 2)
        p.setPen(QPen(INK, 2))
        p.setBrush(QColor('#f3f5f8'))
        p.drawEllipse(QRectF(cx - r, cy - r, 2 * r, 2 * r))
        p.setBrush(QColor('#ffffff'))
        p.drawEllipse(QRectF(cx - r * 0.58, cy - r * 0.58,
                             r * 1.16, r * 1.16))
        bw = max(18, self.b * ks)
        kh = max(12, min(28, self.b * 0.8 * ks))
        p.setPen(QPen(INK, 1.8))
        p.setBrush(BLUE)
        poly = [QRectF(cx - bw / 2, cy - r, bw, kh)]
        p.drawPolygon(
            QPointF(cx - bw / 2, cy - r),
            QPointF(cx + bw / 2, cy - r),
            QPointF(cx + bw * 0.38, cy - r + kh),
            QPointF(cx - bw * 0.38, cy - r + kh))
        self._font(p, 13)
        p.setPen(QColor('#17202a'))
        p.drawText(QRectF(cx - 160, 24, 320, 24), Qt.AlignCenter,
                   '普通楔键  b=%g  L=%g' % (self.b, self.L))
        p.drawText(QRectF(cx - 140, cy + r + 18, 280, 22), Qt.AlignCenter,
                   '上下面为工作面，1:100 斜度')

    def _draw_woodruff(self, p):
        w, h = self.width(), self.height()
        cx, cy = w / 2, 170
        r = min(100, h * 0.27)
        p.setPen(QPen(INK, 2))
        p.setBrush(QColor('#f3f5f8'))
        p.drawEllipse(QRectF(cx - r, cy - r, 2 * r, 2 * r))
        p.setBrush(QColor('#ffffff'))
        p.drawEllipse(QRectF(cx - r * 0.58, cy - r * 0.58,
                             r * 1.16, r * 1.16))
        p.setBrush(BLUE)
        p.drawChord(QRectF(cx - 22, cy - r - 12, 44, 30), 0, 180 * 16)
        self._font(p, 13)
        p.setPen(QColor('#17202a'))
        p.drawText(QRectF(cx - 180, 24, 360, 24), Qt.AlignCenter,
                   '半圆键  %s' % (self.spec or ''))
        p.drawText(QRectF(cx - 160, cy + r + 18, 320, 22), Qt.AlignCenter,
                   '键可绕几何中心摆动')

class KeyAssistantPage(QWidget):
    """设计助手：按工况推荐键型。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        content = QWidget()
        root = QVBoxLayout(content)
        root.setContentsMargins(18, 16, 18, 16)
        root.setSpacing(10)
        title = QLabel('设计助手 · 键型推荐')
        title.setStyleSheet('font-size:18px;font-weight:bold;color:#17202a;')
        root.addWidget(title)
        form = QFormLayout()
        form.setHorizontalSpacing(14)
        form.setVerticalSpacing(8)
        self.d = QDoubleSpinBox()
        self.d.setRange(1, 500)
        self.d.setValue(30)
        self.d.setSuffix(' mm')
        self.load = QComboBox()
        self.load.addItems(['静载荷', '轻微冲击', '冲击'])
        self.move = QComboBox()
        self.move.addItems(['否', '是'])
        self.precision = QComboBox()
        self.precision.addItems(['一般', '高'])
        self.axial = QComboBox()
        self.axial.addItems(['否', '是'])
        for label, w in [('轴径 d', self.d), ('载荷性质', self.load),
                         ('需要轴向移动', self.move),
                         ('对中性要求', self.precision),
                         ('需承受轴向力', self.axial)]:
            form.addRow(QLabel(label), w)
        root.addLayout(form)
        btn = QPushButton('推荐键型')
        btn.setProperty('class', 'b-print')
        btn.setMaximumWidth(120)
        btn.clicked.connect(self.calculate)
        root.addWidget(btn, alignment=Qt.AlignLeft)
        self.summary = QLabel('')
        self.summary.setWordWrap(True)
        self.summary.setStyleSheet('font-size:14px;color:#17202a;')
        root.addWidget(self.summary)
        self.cards = QVBoxLayout()
        self.cards.setSpacing(6)
        root.addLayout(self.cards)
        root.addWidget(QLabel('键型特性对比'))
        self.trait_table = QTableWidget(5, 6)
        self.trait_table.setHorizontalHeaderLabels(
            ['键型', '对中性', '承载', '装拆', '轴向固定', '成本'])
        self.trait_table.verticalHeader().setVisible(False)
        self.trait_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.trait_table.horizontalHeader().setStretchLastSection(True)
        traits = [
            ('普通平键', '好', '中', '简单', '无', '低'),
            ('导向平键', '好', '中', '简单', '导向滑移', '低'),
            ('半圆键', '好', '小', '方便', '无', '低'),
            ('楔键', '差', '中', '较麻烦', '单向轴向', '低'),
            ('矩形花键', '优', '大', '需专用工装', '可导向', '较高'),
        ]
        for row, values in enumerate(traits):
            for col, value in enumerate(values):
                self.trait_table.setItem(row, col, QTableWidgetItem(value))
        self.trait_table.setMinimumHeight(220)
        self.trait_table.setMaximumHeight(240)
        self.trait_table.verticalHeader().setDefaultSectionSize(32)
        root.addWidget(self.trait_table)
        root.addStretch(1)
        scroll.setWidget(content)
        outer.addWidget(scroll)
        self.calculate()

    def calculate(self):
        while self.cards.count():
            item = self.cards.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        recs = recommend_key_type(
            self.d.value(), self.load.currentText(),
            self.move.currentText() == '是', self.precision.currentText(),
            self.axial.currentText() == '是')
        best = recs[0]
        self.summary.setText('推荐顺序：%s' % ' → '.join(
            '%s（%s/%d分）' % (r['name'], VERDICT_LABEL[r['verdict']],
                                r.get('score', 0))
            for r in recs))
        colors = {'suit': '#1a7f37', 'ok': '#a15c00', 'no': '#c0392b'}
        for r in recs:
            card = QFrame()
            card.setStyleSheet('QFrame{background:#fff;border:1px solid #d6dee7;'
                               'border-left:4px solid %s;border-radius:4px;}'
                               % colors[r['verdict']])
            card.setMinimumHeight(68)
            lay = QVBoxLayout(card)
            lay.setContentsMargins(12, 8, 12, 8)
            lay.setSpacing(4)
            lab = QLabel('%s · %s　%d 分' % (
                VERDICT_LABEL[r['verdict']], r['name'], r.get('score', 0)))
            lab.setMinimumHeight(22)
            lab.setStyleSheet('font-size:14px;font-weight:bold;color:%s;'
                              % colors[r['verdict']])
            reason = QLabel(r['reason'])
            reason.setWordWrap(True)
            reason.setMinimumHeight(34)
            reason.setStyleSheet('font-size:12px;color:#555;')
            lay.addWidget(lab)
            lay.addWidget(reason)
            self.cards.addWidget(card)
        return recs


class KeyTypePage(QWidget):
    """平键/半圆键/楔键/花键的独立校核页。"""

    def __init__(self, kind, parent=None):
        super().__init__(parent)
        self.kind = kind
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        content = QWidget()
        root = QVBoxLayout(content)
        root.setContentsMargins(18, 16, 18, 16)
        root.setSpacing(8)
        title = QLabel({'parallel': '平键选型', 'woodruff': '半圆键选型',
                        'taper': '楔键选型', 'spline': '矩形花键选型'}[kind])
        title.setStyleSheet('font-size:18px;font-weight:bold;color:#17202a;')
        root.addWidget(title)
        form = QFormLayout()
        form.setHorizontalSpacing(14)
        form.setVerticalSpacing(6)
        self.boxes, self.combos = {}, {}
        self._add_spin(form, 'd', '轴径/小径 d', 30.0, ' mm')
        self._add_spin(form, 'T', '传递扭矩 T', 50.0, ' N·m')
        if kind == 'parallel':
            self._add_spin(form, 'hub', '轮毂宽度', 32.0, ' mm')
            self._add_spin(form, 'b', '键宽 b（0=自动）', 0.0, ' mm')
            self._add_spin(form, 'h', '键高 h（0=自动）', 0.0, ' mm')
            self._add_spin(form, 'L', '键长 L（0=自动）', 0.0, ' mm')
            self._add_combo(form, 'std_length', '标准键长',
                            ['自定义'] + [str(x) for x in KEY_LENGTH_SERIES])
            self._add_combo(form, 'key_material', '键材料',
                            list(KEY_MATERIALS))
            self._add_combo(form, 'key_type', '键型', ['A', 'B', 'C'])
            self._add_combo(form, 'fit', '配合',
                            ['松联结', '正常联结', '紧密联结'])
        if kind == 'taper':
            self._add_spin(form, 'hub', '轮毂宽度（自动选长）', 32.0, ' mm')
            self._add_spin(form, 'L', '键长 L（0=自动）', 0.0, ' mm')
            self._add_combo(form, 'std_length', '标准键长',
                            ['自定义'] + [str(x) for x in KEY_LENGTH_SERIES])
            self._add_combo(form, 'taper_kind', '楔键类型', ['普通A', '普通B', '钩头'])
        if kind == 'spline':
            self._add_spin(form, 'L', '键长/结合长度 L', 40.0, ' mm')
        self._add_combo(form, 'material', '轮毂材料', ['钢', '铸铁'])
        self._add_combo(form, 'load', '载荷性质', ['静载荷', '轻微冲击', '冲击'])
        if kind == 'woodruff':
            self._add_combo(form, 'woodruff_code', '半圆键规格',
                            [x['code'] for x in woodruff_options(30)])
            self.boxes['d'].valueChanged.connect(self._refresh_woodruff)
        if kind == 'spline':
            self._add_combo(form, 'heat', '齿面热处理', ['未热处理', '已热处理'])
            self._add_combo(form, 'usage', '使用情况', ['良好', '中等', '不良'])
            self._add_combo(form, 'conn', '联接方式', ['静联接', '动联接'])
            self._add_combo(form, 'centering', '定心方式',
                            ['齿侧定心', '外径定心', '内径定心'])
        if 'std_length' in self.combos:
            self.combos['std_length'].currentTextChanged.connect(
                self._std_length_changed)
        root.addLayout(form)
        btn = QPushButton('计算')
        btn.setProperty('class', 'b-print')
        btn.setMaximumWidth(120)
        btn.clicked.connect(self.calculate)
        btn.setMinimumHeight(34)
        root.addWidget(btn, alignment=Qt.AlignLeft)
        self.result = QLabel('—')
        self.result.setWordWrap(True)
        self.result.setMinimumHeight(110)
        self.result.setStyleSheet('font-size:13px;color:#17202a;'
                                  'background:#f5f8fb;padding:10px;'
                                  'border:1px solid #d6dee7;border-radius:4px;')
        root.addWidget(self.result)
        self.drawing = KeyDrawing()
        root.addWidget(self.drawing)
        root.addStretch(1)
        scroll.setWidget(content)
        outer.addWidget(scroll)
        self.calculate()

    def _add_spin(self, form, key, label, value, suffix):
        box = QDoubleSpinBox()
        box.setRange(0.0, 100000)
        box.setDecimals(2)
        box.setValue(value)
        box.setSuffix(suffix)
        box.setMinimumWidth(220)
        self.boxes[key] = box
        lab = QLabel(label)
        lab.setMinimumHeight(24)
        form.addRow(lab, box)

    def _refresh_woodruff(self, *_):
        combo = self.combos.get('woodruff_code')
        if combo is None:
            return
        current = combo.currentText()
        codes = [x['code'] for x in woodruff_options(self.boxes['d'].value())]
        combo.blockSignals(True)
        combo.clear()
        combo.addItems(codes)
        if current in codes:
            combo.setCurrentText(current)
        combo.blockSignals(False)

    def _add_combo(self, form, key, label, items):
        box = QComboBox()
        box.addItems(items)
        self.combos[key] = box
        lab = QLabel(label)
        lab.setMinimumHeight(24)
        form.addRow(lab, box)

    def _std_length_changed(self, text):
        if text and text != '自定义':
            try:
                self.boxes['L'].setValue(float(text))
            except ValueError:
                pass

    def calculate(self):
        d, torque = self.boxes['d'].value(), self.boxes['T'].value()
        material = self.combos['material'].currentText()
        load = self.combos['load'].currentText()
        try:
            if self.kind == 'parallel':
                b = self.boxes['b'].value()
                h = self.boxes['h'].value()
                L = self.boxes['L'].value()
                if b > 0 and h > 0 and L > 0:
                    r = parallel_check_manual(
                        d, b, h, L, torque, material, load,
                        self.combos['key_type'].currentText(),
                        self.combos['fit'].currentText(),
                        self.combos['key_material'].currentText())
                    text = ('%s\n挤压 %.2f / %.0f MPa（%.1f%%）\n'
                            '剪切 %.2f / %.0f MPa\n%s\n'
                            '公差：键宽 %s，键高 %s，键长 %s\n'
                            '配合：轴槽 %s，毂槽 %s'
                            % (r['mark'], r['sigma_p'], r['allowable_p'],
                               r['ratio_p'], r['tau'], r['allowable_tau'],
                               '通过' if r['safe'] else '不通过',
                               r['tol']['b'], r['tol']['h'], r['tol']['L'],
                               r['fit_shaft'], r['fit_hub']))
                else:
                    r = check(d, torque, self.boxes['hub'].value(),
                              material, load,
                              self.combos['key_material'].currentText())
                    text = ('键 %d×%d×%d\n挤压 %.2f / %.0f MPa（%.1f%%）\n'
                            '剪切 %.2f / %.0f MPa\n%s\n'
                            '公差：键宽 %s，键高 %s，键长 %s'
                            % (r['b'], r['h'], r['L'], r['sigma_p'],
                               r['allowable_p'], r['ratio_p'], r['tau'],
                               r['allowable_tau'],
                               '通过' if r['safe'] else '不通过',
                               r['tol']['b'], r['tol']['h'], r['tol']['L']))
            elif self.kind == 'woodruff':
                r = woodruff_check(d, torque, material, load,
                                   self.combos['woodruff_code'].currentText())
                text = ('半圆键 %s\n挤压 %.2f / %.0f MPa（%.1f%%）\n%s\n'
                        '公差：键宽 %s，键高 %s，键径 %s\n'
                        '配合：轴槽 %s，毂槽 %s'
                        % (r['code'], r['sigma_p'], r['allowable'],
                           r['ratio'], '通过' if r['safe'] else '不通过',
                           r['tol']['b'], r['tol']['h'], r['tol']['d1'],
                           r['fit_shaft'], r['fit_hub']))
            elif self.kind == 'taper':
                kind = self.combos['taper_kind'].currentText()
                length = self.boxes['L'].value() or None
                r = taper_check(d, torque, length, material, load, kind,
                                self.boxes['hub'].value())
                text = ('%s楔键 b=%g  L=%g\n挤压 %.2f / %.0f MPa（%.1f%%）\n%s\n%s\n'
                        '公差：键宽 %s，键高 %s，键长 %s\n'
                        '配合：轴槽 %s，毂槽 %s'
                        % (kind, r['b'], r['L'], r['sigma_p'],
                           r['allowable'], r['ratio'],
                           '通过' if r['safe'] else '不通过',
                           r['standard'], r['tol']['b'], r['tol']['h'],
                           r['tol']['L'], r['fit_shaft'], r['fit_hub']))
            else:
                r = spline_check(d, torque, self.boxes['L'].value(),
                                 self.combos['heat'].currentText(),
                                 self.combos['usage'].currentText(),
                                 self.combos['conn'].currentText(),
                                 self.combos['centering'].currentText())
                text = ('花键 %s\n挤压 %.2f / %.0f MPa（%.1f%%）\n%s\n'
                        '定心：%s　配合 %s'
                        % (r['spec'], r['p'], r['allowable'], r['ratio'],
                           '通过' if r['safe'] else '不通过',
                           r['centering'], r['fit']))
        except ValueError as exc:
            self.result.setText('参数错误：%s' % exc)
            return None
        tol_text = format_tolerance_rows(r.get('tolerances', []))
        if tol_text:
            text += '\n' + tol_text
        self.result.setText(text)
        self.result.setMinimumHeight(210)
        self.last_result = r
        depth = keyway_depth(d)
        if self.kind == 'parallel':
            self.drawing.set_data(r['b'], r['h'], r['L'],
                                  depth['t1'], depth['t2'], d)
        elif self.kind == 'woodruff':
            self.drawing.set_data(r['b'], r['h'], r['d1'],
                                  r['d1'] / 2, 0, d, kind='woodruff',
                                  spec=r['code'])
        elif self.kind == 'taper':
            self.drawing.set_data(r['b'], max(4, r['b'] * 0.8), r['L'],
                                  depth['t1'], depth['t2'], d, kind='taper',
                                  spec=r['kind'])
        else:
            self.drawing.set_data(r['B'], r['h'], r['L'], 0, 0, d,
                                  kind='spline', spec=r)
        return r


class KeyOverviewPage(QWidget):
    """总览：键型、标准、适用范围和快捷入口。"""

    open_type = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(18, 14, 18, 14)
        title = QLabel('键联接总览')
        title.setStyleSheet('font-size:16px;font-weight:bold;color:#17202a;')
        root.addWidget(title)
        tip = QLabel('按标准选择键型；点击“打开”进入对应校核页。')
        tip.setStyleSheet('font-size:12px;color:#666;')
        root.addWidget(tip)
        grid = QGridLayout()
        grid.setSpacing(10)
        items = [
            ('普通平键', 'GB/T 1096-2003', '轴径 6–500 mm',
             '对中好、装拆方便，最常用；分 A/B/C 型。', '平键'),
            ('半圆键', 'GB/T 1099.1-2003', '轴径 6–38 mm',
             '可在轴槽内摆动，适合锥形轴端和薄轮毂。', '半圆键'),
            ('楔键', 'GB/T 1564/1565-2003', '轴径 6–500 mm',
             '靠楔紧传力，可承受单向轴向力，对中性差。', '楔键'),
            ('矩形花键', 'GB/T 1144-2001', '小径 11–112 mm',
             '承载大、对中好，适合重载和导向联接。', '花键'),
            ('导向平键', 'GB/T 1097-2003', '按平键系列',
             '允许轮毂轴向滑移，用于离合器和变速箱。', '平键'),
        ]
        for i, (name, std, scope, desc, target) in enumerate(items):
            card = QFrame()
            card.setStyleSheet('QFrame{background:#fff;border:1px solid #d6dee7;'
                               'border-radius:6px;}')
            lay = QVBoxLayout(card)
            head = QLabel(name)
            head.setStyleSheet('font-size:14px;font-weight:bold;color:#17202a;')
            lay.addWidget(head)
            meta = QLabel('%s\n%s' % (std, scope))
            meta.setStyleSheet('font-size:12px;color:#6c5ce7;')
            lay.addWidget(meta)
            body = QLabel(desc)
            body.setWordWrap(True)
            body.setStyleSheet('font-size:12px;color:#555;')
            lay.addWidget(body)
            btn = QPushButton('打开')
            btn.setStyleSheet('background:#fff;color:#6c5ce7;'
                              'border:1px solid #6c5ce7;border-radius:4px;'
                              'padding:3px 12px;')
            btn.clicked.connect(lambda _, n=target: self.open_type.emit(n))
            lay.addWidget(btn, alignment=Qt.AlignLeft)
            grid.addWidget(card, i // 3, i % 3)
        root.addLayout(grid)
        root.addStretch(1)


class KeyLibraryPage(QWidget):
    """选型库：保存智能选型结果，支持载入/删除。"""

    restore_requested = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = QSettings('FlangeQueryV2', 'KeyTool')
        root = QVBoxLayout(self)
        root.setContentsMargins(18, 14, 18, 14)
        title = QLabel('选型库')
        title.setStyleSheet('font-size:16px;font-weight:bold;color:#17202a;')
        root.addWidget(title)
        tip = QLabel('智能选型结果可保存到库；双击记录载入参数。')
        tip.setStyleSheet('font-size:12px;color:#666;')
        root.addWidget(tip)
        self.list = QListWidget()
        self.list.setStyleSheet('font-size:13px;')
        self.list.itemDoubleClicked.connect(self._restore)
        root.addWidget(self.list, 1)
        row = QHBoxLayout()
        load_btn = QPushButton('载入选中')
        load_btn.setStyleSheet('background:#6c5ce7;color:white;border:none;'
                               'border-radius:4px;padding:4px 12px;')
        load_btn.clicked.connect(self._load_selected)
        row.addWidget(load_btn)
        del_btn = QPushButton('删除选中')
        clear_btn = QPushButton('清空选型库')
        for btn in (del_btn, clear_btn):
            btn.setStyleSheet('background:#fff;border:1px solid #d6dee7;'
                              'border-radius:4px;padding:4px 12px;')
            row.addWidget(btn)
        row.addStretch(1)
        del_btn.clicked.connect(self._delete)
        clear_btn.clicked.connect(self._clear)
        root.addLayout(row)
        self._refresh()

    def _records(self):
        try:
            data = json.loads(self.settings.value('library', '[]'))
        except (TypeError, ValueError):
            data = []
        return data if isinstance(data, list) else []

    def _write(self, data):
        self.settings.setValue('library', json.dumps(data[:30], ensure_ascii=False))
        self.settings.sync()
        self._refresh()

    def add(self, record):
        data = self._records()
        mark = record.get('mark', '')
        data = [x for x in data if x.get('mark') != mark]
        data.insert(0, record)
        self._write(data)

    def _refresh(self):
        self.list.clear()
        self.records = self._records()
        for item in self.records:
            self.list.addItem('%s  %s · d=%g · T=%g' % (
                item.get('time', ''), item.get('mark', ''),
                item.get('d', 0), item.get('T', 0)))

    def _load_selected(self):
        item = self.list.currentItem()
        if item is not None:
            self._restore(item)

    def _delete(self):
        row = self.list.currentRow()
        data = self._records()
        if 0 <= row < len(data):
            data.pop(row)
            self._write(data)

    def _clear(self):
        if QMessageBox.question(
                self, '清空选型库', '确定清空全部选型库记录？',
                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            self._write([])

    def _restore(self, item):
        row = self.list.row(item)
        data = self._records()
        if 0 <= row < len(data):
            self.restore_requested.emit(data[row])


class KeyPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(18, 12, 18, 12)
        root.setSpacing(8)
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(
            'QTabWidget::pane{border:1px solid #d6dee7;background:#fff;}'
            'QTabBar::tab{padding:7px 18px;background:#f5f7fa;'
            'border:1px solid #d6dee7;border-bottom:none;'
            'margin-right:2px;}'
            'QTabBar::tab:selected{background:#fff;color:#6c5ce7;'
            'font-weight:bold;}')
        self.tabs.addTab(self._build_smart(), '智能选型')
        self.tabs.addTab(self._build_home(), '首页')
        self.tabs.addTab(KeyTypePage('parallel'), '平键')
        self.tabs.addTab(KeyTypePage('woodruff'), '半圆键')
        self.tabs.addTab(KeyTypePage('taper'), '楔键')
        self.tabs.addTab(KeyTypePage('spline'), '花键')
        self.tabs.addTab(KeyAssistantPage(), '设计助手')
        self.library_page = KeyLibraryPage(self)
        self.tabs.addTab(self.library_page, '选型库')
        self.library_page.restore_requested.connect(self._restore_library)
        self.overview_page = KeyOverviewPage(self)
        self.tabs.addTab(self.overview_page, '总览')
        self.overview_page.open_type.connect(self._open_named_tab)
        # 原工具顺序：首页在智能选型之前
        self.tabs.tabBar().moveTab(1, 0)
        self.tabs.tabBar().moveTab(6, 2)
        self.tabs.setCurrentIndex(1)
        tools = QHBoxLayout()
        tools.addStretch(1)
        self.help_btn = QPushButton('帮助')
        self.help_btn.setStyleSheet('background:#fff;border:1px solid #d6dee7;'
                                    'border-radius:4px;padding:4px 12px;')
        self.help_btn.clicked.connect(self.show_help)
        tools.addWidget(self.help_btn)
        self.copy_btn = QPushButton('复制结果')
        self.copy_btn.setStyleSheet('background:#fff;border:1px solid #d6dee7;'
                                    'border-radius:4px;padding:4px 12px;')
        self.copy_btn.clicked.connect(self.copy_result)
        self.export_btn = QPushButton('导出结果')
        self.export_btn.setStyleSheet('background:#fff;border:1px solid #d6dee7;'
                                      'border-radius:4px;padding:4px 12px;')
        self.export_btn.clicked.connect(self.export_result)
        self.pdf_btn = QPushButton('导出 PDF')
        self.pdf_btn.setStyleSheet('background:#fff;border:1px solid #d6dee7;'
                                   'border-radius:4px;padding:4px 12px;')
        self.pdf_btn.clicked.connect(self.export_pdf)
        self.paper_btn = QPushButton('页面设置')
        self.paper_btn.setStyleSheet('background:#fff;border:1px solid #d6dee7;'
                                     'border-radius:4px;padding:4px 12px;')
        self.paper_btn.clicked.connect(self.page_setup)
        tools.addWidget(self.copy_btn)
        tools.addWidget(self.export_btn)
        tools.addWidget(self.paper_btn)
        tools.addWidget(self.pdf_btn)
        self.preview_btn = QPushButton('打印预览')
        self.preview_btn.setStyleSheet('background:#fff;border:1px solid #d6dee7;'
                                       'border-radius:4px;padding:4px 12px;')
        self.preview_btn.clicked.connect(self.print_preview)
        tools.addWidget(self.preview_btn)
        root.addLayout(tools)
        root.addWidget(self.tabs)
        self.settings = QSettings('FlangeQueryV2', 'KeyTool')
        self._load_settings()
        self.calculate()

    def _build_home(self):
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(18, 16, 18, 16)
        lay.setSpacing(10)
        title = QLabel('键联接选型工具')
        title.setStyleSheet('font-size:22px;font-weight:bold;color:#17202a;')
        lay.addWidget(title)
        sub = QLabel('GB/T 1096 平键 · GB/T 1099.1 半圆键 · '
                     'GB/T 1564/1565 楔键 · GB/T 1144 矩形花键')
        sub.setStyleSheet('font-size:12px;color:#666;')
        lay.addWidget(sub)
        cards = QHBoxLayout()
        for text, index in (
                ('智能选型', 1), ('设计助手', 2), ('平键', 3),
                ('半圆键', 4), ('楔键', 5), ('花键', 6)):
            btn = QPushButton(text)
            btn.setMinimumHeight(52)
            btn.setStyleSheet('background:#fff;border:1px solid #d6dee7;'
                              'border-radius:6px;font-size:14px;color:#17202a;')
            btn.clicked.connect(lambda _=False, i=index: self.tabs.setCurrentIndex(i))
            cards.addWidget(btn)
        lay.addLayout(cards)
        self.home_last = QLabel('当前结果：请在“智能选型”中计算。')
        self.home_last.setWordWrap(True)
        self.home_last.setStyleSheet('font-size:13px;color:#555;'
                                     'background:#fafbfc;padding:10px;'
                                     'border:1px solid #e4e8ee;border-radius:4px;')
        lay.addWidget(self.home_last)
        self.history_label = QLabel('')
        self.history_label.setWordWrap(True)
        self.history_label.setStyleSheet('font-size:12px;color:#666;'
                                         'background:#fafbfc;padding:10px;'
                                         'border:1px solid #e4e8ee;border-radius:4px;')
        lay.addWidget(self.history_label)
        self.history_list = QListWidget()
        self.history_list.setMaximumHeight(110)
        self.history_list.setStyleSheet('font-size:12px;border:1px solid #e4e8ee;')
        self.history_list.itemDoubleClicked.connect(self._restore_history)
        lay.addWidget(self.history_list)
        hist_btns = QHBoxLayout()
        del_btn = QPushButton('删除选中记录')
        clear_btn = QPushButton('清空历史')
        for btn in (del_btn, clear_btn):
            btn.setStyleSheet('background:#fff;border:1px solid #d6dee7;'
                              'border-radius:4px;padding:3px 10px;')
            hist_btns.addWidget(btn)
        hist_btns.addStretch(1)
        del_btn.clicked.connect(self._confirm_delete_history)
        clear_btn.clicked.connect(self._confirm_clear_history)
        lay.addLayout(hist_btns)
        lay.addStretch(1)
        return page

    def _load_settings(self):
        s = self.settings
        self.d.setValue(float(s.value('d', 30)))
        self.torque.setValue(float(s.value('torque', 50)))
        self.hub_edit.setText(str(s.value('hub', '')))
        for combo, key, default in (
                (self.hub_material, 'material', '铸铁'),
                (self.load_type, 'load', '静载荷'),
                (self.axial_move, 'move', '否'),
                (self.centering, 'centering', '高'),
                (self.axial_force, 'axial', '否')):
            combo.setCurrentText(str(s.value(key, default)))
        self._update_summary()
        self._refresh_history()

    def _save_to_library(self):
        r = getattr(self, 'last_result', None)
        if not r:
            return
        mark = r.get('mark') or '%s %g×%g×%g' % (
            r.get('type_name', ''), r.get('b', 0),
            r.get('h', 0), r.get('L', 0))
        record = {
            'mark': mark, 'type_name': r.get('type_name', ''),
            'd': self.d.value(), 'T': self.torque.value(),
            'hub': self.hub_edit.text(),
            'material': self.hub_material.currentText(),
            'load': self.load_type.currentText(),
            'move': self.axial_move.currentText(),
            'centering': self.centering.currentText(),
            'axial': self.axial_force.currentText(),
            'time': datetime.now().strftime('%m-%d %H:%M'),
        }
        self.library_page.add(record)
        self.save_lib_btn.setText('已保存 ✓')

    def _restore_library(self, record):
        self.d.setValue(float(record.get('d', 30)))
        self.torque.setValue(float(record.get('T', 50)))
        self.hub_edit.setText(str(record.get('hub', '')))
        for combo, key, default in (
                (self.hub_material, 'material', '铸铁'),
                (self.load_type, 'load', '静载荷'),
                (self.axial_move, 'move', '否'),
                (self.centering, 'centering', '高'),
                (self.axial_force, 'axial', '否')):
            combo.setCurrentText(str(record.get(key, default)))
        self.tabs.setCurrentIndex(1)
        self.calculate()

    def _open_named_tab(self, name):
        for i in range(self.tabs.count()):
            if self.tabs.tabText(i) == name:
                self.tabs.setCurrentIndex(i)
                return

    def _open_detail(self):
        r = getattr(self, 'last_result', None)
        if not r:
            return
        typ = r.get('type', 'parallel')
        mapping = {'parallel': '平键', 'guided': '平键', 'woodruff': '半圆键',
                   'taper': '楔键', 'spline': '花键'}
        name = mapping.get(typ, '平键')
        index = next((i for i in range(self.tabs.count())
                      if self.tabs.tabText(i) == name), 0)
        self.tabs.setCurrentIndex(index)
        page = self.tabs.currentWidget()
        d = self.d.value()
        torque = self.torque.value()
        if 'd' in getattr(page, 'boxes', {}):
            page.boxes['d'].setValue(d)
        if 'T' in getattr(page, 'boxes', {}):
            page.boxes['T'].setValue(torque)
        if typ in ('parallel', 'guided'):
            page.boxes['b'].setValue(r.get('b', 0))
            page.boxes['h'].setValue(r.get('h', 0))
            page.boxes['L'].setValue(r.get('L', 0))
        elif typ == 'woodruff':
            page._refresh_woodruff()
            code = r.get('code')
            if code:
                page.combos['woodruff_code'].setCurrentText(code)
        elif typ == 'taper':
            page.boxes['hub'].setValue(r.get('hub_width', 4 * r.get('b', 8)))
            page.boxes['L'].setValue(r.get('L', 0))
        elif typ == 'spline':
            page.boxes['L'].setValue(r.get('L', 0))
        page.calculate()

    def page_setup(self):
        dlg = QDialog(self)
        dlg.setWindowTitle('PDF 页面设置')
        form = QFormLayout(dlg)
        paper = QComboBox()
        paper.addItems(['A4', 'A3'])
        paper.setCurrentText(str(self.settings.value('paper', 'A4')))
        orient = QComboBox()
        orient.addItem('纵向', 'portrait')
        orient.addItem('横向', 'landscape')
        current = str(self.settings.value('orientation', 'portrait'))
        orient.setCurrentIndex(0 if current == 'portrait' else 1)
        form.addRow('纸张', paper)
        form.addRow('方向', orient)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dlg.accept)
        buttons.rejected.connect(dlg.reject)
        form.addRow(buttons)
        if dlg.exec_() == QDialog.Accepted:
            self.settings.setValue('paper', paper.currentText())
            self.settings.setValue('orientation', orient.currentData())
            self.settings.sync()

    def _paint_result(self, p, width, height):
        margin = 80
        p.setFont(QFont('Microsoft YaHei', 16, QFont.Bold))
        p.setPen(QColor('#17202a'))
        p.drawText(width // 2 - 250, margin, 500, 50, Qt.AlignCenter,
                   '键联接选型结果')
        p.setFont(QFont('Microsoft YaHei', 10))
        p.setPen(QColor('#333333'))
        text_rect = p.viewport().adjusted(margin, margin + 70,
                                          -margin, -(height // 2))
        p.drawText(text_rect, Qt.AlignLeft | Qt.TextWordWrap,
                   self._result_text())
        pm = self.drawing.grab() if hasattr(self, 'drawing') else None
        if pm is not None and not pm.isNull():
            target = pm.rect()
            target.setWidth(width - 2 * margin)
            target.setHeight(int(target.width() * pm.height() / pm.width()))
            if target.height() > height // 2 - margin:
                target.setHeight(height // 2 - margin)
            p.drawPixmap(QRect(margin, height // 2,
                               target.width(), target.height()), pm)

    def _render_pdf(self, path):
        writer = QPdfWriter(path)
        paper = str(self.settings.value('paper', 'A4'))
        orient = str(self.settings.value('orientation', 'portrait'))
        writer.setPageSize(QPageSize(QPageSize.A3 if paper == 'A3' else QPageSize.A4))
        writer.setPageOrientation(
            QPageLayout.Landscape if orient == 'landscape' else QPageLayout.Portrait)
        writer.setResolution(150)
        p = QPainter(writer)
        try:
            self._paint_result(p, writer.width(), writer.height())
        finally:
            p.end()
        return path

    def _paint_print(self, printer):
        p = QPainter(printer)
        try:
            rect = printer.pageRect(QPrinter.DevicePixel)
            self._paint_result(p, int(rect.width()), int(rect.height()))
        finally:
            p.end()

    def print_preview(self):
        printer = QPrinter(QPrinter.HighResolution)
        dialog = QPrintPreviewDialog(printer, self)
        dialog.setWindowTitle('键选型结果打印预览')
        dialog.paintRequested.connect(self._paint_print)
        dialog.exec_()

    def export_pdf(self):
        path, _ = QFileDialog.getSaveFileName(
            self, '导出键选型 PDF', '键选型结果.pdf', 'PDF (*.pdf)')
        if not path:
            return
        if not path.lower().endswith('.pdf'):
            path += '.pdf'
        self._render_pdf(path)

    @staticmethod
    def _help_text():
        return (
            '键联接选型工具\n\n'
            '1. 普通平键：GB/T 1096-2003\n'
            '   键宽 h8，键高 h11，键长 h14；\n'
            '   轴槽 N9，毂槽 JS9。\n\n'
            '2. 半圆键：GB/T 1099.1-2003\n'
            '   键宽 h9，键高 h11，键径 h12。\n\n'
            '3. 楔键：GB/T 1564/1565-2003\n'
            '   普通 A/B、钩头；键宽 h9，键高 h11，键长 h14。\n\n'
            '4. 矩形花键：GB/T 1144-2001\n'
            '   齿侧定心 H7/f7；外径定心 H7/h6；内径定心 H7/g6。\n\n'
            '5. 校核公式\n'
            '   平键挤压：σp = 2T/[d(h/2)(L-b)]\n'
            '   平键剪切：τ = 2T/[d b (L-b)]\n'
            '   楔键：σp = 12T/[b l (6μd+b)]\n'
            '   花键：p = 2T/(0.75 N h l dm)\n\n'
            '6. 键材料许用剪切应力\n'
            '   45钢 60 MPa；40Cr 70 MPa；不锈钢 50 MPa。\n\n'
            '7. 说明\n'
            '   结果仅供参考，最终设计须结合工况、安全系数、'
            '加工精度和现行标准由专业工程师确认。'
        )

    def show_help(self):
        dlg = QDialog(self)
        dlg.setWindowTitle('键联接帮助')
        dlg.resize(560, 520)
        lay = QVBoxLayout(dlg)
        browser = QTextBrowser()
        browser.setPlainText(self._help_text())
        browser.setStyleSheet('font-size:13px;')
        lay.addWidget(browser)
        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(dlg.reject)
        buttons.accepted.connect(dlg.accept)
        lay.addWidget(buttons)
        dlg.exec_()

    def _result_text(self):
        page = self.tabs.currentWidget()
        if page is None:
            return ''
        if self.tabs.currentIndex() == 1:
            parts = [self.type_line.text(), self.result_title.text(),
                     self.result_text.text(), self.mark.text(),
                     self.why.text()]
        elif hasattr(page, 'result'):
            parts = [page.result.text()]
        elif hasattr(page, 'summary'):
            parts = [page.summary.text()]
            for lab in page.findChildren(QLabel):
                if lab.text() and lab not in (page.summary,):
                    parts.append(lab.text())
        else:
            parts = [lab.text() for lab in page.findChildren(QLabel)
                     if lab.text()]
        return '\n'.join(x for x in parts if x and x != '—')

    def copy_result(self):
        QApplication.clipboard().setText(self._result_text())

    def _result_rows(self):
        rows = [('页面', self.tabs.tabText(self.tabs.currentIndex()))]
        page = self.tabs.currentWidget()
        r = getattr(self, 'last_result', None) if self.tabs.currentIndex() == 1 else getattr(page, 'last_result', None)
        if r:
            rows += [('键型', r.get('type_name', r.get('kind', ''))),
                     ('规格', r.get('mark', r.get('code', r.get('spec', '')))),
                     ('键宽 b (mm)', r.get('b', '')),
                     ('键高 h (mm)', r.get('h', '')),
                     ('键长 L (mm)', r.get('L', '')),
                     ('键材料', r.get('key_material', '45钢')),
                     ('挤压应力 MPa', round(r.get('sigma_p', r.get('p', 0)), 2)),
                     ('许用应力 MPa', r.get('allowable_p', r.get('allowable', ''))),
                     ('许用剪切 MPa', r.get('allowable_tau', '')),
                     ('通过', '是' if r.get('safe') else '否')]
            tol_text = format_tolerance_rows(r.get('tolerances', []))
            if tol_text:
                rows.append(('公差', tol_text))
        else:
            rows.append(('结果', self._result_text()))
        return rows

    def export_result(self):
        path, _ = QFileDialog.getSaveFileName(
            self, '导出键选型结果', '键选型结果.txt',
            'Text (*.txt);;CSV (*.csv)')
        if not path:
            return
        if path.lower().endswith('.csv'):
            with open(path, 'w', encoding='utf-8-sig', newline='') as fh:
                writer = csv.writer(fh)
                writer.writerow(['项目', '值'])
                writer.writerows(self._result_rows())
        else:
            with open(path, 'w', encoding='utf-8-sig') as fh:
                fh.write(self._result_text())

    def _history(self):
        raw = self.settings.value('history', '[]')
        try:
            data = json.loads(raw)
        except (TypeError, ValueError):
            data = []
        return data if isinstance(data, list) else []

    def _add_history(self, r):
        mark = r.get('mark')
        if not mark:
            if r.get('type') == 'spline':
                mark = '花键 %s' % r.get('spec', '')
            else:
                mark = '%s %g×%g×%g' % (
                    r.get('type_name', ''), r.get('b', 0),
                    r.get('h', 0), r.get('L', 0))
        entry = {
            'text': '%s · d=%g · T=%g N·m' % (
                mark, self.d.value(), self.torque.value()),
            'time': datetime.now().strftime('%m-%d %H:%M'),
            'd': self.d.value(), 'torque': self.torque.value(),
            'hub': self.hub_edit.text(),
            'material': self.hub_material.currentText(),
            'load': self.load_type.currentText(),
            'move': self.axial_move.currentText(),
            'centering': self.centering.currentText(),
            'axial': self.axial_force.currentText(),
        }
        data = self._history()
        if data and data[0].get('text') == entry['text']:
            return
        data.insert(0, entry)
        self._write_history(data[:8])

    def _write_history(self, data):
        self.settings.setValue('history', json.dumps(data[:8], ensure_ascii=False))
        self.settings.sync()
        self._refresh_history()

    def _confirm_delete_history(self):
        if QMessageBox.question(
                self, '删除记录', '确定删除选中的历史记录？',
                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            self._delete_history()

    def _confirm_clear_history(self):
        if QMessageBox.question(
                self, '清空历史', '确定清空全部历史记录？',
                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            self._clear_history()

    def _delete_history(self):
        row = self.history_list.currentRow()
        data = self._history()
        if 0 <= row < len(data):
            data.pop(row)
            self._write_history(data)

    def _clear_history(self):
        self._write_history([])

    def _restore_history(self, item):
        row = self.history_list.row(item)
        data = self._history()
        if row < 0 or row >= len(data):
            return
        entry = data[row]
        self.d.setValue(float(entry.get('d', 30)))
        self.torque.setValue(float(entry.get('torque', 50)))
        self.hub_edit.setText(str(entry.get('hub', '')))
        for combo, key, default in (
                (self.hub_material, 'material', '铸铁'),
                (self.load_type, 'load', '静载荷'),
                (self.axial_move, 'move', '否'),
                (self.centering, 'centering', '高'),
                (self.axial_force, 'axial', '否')):
            combo.setCurrentText(str(entry.get(key, default)))
        self.tabs.setCurrentIndex(1)
        self.calculate()

    def _refresh_history(self):
        if not hasattr(self, 'history_label'):
            return
        self.history_list.clear()
        data = self._history()
        if not data:
            self.history_label.setText('最近选型：暂无记录。')
            return
        lines = ['最近选型：']
        for item in data[:5]:
            lines.append('%s  %s' % (item.get('time', ''), item.get('text', '')))
        self.history_label.setText('\n'.join(lines))
        for item in data[:8]:
            self.history_list.addItem('%s  %s' % (
                item.get('time', ''), item.get('text', '')))
        self.history_list.setVisible(bool(data))

    def _save_settings(self):
        s = self.settings
        s.setValue('d', self.d.value())
        s.setValue('torque', self.torque.value())
        s.setValue('hub', self.hub_edit.text())
        s.setValue('material', self.hub_material.currentText())
        s.setValue('load', self.load_type.currentText())
        s.setValue('move', self.axial_move.currentText())
        s.setValue('centering', self.centering.currentText())
        s.setValue('axial', self.axial_force.currentText())
        s.sync()

    def _label(self, text, size=13, color='#333', bold=False):
        lab = QLabel(text)
        lab.setStyleSheet('font-size:%dpx;color:%s;%s'
                          % (size, color, 'font-weight:bold;' if bold else ''))
        return lab

    def _spin(self, value, maximum, suffix=''):
        box = QDoubleSpinBox()
        box.setRange(0.001, maximum)
        box.setDecimals(2)
        box.setValue(value)
        box.setSuffix(suffix)
        box.setMinimumWidth(220)
        box.setKeyboardTracking(False)
        return box

    def _build_smart(self):
        page = QWidget()
        outer = QVBoxLayout(page)
        outer.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        content = QWidget()
        lay = QVBoxLayout(content)
        lay.setContentsMargins(16, 14, 16, 14)
        lay.setSpacing(10)

        inp = QFrame()
        inp.setStyleSheet('QFrame{background:#fff;border:1px solid #d6dee7;'
                          'border-radius:6px;}')
        iv = QHBoxLayout(inp)
        iv.setContentsMargins(14, 12, 14, 12)
        iv.setSpacing(10)
        iv.addWidget(self._label('轴径 d (mm)：', 13))
        self.d = self._spin(30, 500)
        iv.addWidget(self.d)
        iv.addSpacing(14)
        iv.addWidget(self._label('传递扭矩 T (N·m)：', 13))
        self.torque = self._spin(50, 100000)
        iv.addWidget(self.torque)
        iv.addStretch(1)
        btn = QPushButton('智能推荐')
        btn.setStyleSheet('background:#6c5ce7;color:white;border:none;'
                          'border-radius:5px;padding:8px 20px;'
                          'font-weight:bold;')
        btn.clicked.connect(self.calculate)
        iv.addWidget(btn)
        lay.addWidget(inp)

        # 可展开参数面板
        param_head = QHBoxLayout()
        param_head.setSpacing(10)
        self.param_toggle = QPushButton('收起参数 ▲')
        self.param_toggle.setStyleSheet(
            'background:#f5f7fa;border:1px solid #d6dee7;border-radius:4px;'
            'padding:4px 10px;color:#555;')
        self.param_toggle.clicked.connect(self._toggle_params)
        param_head.addWidget(self.param_toggle)
        self.param_summary = QLabel('')
        self.param_summary.setStyleSheet('color:#6c5ce7;font-size:12px;')
        param_head.addWidget(self.param_summary)
        param_head.addStretch(1)
        lay.addLayout(param_head)

        self.param_panel = QFrame()
        self.param_panel.setStyleSheet(
            'QFrame{background:#fafbfc;border:1px solid #e4e8ee;'
            'border-radius:4px;}')
        pg = QGridLayout(self.param_panel)
        pg.setContentsMargins(12, 10, 12, 10)
        pg.setHorizontalSpacing(16)
        pg.setVerticalSpacing(8)
        self.load_type = QComboBox()
        self.load_type.addItems(['静载荷', '轻微冲击', '冲击'])
        self.hub_material = QComboBox()
        self.hub_material.addItems(['钢', '铸铁'])
        self.hub_material.setCurrentText('铸铁')
        self.axial_move = QComboBox()
        self.axial_move.addItems(['否', '是'])
        self.centering = QComboBox()
        self.centering.addItems(['高', '一般', '低'])
        self.centering.setCurrentText('高')
        self.axial_force = QComboBox()
        self.axial_force.addItems(['否', '是'])
        self.hub_edit = QLineEdit()
        self.hub_edit.setPlaceholderText('空 = 按 4×键宽估算')
        self.hub_edit.setStyleSheet('background:#fff;border:1px solid #d6dee7;'
                                    'border-radius:4px;padding:4px 8px;')
        fields = [
            ('载荷性质', self.load_type), ('轮毂材料', self.hub_material),
            ('需要轴向移动', self.axial_move), ('对中性要求', self.centering),
            ('需承受轴向力', self.axial_force), ('轮毂宽度 B (mm, 可空):', self.hub_edit),
        ]
        for i, (label, widget) in enumerate(fields):
            row, col = divmod(i, 2)
            pg.addWidget(self._label(label, 12, '#555'), row, col * 2)
            pg.addWidget(widget, row, col * 2 + 1)
        pg.setColumnStretch(1, 1)
        pg.setColumnStretch(3, 1)
        lay.addWidget(self.param_panel)

        for combo in (self.load_type, self.hub_material, self.axial_move,
                      self.centering, self.axial_force):
            combo.currentTextChanged.connect(self._param_changed)
        self.hub_edit.editingFinished.connect(self._param_changed)
        self._update_summary()

        # 下方两栏：左“为什么是它”，右“选型结果数据”
        cols = QHBoxLayout()
        cols.setSpacing(12)
        why = QFrame()
        why.setStyleSheet('QFrame{background:#fff;border:1px solid #d6dee7;'
                          'border-radius:6px;}')
        wv = QVBoxLayout(why)
        wv.setContentsMargins(16, 10, 16, 10)
        wv.addWidget(self._label('为什么是它', 13, '#555', True))
        self.why = QLabel('对中性好、装拆方便\n'
                          '齿轮/带轮/蜗轮与轴的连接最常用。')
        self.why.setStyleSheet('font-size:13px;color:#17202a;')
        self.why.setWordWrap(True)
        wv.addWidget(self.why)
        wv.addStretch(1)
        cols.addWidget(why, 1)

        card = QFrame()
        card.setStyleSheet('QFrame{background:#fff;border:1px solid #d6dee7;'
                           'border-radius:6px;}')
        card.setMinimumWidth(430)
        cv = QVBoxLayout(card)
        cv.setContentsMargins(18, 14, 18, 14)
        cv.setSpacing(8)
        cv.addWidget(self._label('GB/T 1096-2003 平键选型结果', 13,
                                 '#555', True))
        self.type_line = QLabel('')
        self.type_line.setStyleSheet('font-size:13px;color:#6c5ce7;'
                                    'font-weight:bold;')
        cv.addWidget(self.type_line)
        self.result_title = QLabel('')
        self.result_title.setStyleSheet(
            'font-size:15px;font-weight:bold;color:#17202a;')
        cv.addWidget(self.result_title)
        self.result_text = QLabel('—')
        self.result_text.setStyleSheet(
            'font-size:13px;color:#17202a;line-height:1.7;')
        self.result_text.setWordWrap(True)
        self.result_text.setTextFormat(Qt.PlainText)
        cv.addWidget(self.result_text)
        self.mark = QLabel('')
        self.mark.setStyleSheet('font-size:13px;color:#17202a;'
                                'font-weight:bold;padding-top:6px;')
        cv.addWidget(self.mark)
        self.disclaimer = QLabel(
            '⚠ 仅供参考，不作为最终设计依据。\n'
            '数据来源：GB/T 1096/1099.1/1564/1565/1144/1095 + '
            '机械设计手册推荐值。')
        self.disclaimer.setWordWrap(True)
        self.disclaimer.setStyleSheet('font-size:11px;color:#a15c00;')
        cv.addWidget(self.disclaimer)
        self.open_detail_btn = QPushButton('转到校核页')
        self.open_detail_btn.setStyleSheet(
            'background:#6c5ce7;color:white;border:none;border-radius:4px;'
            'padding:5px 14px;')
        self.open_detail_btn.clicked.connect(self._open_detail)
        self.save_lib_btn = QPushButton('保存到库')
        self.save_lib_btn.setStyleSheet(
            'background:#fff;color:#6c5ce7;border:1px solid #6c5ce7;'
            'border-radius:4px;padding:4px 14px;')
        self.save_lib_btn.clicked.connect(self._save_to_library)
        btn_row = QHBoxLayout()
        btn_row.addWidget(self.open_detail_btn)
        btn_row.addWidget(self.save_lib_btn)
        btn_row.addStretch(1)
        cv.addLayout(btn_row)
        cv.addStretch(1)
        cols.addWidget(card, 1)
        lay.addLayout(cols)

        dw = QFrame()
        dw.setStyleSheet('QFrame{background:#fff;border:1px solid #d6dee7;'
                         'border-radius:6px;}')
        dv = QVBoxLayout(dw)
        dv.setContentsMargins(8, 8, 8, 8)
        dv.addWidget(self._label('键联接剖面图', 13, '#555', True))
        self.drawing = KeyDrawing()
        dv.addWidget(self.drawing)
        lay.addWidget(dw)
        lay.addStretch(1)
        scroll.setWidget(content)
        outer.addWidget(scroll)
        return page

    def _toggle_params(self):
        visible = not self.param_panel.isVisible()
        self.param_panel.setVisible(visible)
        self.param_toggle.setText('收起参数 ▲' if visible else '更改参数 ▾')

    def _param_changed(self, *_):
        self._update_summary()
        if self.param_panel.isVisible():
            self.calculate()

    def _update_summary(self):
        self.param_summary.setText(
            '已改工况：%s · %s · %s轴向移动 · %s对中 · %s轴向力'
            % (self.load_type.currentText(), self.hub_material.currentText(),
               '无' if self.axial_move.currentText() == '否' else '有',
               self.centering.currentText(),
               '无' if self.axial_force.currentText() == '否' else '有'))

    def calculate(self):
        d, torque = self.d.value(), self.torque.value()
        text = self.hub_edit.text().strip()
        try:
            hub = float(text) if text else None
            r = smart_design(
                d, torque, hub, self.hub_material.currentText(),
                self.load_type.currentText(),
                self.axial_move.currentText() == '是',
                self.centering.currentText(),
                self.axial_force.currentText() == '是')
        except ValueError as exc:
            self.type_line.setText('参数错误')
            self.result_text.setText(str(exc))
            self.mark.setText('')
            return None
        self.last_result = r
        self.type_line.setText('推荐键型：%s' % r['type_name'])
        if hasattr(self, 'home_last'):
            self.home_last.setText(
                '当前结果：%s\n%s' % (r['type_name'], r.get('mark',
                '键 %d×%d×%d' % (r.get('b', 0), r.get('h', 0), r.get('L', 0)))))
            self._add_history(r)
        if r['type'] in ('parallel', 'guided'):
            self.result_title.setText(
                '键 %d×%d×%d　GB/T 1096-2003' % (r['b'], r['h'], r['L']))
            self.result_text.setText(
                '轴径：%.1f mm\n键截面：b×h = %d×%d mm\n'
                '键槽深度：轴槽 t1=%.1f mm，毂槽 t2=%.1f mm\n'
                '轮毂宽度：%s → 建议键长 L = %d mm\n'
                '公差：键宽 %s，键高 %s，键长 %s'
                % (d, r['b'], r['h'], r['t1'], r['t2'],
                   ('按 4×键宽估算（%.0f mm）' % r['hub_width'])
                   if r['hub_auto'] else ('%.0f mm' % r['hub_width']),
                   r['L'], r['tol']['b'], r['tol']['h'], r['tol']['L']))
            self.mark.setText('标记示例：键B %d×%d×%d GB/T 1096-2003'
                              % (r['b'], r['h'], r['L']))
            self.why.setText(
                '%s\n挤压应力 %.1f / %.0f MPa（%.1f%%）\n'
                '联结：%s，键宽 %s，轴槽 %s，毂槽 %s'
                % (r['reason'], r['sigma_p'], r['allowable_p'],
                   r['ratio'], r['fit_name'], r['fit_key'],
                   r['fit_shaft'], r['fit_hub']))
            self.drawing.setVisible(True)
            self.drawing.set_data(r['b'], r['h'], r['L'], r['t1'], r['t2'], d,
                                  kind=r['type'])
        elif r['type'] == 'taper':
            self.result_title.setText('普通楔键　GB/T 1564-2003')
            self.result_text.setText(
                '轴径：%.1f mm\n键宽：%d mm\n键长：%g mm\n'
                '挤压应力：%.2f / %.0f MPa（%.1f%%）'
                % (d, r['b'], r['L'], r['sigma_p'], r['allowable'],
                   r['ratio']))
            self.mark.setText('标记示例：键 %d×%g GB/T 1564-2003'
                              % (r['b'], r['L']))
            self.why.setText('%s\n%s' % (r['reason'],
                                         '通过' if r['safe'] else '不通过'))
            self.drawing.setVisible(True)
            depth = keyway_depth(d)
            self.drawing.set_data(r['b'], max(4, r['b'] * 0.8), r['L'],
                                  depth['t1'], depth['t2'], d, kind='taper',
                                  spec=r['kind'])
        else:
            self.result_title.setText('矩形花键　GB/T 1144-2001')
            self.result_text.setText(
                '轴径：%.1f mm\n花键规格：%s\n'
                '结合长度：%g mm\n挤压应力：%.2f / %.0f MPa（%.1f%%）'
                % (d, r['spec'], r['L'], r['p'], r['allowable'],
                   r['ratio']))
            self.mark.setText('标记示例：%s GB/T 1144-2001' % r['spec'])
            self.why.setText('%s\n%s' % (r['reason'],
                                         '通过' if r['safe'] else '不通过'))
            self.drawing.setVisible(True)
            self.drawing.set_data(r['B'], r['h'], r['L'], 0, 0, d,
                                  kind='spline', spec=r)
        tol_text = format_tolerance_rows(r.get('tolerances', []))
        if tol_text:
            self.result_text.setText(
                self.result_text.text() + '\n' + tol_text)
        self._save_settings()
        return r
