# -*- coding: utf-8 -*-
"""CadQuery 齿轮 STEP 工作进程（由 Python 3.12 + CadQuery 执行）。"""

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from core.gear_stp import _build


def main():
    if len(sys.argv) != 2:
        print('用法: python cadquery_gear_worker.py <json>', file=sys.stderr)
        return 2
    try:
        job = json.loads(sys.argv[1])
    except Exception as exc:
        print('JSON 解析失败: %s' % exc, file=sys.stderr)
        return 2
    path = job.get('path')
    try:
        out = _build(job.get('mode', 'spur'), job.get('params') or {}, path)
        print(json.dumps({'ok': True, 'path': out,
                          'size': os.path.getsize(out)}, ensure_ascii=False))
        return 0
    except Exception as exc:
        print('%s: %s' % (type(exc).__name__, exc), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
