# -*- coding: utf-8 -*-
"""逐包对比「修订前（git HEAD）」与「修订后（当前工作区）」的素材包内容差异。

用途：为「素材包与题目完全对应」整改报告提供可核查的事实依据，
      逐题列出原素材情况与修订内容，不依赖人工描述。

用法：
    python tools/material/diff_packages.py            # 生成 pkg_diff_report.json
    python tools/material/diff_packages.py --print 4  # 打印第 4 次课明细
"""
import io
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).parent
MAT = ROOT / '练习素材'
OUTJSON = HERE / 'pkg_diff_report.json'

sys.path.insert(0, str(HERE))


def git_show(path):
    """读取 git HEAD 中的文件字节，不存在返回 None。"""
    p = subprocess.run(['git', 'show', 'HEAD:' + path], cwd=str(ROOT),
                       capture_output=True)
    if p.returncode != 0:
        return None
    return p.stdout


def summarize_docx(data):
    from docx import Document
    d = Document(io.BytesIO(data))
    paras = [x.text.strip() for x in d.paragraphs if x.text.strip()]
    return {'段数': len(paras), '首段': paras[0] if paras else ''}


def summarize_xlsx(data):
    import openpyxl
    wb = openpyxl.load_workbook(io.BytesIO(data))
    sheets = []
    for ws in wb.worksheets:
        head = []
        for row in ws.iter_rows(min_row=1, max_row=1, values_only=True):
            head = [str(c) for c in row if c is not None]
        sheets.append({'表名': ws.title, '表头': head,
                       '行数': ws.max_row})
    return {'表数': len(sheets), '工作表': sheets}


def summarize_pptx(data):
    from pptx import Presentation
    pr = Presentation(io.BytesIO(data))
    pages = []
    for s in pr.slides:
        t = [sh.text_frame.text.strip().split('\n')[0]
             for sh in s.shapes if sh.has_text_frame and sh.text_frame.text.strip()]
        pages.append(t[0] if t else '')
    return {'页数': len(pr.slides), '页标题': pages}


def summarize(name, data):
    try:
        if name.endswith('.docx'):
            return summarize_docx(data)
        if name.endswith('.xlsx'):
            return summarize_xlsx(data)
        if name.endswith('.pptx'):
            return summarize_pptx(data)
    except Exception as e:  # pragma: no cover
        return {'错误': str(e)}
    return None


def main():
    manifest = json.load(open(HERE / 'manifest.json', encoding='utf-8'))
    rows = []
    for r in manifest:
        folder = MAT / r['folder']
        files = sorted(p.name for p in folder.iterdir()
                       if p.is_file() and not p.name.startswith('~$'))
        entry = dict(no=r['no'], ci=r['ci'], seq=r['seq'], title=r['title'],
                     folder=r['folder'], old=[], new=[], changed=False)
        for fn in files:
            new_path = folder / fn
            if fn.endswith(('.docx', '.xlsx', '.pptx')):
                old_data = git_show('练习素材/%s/%s' % (r['folder'], fn))
                new_data = new_path.read_bytes()
                s_old = summarize(fn, old_data) if old_data else None
                s_new = summarize(fn, new_data)
                entry['old'].append(dict(file=fn, sum=s_old))
                entry['new'].append(dict(file=fn, sum=s_new))
                if s_old != s_new:
                    entry['changed'] = True
            else:
                old_data = git_show('练习素材/%s/%s' % (r['folder'], fn))
                new_data = new_path.read_bytes()
                if old_data != new_data:
                    entry['changed'] = True
                entry['old'].append(dict(file=fn, bytes=len(old_data or b'')))
                entry['new'].append(dict(file=fn, bytes=len(new_data)))
        # 文件集合本身的变化
        old_names = set()
        for o in entry['old']:
            old_names.add(o['file'])
        new_names = set(f['file'] for f in entry['new'])
        entry['added_files'] = sorted(new_names - old_names)
        entry['removed_files'] = sorted(old_names - new_names)
        if entry['added_files'] or entry['removed_files']:
            entry['changed'] = True
        rows.append(entry)

    rep = dict(total=len(rows),
               changed=sum(1 for x in rows if x['changed']),
               unchanged=sum(1 for x in rows if not x['changed']),
               rows=rows)
    OUTJSON.write_text(json.dumps(rep, ensure_ascii=False, indent=1),
                        encoding='utf-8')
    print('素材包差异：%d 个包 / 变更 %d / 未变 %d'
          % (rep['total'], rep['changed'], rep['unchanged']))
    print('报告：tools/material/pkg_diff_report.json')

    if '--print' in sys.argv:
        i = sys.argv.index('--print')
        ci = int(sys.argv[i + 1])
        for x in rows:
            if x['ci'] == ci:
                print('\n【%s】%s  %s' % (x['no'], x['title'], x['folder']))
                print('  原：', json.dumps(x['old'], ensure_ascii=False)[:600])
                print('  新：', json.dumps(x['new'], ensure_ascii=False)[:600])


if __name__ == '__main__':
    main()
