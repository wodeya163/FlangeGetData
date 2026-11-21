# Reconstructed from bytecode by split_decompile.py
# dialogs.relaxed.pyc

'''轴承选型工具 - 启动三件套：欢迎 / 密码锁 / 免责声明（与系列工具统一风格）

三件套齐备是《机械工具箱开发手册》第五章合规校验的强制项
（check_compliance.py 检查 WelcomeDialog / LockDialog / DisclaimerDialog）。
'''
import os
import json
import sys
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QLineEdit, QFrame, QCheckBox, QScrollArea, QWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QFont
from bearing_data import VERSION
BG = '#0f0f14'
CARD = '#1a1a24'
BORDER = '#2a2a3a'
TEXT = '#e0e0e8'
TEXT2 = '#8888a0'
ACCENT = '#6c8cff'
ORANGE = '#f0a050'
if not os.environ.get('BEARINGTOOL_HOME'):
    pass
_APP_DIR = os.path.join(os.path.expanduser('~'), '.BearingTool')
os.makedirs(_APP_DIR, exist_ok = True)
CONFIG_PATH = os.path.join(_APP_DIR, 'config.json')
PASSWORD_HASH = 'c76d09e61444b6081ad0adb484b2bb231acba4d1d46369ddd03598b936115b6e'

def _qr_path():
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, 'assets', 'qrcode.png')
    return None.path.join(os.path.dirname(__file__), 'assets', 'qrcode.png')
def load_config():
    '''读取本工具配置（《开发手册》第五章标准命名）。缺失/损坏返回 {}。'''
    if os.path.exists(CONFIG_PATH):

        try:
            f = open(CONFIG_PATH, 'r', encoding = 'utf-8-sig')

            try:
                (None, None)
                return None, json.load(f)
                with None:
                    if not None:

                        try:

                            try:
                                pass
                            except (ValueError, OSError):
                                return 

                            return { }
def save_config(cfg):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok = True)
    f = open(CONFIG_PATH, 'w', encoding = 'utf-8')
    json.dump(cfg, f, ensure_ascii = False, indent = 2)
    None(None, None)
    return None
    with None:
        if not None:
            pass
_load_config = load_config
_save_config = save_config

def is_first_run():
    '''是否首次运行（《开发手册》第五章标准：读 first_run 字段，缺省 True）。

    注意：不可写成 not unlocked ——那会把"是否看过欢迎页"和"是否已解锁"绑成
    同一个开关，解锁后配置文件里没有 first_run 记录，欢迎页状态无法持久化。
    '''
    return load_config().get('first_run', True)
def is_unlocked():
    return load_config().get('unlocked', False)
def is_disclaimer_accepted():
    return load_config().get('disclaimer_accepted', False)
class WelcomeDialog:

    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle('轴承选型工具 — 使用说明')
        self.setFixedSize(520, 580)
        self.setStyleSheet(f'''QDialog {{ background: {BG}; }}''')
        root = QVBoxLayout(self)
        root.setSpacing(10)
        root.setContentsMargins(24, 20, 24, 20)
        title = QLabel(f'''⚙️ 轴承选型工具 {VERSION}''')
        title.setFont(QFont('Microsoft YaHei', 16, QFont.Weight.Bold))
        title.setStyleSheet(f'''color: {TEXT};''')
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(title)
        subtitle = QLabel('场合速选 · 寿命校核 · 反向选型 · 资源收藏  一站搞定')
        subtitle.setStyleSheet(f'''color: {TEXT2}; font-size: 13px;''')
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(subtitle)
        beta = QLabel('本版为测试版，功能与数据仍在完善；重要场合请以所选厂家样本复核')
        beta.setStyleSheet(f'''color: {TEXT2}; font-size: 11px;''')
        beta.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(beta)
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet(f'''background: {BORDER}; max-height: 1px;''')
        root.addWidget(line)
        features = [
            ('🧭  场合速选', '按工况（载荷大小与方向、转速、是否调心、安装空间…）逐项选择，\n给出推荐排序和各自适合的场景'),
            ('📐  寿命校核', '输入载荷/转速，自动查 e/Y 系数算当量载荷，\nL10h 额定寿命 + 静载荷安全系数一步出结果'),
            ('🔍  反向选型', '已知轴径和载荷，反推满足寿命要求的深沟球型号'),
            ('🗂️  资源收藏', '每个型号可登记三维/图纸/供应商/购买地址，\n支持分类归组和一键套用其它型号的采购信息')]
        for icon_title, desc in features:
            row = QLabel(f'''  {icon_title}''')
            row.setStyleSheet(f'''color: {ACCENT}; font-size: 13px; font-weight: bold; padding: 6px 0 2px 0;''')
            root.addWidget(row)
            for line_text in desc.split('\n'):
                d = QLabel(f'''    {line_text}''')
                d.setStyleSheet(f'''color: {TEXT}; font-size: 12px; padding: 1px 0;''')
                root.addWidget(d)
                line2 = QFrame()
                line2.setFrameShape(QFrame.Shape.HLine)
                line2.setStyleSheet(f'''background: {BORDER}; max-height: 1px;''')
                root.addWidget(line2)
                hint = QLabel('点击「开始使用」后，请扫描公众号「机械领域-0-开」二维码获取解锁密码')
                hint.setStyleSheet(f'''color: {TEXT2}; font-size: 11px;''')
                hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
                root.addWidget(hint)
                btn = QPushButton('开始使用 →')
                btn.setFixedHeight(36)
                btn.setCursor(Qt.CursorShape.PointingHandCursor)
                btn.setStyleSheet(f'''\n            QPushButton {{\n                background: {ACCENT}; color: white; border: none;\n                border-radius: 6px; font-size: 13px; font-weight: bold;\n            }}\n            QPushButton:hover {{ background: #5a7ae8; }}\n        ''')
                btn.clicked.connect(self.accept)
                root.addWidget(btn)
                return None
    __classcell__ = None
class LockDialog:

    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle('轴承选型工具 — 解锁')
        self.setFixedSize(420, 520)
        self.setStyleSheet(f'''QDialog {{ background: {BG}; }}''')
        self._ok = False
        root = QVBoxLayout(self)
        root.setSpacing(10)
        root.setContentsMargins(28, 24, 28, 20)
        title = QLabel('🔒 轴承选型工具')
        title.setFont(QFont('Microsoft YaHei', 15, QFont.Weight.Bold))
        title.setStyleSheet(f'''color: {TEXT};''')
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(title)
        sub = QLabel('使用前请先解锁')
        sub.setStyleSheet(f'''color: {TEXT2}; font-size: 12px;''')
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(sub)
        qr_label = QLabel()
        qr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        qr_file = _qr_path()
        if os.path.exists(qr_file):
            pixmap = QPixmap(qr_file)
            qr_label.setPixmap(pixmap.scaled(180, 180, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            qr_label.setText('[ 请将公众号二维码放到 assets/qrcode.png ]')
            qr_label.setStyleSheet(f'''color: {ORANGE}; font-size: 12px;''')
            qr_label.setFixedHeight(180)
        root.addWidget(qr_label)
        hint = QLabel('扫码关注公众号「机械领域-0-开」获取解锁密码\n解锁后本机不再重复要求输入（换电脑或清除配置后需重新解锁）')
        hint.setStyleSheet(f'''color: {TEXT2}; font-size: 12px; line-height: 1.6;''')
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(hint)
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet(f'''background: {BORDER}; max-height: 1px;''')
        root.addWidget(line)
        pwd_label = QLabel('请输入解锁密码：')
        pwd_label.setStyleSheet(f'''color: {TEXT}; font-size: 12px;''')
        root.addWidget(pwd_label)
        self.pwd_input = QLineEdit()
        self.pwd_input.setPlaceholderText('请输入密码…')
        self.pwd_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pwd_input.setFixedHeight(34)
        self.pwd_input.setStyleSheet(f'''\n            QLineEdit {{\n                background: {CARD}; color: {TEXT}; border: 1px solid {BORDER};\n                border-radius: 6px; padding: 0 12px; font-size: 13px;\n            }}\n            QLineEdit:focus {{ border-color: {ACCENT}; }}\n        ''')
        self.pwd_input.returnPressed.connect(self._check_password)
        root.addWidget(self.pwd_input)
        self.err_label = QLabel('')
        self.err_label.setStyleSheet('color: #ff6c6c; font-size: 11px;')
        self.err_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(self.err_label)
        btn = QPushButton('🔓 解锁')
        btn.setFixedHeight(36)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(f'''\n            QPushButton {{\n                background: {ACCENT}; color: white; border: none;\n                border-radius: 6px; font-size: 13px; font-weight: bold;\n            }}\n            QPushButton:hover {{ background: #5a7ae8; }}\n        ''')
        btn.clicked.connect(self._check_password)
        root.addWidget(btn)
    def _check_password(self):
        import hashlib
        pwd = self.pwd_input.text().strip()
        if hashlib.sha256(pwd.encode()).hexdigest() == PASSWORD_HASH:
            self._ok = True
            cfg = _load_config()
            cfg['unlocked'] = True
            _save_config(cfg)
            self.accept()
            return None
        None.err_label.setText('❌ 密码错误，请关注公众号获取正确密码')
        self.pwd_input.clear()
        self.pwd_input.setFocus()
    def was_unlocked(self):
        return self._ok
    __classcell__ = None
class DisclaimerDialog:

    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle(f'''轴承选型工具 {VERSION} — 免责声明''')
        self.setFixedSize(540, 560)
        self.setStyleSheet(f'''QDialog {{ background: {BG}; }}''')
        self._accepted = False
        root = QVBoxLayout(self)
        root.setSpacing(10)
        root.setContentsMargins(24, 18, 24, 18)
        title = QLabel('📋 工具声明')
        title.setFont(QFont('Microsoft YaHei', 15, QFont.Weight.Bold))
        title.setStyleSheet(f'''color: {TEXT};''')
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(title)
        sub = QLabel('使用本工具前，请先阅读以下声明')
        sub.setStyleSheet(f'''color: {TEXT2}; font-size: 12px;''')
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(sub)
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet(f'''background: {BORDER}; max-height: 1px;''')
        root.addWidget(line)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet('QScrollArea { border: none; background: transparent; }')
        holder = QWidget()
        hold = QVBoxLayout(holder)
        hold.setSpacing(8)
        hold.setContentsMargins(0, 4, 0, 4)
        clauses = [
            '1. 本工具收录的轴承外形尺寸、额定载荷、极限转速等数据，整理自公开国家标准与轴承厂商公开样本，经人工比对校对，仍可能存在偏差、遗漏或版本滞后。',
            '2. 本工具仅供学习参考，不替代实际工程设计、制造、检验或采购验收所需的正式依据。',
            '3. 同型号轴承的载荷与极限转速因厂家、精度等级、游隙及密封形式不同而略有差异，关键参数请以所选厂家样本原文复核。',
            '4. 极限转速为参考值，实际可用转速还受润滑、冷却、载荷、安装与散热条件影响。',
            '5. 寿命计算采用 GB/T 6391（ISO 281）额定寿命方法，属理论估算；实际寿命受工况、润滑与制造质量影响。',
            '6. 使用者需结合实际情况与专业判断进行决策，因未经验证直接采用本工具数据导致的工程问题，作者不承担责任。',
            '7. 本工具引用的国家标准内容，版权归原作者及发布单位所有；本工具限个人学习参考，禁止捆绑销售、收费授权或嵌入商业系统。',
            '8. 本工具为离线工具，不收集、不上传用户的任何个人数据。']
        for clause in clauses:
            c = QLabel(clause)
            c.setWordWrap(True)
            c.setStyleSheet(f'''color: {TEXT}; font-size: 12px; padding: 6px 8px; background: {CARD}; border: 1px solid {BORDER}; border-radius: 6px;''')
            hold.addWidget(c)
            hold.addStretch()
            scroll.setWidget(holder)
            root.addWidget(scroll)
            line2 = QFrame()
            line2.setFrameShape(QFrame.Shape.HLine)
            line2.setStyleSheet(f'''background: {BORDER}; max-height: 1px;''')
            root.addWidget(line2)
            self.chk = QCheckBox('我已阅读并同意以上声明')
            self.chk.setStyleSheet(f'''color: {TEXT}; font-size: 12px; spacing: 8px;''')
            self.chk.stateChanged.connect(self._on_check)
            root.addWidget(self.chk)
            self.btn = QPushButton('同意并进入工具')
            self.btn.setFixedHeight(36)
            self.btn.setEnabled(False)
            self.btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self.btn.setStyleSheet('QPushButton { background: #4a4a58; color: #9a9aa8; border: none; border-radius: 6px; font-size: 13px; font-weight: bold; }')
            self.btn.clicked.connect(self._do_accept)
            root.addWidget(self.btn)
            return None
    def _on_check(self, state):
        if state:
            self.btn.setEnabled(True)
            self.btn.setStyleSheet(f'''QPushButton {{ background: {ACCENT}; color: white; border: none; border-radius: 6px; font-size: 13px; font-weight: bold; }}QPushButton:hover {{ background: #5a7ae8; }}''')
            return None
        None.btn.setEnabled(False)
        self.btn.setStyleSheet('QPushButton { background: #4a4a58; color: #9a9aa8; border: none; border-radius: 6px; font-size: 13px; font-weight: bold; }')
    def _do_accept(self):
        self._accepted = True
        cfg = _load_config()
        cfg['disclaimer_accepted'] = True
        _save_config(cfg)
        self.accept()
    def was_accepted(self):
        return self._accepted
    __classcell__ = None

