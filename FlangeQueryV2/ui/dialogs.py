# -*- coding: utf-8 -*-
"""搜索、标准覆盖对话框（Model/View）。"""

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import (QAbstractItemView, QDialog, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QTableView, QVBoxLayout,
                             QHeaderView)

from core.review import REVIEW_LABELS, STANDARDS_COVERAGE


class SearchDialog(QDialog):
    """全库搜索 / 尺寸反查：跨标准查尺寸，双击结果跳转。"""

    row_chosen = pyqtSignal(str, dict)

    def __init__(self, search_fn, parent=None):
        super().__init__(parent)
        self._search = search_fn
        self._cache = {}
        self.setWindowTitle('全库搜索 / 尺寸反查')
        self.resize(880, 560)
        layout = QVBoxLayout(self)
        row = QHBoxLayout()
        self.query = QLineEdit()
        self.query.setPlaceholderText('如：DN50、K=125、n=4、PN16、不锈钢')
        btn = QPushButton('搜索')
        btn.clicked.connect(self.run_search)
        row.addWidget(self.query, 1)
        row.addWidget(btn)
        layout.addLayout(row)
        layout.addWidget(QLabel(
            '支持“列=值”精确反查（如 K=125、n=4）与关键字搜索；双击结果跳转。'))
        self.model = QStandardItemModel(0, 5, self)
        self.model.setHorizontalHeaderLabels(
            ['标准', '类型', '压力/等级', 'DN', '匹配条件'])
        self.table = QTableView()
        self.table.setModel(self.model)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.doubleClicked.connect(self._choose)
        layout.addWidget(self.table, 1)
        self.status = QLabel('')
        layout.addWidget(self.status)
        self.query.returnPressed.connect(self.run_search)
        self.query.setFocus()

    def run_search(self):
        text = self.query.text().strip()
        if not text:
            self.status.setText('请输入查询内容')
            return
        results = self._search(text, limit=300, cache=self._cache)
        self.table.setSortingEnabled(False)
        self.model.clear()
        self.model.setHorizontalHeaderLabels(
            ['标准', '类型', '压力/等级', 'DN', '匹配条件'])
        for i, (std, name, csvf, row, summary) in enumerate(results):
            pn = (row.get('Class') and ('Class ' + row['Class'])) \
                or row.get('PN', '') or ''
            values = [std, name, pn, row.get('DN', ''), summary]
            for j, value in enumerate(values):
                item = QStandardItem(str(value or ''))
                item.setTextAlignment(Qt.AlignCenter)
                if j == 0:
                    item.setData((csvf, row), Qt.UserRole)
                self.model.setItem(i, j, item)
        self.table.setSortingEnabled(True)
        self.table.resizeColumnsToContents()
        self.status.setText('共 %d 条结果%s'
                            % (len(results),
                               '（已截断，请缩小条件）' if len(results) >= 300 else ''))

    def _choose(self, index):
        item = self.model.item(index.row(), 0)
        if item is None:
            return
        data = item.data(Qt.UserRole)
        if data:
            self.row_chosen.emit(data[0], data[1])
            self.accept()


class CoverageDialog(QDialog):
    """标准覆盖矩阵：哪些标准已收录、覆盖范围、复核状态与缺口。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('标准覆盖与数据复核状态')
        self.resize(1000, 580)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(
            '“已核对”仅表示数据来自对应标准 PDF 全文；'
            '“部分核对/推断/来源待复核”请在使用前按正式标准复核。'))
        self.model = QStandardItemModel(len(STANDARDS_COVERAGE), 5, self)
        self.model.setHorizontalHeaderLabels(
            ['标准号', '名称', '收录范围', '状态', '说明'])
        table = QTableView()
        table.setModel(self.model)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.verticalHeader().setVisible(False)
        for i, (no, name, scope, status, note) in enumerate(STANDARDS_COVERAGE):
            values = [no, name, scope, REVIEW_LABELS.get(status, status), note]
            for j, value in enumerate(values):
                item = QStandardItem(value)
                item.setTextAlignment(Qt.AlignCenter)
                if status in ('missing', 'alias'):
                    item.setForeground(QColor('#a15c00'))
                self.model.setItem(i, j, item)
        table.resizeRowsToContents()
        table.setColumnWidth(0, 150)
        table.setColumnWidth(1, 240)
        table.setColumnWidth(2, 170)
        table.setColumnWidth(3, 90)
        table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        table.setWordWrap(True)
        layout.addWidget(table, 1)
        close = QPushButton('关闭')
        close.clicked.connect(self.accept)
        layout.addWidget(close, 0, Qt.AlignRight)
