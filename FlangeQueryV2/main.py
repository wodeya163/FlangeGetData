# -*- coding: utf-8 -*-
"""管路智选 —— 布局严格按 ui_home_v2b.html（B 版定稿）
顶栏(44) → 工具条(36, 分类页签) → 三栏 [树220 | 查询表 | 侧栏430] → 状态栏(24)
侧栏：两行标题头 → 图形卡(模板×0.7 + 数值标注 + 右上角标) → 键值尺寸列表 → 底部双按钮
图形机制：模板位图 + 固定坐标数值标签（WN 页坐标经位图实测修正，其余页后续逐页精修）
"""
import csv
import datetime
import logging
import os
import sys
import tempfile
import traceback
from logging.handlers import RotatingFileHandler

from PyQt5.QtCore import Qt, QRect, QSettings, QEvent, QTimer, pyqtSignal
from PyQt5.QtGui import (QFont, QPixmap, QColor, QPainter, QIcon,
                         QStandardItem, QStandardItemModel)
from PyQt5.QtPrintSupport import QPrinter, QPrintPreviewDialog
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QSplitter,
    QTreeWidget, QTreeWidgetItem, QTableWidget, QTableWidgetItem, QLabel,
    QComboBox, QPushButton, QHeaderView, QAbstractItemView, QFileDialog,
    QStackedWidget,
    QTableView,
    QMessageBox, QFrame, QLineEdit, QScrollArea, QMenu, QAction, QDialog,
)

from flange_export import (resolve_export_columns, rows_to_tsv, write_csv,
                           write_xlsx)
from drawing import render_flange
from version import (APP_ID, APP_NAME, APP_TAGLINE, APP_VERSION,
                     APP_VERSION_DISPLAY)
from updater import (UpdateChecker, UpdateDownloader, apply_and_restart,
                     apply_exe_and_restart, apply_setup_and_restart,
                     UPDATE_DISABLED)
from core.page_spec import PageSpec
from core.page_kind import page_kind
from core import storage
from ui.data_table import DataTable
from ui.dialogs import SearchDialog, CoverageDialog
from ui.kv_panel import KvPanel
from ui.chrome import build_topbar, build_tools
from ui.drawing_card import DrawingCard, FLANGE_TPL_KIND
from ui.weight_page import WeightPage
from ui.metal_weight_page import MetalWeightPage
from ui.selection_page import SelectionPage, TOOLS as SELECTION_TOOLS
from ui.statusbar import build_statusbar
from ui.tree_panel import build_tree_panel
from ui.center_panel import build_center_panel
from ui.side_panel import build_side_panel
from ui.export_controller import export_selected, export_all, export_row
from ui.vector_export import export_vector
from ui.print_controller import do_print, render_print_page
from ui.page_controller import on_tree, fill_table, on_row
from ui.filters import (build_filters, clear_filter_widgets, enum_values,
                        filtered_rows, match, on_filter_changed, reset_filters,
                        schedule_filter)

from core.config import (APP_DIR, RES_DIR, TPL_DIR, SCALE,
                         VECTOR_ENABLED, logger)

LOG_FILE = None
ICON_PATH = os.path.join(RES_DIR, 'app_icon.ico')
# 数据目录：内嵌 Data 优先；其次本目录；最后回退原版程序 Data
DATA_DIRS = [os.path.join(RES_DIR, 'Data'),
             os.path.join(APP_DIR, 'Data'),
             os.path.join(os.path.dirname(APP_DIR), 'FlangeSheet_V1.00',
                          'FlangeSheet', 'Data')]
DB_PATH = os.path.join(DATA_DIRS[0], 'data.db')
SQLITE_ENABLED = os.environ.get('FLANGE_SQLITE', '1') != '0'




def _default_log_dir():
    base = os.environ.get('LOCALAPPDATA') or os.path.expanduser('~')
    return os.path.join(base, APP_ID, 'logs')


def setup_logging():
    """初始化文件日志和全局异常钩子；日志目录不可写时回退到临时目录。"""
    global LOG_FILE

    def _open(log_dir):
        os.makedirs(log_dir, exist_ok=True)
        path = os.path.join(log_dir, 'FlangeQuery.log')
        handler = RotatingFileHandler(path, maxBytes=1_000_000,
                                      backupCount=3, encoding='utf-8')
        return path, handler

    try:
        LOG_FILE, handler = _open(_default_log_dir())
    except OSError:
        LOG_FILE, handler = _open(tempfile.gettempdir())
    handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s %(name)s: %(message)s'))
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    if not any(isinstance(h, RotatingFileHandler) for h in root.handlers):
        root.addHandler(handler)
    sys.excepthook = _excepthook
    logger.info('日志文件：%s', LOG_FILE)


def _excepthook(exc_type, exc_value, exc_tb):
    logger.critical('未捕获异常', exc_info=(exc_type, exc_value, exc_tb))
    if QApplication.instance() is not None:
        try:
            detail = ''.join(traceback.format_exception(
                exc_type, exc_value, exc_tb))
            QMessageBox.critical(
                None, '程序错误',
                '发生未处理异常，详情已写入日志：\n%s\n\n%s'
                % (LOG_FILE or '（日志未初始化）', detail[-1200:]))
        except Exception:
            pass
    sys.__excepthook__(exc_type, exc_value, exc_tb)


# ---------------------------------------------------------------- 页面配置
# labels 坐标为模板位图像素坐标（WN 页经 2026-10-18 位图实测修正）
WN_LABELS = {
    'N_A(N_B)':    ([207, 90, 120, 14],  '{N_A}({N_B})'),
    'A1_A(A1_B)':  ([200, 113, 120, 14], '{A1_A}({A1_B})'),
    'n×ΦL':        ([54, 205, 74, 14],   '{n}×Φ{L}'),
    'K':           ([207, 319, 120, 13], '{K}'),
    'D':           ([207, 345, 120, 13], '{D}'),
    'H':           ([550, 235, 42, 14],  '{H}'),
    'C':           ([550, 288, 42, 14],  '{C}'),
}
# 仅 WN 页的标注坐标经过位图实测；其余法兰型式若沿用 WN 坐标会把数值
# 叠加到错误位置。这里先置空，宁可不显示，也不显示错位数字；逐类校准后再填回。
GENERIC_LABELS = {}

# 钢管/管件页标注（pipe.bmp 200×176：中心十字 x=88/y=88；壁厚各 Sch 列差异大，
# 不做单一叠加值，统一在右侧键值列表展示）
PIPE_LABELS = {
    'D_o':  ([100, 62, 92, 14],  'Φ{D_o}'),
}
# D_o_A/B 双系列页（ANSI B36 / GB12459）用 A 系外径标注
PIPE_LABELS_AB = {
    'D_o':  ([100, 62, 92, 14],  'Φ{D_o_A}'),
}

# GB/T 12459 管件页标注（fittings_*.bmp 520×460，字母+数值由 QLabel 叠加）
FITTING_ELBOW_LABELS = {
    'F':  ([258, 296, 120, 16], 'F={F_90LR}'),
    'D':  ([368, 168, 130, 16], 'D={D_o_A}'),
    'H45': ([90, 60, 150, 16],  'H(45°)={H_45}'),
}
FITTING_TEE_LABELS = {
    'C':  ([300, 396, 110, 16], 'C={C}'),
    'D':  ([452, 236, 130, 16], 'D={D_o_A}'),
}
FITTING_REDUCER_LABELS = {
    'H':  ([196, 410, 120, 16], 'H={H}'),
    'D':  ([38, 226, 130, 16],  'D={D_o_A}'),
    'D1': ([452, 226, 150, 16], 'D1={D_o_A_s}'),
}
FITTING_CAP_LABELS = {
    'E':  ([140, 374, 110, 16], 'E={E}'),
    'D':  ([36, 226, 130, 16],  'D={D_o_A}'),
}
from core.page_kind import (PIPE_CSVS, FITTING_CSVS, GASKET_PN_CSVS,
                            GASKET_CLASS_CSVS, GASKET_REF_CSVS, GASKET_CSVS)

# 垫片图形卡的标注坐标（模板像素坐标 596×498；数值由程序叠加，与法兰模板一致）
GASKET_LABELS = {
    'flat': {
        'D1': ([12, 12, 150, 18], 'D1={D1}'),
        'D2': ([12, 34, 150, 18], 'D2={D2}'),
        'T':  ([430, 12, 150, 18], 'T={T}'),
        'b':  ([430, 34, 150, 18], 'b={b}'),
    },
    'ptfe': {
        'D1': ([12, 12, 150, 18], 'D1={D1}'),
        'D2': ([12, 34, 150, 18], 'D2={D2}'),
        'D3': ([430, 12, 150, 18], 'D3={D3}'),
        'T':  ([430, 34, 150, 18], 'T={T}'),
    },
    'metaljacket': {
        'D1': ([12, 12, 150, 18], 'D1={D1}'),
        'D2': ([12, 34, 150, 18], 'D2={D2}'),
        'T':  ([430, 12, 150, 18], 'T={T}'),
    },
    'spiral': {
        'D1': ([12, 12, 150, 18], 'D1={D1}'),
        'D2': ([12, 34, 150, 18], 'D2={D2}'),
        'D3': ([430, 12, 150, 18], 'D3={D3}'),
        'T':  ([430, 34, 150, 18], 'T={T}'),
    },
    'serrated': {
        # 注：HG/T 20611 齿形组合垫标准表不单列齿深 t（gen_gasket_data.py 恒置 ''），
        # 统一表头亦无 t 列，故图形卡仅叠加 D1/D2/T 三项真实维度。
        'D1': ([12, 12, 150, 18], 'D1={D1}'),
        'D2': ([12, 34, 150, 18], 'D2={D2}'),
        'T':  ([430, 12, 150, 18], 'T={T}'),
    },
    'ring': {
        'P': ([12, 12, 150, 18], 'P={P}'),
        'A': ([12, 34, 150, 18], 'A={A}'),
        'H': ([12, 56, 150, 18], 'H={H}'),
        'B': ([430, 12, 150, 18], 'B={B}'),
        'C': ([430, 34, 150, 18], 'C={C}'),
        'r': ([430, 56, 150, 18], 'r={r}'),
    },
}

# 垫片页侧栏键值中文名
GASKET_KV = {
    '标准': '标准', 'DN': '公称尺寸 DN', 'DN2': '管径 NPS', 'PN': '压力等级 PN',
    'Class': '压力等级 Class', '型式': '垫片型式', 'D1': '垫片内径 D1',
    'D2': '垫片外径 D2', 'D3': 'D3', 'T': '厚度 T', 'b': '包边宽度 b',
    'P': '节圆直径 P', 'A': '环宽 A', 'H': '环高 H', 'B': '八角平面宽 B',
    'C': '环厚 C', 'r': '圆角半径 r', 't': '齿深 t',
    '代号': '代号', '名称': '名称', '适用标准': '适用标准',
    '适用压力范围': '适用压力范围', '说明': '说明',
}

# 树节点 → (显示名, CSV 文件名, 模板图, 标签配置, 标准号)
# 前四组：HG/T 与 NB/T 原版数据；后三组：GB/T 9124 国标法兰（尺寸与
# HG/T 20592/20615 衔接）与钢管、管件组（视图切换见 fill_table/on_row）
# ---- U 形波纹管膨胀节（70B125-2002 附录A 表A.1）----
# 中间表列序（列名 → 表头）
BELLOWS_COLS = [
    ('序号', '序号'), ('DN', '公称直径 DN'), ('接管规格', '接管规格 dᵢ×S'),
    ('D_o', '波谷外径 Do'), ('h', '波高 h'), ('q', '波距 q'),
    ('r', '波谷半径 r'), ('Lt', '直段长度 Lt'),
    ('N', '一次成型最多波数 N'), ('a', '一个波展开长度 a'),
]
# 详情键值中文名
BELLOWS_KV = {
    '序号': '序号', 'DN': '公称直径 DN', '接管规格': '接管规格 dᵢ×S',
    'D_o': '波谷外径 Do (mm)', 'h': '波高 h (mm)', 'q': '波距 q (mm)',
    'r': '波谷半径 r (mm)', 'Lt': '直段长度 Lt (mm)',
    'N': '一次成型最多波数 N (个)', 'a': '一个波展开长度 a (mm)',
}
# bellows.bmp（596×498）标注框位置（与模板预留框对齐）
BELLOWS_LABELS = {
    'DN':  ([12, 12, 200, 26],  'DN {DN}'),
    'D_o': ([250, 300, 96, 24], 'Φ{D_o}'),
    'pipe': ([12, 460, 200, 26], '接管 {接管规格}'),
    'hq':  ([384, 460, 200, 26], 'h={h}  q={q}'),
    'rLt': ([384, 300, 200, 24], 'r={r}  Lt={Lt}'),
}

PAGES = [
    ('GB/T 9124.1-2019（PN 系列·欧洲体系）', [
        ('WN 带颈对焊（GB/T 真值 PN2.5–400）', 'GBT9124_1_带颈对焊.csv',
         'WN-带颈对焊.bmp', WN_LABELS),
        ('SO 带颈平焊',   'GBT9124_1_带颈平焊.csv',   'SO-带颈平焊.bmp',   GENERIC_LABELS),
        ('PL 板式平焊',   'GBT9124_1_板式平焊.csv',   'PL板式平焊.bmp',    GENERIC_LABELS),
        ('SW 承插焊',     'GBT9124_1_承插焊.csv',     'SW承插焊.bmp',      GENERIC_LABELS),
        ('Th 螺纹',       'GBT9124_1_螺纹.csv',       'Th螺纹.bmp',        GENERIC_LABELS),
        ('BL 法兰盖',     'GBT9124_1_法兰盖.csv',     'BL法兰盖.bmp',      GENERIC_LABELS),
        ('IF 整体法兰',   'GBT9124_1_整体.csv',       'IF整体法兰.bmp',    GENERIC_LABELS),
        ('PJSE 对焊环松套', 'GBT9124_1_对焊环松套.csv', 'PJSE对焊环松套592.bmp', GENERIC_LABELS),
        ('PJRJ 平焊环松套', 'GBT9124_1_平焊环松套.csv', 'PJRJ平焊环松套.bmp',  GENERIC_LABELS),
        ('BL(S) 衬里法兰盖', 'HGT20592_不锈钢衬里法兰盖.csv', 'BL法兰盖.bmp', GENERIC_LABELS),
    ]),
    ('GB/T 9124.2-2019（Class 系列·美洲体系）', [
        ('WN 带颈对焊（GB/T 真值 Class150–2500）',
         'GBT9124_2_带颈对焊.csv', 'WN-带颈对焊.bmp', WN_LABELS),
        ('SO 带颈平焊（GB/T 真值 Class150–1500）',
         'GBT9124_2_带颈平焊.csv', 'SO-带颈平焊.bmp',
         GENERIC_LABELS),
        ('IF 整体法兰（GB/T 真值 Class150–2500）',
         'GBT9124_2_整体.csv', 'IF整体法兰.bmp', GENERIC_LABELS),
        ('SW 承插焊（GB/T 真值 Class150–1500）',
         'GBT9124_2_承插焊.csv', 'SW承插焊.bmp',
         GENERIC_LABELS),
        ('Th 螺纹（GB/T 真值 Class150–2500）',
         'GBT9124_2_螺纹.csv', 'Th螺纹.bmp', GENERIC_LABELS),
        ('BL 法兰盖（GB/T 真值 Class150–2500）',
         'GBT9124_2_法兰盖.csv', 'BL法兰盖.bmp',
         GENERIC_LABELS),
        ('WN 带颈对焊',   'HGT20615_带颈对焊.csv',   'WN-带颈对焊.bmp',   WN_LABELS),
        ('SO 带颈平焊',   'HGT20615_带颈平焊.csv',   'SO-带颈平焊.bmp',   GENERIC_LABELS),
        ('SW 承插焊',     'HGT20615_承插焊.csv',     'SW承插焊.bmp',      GENERIC_LABELS),
        ('Th 螺纹',       'HGT20615_螺纹.csv',       'Th螺纹.bmp',        GENERIC_LABELS),
        ('BL 法兰盖',     'HGT20615_法兰盖.csv',     'BL法兰盖.bmp',      GENERIC_LABELS),
        ('IF 整体法兰',   'HGT20615_整体.csv',       'IF整体法兰.bmp',    GENERIC_LABELS),
        ('LWN 长高颈',    'HGT20615_长高颈.csv',     'LWN-长高颈.bmp',    GENERIC_LABELS),
        ('PJSE 对焊环松套', 'HGT20615_对焊环松套.csv', 'PJSE对焊环松套615.bmp', GENERIC_LABELS),
    ]),
    ('HG/T 20592-2009（欧洲体系）', [
        ('WN 带颈对焊',   'HGT20592_带颈对焊.csv',   'WN-带颈对焊.bmp',   WN_LABELS),
        ('SO 带颈平焊',   'HGT20592_带颈平焊.csv',   'SO-带颈平焊.bmp',   GENERIC_LABELS),
        ('PL 板式平焊',   'HGT20592_板式平焊.csv',   'PL板式平焊.bmp',    GENERIC_LABELS),
        ('SW 承插焊',     'HGT20592_承插焊.csv',     'SW承插焊.bmp',      GENERIC_LABELS),
        ('Th 螺纹',       'HGT20592_螺纹.csv',       'Th螺纹.bmp',        GENERIC_LABELS),
        ('BL 法兰盖',     'HGT20592_法兰盖.csv',     'BL法兰盖.bmp',      GENERIC_LABELS),
        ('IF 整体法兰',   'HGT20592_整体.csv',       'IF整体法兰.bmp',    GENERIC_LABELS),
        ('PJSE 对焊环松套', 'HGT20592_对焊环松套.csv', 'PJSE对焊环松套592.bmp', GENERIC_LABELS),
        ('PJRJ 平焊环松套', 'HGT20592_平焊环松套.csv', 'PJRJ平焊环松套.bmp',  GENERIC_LABELS),
        ('BL(S) 衬里法兰盖', 'HGT20592_不锈钢衬里法兰盖.csv', 'BL法兰盖.bmp', GENERIC_LABELS),
    ]),
    ('HG/T 20615-2009（美洲体系）', [
        ('WN 带颈对焊',   'HGT20615_带颈对焊.csv',   'WN-带颈对焊.bmp',   WN_LABELS),
        ('SO 带颈平焊',   'HGT20615_带颈平焊.csv',   'SO-带颈平焊.bmp',   GENERIC_LABELS),
        ('SW 承插焊',     'HGT20615_承插焊.csv',     'SW承插焊.bmp',      GENERIC_LABELS),
        ('Th 螺纹',       'HGT20615_螺纹.csv',       'Th螺纹.bmp',        GENERIC_LABELS),
        ('BL 法兰盖',     'HGT20615_法兰盖.csv',     'BL法兰盖.bmp',      GENERIC_LABELS),
        ('IF 整体法兰',   'HGT20615_整体.csv',       'IF整体法兰.bmp',    GENERIC_LABELS),
        ('LWN 长高颈',    'HGT20615_长高颈.csv',     'LWN-长高颈.bmp',    GENERIC_LABELS),
        ('PJSE 对焊环松套', 'HGT20615_对焊环松套.csv', 'PJSE对焊环松套615.bmp', GENERIC_LABELS),
    ]),
    ('HG/T 20623-2009（大直径）', [
        ('WN 带颈对焊 A 系列', 'HGT20623_带颈对焊A系列.csv', 'WN-带颈对焊.bmp', WN_LABELS),
        ('WN 带颈对焊 B 系列', 'HGT20623_带颈对焊B系列.csv', 'WN-带颈对焊.bmp', WN_LABELS),
        ('BL 法兰盖 A 系列',   'HGT20623_A系列法兰盖.csv',   '623法兰盖.bmp',   GENERIC_LABELS),
        ('BL 法兰盖 B 系列',   'HGT20623_B系列法兰盖.csv',   '623法兰盖.bmp',   GENERIC_LABELS),
    ]),
    ('NB/T 47023（容器法兰）', [
        ('WN 带颈对焊',   'NBT47023_带颈对焊.csv',   '容器法兰.bmp',      GENERIC_LABELS),
    ]),
    ('钢管（壁厚规格）', [
        ('GB/T 17395-2024 普通钢管', 'GB17395_普通钢管.csv', 'pipe.bmp', PIPE_LABELS),
        ('GB/T 17395-2024 精密钢管', 'GB17395_精密钢管.csv', 'pipe.bmp', PIPE_LABELS),
        ('GB/T 17395-2024 不锈钢管', 'GB17395_不锈钢管.csv', 'pipe.bmp', PIPE_LABELS),
        ('ANSI B36.10M/B36.19M 钢管', 'ANSIB36.10M_B36.19M.csv', 'pipe.bmp', PIPE_LABELS_AB),
        ('HGJ514 无缝钢管',           'HGJ514无缝管.csv',        'pipe.bmp', PIPE_LABELS),
        ('HGJ528-2 有缝钢管',         'HGJ528_2有缝管.csv',      'pipe.bmp', PIPE_LABELS),
        ('HG/T 20553 (Ia) 系列',      'HG20553(Ia)系列.csv',     'pipe.bmp', PIPE_LABELS),
    ]),
    ('U形波纹管膨胀节（70B125-2002）', [
        ('U形波纹管几何参数', 'U_bellows.csv', 'bellows.bmp', BELLOWS_LABELS),
    ]),
    ('钢制对焊管件（GB/T 12459 / GB/T 13401）', [
        ('90°/45°/180° 弯头', 'GB12459_弯头.csv',   'fittings_elbow.bmp',   FITTING_ELBOW_LABELS),
        ('等径三通/四通',     'GB12459_三通.csv',   'fittings_tee.bmp',     FITTING_TEE_LABELS),
        ('同心/偏心异径管',   'GB12459_异径管.csv', 'fittings_reducer.bmp', FITTING_REDUCER_LABELS),
        ('椭圆管帽',          'GB12459_管帽.csv',   'fittings_cap.bmp',     FITTING_CAP_LABELS),
        ('管件壁厚表',        'GB12459_GBT13401.csv', 'pipe.bmp',           PIPE_LABELS_AB),
    ]),
    # ---- 垫片模块（HG/T 20606~20612 PN 系 / 20627~20631 Class 系）----
    ('垫片 HG/T 20606-2009 非金属平垫（PN 系列）', [
        ('FF 全平面型',  'HGT20606_FF.csv',   'gasket_flat.bmp',       GASKET_LABELS['flat']),
        ('RF 突面型',    'HGT20606_RF.csv',   'gasket_flat.bmp',       GASKET_LABELS['flat']),
        ('MFM 凹凸面型', 'HGT20606_MFM.csv',  'gasket_flat.bmp',       GASKET_LABELS['flat']),
        ('TG 榫槽面型',  'HGT20606_TG.csv',   'gasket_flat.bmp',       GASKET_LABELS['flat']),
    ]),
    ('垫片 HG/T 20607-2009 PTFE 包覆垫（PN 系列）', [
        ('PTFE 包覆垫', 'HGT20607.csv', 'gasket_ptfe.bmp', GASKET_LABELS['ptfe']),
    ]),
    ('垫片 HG/T 20609-2009 金属包覆垫（PN 系列）', [
        ('金属包覆垫', 'HGT20609.csv', 'gasket_metaljacket.bmp', GASKET_LABELS['metaljacket']),
    ]),
    ('垫片 HG/T 20610-2009 缠绕式垫片（PN 系列）', [
        ('缠绕式垫片', 'HGT20610.csv', 'gasket_spiral.bmp', GASKET_LABELS['spiral']),
    ]),
    ('垫片 HG/T 20611-2009 齿形组合垫（PN 系列）', [
        ('齿形组合垫', 'HGT20611.csv', 'gasket_serrated.bmp', GASKET_LABELS['serrated']),
    ]),
    ('垫片 HG/T 20612-2009 金属环垫（PN 系列）', [
        ('金属环垫', 'HGT20612.csv', 'gasket_ring.bmp', GASKET_LABELS['ring']),
    ]),
    ('垫片 HG/T 20627-2009 非金属平垫（Class 系列）', [
        ('非金属平垫', 'HGT20627.csv', 'gasket_flat.bmp', GASKET_LABELS['flat']),
    ]),
    ('垫片 HG/T 20631-2009 缠绕式垫片（Class 系列）', [
        ('缠绕式垫片', 'HGT20631.csv', 'gasket_spiral.bmp', GASKET_LABELS['spiral']),
    ]),
    ('密封面型式参考（RF / MFM / TG / RJ）', [
        ('突面 RF',      'mfm_RF.csv',  'mfm_突面.bmp',   {}),
        ('凹凸面 MFM',   'mfm_MFM.csv', 'mfm_凹凸面.bmp', {}),
        ('榫槽面 TG',    'mfm_TG.csv',  'mfm_楔槽面.bmp', {}),
        ('环连接面 RJ',  'mfm_RJ.csv',  'mfm_环连接面.bmp', {}),
    ]),
]

# 页面声明：把 PAGES 字面量升级为 PageSpec，同时保持 4 元组解包兼容
PAGES = [(std, [PageSpec(*page) for page in pages]) for std, pages in PAGES]


def _drawing_key(tpl):
    kind = FLANGE_TPL_KIND.get(tpl)
    if kind:
        return 'flange:' + kind
    if tpl == 'bellows.bmp':
        return 'bellows'
    if tpl == 'pipe.bmp':
        return 'pipe'
    if tpl.startswith('gasket_'):
        return 'gasket:' + tpl[len('gasket_'):].split('.')[0]
    if tpl.startswith('fittings_'):
        return 'fitting:' + tpl[len('fittings_'):].split('.')[0]
    if tpl.startswith('mfm_'):
        return 'seal'
    return ''


def _controls_for(tpl):
    if tpl in FLANGE_TPL_KIND:
        return ('face',)
    if tpl == 'fittings_elbow.bmp':
        return ('angle', 'sch')
    if tpl.startswith('fittings_'):
        return ('sch',)
    return ()


PAGES = [(std, [
    p.with_meta(group=std, kind=page_kind(p.csvf),
                drawing=_drawing_key(p.template),
                controls=_controls_for(p.template))
    for p in pages
]) for std, pages in PAGES]

# 重量计算页：无 CSV，参数全部手动输入
WEIGHT_PAGES = [
    PageSpec('直管重量', '', '', {}, group='重量计算', kind='weight',
             subtype='pipe', code='weight:pipe'),
    PageSpec('弯头重量', '', '', {}, group='重量计算', kind='weight',
             subtype='elbow', code='weight:elbow'),
    PageSpec('三通重量', '', '', {}, group='重量计算', kind='weight',
             subtype='tee', code='weight:tee'),
    PageSpec('金属材料', '', '', {}, group='重量计算', kind='weight',
             subtype='metal', code='weight:metal'),
]
PAGES.append(('重量计算', WEIGHT_PAGES))

# 选型工具页：无 CSV，按工具独立移植
SELECTION_PAGES = [
    PageSpec(name, '', '', {}, group='选型工具', kind='selection',
             subtype=key, code='selection:' + key)
    for key, name, _desc in SELECTION_TOOLS
]
PAGES.append(('选型工具', SELECTION_PAGES))

# 工具条分类页签 → 匹配的树组前缀（空列表 = 模块开发中）
TABS = [
    ('法兰',     ['GB/T', 'HG/T']),
    ('密封件',   ['垫片', '密封面型式']),
    ('管件',     ['钢制对焊管件']),
    ('钢管',     ['钢管']),
    ('波纹管',   ['U形波纹管']),
    ('容器法兰', ['NB/T']),
    ('重量计算', ['重量计算']),
    ('选型工具', ['选型工具']),
]

from core.review import (PROVENANCE, REVIEW_LABELS, DATA_REVIEW, STANDARDS_COVERAGE,
                        source_note, attach_source, review_for, attach_review,
                        annotate_rows)

# 中间表展示列（列名 → 表头）
SHOW_COLS = [
    ('DN', '公称尺寸'), ('D', '外径 D'), ('K', '螺栓孔中心圆 K'),
    ('n', 'n'), ('L', 'L'), ('C', '厚度 C'), ('H', '总高 H'),
    ('N_A', 'N_A'), ('N_B', 'N_B'), ('A1_A', 'A1_A'), ('A1_B', 'A1_B'),
    ('RF_d', '密封面 d'), ('RF_f1', 'f1'), ('Th', '螺栓 Th'), ('m_kg', '质量 kg'),
    # 垫片列（法兰行无此类数据，会被自动过滤）
    ('DN2', '管径 NPS'), ('型式', '垫片型式'),
    ('D1', '垫片内径 D1'), ('D2', '垫片外径 D2'), ('D3', 'D3'),
    ('T', '厚度 T'), ('b', '包边宽 b'),
    ('P', '节圆 P'), ('A', '环宽 A'), ('B', '八角宽 B'), ('r', '圆角 r'),
]

KV_LABELS = [
    ('DN', '公称尺寸 DN'), ('D', '法兰外径 D'), ('K', '螺栓孔中心圆 K'),
    ('C', '法兰厚度 C'), ('H', '法兰总高 H'),
    ('N_A', '颈部直径 N (A系)'), ('N_B', '颈部直径 N (B系)'),
    ('A1_A', '焊端外径 A1 (A系)'), ('A1_B', '焊端外径 A1 (B系)'),
    ('RF_d', '密封面 d'), ('RF_f1', '密封面 f1'), ('Th', '螺栓 Th'),
    ('m_kg', '参考质量 kg'),
]
# 松套/衬里等页面的质量字段不叫 m_kg，单独补充展示
KV_EXTRA = {
    'PJ_m_kg': '松套质量 kg',
    'SE_m_kg': '密封环质量 kg',
    'RJ_m_kg': '环质量 kg',
}

# ---------------------------------------------------------------- 筛选体系
# 每个页码 → 筛选字段列表 (列名, 显示名, 显示变换函数)
# 值为 '' 或 '-' 视为无值；"全部" 不过滤。数值类按数值排序。
def _pn_label(v):
    return 'PN' + v if v and not v.upper().startswith('PN') else v


def _inch_sort(v):
    """DN 列排序：'1/2"' → 0.5，'1 1/4"' → 1.25，纯数字直接用。"""
    s = str(v).strip().replace('"', '').replace('″', '')
    try:
        if '/' in s:
            parts = s.split()
            frac = parts[-1]
            num, den = frac.split('/')
            base = float(parts[0]) if len(parts) > 1 else 0.0
            return (0, base + float(num) / float(den), s)
        return (0, float(s.replace(',', '.')), s)
    except (ValueError, ZeroDivisionError):
        return (1, 0, s)


def _class_label(v):
    return 'Class ' + v


FILTER_DEFS = {
    # 欧洲体系（HG/T 20592 / GB/T 9124.1）
    'hgt20592': [
        ('PN', '压力', _pn_label),
        ('seal', '密封面', None),      # 派生：RF / RJ / FM / TG 有无 d 值
        ('DN', 'DN', None),
        ('Th', '螺栓', None),
    ],
    # 美洲体系（HG/T 20615 / GB/T 9124.2）
    'hgt20615': [
        ('Class', 'Class', _class_label),
        ('seal', '密封面', None),
        ('DN', 'DN', None),
        ('DN2', 'NPS', None),
        ('Th', '螺栓', None),
    ],
    # 大直径（HG/T 20623）
    'hgt20623': [
        ('PN', '压力', _pn_label),
        ('Class', 'Class', _class_label),
        ('DN', 'DN', None),
    ],
    # 容器法兰（NB/T 47023）
    'nbt47023': [
        ('PN', '压力', _pn_label),
        ('DN', 'DN', None),
        ('Th', '螺栓', None),
    ],
    # 钢管 / 管件（壁厚系列）
    'pipe': [
        ('DN', 'DN', None),
        ('DN2', 'NPS', None),
        ('Sch', '壁厚', None),         # 派生：仅显示有值的 Sch 列
    ],
    # GB/T 17395-2024 三表（普通/精密/不锈钢，长表格式）：
    # 查询条件 = 公称直径(DN) / 外径(D_o) / 壁厚(壁厚S(mm))，结果列含「每米重量(kg/m)」。
    'gbt_pipe': [
        ('DN', 'DN', None),
        ('D_o', '外径', None),
        ('壁厚S(mm)', '壁厚', None),
    ],
    # GB/T 12459 对焊管件（弯头/三通/异径管/管帽）
    'fitting': [
        ('DN', 'DN', None),
        ('DN2', 'NPS', None),
    ],
    # U 形波纹管膨胀节（70B125-2002 表A.1）
    'bellows': [
        ('DN', 'DN', None),
        ('接管规格', '接管规格', None),
    ],
    # 垫片（PN 系列：HG/T 20606/20607/20609/20610/20611/20612）
    'gasket_pn': [
        ('PN', '压力', _pn_label),
        ('DN', 'DN', None),
        ('型式', '垫片型式', None),
    ],
    # 垫片（Class 系列：HG/T 20627/20631）
    'gasket_class': [
        ('Class', 'Class', _class_label),
        ('DN', 'DN', None),
        ('DN2', 'NPS', None),
        ('型式', '垫片型式', None),
    ],
    # 密封面型式参考（无筛选维度）
    'gasket_ref': [],
}

# 取值过多、用下拉无法操作的数值维度改用“最小~最大”区间筛选
RANGE_FILTER_COLS = {
    'gbt_pipe': {'D_o', '壁厚S(mm)'},
}


from core.page_kind import page_kind, row_seals, row_schs

def fmt_num(v):
    """数值友好显示：去掉多余 .0。"""
    try:
        f = float(v)
        return ('%d' % f) if abs(f - int(f)) < 1e-9 else ('%g' % f)
    except (TypeError, ValueError):
        return str(v)


def sort_key_mixed(v):
    """DN/PN 排序：优先数值，其次字符串长度。"""
    try:
        return (0, float(str(v).replace(',', '.')), '')
    except ValueError:
        return (1, 0, str(v))


def _to_float(value):
    try:
        return float(str(value).strip().replace(',', '.'))
    except (TypeError, ValueError):
        return None


def _in_range(value, low, high):
    number = _to_float(value)
    if number is None:
        return False
    if low is not None and number < low:
        return False
    if high is not None and number > high:
        return False
    return True


# 壁厚系列标准顺序（薄 → 厚）
_SCH_ORDER = ['Sch5s', 'Sch10s', 'Sch20s', 'Sch10', 'Sch20', 'Sch30', 'Sch40s',
              'Sch40', 'STD', 'Sch60', 'Sch80s', 'Sch80', 'XS', 'Sch100',
              'Sch120', 'Sch140', 'Sch160', 'XXS']


def _sch_order(v):
    return (_SCH_ORDER.index(v) if v in _SCH_ORDER else 99, v)


def _col_label(col):
    """筛选维度中文名（用于条件徽标）。"""
    return {'PN': '压力等级', 'Class': '压力等级', 'DN': 'DN', 'DN2': 'NPS',
            'seal': '密封面', 'Sch': '壁厚系列', 'Th': '螺栓',
            'D_o': '外径', '壁厚S(mm)': '壁厚',
            '型式': '垫片型式'}.get(col, col)


# QSS（与 ui_home_v2b.html 样式对应）
QSS = '''
QMainWindow { background:#163a5f; }
QWidget { background:#f7f8fa; font-family:"Microsoft YaHei"; color:#222; }
QSplitter::handle { background:#163a5f; }
/* 顶栏 */
#top { background:#1f4e79; }
#top QLabel { color:#fff; background:transparent; }
#logo { font-size:16px; font-weight:bold; letter-spacing:1px; }
#top QLabel#ver { font-size:11px; background:rgba(255,255,255,.15); padding:2px 8px; border-radius:9px; }
#subtitle { font-size:12px; }
.topbtn { font-size:12px; color:#fff; background:rgba(255,255,255,.16);
          border:none; border-radius:12px; padding:5px 14px; }
.topbtn:hover { background:rgba(255,255,255,.28); }
/* 工具条 */
#tools { background:#fff; border-bottom:1px solid #dfe3e8; }
#tools QLabel { color:#888; font-size:12px; background:transparent; }
.tab { font-size:12px; color:#444; background:transparent;
       border:none; border-radius:11px; padding:5px 14px; }
.tab:hover { background:#e8eef5; }
.tab:checked { background:#1f4e79; color:#fff; }
/* 树 */
#tree { background:#fff; border:none; font-size:12px; }
#tree::item { padding:4px 8px; border-radius:4px; }
#tree::item:hover { background:#eef3f8; }
#tree::item:selected { background:#1f4e79; color:#fff; }
#treeSearch { border:1px solid #c2c8cf; border-radius:4px; padding:4px 8px; font-size:12px; background:#fff; }
/* 中间表 */
#center { background:#fff; }
#selbar { background:#f7f9fb; border-bottom:1px solid #e2e6ea; }
#selbar QLabel { color:#555; font-size:12px; background:transparent; }
#selbar QComboBox { border:1px solid #c2c8cf; border-radius:4px; padding:3px 6px; font-size:12px; background:#fff; }
#cap { color:#666; font-size:12px; background:transparent; }
#cap b { color:#222; }
QTableWidget, QTableView { gridline-color:#d8dde3; font-size:12px; background:#fff; }
QTableWidget::item, QTableView::item { padding:4px 9px; }
QTableWidget::item:hover, QTableView::item:hover { background:#f2f7fc; }
QTableWidget::item:selected, QTableView::item:selected {
    background:#fff6e6; color:#222; font-weight:bold; }
QHeaderView::section { background:#eef3f8; color:#1f4e79; border:1px solid #d8dde3;
                       padding:4px 9px; font-size:12px; }
/* 侧栏 */
#side { background:#fdfdfe; }
#shead { background:#fff; border-bottom:1px solid #e2e6ea; }
#shead .t1 { font-size:13px; font-weight:bold; color:#1f4e79; background:transparent; }
#shead .t2 { font-size:11px; color:#777; background:transparent; }
#stage { background:#fdfdfe; }
#kvhead { font-size:12px; font-weight:bold; color:#1f4e79; background:#fff;
          border-top:1px solid #e2e6ea; border-bottom:1px solid #e2e6ea; padding:6px 14px; }
#kv QTableWidget, #kv QTableView, #kv { background:#fdfdfe; }
#kv QTableWidget, #kv QTableView { gridline-color:transparent; font-size:12px; }
#kv QHeaderView::section { background:#fdfdfe; border:none; }
.b-print { background:#1f4e79; color:#fff; border:none; border-radius:4px; padding:7px 0; font-size:13px; }
.b-print:hover { background:#2a5f92; }
.b-exp { background:#fff; color:#1f4e79; border:1px solid #1f4e79; border-radius:4px; padding:7px 0; font-size:13px; }
.b-exp:hover { background:#eef3f8; }
/* 状态栏 */
#statusbar { background:#f7f8fa; border-top:1px solid #cfd4da; }
#statusbar QLabel { color:#666; font-size:11px; background:transparent; }
'''


def find_data(name):
    for d in DATA_DIRS:
        p = os.path.join(d, name)
        if os.path.exists(p):
            return p
    return None


def safe_filename_part(text):
    """清理 DN 等值中的 Windows 非法文件名字符。"""
    text = str(text).strip()
    for ch in '<>:"/\\|?*':
        text = text.replace(ch, '_')
    return text.strip(' .') or '未命名'


from core.data import COLUMN_ALIASES, _normalize_columns, load_csv

from core import search as core_search
from core.search import split_query, row_matches_query


def search_all(query, limit=300, cache=None):
    return core_search.search_all(query, PAGES, find_data, load_csv,
                                  limit, cache)

class NumItem(QTableWidgetItem):
    """按数值排序的表格项（DN/PN/尺寸列用），显示文本保持原样。"""

    def __init__(self, text, sort_val):
        super().__init__(text)
        self._sv = sort_val

    def __lt__(self, other):
        if isinstance(other, NumItem):
            try:
                return self._sv < other._sv
            except TypeError:
                return str(self._sv) < str(other._sv)
        return super().__lt__(other)


def _num_or_str(v):
    try:
        return float(str(v).replace(',', '.'))
    except (TypeError, ValueError):
        return _inch_sort(v)


class MultiCombo(QPushButton):
    """多选下拉：按钮显示当前选择摘要，弹出菜单逐项勾选（用于密封面等集合维度）。"""

    changed = pyqtSignal()

    def __init__(self, options, parent=None):
        super().__init__(parent)
        from PyQt5.QtWidgets import QMenu
        self._opts = list(options)
        self._checked = set()
        self._menu = QMenu(self)
        for o in self._opts:
            a = self._menu.addAction(o)
            a.setCheckable(True)
            a.toggled.connect(lambda ck, name=o: self._toggle(name, ck))
        self._menu.addSeparator()
        clr = self._menu.addAction('清空选择')
        clr.triggered.connect(self.clear_all)
        self.clicked.connect(self._popup)
        self.setStyleSheet('font-size:12px;text-align:left;padding:3px 6px;'
                           'border:1px solid #c2c8cf;border-radius:4px;background:#fff;')
        self._refresh()

    def _popup(self):
        self._menu.setMinimumWidth(max(140, self.width()))
        self._menu.exec_(self.mapToGlobal(self.rect().bottomLeft()))

    def _toggle(self, name, checked):
        if checked:
            self._checked.add(name)
        else:
            self._checked.discard(name)
        self._refresh()
        self.changed.emit()

    def clear_all(self):
        self._checked.clear()
        for a in self._menu.actions():
            if a.isCheckable():
                a.blockSignals(True)
                a.setChecked(False)
                a.blockSignals(False)
        self._refresh()
        self.changed.emit()

    def _refresh(self):
        self.setText(' / '.join(sorted(self._checked)) if self._checked else '全部')

    def values(self):
        return sorted(self._checked)

    def set_values(self, vals):
        self._checked = set(vals)
        for a in self._menu.actions():
            if a.isCheckable():
                a.blockSignals(True)
                a.setChecked(a.text() in self._checked)
                a.blockSignals(False)
        self._refresh()

    # 与 QComboBox 接口兼容，便于统一处理
    def currentText(self):
        return self.text()

    def setCurrentIndex(self, _ix):
        self.clear_all()


def load_page_with_source(csvf, csv_path, std=''):
    """返回 (head, rows, source)；rows 已附加行级复核字段。"""
    if SQLITE_ENABLED and storage.has_database(DB_PATH):
        try:
            head, rows = storage.load_sqlite(csvf, DB_PATH)
            return head, annotate_rows(rows, csvf, std), 'SQLite'
        except Exception as exc:  # 损坏/缺表时回退，不阻塞页面
            logger.warning('SQLite 读取失败，回退 CSV：%s（%s）', csvf, exc)
    head, rows = load_csv(csv_path)
    return head, annotate_rows(rows, csvf, std), 'CSV'


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings(APP_ID, APP_ID + 'V3')
        self.setWindowTitle('%s %s' % (APP_NAME, APP_VERSION_DISPLAY))
        self.resize(1440, 880)
        self.rows = []
        self.cur_page = None
        self.cur_row = None
        self.current_cols = []
        self._active_tab = None
        self._filter_timer = QTimer(self)
        self._filter_timer.setSingleShot(True)
        self._filter_timer.setInterval(250)
        self._filter_timer.timeout.connect(self.fill_table)

        root = QWidget()
        root.setObjectName('shell')
        # 注意：必须带 #shell 选择器限定自身；无选择器的 background 会波及全部子孙，
        # 把 #top/#tools/#statusbar 等统统刷成同一色（本程序顶栏发灰的历史根因）
        root.setStyleSheet('#shell { background:#163a5f; }')
        self.setCentralWidget(root)
        vbox = QVBoxLayout(root)
        vbox.setSpacing(0)
        vbox.setContentsMargins(0, 0, 0, 0)

        vbox.addWidget(self._build_top())
        vbox.addWidget(self._build_tools())
        vbox.addWidget(self._build_main(), 1)
        vbox.addWidget(self._build_status())

        self.setStyleSheet(QSS)
        self.build_tree()
        geo = self.settings.value('window/geometry')
        if geo:
            self.restoreGeometry(geo)
        try:
            tab_ix = int(self.settings.value('ui/tab', 0))
        except (TypeError, ValueError):
            tab_ix = 0
        if 0 <= tab_ix < len(self.tab_group):
            self.on_tab(tab_ix)

        # 半自动更新：启动后延迟静默检查一次（可在「关于」手动触发）
        if not UPDATE_DISABLED:
            QTimer.singleShot(4000, self._startup_check_update)

    def closeEvent(self, event):
        try:
            self._save_header_state()
            self.settings.setValue('window/geometry', self.saveGeometry())
            tab_ix = next((i for i, b in enumerate(self.tab_group)
                           if b.isChecked()), 0)
            self.settings.setValue('ui/tab', tab_ix)
            self.settings.sync()
        except Exception:
            logger.exception('保存窗口状态失败')
        logger.info('应用退出')
        super().closeEvent(event)

    def eventFilter(self, obj, event):
        """侧栏视口宽度变化时重算图形卡缩放，避免右侧标注被裁。"""
        side = getattr(self, 'side', None)
        if (side is not None and obj is side.viewport()
                and event.type() == QEvent.Resize):
            card = getattr(self, 'card', None)
            if card is not None:
                card.relayout_if_needed()
        return super().eventFilter(obj, event)

    # ---------------- 顶栏（.top）
    def _build_top(self):
        return build_topbar(self, APP_NAME, APP_VERSION_DISPLAY, APP_TAGLINE)
    # ---------------- 工具条（.tools 分类页签）
    def _build_tools(self):
        return build_tools(self, TABS, TPL_DIR)
    def on_tab(self, ix):
        # 再次点击当前页签时保留当前查询结果，只同步按钮状态
        if self._active_tab == ix:
            for j, b in enumerate(self.tab_group):
                b.setChecked(j == ix)
            return
        self._active_tab = ix
        for j, b in enumerate(self.tab_group):
            b.setChecked(j == ix)
        prefixes = TABS[ix][1]
        for i in range(self.tree.topLevelItemCount()):
            it = self.tree.topLevelItem(i)
            it.setHidden(not prefixes
                         or not any(it.text(0).startswith(p) for p in prefixes))
        self._save_header_state()
        self._clear_page()
        if not prefixes:
            self.cap.setText('该模块开发中：敬请期待')

    def _clear_page(self):
        """清空当前页数据、筛选器与侧栏详情，避免切换页签后残留上一页内容。"""
        self.cur_page = None
        self.cur_row = None
        self.current_cols = []
        self.rows = []
        self.head = []
        self.cur_kind = ''
        self.cur_view = 'flange'
        self.table.clearContents()
        self.table.setRowCount(0)
        self.table.setColumnCount(0)
        self.cap.setText('请选择左侧标准')
        self.count_lab.clear()
        self.chips.clear()
        self.t1.setText('请选择左侧法兰类型')
        self.t2.setText('选择类型后此处显示标准与单位')
        self.kv.clear_rows()
        self.card.reset()
        self._clear_filter_widgets()
        self.frow.addStretch(1)
        self.st_msg.setText('就绪')
        self.st_tpl.clear()
        self.st_anchor.clear()
        self.tree.clearSelection()
        self.tree.setCurrentItem(None)

    # ---------------- 三栏（.main）
    def _build_main(self):
        split = QSplitter()
        split.setHandleWidth(6)
        split.setChildrenCollapsible(False)
        self.center = build_center_panel(self)
        self.side = build_side_panel(self)
        self.data_page = QWidget()
        dl = QHBoxLayout(self.data_page)
        dl.setContentsMargins(0, 0, 0, 0)
        dl.setSpacing(0)
        dl.addWidget(self.center, 1)
        dl.addWidget(self.side)
        self.weight_page = WeightPage()
        self.metal_weight_page = MetalWeightPage()
        self.selection_page = SelectionPage()
        self.main_stack = QStackedWidget()
        self.main_stack.addWidget(self.data_page)
        self.main_stack.addWidget(self.weight_page)
        self.main_stack.addWidget(self.metal_weight_page)
        self.main_stack.addWidget(self.selection_page)
        split.addWidget(build_tree_panel(self))
        split.addWidget(self.main_stack)
        split.setSizes([220, 1210])
        return split

    def show_weight_page(self, kind):
        if kind == 'metal':
            self.main_stack.setCurrentWidget(self.metal_weight_page)
            return
        self.main_stack.setCurrentWidget(self.weight_page)
        self.weight_page.show_kind(kind)

    def show_selection_page(self, kind):
        self.main_stack.setCurrentWidget(self.selection_page)
        self.selection_page.show_kind(kind)
    # ---------------- 状态栏（.status 多段）
    def _build_status(self):
        return build_statusbar(self)
    # ---------------- 树
    def build_tree(self):
        for std, items in PAGES:
            top = QTreeWidgetItem([std])
            top.setFlags(Qt.ItemIsEnabled)
            f = top.font(0)
            f.setBold(True)
            top.setFont(0, f)
            top.setForeground(0, QColor('#1f4e79'))
            self.tree.addTopLevelItem(top)
            for page in items:
                name, csvf, tpl, labels = page[:4]
                if page.kind not in ('weight', 'selection') and find_data(csvf) is None:
                    continue
                ch = QTreeWidgetItem([name])
                ch.setData(0, Qt.UserRole,
                           (name, csvf, tpl, labels, std, page))
                top.addChild(ch)
        self.tree.expandAll()

    def filter_tree(self, text):
        text = text.strip().lower()
        for i in range(self.tree.topLevelItemCount()):
            top = self.tree.topLevelItem(i)
            top_hit = text in top.text(0).lower()
            any_child = False
            for j in range(top.childCount()):
                ch = top.child(j)
                hit = top_hit or text in ch.text(0).lower()
                ch.setHidden(bool(text) and not hit)
                any_child = any_child or hit
            top.setHidden(bool(text) and not (top_hit or any_child))

    def _clear_detail(self):
        """清空右侧详情，避免切换标准后仍显示上一页的行数据。"""
        self.cur_row = None
        self.kv.clear_rows()
        self.card.reset()
        self.st_tpl.clear()
        self.st_anchor.clear()

    def on_tree(self, item, _col):
        on_tree(self, item, _col)
    # ---------------- 动态筛选器
    def _clear_filter_widgets(self):
        clear_filter_widgets(self)

    def build_filters(self):
        build_filters(self)

    def _enum_values(self, col, disp=None):
        return enum_values(self, col, disp)

    def on_filter_changed(self, _text=''):
        on_filter_changed(self, _text)

    def _schedule_filter(self, _text=''):
        schedule_filter(self, _text)

    def reset_filters(self):
        reset_filters(self)

    def _match(self, r, col, val):
        return match(self, r, col, val)

    def _filtered_rows(self):
        return filtered_rows(self)
    def fill_table(self):
        fill_table(self)
    def on_row(self):
        on_row(self)
    def _selected_rows(self):
        """按表格行序返回选中的数据行（多选时去重）。"""
        indexes = sorted({i.row() for i in self.table.selectedIndexes()})
        rows = []
        for index in indexes:
            item = self.table.item(index, 0)
            if item is not None:
                rows.append(item.data(Qt.UserRole))
        return rows

    def copy_selected_rows(self):
        rows = self._selected_rows()
        if not rows:
            QMessageBox.information(self, '提示', '请先在表格中选择行')
            return
        QApplication.clipboard().setText(rows_to_tsv(rows, self.current_cols))
        self.st_msg.setText('已复制 %d 行 × %d 列到剪贴板'
                            % (len(rows), len(self.current_cols)))

    def show_table_menu(self, pos):
        menu = QMenu(self)
        act_copy = menu.addAction('复制选中行\tCtrl+C')
        act_export = menu.addAction('导出选中行…')
        act_all = menu.addAction('导出当前筛选结果…')
        chosen = menu.exec_(self.table.viewport().mapToGlobal(pos))
        if chosen is act_copy:
            self.copy_selected_rows()
        elif chosen is act_export:
            self.do_export_selected()
        elif chosen is act_all:
            self.do_export()

    def do_export_selected(self):
        export_selected(self)
    # ---------------- 列宽记忆
    def _header_key(self, csvf):
        return 'table/header/%s' % csvf

    def _save_header_state(self):
        if not getattr(self, 'cur_page', None):
            return
        try:
            self.settings.setValue(self._header_key(self.cur_page[1]),
                                   self.table.horizontalHeader().saveState())
        except Exception:
            logger.exception('保存列宽失败')

    def _restore_header_state(self, csvf):
        state = self.settings.value(self._header_key(csvf))
        if state:
            try:
                self.table.horizontalHeader().restoreState(state)
            except Exception:
                logger.exception('恢复列宽失败')

    def show_search(self):
        dlg = SearchDialog(search_all, self)
        dlg.row_chosen.connect(self.open_search_result)
        dlg.exec_()

    def show_coverage(self):
        CoverageDialog(self).exec_()

    def open_search_result(self, csvf, row):
        target = None
        for i in range(self.tree.topLevelItemCount()):
            top = self.tree.topLevelItem(i)
            for j in range(top.childCount()):
                child = top.child(j)
                meta = child.data(0, Qt.UserRole)
                if meta and meta[1] == csvf:
                    target = child
                    break
            if target is not None:
                break
        if target is None:
            return
        self.on_tree(target, 0)
        for i in range(self.table.rowCount()):
            item = self.table.item(i, 0)
            if item is not None and item.data(Qt.UserRole) == row:
                self.table.selectRow(i)
                self.table.scrollToItem(item)
                break

    def show_about(self):
        n_groups = len(PAGES)
        n_pages = sum(len(items) for _, items in PAGES)
        sample = find_data('HGT20592_带颈对焊.csv')
        dlg = QDialog(self)
        dlg.setWindowTitle('关于')
        dlg.setMinimumWidth(440)
        layout = QVBoxLayout(dlg)
        info = ('%s %s\n\n标准组：%d 组 / %d 个子页\n数据目录：%s\n日志文件：%s\n\n'
                '数据复核状态与来源说明见 README.md。'
                % (APP_NAME, APP_VERSION_DISPLAY, n_groups, n_pages,
                   os.path.dirname(sample) if sample else '未找到',
                   LOG_FILE or '（未初始化）'))
        layout.addWidget(QLabel(info))
        btn_box = QHBoxLayout()
        btn_check = QPushButton('检查更新')
        btn_check.clicked.connect(self._manual_check)
        btn_close = QPushButton('关闭')
        btn_close.clicked.connect(dlg.accept)
        btn_box.addStretch(1)
        btn_box.addWidget(btn_check)
        btn_box.addWidget(btn_close)
        layout.addLayout(btn_box)
        dlg.exec_()

    # ---------------- 半自动更新
    def _startup_check_update(self):
        if UPDATE_DISABLED:
            return
        logger.info('开始检查更新（当前 %s）', APP_VERSION_DISPLAY)
        self._uc = UpdateChecker(APP_VERSION)
        self._uc.check_done.connect(self._on_check_done)
        self._uc.start()

    def _on_check_done(self, r):
        if r.get('error'):
            logger.warning('更新检查失败（已静默忽略）：%s', r['error'])
            return
        if r.get('need'):
            self._prompt_update(r['info'])

    def _manual_check(self):
        if UPDATE_DISABLED:
            QMessageBox.information(
                self, '检查更新',
                '自动更新已禁用（环境变量 FLANGE_NO_UPDATE=1）')
            return
        self._mc = UpdateChecker(APP_VERSION)
        self._mc.check_done.connect(self._on_manual_check_done)
        self._mc.start()

    def _on_manual_check_done(self, r):
        if r.get('error'):
            QMessageBox.warning(self, '检查更新', '检查失败：%s' % r['error'])
            return
        if r.get('need'):
            self._prompt_update(r['info'])
        else:
            QMessageBox.information(
                self, '检查更新', '当前已是最新版本（%s）' % APP_VERSION_DISPLAY)

    def _prompt_update(self, info):
        latest = info.get('latest', '?')
        notes = info.get('notes', '（未提供更新说明）')
        msg = ('发现新版本 %s（当前 %s）\n\n更新内容：\n%s\n\n是否立即更新？'
               '（更新会下载新版并重启程序）'
               % (latest, APP_VERSION_DISPLAY, notes))
        logger.info('提示更新：当前 %s → 最新 %s', APP_VERSION_DISPLAY, latest)
        btn = QMessageBox.question(
            self, '发现新版本', msg,
            QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if btn == QMessageBox.Yes:
            self._do_update(info)
        else:
            logger.info('用户选择暂不更新')

    def _do_update(self, info):
        logger.info('开始下载更新：%s', info.get('latest'))
        self.statusBar().showMessage('正在下载更新…（完成后自动重启）')
        self._dl = UpdateDownloader(APP_VERSION, info)
        self._dl.dl_done.connect(self._on_dl_done)
        self._dl.dl_progress.connect(self._on_dl_progress)
        self._dl.start()

    def _on_dl_progress(self, got, total):
        if total:
            self.statusBar().showMessage(
                '正在下载更新… %d%%（%.1f / %.1f MB）'
                % (got * 100 // total, got / 1048576.0, total / 1048576.0))

    def _on_dl_done(self, r):
        if not r.get('ok'):
            logger.warning('下载更新失败：%s', r.get('error'))
            QMessageBox.critical(
                self, '更新失败', '下载或校验失败：%s' % r.get('error'))
            self.statusBar().showMessage('更新失败')
            return
        new_exe = r.get('new_exe')
        new_setup = r.get('new_setup')
        if new_exe:
            ok = apply_exe_and_restart(new_exe)
        elif new_setup:
            ok = apply_setup_and_restart(new_setup)
        else:
            ok = apply_and_restart(r.get('new_dir'))
        logger.info('更新包已就绪，触发重启=%s（%s）', ok,
                    new_exe or new_setup or r.get('new_dir'))
        if ok:
            self.statusBar().showMessage('更新就绪，即将重启…')
            QApplication.quit()
        else:
            self.statusBar().showMessage('更新未触发（DRY_RUN）')

    # ---------------- 打印 / 导出
    def do_print(self):
        do_print(self)

    def _render_print_page(self, printer):
        render_print_page(self, printer)
    def do_export(self):
        export_all(self, SHOW_COLS)

    def do_export_row(self):
        export_row(self)

    def do_export_vector(self):
        export_vector(self)


def main():
    setup_logging()
    logger.info('启动 %s', APP_VERSION_DISPLAY)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    if os.path.exists(ICON_PATH):
        app.setWindowIcon(QIcon(ICON_PATH))
    w = MainWindow()
    w.show()
    rc = app.exec_()
    logger.info('退出码 %s', rc)
    sys.exit(rc)


if __name__ == '__main__':
    main()