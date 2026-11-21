'''OCR 截图查公差：框选屏幕区域 → RapidOCR 识别 → 解析公差代号 → 查询结果。

技术栈复用自 ScreenTool（截图翻译）：区域框选 + RapidOCR + 浮窗展示。
全局热键 Ctrl+Shift+D（D=公差），与截图翻译的 A/S/C/F 不冲突。
'''
import os
import re
import sys
from PySide6.QtCore import QObject, Qt, QRect, Signal, QThread
from PySide6.QtGui import QColor, QGuiApplication, QImage, QPainter, QPen
from PySide6.QtWidgets import QWidget
_CODE = '([A-Za-z]{1,2}\\s?[0-9]{1,2})'
_SIZE = '[φΦθ⌀oO〇pб]?\\s*([0-9]{1,4}(?:\\.[0-9]+)?)'
_UNIT = '\\s*(?:mm|㎜)?\\s*'
_SEP = '\\s*(?:[/／\\\\|,，、或和与]|\\s)\\s*'
_FIT_RE = re.compile(f'{_SIZE}{_UNIT}{_CODE}(?:{_SEP}{_CODE})?', re.IGNORECASE)


def _norm_code(raw: str):
    '''归一化公差带代号：去空格，js→Js 特例。返回 None 表示不合法。'''
    if not raw:
        return None
    c = raw.replace(' ', '').replace('　', '')
    m = re.fullmatch('([A-Za-z]{1,2})([0-9]{1,2})', c)
    if not m:
        return None
    letters, grade = m.group(1), m.group(2)
    if len(letters) == 2 and letters.lower() == 'js':
        letters = 'Js' if letters[0].isupper() or letters == 'js' else 'js'
    return f'{letters}{grade}'


def parse_fits(text: str):
    '''从 OCR 文本中解析公差配合。

    返回列表，每项: {"size": float, "hole": "H7", "shaft": "g6"|None, "raw": 原文}
    解析规则：尺寸后紧跟的代号视为孔（图纸标注惯例 H7/g6 中孔在前），
    分隔符后的第二个代号视为轴。
    '''
    results, seen = [], set()
    for m in _FIT_RE.finditer(text or ''):
        size = float(m.group(1))
        hole = _norm_code(m.group(2))
        shaft = _norm_code(m.group(3)) if m.group(3) else None
        if not hole:
            continue
        key = (size, hole, shaft)
        if key in seen:
            continue
        seen.add(key)
        results.append({'size': size, 'hole': hole, 'shaft': shaft, 'raw': m.group(0).strip()})
    return results


def _lookup_code(code: str):
    '''查单个公差带代号，返回 (role, deviations) 或 None。

    严格区分大小写（H7=孔 / h7=轴），查不区分大小写的兜底表。
    '''
    from data.limit_deviations import HOLE_DEVIATIONS, SHAFT_DEVIATIONS
    if code in HOLE_DEVIATIONS:
        return ('hole', HOLE_DEVIATIONS[code])
    if code in SHAFT_DEVIATIONS:
        return ('shaft', SHAFT_DEVIATIONS[code])
    low = code.lower()
    for k, v in HOLE_DEVIATIONS.items():
        if k.lower() == low:
            return ('hole', v)
    for k, v in SHAFT_DEVIATIONS.items():
        if k.lower() == low:
            return ('shaft', v)
    return None


def query_fit(size: float, code1: str, code2: str | None):
    '''查询配合。孔/轴角色由数据表决定（H7→孔、g6→轴），不依赖书写顺序。

    返回结果 dict 或 {"error": 原因}。
    '''
    from data.limit_deviations import SIZE_RANGES, get_fit_type, get_size_range_index
    idx = get_size_range_index(size)
    if idx < 0:
        return {'error': f'尺寸 {size} 超出范围（0~3150mm）'}
    lo, hi = SIZE_RANGES[idx]
    role1 = _lookup_code(code1)

    def _seg(row, i):
        if row is not None and i < len(row):
            return row[i]
        return None

    dev1 = _seg(role1[1], idx) if role1 else None
    if role1 is None or dev1 is None:
        return {'error': f'公差带 {code1} 在 {lo}~{hi}mm 段无数据'}
    role2 = _lookup_code(code2) if code2 else None
    dev2 = _seg(role2[1], idx) if role2 else None
    if code2 and (role2 is None or dev2 is None):
        return {'error': f'公差带 {code2} 在 {lo}~{hi}mm 段无数据'}
    hole_code, hole_dev = (None, None)
    shaft_code, shaft_dev = (None, None)
    if role1[0] == 'hole':
        hole_code, hole_dev = (code1, dev1)
    else:
        shaft_code, shaft_dev = (code1, dev1)
    if role2:
        if role2[0] == role1[0]:
            who = '孔' if role1[0] == 'hole' else '轴'
            return {'error': f'{code1} 和 {code2} 都是{who}公差带，构不成配合'}
        if role2[0] == 'hole':
            hole_code, hole_dev = (code2, dev2)
        else:
            shaft_code, shaft_dev = (code2, dev2)
    out = {'size': size, 'seg': (lo, hi), 'hole': hole_code, 'hole_dev': hole_dev, 'shaft': shaft_code, 'shaft_dev': shaft_dev}
    if shaft_dev and hole_dev:
        out['fit_type'] = get_fit_type(hole_code, shaft_code, size)
        out['limit_a'] = hole_dev[0] - shaft_dev[1]
        out['limit_b'] = hole_dev[1] - shaft_dev[0]
    return out


class RegionOverlay(QWidget):
    '''全屏半透明遮罩，拖拽框选区域。选中后 emit selected(QRect)，ESC 取消。'''
    selected = Signal(QRect)
    cancelled = Signal()

    def __init__(self):
        super().__init__(None, Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setCursor(Qt.CursorShape.CrossCursor)
        self._origin = None
        self._rect = QRect()
        self._bg = None
        screen = QGuiApplication.primaryScreen().virtualGeometry()
        self.setGeometry(screen)
        self._load_bg()

    def _load_bg(self):
        '''整屏截图做底图(全部屏幕拼到一张画布, 坐标=虚拟桌面)。

            失败(抓屏返回空)置 None: 画布降级为纯暗色, 选中后 crop_region
            返回 None, 由控制器走抓屏兜底并如实报错, 不静默出假图。
            '''
        geo = self.geometry()
        if geo.width() <= 0 or geo.height() <= 0:
            self._bg = None
            return None
        img = QImage(geo.width(), geo.height(), QImage.Format.Format_ARGB32_Premultiplied)
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
        if grabbed:
            self._bg = img
            return None
        self._bg = None

    def crop_region(self, rect: QRect):
        '''从底图裁剪选区(全局逻辑坐标 → 底图像素坐标)。

            相对 ScreenTool 的差异: ScreenTool 关遮罩后用 mss 重截选区,
            这里直接裁内存底图 —— 不依赖关窗/抓屏时序, 多屏按比例映射,
            且可在无真实屏幕的测试里注入合成底图做确定性断言。
            越界或无底图返回 None(不裁半张图冒充成功)。
            '''
        if self._bg is None or self._bg.isNull():
            return None
        w, h = (self.width(), self.height())
        if w <= 0 or h <= 0:
            return None
        sx = self._bg.width() / float(w)
        sy = self._bg.height() / float(h)
        src = QRect(int(rect.x() * sx), int(rect.y() * sy), int(rect.width() * sx), int(rect.height() * sy))
        if not QRect(0, 0, self._bg.width(), self._bg.height()).contains(src):
            return None
        return self._bg.copy(src)

    def paintEvent(self, event):
        p = QPainter(self)
        r = self.rect()
        if self._bg is not None:
            p.drawImage(0, 0, self._bg)
        p.fillRect(r, QColor(0, 0, 0, 96))
        if not self._rect.isNull():
            if self._bg is not None:
                p.save()
                p.setClipRect(self._rect)
                p.drawImage(0, 0, self._bg)
                p.restore()
            pen = QPen(QColor('#1D9E75'))
            pen.setWidth(2)
            p.setPen(pen)
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawRect(self._rect)
        p.end()

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self._origin = e.globalPosition().toPoint()
            self._rect = QRect(self._origin, self._origin)
            self.update()
            return None

    def mouseMoveEvent(self, e):
        if self._origin is not None:
            self._rect = QRect(self._origin, e.globalPosition().toPoint()).normalized()
            self.update()
            return None

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton and not self._rect.isNull() and self._rect.width() > 4 and self._rect.height() > 4:
            rect = self._rect
            self.close()
            self.selected.emit(rect)
            return None
        self.close()
        self.cancelled.emit()

    def keyPressEvent(self, e):
        if e.key() == Qt.Key.Key_Escape:
            self.close()
            self.cancelled.emit()
            return None


class _OCRWorker(QThread):
    '''后台跑 RapidOCR，避免卡 UI。'''
    done = Signal(object)

    def __init__(self, image: QImage):
        super().__init__()
        self._image = image

    def run(self):
        try:
            from rapidocr_onnxruntime import RapidOCR
            img = self._image.convertToFormat(QImage.Format.Format_RGBA8888)
            w, h = (img.width(), img.height())
            ptr = img.constBits()
            arr = bytes(ptr) if hasattr(ptr, 'tobytes') else bytes(ptr)
            import numpy as np
            arr = np.frombuffer(arr, dtype=np.uint8).reshape((h, w, 4))[:, :, :3]
            ocr = RapidOCR()
            result, _ = ocr(arr)
            out = [(r[1], r[2]) for r in result or []]
            self.done.emit(out)
        except Exception as e:
            self.done.emit([f'__OCR_ERROR__{e}', 0.0])


class OCRQueryController(QObject):
    '''全局热键 Ctrl+Shift+D → 框选 → OCR → 弹结果浮窗。

    用法:  ctrl = OCRQueryController(); ctrl.start()
    '''
    HOTKEY = 'ctrl+shift+d'

    def __init__(self):
        super().__init__()
        self._overlay = None
        self._worker = None
        self._hotkey_registered = False

    def start(self):
        self.trigger.connect(self.start_capture)
        try:
            import keyboard
            keyboard.add_hotkey(self.HOTKEY, lambda: self.trigger.emit())
            self._hotkey_registered = True
        except Exception:
            self._hotkey_registered = False

    def stop(self):
        if self._hotkey_registered:
            try:
                import keyboard
                keyboard.remove_hotkey(self.HOTKEY)
            except Exception:
                pass

    trigger = Signal()

    def start_capture(self):
        self._overlay = RegionOverlay()
        self._overlay.selected.connect(self._on_region)
        self._overlay.cancelled.connect(self._on_cancel)
        self._overlay.showFullScreen()

    def _on_cancel(self):
        self._overlay = None

    def _on_region(self, rect: QRect):
        overlay = self._overlay
        self._overlay = None
        img = None
        if overlay is not None:
            img = overlay.crop_region(rect)
        if img is None or img.isNull():
            screen = QGuiApplication.primaryScreen()
            if screen is not None:
                pm = screen.grabWindow(0, rect.x(), rect.y(), rect.width(), rect.height())
                if not pm.isNull():
                    img = pm.toImage()
        if img is None or img.isNull():
            from ui.ocr_popup import ResultPopup
            ResultPopup.show_error('截屏失败，未获取到画面')
            return None
        self._worker = _OCRWorker(img.copy())
        self._worker.done.connect(self._on_ocr_done)
        self._worker.start()

    def _on_ocr_done(self, lines):
        if isinstance(lines, list) and lines and isinstance(lines[0], str) and lines[0].startswith('__OCR_ERROR__'):
            from ui.ocr_popup import ResultPopup
            ResultPopup.show_error(lines[0].replace('__OCR_ERROR__', ''))
            return
        text = ' '.join(t for (t, _) in lines)
        fits = parse_fits(text)
        from ui.ocr_popup import ResultPopup
        if not fits:
            ResultPopup.show_error('未识别到公差代号\n（支持格式：φ50H7/g6、50H7）\n原文: ' + text[:60])
            return
        results = [query_fit(f['size'], f['hole'], f['shaft']) for f in fits]
        ResultPopup.show_results(fits, results)


def selftest(image_path: str, out_path: str) -> int:
    '''图片→OCR→解析→查询 全链路自测（供 EXE `--ocr-selftest` 调用）。

    结果写 out_path, 返回退出码: 0=全过, 1=识别/查询未过, 2=引擎异常。
    '''

    def _w(text):
        try:
            with open(out_path, 'w', encoding='utf-8') as fp:
                fp.write(text)
        except Exception:
            pass
    try:
        from rapidocr_onnxruntime import RapidOCR
        import numpy as np
        from PIL import Image
        arr = np.array(Image.open(image_path).convert('RGB'))
        ocr = RapidOCR()
        result, _ = ocr(arr)
        text = ' '.join(r[1] for r in result or [])
        fits = parse_fits(text)
        lines = [f'TEXT={text}', f'FITS={fits}']
        rc = 0
        if not fits:
            lines.append('RESULT=FAIL 未识别到公差代号')
            rc = 1
        else:
            for f in fits:
                res = query_fit(f['size'], f['hole'], f['shaft'])
                lines.append(f'QUERY={res}')
                if 'error' in res:
                    rc = 1
            lines.append('RESULT=' + ('PASS' if rc == 0 else 'FAIL'))
        _w('\n'.join(lines))
        return rc
    except Exception as e:
        _w(f'RESULT=ERROR {e}')
        return 2


def overlay_selftest(out_path: str) -> int:
    '''框选覆盖层全链路自测(供 EXE `--overlay-selftest` 调用)。

    合成底图(PIL 系统字体画 φ50H7/g6) → 注入 RegionOverlay → paintEvent
    非空选区(2026-10-08 真机崩溃路径) → QTest 拖拽全链 → 底图裁剪 →
    _OCRWorker 真实像素路径 → RapidOCR → 解析 → 查询。
    强制 offscreen 平台: 自测不得在用户桌面上闪全屏遮罩。
    结果写 out_path, 返回退出码: 0=全过, 1=链路未过, 2=环境异常。
    '''

    def _w(text):
        try:
            with open(out_path, 'w', encoding='utf-8') as fp:
                fp.write(text)
        except Exception:
            pass
    try:
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'
        from PySide6.QtCore import QEventLoop, QPoint, QTimer, Qt
        from PySide6.QtGui import QImage
        from PySide6.QtTest import QTest
        from PySide6.QtWidgets import QApplication
        app = QApplication.instance() or QApplication(sys.argv[:1])
        from PIL import Image, ImageDraw, ImageFont
        font_path = 'C:\\Windows\\Fonts\\msyh.ttc'
        if not os.path.exists(font_path):
            font_path = 'C:\\Windows\\Fonts\\arial.ttf'
        if not os.path.exists(font_path):
            _w('RESULT=ERROR 系统字体文件缺失')
            return 2
        font = ImageFont.truetype(font_path, 64)
        pil = Image.new('RGB', (480, 200), (255, 255, 255))
        ImageDraw.Draw(pil).text((30, 60), 'φ50H7/g6', font=font, fill=(0, 0, 0))
        bg = QImage(pil.tobytes(), pil.width, pil.height, QImage.Format.Format_RGB888).copy()
        ov = RegionOverlay()
        ov.show()
        ov.setGeometry(0, 0, bg.width(), bg.height())
        ov._bg = bg
        rendered = QImage(ov.width(), ov.height(), QImage.Format.Format_ARGB32_Premultiplied)
        rendered.fill(QColor(0, 0, 0, 0))
        ov._rect = QRect(20, 30, 440, 140)
        ov.render(rendered)
        inner = rendered.pixelColor(430, 40)
        outer = rendered.pixelColor(5, 5)
        paint_ok = inner.red() >= 250 and 100 <= outer.red() <= 200
        ov._rect = QRect()
        got = []
        ov.selected.connect(lambda r: got.append(r))
        ov.cancelled.connect(lambda: got.append('cancelled'))
        QTest.mousePress(ov, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier, QPoint(20, 30))
        QTest.mouseMove(ov, QPoint(460, 170))
        QTest.mouseRelease(ov, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier, QPoint(460, 170))
        drag_ok = bool(got) and isinstance(got[0], QRect)
        sel = got[0] if drag_ok else QRect()
        expected = QRect(ov.mapToGlobal(QPoint(20, 30)), ov.mapToGlobal(QPoint(460, 170))).normalized()
        drag_ok = drag_ok and sel == expected
        crop = ov.crop_region(sel) if drag_ok else None
        crop_ok = crop is not None and not crop.isNull() and crop.width() == sel.width() and crop.height() == sel.height()
        if crop_ok:
            corner = crop.pixelColor(2, 2)
            crop_ok = corner.red() >= 250
        fits, query_err = [], ''
        if crop_ok:
            done_lines = []
            worker = _OCRWorker(crop)
            worker.done.connect(done_lines.append)
            worker.start()
            loop = QEventLoop()
            QTimer.singleShot(60000, loop.quit)
            while not done_lines:
                loop.exec()
            worker.wait(30000)
            lines = done_lines[0] if done_lines else []
            if isinstance(lines, list) and lines and isinstance(lines[0], str) and lines[0].startswith('__OCR_ERROR__'):
                query_err = lines[0]
            else:
                text = ' '.join(t for (t, _) in lines or [])
                fits = parse_fits(text)
                if fits:
                    res = query_fit(fits[0]['size'], fits[0]['hole'], fits[0]['shaft'])
                    if 'error' in res:
                        query_err = res['error']
                else:
                    query_err = '未解析到代号 TEXT=' + text[:60]
        ocr_ok = bool(fits) and not query_err
        rc = 0 if paint_ok and drag_ok and crop_ok and ocr_ok else 1
        _w('\n'.join([f'PAINT={"PASS" if paint_ok else "FAIL"} inner={inner.red()},{inner.green()},{inner.blue()} outer={outer.red()},{outer.green()},{outer.blue()}', f'DRAG={"PASS" if drag_ok else "FAIL"} rect={sel}', f'CROP={"PASS" if crop_ok else "FAIL"} size={crop.width() if crop else 0}x{crop.height() if crop else 0}', f'OCR={"PASS" if ocr_ok else "FAIL"} FITS={fits} {query_err}', 'RESULT=' + ('PASS' if rc == 0 else 'FAIL')]))
        return rc
    except Exception as e:
        import traceback
        _w('RESULT=ERROR %s\n%s' % (e, traceback.format_exc()))
        return 2


if __name__ == '__main__':
    for t in ('φ50H7/g6', '50 H7 / g6', 'Φ30H7/k6', '20h6', '轴径100H8或p6', 'M8×1.25 6H', '垃圾文本没有代号'):
        print(t, '→', parse_fits(t))
