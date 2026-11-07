# -*- coding: utf-8 -*-
"""本轮「表述不准确」修订：例 8-3 超链接题的题目内部矛盾（幂等）。

问题（全站审计 OUT_NET + 人工逐题复核发现）：
  1. 采分点写「图片链接为指定网址」，但题目要求 / 解题步骤都是「图片链接到本文档第 2 张（目录页）」；
  2. 采分点同时写「第三部分链接到第 5 张」与「第三部分链接已取消」，最终状态自相矛盾；
  3. 解题步骤第 5 步已取消「第三部分」链接，第 7 步仍验证「点第三部分应跳到第 5 张」；
  4. 易错提醒写「网址漏了 https://」，既与本题无关（本题不设网页链接），
     又让操作题正文出现联网字面量，容易被误读为操作需联网。

修订原则：题意、题号、顺序、素材、最终操作对象不变，只把表述改到自洽且落在
WPS Office 教育考试专用版离线可完成范围内。

用法：python tools/material/fix_scope.py
      之后按既定重建顺序运行 make_shots.py → make_results.py → verify.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAGE = ROOT / '实操-演示2.html'
REPORT = ROOT / 'tools' / 'material' / 'scope_fix_report.json'

# 只匹配例 8-3 所在文章内的精确片段；字符串足够长，不会误伤其它题
PAIRS = [
    (
        '<div class="score"><b>采分点</b>「第三部分」链接到本文档第 5 张 · 图片链接为指定网址 · '
        '第 6 张有「第一张」动作按钮且单击生效 · 「第三部分」链接已取消 · '
        '第 8 张有「结束放映」动作按钮</div>',
        '<div class="score"><b>采分点</b>「第三部分」按题目要求完成第 5 张超链接设置后已取消、'
        '最终恢复为普通文本 · 第 6 张图片链接指向本文档第 2 张（目录页） · '
        '第 6 张有「第一张」动作按钮且单击生效 · 第 8 张有「结束放映」动作按钮</div>',
        '采分点与题目要求、最终状态对齐',
    ),
    (
        '<li><b>验证。</b>按 <kbd>F5</kbd> 放映 → 点「第三部分」应跳到第 5 张；'
        '点图片应跳到第 2 张；点动作按钮应回首页。</li>',
        '<li><b>验证。</b>按 <kbd>F5</kbd> 放映 → 在第 6 张点图片应跳到第 2 张（目录页）；'
        '点第 6 张动作按钮应回第 1 张；点第 8 张结束按钮可结束放映；'
        '「第三部分」已不再跳转（链接已取消）。</li>',
        '验证步骤与第 5 步「取消链接」对齐',
    ),
    (
        '<li>网址漏了 https://：被当成相对路径，打不开。</li>',
        '<li>图片超链接误设为外部文件目标：放映时不会跳回目录页，与题目要求不符。</li>',
        '删除与本题无关的联网字面量，改为本题真实易错点',
    ),
]


def patch_page():
    """三处片段都足够长，全文件唯一；逐条断言命中 0/1 次，避免误伤或漏改。"""
    s = PAGE.read_text(encoding='utf-8')
    done, skipped = [], []
    for old, new, why in PAIRS:
        n = s.count(old)
        if n == 1:
            s = s.replace(old, new, 1)
            done.append(why)
        elif s.count(new) == 1 and n == 0:
            skipped.append(why)
        else:
            raise SystemExit('片段命中异常（%d 次）：%s' % (n, why))
    PAGE.write_text(s, encoding='utf-8')
    return done, skipped


def sync_downstream():
    """按既定链路把网页改动同步到生成数据 / 说明 / zip / 截图 / 比对文档。"""
    import sys
    sys.path.insert(0, str(ROOT / 'tools' / 'material'))
    import fix_link
    n_json = fix_link.sync_json()
    n_readme, miss = fix_link.regen_readmes_and_repack()
    # 延迟 import，确保读到刚回写的 exercises.json
    import make_shots
    import make_results
    make_shots.main()
    make_results.main()
    return dict(exercises_fields=n_json, readmes=n_readme, zips=72,
                missing_packs=len(miss), shots=72, compare_docs=72)


def main():
    done, skipped = patch_page()
    print('=== 例 8-3 表述修订 ===')
    for x in done:
        print('  [改] ' + x)
    for x in skipped:
        print('  [已修] ' + x)
    print('=== 下游同步 ===')
    r = sync_downstream()
    for k, v in r.items():
        print('  %-18s %s' % (k, v))
    REPORT.write_text(json.dumps(dict(
        exercise='例 8-3 三类超链接 + 动作按钮 + 取消链接',
        page='实操-演示2.html',
        category='表述不准确 / 题目内部矛盾',
        fixes=[dict(reason=why, before=old, after=new) for old, new, why in PAIRS],
        downstream=r,
        scope='WPS Office 教育考试专用版（离线，超链接目标为本文档内部位置）',
    ), ensure_ascii=False, indent=1), encoding='utf-8')
    print('  修正清单 → tools/material/scope_fix_report.json')


if __name__ == '__main__':
    main()
