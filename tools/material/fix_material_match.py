# -*- coding: utf-8 -*-
"""全量逐题核对后的最小必要修订（幂等）。

依据 tools/material/match_report.json 的结论，只修订确认有误的内容：
  1. 例 4-1  素材数据集改为题干声明的 12 条销售记录、仅保留 Sheet1；
             标题 / 采分点「4 张工作表」订正为「3 张工作表」。
  2. 例 7-1  大纲.txt 改为题干声明的 8 条大纲。
  3. 例 7-2/3/4/5/8、例 8-3 起始文稿补足到题目涉及的页序。
  4. 例 7-8  补教学视频.mp4、移除无关的图表数据.xlsx、步骤写明素材文件名。
  5. 例 8-7  移除无关的图表数据.xlsx。
  6. 例 8-8  评分表改为第 8-7 题 10 项采分点 × 2 分 = 20 分。

本脚本负责：网页题目文本 → exercises.json → 72 个素材包 / zip / manifest
→ 网页素材块。操作示意 SVG、完成比对文档、索引页与校验报告由后续脚本重跑。
用法：python tools/material/fix_material_match.py
"""
import os, re, sys, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build as B
import fix_link
import patch_html

TITLE_OLD = '建工作簿：4 张工作表 + 标签颜色 + 列宽行高 + 冻结首行'
TITLE_NEW = '建工作簿：3 张工作表 + 标签颜色 + 列宽行高 + 冻结首行'

PAIRS = {
    '实操-表格1.html': [
        # 课页索引里的题名是截断显示，用最短公共子串覆盖全部 3 处
        ('4 张工作表', '3 张工作表'),
    ],
    '实操训练.html': [
        (TITLE_OLD, TITLE_NEW),
    ],
    '实操-演示1.html': [
        ('<li>在第 1 张插入素材音频，设置：',
         '<li>在第 1 张插入素材包中的 <code>背景音乐.wav</code>，设置：'),
        ('<li>在第 7 张插入素材视频，设置：',
         '<li>在第 7 张插入素材包中的 <code>教学视频.mp4</code>，设置：'),
        ('→「本地音频」→ 选文件 → 出现喇叭图标。',
         '→「本地音频」→ 选 <code>背景音乐.wav</code> → 出现喇叭图标。'),
        ('→「本地视频」→ 选文件。',
         '→「本地视频」→ 选 <code>教学视频.mp4</code>。'),
    ],
}


def replace_in(path, pairs):
    p = ROOT / path
    s = p.read_text(encoding='utf-8')
    n = 0
    for a, b in pairs:
        c = s.count(a)
        if c:
            s = s.replace(a, b)
            n += c
    if n:
        p.write_text(s, encoding='utf-8')
    return n


def fix_text():
    total = 0
    for fn, pairs in PAIRS.items():
        total += replace_in(fn, pairs)
    # PDF 三册的源数据同样引用了例 4-1 题文，保持源码口径一致
    # （PDF 成品为独立静态交付物，本次不重建）
    total += replace_in('tools/pdata_s.py', [
        (TITLE_OLD, TITLE_NEW),
        ('"score": "4 张工作表名称完全一致', '"score": "3 张工作表名称完全一致'),
    ])
    return total


def sync_titles():
    """fix_link.sync_json() 只回写 reqs/steps/score，题名需单独同步。"""
    p = HERE / 'exercises.json'
    data = json.loads(p.read_text(encoding='utf-8'))
    n = 0
    for q in data:
        if (q['ci'], q['seq']) == (4, 1) and '4 张工作表' in q['title']:
            q['title'] = q['title'].replace('4 张工作表', '3 张工作表')
            n += 1
    if n:
        p.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding='utf-8')
    return n


def refresh_mat_blocks():
    """按新 manifest 与 zip 实际大小刷新网页素材块，不触碰完成比对链接。"""
    MF = json.loads((HERE / 'manifest.json').read_text(encoding='utf-8'))
    by = {(r['ci'], r['seq']): r for r in MF}
    total = 0
    for ci, fn in enumerate(fix_link.PAGES, 1):
        p = ROOT / fn
        s = p.read_text(encoding='utf-8')
        orig = s
        for seq in range(1, 17 if ci == 1 else 9):
            r = by.get((ci, seq))
            if not r:
                continue
            m = re.search(r'<div class="mat" id="mat-%d-%d">' % (ci, seq), s)
            if not m:
                continue
            dl = re.search(r'<a class="mat-dl"[^>]*>.*?</a>', s[m.end():], re.S)
            if not dl:
                continue
            end = m.end() + dl.end()
            block = s[m.start():end]
            full = patch_html.mat_block(r, seq)
            ul = re.search(r'<ul class="mat-files">.*?</ul>', full, re.S)
            kb = re.search(r'<span class="mat-size">([^<]*)</span>', full)
            if not ul or not kb:
                continue
            block2 = re.sub(r'<ul class="mat-files">.*?</ul>',
                            lambda _: ul.group(0), block, count=1, flags=re.S)
            block2 = re.sub(r'<span class="mat-size">[^<]*</span>',
                            lambda _: '<span class="mat-size">%s</span>' % kb.group(1),
                            block2, count=1)
            if block2 != block:
                s = s[:m.start()] + block2 + s[end:]
                total += 1
        if s != orig:
            p.write_text(s, encoding='utf-8')
    return total


def main():
    print('网页 / PDF 源文本修订：%d 处' % fix_text())
    print('exercises.json 回写字段：%d' % fix_link.sync_json())
    print('例 4-1 题名同步：%d 处' % sync_titles())
    B.DATA = json.loads((HERE / 'exercises.json').read_text(encoding='utf-8'))
    B.main()
    print('网页素材块刷新：%d 题' % refresh_mat_blocks())


if __name__ == '__main__':
    main()
