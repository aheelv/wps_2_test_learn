# -*- coding: utf-8 -*-
"""把「题目要求」与「素材包真实内容」并排导出，供逐题人工核对。

用法：
    python tools/material/dump_mat.py            # 全部 72 题
    python tools/material/dump_mat.py 4 5        # 只看第 4、5 次课
    python tools/material/dump_mat.py --dir 11-11   # 只看某个外部素材目录
"""
import json
import os
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
MAT = ROOT / "练习素材"


def brief(v, n=26):
    s = "" if v is None else str(v)
    s = " ".join(s.split())
    return s if len(s) <= n else s[: n - 1] + "…"


def dump_docx(p):
    from docx import Document
    d = Document(str(p))
    out = ["段落 %d 个" % len(d.paragraphs)]
    txt = [x.text.strip() for x in d.paragraphs if x.text.strip()]
    out.append("正文: " + " ⏐ ".join(brief(t) for t in txt[:8]))
    if d.tables:
        out.append("表格 %d 个" % len(d.tables))
        for ti, tb in enumerate(d.tables[:2]):
            rows = []
            for r in tb.rows[:4]:
                rows.append("|".join(brief(c.text, 14) for c in r.cells))
            out.append("  表%d: %s" % (ti + 1, " / ".join(rows)))
    return out


def dump_xlsx(p):
    import openpyxl
    wb = openpyxl.load_workbook(str(p), data_only=False)
    out = []
    for ws in wb.worksheets:
        out.append("表「%s」 %dx%d" % (ws.title, ws.max_row, ws.max_column))
        for r in ws.iter_rows(min_row=1, max_row=min(ws.max_row, 8), values_only=True):
            out.append("    " + " | ".join(brief(v) for v in r))
        if ws.max_row > 8:
            out.append("    …")
    return out


def dump_pptx(p):
    from pptx import Presentation
    pr = Presentation(str(p))
    out = ["幻灯片 %d 页" % len(pr.slides)]
    for i, s in enumerate(pr.slides, 1):
        texts = []
        for sh in s.shapes:
            if sh.has_text_frame and sh.text_frame.text.strip():
                texts.append(brief(sh.text_frame.text, 40))
        out.append("  第%d张: %s" % (i, " ⏐ ".join(texts) if texts else "(无文本占位)"))
    return out


def dump_txt(p):
    t = Path(p).read_text(encoding="utf-8", errors="replace")
    lines = [x for x in t.splitlines() if x.strip()]
    return ["文本 %d 行" % len(lines)] + ["    " + brief(x, 60) for x in lines[:14]]


def dump_pkg(pkgdir):
    out = []
    for f in sorted(os.listdir(pkgdir)):
        if f.startswith("~$") or f.startswith("."):
            continue
        fp = os.path.join(pkgdir, f)
        out.append("--- %s (%d B)" % (f, os.path.getsize(fp)))
        try:
            if f.endswith(".docx"):
                out += dump_docx(fp)
            elif f.endswith(".xlsx"):
                out += dump_xlsx(fp)
            elif f.endswith(".pptx"):
                out += dump_pptx(fp)
            elif f.endswith(".txt"):
                out += dump_txt(fp)
            elif f.endswith(".png"):
                from PIL import Image
                im = Image.open(fp)
                out.append("图片 %dx%d" % im.size)
            elif f.endswith(".wav"):
                out.append("音频")
            elif f.endswith(".mp4"):
                out.append("视频")
        except Exception as e:
            out.append("    !! 读取失败: %s" % e)
    return out


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    E = json.loads((HERE / "exercises.json").read_text(encoding="utf-8"))
    src_dir = None
    if "--dir" in sys.argv:
        src_dir = ROOT / sys.argv[sys.argv.index("--dir") + 1]
    cis = [int(x) for x in args] if args else None
    for q in E:
        if cis and q["ci"] not in cis:
            continue
        if src_dir:
            cands = [d for d in sorted(os.listdir(src_dir)) if d.startswith("练习%d-%d-" % (q["ci"], q["seq"]))]
            if not cands:
                continue
            pkg = str(src_dir / cands[0])
            tag = "【外部目录】"
        else:
            pkg = None
            for d in sorted(os.listdir(MAT)):
                if d.startswith("练习%d-%d-" % (q["ci"], q["seq"])) and os.path.isdir(MAT / d):
                    pkg = str(MAT / d)
                    break
            tag = "【站内】"
        print("=" * 100)
        print("%s %s ｜ %s" % (tag, q["no"], q["title"]))
        print("归属: 第 %d 次课 ｜ 页面: %s" % (q["ci"], q["page"]))
        print("题目要求:")
        for i, r in enumerate(q["reqs"], 1):
            print("   %d) %s" % (i, r))
        if q.get("src"):
            print("起始素材(src):")
            for ln in str(q["src"]).splitlines():
                if ln.strip():
                    print("   · " + brief(ln, 90))
        print("采分点: %s" % brief(q.get("score", ""), 200))
        print("步骤首条: %s" % brief(q["steps"][0] if q["steps"] else "", 120))
        if pkg:
            print("素材包 %s:" % os.path.basename(pkg))
            for line in dump_pkg(pkg):
                print("   " + line)
        else:
            print("素材包: !! 未找到")
        print()


if __name__ == "__main__":
    main()
