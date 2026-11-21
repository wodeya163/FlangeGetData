# -*- coding: utf-8 -*-
"""GB/T 17395-2024 数据生成器：从 gbt_2024.json（PDF 网格提取产物）生成 3 个钢管 CSV。

数据来源：GB/T 17395-2024《无缝钢管尺寸、外形、重量及允许偏差》正式 PDF。
  表1 普通钢管 S<=65mm (PDF p8-28)  + 表2 普通钢管 S>65mm (p29-30)
  表3 精密钢管 (p31-34)
  表4 不锈钢管 (p35-43, 点阵)

【长表（tidy）格式】每个 (外径 × 壁厚) 组合一行，便于按「公称直径 / 外径 / 壁厚」
三维条件检索，并直接列出每米重量：
    普通钢管  → Data/GB17395_普通钢管.csv
        列：DN, DN2, D_o, 系列, 壁厚S(mm), 每米重量(kg/m)
    精密钢管  → Data/GB17395_精密钢管.csv
        列：DN, DN2, D_o, 壁厚S(mm), 每米重量(kg/m)
    不锈钢管  → Data/GB17395_不锈钢管.csv
        列：DN, DN2, D_o, 系列, 壁厚S(mm), 每米重量(kg/m), 标准尺寸

理论重量按标准式(1)：W = 0.0246615 × (D − S) × S（密度 7.85 g/cm³），
W<1 保留 3 位小数、W>=1 保留 2 位，修约按 GB/T 8170（四舍六入五留双），
与标准表列印刷值一致，已抽查验证。
D/S 均取括号外数值（标准表注：重量按括号外公称外径与公称壁厚计算）。
不锈钢管标准表4 仅给出 ● 尺寸可用性、不列重量，此处按同一几何公式补算理论重量，
并以「标准尺寸」列保留原 ● 标记。

DN / DN2（NPS）为辅助检索列，按 GB/T 1047 / HG/T 20553 A(B) 系惯例映射，
标准原文无此两列；精密钢管为机械/锅炉用定径管，不标注 系列。

系列归属：以表1 的 3 子列网格检测为准（跨页一致、符合 ISO 4200），
表2 的系列检测因网格错位有误，不参与系列判定；表4 不锈钢的系列以表4 自身检测为准。
"""
import csv
import json
import re
from decimal import Decimal, ROUND_HALF_EVEN

# DN 映射（键 = 外径数值，括号外/括号内均可命中）
DN_MAP = {
    # A 系列（ISO 4200 / 英寸系）
    10.2: '6', 17.2: '10', 21.3: '15', 26.9: '20', 33.7: '25', 42.4: '32',
    48.3: '40', 60.3: '50', 76.1: '65', 88.9: '80', 114.3: '100', 139.7: '125',
    168.3: '150', 219.1: '200', 273.1: '250', 323.9: '300', 355.6: '350',
    406.4: '400', 457: '450', 508: '500', 559: '550', 610: '600', 660: '650',
    711: '700', 762: '750', 813: '800', 914: '900', 1016: '1000', 1067: '1050',
    1118: '1100', 1219: '1200', 1321: '1300', 1422: '1400', 1524: '1500',
    1626: '1600', 1829: '1800', 2032: '2000', 2540: '2500',
    # B 系列（括号外即 B 值者，及常见 B 系小数）
    12: '8', 12.7: '8', 13.5: '10', 14: '10', 18: '15', 25: '20', 31.8: '25',
    32: '25', 38: '32', 44.5: '40', 45: '40', 57: '50', 73: '65', 82.5: '65',
    108: '100', 133: '125', 141.3: '125', 152.4: '150', 159: '150', 180: '175',
    193.7: '200', 219: '200', 244.5: '200', 267.4: '250', 273: '250', 298.5: '300',
    299: '300', 323.9: '300', 325: '300', 339.7: '350', 351: '350', 355.6: '350',
    377: '350', 398: '400', 426: '400', 450: '400', 473: '450', 480: '450',
    500: '500', 530: '500', 558.8: '500', 559: '500', 630: '600', 720: '700',
    788.5: '700', 2020: '2000',
}
DN2_MAP = {'6': '1/8', '10': '3/8', '15': '1/2', '20': '3/4', '25': '1',
           '32': '1 1/4', '40': '1 1/2', '50': '2', '65': '2 1/2', '80': '3',
           '100': '4', '125': '5', '150': '6', '175': '7', '200': '8',
           '250': '10', '300': '12', '350': '14', '400': '16', '450': '18',
           '500': '20', '550': '22', '600': '24', '650': '26', '700': '28',
           '750': '30', '800': '32', '900': '36', '1000': '40', '1050': '42',
           '1100': '44', '1200': '48', '1300': '52', '1400': '56',
           '1500': '60', '1600': '64', '1800': '72', '2000': '80',
           '2500': '100'}

SERIES_COLS = ['系列1', '系列2', '系列3']
K = Decimal('0.0246615')


def od_nums(od):
    """OD 原文字符串 → 全部数值（括号外在前）。"""
    return [float(x) for x in re.findall(r'\d+(?:\.\d+)?', od)]


def od_outer(od):
    """括号外公称外径（重量计算用）。"""
    return float(od.split('(')[0])


def fmt_do(do):
    """外径显示字符串：整数去小数点，否则去尾零。"""
    if do == int(do):
        return str(int(do))
    return ('%.4f' % do).rstrip('0').rstrip('.')


def weight(D, S):
    # 重量修约按 GB/T 8170（四舍六入五留双，即 round-half-to-even），
    # 与 GB/T 17395 表列印刷值一致。
    w = K * (Decimal(str(D)) - Decimal(str(S))) * Decimal(str(S))
    if w < 1:
        return str(w.quantize(Decimal('0.001'), rounding=ROUND_HALF_EVEN))
    return str(w.quantize(Decimal('0.01'), rounding=ROUND_HALF_EVEN))


def dn_of(od):
    # 同时兼容 int / float 键（DN_MAP 混用两种键，OD 数值可能为 660.0）
    for x in od_nums(od):
        if x in DN_MAP:
            return DN_MAP[x]
        if int(x) in DN_MAP:
            return DN_MAP[int(x)]
    return ''


def od_order(tabs):
    """合并多表的 OD 行序（以 tabs[0] 为主，补入其余表独有 OD）。"""
    tab0 = TABLES[str(tabs[0])]
    order = list(tab0['order'])
    for t in tabs[1:]:
        for od in TABLES[str(t)]['order']:
            if od not in tab0['data'] and od not in order:
                order.append(od)
    return order


def s_union(od, tabs):
    """该 OD 在所有表中的 S 键并集（数值升序）。"""
    s = set()
    for t in tabs:
        mp = TABLES[str(t)]['data'].get(od)
        if mp:
            s |= set(mp)
    return sorted(s, key=float)


def write_long(fn, tabs, with_series, with_dn, stainless=False):
    """输出长表：每行 = (外径 × 壁厚)，含 壁厚S 与 每米重量。

    列：DN, DN2, D_o, [系列], 壁厚S(mm), 每米重量(kg/m), [标准尺寸]
    系列仅以 tabs[0] 的 series 判定（普通=表1；不锈钢=表4；精密无 series）。
    """
    tab0 = TABLES[str(tabs[0])]
    cols = (['DN', 'DN2', 'D_o'] if with_dn else ['D_o']) \
        + (['系列'] if with_series else []) \
        + ['壁厚S(mm)', '每米重量(kg/m)'] \
        + (['标准尺寸'] if stainless else [])
    n = 0
    with open(fn, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f)
        w.writerow(cols)
        for od in od_order(tabs):
            do = od_outer(od)
            dn = dn_of(od) if with_dn else ''
            dn2 = DN2_MAP.get(dn, '') if with_dn else ''
            si = tab0['series'].get(od)
            ser = SERIES_COLS[si] if (with_series and si is not None
                                      and si < len(SERIES_COLS)) else ''
            for s in s_union(od, tabs):
                row = []
                if with_dn:
                    row += [dn, dn2, fmt_do(do)]
                else:
                    row += [fmt_do(do)]
                if with_series:
                    row += [ser]
                row += [s, weight(do, s)]
                if stainless:
                    row += ['●']
                w.writerow(row)
                n += 1
    print(fn, '->', n, '行 ×', len(cols), '列')


if __name__ == '__main__':
    TABLES = json.load(open('gbt_2024.json', encoding='utf-8'))
    write_long('Data/GB17395_普通钢管.csv', [1, 2], with_series=True,
               with_dn=True, stainless=False)
    write_long('Data/GB17395_精密钢管.csv', [3], with_series=False,
               with_dn=True, stainless=False)
    write_long('Data/GB17395_不锈钢管.csv', [4], with_series=True,
               with_dn=True, stainless=True)
