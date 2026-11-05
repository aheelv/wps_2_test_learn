# -*- coding: utf-8 -*-
"""逐题核验后的最小化修订：把解题步骤里超出 WPS Office 教育考试专用版
可用功能范围（考场离线、精简经典功能集）的操作换成等价可用操作，并同步
题干、采分点、知识清单、素材说明与生成数据。

原则：只改下表列出的片段；题意、题目顺序、最终答案形态、其余原文不动。
"""
import json, zipfile, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MF = json.load(open(ROOT / 'tools/material/manifest.json', encoding='utf-8'))

# ---------------------------------------------------------------- 网页精确替换
HTML = {}

HTML['实操-表格1.html'] = [
    # 例 4-2：旧版选项卡名 -> 教育版「页面」
    ('「<b>页面布局</b>」', '「<b>页面</b>」'),
    # 例 4-8：新版 IFS -> 教育版经典 IF + AND 区间写法（E 列结果不变）
    ('<li><b>IFS 重写。</b>E2 输入 <span class="fx">=IFS(B2&gt;=90,&quot;优&quot;,'
     'B2&gt;=80,&quot;良&quot;,B2&gt;=70,&quot;中&quot;,B2&gt;=60,&quot;及格&quot;,'
     'TRUE,&quot;不及格&quot;)</span> → 下拉。<br>IFS 的写法是「条件1,结果1,条件2,结果2…」，'
     '最后用 <code>TRUE</code> 兜底。</li>',
     '<li><b>IF + AND 重写。</b>E2 输入 <span class="fx">=IF(B2&gt;=90,&quot;优&quot;,'
     'IF(AND(B2&gt;=80,B2&lt;90),&quot;良&quot;,IF(AND(B2&gt;=70,B2&lt;80),&quot;中&quot;,'
     'IF(AND(B2&gt;=60,B2&lt;70),&quot;及格&quot;,&quot;不及格&quot;))))</span> → 下拉。<br>'
     '用 <code>AND</code> 把每个区间的上下界写全，条件之间不重叠、不留空档。</li>'),
    ('在 E2 用 <b>IFS</b> 重写同一逻辑，下拉。',
     '在 E2 用 <b>IF + AND</b> 按区间重写同一逻辑，下拉。'),
    ('E 列 IFS 与 D 列结果完全一致', 'E 列 IF + AND 与 D 列结果完全一致'),
    ('IFS 最后没有兜底条件：低于 60 的行显示 #N/A。',
     '区间条件没写全上下界：低于 60 的行会落到错误等级。'),
    ('优先改用 IFS（清晰、不易错）', '优先把区间条件用 AND 写全（清晰、不易错）'),
    ('IF 三级跳：单条件 → 嵌套五级 → IFS + AND/OR 组合',
     'IF 三级跳：单条件 → 嵌套五级 → IF + AND/OR 组合'),
    ('IF 三级跳：单条件 → 嵌套五级 → IFS + ',
     'IF 三级跳：单条件 → 嵌套五级 → IF + AND/OR '),
    ('<span class="badge info">IFS</span>', '<span class="badge info">IF + AND</span>'),
    ('IF 单条件、IF 嵌套多级、IFS 多条件（新版）',
     'IF 单条件、IF 嵌套多级、IF + AND 区间组合'),
    ('IF/IFS/AND/OR 嵌套', 'IF/AND/OR 嵌套'),
]

HTML['实操-表格2.html'] = [
    # 例 5-3：新版 TEXTJOIN / CONCAT -> 教育版经典 & 连接符（J2 结果不变）
    ('TEXT/TEXTJOIN</li>', 'TEXT/CONCATENATE</li>'),
    ('CONCAT / TEXTJOIN / &amp; 合并文本', 'CONCATENATE / &amp; 合并文本'),
    ('在 <b>J2</b> 用 <b>TEXTJOIN</b> 把姓名与电话合并为「姓名：电话」。',
     '在 <b>J2</b> 用 <b>&amp; 连接符</b> 把姓名与电话合并为「姓名：电话」。'),
    ('<span class="fx">=TEXTJOIN(&quot;：&quot;,TRUE,A2,C2)</span>',
     '<span class="fx">=A2&amp;&quot;：&quot;&amp;C2</span>'),
    ('TEXTJOIN 的第一参数是分隔符，第二参数 TRUE 表示忽略空单元格。',
     '用 <code>&amp;</code> 把单元格与分隔符串起来，分隔符必须放在英文双引号里。'),
    ('J 列 TEXTJOIN 分隔符与忽略空值正确', 'J 列连接符与分隔符正确'),
    ('TEXTJOIN 第二参数写 FALSE：空单元格会多出分隔符。',
     '分隔符漏写英文双引号，或误用全角标点当连接符：J 列会报错或格式不符。'),
]

HTML['实操-演示1.html'] = [
    # 例 7-3：「变体」为其他套件功能名；教育版「设计」选项卡为 主题/配色/字体/背景/母版
    ('主题的应用与「变体」（配色/字体/效果组合）', '主题的应用与「配色」「字体」下拉'),
    ('<li><b>换变体。</b>「设计」→「<b>变体</b>」→ 展开后选一种'
     '（不同变体主要改配色深浅与字体搭配）。</li>',
     '<li><b>换配色。</b>「设计」→「<b>配色</b>」→ 展开后选一种'
     '（不同配色主要改图表与形状的颜色深浅）。</li>'),
    ('<b>改配色。</b>「变体」→「<b>颜色</b>」', '<b>改配色。</b>「设计」→「<b>配色</b>」'),
    ('<b>改字体。</b>「变体」→「<b>字体</b>」', '<b>改字体。</b>「设计」→「<b>字体</b>」'),
    ('「聚合」主题及变体', '「聚合」主题及配色方案'),
    ('再选用一种<b>变体</b>。', '再选用一种<b>配色方案</b>。'),
    ('<span class="badge info">变体</span>', '<span class="badge info">配色方案</span>'),
    ('主题 + 变体 + 渐变背景', '主题 + 配色方案 + 渐变背景'),
    ('主题与变体、配色与字体方案', '主题应用、配色与字体方案'),
    ('会应用主题与变体', '会应用主题与配色方案'),
    ('<b>变体</b>是主题的预设组合，<b>单独改配色/字体</b>只动其中一层。',
     '<b>配色</b>与<b>字体</b>在「设计」选项卡分别设置，'
     '<b>单独改配色/字体</b>只动其中一层。'),
]

HTML['实操-演示2.html'] = [
    # 例 8-3：离线考场无法访问外部网址，超链接改为「本文档中的位置」
    ('<li>在第 6 张的图片上设超链接，指向网址 '
     '<code>https://ncre.neea.edu.cn/</code>。</li>',
     '<li>在第 6 张的图片上设超链接，指向本文档 <b>第 2 张（目录页）</b>。</li>'),
    ('<li><b>图片超链接。</b>选中第 6 张的图片 → 右键 →「<b>超链接</b>」→ '
     '左侧选「<b>现有文件或网页</b>」→ 在地址栏输入 '
     '<code>https://ncre.neea.edu.cn/</code> → 确定。</li>',
     '<li><b>图片超链接。</b>选中第 6 张的图片 → 右键 →「<b>超链接</b>」→ '
     '左侧选「<b>本文档中的位置</b>」→ 选「<b>第 2 张（目录页）</b>」→ 确定。</li>'),
    ('点图片应打开浏览器；', '点图片应跳到第 2 张；'),
    # 例 8-6：「文件→信息→检查问题→检查兼容性」为其他套件路径，教育版用「检查文档」
    ('<li><b>看兼容性。</b>「文件」→「信息」→「<b>检查问题</b>」→'
     '「<b>检查兼容性</b>」→ 列表会提示哪些效果在旧版不可用（如某些切换、3D 效果）。'
     '记下并酌情替换。</li>',
     '<li><b>查文档。</b>「文件」→「<b>检查文档</b>」→ 按提示检查隐藏信息与辅助功能，'
     '确认没有依赖联网或新版专属效果。记下检查结果。</li>'),
    # 例 8-7：主题变体 -> 配色
    ('→ 变体选一种。', '→ 配色选一种。'),
    # 切换「平滑」为新版效果，教育版用经典「淡入淡出」
    ('所有页都变平滑，前功尽弃。', '所有页都跟着变，前功尽弃。'),
    ('平滑', '淡入淡出'),
]

HTML['实操训练.html'] = [
    ('主题与变体、渐变与图片背景', '主题与配色方案、渐变与图片背景'),
    ('主题 + 变体 + 渐变背景', '主题 + 配色方案 + 渐变背景'),
]

# ---------------------------------------------------------------- 生成数据 / 素材说明（纯文本同步）
TEXT = [
    # 旧界面名（生成数据早于上一轮版本统一，需同步，避免重跑时回退）
    ('「页面布局」', '「页面」'),
    ('「页面布局 →', '「页面 →'),
    # 例 4-8：JSON / 说明为纯文本（无 HTML 实体），整段换成等价嵌套 IF
    ('=IFS(B2>=90,"优",B2>=80,"良",B2>=70,"中",B2>=60,"及格",TRUE,"不及格")',
     '=IF(B2>=90,"优",IF(AND(B2>=80,B2<90),"良",IF(AND(B2>=70,B2<80),"中",'
     'IF(AND(B2>=60,B2<70),"及格","不及格"))))'),
    ('IFS 的写法是「条件1,结果1,条件2,结果2…」，最后用 TRUE 兜底。',
     '用 AND 把每个区间的上下界写全，条件之间不重叠、不留空档。'),
    ('IFS 重写。', 'IF + AND 重写。'),
    ('用 IFS 重写同一逻辑', '用 IF + AND 按区间重写同一逻辑'),
    ('IFS 最后没有兜底条件：低于 60 的行显示 #N/A。',
     '区间条件没写全上下界：低于 60 的行会落到错误等级。'),
    ('优先改用 IFS（清晰、不易错）', '优先把区间条件用 AND 写全（清晰、不易错）'),
    ('→ IFS + AND/OR 组合', '→ IF + AND/OR 组合'),
    ('→ IFS + ', '→ IF + AND/OR '),
    ('E 列 IFS 与 D 列', 'E 列 IF + AND 与 D 列'),
    ('IFS 多条件（新版）', 'IF + AND 区间组合'),
    ('IF/IFS/AND/OR', 'IF/AND/OR'),
    # 例 5-3：整段换成等价连接符写法（J2 结果不变）
    ('=TEXTJOIN("：",TRUE,A2,C2)', '=A2&"："&C2'),
    ('TEXTJOIN 的第一参数是分隔符，第二参数 TRUE 表示忽略空单元格。',
     '用 & 把单元格与分隔符串起来，分隔符必须放在英文双引号里。'),
    ('TEXTJOIN 第二参数写 FALSE：空单元格会多出分隔符。',
     '分隔符漏写英文双引号，或误用全角标点当连接符：J 列会报错或格式不符。'),
    ('J 列 TEXTJOIN 分隔符与忽略空值正确', 'J 列连接符与分隔符正确'),
    ('用 TEXTJOIN 把', '用 & 连接符把'),
    ('TEXTJOIN', '& 连接符'),
    ('CONCAT / & 连接符', 'CONCATENATE'),
    ('TEXT/& 连接符', 'TEXT/CONCATENATE'),
    # 演示：功能名 / 效果名 / 离线外部动作
    ('变体', '配色方案'),
    ('平滑', '淡入淡出'),
    ('所有页都变淡入淡出，前功尽弃。', '所有页都跟着变，前功尽弃。'),
    ('现有文件或网页', '本文档中的位置'),
    ('检查兼容性', '检查文档'),
    ('检查问题', '检查文档'),
    ('3D 效果', '新版专属效果'),
    ('打开浏览器', '跳到第 2 张'),
    ('指向网址 https://ncre.neea.edu.cn/', '指向本文档第 2 张（目录页）'),
    ('在地址栏输入 https://ncre.neea.edu.cn/', '选「第 2 张（目录页）」'),
    ('https://ncre.neea.edu.cn/', '本文档第 2 张（目录页）'),
]

NOTE_FILES = [
    '练习5-3-身份证与文本函数', '练习7-3-主题与背景',
    '练习8-2-切换与排练计时', '练习8-3-超链接与动作',
    '练习8-7-六页汇报综合题',
]


COUNT = [0]


def apply(s, pairs):
    n = 0
    for old, new in pairs:
        c = s.count(old)
        if c:
            s = s.replace(old, new)
            n += c
    return s, n


def walk(o):
    """结构化遍历 JSON，避免 JSON 转义（\\"）导致整段公式替换落空。"""
    if isinstance(o, str):
        s, n = apply(o, TEXT)
        COUNT[0] += n
        return s
    if isinstance(o, list):
        return [walk(x) for x in o]
    if isinstance(o, dict):
        return {k: walk(v) for k, v in o.items()}
    return o


def sync_exercises_from_html():
    """以修订后的网页为准，回写生成数据的 reqs / steps / score，
    保证下次重跑 build.py 时素材说明不会退回旧文案。题号、顺序、src 等字段不动。"""
    import html as H
    pages = ['入门实操课.html', '实操-文字2.html', '实操-文字3.html',
             '实操-表格1.html', '实操-表格2.html', '实操-表格3.html',
             '实操-演示1.html', '实操-演示2.html']

    def clean(s):
        # 与最初解析 exercises.json 时的口径一致：去标签不留空格，避免产生无意义差异
        return re.sub(r'\s+', ' ', H.unescape(re.sub(r'<[^>]+>', '', s))).strip()

    p = ROOT / 'tools/material/exercises.json'
    data = json.loads(p.read_text(encoding='utf-8'))
    by = {(x['ci'], x['seq']): x for x in data}
    changed = 0
    for ci, fn in enumerate(pages, 1):
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


def main():
    print('=== 网页精确替换（幂等：已修订的片段自动跳过） ===')
    for fn, pairs in HTML.items():
        p = ROOT / fn
        s = p.read_text(encoding='utf-8')
        s2, n = apply(s, pairs)
        if s2 != s:
            p.write_text(s2, encoding='utf-8')
        print('  %-22s 本次 %2d 处' % (fn, n))

    print('=== 生成数据同步 ===')
    for name in ('exercises.json', '_steps.json'):
        p = ROOT / 'tools/material' / name
        if not p.exists():
            continue
        COUNT[0] = 0
        obj = walk(json.loads(p.read_text(encoding='utf-8')))
        p.write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding='utf-8')
        print('  %-18s 本次 %d 处（JSON 结构校验通过）' % (name, COUNT[0]))
    n = sync_exercises_from_html()
    print('  exercises.json 字段回写 %d 处（以修订后网页为准）' % n)

    print('=== 素材说明与 zip 同步 ===')
    for folder in NOTE_FILES:
        d = ROOT / '练习素材' / folder
        f = d / '素材说明.txt'
        s2, n = apply(f.read_text(encoding='utf-8'), TEXT)
        f.write_text(s2, encoding='utf-8')
        # 只重打这一个包，文件顺序与 manifest 保持一致
        rec = next(r for r in MF if r['folder'] == folder)
        zp = ROOT / '练习素材' / '下载' / rec['zip']
        with zipfile.ZipFile(zp, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
            for fn in rec['files']:
                z.write(d / fn, arcname=folder + '/' + fn)
        print('  %-24s 说明 %d 处，zip 已重打' % (folder, n))

    print('\n=== 修订后残留扫描（解题步骤相关词） ===')
    files = [ROOT / f for f in HTML] + [ROOT / 'tools/material/exercises.json'] + \
            [ROOT / '练习素材' / f / '素材说明.txt' for f in NOTE_FILES]
    words = ['「页面布局」', 'IFS(', 'TEXTJOIN', 'CONCAT /', '变体', '平滑',
             '现有文件或网页', '检查兼容性', '检查问题', '3D 效果', '打开浏览器']
    bad = 0
    for p in files:
        s = p.read_text(encoding='utf-8')
        left = {w: s.count(w) for w in words if s.count(w)}
        # 页脚官方信息链接不属于题目内容，单独排除
        if 'https://ncre.neea.edu.cn/' in s and p.suffix == '.html':
            pass
        if left:
            print('  %-26s %s' % (p.name, left))
            bad += sum(left.values())
    print('  残留合计（不含官方信息链接）：%d' % bad)


if __name__ == '__main__':
    main()
