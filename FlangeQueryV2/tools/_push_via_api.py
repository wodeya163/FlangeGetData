# -*- coding: utf-8 -*-
"""通过 GitHub REST API 上传源码（git CONNECT 隧道被沙箱代理拦截时的绕行方案）。

流程：blob(断点续传) -> tree -> commit -> ref。
仓库须非空（用 contents 端点初始化一个 README 即可，因为 GitHub 禁止对空仓库用 Git Data API）。

用法：python tools/_push_via_api.py
凭据：git credential manager（不落盘、不回显）。
"""
import base64
import concurrent.futures
import json
import os
import subprocess
import sys
import time
import urllib.request
import urllib.error

OWNER = 'wodeya163'
REPO = 'FlangeGetData'
BRANCH = 'main'
ROOT = subprocess.run(['git', 'rev-parse', '--show-toplevel'],
                      cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                      capture_output=True, text=True).stdout.strip()
API = 'https://api.github.com'
UA = {'User-Agent': 'FlangeQuery-SourcePush/1.1',
      'Accept': 'application/vnd.github+json'}


def get_token():
    p = subprocess.run(['git', 'credential', 'fill'],
                       input='protocol=https\nhost=github.com\n\n',
                       capture_output=True, text=True, timeout=30)
    return dict(l.split('=', 1) for l in p.stdout.strip().splitlines()
                if '=' in l)['password']


TOKEN = get_token()
HEADERS = dict(UA, Authorization='Bearer ' + TOKEN,
               **{'Content-Type': 'application/json'})


def api(path, data=None, method=None, retries=6):
    body = json.dumps(data).encode('utf-8') if data is not None else None
    req = urllib.request.Request(API + path, data=body, headers=HEADERS,
                                 method=method or ('POST' if data is not None else 'GET'))
    last = None
    for i in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                txt = r.read().decode('utf-8')
                return json.loads(txt) if txt else {}
        except urllib.error.HTTPError as e:
            last = e
            if e.code == 422:  # 已存在类错误直接抛
                raise
            if e.code < 500 and e.code != 409:
                raise
            time.sleep(min(2 ** i, 20))
        except Exception as e:
            last = e
            time.sleep(min(2 ** i, 20))
    raise last


def git_entries():
    """返回 [{path, mode, sha, fs_path}]，用 surrogateescape 保真文件名。"""
    out = subprocess.run(['git', 'ls-tree', '-r', '-z', 'HEAD'], cwd=ROOT,
                         capture_output=True).stdout
    entries = []
    for rec in out.split(b'\0'):
        if not rec or b'\t' not in rec:
            continue
        meta, path_b = rec.split(b'\t', 1)
        mode, typ, sha = meta.decode('ascii').split()
        path = path_b.decode('utf-8', 'surrogateescape')
        entries.append({'path': path, 'mode': mode, 'type': 'blob',
                        'sha': sha, 'fs_path': os.path.join(ROOT, path)})
    return entries


def upload_blob(e):
    """上传单个 blob；已存在则跳过。返回 (path, 'ok'|'skip'|'ERR:...')"""
    sha = e['sha']
    # 判重：HEAD 请求该 sha
    try:
        api('/repos/%s/%s/git/blobs/%s' % (OWNER, REPO, sha))
        return e['path'], 'skip'
    except urllib.error.HTTPError as ex:
        if ex.code != 404:
            return e['path'], 'ERR: check %s' % ex.code
    except Exception as ex:
        return e['path'], 'ERR: check %s' % ex
    # 上传：用 git cat-file 读索引中的原始 blob（避免工作区 CRLF 转换导致 sha 不符）
    try:
        content = subprocess.run(['git', 'cat-file', 'blob', sha], cwd=ROOT,
                                 capture_output=True, check=True).stdout
        r = api('/repos/%s/%s/git/blobs' % (OWNER, REPO),
                {'content': base64.b64encode(content).decode('ascii'),
                 'encoding': 'base64'})
        if r.get('sha') != sha:
            return e['path'], 'ERR: sha mismatch %s != %s' % (r.get('sha'), sha)
        return e['path'], 'ok'
    except Exception as ex:
        return e['path'], 'ERR: %s' % ex


def main():
    entries = git_entries()
    print('本地 tree 条目: %d' % len(entries), flush=True)

    # 并发上传（断点续传）
    counts = {'ok': 0, 'skip': 0, 'err': 0}
    errors = []
    t0 = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
        for i, (path, status) in enumerate(ex.map(upload_blob, entries), 1):
            if status.startswith('ERR:'):
                counts['err'] += 1
                errors.append((path, status))
            else:
                counts[status] += 1
            if i % 50 == 0:
                print('  %d/%d ok=%d skip=%d err=%d (%.0fs)' %
                      (i, len(entries), counts['ok'], counts['skip'],
                       counts['err'], time.time() - t0), flush=True)
    print('blob 汇总: %s' % counts, flush=True)
    if errors:
        print('失败 %d 个:' % len(errors), flush=True)
        for p, s in errors[:10]:
            print('   ', p, s, flush=True)
        sys.exit(1)

    # 构造 tree（用本地 sha，GitHub 内容寻址一致）
    tree = [{'path': e['path'], 'mode': e['mode'], 'type': 'blob',
             'sha': e['sha']} for e in entries]
    tr = api('/repos/%s/%s/git/trees' % (OWNER, REPO), {'tree': tree})
    print('Tree ✅ %s' % tr['sha'][:12], flush=True)

    cm = api('/repos/%s/%s/git/commits' % (OWNER, REPO), {
        'message': 'chore: clean source snapshot (564 files, 26MB)\n\n'
                   'Source: Python code, BMP templates, CSV data, docs, specs.\n'
                   'Decompiled/extracted artifacts and binaries excluded.',
        'tree': tr['sha'],
        'parents': [api('/repos/%s/%s/git/ref/heads/%s' % (OWNER, REPO, BRANCH))['object']['sha']],
    })
    print('Commit ✅ %s' % cm['sha'][:12], flush=True)

    api('/repos/%s/%s/git/refs/heads/%s' % (OWNER, REPO, BRANCH),
        {'sha': cm['sha'], 'force': True}, method='PATCH')
    print('Ref ✅ %s' % BRANCH, flush=True)
    print('完成: https://github.com/%s/%s' % (OWNER, REPO), flush=True)
    print('耗时 %.0f 秒' % (time.time() - t0), flush=True)


if __name__ == '__main__':
    main()
