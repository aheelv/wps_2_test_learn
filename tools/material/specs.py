# -*- coding: utf-8 -*-
"""八次课 72 道题的练习素材规格。

命名沿用参考包「Word练习素材-练习3-2至3-8」的约定：
    目录  练习N-M-题目短名/
    主文件 素材-练习N-M.docx | .xlsx | .pptx
    附件  按用途命名（图1-xxx.png / 初稿.docx / 新生名单.xlsx ...）
    说明  素材说明.txt
    下载  练习素材/下载/练习N-M-题目短名.zip

字段：
    short : 目录/压缩包短名
    kind  : docx / xlsx / pptx / ref（ref = 直接沿用参考包已生成内容）
    extra : 附加文件清单（由 build.py 按名字构造）
    refdir: kind=ref 时参考包中的原目录名
    topic : 无「录入素材」的题，生成初始正文时使用的主题句
"""

SPECS = {
    # ---------------- 第 1 次课 · 文字入门（16 题） ----------------
    (1, 1):  dict(short="新建与保存", kind="docx", topic="关于举办理工类实验技能竞赛的通知"),
    (1, 2):  dict(short="符号与上下标", kind="docx", topic="水的化学式为 H2O，面积单位记作 m2，勾股定理 a2+b2=c2"),
    (1, 3):  dict(short="选定与撤销", kind="docx", topic="段落一：WPS 文字支持鼠标拖选、双击选词、三击选段。段落二：Ctrl+Z 撤销，Ctrl+Y 恢复。"),
    (1, 4):  dict(short="页面设置与输出", kind="docx", topic="2026 年春季学期教学资料（待设置页面、输出 PDF 并加密）"),
    (1, 5):  dict(short="通知标题格式", kind="docx", topic="关于开展 2026 年暑期实训的通知"),
    (1, 6):  dict(short="段落格式", kind="docx", topic="关于开展 2026 年暑期实训的通知"),
    (1, 7):  dict(short="字符格式与格式刷", kind="docx", topic="排版规范：标题、正文、重点词句的统一格式"),
    (1, 8):  dict(short="编号与边框底纹", kind="docx", topic="实训报名须知（待设置自动编号、项目符号与段落边框底纹）"),
    (1, 9):  dict(short="样式套用与修改", kind="docx", topic="毕业论文正文样式统一说明"),
    (1, 10): dict(short="查找替换三连", kind="docx", topic="关于开展 2026 年暑期实训的通知（含待替换词与多余空行）"),
    (1, 11): dict(short="分栏与首字下沉", kind="docx", topic="校园通讯：实训基地建设纪实"),
    (1, 12): dict(short="水印与页面边框", kind="docx", topic="内部资料：2026 年实训教学安排"),
    (1, 13): dict(short="分节与页眉页脚", kind="docx", topic="2026 年实训报告（封面 + 正文，待分节设置页码）"),
    (1, 14): dict(short="表格制作", kind="docx", topic="2026 年春季学期成绩登记表（待插入 5 行 4 列表格）"),
    (1, 15): dict(short="图片与文本框", kind="docx", extra=["图1-实训基地.png"], topic="实训基地简介（待插入图片并设置环绕）"),
    (1, 16): dict(short="报名通知综合题", kind="docx", topic="关于 2026 年暑期实训报名的通知（综合排版）"),

    # ---------------- 第 2 次课 · 文字进阶（8 题） ----------------
    (2, 1): dict(short="奇偶页页眉", kind="docx", topic="区域物流需求预测方法研究（毕业论文初稿）"),
    (2, 2): dict(short="标书分节与页码", kind="docx", topic="智慧校园数据中心建设项目投标文件"),
    (2, 3): dict(short="表格边框与底纹", kind="docx", topic="2026 年春季学期学生成绩表"),
    (2, 4): dict(short="表格公式与排序", kind="docx", topic="课程总评成绩表（待用表格公式计算总评）"),
    (2, 5): dict(short="图片环绕与组合", kind="docx", extra=["图1-实训场景.png"], topic="实训基地图文介绍（待插入图片并设四周型环绕）"),
    (2, 6): dict(short="流程图与智能图形", kind="docx", topic="报名流程说明（待用形状绘制流程图）"),
    (2, 7): dict(short="文本框链接与域", kind="docx", topic="实训简报（待插入竖排文本框并建立链接）"),
    (2, 8): dict(short="数学公式", kind="docx", topic="数值分析公式示例（待用公式编辑器录入分式、根式、定积分与矩阵）"),

    # ---------------- 第 3 次课 · 长文档与协作（8 题） ----------------
    (3, 1): dict(short="多级列表与目录", kind="docx", topic="毕业论文正文：含一、二级标题与三级标题，待链接多级列表并生成 3 级目录"),
    (3, 2): dict(short="题注与交叉引用", kind="ref", refdir="练习3-2-题注与交叉引用"),
    (3, 3): dict(short="脚注与尾注", kind="ref", refdir="练习3-3-脚注与尾注"),
    (3, 4): dict(short="引文与索引", kind="ref", refdir="练习3-4-引文与索引"),
    (3, 5): dict(short="修订与批注", kind="ref", refdir="练习3-5-修订与批注"),
    (3, 6): dict(short="文档比较与保护", kind="ref", refdir="练习3-6-文档比较与保护"),
    (3, 7): dict(short="邮件合并", kind="ref", refdir="例3-7-邮件合并"),
    (3, 8): dict(short="多窗口协作", kind="ref", refdir="例3-8-多窗口协作"),

    # ---------------- 第 4 次课 · 表格基础（8 题） ----------------
    # 例 4-1 题干声明「日期 / 产品 / 数量 / 单价 / 金额，共 12 条」，且要求从 Sheet1
    # 开始建表；使用专用数据集、不预置「题目说明」表，保证素材与题目要求一致。
    (4, 1): dict(short="工作簿与工作表", kind="xlsx", dataset="sales12", no_note=True),
    (4, 2): dict(short="打印区域与标题行", kind="xlsx", dataset="sales"),
    (4, 3): dict(short="数据录入与格式", kind="xlsx", dataset="staff"),
    (4, 4): dict(short="条件格式与批注", kind="xlsx", dataset="score"),
    (4, 5): dict(short="单元格引用", kind="xlsx", dataset="sales"),
    (4, 6): dict(short="公式与错误排查", kind="xlsx", dataset="sales"),
    (4, 7): dict(short="统计与取整函数", kind="xlsx", dataset="score"),
    (4, 8): dict(short="IF与逻辑函数", kind="xlsx", dataset="score"),

    # ---------------- 第 5 次课 · 表格函数（8 题） ----------------
    (5, 1): dict(short="查找引用函数", kind="xlsx", dataset="lookup"),
    (5, 2): dict(short="反向查找与动态引用", kind="xlsx", dataset="lookup"),
    (5, 3): dict(short="身份证与文本函数", kind="xlsx", dataset="idcard"),
    (5, 4): dict(short="日期与工作日函数", kind="xlsx", dataset="staff"),
    (5, 5): dict(short="多条件求和", kind="xlsx", dataset="sales"),
    (5, 6): dict(short="排名与统计分布", kind="xlsx", dataset="score"),
    (5, 7): dict(short="排序与筛选", kind="xlsx", dataset="sales"),
    (5, 8): dict(short="高级筛选", kind="xlsx", dataset="sales"),

    # ---------------- 第 6 次课 · 表格分析（8 题） ----------------
    (6, 1): dict(short="分类汇总", kind="xlsx", dataset="sales"),
    (6, 2): dict(short="合并计算与有效性", kind="xlsx", dataset="sales"),
    (6, 3): dict(short="组合图表双轴", kind="xlsx", dataset="trend"),
    (6, 4): dict(short="饼图与迷你图", kind="xlsx", dataset="share"),
    (6, 5): dict(short="数据透视表", kind="xlsx", dataset="sales"),
    (6, 6): dict(short="透视图与切片器", kind="xlsx", dataset="sales"),
    (6, 7): dict(short="模拟分析与方案", kind="xlsx", dataset="loan"),
    (6, 8): dict(short="保护与打印输出", kind="xlsx", dataset="sales"),

    # ---------------- 第 7 次课 · 演示基础（8 题） ----------------
    (7, 1): dict(short="从大纲生成幻灯片", kind="pptx", extra=["大纲.txt"], slides=1),
    (7, 2): dict(short="视图与备注", kind="pptx", slides=8),
    (7, 3): dict(short="主题与背景", kind="pptx", extra=["图1-封面背景.png"], slides=8),
    (7, 4): dict(short="幻灯片母版", kind="pptx", extra=["图1-校徽logo.png"], slides=8),
    (7, 5): dict(short="艺术字与文本效果", kind="pptx", slides=8),
    (7, 6): dict(short="形状与智能图形", kind="pptx", slides=6),
    (7, 7): dict(short="图片处理与相册", kind="pptx",
                 extra=["图1-校园全景.png", "图2-实训车间.png", "图3-图书馆.png"], slides=6),
    # 例 7-8 需要「素材视频」，题目按第 7 张操作；移除与题目无关的「图表数据.xlsx」
    (7, 8): dict(short="图表与音视频", kind="pptx",
                 extra=["背景音乐.wav", "教学视频.mp4"], slides=8),

    # ---------------- 第 8 次课 · 演示输出（8 题） ----------------
    (8, 1): dict(short="对象动画", kind="pptx", slides=6),
    (8, 2): dict(short="切换与排练计时", kind="pptx", slides=6),
    (8, 3): dict(short="超链接与动作", kind="pptx", slides=8),
    (8, 4): dict(short="放映设置", kind="pptx", slides=8),
    (8, 5): dict(short="打包与输出", kind="pptx", slides=6),
    (8, 6): dict(short="文档保护与检查", kind="pptx", slides=6),
    (8, 7): dict(short="六页汇报综合题", kind="pptx", slides=6),
    (8, 8): dict(short="限时模拟与自评", kind="pptx", extra=["评分表.xlsx"], slides=6),
}

KIND_BY_CI = {1: "docx", 2: "docx", 3: "docx", 4: "xlsx", 5: "xlsx", 6: "xlsx", 7: "pptx", 8: "pptx"}
MODULE = {1: "WPS 文字", 2: "WPS 文字", 3: "WPS 文字",
          4: "WPS 表格", 5: "WPS 表格", 6: "WPS 表格",
          7: "WPS 演示", 8: "WPS 演示"}

ENV = "WPS Office 教育考试专用版（2025 年版考试大纲指定考试环境）"
