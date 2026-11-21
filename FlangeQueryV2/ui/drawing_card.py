# -*- coding: utf-8 -*-
"""侧栏图形卡：模板位图 + 数值标注；实验矢量图开关。"""

import os

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtWidgets import QComboBox, QLabel, QScrollArea, QWidget

from drawspec.wall import available_series
from core.config import (BELLOWS_VECTOR_ENABLED, FLANGE_VECTOR_ENABLED,
                         SCALE, TPL_DIR, VECTOR_ENABLED, logger)

FLANGE_TPL_KIND = {
    'WN-带颈对焊.bmp': 'WN', 'SO-带颈平焊.bmp': 'SO',
    'PL板式平焊.bmp': 'PL', 'SW承插焊.bmp': 'SW',
    'Th螺纹.bmp': 'TH', 'BL法兰盖.bmp': 'BL',
    'IF整体法兰.bmp': 'IF',
    'LWN-长高颈.bmp': 'LWN',
    '623法兰盖.bmp': 'BL',
    'PL板式平焊.bmp': 'PL',
    'PJSE对焊环松套592.bmp': 'PJ',
    'PJSE对焊环松套615.bmp': 'PJ',
    'PJRJ平焊环松套.bmp': 'PJ',
}

CONTAINER_TPLS = {'容器法兰.bmp'}
PIPE_TPLS = {'pipe.bmp'}
GASKET_TPLS = {
    'gasket_flat.bmp', 'gasket_ptfe.bmp', 'gasket_metaljacket.bmp',
    'gasket_spiral.bmp', 'gasket_serrated.bmp', 'gasket_ring.bmp',
}
FITTING_TPLS = {
    'fittings_elbow.bmp', 'fittings_tee.bmp',
    'fittings_reducer.bmp', 'fittings_cap.bmp',
}
SEAL_TPLS = {
    'mfm_突面.bmp', 'mfm_凹凸面.bmp', 'mfm_楔槽面.bmp',
    'mfm_环连接面.bmp',
}


def _fmt_keys(fmt):
    import string
    return [fn for _, fn, _, _ in string.Formatter().parse(fmt) if fn]

class DrawingCard(QWidget):
    """图形卡：模板位图 ×0.7 + 数值标注 + 右上角标（严格按 mockup .card）。"""

    _PIXMAP_CACHE = {}

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet('background:#fff;border:1px solid #b8bec6;')
        self.pic = QLabel(self)
        self.mark = QLabel(self)
        self.mark.setAlignment(Qt.AlignRight | Qt.AlignTop)
        self.mark.setStyleSheet('color:#888;font-size:9px;background:transparent;')
        self.labels = {}
        self.cur_tpl = None
        self.src_size = None
        self._state = None
        self._last_avail = None
        self._vector = False
        self.angle = 90
        self.angle_box = QComboBox(self)
        self.angle_box.addItems(['45°', '90°', '180°'])
        self.angle_box.setCurrentText('90°')
        self.angle_box.setFixedWidth(62)
        self.angle_box.setStyleSheet('font-size:10px;background:#fff;')
        self.angle_box.hide()
        self.angle_box.currentTextChanged.connect(self._on_angle)
        self.face = 'RF'
        self.face_box = QComboBox(self)
        self.face_box.addItems(['RF', 'FF', 'MFM', 'TG', 'RJ'])
        self.face_box.setCurrentText('RF')
        self.face_box.setFixedWidth(62)
        self.face_box.setStyleSheet('font-size:10px;background:#fff;')
        self.face_box.hide()
        self.face_box.currentTextChanged.connect(self._on_face)
        self.sch = 'Sch40'
        self.sch_box = QComboBox(self)
        series = list(available_series())
        if 'T_lim' not in series:
            series.append('T_lim')
        self.sch_box.addItems(series)
        if 'Sch40' in series:
            self.sch_box.setCurrentText('Sch40')
        self.sch_box.setFixedWidth(88)
        self.sch_box.setStyleSheet('font-size:10px;background:#fff;')
        self.sch_box.hide()
        self.sch_box.currentTextChanged.connect(self._on_sch)

    def _on_angle(self, text):
        try:
            self.angle = int(text.rstrip('°'))
        except ValueError:
            self.angle = 90
        if self._state is not None:
            self.relayout()

    def _on_face(self, text):
        self.face = text or 'RF'
        if self._state is not None:
            self.relayout()

    def _on_sch(self, text):
        self.sch = text or 'Sch40'
        if self._state is not None:
            self.relayout()

    def reset(self):
        """清空图形卡，回到“请选择规格”占位状态。"""
        self._state = None
        self._last_avail = None
        self.cur_tpl = None
        self.src_size = None
        self._vector = False
        for lb in self.labels.values():
            lb.hide()
            lb.deleteLater()
        self.labels.clear()
        self.pic.clear()
        self.pic.setText('请选择左侧规格')
        self.pic.setAlignment(Qt.AlignCenter)
        avail = self.available_width()
        w = max(120, min(420, avail - 4))
        h = max(100, int(w * 0.83))
        self.setFixedSize(w + 3, h + 3)
        self.pic.setGeometry(1, 1, w, h)
        self.pic.show()
        self.mark.clear()
        self.mark.hide()
        self.angle_box.hide()
        self.face_box.hide()
        self.sch_box.hide()

    def available_width(self):
        """优先按滚动区视口宽度计算，避免被内容最小宽度带偏。"""
        widget = self.parentWidget()
        margins = 24
        if widget is not None and widget.layout() is not None:
            m = widget.layout().contentsMargins()
            margins = m.left() + m.right()
        node = widget
        while node is not None:
            if isinstance(node, QScrollArea):
                return max(120, node.viewport().width() - margins)
            node = node.parentWidget()
        if widget is not None and widget.layout() is not None:
            width = widget.layout().contentsRect().width()
            if width > 50:
                return width
        return max(120, 413 - margins)

    def show_page(self, tpl_name, labels_cfg, values, mark_text='', standard=''):
        self._state = (tpl_name, labels_cfg, dict(values or {}), mark_text,
                      standard)
        self.relayout()

    def relayout_if_needed(self):
        """视口宽度变化时重算缩放；宽度未变则跳过，避免布局递归。"""
        if self._state is None:
            return
        avail = self.available_width()
        if self._last_avail is not None and abs(avail - self._last_avail) < 1:
            return
        self.relayout()

    def relayout(self):
        if self._state is None:
            return
        tpl_name, labels_cfg, values, mark_text, standard = self._state
        avail = self.available_width()
        self._last_avail = avail
        self.cur_tpl = tpl_name
        # 仅重建数值标签；pic/mark 为常驻控件，绝不能 deleteLater
        #（否则事件循环销毁后图形永久消失——2026-10-18 实测 bug）
        for lb in self.labels.values():
            lb.hide()
            lb.deleteLater()
        self.labels.clear()
        vector_pm = None
        if FLANGE_VECTOR_ENABLED and tpl_name in FLANGE_TPL_KIND:
            try:
                from flange_drawing import compact_labels, render_gb_flange
                kind = FLANGE_TPL_KIND[tpl_name]
                vector_pm = render_gb_flange(values, frame=False, kind=kind,
                                             show_labels=True,
                                             standard=standard,
                                             compact=True,
                                             face=self.face)
                if vector_pm is not None:
                    labels_cfg = {}
            except Exception:
                logger.exception('法兰矢量绘图失败，回退 BMP')
        elif BELLOWS_VECTOR_ENABLED and tpl_name == 'bellows.bmp':
            try:
                from bellows_drawing import compact_labels, render_bellows
                vector_pm = render_bellows(values, 1200, 760,
                                           show_labels=False)
                labels_cfg = compact_labels(values)
            except Exception:
                logger.exception('波纹管矢量绘图失败，回退 BMP')
        elif tpl_name in CONTAINER_TPLS:
            try:
                from parts_drawing import render_container
                vector_pm = render_container(values, tpl_name)
                labels_cfg = {}
            except Exception:
                logger.exception('容器法兰矢量绘图失败，回退 BMP')
        elif tpl_name in PIPE_TPLS:
            try:
                from parts_drawing import render_pipe
                vector_pm = render_pipe(values, tpl_name)
                labels_cfg = {}
            except Exception:
                logger.exception('钢管矢量绘图失败，回退 BMP')
        elif tpl_name in GASKET_TPLS:
            try:
                from parts_drawing import render_gasket
                vector_pm = render_gasket(values, tpl_name)
                labels_cfg = {}
            except Exception:
                logger.exception('垫片矢量绘图失败，回退 BMP')
        elif tpl_name in FITTING_TPLS:
            try:
                from parts_drawing import render_fitting
                vector_pm = render_fitting(values, tpl_name, angle=self.angle,
                                           wall_series=self.sch)
                labels_cfg = {}
            except Exception:
                logger.exception('管件矢量绘图失败，回退 BMP')
        elif tpl_name in SEAL_TPLS:
            try:
                from parts_drawing import render_seal
                vector_pm = render_seal(values, tpl_name)
                labels_cfg = {}
            except Exception:
                logger.exception('密封面矢量绘图失败，回退 BMP')
        if vector_pm is not None:
            pm = vector_pm
            self._vector = True
        else:
            self._vector = False
            path = os.path.join(TPL_DIR, tpl_name)
            key = (path, os.path.getmtime(path)) if os.path.exists(path) else (path, 0)
            pm = DrawingCard._PIXMAP_CACHE.get(key)
            if pm is None:
                pm = QPixmap(path)
                if not pm.isNull():
                    DrawingCard._PIXMAP_CACHE[key] = pm
        if pm.isNull():
            self.src_size = None
            w = max(120, min(420, avail - 4))
            h = max(100, int(w * 0.83))
            self.pic.setText('模板缺失: ' + tpl_name)
            self.pic.setAlignment(Qt.AlignCenter)
            self.pic.setGeometry(1, 1, w, h)
            self.pic.show()
            self.setFixedSize(w + 3, h + 3)
            return
        w0, h0 = pm.width(), pm.height()
        self.src_size = (w0, h0)
        # 侧栏 430px 时内容区约 389px：596px 模板按 0.7 缩放得到 420px 卡片，
        # 右侧标注会被裁掉。这里按可用宽度收敛，宽度变化时由事件过滤器重算。
        if w0 >= 300:
            s = min(SCALE, max(0.05, (avail - 4) / w0))
        else:
            s = min(1.8, max(0.05, (avail - 4) / w0))  # 小模板（如钢管截面）放大显示
        w, h = int(w0 * s), int(h0 * s)
        self.setFixedSize(w + 3, h + 3)
        self.pic.setPixmap(pm.scaled(w, h, Qt.KeepAspectRatio,
                                     Qt.SmoothTransformation))
        self.pic.setGeometry(1, 1, w, h)
        self.pic.show()
        is_fitting = tpl_name.startswith('fittings_')
        if tpl_name == 'fittings_elbow.bmp':
            self.angle_box.setGeometry(6, max(4, h - 28), 62, 22)
            self.angle_box.show()
            self.angle_box.raise_()
        else:
            self.angle_box.hide()
        if is_fitting:
            self.sch_box.setGeometry(72 if tpl_name == 'fittings_elbow.bmp' else 6,
                                     max(4, h - 28), 88, 22)
            self.sch_box.show()
            self.sch_box.raise_()
        else:
            self.sch_box.hide()
        if tpl_name in FLANGE_TPL_KIND:
            self.face_box.setGeometry(6, max(4, h - 28), 62, 22)
            self.face_box.show()
            self.face_box.raise_()
        else:
            self.face_box.hide()
        self.mark.setText(mark_text)
        self.mark.setGeometry(max(w - 150, 4), 6, 142, 52)
        self.mark.show()
        f = QFont('Microsoft YaHei')
        f.setPixelSize(max(8, int(12 * min(s, 1.2))))
        for name, (rect, fmt) in labels_cfg.items():
            x, y, wd, ht = rect
            lb = QLabel(self)
            lb.setFont(f)
            lb.setStyleSheet('color:#111;background:#fff;')
            try:
                txt = fmt.format(**{k: str(values.get(k, '-')).strip() or '-'
                                    for k in _fmt_keys(fmt)})
            except Exception:
                txt = '-'
            lb.setText(txt)
            lb.setGeometry(1 + int(x * s), 1 + int(y * s),
                           int(wd * s), int(ht * s))
            lb.show()
            self.labels[name] = lb

