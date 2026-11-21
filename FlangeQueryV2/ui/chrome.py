# -*- coding: utf-8 -*-
"""顶栏与分类工具条。"""

import os

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton


def build_topbar(win, app_name, version, tagline=''):
    top = QFrame()
    top.setObjectName('top')
    top.setFixedHeight(44)
    tv = QHBoxLayout(top)
    tv.setContentsMargins(14, 0, 14, 0)
    tv.setSpacing(14)
    logo = QLabel(app_name)
    logo.setObjectName('logo')
    ver = QLabel(version)
    ver.setObjectName('ver')
    sub = QLabel(tagline or '法兰管件 · 管道附件 · 机械选型 · 离线查询')
    sub.setObjectName('subtitle')
    tv.addWidget(logo)
    tv.addWidget(ver)
    tv.addWidget(sub)
    tv.addStretch(1)
    b0 = QPushButton('🔍 搜索')
    b1 = QPushButton('🖨 打印预览')
    b2 = QPushButton('📤 导出数据')
    b3 = QPushButton('ℹ 关于')
    b4 = QPushButton('📚 标准')
    b5 = QPushButton('📐 矢量图')
    for button in (b0, b1, b2, b3, b4, b5):
        button.setProperty('class', 'topbtn')
        button.setCursor(Qt.PointingHandCursor)
    b0.clicked.connect(win.show_search)
    b1.clicked.connect(win.do_print)
    b2.clicked.connect(win.do_export)
    b3.clicked.connect(win.show_about)
    b4.clicked.connect(win.show_coverage)
    b5.clicked.connect(win.do_export_vector)
    tv.addWidget(b0)
    tv.addWidget(b4)
    tv.addWidget(b1)
    tv.addWidget(b2)
    tv.addWidget(b5)
    tv.addWidget(b3)
    return top


def build_tools(win, tabs, tpl_dir):
    tools = QFrame()
    tools.setObjectName('tools')
    tools.setFixedHeight(36)
    tv = QHBoxLayout(tools)
    tv.setContentsMargins(12, 0, 12, 0)
    tv.setSpacing(8)
    win.tab_group = []
    for i, (name, _) in enumerate(tabs):
        button = QPushButton(name)
        button.setCheckable(True)
        button.setProperty('class', 'tab')
        button.setCursor(Qt.PointingHandCursor)
        button.clicked.connect(lambda _, ix=i: win.on_tab(ix))
        if i == 0:
            button.setChecked(True)
        win.tab_group.append(button)
        tv.addWidget(button)
    tv.addStretch(1)
    count = (len([n for n in os.listdir(tpl_dir) if n.lower().endswith('.bmp')])
             if os.path.isdir(tpl_dir) else 0)
    tv.addWidget(QLabel('数据源：CSV 本地库 · %d 类图形模板' % count))
    return tools
