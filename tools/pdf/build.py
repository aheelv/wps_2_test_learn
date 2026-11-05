# -*- coding: utf-8 -*-
"""生成三份 PDF：两次渲染回填目录页码，并做覆盖性校验"""
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pymupdf
from pypdf import PdfReader, PdfWriter

from docgen import Builder
import data_w
import data_s
import data_p

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, "..", "..", "实操训练三部分"))
TMP = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)
os.makedirs(TMP, exist_ok=True)

DOCS = [
    (data_w.DOC, "实操训练 第一部分 · 文字处理（30 分）"),
    (data_s.DOC, "实操训练 第二部分 · 电子表格（30 分）"),
    (data_p.DOC, "实操训练 第三部分 · 演示文稿（20 分）"),
]
FILES = {
    "A": "实操训练-第一部分-文字处理.pdf",
    "B": "实操训练-第二部分-电子表格.pdf",
    "C": "实操训练-第三部分-演示文稿.pdf",
}


def norm(s):
    return re.sub(r"[\s\u3000]+", "", s)


def render_pdf(html_path, pdf_path, header_title, header_sub):
    r = subprocess.run(
        ["node", os.path.join(HERE, "render.mjs"), html_path, pdf_path,
         "--title=" + header_title, "--sub=" + header_sub],
        capture_output=True, text=True, encoding="utf-8",
    )
    if r.returncode != 0:
        raise RuntimeError(r.stdout + r.stderr)
    return r.stdout.strip()


def page_map(pdf_path, entries):
    doc = pymupdf.open(pdf_path)
    texts = [norm(p.get_text()) for p in doc]
    # 目录页位置（通过唯一句定位）
    toc_idx = 0
    for i, t in enumerate(texts):
        if "页码为本册实际页序" in t:
            toc_idx = i
            break
    m = {}
    misses = []
    for level, num, title in entries:
        key = norm(num + title)
        found = None
        for i in range(toc_idx + 1, len(texts)):
            if key and key in texts[i]:
                found = i + 1
                break
        if found is None:
            for i in range(toc_idx + 1, len(texts)):
                if norm(title) and norm(title) in texts[i]:
                    found = i + 1
                    break
        if found is None:
            misses.append((level, num, title))
            continue
        m[num + title] = str(found)
    return m, misses, len(texts)


def validate(doc):
    errs = []
    codes = {k[0] for k in doc["kps"]}
    seen = set()
    for e in doc["exercises"]:
        if e["no"] in seen:
            errs.append("重复题号 " + e["no"])
        seen.add(e["no"])
        if len(e["covers"]) < 2:
            errs.append(e["no"] + " 覆盖知识点不足 2 个")
        for c in e["covers"]:
            if c not in codes:
                errs.append("%s 引用了不存在的知识点 %s" % (e["no"], c))
    covered = {c for e in doc["exercises"] for c in e["covers"]}
    miss = codes - covered
    if miss:
        errs.append("未被任何练习覆盖的知识点：" + "、".join(sorted(miss)))
    # 难度递增
    stars = [e["star"] for e in doc["exercises"]]
    if stars != sorted(stars):
        errs.append("练习难度未按升序排列")
    # 知识点编号连续
    for i, k in enumerate(doc["kps"]):
        if k[0] != "%s%02d" % (doc["kp_prefix"], i + 1):
            errs.append("知识点编号不连续：" + k[0])
    # 考纲条目是否都有知识点
    sylan = {k[2] for k in doc["kps"]}
    for s in doc["syl"]:
        if s not in sylan:
            errs.append("考纲条目无知识点：" + s)
    return errs


def exercise_pages(pdf_path, doc, after_page):
    """在练习总览页之后定位每道练习的起始页"""
    d = pymupdf.open(pdf_path)
    texts = [norm(p.get_text()) for p in d]
    out = []
    card_pages = [i for i in range(after_page + 1, len(texts)) if "操作目标" in texts[i]]
    if len(card_pages) == len(doc["exercises"]):
        pairs = list(zip(doc["exercises"], card_pages))
    else:
        pairs = []
        cur = after_page + 1
        for e in doc["exercises"]:
            key = norm(e["no"] + e["title"])[:24]
            pg = None
            for i in range(cur, len(texts)):
                if key in texts[i] and "操作目标" in texts[i]:
                    pg = i
                    break
            if pg is None:
                for i in range(cur, len(texts)):
                    if key in texts[i]:
                        pg = i
                        break
            if pg is not None:
                pairs.append((e, pg))
                cur = pg
    for e, pg in pairs:
        out.append((e["no"] + "　" + e["title"], pg))
    return out


def add_outline(pdf_path, entries, pm, header, doc=None):
    r = PdfReader(pdf_path)
    w = PdfWriter()
    w.append(r)
    items = []
    for level, num, title in entries:
        key = num + title
        if key in pm:
            label = (num + "　" + title) if level == 1 else title
            items.append((level, label, int(pm[key]) - 1))
    # 在「第四章」下补练习级书签
    if doc is not None and "4.0练习总览" in pm:
        exs = exercise_pages(pdf_path, doc, int(pm["4.0练习总览"]) - 1)
        cut = len(items)
        for i, (lv, lab, _) in enumerate(items):
            if lv == 1 and lab.startswith("第五章"):
                cut = i
                break
        items[cut:cut] = [(2, lab, pg) for lab, pg in exs]
    last = None
    for level, label, pg in items:
        if level == 1:
            last = w.add_outline_item(label, pg)
        else:
            w.add_outline_item(label, pg, parent=last)
    w.add_metadata({
        "/Title": header,
        "/Author": "大连财经学院 · 计算机国家二级考试（WPS 类）课程组",
        "/Subject": "全国计算机等级考试二级 WPS Office 高级应用与设计 · 实操训练",
        "/Keywords": "NCRE 二级 WPS Office 实操训练 知识点 练习",
    })
    tmp = pdf_path + ".tmp"
    with open(tmp, "wb") as f:
        w.write(f)
    os.replace(tmp, pdf_path)


def build(doc, header):
    b = Builder(doc)
    html = b.build({})
    p1 = os.path.join(TMP, doc["code"] + "-p1.html")
    pdf1 = os.path.join(TMP, doc["code"] + "-p1.pdf")
    with open(p1, "w", encoding="utf-8") as f:
        f.write(html)
    render_pdf(p1, pdf1, header, "%s · 知识点与实操练习" % doc["name"])
    pm, misses, n = page_map(pdf1, b.toc_entries)

    final = os.path.join(OUT, FILES[doc["code"]])
    for attempt in range(3):
        html = b.build(pm)
        p2 = os.path.join(TMP, doc["code"] + "-p2.html")
        pdf2 = final
        with open(p2, "w", encoding="utf-8") as f:
            f.write(html)
        render_pdf(p2, pdf2, header, "%s · 知识点与实操练习" % doc["name"])
        pm2, misses2, n2 = page_map(pdf2, b.toc_entries)
        if pm2 == pm:
            add_outline(final, b.toc_entries, pm2, header, doc)
            return final, n2, misses2, attempt + 1
        pm = pm2
    add_outline(final, b.toc_entries, pm2, header, doc)
    return final, n2, misses2, 3


def main():
    summary = []
    only = set(sys.argv[1:])
    for doc, header in DOCS:
        if only and doc["code"] not in only:
            continue
        errs = validate(doc)
        path, pages, misses, rounds = build(doc, header)
        size = os.path.getsize(path) / 1024 / 1024
        summary.append((doc["part"], doc["name"], len(doc["kps"]), len(doc["exercises"]),
                        pages, rounds, len(misses), "%.1fMB" % size, errs))
        print("=== %s %s" % (doc["part"], doc["name"]))
        print("  知识点 %d / 练习 %d / 页数 %d / 回填轮次 %d / 目录缺页码 %d / %s"
              % (len(doc["kps"]), len(doc["exercises"]), pages, rounds, len(misses), "%.1fMB" % size))
        if misses:
            for m in misses:
                print("   MISS", m)
        if errs:
            for e in errs:
                print("   ERR", e)
        else:
            print("   校验：通过")
    print("\n输出目录：", OUT)
    for s in summary:
        print("  %s %s  %s" % (s[0], s[1], s[7]))


if __name__ == "__main__":
    main()
