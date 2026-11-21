# -*- coding: utf-8 -*-
"""状态栏。"""

import datetime

from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel


def build_statusbar(win):
    bar = QFrame()
    bar.setObjectName('statusbar')
    bar.setFixedHeight(24)
    bv = QHBoxLayout(bar)
    bv.setContentsMargins(12, 0, 12, 0)
    bv.setSpacing(18)
    win.st_msg = QLabel('就绪')
    win.st_tpl = QLabel('')
    win.st_anchor = QLabel('')
    bv.addWidget(win.st_msg)
    bv.addWidget(win.st_tpl)
    bv.addWidget(win.st_anchor)
    bv.addStretch(1)
    bv.addWidget(QLabel(datetime.date.today().strftime('%Y-%m-%d')))
    return bar
