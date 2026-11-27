# -*- coding: utf-8 -*-
"""从网站现有数据源生成「WPS 国家二级考试知识图谱」数据。

数据源：
  assets/curriculum.js            课程知识点 / 考试要点 / 讲解
  tools/_questions_extract.json   120 道单选题（题干 / 选项 / 答案 / 解析）
  tools/material/exercises.json   72 道实操题（题号 / 页面 / 要求 / 步骤 / 采分点）
  assets/knowledge-data.js        72 题逐题背景知识（原理 / 公式 / 例题 / 易错 / 考法）

输出：
  assets/knowledge-graph-data.js  window.KNOWLEDGE_GRAPH = {...}

结构：模块(module) → 知识域(domain) → 知识点(point)。
每个知识点含：brief 聚焦要点 / detail 去重讲解 / points 考点清单 /
difficulty 易错提醒 / questions 唯一挂载的理论题 / practicalKeys 关联操作题。
操作题只存一份在 data.practicals，节点通过 key 引用，避免 72 题内容重复膨胀。
"""
import collections
import html
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]


def load_js_object(path, var):
    text = (ROOT / path).read_text(encoding='utf-8')
    m = re.search(r'window\.' + re.escape(var) + r'\s*=\s*(\{.*\})\s*;?\s*$', text, re.S)
    if not m:
        raise SystemExit('无法解析 %s 中的 window.%s' % (path, var))
    return json.loads(m.group(1))


cur = load_js_object('assets/curriculum.js', 'CURRICULUM')
kb = load_js_object('assets/knowledge-data.js', 'WPS_KNOWLEDGE')
exercises = json.loads((ROOT / 'tools/material/exercises.json').read_text(encoding='utf-8'))
questions = json.loads((ROOT / 'tools/_questions_extract.json').read_text(encoding='utf-8'))

EX_BY_KEY = {'%d-%d' % (e['ci'], e['seq']): e for e in exercises}

# ---------- 模块 → 知识域定义 ----------
DOMAIN_DEF = {
    'M1': [
        ('D-PC',   '计算机系统与信息表示', ['计算机系统', '冯·诺依曼', '数制', '编码', '存储', 'CPU', '输入输出', '性能指标']),
        ('D-NET',  '网络与信息安全', ['网络', 'Internet', 'TCP', 'IP', '病毒', '安全', '协议']),
        ('D-DS',   '数据结构与算法', ['数据结构', '线性表', '栈', '队列', '二叉树', '查找', '排序', '算法', '复杂度']),
        ('D-PROG', '程序设计基础', ['程序设计', '结构化', '面向对象']),
        ('D-SE',   '软件工程与数据库', ['软件工程', '数据库', '数据流图', 'E-R', '测试', 'DB']),
        ('D-OA',   'WPS 综合应用', ['WPS 综合', '快捷键', '文件格式', 'PDF', '界面', '窗口', '输出']),
    ],
    'M2': [
        ('D-W-BASE', '文档基础与编辑', ['创建', '编辑', '查找替换', '打印', '符号', '多窗口']),
        ('D-W-FMT',  '字体段落与样式', ['字体', '段落', '样式', '主题', '页面', '边框', '底纹', '分栏', '首字下沉']),
        ('D-W-TBL',  '表格制作与编辑', ['表格制作', '表格编辑', '合并单元格', '表格公式']),
        ('D-W-GFX',  '图形图像与文本框', ['图形', '图像', '图片', '文本框', '公式编辑器', '文档部件']),
        ('D-W-REF',  '页面引用与长文档', ['页眉', '页脚', '页码', '分节', '目录', '题注', '脚注', '索引', '引用']),
        ('D-W-REV',  '审阅修订与邮件合并', ['审阅', '修订', '批注', '邮件合并', '比较', '保护']),
    ],
    'M3': [
        ('D-S-BASE', '工作簿与工作表', ['工作簿', '工作表', '单元格', '视图', '打印', '页面']),
        ('D-S-FMT',  '数据输入与单元格格式', ['输入', '格式', '有效性', '条件格式', '自定义格式']),
        ('D-S-FUNC', '公式引用与函数', ['公式', '函数', '引用', 'IF', 'SUM', 'VLOOKUP', '查找', '统计']),
        ('D-S-DATA', '排序筛选与汇总', ['排序', '筛选', '分类汇总', '合并计算', '模拟分析']),
        ('D-S-CHART','图表与透视表', ['图表', '数据透视', '透视图', '切片器', '迷你图']),
        ('D-S-SAFE', '安全性与多表联动', ['安全', '保护', '加密', '联动', '协作', '共享']),
    ],
    'M4': [
        ('D-P-BASE', '演示文稿基础与视图', ['幻灯片', '视图', '大纲', '备注', '版式', '组织']),
        ('D-P-THEME','主题背景与母版', ['主题', '背景', '母版', '配色', '版式']),
        ('D-P-OBJ',  '文本图形图表与媒体', ['艺术字', '图形', '智能图形', '图片', '图表', '音频', '视频', '文本']),
        ('D-P-ANIM', '动画切换与交互', ['动画', '切换', '超链接', '动作', '交互']),
        ('D-P-SHOW', '放映打包与输出', ['放映', '打包', '输出', 'PDF', '打印']),
    ],
    'M5': [
        ('D-M-MOCK', '全真模拟与综合冲刺', ['模拟', '综合', '真题', '冲刺', '错题']),
    ],
}

# 课时归属纠偏：原关键词匹配把「表格制作」误归到字体段落域，
# 把「邮件合并」误归到文档基础域。按课时号显式指定，确保 24 个知识域都有内容。
DOMAIN_OVERRIDE = {
    9: 'D-W-BASE', 10: 'D-W-FMT', 11: 'D-W-FMT', 12: 'D-W-REF',
    13: 'D-W-REF', 14: 'D-W-TBL', 15: 'D-W-GFX', 16: 'D-W-GFX',
    17: 'D-W-REF', 18: 'D-W-REV', 19: 'D-W-REV', 20: 'D-W-BASE',
    21: 'D-S-BASE', 22: 'D-S-FMT', 23: 'D-S-FUNC', 24: 'D-S-FUNC',
    25: 'D-S-FUNC', 26: 'D-S-FUNC', 27: 'D-S-FUNC', 28: 'D-S-DATA',
    29: 'D-S-DATA', 30: 'D-S-CHART', 31: 'D-S-CHART', 32: 'D-S-SAFE',
    33: 'D-P-BASE', 34: 'D-P-THEME', 35: 'D-P-OBJ', 36: 'D-P-OBJ',
    37: 'D-P-ANIM', 38: 'D-P-ANIM', 39: 'D-P-SHOW', 40: 'D-P-SHOW',
}

# 72 道操作题 → 知识点。按题目的实际考点挂载，不按课次机械平均分配。
PRACTICAL_POINTS = {
    '1-1':  ['P-M1-8-1', 'P-M2-9-2'],
    '1-2':  ['P-M2-10-1', 'P-M2-16-2'],
    '1-3':  ['P-M2-9-1'],
    '1-4':  ['P-M1-8-2', 'P-M2-9-2', 'P-M2-12-1'],
    '1-5':  ['P-M2-10-1', 'P-M2-10-2'],
    '1-6':  ['P-M2-10-2'],
    '1-7':  ['P-M2-10-1'],
    '1-8':  ['P-M2-10-2'],
    '1-9':  ['P-M2-11-1', 'P-M2-11-2'],
    '1-10': ['P-M2-9-1'],
    '1-11': ['P-M2-12-1'],
    '1-12': ['P-M2-12-1'],
    '1-13': ['P-M2-12-2', 'P-M2-13-1', 'P-M2-13-2'],
    '1-14': ['P-M2-14-1', 'P-M2-14-2', 'P-M2-17-1'],
    '1-15': ['P-M2-15-1', 'P-M2-16-1'],
    '1-16': ['P-M2-11-1', 'P-M2-10-2', 'P-M2-14-1', 'P-M2-17-1', 'P-M5-42-1'],
    '2-1':  ['P-M2-13-1', 'P-M2-12-1'],
    '2-2':  ['P-M2-12-2', 'P-M2-13-1', 'P-M2-13-2'],
    '2-3':  ['P-M2-14-1', 'P-M2-14-2'],
    '2-4':  ['P-M2-14-2'],
    '2-5':  ['P-M2-15-1', 'P-M2-15-2', 'P-M2-16-1'],
    '2-6':  ['P-M2-15-1', 'P-M2-15-2'],
    '2-7':  ['P-M2-16-1', 'P-M2-16-2', 'P-M2-13-1'],
    '2-8':  ['P-M2-16-2', 'P-M2-15-1', 'P-M2-17-1'],
    '3-1':  ['P-M2-11-1', 'P-M2-11-2', 'P-M2-17-1'],
    '3-2':  ['P-M2-17-1', 'P-M2-17-2'],
    '3-3':  ['P-M2-17-2'],
    '3-4':  ['P-M2-17-2'],
    '3-5':  ['P-M2-18-1', 'P-M1-8-3'],
    '3-6':  ['P-M2-18-2', 'P-M1-8-2'],
    '3-7':  ['P-M2-19-1', 'P-M2-19-2', 'P-M5-42-2'],
    '3-8':  ['P-M2-20-1', 'P-M2-20-2', 'P-M2-17-1'],
    '4-1':  ['P-M3-21-1', 'P-M3-21-2'],
    '4-2':  ['P-M3-21-2', 'P-M1-8-2'],
    '4-3':  ['P-M3-22-1', 'P-M3-22-2', 'P-M3-29-2'],
    '4-4':  ['P-M3-22-2'],
    '4-5':  ['P-M3-23-1', 'P-M3-23-2'],
    '4-6':  ['P-M3-23-1', 'P-M3-24-3', 'P-M5-43-1'],
    '4-7':  ['P-M3-24-1', 'P-M3-24-2'],
    '4-8':  ['P-M3-24-3', 'P-M3-24-2'],
    '5-1':  ['P-M3-25-1'],
    '5-2':  ['P-M3-25-2', 'P-M3-23-2'],
    '5-3':  ['P-M3-26-1', 'P-M3-26-2', 'P-M3-24-3'],
    '5-4':  ['P-M3-26-2'],
    '5-5':  ['P-M3-27-1', 'P-M3-27-2', 'P-M3-24-1'],
    '5-6':  ['P-M3-24-2', 'P-M3-27-2'],
    '5-7':  ['P-M3-28-1'],
    '5-8':  ['P-M3-28-2'],
    '6-1':  ['P-M3-29-1'],
    '6-2':  ['P-M3-29-1', 'P-M3-29-2'],
    '6-3':  ['P-M3-30-1'],
    '6-4':  ['P-M3-30-2', 'P-M3-30-1'],
    '6-5':  ['P-M3-31-1', 'P-M5-43-2'],
    '6-6':  ['P-M3-31-2', 'P-M3-31-1'],
    '6-7':  ['P-M3-32-1'],
    '6-8':  ['P-M3-32-2', 'P-M3-32-3'],
    '7-1':  ['P-M4-33-1', 'P-M4-33-2'],
    '7-2':  ['P-M4-33-2'],
    '7-3':  ['P-M4-34-1'],
    '7-4':  ['P-M4-34-2', 'P-M4-34-1'],
    '7-5':  ['P-M4-35-1'],
    '7-6':  ['P-M4-35-2', 'P-M4-35-1'],
    '7-7':  ['P-M4-36-1'],
    '7-8':  ['P-M4-36-1', 'P-M4-36-2'],
    '8-1':  ['P-M4-37-1', 'P-M4-37-2'],
    '8-2':  ['P-M4-37-2', 'P-M4-38-2'],
    '8-3':  ['P-M4-38-1'],
    '8-4':  ['P-M4-38-2', 'P-M4-33-2'],
    '8-5':  ['P-M4-39-1', 'P-M4-39-2'],
    '8-6':  ['P-M4-39-1', 'P-M1-8-2'],
    '8-7':  ['P-M4-40-1', 'P-M4-40-2', 'P-M4-34-1', 'P-M4-37-1', 'P-M5-44-1'],
    '8-8':  ['P-M4-40-2', 'P-M5-41-2', 'P-M5-44-2'],
}

# 单选题按 topic 精确挂载，避免旧版按宽泛关键词把 6 道题重复分给同一课时多个节点。
TOPIC_POINT = {
    # 公共基础
    '计算机系统 · 存储容量单位': 'P-M1-1-2', '计算机系统 · CPU 组成': 'P-M1-1-1',
    '计算机系统 · 存储器': 'P-M1-1-1', '计算机系统 · 数制转换': 'P-M1-1-3',
    '计算机系统 · 冯·诺依曼结构': 'P-M1-1-1', '计算机系统 · 字符编码': 'P-M1-1-2',
    '计算机系统 · 输入输出设备': 'P-M1-1-1', '计算机系统 · 系统组成': 'P-M1-1-1',
    '计算机系统 · 性能指标': 'P-M1-1-2', '算法 · 时间复杂度': 'P-M1-3-1',
    '数据结构 · 线性链表': 'P-M1-4-2', '数据结构 · 栈': 'P-M1-4-1',
    '数据结构 · 队列': 'P-M1-4-1', '数据结构 · 二叉树性质': 'P-M1-5-1',
    '数据结构 · 二叉树遍历': 'P-M1-5-1', '算法 · 二分查找': 'P-M1-5-2',
    '算法 · 冒泡排序': 'P-M1-5-2', '算法 · 顺序查找': 'P-M1-5-2',
    '算法 · 基本特征': 'P-M1-3-1', '数据结构 · 基本概念': 'P-M1-3-2',
    '数据结构 · 循环队列': 'P-M1-4-2', '算法 · 排序复杂度': 'P-M1-5-2',
    '程序设计 · 结构化': 'P-M1-6-1', '程序设计 · 结构化原则': 'P-M1-6-1',
    '程序设计 · 封装': 'P-M1-6-1', '程序设计 · 继承': 'P-M1-6-1',
    '程序设计 · 多态': 'P-M1-6-1', '程序设计 · 类与对象': 'P-M1-6-1',
    '程序设计 · 消息': 'P-M1-6-1', '程序设计 · 类': 'P-M1-6-1',
    '软件工程 · 软件生命周期': 'P-M1-6-2', '软件工程 · 需求分析': 'P-M1-6-2',
    '软件工程 · 结构化分析': 'P-M1-6-2', '软件工程 · 模块独立性': 'P-M1-6-2',
    '软件工程 · 白盒测试': 'P-M1-6-2', '软件工程 · 黑盒测试': 'P-M1-6-2',
    '软件工程 · 软件测试': 'P-M1-6-2', '软件工程 · 程序调试': 'P-M1-6-2',
    '软件工程 · 详细设计': 'P-M1-6-2', '软件工程 · 软件设计': 'P-M1-6-2',
    '数据库 · 三级模式': 'P-M1-7-2', '数据库 · E-R 图': 'P-M1-7-1',
    '数据库 · 关系模型': 'P-M1-7-1', '数据库 · 规范化': 'P-M1-7-2',
    '数据库 · 范式': 'P-M1-7-2', '数据库 · 关系代数': 'P-M1-7-1',
    # WPS 综合
    'WPS 综合 · 文件格式': 'P-M1-8-1', 'WPS 综合 · 常用快捷键': 'P-M1-8-1',
    'WPS 综合 · 文档加密': 'P-M1-8-2', 'WPS 综合 · PDF': 'P-M1-8-2',
    'WPS 综合 · 云文档协作': 'P-M1-8-1', 'WPS 综合 · 共享协作': 'P-M1-8-1',
    'WPS 综合 · 版本管理': 'P-M1-8-1', 'WPS 综合 · 导出 PDF': 'P-M1-8-2',
    'WPS 综合 · 备份与恢复': 'P-M1-8-1', 'WPS 综合 · 兼容性': 'P-M1-8-1',
    'WPS 综合 · 文件保存': 'P-M1-8-1', 'WPS 综合 · 在线办公': 'P-M1-8-1',
    'WPS 文字 · 视图': 'P-M2-20-1', 'WPS 演示 · 视图': 'P-M4-33-2',
    # WPS 文字
    'WPS 文字 · 段落缩进': 'P-M2-10-2', 'WPS 文字 · 行距': 'P-M2-10-2',
    'WPS 文字 · 多级列表': 'P-M2-10-2', 'WPS 文字 · 样式': 'P-M2-11-1',
    'WPS 文字 · 目录': 'P-M2-17-1', 'WPS 文字 · 目录更新': 'P-M2-17-1',
    'WPS 文字 · 分节': 'P-M2-12-2', 'WPS 文字 · 页眉分节': 'P-M2-12-2',
    'WPS 文字 · 页眉页脚': 'P-M2-13-1', 'WPS 文字 · 邮件合并': 'P-M2-19-1',
    'WPS 文字 · 审阅修订': 'P-M2-18-1', 'WPS 文字 · 脚注尾注': 'P-M2-17-2',
    'WPS 文字 · 表格操作': 'P-M2-14-1', 'WPS 文字 · 表格公式': 'P-M2-14-2',
    'WPS 文字 · 题注与交叉引用': 'P-M2-17-1', 'WPS 文字 · 查找替换': 'P-M2-9-1',
    'WPS 文字 · 页面设置': 'P-M2-12-1', 'WPS 文字 · 文本框': 'P-M2-16-1',
    # WPS 表格
    'WPS 表格 · 单元格引用': 'P-M3-23-1', 'WPS 表格 · 混合引用': 'P-M3-23-1',
    'WPS 表格 · 跨表引用': 'P-M3-23-2', 'WPS 表格 · IFERROR': 'P-M3-23-1',
    'WPS 表格 · VLOOKUP': 'P-M3-25-1', 'WPS 表格 · SUMIF': 'P-M3-27-1',
    'WPS 表格 · COUNTIF': 'P-M3-27-2', 'WPS 表格 · COUNTIFS': 'P-M3-27-2',
    'WPS 表格 · INDEX 与 MATCH': 'P-M3-25-2', 'WPS 表格 · 数组公式': 'P-M3-27-1',
    'WPS 表格 · RANK': 'P-M3-24-2', 'WPS 表格 · 分类汇总': 'P-M3-29-1',
    'WPS 表格 · 合并计算': 'P-M3-29-1', 'WPS 表格 · 数据透视表': 'P-M3-31-1',
    'WPS 表格 · 数据有效性': 'P-M3-29-2', 'WPS 表格 · 条件格式': 'P-M3-22-2',
    'WPS 表格 · 图表类型': 'P-M3-30-1', 'WPS 表格 · 冻结窗格': 'P-M3-21-1',
    # WPS 演示
    'WPS 演示 · 母版': 'P-M4-34-2', 'WPS 演示 · 版式': 'P-M4-33-1',
    'WPS 演示 · 主题': 'P-M4-34-1', 'WPS 演示 · 切换与动画': 'P-M4-37-2',
    'WPS 演示 · 动画类型': 'P-M4-37-1', 'WPS 演示 · 动画开始方式': 'P-M4-37-1',
    'WPS 演示 · 动画窗格': 'P-M4-37-1', 'WPS 演示 · 交互设置': 'P-M4-38-1',
    'WPS 演示 · 排练计时': 'P-M4-38-2', 'WPS 演示 · 自定义放映': 'P-M4-38-2',
    'WPS 演示 · 打包输出': 'P-M4-39-1', 'WPS 演示 · 智能图形': 'P-M4-35-2',
    'WPS 演示 · 音频设置': 'P-M4-36-1', 'WPS 演示 · 页眉页脚': 'P-M4-34-2',
}

CAT_MODULE = {'public': 'M1', 'basic': 'M1', 'word': 'M2', 'excel': 'M3', 'ppt': 'M4'}


# ---------- 工具函数 ----------
def clean(s):
    if s is None:
        return ''
    s = re.sub(r'<br\s*/?>', '\n', str(s), flags=re.I)
    s = re.sub(r'<[^>]+>', '', s)
    s = html.unescape(s)
    return re.sub(r'\s+', ' ', s).strip()


def short(s, n):
    s = clean(s)
    if len(s) <= n:
        return s
    cut = s[:n]
    p = max(cut.rfind('。'), cut.rfind('；'), cut.rfind('，'))
    if p > n * 0.6:
        return cut[:p + 1]
    return cut.rstrip('，。；、') + '…'


def match(text, kws):
    t = text.lower()
    return any(k.lower() in t for k in kws)


def anchor_of(ex):
    """锚点以页面展示题号为准：例 5-3 → e5-3，综合题 → e4-4。"""
    m = re.search(r'(\d+)\s*[-－—]\s*(\d+)', ex['no'])
    if m:
        return 'e%s-%s' % (m.group(1), m.group(2))
    if '综合' in ex['no']:
        return 'e4-4'
    return 'e%d-%d' % (ex['ci'], ex['seq'])


def terms_of(node):
    out = []
    for p in node.get('points', []):
        t = clean(p)
        if t:
            out.append(t)
        for x in re.split(r'[：:、,，;；+（）()\-—\s]+', t):
            if len(x) >= 2 and x not in out:
                out.append(x)
    name = clean(node.get('name', ''))
    if name:
        out.append(name)
    return out


def kws_of(defs, mid, did):
    for d in defs.get(mid, []):
        if d[0] == did:
            return d[2]
    return []


def mk_question(q):
    return {
        'id': q['id'], 'topic': q['topic'], 'diff': q.get('diff', ''),
        'q': q['q'], 'opts': q.get('opts', []), 'ans': q.get('ans'),
        'exp': q.get('exp', ''),
    }


def mk_practical(key):
    e = EX_BY_KEY[key]
    k = kb.get(key, {})
    reqs = [clean(x) for x in e.get('reqs', []) if clean(x)]
    steps = [clean(x) for x in e.get('steps', []) if clean(x)]
    explanation = ''.join(
        '【%s】%s' % (label, short(k.get(field, ''), limit))
        for label, field, limit in (
            ('考点', 'points', 190), ('原理', 'principle', 300),
            ('公式与参数', 'formula', 260), ('示例', 'example', 220),
        ) if k.get(field)
    )
    return {
        'key': key,
        'no': e['no'],
        'title': e['title'],
        'page': e['page'],
        'anchor': anchor_of(e),
        'href': './%s#%s' % (e['page'], anchor_of(e)),
        'reqs': reqs,
        'steps': steps[:3],
        'explanation': explanation,
        'mistakes': short(k.get('mistakes', ''), 240),
        'exam': short(k.get('exam', ''), 220),
        'score': clean(e.get('score', '')),
    }


def build():
    modules = {m['id']: m for m in cur['modules']}
    nodes, edges = [], []
    stats = collections.Counter()

    nodes.append({
        'id': 'ROOT', 'type': 'root', 'name': '二级 WPS Office', 'short': 'NCRE 67', 'level': 0,
        'brief': '全国计算机等级考试二级 WPS Office 高级应用与设计（科目代码 67）。',
        'detail': '上机考试 120 分钟，满分 100 分：单选 20 分（含公共基础 10 分）、文字 30 分、表格 30 分、演示 20 分，60 分合格。考试环境为 WPS Office 教育考试专用版。',
        'meta': {'score': '100 分', 'hours': '44 课时'}, 'questions': [], 'practicalKeys': [],
        'links': [
            {'label': '实操训练', 'href': './实操训练.html'},
            {'label': '模拟考试', 'href': './考试模拟系统/index.html'},
        ],
    })

    for mid, m in modules.items():
        nodes.append({
            'id': mid, 'type': 'module', 'name': m['name'], 'short': m.get('short', m['name']),
            'level': 1, 'parent': 'ROOT',
            'brief': clean(m.get('desc', ''))[:400],
            'detail': clean(m.get('desc', '')) + ('\n\n覆盖考纲：' + m.get('syl', '') if m.get('syl') else ''),
            'meta': {'score': m.get('score', ''), 'hours': '%s 课时' % m.get('hours', '')},
            'questions': [], 'practicalKeys': [],
            'links': [
                {'label': '考纲对照', 'href': './考纲对照表.html'},
                {'label': '模拟考试', 'href': './考试模拟系统/index.html'},
            ],
        })
        edges.append({'source': 'ROOT', 'target': mid, 'kind': 'belong'})

        for did, dname, kws in DOMAIN_DEF.get(mid, []):
            nodes.append({
                'id': did, 'type': 'domain', 'name': dname, 'short': dname,
                'level': 2, 'parent': mid, 'brief': '%s · %s' % (dname, m.get('short', '')),
                'detail': '「%s」是%s下的核心知识域，涵盖该方向的高频考点与典型题型。' % (dname, m['name']),
                'meta': {}, 'questions': [], 'practicalKeys': [],
                'links': [{'label': '查看课件', 'href': './培训课件.html'}],
            })
            edges.append({'source': mid, 'target': did, 'kind': 'belong'})

        for lesson in m.get('lessons', []):
            lno = lesson.get('no')
            ltext = ' '.join([
                lesson.get('title', ''),
                ' '.join(lesson.get('obj', [])),
                ' '.join(lesson.get('key', [])),
            ])

            if lno in DOMAIN_OVERRIDE:
                best = DOMAIN_OVERRIDE[lno]
            else:
                best, bestn = None, 0
                for did, dname, kws in DOMAIN_DEF.get(mid, []):
                    n = sum(1 for k in kws if k.lower() in ltext.lower())
                    if n > bestn:
                        best, bestn = did, n
                if best is None:
                    best = DOMAIN_DEF[mid][0][0]

            keys = lesson.get('key', []) or lesson.get('obj', [])
            chunks = [keys[:3], keys[3:6], keys[6:9]]
            chunks = [c for c in chunks if c]
            if not chunks:
                chunks = [['掌握' + lesson.get('title', '')]]

            # 同一课时的幻灯片要点只分配一次，避免「·2」「·3」节点复制整课讲解。
            used_bullets = set()
            for ci, chunk in enumerate(chunks):
                pid = 'P-%s-%s-%d' % (mid, lno, ci + 1)
                pname = lesson.get('title', '') if ci == 0 else '%s · %d' % (lesson.get('title', ''), ci + 1)
                chunk_terms = terms_of({'points': chunk, 'name': pname})
                detail = ['【本节聚焦】%s。' % '；'.join(clean(x) for x in chunk)]

                for sl in lesson.get('slides', []):
                    picked = None
                    for b in (sl.get('b', []) or []):
                        bt = clean(b)
                        if not bt or bt in used_bullets:
                            continue
                        if any(len(t) >= 3 and t in bt for t in chunk_terms):
                            picked = bt
                            used_bullets.add(bt)
                            break
                    if picked:
                        detail.append('【%s】%s' % (clean(sl.get('t', '要点')), picked))
                    if len(detail) >= 4:
                        break

                if len(detail) == 1:
                    detail.append('【考试口径】围绕「%s」辨清概念、适用条件与题目给出的操作对象，避免只凭记忆套步骤。'
                                  % clean(chunk[0]))
                diff = '；'.join(clean(x) for x in (lesson.get('diff', []) or [])[:5])
                if diff:
                    detail.append('【易错提醒】%s' % diff)

                node = {
                    'id': pid, 'type': 'point', 'name': pname[:60], 'short': pname[:22],
                    'level': 3, 'parent': best,
                    'brief': '；'.join(clean(x) for x in chunk[:3])[:220],
                    'detail': '\n'.join(detail[:6]),
                    'points': [clean(x) for x in chunk],
                    'difficulty': diff,
                    'meta': {'lesson': lno, 'hours': lesson.get('hours')},
                    'questions': [], 'practicalKeys': [],
                    'links': [
                        {'label': '查看课件', 'href': './培训课件.html'},
                        {'label': '电子书详解', 'href': './电子书.html'},
                        {'label': '考纲对照', 'href': './考纲对照表.html'},
                    ],
                }
                if mid == 'M1':
                    node['links'].append({'label': '模拟考试', 'href': './考试模拟系统/index.html'})
                nodes.append(node)
                edges.append({'source': best, 'target': pid, 'kind': 'belong'})
                stats[pid.split('-')[1]] += 1

    by_id = {n['id']: n for n in nodes}
    point_nodes = [n for n in nodes if n['type'] == 'point']

    # ---------- 操作题映射 ----------
    practicals = {}
    for key, pids in PRACTICAL_POINTS.items():
        if key not in EX_BY_KEY:
            raise SystemExit('操作题 key 不存在：%s' % key)
        if key not in kb:
            raise SystemExit('背景知识 key 不存在：%s' % key)
        for pid in pids:
            if pid not in by_id or by_id[pid]['type'] != 'point':
                raise SystemExit('知识点 id 不存在：%s（来自 %s）' % (pid, key))
        practicals[key] = mk_practical(key)
        for pid in pids:
            by_id[pid]['practicalKeys'].append(key)

    for n in point_nodes:
        n['practicalKeys'] = list(dict.fromkeys(n['practicalKeys']))
        if n['practicalKeys']:
            first = practicals[n['practicalKeys'][0]]
            n['examFocus'] = first['exam']
            if len(n['detail'].splitlines()) < 3:
                n['detail'] += '\n【操作印证】%s' % short(first['explanation'], 220)
            for key in n['practicalKeys']:
                p = practicals[key]
                n['links'].append({'label': '%s · 直达例题' % p['no'], 'href': p['href']})

    # 校验：72 题全部进入图谱，且每个操作型知识点至少有一道题。
    missing = sorted(set(EX_BY_KEY) - set(practicals))
    if missing:
        raise SystemExit('操作题未挂载：%s' % missing)
    orphan = [n['id'] for n in point_nodes
              if n['parent'][:2] in ('M2', 'M3', 'M4') and not n['practicalKeys']]
    if orphan:
        raise SystemExit('操作型知识点无关联题：%s' % orphan)

    # ---------- 理论题唯一挂载 ----------
    assigned = collections.defaultdict(list)
    for q in questions:
        topic = q.get('topic', '')
        pid = TOPIC_POINT.get(topic)
        if not pid:
            # 未在精确表中的题按题库分类兜底到对应模块，再在模块内找余量最小的节点。
            mid = CAT_MODULE.get(q.get('cat', ''), 'M1')
            cands = [n for n in point_nodes if n['id'].startswith('P-' + mid + '-')]
            pid = min(cands, key=lambda n: (len(assigned[n['id']]), n['id']))['id']
        if len(assigned[pid]) >= 6:
            mid = pid.split('-')[1]
            cands = [n for n in point_nodes if n['id'].startswith('P-' + mid + '-')]
            pid = min(cands, key=lambda n: (len(assigned[n['id']]), n['id']))['id']
        assigned[pid].append(mk_question(q))
    for n in point_nodes:
        n['questions'] = assigned.get(n['id'], [])
    if sum(len(v) for v in assigned.values()) != len(questions):
        raise SystemExit('理论题挂载数量不一致')

    # ---------- 跨域关联 ----------
    by_kw = collections.defaultdict(list)
    for n in point_nodes:
        for k in n.get('points', []):
            kk = re.sub(r'[：:·\s（）()\-—]+', '', clean(k))
            if len(kk) >= 4:
                by_kw[kk[:6]].append(n['id'])
    seen = set()

    def add_rel(a, b, label):
        if a == b or (a, b) in seen or (b, a) in seen:
            return
        seen.add((a, b))
        edges.append({'source': a, 'target': b, 'kind': 'related', 'label': label})

    pts_by_domain = collections.defaultdict(list)
    for n in point_nodes:
        pts_by_domain[n['parent']].append(n['id'])
    for did, ids in pts_by_domain.items():
        for a, b in zip(ids, ids[1:]):
            add_rel(a, b, '知识链')
    for kw, ids in by_kw.items():
        if 1 < len(ids) <= 6:
            for a in ids:
                for b in ids:
                    if a >= b:
                        continue
                    add_rel(a, b, kw)
    topic_map = collections.defaultdict(set)
    for n in point_nodes:
        for q in n.get('questions', []):
            topic_map[q['topic']].add(n['id'])
    for topic, ids in topic_map.items():
        ids = list(ids)
        if len(ids) > 1:
            for a, b in zip(ids, ids[1:]):
                add_rel(a, b, topic.split(' · ')[-1][:8])

    return {
        'meta': {
            'title': 'WPS 国家二级考试知识图谱',
            'subtitle': '知识点 · 考试要点 · 经典题目分析 · 考试详解',
            'source': '依据 NCRE 二级 WPS Office 高级应用与设计考试大纲（2025 年版）及本站课程数据重构',
            'engine': 'D3.js v7 (d3/d3, ISC)',
            'counts': {
                'nodes': len(nodes),
                'edges': len(edges),
                'modules': len(modules),
                'domains': sum(1 for n in nodes if n['type'] == 'domain'),
                'points': len(point_nodes),
                'theoryQuestions': len(questions),
                'practicals': len(practicals),
                'practicalLinks': sum(len(n['practicalKeys']) for n in point_nodes),
            },
        },
        'nodes': nodes, 'edges': edges, 'practicals': practicals,
    }


if __name__ == '__main__':
    data = build()
    out = ROOT / 'assets/knowledge-graph-data.js'
    out.write_text(
        '/* 由 tools/build_knowledge_graph.py 从网站现有数据生成，请勿手工编辑 */\n'
        'window.KNOWLEDGE_GRAPH = ' + json.dumps(data, ensure_ascii=False, separators=(',', ':')) + ';\n',
        encoding='utf-8')
    print('meta', data['meta']['counts'])
    print('written', out, out.stat().st_size, 'bytes')
