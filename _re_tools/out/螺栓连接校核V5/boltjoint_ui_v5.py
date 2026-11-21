# Reconstructed from bytecode by split_decompile.py
# boltjoint_ui_v5.pyc

'''BoltJointTool V5 - 可视化螺栓校核'''
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox, QLabel, QComboBox, QSpinBox, QDoubleSpinBox, QPushButton, QFrame, QMessageBox, QScrollArea
from PySide6.QtCore import Qt, QTimer, QPointF, QRectF
from PySide6.QtGui import QPainter, QColor, QPen, QFont, QPolygonF, QPainterPath
import math
from boltjoint_calcs_v3 import BOLT_MATERIALS, PLATE_MATERIALS, FRICTION_COEFFICIENTS, BOLT_SIZES, calculate_bolt_joint, calculate_screw_joint, calculate_preload, calculate_bolt_length

class _ArrowMixin:
    '''共用三角箭头绘制 + 点击区域检测'''
    _BTN_W = 24

    def _draw_arrows(self, p):
        h = self.height()
        w = self.width()
        cx = w - self._BTN_W // 2
        p.setBrush(QColor('#99aabb'))
        p.setPen(Qt.NoPen)
        tri_up = QPolygonF([
            QPointF(cx - 5, h * 0.3),
            QPointF(cx + 5, h * 0.3),
            QPointF(cx, h * 0.15)])
        p.drawPolygon(tri_up)
        p.setBrush(QColor('#667788'))
        tri_dn = QPolygonF([
            QPointF(cx - 5, h * 0.7),
            QPointF(cx + 5, h * 0.7),
            QPointF(cx, h * 0.85)])
        p.drawPolygon(tri_dn)
    def _hit_test(self, event):
        x = event.position().x() if hasattr(event, 'position') else event.x()
        w = self.width()
        return x > w - self._BTN_W
    def stepUp(self):
        self.setValue(self.value() + self.singleStep())
    def stepDown(self):
        self.setValue(self.value() - self.singleStep())
class ArrowSpinBox:
    '''自定义QDoubleSpinBox：右侧三角箭头 + 清晰边框'''

    def __init__(self, *args, **kwargs):
        pass
    # WARNING: Decompyle incomplete
    def paintEvent(self, event):
        super().paintEvent(event)
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        self._draw_arrows(p)
        p.end()
    def mousePressEvent(self, event):
        x = event.position().x() if hasattr(event, 'position') else event.x()
        y = event.position().y() if hasattr(event, 'position') else event.y()
        h = self.height()
        w = self.width()
        if x > w - self._BTN_W:
            if y < h / 2:
                self.stepUp()
                return None
            None.stepDown()
            return None
        None().mousePressEvent(event)
    __classcell__ = None
class ArrowSpinBoxI:
    '''自定义QSpinBox：右侧三角箭头 + 清晰边框'''

    def __init__(self, *args, **kwargs):
        pass
    # WARNING: Decompyle incomplete
    def paintEvent(self, event):
        super().paintEvent(event)
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        self._draw_arrows(p)
        p.end()
    def mousePressEvent(self, event):
        x = event.position().x() if hasattr(event, 'position') else event.x()
        y = event.position().y() if hasattr(event, 'position') else event.y()
        h = self.height()
        w = self.width()
        if x > w - self._BTN_W:
            if y < h / 2:
                self.stepUp()
                return None
            None.stepDown()
            return None
        None().mousePressEvent(event)
    __classcell__ = None
SCENARIOS = {
    '法兰盘密封': {
        'n': 8,
        'friction': '喷砂-钢',
        'desc': '法兰盘螺栓连接，螺栓沿圆周均布，预紧力压紧密封面防止泄漏',
        'note': '典型应用：管道法兰、压力容器端盖、阀门连接' },
    '支架连接': {
        'n': 4,
        'friction': '手工除锈-钢',
        'desc': '钢支架用螺栓固定在立柱或墙面上，主要承受剪力',
        'note': '典型应用：管道支架、设备底座、栏杆固定' },
    '盖板固定': {
        'n': 4,
        'friction': '轧制表面-钢',
        'desc': '盖板用螺栓固定在箱体或基座上，防止松动',
        'note': '典型应用：减速器端盖、检修口盖板' },
    '螺纹盲孔': {
        'n': 1,
        'friction': '涂防锈漆-钢',
        'desc': '螺钉拧入零件上的螺纹盲孔，靠螺纹啮合承载',
        'note': '典型应用：端盖螺钉、铭牌固定、小件紧固' } }
BG = '#0f0f14'
CARD = '#2a2a3a'
CARD_BORDER = '#1e1e30'
TEXT = '#e0e0e8'
TEXT_DIM = '#666680'
ACCENT = '#6c5ce7'
GREEN = '#2ecc71'
YELLOW = '#f39c12'
RED = '#e74c3c'
BLUE = '#3498db'
DARK_STYLE = []['\nQWidget#root{background:'][f'''{BG}'''][';color:'][f'''{TEXT}'''][';font-family:"Microsoft YaHei","Segoe UI",sans-serif;font-size:12px}\nQGroupBox{border:1px solid '][f'''{CARD_BORDER}'''][';border-radius:8px;margin-top:10px;padding:8px 6px 6px 6px;font-weight:bold;color:'][f'''{TEXT}'''][';background:transparent}\nQGroupBox::title{subcontrol-origin:margin;left:12px;padding:0 6px;color:'][f'''{ACCENT}'''][';font-size:12px}\nQComboBox,QSpinBox,QDoubleSpinBox{background:'][f'''{CARD}'''][';border:1px solid '][f'''{CARD_BORDER}'''][';border-radius:4px;padding:4px 8px;color:'][f'''{TEXT}'''][';min-height:22px;font-size:12px}\nQComboBox:focus,QSpinBox:focus,QDoubleSpinBox:focus{border:1px solid '][f'''{ACCENT}''']['}\nQComboBox::drop-down{border:none;width:20px}\nQSpinBox::up-button,QDoubleSpinBox::up-button{width:0px;height:0px;border:none;background:transparent;margin:0;padding:0}\nQSpinBox::down-button,QDoubleSpinBox::down-button{width:0px;height:0px;border:none;background:transparent;margin:0;padding:0}\nQSpinBox::up-arrow,QDoubleSpinBox::up-arrow{image:none;border:none;width:0;height:0}\nQSpinBox::down-arrow,QDoubleSpinBox::down-arrow{image:none;border:none;width:0;height:0}\nQPushButton#btn_calc{background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #6c5ce7,stop:1 #a855f7);color:white;border:none;border-radius:8px;padding:10px;font-size:14px;font-weight:bold;min-height:36px}\nQPushButton#btn_calc:hover{background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #7d6df7,stop:1 #b866f7)}\nQPushButton#btn_calc:pressed{background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #5b4bd5,stop:1 #9845e7)}\nQLabel{color:'][f'''{TEXT}'''][';background:transparent}\nQLabel#title{font-size:18px;font-weight:bold;color:'][f'''{ACCENT}''']['}\nQLabel#subtitle{font-size:11px;color:#9999aa}\nQFrame#result_card{background:'][f'''{CARD}'''][';border:1px solid '][f'''{CARD_BORDER}'''][';border-radius:6px}\nQFrame#result_card_pass{background:'][f'''{CARD}'''][';border:1px solid #1a3a2a;border-radius:6px}\nQFrame#result_card_warn{background:'][f'''{CARD}'''][';border:1px solid #3a3a1a;border-radius:6px}\nQFrame#result_card_fail{background:'][f'''{CARD}'''][';border:1px solid #3a1a1a;border-radius:6px}\nQLabel#verdict_pass{font-size:16px;font-weight:bold;color:'][f'''{GREEN}'''][';padding:8px;background:'][f'''{CARD}'''][';border-radius:8px}\nQLabel#verdict_warn{font-size:16px;font-weight:bold;color:'][f'''{YELLOW}'''][';padding:8px;background:'][f'''{CARD}'''][';border-radius:8px}\nQLabel#verdict_fail{font-size:16px;font-weight:bold;color:'][f'''{RED}'''][';padding:8px;background:'][f'''{CARD}'''][';border-radius:8px}\nQLabel#section_title{font-size:11px;font-weight:bold;color:#9999aa;padding:4px 0}\nQComboBox{background:'][f'''{CARD}''']['}\nQComboBox QAbstractItemView{background:'][f'''{CARD}'''][';color:'][f'''{TEXT}'''][';border:1px solid '][f'''{CARD_BORDER}'''][';selection-background-color:'][f'''{ACCENT}''']([]['\nQWidget#root{background:'][f'''{BG}'''][';color:'][f'''{TEXT}'''][';font-family:"Microsoft YaHei","Segoe UI",sans-serif;font-size:12px}\nQGroupBox{border:1px solid '][f'''{CARD_BORDER}'''][';border-radius:8px;margin-top:10px;padding:8px 6px 6px 6px;font-weight:bold;color:'][f'''{TEXT}'''][';background:transparent}\nQGroupBox::title{subcontrol-origin:margin;left:12px;padding:0 6px;color:'][f'''{ACCENT}'''][';font-size:12px}\nQComboBox,QSpinBox,QDoubleSpinBox{background:'][f'''{CARD}'''][';border:1px solid '][f'''{CARD_BORDER}'''][';border-radius:4px;padding:4px 8px;color:'][f'''{TEXT}'''][';min-height:22px;font-size:12px}\nQComboBox:focus,QSpinBox:focus,QDoubleSpinBox:focus{border:1px solid '][f'''{ACCENT}''']['}\nQComboBox::drop-down{border:none;width:20px}\nQSpinBox::up-button,QDoubleSpinBox::up-button{width:0px;height:0px;border:none;background:transparent;margin:0;padding:0}\nQSpinBox::down-button,QDoubleSpinBox::down-button{width:0px;height:0px;border:none;background:transparent;margin:0;padding:0}\nQSpinBox::up-arrow,QDoubleSpinBox::up-arrow{image:none;border:none;width:0;height:0}\nQSpinBox::down-arrow,QDoubleSpinBox::down-arrow{image:none;border:none;width:0;height:0}\nQPushButton#btn_calc{background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #6c5ce7,stop:1 #a855f7);color:white;border:none;border-radius:8px;padding:10px;font-size:14px;font-weight:bold;min-height:36px}\nQPushButton#btn_calc:hover{background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #7d6df7,stop:1 #b866f7)}\nQPushButton#btn_calc:pressed{background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #5b4bd5,stop:1 #9845e7)}\nQLabel{color:'][f'''{TEXT}'''][';background:transparent}\nQLabel#title{font-size:18px;font-weight:bold;color:'][f'''{ACCENT}''']['}\nQLabel#subtitle{font-size:11px;color:#9999aa}\nQFrame#result_card{background:'][f'''{CARD}'''][';border:1px solid '][f'''{CARD_BORDER}'''][';border-radius:6px}\nQFrame#result_card_pass{background:'][f'''{CARD}'''][';border:1px solid #1a3a2a;border-radius:6px}\nQFrame#result_card_warn{background:'][f'''{CARD}'''][';border:1px solid #3a3a1a;border-radius:6px}\nQFrame#result_card_fail{background:'][f'''{CARD}'''][';border:1px solid #3a1a1a;border-radius:6px}\nQLabel#verdict_pass{font-size:16px;font-weight:bold;color:'][f'''{GREEN}'''][';padding:8px;background:'][f'''{CARD}'''][';border-radius:8px}\nQLabel#verdict_warn{font-size:16px;font-weight:bold;color:'][f'''{YELLOW}'''][';padding:8px;background:'][f'''{CARD}'''][';border-radius:8px}\nQLabel#verdict_fail{font-size:16px;font-weight:bold;color:'][f'''{RED}'''][';padding:8px;background:'][f'''{CARD}'''][';border-radius:8px}\nQLabel#section_title{font-size:11px;font-weight:bold;color:#9999aa;padding:4px 0}\nQComboBox{background:'][f'''{CARD}''']['}\nQComboBox QAbstractItemView{background:'][f'''{CARD}'''][';color:'][f'''{TEXT}'''][';border:1px solid '][f'''{CARD_BORDER}'''][';selection-background-color:'][f'''{ACCENT}''']['}\n'])

class BoltSchematic:
    '''2D工程截面图：侧视螺栓连接，专业制图风格'''

    def __init__(self):
        super().__init__()
        self.setMinimumHeight(200)
        self.results = None
        self.n_bolts = 4
        self.plate_t = 10
        self.plate_w = 200
        self.plate_h = 200
        self.bolt_size = 'M12'
        self.bolt_yield = 1.5
        self.setStyleSheet('background:#0e0e16')
    def set_results(self, r, n_bolts, plate_t, plate_w, plate_h, bolt_size, bolt_yield):
        self.results = r
        self.n_bolts = n_bolts
        self.plate_t = plate_t
        self.plate_w = plate_w
        self.plate_h = plate_h
        self.bolt_size = bolt_size
        self.bolt_yield = bolt_yield
        self.update()
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        h = self.height()
        w = self.width()
        p.fillRect(0, 0, w, h, QColor(14, 14, 22))
        if not self.results:
            p.setPen(QColor(100, 100, 120))
            p.setFont(QFont('Microsoft YaHei', 11))
            p.drawText(QRectF(0, 0, w, h), Qt.AlignCenter, '输入参数后自动显示')
            p.end()
            return None
        b = None.get(self.bolt_size, BOLT_SIZES['M12'])
        d = b['d']
        pt = self.plate_t
        margin = 50
        draw_w = w - margin * 2
        draw_h = h - margin * 2
        cx = w / 2
        cy = h / 2
        max_dim = max(pt * 2 + 8, d * 3, 40)
        scale = min(draw_w / 120, draw_h / max_dim) * 0.8
        plate_px = max(pt * scale, 8)
        bolt_r_px = max(d * scale * 0.5, 3)
        head_r = bolt_r_px * 1.8
        head_h = plate_px * 0.4
        nut_r = bolt_r_px * 1.5
        nut_h = plate_px * 0.35
        gap = max(plate_px * 0.15, 2)
        w_ratio = min(0.5 * (self.plate_w / 200), 0.85)
        plate_half_w = draw_w * w_ratio / 2
        plate1_top = cy + gap / 2
        plate1_bot = plate1_top + plate_px
        plate2_bot = cy - gap / 2
        plate2_top = plate2_bot - plate_px
        p.setPen(QPen(QColor(80, 130, 180), 1.5))
        p.setBrush(QColor(30, 50, 70))
        p.drawRect(QRectF(cx - plate_half_w, plate1_top, plate_half_w * 2, plate_px))
        self._draw_hatch(p, cx - plate_half_w, plate1_top, plate_half_w * 2, plate_px, QColor(60, 100, 140))
        p.setPen(QPen(QColor(80, 130, 180), 1.5))
        p.setBrush(QColor(35, 55, 75))
        p.drawRect(QRectF(cx - plate_half_w, plate2_top, plate_half_w * 2, plate_px))
        self._draw_hatch(p, cx - plate_half_w, plate2_top, plate_half_w * 2, plate_px, QColor(65, 105, 145))
        hole_pen = QPen(QColor(80, 80, 100), 1, Qt.DashLine)
        p.setPen(hole_pen)
        p.drawLine(QPointF(cx - bolt_r_px - 2, plate2_top), QPointF(cx - bolt_r_px - 2, plate1_bot))
        p.drawLine(QPointF(cx + bolt_r_px + 2, plate2_top), QPointF(cx + bolt_r_px + 2, plate1_bot))
        if self.bolt_yield >= 1.5:
            pass
        elif self.bolt_yield >= 1:
            pass

        bolt_color = QColor(RED)
        p.setPen(QPen(bolt_color, 2))
        p.setBrush(QColor(bolt_color.red(), bolt_color.green(), bolt_color.blue(), 40))
        bolt_top = plate2_top - head_h - 2
        bolt_bot = plate1_bot + nut_h + 2
        p.drawRect(QRectF(cx - bolt_r_px, bolt_top, bolt_r_px * 2, bolt_bot - bolt_top))
        p.setPen(QPen(QColor(180, 190, 210), 2))
        p.setBrush(QColor(50, 60, 80))
        p.drawRect(QRectF(cx - head_r, plate2_top - head_h - 2, head_r * 2, head_h))
        p.setPen(QPen(QColor(160, 170, 190), 2))
        p.setBrush(QColor(45, 55, 75))
        p.drawRect(QRectF(cx - nut_r, plate1_bot + 2, nut_r * 2, nut_h))
        center_pen = QPen(QColor(100, 100, 130), 1, Qt.DotLine)
        p.setPen(center_pen)
        p.drawLine(QPointF(cx, plate2_top - head_h - 20), QPointF(cx, plate1_bot + nut_h + 20))
        fx = self.results.details.get('F_shear', 0)
        fy = self.results.details.get('F_axial', 0)
        arrow_y = cy
        if abs(fx) > 0:
            arr_len = min(60, (abs(fx) / 1000) * 3 + 20)
            sign = 1 if fx > 0 else -1
            x1 = cx + sign * (head_r + 8)
            x2 = cx + sign * (head_r + 8 + arr_len)
            self._draw_arrow_2d(p, x1, arrow_y, x2, arrow_y, QColor(255, 80, 80), 3)
            p.setPen(QColor(255, 80, 80))
            p.setFont(QFont('Microsoft YaHei', 9, QFont.Bold))
            fx_label_x = x2 + sign * 5
            fx_label_y = arrow_y - 12
            p.drawText(QPointF(fx_label_x, fx_label_y), f'''Fx={fx / 1000:.1f}kN''')
        if abs(fy) > 0:
            arr_len = min(50, (abs(fy) / 1000) * 2 + 15)
            sign = -1 if fy > 0 else 1
            y1 = plate2_top - head_h - 5
            y2 = y1 + sign * arr_len
            self._draw_arrow_2d(p, cx + head_r + 15, y1, cx + head_r + 15, y2, QColor(80, 160, 255), 3)
            p.setPen(QColor(80, 160, 255))
            p.setFont(QFont('Microsoft YaHei', 9, QFont.Bold))
            fy_label_x = cx + head_r + 20
            fy_label_y = y2 + sign * 12
            if abs(fx) > 0 and abs(fy_label_y - arrow_y) < 15:
                fy_label_y = arrow_y + 18 if sign < 0 else arrow_y - 25
            p.drawText(QPointF(fy_label_x, fy_label_y), f'''Fy={fy / 1000:.1f}kN''')
        dim_color = QColor(120, 120, 150)
        dim_pen = QPen(dim_color, 1)
        p.setPen(dim_pen)
        p.setFont(QFont('Consolas', 8))
        dim_x = cx - plate_half_w - 15
        self._draw_dim(p, dim_x, plate1_top, dim_x, plate1_bot, f'''{pt:.0f}''')
        self._draw_dim(p, dim_x, plate2_top, dim_x, plate2_bot, f'''{pt:.0f}''')
        gap_mm = 0.5
        self._draw_dim(p, dim_x + 30, plate2_bot, dim_x + 30, plate1_top, f'''{gap_mm:.1f}''')
        dim_y_bot = plate1_bot + 12
        self._draw_dim_h(p, cx - plate_half_w, dim_y_bot, cx + plate_half_w, dim_y_bot, f'''W={self.plate_w:.0f}''')
        dim_y = plate2_top - head_h - 15
        self._draw_dim_h(p, cx - bolt_r_px, dim_y, cx + bolt_r_px, dim_y, f'''d={d}''')
        sf = self.results.safety_factor
        mode = self.results.failure_mode
        if sf >= 1.5:
            result_color = GREEN
            result_text = f'''SF = {sf:.2f}  OK'''
        elif sf >= 1:
            result_color = YELLOW
            result_text = f'''SF = {sf:.2f}  WARNING'''
        else:
            result_color = RED
            result_text = f'''SF = {sf:.2f}  FAIL'''
        p.setPen(QColor(result_color))
        p.setFont(QFont('Consolas', 12, QFont.Bold))
        p.drawText(QRectF(10, h - 30, w - 20, 25), Qt.AlignRight | Qt.AlignVCenter, result_text)
        mode_text = {
            'friction': '摩擦力不足',
            'bolt_yield': '螺栓屈服',
            'separation': '板件分离',
            'bolt_shear': '螺栓剪切',
            'plate_bearing': '板件承压',
            'plate_tearout': '板件撕裂',
            'screw_yield': '螺钉屈服',
            'thread_stripping': '螺纹拧出' }
        p.setPen(QColor(140, 140, 160))
        p.setFont(QFont('Microsoft YaHei', 9))
        p.drawText(QRectF(10, h - 50, w - 20, 20), Qt.AlignRight | Qt.AlignVCenter, f'''控制项: {mode_text.get(mode, mode)}''')
        p.setPen(QColor(100, 100, 130))
        p.setFont(QFont('Consolas', 9))
        p.drawText(QRectF(10, 5, w - 20, 18), Qt.AlignLeft, f'''{self.bolt_size} {self.results.details.get('bolt_grade', '')} x{self.n_bolts}  |  预紧={self.results.details.get('preload', 0) / 1000:.1f}kN  |  摩擦面={self.results.details.get('_n_surfaces', 2)}''')
        p.end()
    def _draw_hatch(self, p, x, y, w, h, color):
        '''45度剖面线'''
        pen = QPen(color, 0.5)
        p.setPen(pen)
        step = 6
        for i in range(-int(h / step) - 1, int(w / step) + int(h / step) + 2):
            sx = x + i * step
            p.drawLine(QPointF(max(sx, x), y + max(0, -(sx - x))), QPointF(min(sx + h, x + w), y + min(h, (sx + h - sx - x) + (x + w - sx - h))))
            return None
    def _draw_arrow_2d(self, p, x1, y1, x2, y2, color, width):
        '''2D箭头'''
        pen = QPen(color, width)
        p.setPen(pen)
        p.drawLine(QPointF(x1, y1), QPointF(x2, y2))
        dx = x2 - x1
        dy = y2 - y1
        length = math.sqrt(dx * dx + dy * dy)
        if length < 1:
            return None
        ny = dy / length
        nx = None / length
        head_len = 8
        head_w = 4
        p.setBrush(color)
        p.setPen(Qt.NoPen)
        tip = QPointF(x2, y2)
        left = QPointF((x2 - nx * head_len) + ny * head_w, y2 - ny * head_len - nx * head_w)
        right = QPointF(x2 - nx * head_len - ny * head_w, (y2 - ny * head_len) + nx * head_w)
        p.drawPolygon(QPolygonF([
            tip,
            left,
            right]))
    def _draw_dim(self, p, x1, y1, x2, y2, text):
        '''垂直尺寸标注'''
        p.setPen(QPen(QColor(120, 120, 150), 0.8))
        p.drawLine(QPointF(x1, y1), QPointF(x1, y2))
        p.drawLine(QPointF(x1 - 3, y1 + 5), QPointF(x1, y1))
        p.drawLine(QPointF(x1 + 3, y1 + 5), QPointF(x1, y1))
        p.drawLine(QPointF(x1 - 3, y2 - 5), QPointF(x1, y2))
        p.drawLine(QPointF(x1 + 3, y2 - 5), QPointF(x1, y2))
        mid_y = (y1 + y2) / 2
        p.setFont(QFont('Consolas', 7))
        p.drawText(QPointF(x1 - 20, mid_y + 3), text + 'mm')
    def _draw_dim_h(self, p, x1, y, x2, y2, text):
        '''水平尺寸标注'''
        p.setPen(QPen(QColor(120, 120, 150), 0.8))
        p.drawLine(QPointF(x1, y), QPointF(x2, y))
        p.drawLine(QPointF(x1 + 5, y - 3), QPointF(x1, y))
        p.drawLine(QPointF(x1 + 5, y + 3), QPointF(x1, y))
        p.drawLine(QPointF(x2 - 5, y - 3), QPointF(x2, y))
        p.drawLine(QPointF(x2 - 5, y + 3), QPointF(x2, y))
        mid_x = (x1 + x2) / 2
        p.setFont(QFont('Consolas', 7))
        p.drawText(QPointF(mid_x - 15, y - 5), text)
    __classcell__ = None
class ResultCard:

    def __init__(self, label_text):
        super().__init__()
        self.setObjectName('result_card')
        self.setFixedHeight(44)
        l = QHBoxLayout(self)
        l.setContentsMargins(8, 4, 8, 4)
        l.setSpacing(6)
        self.icon = QLabel('○')
        self.icon.setFixedWidth(20)
        self.icon.setAlignment(Qt.AlignCenter)
        f = self.icon.font()
        f.setPixelSize(14)
        self.icon.setFont(f)
        l.addWidget(self.icon)
        self.label = QLabel(label_text)
        self.label.setStyleSheet('font-size:12px; color:#ccccdd; font-weight:bold')
        l.addWidget(self.label, 1)
        self.value = QLabel('--')
        self.value.setMinimumWidth(50)
        self.value.setAlignment(Qt.AlignRight | Qt.AlignCenter)
        self.value.setStyleSheet('font-size:13px; font-weight:bold; color:#b0b0c0')
        l.addWidget(self.value)
        self.bar = QLabel()
        self.bar.setFixedWidth(32)
        self.bar.setFixedHeight(5)
        l.addWidget(self.bar)
    def update_val(self, sf, target):
        if sf >= target:
            self.icon.setText('✓')
            self.icon.setStyleSheet(f'''color:{GREEN}; font-size:14px; font-weight:bold''')
            self.value.setText(f'''{sf:.1f}''')
            self.value.setStyleSheet(f'''color:{GREEN}; font-size:12px; font-weight:bold''')
            self.setObjectName('result_card_pass')
            bar_color = GREEN
        elif sf >= 1:
            self.icon.setText('!')
            self.icon.setStyleSheet(f'''color:{YELLOW}; font-size:14px; font-weight:bold''')
            self.value.setText(f'''{sf:.1f}''')
            self.value.setStyleSheet(f'''color:{YELLOW}; font-size:12px; font-weight:bold''')
            self.setObjectName('result_card_warn')
            bar_color = YELLOW
        else:
            self.icon.setText('✗')
            self.icon.setStyleSheet(f'''color:{RED}; font-size:14px; font-weight:bold''')
            self.value.setText(f'''{sf:.1f}''')
            self.value.setStyleSheet(f'''color:{RED}; font-size:12px; font-weight:bold''')
            self.setObjectName('result_card_fail')
            bar_color = RED
        self.style().unpolish(self)
        self.style().polish(self)
        pct = min(100, max(5, (sf / 3) * 100))
        self.bar.setStyleSheet(f'''background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 {bar_color} {int(pct)}%, transparent {int(pct)}%);border-radius:3px; min-height:6px''')
    def reset(self):
        self.icon.setText('○')
        self.icon.setStyleSheet('color:#444; font-size:14px')
        self.value.setText('--')
    __classcell__ = None
NUT_GRADES = {
    '4.6': [
        '4级',
        '5级'],
    '4.8': [
        '4级',
        '5级'],
    '5.6': [
        '5级'],
    '5.8': [
        '5级'],
    '6.8': [
        '6级',
        '8级'],
    '8.8': [
        '8级',
        '10级'],
    '9.8': [
        '8级',
        '9级'],
    '10.9': [
        '10级',
        '12级'],
    '12.9': [
        '12级'],
    'A2-50': [
        'A2-50'],
    'A2-70': [
        'A2-70'],
    'A2-80': [
        'A2-80'],
    'A4-70': [
        'A4-70'],
    'A4-80': [
        'A4-80'] }
NUT_STRENGTH = {
    '4级': {
        'sigma_s': 240,
        'sigma_u': 400 },
    '5级': {
        'sigma_s': 300,
        'sigma_u': 500 },
    '6级': {
        'sigma_s': 360,
        'sigma_u': 600 },
    '8级': {
        'sigma_s': 640,
        'sigma_u': 800 },
    '9级': {
        'sigma_s': 720,
        'sigma_u': 900 },
    '10级': {
        'sigma_s': 940,
        'sigma_u': 1040 },
    '12级': {
        'sigma_s': 1100,
        'sigma_u': 1220 },
    'A2-50': {
        'sigma_s': 210,
        'sigma_u': 500 },
    'A2-70': {
        'sigma_s': 450,
        'sigma_u': 700 },
    'A2-80': {
        'sigma_s': 600,
        'sigma_u': 800 },
    'A4-70': {
        'sigma_s': 450,
        'sigma_u': 700 },
    'A4-80': {
        'sigma_s': 600,
        'sigma_u': 800 } }

class MainWindow:

    def __init__(self):
        super().__init__()
        self.setWindowTitle('螺栓连接校核 V5 测试版')
        self.setMinimumSize(750, 600)
        self.resize(820, 650)
        self.setStyleSheet(DARK_STYLE)
        self._build()
        self._timer = QTimer()
        self._timer.setSingleShot(True)
        self._timer.setInterval(300)
        self._timer.timeout.connect(self._calc)
        self._connect_signals()
        self._calc()
    def _connect_signals(self):
        for w in (self.combo_scene, self.combo_size, self.combo_grade, self.combo_nut, self.combo_plate, self.combo_mu, self.combo_n_surfaces):
            w.currentTextChanged.connect(self._schedule_calc)
            for w in (self.spin_n, self.spin_fx, self.spin_fy, self.spin_m, self.spin_t, self.spin_pw, self.spin_ph, self.spin_engagement):
                w.valueChanged.connect(self._schedule_calc)
                return None
    def _schedule_calc(self, *args):
        self._timer.start()
    def _build(self):
        c = QWidget()
        c.setObjectName('root')
        self.setCentralWidget(c)
        h = QHBoxLayout(c)
        h.setContentsMargins(8, 8, 8, 8)
        h.setSpacing(8)
        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        left_scroll.setFrameShape(QFrame.NoFrame)
        left_scroll.setStyleSheet('QScrollArea{background:transparent;border:none}')
        left_scroll.setMinimumWidth(360)
        left_scroll.setMaximumWidth(400)
        left = QWidget()
        left.setObjectName('root')
        ll = QVBoxLayout(left)
        ll.setContentsMargins(4, 4, 4, 4)
        ll.setSpacing(8)
        t = QLabel('螺栓连接校核')
        t.setObjectName('title')
        ll.addWidget(t)
        s = QLabel('实时计算 · 可视化应力')
        s.setObjectName('subtitle')
        ll.addWidget(s)
        g0 = QGroupBox('连接场景')
        gl0 = QVBoxLayout(g0)
        gl0.setSpacing(4)
        gl0.setContentsMargins(8, 8, 8, 8)
        self.combo_scene = QComboBox()
        self.combo_scene.blockSignals(True)
        self.combo_scene.addItems(list(SCENARIOS.keys()))
        self.combo_scene.blockSignals(False)
        self.combo_scene.currentTextChanged.connect(self._scene)
        gl0.addWidget(self.combo_scene)
        self.lbl_desc = QLabel(SCENARIOS['法兰盘密封']['desc'])
        self.lbl_desc.setStyleSheet(f'''color:{TEXT_DIM}; font-size:10px''')
        self.lbl_desc.setWordWrap(True)
        gl0.addWidget(self.lbl_desc)
        ll.addWidget(g0)
        g1 = QGroupBox('螺栓规格')
        gl1 = QGridLayout(g1)
        gl1.setSpacing(6)
        gl1.setContentsMargins(8, 8, 8, 8)
        gl1.addWidget(QLabel('型号'), 0, 0)
        self.combo_size = QComboBox()
        self.combo_size.addItems(list(BOLT_SIZES.keys()))
        self.combo_size.setCurrentText('M12')
        gl1.addWidget(self.combo_size, 0, 1)
        gl1.addWidget(QLabel('等级'), 1, 0)
        self.combo_grade = QComboBox()
        self.combo_grade.addItems(list(BOLT_MATERIALS.keys()))
        self.combo_grade.setCurrentText('8.8')
        gl1.addWidget(self.combo_grade, 1, 1)
        gl1.addWidget(QLabel('螺母'), 2, 0)
        self.combo_nut = QComboBox()
        self.combo_nut.addItems([
            '8级 (默认)',
            '10级'])
        self.combo_nut.setToolTip('GB/T 6170 螺母等级\n默认跟随螺栓等级配套\n螺母强度 >= 螺栓强度 时由螺栓控制')
        gl1.addWidget(self.combo_nut, 2, 1)
        gl1.addWidget(QLabel('数量'), 3, 0)
        self.spin_n = ArrowSpinBoxI()
        self.spin_n.setRange(1, 100)
        self.spin_n.setValue(4)
        gl1.addWidget(self.spin_n, 3, 1)
        self.lbl_bolt_info = QLabel()
        self.lbl_bolt_info.setStyleSheet(f'''color:{TEXT_DIM}; font-size:10px; background:#0e0e1a; border-radius:4px; padding:4px''')
        self.lbl_bolt_info.setWordWrap(True)
        gl1.addWidget(self.lbl_bolt_info, 4, 0, 1, 2)
        ll.addWidget(g1)
        g2 = QGroupBox('外力')
        gl2 = QGridLayout(g2)
        gl2.setSpacing(6)
        gl2.setContentsMargins(8, 8, 8, 8)
        gl2.addWidget(QLabel('面内剪力 (N)'), 0, 0)
        self.spin_fx = ArrowSpinBox()
        self.spin_fx.setRange(-1e+06, 1e+06)
        self.spin_fx.setValue(10000)
        self.spin_fx.setSingleStep(1000)
        self.spin_fx.setToolTip('平行于板面的力，使板件沿表面滑动')
        gl2.addWidget(self.spin_fx, 0, 1)
        gl2.addWidget(QLabel('轴向力 (N)'), 1, 0)
        self.spin_fy = ArrowSpinBox()
        self.spin_fy.setRange(-1e+06, 1e+06)
        self.spin_fy.setValue(0)
        self.spin_fy.setSingleStep(1000)
        self.spin_fy.setToolTip('垂直于板面的力：正值=拉力(拉开板件)，负值=压力(压紧板件)')
        gl2.addWidget(self.spin_fy, 1, 1)
        gl2.addWidget(QLabel('弯矩 (N·m)'), 2, 0)
        self.spin_m = ArrowSpinBox()
        self.spin_m.setRange(0, 100000)
        self.spin_m.setValue(0)
        self.spin_m.setSingleStep(10)
        self.spin_m.setToolTip('绕螺栓组中心的翻转力矩')
        gl2.addWidget(self.spin_m, 2, 1)
        self.lbl_force_hint = QLabel('↔ 剪力使板滑动 │ ↑ 拉力拉开板件 │ ↓ 压力压紧板件')
        self.lbl_force_hint.setStyleSheet(f'''color:{TEXT_DIM}; font-size:9px; padding:2px 0''')
        gl2.addWidget(self.lbl_force_hint, 3, 0, 1, 2)
        ll.addWidget(g2)
        g3 = QGroupBox('板件')
        gl3 = QGridLayout(g3)
        gl3.setSpacing(6)
        gl3.setContentsMargins(8, 8, 8, 8)
        gl3.addWidget(QLabel('材料'), 0, 0)
        self.combo_plate = QComboBox()
        self.combo_plate.addItems(list(PLATE_MATERIALS.keys()))
        self.combo_plate.setCurrentText('Q235')
        gl3.addWidget(self.combo_plate, 0, 1)
        gl3.addWidget(QLabel('厚(mm)'), 1, 0)
        self.spin_t = ArrowSpinBox()
        self.spin_t.setRange(1, 200)
        self.spin_t.setValue(10)
        gl3.addWidget(self.spin_t, 1, 1)
        gl3.addWidget(QLabel('宽(mm)'), 2, 0)
        self.spin_pw = ArrowSpinBox()
        self.spin_pw.setRange(20, 2000)
        self.spin_pw.setValue(200)
        self.spin_pw.setSingleStep(10)
        gl3.addWidget(self.spin_pw, 2, 1)
        gl3.addWidget(QLabel('高(mm)'), 3, 0)
        self.spin_ph = ArrowSpinBox()
        self.spin_ph.setRange(20, 2000)
        self.spin_ph.setValue(200)
        self.spin_ph.setSingleStep(10)
        gl3.addWidget(self.spin_ph, 3, 1)
        gl3.addWidget(QLabel('表面'), 4, 0)
        self.combo_mu = QComboBox()
        self.combo_mu.setEditable(True)
        self.combo_mu.addItems(list(FRICTION_COEFFICIENTS.keys()))
        self.combo_mu.setCurrentText('喷砂-钢')
        None((lambda : self._update_mu_info()))
        self.combo_mu.setToolTip('选择预设表面，或直接输入数字μ值（如0.25）')
        gl3.addWidget(self.combo_mu, 4, 1)
        gl3.addWidget(QLabel('摩擦面'), 5, 0)
        self.combo_n_surfaces = QComboBox()
        self.combo_n_surfaces.addItems([
            '双面 (2)',
            '单面 (1)'])
        self.combo_n_surfaces.setToolTip('双面: 两块板各一个接触面(标准)\n单面: T型接头或仅一个摩擦面')
        gl3.addWidget(self.combo_n_surfaces, 5, 1)
        gl3.addWidget(QLabel('锁入深度'), 6, 0)
        self.spin_engagement = ArrowSpinBox()
        self.spin_engagement.setRange(0, 50)
        self.spin_engagement.setValue(0)
        self.spin_engagement.setSingleStep(0.5)
        self.spin_engagement.setToolTip('螺钉拧入深度(mm)\n0=自动(按材料:钢1d/铝2d/铸铁1.25d)\n>0: 手动指定')
        gl3.addWidget(self.spin_engagement, 6, 1)
        self.lbl_plate_info = QLabel()
        self.lbl_plate_info.setStyleSheet(f'''color:{TEXT_DIM}; font-size:10px; background:#0e0e1a; border-radius:4px; padding:4px''')
        self.lbl_plate_info.setWordWrap(True)
        gl3.addWidget(self.lbl_plate_info, 7, 0, 1, 2)
        self.lbl_mu_info = QLabel()
        self.lbl_mu_info.setStyleSheet(f'''color:{TEXT_DIM}; font-size:10px; background:#0e0e1a; border-radius:4px; padding:4px''')
        gl3.addWidget(self.lbl_mu_info, 8, 0, 1, 2)
        self.lbl_scene_info = QLabel()
        self.lbl_scene_info.setStyleSheet(f'''color:{TEXT_DIM}; font-size:10px; background:#0e0e1a; border-radius:4px; padding:4px''')
        gl3.addWidget(self.lbl_scene_info, 9, 0, 1, 2)
        ll.addWidget(g3)
        self.btn_calc = QPushButton('⚡  一键校核  ')
        self.btn_calc.setObjectName('btn_calc')
        self.btn_calc.clicked.connect(self._calc)
        ll.addWidget(self.btn_calc)
        ll.addStretch()
        self.lbl_version = QLabel('V5 测试版 · 仅供参考 · GB/T 3098 / GB/T 16823 / GB 50017')
        self.lbl_version.setStyleSheet('color:#555568; font-size:9px; padding:2px 0')
        ll.addWidget(self.lbl_version)
        self.lbl_scope = QLabel('适用范围: 静载螺栓/螺钉连接校核\n不包含: 疲劳分析(VDI 2230 R9)、法兰垫片密封力(F_KP)、\n螺栓拧紧力矩(需另算)、动态/冲击载荷')
        self.lbl_scope.setStyleSheet('color:#444460; font-size:9px; padding:2px 0')
        self.lbl_scope.setWordWrap(True)
        ll.addWidget(self.lbl_scope)
        left_scroll.setWidget(left)
        h.addWidget(left_scroll, 3)
        right = QWidget()
        right.setObjectName('root')
        rl = QVBoxLayout(right)
        rl.setContentsMargins(0, 0, 0, 0)
        rl.setSpacing(6)
        self.canvas = BoltSchematic()
        self.canvas.setMinimumHeight(250)
        rl.addWidget(self.canvas, 1)
        res_title = QLabel('校核结果')
        res_title.setObjectName('section_title')
        rl.addWidget(res_title)
        self.verdict = QLabel('调整参数查看结果')
        self.verdict.setObjectName('subtitle')
        self.verdict.setAlignment(Qt.AlignCenter)
        self.verdict.setStyleSheet(f'''font-size:14px; color:{TEXT_DIM}; padding:10px; background:{CARD}; border-radius:8px''')
        rl.addWidget(self.verdict)
        cards_widget = QWidget()
        cards_widget.setObjectName('root')
        cg = QGridLayout(cards_widget)
        cg.setSpacing(4)
        cg.setContentsMargins(0, 0, 0, 0)
        self.cards = { }
        labels = [
            ('friction', '摩擦力'),
            ('bolt_yield', '螺栓强度'),
            ('separation', '板件分离'),
            ('bolt_shear', '螺栓剪切'),
            ('plate_bearing', '承压'),
            ('plate_tearout', '撕裂')]
        for k, t in enumerate(labels):
            card = ResultCard(t)
            (r, c) = divmod(idx, 2)
            cg.addWidget(card, r, c)
            self.cards[k] = card
            rl.addWidget(cards_widget)
            self.lbl_max = QLabel()
            self.lbl_max.setStyleSheet(f'''font-size:13px; font-weight:bold; color:{TEXT}; background:{CARD}; border:1px solid {CARD_BORDER}; border-radius:8px; padding:8px; text-align:center''')
            self.lbl_max.setAlignment(Qt.AlignCenter)
            rl.addWidget(self.lbl_max)
            self.lbl_layout_warn = QLabel()
            self.lbl_layout_warn.setStyleSheet('color:#ff6b6b; font-size:11px; background:#2a1a1a; border:1px solid #5a2a2a; border-radius:6px; padding:4px')
            self.lbl_layout_warn.setWordWrap(True)
            self.lbl_layout_warn.setVisible(False)
            rl.addWidget(self.lbl_layout_warn)
            self.lbl_tip = QLabel()
            self.lbl_tip.setStyleSheet(f'''color:{YELLOW}; font-size:11px; background:{CARD}; border-radius:6px; padding:4px''')
            self.lbl_tip.setWordWrap(True)
            rl.addWidget(self.lbl_tip)
            self.lbl_physics = QLabel()
            self.lbl_physics.setStyleSheet(f'''color:{TEXT_DIM}; font-size:10px; background:{CARD}; border-radius:4px; padding:3px 6px''')
            self.lbl_physics.setWordWrap(True)
            rl.addWidget(self.lbl_physics)
            self.lbl_disclaimer = QLabel('⚠ 参考工具，不替代正式计算。公式:GB/T 16823.2 预紧力 | GB 50017-2017 承载力 | VDI 2230 分离')
            self.lbl_disclaimer.setStyleSheet('color:#886633; font-size:9px; background:#1a1a14; border:1px solid #332200; border-radius:4px; padding:4px 6px')
            self.lbl_disclaimer.setWordWrap(True)
            rl.addWidget(self.lbl_disclaimer)
            h.addWidget(right, 1)
            self._scene('法兰盘密封')
            return None
    def _scene(self, name):
        p = SCENARIOS[name]
        self.spin_n.setValue(p['n'])
        i = self.combo_mu.findText(p['friction'])
        if i >= 0:
            self.combo_mu.setCurrentIndex(i)
        self.lbl_desc.setText(p['desc'])
        if name == '螺纹盲孔':
            self.spin_n.setValue(1)
            self.spin_n.setEnabled(False)
        else:
            self.spin_n.setEnabled(True)
        self.lbl_scene_info.setText(p['note'])
        self._calc()
    def _update_mu_info(self):
        key = self.combo_mu.currentText()
        if key in FRICTION_COEFFICIENTS:
            v = FRICTION_COEFFICIENTS[key]
            if isinstance(v, dict):
                mu = v.get('mu', '?')
                desc = v.get('desc', '')
                note = v.get('note', '')
                self.lbl_mu_info.setText(f'''μ = {mu}  |  {desc}  |  {note}''')
                return None
            None.lbl_mu_info.setText(f'''μ = {v}''')
            return None

        try:
            mu_val = float(key)
            if mu_val <= 0 or mu_val > 1:
                self.lbl_mu_info.setText(f'''μ = {mu_val} (自定义) ⚠ 建议范围0.1~0.5''')
                return None
            None.lbl_mu_info.setText(f'''μ = {mu_val} (自定义)''')
            return None
        except ValueError:
            self.lbl_mu_info.setText('⚠ 请输入数字μ值，如0.25')
            return None
    def _update_info_labels(self):
        s = self.combo_size.currentText()
        g = self.combo_grade.currentText()
        if s in BOLT_SIZES and g in BOLT_MATERIALS:
            b = BOLT_SIZES[s]
            m = BOLT_MATERIALS[g]
            f0 = calculate_preload(m['sigma_s'], b['As'])
            t = 0.2 * f0 * b['d'] / 1000
            d = b['d']
            e_min = max(1.5 * d, 12)
            l_grip = 2 * self.spin_t.value()
            bl = calculate_bolt_length(d, l_grip)
            nut_text = self.combo_nut.currentText()
            nut_grade = nut_text.split(' (')[0] if ' (' in nut_text else nut_text
            if nut_grade in NUT_STRENGTH:
                ns = NUT_STRENGTH[nut_grade]
                nut_info = f'''螺母{nut_grade} σs={ns['sigma_s']}MPa'''
                if ns['sigma_s'] < m['sigma_s']:
                    nut_info += ' ⚠️ 螺母弱于螺栓!'
                else:
                    nut_info = f'''螺母{nut_grade}'''
            bolt_text = f'''d={d}mm P={b['P']}mm As={b['As']}mm² | F0={f0 / 1000:.1f}kN M≈{t:.1f}N·m L={bl['standard_length']:.0f}mm\n{nut_info}'''
            self.lbl_bolt_info.setText(bolt_text)
        pk = self.combo_plate.currentText()
        if pk in PLATE_MATERIALS:
            p = PLATE_MATERIALS[pk]
            ss = p.get('sigma_s', '/')
            _MAT_ENGAGEMENT_DEFAULTS = {
                'Q235': 1,
                'Q345': 1,
                'Q460': 1,
                '20#': 1,
                '45#': 1,
                '40Cr': 1,
                '20CrMnTi': 1,
                '304': 1,
                '316': 1,
                'HT200': 1.25,
                'HT250': 1.25,
                'QT450-10': 1.25,
                '5052': 2,
                '6061-T6': 2,
                '6063-T5': 2,
                '7075-T6': 2,
                'TC4': 1.5,
                **{
                    'PA66': 2.5,
                    'PEEK': 2.5 } }
            eng = _MAT_ENGAGEMENT_DEFAULTS.get(pk, 1.5)
            d = BOLT_SIZES[self.combo_size.currentText()]['d']
            eng_mm = self.spin_engagement.value()
            if eng_mm > 0:
                eng_hint = f'''锁入={eng_mm:.1f}mm({eng_mm / d:.1f}d)'''
            else:
                eng_hint = f'''锁入={eng:.1f}d({eng * d:.1f}mm,自动)'''
            self.lbl_plate_info.setText(f'''σu={p['sigma_u']}  σs={ss}  E={p['E'] / 1000:.0f}GPa  |  {eng_hint}''')
            return None
    def _calc(self):
        self._update_info_labels()

        try:
            cx = self.spin_pw.value() / 2
            cy = self.spin_ph.value() / 2
            n = self.spin_n.value()
            ph = self.spin_ph.value()
            pw = self.spin_pw.value()
            r = min(pw, ph) * 0.35
            n_surfaces = 1 if self.combo_n_surfaces.currentText().startswith('单面') else 2
            mu_key = self.combo_mu.currentText()
            custom_mu = None
            if mu_key not in FRICTION_COEFFICIENTS:

                try:
                    custom_mu = float(mu_key)

                    try:
                        pass
                    except ValueError:
                        custom_mu = 0.3

                        try:
                            pass
                        try:
                            is_screw = self.combo_scene.currentText() == '螺纹盲孔'
                            self._show(r)
                            return None
                        except Exception:
                            e = None
                            self.verdict.setText(f'''计算错误: {e}''')
                            self.verdict.setStyleSheet(f'''font-size:13px; color:{RED}; padding:10px; background:{CARD}; border-radius:8px''')
                            e = None
                            del e
                            return None
                            e = None
                            del e
    def _show(self, r):
        sf = r.safety_factor
        mode = r.failure_mode
        if sf >= 1.5:
            self.verdict.setText(f'''✓ 参考安全  SF = {sf:.2f}（参考值）''')
            self.verdict.setObjectName('verdict_pass')
        elif sf >= 1:
            self.verdict.setText(f'''⚠ 参考裕度不足  SF = {sf:.2f}（参考值）''')
            self.verdict.setObjectName('verdict_warn')
        else:
            self.verdict.setText(f'''✗ 参考不安全  SF = {sf:.2f}（参考值）''')
            self.verdict.setObjectName('verdict_fail')
        self.verdict.style().unpolish(self.verdict)
        self.verdict.style().polish(self.verdict)
        d = r.details
        sf_dict = d['safety_factors']
        mn_all = sf
        target = 1.5
        for k, v in sf_dict.items():
            if v < mn_all:
                mn_all = v
            max_load = r.max_safe_load
            bolt_yield_sf = sf_dict.get('bolt_yield', 99)
            is_screw = 'screw_yield' in sf_dict
            if is_screw:
                ts = sf_dict.get('thread_stripping', 99)
                friction_sf = ts if ts < 1e+10 else sf_dict.get('screw_yield', 99)
            else:
                friction_sf = sf_dict.get('friction', 99)
        self.cards['friction'].update_val(friction_sf)
        self.cards['bolt_yield'].update_val(sf_dict.get('bolt_yield', sf_dict.get('screw_yield', 99)), target = 1.2)
        if is_screw:
            ts = sf_dict.get('thread_stripping', 99)
            if ts < 1e+10:
                self.cards['separation'].update_val(ts)
            else:
                self.cards['separation'].update_val(sf_dict.get('plate_bearing', 99))
        else:
            self.cards['separation'].update_val(sf_dict.get('separation', 99))
        self.cards['bolt_shear'].update_val(sf_dict.get('bolt_shear', 99))
        self.cards['plate_bearing'].update_val(sf_dict.get('plate_bearing', 99))
        self.cards['plate_tearout'].update_val(sf_dict.get('plate_tearout', 99))
        if is_screw:
            self.cards['friction'].label.setText('螺纹拧出')
            self.cards['bolt_yield'].label.setText('螺钉强度')
            self.cards['separation'].label.setText('板件承压')
            self.cards['bolt_shear'].label.setText('板件撕裂')
        else:
            self.cards['friction'].label.setText('摩擦力')
            self.cards['bolt_yield'].label.setText('螺栓强度')
            self.cards['separation'].label.setText('板件分离')
            self.cards['bolt_shear'].label.setText('螺栓剪切')
        if not max_load is None:
            self.lbl_max.setText(f'''最大安全载荷: {max_load / 1000:.1f} kN（参考值）''')
        else:
            self.lbl_max.setText('')
        warnings = d.get('warnings', [])
        layout_warns = warnings()
        other_warns = warnings()
        physics_parts = []
        if d.get('F_shear', 0) != 0:
            physics_parts.append(f'''Fx={d['F_shear']:.0f}N (面内剪力)''')
        if d.get('F_axial', 0) != 0:
            axial_val = d['F_axial']
            axial_label = '轴向压力' if axial_val < 0 else '轴向拉力'
            physics_parts.append(f'''Fy={axial_val:.0f}N ({axial_label})''')
        self.canvas.set_results(r, self.spin_n.value(), self.spin_t.value(), self.spin_pw.value(), self.spin_ph.value(), self.combo_size.currentText(), sf_dict.get('bolt_yield', sf_dict.get('screw_yield', 99)))
    __classcell__ = None

