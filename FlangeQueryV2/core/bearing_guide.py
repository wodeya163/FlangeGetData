# -*- coding: utf-8 -*-
"""轴承类型选择指南（来自原版数据表）。"""

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

