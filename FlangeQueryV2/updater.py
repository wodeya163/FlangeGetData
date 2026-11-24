# -*- coding: utf-8 -*-
"""半自动更新核心模块（纯标准库 + PyQt5，兼容 PyInstaller onedir）。

设计要点
--------
- 只在启动时做一次静默检查（也可在「关于」框手动触发），不收集任何用户数据。
- 联网失败静默（仅记日志），不弹错。
- 更新为「半自动」：检查到新版 → 弹窗询问 → 用户确认 → 后台下载 + 校验 →
  写入 _apply_update.bat 并退出程序，由 bat 在旧进程退出后覆盖文件、再启动新版本。
- 仅支持「文件夹版（onedir）」自更新；单文件版（onefile）运行中被锁，不支持自更新。

部署切换
--------
- 支持三类更新源，按优先级自动选：GITEE_REPO → GITHUB_REPO → UPDATE_BASE_URL(http/file)。
  1) Gitee 码云 Releases（国内稳，公开免鉴权）：把 GITEE_REPO 设为 'owner/repo'，
     或用环境变量 FLANGE_GITEE_REPO 指定。updater 通过 Gitee API 取最新 release 的
     assets（兼容其 download_url 字段），无需固定 URL、不受 tag 变化影响。发布脚本用
     Gitee API（私人令牌 FLANGE_GITEE_TOKEN）创建 release 并上传 version.json + folder zip。
  2) GitHub Releases（公开免鉴权）：GITEE_REPO 留空、GITHUB_REPO 设为 'owner/repo'
     时启用。结构与 Gitee 分支共用同一套 assets 解析逻辑。
  3) 通用 http(s)/file 直链：两者都留空时回退，用 UPDATE_BASE_URL 指向的地址下放
     version.json 与 folder zip（本机联调默认走这条）。
- WorkBuddy 云存储不适用：其 Storage 仅供 WorkBuddy 在线应用运行时经 SDK/OAuth 访问，
  并非面向任意客户端可免鉴权拉的公开静态分发源，无法给桌面 exe 当更新源。
- 消费级网盘（百度/阿里/微云/OneDrive）给不了稳定免鉴权直链，不适合做自动更新源；
  若只能用手动更新，请把最新 folder zip 放到网盘分享，并在「关于」框告知用户下载地址。
"""
import hashlib
import json
import logging
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
import zipfile

from PyQt5.QtCore import QThread, pyqtSignal

# ----------------------------- 配置 -----------------------------
UPDATE_BASE_URL = os.environ.get(
    'FLANGE_UPDATE_BASE',
    'file:///E:/AI作品/work/FlangeGetData/发布')   # 默认本地模拟；真实部署改 http(s)
# Releases 源（Gitee 优先，其次 GitHub，最后回退 http/file）。
# 设为 'owner/repo' 即启用对应源；也可通过环境变量覆盖（便于分发给不同仓库）。
GITEE_REPO = os.environ.get('FLANGE_GITEE_REPO', '')       # 备用：设为 owner/repo 可切回 Gitee
GITHUB_REPO = os.environ.get('FLANGE_GITHUB_REPO', 'wodeya163/FlangeGetData')  # 默认更新源
GITHUB_API = 'https://api.github.com'
GITEE_API = 'https://gitee.com/api/v5'
UPDATE_DISABLED = os.environ.get('FLANGE_NO_UPDATE', '0') == '1'
APPLY_DRY_RUN = os.environ.get('FLANGE_UPDATE_DRYRUN', '0') == '1'
USER_AGENT = 'FlangeQuery-Updater/1.0'
log = logging.getLogger('flangequery.updater')


# --------------------------- 版本解析 ---------------------------
def parse_version(v):
    """'V3.78.0' / '3.78.0' / '3.79' -> (major, minor, patch) 元组，便于比较。"""
    if not v:
        return (0, 0, 0)
    s = str(v).lstrip('vV').strip()
    parts = re.split(r'[.\-]', s)
    out = []
    for p in parts[:3]:
        m = re.match(r'\d+', p)
        out.append(int(m.group()) if m else 0)
    while len(out) < 3:
        out.append(0)
    return tuple(out)


def read_local_version(version_py=None):
    """从 version.py 读取 APP_VERSION（正则，不 import，避免循环依赖）。"""
    if version_py is None:
        version_py = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 'version.py')
    try:
        with open(version_py, encoding='utf-8') as fh:
            txt = fh.read()
        m = re.search(r"APP_VERSION\s*=\s*['\"]([^'\"]+)['\"]", txt)
        if m:
            return m.group(1)
    except OSError:
        pass
    return '0.0.0'


def normalize_base(url):
    return (url or '').rstrip('/')


def is_onefile():
    """PyInstaller 单文件版：运行时解压目录在 %TEMP%，与 exe 目录不同。"""
    if not getattr(sys, 'frozen', False):
        return False
    meipass = getattr(sys, '_MEIPASS', None)
    if not meipass:
        return False
    exe_dir = os.path.dirname(os.path.abspath(sys.executable))
    return os.path.normcase(os.path.abspath(meipass)) != os.path.normcase(exe_dir)


def _read_url(req, timeout=60):
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def _retry(fn, what, attempts=3):
    """网络抖动重试：只重试连接类错误，HTTP 错误（404/403）直接抛出。"""
    last = None
    for i in range(attempts):
        try:
            return fn()
        except urllib.error.HTTPError:
            raise
        except Exception as e:
            last = e
            if i + 1 < attempts:
                wait = 1.5 * (2 ** i)
                log.warning('%s 失败（第 %d/%d 次）：%s；%.1fs 后重试',
                            what, i + 1, attempts, e, wait)
                time.sleep(wait)
    log.error('%s 失败（已重试 %d 次）：%s', what, attempts, last)
    raise last


def _local_path_of(url):
    if url.startswith('file://'):
        return urllib.request.url2pathname(url[len('file://'):])
    return None


# --------------------------- Releases 源（GitHub / Gitee 通用） ---------------------------
def _releases_headers(token, accept='application/json'):
    h = {'User-Agent': USER_AGENT, 'Accept': accept}
    if token:
        h['Authorization'] = 'Bearer ' + token
    return h


def _asset_item(assets, suffix):
    """按文件名后缀匹配资产（返回资产 dict）。"""
    for a in assets or []:
        if a.get('name', '').endswith(suffix):
            return a
    return None


def _asset_urls(asset, prefer='api'):
    """资产的候选下载地址 [(url, headers, timeout)]。

    - API 端点会 302 到 release-assets.githubusercontent.com，国内可通但速度偏慢；
    - 原 browser 地址（github.com/.../releases/download）快，但常被重置。
    小文件（version.json）API 优先；大包直连优先，失败再走 API。"""
    if not asset:
        return []
    api = asset.get('_api_url')
    direct = asset.get('browser_download_url') or asset.get('download_url')
    api_item = ((api, {'User-Agent': USER_AGENT,
                       'Accept': 'application/octet-stream'}, 120) if api else None)
    direct_item = ((direct, {'User-Agent': USER_AGENT}, 30) if direct else None)
    order = (api_item, direct_item) if prefer == 'api' else (direct_item, api_item)
    return [x for x in order if x]


def _asset_url(assets, suffix):
    urls = _asset_urls(_asset_item(assets, suffix))
    return urls[0][0] if urls else None


def _info_from_release(rel, assets):
    """version.json 下载失败时的降级：tag 当版本，notes 取 release body，
    SHA256 取 GitHub 的 asset digest。"""
    def meta(a):
        if not a:
            return None
        digest = str(a.get('digest') or '')
        sha = digest.split(':', 1)[1] if digest.startswith('sha256:') else None
        return {'name': a.get('name'), 'size': a.get('size'), 'sha256': sha}

    info = {'latest': str(rel.get('tag_name', '')).lstrip('vV') or None,
            'notes': rel.get('body', ''), 'files': {}}
    for key, suffix in (('folder', '-folder.zip'), ('onefile', '-onefile.exe')):
        m = meta(_asset_item(assets, suffix))
        if m:
            info['files'][key] = m
    return info


def github_latest_release(repo):
    """拉取 latest release（公开仓库免 token；私有仓库需 FLANGE_GITHUB_TOKEN）。"""
    tok = os.environ.get('FLANGE_GITHUB_TOKEN')
    url = '%s/repos/%s/releases/latest' % (GITHUB_API, repo)

    def _get():
        req = urllib.request.Request(url, headers=_releases_headers(tok))
        return json.loads(_read_url(req).decode('utf-8'))

    log.info('读取 GitHub 最新 Release：%s', repo)
    rel = _retry(_get, '读取 GitHub Release')
    for a in rel.get('assets') or []:
        if a.get('id'):
            a['_api_url'] = '%s/repos/%s/releases/assets/%d' % (
                GITHUB_API, repo, a['id'])
    return rel


def gitee_latest_release(repo):
    """Gitee 无 /latest 端点，且列表排序不保证最新在前。2026-11-22 实测当前
    仓库 id 最大的 release 竟是临时测试 tag（v0.0.0-split-test），按 id 取会
    误选中它并让客户端误报“已是最新”。改为按 tag 的语义版本取最大，并排除
    prerelease；公开仓库可免 token（限流较严），设 FLANGE_GITEE_TOKEN 提升稳定性。"""
    tok = os.environ.get('FLANGE_GITEE_TOKEN')
    url = '%s/repos/%s/releases?per_page=20' % (GITEE_API, repo)
    if tok:
        url += '&access_token=' + tok
    req = urllib.request.Request(url, headers=_releases_headers(tok))
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode('utf-8'))
    if isinstance(data, list) and data:
        # (is_stable, major, minor, patch)：测试/预发布 tag 永远排在正式版之后
        return max(data, key=lambda x: (
            0 if x.get('prerelease') else 1,
        ) + parse_version(x.get('tag_name')))
    raise RuntimeError('Gitee 仓库 %s 暂无 release' % repo)


# --------------------------- 网络/文件 ---------------------------
def fetch_bytes(url):
    """读取字节；支持 http(s) 与 file://。"""
    lp = _local_path_of(url)
    if lp is not None:
        with open(lp, 'rb') as f:
            return f.read()
    def _get():
        req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
        return _read_url(req)

    return _retry(_get, '读取 %s' % url)


def _fetch_asset(asset):
    """下载小资产（如 version.json），API 端点失败时自动换原地址。"""
    last = None
    for url, headers, timeout in _asset_urls(asset, 'api'):
        def _get(u=url, h=headers, t=timeout):
            return _read_url(urllib.request.Request(u, headers=h), timeout=t)

        try:
            return _retry(_get, '下载 %s' % asset.get('name'), attempts=2)
        except Exception as e:
            last = e
            log.warning('下载地址失败（%s）：%s', url, e)
    raise last or RuntimeError('资产没有可用下载地址')


def fetch_version_info(base=None, repo=None, source=None):
    """取版本清单。source 可显式指定 'gitee'/'github'/'http'；
    不指定则按 GITEE_REPO → GITHUB_REPO → http 优先级自动选。

    返回 dict 含 latest（最新版本号）、files.folder（含 sha256）、
    _release.assets（用于解析 folder zip 直链）。"""
    if source is None:
        source = 'gitee' if GITEE_REPO else ('github' if GITHUB_REPO else 'http')
    if source in ('gitee', 'github'):
        try:
            rel = (gitee_latest_release(GITEE_REPO) if source == 'gitee'
                   else github_latest_release(GITHUB_REPO))
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return {'latest': None, 'files': {}}   # 仓库/Release 尚未建立
            raise
        assets = rel.get('assets') or []
        # 发布完整性校验：Releases 源必须带 folder zip。缺包时若继续走后面的
        # files.folder.url 分支，会错误回退到本机开发用的 file:// 发布目录，
        # 在用户机器上表现为“下载失败”，在开发机上则因 SHA 不符而失败——
        # 两种情况都掩盖了真正原因。2026-11-22 实测 v3.78.1 即缺该资产。
        folder_asset = _asset_url(assets, '-folder.zip')
        onefile_asset = _asset_url(assets, '-onefile.exe')
        if not folder_asset and not onefile_asset:
            raise RuntimeError(
                '发布源(%s) 最新 release %s 缺少更新包（*-folder.zip 或 '
                '*-onefile.exe），请先在 Gitee/GitHub Release 上传完整包'
                % (source, rel.get('tag_name')))
        if is_onefile() and not onefile_asset:
            raise RuntimeError(
                '当前为单文件版，但发布源(%s) 最新 release %s 没有 '
                '*-onefile.exe；请补传单文件包，或改用文件夹版'
                % (source, rel.get('tag_name')))
        vj = next((a for a in assets if a.get('name') == 'version.json'), None)
        info = None
        if vj:
            try:
                info = json.loads(_fetch_asset(vj).decode('utf-8'))
            except Exception as e:
                log.warning('version.json 资产读取失败，改用 Release 元数据：%s', e)
        if info is None:
            info = _info_from_release(rel, assets)
        info['_release'] = {'tag': rel.get('tag_name'), 'assets': assets}
        return info
    base = normalize_base(base or UPDATE_BASE_URL)
    raw = fetch_bytes(base + '/version.json')
    return json.loads(raw.decode('utf-8'))


def need_update(local_version, info):
    latest = info.get('latest') if isinstance(info, dict) else None
    if not latest:
        return False
    return parse_version(latest) > parse_version(local_version)


def _download_to(url, headers, dest, progress_cb=None, timeout=120):
    lp = _local_path_of(url)
    if lp is not None:
        shutil.copyfile(lp, dest)
        if progress_cb:
            progress_cb(100, 100)
        return dest

    def _get():
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout) as resp, open(dest, 'wb') as out:
            total = int(resp.headers.get('Content-Length', '0') or 0)
            got = 0
            while True:
                chunk = resp.read(65536)
                if not chunk:
                    break
                out.write(chunk)
                got += len(chunk)
                if progress_cb and total:
                    progress_cb(got, total)
        return dest

    log.info('下载：%s', url)
    return _retry(_get, '下载')


def download(url, dest, progress_cb=None):
    """支持 http(s) 与 file://；file:// 直接拷贝，http 流式写并回调进度。"""
    return _download_to(url, {'User-Agent': USER_AGENT}, dest, progress_cb)


def _download_asset(asset, dest, progress_cb=None):
    """下载大资产（folder zip / onefile exe）：直连优先，API 兜底。"""
    last = None
    for url, headers, timeout in _asset_urls(asset, 'direct'):
        try:
            return _download_to(url, headers, dest, progress_cb, timeout)
        except Exception as e:
            last = e
            log.warning('下载地址失败（%s）：%s', url, e)
    raise last or RuntimeError('资产没有可用下载地址')



def sha256_of(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for c in iter(lambda: f.read(65536), b''):
            h.update(c)
    return h.hexdigest()


def verify_sha256(path, expected):
    if not expected:
        return True
    try:
        return sha256_of(path).lower() == str(expected).lower()
    except OSError:
        return False


def _resolve_folder_url(info, base):
    # Releases 模式（gitee/github 通用）：直接从最新 release assets 取 folder zip 下载地址；
    # 禁止回退到本机 file:// 发布目录（见 fetch_version_info 的完整性校验）。
    rel = info.get('_release') if isinstance(info, dict) else None
    if isinstance(rel, dict):
        return _asset_url(rel.get('assets', []), '-folder.zip')
    # http/file 模式：从 version.json 的 files.folder.url 取
    f = info.get('files', {}).get('folder')
    if not isinstance(f, dict):
        f = {'url': info.get('url')}
    url = f.get('url')
    if not url:
        return None
    if url.startswith(('http://', 'https://', 'file://')):
        return url
    return normalize_base(base) + '/' + url.lstrip('/')


def _resolve_onefile_url(info, base):
    """单文件版更新包地址：优先 Release assets，其次 version.json 的 files.onefile。"""
    rel = info.get('_release') if isinstance(info, dict) else None
    if isinstance(rel, dict):
        return _asset_url(rel.get('assets', []), '-onefile.exe')
    f = info.get('files', {}).get('onefile')
    if isinstance(f, dict):
        url = f.get('url')
        if url:
            if url.startswith(('http://', 'https://', 'file://')):
                return url
            return normalize_base(base) + '/' + url.lstrip('/')
    return None


def download_onefile(info, base=None, progress_cb=None):
    """下载单文件版新 exe 并校验 SHA256，返回临时文件路径。"""
    base = normalize_base(base or UPDATE_BASE_URL)
    rel = info.get('_release') if isinstance(info, dict) else None
    asset = (_asset_item(rel.get('assets', []), '-onefile.exe')
             if isinstance(rel, dict) else None)
    meta = info.get('files', {}).get('onefile') or {}
    tmp = tempfile.mkdtemp(prefix='flange_upd_')
    exe_path = os.path.join(tmp, 'FlangeQueryV2.new.exe')
    if asset:
        _download_asset(asset, exe_path, progress_cb)
    else:
        url = _resolve_onefile_url(info, base)
        if not url:
            raise ValueError('version.json 缺少单文件版下载地址')
        download(url, exe_path, progress_cb)
    if not verify_sha256(exe_path, meta.get('sha256')):
        raise ValueError('单文件版 SHA256 校验失败，可能损坏或被篡改')
    return exe_path


def download_and_extract(local_version, info, base=None, tmp_root=None,
                         progress_cb=None):
    """下载 folder zip → 校验 SHA256 → 解压，返回 new_dir（解压根）。异常向上抛。"""
    base = normalize_base(base or UPDATE_BASE_URL)
    rel = info.get('_release') if isinstance(info, dict) else None
    asset = (_asset_item(rel.get('assets', []), '-folder.zip')
             if isinstance(rel, dict) else None)
    expected = (info.get('files', {}).get('folder') or {}).get('sha256')
    tmp = tempfile.mkdtemp(prefix='flange_upd_', dir=tmp_root)
    zip_path = os.path.join(tmp, 'folder.zip')
    if asset:
        _download_asset(asset, zip_path, progress_cb)
    else:
        url = _resolve_folder_url(info, base)
        if not url:
            raise ValueError('version.json 缺少 folder 下载地址')
        log.info('下载文件夹版更新包：%s', url)
        download(url, zip_path, progress_cb)
    if not verify_sha256(zip_path, expected):
        raise ValueError('下载文件 SHA256 校验失败，可能损坏或被篡改')
    new_dir = os.path.join(tmp, 'new')
    os.makedirs(new_dir, exist_ok=True)
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(new_dir)
    log.info('更新包校验通过并已解压：%s', new_dir)
    return new_dir


def build_apply_bat(prog_dir, new_dir, exe_name, pid):
    """生成 _apply_update.bat：等待旧进程退出 → robocopy 覆盖 → 启动新版本。"""
    bat = os.path.join(prog_dir, '_apply_update.bat')
    content = (
        '@echo off\r\n'
        'set "PROG=%~1"\r\n'
        'set "NEW=%~2"\r\n'
        'set "EXE=%~3"\r\n'
        'set "PID=%~4"\r\n'
        ':wait\r\n'
        'tasklist /FI "PID eq %PID%" | find "%PID%" >nul\r\n'
        'if %errorlevel%==0 (timeout /t 1 /nobreak >nul & goto wait)\r\n'
        'robocopy "%NEW%" "%PROG%" /E /IS /IT /NFL /NDL /NJH /NJS\r\n'
        'if exist "%PROG%\\%EXE%" start "" "%PROG%\\%EXE%"\r\n'
    )
    # Windows cmd 默认 gbk；路径均为英文，gbk 写最稳妥
    with open(bat, 'w', encoding='gbk', newline='') as f:
        f.write(content)
    return bat


def build_apply_exe_bat(prog_dir, new_exe, exe_name, pid):
    """单文件版：等待旧进程退出 → 覆盖 exe → 启动。bootloader 父进程会晚些释放文件，
    因此退出后额外等待 2 秒，并对 copy 做最多 5 次重试。"""
    bat = os.path.join(prog_dir, '_apply_update.bat')
    content = (
        '@echo off\r\n'
        'set "PROG=%~1"\r\n'
        'set "NEW=%~2"\r\n'
        'set "EXE=%~3"\r\n'
        'set "PID=%~4"\r\n'
        ':wait\r\n'
        'tasklist /FI "PID eq %PID%" | find "%PID%" >nul\r\n'
        'if %errorlevel%==0 (timeout /t 1 /nobreak >nul & goto wait)\r\n'
        'timeout /t 2 /nobreak >nul\r\n'
        'set /a N=0\r\n'
        ':copy\r\n'
        'copy /Y "%NEW%" "%PROG%\\%EXE%" >nul\r\n'
        'if not errorlevel 1 goto start\r\n'
        'timeout /t 2 /nobreak >nul\r\n'
        'set /a N+=1\r\n'
        'if %N% lss 5 goto copy\r\n'
        ':start\r\n'
        'if exist "%PROG%\\%EXE%" start "" "%PROG%\\%EXE%"\r\n'
    )
    with open(bat, 'w', encoding='gbk', newline='') as f:
        f.write(content)
    return bat


def _spawn_hidden(bat, *args):
    si = subprocess.STARTUPINFO()
    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    si.wShowWindow = subprocess.SW_HIDE
    subprocess.Popen(
        [bat] + list(args),
        creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP,
        startupinfo=si, close_fds=True)


def apply_and_restart(new_dir):
    """文件夹版：写 bat 并 detached 启动，由调用方随后退出程序。

    返回 True 表示已触发重启；APPLY_DRY_RUN 时仅打印并返回 False（用于联调）。
    """
    prog_dir = os.path.dirname(sys.executable)
    exe_name = os.path.basename(sys.executable)
    pid = os.getpid()
    bat = build_apply_bat(prog_dir, new_dir, exe_name, pid)
    log.info('准备覆盖更新：程序目录 %s，来源 %s，脚本 %s', prog_dir, new_dir, bat)
    if APPLY_DRY_RUN:
        print('[DRY_RUN] 将启动更新脚本：%s\n  PROG=%s\n  NEW=%s\n  EXE=%s\n  PID=%s'
              % (bat, prog_dir, new_dir, exe_name, pid))
        return False
    _spawn_hidden(bat, prog_dir, new_dir, exe_name, str(pid))
    return True


def apply_exe_and_restart(new_exe):
    """单文件版：等待退出后替换当前 exe 并重启。"""
    prog_dir = os.path.dirname(sys.executable)
    exe_name = os.path.basename(sys.executable)
    pid = os.getpid()
    bat = build_apply_exe_bat(prog_dir, new_exe, exe_name, pid)
    log.info('准备替换单文件版：程序 %s，来源 %s，脚本 %s', exe_name, new_exe, bat)
    if APPLY_DRY_RUN:
        print('[DRY_RUN] 将启动单文件更新脚本：%s\n  PROG=%s\n  NEW=%s\n  EXE=%s\n  PID=%s'
              % (bat, prog_dir, new_exe, exe_name, pid))
        return False
    _spawn_hidden(bat, prog_dir, new_exe, exe_name, str(pid))
    return True


# --------------------------- 后台线程 ---------------------------
class UpdateChecker(QThread):
    """静默检查 version.json；结果通过 check_done 信号回传主线程。"""
    check_done = pyqtSignal(dict)   # {'need':bool, 'info':dict, 'error':str}

    def __init__(self, local_version):
        super().__init__()
        self.local_version = local_version

    def run(self):
        try:
            info = fetch_version_info()
            need = need_update(self.local_version, info)
            log.info('更新检查完成：本地 %s，最新 %s，需要更新=%s',
                     self.local_version, info.get('latest'), need)
            self.check_done.emit({
                'need': need, 'info': info, 'error': None})
        except Exception as e:
            log.warning('更新检查失败：%s', e)
            self.check_done.emit({'need': False, 'info': None, 'error': str(e)})


class UpdateDownloader(QThread):
    """后台下载 + 校验 + 解压；结果通过 dl_done 信号回传主线程。"""
    dl_done = pyqtSignal(dict)      # {'ok':bool, 'new_dir':str, 'error':str}
    dl_progress = pyqtSignal(int, int)   # (已下载字节, 总字节)

    def __init__(self, local_version, info):
        super().__init__()
        self.local_version = local_version
        self.info = info

    def run(self):
        try:
            if is_onefile():
                new_exe = download_onefile(self.info,
                                           progress_cb=self.dl_progress.emit)
                log.info('单文件版更新包已就绪：%s', new_exe)
                self.dl_done.emit({'ok': True, 'new_exe': new_exe,
                                   'new_dir': None, 'error': None})
            else:
                new_dir = download_and_extract(
                    self.local_version, self.info,
                    progress_cb=self.dl_progress.emit)
                log.info('文件夹版更新包已就绪：%s', new_dir)
                self.dl_done.emit({'ok': True, 'new_exe': None,
                                   'new_dir': new_dir, 'error': None})
        except Exception as e:
            log.exception('下载更新失败')
            self.dl_done.emit({'ok': False, 'new_exe': None,
                               'new_dir': None, 'error': str(e)})
