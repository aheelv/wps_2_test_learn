# -*- coding: utf-8 -*-
"""核对并同步三处「起始素材」文本：网页录入素材块 / exercises.json 的 src / 素材包实际内容。

判定规则：以素材包为准，页面与题库必须「包含」素材包的全部起始文字
（页面允许额外加「第 N 段」这类定位标注）。

页面编辑以 <article class="ex"> 为操作单元，避免跨题替换破坏 DOM 结构。

用法：
    python tools/material/sync_src.py --check   # 只比对并报告差异
    python tools/material/sync_src.py --fix     # 以素材包为准回填网页与题库
"""
import html as H
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
MAT = ROOT / "练习素材"
PAGES = ["入门实操课.html", "实操-文字2.html", "实操-文字3.html", "实操-表格1.html",
         "实操-表格2.html", "实操-表格3.html", "实操-演示1.html", "实操-演示2.html"]
PAGE_CI = {p: i + 1 for i, p in enumerate(PAGES)}
KICKER_TEXT = "录入素材（素材包内的起始文字，按此录入 / 打开排版）"
LABEL_RE = re.compile(r"^（第\s*\d+\s*段）\s*")
ART_RE = re.compile(r'(<article class="ex"[^>]*>)(.*?)</article>', re.S)


def norm(s):
    s = H.unescape(re.sub(r"<[^>]+>", "", str(s or "")))
    return re.sub(r"\s+", "", LABEL_RE.sub("", s.strip()))


def lines_of(txt):
    return [x.strip() for x in str(txt or "").splitlines() if x.strip()]


def extract_pre(art):
    i = art.find('<div class="src">')
    if i < 0:
        return None
    m = re.search(r"<pre>(.*?)</pre>", art[i:], re.S)
    return m.group(1) if m else None


def page_blocks():
    """{(ci,seq): (页文件, 文章块内容, src 文本)}"""
    out = {}
    for p in PAGES:
        t = (ROOT / p).read_text(encoding="utf-8")
        ci = PAGE_CI[p]
        for j, m in enumerate(ART_RE.finditer(t), 1):
            out[(ci, j)] = (p, m.group(2), extract_pre(m.group(2)))
    return out


def pkg_groups(ci, seq):
    """返回 [(文件名, [起始文字行…])]，只取可作为「起始素材」的文档类文件"""
    d = None
    for x in sorted(os.listdir(MAT)):
        if x.startswith("练习%d-%d-" % (ci, seq)) and os.path.isdir(MAT / x):
            d = MAT / x
            break
    if not d:
        return []
    groups = []
    for f in sorted(os.listdir(d)):
        if f.startswith("~$"):
            continue
        p = d / f
        if f.endswith(".docx"):
            from docx import Document
            ls = [x.text.strip() for x in Document(str(p)).paragraphs if x.text.strip()]
            if ls:
                groups.append((f, ls))
        elif f.endswith(".txt") and f != "素材说明.txt":
            ls = lines_of(p.read_text(encoding="utf-8", errors="replace"))
            if ls:
                groups.append((f, ls))
    return groups


def build_pre(groups, page_pre=None):
    """多文档题按文件分区展示；单文档题直接给出全文。

    已有页面文本时做「合并」：保留页面的定位标注（如「第 1 段」），
    只补上素材包里页面缺失的行，并按素材包顺序排列。
    """
    if len(groups) <= 1:
        pkg = list(groups[0][1]) if groups else []
    else:
        pkg = []
        for fn, ls in groups:
            pkg.append("【%s】" % fn)
            pkg += ls
            pkg.append("")
        pkg = [x for x in pkg if x != ""] or pkg
    if page_pre is None:
        return "\n".join(pkg)
    page_lines = lines_of(page_pre)
    used, out = set(), []
    for pl in pkg:
        hit = None
        for i, ql in enumerate(page_lines):
            if i in used:
                continue
            nq, np_ = norm(ql), norm(pl)
            if np_ and (nq.endswith(np_) or np_ in nq):
                hit = ql
                used.add(i)
                break
        out.append(hit if hit is not None else pl)
    for i, ql in enumerate(page_lines):
        if i not in used:
            out.append(ql)
    return "\n".join(out)


def replace_src(art, new_pre):
    """在文章块内替换 / 插入 录入素材 区块，返回新文章块"""
    block = ('<div class="src">\n              <div class="kicker">%s</div>\n'
             '              <pre>%s</pre>\n            </div>\n'
             % (KICKER_TEXT, H.escape(new_pre)))
    i = art.find('<div class="src">')
    if i >= 0:
        j = art.find('</pre>', i)
        e = art.find('</div>', j) + len('</div>')
        return art[:i] + block.rstrip("\n") + art[e:]
    k = art.find('<div class="req">')
    if k < 0:
        return art
    e = art.find('</ol>', k)
    e = art.find('</div>', e) + len('</div>')
    return art[:e] + "\n            " + block.rstrip("\n") + art[e:]


def main():
    mode = "--fix" if "--fix" in sys.argv else "--check"
    blocks = page_blocks()
    E = json.loads((HERE / "exercises.json").read_text(encoding="utf-8"))
    by = {(q["ci"], q["seq"]): q for q in E}
    changed = {}
    changed_json = 0
    report = []

    for key in sorted(blocks):
        ci, seq = key
        q = by.get(key)
        if not q:
            continue
        page, art, pre = blocks[key]
        groups = pkg_groups(ci, seq)
        if not groups:
            continue
        pkg_lines = []
        for _, ls in groups:
            pkg_lines += ls
        if not pkg_lines:
            continue
        page_norm = {norm(x) for x in lines_of(pre or "")}
        json_norm = {norm(x) for x in lines_of(str(q.get("src") or ""))}
        miss_page = [x for x in pkg_lines if norm(x) not in page_norm]
        miss_json = [x for x in pkg_lines if norm(x) not in json_norm]
        mism = []
        if pre is None:
            mism.append("页面无录入素材块")
        elif miss_page:
            mism.append("页面录入素材缺少 %d 行素材内容" % len(miss_page))
        if miss_json:
            mism.append("题库 src 缺少 %d 行素材内容" % len(miss_json))
        if not mism:
            continue
        report.append((page, q["no"], mism))
        print("[%s] %s（%s）" % (page, q["no"], q["title"]))
        for m in mism:
            print("    - " + m)
        if mode == "--fix":
            new_art = replace_src(art, build_pre(groups, pre))
            changed.setdefault(page, {})[seq] = new_art
            q["src"] = "\n".join(pkg_lines)
            changed_json += 1

    if mode == "--fix" and changed:
        for page, items in changed.items():
            p = ROOT / page
            t = p.read_text(encoding="utf-8")
            reps = []
            for j, m in enumerate(ART_RE.finditer(t), 1):
                if j in items:
                    reps.append((m.start(), m.end(), m.group(1) + items[j] + '</article>'))
            for s, e, new in sorted(reps, key=lambda x: -x[0]):
                t = t[:s] + new + t[e:]
            p.write_text(t, encoding="utf-8")
            print("已更新页面：%s（%d 题）" % (page, len(items)))
        with open(HERE / "exercises.json", "w", encoding="utf-8") as f:
            json.dump(E, f, ensure_ascii=False, indent=1)
        print("已更新题库 src：%d 题" % changed_json)
    print("\n差异题数：%d" % len(report))


if __name__ == "__main__":
    main()
