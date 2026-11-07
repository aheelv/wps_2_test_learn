# -*- coding: utf-8 -*-
"""为 72 道题生成「模拟操作截图」（SVG 界面示意图）。

每张图严格绑定本题：
  · 窗口 / 选项卡 / 功能区 = WPS Office 教育考试专用版现行界面（复用 tools/pdf/ui.py）；
  · 高亮的功能命令 = 本题解题步骤里真实出现的入口；
  · 编辑区文字 / 数据 = 从本题素材包主文件实时读取；
  · 下方编号 = 该题解题步骤在网页 <ol class="steps"> 中的真实序号；
  · 右侧完成效果 = 该题题目要求与采分点。

输出：练习素材/完成比对/<素材包同名目录>/操作示意.svg
用法：python tools/material/make_shots.py
"""
import os, re, sys, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools' / 'pdf'))
import ui

E = json.load(open(ROOT / 'tools/material/exercises.json', encoding='utf-8'))
M = json.load(open(ROOT / 'tools/material/manifest.json', encoding='utf-8'))
BY = {(r['ci'], r['seq']): r for r in M}
OUT = ROOT / '练习素材' / '完成比对'

APP = {1: 'wps', 2: 'wps', 3: 'wps', 4: 'et', 5: 'et', 6: 'et', 7: 'wpp', 8: 'wpp'}
EXT = {'wps': 'docx', 'et': 'xlsx', 'wpp': 'pptx'}
APPNAME = {'wps': 'WPS 文字', 'et': 'WPS 表格', 'wpp': 'WPS 演示'}
TABS = {'wps': ui.TABS_W, 'et': ui.TABS_S, 'wpp': ui.TABS_P}

def rib_wpp_design_wide():
    """「设计」选项卡首组长标签留足宽度，避免「幻灯片大小」被画布边缘裁切。"""
    g = ui.rib_wpp_design()
    return [(g[0][0], 190, [[("big", "幻灯片大小", 72, "slide"),
                             ("big", "主题", 52, "slide")]])] + list(g[1:])


GROUPS = {
    ('wps', '开始'): ui.rib_wps_home, ('wps', '插入'): ui.rib_wps_insert,
    ('wps', '页面'): ui.rib_wps_page, ('wps', '引用'): ui.rib_wps_ref,
    ('wps', '审阅'): ui.rib_wps_review, ('wps', '视图'): ui.rib_wps_view,
    ('et', '开始'): ui.rib_et_home, ('et', '插入'): ui.rib_et_insert,
    ('et', '页面'): ui.rib_et_page, ('et', '公式'): ui.rib_et_formula,
    ('et', '数据'): ui.rib_et_data, ('et', '审阅'): ui.rib_et_review,
    ('wpp', '开始'): ui.rib_wpp_home, ('wpp', '插入'): ui.rib_wpp_insert,
    ('wpp', '设计'): rib_wpp_design_wide, ('wpp', '动画'): ui.rib_wpp_anim,
    ('wpp', '切换'): ui.rib_wpp_slide, ('wpp', '放映'): ui.rib_wpp_slide,
}

# 功能入口关键词 -> 优先选项卡（同一模块内按命中数取最高）
TAB_HINT = [
    ('页面', r'页边距|纸张|页面设置|打印区域|打印标题|分页|分栏|页眉|页脚|水印|页面边框|缩放'),
    ('引用', r'目录|题注|交叉引用|脚注|尾注|索引|书目|邮件合并|域'),
    ('审阅', r'修订|批注|比较|拼写|保护文档|限制编辑|检查文档|文档加密'),
    ('插入', r'插入图片|插入表格|形状|文本框|艺术字|超链接|图表|音频|视频|对象|符号'),
    ('公式', r'公式|函数|插入函数|名称管理器|公式求值|追踪|SUM|IF\s*\(|VLOOKUP'),
    ('数据', r'排序|筛选|高级筛选|分类汇总|合并计算|数据透视|数据验证|有效性|模拟分析|方案'),
    ('设计', r'主题|配色|字体方案|背景|母版|幻灯片大小'),
    ('切换', r'切换效果|切换|排练计时|放映|设置放映'),
    ('动画', r'动画|动画窗格|效果选项|触发器|淡入|淡出'),
    ('开始', r'字体|字号|对齐|行距|缩进|样式|边框|条件格式|单元格|复制|粘贴|查找|替换'),
]


def pick_tab(q, app):
    body = ' '.join(q['steps'] + q['reqs'])
    allowed = set(TABS[app])
    best, score = '开始', 0
    for tab, pat in TAB_HINT:
        if tab not in allowed:
            continue
        n = len(re.findall(pat, body))
        # 开始 作为兜底，不抢占专属选项卡
        if tab == '开始':
            n = n // 3
        if n > score:
            best, score = tab, n
    return best


def quoted_words(q):
    w = []
    for s in q['steps'] + q['reqs']:
        w += re.findall(r'「([^」]{1,14})」', s)
    out = []
    for x in w:
        if x not in out:
            out.append(x)
    return out


def cut(s, n):
    s = re.sub(r'\s+', ' ', s).strip()
    return s if len(s) <= n else s[:n - 1] + '…'


def step_paths(q):
    """按步骤真实序号生成操作路径摘要；不重编号、不改顺序。"""
    out = []
    for i, s in enumerate(q['steps'], 1):
        cmds = re.findall(r'「([^」]{1,14})」', s)
        path = ' → '.join(cmds[:4]) if cmds else ''
        if not path:
            path = re.split(r'[。；]', s)[0]
        out.append((i, cut(path, 34)))
    return out


def source_preview(rec, app):
    """从本题素材包主文件读取真实内容，保证截图与素材一一对应。

    返回 (主文件名, 文本行, 表格单元格)。xlsx 取数据量最大的工作表，
    避免把「说明」页当成起始数据区。
    """
    d = ROOT / '练习素材' / rec['folder']
    ext = EXT[app]
    fns = [x for x in rec['files'] if x.endswith('.' + ext)]
    if not fns:
        return '(本题为多文档题)', [], []
    fn = fns[0]
    lines, cells = [], []
    try:
        p = d / fn
        if ext == 'docx':
            from docx import Document
            lines = [cut(x.text.strip(), 30) for x in Document(str(p)).paragraphs
                     if x.text.strip()][:7]
        elif ext == 'xlsx':
            from openpyxl import load_workbook
            wb = load_workbook(str(p), read_only=True, data_only=True)
            ws = max(wb.worksheets, key=lambda w: w.max_row * w.max_column)
            for row in ws.iter_rows(min_row=1, max_row=8, max_col=5, values_only=True):
                cells.append(['' if v is None else str(v) for v in row])
            lines = [cut(' | '.join(c), 30) for c in cells[:7]]
            wb.close()
        else:
            from pptx import Presentation
            prs = Presentation(str(p))
            for i, sl in enumerate(prs.slides, 1):
                if len(lines) >= 7:
                    break
                t = ' '.join(sh.text.strip() for sh in sl.shapes
                             if sh.has_text_frame and sh.text.strip())
                lines.append(cut(t or '第 %d 张幻灯片' % i, 30))
    except Exception as ex:
        lines = ['(素材读取异常：%s)' % type(ex).__name__]
    return fn, [x for x in lines if x][:7], cells[:8]


def card(f, x, y, w, h, title, lines, accent=None):
    f.rect(x, y, w, h, '#ffffff', ui.K['line2'], 1, 4)
    f.rect(x, y, w, 27, accent or '#eef2f8', 'none', 0, 4)
    f.txt(x + 12, y + 18, title, 12, ui.K['txt'], bold=True)
    cy = y + 46
    for ln in lines:
        f.txt(x + 12, cy, cut(ln.rstrip('…'), 19), 10.8, ui.K['txt2'])
        cy += 19


def drawing(q, rec):
    app, ci, seq = APP[q['ci']], q['ci'], q['seq']
    tab = pick_tab(q, app)
    groups = GROUPS.get((app, tab), GROUPS[(app, '开始')])()
    fn, srclines, src_cells = source_preview(rec, app)
    paths = step_paths(q)
    words = quoted_words(q)

    f = ui.Fig(1000, 690)
    title = '%s - WPS Office 教育考试专用版' % fn
    ry, by, bh = ui.window(f, 1000, 690, title, app, TABS[app], tab,
                           rib_h=86, status_left='就绪　｜　第 %d 次课 · %s　｜　界面示意' % (ci, q['no']))
    # 右移 8px，避免最左侧「幻灯片大小」等长标签被画布边缘裁切
    ui.ribbon(f, 8, ry, 984, groups, h=86)

    # 功能区：把本题步骤真实用到的命令描橙框（教育版功能区内的既有命令，不虚构入口）
    body = ' '.join(q['steps'])
    labels = []
    for g in groups:
        for row in g[2]:
            for el in row:
                if el[0] in ('big', 'btn', 'combo'):
                    labels.append((el[0], el[1]))
    hit = 0
    for kind, lab in labels:
        if hit >= 6:
            break
        if len(lab) < 2 or lab not in body and lab not in words:
            continue
        p = f.pos(kind + ':' + lab)
        if not p:
            continue
        x, y = p
        w = 52 if kind == 'big' else 34
        f.rect(x - w / 2, y - 27, w, 52, 'none', ui.K['mark'], 1.6, 3, op=0.9)
        hit += 1

    # ---- 编辑区 ----
    top, eh = by + 8, 316
    f.rect(0, top, 1000, eh, ui.K['doc'])
    card(f, 18, top + 10, 246, eh - 20, '本题起始素材 · %s' % APPNAME[app],
         [cut(fn, 26)] + ['· ' + cut(x, 24) for x in srclines[:6]], '#eef4ff')

    mx, mw = 278, 452
    if app == 'wps':
        f.rect(mx, top + 10, mw, eh - 20, '#ffffff', ui.K['line2'], 1, 2)
        f.txt(mx + mw / 2, top + 48, cut(q['title'], 22), 15, '#1a2129', 'middle', bold=True)
        cy = top + 82
        for ln in srclines[:6]:
            f.rect(mx + 26, cy - 9, mw - 52, 4, '#d6dce5', 'none', 0, 2)
            if ln:
                f.txt(mx + 26, cy + 12, cut(ln, 32), 10.5, ui.K['txt2'])
            cy += 30
    elif app == 'et':
        y0, hdrh, rh, cw = top + 14, 20, 27, (mw - 34) / 5
        f.rect(mx, top + 10, mw, eh - 20, '#ffffff', ui.K['line2'], 1, 2)
        # 列标行（独立于数据行，避免与首行表头文字重叠）
        f.rect(mx, y0, mw, hdrh, ui.K['head'])
        f.line(mx, y0 + hdrh, mx + mw, y0 + hdrh, ui.K['grid'], 1)
        for c in range(5):
            f.line(mx + 34 + c * cw, y0, mx + 34 + c * cw,
                   y0 + hdrh + 7 * rh, ui.K['grid'], 1)
            f.txt(mx + 34 + (c + 0.5) * cw, y0 + 14, chr(65 + c), 10,
                  ui.K['txt2'], 'middle')
        f.line(mx + 34 + 5 * cw, y0, mx + 34 + 5 * cw, y0 + hdrh + 7 * rh, ui.K['grid'], 1)
        f.rect(mx, y0 + hdrh, mw, rh, '#e9f0ff', 'none', 0, 0, op=0.6)
        for r in range(7):
            yy = y0 + hdrh + r * rh
            f.line(mx, yy, mx + mw, yy, ui.K['grid'], 1)
            f.rect(mx, yy, 34, rh, '#fafbfc')
            f.txt(mx + 17, yy + 18, str(r + 1), 10, ui.K['txt3'], 'middle')
            if r < len(src_cells):
                for c, v in enumerate(src_cells[r][:5]):
                    f.txt(mx + 40 + c * cw, yy + 18, cut(v, 9), 10, ui.K['txt2'])
    else:
        f.rect(mx, top + 10, mw, eh - 20, '#ffffff', ui.K['line2'], 1, 2)
        f.rect(mx + 34, top + 40, mw - 68, 196, '#f7f9fc', ui.K['line2'], 1, 3)
        f.txt(mx + mw / 2, top + 112, cut(q['title'], 22), 17, '#1a2129', 'middle', bold=True)
        cy = top + 158
        for ln in srclines[:3]:
            f.txt(mx + mw / 2, cy, '· ' + cut(ln, 26), 11, ui.K['txt2'], 'middle')
            cy += 24
        for i in range(4):
            f.rect(mx + 34 + i * 44, top + 252, 34, 22, '#e9edf3', ui.K['line2'], 0.8, 2)
            f.txt(mx + 51 + i * 44, top + 267, str(i + 1), 10, ui.K['txt3'], 'middle')

    effect = [cut(x, 24) for x in q['reqs'][:4]]
    if q.get('score'):
        effect += ['【采分点】' + cut(q['score'], 22)]
    card(f, 744, top + 10, 238, eh - 20, '完成效果 / 采分点', effect[:6], '#fff5e9')

    # ---- 步骤路径条：编号 = 网页 <ol class="steps"> 的真实序号 ----
    sy = by + 8 + eh
    sh = 690 - 22 - sy
    f.rect(0, sy, 1000, sh, '#f7f9fc')
    f.line(0, sy, 1000, sy, ui.K['line2'], 1)
    f.txt(18, sy + 21, '本题解题步骤 · 编号与网页步骤序号一致', 12.5, ui.K['txt'], bold=True)
    f.txt(760, sy + 21, cut('当前界面：%s →「%s」选项卡' % (APPNAME[app], tab), 30),
          11, ui.K['txt3'])
    shown = paths[:12]
    if len(paths) > 12:
        shown.append(('…', '其余 %d 步见网页解题步骤（编号连续）' % (len(paths) - 12)))
    per = (len(shown) + 1) // 2
    for col in range(2):
        for j in range(per):
            k = col * per + j
            if k >= len(shown):
                break
            no, desc = shown[k]
            x = 18 + col * 492
            y = sy + 44 + j * 23
            f.circle(x + 10, y - 4, 9.5, ui.K['mark'])
            f.txt(x + 10, y - 0.5, str(no), 10 if str(no) == '…' else 10.5,
                  '#ffffff', 'middle', bold=True)
            f.txt(x + 27, y, desc, 11.2, ui.K['txt2'])
    f.txt(18, 660, '界面示意 · WPS Office 教育考试专用版（2025 年版考试大纲指定考试环境）'
                    ' · 图中文字与数据取自本题素材包，操作路径取自本题解题步骤', 10, ui.K['txt3'])
    return f.svg()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    n = 0
    for q in E:
        rec = BY[(q['ci'], q['seq'])]
        d = OUT / rec['folder']
        d.mkdir(parents=True, exist_ok=True)
        (d / '操作示意.svg').write_text(drawing(q, rec), encoding='utf-8')
        n += 1
    print('模拟操作截图：%d 张 → %s' % (n, OUT))


if __name__ == '__main__':
    main()
