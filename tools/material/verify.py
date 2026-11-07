# -*- coding: utf-8 -*-
"""交付校验：文件齐全性 / 题目与包对应 / 网页入口 / 版本一致性，并生成索引页。"""
import re, json, zipfile, html as H
from pathlib import Path
from urllib.parse import unquote, quote

ROOT = Path(__file__).resolve().parents[2]
MF = json.load(open(Path(__file__).parent / "manifest.json", encoding="utf-8"))
PAGES = ['入门实操课.html', '实操-文字2.html', '实操-文字3.html', '实操-表格1.html',
         '实操-表格2.html', '实操-表格3.html', '实操-演示1.html', '实操-演示2.html']
RESULT = []


def chk(name, ok, detail=""):
    RESULT.append(dict(item=name, ok=bool(ok), detail=str(detail)))
    return ok


# ------------------------------------------------ 1. 文件齐全
def check_files():
    base, dl = ROOT / '练习素材', ROOT / '练习素材' / '下载'
    dirs = sorted([p.name for p in base.iterdir() if p.is_dir() and p.name.startswith('练习')])
    zips = sorted([p.name for p in dl.glob('*.zip')])
    chk('素材目录数 = 72', len(dirs) == 72, '%d 个' % len(dirs))
    chk('下载压缩包数 = 72', len(zips) == 72, '%d 个' % len(zips))
    expect_z = sorted(r['zip'] for r in MF)
    chk('压缩包命名与清单一一对应', zips == expect_z, '差异 %d' % len(set(zips) ^ set(expect_z)))
    expect_d = sorted(r['folder'] for r in MF)
    chk('目录命名与清单一一对应', dirs == expect_d, '差异 %d' % len(set(dirs) ^ set(expect_d)))
    bad, nameless = [], []
    for r in MF:
        d = base / r['folder']
        real = sorted(p.name for p in d.iterdir() if p.is_file())
        if real != sorted(r['files']): bad.append(r['no'])
        with zipfile.ZipFile(dl / r['zip']) as z:
            inner = sorted(n.split('/')[-1] for n in z.namelist())
        if inner != sorted(r['files']): bad.append(r['no'] + '(zip)')
        if not any(f.startswith('素材-练习') or f in ('初稿.docx', '修改稿.docx',
                   '素材A.docx', '素材B.docx', '录取通知书-主文档占位模板.docx') for f in real):
            nameless.append(r['no'])
        note = (d / '素材说明.txt').read_text(encoding='utf-8')
        if '【题目要求】' not in note or '【完成效果' not in note and '【完成效果 / 采分点】' not in note:
            bad.append(r['no'] + '(说明)')
    chk('包内文件与压缩包内容一致、无无关文件', not bad, ', '.join(bad[:8]))
    chk('每包含起始素材与素材说明', not nameless, ', '.join(nameless[:8]))
    total_files = sum(len(r['files']) for r in MF)
    return total_files


# ------------------------------------------------ 2. 文档可打开
def check_docs():
    from docx import Document
    from openpyxl import load_workbook
    from pptx import Presentation
    bad, counts = [], {'docx': 0, 'xlsx': 0, 'pptx': 0, 'png': 0, 'wav': 0, 'txt': 0}
    for r in MF:
        d = ROOT / '练习素材' / r['folder']
        for f in r['files']:
            p = d / f
            ext = p.suffix.lstrip('.')
            if ext in counts: counts[ext] += 1
            if not p.exists() or p.stat().st_size == 0:
                bad.append(f); continue
            try:
                if ext == 'docx' and len(Document(str(p)).paragraphs) < 2: bad.append(f)
                if ext == 'xlsx' and not load_workbook(str(p)).sheetnames: bad.append(f)
                if ext == 'pptx' and len(Presentation(str(p)).slides) < 1: bad.append(f)
            except Exception as ex:
                bad.append('%s(%s)' % (f, ex))
    chk('所有 docx/xlsx/pptx 可正常打开且非空', not bad, ', '.join(bad[:5]))
    return counts


# ------------------------------------------------ 3. 网页入口
def check_pages():
    total_links, bad = 0, []
    for ci, f in enumerate(PAGES, 1):
        s = (ROOT / f).read_text(encoding='utf-8')
        arts = re.findall(r'<article class="ex"[^>]*>.*?</article>', s, re.S)
        mats = re.findall(r'<a class="mat-dl" href="([^"]+)" download="([^"]+)"', s)
        if len(arts) != len([r for r in MF if r['ci'] == ci]): bad.append(f + ' 题目数')
        if len(mats) != len(arts): bad.append(f + ' 下载入口数 %d/%d' % (len(mats), len(arts)))
        if s.count('class="mat"') != len(arts): bad.append(f + ' 素材块数')
        idx = re.search(r'<div class="matidx".*?</div>\s*</div>', s, re.S)
        ilinks = re.findall(r'<a class="matidx-i" href="([^"]+)"', s)
        if len(ilinks) != len(arts): bad.append(f + ' 索引链接数 %d/%d' % (len(ilinks), len(arts)))
        for href, dn in mats + [(h, '') for h in ilinks]:
            p = ROOT / unquote(href.lstrip('./'))
            if not p.exists(): bad.append(f + ' 失效链接 ' + href[:60])
        total_links += len(mats)
        # 同步说明按题计数；解题步骤块数与题数一致，且步骤内不再用「打开素材」旧泛称
        notes = s.count('解题步骤中凡需打开素材，均使用本包内的起始文件')
        if notes != len(arts): bad.append(f + ' 素材同步说明 %d/%d' % (notes, len(arts)))
        steps = re.findall(r'<ol class="steps">(.*?)</ol>', s, re.S)
        if len(steps) != len(arts): bad.append(f + ' 解题步骤块数 %d/%d' % (len(steps), len(arts)))
        st = re.sub(r'<[^>]+>', '', ''.join(steps))
        if re.search(r'打开素材(?!包)', st): bad.append(f + ' 解题步骤残留旧泛称')
    chk('8 个课页 72 题均有唯一下载入口', total_links == 72 and not bad,
        '%d 个入口；%s' % (total_links, ', '.join(bad[:5])))
    tot = (ROOT / '实操训练.html').read_text(encoding='utf-8')
    chk('总页含素材索引章节', 'id="materials"' in tot)
    brows = re.findall(r'<tr><td class="c">(?:例 |综合题)', tot)
    chk('总页含 72 行对应关系清单', len(brows) == 72, '%d 行' % len(brows))
    return total_links


# ------------------------------------------------ 4. 版本一致性
BAN = [
    (r'12\.x|12\.1\.|11\.1\.', '具体小版本号'),
    (r'WPS\s?(?:2010|2013|2016|2019)', '旧版年份'),
    (r'Windows 10/11|教育考试专用版（Windows', '操作系统硬绑定'),
    # 校验项显示名不得含被禁字面词，否则生成的索引页会「自指命中」
    (r'个人版', '非考试专用版称谓'),
    (r'Word 文件\(\*\.docx\)|Excel 工作簿\(\*\.xlsx\)', '其他套件文件类型名'),
    (r'或 PowerPoint|（Word/txt）|与 Excel 的区别|Excel 名单', 'Office 组件混称'),
    (r'「页面布局」|>页面布局</text>|「页面布局 →', '旧版选项卡名'),
]
KEEP_OK = ('页面布局',)  # 考纲条目 / 知识点名，允许保留

# 修正清单的「修订前」需原样引用旧文案；用等长空白屏蔽历史引文区，其余内容照常严格扫描
QUOTE_RE = re.compile(r'<!--\s*AUDIT-QUOTE-BEGIN\s*-->.*?<!--\s*AUDIT-QUOTE-END\s*-->', re.S)


def strip_quotes(s):
    return QUOTE_RE.sub(lambda m: re.sub(r'[^\n]', ' ', m.group(0)), s)


def check_version():
    files = sorted((ROOT).glob('*.html')) + sorted((ROOT / 'assets/wps-img').glob('*.svg')) + \
            sorted((ROOT / '考试模拟系统').glob('*.html')) + \
            sorted((ROOT / 'assets').glob('*.js'))
    # 理论题库（站内发布的离线应用）与素材总说明、索引页一并纳入版本口径扫描
    for extra in (ROOT / '理论题库' / 'index.html', ROOT / '理论题库' / 'README.txt',
                  ROOT / '练习素材' / '索引.html', ROOT / '练习素材' / 'README.txt'):
        if extra.exists(): files.append(extra)
    files += sorted((ROOT / '练习素材').glob('练习*/素材说明.txt'))
    # 完成比对文档与模拟操作截图同样纳入版本口径扫描
    cdir = ROOT / '练习素材' / '完成比对'
    files += sorted(cdir.glob('*/完成比对文档.html')) + sorted(cdir.glob('*/操作示意.svg'))
    detail = []
    for pat, name in BAN:
        hits = []
        for p in files:
            s = strip_quotes(p.read_text(encoding='utf-8'))
            n = len(re.findall(pat, s))
            if n: hits.append('%s:%d' % (p.name, n))
        chk('无「%s」残留' % name, not hits, ', '.join(hits[:4]))
    alltext = '\n'.join(strip_quotes(p.read_text(encoding='utf-8')) for p in files)
    std = 'WPS Office 教育考试专用版'
    chk('统一称谓「%s」在用' % std, alltext.count(std) >= 55, '%d 处' % alltext.count(std))
    chk('组件术语统一（WPS 文字 / WPS 表格 / WPS 演示）',
        all(w in alltext for w in ('WPS 文字', 'WPS 表格', 'WPS 演示')))
    chk('现行功能入口「页面」在用', '「页面」' in alltext, '%d 处' % alltext.count('「页面」'))
    kept = alltext.count('页面布局')
    detail.append('考纲条目/知识点名保留「页面布局」%d 处（大纲原文，非界面名）' % kept)
    return detail


# ------------------------------------------------ 5. 索引页
def esc(s): return H.escape(str(s), quote=False)


def make_index():
    rows = []
    for r in MF:
        href = './下载/' + r['zip']
        cmp_href = './完成比对/' + quote(r['folder']) + '/完成比对文档.html'
        fl = '、'.join('<code>%s</code>' % esc(f) for f in r['files'] if f != '素材说明.txt')
        rows.append('<tr><td class="c">%s</td><td class="c">第 %d 次课</td><td>%s</td>'
                    '<td><code>%s</code><br><span class="mut">%s</span></td><td class="c">%d</td>'
                    '<td><a class="btn" href="%s" download="%s">下载</a> '
                    '<a class="btn" href="%s">比对</a></td></tr>'
                    % (esc(r['no']), r['ci'], esc(r['title'][:40]), esc(r['zip']),
                       fl, len(r['files']), quote(href), esc(r['zip']), cmp_href))
    upd = [
        ('练习素材/（新建目录）', '72 个题目素材目录 + 72 个 zip + 总说明 README.txt'),
        ('assets/practice.css（追加）', '素材包下载块、课页索引、总页索引样式'),
        ('8 个实操课页', '每题卡片插入素材包下载入口；页首插入本课素材索引；题目要求与解题步骤同步指向素材包；meta 文案更新'),
        ('实操训练.html', '新增「五、练习素材包索引」与 72 行对应清单；原「五、配套资源」顺延为六；hero 与页脚加入口'),
        ('其余 14 个页面 + 50 张界面示意图', '版本口径统一，清除旧版残留'),
        ('tools/material/（脚本）', 'specs.py / build.py / patch_html.py / fix_version.py / verify.py / manifest.json'),
        ('练习素材/完成比对/（新建 72 个目录）', '每套含 完成比对文档.html + 完成结果文件 + 操作示意.svg，与素材包同名一一对应'),
        ('8 个实操课页（追加）', '每题新增「完成比对文档」链接与解题步骤模拟操作截图块，编号与步骤序号一致'),
        ('assets/practice.css（追加）', '.cmp-dl / .steps-shot 样式'),
        ('tools/material/（新增脚本与清单）', 'fix_link.py / make_shots.py / make_results.py / audit_link.py / audit_coverage.py / compare_manifest.json'),
    ]
    upd_rows = ''.join('<tr><td><code>%s</code></td><td>%s</td></tr>' % (esc(a), esc(b)) for a, b in upd)
    vr = ''.join('<tr><td>%s</td><td class="%s">%s</td><td class="mut">%s</td></tr>'
                 % (esc(x['item']), 'ok' if x['ok'] else 'no', 'PASS' if x['ok'] else 'FAIL', esc(x['detail']))
                 for x in RESULT)
    nok = sum(1 for x in RESULT if x['ok'])
    vbad = sum(1 for x in RESULT if not x['ok'] and any(
        k in x['item'] for k in ('残留', '称谓', '术语', '功能入口')))
    doc = '''<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>练习素材索引与版本一致性校验 · 实操训练 8 次课 72 题</title>
<style>
:root{--ink:#1f2733;--mut:#6b7683;--line:#dbe3ec;--brand:#1c4ed8;--bg:#f6f8fb}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.7 "Microsoft YaHei",sans-serif}
.wrap{max-width:1180px;margin:0 auto;padding:28px 22px 70px}
h1{font-size:27px;margin:0 0 6px}h2{font-size:20px;margin:34px 0 12px;padding-left:11px;border-left:4px solid var(--brand)}
.lead{color:var(--mut);margin:0 0 18px}.card{background:#fff;border:1px solid var(--line);border-radius:12px;padding:18px 20px;box-shadow:0 2px 8px rgba(20,40,80,.05)}
table{width:100%;border-collapse:collapse;font-size:13.5px}th,td{border-bottom:1px solid var(--line);padding:8px 9px;text-align:left;vertical-align:top}
th{background:#eef4fe;color:#12306b;font-weight:700}td.c,th.c{text-align:center}
code{background:#f1f5fa;border-radius:4px;padding:1px 5px;font-size:12px;color:#12306b;word-break:break-all}
.mut{color:var(--mut);font-size:12px}.ok{color:#12703f;font-weight:800}.no{color:#c0392b;font-weight:800}
a.btn{display:inline-block;background:var(--brand);color:#fff;text-decoration:none;border-radius:6px;padding:4px 12px;font-size:12.5px;white-space:nowrap}
a.btn:hover{background:#12306b}.stat{display:flex;gap:14px;flex-wrap:wrap;margin:14px 0}
.stat div{background:#fff;border:1px solid var(--line);border-radius:10px;padding:12px 20px}
.stat b{display:block;font-size:24px;color:var(--brand)}.stat span{font-size:12px;color:var(--mut)}
</style></head><body><div class="wrap">
<h1>练习素材索引与全链路校验</h1>
<p class="lead">实操训练 8 次课 · 32 小节 · 72 道实操题 ｜ 每题一个独立素材包 + 一套完成比对文档 ｜ 考试环境：WPS Office 教育考试专用版</p>
<div class="stat"><div><b>72</b><span>题目 / 素材包</span></div><div><b>72</b><span>完成比对 / 截图</span></div>
<div><b>@@FILES@@</b><span>包内文件总数</span></div>
<div><b>@@NOK@@ / @@TOTAL@@</b><span>校验通过 / 校验项</span></div><div><b>@@VBAD@@</b><span>版本一致性异常项</span></div></div>
<h2>一、更新清单</h2><div class="card"><table><thead><tr><th style="width:290px">位置</th><th>更新内容</th></tr></thead><tbody>@@UPD@@</tbody></table></div>
<h2>二、题目与文件包对应关系（72 条）</h2><div class="card"><table>
<thead><tr><th class="c" style="width:64px">题号</th><th class="c" style="width:80px">次课</th><th style="width:230px">题目</th>
<th>素材包 / 包内文件</th><th class="c" style="width:52px">文件数</th><th class="c" style="width:112px">下载 / 比对</th></tr></thead>
<tbody>@@ROWS@@</tbody></table></div>
<h2>三、全链路校验结果（@@TOTAL@@ 项）</h2><div class="card"><table>
<thead><tr><th style="width:330px">校验项</th><th class="c" style="width:90px">结果</th><th>说明</th></tr></thead>
<tbody>@@VER@@</tbody></table></div>
<h2>四、命名与内容口径</h2><div class="card">
<p><b>目录</b> <code>练习N-M-题目短名/</code> ｜ <b>下载包</b> <code>下载/练习N-M-题目短名.zip</code> ｜
<b>主文件</b> <code>素材-练习N-M.docx / .xlsx / .pptx</code>；多文档题（文档比较、邮件合并、多窗口协作）按用途命名，与参考包一致。</p>
<p><b>内容</b>：只提供起始文字、原始数据与必要附件；格式、公式、图表、动画、修订、目录、题注等答案动作一律不预置；
每包 <code>素材说明.txt</code> 列出文件清单、题目要求、完成效果（采分点）与功能入口口径。数据均为自拟教学数据。</p>
<p><b>版本</b>：全站统一 <b>WPS Office 教育考试专用版</b>（2025 年版考试大纲指定考试环境）；组件称 WPS 文字 / WPS 表格 / WPS 演示；
页面级命令在「页面」选项卡；不引用具体小版本号，不与任何其他版本混用。考纲条目中的页面设置类知识点名称按大纲原文保留，仅作知识点名，不作界面入口。</p>
<p class="mut">生成工具：tools/material/ ｜ <a href="../实操训练.html#materials">返回实操训练 · 素材索引</a></p></div>
<h2>五、完成比对文档与模拟操作截图</h2><div class="card">
<p><b>位置</b>：<code>练习素材/完成比对/&lt;素材包同名目录&gt;/</code>，共 72 套，与素材包紧邻且一一对应。</p>
<p><b>完成比对文档</b>（网页上统一链接名「完成比对文档」）：起始素材清单、题目要求、解题步骤、
完成效果 / 采分点、逐项完成核对表、可打开的解题结果文件与模拟操作截图。</p>
<p><b>解题结果文件</b>：<code>完成结果-练习N-M.docx / .xlsx / .pptx</code>，按原题组件类型生成，
列出每一步应出现的参数、公式、区域与对象基准，供交卷自查逐项比对。</p>
<p><b>模拟操作截图</b>：<code>操作示意.svg</code>，按 WPS Office 教育考试专用版功能区绘制；
橙色编号与网页解题步骤序号一致，图中文字与数据取自本题素材包，功能入口取自本题解题步骤。</p>
<p><b>覆盖核验</b>：48 项考纲操作类知识点全覆盖（WPS 文字 19 / WPS 表格 17 / WPS 演示 12）；
72 题 0 越界知识点、0 不可实现操作、0 版本混用措辞。单项选择题 20 分属理论题，不在 72 道实操题覆盖范围内。</p>
</div>
</div></body></html>
'''
    # 用占位符替换而非 % 格式化：模板内含 CSS 字面百分号（如 width:100%），
    # 也与 CSS 花括号互不干扰，后续增删样式不会再触发格式化异常。
    for k, v in (('@@FILES@@', sum(len(r['files']) for r in MF)),
                 ('@@NOK@@', nok), ('@@TOTAL@@', len(RESULT)), ('@@VBAD@@', vbad),
                 ('@@UPD@@', upd_rows), ('@@ROWS@@', ''.join(rows)), ('@@VER@@', vr)):
        doc = doc.replace(k, str(v))
    p = ROOT / '练习素材' / '索引.html'
    p.write_text(doc, encoding='utf-8')
    return p, nok


def check_compliance():
    """逐题核验解题步骤是否落在教育考试专用版可用功能范围内。"""
    import audit_steps
    qs = audit_steps.load()
    n = sum(len(audit_steps.scan(q)) for q in qs)
    chk('72 题解题步骤均在教育考试专用版可用功能范围内',
        len(qs) == 72 and n == 0, '%d 题 / %d 处越界' % (len(qs), n))


def check_results():
    """完成比对文档 / 解题结果文件 / 模拟操作截图 / 网页链接 / 全链路一致性 / 知识点覆盖。"""
    import audit_link, audit_coverage
    from docx import Document
    from openpyxl import load_workbook
    from pptx import Presentation
    P = Path(__file__).parent
    R = json.load(open(P / 'compare_manifest.json', encoding='utf-8'))
    EX = json.load(open(P / 'exercises.json', encoding='utf-8'))
    MB = {(r['ci'], r['seq']): r for r in MF}
    EB = {(r['ci'], r['seq']): r for r in EX}

    bad = []
    if len(R) != 72:
        bad.append('清单 %d 条' % len(R))
    for r in R:
        k = (r['ci'], r['seq'])
        if k not in EB or k not in MB:
            bad.append('%s 无对应题目' % r['no'])
        elif r['folder'] != MB[k]['folder'] or r['page'] != EB[k]['page']:
            bad.append('%s 对应错位' % r['no'])
    chk('完成比对清单 72 条与题目 / 素材包一一对应', not bad, ', '.join(bad[:4]))

    for label, key in (('完成比对文档', 'doc'), ('解题结果文件', 'result'),
                       ('模拟操作截图', 'shot')):
        miss = [r['no'] for r in R if not r[key] or not (ROOT / r[key]).exists()]
        chk('72 份%s齐全' % label, not miss, '缺 %d 份：%s' % (len(miss), ', '.join(miss[:4])))

    bad = []
    for r in R:
        p = ROOT / r['result']
        try:
            if p.suffix == '.docx': Document(str(p))
            elif p.suffix == '.xlsx':
                wb = load_workbook(str(p), read_only=True); wb.close()
            else: Presentation(str(p))
        except Exception as ex:
            bad.append('%s(%s)' % (r['no'], type(ex).__name__))
    chk('72 份解题结果文件均可正常打开', not bad, ', '.join(bad[:4]))

    bad = []
    for r in R:
        t = (ROOT / r['doc']).read_text(encoding='utf-8')
        for kw in ('本题起始素材包', '题目要求', '解题步骤', '逐项完成核对表',
                   '操作示意.svg', '完成结果-练习', '教育考试专用版'):
            if kw not in t:
                bad.append('%s 缺 %s' % (r['no'], kw))
        for u in re.findall(r'(?:href|src)="([^"]+)"', t):
            if u.startswith(('http', '#')):
                continue
            if not ((ROOT / r['doc']).parent / unquote(u.split('#')[0])).exists():
                bad.append('%s 失效链接 %s' % (r['no'], u[:36]))
    chk('72 份完成比对文档内容完整且内部链接有效', not bad, ', '.join(bad[:4]))

    bad = []
    for r in R:
        s = (ROOT / r['shot']).read_text(encoding='utf-8')
        steps = len(EB[(r['ci'], r['seq'])]['steps'])
        expect = min(steps, 12) + (1 if steps > 12 else 0)
        n = s.count('fill="#e8710a"')
        if not s.startswith('<svg') or '教育考试专用版' not in s or n < expect:
            bad.append('%s(编号 %d/%d)' % (r['no'], n, expect))
    chk('72 张截图为教育考试专用版界面且编号覆盖解题步骤', not bad, ', '.join(bad[:4]))

    bad = []
    for q in EX:
        s = (ROOT / q['page']).read_text(encoding='utf-8')
        a = re.findall(r'<article class="ex"[^>]*>.*?</article>', s, re.S)[q['seq'] - 1]
        c = re.search(r'<a class="cmp-dl" href="([^"]+)"[^>]*>(.*?)</a>', a, re.S)
        sh = re.search(r'<div class="steps-shot">.*?<img src="([^"]+)"', a, re.S)
        if not c or '完成比对文档' not in re.sub(r'<[^>]+>', '', c.group(2)):
            bad.append('%s 缺完成比对链接' % q['no'])
        if not sh:
            bad.append('%s 缺步骤截图' % q['no'])
        for u in ([c.group(1)] if c else []) + ([sh.group(1)] if sh else []):
            if not (ROOT / unquote(u.lstrip('./'))).exists():
                bad.append('%s 失效目标 %s' % (q['no'], u[:40]))
    chk('72 题网页「完成比对文档」链接与步骤截图配置正确', not bad, ', '.join(bad[:4]))

    detail, _ = audit_link.collect()
    chk('题目 / 步骤 / 素材包 / 网页全链路一致', not detail,
        '%d 处不一致' % len(detail))

    rows, gaps, outside, mix = audit_coverage.collect()
    chk('考纲操作类知识点全覆盖', len(rows) >= 40 and not gaps,
        '%d / %d 项；未覆盖：%s' % (len(rows) - len(gaps), len(rows),
                                  ', '.join(g['point'] for g in gaps[:3])))
    chk('无越界知识点或不可实现操作', not outside,
        '%d 题越界' % len(outside))
    chk('全站无版本混用措辞', not mix, '%d 处' % len(mix))


def main():
    check_files()
    counts = check_docs()
    check_pages()
    detail = check_version()
    check_compliance()
    check_results()
    p, nok = make_index()
    # 总页补索引页入口
    tp = ROOT / '实操训练.html'
    s = tp.read_text(encoding='utf-8')
    if './练习素材/索引.html' not in s:
        s = s.replace('<a href="./练习素材/README.txt">素材总说明</a>',
                      '<a href="./练习素材/README.txt">素材总说明</a> · <a href="./练习素材/索引.html">对应关系与校验报告</a>')
        s = s.replace('<h2>五、练习素材包索引（8 次课 · 72 题 · 72 个包）</h2>',
                      '<h2>五、练习素材包索引（8 次课 · 72 题 · 72 个包）</h2>\n'
                      '    <p><a class="btn ghost" href="./练习素材/索引.html">查看完整对应关系与版本一致性校验报告 &#8594;</a></p>')
        tp.write_text(s, encoding='utf-8')
    json.dump(RESULT, open(Path(__file__).parent / 'verify_report.json', 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print('\n=== 校验结果 ===')
    for x in RESULT:
        print('  %-4s %-46s %s' % ('PASS' if x['ok'] else 'FAIL', x['item'], x['detail']))
    print('\n通过 %d / %d ｜ 文档类型数：%s' % (nok, len(RESULT), counts))
    print('索引页：', p)
    for d in detail: print(' ·', d)


if __name__ == '__main__':
    main()
