# Reconstructed from bytecode by split_decompile.py
# app.pyc

'''
螺栓拧紧力矩工具 — 密码锁 + 入口
'''
import sys
import os
import json
import subprocess

def _anti_debug():
    if sys.platform == 'win32':

        try:
            result = subprocess.run([
                'tasklist',
                '/FO',
                'CSV',
                '/NH'], capture_output = True, text = True, timeout = 3, creationflags = 134217728)
            debuggers = [
                'ollydbg',
                'x64dbg',
                'x32dbg',
                'ida',
                'ida64',
                'windbg',
                'processhacker',
                'cheatengine']
            output = result.stdout.lower()
            for dbg in debuggers:
                if dbg in output:
                    sys.exit(0)
                return None
                except Exception:
                    return None
                return None
def _check_integrity():
    if not getattr(sys, 'frozen', False):
        return None

    try:
        if os.path.getsize(sys.executable) < 102400:
            sys.exit(0)
            return None
        return None
    except Exception:
        return None
_anti_debug()
_check_integrity()
_APP_DIR = os.path.join(os.path.expanduser('~'), '.TorqueTool')
os.makedirs(_APP_DIR, exist_ok = True)
CONFIG_PATH = os.path.join(_APP_DIR, 'config.json')
PASSWORD = 'jxly0kai'

def _load_config():
    if os.path.exists(CONFIG_PATH):

        try:
            f = open(CONFIG_PATH, 'r', encoding = 'utf-8')

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
def _qr_path():
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, 'assets', 'qrcode.png')
    return None.path.join(os.path.dirname(__file__), 'assets', 'qrcode.png')
def _ico_path():
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, 'assets', 'icon.ico')
    return None.path.join(os.path.dirname(__file__), 'assets', 'icon.ico')
def is_first_run():
    return not _load_config().get('unlocked', False)
def is_unlocked():
    return _load_config().get('unlocked', False)
from PySide6.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFrame, QCheckBox, QScrollArea, QWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QFont, QIcon
from theme import get_palette, build_style
_p = get_palette()
BG = _p['BG']
CARD = _p['CARD']
BORDER = _p['BORDER']
TEXT = _p['TEXT']
TEXT2 = _p['TEXT2']
ACCENT = _p['ACCENT']
ORANGE = _p['ORANGE']
RED = _p['RED']
ACCENT_H = _p['ACCENT_H']

class WelcomeDialog:

    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle('螺栓拧紧力矩工具 — 使用说明')
        self.setFixedSize(480, 380)
        self.setStyleSheet(f'''QDialog {{ background: {BG}; }}''')
        root = QVBoxLayout(self)
        root.setSpacing(10)
        root.setContentsMargins(28, 20, 28, 20)
        title = QLabel('🔩 螺栓拧紧力矩工具')
        title.setFont(QFont('Microsoft YaHei', 16, QFont.Weight.Bold))
        title.setStyleSheet(f'''color: {TEXT};''')
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(title)
        sub = QLabel('外六角 · 内六角 · 自攻螺钉 三合一速查')
        sub.setStyleSheet(f'''color: {TEXT2}; font-size: 13px;''')
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(sub)
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet(f'''background: {BORDER}; max-height: 1px;''')
        root.addWidget(line)
        features = [
            ('📋  外六角螺栓', 'M6~M30 ｜ 8.8/10.9/12.9级 ｜ GB/T 16823.2 查表值'),
            ('🔩  内六角螺钉', 'M3~M24 ｜ 8.8/10.9/12.9级 ｜ DIN 912 / ISO 4762'),
            ('🔧  自攻螺钉', 'ST2.2~ST6.3 ｜ 4种底材场景 ｜ GB/T 5280'),
            ('📐  三档力矩', '最小 · 推荐 · 最大，含粗牙细牙自动换算'),
            ('🎯  工况场景', '一般连接 · 重要承载 · 高温振动，预紧占比实时计算'),
            ('💻  完全离线', '无需联网，数据本地计算，不收集任何个人数据')]
        for icon_title, desc in features:
            row = QLabel(f'''  {icon_title}  —  {desc}''')
            row.setStyleSheet(f'''color: {TEXT}; font-size: 12px; padding: 3px 0;''')
            root.addWidget(row)
            line2 = QFrame()
            line2.setFrameShape(QFrame.Shape.HLine)
            line2.setStyleSheet(f'''background: {BORDER}; max-height: 1px;''')
            root.addWidget(line2)
            hint = QLabel('数据来源：GB/T 16823.2-1997 / 成大先机械设计手册 / 行业参考值')
            hint.setStyleSheet(f'''color: {TEXT2}; font-size: 11px;''')
            hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
            root.addWidget(hint)
            hint2 = QLabel('扫描公众号「机械领域-0-开」二维码获取解锁密码')
            hint2.setStyleSheet(f'''color: {ACCENT}; font-size: 11px;''')
            hint2.setAlignment(Qt.AlignmentFlag.AlignCenter)
            root.addWidget(hint2)
            btn = QPushButton('开始使用 →')
            btn.setFixedHeight(36)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(f'''QPushButton {{ background: {ACCENT}; color: white; border: none; border-radius: 6px; font-size: 13px; font-weight: bold; }} QPushButton:hover {{ background: {ACCENT_H}; }}''')
            btn.clicked.connect(self.accept)
            root.addWidget(btn)
            return None
    __classcell__ = None
class LockDialog:

    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle('螺栓拧紧力矩工具 — 解锁')
        self.setFixedSize(420, 480)
        self.setStyleSheet(f'''QDialog {{ background: {BG}; }}''')
        self._ok = False
        root = QVBoxLayout(self)
        root.setSpacing(10)
        root.setContentsMargins(28, 20, 28, 20)
        title = QLabel('🔒 螺栓拧紧力矩工具')
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
        hint.setStyleSheet(f'''color: {TEXT2}; font-size: 12px;''')
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
        self.pwd_input.setStyleSheet(f'''QLineEdit {{ background: {CARD}; color: {TEXT}; border: 1px solid {BORDER}; border-radius: 6px; padding: 0 12px; font-size: 13px; }} QLineEdit:focus {{ border-color: {ACCENT}; }}''')
        self.pwd_input.returnPressed.connect(self._check)
        root.addWidget(self.pwd_input)
        self.err_label = QLabel('')
        self.err_label.setStyleSheet(f'''color: {RED}; font-size: 11px;''')
        self.err_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(self.err_label)
        btn = QPushButton('🔓 解锁')
        btn.setFixedHeight(36)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(f'''QPushButton {{ background: {ACCENT}; color: white; border: none; border-radius: 6px; font-size: 13px; font-weight: bold; }} QPushButton:hover {{ background: {ACCENT_H}; }}''')
        btn.clicked.connect(self._check)
        root.addWidget(btn)
    def _check(self):
        if self.pwd_input.text().strip() == PASSWORD:
            self._ok = True
            cfg = _load_config()
            cfg['unlocked'] = True
            _save_config(cfg)
            self.accept()
            return None
        None.err_label.setText('❌ 密码错误，请关注公众号获取正确密码')
        self.pwd_input.clear()
        self.pwd_input.setFocus()
    __classcell__ = None
class DisclaimerDialog:

    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle('螺栓拧紧力矩工具 — 免责声明')
        self.setFixedSize(520, 520)
        self.setStyleSheet(f'''QDialog {{ background: {BG}; }}''')
        self._accepted = False
        root = QVBoxLayout(self)
        root.setSpacing(10)
        root.setContentsMargins(24, 16, 24, 16)
        title = QLabel('📋 工具声明')
        title.setFont(QFont('Microsoft YaHei', 15, QFont.Weight.Bold))
        title.setStyleSheet(f'''color: {TEXT};''')
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(title)
        sub = QLabel('使用本工具前，请仔细阅读以下声明')
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
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(8)
        scroll_layout.setContentsMargins(0, 4, 0, 4)
        clauses = [
            '1. 本工具提供的数据来源于公开国家标准、行业手册及厂商资料，经人工整理校对，但可能存在偏差、遗漏或版本滞后。',
            '2. 本工具仅供学习参考，不作为实际工程设计、制造、检验、采购验收的唯一依据。',
            '3. 材料力学性能与热处理状态密切相关，本工具未特别标注时均为典型值。关键参数请务必查阅最新版标准原文。',
            '4. 螺栓拧紧力矩为理论估算值，实际扭矩受摩擦系数、表面处理、润滑条件、拧紧方法等因素影响较大，重要连接请咨询专业工程师并使用校准后的扭力扳手。',
            '5. 使用者需结合实际情况和专业判断进行决策。因未经验证直接使用本工具数据而导致的工程问题，作者不承担责任。',
            '6. 本工具中引用的国家标准内容版权归原作者及发布单位所有。',
            '7. 本工具为个人学习参考用途，禁止将本工具本身进行捆绑销售、收费授权或嵌入商业系统。',
            '8. 本工具为离线工具，不收集、不上传用户的任何个人数据。']
        for clause in clauses:
            c = QLabel(clause)
            c.setWordWrap(True)
            c.setStyleSheet(f'''color: {TEXT}; font-size: 12px; padding: 6px 8px; background: {CARD}; border: 1px solid {BORDER}; border-radius: 6px;''')
            scroll_layout.addWidget(c)
            scroll_layout.addStretch()
            scroll.setWidget(scroll_widget)
            root.addWidget(scroll)
            line2 = QFrame()
            line2.setFrameShape(QFrame.Shape.HLine)
            line2.setStyleSheet(f'''background: {BORDER}; max-height: 1px;''')
            root.addWidget(line2)
            self._checkbox = QCheckBox('我已阅读并同意以上声明')
            self._checkbox.setStyleSheet(f'''color: {TEXT}; font-size: 12px; spacing: 8px;''')
            self._checkbox.stateChanged.connect(self._on_check)
            root.addWidget(self._checkbox)
            self._btn = QPushButton('✅ 同意并进入工具')
            self._btn.setFixedHeight(36)
            self._btn.setEnabled(False)
            self._btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self._btn.setStyleSheet('QPushButton { background: #555; color: #888; border: none; border-radius: 6px; font-size: 13px; font-weight: bold; }')
            self._btn.clicked.connect(self._do_accept)
            root.addWidget(self._btn)
            return None
    def _on_check(self, state):
        if state:
            self._btn.setEnabled(True)
            self._btn.setStyleSheet(f'''QPushButton {{ background: {ACCENT}; color: white; border: none; border-radius: 6px; font-size: 13px; font-weight: bold; }} QPushButton:hover {{ background: {ACCENT_H}; }}''')
            return None
        None._btn.setEnabled(False)
        self._btn.setStyleSheet('QPushButton { background: #555; color: #888; border: none; border-radius: 6px; font-size: 13px; font-weight: bold; }')
    def _do_accept(self):
        self._accepted = True
        cfg = _load_config()
        cfg['disclaimer_accepted'] = True
        _save_config(cfg)
        self.accept()
    __classcell__ = None
def is_disclaimer_accepted():
    return _load_config().get('disclaimer_accepted', False)
def main():
    app = QApplication(sys.argv)
    app.setFont(QFont('Microsoft YaHei', 10))
    app.setStyle('Fusion')
    app.setWindowIcon(QIcon(_ico_path()))
    QPalette = QPalette
    QColor = QColor
    import PySide6.QtGui
    p = QPalette()
    p.setColor(QPalette.ColorRole.Window, QColor(BG))
    p.setColor(QPalette.ColorRole.WindowText, QColor(TEXT))
    p.setColor(QPalette.ColorRole.Base, QColor(CARD))
    p.setColor(QPalette.ColorRole.Text, QColor(TEXT))
    p.setColor(QPalette.ColorRole.Button, QColor(CARD))
    p.setColor(QPalette.ColorRole.ButtonText, QColor(TEXT))
    app.setPalette(p)
    app.setStyleSheet(build_style(get_palette()))

    try:
        if is_first_run():
            w = WelcomeDialog()
            if w.exec() != QDialog.Accepted:
                return None
            cfg = None()
            cfg['first_run'] = False
            _save_config(cfg)
        if not is_unlocked():
            lock = LockDialog()
            if lock.exec() != QDialog.Accepted:
                return None
            if not None():
                disc = DisclaimerDialog()
                if disc.exec() != QDialog.Accepted:
                    return None
                MainWindow = MainWindow
                import torque_ui
                win = MainWindow()
                win.show()
                sys.exit(app.exec())
                return None
            except Exception:
                e = None
                import traceback
                err = traceback.format_exc()
                log_path = os.path.join(os.path.expanduser('~'), '.TorqueTool', 'crash.log')
                os.makedirs(os.path.dirname(log_path), exist_ok = True)
                f = open(log_path, 'w', encoding = 'utf-8')
                f.write(err)
                None(None, None)
            except:
                with None:
                    if not None:
                        pass
            QMessageBox = QMessageBox
            import PySide6.QtWidgets
            QMessageBox.critical(None, '螺栓拧紧力矩工具 - 错误', f'''启动失败，请将以下信息发给开发者：\n\n{err[-1000:]}''')
        else:
            except Exception:
                print(err)
            except:
                e = None
                del e
                return None
            e = None
            del e
            return None
        e = None
        del e
if __name__ == '__main__':
    main()
    return None
