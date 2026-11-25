# -*- coding: utf-8 -*-
"""从网站现有数据源生成「WPS 国家二级考试知识图谱」数据。

唯一数据源：
  assets/curriculum.js          课程知识点 / 考试要点 / 讲解
  考试模拟系统/index.html       120 道单选题（题干 / 选项 / 答案 / 解析）
  tools/_questions_extract.json 由 Node 从上述页面提取的题库 JSON（中间产物）

输出：
  assets/knowledge-graph-data.js  window.KNOWLEDGE_GRAPH = {...}

结构：模块(module) → 知识域(domain) → 知识点(point)
每个知识点含：brief 考试要点 / detail 考试详解 / questions 经典题目解析 / link 站内入口。
"""
import json, re, pathlib, collections

ROOT = pathlib.Path(__file__).resolve().parents[1]

# ---------- 读取课程数据 ----------
cur_src = (ROOT / 'assets/curriculum.js').read_text(encoding='utf-8')
cur = json.loads(re.search(r'window\.CURRICULUM\s*=\s*(\{.*\})\s*;?\s*$', cur_src, re.S).group(1))

# ---------- 读取题库 ----------
qpath = ROOT / 'tools/_questions_extract.json'
if not qpath.exists():
    raise SystemExit('缺少 tools/_questions_extract.json，请先运行提取脚本')
questions = json.loads(qpath.read_text(encoding='utf-8'))

# ---------- 模块 → 知识域定义 ----------
# 每个域：id, name, 关键词（匹配课程课时标题 / 题库 topic）,  icon
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
        ('D-W-TBL',  '表格制作与编辑', ['表格', '合并', '公式']),
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

# ---------- 工具函数 ----------
def clean(s):
    if s is None: return ''
    s = re.sub(r'<[^>]+>', '', str(s))
    return re.sub(r'\s+', ' ', s).strip()

def match(text, kws):
    return any(k.lower() in text.lower() for k in kws)

def mk_question(q):
    return {
        'id': q['id'], 'topic': q['topic'], 'diff': q.get('diff', ''),
        'q': q['q'], 'opts': q.get('opts', []), 'ans': q.get('ans'),
        'exp': q.get('exp', ''),
    }

def build():
    modules = {m['id']: m for m in cur['modules']}
    nodes, edges = [], []
    stats = collections.Counter()

    # 根节点
    nodes.append({'id': 'ROOT', 'type': 'root', 'name': '二级 WPS Office',
                  'short': 'NCRE 67', 'level': 0,
                  'brief': '全国计算机等级考试二级 WPS Office 高级应用与设计（科目代码 67）。',
                  'detail': '上机考试 120 分钟，满分 100 分：单选 20 分（含公共基础 10 分）、文字 30 分、表格 30 分、演示 20 分，60 分合格。考试环境为 WPS Office 教育考试专用版。',
                  'meta': {'score': '100 分', 'hours': '44 课时'}, 'questions': []})

    for mid, m in modules.items():
        nodes.append({'id': mid, 'type': 'module', 'name': m['name'], 'short': m.get('short', m['name']),
                      'level': 1, 'parent': 'ROOT',
                      'brief': clean(m.get('desc',''))[:400],
                      'detail': clean(m.get('desc','')) + ('\n\n覆盖考纲：' + m.get('syl','') if m.get('syl') else ''),
                      'meta': {'score': m.get('score',''), 'hours': f"{m.get('hours','')} 课时"}, 'questions': []})
        edges.append({'source': 'ROOT', 'target': mid, 'kind': 'belong'})

        # 域
        for did, dname, kws in DOMAIN_DEF.get(mid, []):
            nodes.append({'id': did, 'type': 'domain', 'name': dname, 'short': dname,
                          'level': 2, 'parent': mid, 'brief': f'{dname} · {m.get("short","")}',
                          'detail': f'「{dname}」是{m["name"]}下的核心知识域，涵盖该方向的高频考点与典型题型。',
                          'meta': {}, 'questions': []})
            edges.append({'source': mid, 'target': did, 'kind': 'belong'})

        # 知识点：按课时切片生成，归入匹配度最高的域
        for lesson in m.get('lessons', []):
            ltext = lesson.get('title','') + ' ' + ' '.join(lesson.get('obj',[])) + ' ' + ' '.join(lesson.get('key',[]))
            best, bestn = None, 0
            for did, dname, kws in DOMAIN_DEF.get(mid, []):
                n = sum(1 for k in kws if k.lower() in ltext.lower())
                if n > bestn: best, bestn = did, n
            if best is None:
                best = DOMAIN_DEF[mid][0][0]

            # 每个课时拆成 1~3 个知识点（按 key 列表分组）
            keys = lesson.get('key', []) or lesson.get('obj', [])
            chunks = [keys[:3], keys[3:6], keys[6:9]]
            chunks = [c for c in chunks if c]
            if not chunks: chunks = [['掌握' + lesson.get('title','')]]

            for ci, chunk in enumerate(chunks):
                pid = f'P-{mid}-{lesson.get("no",0)}-{ci+1}'
                pname = lesson.get('title','') if ci == 0 else f'{lesson.get("title","")} · {ci+1}'
                detail_parts = []
                for sl in lesson.get('slides', []):
                    pts = sl.get('b', []) or []
                    if pts:
                        detail_parts.append('【' + sl.get('t','要点') + '】' + '；'.join(clean(x) for x in pts[:6]))
                    eg = sl.get('eg') or {}
                    if eg.get('text'):
                        detail_parts.append('实例：' + clean(eg['text'])[:300])
                    if eg.get('warn'):
                        detail_parts.append('提醒：' + clean(eg['warn'])[:200])
                if not detail_parts:
                    detail_parts = ['；'.join(clean(x) for x in lesson.get('key',[])[:8])]
                diff = '；'.join(clean(x) for x in (lesson.get('diff',[]) or [])[:5])

                qmatch = [q for q in questions if match(q.get('topic','') + ' ' + q.get('q',''), chunk) or
                          match(q.get('topic',''), [lesson.get('title','')]) or
                          match(q.get('topic',''), kws_of(DOMAIN_DEF, mid, best))]
                qmatch = qmatch[:6]

                node = {
                    'id': pid, 'type': 'point', 'name': pname[:60], 'short': pname[:22],
                    'level': 3, 'parent': best,
                    'brief': '；'.join(clean(x) for x in chunk[:3])[:220],
                    'detail': '\n'.join(detail_parts[:6]) + ('\n\n难点：' + diff if diff else ''),
                    'points': [clean(x) for x in chunk],
                    'difficulty': diff,
                    'meta': {'lesson': lesson.get('no'), 'hours': lesson.get('hours')},
                    'questions': [mk_question(q) for q in qmatch],
                    'links': [
                        {'label': '查看课件', 'href': './培训课件.html'},
                        {'label': '电子书详解', 'href': './电子书.html'},
                        {'label': '考纲对照', 'href': './考纲对照表.html'},
                    ],
                }
                if mid == 'M1': node['links'].append({'label': '模拟考试', 'href': './考试模拟系统/index.html'})
                if mid == 'M2': node['links'].append({'label': '文字实操', 'href': './实操训练.html'})
                if mid == 'M3': node['links'].append({'label': '表格实操', 'href': './实操训练.html'})
                if mid == 'M4': node['links'].append({'label': '演示实操', 'href': './实操训练.html'})
                nodes.append(node)
                edges.append({'source': best, 'target': pid, 'kind': 'belong'})
                stats[pid.split('-')[1]] += 1

    # 跨域关联：①同域相邻知识点（知识链）②共享高频词 ③同题库主题
    by_kw = collections.defaultdict(list)
    for n in nodes:
        if n['type'] == 'point':
            for k in n.get('points', []):
                kk = re.sub(r'[：:·\s（）()\-—]+', '', clean(k))
                if len(kk) >= 4:
                    by_kw[kk[:6]].append(n['id'])
    seen = set()
    def add_rel(a, b, label):
        if a == b or (a,b) in seen or (b,a) in seen: return
        seen.add((a,b))
        edges.append({'source': a, 'target': b, 'kind': 'related', 'label': label})
    # 同域相邻知识点：按顺序串联，形成学习路径
    pts_by_domain = collections.defaultdict(list)
    for n in nodes:
        if n['type'] == 'point': pts_by_domain[n['parent']].append(n['id'])
    for did, ids in pts_by_domain.items():
        for a, b in zip(ids, ids[1:]):
            add_rel(a, b, '知识链')
    # 共享关键词
    for kw, ids in by_kw.items():
        if len(ids) > 1 and len(ids) <= 6:
            for a in ids:
                for b in ids:
                    if a >= b: continue
                    add_rel(a, b, kw)
                    if len(seen) > 200: break
                if len(seen) > 200: break
        if len(seen) > 200: break
    # 同题库主题跨域关联（优先公共基础与综合）
    topic_map = collections.defaultdict(set)
    for n in nodes:
        if n['type'] == 'point':
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
            'engine': 'D3.js v7 (d3/d3, GitHub 114k★, ISC)',
            'counts': {'nodes': len(nodes), 'edges': len(edges),
                       'points': sum(1 for n in nodes if n['type']=='point'),
                       'questions': sum(len(n.get('questions',[])) for n in nodes)},
        },
        'nodes': nodes, 'edges': edges,
    }

def kws_of(defs, mid, did):
    for d in defs.get(mid, []):
        if d[0] == did: return d[2]
    return []

if __name__ == '__main__':
    data = build()
    out = ROOT / 'assets/knowledge-graph-data.js'
    out.write_text('/* 由 tools/build_knowledge_graph.py 从网站现有数据生成，请勿手工编辑 */\nwindow.KNOWLEDGE_GRAPH = ' +
                   json.dumps(data, ensure_ascii=False, separators=(',',':')) + ';\n', encoding='utf-8')
    print('nodes', data['meta']['counts'])
    print('written', out, out.stat().st_size, 'bytes')
