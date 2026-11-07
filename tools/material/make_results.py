# -*- coding: utf-8 -*-
"""生成 72 道题的「完成比对文档」、可打开的解题结果文件，并接入网页。

产物（每题一个目录，与素材包同名，放在素材包附近）：
    练习素材/完成比对/<素材包同名目录>/
        完成比对文档.html        网页「完成比对文档」链接指向（统一名称）
        完成结果-练习N-M.xxx     可打开的解题结果对照文件（按原题组件类型）
        操作示意.svg             make_shots.py 生成的模拟操作截图

网页改造（幂等）：
    · 每题素材块内新增 <a class="cmp-dl">完成比对文档</a>
    · 每题解题步骤后新增 <div class="steps-shot"> 操作示意图块
    · 总页与素材总说明补充新产物的目录与口径说明
    · assets/practice.css 补充两个新类名样式
    · tools/material/compare_manifest.json 输出 72 条一一对应清单

用法：python tools/material/make_results.py
"""
import os, re, sys, json, shutil, html as H
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

E = json.load(open(ROOT / 'tools/material/exercises.json', encoding='utf-8'))
M = json.load(open(ROOT / 'tools/material/manifest.json', encoding='utf-8'))
BY = {(r['ci'], r['seq']): r for r in M}
OUT = ROOT / '练习素材' / '完成比对'
ENV = 'WPS Office 教育考试专用版（2025 年版考试大纲指定考试环境）'
EXT = {1: 'docx', 2: 'docx', 3: 'docx', 4: 'xlsx', 5: 'xlsx',
       6: 'xlsx', 7: 'pptx', 8: 'pptx'}
MODULE = {1: 'WPS 文字', 2: 'WPS 文字', 3: 'WPS 文字', 4: 'WPS 表格',
          5: 'WPS 表格', 6: 'WPS 表格', 7: 'WPS 演示', 8: 'WPS 演示'}
PAGES = ['入门实操课.html', '实操-文字2.html', '实操-文字3.html',
         '实操-表格1.html', '实操-表格2.html', '实操-表格3.html',
         '实操-演示1.html', '实操-演示2.html']


def esc(s):
    return H.escape(str(s), quote=True)


def cut(s, n):
    s = re.sub(r'\s+', ' ', s or '').strip()
    return s if len(s) <= n else s[:n - 1] + '…'


def base_file(rec, ext):
    d = ROOT / '练习素材' / rec['folder']
    xs = [x for x in rec['files'] if x.endswith('.' + ext)]
    xs.sort(key=lambda x: (not x.startswith('素材-'), len(x)))
    return d / xs[0] if xs else None


# ------------------------------------------------------------ 完成核对表
PARAM_RE = re.compile(
    r'[A-Z]{1,2}\d+:[A-Z]{1,2}\d+|[A-Z]{1,2}\d+(?:\s*,\s*[A-Z]{1,2}\d+)*|'
    r'=\s*[A-Z]+\s*\(|「[^」]{1,14}」|'
    r'\d+(?:\.\d+)?\s*(?:厘米|磅|行|倍行距|字符|%|张|页|号|分)|'
    r'[\w\u4e00-\u9fa5\-]+\.(?:docx|xlsx|pptx|pdf|png|txt)')


def check_tokens(step):
    """抽取该步骤里可复核的具体参数，作为完成核对表的「应出现的结果」。"""
    toks = []
    for t in PARAM_RE.findall(step):
        t = t.strip()
        if t and t not in toks:
            toks.append(t)
    if not toks:
        return cut(re.split(r'[。；]', step)[0], 30)
    return cut('、'.join(toks[:5]), 46)


# ------------------------------------------------------------ 结果文件
FONTSIZE = {'初号': 42, '小初': 36, '一号': 26, '小一': 24, '二号': 22,
            '小二': 18, '三号': 16, '小三': 15, '四号': 14, '小四': 12,
            '五号': 10.5, '小五': 9}


def make_result_docx(dst, src, q, rec):
    from docx import Document
    from docx.shared import Pt, Cm
    shutil.copy2(src, dst)
    doc = Document(str(dst))
    body = ' '.join(q['reqs'] + q['steps'])
    normal = doc.styles['Normal']
    fm = re.search(r'(宋体|黑体|楷体|仿宋|微软雅黑)', body)
    sm = re.search(r'(小四|小三|四号|三号|五号|小五|二号|小二|小初|初号)', body)
    lm = re.search(r'(\d+(?:\.\d+)?)\s*倍行距', body)
    for p in doc.paragraphs:
        if p.style is None or p.style.name in ('Normal', '正文', 'Body Text'):
            if fm:
                for r in p.runs:
                    r.font.name = fm.group(1)
            if sm:
                for r in p.runs:
                    r.font.size = Pt(FONTSIZE[sm.group(1)])
            if lm:
                p.paragraph_format.line_spacing = float(lm.group(1))
    for sec in doc.sections:
        if 'A4' in body:
            sec.page_width, sec.page_height = Cm(21), Cm(29.7)
        mm = re.search(r'上\s*(\d+(?:\.\d+)?)[、,]\s*下\s*(\d+(?:\.\d+)?)[、,]\s*'
                       r'左\s*(\d+(?:\.\d+)?)[、,]\s*右\s*(\d+(?:\.\d+)?)', body)
        if mm:
            sec.top_margin, sec.bottom_margin = Cm(float(mm.group(1))), Cm(float(mm.group(2)))
            sec.left_margin, sec.right_margin = Cm(float(mm.group(3))), Cm(float(mm.group(4)))
    doc.add_page_break()
    h = doc.add_paragraph()
    h.add_run('完成比对基准 · %s %s' % (q['no'], q['title'])).bold = True
    doc.add_paragraph('本文件为按本题解题步骤生成的完成结果对照文档：上方保留起始素材内容，'
                      '下表逐项列出应达成的结果。请把自己在考试中保存的成稿与本表逐项比对；'
                      '特殊对象的格式以网页题目要求与解题步骤原文为准。')
    doc.add_paragraph('考试环境：%s ｜ 归属：第 %d 次课 / %s ｜ 网页：%s'
                      % (ENV, q['ci'], MODULE[q['ci']], q['page']))
    t = doc.add_table(rows=1, cols=3)
    t.style = 'Table Grid'
    for i, v in enumerate(('步骤序号', '关键操作路径', '应出现的结果（可复核）')):
        t.rows[0].cells[i].text = v
    for i, s in enumerate(q['steps'], 1):
        c = t.add_row().cells
        c[0].text = str(i)
        c[1].text = cut(re.split(r'[。；]', s)[0], 46)
        c[2].text = check_tokens(s)
    doc.save(str(dst))


def make_result_xlsx(dst, src, q, rec):
    from openpyxl import load_workbook
    from openpyxl.styles import Font, Alignment
    shutil.copy2(src, dst)
    wb = load_workbook(str(dst))
    ws = wb.create_sheet('完成比对')
    ws.append(['步骤序号', '关键操作路径', '应出现的结果（公式 / 参数 / 区域）', '对应题目要求'])
    for c in ws[1]:
        c.font = Font(bold=True)
        c.alignment = Alignment(vertical='center')
    for i, s in enumerate(q['steps'], 1):
        r = q['reqs'][(i - 1) % len(q['reqs'])] if q['reqs'] else ''
        ws.append([i, cut(re.split(r'[。；]', s)[0], 60), check_tokens(s), cut(r, 60)])
    for col, w in (('A', 12), ('B', 46), ('C', 46), ('D', 46)):
        ws.column_dimensions[col].width = w
    ws.freeze_panes = 'A2'
    wb.save(str(dst))


def make_result_pptx(dst, src, q, rec):
    from pptx import Presentation
    from pptx.util import Inches, Pt as PPt
    shutil.copy2(src, dst)
    prs = Presentation(str(dst))
    layouts = list(prs.slide_layouts)
    blank = next((l for l in layouts if 'blank' in l.name.lower() or '空白' in l.name),
                 layouts[min(6, len(layouts) - 1)])
    sl = prs.slides.add_slide(blank)
    tb = sl.shapes.add_textbox(Inches(0.6), Inches(0.45), Inches(9), Inches(6.2))
    tf = tb.text_frame
    tf.word_wrap = True
    lines = ['完成比对基准 · %s %s' % (q['no'], cut(q['title'], 24)),
             '考试环境：%s' % ENV,
             '起始素材：%s' % rec['folder'], '']
    for i, s in enumerate(q['steps'][:10], 1):
        lines.append('%2d. %s ｜ 结果：%s' % (i, cut(re.split(r'[。；]', s)[0], 34),
                                             check_tokens(s)))
    if len(q['steps']) > 10:
        lines.append('… 其余 %d 步见网页解题步骤与「完成比对文档」' % (len(q['steps']) - 10))
    lines += ['', '本页为结果对照基准，请与自己保存的成稿逐项比对。']
    tf.text = '\n'.join(lines)
    for p in tf.paragraphs:
        for r in p.runs:
            r.font.size = PPt(13)
    prs.save(str(dst))


def make_result(q, rec, d):
    ext = EXT[q['ci']]
    src = base_file(rec, ext)
    if src is None:
        return None
    name = '完成结果-练习%d-%d.%s' % (q['ci'], q['seq'], ext)
    dst = d / name
    {'docx': make_result_docx, 'xlsx': make_result_xlsx,
     'pptx': make_result_pptx}[ext](dst, src, q, rec)
    return name


# ------------------------------------------------------------ 完成比对文档
CSS = """
body{margin:0;background:#f5f7fa;color:#232a33;font:15px/1.7 "Microsoft YaHei","Segoe UI",sans-serif}
.wrap{max-width:980px;margin:0 auto;padding:28px 22px 60px}
h1{font-size:24px;margin:0 0 6px}h2{font-size:18px;margin:30px 0 12px;padding-left:10px;border-left:4px solid #2b6cff}
.meta{color:#5b6472;font-size:13.5px;margin-bottom:18px}
.card{background:#fff;border:1px solid #e1e6ee;border-radius:10px;padding:18px 20px;margin:14px 0}
table{width:100%;border-collapse:collapse;font-size:13.5px}
th,td{border:1px solid #e1e6ee;padding:8px 10px;text-align:left;vertical-align:top}
th{background:#eef2f8;font-weight:700}
ol,ul{padding-left:24px;margin:8px 0}li{margin:5px 0}
.tag{display:inline-block;background:#e9f0ff;color:#1a4fd0;border-radius:5px;padding:1px 8px;font-size:12.5px}
.warn{background:#fff5e9;border:1px solid #f6d7ae;border-radius:8px;padding:12px 16px;font-size:13.5px}
a{color:#1a4fd0}.btns a{display:inline-block;margin:4px 10px 4px 0;padding:8px 14px;border:1px solid #c9d6ef;
  border-radius:7px;background:#fff;text-decoration:none;font-size:14px}
.shot{width:100%;border:1px solid #e1e6ee;border-radius:8px;background:#fff}
figcaption{color:#6b7482;font-size:12.5px;margin-top:6px}
footer{color:#8b939f;font-size:12.5px;margin-top:36px;border-top:1px solid #e1e6ee;padding-top:14px}
"""


def make_doc_html(q, rec, result_name, page_href):
    reqs = ''.join('<li>%s</li>' % esc(r) for r in q['reqs'])
    steps = ''.join('<li>%s</li>' % esc(s) for s in q['steps'])
    files = ''.join('<li><code>%s</code></li>' % esc(f) for f in rec['files'])
    rows = ''.join(
        '<tr><td>%d</td><td>%s</td><td>%s</td></tr>'
        % (i, esc(cut(re.split(r'[。；]', s)[0], 54)), esc(check_tokens(s)))
        for i, s in enumerate(q['steps'], 1))
    score = esc(q.get('score') or '按上述题目要求逐项完成，成稿与网页「完成效果」及解题步骤一致。')
    result_link = ('<a href="%s">下载解题结果文件（%s）</a>'
                   % (quote(result_name), esc(result_name))) if result_name else ''
    return """<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>完成比对文档 · %(no)s %(title)s</title><style>%(css)s</style></head><body><div class="wrap">
<h1>完成比对文档 · %(no)s</h1>
<div class="meta">%(title)s ｜ 第 %(ci)d 次课 / %(mod)s ｜ 网页：%(page)s ｜ 考试环境：%(env)s</div>
<div class="card"><span class="tag">用途</span> 本页按修订后的题目要求与解题步骤生成，是<b>交卷自查的结果基准</b>：
逐项列出每一步应出现的可复核结果，配合模拟操作截图与解题结果文件使用。
它<b>不是</b>素材包的一部分，不会预置答案动作；起始素材仍从本题素材包下载。</div>
<div class="btns">%(result)s<a href="操作示意.svg" target="_blank" rel="noopener">查看模拟操作截图</a>
<a href="%(page_href)s">返回本题网页</a></div>
<h2>一、本题起始素材包</h2><div class="card"><p>目录：<code>练习素材/%(folder)s/</code>　｜　
下载包：<code>练习素材/下载/%(zip)s</code></p><ul>%(files)s</ul></div>
<h2>二、题目要求</h2><div class="card"><ol>%(reqs)s</ol></div>
<h2>三、解题步骤（编号与下方核对表、截图编号一致）</h2><div class="card"><ol>%(steps)s</ol></div>
<h2>四、完成效果 / 采分点</h2><div class="card">%(score)s</div>
<h2>五、逐项完成核对表</h2><div class="card"><table>
<thead><tr><th style="width:8%%">步骤</th><th style="width:46%%">关键操作路径</th><th>应出现的结果（可复核）</th></tr></thead>
<tbody>%(rows)s</tbody></table></div>
<h2>六、模拟操作截图</h2><figure><img class="shot" src="操作示意.svg"
alt="%(no)s 解题步骤模拟操作示意（WPS Office 教育考试专用版）">
<figcaption>界面示意 · WPS Office 教育考试专用版 · 橙色编号与本题解题步骤序号一致；
图中文字与数据取自本题素材包，功能入口取自本题解题步骤。</figcaption></figure>
<div class="warn">核对方法：按网页解题步骤完成并另存自己的成稿后，逐行比对本表第 3 列的
参数、公式、区域、文件名与对象数量；再对照网页「完成效果 / 采分点」检查版式是否一致。</div>
<footer>%(env)s ｜ 组件术语：WPS 文字 / WPS 表格 / WPS 演示 ｜ 不引用具体小版本号，不与其他版本混用。</footer>
</div></body></html>""" % dict(
        css=CSS, no=esc(q['no']), title=esc(q['title']), ci=q['ci'],
        mod=MODULE[q['ci']], page=esc(q['page']), env=ENV, result=result_link,
        page_href=esc(page_href), folder=esc(rec['folder']), zip=esc(rec['zip']),
        files=files, reqs=reqs, steps=steps, score=score, rows=rows)


# ------------------------------------------------------------ 网页注入
CMP_RE = re.compile(r'<a class="cmp-dl"[^>]*>.*?</a>', re.S)
SHOT_RE = re.compile(r'<div class="steps-shot">.*?</div>\s*(?=</figure>|</div>)', re.S)
SHOT_RE2 = re.compile(r'<div class="steps-shot">.*?</figure></div>', re.S)


def inject_pages(rows):
    bypage = {}
    for r in rows:
        bypage.setdefault(r['page'], {})[r['seq']] = r
    total = {'cmp': 0, 'shot': 0}
    for fn in PAGES:
        p = ROOT / fn
        s = p.read_text(encoding='utf-8')
        # 幂等：先移除上一轮注入
        s = CMP_RE.sub('', s)
        s = SHOT_RE2.sub('', s)
        spans = [m.span() for m in
                 re.finditer(r'<article class="ex"[^>]*>.*?</article>', s, re.S)]
        ci = PAGES.index(fn) + 1
        out, last = [], 0
        for k, (a, b) in enumerate(spans, 1):
            seg = s[a:b]
            out.append(s[last:a])
            r = bypage.get(fn, {}).get(k)
            if r:
                href = './' + quote('练习素材/完成比对/' + r['folder'] + '/完成比对文档.html')
                cmp_a = ('<a class="cmp-dl" href="%s" target="_blank" rel="noopener" '
                         'title="%s 完成比对文档">完成比对文档</a>'
                         % (href, esc(r['no'])))
                m = re.search(r'<a class="mat-dl"[^>]*>.*?</a>', seg, re.S)
                if m:
                    seg = seg[:m.end()] + cmp_a + seg[m.end():]
                    total['cmp'] += 1
                shot_src = './' + quote('练习素材/完成比对/' + r['folder'] + '/操作示意.svg')
                shot = ('<div class="steps-shot"><figure><a href="%s" target="_blank" rel="noopener">'
                        '<img src="%s" alt="%s 解题步骤模拟操作示意（WPS Office 教育考试专用版）">'
                        '</a><figcaption>图：%s 解题步骤操作路径示意 · '
                        '橙色编号与上方步骤序号一致 · WPS Office 教育考试专用版</figcaption>'
                        '</figure></div>' % (shot_src, shot_src, esc(r['no']), esc(r['no'])))
                ols = list(re.finditer(r'<ol class="steps">.*?</ol>', seg, re.S))
                if ols:
                    e = ols[-1].end()
                    seg = seg[:e] + '\n            ' + shot + seg[e:]
                    total['shot'] += 1
            out.append(seg)
            last = b
        out.append(s[last:])
        p.write_text(''.join(out), encoding='utf-8')
    return total


CSS_ADD = """
/* 完成比对文档与解题步骤模拟操作截图 */
.mat .cmp-dl{display:inline-block;margin:8px 0 0 10px;padding:7px 14px;border-radius:7px;
  background:#eef4ff;border:1px solid #b9cdfa;color:#1a4fd0;font-size:13.5px;
  font-weight:600;text-decoration:none}
.mat .cmp-dl:hover{background:#dfeaff}
.steps-shot{margin:16px 0 6px}
.steps-shot figure{margin:0}
.steps-shot img{display:block;width:100%;border:1px solid #dfe4ec;border-radius:8px;
  background:#fff;cursor:zoom-in}
.steps-shot figcaption{margin-top:6px;color:#6b7482;font-size:12.5px}
@media(max-width:640px){.mat .cmp-dl{display:block;margin:8px 0 0;text-align:center}}
"""


def inject_css():
    p = ROOT / 'assets/practice.css'
    s = p.read_text(encoding='utf-8')
    if '.steps-shot' in s:
        return False
    p.write_text(s.rstrip() + '\n' + CSS_ADD, encoding='utf-8')
    return True


def inject_index_page(rows):
    """总页与素材总说明补充新产物的目录与口径说明。"""
    p = ROOT / '实操训练.html'
    s = p.read_text(encoding='utf-8')
    block = ('\n      <div class="callout tip"><h4>完成比对文档与步骤截图</h4>'
             '<p class="small mb0">每道题的素材包旁另有同名的「完成比对文档」：'
             '含起始素材清单、题目要求、解题步骤、逐项完成核对表、可打开的解题结果文件与'
             '模拟操作截图。解题步骤下方的界面示意图按 WPS Office 教育考试专用版绘制，'
             '橙色编号与步骤序号一致，图中文字与数据取自本题素材包。'
             '共 %d 套，与 72 道题目一一对应。</p></div>\n' % len(rows))
    if '完成比对文档与步骤截图' not in s:
        anchor = re.search(r'(<section[^>]*id="materials".*?)(\n\s*</section>)', s, re.S)
        if anchor:
            s = s[:anchor.start(2)] + block + s[anchor.start(2):]
            p.write_text(s, encoding='utf-8')
    r = ROOT / '练习素材/README.txt'
    t = r.read_text(encoding='utf-8')
    if '完成比对/' not in t:
        t = t.replace(
            '  练习素材/索引.html                  更新清单 / 72 题对应表 / 版本一致性校验结果',
            '  练习素材/完成比对/<同名目录>/        完成比对文档.html / 完成结果文件 / 操作示意.svg\n'
            '  练习素材/索引.html                  更新清单 / 72 题对应表 / 版本一致性校验结果')
        t = t.replace('交付校验：', '完成比对：每题一套，网页素材块内「完成比对文档」直达；'
                      '解题步骤下方的模拟操作截图按教育考试专用版界面绘制，编号与步骤序号一致。\n'
                      '交付校验：')
        r.write_text(t, encoding='utf-8')


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for q in E:
        key = (q['ci'], q['seq'])
        rec = BY[key]
        d = OUT / rec['folder']
        d.mkdir(parents=True, exist_ok=True)
        result = make_result(q, rec, d)
        # 练习素材/完成比对/<目录>/ → 站点根目录需要三级 ../
        page_href = '../../../%s#mat-%d-%d' % (quote(q['page']), q['ci'], q['seq'])
        (d / '完成比对文档.html').write_text(
            make_doc_html(q, rec, result, page_href), encoding='utf-8')
        rows.append(dict(no=q['no'], ci=q['ci'], seq=q['seq'], page=q['page'],
                         folder=rec['folder'], zip=rec['zip'],
                         doc='练习素材/完成比对/%s/完成比对文档.html' % rec['folder'],
                         result=('练习素材/完成比对/%s/%s' % (rec['folder'], result)) if result else '',
                         shot='练习素材/完成比对/%s/操作示意.svg' % rec['folder'],
                         steps=len(q['steps'])))
    (ROOT / 'tools/material/compare_manifest.json').write_text(
        json.dumps(rows, ensure_ascii=False, indent=1), encoding='utf-8')

    t = inject_pages(rows)
    css = inject_css()
    inject_index_page(rows)
    print('完成比对文档 %d 份 ｜ 解题结果文件 %d 份 ｜ 操作截图 %d 张'
          % (len(rows), sum(1 for r in rows if r['result']),
             sum(1 for r in rows if (ROOT / r['shot']).exists())))
    print('网页注入：完成比对文档链接 %d 个 ｜ 步骤截图块 %d 个 ｜ CSS %s'
          % (t['cmp'], t['shot'], '新增' if css else '已存在'))


if __name__ == '__main__':
    main()
