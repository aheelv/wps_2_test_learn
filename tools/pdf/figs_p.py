# -*- coding: utf-8 -*-
"""第三部分 · 演示文稿：界面示意图（课程 8 张）"""
from ui import *
import ui


def thumb_panel(f, by, h, n=4, active=0, labels=()):
    """左栏缩略图（覆盖默认，带编号与标题）"""
    for i in range(n):
        ty = by + 8 + i * 70
        if ty + 62 > h - 26:
            break
        on = i == active
        f.rect(12, ty, 96, 60, "#ffffff" if on else "#fbfcfd",
               K["blue"] if on else K["line2"], 1.6 if on else 0.8, 2)
        f.txt(6, ty + 34, str(i + 1), 9, K["txt3"], "middle")
        if i < len(labels) and labels[i]:
            f.txt(60, ty + 20, labels[i], 8.4, K["txt2"], "middle")
        if on:
            f.at("thumb", 60, ty + 30)
    return f


def slide_scene2(title="演示文稿.pptx - WPS 演示", tab="开始", groups=None, h=520,
                 status="幻灯片 1 / 6", labels=(), active=0, slide_kw=None):
    f, by = slide_scene(title=title, tab=tab, groups=groups, h=h, status=status,
                        slide_kw=slide_kw, panel=False)
    f.rect(0, by, 118, h - by - 22, "#f4f6f9")
    f.line(118, by, 118, h - 22, K["line2"], 1)
    thumb_panel(f, by, h, n=len(labels) or 4, active=active, labels=labels)
    return f, by


# ============================================================
#  课程配图
# ============================================================
def p7_1():
    """7.1 演示文稿基本操作与幻灯片管理"""
    f, by = slide_scene2(tab="开始", labels=("封面", "目录", "现状", "方案", "总结"),
                         active=2, slide_kw=dict(kind="content", title="二、现状分析", bullets=3))
    menu(f, 128, by + 168, 200, [("head", "幻灯片操作"), ("新建幻灯片", ""),
                                 ("复制幻灯片", ""), ("删除幻灯片", ""), ("sep",),
                                 ("隐藏幻灯片", "")], hi="复制幻灯片")
    marks_from(f, [
        ("big:新建幻灯片", "「开始」→「新建幻灯片」，或按 Ctrl+M", "bottom", 52),
        ("big:版式", "「版式」决定标题/内容占位符的位置", "bottom", 52),
        ("mi:复制幻灯片", "左栏缩略图右键：复制、删除、隐藏、移动", "right", 24),
    ])
    return f


def p7_2():
    """7.2 主题应用、背景设置与母版制作"""
    f, by = slide_scene2(tab="设计", groups=rib_wpp_design(), labels=("封面", "目录", "正文"),
                         active=1, slide_kw=dict(kind="title", title="毕业论文答辩", sub="答辩人：张三"))
    # 主题库
    tx, ty = 130, by + 152
    shadow(f, tx, ty, 420, 190, 4, 0.18, 3)
    f.rect(tx, ty, 420, 190, "#ffffff", K["line2"], 1, 4)
    f.txt(tx + 12, ty + 20, "主题", 12, K["txt"], bold=True)
    names = ["淡雅", "商务", "扁平", "学术", "简约", "渐变"]
    for i, nm in enumerate(names):
        cx = tx + 12 + (i % 3) * 132
        cy = ty + 32 + (i // 3) * 74
        f.rect(cx, cy, 118, 62, "#f2f5fa", K["line2"], 0.8, 2)
        f.rect(cx, cy, 118, 14, "#4a7bd6" if i == 3 else "#9db4d8", "none", 0, 2)
        f.rect(cx + 8, cy + 22, 58, 3.4, "#c9d4e4", "none", 0, 2)
        f.rect(cx + 8, cy + 31, 90, 3.4, "#dde4ee", "none", 0, 2)
        f.rect(cx + 8, cy + 40, 74, 3.4, "#dde4ee", "none", 0, 2)
        f.txt(cx + 59, cy + 55, nm, 9.2, K["txt2"], "middle")
        if i == 3:
            f.rect(cx - 1, cy - 1, 120, 64, "none", K["blue"], 1.6, 2)
            f.at("theme", cx + 59, cy + 30)
    marks_from(f, [
        ("big:配色", "「设计」→ 主题：一键改全部页面的配色与字体", "bottom", 52),
        ("theme", "选定主题后，母版占位符位置随之确定", "right", 24),
        ("big:幻灯片母版", "「视图」→「幻灯片母版」：改一处，全部页统一", "bottom", 52),
    ])
    return f


def p7_3():
    """7.3 文本、艺术字、图形与智能图形"""
    f, by = slide_scene2(tab="插入", groups=rib_wpp_insert(),
                         labels=("封面", "要点", "图示"), active=1,
                         slide_kw=dict(kind="content", title="三、实施路径", bullets=2))
    # 智能图形（三个箭头流程）
    ax, ay = 300, by + 250
    for i in range(3):
        bx = ax + i * 130
        f.rect(bx, ay, 108, 52, "#e8f0fb" if i != 1 else "#cfe0ff", "#7ea6e0", 1, 3)
        f.txt(bx + 54, ay + 20, ["调研", "设计", "上线"][i], 10, K["txt2"], "middle")
        f.txt(bx + 54, ay + 36, "阶段 %d" % (i + 1), 8, K["txt3"], "middle")
        if i < 2:
            f.path("M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" % (bx + 110, ay + 20, bx + 124, ay + 26,
                                                           bx + 110, ay + 32), "#7ea6e0", "none", 0.8)
    f.at("smart", ax + 110, ay + 26)
    marks_from(f, [
        ("big:文本框", "「插入」→「文本框」→ 横排 / 竖排", "bottom", 52),
        ("big:形状", "形状可设填充、轮廓、效果；按住 Shift 画正圆/正方", "bottom", 52),
        ("smart", "「智能图形」插入流程图，文字直接在占位符里打", "bottom", 24),
    ])
    return f


def p7_4():
    """7.4 图片、图表、音频与视频对象"""
    f, by = slide_scene2(tab="插入", groups=rib_wpp_insert(),
                         labels=("封面", "数据", "配图"), active=1,
                         slide_kw=dict(kind="content", title="四、数据支撑", bullets=0))
    # 图表
    cx, cy, cw, ch = 210, by + 120, 330, 220
    shadow(f, cx, cy, cw, ch, 3, 0.12, 2)
    f.rect(cx, cy, cw, ch, "#ffffff", K["line2"], 1, 3)
    base = cy + ch - 30
    for i, v in enumerate([62, 78, 45, 88]):
        bh = v * 1.4
        f.rect(cx + 34 + i * 66, base - bh, 40, bh, "#4a7bd6", "none", 0, 0)
        f.txt(cx + 54 + i * 66, base + 12, "Q%d" % (i + 1), 8, K["txt3"], "middle")
    f.line(cx + 24, base, cx + cw - 20, base, "#c8d0dc", 1)
    f.at("chart", cx + 160, cy + 110)
    # 音频图标
    f.rect(600, by + 220, 150, 56, "#f4f7fb", "#b9c3d0", 1, 3)
    f.circle(626, by + 248, 12, "#4a7bd6")
    f.path("M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" % (623, by + 242, 633, by + 248, 623, by + 254),
           "#ffffff", "none", 0.8)
    f.txt(650, by + 244, "背景音乐.mp3", 9, K["txt2"])
    f.txt(650, by + 258, "0:00 / 1:32", 8, K["txt3"])
    f.at("audio", 626, by + 248)
    marks_from(f, [
        ("big:图片", "「插入」→「图片」→ 本地图片；图片工具可裁剪、调亮度", "bottom", 52),
        ("chart", "「插入」→「图表」→ 选类型后弹出数据表，改数据即改图", "top", 24),
        ("audio", "「插入」→「音频 / 视频」→ 选文件，设自动播放", "bottom", 22),
    ])
    return f


def p8_1():
    """8.1 对象动画与幻灯片切换"""
    f, by = slide_scene2(tab="动画", groups=rib_wpp_anim(),
                         labels=("封面", "要点", "图示"), active=1,
                         slide_kw=dict(kind="content", title="五、关键措施", bullets=3))
    px, py, pw, ph = 640, by + 8, 320, 300
    pane(f, px, py, pw, ph, "动画窗格")
    rows = [("标题 1: 五、关键措施", "开始：单击时", 0), ("内容占位符: 淡出", "持续时间 0.5 秒", 1),
            ("矩形 3: 擦除", "开始：上一动画之后", 2)]
    for i, (nm, sub, lv) in enumerate(rows):
        ry = py + 44 + i * 54
        f.rect(px + 10, ry, pw - 20, 46, "#fbfcfd", K["line2"], 0.8, 2)
        f.txt(px + 22 + lv * 12, ry + 18, nm, 9.4, K["txt2"])
        f.txt(px + 22 + lv * 12, ry + 34, sub, 8.4, K["txt3"])
        if i == 1:
            f.at("animrow", px + 200, ry + 24)
    marks_from(f, [
        ("big:添加动画", "选中对象 →「动画」→「添加动画」→ 进入/强调/退出", "bottom", 52),
        ("animrow", "「动画窗格」里调顺序、开始方式、持续时间、延迟", "left", 22),
        ("tab:切换", "切到「切换」选项卡：整页动效 + 换片方式", "bottom", 30),
    ])
    return f


def p8_2():
    """8.2 超链接、交互设置与放映控制"""
    f, by = slide_scene2(tab="插入", groups=rib_wpp_insert(),
                         labels=("封面", "目录", "正文"), active=1,
                         slide_kw=dict(kind="content", title="目录", bullets=0))
    # 目录条目（可点击）
    for i, nm in enumerate(["一、研究背景", "二、现状分析", "三、实施路径"]):
        ty = by + 150 + i * 46
        f.txt(300, ty, nm, 12, K["blue"])
        f.rect(300, ty + 4, 150, 0.8, K["blue"], "none", 0, 0)
    f.at("link", 375, by + 168)
    dx, dy = 600, by + 150
    form(f, dx, dy, 360, title="编辑超链接", rows=[
        ("rd", "本文档中的位置", True),
        ("c", [("请选择文档中的位置", "combo", "3. 三、实施路径", 180)]),
        ("rd", "原有文件或网页", False),
    ])
    marks_from(f, [
        ("big:超链接", "选中文字 →「插入」→「超链接」→ 选「本文档中的位置」", "bottom", 52),
        ("link", "链接到指定幻灯片，放映时点击可跳转", "left", 22),
        ("big:图表", "动作按钮：形状里的「动作按钮」可做上一页/下一页", "bottom", 52),
    ])
    return f


def p8_3():
    """8.3 打包输出、保护与检查"""
    f, by = slide_scene2(tab="开始", labels=("封面", "目录", "正文"), active=0,
                         slide_kw=dict(kind="title", title="毕业论文答辩", sub="2026 年 7 月"))
    f.rect(0, by, 214, 520 - 22 - by, "#ffffff", K["line2"], 1)
    items = ["新建", "打开", "保存", "另存为", "输出为 PDF", "输出为视频", "文档加密", "打印"]
    cy = by + 14
    for it in items:
        on = it in ("输出为 PDF", "文档加密")
        if on:
            f.rect(8, cy, 198, 30, K["blue2"], "none", 0, 3)
        f.txt(24, cy + 20, it, 12.5, K["blue"] if on else K["txt"], bold=on)
        f.at("bs:" + it, 24, cy + 15)
        cy += 34
    dx, dy = 470, 226
    form(f, dx, dy, 400, title="文档加密", rows=[
        ("c", [("打开权限密码", "field", "••••••", 170, "pw1", True)]),
        ("c", [("修改权限密码", "field", "（可不设）", 170)]),
        ("sep",),
        ("note", "设置后每次打开都需输入密码；密码区分大小写"),
    ])
    marks_from(f, [
        ("bs:输出为 PDF", "「文件」→「输出为 PDF」：格式固定、不会跑版", "right", 24),
        ("bs:文档加密", "「文件」→「文档加密」→ 打开权限密码", "right", 24),
        ("pw1", "密码区分大小写，交卷前务必记住", "right", 24),
    ])
    return f


def p8_4():
    """8.4 综合实战：20 分演示题全流程"""
    f, by = slide_scene2(tab="设计", groups=rib_wpp_design(), h=452,
                         labels=("封面", "目录", "数据", "总结"), active=2,
                         slide_kw=dict(kind="content", title="四、数据支撑", bullets=0,
                                       h=252, w=448))
    # 迷你图表
    cx, cy, cw, ch = 262, by + 92, 264, 136
    f.rect(cx, cy, cw, ch, "#ffffff", K["line2"], 1, 2)
    base = cy + ch - 24
    for i, v in enumerate([58, 72, 40]):
        f.rect(cx + 30 + i * 68, base - v * 1.0, 38, v * 1.0, "#4a7bd6", "none", 0, 0)
    f.line(cx + 20, base, cx + cw - 16, base, "#c8d0dc", 1)
    f.at("chart", cx + 132, cy + 72)
    marks_from(f, [
        ("big:主题", "第 1 步：套主题，统一配色与字体（20 分里的 3 分）", "", (56, 50)),
        ("chart", "第 2 步：按题干插入图表并改数据源", "top", 24),
        ("big:幻灯片母版", "第 3 步：母版加页脚/编号，交卷前「检查文档」", "", (56, 46)),
    ])
    return f


def r_p():
    """第四章开头的成稿版式基准（合格演示文稿的要素）"""
    f = Fig(1000, 448)
    sx, sy, sw = 40, 20, 524
    sh = round(sw * 9 / 16.0)
    shadow(f, sx, sy, sw, sh, 1, 0.12, 2)
    f.rect(sx, sy, sw, sh, "#ffffff", K["line2"], 0.9, 1)
    # 标题
    f.txt(sx + 40, sy + 54, "二、数据看板：三个指标看全年", 17, "#12306b", bold=True)
    f.rect(sx + 40, sy + 66, 96, 3.4, "#1c4ed8", "none", 0, 0)
    f.at("ttl", sx + 40, sy + 44)
    # 一级要点
    bul = ["营业收入 12.47 亿元，同比增长 18.6%",
           "华东、华南两区贡献 57%，是增长主引擎",
           "西南区完成率 58.3%，需重点跟进"]
    cy = sy + 96
    for s in bul:
        f.circle(sx + 44, cy - 4, 2.6, "#1c4ed8")
        f.txt(sx + 56, cy, s, 10.6, "#1f2937")
        cy += 24
    # 二级要点
    f.circle(sx + 52, cy - 4, 2.0, "#7e8ba3")
    f.txt(sx + 64, cy, "同期基数偏低，含一次性大单", 9.6, "#4b5563")
    f.at("sub", sx + 56, cy - 8)
    # 右侧图表占位（柱形 + 折线）
    cx0, cy0, cw0, ch0 = sx + 336, sy + 80, 156, 116
    f.rect(cx0, cy0, cw0, ch0, "#f7f9fc", "#dde4ee", 1, 2)
    base = cy0 + ch0 - 18
    for i, hh in enumerate([38, 52, 66, 46]):
        bx = cx0 + 18 + i * 33
        f.rect(bx, base - hh, 18, hh, "#9db8e8", "#6f92cd", 0.8, 1)
    f.line(cx0 + 8, base, cx0 + cw0 - 8, base, "#b6c0cf", 1)
    f.path("M%.1f %.1f L%.1f %.1f L%.1f %.1f L%.1f %.1f" % (
        cx0 + 27, base - 44, cx0 + 60, base - 58, cx0 + 93, base - 72, cx0 + 126, base - 54),
        "none", "#e8710a", 1.6)
    # 页脚与页码
    f.line(sx + 40, sy + sh - 30, sx + sw - 40, sy + sh - 30, "#d7dee8", 0.9)
    f.txt(sx + 42, sy + sh - 14, "2026 年度经营分析 · 财务部", 8.2, "#6b7683")
    f.txt(sx + sw - 42, sy + sh - 14, "3", 9, "#6b7683", "end")
    f.at("pgno", sx + sw - 42, sy + sh - 18)

    ty2 = spec_table(f, 594, 18, 388, [
        ("结构", "封面 → 目录 → 内容 → 结束，共 8—12 页"),
        ("标题", "母版占位符，黑体 40 pt，一页一观点"),
        ("正文", "24—28 pt，两级以内，一级 3—5 条"),
        ("字号下限", "注释不小于 14 pt，投影也看得清"),
        ("配色", "主色 + 辅色不超过 3 种，与模板一致"),
        ("动画", "同类型统一一个效果，逐项「单击时」"),
        ("页码", "插入 → 幻灯片编号，母版里统一位置"),
    ], title="合格演示稿的要素")
    f.txt(594, ty2 + 16, "评委看的是「一眼看懂」：字少、图大、层级清。", 10, K["txt3"])
    tip(f, 594, ty2 + 30, 388, "一页只讲一件事；讲不完就再拆一页，别把字号缩小硬塞")
    tip(f, 594, ty2 + 62, 388, "交付前按 F5 从头放映一遍，检查切页、动画与字体")

    # 下方：四段式结构缩略图
    f.txt(sx, 340, "结构：封面 → 目录 → 内容 → 结束", 10.5, K["txt2"], bold=True)
    for k, lab in enumerate(["封面", "目录", "内容", "结束"]):
        mx = sx + k * 132
        mw, mh = 118, 72
        f.rect(mx, 348, mw, mh, "#ffffff", K["line2"], 0.9, 1)
        if k == 0:
            f.txt(mx + mw / 2, 374, "标题", 8.6, "#334155", "middle", bold=True)
            f.txt(mx + mw / 2, 390, "副标题 / 汇报人", 6.6, "#6b7683", "middle")
        elif k == 1:
            for i in range(4):
                f.rect(mx + 20, 360 + i * 12, 78, 4, "#dde4ee", "none", 0, 2)
        elif k == 2:
            f.rect(mx + 12, 360, 60, 4.4, "#9db8e8", "none", 0, 2)
            for i in range(3):
                f.rect(mx + 12, 370 + i * 10, 52 - i * 6, 3.6, "#dde4ee", "none", 0, 2)
            f.rect(mx + 78, 366, 28, 30, "#eef3fa", "#c9d5e6", 0.7, 1)
        else:
            f.txt(mx + mw / 2, 388, "谢谢 / 联系方式", 7.4, "#334155", "middle")
        f.txt(mx + mw / 2, 436, lab, 8.6, K["txt3"], "middle")
        if k < 3:
            f.txt(mx + mw + 7, 386, "›", 12, "#9aa6b5", "middle")

    marks_from(f, [
        ("ttl", "标题走母版占位符，不要手动画文本框", "top", 22),
        ("sub", "二级要点小 4 pt，换一种项目符号", "left", 66),
        ("pgno", "页码在母版里设，标题页勾「不显示」", "bottom", 28),
    ])
    return f


REG = {
    "p7_1": p7_1, "p7_2": p7_2, "p7_3": p7_3, "p7_4": p7_4,
    "p8_1": p8_1, "p8_2": p8_2, "p8_3": p8_3, "p8_4": p8_4,
    "r_p": r_p,
}
