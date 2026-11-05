# -*- coding: utf-8 -*-
"""图形预览：python _preview.py figs_w w1_1 w1_2 ...  → _preview.html"""
import sys, os, importlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

mod = importlib.import_module(sys.argv[1])
keys = sys.argv[2:]
if not keys:
    keys = list(mod.REG.keys())

parts = []
for k in keys:
    f = mod.REG[k]()
    legs = "".join('<span class="lg"><i>%d</i>%s</span>' % (n, t) for n, t in f.marks())
    parts.append('<div class="fw"><div class="cap">%s</div>%s<div class="leg">%s</div></div>'
                 % (k, f.svg(), legs))

TPL = """<!DOCTYPE html><html><head><meta charset="utf-8"><style>
body{margin:0;background:#eceff3;font-family:"Microsoft YaHei"}
.fw{width:1000px;margin:10px auto;background:#fff;padding:8px 0 10px}
.cap{font-size:12px;color:#888;padding:2px 8px}
.leg{font-size:12.5px;color:#333;padding:8px 14px 0;line-height:1.9}
.lg{margin-right:18px;white-space:nowrap}
.lg i{display:inline-block;width:16px;height:16px;border-radius:50%;background:#e8710a;color:#fff;
font-style:normal;font-size:11px;text-align:center;line-height:16px;margin-right:5px}
</style></head><body>@@BODY@@</body></html>"""
html = TPL.replace("@@BODY@@", "".join(parts))
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "_preview.html"), "w",
     encoding="utf-8").write(html)
print("ok", len(keys), "figs")
