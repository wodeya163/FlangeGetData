import io
p = r"_decompiled_tools\密封圈选型工具V2.5\source\app.py"
s = io.open(p, encoding="utf-8").read()
s = s.replace("        None._btn.setEnabled(False)", "        self._btn.setEnabled(False)")
if "__main__" not in s:
    s = s.rstrip("\n") + """

if __name__ == '__main__':
    if debugger_present():
        sys.exit(0)
    try:
        run()
    except Exception:
        import traceback
        err = traceback.format_exc()
        log_path = os.path.join(os.path.expanduser('~'), '.SealTool', 'crash.log')
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write(err)
        try:
            QMessageBox.critical(None, '密封圈选型工具 - 启动失败', '程序启动失败，请退出后重试；\\n如反复出现，可在公众号评论区反馈。')
        except Exception:
            pass
        sys.exit(1)
"""
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("ok")
