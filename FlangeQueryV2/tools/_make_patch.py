# -*- coding: utf-8 -*-
"""生成增量更新包：只含两个完整包之间变化的文件，供 robocopy 覆盖式更新。

用法：
    python tools/_make_patch.py <旧完整包.zip> <新完整包.zip> [输出patch.zip]

原理：PyInstaller onedir 包中大部分是运行时 DLL，跨版本不变；真正变化
的往往只有 exe 与少量模块。更新器的 apply bat 用 robocopy /E（覆盖式、
非镜像），因此增量包解压覆盖即可完成升级，无需下载 41MB 完整包。

注意：robocopy /E 不会删除旧文件，若某版本有"删除文件"变更需另行处理。
"""
import hashlib
import os
import sys
import zipfile


def manifest(zf):
    return {i.filename: hashlib.md5(zf.read(i.filename)).hexdigest()
            for i in zf.infolist() if not i.is_dir()}


def make_patch(old_zip, new_zip, out_zip=None):
    a = zipfile.ZipFile(old_zip)
    b = zipfile.ZipFile(new_zip)
    ma, mb = manifest(a), manifest(b)
    changed = sorted(k for k in set(ma) & set(mb) if ma[k] != mb[k])
    added = sorted(set(mb) - set(ma))
    removed = sorted(set(ma) - set(mb))
    targets = changed + added
    if not targets:
        print('无变化文件，无需增量包')
        return None
    if removed:
        print('警告：以下文件在新版中被删除，增量包(robocopy /E)不会清除它们：')
        for k in removed:
            print('   -', k)
    if out_zip is None:
        base = os.path.splitext(os.path.basename(new_zip))[0]
        out_zip = os.path.join(os.path.dirname(os.path.abspath(new_zip)),
                               base.replace('-folder', '') + '-patch.zip')
    with zipfile.ZipFile(out_zip, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for k in targets:
            z.writestr(k, b.read(k))
    size = os.path.getsize(out_zip)
    sha = hashlib.sha256(open(out_zip, 'rb').read()).hexdigest()
    print('增量包: %s' % out_zip)
    print('变化文件 (%d):' % len(targets))
    for k in targets:
        print('   %9d B  %s' % (b.getinfo(k).file_size, k))
    print('patch 大小: %d B (%.2f MB)' % (size, size / 1048576))
    print('sha256: %s' % sha)
    print('\n将 version.json 的 files.folder 改为：')
    print("  {'name': '%s', 'sha256': '%s', 'size': %d}"
          % (os.path.basename(out_zip), sha, size))
    return out_zip


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    make_patch(sys.argv[1], sys.argv[2],
               sys.argv[3] if len(sys.argv) > 3 else None)


if __name__ == '__main__':
    main()
