# -*- coding: utf-8 -*-
"""scenes_b.py —— 课时 3、4 配套界面示意图"""
from wpsdraw import *          # noqa
from gen_wps_shots import (ui, dialog_scene, page_scene, two_pages, write, tag_svg,
                           W, H, TAB_GROUPS)


def build_l3():
    # 27. 样式组 + 引用选项卡
    o = []
    o.append(app_shell(W, 560, "实训报告 - WPS Office", tab="开始", tabs=[
        "文件", "首页", "开始", "插入", "页面布局", "引用", "审阅", "视图", "会员"]))
    o.append(R(0, 66, W, 130, fill="#FFFFFF", stroke=None, rx=0))
    # 开始选项卡：样式组
    svg, pos, gw = ribbon_group_buttons(24, 80, "样式",
                                         [("H1", "标题1"), ("H2", "标题2"), ("H3", "标题3"),
                                          ("正", "正文"), ("强", "强调"), ("引", "引用")], cols=3)
    o.append(svg)
    o.append(mark(pos["标题1"][0] - 4, pos["标题1"][1] - 4, pos["标题1"][2] + 8, pos["标题1"][3] + 8, 1))
    o.append(mark(pos["标题2"][0] - 4, pos["标题2"][1] - 4, pos["标题2"][2] + 8, pos["标题2"][3] + 8, 2))
    o.append(T(30, 178, "① 一级标题套「标题1」　② 二级标题套「标题2」——目录靠的就是样式",
               size=13, fill=C_TEXT2))
    o.append(L(0, 196, W, 196, stroke=C_DIVIDER))
    # 引用选项卡
    o.append(R(0, 196, W, 118, fill="#FFFFFF", stroke=None, rx=0))
    svg2, pos2, _ = ribbon_group_buttons(24, 208, "目录", [("目", "目录"), ("题", "题注")], cols=2)
    o.append(svg2)
    o.append(mark(pos2["目录"][0] - 4, pos2["目录"][1] - 4, pos2["目录"][2] + 8, pos2["目录"][3] + 8, 3))
    o.append(T(150, 232, "③「引用 → 目录 → 自动目录」：先套样式，才能生成目录", size=13, fill=C_TEXT2))
    o.append(T(150, 258, "④「引用 → 题注」：给表格和图片加「表1」「图1」", size=13, fill=C_TEXT2))
    o.append(L(0, 314, W, 314, stroke=C_DIVIDER))
    # 编辑区
    o.append(R(0, 314, W, 246, fill=C_BG, stroke=None, rx=0))
    o.append(R(60, 330, 1080, 210, fill="#FFFFFF", stroke="#D7DBE0", sw=1, rx=2,
               extra=' filter="url(#sh)"'))
    o.append(T(90, 362, "计算机等级考试实训报告", size=12, weight=700, anchor="middle"))
    o.append(T(90, 392, "一、实训目的", size=10.5, weight=700))
    o.append(T(90, 416, "二、实训内容", size=10.5, weight=700))
    o.append(T(90, 440, "三、实训总结", size=10.5, weight=700))
    o.append(T(60, 300, "示例文档：三个二级标题已套用「标题2」样式，导航窗格可显示层级",
               size=12.5, fill="#6B7A90"))
    o.append(tag_svg(W, 560))
    write("l3-style", svg_doc(W, 560, "".join(o), bg="#FFFFFF"))

    # 28. 样式面板与右键菜单
    o = [R(0, 0, W, 470, fill="#F3F5F8", stroke=None, rx=0)]
    o.append(R(40, 40, 240, 340, fill="#FFFFFF", stroke=C_BORDER, sw=1, rx=6))
    o.append(T(58, 68, "样式", size=13, weight=700, fill=C_TEXT))
    items = [("H1", "标题 1"), ("H2", "标题 2"), ("H3", "标题 3"), ("正", "正文"),
             ("强", "强调"), ("引", "引用")]
    yy = 92
    for g, l in items:
        o.append(T(58, yy + 14, g, size=11.5, weight=700, fill=C_TEXT2))
        o.append(T(88, yy + 14, l, size=12.5, fill=C_TEXT))
        yy += 30
    o.append(R(52, 86, 216, 30, fill="#EAF2FD", stroke=None, rx=4))
    o.append(mark(52, 86, 216, 30, 1))
    mp, _ = menu_panel(300, 96, 210, ["更新 标题1", "修改…", "设为默认", "清除格式", "隐藏"], marked={"修改…": 2})
    o.append(mp)
    o.append(T(300, 60, "在样式上右键 →「修改…」", size=13.5, fill=C_TEXT))
    o.append(T(560, 120, "① 样式面板中的「标题 1」", size=13, fill=C_TEXT2))
    o.append(T(560, 150, "② 右键菜单中的「修改…」", size=13, fill=C_TEXT2))
    o.append(T(560, 196, "修改样式定义 = 一次性改掉全文所有同级段落，", size=13, fill=C_TEXT2))
    o.append(T(560, 222, "比逐段手工调整快得多，也更整齐。", size=13, fill=C_TEXT2))
    o.append(T(560, 262, "注意：不要勾选「添加到模板」", size=12.5, fill=C_HILITE, weight=600))
    o.append(tag_svg(W, 470))
    write("e3-1-style", svg_doc(W, 470, "".join(o), bg="#F3F5F8"))

    # 29. 修改样式对话框
    dialog_scene("e3-1-modify", "修改样式: 标题 1", ["字体", "格式"],
                 [("中文字体", "黑体", "sel"),
                  ("西文字体", "黑体", "sel"),
                  ("字形", "标准", "sel"),
                  ("字号", "小二 (18 磅)", "sel"),
                  ("对齐方式", "居中", "sel"),
                  ("段前", "0.5 行", "text"),
                  ("段后", "0.5 行", "text")],
                 marks={0: 1, 3: 1, 4: 2, 5: 2, 6: 2},
                 active_tab=0,
                 note=["① 字体选项卡：黑体、小二", "② 切到「格式」→ 段落：居中、段前段后 0.5 行",
                       "确定后全文使用「标题 1」的段落同步改变"])

    # 30. 例3-1 效果页（带导航窗格）
    p = Page()
    p.title("计算机等级考试实训报告", size=24, space=16)
    p.h2("一、实训目的", size=17, space=6)
    p.p("本次实训旨在熟悉WPS文字的基本操作，掌握文档排版的规范方法，"
        "为参加国家计算机等级二级考试做好准备。", indent_chars=2, space=8)
    p.h2("二、实训内容", size=17, space=6)
    p.p("实训内容包括文档新建与保存、字符与段落格式设置、样式应用、"
        "表格制作以及图文混排等内容。", indent_chars=2, space=8)
    p.h2("三、实训总结", size=17, space=6)
    p.p("实训过程中发现，格式不统一是最常见的问题，主要原因是逐段手工设置而忽略了样式功能。",
        indent_chars=2, space=10)
    page = p.render()
    o = [R(0, 0, 120 + p.w + 60, p.h + 80, fill="#EEF1F5", stroke=None, rx=0)]
    o.append(R(20, 40, 210, p.h, fill="#FFFFFF", stroke=C_BORDER, sw=1, rx=4))
    o.append(T(36, 70, "导航窗格", size=12.5, weight=700, fill=C_TEXT))
    o.append(T(44, 102, "计算机等级考试实训报告", size=12, weight=700, fill=C_TEXT))
    for i, t in enumerate(["一、实训目的", "二、实训内容", "三、实训总结"]):
        o.append(T(58, 132 + i * 26, t, size=12, fill=C_TEXT2))
    o.append(mark(36, 84, 180, 28, 1))
    o.append('<g transform="translate(250,40)">%s</g>' % page)
    o.append(tag_svg(120 + p.w + 60, p.h + 80))
    write("e3-1-result", svg_doc(120 + p.w + 60, p.h + 80, "".join(o), bg="#EEF1F5"))

    # 31. 例3-2 查找和替换对话框
    CW, CH = 880, 560
    o = [R(0, 0, CW, CH, fill="#F3F5F8", stroke=None, rx=0),
         R(40, 40, 760, 470, fill="#FFFFFF", stroke="#C9CDD4", sw=1, rx=9),
         R(40, 40, 760, 32, fill="#F5F6F8", stroke=None, rx=9),
         R(40, 60, 760, 12, fill="#F5F6F8", stroke=None, rx=0),
         T(56, 61, "查找和替换", size=13, fill=C_TEXT, weight=700),
         T(784, 61, "✕", size=12, fill=C_MUTED, anchor="middle")]
    o.append(T(60, 100, "查找内容", size=12.5, fill=C_TEXT2))
    o.append(field_box(140, 84, 420, 28, "电子商务", "text"))
    o.append(T(60, 138, "替换为", size=12.5, fill=C_TEXT2))
    o.append(field_box(140, 122, 420, 28, "跨境电子商务", "text"))
    for bx, bw_, lbl in [(60, 120, "查找下一处"), (190, 120, "全部替换"), (320, 120, "替换")]:
        o.append(R(bx, 168, bw_, 30, fill="#FFFFFF", stroke=C_INPUT_BD, sw=1, rx=4))
        o.append(T(bx + bw_ / 2, 188, lbl, size=12.5, fill=C_TEXT, anchor="middle"))
    for bx, bw_, lbl in [(60, 120, "格式…"), (190, 150, "特殊字符…"), (350, 120, "更多 >>")]:
        o.append(R(bx, 210, bw_, 30, fill="#FFFFFF", stroke=C_INPUT_BD, sw=1, rx=4))
        o.append(T(bx + bw_ / 2, 230, lbl, size=12.5, fill=C_TEXT, anchor="middle"))
    o.append(mark(136, 80, 428, 74, 1, pos="tr"))
    o.append(mark(346, 206, 128, 38, 3))
    o.append(L(40, 300, 800, 300, stroke=C_DIVIDER))
    o.append(T(60, 326, "搜索选项（点「更多 >>」展开）", size=12, weight=700, fill=C_TEXT2))
    o.append(T(60, 354, "搜索范围", size=12, fill=C_TEXT2))
    o.append(field_box(140, 338, 180, 24, "全部", "sel"))
    o.append(T(360, 354, "使用通配符", size=12, fill=C_TEXT2))
    o.append(field_box(430, 338, 16, 24, "", "chk"))
    o.append(T(456, 354, "查找内容中可用 ? 与 *", size=11.5, fill=C_MUTED))
    o.append(T(60, 386, "特殊字符代码", size=12, fill=C_TEXT2))
    o.append(T(140, 386, "^p 段落标记　^t 制表符　^l 手动换行符　^w 空白区域", size=11.5, fill=C_TEXT2))
    o.append(L(40, 410, 800, 410, stroke=C_DIVIDER))
    o.append(R(600, 420, 74, 28, fill=C_ACTIVE, stroke=None, rx=4))
    o.append(T(637, 439, "关闭", size=12.5, fill="#FFFFFF", weight=600, anchor="middle"))
    o.append(R(686, 420, 54, 28, fill="#FFFFFF", stroke=C_INPUT_BD, sw=1, rx=4))
    o.append(T(713, 439, "取消", size=12.5, fill=C_TEXT, anchor="middle"))
    o.append(T(60, 486, "① 查找内容 / 替换为　②「格式…」设置查找与替换两端的格式　③ 更多 >> 展开通配符与特殊字符",
               size=12.5, fill=C_TEXT2))
    o.append(T(60, 514, "删除多余空行：查找 ^p^p → 替换为 ^p，反复替换直到提示「0 处」",
               size=12.5, fill=C_TEXT2))
    o.append(tag_svg(CW, CH))
    write("e3-2-replace", svg_doc(CW, CH, "".join(o), bg="#F3F5F8"))

    # 32. 例3-2 格式替换
    CW2, CH2 = 880, 520
    o = [R(0, 0, CW2, CH2, fill="#F3F5F8", stroke=None, rx=0),
         R(40, 40, 760, 400, fill="#FFFFFF", stroke="#C9CDD4", sw=1, rx=9),
         R(40, 40, 760, 32, fill="#F5F6F8", stroke=None, rx=9),
         R(40, 60, 760, 12, fill="#F5F6F8", stroke=None, rx=0),
         T(56, 61, "查找和替换", size=13, fill=C_TEXT, weight=700)]
    o.append(T(60, 104, "查找内容", size=12.5, fill=C_TEXT2))
    o.append(field_box(140, 88, 420, 28, "", "text"))
    o.append(T(150, 107, "格式：红色、加粗", size=12, fill="#C0392B", weight=600))
    o.append(mark(136, 84, 428, 36, 1, pos="tr"))
    o.append(T(60, 142, "替换为", size=12.5, fill=C_TEXT2))
    o.append(field_box(140, 126, 420, 28, "", "text"))
    o.append(T(150, 145, "格式：蓝色、不加粗", size=12, fill=C_BLUE, weight=600))
    o.append(mark(136, 122, 428, 36, 2, pos="tr"))
    o.append(R(60, 176, 300, 30, fill="#FFFFFF", stroke=C_INPUT_BD, sw=1, rx=4))
    o.append(T(210, 196, "查找下一处", size=12.5, fill=C_TEXT, anchor="middle"))
    o.append(R(170, 176, 300, 30, fill="#FFFFFF", stroke=C_INPUT_BD, sw=1, rx=4))
    o.append(T(320, 196, "全部替换", size=12.5, fill=C_TEXT, anchor="middle"))
    o.append(mark(166, 172, 308, 38, 3, pos="out"))
    o.append(L(40, 230, 800, 230, stroke=C_DIVIDER))
    o.append(T(60, 258, "格式替换要点", size=12.5, weight=700, fill=C_TEXT))
    for i, t in enumerate(["查找条件与替换条件必须分别设置，只设一端看不出变化",
                           "设完格式后先点「查找下一处」确认命中，再点「全部替换」",
                           "做文本替换前先点「不限定格式」清掉残留的格式条件"]):
        o.append(T(70, 286 + i * 26, "· " + t, size=12.5, fill=C_TEXT2))
    o.append(tag_svg(CW2, CH2))
    write("e3-2-format", svg_doc(CW2, CH2, "".join(o), bg="#F3F5F8"))

    # 33. 例3-2 替换前后对比
    def mkpage(title_text, lines, note_text, note_color):
        p = Page()
        p.title(title_text, size=22, space=14)
        for t, c in lines:
            p.line(t, size=14.5, lh=1.8, space=4, color=c)
        p.spacer(10)
        p.raw(T(p.margin, p.y, note_text, size=13, fill=note_color))
        return p

    p1 = mkpage("替换前", [("电子商务专业实训方案", "#1A1A1A"),
                           ("电子商务已成为区域经济的重要增长点。", "#1A1A1A"),
                           ("跨境电子商务业务量逐年上升。", "#C0392B"),
                           ("跨境电子商务专业方向正式设立。", "#C0392B")],
                "直接替换会出现「跨境跨境电子商务」", "#C0392B")
    p2 = mkpage("替换后", [("跨境电子商务专业实训方案", "#1A1A1A"),
                           ("跨境电子商务已成为区域经济的重要增长点。", "#1A1A1A"),
                           ("跨境电子商务业务量逐年上升。", "#1A1A1A"),
                           ("跨境电子商务专业方向正式设立。", "#1A1A1A")],
                "占位符两遍替换：@@ → 跨境电子商务", "#16A34A")
    two_pages("e3-2-result", p1, p2, "直接替换：出现「跨境跨境」", "占位符替换：结果正确")

    # 34. 例3-3 分栏对话框
    dialog_scene("e3-3-cols", "分栏", None,
                 [("栏数", "两栏", "sel"),
                  ("分隔线", "有（实线）", "sel"),
                  ("宽度", "6.9 厘米", "text"),
                  ("栏间距", "1 厘米", "text"),
                  ("应用于", "所选文字", "sel")],
                 marks={0: 1, 1: 2, 3: 2, 4: 3},
                 note=["① 预设选「两栏」", "② 勾选分隔线，栏间距 1 厘米",
                       "③「应用于」必须是「所选文字」，否则整篇都会变两栏"])

    # 35. 例3-3 效果
    p = Page()
    p.h2("二、实训内容", size=17, space=8)
    top = p.y
    colw = 278
    lx, rx = p.margin, p.margin + colw + 34
    left = "实训内容包括文档新建与保存、字符与段落格式设置、样式应用、表格制作与图文混排等内容。"
    right = "每一项内容均配有课堂练习，练习结束后由教师逐台检查并当场点评；建议先套用样式再微调。"
    ls_ = wrap_text(left, 13, colw)
    rs_ = wrap_text(right, 13, colw)
    # 左栏首字下沉
    first = ls_[0][0]
    rest = ls_[0][1:]
    p.add(T(lx, top + 20, first, size=32, fill="#1A1A1A", weight=700))
    p.add(T(lx + 38, top, rest, size=13, fill="#1A1A1A"))
    for i, tline in enumerate(ls_[1:]):
        p.add(T(lx, top + 30 + i * 24, tline, size=13, fill="#1A1A1A"))
    for i, tline in enumerate(rs_):
        p.add(T(rx, top + i * 24, tline, size=13, fill="#1A1A1A"))
    p.add(L(p.margin + colw + 17, top - 18, p.margin + colw + 17, top + 62, stroke="#9AA0A6", sw=1.2))
    p.y = top + 78
    p.spacer(8)
    p.raw(T(p.margin, p.y, "两栏 + 分隔线 + 栏间距 1 厘米；左栏首字下沉 2 行", size=13, fill="#C0392B"))
    p.y += 26
    page_scene("e3-3-result", p, "分栏排版效果（第一段首字下沉）")

    # 36. 例3-4 自定义水印
    dialog_scene("e3-4-watermark", "自定义水印", None,
                 [("水印类型", "文字水印", "sel"),
                  ("文字", "内部资料 请勿外传", "text"),
                  ("字体", "宋体", "sel"),
                  ("字号", "36 磅", "text"),
                  ("颜色", "浅灰 RGB(192,192,192)", "text"),
                  ("半透明", "勾选", "chk")],
                 marks={1: 1, 3: 2, 5: 3},
                 note=["① 水印文字与字号按题目要求填写", "② 颜色选浅灰，避免遮挡正文",
                       "③ 勾选半透明；删除水印用「水印 → 删除水印」"])

    # 37. 例3-4 页面边框
    dialog_scene("e3-4-border", "页面边框", ["边框", "底纹"],
                 [("设置", "方框", "sel"),
                  ("线型", "双线", "sel"),
                  ("宽度", "1.5 磅", "sel"),
                  ("应用于", "整篇文档", "sel"),
                  ("颜色", "自动", "sel")],
                 marks={0: 1, 1: 2, 2: 2, 3: 3},
                 active_tab=0,
                 note=["① 设置选「方框」", "② 线型选双线、宽度 1.5 磅", "③ 「应用于」选整篇文档"])

    # 38. 例3-4 效果
    p = Page()
    p.set_watermark("内部资料 请勿外传", size=42, color="#C4CAD1", opacity=0.75, rot=-26)
    p.set_bg("#DDEBF7")
    p.set_page_border(sw=1.5, double=True, color="#9AA0A6")
    p.title("计算机等级考试实训报告", size=24, space=18)
    p.p("本文档为校内教学辅助材料，页面已加文字水印、双线页面边框与浅蓝页面颜色。",
        indent_chars=2, space=8)
    p.p("水印位于正文之后、页面背景之上，不影响文字阅读与打印。", indent_chars=2, space=16)
    p.raw(T(p.margin, p.y, "浅蓝底 RGB(221,235,247)｜双线页框 1.5 磅｜水印半透明", size=13, fill="#5A6169"))
    p.y += 24
    page_scene("e3-4-result", p, "水印 + 页面边框 + 页面颜色 同时呈现")


def build_l4():
    # 39. 插入选项卡
    ui("l4-insert", "插入", TAB_GROUPS["插入"],
       [(1, "表格", 1), (1, "图片", 2), (0, "页码", 3), (2, "文本框", 4), (3, "题注", 5)],
       doc={"title": "报名通知", "lines": [{"w": 150, "c": "#9AA0A6"}, {"w": 240, "c": "#C8CDD3"},
                                            {"w": 220, "c": "#C8CDD3"}]},
       note=["① 表格　② 图片　③ 页码　④ 文本框　⑤ 题注（表格/图片的编号）"])

    # 40. 分隔符下拉
    o = [R(0, 0, W, 400, fill="#F3F5F8", stroke=None, rx=0)]
    mp, _ = menu_panel(70, 50, 240,
                       ["分页符", "分栏符", "下一页分节符", "连续分节符", "偶数页分节符", "奇数页分节符"],
                       marked={"下一页分节符": 1}, title="分隔符", rowh=32)
    o.append(mp)
    o.append(T(350, 90, "①「页面布局 → 分隔符 → 分节符·下一页」", size=14, fill=C_TEXT))
    o.append(T(350, 122, "用分节符才能让封面与正文分别设置页眉、页脚和页码。", size=13, fill=C_TEXT2))
    o.append(T(350, 150, "用连续回车把正文顶到下一页 → 没有分节，页码无法独立设置。", size=13, fill="#C0392B"))
    o.append(T(350, 200, "插入后打开段落标记，可看到一条「分节符（下一页）」双虚线。", size=13, fill=C_TEXT2))
    o.append(tag_svg(W, 400))
    write("e4-1-section", svg_doc(W, 400, "".join(o), bg="#F3F5F8"))

    # 41. 页眉页脚编辑界面
    o = [app_shell(W, 560, "实训报告 - WPS Office", tab="插入", tabs=[
        "文件", "首页", "开始", "插入", "页面布局", "引用", "审阅", "视图", "会员"])]
    o.append(R(0, 66, W, 46, fill="#F0F6FF", stroke=None, rx=0))
    for i, (g, lbl) in enumerate([("眉", "页眉"), ("脚", "页脚"), ("页", "页码"), ("上", "上页"),
                                  ("下", "下一页"), ("同", "同前节"), ("首", "首页不同"), ("关", "关闭页眉和页脚")]):
        bx = 20 + i * 118
        o.append(R(bx, 72, 30, 26, fill="#FFFFFF", stroke="#C9CDD4", sw=1, rx=5))
        o.append(T(bx + 15, 90, g, size=12, fill=C_TEXT, weight=600, anchor="middle"))
        o.append(T(bx + 15, 108, lbl, size=10, fill=C_TEXT2, anchor="middle"))
    o.append(mark(20 + 5 * 118 - 4, 68, 38, 34, 1))
    o.append(mark(20 + 2 * 118 - 4, 68, 38, 34, 2))
    o.append(L(0, 112, W, 112, stroke=C_DIVIDER))
    o.append(R(0, 112, W, 448, fill=C_BG, stroke=None, rx=0))
    o.append(R(120, 130, 420, 400, fill="#FFFFFF", stroke="#D7DBE0", sw=1, rx=2,
               extra=' filter="url(#sh)"'))
    o.append(T(140, 168, "页眉区（双击进入编辑）", size=12, fill="#9AA0A6"))
    o.append(R(140, 178, 380, 30, fill="none", stroke="#7BA7DE", sw=1.2, rx=0,
               extra=' stroke-dasharray="6 4"'))
    o.append(T(140, 210, "大数据管理与应用专业 实训报告", size=13, fill="#1A1A1A", anchor="middle"))
    o.append(L(150, 222, 510, 222, stroke="#1A1A1A", sw=1))
    for i in range(9):
        o.append(R(140, 244 + i * 18, 370 - (i % 3) * 40, 6, fill="#C8CDD3", rx=3))
    o.append(R(120, 470, 420, 46, fill="#FFFFFF", stroke="#D7DBE0", sw=1, rx=2))
    o.append(R(130, 478, 400, 30, fill="none", stroke="#7BA7DE", sw=1.2, rx=0,
               extra=' stroke-dasharray="6 4"'))
    o.append(T(330, 498, "第 1 页 共 3 页", size=13, fill="#1A1A1A", anchor="middle"))
    o.append(T(580, 180, "①「同前节」必须点掉", size=14, fill=C_TEXT, weight=700))
    o.append(T(580, 212, "处于按下状态时，正文页眉与封面共用一份，", size=13, fill=C_TEXT2))
    o.append(T(580, 238, "删封面页码会把正文页码一起删掉。", size=13, fill=C_TEXT2))
    o.append(T(580, 278, "②「页码」按钮插入页码与「第 X 页 共 Y 页」", size=14, fill=C_TEXT, weight=700))
    o.append(tag_svg(W, 560))
    write("e4-1-header", svg_doc(W, 560, "".join(o), bg="#FFFFFF"))

    # 42. 设置页码格式
    dialog_scene("e4-1-pageno", "设置页码格式", None,
                 [("起始页码", "1", "text"),
                  ("数字格式", "1, 2, 3, ...", "sel"),
                  ("页码位置", "页脚", "sel"),
                  ("对齐方式", "居中", "sel"),
                  ("包含章节号", "不包含", "sel")],
                 marks={0: 1, 2: 2, 3: 2},
                 note=["① 起始页码设为 1：正文从 1 开始编号",
                       "② 页码位置与对齐方式按题目要求选择"])

    # 43. 例4-1 封面 + 正文
    cover = Page()
    cover.spacer(180)
    cover.title("计算机等级考试实训报告", size=30, space=40)
    cover.title("大数据管理与应用专业 2026级", size=18, weight=400, space=90)
    cover.title("姓名：×××　学号：×××", size=16, weight=400, space=20)
    body = Page()
    body.set_header("大数据管理与应用专业 实训报告", rule=True)
    body.set_footer("第 1 页 共 3 页")
    body.h2("一、实训目的", size=17, space=8)
    body.p("本次实训旨在熟悉WPS文字的基本操作，掌握长文档的排版规范，"
           "包括分节、页眉页脚、页码与目录的用法。", indent_chars=2, space=8)
    body.h2("二、实训内容", size=17, space=8)
    body.p("实训内容包括分节符的插入、页眉页脚的分节设置、页码起始值的调整"
           "以及自动目录的生成与更新。", indent_chars=2, space=8)
    two_pages("e4-1-result", cover, body,
              "封面（第 1 节）：无页眉、无页脚、无页码",
              "正文（第 2 节）：页眉带下框线，页脚页码从 1 开始")

    # 44. 插入表格对话框
    dialog_scene("e4-2-insert", "插入表格", None,
                 [("列数", "4", "text"),
                  ("行数", "5", "text"),
                  ("首行为标题行", "勾选", "chk"),
                  ("自动套用表格样式", "无", "sel"),
                  ("对齐方式", "居中", "sel")],
                 marks={0: 1, 1: 1, 2: 2, 4: 3},
                 note=["① 列数 4、行数 5", "② 勾选「首行为标题行」，第 2 页自动重复表头",
                       "③ 对齐方式选居中，表格整体居中"])

    # 45. 表格属性对话框
    dialog_scene("e4-2-prop", "表格属性", ["表格", "列", "行"],
                 [("首选宽度", "（自动）", "text"),
                  ("对齐方式", "居中", "sel"),
                  ("文字环绕", "无", "sel"),
                  ("第 1 列宽度", "1.5 厘米", "text"),
                  ("第 2 列宽度", "4 厘米", "text"),
                  ("第 3 列宽度", "3 厘米", "text"),
                  ("第 4 列宽度", "3 厘米", "text")],
                 marks={1: 1, 3: 2, 4: 2, 5: 2, 6: 2},
                 active_tab=1,
                 note=["①「表格」选项卡：整表居中、文字环绕选「无」",
                       "②「列」选项卡：逐列填写宽度，先设「自动调整 → 固定列宽」再改数值"])

    # 46. 成绩表
    p = Page()
    p.line("表1 学生成绩表", size=13, align="center", space=14)
    p.table(["序号", "姓名", "平时成绩", "总评"],
            [["1", "王思远", "88", "优"], ["2", "李明轩", "92", "优"],
             ["3", "张雨欣", "79", "良"], ["4", "陈子豪", "85", "良"]],
            [70, 150, 130, 130], head_bg="#EFEFEF")
    p.spacer(18)
    p.raw(T(p.margin, p.y, "表头浅灰底纹 + 加粗居中；全表所有框线；列宽 1.5 / 4 / 3 / 3 厘米",
            size=13, fill="#C0392B"))
    p.y += 24
    page_scene("e4-2-result", p, "表格成品：4 列 5 行，表头底纹、框线、居中")

    # 47. 图片环绕菜单
    o = [R(0, 0, W, 420, fill="#F3F5F8", stroke=None, rx=0)]
    mp, _ = menu_panel(60, 46, 220,
                       ["嵌入型", "四周型环绕", "紧密型环绕", "衬于文字下方", "浮于文字上方", "上下型环绕"],
                       marked={"四周型环绕": 1}, title="环绕文字", rowh=30)
    o.append(mp)
    o.append(T(330, 80, "① 图片工具 → 环绕 → 四周型环绕", size=14, fill=C_TEXT))
    o.append(T(330, 112, "默认的「嵌入型」图片无法自由拖动，", size=13, fill=C_TEXT2))
    o.append(T(330, 138, "必须先改成浮动方式。", size=13, fill=C_TEXT2))
    o.append(T(330, 180, "②「图片工具 → 大小」中把宽度改为 7 厘米", size=14, fill=C_TEXT))
    o.append(T(330, 212, "③「图片工具 → 对齐 → 水平居中」（相对于页边距）", size=14, fill=C_TEXT))
    o.append(T(330, 244, "④「图片工具 → 图片边框」：颜色橙色、粗细 1 磅", size=14, fill=C_TEXT))
    o.append(T(60, 350, "⑤ 图片下方加图注：「引用 → 题注 → 新建标签『图』→ 所选项目下方」", size=13.5, fill=C_TEXT2))
    o.append(tag_svg(W, 420))
    write("e4-3-wrap", svg_doc(W, 420, "".join(o), bg="#F3F5F8"))

    # 48. 图片环绕效果
    p = Page()
    p.h2("二、实训内容", size=17, space=6)
    p.p("实训内容包括分节符的插入、页眉页脚的分节设置以及自动目录的生成与更新。"
        "下图为实训机房实景。", indent_chars=2, space=10)
    p.img_block(300, 200, caption="图1 实训机房")
    p.raw(T(p.margin, p.y, "图片宽 7 厘米、四周型环绕、居中，1 磅橙色边框，下方为图注",
            size=13, fill="#C0392B"))
    p.y += 24
    page_scene("e4-3-result", p, "图片四周型环绕 + 居中 + 图注")

    # 49. 自动目录对话框与目录效果
    CW3, CH3 = 840, 500
    o = [R(0, 0, CW3, CH3, fill="#F3F5F8", stroke=None, rx=0),
         R(40, 40, 700, 400, fill="#FFFFFF", stroke="#C9CDD4", sw=1, rx=9),
         R(40, 40, 700, 32, fill="#F5F6F8", stroke=None, rx=9),
         R(40, 60, 700, 12, fill="#F5F6F8", stroke=None, rx=0),
         T(56, 61, "目录", size=13, fill=C_TEXT, weight=700)]
    o.append(T(60, 100, "目录样式", size=12.5, fill=C_TEXT2))
    o.append(field_box(140, 84, 220, 26, "目录 1", "sel"))
    o.append(T(60, 138, "显示级别", size=12.5, fill=C_TEXT2))
    o.append(field_box(140, 122, 80, 26, "3", "text"))
    o.append(R(60, 164, 300, 30, fill="#FFFFFF", stroke=C_INPUT_BD, sw=1, rx=4))
    o.append(T(210, 184, "确定", size=12.5, fill=C_TEXT, anchor="middle"))
    o.append(R(170, 164, 300, 30, fill="#FFFFFF", stroke=C_INPUT_BD, sw=1, rx=4))
    o.append(T(320, 184, "取消", size=12.5, fill=C_TEXT, anchor="middle"))
    o.append(mark(136, 80, 228, 74, 1, pos="tr"))
    o.append(L(40, 216, 740, 216, stroke=C_DIVIDER))
    for i, t in enumerate(["目录", "一、实训目的 ............................ 2",
                           "二、实训内容 ............................ 3",
                           "三、实训总结 ............................ 4"]):
        o.append(T(70, 254 + i * 30, t, size=13.5, fill="#1A1A1A", weight=700 if i == 0 else 400))
    o.append(T(70, 392, "生成后若页码有变：点「更新目录 → 更新整个目录」，或 Ctrl+A 后按 F9",
               size=12.5, fill="#C0392B"))
    o.append(tag_svg(CW3, CH3))
    write("e4-4-toc", svg_doc(CW3, CH3, "".join(o), bg="#F3F5F8"))

    # 50. 目录页
    p = Page()
    p.title("目　录", size=26, space=30)
    p.toc([("一、报考对象", "2"), ("二、报名流程", "3"), ("三、时间安排", "4"),
           ("四、注意事项", "5")], size=15, gap=30)
    p.spacer(24)
    p.raw(T(p.margin, p.y, "目录由「标题1 / 标题2」样式自动生成，可点击跳转", size=13, fill="#C0392B"))
    p.y += 24
    page_scene("e4-4-tocpage", p, "自动目录：单独占一页，页码与正文对应")

    # 51. 综合成品页
    p = Page()
    p.set_header("管理学院 考试报名通知", rule=False)
    p.set_footer("第 2 页", align="center")
    p.title("关于2026年秋季学期计算机等级考试报名的通知", size=22, space=16)
    p.h2("一、报考对象", size=16, space=6)
    p.p("全体在校本科生，尤其是大数据管理与应用、电子商务、物流管理等专业2026级学生。",
        indent_chars=2, space=8)
    p.h2("二、报名流程", size=16, space=6)
    for i, t in enumerate(["登录中国教育考试网注册账号", "选择考点与考试科目",
                           "上传照片并在线缴费", "打印准考证"]):
        p.numbered(i + 1, t, size=14, space=2)
    p.spacer(8)
    p.h2("三、时间安排", size=16, space=6)
    p.table(["阶段", "时间", "说明"],
            [["报名", "9月1日—9月15日", "中国教育考试网在线报名"],
             ["考试", "9月26日—9月28日", "实训楼A座三楼机房"]],
            [90, 170, 210], head_bg="#EFEFEF", size=13, hrow=28, brow=25)
    p.spacer(10)
    p.h2("四、注意事项", size=16, space=6)
    for t in ["照片须为近期免冠证件照，背景为白色或浅蓝色",
              "缴费后请保留支付凭证截图", "报名截止后不再接受补报"]:
        p.bullet(t, size=14, space=2)
    page_scene("e4-4-doc", p, "综合大题成品：标题样式 + 编号 + 表格 + 页眉页脚")
