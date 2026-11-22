# -*- coding: utf-8 -*-
"""串行补传失败的大文件 blob（避免并发触发 401 限流 / 400 大 payload）。

从日志提取失败文件列表，逐个用 git cat-file 读索引内容上传，
成功后打印 sha。全部成功后再跑 _finish_push_api.py 组装 tree/commit/ref。
"""
import base64
import json
import os
import re
import subprocess
import time
import urllib.request
import urllib.error

OWNER = 'wodeya163'
REPO = 'FlangeGetData'
API = 'https://api.github.com'
ROOT = subprocess.run(['git', 'rev-parse', '--show-toplevel'],
                      capture_output=True, text=True).stdout.strip()

p = subprocess.run(['git', 'credential', 'fill'],
                   input='protocol=https\nhost=github.com\n\n',
                   capture_output=True, text=True, timeout=30)
TOK = dict(l.split('=', 1) for l in p.stdout.strip().splitlines() if '=' in l)['password']
H = {'User-Agent': 'FlangeQuery-Retry/1.0', 'Authorization': 'Bearer ' + TOK,
     'Accept': 'application/vnd.github+json', 'Content-Type': 'application/json'}


def upload_one(path, sha, retries=6):
    body = json.dumps({'content': base64.b64encode(
        subprocess.run(['git', 'cat-file', 'blob', sha], cwd=ROOT,
                       capture_output=True, check=True).stdout).decode('ascii'),
        'encoding': 'base64'}).encode('utf-8')
    req = urllib.request.Request('%s/repos/%s/%s/git/blobs' % (API, OWNER, REPO),
                                 data=body, headers=H, method='POST')
    for i in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                d = json.loads(r.read().decode('utf-8'))
            if d['sha'] == sha:
                return 'OK'
            return 'MISMATCH %s' % d['sha'][:10]
        except urllib.error.HTTPError as e:
            last = 'HTTP %s' % e.code
            if e.code in (401, 403, 429, 400, 500, 502, 503):
                time.sleep(3 * (i + 1))
                continue
            return last
        except Exception as e:
            last = str(e)[:60]
            time.sleep(3 * (i + 1))
    return last


def main():
    # 从上传日志提取失败文件（"    path ERR: ..." 行）
    log = 'E:/AI作品/work/FlangeGetData/_api_push4.log'
    text = open(log, encoding='utf-8', errors='replace').read()
    paths = []
    for line in text.splitlines():
        m = re.match(r'^    (.+?) ERR:', line)
        if m:
            paths.append(m.group(1))
    print('失败文件 %d 个，串行补传...' % len(paths), flush=True)

    out = subprocess.run(['git', 'ls-tree', '-r', '-z', 'HEAD'], cwd=ROOT,
                         capture_output=True).stdout
    sha_map = {}
    for rec in out.split(b'\0'):
        if b'\t' in rec:
            meta, pb = rec.split(b'\t', 1)
            sha_map[pb.decode('utf-8', 'surrogateescape')] = meta.decode('ascii').split()[2]

    failed = []
    for i, path in enumerate(paths, 1):
        sha = sha_map.get(path)
        if not sha:
            print('  [%d/%d] %s -> 路径未找到!' % (i, len(paths), path), flush=True)
            failed.append(path); continue
        r = upload_one(path, sha)
        print('  [%d/%d] %s -> %s' % (i, len(paths), os.path.basename(path), r),
              flush=True)
        if r != 'OK':
            failed.append(path)
        time.sleep(1.5)  # 令牌限流保护

    if failed:
        print('\n仍失败 %d 个:' % len(failed), flush=True)
        for p in failed: print('   ', p, flush=True)
        raise SystemExit(1)
    print('\n全部补传成功 ✅', flush=True)


if __name__ == '__main__':
    main()
