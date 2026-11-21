# -*- coding: utf-8 -*-
"""左侧标准树面板。"""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLineEdit, QTreeWidget, QVBoxLayout, QWidget


def build_tree_panel(win):
    treew = QWidget()
    treew.setFixedWidth(220)
    treew.setStyleSheet('background:#fff;')
    tv = QVBoxLayout(treew)
    tv.setContentsMargins(8, 8, 8, 8)
    tv.setSpacing(6)
    win.treeSearch = QLineEdit()
    win.treeSearch.setObjectName('treeSearch')
    win.treeSearch.setPlaceholderText('搜索标准 / 类型（DN/PN 用筛选器）')
    win.treeSearch.textChanged.connect(win.filter_tree)
    tv.addWidget(win.treeSearch)
    win.tree = QTreeWidget()
    win.tree.setObjectName('tree')
    win.tree.setHeaderHidden(True)
    win.tree.itemClicked.connect(win.on_tree)
    tv.addWidget(win.tree, 1)
    return treew
