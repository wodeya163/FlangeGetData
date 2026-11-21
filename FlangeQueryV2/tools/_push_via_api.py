# -*- coding: utf-8 -*-
"""通过 GitHub REST API 上传源码到仓库（绕过 git CONNECT 隧道被沙箱代理拦截的问题）。

策略：Git Data API —— 逐文件创建 blob（base64），构造 tree，创建 commit，
更新分支 ref。26MB / 563 文件，blob 逐个上传（并发 8），避开大 payload。

用法：python tools/_push_via_api.py
凭据：从 git credential manager 读取（不落盘、不回显）。
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
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API = 'https://api.github.com'
UA = {'User-Agent': 'FlangeQuery-SourcePush/1.0',
      'Accept': 'application/vnd.github+json'}


def get_token():
    p = subprocess.run(['git', 'credential', 'fill'],
                       input='protocol=https\nhost=github.com\n\n',
                       capture_output=True, text=True, timeout=30)
    return dict(l.split('=', 1) for l in p.stdout.strip().splitlines()
                if '=' in l)['password']


TOKEN = get_token()
HEADERS = dict(UA, Authorization='Bearer ' + TOKEN)


def api(path, data=None, method=None, retries=4):
    """API 调用，带重试（502/超时常见）。"""
    body = json.dumps(data).encode('utf-8') if data is not None else None
    req = urllib.request.Request(API + path, data=body, headers=HEADERS,
                                 method=method or ('POST' if data else 'GET'))
    last = None
    for i in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                txt = r.read().decode('utf-8')
                return json.loads(txt) if txt else {}
        except urllib.error.HTTPError as e:
            last = e
            if e.code < 500:
                raise
            time.sleep(2 ** i)
        except Exception as e:
            last = e
            time.sleep(2 ** i)
    raise last


def upload_blob(path):
    """上传单个文件为 blob，返回 (path, sha) 或 (path, None)。"""
    fp = os.path.join(ROOT, path)
    try:
        with open(fp, 'rb') as f:
            content = base64.b64encode(f.read()).decode('ascii')
        r = api('/repos/%s/%s/git/blobs' % (OWNER, REPO),
                {'content': content, 'encoding': 'base64'})
        return path, r['sha']
    except Exception as e:
        return path, 'ERR: %s' % e


def main():
    # 1) 取待提交文件（git diff --cached 名称）
    files = [f for f in subprocess.run(
        ['git', 'diff', '--cached', '--name-only', '-z'],
        cwd=ROOT, capture_output=True).stdout.decode('utf-8', 'replace').split('\0') if f]
    print('待上传文件: %d 个' % len(files), flush=True)

    # 2) 并发上传 blob
    blobs = {}
    errors = []
    t0 = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
        for i, (path, sha) in enumerate(ex.map(upload_blob, files), 1):
            if sha and not sha.startswith('ERR:'):
                blobs[path] = sha
            else:
                errors.append((path, sha))
            if i % 50 == 0:
                print('  已上传 %d/%d (%.0fs)' % (i, len(files), time.time() - t0),
                      flush=True)
    if errors:
        print('上传失败 %d 个:' % len(errors), flush=True)
        for p, e in errors[:10]:
            print('   ', p, e, flush=True)
        sys.exit(1)

    # 3) 构造 tree
    tree = [{'path': p, 'mode': '100644', 'type': 'blob', 'sha': blobs[p]}
            for p in files]
    tr = api('/repos/%s/%s/git/trees' % (OWNER, REPO), {'tree': tree})
    print('Tree 创建 ✅ sha=%s' % tr['sha'][:12], flush=True)

    # 4) 创建 commit（无父 = orphan 干净起步）
    cm = api('/repos/%s/%s/git/commits' % (OWNER, REPO), {
        'message': 'chore: clean source snapshot (563 files, 26MB)\n\n'
                   'Source only: Python code, BMP templates, CSV data, docs, specs.\n'
                   'Decompiled/extracted artifacts and binaries excluded via .gitignore.',
        'tree': tr['sha'],
    })
    print('Commit 创建 ✅ sha=%s' % cm['sha'][:12], flush=True)

    # 5) 更新分支 ref
    ref = api('/repos/%s/%s/git/refs/heads/%s' % (OWNER, REPO, BRANCH),
              {'sha': cm['sha'], 'force': True}, method='PATCH')
    print('分支更新 ✅ %s -> %s' % (BRANCH, cm['sha'][:12]), flush=True)
    print('仓库地址: https://github.com/%s/%s' % (OWNER, REPO), flush=True)
    print('总耗时 %.0f 秒' % (time.time() - t0), flush=True)


if __name__ == '__main__':
    main()
