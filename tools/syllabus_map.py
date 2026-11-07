# -*- coding: utf-8 -*-
"""按《NCRE 二级 WPS Office 高级应用与设计考试大纲（2025 年版）》28 条考试内容，
建立「大纲条目 → 实操 72 题 + 理论 781 题」的覆盖矩阵。

口径说明（重要）：
  · 操作题（80 分）：考场为离线、无账号的 WPS Office 教育考试专用版，
    解题步骤不得依赖云端 / AI / 插件 / 宏等不可执行功能；
  · 单项选择题（20 分，含公共基础 10 分）：大纲「一、WPS 综合应用基础」明确要求
    掌握「PDF 的阅读、批注、编辑、处理、保护、转换」与「WPS 在线办公概念、
    文档上云、共享协作、创新应用」，因此理论题中出现云 / 共享 / 在线办公属考纲范围，
    不按操作越界处理；
  · 「公共基础知识」按《二级公共基础知识考试大纲（2025 年版）》单列。

输出：tools/syllabus_coverage.json
用法：python tools/syllabus_map.py
"""
import re, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
E = json.load(open(ROOT / 'tools/material/exercises.json', encoding='utf-8'))
QUIZ = json.load(open(ROOT / '11-6/quiz_data.json', encoding='utf-8'))

# (模块, 条目, 检索式)。条目文字与考试介绍.html 的官方条目一致。
ITEMS = [
    ('一、WPS 综合应用基础', 'WPS 功能界面和窗口视图设置',
     r'功能界面|窗口视图|导航窗格|视图模式|功能区|选项卡|界面'),
    ('一、WPS 综合应用基础', '文件的新建、保存、加密、打印等基本操作',
     r'新建|保存|另存|加密|打印|打开密码|文档加密|只读'),
    ('一、WPS 综合应用基础', 'PDF 的阅读、批注、编辑、处理、保护、转换等操作',
     r'PDF|版式文档|输出为\s*PDF|转换'),
    ('一、WPS 综合应用基础', 'WPS 在线办公概念，文档上云、共享协作、创新应用',
     r'在线办公|上云|云文档|共享|协作|协同|WPS\s*首页|创新应用|多人'),
    ('二、WPS 处理文字文档', '文档创建、输入编辑、查找替换、打印等基础操作',
     r'新建|录入|输入|查找|替换|选定|复制|撤销|打印'),
    ('二、WPS 处理文字文档', '字体段落格式、样式主题、页面布局等排版操作',
     r'字体|字号|段落|行距|缩进|样式|主题|页边距|页面设置|A4'),
    ('二、WPS 处理文字文档', '文档中表格的制作与编辑',
     r'插入表格|表格属性|单元格|表格样式|表头|表格'),
    ('二、WPS 处理文字文档', '图形图像对象、文本框、文档部件、符号与数学公式',
     r'图片|形状|文本框|艺术字|符号|公式|环绕|裁剪|文档部件'),
    ('二、WPS 处理文字文档', '分栏分页分节、页眉页脚、文档内容引用',
     r'分栏|分页|分节|分隔符|页眉|页脚|页码|题注|交叉引用|目录|脚注|索引'),
    ('二、WPS 处理文字文档', '文档审阅和修订',
     r'审阅|修订|批注|比较文档|接受修订|限制编辑'),
    ('二、WPS 处理文字文档', '利用邮件合并批量制作和处理文档',
     r'邮件合并|主文档|数据源|合并域'),
    ('二、WPS 处理文字文档', '多窗口和多文档编辑，文档视图的使用',
     r'多窗口|并排|多文档|视图|导航窗格|拆分'),
    ('二、WPS 处理文字文档', '分析图文素材并提取信息引用到 WPS 文字文档',
     r'素材|提取|引用到|综合题|按要求|自拟'),
    ('三、WPS 处理数据表格', '工作簿和工作表基本操作、视图控制、打印和输出',
     r'工作簿|工作表|视图|打印区域|打印标题|打印|冻结'),
    ('三、WPS 处理数据表格', '数据输入编辑、单元格格式化、数据格式设置',
     r'数据验证|有效性|单元格格式|条件格式|数字格式|百分比|边框|填充'),
    ('三、WPS 处理数据表格', '排序筛选对比、分类汇总、合并计算、有效性和模拟分析',
     r'排序|筛选|分类汇总|合并计算|模拟分析|方案|有效性|对比'),
    ('三、WPS 处理数据表格', '单元格引用、公式、函数和数组的使用',
     r'公式|函数|引用|数组|SUM\s*\(|IF\s*\(|VLOOKUP|COUNTIF'),
    ('三、WPS 处理数据表格', '图表的创建、编辑与修饰',
     r'图表|柱形|折线|饼图|迷你图|次坐标轴|数据系列'),
    ('三、WPS 处理数据表格', '数据透视表和数据透视图的使用',
     r'数据透视|透视图|切片器|值字段|行标签'),
    ('三、WPS 处理数据表格', '工作簿和工作表的安全性与跟踪协作',
     r'保护工作表|保护工作簿|安全性|跟踪|共享工作簿|密码'),
    ('三、WPS 处理数据表格', '多个工作表的联动操作',
     r'联动|多工作表|跨表|合并计算|三维引用|Sheet\d'),
    ('三、WPS 处理数据表格', '分析数据素材并提取信息引用到 WPS 表格文档',
     r'素材|提取|引用到|按要求|自拟'),
    ('四、WPS 设计演示文稿', '演示文稿基本操作、幻灯片组织管理、视图模式',
     r'幻灯片|版式|视图|组织|管理|新建演示'),
    ('四、WPS 设计演示文稿', '主题应用、背景设置、母版制作和使用',
     r'主题|配色|背景|母版|字体方案|渐变'),
    ('四、WPS 设计演示文稿', '文本艺术字图形智能图形图像图表音频视频对象',
     r'艺术字|形状|智能图形|图片|图表|音频|视频|文本框|媒体'),
    ('四、WPS 设计演示文稿', '对象动画、幻灯片切换效果、链接操作等交互设置',
     r'动画|切换|超链接|动作|触发器|交互|排练计时'),
    ('四、WPS 设计演示文稿', '幻灯片放映设置，演示文稿的打包和输出',
     r'放映|打包|输出|检查文档|标记为最终状态|密码'),
    ('四、WPS 设计演示文稿', '分析图文素材并提取信息引用到 WPS 演示文档',
     r'素材|提取|引用到|综合题|汇报|按要求'),
]


def ops_text():
    out = []
    for q in E:
        t = ' '.join([q['title']] + q['reqs'] + q['steps'] + [q['score'] or ''])
        out.append(('%s(c%d-%d)' % (q['no'], q['ci'], q['seq']), t))
    return out


def theory_text():
    out = []
    for s in QUIZ:
        for q in s['questions']:
            t = ' '.join([q.get('q', '')] + list(q.get('o', [])))
            out.append(('%s#%s' % (s['name'], q.get('no')), t))
    return out


def main():
    ops, theory = ops_text(), theory_text()
    rows = []
    for mod, item, pat in ITEMS:
        rx = re.compile(pat, re.I)
        o = [n for n, t in ops if rx.search(t)]
        th = [n for n, t in theory if rx.search(t)]
        rows.append(dict(module=mod, item=item, pattern=pat,
                         ops=len(o), theory=len(th),
                         ops_sample=o[:3], theory_sample=th[:3],
                         verdict='COVERED' if (o or th) else 'GAP'))
    gaps = [r for r in rows if r['verdict'] == 'GAP']
    from collections import Counter
    cm = Counter(r['module'] for r in rows)
    cc = Counter(r['module'] for r in rows if r['verdict'] == 'COVERED')
    print('官方大纲条目 %d 条 ｜ 已覆盖 %d 条 ｜ 缺漏 %d 条' %
          (len(rows), len(rows) - len(gaps), len(gaps)))
    for m in cm:
        print('  %-18s %d / %d' % (m, cc[m], cm[m]))
    print('实操 72 题覆盖条目 %d ｜ 理论 781 题覆盖条目 %d' %
          (sum(1 for r in rows if r['ops']), sum(1 for r in rows if r['theory'])))
    for g in gaps:
        print('  [缺漏] %s ｜ %s' % (g['module'], g['item']))
    print('\n实操题覆盖为 0、仅由理论题覆盖的条目（属单选范围，正常）：')
    for r in rows:
        if not r['ops'] and r['theory']:
            print('  %-18s %-38s 理论 %3d 题' % (r['module'][:2], r['item'][:36], r['theory']))
    rep = dict(total=len(rows), covered=len(rows) - len(gaps),
               gaps=[r['item'] for r in gaps], rows=rows,
               scope_note=dict(
                   ops='操作题 80 分：离线 WPS Office 教育考试专用版，步骤不得依赖云端/AI/插件/宏',
                   theory='单选 20 分（含公共基础 10 分）：大纲明确含 PDF 处理与在线办公概念',
                   source='NCRE 二级 WPS Office 高级应用与设计考试大纲（2025 年版）'))
    (ROOT / 'tools' / 'syllabus_coverage.json').write_text(
        json.dumps(rep, ensure_ascii=False, indent=1), encoding='utf-8')
    return len(gaps)


if __name__ == '__main__':
    sys.exit(0 if main() == 0 else 1)
