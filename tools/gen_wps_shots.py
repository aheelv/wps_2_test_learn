# -*- coding: utf-8 -*-
"""
gen_wps_shots.py —— 生成《WPS 文字入门实操 4 课时》配套界面示意图（SVG）
运行：python tools/gen_scenes.py
输出：assets/wps-img/*.svg
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wpsdraw import *   # noqa

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "wps-img")
os.makedirs(OUT, exist_ok=True)

W, H = 1200, 720
RH = 200          # 功能区高度
WPS_TABS = ["文件", "首页", "开始", "插入", "页面布局", "引用", "审阅", "视图", "会员"]

TAB_GROUPS = {
    "开始": [
        ("剪贴板", [("粘", "粘贴"), ("剪", "剪切"), ("复", "复制"), ("刷", "格式刷")]),
        ("字体", [("黑", "字体"), ("小四", "字号"), ("B", "加粗"), ("I", "倾斜"),
                  ("U", "下划线"), ("A", "字符底纹"), ("框", "字符边框"), ("间", "字符间距"),
                  ("X²", "上标"), ("X₂", "下标")]),
        ("段落", [("符", "项目符号"), ("号", "编号"), ("⇤", "减少缩进"), ("⇥", "增大缩进"),
                  ("行", "行距"), ("左", "左对齐"), ("中", "居中"), ("右", "右对齐"),
                  ("J", "两端对齐"), ("¶", "显示/隐藏")]),
        ("样式", [("H1", "标题1"), ("H2", "标题2"), ("正", "正文")]),
        ("编辑", [("查", "查找"), ("换", "替换"), ("选", "选择")]),
    ],
    "插入": [
        ("页面", [("页", "页码"), ("眉", "页眉页脚"), ("分", "分隔符")]),
        ("图表", [("表", "表格"), ("图", "图片"), ("形", "形状"), ("图", "图表")]),
        ("符号", [("符", "符号"), ("式", "公式"), ("文", "文本框")]),
        ("引用", [("目", "目录"), ("注", "题注"), ("脚", "脚注"), ("链", "超链接")]),
    ],
    "页面布局": [
        ("页面", [("纸", "纸张大小"), ("向", "纸张方向"), ("边", "页边距"), ("栏", "分栏"),
                  ("符", "分隔符"), ("号", "行号")]),
        ("背景", [("水", "水印"), ("框", "页面边框"), ("色", "页面颜色")]),
        ("样式", [("文", "文字方向"), ("纸", "稿纸设置")]),
    ],
    "引用": [
        ("目录", [("目", "目录"), ("题", "题注")]),
        ("注释", [("脚", "脚注"), ("尾", "尾注"), ("交", "交叉引用")]),
        ("索引", [("索", "索引"), ("书", "书签")]),
    ],
    "审阅": [
        ("校对", [("拼", "拼写检查"), ("字", "字数统计"), ("译", "翻译")]),
        ("修订", [("批", "新建批注"), ("订", "修订"), ("比", "比较")]),
        ("保护", [("保", "保护文档"), ("限", "限制编辑")]),
    ],
}


# ------------------------------------------------------------------
# 通用场景
# ------------------------------------------------------------------
def doc_thumb(x, y, w, h, spec):
    """编辑区中的文档缩略页"""
    o = [R(x, y, w, h, fill="#FFFFFF", stroke="#D7DBE0", sw=1, rx=2,
           extra=' filter="url(#sh)"')]
    mx = x + 18
    cy = y + 24
    o.append(L(x + 10, y + 14, x + 10, y + h - 14, stroke="#E3B7B0", sw=1, dash="3 2"))
    if spec.get("title"):
        o.append(T(x + w / 2, cy, spec["title"], size=9.5, weight=700, anchor="middle"))
        cy += 18
    for i, ln in enumerate(spec.get("lines", [])):
        if isinstance(ln, dict) and ln.get("t"):
            o.append(T(mx, cy, ln["t"], size=8.5, fill="#5A6169"))
            cy += 13
            continue
        wdt = ln.get("w", w - 60)
        col = ln.get("c", "#C8CDD3")
        o.append(R(mx, cy - 6, wdt, 6, fill=col, stroke=None, rx=3))
        if spec.get("marks", True):
            o.append(T(mx + wdt + 4, cy, "¶", size=8, fill="#B9BEC4"))
        cy += 13
    if spec.get("sel") is not None:
        i = spec["sel"]
        sel_y = y + 24 + 18 * (1 if spec.get("title") else 0) + 13 * i
        o.append(R(x + 14, sel_y - 9, w - 42, 12, fill="#CFE0F7", stroke="#7BA7DE", sw=0.8, rx=2))
    if spec.get("cursor"):
        o.append(L(x + 20 + spec["cursor"], y + 18, x + 20 + spec["cursor"], y + 34,
                   stroke="#1F2329", sw=1.2))
    return "".join(o)


def ui(name, tab, groups, marks, doc=None, note=None, w=W, h=H,
       status="第 1 页    字数：0"):
    """WPS 主界面场景。marks: [(组号, 标签, 序号)]"""
    o = [app_shell(w, h, doc_title="练习 - WPS Office", tab=tab, tabs=WPS_TABS)]
    o.append(ribbon_bg(w, 66, RH))
    x = 14
    gpos = []
    for gi, (gname, items) in enumerate(groups):
        svg, pos, gw = ribbon_group_buttons(x + 8, 76, gname, items, cols=5)
        o.append(svg)
        gpos.append(pos)
        x += gw + 6
    for gi, label, n in marks:
        if gi < len(gpos) and label in gpos[gi]:
            bx, by, bw, bh = gpos[gi][label]
            o.append(mark(bx - 4, by - 4, bw + 8, bh + 8, n))
    o.append(L(0, 66 + RH, w, 66 + RH, stroke=C_DIVIDER))
    ey = 66 + RH
    eh = h - ey - 26
    o.append(R(0, ey, w, eh, fill=C_BG, stroke=None, rx=0))
    pw, ph = 320, int(320 * 297 / 210.0)
    px = 60
    py = ey + 16
    spec = dict(doc or {})
    lines = list(spec.get("lines", []))
    for i in range(len(lines), 9):
        lines.append({"w": 250 - (i % 4) * 42, "c": "#C8CDD3"})
    spec["lines"] = lines
    o.append(doc_thumb(px, py, pw, ph, spec))
    o.append(T(px + pw / 2, py + ph + 20, "文档编辑区（插入点所在页面）", size=11.5, fill="#9AA0A6", anchor="middle"))
    if note:
        yy = ey + 46
        for line in note:
            o.append(T(px + pw + 70, yy, line, size=13, fill=C_TEXT2))
            yy += 24
    o.append(R(0, h - 26, w, 26, fill="#FAFAFA", stroke=None, rx=0))
    o.append(L(0, h - 26, w, h - 26, stroke=C_DIVIDER))
    o.append(T(14, h - 9, status, size=11, fill=C_MUTED))
    o.append(T(w - 16, h - 9, "视图  100%", size=11, fill=C_MUTED, anchor="end"))
    o.append(tag_svg(w, h))
    write(name, svg_doc(w, h, "".join(o), bg="#FFFFFF"))


def tag_svg(w, h):
    txt = "界面示意图 · WPS 文字 12.x"
    ww = tw(txt, 11) + 16
    return (R(w - ww, h - 40, ww, 20, fill="#FFFFFF", stroke=C_BORDER, sw=1, rx=0, opacity=0.95) +
            T(w - ww / 2, h - 25, txt, size=11, fill=C_MUTED, anchor="middle"))


def write(name, svg):
    path = os.path.join(OUT, name + ".svg")
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg)
    return path


def file_backstage(items, marked, w=W, h=H, y=66):
    """文件 backstage：左侧菜单 + 右侧「新建 / 最近使用」主区"""
    o = [R(0, y, 268, h - y - 26, fill="#FFFFFF", stroke=None, rx=0),
         R(268, y, w - 268, h - y - 26, fill="#F7F8FA", stroke=None, rx=0),
         L(268, y, 268, h - 26, stroke=C_DIVIDER)]
    yy = y + 34
    for it in items:
        if it in marked:
            o.append(R(12, yy - 20, 244, 30, fill="#FDEEEA", stroke=None, rx=6))
            o.append(CIRC(232, yy - 5, 10, fill=C_HILITE))
            o.append(T(232, yy - 1, str(marked[it]), size=11, fill="#FFFFFF", weight=800, anchor="middle"))
        o.append(T(26, yy, it, size=13, fill=C_TEXT if it in marked else C_TEXT2,
                   weight=700 if it in marked else 500))
        yy += 34
    # 主区：新建
    o.append(T(320, y + 44, "新建", size=17, weight=800, fill=C_TEXT))
    cards = [("空", "空白文档"), ("表", "表格"), ("演", "演示文稿"), ("PDF", "PDF")]
    for i, (g, t) in enumerate(cards):
        cx = 320 + i * 150
        o.append(R(cx, y + 66, 130, 104, fill="#FFFFFF", stroke=C_BORDER, sw=1, rx=8))
        o.append(R(cx + 45, y + 84, 40, 40, fill="#EEF3FA", stroke=None, rx=8))
        o.append(T(cx + 65, y + 110, g, size=15, fill="#4A6FA5", weight=700, anchor="middle"))
        o.append(T(cx + 65, y + 150, t, size=12, fill=C_TEXT2, anchor="middle"))
    o.append(mark(318, y + 62, 136, 112, 1))
    # 主区：最近使用
    o.append(T(320, y + 226, "最近使用", size=15, weight=800, fill=C_TEXT))
    recents = ["实训报告.docx", "报名通知.docx", "成绩表.xlsx"]
    for i, f in enumerate(recents):
        o.append(R(320, y + 244 + i * 40, 470, 34, fill="#FFFFFF", stroke=C_BORDER, sw=1, rx=6))
        o.append(T(336, y + 266 + i * 40, "▤", size=13, fill="#7A8089"))
        o.append(T(360, y + 266 + i * 40, f, size=12.5, fill=C_TEXT2))
    o.append(T(320, y + 386, "提示：考试中只需「新建 → 空白文档」与「另存为」，", size=12.5, fill=C_MUTED))
    o.append(T(320, y + 410, "「输出为PDF」「文档加密」在交卷前按要求操作。", size=12.5, fill=C_MUTED))
    return "".join(o)


def ui_file(name, items, marked, note=None):
    """文件 backstage 场景"""
    o = [app_shell(W, H, doc_title="WPS Office", tab="文件", tabs=WPS_TABS)]
    o.append(file_backstage(items, marked))
    o.append(R(0, H - 26, W, 26, fill="#FAFAFA", stroke=None, rx=0))
    o.append(L(0, H - 26, W, H - 26, stroke=C_DIVIDER))
    o.append(T(14, H - 9, "返回", size=11, fill=C_MUTED))
    o.append(tag_svg(W, H))
    write(name, svg_doc(W, H, "".join(o), bg="#FFFFFF"))


def dialog_scene(name, title, tabs, rows, marks=None, foot=None, active_tab=0,
                 note=None, dlgw=720, extra_top=0):
    """对话框场景：画布按内容自动裁剪"""
    marks = marks or {}
    dlgx, dlgy = 60, 40
    d, pos, dh = dialog(dlgx, dlgy, dlgw, title, tabs=tabs, rows=rows, foot=foot,
                        active_tab=active_tab)
    o = [d]
    for idx, n in marks.items():
        if str(idx) in pos:
            bx, by, bw, bh = pos[str(idx)]
            o.append(mark(bx - 4, by - 4, bw + 8, bh + 8, n, pos="out"))
    note_h = 0
    if note:
        note_h = len(note) * 26 + 14
        yy = dlgy + dh + 30
        for line in note:
            o.append(T(dlgx + 4, yy, line, size=13, fill=C_TEXT2))
            yy += 26
    wc = dlgw + 170
    hc = dlgy + dh + note_h + 24
    o.append(tag_svg(wc, hc))
    write(name, svg_doc(wc, hc, "".join(o), bg="#F3F5F8"))


def page_scene(name, page, caption=None, bg="#EEF1F5", crop=True):
    """文档效果页（可按内容裁剪高度）"""
    h = page.h
    if crop and not (page.watermark or page.page_border or page.header or page.footer):
        h = min(page.h, max(page.y + 70, 300))
    w = page.w + 80
    body = [R(0, 0, w, h + 80, fill=bg, stroke=None, rx=0),
            '<g transform="translate(40,40)">%s</g>' % page.render(h=h)]
    if caption:
        body.append(T(w / 2, h + 58, caption, size=12.5, fill="#6B7A90", anchor="middle"))
    body.append(tag_svg(w, h + 80))
    write(name, svg_doc(w, h + 80, "".join(body), bg=bg))


def two_pages(name, p1, p2, cap1, cap2, gap=70):
    w = p1.w + p2.w + 80 * 2 + gap
    h = max(p1.h, p2.h) + 80
    o = [R(0, 0, w, h, fill="#EEF1F5", stroke=None, rx=0)]
    o.append('<g transform="translate(40,40)">%s</g>' % p1.render())
    o.append('<g transform="translate(%d,40)">%s</g>' % (40 + p1.w + gap, p2.render()))
    o.append(T(40 + p1.w / 2, h - 22, cap1, size=12.5, fill="#6B7A90", anchor="middle"))
    o.append(T(40 + p1.w + gap + p2.w / 2, h - 22, cap2, size=12.5, fill="#6B7A90", anchor="middle"))
    o.append(tag_svg(w, h))
    write(name, svg_doc(w, h, "".join(o), bg="#EEF1F5"))
