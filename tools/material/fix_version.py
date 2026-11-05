# -*- coding: utf-8 -*-
"""清除旧版残留：统一 WPS Office 教育考试专用版界面名、组件名与文件类型名。

只改「界面入口 / 版本脚注 / 文件类型」用语；考纲条目名与知识点名中的
「页面布局」（如「字体段落、样式主题、页面布局」）属大纲原文，保留不动。
"""
import re, glob, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STAT = {}

# ---- 1. 界面入口与文件类型：精确短语替换 ----
PAIRS = [
    ('「页面布局」选项卡（部分版本叫「页面」）', '「页面」选项卡'),
    ('「页面布局（布局）」选项卡', '「页面」选项卡'),
    ('“页面布局（布局）”选项卡', '“页面”选项卡'),
    ('「页面布局」', '「页面」'),
    ('「页面布局 →', '「页面 →'),
    ('页面布局（或"页面"）→', '页面 →'),
    ('页面布局（或“页面”）→', '页面 →'),
    ('选项卡：文件 / 开始 / 插入 / 页面布局 / 引用',
     '选项卡：文件 / 开始 / 插入 / 页面 / 引用'),
    ('<b>Word 文件(*.docx)</b>', '<b>WPS 文字 文件(*.docx)</b>'),
    ('Word 文件(*.docx)', 'WPS 文字 文件(*.docx)'),
    ('「<b>Excel 工作簿(*.xlsx)</b>」', '「<b>WPS 表格 文件(*.xlsx)</b>」'),
    ('<b>Excel 工作簿(*.xlsx)</b>', '<b>WPS 表格 文件(*.xlsx)</b>'),
    ('界面示意图 · WPS 文字 12.x', '界面示意图 · WPS Office 教育考试专用版'),
    ('>页面布局</text>', '>页面</text>'),
]

# ---- 2. 整段重写：跨版本对比说明（版本混用） ----
OLD_PARA = ('<p>WPS 教育考试专用版、个人版、较新版本之间，选项卡名称偶有差别：<b>「页面布局」</b>在部分版本叫'
            '<b>「页面」</b>；<b>「输出为 PDF」</b>在部分版本叫<b>「另存为 PDF」</b>；页眉页脚工具里的'
            '<b>「同前节」</b>有的版本写作<b>「链接到前一条页眉」</b>。功能位置完全对应，'
            '<b>考试时以本机界面为准</b>，按功能找按钮，不要死记名字。</p>')
NEW_PARA = ('<p>本页所有界面名称、功能入口与操作结果，均按 <b>WPS Office 教育考试专用版</b>'
            '（2025 年版考试大纲指定考试环境）统一表述：页面级命令在 <b>「页面」</b>选项卡，'
            '输出 PDF 用 <b>「输出为 PDF」</b>，分节后断开页眉页脚链接用 <b>「同前节」</b>，'
            '保存类型选 <b>WPS 文字 文件(*.docx)</b>。组件统一称 WPS 文字 / WPS 表格 / WPS 演示，'
            '不引用具体小版本号，也不与其他版本混用；界面示意图按此口径绘制。</p>')


def patch(path):
    s = path.read_text(encoding='utf-8')
    before = s
    if OLD_PARA in s:
        s = s.replace(OLD_PARA, NEW_PARA)
        STAT['跨版本对比段落重写'] = STAT.get('跨版本对比段落重写', 0) + 1
    for a, b in PAIRS:
        n = s.count(a)
        if n:
            s = s.replace(a, b)
            STAT[a[:26]] = STAT.get(a[:26], 0) + n
    if s != before:
        path.write_text(s, encoding='utf-8')
        return 1
    return 0


def main():
    targets = sorted(glob.glob(str(ROOT / '*.html'))) + \
              sorted(glob.glob(str(ROOT / 'assets/wps-img/*.svg'))) + \
              sorted(glob.glob(str(ROOT / '考试模拟系统/*.html')))
    changed = sum(patch(Path(f)) for f in targets)
    print('改动文件数：', changed)
    for k, v in sorted(STAT.items(), key=lambda x: -x[1]):
        print('  %3d × %s' % (v, k))


if __name__ == '__main__':
    main()
