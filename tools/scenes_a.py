# -*- coding: utf-8 -*-
"""scenes_a.py —— 课时 1、2 配套界面示意图"""
from wpsdraw import *          # noqa
from gen_wps_shots import (ui, ui_file, dialog_scene, page_scene, two_pages,
                           file_backstage, write, tag_svg, W, H, TAB_GROUPS)


def file_list_panel(x, y, w, h, folders, active=0, files=None):
    o = [R(x, y, w, h, fill="#FFFFFF", stroke=C_BORDER, sw=1, rx=0)]
    o.append(T(x + 14, y + 24, "文件夹", size=12, fill=C_TEXT2, weight=700))
    yy = y + 44
    for i, f in enumerate(folders):
        if i == active:
            o.append(R(x + 6, yy - 14, w - 12, 26, fill="#EAF2FD", stroke=None, rx=4))
        o.append(T(x + 20, yy, "📁" if False else "▣", size=12, fill="#7A8089"))
        o.append(T(x + 40, yy, f, size=12, fill=C_TEXT if i == active else C_TEXT2))
        yy += 26
    if files:
        o.append(T(x + 14, yy + 14, "文件", size=12, fill=C_TEXT2, weight=700))
        yy += 34
        for f in files:
            o.append(T(x + 20, yy, "▤", size=12, fill="#7A8089"))
            o.append(T(x + 40, yy, f, size=12, fill=C_TEXT2))
            yy += 24
    return "".join(o)


# ============================== 课时 1 ==============================
def build_l1():
    # 1. 文件菜单（新建 / 另存为 / 输出 PDF / 文档加密）
    ui_file("l1-file",
            ["新建", "打开", "最近使用", "保存", "另存为", "输出为PDF", "文档加密", "打印", "关闭"],
            {"新建": 1, "另存为": 2, "输出为PDF": 3, "文档加密": 4})

    # 2. 新建后的开始选项卡：插入点与段落标记
    ui("l1-new", "开始", TAB_GROUPS["开始"],
       [(4, "显示/隐藏", 1)],
       doc={"title": "我的第一个WPS文档", "lines": [{"w": 150, "c": "#9AA0A6"},
                                                  {"w": 250, "c": "#C8CDD3"},
                                                  {"w": 230, "c": "#C8CDD3"}],
            "cursor": 6},
       note=["插入点：闪烁的竖线，文字从这里输入",
             "①「显示/隐藏段落标记」：看清 Enter 与 Shift+Enter 的区别",
             "行首 2 格 = 缩进标记，不是空格"])

    # 3. 例1-1 「另存为」对话框
    DW, DH = 900, 620
    o = [R(0, 0, DW, DH, fill="#F3F5F8", stroke=None, rx=0)]
    ox, oy, ow, oh = 40, 30, 820, 470
    o.append(R(ox + 4, oy + 5, ow, oh, fill="#1F2329", stroke=None, rx=9, opacity=0.12))
    o.append(R(ox, oy, ow, oh, fill="#FFFFFF", stroke="#C9CDD4", sw=1, rx=9))
    o.append(R(ox, oy, ow, 34, fill="#F5F6F8", stroke=None, rx=9))
    o.append(R(ox, oy + 22, ow, 12, fill="#F5F6F8", stroke=None, rx=0))
    o.append(T(ox + 16, oy + 22, "另存为", size=13, fill=C_TEXT, weight=700))
    o.append(T(ox + ow - 18, oy + 22, "✕", size=12, fill=C_MUTED, anchor="middle"))
    o.append(L(ox, oy + 34, ox + ow, oy + 34, stroke=C_DIVIDER))
    # 左侧目录
    o.append(R(ox + 1, oy + 35, 200, oh - 35, fill="#FAFAFB", stroke=None, rx=0))
    o.append(L(ox + 201, oy + 35, ox + 201, oy + oh, stroke=C_DIVIDER))
    o.append(T(ox + 18, oy + 62, "位置", size=12.5, fill=C_TEXT2, weight=700))
    tree = ["此电脑", "桌面", "二级WPS练习", "课时1"]
    for i, t in enumerate(tree):
        ty = oy + 92 + i * 32
        if i == 3:
            o.append(R(ox + 8, ty - 20, 186, 28, fill="#EAF2FD", stroke=None, rx=5))
        o.append(T(ox + 24 + i * 12, ty, t, size=12.5, fill=C_TEXT if i == 3 else C_TEXT2,
                   weight=700 if i == 3 else 400))
    o.append(mark(ox + 8, oy + 76, 186, 120, 3))
    # 右侧文件区
    o.append(T(ox + 222, oy + 62, "二级WPS练习 \\ 课时1", size=12.5, fill=C_TEXT2))
    for i, f in enumerate(["练习1-3.docx", "练习1-4.docx"]):
        o.append(T(ox + 226, oy + 96 + i * 30, "▤", size=13, fill="#7A8089"))
        o.append(T(ox + 248, oy + 96 + i * 30, f, size=12.5, fill=C_TEXT2))
    # 底部表单
    o.append(L(ox, oy + oh - 128, ox + ow, oy + oh - 128, stroke=C_DIVIDER))
    o.append(T(ox + 22, oy + oh - 96, "文件名", size=12.5, fill=C_TEXT2))
    o.append(field_box(ox + 92, oy + oh - 110, 430, 28, "学号-姓名-练习1-1", "text"))
    o.append(mark(ox + 88, oy + oh - 114, 438, 36, 1, pos="tr"))
    o.append(T(ox + 22, oy + oh - 56, "保存类型", size=12.5, fill=C_TEXT2))
    o.append(field_box(ox + 92, oy + oh - 70, 250, 28, "Word 文件(*.docx)", "sel"))
    o.append(mark(ox + 88, oy + oh - 74, 258, 36, 2, pos="tr"))
    o.append(T(ox + 372, oy + oh - 56, "编码", size=12.5, fill=C_TEXT2))
    o.append(field_box(ox + 422, oy + oh - 70, 130, 28, "UTF-8", "sel"))
    o.append(R(ox + ow - 190, oy + oh - 62, 80, 32, fill=C_ACTIVE, stroke=None, rx=4))
    o.append(T(ox + ow - 150, oy + oh - 40, "保存", size=13, fill="#FFFFFF", weight=600, anchor="middle"))
    o.append(R(ox + ow - 100, oy + oh - 62, 80, 32, fill="#FFFFFF", stroke=C_INPUT_BD, sw=1, rx=4))
    o.append(T(ox + ow - 60, oy + oh - 40, "取消", size=13, fill=C_TEXT, anchor="middle"))
    for i, line in enumerate(["① 文件名：与题目要求一字不差（含学号、姓名、下划线）",
                              "② 保存类型：Word 文件(*.docx)，不要选成 .wps 或 PDF",
                              "③ 保存位置：必须是题目指定文件夹，考场存错位置等于白做"]):
        o.append(T(60, DH - 90 + i * 24, line, size=13, fill=C_TEXT2))
    o.append(tag_svg(DW, DH))
    write("e1-1-save", svg_doc(DW, DH, "".join(o), bg="#F3F5F8"))

    # 4. 例1-1 完成效果
    p = Page()
    p.title("我的第一个WPS文档", size=26, weight=700, space=18)
    p.p("国家计算机二级考试（WPS Office）由上机操作题和单项选择题组成。"
        "其中，文字处理操作题占30分，是本课程训练的重点。今天我们从新建文档开始。")
    p.spacer(20)
    p.raw(T(p.margin, p.y, "标题与正文之间按了一次 Enter，形成两个独立段落", size=13, fill="#C0392B"))
    p.y += 24
    page_scene("e1-1-result", p, "保存后的文档：标题独占一段，正文另起一段")

    # 5. 例1-2 插入符号对话框
    syms = ["©", "®", "§", "¥", "℃", "±", "×", "÷", "°", "′", "″", "№",
            "☆", "★", "●", "○", "■", "□", "△", "◇", "√", "∞", "≠", "≈"]
    SW, SH = 820, 620
    o = [R(0, 0, SW, SH, fill="#F3F5F8", stroke=None, rx=0),
         R(40, 40, 700, 430, fill="#FFFFFF", stroke="#C9CDD4", sw=1, rx=9),
         R(40, 40, 700, 32, fill="#F5F6F8", stroke=None, rx=9),
         R(40, 60, 700, 12, fill="#F5F6F8", stroke=None, rx=0),
         T(56, 61, "符号", size=13, fill=C_TEXT, weight=700),
         T(724, 61, "✕", size=12, fill=C_MUTED, anchor="middle")]
    o.append(field_box(60, 90, 200, 26, "普通文本", "sel"))
    o.append(T(276, 108, "字体", size=12, fill=C_TEXT2))
    o.append(field_box(320, 90, 200, 26, "类似字母的符号", "sel"))
    o.append(T(536, 108, "子集", size=12, fill=C_TEXT2))
    for i, s in enumerate(syms):
        cx = 70 + (i % 12) * 55
        cy = 135 + (i // 12) * 46
        o.append(R(cx, cy, 44, 36, fill="#FFFFFF", stroke=C_DIVIDER, sw=1, rx=3))
        o.append(T(cx + 22, cy + 25, s, size=17, fill=C_TEXT, anchor="middle"))
    o.append(mark(70 + 4 * 55, 135, 44, 36, 1))
    o.append(mark(70 + 3 * 55, 135, 44, 36, 2))
    o.append(mark(70 + 0 * 55, 135, 44, 36, 3))
    o.append(mark(70 + 1 * 55, 135, 44, 36, 4))
    o.append(R(40, 400, 700, 40, fill="#FFFFFF", stroke=None, rx=0))
    o.append(L(40, 400, 740, 400, stroke=C_DIVIDER))
    o.append(R(600, 406, 74, 28, fill=C_ACTIVE, stroke=None, rx=4))
    o.append(T(637, 425, "插入", size=12.5, fill="#FFFFFF", weight=600, anchor="middle"))
    o.append(R(686, 406, 44, 28, fill="#FFFFFF", stroke=C_INPUT_BD, sw=1, rx=4))
    o.append(T(708, 425, "取消", size=12.5, fill=C_TEXT, anchor="middle"))
    o.append(T(60, 520, "① ℃ 摄氏度    ② ¥ 人民币    ③ © 版权符号    ④ ® 注册商标", size=13.5, fill=C_TEXT2))
    o.append(T(60, 548, "「插入 → 符号 → 其他符号」，在字符表中找到符号后双击即可插入", size=13, fill=C_MUTED))
    o.append(tag_svg(SW, SH))
    write("e1-2-symbol", svg_doc(SW, SH, "".join(o), bg="#F3F5F8"))

    # 6. 例1-2 上标/下标按钮
    ui("e1-2-supsub", "开始", TAB_GROUPS["开始"],
       [(1, "上标", 1), (1, "下标", 2)],
       doc={"title": "字符格式", "lines": [{"w": 120, "c": "#9AA0A6"}, {"w": 200, "c": "#C8CDD3"},
                                           {"w": 180, "c": "#C8CDD3"}]},
       note=["① 上标 X²：m2 → m²　快捷键 Ctrl+Shift+=",
             "② 下标 X₂：H2O → H₂O　快捷键 Ctrl+=",
             "选中数字后再点按钮；不能改字号冒充上下标"])

    # 7. 例1-2 完成效果
    p = Page()
    p.line("温度为25℃，湿度60%，面积120m²，水的化学式H₂O。", size=15.3, lh=1.9, space=10)
    p.line("版权符号©，注册商标®，章节符号§，人民币¥1000。", size=15.3, lh=1.9, space=10)
    p.line("英文句子：WPS Office is easy to use.", size=15.3, lh=1.9, space=10)
    p.line("全角括号（示例）与半角括号(示例)的区别。", size=15.3, lh=1.9, space=16)
    p.raw(T(p.margin, p.y, "℃ 由「插入 → 符号」插入；m²、H₂O 使用真正的上标 / 下标格式",
            size=13, fill="#C0392B"))
    p.y += 24
    page_scene("e1-2-result", p, "录入结果：符号用插入，上下标用格式，不用改字号冒充")

    # 8. 例1-3 三种选定方式
    o = [R(0, 0, W, 430, fill="#F3F5F8", stroke=None, rx=0)]
    titles = [("双击：选中一个词（连续汉字）", 1, 60), ("三击：选中整段（含段末 ¶）", 2, 420),
              ("Shift+单击：选中两点之间的内容", 3, 780)]
    for t, n, x in titles:
        o.append(T(x, 42, t, size=14, fill=C_TEXT, weight=700))
        o.append(R(x, 58, 330, 250, fill="#FFFFFF", stroke="#D7DBE0", sw=1, rx=2,
                   extra=' filter="url(#sh)"'))
        o.append(T(x + 20, 96, "成绩查询：考试结束后", size=14, fill="#5A6169"))
        o.append(T(x + 20, 132, "30个工作日公布。", size=14, fill="#5A6169"))
        o.append(T(x + 20, 186, "报名时间：9月1日至9月15日。", size=14, fill="#5A6169"))
        o.append(T(x + 20, 222, "考试时间：9月26日至9月28日。", size=14, fill="#5A6169"))
        o.append(CIRC(x + 30, 244, 11, fill=C_HILITE))
        o.append(T(x + 30, 248, str(n), size=11, fill="#FFFFFF", weight=800, anchor="middle"))
    o.append(R(78, 84, 96, 22, fill="#CFE0F7", stroke="#7BA7DE", sw=0.8, rx=2))
    o.append(R(438, 78, 262, 68, fill="#CFE0F7", stroke="#7BA7DE", sw=0.8, rx=2))
    o.append(R(798, 178, 200, 58, fill="#CFE0F7", stroke="#7BA7DE", sw=0.8, rx=2))
    o.append(T(40, 380, "双击选词用于替换单个词；三击选段用于整段移动；Shift 拖选用于精确框选。",
               size=13.5, fill=C_TEXT2))
    o.append(tag_svg(W, 430))
    write("e1-3-select", svg_doc(W, 430, "".join(o), bg="#F3F5F8"))

    # 9. 例1-3 移动段落后的效果
    p = Page()
    p.p("成绩查询：考试结束后约30个工作日公布。", indent_chars=2, space=8)
    p.p("报名时间：2026年9月1日至9月15日。", indent_chars=2, space=8)
    p.p("考试时间：2026年9月26日至9月28日。", indent_chars=2, space=14)
    p.raw(T(p.margin, p.y, "剪切时连同段末 ¶ 一起选中，粘贴后仍为三个独立段落", size=13, fill="#C0392B"))
    p.y += 24
    page_scene("e1-3-result", p, "第 3 段整体移到最前：段落顺序 3 → 1 → 2")

    # 10. 例1-4 页面设置对话框
    dialog_scene("e1-4-page", "页面设置", ["纸张", "页边距", "版式", "文档网格"],
                 [("纸张", "A4", "sel"),
                  ("方向", "纵向", "sel"),
                  ("上边距", "2.54 厘米", "text"),
                  ("下边距", "2.54 厘米", "text"),
                  ("左边距", "3.17 厘米", "text"),
                  ("右边距", "3.17 厘米", "text"),
                  ("应用于", "整篇文档", "sel")],
                 marks={2: 1, 3: 1, 4: 2, 5: 2, 6: 3},
                 active_tab=1,
                 note=["①② 四个边距数值直接填写，单位保持「厘米」",
                       "③「应用于」必须选整篇文档；多节文档选「本节」会漏改"])

    # 11. 例1-4 页面布局选项卡
    ui("e1-4-layout", "页面布局", TAB_GROUPS["页面布局"],
       [(0, "纸张大小", 1), (0, "页边距", 2), (1, "水印", 3), (1, "页面边框", 4)],
       doc={"title": "页面设置", "lines": [{"w": 160, "c": "#9AA0A6"}, {"w": 240, "c": "#C8CDD3"},
                                           {"w": 210, "c": "#C8CDD3"}]},
       note=["① 纸张大小 → A4", "② 页边距 → 自定义页边距", "③ 水印", "④ 页面边框"])

    # 12. 例1-4 文档加密对话框
    dialog_scene("e1-4-encrypt", "文档加密", None,
                 [("打开权限密码", "••••••", "text"),
                  ("密码保护类型", "密码加密（打开文档需密码）", "sel"),
                  ("修改权限密码", "（留空表示允许直接编辑）", "text")],
                 marks={0: 1, 1: 2},
                 note=["① 打开权限密码：打开文档时校验", "② 加密后必须保存才生效",
                       "交卷前记得把密码清空，否则文件打不开"])

    # 13. 例1-4 页面效果
    p = Page()
    p.title("我的第一个WPS文档", size=24, space=16)
    p.p("国家计算机二级考试（WPS Office）由上机操作题和单项选择题组成。", indent_chars=2)
    p.spacer(30)
    p.raw(R(70, 60, 620, 900, fill="none", stroke="#C0392B", sw=1.4, rx=0,
            extra=' stroke-dasharray="8 5"'))
    p.raw(T(88, 100, "上 2.54cm", size=13, fill="#C0392B"))
    p.raw(T(88, 124, "左 3.17cm", size=13, fill="#C0392B"))
    p.raw(T(560, 940, "下 2.54cm / 右 3.17cm", size=13, fill="#C0392B"))
    page_scene("e1-4-result", p, "A4 纵向 + 上下 2.54 / 左右 3.17 厘米（虚线为页边距）")


# ============================== 课时 2 ==============================
def build_l2():
    # 15. 开始选项卡总览
    ui("l2-begin", "开始", TAB_GROUPS["开始"],
       [(1, "字体", 1), (2, "段落", 2)],
       doc={"title": "通知", "lines": [{"w": 140, "c": "#9AA0A6"}, {"w": 240, "c": "#C8CDD3"},
                                       {"w": 225, "c": "#C8CDD3"}]},
       note=["① 字体组：字体、字号、字形、颜色、字符底纹与边框、字符间距",
             "② 段落组：对齐、缩进、行距、段间距、项目符号与编号"])

    # 16. 例2-1 字体对话框 - 字符间距
    dialog_scene("e2-1-font", "字体", ["字体", "字符间距"],
                 [("中文字体", "黑体", "sel"),
                  ("西文字体", "黑体", "sel"),
                  ("字形", "标准", "sel"),
                  ("字号", "二号 (22 磅)", "sel"),
                  ("字间距", "加宽", "sel"),
                  ("磅值", "2 磅", "text")],
                 marks={4: 1, 5: 1},
                 active_tab=1,
                 note=["①「字符间距」选项卡 → 间距选「加宽」→ 磅值填 2 磅",
                       "字体、字号也可直接在下拉框输入名称后回车"])

    # 17. 例2-1 段落对话框
    dialog_scene("e2-1-para", "段落", ["缩进和间距", "中文版式", "换行和分页"],
                 [("对齐方式", "居中", "sel"),
                  ("行距", "1.5 倍行距", "sel"),
                  ("段前", "0.5 行", "text"),
                  ("段后", "0.5 行", "text"),
                  ("缩进", "（段落级别设置）", "field")],
                 marks={0: 1, 2: 2, 3: 2},
                 note=["① 对齐方式：标题居中、落款右对齐、正文两端对齐",
                       "② 段前 / 段后可填「行」也可填「磅」，题目要求几行就填几行"])

    # 18. 例2-1 通知成品
    p = Page()
    p.title("关于2026年秋季学期计算机等级考试报名的通知", size=24, weight=700, space=20)
    p.line("各二级学院、全体在校学生：", size=15.3, space=10)
    p.p("根据教育部教育考试院安排，2026年下半年全国计算机等级考试将于9月26日至28日举行。"
        "本次考试我校考点设在实训楼A座三楼机房，共设6个考场。", indent_chars=2, space=6)
    p.p("报名采用网上报名方式，考生须登录中国教育考试网完成注册、填报与缴费。"
        "报名成功后请在规定时间内自行打印准考证。", indent_chars=2, space=20)
    p.line("教务处", size=15.3, align="right", space=2)
    p.line("2026年9月1日", size=15.3, align="right", space=16)
    p.raw(T(p.margin, p.y, "标题：黑体二号加粗居中、字符加宽 2 磅、段前后 0.5 行；落款用右对齐，不用空格",
            size=13, fill="#C0392B"))
    p.y += 24
    page_scene("e2-1-result", p, "通知成品：标题、称谓、正文、落款四级格式齐备")

    # 19. 例2-2 段落对话框
    dialog_scene("e2-2-para", "段落", ["缩进和间距", "中文版式", "换行和分页"],
                 [("对齐方式", "两端对齐", "sel"),
                  ("行距", "1.5 倍行距", "sel"),
                  ("段前", "0 行", "text"),
                  ("段后", "0 行", "text"),
                  ("特殊格式", "首行缩进", "sel"),
                  ("度量值", "2 字符", "text")],
                 marks={0: 1, 1: 1, 4: 2, 5: 2},
                 note=["① 两端对齐 + 1.5 倍行距 + 段前段后 0 行",
                       "② 特殊格式选「首行缩进」，度量值填 2 字符（不是 2 厘米）"])

    # 20. 例2-2 正文效果
    p = Page()
    p.p("根据教育部教育考试院安排，2026年下半年全国计算机等级考试将于9月26日至28日举行。"
        "本次考试我校考点设在实训楼A座三楼机房，共设6个考场。", indent_chars=2, lh=2.0, space=10)
    p.p("报名采用网上报名方式，考生须登录中国教育考试网完成注册、填报与缴费。"
        "报名成功后请在规定时间内自行打印准考证。", indent_chars=2, lh=2.0, space=16)
    p.raw(T(p.margin, p.y, "首行缩进 2 字符（首行前空两格，是缩进不是空格）　行距 1.5 倍",
            size=13, fill="#C0392B"))
    p.y += 26
    page_scene("e2-2-result", p, "正文效果：首行缩进两格、两端对齐、1.5 倍行距")

    # 21. 例2-3 字符底纹与边框
    ui("e2-3-char", "开始", TAB_GROUPS["开始"],
       [(1, "字符底纹", 1), (1, "字符边框", 2)],
       doc={"title": "重点提示", "lines": [{"w": 120, "c": "#F6D97A"}, {"w": 240, "c": "#C8CDD3"},
                                           {"w": 210, "c": "#C8CDD3"}]},
       note=["① 字符底纹：给文字加底色（黄色小块）", "② 字符边框：给文字加方框",
             "字符级格式只包住文字；整行通栏的底纹要到「边框和底纹」里设段落"])

    # 22. 例2-3 格式刷
    ui("e2-3-paint", "开始", TAB_GROUPS["开始"],
       [(0, "格式刷", 1)],
       doc={"title": "第 1 段（样板）", "lines": [{"w": 150, "c": "#9AA0A6"}, {"w": 230, "c": "#C8CDD3"}]},
       note=["①「格式刷」在「开始 → 剪贴板」组",
             "单击：只能刷一次，松开即失效",
             "双击：可连续刷多段，按 Esc 退出",
             "只复制格式，不复制文字"])

    # 23. 例2-3 效果
    p = Page()
    p.line("重点提示：报名信息一经提交，姓名与身份证号不可修改。", size=15.3, space=4)
    p.raw(R(p.margin - 4, p.y - 20, tw("重点提示", 15.3) + 10, 26, fill="#FFF2A8", stroke="#D9B400", sw=1.2, rx=3))
    p.y += 18
    p.line("注意：缴费成功后才算报名完成，未缴费的报名记录将在24小时后自动失效。", size=15.3, space=10)
    p.raw(R(p.margin + tw("注意", 15.3), p.y - 22, tw("注意", 15.3), 24, fill="none", stroke="#C0392B", sw=1.6, rx=3))
    p.raw(T(p.margin + tw("注意", 15.3) + 2, p.y - 6, "注意", size=15.3, fill="#C0392B", weight=700))
    p.y += 14
    p.line("请考生在考前一周登录系统打印准考证，并核对考试时间与考场位置。", size=15.3, space=10)
    p.line("考试当天须携带准考证和有效身份证件，提前30分钟到达考场。", size=15.3, space=16)
    p.raw(T(p.margin, p.y, "第 1 段设为楷体小四加粗后，用格式刷双击复制到第 3、4 段",
            size=13, fill="#C0392B"))
    p.y += 24
    page_scene("e2-3-result", p, "字符底纹 + 字符边框 + 红色加粗 + 格式刷统一格式")

    # 24. 例2-4 编号与项目符号下拉
    o = [R(0, 0, W, 420, fill="#F3F5F8", stroke=None, rx=0)]
    mp, mh = menu_panel(60, 40, 220, ["无", "●", "○", "■"], marked={"●": 1}, title="项目符号", rowh=30)
    o.append(mp)
    mp2, _ = menu_panel(320, 40, 220, ["无", "1. 2. 3.", "1) 2) 3)", "I. II. III.", "a. b. c."],
                        marked={"1. 2. 3.": 2}, title="编号", rowh=30)
    o.append(mp2)
    o.append(T(60, 250, "① 项目符号下拉：选圆点「●」", size=14, fill=C_TEXT2))
    o.append(T(320, 250, "② 编号下拉：选「1. 2. 3.」自动编号", size=14, fill=C_TEXT2))
    o.append(T(60, 290, "自动编号不手打数字：中间插入或删除一条，其余自动重排", size=13, fill=C_MUTED))
    o.append(T(60, 320, "选中多段后再套编号 / 项目符号，一次即可全部生效", size=13, fill=C_MUTED))
    o.append(tag_svg(W, 420))
    write("e2-4-list", svg_doc(W, 420, "".join(o), bg="#F3F5F8"))

    # 25. 例2-4 边框和底纹对话框
    dialog_scene("e2-4-border", "边框和底纹", ["边框", "底纹", "页面边框"],
                 [("设置", "方框", "sel"),
                  ("线型", "实线", "sel"),
                  ("宽度", "1.5 磅", "sel"),
                  ("应用于", "段落", "sel"),
                  ("填充", "浅黄 RGB(255,255,204)", "text"),
                  ("距正文 左/右", "0.2 厘米", "text")],
                 marks={0: 1, 2: 1, 3: 2, 4: 2, 5: 3},
                 active_tab=0,
                 note=["① 边框：方框 + 实线 + 1.5 磅", "② 底纹颜色用「其他颜色 → 自定义」输入 RGB",
                       "③「应用于」选段落；「选项」里设置距正文距离"])

    # 26. 例2-4 效果
    p = Page()
    p.h2("报名流程", size=18, space=8)
    for i, t in enumerate(["登录中国教育考试网注册账号", "选择考点与考试科目",
                           "上传照片并在线缴费", "打印准考证"]):
        p.numbered(i + 1, t, space=3)
    p.y += 10

    def inner():
        p.h2("注意事项", size=18, space=8)
        for t in ["照片须为近期免冠证件照，背景为白色或浅蓝色",
                  "缴费后请保留支付凭证截图", "报名截止后不再接受补报"]:
            p.bullet(t, space=3)

    p.boxed(inner, bg="#FFFDE0", stroke="#D9B400")
    p.spacer(12)
    p.raw(T(p.margin, p.y, "「注意事项」整块：1.5 磅方框 + 浅黄底纹 + 距正文 0.2 厘米",
            size=13, fill="#C0392B"))
    p.y += 24
    page_scene("e2-4-result", p, "自动编号 + 项目符号 + 段落边框底纹块")
