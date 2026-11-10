# -*- coding: utf-8 -*-
"""把素材包接入网页：每题下载入口、课页索引、总页索引、版本口径统一。"""
import os, re, json, html as H
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[2]
MF = json.load(open(Path(__file__).parent / "manifest.json", encoding="utf-8"))
BY = {(r["ci"], r["seq"]): r for r in MF}
FILES = ['入门实操课.html', '实操-文字2.html', '实操-文字3.html',
         '实操-表格1.html', '实操-表格2.html', '实操-表格3.html',
         '实操-演示1.html', '实操-演示2.html']
MOD = {1: 'WPS 文字', 2: 'WPS 文字', 3: 'WPS 文字', 4: 'WPS 表格',
       5: 'WPS 表格', 6: 'WPS 表格', 7: 'WPS 演示', 8: 'WPS 演示'}
ENV = 'WPS Office 教育考试专用版'

# ---------------------------------------------------------------- 版本口径统一
REPL = [
    ('WPS Office 教育考试专用版（Windows 10/11）；个人版操作路径基本一致',
     'WPS Office 教育考试专用版；功能入口按该版本现行界面命名'),
    ('WPS Office 教育考试专用版（Windows 10）', 'WPS Office 教育考试专用版'),
    ('，个人版菜单名称可能略有差异，按功能名称定位即可。',
     '；功能入口与按钮名称一律以该版本现行功能区为准。'),
    ('依据 WPS Office 文字 12.x 界面绘制的教学示意图',
     '依据 WPS Office 教育考试专用版（WPS 文字）界面绘制的教学示意图'),
    ('50 张 WPS 文字 12.x 界面示意图', '50 张 WPS Office 教育考试专用版界面示意图'),
    ('「文件类型」选 Word 文件(*.docx)', '「文件类型」选 WPS 文字 文件(*.docx)'),
    ('文件类型选「Excel 工作簿(*.xlsx)」', '文件类型选「WPS 表格 文件(*.xlsx)」'),
    ('WPS 演示（或 PowerPoint）', 'WPS 演示'),
    ('从大纲文件（Word/txt）导入', '从大纲文件（WPS 文字文档 / txt）导入'),
    ('表格公式与 Excel 的区别', 'WPS 文字表格公式与 WPS 表格公式的区别'),
    ('把 Excel 名单套进模板', '把 WPS 表格名单套进模板'),
    ('中文版 Windows 10；WPS Office 教育考试专用版',
     '中文版 Windows 7 或以上（推荐 Windows 10）；WPS Office 教育考试专用版'),
    ('每道题都<b>从新建文件开始</b>，给出可直接跟做的步骤',
     '每道题都<b>配套可下载的练习素材包</b>，并保留从零新建的完整路径，给出可直接跟做的步骤'),
    ('4 课时 16 道例题，全部从新建文件开始，逐步覆盖',
     '4 课时 16 道例题，每题配套可下载素材包并保留从零新建路径，逐步覆盖'),
    ('关于界面图与素材</h3>\n        <p class="small mb0">第 1 次课配有 50 张 WPS Office 教育考试专用版界面示意图，标注「步骤 N / 完成效果」，用于直观跟做；第 2~8 次课以<b>文字步骤 + 参数值</b>为主，不再逐题配图——因为表格与演示的评分点几乎全在「参数是否精确」而非「按钮在哪」。<br><br>所有例题的素材均为自拟教学数据，不涉及真实个人信息；操作路径以 <b>WPS Office 教育考试专用版</b>为准；功能入口与按钮名称一律以该版本现行功能区为准。',
     '关于界面图与练习素材</h3>\n        <p class="small mb0">第 1 次课配有 50 张 WPS Office 教育考试专用版界面示意图，标注「步骤 N / 完成效果」，用于直观跟做；第 2~8 次课以<b>文字步骤 + 参数值</b>为主，不再逐题配图——因为表格与演示的评分点几乎全在「参数是否精确」而非「按钮在哪」。<br><br>八次课 72 道题<b>每题都有一个独立素材包</b>，包内含起始文件、必要图片/数据源与「素材说明.txt」；答案动作一律不预置，完成效果以该题采分点为准。所有素材均为自拟教学数据，不涉及真实个人信息；操作路径、功能入口与按钮名称一律以 <b>WPS Office 教育考试专用版</b>现行界面为准。'),
]
HITS = {}


def unify(s, tag=''):
    for a, b in REPL:
        n = s.count(a)
        if n:
            s = s.replace(a, b)
            HITS[a[:28]] = HITS.get(a[:28], 0) + n
    return s


# ---------------------------------------------------------------- 素材块
def esc(s): return H.escape(s, quote=False)


def mat_block(r, idx):
    folder, zipn = r['folder'], r['zip']
    href = './' + quote('练习素材/下载/' + zipn)
    size = (ROOT / '练习素材' / '下载' / zipn).stat().st_size
    kb = '%.0f KB' % (size / 1024) if size < 1024 * 1024 else '%.1f MB' % (size / 1048576)
    lis = []
    for fn in r['files']:
        desc = '文件清单 / 题目要求 / 完成效果 / 环境口径' if fn == '素材说明.txt' else ''
        if not desc:
            if fn.endswith('.docx'): desc = '起始文档（WPS 文字）'
            elif fn.endswith('.xlsx'): desc = '数据表 / 数据源（WPS 表格）'
            elif fn.endswith('.pptx'): desc = '起始演示文稿（WPS 演示）'
            elif fn.endswith('.png'): desc = '图片源文件'
            elif fn.endswith('.wav'): desc = '音频源文件'
            elif fn.endswith('.mp4'): desc = '视频源文件'
            elif fn.endswith('.txt'): desc = '大纲 / 说明文本'
            else: desc = '配套素材'
        lis.append('<li><code>%s</code><span>%s</span></li>' % (esc(fn), esc(desc)))
    return (
        '<div class="mat" id="mat-%d-%d">'
        '<div class="mat-h"><span class="mat-tag">练习素材包</span>'
        '<b>%s</b><span class="mat-size">%s</span></div>'
        '<div class="mat-b"><ul class="mat-files">%s</ul>'
        '<p class="mat-note">解题步骤中凡需打开素材，均使用本包内的起始文件；'
        '若题目要求从零新建，请以包内文字/数据为录入内容，参数与题目要求保持一致。'
        '包内「素材说明.txt」列有完整题目要求与完成效果（采分点）。'
        '格式、公式、图表、动画、修订、目录、题注等答案动作均<b>不预置</b>。</p></div>'
        '<a class="mat-dl" href="%s" download="%s">&#11015; 下载本题素材包</a>'
        '</div>'
    ) % (r['ci'], r['seq'], esc(zipn), kb, ''.join(lis), href, esc(zipn))


def mat_index(ci):
    rs = [r for r in MF if r['ci'] == ci]
    head = (('<div class="matidx" id="matindex">'
             '<div class="matidx-h"><h3>本课练习素材包（%d 个）</h3>'
             '<span class="matidx-sub">%s ｜ 每题一个独立压缩包，命名「练习%d-M-题目短名.zip」</span></div>'
             '<div class="matidx-grid">') % (len(rs), MOD[ci], ci))
    items = []
    for r in rs:
        href = './' + quote('练习素材/下载/' + r['zip'])
        items.append('<a class="matidx-i" href="%s" download="%s">'
                     '<span class="mi-no">%s</span><span class="mi-t">%s</span>'
                     '<span class="mi-dl">&#11015; 下载</span></a>'
                     % (href, esc(r['zip']), esc(r['no']), esc(r['title'][:26])))
    tail = ('</div><p class="matidx-f">环境与术语：%s；组件统一称 WPS 文字 / WPS 表格 / WPS 演示，'
            '功能入口按该版本现行功能区命名。全套目录见 <a href="./实操训练.html#materials">实操训练 · 练习素材索引</a>。</p>'
            '</div>') % ENV
    return head + ''.join(items) + tail


def patch_page(f, ci):
    p = ROOT / f
    s = p.read_text(encoding='utf-8')
    arts = list(re.finditer(r'<article class="ex"[^>]*>.*?</article>', s, re.S))
    assert len(arts) == len([r for r in MF if r['ci'] == ci]), (f, len(arts))
    out, last = [], 0
    for k, m in enumerate(arts, 1):
        r = BY[(ci, k)]
        a = m.group(0)
        assert 'class="mat"' not in a, '重复插入 ' + f
        a2, n = re.subn(r'(<div class="ex-b"[^>]*>)', r'\1' + mat_block(r, k).replace('\\', '\\\\'), a, count=1)
        assert n == 1, 'ex-b 未找到 ' + f + str(k)
        # 题目要求 / 解题步骤：把「打开素材」明确指向素材包
        a2 = a2.replace('打开素材', '打开本题素材包中的起始文件')
        out.append(s[last:m.start()]); out.append(a2); last = m.end()
    out.append(s[last:])
    s = ''.join(out)
    # 课页索引：插在第 1 小节之前
    anchor = '<nav class="lessonnav"' if '<nav class="lessonnav"' in s else '<section id="l1">' if ci == 1 else '<section id="s1">'
    if '<nav class="lessonnav"' in s:
        # 插到 lessonnav 这一行之后
        mm = re.search(r'(<nav class="lessonnav"[^>]*>.*?</nav>)', s, re.S)
        s = s[:mm.end()] + '\n\n  ' + mat_index(ci) + '\n' + s[mm.end():]
    else:
        pos = s.find(anchor)
        assert pos > 0, anchor
        s = s[:pos] + mat_index(ci) + '\n\n  ' + s[pos:]
    # 本页 meta 文案
    if '每题配套可下载' not in s[:1600]:
        s = re.sub(r'(<meta name="description" content=")([^"]*)(")',
                   lambda m: m.group(1) + m.group(2).rstrip('。') + '；八次课每题配套可下载的练习素材包。' + m.group(3),
                   s, count=1)
    p.write_text(unify(s, f), encoding='utf-8')
    return len(arts)


# ---------------------------------------------------------------- 总页
def total_index():
    rows = []
    for ci in range(1, 9):
        rs = [r for r in MF if r['ci'] == ci]
        page = FILES[ci - 1]
        rows.append('<tr><td class="c"><b>第 %d 次课</b></td><td>%s</td><td class="c">%d</td>'
                    '<td class="small">练习%d-1-… ～ 练习%d-%d-…</td>'
                    '<td><a href="./%s#matindex">本课素材索引 &#8594;</a></td></tr>'
                    % (ci, MOD[ci], len(rs), ci, ci, len(rs), page))
    detail = []
    for r in MF:
        href = './' + quote('练习素材/下载/' + r['zip'])
        detail.append('<tr><td class="c">%s</td><td>%s</td><td><code>%s</code></td>'
                      '<td><a href="%s" download="%s">&#11015; 下载</a></td></tr>'
                      % (esc(r['no']), esc(r['title'][:34]), esc(r['zip']), href, esc(r['zip'])))
    return ('''
  <section class="section-sm" id="materials">
    <h2>五、练习素材包索引（8 次课 · 72 题 · 72 个包）</h2>
    <p class="muted">每道题都有一个独立素材包，位置就在该题卡片顶部的「练习素材包」区块内，点击即可下载。
      包内含起始文件、必要附件与 <code>素材说明.txt</code>；答案动作一律不预置，完成效果以该题采分点为准。</p>
    <div class="table-wrap mt2"><table class="tbl">
      <thead><tr><th class="c" style="width:80pt">次课</th><th style="width:90pt">模块</th>
      <th class="c" style="width:50pt">包数</th><th>命名范围</th><th style="width:150pt">索引入口</th></tr></thead>
      <tbody>%s</tbody></table></div>
    <div class="matrules">
      <div class="card"><h3>命名与目录</h3><p class="small mb0"><code>练习素材/练习N-M-题目短名/</code> 为解压目录，
      <code>练习素材/下载/练习N-M-题目短名.zip</code> 为下载包；N 是次课、M 是课内题序。
      主文件统一为 <code>素材-练习N-M.docx / .xlsx / .pptx</code>，多文档题按用途命名。</p></div>
      <div class="card"><h3>版本与术语</h3><p class="small mb0">全套素材与全部网页统一以
      <b>WPS Office 教育考试专用版</b>（2025 年版考试大纲指定考试环境）为准；组件称
      WPS 文字 / WPS 表格 / WPS 演示，功能入口按该版本现行功能区命名，
      不引用具体小版本号，不与其他版本混用。</p></div>
    </div>
    <details class="matall"><summary>展开 72 道题与素材包的一一对应清单</summary>
      <div class="table-wrap"><table class="tbl"><thead><tr><th class="c" style="width:64pt">题号</th>
      <th>题目</th><th style="width:230pt">素材包</th><th class="c" style="width:60pt">下载</th></tr></thead>
      <tbody>%s</tbody></table></div></details>
  </section>
''' % (''.join(rows), ''.join(detail)))


def patch_total():
    p = ROOT / '实操训练.html'
    s = p.read_text(encoding='utf-8')
    old = '  <section class="section-sm">\n    <h2>五、配套资源</h2>'
    assert old in s, '总页插入锚点未找到'
    s = s.replace(old, total_index().rstrip() + '\n\n' + old.replace('五、', '六、'), 1)
    s = s.replace('<a class="btn ghost" href="#map">跳到学习地图</a>',
                  '<a class="btn ghost" href="#map">跳到学习地图</a>\n    <a class="btn ghost" href="#materials">下载练习素材</a>', 1)
    s = s.replace('<div><h4>实操训练导航</h4>',
                  '<div><h4>实操训练导航</h4><p class="small"><a href="#materials">练习素材包索引（72 个）</a> · <a href="./练习素材/README.txt">素材总说明</a></p>', 1)
    p.write_text(unify(s, '实操训练.html'), encoding='utf-8')


def main():
    total = 0
    for ci, f in enumerate(FILES, 1):
        total += patch_page(f, ci)
    patch_total()
    # 其余页面只做版本口径统一
    others = ['index.html', '考试介绍.html', '教学大纲.html', '教学日历.html', '教案.html',
              '考纲对照表.html', '使用说明.html', '关于本站.html', '资料汇编.html', '电子书.html',
              '群管理.html', '用户中心.html', '培训课件.html', '考试模拟系统/index.html']
    for f in others:
        p = ROOT / f
        if p.exists():
            p.write_text(unify(p.read_text(encoding='utf-8'), f), encoding='utf-8')
    print('已接入下载入口的题目数：', total)
    print('版本口径替换命中：')
    for k, v in HITS.items(): print('  %2d × %s' % (v, k))


if __name__ == '__main__':
    main()
