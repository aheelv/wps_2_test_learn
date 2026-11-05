# -*- coding: utf-8 -*-
"""把内容数据渲染成 A4 打印版 HTML（含目录页码占位）"""
import html as _h
import importlib

STAR = {1: "★☆☆☆", 2: "★★☆☆", 3: "★★★☆", 4: "★★★★"}


def esc(s):
    return _h.escape(str(s), quote=False)


def raw(s):
    return str(s)


class Builder:
    def __init__(self, doc):
        self.d = doc
        self.p = doc["primary"]
        self.deep = doc["deep"]
        self.tint = doc["tint"]
        self.line = doc["line"]
        self.toc_entries = []
        self._figseq = {}
        self.figs = {}
        if doc.get("figmod"):
            try:
                self.figs = importlib.import_module(doc["figmod"]).REG
            except Exception:
                self.figs = {}

    # ---------- 配图 ----------
    def figure(self, key, cap, chno, lead=""):
        """插入一张界面示意图，自动编号「图 章-序」"""
        fn = self.figs.get(key)
        if not fn:
            return ""
        f = fn()
        n = self._figseq.get(chno, 0) + 1
        self._figseq[chno] = n
        no = "图 %d-%d" % (chno, n)
        legs = "".join('<span class="fl"><i>%d</i>%s</span>' % (i, t) for i, t in f.marks())
        ld = '<p class="figlead">%s</p>' % lead if lead else ""
        return ('%s<figure class="fig"><div class="figbox">%s</div>'
                '<div class="figcap"><b>%s</b>　%s</div>'
                '<div class="figleg">%s</div></figure>' % (ld, f.svg(), no, esc(cap), legs))

    # ---------- 目录 ----------
    def toc_add(self, level, num, title):
        self.toc_entries.append((level, num, title))

    def render_toc(self, pm):
        rows = []
        for level, num, title in self.toc_entries:
            pg = pm.get(num + title, "")
            cls = "lv1" if level == 1 else "lv2"
            rows.append(
                '<div class="toc-row %s"><span class="toc-num">%s</span>'
                '<span class="toc-tt">%s</span><span class="toc-dot"></span>'
                '<span class="toc-pg">%s</span></div>'
                % (cls, esc(num), esc(title), esc(pg))
            )
        return (
            '<section class="toc-page"><div class="toc-head"><span class="toc-en">CONTENTS</span>'
            '<h1>目 录</h1></div>'
            '<p class="toc-note">页码为本册实际页序；章标题加粗，节标题缩进。</p>'
            + "".join(rows)
            + "</section>"
        )

    # ---------- 封面 ----------
    def cover(self):
        d = self.d
        pts = "".join("<li>%s</li>" % p for p in d["cover_points"])
        meta = [
            ("适用考试", "全国计算机等级考试（NCRE）二级 WPS Office 高级应用与设计"),
            ("对应模块", d["module"] + " · 操作题 " + d["score"]),
            ("覆盖课时", d["range"] + "（全 8 次课中的" + ("第 1—3 次" if d["code"] == "A" else ("第 4—6 次" if d["code"] == "B" else "第 7—8 次")) + "）"),
            ("知识体系", "%d 个知识点（%s01—%s%02d）· %d 条考纲条目" % (len(d["kps"]), d["kp_prefix"], d["kp_prefix"], len(d["kps"]), len(d["syl"]))),
            ("练习配置", "%d 道分级练习 · 4 个难度层级（★—★★★★）" % len(d["exercises"])),
            ("编写依据", "《NCRE 二级 WPS Office 高级应用与设计考试大纲（2025 年版）》"),
        ]
        mrows = "".join('<tr><th>%s</th><td>%s</td></tr>' % (k, esc(v)) for k, v in meta)
        return (
            '<section class="cover">'
            '<div class="cov-top"><span class="cov-kicker">国家计算机等级考试二级 · WPS Office 高级应用与设计</span>'
            '<span class="cov-badge">实操训练 · %s</span></div>'
            '<div class="cov-mark">%s</div>'
            '<div class="cov-part">%s</div>'
            '<h1 class="cov-title">%s</h1>'
            '<div class="cov-sub">%s</div>'
            '<ul class="cov-points">%s</ul>'
            '<table class="cov-meta">%s</table>'
            '<div class="cov-foot"><span>大连财经学院 · 计算机国家二级考试（WPS 类）课程组</span>'
            '<span>2026 年 10 月 · 第 1 版</span></div>'
            "</section>"
        ) % (esc(d["score"]), esc(d["code"]), esc(d["part"]), esc(d["name"]), esc(d["subtitle"]), pts, mrows)

    # ---------- 使用说明（前置页） ----------
    def front(self):
        d = self.d
        intro = "".join("<p>%s</p>" % t for t in d["intro"])
        how = "".join(
            '<div class="how-row"><div class="how-t">%s</div><div class="how-c">%s</div></div>' % (esc(a), b)
            for a, b in d["howto"]
        )
        rules = "".join(
            '<tr><td class="c"><b>%s</b></td><td>%s</td></tr>' % (esc(a), b) for a, b in d["rule"]
        )
        pano = "".join(
            '<tr class="%s"><td class="c">%s</td><td>%s</td><td>%s</td><td class="c">%s</td><td class="c">%s</td><td class="c">%s</td></tr>'
            % ("on" if on else "", no, esc(n), esc(t), esc(m), esc(s), "● 本册" if on else "")
            for no, n, t, m, s, on in d["panorama"]
        )
        top_cov = {c for e in d["exercises"] if e["star"] >= 3 for c in e["covers"]}
        cov_pct = int(round(len(top_cov) * 100.0 / len(d["kps"])))
        chaps = [
            ("第一章", "本部分课程内容", "每次课的四个小节、核心内容、操作路径与易错点", "上课前预习；课后复盘"),
            ("第二章", "考试知识点总结", "%d 个知识点的精确参数、掌握要求与考频" % len(d["kps"]), "考前一周集中背参数"),
            ("第三章", "知识点与练习的对应关系", "双向对照表与覆盖核对", "做题卡住时反查同类题"),
            ("第四章", "实操练习", "%d 道分级练习（目标／要求／预期结果／评分点）" % len(d["exercises"]), "全程，按 ★ 到 ★★★★ 顺序做"),
            ("第五章", "附录：自查、评分与速查", "自查清单、评分总表、快捷键、三周路径", "每次交卷前 5 分钟"),
        ]
        chtbl = "".join(
            '<tr><td class="c"><b>%s</b></td><td><b>%s</b></td><td class="xs">%s</td><td class="xs">%s</td></tr>'
            % (a, b, c, e) for a, b, c, e in chaps
        )
        return (
            '<section class="front">'
            '<h2 class="front-h">使用说明</h2>'
            '<div class="front-lead">%s</div>'
            '<h3 class="front-s">0.1　三种用法，按你的时间选一种</h3>'
            '<div class="how">%s</div>'
            '<h3 class="front-s">0.2　编号与命名规则</h3>'
            '<table class="tbl"><thead><tr><th style="width:88pt">项目</th><th>规则</th></tr></thead><tbody>%s</tbody></table>'
            '<h3 class="front-s pb">0.3　本册在全 8 次课中的位置</h3>'
            '<p class="mini">本套实操训练共 8 次课、32 小节，按「文字（30 分）→ 表格（30 分）→ 演示（20 分）」排列，'
            '与考试大纲的三大操作模块一一对应。三份文档结构完全一致，可单独使用，也可按顺序连读。</p>'
            '<table class="tbl pano"><thead><tr><th class="c" style="width:30pt">序</th><th style="width:46pt">次课</th>'
            '<th>主题</th><th class="c" style="width:38pt">模块</th><th class="c" style="width:42pt">分值</th>'
            '<th class="c" style="width:44pt">归属</th></tr></thead><tbody>%s</tbody></table>'
            '<h3 class="front-s">0.4　五章怎么用</h3>'
            '<p class="mini">五章不是「从头读到尾」的关系，而是五个不同场景下的工具。按右列的场景取用，效率最高。</p>'
            '<table class="tbl"><thead><tr><th class="c" style="width:44pt">章</th><th style="width:112pt">内容</th>'
            '<th>里面有什么</th><th style="width:106pt">什么时候看</th></tr></thead><tbody>%s</tbody></table>'
            '<div class="note" style="margin-top:12pt"><b>一个提醒：</b>本册的练习全部可以<b>独立完成</b>——'
            '每道题都自带可用数据、逐条要求与可核对的预期结果，不依赖其他题目或外部素材文件。'
            '若时间紧张，优先做 ★★★ 与 ★★★★ 的题目，它们覆盖了本部分 %d%% 的知识点。'
            '<br><b>配图怎么读：</b>每节「关键操作路径」后面都有一张界面示意图，'
            '橙色编号与路径条目<b>同序</b>，图下方两栏图例给出按钮全名——照编号点一遍，就是这一节的标准操作顺序；'
            '第四章开头另有一张「成稿版式基准」，是全部练习共同的交卷标准。</div>'
            "</section>"
        ) % (intro, how, rules, pano, chtbl, cov_pct)

    # ---------- 第一章 ----------
    def chapter1(self):
        d = self.d
        out = ['<section class="chap"><div class="chap-head"><div class="chap-no">第一章</div>'
               "<h1>本部分课程内容</h1>"
               '<p class="chap-lead">按次课梳理本部分 %s 的教学内容：每次课解决什么问题、四个小节各讲什么、'
               "关键操作的路径在哪里、最容易错的地方是什么。这一章回答「学什么」。</p></div>" % esc(d["range"])]
        for ci, c in enumerate(d["courses"]):
            ch = "1.%d" % (ci + 1)
            self.toc_add(2, ch, c["no"] + " · " + c["title"])
            out.append('<h2 id="c%s">%s　%s</h2>' % (ch, esc(ch), esc(c["no"] + " · " + c["title"])))
            out.append(
                '<div class="meta-line"><span class="mchip">%s</span><span class="mchip">%s</span>'
                '<span class="mchip">对应考纲 %s</span></div>' % (esc(c["hours"]), esc(d["score"]), esc(c["syl"]))
            )
            out.append('<div class="goal"><div class="goal-t">学完这次课，你要能做到</div><ul class="goal-l">')
            for g in c["goal"]:
                out.append("<li>%s</li>" % g)
            out.append("</ul></div>")

            for si, s in enumerate(c["sections"]):
                num = "%s.%d" % (ch, si + 1)
                out.append('<div class="sec">')
                out.append(
                    '<div class="sec-h"><span class="sec-no">%s</span><h3>%s</h3>'
                    '<span class="sec-syl">考纲 %s</span></div>' % (esc(num), esc(s["title"]), esc(s["know"]))
                )
                out.append('<div class="lab">核心内容</div><ul class="core">')
                for p in s["core"]:
                    out.append("<li>%s</li>" % p)
                out.append('</ul><div class="lab">关键操作路径</div><ul class="path">')
                for p in s["path"]:
                    out.append("<li>%s</li>" % p)
                out.append("</ul>")
                fig = s.get("fig")
                if fig:
                    out.append(self.figure(fig[0], fig[1], 1,
                                           "下图把本节「关键操作路径」标在真实界面上：橙色编号与路径同序，"
                                           "图例给出按钮全名，照数字依次点即可。"))
                out.append('<div class="warn"><b>易错</b><ul>')
                for p in s["warn"]:
                    out.append("<li>%s</li>" % p)
                out.append("</ul></div></div>")

            out.append('<div class="course-end">')
            for s in c["summary"]:
                out.append("<p>%s</p>" % s)
            out.append("</div>")
        out.append("</section>")
        return "".join(out)

    # ---------- 第二章 ----------
    def chapter2(self):
        d = self.d
        kps = d["kps"]
        by_syl = {}
        for k in kps:
            by_syl.setdefault(k[2], []).append(k)
        order = [s for s in d["syl"] if s in by_syl]

        # 2.1 总览
        ov = []
        for s in order:
            items = by_syl[s]
            hot = [k[1] for k in items if k[4] == "高"]
            ov.append(
                '<tr><td class="c"><b>%s</b></td><td>%s</td><td>%s</td><td class="c">%d</td><td>%s</td></tr>'
                % (esc(s), esc(d["syl"][s]), "、".join(k[0] for k in items), len(items),
                   ("、".join(hot) if hot else "—"))
            )
        total_hot = sum(1 for k in kps if k[4] == "高")

        # 2.2 详表
        rows = []
        for s in order:
            rows.append('<tr class="grp"><td colspan="5"><b>考纲 %s</b>　%s</td></tr>' % (esc(s), esc(d["syl"][s])))
            for code, name, syl, level, freq, key in by_syl[s]:
                rows.append(
                    '<tr><td class="c kpno">%s</td><td><b>%s</b><span class="kpkey">%s</span></td>'
                    '<td class="c xs">%s</td><td class="c xs"><span class="lv %s">%s</span></td>'
                    '<td class="c xs"><span class="fq f%s">%s</span></td></tr>'
                    % (esc(code), esc(name), key, esc(syl), "lv-" + {"熟练": "a", "掌握": "b", "了解": "c"}[level],
                       esc(level), {"高": "hi", "中": "md", "低": "lo"}[freq], esc(freq))
                )

        # 2.3 高频
        hot_html = []
        for i, (title, items) in enumerate(d["hot"]):
            lis = "".join("<li>%s</li>" % x for x in items)
            hot_html.append(
                '<div class="hotcard"><div class="hot-t"><span class="hot-i">%02d</span>%s</div><ul>%s</ul></div>'
                % (i + 1, esc(title), lis)
            )

        out = ['<section class="chap"><div class="chap-head"><div class="chap-no">第二章</div>'
               "<h1>考试知识点总结</h1>"
               '<p class="chap-lead">把本部分拆成 %d 个可核对的知识点，逐条标注所属考纲条目、掌握程度、考频与关键参数。'
               "这一章回答「考什么」——考前只看这一章，也应该能说清每个考点的判定标准。</p></div>" % len(kps)]

        self.toc_add(2, "2.1", "考点分布总览")
        out.append('<h2>2.1　考点分布总览</h2>')
        out.append('<p class="mini">共 %d 条考纲条目、%d 个知识点，其中高频知识点 %d 个。'
                   "「高频」指历年反复出现、必须练到闭眼能做的部分。</p>" % (len(order), len(kps), total_hot))
        out.append('<table class="tbl"><thead><tr><th class="c" style="width:44pt">考纲</th><th style="width:150pt">条目名称</th>'
                   '<th>覆盖知识点</th><th class="c" style="width:34pt">个数</th><th style="width:110pt">高频知识点</th>'
                   "</tr></thead><tbody>%s</tbody></table>" % "".join(ov))

        self.toc_add(2, "2.2", "知识点详表")
        out.append('<h2>2.2　知识点详表</h2>')
        out.append('<p class="mini">「关键要点」列给出的是<b>评分依据的精确参数</b>，不是概念解释。'
                   "背不下来时，优先背带数字与单位的那几句。</p>")
        out.append('<table class="tbl kp"><thead><tr><th class="c" style="width:34pt">编号</th>'
                   '<th>知识点与关键要点</th><th class="c" style="width:40pt">考纲</th>'
                   '<th class="c" style="width:42pt">掌握</th><th class="c" style="width:34pt">考频</th>'
                   "</tr></thead><tbody>%s</tbody></table>" % "".join(rows))

        self.toc_add(2, "2.3", "高频考点与常见扣分")
        out.append('<h2>2.3　高频考点与常见扣分</h2>')
        out.append('<p class="mini">下面每组的第一行是考点，其后的条目是<b>考场上真实发生过的扣分方式</b>。'
                   "做完练习后回来读一遍，比再做十道题有用。</p>")
        out.append('<div class="hotgrid">%s</div>' % "".join(hot_html))
        out.append("</section>")
        return "".join(out)

    # ---------- 第三章 ----------
    def chapter3(self):
        d = self.d
        kps = d["kps"]
        exs = d["exercises"]
        # 知识点 -> 练习
        kp2ex = {}
        for e in exs:
            for c in e["covers"]:
                kp2ex.setdefault(c, []).append((e["no"], e["star"]))
        rows = []
        for k in kps:
            exl = kp2ex.get(k[0], [])
            txt = "、".join(n for n, s in exl)
            star = max([s for n, s in exl], default=0)
            rows.append(
                '<tr><td class="c kpno">%s</td><td>%s</td><td class="c xs">%s</td><td>%s</td><td class="c xs">%s</td></tr>'
                % (esc(k[0]), esc(k[1]), esc(k[2]), (txt or '<span class="miss">未覆盖</span>'),
                   STAR[star] if star else "—")
            )
        # 练习 -> 知识点
        rows2 = []
        for e in exs:
            rows2.append(
                '<tr><td class="c kpno">%s</td><td><b>%s</b></td><td class="c xs">%s</td><td class="c xs">%d</td>'
                '<td class="xs">%s</td></tr>'
                % (esc(e["no"]), esc(e["title"]), STAR[e["star"]], e["mins"], "、".join(e["covers"]))
            )
        # 覆盖核对
        by_syl = {}
        for k in kps:
            by_syl.setdefault(k[2], []).append(k[0])
        cov = []
        for s in [x for x in d["syl"] if x in by_syl]:
            codes = by_syl[s]
            covered = [c for c in codes if kp2ex.get(c)]
            exset = []
            for c in codes:
                for n, _ in kp2ex.get(c, []):
                    if n not in exset:
                        exset.append(n)
            cov.append(
                '<tr><td class="c"><b>%s</b></td><td class="xs">%s</td><td class="c">%d</td>'
                '<td class="c"><b class="%s">%d</b></td><td>%s</td></tr>'
                % (esc(s), esc(d["syl"][s]), len(codes), "ok" if len(covered) == len(codes) else "miss",
                   len(covered), "、".join(sorted(exset)))
            )
        all_cov = sum(1 for k in kps if kp2ex.get(k[0]))

        out = ['<section class="chap"><div class="chap-head"><div class="chap-no">第三章</div>'
               "<h1>知识点与练习的对应关系</h1>"
               '<p class="chap-lead">本章给出双向对照：从知识点查该做哪道题，从题查它考了哪些知识点。'
               "对照表同时是一张<b>覆盖核对表</b>——%d 个知识点全部有对应练习，%d 条考纲条目全部落到具体练习上。</p></div>"
               % (len(kps), len(d["syl"]))]

        self.toc_add(2, "3.1", "正向对照：知识点 → 练习")
        out.append('<h2>3.1　正向对照：知识点 → 练习</h2>')
        out.append('<p class="mini">用法：某道题做错时，在下表找到该知识点，看它还出现在哪几道题中，'
                   "换一道题再验证一次是否真的掌握。</p>")
        out.append('<table class="tbl"><thead><tr><th class="c" style="width:34pt">编号</th>'
                   '<th style="width:140pt">知识点</th><th class="c" style="width:40pt">考纲</th>'
                   '<th>对应练习</th><th class="c" style="width:52pt">最高难度</th>'
                   "</tr></thead><tbody>%s</tbody></table>" % "".join(rows))

        self.toc_add(2, "3.2", "反向对照：练习 → 知识点")
        out.append('<h2>3.2　反向对照：练习 → 知识点</h2>')
        out.append('<p class="mini">每道题的「覆盖知识点」也在正文题卡中单独列出，两处编号一致。</p>')
        out.append('<table class="tbl"><thead><tr><th class="c" style="width:40pt">练习</th>'
                   '<th>题目</th><th class="c" style="width:52pt">难度</th><th class="c" style="width:36pt">用时</th>'
                   "<th style='width:150pt'>覆盖知识点</th></tr></thead><tbody>%s</tbody></table>" % "".join(rows2))

        self.toc_add(2, "3.3", "覆盖核对与缺口检查")
        out.append('<h2>3.3　覆盖核对与缺口检查</h2>')
        out.append('<p class="mini">覆盖率 <b>%d / %d = %.0f%%</b>。每条考纲条目下的知识点均有练习承接，'
                   "不存在「讲了但没练」的条目；同一知识点在不同题目中从不同角度出现，因此不构成重复题。</p>"
                   % (all_cov, len(kps), all_cov / len(kps) * 100))
        out.append('<table class="tbl keep"><thead><tr><th class="c" style="width:44pt">考纲</th><th>条目名称</th>'
                   '<th class="c" style="width:44pt">知识点</th><th class="c" style="width:52pt">已覆盖</th>'
                   "<th style='width:120pt'>相关练习</th></tr></thead><tbody>%s</tbody></table>" % "".join(cov))
        out.append('<div class="note"><b>关于「不重复」的三条设计约束：</b>'
                   "① 每个知识点的<b>首次出现</b>放在与该知识点同名的小节练习中，后续只做组合应用；"
                   "② 同一知识点若被两道题覆盖，一道考「参数是否精确」，另一道考「与其他对象配合时的顺序」；"
                   "③ 三道综合题（含全真模拟）只做整合，不引入新的考核点。</div>")
        out.append("</section>")
        return "".join(out)

    # ---------- 第四章 ----------
    def exercise_card(self, e):
        reqs = "".join("<li>%s</li>" % r for r in e["reqs"])
        exps = "".join("<li>%s</li>" % r for r in e["expect"])
        chips = "".join('<span class="chip">%s</span>' % esc(c) for c in e["covers"])
        rub = "".join('<span class="ri">%s<b>%d</b></span>' % (esc(a), b) for a, b in e["rubric"])
        total = sum(b for a, b in e["rubric"])
        dat = ""
        if "data" in e:
            dd = e["data"]
            if "text" in dd:
                body = '<pre class="src">%s</pre>' % esc(dd["text"])
            else:
                head = dd["table"][0]
                rest = dd["table"][1:]
                body = (
                    '<table class="dt"><thead><tr>%s</tr></thead><tbody>%s</tbody></table>'
                    % ("".join("<th>%s</th>" % esc(h) for h in head),
                       "".join("<tr>%s</tr>" % "".join("<td>%s</td>" % esc(c) for c in row) for row in rest))
                )
            dat = '<div class="lab">可用数据</div><div class="databox"><div class="d-c">%s</div>%s</div>' % (
                esc(dd["caption"]), body)
        hint = ('<div class="hintbox"><b>提示</b>%s</div>' % e["hint"]) if e.get("hint") else ""
        return (
            '<article class="ex" id="%s">'
            '<div class="ex-h"><span class="ex-no">%s</span><h3>%s</h3>'
            '<span class="ex-meta">%s · %d 分钟 · %d 分</span></div>'
            '<div class="ex-body">'
            '<div class="lab f">操作目标</div><p class="goal-p">%s</p>'
            '<div class="lab">具体要求</div><ol class="req">%s</ol>'
            "%s"
            '<div class="lab">预期结果（自查用）</div><ul class="chk">%s</ul>'
            '<div class="lab">覆盖知识点</div><div class="chips">%s</div>'
            '<div class="rubwrap"><div class="lab">评分点（满分 %d 分，按点给分）</div>'
            '<div class="rubline">%s</div></div>'
            "%s"
            "</div></article>"
        ) % (esc(e["no"]), esc(e["no"]), esc(e["title"]), STAR[e["star"]], e["mins"], total,
             e["goal"], reqs, dat, exps, chips, total, rub, hint)

    def chapter4(self):
        d = self.d
        exs = d["exercises"]
        # 练习总览表（按难度分组）
        idx = []
        for gi, (num, name, lead) in enumerate(d["exercise_groups"]):
            star = gi + 1
            group = [e for e in exs if e["star"] == star]
            if not group:
                continue
            idx.append(
                '<tr class="grp"><td colspan="6"><b>%s　%s</b>　<span class="xs">%s 共 %d 题</span></td></tr>'
                % (esc(num), esc(name), esc(lead), len(group))
            )
            for e in group:
                idx.append(
                    '<tr><td class="c kpno">%s</td><td>%s</td><td class="c xs">%s</td>'
                    '<td class="c xs">%d 分钟</td><td class="c xs">%d</td><td class="xs">%s</td></tr>'
                    % (esc(e["no"]), esc(e["title"]), STAR[e["star"]], e["mins"],
                       sum(b for a, b in e["rubric"]), "、".join(e["covers"][:8]) + ("…" if len(e["covers"]) > 8 else ""))
                )
        out = ['<section class="chap"><div class="chap-head"><div class="chap-no">第四章</div>'
               "<h1>实操练习</h1>"
               '<p class="chap-lead">%d 道练习按难度分四级递进：★ 单点基础 → ★★ 组合应用 → ★★★ 结构综合 → ★★★★ 全真模拟。'
               "每题都给出操作目标、逐条要求、可核对的预期结果与评分点，做完即可自评。"
               "练习彼此独立，可按顺序做，也可按第三章的对照表挑着做。</p></div>" % len(exs)]
        self.toc_add(2, "4.0", "练习总览")
        out.append('<h2>4.0　练习总览</h2>')
        out.append('<p class="mini">「覆盖知识点」列只显示前 8 个编号，完整清单见每题末尾的标签与第三章对照表。'
                   "满分列即该题按点给分的合计分值，用于自评换算。</p>")
        out.append('<table class="tbl"><thead><tr><th class="c" style="width:44pt">编号</th><th>题目</th>'
                   '<th class="c" style="width:46pt">难度</th><th class="c" style="width:42pt">用时</th>'
                   '<th class="c" style="width:32pt">满分</th><th style="width:150pt">覆盖知识点</th>'
                   "</tr></thead><tbody>%s</tbody></table>" % "".join(idx))
        out.append('<div class="note"><b>做题时的三条建议：</b>'
                   "① 先读「操作目标」，30 秒内说清这道题要交什么；② 做到一半卡住不要立刻看提示，"
                   "先按菜单自己找 2 分钟，找得到就是真会；③ 做完只核「预期结果」，不逐字比对步骤——"
                   "步骤可以有别的走法，结果只有一个。</div>")
        if d.get("figres"):
            out.append(self.figure(
                d["figres"], d.get("figres_cap", ""), 4,
                "动手之前先看这张图：它是本册所有练习共同的「交卷标准」。每做完一题，"
                "把成稿和这张图逐项对照——要素齐了，分数就稳了。"))
        for e in exs:
            out.append(self.exercise_card(e))
        # 练习进度记录表（打印后手写）
        self.toc_add(2, "4.5", "练习进度记录表")
        out.append('<h2>4.5　练习进度记录表</h2>')
        out.append('<p class="mini">建议把这一页单独打印，每做完一道题就填一行。'
                   "「需重做」栏打勾的题，隔一周再做一次——第二遍的正确率才是真实水平。</p>")
        rec = []
        for e in exs:
            rec.append(
                '<tr><td class="c kpno">%s</td><td>%s</td><td class="c xs">%s</td>'
                '<td class="c">%d</td><td class="blank"></td><td class="blank"></td><td class="blank"></td></tr>'
                % (esc(e["no"]), esc(e["title"]), STAR[e["star"]],
                   sum(b for a, b in e["rubric"]))
            )
        out.append('<table class="tbl rec"><thead><tr><th class="c" style="width:44pt">练习</th><th>题目</th>'
                   '<th class="c" style="width:48pt">难度</th><th class="c" style="width:34pt">满分</th>'
                   '<th class="c" style="width:64pt">完成日期</th><th class="c" style="width:56pt">自评得分</th>'
                   '<th class="c" style="width:48pt">需重做</th></tr></thead><tbody>%s'
                   '<tr class="sum"><td colspan="3"><b>合计</b></td><td class="c"><b>%d</b></td>'
                   '<td></td><td></td><td></td></tr></tbody></table>'
                   % ("".join(rec), sum(sum(b for a, b in e["rubric"]) for e in exs)))
        out.append("</section>")
        return "".join(out)

    # ---------- 第五章 ----------
    def chapter5(self):
        d = self.d
        exs = d["exercises"]
        ck = "".join('<li><span class="box"></span>%s</li>' % x for x in d["checklist"])
        rub = "".join(
            '<tr><td class="c kpno">%s</td><td>%s</td><td class="c">%d</td><td class="c blank"></td><td></td></tr>'
            % (esc(e["no"]), esc(e["title"]), sum(b for a, b in e["rubric"])) for e in exs
        )
        tot = sum(sum(b for a, b in e["rubric"]) for e in exs)
        keys = "".join(
            '<tr><td class="k"><b>%s</b></td><td>%s</td></tr>' % (esc(a), esc(b)) for a, b in d["shortcuts"]
        )
        # 学习路径：按练习分三周
        n = len(exs)
        plan = [
            ("第 1 周", "跟课 + 单点练习", "、".join(e["no"] for e in exs[: max(3, n // 3)]), "每题能在建议用时的 1.2 倍内完成"),
            ("第 2 周", "组合与结构题", "、".join(e["no"] for e in exs[max(3, n // 3): max(6, n * 2 // 3)]), "自评得分 ≥ 满分的 80%"),
            ("第 3 周", "综合与限时", "、".join(e["no"] for e in exs[max(6, n * 2 // 3):]), "全真模拟 ≥ 满分的 85%，且不超时"),
        ]
        planrows = "".join(
            "<tr><td class=\"c\"><b>%s</b></td><td>%s</td><td class=\"xs\">%s</td><td class=\"xs\">%s</td></tr>" % p
            for p in plan
        )
        out = ['<section class="chap"><div class="chap-head"><div class="chap-no">第五章</div>'
               "<h1>附录：自查、评分与速查</h1>"
               '<p class="chap-lead">交卷前的 5 分钟决定 3—5 分。本章的四张表建议打印出来放在手边：'
               "自查清单（逐项打勾）、评分总表（自评记录）、快捷键速查、三周练习路径。</p></div>"]
        out.append('<div class="note"><b>先读这一段：</b>本册所有参数以 <b>WPS Office 教育考试专用版（Windows 10）</b>为准，'
                   "个人版菜单名称可能略有差异，按<b>功能名称</b>定位即可；文件命名一律为「学号-姓名-练习编号」，"
                   "未按要求命名按 0 分处理。</div>")

        self.toc_add(2, "5.1", "交卷自查清单")
        out.append('<h2>5.1　交卷自查清单</h2>')
        out.append('<p class="mini">做完任何一道题，都按这份清单从头念一遍。清单里每一条都对应过真实失分。</p>')
        out.append('<ul class="cklist">%s</ul>' % ck)

        self.toc_add(2, "5.2", "自评评分总表")
        out.append('<h2>5.2　自评评分总表</h2>')
        out.append('<p class="mini">做完一题填一次，两周后回看这张表，就知道该补哪一块。</p>')
        out.append('<table class="tbl"><thead><tr><th class="c" style="width:44pt">练习</th><th>题目</th>'
                   '<th class="c" style="width:40pt">满分</th><th class="c" style="width:40pt">得分</th>'
                   '<th style="width:120pt">主要失分点</th></tr></thead><tbody>%s'
                   '<tr class="sum"><td colspan="2"><b>合计</b></td><td class="c"><b>%d</b></td>'
                   '<td class="c"></td><td></td></tr></tbody></table>' % (rub, tot))

        self.toc_add(2, "5.3", "快捷键与操作速查")
        out.append('<h2>5.3　快捷键与操作速查</h2>')
        out.append('<p class="mini">考场用快捷键不是为了快，是为了<b>少找菜单</b>——找不到菜单时最容易慌。</p>')
        out.append('<table class="tbl keys"><tbody>%s</tbody></table>' % keys)

        self.toc_add(2, "5.4", "三周练习路径")
        out.append('<h2>5.4　三周练习路径</h2>')
        out.append('<p class="mini">按下面的顺序做，不要跳。前两周解决「会不会」，第三周解决「来不来得及」。</p>')
        out.append('<table class="tbl"><thead><tr><th class="c" style="width:46pt">周次</th><th style="width:100pt">目标</th>'
                   '<th>练习</th><th style="width:120pt">达标标准</th></tr></thead><tbody>%s</tbody></table>' % planrows)
        out.append("</section>")
        return "".join(out)

    # ---------- 组装 ----------
    def css(self):
        return CSS_TMPL % {
            "P": self.p, "D": self.deep, "T": self.tint, "L": self.line,
        }

    def build(self, pm):
        # 先登记章目录，再渲染（章内会继续登记节）
        self.toc_entries = []
        self._figseq = {}
        self.toc_add(1, "第一章", "本部分课程内容")
        c1 = None
        # 章内 h2 在渲染时登记，因此先生成各章 HTML，再渲染目录
        body1 = self.chapter1()
        self.toc_add(1, "第二章", "考试知识点总结")
        body2 = self.chapter2()
        self.toc_add(1, "第三章", "知识点与练习的对应关系")
        body3 = self.chapter3()
        self.toc_add(1, "第四章", "实操练习")
        body4 = self.chapter4()
        self.toc_add(1, "第五章", "附录：自查、评分与速查")
        body5 = self.chapter5()
        toc = self.render_toc(pm)
        html = (
            "<!DOCTYPE html><html lang=\"zh-CN\"><head><meta charset=\"utf-8\">"
            "<title>%s</title><style>%s</style></head><body>%s%s%s%s%s%s%s%s</body></html>"
            % (esc(self.d["part"] + " · " + self.d["name"] + " 实操训练"), self.css(),
               self.cover(), self.front(), toc, body1, body2, body3, body4, body5)
        )
        return html


CSS_TMPL = r"""
@page { size: A4; }
* { box-sizing: border-box; }
html, body { margin:0; padding:0; }
body {
  orphans: 2; widows: 2;
  font-family: "Microsoft YaHei", "PingFang SC", "Hiragino Sans GB", sans-serif;
  font-size: 10pt; line-height: 1.78; color: #1f2a37;
  -webkit-font-smoothing: antialiased;
}
h1,h2,h3,h4 { margin:0; font-weight:700; color:#16202c; }
p { margin: 0 0 6pt; }
b, strong { font-weight: 700; }
code, kbd { font-family: Consolas, "Courier New", monospace; font-size: .92em; }
code { background:#f2f5f9; border:1px solid #e3e9f0; border-radius:2pt; padding:0 2pt; color:#243448; }

/* ============ 封面 ============ */
.cover { page-break-after: always; padding-top: 18pt; display:flex; flex-direction:column; min-height: 700pt; }
.cov-top { display:flex; justify-content:space-between; align-items:center;
  border-bottom: 2.4pt solid %(P)s; padding-bottom: 7pt; }
.cov-kicker { font-size: 8.4pt; letter-spacing:.06em; color:#5b6876; font-weight:600; }
.cov-badge { font-size:8.4pt; font-weight:700; color:#fff; background:%(P)s; padding:2.5pt 8pt; border-radius:2pt; }
.cov-mark { margin-top: 26pt; font-size: 84pt; font-weight:900; line-height:1;
  color: %(L)s; letter-spacing: -.01em; }
.cov-part { margin-top: 6pt; font-size: 15pt; font-weight:800; letter-spacing:.42em; color:%(P)s; }
.cov-title { font-size: 46pt; font-weight:900; margin: 4pt 0 8pt; letter-spacing:.02em; }
.cov-sub { font-size: 11.8pt; color:#3d4a58; font-weight:600; line-height:1.62; max-width: 400pt;
  padding-left: 11pt; border-left: 3pt solid %(L)s; }
.cov-points { list-style:none; margin: 22pt 0 0; padding: 0; }
.cov-points li { font-size: 9.8pt; color:#33404e; padding-left: 16pt; position:relative; margin-bottom: 5pt;
  line-height:1.65; }
.cov-points li:before { content:""; position:absolute; left:2pt; top:6.4pt; width:5pt; height:5pt;
  background:%(P)s; border-radius:50%%; }
.cov-meta { width:100%%; border-collapse:collapse; margin-top: 26pt; font-size:8.8pt; }
.cov-meta th { width: 66pt; text-align:left; font-weight:700; color:%(D)s; background:%(T)s;
  padding: 5.5pt 7pt; border-bottom:1px solid %(L)s; vertical-align:top; }
.cov-meta td { padding: 5.5pt 7pt; border-bottom:1px solid %(L)s; color:#33404e; }
.cov-foot { margin-top: auto; padding-top: 7pt; border-top: 1px solid %(L)s; padding-top: 7pt;
  display:flex; justify-content:space-between; font-size:8.4pt; color:#6b7785; }

/* ============ 前置页 ============ */
.front { page-break-after: always; }
.front-h { font-size: 20pt; font-weight:900; padding-bottom: 8pt; border-bottom: 2.4pt solid %(P)s;
  margin-bottom: 14pt; }
.front-lead p { font-size: 10pt; line-height: 1.85; text-align: justify; margin-bottom: 8pt; }
.front-s { font-size: 12pt; color:%(D)s; margin: 18pt 0 7pt; padding-left: 8pt;
  border-left: 4pt solid %(P)s; }
.pb { page-break-before: always; }
.how { border:1px solid %(L)s; border-radius:3pt; overflow:hidden; }
.how-row { display:flex; border-bottom:1px solid %(L)s; }
.how-row:last-child { border-bottom:0; }
.how-t { flex:none; width: 96pt; background:%(T)s; color:%(D)s; font-weight:700; font-size:9.2pt;
  padding: 7pt 9pt; }
.how-c { flex:1; font-size:9.4pt; padding: 7pt 10pt; color:#33404e; line-height:1.7; }

/* ============ 通用表格 ============ */
table { width:100%%; border-collapse: collapse; }
.tbl { font-size: 8.6pt; margin: 5pt 0 10pt; }
.tbl th { background:%(T)s; color:%(D)s; font-weight:700; text-align:left; padding: 4.6pt 6pt;
  border:1px solid %(L)s; line-height:1.5; }
.tbl td { padding: 4.4pt 6pt; border:1px solid #e4e9ef; vertical-align: top; line-height:1.6; }
.tbl tr { page-break-inside: avoid; }
.tbl tbody tr:nth-child(even) td { background:#fafbfd; }
.tbl tr.grp td { background:%(T)s; color:%(D)s; font-size:8.8pt; border-color:%(L)s; }
.tbl tr.on td { background:%(T)s; }
.tbl td.c, .tbl th.c { text-align:center; }
.tbl .k { width: 132pt; background:#f7f9fc; }
.c { text-align:center; }
.xs { font-size: 8pt; }
.tbl.keep { page-break-inside: avoid; }
.mini { font-size: 9.2pt; color:#4b5866; margin: 2pt 0 8pt; line-height:1.7; }

/* ============ 目录 ============ */
.toc-page { page-break-after: always; }
.toc-head { border-bottom: 2.4pt solid %(P)s; padding-bottom: 8pt; margin-bottom: 6pt; }
.toc-en { font-size: 7.6pt; letter-spacing:.34em; color:#8a97a8; font-weight:700; }
.toc-head h1 { font-size: 24pt; font-weight:900; letter-spacing:.24em; margin-top: 2pt; }
.toc-note { font-size: 8.2pt; color:#7c8899; margin: 4pt 0 14pt; }
.toc-row { display:flex; align-items:baseline; margin-bottom: 9pt; }
.toc-row.lv1 { margin-top: 15pt; }
.toc-row.lv1 .toc-tt { font-weight:800; font-size: 11pt; color:#16202c; }
.toc-row.lv2 { padding-left: 18pt; }
.toc-row.lv2 .toc-tt { font-size: 9.4pt; color:#3d4a58; }
.toc-num { flex:none; width: 46pt; font-weight:700; color:%(P)s; font-size:9pt; }
.toc-row.lv1 .toc-num { font-size: 10pt; }
.toc-tt { }
.toc-dot { flex:1; border-bottom: 1.2px dotted #aab8c8; margin: 0 6pt 3.4pt; }
.toc-pg { flex:none; width: 24pt; text-align:right; font-weight:700; color:#3d4a58; }

.lab { page-break-after: avoid; }
/* ============ 章 ============ */
.chap { page-break-before: always; }
.chap-head { border-left: 6pt solid %(P)s; padding-left: 15pt; margin-bottom: 20pt; }
.chap-no { font-size: 9pt; font-weight:800; letter-spacing:.3em; color:%(P)s; }
.chap-head h1 { font-size: 25pt; font-weight:900; margin: 3pt 0 8pt; letter-spacing:.02em; }
.chap-lead { font-size: 9.6pt; color:#4b5866; line-height:1.8; margin:0; text-align: justify; }
.chap h2 { font-size: 14pt; color:%(D)s; margin: 22pt 0 8pt; padding-bottom: 5pt;
  border-bottom: 1px solid %(L)s; page-break-after: avoid; }
.chap h2:first-of-type { margin-top: 0; }
.chap h3 { font-size: 11.4pt; color:#1b2836; }

/* ============ 次课 ============ */
.meta-line { margin: 2pt 0 10pt; }
.mchip { display:inline-block; font-size:7.8pt; font-weight:700; color:%(D)s; background:%(T)s;
  border:1px solid %(L)s; border-radius:2pt; padding: 1.4pt 6pt; margin: 0 5pt 4pt 0; }
.goal { background:#fbfcfe; border:1px solid #e6ebf1; border-radius:3pt; padding: 9pt 12pt; margin-bottom: 12pt; }
.goal-t { font-size: 8.6pt; font-weight:800; color:%(P)s; letter-spacing:.08em; margin-bottom: 5pt; }
.goal-l { margin:0; padding-left: 13pt; }
.goal-l li { font-size: 9.3pt; line-height:1.75; margin-bottom: 3pt; color:#2b3746; }
.sec { padding-top: 10pt; margin-bottom: 14pt; border-top: 1px dashed #dfe5ec; }
.sec-h { display:flex; align-items:baseline; gap:7pt; margin-bottom: 6pt; page-break-after: avoid; }
.sec-no { flex:none; font-size: 8pt; font-weight:800; color:#fff; background:%(P)s;
  padding: 1.6pt 5pt; border-radius:2pt; }
.sec-h h3 { flex:1; font-size: 11.2pt; }
.sec-syl { flex:none; font-size: 7.6pt; color:#7c8899; font-weight:700; }
.lab { font-size: 8.1pt; font-weight:800; color:%(P)s; letter-spacing:.1em; margin: 6.5pt 0 2pt; }
.lab:before { content:""; display:inline-block; width:4pt; height:4pt; background:%(P)s;
  margin-right: 5pt; vertical-align: 1.4pt; }
.lab.f { margin-top: 0; }
ul.core { margin:0; padding-left: 13pt; }
ul.core li { font-size: 9.3pt; line-height:1.72; margin-bottom: 2.4pt; color:#26313d; }
ul.core li::marker { color:%(P)s; }
ul.path { margin:0; padding: 6pt 9pt 6pt 0; list-style:none; background:#f7f9fc;
  border-left: 2.4pt solid %(L)s; }
ul.path li { font-size: 8.8pt; line-height:1.68; color:#33404e; padding-left: 16pt; position:relative;
  margin-bottom: 2pt; font-family: "Microsoft YaHei", sans-serif; }
ul.path li:before { content:"›"; position:absolute; left:7pt; color:%(P)s; font-weight:800; }
.warn { page-break-inside: avoid; background:#fffaf1; border-left: 2.6pt solid #e0a341; padding: 6pt 10pt; margin-top: 7pt; }
.warn b { font-size: 8.2pt; color:#a2621a; letter-spacing:.08em; }
.warn ul { margin: 2pt 0 0; padding-left: 13pt; }
.warn li { font-size: 8.8pt; line-height:1.68; color:#4a3a22; margin-bottom: 1.5pt; }
.course-end { page-break-inside: avoid; background:%(T)s; border-left: 3pt solid %(P)s; padding: 8pt 12pt; margin: 6pt 0 4pt; }
.course-end p { font-size: 9.2pt; line-height:1.75; margin: 0 0 4pt; color:#2b3746; }
.course-end p:last-child { margin-bottom: 0; }

/* ============ 知识点表 ============ */
.tbl.kp td { font-size: 8.4pt; }
.tbl .lv, .tbl .fq { white-space: nowrap; }
.kpno { font-weight:800; color:%(P)s; white-space:nowrap; }
.kpkey { display:block; font-size: 8.1pt; color:#5b6876; line-height:1.62; margin-top: 1.5pt; }
.lv { display:inline-block; font-size:7.4pt; font-weight:700; border-radius:2pt; padding: 0.6pt 3.4pt; }
.lv-a { background:%(T)s; color:%(D)s; }
.lv-b { background:#eef1f5; color:#54626f; }
.lv-c { background:#f5f6f8; color:#8a97a8; }
.fq { font-size:7.6pt; font-weight:800; }
.fhi { color:#b3261e; } .fmd { color:#9a5b06; } .flo { color:#8a97a8; }
.miss { color:#b3261e; font-weight:800; }
.ok { color:#0f766e; }

/* ============ 高频卡 ============ */
.hotgrid { display:grid; grid-template-columns: 1fr 1fr; column-gap: 10pt; row-gap: 6pt; }
.hotcard { border:1px solid #e6ebf1; border-radius:3pt; padding: 5pt 10pt 4pt; margin-bottom: 5.5pt;
  page-break-inside: avoid; }
.hot-t { font-size: 9.2pt; font-weight:800; color:#1b2836; margin-bottom: 2pt; }
.hot-i { display:inline-block; font-size:7.6pt; font-weight:800; color:#fff; background:%(P)s;
  width: 15pt; text-align:center; border-radius:2pt; margin-right: 6pt; vertical-align: 1pt; }
.hotcard ul { margin:0; padding-left: 14pt; }
.hotcard li { font-size: 8.75pt; line-height:1.56; color:#3d4a58; margin-bottom: 1pt; }

/* ============ 练习卡 ============ */
.ex { border:1px solid #dde4ec; border-radius:4pt; margin: 0 0 12pt; }
.ex-h { background:%(T)s; border-bottom:1px solid %(L)s; padding: 5.5pt 11pt;
  display:flex; align-items:baseline; gap: 8pt; page-break-after: avoid; }
.ex-no { flex:none; background:%(P)s; color:#fff; font-size: 8.6pt; font-weight:800;
  padding: 2pt 7pt; border-radius:2pt; letter-spacing:.04em; }
.ex-h h3 { flex:1; font-size: 11.2pt; line-height:1.45; }
.ex-meta { flex:none; font-size: 8pt; color:#5b6876; font-weight:700; white-space:nowrap; }
.ex-body { padding: 7pt 11pt 8pt; }
.goal-p { font-size: 9.2pt; line-height:1.6; color:#2b3746; margin: 0; }
ol.req { margin: 0; padding-left: 15pt; }
.databox, .rubwrap, .hintbox { page-break-inside: avoid; }
ol.req li, ul.chk li, ul.core li, .hotcard li, .goal-l li { page-break-inside: avoid; }
ol.req li { font-size: 8.85pt; line-height:1.58; margin-bottom: 2pt; color:#24303d; }
ol.req li::marker { font-weight:800; color:%(P)s; }
ul.chk { margin:0; padding:0; list-style:none; }
ul.chk li { font-size: 8.8pt; line-height:1.54; color:#2b3746; padding-left: 13pt; position:relative;
  margin-bottom: 1.4pt; }
ul.chk li:before { content:"▢"; position:absolute; left:0; top:0; color:%(P)s; font-size:8pt; }
.chips { margin-top: 1pt; }
.chip { display:inline-block; font-size:7.6pt; font-weight:700; color:%(D)s; background:%(T)s;
  border:1px solid %(L)s; border-radius:2pt; padding: 0.8pt 4.4pt; margin: 0 3pt 1.5pt 0; }
.rubwrap { margin-top: 2pt; page-break-inside: avoid; }
.rubline { background:#f8fafc; border:1px solid #e7edf4; border-radius:3pt; padding: 5pt 9pt 3pt;
  font-size: 8.3pt; line-height:1.72; color:#2b3746; }
.rubline .ri { display:inline-block; margin: 0 12pt 2pt 0; }
.rubline .ri b { font-weight:800; color:%(P)s; margin-left: 3pt; }
table.rub { width:100%%; font-size: 8.1pt; margin-top: 2pt; }
table.rub th { background:%(T)s; color:%(D)s; font-weight:700; padding: 2.4pt 6pt; border:1px solid #e6ebf1; text-align:left; }
table.rub th.c { text-align:center; }
table.rub td { border:1px solid #e6ebf1; padding: 2.6pt 7pt; }
table.rub td.c, table.rub th.c { width: 26pt; }
.databox { border:1px dashed %(L)s; background:#fcfdfe; padding: 5pt 8pt 4pt; border-radius:3pt; }
.d-c { font-size: 7.8pt; color:#6b7785; margin-bottom: 3pt; font-weight:700; }
table.dt { font-size: 8pt; width:auto; min-width: 62%%; }
table.dt th { background:#eef2f7; color:#33404e; padding: 2.6pt 7pt; border:1px solid #e0e6ee; text-align:center; }
table.dt td { padding: 2.4pt 7pt; border:1px solid #e6ebf1; text-align:center; }
pre.src { font-family: "Microsoft YaHei", sans-serif; font-size: 8.3pt; line-height:1.52;
  white-space: pre-wrap; margin:0; color:#2b3746; }
.hintbox { margin-top: 5pt; background:#f4f8fd; border-left: 2.6pt solid %(P)s; padding: 5pt 9pt;
  font-size: 8.6pt; line-height:1.6; color:#2b3746; }
.hintbox b { color:%(P)s; margin-right: 5pt; font-size:8.2pt; letter-spacing:.08em; }


/* ============ 配图 ============ */
.figlead { font-size: 8.6pt; color: #4b5866; margin: 7pt 0 4pt; page-break-after: avoid; }
.fig { margin: 4pt 0 10pt; page-break-inside: avoid; }
.figbox { border: 1px solid #e2e7ee; border-radius: 3pt; padding: 3pt; background: #ffffff; }
.figbox svg { display: block; width: 100%%; height: auto; }
.figcap { font-size: 8.2pt; color: #5b6876; margin-top: 3.5pt; page-break-after: avoid; }
.figcap b { color: %(D)s; font-weight: 700; margin-right: 2pt; }
.figleg { display: grid; grid-template-columns: 1fr 1fr; column-gap: 12pt; row-gap: 2pt;
  margin-top: 2pt; page-break-inside: avoid; }
.figleg .fl { font-size: 8.2pt; line-height: 1.5; color: #33404e; padding-left: 15pt; position: relative; }
.figleg .fl i { position: absolute; left: 0; top: 0.8pt; width: 11pt; height: 11pt; border-radius: 50%%;
  background: #e8710a; color: #ffffff; font-style: normal; font-size: 7pt; font-weight: 700;
  text-align: center; line-height: 11pt; }

/* ============ 附录 ============ */
ul.cklist { margin:0; padding:0; list-style:none; columns: 2; column-gap: 20pt; }
ul.cklist li { font-size: 8.8pt; line-height:1.66; color:#24303d; padding-left: 14pt; position:relative;
  margin-bottom: 4.5pt; break-inside: avoid; }
ul.cklist .box { position:absolute; left:0; top: 2pt; width: 7pt; height: 7pt;
  border: 1px solid %(P)s; border-radius: 1pt; }
table.tbl td.blank { height: 16pt; }
.tbl tr.sum td { background:%(T)s; }
.tbl.rec td { padding: 3.5pt 6pt; }
.tbl.rec td.blank { height: 17pt; }
.tbl.keys td { font-size: 8.6pt; }
.tbl.keys td.k { background:#f7f9fc; }
.note { background:#f7f9fc; border:1px solid #e4e9ef; border-radius:3pt; padding: 9pt 12pt;
  font-size: 9pt; line-height:1.75; color:#2b3746; margin-top: 10pt; }
.note b { color:%(D)s; }
"""
