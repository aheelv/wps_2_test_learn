# -*- coding: utf-8 -*-
"""Build self-contained question data (with inline base64 images + OMML formulas) from the docx."""
import zipfile, re, sys, json, base64, os
from xml.etree import ElementTree as ET

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
R = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'
A = '{http://schemas.openxmlformats.org/drawingml/2006/main}'
M = '{http://schemas.openxmlformats.org/officeDocument/2006/math}'
VML = '{urn:schemas-microsoft-com:vml}'

path = sys.argv[1]
out = sys.argv[2]
z = zipfile.ZipFile(path)
rels = ET.fromstring(z.read('word/_rels/document.xml.rels'))
relmap = {r.get('Id'): r.get('Target') for r in rels}
root = ET.fromstring(z.read('word/document.xml'))
body = root.find(W + 'body')

cache = {}
def data_uri(target):
    if target in cache:
        return cache[target]
    name = target if target.startswith('word/') else 'word/' + target.lstrip('/').replace('word/', '', 1)
    if name not in z.namelist():
        name = 'word/' + target
    raw = z.read(name)
    ext = os.path.splitext(name)[1].lower().lstrip('.')
    mime = {'png': 'image/png', 'jpg': 'image/jpeg', 'jpeg': 'image/jpeg',
            'gif': 'image/gif', 'bmp': 'image/bmp', 'emf': 'image/emf', 'wmf': 'image/wmf'}.get(ext, 'image/png')
    uri = 'data:%s;base64,%s' % (mime, base64.b64encode(raw).decode('ascii'))
    cache[target] = uri
    return uri

def ln(tag):
    return tag.split('}')[-1]

def child(n, name):
    for c in n:
        if ln(c.tag) == name:
            return c
    return None

def brace(s):
    s = s.strip()
    return ('{' + s + '}') if len(s) > 1 else s

def node_text(n):
    """Recursively linearise a paragraph, including OMML math as readable plain text."""
    tag = ln(n.tag)
    if tag in ('t',):
        return n.text or ''
    if tag in ('instrText', 'delText'):
        return ''
    if tag == 'tab':
        return '\t'
    if tag == 'br':
        return '\n'
    if tag == 'sSub':
        e, sub = child(n, 'e'), child(n, 'sub')
        return node_text(e) + '_' + brace(node_text(sub))
    if tag == 'sSup':
        e, sup = child(n, 'e'), child(n, 'sup')
        return node_text(e) + '^' + brace(node_text(sup))
    if tag == 'sSubSup':
        e, sub, sup = child(n, 'e'), child(n, 'sub'), child(n, 'sup')
        return node_text(e) + '_' + brace(node_text(sub)) + '^' + brace(node_text(sup))
    if tag == 'f':
        num, den = child(n, 'num'), child(n, 'den')
        return brace(node_text(num)) + '/' + brace(node_text(den))
    if tag == 'rad':
        deg, e = child(n, 'deg'), child(n, 'e')
        d = node_text(deg).strip()
        return ('√' + ('(' + d + ')' if d else '') + '(' + node_text(e) + ')')
    if tag == 'nary':
        pr = child(n, 'naryPr') or n
        chrnode = child(pr, 'chr')
        op = chrnode.get(M + 'val') if chrnode is not None else '∑'
        sub, sup, e = child(n, 'sub'), child(n, 'sup'), child(n, 'e')
        s = op or '∑'
        if sub is not None and node_text(sub).strip():
            s += '_' + brace(node_text(sub))
        if sup is not None and node_text(sup).strip():
            s += '^' + brace(node_text(sup))
        return s + '(' + node_text(e) + ')'
    if tag == 'd':
        pr = child(n, 'dPr') or n
        beg, end = child(pr, 'begChr'), child(pr, 'endChr')
        b = beg.get(M + 'val') if beg is not None else None
        en = end.get(M + 'val') if end is not None else None
        b = b if b is not None else '('
        en = en if en is not None else ')'
        inner = ''.join(node_text(c) for c in n if ln(c.tag) == 'e')
        return b + inner + en
    return ''.join(node_text(c) for c in n)

def para_text(p):
    return node_text(p)

def para_images(p):
    res = []
    for n in p.iter():
        rid = None
        if n.tag == A + 'blip':
            rid = n.get(R + 'embed')
        elif n.tag in (VML + 'imagedata', W + 'imagedata'):
            rid = n.get(R + 'id')
        if rid and rid in relmap:
            res.append(data_uri(relmap[rid]))
    return res

SEC_RE = re.compile(r'^\s*(.+?部分)（共[：:]\s*(\d+)\s*道）\s*$')
Q_RE = re.compile(r'^\s*(\d{1,3})\s*[.．、]\s*(.*)$')
OPT_RE = re.compile(r'^\s*([A-Da-d])\s*[、．.,，:：]\s*(.*)$')
ANS_RE = re.compile(r'^\s*答\s*案\s*[：:]\s*(.+?)\s*$')

sections = []
cur_sec = None
cur_q = None
expected = 1
field = None

def flush_q():
    global cur_q, field
    if cur_q is None:
        return
    cur_q['q'] = cur_q['q'].strip()
    cur_q['o'] = [o.strip() for o in cur_q['o']]
    cur_sec['questions'].append(cur_q)
    cur_q = None
    field = None

def attach_images(ims):
    if not ims or cur_q is None:
        return
    if field == 'stem' or not cur_q['o']:
        cur_q.setdefault('img', []).extend(ims)
    else:
        oi = cur_q.setdefault('oi', [None, None, None, None])
        idx = len(cur_q['o']) - 1
        if idx < 4:
            oi[idx] = oi[idx] or ims[0]

def process(line, ims):
    global cur_sec, cur_q, expected, field
    line = line.strip()
    if not line and not ims:
        return
    m = SEC_RE.match(line)
    if m:
        flush_q()
        cur_sec = {'name': m.group(1).strip(), 'declared': int(m.group(2)), 'questions': []}
        sections.append(cur_sec)
        expected = 1
        return
    if cur_sec is None:
        return  # leading decoration / logo
    m = ANS_RE.match(line)
    if m and cur_q is not None:
        cur_q['a'] = re.sub(r'[^A-Da-d]', '', m.group(1)).upper()
        field = None
        if ims:
            cur_q.setdefault('img', []).extend(ims)
        return
    m = OPT_RE.match(line)
    if m and cur_q is not None:
        cur_q['o'].append(m.group(2))
        cur_q['letters'].append(m.group(1).upper())
        field = 'opt'
        attach_images(ims)
        return
    m = Q_RE.match(line)
    if m and int(m.group(1)) == expected:
        flush_q()
        cur_q = {'no': expected, 'q': m.group(2), 'o': [], 'letters': [], 'a': ''}
        expected += 1
        field = 'stem'
        attach_images(ims)
        return
    if cur_q is None:
        return
    attach_images(ims)
    if line:
        if field == 'stem' or not cur_q['o']:
            cur_q['q'] += ('\n' + line)
        else:
            cur_q['o'][-1] += ('\n' + line)

for p in body.iter(W + 'p'):
    raw = para_text(p)
    ims = para_images(p)
    sublines = raw.split('\n')
    for i, sub in enumerate(sublines):
        process(sub, ims if i == 0 else [])

flush_q()

# One known typo in the source document: "S(S#,Sn,Sd,SA、（" should be "S(S#,Sn,Sd,Sa)（"
SOURCE_FIXES = [('S(S#,Sn,Sd,SA、（', 'S(S#,Sn,Sd,Sa)（')]

data = []
for si, s in enumerate(sections):
    qs = []
    for q in s['questions']:
        stem = q['q']
        for a, b in SOURCE_FIXES:
            stem = stem.replace(a, b)
        item = {'no': q['no'], 'q': stem, 'o': q['o'], 'a': q['a']}
        if q.get('img'):
            item['img'] = q['img']
        if q.get('oi') and any(q['oi']):
            item['oi'] = q['oi']
        qs.append(item)
    data.append({'id': si, 'name': s['name'], 'questions': qs})

with open(out, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, separators=(',', ':'))

problems = []
for s in sections:
    if len(s['questions']) != s['declared']:
        problems.append('%s declared %d got %d' % (s['name'], s['declared'], len(s['questions'])))
    for q in s['questions']:
        if len(q['o']) != 4 or q['letters'] != ['A', 'B', 'C', 'D'] or q['a'] not in 'ABCD' or len(q['a']) != 1:
            problems.append('%s #%d opts=%s letters=%s ans=%r' % (s['name'], q['no'], len(q['o']), q['letters'], q['a']))
print('sections:', [(d['name'], len(d['questions'])) for d in data])
print('total questions:', sum(len(d['questions']) for d in data))
print('with stem image:', sum(1 for d in data for q in d['questions'] if q.get('img')))
print('with option image:', sum(1 for d in data for q in d['questions'] if q.get('oi')))
print('empty stems:', sum(1 for d in data for q in d['questions'] if not q['q']))
print('empty options:', sum(1 for d in data for q in d['questions'] for o in q['o'] if not o))
print('distinct embedded images:', len(cache))
print('json bytes:', os.path.getsize(out))
print('problems:', len(problems))
for p in problems[:30]:
    print(' -', p)
