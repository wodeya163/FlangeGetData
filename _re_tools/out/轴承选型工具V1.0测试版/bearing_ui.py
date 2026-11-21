# Reconstructed from bytecode by split_decompile.py
# bearing_ui.pyc

'''BearingTool 界面层（版本号见 bearing_data.VERSION，不在此硬编码）'''
import os
import sys
from PySide6.QtCore import Qt, QUrl, QPointF, QRectF
from PySide6.QtGui import QColor, QBrush, QDesktopServices, QIcon, QPixmap, QPainter, QPen, QPolygonF
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QDoubleSpinBox, QSpinBox, QFrame, QGridLayout, QScrollArea, QTableWidget, QTableWidgetItem, QHeaderView, QTabWidget, QFileDialog, QLineEdit, QButtonGroup, QDialog, QInputDialog, QListWidget, QListWidgetItem, QSplitter
import bearing_data as BD
import bearing_3d as B3
import dialogs
(BG, CARD, TEXT, TEXT_G) = ('#f4f6f8', '#ffffff', '#1f2d3d', '#7f8c9b')
(ACCENT, ACCENT_H) = ('#2f6fed', '#e8590c')
(OK_C, WARN_C) = ('#2f9e44', '#e8590c')
COMBO = 'QComboBox{background:#fff;border:1px solid #d5dce4;border-radius:6px;padding:4px 8px;}QComboBox:hover{border-color:%s;}' % ACCENT
BTN = 'QPushButton{background:%s;color:#fff;border:none;border-radius:6px;padding:6px 14px;font-weight:bold;}QPushButton:hover{background:#2258c4;}' % ACCENT
CARD_CSS = f'''QFrame{{background:{CARD};border:1px solid #e3e8ee;border-radius:10px;}}'''

def card():
    f = QFrame()
    f.setStyleSheet(CARD_CSS)
    return (f, QVBoxLayout(f))
def _paint_glyph(kind, size):
    '''程序自绘图标：轴承 logo + 各页签功能图形（零外部素材）'''
    cos = cos
    sin = sin
    radians = radians
    import math
    pm = QPixmap(size, size)
    pm.fill(Qt.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing)
    s = size / 64
    if kind == 'bearing':
        p.setPen(QPen(QColor(ACCENT), 6 * s))
        p.setBrush(Qt.NoBrush)
        p.drawEllipse(QRectF(6 * s, 6 * s, 52 * s, 52 * s))
        p.setPen(QPen(QColor(ACCENT), 4 * s))
        p.drawEllipse(QRectF(24 * s, 24 * s, 16 * s, 16 * s))
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(ACCENT))
        for i in range(8):
            a = radians(i * 45)
            p.drawEllipse(QPointF(32 * s + 19 * s * cos(a), 32 * s + 19 * s * sin(a)), 4.5 * s, 4.5 * s)
    if kind == 'guide':
        p.setPen(QPen(QColor(ACCENT), 5 * s))
        p.drawEllipse(QRectF(12 * s, 12 * s, 40 * s, 40 * s))
        for x1, y1, x2, y2 in ((32, 3, 32, 18), (32, 46, 32, 61), (3, 32, 18, 32), (46, 32, 61, 32)):
            p.drawLine(QPointF(x1 * s, y1 * s), QPointF(x2 * s, y2 * s))
    if kind == 'check':
        p.setPen(QPen(QColor(ACCENT), 5 * s))
        p.drawEllipse(QRectF(9 * s, 9 * s, 46 * s, 46 * s))
        p.drawLine(QPointF(32 * s, 32 * s), QPointF(32 * s, 17 * s))
        p.drawLine(QPointF(32 * s, 32 * s), QPointF(43 * s, 39 * s))
    elif kind == 'reverse':
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(ACCENT))
        p.drawPolygon(QPolygonF([
            QPointF(9 * s, 12 * s),
            QPointF(55 * s, 12 * s),
            QPointF(38 * s, 34 * s),
            QPointF(38 * s, 55 * s),
            QPointF(26 * s, 48 * s),
            QPointF(26 * s, 34 * s)]))
    elif kind == 'cube':
        p.setPen(QPen(QColor(ACCENT), 4 * s))
        p.setBrush(Qt.NoBrush)
        p.drawPolygon(QPolygonF([
            QPointF(32 * s, 6 * s),
            QPointF(56 * s, 19 * s),
            QPointF(56 * s, 45 * s),
            QPointF(32 * s, 58 * s),
            QPointF(8 * s, 45 * s),
            QPointF(8 * s, 19 * s)]))
        p.drawLine(QPointF(8 * s, 19 * s), QPointF(32 * s, 32 * s))
        p.drawLine(QPointF(56 * s, 19 * s), QPointF(32 * s, 32 * s))
        p.drawLine(QPointF(32 * s, 32 * s), QPointF(32 * s, 58 * s))
    elif kind == 'about':
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(ACCENT))
        p.drawEllipse(QPointF(32 * s, 15 * s), 5.5 * s, 5.5 * s)
        p.drawRoundedRect(QRectF(26.5 * s, 26 * s, 11 * s, 28 * s), 3 * s, 3 * s)
    p.end()
    return pm
def glyph_icon(kind, size):
    return QIcon(_paint_glyph(kind, size))
class GuideTab:
    '''场合速选：问答 → 类型推荐'''

    def __init__(self):
        super().__init__()
        root = QVBoxLayout(self)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(10)
        (f, self.form) = card()
        title = QLabel('回答几个工况问题，推荐适合的轴承类型')
        title.setStyleSheet(f'''font-size:15px;font-weight:bold;color:{TEXT};border:none;''')
        self.form.addWidget(title)
        grid = QGridLayout()
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(8)

        def combo(label, items):
            w = QComboBox()
            w.setStyleSheet(COMBO)
            w.addItems(items)
            lab = QLabel(label)
            lab.setStyleSheet(f'''color:{TEXT};''')
            return (lab, w)
        (self.cb_load_lab, self.cb_load) = combo('载荷大小', [
            '中等',
            '轻载',
            '重载',
            '有冲击/振动'])
        (self.cb_dir_lab, self.cb_dir) = combo('载荷方向', [
            '以径向为主+少量轴向',
            '纯径向',
            '以轴向为主',
            '纯轴向'])
        (self.cb_speed_lab, self.cb_speed) = combo('转速', [
            '中等',
            '高转速',
            '低速'])
        (self.cb_align_lab, self.cb_align) = combo('轴线可能不对中/需要调心?', [
            '不需要',
            '需要'])
        (self.cb_space_lab, self.cb_space) = combo('安装空间', [
            '无限制',
            '径向空间受限',
            '轴向空间受限'])
        (self.cb_impact_lab, self.cb_impact) = combo('工况补充', [
            '正常',
            '温度偏高/粉尘/潮湿等恶劣环境'])
        for lab, w in enumerate([
            (self.cb_load_lab, self.cb_load),
            (self.cb_dir_lab, self.cb_dir),
            (self.cb_speed_lab, self.cb_speed),
            (self.cb_align_lab, self.cb_align),
            (self.cb_space_lab, self.cb_space),
            (self.cb_impact_lab, self.cb_impact)]):
            grid.addWidget(lab, (i // 2) * 2, (i % 2) * 2)
            grid.addWidget(w, (i // 2) * 2 + 1, (i % 2) * 2)
            self.form.addLayout(grid)
            btn = QPushButton('推荐轴承类型')
            btn.setStyleSheet(BTN)
            btn.clicked.connect(self.on_guide)
            self.form.addWidget(btn)
            root.addWidget(f)
            self.result_host = QWidget()
            self.result_lay = QVBoxLayout(self.result_host)
            self.result_lay.setContentsMargins(0, 0, 0, 0)
            self.result_lay.setSpacing(8)
            root.addWidget(self.result_host)
            root.addStretch()
            return None
    def on_guide(self):
        if self.result_lay.count():
            it = self.result_lay.takeAt(0)
            if it.widget():
                it.widget().deleteLater()
            if not self.result_lay.count():
                load = {
                    '轻载': 'light',
                    '重载': 'heavy',
                    '有冲击/振动': 'impact' }.get(self.cb_load.currentText(), 'medium')
                direction = {
                    '纯径向': 'pure_radial',
                    '以轴向为主': 'axial_main',
                    '纯轴向': 'pure_axial' }.get(self.cb_dir.currentText(), 'radial_main')
                speed = {
                    '高转速': 'high',
                    '低速': 'low' }.get(self.cb_speed.currentText(), 'medium')
                align = self.cb_align.currentText() == '需要'
                space = {
                    '径向空间受限': 'radial_limited',
                    '轴向空间受限': 'axial_limited' }.get(self.cb_space.currentText(), 'free')
                impact = self.cb_impact.currentText() != '正常'
                for t, s in enumerate(BD.type_guide(load, direction, speed, align, space, impact), 1):
                    (f2, lay) = card()
                    head = QLabel(f'''第{rank}名  {t['name']}  ({t['gb']})''')
                    head.setStyleSheet(f'''font-size:14px;font-weight:bold;color:{ACCENT if rank == 1 else TEXT};border:none;''')
                    lay.addWidget(head)
                    info = QLabel('适合：' + '；'.join(t['scene'][:2]))
                    info.setWordWrap(True)
                    info.setStyleSheet(f'''color:{TEXT};border:none;''')
                    lay.addWidget(info)
                    avoid = QLabel('避免：' + '；'.join(t['avoid'][:2]))
                    avoid.setWordWrap(True)
                    avoid.setStyleSheet(f'''color:{WARN_C};border:none;''')
                    lay.addWidget(avoid)
                    note = QLabel(t['note'])
                    note.setWordWrap(True)
                    note.setStyleSheet(f'''color:{TEXT_G};font-size:11px;border:none;''')
                    lay.addWidget(note)
                    self.result_lay.addWidget(f2)
                    return None
    __classcell__ = None
class CheckTab:
    '''正向校核：型号 + 载荷转速 → 当量载荷/寿命'''
    W = 880

    def __init__(self):
        super().__init__()
        root = QVBoxLayout(self)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(10)
        (f, lay) = card()
        f.setFixedWidth(self.W)
        lay.addWidget(QLabel('<b>输入工况，核算所选深沟球轴承的寿命</b>'))
        g = QGridLayout()
        g.setHorizontalSpacing(16)
        self.cb_code = QComboBox()
        self.cb_code.setStyleSheet(COMBO)
        self.cb_code.addItems(list(BD.DEEP_GROOVE.keys()))
        self.cb_lub = QComboBox()
        self.cb_lub.setStyleSheet(COMBO)
        self.cb_lub.addItems([
            '脂润滑',
            '油润滑'])
        self.cb_seal = QComboBox()
        self.cb_seal.setStyleSheet(COMBO)
        (lambda .0: [ s[0] for s in .0 ])(BD.SEAL_TYPES())
        self.cb_seal.setToolTip('2RS 胶封的极限转速约为开式的 6 成（多源核验）')
        self.sp_fr = QDoubleSpinBox()
        self.sp_fr.setRange(0, 999)
        self.sp_fr.setDecimals(2)
        self.sp_fr.setSuffix(' kN')
        self.sp_fa = QDoubleSpinBox()
        self.sp_fa.setRange(0, 999)
        self.sp_fa.setDecimals(2)
        self.sp_fa.setSuffix(' kN')
        self.sp_n = QSpinBox()
        self.sp_n.setRange(1, 99999)
        self.sp_n.setValue(1450)
        self.sp_n.setSuffix(' rpm')
        for w in (self.sp_fr, self.sp_fa, self.sp_n):
            w.setStyleSheet(COMBO)
            for lab, w in enumerate([
                ('型号', self.cb_code),
                ('径向载荷 Fr', self.sp_fr),
                ('轴向载荷 Fa', self.sp_fa),
                ('转速', self.sp_n),
                ('润滑', self.cb_lub),
                ('密封形式', self.cb_seal)]):
                g.addWidget(QLabel(lab), (i // 3) * 2, i % 3)
                g.addWidget(w, (i // 3) * 2 + 1, i % 3)
                lay.addLayout(g)
                btn = QPushButton('核算寿命')
                btn.setStyleSheet(BTN)
                btn.clicked.connect(self.on_check)
                lay.addWidget(btn)
                self.out = QLabel('')
                self.out.setWordWrap(True)
                self.out.setTextFormat(Qt.RichText)
                self.out.setStyleSheet('border:none;')
                lay.addWidget(self.out)
                row = QHBoxLayout()
                row.addStretch()
                row.addWidget(f)
                row.addStretch()
                root.addLayout(row)
                (f2, lay2) = card()
                f2.setFixedWidth(self.W)
                head = QLabel('型号参数速览')
                head.setStyleSheet(f'''font-weight:bold;color:{TEXT};border:none;''')
                lay2.addWidget(head)
                self.lbl_spec = QLabel('')
                self.lbl_spec.setWordWrap(True)
                self.lbl_spec.setTextFormat(Qt.RichText)
                self.lbl_spec.setStyleSheet('border:none;')
                lay2.addWidget(self.lbl_spec)
                row2 = QHBoxLayout()
                row2.addStretch()
                row2.addWidget(f2)
                row2.addStretch()
                root.addLayout(row2)
                self.cb_code.currentTextChanged.connect(self.update_spec)
                self.cb_lub.currentTextChanged.connect(self.update_spec)
                self.update_spec()
                root.addStretch()
                return None
    def update_spec(self):
        code = self.cb_code.currentText()
        spec = BD.DEEP_GROOVE.get(code)
        if not spec:
            self.lbl_spec.setText('无此型号数据')
            return None
        (d, D, B, cr, c0, ng, no) = None[:7]
        self.lbl_spec.setText(f'''<b>{code}</b>　内径 {d} × 外径 {D} × 宽 {B} mm　｜　Cr {cr} kN · C0r {c0} kN　｜　极限转速：脂 {ng:,} / 油 {no:,} rpm<br><span style=\'color:{TEXT_G};font-size:11px;\'>不同厂家同型号数值略有差异，以所选厂家样本原文为准</span>''')
    def on_check(self):
        pass

    __classcell__ = None
class ReverseTab:
    '''反向选型：工况+目标寿命 → 候选型号'''

    def __init__(self):
        super().__init__()
        root = QVBoxLayout(self)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(10)
        (f, lay) = card()
        f.setMaximumWidth(880)
        lay.addWidget(QLabel('<b>输入工况与目标寿命，推荐满足要求的深沟球型号（外径从小到大）</b>'))
        g = QGridLayout()
        g.setHorizontalSpacing(16)
        self.sp_fr = QDoubleSpinBox()
        self.sp_fr.setRange(0, 999)
        self.sp_fr.setSuffix(' kN')
        self.sp_fr.setValue(3)
        self.sp_fa = QDoubleSpinBox()
        self.sp_fa.setRange(0, 999)
        self.sp_fa.setSuffix(' kN')
        self.sp_fa.setValue(1)
        self.sp_n = QSpinBox()
        self.sp_n.setRange(1, 99999)
        self.sp_n.setValue(1450)
        self.sp_n.setSuffix(' rpm')
        self.sp_h = QSpinBox()
        self.sp_h.setRange(100, 200000)
        self.sp_h.setValue(20000)
        self.sp_h.setSuffix(' h')
        self.cb_lub = QComboBox()
        self.cb_lub.setStyleSheet(COMBO)
        self.cb_lub.addItems([
            '脂润滑',
            '油润滑'])
        self.cb_bore = QComboBox()
        self.cb_bore.setStyleSheet(COMBO)
        self.cb_bore.addItem('不限内径')
        sorted((lambda .0: pass# WARNING: Decompyle incomplete
    )(BD.DEEP_GROOVE.values()())())
        for w in (self.sp_fr, self.sp_fa, self.sp_n, self.sp_h):
            w.setStyleSheet(COMBO)
            for lab, w in enumerate([
                ('径向载荷 Fr', self.sp_fr),
                ('轴向载荷 Fa', self.sp_fa),
                ('转速', self.sp_n),
                ('目标寿命', self.sp_h),
                ('润滑', self.cb_lub),
                ('内径', self.cb_bore)]):
                g.addWidget(QLabel(lab), (i // 3) * 2, i % 3)
                g.addWidget(w, (i // 3) * 2 + 1, i % 3)
                lay.addLayout(g)
                btn = QPushButton('推荐型号')
                btn.setStyleSheet(BTN)
                btn.clicked.connect(self.on_reverse)
                lay.addWidget(btn)
                frow = QHBoxLayout()
                frow.addStretch()
                frow.addWidget(f)
                frow.addStretch()
                root.addLayout(frow)
                self.table = QTableWidget(0, 8)
                self.table.setHorizontalHeaderLabels([
                    '型号',
                    '内径 d',
                    '外径 D',
                    '宽 B',
                    'Cr',
                    'C0r',
                    'P',
                    'L10h'])
                self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
                self.table.verticalHeader().setVisible(False)
                self.table.setEditTriggers(QTableWidget.NoEditTriggers)
                self.table.setStyleSheet(f'''QTableWidget{{background:{CARD};gridline-color:#e3e8ee;}}''')
                root.addWidget(self.table, 1)
                return None
    def on_reverse(self):
        lub = 'grease' if self.cb_lub.currentText() == '脂润滑' else 'oil'
        bore = None if self.cb_bore.currentIndex() == 0 else float(self.cb_bore.currentText())
        hits = BD.recommend(self.sp_fr.value(), self.sp_fa.value(), self.sp_n.value(), self.sp_h.value(), lub, bore)
        self.table.setRowCount(0)
        self.table.clearSpans()
        for h in hits:
            r = self.table.rowCount()
            self.table.insertRow(r)
            vals = [
                h['code'],
                f'''{h['d']}''',
                f'''{h['D']}''',
                f'''{h['B']}''',
                f'''{h['Cr']:.1f}''',
                f'''{h['C0r']:.2f}''',
                f'''{h['P']:.2f}''',
                f'''{h['L10h']:,}''']
            for c, v in enumerate(vals):
                it = QTableWidgetItem(v)
                if c == 0:
                    it.setForeground(QBrush(QColor(ACCENT)))
                    f = it.font()
                    f.setBold(True)
                    it.setFont(f)
                self.table.setItem(r, c, it)
                if not hits:
                    it = QTableWidgetItem('无满足条件的型号 — 建议改用滚子类轴承，或降低载荷/转速后重试')
                    self.table.insertRow(0)
                    self.table.setItem(0, 0, it)
                    self.table.setSpan(0, 0, 1, 8)
                    return None
                return None
    __classcell__ = None
DLG_3D = '所有文件 (*.*);;三维模型 (*.step *.stp *.iges *.igs *.stl *.obj *.brep *.x_t *.x_b)'
DLG_DRAWING = '所有文件 (*.*);;图纸 (*.pdf *.dwg *.dxf *.png *.jpg *.jpeg *.webp *.bmp)'
CHIP_CSS = f'''QPushButton{{background:#eef2f7;border:1px solid #dde4ec;border-radius:12px;padding:4px 12px;color:{TEXT};}}QPushButton:checked{{background:{ACCENT};color:white;border-color:{ACCENT};}}QPushButton:hover{{border-color:''' + ACCENT + ';}'
GROUP_CSS = '#eef2f7'
BTN2 = f'''QPushButton{{background:#eef2f7;border:1px solid #dde4ec;border-radius:6px;padding:5px 12px;color:{TEXT};}}QPushButton:hover{{border-color:{ACCENT};color:{ACCENT};}}QPushButton:disabled{{color:#b6c0ca;}}'''

def _dot_color(p):
    if not p:
        return '#d5dce4'
    return OK_C if None.file_status(p) else WARN_C
def _res_icon(rec):
    '''列表小图标：三个状态点 = 三维 / 图纸 / 供应商·链接'''
    pm = QPixmap(38, 16)
    pm.fill(Qt.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing)
    dots = (_dot_color(rec['three_d']), _dot_color(rec['drawing']), OK_C if rec['supplier'] or rec['url'] else '#d5dce4')
    for i, c in enumerate(dots):
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(c))
        p.drawEllipse(3 + i * 12, 3, 10, 10)
        p.end()
        return QIcon(pm)
class CollectionTab:
    '''资源收藏（主从布局）：左列型号带状态点，右侧大详情卡逐项登记。

    使用逻辑：左列搜索/筛选找型号（圆点一眼分辨登记状态）→ 右侧看该型号全部资源，
    文字行内直接输入、文件大按钮指定/打开；密封/材料/游隙为全型号通用知识，收进对话框讲一次。
    '''

    def __init__(self):
        super().__init__()
        self.res = B3.load_lib()
        root = QVBoxLayout(self)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(8)
        (f, lay) = card()
        top = QHBoxLayout()
        t = QLabel('<b>资源收藏</b>')
        t.setStyleSheet(f'''font-size:15px;font-weight:bold;color:{TEXT};border:none;''')
        top.addWidget(t, 1)
        self.btn_knowledge = QPushButton('变体知识详解')
        self.btn_knowledge.setStyleSheet(BTN)
        self.btn_knowledge.setCursor(Qt.PointingHandCursor)
        self.btn_knowledge.clicked.connect(self.on_knowledge)
        top.addWidget(self.btn_knowledge)
        lay.addLayout(top)
        hint = QLabel('左边选型号，右边登记它的三维 / 图纸 / 供应商 / 购买地址（不限文件格式，工具只记录地址、不内置任何文件）。型号前的小圆点依次代表：三维 · 图纸 · 供应商链接 是否已登记。')
        hint.setWordWrap(True)
        hint.setStyleSheet(f'''color:{TEXT_G};font-size:11px;border:none;''')
        lay.addWidget(hint)
        self.lbl_count = QLabel('')
        self.lbl_count.setTextFormat(Qt.RichText)
        self.lbl_count.setStyleSheet(f'''color:{TEXT_G};border:none;''')
        lay.addWidget(self.lbl_count)
        root.addWidget(f)
        sp = QSplitter(Qt.Horizontal)
        left = QWidget()
        ll = QVBoxLayout(left)
        ll.setContentsMargins(0, 0, 0, 0)
        ll.setSpacing(8)
        self.ed_search = QLineEdit()
        self.ed_search.setPlaceholderText('搜索：型号 / 供应商 / 文件名')
        self.ed_search.setClearButtonEnabled(True)
        self.ed_search.setStyleSheet(COMBO)
        self.ed_search.textChanged.connect(self.refresh)
        ll.addWidget(self.ed_search)
        self.filters = QButtonGroup(self)
        self.filters.setExclusive(True)
        self.chips = { }
        grid = QGridLayout()
        grid.setHorizontalSpacing(6)
        grid.setVerticalSpacing(6)
        for key, label in enumerate((('all', '全部'), ('no3d', '缺三维'), ('nodwg', '缺图纸'), ('nosup', '缺供应商'), ('filled', '已登记'), ('lost', '文件丢失'))):
            b = QPushButton(label)
            b.setCheckable(True)
            b.setStyleSheet(CHIP_CSS)
            b.setCursor(Qt.PointingHandCursor)
            if key == 'all':
                b.setChecked(True)
            self.filters.addButton(b)
            self.chips[key] = b
            b.toggled.connect(self.refresh)
            grid.addWidget(b, i // 3, i % 3)
            ll.addLayout(grid)
            self.list = QListWidget()
            self.list.setStyleSheet('QListWidget{background:#fff;border:1px solid #e3e8ee;border-radius:8px;font-size:13px;}QListWidget::item{height:32px;padding-left:6px;}QListWidget::item:selected{background:#e8f0fe;border-left:3px solid ' + ACCENT + ';}')
            self.list.currentItemChanged.connect(self.on_list_changed)
            ll.addWidget(self.list, 1)
            btn_add = QPushButton('＋ 自定义型号')
            btn_add.setStyleSheet(BTN2)
            btn_add.setCursor(Qt.PointingHandCursor)
            btn_add.clicked.connect(self.on_add_custom)
            ll.addWidget(btn_add)
            sp.addWidget(left)
            sc = QScrollArea()
            sc.setWidgetResizable(True)
            sc.setFrameShape(QFrame.NoFrame)
            sc.setStyleSheet('QScrollArea{background:transparent;}')
            self.detail_host = QWidget()
            self._build_detail()
            sc.setWidget(self.detail_host)
            sp.addWidget(sc)
            sp.setStretchFactor(0, 0)
            sp.setStretchFactor(1, 1)
            sp.setSizes([
                286,
                660])
            root.addWidget(sp, 1)
            self.refresh()
            return None
    def _build_detail(self):
        self.detail_host.setStyleSheet('background:transparent;')
        dl = QVBoxLayout(self.detail_host)
        dl.setContentsMargins(4, 2, 8, 2)
        dl.setSpacing(8)
        head = QHBoxLayout()
        self.lbl_model = QLabel('—')
        self.lbl_model.setStyleSheet(f'''font-size:22px;font-weight:bold;color:{ACCENT};border:none;''')
        head.addWidget(self.lbl_model)
        head.addStretch()
        self.lbl_badge = QLabel('')
        self.lbl_badge.setTextFormat(Qt.RichText)
        self.lbl_badge.setStyleSheet('border:none;')
        head.addWidget(self.lbl_badge)
        dl.addLayout(head)
        self.lbl_dims = QLabel('')
        self.lbl_dims.setWordWrap(True)
        self.lbl_dims.setStyleSheet(f'''color:{TEXT};border:none;''')
        dl.addWidget(self.lbl_dims)
        dl.addSpacing(2)

        def file_block(title, btns):
            cap = QLabel(title)
            cap.setStyleSheet(f'''font-weight:bold;color:{TEXT};border:none;''')
            dl.addWidget(cap)
            lbl = QLabel('')
            lbl.setWordWrap(True)
            lbl.setStyleSheet(f'''color:{TEXT_G};border:none;''')
            dl.addWidget(lbl)
            row = QHBoxLayout()
            for key, text in (('pick', '指定文件…'), ('open', '打开'), ('folder', '所在文件夹'), ('clear', '清除')):
                b = QPushButton(text)
                b.setStyleSheet(BTN if key == 'pick' else BTN2)
                b.setCursor(Qt.PointingHandCursor)
                btns[key] = b
                row.addWidget(b)
                row.addStretch()
                dl.addLayout(row)
                return lbl
        self.btns_3d, self.btns_dwg = { }, { }
        self.lbl_3d = file_block('三维模型', self.btns_3d)
        self.lbl_dwg = file_block('图纸', self.btns_dwg)
        None((lambda : self._pick('three_d')))
        None((lambda : self._open_file('three_d')))
        None((lambda : self._open_folder('three_d')))
        None((lambda : self._clear('three_d')))
        None((lambda : self._pick('drawing')))
        None((lambda : self._open_file('drawing')))
        None((lambda : self._open_folder('drawing')))
        None((lambda : self._clear('drawing')))
        g = QGridLayout()
        g.setHorizontalSpacing(10)
        g.setVerticalSpacing(8)
        g.setColumnStretch(1, 1)
        self._ed = { }
        for field, label in enumerate((('supplier', '供应商'), ('url', '购买地址'), ('note', '备注'), ('group', '分类'))):
            lab = QLabel(label)
            lab.setStyleSheet(f'''font-weight:bold;color:{TEXT};border:none;''')
            ed = QLineEdit()
            ed.setStyleSheet(COMBO)
            ed.setPlaceholderText('点这里直接输入，回车或点别处即保存')
            None((lambda ff = None: self._save_text(ff)))
            g.addWidget(lab, r, 0)
            g.addWidget(ed, r, 1)
            self._ed[field] = ed
            self._ed['note'].setPlaceholderText('选型备注、询价记录…')
            self._ed['group'].setPlaceholderText('如「减速机项目」— 同类型号共用供应商时归为一堆')
            self.btn_url = QPushButton('打开链接')
            self.btn_url.setStyleSheet(BTN2)
            self.btn_url.setCursor(Qt.PointingHandCursor)
            self.btn_url.clicked.connect(self.on_open_url)
            g.addWidget(self.btn_url, 1, 2)
            dl.addLayout(g)
            dl.addSpacing(2)
            self.btn_apply = QPushButton('套用其他型号的供应商/购买地址…')
            self.btn_apply.setStyleSheet(BTN2)
            self.btn_apply.setCursor(Qt.PointingHandCursor)
            self.btn_apply.clicked.connect(self.on_apply_contact)
            arow = QHBoxLayout()
            arow.addWidget(self.btn_apply)
            arow.addStretch()
            dl.addLayout(arow)
            self.lbl_vsum = QLabel('')
            self.lbl_vsum.setWordWrap(True)
            self.lbl_vsum.setTextFormat(Qt.RichText)
            self.lbl_vsum.setStyleSheet(f'''color:{TEXT_G};font-size:11px;border:none;''')
            dl.addWidget(self.lbl_vsum)
            return None
    def _mode(self):
        for key, b in self.chips.items():
            if b.isChecked():

                return None, key
            return 'all'
    def _shown(self):
        rows = B3.filter_models(self.res, list(BD.DEEP_GROOVE.keys()), self.ed_search.text(), False)
        mode = self._mode()
        if mode == 'no3d':
            rows = rows()
        elif mode == 'nodwg':
            rows = rows()
        elif mode == 'nosup':
            rows = rows()
        elif mode == 'filled':
            rows = rows()
        elif mode == 'lost':
            rows = rows()
        return rows
    def _rec(self, m):
        r = B3._blank()
        r.update(self.res.get(m, { }))
        return r
    def _filled_n(self, rec):
        pass

    _tip = (lambda m, rec: pass)()

    def _current_model(self):
        it = self.list.currentItem()
        return it.data(Qt.UserRole) if it else None
    def on_list_changed(self, *_):
        self.update_detail()
    def refresh(self):
        '''重建左列（尽量保留当前选中型号），并刷新右侧与统计。'''
        keep = self._current_model()
        shown = self._shown()
        self.list.blockSignals(True)
        self.list.clear()
        row_for = { }
        last_group = None
        GROUPS = {
            '60': '60 系列',
            '62': '62 系列',
            '63': '63 系列' }
        for m, rec in shown:
            grp = GROUPS.get(m[:2], '自定义型号') if m in BD.DEEP_GROOVE else '自定义型号'
            if grp != last_group:
                sep = QListWidgetItem('　▍' + grp)
                sep.setFlags(Qt.NoItemFlags)
                sep.setForeground(QBrush(QColor(TEXT_G)))
                fo = sep.font()
                fo.setBold(True)
                sep.setFont(fo)
                self.list.addItem(sep)
                last_group = grp
            it = QListWidgetItem(_res_icon(rec), m)
            it.setData(Qt.UserRole, m)
            it.setToolTip(self._tip(m, rec))
            self.list.addItem(it)
            row_for[m] = it
            if not row_for.get(keep):
                target = next(iter(row_for.values()), None)
                if target:
                    self.list.setCurrentItem(target)
        self.list.blockSignals(False)
        if target:
            self.list.scrollToItem(target)
        self.update_detail()
        self._update_count()
    def _update_count(self):
        pass


    def update_detail(self):
        m = self._current_model()
        for ed in self._ed.values():
            ed.blockSignals(True)
            if not m:
                self.lbl_model.setText('—')
                self.lbl_badge.setText('')
                self.lbl_dims.setText('左列没有匹配的型号：换个关键词，或点「全部」复位筛选。')
                self.lbl_3d.setText('')
                self.lbl_dwg.setText('')
                for b in list(self.btns_3d.values()) + list(self.btns_dwg.values()) + [
                    self.btn_url,
                    self.btn_apply]:
                    b.setEnabled(False)
                    for ed in self._ed.values():
                        ed.clear()
                        ed.setEnabled(False)
                        self.lbl_vsum.setText('')
                        for ed in self._ed.values():
                            ed.blockSignals(False)
                            return None
                            rec = self._rec(m)
                            spec = BD.DEEP_GROOVE.get(m)
                            self.lbl_model.setText(m)
                            n = self._filled_n(rec)
                            if n == 3:
                                pass
                            elif n:
                                pass

        col = TEXT_G
        self.lbl_badge.setText(f'''<b style=\'color:{col};\'>已登记 {n}/3</b>''')
        for lbl, btns, kind in ((self.lbl_3d, self.btns_3d, 'three_d'), (self.lbl_dwg, self.btns_dwg, 'drawing')):
            p = rec[kind]
            if bool(p):
                btns['open'].setEnabled(B3.file_status(p))
                if bool(p):
                    btns['folder'].setEnabled(B3.file_status(p))
                    btns['clear'].setEnabled(bool(p))
                    continue
                    for field, ed in self._ed.items():
                        ed.setEnabled(True)
                        ed.setText(rec[field])
                        for ed in self._ed.values():
                            ed.blockSignals(False)
                            self.btn_url.setEnabled(bool(rec['url'].strip()))
                            self.btn_apply.setEnabled(True)
                            seal_names = (lambda .0: for s in .0:
    s[0]None)(BD.SEAL_TYPES())
                            clr_names = (lambda .0: for c in .0:
    c[0]None)(BD.CLEARANCES())
                            mat_names = (lambda .0: for x in .0:
    x[0]None)(BD.MATERIALS())
                            self.lbl_vsum.setText(f'''同一型号的介绍基本通用：密封（{seal_names}）· 游隙（{clr_names}）· 材料（{mat_names}）— 适用场景与转速影响见右上「变体知识详解」；关键参数以所选厂家样本原文为准''')
                            return None
    def _sync_item(self, m):
        '''文字保存后只同步该型号的圆点/提示/徽章，不整页重建（不打断连续录入）。'''
        rec = self._rec(m)
        for i in range(self.list.count()):
            it = self.list.item(i)
            if it.data(Qt.UserRole) == m:
                it.setIcon(_res_icon(rec))
                it.setToolTip(self._tip(m, rec))

            if m == self._current_model():
                n = self._filled_n(rec)
                if n == 3:
                    pass
                elif n:
                    pass

                col = TEXT_G
                self.lbl_badge.setText(f'''<b style=\'color:{col};\'>已登记 {n}/3</b>''')
                self.btn_url.setEnabled(bool(rec['url'].strip()))
                return None
            return None
    def _save_text(self, field):
        m = self._current_model()
        if not m:
            return None
        ed = None._ed[field]
        (self.res, _e) = B3.set_text(self.res, m, field, ed.text())
        B3.save_lib(self.res)
        self._sync_item(m)
        self._update_count()
    def _pick(self, kind):
        m = self._current_model()
        if not m:
            return None
        (title, dlg) = ('选择三维文件', DLG_3D) if None == 'three_d' else ('选择图纸文件', DLG_DRAWING)
        (path, _) = QFileDialog.getOpenFileName(self, title, '', dlg)
        if path:
            self._set_file_direct(m, kind, path)
            return None
    def _set_file_direct(self, model, kind, path):
        '''登记入口（按钮与测试共用），返回错误信息（空串=成功）。'''
        (self.res, err) = B3.set_file(self.res, model, kind, path)
        if err:
            self.lbl_count.setText(f'''<span style=\'color:{WARN_C};\'>{err}</span>''')
            return err
        None.save_lib(self.res)
        self.refresh()
        return ''
    def _clear(self, field):
        m = self._current_model()
        if not m:
            return None
        (self.res, _) = None.clear_field(self.res, m, field)
        B3.save_lib(self.res)
        self.refresh()
    def on_add_custom(self):
        (name, okd) = QInputDialog.getText(self, '添加自定义型号', '型号名称（如 6310-2RS、厂家内部编号）：')
        if not name:
            name = ''.strip()
            if not okd or name:
                return None
            if None not in self.res:
                self.res[name] = B3._blank()
                B3.save_lib(self.res)
        if self.ed_search.text():
            self.ed_search.clear()
        elif self._mode() != 'all':
            self.chips['all'].setChecked(True)
        else:
            self.refresh()
        for i in range(self.list.count()):
            it = self.list.item(i)
            if it.data(Qt.UserRole) == name:
                self.list.setCurrentItem(it)
                self.list.scrollToItem(it)
                return None
            return None
    def on_apply_contact(self):
        pass


    def _apply_contact(self, src, group_name):
        pass


    def _open_file(self, kind):
        m = self._current_model()
        if not m:
            return None
        p = None._rec(m)[kind]
        if p or B3.file_status(p):
            QDesktopServices.openUrl(QUrl.fromLocalFile(p))
            return None
        return None
    def _open_folder(self, kind):
        m = self._current_model()
        if not m:
            return None
        p = None._rec(m)[kind]
        if p or B3.file_status(p):
            QDesktopServices.openUrl(QUrl.fromLocalFile(os.path.dirname(p)))
            return None
        return None
    def on_open_url(self):
        m = self._current_model()
        if not m:
            return None
        u = None._rec(m)['url'].strip()
        if u:
            if not u.lower().startswith(('http://', 'https://')):
                u = 'https://' + u
            QDesktopServices.openUrl(QUrl(u))
            return None
    def _knowledge_html(self):
        html = [
            "<b style='font-size:14px;'>同一型号（如 6205）按密封 / 材料 / 游隙分成多种变体，以下知识对所有深沟球型号通用</b>"]
        html.append("<br><br><b style='color:#2f6fed;'>① 密封形式（型号后缀）</b>")
        for name, feat, factor, scene in BD.SEAL_TYPES:
            rpm = '极限转速不降' if factor >= 1 else f'''极限转速按 ×{factor} 折减'''
            html.append(f'''<br><b>{name}</b>：{feat}<br><span style=\'color:#555;font-size:11px;\'>{rpm}；适用：{scene}</span>''')
            html.append("<br><br><b style='color:#2f6fed;'>② 材料</b>")
            for n, ft, sc in BD.MATERIALS:
                html.append(f'''<br><b>{n}</b>：{ft}<br><span style=\'color:#555;font-size:11px;\'>适用：{sc}</span>''')
                html.append("<br><br><b style='color:#2f6fed;'>③ 游隙（型号后缀）</b>")
                for n, ft, sc in BD.CLEARANCES:
                    html.append(f'''<br><b>{n}</b>：{ft}<br><span style=\'color:#555;font-size:11px;\'>适用：{sc}</span>''')
                    html.append(f'''<br><br><span style=\'color:#555;font-size:11px;\'>{BD.SUFFIX_NOTES}；游隙数值以 6205 为例，其他型号原理相同</span>''')
                    return ''.join(html)
    def on_knowledge(self):
        dlg = QDialog(self)
        dlg.setWindowTitle('变体知识速查（通用）')
        dlg.resize(620, 660)
        v = QVBoxLayout(dlg)
        lbl = QLabel(self._knowledge_html())
        lbl.setWordWrap(True)
        lbl.setTextFormat(Qt.RichText)
        lbl.setStyleSheet('background:#fff;padding:14px;')
        sc2 = QScrollArea()
        sc2.setWidgetResizable(True)
        sc2.setWidget(lbl)
        sc2.setFrameShape(QFrame.NoFrame)
        v.addWidget(sc2, 1)
        row = QHBoxLayout()
        row.addStretch()
        b = QPushButton('知道了')
        b.setStyleSheet(BTN)
        b.clicked.connect(dlg.accept)
        row.addWidget(b)
        v.addLayout(row)
        dlg.exec()
    __classcell__ = staticmethod
    return staticmethod
class AboutTab:
    '''关于：版本、数据来源、合规与免责'''

    def __init__(self):
        super().__init__()
        root = QVBoxLayout(self)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(10)
        (f, lay) = card()
        f.setMaximumWidth(680)
        lay.setContentsMargins(24, 24, 24, 24)
        lay.setSpacing(10)
        logo = QLabel()
        logo.setPixmap(_paint_glyph('bearing', 72))
        logo.setAlignment(Qt.AlignHCenter)
        logo.setStyleSheet('border:none;')
        lay.addWidget(logo)
        t = QLabel(f'''轴承选型工具 {BD.VERSION}''')
        t.setAlignment(Qt.AlignHCenter)
        t.setStyleSheet(f'''font-size:18px;font-weight:bold;color:{TEXT};border:none;''')
        lay.addWidget(t)

        def section(head, body):
            h = QLabel(head)
            h.setStyleSheet(f'''font-weight:bold;color:{ACCENT};border:none;''')
            b = QLabel(body)
            b.setWordWrap(True)
            b.setStyleSheet(f'''color:{TEXT};border:none;''')
            lay.addSpacing(6)
            lay.addWidget(h)
            lay.addWidget(b)
        section('功能', '场合速选 · 寿命校核 · 反向选型 · 资源收藏（三维/图纸/供应商/购买地址）')
        section('计算方法', 'L10 = (C/P)³ × 10⁶ 转（ISO 281，球轴承指数 3）；当量动载荷 P = X·Fr + Y·Fa')
        section('数据来源', '深沟球轴承 6000/6200/6300 系列共 63 个型号，参数依据 NTN 现行样本等各厂家公开资料整理，不同厂家同型号数值略有差异，关键参数请以所选厂家样本原文复核')
        section('资源收藏', '三维/图纸/供应商/购买地址均只记录用户自备资源的本地地址与文字信息，不内置、不分发任何文件')
        section('开源许可', '本程序界面基于 PySide6（LGPLv3）构建')
        sec = QLabel('免责声明')
        sec.setStyleSheet(f'''font-weight:bold;color:{WARN_C};border:none;''')
        lay.addSpacing(6)
        lay.addWidget(sec)
        dis = QLabel('工具是业余时间做的，重要参数请多查一本手册，别全信我，仅供学习参考🙏')
        dis.setWordWrap(True)
        dis.setStyleSheet(f'''color:{TEXT};border:none;''')
        lay.addWidget(dis)
        row = QHBoxLayout()
        row.addStretch()
        row.addWidget(f)
        row.addStretch()
        root.addStretch()
        root.addLayout(row)
        root.addStretch()
    __classcell__ = None
class MainWindow:

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f'''轴承选型工具 {BD.VERSION}''')
        self.setWindowIcon(glyph_icon('bearing'))
        self.setMinimumSize(980, 720)
        self.resize(1060, 760)
        self.setStyleSheet(f'''QWidget{{background:{BG};}} QLabel{{color:{TEXT};border:none;}}''')
        tabs = QTabWidget()
        tabs.setStyleSheet('QTabWidget::pane{border:none;}')
        self.tabs = tabs
        self.guide_tab = GuideTab()
        self.check_tab = CheckTab()
        self.reverse_tab = ReverseTab()
        self.coll_tab = CollectionTab()
        self.about_tab = AboutTab()
        for kind, w, text in (('guide', self.guide_tab, '场合速选'), ('check', self.check_tab, '寿命校核'), ('reverse', self.reverse_tab, '反向选型'), ('cube', self.coll_tab, '资源收藏'), ('about', self.about_tab, '关于')):
            tabs.addTab(w, glyph_icon(kind, 20), text)
            self.setCentralWidget(tabs)
            return None
    __classcell__ = None
def _anti_debug():
    '''反调试（开发手册开发红线 10）：检测到调试器即退出。'''

    try:
        import ctypes
        if ctypes.windll.kernel32.IsDebuggerPresent():
            sys.exit(0)
            return None
        return None
    except (AttributeError, OSError):
        return None
def _crash_log_path():
    if not os.environ.get('BEARINGTOOL_HOME'):
        pass
    base = os.path.join(os.path.expanduser('~'), '.BearingTool')
    return os.path.join(base, 'crash.log')
def _write_crash_log(err):
    '''写入 crash.log（开发手册红线 10）；写不出时退回标准错误，不静默丢弃。'''

    try:
        path = _crash_log_path()
        os.makedirs(os.path.dirname(path), exist_ok = True)
        f = open(path, 'w', encoding = 'utf-8')
        f.write(err)

        try:
            None(None, None)
        with None:
            if not None:

                try:

                    try:
                        return path
                    except OSError:
                        exc = None
                        print(f'''[crash.log 写入失败: {exc}]\n{err}''', file = sys.stderr)
                        exc = None
                        del exc
                        return None
                        exc = None
                        del exc
def main():
    _anti_debug()

    try:
        app = QApplication(sys.argv)
        app.setWindowIcon(glyph_icon('bearing'))
        if dialogs.is_first_run():
            welcome = dialogs.WelcomeDialog()
            if welcome.exec() != QDialog.Accepted:
                sys.exit(0)
            cfg = dialogs.load_config()
            cfg['first_run'] = False
            dialogs.save_config(cfg)
        if not dialogs.is_unlocked():
            lock = dialogs.LockDialog()
            if lock.exec() != QDialog.Accepted:
                sys.exit(0)
        if not dialogs.is_disclaimer_accepted():
            disc = dialogs.DisclaimerDialog()
            if disc.exec() != QDialog.Accepted:
                sys.exit(0)
        win = MainWindow()
        win.show()
        sys.exit(app.exec())
        return None
    except SystemExit:
        raise 
        except Exception:
            import traceback
            err = traceback.format_exc()
            _write_crash_log(err)
            QMessageBox = QMessageBox
            import PySide6.QtWidgets
            QMessageBox.critical(None, f'''轴承选型工具 {BD.VERSION} — 启动失败''', f'''请将以下信息发给开发者：\n\n{err[-1000:]}''')
        except Exception:
            print(err)
        sys.exit(1)
        return None
if __name__ == '__main__':
    main()
    return None
