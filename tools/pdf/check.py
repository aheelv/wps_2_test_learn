# -*- coding: utf-8 -*-
"""检查 PDF 的版面密度：找出留白过多的页（排版断页不佳）"""
import sys
import pymupdf

for path in sys.argv[1:]:
    d = pymupdf.open(path)
    print("==", path, d.page_count, "页")
    sparse = []
    for i, p in enumerate(d):
        blocks = [b for b in p.get_text("blocks") if b[4].strip() and b[3] < p.rect.height - 60]
        if not blocks:
            continue
        bottom = max(b[3] for b in blocks)
        ratio = bottom / (p.rect.height - 55)
        if ratio < 0.62:
            first = blocks[0][4].strip().split("\n")[0][:24]
            sparse.append((i + 1, round(ratio, 2), first))
    if sparse:
        for s in sparse:
            print("   稀疏页 p%02d  填充 %s  «%s»" % s)
    else:
        print("   无明显稀疏页")
