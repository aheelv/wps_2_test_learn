# -*- coding: utf-8 -*-
"""
inject_figures.py —— 把界面示意图按「例题 → 步骤 → 效果」插入《入门实操课.html》
运行：python tools/inject_figures.py
"""
import io
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML = os.path.join(ROOT, "入门实操课.html")
IMG = "./assets/wps-img/"

# 例题 id -> (步骤截图列表, 效果截图)
# 步骤截图: (图片名, 步骤标注, 图注)
# 效果截图: (图片名, 图注)
FIGS = {
    "e1-1": ([("e1-1-save", "步骤 6",
               "「另存为」对话框：文件名填 <code>学号-姓名-练习1-1</code>，保存类型选 "
               "<b>Word 文件(*.docx)</b>，左侧位置定位到 <code>二级WPS练习 \\ 课时1</code>。")],
             ("e1-1-result", "保存后的文档：标题独占一段，正文另起一段（注意两处段落标记）")),
    "e1-2": ([("e1-2-symbol", "步骤 3",
               "「插入 → 符号 → 其他符号」：字体选普通文本，子集选类似字母的符号，"
               "在字符表中双击 <b>℃</b> 即可插入。"),
              ("e1-2-supsub", "步骤 4–5",
               "「开始」选项卡字体组末位的 <b>X²</b>（上标）与 <b>X₂</b>（下标）："
               "选中文本后点按钮，不能用改字号代替。")],
             ("e1-2-result", "录入结果：符号用「插入」取得，上下标用真实格式设置")),
    "e1-3": ([("e1-3-select", "步骤 2",
               "三种选定方式：双击选一个词、三击选整段（含段末 ¶）、Shift+单击框选两点之间的内容。")],
             ("e1-3-result", "第 3 段整体移到最前：顺序变为 成绩查询 → 报名时间 → 考试时间，三段仍是三个独立段落")),
    "e1-4": ([("e1-4-layout", "步骤 2",
               "「页面布局」选项卡：纸张大小、页边距、分栏、分隔符、水印、页面边框、页面颜色都在这一组。"),
              ("e1-4-page", "步骤 3",
               "「页面设置 → 页边距」：上下填 2.54 厘米、左右填 3.17 厘米，"
               "「应用于」必须选 <b>整篇文档</b>。"),
              ("e1-4-encrypt", "步骤 6",
               "「文件 → 文档加密 → 密码加密」：在「打开权限密码」中输入密码，确认后保存才生效。")],
             ("e1-4-result", "A4 纵向 + 上下 2.54 / 左右 3.17 厘米，红色虚线为页边距位置")),

    "e2-1": ([("e2-1-font", "步骤 6",
               "「字体」对话框 →「字符间距」选项卡：间距选 <b>加宽</b>，磅值填 <b>2 磅</b>。"),
              ("e2-1-para", "步骤 5",
               "「段落」对话框：段前、段后各填 <b>0.5 行</b>，对齐方式按标题 / 正文 / 落底分别选择。")],
             ("e2-1-result", "通知成品：黑体二号居中标题、称谓、正文、右对齐落款四级格式齐备")),
    "e2-2": ([("e2-2-para", "步骤 3–5",
               "「段落」对话框一次设好：两端对齐、1.5 倍行距、段前段后 0 行、"
               "特殊格式「首行缩进」度量值 <b>2 字符</b>。")],
             ("e2-2-result", "正文效果：首行缩进两格（缩进标记，不是空格）、两端对齐、1.5 倍行距")),
    "e2-3": ([("e2-3-char", "步骤 2–3",
               "字体组中的 <b>A 带底色</b>（字符底纹）与 <b>方框 A</b>（字符边框）：只包住被选中的文字。"),
              ("e2-3-paint", "步骤 6–7",
               "「格式刷」在「开始 → 剪贴板」组：单击刷一次，双击连续刷多段，按 Esc 退出。")],
             ("e2-3-result", "字符底纹 + 字符边框 + 红色加粗 + 格式刷统一后的段落格式")),
    "e2-4": ([("e2-4-list", "步骤 2–3",
               "「编号」下拉选 1. 2. 3.、「项目符号」下拉选圆点：自动编号可随内容增减自动重排。"),
              ("e2-4-border", "步骤 4–6",
               "「边框和底纹」：边框选方框、实线、<b>1.5 磅</b>；底纹用自定义 RGB(255,255,204)；"
               "「应用于」选 <b>段落</b>，「选项」中距正文左右 0.2 厘米。")],
             ("e2-4-result", "自动编号 + 项目符号 + 1.5 磅方框浅黄底纹的「注意事项」块")),

    "e3-1": ([("e3-1-style", "步骤 5",
               "在样式上右键 →「修改…」：改一次样式，全文使用该样式的段落同步改变。"),
              ("e3-1-modify", "步骤 5–6",
               "「修改样式」对话框：字体选项卡设黑体、小二；「格式」按钮进入段落设居中与段前段后 0.5 行。")],
             ("e3-1-result", "套用样式后的报告页，右侧「导航窗格」可显示标题层级")),
    "e3-2": ([("e3-2-replace", "步骤 1–2",
               "「查找和替换」（Ctrl+H）：查找内容 / 替换为两栏输入，「更多 >>」可展开通配符与特殊字符。"),
              ("e3-2-format", "步骤 3",
               "格式替换：查找端设「红色 + 加粗」，替换端设「蓝色 + 不加粗」，两端格式必须分别设置。")],
             ("e3-2-result", "替换前后对比：直接替换会出现「跨境跨境电子商务」，占位符两遍替换结果正确")),
    "e3-3": ([("e3-3-cols", "步骤 2",
               "「分栏」对话框：栏数选两栏、勾选分隔线、栏间距 1 厘米，"
               "「应用于」必须是 <b>所选文字</b>。")],
             ("e3-3-result", "两栏 + 分隔线的版面，左栏首字下沉 2 行")),
    "e3-4": ([("e3-4-watermark", "步骤 1",
               "「自定义水印」：水印类型选文字水印，填文字与字号 36，颜色浅灰并勾选半透明。"),
              ("e3-4-border", "步骤 2",
               "「页面边框」：设置选方框、线型双线、宽度 1.5 磅，「应用于」选整篇文档。")],
             ("e3-4-result", "文字水印 + 双线页面边框 + 浅蓝页面颜色同时呈现")),

    "e4-1": ([("e4-1-section", "步骤 2",
               "「页面布局 → 分隔符 → 分节符·下一页」：用分节符才能让封面与正文分别设置页眉页脚。"),
              ("e4-1-header", "步骤 4–5",
               "页眉页脚编辑状态下的工具条：<b>「同前节」必须点掉</b>，否则正文页眉与封面共用一份。"),
              ("e4-1-pageno", "步骤 8",
               "「设置页码格式」：起始页码填 1，页码位置与对齐方式按题目要求选择。")],
             ("e4-1-result", "封面（第 1 节）无页眉页脚，正文（第 2 节）页眉带下框线、页脚页码从 1 开始")),
    "e4-2": ([("e4-2-insert", "步骤 1",
               "「插入 → 表格 → 插入表格」：列数 4、行数 5，勾选「首行为标题行」，对齐方式居中。"),
              ("e4-2-prop", "步骤 4",
               "「表格属性 → 列」：逐列填写宽度 1.5 / 4 / 3 / 3 厘米（先设固定列宽再改数值）。")],
             ("e4-2-result", "成绩表成品：表头浅灰底纹加粗居中、全表所有框线、表格整体居中")),
    "e4-3": ([("e4-3-wrap", "步骤 2–4",
               "「图片工具 → 环绕 → 四周型环绕」，在「大小」中把宽度设为 7 厘米，"
               "「对齐」选水平居中（相对于页边距），「图片边框」设 1 磅橙色。")],
             ("e4-3-result", "图片四周型环绕 + 居中 + 1 磅橙色边框，下方为「图1」题注")),
    "e4-4": ([("e4-4-toc", "步骤 8",
               "「引用 → 目录 → 自动目录」：先套用标题样式，再生成目录；页码有变时选「更新整个目录」。"),
              ("e4-4-tocpage", "步骤 8",
               "生成的目录单独占一页，条目与正文标题一一对应，页码可通过点击跳转。")],
             ("e4-4-doc", "综合大题成品：标题样式 + 自动编号 + 表格 + 项目符号 + 页眉页脚")),
}

# 课时导览图（插在各课时开头的「本课时学完」之后）
LESSON_FIGS = {
    "l1": ("l1-file", "课前导览",
           "WPS「文件」菜单：新建、另存为、输出为PDF、文档加密四个入口，是考试中最常用的操作。"),
    "l2": ("l2-begin", "课前导览",
           "「开始」选项卡的字体组与段落组：所有字符格式与段落格式都从这里设置。"),
    "l3": ("l3-style", "课前导览",
           "「开始 → 样式」决定文档结构，「引用 → 目录 / 题注」决定目录与编号，二者配合才能一键生成。"),
    "l4": ("l4-insert", "课前导览",
           "「插入」选项卡集中了表格、图片、页码、文本框、题注等对象，构成长文档的主体。"),
}

FIG_CSS = """
  /* ===== 界面示意图 ===== */
  .shotblock{margin-top:16px}
  .shotblock>.kicker{display:flex;align-items:center;gap:8px;margin-bottom:8px}
  .shotgrid{display:grid;grid-template-columns:repeat(2,1fr);gap:14px}
  @media(max-width:760px){.shotgrid{grid-template-columns:1fr}}
  .shot{margin:0;background:#fff;border:1px solid var(--line);border-radius:12px;overflow:hidden;box-shadow:var(--shadow);break-inside:avoid}
  .shot img{display:block;width:100%;height:auto;background:#F3F5F8}
  .shot figcaption{padding:10px 13px;font-size:13px;line-height:1.75;color:var(--ink-2);border-top:1px solid var(--line-2)}
  .shot figcaption .tag-step{display:inline-block;font-size:11px;font-weight:800;color:#fff;background:var(--brand);border-radius:6px;padding:2px 8px;margin-right:6px;white-space:nowrap}
  .shot figcaption .tag-eff{display:inline-block;font-size:11px;font-weight:800;color:#fff;background:var(--accent);border-radius:6px;padding:2px 8px;margin-right:6px;white-space:nowrap}
  .shot figcaption code{font-size:12px}
  .shot.result{max-width:580px;margin:14px auto 0}
  .shot.result img{background:#EEF1F5}
  .shotblock .tipimg{font-size:12px;color:var(--muted);margin-top:8px}
  @media print{
    .shot{box-shadow:none}
    .shotblock{break-inside:avoid}
  }
"""


def figure(img, alt, cap, tag_text, tag_cls="tag-step"):
    return ('<figure class="shot"><img src="%s%s.svg" alt="%s" loading="lazy">'
            '<figcaption><span class="%s">%s</span>%s</figcaption></figure>'
            % (IMG, img, alt, tag_cls, tag_text, cap))


def build():
    s = io.open(HTML, encoding="utf-8").read()
    if "shotblock" in s:
        print("已插入过示意图，跳过。")
        return

    # 1) 插入样式
    s = s.replace("  /* ===== 本页专用：例题卡片 ===== */", FIG_CSS + "\n  /* ===== 本页专用：例题卡片 ===== */")

    # 2) 课前导览图：插在各课时「本课时学完，你要能做到」提示框之后
    for key, (img, tagt, cap) in LESSON_FIGS.items():
        anchor = '<div class="callout tip">\n          <h4>本课时学完，你要能做到</h4>'
        idx = s.find(anchor, s.find('id="%s"' % key))
        if idx < 0:
            continue
        end = s.find("</div>", s.find("</ul>", idx)) + len("</div>")
        blk = ('\n        <div class="shotblock"><div class="kicker">课前导览</div>'
               '<div class="shotgrid">%s</div></div>' % figure(img, cap, cap, tagt))
        s = s[:end] + blk + s[end:]

    # 3) 例题截图
    for ex_id, (steps, result) in FIGS.items():
        start = s.find('<article class="ex" id="%s"' % ex_id)
        if start < 0:
            print("未找到例题：", ex_id)
            continue
        end = s.find("</article>", start)
        block = s[start:end]

        # 3.1 步骤截图：插在步骤列表 </ol> 之后
        if steps:
            m = re.search(r'</ol>\s*(?=<div class="score">)', block)
            if not m:
                print("未定位到步骤结束位置：", ex_id)
                continue
            figs = "".join(figure(i, cap, cap, t) for i, t, cap in steps)
            ins = ('\n            <div class="shotblock"><div class="kicker">关键操作截图</div>'
                   '<div class="shotgrid">%s</div></div>\n            ' % figs)
            block = block[:m.end()] + ins + block[m.end():]

        # 3.2 效果截图：插在 </article> 之前
        if result:
            img, cap = result
            ins = ('\n            <div class="shotblock"><div class="kicker">完成效果</div>'
                   '<div class="shotgrid">%s</div></div>\n            '
                   % figure(img, cap, cap, "完成效果", "tag-eff"))
            block = block + ins

        s = s[:start] + block + s[end:]

    # 4) 顶部说明
    note = ('  <div class="callout warn mt2">\n'
            '    <h4>📌 关于本页的界面示意图</h4>\n'
            '    <p class="mb0">下方所有界面图为<b>依据 WPS Office 文字 12.x 界面绘制的教学示意图</b>（非软件实机截图），'
            '图中按钮位置、对话框字段与参数值均与对应例题的步骤一一对应，红色虚线框与序号标注即为操作点；'
            '带「完成效果」标签的图为按题目要求排版后的文档效果。教学演示时，请以本机实际界面为准，按功能名称定位按钮。</p>\n'
            '  </div>\n')
    s = s.replace('  <section class="section-sm" id="design">', note + '  <section class="section-sm" id="design">')

    io.open(HTML, "w", encoding="utf-8").write(s)
    n = s.count('class="shot"')
    print("插入示意图 %d 张（含效果图）" % n)


if __name__ == "__main__":
    build()
