# -*- coding: utf-8 -*-
"""逐题核对 8 次课 72 道实操题与配套素材包的对应关系（全量，不抽查）。

核对维度（每题都跑，不抽样）：
    R1 主文件类型与课次模块是否匹配（docx / xlsx / pptx）
    R2 题目与步骤引用的起始文件是否都在本题素材包内
    R3 题干 src 声明的表头列是否出现在素材数据表表头中
    R4 题干 src 声明的记录条数是否与素材数据行数一致
    R5 题目声明的单元格范围是否超出素材实际范围
    R6 题目声明的幻灯片页数与素材起始文稿页数
    R7 包内每个附件是否被题目或解题步骤引用（避免无关文件）
    R8 题内数量自洽：标题 / 要求 / 采分点中的「N 张工作表」等
    R9 题目提到的起始数据表名是否在素材中存在
    R10 有录入素材的文字题：src 正文是否进入素材主文档
    R11 专用附件内容是否与题目声明一致（大纲 / 评分表 / 图表数据）

输出：tools/material/match_report.json（逐题明细 + 汇总）
用法：python tools/material/audit_match.py [--detail]
"""
import os, re, sys, json, html as H
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from specs import SPECS, KIND_BY_CI, MODULE

E = json.load(open(HERE / 'exercises.json', encoding='utf-8'))
M = json.load(open(HERE / 'manifest.json', encoding='utf-8'))
BY = {(r['ci'], r['seq']): r for r in M}

TAG_RE = re.compile(r'</?[A-Za-z][^>]*>')
FILE_RE = re.compile(r'[\w\u4e00-\u9fa5\-.]+\.(?:docx|xlsx|pptx|png|txt|wav|mp4|pdf|zip)')
RANGE_RE = re.compile(r'\b([A-Z]{1,2})(\d+):([A-Z]{1,2})(\d+)\b')
OUT_WORDS = re.compile(r'另存为|保存为|输出为|导出为|命名为|生成|得到|结果为|文件名|保存到|打包|另存')
VERB_PREFIX = ('打开', '选中', '选择', '选', '用', '把', '将', '为', '到', '即', '是', '和', '与')
OUT_NAME = ('学号-姓名', '完成', '结果', '比较结果', '通知书', '前四页', '课时')
KNOWN_SHEETS = ('销售明细', '成绩表', '员工信息', '部门一览', '一季度', '二季度', '三季度',
                '学生档案', '成绩数据', '查询区', '身份信息', '月度趋势', '品类占比',
                '贷款测算', '利率敏感性', '题目说明', 'Sheet1', '汇总', '参数',
                '新生名单', '图表数据', '自评表')
# 学生要新建/重命名的目标表，不要求素材预置
TARGET_SHEETS = ('汇总', '参数', '销售明细')


def clean(s):
    return re.sub(r'\s+', ' ', H.unescape(TAG_RE.sub('', s or ''))).strip()


def norm_fn(fn):
    if fn.count('.docx') > 1 or fn.count('.xlsx') > 1 or fn.count('.pptx') > 1:
        return None
    if fn.startswith(OUT_NAME) or fn in ('README.txt', '素材说明.txt'):
        return None
    for v in VERB_PREFIX:
        if fn.startswith(v) and len(fn) > len(v) + 5:
            return fn[len(v):]
    return fn


def colnum(c):
    n = 0
    for ch in c:
        n = n * 26 + (ord(ch) - 64)
    return n


def inspect(rec):
    """读取素材包内每个文件的真实内容，返回结构化事实。"""
    d = ROOT / '练习素材' / rec['folder']
    out = dict(files=rec['files'], main='', sheets={}, texts={}, slides=0,
               paragraphs=0, missing=[])
    for fn in rec['files']:
        p = d / fn
        if not p.exists():
            out['missing'].append(fn)
            continue
        if fn.endswith('.xlsx'):
            from openpyxl import load_workbook
            wb = load_workbook(str(p), read_only=True, data_only=True)
            for ws in wb.worksheets:
                rows = list(ws.iter_rows(values_only=True))
                hdr = [str(v).strip() if v is not None else '' for v in (rows[0] if rows else [])]
                vals = ' '.join(str(v) for r in rows[:25] for v in r if v is not None)
                out['sheets'][ws.title] = dict(rows=ws.max_row, cols=ws.max_column,
                                               headers=hdr, text=vals)
                out['texts'][fn + '#' + ws.title] = ' '.join(hdr) + ' ' + vals
            wb.close()
        elif fn.endswith('.docx'):
            from docx import Document
            ps = [x.text for x in Document(str(p)).paragraphs if x.text.strip()]
            out['texts'][fn] = ' '.join(ps)
            out['paragraphs'] += len(ps)
        elif fn.endswith('.pptx'):
            from pptx import Presentation
            pr = Presentation(str(p))
            out['slides'] = max(out['slides'], len(pr.slides))
            out['texts'][fn] = ' '.join(
                sh.text_frame.text for s in pr.slides for sh in s.shapes
                if sh.has_text_frame and sh.text_frame.text.strip())
        elif fn.endswith(('.txt',)):
            out['texts'][fn] = p.read_text(encoding='utf-8', errors='replace')
        else:
            out['texts'][fn] = ''
    mains = [f for f in rec['files'] if f.startswith('素材-') or f in
             ('初稿.docx', '修改稿.docx', '素材A.docx', '素材B.docx',
              '录取通知书-主文档占位模板.docx')]
    out['main'] = mains[0] if mains else (rec['files'][0] if rec['files'] else '')
    return out


def qtext(q):
    return clean(' '.join([q['title']] + q['reqs'] + q['steps'] +
                          [q.get('score') or ''] + [q.get('src') or '']))


def data_sheets(mat):
    return {k: v for k, v in mat['sheets'].items() if k != '题目说明'}


def check(q, mat):
    issues = []
    rec = BY[(q['ci'], q['seq'])]
    key = (q['ci'], q['seq'])
    spec = SPECS[key]
    Q = qtext(q)
    src = clean(q.get('src') or '')
    body = '\n'.join(q['reqs'] + q['steps'] + [q.get('score') or ''])
    ds = data_sheets(mat)

    # R1 主文件类型
    ext = mat['main'].rsplit('.', 1)[-1] if '.' in mat['main'] else ''
    want = KIND_BY_CI[q['ci']]
    if ext != want:
        issues.append(dict(rule='R1', type='主文件类型与课次模块不符',
                           expect=want, actual=ext or '(无)'))

    # R2 引用文件
    for m in FILE_RE.finditer(body):
        fn = norm_fn(m.group(0))
        if not fn or fn.endswith('.zip'):
            continue
        ctx = body[max(0, m.start() - 45):m.end() + 20]
        if OUT_WORDS.search(ctx):
            continue
        if fn not in rec['files'] and not any(w in fn for w in ('完成', '结果', '比对')):
            issues.append(dict(rule='R2', type='引用文件不在包内', value=fn))

    # R3 src 声明的表头列
    mh = re.search(r'表头[：:]\s*([^\n。]+)', src)
    if mh and spec['kind'] == 'xlsx':
        # 题干常把「表头：A|B|C」「记录示例：…」「共 N 条，…」写在同一段，
        # 只取表头部分，避免把示例数值当成列名。
        seg = re.split(r'记录示例|共\s*\d+\s*条|[。;；]', mh.group(1))[0]
        cols = [c.strip() for c in re.split(r'[|｜、,，\s]+', seg) if c.strip()]
        allhdr = set()
        for v in ds.values():
            allhdr |= set(v['headers'])
        missing = [c for c in cols if c and c not in allhdr and len(c) <= 8]
        if missing:
            issues.append(dict(rule='R3', type='题干表头列在素材中缺失',
                               value='、'.join(missing),
                               actual='；'.join('%s:%s' % (k, '/'.join(v['headers'][:8]))
                                                for k, v in ds.items())))

    # R4 src 声明的记录条数
    mn = re.search(r'共\s*(\d+)\s*条|(\d+)\s*条记录', src + ' ' + Q)
    if mn and spec['kind'] == 'xlsx':
        n = int(mn.group(1) or mn.group(2))
        rows = [v['rows'] for v in ds.values()]
        if rows and max(rows) != n + 1:
            issues.append(dict(rule='R4', type='记录条数与素材数据行数不符',
                               expect=n, actual='最大数据表 %d 行（含表头）' % max(rows)))

    # R5 单元格范围
    for m in RANGE_RE.finditer(body):
        c1, r1, c2, r2 = colnum(m.group(1)), int(m.group(2)), colnum(m.group(3)), int(m.group(4))
        if not ds:
            continue
        maxr = max(v['rows'] for v in ds.values())
        maxc = max(v['cols'] for v in ds.values())
        if c1 > maxc or r1 > maxr + 1 or c2 > maxc:
            continue
        if maxr < r2:
            issues.append(dict(rule='R5', type='起始数据范围超出素材',
                               value=m.group(0), actual='%d行×%d列' % (maxr, maxc)))

    # R6 幻灯片页数
    for m in re.finditer(r'(?:共|计|为|成)\s*(\d+)\s*张|(?:共|计)\s*(\d+)\s*页', Q):
        n = int(m.group(1) or m.group(2))
        if spec['kind'] == 'pptx' and mat['slides'] > n > 0:
            issues.append(dict(rule='R6', type='素材页数超过题目目标',
                               expect=n, actual=mat['slides']))

    # R7 包内附件是否有对应的题目用途（按对象类型判断，不按泛称关键词硬匹配）
    for fn in rec['files']:
        if fn == '素材说明.txt' or fn == mat['main'] or fn.startswith('素材-'):
            continue
        if spec['kind'] == 'ref':
            continue          # 参考包题的多文档均被步骤引用，另行核对
        ext = fn.rsplit('.', 1)[-1]
        purpose = False
        if ext in ('wav', 'mp3') and re.search(r'音频|背景音乐|声音', Q):
            purpose = True
        elif ext in ('mp4', 'avi', 'wmv', 'mov') and re.search(r'视频', Q):
            purpose = True
        elif ext in ('png', 'jpg', 'jpeg') and re.search(r'素材图|图片|logo|图标|背景图|相册', Q):
            purpose = True
        elif fn == '大纲.txt' and re.search(r'大纲', Q):
            purpose = True
        elif fn == '评分表.xlsx' and re.search(r'评分表|自评表', Q):
            purpose = True
        elif fn == '图表数据.xlsx' and re.search(r'图表数据源|打开图表数据|以图表数据', Q):
            purpose = True
        if not purpose:
            issues.append(dict(rule='R7', type='包内附件无对应题目用途', value=fn))

    # R8 题内数量自洽（工作表张数）
    title_n = re.search(r'(\d+)\s*张工作表', q['title'])
    score_n = re.search(r'(\d+)\s*张工作表', clean(q.get('score') or ''))
    if title_n and score_n and title_n.group(1) != score_n.group(1):
        issues.append(dict(rule='R8', type='标题与采分点工作表张数不一致',
                           title=title_n.group(1), score=score_n.group(1)))
    listed = re.search(r'工作表顺序为\s*([^\n·]+)', clean(q.get('score') or ''))
    if score_n and listed:
        names = [x.strip() for x in re.split(r'[/、,，]', listed.group(1)) if x.strip()]
        if len(names) != int(score_n.group(1)):
            issues.append(dict(rule='R8', type='采分点工作表张数与列出的表名数量不符',
                               declared=score_n.group(1), listed=len(names)))

    # R9 题目提到的起始数据表名
    for name in KNOWN_SHEETS:
        if name in TARGET_SHEETS or name == '题目说明' or name == 'Sheet1':
            continue
        if re.search(r'「%s」|「%s」表|%s\s*工作表' % (name, name, name), Q):
            if name not in mat['sheets'] and not any(name in k for k in mat['sheets']):
                issues.append(dict(rule='R9', type='题目提到的数据表在素材中不存在', value=name))

    # R10 有 src 的文字题：正文是否进入素材主文档
    if spec['kind'] == 'docx' and src and len(src) > 24:
        frag = re.sub(r'\s+', '', src)[:24]
        mattext = re.sub(r'\s+', '', ' '.join(mat['texts'].get(f, '') for f in rec['files']
                                              if f.endswith('.docx')))
        if frag and frag not in mattext:
            issues.append(dict(rule='R10', type='录入素材正文未进入素材文档',
                               value=frag[:24]))

    # R11 专用附件内容
    for fn, text in mat['texts'].items():
        if '大纲.txt' in fn and src:
            # 题干的「录入素材」被压成单行：去掉开头括号说明后按空白切出条目
            body = re.sub(r'^[（(][^）)]*[）)]\s*', '', src)
            items = [x.strip() for x in re.split(r'\s+', body) if len(x.strip()) >= 3]
            plain = re.sub(r'\s+', '', text)
            hit = sum(1 for x in items[:8] if re.sub(r'\s+', '', x) in plain)
            if items and hit < max(1, int(len(items[:8]) * 0.75)):
                issues.append(dict(rule='R11', type='大纲.txt 内容与题干声明的大纲不一致',
                                   actual=text.replace('\n', ' / ')[:100]))

    # R12 题目要求的媒体/文件类型是否齐全
    if re.search(r'素材视频|本地视频|插入视频|视频文件', Q):
        if not any(f.rsplit('.', 1)[-1] in ('mp4', 'avi', 'wmv', 'mov') for f in rec['files']):
            issues.append(dict(rule='R12', type='题目要求插入素材视频但包内无视频文件',
                               value='缺少 mp4/avi/wmv'))
    if re.search(r'素材音频|本地音频|插入音频', Q):
        if not any(f.rsplit('.', 1)[-1] in ('wav', 'mp3') for f in rec['files']):
            issues.append(dict(rule='R12', type='题目要求插入素材音频但包内无音频文件',
                               value='缺少 wav/mp3'))

    # R13 评分表分值 / 项数与题目声明一致
    if '评分表.xlsx' in rec['files']:
        m = re.search(r'每项\s*(\d+)\s*分[，,、]?\s*满分\s*(\d+)\s*分', Q)
        if m:
            per, total = int(m.group(1)), int(m.group(2))
            ws = mat['sheets'].get('自评表')
            rows = list(__import__('openpyxl').load_workbook(
                str(ROOT / '练习素材' / rec['folder'] / '评分表.xlsx'),
                read_only=True, data_only=True).active.iter_rows(values_only=True))
            declared = [r for r in rows[1:] if r[0] and str(r[0]) != '合计']
            points = sum(int(r[1]) for r in declared if isinstance(r[1], (int, float)))
            if len(declared) != total // per or points != total:
                issues.append(dict(rule='R13', type='评分表项数或分值与题目要求不符',
                                   expect='%d 项 × %d 分 = %d 分' % (total // per, per, total),
                                   actual='%d 项 / 合计 %d 分' % (len(declared), points)))

    # R14 起始文稿页数需覆盖题目涉及的页序（题目自行生成的张数不算）
    if spec['kind'] == 'pptx' and not re.search(r'生成\s*\d+\s*张|新建\s*\d+\s*张', Q):
        nums = [int(x) for x in re.findall(r'第\s*(\d+)\s*张', Q)]
        if nums and max(nums) > mat['slides']:
            issues.append(dict(rule='R14', type='起始文稿页数不足以覆盖题目操作的页序',
                               expect='至少 %d 张' % max(nums), actual=mat['slides']))

    # R15 题目声明的起始文稿张数
    if spec['kind'] == 'pptx':
        m = re.search(r'起始文件[（(]\s*(\d+)\s*张幻灯片', Q)
        if m and int(m.group(1)) != mat['slides']:
            issues.append(dict(rule='R15', type='起始文稿张数与题目声明不符',
                               expect=int(m.group(1)), actual=mat['slides']))

    # R16 明确要求「以 Sheet1 为唯一起点建表」的题，素材不得预置多余工作表
    # （仅「新建工作簿」而题干未声明表结构的题，素材是备用参考数据，不受此限）
    if spec['kind'] == 'xlsx' and re.search(r'将\s*Sheet1\s*重命名', Q):
        names = [k for k in mat['sheets'] if k != '题目说明']
        if len(names) != 1 or names[0] != 'Sheet1':
            issues.append(dict(rule='R16', type='从零建表题的素材预置了多余工作表',
                               expect='仅 Sheet1', actual='、'.join(mat['sheets'])))

    # R17 附件数据内容与题目声明的图表数据不符
    if '图表数据.xlsx' in rec['files'] and re.search(r'季度销售额|4 个季度', Q):
        txt = mat['texts'].get('图表数据.xlsx#图表数据', '')
        if not re.search(r'季度|Q1|Q2', txt):
            issues.append(dict(rule='R17', type='图表数据附件内容与题目声明的季度数据不符',
                               actual=txt[:100]))
    return issues


def collect():
    rows, detail = [], []
    for q in E:
        rec = BY[(q['ci'], q['seq'])]
        mat = inspect(rec)
        issues = check(q, mat)
        rows.append(dict(ci=q['ci'], seq=q['seq'], no=q['no'], title=q['title'],
                         folder=rec['folder'], main=mat['main'], files=rec['files'],
                         sheets={k: (v['rows'], v['cols'], v['headers'][:8])
                                 for k, v in mat['sheets'].items()},
                         slides=mat['slides'], issue_count=len(issues)))
        for i in issues:
            detail.append(dict(ci=q['ci'], seq=q['seq'], no=q['no'], page=q['page'],
                               folder=rec['folder'], **i))
    return rows, detail


def main():
    rows, detail = collect()
    rep = dict(total=len(rows), checked=len(rows), issues=len(detail),
               affected=len({(d['ci'], d['seq']) for d in detail}),
               by_rule={}, rows=rows, detail=detail)
    from collections import Counter
    rep['by_rule'] = dict(Counter(d['rule'] for d in detail))
    json.dump(rep, open(HERE / 'match_report.json', 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print('全量核对：%d 题 / 已逐题检查 %d 题 / 不一致 %d 处 / 受影响 %d 题'
          % (rep['total'], rep['checked'], rep['issues'], rep['affected']))
    for k in sorted(rep['by_rule']):
        print('  %-4s %d' % (k, rep['by_rule'][k]))
    if '--detail' in sys.argv:
        for d in detail:
            print('  C%d-%02d %-9s [%s] %s %s' %
                  (d['ci'], d['seq'], d['no'], d['rule'], d['type'],
                   json.dumps({k: v for k, v in d.items()
                               if k not in ('ci', 'seq', 'no', 'page', 'folder', 'rule', 'type')},
                              ensure_ascii=False)[:220]))
    else:
        for r in rows:
            if r['issue_count']:
                print('  C%d-%02d %-9s %d 处 | %s' % (r['ci'], r['seq'], r['no'],
                                                     r['issue_count'], r['title'][:40]))


if __name__ == '__main__':
    main()
