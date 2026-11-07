# -*- coding: utf-8 -*-
"""本轮核查发现的「超纲 / 缺漏 / 版本不一致 / 表述不准确」最小化修订（幂等）。

只改确认为真的命中，不改考纲允许的内容：
  · 理论题中的「在线办公 / 文档上云 / 共享协作」属 2025 大纲「WPS 综合应用基础」，
    是单项选择题考试范围，不按操作越界处理；
  · 「输出为PDF」作为教育考试专用版真实按钮名、以及题目原文中的该字样，予以保留；
  · 「页面布局」作为考纲知识点名（非界面入口）予以保留。

用法：python tools/site_fix.py
"""
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# 文件 -> [(旧串, 新串, 期望最少命中数)]
FIX = {
    'assets/curriculum.js': [
        ('编辑完按 Ctrl+S 保存；要改格式或另存为 PDF 按 F12（另存为）；给文档加密：另存为→工具→常规选项。',
         '编辑完按 Ctrl+S 保存；要改文件名或位置按 F12（另存为）；输出 PDF 用「文件 → 输出为 PDF」；'
         '给文档加密用「文件 → 文档加密 → 密码加密」。', 1),
        ('可另存为 PDF、导出为图片', '可输出为 PDF、导出为图片', 1),
        ('另存为 PDF / 图片（PNG/JPG）/ 视频', '输出为 PDF / 图片（PNG/JPG）/ 视频', 1),
        ('另存为 PDF 文件', '输出为 PDF 文件', 1),
        ('另存为 PDF 会丢失动画与 multimedia', '输出为 PDF 会丢失动画与多媒体', 0),  # 兜底，见下方通用替换
        ('另存为 PDF 会丢失动画与多媒体', '输出为 PDF 会丢失动画与多媒体', 1),
        ('「页面布局」选项卡', '「页面」选项卡', 2),
        ('另存为 PDF', '输出为 PDF', 0),  # 通用兜底：处理剩余孤立出现
    ],
    '考试模拟系统/index.html': [
        ('将文档另存为 PDF', '将文档输出为 PDF', 1),
        ('适合保留不同版本', '适合保留历史副本', 1),
    ],
    '入门实操课.html': [
        ('页面布局 → 水印', '页面 → 水印', 1),
        ('页面布局 → 分隔符', '页面 → 分隔符', 1),
        ('二者配合才能一键生成。', '二者配合才能生成自动目录。', 2),
    ],
    'tools/material/verify.py': [
        ("'旧版 WPS 年份'", "'旧版年份'", 1),
    ],
}


def run_fix():
    total = 0
    for f, pairs in FIX.items():
        p = ROOT / f
        s = p.read_text(encoding='utf-8')
        orig = s
        counts = []
        for a, b, minimum in pairs:
            if a == b:
                continue
            n = s.count(a)
            if n:
                s = s.replace(a, b)
                total += n
            counts.append((a[:26], n, minimum, n >= minimum))
        if s != orig:
            p.write_text(s, encoding='utf-8')
        print('  %-32s %s' % (f, ', '.join('%s:%d' % (c[0], c[1]) for c in counts if c[1])))
    return total


def sync_manifest_titles():
    """manifest.json 的题名来自早期生成结果，与合规修订后的 exercises.json 有 2 处不同步。"""
    ep = ROOT / 'tools/material/exercises.json'
    mp = ROOT / 'tools/material/manifest.json'
    E = json.load(open(ep, encoding='utf-8'))
    M = json.load(open(mp, encoding='utf-8'))
    by = {(q['ci'], q['seq']): q['title'] for q in E}
    changed = []
    for r in M:
        t = by[(r['ci'], r['seq'])]
        if r['title'] != t:
            changed.append((r['no'], r['title'], t))
            r['title'] = t
    if changed:
        mp.write_text(json.dumps(M, ensure_ascii=False, indent=1), encoding='utf-8')
    for no, old, new in changed:
        print('  %-9s %s → %s' % (no, old, new))
    return len(changed)


def main():
    print('=== 表述 / 版本口径修订 ===')
    n = run_fix()
    print('  替换合计 %d 处' % n)
    print('=== 题名同步（manifest → exercises） ===')
    m = sync_manifest_titles()
    print('  同步 %d 条' % m)


if __name__ == '__main__':
    main()
