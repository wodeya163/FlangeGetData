"""形位公差查询页面"""
import sys
import os
import math
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from compat.PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QPushButton, QFrame, QGridLayout, QGroupBox,
    QScrollArea, QRadioButton, QButtonGroup
)
from compat.PySide6.QtCore import Qt, QRegularExpression, QTimer, QTimer
from compat.PySide6.QtGui import QRegularExpressionValidator

from vendor.tolerance.data.form_tolerance import (
    FORM_TOLERANCE_TYPES, GRADE_DESCRIPTIONS,
    get_straightness_flatness, get_roundness_cylindricity,
    get_parallelism, get_perpendicularity, get_runout_symmetry,
    recommend_by_machining, MACHINING_RECOMMEND
)

# 调色板(当前主题, 重启生效)
from vendor.tolerance.ui.theme import get_palette, unpack
(BG, CARD, CARD_H, BORDER, TEXT, TEXT2,
 ACCENT, GREEN, ORANGE, RED) = unpack(get_palette())


class FormTolerancePage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(10)

        # ═══ 模式选择 ═══
        mode_box = QGroupBox("查询模式")
        mode_lay = QHBoxLayout(mode_box)
        mode_lay.setContentsMargins(0, 0, 0, 0)
        self.mode_group = QButtonGroup()
        self.mode_query = QRadioButton("查公差值（输入尺寸+等级→给出公差值）")
        self.mode_recommend = QRadioButton("查等级建议（输入尺寸+加工方法→推荐等级）")
        self.mode_query.setChecked(True)
        self.mode_group.addButton(self.mode_query, 0)
        self.mode_group.addButton(self.mode_recommend, 1)
        mode_lay.addWidget(self.mode_query)
        mode_lay.addWidget(self.mode_recommend)
        self.mode_group.buttonClicked.connect(self._on_mode_changed)
        layout.addWidget(mode_box)

        # ═══ 输入区域 ═══
        input_box = QGroupBox("输入参数")
        input_lay = QVBoxLayout(input_box)
        input_lay.setContentsMargins(0, 0, 0, 0)

        # 用QGridLayout统一排列标签和控件
        grid = QGridLayout()
        grid.setSpacing(10)
        grid.setHorizontalSpacing(16)

        # 第0行: 标签
        grid.addWidget(QLabel("基本尺寸 (mm)"), 0, 0)
        grid.addWidget(QLabel("公差类型"), 0, 1)
        self.grade_label = QLabel("公差等级")
        grid.addWidget(self.grade_label, 0, 2)
        self.machining_label = QLabel("加工方法")
        grid.addWidget(self.machining_label, 0, 3)
        self.machining_label.hide()

        # 第1行: 输入控件
        self.size_input = QLineEdit()
        self.size_input.setPlaceholderText("例如 50")
        self.size_input.setStyleSheet(f"QLineEdit {{ font-size: 12px; }} QLineEdit::placeholder {{ font-size: 11px; color: {TEXT2}; }}")
        self.size_input.setValidator(QRegularExpressionValidator(QRegularExpression(r"^\d+\.?\d*$")))
        self.size_input.returnPressed.connect(self.do_query)
        self.size_input.textChanged.connect(self._on_size_changed)
        grid.addWidget(self.size_input, 1, 0)

        self.type_combo = QComboBox()
        for category, items in FORM_TOLERANCE_TYPES.items():
            for name, symbol, desc, grades in items:
                self.type_combo.addItem(f"{symbol} {name} — {desc}", name)
        self.type_combo.currentIndexChanged.connect(self._on_type_changed)
        grid.addWidget(self.type_combo, 1, 1)

        self.grade_combo = QComboBox()
        for i in range(13):
            self.grade_combo.addItem(f"{i}级 — {GRADE_DESCRIPTIONS.get(i, '')}", i)
        self.grade_combo.setCurrentIndex(7)
        grid.addWidget(self.grade_combo, 1, 2)

        self.machining_combo = QComboBox()
        for method, info in MACHINING_RECOMMEND.items():
            self.machining_combo.addItem(f"{method} — {info['说明']}", method)
        grid.addWidget(self.machining_combo, 1, 3)
        self.machining_combo.hide()

        # 第2行: 提示
        self.size_hint = QLabel("")
        self.size_hint.setStyleSheet(f"color:{TEXT2}; font-size:11px;")
        grid.addWidget(self.size_hint, 2, 0)
        self.type_hint = QLabel("")
        self.type_hint.setStyleSheet(f"color:{TEXT2}; font-size:11px;")
        grid.addWidget(self.type_hint, 2, 1)

        input_lay.addLayout(grid)
        layout.addWidget(input_box)

        # 初始化提示
        self._on_type_changed()

        # ═══ 即时查询(300ms 防抖) ═══
        self._debounce = QTimer(self)
        self._debounce.setSingleShot(True)
        self._debounce.setInterval(300)
        self._debounce.timeout.connect(self.do_query)
        self.grade_combo.currentIndexChanged.connect(lambda _: self._debounce.start())
        self.machining_combo.currentIndexChanged.connect(lambda _: self._debounce.start())

        # ═══ 结果 ═══
        self.result_area = QScrollArea()
        self.result_area.setWidgetResizable(True)
        self.result_container = QWidget()
        self.result_layout = QVBoxLayout(self.result_container)
        self.result_layout.setContentsMargins(0, 0, 0, 0)
        self.result_area.setWidget(self.result_container)
        layout.addWidget(self.result_area, 1)

        self.hint_label = QLabel("输入参数后自动查询")
        self.hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hint_label.setStyleSheet(f"color:{TEXT2}; font-size:14px; padding:30px;")
        self.result_layout.addWidget(self.hint_label)

        self._update_type_hint()

    def _schedule(self):
        if getattr(self, "_debounce", None):
            self._debounce.start()

    def _on_mode_changed(self):
        is_recommend = self.mode_recommend.isChecked()
        self.grade_combo.setVisible(not is_recommend)
        self.grade_label.setVisible(not is_recommend)
        self.machining_combo.setVisible(is_recommend)
        self.machining_label.setVisible(is_recommend)
        self._schedule()

    # 公差类型 → 尺寸输入提示
    SIZE_HINTS = {
        '直线度': '请输入被测线的长度',
        '平面度': '请输入平面较长边的长度',
        '圆度': '请输入被测圆的直径',
        '圆柱度': '请输入被测圆柱的直径',
        '平行度': '请输入被测要素的长度',
        '垂直度': '请输入被测要素的长度',
        '倾斜度': '请输入被测要素的长度',
        '同轴度': '请输入被测圆柱的直径',
        '对称度': '请输入被测要素的宽度或长度',
        '圆跳动': '请输入被测圆柱的直径',
        '全跳动': '请输入被测圆柱的直径',
    }

    def _on_type_changed(self):
        self._update_type_hint()
        self._schedule()

    def _update_type_hint(self):
        name = self.type_combo.currentData()
        for category, items in FORM_TOLERANCE_TYPES.items():
            for n, symbol, desc, grades in items:
                if n == name:
                    self.type_hint.setText(f"等级范围: {grades}")
                    break
        hint = self.SIZE_HINTS.get(name, '')
        if hint:
            self.size_input.setPlaceholderText(hint)
        else:
            self.size_input.setPlaceholderText('请输入尺寸')

    def _on_size_changed(self, text):
        # 2026-10-08 负例补齐: 空/非数/非正/非有限值都给提示, 且统一触发防抖失效旧结果
        if not text.strip():
            self.size_hint.setText("输入尺寸后自动查询")
            self.size_hint.setStyleSheet(f"color:{TEXT2}; font-size:11px;")
            self._schedule()
            return
        try:
            size = float(text)
        except ValueError:
            self.size_hint.setText("请输入有效尺寸")
            self.size_hint.setStyleSheet(f"color:{RED}; font-size:11px;")
            self._schedule()
            return
        if not math.isfinite(size):
            self.size_hint.setText("请输入有效尺寸")
            self.size_hint.setStyleSheet(f"color:{RED}; font-size:11px;")
        elif size <= 0:
            self.size_hint.setText("请输入正数")
            self.size_hint.setStyleSheet(f"color:{RED}; font-size:11px;")
        elif size > 10000:
            # 形位表整体上界 10000mm, 超出不给 ✓ (类型细分上界由结果区红字陈述)
            self.size_hint.setText("超出范围(0~10000mm)")
            self.size_hint.setStyleSheet(f"color:{RED}; font-size:11px;")
        else:
            self.size_hint.setText("✓")
            self.size_hint.setStyleSheet(f"color:{GREEN}; font-size:11px;")
        self._schedule()

    def _show_input_placeholder(self, msg):
        """输入无效时清空过期结果并显示占位(参数变更即失效)。"""
        self._clear_results()
        lbl = QLabel(msg)
        lbl.setStyleSheet(f"color:{TEXT2}; font-size:14px; padding:30px;")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.result_layout.addWidget(lbl)

    def do_query(self):
        text = self.size_input.text().strip()
        size = None
        if text:
            try:
                v = float(text)
                if math.isfinite(v) and 0 < v <= 10000:
                    size = v
            except ValueError:
                pass
        if size is None:
            # 空/非数/非正/inf/超上界 → 过期结果立即失效, 不残留旧卡片
            self._show_input_placeholder("输入有效尺寸后显示结果")
            return

        type_name = self.type_combo.currentData()
        is_recommend = self.mode_recommend.isChecked()

        self._clear_results()

        if is_recommend:
            self._do_recommend(size, type_name)
        else:
            self._do_query_value(size, type_name)

    def _do_query_value(self, size, type_name):
        """查公差值模式"""
        grade = self.grade_combo.currentData()

        # 根据类型调用对应函数
        result = None
        for category, items in FORM_TOLERANCE_TYPES.items():
            for name, symbol, desc, grades in items:
                if name == type_name:
                    if name in ("直线度", "平面度"):
                        result = get_straightness_flatness(size, grade)
                    elif name in ("圆度", "圆柱度"):
                        result = get_roundness_cylindricity(size, grade)
                    elif name == "平行度":
                        result = get_parallelism(size, grade)
                    elif name == "垂直度":
                        result = get_perpendicularity(size, grade)
                    elif name in ("同轴度", "对称度", "圆跳动", "全跳动"):
                        result = get_runout_symmetry(size, grade)
                    break

        if result is None:
            lbl = QLabel(f"未找到 {type_name} 在 {size}mm / {grade}级 的数据")
            lbl.setStyleSheet(f"color:{RED}; font-size:14px; padding:30px;")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.result_layout.addWidget(lbl)
            return

        tolerance_um, size_label = result
        tolerance_mm = tolerance_um / 1000

        # 找到符号和描述
        symbol = ""
        desc = ""
        for category, items in FORM_TOLERANCE_TYPES.items():
            for name, sym, d, g in items:
                if name == type_name:
                    symbol, desc = sym, d
                    break

        # 结果卡片
        card = QFrame()
        card.setStyleSheet(f"QFrame{{ background:{CARD}; border:1px solid {BORDER}; border-radius:10px; }}")
        cl = QVBoxLayout(card)
        cl.setContentsMargins(20, 16, 20, 16)
        cl.setSpacing(6)

        # 标题
        title_row = QHBoxLayout()
        t = QLabel(f"{symbol} {type_name}")
        t.setStyleSheet(f"font-size:20px; font-weight:bold; color:{TEXT};")
        title_row.addWidget(t)
        title_row.addStretch()
        g = QLabel(f"  {grade}级  ")
        g.setStyleSheet(f"font-size:13px; font-weight:bold; color:{ACCENT}; background:{CARD_H}; border-radius:4px; padding:3px 8px;")
        title_row.addWidget(g)
        cl.addLayout(title_row)

        # 说明
        desc_label = QLabel(desc)
        desc_label.setStyleSheet(f"color:{TEXT2}; font-size:12px;")
        cl.addWidget(desc_label)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"background:{BORDER}; max-height:1px; margin:4px 0;")
        cl.addWidget(sep)

        # 参数
        params = QGridLayout()
        params.setSpacing(6)
        params.setHorizontalSpacing(30)

        for r, (name, val) in enumerate([
            ("基本尺寸", f"{size} mm"),
            ("尺寸段", size_label),
            ("公差等级", f"IT{grade}级"),
            ("等级说明", GRADE_DESCRIPTIONS.get(grade, "")),
            ("公差值", f"{tolerance_um} μm = {tolerance_mm:.4f} mm"),
        ]):
            nl = QLabel(name)
            nl.setStyleSheet(f"font-size:12px; color:{TEXT2};")
            params.addWidget(nl, r, 0)
            vl = QLabel(val)
            vl.setStyleSheet(f"font-size:14px; color:{TEXT}; font-weight:bold;")
            params.addWidget(vl, r, 1)

        cl.addLayout(params)

        # 应用场景提示
        cl.addSpacing(6)
        scene = QLabel(self._get_scene(type_name, grade))
        scene.setStyleSheet(f"color:{ORANGE}; font-size:12px; background:{CARD_H}; border-radius:4px; padding:6px 10px;")
        scene.setWordWrap(True)
        cl.addWidget(scene)

        cl.addStretch()
        self.result_layout.addWidget(card)

    def _do_recommend(self, size, type_name):
        """查等级建议模式"""
        method = self.machining_combo.currentData()
        rec = recommend_by_machining(method)

        if rec is None:
            lbl = QLabel("未找到该加工方法的推荐等级")
            lbl.setStyleSheet(f"color:{RED}; font-size:14px; padding:30px;")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.result_layout.addWidget(lbl)
            return

        grade_range = rec["等级"]
        method_desc = rec["说明"]

        # 解析等级范围
        parts = grade_range.split("~")
        low, high = int(parts[0]), int(parts[1])

        # 找到符号
        symbol = ""
        desc = ""
        for category, items in FORM_TOLERANCE_TYPES.items():
            for name, sym, d, g in items:
                if name == type_name:
                    symbol, desc = sym, d
                    break

        # 结果卡片
        card = QFrame()
        card.setStyleSheet(f"QFrame{{ background:{CARD}; border:1px solid {BORDER}; border-radius:10px; }}")
        cl = QVBoxLayout(card)
        cl.setContentsMargins(20, 16, 20, 16)
        cl.setSpacing(6)

        # 标题
        t = QLabel(f"{symbol} {type_name} — 加工方法推荐")
        t.setStyleSheet(f"font-size:18px; font-weight:bold; color:{TEXT};")
        cl.addWidget(t)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"background:{BORDER}; max-height:1px; margin:4px 0;")
        cl.addWidget(sep)

        # 推荐信息
        info = QGridLayout()
        info.setSpacing(6)
        info.setHorizontalSpacing(30)
        for r, (name, val) in enumerate([
            ("加工方法", method),
            ("方法说明", method_desc),
            ("推荐等级", f"IT{parts[0]}~IT{parts[1]}"),
            ("基本尺寸", f"{size} mm"),
        ]):
            nl = QLabel(name)
            nl.setStyleSheet(f"font-size:12px; color:{TEXT2};")
            info.addWidget(nl, r, 0)
            vl = QLabel(val)
            vl.setStyleSheet(f"font-size:14px; color:{TEXT}; font-weight:bold;")
            info.addWidget(vl, r, 1)
        cl.addLayout(info)

        # 各等级公差值
        cl.addSpacing(6)
        cl.addWidget(QLabel("各等级对应公差值:"))
        val_grid = QGridLayout()
        val_grid.setSpacing(4)

        for i, grade in enumerate(range(low, high + 1)):
            result = None
            if type_name in ("直线度", "平面度"):
                result = get_straightness_flatness(size, grade)
            elif type_name in ("圆度", "圆柱度"):
                result = get_roundness_cylindricity(size, grade)
            elif type_name == "平行度":
                result = get_parallelism(size, grade)
            elif type_name == "垂直度":
                result = get_perpendicularity(size, grade)
            elif type_name in ("同轴度", "对称度", "圆跳动", "全跳动"):
                result = get_runout_symmetry(size, grade)

            if result:
                um, _ = result
                mm = um / 1000
                lbl = QLabel(f"{grade}级")
                lbl.setStyleSheet(f"color:{TEXT2}; font-size:12px;")
                val_grid.addWidget(lbl, i, 0)
                vlbl = QLabel(f"{um} μm ({mm:.4f} mm)")
                vlbl.setStyleSheet(f"color:{TEXT}; font-size:13px; font-weight:bold;")
                val_grid.addWidget(vlbl, i, 1)

        cl.addLayout(val_grid)

        if high > 12:
            gnote = QLabel(f"※ 形位公差数值表仅覆盖1~12级，IT13~IT{high} 不列出数值")
            gnote.setStyleSheet(f"color:{ORANGE}; font-size:11px;")
            gnote.setWordWrap(True)
            cl.addWidget(gnote)

        # 应用场景
        cl.addSpacing(6)
        scene = QLabel(self._get_scene(type_name, (low + high) // 2))
        scene.setStyleSheet(f"color:{ORANGE}; font-size:12px; background:{CARD_H}; border-radius:4px; padding:6px 10px;")
        scene.setWordWrap(True)
        cl.addWidget(scene)

        cl.addStretch()
        self.result_layout.addWidget(card)

    def _get_scene(self, type_name, grade):
        """根据类型和等级返回应用场景"""
        scenes = {
            "直线度": {
                (1,3): "精密量具、光学仪器",
                (4,6): "机床导轨、精密平面",
                (7,9): "一般零件平面",
                (10,12): "粗糙表面",
            },
            "平面度": {
                (1,3): "精密平板、量具",
                (4,6): "机床工作台、精密配合面",
                (7,9): "一般配合面",
                (10,12): "非配合面",
            },
            "圆度": {
                (0,3): "精密轴承、量具",
                (4,6): "机床主轴、精密配合轴",
                (7,9): "一般配合轴/孔",
                (10,12): "粗糙配合面",
            },
            "圆柱度": {
                (0,3): "精密主轴、液压件",
                (4,6): "机床导柱导套",
                (7,9): "一般配合面",
                (10,12): "粗糙配合面",
            },
            "平行度": {
                (1,3): "精密机床基准面",
                (4,6): "机床导轨面、精密配合面",
                (7,9): "一般配合面",
                (10,12): "非配合面",
            },
            "垂直度": {
                (1,3): "精密机床基准面",
                (4,6): "机床立柱、精密装配面",
                (7,9): "一般配合面",
                (10,12): "非配合面",
            },
            "倾斜度": {
                (1,3): "精密角度面",
                (4,6): "斜面配合",
                (7,9): "一般斜面",
                (10,12): "粗糙斜面",
            },
            "同轴度": {
                (1,3): "精密主轴、齿轮配合",
                (4,6): "联轴器、轴承座",
                (7,9): "一般轴孔配合",
                (10,12): "粗糙配合",
            },
            "对称度": {
                (1,3): "精密键槽、花键",
                (4,6): "一般键槽配合",
                (7,9): "普通配合面",
                (10,12): "非配合面",
            },
            "圆跳动": {
                (1,3): "精密主轴、齿轮",
                (4,6): "机床主轴、高精度配合",
                (7,9): "一般轴类零件",
                (10,12): "粗糙旋转面",
            },
            "全跳动": {
                (1,3): "精密主轴",
                (4,6): "机床主轴、高精度旋转件",
                (7,9): "一般旋转件",
                (10,12): "粗糙旋转面",
            },
        }

        type_scenes = scenes.get(type_name, {})
        for (low, high), scene in type_scenes.items():
            if low <= grade <= high:
                return f"💡 {grade}级{type_name}常用于: {scene}"
        return ""

    def _clear_results(self):
        while self.result_layout.count():
            item = self.result_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
