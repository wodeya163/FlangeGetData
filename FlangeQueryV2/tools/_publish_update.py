# -*- coding: utf-8 -*-
"""发布更新包：压缩文件夹版 -> 生成 version.json -> 推到发布目录。

用法
----
  python tools/_publish_update.py --build        # 先重建再发布
  python tools/_publish_update.py                # 复用现有 dist 发布
  python tools/_publish_update.py --notes "修复XX；新增XX"

产物（发布目录，默认 FlangeGetData/发布）
  version.json                      更新清单（latest / files.folder.url+sha256+size）
  FlangeQueryV2-<ver>-folder.zip    文件夹版整包（顶层直接是 exe + _internal）

与更新器联动
------------
  更新源由 updater 的 GITEE_REPO / GITHUB_REPO 决定（Gitee 优先）：
  A) Gitee 码云 Releases（国内稳）：本脚本加 --gitee owner/repo，用 Gitee API + 私人令牌
     （FLANGE_GITEE_TOKEN）创建 release 并上传 version.json + folder zip；updater 走 Gitee API
     取最新 release 的 assets（兼容其 download_url 字段），免固定 URL、不受 tag 变化影响。
  B) GitHub Releases：加 --github owner/repo，自动 `gh release create` 上传同样两个资产。
  C) 通用 http(s)/file：两者都留空时，updater 读 UPDATE_BASE_URL 下的 version.json；
     本脚本把产物拷到 PUBDIR，你再把 PUBDIR 同步到 http(s) 托管。

  三种模式下 version.json 的 files.folder 字段：A/B 写 name（updater 从 assets 取直链），
  C 写 url；updater 都能解析。

注意：仅发布「文件夹版」用于自更新；单文件版（onefile）运行中被锁，不支持自更新。
"""
import argparse
import datetime
import hashlib
import json
import mimetypes
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request
import urllib.error
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(ROOT, 'dist')
PUBDIR = os.path.join(os.path.dirname(ROOT), '发布')   # 对应 file:///E:/AI作品/work/FlangeGetData/发布
FOLDER = os.path.join(DIST, 'FlangeQueryV2')          # onedir 产物目录
VERSION_PY = os.path.join(ROOT, 'version.py')
GITHUB_API = 'https://api.github.com'
GITEE_API = 'https://gitee.com/api/v5'
USER_AGENT = 'FlangeQuery-Publisher/1.0'


def read_version():
    with open(VERSION_PY, encoding='utf-8') as fh:
        txt = fh.read()
    m = re.search(r"APP_VERSION\s*=\s*['\"]([^'\"]+)['\"]", txt)
    return m.group(1) if m else '0.0.0'


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for c in iter(lambda: f.read(65536), b''):
            h.update(c)
    return h.hexdigest()


def zip_folder(version):
    """压缩 FOLDER 的内容（顶层直接是 FlangeQueryV2.exe + _internal），
    便于 robocopy 整包覆盖到用户程序目录。"""
    zip_path = os.path.join(DIST, 'FlangeQueryV2-%s-folder.zip' % version)
    if os.path.exists(zip_path):
        os.remove(zip_path)
    n = 0
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(FOLDER):
            for name in files:
                fp = os.path.join(root, name)
                rel = os.path.relpath(fp, FOLDER)
                zf.write(fp, rel)
                n += 1
    print('已压缩文件夹版：%d 个文件 -> %s' % (n, os.path.basename(zip_path)))
    return zip_path


def build():
    print('重建发布包（build_release.py --clean）…')
    subprocess.check_call(
        [sys.executable, os.path.join('tools', 'build_release.py'), '--clean'])


# --------------------------- GitHub Releases 发布 ---------------------------
def _github_api_post(url, data, tok, method='POST'):
    req = urllib.request.Request(
        url, data=data, method=method,
        headers={'Authorization': 'Bearer ' + tok,
                 'User-Agent': USER_AGENT,
                 'Accept': 'application/vnd.github+json'})
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read().decode('utf-8'))


def _upload_asset(upload_url, fp, tok):
    ct = mimetypes.guess_type(fp)[0] or 'application/octet-stream'
    with open(fp, 'rb') as fh:
        body = fh.read()
    url = upload_url + '?name=' + urllib.parse.quote(os.path.basename(fp))
    _github_api_post(url, body, tok)
    print('   已上传资产：%s（%d KB）' % (os.path.basename(fp), len(body) // 1024))


def publish_github(repo, version, zip_path, version_json_path, notes):
    """创建 latest release 并上传 version.json + folder zip。

    优先用 gh CLI；找不到 gh 但有 FLANGE_GITHUB_TOKEN 时改用 GitHub API。
    两者都不可用则只生成本地产物并打印手动上传指引，不阻塞。
    """
    tag = 'v' + version
    nf = os.path.join(tempfile.gettempdir(), 'flange_release_notes.txt')
    with open(nf, 'w', encoding='utf-8') as fh:
        fh.write(notes)

    have_gh = shutil.which('gh')
    if have_gh:
        print('用 gh 创建 release %s …' % tag)
        subprocess.check_call(
            ['gh', 'release', 'create', tag, '-R', repo,
             '-F', nf, '--title', '管路智选 V%s' % version,
             zip_path, version_json_path])
        print('✅ 已发布：https://github.com/%s/releases/tag/%s' % (repo, tag))
        return True

    tok = os.environ.get('FLANGE_GITHUB_TOKEN')
    if tok:
        print('gh 未安装，改用 GitHub API + token 创建 release %s …' % tag)
        rel = _github_api_post(
            '%s/repos/%s/releases' % (GITHUB_API, repo),
            json.dumps({'tag_name': tag,
                        'name': '管路智选 V%s' % version,
                        'body': notes,
                        'draft': False, 'prerelease': False}).encode('utf-8'),
            tok)
        upload_url = rel['upload_url'].split('{')[0]
        for fp in (version_json_path, zip_path):
            _upload_asset(upload_url, fp, tok)
        print('✅ 已发布：https://github.com/%s/releases/tag/%s' % (repo, tag))
        return True

    print('⚠️ 未检测到 gh CLI，也未设置 FLANGE_GITHUB_TOKEN。本地产物已生成，请任选其一上传：')
    print('   1) 安装 gh 并 `gh auth login`，重跑本脚本（自动上传）；')
    print('   2) GitHub 网页手动新建 release %s，拖入：' % tag)
    print('        %s' % version_json_path)
    print('        %s' % zip_path)
    return False


# --------------------------- Gitee 码云 Releases 发布 ---------------------------
def _gitee_api(url, data=None, files=None, tok=None, method='POST', timeout=120):
    """Gitee API 调用；私人令牌统一走 access_token 查询参数（最稳）。
    data 为 JSON 字节；files 为 {字段名: 文件路径} 用于 multipart 上传附件。
    timeout 可调（大文件上传建议 600）。"""
    if tok and 'access_token' not in url:
        url += ('?' if '?' not in url else '&') + 'access_token=' + tok
    if files:
        boundary = '----FlangeBoundary7QX'
        body = b''
        for k, v in files.items():
            body += ('--%s\r\n' % boundary).encode()
            body += ('Content-Disposition: form-data; name="%s"; filename="%s"\r\n'
                     % (k, os.path.basename(v))).encode('utf-8')
            body += b'Content-Type: application/octet-stream\r\n\r\n'
            with open(v, 'rb') as fh:
                body += fh.read()
            body += b'\r\n'
        body += ('--%s--\r\n' % boundary).encode()
        headers = {'User-Agent': USER_AGENT,
                   'Content-Type': 'multipart/form-data; boundary=%s' % boundary}
        req = urllib.request.Request(url, data=body, method=method, headers=headers)
    else:
        headers = {'User-Agent': USER_AGENT,
                   'Content-Type': 'application/json',
                   'Accept': 'application/json'}
        req = urllib.request.Request(url, data=data, method=method, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        txt = resp.read().decode('utf-8')
        return json.loads(txt) if txt else {}


def publish_gitee(repo, version, zip_path, version_json_path, notes):
    """创建 Gitee release 并上传 version.json + folder zip。
    需要 FLANGE_GITEE_TOKEN（gitee.com→设置→私人令牌，勾 projects 权限）。"""
    tok = os.environ.get('FLANGE_GITEE_TOKEN')
    if not tok:
        print('⚠️ 未设置 FLANGE_GITEE_TOKEN。Gitee 发布需要私人令牌。')
        _manual_upload_tip(version, zip_path, version_json_path, repo, 'gitee')
        return False
    tag = 'v' + version
    # 已有同名 release 则复用（支持断点重跑），否则创建
    existing = _gitee_api('%s/repos/%s/releases?per_page=20' % (GITEE_API, repo),
                          tok=tok, method='GET')
    rel = None
    if isinstance(existing, list):
        rel = next((x for x in existing if x.get('tag_name') == tag), None)
    if rel:
        rid = rel.get('id')
        have = {a.get('name') for a in (rel.get('assets') or [])}
        print('ℹ️ release %s 已存在 (id=%s)，复用；已有资产：%s'
              % (tag, rid, sorted(have) or '无'))
    else:
        # Gitee 创建 release 时 target_commitish 为必填（GitHub 可选），取仓库默认分支
        repo_info = _gitee_api('%s/repos/%s' % (GITEE_API, repo), tok=tok, method='GET')
        branch = repo_info.get('default_branch') or 'master'
        rel = _gitee_api(
            '%s/repos/%s/releases' % (GITEE_API, repo),
            json.dumps({'tag_name': tag, 'name': '管路智选 V%s' % version,
                        'body': notes, 'prerelease': False,
                        'target_commitish': branch}).encode('utf-8'),
            tok=tok, method='POST')
        rid = rel.get('id')
        have = set()
        if not rid:
            print('⚠️ 创建 Gitee release 失败（可能令牌权限不足）：%s' % rel)
            _manual_upload_tip(version, zip_path, version_json_path, repo, 'gitee')
            return False
        print('✅ 已创建 Gitee release %s (id=%s)' % (tag, rid))
    # 逐个上传缺失资产（大文件走 600s 超时；已存在则跳过）
    for fp in (version_json_path, zip_path):
        if os.path.basename(fp) in have:
            print('   已存在，跳过：%s' % os.path.basename(fp))
            continue
        _gitee_api(
            '%s/repos/%s/releases/%s/attach_files' % (GITEE_API, repo, rid),
            files={'file': fp}, tok=tok, method='POST', timeout=600)
        print('   已上传：%s（%d KB）'
              % (os.path.basename(fp), os.path.getsize(fp) // 1024))
    print('✅ 已发布：https://gitee.com/%s/releases' % repo)
    return True


def _manual_upload_tip(version, zip_path, version_json_path, repo, platform):
    print('   本地产物已生成，请任选其一上传到 %s：' % platform)
    print('   1) 设置私人令牌环境变量后重跑本脚本（自动上传）；')
    print('   2) 网页手动到 %s 新建 release v%s，拖入：' % (repo, version))
    print('        %s' % version_json_path)
    print('        %s' % zip_path)


def _upload(pubdir, version):
    """真实部署时在此接入上传（rclone / curl / 云存储 CLI）。默认仅本地。"""
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--build', action='store_true', help='发布前先重建')
    ap.add_argument('--github', metavar='owner/repo', default=None,
                    help='发布到 GitHub Releases，如 --github zhang/FlangeQueryV2')
    ap.add_argument('--gitee', metavar='owner/repo', default=None,
                    help='发布到 Gitee 码云 Releases，如 --gitee zhang/FlangeQueryV2')
    ap.add_argument('--notes', default='', help='更新说明（换行用 \\n）')
    args = ap.parse_args()

    if args.build:
        build()

    if not os.path.isdir(FOLDER):
        sys.exit('缺少文件夹版产物：%s\n先用 --build 或 tools/build_release.py' % FOLDER)

    version = read_version()
    zip_path = zip_folder(version)
    sha = sha256_of(zip_path)
    size = os.path.getsize(zip_path)

    folder_meta = {'sha256': sha, 'size': size}
    if args.gitee or args.github:
        folder_meta['name'] = os.path.basename(zip_path)   # Releases 模式：updater 从 assets 取
    else:
        folder_meta['url'] = os.path.basename(zip_path)    # 通用 http 模式：相对/完整 URL
    info = {
        'latest': version,
        'min_version': '3.78.0',
        'channel': 'stable',
        'release_date': datetime.date.today().isoformat(),
        'notes': (args.notes or '管路智选 V%s 更新' % version).replace('\\n', '\n'),
        'files': {'folder': folder_meta},
    }

    os.makedirs(PUBDIR, exist_ok=True)
    vj = os.path.join(PUBDIR, 'version.json')
    with open(vj, 'w', encoding='utf-8') as f:
        json.dump(info, f, ensure_ascii=False, indent=2)
    shutil.copy2(zip_path, PUBDIR)

    print('发布完成：V%s' % version)
    print('  version.json -> %s' % vj)
    print('  folder zip   -> %s (%d MB)' % (
        os.path.join(PUBDIR, os.path.basename(zip_path)),
        size // 1024 // 1024))
    print('  sha256       -> %s' % sha)

    if args.gitee:
        publish_gitee(args.gitee, version, zip_path, vj, info['notes'])
    elif args.github:
        publish_github(args.github, version, zip_path, vj, info['notes'])
    elif not _upload(PUBDIR, version):
        print('（本地发布模式：把 %s 整目录同步到 http(s) 托管即可上线）' % PUBDIR)


if __name__ == '__main__':
    main()
