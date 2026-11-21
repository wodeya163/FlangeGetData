# -*- coding: utf-8 -*-
"""Gitee 端到端更新链路真实验证（模拟旧版用户）。

用法（受管 python + PYTHONPATH=pylibs）：
  python tools/_test_gitee_e2e.py [本地版本号]

不设任何 token（验证公开仓库免鉴权拉取）；FLANGE_GITEE_REPO 若已设则以其为准，
否则用 updater.py 内嵌默认仓库名——与真实分发场景一致。
"""
import os
import sys

import updater

LOCAL_VERSION = sys.argv[1] if len(sys.argv) > 1 else '0.0.0'


def main():
    print('更新源: GITEE_REPO = %r (未设 token，模拟真实用户端)' % updater.GITEE_REPO)
    info = updater.fetch_version_info()
    latest = info.get('latest')
    print('[1] fetch_version_info ✅  latest=%s' % latest)
    assets = [a.get('name') for a in (info.get('_release', {}).get('assets') or [])]
    print('    assets: %s' % assets)
    if not latest:
        print('⚠️ Gitee 上尚无 release，无法验证')
        return 1
    need = updater.need_update(LOCAL_VERSION, info)
    print('[2] need_update(%s -> %s) = %s %s'
          % (LOCAL_VERSION, latest, need, '✅' if need else '（本机已是最新）'))
    if not need:
        return 0
    url = updater._resolve_folder_url(info, None)
    print('[3] folder 直链 ✅  -> %s' % url)
    new_dir = updater.download_and_extract(LOCAL_VERSION, info)
    exe = os.path.join(new_dir, 'FlangeQueryV2.exe')
    internal = os.path.join(new_dir, '_internal')
    n = sum(len(fs) for _, _, fs in os.walk(new_dir))
    assert os.path.isfile(exe), '解压缺 exe'
    assert os.path.isdir(internal), '解压缺 _internal'
    print('[4] 下载 + SHA256 校验 + 解压 ✅  共 %d 文件，exe/_internal 完整' % n)
    print()
    print('✅ 端到端全链路通过：Gitee 发布 → 检查 → 拉取 → 校验 → 就绪')
    return 0


if __name__ == '__main__':
    sys.exit(main())
