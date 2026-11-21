# Reconstructed from bytecode by split_decompile.py
# drawing.pyc

'''键联接截面示意图 —— 参数化绘制（QPainter，零新增依赖）

画法依据（2026-09-26/27 联网多源交叉核验 + 机械资料大全《怎样识读〈机械制图〉新标准
第3版》第二十章花键联结画法参照，机械工业出版社《典型机械零部件表达方法350例》等
教学来源一致）：
  1. 径向剖切（端面，垂直轴线）：轴、键、毂三者均画剖面线，且方向/间距相互区分
  2. 轴向剖切（纵剖，剖切面过轴线平行键长）：轴、键为实心件按不剖绘制（不画剖面线），
     仅轮毂画剖面线
  3. 键两侧面、底面为工作面：与键槽贴合，画单实线
  4. 键顶面为非工作面：与毂槽底存在间隙（t1+t2-h），必须画两条实线
  5. 尺寸注法按制图惯例：轴槽标 d−t1（键槽底至对面母线）、键宽标 b、键长标 L

比例说明：全部尺寸按真实比例（b/h/t1/t2/d/L 来自经审计的 GB/T 1095/1096 数据）。
唯一例外：键顶面间隙实际仅 0.2~0.5mm，按真实比例在屏幕上不足 1 像素，
为保证"两条实线"的画法规范可见，间隙显示下限 2px（图中已注明"间隙放大显示"）。

布局：上下双视图——上径向（端面）、下轴向（纵剖），各占整幅宽度，避免挤压。
A/B/C 型键的端头圆弧只体现在俯视图，本图两视图均为矩形轮廓，不受键型号影响。
'''
import math
from PySide6.QtCore import Qt, QPoint, QPointF, QRectF, QTimer
from PySide6.QtGui import QPainter, QPen, QColor, QPainterPath, QFont, QPolygonF, QFontDatabase
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QScrollArea
from key_data import THEMES, get_theme_key
GAP_MIN_PX = 8
TV_RATIO = 0.52
HEAD_H = 46
SUB_H = 20
_CJK_CHAIN = [
    'Microsoft YaHei',
    '微软雅黑',
    'Noto Sans CJK SC',
    'Source Han Sans SC',
    'WenQuanYi Zen Hei',
    'SimHei']

def _font(size, bold = (False,)):
    pass


def _theme():
    return THEMES[get_theme_key()]
def _hatch(painter, path, angle_deg, spacing, color):
    '''在 path 区域内画剖面线（clip 后按角度画平行线）'''
    painter.save()
    painter.setClipPath(path, Qt.IntersectClip)
    painter.setPen(QPen(color, 1))
    br = path.boundingRect()
    diag = math.hypot(br.width(), br.height())
    c = br.center()
    painter.translate(c)
    painter.rotate(angle_deg)
    n = int(diag / spacing) + 2
    for i in range(-n, n + 1):
        x = i * spacing
        painter.drawLine(QPointF(x, -diag / 2), QPointF(x, diag / 2))
        painter.restore()
        return None
def _dim_line(painter, x1, y1, x2, y2, color, text, text_dx, text_dy, bg):
    '''带双箭头的尺寸线与标注文字（bg=文字背景垫色，防止压在剖面线上发糊）'''
    pen = QPen(color, 1)
    painter.setPen(pen)
    painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))
    dy = y2 - y1
    dx = x2 - x1
    ln = math.hypot(dx, dy)
    if ln == 0:
        return None
    uy = dy / ln
    ux = None / ln
    for px, py, sgn in ((x1, y1, 1), (x2, y2, -1)):
        a1 = QPointF(px + sgn * (4 * ux - 2 * uy), py + sgn * (4 * uy + 2 * ux))
        a2 = QPointF(px + sgn * (4 * ux + 2 * uy), py + sgn * (4 * uy - 2 * ux))
        painter.drawLine(QPointF(px, py), a1)
        painter.drawLine(QPointF(px, py), a2)
        tx = (x1 + x2) / 2 + text_dx
        ty = (y1 + y2) / 2 + text_dy
        if not bg is None:
            fm = painter.fontMetrics()
            painter.fillRect(QRectF(tx - 2, ty - fm.ascent(), fm.horizontalAdvance(text) + 4, fm.height()), bg)
    painter.drawText(QPointF(tx, ty), text)
class KeySectionFigure:
    '''平键联接剖面图：上径向（端面）+ 下轴向（纵剖），上下双视图'''

    def __init__(self, parent):
        super().__init__(parent)
        self._params = None
        self.setMinimumHeight(430)
        self.setObjectName('figure')
    def set_params(self, d, b, h, t1, t2, L, hub_w, mark):
        self._params = dict(d = d, b = b, h = h, t1 = t1, t2 = t2, L = L, hub_w = hub_w, mark = mark)
        self.update()
    def clear(self):
        self._params = None
        self.update()
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        th = _theme()
        bg = QColor(th['CARD_BG'])
        p.fillRect(self.rect(), bg)
        if not self._params:
            p.setPen(QColor(th['TEXT_G']))
            p.drawText(self.rect(), Qt.AlignCenter, '查询后在此显示截面示意图')
            return None
        pr = None._params
        ink = QColor(th['TEXT_W'])
        dim = QColor(th['TEXT_G'])
        line = QColor(th['BORDER'])
        f_title = QFont('Microsoft YaHei', 10)
        f_title.setBold(True)
        f_lbl = QFont('Microsoft YaHei', 8)
        p.setPen(QPen(ink, 1))
        p.setFont(f_title)
        p.drawText(QRectF(0, 6, self.width(), 22), Qt.AlignCenter, pr['mark'] + '  联接剖面图')
        p.setFont(f_lbl)
        p.setPen(QPen(dim, 1))
        p.drawText(QRectF(0, 26, self.width(), 16), Qt.AlignCenter, '轴、键、毂剖面线方向区分｜键顶为非工作面，间隙两条线（放大显示）')
        H = self.height()
        W = self.width()
        body = H - HEAD_H
        y1 = HEAD_H + body * TV_RATIO
        y0 = HEAD_H
        p.setFont(f_lbl)
        p.setPen(QPen(ink, 1))
        p.drawText(QRectF(0, y0, W, SUB_H), Qt.AlignHCenter, '径向剖面（端面）')
        self._draw_transverse(p, th, ink, dim, line, y0 + SUB_H, y1)
        y1b = H
        y0b = y1
        p.setFont(f_lbl)
        p.setPen(QPen(ink, 1))
        p.drawText(QRectF(0, y0b, W, SUB_H), Qt.AlignHCenter, '轴向剖面（纵剖：轴、键不剖，仅毂画剖面线）')
        self._draw_longitudinal(p, th, ink, dim, line, y0b + SUB_H, y1b)
    def _draw_transverse(self, p, th, ink, dim, line, y0, y1):
        pr = self._params
        h = pr['h']
        b = pr['b']
        d = pr['d']
        t2 = pr['t2']
        t1 = pr['t1']
        wall = max(12, d * 0.45)
        avail_h = y1 - y0 - 10
        s = min(avail_h / (d + 2 * wall), 4.2)
        cx = self.width() / 2
        cy = y0 + avail_h / 2
        R = (d / 2) * s
        Rout = R + wall * s
        kb = (b / 2) * s
        y_shaft_kw_bot = cy - R - t1 * s
        y_key_top = y_shaft_kw_bot - h * s
        y_hub_kw_bot = min(cy - (R + t2 * s), y_key_top - GAP_MIN_PX)
        ann = QPainterPath()
        ann.addEllipse(QPointF(cx, cy), Rout, Rout)
        ann.addEllipse(QPointF(cx, cy), R, R)
        ann.setFillRule(Qt.OddEvenFill)
        slot = QPainterPath()
        slot.addRect(QRectF(cx - kb, y_hub_kw_bot, 2 * kb, (y_hub_kw_bot - cy - Rout) + 6))
        hub = ann.subtracted(slot)
        p.setPen(Qt.NoPen)
        p.fillPath(hub, QColor(th['CARD2']))
        _hatch(p, hub, 135, 7, QColor(th['TEXT_G']))
        p.setPen(QPen(ink, 1.6))
        p.setBrush(Qt.NoBrush)
        p.drawEllipse(QPointF(cx, cy), Rout, Rout)
        circ = QPainterPath()
        circ.addEllipse(QPointF(cx, cy), R, R)
        cut = QPainterPath()
        cut.addRect(QRectF(cx - kb, y_shaft_kw_bot, 2 * kb, (cy - R - y_shaft_kw_bot) + 3))
        shaft = circ.subtracted(cut)
        p.setPen(Qt.NoPen)
        p.fillPath(shaft, QColor(th['BG']))
        _hatch(p, shaft, 45, 7, QColor(th['TEXT_G']))
        p.setPen(QPen(ink, 1.6))
        p.setBrush(Qt.NoBrush)
        p.drawEllipse(QPointF(cx, cy), R, R)
        key = QPainterPath()
        key.addRect(QRectF(cx - kb, y_key_top, 2 * kb, h * s))
        p.setPen(Qt.NoPen)
        p.fillPath(key, QColor(th['ACCENT']))
        _hatch(p, key, 45, 3.5, QColor(0, 0, 0, 150) if th['SWATCH'] != '#f59e0b' else QColor(255, 255, 255, 170))
        p.setPen(QPen(ink, 1.6))
        p.setBrush(Qt.NoBrush)
        p.drawRect(QRectF(cx - kb, y_key_top, 2 * kb, h * s))
        p.setPen(QPen(ink, 1.2))
        p.drawLine(QPointF(cx - kb, y_hub_kw_bot), QPointF(cx + kb, y_hub_kw_bot))
        p.drawLine(QPointF(cx - kb, y_hub_kw_bot), QPointF(cx - kb, cy - R))
        p.drawLine(QPointF(cx + kb, y_hub_kw_bot), QPointF(cx + kb, cy - R))
        p.setFont(QFont('Microsoft YaHei', 8))
        yb = y_hub_kw_bot - 12
        _dim_line(p, cx - kb, yb, cx + kb, yb, dim, 'b=%g' % b, text_dx = -10, text_dy = -4, bg = QColor(th['CARD_BG']))
        _dim_line(p, cx, y_shaft_kw_bot, cx, cy + R, dim, '')
        txt_dt1 = 'd−t1=%g' % (d - t1)
        fm1 = p.fontMetrics()
        tx1 = cx - fm1.horizontalAdvance(txt_dt1) / 2
        ty1 = cy + R + 18
        p.fillRect(QRectF(tx1 - 3, ty1 - fm1.ascent() - 2, fm1.horizontalAdvance(txt_dt1) + 6, fm1.height() + 3), QColor(th['CARD_BG']))
        p.setPen(QPen(dim, 1))
        p.drawText(QPointF(tx1, ty1), txt_dt1)
    def _draw_longitudinal(self, p, th, ink, dim, line, y0, y1):
        pr = self._params
        h = pr['h']
        b = pr['b']
        d = pr['d']
        t2 = pr['t2']
        t1 = pr['t1']
        hub_w = pr['hub_w']
        L = pr['L']
        wall = max(10, d * 0.35)
        ext = 8
        span_mm = max(L + 2 * ext, hub_w + 2 * ext, 40)
        x0 = 60
        avail_w = self.width() - x0 - 70
        s = min(avail_w / span_mm, (y1 - y0 - 36) / (d + 2 * wall + t2))
        y_ax = y0 + (t2 + wall + d / 2) * s
        y_top = y_ax - (d / 2) * s
        y_bot = y_ax + (d / 2) * s
        W = (L + 2 * ext) * s
        xk1 = x0 + (ext + L) * s
        xk0 = x0 + ext * s
        xh0 = x0 + (ext - max(0, (hub_w - L) / 2)) * s
        xh1 = x0 + (ext + L + max(0, (hub_w - L) / 2)) * s
        xh1 = min(xh1, x0 + W)
        xh0 = max(xh0, x0)
        y_kw_bot = y_top + t1 * s
        y_key_top = y_kw_bot - h * s
        y_hub_kw_bot = min(y_top - t2 * s, y_key_top - GAP_MIN_PX)
        y_hub_top = y_hub_kw_bot - wall * s
        y_hub_bot = y_bot + wall * s
        hub_up = QPainterPath()
        poly = QPolygonF([
            QPointF(xh0, y_hub_top),
            QPointF(xh1, y_hub_top),
            QPointF(xh1, y_top),
            QPointF(xk1, y_top),
            QPointF(xk1, y_hub_kw_bot),
            QPointF(xk0, y_hub_kw_bot),
            QPointF(xk0, y_top),
            QPointF(xh0, y_top)])
        hub_up.addPolygon(poly)
        hub_up.closeSubpath()
        p.setPen(Qt.NoPen)
        p.fillPath(hub_up, QColor(th['CARD2']))
        _hatch(p, hub_up, 135, 7, QColor(th['TEXT_G']))
        p.setPen(QPen(ink, 1.6))
        p.setBrush(Qt.NoBrush)
        p.drawPath(hub_up)
        hub_lo = QPainterPath()
        hub_lo.addRect(QRectF(xh0, y_bot, xh1 - xh0, wall * s))
        p.setPen(Qt.NoPen)
        p.fillPath(hub_lo, QColor(th['CARD2']))
        _hatch(p, hub_lo, 135, 7, QColor(th['TEXT_G']))
        p.setPen(QPen(ink, 1.6))
        p.setBrush(Qt.NoBrush)
        p.drawRect(QRectF(xh0, y_bot, xh1 - xh0, wall * s))
        shaft = QPainterPath()
        poly2 = QPolygonF([
            QPointF(x0, y_bot),
            QPointF(x0, y_top),
            QPointF(xk0, y_top),
            QPointF(xk0, y_kw_bot),
            QPointF(xk1, y_kw_bot),
            QPointF(xk1, y_top),
            QPointF(x0 + W, y_top),
            QPointF(x0 + W, y_bot)])
        shaft.addPolygon(poly2)
        shaft.closeSubpath()
        p.setPen(Qt.NoPen)
        p.fillPath(shaft, QColor(th['CARD2']))
        p.setPen(QPen(ink, 1.6))
        p.setBrush(Qt.NoBrush)
        p.drawPath(shaft)
        key_rect = QRectF(xk0, y_kw_bot - h * s, xk1 - xk0, h * s)
        p.setPen(Qt.NoPen)
        p.fillRect(key_rect, QColor(th['ACCENT']))
        p.setPen(QPen(ink, 1.6))
        p.setBrush(Qt.NoBrush)
        p.drawRect(key_rect)
        p.setPen(QPen(ink, 1.2))
        p.drawLine(QPointF(xh0, y_hub_kw_bot), QPointF(xh1, y_hub_kw_bot))
        p.setFont(QFont('Microsoft YaHei', 8))
        yL = y_hub_bot + 14
        _dim_line(p, xk0, yL, xk1, yL, dim, 'L=%g' % L, text_dx = -14, text_dy = 12, bg = QColor(th['CARD_BG']))
        p.setPen(QPen(dim, 1))
        p.drawLine(QPointF((xk0 + xk1) * 0.5, y_kw_bot), QPointF((xk0 + xk1) * 0.5 + 26, y_kw_bot + 14))
        p.drawText(QPointF((xk0 + xk1) * 0.5 + 28, y_kw_bot + 18), 't1=%g' % t1)
        p.drawLine(QPointF(xh1 - 8, y_hub_kw_bot), QPointF(xh1 + 14, y_hub_kw_bot - 12))
        p.drawText(QPointF(xh1 + 16, y_hub_kw_bot - 10), 't2=%g' % t2)
    __classcell__ = None
class SplineFigure:
    '''矩形花键端面简图：小径 d、大径 D、N 个均布键齿（GB/T 1144 规格参数化）'''

    def __init__(self, parent):
        super().__init__(parent)
        self._params = None
        self.setMinimumHeight(300)
        self.setObjectName('figure')
    def set_params(self, N, d_small, D, B, mark):
        self._params = dict(N = int(N), d = d_small, D = D, B = B, mark = mark)
        self.update()
    def clear(self):
        self._params = None
        self.update()
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        th = _theme()
        p.fillRect(self.rect(), QColor(th['CARD_BG']))
        if not self._params:
            p.setPen(QColor(th['TEXT_G']))
            p.drawText(self.rect(), Qt.AlignCenter, '选择花键记录后在此显示端面简图')
            return None
        pr = None._params
        ink = QColor(th['TEXT_W'])
        dim = QColor(th['TEXT_G'])
        (N, d_sm, D, B) = (pr['N'], pr['d'], pr['D'], pr['B'])
        f_title = QFont('Microsoft YaHei', 10)
        f_title.setBold(True)
        f_lbl = QFont('Microsoft YaHei', 8)
        p.setPen(QPen(ink, 1))
        p.setFont(f_title)
        p.drawText(QRectF(0, 6, self.width(), 22), Qt.AlignCenter, pr['mark'] + '  ' if pr['mark'] else '' + '花键端面简图')
        p.setFont(f_lbl)
        p.setPen(QPen(dim, 1))
        p.drawText(QRectF(0, 26, self.width(), 16), Qt.AlignCenter, 'N 个矩形齿均布｜小径 d 定心｜B 为键齿(槽)宽')
        cy = (self.height() + HEAD_H) / 2
        cx = self.width() / 2
        s = min((self.height() - HEAD_H - 70) / 2 / D, (self.width() - 150) / 2 / D, 6)
        r_in = (d_sm / 2) * s
        r_out = (D / 2) * s
        p.setPen(QPen(ink, 1.6))
        p.setBrush(Qt.NoBrush)
        p.drawEllipse(QPointF(cx, cy), r_in, r_in)
        p.drawEllipse(QPointF(cx, cy), r_out, r_out)
        half_b = (B / 2) * s
        p.setBrush(QColor(th['ACCENT']))
        p.setPen(QPen(ink, 1.2))
        for i in range(N):
            ang = 2 * math.pi * i / N - math.pi / 2
            sa = math.sin(ang)
            ca = math.cos(ang)
            ny = ca
            nx = -sa
            p.drawLine(QPointF(cx + nx * half_b + ca * r_in, cy + ny * half_b + sa * r_in), QPointF(cx + nx * half_b + ca * r_out, cy + ny * half_b + sa * r_out))
            p.drawLine(QPointF((cx - nx * half_b) + ca * r_in, (cy - ny * half_b) + sa * r_in), QPointF((cx - nx * half_b) + ca * r_out, (cy - ny * half_b) + sa * r_out))
            p.drawLine(QPointF(cx + nx * half_b + ca * r_out, cy + ny * half_b + sa * r_out), QPointF((cx - nx * half_b) + ca * r_out, (cy - ny * half_b) + sa * r_out))
            pen_c = QPen(dim, 1, Qt.DashLine)
            p.setPen(pen_c)
            ext = 8
            p.drawLine(QPointF(cx - r_out - ext, cy), QPointF(cx + r_out + ext, cy))
            p.drawLine(QPointF(cx, cy - r_out - ext), QPointF(cx, cy + r_out + ext))
            p.setFont(f_lbl)
            _dim_line(p, cx - r_out, cy - r_out - 14, cx + r_out, cy - r_out - 14, dim, 'D=%g' % D, text_dx = -8, text_dy = -4, bg = QColor(th['CARD_BG']))
            _dim_line(p, cx - r_in, cy + r_in + 14, cx + r_in, cy + r_in + 14, dim, 'd=%g' % d_sm, text_dx = -8, text_dy = 10, bg = QColor(th['CARD_BG']))
            p.setPen(QPen(ink, 1))
            p.drawText(QPointF(cx + r_in + 10, cy - r_in - 6), 'N=%d 齿, B=%g' % (N, B))
            return None
    __classcell__ = None
class MarginBar:
    '''强度利用率条：绿(<70%) → 黄(70~100%) → 红(>100%)，100% 处画刻度线'''

    def __init__(self, parent):
        super().__init__(parent)
        self._name = ''
        self._value = 0
        self._allow = 0
        self._ratio = 0
        self.setMinimumHeight(42)
        self.setObjectName('figure')
    def set_value(self, name, value, allowable):
        self._name = name
        self._value = float(value)
        self._allow = float(allowable)
        self._ratio = self._value / self._allow if self._allow > 0 else 0
        self.update()
    def clear(self):
        self._name = ''
        self.update()
    def paintEvent(self, event):
        if not self._name:
            return None
        p = None(self)
        p.setRenderHint(QPainter.Antialiasing)
        th = _theme()
        hgt = self.height()
        w = self.width()
        bar_h = 12
        y = 5
        x_name_end = 110
        track = QRectF(x_name_end, y, w - x_name_end - 24, bar_h)
        p.setPen(QPen(QColor(th['BORDER']), 1))
        p.setBrush(QColor(th['CARD2']))
        p.drawRoundedRect(track, 4, 4)
        ratio = self._ratio
        fill_w = track.width() * min(ratio, 1)
        color = QColor(th['GREEN'])
        if ratio > 1:
            color = QColor(th['DANGER'])
        elif ratio > 0.7:
            color = QColor(th['WARN'])
        p.setPen(Qt.NoPen)
        p.setBrush(color)
        p.drawRoundedRect(QRectF(track.x(), track.y(), fill_w, bar_h), 4, 4)
        p.setPen(QPen(QColor(th['TEXT_G']), 1))
        p.drawLine(QPointF(track.right(), y - 3), QPointF(track.right(), y + bar_h + 3))
        p.setPen(QColor(th['TEXT_W']))
        p.setFont(QFont('Microsoft YaHei', 9))
        p.drawText(QPointF(8, y + bar_h - 1), self._name)
        state = '满足' if ratio <= 1 else '超限!'
        txt = '%.1f / [%.0f] MPa · 利用率 %.0f%% · %s' % (self._value, self._allow, ratio * 100, state)
        p.drawText(QPointF(8, y + bar_h + 22), txt)
    __classcell__ = None
class WoodruffFigure:
    '''半圆键联接示意：上轴向剖面（月牙键坐弧形轴槽）+ 下径向端面（两侧工作面）'''

    def __init__(self, parent):
        super().__init__(parent)
        self._params = None
        self.setMinimumHeight(400)
        self.setObjectName('figure')
    def set_params(self, d, b, h, d1, code, hub_w):
        self._params = dict(d = float(d), b = float(b), h = float(h), d1 = float(d1), code = code, hub_w = hub_w)
        self.update()
    def clear(self):
        self._params = None
        self.update()
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        th = _theme()
        p.fillRect(self.rect(), QColor(th['CARD_BG']))
        if not self._params:
            p.setPen(QColor(th['TEXT_G']))
            p.drawText(self.rect(), Qt.AlignCenter, '查询后在此显示半圆键联接示意图')
            return None
        pr = None._params
        dim = QColor(th['TEXT_G'])
        ink = QColor(th['TEXT_W'])
        p.setPen(QPen(ink, 1))
        p.setFont(_font(10, True))
        p.drawText(QRectF(0, 6, self.width(), 22), Qt.AlignCenter, pr['code'] + '  ' if pr['code'] else '' + '半圆键联接示意图')
        p.setFont(_font(8))
        p.setPen(QPen(dim, 1))
        p.drawText(QRectF(0, 26, self.width(), 16), Qt.AlignCenter, '两侧面为工作面｜键可沿槽底圆弧摆动以适应毂槽底面｜轴槽由半圆键槽铣刀（GB/T 1127）加工')
        H = self.height()
        W = self.width()
        body = H - HEAD_H
        y1 = HEAD_H + body * TV_RATIO
        y0 = HEAD_H
        p.setFont(_font(8))
        p.setPen(QPen(ink, 1))
        p.drawText(QRectF(0, y0, W, SUB_H), Qt.AlignHCenter, '轴向剖面（沿轴线：月牙键落在弧形槽中）')
        self._draw_longitudinal(p, th, ink, dim, y0 + SUB_H, y1)
        y1b = H
        y0b = y1
        p.setPen(QPen(ink, 1))
        p.drawText(QRectF(0, y0b, W, SUB_H), Qt.AlignHCenter, '径向端面（键宽 b，两侧面工作）')
        self._draw_transverse(p, th, ink, dim, y0b + SUB_H, y1b)
    def _draw_longitudinal(self, p, th, ink, dim, y0, y1):
        pr = self._params
        d1 = pr['d1']
        h = pr['h']
        d = pr['d']
        Rs_mm = d1 / 2
        t = h / 2
        wall = max(10, d * 0.35)
        ext = max(10, d * 0.55)
        span = d1 + 2 * ext
        x0 = 66
        avail_w = self.width() - x0 - 76
        avail_h = y1 - y0 - 34
        s = min(avail_w / span, avail_h / (d + 2 * wall + h), 6)
        W = span * s
        y_ax = y0 + (h + wall + d / 2) * s
        y_bot = y_ax + (d / 2) * s
        y_top = y_ax - (d / 2) * s
        Rs = Rs_mm * s
        cx = x0 + W / 2
        Oy = y_top + t * s - Rs
        shaft = QPainterPath()
        shaft.addRect(QRectF(x0, y_top, W, y_bot - y_top))
        cut = QPainterPath()
        cut.addEllipse(QPointF(cx, Oy), Rs, Rs)
        shaft = shaft.subtracted(cut)
        p.setPen(Qt.NoPen)
        p.fillPath(shaft, QColor(th['CARD2']))
        p.setPen(QPen(ink, 1.6))
        p.setBrush(Qt.NoBrush)
        p.drawPath(shaft)
        ky_bot = Oy + Rs
        ky_top = ky_bot - h * s
        dy = ky_top - Oy
        half = math.sqrt(max(Rs * Rs - dy * dy, 0))
        th_b = math.atan2(dy, half)
        th_a = math.atan2(dy, -half)
        pts = [
            QPointF(cx + half, ky_top)]
        n = 48
        for i in range(n + 1):
            a = th_b + (th_a - th_b) * i / n
            pts.append(QPointF(cx + Rs * math.cos(a), Oy + Rs * math.sin(a)))
            pts.append(QPointF(cx - half, ky_top))
            key = QPainterPath()
            key.addPolygon(QPolygonF(pts))
            key.closeSubpath()
            p.setPen(Qt.NoPen)
            p.fillPath(key, QColor(th['ACCENT']))
            p.setPen(QPen(ink, 1.6))
            p.setBrush(Qt.NoBrush)
            p.drawPath(key)
            hub_top = min(ky_top - wall * s, y0 + 2)
            xh1 = x0 + W - ext * 0.5 * s
            xh0 = x0 + ext * 0.5 * s
            gap_l = cx - half - 1.5
            gap_r = cx + half + 1.5
            poly = QPolygonF([
                QPointF(xh0, hub_top),
                QPointF(xh1, hub_top),
                QPointF(xh1, y_top),
                QPointF(gap_r, y_top),
                QPointF(gap_r, ky_top),
                QPointF(gap_l, ky_top),
                QPointF(gap_l, y_top),
                QPointF(xh0, y_top)])
            hub = QPainterPath()
            hub.addPolygon(poly)
            hub.closeSubpath()
            p.setPen(Qt.NoPen)
            p.fillPath(hub, QColor(th['CARD2']))
            _hatch(p, hub, 135, 7, QColor(th['TEXT_G']))
            p.setPen(QPen(ink, 1.6))
            p.setBrush(Qt.NoBrush)
            p.drawPath(hub)
            p.setFont(_font(8))
            _dim_line(p, cx - half, ky_top - 12, cx + half, ky_top - 12, dim, 'd1=%g' % d1, text_dx = -12, text_dy = -4, bg = QColor(th['CARD_BG']))
            p.setPen(QPen(dim, 1))
            p.drawLine(QPointF(cx + Rs + 4, ky_top), QPointF(cx + Rs + 22, ky_top))
            p.drawLine(QPointF(cx + Rs + 4, ky_bot), QPointF(cx + Rs + 22, ky_bot))
            p.drawLine(QPointF(cx + Rs + 18, ky_top), QPointF(cx + Rs + 18, ky_bot))
            p.drawText(QPointF(cx + Rs + 24, (ky_top + ky_bot) / 2 + 3), 'h=%g' % h)
            _dim_line(p, cx - Rs - 14, ky_top, cx - Rs - 14, y_top, dim, 'k=%g' % h / 2, text_dx = -24, text_dy = 4, bg = QColor(th['CARD_BG']))
            p.setPen(QPen(QColor(th['ACCENT_H']), 1.2))
            sw = QRectF(cx - Rs * 0.55, ky_bot - Rs * 0.35, Rs * 1.1, Rs * 0.7)
            p.drawArc(sw, int(3200), int(2240))
            p.setPen(QPen(dim, 1))
            p.drawText(QPointF(8, y_bot + 18), '轴槽圆弧由同直径半圆键槽铣刀切出；键可沿槽底圆弧微摆，装配时自动贴合毂槽底面')
            p.drawText(QPointF(8, y_bot + 32), '槽深按本工具校核口径 k=h/2 示画，实际键槽尺寸按 GB/T 1098 查表')
            return None
    def _draw_transverse(self, p, th, ink, dim, y0, y1):
        pr = self._params
        h = pr['h']
        b = pr['b']
        d = pr['d']
        wall = max(12, d * 0.45)
        avail_h = y1 - y0 - 10
        s = min(avail_h / (d + 2 * wall), 4.2)
        cy = y0 + avail_h / 2
        cx = self.width() / 2
        R = (d / 2) * s
        Rout = R + wall * s
        kb = (b / 2) * s
        t = h / 2
        y_kw_bot = cy - R - t * s
        y_key_top = y_kw_bot - h * s
        y_hub_kw_bot = y_key_top
        ann = QPainterPath()
        ann.addEllipse(QPointF(cx, cy), Rout, Rout)
        ann.addEllipse(QPointF(cx, cy), R, R)
        ann.setFillRule(Qt.OddEvenFill)
        slot = QPainterPath()
        slot.addRect(QRectF(cx - kb, y_hub_kw_bot, 2 * kb, (y_hub_kw_bot - cy - Rout) + 6))
        hub = ann.subtracted(slot)
        p.setPen(Qt.NoPen)
        p.fillPath(hub, QColor(th['CARD2']))
        _hatch(p, hub, 135, 7, QColor(th['TEXT_G']))
        p.setPen(QPen(ink, 1.6))
        p.setBrush(Qt.NoBrush)
        p.drawEllipse(QPointF(cx, cy), Rout, Rout)
        circ = QPainterPath()
        circ.addEllipse(QPointF(cx, cy), R, R)
        cutp = QPainterPath()
        cutp.addRect(QRectF(cx - kb, y_kw_bot, 2 * kb, (cy - R - y_kw_bot) + 3))
        shaft = circ.subtracted(cutp)
        p.setPen(Qt.NoPen)
        p.fillPath(shaft, QColor(th['BG']))
        _hatch(p, shaft, 45, 7, QColor(th['TEXT_G']))
        p.setPen(QPen(ink, 1.6))
        p.setBrush(Qt.NoBrush)
        p.drawEllipse(QPointF(cx, cy), R, R)
        key = QPainterPath()
        key.addRect(QRectF(cx - kb, y_key_top, 2 * kb, h * s))
        p.setPen(Qt.NoPen)
        p.fillPath(key, QColor(th['ACCENT']))
        p.setPen(QPen(ink, 1.6))
        p.setBrush(Qt.NoBrush)
        p.drawRect(QRectF(cx - kb, y_key_top, 2 * kb, h * s))
        p.setFont(_font(8))
        _dim_line(p, cx - kb, y_hub_kw_bot - 12, cx + kb, y_hub_kw_bot - 12, dim, 'b=%g' % b, text_dx = -10, text_dy = -4, bg = QColor(th['CARD_BG']))
        p.setPen(QPen(QColor(th['ACCENT_H']), 1))
        p.drawText(QPointF(cx + Rout * 0.62, cy), '两侧面＝工作面（传扭）')
    __classcell__ = None
class TaperFigure:
    '''楔键联接示意：上轴向剖面（1:100 楔紧）+ 下径向端面（上下面工作、两侧留隙）'''

    def __init__(self, parent):
        super().__init__(parent)
        self._params = None
        self.setMinimumHeight(400)
        self.setObjectName('figure')
    def set_params(self, d, b, h, L, hub_w, hook, mark):
        self._params = dict(d = float(d), b = float(b), h = float(h), L = float(L), hub_w = float(hub_w), hook = bool(hook), mark = mark)
        self.update()
    def clear(self):
        self._params = None
        self.update()
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        th = _theme()
        p.fillRect(self.rect(), QColor(th['CARD_BG']))
        if not self._params:
            p.setPen(QColor(th['TEXT_G']))
            p.drawText(self.rect(), Qt.AlignCenter, '查询后在此显示楔键联接示意图')
            return None
        pr = None._params
        dim = QColor(th['TEXT_G'])
        ink = QColor(th['TEXT_W'])
        p.setPen(QPen(ink, 1))
        p.setFont(_font(10, True))
        p.drawText(QRectF(0, 6, self.width(), 22), Qt.AlignCenter, pr['mark'] + '  ' if pr['mark'] else '' + '钩头楔键' if pr['hook'] else '楔键' + '联接示意图')
        p.setFont(_font(8))
        p.setPen(QPen(dim, 1))
        p.drawText(QRectF(0, 26, self.width(), 16), Qt.AlignCenter, '上下面为工作面（1:100 斜度，夸大显示）｜两侧面留间隙为非工作面｜打入楔紧后靠摩擦传扭')
        H = self.height()
        W = self.width()
        body = H - HEAD_H
        y1 = HEAD_H + body * TV_RATIO
        y0 = HEAD_H
        p.setFont(_font(8))
        p.setPen(QPen(ink, 1))
        p.drawText(QRectF(0, y0, W, SUB_H), Qt.AlignHCenter, '轴向剖面（打紧方向 →；楔紧使轴上零件偏心，对中精度不高）')
        self._draw_longitudinal(p, th, ink, dim, y0 + SUB_H, y1)
        y1b = H
        y0b = y1
        p.setPen(QPen(ink, 1))
        p.drawText(QRectF(0, y0b, W, SUB_H), Qt.AlignHCenter, '径向端面（标出两侧的非工作面间隙）')
        self._draw_transverse(p, th, ink, dim, y0b + SUB_H, y1b)
    def _draw_longitudinal(self, p, th, ink, dim, y0, y1):
        pr = self._params
        (d, h, L, hub_w, hook) = (pr['d'], pr['h'], pr['L'], pr['hub_w'], pr['hook'])
        wall = max(10, d * 0.35)
        ext = max(12, d * 0.5)
        span = max(L + 2 * ext, hub_w + 2 * ext, 40)
        x0 = 60
        avail_w = self.width() - x0 - 84
        avail_h = y1 - y0 - 84
        s = min(avail_w / span, avail_h / (d + 2 * wall + h * 1.2), 6)
        W = span * s
        y_ax = y0 + (h * 0.9 + wall + d / 2) * s
        y_bot = y_ax + (d / 2) * s
        y_top = y_ax - (d / 2) * s
        off_h = max(0, (L - hub_w) / 2) * s
        off_k = max(0, (hub_w - L) / 2) * s
        xh1 = x0 + ext * s + off_h + hub_w * s
        xh0 = x0 + ext * s + off_h
        xk1 = x0 + ext * s + off_k + L * s
        xk0 = x0 + ext * s + off_k
        embed = h * 0.25 * s
        slope = max(7, L * s * 0.055)
        y_kbot = y_top + embed
        y_ktop_r = y_kbot - h * s
        y_ktop_l = y_ktop_r + slope
        shaft = QPainterPath()
        poly = QPolygonF([
            QPointF(x0, y_bot),
            QPointF(x0, y_top),
            QPointF(xk0, y_top),
            QPointF(xk0, y_kbot),
            QPointF(xk1, y_kbot),
            QPointF(xk1, y_top),
            QPointF(x0 + W, y_top),
            QPointF(x0 + W, y_bot)])
        shaft.addPolygon(poly)
        shaft.closeSubpath()
        p.setPen(Qt.NoPen)
        p.fillPath(shaft, QColor(th['CARD2']))
        p.setPen(QPen(ink, 1.6))
        p.setBrush(Qt.NoBrush)
        p.drawPath(shaft)
        krect = QPolygonF([
            QPointF(xk0, y_ktop_l),
            QPointF(xk1, y_ktop_r),
            QPointF(xk1, y_kbot),
            QPointF(xk0, y_kbot)])
        key = QPainterPath()
        key.addPolygon(krect)
        key.closeSubpath()
        p.setPen(Qt.NoPen)
        p.fillPath(key, QColor(th['ACCENT']))
        p.setPen(QPen(ink, 1.6))
        p.setBrush(Qt.NoBrush)
        p.drawPath(key)
        if hook:
            hk_w = max(12, h * s * 0.85)
            hk_h = max(16, h * s * 1.05)
            xh_b = xk1 + hk_w
            xh_a = xk1
            y_hk_top = y_ktop_r - hk_h
            hook_path = QPainterPath()
            hook_path.addPolygon(QPolygonF([
                QPointF(xh_a, y_hk_top),
                QPointF(xh_b, y_hk_top),
                QPointF(xh_b, y_kbot),
                QPointF(xh_a, y_kbot)]))
            hook_path.closeSubpath()
            p.setPen(Qt.NoPen)
            p.fillPath(hook_path, QColor(th['ACCENT']))
            p.setPen(QPen(ink, 1.6))
            p.setBrush(Qt.NoBrush)
            p.drawPath(hook_path)
            p.setPen(QPen(dim, 1))
            p.drawText(QPointF(xh_b + 6, (y_hk_top + y_kbot) / 2), '钩头（拆卸用）')
        hub_top = min(y_ktop_l - wall * s, y0 + 2)
        hp = QPolygonF([
            QPointF(xh0, hub_top),
            QPointF(xh1, hub_top),
            QPointF(xh1, y_top),
            QPointF(min(xk1, xh1), y_top),
            QPointF(min(xk1, xh1), y_ktop_r),
            QPointF(max(xk0, xh0), y_ktop_l),
            QPointF(max(xk0, xh0), y_top),
            QPointF(xh0, y_top)])
        hub = QPainterPath()
        hub.addPolygon(hp)
        hub.closeSubpath()
        p.setPen(Qt.NoPen)
        p.fillPath(hub, QColor(th['CARD2']))
        _hatch(p, hub, 135, 7, QColor(th['TEXT_G']))
        p.setPen(QPen(ink, 1.6))
        p.setBrush(Qt.NoBrush)
        p.drawPath(hub)
        ay = y_bot + 16
        p.setPen(QPen(QColor(th['ACCENT_H']), 1.6))
        p.drawLine(QPointF(xk0, ay), QPointF(xk1 + 0 if not hook else 14, ay))
        p.drawLine(QPointF(xk1 + 0 if not hook else 14, ay), QPointF((xk1 - 8) + 0 if not hook else 14, ay - 4))
        p.drawLine(QPointF(xk1 + 0 if not hook else 14, ay), QPointF((xk1 - 8) + 0 if not hook else 14, ay + 4))
        p.setPen(QPen(dim, 1))
        p.drawText(QPointF(xk0, ay + 16), '打紧方向')
        p.setFont(_font(8))
        _dim_line(p, xk0, ay + 30, xk1, ay + 30, dim, 'L=%g' % L, text_dx = -14, text_dy = 12, bg = QColor(th['CARD_BG']))
        p.setPen(QPen(dim, 1))
        notes = [
            '键的上表面与毂槽底面均有 1:100 斜度（图中夸大显示）；',
            '键槽深度按 GB/T 1563 规定，本工具未录入，图中为浅槽示意']
        if hook:
            notes.append('钩头端面与轮毂端面间应留出距离，便于拆卸（装入后钩头外露）')
        for i, txt in enumerate(notes):
            p.drawText(QPointF(8, ay + 56 + i * 14), txt)
            return None
    def _draw_transverse(self, p, th, ink, dim, y0, y1):
        pr = self._params
        h = pr['h']
        b = pr['b']
        d = pr['d']
        wall = max(12, d * 0.45)
        avail_h = y1 - y0 - 10
        s = min(avail_h / (d + 2 * wall), 4.2)
        cy = y0 + avail_h / 2
        cx = self.width() / 2
        R = (d / 2) * s
        Rout = R + wall * s
        kb = (b / 2) * s
        gap_px = max(2.5, b * 0.12 * s)
        embed = h * 0.25 * s
        y_kbot = cy - R - embed
        y_ktop = y_kbot - h * s
        ann = QPainterPath()
        ann.addEllipse(QPointF(cx, cy), Rout, Rout)
        ann.addEllipse(QPointF(cx, cy), R, R)
        ann.setFillRule(Qt.OddEvenFill)
        slot = QPainterPath()
        slot.addRect(QRectF(cx - kb - gap_px, y_ktop - 4, 2 * (kb + gap_px), (y_ktop - cy - Rout) + 8))
        hub = ann.subtracted(slot)
        p.setPen(Qt.NoPen)
        p.fillPath(hub, QColor(th['CARD2']))
        _hatch(p, hub, 135, 7, QColor(th['TEXT_G']))
        p.setPen(QPen(ink, 1.6))
        p.setBrush(Qt.NoBrush)
        p.drawEllipse(QPointF(cx, cy), Rout, Rout)
        circ = QPainterPath()
        circ.addEllipse(QPointF(cx, cy), R, R)
        cutp = QPainterPath()
        cutp.addRect(QRectF(cx - kb, y_kbot, 2 * kb, (cy - R - y_kbot) + 3))
        shaft = circ.subtracted(cutp)
        p.setPen(Qt.NoPen)
        p.fillPath(shaft, QColor(th['BG']))
        _hatch(p, shaft, 45, 7, QColor(th['TEXT_G']))
        p.setPen(QPen(ink, 1.6))
        p.setBrush(Qt.NoBrush)
        p.drawEllipse(QPointF(cx, cy), R, R)
        key = QRectF(cx - kb, y_ktop, 2 * kb, h * s)
        p.setPen(Qt.NoPen)
        p.fillRect(key, QColor(th['ACCENT']))
        p.setPen(QPen(ink, 1.6))
        p.setBrush(Qt.NoBrush)
        p.drawRect(key)
        p.setFont(_font(8))
        _dim_line(p, cx - kb, y_ktop - 14, cx + kb, y_ktop - 14, dim, 'b=%g' % b, text_dx = -10, text_dy = -4, bg = QColor(th['CARD_BG']))
        p.setPen(QPen(QColor(th['ACCENT_H']), 1))
        p.drawText(QPointF(cx + kb + 4, y_ktop + h * s * 0.45), '间隙')
        p.drawText(QPointF(cx - kb - 30, y_ktop + h * s * 0.45), '间隙')
        p.drawText(QPointF(cx - Rout - 10, y1 - 8), '上下面＝工作面（传扭／承受单向轴向力）')
    __classcell__ = None
class FigurePanel:
    '''示意图折叠容器。

    2026-10-03 改：用户反馈「没看到示意图」——此前按页面精简纪律默认收起成一行
    按钮，而按钮被结果文本挤到视口外 267~457px，等于不可见。示意图是用户明确
    提出要的内容，不是可折叠的次要信息，故改为**默认展开**，并在挂图后把所在
    滚动区定位到图（reveal），需要时仍可点标题行收起。
    set_figure(None) → 整个面板隐藏（未查询或该方案无图时不占位）。
    '''

    def __init__(self, parent, title, open_by_default):
        super().__init__(parent)
        self._fig = None
        self._open = bool(open_by_default)
        self._title = title
        v = QVBoxLayout(self)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(4)
        row = QHBoxLayout()
        row.setSpacing(8)
        self.btn = QPushButton(title + ' ▾')
        self.btn.setObjectName('mini')
        self.btn.setCursor(Qt.PointingHandCursor)
        self.btn.clicked.connect(self.toggle)
        row.addWidget(self.btn)
        self.summary = QLabel('')
        self.summary.setObjectName('hint')
        row.addWidget(self.summary)
        row.addStretch()
        v.addLayout(row)
        self._host = QWidget()
        hv = QVBoxLayout(self._host)
        hv.setContentsMargins(0, 0, 0, 0)
        hv.setSpacing(0)
        v.addWidget(self._host)
        self._host.setVisible(False)
        self.setVisible(False)
    def toggle(self):
        self._open = not (self._open)
        if self._open:
            self._host.setVisible(self._fig is not None)
        self.btn.setText(self._title + ' ▴' if self._open else ' ▾')
        if not self._open or self._fig is None:
            QTimer.singleShot(0, self.reveal)
            QTimer.singleShot(80, self.reveal)
            return None
        return None
    def set_figure(self, fig, summary):
        '''换图：先摘掉旧图（deleteLater 防泄漏），再挂新图；未查询→整体隐藏'''
        if not self._fig is None:
            self._host.layout().removeWidget(self._fig)
            self._fig.setParent(None)
            self._fig.deleteLater()
        self._fig = fig
        if not fig is None:
            self._host.layout().addWidget(fig)
        self.summary.setText(summary)
        self.setVisible(fig is not None)
        self.btn.setText(self._title + ' ▴' if self._open else ' ▾')
        if self._open:
            self._host.setVisible(fig is not None)
            if fig is None or self._open:
                QTimer.singleShot(0, self.reveal)
                QTimer.singleShot(80, self.reveal)
                return None
            return None
        return self._open
    def reveal(self):
        '''把本面板滚到视野中（挂图后自动调用）。

            2026-10-03 二次修：v2.3.26 的判断是「图顶边在视口内就不滚」，结果只露出
            21%~39%（半圆键页 125/520px），用户仍然看不到图。现改为按**可见高度**
            判定：要求至少露出 min(整图高, 视口高) 的 90%，否则滚动——
            · 图高于视口 → 顶对齐，露出尽可能多；
            · 图能整幅放下 → 底对齐，整图进视野且上方尽量多留结果文字作上下文。
            '''
        if not self.isVisible() and self._fig is None or self._open:
            return None
        sa = None.parent()
        if not sa is None and isinstance(sa, QScrollArea):
            sa = sa.parent()
            if not sa is None:
                if not isinstance(sa, QScrollArea) or sa is None or sa.widget() is not None:
                    return None
                content = isinstance(sa, QScrollArea).widget()
                vp_h = sa.viewport().height()
                if vp_h <= 0:
                    return None
                y = None.mapTo(content, QPoint(0, 0)).y()
                h = self.height()
                if h <= 0:
                    return None
                sb = None.verticalScrollBar()
                cur = sb.value()
                shown = max(0, min(y + h, cur + vp_h) - max(y, cur))
                want = min(h, vp_h - 8)
                if shown >= want * 0.9:
                    return None
                if None >= vp_h - 8:
                    target = y - 8
                else:
                    target = min(y - 8, (y + h - vp_h) + 8)
        sb.setValue(max(0, int(target)))
    __classcell__ = None
def make_key_figure(kind):
    '''按键型给出对应示意图实例；无图型返回 None'''
    if kind == 'parallel':
        return KeySectionFigure()
    if None == 'woodruff':
        return WoodruffFigure()
    if None in ('taper', 'taper_hook'):
        return TaperFigure()
    if None == 'spline':
        return SplineFigure()

