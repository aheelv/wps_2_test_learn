# -*- coding: utf-8 -*-
"""逐题核验「素材包是否与题目内容匹配」的严格审计器。

与 audit_match.py（结构一致性）互补，本脚本只回答一个问题：
    学生打开这个素材包，能不能直接按题目要求操作？

规则：
    F1  起始素材覆盖：题干/起始素材里声明的每一行文字都必须出现在包内文件中
    F2  通用填充残留：包内不得出现与题目无关的通用教学填充段落
    F3  演示模板残留：PPTX 不得出现通用汇报模板的标题与正文
    F4  关键对象缺失：题干/步骤中用书名号或引号标出的关键内容（表名、页标题、
                     图表标题、按钮文字等）必须在包内存在，学生才有对象可操作
    F5  张数不足：题干点名要操作的第 N 张幻灯片/工作表必须存在
    F6  附件缺失：题干点名要使用的文件必须在包内
    F7  表名不符：题干点名的表名/工作表名必须在包内工作簿中存在

用法：python tools/material/audit_fit.py [--dir 11-11]
输出：tools/material/fit_report.json
"""
import json
import os
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
MAT = ROOT / "练习素材"

# 与题目无关的通用填充段落（历史模板遗留）
FILLER = [
    "学院围绕计算机应用能力培养组织了系列实训",
    "以项目任务为主线",
    "共 8 次课、32 小节、72 道实操题",
    "覆盖文档排版、数据处理与演示汇报三个模块",
    "2026 年春季实训成果汇报",
    "一、实训背景与目标",
    "二、实施过程",
    "三、数据结果",
    "四、问题与改进",
    "五、下一步计划",
]

# 题干里出现的功能区/界面术语，不作为「关键对象」要求包内出现
UI_TERMS = {
    "开始", "插入", "页面", "引用", "审阅", "视图", "工具", "设计", "布局", "动画",
    "切换", "幻灯片放映", "录制", "文件", "主页", "数据", "邮件",
    "图片", "形状", "表格", "图表", "文本框", "艺术字", "视频", "音频", "公式",
    "字体", "段落", "样式", "编号", "项目符号", "查找", "替换", "选择", "新建",
    "打开", "保存", "另存为", "打印", "预览", "页面设置", "显示", "编辑",
    "标题", "正文", "占位符", "幻灯片浏览", "普通", "大纲", "备注页", "阅读",
    "演示文稿", "任务窗格", "选项卡", "功能区", "工具栏", "对话框", "向导",
    "文档加密", "文档检查器", "压缩媒体", "自定义幻灯片放映",
    "排练计时", "设置放映方式", "裁剪", "删除背景", "压缩图片", "相册",
    "合并单元格", "拆分单元格", "自动调整", "边框和底纹", "行距", "缩进",
    "页眉", "页脚", "分节符", "水印", "页面边框", "首字下沉", "分栏",
    "题注", "交叉引用", "脚注", "尾注", "引文", "索引", "修订", "批注",
    "限制编辑", "邮件合并", "并排比较", "保留源格式", "定义", "目录",
    "创建目录", "文件夹", "计算机", "鼠标", "快捷键", "菜单", "状态栏",
    "空白文档", "文件类型", "未保存", "其他符号", "普通文本", "子集",
    "类似字母的符号", "货币符号", "纸张大小", "纸张方向", "自定义页边距",
    "字符", "密码加密", "打开权限密码", "磅值", "对齐方式", "度量值", "间距",
    "确定", "空两格", "样板段", "填充", "其他颜色", "自定义", "查找内容",
    "更多", "全部替换", "不限定格式", "使用通配符", "分隔符",
    "页眉和页脚", "插入 → 域", "设置页码格式", "首页不同", "插入表格",
    "表格属性", "指定宽度", "自动调整 → 固定列宽", "表格工具", "边框",
    "标题行重复", "新建标签", "图片工具", "嵌入型", "锁定纵横比", "对齐",
    "相对于", "图片边框", "粗细", "形状填充", "形状轮廓", "标题1",
    "引用 → 题注", "页边距 → 自定义", "插入 → 页眉和页脚",
    "插入 → 页码", "更新目录", "文件 → 输出为PDF", "节页数",
    "分节符（下一页）", "更多分栏", "应用于", "所选文字", "首字下沉选项",
    "下沉行数", "自定义水印", "表格工具 → 对齐方式", "表格工具 → 布局",
    "按位置合并", "按类别合并", "有效性", "圈释无效数据", "单变量模拟",
    "双变量模拟", "单变量求解", "模拟运算表", "方案管理器", "数据透视表",
    "数据透视图", "切片器", "日程表", "组合图", "次坐标轴", "迷你图",
    "分类汇总", "高级筛选", "条件区域", "自动筛选", "自定义序列",
    "按颜色排序", "排名", "分段", "中位数", "百分位", "查找引用函数",
    "反向查找", "动态引用", "身份证", "工作日函数", "多条件求和", "IFERROR",
    "嵌套", "取整", "单双", "偏差", "绝对值", "舍入", "同比", "环比",
    "标题幻灯片", "标题和内容", "仅标题", "两栏内容", "正文占位符",
    "标题占位符", "母版", "版式", "配色方案", "字体方案", "主题",
    "图片填充", "渐变填充", "线性向下", "隐藏背景图形", "艺术字",
    "文本效果", "阴影", "映像", "图片项目符号", "竖排", "两栏",
    "编辑顶点", "顶端对齐", "横向分布", "智能图形", "组合", "圆角矩形",
    "菱形", "连接符", "流程", "相册", "视频全屏", "跨幻灯片播放",
    "淡出", "循环播放", "自动播放", "簇状柱形图", "图表标题",
    "进入动画", "强调动画", "退出动画", "动作路径", "自定义路径",
    "动画刷", "动画窗格", "擦除", "脉冲", "飞入", "上一动画之后",
    "与上一动画同时", "单击时", "推入", "自右侧", "自左侧", "淡入淡出",
    "自动换片", "循环放映", "演讲者放映", "演讲者视图", "不加动画",
    "自定义放映", "超链接", "本文档中的位置", "动作按钮", "返回第一张",
    "结束放映", "打开密码", "标记为最终状态", "检查文档", "兼容性",
    "嵌入字体", "链接的文件", "讲义", "水平顺序", "A4 横向", "每页 4 张",
    "分辨率", "打包", "目录", "返回目录", "现状", "问题", "对策", "谢谢",
    "封面", "结束页", "谢谢观看", "第一张", "第二张", "第三张", "第四张",
    "第五张", "第六张", "第七张", "第八张", "第九张",
}

FILE_RE = re.compile(r"[\w\u4e00-\u9fa5\-.]+\.(?:docx|xlsx|pptx|png|txt|wav|mp4|pdf|zip)")
SHEET_RE = re.compile(r"[「『\"]([^」』\"]{2,12})[」』\"]")
OUT_WORDS = re.compile(r"(输出为|保存为|导出为|另存为|生成|命名为|文件名)")
# 起始素材里的「说明行」：描述数据而非要逐字录入的正文
DESC_LINE = re.compile(
    r"^(表头|记录示例|记录格式|示例|说明|注|备注|口径|共\s*\d+\s*条)"
    r"|^（.*(示意|说明|提示).*）$")


def norm(s):
    return re.sub(r"\s+", "", str(s or ""))


def norm_line(s):
    """比较用归一化：去掉「（第 N 段）」段落标签与合并域占位符差异。"""
    s = re.sub(r"^（第\s*\d+\s*段）", "", str(s or "").strip())
    s = re.sub(r"【[^】]*】", "#", s)
    return norm(s)


def read_docx(p):
    from docx import Document
    d = Document(str(p))
    out = [x.text for x in d.paragraphs]
    for tb in d.tables:
        for r in tb.rows:
            for c in r.cells:
                out.append(c.text)
    return "\n".join(out)


def read_xlsx(p):
    import openpyxl
    wb = openpyxl.load_workbook(str(p), data_only=False)
    out = []
    for ws in wb.worksheets:
        out.append(ws.title)
        for r in ws.iter_rows(values_only=True):
            for v in r:
                if v is not None:
                    out.append(str(v))
    return "\n".join(out)


def read_pptx(p):
    from pptx import Presentation
    pr = Presentation(str(p))
    out = []
    for s in pr.slides:
        for sh in s.shapes:
            if sh.has_text_frame:
                out.append(sh.text_frame.text)
    return "\n".join(out)


def read_pkg(pkg):
    """返回 (文本语料, 文件清单, 工作表名列表, 幻灯片数)"""
    corpus, files, sheets, slides = [], [], [], 0
    for f in sorted(os.listdir(pkg)):
        if f.startswith("~$") or f.startswith("."):
            continue
        fp = os.path.join(pkg, f)
        if not os.path.isfile(fp):
            continue
        files.append(f)
        try:
            if f.endswith(".docx"):
                corpus.append(read_docx(fp))
            elif f.endswith(".xlsx"):
                import openpyxl
                wb = openpyxl.load_workbook(fp)
                sheets += [ws.title for ws in wb.worksheets]
                corpus.append(read_xlsx(fp))
            elif f.endswith(".pptx"):
                from pptx import Presentation
                slides = len(Presentation(fp).slides)
                corpus.append(read_pptx(fp))
            elif f.endswith(".txt"):
                corpus.append(Path(fp).read_text(encoding="utf-8", errors="replace"))
        except Exception as e:
            corpus.append("!!读取失败:%s" % e)
    return "\n".join(corpus), files, sheets, slides


def key_quotes(q):
    """从题干「题目要求」中提取书名号/引号标出的关键内容对象。

    只看 reqs（题目要求）不看 steps：步骤里大量是功能区名称，不是素材内容。
    引号内以「…」结尾的是题干的省略写法，按前缀匹配。
    """
    out = []
    for m in SHEET_RE.finditer(" ".join(q["reqs"])):
        s = m.group(1).strip().rstrip("…").strip()
        if not (2 <= len(s) <= 14):
            continue
        if s in UI_TERMS or s in FILLER:
            continue
        if re.match(r"^[\d\.\s]+$", s):
            continue
        out.append(s)
    seen, uniq = set(), []
    for s in out:
        if s not in seen:
            seen.add(s)
            uniq.append(s)
    return uniq


def sheet_names_quoted(q):
    """题干中以「」标注、且形如工作表名的内容"""
    return key_quotes(q)


def check(q, corpus, files, sheets, slides, src_dir=None):
    issues = []
    flat = norm(corpus)
    reqs = " ".join(q["reqs"])
    steps = " ".join(q["steps"])

    # F1 起始素材覆盖
    for ln in [x.strip() for x in str(q["src"]).splitlines() if x.strip()]:
        if DESC_LINE.match(ln):
            continue          # 说明行（表头说明、记录示例、条数说明等），不是要录入的字面文字
        if norm_line(ln) not in norm_line(corpus):
            issues.append(("F1", "起始素材缺行：%s" % ln[:40]))

    # F2 通用填充残留
    for f in FILLER:
        if norm(f) in flat:
            issues.append(("F2", "残留通用填充内容：%s" % f))

    # F3 演示模板残留
    if slides and any(norm(f) in flat for f in FILLER[4:]):
        issues.append(("F3", "PPTX 仍是通用汇报模板，未按本题内容定制"))

    # F4 关键对象缺失
    for s in key_quotes(q):
        if norm(s) not in flat:
            issues.append(("F4", "题目引用的「%s」在素材包中不存在" % s))

    # F5 张数不足（题干点名要操作的第 N 张必须存在）
    #     但若题目本身要求「导入大纲生成幻灯片」，页数由学生生成，不作要求
    imported = bool(re.search(r"(导入|生成|新建)[^。；]{0,12}幻灯片", reqs + " " + steps))
    need = 0
    for m in re.finditer(r"第\s*(\d+)\s*张", reqs + " " + steps):
        need = max(need, int(m.group(1)))
    if slides and need > slides and not imported:
        issues.append(("F5", "题目操作到第 %d 张，素材只有 %d 张" % (need, slides)))

    # F6 附件缺失：题目里的文件名前后可能带动词前缀（选/打开/插入），按后缀回退匹配
    for m in FILE_RE.finditer(reqs + " " + steps):
        fn = m.group(0)
        ctx = (reqs + " " + steps)[max(0, m.start() - 40):m.start()]
        if OUT_WORDS.search(ctx):
            continue          # 学生要产出的文件，不是起始素材
        if fn.startswith("学号-姓名") or fn.startswith("打包-"):
            continue          # 学生按题目要求命名的产出文件
        if fn in files:
            continue
        hit = None
        for i in range(1, len(fn)):
            if fn[i:] in files:
                hit = fn[i:]
                break
        if hit:
            continue          # 「选初稿.docx」这类前缀误匹配
        issues.append(("F6", "题目引用的素材文件 %s 不在包内" % fn))

    # F7 表名不符：只针对「素材里本来就应该有」的工作表名；
    #     学生要新建 / 重命名 / 插入的表不要求出现在起始工作簿中
    for s in sheet_names_quoted(q):
        if s in sheets or any(norm(s) in norm(x) for x in sheets):
            continue
        m = re.search(r"[^。；]{0,30}%s[^。；]{0,30}" % re.escape(s), reqs)
        if not m:
            continue
        seg = m.group(0)
        if re.search(r"(新建|重命名|插入|另建|创建|新增)", seg):
            continue
        if re.search(r"(工作表|工作簿|表名)", seg):
            issues.append(("F7", "题干要求的工作表「%s」不在素材工作簿中（现有：%s）"
                           % (s, "、".join(sheets) or "无")))
    return issues


def main():
    src = None
    if "--dir" in sys.argv:
        src = ROOT / sys.argv[sys.argv.index("--dir") + 1]
    E = json.loads((HERE / "exercises.json").read_text(encoding="utf-8"))
    rows, detail = [], []
    for q in E:
        if src:
            cands = [d for d in sorted(os.listdir(src))
                     if d.startswith("练习%d-%d-" % (q["ci"], q["seq"]))]
            pkg = str(src / cands[0]) if cands else None
        else:
            pkg = None
            for d in sorted(os.listdir(MAT)):
                if d.startswith("练习%d-%d-" % (q["ci"], q["seq"])) and os.path.isdir(MAT / d):
                    pkg = str(MAT / d)
                    break
        if not pkg or not os.path.isdir(pkg):
            rows.append(dict(no=q["no"], ci=q["ci"], seq=q["seq"], issues=1, list=[]))
            detail.append(dict(no=q["no"], ci=q["ci"], seq=q["seq"],
                               problems=["素材包缺失"], pkg=None))
            continue
        corpus, files, sheets, slides = read_pkg(pkg)
        iss = check(q, corpus, files, sheets, slides)
        rows.append(dict(no=q["no"], ci=q["ci"], seq=q["seq"], title=q["title"],
                         folder=os.path.basename(pkg), files=files, sheets=sheets,
                         slides=slides, issues=len(iss), list=[list(x) for x in iss]))
        detail.append(dict(no=q["no"], ci=q["ci"], seq=q["seq"], title=q["title"],
                           folder=os.path.basename(pkg), pkg=pkg,
                           problems=["%s %s" % (c, m) for c, m in iss]))
    total = len(rows)
    bad = sum(1 for r in rows if r["issues"])
    print("适配度审计：%d 题 / 有问题 %d 题 / 共 %d 处"
          % (total, bad, sum(r["issues"] for r in rows)))
    for d in detail:
        if d["problems"]:
            print("  [%s] 第%d次课 seq=%d %s" % (d["no"], d["ci"], d["seq"], d.get("title", "")))
            for p in d["problems"]:
                print("      - " + p)
    (HERE / "fit_report.json").write_text(
        json.dumps(dict(total=total, bad=bad, rows=rows, detail=detail),
                   ensure_ascii=False, indent=1), encoding="utf-8")
    print("\n报告：tools/material/fit_report.json")


if __name__ == "__main__":
    main()
