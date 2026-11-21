"""首次欢迎 + 密码锁对话框"""
import os, json
from compat.PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QFrame, QSizePolicy, QScrollArea, QWidget,
    QCheckBox
)
from compat.PySide6.QtCore import Qt
from compat.PySide6.QtGui import QPixmap, QFont

# ─── 调色板(当前主题, 重启生效) ───
from vendor.tolerance.ui.theme import get_palette, unpack
(BG, CARD, CARD_H, BORDER, TEXT, TEXT2,
 ACCENT, GREEN, ORANGE, RED) = unpack(get_palette())
ACCENT_H = get_palette()["ACCENT_H"]

# 配置文件：始终存在用户目录，确保打包后持久化
_APP_DIR = os.path.join(os.path.expanduser('~'), '.ToleranceTool')
os.makedirs(_APP_DIR, exist_ok=True)
CONFIG_PATH = os.path.join(_APP_DIR, 'config.json')

# 二维码路径

# ─── 全局共享配置（所有工具共用） ───
_GLOBAL_CONFIG_DIR = os.path.join(os.path.expanduser('~'), '.QClaw')
os.makedirs(_GLOBAL_CONFIG_DIR, exist_ok=True)
GLOBAL_CONFIG_PATH = os.path.join(_GLOBAL_CONFIG_DIR, 'config.json')


def _load_global_config():
    if os.path.exists(GLOBAL_CONFIG_PATH):
        with open(GLOBAL_CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def _save_global_config(cfg):
    with open(GLOBAL_CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)

def _qr_path():
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, 'assets', 'qrcode.png')
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'qrcode.png')

import sys

PASSWORD = "jxly0kai"


# ───────── 免责声明对话框 ─────────
class DisclaimerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("免责声明")
        self.setFixedSize(560, 600)
        self.setStyleSheet(f"QDialog {{ background: {BG}; }}")
        self._agreed = False

        root = QVBoxLayout(self)
        root.setSpacing(10)
        root.setContentsMargins(24, 20, 24, 20)

        title = QLabel("⚖️ 免责声明")
        title.setFont(QFont("Microsoft YaHei", 16, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {ORANGE};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(title)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet(f"background: {BORDER}; max-height: 1px;")
        root.addWidget(line)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"QScrollArea {{ border: none; background: {CARD}; }}")
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(8)
        scroll_layout.setContentsMargins(12, 10, 12, 10)

        disclaimer_text = [
            "1. 本工具提供的数据来源于公开国家标准、行业手册及多家厂商资料，经人工整理校对，但可能存在偏差或遗漏。",
            "2. 本工具仅供参考学习，不作为实际工程设计、制造、检验的唯一依据。",
            "3. 使用者应结合工程实际复核计算结果；依法不能免除的责任（如人身损害）本声明不作免除。",
            "4. 使用者需自行判断数据的适用性和准确性，关键参数请务必查阅标准原文。",
            "5. 本工具严禁用于任何商业盈利目的（包括但不限于：捆绑销售、收费授权、嵌入商业系统等）。",
            "6. 材料数据可能因标准更新而变化，请以最新发布的标准原文为准。",
            "7. 本工具仅提供参数查询功能，不涉及工艺参数优化、结构设计校核等专业工程服务。",
        ]
        for text in disclaimer_text:
            lbl = QLabel(text)
            lbl.setWordWrap(True)
            lbl.setStyleSheet(f"color: {TEXT}; font-size: 12px; line-height: 1.6;")
            scroll_layout.addWidget(lbl)

        scroll.setWidget(scroll_content)
        scroll.setFixedHeight(360)
        root.addWidget(scroll)

        self.agree_box = QCheckBox("我已阅读并同意以上免责声明")
        self.agree_box.setStyleSheet(f"color: {TEXT}; font-size: 12px; padding: 4px 0;")
        root.addWidget(self.agree_box)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        btn_cancel = QPushButton("退出")
        btn_cancel.setFixedHeight(36)
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setStyleSheet(f"""
            QPushButton {{
                background: {CARD}; color: {TEXT2}; border: 1px solid {BORDER};
                border-radius: 6px; font-size: 13px;
            }}
            QPushButton:hover {{ background: {CARD_H}; }}
        """)
        btn_cancel.clicked.connect(self.reject)
        btn_row.addWidget(btn_cancel)

        btn_agree = QPushButton("同意并继续使用 →")
        btn_agree.setFixedHeight(36)
        btn_agree.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_agree.setStyleSheet(f"""
            QPushButton {{
                background: {ACCENT}; color: white; border: none;
                border-radius: 6px; font-size: 13px; font-weight: bold;
            }}
            QPushButton:hover {{ background: #5a7ae8; }}
        """)
        btn_agree.clicked.connect(self._on_agree)
        btn_row.addWidget(btn_agree)

        root.addLayout(btn_row)

    def _on_agree(self):
        if self.agree_box.isChecked():
            self._agreed = True
            self.accept()
        else:
            self.agree_box.setStyleSheet(f"color: #ff6c6c; font-size: 12px; padding: 4px 0;")

    def was_agreed(self):
        return self._agreed


def _load_config():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8-sig") as f:  # utf-8-sig 自动跳过 BOM
                return json.load(f)
        except Exception:
            pass
    return {}


def _save_config(cfg):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


def is_first_run():
    """首次运行检测（红线12: 读 first_run 字段, 缺省 True; 禁止用 not unlocked 顶替）"""
    return _load_config().get("first_run", True)


def mark_welcome_done():
    """欢迎页通过后立即落盘 first_run=False（红线12）"""
    cfg = _load_config()
    cfg["first_run"] = False
    _save_config(cfg)


def is_unlocked():
    """已解锁检测（全局共享）"""
    return _load_global_config().get("unlocked", False)


class WelcomeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("欢迎")
        self.setMinimumWidth(420)
        self.setMinimumHeight(520)

        root = QVBoxLayout(self)
        root.setSpacing(10)
        root.setContentsMargins(24, 20, 24, 20)

        # 标题
        title = QLabel("📐 公差查询工具 V2.5")
        title.setFont(QFont("Microsoft YaHei", 16, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {TEXT};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(title)

        subtitle = QLabel("孔轴配合 · 形位公差 · 表面粗糙度  一键速查")
        subtitle.setStyleSheet(f"color: {TEXT2}; font-size: 13px;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(subtitle)

        # 分割线
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet(f"background: {BORDER}; max-height: 1px;")
        root.addWidget(line)

        # 功能说明
        features = [
            ("⚙️  孔轴配合查询", "输入孔/轴代号和尺寸，自动判断间隙/过渡/过盈配合，\n显示极限偏差和最大最小间隙/过盈量"),
            ("📐  形位公差查询", "GB/T 1184-1996标准，12种形位公差类型，\n支持按等级和尺寸查询公差值"),
            ("🔩  表面粗糙度查询", "Ra↔Rz对照、加工方法×材料查询、\n37种应用场景推荐（含模具专业场景）"),
        ]
        for icon_title, desc in features:
            row = QLabel(f"  {icon_title}")
            row.setStyleSheet(f"color: {ACCENT}; font-size: 13px; font-weight: bold; padding: 6px 0 2px 0;")
            root.addWidget(row)
            for line_text in desc.split('\n'):
                d = QLabel(f"    {line_text}")
                d.setStyleSheet(f"color: {TEXT}; font-size: 12px; padding: 1px 0;")
                root.addWidget(d)

        # 分割线
        line2 = QFrame()
        line2.setFrameShape(QFrame.Shape.HLine)
        line2.setStyleSheet(f"background: {BORDER}; max-height: 1px;")
        root.addWidget(line2)

        hint = QLabel("点击「开始使用」后，请扫描公众号「机械领域-0-开」二维码获取解锁密码")
        hint.setStyleSheet(f"color: {TEXT2}; font-size: 11px;")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(hint)

        # 按钮
        btn = QPushButton("开始使用 →")
        btn.setFixedHeight(36)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: {ACCENT}; color: white; border: none;
                border-radius: 6px; font-size: 13px; font-weight: bold;
            }}
            QPushButton:hover {{ background: #5a7ae8; }}
        """)
        btn.clicked.connect(self.accept)
        root.addWidget(btn)


# ───────── 密码锁对话框 ─────────
class LockDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("公差查询工具 — 解锁")
        self.setFixedSize(420, 520)
        self.setStyleSheet(f"QDialog {{ background: {BG}; }}")
        self._ok = False

        root = QVBoxLayout(self)
        root.setSpacing(10)
        root.setContentsMargins(28, 24, 28, 20)

        # 标题
        title = QLabel("🔒 公差查询工具")
        title.setFont(QFont("Microsoft YaHei", 15, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {TEXT};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(title)

        sub = QLabel("使用前请先解锁")
        sub.setStyleSheet(f"color: {TEXT2}; font-size: 12px;")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(sub)

        # 二维码
        qr_label = QLabel()
        qr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        qr_file = _qr_path()
        if os.path.exists(qr_file):
            pixmap = QPixmap(qr_file)
            qr_label.setPixmap(pixmap.scaled(180, 180, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            qr_label.setText("[ 请将公众号二维码放到 assets/qrcode.png ]")
            qr_label.setStyleSheet(f"color: {ORANGE}; font-size: 12px;")
            qr_label.setFixedHeight(180)
        root.addWidget(qr_label)

        # 引导文字
        hint = QLabel("扫码关注公众号「机械领域-0-开」获取解锁密码\n一次解锁，后续免密使用")
        hint.setStyleSheet(f"color: {TEXT2}; font-size: 12px; line-height: 1.6;")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(hint)

        # 分割线
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet(f"background: {BORDER}; max-height: 1px;")
        root.addWidget(line)

        # 密码输入
        pwd_label = QLabel("请输入解锁密码：")
        pwd_label.setStyleSheet(f"color: {TEXT}; font-size: 12px;")
        root.addWidget(pwd_label)

        self.pwd_input = QLineEdit()
        self.pwd_input.setPlaceholderText("请输入密码…")
        self.pwd_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pwd_input.setFixedHeight(34)
        self.pwd_input.setStyleSheet(f"""
            QLineEdit {{
                background: {CARD}; color: {TEXT}; border: 1px solid {BORDER};
                border-radius: 6px; padding: 0 12px; font-size: 13px;
            }}
            QLineEdit:focus {{ border-color: {ACCENT}; }}
        """)
        self.pwd_input.returnPressed.connect(self._check_password)
        root.addWidget(self.pwd_input)

        # 错误提示
        self.err_label = QLabel("")
        self.err_label.setStyleSheet(f"color: #ff6c6c; font-size: 11px;")
        self.err_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(self.err_label)

        # 解锁按钮
        btn = QPushButton("🔓 解锁")
        btn.setFixedHeight(36)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: {ACCENT}; color: white; border: none;
                border-radius: 6px; font-size: 13px; font-weight: bold;
            }}
            QPushButton:hover {{ background: #5a7ae8; }}
        """)
        btn.clicked.connect(self._check_password)
        root.addWidget(btn)

    def _check_password(self):
        pwd = self.pwd_input.text().strip()
        if pwd == PASSWORD:
            self._ok = True
            cfg = _load_config()
            cfg["unlocked"] = True
            _save_config(cfg)
            self.accept()
        else:
            self.err_label.setText("❌ 密码错误，请关注公众号获取正确密码")
            self.pwd_input.clear()
            self.pwd_input.setFocus()

    def was_unlocked(self):
        return self._ok
