# -*- coding: utf-8 -*-
"""公差截图 OCR：框选屏幕区域，Tesseract 识别后填入孔轴配合。"""

import os
import re
import shutil
import subprocess
import tempfile

from PyQt5.QtCore import QObject, QRect, Qt, QThread, pyqtSignal
from PyQt5.QtGui import QColor, QGuiApplication, QImage, QPainter, QPen
from PyQt5.QtWidgets import QInputDialog, QMessageBox, QWidget

_CODE = r'([A-Za-z]{1,2}\s?[0-9]{1,2})'
_SIZE = r'[φΦθ⌀oO〇pб]?\s*([0-9]{1,4}(?:\.[0-9]+)?)'
_UNIT = r'\s*(?:mm|㎜)?\s*'
_SEP = r'\s*(?:[/／\\|,，、或和与]|\s)\s*'
FIT_RE = re.compile(_SIZE + _UNIT + _CODE + '(?:' + _SEP + _CODE + ')?',
                    re.IGNORECASE)


def norm_code(raw):
    if not raw:
        return None
    c = raw.replace(' ', '').replace('　', '')
    m = re.fullmatch(r'([A-Za-z]{1,2})([0-9]{1,2})', c)
    if not m:
        return None
    letters, grade = m.group(1), m.group(2)
    if len(letters) == 2 and letters.lower() == 'js':
        letters = 'Js' if letters[0].isupper() else 'js'
    return '%s%s' % (letters, grade)


def parse_fits(text):
    """从 OCR 文本解析尺寸+孔/轴代号。"""
    out, seen = [], set()
    for m in FIT_RE.finditer(text or ''):
        size = float(m.group(1))
        hole = norm_code(m.group(2))
        shaft = norm_code(m.group(3)) if m.group(3) else None
        if not hole:
            continue
        key = (size, hole, shaft)
        if key in seen:
            continue
        seen.add(key)
        out.append({'size': size, 'hole': hole, 'shaft': shaft,
                    'raw': m.group(0).strip()})
    return out


class RegionOverlay(QWidget):
    selected = pyqtSignal(QRect)
    cancelled = pyqtSignal()

    def __init__(self):
        super().__init__(None, Qt.FramelessWindowHint |
                         Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setCursor(Qt.CrossCursor)
        self._origin = None
        self._rect = QRect()
        self._bg = None
        geo = QGuiApplication.primaryScreen().virtualGeometry()
        self.setGeometry(geo)
        self._load_bg(geo)

    def _load_bg(self, geo):
        img = QImage(geo.width(), geo.height(), QImage.Format_ARGB32)
        img.fill(QColor(30, 30, 30, 255))
        grabbed = False
        for scr in QGuiApplication.screens():
            pm = scr.grabWindow(0)
            if pm.isNull():
                continue
            off = scr.geometry().topLeft() - geo.topLeft()
            p = QPainter(img)
            p.drawPixmap(off, pm)
            p.end()
            grabbed = True
        self._bg = img if grabbed else None

    def crop_region(self, rect):
        if self._bg is None or self._bg.isNull():
            return None
        sx = self._bg.width() / float(max(1, self.width()))
        sy = self._bg.height() / float(max(1, self.height()))
        src = QRect(int(rect.x() * sx), int(rect.y() * sy),
                    max(1, int(rect.width() * sx)),
                    max(1, int(rect.height() * sy)))
        return self._bg.copy(src)

    def paintEvent(self, event):
        p = QPainter(self)
        if self._bg is not None:
            p.drawImage(0, 0, self._bg)
        p.fillRect(self.rect(), QColor(0, 0, 0, 96))
        if not self._rect.isNull():
            if self._bg is not None:
                p.save()
                p.setClipRect(self._rect)
                p.drawImage(0, 0, self._bg)
                p.restore()
            p.setPen(QPen(QColor('#1f4e79'), 2))
            p.setBrush(Qt.NoBrush)
            p.drawRect(self._rect)
        p.end()

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self._origin = e.pos()
            self._rect = QRect(self._origin, self._origin)
            self.update()

    def mouseMoveEvent(self, e):
        if self._origin is not None:
            self._rect = QRect(self._origin, e.pos()).normalized()
            self.update()

    def mouseReleaseEvent(self, e):
        if (e.button() == Qt.LeftButton and not self._rect.isNull()
                and self._rect.width() > 5 and self._rect.height() > 5):
            rect = self._rect
            self.close()
            self.selected.emit(rect)
        else:
            self.close()
            self.cancelled.emit()

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()
            self.cancelled.emit()


class OCRWorker(QThread):
    done = pyqtSignal(object)

    def __init__(self, image, parent=None):
        super().__init__(parent)
        self._image = image

    def run(self):
        try:
            exe = shutil.which('tesseract')
            if not exe:
                for cand in (r'C:\Program Files\Tesseract-OCR\tesseract.exe',
                             r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'):
                    if os.path.isfile(cand):
                        exe = cand
                        break
            if not exe:
                self.done.emit(['__OCR_ERROR__未找到 Tesseract-OCR'])
                return
            fd, path = tempfile.mkstemp(suffix='.png')
            os.close(fd)
            try:
                self._image.save(path, 'PNG')
                flags = 0x08000000 if os.name == 'nt' else 0
                proc = subprocess.run(
                    [exe, path, 'stdout', '-l', 'chi_sim', '--psm', '6'],
                    capture_output=True, text=True, encoding='utf-8',
                    errors='replace', creationflags=flags, timeout=60)
                text = proc.stdout or ''
                if proc.returncode != 0 and not text:
                    raise RuntimeError((proc.stderr or 'OCR 失败').strip())
            finally:
                try:
                    os.unlink(path)
                except OSError:
                    pass
            self.done.emit([line for line in text.splitlines() if line.strip()])
        except Exception as exc:
            self.done.emit(['__OCR_ERROR__%s' % exc])


class ToleranceOCRController(QObject):
    """把 OCR 结果写回公差窗口的孔轴配合页。"""

    def __init__(self, window, root=None):
        super().__init__(window)
        self.window = window
        self.root = root
        self._overlay = None
        self._worker = None

    def start_capture(self):
        self._overlay = RegionOverlay()
        self._overlay.selected.connect(self._on_selected)
        self._overlay.cancelled.connect(lambda: None)
        self._overlay.show()

    def _on_selected(self, rect):
        img = self._overlay.crop_region(rect) if self._overlay else None
        if img is None or img.isNull():
            QMessageBox.warning(self.window, '截图查公差', '没有截到画面')
            return
        self._worker = OCRWorker(img, self)
        self._worker.done.connect(self._on_text)
        self._worker.start()

    def _on_text(self, lines):
        if lines and str(lines[0]).startswith('__OCR_ERROR__'):
            QMessageBox.warning(self.window, '截图查公差',
                                str(lines[0]).replace('__OCR_ERROR__', ''))
            return
        text = '\n'.join(lines or [])
        fits = parse_fits(text)
        if not fits:
            QMessageBox.information(
                self.window, '截图查公差',
                '没有识别到孔轴配合。\n请框选类似 “φ30 H7/g6” 的标注。\n\n'
                '识别文本：\n' + (text or '（空）'))
            return
        fit = fits[0]
        if len(fits) > 1:
            labels = ['%s  (%s)' % (f['raw'], f['hole'] +
                                     ('/' + f['shaft'] if f['shaft'] else ''))
                      for f in fits]
            choice, ok = QInputDialog.getItem(
                self.window, '截图查公差', '识别到多个配合，请选择：',
                labels, 0, False)
            if not ok:
                return
            fit = fits[labels.index(choice)]
        self._apply(fit)

    @staticmethod
    def _repair(code, valid):
        if code in valid:
            return code
        m = re.fullmatch(r'([A-Za-z]{1,2})([0-9]{1,2})', code or '')
        if not m:
            return code
        letters, grade = m.group(1), m.group(2)
        for cand in (letters[0] + grade, letters[1] + grade
                     if len(letters) > 1 else ''):
            if cand and cand in valid:
                return cand
        return code

    def _apply(self, fit):
        try:
            from vendor.tolerance.ui.main_window import FitTab
            from vendor.tolerance.data.limit_deviations import (HOLE_DEVIATIONS,
                                                                SHAFT_DEVIATIONS)
            fit['hole'] = self._repair(fit['hole'], set(HOLE_DEVIATIONS))
            if fit.get('shaft'):
                fit['shaft'] = self._repair(fit['shaft'], set(SHAFT_DEVIATIONS))
            tab = (self.root or self.window).findChild(FitTab)
            if tab is None:
                raise RuntimeError('未找到孔轴配合页')
            tab.size_input.setText(str(fit['size']))
            tab.hole_combo.setCurrentText(fit['hole'])
            if fit.get('shaft'):
                tab.shaft_combo.setCurrentText(fit['shaft'])
            tab._query_now()
            QMessageBox.information(
                self.window, '截图查公差',
                '已识别：%s\n孔 %s / 轴 %s，结果已填入。'
                % (fit['raw'], fit['hole'], fit.get('shaft') or '—'))
        except Exception as exc:
            QMessageBox.warning(self.window, '截图查公差', str(exc))
