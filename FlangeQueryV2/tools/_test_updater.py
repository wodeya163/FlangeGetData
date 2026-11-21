# -*- coding: utf-8 -*-
"""updater 联调测试（本地 file:// 模拟托管，DRY_RUN 不真替换开发目录）。

流程：构造 _test_pub（latest=3.79.0，folder zip 复用真实基线包），
验证 fetch / need_update / download+SHA256校验 / 解压 / apply_and_restart(DRY_RUN)。
"""
import hashlib
import json
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUBDIR = os.path.join(os.path.dirname(ROOT), '发布')
TESTPUB = os.path.join(ROOT, '_test_pub')
sys.path.insert(0, ROOT)

src_zip = os.path.join(PUBDIR, 'FlangeQueryV2-3.78.0-folder.zip')
assert os.path.isfile(src_zip), '请先运行 tools/_publish_update.py 生成基线发布'

os.makedirs(TESTPUB, exist_ok=True)
test_zip = os.path.join(TESTPUB, 'FlangeQueryV2-3.79.0-folder.zip')
shutil.copy2(src_zip, test_zip)
sha = hashlib.sha256(open(test_zip, 'rb').read()).hexdigest()
info = {
    'latest': '3.79.0',
    'min_version': '3.78.0',
    'channel': 'stable',
    'release_date': '2026-11-10',
    'notes': '测试更新：验证半自动更新链路',
    'files': {'folder': {
        'url': 'FlangeQueryV2-3.79.0-folder.zip',
        'sha256': sha,
        'size': os.path.getsize(test_zip),
    }},
}
json.dump(info, open(os.path.join(TESTPUB, 'version.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=2)
base = 'file:///' + TESTPUB.replace('\\', '/')

import updater  # 需要 PyQt5（由 PYTHONPATH=pylibs 提供）

# 1) 检查 + 比较版本
fetched = updater.fetch_version_info(base)
assert updater.need_update('3.78.0', fetched) is True, '应检测到 3.79.0 > 3.78.0'
assert updater.need_update('3.79.0', fetched) is False, '同版本不应触发更新'
print('[1] fetch_version_info + need_update ✅  (latest=%s)' % fetched['latest'])

# 2) 下载 + SHA256 校验 + 解压
new_dir = updater.download_and_extract('3.78.0', info, base=base)
assert os.path.isfile(os.path.join(new_dir, 'FlangeQueryV2.exe')), '解压后应有 exe'
print('[2] download + SHA256 校验 + 解压 ✅  (new_dir=%s)' % new_dir)

# 3) 应用（DRY_RUN，不真替换开发目录）
os.environ['FLANGE_UPDATE_DRYRUN'] = '1'
ok = updater.apply_and_restart(new_dir)
print('[3] apply_and_restart(DRY_RUN) 返回=%s ✅（未替换开发目录）' % ok)

# 清理
shutil.rmtree(TESTPUB, ignore_errors=True)
print('\n✅ updater 联调全流程通过：检查→下载→校验→解压→生成更新脚本')
