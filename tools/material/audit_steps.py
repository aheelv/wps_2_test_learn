# -*- coding: utf-8 -*-
"""逐题核验：解题步骤是否落在 WPS Office 教育考试专用版可用功能范围内。

依据：《二级 WPS Office 高级应用与设计考试大纲（2025 年版）》四大模块 + 考场环境
（教育考试专用版为离线、无账号、剔除云端增值服务与高级插件的精简功能集）。

用法：
  python tools/material/audit_steps.py            # 输出逐题结论简表（不输出题目原文）
  python tools/material/audit_steps.py --detail   # 另写 _audit_detail.json 供本地修订使用
"""
import re, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAGES = ['入门实操课.html', '实操-文字2.html', '实操-文字3.html',
         '实操-表格1.html', '实操-表格2.html', '实操-表格3.html',
         '实操-演示1.html', '实操-演示2.html']

# 规则码 -> (说明, 正则)。命中即需人工复核；FIX 类为确定越界，WARN 类为需结合上下文判断。
RULES = [
    ('CLOUD', '在线/云/协作/账号（仅属单选概念题，操作题不可实际调用）',
     r'云文档|上云|云端|云盘|网盘|共享协作|协同编辑|多人编辑|多人协作|分享链接|扫码|登录账号|登录帐号|稻壳|在线模板|在线素材|云字体|WPS\s?云'),
    ('AI', 'AI/会员增值/联网智能工具',
     r'WPS\s?AI|AI\s?写作|智能助手|智能写作|智能美化|一键生成|OCR|图片转文字|PDF\s?转\s?Word|文档修复|数据恢复|文档翻译|语音输入|论文查重|超级简历'),
    ('EXT', '外部程序/插件/宏/开发工具/联网下载',
     r'Office\s?365|OneDrive|Photoshop|插件|加载项|VBA|\b宏\b|Power\s?Query|Power\s?Pivot|命令行|注册表|下载安装|联网|第三方软件|控件工具箱|开发工具'),
    ('MSO', '其他套件功能路径或文件类型名（表述不当）',
     r'Word\s?文件|Excel\s?工作簿|PowerPoint|检查兼容性|检查问题|现有文件或网页|变体'),
    ('VER', '版本口径残留（小版本号 / 旧版界面名 / 个人版）',
     r'12\.[x1]|11\.1\.|个人版|WPS\s?20(?:10|13|16|19)|Word\s?文件|Excel\s?工作簿|or\s?PowerPoint'),
    ('TAB', '旧版选项卡名「页面布局」当作界面入口',
     r'「\s*页面布局\s*」|页面布局\s*→|页面布局\s*选项卡'),
    ('NEWFUNC', '新版函数（教育考试专用版精简函数集不保证提供，宜用等价经典写法）',
     r'\bIFS\s*\(|\bTEXTJOIN\s*\(|\bXLOOKUP\s*\(|\bUNIQUE\s*\(|\bFILTER\s*\(|\bLET\s*\(|\bLAMBDA\s*\(|\bMAXIFS\s*\(|\bCONCAT\s*\('),
    ('NEWFX', '新版/非经典切换与对象',
     r'平滑|3D\s?模型|3D\s?效果|缩放定位|平滑切换'),
    ('NET', '离线考场无法执行或验证的外部动作',
     r'https?://|打开浏览器|访问网址|发送邮件|邮件发送|上传到|上云|U\s?盘|手机端|小程序'),
    # 以下为「全面核验」补充规则：云端/AI/新版专属能力、版本混用表述
    ('CLOUD2', '在线/云/协作的其它表述',
     r'文档上云|在线编辑|在线文档|协同编辑|多人同时|团队共享|分享给|链接分享|云端同步|WPS\s?云|云字体|网盘|上传到云'),
    ('AI2', 'AI / 会员增值服务',
     r'AI\s?助手|WPS\s?AI|智能摘要|智能排版|一键美化|AI\s?生成|论文查重|文档翻译|OCR|语音转文字|PDF\s?转\s?Word|图片转文字|文档修复|批量转换工具|超级简历'),
    ('MSO2', '新版/其他套件专属对象与开发功能',
     r'3D\s?模型|3D\s?效果|缩放定位|墨迹书写|屏幕录制|开发工具|ActiveX|控件工具箱|宏录制|加载宏|VBA|Power\s?Map|Power\s?View|Python\s?脚本'),
    ('MIXVER', '版本混用或不确定表述',
     r'部分版本|较新版本|旧版可用|视版本而定|不同版本|个人版|新版才有|版本差异'),
]


def strip_tags(s):
    return re.sub(r'\s+', ' ', re.sub(r'</?[A-Za-z][^>]*>', ' ', s)).strip()


def load():
    out = []
    for ci, fn in enumerate(PAGES, 1):
        s = (ROOT / fn).read_text(encoding='utf-8')
        arts = re.findall(r'<article class="ex"[^>]*>(.*?)</article>', s, re.S)
        for k, a in enumerate(arts, 1):
            no = re.search(r'class="ex-no"[^>]*>(.*?)<', a, re.S)
            no = strip_tags(no.group(1)) if no else '(无题号)'
            steps = [strip_tags(x) for x in re.findall(
                r'<li[^>]*>(.*?)</li>', ''.join(re.findall(r'<ol class="steps">(.*?)</ol>', a, re.S)), re.S)]
            m = re.search(r'<div class="req">(.*?)(?:<div class="kicker">解题步骤|<ol class="steps">)',
                          a, re.S)
            req = strip_tags(m.group(1)) if m else ''
            m = re.search(r'<div class="score">(.*?)</div>', a, re.S)
            score = strip_tags(m.group(1)) if m else ''
            out.append(dict(ci=ci, seq=k, no=no, page=fn, steps=steps, req=req, score=score))
    return out


def scan(q):
    hits = []
    for code, desc, pat in RULES:
        for i, t in enumerate(q['steps'], 1):
            if re.search(pat, t, re.I):
                hits.append(dict(rule=code, where='step', idx=i, text=t))
        for field in ('req', 'score'):
            if re.search(pat, q[field] or '', re.I):
                hits.append(dict(rule=code, where=field, idx=0, text=q[field]))
    return hits


def main():
    qs = load()
    table, detail = [], []
    for q in qs:
        h = scan(q)
        codes = sorted(set(x['rule'] for x in h))
        table.append(dict(no=q['no'], ci=q['ci'], seq=q['seq'],
                          steps=len(q['steps']), rules=codes, n=len(h)))
        for x in h:
            detail.append(dict(no=q['no'], ci=q['ci'], page=q['page'], **x))
    if '--detail' in sys.argv:
        json.dump(detail, open(Path(__file__).parent / '_audit_detail.json', 'w', encoding='utf-8'),
                  ensure_ascii=False, indent=1)
    if '--report' in sys.argv:
        rep = []
        for q, r in zip(qs, table):
            rep.append(dict(no=q['no'], ci=q['ci'], seq=q['seq'], page=q['page'],
                            steps=len(q['steps']), violations=r['rules'],
                            verdict='PASS' if not r['rules'] else 'FAIL'))
        json.dump(rep, open(Path(__file__).parent / 'verify_compliance.json', 'w',
                            encoding='utf-8'), ensure_ascii=False, indent=1)
        print('逐题结论已写入 tools/material/verify_compliance.json')
    print('题目数 %d ｜ 解题步骤总数 %d ｜ 命中规则条目 %d' %
          (len(qs), sum(len(q['steps']) for q in qs), len(detail)))
    print('\n=== 逐题结论（命中规则的题目） ===')
    for r in table:
        if r['rules']:
            print('  第%d次课 %-9s 步骤%2d  命中 %s (%d 处)' %
                  (r['ci'], r['no'], r['steps'], ','.join(r['rules']), r['n']))
    print('\n=== 规则汇总 ===')
    for code, desc, _ in RULES:
        n = sum(1 for d in detail if d['rule'] == code)
        items = sorted(set(d['no'] for d in detail if d['rule'] == code))
        print('  %-8s %2d 处 ｜ 涉及 %d 题 ｜ %s' % (code, n, len(items), ' '.join(items)))
    print('\n=== 无命中题目数 ===')
    print('  %d / %d' % (sum(1 for r in table if not r['rules']), len(table)))


if __name__ == '__main__':
    main()
