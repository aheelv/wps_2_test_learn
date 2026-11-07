# -*- coding: utf-8 -*-
"""首页重构：实操训练与理论考试作为核心模块优先呈现，基础介绍降为辅助层级。

由 tools/site_config.json 取核心模块与学习路线；其余栏目从配置生成辅助资料区。
幂等：整段替换 hero / main 区块 / 学习路线 JS / 页脚导航，可反复运行。

用法：python tools/site_home.py
"""
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CFG = json.load(open(ROOT / 'tools' / 'site_config.json', encoding='utf-8'))
HOME = ROOT / 'index.html'

CARD_DESC = {
    '考试介绍': ('考试说明', '报考方式、考试内容、形式与时长、题型分值、成绩与证书', '📖', 'var(--m1)'),
    '教学大纲': ('教学大纲', '课程定位、能力目标、11 次课结构与讲练配比', '📋', 'var(--m4)'),
    '考纲对照表': ('考纲对照表', '2025 版大纲 28 条考试内容 → 课程章节与题目', '🧭', 'var(--m2)'),
    '培训课件': ('培训课件', '11 次课 44 课时，HTML 放映与 .pptx 双格式', '📊', 'var(--m3)'),
    '电子书': ('电子书', '按 44 个知识点精讲的网页教材，支持离线与打印', '📚', 'var(--m2)'),
    '教案': ('教案', '11 份教案：目标、课时安排、课堂练习与反思栏', '📝', 'var(--m3)'),
    '教学日历': ('教学日历', '11 次课排期、讲练配比与阶段里程碑', '🗓️', 'var(--m4)'),
    '资料汇编': ('资料汇编', '汇总资料与补充阅读，按主题归档', '🗂️', 'var(--m5)'),
    '整站内容配置': ('整站内容配置', '栏目层级、入口、学习路径与核查结论的可读视图', '🧩', 'var(--m6)'),
}
SUPPORT_ORDER = ['考试介绍', '教学大纲', '考纲对照表', '培训课件', '电子书',
                 '教案', '教学日历', '资料汇编', '整站内容配置']


def support_cards():
    items = {i['name']: i for g in CFG['nav']['support_groups'] for i in g['items']}
    out = []
    for n in SUPPORT_ORDER:
        it = items[n]
        label, desc, icon, color = CARD_DESC[n]
        out.append('<a class="qcard" style="--mc:%s" href="%s"><div class="ic">%s</div>'
                   '<h3>%s</h3><p>%s</p><span class="go">打开 →</span></a>'
                   % (color, it['href'], icon, label, desc))
    return '\n      '.join(out)


def core_section():
    p, t = CFG['core_modules']
    return """  <section class="section-sm" id="core">
    <h2>一、两大核心模块（先练这两块）</h2>
    <p class="lead">考试 100 分 = 操作题 80 分 + 单项选择题 20 分。首页只把直接对应得分的两块放在最前面；考试说明、考试大纲、课件与电子书降为辅助层级，放在后面按需查阅。</p>
    <div class="coregrid mt2">
      <a class="exbanner" href="%s" style="background:linear-gradient(120deg,#b8452f,#8c2f1f)">
        <div class="exb-ic">🖱️</div>
        <div class="exb-tx"><h3>实操训练 · %s</h3>
          <p>%s</p></div>
        <span class="exb-go">进入实操训练 →</span></a>
      <a class="exbanner" href="%s" style="background:linear-gradient(120deg,#1f5f8b,#123a5c)">
        <div class="exb-ic">📝</div>
        <div class="exb-tx"><h3>理论考试 · %s</h3>
          <p>%s</p></div>
        <span class="exb-go">进入理论考试 →</span></a>
    </div>
    <p class="small muted mt1">冲刺阶段用 <a href="./考试模拟系统/index.html"><b>全真模拟考试</b></a> 做整卷演练 ·
      <a href="./整站内容配置.html">查看整站内容配置与核查结论 →</a></p>
  </section>""" % (p['href'], p['stat'], p['detail'], t['href'], t['stat'], t['detail'])


def hero():
    return """<section class="hero"><div class="wrap">
  <div class="eyebrow">大连财经学院 · 计算机国家二级考试（WPS 类）· 学习中心</div>
  <h1>按 2025 版大纲自学备考<br><span style="font-size:.62em;font-weight:700;color:#ffd9a1">实操训练 + 理论考试，两条主线直通考场</span></h1>
  <p class="sub">本站把 <b>操作题 80 分</b> 与 <b>单项选择题 20 分</b> 拆成两条并行的学习主线：<b>8 次课 72 道实操题</b>（WPS 文字 3 次 / 表格 3 次 / 演示 2 次）逐题上手，<b>2 分册 781 道理论题</b>按大纲分册刷题；考试大纲、考试说明、课件与电子书作为辅助资料按需查阅。全部依据官方考试大纲（2025 年版）编写，统一按 <b>WPS Office 教育考试专用版</b> 口径。</p>
  <div class="flex mt2">
    <a class="btn accent" href="./实操训练.html">▶ 进入实操训练（72 题）</a>
    <a class="btn ghost" href="./理论考试.html">📝 进入理论考试（781 题）</a>
    <a class="btn ghost" href="./考试模拟系统/index.html">🖥 全真模拟考试</a>
  </div>
  <div class="hero-stats">
    <div class="hero-stat"><b>72</b><span>道实操题 · 8 次课</span></div>
    <div class="hero-stat"><b>781</b><span>道理论题 · 2 分册</span></div>
    <div class="hero-stat"><b>80+20</b><span>操作题 + 单选题</span></div>
    <div class="hero-stat"><b>28/28</b><span>2025 大纲条目覆盖</span></div>
    <div class="hero-stat"><b>2025</b><span>版官方大纲</span></div>
  </div>
</div></section>"""


def learning_path_js():
    colors = ['var(--m1)', 'var(--m3)', 'var(--m4)', 'var(--m5)', 'var(--m6)']
    rows = []
    for i, x in enumerate(CFG['learning_path']):
        rows.append("    ['%s','%s','%s','%s']" %
                    (x['stage'], x['name'], x['text'], colors[i % len(colors)]))
    return 'const steps=[\n' + ',\n'.join(rows) + '\n  ];'


def main():
    s = HOME.read_text(encoding='utf-8')
    orig = s

    # 1) meta 描述改为核心优先口径
    s = re.sub(r'<meta name="description" content="[^"]*">',
               '<meta name="description" content="大连财经学院计算机国家二级考试（WPS 类）学习中心：'
               '以实操训练 72 题与理论考试 781 题为两大核心模块，按 NCRE 二级 WPS Office '
               '高级应用与设计考试大纲（2025 年版）自学备考；考试说明、教学大纲、课件与电子书为辅助资料。'
               '本站为非官方考试网站，不提供报名、缴费、查分服务，不收集任何个人信息。">',
               s, count=1)

    # 2) hero 整段
    s, n = re.subn(r'<section class="hero">.*?</section>', lambda m: hero(), s, count=1, flags=re.S)
    assert n == 1, 'hero 未定位'

    # 3) 拆出 main 内的 section，按新层级重排
    m = re.search(r'<main class="wrap">(.*?)</main>', s, re.S)
    assert m, 'main 未定位'
    blocks = re.findall(r'<section class="section-sm">.*?</section>', m.group(1), re.S)
    # 幂等：首次运行 7 个 section（含两枚旧 banner）；重跑后核心区带 id 属性，
    # 不匹配无属性的 section 正则，故剩 5 个可复用区块
    assert len(blocks) >= 5, 'section 数量异常：%d' % len(blocks)

    def pick(key):
        return next(b for b in blocks if key in b)

    b_stat = pick('id="statband"')
    b_path = pick('id="path"')
    b_quick = pick('class="quick mt2"')
    b_mod = pick('id="modline"')
    b_exam = pick('id="scoreTable"')

    # 3a) 学习路线：改标题与导语，保留 #path 容器
    b_path = re.sub(r'<h2>.*?</h2>',
                    '<h2>二、按大纲自学路线（实操 + 理论双线）</h2>'
                    '<p class="lead">五个阶段，每阶段同时给上机题与理论题的安排；'
                    '考试大纲与考试说明在需要核对时再查，不占主线。</p>', b_path, count=1)
    # 3b) 辅助资料：改标题、导语，并按配置重建卡片
    b_quick = re.sub(r'<h2>.*?</h2>', '<h2>三、辅助资料（按大纲查漏补缺）</h2>', b_quick, count=1)
    b_quick = re.sub(r'<p class="lead">.*?</p>',
                     '<p class="lead">考试说明、考试大纲、考纲对照表、课件、电子书、教案与日历等为基础介绍与备课资料，'
                     '归入辅助层级；练习仍以<a href="./实操训练.html">实操训练</a>与<a href="./理论考试.html">理论考试</a>为准。</p>',
                     b_quick, count=1, flags=re.S)
    i = b_quick.index('<div class="quick mt2">')
    j = b_quick.rfind('</div>') + len('</div>')
    b_quick = b_quick[:i] + '<div class="quick mt2">\n      ' + support_cards() + '\n    </div>' + b_quick[j:]
    # 3c) 课程结构与考试信息降为辅助、顺延编号
    b_mod = re.sub(r'<h2>.*?</h2>', '<h2>四、课程结构（辅助 · 11 次课 44 课时 · 5 大模块）</h2>', b_mod, count=1)
    b_exam = re.sub(r'<h2>.*?</h2>', '<h2>五、考试信息速览（辅助）</h2>', b_exam, count=1)

    new_main = ('<main class="wrap">\n\n' + '\n\n'.join([
        b_stat.strip(), core_section(), b_path.strip(), b_quick.strip(),
        b_mod.strip(), b_exam.strip()]) + '\n\n</main>')
    s = s[:m.start()] + new_main + s[m.end():]

    # 4) 学习路线 JS 数据
    s, n = re.subn(r'const steps=\[.*?\];', lambda mm: learning_path_js(), s, count=1, flags=re.S)
    assert n == 1, 'steps JS 未定位'

    # 5) 页脚导航：核心模块前置
    old_footer = re.search(r'<div><h4>成果导航</h4>.*?</div>', s, re.S)
    if old_footer:
        new_footer = ('<div><h4>核心模块</h4><p class="small">'
                      '<a href="./实操训练.html">实操训练 · 72 题</a> · '
                      '<a href="./理论考试.html">理论考试 · 781 题</a> · '
                      '<a href="./考试模拟系统/index.html">模拟考试</a></p>'
                      '<p class="small"><a href="./整站内容配置.html">整站内容配置</a> · '
                      '<a href="./练习素材/索引.html">练习素材索引</a></p>'
                      '<p class="small">辅助：<a href="./考试介绍.html">考试介绍</a> · '
                      '<a href="./教学大纲.html">教学大纲</a> · <a href="./考纲对照表.html">考纲对照表</a> · '
                      '<a href="./培训课件.html">培训课件</a> · <a href="./电子书.html">电子书</a> · '
                      '<a href="./教案.html">教案</a> · <a href="./教学日历.html">教学日历</a> · '
                      '<a href="./资料汇编.html">资料汇编</a></p>'
                      '<p class="small"><a href="./用户中心.html">用户中心</a> · '
                      '<a href="./群管理.html">班级群</a> · <a href="./使用说明.html">使用说明</a> · '
                      '<a href="./关于本站.html">关于本站</a></p></div>')
        s = s.replace(old_footer.group(0), new_footer, 1)

    HOME.write_text(s, encoding='utf-8')
    print('首页重构完成：%d → %d 字节' % (len(orig), len(s)))
    print('  核心模块 %d 个 · 辅助资料卡片 %d 张 · 学习路线 %d 阶段' %
          (len(CFG['core_modules']), len(SUPPORT_ORDER), len(CFG['learning_path'])))


if __name__ == '__main__':
    main()
