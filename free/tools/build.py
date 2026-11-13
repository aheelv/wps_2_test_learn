# -*- coding: utf-8 -*-
"""WPS 二级免费资源站 — 静态页面生成器

从 data/resources.json + data/categories.json 生成全部静态 HTML 页面、
客户端检索数据 data/resources.js、站内 SVG 图标及交付文档。

用法：python tools/build.py
生成结果均为纯静态文件，无需构建工具即可直接访问。
"""
import json
import os
import re
import html
import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, 'data')
CONTENT_DIR = os.path.join(ROOT, 'content')
IMG_DIR = os.path.join(ROOT, 'assets', 'img')
TODAY = datetime.date.today().isoformat()

with open(os.path.join(DATA_DIR, 'resources.json'), encoding='utf-8') as f:
    RESOURCES = json.load(f)
with open(os.path.join(DATA_DIR, 'categories.json'), encoding='utf-8') as f:
    CATEGORIES = json.load(f)

BY_ID = {r['id']: r for r in RESOURCES}
BY_CAT = {c['id']: c for c in CATEGORIES}
URL_COUNT = sum(len(r['links']) for r in RESOURCES)
SITE_TITLE = 'WPS 二级免费资源站'


def esc(s):
    return html.escape(str(s if s is not None else ''), quote=True)


def rich(s):
    """把数据里的 **加粗** 与 `代码` 标记转成安全的 HTML。"""
    t = esc(s)
    t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'`([^`]+)`', r'<code>\1</code>', t)
    return t


def write(rel, text):
    p = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)
    return rel


def stars(n):
    n = max(0, min(5, int(n)))
    return '<span class="stars">%s<span class="off">%s</span></span>' % ('★' * n, '★' * (5 - n))


def level_pill(v):
    cls = 'high' if v in ('极高', '高') else ('mid' if v == '中' else 'low')
    return '<span class="level-pill %s">%s</span>' % (cls, esc(v))


def prefix(depth):
    return '../' if depth == 1 else ''


def navbar(p, active):
    items = [
        ('index.html', '首页', 'home'),
        ('categories.html', '分类浏览', 'categories'),
        ('guide.html', '备考指南', 'guide'),
        ('search.html', '全站检索', 'search'),
        ('about.html', '关于', 'about'),
    ]
    links = []
    for href, label, key in items:
        cls = 'nav-link' + (' active' if active == key else '')
        if key == 'categories':
            sub = ''.join(
                '<li><a class="dropdown-item" href="%scategory/%s.html">%s <span class="text-muted small">(%d)</span></a></li>'
                % (p, c['id'], esc(c['name']), sum(1 for r in RESOURCES if r['category'] == c['id']))
                for c in CATEGORIES)
            links.append(
                '<li class="nav-item dropdown">'
                '<a class="%s dropdown-toggle" href="%scategories.html" data-bs-toggle="dropdown" role="button" aria-expanded="false">%s</a>'
                '<ul class="dropdown-menu dropdown-menu-end">%s'
                '<li><hr class="dropdown-divider"></li>'
                '<li><a class="dropdown-item fw-bold" href="%scategories.html">查看全部分类 →</a></li>'
                '</ul></li>' % (cls, p, label, sub, p))
        else:
            links.append('<li class="nav-item"><a class="%s" href="%s%s">%s</a></li>' % (cls, p, href, label))
    return '''<nav class="navbar navbar-expand-lg site-nav navbar-dark">
  <div class="container">
    <a class="navbar-brand" href="{p}index.html"><span class="brand-mark">W2</span>{title}</a>
    <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#mainNav"
      aria-controls="mainNav" aria-expanded="false" aria-label="切换导航"><span class="navbar-toggler-icon"></span></button>
    <div class="collapse navbar-collapse" id="mainNav">
      <ul class="navbar-nav ms-auto mb-2 mb-lg-0 align-items-lg-center">{links}</ul>
      <form class="d-flex site-search ms-lg-3" action="{p}search.html" method="get" role="search">
        <input class="form-control form-control-sm" type="search" name="q" placeholder="搜索资源…" aria-label="搜索资源">
        <button class="btn btn-sm" type="submit">检索</button>
      </form>
    </div>
  </div>
</nav>'''.format(p=p, title=SITE_TITLE, links=''.join(links))


def footer(p):
    cat_links = ''.join(
        '<li><a href="%scategory/%s.html">%s</a></li>' % (p, c['id'], esc(c['name'])) for c in CATEGORIES)
    return '''<footer class="site-footer">
  <div class="container">
    <div class="row g-4">
      <div class="col-md-5">
        <h6>{title}</h6>
        <p class="small mb-2">面向 NCRE 二级 WPS Office 高级应用与设计（科目代码 67）的免费资源索引。依据 2025 年版考试大纲与官方样题整理，资料核验于 2026-11-11。</p>
        <p class="small mb-0">页面框架基于 <a href="https://github.com/StartBootstrap/startbootstrap-blog-home" target="_blank" rel="noopener noreferrer">Start Bootstrap · Blog Home</a>（MIT）。</p>
      </div>
      <div class="col-6 col-md-3"><h6>分类导航</h6><ul class="foot-links">{cat_links}</ul></div>
      <div class="col-6 col-md-4"><h6>站点页面</h6><ul class="foot-links">
        <li><a href="{p}index.html">首页</a></li>
        <li><a href="{p}categories.html">分类总览</a></li>
        <li><a href="{p}guide.html">备考指南</a></li>
        <li><a href="{p}search.html">全站检索</a></li>
        <li><a href="{p}about.html">关于与说明</a></li>
        <li><a href="{p}TEMPLATE.md">模板与许可证</a></li>
      </ul></div>
    </div>
    <div class="foot-bottom d-flex flex-wrap justify-content-between gap-2">
      <span>资料内容由公开免费资源整理，版权归各原作者所有；本站仅作索引与学习规划。</span>
      <span>生成日期 {today} · 纯静态，无追踪、无外部依赖</span>
    </div>
  </div>
</footer>'''.format(title=SITE_TITLE, cat_links=cat_links, p=p, today=TODAY)


def page(title, desc, depth, active, body):
    p = prefix(depth)
    return '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
<meta name="description" content="{desc}">
<meta name="author" content="WPS 二级免费资源站">
<title>{title} · {site}</title>
<link rel="icon" type="image/x-icon" href="{p}assets/template/favicon.ico">
<link href="{p}assets/template/styles.css" rel="stylesheet">
<link href="{p}assets/css/site.css" rel="stylesheet">
</head>
<body data-base="{p}">
{nav}
{body}
{foot}
<script src="{p}assets/vendor/bootstrap.bundle.min.js"></script>
<script src="{p}assets/template/scripts.js"></script>
<script src="{p}data/resources.js"></script>
<script src="{p}assets/js/site.js"></script>
</body>
</html>
'''.format(title=esc(title), desc=esc(desc), site=SITE_TITLE, p=p,
           nav=navbar(p, active), body=body, foot=footer(p))


def breadcrumb(p, trail):
    items = []
    for i, (label, href) in enumerate(trail):
        if i == len(trail) - 1:
            items.append('<li class="breadcrumb-item active" aria-current="page">%s</li>' % esc(label))
        else:
            items.append('<li class="breadcrumb-item"><a href="%s">%s</a></li>' % (p + href, esc(label)))
    return '<div class="breadcrumb-bar"><div class="container"><ol class="breadcrumb">%s</ol></div></div>' % ''.join(items)


def haystack(r):
    # 检索索引只保留外链的域名（大小写不敏感），不写入完整 URL：
    # 避免大小写敏感的服务端路径被小写化后出现无法访问的地址字面量。
    domains = [l['label'] + ' ' + re.sub(r'^https?://([^/]+).*$', r'\1', l['url'])
               for l in r['links']]
    parts = [r['name'], r['summary'], r['purpose'], r['access'], r['free'], r['caveat'],
             r['kind'], BY_CAT[r['category']]['name'], ' '.join(r['tags']),
             ' '.join(r['syllabus'])] + domains
    return ' '.join(parts).lower().replace(' ', '')


def rcard(r, p, extra_class='filter-item'):
    c = BY_CAT[r['category']]
    url = p + 'resource/' + r['id'] + '.html'
    tags = ''.join('<span class="chip">%s</span>' % esc(t) for t in r['tags'][:3])
    return '''<div class="col-md-6 col-xl-4 mb-4 {ec}" data-text="{txt}" data-tags="{tags}" data-rating="{rating}">
  <div class="rcard">
    <div class="rcard-top" style="background:{accent}"></div>
    <div class="rcard-body">
      <div class="d-flex justify-content-between align-items-start mb-2 gap-2">
        <span class="chip chip-kind">{cat}</span>{stars}
      </div>
      <a class="rcard-title" href="{url}">{name}</a>
      <p class="rcard-sum">{summary}</p>
      <div class="mb-2">{chips}</div>
      <div class="rcard-foot">
        <span>零基础 <b>{zero}</b> · 备考 <b>{exam}</b></span>
        <a href="{url}">详情 →</a>
      </div>
    </div>
  </div>
</div>'''.format(ec=extra_class, txt=esc(haystack(r)), tags=esc('|'.join(r['tags'])),
                 rating=r['rating'], accent=c['accent'], cat=esc(c['name']), stars=stars(r['rating']),
                 url=url, name=esc(r['name']), summary=esc(r['summary']), chips=tags,
                 zero=esc(r['zero']), exam=esc(r['exam']))


def catcard(c, p, show_list=False):
    n = sum(1 for r in RESOURCES if r['category'] == c['id'])
    listing = ''
    if show_list:
        rows = [r for r in RESOURCES if r['category'] == c['id']][:4]
        listing = '<ul class="small mb-3 ps-3 text-muted">' + ''.join(
            '<li><a href="%sresource/%s.html">%s</a></li>' % (p, r['id'], esc(r['name'])) for r in rows
        ) + '</ul>'
    return '''<div class="col-md-6 col-lg-4 mb-4">
  <div class="catcard">
    <div class="cat-icon" style="background:{accent}" aria-hidden="true">{icon}</div>
    <h3><a href="{p}category/{cid}.html" class="text-dark">{name}</a></h3>
    <p>{desc}</p>
    {listing}
    <div class="d-flex justify-content-between align-items-center">
      <span class="cat-count">{n} 条资源</span>
      <a class="small fw-bold" href="{p}category/{cid}.html">进入分类 →</a>
    </div>
  </div>
</div>'''.format(accent=c['accent'], icon=inline_icon(c['id']), p=p, cid=c['id'], name=esc(c['name']),
                 desc=esc(c['desc']), listing=listing, n=n)


# ---------------------------------------------------------------- 图标
ICON_PATHS = {
    'docs': '<path d="M7 3h7l5 5v13H7z"/><path d="M14 3v5h5"/><path d="M10 13h6M10 17h6"/>',
    'courses': '<circle cx="12" cy="12" r="9"/><path d="M10 8.5l6 3.5-6 3.5z"/>',
    'opensource': '<path d="M8 5l-4 7 4 7M16 5l4 7-4 7M14 4l-4 16"/>',
    'templates': '<rect x="3" y="3" width="8" height="8" rx="1"/><rect x="13" y="3" width="8" height="8" rx="1"/><rect x="3" y="13" width="8" height="8" rx="1"/><rect x="13" y="13" width="8" height="8" rx="1"/>',
    'tools': '<path d="M14.5 5.5a4 4 0 0 0-5 5L4 16l4 4 5.5-5.5a4 4 0 0 0 5-5l-3 3-2.5-2.5z"/>',
    'reference': '<circle cx="12" cy="12" r="9"/><path d="M15.5 8.5l-2 5-5 2 2-5z"/>',
}


HERO_SVG = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 320" width="320" height="320">
<g fill="none" stroke="#ffffff" stroke-opacity="0.5" stroke-width="1.2">
<circle cx="160" cy="160" r="60"/><circle cx="160" cy="160" r="100"/><circle cx="160" cy="160" r="140"/>
<path d="M160 10v300M10 160h300"/><path d="M54 54l212 212M266 54L54 266"/>
</g>
<g fill="#fbbf24" fill-opacity="0.85">
<circle cx="160" cy="20" r="5"/><circle cx="300" cy="160" r="5"/><circle cx="160" cy="300" r="5"/><circle cx="20" cy="160" r="5"/>
<circle cx="160" cy="60" r="3"/><circle cx="260" cy="160" r="3"/><circle cx="160" cy="260" r="3"/><circle cx="60" cy="160" r="3"/>
</g>
</svg>
'''


def icon_svg(cid, size=26):
    """内联 SVG：避免部分静态托管服务把 .svg 返回成非标准 MIME 导致破图。"""
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="%d" height="%d" '
            'fill="none" stroke="#ffffff" stroke-width="1.8" stroke-linecap="round" '
            'stroke-linejoin="round" aria-hidden="true">%s</svg>' % (size, size, ICON_PATHS[cid]))


# 兼容旧命名
inline_icon = icon_svg


def gen_icons():
    for c in CATEGORIES:
        write('assets/img/icon-%s.svg' % c['id'], icon_svg(c['id'], 48) + '\n')
    write('assets/img/hero-pattern.svg', HERO_SVG)


def gen_data_js():
    payload = {
        'generated': TODAY,
        'resources': RESOURCES,
        'categories': CATEGORIES,
    }
    js = ('/* 由 tools/build.py 从 data/resources.json 生成，请勿手改。 */\n'
          'window.SITE_DATA = ' + json.dumps(payload, ensure_ascii=False, indent=2) + ';\n')
    write('data/resources.js', js)


# ---------------------------------------------------------------- 首页
def gen_index():
    p = ''
    hero = '''<section class="page-hero">
  {hero_art}
  <div class="container">
    <span class="hero-kicker">NCRE 二级 WPS Office · 科目代码 67</span>
    <h1>WPS 二级免费资源站</h1>
    <p class="lead">把分散在 WPS 官方学堂、官方博客、B 站、CSDN、GitHub / Gitee 与公开在线备考站里的免费备考资料，
    按语义整理成一套可检索、可随时查阅的索引。每条资源都标注用途、获取方式与免费限制。</p>
    <div class="hero-stats">
      <div class="stat"><b>{nr}</b><span>条免费资源</span></div>
      <div class="stat"><b>{nc}</b><span>个语义分类</span></div>
      <div class="stat"><b>{nu}</b><span>个获取入口</span></div>
      <div class="stat"><b>2</b><span>份官方 PDF 站内副本</span></div>
    </div>
    <div class="mt-4 d-flex gap-2 flex-wrap">
      <a class="btn btn-hero" href="categories.html">按分类浏览 →</a>
      <a class="btn btn-hero-ghost" href="guide.html">查看备考指南</a>
      <a class="btn btn-hero-ghost" href="search.html">全站检索</a>
    </div>
  </div>
</section>'''.format(nr=len(RESOURCES), nc=len(CATEGORIES), nu=URL_COUNT,
                       hero_art=HERO_SVG.replace('<svg ', '<svg class="hero-art" aria-hidden="true" ', 1))

    steps = [
        ('1', '先定范围', '读 2025 年版考试大纲与官方样题 PDF，确认真实难度与颗粒度。',
         'resource/d-outline-pdf.html', '官方大纲'),
        ('2', '再打基础', '用官方通关课按考纲逐项打通，三门新手入门课当字典随时回查。',
         'resource/c-fast-pass.html', '高效通关课'),
        ('3', '最后冲刺', '真题讲解打通考场动线，在线版模拟考试系统跑 2 套 120 分钟全真卷。',
         'resource/u-exam-sim.html', '模拟考试系统'),
    ]
    step_html = ''.join('''<div class="col-md-4 mb-3">
  <div class="catcard h-100">
    <div class="d-flex align-items-center gap-2 mb-2"><span class="step-num">%s</span><h3 class="mb-0">%s</h3></div>
    <p>%s</p><a class="small fw-bold" href="%s">%s →</a>
  </div></div>''' % (n, esc(t), esc(d), p + h, esc(l)) for n, t, d, h, l in steps)

    cats = ''.join(catcard(c, p) for c in CATEGORIES)
    picks = ['d-sample-pdf', 'd-outline-pdf', 'c-fast-pass', 'c-damao-real', 'o-local-site', 'u-exam-sim']
    picked = ''.join(rcard(BY_ID[i], p, extra_class='') for i in picks)

    body = hero + '''<div class="container py-5">
  <div class="section-head"><div><div class="eyebrow">Start here</div><h2 class="section-title">从哪里开始</h2>
    <p class="section-sub mb-0">操作题占 80 分，先把靶子看清，再决定学什么。</p></div></div>
  <div class="row mb-5">{steps}</div>

  <div class="section-head"><div><div class="eyebrow">Browse by category</div><h2 class="section-title">按类别浏览</h2>
    <p class="section-sub mb-0">六类资源各司其职，避免把所有链接堆在一个页面里。</p></div>
    <a class="small fw-bold" href="categories.html">分类总览 →</a></div>
  <div class="row mb-5">{cats}</div>

  <div class="section-head"><div><div class="eyebrow">Editor's picks</div><h2 class="section-title">优先看的 6 条</h2>
    <p class="section-sub mb-0">如果只选三样：官方通关课 + 真题讲解 + 官方样题 PDF。</p></div>
    <a class="small fw-bold" href="search.html?q=&amp;cat=">查看全部 {n} 条 →</a></div>
  <div class="row mb-4">{picked}</div>

  <div class="callout callout-blue">
    <strong>关于「免费」：</strong>本站只收录公开免费资源，但部分资源存在前置条件——
    WPS 教学平台需要高校邀请码、GitHub / Gitee 题库内容滞后于 2025 年版大纲、B 站部分功能需登录。
    每条资源详情页都单独列出了免费限制说明，<a href="about.html">也可在「关于」页看总览</a>。
  </div>
</div>'''.format(steps=step_html, cats=cats, picked=picked, n=len(RESOURCES))
    write('index.html', page('首页', 'NCRE 二级 WPS Office 免费备考资源索引：文档教程、视频课程、开源项目、模板素材、工具服务与设计参考。', 0, 'home', body))


# ---------------------------------------------------------------- 分类总览
def gen_categories():
    p = ''
    cards = ''.join(catcard(c, p, show_list=True) for c in CATEGORIES)
    table = ''.join('''<tr><td><a href="category/{cid}.html"><strong>{name}</strong></a></td>
      <td>{desc}</td><td>{use}</td><td class="text-center">{n}</td></tr>'''.format(
        cid=c['id'], name=esc(c['name']), desc=esc(c['desc']), use=esc(c['use']),
        n=sum(1 for r in RESOURCES if r['category'] == c['id'])) for c in CATEGORIES)
    body = '''<div class="page-head"><div class="container">
  <h1>分类总览</h1>
  <p>按「这份资料是拿来做什么的」而不是「它在哪个网站」分类。6 类共 {nr} 条资源，每条都有独立详情页。</p>
</div></div>
<div class="container">
  <div class="row mb-5">{cards}</div>
  <div class="prose mb-4">
    <h2>分类逻辑对照</h2>
    <div class="table-responsive"><table class="table table-hover align-middle">
      <thead><tr><th>分类</th><th>收录什么</th><th>什么时候用</th><th class="text-center">条数</th></tr></thead>
      <tbody>{table}</tbody></table></div>
    <p class="text-muted small mb-0">同一份资料可能横跨多类，本站按「主要用途」只归入一类，并在详情页用「相关资源」建立横向链接。</p>
  </div>
</div>'''.format(nr=len(RESOURCES), cards=cards, table=table)
    write('categories.html', page('分类总览', '按语义划分的六类免费备考资源，附分类逻辑对照表。', 0, 'categories', body))


# ---------------------------------------------------------------- 分类页
def gen_category(c):
    p = '../'
    rows = [r for r in RESOURCES if r['category'] == c['id']]
    freq = {}
    for r in rows:
        for t in r['tags']:
            freq[t] = freq.get(t, 0) + 1
    hot = [t for t, _ in sorted(freq.items(), key=lambda kv: (-kv[1], kv[0]))[:10]]
    tag_btns = ''.join('<button type="button" class="tag-btn" data-tag="%s">%s</button>' % (esc(t), esc(t)) for t in hot)
    cards = ''.join(rcard(r, p) for r in rows)
    other = ''.join(
        '<a class="chip chip-accent" href="%s.html">%s</a>' % (x['id'], esc(x['name']))
        for x in CATEGORIES if x['id'] != c['id'])
    body = breadcrumb(p, [('首页', 'index.html'), ('分类总览', 'categories.html'), (c['name'], '')]) + '''
<div class="page-head"><div class="container d-flex align-items-start gap-3 flex-wrap">
  <div class="cat-icon mb-0" style="background:{accent};width:56px;height:56px" aria-hidden="true">{icon}</div>
  <div><h1>{name}</h1><p>{desc}</p>
    <div class="mt-2 small text-muted"><strong>适用场景：</strong>{use}</div></div>
</div></div>
<div class="container">
  <div class="filter-bar">
    <div class="row g-3 align-items-end">
      <div class="col-md-5"><label for="filterInput">在本分类内搜索</label>
        <input class="form-control" id="filterInput" type="search" placeholder="输入关键词，如「透视表」「免费」「母版」"></div>
      <div class="col-md-3"><label for="minRating">最低推荐度</label>
        <select class="form-select" id="minRating">
          <option value="0">全部</option><option value="5">★★★★★</option>
          <option value="4">★★★★ 及以上</option><option value="3">★★★ 及以上</option></select></div>
      <div class="col-md-4"><label>热门标签（点击筛选）</label><div class="tag-filter">{tags}</div></div>
    </div>
  </div>
  <div class="d-flex justify-content-between align-items-center mb-3 flex-wrap gap-2">
    <div class="result-count">当前显示 <strong id="visibleCount">{n}</strong> / {n} 条</div>
    <a class="small" href="{p}search.html?cat={cid}">在全站检索中筛选此分类 →</a>
  </div>
  <div class="row" data-filter-root>{cards}</div>
  <div class="empty-state" id="filterEmpty">没有符合条件的资源，试试清空关键词或标签。</div>
  <div class="prose mt-4"><h2>其他分类</h2><p>{other}</p>
    <p class="mb-0 small text-muted">本页卡片为静态内容，关闭 JavaScript 也可正常浏览与跳转；搜索与标签筛选为渐进增强。</p></div>
</div>'''.format(accent=c['accent'], p=p, cid=c['id'], name=esc(c['name']), desc=esc(c['desc']),
                 use=esc(c['use']), tags=tag_btns, n=len(rows), cards=cards, other=other,
                 icon=icon_svg(c['id'], 30))
    write('category/%s.html' % c['id'],
          page(c['name'], '%s — %s' % (c['name'], c['desc']), 1, 'categories', body))


# ---------------------------------------------------------------- 详情页
def gen_resource(r):
    p = '../'
    c = BY_CAT[r['category']]
    trail = [('首页', 'index.html'), ('分类总览', 'categories.html'),
             (c['name'], 'category/%s.html' % c['id']), (r['name'], '')]

    def link_item(l):
        u = l['url']
        if u.startswith(('http://', 'https://')):
            href, target, arrow = u, ' target="_blank" rel="noopener noreferrer"', '↗'
        else:
            href, target, arrow = p + u, '', '→'
        return ('<div class="link-item"><span class="text-muted">%s</span><div>'
                '<a class="ext" href="%s"%s>%s</a>'
                '<div class="small text-muted">%s</div></div></div>'
                % (arrow, esc(href), target, esc(l['label']), esc(u)))

    links_html = (''.join(link_item(l) for l in r['links'])
                  if r['links'] else '<p class="text-muted mb-0">该资源的内容已整理在本站页面，详见下方站内附件。</p>')

    asset_html = ''
    loc = r['asset']
    if loc.startswith('assets/'):
        asset_html = ('<p><a class="btn btn-sm btn-outline-primary" href="%s%s" target="_blank" rel="noopener">'
                      '打开站内副本（%s）</a></p>' % (p, esc(loc), esc(os.path.basename(loc))))
    elif loc.startswith('content/'):
        asset_html = '<p><a class="btn btn-sm btn-outline-primary" href="%s%s">查看资料原文（Markdown）</a></p>' % (p, esc(loc))
    else:
        asset_html = '<p class="text-muted small mb-0">该资源通过上方线上正式网址访问，本站不托管其原始文件。</p>'

    syllabus = ''.join('<li>%s</li>' % esc(s) for s in r['syllabus']) or '<li class="text-muted">不直接对应具体考纲条目（方法论 / 补充记录）</li>'
    tags = ''.join('<span class="chip">%s</span>' % esc(t) for t in r['tags'])
    related = ''.join(
        '<a class="d-block small py-1 border-bottom" href="%s.html">%s <span class="text-muted">· %s</span></a>'
        % (i, esc(BY_ID[i]['name']), esc(BY_CAT[BY_ID[i]['category']]['name']))
        for i in r['related'] if i in BY_ID)

    body = breadcrumb(p, trail) + '''
<div class="page-head"><div class="container">
  <div class="d-flex flex-wrap align-items-center gap-2 mb-2">
    <span class="chip chip-kind">{cat}</span><span class="chip">{kind}</span>{stars}
  </div>
  <h1>{name}</h1><p>{summary}</p>
</div></div>
<div class="container">
  <div class="row">
    <div class="col-lg-8">
      <div class="detail-block"><h2>用途</h2><p>{purpose}</p>
        <div class="mt-3">{tags}</div></div>

      <div class="detail-block"><h2>获取方式</h2><p>{access}</p>
        <div class="mt-3">{links_html}</div>
        <hr><h2 class="mt-3">站内附件 / 在线链接</h2>{asset_html}</div>

      <div class="detail-block"><h2>免费限制说明</h2>
        <div class="callout"><strong>免费但有边界：</strong>{free}</div>
        <p class="small text-muted mt-3 mb-0">「免费」指获取该资源本身不需要付费；不等同于无门槛、无时效、无账号要求。</p></div>

      <div class="detail-block"><h2>对应考纲 / 适用范围</h2><ul>{syllabus}</ul></div>

      <div class="detail-block"><h2>使用提醒</h2>
        <div class="callout callout-blue">{caveat}</div></div>
    </div>

    <div class="col-lg-4">
      <div class="info-card mb-4">
        <h5>资源速览</h5>
        <div class="kv"><span>所属分类</span><span><a href="{p}category/{cid}.html">{cat}</a></span></div>
        <div class="kv"><span>资源性质</span><span>{kind}</span></div>
        <div class="kv"><span>推荐度</span><span>{stars2}</span></div>
        <div class="kv"><span>零基础友好</span><span>{zero}</span></div>
        <div class="kv"><span>备考适配</span><span>{exam}</span></div>
        <div class="kv"><span>外部入口</span><span>{nlinks} 个</span></div>
      </div>
      <div class="info-card mb-4"><h5>相关资源</h5>{related}</div>
      <div class="info-card"><h5>快捷跳转</h5>
        <a class="d-block small py-1" href="{p}category/{cid}.html">← 返回「{cat}」分类</a>
        <a class="d-block small py-1" href="{p}search.html">全站检索</a>
        <a class="d-block small py-1" href="{p}guide.html">备考指南</a>
        <a class="d-block small py-1" href="{p}about.html">免费限制总览</a>
      </div>
    </div>
  </div>
</div>'''.format(cat=esc(c['name']), kind=esc(r['kind']), stars=stars(r['rating']),
                 name=esc(r['name']), summary=esc(r['summary']), purpose=rich(r['purpose']),
                 tags=tags, access=rich(r['access']), links_html=links_html, asset_html=asset_html,
                 free=rich(r['free']), syllabus=syllabus, caveat=rich(r['caveat']),
                 p=p, cid=c['id'], stars2=stars(r['rating']),
                 zero=level_pill(r['zero']), exam=level_pill(r['exam']),
                 nlinks=len(r['links']), related=related)
    write('resource/%s.html' % r['id'],
          page(r['name'], '%s — %s' % (r['name'], r['summary']), 1, 'categories', body))


# ---------------------------------------------------------------- 检索页
def gen_search():
    p = ''
    opts = ''.join('<option value="%s">%s（%d）</option>' % (
        c['id'], esc(c['name']), sum(1 for r in RESOURCES if r['category'] == c['id']))
        for c in CATEGORIES)
    words = ['透视表', '母版', '交叉引用', '真题', '零基础', '需邀请码', '在线版', '模拟考试', '超纲']
    hot = ''.join('<button type="button" class="hot-word" data-q="%s">%s</button>' % (esc(w), esc(w)) for w in words)
    body = '''<div class="search-hero"><div class="container">
  <h1 class="fw-bold mb-2">全站检索</h1>
  <p class="text-muted mb-3">在 {nr} 条资源的名称、用途、获取方式、免费限制、标签与考纲映射中做客户端全文匹配，浏览器端即时完成。</p>
  <div class="input-group mb-3">
    <input class="form-control" id="q" type="search" placeholder="输入关键词，多个词用空格分隔（如：表格 免费）" autocomplete="off">
    <button class="btn" id="searchBtn" type="button">检索</button>
  </div>
  <div class="d-flex flex-wrap gap-2 align-items-center">
    <span class="small text-muted me-1">热门：</span>{hot}
  </div>
</div></div>
<div class="container py-4" id="searchApp">
  <div class="filter-bar">
    <div class="row g-3 align-items-end">
      <div class="col-md-4"><label for="catFilter">限定分类</label>
        <select class="form-select" id="catFilter"><option value="">全部分类</option>{opts}</select></div>
      <div class="col-md-4"><label for="ratingFilter">最低推荐度</label>
        <select class="form-select" id="ratingFilter">
          <option value="0">全部</option><option value="5">★★★★★</option>
          <option value="4">★★★★ 及以上</option><option value="3">★★★ 及以上</option></select></div>
      <div class="col-md-4 text-md-end pb-1"><span class="result-count" id="resultCount"></span></div>
    </div>
  </div>
  <div class="row" id="results"></div>
  <div class="empty-state" id="emptyState">没有匹配的资源。试试更短的关键词，或清空分类与推荐度限制。</div>
  <noscript><div class="callout mt-3">检索功能需要 JavaScript。若已关闭，请改用「分类浏览」逐页查看，本站所有详情页均为静态页面。</div></noscript>
  <div class="prose mt-4"><h2>检索说明</h2>
    <ul class="mb-0">
      <li>支持多个关键词（空格分隔，需同时匹配），例如「透视表 免费」。</li>
      <li>匹配范围含名称、用途、获取方式、免费限制、注意事项、标签、考纲条目与链接文字。</li>
      <li>结果按推荐度排序；顶部导航与分类页的搜索框会把关键词带到这里。</li>
      <li>按 <code>/</code> 键可快速聚焦搜索框。所有资源详情页链接均为站内相对路径，部署后随正式域名自动解析。</li>
    </ul>
  </div>
</div>'''.format(nr=len(RESOURCES), opts=opts, hot=hot)
    write('search.html', page('全站检索', '在全部免费资源中按关键词、分类与推荐度检索。', 0, 'search', body))


# ---------------------------------------------------------------- 备考指南
GUIDE_DOCS = [
    ('difficulty', '样题难度基准', 'content/样题难度基准.md'),
    ('order', '知识点分级学习顺序', 'content/学习顺序.md'),
    ('plan', '4 周 48 小时计划', 'content/四周计划.md'),
    ('mapping', '考纲条款映射', 'content/考纲映射.md'),
    ('boundary', '超纲边界与易误判考点', 'content/超纲边界.md'),
]


def gen_guide():
    p = ''
    anchors = ''.join('<a class="list-group-item" href="#%s">%s</a>' % (a, esc(t)) for a, t, _ in GUIDE_DOCS)
    doc_links = ''.join('<li><a href="%s">%s（Markdown 原文）</a></li>' % (f, esc(t)) for _, t, f in GUIDE_DOCS)

    diff = '''<div class="row g-3">
  <div class="col-md-4"><div class="catcard h-100"><h3>文字 · 30 分</h3>
    <ul class="small mb-0"><li>多级编号自定义格式与级别间重新编号</li><li>题注按章编号「图 4-1」、交叉引用、F9 更新域</li>
    <li>三线表边框磅值、重复标题行</li><li>分 4 节独立页眉页脚与不同页码格式</li><li>目录更新时保持格式、另输出 PDF</li></ul></div></div>
  <div class="col-md-4"><div class="catcard h-100"><h3>表格 · 30 分</h3>
    <ul class="small mb-0"><li>条件格式重复值、数据有效性下拉 + 出错警告</li><li>DATEDIF 动态工龄、VLOOKUP 查找引用</li>
    <li>COUNTIFS 跨区域复制的引用方式陷阱</li><li>文本分列、冻结首行、打印缩放一页</li><li>饼图图例与百分比数据标签</li></ul></div></div>
  <div class="col-md-4"><div class="catcard h-100"><h3>演示 · 20 分</h3>
    <ul class="small mb-0"><li>编辑母版统一设背景、批量加 Logo、隐藏背景图形</li><li>艺术字预设样式名（渐变填充-金色，轮廓-着色4）</li>
    <li>动画劈裂/切入 + 方向 + 开始方式</li><li>母版级超链接返回目录、SmartArt 梯形列表</li><li>图片柔化边缘 25 磅 + 置于底层、切换速度</li></ul></div></div>
</div>
<div class="callout mt-3">样题属于「Word / PPT 高级应用」层级，不是 Office 基础操作。因此本站刻意不推荐纯新手速成资料作为主力，而是分层给出：官方精讲课打底 → 官方入门课补操作细节 → 真题讲解打通考场动作路径。</div>'''

    order = '''<div class="table-responsive"><table class="table table-hover align-middle">
<thead><tr><th>阶段</th><th>模块</th><th>重点</th><th>主资源</th></tr></thead><tbody>
<tr><td rowspan="3"><strong>通用底层</strong></td><td>L0 界面与文件</td><td>功能区、视图、新建保存、文档属性</td><td>三门新手课第 1 章 + 通关课 1-2</td></tr>
<tr><td>L0.5 快捷键</td><td><strong>F4 引用切换、F9 更新域</strong>、Ctrl 系列</td><td>所有模块通用</td></tr>
<tr><td>L0.8 素材规范</td><td>后续操作均基于原文件，否则不得分</td><td>官方样题题面</td></tr>
<tr><td rowspan="3"><strong>文字 6 级</strong></td><td>L1—L2 基础与样式</td><td>格式刷、回车符 vs 换行符、改样式而非逐个改格式、多级编号</td><td>文字新手课第 1—2 章</td></tr>
<tr><td>L3—L4 页面与引用</td><td><strong>分节符是分水岭</strong>；题注、交叉引用、自动目录</td><td>官方交叉引用图文 → 通关课 → 真题讲解</td></tr>
<tr><td>L5—L6 表格图文与审阅</td><td>三线表、图片柔化、邮件合并、输出 PDF</td><td>通关课 2-4 → 真题讲解</td></tr>
<tr><td rowspan="3"><strong>表格 6 级</strong></td><td>L1—L2 录入与引用</td><td>分列、Ctrl+E、日期自定义格式、相对/绝对/混合引用 + F4</td><td>表格新手课第 1、4 章</td></tr>
<tr><td>L3—L4 函数与数据管理</td><td>VLOOKUP &gt; 统计 &gt; 文本 &gt; 日期；条件格式 + 数据有效性</td><td>通关课 4-1~4-5、5-1~5-5</td></tr>
<tr><td>L5—L6 透视表与输出</td><td><strong>数据透视表是独立考点</strong>；打印缩放一页、保护工作表</td><td>透视表专项 + 通关课 5-6</td></tr>
<tr><td rowspan="2"><strong>演示 5 级</strong></td><td>L1—L3 基础、母版、对象</td><td>改母版是杠杆；艺术字预设样式名、SmartArt 方向/色值/尺寸</td><td>演示新手课 + SmartArt 官方图文</td></tr>
<tr><td>L4—L5 动画与交互</td><td>具体效果名、方向、开始方式；<strong>母版内做超链接</strong>、文件打包</td><td>通关课 6-8~6-9 → 真题讲解</td></tr>
</tbody></table></div>'''

    plan = '''<div class="row g-3 mb-3">
  <div class="col-md-6 col-lg-3"><div class="catcard h-100"><span class="chip chip-accent">W1 · 12h</span><h3 class="mt-2">地基 + 文字上半</h3>
    <p class="small">界面与文件、快捷键、文字 L1—L3。样题文字 (1)—(5) 逐条对照做，不做真题。</p>
    <div class="small text-muted">产出：《文字操作速查表》</div></div></div>
  <div class="col-md-6 col-lg-3"><div class="catcard h-100"><span class="chip chip-accent">W2 · 12h</span><h3 class="mt-2">文字下半 + 表格前半</h3>
    <p class="small">引用体系是本周核心；表格 L1—L3。引入真题讲解第 01—02 套跟做。</p>
    <div class="small text-muted">产出：引用体系操作卡</div></div></div>
  <div class="col-md-6 col-lg-3"><div class="catcard h-100"><span class="chip chip-accent">W3 · 12h</span><h3 class="mt-2">表格下半 + 演示</h3>
    <p class="small">函数第二组、透视表、演示 L1—L5。第 04—06 套限时 40 分钟做。</p>
    <div class="small text-muted">产出：演示考点 → 操作路径对照表</div></div></div>
  <div class="col-md-6 col-lg-3"><div class="catcard h-100"><span class="chip chip-accent">W4 · 12h</span><h3 class="mt-2">查漏 + 单选 + 全真</h3>
    <p class="small">公共基础 10 分集中背；<strong>2 套 120 分钟全真卷</strong>；必须用教育考试专用版。</p>
    <div class="small text-muted">产出：错题本 + 时间分配节奏</div></div></div>
</div>
<div class="callout callout-blue"><strong>时间分配训练：</strong>单选 15 分钟 + 文字 35 分钟 + 表格 40 分钟 + 演示 25 分钟 + 检查 5 分钟，至少完整跑 2 次。考前 1 天只看自己的速查表与错题本，不碰新知识点。</div>'''

    mapping = '''<p>依据 2025 年版大纲四大板块逐条映射主资源、补充资源与覆盖度结论，完整 29 条对照表见下方 Markdown 原文。这里给出结论：</p>
<div class="table-responsive"><table class="table table-hover"><thead><tr><th>板块</th><th>覆盖情况</th><th>主资源</th></tr></thead><tbody>
<tr><td>一、综合应用基础</td><td><span class="level-pill high">基本充分</span>，仅 PDF 处理相对薄弱</td><td>官方通关课 1-2、1-3</td></tr>
<tr><td>二、文字文档 9 条</td><td><span class="level-pill high">充分</span>，引用体系需多资源叠加</td><td>通关课 2-x + 文字新手课 + 真题讲解</td></tr>
<tr><td>三、数据表格 9 条</td><td><span class="level-pill high">充分</span>，模拟分析略弱</td><td>通关课 3-x~5-x + 透视表专项</td></tr>
<tr><td>四、演示文稿 6 条</td><td><span class="level-pill high">充分</span>，但新手课有 3 处缺口</td><td>通关课 6-x + SmartArt 图文 + 真题讲解</td></tr>
</tbody></table></div>
<div class="callout"><strong>两个真实缺口：</strong>① PDF 处理只有通关课 1-3 约 13 分钟覆盖，实际考查强度低于大纲权重，了解即可；② 数组公式、模拟分析大纲明文列出，但所有免费视频课均未系统讲解，遇真题再针对性查。</div>'''

    boundary = '''<div class="row g-3">
  <div class="col-md-6"><div class="catcard h-100"><h3>明确超纲 · 完全跳过</h3>
    <ul class="small mb-0"><li>WPS 宏 / VBA / JS 编程</li><li>WPS AI / 智能美化 / AI 排版</li>
    <li>多维表格 / WPS 团队 / 协同办公进阶</li><li>WPS 组件（PDF 组件、DTP、邮件组件）完整功能</li>
    <li>打印驱动与打印机硬件设置</li><li>Python / JS 宏 / 插件开发</li></ul></div></div>
  <div class="col-md-6"><div class="catcard h-100"><h3>看似超纲 · 实际必考</h3>
    <ul class="small mb-0"><li>邮件合并（大纲二.7）</li><li>数据透视表（大纲三.6，最高频被低估）</li>
    <li>文档网格「每页 33 行」（样题原题）</li><li>多级编号高级用法、交叉引用 + F9</li>
    <li>SmartArt 智能图形（大纲四.3）</li><li>图片柔化边缘 / 置于底层、自定义放映方案</li></ul></div></div>
</div>
<div class="callout callout-blue mt-3"><strong>两个反向提醒：</strong>SmartArt 是考纲内的老功能，与「WPS AI 排版」是两回事，不要因排斥 AI 而漏掉；另外要确认资料标的是<strong>二级</strong>还是一级——二级考样式体系、引用体系、透视表、母版、动画，一级完全不考。</div>'''

    sections = [('difficulty', '样题难度基准', diff), ('order', '知识点分级学习顺序', order),
                ('plan', '4 周 48 小时计划', plan), ('mapping', '考纲条款映射', mapping),
                ('boundary', '超纲边界与易误判考点', boundary)]
    sec_html = ''.join('''<section id="{aid}" class="prose mb-4">
  <h2>{title}</h2>{content}
  <p class="mt-3 mb-0"><a class="src-link" href="{p}{file}">查看完整资料原文（Markdown）→</a></p>
</section>'''.format(aid=a, title=esc(t), content=c, p=p, file=f)
        for (a, t, f), (_, _, c) in zip(GUIDE_DOCS, sections))

    body = '''<div class="page-head"><div class="container">
  <h1>备考指南</h1>
  <p>把调研报告里的「怎么学、按什么顺序学、哪些不用学」单独成页，与资源清单分开，避免在目录页堆砌长文。</p>
</div></div>
<div class="container">
  <div class="row">
    <div class="col-lg-3 mb-4"><div class="info-card anchor-nav"><h5>本页目录</h5>
      <div class="list-group list-group-flush">{anchors}</div>
      <hr><h5>资料原文</h5><ul class="small ps-3 mb-0">{doc_links}</ul>
      <hr><p class="small text-muted mb-0">所有资料原文同时保存在站点 <code>content/</code> 目录，随站点一同部署。</p>
    </div></div>
    <div class="col-lg-9">{sections}</div>
  </div>
</div>'''.format(anchors=anchors, doc_links=doc_links, sections=sec_html)
    write('guide.html', page('备考指南', 'WPS 二级备考的学习顺序、四周计划、考纲映射、样题难度基准与超纲边界。', 0, 'guide', body))


# ---------------------------------------------------------------- 关于页
def gen_about():
    p = ''
    cat_rows = ''.join('<tr><td><a href="category/%s.html">%s</a></td><td>%s</td><td class="text-center">%d</td></tr>' % (
        c['id'], esc(c['name']), esc(c['desc']), sum(1 for r in RESOURCES if r['category'] == c['id']))
        for c in CATEGORIES)
    limits = [
        ('完全免费、无门槛', '官方大纲 / 样题 PDF、WPS 365 官方博客图文、NCRE 官网、本站全部内容', '可自由下载、打印；本站已留存 2 份 PDF 站内副本'),
        ('公开免费但未逐项核验', 'WPS 学堂 4 套系统课 + 透视表专题', '课程目录与时长已核验，未逐节确认视频可用性与是否全部免费'),
        ('免费但需账号 / 邀请码', 'WPS 教学平台、B 站高清与倍速、Gitee 附件下载', 'WPS 教学平台需高校邀请码，个人无法自助开通'),
        ('免费但内容滞后', 'GitHub / Gitee 的 ncre 题库', '最后提交 2022-04，只有选择题、无操作题素材，不可作主线'),
        ('在线公开资源', '在线备考站、模拟考试系统、WPS 官网', '公开免费、无需账号；站点只给出线上正式网址，不复制分发原站文件'),
        ('未核验、不推荐', '虎课网、知乎知学堂部分课程', '虎课网返回身份验证，无法确认免费状态，仅作检索记录保留'),
    ]
    limit_rows = ''.join('<tr><td><strong>%s</strong></td><td>%s</td><td>%s</td></tr>' % (
        esc(a), esc(b), esc(c)) for a, b, c in limits)

    body = '''<div class="page-head"><div class="container">
  <h1>关于与说明</h1>
  <p>数据来源、收录标准、免费限制总览、模板与许可证，以及静态资源站内化清单。</p>
</div></div>
<div class="container"><div class="prose">
  <h2>1. 站点定位与数据范围</h2>
  <p>本站把 2026-11-11 完成的《WPS 二级备考资源调研》中<strong>实际核验过的公开免费资源</strong>整理为可检索的静态索引，
  面向全国计算机等级考试（NCRE）二级 <strong>WPS Office 高级应用与设计</strong>（科目代码 67）。
  共 {nr} 条资源、{nc} 个语义分类、{nu} 个外部获取入口，另含 2 份已随站点部署的官方 PDF。</p>
  <p>收录标准：① 获取本身不需要付费；② 链接于核验当日实际访问；③ 能说清用途与限制。
  <strong>未收录</strong>付费网盘题库、纸质出版物、无法核验免费状态的课程。虎课网等未核验来源仅作为「已检索但未采纳」记录保留，不计入推荐。</p>

  <h2>2. 资源分布</h2>
  <div class="table-responsive"><table class="table table-hover align-middle">
  <thead><tr><th>分类</th><th>收录内容</th><th class="text-center">条数</th></tr></thead><tbody>{cat_rows}</tbody></table></div>

  <h2>3. 免费限制总览</h2>
  <p>「免费」不等于「无门槛」。下表按限制类型汇总，每条资源详情页还有单独说明。</p>
  <div class="table-responsive"><table class="table table-hover align-middle">
  <thead><tr><th>限制类型</th><th>涉及资源</th><th>具体说明</th></tr></thead><tbody>{limit_rows}</tbody></table></div>

  <h2>4. 三维评价方法</h2>
  <p>每条资源按三个维度判断定位，避免把真题课当入门课、把职场课当备考课：</p>
  <ul><li><strong>零基础友好度</strong>：是否从界面起步、颗粒度是否够细。</li>
  <li><strong>图文结合度</strong>：是否有图文技巧、练习文档或分 P 文字目录可脱离视频复看。</li>
  <li><strong>备考适配度</strong>：与 2025 年版考纲的映射精度、是否命中官方样题的真实难度。</li></ul>
  <div class="callout">如果只选三样：官方《计算机二级 高效通关课》（教「有哪些」）+ 大猫《WPS计算机二级真题讲解》（教「怎么做」）+ 官方样题 PDF（定「考到什么颗粒度」）。三门新手入门课当字典随时回查，不要从头到尾刷。</div>

  <h2>5. 模板与许可证</h2>
  <p>页面框架基于 <a href="https://github.com/StartBootstrap/startbootstrap-blog-home" target="_blank" rel="noopener noreferrer">Start Bootstrap · Blog Home</a>
  （Bootstrap 5.2.3，<strong>MIT License</strong>，Copyright 2013-2023 Start Bootstrap LLC）。
  模板原文件保存在 <code>assets/template/</code>，许可证全文见 <a href="LICENSE-TEMPLATE.txt">LICENSE-TEMPLATE.txt</a>，
  改造清单见 <a href="TEMPLATE.md">TEMPLATE.md</a>。</p>
  <p>改造内容：把单页博客列表重构为「首页 / 分类总览 / 6 个分类页 / {nr} 个详情页 / 检索页 / 备考指南 / 关于页」的多页站点；
  替换导航为分类下拉 + 全站搜索；新增资源卡片、评分、标签、筛选与客户端全文检索；新增 <code>assets/css/site.css</code> 定制样式层。</p>

  <h2>6. 静态资源站内化与外链政策</h2>
  <ul>
    <li><strong>CSS / JS 全部随站点部署：</strong>模板 <code>styles.css</code>（内含 Bootstrap 5.2.3）、Bootstrap <code>bundle.min.js</code>、模板 <code>scripts.js</code>、站点 <code>site.css</code> / <code>site.js</code>、检索数据 <code>resources.js</code> 均为站内文件，不使用任何 CDN。</li>
    <li><strong>图片全部站内：</strong>6 个分类线性图标与首页装饰图由站点自绘，以<strong>内联 SVG</strong> 嵌入页面（同时保留 <code>assets/img/</code> 独立 SVG 文件），favicon 来自模板站内文件；原模板的 <code>dummyimage.com</code> 占位图已全部移除。图标内联可规避部分静态托管服务把 <code>.svg</code> 返回成非标准 MIME 导致的破图，页面不引用任何外部图片。</li>
    <li><strong>字体使用系统字体栈</strong>，不加载外部字体。</li>
    <li><strong>官方 PDF 站内副本：</strong>考纲与样题已存入 <code>assets/files/</code>，即使原站链接失效也可查看。</li>
    <li><strong>内容外链为资源本身：</strong>详情页的「获取方式」链接指向原资源站点，属于内容而非页面依赖，均标注完整 URL 并在新窗口打开，页面加载不依赖它们。</li>
  </ul>

  <h2>7. 目录结构</h2>
  <pre><code>aheelv/wps_2_test_learn/free/
├─ index.html / categories.html / search.html / guide.html / about.html
├─ category/          6 个分类列表页
├─ resource/          {nr} 个资源详情页
├─ assets/
│  ├─ template/       模板原始文件（未改动，MIT）
│  ├─ vendor/         站内 Bootstrap JS
│  ├─ css/ js/ img/   站点定制样式、交互脚本、站内 SVG
│  └─ files/          2 份官方 PDF 站内副本
├─ data/              resources.json / categories.json / resources.js（内容数据）
├─ content/           语义化整理文档（Markdown）
├─ tools/build.py     静态页面生成器
└─ README.md / TEMPLATE.md / LICENSE-TEMPLATE.txt</code></pre>
  <p class="small text-muted">站点代码（assets/ 与根目录 HTML）与资源内容（data/、content/、assets/files/）分层存放；
  新增或修改资源只需编辑 <code>data/resources.json</code> 后运行 <code>python tools/build.py</code>，页面与检索数据会同步重建。</p>
  <p class="small text-muted mb-0">本站部署于 GitHub Pages 子路径 <code>/wps_2_test_learn/free/</code>，正式入口为
  <a href="https://aheelv.github.io/wps_2_test_learn/free/" target="_blank" rel="noopener noreferrer">https://aheelv.github.io/wps_2_test_learn/free/</a>；
  全部站内链接均为相对路径，因此在该子路径下页面、样式、脚本、附件与检索功能均可直接使用。</p>

  <h2>8. 免责声明</h2>
  <p class="mb-0">资料版权归各原作者与发布方所有，本站仅作索引、评价与学习规划，不托管第三方付费内容，也不代表任何官方机构。
  链接有效性以 2026-11-12 复核结果为准；考试政策、大纲与平台开通方式可能变化，请以中国教育考试网及所在学校通知为准。</p>
</div></div>'''.format(nr=len(RESOURCES), nc=len(CATEGORIES), nu=URL_COUNT,
                       cat_rows=cat_rows, limit_rows=limit_rows)
    write('about.html', page('关于与说明', '数据来源、免费限制总览、模板许可证与静态资源站内化说明。', 0, 'about', body))


# ---------------------------------------------------------------- content 文档
def gen_content_docs():
    lines = ['# 资源内容层说明', '',
             '本目录存放按语义整理后的资料原文（Markdown），与站点代码分离。',
             '页面只呈现结构化摘要与导航，完整长文放在这里，避免内容堆砌。', '',
             '## 文件清单', '',
             '| 文件 | 内容 |', '|---|---|']
    for _, t, f in GUIDE_DOCS:
        lines.append('| `%s` | %s |' % (os.path.basename(f), t))
    lines += ['| `分类-*.md` | 各分类的完整资源清单（由生成器输出） |',
              '| `资源清单-全量.md` | 全站资源清单，含用途、获取方式与免费限制 |',
              '| `免费限制说明.md` | 按限制类型汇总的免费边界 |', '']
    for c in CATEGORIES:
        lines.append('## %s' % c['name'])
        lines.append('')
        lines.append(c['desc'])
        lines.append('')
        lines.append('资源原文见 `分类-%s.md`；对应站点页面 `category/%s.html`。' % (c['id'], c['id']))
        lines.append('')
    write('content/README.md', '\n'.join(lines) + '\n')

    for c in CATEGORIES:
        rows = [r for r in RESOURCES if r['category'] == c['id']]
        out = ['# %s · 资源清单' % c['name'], '', '> %s' % c['desc'], '',
               '> 适用场景：%s' % c['use'], '',
               '共 %d 条。站点页面：`category/%s.html`。' % (len(rows), c['id']), '']
        for i, r in enumerate(rows, 1):
            out += ['## %d. %s' % (i, r['name']), '',
                    '- **类型**：%s ｜ **推荐度**：%s ｜ **零基础**：%s ｜ **备考适配**：%s'
                    % (r['kind'], '★' * r['rating'] + '☆' * (5 - r['rating']), r['zero'], r['exam']),
                    '- **用途**：%s' % r['summary'],
                    '- **详细说明**：%s' % r['purpose'],
                    '- **获取方式**：%s' % r['access'],
                    '- **免费限制**：%s' % r['free'],
                    '- **考纲映射**：%s' % ('、'.join(r['syllabus']) or '不直接对应'),
                    '- **使用提醒**：%s' % r['caveat'],
                    '- **标签**：%s' % '、'.join(r['tags'])]
            if r['links']:
                out.append('- **链接**：')
                out += ['  - %s — %s' % (l['label'],
                        l['url'] if l['url'].startswith(('http://', 'https://')) else '../' + l['url'])
                        for l in r['links']]
            if r['asset']:
                out.append('- **站内附件**：`%s`' % r['asset'])
            out += ['- **详情页**：`resource/%s.html`' % r['id'], '']
        write('content/分类-%s.md' % c['name'], '\n'.join(out) + '\n')

    out = ['# 全站资源清单', '',
           '> 生成日期：%s ｜ 共 %d 条资源、%d 个分类、%d 个外部获取入口。'
           % (TODAY, len(RESOURCES), len(CATEGORIES), URL_COUNT), '',
           '## 按分类速览', '', '| # | 名称 | 分类 | 类型 | 推荐度 | 免费限制 | 详情页 |',
           '|---:|---|---|---|---:|---|---|']
    for i, r in enumerate(RESOURCES, 1):
        out.append('| %d | %s | %s | %s | %s | %s | [详情](%s) |' % (
            i, r['name'], BY_CAT[r['category']]['name'], r['kind'],
            '★' * r['rating'], r['free'].replace('|', '\\|'),
            '../resource/%s.html' % r['id']))
    out += ['', '## 完整字段说明', '',
            '每条资源的用途、获取方式、免费限制、考纲映射、使用提醒与全部链接，'
            '见 `分类-*.md` 及 `data/resources.json`。', '']
    write('content/资源清单-全量.md', '\n'.join(out) + '\n')

    limits = {}
    for r in RESOURCES:
        key = ('需账号 / 邀请码' if '邀请码' in r['free'] or '登录' in r['free'] else
               '内容滞后' if '滞后' in r['free'] or '2022' in r['free'] else
               '在线公开资源' if '在线' in r['free'] or 'GitHub Pages' in r['free'] else
               '未核验' if '未' in r['free'] else '公开免费')
        limits.setdefault(key, []).append(r['name'])
    out = ['# 免费限制说明', '',
           '> 本站只收录获取本身不需要付费的资源，但「免费」不等于「无门槛、无时效、无账号要求」。', '',
           '## 按限制类型分组', '']
    for k, v in limits.items():
        out += ['### %s（%d 条）' % (k, len(v)), '']
        out += ['- %s' % n for n in v]
        out.append('')
    out += ['## 逐条说明', '', '| 资源 | 免费限制 |', '|---|---|']
    for r in RESOURCES:
        out.append('| [%s](../resource/%s.html) | %s |' % (r['name'], r['id'], r['free'].replace('|', '\\|')))
    write('content/免费限制说明.md', '\n'.join(out) + '\n')


# ---------------------------------------------------------------- 交付文档
def gen_readme():
    cat_list = '\n'.join('| `%s` | %s | %d |' % (
        c['id'], c['name'], sum(1 for r in RESOURCES if r['category'] == c['id'])) for c in CATEGORIES)
    body = '''# WPS 二级免费资源站

面向 **NCRE 二级 WPS Office 高级应用与设计（科目代码 67）** 的免费备考资源索引站。
把调研到的公开免费资料按语义归类，标注名称、用途、获取方式与免费限制，做成一个**纯静态、无外部依赖、可直接打开**的网站。

> 资料核验时间：2026-11-11 ｜ 生成日期：{today} ｜ 共 {nr} 条资源、{nc} 个分类、{nu} 个外部获取入口、2 份官方 PDF 站内副本。

---

## 一、部署与访问

**正式入口**：<https://aheelv.github.io/wps_2_test_learn/free/>

本站挂载在 GitHub 仓库 `aheelv/wps_2_test_learn` 的 `free/` 子目录，由该仓库 `main` 分支根目录的 GitHub Pages 发布。
仓库其他目录（原在线备考站的页面、题库、练习素材、课件等）保持不变，本次部署只新增 `free/` 一个目录。

本站为纯静态站点，无需构建步骤、后端或接口调用；整体放到任意静态托管的任意子路径下即可访问。

- **子路径适配**：所有页面链接、CSS / JS、图标、PDF 与检索数据均为站内相对路径。根目录页面引用 `assets/…`，
  `category/` 与 `resource/` 下的页面引用 `../assets/…`，检索结果中的详情页链路由 `data-base`
  （根页面为 `''`、二级页面为 `'../'`）按层级拼接，因此在 `/wps_2_test_learn/free/` 下全部解析正确；
  页面不硬编码域名、端口、回环地址、局域网地址或文件系统绝对路径，迁移到别的子路径也无需改代码。
- **入口页**：`free/index.html`，访问目录 `…/free/` 时由静态托管自动定位到该文件。
- 页面加载不发起 `fetch` / XHR 请求，检索与筛选在浏览器端即时完成。
- 详情页的「获取方式」链接指向各资源的线上正式网址，属于内容本身，均在新窗口打开，不参与页面加载；
  其中指向同仓库根目录备考站页面的链接仍是绝对正式网址，不会因本站位于 `free/` 子目录而失效。

### 重新生成页面

```bash
python tools/build.py
```

修改 `data/resources.json` 或 `data/categories.json` 后运行该命令，
即可重建全部 HTML 页面、`data/resources.js`、站内 SVG 图标与 `content/` 下的清单文档。

---

## 二、目录结构

```
aheelv/wps_2_test_learn/free/        ← 本站在仓库中的部署目录
├── index.html               首页（概览、入门路径、分类入口、精选资源）
├── categories.html          分类总览（6 类 + 分类逻辑对照）
├── search.html              全站检索（关键词 / 分类 / 推荐度，客户端全文匹配）
├── guide.html               备考指南（难度基准、学习顺序、四周计划、考纲映射、超纲边界）
├── about.html               关于与说明（数据来源、免费限制、许可证、站内化清单）
├── category/                6 个分类列表页
│   ├── docs.html            文档教程
│   ├── courses.html         视频课程
│   ├── opensource.html      开源项目
│   ├── templates.html       模板素材
│   ├── tools.html           工具服务
│   └── reference.html       设计参考
├── resource/                {nr} 个资源详情页（每条含用途/获取方式/免费限制/考纲映射/相关资源）
├── assets/                  站点代码层
│   ├── template/            模板原始文件（未改动）：styles.css / scripts.js / favicon.ico
│   ├── vendor/              站内 bootstrap.bundle.min.js
│   ├── css/site.css         站点定制样式（改造层）
│   ├── js/site.js           检索与筛选逻辑
│   ├── img/                 站内 SVG 图标（6 个分类图标 + 首页装饰图）
│   └── files/               官方大纲、官方样题 2 份 PDF 站内副本
├── data/                    资源内容层（结构化数据）
│   ├── resources.json       全部资源的结构化字段（唯一维护入口）
│   ├── categories.json      分类元数据
│   └── resources.js         由生成器输出，供浏览器端检索使用（内联数据，无网络请求）
├── content/                 资源内容层（语义化 Markdown 文档）
│   ├── README.md            内容层说明
│   ├── 分类-*.md            6 份分类完整清单
│   ├── 考纲映射.md          大纲 29 条 → 资源覆盖对照
│   ├── 样题难度基准.md      三大模块真实考点颗粒度
│   ├── 学习顺序.md          L0—L6 知识点分级
│   ├── 四周计划.md          4 周 48 小时计划
│   ├── 超纲边界.md          超纲 / 易误判清单
│   ├── 资源清单-全量.md     全站资源总表
│   └── 免费限制说明.md      按限制类型汇总
├── tools/build.py           静态页面生成器
├── README.md                本文件
├── TEMPLATE.md              模板来源、许可证与改造清单
└── LICENSE-TEMPLATE.txt     模板 MIT 许可证全文
```

**分层原则**：`assets/` 与根目录 HTML 是站点代码；`data/`、`content/`、`assets/files/` 是资源内容。
两者互不混杂，新增资源只改数据文件再重新生成即可。

---

## 三、页面与链接互通

| 入口 | 可到达 |
|---|---|
| 全站导航 | 首页、分类总览、分类下拉（6 类直达）、备考指南、全站检索、关于 |
| 首页 | 6 个分类页、6 条精选详情、入门路径 3 条详情、备考指南、检索页 |
| 分类总览 | 6 个分类页 + 各分类前 4 条详情 |
| 分类列表页 | 该分类全部详情、标签/评分/关键词筛选、跳转到检索页并预选该分类 |
| 资源详情页 | 面包屑回首页/分类总览/分类页、相关资源详情、全站检索、备考指南、线上获取链接、站内 PDF 副本 |
| 检索页 | 任意资源详情；支持 URL 参数 `?q=关键词&cat=分类` |

所有内部链接均为相对路径，部署后随正式域名自动解析，在 `/wps_2_test_learn/free/` 子路径下同样成立；外部链接统一 `target="_blank" rel="noopener noreferrer"`，不参与页面加载。

---

## 四、资源清单概览

| 分类 ID | 分类名称 | 条数 |
|---|---|---:|
{cat_list}
| **合计** | **{nc} 类** | **{nr}** |

完整清单（含每条的用途、获取方式、免费限制与链接）见：

- `content/资源清单-全量.md`（全站总表）
- `content/分类-*.md`（按类展开的完整字段）
- `content/免费限制说明.md`（免费边界）
- `data/resources.json`（机器可读的结构化数据）

**外部获取入口共 {nu} 个**，覆盖 WPS 官方学堂 / WPS 365 官方博客 / 中国教育考试网 / 哔哩哔哩 / CSDN / GitHub / Gitee / 知乎等来源；
另有 2 份官方 PDF 已随站点部署，其余资源均通过线上正式网址访问。

### 优先看的 6 条

1. 官方《样题及参考答案》PDF（定颗粒度）
2. 官方《考试大纲（2025 年版）》PDF（定范围）
3. WPS 官方《计算机二级 高效通关课》35 节（教有哪些）
4. 大猫《WPS计算机二级真题讲解》（教怎么做）
5. 在线备考站 `wps_2_test_learn`（考纲对照 + 课件）
6. 网页版 120 分钟计时评分模拟考试系统（全真演练）

---

## 五、模板与许可证

| 项 | 内容 |
|---|---|
| 模板名称 | **Start Bootstrap — Blog Home** |
| 仓库地址 | <https://github.com/StartBootstrap/startbootstrap-blog-home> |
| 版本 / 技术 | Bootstrap 5.2.3（模板 `dist/` 构建产物） |
| 许可证 | **MIT License**，Copyright (c) 2013-2023 Start Bootstrap LLC |
| 许可证全文 | `LICENSE-TEMPLATE.txt` |
| 改造清单 | `TEMPLATE.md` |

改造要点：单页博客列表 → 多页资源目录站；新增分类下拉导航、全站搜索、资源卡片、评分/标签体系、
分类页筛选、客户端全文检索；新增 `site.css` 定制层；移除全部 CDN 与占位外链图片。

---

## 六、质量与部署说明

- **子路径部署**：站点整体位于 `/wps_2_test_learn/free/`，全部页面、PDF、Markdown 清单与静态资源通过相对路径互连；仓库根目录的原有页面未被改写，也不作为相对路径依赖。
- **响应式**：Bootstrap 5 栅格 + 断点补强，桌面 / 平板 / 手机自适应，导航自动折叠。
- **静态资源站内化**：CSS、JS、字体（系统字体栈）、图标、favicon、PDF 全部随站点部署；页面加载不请求任何外部资源。分类图标与首页装饰图以内联 SVG 呈现（`assets/img/` 另留独立文件），不受静态托管服务对 `.svg` 的 MIME 设置影响。
- **无需构建**：交付物即最终 HTML，部署即可访问；`tools/build.py` 仅用于后续维护。
- **渐进增强**：分类页与详情页内容均为静态 HTML，关闭 JavaScript 仍可浏览与跳转；检索与筛选为增强功能。
- **外链政策**：详情页的获取链接是内容本身，均标注完整 URL 并在新窗口打开，失效不影响页面渲染；关键官方 PDF 已留站内副本。
- **外链核验**：所有外部地址已于 2026-11-12 复核，均为官方或原发布方的正式网址；CSDN、GitHub 等站点对自动化探测有反爬或网络限制，浏览器访问正常；GitHub 题库另附 Gitee 镜像作为稳定入口。
- **数据一致性**：`data/resources.js`、`content/分类-*.md`、全部详情页均由同一份 `resources.json` 生成。

---

## 七、免责声明

资料版权归各原作者与发布方所有，本站仅作索引、评价与学习规划，不托管第三方付费内容，也不代表任何官方机构。
链接有效性以 2026-11-12 复核结果为准；考试政策、大纲与平台开通方式可能变化，请以中国教育考试网及所在学校通知为准。
'''.format(today=TODAY, nr=len(RESOURCES), nc=len(CATEGORIES), nu=URL_COUNT, cat_list=cat_list)
    write('README.md', body)


def gen_template_md():
    body = '''# 模板来源、许可证与改造清单

## 模板信息

| 项 | 内容 |
|---|---|
| 模板名称 | **Start Bootstrap — Blog Home** |
| 仓库地址 | <https://github.com/StartBootstrap/startbootstrap-blog-home> |
| 官方介绍 | <https://startbootstrap.com/template/blog-home> |
| 获取分支 | `master`，取 `dist/` 构建产物 |
| 技术栈 | HTML + Bootstrap 5.2.3 + 原生 JS（无构建依赖） |
| 许可证 | **MIT License** |
| 版权声明 | Copyright (c) 2013-2023 Start Bootstrap LLC |
| 许可证全文 | 本目录 `LICENSE-TEMPLATE.txt`，以及 `assets/template/` 内保留的原始文件 |

模板所用 Bootstrap 5.2.3 同为 MIT 许可（Copyright 2011-2022 The Bootstrap Authors），
其压缩版 JS 已随站点部署至 `assets/vendor/bootstrap.bundle.min.js`，文件头保留原始版权注释。

## 下载方式

GitHub 主站直连不稳定，本次通过 GitHub API 与 `raw.githubusercontent.com` 逐文件获取：

```
https://raw.githubusercontent.com/StartBootstrap/startbootstrap-blog-home/master/dist/css/styles.css
https://raw.githubusercontent.com/StartBootstrap/startbootstrap-blog-home/master/dist/js/scripts.js
https://raw.githubusercontent.com/StartBootstrap/startbootstrap-blog-home/master/dist/assets/favicon.ico
https://raw.githubusercontent.com/StartBootstrap/startbootstrap-blog-home/master/dist/index.html
https://raw.githubusercontent.com/StartBootstrap/startbootstrap-blog-home/master/LICENSE
```

实际复用并保持未改动的原始文件保存在 `assets/template/`：

- `styles.css` — 模板核心 CSS，内含 Bootstrap 5.2.3
- `scripts.js` — 模板核心 JS（版本与许可注释）
- `favicon.ico` — 站点图标

模板原始首页与说明文件仅含示例占位图、社交链接与徽章外链，不属于站点运行所需，已从交付物中移除；
如需核对模板结构，请访问上方官方仓库地址。

## 改造清单

| 原始模板 | 本站改造 |
|---|---|
| 单个 `index.html` 博客首页 | 首页 / 分类总览 / 6 个分类页 / {nr} 个详情页 / 检索页 / 备考指南 / 关于页 |
| 顶部 4 个静态导航项 | 分类下拉导航（6 类直达）+ 全站搜索框 + 当前页高亮 |
| 模板示例外链占位图 | 全部移除，替换为站点自绘的内联 SVG 图标（另在 `assets/img/` 保留独立 SVG 文件）与 CSS 渐变装饰 |
| CDN 引入 `bootstrap.bundle.min.js` | 下载到 `assets/vendor/` 站内引用 |
| 博客文章卡片 | 资源卡片：分类色条、推荐度星级、标签、三维评价、详情链接 |
| 侧栏「Search / Categories」静态占位 | 全站检索页 + 分类页的关键词 / 标签 / 推荐度筛选（客户端实时过滤） |
| 固定假内容分页 | 由 `data/resources.json` 驱动的语义化分类与相关资源链接 |
| 深灰导航 + 浅色正文 | 深蓝品牌渐变导航、Hero 区、统一卡片与说明页排版 |
| 英文占位文案 | 全中文内容，按「文档教程 / 视频课程 / 开源项目 / 模板素材 / 工具服务 / 设计参考」归类 |

## 新增文件（非模板内容）

- `assets/css/site.css` — 定制样式层，不修改模板 `styles.css`
- `assets/js/site.js` — 客户端检索与筛选
- `assets/img/*.svg` — 6 个分类图标 + 首页装饰图（站点自绘）
- `assets/vendor/bootstrap.bundle.min.js` — 站内的 Bootstrap JS
- `assets/files/*.pdf` — 官方大纲与样题的站内副本
- `data/` `content/` `tools/` — 资源内容与生成脚本
- 根目录全部业务页面与说明文档

## MIT 许可要求说明

依 MIT 许可证，本站在交付物中保留了模板原始版权声明与许可全文（`LICENSE-TEMPLATE.txt`），
并在页脚与「关于」页注明模板名称、仓库地址与许可证。模板原始文件以未改动形式保存于 `assets/template/`，
便于核对。本站新增内容与整理文档不受模板许可限制。
'''.format(nr=len(RESOURCES))
    write('TEMPLATE.md', body)


def main():
    gen_icons()
    gen_data_js()
    gen_index()
    gen_categories()
    for c in CATEGORIES:
        gen_category(c)
    for r in RESOURCES:
        gen_resource(r)
    gen_search()
    gen_guide()
    gen_about()
    gen_content_docs()
    gen_readme()
    gen_template_md()
    print('Generated: %d resource pages, %d category pages, 5 root pages, %d content docs.' % (
        len(RESOURCES), len(CATEGORIES), len(GUIDE_DOCS) + 4))
    print('Output root: %s' % ROOT)


if __name__ == '__main__':
    main()
