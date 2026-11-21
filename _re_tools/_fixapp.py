import io
p = r"_decompiled_tools\密封圈选型工具V2.5\source\app.py"
s = io.open(p, encoding="utf-8").read()

old = """def _load_config():
    os.makedirs(CONF_DIR, exist_ok=True)
# WARNING: Decompyle incomplete
def _save_config(cfg):
    os.makedirs(CONF_DIR, exist_ok=True)
    with open(CONF_FILE, 'w', encoding='utf-8') as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)
        None(None, None, None)
        return None
        with None:
            if not None:
                pass
def _qr_path():
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, 'assets', 'qrcode.jpg')
    return None.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'qrcode.jpg')
"""
new = """def _load_config():
    os.makedirs(CONF_DIR, exist_ok=True)
    if os.path.exists(CONF_FILE):
        try:
            with open(CONF_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {'first_run': True, 'unlocked': False}

def _save_config(cfg):
    os.makedirs(CONF_DIR, exist_ok=True)
    with open(CONF_FILE, 'w', encoding='utf-8') as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)

def _qr_path():
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, 'assets', 'qrcode.jpg')
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'qrcode.jpg')
"""
assert old in s
s = s.replace(old, new)

s = s.replace("class WelcomeDialog:\n\n    def __init__(self, parent):", "class WelcomeDialog(QDialog):\n\n    def __init__(self, parent=None):")
s = s.replace("class LockDialog:\n\n    def __init__(self, parent):", "class LockDialog(QDialog):\n\n    def __init__(self, parent=None):")
s = s.replace("class DisclaimerDialog:\n\n    def __init__(self, parent):", "class DisclaimerDialog(QDialog):\n\n    def __init__(self, parent=None):")

s = s.replace("""        None.err_label.setText('❌ 密码错误，请关注公众号获取正确密码')""",
              """        self.err_label.setText('❌ 密码错误，请关注公众号获取正确密码')""")

s = s.replace("""def debugger_present():
    '''反调试：检测到调试器附加则返回 True（静默退出，不做任何提示）。'''
    pass
# WARNING: Decompyle incomplete
""", """def debugger_present():
    '''反调试：检测到调试器附加则返回 True（静默退出，不做任何提示）。'''
    try:
        return bool(ctypes.windll.kernel32.IsDebuggerPresent())
    except Exception:
        return False

""")

old_run_start = s.index("def run():")
s = s[:old_run_start] + """def run():
    app = QApplication(sys.argv)

    import theme
    theme.init_from_config()
    from seal_ui import setup_theme
    setup_theme(app)

    cfg = _load_config()

    if cfg.get('first_run', True):
        welcome = WelcomeDialog()
        if welcome.exec() != QDialog.DialogCode.Accepted:
            return None
        cfg['first_run'] = False
        _save_config(cfg)
        cfg = _load_config()

    if not cfg.get('unlocked', False):
        lock = LockDialog()
        if lock.exec() != QDialog.DialogCode.Accepted:
            return None
        cfg = _load_config()

    if not cfg.get('usage_guide_accepted', False):
        guide = DisclaimerDialog()
        if guide.exec() != QDialog.DialogCode.Accepted:
            return None

    from seal_ui import MainWindow
    win = MainWindow()
    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'seal.ico')
    if os.path.exists(icon_path):
        win.setWindowIcon(QIcon(icon_path))
    win.show()
    sys.exit(app.exec())
"""

s = s.replace("    __classcell__ = None\n", "")
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("done")
