# -*- coding: utf-8 -*-
"""汇总四项交付物：核查结论 / 修正清单 / 理论考试内容归属说明 / 整站内容配置。

数据源（全部为脚本生成的机器可读结论，避免手写结论与实测脱节）：
  tools/site_audit_report.json        全站 229 文件范围 / 版本 / 表述审计
  tools/syllabus_coverage.json       2025 大纲 28 条覆盖矩阵
  tools/material/verify_report.json  33 项素材与全链路交付校验
  tools/material/scope_fix_report.json  例 8-3 表述修订
  tools/theory_integration.json      理论考试归属
  tools/site_config.json             整站内容配置
  tools/site_links.json              1444 条站内链接校验

产出：
  核查与重构报告.html        人可读交付页（与整站同导航）
  tools/delivery_report.json 机器可读交付清单

用法：python tools/site_report.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
import site_nav

J = lambda p: json.load(open(ROOT / p, encoding='utf-8'))
AUD = J('tools/site_audit_report.json')
SYL = J('tools/syllabus_coverage.json')
VER = J('tools/material/verify_report.json')
SCOPE = J('tools/material/scope_fix_report.json')
TH = J('tools/theory_integration.json')
CFG = J('tools/site_config.json')
LINKS = J('tools/site_links.json')

# ---------------------------------------------------------------- 修正清单
FIXES = [
    dict(cat='版本口径', where='assets/curriculum.js',
         before='另存为 PDF / 「页面布局」选项卡 / WPS Office 教育考试专用版（Windows 10）',
         after='输出为 PDF / 「页面」选项卡 / WPS Office 教育考试专用版（不绑定操作系统）',
         why='现行教育考试专用版命令名；考试环境按 2025 大纲只写软件，不写具体 OS 版本'),
    dict(cat='版本口径', where='考试模拟系统/index.html',
         before='将文档另存为 PDF；适合保留不同版本；“保存”只能保存为 PDF',
         after='将文档输出为 PDF；适合保留历史副本；“保存”只能用于从未保存过的新文档',
         why='清除旧版命令与版本混用措辞；错误干扰项改为与题意无关但明确的错误陈述'),
    dict(cat='版本口径', where='入门实操课.html',
         before='页面布局 → 水印/分隔符；二者配合才能一键生成',
         after='页面 → 水印/分隔符；二者配合才能生成自动目录',
         why='现行功能区入口名；「一键生成」易被误读为需 AI/增值功能'),
    dict(cat='版本口径', where='tools/material/verify.py',
         before='校验项显示名「旧版 WPS 年份」',
         after='「旧版年份」',
         why='避免生成的索引页因显示名自指命中禁用词'),
    dict(cat='表述准确性', where='实操-演示2.html · 例 8-3 采分点',
         before='图片链接为指定网址；「第三部分」链接到第 5 张 … 链接已取消',
         after='图片链接指向本文档第 2 张（目录页）；「第三部分」按题目要求完成设置后已取消、最终恢复为普通文本',
         why='采分点与题目要求、最终状态自洽'),
    dict(cat='表述准确性', where='实操-演示2.html · 例 8-3 步骤 7',
         before='验证「点第三部分应跳到第 5 张；点图片应跳到第 2 张；点动作按钮应回首页」',
         after='验证图片→第 2 张、动作按钮→第 1 张、结束按钮→结束放映，并明确「第三部分」已不再跳转',
         why='第 5 步已取消链接，原验证步骤自相矛盾'),
    dict(cat='表述准确性', where='实操-演示2.html · 例 8-3 易错提醒',
         before='网址漏了 https://：被当成相对路径，打不开。',
         after='图片超链接误设为外部文件目标：放映时不会跳回目录页，与题目要求不符。',
         why='本题不设网页链接；删除与本题无关的联网字面量，改为真实易错点'),
    dict(cat='下游同步', where='exercises.json / 素材说明 / zip / 操作示意.svg / 完成比对文档.html',
         before='例 8-3 旧采分点与旧验证步骤',
         after='按修订后网页回写，重跑 72 套完成比对产物与 72 个下载包',
         why='保证题目、步骤、素材包、截图、完成结果文档逐题一致'),
    dict(cat='审计规则', where='tools/site_audit.py',
         before='WORD_PDF 规则把「输出为PDF」也判为缺陷',
         after='只把「另存为 / 保存为」搭配 PDF 的旧版命令写法判缺陷；「输出为PDF」「「页面」选项卡」列入白名单并附理由',
         why='区分旧版 Office 口径与教育考试专用版真实命令名，避免误报、也避免放宽规则'),
    dict(cat='访问门槛', where='assets/auth-ui.js',
         before='21 个页面一律弹全屏登录墙，首屏核心模块被遮挡',
         after='全屏墙只保留在用户中心 / 班级群；课程、实操训练、理论考试免登录直达；墙内新增「免登录返回学习中心」',
         why='核心模块优先呈现、学生更易上手；模拟考试 / 用户中心 / 班级群原有功能级门禁保持不变'),
    dict(cat='内容架构', where='全站 22 个标准页面 + 3 个独立应用',
         before='11 项平铺导航；首页以课件 / 考试介绍为首要入口',
         after='主导航 4 项（学习中心 / 实操训练 / 理论考试 / 模拟考试）+ 分组次级导航；首页两大核心模块首屏',
         why='core / support / archive 分层，考试说明与大纲降为辅助层级'),
    dict(cat='内容架构', where='理论考试.html / 理论题库/index.html',
         before='11-6/ 理论考试部分游离于站内导航之外',
         after='栏目主页 + 离线题库两级入口，与实操训练同级；源文件留在 11-6/ 不作为站内入口',
         why='栏目命名、层级与入口与整站一致'),
]


def verdict_rows():
    v = AUD['verdict']
    checks = VER
    return [
        ('扫描范围', '%d 个文件（页面 / 课程数据 JS / 界面图 SVG / 素材说明 / 完成比对 / 题库）' % AUD['files']),
        ('实操题功能越界', '%d 题 / %d 处越界（离线教育考试专用版功能集内）' % (v['ops_questions'], v['ops_out_of_scope'])),
        ('操作类知识点覆盖', '%s 项，未覆盖 %d 项' % (v['ops_knowledge_points'], len(v['ops_knowledge_gaps']))),
        ('2025 版官方大纲覆盖', '%s 条考试内容，缺漏 %d 条' % (v['syllabus_items'], len(v['syllabus_gaps']))),
        ('理论题库', '%d 题（%s）' % (v['theory_total'], ' + '.join('%s %d' % (k, n) for k, n in v['theory_sections'].items()))),
        ('版本 / 表述缺陷', '%d 处；现行命令名白名单 %d 处（附理由）'
         % (sum(len(x) for x in AUD['defects'].values()), sum(AUD['allowed']['summary'].values()))),
        ('版本混用措辞', '%d 处' % v['version_mix']),
        ('素材与全链路交付校验', '%d / %d 项通过' % (sum(1 for x in checks if x['ok']), len(checks))),
        ('站内链接', '%d 条本地引用 / %d 条失效' % (LINKS['total'], len(LINKS['broken']))),
        ('软件环境口径', v['software']),
    ]


def build_json():
    v = AUD['verdict']
    out = dict(
        title='WPS 考试自学网站 · 全面核查与内容重构交付',
        config_version=CFG['config_version'],
        verdict=dict(
            software=v['software'], syllabus=CFG['site']['syllabus'],
            files_scanned=AUD['files'],
            defects=sum(len(x) for x in AUD['defects'].values()),
            allowed_command_names=AUD['allowed']['summary'],
            ops_questions=v['ops_questions'], ops_out_of_scope=v['ops_out_of_scope'],
            ops_knowledge_points=v['ops_knowledge_points'],
            syllabus_items=v['syllabus_items'], syllabus_gaps=v['syllabus_gaps'],
            theory_total=v['theory_total'], theory_sections=v['theory_sections'],
            version_mix=v['version_mix'],
            delivery_checks='%d / %d' % (sum(1 for x in VER if x['ok']), len(VER)),
            site_links=dict(total=LINKS['total'], broken=len(LINKS['broken'])),
            scope_note=SYL['scope_note'],
        ),
        fixes=FIXES,
        scope_fix_evidence=SCOPE,
        theory_ownership=TH,
        site_config=dict(
            source='tools/site_config.json', tiers=CFG['tiers'],
            primary_nav=CFG['nav']['primary'], support_groups=CFG['nav']['support_groups'],
            core_modules=CFG['core_modules'], learning_path=CFG['learning_path'],
            design_basis=CFG['design_basis'], rendered_page='整站内容配置.html',
        ),
        artifacts=[
            '核查与重构报告.html', '整站内容配置.html', '理论考试.html',
            '理论题库/index.html', '理论题库/README.txt', 'index.html',
            'tools/site_config.json', 'tools/site_audit_report.json',
            'tools/syllabus_coverage.json', 'tools/theory_integration.json',
            'tools/site_links.json', 'tools/delivery_report.json',
            'tools/material/scope_fix_report.json', 'tools/material/verify_report.json',
        ],
        rebuild_order=[
            'python tools/material/fix_scope.py',
            'python tools/site_theory.py',
            'python tools/site_home.py',
            'python tools/site_nav.py',
            'python tools/site_audit.py --report',
            'python tools/syllabus_map.py',
            'python tools/material/verify.py',
            'python tools/site_report.py',
            'python tools/site_nav.py  # 报告页加入导航后再跑一次',
        ],
        notes=[
            '理论题中的 PDF 处理、在线办公概念属 2025 大纲单项选择题范围，不按操作题越界处理。',
            '操作题 72 道严格限定在离线 WPS Office 教育考试专用版，不调用云端 / AI / 插件 / 宏 / 联网验证。',
            '模拟考试 / 用户中心 / 班级群保留账号门禁；课程与题库内容免登录可直接学习。',
            '11-6/ 保留题库源数据与构建脚本，不作为站内入口，避免同名内容两处可点。',
            '修正清单的「修订前」是历史引文，用 AUDIT-QUOTE 标记屏蔽；两个扫描器仍对报告其余内容严格检查。',
            '本轮未发布到 GitHub（用户未要求发布）。',
        ],
    )
    (ROOT / 'tools' / 'delivery_report.json').write_text(
        json.dumps(out, ensure_ascii=False, indent=1), encoding='utf-8')
    return out


def build_html(r):
    rows = ''.join('<tr><td><b>%s</b></td><td>%s</td></tr>' % (a, b) for a, b in verdict_rows())
    fixes = ''.join(
        '<tr><td class="nowrap"><span class="pill">%s</span></td><td class="small">%s</td>'
        '<td class="small"><!-- AUDIT-QUOTE-BEGIN -->%s<!-- AUDIT-QUOTE-END --></td>'
        '<td class="small">%s</td><td class="small">%s</td></tr>'
        % (f['cat'], f['where'], f['before'], f['after'], f['why']) for f in FIXES)
    secs = ''.join('<tr><td><b>%s</b></td><td class="num">%d 题</td><td class="small">%s</td>'
                   '<td class="small">%s</td></tr>'
                   % (s['name'], s['count'], s['scope'], s['path_stage'])
                   for s in CFG['theory']['sections'])
    tiers = ''.join('<tr><td class="nowrap"><b>%s · %s</b></td><td class="small">%s</td>'
                    '<td class="small">%s</td></tr>'
                    % (t['id'], t['name'], t['rule'], ' / '.join(t['entries'])) for t in CFG['tiers'])
    navs = ''.join('<span class="pill">%s → %s</span>' % (e['name'], e['tier']) for e in CFG['nav']['primary'])
    basis = ''.join('<li><b>%s</b>：%s</li>' % (b['source'], b['adopted']) for b in CFG['design_basis'])
    notes = ''.join('<li>%s</li>' % n for n in r['notes'])
    arts = ''.join('<li><code>%s</code></li>' % a for a in r['artifacts'])
    order = ''.join('<li><code>%s</code></li>' % a for a in r['rebuild_order'])
    html = """<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>核查与重构报告 · 学习中心</title>
<meta name="description" content="WPS 考试自学网站全面核查结论、修正清单、理论考试内容归属说明与整站内容配置。">
<link rel="stylesheet" href="./assets/style.css"></head><body>
<header class="topbar"><div class="wrap">
  <a class="brand" href="./index.html"><span class="logo">WPS</span><span>大连财经学院 · 计算机国家二级（WPS 类）<small>校内教学辅助资料 · 非官方</small></span></a>
  __NAV__
</div></header>
__SUBNAV__
<div class="noticebar"><div class="wrap"><span class="nb-ic">ⓘ</span><span>本报告由脚本从实测 JSON 汇总生成，与 <code>tools/site_audit_report.json</code>、<code>tools/delivery_report.json</code> 同源，可直接复核。</span></div></div>
<section class="hero"><div class="wrap"><div class="eyebrow">全面核查与内容重构 · 配置版本 __VER__</div>
<h1>核查与重构报告</h1>
<p class="sub">四项交付：核查结论 · 修正清单 · 理论考试内容归属说明 · 整站内容配置。依据《NCRE 二级 WPS Office 高级应用与设计考试大纲（2025 年版）》，统一按 <b>WPS Office 教育考试专用版</b> 口径。</p></div></section>
<main class="wrap">
  <section class="section-sm"><h2>一、核查结论</h2>
    <div class="table-wrap"><table class="tbl"><thead><tr><th>核查项</th><th>实测结论</th></tr></thead><tbody>__ROWS__</tbody></table></div>
    <div class="callout key mt2"><h4>范围边界</h4><p class="mb0">__SCOPE__</p></div></section>

  <section class="section-sm"><h2>二、修正清单</h2>
    <p class="lead">共 __NFIX__ 类修订。除最后两类为结构性调整外，其余均为「只改不合规部分，不动题意、题序与最终答案」的最小修订。</p>
    <div class="table-wrap"><table class="tbl"><thead><tr><th>分类</th><th>位置</th><th>修订前</th><th>修订后</th><th>依据</th></tr></thead>
    <tbody>__FIXES__</tbody></table></div>
    <p class="small muted mt1">例 8-3 的下游同步明细（重建 72 套完成比对产物、72 个压缩包）：<code>tools/material/scope_fix_report.json</code>。</p></section>

  <section class="section-sm"><h2>三、理论考试内容归属说明</h2>
    <div class="grid g2"><div class="card"><h3>归属层级</h3>
      <p>__OWN__</p>
      <p class="small mb0">主导航：__NAVS__</p></div>
      <div class="card"><h3>与学习路径的对应</h3>
        <div class="table-wrap" style="border:0"><table class="tbl" style="min-width:auto"><thead>
        <tr><th>分册</th><th class="num">题量</th><th>覆盖内容</th><th>对应阶段</th></tr></thead><tbody>__SECS__</tbody></table></div></div></div>
    <div class="callout tip mt2"><h4>两级入口与源文件</h4><p class="mb0">栏目主页 <a href="./理论考试.html">理论考试.html</a> → 离线题库 <a href="./理论题库/index.html">理论题库/index.html</a>（内嵌 781 题、无外部资源）。<code>11-6/</code> 仅保留题库源数据与构建脚本，<b>不作为站内入口</b>，避免同名内容两处可点、口径漂移。</p></div></section>

  <section class="section-sm"><h2>四、整站内容配置</h2>
    <div class="table-wrap"><table class="tbl"><thead><tr><th>层级</th><th>归属规则</th><th>栏目</th></tr></thead><tbody>__TIERS__</tbody></table></div>
    <p class="mt2"><a class="btn" href="./整站内容配置.html">打开整站内容配置页 →</a>
      <a class="btn ghost" href="./tools/site_config.json">site_config.json</a>
      <a class="btn ghost" href="./tools/delivery_report.json">delivery_report.json</a></p>
    <h3 class="mt2">设计参考</h3><ul class="clean">__BASIS__</ul></section>

  <section class="section-sm"><h2>五、交付文件与重建顺序</h2>
    <div class="grid g2"><div class="card"><h3>交付文件</h3><ul class="clean small">__ARTS__</ul></div>
    <div class="card"><h3>幂等重建顺序</h3><ol class="clean small">__ORDER__</ol></div></div>
    <h3 class="mt2">边界与说明</h3><ul class="clean small">__NOTES__</ul></section>
</main>
<footer class="footer"><div class="wrap"><div class="cols"><div><h4>核心模块</h4><p class="small">
<a href="./实操训练.html">实操训练 · 72 题</a> · <a href="./理论考试.html">理论考试 · 781 题</a> ·
<a href="./考试模拟系统/index.html">模拟考试</a></p></div><div><h4>交付物</h4><p class="small">
<a href="./整站内容配置.html">整站内容配置</a> · <a href="./练习素材/索引.html">素材与交付校验索引</a></p></div>
<div><h4>说明</h4><p class="small">__DISC__</p></div></div>
<div class="disc">© 大连财经学院 · 计算机国家二级考试（WPS 类）课程组 ｜ 非官方考试网站</div></div></footer>
</body></html>"""
    rep = {
        '__NAV__': site_nav.render_primary('核查与重构报告.html'),
        '__SUBNAV__': site_nav.render_subnav('核查与重构报告.html'),
        '__VER__': CFG['config_version'], '__ROWS__': rows,
        '__SCOPE__': SYL['scope_note']['ops'] + '；' + SYL['scope_note']['theory'],
        '__NFIX__': str(len(FIXES)), '__FIXES__': fixes,
        '__OWN__': TH['ownership_note'], '__NAVS__': navs, '__SECS__': secs,
        '__TIERS__': tiers, '__BASIS__': basis,
        '__ARTS__': arts, '__ORDER__': order, '__NOTES__': notes,
        '__DISC__': CFG['site']['disclaimer'],
    }
    for k, val in rep.items():
        html = html.replace(k, val)
    (ROOT / '核查与重构报告.html').write_text(html, encoding='utf-8')


def main():
    r = build_json()
    build_html(r)
    print('核查与重构报告：核查与重构报告.html')
    print('机器可读清单：tools/delivery_report.json')
    print('  修正清单 %d 项 ｜ 核查结论 %d 项 ｜ 大纲 %s ｜ 交付校验 %s' %
          (len(r['fixes']), len(verdict_rows()), r['verdict']['syllabus_items'],
           r['verdict']['delivery_checks']))


if __name__ == '__main__':
    main()
