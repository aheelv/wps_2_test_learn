# -*- coding: utf-8 -*-
"""全站核查：WPS 教育考试专用版范围 / 2025 大纲覆盖 / 版本口径 / 表述准确性。

扫描范围：根目录全部页面、assets 里的课程数据 JS 与界面图 SVG、
练习素材说明与完成比对文档、考试模拟系统、以及 11-6 理论题库数据。

用法：
  python tools/site_audit.py              # 结构化结论（不打印原文）
  python tools/site_audit.py --report     # 写 tools/site_audit_report.json
  python tools/site_audit.py --detail     # 打印命中位置（文件:行号:规则，仍不打印整段原文）
"""
import re, sys, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools' / 'material'))
import audit_steps  # 13 类教育版功能边界规则

PAGES = sorted(ROOT.glob('*.html'))
EXTRA = [ROOT / '考试模拟系统' / 'index.html', ROOT / '11-6' / 'index.html',
         ROOT / '11-6' / 'build' / 'quiz_template.html',
         ROOT / '理论题库' / 'index.html', ROOT / '理论题库' / 'README.txt',
         ROOT / '练习素材' / '索引.html', ROOT / '练习素材' / 'README.txt']
EXTRA += sorted((ROOT / 'assets').glob('*.js'))
EXTRA += sorted((ROOT / 'assets' / 'wps-img').glob('*.svg'))
EXTRA += sorted((ROOT / '练习素材').glob('练习*/素材说明.txt'))
EXTRA += sorted((ROOT / '练习素材' / '完成比对').glob('*/完成比对文档.html'))
FILES = [p for p in PAGES + EXTRA if p.exists()]

# 操作类内容：必须严格落在教育考试专用版离线功能集内
OPS_HINT = ('入门实操课.html', '实操-', '实操训练.html', '练习素材', '完成比对')
# 概念类内容：讲考纲概念（云/共享/WPS 首页）属正常，只查版本口径与表述
CONCEPT_HINT = ('11-6', '考试介绍.html', '考纲对照表.html', '教学大纲.html',
                '教学日历.html', '教案.html', '资料汇编.html', '考试模拟系统')

VERSION_RULES = [
    ('VER_NUM', r'12\.x|12\.1\.|11\.1\.|\bWPS\s?Office\s?20\d{2}\b'),
    ('VER_OLD', r'WPS\s?(?:2010|2013|2016|2019)|旧版\s*WPS'),
    ('VER_EDITION', r'个人版|企业版|专业版|免费版'),
    ('VER_MIX', r'部分版本|不同版本|较新版本|视版本而定|版本差异|新版才有|部分版本叫'),
    ('MSO_NAME', r'Word\s*文件\(\*\.docx\)|Excel\s*工作簿\(\*\.xlsx\)|'
                 r'或\s*PowerPoint|与\s*Excel\s*的区别|Excel\s*名单'),
    ('TAB_OLD', r'「页面布局」|>页面布局</text>|「页面布局\s*→'),
]
# 表述准确性：教育考试专用版现行界面/命令名
WORDING_RULES = [
    ('WORD_VARIANT', r'「变体」|主题变体|变体\s*→'),
    ('WORD_COMPAT', r'检查兼容性|检查问题\s*→|文件\s*→\s*信息\s*→'),
    # 「输出为PDF」是教育考试专用版「文件」菜单的真实命令名，属正确表述（见 ALLOWED_RULES）；
    # 只有把它写成「另存为 / 保存为 PDF」才是旧版 Office 口径，需修正。
    ('WORD_PDF', r'另存为\s*PDF|保存为\s*PDF'),
    ('WORD_VALID', r'「数据验证」|数据验证\s*→'),
    ('WORD_SMOOTH', r'平滑切换|「平滑」'),
    # 用 (?<![\w.]) 排除 JavaScript 的 Array.concat() / 对象方法，避免误报
    ('WORD_NEWFX', r'(?<![\w.])(?:IFS|TEXTJOIN|XLOOKUP|CONCAT)\s*\('),
    ('WORD_TAB', r'「页面布局」选项卡|页面布局\s*选项卡'),
]
# 经核验属于现行考试环境的真实命令名 / 正确概念表述，不计为缺陷，
# 但在报告中单独列出与理由，保证「0 命中」不是靠放宽规则换来的。
ALLOWED_RULES = [
    ('CMD_PDF', r'输出为\s?PDF',
     '教育考试专用版「文件」菜单真实命令名；操作题按此入口输出 PDF，不依赖外部软件'),
    ('CMD_PAGE', r'「页面」选项卡',
     '教育考试专用版现行功能区页面设置入口（旧称「页面布局」已全部清除）'),
]

# 考纲条目（2025 年版，四大模块 + 公共基础）——用于覆盖判定
SYLLABUS = [
    ('WPS 综合应用基础', r'WPS\s*首页|WPS\s*Office\s*基础|综合应用基础|文件\s*基础|基础\s*知识'),
    ('公共基础知识', r'公共基础|数据结构|算法|程序设计|软件工程|数据库设计基础'),
    ('WPS 文字：文档基本操作', r'新建|保存|另存|文档加密|输出\s*PDF'),
    ('WPS 文字：文本编辑与格式', r'字体|段落|样式|项目符号|编号|查找替换'),
    ('WPS 文字：页面与长文档', r'页眉|页脚|分栏|分页|目录|题注|脚注|邮件合并|审阅|修订'),
    ('WPS 文字：表格与图形', r'表格|图片|形状|艺术字|文本框|环绕'),
    ('WPS 表格：工作簿与数据', r'工作表|单元格|数据验证|有效性|条件格式|填充'),
    ('WPS 表格：公式与函数', r'公式|函数|SUM\s*\(|IF\s*\(|VLOOKUP|引用'),
    ('WPS 表格：数据处理', r'排序|筛选|分类汇总|合并计算|数据透视|模拟分析'),
    ('WPS 表格：图表与输出', r'图表|迷你图|打印区域|打印标题|保护工作表'),
    ('WPS 演示：文稿与母版', r'幻灯片|母版|主题|配色|背景|版式'),
    ('WPS 演示：对象与媒体', r'艺术字|形状|智能图形|图片|表格|图表|音频|视频'),
    ('WPS 演示：动画与放映', r'动画|切换|超链接|放映|排练计时'),
    ('WPS 演示：输出与检查', r'打包|输出|密码|检查文档'),
]


# 修正清单中的「修订前」必须原样引用旧文案；显式标记历史引文区，
# 扫描时用等长空白替换（保留行号与偏移），其余内容仍按同一套规则严格检查。
QUOTE_RE = re.compile(r'<!--\s*AUDIT-QUOTE-BEGIN\s*-->.*?<!--\s*AUDIT-QUOTE-END\s*-->', re.S)


def strip_quotes(text):
    return QUOTE_RE.sub(lambda m: re.sub(r'[^\n]', ' ', m.group(0)), text)


def in_tag(text, pos):
    """命中位置是否落在 HTML 标签内部（href / src / xmlns 等属性）。

    页面里的官方链接、SVG namespace 属于站点基础设施，不是「解题步骤要求联网」，
    因此 OUT_NET 只统计标签外的可见正文。
    """
    return text.rfind('<', 0, pos) > text.rfind('>', 0, pos)


def scan_file(p):
    """返回 (缺陷, 白名单命中)；元素均为 (规则码, 行号, 命中词)，不保留整段原文。"""
    text = strip_quotes(p.read_text(encoding='utf-8', errors='ignore'))
    ops = any(h in str(p) for h in OPS_HINT)
    out, allow = [], []
    for code, pat in VERSION_RULES + WORDING_RULES:
        for m in re.finditer(pat, text, re.I):
            out.append((code, text.count('\n', 0, m.start()) + 1, m.group(0)[:24]))
    for code, pat, _why in ALLOWED_RULES:
        for m in re.finditer(pat, text, re.I):
            allow.append((code, text.count('\n', 0, m.start()) + 1, m.group(0)[:24]))
    if ops:
        for code, _desc, pat in audit_steps.RULES:
            for m in re.finditer(pat, text, re.I):
                if code == 'NET' and in_tag(text, m.start()):
                    continue
                out.append(('OUT_' + code, text.count('\n', 0, m.start()) + 1,
                            m.group(0)[:24]))
    return out, allow


def coverage():
    import audit_coverage
    rows, gaps, outside, mix = audit_coverage.collect()
    quiz = json.load(open(ROOT / '11-6' / 'quiz_data.json', encoding='utf-8'))
    sections = {s['name']: len(s['questions']) for s in quiz}
    return dict(points=len(rows), covered=len(rows) - len(gaps),
                gaps=[g['point'] for g in gaps], outside=len(outside), mix=len(mix),
                quiz_sections=sections, quiz_total=sum(sections.values()))


def verdicts(cov):
    """把「逐题合规 / 知识点覆盖 / 官方大纲覆盖 / 理论题库」合并为可交付结论。"""
    import audit_steps
    qs = audit_steps.load()
    bad = sum(len(audit_steps.scan(q)) for q in qs)
    syl = json.load(open(ROOT / 'tools' / 'syllabus_coverage.json', encoding='utf-8'))
    return dict(
        ops_questions=len(qs),
        ops_out_of_scope=bad,
        ops_knowledge_points='%d / %d' % (cov['covered'], cov['points']),
        ops_knowledge_gaps=cov['gaps'],
        ops_outside_questions=cov['outside'],
        version_mix=cov['mix'],
        syllabus_items='%d / %d' % (syl['covered'], syl['total']),
        syllabus_gaps=syl['gaps'],
        theory_sections=cov['quiz_sections'],
        theory_total=cov['quiz_total'],
        theory_scope=syl['scope_note'],
        software='WPS Office 教育考试专用版（2025 年版考试大纲指定考试环境）',
    )


def main():
    hits, allowed = {}, {}
    for p in FILES:
        h, a = scan_file(p)
        if h:
            hits[str(p.relative_to(ROOT))] = h
        if a:
            allowed[str(p.relative_to(ROOT))] = a
    from collections import Counter
    c = Counter(x[0] for h in hits.values() for x in h)
    ca = Counter(x[0] for a in allowed.values() for x in a)
    cov = coverage()
    v = verdicts(cov)
    print('扫描文件 %d 个 ｜ 缺陷命中 %d 处 ｜ 白名单（现行命令名）%d 处' %
          (len(FILES), sum(len(h) for h in hits.values()), sum(len(a) for a in allowed.values())))
    for k, n in c.most_common():
        print('  %-18s %d' % (k, n))
    print('\n按文件（缺陷）：')
    for f, h in sorted(hits.items(), key=lambda x: -len(x[1]))[:20]:
        print('  %-46s %d' % (f, len(h)))
    print('\n逐题合规：%d 题 / %d 处越界 ｜ 知识点 %s ｜ 大纲 %s ｜ 理论题 %d' %
          (v['ops_questions'], v['ops_out_of_scope'], v['ops_knowledge_points'],
           v['syllabus_items'], v['theory_total']))
    if '--detail' in sys.argv:
        for f, h in sorted(hits.items()):
            for code, line, word in h[:14]:
                print('  %-44s L%-6d %-16s %s' % (f, line, code, word))
    if '--report' in sys.argv:
        json.dump(dict(
            files=len(FILES),
            defects={f: [dict(rule=a, line=b, word=c) for a, b, c in h]
                     for f, h in hits.items()},
            summary=dict(c),
            allowed=dict(
                reasons={code: why for code, _pat, why in ALLOWED_RULES},
                summary=dict(ca),
                files={f: [dict(rule=a, line=b, word=c) for a, b, c in h]
                       for f, h in allowed.items()}),
            coverage=cov,
            verdict=v,
            rule_scope=dict(
                ops='操作题正文：必须落在离线教育考试专用版功能集内',
                concept='理论题与考试介绍：按 2025 大纲允许出现 PDF 处理、在线办公等概念题',
                version='全站：组件名 / 命令名 / 选项卡名按教育考试专用版统一，无小版本号与旧版称谓',
            ),
        ), open(ROOT / 'tools' / 'site_audit_report.json', 'w', encoding='utf-8'),
            ensure_ascii=False, indent=1)
    return len(hits)


if __name__ == '__main__':
    main()
