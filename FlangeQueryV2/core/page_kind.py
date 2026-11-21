# -*- coding: utf-8 -*-
"""页面类型判定与行派生字段（无 Qt 依赖）。"""

PIPE_CSVS = {
    'ANSIB36.10M_B36.19M.csv', 'HGJ514无缝管.csv', 'HGJ528_2有缝管.csv',
    'HG20553(Ia)系列.csv', 'GB12459_GBT13401.csv',
    'GB17395_普通钢管.csv', 'GB17395_精密钢管.csv', 'GB17395_不锈钢管.csv',
}
FITTING_CSVS = {
    'GB12459_弯头.csv', 'GB12459_三通.csv', 'GB12459_异径管.csv',
    'GB12459_管帽.csv',
}

# ---------------------------------------------------------------- 垫片模块
# 垫片统一长表列：标准,DN,DN2,PN,Class,型式,D1,D2,D3,T,b,P,A,H,B,C,r
GASKET_PN_CSVS = {
    'HGT20606_FF.csv', 'HGT20606_RF.csv', 'HGT20606_MFM.csv', 'HGT20606_TG.csv',
    'HGT20607.csv', 'HGT20609.csv', 'HGT20610.csv', 'HGT20611.csv', 'HGT20612.csv',
}
GASKET_CLASS_CSVS = {'HGT20627.csv', 'HGT20631.csv'}
# 密封面型式参考（描述性 CSV，复用 mfm_*.bmp，无数值叠加）
GASKET_REF_CSVS = {'mfm_RF.csv', 'mfm_MFM.csv', 'mfm_TG.csv', 'mfm_RJ.csv'}
GASKET_CSVS = GASKET_PN_CSVS | GASKET_CLASS_CSVS | GASKET_REF_CSVS


def page_kind(csvf):
    """按 CSV 名判定筛选类型。"""
    if csvf in GASKET_REF_CSVS:
        return 'gasket_ref'
    if csvf in GASKET_CLASS_CSVS:
        return 'gasket_class'
    if csvf in GASKET_PN_CSVS:
        return 'gasket_pn'
    if csvf in FITTING_CSVS:
        return 'fitting'
    if csvf == 'U_bellows.csv':
        return 'bellows'
    if csvf in {'GB17395_普通钢管.csv', 'GB17395_精密钢管.csv',
                'GB17395_不锈钢管.csv'}:
        return 'gbt_pipe'
    if csvf in PIPE_CSVS:
        return 'pipe'
    if 'NBT47023' in csvf:
        return 'nbt47023'
    if 'HGT20623' in csvf:
        return 'hgt20623'
    if 'HGT20615' in csvf:
        return 'hgt20615'
    return 'hgt20592'


def row_seals(r):
    """从数据行推导密封面型式集合：RF 有值→RF；RJ_d 有值→RJ；d 与 RF_d 不同→FM/TG。"""
    out = set()
    if str(r.get('RF_d', '')).strip() not in ('', '-'):
        out.add('RF 突面')
    if str(r.get('RJ_d', '')).strip() not in ('', '-'):
        out.add('RJ 环连接')
    dv = str(r.get('d', '')).strip()
    rfv = str(r.get('RF_d', '')).strip()
    if dv not in ('', '-') and rfv not in ('', '-') and dv != rfv:
        out.add('FM/TG 凹凸/榫槽')
    return out


def row_schs(r):
    """钢管行有值的壁厚系列列名集合。"""
    base = {'DN', 'DN2', 'D_o', 'D_o_A', 'D_o_B'}
    out = set()
    for k, v in r.items():
        if k in base:
            continue
        if str(v).strip() not in ('', '-'):
            out.add(k)
    return out


