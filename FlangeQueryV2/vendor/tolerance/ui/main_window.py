"""公差查询工具 - 主窗口 V2.5: 场合选择+公差带图解+精简布局+手动输入偏差"""
import sys
import os
import json
import math
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from compat.PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QComboBox, QPushButton, QFrame, QGridLayout,
    QScrollArea, QGroupBox, QTabWidget, QDialog,
    QRadioButton, QButtonGroup, QMessageBox, QCheckBox
)
from compat.PySide6.QtCore import Qt, QRegularExpression, QRect, QTimer, QProcess
from compat.PySide6.QtGui import QRegularExpressionValidator, QPainter, QColor, QPen, QFont

from vendor.tolerance.data.limit_deviations import (
    get_deviations, get_fit_type, get_common_fits,
    fit_type_from_devs,
    SIZE_RANGES, get_size_range_index,
    HOLE_DEVIATIONS, SHAFT_DEVIATIONS
)

from vendor.tolerance.ui.theme import (
    THEMES, THEME_ORDER, get_palette, unpack, build_style,
    load_theme_name, save_theme_name
)

# ═══════════════════════════════════════
# 调色板(当前主题, 重启生效)
# ═══════════════════════════════════════
P = get_palette()
(BG, CARD, CARD_H, BORDER, TEXT, TEXT2,
 ACCENT, GREEN, ORANGE, RED) = unpack(P)

STYLE = build_style(P)

# ═══════════════════════════════════════
# 版本号(产品代码唯一出处: 窗口标题 + 底部水印共用)
# ═══════════════════════════════════════
VERSION_TEXT = "公差查询工具 V2.5"

STYLE = f"""
QMainWindow, QWidget {{ background-color:{BG}; color:{TEXT}; }}
QLabel {{ color:{TEXT}; background:transparent; }}
QLineEdit {{
    background:{CARD}; border:1px solid {BORDER}; border-radius:6px;
    padding:8px 12px; color:{TEXT}; font-size:16px;
    selection-background-color:{ACCENT};
}}
QLineEdit:focus {{ border:1px solid {ACCENT}; }}
QComboBox {{
    background:{CARD}; border:1px solid {BORDER}; border-radius:6px;
    padding:8px 12px; color:{TEXT}; font-size:13px; min-height:22px;
}}
QComboBox:hover {{ border:1px solid {ACCENT}; }}
QComboBox::drop-down {{ border:none; width:24px; }}
QComboBox QAbstractItemView {{
    background:{CARD}; border:1px solid {BORDER}; color:{TEXT};
    selection-background-color:{ACCENT}; padding:4px;
}}
QPushButton {{
    background:{ACCENT}; color:white; border:none; border-radius:6px;
    padding:10px; font-size:14px; font-weight:bold;
}}
QPushButton:hover {{ background:#5a7aee; }}
QPushButton:pressed {{ background:#4a6ade; }}
QPushButton.scenario-btn {{
    background:{CARD_H}; border:1px solid {BORDER}; border-radius:5px;
    padding:5px 8px; color:{TEXT}; font-size:12px; font-weight:normal;
}}
QPushButton.scenario-btn:hover {{ border:1px solid {ACCENT}; background:{CARD}; }}
QPushButton.scenario-btn:checked {{ border:1px solid {ACCENT}; background:{CARD}; color:{ACCENT}; font-weight:bold; }}
QGroupBox {{
    background:{CARD}; border:1px solid {BORDER}; border-radius:8px;
    margin-top:14px; padding:14px 10px 10px 10px;
    font-size:12px; color:{TEXT2}; font-weight:bold;
}}
QGroupBox::title {{ subcontrol-origin:margin; left:16px; padding:0 6px; }}
QScrollArea {{ border:none; background:transparent; }}
QTabWidget::pane {{
    border: 1px solid {BORDER};
    border-radius: 6px;
    background: transparent;
}}
QTabBar::tab {{
    background: {CARD};
    border: 1px solid {BORDER};
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    padding: 8px 20px;
    color: {TEXT2};
    font-size: 13px;
    margin-right: 2px;
}}
QTabBar::tab:selected {{
    background: {CARD_H};
    color: {ACCENT};
    font-weight: bold;
    border: 1px solid {ACCENT};
    border-bottom: 1px solid {CARD_H};
}}
QScrollBar:vertical {{ background:transparent; width:6px; }}
QScrollBar::handle:vertical {{ background:{BORDER}; border-radius:3px; min-height:30px; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height:0px; }}
"""

# ═══════════════════════════════════════
# 场合→配合映射表(唯一入口)
# ═══════════════════════════════════════
SCENARIO_MAP = {
    # 间隙配合(绿色)
    "滑动轴承": ("H7", "g6", "精密滑动配合,可自由旋转"),
    "齿轮传动": ("H7", "f7", "齿轮内孔与轴配合,允许微量间隙"),
    "导轨滑块": ("H7", "h6", "直线导轨定位,微小间隙可拆卸"),
    "活塞销":   ("H8", "f8", "活塞销与销孔,大间隙便于拆装"),
    # 过渡配合(橙色)
    "定位销":   ("H7", "n6", "精密定位,可传递扭矩,需轻压力装配"),
    "联轴器":   ("H7", "k6", "联轴器与轴对中,略有间隙或过盈"),
    "齿轮与轴": ("H7", "m6", "齿轮固定于轴,可传递较大力矩"),
    "键联接":   ("H7", "k6", "键槽配合,对中性好"),
    # 过盈配合(红色)
    "轴承压装": ("H7", "p6", "轴承内圈压入轴,轻过盈压入定位"),
    "衬套压入": ("H7", "r6", "衬套压入孔,中等过盈"),
    "传动销":   ("H7", "s6", "传递较大扭矩,需较大压力"),
    "热装连接": ("H7", "u6", "大过盈,需加热装配"),
}

# ═══════════════════════════════════════
# 代号分类与下拉数据自动生成
# ═══════════════════════════════════════
_TWO_LETTER = {"JS": "过渡", "CD": "间隙", "EF": "间隙", "FG": "间隙",
               "ZA": "过盈", "ZB": "过盈", "ZC": "过盈"}


def classify_code(code):
    """公差带代号 → 配合类别(基准/间隙/过渡/过盈/其他)"""
    letters = "".join(c for c in code if c.isalpha()).upper()
    if letters == "H":
        return "基准"
    if letters in _TWO_LETTER:
        return _TWO_LETTER[letters]
    if letters in set("ABCDEFG"):
        return "间隙"
    if letters in {"J", "K", "M", "N"}:
        return "过渡"
    if letters in set("PRSTUVXYZ"):
        return "过盈"
    return "其他"


def _code_groups(table):
    """从数据表自动生成 [(类别, [代号])], 只含有数据的代号, 组内按字母+等级排序"""
    groups = {}
    for code, segs in table.items():
        if any(v is not None for v in segs):
            groups.setdefault(classify_code(code), []).append(code)

    def sort_key(c):
        letters = "".join(ch for ch in c if ch.isalpha())
        digits = "".join(ch for ch in c if ch.isdigit())
        return (letters, int(digits) if digits else 0)

    return [(cat, sorted(groups[cat], key=sort_key))
            for cat in ("基准", "间隙", "过渡", "过盈", "其他") if cat in groups]


def _fill_combo(combo, groups):
    """填充下拉框, 组间插入分隔符"""
    combo.clear()
    for gi, (cat, codes) in enumerate(groups):
        if gi:
            combo.insertSeparator(combo.count())
        for c in codes:
            combo.addItem(c)


def _qc(css, alpha=255):
    """主题色 → QColor(可带透明度)"""
    c = QColor(css)
    c.setAlpha(alpha)
    return c


# ═══════════════════════════════════════
# 公差带图解 Widget
# ═══════════════════════════════════════
class ToleranceBandWidget(QWidget):
    """可视化显示孔/轴公差带与零线的位置关系"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(130)
        self.setMaximumHeight(140)
        self._hole_dev = None
        self._shaft_dev = None
        self._hole_code = ""
        self._shaft_code = ""
        self._fit_type = ""

    def set_data(self, hole_dev, shaft_dev, hole_code, shaft_code, fit_type):
        self._hole_dev = hole_dev
        self._shaft_dev = shaft_dev
        self._hole_code = hole_code
        self._shaft_code = shaft_code
        self._fit_type = fit_type
        self.update()

    def paintEvent(self, event):
        if not self._hole_dev and not self._shaft_dev:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()

        all_vals = []
        if self._hole_dev:
            all_vals.extend(self._hole_dev)
        if self._shaft_dev:
            all_vals.extend(self._shaft_dev)
        if not all_vals:
            return
        min_val = min(all_vals)
        max_val = max(all_vals)
        margin = max(abs(min_val), abs(max_val)) * 0.15 + 5
        min_val -= margin
        max_val += margin

        def y_of(val):
            bar_top = 18
            bar_bot = h - 20
            bar_h = bar_bot - bar_top
            if max_val == min_val:
                return bar_top + bar_h / 2
            return bar_top + bar_h * (max_val - val) / (max_val - min_val)

        zy = y_of(0)
        painter.setPen(QPen(QColor("#555570"), 1, Qt.PenStyle.DashLine))
        painter.drawLine(60, int(zy), w - 10, int(zy))
        painter.setPen(QPen(QColor("#8888a0"), 1))
        painter.drawText(QRect(5, int(zy) - 8, 50, 16),
                         Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, "0")

        band_w = 80
        gap = 40

        if self._hole_dev:
            es, ei = self._hole_dev
            y_top = y_of(es)
            y_bot = y_of(ei)
            x1 = w // 2 - band_w - gap // 2
            rect = QRect(int(x1), int(min(y_top, y_bot)),
                         band_w, max(int(abs(y_bot - y_top)), 2))
            from compat.PySide6.QtGui import QPainterPath, QBrush
            path = QPainterPath()
            path.addRoundedRect(float(rect.x()), float(rect.y()),
                                float(rect.width()), float(rect.height()), 4, 4)
            painter.fillPath(path, QBrush(QColor(92, 214, 138, 50)))
            painter.setPen(QPen(QColor(92, 214, 138), 2))
            painter.drawPath(path)
            painter.setPen(QColor(92, 214, 138))
            painter.setFont(QFont("Microsoft YaHei", 9, QFont.Weight.Bold))
            painter.drawText(QRect(int(x1), int(min(y_top, y_bot)) + 2,
                                   band_w, max(int(abs(y_bot - y_top)) - 4, 10)),
                             Qt.AlignmentFlag.AlignCenter, self._hole_code)
            painter.setFont(QFont("Microsoft YaHei", 8))
            painter.setPen(QColor("#aaaacc"))
            painter.drawText(QRect(int(x1) - 35, int(y_of(es)) - 8, 32, 16),
                             Qt.AlignmentFlag.AlignRight, f"+{es}")
            painter.drawText(QRect(int(x1) - 35, int(y_of(ei)) - 8, 32, 16),
                             Qt.AlignmentFlag.AlignRight, f"+{ei}" if ei > 0 else str(ei))

        if self._shaft_dev:
            es, ei = self._shaft_dev
            y_top = y_of(es)
            y_bot = y_of(ei)
            x2 = w // 2 + gap // 2
            if self._fit_type == "间隙配合":
                color = QColor(100, 160, 255, 50)
                border = QColor(100, 160, 255)
            elif self._fit_type == "过盈配合":
                color = QColor(255, 100, 100, 50)
                border = QColor(255, 100, 100)
            else:
                color = QColor(240, 160, 80, 50)
                border = QColor(240, 160, 80)
            rect = QRect(int(x2), int(min(y_top, y_bot)),
                         band_w, max(int(abs(y_bot - y_top)), 2))
            from compat.PySide6.QtGui import QPainterPath, QBrush
            path = QPainterPath()
            path.addRoundedRect(float(rect.x()), float(rect.y()),
                                float(rect.width()), float(rect.height()), 4, 4)
            painter.fillPath(path, QBrush(color))
            painter.setPen(QPen(border, 2))
            painter.drawPath(path)
            painter.setPen(border)
            painter.setFont(QFont("Microsoft YaHei", 9, QFont.Weight.Bold))
            painter.drawText(QRect(int(x2), int(min(y_top, y_bot)) + 2,
                                   band_w, max(int(abs(y_bot - y_top)) - 4, 10)),
                             Qt.AlignmentFlag.AlignCenter, self._shaft_code)
            painter.setFont(QFont("Microsoft YaHei", 8))
            painter.setPen(QColor("#aaaacc"))
            painter.drawText(QRect(int(x2) + band_w + 5, int(y_of(es)) - 8, 32, 16),
                             Qt.AlignmentFlag.AlignLeft,
                             f"+{es}" if es > 0 else str(es))
            painter.drawText(QRect(int(x2) + band_w + 5, int(y_of(ei)) - 8, 32, 16),
                             Qt.AlignmentFlag.AlignLeft,
                             f"+{ei}" if ei > 0 else str(ei))

        painter.setPen(QColor("#e0e0e8"))
        painter.setFont(QFont("Microsoft YaHei", 9))
        painter.drawText(QRect(60, 2, w - 70, 14),
                         Qt.AlignmentFlag.AlignCenter, "公差带图解")
        painter.end()


# ═══════════════════════════════════════
# 手动输入偏差校验(#140): 纯函数, 便于测试直调
#   V1 数字格式 / V2 上偏差不小于下偏差 / V3 范围 / V4 四项成对完整
#   范围依据: 数据表内偏差极值 ±33000 μm, 手动输入放宽到 ±100000 μm
# ═══════════════════════════════════════
MANUAL_DEV_LIMIT = 100000  # μm, 手动输入上界(表内极值 ±33000 的 3 倍余量)


def _parse_num(text):
    """文本 → 数字; 非数/非有限返回 None。"""
    try:
        v = float(text)
    except ValueError:
        return None
    return v if math.isfinite(v) else None


def parse_manual_pair(es_text, ei_text, side_name):
    """校验一对手动偏差, 返回 ((上偏差, 下偏差) μm 或 None, 错误提示或 None)。

    - V4 成对: 任一为空即报错(调用方保证四项均已尝试)
    - V1 格式: 需为有限数字
    - V3 范围: |偏差| <= MANUAL_DEV_LIMIT
    - V2 顺序: 上偏差不小于下偏差(与数据表 es>=ei 不变量一致)
    整数值返回 int, 与查表路径显示一致。
    """
    es_t = (es_text or "").strip()
    ei_t = (ei_text or "").strip()
    if not es_t or not ei_t:
        return None, "%s上下偏差需成对填写" % side_name
    es = _parse_num(es_t)
    ei = _parse_num(ei_t)
    if es is None or ei is None:
        return None, "偏差需为数字, 如 21 或 -7.5"
    if abs(es) > MANUAL_DEV_LIMIT or abs(ei) > MANUAL_DEV_LIMIT:
        return None, "偏差超出范围(±%d μm)" % MANUAL_DEV_LIMIT
    if es < ei:
        return None, "%s上偏差需不小于下偏差" % side_name
    if es == int(es):
        es = int(es)
    if ei == int(ei):
        ei = int(ei)
    return (es, ei), None


def parse_manual_devs(hole_es, hole_ei, shaft_es, shaft_ei):
    """四项手动偏差 → ((孔dev, 轴dev) 或 (None, None), 错误提示或 None)。"""
    hole_dev, err = parse_manual_pair(hole_es, hole_ei, "孔")
    if err:
        return None, None, err
    shaft_dev, err = parse_manual_pair(shaft_es, shaft_ei, "轴")
    if err:
        return None, None, err
    return hole_dev, shaft_dev, None


# ═══════════════════════════════════════
# Tab1: 孔轴配合(场合选择 + 自定义 + 图解)
# ═══════════════════════════════════════
class FitTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 10, 16, 10)
        layout.setSpacing(6)

        # ── 1. 查询条: 尺寸 + 公差带, 输入即查 ──
        bar = QFrame()
        bar.setObjectName("queryBar")
        bar.setStyleSheet(f"QFrame#queryBar {{ background:{CARD}; border:1px solid {BORDER}; border-radius:10px; }}")
        bar_lay = QHBoxLayout(bar)
        bar_lay.setContentsMargins(14, 10, 14, 8)
        bar_lay.setSpacing(12)

        size_col = QVBoxLayout()
        size_col.setSpacing(2)
        self.size_input = QLineEdit()
        self.size_input.setPlaceholderText("基本尺寸, 如 30 — 输入后自动查询")
        self.size_input.setValidator(QRegularExpressionValidator(QRegularExpression(r"^\d+\.?\d*$")))
        self.size_input.returnPressed.connect(self._query_now)
        self.size_input.textChanged.connect(self._on_size_changed)
        size_col.addWidget(self.size_input)
        self.size_hint = QLabel(" ")
        self.size_hint.setStyleSheet(f"color:{TEXT2}; font-size:11px;")
        size_col.addWidget(self.size_hint)
        bar_lay.addLayout(size_col, 1)

        hole_col = QVBoxLayout()
        hole_col.setSpacing(2)
        self.hole_combo = QComboBox()
        _fill_combo(self.hole_combo, _code_groups(HOLE_DEVIATIONS))
        self.hole_combo.setCurrentText("H7")
        hole_col.addWidget(self.hole_combo)
        self.hole_desc = QLabel("孔")
        self.hole_desc.setStyleSheet(f"color:{TEXT2}; font-size:11px;")
        hole_col.addWidget(self.hole_desc)
        bar_lay.addLayout(hole_col)

        sep = QLabel("/")
        sep.setStyleSheet(f"font-size:20px; color:{TEXT2}; font-weight:bold;")
        sep.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bar_lay.addWidget(sep)

        shaft_col = QVBoxLayout()
        shaft_col.setSpacing(2)
        self.shaft_combo = QComboBox()
        _fill_combo(self.shaft_combo, _code_groups(SHAFT_DEVIATIONS))
        self.shaft_combo.setCurrentText("g6")
        shaft_col.addWidget(self.shaft_combo)
        self.shaft_desc = QLabel("轴")
        self.shaft_desc.setStyleSheet(f"color:{TEXT2}; font-size:11px;")
        shaft_col.addWidget(self.shaft_desc)
        bar_lay.addLayout(shaft_col)
        layout.addWidget(bar)

        # ── 1b. 手动输入偏差(#140): 勾选展开, 默认收起不占版面 ──
        self.manual_box = QCheckBox("手动输入偏差 (μm)")
        # STYLE 字面量未覆盖 QCheckBox → 内联样式(参照 dialogs.py 免责勾选框)
        self.manual_box.setStyleSheet(
            f"color:{TEXT}; font-size:12px; padding:3px 0;")
        layout.addWidget(self.manual_box)

        self.manual_panel = QFrame()
        self.manual_panel.setObjectName("manualPanel")
        self.manual_panel.setStyleSheet(
            f"QFrame#manualPanel {{ background:{CARD}; border:1px solid {BORDER};"
            f" border-radius:10px; }}")
        mp_lay = QVBoxLayout(self.manual_panel)
        mp_lay.setContentsMargins(14, 8, 14, 8)
        mp_lay.setSpacing(2)
        mp_row = QHBoxLayout()
        mp_row.setSpacing(8)
        self.manual_inputs = {}
        for side, caps, keys in (
                ("孔", ("ES", "EI"), ("hole_es", "hole_ei")),
                ("轴", ("es", "ei"), ("shaft_es", "shaft_ei"))):
            slbl = QLabel(side)
            slbl.setStyleSheet(
                f"font-size:12px; font-weight:bold; color:{ACCENT}; padding:0 4px;")
            mp_row.addWidget(slbl)
            for cap, key in zip(caps, keys):
                clbl = QLabel(cap)
                clbl.setStyleSheet(f"color:{TEXT2}; font-size:11px;")
                mp_row.addWidget(clbl)
                le = QLineEdit()
                le.setPlaceholderText("μm")
                le.setFixedWidth(88)
                # 允许负号/小数, 中间态(如 "-"/"1.")由校验函数最终判定
                le.setValidator(QRegularExpressionValidator(
                    QRegularExpression(r"^-?\d*\.?\d*$")))
                self.manual_inputs[key] = le
                mp_row.addWidget(le)
        mp_row.addStretch()
        mp_lay.addLayout(mp_row)
        self.manual_hint = QLabel(" ")
        self.manual_hint.setStyleSheet(f"color:{TEXT2}; font-size:11px;")
        mp_lay.addWidget(self.manual_hint)
        self.manual_panel.hide()
        layout.addWidget(self.manual_panel)

        # ── 2. 常用场景: 点击自动填入并查询 ──
        scenario_box = QGroupBox("常用场景 (点击即查)")
        sc_lay = QVBoxLayout(scenario_box)
        sc_lay.setContentsMargins(0, 0, 0, 0)
        sc_lay.setSpacing(4)

        self.scenario_btns = []
        self._selected_scenario = None
        _CAT_COLOR = {"间隙": GREEN, "过渡": ORANGE, "过盈": RED}
        scenarios = list(SCENARIO_MAP.keys())
        # 3行:间隙(4) / 过渡(4) / 过盈(4)
        for row_list in [scenarios[:4], scenarios[4:8], scenarios[8:]]:
            row_lay = QHBoxLayout()
            row_lay.setSpacing(4)
            for name in row_list:
                btn = QPushButton(name)
                btn.setCheckable(True)
                btn.setFixedHeight(28)
                c = _CAT_COLOR.get(classify_code(SCENARIO_MAP[name][1]), ACCENT)
                btn.setStyleSheet(f"""
                    QPushButton {{ background:{CARD_H}; border:1px solid {BORDER};
                        border-radius:5px; padding:5px 8px; color:{TEXT};
                        font-size:12px; font-weight:normal; }}
                    QPushButton:hover {{ border:1px solid {c}; }}
                    QPushButton:checked {{ border:1px solid {c}; color:{c}; font-weight:bold; }}
                """)
                btn.clicked.connect(lambda checked, n=name: self._select_scenario(n))
                row_lay.addWidget(btn)
                self.scenario_btns.append((name, btn))
            row_lay.addStretch()
            sc_lay.addLayout(row_lay)

        self.scenario_hint = QLabel("")
        self.scenario_hint.setStyleSheet(f"color:{ACCENT}; font-size:12px; padding:2px 0;")
        sc_lay.addWidget(self.scenario_hint)
        layout.addWidget(scenario_box)

        # ── 3. 结果 ──
        self.result_area = QScrollArea()
        self.result_area.setWidgetResizable(True)
        self.result_container = QWidget()
        self.result_layout = QVBoxLayout(self.result_container)
        self.result_layout.setContentsMargins(0, 0, 0, 0)
        self.result_area.setWidget(self.result_container)
        layout.addWidget(self.result_area, 1)

        self._update_desc(self.hole_combo, self.hole_desc, is_hole=True)
        self._update_desc(self.shaft_combo, self.shaft_desc, is_hole=False)

        # 手动选择公差带 → 即时重查(信号在初始化完成后连接, 避免构建期误触发)
        self.hole_combo.currentTextChanged.connect(self._on_custom_change)
        self.shaft_combo.currentTextChanged.connect(self._on_custom_change)

        # 手动输入偏差(#140): 展开开关与四输入即时校验查询
        self.manual_box.toggled.connect(self._on_manual_toggled)
        for _le in self.manual_inputs.values():
            _le.textChanged.connect(self._on_manual_changed)

        # 公差带图解组件
        self.band_widget = ToleranceBandWidget()
        self.band_widget.hide()

        # 防抖即时查询
        self._debounce = QTimer(self)
        self._debounce.setSingleShot(True)
        self._debounce.setInterval(300)
        self._debounce.timeout.connect(self._query_now)

        # 默认示例结果(空态引导)
        self.size_input.setText("30")
        self._do_query(30, "H7", "g6")

    def _update_desc(self, combo, label, is_hole):
        code = combo.currentText()
        letter = ''.join(c for c in code if c.isalpha()).upper()
        grade = ''.join(c for c in code if c.isdigit())
        if is_hole:
            n = {"H":"基准孔","F":"间隙孔","G":"间隙孔","D":"大间隙孔",
                 "E":"间隙孔","Js":"对称过渡孔","K":"过渡孔","M":"过渡孔",
                 "N":"过渡孔","P":"过盈孔","R":"过盈孔","S":"过盈孔"}.get(letter, letter)
        else:
            n = {"H":"基准轴","F":"间隙轴","G":"间隙轴","D":"大间隙轴",
                 "E":"间隙轴","Js":"对称过渡轴","K":"过渡轴","M":"过渡轴",
                 "N":"过渡轴","P":"过盈轴","R":"过盈轴","S":"过盈轴",
                 "T":"过盈轴","U":"过盈轴"}.get(letter, letter)
        label.setText(f"{n} · IT{grade}级")

    # ── 场景选择: 填入并立即查询 ──
    def _select_scenario(self, name):
        if name not in SCENARIO_MAP:
            return
        if self.manual_box.isChecked():
            self.manual_box.setChecked(False)  # 场景选择回到代号模式(toggled 内恢复下拉)
        hole, shaft, note = SCENARIO_MAP[name]
        self._selected_scenario = name
        # 更新公差带选择
        self.hole_combo.blockSignals(True)
        self.shaft_combo.blockSignals(True)
        self.hole_combo.setCurrentText(hole)
        self.shaft_combo.setCurrentText(shaft)
        self.hole_combo.blockSignals(False)
        self.shaft_combo.blockSignals(False)
        self._update_desc(self.hole_combo, self.hole_desc, is_hole=True)
        self._update_desc(self.shaft_combo, self.shaft_desc, is_hole=False)
        # 高亮场景按钮
        for n, btn in self.scenario_btns:
            btn.setChecked(n == name)
        self.scenario_hint.setText(f"✓ {name} → {hole}/{shaft} · {note}")
        self._query_now()

    # ── 手动修改公差带 → 保留场景上下文, 即时重查 ──
    def _on_custom_change(self):
        self._update_desc(self.hole_combo, self.hole_desc, is_hole=True)
        self._update_desc(self.shaft_combo, self.shaft_desc, is_hole=False)
        if self._selected_scenario:
            old = self._selected_scenario
            self._selected_scenario = None
            for n, btn in self.scenario_btns:
                btn.setChecked(False)
            self.scenario_hint.setText(f"已在「{old}」基础上手动调整")
        self._debounce.start()

    # ── 手动输入偏差(#140): 开关面板, 手动模式与代号/场景互斥 ──
    def _on_manual_toggled(self, checked):
        self.manual_panel.setVisible(checked)
        self.hole_combo.setEnabled(not checked)
        self.shaft_combo.setEnabled(not checked)
        if checked:
            self.hole_desc.setText("手动 ES/EI")
            self.shaft_desc.setText("手动 es/ei")
            if self._selected_scenario:
                self._selected_scenario = None
                for n, btn in self.scenario_btns:
                    btn.setChecked(False)
            self.scenario_hint.setText("手动输入偏差模式")
        else:
            self._update_desc(self.hole_combo, self.hole_desc, is_hole=True)
            self._update_desc(self.shaft_combo, self.shaft_desc, is_hole=False)
            self.scenario_hint.setText("")
            self.manual_hint.setText(" ")
            self.manual_hint.setStyleSheet(f"color:{TEXT2}; font-size:11px;")
        self._debounce.start()

    def _on_manual_changed(self, _text=None):
        # 输入即查(防抖300ms), 校验与结果失效统一走 _query_now
        self._debounce.start()

    def _on_size_changed(self, text):
        # 2026-10-08 负例补齐: 所有无效分支都启动防抖, 让 _query_now 统一失效旧结果
        if not text.strip():
            self.size_hint.setText("输入尺寸后自动查询")
            self.size_hint.setStyleSheet(f"color:{TEXT2}; font-size:11px;")
            self._debounce.start()
            return
        try:
            size = float(text)
        except ValueError:
            self.size_hint.setText("请输入有效尺寸")
            self.size_hint.setStyleSheet(f"color:{RED}; font-size:11px;")
            self._debounce.start()
            return
        if not math.isfinite(size):
            self.size_hint.setText("超出范围(0~3150mm)")
            self.size_hint.setStyleSheet(f"color:{RED}; font-size:11px;")
        elif size <= 0:
            self.size_hint.setText("请输入大于0的尺寸")
            self.size_hint.setStyleSheet(f"color:{RED}; font-size:11px;")
        else:
            idx = get_size_range_index(size)
            if idx >= 0:
                low, high = SIZE_RANGES[idx]
                lbl = f"≤{high}mm" if low == 0 else f"{low}~{high}mm"
                self.size_hint.setText(f"尺寸段: {lbl}")
                self.size_hint.setStyleSheet(f"color:{ACCENT}; font-size:11px;")
            else:
                self.size_hint.setText("超出范围(0~3150mm)")
                self.size_hint.setStyleSheet(f"color:{RED}; font-size:11px;")
        self._debounce.start()

    def _show_input_placeholder(self, msg):
        """输入无效时清空过期结果并显示占位(参数变更即失效)。"""
        self._clear_results()
        lbl = QLabel(msg)
        lbl.setStyleSheet(f"color:{TEXT2}; font-size:14px; padding:30px;")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.result_layout.addWidget(lbl)

    def _query_now(self):
        text = self.size_input.text().strip()
        basic_size = None
        if text:
            try:
                v = float(text)
                if math.isfinite(v) and 0 < v <= 3150:
                    # 整数值归一: 避免标题显示 φ40.0mm(与默认卡 φ30mm 一致)
                    basic_size = int(v) if v == int(v) else v
            except ValueError:
                pass
        if basic_size is None:
            # 空/非数/非正/超范围 → 过期结果立即失效, 不残留旧卡片
            if self.manual_box.isChecked():
                # 手动模式下尺寸失效: 提示归位, 避免旧绿色生效提示与占位同屏矛盾
                self.manual_hint.setText(" ")
                self.manual_hint.setStyleSheet(f"color:{TEXT2}; font-size:11px;")
            self._show_input_placeholder("输入有效尺寸后显示结果")
            return
        if self.manual_box.isChecked():
            self._query_manual(basic_size)
            return
        hole_code = self.hole_combo.currentText()
        shaft_code = self.shaft_combo.currentText()
        if not hole_code or not shaft_code:  # 分隔符行
            return
        self._do_query(basic_size, hole_code, shaft_code)

    def _query_manual(self, basic_size):
        """手动偏差路径(#140): V1-V4 校验通过后绕过查表直接出结果卡。"""
        vals = {k: le.text() for k, le in self.manual_inputs.items()}
        if not any(v.strip() for v in vals.values()):
            self.manual_hint.setText("填写孔、轴偏差后自动查询")
            self.manual_hint.setStyleSheet(f"color:{TEXT2}; font-size:11px;")
            self._show_input_placeholder("填写孔、轴偏差后显示结果")
            return
        hole_dev, shaft_dev, err = parse_manual_devs(
            vals["hole_es"], vals["hole_ei"], vals["shaft_es"], vals["shaft_ei"])
        if err:
            # 参数不合法 → 旧结果立即失效, 提示指向修正位置
            self.manual_hint.setText(err)
            self.manual_hint.setStyleSheet(f"color:{RED}; font-size:11px;")
            self._show_input_placeholder("按提示修正偏差后显示结果")
            return
        self.manual_hint.setText("✓ 孔/轴手动偏差已生效, 配合类型按数值判定")
        self.manual_hint.setStyleSheet(f"color:{GREEN}; font-size:11px;")
        self._do_query(basic_size, "自定义", "自定义",
                       hole_dev=hole_dev, shaft_dev=shaft_dev, manual=True)

    def _do_query(self, basic_size, hole_code, shaft_code,
                  hole_dev=None, shaft_dev=None, manual=False):
        if not manual:
            hole_dev = get_deviations(hole_code, basic_size)
            shaft_dev = get_deviations(shaft_code, basic_size)
        # manual=True 时偏差由 _query_manual 校验后传入, 不查表
        self._clear_results()

        if hole_dev is None and shaft_dev is None:
            lbl = QLabel(f"{hole_code}/{shaft_code} 在 φ{basic_size}mm 所在尺寸段暂无数据")
            lbl.setStyleSheet(f"color:{RED}; font-size:14px; padding:30px;")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.result_layout.addWidget(lbl)
            return

        if manual:
            # 手动偏差无代号可依 → 按数值判定配合类型(与查表路径同一判定函数)
            fit_type = fit_type_from_devs(hole_dev, shaft_dev)
        else:
            fit_type = get_fit_type(hole_code, shaft_code, basic_size)
        fc = {"间隙配合":GREEN, "过渡配合":ORANGE,
              "过盈配合":RED}.get(fit_type, TEXT2)

        card = QFrame()
        card.setStyleSheet(f"QFrame{{ background:{CARD}; border:1px solid {BORDER}; border-radius:10px; }}")
        cl = QVBoxLayout(card)
        cl.setContentsMargins(20, 14, 20, 14)
        cl.setSpacing(4)

        # 标题行
        tr = QHBoxLayout()
        if manual:
            title = QLabel(f"φ{basic_size}mm   自定义偏差")
        else:
            title = QLabel(f"φ{basic_size}mm   {hole_code}/{shaft_code}")
        title.setStyleSheet(f"font-size:17px; font-weight:bold; color:{TEXT};")
        tr.addWidget(title)
        tr.addStretch()
        if self._selected_scenario:
            sl = QLabel(f"  {self._selected_scenario}  ")
            sl.setStyleSheet(f"font-size:12px; color:{ACCENT}; background:{CARD_H}; border-radius:4px; padding:3px 8px;")
            tr.addWidget(sl)
        tp = QLabel(f"  {fit_type}  ")
        tp.setStyleSheet(f"font-size:12px; font-weight:bold; color:{fc}; background:{CARD_H}; border-radius:4px; padding:3px 8px;")
        tr.addWidget(tp)
        cl.addLayout(tr)

        sep = QFrame(); sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"background:{BORDER}; max-height:1px; margin:4px 0;")
        cl.addWidget(sep)

        # 偏差数据
        grid = QGridLayout()
        grid.setSpacing(2)
        grid.setHorizontalSpacing(24)
        col = 0
        if hole_dev:
            self._add_col(grid, col, "孔",
                          "自定义" if manual else hole_code,
                          hole_dev[0], hole_dev[1], basic_size)
            col += 1
        if shaft_dev:
            self._add_col(grid, col, "轴",
                          "自定义" if manual else shaft_code,
                          shaft_dev[0], shaft_dev[1], basic_size)
        cl.addLayout(grid)

        # 间隙/过盈
        if hole_dev and shaft_dev:
            h_es, h_ei = hole_dev
            s_es, s_ei = shaft_dev
            max_gap = h_es - s_ei
            min_gap = h_ei - s_es

            sep2 = QFrame(); sep2.setFrameShape(QFrame.Shape.HLine)
            sep2.setStyleSheet(f"background:{BORDER}; max-height:1px; margin:4px 0;")
            cl.addWidget(sep2)

            gr = QHBoxLayout()
            gr.setSpacing(12)
            if min_gap >= 0:
                gr.addWidget(self._gap("最大间隙", f"+{max_gap} μm", GREEN))
                gr.addWidget(self._gap("最小间隙", f"+{min_gap} μm", GREEN))
            elif max_gap <= 0:
                gr.addWidget(self._gap("最大过盈", f"{-min_gap} μm", RED))
                gr.addWidget(self._gap("最小过盈", f"{-max_gap} μm", RED))
            else:
                gr.addWidget(self._gap("最大间隙", f"+{max_gap} μm", GREEN))
                gr.addWidget(self._gap("最大过盈", f"{-min_gap} μm", RED))
            gr.addStretch()
            cl.addLayout(gr)

            # 公差带图解
            sep3 = QFrame(); sep3.setFrameShape(QFrame.Shape.HLine)
            sep3.setStyleSheet(f"background:{BORDER}; max-height:1px; margin:4px 0;")
            cl.addWidget(sep3)
            self.band_widget.set_data(hole_dev, shaft_dev, hole_code, shaft_code, fit_type)
            self.band_widget.show()
            cl.addWidget(self.band_widget)

        cl.addStretch()
        self.result_layout.addWidget(card)

    def _add_col(self, grid, col, label, code, es, ei, size):
        r = 0
        hdr = QLabel(f"  {label}  ")
        hdr.setStyleSheet(f"font-size:13px; font-weight:bold; color:{ACCENT}; background:{CARD_H}; border-radius:4px; padding:3px 8px;")
        grid.addWidget(hdr, r, col*3, 1, 3); r += 1
        code_label = QLabel(code)
        code_label.setStyleSheet(f"font-size:12px; color:{TEXT2};")
        grid.addWidget(code_label, r, col*3, 1, 3); r += 1
        for name, val in [("上偏差", self._fmt(es)), ("下偏差", self._fmt(ei)),
                          ("最大极限", f"{size + es/1000:.4f} mm"), ("最小极限", f"{size + ei/1000:.4f} mm")]:
            nl = QLabel(name)
            nl.setStyleSheet(f"font-size:11px; color:{TEXT2}; padding:1px 0;")
            grid.addWidget(nl, r, col*3)
            vl = QLabel(val)
            vl.setStyleSheet(f"font-size:13px; color:{TEXT}; font-weight:bold; padding:1px 0;")
            grid.addWidget(vl, r, col*3+1, 1, 2)
            r += 1

    def _fmt(self, v):
        if v == int(v):
            return f"{int(v):+d} μm"
        return f"{v:+.1f} μm"

    def _gap(self, label, value, color):
        f = QFrame()
        f.setStyleSheet(f"QFrame{{ background:{CARD_H}; border-radius:6px; }}")
        lay = QVBoxLayout(f)
        lay.setContentsMargins(14, 8, 14, 8)
        lay.setSpacing(2)
        l = QLabel(label)
        l.setStyleSheet(f"font-size:11px; color:{TEXT2};")
        lay.addWidget(l)
        v = QLabel(value)
        v.setStyleSheet(f"font-size:17px; font-weight:bold; color:{color};")
        lay.addWidget(v)
        return f

    def _clear_results(self):
        # band_widget 是复用成员, 查询时被挂进结果卡片; 删卡前必须先拆出,
        # 否则卡片 deleteLater 连带销毁它, 下次 set_data 报 already deleted
        if self.band_widget.parent() is not None:
            self.band_widget.setParent(self)
            self.band_widget.hide()
        while self.result_layout.count():
            item = self.result_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()


# ═══════════════════════════════════════
# Tab2: 形位公差
# ═══════════════════════════════════════
from vendor.tolerance.ui.form_tolerance_page import FormTolerancePage
from vendor.tolerance.ui.surface_roughness_page import SurfaceRoughnessPage


# ═══════════════════════════════════════
# 使用说明对话框
# ═══════════════════════════════════════
class UsageGuideDialog(QDialog):
    """使用说明对话框"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("使用说明")
        self.setFixedSize(600, 520)
        self.setStyleSheet(f"""
            QDialog {{ background-color:{BG}; color:{TEXT}; }}
            QLabel {{ color:{TEXT}; background:transparent; }}
            QScrollBar:vertical {{ background:transparent; width:6px; }}
            QScrollBar::handle:vertical {{ background:{BORDER}; border-radius:3px; min-height:30px; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height:0px; }}
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(10)

        title = QLabel("📖 公差查询工具 使用说明")
        title.setStyleSheet(f"font-size:18px; font-weight:bold; color:{ACCENT}; padding:4px 0;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        content = QWidget()
        cl = QVBoxLayout(content)
        cl.setContentsMargins(0, 0, 8, 0)
        cl.setSpacing(8)

        sections = [
            ("一、即时查询", [
                "1. 在顶部查询条输入基本尺寸(mm), 结果约0.3秒后自动刷新, 无需点按钮",
                "2. 在查询条直接切换孔/轴公差带, 结果同样即时更新",
                "3. 回车可立即查询",
            ]),
            ("二、常用场景", [
                "1. 点击场景按钮(如「滑动轴承」「定位销」)自动填入推荐配合并立即查询",
                "2. 按配合类型着色: 绿=间隙, 橙=过渡, 红=过盈",
                "3. 手动修改公差带会保留场景提示「已在XX基础上手动调整」",
            ]),
            ("三、配合代号说明", [
                "• H7/g6 → 孔H7 + 轴g6,精密滑动配合(间隙)",
                "• H7/k6 → 孔H7 + 轴k6,精密定位过渡",
                "• H7/p6 → 孔H7 + 轴p6,小过盈配合",
                "• 字母部分(H/g/k/p...)= 公差带位置(决定配合类型)",
                "• 数字部分(6/7/8...)= IT公差等级(数字越小精度越高)",
            ]),
            ("四、结果解读", [
                "• 绿色 = 间隙配合(孔总大于轴,可自由装配)",
                "• 橙色 = 过渡配合(可能间隙可能过盈,需选配)",
                "• 红色 = 过盈配合(轴总大于孔,需压力/热装装配)",
                "• 公差带图解:绿色条=孔,红色条=轴,虚线=零线",
            ]),
            ("五、支持的范围", [
                "• 基本尺寸:0~3150 mm",
                "• 公差带下拉与数据库同步, 只列出有数据的代号, 按基准/间隙/过渡/过盈分组",
                "• 某代号在某尺寸段无数据时会提示「暂无数据」(数据持续补充中)",
            ]),
            ("六、其他Tab", [
                "• 形位公差 Tab:查GB/T 1184-1996规定的形位公差值(输入即查)",
                "• 表面粗糙度 Tab:查GB/T 1031粗糙度Ra对照(输入即查)",
            ]),
            ("七、截图查公差", [
                "• 点击顶部「📷 截图查公差」按钮, 或按 Ctrl+Shift+D, 拖动框选图纸上的公差标注",
                "• 自动识别如 φ50H7/g6 的标注, 给出上下偏差与配合类型",
                "• 识别结果仅供参考, 关键参数请核对标准原文",
                "• 热键无响应时, 点击顶部「📷 截图查公差」按钮即可",
            ]),
            ("八、手动输入偏差", [
                "• 勾选查询条下方「手动输入偏差」展开孔 ES/EI、轴 es/ei 四个输入框(单位 μm)",
                "• 四项填写完整且合法后自动查询, 结果卡代号显示「自定义」, 配合类型按偏差数值判定",
                "• 校验规则: 需为数字, 上偏差不小于下偏差, 范围 ±100000 μm",
                "• 取消勾选即回到公差带代号查询; 点击场景按钮也会回到代号模式",
            ]),
        ]

        for heading, items in sections:
            hl = QLabel(heading)
            hl.setStyleSheet(f"font-size:14px; font-weight:bold; color:{ACCENT}; padding:6px 0 2px 0;")
            cl.addWidget(hl)
            for item in items:
                il = QLabel(f"  {item}")
                il.setStyleSheet(f"font-size:12px; color:{TEXT}; padding:1px 0 1px 12px; line-height:1.4;")
                il.setWordWrap(True)
                cl.addWidget(il)

        cl.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll)

        close_btn = QPushButton("关闭")
        close_btn.setFixedWidth(100)
        close_btn.clicked.connect(self.accept)
        bl = QHBoxLayout()
        bl.addStretch()
        bl.addWidget(close_btn)
        layout.addLayout(bl)


# ═══════════════════════════════════════
# 设置对话框(主题切换)
# ═══════════════════════════════════════
class SettingsDialog(QDialog):
    """设置: 主题选择, 保存后重启生效(支持立即重启)"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置")
        self.setMinimumWidth(440)
        self.setStyleSheet(f"QDialog {{ background:{BG}; }}")
        self._restarted = False
        current = load_theme_name()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(8)

        title = QLabel("🎨 界面主题")
        title.setStyleSheet(f"font-size:15px; font-weight:bold; color:{TEXT};")
        layout.addWidget(title)

        self._group = QButtonGroup(self)
        self._rows = []
        for idx, name in enumerate(THEME_ORDER):
            p = THEMES[name]
            row = QFrame()
            row.setCursor(Qt.CursorShape.PointingHandCursor)
            rl = QHBoxLayout(row)
            rl.setContentsMargins(12, 8, 12, 8)
            rl.setSpacing(8)
            rb = QRadioButton(name)
            rb.setCursor(Qt.CursorShape.PointingHandCursor)
            self._group.addButton(rb, idx)
            rl.addWidget(rb)
            rl.addStretch()
            # 色板预览
            for key in ("BG", "CARD", "ACCENT", "GREEN", "ORANGE", "RED"):
                chip = QFrame()
                chip.setFixedSize(20, 20)
                chip.setStyleSheet(f"QFrame {{ background:{p[key]}; border:1px solid {BORDER}; border-radius:4px; }}")
                rl.addWidget(chip)
            layout.addWidget(row)
            self._rows.append((row, rb, name))
            # 选中态变化 → 整行高亮
            rb.toggled.connect(lambda on, r=row, b=rb: self._style_row(r, b, on))
            self._style_row(row, rb, name == current)

        self._group.buttonClicked.connect(self._on_pick)

        frozen_hint = "（打包版保存后需手动重新打开工具）" if getattr(sys, 'frozen', False) else "（开发版会立即重启）"
        self.hint = QLabel(f"点击主题立即保存; 切换主题需重新打开工具生效 {frozen_hint}")
        self.hint.setStyleSheet(f"color:{TEXT2}; font-size:11px;")
        layout.addWidget(self.hint)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self.restart_btn = QPushButton(
            "保存主题" if getattr(sys, 'frozen', False) else "保存并立即重启"
        )
        self.restart_btn.setFixedHeight(34)
        self.restart_btn.clicked.connect(self._save_and_restart)
        btn_row.addWidget(self.restart_btn)
        close_btn = QPushButton("关闭")
        close_btn.setFixedHeight(34)
        close_btn.setStyleSheet(f"""
            QPushButton {{ background:{CARD_H}; color:{TEXT2}; border:1px solid {BORDER}; }}
            QPushButton:hover {{ border:1px solid {ACCENT}; color:{ACCENT}; }}
        """)
        close_btn.clicked.connect(self.reject)
        btn_row.addWidget(close_btn)
        layout.addLayout(btn_row)

    def _style_row(self, row, rb, on):
        """主题行选中态: ACCENT 边框高亮 + 文字加粗变色"""
        if on:
            row.setStyleSheet(f"QFrame {{ background:{CARD_H}; border:2px solid {ACCENT}; border-radius:8px; }}"
                              f"QFrame QRadioButton {{ color:{ACCENT}; font-size:13px; font-weight:bold; background:transparent; }}")
            rb.setChecked(True)
        else:
            row.setStyleSheet(f"QFrame {{ background:{CARD}; border:1px solid {BORDER}; border-radius:8px; }}"
                              f"QFrame QRadioButton {{ color:{TEXT}; font-size:13px; background:transparent; }}")

    def _current_name(self):
        return THEME_ORDER[self._group.checkedId()]

    def _on_pick(self, btn):
        save_theme_name(self._current_name())
        self.hint.setText(f"✓ 已保存「{self._current_name()}」, 重启后生效")

    def _save_and_restart(self):
        save_theme_name(self._current_name())
        if getattr(sys, 'frozen', False):
            # PyInstaller onefile 自重启会报 PYI-19860: 提示用户手动重启, 不再调用 startDetached
            QMessageBox.information(
                self, "主题已保存",
                f"主题已保存为「{self._current_name()}」。\n"
                "打包版请手动重新打开工具以生效。"
            )
            QApplication.instance().quit()
        else:
            main_py = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'main.py')
            QProcess.startDetached(sys.executable, [main_py])
            QApplication.instance().quit()


# ═══════════════════════════════════════
# 主窗口
# ═══════════════════════════════════════
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(VERSION_TEXT)
        self.resize(880, 800)
        self.setMinimumSize(700, 620)
        self._ocr_ctrl = None  # OCR截图查公差控制器, 由 run() 注入

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(12, 12, 12, 12)

        # 顶部标题栏:标题 + 帮助按钮
        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(0, 0, 0, 0)
        title_lbl = QLabel("公差查询工具")
        title_lbl.setStyleSheet(f"font-size:16px; font-weight:bold; color:{ACCENT}; background:transparent;")
        top_bar.addWidget(title_lbl)
        top_bar.addStretch()
        ocr_btn = QPushButton("📷 截图查公差")
        ocr_btn.setFixedHeight(30)
        ocr_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        ocr_btn.setStyleSheet(f"""
            QPushButton {{
                background:{CARD}; color:{TEXT}; border:1px solid {BORDER};
                border-radius:15px; font-size:13px; font-weight:bold; padding:0 14px;
            }}
            QPushButton:hover {{ border:1px solid {ACCENT}; color:{ACCENT}; background:{CARD_H}; }}
        """)
        ocr_btn.setToolTip("框选屏幕上的公差标注自动识别查询 (Ctrl+Shift+D)")
        ocr_btn.clicked.connect(self._start_ocr_capture)
        self._ocr_btn = ocr_btn
        top_bar.addWidget(ocr_btn)
        gear_btn = QPushButton("⚙ 设置")
        gear_btn.setFixedHeight(30)
        gear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        gear_btn.setStyleSheet(f"""
            QPushButton {{
                background:{CARD}; color:{TEXT}; border:1px solid {BORDER};
                border-radius:15px; font-size:13px; font-weight:bold; padding:0 14px;
            }}
            QPushButton:hover {{ border:1px solid {ACCENT}; color:{ACCENT}; background:{CARD_H}; }}
        """)
        gear_btn.setToolTip("设置(主题等)")
        gear_btn.clicked.connect(self._show_settings)
        top_bar.addWidget(gear_btn)
        help_btn = QPushButton("? 帮助")
        help_btn.setFixedHeight(30)
        help_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        help_btn.setStyleSheet(f"""
            QPushButton {{
                background:{CARD}; color:{TEXT}; border:1px solid {BORDER};
                border-radius:15px; font-size:13px; font-weight:bold; padding:0 14px;
            }}
            QPushButton:hover {{ border:1px solid {ACCENT}; color:{ACCENT}; background:{CARD_H}; }}
        """)
        help_btn.setToolTip("使用说明")
        help_btn.clicked.connect(self._show_help)
        top_bar.addWidget(help_btn)
        layout.addLayout(top_bar)

        tabs = QTabWidget()
        tabs.addTab(FitTab(), "孔轴配合")
        tabs.addTab(FormTolerancePage(), "形位公差")
        tabs.addTab(SurfaceRoughnessPage(), "表面粗糙度")
        layout.addWidget(tabs)

        disclaimer = QLabel("⚠ 实际加工可能因设备、材料、工艺不同而有偏差,仅供参考,关键参数请查阅GB/T 1800标准原文")
        disclaimer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        disclaimer.setStyleSheet(f"color:{TEXT2}; font-size:11px; padding:4px 0; background:transparent;")
        # 版本号水印(免责声明行右端: 文字仅~560px, 挤压后单行仍放得下;
        # 放数据来源行会把其挤成两行 -> 10px 小字 OCR 漏识, 2026-10-09 真机实证)
        version_lbl = QLabel(VERSION_TEXT)
        version_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        version_lbl.setStyleSheet(f"color:{TEXT2}; font-size:10px; padding:4px 0; background:transparent;")
        disc_row = QHBoxLayout()
        disc_row.setContentsMargins(16, 0, 16, 0)
        disc_row.addWidget(disclaimer)
        disc_row.addSpacing(8)
        disc_row.addWidget(version_lbl)
        layout.addLayout(disc_row)

        data_source = QLabel("数据来源: 成大先《机械设计手册》表2-2-2/表2-2-3 | GB/T 1800 系列(现行 GB/T 1800.1-2020、GB/T 1800.2-2020)")
        data_source.setWordWrap(True)
        data_source.setAlignment(Qt.AlignmentFlag.AlignCenter)
        data_source.setStyleSheet(f"color:{TEXT2}; font-size:10px; padding:2px 0; background:transparent;")
        layout.addWidget(data_source)

    def _show_settings(self):
        dlg = SettingsDialog(self)
        dlg.exec()

    def _show_help(self):
        dlg = UsageGuideDialog(self)
        dlg.exec()

    def set_ocr_controller(self, ctrl):
        """注入 OCR 截图查公差控制器 (由 run() 调用)。ctrl=None 时按钮禁用并说明原因。"""
        self._ocr_ctrl = ctrl
        if ctrl is None:
            self._ocr_btn.setEnabled(False)
            self._ocr_btn.setToolTip("OCR 组件未就绪 (依赖缺失)")

    def _start_ocr_capture(self):
        if self._ocr_ctrl is None:
            QMessageBox.information(self, "截图查公差", "OCR 组件未就绪, 请重新安装工具。")
            return
        self._ocr_ctrl.start_capture()


def run():
    from vendor.tolerance.ui.dialogs import (WelcomeDialog, LockDialog, DisclaimerDialog,
                            is_first_run, is_unlocked, mark_welcome_done)

    app = QApplication(sys.argv)
    app.setStyleSheet(STYLE)

    if is_first_run():
        welcome = WelcomeDialog()
        if welcome.exec() != QDialog.DialogCode.Accepted:
            return  # 红线12: 三件套任一非 Accepted 即退出
        mark_welcome_done()  # 红线12: 欢迎页通过后立即落盘 first_run=False

    # 先加载本地config
    cfg_path = os.path.join(os.path.expanduser('~'), '.ToleranceTool', 'config.json')
    cfg = {}
    if os.path.exists(cfg_path):
        try:
            with open(cfg_path, 'r', encoding='utf-8') as f:
                cfg = json.load(f)
        except Exception:
            pass

    # 密码锁（检查本地config，而非全局）
    local_unlocked = cfg.get("unlocked", False)
    if not local_unlocked:
        lock = LockDialog()
        if lock.exec() != QDialog.DialogCode.Accepted:
            return
        # LockDialog._check_password 已写入本地config，刷新cfg
        if os.path.exists(cfg_path):
            try:
                with open(cfg_path, 'r', encoding='utf-8') as f:
                    cfg = json.load(f)
            except Exception:
                pass

    # 免责声明(首次必须同意)
    if not cfg.get('disclaimer_accepted', False):
        disc = DisclaimerDialog()
        if disc.exec() != QDialog.DialogCode.Accepted:
            return
        cfg['disclaimer_accepted'] = True
        with open(cfg_path, 'w', encoding='utf-8') as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)

    w = MainWindow()
    # OCR 截图查公差: 全局热键 Ctrl+Shift+D + 界面按钮 (依赖缺失不禁用主功能)
    try:
        from ocr_query import OCRQueryController
        ocr_ctrl = OCRQueryController()
        ocr_ctrl.start()
        w.set_ocr_controller(ocr_ctrl)
        w._ocr_ctrl_ref = ocr_ctrl  # 持有引用防 GC
    except Exception:
        w.set_ocr_controller(None)
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    run()
