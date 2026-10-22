# -*- coding: utf-8 -*-
"""汇总所有实操课页面数据"""
from pdata_w import PAGES as W

PAGES = list(W)

for mod in ("pdata_s", "pdata_s2", "pdata_s3", "pdata_p"):
    try:
        m = __import__(mod)
        PAGES += list(m.PAGES)
    except ImportError:
        pass
