# -*- coding: utf-8 -*-
"""把 11-6/ 的 WPS 理论考试部分整合进站内学习路径。

产出：
  理论考试.html            栏目主页（导学 / 分册 / 学习路径 / 归属说明）
  理论题库/index.html      离线刷题应用（由 11-6/index.html 生成 + 一致站点条）
  理论题库/README.txt      构建关系说明
  tools/theory_integration.json  归属说明（机器可读）

11-6/ 保留题库源文件（quiz_data.json）与构建脚本（build/），不作为站内入口；
线上只暴露「理论考试 → 理论题库」两级，避免同名内容两处可点、口径漂移。

用法：python tools/site_theory.py
"""
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CFG = json.load(open(ROOT / 'tools' / 'site_config.json', encoding='utf-8'))
TH = CFG['theory']
import site_nav

SRC = ROOT / TH['app_source']
DATA = ROOT / TH['data_source']
OUTDIR = ROOT / '理论题库'
APP = OUTDIR / 'index.html'
HUB = ROOT / '理论考试.html'


def sections():
    d = json.load(open(DATA, encoding='utf-8'))
    return [(s['name'], len(s['questions'])) for s in d]


def build_app():
    OUTDIR.mkdir(parents=True, exist_ok=True)
    s = SRC.read_text(encoding='utf-8')
    assert 'const DATA = ' in s, '题库应用源缺少内嵌数据'
    assert not re.search(r'<(?:link|script)[^>]+(?:src|href)="https?://', s), '应用不得依赖外部资源'
    # 标题与站点条
    s = re.sub(r'<title>.*?</title>',
               '<title>理论题库 · 单项选择题 781 题 · 大连财经学院 WPS 二级学习中心</title>',
               s, count=1, flags=re.S)
    bar = site_nav.site_bar('../', '理论题库（理论考试）')
    hit = site_nav.replace_marked(s, site_nav.BAR_BEGIN, site_nav.BAR_END, bar)
    if hit is not None:
        s = hit
    else:
        s = s.replace('<body>', '<body>\n' + bar, 1)
    APP.write_text(s, encoding='utf-8')
    (OUTDIR / 'README.txt').write_text(
        '理论题库（离线单文件刷题应用）\n'
        '================================\n'
        '本目录由 tools/site_theory.py 生成，请勿手工编辑 index.html。\n'
        '  源文件：11-6/index.html（由 11-6/build/make_page.py 注入题库生成）\n'
        '  题库数据：11-6/quiz_data.json（2 分册 / 781 题）\n'
        '  栏目主页：../理论考试.html\n'
        '  配置来源：tools/site_config.json\n'
        '生成动作：替换页面标题 + 插入与主站一致的「站点导航」条；应用本体不外链任何资源，\n'
        '          可整页离线使用，进度保存在浏览器 localStorage。\n'
        '重建顺序：python 11-6/build/make_page.py → python tools/site_theory.py → python tools/site_nav.py\n',
        encoding='utf-8')
    return len(s)


def build_hub():
    secs = sections()
    total = sum(n for _, n in secs)
    rows = ''.join(
        '<tr><td><b>%s</b></td><td class="num"><b>%d</b> 题</td><td class="small">%s</td>'
        '<td class="small">%s</td></tr>' % (x['name'], x['count'], x['scope'], x['path_stage'])
        for x in TH['sections'])
    feats = ''.join('<span class="pill">%s</span>' % f for f in TH['features'])
    path = ''.join('<div class="pstep" style="--mc:var(--m1)"><div class="w">%s</div>'
                   '<h4>%s</h4><p>%s</p></div>' % (x['stage'], x['name'], x['text'])
                   for x in CFG['learning_path'])
    html = """<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>理论考试 · 单项选择题 781 题 · 学习中心</title>
<meta name="description" content="WPS 二级理论考试栏目：781 道单项选择题，基础知识 150 题 + 二级公共基础 631 题，对应单项选择题 20 分（含公共基础 10 分）；离线刷题、按 2025 大纲自学与错题复盘。">
<link rel="stylesheet" href="./assets/style.css">
<style>
  .pstep{padding:16px 14px;position:relative;border-top:3px solid var(--line)}
  .pstep .w{font-size:12px;font-weight:900;letter-spacing:.06em;color:var(--muted)}
  .pstep h4{margin:5px 0 5px;font-size:16px}
  .pstep p{font-size:12.5px;color:var(--muted);margin:0}
  .pstep::before{content:"";position:absolute;left:0;top:-8px;width:12px;height:12px;border-radius:50%;background:#fff;border:3px solid var(--mc,var(--brand))}
  .path5{display:grid;grid-template-columns:repeat(5,1fr);gap:0;margin-top:18px}
  @media(max-width:900px){.path5{grid-template-columns:1fr}.path5 .pstep{border-top:0;border-left:3px solid var(--line);padding-left:16px}}
  .bigbtn{display:inline-flex;align-items:center;gap:10px;background:var(--accent);color:#fff;
    font-weight:800;font-size:16px;border-radius:12px;padding:14px 26px;text-decoration:none}
  .bigbtn:hover{filter:brightness(1.08)}
</style></head><body>
<header class="topbar"><div class="wrap">
  <a class="brand" href="./index.html"><span class="logo">WPS</span><span>大连财经学院 · 计算机国家二级（WPS 类）<small>校内教学辅助资料 · 非官方</small></span></a>
  __NAV__
</div></header>
__SUBNAV__
<div class="noticebar"><div class="wrap"><span class="nb-ic">ⓘ</span><span><b>大连财经学院</b> 计算机国家二级考试（WPS 类）校内教学辅助资料 · <b>本站为非官方考试网站</b>，不提供报名、缴费、查分服务，不收集任何个人信息。理论题进度只保存在本机浏览器。</span></div></div>
<section class="hero"><div class="wrap">
  <div class="eyebrow">核心模块 ② / 与实操训练并列 · 对应 2025 年版考试大纲</div>
  <h1>理论考试：单项选择题 20 分<br><span style="font-size:.62em;font-weight:700;color:#ffd9a1">2 分册 781 题 · 按大纲自学 · 离线可刷</span></h1>
  <p class="sub">单选题 20 分（含公共基础知识 10 分）由<b>基础知识部分 150 题</b>与<b>二级公共基础部分 631 题</b>覆盖。题库是纯离线单文件应用，支持分类/状态筛选、练习、背题、模拟测试、答题卡、收藏与错题统计；进度只存本机，不上传任何数据。</p>
  <div class="flex mt2"><a class="btn accent" href="./理论题库/index.html">▶ 进入理论题库（离线刷题）</a>
  <a class="btn ghost" href="./考纲对照表.html">📋 按大纲查知识点</a>
  <a class="btn ghost" href="./实操训练.html">🖱 回到实操训练</a></div>
  <div class="hero-stats">
    <div class="hero-stat"><b>__TOTAL__</b><span>道单项选择题</span></div>
    <div class="hero-stat"><b>2</b><span>分册 · 基础 + 公共基础</span></div>
    <div class="hero-stat"><b>20</b><span>分 · 含公共基础 10 分</span></div>
    <div class="hero-stat"><b>28/28</b><span>2025 大纲条目覆盖</span></div>
    <div class="hero-stat"><b>离线</b><span>无需账号、无需联网</span></div>
  </div>
</div></section>
<main class="wrap">
  <section class="section-sm"><h2>一、栏目定位与入口</h2>
    <div class="grid g2"><div class="card"><h3>与「实操训练」并列的核心模块</h3>
      <p>考试 100 分 = 操作题 80 分 + 单项选择题 20 分。本站据此把 <a href="./实操训练.html"><b>实操训练（72 题）</b></a> 与 <b>理论考试（781 题）</b> 并列为两大核心模块，首页与主导航优先呈现；<a href="./考试介绍.html">考试说明</a>、<a href="./教学大纲.html">考试大纲</a>、课件与电子书等降为辅助资料，需要时再查。</p>
      <p class="mt1"><a class="bigbtn" href="./理论题库/index.html">打开离线题库 →</a></p></div>
      <div class="card"><h3>本栏目两级结构</h3>
        <ul class="clean"><li><b>第一级 · 栏目主页</b>（本页）：分册说明、学习路径对应、按大纲导学、范围边界与归属说明。</li>
        <li><b>第二级 · 离线题库</b>（<code>理论题库/index.html</code>）：781 题刷题应用，练习 / 背题 / 模拟测试、答题卡、收藏、错题、进度保存。</li>
        <li><b>构建源</b>（<code>11-6/</code>）：题库源数据与构建脚本，不对学生暴露入口。</li></ul>
        <p class="small muted mb0">命名、层级与入口与全站一致：栏目名「理论考试」，主导航第 3 项，与「实操训练」同级。</p></div></div></section>

  <section class="section-sm"><h2>二、题量与分册归属</h2>
    <div class="table-wrap"><table class="tbl"><thead><tr><th>分册</th><th class="num">题量</th><th>覆盖内容</th><th>对应学习路径</th></tr></thead>
    <tbody>__ROWS__</tbody></table></div>
    <p class="small muted mt1">合计 <b>__TOTAL__</b> 题，数据取自 <code>11-6/quiz_data.json</code>；应用内嵌同一份数据，离线打开即可作答。</p></section>

  <section class="section-sm"><h2>三、题库功能与练习方式</h2>
    <div class="card"><div class="pill-row">__FEATS__</div>
      <p class="small muted mt2 mb0">建议：第 1–2 次课用「练习模式」按分册推进；错题与收藏自动留痕；冲刺阶段切换「模拟测试」自测，再用状态筛选只刷未掌握 / 错题。进度保存在本机 localStorage，可导出 JSON 备份。</p></div></section>

  <section class="section-sm"><h2>四、与学习路径的对应</h2>
    <p class="lead">两条主线并行：每次课既有上机题，也有对应的理论题安排。</p>
    <div class="path5">__PATH__</div></section>

  <section class="section-sm"><h2>五、按大纲自学与范围边界</h2>
    <div class="grid g2"><div class="card"><h3>按大纲自学</h3>
      <p class="small">依据《NCRE 二级 WPS Office 高级应用与设计考试大纲（2025 年版）》与《二级公共基础知识考试大纲（2025 年版）》，全站已建立 <b>28 条官方考试内容 → 实操 72 题 + 理论 781 题</b> 的覆盖矩阵，28 / 28 条均有题目承载。</p>
      <p class="small mb0"><a href="./考纲对照表.html">考纲对照表 →</a> · <a href="./教学大纲.html">教学大纲 →</a> · <a href="./整站内容配置.html">整站内容配置 →</a></p></div>
      <div class="card"><h3>范围边界（重要）</h3>
        <p class="small">理论选择题按 2025 大纲<b>包含</b> PDF 阅读/批注/编辑/转换、WPS 在线办公概念、文档上云与共享协作等考点；这些属于<b>概念题范围</b>。</p>
        <p class="small mb0">而 <a href="./实操训练.html">实操训练</a> 的 72 道操作题严格限定在<b>离线 WPS Office 教育考试专用版</b>可用功能内，不调用云端、AI、插件、宏或需联网验证的外部动作。两者互不越界。</p></div></div>
    <div class="callout key mt2"><h4>核查结论</h4><p class="mb0">全站 225 个文件扫描：0 处版本口径 / 表述缺陷；72 道操作题 0 处越界；操作类知识点 48 / 48 覆盖；2025 大纲 28 / 28 条覆盖；理论题库 781 题。详见 <a href="./tools/site_audit_report.json">全站审计报告</a>。</p></div></section>

  <section class="section-sm"><h2>六、理论考试内容归属说明</h2>
    <div class="card"><p class="mb0">__OWN__</p></div></section>
</main>
<footer class="footer"><div class="wrap"><div class="cols">
  <div><h4>核心模块</h4><p class="small"><a href="./实操训练.html">实操训练 · 72 题</a> · <a href="./理论考试.html">理论考试 · 781 题</a> · <a href="./考试模拟系统/index.html">模拟考试</a></p></div>
  <div><h4>辅助资料</h4><p class="small"><a href="./考试介绍.html">考试介绍</a> · <a href="./教学大纲.html">教学大纲</a> · <a href="./考纲对照表.html">考纲对照表</a> · <a href="./整站内容配置.html">整站内容配置</a></p></div>
  <div><h4>说明</h4><p class="small">依据 2025 年版官方大纲编写；校内教学辅助资料，非官方考试网站，不收集个人信息。</p></div>
</div><div class="disc">© 大连财经学院 · 计算机国家二级考试（WPS 类）课程组 ｜ 考试政策以中国教育考试网公告为准</div></div></footer>
</body></html>"""
    rep = {
        '__NAV__': site_nav.render_primary('理论考试.html'),
        '__SUBNAV__': site_nav.render_subnav('理论考试.html'),
        '__ROWS__': rows, '__TOTAL__': str(total), '__FEATS__': feats,
        '__PATH__': path, '__OWN__': TH['ownership_note'],
    }
    for k, v in rep.items():
        html = html.replace(k, v)
    HUB.write_text(html, encoding='utf-8')


def report():
    secs = sections()
    out = dict(
        module='理论考试', tier='core（与实操训练并列的一级核心模块）',
        hub='理论考试.html', app='理论题库/index.html',
        source=dict(page=TH['app_source'], data=TH['data_source'], build=TH['build_source']),
        sections=[dict(name=n, count=c) for n, c in secs],
        total=sum(c for _, c in secs), score=TH['score'],
        features=TH['features'], offline=TH['offline'],
        nav=['学习中心', '实操训练', '理论考试', '模拟考试'],
        learning_path=[x['stage'] + ' ' + x['name'] for x in CFG['learning_path']],
        ownership_note=TH['ownership_note'],
        generated_files=['理论考试.html', '理论题库/index.html', '理论题库/README.txt'],
    )
    (ROOT / 'tools' / 'theory_integration.json').write_text(
        json.dumps(out, ensure_ascii=False, indent=1), encoding='utf-8')
    return out


def main():
    secs = sections()
    assert sum(c for _, c in secs) == TH['total'], '题库题量与配置不一致'
    n = build_app()
    build_hub()
    r = report()
    print('理论考试栏目：理论考试.html')
    print('离线题库：理论题库/index.html（%d 字节，内嵌 %d 题）' % (n, r['total']))
    print('分册：' + ' + '.join('%s %d' % (a, b) for a, b in secs))
    print('归属：%s ｜ 主导航与实操训练同级' % r['tier'])


if __name__ == '__main__':
    main()
