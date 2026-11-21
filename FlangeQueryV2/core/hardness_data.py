# Reconstructed from bytecode by split_decompile.py
# hardness_data.pyc

'''
硬度换算数据 — 依据 GB/T 1172-1999 原文（0.5步长完整表）
各硬度值之间的换算采用线性插值法。
'''
_TABLE = [
    (20, 226, 225),
    (20.5, 228, 227),
    (21, 230, 229),
    (21.5, 233, 232),
    (22, 235, 234),
    (22.5, 238, 237),
    (23, 241, 240),
    (23.5, 244, 242),
    (24, 247, 245),
    (24.5, 250, 248),
    (25, 253, 251),
    (25.5, 256, 254),
    (26, 259, 257),
    (26.5, 262, 260),
    (27, 266, 263),
    (27.5, 269, 266),
    (28, 273, 269),
    (28.5, 276, 273),
    (29, 280, 276),
    (29.5, 284, 280),
    (30, 288, 283),
    (30.5, 292, 287),
    (31, 296, 291),
    (31.5, 300, 294),
    (32, 304, 298),
    (32.5, 308, 302),
    (33, 313, 306),
    (33.5, 317, 310),
    (34, 321, 314),
    (34.5, 326, 318),
    (35, 331, 323),
    (35.5, 335, 327),
    (36, 340, 332),
    (36.5, 345, 336),
    (37, 350, 341),
    (37.5, 355, 345),
    (38, 360, 350),
    (38.5, 365, 355),
    (39, 371, 360),
    (39.5, 376, 365),
    (40, 381, 370),
    (40.5, 387, 375),
    (41, 393, 380),
    (41.5, 398, 385),
    (42, 404, 391),
    (42.5, 410, 396),
    (43, 416, 401),
    (43.5, 422, 407),
    (44, 428, 413),
    (44.5, 435, 418),
    (45, 441, 424),
    (45.5, 448, 430),
    (46, 454, 436),
    (46.5, 461, 442),
    (47, 468, 449),
    (47.5, 475, None),
    (48, 482, None),
    (48.5, 489, None),
    (49, 497, None),
    (49.5, 504, None),
    (50, 512, None),
    (50.5, 520, None),
    (51, 527, None),
    (51.5, 535, 527),
    (52, 544, 535),
    (52.5, 552, 544),
    (53, 561, 552),
    (53.5, 569, 561),
    (54, 578, 569),
    (54.5, 587, 577),
    (55, 596, 585),
    (55.5, 606, 593),
    (56, 615, 601),
    (56.5, 625, 608),
    (57, 635, None),
    (57.5, 645, None),
    (58, 655, None),
    (58.5, 666, None),
    (59, 676, None),
    (59.5, 687, None),
    (60, 698, None),
    (60.5, 710, None),
    (61, 722, None),
    (61.5, 734, None),
    (62, 746, None),
    (62.5, 759, None),
    (63, 772, None),
    (63.5, 785, None),
    (64, 799, None),
    (64.5, 813, None),
    (65, 827, None),
    (65.5, 842, None),
    (66, 857, None),
    (66.5, 872, None),
    (67, 888, None),
    (67.5, 904, None),
    (68, 920, None)]
_HS_TABLE = [
    (20, 41.8),
    (25, 44.7),
    (30, 47.8),
    (35, 51.4),
    (40, 55.7),
    (45, 61.1),
    (50, 67.7),
    (55, 75.7),
    (60, 85.7)]

def _interpolate(table, key_idx, target_idx, value):
    '''在 table 上按 key_idx 列做线性插值，返回 target_idx 列的值。
    table 按 key_idx 升序排列。'''
    if not table:
        return None
    if value < table[0][key_idx] or value > table[-1][key_idx]:
        return None
    for i in range(len(table) - 1):
        v0 = table[i][key_idx]
        v1 = table[i + 1][key_idx]
        if v0 <= value <= v1:
            t = (value - v0) / (v1 - v0) if v1 != v0 else 0
            y0 = table[i][target_idx]
            y1 = table[i + 1][target_idx]
            if y0 is None or y1 is None:
                return None
            return y0 + t * (y1 - y0)
    return None


def _hrc_from_table(table, key_idx, value):
    '''从其他硬度值反推 HRC，过滤 None'''
    filtered = [row for row in table if row[key_idx] is not None]
    if not filtered:
        return None
    return _interpolate(filtered, key_idx, 0, value)


def _convert_from_hrc(hrc):
    hv = _interpolate(_TABLE, 0, 1, hrc)
    hb = _interpolate(_TABLE, 0, 2, hrc)
    hs = _interpolate(_HS_TABLE, 0, 1, hrc)
    return {
        'HRC': hrc,
        'HV': hv,
        'HBW': hb,
        'HS': hs }
def _convert_from_hv(hv):
    hrc = _hrc_from_table(_TABLE, 1, hv)
    if hrc is None:
        return {
            'HRC': None,
            'HV': hv,
            'HBW': None,
            'HS': None }
    hb = _interpolate(_TABLE, 0, 2, hrc)
    hs = _interpolate(_HS_TABLE, 0, 1, hrc)
    return {
        'HRC': hrc,
        'HV': hv,
        'HBW': hb,
        'HS': hs }
def _convert_from_hbw(hbw):
    hrc = _hrc_from_table(_TABLE, 2, hbw)
    if hrc is None:
        return {
            'HRC': None,
            'HV': None,
            'HBW': hbw,
            'HS': None }
    hv = _interpolate(_TABLE, 0, 1, hrc)
    hs = _interpolate(_HS_TABLE, 0, 1, hrc)
    return {
        'HRC': hrc,
        'HV': hv,
        'HBW': hbw,
        'HS': hs }
def _convert_from_hs(hs):
    hrc = _hrc_from_table(_HS_TABLE, 1, hs)
    if hrc is None:
        return {
            'HRC': None,
            'HV': None,
            'HBW': None,
            'HS': hs }
    hv = _interpolate(_TABLE, 0, 1, hrc)
    hb = _interpolate(_TABLE, 0, 2, hrc)
    return {
        'HRC': hrc,
        'HV': hv,
        'HBW': hb,
        'HS': hs }
def convert(value, source_type):
    '''
    硬度换算入口
    :param value: 输入值（float）
    :param source_type: 硬度类型 "HRC"/"HV"/"HBW"/"HS"
    :return: dict {"HRC": float|None, "HV": float|None, "HBW": float|None, "HS": float|None}
    '''
    if value is None:
        return {
            'HRC': None,
            'HV': None,
            'HBW': None,
            'HS': None }
    (lo, hi) = RANGES.get(source_type, (0, 0))
    if value < lo or value > hi:
        return {
            'HRC': None,
            'HV': None,
            'HBW': None,
            'HS': None }
    converters = {
        'HRC': _convert_from_hrc,
        'HV': _convert_from_hv,
        'HBW': _convert_from_hbw,
        'HS': _convert_from_hs }
    return converters[source_type](value)
RANGES = {
    'HRC': (20, 67),
    'HV': (226, 920),
    'HBW': (225, 601),
    'HS': (41.8, 85.7) }
NAMES = {
    'HRC': '洛氏硬度 (HRC)',
    'HV': '维氏硬度 (HV)',
    'HBW': '布氏硬度 (HBW)',
    'HS': '肖氏硬度 (HS)' }
