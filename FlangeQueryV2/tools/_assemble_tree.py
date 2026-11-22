# -*- coding: utf-8 -*-
"""组装 GitHub tree/commit/ref，自动跳过尚未上传的 blob（让仓库先用起来）。

与 _finish_push_api.py 区别：对每个 blob 做 HEAD 校验，缺失的跳过并记录，
保证仓库能立即建立；后续补传缺失 blob 后再跑一次即可补全。
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
API = 'https://api.github.com'
ROOT = subprocess.run(['git', 'rev-parse', '--show-toplevel'],
                      capture_output=True, text=True).stdout.strip()

p = subprocess.run(['git', 'credential', 'fill'],
                   input='protocol=https\nhost=github.com\n\n',
                   capture_output=True, text=True, timeout=30)
TOK = dict(l.split('=', 1) for l in p.stdout.strip().splitlines() if '=' in l)['password']
H = {'User-Agent': 'FlangeQuery-Assemble/2.0', 'Authorization': 'Bearer ' + TOK,
     'Accept': 'application/vnd.github+json', 'Content-Type': 'application/json'}


def api(path, data=None, method=None, retries=5):
    body = json.dumps(data).encode('utf-8') if data is not None else None
    req = urllib.request.Request(API + path, data=body, headers=H,
                                 method=method or ('POST' if data is not None else 'GET'))
    last = None
    for i in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                txt = r.read().decode('utf-8')
                return json.loads(txt) if txt else {}
        except urllib.error.HTTPError as e:
            last = e
            if e.code < 500 and e.code != 409:
                raise RuntimeError('HTTP %s: %s' % (e.code, e.read().decode('utf-8', 'replace')[:200]))
            time.sleep(2 ** i)
        except Exception as e:
            last = e
            time.sleep(2 ** i)
    raise last


def exists(sha):
    req = urllib.request.Request('%s/repos/%s/%s/git/blobs/%s' % (API, OWNER, REPO, sha),
                                 headers=H)
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            r.read()
        return True
    except urllib.error.HTTPError as e:
        return e.code != 404
    except Exception:
        return False


def main():
    out = subprocess.run(['git', 'ls-tree', '-r', '-z', 'HEAD'], cwd=ROOT,
                         capture_output=True).stdout
    entries = []
    for rec in out.split(b'\0'):
        if b'\t' in rec:
            meta, pb = rec.split(b'\t', 1)
            mode, typ, sha = meta.decode('ascii').split()
            entries.append({'path': pb.decode('utf-8', 'surrogateescape'),
                            'mode': mode, 'type': 'blob', 'sha': sha})
    print('本地条目 %d，校验 GitHub blob...' % len(entries), flush=True)

    tree, skipped = [], []
    for i, e in enumerate(entries, 1):
        if exists(e['sha']):
            tree.append({k: e[k] for k in ('path', 'mode', 'type', 'sha')})
        else:
            skipped.append(e['path'])
        if i % 100 == 0:
            print('  已校验 %d' % i, flush=True)
    print('可用 blob %d，跳过 %d' % (len(tree), len(skipped)), flush=True)
    for p in skipped:
        print('  跳过:', p, flush=True)

    tr = api('/repos/%s/%s/git/trees' % (OWNER, REPO), {'tree': tree})
    print('Tree ✅ %s' % tr['sha'][:12], flush=True)

    # 取当前 main 的 commit 作父（init 或上次提交）
    parents = []
    try:
        ref = api('/repos/%s/%s/git/ref/heads/%s' % (OWNER, REPO, BRANCH))
        parents = [ref['object']['sha']]
    except Exception:
        pass
    cm = api('/repos/%s/%s/git/commits' % (OWNER, REPO), {
        'message': 'feat: import FlangeQueryV2 source (563 files)',
        'tree': tr['sha'], 'parents': parents,
    })
    print('Commit ✅ %s' % cm['sha'][:12], flush=True)

    try:
        api('/repos/%s/%s/git/refs/heads/%s' % (OWNER, REPO, BRANCH),
            {'sha': cm['sha'], 'force': True}, method='PATCH')
    except Exception:
        api('/repos/%s/%s/git/refs' % (OWNER, REPO),
            {'ref': 'refs/heads/' + BRANCH, 'sha': cm['sha']})
    print('Ref ✅', flush=True)
    print('https://github.com/%s/%s' % (OWNER, REPO), flush=True)
    if skipped:
        open('_tree_sha.txt', 'w').write(tr['sha'])
        print('注意：%d 个文件待补传' % len(skipped), flush=True)


if __name__ == '__main__':
    main()
