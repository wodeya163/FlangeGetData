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
import os
import re
import shutil
import subprocess
import sys
import tempfile
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


def _asset_url(assets, suffix):
    """从 assets 列表按文件名后缀匹配下载地址；兼容 GitHub 的
    browser_download_url 与 Gitee 的 download_url 两种字段名。"""
    if not assets:
        return None
    for a in assets:
        if a.get('name', '').endswith(suffix):
            return a.get('browser_download_url') or a.get('download_url')
    return None


def github_latest_release(repo):
    """拉取 latest release（公开仓库免 token；私有仓库需 FLANGE_GITHUB_TOKEN）。"""
    tok = os.environ.get('FLANGE_GITHUB_TOKEN')
    url = '%s/repos/%s/releases/latest' % (GITHUB_API, repo)
    req = urllib.request.Request(url, headers=_releases_headers(tok))
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode('utf-8'))


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
    req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read()


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
        if not _asset_url(assets, '-folder.zip'):
            raise RuntimeError(
                '发布源(%s) 最新 release %s 缺少 *-folder.zip 更新包，'
                '请先在 Gitee/GitHub Release 上传完整包'
                % (source, rel.get('tag_name')))
        vj = next((a for a in assets if a['name'] == 'version.json'), None)
        if vj:
            raw = fetch_bytes(vj.get('browser_download_url') or vj.get('download_url'))
            info = json.loads(raw.decode('utf-8'))
        else:
            # 没附带 version.json：用 tag 当 latest，其余信息从 assets 取
            info = {'latest': str(rel.get('tag_name', '')).lstrip('vV') or None,
                    'notes': rel.get('body', ''), 'files': {}}
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


def download(url, dest, progress_cb=None):
    """支持 http(s) 与 file://；file:// 直接拷贝，http 流式写并回调进度。"""
    lp = _local_path_of(url)
    if lp is not None:
        shutil.copyfile(lp, dest)
        if progress_cb:
            progress_cb(100, 100)
        return dest
    req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
    with urllib.request.urlopen(req, timeout=120) as resp, open(dest, 'wb') as out:
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


def download_and_extract(local_version, info, base=None, tmp_root=None):
    """下载 folder zip → 校验 SHA256 → 解压，返回 new_dir（解压根）。异常向上抛。"""
    base = normalize_base(base or UPDATE_BASE_URL)
    url = _resolve_folder_url(info, base)
    if not url:
        raise ValueError('version.json 缺少 folder 下载地址')
    expected = (info.get('files', {}).get('folder') or {}).get('sha256')
    tmp = tempfile.mkdtemp(prefix='flange_upd_', dir=tmp_root)
    zip_path = os.path.join(tmp, 'folder.zip')
    download(url, zip_path)
    if not verify_sha256(zip_path, expected):
        raise ValueError('下载文件 SHA256 校验失败，可能损坏或被篡改')
    new_dir = os.path.join(tmp, 'new')
    os.makedirs(new_dir, exist_ok=True)
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(new_dir)
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
    with open(bat, 'w', encoding='gbk') as f:
        f.write(content)
    return bat


def apply_and_restart(new_dir):
    """写 bat 并以 detached 方式启动（无黑窗），由调用方随后退出程序。

    返回 True 表示已触发重启；APPLY_DRY_RUN 时仅打印并返回 False（用于联调）。
    """
    prog_dir = os.path.dirname(sys.executable)
    exe_name = os.path.basename(sys.executable)
    pid = os.getpid()
    bat = build_apply_bat(prog_dir, new_dir, exe_name, pid)
    if APPLY_DRY_RUN:
        print('[DRY_RUN] 将启动更新脚本：%s\n  PROG=%s\n  NEW=%s\n  EXE=%s\n  PID=%s'
              % (bat, prog_dir, new_dir, exe_name, pid))
        return False
    si = subprocess.STARTUPINFO()
    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    si.wShowWindow = subprocess.SW_HIDE
    subprocess.Popen(
        [bat, prog_dir, new_dir, exe_name, str(pid)],
        creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP,
        startupinfo=si, close_fds=True)
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
            self.check_done.emit({
                'need': need_update(self.local_version, info),
                'info': info, 'error': None})
        except Exception as e:
            self.check_done.emit({'need': False, 'info': None, 'error': str(e)})


class UpdateDownloader(QThread):
    """后台下载 + 校验 + 解压；结果通过 dl_done 信号回传主线程。"""
    dl_done = pyqtSignal(dict)      # {'ok':bool, 'new_dir':str, 'error':str}

    def __init__(self, local_version, info):
        super().__init__()
        self.local_version = local_version
        self.info = info

    def run(self):
        try:
            new_dir = download_and_extract(self.local_version, self.info)
            self.dl_done.emit({'ok': True, 'new_dir': new_dir, 'error': None})
        except Exception as e:
            self.dl_done.emit({'ok': False, 'new_dir': None, 'error': str(e)})
