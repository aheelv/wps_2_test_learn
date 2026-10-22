# -*- coding: utf-8 -*-
"""
实操训练课页面渲染器
用法：python tools/gen_practice.py
数据：tools/pdata_*.py 中的 PAGES 列表（每个元素 = 一次课的完整数据）

设计原则：
1. 与 入门实操课.html 完全一致的组件与观感（同一套 practice.css）
2. 一次课 = 4 小节（每小节 1 个课时/45 分钟） = 8 道实操题（每小节 2 题）
3. 例题固定五段式：题目要求 → 录入素材 → 解题步骤 → 采分点 → 易错提醒
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))

NAV = [
    ("./index.html", "学习中心"),
    ("./考试介绍.html", "考试介绍"),
    ("./教学大纲.html", "教学大纲"),
    ("./考纲对照表.html", "考纲对照表"),
    ("./教学日历.html", "教学日历"),
    ("./教案.html", "教案"),
    ("./实操训练.html", "实操训练"),
    ("./培训课件.html", "培训课件"),
    ("./电子书.html", "电子书"),
    ("./资料汇编.html", "资料汇编"),
    ("./考试模拟系统/index.html", "模拟考试"),
]

MOD_META = {
    "文字": {"color": "var(--m3)", "name": "WPS 处理文字文档", "modno": "模块二", "score": "30 分", "type": "文字文档操作题", "hours": 12},
    "表格": {"color": "var(--m4)", "name": "WPS 处理电子表格", "modno": "模块三", "score": "30 分", "type": "电子表格操作题", "hours": 12},
    "演示": {"color": "var(--m5)", "name": "WPS 设计演示文稿", "modno": "模块四", "score": "20 分", "type": "演示文稿操作题", "hours": 8},
}


def nav_html(current):
    out = []
    for href, label in NAV:
        cls = ' class="on"' if label == current else ""
        out.append('    <a%s href="%s">%s</a>' % (cls, href, label))
    return "\n".join(out)


def li(items, cls=""):
    c = ' class="%s"' % cls if cls else ""
    return "".join("<li>%s</li>" % x for x in items)


def render_ex(P, sec_i, ex_i, ex):
    eid = "e%d-%d" % (P["seq"], ex_i + 1)
    badges = "".join('<span class="badge info">%s</span>' % t for t in ex.get("tags", []))
    src = ""
    if ex.get("src"):
        src = ('            <div class="src"><div class="kicker">录入素材</div>'
               "<pre>%s</pre></div>\n" % ex["src"])
    steps = "".join("<li>%s</li>" % s for s in ex["steps"])
    warns = "<ul>%s</ul>" % li(ex.get("warns", [])) if ex.get("warns") else ""
    tip = ""
    if ex.get("tip"):
        tip = ('            <div class="callout tip"><h4>%s</h4><p class="small mb0">%s</p></div>\n'
               % (ex["tip"][0], ex["tip"][1]))
    return """        <article class="ex" id="{eid}">
          <header class="ex-h">
            <span class="ex-no">例 {no}</span>
            <h4>{title}</h4>
            {badges}
            <span class="badge">{mins} 分钟</span>
            <button class="fold" type="button" data-fold>收起步骤</button>
          </header>
          <div class="ex-b">
            <div class="req">
              <div class="kicker">题目要求</div>
              <ol>{req}</ol>
            </div>
{src}            <div class="kicker">解题步骤</div>
            <ol class="steps">{steps}</ol>
            <div class="score"><b>采分点</b>{score}</div>
            <div class="callout warn">
              <h4>易错提醒</h4>
              {warns}
            </div>
{tip}          </div>
        </article>
""".format(eid=eid, no=ex["no"], title=ex["title"], badges=badges,
           mins=ex.get("mins", 12), req=li(ex["req"]), src=src,
           steps=steps, score=ex["score"], warns=warns, tip=tip)


def render_sec(P, si, sec):
    meta = MOD_META[P["mod"]]
    exs = "".join(render_ex(P, si, ei, ex) for ei, ex in enumerate(sec["exs"]))
    points = "".join("<li>%s</li>" % p for p in sec["points"])
    return """  <!-- ============ 第 {n} 小节 ============ -->
  <section id="s{n}">
    <div class="lesson">
      <div class="lesson-h">
        <div class="lnum"><small>小节</small>{n2}</div>
        <div class="ltx">
          <h3>{title}</h3>
          <p>{sub}</p>
          <div class="lmeta"><span>45 分钟</span><span>讲 10 / 练 35</span><span>2 道实操题</span><span>{know}</span></div>
        </div>
      </div>
      <div class="lesson-b">
        <div class="callout tip">
          <h4>本小节必须掌握的知识点</h4>
          <ul class="clean small" style="margin-top:6px">{points}</ul>
        </div>
{exs}      </div>
    </div>
  </section>

""".format(n=si + 1, n2="%02d" % (si + 1), title=sec["title"], sub=sec["sub"],
           know=sec["know"], points=points, exs=exs)


def render_cover(P):
    rows = []
    for si, sec in enumerate(P["sections"]):
        pills = "".join('<span class="pill">%s</span>' % p for p in sec["points"])
        exs = "、".join("例 %s" % ex["no"] for ex in sec["exs"])
        rows.append(
            "<tr><td class=\"num\"><b>%d</b></td><td><b>%s</b></td>"
            '<td class="small">%s</td><td class="small nowrap">%s</td><td>%s</td></tr>'
            % (si + 1, sec["title"].replace("<br>", ""), sec["know"], exs, pills)
        )
    return """    <div class="table-wrap mt2">
      <table class="tbl cover-tbl">
        <thead><tr><th class="num" style="width:56px">小节</th><th style="width:210px">小节主题</th><th style="width:190px">对应考纲条目</th><th class="num" style="width:110px">题目</th><th>覆盖知识点</th></tr></thead>
        <tbody>
%s
        </tbody>
      </table>
    </div>""" % "\n".join(rows)


def render_pager(P):
    prev, nxt = P.get("prev"), P.get("next")
    cells = []
    if prev:
        cells.append('<a class="prev" href="./%s"><div class="dir">← 上一次课</div>'
                     '<div class="tt">%s</div><div class="dd">%s</div></a>' % (prev[0], prev[1], prev[2]))
    else:
        cells.append('<a class="prev" href="./实操训练.html"><div class="dir">← 返回</div>'
                     '<div class="tt">实操训练总览</div><div class="dd">8 次课学习地图</div></a>')
    if nxt:
        cells.append('<a class="next" href="./%s"><div class="dir">下一次课 →</div>'
                     '<div class="tt">%s</div><div class="dd">%s</div></a>' % (nxt[0], nxt[1], nxt[2]))
    else:
        cells.append('<a class="next" href="./考试模拟系统/index.html"><div class="dir">下一步 →</div>'
                     '<div class="tt">进入全真模拟</div><div class="dd">120 分钟限时自测</div></a>')
    return '<div class="pager">%s</div>' % "".join(cells)


def render(P):
    meta = MOD_META[P["mod"]]
    secs = "".join(render_sec(P, i, s) for i, s in enumerate(P["sections"]))
    goals = li(P["goal"])
    checklist = li(P["checklist"], "ck")
    pitfalls = li(P["pitfalls"])
    navs = "".join('<a href="#s%d">第 %d 小节 · %s</a>' % (i + 1, i + 1, s["short"])
                   for i, s in enumerate(P["sections"]))
    ex_total = sum(len(s["exs"]) for s in P["sections"])
    title_full = "%s · 第 %d 次课（4 小节 %d 题）| 大连财经学院 计算机国家二级（WPS 类）" % (
        meta["name"], P["seq"], ex_total)

    html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title_full}</title>
<meta name="description" content="{desc}">
<link rel="stylesheet" href="./assets/style.css">
<link rel="stylesheet" href="./assets/practice.css">
</head>
<body>

<header class="topbar"><div class="wrap">
  <a class="brand" href="./index.html"><span class="logo">WPS</span><span>大连财经学院 · 计算机国家二级（WPS 类）<small>校内教学辅助资料 · 非官方</small></span></a>
  <nav class="navlinks">
{nav}
  </nav>
</div></header>

<div class="noticebar"><div class="wrap">
  <span class="nb-ic">ⓘ</span>
  <span><b>大连财经学院</b> 计算机国家二级考试（WPS 类）校内教学辅助资料 · <b>本站为非官方考试网站</b>，不提供报名、缴费、查分服务，不收集任何个人信息。官方信息请以中国教育考试网 <a href="https://ncre.neea.edu.cn/" target="_blank" rel="noopener">ncre.neea.edu.cn</a> 为准。</span>
</div></div>

<section class="hero"><div class="wrap">
  <div class="eyebrow">实操训练 · 第 {seq} 次课 / 共 8 次 · {modname}</div>
  <h1>{h1}</h1>
  <p class="sub">{sub}</p>
  <div class="flex mt2">
    <a class="btn accent" href="#s1">▶ 从第 1 小节开始</a>
    <a class="btn ghost" href="#cover">知识点覆盖对照</a>
    <a class="btn ghost" href="#check">交卷自查清单</a>
  </div>
  <div class="hero-stats">
    <div class="hero-stat"><b>4</b><span>小节 · 每节 45 分钟</span></div>
    <div class="hero-stat"><b>{ex_total}</b><span>道实操例题</span></div>
    <div class="hero-stat"><b>{score}</b><span>{type}</span></div>
    <div class="hero-stat"><b>80%</b><span>课堂时间用于动手</span></div>
    <div class="hero-stat"><b>{modno}</b><span>{hours} 课时</span></div>
  </div>
</div></section>

<main class="wrap">

  <div class="crumbs">
    <a href="./index.html">学习中心</a><span class="sep">/</span><a href="./实操训练.html">实操训练</a><span class="sep">/</span>第 {seq} 次课 · {modname}
  </div>

  <section class="section-sm">
    <h2>本次课定位与目标</h2>
    <p class="lead">{lead}</p>
    <div class="grid g2 mt2">
      <div class="card">
        <h3>课程基本信息</h3>
        <div class="table-wrap mt1" style="border:0">
          <table class="tbl small-tbl" style="min-width:auto">
            <tbody>
              <tr><th style="width:110px">所属模块</th><td>{modno} · {modname}（{hours} 课时）</td></tr>
              <tr><th>本次课位置</th><td>第 {seq} 次课 / 共 8 次 · 4 小节 {ex_total} 题</td></tr>
              <tr><th>对应考纲</th><td>{syllabus}</td></tr>
              <tr><th>对应题型</th><td>{type}（{score}）</td></tr>
              <tr><th>讲练配比</th><td>每小节讲授 8~10 分钟 ＋ 动手 35~37 分钟（练习占 <b>80%</b>）</td></tr>
              <tr><th>前置要求</th><td>{prereq}</td></tr>
              <tr><th>结课标准</th><td>{std}</td></tr>
            </tbody>
          </table>
        </div>
      </div>
      <div class="card" style="border-left:5px solid {color}">
        <h3>学完这 4 小节，你要能做到</h3>
        <ul class="clean mt1">{goals}</ul>
        <div class="callout key mt2"><h4>💡 为什么这样排</h4><p class="small mb0">{why}</p></div>
      </div>
    </div>
  </section>

  <section class="section-sm" id="cover">
    <h2>知识点覆盖对照表</h2>
    <p class="muted">本表逐小节列出「对应考纲条目 → 承载题目 → 覆盖的具体知识点」，用于核对<b>无遗漏</b>；考前可只看这一张表做最后清点。</p>
{cover}
    <div class="callout warn mt2">
      <h4>⚠️ 覆盖口径说明</h4>
      <p class="mb0 small">表中知识点均来自《全国计算机等级考试（NCRE）二级 WPS Office 高级应用与设计考试大纲（2025 年版）》{modno}对应条目，每一条都有具体题目承接。<b>同一知识点在不同题目中重复出现是有意设计</b>——考试评分看的是操作结果，只有练到"不看书也能做对"才算掌握。</p>
    </div>
  </section>

  <nav class="lessonnav">{navs}</nav>

{secs}
  <section class="section-sm" id="check">
    <h2>本次课小结与交卷自查</h2>
    <p class="lead">做完 8 道题，用下面两张表各花 3 分钟过一遍——<b>自查过的题，考场上才敢交卷</b>。</p>
    <div class="grid g2 mt2">
      <div class="card">
        <h3>✅ 交卷自查清单（做完逐项打勾）</h3>
        <ol class="checklist mt1">{checklist}</ol>
      </div>
      <div class="card" style="border-left:5px solid var(--accent)">
        <h3>🔻 本次课最容易丢分的 5 处</h3>
        <ul class="clean mt1">{pitfalls}</ul>
        <div class="callout key mt2"><h4>考场时间提示</h4><p class="small mb0">{timeplan}</p></div>
      </div>
    </div>
{pager}
  </section>

</main>

<div class="bar">
  <button type="button" id="btnAll">收起全部步骤</button>
  <button type="button" class="clock" id="btnClock">⏱ 45:00 课时计时</button>
</div>

<footer class="footer"><div class="wrap"><div class="cols">
  <div><h4>大连财经学院 · 计算机国家二级考试（WPS 类）</h4><p class="small"><span class="org">主办：大连财经学院计算机国家二级考试（WPS 类）课程组</span></p><p class="small">本站为<b>校内教学辅助资料</b>，依据《全国计算机等级考试(NCRE) 二级 WPS Office 高级应用与设计考试大纲(2025 年版)》与《二级公共基础知识考试大纲(2025 年版)》编写，供教学与备考使用。</p></div>
  <div><h4>实操训练导航</h4><p class="small"><a href="./实操训练.html">实操训练总览</a> · <a href="./入门实操课.html">文字 1</a> · <a href="./实操-文字2.html">文字 2</a> · <a href="./实操-文字3.html">文字 3</a></p><p class="small"><a href="./实操-表格1.html">表格 1</a> · <a href="./实操-表格2.html">表格 2</a> · <a href="./实操-表格3.html">表格 3</a></p><p class="small"><a href="./实操-演示1.html">演示 1</a> · <a href="./实操-演示2.html">演示 2</a> · <a href="./考试模拟系统/index.html">模拟考试</a></p></div>
  <div><h4>官方信息</h4><p class="small">本站为<b>非官方</b>网站，不提供报名、缴费、查分服务。考试政策与报名信息以中国教育考试网 <a href="https://ncre.neea.edu.cn/" target="_blank" rel="noopener">ncre.neea.edu.cn</a> 当年公告为准。</p><p class="small">学校官网：<a href="https://www.dlufe.edu.cn/" target="_blank" rel="noopener">www.dlufe.edu.cn</a></p></div>
  <div><h4>免责声明</h4><p class="small">本站不收集任何个人信息，无收费项目，不含广告与商业推广；内容仅供校内教学与备考参考，如与官方文件不一致，以官方文件为准。</p><p class="small"><a href="./关于本站.html">关于本站 / 免责声明 →</a></p></div>
</div>
<div class="disc">© 大连财经学院 · 计算机国家二级考试（WPS 类）课程组 ｜ 校内教学辅助资料，非官方考试网站 ｜ 考试政策以中国教育考试网公告为准</div>
</div></footer>

<script>
(function(){{
  document.querySelectorAll('[data-fold]').forEach(function(btn){{
    btn.addEventListener('click', function(){{
      var card = btn.closest('.ex');
      var body = card.querySelector('.ex-b');
      var hidden = body.classList.toggle('hide');
      btn.textContent = hidden ? '展开步骤' : '收起步骤';
    }});
  }});

  var allBtn = document.getElementById('btnAll');
  var expanded = true;
  allBtn.addEventListener('click', function(){{
    expanded = !expanded;
    document.querySelectorAll('.ex-b').forEach(function(b){{ b.classList.toggle('hide', !expanded); }});
    document.querySelectorAll('[data-fold]').forEach(function(b){{ b.textContent = expanded ? '收起步骤' : '展开步骤'; }});
    allBtn.textContent = expanded ? '收起全部步骤' : '展开全部步骤';
  }});

  var clock = document.getElementById('btnClock');
  var left = 45 * 60, timer = null;
  function fmt(s){{
    var m = Math.floor(s / 60), ss = s % 60;
    return (m < 10 ? '0' : '') + m + ':' + (ss < 10 ? '0' : '') + ss;
  }}
  clock.addEventListener('click', function(){{
    if (timer) {{ clearInterval(timer); timer = null; clock.textContent = '⏱ ' + fmt(left) + ' 已暂停'; return; }}
    if (left <= 0) {{ left = 45 * 60; }}
    timer = setInterval(function(){{
      left--;
      if (left <= 0) {{ clearInterval(timer); timer = null; clock.textContent = '⏱ 时间到！'; left = 0; return; }}
      clock.textContent = '⏱ ' + fmt(left);
    }}, 1000);
    clock.textContent = '⏱ ' + fmt(left);
  }});
}})();
</script>
<script src="./assets/auth.js"></script>
<script src="./assets/groups.js"></script>
<script src="./assets/auth-ui.js"></script>
</body>
</html>
""".format(
        title_full=title_full,
        desc=P.get("desc", title_full),
        nav=nav_html("实操训练"),
        seq=P["seq"], modname=meta["name"], modno=meta["modno"], hours=meta["hours"],
        score=meta["score"], type=meta["type"], color=meta["color"],
        h1=P["title"], sub=P["subtitle"], lead=P["lead"], ex_total=ex_total,
        mod=P["mod"], syllabus=P["syllabus"], prereq=P["prereq"], std=P["std"],
        goals=goals, why=P["why"], cover=render_cover(P), navs=navs, secs=secs,
        checklist=checklist, pitfalls=pitfalls, timeplan=P["timeplan"], pager=render_pager(P),
    )
    return html


def main():
    import pdata_all

    for P in pdata_all.PAGES:
        out = os.path.join(ROOT, P["file"])
        with open(out, "w", encoding="utf-8") as f:
            f.write(render(P))
        size = os.path.getsize(out) / 1024
        exs = sum(len(s["exs"]) for s in P["sections"])
        print("OK  %-22s %2d 小节 %2d 题  %6.1f KB" % (P["file"], len(P["sections"]), exs, size))


if __name__ == "__main__":
    main()
