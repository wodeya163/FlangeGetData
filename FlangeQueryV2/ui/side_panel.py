# -*- coding: utf-8 -*-
"""右侧图形/尺寸侧栏。"""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QFrame, QHBoxLayout, QLabel, QPushButton,
                             QScrollArea, QVBoxLayout, QWidget)

from ui.drawing_card import DrawingCard
from ui.kv_panel import KvPanel


def build_side_panel(win):
    side = QScrollArea()
    side.setObjectName('side')
    side.setFixedWidth(430)
    side.setWidgetResizable(True)
    side.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    inner_side = QWidget()
    inner_side.setObjectName('side')
    sv2 = QVBoxLayout(inner_side)
    sv2.setContentsMargins(0, 0, 0, 0)
    sv2.setSpacing(0)

    shead = QFrame()
    shead.setObjectName('shead')
    hv = QVBoxLayout(shead)
    hv.setContentsMargins(14, 9, 14, 9)
    hv.setSpacing(2)
    win.t1 = QLabel('请选择左侧法兰类型')
    win.t1.setProperty('class', 't1')
    win.t1.setWordWrap(True)
    win.t2 = QLabel('选择类型后此处显示标准与单位')
    win.t2.setProperty('class', 't2')
    win.t2.setWordWrap(True)
    hv.addWidget(win.t1)
    hv.addWidget(win.t2)
    sv2.addWidget(shead)

    stage = QFrame()
    stage.setObjectName('stage')
    stv = QVBoxLayout(stage)
    stv.setAlignment(Qt.AlignCenter)
    stv.setContentsMargins(12, 12, 12, 12)
    win.card = DrawingCard()
    stv.addWidget(win.card)
    sv2.addWidget(stage)

    kvhead = QLabel('选中规格尺寸列表')
    kvhead.setObjectName('kvhead')
    sv2.addWidget(kvhead)

    win.kv = KvPanel()
    sv2.addWidget(win.kv)
    sv2.addStretch(1)

    sfoot = QFrame()
    fv = QHBoxLayout(sfoot)
    fv.setContentsMargins(14, 8, 14, 14)
    fv.setSpacing(8)
    win.b_print2 = QPushButton('打印（图 + 选中尺寸）')
    win.b_print2.setProperty('class', 'b-print')
    win.b_print2.clicked.connect(win.do_print)
    win.b_exp2 = QPushButton('导出当前行 CSV')
    win.b_exp2.setProperty('class', 'b-exp')
    win.b_exp2.clicked.connect(win.do_export_row)
    fv.addWidget(win.b_print2, 1)
    fv.addWidget(win.b_exp2, 1)
    sv2.addWidget(sfoot)

    side.setWidget(inner_side)
    win.side = side
    side.viewport().installEventFilter(win)
    return side
