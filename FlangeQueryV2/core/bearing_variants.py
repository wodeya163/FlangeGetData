# -*- coding: utf-8 -*-
"""轴承变体速查：密封、材料、游隙与常见后缀。"""

from core.bearing_data_table import DEEP_GROOVE

SEAL_TYPES = [
    ('开式', '无密封件，需外部供油/脂（油浴、集中润滑），承载能力不打折',
     1, '齿轮箱、有润滑系统的场合；不防尘防水，脏环境别用'),
    ('ZZ 铁封（防尘盖）', '双侧钢板防尘盖，非接触不摩擦，出厂已填脂免维护',
     1, '电机、风机等一般机械；防粗颗粒粉尘，但防水一般；转速不降'),
    ('2RS 胶封（橡胶密封圈）',
     '双侧丁腈橡胶接触唇封，出厂填脂，防尘防水最佳；摩擦略大、温升略高',
     0.6, '水泵、农机、户外潮湿/泥水/粉尘场合；极限转速约为开式的 6 成'),
]
MATERIALS = [
    ('轴承钢（GCr15）', '最常用，淬硬 HRC 60~64，承载与性价比最优',
     '一般工况首选'),
    ('不锈钢（如 440C）', '耐腐蚀、耐水汽/弱酸碱，同型号承载略低于轴承钢',
     '潮湿、食品、化工、需经常清洗的场合'),
    ('陶瓷混合（钢圈+氮化硅球）',
     '球更轻更硬、允许更高转速、电绝缘、寿命长，价格高',
     '高速主轴、防电蚀（变频电机）、极端工况'),
]
CLEARANCES = [
    ('C2（小游隙）', '径向游隙 1~11 µm，比标准小',
     '精密定位、有预紧的场合；高温会胀死，别用'),
    ('CN（标准游隙）', '径向游隙 5~20 µm，无后缀即 CN',
     '绝大多数常温场合的默认选择'),
    ('C3（大游隙）', '径向游隙 13~28 µm，比标准大',
     '持续高温（>60~70°C）、内圈配合较紧、温差大的轴；防热膨胀卡死'),
]
SUFFIX_NOTES = (
    '其他常见后缀：N/NR=外圈带止动槽/止动环（轴向定位用）；'
    '2RSL/LL=低摩擦橡胶封（转速约开式 7 成）；M=黄铜保持架（更高转速）；'
    '同一型号还可叠加游隙后缀（如 6205-2RS/C3）')


def variant_guide(code):
    """返回指定型号的密封/材料/游隙说明和组合示例。"""
    spec = DEEP_GROOVE.get(code)
    if not spec:
        return None
    d, D, B, cr, c0, ng, no = spec[:7]
    seals = []
    for name, feat, factor, scene in SEAL_TYPES:
        rpm = ('极限转速约 %s rpm（脂）' % format(int(ng * factor), ',')
               if factor < 1 else '极限转速不降')
        seals.append('<b>%s</b>：%s；%s<br><span style="color:#667085">%s</span>'
                     % (name, feat, rpm, scene))
    materials = ['<b>%s</b>：%s<br><span style="color:#667085">%s</span>'
                 % (n, f, s) for n, f, s in MATERIALS]
    clearances = ['<b>%s</b>：%s<br><span style="color:#667085">%s</span>'
                  % (n, f, s) for n, f, s in CLEARANCES]
    examples = [
        '%s（开式，默认 CN 游隙）' % code,
        '%s-ZZ（双侧铁封，免维护）' % code,
        '%s-2RS/C3（胶封 + 大游隙，湿热/高温）' % code,
    ]
    return {
        'dims': (d, D, B, cr, c0, ng, no),
        'seals': seals,
        'materials': materials,
        'clearances': clearances,
        'suffix': SUFFIX_NOTES,
        'examples': examples,
    }
