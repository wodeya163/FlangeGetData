# -*- coding: utf-8 -*-
"""当前页面的矢量图导出：DrawingSpec → PDF / SVG。"""

import logging
import os

from PyQt5.QtWidgets import QFileDialog, QMessageBox

from drawspec.bellows import build_bellows_spec
from drawspec.fitting import (build_cap_spec, build_elbow_spec,
                              build_reducer_spec, build_tee_spec)
from drawspec.flange import build_flange_spec
from drawspec.gasket import build_gasket_spec
from drawspec.pipe import build_pipe_spec
from drawspec.seal import build_seal_spec
from drawspec.renderer import save_pdf, save_svg
from ui.drawing_card import FLANGE_TPL_KIND

logger = logging.getLogger('flangequery')


def build_current_spec(win):
    if not win.cur_page or not win.cur_row:
        return None
    name, csvf, tpl, labels, std = win.cur_page[:5]
    page_spec = getattr(win, 'cur_spec', None)
    drawing = getattr(page_spec, 'drawing', '') if page_spec else ''
    if drawing.startswith('flange:'):
        kind = drawing.split(':', 1)[1]
        return build_flange_spec(win.cur_row, kind=kind,
                                 face=win.cur_row.get('密封面', 'RF'),
                                 standard=std)
    if drawing == 'fitting:elbow':
        return build_elbow_spec(win.cur_row, angle=getattr(win.card, 'angle', 90),
                                standard=std,
                                wall_series=getattr(win.card, 'sch', 'Sch40'))
    if drawing == 'fitting:tee':
        return build_tee_spec(win.cur_row, standard=std,
                              wall_series=getattr(win.card, 'sch', 'Sch40'))
    if drawing == 'fitting:reducer':
        return build_reducer_spec(win.cur_row, standard=std,
                                  wall_series=getattr(win.card, 'sch', 'Sch40'))
    if drawing == 'fitting:cap':
        return build_cap_spec(win.cur_row, standard=std,
                              wall_series=getattr(win.card, 'sch', 'Sch40'))
    if drawing.startswith('gasket:'):
        return build_gasket_spec(win.cur_row, drawing.split(':', 1)[1])
    if drawing == 'pipe':
        return build_pipe_spec(win.cur_row)
    if drawing == 'bellows':
        return build_bellows_spec(win.cur_row)
    if drawing == 'seal':
        return build_seal_spec(win.cur_row, tpl)
    kind = FLANGE_TPL_KIND.get(tpl)
    if kind:
        return build_flange_spec(win.cur_row, kind=kind,
                                 face=win.cur_row.get('密封面', 'RF'),
                                 standard=std)
    if '弯头' in tpl:
        return build_elbow_spec(win.cur_row, angle=getattr(win.card, 'angle', 90),
                                standard=std,
                                wall_series=getattr(win.card, 'sch', 'Sch40'))
    return None


def export_vector(win):
    spec = build_current_spec(win)
    if spec is None:
        QMessageBox.information(
            win, '矢量导出',
            '当前页面暂无参数化矢量模板。\n'
            '已支持：法兰、弯头/三通/异径管/管帽、垫片、钢管、波纹管、密封面。')
        return
    base = os.path.splitext(win.cur_page[1])[0]
    default = '%s_DN%s.pdf' % (base, win.cur_row.get('DN', ''))
    fn, selected = QFileDialog.getSaveFileName(
        win, '导出矢量图', default,
        'PDF 矢量图 (*.pdf);;SVG 矢量图 (*.svg)')
    if not fn:
        return
    try:
        if fn.lower().endswith('.svg'):
            save_svg(spec, fn)
        else:
            if not fn.lower().endswith('.pdf'):
                fn += '.pdf'
            save_pdf(spec, fn)
        QMessageBox.information(win, '矢量导出', '已导出：\n%s' % fn)
    except Exception:
        logger.exception('矢量导出失败')
        QMessageBox.warning(win, '矢量导出', '导出失败，详见日志。')
