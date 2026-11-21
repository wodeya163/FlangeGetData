# -*- coding: utf-8 -*-
"""齿轮 STEP 生成。

主程序运行在 Python 3.13；CadQuery/OCP 的 OCP 轮子只提供到 CPython 3.12，
因此这里把建模任务交给独立的 CadQuery 解释器执行。
"""

import json
import math
import os
import subprocess
import sys
import tempfile


_WORKER_SOURCE = r"""# -*- coding: utf-8 -*-
import json, math, os, sys

def _polar(r, a):
    return (r * math.cos(a), r * math.sin(a))

def _tooth_points(m, z, alpha=20.0, ha_star=1.0, c_star=0.25, x=0.0,
                  beta=0.0, b=0.0):
    rp = m * z / 2.0
    ra = rp + m * (ha_star + x)
    rf = max(0.1, rp - m * (ha_star + c_star - x))
    pitch = 2 * math.pi / z
    a = math.radians(alpha)
    tooth_half = math.pi / (2 * z) + 2 * x * math.tan(a) / z
    tooth_half = max(0.05 * pitch, min(0.42 * pitch, tooth_half))
    tip_half = tooth_half * 0.55
    pts = []
    for i in range(z):
        c = i * pitch
        pts.extend([
            _polar(rf, c - pitch * 0.42), _polar(rf, c - pitch * 0.30),
            _polar(rp, c - tooth_half), _polar(ra, c - tip_half),
            _polar(ra, c + tip_half), _polar(rp, c + tooth_half),
            _polar(rf, c + pitch * 0.30), _polar(rf, c + pitch * 0.42)])
    if b and beta:
        tw = b * math.tan(math.radians(beta)) / rp
        cc, ss = math.cos(tw), math.sin(tw)
        pts = [(px * cc - py * ss, px * ss + py * cc) for px, py in pts]
    return pts

def build(mode, p, path):
    import cadquery as cq
    m = float(p.get('m') or p.get('mn') or 3)
    z = int(p.get('z') or 20)
    b = float(p.get('b') or 20)
    bore = float(p.get('bore') or 0)
    alpha = float(p.get('alpha') or 20)
    beta = float(p.get('beta') or 0)
    x = float(p.get('x') or 0)
    ha = float(p.get('ha_star') or p.get('ha') or 1.0)
    cs = float(p.get('c_star') or 0.25)
    pts1 = _tooth_points(m, z, alpha, ha, cs, x, beta, 0)
    if (mode or 'spur').lower() == 'helical':
        pts2 = _tooth_points(m, z, alpha, ha, cs, x, beta, b)
        w1 = cq.Workplane('XY').polyline(pts1).close().wire().val()
        w2 = (cq.Workplane('XY').polyline(pts2).close()
              .translate((0, 0, b)).wire().val())
        solid = cq.Workplane('XY').add(cq.Solid.makeLoft([w1, w2], ruled=True))
    else:
        solid = cq.Workplane('XY').polyline(pts1).close().extrude(b)
    if bore > 0:
        cutter = (cq.Workplane('XY').circle(bore / 2.0)
                  .extrude(b + 2).translate((0, 0, -1)))
        solid = solid.cut(cutter)
    cq.exporters.export(solid, path)
    if not os.path.exists(path) or os.path.getsize(path) <= 0:
        raise RuntimeError('STEP file not generated')
    return path

def main():
    if len(sys.argv) != 2:
        print('usage: worker <json>', file=sys.stderr)
        return 2
    job = json.loads(sys.argv[1])
    path = job['path']
    try:
        build(job.get('mode', 'spur'), job.get('params') or {}, path)
        print(json.dumps({'ok': True, 'path': path,
                          'size': os.path.getsize(path)}))
        return 0
    except Exception as exc:
        print('%s: %s' % (type(exc).__name__, exc), file=sys.stderr)
        return 1

if __name__ == '__main__':
    sys.exit(main())
"""


def _worker_path():
    if os.path.exists(WORKER):
        return WORKER
    folder = tempfile.mkdtemp(prefix='flange_gear_')
    path = os.path.join(folder, 'flange_gear_worker.py')
    with open(path, 'w', encoding='utf-8') as fh:
        fh.write(_WORKER_SOURCE)
    return path


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKER = os.path.join(ROOT, 'core', 'cadquery_gear_worker.py')


def _candidates():
    env = os.environ.get('FLANGE_CADQUERY_PYTHON')
    if env:
        yield env
    bases = [ROOT, os.path.dirname(ROOT),
             os.path.dirname(os.path.abspath(sys.executable))]
    seen = set()
    for base in bases:
        path = os.path.join(base, '_cadquery_env', 'Scripts', 'python.exe')
        if path not in seen:
            seen.add(path)
            yield path


def _clean_env():
    env = dict(os.environ)
    for key in ('PYTHONPATH', 'PYTHONHOME', 'QT_PLUGIN_PATH',
                'QT_QPA_PLATFORM'):
        env.pop(key, None)
    env['PYTHONIOENCODING'] = 'utf-8'
    env['PYTHONNOUSERSITE'] = '1'
    return env


def find_python(verify=True):
    """返回可用的 CadQuery/OCP Python 路径，找不到返回 None。"""
    for path in _candidates():
        if path and os.path.exists(path):
            if not verify:
                return path
            try:
                result = subprocess.run(
                    [path, '-c', 'import cadquery, OCP; print("ok")'],
                    capture_output=True, text=True, timeout=120,
                    env=_clean_env())
                if result.returncode == 0 and 'ok' in result.stdout:
                    return path
            except (OSError, subprocess.TimeoutExpired):
                pass
    return None


def _polar(r, angle):
    return (r * math.cos(angle), r * math.sin(angle))


def _tooth_points(m, z, alpha=20.0, ha_star=1.0, c_star=0.25, x=0.0,
                  beta=0.0, b=0.0):
    """近似渐开线齿形的闭合多边形点。"""
    rp = m * z / 2.0
    ra = rp + m * (ha_star + x)
    rf = max(0.1, rp - m * (ha_star + c_star - x))
    pitch = 2 * math.pi / z
    a = math.radians(alpha)
    tooth_half = math.pi / (2 * z) + 2 * x * math.tan(a) / z
    tooth_half = max(0.05 * pitch, min(0.42 * pitch, tooth_half))
    tip_half = tooth_half * 0.55
    pts = []
    for i in range(z):
        center = i * pitch
        pts.extend([
            _polar(rf, center - pitch * 0.42),
            _polar(rf, center - pitch * 0.30),
            _polar(rp, center - tooth_half),
            _polar(ra, center - tip_half),
            _polar(ra, center + tip_half),
            _polar(rp, center + tooth_half),
            _polar(rf, center + pitch * 0.30),
            _polar(rf, center + pitch * 0.42),
        ])
    if b and beta:
        twist = b * math.tan(math.radians(beta)) / rp
        c, s = math.cos(twist), math.sin(twist)
        pts = [(px * c - py * s, px * s + py * c) for px, py in pts]
    return pts


def _build(mode, p, path):
    """在 CadQuery 解释器中建模并导出 STEP。"""
    import cadquery as cq

    mode = (mode or 'spur').lower()
    m = float(p.get('m') or p.get('mn') or 3)
    z = int(p.get('z') or 20)
    b = float(p.get('b') or 20)
    bore = float(p.get('bore') or 0)
    alpha = float(p.get('alpha') or 20)
    beta = float(p.get('beta') or 0)
    x = float(p.get('x') or 0)
    ha = float(p.get('ha_star') or p.get('ha') or 1.0)
    cstar = float(p.get('c_star') or 0.25)

    pts1 = _tooth_points(m, z, alpha, ha, cstar, x, beta, 0)
    if mode == 'helical':
        pts2 = _tooth_points(m, z, alpha, ha, cstar, x, beta, b)
        w1 = cq.Workplane('XY').polyline(pts1).close().wire().val()
        w2 = (cq.Workplane('XY').polyline(pts2).close()
              .translate((0, 0, b)).wire().val())
        solid = cq.Solid.makeLoft([w1, w2], ruled=True)
        solid = cq.Workplane('XY').add(solid)
    else:
        solid = cq.Workplane('XY').polyline(pts1).close().extrude(b)

    if bore > 0:
        cutter = (cq.Workplane('XY').circle(bore / 2.0)
                  .extrude(b + 2).translate((0, 0, -1)))
        solid = solid.cut(cutter)

    cq.exporters.export(solid, path)
    if not os.path.exists(path) or os.path.getsize(path) <= 0:
        raise RuntimeError('STEP 文件未生成')
    return path


def generate(mode, params, path):
    """生成 STEP；自动选择本机可用的 CadQuery 解释器。"""
    python = find_python(False)
    if not python:
        raise RuntimeError('未找到 CadQuery/OCP 解释器，请设置 '
                           'FLANGE_CADQUERY_PYTHON 或安装 _cadquery_env')
    worker = _worker_path()
    payload = json.dumps({'mode': mode, 'params': params, 'path': path},
                         ensure_ascii=False)
    result = subprocess.run(
        [python, worker, payload], capture_output=True, text=True,
        encoding='utf-8', errors='replace', timeout=300,
        env=_clean_env())
    if result.returncode != 0 or not os.path.exists(path):
        detail = (result.stderr or result.stdout or '').strip()[-500:]
        raise RuntimeError('STP 生成失败：%s' % (detail or '无输出'))
    return path
