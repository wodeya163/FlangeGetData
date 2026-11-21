# Reconstructed from bytecode by split_decompile.py
# bearing_data.pyc

'''
BearingTool V1.0 测试版 数据层
├─ BEARING_TYPES   轴承类型知识库（场合匹配的依据，教材级常识）
├─ DEEP_GROOVE     深沟球轴承型号底账（6000/6200/6300 系列，联网多源交叉验证）
└─ 选型/校核计算   当量动载荷 → L10h；反向选型

数据来源说明：
- 尺寸/额定载荷按 ISO 15 / GB/T 276 系列约定；Cr/C0r/极限转速为 2026-09-28 联网
  多家厂商目录交叉验证（DRB/JUNC/SKONN/华轴网等 3~5 家取一致值），各家 ±2% 内
  略有出入，**最终以所选厂家样本为准**。
- 类型知识库为机械设计通用教材常识（承载/转速/调心等定性分级）；角度/区间等数值
  标注 ≈ 表示约数。本文件不含任何第三方版权资料原文。
'''
VERSION = 'V1.0测试版'
BEARING_TYPES = [
    dict(key = 'deep_groove', name = '深沟球轴承', gb = 'GB/T 276 (60000 型)', radial = 3, axial = 2, speed = 5, align = 0.0, rigid = 2, impact = 2, price = 1, scene = [
        '电机、水泵、风机、家电等通用机械',
        '汽车变速箱、轮端（轻型）',
        '转速较高、载荷以径向为主 + 少量双向轴向',
        '要求低摩擦、低噪音、免维护（带密封圈）'], avoid = [
        '纯轴向大载荷',
        '重载冲击',
        '轴弯曲/跨距大需要调心的场合'], note = '最通用的轴承：结构简单、可高速、价格低；带 2RS 密封噪声低但极限转速降 ~30%（≈）'),
    dict(key = 'angular_contact', name = '角接触球轴承', gb = 'GB/T 292 (70000C/AC/B 型)', paired = True, radial = 3, axial = 4, speed = 5, align = 0.0, rigid = 4, impact = 2, price = 2, scene = [
        '机床主轴、蜗轮减速机、泵类',
        '径向 + 单向较大轴向联合载荷',
        '需要预紧提高刚性的精密场合'], avoid = [
        '单独承受纯轴向悬臂载荷（应成对、面对面/背对背布置）',
        '需要调心的场合'], note = '只能承受单向轴向力，通常成对使用；接触角 15°(C)/25°(AC)/40°(B) 轴向能力递增（≈）'),
    dict(key = 'self_aligning_ball', name = '调心球轴承', gb = 'GB/T 281 (10000 型)', radial = 2, axial = 1, speed = 4, align = 2.5, rigid = 1, impact = 1, price = 2, scene = [
        '多支点传动轴、加工/装配误差导致轴线不对中',
        '细长轴挠曲变形大的场合'], avoid = [
        '重载',
        '轴向载荷为主的工况'], note = '双列钢球 + 球面外滚道，可自动调心 ≈2°~3°；承载能力低于同尺寸深沟球'),
    dict(key = 'self_aligning_roller', name = '调心滚子轴承', gb = 'GB/T 288 (20000 型)', radial = 5, axial = 3, speed = 2, align = 2.0, rigid = 5, impact = 5, price = 4, scene = [
        '重载且有冲击：破碎机、振动筛、轧机',
        '鼓风机、大型传动轴',
        '重载 + 轴线不对中并存'], avoid = [
        '高转速（滚子离心力大）',
        '轻载精密场合（大材小用）'], note = '重载首选调心轴承：调心 ≈1°~2°，径向承载在同尺寸里属最高档；价格高、极限制速低'),
    dict(key = 'cylindrical_roller', name = '圆柱滚子轴承', gb = 'GB/T 283 (N0000 型)', radial = 5, axial = 0, speed = 4, align = 0, rigid = 5, impact = 3, price = 2, scene = [
        '电机、机床主轴的纯径向支承',
        '齿轮箱中间轴（轴向由别的轴承承担）',
        '高刚性高转速的径向重载'], avoid = [
        '单独使用承受轴向力（基本不能）',
        '需要调心的场合'], note = '纯径向承载能力约为同尺寸深沟球的 1.5~2 倍（≈），滚子类里转速最高；需与止推轴承配对'),
    dict(key = 'needle', name = '滚针轴承', gb = 'GB/T 5801 (NA/HK/BK 型)', radial = 4, axial = 0, speed = 2, align = 0, rigid = 4, impact = 3, price = 1, scene = [
        '径向空间受限制的部位：连杆、万向节、液压泵',
        '摇臂、摆动机构'], avoid = [
        '轴向载荷',
        '高速（滚针摩擦大）'], note = '径向截面最小，同径向空间下承载高于滚珠；对轴颈硬度和表面质量要求高，一般不允许轴线歪斜'),
    dict(key = 'tapered_roller', name = '圆锥滚子轴承', gb = 'GB/T 297 (30000 型)', paired = True, radial = 4, axial = 4, speed = 2, align = 0, rigid = 5, impact = 4, price = 2, scene = [
        '汽车轮毂、圆锥齿轮轴（径向 + 单向大轴向）',
        '需要通过预紧控制游隙/刚性的中低速重载'], avoid = [
        '单独受双向交替轴向力（须成对安装）',
        '高转速'], note = '内外圈可分离、便于游隙调整；成对使用时轴向能力倍增，是「径向+大轴向」中速场合的性价比之选'),
    dict(key = 'thrust_ball', name = '推力球轴承', gb = 'GB/T 301 (51000 型)', radial = 0, axial = 3, speed = 1, align = 0, rigid = 2, impact = 1, price = 1, scene = [
        '低速纯轴向载荷：千斤顶、立式水泵轴端、吊钩'], avoid = [
        '径向载荷（完全不能承受）',
        '中高转速（离心力使钢球打滑）'], note = '只能承受单向轴向力，51000 单向 / 52000 双向；低速专用'),
    dict(key = 'thrust_roller', name = '推力调心滚子轴承', gb = 'GB/T 5859 (29000 型)', radial = 2, axial = 5, speed = 1, align = 2, rigid = 5, impact = 4, price = 4, scene = [
        '低速重载纯轴向：水轮机、立式电机、塔吊回转支承',
        '轴向为主 + 允许少量径向且需要调心'], avoid = [
        '高转速'], note = '球面滚道可调心 ≈2°（约），轴向承载能力在推力类里最高'),
    dict(key = 'insert', name = '带座外球面轴承', gb = 'GB/T 7809 (UC/UEL 型)', radial = 3, axial = 1, speed = 3, align = 1.5, rigid = 2, impact = 2, price = 1, scene = [
        '输送机、农机、食品包装机械等简易支承',
        '安装基面粗糙、需要自位 + 免维护（已填脂密封）'], avoid = [
        '精密传动',
        '重载冲击'], note = '外圈外径为球面可与铸座自位（≈2°），自带密封填脂，安装方便；精度和承载为一般水平'),
    dict(key = 'crossed_roller', name = '交叉滚子轴承', gb = '—（精密类，各厂企标）', radial = 4, axial = 4, speed = 2, align = 0, rigid = 5, impact = 2, price = 5, scene = [
        '机器人关节、数控转台、精密回转工作台（高刚性 + 紧凑 + 高回转精度）'], avoid = [
        '成本敏感场合',
        '高速'], note = '圆柱滚子 90° 交叉排列，一个轴承同时承受径向/轴向/倾覆力矩，刚性极高；价格最贵'),
    dict(key = 'thrust_cyl_roller', name = '推力圆柱滚子轴承', gb = 'GB/T 4663 (81000 型)', radial = 0, axial = 5, speed = 1, align = 0, rigid = 5, impact = 3, price = 3, scene = [
        '低速特重轴向载荷：起重吊钩、钻机、重型立式设备'], avoid = [
        '径向载荷',
        '转速（滚子端面滑动摩擦大，仅宜低速）'], note = '轴向承载最大的一类，但只宜低速；不允许轴线歪斜')]
DEEP_GROOVE = {
    '6000': (10, 26, 8, 4.55, 1.96, 29000, 34000),
    '6001': (12, 28, 8, 5.1, 2.39, 26000, 30000),
    '6002': (15, 32, 9, 5.6, 2.83, 22000, 26000),
    '6003': (17, 35, 10, 6.8, 3.35, 20000, 24000),
    '6004': (20, 42, 12, 9.4, 5.05, 18000, 21000),
    '6005': (25, 47, 12, 10.1, 5.85, 15000, 18000),
    '6006': (30, 55, 13, 13.2, 8.3, 13000, 15000),
    '6007': (35, 62, 14, 16.0, 10.3, 12000, 14000),
    '6008': (40, 68, 15, 16.8, 11.5, 10000, 12000),
    '6009': (45, 75, 16, 21, 15.1, 9200, 11000),
    '6010': (50, 80, 16, 21.8, 16.6, 8400, 9000),
    '6011': (55, 90, 18, 28.3, 21.2, 7700, 9000),
    '6012': (60, 95, 18, 29.5, 23.2, 7000, 8300),
    '6013': (65, 100, 18, 30.5, 25.2, 6500, 7700),
    '6014': (70, 110, 20, 38, 31, 6100, 7100),
    '6015': (75, 115, 20, 39.5, 33.5, 5700, 6700),
    '6016': (80, 125, 22, 47.5, 40, 5300, 6200),
    '6017': (85, 130, 22, 49.5, 43, 5000, 5900),
    '6018': (90, 140, 24, 58, 49.5, 4700, 5600),
    '6019': (95, 145, 24, 60.5, 54, 4500, 5300),
    '6020': (100, 150, 24, 60, 54, 4200, 5000),
    '6200': (10, 30, 9, 5.1, 2.39, 25000, 30000),
    '6201': (12, 32, 10, 6.82, 3.05, 22000, 28000),
    '6202': (15, 35, 11, 7.75, 3.6, 19000, 23000),
    '6203': (17, 40, 12, 9.6, 4.6, 18000, 21000),
    '6204': (20, 47, 14, 12.8, 6.65, 16000, 18000),
    '6205': (25, 52, 15, 14, 7.85, 13000, 15000),
    '6206': (30, 62, 16, 19.5, 11.3, 11000, 13000),
    '6207': (35, 72, 17, 25.7, 15.3, 9800, 11000),
    '6208': (40, 80, 18, 29.1, 17.8, 8700, 10000),
    '6209': (45, 85, 19, 32.5, 20.4, 7800, 9200),
    '6210': (50, 90, 20, 35, 23.2, 7100, 8300),
    '6211': (55, 100, 21, 43.5, 29.2, 6400, 7600),
    '6212': (60, 110, 22, 52.5, 36, 6000, 7000),
    '6213': (65, 120, 23, 57.5, 40, 5500, 6500),
    '6214': (70, 125, 24, 62, 44, 5100, 6000),
    '6215': (75, 130, 25, 66, 49.5, 4800, 5600),
    '6216': (80, 140, 26, 72.5, 53, 4500, 5300),
    '6217': (85, 150, 28, 83.5, 64, 4200, 5000),
    '6218': (90, 160, 30, 96, 71.5, 4000, 4700),
    '6219': (95, 170, 32, 109, 82, 3700, 4400),
    '6220': (100, 180, 34, 122, 93, 3500, 4200),
    '6300': (10, 35, 11, 8.1, 3.45, 22000, 27000),
    '6301': (12, 37, 12, 9.7, 4.2, 20000, 24000),
    '6302': (15, 42, 13, 11.4, 5.45, 17000, 21000),
    '6303': (17, 47, 14, 13.6, 6.65, 15000, 18000),
    '6304': (20, 52, 15, 15.9, 7.85, 14000, 17000),
    '6305': (25, 62, 17, 22.4, 11.5, 11000, 14000),
    '6306': (30, 72, 19, 28.1, 15.8, 9500, 12000),
    '6307': (35, 80, 21, 33.4, 19.3, 8500, 10000),
    '6308': (40, 90, 23, 40.7, 24, 7500, 9000),
    **{
        '6309': (45, 100, 25, 52.8, 31.8, 6700, 8000),
        '6310': (50, 110, 27, 61.8, 37.9, 6000, 7000),
        '6311': (55, 120, 29, 71.6, 44.8, 5300, 6300),
        '6312': (60, 130, 31, 81.8, 51.8, 5000, 6000),
        '6313': (65, 140, 33, 93.8, 60.5, 4500, 5600),
        '6314': (70, 150, 35, 105, 68, 4300, 5300),
        '6315': (75, 160, 37, 113, 77.2, 4000, 4700),
        '6316': (80, 170, 39, 123, 86.7, 3800, 4500),
        '6317': (85, 180, 41, 133, 96.8, 3600, 4200),
        '6318': (90, 190, 43, 143, 107, 3300, 3900),
        '6319': (95, 200, 45, 153, 119, 3200, 3700),
        '6320': (100, 215, 47, 173, 141, 3200, 3700) } }
_DEEP_GROOVE_XY = [
    (0.014, 0.19, 2.3),
    (0.028, 0.22, 1.99),
    (0.056, 0.26, 1.71),
    (0.084, 0.28, 1.55),
    (0.11, 0.3, 1.45),
    (0.17, 0.34, 1.31),
    (0.28, 0.38, 1.15),
    (0.42, 0.42, 1.04),
    (0.56, 0.44, 1)]

def xy_factors(fa_over_c0):
    '''按 Fa/C0r 线性插值查 (e, Y)（深沟球）。表外向下取端点。'''
    table = _DEEP_GROOVE_XY
    if fa_over_c0 <= table[0][0]:
        return (table[0][1], table[0][2])
    for i in range(len(table) - 1):
        (t0, e0, y0) = table[i]
        (t1, e1, y1) = table[i + 1]
        if fa_over_c0 <= t1:
            f = (fa_over_c0 - t0) / (t1 - t0)
            return (e0 + f * (e1 - e0), y0 + f * (y1 - y0))
    return (table[-1][1], table[-1][2])
def equivalent_load(spec, fr, fa):
    '''当量动载荷 P (kN)。spec=DEEP_GROOVE 条目, fr/fa=径向/轴向载荷 kN。'''
    (e, y) = xy_factors(fa / spec[4] if spec[4] else 0)
    if fr <= 0 and fa <= 0:
        return (0.0, e, y)
    if fr > 0 and fa / fr <= e:
        p = fr
    else:
        p = 0.56 * fr + y * fa
    return (max(p, fr), e, y)
def static_safety(spec, fr, fa):
    '''静载荷校核：P0 = 0.6Fr + 0.5Fa（P0<Fr 时取 Fr，SKF/GB 惯例），S0 = C0r/P0。
    返回 (P0 kN, S0)。载荷全零时返回 (0, inf)。'''
    p0 = 0.6 * fr + 0.5 * fa
    p0 = max(p0, fr)
    if p0 <= 0:
        return (0.0, float('inf'))
    return (p0, spec[4] / p0)
def life_hours(spec, p, rpm, lubricant = 'grease', seal_factor = 1.0):
    '''额定寿命 L10h (小时)。球轴承指数 3。返回 (L10h, 转速是否超限)。
    seal_factor: 密封形式对极限转速的折减（开式/ZZ=1.0，2RS=0.6），只影响超限判定，不改变寿命计算。'''
    (n_grease, n_oil) = (spec[5], spec[6])
    n_limit = (n_grease if lubricant == 'grease' else n_oil) * seal_factor
    over = rpm > n_limit
    if p <= 0 or rpm <= 0:
        return (float('inf'), over)
    l10_rev = (spec[3] / p) ** 3 * 1000000.0
    return (l10_rev / (60 * rpm), over)
def recommend(fr, fa, rpm, target_h, lubricant = 'grease', bore = None):
    '''反向选型：返回满足寿命与转速要求的型号列表（按外径升序）。
    bore: 指定内径(mm, None=不限制)。'''
    hits = []
    for code, spec in sorted(DEEP_GROOVE.items(), key = (lambda kv: (kv[1][1], kv[1][0]))):
        if bore is not None and spec[0] != bore:
            continue
        (p, e, y) = equivalent_load(spec, fr, fa)
        (l10, over) = life_hours(spec, p, rpm, lubricant)
        if over:
            continue
        if l10 >= target_h:
            hits.append(dict(code = code, d = spec[0], D = spec[1], B = spec[2], Cr = spec[3], C0r = spec[4], P = round(p, 2), L10h = round(l10), e = e, y = y))
    return hits
def type_guide(load = 'medium', direction = 'radial_main', speed = 'medium', need_align = False, space = 'free', impact = False):
    '''场合→类型推荐（权重打分）。返回按得分降序的类型列表。'''
    score = { }
    for t in BEARING_TYPES:
        s = 0.0
        if load == 'light':
            s += (5 - t['radial']) * 0.4 + (5 - t['price']) * 0.3
        elif load == 'heavy':
            s += t['radial'] * 1.2
        elif load == 'impact':
            s += t['impact'] * 1.5 + t['radial'] * 0.5
        else:
            s += t['radial'] * 0.8
        if direction == 'pure_radial':
            s += t['radial'] * 0.6 - abs(t['axial'] - 0) * 0.1
        elif direction == 'radial_main':
            s += t['radial'] * 0.6 + t['axial'] * 0.3
        elif direction == 'axial_main':
            s += t['axial'] * 1.2 - t['radial'] * 0.1
        else:
            s += t['axial'] * 1.5 - t['radial'] * 0.4
        s += {
            'high': t['speed'] * 1.4,
            'medium': t['speed'] * 0.5,
            'low': (5 - t['speed']) * 0.25 }[speed]
        if direction in ('radial_main', 'pure_radial') and t.get('paired'):
            s -= 1.0
        if need_align:
            s += 3.5 if t['align'] >= 1.5 else (-2.5 if t['align'] == 0 else 0.5)
        if space == 'radial_limited':
            s += 2.0 if t['key'] == 'needle' else (-0.5 if t['price'] >= 4 else 0)
        elif space == 'axial_limited':
            s += 1.0 if t['key'] in ('deep_groove', 'needle', 'cylindrical_roller') else 0
        if impact:
            s += t['impact'] * 0.8
        score[t['key']] = round(s, 2)
    ranked = sorted(BEARING_TYPES, key = (lambda t: -score[t['key']]))
    return [(t, score[t['key']]) for t in ranked[:5]]
SEAL_TYPES = [
    ('开式', '无密封件，需外部供油/脂（油浴、集中润滑），承载力道不打折', 1, '齿轮箱、有润滑系统的场合；不防尘防水，脏环境别用'),
    ('ZZ 铁封（防尘盖）', '双侧钢板防尘盖，非接触不摩擦，出厂已填脂免维护', 1, '电机、风机等一般机械；防粗颗粒粉尘，但防水一般；转速不降'),
    ('2RS 胶封（橡胶密封圈）', '双侧丁腈橡胶接触唇封，出厂填脂，防尘防水最佳；摩擦略大、温升略高', 0.6, '水泵、农机、户外潮湿/泥水/粉尘场合；极限转速约为开式的 6 成（多源 0.55~0.65，取保守 0.6）')]
MATERIALS = [
    ('轴承钢（GCr15）', '最常用，淬硬 HRC 60~64，承载与性价比最优', '一般工况首选'),
    ('不锈钢（如 440C）', '耐腐蚀、耐水汽/弱酸碱，同型号承载略低于轴承钢', '潮湿、食品、化工、需经常清洗的场合'),
    ('陶瓷混合（钢圈+氮化硅球）', '球更轻更硬、允许更高转速、电绝缘、寿命长，价格高', '高速主轴、防电蚀（变频电机）、极端工况')]
CLEARANCES = [
    ('C2（小游隙）', '径向游隙 1~11 µm，比标准小', '精密定位、有预紧的场合；高温会胀死，别用'),
    ('CN（标准游隙）', '径向游隙 5~20 µm，无后缀即 CN', '绝大多数常温场合的默认选择'),
    ('C3（大游隙）', '径向游隙 13~28 µm，比标准大', '持续高温（>60~70°C）、内圈配合较紧、温差大的轴；防热膨胀卡死')]
SUFFIX_NOTES = '其他常见后缀：N/NR=外圈带止动槽/止动环（轴向定位用）；2RSL/LL=低摩擦橡胶封（转速约开式 7 成）；M=黄铜保持架（更高转速）；同一型号还可叠加游隙后缀（如 6205-2RS/C3）'

def variant_guide(code):
    '''返回该型号的变体速查：密封/材料/游隙三张知识表 + 组合后缀示例。'''
    spec = DEEP_GROOVE.get(code)
    if not spec:
        return None
    (d, D, B, cr, c0, ng, no) = spec[:7]
    seal_lines = []
    for name, feat, factor, scene in SEAL_TYPES:
        rpm = f'''极限转速约 {int(ng * factor):,} rpm（脂）''' if factor < 1 else '极限转速不降'
        seal_lines.append(f'''<b>{name}</b>：{feat}；{rpm}<br><span style=\'font-size:11px;color:#555\'>{scene}</span>''')
    return {
        'seals': seal_lines,
        'materials': [f'''<b>{n}</b>：{f}<br><span style=\'font-size:11px;color:#555\'>{s}</span>''' for n, f, s in MATERIALS],
        'clearances': [f'''<b>{n}</b>：{f}<br><span style=\'font-size:11px;color:#555\'>{s}</span>''' for n, f, s in CLEARANCES],
        'suffix': SUFFIX_NOTES,
        'dims': (d, D, B, cr, c0, ng, no)}

