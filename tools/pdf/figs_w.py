# -*- coding: utf-8 -*-
"""第一部分 · 文字处理：界面示意图（课程 12 张 + 成稿基准 1 张）

约定
- 每张图 = WPS 文字窗口的一段真实界面，标注编号 1..n 与图例一一对应。
- 图上出现的每个命令，都在该节的「核心内容」或「关键操作路径」里出现过，不引入新操作。
"""
from ui import *
import ui


# ============================================================
#  本册专用零件
# ============================================================
def ctx_tab(f, x, y, label, color=None):
    """上下文选项卡（如「页眉和页脚」「图片工具」），与普通选项卡区分"""
    c = color or "#c2410c"
    tw = 20 + len(label) * 13.4
    f.rect(x, y + 3, tw, 29, "#fff7ed", c, 1.2, 2)
    f.rect(x + 4, y + 29, tw - 8, 2.4, c)
    f.txt(x + tw / 2, y + 22, label, 13, c, "middle", bold=True)
    f.at("ctx:" + label, x + tw / 2, y + 18)
    return tw


def backstage(f, x, y, w, h, items, hi=None):
    f.rect(x, y, w, h, "#ffffff", K["line2"], 1)
    cy = y + 14
    for it in items:
        on = it == hi
        if on:
            f.rect(x + 8, cy, w - 16, 30, K["blue2"], "none", 0, 3)
        f.txt(x + 24, cy + 20, it, 12.5, K["blue"] if on else K["txt"], bold=on)
        f.at("bs:" + it, x + 24, cy + 15)
        cy += 34
    return f


def template_cards(f, x, y, w, title="新建"):
    f.txt(x, y + 8, title, 15, K["txt"], bold=True)
    names = ["空白文档", "简历", "工作汇报", "会议纪要", "论文", "合同"]
    for i, nm in enumerate(names):
        cx = x + (i % 3) * 128
        cy = y + 28 + (i // 3) * 116
        f.rect(cx, cy, 112, 92, "#fbfcfd", K["line2"], 0.9, 3)
        f.rect(cx + 14, cy + 12, 84, 52, "#ffffff", K["line"], 0.8)
        for j, ww in enumerate([64, 64, 44]):
            f.rect(cx + 24, cy + 24 + j * 9, ww, 3.4, "#dde3ea", "none", 0, 2)
        f.txt(cx + 56, cy + 78, nm, 10.8, K["txt2"], "middle")
    return f


def style_gallery(f, x, y, w=250, hi="标题 1"):
    shadow(f, x, y, w, 236, 4, 0.20, 3)
    f.rect(x, y, w, 236, "#ffffff", K["line2"], 1, 4)
    f.txt(x + 12, y + 20, "样式", 12.5, K["txt"], bold=True)
    f.txt(x + w - 16, y + 20, "全部清除", 10.5, K["blue"], "end")
    rows = [("正文", "宋体 小四"), ("标题 1", "黑体 三号 加粗"), ("标题 2", "黑体 四号 加粗"),
            ("标题 3", "黑体 小四 加粗"), ("题注", "宋体 五号"), ("页眉", "宋体 小五")]
    for i, (nm, desc) in enumerate(rows):
        ry = y + 32 + i * 32
        on = nm == hi
        if on:
            f.rect(x + 6, ry, w - 12, 28, K["blue2"], "none", 0, 3)
        f.txt(x + 16, ry + 18, nm, 12, K["blue"] if on else K["txt"], bold=on)
        f.txt(x + w - 16, ry + 18, desc, 10, K["txt3"], "end")
        f.at("st:" + nm, x + 6, ry + 14)
    return f


def page_with_header(f, x, y, w, h, header="毕业论文", footer="第 1 页 共 12 页",
                     body_lines=6, title=""):
    """带页眉页脚的页面，页眉页脚区用虚线框标出"""
    page(f, x, y, w, h, title="", top=0)
    f.rect(x + 24, y + 14, w - 48, 22, "#f7fafd")
    f.raw('<rect x="%.1f" y="%.1f" width="%.1f" height="22" rx="1" fill="none" stroke="%s" '
          'stroke-width="0.9" stroke-dasharray="4 3"/>' % (x + 24, y + 14, w - 48, K["blue"]))
    f.txt(x + 32, y + 29, header, 9.5, "#334155")
    f.at("hdrarea", x + w / 2, y + 25)
    ty = y + 54
    if title:
        f.txt(x + w / 2, ty + 8, title, 14, "#1a2129", "middle", bold=True)
        ty += 26
    text_lines(f, x + 30, ty, w - 60, body_lines, 13.2, "#c9d0da", 4.1)
    fy = y + h - 38
    f.rect(x + 24, fy, w - 48, 22, "#f7fafd")
    f.raw('<rect x="%.1f" y="%.1f" width="%.1f" height="22" rx="1" fill="none" stroke="%s" '
          'stroke-width="0.9" stroke-dasharray="4 3"/>' % (x + 24, fy, w - 48, K["blue"]))
    f.txt(x + w / 2, fy + 15, footer, 9.5, "#334155", "middle")
    f.at("ftrarea", x + w / 2, fy + 11)
    return f


def photo_box(f, x, y, w, h, label="图片"):
    f.rect(x, y, w, h, "#eef2f7", "#b9c3d0", 1, 2)
    f.circle(x + w * .28, y + h * .28, w * .045, "none", "#9aa6b5", 1.2)
    f.path("M%.1f %.1f L%.1f %.1f L%.1f %.1f L%.1f %.1f Z" % (
        x + 6, y + h - 6, x + w * .42, y + h * .40, x + w * .62, y + h - 20, x + w - 8, y + h - 6),
        "#d6dee8", "#9aa6b5", 1)
    return f


# ============================================================
#  课程配图
# ============================================================
def c1_1():
    """1.1 新建、录入、选定与保存"""
    f, by = doc_scene(title="实习报告.docx - WPS Office", tab="文件", groups=[],
                      status="第 1 页，共 2 页　字数：1,284", ruler_on=False)
    backstage(f, 0, by, 214, 560 - 22 - by,
              ["新建", "打开", "最近使用", "保存", "另存为", "输出为 PDF", "打印", "关闭"], hi="另存为")
    template_cards(f, 240, by + 6, 700)
    dx, dy = 470, 246
    form(f, dx, dy, 420, title="另存为", rows=[
        ("c", [("文件名(N)", "field", "20230101-张三-W-01.docx", 252)]),
        ("c", [("文件类型(T)", "combo", "WPS 文字 文件(*.docx)", 252)]),
        ("note", "保存位置：D:\\考试作品\\    修改时间：今天 14:20"),
    ], buttons=("保存", "取消"))
    f.at("fname", dx + 262, dy + 57)
    marks_from(f, [
        ("tab:文件", "点「文件」进入后台视图", "top", 30),
        ("bs:另存为", "「另存为」；直接按 F12 也可弹此框", "right", 26),
        ("fname", "文件名：学号-姓名-练习编号，扩展名保持 .docx", "right", 24),
    ])
    return f


def c1_2():
    """1.2 字符格式与段落格式"""
    f, by = doc_scene(title="毕业论文.docx - WPS Office", tab="开始",
                      status="第 1 页，共 12 页　字数：8,436", page_kw=None)
    page(f, 118, by + 26, 254, 366, title="第一章　绪论", top=28)
    f.rect(152, by + 100, 186, 4.1, "#c3cbd6", "none", 0, 2)
    f.rect(152, by + 113, 186, 4.1, "#c3cbd6", "none", 0, 2)
    f.rect(124, by + 127, 214, 4.1, "#9aa4b2", "none", 0, 2)
    f.rect(124, by + 140, 214, 4.1, "#c3cbd6", "none", 0, 2)
    text_lines(f, 124, by + 162, 214, 9, 13.2, "#c9d0da", 4.1)

    dx, dy = 412, 160
    form(f, dx, dy, 424, title="段落", rows=[
        ("g", "缩进"),
        ("c", [("左(L)", "spin", "0 字符", 84), ("右(R)", "spin", "0 字符", 84)]),
        ("c", [("特殊格式", "combo", "首行缩进", 116, "dfmt", True)]),
        ("c", [("度量值", "spin", "2 字符", 116, "dval")]),
        ("sep",),
        ("g", "间距"),
        ("c", [("段前", "spin", "0 行", 84), ("段后", "spin", "0 行", 84)]),
        ("c", [("行距", "combo", "1.5 倍行距", 116, "dlh")]),
        ("c", [("设置值", "field", "", 116)]),
    ], tabs=["缩进和间距", "换行和分页", "中文版式"], active="缩进和间距")

    marks_from(f, [
        ("launcher:段落", "「段落」组右下角：对话框启动器", "bottom", 36),
        ("dfmt", "特殊格式 → 首行缩进", "right", 26),
        ("dlh", "行距 → 1.5 倍行距", "right", 26),
    ])
    return f


def c1_3():
    """1.3 样式、主题、查找替换与页面装饰"""
    f, by = doc_scene(title="毕业论文.docx - WPS Office", tab="开始",
                      status="第 1 页，共 12 页　字数：8,436", page_kw=None)
    style_gallery(f, 620, by + 4, 250)
    dx, dy = 96, 214
    form(f, dx, dy, 452, title="查找和替换", rows=[
        ("c", [("查找内容(N)", "field", "第 1 章", 250)]),
        ("c", [("替换为(I)", "field", "第一章", 250)]),
        ("cb", "使用通配符", False, "wild", 186),
    ], tabs=["查找", "替换", "定位"], active="替换",
        buttons=("替换全部", "查找下一个", "取消"))
    marks_from(f, [
        ("launcher:样式", "「样式」组右下角箭头：打开样式窗格", "bottom", 34),
        ("st:标题 1", "右键样式 → 修改；改一处、全文同步", "left", 26),
        ("wild", "「替换」选项卡 → 勾选使用通配符", "right", 26),
    ])
    return f


def c1_4():
    """1.4 长文档五件套与综合大题"""
    f, by = doc_scene(title="毕业论文.docx - WPS Office", tab="引用",
                      status="第 3 页，共 24 页　字数：15,672", page_kw=None,
                      groups=rib_wps_ref())
    page(f, 96, by + 26, 254, 358, title="目　录", top=26)
    items = ["第一章 绪论", "1.1 研究背景", "1.2 研究方法", "第二章 需求分析",
             "2.1 功能需求", "2.2 非功能需求", "第三章 系统设计"]
    for i, txt in enumerate(items):
        ty = by + 78 + i * 20
        indent = 0 if len(txt) > 6 else 16
        f.txt(110 + indent, ty, txt, 9.2, "#334155")
        f.rect(232, ty - 2, 64 - indent, 2, "#d5dce6", "none", 0, 1)
        f.txt(330, ty, str(1 + i), 9.2, "#64748b", "end")

    dx, dy = 430, 196
    form(f, dx, dy, 402, title="目录", rows=[
        ("cb", "显示页码", True),
        ("c", [("显示级别(S)", "spin", "3", 70, "lvl")]),
        ("c", [("制表符前导符(T)", "combo", "……", 96, "lead")]),
        ("sep",),
        ("note", "格式：来自模板「目录 1」「目录 2」「目录 3」"),
    ], tabs=["目录", "显示级别"], active="目录")
    marks_from(f, [
        ("big:目录", "「引用」→「目录」→ 插入目录", "right", 28),
        ("lvl", "显示级别设为 3：标题 1—3 全部进目录", "right", 26),
        ("lead", "制表符前导符选点线，页码右对齐", "right", 26),
    ])
    return f


def c2_1():
    """2.1 页眉页脚与页码进阶"""
    f, by = doc_scene(title="毕业论文.docx - WPS Office", tab="插入",
                      status="第 2 页，共 12 页　字数：9,120", ruler_on=False,
                      groups=[("页眉和页脚", 214, [[("big", "页眉", 52, "pagehdr"),
                                                    ("big", "页脚", 52, "pagehdr"),
                                                    ("big", "页码", 52, "toc")]]),
                              ("选项", 200, [[("btn", "首页不同", 80), ("btn", "奇偶页不同", 92)]]),
                              ("位置", 150, [[("btn", "页眉顶端 1.5cm", 128)]]),
                              ("关闭", 80, [[("btn", "关闭页眉", 64)]])])
    ctx_tab(f, 466, 30, "页眉和页脚")
    page_with_header(f, 118, by + 16, 254, 328, header="大连财经学院 · 毕业论文",
                     footer="第 2 页　共 12 页", body_lines=5, title="第一章　绪论")
    marks_from(f, [
        ("big:页眉", "「插入」→「页眉」→ 选内置样式后进入编辑态", "bottom", 62),
        ("btn:首页不同", "勾选首页不同 / 奇偶页不同", "bottom", 32),
        ("ftrarea", "页脚内插页码域：插入 → 页码 → 页面底端居中", "bottom", 26),
    ])
    return f


def c2_2():
    """2.2 表格的制作与编辑"""
    f, by = doc_scene(title="实习报告.docx - WPS Office", tab="插入",
                      status="第 2 页，共 5 页　字数：1,860", page_kw=None,
                      groups=rib_wps_insert())
    page(f, 110, by + 24, 300, 362, title="")
    f.txt(260, by + 48, "三、实习数据统计", 11, "#1a2129", "middle", bold=True)
    cell_table(f, 120, by + 62, ["部门", "人数", "占比", "平均工时"], [
        ["研发部", "42", "38.5%", "9.2"],
        ["市场部", "28", "25.7%", "8.6"],
        ["行政部", "15", "13.8%", "8.0"],
        ["合　计", "109", "100%", "—"],
    ], rowh=21, colw=[70, 54, 60, 72], size=9.6,
        fills={(4, 0): "#f1f5fb", (4, 1): "#f1f5fb", (4, 2): "#f1f5fb", (4, 3): "#f1f5fb"})
    f.at("cell", 120, by + 72)
    text_lines(f, 128, by + 196, 264, 6, 13, "#c9d0da", 4)

    dx, dy = 452, 214
    form(f, dx, dy, 380, title="表格属性", rows=[
        ("g", "行"),
        ("c", [("指定高度", "spin", "1.2 厘米", 96, "rh")]),
        ("c", [("行高值是", "combo", "固定值", 96, "rhm")]),
        ("sep",),
        ("g", "列"),
        ("c", [("指定宽度", "spin", "3.5 厘米", 96, "cw")]),
    ], tabs=["表格", "行", "列", "单元格"], active="行")
    marks_from(f, [
        ("big:表格", "「插入」→「表格」→ 拖选或输入行列数", "bottom", 30),
        ("rh", "表格属性 → 行 → 指定高度 + 固定值", "right", 26),
        ("cell", "选中整表：边框和底纹 → 自定义线型与宽度", "left", 22),
    ])
    return f


def c2_3():
    """2.3 图形与图像对象的编辑处理"""
    f, by = doc_scene(title="实习报告.docx - WPS Office", tab="插入",
                      status="第 3 页，共 5 页　字数：2,140", page_kw=None)
    ctx_tab(f, 466, 30, "图片工具")
    page(f, 110, by + 20, 320, 366, title="")
    f.txt(270, by + 42, "二、实习现场", 11, "#1a2129", "middle", bold=True)
    photo_box(f, 140, by + 56, 260, 150, "现场照片")
    f.rect(140, by + 56, 260, 150, "none", K["blue"], 1.4, 0)
    for hx, hy in [(140, by + 56), (400, by + 56), (140, by + 206), (400, by + 206)]:
        f.rect(hx - 3, hy - 3, 6, 6, "#ffffff", K["blue"], 1.2, 0)
    f.at("pic", 270, by + 130)
    text_lines(f, 140, by + 222, 260, 6, 13, "#c9d0da", 4)

    dx, dy = 470, 200
    form(f, dx, dy, 386, title="布局", rows=[
        ("g", "文字环绕"),
        ("rd", "嵌入型", False),
        ("rd", "四周型（文字环绕在四周）", True, "wrap"),
        ("sep",),
        ("c", [("上", "spin", "0.5 厘米", 78), ("下", "spin", "0.5 厘米", 78)]),
        ("c", [("左", "spin", "0.5 厘米", 78), ("右", "spin", "0.5 厘米", 78)]),
    ])
    marks_from(f, [
        ("pic", "选中图片 →「图片工具」→「环绕」→ 四周型", "left", 22),
        ("wrap", "其他布局选项 → 距正文上下左右各 0.5 厘米", "right", 26),
        ("ctx:图片工具", "图片工具选项卡：大小、裁剪、环绕、对齐都在这里", "bottom", 28),
    ])
    return f


def c2_4():
    """2.4 文本框、文档部件、符号与公式"""
    f, by = doc_scene(title="数学试卷.docx - WPS Office", tab="插入",
                      status="第 1 页，共 4 页　字数：1,320", page_kw=None,
                      groups=rib_wps_insert())
    page(f, 110, by + 20, 330, 364, title="")
    f.txt(275, by + 46, "一、填空题", 12, "#1a2129", "middle", bold=True)
    f.rect(300, by + 68, 58, 132, "#ffffff", K["blue"], 1.3, 2)
    for i, ch in enumerate("答案区域"):
        f.txt(329, by + 92 + i * 22, ch, 11, "#334155", "middle")
    f.at("tb", 300, by + 134)
    f.rect(140, by + 80, 132, 46, "#fbfcfe", "#dbe2ec", 0.9, 2)
    f.txt(156, by + 110, "x =", 12.5, "#1f2937")
    f.txt(190, by + 100, "−b ± √(b²−4ac)", 10.5, "#1f2937")
    f.rect(188, by + 103, 104, 1, "#334155", "none", 0, 0)
    f.txt(190, by + 121, "2a", 10.5, "#1f2937")
    f.at("formula", 205, by + 103)

    menu(f, 726, by + 4, 234, [("head", "文本框"), ("横排文本框", ""), ("竖排文本框", ""),
                               ("sep",), ("绘制文本框", ""), ("文本框链接", "")], hi="竖排文本框")
    menu(f, 250, by + 150, 214, [("head", "公式"), ("插入新公式", ""), ("分式", "▸"),
                                 ("根式", "▸"), ("积分", "▸"), ("矩阵", "▸")], hi="根式")
    marks_from(f, [
        ("big:文本框", "「插入」→「文本框」→ 横排 / 竖排", "bottom", 30),
        ("tb", "竖排文本框：文字自上而下，用于侧栏、书脊", "left", 22),
        ("formula", "「插入」→「公式」→ 选结构（分式／根式／矩阵）", "top", 26),
    ])
    return f


def c3_1():
    """3.1 目录、题注与交叉引用"""
    f, by = doc_scene(title="毕业论文.docx - WPS Office", tab="开始",
                      status="第 5 页，共 24 页　字数：16,420", page_kw=None)
    page(f, 60, by + 18, 250, 358, title="")
    items = ["第一章　绪论", "1.1　研究背景", "1.2　研究方法", "第二章　需求分析",
             "2.1　功能需求", "2.2　非功能需求"]
    for i, txt in enumerate(items):
        ty = by + 48 + i * 22
        f.txt(76, ty, txt, 8.8, "#334155")
        f.rect(200, ty - 2, 66, 2, "#d5dce6", "none", 0, 1)
        f.txt(300, ty, str(1 + i), 8.8, "#64748b", "end")
    f.at("lv", 76, by + 70)
    menu(f, 330, by + 2, 262, [("head", "多级列表"), ("无列表", ""), ("1. 2. 3.", ""),
                               ("定义新多级列表", ""), ("定义新列表样式", ""),
                               ("sep",), ("设置列表级别", "▸")], hi="定义新多级列表")

    dx, dy = 610, 196
    form(f, dx, dy, 376, title="题注", rows=[
        ("c", [("题注(C)", "field", "表 1-1", 210)]),
        ("c", [("标签(L)", "combo", "表", 96)]),
        ("c", [("位置(P)", "combo", "所选项目下方", 148)]),
        ("sep",),
        ("cb", "包含章节号", True, "chap"),
        ("c", [("章节起始样式", "combo", "标题 1", 108), ("分隔符", "combo", "-", 56)]),
    ])
    marks_from(f, [
        ("mi:定义新多级列表", "「多级列表」→ 定义新多级列表 → 更多 → 链接到样式", "right", 24),
        ("lv", "标题 1—3 挂上编号，目录才能自动生成三级条目", "left", 22),
        ("chap", "题注 → 勾选包含章节号，编号变成「表 1-1」", "right", 24),
    ])
    return f


def c3_2():
    """3.2 脚注、尾注与索引"""
    f, by = doc_scene(title="毕业论文.docx - WPS Office", tab="引用",
                      status="第 6 页，共 24 页　字数：16,980", page_kw=None,
                      groups=rib_wps_ref())
    page(f, 96, by + 18, 268, 362, title="")
    f.txt(130, by + 42, "第一章　绪论", 11, "#1a2129")
    text_lines(f, 112, by + 58, 236, 7, 13, "#c9d0da", 4)
    f.txt(112, by + 166, "研究背景", 9.2, "#334155")
    f.txt(146, by + 166, "①", 8, "#cf3f3f")
    f.rect(96, by + 296, 268, 1, "#cbd5e1", "none", 0, 0)
    f.txt(108, by + 314, "① 王某某. 毕业论文写作规范[M]. 北京: 高等教育出版社, 2023: 15.",
          7.6, "#475569")
    f.at("fn", 340, by + 166)

    dx, dy = 400, 196
    form(f, dx, dy, 386, title="脚注和尾注", rows=[
        ("g", "位置"),
        ("rd", "脚注：页面底端", True),
        ("rd", "尾注：文档结尾", False),
        ("sep",),
        ("c", [("编号格式", "combo", "①, ②, ③", 104), ("起始编号", "spin", "1", 56)]),
        ("c", [("编号方式", "combo", "连续", 104)]),
    ], buttons=("转换", "应用", "取消"))
    marks_from(f, [
        ("big:插入脚注", "「引用」→「插入脚注」，光标处出现上标序号", "bottom", 30),
        ("fn", "脚注正文在页面底端，与正文用短横线分隔", "right", 26),
        ("btn:转换", "脚注对话框 →「转换」可与尾注互换", "bottom", 24),
    ])
    return f


def c3_3():
    """3.3 文档审阅与修订"""
    f, by = doc_scene(title="论文修改稿.docx - WPS Office", tab="审阅",
                      status="第 2 页，共 12 页　字数：7,640", page_kw=None,
                      groups=rib_wps_review())
    page(f, 96, by + 20, 300, 360, title="")
    f.txt(130, by + 46, "第二章　需求分析", 12, "#1a2129", bold=True)
    f.txt(112, by + 76, "系统应支持", 9.6, "#334155")
    f.raw('<text x="196" y="%d" font-size="9.6" fill="#b91c1c" '
          'text-decoration="line-through">最多 500 人</text>' % (by + 76))
    f.txt(268, by + 76, "在线", 9.6, "#15803d")
    f.txt(112, by + 94, "同时在线考试，并记录操作日志。", 9.6, "#334155")
    f.rect(402, by + 60, 92, 44, "#fefce8", "#e5d08a", 0.9, 2)
    f.txt(410, by + 76, "审阅人 A", 8.2, "#92720a", bold=True)
    f.txt(410, by + 89, "人数要与需求文档一致", 7.8, "#92720a")
    f.at("rev", 306, by + 76)

    dx, dy = 528, 236
    pane(f, dx, dy, 420, 262, "限制编辑", tabs=["限制编辑", "保护文档"], active="限制编辑")
    check(f, dx + 16, dy + 66, "仅允许在文档中进行此类型的编辑", True)
    combo_box(f, dx + 28, dy + 92, 272, "不允许任何更改（只读）")
    check(f, dx + 16, dy + 126, "设置文档的保护方式", False)
    field(f, dx + 28, dy + 150, 180, "输入密码", ph=True)
    f.at("protect", dx + 210, dy + 161)
    btn(f, dx + 292, dy + 188, 96, "启动强制保护", 24, True)
    f.at("force", dx + 340, dy + 200)
    marks_from(f, [
        ("big:修订", "「审阅」→「修订」→ 开始修订，之后所有改动留痕", "bottom", 58),
        ("rev", "删除线＝删掉的内容，下划线＝新增的内容", "right", 24),
        ("protect", "限制编辑 → 只读 → 启动强制保护", "right", 24),
    ])
    return f


def c3_4():
    """3.4 邮件合并与多窗口协作"""
    f, by = doc_scene(title="录取通知书.docx - WPS Office", tab="邮件",
                      tabs=["开始", "插入", "页面", "引用", "邮件", "审阅", "视图"],
                      status="第 1 页，共 1 页　字数：186", page_kw=None,
                      groups=[("邮件合并", 306, [[("big", "开始邮件合并", 86, "page"),
                                                  ("big", "选择收件人", 76, "table"),
                                                  ("big", "插入合并域", 86, "link")]]),
                              ("编写与插入域", 226, [[("big", "突出显示合并域", 96, "review"),
                                                      ("big", "规则", 56, "fx")]]),
                              ("完成", 196, [[("big", "完成并合并", 86, "review"),
                                              ("big", "预览结果", 76, "view")]])])
    page(f, 96, by + 20, 300, 356, title="")
    f.txt(246, by + 48, "录 取 通 知 书", 13, "#1a2129", "middle", bold=True)
    f.rect(110, by + 73, 44, 15, "#fff3d6", "#e0c07a", 0.9, 1)
    f.rect(170, by + 91, 44, 15, "#fff3d6", "#e0c07a", 0.9, 1)
    f.txt(112, by + 84, "《姓名》同学：", 10, "#334155")
    f.txt(112, by + 102, "祝贺你被我校《专业》专业录取。", 10, "#334155")
    f.txt(112, by + 120, "请于 9 月 1 日持本通知书报到。", 10, "#334155")
    f.at("field", 268, by + 98)
    f.txt(112, by + 180, "大连财经学院", 10, "#475569")
    f.txt(112, by + 198, "2026 年 7 月", 10, "#475569")

    menu(f, 452, by + 4, 236, [("head", "完成并合并"), ("编辑单个文档", ""),
                               ("打印文档", ""), ("发送电子邮件", ""), ("sep",),
                               ("合并到新文档", "")], hi="编辑单个文档")
    marks_from(f, [
        ("big:开始邮件合并", "「邮件」→「开始邮件合并」→ 信函", "bottom", 52),
        ("field", "光标定位 → 插入合并域 → 姓名 / 专业", "right", 24),
        ("mi:编辑单个文档", "完成并合并 → 编辑单个文档 → 全部", "right", 26),
    ])
    return f


def r_w():
    """第四章开头的成稿版式基准（合格文档的版式要素）"""
    f = Fig(1000, 470)
    px, py, pw, ph = 88, 14, 320, 442
    page(f, px, py, pw, ph, title="")
    # 版心（页边距以内）虚线
    f.raw('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="2" fill="none" stroke="%s" '
          'stroke-width="1" stroke-dasharray="5 4" opacity="0.7"/>'
          % (px + 26, py + 8, pw - 52, ph - 58, K["blue"]))
    # 页眉
    f.txt(px + pw / 2, py + 28, "2026 年暑期实训 · 通知类公文", 8.6, "#334155", "middle")
    f.line(px + 30, py + 34, px + pw - 30, py + 34, "#8fa3bd", 0.9)
    f.at("hdrarea", px, py + 30)
    # 标题（黑体二号居中，可折两行）
    f.txt(px + pw / 2, py + 66, "关于开展 2026 年", 12.5, "#1a2129", "middle", bold=True)
    f.txt(px + pw / 2, py + 84, "暑期实训的通知", 12.5, "#1a2129", "middle", bold=True)
    f.at("title", px, py + 76)
    # 正文：首行缩进 2 字符，1.5 倍行距
    ty = py + 106
    for n in (3, 3, 2):
        for i in range(n):
            ind = 22 if i == 0 else 0
            f.rect(px + 30 + ind, ty, pw - 62 - ind - [0, 18, 6][i % 3], 4.2, "#c9d0da", "none", 0, 2)
            ty += 14.6
        ty += 6
    f.at("body", px + 30, py + 112)
    # 表格
    cell_table(f, px + 30, ty + 2, ["序号", "实训项目", "时间"], [
        ["1", "文档排版与长文档", "7 月 6 日"], ["2", "表格函数与图表", "7 月 8 日"]],
        colw=[30, 118, 84], rowh=18, size=9.2)
    # 落款：右对齐
    f.txt(px + pw - 32, py + ph - 88, "大连财经学院", 9.2, "#475569", "end")
    f.txt(px + pw - 32, py + ph - 72, "2026 年 7 月 1 日", 9.2, "#475569", "end")
    # 页脚
    f.line(px + 30, py + ph - 36, px + pw - 30, py + ph - 36, "#8fa3bd", 0.9)
    f.txt(px + pw / 2, py + ph - 19, "第 1 页 共 3 页", 8.6, "#334155", "middle")
    f.at("ftrarea", px, py + ph - 26)

    ty2 = spec_table(f, 442, 16, 540, [
        ("页边距", "上/下 2.54 厘米，左/右 3.17 厘米"),
        ("页眉", "宋体小五居中 + 下框线；首页不同按需勾选"),
        ("标题", "黑体二号居中，段前段后 0.5 行"),
        ("正文", "仿宋三号，首行缩进 2 字符，1.5 倍行距"),
        ("表格", "三线表或全框线，表题在表格上方居中"),
        ("落款", "单位与日期右对齐，右缩进 2 字符"),
        ("页码", "宋体小五，页脚居中，「第 X 页 共 Y 页」"),
        ("存盘", "按「学号-姓名-题号」命名，另存 .docx 与 .pdf"),
    ], title="合格成稿的版式要素", rowh=29)
    f.txt(442, ty2 + 16, "题目另给了具体数值时以题目为准；上表只是通用基准。", 10, K["txt3"])
    tip(f, 442, ty2 + 30, 540, "交卷前 30 秒自检：页眉页脚对不对 · 标题字号一致吗 · 页码从第几页起 · 文件名合规吗")
    tip(f, 442, ty2 + 62, 540, "排版顺序记牢：先定页面（页边距/纸张）→ 再套样式 → 最后插图插表，返工最少")

    marks_from(f, [
        ("hdrarea", "页眉：双击页面顶端进入，页边距随拖动改变", "left", 30),
        ("title", "标题与正文都靠「段落」设，不靠空格凑", "left", 30),
        ("ftrarea", "页脚插页码：插入 → 页码 → 位置与格式", "left", 30),
    ])
    return f


REG = {
    "w1_1": c1_1, "w1_2": c1_2, "w1_3": c1_3, "w1_4": c1_4,
    "w2_1": c2_1, "w2_2": c2_2, "w2_3": c2_3, "w2_4": c2_4,
    "w3_1": c3_1, "w3_2": c3_2, "w3_3": c3_3, "w3_4": c3_4,
    "r_w": r_w,
}
