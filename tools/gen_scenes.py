# -*- coding: utf-8 -*-
"""gen_scenes.py —— 生成全部示意图：python tools/gen_scenes.py"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import scenes_a
import scenes_b

scenes_a.build_l1()
scenes_a.build_l2()
scenes_b.build_l3()
scenes_b.build_l4()

out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "wps-img")
files = sorted(f for f in os.listdir(out) if f.endswith(".svg"))
total = 0
for f in files:
    total += os.path.getsize(os.path.join(out, f))
print("生成 %d 张示意图，总计 %.1f KB" % (len(files), total / 1024.0))
for f in files:
    print("  ", f)
