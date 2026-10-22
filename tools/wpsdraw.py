# -*- coding: utf-8 -*-
"""
wpsdraw.py —— WPS 文字 12.x 界面高保真示意图绘制库（纯标准库，输出 SVG）

用途：为《WPS 文字入门实操 4 课时》网页生成"关键操作步骤 + 最终完成效果"的界面示意图。
说明：图形依据 WPS Office 文字处理界面布局绘制，用于教学示意，非软件截图。
"""
import math

FONT = "Microsoft YaHei, PingFang SC, Noto Sans SC, Source Han Sans SC, sans-serif"
MONO = "Consolas, Menlo, DejaVu Sans Mono, monospace"

# —— WPS 主题色（浅色系）——
C_BG        = "#EEF1F5"   # 编辑区底色
C_TITLEBAR  = "#FFFFFF"
C_TABBAR    = "#F7F8FA"
C_ACTIVE    = "#E8503A"   # 站点主色 / WPS 红橙
C_ACCENT2   = "#F2A33C"
C_BORDER    = "#DFE3E8"
C_DIVIDER   = "#E9ECEF"
C_TEXT      = "#1F2329"
C_TEXT2     = "#5A6169"
C_MUTED     = "#9AA0A6"
C_BTN       = "#FFFFFF"
C_INPUT     = "#FFFFFF"
C_INPUT_BD  = "#C9CDD4"
C_FIELD     = "#F7F8FA"
C_HILITE    = "#E8503A"   # 高亮框
C_GREEN     = "#16A34A"
C_BLUE      = "#2563EB"
C_PAPER     = "#FFFFFF"


def esc(t):
    return (str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;"))


def tw(s, size, mono=False):
    """估算文本宽度（中文按 1em，西文按 0.55em）"""
    w = 0.0
    for ch in str(s):
        if mono:
            w += 0.6
        elif ord(ch) > 0x2E80:
            w += 1.0
        else:
            w += 0.55
    return w * size


def T(x, y, s, size=13, fill=C_TEXT, weight=400, anchor="start", mono=False,
      opacity=None, ls=None, family=None, style=None, color=None):
    if color is not None:
        fill = color
    o = opacity if opacity is not None else 1
    f = family or (MONO if mono else FONT)
    extra = ' letter-spacing="%s"' % ls if ls else ""
    if style:
        extra += ' font-style="%s"' % style
    return ('<text x="%.1f" y="%.1f" font-family="%s" font-size="%.1f" font-weight="%s" '
            'fill="%s" text-anchor="%s" opacity="%s"%s>%s</text>'
            % (x, y, f, size, weight, fill, anchor, o, extra, esc(s)))


def R(x, y, w, h, fill=C_BTN, stroke=C_BORDER, sw=1, rx=4, opacity=None, extra=""):
    o = ' opacity="%s"' % opacity if opacity is not None else ""
    st = ' stroke="%s" stroke-width="%s"' % (stroke, sw) if stroke else ' stroke="none"'
    return ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%s" fill="%s"%s%s%s/>'
            % (x, y, w, h, rx, fill, st, o, extra))


def L(x1, y1, x2, y2, stroke=C_DIVIDER, sw=1, dash=None, cap=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ""
    c = ' stroke-linecap="%s"' % cap if cap else ""
    return ('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="%s"%s%s/>'
            % (x1, y1, x2, y2, stroke, sw, d, c))


def CIRC(x, y, r, fill=C_HILITE, stroke="#FFFFFF", sw=2, opacity=None):
    o = ' opacity="%s"' % opacity if opacity is not None else ""
    st = ' stroke="%s" stroke-width="%s"' % (stroke, sw) if stroke else ' stroke="none"'
    return '<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s"%s%s/>' % (x, y, r, fill, st, o)


def PATH(d, stroke=C_HILITE, sw=2, fill="none", extra=""):
    return '<path d="%s" fill="%s" stroke="%s" stroke-width="%s" %s/>' % (d, fill, stroke, sw, extra)


def mark(x, y, w, h, n, label=None, color=C_HILITE, pos="tl"):
    """高亮框 + 序号圆标（pos: tl 左上 / tr 右侧 / out 框外右侧）"""
    out = [R(x, y, w, h, fill="none", stroke=color, sw=2.2, rx=6,
             extra=' stroke-dasharray="6 4"')]
    if pos == "tr":
        bx, by = x + w - 4, y + 2
    elif pos == "out":
        bx, by = x + w + 6, y + 2
    else:
        bx, by = x + 2, y + 2
    out.append(CIRC(bx, by, 11, fill=color))
    out.append(T(bx, by + 4.5, str(n), size=12, fill="#FFFFFF", weight=800, anchor="middle"))
    if label:
        lw = tw(label, 11) + 16
        out.append(R(x + w - lw, y + h - 22, lw, 18, fill=color, stroke=None, rx=9))
        out.append(T(x + w - lw / 2, y + h - 9, label, size=11, fill="#FFFFFF",
                     weight=700, anchor="middle"))
    return "".join(out)


def arrow(x1, y1, x2, y2, color=C_HILITE, sw=2.2):
    """带箭头的指示线"""
    ang = math.atan2(y2 - y1, x2 - x1)
    head = 9
    hx1 = x2 - head * math.cos(ang - math.radians(22))
    hy1 = y2 - head * math.sin(ang - math.radians(22))
    hx2 = x2 - head * math.cos(ang + math.radians(22))
    hy2 = y2 - head * math.sin(ang + math.radians(22))
    return (L(x1, y1, x2, y2, stroke=color, sw=sw, cap="round") +
            PATH("M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" % (x2, y2, hx1, hy1, hx2, hy2),
                 stroke=color, sw=1, fill=color))


def badge(x, y, text, fill="#F0F1F3", color=C_TEXT2, size=11, pad=8, h=20, rx=10, weight=600):
    w = tw(text, size) + pad * 2
    out = [R(x, y, w, h, fill=fill, stroke=None, rx=rx)]
    out.append(T(x + w / 2, y + h / 2 + size * 0.36, text, size=size, fill=color,
                 weight=weight, anchor="middle"))
    return "".join(out), w


def svg_doc(w, h, body, bg="#FFFFFF"):
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">'
            '<defs><filter id="sh" x="-20%%" y="-20%%" width="140%%" height="140%%">'
            '<feDropShadow dx="0" dy="2" stdDeviation="4" flood-color="#1F2329" flood-opacity="0.13"/>'
            '</filter>'
            '<filter id="shs" x="-30%%" y="-30%%" width="160%%" height="160%%">'
            '<feDropShadow dx="0" dy="6" stdDeviation="10" flood-color="#1F2329" flood-opacity="0.18"/>'
            '</filter></defs>'
            '<rect width="%d" height="%d" fill="%s"/>%s</svg>'
            % (w, h, w, h, w, h, bg, body))


def tag(s):
    """右下角'示意图'标识"""
    w = tw("界面示意图", 11) + 16
    return (R(0, 0, w, 20, fill="#FFFFFF", stroke=C_BORDER, sw=1, rx=0, opacity=0.92) +
            T(8, 14, "界面示意图", size=11, fill=C_MUTED))


# ============================================================
# 应用窗口骨架
# ============================================================
def app_shell(w, h, doc_title, tab, tabs=None, active=None):
    """返回 (body字符串, 内容区左上角坐标) —— 标题栏 + 选项卡栏 + 功能区背景 + 状态栏"""
    tabs = tabs or ["文件", "首页", "开始", "插入", "页面布局", "引用", "审阅", "视图", "会员"]
    active = active or tab
    o = []
    o.append(R(0, 0, w, h, fill="#FFFFFF", stroke=C_BORDER, sw=1, rx=0))
    # 标题栏
    o.append(R(0, 0, w, 34, fill=C_TITLEBAR, stroke=None, rx=0))
    o.append(R(14, 9, 20, 16, fill=C_ACTIVE, stroke=None, rx=4))
    o.append(T(24, 21, "W", size=11, fill="#FFFFFF", weight=800, anchor="middle"))
    o.append(T(42, 21, doc_title, size=12, fill=C_TEXT2))
    for i, g in enumerate(["—", "□", "✕"]):
        o.append(T(w - 26 - i * 26, 21, g, size=12, fill=C_MUTED, anchor="middle"))
    o.append(L(0, 34, w, 34, stroke=C_DIVIDER))
    # 选项卡
    o.append(R(0, 34, w, 32, fill=C_TABBAR, stroke=None, rx=0))
    x = 14
    for t in tabs:
        tw_ = tw(t, 13) + 22
        if t == active:
            o.append(R(x, 34, tw_, 31, fill="#FFFFFF", stroke=None, rx=0))
            o.append(R(x, 63, tw_, 2.5, fill=C_ACTIVE, stroke=None, rx=0))
        o.append(T(x + tw_ / 2, 55, t, size=13,
                   fill=C_ACTIVE if t == active else C_TEXT2,
                   weight=700 if t == active else 500, anchor="middle"))
        x += tw_
    o.append(L(0, 66, w, 66, stroke=C_DIVIDER))
    return "".join(o)


def ribbon_bg(w, y, h, x0=0, x1=None):
    x1 = x1 or w
    return R(x0, y, x1 - x0, h, fill="#FFFFFF", stroke=None, rx=0)


def group_frame(x, y, w, h, name):
    """功能区分组：左右竖线 + 底部组名（组名位于所有按钮文字之下）"""
    o = [L(x, y + 8, x, y + h - 8, stroke=C_DIVIDER, sw=1),
         L(x + w, y + 8, x + w, y + h - 8, stroke=C_DIVIDER, sw=1),
         T(x + w / 2, y + h - 5, name, size=11, fill=C_MUTED, anchor="middle")]
    return "".join(o)


def ribbon_button(x, y, w, h, glyph, label=None, glyph_size=13, fill="#FFFFFF",
                  stroke="#D8DCE1", glyph_color=C_TEXT):
    o = [R(x, y, w, h, fill=fill, stroke=stroke, sw=1, rx=5)]
    o.append(T(x + w / 2, y + h / 2 + glyph_size * 0.36, glyph, size=glyph_size,
               fill=glyph_color, weight=600, anchor="middle"))
    if label:
        o.append(T(x + w / 2, y + h + 13, label, size=10.5, fill=C_TEXT2, anchor="middle"))
    return "".join(o)


def ribbon_group_buttons(x, y, name, items, cols=5, bw=32, bh=26, gap=7, rowgap=28):
    """
    items: [(glyph, label)]  返回 (svg, 按钮坐标字典 {label:(bx,by,bw,bh)}, 组总宽)
    """
    o = []
    pos = {}
    gx, gy = x, y
    for i, (glyph, label) in enumerate(items):
        col, row = i % cols, i // cols
        bx = gx + col * (bw + gap)
        by = gy + row * (bh + rowgap)
        o.append(ribbon_button(bx, by, bw, bh, glyph, None))
        if label:
            o.append(T(bx + bw / 2, by + bh + 13, label, size=9.5, fill=C_MUTED, anchor="middle"))
        pos[label or glyph] = (bx, by, bw, bh)
    rows = math.ceil(len(items) / cols)
    cols_used = min(cols, len(items))
    last_bottom = gy + (rows - 1) * (bh + rowgap) + bh
    name_y = last_bottom + 29
    frame_top = gy - 8
    frame_h = name_y + 5 - frame_top
    gw = cols_used * (bw + gap) - gap
    o.append(group_frame(gx - 9, frame_top, gw + 18, frame_h, name))
    return "".join(o), pos, gw + 18


def field_box(x, y, w, h, value, kind="text", size=12, align="left"):
    """表单控件"""
    o = []
    if kind == "sel":
        o.append(R(x, y, w, h, fill=C_INPUT, stroke=C_INPUT_BD, sw=1, rx=3))
        o.append(T(x + 8, y + h / 2 + size * 0.36, value, size=size, fill=C_TEXT))
        o.append(PATH("M %.1f %.1f L %.1f %.1f L %.1f %.1f Z"
                       % (x + w - 16, y + h / 2 - 2, x + w - 11, y + h / 2 - 2, x + w - 13.5, y + h / 2 + 2.5),
                       stroke="#7A8089", sw=1.2, fill="#7A8089"))
    elif kind == "chk":
        o.append(R(x, y, 14, 14, fill="#FFFFFF", stroke=C_INPUT_BD, sw=1, rx=2))
        o.append(PATH("M %.1f %.1f L %.1f %.1f L %.1f %.1f Z"
                       % (x + 3, y + 7, x + 6, y + 10.5, x + 11, y + 3.5),
                       stroke=C_BLUE, sw=1.8, fill=C_BLUE))
        o.append(T(x + 20, y + h / 2 + size * 0.36, value, size=size, fill=C_TEXT))
    elif kind == "radio":
        o.append(CIRC(x + 7, y + h / 2, 6.5, fill="#FFFFFF", stroke=C_INPUT_BD, sw=1.2))
        o.append(CIRC(x + 7, y + h / 2, 3.2, fill=C_BLUE, stroke=None))
        o.append(T(x + 20, y + h / 2 + size * 0.36, value, size=size, fill=C_TEXT))
    elif kind == "radiooff":
        o.append(CIRC(x + 7, y + h / 2, 6.5, fill="#FFFFFF", stroke=C_INPUT_BD, sw=1.2))
        o.append(T(x + 20, y + h / 2 + size * 0.36, value, size=size, fill=C_TEXT))
    else:
        o.append(R(x, y, w, h, fill=C_INPUT, stroke=C_INPUT_BD, sw=1, rx=3))
        tx = x + 8
        if align == "right":
            tx = x + w - 8
        o.append(T(tx, y + h / 2 + size * 0.36, value, size=size, fill=C_TEXT, anchor=align))
    return "".join(o)


def dialog(x, y, w, title, tabs=None, rows=None, buttons=("确定", "取消"),
           foot=None, active_tab=0):
    """
    rows: [(label, value, kind, note)]  kind: text/sel/chk/radio/radiooff/sep
    返回 (svg, 控件坐标 dict)
    """
    o = []
    h = 40 + (30 if tabs else 0) + 38 * len(rows or []) + 56
    o.append(R(x + 3, y + 5, w, h, fill="#1F2329", stroke=None, rx=9, opacity=0.10))
    o.append(R(x, y, w, h, fill="#FFFFFF", stroke="#C9CDD4", sw=1, rx=9))
    o.append(R(x, y, w, 32, fill="#F5F6F8", stroke=None, rx=9))
    o.append(R(x, y + 20, w, 12, fill="#F5F6F8", stroke=None, rx=0))
    o.append(T(x + 16, y + 21, title, size=13, fill=C_TEXT, weight=700))
    o.append(T(x + w - 18, y + 21, "✕", size=12, fill=C_MUTED, anchor="middle"))
    o.append(L(x, y + 32, x + w, y + 32, stroke=C_DIVIDER))
    cy = y + 32
    if tabs:
        tx = x + 14
        for i, t in enumerate(tabs):
            tw_ = tw(t, 12) + 24
            if i == active_tab:
                o.append(R(tx, cy + 2, tw_, 26, fill="#FFFFFF", stroke=C_BORDER, sw=1, rx=4))
                o.append(T(tx + tw_ / 2, cy + 19, t, size=12, fill=C_TEXT, weight=700, anchor="middle"))
            else:
                o.append(T(tx + tw_ / 2, cy + 19, t, size=12, fill=C_TEXT2, anchor="middle"))
            tx += tw_ + 4
        o.append(L(x, cy + 30, x + w, cy + 30, stroke=C_DIVIDER))
        cy += 32
    pos = {}
    for i, r in enumerate(rows or []):
        label, value, kind = r[0], r[1], r[2]
        note = r[3] if len(r) > 3 else None
        ry = cy + 12 + i * 38
        o.append(T(x + 20, ry + 17, label, size=12.5, fill=C_TEXT2))
        if kind in ("text", "sel"):
            o.append(field_box(x + 160, ry, 230, 26, value, kind))
            pos[str(i)] = (x + 160, ry, 230, 26)
        elif kind == "chk":
            o.append(field_box(x + 160, ry, 20, 26, value, "chk"))
            pos[str(i)] = (x + 160, ry, 180, 26)
        elif kind in ("radio", "radiooff"):
            o.append(field_box(x + 160, ry, 20, 26, value, kind))
            pos[str(i)] = (x + 160, ry, 180, 26)
        else:
            o.append(R(x + 160, ry, 230, 26, fill=C_FIELD, stroke=C_BORDER, sw=1, rx=3))
            o.append(T(x + 170, ry + 17, value, size=12, fill=C_TEXT2))
            pos[str(i)] = (x + 160, ry, 230, 26)
        if note:
            o.append(T(x + 404, ry + 17, note, size=11, fill=C_HILITE, weight=600))
    cy += 12 + 38 * len(rows or [])
    o.append(L(x, cy, x + w, cy, stroke=C_DIVIDER))
    by = cy + 12
    bx = x + w - 20
    for b in reversed(buttons):
        bw = tw(b, 12.5) + 32
        is_main = (b == buttons[0])
        o.append(R(bx - bw, by, bw, 30, fill=C_ACTIVE if is_main else "#FFFFFF",
                   stroke=None if is_main else C_INPUT_BD, sw=1, rx=4))
        o.append(T(bx - bw / 2, by + 20, b, size=12.5, fill="#FFFFFF" if is_main else C_TEXT,
                   weight=600, anchor="middle"))
        bx -= bw + 10
    if foot:
        o.append(T(x + 20, by + 20, foot, size=11, fill=C_MUTED))
    return "".join(o), pos, h


def menu_panel(x, y, w, items, marked=None, title=None, rowh=28, icon_col=True):
    """下拉菜单 / 样式面板"""
    marked = marked or {}
    o = []
    h = (26 if title else 0) + rowh * len(items) + 10
    o.append(R(x + 2, y + 3, w, h, fill="#1F2329", stroke=None, rx=6, opacity=0.10))
    o.append(R(x, y, w, h, fill="#FFFFFF", stroke="#C9CDD4", sw=1, rx=6))
    if title:
        o.append(T(x + 12, y + 18, title, size=11, fill=C_MUTED))
        o.append(L(x, y + 26, x + w, y + 26, stroke=C_DIVIDER))
    for i, it in enumerate(items):
        ry = y + (26 if title else 0) + 5 + i * rowh
        if it in marked:
            o.append(R(x + 3, ry, w - 6, rowh - 2, fill="#EAF2FD", stroke=None, rx=4))
        glyph, label = (it if isinstance(it, tuple) else ("", it))
        tx = x + 14
        if icon_col and glyph:
            o.append(T(tx, ry + 19, glyph, size=13, fill=C_TEXT, weight=600))
            tx += 26
        o.append(T(tx, ry + 19, label, size=12.5, fill=C_TEXT))
        if it in marked:
            o.append(mark(x + w - 34, ry + 2, 26, rowh - 6, marked[it], color=C_HILITE))
    return "".join(o), h


# ============================================================
# A4 纸张（文档效果）
# ============================================================
def wrap_text(text, size, maxw):
    """按像素宽度折行"""
    lines, cur = [], ""
    for ch in str(text):
        if tw(cur + ch, size) > maxw and cur:
            lines.append(cur)
            cur = ch
        else:
            cur += ch
    if cur:
        lines.append(cur)
    return lines


class Page:
    """A4 纸面渲染器：1cm = 36.2px（760px 宽对应 21cm）"""

    CM = 36.2

    def __init__(self, w=760, margin=90, top=64, bottom=70):
        self.w = w
        self.h = 1024
        self.margin = margin
        self.y = top
        self.body = []
        self.header = None
        self.footer = None
        self.watermark = None
        self.page_border = None
        self.bg = None

    # ---- 基础 ----
    def _cx(self):
        return self.w / 2

    def add(self, s):
        self.body.append(s)
        return self

    def line(self, text, size=15.3, color="#1A1A1A", weight=400, align="left",
             indent=0, space=0, lh=1.75, family=FONT, spacing=None, marker=None, ls=None):
        x = self.margin + indent
        if align == "center":
            self.add(T(self._cx(), self.y, text, size=size, color=color, weight=weight,
                       anchor="middle", family=family, ls=ls or spacing))
        elif align == "right":
            self.add(T(self.w - self.margin, self.y, text, size=size, color=color,
                       weight=weight, anchor="end", family=family, ls=ls or spacing))
        else:
            self.add(T(x, self.y, text, size=size, color=color, weight=weight,
                       family=family, ls=ls or spacing))
        if marker:
            self.add(marker)
        self.y += size * lh + space
        return self

    def raw(self, s, dy=0):
        self.body.append(s)
        return self

    def spacer(self, h):
        self.y += h
        return self

    # ---- 构件 ----
    def title(self, text, size=28, color="#000000", align="center", space=14, weight=700, spacing=1.0):
        return self.line(text, size=size, color=color, align=align, weight=weight,
                         space=space, lh=1.35, ls=spacing)

    def h2(self, text, size=18, space=10, color="#000000"):
        return self.line(text, size=size, color=color, weight=700, space=space, lh=1.5)

    def p(self, text, size=15.3, indent_chars=2, align="left", lh=1.9, space=6, color="#1A1A1A"):
        ind = size * indent_chars
        return self.line(text, size=size, color=color, align=align, indent=ind, lh=lh, space=space)

    def numbered(self, idx, text, size=15.3, lh=1.8, space=4):
        x = self.margin + 4
        self.add(T(x, self.y, "%d." % idx, size=size, color="#1A1A1A"))
        self.add(T(x + 22, self.y, text, size=size, color="#1A1A1A"))
        self.y += size * lh + space
        return self

    def bullet(self, text, size=15.3, lh=1.8, space=4, color="#1A1A1A"):
        x = self.margin + 6
        self.add(CIRC(x + 4, self.y - 5, 3.4, fill="#1A1A1A", stroke=None))
        self.add(T(x + 20, self.y, text, size=size, color=color))
        self.y += size * lh + space
        return self

    def boxed(self, blocks_fn, pad=12, bg="#FFFDE0", stroke="#E3C765", sw=1.4, radius=4):
        """带边框底纹的段落块（先量高，再绘制）"""
        y0 = self.y
        blocks_fn()
        y1 = self.y
        self.body.insert(0, R(self.margin - 8, y0 - 22, self.w - 2 * self.margin + 16,
                              y1 - y0 + 26, fill=bg, stroke=stroke, sw=sw, rx=radius))
        return self

    def table(self, header, rows, colw, size=13.5, head_bg="#F0F0F0", hrow=30, brow=26,
              align=None, head_align="center", cell_align="left", border="#7A7A7A"):
        total = sum(colw)
        x0 = self.margin
        align = align or ["left"] * len(header)
        # 表头
        self.add(R(x0, self.y, total, hrow, fill=head_bg, stroke=border, sw=1))
        cx = x0
        for i, htxt in enumerate(header):
            self.add(T(cx + colw[i] / 2, self.y + hrow / 2 + size * 0.36, htxt, size=size,
                       weight=700, anchor="middle"))
            cx += colw[i]
        self.y += hrow
        for r in rows:
            self.add(R(x0, self.y, total, brow, fill="#FFFFFF", stroke=border, sw=1))
            cx = x0
            for i, cell in enumerate(r):
                if align[i] == "center":
                    self.add(T(cx + colw[i] / 2, self.y + brow / 2 + size * 0.36, cell,
                               size=size, anchor="middle"))
                else:
                    self.add(T(cx + 8, self.y + brow / 2 + size * 0.36, cell, size=size))
                cx += colw[i]
            self.y += brow
        self.y += 10
        return self

    def img_block(self, w, h, caption=None, label="图片（四周型环绕）"):
        """图片占位块"""
        x = self.margin + 40
        self.add(R(x, self.y, w, h, fill="#EAF1F8", stroke="#9DB8D4", sw=1.2, rx=3))
        self.add(PATH("M %.1f %.1f L %.1f %.1f L %.1f %.1f Z"
                       % (x + 10, self.y + h - 12, x + w * 0.42, self.y + h * 0.34,
                          x + w - 10, self.y + h - 12), stroke="#9DB8D4", sw=1, fill="#D6E4F2"))
        self.add(CIRC(x + w * 0.24, self.y + h * 0.26, 11, fill="#F2C14E", stroke=None))
        self.add(T(x + w / 2, self.y + h / 2 + 5, label, size=13, fill="#5C7899", anchor="middle"))
        self.y += h
        if caption:
            self.y += 8
            self.add(T(self._cx(), self.y, caption, size=13, fill="#1A1A1A", anchor="middle"))
            self.y += 20
        else:
            self.y += 10
        return self

    def toc(self, entries, size=14, gap=26):
        for e in entries:
            self.add(T(self.margin, self.y, e[0], size=size, color="#1A1A1A"))
            self.add(T(self.w - self.margin, self.y, e[1], size=size, color="#1A1A1A", anchor="end"))
            # 引导点
            lead = self.w - 2 * self.margin - tw(e[0], size) - tw(e[1], size) - 12
            if lead > 20:
                for i in range(int(lead // 8)):
                    self.add(CIRC(self.margin + tw(e[0], size) + 6 + i * 8,
                                  self.y - 4, 1.1, fill="#8A8A8A", stroke=None))
            self.y += gap
        return self

    def set_header(self, text, size=12, align="center", rule=True, color="#1A1A1A"):
        self.header = (text, size, align, rule, color)
        self.y = max(self.y, 92)
        return self

    def set_footer(self, text, size=12, align="center"):
        self.footer = (text, size, align)
        return self

    def set_watermark(self, text, size=46, color="#C8CDD3", opacity=0.55, rot=-28):
        self.watermark = (text, size, color, opacity, rot)
        return self

    def set_page_border(self, sw=1.5, double=True, color="#7A7A7A"):
        self.page_border = (sw, double, color)
        return self

    def set_bg(self, color):
        self.bg = color
        return self

    def render(self, shadow=True, h=None):
        H_ = h or self.h
        o = []
        o.append(R(0, 0, self.w, H_, fill=self.bg or C_PAPER, stroke=None, rx=0,
                   extra=' filter="url(#sh)"' if shadow else ""))
        if self.page_border:
            sw, dbl, color = self.page_border
            o.append(R(34, 34, self.w - 68, H_ - 68, fill="none", stroke=color,
                       sw=sw, rx=0, extra=' stroke-dasharray="%s"' % ("10 4" if dbl else "none")))
        if self.watermark:
            text, size, color, op, rot = self.watermark
            o.append('<g transform="rotate(%d %.1f %.1f)" opacity="%s">%s</g>'
                     % (rot, self.w / 2, H_ / 2, op,
                        T(self.w / 2, H_ / 2, text, size=size, fill=color, weight=700,
                          anchor="middle")))
        if self.header:
            text, size, align, rule, color = self.header
            hx = self.margin if align == "left" else (self.w - self.margin if align == "right" else self.w / 2)
            o.append(T(hx, 46, text, size=size, fill=color, anchor=align))
            if rule:
                o.append(L(self.margin, 56, self.w - self.margin, 56, stroke="#1A1A1A", sw=1))
        if self.footer:
            text, size, align = self.footer
            fx = self.margin if align == "left" else (self.w - self.margin if align == "right" else self.w / 2)
            o.append(T(fx, H_ - 40, text, size=size, fill="#1A1A1A", anchor=align))
        o.append("".join(self.body))
        return "".join(o)


def doc_scene(page, caption=None, bg="#EEF1F5", pad=0, w=None):
    """把一张 A4 页面放进浅灰底"""
    w = w or page.w + 80
    h = page.h + 80
    o = [R(0, 0, w, h, fill=bg, stroke=None, rx=0)]
    o.append('<g transform="translate(40,40)">%s</g>' % page.render())
    if caption:
        o.append(T(w / 2, h - 18, caption, size=12, fill="#6B7A90", anchor="middle"))
    return "".join(o)
