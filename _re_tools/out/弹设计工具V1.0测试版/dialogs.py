# Reconstructed from bytecode by split_decompile.py
# dialogs.relaxed.pyc

'''弹簧设计工具 - 启动三件套：欢迎 / 密码锁 / 免责声明

严格遵循开发手册第五章与 2026-10-01 新增红线：
· is_first_run() 读 first_run 字段（缺省 True），禁止用 not unlocked 顶替
· 欢迎页通过后落盘 first_run=False
· 三个对话框均校验 exec() 返回值，拒绝即退出
· 支持 SPRINGTOOL_HOME 环境变量覆盖配置目录，供测试隔离
'''
import os
import json
import sys
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QLineEdit, QFrame, QCheckBox, QScrollArea, QWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QFont
from spring_data import VERSION
import theme
_APP_DIR = os.environ.get('SPRINGTOOL_HOME') or os.path.join(os.path.expanduser('~'), '.SpringTool')
os.makedirs(_APP_DIR, exist_ok = True)
CONFIG_PATH = os.path.join(_APP_DIR, 'config.json')
PASSWORD_HASH = 'c76d09e61444b6081ad0adb484b2bb231acba4d1d46369ddd03598b936115b6e'

def _qr_path():
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, 'assets', 'qrcode.png')
    return os.path.join(os.path.dirname(__file__), 'assets', 'qrcode.png')
def load_config():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, 'r', encoding='utf-8-sig') as f:
                return json.load(f)
        except (ValueError, OSError):
            return { }
    return { }
def save_config(cfg):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok = True)
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)
_load_config = load_config
_save_config = save_config

def is_first_run():
    '''是否首次运行（读 first_run 字段，缺省 True）'''
    return load_config().get('first_run', True)
def is_unlocked():
    return load_config().get('unlocked', False)
def is_disclaimer_accepted():
    return load_config().get('disclaimer_accepted', False)
class WelcomeDialog(QDialog):

    def __init__(self, parent=None):
        t = theme.current()
        super().__init__(parent)
        self.setWindowTitle(f'''弹簧设计工具 {VERSION} — 使用说明''')
        self.setFixedSize(520, 560)
        self.setStyleSheet(f'''QDialog {{ background: {t['bg']}; }}''')
        root = QVBoxLayout(self)
        root.setSpacing(10)
        root.setContentsMargins(24, 20, 24, 20)
        title = QLabel(f'''⚙️ 弹簧设计工具 {VERSION}''')
        title.setFont(QFont('Microsoft YaHei', 16, QFont.Weight.Bold))
        title.setStyleSheet(f'''color: {t['text']};''')
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(title)
        subtitle = QLabel('压缩 / 拉伸 / 扭转圆柱螺旋弹簧设计校核')
        subtitle.setStyleSheet(f'''color: {t['text2']}; font-size: 13px;''')
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(subtitle)
        beta = QLabel('本版为测试版，数据来自 GB/T 23935-2009；重要场合请以所选材料标准复核')
        beta.setStyleSheet(f'''color: {t['text2']}; font-size: 11px;''')
        beta.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(beta)
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet(f'''background: {t['border']}; max-height: 1px;''')
        root.addWidget(line)
        features = [
            ('🔩  压缩弹簧', '给定最大载荷与行程，选材料、算线径/中径/有效圈数，\n校核切应力、稳定性与疲劳安全系数'),
            ('🔗  拉伸弹簧', '校核切应力与变形量；初拉力 F0 与钩环处\n应力集中未计入，需按标准另行校核'),
            ('🔧  扭转弹簧', '给定扭矩，校核弯曲应力与有效圈数'),
            ('📐  辅助参考', '按 GB/T 23935-2009 推荐旋绕比、材料 Rm 下限值，\n结果给出选用方案与风险提示')]
        for icon_title, desc in features:
            row = QLabel(f'''  {icon_title}''')
            row.setStyleSheet(f'''color: {t['accent']}; font-size: 13px; font-weight: bold; padding: 6px 0 2px 0;''')
            root.addWidget(row)
            for line_text in desc.split('\n'):
                d = QLabel(f'''    {line_text}''')
                d.setStyleSheet(f'''color: {t['text']}; font-size: 12px; padding: 1px 0;''')
                root.addWidget(d)
        line2 = QFrame()
        line2.setFrameShape(QFrame.Shape.HLine)
        line2.setStyleSheet(f'''background: {t['border']}; max-height: 1px;''')
        root.addWidget(line2)
        hint = QLabel('点击「开始使用」后，请扫描公众号「机械领域-0-开」二维码获取解锁密码')
        hint.setStyleSheet(f'''color: {t['text2']}; font-size: 11px;''')
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(hint)
        btn = QPushButton('开始使用 →')
        btn.setFixedHeight(36)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(f'''\n            QPushButton {{ background: {t['accent']}; color: {t['accent_text']}; border: none;\n                border-radius: 6px; font-size: 13px; font-weight: bold; }}\n            QPushButton:hover {{ background: {t['accent_hover']}; }}\n        ''')
        btn.clicked.connect(self.accept)
        root.addWidget(btn)
        return None
class LockDialog(QDialog):

    def __init__(self, parent=None):
        t = theme.current()
        super().__init__(parent)
        self.setWindowTitle(f'''弹簧设计工具 {VERSION} — 解锁''')
        self.setFixedSize(420, 520)
        self.setStyleSheet(f'''QDialog {{ background: {t['bg']}; }}''')
        self._ok = False
        root = QVBoxLayout(self)
        root.setSpacing(10)
        root.setContentsMargins(28, 24, 28, 20)
        title = QLabel('🔒 弹簧设计工具')
        title.setFont(QFont('Microsoft YaHei', 15, QFont.Weight.Bold))
        title.setStyleSheet(f'''color: {t['text']};''')
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(title)
        sub = QLabel('使用前请先解锁')
        sub.setStyleSheet(f'''color: {t['text2']}; font-size: 12px;''')
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(sub)
        qr_label = QLabel()
        qr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        qr_file = _qr_path()
        if os.path.exists(qr_file):
            pix = QPixmap(qr_file).scaled(180, 180, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            qr_label.setPixmap(pix)
        else:
            qr_label.setText('[ 请将公众号二维码放到 assets/qrcode.png ]')
            qr_label.setStyleSheet(f'''color: {t['orange']}; font-size: 12px;''')
            qr_label.setFixedHeight(180)
        root.addWidget(qr_label)
        hint = QLabel('扫码关注公众号「机械领域-0-开」获取解锁密码\n解锁后本机不再重复要求输入（换电脑或清除配置后需重新解锁）')
        hint.setStyleSheet(f'''color: {t['text2']}; font-size: 12px; line-height: 1.6;''')
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(hint)
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet(f'''background: {t['border']}; max-height: 1px;''')
        root.addWidget(line)
        pwd_label = QLabel('请输入解锁密码：')
        pwd_label.setStyleSheet(f'''color: {t['text']}; font-size: 12px;''')
        root.addWidget(pwd_label)
        self.pwd_input = QLineEdit()
        self.pwd_input.setPlaceholderText('请输入密码…')
        self.pwd_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pwd_input.setFixedHeight(34)
        self.pwd_input.setStyleSheet(f'''\n            QLineEdit {{ background: {t['card']}; color: {t['text']}; border: 1px solid {t['border']};\n                border-radius: 6px; padding: 0 12px; font-size: 13px; }}\n            QLineEdit:focus {{ border-color: {t['accent']}; }}\n        ''')
        self.pwd_input.returnPressed.connect(self._check_password)
        root.addWidget(self.pwd_input)
        self.err_label = QLabel('')
        self.err_label.setStyleSheet(f'''color: {t['red']}; font-size: 11px;''')
        self.err_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(self.err_label)
        btn = QPushButton('🔓 解锁')
        btn.setFixedHeight(36)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(f'''\n            QPushButton {{ background: {t['accent']}; color: {t['accent_text']}; border: none;\n                border-radius: 6px; font-size: 13px; font-weight: bold; }}\n            QPushButton:hover {{ background: {t['accent_hover']}; }}\n        ''')
        btn.clicked.connect(self._check_password)
        root.addWidget(btn)
    def _check_password(self):
        import hashlib
        pwd = self.pwd_input.text().strip()
        if hashlib.sha256(pwd.encode()).hexdigest() == PASSWORD_HASH:
            self._ok = True
            cfg = load_config()
            cfg['unlocked'] = True
            save_config(cfg)
            self.accept()
            return None
        self.err_label.setText('❌ 密码错误，请关注公众号获取正确密码')
        self.pwd_input.clear()
        self.pwd_input.setFocus()
    def was_unlocked(self):
        return self._ok
class DisclaimerDialog(QDialog):

    def __init__(self, parent=None):
        t = theme.current()
        super().__init__(parent)
        self.setWindowTitle(f'''弹簧设计工具 {VERSION} — 免责声明''')
        self.setFixedSize(540, 560)
        self.setStyleSheet(f'''QDialog {{ background: {t['bg']}; }}''')
        self._accepted = False
        root = QVBoxLayout(self)
        root.setSpacing(10)
        root.setContentsMargins(24, 18, 24, 18)
        title = QLabel('📋 工具声明')
        title.setFont(QFont('Microsoft YaHei', 15, QFont.Weight.Bold))
        title.setStyleSheet(f'''color: {t['text']};''')
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(title)
        sub = QLabel('使用本工具前，请先阅读以下声明')
        sub.setStyleSheet(f'''color: {t['text2']}; font-size: 12px;''')
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(sub)
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet(f'''background: {t['border']}; max-height: 1px;''')
        root.addWidget(line)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet('QScrollArea { border: none; background: transparent; }')
        holder = QWidget()
        hold = QVBoxLayout(holder)
        hold.setSpacing(8)
        hold.setContentsMargins(0, 4, 0, 4)
        clauses = [
            '1. 本工具数据整理自 GB/T 23935-2009《圆柱螺旋弹簧设计计算》及引用的材料标准，仅录入数值与标准号，不复制标准原文。',
            '2. 工具按标准推荐公式进行估算，设计结果仅供参考；关键参数与许用应力请以所选材料标准的现行有效版本复核。',
            '3. 弹簧实际性能受加工工艺、热处理、表面质量、疲劳载荷谱及工作环境影响，本工具计算结果不能替代实际试验或正式设计文件。',
            '4. 动负荷与疲劳计算采用标准给出的经验系数与范围值，属于近似估算；重要用途弹簧建议做疲劳试验或咨询专业厂家。',
            '5. 本工具引用的国家标准内容版权归原作者及发布单位所有；本工具限个人学习参考，禁止捆绑销售、收费授权或嵌入商业系统。',
            '6. 本工具为离线工具，不收集、不上传用户的任何个人数据。']
        for clause in clauses:
            c = QLabel(clause)
            c.setWordWrap(True)
            c.setStyleSheet(f'''color: {t['text']}; font-size: 12px; padding: 6px 8px; background: {t['card']}; border: 1px solid {t['border']}; border-radius: 6px;''')
            hold.addWidget(c)
        hold.addStretch()
        scroll.setWidget(holder)
        root.addWidget(scroll)
        line2 = QFrame()
        line2.setFrameShape(QFrame.Shape.HLine)
        line2.setStyleSheet(f'''background: {t['border']}; max-height: 1px;''')
        root.addWidget(line2)
        self.chk = QCheckBox('我已阅读并同意以上声明')
        self.chk.setStyleSheet(f'''color: {t['text']}; font-size: 12px; spacing: 8px;''')
        self.chk.stateChanged.connect(self._on_check)
        root.addWidget(self.chk)
        self.btn = QPushButton('同意并进入工具')
        self.btn.setFixedHeight(36)
        self.btn.setEnabled(False)
        self.btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn.setStyleSheet(f'''QPushButton {{ background: {t['disabled_bg']}; color: {t['disabled_text']}; border: none; border-radius: 6px; font-size: 13px; font-weight: bold; }}''')
        self.btn.clicked.connect(self._do_accept)
        root.addWidget(self.btn)
        return None
    def _on_check(self, state):
        t = theme.current()
        if state:
            self.btn.setEnabled(True)
            self.btn.setStyleSheet(f'''QPushButton {{ background: {t['accent']}; color: {t['accent_text']}; border: none; border-radius: 6px; font-size: 13px; font-weight: bold; }}QPushButton:hover {{ background: {t['accent_hover']}; }}''')
            return None
        self.btn.setEnabled(False)
        self.btn.setStyleSheet(f'''QPushButton {{ background: {t['disabled_bg']}; color: {t['disabled_text']}; border: none; border-radius: 6px; font-size: 13px; font-weight: bold; }}''')
    def _do_accept(self):
        self._accepted = True
        cfg = load_config()
        cfg['disclaimer_accepted'] = True
        save_config(cfg)
        self.accept()
    def was_accepted(self):
        return self._accepted

