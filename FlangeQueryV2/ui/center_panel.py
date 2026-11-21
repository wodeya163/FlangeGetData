# -*- coding: utf-8 -*-
"""中间筛选条 + 数据表区域。"""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QAbstractItemView, QAction, QFrame, QHBoxLayout,
                             QHeaderView, QLabel, QVBoxLayout, QWidget)

from ui.data_table import DataTable


def build_center_panel(win):
    center = QWidget()
    center.setObjectName('center')
    cv = QVBoxLayout(center)
    cv.setContentsMargins(0, 0, 0, 0)
    cv.setSpacing(0)
    selbar = QFrame()
    selbar.setObjectName('selbar')
    sv = QVBoxLayout(selbar)
    sv.setContentsMargins(14, 5, 14, 5)
    sv.setSpacing(4)
    win.frow = QHBoxLayout()
    win.frow.setSpacing(8)
    win.frow.setContentsMargins(0, 0, 0, 0)
    sv.addLayout(win.frow)
    win.frow2 = QHBoxLayout()
    win.frow2.setSpacing(6)
    win.frow2.setContentsMargins(0, 0, 0, 0)
    win.chips = QLabel('')
    win.chips.setStyleSheet('color:#1f4e79;font-size:11px;background:transparent;')
    win.frow2.addWidget(win.chips)
    win.frow2.addStretch(1)
    win.count_lab = QLabel('')
    win.count_lab.setStyleSheet('color:#888;font-size:12px;'
                                'background:transparent;')
    win.frow2.addWidget(win.count_lab)
    sv.addLayout(win.frow2)
    win.filter_widgets = {}
    win.range_widgets = {}
    win._filter_labels = []
    cv.addWidget(selbar)
    inner = QWidget()
    inner.setStyleSheet('background:#fff;')
    iv = QVBoxLayout(inner)
    iv.setContentsMargins(14, 10, 14, 10)
    iv.setSpacing(8)
    win.cap = QLabel('')
    win.cap.setObjectName('cap')
    iv.addWidget(win.cap)
    win.table = DataTable()
    win.table.setSelectionBehavior(QAbstractItemView.SelectRows)
    win.table.setSelectionMode(QAbstractItemView.ExtendedSelection)
    win.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
    win.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
    win.table.verticalHeader().setVisible(False)
    win.table.setShowGrid(True)
    win.table.itemSelectionChanged.connect(win.on_row)
    win.table.setSortingEnabled(True)
    win.table.setContextMenuPolicy(Qt.CustomContextMenu)
    win.table.customContextMenuRequested.connect(win.show_table_menu)
    win.copy_action = QAction('复制选中行', win)
    win.copy_action.setShortcut('Ctrl+C')
    win.copy_action.setShortcutContext(Qt.WidgetWithChildrenShortcut)
    win.copy_action.triggered.connect(win.copy_selected_rows)
    win.table.addAction(win.copy_action)
    iv.addWidget(win.table, 1)
    cv.addWidget(inner, 1)
    return center
