# -*- coding: utf-8 -*-
"""第二部分 · 电子表格：界面示意图（课程 12 张 + 练习若干）

每张图 = WPS 表格窗口的一段真实界面，标注编号 1..n 与图例一一对应。
"""
from ui import *
import ui


# ============================================================
#  本册专用零件
# ============================================================
def formula_bar(f, by, addr="A1", formula=""):
    """覆盖编辑栏内容：名称框地址 + 公式"""
    f.rect(4, by + 3, 58, 18, "#ffffff", K["fieldb"], 0.9, 1)
    f.txt(33, by + 16, addr, 10.5, K["txt2"], "middle")
    f.txt(70, by + 16.5, "fx", 11, K["txt3"])
    f.line(84, by + 4, 84, by + 20, K["line2"], 1)
    f.txt(92, by + 16.5, formula, 11, K["txt"], mono=True)
    f.at("addr", 33, by + 12)
    f.at("fxbar", 400, by + 12)
    return f


def cell_hit(f, x, y, w, h, color="#cfe0ff"):
    """单元格选中/区域高亮"""
    f.rect(x, y, w, h, color, K["blue"], 1.6, 0)
    return f


def funcdlg(f, x, y, w, title="函数参数", params=(), result="", note="", hi=None):
    h = 46 + len(params) * 46 + (44 if result else 26)
    dlg(f, x, y, w, h, title)
    cy = y + 40
    for name, val in params:
        on = (name == hi)
        f.txt(x + 18, cy + 12, name, 11.5, K["txt"], bold=True)
        field(f, x + 104, cy + 2, w - 190, val, focus=on)
        f.txt(x + w - 78, cy + 16, "= " + val[:12], 9.5, K["txt3"])
        f.at("p:" + name, x + 104 + (w - 190) / 2, cy + 13)
        cy += 46
    if result:
        f.line(x + 16, cy + 4, x + w - 16, cy + 4, K["line"], 1)
        f.txt(x + 18, cy + 22, "计算结果 =", 11, K["txt2"])
        f.txt(x + w - 18, cy + 22, result, 11.5, K["green"], "end", bold=True)
        f.at("result", x + w - 40, cy + 18)
        cy += 30
    if note:
        f.txt(x + 18, cy + 16, note, 10, K["txt3"])
    return f


def sheet_grid_at(f, x, y, w, h, data=None, colw=96, rowh=22):
    """指定区域的表格网格（用于浮层里的小表）"""
    ui.sheet_grid(f, x, y, w, h, data=data, colw=colw, rowh=rowh)
    return f


GRADE = {
    (0, 0): "学号", (0, 1): "姓名", (0, 2): "专业", (0, 3): "总分", (0, 4): "平均分",
    (1, 0): "20230101", (1, 1): "张三", (1, 2): "会计学", (1, 3): "412", (1, 4): "82.4",
    (2, 0): "20230102", (2, 1): "李四", (2, 2): "金融学", (2, 3): "396", (2, 4): "79.2",
    (3, 0): "20230103", (3, 1): "王五", (3, 2): "会计学", (3, 3): "431", (3, 4): "86.2",
    (4, 0): "20230104", (4, 1): "赵六", (4, 2): "市场营销", (4, 3): "378", (4, 4): "75.6",
}


# ============================================================
#  课程配图
# ============================================================
def s4_1():
    """4.1 工作簿、工作表与打印输出"""
    f, by = sheet_scene(title="成绩统计.xlsx - WPS 表格", tab="页面", groups=rib_et_page(),
                        status="就绪　　　　　　　　　　　　　　　　　　　工作表 1/3", data=GRADE)
    dx, dy = 470, 216
    form(f, dx, dy, 420, title="页面设置", rows=[
        ("g", "打印"),
        ("c", [("顶端标题行", "field", "$1:$1", 190, "row1")]),
        ("c", [("左端标题列", "field", "$A:$A", 190)]),
        ("cb", "网格线", True),
        ("cb", "行号列标", True),
    ], tabs=["页面", "页边距", "页眉/页脚", "工作表"], active="工作表")
    marks_from(f, [
        ("big:打印区域", "选中区域 →「页面」→「打印区域」→ 设置打印区域", "bottom", 52),
        ("row1", "「打印标题」→ 顶端标题行填 $1:$1，每页都带表头", "right", 26),
        ("big:打印预览", "先「打印预览」再打印，避免分页错位", "bottom", 58),
    ])
    return f


def s4_2():
    """4.2 数据输入与单元格格式化"""
    f, by = sheet_scene(title="成绩统计.xlsx - WPS 表格", tab="开始",
                        status="就绪　平均值: 80.85　计数: 4　求和: 323.4", data=GRADE)
    cell_hit(f, 26 + 4 * 96, 170 + 22, 96, 110)
    f.at("rng", 26 + 4 * 96 + 48, 170 + 60)
    dx, dy = 430, 208
    form(f, dx, dy, 420, title="单元格格式", rows=[
        ("g", "数字"),
        ("c", [("分类(C)", "combo", "数值", 130, "cat", True)]),
        ("c", [("小数位数(D)", "spin", "2", 70, "dec")]),
        ("cb", "使用千位分隔符（,）", True),
        ("cb", "负数红色显示", False),
        ("sep",),
        ("note", "示例：323.40　　确定后整列按此格式显示"),
    ], tabs=["数字", "对齐", "字体", "边框", "填充", "保护"], active="数字")
    marks_from(f, [
        ("combo:¥", "选中区域 →「数字格式」下拉 → 或按 Ctrl+1 开此框", "bottom", 34),
        ("cat", "分类选「数值」，小数位数 2", "right", 26),
        ("dec", "对齐选项卡里可设「自动换行」「合并单元格」", "right", 26),
    ])
    return f


def s4_3():
    """4.3 单元格引用与公式基础"""
    f, by = sheet_scene(title="成绩统计.xlsx - WPS 表格", tab="开始",
                        status="就绪　求和: 1617", data=GRADE)
    formula_bar(f, by, "F2", "=SUM(D2:D5)")
    cell_hit(f, 26 + 3 * 96, 170 + 22, 96, 88)
    f.at("rng", 26 + 3 * 96 + 48, 170 + 80)
    dx, dy = 470, 236
    funcdlg(f, dx, dy, 470, "函数参数", [("Number1", "D2:D5")], result="1617",
            note="D2:D5 为相对引用，向下填充会变成 D3:D6")
    marks_from(f, [
        ("addr", "名称框输入单元格地址，可快速定位", "right", 24),
        ("fxbar", "编辑栏以「=」开头输入公式，回车得到结果", "right", 24),
        ("p:Number1", "相对引用 D2 → 按 F4 变绝对引用 $D$2", "right", 26),
    ])
    return f


def s4_4():
    """4.4 数学统计函数与逻辑函数"""
    f, by = sheet_scene(title="成绩统计.xlsx - WPS 表格", tab="公式", groups=rib_et_formula(),
                        status="就绪　求和: 1617", data=GRADE)
    dx, dy = 380, 190
    dlg(f, dx, dy, 500, 300, "插入函数")
    f.txt(dx + 18, dy + 52, "搜索函数(S)", 11, K["txt2"])
    field(f, dx + 104, dy + 40, 220, "请输入函数名或功能描述", ph=True)
    btn(f, dx + 334, dy + 40, 62, "转到", 22)
    f.txt(dx + 18, dy + 92, "选择类别(C)", 11, K["txt2"])
    combo_box(f, dx + 104, dy + 80, 168, "数学与三角函数")
    f.txt(dx + 18, dy + 128, "选择函数(N)", 11, K["txt2"])
    f.rect(dx + 104, dy + 116, 168, 118, "#ffffff", K["fieldb"], 1, 1)
    for i, nm in enumerate(["SUM", "SUMIF", "SUMIFS", "ROUND", "INT", "ABS", "IF"]):
        yy = dy + 132 + i * 15
        on = nm == "SUM"
        if on:
            f.rect(dx + 106, yy - 11, 164, 15, K["blue2"], "none", 0, 0)
        f.txt(dx + 112, yy, nm, 10.5, K["blue"] if on else K["txt"])
    f.rect(dx + 288, dy + 116, 194, 118, "#fbfcfd", K["fieldb"], 1, 1)
    f.txt(dx + 296, dy + 134, "SUM(number1, [number2], …)", 9.2, K["txt3"])
    f.txt(dx + 296, dy + 152, "返回某一单元格区域中", 9.2, K["txt2"])
    f.txt(dx + 296, dy + 166, "所有数值之和。", 9.2, K["txt2"])
    f.at("cat", dx + 188, dy + 91)
    f.at("func", dx + 140, dy + 121)
    btn(f, dx + 336, dy + 258, 66, "确定", 24, True)
    btn(f, dx + 410, dy + 258, 66, "取消", 24)
    marks_from(f, [
        ("big:插入函数", "「公式」→「插入函数」，或直接点编辑栏左侧 fx", "bottom", 54),
        ("cat", "类别选「数学与三角函数」，下方列表随之筛选", "right", 24),
        ("func", "选中 SUM 后点确定，再到「函数参数」里框选区域", "right", 24),
    ])
    return f


def s5_1():
    """5.1 查找与引用函数"""
    data = dict(GRADE)
    data.update({(0, 6): "查询姓名", (1, 6): "王五", (0, 7): "总分"})
    f, by = sheet_scene(title="成绩查询.xlsx - WPS 表格", tab="公式", groups=rib_et_formula(),
                        status="就绪　计数: 4", data=data)
    formula_bar(f, by, "H2", "=VLOOKUP(G2,$A$2:$E$5,4,0)")
    dx, dy = 400, 186
    funcdlg(f, dx, dy, 500, "函数参数", [
        ("查找值", "G2"),
        ("数据表", "$A$2:$E$5"),
        ("列序数", "4"),
        ("匹配条件", "0"),
    ], result="#N/A", note="VLOOKUP(查找值, 数据表, 列序数, 匹配条件)", hi="数据表")
    marks_from(f, [
        ("big:插入函数", "「公式」→「插入函数」→ 类别选「查找与引用」→ VLOOKUP", "bottom", 54),
        ("p:数据表", "第二参数按 F4 锁定：$A$2:$E$5，否则下拉会错位", "right", 26),
        ("p:匹配条件", "第四参数填 0（精确匹配），省略会得到近似值", "right", 26),
    ])
    return f


def s5_2():
    """5.2 文本函数与日期时间函数"""
    f, by = sheet_scene(title="员工信息.xlsx - WPS 表格", tab="公式", groups=rib_et_formula(),
                        status="就绪　计数: 5",
                        data={(0, 0): "姓名", (0, 1): "入职日期", (0, 2): "工龄(年)", (0, 3): "显示文本",
                              (1, 0): "张三", (1, 1): "2019/7/1", (1, 2): "7", (1, 3): "2019年07月01日",
                              (2, 0): "李四", (2, 1): "2021/3/15", (2, 2): "5", (2, 3): "2021年03月15日",
                              (3, 0): "王五", (3, 1): "2023/9/8", (3, 2): "3", (3, 3): "2023年09月08日"})
    formula_bar(f, by, "D2", '=TEXT(B2,"yyyy年mm月dd日")')
    dx, dy = 420, 250
    funcdlg(f, dx, dy, 470, "函数参数", [
        ("数值", "B2"),
        ("格式文本", '"yyyy年mm月dd日"'),
    ], result="2019年07月01日", note="TEXT(数值, 格式文本)：把日期变成指定样式的文本")
    marks_from(f, [
        ("big:插入函数", "「公式」→「插入函数」→ 类别选「文本」→ TEXT", "bottom", 54),
        ("p:格式文本", "格式代码用英文双引号包住：yyyy 年、mm 月、dd 日", "right", 26),
        ("result", "结果靠左＝已变成文本；真日期靠右且可参与计算", "right", 26),
    ])
    return f


def s5_3():
    """5.3 数组公式与多条件统计"""
    f, by = sheet_scene(title="销售明细.xlsx - WPS 表格", tab="公式", groups=rib_et_formula(),
                        status="就绪　求和: 8600",
                        data={(0, 0): "月份", (0, 1): "部门", (0, 2): "金额", (0, 3): "达标",
                              (1, 0): "1 月", (1, 1): "研发", (1, 2): "3200", (1, 3): "是",
                              (2, 0): "1 月", (2, 1): "市场", (2, 2): "2100", (2, 3): "否",
                              (3, 0): "2 月", (3, 1): "研发", (3, 2): "5400", (3, 3): "是"})
    formula_bar(f, by, "F1", '=SUMIFS(C2:C4,A2:A4,"1 月",B2:B4,"研发")')
    dx, dy = 330, 240
    funcdlg(f, dx, dy, 540, "函数参数", [
        ("求和区域", "C2:C4"),
        ("区域 1", 'A2:A4 = "1 月"'),
        ("区域 2", 'B2:B4 = "研发"'),
    ], result="3200", note="条件成对出现：区域 1 对应条件 1，区域 2 对应条件 2，可继续添加")
    marks_from(f, [
        ("big:插入函数", "「公式」→ 插入 SUMIFS；多条件计数用 COUNTIFS", "bottom", 54),
        ("p:区域 1", "求和区域在前，后面「区域—条件」成对出现", "right", 26),
        ("result", "输入完成后按 Ctrl+Shift+Enter 生成数组公式（两端加 {}）", "right", 26),
    ])
    return f


def s5_4():
    """5.4 数据排序与筛选"""
    f, by = sheet_scene(title="成绩统计.xlsx - WPS 表格", tab="数据", groups=rib_et_data(),
                        status="就绪　筛选模式：4 条记录", data=GRADE)
    # 表头筛选按钮
    for c in range(5):
        bx = 26 + c * 96 + 96 - 14
        f.path("M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" % (bx, 170 + 8, bx + 8, 170 + 8, bx + 4, 170 + 14),
               "#7c8899", "none", 0.8)
    dx, dy = 430, 206
    form(f, dx, dy, 460, title="排序", rows=[
        ("c", [("主要关键字", "combo", "总分", 130, "k1", True)]),
        ("c", [("排序依据", "combo", "单元格值", 130)]),
        ("c", [("次序", "combo", "降序", 130)]),
        ("sep",),
        ("cb", "数据包含标题", True),
        ("cb", "区分大小写", False),
    ], buttons=("确定", "取消", "选项"))
    marks_from(f, [
        ("big:排序", "「数据」→「排序」：先选主要关键字，再设次序", "bottom", 54),
        ("k1", "主要关键字选「总分」，次序选「降序」", "right", 26),
        ("big:筛选", "「数据」→「筛选」后，表头出现下拉箭头", "bottom", 54),
    ])
    return f


def s6_1():
    """6.1 分类汇总、合并计算与数据有效性"""
    f, by = sheet_scene(title="销售明细.xlsx - WPS 表格", tab="数据", groups=rib_et_data(),
                        status="就绪　分级显示：2 级",
                        data={(0, 0): "部门", (0, 1): "月份", (0, 2): "金额",
                              (1, 0): "研发", (1, 1): "1 月", (1, 2): "3200",
                              (2, 0): "研发", (2, 1): "2 月", (2, 2): "5400",
                              (3, 0): "研发 汇总", (3, 1): "", (3, 2): "8600",
                              (4, 0): "市场", (4, 1): "1 月", (4, 2): "2100"})
    f.rect(26, 170 + 22 * 3, 480, 22, "#eef6ff", "none", 0, 0)
    dx, dy = 500, 208
    form(f, dx, dy, 440, title="分类汇总", rows=[
        ("c", [("分类字段(A)", "combo", "部门", 150, "f1", True)]),
        ("c", [("汇总方式(U)", "combo", "求和", 150)]),
        ("c", [("选定汇总项(S)", "field", "金额", 150, "f3")]),
        ("sep",),
        ("cb", "替换当前分类汇总", True),
        ("cb", "汇总结果显示在数据下方", True),
    ])
    marks_from(f, [
        ("big:分类汇总", "先按分类字段排序，再「数据」→「分类汇总」", "bottom", 54),
        ("f1", "分类字段＝部门，汇总方式＝求和，汇总项勾金额", "right", 26),
        ("f3", "「数据验证」→ 允许「序列」，做下拉选项", "right", 26),
    ])
    return f


def s6_2():
    """6.2 图表的创建、编辑与修饰"""
    f, by = sheet_scene(title="成绩统计.xlsx - WPS 表格", tab="插入", groups=rib_et_insert(),
                        status="就绪", data=GRADE)
    # 图表浮在数据右侧
    cx, cy, cw, ch = 560, 220, 380, 240
    shadow(f, cx, cy, cw, ch, 3, 0.14, 2)
    f.rect(cx, cy, cw, ch, "#ffffff", K["line2"], 1, 3)
    f.txt(cx + cw / 2, cy + 22, "各专业总分对比", 11, K["txt"], "middle", bold=True)
    base = cy + ch - 34
    for i, (nm, v) in enumerate([("会计学", 843), ("金融学", 396), ("营销", 378)]):
        bh = v / 900 * 130
        bx = cx + 54 + i * 96
        f.rect(bx, base - bh, 52, bh, "#4a7bd6", "none", 0, 0)
        f.txt(bx + 26, base - bh - 6, str(v), 8.6, K["txt2"], "middle")
        f.txt(bx + 26, base + 13, nm, 8.6, K["txt3"], "middle")
    f.line(cx + 34, base, cx + cw - 26, base, "#c8d0dc", 1)
    f.at("chart", cx + 100, cy + 120)
    marks_from(f, [
        ("big:图表", "选中数据区域 →「插入」→「图表」→ 柱形图", "bottom", 54),
        ("chart", "图表工具 →「选择数据」可改数据源与系列", "left", 26),
        ("big:筛选", "数据标签、坐标轴、图例在「图表工具」里逐项设置", "bottom", 54),
    ])
    return f


def s6_3():
    """6.3 数据透视表与数据透视图"""
    f, by = sheet_scene(title="销售明细.xlsx - WPS 表格", tab="插入", groups=rib_et_insert(),
                        status="就绪", data={(0, 0): "部门", (0, 1): "月份", (0, 2): "金额"},
                        )
    # 透视表结果
    cell_table(f, 330, 190, ["部门", "1 月", "2 月", "总计"], [
        ["研发", "3200", "5400", "8600"],
        ["市场", "2100", "1800", "3900"],
        ["总计", "5300", "7200", "12500"],
    ], rowh=24, colw=[80, 76, 76, 80], size=10.5,
        fills={(3, 0): "#eef2f8", (3, 1): "#eef2f8", (3, 2): "#eef2f8", (3, 3): "#eef2f8"})
    # 字段列表窗格
    px, py, pw, ph = 676, 182, 300, 300
    pane(f, px, py, pw, ph, "数据透视表字段")
    f.txt(px + 12, py + 48, "选择要添加到报表的字段", 10, K["txt3"])
    for i, nm in enumerate(["部门", "月份", "金额"]):
        check(f, px + 14, py + 58 + i * 24, nm, i < 2, 12)
    f.rect(px + 12, py + 142, pw - 24, 52, "#f7f9fc", K["fieldb"], 0.8, 2)
    f.txt(px + 20, py + 160, "行：部门", 10, K["txt2"])
    f.txt(px + 20, py + 178, "列：月份", 10, K["txt2"])
    f.at("pane", px + 150, py + 168)
    f.rect(px + 12, py + 200, pw - 24, 34, "#f7f9fc", K["fieldb"], 0.8, 2)
    f.txt(px + 20, py + 220, "值：求和项 金额", 10, K["txt2"])
    f.at("pane2", px + 150, py + 216)
    marks_from(f, [
        ("big:数据透视表", "选中数据 →「插入」→「数据透视表」→ 选放置位置", "bottom", 54),
        ("pane", "把「部门」拖到行、「月份」拖到列、「金额」拖到值", "left", 22),
        ("pane2", "值字段设置 → 求和 / 计数 / 平均值", "left", 22),
    ])
    return f


def s6_4():
    """6.4 模拟分析、安全性与打印输出"""
    f, by = sheet_scene(title="贷款测算.xlsx - WPS 表格", tab="页面", groups=rib_et_page(),
                        status="就绪",
                        data={(0, 0): "贷款额", (0, 1): "200000", (0, 2): "年利率", (0, 3): "4.90%",
                              (1, 0): "期限(月)", (1, 1): "240", (1, 2): "月供", (1, 3): "1308.89",
                              (2, 0): "利率", (2, 1): "", (2, 2): "月供", (2, 3): ""})
    menu(f, 560, by + 4, 254, [("head", "模拟分析"), ("单变量求解", ""), ("模拟运算表", ""),
                               ("方案管理器", "")], hi="单变量求解")
    dx, dy = 470, 300
    form(f, dx, dy, 420, title="保护工作表", rows=[
        ("c", [("密码(P)", "field", "••••••", 190, "pwd", True)]),
        ("cb", "允许选定锁定单元格", True),
        ("cb", "允许选定未锁定单元格", True),
        ("cb", "允许设置单元格格式", False),
    ])
    marks_from(f, [
        ("mi:单变量求解", "「数据」→「模拟分析」→ 单变量求解 / 模拟运算表", "right", 26),
        ("pwd", "「审阅」→「保护工作表」设密码，防改公式", "right", 26),
        ("big:打印标题", "「页面」→「打印标题」设顶端标题行，分页带表头", "bottom", 54),
    ])
    return f


def r_s():
    """第四章开头的成稿版式基准（合格工作表的要素）"""
    f = Fig(1000, 432)
    x, y, w = 40, 46, 490
    cols = [(0, 96, "部门"), (96, 78, "一季度"), (174, 78, "二季度"),
            (252, 78, "三季度"), (330, 88, "合计"), (418, 72, "完成率")]
    rows = [("华东", "1,286,400", "1,102,300", "1,463,800", "3,852,500", "108.6%"),
            ("华南", "986,200", "1,074,500", "1,218,600", "3,279,300", "96.2%"),
            ("华北", "742,800", "698,400", "916,200", "2,357,400", "84.1%"),
            ("西南", "518,600", "562,900", "604,300", "1,685,800", "58.3%"),
            ("东北", "396,400", "412,700", "489,500", "1,298,600", "72.9%")]
    # 合并标题行（A1:F1）
    f.rect(x, y, w, 30, "#dbe7f6", "#9fb4d0", 1)
    f.txt(x + w / 2, y + 20, "2026 年前三季度部门销售统计表", 12.5, "#1a2129", "middle", bold=True)
    f.at("mrg", x, y + 15)
    # 表头
    hy = y + 30
    for cx, cw, name in cols:
        f.rect(x + cx, hy, cw, 26, K["head"], K["grid"], 0.9)
        f.txt(x + cx + cw / 2, hy + 17, name, 10.4, K["txt2"], "middle", bold=True)
    # 数据行
    for ri, row in enumerate(rows):
        ry = hy + 26 + ri * 24
        for ci, (cx, cw, _) in enumerate(cols):
            f.rect(x + cx, ry, cw, 24, "#ffffff" if ri % 2 == 0 else "#fbfcfd", K["grid"], 0.9)
            if ci == 5:
                barw = min((cw - 10) * float(row[ci][:-1]) / 110.0, cw - 10)
                f.rect(x + cx + 5, ry + 5, barw, 14, "#cfe0ff", "none", 0, 2)
                f.txt(x + cx + cw - 6, ry + 16, row[ci], 9.6, K["txt"], "end")
            elif ci == 0:
                f.txt(x + cx + 8, ry + 16, row[ci], 9.6, K["txt"])
            else:
                f.txt(x + cx + cw - 7, ry + 16, row[ci], 9.6, K["txt"], "end")
    fy = hy + 26 + len(rows) * 24
    # 合计行：加粗 + 上方双线
    for cx, cw, _ in cols:
        f.rect(x + cx, fy, cw, 28, "#eef3fa", K["grid"], 0.9)
    f.txt(x + 8, fy + 18, "合计", 10, K["txt"], bold=True)
    for cx, cw, val in [(96, 78, "3,930,400"), (174, 78, "3,850,800"), (252, 78, "4,692,400"),
                        (330, 88, "12,473,600")]:
        f.txt(x + cx + cw - 7, fy + 18, val, 9.6, K["txt"], "end", bold=True)
    f.txt(x + 418 + 66, fy + 18, "84.2%", 9.6, K["txt"], "end", bold=True)
    f.line(x, fy - 2, x + w, fy - 2, "#5b6675", 1.2)
    f.line(x, fy + 1, x + w, fy + 1, "#5b6675", 0.8)
    f.at("sum", x, fy + 14)
    f.at("bar", x + w, hy + 26 + 3 * 24 + 12)

    # 下方：打印预览（两页，标题行重复）
    f.txt(x, 288, "打印预览：顶端标题行 $1:$2，分页后每页都带表头", 10.5, K["txt2"], bold=True)
    for k, lab in enumerate(["第 1 页", "第 2 页"]):
        mx = x + k * 168
        f.rect(mx, 298, 152, 112, "#ffffff", K["line2"], 0.9, 1)
        # 重复出现的标题行（浅蓝）
        f.rect(mx + 10, 306, 132, 11, "#dbe7f6", "#9fb4d0", 0.7)
        # 表头行
        for c in range(5):
            f.rect(mx + 10 + c * 26.4, 317, 26.4, 12, K["head"], K["grid"], 0.6)
        # 数据行
        for r in range(4):
            for c in range(5):
                f.rect(mx + 10 + c * 26.4, 329 + r * 15, 26.4, 15,
                       "#ffffff" if r % 2 == 0 else "#fbfcfd", K["grid"], 0.6)
        f.txt(mx + 76, 398, lab, 8.4, K["txt3"], "middle")
    f.at("prev", x + 76, 302)

    ty2 = spec_table(f, 596, 18, 384, [
        ("列宽", "部门列 12 字符，数值列 12 字符，全表统一"),
        ("数字", "#,##0.00；百分比 0.0%，不手打「元」"),
        ("条件格式", "完成率用数据条；<60% 浅红底突出"),
        ("合计", "=SUM(C3:C7)，上方加双线区分明细"),
        ("打印", "顶端标题行 $1:$2 + 页面水平居中"),
        ("命名", "工作表按内容改名，不留 Sheet1"),
    ], title="合格工作表的要素", rowh=29)
    f.txt(596, ty2 + 16, "先算数字、再定格式：数据错，格式再漂亮也不给分。", 10, K["txt3"])
    tip(f, 596, ty2 + 30, 384, "改格式前先选中整块区域，一步到位，别逐格调")
    tip(f, 596, ty2 + 62, 384, "交付前按 Ctrl+End 看最后一行，确认没有残留空行")

    marks_from(f, [
        ("mrg", "标题行合并居中（A1:F1），与表体空一行", "left", 28),
        ("bar", "条件格式 → 数据条，高低一眼看出", "right", 30),
        ("sum", "合计用 =SUM() 算，不手算不硬敲", "left", 28),
    ])
    return f


REG = {
    "s4_1": s4_1, "s4_2": s4_2, "s4_3": s4_3, "s4_4": s4_4,
    "s5_1": s5_1, "s5_2": s5_2, "s5_3": s5_3, "s5_4": s5_4,
    "s6_1": s6_1, "s6_2": s6_2, "s6_3": s6_3, "s6_4": s6_4,
    "r_s": r_s,
}
