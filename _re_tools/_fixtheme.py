import io
p = r"_decompiled_tools\密封圈选型工具V2.5\source\theme.py"
s = io.open(p, encoding="utf-8").read()

s = s.replace("""def current_name():
    if _current in THEMES:
        return _current""", """def current_name():
    if _current in THEMES:
        return _current
    return DEFAULT""")

s = s.replace("""    for modname in None:
        mod = sys.modules.get(modname)
        p = getattr(mod, 'CONF_FILE', None)
        if p:
            return p
        return os.path.join(os.path.expanduser('~'), '.SealTool', 'config.json')""",
"""    for modname in ('app', '__main__'):
        mod = sys.modules.get(modname)
        p = getattr(mod, 'CONF_FILE', None)
        if p:
            return p
    return os.path.join(os.path.expanduser('~'), '.SealTool', 'config.json')""")

s = s.replace("""def load_saved():
    '''读出已保存的主题名；文件不存在或主题名失效时返回 None。'''
    pass
# WARNING: Decompyle incomplete
""", """def load_saved():
    '''读出已保存的主题名；文件不存在或主题名失效时返回 None。'''
    try:
        import json
        with open(_config_path(), 'r', encoding='utf-8-sig') as f:
            cfg = json.load(f)
    except (OSError, ValueError):
        return None
    name = cfg.get('theme')
    if is_valid(name):
        return name
    return None

""")

s = s.replace("""    path = None()
    cfg = { }
# WARNING: Decompyle incomplete
""", """    path = _config_path()
    cfg = { }
    try:
        with open(path, 'r', encoding='utf-8-sig') as f:
            cfg = json.load(f)
    except (OSError, ValueError):
        cfg = { }
    cfg['theme'] = name
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(cfg, ensure_ascii=False, indent=2, fp=f)
    except OSError:
        return False
    return True

""")

s = s.replace("""    _current = None
    save(name)
    return True""", """    _current = name
    save(name)
    return True""")

s = s.replace("""    global _current, _current
    saved = load_saved()
    if saved:
        _current = saved
        return _current
    _current = None
    return _current""", """    global _current
    saved = load_saved()
    if saved:
        _current = saved
        return _current
    _current = DEFAULT
    return _current""")

io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("ok")
