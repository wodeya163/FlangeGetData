# -*- coding: utf-8 -*-
"""构建 Inno Setup 安装包；如配置了签名工具，则先签 exe、后签安装包。"""

import argparse
import os
import shutil
import subprocess
import sys


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(ROOT, 'dist')
ONEFILE = os.path.join(DIST, 'FlangeQueryV2.exe')
ONEDIR = os.path.join(DIST, 'FlangeQueryV2', 'FlangeQueryV2.exe')
ISS = os.path.join(ROOT, 'tools', 'installer.iss')


def _version():
    ns = {}
    with open(os.path.join(ROOT, 'version.py'), encoding='utf-8') as fh:
        exec(compile(fh.read(), 'version.py', 'exec'), ns)
    return ns['APP_VERSION']


def _find_iscc():
    env = os.environ.get('ISCC')
    candidates = [
        env,
        shutil.which('iscc'),
        shutil.which('ISCC'),
        r'C:\Program Files (x86)\Inno Setup 6\ISCC.exe',
        r'C:\Program Files\Inno Setup 6\ISCC.exe',
    ]
    for path in candidates:
        if path and os.path.isfile(path):
            return path
    return None


def _sign(path):
    """可选签名：需设置 SIGNTOOL（signtool.exe 路径）与 CERT_PATH（pfx 路径）。"""
    signtool = os.environ.get('SIGNTOOL')
    cert = os.environ.get('CERT_PATH')
    if not signtool or not cert:
        return False
    subprocess.run([signtool, 'sign', '/fd', 'sha256', '/f', cert,
                    '/tr', 'http://timestamp.digicert.com', '/td', 'sha256',
                    path], check=True)
    print('已签名：', path)
    return True


def main():
    parser = argparse.ArgumentParser(description='构建 FlangeQuery 安装包')
    parser.add_argument('--no-sign', action='store_true', help='跳过签名')
    args = parser.parse_args()

    version = _version()
    for path in (ONEFILE, ONEDIR):
        if not os.path.isfile(path):
            raise SystemExit('缺少发布产物，请先运行 build_release.py：' + path)
    iscc = _find_iscc()
    if not iscc:
        print('未找到 ISCC.exe（Inno Setup 6）。')
        print('安装 Inno Setup 6 后重试，或设置环境变量 ISCC 指向 ISCC.exe。')
        return 1

    if not args.no_sign:
        try:
            _sign(ONEFILE)
            _sign(ONEDIR)
        except subprocess.CalledProcessError as exc:
            raise SystemExit('签名失败：%s' % exc)

    subprocess.run([iscc, '/DMyAppVersion=%s' % version, ISS],
                   cwd=ROOT, check=True)
    installer = os.path.join(DIST, 'installer',
                             'FlangeQueryV2-%s-setup.exe' % version)
    if not os.path.isfile(installer):
        raise SystemExit('安装包未生成：' + installer)
    if not args.no_sign:
        try:
            _sign(installer)
        except subprocess.CalledProcessError as exc:
            raise SystemExit('安装包签名失败：%s' % exc)
    print('安装包：', installer)
    return 0


if __name__ == '__main__':
    sys.exit(main())
