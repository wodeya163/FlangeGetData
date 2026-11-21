# -*- coding: utf-8 -*-
"""路径、缩放与实验开关。"""

import logging
import os
import sys

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES_DIR = getattr(sys, '_MEIPASS', APP_DIR)
TPL_DIR = os.path.join(RES_DIR, 'templates')
SCALE = 0.7
VECTOR_ENABLED = os.environ.get('FLANGE_VECTOR') == '1'
# 波纹管矢量图默认启用；FLANGE_BELLOWS_VECTOR=0 可强制回退 BMP
BELLOWS_VECTOR_ENABLED = os.environ.get('FLANGE_BELLOWS_VECTOR', '1') != '0'
# 法兰矢量图默认启用；FLANGE_FLANGE_VECTOR=0 可强制回退 BMP
FLANGE_VECTOR_ENABLED = os.environ.get('FLANGE_FLANGE_VECTOR', '1') != '0'
logger = logging.getLogger('flangequery')
