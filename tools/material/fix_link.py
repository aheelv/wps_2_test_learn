# -*- coding: utf-8 -*-
"""全链路一致性修订（幂等，按 (ci, seq) 唯一定位，绝不按题号）。

修复四类不一致，并把网页 → 生成数据 → 素材说明 → zip 全链同步：
  1. 网页 <code> 标签内的跨题旧文件引用（上一轮纯文本替换漏掉的部分）；
  2. 版本混用 / 不确定表述（部分版本、版本差异、旧版不支持…）；
  3. 数据规模描述与素材实际行数不符（60 行 / 30 行 → 20 行，对应 A1:F21）；
  4. exercises.json、72 份素材说明.txt、72 个下载包与网页逐题对齐。

用法：python tools/material/fix_link.py
"""
import os, re, sys, json, zipfile, html as H
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build as B

PAGES = ['入门实操课.html', '实操-文字2.html', '实操-文字3.html',
         '实操-表格1.html', '实操-表格2.html', '实操-表格3.html',
         '实操-演示1.html', '实操-演示2.html']

# ---------------------------------------------------------------- 1) 按题定位
# key = (第几次课, 该课内题序)。网页 <code> 标签内的替换必须用完整 HTML 片段。
ART_FIX = {
    (1, 4): [
        ('打开 <code>练习1-3.docx</code>，把纸张设为',
         '打开本题素材包中的 <code>素材-练习1-4.docx</code>，把纸张设为'),
        ('选 <code>练习1-3.docx</code> → 打开',
         '选 <code>素材-练习1-4.docx</code> → 打开'),
    ],
    (1, 6): [
        ('在 <code>练习2-1.docx</code> 基础上（或新建录入素材三段）',
         '打开本题素材包中的 <code>素材-练习1-6.docx</code>（含三段待排版文字）'),
    ],
    (1, 11): [
        ('在 <code>练习3-1.docx</code> 基础上，把「二、实训内容」',
         '打开本题素材包中的 <code>素材-练习1-11.docx</code>，把「二、实训内容」'),
    ],
}

# ---------------------------------------------------------------- 2) 版本口径
# 全站精确替换：把「不确定 / 版本对比」措辞改为教育考试专用版的确定表述。
PAGE_FIX = {
    '入门实操课.html': [
        ('关于版本差异（很重要，别被界面名字绕住）',
         '关于界面名称（统一按教育考试专用版表述）'),
        ('文件 → 输出为PDF（部分版本：另存为PDF）', '文件 → 输出为 PDF'),
    ],
    '实操-文字2.html': [
        ('功能区才会出现「表格工具」选项卡（部分版本显示为「表格」）',
         '功能区才会出现「表格工具」选项卡'),
    ],
    '实操-表格1.html': [
        ('部分版本不认，必须点行号让系统写入 $1:$1',
         '手打区域引用无效，必须点行号让系统写入 $1:$1'),
    ],
    '实操-演示1.html': [
        ('竖排文本框用横排后改文字方向：部分版本会重排错位，建议直接插竖向文本框。',
         '竖排文本框用横排后改文字方向：容易重排错位，应直接插入竖排文本框。'),
        ('那不是改数据，只是改图形（部分版本不允许）。',
         '那不是改数据，只是改图形，图表系列值并未改变。'),
    ],
    '实操-演示2.html': [
        ('检查是否存在<b>兼容性问题</b>（是否有旧版不支持的动画/媒体）。',
         '检查文档中是否存在<b>无法播放的动画与媒体</b>（确认所用对象均为教育考试专用版支持的类型）。'),
    ],
    '使用说明.html': [
        ('仅用于兼容旧版按功能控制', '仅用于兼容既有按功能控制的设置'),
    ],
}

# ---------------------------------------------------------------- 3) 数据规模
# 素材主数据表为 21 行（1 行表头 + 20 行数据），题目中的历史规模描述统一到 20 行。
SCALE_FILES = ['实操-表格1.html', '实操-表格2.html', '实操-表格3.html']
SCALE_RE = [
    (r'60\s*行', '20 行'),
    (r'共\s*30\s*行', '共 20 行'),
    (r'(?<![0-9])30\s*行', '20 行'),
    (r'(?<![0-9])30\s*条', '20 条'),
    (r'(?<![0-9])30\s*条记录', '20 条记录'),
]


def apply(s, pairs):
    n = 0
    for a, b in pairs:
        c = s.count(a)
        if c:
            s = s.replace(a, b)
            n += c
    return s, n


def fix_pages():
    total = {'art': 0, 'ver': 0, 'scale': 0}
    for ci, fn in enumerate(PAGES, 1):
        p = ROOT / fn
        s = p.read_text(encoding='utf-8')
        orig = s

        # (1) 按题定位：拆 article，逐段替换后原样拼回
        if any(k[0] == ci for k in ART_FIX):
            spans = [m.span() for m in
                     re.finditer(r'<article class="ex"[^>]*>.*?</article>', s, re.S)]
            out, last = [], 0
            for k, (a, b) in enumerate(spans, 1):
                seg = s[a:b]
                out.append(s[last:a])
                pairs = ART_FIX.get((ci, k))
                if pairs:
                    seg, n = apply(seg, pairs)
                    total['art'] += n
                out.append(seg)
                last = b
            out.append(s[last:])
            s = ''.join(out)

        # (2) 版本口径
        s, n = apply(s, PAGE_FIX.get(fn, []))
        total['ver'] += n

        # (3) 数据规模
        if fn in SCALE_FILES:
            for pat, rep in SCALE_RE:
                s, n2 = re.subn(pat, rep, s)
                total['scale'] += n2

        if s != orig:
            p.write_text(s, encoding='utf-8')
    # 总页 / 其它页面也可能有版本措辞
    for fn, pairs in PAGE_FIX.items():
        if fn in PAGES:
            continue
        p = ROOT / fn
        if not p.exists():
            continue
        s, n = apply(p.read_text(encoding='utf-8'), pairs)
        if n:
            p.write_text(s, encoding='utf-8')
            total['ver'] += n
    return total


# ---------------------------------------------------------------- 4) 同步 JSON
TAG_RE = re.compile(r'</?[A-Za-z][^>]*>')   # 只剥真实标签，保留 <=79 / <60 等比较符


def clean(s):
    return re.sub(r'\s+', ' ', H.unescape(TAG_RE.sub('', s))).strip()


def sync_json():
    """以修订后的网页为准回写 reqs / steps / score；题号、顺序、src 不动。"""
    p = ROOT / 'tools/material/exercises.json'
    data = json.loads(p.read_text(encoding='utf-8'))
    by = {(x['ci'], x['seq']): x for x in data}
    changed = 0
    for ci, fn in enumerate(PAGES, 1):
        s = (ROOT / fn).read_text(encoding='utf-8')
        arts = re.findall(r'<article class="ex"[^>]*>(.*?)</article>', s, re.S)
        for k, a in enumerate(arts, 1):
            q = by[(ci, k)]
            m = re.search(r'<div class="req">(.*?)(?:<div class="kicker">解题步骤|<ol class="steps">)',
                          a, re.S)
            reqs = [clean(x) for x in re.findall(r'<li[^>]*>(.*?)</li>', m.group(1), re.S)] if m else []
            ols = re.findall(r'<ol class="steps">(.*?)</ol>', a, re.S)
            steps = [clean(x) for x in re.findall(r'<li[^>]*>(.*?)</li>', ''.join(ols), re.S)]
            m2 = re.search(r'<div class="score">(.*?)</div>', a, re.S)
            score = clean(m2.group(1)) if m2 else q['score']
            for key, val in (('reqs', reqs), ('steps', steps), ('score', score)):
                if q.get(key) != val:
                    q[key] = val
                    changed += 1
    p.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding='utf-8')
    return changed


# ---------------------------------------------------------------- 5) 说明 + zip
def uses_for(rec):
    """与 build.py 相同的确定性用途口径，避免解析既有说明造成质量回退。"""
    spec = B.SPECS[(rec['ci'], rec['seq'])]
    out = []
    for fn in rec['files']:
        if fn == '素材说明.txt':
            use = '文件清单 / 题目要求 / 完成效果 / 环境口径'
        elif spec['kind'] == 'ref':
            use = B.ref_use(fn, None)
        elif fn.startswith('素材-'):
            use = '起始素材（%s）：解题步骤的操作对象' % B.MODULE[rec['ci']]
        else:
            use = B.extra_use(fn)
        out.append((fn, use))
    return out


def regen_readmes_and_repack():
    """按修订后的题目重建 72 份素材说明，并重打全部 72 个 zip。"""
    B.DATA = json.load(open(ROOT / 'tools/material/exercises.json', encoding='utf-8'))
    MF = json.load(open(ROOT / 'tools/material/manifest.json', encoding='utf-8'))
    used, missing = 0, []
    for rec in MF:
        key = (rec['ci'], rec['seq'])
        e = next((x for x in B.DATA if (x['ci'], x['seq']) == key), None)
        if e is None:
            missing.append(rec['folder'])
            continue
        spec = B.SPECS[key]
        d = ROOT / '练习素材' / rec['folder']
        f = d / '素材说明.txt'
        txt = B.readme_text(e, spec, uses_for(rec), rec['folder'])
        if (not f.exists()) or f.read_text(encoding='utf-8') != txt:
            f.write_text(txt, encoding='utf-8')
            used += 1
        zp = ROOT / '练习素材' / '下载' / rec['zip']
        zp.unlink(missing_ok=True)
        with zipfile.ZipFile(zp, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
            for fn in rec['files']:
                z.write(d / fn, arcname=rec['folder'] + '/' + fn)
    return used, missing


def main():
    t = fix_pages()
    print('网页修订：跨题引用 %d 处 ｜ 版本口径 %d 处 ｜ 数据规模 %d 处'
          % (t['art'], t['ver'], t['scale']))
    print('exercises.json 回写字段数：%d' % sync_json())
    n, miss = regen_readmes_and_repack()
    print('素材说明重建 %d 份 ｜ zip 重打 %d 个 ｜ 缺题包 %d 个'
          % (n, 72, len(miss)))
    if miss:
        print('  需复核：', ', '.join(miss))


if __name__ == '__main__':
    main()
