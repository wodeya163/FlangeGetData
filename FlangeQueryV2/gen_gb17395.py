# -*- coding: utf-8 -*-
"""重建 GB17395_钢管系列.csv —— 按 ASME B36.10M / GB/T 17395 外径系列1 + 标准壁厚系列。

数据源（交叉核对，2026-10-20）：
- steelbrisk.com ASME B36.10M 外径/壁厚总表（最完整，NPS 1/2–48″ 全系列，主表）
- mlc.org.uk Pipe Schedules Chart（碳钢，NPS 1/2–24″ 校核）
- tuspipe.com Pipe Thickness Chart（含 Sch5s/10s/20s/40s/80s 不锈钢系列校核）

核心规则：
- 外径 D_o 取 GB/T 17395 外径系列1（与程序原值一致：21.3/26.9/…/559/610/660…）。
- Sch40s ≡ STD、Sch80s ≡ XS（名义壁厚一致，由脚本推导）。
- Sch5s/Sch10s 为 B36.19M 不锈钢薄壁系列（仅小口径有定义）。
- 大口径（NPS≥26）重壁厚 Sch40~Sch160 在权威表中本就空缺，留空待正式标准 PDF 复核。
- 壁厚保留 2 位小数精度（如 19.05、15.88），不再粗暴四舍五入到 0.1。

列顺序与 main.py _SCH_ORDER 对齐（去掉 LG，LG 经核实为 Sch10 误标）。
注意：Sch20s 沿用旧文件数值（未经 B36.19M 核验），如用于精确选型请另行校核。
"""
import csv
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, 'Data')

# 壁厚列顺序（与 main.py _SCH_ORDER 对齐，去掉 LG）
WALL_COLS = ['Sch5s', 'Sch10s', 'Sch20s', 'Sch10', 'Sch20', 'Sch30', 'Sch40s',
             'Sch40', 'STD', 'Sch60', 'Sch80s', 'Sch80', 'XS', 'Sch100',
             'Sch120', 'Sch140', 'Sch160', 'XXS']

# DN -> (NPS字符串, D_o系列1, 外径B系列2, {壁厚列: 值或None})
# 仅列出有值的列；Sch40s/Sch80s 由脚本按 STD/XS 推导。
# Sch20s 为旧文件沿用值（未核验）。
ROWS = [
    (15,  '1/2"',  21.3, 18,   dict(Sch5s=1.65, Sch10s=2.11, Sch20s=2.6, Sch40=2.77, Sch80=3.73, Sch160=4.78, XXS=7.47, STD=2.77, XS=3.73)),
    (20,  '3/4"',  26.9, 25,   dict(Sch5s=1.65, Sch10s=2.11, Sch20s=2.6, Sch40=2.87, Sch80=3.91, Sch160=5.56, XXS=7.82, STD=2.87, XS=3.91)),
    (25,  '1"',    33.7, 32,   dict(Sch5s=1.65, Sch10s=2.77, Sch20s=3.2, Sch40=3.38, Sch80=4.55, Sch160=6.35, XXS=9.09, STD=3.38, XS=4.55)),
    (32,  '1-1/4"',42.4, 38,   dict(Sch5s=1.65, Sch10s=2.77, Sch20s=3.2, Sch40=3.56, Sch80=4.85, Sch160=6.35, XXS=9.70, STD=3.56, XS=4.85)),
    (40,  '1-1/2"',48.3, 45,   dict(Sch5s=1.65, Sch10s=2.77, Sch20s=3.2, Sch40=3.68, Sch80=5.08, Sch160=7.14, XXS=10.15, STD=3.68, XS=5.08)),
    (50,  '2"',    60.3, 57,   dict(Sch5s=1.65, Sch10s=2.77, Sch20s=3.6, Sch40=3.91, Sch80=5.54, Sch160=8.74, XXS=11.07, STD=3.91, XS=5.54)),
    (65,  '2-1/2"',76.1, 76,   dict(Sch5s=2.11, Sch10s=3.05, Sch20s=3.6, Sch40=5.16, Sch80=7.01, Sch160=9.53, XXS=14.02, STD=5.16, XS=7.01)),
    (80,  '3"',    88.9, 89,   dict(Sch5s=2.11, Sch10s=3.05, Sch20s=4.0, Sch40=5.49, Sch80=7.62, Sch160=11.13, XXS=15.24, STD=5.49, XS=7.62)),
    (90,  '3-1/2"',101.6,None, dict(Sch5s=2.11, Sch10s=3.05, Sch20s=4.0, Sch40=5.74, Sch80=8.08, STD=5.74, XS=8.08)),
    (100, '4"',    114.3,108,  dict(Sch5s=2.11, Sch10s=3.05, Sch20s=4.0, Sch40=6.02, Sch80=8.56, Sch120=11.13, Sch160=13.49, XXS=17.12, STD=6.02, XS=8.56)),
    (125, '5"',    139.7,133,  dict(Sch5s=2.77, Sch10s=3.40, Sch20s=5.0, Sch40=6.55, Sch80=9.53, Sch120=12.70, Sch160=15.88, XXS=19.05, STD=6.55, XS=9.53)),
    (150, '6"',    168.3,159,  dict(Sch5s=2.77, Sch10s=3.40, Sch20s=5.0, Sch40=7.11, Sch80=10.97, Sch120=14.27, Sch160=18.26, XXS=21.95, STD=7.11, XS=10.97)),
    (200, '8"',    219.1,219,  dict(Sch5s=2.77, Sch10s=3.76, Sch20s=6.3, Sch20=6.35, Sch30=7.04, Sch40=8.18, Sch60=10.31, Sch80=12.70, Sch100=15.09, Sch120=18.26, Sch140=20.62, Sch160=23.01, XXS=22.23, STD=8.18, XS=12.70)),
    (250, '10"',   273.0,273,  dict(Sch5s=3.40, Sch10s=4.19, Sch20s=6.3, Sch20=6.35, Sch30=7.80, Sch40=9.27, Sch60=12.70, Sch80=15.09, Sch100=18.26, Sch120=21.44, Sch140=25.40, Sch160=28.58, XXS=25.40, STD=9.27, XS=12.70)),
    (300, '12"',   323.9,325,  dict(Sch5s=3.96, Sch10s=4.57, Sch20s=6.3, Sch20=6.35, Sch30=8.38, Sch40=10.31, Sch60=14.27, Sch80=17.48, Sch100=21.44, Sch120=25.40, Sch140=28.58, Sch160=33.32, XXS=25.40, STD=9.53, XS=12.70)),
    (350, '14"',   355.6,377,  dict(Sch5s=3.96, Sch10s=4.78, Sch20s=8.0, Sch10=6.35, Sch20=7.92, Sch30=9.53, Sch40=11.13, Sch60=15.09, Sch80=19.05, Sch100=23.83, Sch120=27.79, Sch140=31.75, Sch160=35.71, STD=9.53, XS=12.70)),
    (400, '16"',   406.4,426,  dict(Sch5s=4.19, Sch10s=4.78, Sch20s=8.0, Sch10=6.35, Sch20=7.92, Sch30=9.53, Sch40=12.70, Sch60=16.66, Sch80=21.44, Sch100=26.19, Sch120=30.96, Sch140=36.53, Sch160=40.49, STD=9.53, XS=12.70)),
    (450, '18"',   457.2,478,  dict(Sch5s=4.19, Sch10s=4.78, Sch20s=8.0, Sch10=6.35, Sch20=7.92, Sch30=11.13, Sch40=14.27, Sch60=19.05, Sch80=23.83, Sch100=29.36, Sch120=34.96, Sch140=39.67, Sch160=45.24, STD=9.53, XS=12.70)),
    (500, '20"',   508.0,529,  dict(Sch5s=4.78, Sch10s=5.54, Sch20s=8.0, Sch10=6.35, Sch20=9.53, Sch30=12.70, Sch40=15.09, Sch60=20.62, Sch80=26.19, Sch100=32.54, Sch120=38.10, Sch140=44.45, Sch160=50.01, STD=9.53, XS=12.70)),
    (550, '22"',   559, None,  dict(Sch5s=4.78, Sch10s=5.54, Sch20s=8.0, Sch10=6.35, Sch20=9.53, Sch30=12.70, Sch40=None, Sch60=22.23, Sch80=28.58, Sch100=34.93, Sch120=41.28, Sch140=47.63, Sch160=53.98, STD=9.53, XS=12.70)),
    (600, '24"',   610, 630,   dict(Sch5s=5.54, Sch10s=6.35, Sch20s=8.0, Sch10=6.35, Sch20=9.53, Sch30=14.27, Sch40=17.48, Sch60=24.61, Sch80=30.96, Sch100=38.89, Sch120=46.02, Sch140=52.37, Sch160=59.54, STD=9.53, XS=12.70)),
    # NPS 26–48：仅填权威表定义的 Sch10 / Sch20 / Sch30 / STD(9.53) / XS(12.70)；
    # 重壁厚 Sch40~Sch160 在权威表中本就空缺，留空待正式标准 PDF 复核。
    (650, '26"',   660, None,  dict(Sch5s=5.54, Sch10s=6.35, Sch20s=8.0, Sch10=7.92, Sch20=12.70, STD=9.53, XS=12.70)),
    (700, '28"',   711, 720,   dict(Sch5s=5.54, Sch10s=6.35, Sch20s=8.0, Sch10=7.92, Sch20=12.70, Sch30=15.88, Sch40=None, STD=9.53, XS=12.70)),
    (750, '30"',   762, None,  dict(Sch5s=5.54, Sch10s=6.35, Sch20s=8.0, Sch10=7.92, Sch20=12.70, Sch30=15.88, Sch40=None, STD=9.53, XS=12.70)),
    (800, '32"',   813, 820,   dict(Sch5s=5.54, Sch10s=6.35, Sch20s=8.0, Sch10=7.92, Sch20=12.70, Sch30=15.88, Sch40=17.48, STD=9.53, XS=12.70)),
    (850, '34"',   864, None,  dict(Sch5s=5.54, Sch10s=6.35, Sch20s=8.0, Sch10=7.92, Sch20=12.70, Sch30=15.88, Sch40=17.48, STD=9.53, XS=12.70)),
    (900, '36"',   914, 920,   dict(Sch5s=5.54, Sch10s=6.35, Sch20s=8.0, Sch10=7.92, Sch20=12.70, Sch30=15.88, Sch40=17.48, STD=9.53, XS=12.70)),
    (950, '38"',   965, None,  dict(Sch5s=5.54, Sch10s=6.35, Sch20s=8.0, STD=9.53, XS=12.70)),
    (1000,'40"',   1016,1020,  dict(Sch5s=5.54, Sch10s=6.35, Sch20s=8.0, STD=9.53, XS=12.70)),
    (1050,'42"',   1067,None,  dict(Sch5s=5.54, Sch10s=6.35, Sch20s=8.0, STD=9.53, XS=12.70)),
    (1100,'44"',   1118,1120,  dict(Sch5s=5.54, Sch10s=6.35, Sch20s=8.0, STD=9.53, XS=12.70)),
    (1150,'46"',   1168,None,  dict(Sch5s=5.54, Sch10s=6.35, Sch20s=8.0, STD=9.53, XS=12.70)),
    (1200,'48"',   1219,1220,  dict(Sch5s=5.54, Sch10s=6.35, Sch20s=8.0, STD=9.53, XS=12.70)),
]


def fmt(v):
    if v is None:
        return '-'
    return ('%.2f' % v).rstrip('0').rstrip('.')


def build_rows():
    out = []
    for dn, nps, do_a, do_b, w in ROWS:
        rec = dict(w)
        # 推导 Sch40s = STD、Sch80s = XS（名义壁厚一致）
        if rec.get('STD') is not None:
            rec['Sch40s'] = rec['STD']
        if rec.get('XS') is not None:
            rec['Sch80s'] = rec['XS']
        row = [dn, nps, do_a] + [fmt(rec.get(c)) for c in WALL_COLS]
        out.append((dn, row))
    return out


def write_gb17395():
    rows = build_rows()
    p = os.path.join(DATA, 'GB17395_钢管系列.csv')
    with open(p, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f)
        w.writerow(['DN', 'DN2', 'D_o'] + WALL_COLS)
        for _, r in rows:
            w.writerow(r)
    print('GB17395_钢管系列.csv: %d 行, %d 列' % (len(rows), len(WALL_COLS) + 3))


def write_source():
    """同步更新源文件 GB12459_GBT13401.csv（LG -> Sch10，并补全壁厚列）"""
    rows = build_rows()
    p = os.path.join(DATA, 'GB12459_GBT13401.csv')
    with open(p, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f)
        w.writerow(['', 'DN', 'DN2', 'D_o_A', 'D_o_B'] + WALL_COLS)
        for i, (dn, r) in enumerate(rows):
            _, nps, do_a = r[0], r[1], r[2]
            do_b = next((b for d, _, _, b, _ in ROWS if d == dn), None)
            w.writerow([i, dn, nps, do_a, '-' if do_b is None else do_b] + r[3:])
    print('GB12459_GBT13401.csv: 源文件同步更新（LG->Sch10，%d 行）' % len(rows))


if __name__ == '__main__':
    write_gb17395()
    write_source()
