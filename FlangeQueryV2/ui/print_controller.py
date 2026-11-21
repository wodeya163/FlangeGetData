# -*- coding: utf-8 -*-
"""打印预览控制器。"""

from PyQt5.QtCore import QRect, Qt
from PyQt5.QtGui import QColor, QFont, QPainter
from PyQt5.QtPrintSupport import QPrinter, QPrintPreviewDialog
from PyQt5.QtWidgets import QMessageBox

from version import APP_NAME, APP_VERSION_DISPLAY

import logging

logger = logging.getLogger('flangequery')


def do_print(win):
    if not win.cur_row:
        QMessageBox.information(win, '提示', '请先在中间表选择一行规格')
        return
    printer = QPrinter(QPrinter.HighResolution)
    preview = QPrintPreviewDialog(printer, win)
    preview.setWindowTitle('打印预览')
    preview.paintRequested.connect(lambda p: render_print_page(win, p))
    preview.exec_()


def render_print_page(win, printer):
    """按纸张大小缩放渲染图形卡与尺寸表，避免固定像素打印溢出。"""
    if not win.cur_row:
        return
    painter = QPainter(printer)
    try:
        page = printer.pageRect(QPrinter.DevicePixel)
        page_left = int(page.left())
        page_top = int(page.top())
        page_bottom = int(page.bottom())
        page_width = max(1, int(page.width()))
        page_height = max(1, int(page.height()))
        margin = max(24, int(min(page_width, page_height) * 0.05))
        x = page_left + margin
        y = page_top + margin
        width = max(1, page_width - 2 * margin)
        header_h = max(64, int(page_height * 0.09))

        title_font = QFont('Microsoft YaHei')
        title_font.setBold(True)
        title_font.setPixelSize(max(16, int(page.height() * 0.022)))
        painter.setFont(title_font)
        painter.setPen(QColor('#163a5f'))
        painter.drawText(QRect(x, y, width, int(header_h * 0.45)),
                         Qt.AlignLeft | Qt.AlignVCenter, win.t1.text())

        sub_font = QFont('Microsoft YaHei')
        sub_font.setPixelSize(max(10, int(page.height() * 0.013)))
        painter.setFont(sub_font)
        painter.setPen(QColor('#555555'))
        painter.drawText(QRect(x, y + int(header_h * 0.42), width,
                               int(header_h * 0.35)),
                         Qt.AlignLeft | Qt.AlignVCenter | Qt.TextWordWrap,
                         win.t2.text())
        painter.setPen(QColor('#1f4e79'))
        painter.drawLine(x, y + header_h - 6, x + width, y + header_h - 6)

        body_top = y + header_h
        body_h = max(1, page_bottom - margin - body_top)
        gap = max(12, int(page_height * 0.012))
        spec = None
        try:
            from ui.vector_export import build_current_spec
            spec = build_current_spec(win)
        except Exception:
            logger.exception('打印矢量 spec 构建失败')
        if spec is not None:
            spec.title = ''
            vec_scale = min(width / max(1, spec.width),
                            body_h / max(1, spec.height))
            painter.save()
            painter.translate(x + (width - spec.width * vec_scale) / 2,
                              body_top)
            painter.scale(vec_scale, vec_scale)
            from drawspec.renderer import paint_spec
            paint_spec(painter, spec)
            painter.restore()
        else:
            card_w = max(1, win.card.width())
            card_h = max(1, win.card.height())
            kv_w = max(1, win.kv.width())
            kv_h = max(1, win.kv.height())
            content_w = max(card_w, kv_w)
            content_h = card_h + gap + kv_h
            scale = min(1.0, width / content_w, body_h / content_h)
            painter.save()
            painter.translate(x, body_top)
            painter.scale(scale, scale)
            win.card.render(painter)
            painter.translate(0, card_h + gap)
            win.kv.render(painter)
            painter.restore()

        foot_font = QFont('Microsoft YaHei')
        foot_font.setPixelSize(max(8, int(page.height() * 0.010)))
        painter.setFont(foot_font)
        painter.setPen(QColor('#888888'))
        painter.drawText(
            QRect(x, page_bottom - margin + 4, width, 20),
            Qt.AlignRight | Qt.AlignVCenter,
            '%s %s%s' % (APP_NAME, APP_VERSION_DISPLAY,
                                         '  · 矢量' if spec is not None else ''))
    except Exception:
        logger.exception('打印渲染失败')
        raise
    finally:
        painter.end()
