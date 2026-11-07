# -*- coding: utf-8 -*-
"""核验 72 道实操题对《二级 WPS Office 高级应用与设计考试大纲（2025 年版）》
操作类知识点的覆盖情况，并检查有无越界知识点 / 教育考试专用版不可实现的操作。

判定口径：
  · 考纲操作题 80 分 = WPS 文字 30 + WPS 表格 30 + WPS 演示 20；
    单项选择题 20 分属理论题，不在 72 道实操题覆盖范围，单列说明。
  · 教育考试专用版考场为离线、无账号的经典功能集，云端 / AI / 宏 / 插件 /
    新版专属函数与对象均属越界，复用 audit_steps.py 的规则扫描。

输出：
  python tools/material/audit_coverage.py            结构化结论（不打印题目原文）
  python tools/material/audit_coverage.py --report    另写 verify_coverage.json
"""
import re, sys, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
E = json.load(open(ROOT / 'tools/material/exercises.json', encoding='utf-8'))
M = json.load(open(ROOT / 'tools/material/manifest.json', encoding='utf-8'))
BY = {(r['ci'], r['seq']): r for r in M}

# (模块, 知识点, 检索式)。检索式按考纲条目措辞 + 本题库实际用语取并集。
POINTS = [
    # ---- WPS 文字 ----
    ('WPS 文字', '文档新建 / 打开 / 保存 / 另存为',
     r'新建|打开文档|保存为|另存为|Ctrl\+N|Ctrl\+S|F12'),
    ('WPS 文字', '文档加密 / 输出 PDF / 打印',
     r'文档加密|打开密码|密码加密|输出为\s*PDF|输出\s*PDF|打印预览|打印'),
    ('WPS 文字', '文本选定 / 编辑 / 查找替换 / 撤销',
     r'选定|选中文本|复制|剪切|粘贴|查找|替换|撤销|恢复|Ctrl\+Z|Ctrl\+F'),
    ('WPS 文字', '字符格式（字体 / 字号 / 效果 / 间距）',
     r'字体|字号|宋体|黑体|楷体|仿宋|加粗|倾斜|字符间距|上标|下标|字体颜色'),
    ('WPS 文字', '段落格式（对齐 / 缩进 / 行距 / 段间距）',
     r'段落|对齐|首行缩进|行距|段前|段后|两端对齐|居中对齐|悬挂缩进'),
    ('WPS 文字', '项目符号 / 编号 / 边框底纹',
     r'项目符号|自动编号|编号列表|边框和底纹|底纹|边框'),
    ('WPS 文字', '样式应用与修改', r'样式|标题\s*1|标题\s*2|正文样式|修改样式'),
    ('WPS 文字', '多级列表链接到样式', r'多级列表|定义新的多级列表|编号格式|将级别链接到样式'),
    ('WPS 文字', '页面设置（纸张 / 方向 / 页边距）',
     r'页面设置|A4|纸张大小|纸张方向|页边距|纵向|横向'),
    ('WPS 文字', '分节 / 分页 / 分栏 / 分隔符',
     r'分节符|分页符|分页|分栏|分隔符|栏间距|首字下沉'),
    ('WPS 文字', '页眉页脚 / 页码域 / 奇偶页不同',
     r'页眉|页脚|页码|Page|NumPages|首页不同|奇偶页不同|同前节'),
    ('WPS 文字', '表格插入与格式', r'插入表格|表格属性|单元格合并|表格样式|表头|表格|行高|列宽'),
    ('WPS 文字', '图片 / 形状 / 艺术字 / 文本框 / 环绕',
     r'图片|形状|艺术字|文本框|环绕|裁剪|四周型|紧密型|衬于文字下方'),
    ('WPS 文字', '题注 / 交叉引用 / 脚注尾注',
     r'题注|交叉引用|脚注|尾注|插入题注'),
    ('WPS 文字', '自动目录与更新域', r'目录|插入目录|更新域|更新整个目录|前导符'),
    ('WPS 文字', '邮件合并', r'邮件合并|主文档|数据源|合并到新文档|插入合并域'),
    ('WPS 文字', '修订 / 批注 / 比较 / 合并文档',
     r'修订|批注|比较文档|文档比较|合并文档|接受修订|拒绝修订'),
    ('WPS 文字', '文档保护 / 限制编辑 / 检查文档',
     r'限制编辑|保护文档|文档保护|检查文档|标记为最终状态'),
    ('WPS 文字', '水印 / 页面背景 / 页面边框',
     r'水印|页面颜色|页面边框|背景'),
    # ---- WPS 表格 ----
    ('WPS 表格', '工作簿 / 工作表基本操作',
     r'工作表|工作簿|重命名|移动或复制|Sheet\d|新建工作表'),
    ('WPS 表格', '单元格 / 区域 / 数据录入 / 填充',
     r'单元格|区域|填充柄|序列填充|数据录入|A1:|录入'),
    ('WPS 表格', '数据验证 / 有效性', r'数据验证|有效性|下拉列表|允许输入|出错警告'),
    ('WPS 表格', '条件格式', r'条件格式|突出显示单元格|色阶|数据条|图标集'),
    ('WPS 表格', '单元格格式（数字 / 对齐 / 边框）',
     r'单元格格式|数字格式|百分比|小数位|边框|底纹|行高|列宽|合并及居中'),
    ('WPS 表格', '相对 / 绝对 / 混合引用', r'绝对引用|相对引用|混合引用|\$[A-Z]\$?\d|单元格引用'),
    ('WPS 表格', '公式与常用函数',
     r'公式|SUM\s*\(|AVERAGE\s*\(|IF\s*\(|COUNTIF|SUMIF|VLOOKUP|ROUND|INT|MOD|RANK|函数'),
    ('WPS 表格', '文本 / 日期 / 统计函数',
     r'LEFT\s*\(|RIGHT\s*\(|MID\s*\(|LEN\s*\(|TEXT\s*\(|YEAR\s*\(|MONTH\s*\(|'
     r'NETWORKDAYS|WORKDAY|COUNT\s*\(|MAX\s*\(|MIN\s*\(|STDEV|身份证|文本函数|日期函数'),
    ('WPS 表格', '查找引用 / 逻辑函数',
     r'VLOOKUP|HLOOKUP|INDEX\s*\(|MATCH\s*\(|AND\s*\(|OR\s*\(|IF\s*\(|查找引用|反向查找'),
    ('WPS 表格', '排序 / 筛选 / 高级筛选',
     r'排序|筛选|高级筛选|自动筛选|条件区域|升序|降序'),
    ('WPS 表格', '分类汇总 / 合并计算',
     r'分类汇总|合并计算|汇总|分级显示'),
    ('WPS 表格', '数据透视表 / 透视图 / 切片器',
     r'数据透视|透视图|切片器|行标签|值字段'),
    ('WPS 表格', '图表创建与编辑 / 组合图 / 次坐标轴',
     r'图表|柱形图|折线图|饼图|组合图|次坐标轴|图表类型|数据系列|图例'),
    ('WPS 表格', '迷你图', r'迷你图|折线迷你图|柱形迷你图'),
    ('WPS 表格', '页面设置 / 打印区域 / 打印标题',
     r'页面设置|打印区域|打印标题|顶端标题行|分页预览|缩放|页眉|页脚'),
    ('WPS 表格', '工作表 / 工作簿保护',
     r'保护工作表|保护工作簿|撤销工作表保护|允许编辑区域|锁定单元格'),
    ('WPS 表格', '模拟分析 / 方案 / 单变量求解',
     r'模拟分析|方案管理器|单变量求解|规划求解|方案'),
    # ---- WPS 演示 ----
    ('WPS 演示', '演示文稿 / 幻灯片基本操作',
     r'新建幻灯片|幻灯片|复制幻灯片|删除幻灯片|版式|节'),
    ('WPS 演示', '大纲导入 / 视图 / 备注',
     r'大纲|从大纲|备注|视图|幻灯片浏览|阅读视图'),
    ('WPS 演示', '主题 / 配色 / 字体方案 / 背景',
     r'主题|配色|字体方案|背景|渐变|图片填充'),
    ('WPS 演示', '幻灯片母版 / 版式统一',
     r'母版|版式|占位符|页脚|母版视图'),
    ('WPS 演示', '艺术字 / 文本效果 / 形状 / 智能图形',
     r'艺术字|文本效果|形状|智能图形|SmartArt|文本框|竖排'),
    ('WPS 演示', '图片处理 / 相册 / 剪裁',
     r'图片|相册|裁剪|压缩图片|图片样式|删除背景'),
    ('WPS 演示', '表格 / 图表 / 音频 / 视频',
     r'插入表格|图表|音频|视频|媒体|跨幻灯片播放|全屏播放'),
    ('WPS 演示', '对象动画 / 效果选项 / 动画窗格',
     r'动画|动画窗格|效果选项|进入动画|强调动画|退出动画|触发器'),
    ('WPS 演示', '切换效果 / 计时 / 排练计时',
     r'切换效果|切换|排练计时|设置自动换片|全部应用|淡入淡出'),
    ('WPS 演示', '超链接 / 动作 / 放映设置',
     r'超链接|动作按钮|动作设置|放映设置|设置放映方式|自定义放映'),
    ('WPS 演示', '打包 / 输出 / 保护 / 检查文档',
     r'打包|输出为|另存为|打开密码|标记为最终状态|检查文档|文档属性'),
    ('WPS 演示', '综合设计与自评',
     r'综合|汇报|自评|评分表|限时|采分点'),
]

EXCLUDED = ('CLOUD', 'AI', 'EXT', 'MSO', 'VER', 'TAB', 'NEWFUNC', 'NEWFX',
            'NET', 'CLOUD2', 'AI2', 'MSO2', 'MIXVER')


def bodies():
    out = []
    for q in E:
        rec = BY[(q['ci'], q['seq'])]
        txt = '\n'.join([q['title']] + q['reqs'] + q['steps'] + [q['score'] or ''])
        out.append((q, rec, txt))
    return out


def collect():
    """返回 (知识点覆盖行, 未覆盖项, 越界题, 版本混用命中)，供 verify.py 实时复用。"""
    data = bodies()
    rows = []
    for mod, name, pat in POINTS:
        hit = [(q['no'], q['ci'], q['seq']) for q, rec, txt in data
               if re.search(pat, txt, re.I)]
        rows.append(dict(module=mod, point=name, pattern=pat, count=len(hit),
                         covered_by=['%s(c%d-%d)' % (n, c, s) for n, c, s in hit]))
    gaps = [r for r in rows if r['count'] == 0]

    # 越界检查：复用合规审计规则，逐题扫描题目 + 步骤 + 采分点
    import audit_steps
    qs = audit_steps.load()
    outside = []
    for q in qs:
        hits = audit_steps.scan(q)
        if hits:
            outside.append(dict(no=q['no'], ci=q['ci'], seq=q['seq'],
                                rules=sorted(set(x['rule'] for x in hits))))
    # 全站（含非 article 段落）版本混用措辞
    pages = sorted({q['page'] for q in E}) + ['实操训练.html']
    mix = []
    for fn in pages:
        p = ROOT / fn
        if not p.exists():
            continue
        for m in re.finditer(r'部分版本|不同版本|较新版本|视版本而定|版本差异|新版才有',
                             p.read_text(encoding='utf-8')):
            mix.append(dict(file=fn, word=m.group(0)))

    return rows, gaps, outside, mix


def main():
    rows, gaps, outside, mix = collect()
    print('考纲操作类知识点 %d 项 ｜ 已覆盖 %d 项 ｜ 未覆盖 %d 项'
          % (len(rows), len(rows) - len(gaps), len(gaps)))
    for g in gaps:
        print('  [未覆盖] %-8s %s' % (g['module'], g['point']))
    from collections import Counter
    c = Counter(r['module'] for r in rows)
    cc = Counter(r['module'] for r in rows if r['count'])
    for mod in c:
        print('  %-8s %d / %d 项覆盖' % (mod, cc[mod], c[mod]))
    print('越界题 %d ｜ 版本混用措辞 %d ｜ 覆盖题数 %d'
          % (len(outside), len(mix), len(set(n for r in rows for n in r['covered_by']))))
    if '--report' in sys.argv:
        json.dump(dict(total=len(rows), covered=len(rows) - len(gaps),
                       gaps=[g['point'] for g in gaps], points=rows,
                       outside=outside, mixed_wording=mix,
                       theory_note='单项选择题 20 分属理论题，不在 72 道实操题覆盖范围内。'),
                  open(ROOT / 'tools/material/verify_coverage.json', 'w', encoding='utf-8'),
                  ensure_ascii=False, indent=1)
    return len(gaps), len(outside), len(mix)


if __name__ == '__main__':
    sys.exit(0 if main() == (0, 0, 0) else 1)
