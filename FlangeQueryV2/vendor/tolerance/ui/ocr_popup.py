# -*- coding: utf-8 -*-
"""OCR 查询结果浮窗：无框、置顶、点击外部或超时自动关闭。"""
import time

from compat.PySide6.QtCore import Qt, QTimer
from compat.PySide6.QtGui import QGuiApplication
from compat.PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QFrame)

from vendor.tolerance.ui.theme import get_palette

_P = get_palette()
ACCENT = _P["GREEN"]   # OCR 浮窗中 ACCENT 用于配合类型文字, 沿用主题绿
RED = _P["RED"]
BG = _P["CARD"]
TEXT = _P["TEXT"]
TEXT2 = _P["TEXT2"]
BORDER = _P["BORDER"]


def _fmt(v: int) -> str:
    return f"+{v}" if v > 0 else str(v)


class ResultPopup(QWidget):
    """静态工厂入口: show_results(fits, results) / show_error(msg)。"""

    _instance = None

    def __init__(self, lines):
        super().__init__(None, Qt.WindowType.FramelessWindowHint
                         | Qt.WindowType.Tool
                         | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setStyleSheet(f"ResultPopup {{ background:{BG}; border-radius:10px; }} "
                           f"ResultPopup QLabel {{ color:{TEXT}; background:transparent; }}")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 12, 16, 12)
        lay.setSpacing(8)
        for w in lines:
            lay.addWidget(w)
        self._close_timer = QTimer(self)
        self._close_timer.setInterval(15000)
        self._close_timer.timeout.connect(self.close)
        self._close_timer.start()

    # ── 构建内容 ──
    @staticmethod
    def _line_for_fit(fit, res) -> QWidget:
        row = QFrame()
        row.setStyleSheet(f"QFrame{{border:0.5px solid {BORDER}; border-radius:8px;}}"
                          "QFrame QLabel{border:none;}")
        v = QVBoxLayout(row)
        v.setContentsMargins(12, 8, 12, 8)
        v.setSpacing(4)
        if "error" in res:
            err = QLabel(f"⚠ {fit['raw']}  →  {res['error']}")
            err.setStyleSheet(f"color:{RED}; font-size:13px;")
            err.setWordWrap(True)
            v.addWidget(err)
            return row

        hd = res.get("hole_dev")
        sd = res.get("shaft_dev")
        if hd and sd:
            title = QLabel(f"φ{res['size']:g} {res['hole']}/{res['shaft']}")
        elif hd:
            title = QLabel(f"φ{res['size']:g} {res['hole']}（孔）")
        else:
            title = QLabel(f"φ{res['size']:g} {res['shaft']}（轴）")
        title.setStyleSheet("font-size:15px; font-weight:500;")
        v.addWidget(title)

        seg = res["seg"]
        parts = []
        if hd:
            parts.append(f"孔 {res['hole']}: {_fmt(hd[0])} / {_fmt(hd[1])} μm")
        if sd:
            parts.append(f"轴 {res['shaft']}: {_fmt(sd[0])} / {_fmt(sd[1])} μm")
        info = QLabel("    ".join(parts) + f"    （{seg[0]}~{seg[1]}mm 段）")
        info.setStyleSheet(f"font-size:13px; color:{TEXT2};")
        info.setWordWrap(True)
        v.addWidget(info)

        if hd and sd:
            a, b = res["limit_a"], res["limit_b"]
            if b >= 0:
                kind = "间隙配合"
                detail = f"最大间隙 {_fmt(a)} μm / 最小间隙 {_fmt(b)} μm"
            elif a < 0:
                kind = "过盈配合"
                detail = f"最小过盈 {_fmt(-a)} μm / 最大过盈 {_fmt(-b)} μm"
            else:
                kind = "过渡配合"
                detail = f"最大间隙 {_fmt(a)} μm / 最大过盈 {_fmt(-b)} μm"
            ft = QLabel(f"{kind}  ·  {detail}")
            ft.setStyleSheet(f"font-size:13px; color:{ACCENT};")
            ft.setWordWrap(True)
            v.addWidget(ft)

        btn = QPushButton("复制标注")
        btn.setFixedHeight(26)
        btn.setStyleSheet(f"font-size:12px; color:{ACCENT};")
        code_only = res["hole"] or res["shaft"]
        mark = f"φ{res['size']:g}{code_only}" + (f"/{res['shaft']}" if res["hole"] and res["shaft"] else "")
        btn.clicked.connect(lambda _, m=mark: _copy(m))
        h = QHBoxLayout()
        h.addStretch(1)
        h.addWidget(btn)
        v.addLayout(h)
        return row

    @classmethod
    def show_results(cls, fits, results):
        lines = []
        head = QLabel("📷 公差查询结果")
        head.setStyleSheet("font-size:14px; font-weight:500;")
        lines.append(head)
        for fit, res in zip(fits, results):
            lines.append(cls._line_for_fit(fit, res))
        cls._popup(lines)

    @classmethod
    def show_error(cls, msg: str):
        head = QLabel("📷 公差查询")
        head.setStyleSheet("font-size:14px; font-weight:500;")
        err = QLabel(msg)
        err.setStyleSheet(f"color:{RED}; font-size:13px;")
        err.setWordWrap(True)
        cls._popup([head, err])

    @classmethod
    def _popup(cls, lines):
        if cls._instance is not None:
            try:
                cls._instance.close()
            except Exception:
                pass
        pop = cls(lines)
        pop.adjustSize()
        if pop.width() > 480:
            pop.setFixedWidth(480)
        screen = QGuiApplication.primaryScreen().availableGeometry()
        pop.move(screen.right() - pop.width() - 24,
                 screen.bottom() - pop.height() - 24)
        pop.show()
        cls._instance = pop


def _copy(text: str):
    QGuiApplication.clipboard().setText(text)
