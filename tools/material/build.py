# -*- coding: utf-8 -*-
"""生成八次课 72 道题的完整练习素材包。

输出结构（工作区根目录下）：
    练习素材/
        README.txt                      全套总说明
        练习N-M-题目短名/                每题一个目录
            素材-练习N-M.docx|xlsx|pptx  主素材（多文档题按用途命名）
            附件...                      图片 / 数据源 / 大纲 / 评分表
            素材说明.txt                 文件清单 + 题目要求 + 最终效果 + 环境
        下载/
            练习N-M-题目短名.zip         每题一个可下载压缩包
"""
import os, sys, re, json, shutil, zipfile, html as H, math, wave, struct
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from specs import SPECS, MODULE, ENV

ROOT = Path(__file__).resolve().parents[2]
REF = Path(r"D:\workbuddy\wps_2_test_learn-main\Word练习素材-练习3-2至3-8")
OUT = ROOT / "练习素材"
DL = OUT / "下载"
ASSETS = Path(__file__).resolve().parent / "assets"   # 固定二进制素材（教学视频.mp4 等）
DATA = json.load(open(Path(__file__).parent / "exercises.json", encoding="utf-8"))
BY = {(e["ci"], e["seq"]): e for e in DATA}


TAG_RE = re.compile(r"</?[A-Za-z][^>]*>")   # 只剥真实标签，保留 <=79 / <60 等比较符


def clean(s):
    return re.sub(r"\s+", " ", H.unescape(TAG_RE.sub("", s))).strip()


# 网页未写 <div class="score"> 时，用网页自评表 / 题目要求补齐「完成效果」，
# 保证 72 个包的素材说明都含该段（校验项：包内文件与说明完整性）。
SCORE_FALLBACK = {
    (1, 16): "按网页 10 项评分表（共 30 分）逐项自评：① 文件名、扩展名、文件夹三者全对；"
             "② 大标题黑体二号居中、段后 1 行且用样式；③ 三个小标题都套「标题2」，导航窗格可见；"
             "④ 正文宋体小四、首行缩进 2 字符（非空格）、1.5 倍行距；⑤ 自动编号与项目符号，不是手打；"
             "⑥ 4 行 3 列表格、表头底纹加粗居中、所有框线、表格居中；⑦ 图片四周型环绕宽 6 厘米、图注在下；"
             "⑧ A4 与四个页边距、页眉居中、页脚「第 X 页」；⑨ 自动目录单独一页、可跳转、页码正确；"
             "⑩ 同名同目录 PDF 打开无乱码。≥ 24 分视为通过本模块入门要求。",
}


# ---------------------------------------------------------------- 数据集
def ds_sales():
    """销售明细：部门/季度/产品/数量/单价/金额（金额留空由学生用公式计算）"""
    rows = [["订单号", "部门", "季度", "产品", "数量", "单价", "金额"]]
    dep = ["华东", "华南", "华北", "西南"]
    q = ["Q1", "Q2", "Q3", "Q4"]
    prod = ["A 型设备", "B 型耗材", "C 型配件"]
    for i in range(20):
        rows.append(["D%04d" % (1001 + i), dep[i % 4], q[i % 4], prod[i % 3],
                     6 + (i * 3) % 25, 1200 + (i * 7) % 9 * 100, ""])
    return {"销售明细": rows}


def ds_staff():
    rows = [["工号", "姓名", "部门", "入职日期", "月薪", "学历"]]
    names = ["王雨桐", "李文博", "赵思远", "陈嘉懿", "周泓然", "孙浩然", "吴梦琪", "郑一鸣",
             "冯晓宁", "蒋博文", "韩若彤", "许嘉树", "何雨泽", "吕思颖", "施宇辰", "张沐阳",
             "孔令仪", "曹译文", "严思齐", "华梓涵"]
    deps = ["财务部", "市场部", "技术部", "人力资源部"]
    deg = ["本科", "硕士", "博士"]
    for i, nm in enumerate(names):
        rows.append(["%06d" % (1 + i), nm, deps[i % 4], "2019-%02d-%02d" % (1 + i % 12, 1 + i % 28),
                     6000 + (i * 7) % 13 * 500, deg[i % 3]])
    return {"员工信息": rows}


def ds_score():
    rows = [["学号", "姓名", "语文", "数学", "英语", "总分", "平均分", "等级"]]
    names = ["张一诺", "李思远", "王语桐", "赵子墨", "陈嘉禾", "刘沐阳", "杨雨澄", "黄亦辰",
             "周可欣", "吴致远", "徐若涵", "孙博文", "马语晨", "朱景行", "胡安宁", "林清越",
             "何嘉树", "郭一鸣", "高思颖", "罗展鹏"]
    for i, nm in enumerate(names):
        a, b, c = 62 + (i * 7) % 36, 55 + (i * 11) % 44, 68 + (i * 5) % 30
        rows.append(["20230%03d" % (101 + i), nm, a, b, c, "", "", ""])
    return {"成绩表": rows}


def ds_org():
    return {
        "部门一览": [["部门编号", "部门名称", "负责人", "人数"],
                 ["D01", "财务部", "王雨桐", 8], ["D02", "市场部", "李文博", 12],
                 ["D03", "技术部", "赵思远", 15], ["D04", "人力资源部", "陈嘉懿", 6]],
        "一季度": [["产品", "销量", "单价"]] + [["A 型设备", 120, 1200], ["B 型耗材", 260, 380], ["C 型配件", 180, 560]],
        "二季度": [["产品", "销量", "单价"]] + [["A 型设备", 138, 1200], ["B 型耗材", 245, 380], ["C 型配件", 205, 560]],
        "三季度": [["产品", "销量", "单价"]] + [["A 型设备", 151, 1200], ["B 型耗材", 288, 380], ["C 型配件", 226, 560]],
    }


def ds_lookup():
    base = ds_score()["成绩表"]
    stu = [["学号", "姓名", "专业", "班级"]]
    major = ["会计学", "金融学", "市场营销", "信息管理"]
    for i in range(1, len(base)):
        stu.append([base[i][0], base[i][1], major[i % 4], "2023 级 %d 班" % (1 + i % 3)])
    q = [["查询学号", "20230105"], ["姓名", ""], ["专业", ""], ["总分", ""], ["绩点", ""]]
    return {"学生档案": stu, "成绩数据": [r[:6] for r in base], "查询区": q}


def ds_idcard():
    rows = [["序号", "姓名", "身份证号", "联系电话", "出生日期", "性别", "年龄"]]
    names = ["张一诺", "李思远", "王语桐", "赵子墨", "陈嘉禾", "刘沐阳", "杨雨澄", "黄亦辰"]
    for i, nm in enumerate(names):
        # 教学用虚构号码，仅满足 18 位结构与校验位可解的结构，不含真实个人信息
        rows.append([i + 1, nm, "21020219%02d%02d%02d%04d" % (90 + i, 1 + i % 12, 1 + i % 28, 1001 + i * 137),
                     "138%08d" % (10000000 + i * 111111), "", "", ""])
    return {"身份信息": rows}


def ds_trend():
    rows = [["月份", "销售额", "增长率"]]
    vals = [128, 136, 145, 141, 158, 172, 168, 185, 196, 203, 215, 228]
    for i, v in enumerate(vals):
        rows.append(["%d 月" % (i + 1), v, "" if i == 0 else ""])
    return {"月度趋势": rows}


def ds_share():
    return {"品类占比": [["品类", "销售额"],
                     ["A 型设备", 1286400], ["B 型耗材", 986200], ["C 型配件", 742800],
                     ["D 型服务", 518600], ["E 型其他", 396400]]}


def ds_loan():
    return {"贷款测算": [["项目", "数值", "说明"],
                     ["贷款总额", 200000, "元"],
                     ["年利率", 0.049, "4.90%"],
                     ["期限（月）", 240, "20 年"],
                     ["月供", "", "由 PMT 计算"],
                     ["还款总额", "", "月供 × 期数"],
                     ["总利息", "", "还款总额 − 贷款总额"]],
            "利率敏感性": [["月供 \\ 年利率", 0.045, 0.049, 0.053]]}


def ds_sales12():
    """例 4-1 专用：题干声明的表头与 12 条记录（金额列留空，不预置答案）。

    表头：日期 | 产品 | 数量 | 单价 | 金额
    记录示例：2026-09-01 | 笔记本 | 12 | 4580 |
    共 12 条，日期按天递增，产品在笔记本 / 台式机 / 显示器 / 键盘中轮换。
    """
    rows = [["日期", "产品", "数量", "单价", "金额"]]
    prod = ["笔记本", "台式机", "显示器", "键盘"]
    for i in range(12):
        rows.append(["2026-09-%02d" % (1 + i), prod[i % 4],
                     12 + (i * 3) % 9, 4580 + (i * 5) % 6 * 100, ""])
    return {"Sheet1": rows}


DATASETS = {"sales": ds_sales, "staff": ds_staff, "score": ds_score, "org": ds_org,
            "lookup": ds_lookup, "idcard": ds_idcard, "trend": ds_trend,
            "share": ds_share, "loan": ds_loan, "sales12": ds_sales12}


# ---------------------------------------------------------------- 文档生成
def doc_font(run, size=12):
    from docx.oxml.ns import qn
    from docx.shared import Pt
    run.font.name = "宋体"
    run.font.size = Pt(size)
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")


def make_docx(path, e, spec):
    from docx import Document
    from docx.shared import Cm, Pt
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    d = Document()
    sec = d.sections[0]
    sec.page_width, sec.page_height = Cm(21), Cm(29.7)
    sec.top_margin = sec.bottom_margin = sec.left_margin = sec.right_margin = Cm(2.5)
    st = d.styles["Normal"]
    st.font.name, st.font.size = "宋体", Pt(12)
    st.paragraph_format.line_spacing = 1.5
    from docx.oxml.ns import qn
    st.element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")

    title = "【%s 练习素材】%s" % (e["no"], e["title"])
    p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc_font(p.add_run(title), 14)
    p.runs[0].bold = True

    body = clean(e["src"]) if e["src"] else ""
    lines = [x.strip() for x in re.split(r"[\n\r]+", body) if x.strip()]
    if not lines:
        t = spec.get("topic", e["title"])
        lines = [
            t,
            "本文件为第 %d 次课「%s」的起始素材。请按网页中的题目要求，在 WPS 文字中完成全部操作。" % (e["ci"], e["title"]),
            "素材仅提供未经排版的原始文字，字体、段落、样式、页眉页脚、题注、目录等格式效果均需按题目要求自行设置，不在素材中预置。",
            "原始文字：2026 年春季学期，学院围绕计算机应用能力培养组织了系列实训。实训以项目任务为主线，"
            "覆盖文档排版、数据处理与演示汇报三个模块，学生需在规定时间内独立完成并提交作品。",
            "第二组文字：数据表明，参与实训的学生在格式规范、函数运用与版式设计三项指标上均有明显提升，"
            "其中格式规范一项提升最为显著。指导教师建议后续增加长文档协作与批量处理的训练比重。",
        ]
    for i, line in enumerate(lines):
        p = d.add_paragraph()
        p.paragraph_format.space_after = Pt(6)
        doc_font(p.add_run(line), 12)

    d.add_paragraph()
    p = d.add_paragraph()
    doc_font(p.add_run("（素材文件结束。请勿在本文件上预置答案效果；完成后按题目要求另存为「学号-姓名-练习%s-%d.docx」。）"
                       % (e["ci"], e["seq"])), 10)
    d.save(str(path))


def make_xlsx(path, e, spec):
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
    ds = DATASETS[spec.get("dataset", "sales")]()
    wb = Workbook(); wb.remove(wb.active)
    head_fill = PatternFill("solid", fgColor="DCE6F1")
    thin = Side(style="thin", color="B7C3D1")
    for name, rows in ds.items():
        ws = wb.create_sheet(name[:30])
        for r in rows:
            ws.append(r)
        for c in range(1, len(rows[0]) + 1):
            cell = ws.cell(row=1, column=c)
            cell.font = Font(name="宋体", size=11, bold=True)
            cell.fill = head_fill
            cell.alignment = Alignment(horizontal="center", vertical="center")
            ws.column_dimensions[get_column_letter(c)].width = max(12, min(24, len(str(rows[0][c - 1])) * 2 + 8))
        for row in ws.iter_rows(min_row=2):
            for cell in row:
                cell.font = Font(name="宋体", size=11)
                cell.border = Border(bottom=thin)
        ws.freeze_panes = "A2"
        ws.row_dimensions[1].height = 22
    # 说明页：记录本题需要做哪些动作（但不代做）
    # 从零建表的题（例 4-1）只保留 Sheet1，避免素材预置多余工作表与题目要求冲突。
    if not spec.get("no_note"):
        note = wb.create_sheet("题目说明", 0)
        note.append(["题号", e["no"]]); note.append(["模块", MODULE[e["ci"]]])
        note.append(["题目", e["title"]]); note.append(["起始文件", path.name])
        note.append(["说明", "本工作簿只提供原始数据；公式、函数、条件格式、图表、透视表、排序筛选等均按网页题目要求自行完成。"])
        note.column_dimensions["A"].width = 14; note.column_dimensions["B"].width = 96
        for r in note.iter_rows():
            for c in r: c.font = Font(name="宋体", size=11)
    wb.save(str(path))


def make_pptx(path, e, spec):
    from pptx import Presentation
    from pptx.util import Inches, Pt as PPt
    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
    n = spec.get("slides", 6)
    titles = ["2026 年春季实训成果汇报", "目录", "一、实训背景与目标", "二、实施过程",
              "三、数据结果", "四、问题与改进", "五、下一步计划", "结束页"]
    bullets = ["覆盖文档排版、数据处理与演示汇报三个模块", "以项目任务为主线，按周推进",
               "共 8 次课、32 小节、72 道实操题", "操作题按点给分，过程与结果都要留痕"]
    for i in range(n):
        if i == 0:
            s = prs.slides.add_slide(prs.slide_layouts[0])
            s.shapes.title.text = titles[0]
            s.placeholders[1].text = "第 %d 次课 · %s ｜ 起始素材" % (e["ci"], e["title"][:24])
        elif i == n - 1:
            s = prs.slides.add_slide(prs.slide_layouts[1])
            s.shapes.title.text = "谢谢观看"
            s.placeholders[1].text = "请按题目要求完成动画、切换、链接与输出设置"
        else:
            s = prs.slides.add_slide(prs.slide_layouts[1])
            s.shapes.title.text = titles[min(i, len(titles) - 1)]
            s.placeholders[1].text = "\n".join(bullets[(i - 1) % 4:(i - 1) % 4 + 3])
        for sh in s.shapes:
            if sh.has_text_frame:
                for p in sh.text_frame.paragraphs:
                    for r in p.runs:
                        r.font.size = PPt(24 if sh == s.shapes.title else 18)
    prs.save(str(path))


def make_png(path, label="配图"):
    from PIL import Image, ImageDraw, ImageFont
    W, Hp = 1200, 760
    im = Image.new("RGB", (W, Hp), "#f7f9fc")
    dr = ImageDraw.Draw(im)
    fp = None
    for cand in [r"C:\Windows\Fonts\msyh.ttc", r"C:\Windows\Fonts\simhei.ttf", r"C:\Windows\Fonts\simsun.ttc"]:
        if os.path.exists(cand): fp = cand; break
    def font(sz):
        return ImageFont.truetype(fp, sz) if fp else ImageFont.load_default()
    dr.rectangle([20, 20, W - 20, Hp - 20], outline="#c8d4e4", width=2)
    dr.text((48, 40), label, fill="#1c4ed8", font=font(34))
    # 教学示意：柱状图
    base, vals = Hp - 90, [180, 265, 210, 330, 290, 370, 315]
    for i, v in enumerate(vals):
        x = 110 + i * 140
        dr.rectangle([x, base - v, x + 82, base], fill="#5b8fe0" if i % 2 == 0 else "#8fb3e8", outline="#3f6db5")
        dr.text((x + 16, base - v - 34), str(v), fill="#33404e", font=font(20))
    dr.line([70, base, W - 70, base], fill="#8a97a8", width=2)
    dr.text((48, Hp - 62), "教学示意图 · 自拟数据 · 300dpi 输出", fill="#6b7683", font=font(18))
    im.save(str(path), dpi=(300, 300))


def make_wav(path):
    sr, dur, freq = 22050, 3, 440.0
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        for i in range(sr * dur):
            v = int(9000 * math.sin(2 * math.pi * freq * i / sr) *
                    (0.3 + 0.7 * min(1.0, i / (sr * 0.2))))
            w.writeframesraw(struct.pack("<h", v))


def make_aux_xlsx(path, kind, e):
    from openpyxl import Workbook
    from openpyxl.styles import Font
    wb = Workbook(); ws = wb.active
    if kind == "图表数据":
        ws.title = "图表数据"
        ws.append(["月份", "销售额", "增长率"])
        for i, v in enumerate([128, 136, 145, 141, 158, 172, 168, 185]):
            ws.append(["%d 月" % (i + 1), v, "" if i == 0 else round((v / [128, 136, 145, 141, 158, 172, 168, 185][i - 1] - 1) * 100, 1)])
    else:
        # 例 8-8 的自评对象是第 8-7 题的 10 项采分点，题目规定每项 2 分、满分 20 分。
        # 旧版按本题 5 条要求 × 5 分生成，与题目要求不符，此处改为按 8-7 采分点生成。
        ws.title = "自评表"
        ws.append(["评分项", "满分", "自评分", "备注"])
        q87 = next((x for x in DATA if (x["ci"], x["seq"]) == (8, 7)), None)
        score87 = clean(q87["score"]) if q87 else ""
        score87 = re.sub(r"^采分点\s*", "", score87)
        items = [x.strip(" ·") for x in re.split(r"[①②③④⑤⑥⑦⑧⑨⑩]", score87)
                 if x.strip(" ·")]
        for j, t in enumerate(items[:10], 1):
            ws.append(["%d. %s" % (j, t[:52]), 2, "", ""])
        ws.append(["合计", len(items[:10]) * 2, "", ""])
    for row in ws.iter_rows():
        for c in row: c.font = Font(name="宋体", size=11)
    for i in range(1, 5): ws.column_dimensions[chr(64 + i)].width = 22
    wb.save(str(path))


def make_outline(path, e):
    # 与例 7-1 题干「录入素材」声明的 8 条大纲完全一致：
    # 8 个一级标题 → 从大纲导入后生成 8 张幻灯片（1 张标题 + 7 张内容）。
    lines = ["大数据时代的企业决策", "数据从哪里来", "数据质量的三道关",
             "从描述到预测", "可视化不是画图", "常见误区", "行动建议", "谢谢"]
    path.write_text("\n".join(lines), encoding="utf-8")


# ---------------------------------------------------------------- 包组装
def readme_text(e, spec, files, folder_name):
    L = []
    L.append("=" * 64)
    L.append("练习素材包：%s" % folder_name)
    L.append("=" * 64)
    L.append("题号：%s" % e["no"])
    L.append("题目：%s" % e["title"])
    L.append("归属：第 %d 次课 / %s ｜ 网页：%s" % (e["ci"], MODULE[e["ci"]], e["page"]))
    L.append("考试环境：%s" % ENV)
    L.append("")
    L.append("【文件清单】")
    for fn, use in files:
        L.append("  · %-34s %s" % (fn, use))
    L.append("")
    L.append("【题目要求】")
    for i, r in enumerate(e["reqs"], 1):
        L.append("  %2d. %s" % (i, clean(r)))
    L.append("")
    score = e.get("score")
    if score:
        score = clean(score).replace("采分点", "", 1)
    else:
        score = SCORE_FALLBACK.get(
            (e["ci"], e["seq"]),
            "按上述 %d 项题目要求逐项完成，成稿与网页「完成效果」配图及解题步骤一致。" % len(e["reqs"]))
    L.append("【完成效果 / 采分点】")
    L.append("  " + score)
    L.append("")
    L.append("【素材说明】")
    L.append("  1. 所有答案动作（格式、公式、图表、动画、修订、目录、题注等）均不在素材中预置，")
    L.append("     请按网页「解题步骤」在素材上完成，保证练习可操作性。")
    L.append("  2. 解题步骤中的「打开素材」「新建文件」均以本包内的起始文件为操作对象；")
    L.append("     如需从零新建，请以本包文字/数据为录入内容，参数与题目要求保持一致。")
    L.append("  3. 数据均为自拟教学数据，不含真实个人信息；完成后按题目要求另存为")
    L.append("     「学号-姓名-练习%d-%d」加对应扩展名。" % (e["ci"], e["seq"]))
    L.append("  4. docx 统一 A4、上下左右 2.5cm 页边距、宋体正文 12pt、1.5 倍行距；图片 300dpi。")
    L.append("")
    L.append("【功能入口口径】")
    L.append("  WPS 文字 / WPS 表格 / WPS 演示；选项卡名按 WPS Office 教育考试专用版现行界面：")
    L.append("  文件 · 开始 · 插入 · 页面 · 引用 · 审阅 · 视图 · 工具（模块专属选项卡随对象出现）。")
    L.append("=" * 64)
    return "\n".join(L) + "\n"


def build_one(e, spec):
    ci, seq = e["ci"], e["seq"]
    folder = "练习%d-%d-%s" % (ci, seq, spec["short"])
    dest = OUT / folder
    if dest.exists(): shutil.rmtree(dest)
    dest.mkdir(parents=True)
    files = []   # (文件名, 用途)

    if spec["kind"] == "ref":
        src = REF / spec["refdir"]
        if not src.exists():
            raise RuntimeError("参考素材缺失：%s" % src)
        for p in sorted(src.iterdir()):
            if p.is_file():
                shutil.copy2(p, dest / p.name)
                files.append((p.name, ref_use(p.name, e)))
    else:
        kind = spec["kind"]
        main = "素材-练习%d-%d.%s" % (ci, seq, kind)
        p = dest / main
        {"docx": make_docx, "xlsx": make_xlsx, "pptx": make_pptx}[kind](p, e, spec)
        files.append((main, "起始素材（%s）：解题步骤的操作对象" % MODULE[ci]))
        for extra in spec.get("extra", []):
            ep = dest / extra
            if extra.endswith(".png"):
                make_png(ep, extra.rsplit(".", 1)[0].replace("-", " · "))
            elif extra.endswith(".wav"):
                make_wav(ep)
            elif extra == "大纲.txt":
                make_outline(ep, e)
            elif extra.endswith(".xlsx"):
                make_aux_xlsx(ep, extra.split(".")[0], e)
            elif extra.endswith(".mp4"):
                if not (ASSETS / extra).exists():
                    raise RuntimeError("固定视频素材缺失：%s" % (ASSETS / extra))
                shutil.copy2(ASSETS / extra, ep)
            else:
                raise RuntimeError("未知附件类型：" + extra)
            files.append((extra, extra_use(extra)))

    (dest / "素材说明.txt").write_text(readme_text(e, spec, files, folder), encoding="utf-8")
    files.append(("素材说明.txt", "文件清单 / 题目要求 / 完成效果 / 环境口径"))

    DL.mkdir(parents=True, exist_ok=True)
    zp = DL / (folder + ".zip")
    if zp.exists(): zp.unlink()
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for fn, _ in files:
            z.write(dest / fn, arcname=folder + "/" + fn)
    return folder, files, zp


def ref_use(fn, e):
    if fn.startswith("素材-") or fn in ("初稿.docx", "修改稿.docx"):
        return "起始素材（WPS 文字）：解题步骤的操作对象"
    if fn.endswith(".png"):
        return "配图源文件：供按题目要求插入/重新插图"
    if fn.endswith(".xlsx"):
        return "数据源：邮件合并 / 图表等操作的记录源"
    if "素材A" in fn: return "并排比较与「保留源格式」复制的来源文档"
    if "素材B" in fn: return "含目录域与自动编号的目标文档"
    if "主文档" in fn: return "邮件合并主文档占位模板"
    return "配套素材"


def extra_use(fn):
    if fn.endswith(".png"): return "图片源文件：供按题目要求插入并设置环绕/裁剪/背景"
    if fn.endswith(".wav"): return "音频源文件：供插入并测试跨页播放"
    if fn.endswith(".mp4"): return "视频源文件：供插入并设置自动播放 / 全屏播放"
    if fn == "大纲.txt": return "大纲文本：供「从大纲生成幻灯片」导入"
    if "图表数据" in fn: return "图表数据源：供编辑图表数据"
    if "评分表" in fn: return "自评评分表：限时模拟后逐项打分"
    return "配套素材"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for e in DATA:
        key = (e["ci"], e["seq"])
        spec = SPECS[key]
        folder, files, zp = build_one(e, spec)
        rows.append(dict(no=e["no"], ci=e["ci"], seq=e["seq"], title=e["title"],
                         page=e["page"], folder=folder, zip=zp.name,
                         files=[f for f, _ in files], module=MODULE[e["ci"]]))
        print("%-9s %s" % (e["no"], folder))
    json.dump(rows, open(Path(__file__).parent / "manifest.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    total = ["八次课实操练习素材包 · 总说明", "=" * 64, "",
             "适用范围：实操训练 8 次课 / 32 小节 / 72 道实操题，每题一个独立素材包。",
             "考试环境：%s" % ENV, "",
             "目录结构：",
             "  练习素材/README.txt                  本文件",
             "  练习素材/练习N-M-题目短名/          每题的解压目录",
             "  练习素材/下载/练习N-M-题目短名.zip  网页可直接下载的压缩包",
             "  练习素材/索引.html                  更新清单 / 72 题对应表 / 版本一致性校验结果", "",
             "命名规则：N = 第几次课（1~8），M = 该次课内的题序（1~16 / 1~8）。",
             "  主文件统一为「素材-练习N-M.docx / .xlsx / .pptx」；",
             "  多文档题（比较、邮件合并、多窗口）按用途命名，与已生成的参考包一致。", "",
             "内容原则：",
             "  1. 素材只提供起始文字、原始数据与必要的图片/数据源；",
             "  2. 格式、公式、图表、动画、修订、目录、题注等答案动作一律不预置；",
             "  3. 每包内的「素材说明.txt」列出文件清单、题目要求、完成效果与功能入口口径；",
             "  4. 数据均为自拟教学数据，不含真实个人信息。", "",
             "版本口径：全站统一使用「WPS Office 教育考试专用版」，",
             "  组件称 WPS 文字 / WPS 表格 / WPS 演示，功能入口按该版本现行功能区命名；",
             "  不引用具体小版本号，不与任何其他版本混用。", "",
             "交付校验：tools/material/verify.py 生成 练习素材/索引.html 与 verify_report.json，",
             "  覆盖文件齐全性、包内无无关文件、文档可打开、72 个下载入口与版本残留。", "",
             "文件总数：%d 个素材目录 + %d 个下载包。" % (len(rows), len(rows)),
             "=" * 64]
    (OUT / "README.txt").write_text("\n".join(total) + "\n", encoding="utf-8")
    print("\n完成：%d 个素材包，%d 个 zip" % (len(rows), len(list(DL.glob('*.zip')))))


if __name__ == "__main__":
    main()
