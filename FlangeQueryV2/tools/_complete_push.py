# -*- coding: utf-8 -*-
"""一键补全：补传缺失的 15 个 BMP 模板到 GitHub，并重建 tree/commit/ref。

网络恢复后运行：python tools/_complete_push.py
流程：找出未上传的 blob -> 串行补传 -> 重建完整 tree -> 更新 main 分支。
"""
import base64
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
H = {'User-Agent': 'FlangeQuery-Complete/1.0', 'Authorization': 'Bearer ' + TOK,
     'Accept': 'application/vnd.github+json', 'Content-Type': 'application/json'}


def api(path, data=None, method=None, retries=6):
    body = json.dumps(data).encode('utf-8') if data is not None else None
    req = urllib.request.Request(API + path, data=body, headers=H,
                                 method=method or ('POST' if data is not None else 'GET'))
    last = None
    for i in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                txt = r.read().decode('utf-8')
                return json.loads(txt) if txt else {}
        except urllib.error.HTTPError as e:
            last = e
            if e.code == 422:
                raise
            if e.code < 500 and e.code != 409:
                raise
            time.sleep(min(3 * (i + 1), 20))
        except Exception as e:
            last = e
            time.sleep(min(3 * (i + 1), 20))
    raise last


def blob_exists(sha):
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
    print('本地条目 %d，检查缺失...' % len(entries), flush=True)
    missing = [e for e in entries if not blob_exists(e['sha'])]
    print('缺失 %d 个' % len(missing), flush=True)

    # 串行补传
    for i, e in enumerate(missing, 1):
        content = subprocess.run(['git', 'cat-file', 'blob', e['sha']], cwd=ROOT,
                                 capture_output=True, check=True).stdout
        body = json.dumps({'content': base64.b64encode(content).decode('ascii'),
                           'encoding': 'base64'}).encode('utf-8')
        req = urllib.request.Request('%s/repos/%s/%s/git/blobs' % (API, OWNER, REPO),
                                     data=body, headers=H, method='POST')
        ok = False
        for attempt in range(10):
            try:
                with urllib.request.urlopen(req, timeout=120) as r:
                    d = json.loads(r.read().decode())
                if d['sha'] == e['sha']:
                    ok = True
                    break
            except urllib.error.HTTPError as ex:
                if ex.code == 422:
                    ok = True
                    break
                time.sleep(3 * (attempt + 1))
            except Exception:
                time.sleep(3 * (attempt + 1))
        print('  [%d/%d] %s -> %s' % (i, len(missing), e['path'].split('/')[-1],
                                      'OK' if ok else 'FAIL'), flush=True)
        if not ok:
            print('网络不通，中止。稍后重跑本脚本。', flush=True)
            return
        time.sleep(2)

    # 重建完整 tree + commit + ref
    tree = [{k: e[k] for k in ('path', 'mode', 'type', 'sha')} for e in entries]
    tr = api('/repos/%s/%s/git/trees' % (OWNER, REPO), {'tree': tree})
    print('Tree ✅', tr['sha'][:12], flush=True)
    ref = api('/repos/%s/%s/git/ref/heads/%s' % (OWNER, REPO, BRANCH))
    cm = api('/repos/%s/%s/git/commits' % (OWNER, REPO), {
        'message': 'feat: complete source import (564 files incl. BMP templates)',
        'tree': tr['sha'], 'parents': [ref['object']['sha']],
    })
    api('/repos/%s/%s/git/refs/heads/%s' % (OWNER, REPO, BRANCH),
        {'sha': cm['sha'], 'force': True}, method='PATCH')
    print('完成 ✅ https://github.com/%s/%s' % (OWNER, REPO), flush=True)


if __name__ == '__main__':
    main()
