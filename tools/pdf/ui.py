# -*- coding: utf-8 -*-
"""WPS 界面矢量绘图库：按 WPS Office 2024（12.x，浅色主题）的真实布局绘制示意图。

设计约定
- 画布宽 1000，对应 A4 正文宽（约 492pt），缩放 0.492：13px 文字 ≈ 6.4pt，可读。
- 功能区采用「显式宽度 + 显式行」模型，不做自动排版，保证不错位。
- 图标一律用几何线条绘制（单色），不使用 emoji，避免与真实界面观感冲突。
- 标注 = 橙色实心圆 + 白色数字，默认浮在目标外侧并用短引线指向目标，不压文字。
"""
import html as _h

K = {
    "winbg": "#f1f3f6",
    "chrome": "#ffffff",
    "tabbar": "#fafbfc",
    "ribbon": "#fcfdfe",
    "line": "#e4e7ed",
    "line2": "#d2d8e1",
    "txt": "#232a33",
    "txt2": "#4b5562",
    "txt3": "#8b939f",
    "blue": "#2b6cff",
    "blue_d": "#1a4fd0",
    "blue2": "#e9f0ff",
    "fieldb": "#d9dee7",
    "doc": "#e8eaee",
    "page": "#ffffff",
    "mark": "#e8710a",
    "markbg": "#fff5e9",
    "red": "#cf3f3f",
    "green": "#137a52",
    "grid": "#dbe0e8",
    "head": "#eef1f6",
    "ico": "#3f5f8c",
}


def esc(s):
    return _h.escape(str(s), quote=False)


class Fig:
    def __init__(self, w=1000, h=480):
        self.w, self.h = w, h
        self.b, self._marks, self._ids = [], [], {}

    # ---------- 基础图元 ----------
    def raw(self, s):
        self.b.append(s)
        return self

    def rect(self, x, y, w, h, fill="none", stroke="none", sw=1, r=0, op=None, dash=None):
        o = ' opacity="%s"' % op if op else ""
        d = ' stroke-dasharray="%s"' % dash if dash else ""
        self.b.append(
            '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%.1f" fill="%s" stroke="%s" '
            'stroke-width="%s"%s%s/>' % (x, y, w, h, r, fill, stroke, sw, o, d))
        return self

    def line(self, x1, y1, x2, y2, stroke=None, sw=1, dash=None, cap="butt"):
        d = ' stroke-dasharray="%s"' % dash if dash else ""
        self.b.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="%s" '
                      'stroke-linecap="%s"%s/>' % (x1, y1, x2, y2, stroke or K["line"], sw, cap, d))
        return self

    def txt(self, x, y, s, size=13, fill=None, anchor="start", bold=False, mono=False, op=None):
        fw = ' font-weight="700"' if bold else ""
        fm = ' font-family="Consolas,Courier New,monospace"' if mono else ""
        o = ' opacity="%s"' % op if op else ""
        self.b.append('<text x="%.1f" y="%.1f" font-size="%s" fill="%s" text-anchor="%s"%s%s%s>%s</text>'
                      % (x, y, size, fill or K["txt"], anchor, fw, fm, o, esc(s)))
        return self

    def circle(self, cx, cy, r, fill="none", stroke="none", sw=1):
        self.b.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s" stroke="%s" stroke-width="%s"/>'
                      % (cx, cy, r, fill, stroke, sw))
        return self

    def path(self, d, fill="none", stroke="none", sw=1, dash=None, cap="round"):
        ds = ' stroke-dasharray="%s"' % dash if dash else ""
        self.b.append('<path d="%s" fill="%s" stroke="%s" stroke-width="%s" stroke-linecap="%s"%s/>'
                      % (d, fill, stroke, sw, cap, ds))
        return self

    # ---------- 定位 ----------
    def at(self, key, x, y):
        self._ids[key] = (x, y)
        return self

    def pos(self, key):
        return self._ids.get(key)

    # ---------- 标注 ----------
    def mark(self, key, n, note="", side="right", gap=17, lead=True):
        x, y = self._ids[key] if isinstance(key, str) else key
        if side == "right":
            cx, cy, ex, ey = x + gap, y, x, y
        elif side == "left":
            cx, cy, ex, ey = x - gap, y, x, y
        elif side == "top":
            cx, cy, ex, ey = x, y - gap, x, y
        elif side == "bottom":
            cx, cy, ex, ey = x, y + gap, x, y
        else:  # 精确定位 (dx, dy)
            cx, cy = x + gap[0], y + gap[1]
            ex, ey = x, y
        if lead:
            self.b.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                          'stroke-width="1.4" opacity="0.75"/>' % (ex, ey, cx, cy, K["mark"]))
        self.b.append('<circle cx="%.1f" cy="%.1f" r="13.4" fill="#ffffff"/>' % (cx, cy))
        self.b.append('<circle cx="%.1f" cy="%.1f" r="11" fill="%s"/>' % (cx, cy, K["mark"]))
        self.txt(cx, cy + 4.6, str(n), 12.5, "#ffffff", "middle", bold=True)
        self._marks.append((n, note))
        return self

    def marks(self):
        return list(self._marks)

    # ---------- 输出 ----------
    def svg(self):
        return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %.0f %.0f" width="100%%" '
                'font-family="Microsoft YaHei, Segoe UI, sans-serif">%s</svg>'
                % (self.w, self.h, "".join(self.b)))


# ============================================================
#  线条图标（单色几何，模仿 WPS 功能区分组图标）
# ============================================================
def ico(f, x, y, kind, s=20, c=None, sw=1.5):
    """在 (x,y) 左上角画 s×s 图标"""
    c = c or K["txt2"]
    h = s / 2
    if kind == "paste":
        f.rect(x + s * .22, y + s * .16, s * .56, s * .72, "none", c, sw, 1.5)
        f.rect(x + s * .36, y + s * .08, s * .28, s * .14, "#fff", c, sw, 1.5)
        f.line(x + s * .32, y + s * .40, x + s * .68, y + s * .40, c, sw)
        f.line(x + s * .32, y + s * .58, x + s * .68, y + s * .58, c, sw)
    elif kind == "cut":
        f.line(x + s * .2, y + s * .2, x + s * .7, y + s * .75, c, sw)
        f.line(x + s * .8, y + s * .2, x + s * .3, y + s * .75, c, sw)
        f.circle(x + s * .22, y + s * .8, s * .12, "none", c, sw)
        f.circle(x + s * .78, y + s * .8, s * .12, "none", c, sw)
    elif kind == "copy":
        f.rect(x + s * .14, y + s * .12, s * .52, s * .62, "none", c, sw, 1.5)
        f.rect(x + s * .34, y + s * .28, s * .52, s * .62, "#fff", c, sw, 1.5)
    elif kind == "brush":
        f.rect(x + s * .2, y + s * .14, s * .6, s * .3, "none", c, sw, 1)
        f.path("M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" % (x + s * .38, y + s * .44, x + s * .62, y + s * .44,
                                                        x + s * .5, y + s * .86), "none", c, sw)
    elif kind == "font":
        f.txt(x + s * .5, y + s * .78, "A", s * .92, c, "middle", bold=True)
    elif kind == "para":
        f.txt(x + s * .5, y + s * .78, "¶", s * 1.0, c, "middle")
    elif kind == "style":
        f.txt(x + s * .5, y + s * .78, "A", s * .8, c, "middle", bold=True)
        f.rect(x + s * .12, y + s * .84, s * .76, s * .12, "none", c, sw, 1)
    elif kind == "find":
        f.circle(x + s * .42, y + s * .42, s * .26, "none", c, sw)
        f.line(x + s * .62, y + s * .62, x + s * .88, y + s * .88, c, sw + .4)
    elif kind == "replace":
        f.txt(x + s * .38, y + s * .5, "A", s * .5, c, "middle")
        f.txt(x + s * .62, y + s * .92, "B", s * .5, c, "middle")
        f.line(x + s * .14, y + s * .38, x + s * .86, y + s * .38, c, sw)
    elif kind == "table":
        f.rect(x + s * .12, y + s * .18, s * .76, s * .64, "none", c, sw, 1)
        f.line(x + s * .12, y + s * .38, x + s * .88, y + s * .38, c, sw)
        f.line(x + s * .12, y + s * .6, x + s * .88, y + s * .6, c, sw)
        f.line(x + s * .44, y + s * .18, x + s * .44, y + s * .82, c, sw)
    elif kind == "picture":
        f.rect(x + s * .1, y + s * .2, s * .8, s * .6, "none", c, sw, 1.5)
        f.circle(x + s * .32, y + s * .38, s * .07, "none", c, sw)
        f.path("M%.1f %.1f L%.1f %.1f L%.1f %.1f L%.1f %.1f" % (
            x + s * .18, y + s * .74, x + s * .42, y + s * .48, x + s * .58, y + s * .66, x + s * .7, y + s * .56),
            "none", c, sw)
        f.path("M%.1f %.1f L%.1f %.1f L%.1f %.1f" % (
            x + s * .7, y + s * .56, x + s * .78, y + s * .66, x + s * .86, y + s * .74), "none", c, sw)
    elif kind == "shape":
        f.path("M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" % (x + s * .5, y + s * .15, x + s * .86, y + s * .82,
                                                        x + s * .14, y + s * .82), "none", c, sw)
    elif kind == "chart":
        f.line(x + s * .12, y + s * .82, x + s * .88, y + s * .82, c, sw)
        f.rect(x + s * .2, y + s * .5, s * .14, s * .3, c, c, 0, 0)
        f.rect(x + s * .42, y + s * .32, s * .14, s * .48, c, c, 0, 0)
        f.rect(x + s * .64, y + s * .58, s * .14, s * .22, c, c, 0, 0)
    elif kind == "page":
        f.rect(x + s * .2, y + s * .12, s * .6, s * .76, "#fff", c, sw, 1)
        f.line(x + s * .3, y + s * .34, x + s * .7, y + s * .34, c, sw)
        f.line(x + s * .3, y + s * .5, x + s * .7, y + s * .5, c, sw)
        f.line(x + s * .3, y + s * .66, x + s * .56, y + s * .66, c, sw)
    elif kind == "pagehdr":
        f.rect(x + s * .2, y + s * .12, s * .6, s * .76, "#fff", c, sw, 1)
        f.rect(x + s * .2, y + s * .12, s * .6, s * .2, "#e8eef8", c, sw, 1)
        f.line(x + s * .3, y + s * .5, x + s * .7, y + s * .5, c, sw)
        f.line(x + s * .3, y + s * .66, x + s * .6, y + s * .66, c, sw)
    elif kind == "textbox":
        f.rect(x + s * .1, y + s * .22, s * .8, s * .48, "none", c, sw, 1)
        f.txt(x + s * .5, y + s * .56, "T", s * .5, c, "middle", bold=True)
    elif kind == "symbol":
        f.txt(x + s * .5, y + s * .74, "Ω", s * .8, c, "middle")
    elif kind == "formula":
        f.txt(x + s * .5, y + s * .78, "√", s * .86, c, "middle")
    elif kind == "link":
        f.path("M%.1f %.1f a%.1f %.1f 0 0 1 0 %.1f" % (x + s * .3, y + s * .45, s * .16, s * .16, s * .28),
               "none", c, sw)
        f.path("M%.1f %.1f a%.1f %.1f 0 0 0 0 %.1f" % (x + s * .7, y + s * .55, s * .16, s * .16, -s * .28),
               "none", c, sw)
    elif kind == "toc":
        f.line(x + s * .16, y + s * .26, x + s * .84, y + s * .26, c, sw)
        f.line(x + s * .3, y + s * .48, x + s * .84, y + s * .48, c, sw)
        f.line(x + s * .3, y + s * .7, x + s * .84, y + s * .7, c, sw)
    elif kind == "caption":
        f.rect(x + s * .16, y + s * .2, s * .68, s * .5, "none", c, sw, 1)
        f.rect(x + s * .16, y + s * .76, s * .5, s * .12, c, "none", 0, 0)
    elif kind == "review":
        f.path("M%.1f %.1f L%.1f %.1f L%.1f %.1f" % (x + s * .18, y + s * .5, x + s * .4, y + s * .74,
                                                      x + s * .84, y + s * .22), "none", c, sw + .3)
    elif kind == "comment":
        f.path("M%.1f %.1f h%.1f a3 3 0 0 1 3 3 v%.1f a3 3 0 0 1 -3 3 h%.1f l-%.1f %.1f v-%.1f a3 3 0 0 1 -3 -3 v-%.1f a3 3 0 0 1 3 -3 Z"
               % (x + s * .14, y + s * .2, s * .72, s * .3, s * .46, s * .14, s * .14, s * .2, s * .46), "none", c, sw)
    elif kind == "view":
        f.circle(x + s * .5, y + s * .5, s * .3, "none", c, sw)
        f.circle(x + s * .5, y + s * .5, s * .1, c, "none", 0)
    elif kind == "zoom":
        f.circle(x + s * .44, y + s * .44, s * .26, "none", c, sw)
        f.line(x + s * .64, y + s * .64, x + s * .86, y + s * .86, c, sw)
    elif kind == "sheet":
        f.rect(x + s * .12, y + s * .16, s * .76, s * .68, "#fff", c, sw, 1)
        f.line(x + s * .12, y + s * .36, x + s * .88, y + s * .36, c, sw)
        f.line(x + s * .38, y + s * .16, x + s * .38, y + s * .84, c, sw)
    elif kind == "slide":
        f.rect(x + s * .1, y + s * .22, s * .8, s * .52, "#fff", c, sw, 1)
        f.line(x + s * .34, y + s * .86, x + s * .66, y + s * .86, c, sw + .4)
        f.line(x + s * .5, y + s * .74, x + s * .5, y + s * .86, c, sw)
    elif kind == "play":
        f.path("M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" % (x + s * .3, y + s * .2, x + s * .82, y + s * .5,
                                                        x + s * .3, y + s * .8), c, c, 1)
    elif kind == "fx":
        f.txt(x + s * .5, y + s * .74, "fx", s * .56, c, "middle", bold=True)
    elif kind in ("b", "i", "u", "s"):
        t = {"b": "B", "i": "I", "u": "U", "s": "S"}[kind]
        f.txt(x + s * .5, y + s * .74, t, s * .82, c, "middle", bold=True)
        if kind == "u":
            f.line(x + s * .2, y + s * .84, x + s * .8, y + s * .84, c, sw)
        if kind == "s":
            f.line(x + s * .18, y + s * .52, x + s * .82, y + s * .52, c, sw)
    elif kind == "bullets":
        for i in range(3):
            f.circle(x + s * .22, y + s * (.28 + i * .22), s * .05, c)
            f.line(x + s * .38, y + s * (.28 + i * .22), x + s * .84, y + s * (.28 + i * .22), c, sw)
    elif kind == "number":
        f.txt(x + s * .16, y + s * .32, "1.", s * .3, c)
        f.txt(x + s * .16, y + s * .62, "2.", s * .3, c)
        f.txt(x + s * .16, y + s * .92, "3.", s * .3, c)
        for i in range(3):
            f.line(x + s * .44, y + s * (.26 + i * .3), x + s * .86, y + s * (.26 + i * .3), c, sw)
    elif kind == "multi":
        f.line(x + s * .18, y + s * .26, x + s * .7, y + s * .26, c, sw)
        f.line(x + s * .3, y + s * .5, x + s * .82, y + s * .5, c, sw)
        f.line(x + s * .42, y + s * .74, x + s * .9, y + s * .74, c, sw)
    elif kind == "al":
        for i, ww in enumerate([.8, .56, .72, .46]):
            f.line(x + s * .14, y + s * (.24 + i * .18), x + s * (.14 + ww), y + s * (.24 + i * .18), c, sw)
    elif kind == "ac":
        for i, ww in enumerate([.7, .5, .62, .4]):
            x1 = (1 - ww) / 2
            f.line(x + s * x1, y + s * (.24 + i * .18), x + s * (x1 + ww), y + s * (.24 + i * .18), c, sw)
    elif kind == "ar":
        for i, ww in enumerate([.8, .56, .72, .46]):
            f.line(x + s * (.86 - ww), y + s * (.24 + i * .18), x + s * .86, y + s * (.24 + i * .18), c, sw)
    elif kind == "aj":
        for i, ww in enumerate([.74, .74, .74, .5]):
            x1 = (1 - ww) / 2
            f.line(x + s * x1, y + s * (.24 + i * .18), x + s * (x1 + ww), y + s * (.24 + i * .18), c, sw)
    elif kind == "ls":
        f.line(x + s * .16, y + s * .3, x + s * .84, y + s * .3, c, sw)
        f.line(x + s * .16, y + s * .7, x + s * .84, y + s * .7, c, sw)
        f.path("M%.1f %.1f L%.1f %.1f L%.1f %.1f" % (x + s * .34, y + s * .18, x + s * .5, y + s * .04,
                                                      x + s * .66, y + s * .18), "none", c, sw)
        f.path("M%.1f %.1f L%.1f %.1f L%.1f %.1f" % (x + s * .34, y + s * .82, x + s * .5, y + s * .96,
                                                      x + s * .66, y + s * .82), "none", c, sw)
    elif kind == "ind":
        f.line(x + s * .14, y + s * .2, x + s * .86, y + s * .2, c, sw)
        f.line(x + s * .34, y + s * .46, x + s * .86, y + s * .46, c, sw)
        f.line(x + s * .34, y + s * .72, x + s * .86, y + s * .72, c, sw)
        f.path("M%.1f %.1f L%.1f %.1f L%.1f %.1f" % (x + s * .1, y + s * .5, x + s * .26, y + s * .6,
                                                      x + s * .1, y + s * .7), "none", c, sw)
    elif kind == "outd":
        f.line(x + s * .14, y + s * .2, x + s * .86, y + s * .2, c, sw)
        f.line(x + s * .34, y + s * .46, x + s * .86, y + s * .46, c, sw)
        f.line(x + s * .34, y + s * .72, x + s * .86, y + s * .72, c, sw)
        f.path("M%.1f %.1f L%.1f %.1f L%.1f %.1f" % (x + s * .26, y + s * .5, x + s * .1, y + s * .6,
                                                      x + s * .26, y + s * .7), "none", c, sw)
    elif kind == "paint":
        f.rect(x + s * .2, y + s * .12, s * .56, s * .2, "none", c, sw, 1)
        f.path("M%.1f %.1f L%.1f %.1f L%.1f %.1f" % (x + s * .28, y + s * .32, x + s * .5, y + s * .56,
                                                      x + s * .72, y + s * .32), c, c, 1)
        f.rect(x + s * .34, y + s * .56, s * .3, s * .3, c, c, 1)
    elif kind == "sort":
        f.line(x + s * .14, y + s * .3, x + s * .86, y + s * .3, c, sw)
        f.line(x + s * .14, y + s * .7, x + s * .86, y + s * .7, c, sw)
        f.path("M%.1f %.1f L%.1f %.1f L%.1f %.1f" % (x + s * .5, y + s * .06, x + s * .62, y + s * .18,
                                                      x + s * .38, y + s * .18), "none", c, sw)
    else:
        f.rect(x + s * .2, y + s * .2, s * .6, s * .6, "none", c, sw, 2)


# ============================================================
#  窗口骨架
# ============================================================
def title_bar(f, x, y, w, title="", app="wps", h=30, quick=True):
    f.rect(x, y, w, h, K["chrome"])
    f.line(x, y + h, x + w, y + h, K["line"], 1)
    col = {"wps": "#2b6cff", "et": "#1f9d55", "wpp": "#d9542b"}.get(app, "#2b6cff")
    f.rect(x + 9, y + h / 2 - 7.5, 15, 15, col, "none", 0, 3)
    f.txt(x + 16.5, y + h / 2 + 4.2, {"wps": "W", "et": "E", "wpp": "P"}.get(app, "W"),
          10.5, "#ffffff", "middle", bold=True)
    if quick:
        for i, g in enumerate(["↶", "↷"]):
            f.txt(x + 32 + i * 17, y + h / 2 + 4.2, g, 12, K["txt3"], "middle")
    f.txt(x + w / 2, y + h / 2 + 4.4, title, 12.5, K["txt2"], "middle")
    # 右侧：搜索框 + 窗口按钮
    f.rect(x + w - 168, y + 6, 66, 18, "#f2f4f7", K["fieldb"], 1, 9)
    f.txt(x + w - 160, y + 18.5, "搜索", 10.5, K["txt3"])
    for i, g in enumerate(["—", "▢", "✕"]):
        f.txt(x + w - 74 + i * 22, y + h / 2 + 3.6, g, 10.5, K["txt3"], "middle")
    f.at("title", x + w / 2, y + h / 2)
    return f


def tab_strip(f, x, y, w, tabs, active=None, h=32):
    f.rect(x, y, w, h, K["tabbar"])
    f.line(x, y + h, x + w, y + h, K["line2"], 1)
    on_file = active == "文件"
    f.rect(x + 54, y + 3, 42, h - 6, K["blue2"] if on_file else K["chrome"],
           K["blue"] if on_file else K["line2"], 1, 2)
    f.txt(x + 75, y + h / 2 + 4.2, "文件", 13, K["blue"] if on_file else K["txt2"], "middle", bold=on_file)
    f.at("tab:文件", x + 75, y + h / 2)
    cx = x + 100
    for t in tabs:
        tw = 16 + len(t) * 13.8
        on = (t == active)
        if on:
            f.rect(cx, y + 3, tw, h - 3, K["chrome"], K["line2"], 1, 2)
            f.line(cx + 1, y + h, cx + tw - 1, y + h, K["chrome"], 2)
            f.rect(cx + 5, y + h - 2.4, tw - 10, 2.4, K["blue"])
        f.txt(cx + tw / 2, y + h / 2 + 4.4, t, 13,
              K["blue"] if on else K["txt2"], "middle", bold=on)
        f.at("tab:" + t, cx + tw / 2, y + h / 2)
        cx += tw + 1
    return f


def ribbon(f, x, y, w, groups, h=86):
    """groups = [(组名, 组宽, [行...])]，行 = [(元素...)]，元素 = (kind, 标签, 宽度[, 图标])"""
    f.rect(x, y, w, h, K["ribbon"])
    f.line(x, y + h, x + w, y + h, K["line2"], 1)
    cx = x + 8
    for gi, g in enumerate(groups):
        name, gw, rows = g[0], g[1], g[2]
        launcher = bool(g[3]) if len(g) > 3 else False
        gx, top = cx, y + 6
        for row in rows:
            big = any(e[0] == "big" for e in row)
            rh = 50 if big else 22
            rx = gx
            for el in row:
                kind, lab = el[0], el[1]
                bw = el[2] if len(el) > 2 else 46
                ic = el[3] if len(el) > 3 else ""
                if kind == "big":
                    ico(f, rx + (bw - 22) / 2, top + 3, ic, 22, K["blue"])
                    f.txt(rx + bw / 2, top + 43, lab, 11.5, K["txt"], "middle")
                    f.at("big:" + lab, rx + bw / 2, top + 26)
                    rx += bw
                elif kind == "btn":
                    f.rect(rx, top + 1, bw, 20, "#ffffff", K["fieldb"], 1, 2)
                    f.txt(rx + bw / 2, top + 15, lab, 11.5, K["txt"], "middle")
                    f.at("btn:" + lab, rx + bw / 2, top + 11)
                    rx += bw + 3
                elif kind == "ico":
                    ico(f, rx + 3, top + 2, ic, 18, K["ico"])
                    f.at("ico:" + ic, rx + 12, top + 11)
                    rx += 26
                elif kind == "combo":
                    f.rect(rx, top + 1, bw, 21, "#ffffff", K["fieldb"], 1, 2)
                    f.txt(rx + 6, top + 15.5, lab, 11.5, K["txt"])
                    f.txt(rx + bw - 9, top + 15, "▾", 9, K["txt3"], "middle")
                    f.at("combo:" + lab, rx + bw / 2, top + 11)
                    rx += bw + 3
            top += rh + 2
        # 组名 + 分隔线
        lblw = max(gw, 30)
        f.txt(gx + lblw / 2, y + h - 5, name, 10.8, K["txt3"], "middle")
        f.at("grp:" + name, gx + lblw / 2, y + h - 10)
        if launcher:
            lx, ly = gx + lblw - 6, y + h - 13
            f.rect(lx - 3.4, ly - 3.4, 6.8, 6.8, "none", K["txt3"], 1, 1)
            f.at("launcher:" + name, lx, ly)
        cx = gx + lblw + 8
        if gi < len(groups) - 1:
            f.line(cx - 4, y + 6, cx - 4, y + h - 16, K["line2"], 1)
    return f


def status_bar(f, x, y, w, left="", h=22, zoom=True):
    f.rect(x, y, w, h, K["chrome"])
    f.line(x, y, x + w, y, K["line2"], 1)
    f.txt(x + 12, y + h / 2 + 4, left, 11, K["txt3"])
    if zoom:
        rx = x + w - 190
        f.txt(rx, y + h / 2 + 4, "−", 10, K["txt3"], "middle")
        f.rect(rx + 12, y + h / 2 - 1.5, 92, 3, K["line2"], "none", 0, 1.5)
        f.circle(rx + 64, y + h / 2, 4.2, K["txt3"])
        f.txt(rx + 116, y + h / 2 + 4, "+", 10, K["txt3"], "middle")
        f.txt(rx + 142, y + h / 2 + 4, "100%", 11, K["txt3"])
    return f


def window(f, w=1000, h=520, title="", app="wps", tabs=(), active=None, hdr_h=30,
           tab_h=32, rib_h=86, status=True, status_left=""):
    """整体窗口骨架，返回 (功能区起始 y, 文档区起点 y)"""
    f.rect(0, 0, w, h, "#ffffff")
    f.rect(0, 0, w, h, "none", K["line2"], 1)
    title_bar(f, 0, 0, w, title, app, hdr_h)
    tab_strip(f, 0, hdr_h, w, tabs, active, tab_h)
    ry = hdr_h + tab_h
    f.rect(0, ry, w, rib_h, K["ribbon"])
    by = ry + rib_h
    bh = h - by - (22 if status else 0)
    f.rect(0, by, w, bh, K["doc"])
    if status:
        status_bar(f, 0, h - 22, w, status_left)
    return ry, by, bh


# ============================================================
#  文档纸 / 表格 / 幻灯片
# ============================================================
def shadow(f, x, y, w, h, r=0, op=0.13, dy=2):
    f.rect(x + 0.8, y + dy, w, h, "#000000", "none", 0, r, op)
    return f


def page(f, x, y, w, h, title="", lines=0, top=26, lead=0, border=True):
    shadow(f, x, y, w, h, 1, 0.12, 2)
    f.rect(x, y, w, h, K["page"], K["line2"] if border else "none", 0.8, 1)
    ty = y + top
    if title:
        f.txt(x + w / 2, ty + 6, title, 15, "#1a2129", "middle", bold=True)
        ty += 24
    if lead:
        ty = text_lines(f, x + 34, ty, w - 68, lead) + 8
    if lines:
        text_lines(f, x + 34, ty, w - 68, lines)
    return f


def text_lines(f, x, y, w, n, gap=14, color="#c9d0da", h=4.2):
    for i in range(n):
        wd = w - [0, 28, 10, 36, 6, 22][i % 6]
        f.rect(x, y + i * gap, wd, h, color, "none", 0, 2)
    return y + n * gap


def cell_table(f, x, y, cols, rows, rowh=22, head=True, fills=None, size=11.5, grid=None,
               colw=None, align=None):
    """画表格；cols 为表头文字列表，rows 为二维数据"""
    grid = grid or K["grid"]
    total = sum(colw) if colw else None
    xs = [x]
    if colw:
        for cw in colw:
            xs.append(xs[-1] + cw)
    else:
        cw = (total or 300) / len(cols)
        xs = [x + i * cw for i in range(len(cols) + 1)]
    nrow = len(rows) + (1 if head else 0)
    allrows = ([cols] if head else []) + list(rows)
    for ri, row in enumerate(allrows):
        ry = y + ri * rowh
        for ci, val in enumerate(row):
            fill = K["head"] if (head and ri == 0) else "#ffffff"
            if fills and (ri, ci) in fills:
                fill = fills[(ri, ci)]
            f.rect(xs[ci], ry, xs[ci + 1] - xs[ci], rowh, fill, grid, 0.9, 0)
            al = (align[ci] if align else ("middle" if ci == 0 else "start"))
            tx = (xs[ci] + xs[ci + 1]) / 2 if al == "middle" else xs[ci] + 7
            f.txt(tx, ry + rowh / 2 + 4, val, size, K["txt"] if not (head and ri == 0) else K["txt2"],
                  al, bold=(head and ri == 0))
    return f


def sheet_grid(f, x, y, w, h, colw=78, rowh=22, rowhdr=26, colhdr=22, cols=None,
               rows_n=14, data=None):
    """表格工作区：列标 + 行号 + 网格 + 可选数据"""
    f.rect(x, y, w, h, "#ffffff", K["line2"], 0.8)
    f.rect(x, y, w, colhdr, K["head"])
    f.rect(x, y, rowhdr, h, K["head"])
    if cols is None:
        ncol = int((w - rowhdr) / colw) + 1
        cols = [chr(65 + (i % 26)) for i in range(ncol)]
    for i, c in enumerate(cols):
        cx = x + rowhdr + i * colw
        if cx + colw > x + w:
            break
        f.line(cx, y, cx, y + h, K["grid"], 0.8)
        f.txt(cx + colw / 2, y + 15, c, 10.5, K["txt3"], "middle")
    n = int((h - colhdr) / rowh) + 1
    for r in range(n):
        ry = y + colhdr + r * rowh
        f.line(x, ry, x + w, ry, K["grid"], 0.8)
        f.txt(x + rowhdr / 2, ry + rowh / 2 + 3.6, str(r + 1), 10.5, K["txt3"], "middle")
    f.line(x + rowhdr, y, x + rowhdr, y + h, K["grid"], 1)
    f.line(x, y + colhdr, x + w, y + colhdr, K["grid"], 1)
    if data:
        for (r, c), val in data.items():
            cx = x + rowhdr + c * colw
            ry = y + colhdr + r * rowh
            f.txt(cx + 5, ry + rowh / 2 + 3.6, val, 10.5, K["txt"])
    return f


def spec_table(f, x, y, w, rows, title="版式基准", colw=(84,), rowh=27, size=11.2,
               head=("项目", "基准值")):
    """右侧参数清单：标题 + 两列表格（用于「成稿版式基准」一类图）"""
    if title:
        f.txt(x, y + 12, title, 13, K["txt"], bold=True)
        f.line(x, y + 21, x + w, y + 21, K["line"], 1.2)
        y += 30
    allrows = [list(head)] + [list(r) for r in rows]
    for ri, row in enumerate(allrows):
        ry = y + ri * rowh
        fill = K["head"] if ri == 0 else ("#fafbfc" if ri % 2 == 0 else "#ffffff")
        f.rect(x, ry, w, rowh, fill, K["grid"], 0.9)
        f.line(x + colw[0], ry, x + colw[0], ry + rowh, K["grid"], 0.9)
        f.txt(x + 8, ry + rowh / 2 + 4, row[0], size,
              K["txt2"] if ri == 0 else K["txt2"], bold=(ri == 0))
        f.txt(x + colw[0] + 8, ry + rowh / 2 + 4, row[1], size,
              K["txt"] if ri else K["txt2"], bold=(ri == 0))
    return y + len(allrows) * rowh


def slide_canvas(f, x, y, w, h, title="", sub="", bullets=0, kind="title"):
    """幻灯片画布（4:3 或 16:9 由 w/h 决定）"""
    shadow(f, x, y, w, h, 1, 0.12, 2)
    f.rect(x, y, w, h, "#ffffff", K["line2"], 0.8, 1)
    if kind == "title":
        f.rect(x, y + h * .34, w, 3, K["blue"], "none", 0, 0)
        f.txt(x + w / 2, y + h * .30, title, w / 22, K["txt"], "middle", bold=True)
        if sub:
            f.txt(x + w / 2, y + h * .52, sub, w / 40, K["txt3"], "middle")
    elif kind == "content":
        f.txt(x + w * .08, y + h * .16, title, w / 26, K["txt"], bold=True)
        f.rect(x + w * .08, y + h * .21, w * .1, 2.4, K["blue"])
        for i in range(bullets):
            yy = y + h * .32 + i * (h * .11)
            f.circle(x + w * .1, yy - 3, 2.6, K["blue"])
            f.rect(x + w * .13, yy - 6, w * (.55 - i * .05), 5, "#c9d0da", "none", 0, 2)
    elif kind == "blank":
        pass
    return f


# ============================================================
#  对话框 / 菜单 / 窗格
# ============================================================
def dlg(f, x, y, w, h, title, tabs=None, active=None, close=True):
    shadow(f, x, y, w, h, 4, 0.22, 4)
    f.rect(x, y, w, h, "#ffffff", K["line2"], 1, 4)
    f.rect(x, y, w, 30, "#f7f8fa", K["line2"], 1, 4)
    f.rect(x + 1, y + 22, w - 2, 8, "#f7f8fa")
    f.txt(x + 13, y + 20, title, 12.5, K["txt"], bold=True)
    if close:
        f.txt(x + w - 15, y + 19.5, "✕", 11, K["txt3"], "middle")
    if tabs:
        dlg_tabs(f, x + 1, y + 30, tabs, active)
    return f


def dlg_tabs(f, x, y, tabs, active):
    cx = x
    for t in tabs:
        tw = 16 + len(t) * 12.6
        on = t == active
        f.rect(cx, y, tw, 26, "#ffffff" if on else "#f7f8fa", K["line2"], 1, 0)
        f.txt(cx + tw / 2, y + 17, t, 12, K["blue"] if on else K["txt2"], "middle", bold=on)
        if on:
            f.line(cx + 1, y + 26, cx + tw - 1, y + 26, "#ffffff", 2)
        f.at("dlgtab:" + t, cx + tw / 2, y + 13)
        cx += tw
    return f


def label(f, x, y, s, size=12, anchor="end", color=None):
    f.txt(x, y, s, size, color or K["txt2"], anchor)
    return f


def field(f, x, y, w, value="", h=22, focus=False, ph=False, size=12):
    f.rect(x, y, w, h, "#ffffff", K["blue"] if focus else K["fieldb"], 1.8 if focus else 1, 2)
    if value:
        f.txt(x + 6, y + h / 2 + 4, value, size, K["txt3"] if ph else K["txt"])
    return f


def spin(f, x, y, w, value, h=22, focus=False):
    f.rect(x, y, w, h, "#ffffff", K["blue"] if focus else K["fieldb"], 1.8 if focus else 1, 2)
    f.txt(x + 6, y + h / 2 + 4, value, 12, K["txt"])
    f.line(x + w - 15, y + 2, x + w - 15, y + h - 2, K["fieldb"], 1)
    f.txt(x + w - 7.5, y + 9, "▲", 6, K["txt3"], "middle")
    f.txt(x + w - 7.5, y + 18, "▼", 6, K["txt3"], "middle")
    return f


def combo_box(f, x, y, w, value, h=22, focus=False, ph=False):
    f.rect(x, y, w, h, "#ffffff", K["blue"] if focus else K["fieldb"], 1.8 if focus else 1, 2)
    f.txt(x + 6, y + h / 2 + 4, value, 12, K["txt3"] if ph else K["txt"])
    f.txt(x + w - 9, y + h / 2 + 3.6, "▾", 9, K["txt3"], "middle")
    return f


def check(f, x, y, s, on=False, size=13):
    f.rect(x, y, size, size, K["blue"] if on else "#ffffff", K["blue"] if on else K["fieldb"], 1.2, 2)
    if on:
        f.path("M%.1f %.1f L%.1f %.1f L%.1f %.1f" % (x + 3.4, y + 6.8, x + 5.6, y + 9.4, x + 9.8, y + 3.6),
               "none", "#ffffff", 1.8)
    if s:
        f.txt(x + size + 7, y + size / 2 + 4, s, 12, K["txt"])
    return f


def radio(f, x, y, s, on=False, size=13):
    f.circle(x + size / 2, y + size / 2, size / 2, "#ffffff", K["blue"] if on else K["fieldb"], 1.2)
    if on:
        f.circle(x + size / 2, y + size / 2, size / 2 - 3.6, K["blue"])
    if s:
        f.txt(x + size + 7, y + size / 2 + 4, s, 12, K["txt"])
    return f


def btn(f, x, y, w, label, h=24, primary=False, disabled=False):
    f.rect(x, y, w, h, K["blue"] if primary else "#ffffff",
           K["blue"] if primary else K["fieldb"], 1, 3)
    f.txt(x + w / 2, y + h / 2 + 4, label, 12,
          "#ffffff" if primary else (K["txt3"] if disabled else K["txt"]), "middle")
    f.at("btn:" + label, x + w / 2, y + h / 2)
    return f


def menu(f, x, y, w, items, h_item=26, hi=None):
    h = 8
    for it in items:
        h += 7 if it[0] == "sep" else (23 if it[0] == "head" else h_item)
    shadow(f, x, y, w, h, 4, 0.20, 3)
    f.rect(x, y, w, h, "#ffffff", K["line2"], 1, 4)
    cy = y + 5
    for it in items:
        if it[0] == "sep":
            f.line(x + 8, cy + 3.5, x + w - 8, cy + 3.5, K["line"], 1)
            cy += 7
        elif it[0] == "head":
            f.txt(x + 11, cy + 15, it[1], 10.5, K["txt3"], bold=True)
            cy += 23
        else:
            lab = it[0]
            key = it[1] if len(it) > 1 else ""
            if hi and lab == hi:
                f.rect(x + 4, cy + 1, w - 8, h_item - 2, K["blue2"], "none", 0, 3)
            f.txt(x + 12, cy + 17, lab, 12, K["txt"])
            if key:
                f.txt(x + w - 12, cy + 17, key, 10.5, K["txt3"], "end")
            f.at("mi:" + lab, x + w / 2, cy + 13)
            cy += h_item
    return f


def pane(f, x, y, w, h, title, r=3, tabs=None, active=None):
    shadow(f, x, y, w, h, r, 0.13, 2)
    f.rect(x, y, w, h, "#ffffff", K["line2"], 1, r)
    f.rect(x, y, w, 28, "#f7f8fa", K["line2"], 1, r)
    f.txt(x + 11, y + 19, title, 12, K["txt"], bold=True)
    f.txt(x + w - 14, y + 19, "✕", 10.5, K["txt3"], "middle")
    if tabs:
        tx = x + 10
        for t in tabs:
            on = t == active
            tw = 10 + len(t) * 11.5
            f.txt(tx + tw / 2, y + 48, t, 11.5, K["blue"] if on else K["txt3"], "middle", bold=on)
            if on:
                f.line(tx, y + 56, tx + tw, y + 56, K["blue"], 2)
            tx += tw + 12
    return f


def tip(f, x, y, w, text, h=26, size=11.5):
    f.rect(x, y, w, h, K["markbg"], "#f0cfa6", 1, 3)
    f.txt(x + 9, y + 17, text, size, "#8a4b06")
    return f


def arrow(f, x1, y1, x2, y2, color=None, sw=1.6, head=6):
    c = color or K["mark"]
    f.line(x1, y1, x2, y2, c, sw)
    import math
    ang = math.atan2(y2 - y1, x2 - x1)
    a1, a2 = ang + math.radians(152), ang - math.radians(152)
    f.path("M%.1f %.1f L%.1f %.1f L%.1f %.1f" % (
        x2 + head * math.cos(a1), y2 + head * math.sin(a1), x2, y2,
        x2 + head * math.cos(a2), y2 + head * math.sin(a2)), "none", c, sw)
    return f


# ============================================================
#  预置功能区（按真实 WPS 12.x 分组与顺序）
# ============================================================
def rib_wps_home():
    return [
        ("剪贴板", 62, [[("big", "粘贴", 46, "paste")]]),
        ("字体", 156, [
            [("combo", "宋体", 88), ("combo", "小四", 54)],
            [("btn", "B", 24), ("btn", "I", 24), ("btn", "U", 24), ("btn", "S", 24)],
        ], True),
        ("段落", 150, [
            [("ico", "", 18, "bullets"), ("ico", "", 18, "number"), ("ico", "", 18, "multi"),
             ("ico", "", 18, "ind"), ("ico", "", 18, "outd")],
            [("ico", "", 18, "al"), ("ico", "", 18, "ac"), ("ico", "", 18, "ar"),
             ("ico", "", 18, "aj"), ("ico", "", 18, "ls")],
        ], True),
        ("样式", 152, [[("combo", "正文", 134)]], True),
        ("编辑", 104, [[("big", "查找", 46, "find"), ("big", "替换", 46, "replace")]]),
    ]


def rib_wps_insert():
    return [
        ("表格", 62, [[("big", "表格", 50, "table")]]),
        ("插图", 168, [[("big", "图片", 50, "picture"), ("big", "形状", 50, "shape"), ("big", "图表", 50, "chart")]]),
        ("页眉页脚", 110, [[("big", "页眉", 50, "pagehdr"), ("big", "页脚", 50, "pagehdr")]]),
        ("文本", 168, [[("big", "文本框", 50, "textbox"), ("big", "艺术字", 50, "font"), ("big", "符号", 50, "symbol")]]),
        ("链接", 62, [[("big", "超链接", 50, "link")]]),
    ]


def rib_wps_page():
    return [
        ("页面设置", 168, [[("big", "页边距", 52, "page"), ("big", "纸张方向", 52, "page"),
                         ("big", "纸张大小", 52, "page")]]),
        ("页面背景", 168, [[("big", "水印", 52, "page"), ("big", "页面颜色", 52, "page"),
                         ("big", "页面边框", 52, "page")]]),
        ("分隔符", 62, [[("big", "分隔符", 52, "page")]]),
        ("分栏", 62, [[("big", "分栏", 52, "toc")]]),
    ]


def rib_wps_ref():
    return [
        ("目录", 62, [[("big", "目录", 52, "toc")]]),
        ("题注", 122, [[("big", "插入题注", 56, "caption"), ("big", "交叉引用", 56, "link")]]),
        ("脚注", 122, [[("big", "插入脚注", 56, "page"), ("big", "插入尾注", 56, "page")]]),
        ("引文与书目", 62, [[("big", "引文", 52, "caption")]]),
        ("索引", 62, [[("big", "标记索引", 52, "toc")]]),
    ]


def rib_wps_review():
    return [
        ("校对", 122, [[("big", "拼写检查", 56, "review"), ("big", "字数统计", 56, "fx")]]),
        ("批注", 62, [[("big", "新建批注", 56, "comment")]]),
        ("修订", 168, [[("big", "修订", 52, "review"), ("big", "接受", 52, "review"), ("big", "拒绝", 52, "review")]]),
        ("比较", 62, [[("big", "比较", 52, "review")]]),
    ]


def rib_wps_view():
    return [
        ("视图", 214, [[("big", "页面视图", 56, "view"), ("big", "阅读版式", 56, "view"),
                     ("big", "大纲", 56, "toc")]]),
        ("显示", 122, [[("big", "标尺", 56, "page"), ("big", "网格线", 56, "table")]]),
        ("显示比例", 122, [[("big", "显示比例", 56, "zoom"), ("big", "单页", 56, "page")]]),
        ("窗口", 122, [[("big", "并排比较", 56, "page"), ("big", "拆分", 56, "page")]]),
    ]


def rib_et_home():
    return [
        ("剪贴板", 62, [[("big", "粘贴", 46, "paste")]]),
        ("字体", 156, [
            [("combo", "宋体", 88), ("combo", "11", 52)],
            [("btn", "B", 24), ("btn", "I", 24), ("btn", "U", 24), ("btn", "S", 24)],
        ], True),
        ("对齐方式", 150, [
            [("ico", "", 18, "al"), ("ico", "", 18, "ac"), ("ico", "", 18, "ar"),
             ("ico", "", 18, "aj"), ("ico", "", 18, "ls")],
            [("ico", "", 18, "ind"), ("ico", "", 18, "outd"), ("ico", "", 18, "sort")],
        ]),
        ("数字格式", 152, [[("combo", "常规", 74), ("combo", "¥", 58)]]),
        ("样式", 122, [[("combo", "常规", 108)]]),
        ("单元格", 104, [[("big", "插入", 46, "table"), ("big", "删除", 46, "table")]]),
        ("编辑", 104, [[("big", "查找", 46, "find"), ("big", "求和", 46, "fx")]]),
    ]


def rib_et_insert():
    return [
        ("表格", 62, [[("big", "表格", 50, "table")]]),
        ("插图", 110, [[("big", "图片", 50, "picture"), ("big", "形状", 50, "shape")]]),
        ("图表", 62, [[("big", "图表", 50, "chart")]]),
        ("迷你图", 62, [[("big", "迷你图", 50, "chart")]]),
        ("筛选", 62, [[("big", "筛选", 50, "table")]]),
        ("数据透视表", 62, [[("big", "数据透视表", 52, "chart")]]),
    ]


def rib_et_page():
    return [
        ("页面设置", 168, [[("big", "页边距", 52, "page"), ("big", "纸张方向", 52, "page"),
                         ("big", "纸张大小", 52, "page")]]),
        ("打印", 168, [[("big", "打印区域", 52, "table"), ("big", "打印标题", 52, "table"),
                     ("big", "打印预览", 52, "view")]]),
        ("分隔符", 62, [[("big", "分隔符", 52, "page")]]),
        ("背景", 62, [[("big", "背景", 52, "picture")]]),
    ]


def rib_et_review():
    return [
        ("校对", 122, [[("big", "拼写检查", 56, "review"), ("big", "字数统计", 56, "fx")]]),
        ("批注", 62, [[("big", "新建批注", 56, "comment")]]),
        ("保护", 168, [[("big", "保护工作表", 52, "review"), ("big", "保护工作簿", 52, "review"),
                     ("big", "允许编辑区域", 52, "review")]]),
    ]


def rib_et_formula():
    return [
        ("函数库", 176, [[("big", "插入函数", 56, "fx"), ("big", "自动求和", 56, "fx"),
                       ("big", "最近使用", 56, "fx")]]),
        ("定义的名称", 122, [[("big", "名称管理器", 56, "fx"), ("big", "定义名称", 56, "fx")]]),
        ("公式审核", 168, [[("big", "追踪引用", 52, "fx"), ("big", "显示公式", 52, "fx")]]),
        ("计算", 62, [[("big", "计算选项", 52, "fx")]]),
    ]


def rib_et_data():
    return [
        ("获取数据", 122, [[("big", "导入数据", 56, "table"), ("big", "分列", 56, "table")]]),
        ("排序和筛选", 168, [[("big", "排序", 52, "sort"), ("big", "筛选", 52, "table"),
                          ("big", "高级", 52, "table")]]),
        ("数据工具", 168, [[("big", "删除重复项", 52, "table"), ("big", "数据验证", 52, "table"),
                        ("big", "合并计算", 52, "table")]]),
        ("分级显示", 122, [[("big", "分类汇总", 56, "table"), ("big", "组合", 56, "table")]]),
    ]


def rib_wpp_home():
    return [
        ("剪贴板", 62, [[("big", "粘贴", 46, "paste")]]),
        ("幻灯片", 168, [[("big", "新建幻灯片", 56, "slide"), ("big", "版式", 56, "slide"),
                      ("big", "重置", 52, "slide")]]),
        ("字体", 156, [
            [("combo", "微软雅黑", 92), ("combo", "28", 48)],
            [("btn", "B", 24), ("btn", "I", 24), ("btn", "U", 24), ("btn", "S", 24)],
        ]),
        ("段落", 150, [
            [("ico", "", 18, "bullets"), ("ico", "", 18, "number"), ("ico", "", 18, "multi"),
             ("ico", "", 18, "ind"), ("ico", "", 18, "outd")],
            [("ico", "", 18, "al"), ("ico", "", 18, "ac"), ("ico", "", 18, "ar"),
             ("ico", "", 18, "aj"), ("ico", "", 18, "ls")],
        ]),
        ("绘图", 62, [[("big", "形状", 52, "shape")]]),
        ("编辑", 104, [[("big", "查找", 46, "find"), ("big", "替换", 46, "replace")]]),
    ]


def rib_wpp_insert():
    return [
        ("表格", 62, [[("big", "表格", 50, "table")]]),
        ("插图", 168, [[("big", "图片", 50, "picture"), ("big", "形状", 50, "shape"),
                     ("big", "图标", 50, "shape")]]),
        ("图表", 62, [[("big", "图表", 50, "chart")]]),
        ("媒体", 110, [[("big", "音频", 50, "play"), ("big", "视频", 50, "play")]]),
        ("链接", 62, [[("big", "超链接", 50, "link")]]),
        ("文本", 110, [[("big", "文本框", 50, "textbox"), ("big", "艺术字", 50, "font")]]),
    ]


def rib_wpp_design():
    return [
        ("页面设置", 168, [[("big", "幻灯片大小", 56, "slide"), ("big", "主题", 52, "slide")]]),
        ("主题", 122, [[("big", "配色", 56, "font"), ("big", "字体", 56, "font")]]),
        ("背景", 62, [[("big", "背景", 52, "slide")]]),
        ("母版", 62, [[("big", "幻灯片母版", 52, "slide")]]),
    ]


def rib_wpp_anim():
    return [
        ("预览", 62, [[("big", "预览", 52, "play")]]),
        ("动画", 168, [[("big", "添加动画", 52, "play"), ("big", "动画窗格", 52, "toc"),
                     ("big", "动画刷", 52, "brush")]]),
        ("计时", 168, [[("big", "开始", 52, "play"), ("big", "持续时间", 52, "fx"),
                     ("big", "延迟", 52, "fx")]]),
    ]


def rib_wpp_slide():
    return [
        ("预览", 62, [[("big", "预览", 52, "play")]]),
        ("切换到此幻灯片", 168, [[("big", "切换效果", 52, "slide"), ("big", "效果选项", 52, "slide"),
                            ("big", "全部应用", 52, "slide")]]),
        ("计时", 168, [[("big", "单击时", 52, "play"), ("big", "持续时间", 52, "fx"),
                     ("big", "自动换片", 52, "fx")]]),
    ]


# ---------- 文档区辅助件 ----------
def ruler(f, x, y, w, origin=0, span=None, indent=None):
    """水平标尺：主刻度 1..，与页面左边界对齐；indent=(x1,x2) 画缩进滑块"""
    f.rect(x, y, w, 15, "#f8f9fb", K["line"], 0.8)
    step = 46
    n = int((w - origin) / step)
    for i in range(n + 1):
        px = x + origin + i * step
        if px > x + w - 4:
            break
        f.line(px, y + 3, px, y + 9, K["txt3"], 0.8)
        f.txt(px, y + 13.6, str(i * 2 + 1), 7.2, K["txt3"], "middle")
        for k in (1, 2, 3):
            mp = px + k * step / 4
            if mp < x + w - 2:
                f.line(mp, y + 6, mp, y + 9, K["line2"], 0.6)
    if indent:
        for ix in indent:
            f.path("M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" % (ix, y + 15, ix - 4.2, y + 9.6, ix + 4.2, y + 9.6),
                   "#6b7b92", "#6b7b92", 0.4)
    return f


def hscroll(f, x, y, w):
    f.rect(x, y, w, 14, "#f2f4f7", K["line"], 0.6)
    f.rect(x, y, w - 40, 14, "#dde3ec", "none", 0, 2)
    return f


# ============================================================
#  场景构造器：一步搭出「窗口 + 功能区 + 文档区」
# ============================================================
TABS_W = ["开始", "插入", "页面", "引用", "审阅", "视图", "工具"]
TABS_S = ["开始", "插入", "页面", "公式", "数据", "审阅", "视图", "工具"]
TABS_P = ["开始", "插入", "设计", "切换", "动画", "放映", "审阅", "视图"]


def doc_scene(title="文档.docx - WPS Office", tab="开始", groups=None, h=560,
              status="第 1 页，共 6 页　字数：2,860", page_kw=None, ruler_on=True, tabs=None):
    f = Fig(1000, h)
    ry, by, bh = window(f, 1000, h, title, "wps", tabs or TABS_W, tab, rib_h=84, status_left=status)
    ribbon(f, 0, ry, 1000, rib_wps_home() if groups is None else groups, h=84)
    if ruler_on:
        ruler(f, 0, by, 1000, origin=118, indent=(124, 248))
    if page_kw:
        kw = dict(x=118, y=by + 26, w=254, h=h - by - 56)
        kw.update(page_kw)
        page(f, **kw)
    return f, by


def sheet_scene(title="销售统计.xlsx - WPS 表格", tab="开始", groups=None, h=560,
                status="就绪　平均值:　计数:　求和:", data=None, cols=None, rows_n=14):
    f = Fig(1000, h)
    ry, by, bh = window(f, 1000, h, title, "et", TABS_S, tab, rib_h=84, status_left=status)
    ribbon(f, 0, ry, 1000, rib_et_home() if groups is None else groups, h=84)
    # 编辑栏
    f.rect(0, by, 1000, 24, "#ffffff")
    f.line(0, by + 24, 1000, by + 24, K["line2"], 1)
    f.rect(4, by + 3, 26, 18, "#ffffff", K["fieldb"], 0.8, 1)
    f.txt(17, by + 16, "A1", 10.5, K["txt2"], "middle")
    f.txt(40, by + 16, "fx", 11, K["txt3"])
    f.line(60, by + 4, 60, by + 20, K["line2"], 1)
    f.txt(68, by + 16, "=", 10.5, K["txt3"])
    # 工作表标签
    tabh = 20
    f.rect(0, h - 22 - tabh, 1000, tabh, "#f2f4f7")
    f.line(0, h - 22 - tabh, 1000, h - 22 - tabh, K["line2"], 1)
    for i, nm in enumerate(["Sheet1", "Sheet2", "Sheet3"]):
        tw = 62
        tx = 40 + i * (tw + 2)
        on = i == 0
        f.rect(tx, h - 22 - tabh + 2, tw, tabh - 2, "#ffffff" if on else "#e9edf3",
               K["line2"], 0.8, 1)
        f.txt(tx + tw / 2, h - 22 - tabh + 15, nm, 10.5, K["txt"] if on else K["txt3"], "middle")
    f.rect(0, by + 24, 1000, h - 22 - tabh - by - 24, "#ffffff")
    sheet_grid(f, 0, by + 24, 1000, h - 22 - tabh - by - 24, data=data,
               cols=None if cols is None else cols, rows_n=rows_n)
    return f, by


def slide_scene(title="演示文稿.pptx - WPS 演示", tab="开始", groups=None, h=540,
                status="幻灯片 1 / 8", slide_kw=None, panel=True):
    f = Fig(1000, h)
    ry, by, bh = window(f, 1000, h, title, "wpp", TABS_P, tab, rib_h=84, status_left=status)
    ribbon(f, 0, ry, 1000, rib_wpp_home() if groups is None else groups, h=84)
    # 左侧缩略图栏
    if panel:
        f.rect(0, by, 118, h - by - 22, "#f4f6f9")
        f.line(118, by, 118, h - 22, K["line2"], 1)
        for i in range(3):
            ty = by + 12 + i * 66
            if ty + 48 > h - 26:
                break
            f.rect(10, ty, 96, 54, "#ffffff" if i == 0 else "#fbfcfd",
                   K["blue"] if i == 0 else K["line2"], 1.4 if i == 0 else 0.8, 2)
            f.txt(6, ty + 30, str(i + 1), 9, K["txt3"], "middle")
    sx = (118 + 1000) / 2 - 320 if panel else 500 - 320
    kw = dict(x=sx, y=by + 22, w=640, h=360, title="", sub="", kind="title")
    if slide_kw:
        kw.update(slide_kw)
    slide_canvas(f, **kw)
    return f, by


# ============================================================
#  描述式对话框
# ============================================================
ROWH = {"g": 28, "c": 34, "cb": 28, "rd": 28, "sep": 12, "note": 22}


def _tw(s, size=11.8):
    """按中英文混排估算文字宽度（中文按 1 字宽，西文按 0.54）"""
    return sum(size if ord(c) > 127 else size * 0.54 for c in s)


def form(f, x, y, w, h=None, title="", rows=(), tabs=None, active=None,
         buttons=("确定", "取消"), pad=20):
    """rows 元素：
    ("g", "组标题") / ("sep",) / ("note", "说明")
    ("c", [(label, kind, value, width, key[, focus]) ...])  一行多个控件
    ("cb", "文字", 是否勾选, key) / ("rd", "文字", 是否选中, key)
    """
    head = 30 + 28 + 12 if tabs else 34
    if h is None:
        h = head + sum(ROWH[it[0]] for it in rows) + 52
    dlg(f, x, y, w, h, title, tabs, active)
    cy = y + head
    for it in rows:
        k = it[0]
        if k == "g":
            f.txt(x + pad, cy + 12, it[1], 12.5, K["txt"], bold=True)
            cy += 28
        elif k == "sep":
            f.line(x + pad, cy + 4, x + w - pad, cy + 4, K["line"], 1)
            cy += 12
        elif k == "note":
            f.txt(x + pad, cy + 11, it[1], 10.5, K["txt3"])
            cy += 22
        elif k == "c":
            cx = x + pad
            for cell in it[1]:
                lab, kind, val, cw = cell[0], cell[1], cell[2], cell[3]
                key = cell[4] if len(cell) > 4 else ""
                focus = cell[5] if len(cell) > 5 else False
                if lab:
                    f.txt(cx, cy + 19, lab, 11.8, K["txt2"])
                    cx += _tw(lab) + 8
                cw = min(cw, x + w - pad - cx - 8)
                if kind == "spin":
                    spin(f, cx, cy + 8, cw, val, focus=focus)
                elif kind == "combo":
                    combo_box(f, cx, cy + 8, cw, val, focus=focus)
                elif kind == "field":
                    field(f, cx, cy + 8, cw, val, focus=focus)
                if key:
                    f.at(key, cx + cw - 4, cy + 19)
                cx += cw + 18
            cy += 34
        elif k == "cb":
            cdx = it[4] if len(it) > 4 else 0
            check(f, x + pad + cdx, cy + 6, it[1], it[2])
            if len(it) > 3 and it[3]:
                f.at(it[3], x + pad + cdx + _tw(it[1]) + 20, cy + 12)
            cy += 28
        elif k == "rd":
            cdx = it[4] if len(it) > 4 else 0
            radio(f, x + pad + cdx, cy + 6, it[1], it[2])
            if len(it) > 3 and it[3]:
                f.at(it[3], x + pad + cdx + _tw(it[1]) + 20, cy + 12)
            cy += 28
    n = len(buttons)
    bx = x + w - pad - n * 68 - (n - 1) * 8
    for i, lab in enumerate(buttons):
        btn(f, bx + i * 76, y + h - 38, 68, lab, 24, primary=(i == 0))
    return f


def marks_from(f, items):
    """items = [(key, note, side, gap), ...] 依次编号"""
    for i, it in enumerate(items, 1):
        key, note = it[0], it[1]
        side = it[2] if len(it) > 2 else "right"
        gap = it[3] if len(it) > 3 else 22
        f.mark(key, i, note, side, gap)
    return f
