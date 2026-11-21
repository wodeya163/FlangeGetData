# -*- coding: utf-8 -*-
"""用本地 git 的 blob sha 直接在 GitHub 构造 tree/commit/ref（零上传）。

原理：GitHub blob 的 sha 就是 git blob 的 sha1（内容寻址），只要 blob 已通过
_push_via_api.py 上传到仓库，就能用本地 `git ls-tree -r HEAD` 得到的 sha
直接构造 tree，无需再上传任何内容。

用法：python tools/_finish_push_api.py
"""
import json
import os
import subprocess
import time
import urllib.request
import urllib.error

OWNER = 'wodeya163'
REPO = 'FlangeGetData'
BRANCH = 'main'
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API = 'https://api.github.com'
UA = {'User-Agent': 'FlangeQuery-Assemble/1.0',
      'Accept': 'application/vnd.github+json'}


def get_token():
    p = subprocess.run(['git', 'credential', 'fill'],
                       input='protocol=https\nhost=github.com\n\n',
                       capture_output=True, text=True, timeout=30)
    return dict(l.split('=', 1) for l in p.stdout.strip().splitlines()
                if '=' in l)['password']


HEADERS = dict(UA, Authorization='Bearer ' + get_token())


def api(path, data=None, method=None, retries=5):
    body = json.dumps(data).encode('utf-8') if data is not None else None
    req = urllib.request.Request(API + path, data=body, headers=HEADERS,
                                 method=method or ('POST' if data else 'GET'))
    last = None
    for i in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                txt = r.read().decode('utf-8')
                return json.loads(txt) if txt else {}
        except urllib.error.HTTPError as e:
            if e.code < 500:
                err = e.read().decode('utf-8', 'replace')
                raise RuntimeError('HTTP %s %s' % (e.code, err[:300]))
            last = e; time.sleep(2 ** i)
        except Exception as e:
            last = e; time.sleep(2 ** i)
    raise last


def main():
    # 从本地 git tree 读全部 blob（path + sha + mode）
    out = subprocess.run(['git', 'ls-tree', '-r', '-z', 'HEAD'], cwd=ROOT,
                         capture_output=True).stdout.decode('utf-8', 'replace')
    entries = []
    for rec in out.split('\0'):
        if not rec or '\t' not in rec:
            continue
        meta, path = rec.split('\t', 1)
        mode, typ, sha = meta.split()
        entries.append({'path': path, 'mode': mode, 'type': 'blob', 'sha': sha})
    print('本地 tree 条目: %d' % len(entries), flush=True)

    # 校验 blob 是否都已存在于 GitHub（抽样查 5 个）
    sample = entries[:5]
    for e in sample:
        try:
            api('/repos/%s/%s/git/blobs/%s' % (OWNER, REPO, e['sha']))
            print('  blob %s 已存在 ✅' % e['sha'][:10], flush=True)
        except Exception as ex:
            print('  blob %s 缺失 ❌ %s' % (e['sha'][:10], ex), flush=True)
            raise SystemExit('有 blob 未上传，请先跑 _push_via_api.py')

    # 构造 tree（base_tree 省略，全量显式）
    tr = api('/repos/%s/%s/git/trees' % (OWNER, REPO), {'tree': entries})
    print('Tree ✅ %s' % tr['sha'][:12], flush=True)

    # commit
    cm = api('/repos/%s/%s/git/commits' % (OWNER, REPO), {
        'message': 'chore: clean source snapshot (564 files, 26MB)\n\n'
                   'Source only: Python code, BMP templates, CSV data, docs, specs.\n'
                   'Decompiled/extracted artifacts and binaries excluded via .gitignore.',
        'tree': tr['sha'],
    })
    print('Commit ✅ %s' % cm['sha'][:12], flush=True)

    # 更新 ref（分支已存在用 PATCH，否则 POST）
    try:
        api('/repos/%s/%s/git/refs/heads/%s' % (OWNER, REPO, BRANCH),
            {'sha': cm['sha'], 'force': True}, method='PATCH')
    except Exception:
        api('/repos/%s/%s/git/refs' % (OWNER, REPO),
            {'ref': 'refs/heads/' + BRANCH, 'sha': cm['sha']})
    print('Ref ✅ %s' % BRANCH, flush=True)
    print('完成: https://github.com/%s/%s' % (OWNER, REPO), flush=True)


if __name__ == '__main__':
    main()
