# -*- coding: utf-8 -*-
"""重新组装便携 zip：用新构建产物替换 _打包 内容并打包校验。"""
import os
import shutil
import zipfile

ROOT = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(ROOT, 'dist')
PKG = os.path.join(ROOT, '_打包')
ZIP = os.path.join(ROOT, 'FlangeQueryV2_EXE便携版.zip')

onedir_src = os.path.join(DIST, 'FlangeQueryV2')          # 文件夹版源
onefile_src = os.path.join(DIST, 'FlangeQueryV2.exe')     # 单文件版源
onedir_dst = os.path.join(PKG, '文件夹版', 'FlangeQueryV2')
onefile_dst = os.path.join(PKG, '单文件版', 'FlangeQueryV2.exe')

assert os.path.isdir(onedir_src), '缺少 onedir 产物'
assert os.path.isfile(onefile_src), '缺少 onefile 产物'

# 1. 替换文件夹版
if os.path.isdir(onedir_dst):
    shutil.rmtree(onedir_dst)
shutil.copytree(onedir_src, onedir_dst)
print('文件夹版已更新：', onedir_dst)

# 2. 替换单文件版
if os.path.isfile(onefile_dst):
    os.remove(onefile_dst)
os.makedirs(os.path.dirname(onefile_dst), exist_ok=True)
shutil.copy2(onefile_src, onefile_dst)
print('单文件版已更新：', onefile_dst)

# 3. 校验内置 CSV 已是最新（GB/T 17395-2024 三表，长表格式）
data_dir = os.path.join(onedir_dst, '_internal', 'Data')
chk = {
    'GB17395_普通钢管.csv': (lambda h: {'DN', 'DN2', 'D_o', '系列',
                                        '壁厚S(mm)', '每米重量(kg/m)'} <= set(h.split(','))),
    'GB17395_精密钢管.csv': (lambda h: {'DN', 'D_o', '壁厚S(mm)', '每米重量(kg/m)'} <= set(h.split(','))
                             and '系列' not in h.split(',')),
    'GB17395_不锈钢管.csv': (lambda h: {'DN', 'D_o', '系列', '壁厚S(mm)',
                                        '每米重量(kg/m)', '标准尺寸'} <= set(h.split(','))),
    'U_bellows.csv': (lambda h: {'序号', 'DN', '接管规格', 'D_o', 'h',
                                 'q', 'r', 'Lt', 'N', 'a'} == set(h.split(','))),
}
for fn, ok in chk.items():
    p = os.path.join(data_dir, fn)
    assert os.path.isfile(p), '内置缺失：' + fn
    hdr = open(p, encoding='utf-8-sig').readline().strip()
    assert ok(hdr), '内置 CSV 校验失败：' + fn + ' -> ' + hdr
    print('内置 CSV 校验通过：', fn, '|', hdr[:60])

# 4. 打包 zip（结构：使用说明.txt + 单文件版/ + 文件夹版/）
if os.path.isfile(ZIP):
    os.remove(ZIP)
with zipfile.ZipFile(ZIP, 'w', zipfile.ZIP_DEFLATED) as z:
    # 使用说明.txt 放根
    z.write(os.path.join(PKG, '使用说明.txt'), '使用说明.txt')
    for sub in ('单文件版', '文件夹版'):
        base = os.path.join(PKG, sub)
        for dp, _, fs in os.walk(base):
            for f in fs:
                fp = os.path.join(dp, f)
                arc = os.path.relpath(fp, PKG).replace(os.sep, '/')
                z.write(fp, arc)
print('便携 zip 已生成：', ZIP)

# 5. testzip 校验
bad = zipfile.ZipFile(ZIP).testzip()
print('testzip 结果：', 'OK' if bad is None else ('损坏: ' + bad))
n = len(zipfile.ZipFile(ZIP).namelist())
print('zip 文件数：', n)
