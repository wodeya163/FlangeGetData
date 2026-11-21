# -*- coding: utf-8 -*-
"""构建 V3 发布包，校验资源并生成 SHA256 清单。"""

import argparse
import datetime
import hashlib
import os
import shutil
import subprocess
import sys
import zipfile


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(ROOT, 'dist')
PACKAGE = os.path.join(ROOT, '_打包')
ZIP = os.path.join(ROOT, 'FlangeQueryV2_EXE便携版.zip')
ONEFILE = os.path.join(DIST, 'FlangeQueryV2.exe')
ONEDIR = os.path.join(DIST, 'FlangeQueryV2', 'FlangeQueryV2.exe')
USAGE_TEMPLATE = os.path.join(ROOT, 'docs', '使用说明模板.txt')
USAGE_FILE = os.path.join(PACKAGE, '使用说明.txt')


def _version():
    ns = {}
    with open(os.path.join(ROOT, 'version.py'), encoding='utf-8') as fh:
        exec(compile(fh.read(), 'version.py', 'exec'), ns)
    return ns['APP_VERSION']


def _hash_file(version):
    """SHA256 清单文件名跟随 version.py，避免升级后还生成旧版本文件名。"""
    return os.path.join(DIST, 'FlangeQueryV2-%s.sha256' % version)


def _render_usage(version):
    """用模板生成便携包使用说明，注入版本、构建日期和资源数量。"""
    if not os.path.isfile(USAGE_TEMPLATE):
        raise SystemExit('缺少使用说明模板：' + USAGE_TEMPLATE)
    data_count = len([n for n in os.listdir(os.path.join(ROOT, 'Data'))
                      if n.lower().endswith('.csv')])
    tpl_count = len([n for n in os.listdir(os.path.join(ROOT, 'templates'))
                     if n.lower().endswith('.bmp')])
    with open(USAGE_TEMPLATE, encoding='utf-8', newline='') as fh:
        text = fh.read()
    replacements = {
        '{{VERSION}}': 'V' + version,
        '{{BUILD_DATE}}': datetime.date.today().isoformat(),
        '{{TEMPLATE_COUNT}}': str(tpl_count),
        '{{DATA_COUNT}}': str(data_count),
    }
    for key, value in replacements.items():
        text = text.replace(key, value)
    if '{{' in text:
        raise SystemExit('使用说明模板存在未替换的占位符')
    os.makedirs(PACKAGE, exist_ok=True)
    with open(USAGE_FILE, 'w', encoding='utf-8', newline='') as fh:
        fh.write(text)
    print('使用说明已生成：%s（版本 V%s，模板 %d，CSV %d）'
          % (USAGE_FILE, version, tpl_count, data_count))


def _run(args, env=None):
    print('\n>>>', ' '.join(args), flush=True)
    subprocess.run(args, cwd=ROOT, env=env, check=True)


def _check_dependencies():
    missing = []
    for name in ('PyQt5', 'PyInstaller'):
        try:
            __import__(name)
        except Exception as exc:
            missing.append('%s (%s)' % (name, exc))
    if missing:
        raise SystemExit('构建环境缺少依赖：\n  ' + '\n  '.join(missing) +
                         '\n请先安装 requirements-build.txt')


def _clean():
    for path in (os.path.join(ROOT, 'build'), DIST,
                 os.path.join(PACKAGE, '单文件版'),
                 os.path.join(PACKAGE, '文件夹版')):
        if os.path.isdir(path):
            print('清理目录：', path)
            shutil.rmtree(path)
    if os.path.isfile(ZIP):
        print('清理文件：', ZIP)
        os.remove(ZIP)


def _sha256(path):
    digest = hashlib.sha256()
    with open(path, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def _write_hashes(version):
    entries = []
    paths = [('单文件版', ONEFILE), ('便携 zip', ZIP)]
    installer = os.path.join(DIST, 'installer',
                             'FlangeQueryV2-%s-setup.exe' % version)
    if os.path.isfile(installer):
        paths.append(('安装包', installer))
    for label, path in paths:
        if not os.path.isfile(path):
            raise SystemExit('缺少发布产物：' + path)
        entries.append('%s  %s' % (_sha256(path), os.path.basename(path)))
        print('%s SHA256：%s' % (label, entries[-1].split('  ')[0]))
    os.makedirs(DIST, exist_ok=True)
    hash_path = _hash_file(version)
    with open(hash_path, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write('\n'.join(entries) + '\n')
    print('SHA256 清单：', hash_path)


def _verify_zip():
    if not os.path.isfile(ZIP):
        raise SystemExit('缺少便携 zip：' + ZIP)
    with zipfile.ZipFile(ZIP) as zf:
        bad = zf.testzip()
        if bad:
            raise SystemExit('便携 zip 损坏：' + bad)
        print('zip 校验通过：%d 个条目，%.1f MB' %
              (len(zf.namelist()), os.path.getsize(ZIP) / 1024.0 / 1024.0))


def _verify_assets():
    """校验打包资源与源目录逐文件一致；数量由实际文件决定，不写死。"""
    pairs = (
        ('CSV', os.path.join(ROOT, 'Data'),
         os.path.join(DIST, 'FlangeQueryV2', '_internal', 'Data'), '.csv'),
        ('BMP', os.path.join(ROOT, 'templates'),
         os.path.join(DIST, 'FlangeQueryV2', '_internal', 'templates'), '.bmp'),
    )
    for label, src_dir, dst_dir, ext in pairs:
        if not os.path.isdir(src_dir):
            raise SystemExit('缺少源资源目录：' + src_dir)
        if not os.path.isdir(dst_dir):
            raise SystemExit('缺少打包资源目录：' + dst_dir)
        src_files = {n for n in os.listdir(src_dir) if n.lower().endswith(ext)}
        dst_files = {n for n in os.listdir(dst_dir) if n.lower().endswith(ext)}
        missing = sorted(src_files - dst_files)
        extra = sorted(dst_files - src_files)
        if missing or extra:
            raise SystemExit('%s 资源不一致：缺失=%s，多余=%s'
                             % (label, missing[:10], extra[:10]))
        for name in sorted(src_files):
            if (_sha256(os.path.join(src_dir, name))
                    != _sha256(os.path.join(dst_dir, name))):
                raise SystemExit('%s 内容不一致：%s' % (label, name))
        print('内置资源校验通过：%s=%d（与源目录逐文件一致）'
              % (label, len(src_files)))


def main():
    parser = argparse.ArgumentParser(description='构建 FlangeQuery 发布包')
    parser.add_argument('--clean', action='store_true', help='构建前清理 build/dist/_打包')
    parser.add_argument('--skip-tests', action='store_true', help='跳过测试')
    parser.add_argument('--skip-build', action='store_true', help='只重新打包和校验')
    parser.add_argument('--installer', action='store_true',
                        help='额外构建 Inno Setup 安装包（需 ISCC）')
    args = parser.parse_args()

    version = _version()
    print('构建版本：V%s' % version)
    if not args.skip_build:
        _check_dependencies()
    if args.clean:
        _clean()

    if not args.skip_tests:
        _run([sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-v'])

    if not args.skip_build:
        _run([sys.executable, os.path.join('tools', 'build_data.py')])
        _run([sys.executable, '-m', 'PyInstaller', '--noconfirm', '--clean',
              'FlangeQueryV2.spec'])
        _run([sys.executable, '-m', 'PyInstaller', '--noconfirm', '--clean',
              'FlangeQueryV2_onedir.spec'])

    _render_usage(version)
    _run([sys.executable, '_assemble_zip.py'])
    _verify_assets()
    _verify_zip()
    if args.installer:
        _run([sys.executable, os.path.join('tools', 'build_installer.py')])
    _write_hashes(version)
    print('\n构建完成：%s' % datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print('单文件版：', ONEFILE)
    print('文件夹版：', ONEDIR)
    print('便携包：  ', ZIP)


if __name__ == '__main__':
    main()
