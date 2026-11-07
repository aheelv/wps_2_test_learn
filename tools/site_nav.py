# -*- coding: utf-8 -*-
"""整站信息架构落地器：由 tools/site_config.json 生成导航、辅助层级与内容配置页。

设计原则（来自 GitHub 参考）：
  · core / support / archive 分层，首页与主导航只放核心；
  · 索引优先、单一配置源，所有页面由脚本统一注入，避免各页口径漂移；
  · 幂等：可反复运行，靠注释标记定位替换区，不重复插入。

用法：
  python tools/site_nav.py            # 注入导航 + 生成整站内容配置页 + 校验站内链接
  python tools/site_nav.py --check    # 只做链接与层级校验，不写文件
"""
import json, re, sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
CFG = json.load(open(ROOT / 'tools' / 'site_config.json', encoding='utf-8'))
NAV = CFG['nav']

NAV_BEGIN, NAV_END = '<!-- SITE-NAV-BEGIN -->', '<!-- SITE-NAV-END -->'
SUB_BEGIN, SUB_END = '<!-- SITE-SUBNAV-BEGIN -->', '<!-- SITE-SUBNAV-END -->'
BAR_BEGIN, BAR_END = '<!-- SITE-BAR-BEGIN -->', '<!-- SITE-BAR-END -->'
CSS_BEGIN, CSS_END = '/* SITE-NAV-CSS-BEGIN */', '/* SITE-NAV-CSS-END */'

CSS = r'''
/* ---------- 核心模块 / 辅助层级导航（由 tools/site_config.json 生成） ---------- */
.navlinks a.core{font-weight:800}
.navlinks a.core::before{content:"";display:inline-block;width:6px;height:6px;border-radius:50%;
  background:var(--accent);margin-right:6px;vertical-align:1px}
.navlinks a.core.on::before{background:#fff}
.subnav{background:#f7f9fc;border-bottom:1px solid var(--line)}
.subnav .wrap{display:flex;align-items:center;gap:10px;flex-wrap:wrap;padding:7px 22px;font-size:12.5px}
.subnav .sn-group{display:flex;align-items:center;gap:6px;flex-wrap:wrap}
.subnav .sn-label{color:var(--muted);font-weight:800;font-size:11.5px;letter-spacing:.05em;white-space:nowrap}
.subnav a{color:var(--ink-2);font-weight:600;padding:2px 7px;border-radius:6px;white-space:nowrap}
.subnav a:hover{background:var(--line-2);color:var(--brand)}
.subnav a.sn-on{background:var(--line-2);color:var(--brand)}
.subnav .sn-sep{width:1px;height:14px;background:var(--line);margin:0 4px}
.coregrid{display:grid;grid-template-columns:repeat(2,1fr);gap:16px}
.coregrid .exbanner{height:100%;flex-wrap:wrap;align-items:flex-start}
.coregrid .exbanner h3{font-size:18px}
.coregrid .exb-go{width:100%;text-align:center}
@media(max-width:900px){.coregrid{grid-template-columns:1fr}}
@media(max-width:820px){.subnav .wrap{padding:7px 15px;gap:6px}.subnav .sn-sep{display:none}}
@media print{.subnav{display:none!important}}
.tiergrid{display:grid;grid-template-columns:repeat(2,1fr);gap:16px}
@media(max-width:820px){.tiergrid{grid-template-columns:1fr}}
.tiercard{background:#fff;border:1px solid var(--line);border-radius:14px;padding:20px;box-shadow:var(--shadow)}
.tiercard h3{margin:0 0 4px;font-size:18px}
.tiercard .rule{color:var(--muted);font-size:13px;margin:0 0 12px}
.tiercard .ent{display:flex;justify-content:space-between;gap:12px;padding:7px 0;border-top:1px solid var(--line);font-size:14px}
.tiercard .ent span{color:var(--muted);font-size:12.5px}
'''


def is_active(entry, page):
    return page in entry.get('active', [])


def render_primary(page):
    parts = [NAV_BEGIN, '  <nav class="navlinks">']
    for e in NAV['primary']:
        cls = []
        if is_active(e, page):
            cls.append('on')
        if e['tier'] == 'core':
            cls.append('core')
        c = (' class="%s"' % ' '.join(cls)) if cls else ''
        parts.append('    <a%s href="%s">%s</a>' % (c, e['href'], e['name']))
    parts += ['  </nav>', NAV_END]
    return '\n'.join(parts)


def render_subnav(page):
    groups = []
    for g in NAV['support_groups']:
        links = []
        for it in g['items']:
            cls = ' class="sn-on"' if is_active(it, page) else ''
            links.append('<a%s href="%s">%s</a>' % (cls, it['href'], it['name']))
        groups.append('<span class="sn-label">%s</span>%s' % (g['label'], ''.join(links)))
    body = '<span class="sn-sep"></span>'.join(groups)
    return ('%s\n<div class="subnav"><div class="wrap">%s</div></div>\n%s'
            % (SUB_BEGIN, body, SUB_END))


def site_bar(prefix, current):
    """独立应用（题库 / 模拟系统 / 课件）顶部的一致站点条，纯内联样式，不依赖全站 CSS。"""
    links = [('学习中心', 'index.html'), ('实操训练', '实操训练.html'),
             ('理论考试', '理论考试.html'), ('模拟考试', '考试模拟系统/index.html')]
    a = ''.join('<a href="%s%s" style="color:#fff;text-decoration:none;'
                'padding:2px 8px;border-radius:6px;background:rgba(255,255,255,.12)">%s</a>'
                % (prefix, h, n) for n, h in links)
    return ('%s\n<div class="site-bar" style="background:#0f2740;color:#fff;'
            'font:600 13px/1.6 -apple-system,BlinkMacSystemFont,\'Segoe UI\',\'Microsoft YaHei\',sans-serif;'
            'padding:7px 18px;display:flex;gap:8px;align-items:center;flex-wrap:wrap">'
            '<span style="opacity:.8;margin-right:4px">站点导航</span>%s'
            '<span style="margin-left:auto;opacity:.8">当前：%s</span></div>\n%s'
            % (BAR_BEGIN, a, current, BAR_END))


def replace_marked(text, begin, end, body):
    """按标记整体替换；无标记则原样返回（由调用方决定首次插入位置）。"""
    if begin in text and end in text:
        i, j = text.index(begin), text.index(end) + len(end)
        return text[:i] + body + text[j:]
    return None


def apply_page(p, page):
    s = p.read_text(encoding='utf-8')
    orig = s
    new_nav = render_primary(page)
    hit = replace_marked(s, NAV_BEGIN, NAV_END, new_nav)
    if hit is None:
        s, n = re.subn(r'[ \t]*<nav class="navlinks">.*?</nav>', new_nav, s, count=1, flags=re.S)
        if n != 1:
            return False, '未找到主导航'
    else:
        s = hit
    new_sub = render_subnav(page)
    hit = replace_marked(s, SUB_BEGIN, SUB_END, new_sub)
    if hit is None:
        s, n = re.subn(r'(<header class="topbar">.*?</header>)', r'\1\n' + new_sub.replace('\\', '\\\\'),
                       s, count=1, flags=re.S)
        if n != 1:
            return False, '未找到 topbar'
    else:
        s = hit
    if s != orig:
        p.write_text(s, encoding='utf-8')
    return True, '更新' if s != orig else '无变化'


def patch_special():
    """三个独立应用页面：保持其自有布局，只补齐一致的站点入口。"""
    out = []
    # 1) 课件放映页
    p = ROOT / '培训课件.html'
    s = p.read_text(encoding='utf-8')
    old = re.search(r'<div id="decknav">.*?</div>', s, re.S)
    if old:
        new = ('<div id="decknav"><a href="./index.html">学习中心</a>'
               '<a href="./实操训练.html">实操训练</a><a href="./理论考试.html">理论考试</a>'
               '<a href="./考试模拟系统/index.html">模拟考试</a></div>')
        s = s.replace(old.group(0), new, 1)
        p.write_text(s, encoding='utf-8')
        out.append('培训课件.html 放映页入口')
    # 2) 电子书侧栏
    p = ROOT / '电子书.html'
    s = p.read_text(encoding='utf-8')
    old = re.search(r'<div class="bk-nav">.*?</div>', s, re.S)
    if old:
        new = ('<div class="bk-nav">\n        '
               '<a href="./index.html">学习中心</a><a href="./实操训练.html">实操训练</a>'
               '<a href="./理论考试.html">理论考试</a><a href="./考纲对照表.html">考纲对照表</a>'
               '<a href="./考试模拟系统/index.html">模拟考试</a>\n      </div>')
        s = s.replace(old.group(0), new, 1)
        p.write_text(s, encoding='utf-8')
        out.append('电子书.html 侧栏入口')
    # 3) 模拟考试系统：body 开头插入站点条（幂等）
    p = ROOT / '考试模拟系统' / 'index.html'
    s = p.read_text(encoding='utf-8')
    bar = site_bar('../', '模拟考试')
    hit = replace_marked(s, BAR_BEGIN, BAR_END, bar)
    if hit is not None:
        s = hit
    elif '<body>' in s:
        s = s.replace('<body>', '<body>\n' + bar, 1)
    if s != p.read_text(encoding='utf-8'):
        p.write_text(s, encoding='utf-8')
        out.append('考试模拟系统/index.html 站点条')
    return out


def inject_css():
    p = ROOT / 'assets' / 'style.css'
    s = p.read_text(encoding='utf-8')
    body = CSS_BEGIN + CSS + CSS_END
    hit = replace_marked(s, CSS_BEGIN, CSS_END, body)
    if hit is None:
        s = s.rstrip() + '\n\n' + body + '\n'
    else:
        s = hit
    p.write_text(s, encoding='utf-8')


def make_config_page():
    """整站内容配置页：把唯一配置源渲染成人可读、可点、可复核的交付物。"""
    tiers, cards = [], []
    hint = {'core': '首页首屏 + 主导航', 'bridge': '主导航保留一个入口',
            'support': '次级导航分组', 'archive': '次级导航末组'}
    for t in CFG['tiers']:
        ents = ''.join('<div class="ent"><b>%s</b><span>%s</span></div>'
                       % (x, hint.get(t['id'], t['id'])) for x in t['entries'])
        tiers.append('<div class="tiercard"><h3>%s · %s</h3><p class="rule">%s</p>%s</div>'
                     % (t['id'], t['name'], t['rule'], ents))
    for m in CFG['core_modules']:
        cards.append('<div class="tiercard"><h3>%s · %s</h3><p class="rule">%s</p>'
                     '<p><b>%s</b> ｜ %s</p><p class="small muted">%s</p>'
                     '<p class="small"><a href="%s">进入栏目 →</a></p></div>'
                     % (m['tier'], m['name'], m['score'], m['stat'], m['detail'], m['env'], m['href']))
    basis = ''.join('<li><b>%s</b>：%s</li>' % (b['source'], b['adopted']) for b in CFG['design_basis'])
    path = ''.join('<tr><td class="nowrap"><b>%s</b></td><td><b>%s</b></td><td class="small">%s</td></tr>'
                   % (x['stage'], x['name'], x['text']) for x in CFG['learning_path'])
    navrows = ''.join('<li><a href="%s">%s</a> · %s</li>' % (e['href'], e['name'], e['tier']) for e in NAV['primary'])
    groups = ''.join('<p class="small"><b>%s</b>：%s</p>' %
                     (g['label'], ' · '.join('<a href="%s">%s</a>' % (i['href'], i['name']) for i in g['items']))
                     for g in NAV['support_groups'])
    html = """<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>整站内容配置 · 学习中心</title>
<meta name="description" content="整站信息架构与内容配置：核心模块、辅助层级、学习路径、理论考试归属与校验结论。">
<link rel="stylesheet" href="./assets/style.css"></head><body>
<header class="topbar"><div class="wrap">
  <a class="brand" href="./index.html"><span class="logo">WPS</span><span>大连财经学院 · 计算机国家二级（WPS 类）<small>校内教学辅助资料 · 非官方</small></span></a>
  __NAV__
</div></header>
__SUBNAV__
<div class="noticebar"><div class="wrap"><span class="nb-ic">ⓘ</span><span>本页由 <code>tools/site_config.json</code> 生成，是整站栏目层级、入口与学习路径的<b>唯一配置源</b>的可读视图；修改配置后运行 <code>tools/site_nav.py</code> 即可同步全站导航。</span></div></div>
<section class="hero"><div class="wrap"><div class="eyebrow">内容架构 · 配置版本 __VER__</div>
<h1>整站内容配置</h1><p class="sub">核心模块优先：实操训练与理论考试直接对应考试得分；考试大纲、考试说明、课件等基础介绍归入辅助层级；其余归入站点服务。全站导航由单一配置源生成，避免层级与命名漂移。</p></div></section>
<main class="wrap">
  <section class="section-sm"><h2>一、四层内容与归属规则</h2><div class="tiergrid">__TIERS__</div></section>
  <section class="section-sm"><h2>二、两大核心模块</h2><div class="tiergrid">__CARDS__</div></section>
  <section class="section-sm"><h2>三、主导航与辅助层级</h2>
    <div class="grid g2"><div class="card"><h3>主导航（首屏可达）</h3><ul class="clean">__NAVROWS__</ul></div>
    <div class="card"><h3>次级导航（分组）</h3>__GROUPS__</div></div></section>
  <section class="section-sm"><h2>四、按大纲自学路线</h2>
    <div class="table-wrap"><table class="tbl"><thead><tr><th>阶段</th><th>主题</th><th>实操 + 理论双线安排</th></tr></thead><tbody>__PATH__</tbody></table></div></section>
  <section class="section-sm"><h2>五、理论考试归属</h2>
    <div class="card"><p><b>__TH_NAME__</b>：__TH_SCORE__，共 __TH_TOTAL__ 题（__TH_SEC__）。</p>
    <p class="small muted">__TH_NOTE__</p>
    <p class="small"><a href="./理论考试.html">栏目主页 →</a> · <a href="./理论题库/index.html">离线题库 →</a> ·
    <a href="./实操训练.html">并列的实操训练 →</a></p></div></section>
  <section class="section-sm"><h2>六、设计参考</h2><ul class="clean">__BASIS__</ul></section>
  <section class="section-sm"><h2>七、校验结论</h2>
    <div class="callout key"><p class="mb0">__VERDICT__</p></div>
    <p class="small mt1"><a href="./tools/site_audit_report.json">全站审计报告 JSON →</a> ·
    <a href="./tools/syllabus_coverage.json">2025 大纲覆盖矩阵 JSON →</a> ·
    <a href="./练习素材/索引.html">素材与交付校验索引 →</a></p></section>
</main>
<footer class="footer"><div class="wrap"><div class="cols"><div><h4>学习中心</h4>
<p class="small">__DISCLAIMER__</p></div><div><h4>核心模块</h4><p class="small">
<a href="./实操训练.html">实操训练</a> · <a href="./理论考试.html">理论考试</a> ·
<a href="./考试模拟系统/index.html">模拟考试</a></p></div></div>
<div class="disc">© 大连财经学院 · 计算机国家二级考试（WPS 类）课程组 ｜ 非官方考试网站</div></div></footer>
</body></html>"""
    th = CFG['theory']
    try:
        r = json.load(open(ROOT / 'tools' / 'site_audit_report.json', encoding='utf-8'))
        v = r['verdict']
        verdict = ('扫描 %d 个文件 / 缺陷 %d 处；实操 %d 题 %d 处越界；知识点 %s；'
                   '2025 大纲条目 %s；理论题 %d 道；版本混用 %d 处。现行命令名 %d 处列入白名单并附理由。'
                   % (r['files'], sum(len(x) for x in r['defects'].values()),
                      v['ops_questions'], v['ops_out_of_scope'], v['ops_knowledge_points'],
                      v['syllabus_items'], v['theory_total'], v['version_mix'],
                      sum(r['allowed']['summary'].values())))
    except Exception as e:
        verdict = '审计报告尚未生成：%s' % e
    rep = {
        '__NAV__': render_primary('整站内容配置.html'),
        '__SUBNAV__': render_subnav('整站内容配置.html'),
        '__VER__': CFG['config_version'], '__TIERS__': ''.join(tiers), '__CARDS__': ''.join(cards),
        '__NAVROWS__': navrows, '__GROUPS__': groups, '__PATH__': path, '__BASIS__': basis,
        '__TH_NAME__': th['hub'], '__TH_SCORE__': th['score'], '__TH_TOTAL__': str(th['total']),
        '__TH_SEC__': ' + '.join('%s %d 题' % (x['name'], x['count']) for x in th['sections']),
        '__TH_NOTE__': th['ownership_note'], '__VERDICT__': verdict,
        '__DISCLAIMER__': CFG['site']['disclaimer'],
    }
    for k, val in rep.items():
        html = html.replace(k, val)
    (ROOT / '整站内容配置.html').write_text(html, encoding='utf-8')


def validate_links():
    """扫描根目录所有页面的本地相对链接，输出失效清单。"""
    bad, total = [], 0
    for p in sorted(ROOT.glob('*.html')):
        s = p.read_text(encoding='utf-8')
        for href in re.findall(r'(?:href|src)="([^"]+)"', s):
            if re.match(r'^(?:https?:|#|mailto:|data:|javascript:)', href):
                continue
            # 跳过 JS 拼接出来的动态 src/href（如 "' + img + '"），不是静态引用
            if any(c in href for c in "'\"+() ") or '${' in href:
                continue
            h = unquote(href.split('#')[0].split('?')[0])
            if not h:
                continue
            total += 1
            if not (ROOT / h.lstrip('./')).exists():
                bad.append(dict(page=p.name, href=href))
    return total, bad


def main():
    check = '--check' in sys.argv
    if not check:
        inject_css()
        pages = 0
        for p in sorted(ROOT.glob('*.html')):
            if '<header class="topbar">' in p.read_text(encoding='utf-8'):
                ok, msg = apply_page(p, p.name)
                if not ok:
                    print('  [跳过] %-24s %s' % (p.name, msg))
                else:
                    pages += 1
        print('主导航 / 辅助层级注入：%d 个标准页面' % pages)
        for x in patch_special():
            print('  独立应用入口：' + x)
        make_config_page()
        print('整站内容配置页：整站内容配置.html')
    total, bad = validate_links()
    print('站内链接校验：%d 条本地引用 / %d 条失效' % (total, len(bad)))
    for b in bad[:10]:
        print('  失效 %-28s %s' % (b['page'], b['href']))
    if not check:
        (ROOT / 'tools' / 'site_links.json').write_text(
            json.dumps(dict(total=total, broken=bad), ensure_ascii=False, indent=1), encoding='utf-8')
    return len(bad)


if __name__ == '__main__':
    sys.exit(0 if main() == 0 else 1)
