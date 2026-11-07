# -*- coding: utf-8 -*-
"""逐题核查题目条件 / 操作要求 / 解题步骤 / 素材包 / 生成文件 / 网页链接的一致性。

只回传结构化结论；详细命中写入 _link_detail.json 供本地修订使用。
用法：
  python tools/material/audit_link.py
  python tools/material/audit_link.py --detail
"""
import re, json, sys, html as H
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
E = json.load(open(ROOT / 'tools/material/exercises.json', encoding='utf-8'))
M = json.load(open(ROOT / 'tools/material/manifest.json', encoding='utf-8'))
BY = {(r['ci'], r['seq']): r for r in M}

FILE_RE = re.compile(r'[\w\u4e00-\u9fa5\-.]+\.(?:docx|xlsx|pptx|png|txt|wav|pdf|zip)')
RANGE_RE = re.compile(r'\b([A-Z]{1,2})(\d+):([A-Z]{1,2})(\d+)\b')
SLIDES_RE = re.compile(r'(?:共|计|为)\s*(\d+)\s*张|(?:共|计)\s*(\d+)\s*页')
CODE_RE = re.compile(r'<code>(.*?)</code>', re.S)

# 学生另存 / 导出 / 生成的目标文件不是起始素材，不应按「引用文件不在包内」报错
OUT_WORDS = re.compile(r'另存为|保存为|输出为|导出为|命名为|生成|得到|结果为|文件名|保存到|打包|另存')
# 中文动词被正则吞进文件名（如「选初稿.docx」）
VERB_PREFIX = ('打开', '选中', '选择', '选', '用', '把', '将', '为', '到', '即', '是', '和', '与')
OUT_NAME = ('学号-姓名', '完成', '结果', '比较结果', '通知书', '前四页', '课时')


TAG_RE = re.compile(r'</?[A-Za-z][^>]*>')


def clean(s):
    return re.sub(r'\s+', ' ', H.unescape(TAG_RE.sub('', s))).strip()


def colnum(c):
    n = 0
    for ch in c:
        n = n * 26 + (ord(ch) - 64)
    return n


def norm_fn(fn):
    """剥离被吞入的中文动词；返回 None 表示应按输出目标 / 反例排除。"""
    if fn.count('.docx') > 1 or fn.count('.xlsx') > 1 or fn.count('.pptx') > 1:
        return None                       # 易错提示里的「练习1-1.docx.docx」反例
    if fn.startswith(OUT_NAME) or fn in ('README.txt', '素材说明.txt'):
        return None
    for v in VERB_PREFIX:
        if fn.startswith(v) and len(fn) > len(v) + 5:
            return fn[len(v):]
    return fn


def inspect_material(rec):
    """读取素材主文件，返回可核对的客观属性。"""
    d = ROOT / '练习素材' / rec['folder']
    out = dict(files=rec['files'], sheets={}, slides=0, paragraphs=0)
    for fn in rec['files']:
        p = d / fn
        if fn.endswith('.xlsx'):
            from openpyxl import load_workbook
            wb = load_workbook(str(p), read_only=True, data_only=False)
            for ws in wb.worksheets:
                out['sheets'][ws.title] = (ws.max_row, ws.max_column)
            wb.close()
        elif fn.endswith('.pptx'):
            from pptx import Presentation
            out['slides'] = max(out['slides'], len(Presentation(str(p)).slides))
        elif fn.endswith('.docx'):
            from docx import Document
            out['paragraphs'] += len(Document(str(p)).paragraphs)
    return out


def collect():
    """返回 (问题明细, 逐题汇总)，供 verify.py 实时复用，不产生屏幕输出。"""
    detail, summary = [], []
    for q in E:
        key = (q['ci'], q['seq'])
        rec = BY[key]
        mat = inspect_material(rec)
        body = '\n'.join(q['reqs'] + q['steps'] + [q['score'] or ''])
        issues = []

        # 1) 生成数据里引用的起始文件必须在本题素材包内
        for m in FILE_RE.finditer(body):
            fn = norm_fn(m.group(0))
            if not fn or fn.endswith('.zip'):
                continue
            ctx = body[max(0, m.start() - 45):m.end() + 20]
            if OUT_WORDS.search(ctx):
                continue
            if fn not in rec['files'] and not any(w in fn for w in ('完成', '结果', '比对')):
                issues.append(dict(type='引用文件不在包内', value=fn))

        # 2) 起始数据区范围不得超出素材；学生新建的结果区（横向加列 / 向下加行）忽略
        for m in RANGE_RE.finditer(body):
            c1, r1 = colnum(m.group(1)), int(m.group(2))
            c2, r2 = colnum(m.group(3)), int(m.group(4))
            if not mat['sheets']:
                continue
            maxr = max(mr for mr, mc in mat['sheets'].values())
            maxc = max(mc for mr, mc in mat['sheets'].values())
            if c1 > maxc or r1 > maxr + 1 or c2 > maxc:
                continue
            if maxr < r2:
                issues.append(dict(type='起始数据范围超出素材', value=m.group(0),
                                   actual=maxr, target=r2))

        # 3) 题目声明的幻灯片页数与素材一致（素材是起始文稿，允许少于目标页数）
        for m in SLIDES_RE.finditer(body):
            n = int(m.group(1) or m.group(2))
            if mat['slides'] and n > 0 and mat['slides'] > n:
                issues.append(dict(type='素材页数超过题目目标', value=n, actual=mat['slides']))

        # 4) 网页侧：本题下载入口 / 素材块 / 完成比对链接 / 步骤截图 / 文件引用 / 文本同步
        s = (ROOT / q['page']).read_text(encoding='utf-8')
        arts = re.findall(r'<article class="ex"[^>]*>(.*?)</article>', s, re.S)
        a = arts[q['seq'] - 1] if q['seq'] <= len(arts) else ''
        chk = dict(
            mat_dl=bool(re.search(r'class="mat-dl"', a)),
            mat_idx=bool(re.search(r'class="mat"', a)),
            cmp_link=bool(re.search(r'class="cmp-dl"', a)),
            step_shot=bool(re.search(r'class="steps-shot"', a)),
        )
        for k, v in chk.items():
            if not v:
                issues.append(dict(type='网页缺少', value=k))

        for c in CODE_RE.findall(a):
            fn = norm_fn(clean(c))
            if not fn or not FILE_RE.fullmatch(fn or ''):
                continue
            if fn not in rec['files'] and fn not in ('素材说明.txt',):
                issues.append(dict(type='网页引用文件不在包内', value=fn))

        lis = [clean(x) for x in re.findall(r'<li[^>]*>(.*?)</li>', a, re.S)]
        alltext = ' '.join(lis)
        miss = sum(1 for t in q['reqs'] + q['steps']
                   if len(t) > 12 and clean(t)[:24] not in alltext)
        if miss:
            issues.append(dict(type='网页与生成数据不同步', value=miss))

        summary.append(dict(no=q['no'], ci=q['ci'], seq=q['seq'], folder=rec['folder'],
                            issues=issues, files=len(rec['files']),
                            slides=mat['slides'], sheets=len(mat['sheets'])))
        for i in issues:
            detail.append(dict(no=q['no'], page=q['page'], **i))
    return detail, summary


def main():
    detail, summary = collect()
    if '--detail' in sys.argv:
        json.dump(detail, open(ROOT / 'tools/material/_link_detail.json', 'w', encoding='utf-8'),
                  ensure_ascii=False, indent=1)
    from collections import Counter
    c = Counter(i['type'] for i in detail)
    print('题目数 %d ｜ 一致项问题 %d' % (len(summary), len(detail)))
    for k, v in c.most_common():
        print('  %-22s %d' % (k, v))
    print('受影响题数 %d' % sum(1 for r in summary if r['issues']))


if __name__ == '__main__':
    main()
