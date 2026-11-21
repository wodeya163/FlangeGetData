# -*- coding: utf-8 -*-
"""轴承三维模型/图纸收藏库。"""

import os

from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import (QComboBox, QDialog, QDialogButtonBox,
                             QFileDialog, QFormLayout, QHBoxLayout,
                             QLabel, QLineEdit, QMessageBox, QPushButton,
                             QTableWidget, QTableWidgetItem, QVBoxLayout,
                             QWidget)

from core.bearing_data_table import DEEP_GROOVE
from core.bearing_library import load_lib, save_lib


class ModelDialog(QDialog):
    def __init__(self, parent=None, code='', data=None):
        super().__init__(parent)
        self.setWindowTitle('登记轴承模型/资料')
        self.setMinimumWidth(520)
        form = QFormLayout(self)
        self.code = QComboBox()
        self.code.setEditable(True)
        self.code.addItems(sorted(DEEP_GROOVE.keys()))
        if code:
            self.code.setCurrentText(code)
        self.three_d = QLineEdit()
        self.drawing = QLineEdit()
        self.supplier = QLineEdit()
        self.url = QLineEdit()
        self.note = QLineEdit()
        for label, edit, kind in [
                ('型号', self.code, None),
                ('三维模型', self.three_d, '3D'),
                ('图纸', self.drawing, '图纸'),
                ('供应商', self.supplier, None),
                ('购买/下载地址', self.url, None),
                ('备注', self.note, None)]:
            if kind:
                row = QHBoxLayout()
                row.addWidget(edit, 1)
                btn = QPushButton('浏览')
                btn.clicked.connect(lambda _, e=edit: self._browse(e))
                row.addWidget(btn)
                form.addRow(label, row)
            else:
                form.addRow(label, edit)
        data = data or {}
        self.three_d.setText(data.get('three_d', ''))
        self.drawing.setText(data.get('drawing', ''))
        self.supplier.setText(data.get('supplier', ''))
        self.url.setText(data.get('url', ''))
        self.note.setText(data.get('note', ''))
        buttons = QDialogButtonBox(QDialogButtonBox.Ok |
                                   QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)

    def _browse(self, edit):
        path, _ = QFileDialog.getOpenFileName(self, '选择文件')
        if path:
            edit.setText(path)

    def values(self):
        return {
            'model': self.code.currentText().strip(),
            'three_d': self.three_d.text().strip(),
            'drawing': self.drawing.text().strip(),
            'supplier': self.supplier.text().strip(),
            'url': self.url.text().strip(),
            'note': self.note.text().strip(),
        }


class BearingLibraryTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.resources = load_lib()
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 10, 0, 0)
        root.setSpacing(8)
        tip = QLabel('只登记本地文件路径，不复制模型本体；可收藏 STEP/STL/IGES、'
                     '图纸、供应商和购买地址。')
        tip.setStyleSheet('font-size:12px;color:#667085;')
        root.addWidget(tip)
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(
            ['型号', '三维模型', '图纸', '供应商', '地址', '备注'])
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setStyleSheet(
            'QTableWidget{background:#fff;border:1px solid #d6dee7;'
            'font-size:12px;} QHeaderView::section{background:#eef3f8;'
            'padding:4px;font-weight:bold;}')
        root.addWidget(self.table, 1)
        row = QHBoxLayout()
        for text, slot in [('登记 / 编辑', self._edit),
                           ('打开三维', lambda: self._open('three_d')),
                           ('打开图纸', lambda: self._open('drawing')),
                           ('删除', self._delete)]:
            btn = QPushButton(text)
            btn.setMinimumHeight(30)
            btn.clicked.connect(slot)
            row.addWidget(btn)
        row.addStretch(1)
        root.addLayout(row)
        self.reload()

    def reload(self):
        self.table.setRowCount(0)
        for code in sorted(self.resources):
            data = self.resources[code]
            r = self.table.rowCount()
            self.table.insertRow(r)
            self.table.setItem(r, 0, QTableWidgetItem(code))
            for j, key in enumerate(['three_d', 'drawing', 'supplier',
                                     'url', 'note'], start=1):
                val = data.get(key, '')
                text = os.path.basename(val) if key in ('three_d',
                                                        'drawing') and val else val
                self.table.setItem(r, j, QTableWidgetItem(text))
        self.table.resizeColumnsToContents()

    def _selected(self):
        row = self.table.currentRow()
        if row < 0:
            return None
        item = self.table.item(row, 0)
        return item.text() if item else None

    def _edit(self):
        code = self._selected() or ''
        dlg = ModelDialog(self, code, self.resources.get(code))
        if dlg.exec_() != QDialog.Accepted:
            return
        vals = dlg.values()
        if not vals['model']:
            QMessageBox.warning(self, '提示', '请填写型号')
            return
        self.resources[vals['model']] = {
            'three_d': vals['three_d'], 'drawing': vals['drawing'],
            'supplier': vals['supplier'], 'url': vals['url'],
            'note': vals['note'], 'group': self.resources.get(
                vals['model'], {}).get('group', '')}
        save_lib(self.resources)
        self.reload()

    def _open(self, key):
        code = self._selected()
        if not code:
            QMessageBox.information(self, '提示', '请先选择一个型号')
            return
        path = self.resources.get(code, {}).get(key, '')
        if not path or not os.path.isfile(path):
            QMessageBox.warning(self, '提示', '文件不存在，请重新登记')
            return
        QDesktopServices.openUrl(QUrl.fromLocalFile(path))

    def _delete(self):
        code = self._selected()
        if not code:
            return
        if QMessageBox.question(self, '删除', '删除 %s 的收藏记录？' % code) \
                != QMessageBox.Yes:
            return
        self.resources.pop(code, None)
        save_lib(self.resources)
        self.reload()
