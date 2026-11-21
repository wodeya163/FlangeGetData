__doc__ = '公差查询工具 - 启动入口'
import sys
import os
import subprocess
LOG_PATH = os.path.join(os.path.expanduser('~'), '.ToleranceTool', 'crash.log')


def _anti_debug():
    '''反调试检测：调试器附加即退出（正常打包/运行不受影响）'''
    try:
        import ctypes
        if getattr(ctypes, 'windll', None) and ctypes.windll.kernel32.IsDebuggerPresent():
            os._exit(0)
    except Exception:
        pass
    if sys.platform == 'win32':
        try:
            result = subprocess.run(['tasklist', '/FO', 'CSV', '/NH'], capture_output=True, text=True, timeout=3, creationflags=134217728)
            debuggers = ['ollydbg', 'x64dbg', 'x32dbg', 'ida', 'ida64', 'idag', 'idag64', 'immunity', 'windbg', 'processhacker', 'cheatengine', 'reclass', 'dnspy', 'de4dot']
            output = result.stdout.lower()
            for dbg in debuggers:
                if dbg in output:
                    sys.exit(0)
        except Exception:
            return


def _check_integrity():
    '''文件完整性校验'''
    if not getattr(sys, 'frozen', False):
        return
    try:
        app_path = sys.executable
        size = os.path.getsize(app_path)
        if size < 102400:
            sys.exit(0)
    except Exception:
        return


def _write_crash(err):
    '''异常落盘 crash.log（手册红线 10）'''
    try:
        os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
        with open(LOG_PATH, 'w', encoding='utf-8') as f:
            f.write(err)
    except Exception:
        return


def _install_excepthook():
    '''未捕获异常写入 crash.log（含 Qt 槽内抛出的异常）'''

    def _hook(exc_type, exc_value, exc_tb):
        import traceback
        _write_crash(''.join(traceback.format_exception(exc_type, exc_value, exc_tb)))
        sys.__excepthook__(exc_type, exc_value, exc_tb)
    sys.excepthook = _hook


_anti_debug()
_check_integrity()
_install_excepthook()
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def _run():
    from ui.main_window import run
    run()


if __name__ == '__main__':
    if len(sys.argv) >= 4 and sys.argv[1] == '--ocr-selftest':
        from ocr_query import selftest as _ocr_selftest
        sys.exit(_ocr_selftest(sys.argv[2], sys.argv[3]))
    if len(sys.argv) >= 3 and sys.argv[1] == '--overlay-selftest':
        from ocr_query import overlay_selftest as _ov_selftest
        sys.exit(_ov_selftest(sys.argv[2]))
    try:
        _run()
    except Exception:
        import traceback
        err = traceback.format_exc()
        _write_crash(err)
        try:
            from PySide6.QtWidgets import QApplication, QMessageBox
            _app = QApplication(sys.argv)
            QMessageBox.critical(None, '公差查询工具 - 启动失败', '请将以下信息发给开发者：\n\n' + err[-1000:])
        except Exception:
            pass
        sys.exit(1)
