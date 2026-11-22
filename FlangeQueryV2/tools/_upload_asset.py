# -*- coding: utf-8 -*-
"""把 folder zip 上传到已有 GitHub Release（用户在自己网络环境运行）。

本环境（agent 沙箱）上行链路会在大文件传输数百 KB 后重置，
43 MB 的 folder zip 无法自动上传；version.json（421 B）已成功上传。
请在自己电脑的正常终端运行本脚本完成大资产上传，一次即可。

用法：
  python tools/_upload_asset.py wodeya163/FlangeGetData v3.78.2 发布/FlangeQueryV2-3.78.2-folder.zip

凭据：git credential manager（git auth 已登录即可，不落盘、不回显）。
也可设环境变量 FLANGE_GITHUB_TOKEN 覆盖。
"""
import mimetypes
import os
import subprocess
import sys
import urllib.parse
import urllib.request

GITHUB_API = 'https://api.github.com'
UA = 'FlangeQuery-AssetUpload/1.0'


def get_token():
    tok = os.environ.get('FLANGE_GITHUB_TOKEN')
    if tok:
        return tok
    p = subprocess.run(['git', 'credential', 'fill'],
                       input='protocol=https\nhost=github.com\n\n',
                       capture_output=True, text=True, timeout=30)
    kv = dict(l.split('=', 1) for l in p.stdout.strip().splitlines() if '=' in l)
    if 'password' not in kv:
        raise SystemExit('未找到 GitHub 凭据：请先 git auth login 或设 FLANGE_GITHUB_TOKEN')
    return kv['password']


def api(tok, path, data=None, method=None, content_type='application/json', timeout=120):
    body = data if isinstance(data, bytes) else (
        None if data is None else __import__('json').dumps(data).encode('utf-8'))
    headers = {'Authorization': 'Bearer ' + tok, 'User-Agent': UA,
               'Accept': 'application/vnd.github+json'}
    if body is not None:
        headers['Content-Type'] = content_type
    req = urllib.request.Request(GITHUB_API + path, data=body, headers=headers,
                                 method=method or ('POST' if body is not None else 'GET'))
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        txt = resp.read().decode('utf-8')
        return __import__('json').loads(txt) if txt else {}


def main():
    if len(sys.argv) != 4:
        raise SystemExit(__doc__)
    repo, tag, fp = sys.argv[1], sys.argv[2], sys.argv[3]
    if not os.path.isfile(fp):
        raise SystemExit('文件不存在：' + fp)
    tok = get_token()
    rel = api(tok, '/repos/%s/releases/tags/%s' % (repo, tag))
    rid = rel.get('id')
    if not rid:
        raise SystemExit('release %s 不存在，请先发布' % tag)
    name = os.path.basename(fp)
    for asset in rel.get('assets') or []:
        if asset.get('name') == name:
            api(tok, '/repos/%s/releases/assets/%s' % (repo, asset['id']),
                method='DELETE')
            print('已删除同名旧资产：%s' % name)
    ct = mimetypes.guess_type(fp)[0] or 'application/octet-stream'
    url = rel['upload_url'].split('{')[0] + '?name=' + urllib.parse.quote(name)
    size = os.path.getsize(fp)
    print('正在上传 %s（%.1f MB）到 %s …' % (name, size / 1048576, tag))
    with open(fp, 'rb') as fh:
        body = fh.read()
    req = urllib.request.Request(url, data=body, headers={
        'Authorization': 'Bearer ' + tok, 'User-Agent': UA,
        'Content-Type': ct, 'Accept': 'application/vnd.github+json'}, method='POST')
    with urllib.request.urlopen(req, timeout=3600) as resp:
        result = __import__('json').loads(resp.read().decode('utf-8'))
    print('✅ 上传成功：%s (%d bytes)' % (result.get('name'), result.get('size')))
    print('发布页：https://github.com/%s/releases/tag/%s' % (repo, tag))


if __name__ == '__main__':
    main()
