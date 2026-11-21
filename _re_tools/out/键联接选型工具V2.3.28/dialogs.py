# Reconstructed from bytecode by split_decompile.py
# dialogs.pyc

'''键联接选型工具 - 首次欢迎 + 密码锁对话框（与公差查询工具统一风格）'''
import os
import json
import sys
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QFrame, QSizePolicy
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QFont
from key_data import VERSION
BG = '#0f0f14'
CARD = '#1a1a24'
BORDER = '#2a2a3a'
TEXT = '#e0e0e8'
TEXT2 = '#8888a0'
ACCENT = '#6c8cff'
GREEN = '#5cd68a'
ORANGE = '#f0a050'
_APP_DIR = os.path.join(os.path.expanduser('~'), '.KeyTool')
os.makedirs(_APP_DIR, exist_ok = True)
CONFIG_PATH = os.path.join(_APP_DIR, 'config.json')
PASSWORD_HASH = 'c76d09e61444b6081ad0adb484b2bb231acba4d1d46369ddd03598b936115b6e'

def _qr_path():
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, 'assets', 'qrcode.png')
    return None.path.join(os.path.dirname(__file__), 'assets', 'qrcode.png')
def _load_config():
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
                            except Exception:
                                pass

                            return { }
def _save_config(cfg):
    f = open(CONFIG_PATH, 'w', encoding = 'utf-8')
    json.dump(cfg, f, ensure_ascii = False, indent = 2)
    None(None, None)
    return None
    with None:
        if not None:
            pass
def is_first_run():
    return not _load_config().get('unlocked', False)
def is_unlocked():
    return _load_config().get('unlocked', False)
class WelcomeDialog:

    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle('键联接选型工具 — 使用说明')
        self.setFixedSize(520, 560)
        self.setStyleSheet(f'''QDialog {{ background: {BG}; }}''')
        root = QVBoxLayout(self)
        root.setSpacing(10)
        root.setContentsMargins(24, 20, 24, 20)
        title = QLabel(f'''🔩 键联接选型工具 {VERSION}''')
        title.setFont(QFont('Microsoft YaHei', 16, QFont.Weight.Bold))
        title.setStyleSheet(f'''color: {TEXT};''')
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(title)
        subtitle = QLabel('智能选型 · 平键 · 半圆键 · 楔键 · 花键  一键速查')
        subtitle.setStyleSheet(f'''color: {TEXT2}; font-size: 13px;''')
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(subtitle)
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet(f'''background: {BORDER}; max-height: 1px;''')
        root.addWidget(line)
        features = [
            ('⚙️  智能选型', '输入轴径+工况条件，按工况推荐合用的键类型，\n并给出推荐度评分和依据'),
            ('📏  平键/半圆键/楔键', 'GB/T 1096/1099/1564/1565标准查表，\n自动确定截面尺寸、键长，校核挤压和剪切强度'),
            ('🔩  矩形花键', 'GB/T 1144-2001标准，小径/大径/齿侧定心，\n支持重载和高精度场合选型')]
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
        self.setWindowTitle('键联接选型工具 — 解锁')
        self.setFixedSize(420, 520)
        self.setStyleSheet(f'''QDialog {{ background: {BG}; }}''')
        self._ok = False
        root = QVBoxLayout(self)
        root.setSpacing(10)
        root.setContentsMargins(28, 24, 28, 20)
        title = QLabel('🔒 键联接选型工具')
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
        hint = QLabel('扫码关注公众号「机械领域-0-开」获取解锁密码\n一次解锁，永久使用')
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

