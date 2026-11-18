# -*- coding: utf-8 -*-
"""背景知识内容质检：结构、字数、禁词、错配风险。

用法：python tools/knowledge/audit.py
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
K = Path(__file__).parent
FIELDS = ['points', 'background', 'principle', 'formula', 'example', 'mistakes', 'exam']

# 版本 / 软件混用禁词（2019 需带版本上下文才算，因为素材里有 2019 年日期）
BAN = [
    (r'\bWord\b', 'Word'), (r'\bExcel\b', 'Excel'),
    (r'\bPowerPoint\b|\bPPT\b', 'PowerPoint/PPT'),
    (r'个人版', '个人版'), (r'专业版', '专业版'), (r'家庭版', '家庭版'),
    (r'WPS\s*20(16|19|21|23|24)', '旧版年份'),
    (r'Office\s*20(16|19|21)', '旧版 Office 年份'),
    (r'微软\s*Office', '微软 Office'),
]

SELF = re.compile(r'<[^>]+>')


def plain(s):
    return SELF.sub('', s).replace('&nbsp;', ' ').strip()


def main():
    data = json.loads((K / 'all.json').read_text(encoding='utf-8'))
    E = {(str(e['ci']) + '-' + str(e['seq'])): e
         for e in json.loads((ROOT / 'tools/material/exercises.json').read_text(encoding='utf-8'))}
    problems = []
    stats = []

    for key in sorted(data, key=lambda x: tuple(map(int, x.split('-')))):
        d = data[key]
        for f in FIELDS:
            if f not in d:
                problems.append((key, '缺字段 ' + f))
        extra = set(d) - set(FIELDS)
        if extra:
            problems.append((key, '多余字段 ' + ','.join(sorted(extra))))
        total = 0
        for f in FIELDS:
            v = d.get(f, '')
            if not isinstance(v, str) or not v.strip():
                problems.append((key, f + ' 为空'))
                continue
            n = len(plain(v))
            total += n
            if n < 110:
                problems.append((key, '%s 过短 %d 字' % (f, n)))
            if n > 620:
                problems.append((key, '%s 过长 %d 字' % (f, n)))
            # 标签白名单
            tags = set(re.findall(r'<\s*([a-zA-Z][\w-]*)', v))
            bad_tags = tags - {'b', 'strong', 'code', 'p', 'br', 'ul', 'li', 'em', 'i', 'span'}
            if bad_tags:
                problems.append((key, '%s 含非法标签 %s' % (f, sorted(bad_tags))))
            # 禁词
            for pat, name in BAN:
                if re.search(pat, v, re.I):
                    problems.append((key, '%s 命中禁词 %s' % (f, name)))
        if total < 1100:
            problems.append((key, '总量偏少 %d 字' % total))
        if 'mistakes' in d and d['mistakes'].count('<li>') < 4:
            problems.append((key, '易错点少于 4 条'))
        # 内容与本题对象的一致性：用 reqs+steps 提取专名（英文函数/文件名/≥3字中文串），
        # 命中任一即认为对应；标题本身多为通用短语（如「从零新建…」），不作强制。
        ex = E.get(key)
        if ex:
            corpus = json.dumps(d, ensure_ascii=False)
            src_text = ' '.join(ex.get('reqs', [])) + ' ' + ' '.join(ex.get('steps', []))
            toks = set(re.findall(r'[A-Za-z][A-Za-z0-9._-]{2,}|[一-龥]{3,}', src_text))
            hit = [t for t in toks if t in corpus]
            if not hit:
                problems.append((key, '内容与题目要求/步骤无任何共同专名：' + ex['title']))
            # 反向：不得出现其他题的专属文件名（练习N-M），除非是本题自己的
            own = '练习%d-%d' % (ex['ci'], ex['seq'])
            # 第 1 次课内题目展示号为「例 2-1 / 3-1 / 4-1」，其文件名也用该展示号，
            # 因此题目自身要求的文件名一律视为合法引用。
            own_refs = set(re.findall(r'练习\d+-\d+', ' '.join(ex.get('reqs', [])) + ' ' +
                                      ' '.join(ex.get('steps', [])) + ' ' + str(ex.get('score', ''))))
            own_refs.add(own)
            foreign = set(re.findall(r'练习\d+-\d+', corpus)) - own_refs
            if foreign:
                problems.append((key, '出现其他题号引用 %s（本题 %s）' % (sorted(foreign), own)))
        stats.append((key, total))

    print('题目数 %d ｜ 单题字数 %d—%d ｜ 平均 %d'
          % (len(stats), min(x[1] for x in stats), max(x[1] for x in stats),
             sum(x[1] for x in stats) // len(stats)))
    print('问题 %d 处' % len(problems))
    for k, p in problems:
        print('  %-7s %s' % (k, p))
    return 0 if not problems else 1


if __name__ == '__main__':
    sys.exit(main())
