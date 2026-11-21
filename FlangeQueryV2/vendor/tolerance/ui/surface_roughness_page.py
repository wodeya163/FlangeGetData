"""表面粗糙度查询页面 - 改进版"""
import sys
import os
import math
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from compat.PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QPushButton, QGridLayout, QGroupBox,
    QScrollArea, QRadioButton, QButtonGroup, QFrame
)
from compat.PySide6.QtCore import Qt, QTimer
from compat.PySide6.QtGui import QDoubleValidator

from vendor.tolerance.data.surface_roughness import (
    RA_RZ_TABLE, MACHINING_METHODS, APPLICATION_RECOMMEND,
    MATERIAL_GROUPS, GRADE_SUMMARY
)

# 调色板(当前主题, 重启生效)
from vendor.tolerance.ui.theme import get_palette, unpack
(BG, CARD, CARD_H, BORDER, TEXT, TEXT2,
 ACCENT, GREEN, ORANGE, RED) = unpack(get_palette())
PURPLE = get_palette().get("PURPLE", "#b06cff")


def _ra_range(lo, hi):
    """区间显示：lo==hi 时显示为 Ra ≤hi μm"""
    if abs(lo - hi) < 1e-9:
        return f"Ra ≤{hi} μm"
    return f"Ra {lo}~{hi} μm"


RZ_NOTE = "Rz 为换算参考值（GB/T 1031-2009 未规定 Ra↔Rz 对应关系）"


class SurfaceRoughnessPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(10)

        # ═══ Tab模式选择 ═══
        mode_box = QGroupBox("查询模式")
        mode_lay = QHBoxLayout(mode_box)
        mode_lay.setContentsMargins(0, 0, 0, 0)
        self.mode_group = QButtonGroup()
        self.mode_ra_lookup = QRadioButton("Ra值查询")
        self.mode_ra_lookup.setToolTip("输入Ra值，自动匹配N等级、Rz值、可达加工方法")
        self.mode_method = QRadioButton("加工方法×材料")
        self.mode_method.setToolTip("选加工方法+材料，查看该材料下可达粗糙度范围")
        self.mode_application = QRadioButton("场景推荐")
        self.mode_application.setToolTip("选应用场景，获取推荐Ra值、等级、加工方法")
        self.mode_ra_lookup.setChecked(True)
        self.mode_group.addButton(self.mode_ra_lookup, 0)
        self.mode_group.addButton(self.mode_method, 1)
        self.mode_group.addButton(self.mode_application, 2)
        mode_lay.addWidget(self.mode_ra_lookup)
        mode_lay.addWidget(self.mode_method)
        mode_lay.addWidget(self.mode_application)
        self.mode_group.buttonClicked.connect(self._on_mode_changed)
        layout.addWidget(mode_box)

        # ═══ 输入区域 ═══
        input_box = QGroupBox("输入参数")
        input_lay = QVBoxLayout(input_box)
        input_lay.setContentsMargins(0, 0, 0, 0)

        grid = QGridLayout()
        grid.setSpacing(10)
        grid.setHorizontalSpacing(16)

        # ── 模式0: Ra值查询 ──
        self.ra_label = QLabel("Ra 值 (μm)")
        grid.addWidget(self.ra_label, 0, 0)
        self.ra_input = QLineEdit()
        self.ra_input.setPlaceholderText("输入Ra值，如 0.8、1.6、3.2")
        self.ra_input.setValidator(QDoubleValidator(0.001, 1000, 3))
        self.ra_input.textChanged.connect(self._on_ra_input)
        grid.addWidget(self.ra_input, 1, 0)

        # ── 模式1: 加工方法×材料 ──
        self.method_label = QLabel("加工方法")
        grid.addWidget(self.method_label, 0, 1)
        self.method_combo = QComboBox()
        # 收集不重复的方法名
        method_names = []
        seen = set()
        for name, mat, lo, hi, desc, scene in MACHINING_METHODS:
            if name not in seen:
                method_names.append(name)
                seen.add(name)
        for name in method_names:
            self.method_combo.addItem(name)
        grid.addWidget(self.method_combo, 1, 1)

        self.mat_label = QLabel("材料类型")
        grid.addWidget(self.mat_label, 0, 2)
        self.mat_combo = QComboBox()
        for mat in MATERIAL_GROUPS:
            self.mat_combo.addItem(mat)
        grid.addWidget(self.mat_combo, 1, 2)

        self.method_label.hide()
        self.method_combo.hide()
        self.mat_label.hide()
        self.mat_combo.hide()

        # ── 模式2: 场景推荐 ──
        self.app_label = QLabel("应用场景")
        grid.addWidget(self.app_label, 0, 3)
        self.app_combo = QComboBox()
        for name, lo, hi, grade, method, desc, is_mold in APPLICATION_RECOMMEND:
            prefix = "[模具] " if is_mold else ""
            self.app_combo.addItem(f"{prefix}{name}", name)
        grid.addWidget(self.app_combo, 1, 3)

        self.app_label.hide()
        self.app_combo.hide()

        # 提示
        self.hint_label = QLabel("")
        self.hint_label.setStyleSheet(f"color:{TEXT2}; font-size:11px;")
        grid.addWidget(self.hint_label, 2, 0, 1, 4)

        input_lay.addLayout(grid)
        layout.addWidget(input_box)

        # ═══ 即时查询(300ms 防抖) ═══
        self._debounce = QTimer(self)
        self._debounce.setSingleShot(True)
        self._debounce.setInterval(300)
        self._debounce.timeout.connect(self.do_query)
        self.method_combo.currentIndexChanged.connect(lambda _: self._debounce.start())
        self.mat_combo.currentIndexChanged.connect(lambda _: self._debounce.start())
        self.app_combo.currentIndexChanged.connect(lambda _: self._debounce.start())

        # ═══ 结果区域 ═══
        self.result_area = QScrollArea()
        self.result_area.setWidgetResizable(True)
        self.result_container = QWidget()
        self.result_layout = QVBoxLayout(self.result_container)
        self.result_layout.setContentsMargins(0, 0, 0, 0)
        self.result_layout.setSpacing(0)
        self.result_area.setWidget(self.result_container)
        layout.addWidget(self.result_area)

        self._on_mode_changed()

    # ─── 模式切换 ───
    def _on_mode_changed(self):
        mode = self.mode_group.checkedId()

        self.ra_label.setVisible(mode == 0)
        self.ra_input.setVisible(mode == 0)
        self.method_label.setVisible(mode == 1)
        self.method_combo.setVisible(mode == 1)
        self.mat_label.setVisible(mode == 1)
        self.mat_combo.setVisible(mode == 1)
        self.app_label.setVisible(mode == 2)
        self.app_combo.setVisible(mode == 2)

        hints = {
            0: "输入Ra值，自动匹配N等级、Rz值、可达加工方法",
            1: "选择加工方法和材料，查看该材料下该方法可达的粗糙度范围",
            2: "选择应用场景，获取推荐Ra值、等级和加工方法",
        }
        self.hint_label.setText(hints.get(mode, ""))
        self._schedule()

    def _schedule(self):
        if getattr(self, "_debounce", None):
            self._debounce.start()

    def _on_ra_input(self, text):
        """Ra输入变化 → 即时查询"""
        self._schedule()

    # ─── 查询 ───
    def do_query(self):
        mode = self.mode_group.checkedId()
        while self.result_layout.count():
            item = self.result_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        if mode == 0:
            self._query_ra_lookup()
        elif mode == 1:
            self._query_method_material()
        elif mode == 2:
            self._query_application()

    def _query_ra_lookup(self):
        """Ra值 → 匹配等级 + Rz + 加工方法"""
        text = self.ra_input.text().strip()
        if not text:
            self.hint_label.setText("请输入Ra值")
            return
        try:
            ra_val = float(text)
        except ValueError:
            self.hint_label.setText("请输入有效的数字")
            return
        # 2026-10-08 负例补齐: 非有限值/非正数不给结果, 防绕过 validator 的输入
        if not math.isfinite(ra_val) or ra_val <= 0:
            self.hint_label.setText("请输入大于0的Ra值")
            return
        # 表范围 0.012~100 μm: 超出不给"最接近"卡, 避免误导(如 3151 显示最接近 N14)
        if ra_val < 0.012 or ra_val > 100:
            self.hint_label.setText("Ra超出表格范围(0.012~100 μm)")
            return

        # 输入合法 → 清除旧错误提示, 避免与结果卡同屏矛盾
        self.hint_label.setText("输入Ra值，自动匹配N等级、Rz值、可达加工方法")

        # 找最近的等级
        best = None
        best_diff = float('inf')
        for item in RA_RZ_TABLE:
            diff = abs(item['ra'] - ra_val)
            if diff < best_diff:
                best_diff = diff
                best = item

        if not best:
            return

        is_exact = best_diff < 0.001

        # 主结果卡片
        if is_exact:
            title = f"Ra {best['ra']} μm — 精确匹配 {best['grade']}"
        else:
            title = f"Ra {ra_val} μm — 最接近 {best['grade']} (Ra {best['ra']} μm)"
        body = f"N等级: {best['grade']}  |  Rz {best['rz']} μm（换算参考）  |  常用加工: {best['name']}"
        card = self._make_result_card(title, body, ACCENT)
        self.result_layout.addWidget(card)

        # 查找所有可达此Ra的加工方法（按材料分组）
        methods_by_mat = {}
        for name, mat, lo, hi, desc, scene in MACHINING_METHODS:
            if lo - 0.001 <= ra_val <= hi + 0.001:
                if mat not in methods_by_mat:
                    methods_by_mat[mat] = []
                methods_by_mat[mat].append((name, lo, hi, desc, scene))

        if methods_by_mat:
            method_card = QGroupBox(f"可达 Ra {ra_val} μm 的加工方法")
            method_card.setStyleSheet(f"""
                QGroupBox {{
                    color: {TEXT}; font-size: 13px; font-weight: bold;
                    border: 1px solid {BORDER}; border-radius: 8px;
                    background: {CARD}; margin-top: 8px; padding-top: 16px;
                }}
                QGroupBox::title {{ subcontrol-origin: margin; left: 12px; padding: 0 4px; }}
            """)
            method_lay = QVBoxLayout(method_card)
            method_lay.setContentsMargins(12, 8, 12, 12)
            method_lay.setSpacing(4)

            for mat, methods in methods_by_mat.items():
                mat_label = QLabel(f"  [{mat}]")
                mat_label.setStyleSheet(f"color: {GREEN}; font-size: 12px; font-weight: bold; background: transparent; border: none;")
                method_lay.addWidget(mat_label)
                for name, lo, hi, desc, scene in methods:
                    line = QLabel(f"      {name}  {_ra_range(lo, hi)}  {desc}")
                    line.setStyleSheet(f"color: {TEXT}; font-size: 11px; background: transparent; border: none;")
                    method_lay.addWidget(line)

            self.result_layout.addWidget(method_card)

        # Ra/Rz/等级 对照速查表
        table_card = QGroupBox("Ra / Rz / N等级 完整对照")
        table_card.setStyleSheet(f"""
            QGroupBox {{
                color: {TEXT}; font-size: 13px; font-weight: bold;
                border: 1px solid {BORDER}; border-radius: 8px;
                background: {CARD}; margin-top: 8px; padding-top: 16px;
            }}
            QGroupBox::title {{ subcontrol-origin: margin; left: 12px; padding: 0 4px; }}
        """)
        table_lay = QVBoxLayout(table_card)
        table_lay.setContentsMargins(12, 8, 12, 12)

        for item in RA_RZ_TABLE:
            is_near = abs(item['ra'] - best['ra']) < 0.001
            prefix = "  ► " if is_near else "     "
            line = QLabel(f"{prefix}{item['grade']:4s}  Ra {item['ra']:<8.3f}  Rz {item['rz']:<8.1f}  {item['name']}")
            if is_near:
                line.setStyleSheet(f"color: {ACCENT}; font-size: 12px; font-weight: bold; font-family: Consolas; background: transparent; border: none;")
            else:
                line.setStyleSheet(f"color: {TEXT}; font-size: 12px; font-family: Consolas; background: transparent; border: none;")
            table_lay.addWidget(line)

        note = QLabel(f"※ {RZ_NOTE}")
        note.setStyleSheet(f"color: {ORANGE}; font-size: 11px; background: transparent; border: none;")
        note.setWordWrap(True)
        table_lay.addWidget(note)

        self.result_layout.addWidget(table_card)

    def _query_method_material(self):
        """加工方法×材料 → 可达粗糙度"""
        method_name = self.method_combo.currentText()
        mat_name = self.mat_combo.currentText()

        results = []
        for name, mat, lo, hi, desc, scene in MACHINING_METHODS:
            if name == method_name:
                if mat_name == "全部" or mat == mat_name or mat == "全部":
                    results.append((mat, lo, hi, desc, scene))

        if not results:
            card = self._make_result_card(
                f"{method_name} + {mat_name}",
                f"无该材料的粗糙度数据",
                RED,
            )
            self.result_layout.addWidget(card)
            return

        # 主结果
        if len(results) == 1:
            mat, lo, hi, desc, scene = results[0]
            title = f"{method_name} — {mat}"
            body = f"可达 {_ra_range(lo, hi)}\n{desc}\n常用场景: {scene}"
        else:
            title = f"{method_name} — {mat_name}"
            ranges = [f"{m}: {_ra_range(lo, hi)}" for m, lo, hi, d, s in results]
            body = f"不同材料可达范围:\n" + "\n".join(ranges)

        card = self._make_result_card(title, body, GREEN)
        self.result_layout.addWidget(card)

        # 等级范围
        all_los = [lo for _, lo, _, _, _ in results]
        all_his = [hi for _, _, hi, _, _ in results]
        min_lo = min(all_los)
        max_hi = max(all_his)

        grade_card = QGroupBox(f"可达粗糙度等级范围")
        grade_card.setStyleSheet(f"""
            QGroupBox {{
                color: {TEXT}; font-size: 13px; font-weight: bold;
                border: 1px solid {BORDER}; border-radius: 8px;
                background: {CARD}; margin-top: 8px; padding-top: 16px;
            }}
            QGroupBox::title {{ subcontrol-origin: margin; left: 12px; padding: 0 4px; }}
        """)
        grade_lay = QVBoxLayout(grade_card)
        grade_lay.setContentsMargins(12, 8, 12, 12)

        for item in RA_RZ_TABLE:
            in_range = min_lo - 0.001 <= item['ra'] <= max_hi + 0.001
            prefix = "  ★ " if in_range else "      "
            color = GREEN if in_range else TEXT2
            line = QLabel(f"{prefix}{item['grade']:4s}  Ra {item['ra']:<8.3f}  Rz {item['rz']:<8.1f}  {item['name']}")
            line.setStyleSheet(f"color: {color}; font-size: 12px; font-family: Consolas; background: transparent; border: none;")
            grade_lay.addWidget(line)

        gnote = QLabel(f"※ {RZ_NOTE}")
        gnote.setStyleSheet(f"color: {ORANGE}; font-size: 11px; background: transparent; border: none;")
        gnote.setWordWrap(True)
        grade_lay.addWidget(gnote)

        self.result_layout.addWidget(grade_card)

        # 如果是"全部"材料，按材料分组展示详细对比
        if mat_name == "全部" and len(results) > 1:
            detail_card = QGroupBox(f"{method_name} — 各材料对比")
            detail_card.setStyleSheet(f"""
                QGroupBox {{
                    color: {TEXT}; font-size: 13px; font-weight: bold;
                    border: 1px solid {BORDER}; border-radius: 8px;
                    background: {CARD}; margin-top: 8px; padding-top: 16px;
                }}
                QGroupBox::title {{ subcontrol-origin: margin; left: 12px; padding: 0 4px; }}
            """)
            detail_lay = QVBoxLayout(detail_card)
            detail_lay.setContentsMargins(12, 8, 12, 12)

            for mat, lo, hi, desc, scene in results:
                line = QLabel(f"  {mat:<12s}  {_ra_range(lo, hi)}    {desc}    {scene}")
                line.setStyleSheet(f"color: {TEXT}; font-size: 11px; font-family: Consolas; background: transparent; border: none;")
                detail_lay.addWidget(line)

            self.result_layout.addWidget(detail_card)

    def _query_application(self):
        """场景推荐 → 具体推荐值"""
        app_name = self.app_combo.currentData()
        app_info = None
        for name, lo, hi, grade, method, desc, is_mold in APPLICATION_RECOMMEND:
            if name == app_name:
                app_info = (name, lo, hi, grade, method, desc, is_mold)
                break

        if not app_info:
            return

        name, lo, hi, grade, method, desc, is_mold = app_info
        mold_tag = " [模具]" if is_mold else ""

        # 主结果
        title = f"{name}{mold_tag}"
        body = (
            f"推荐 Ra: {lo} μm (优先)  |  上限: {hi} μm\n"
            f"N等级: {grade}\n"
            f"推荐加工: {method}\n"
            f"{desc}"
        )
        card = self._make_result_card(title, body, ORANGE)
        self.result_layout.addWidget(card)

        # 推荐值详解
        detail_card = QGroupBox(f"推荐值详解")
        detail_card.setStyleSheet(f"""
            QGroupBox {{
                color: {TEXT}; font-size: 13px; font-weight: bold;
                border: 1px solid {BORDER}; border-radius: 8px;
                background: {CARD}; margin-top: 8px; padding-top: 16px;
            }}
            QGroupBox::title {{ subcontrol-origin: margin; left: 12px; padding: 0 4px; }}
        """)
        detail_lay = QVBoxLayout(detail_card)
        detail_lay.setContentsMargins(12, 8, 12, 12)

        # 找对应等级的Rz
        rz_val = None
        for item in RA_RZ_TABLE:
            if abs(item['ra'] - lo) < 0.001:
                rz_val = item['rz']
                break

        lines = [
            f"  推荐 Ra: {lo} μm  {'(Rz ' + str(rz_val) + ' μm 换算参考)' if rz_val else ''}",
            f"  上限 Ra: {hi} μm  (可接受的最粗值)",
            f"  N等级:   {grade}",
            f"  加工:   {method}",
            f"  说明:   {desc}",
        ]
        for line_text in lines:
            line = QLabel(line_text)
            line.setStyleSheet(f"color: {TEXT}; font-size: 12px; font-family: Consolas; background: transparent; border: none;")
            detail_lay.addWidget(line)

        self.result_layout.addWidget(detail_card)

        # 查找可达此Ra的加工方法（按材料分组）
        methods_by_mat = {}
        for m_name, mat, m_lo, m_hi, m_desc, m_scene in MACHINING_METHODS:
            if m_lo - 0.001 <= lo <= m_hi + 0.001:
                if mat not in methods_by_mat:
                    methods_by_mat[mat] = []
                methods_by_mat[mat].append((m_name, m_lo, m_hi, m_desc))

        if methods_by_mat:
            method_card = QGroupBox(f"可达 Ra {lo} μm 的加工方法")
            method_card.setStyleSheet(f"""
                QGroupBox {{
                    color: {TEXT}; font-size: 13px; font-weight: bold;
                    border: 1px solid {BORDER}; border-radius: 8px;
                    background: {CARD}; margin-top: 8px; padding-top: 16px;
                }}
                QGroupBox::title {{ subcontrol-origin: margin; left: 12px; padding: 0 4px; }}
            """)
            method_lay = QVBoxLayout(method_card)
            method_lay.setContentsMargins(12, 8, 12, 12)
            method_lay.setSpacing(4)

            for mat, methods in methods_by_mat.items():
                mat_label = QLabel(f"  [{mat}]")
                mat_label.setStyleSheet(f"color: {GREEN}; font-size: 12px; font-weight: bold; background: transparent; border: none;")
                method_lay.addWidget(mat_label)
                for m_name, m_lo, m_hi, m_desc in methods:
                    line = QLabel(f"      {m_name}  {_ra_range(m_lo, m_hi)}")
                    line.setStyleSheet(f"color: {TEXT}; font-size: 11px; background: transparent; border: none;")
                    method_lay.addWidget(line)

            self.result_layout.addWidget(method_card)

    def _make_result_card(self, title, body, accent_color):
        """创建结果卡片"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: {CARD};
                border: 1px solid {BORDER};
                border-left: 4px solid {accent_color};
                border-radius: 8px;
                padding: 12px;
            }}
        """)
        card_lay = QVBoxLayout(card)
        card_lay.setContentsMargins(16, 12, 16, 12)
        card_lay.setSpacing(6)

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(f"color: {accent_color}; font-size: 15px; font-weight: bold; background: transparent; border: none;")
        title_lbl.setWordWrap(True)
        card_lay.addWidget(title_lbl)

        body_lbl = QLabel(body)
        body_lbl.setStyleSheet(f"color: {TEXT2}; font-size: 12px; background: transparent; border: none;")
        body_lbl.setWordWrap(True)
        card_lay.addWidget(body_lbl)

        return card


