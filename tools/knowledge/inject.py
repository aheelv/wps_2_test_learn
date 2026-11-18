# -*- coding: utf-8 -*-
"""背景知识功能一键接入：数据 JS + 弹窗组件 + CSS + 8 课页按钮。

产物：
  assets/knowledge-data.js   72 题讲解数据（window.WPS_KNOWLEDGE）
  assets/knowledge.js        弹窗逻辑（无需 fetch，兼容 file://）
  assets/knowledge.css       弹窗样式（light 主题）
  8 个课页                  每题头部插入「背景知识」按钮 + 引入资源

用法：python tools/knowledge/inject.py [--check]
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
K = Path(__file__).parent
ASSETS = ROOT / 'assets'
PAGES = ['入门实操课.html', '实操-文字2.html', '实操-文字3.html',
         '实操-表格1.html', '实操-表格2.html', '实操-表格3.html',
         '实操-演示1.html', '实操-演示2.html']

FIELD_LABELS = [
    ('points', '核心考点', 'kp'),
    ('background', '背景知识', 'bg'),
    ('principle', '操作原理', 'pr'),
    ('formula', '公式与参数详解', 'fm'),
    ('example', '结合本题的例题', 'ex'),
    ('mistakes', '常见易错点', 'er'),
    ('exam', '考试中的考法', 'xm'),
]

BTN_HTML = ('<button class="kb-btn" type="button" data-knowledge="%s" '
            'title="查看本题的背景知识与考点讲解"><span aria-hidden="true">✦</span> 背景知识</button>')

MODAL_HTML = '''
<!-- 背景知识弹窗（由 assets/knowledge.js 驱动） -->
<div class="kb-modal" id="kbModal" role="dialog" aria-modal="true" aria-labelledby="kbTitle" hidden>
  <div class="kb-backdrop" data-kb-close></div>
  <div class="kb-panel" role="document">
    <header class="kb-head">
      <div class="kb-head-txt">
        <span class="kb-tag">背景知识 · 考前精读</span>
        <h3 id="kbTitle"></h3>
        <p id="kbSub"></p>
      </div>
      <button class="kb-close" type="button" data-kb-close aria-label="关闭">×</button>
    </header>
    <nav class="kb-nav" id="kbNav" aria-label="知识板块导航"></nav>
    <div class="kb-body" id="kbBody"></div>
    <footer class="kb-foot">
      <span>内容依据 2025 年版考试大纲与该题素材编写，功能口径限定 WPS Office 教育考试专用版</span>
      <button class="kb-foot-btn" type="button" data-kb-close>关闭</button>
    </footer>
  </div>
</div>
'''

CSS = '''
/* ==========================================================================
   背景知识弹窗 · 72 题逐题精读（light 主题，配合 style.css / practice.css）
   ========================================================================== */
.kb-btn{
  font: inherit; font-size:12.5px; font-weight:700; color:#fff;
  background:var(--brand-2); border:1px solid var(--brand-2);
  border-radius:8px; padding:4px 11px; cursor:pointer; white-space:nowrap;
  transition:background .15s, transform .15s;
}
.kb-btn span{color:#ffd9a0;margin-right:2px}
.kb-btn:hover{background:#16324f;border-color:#16324f;transform:translateY(-1px)}
.kb-btn:focus-visible,.kb-close:focus-visible,.kb-nav button:focus-visible{outline:3px solid #f2a33c;outline-offset:2px}

.kb-modal{position:fixed;inset:0;z-index:9999;display:flex;align-items:center;justify-content:center;padding:20px}
.kb-modal[hidden]{display:none}
.kb-backdrop{position:absolute;inset:0;background:rgba(16,32,54,.55);backdrop-filter:blur(2px)}
.kb-panel{
  position:relative;width:min(880px,100%);max-height:min(88vh,940px);
  display:flex;flex-direction:column;background:var(--surface);
  border:1px solid var(--line);border-radius:16px;box-shadow:var(--shadow-l);overflow:hidden;
}
.kb-head{display:flex;align-items:flex-start;gap:14px;padding:20px 24px 16px;
  background:linear-gradient(135deg,#16324f,#1f4a75);color:#fff;flex:none}
.kb-head-txt{flex:1;min-width:0}
.kb-tag{display:inline-block;font-size:11.5px;font-weight:800;letter-spacing:.08em;
  background:rgba(255,255,255,.14);border:1px solid rgba(255,255,255,.26);
  color:#ffe0bd;border-radius:99px;padding:2px 10px;margin-bottom:8px}
.kb-head h3{margin:0 0 4px;color:#fff;font-size:20px;font-weight:800;line-height:1.4}
.kb-head p{margin:0;font-size:13px;color:#c8dbec}
.kb-close{flex:none;width:34px;height:34px;border-radius:9px;border:1px solid rgba(255,255,255,.35);
  background:rgba(255,255,255,.1);color:#fff;font-size:23px;line-height:1;cursor:pointer}
.kb-close:hover{background:rgba(255,255,255,.22)}

.kb-nav{display:flex;gap:6px;flex-wrap:wrap;padding:11px 24px;background:#f3f7fc;
  border-bottom:1px solid var(--line);flex:none}
.kb-nav button{font:inherit;font-size:12.5px;font-weight:700;color:var(--ink-2);
  background:#fff;border:1px solid var(--line);border-radius:99px;padding:4px 12px;cursor:pointer}
.kb-nav button:hover,.kb-nav button.on{background:var(--accent);border-color:var(--accent);color:#fff}

.kb-body{padding:20px 26px 26px;overflow:auto;flex:1;scroll-behavior:smooth}
.kb-sec{scroll-margin-top:12px;margin-bottom:22px}
.kb-sec:last-child{margin-bottom:0}
.kb-sec h4{display:flex;align-items:center;gap:9px;font-size:15.5px;color:var(--brand);
  margin:0 0 9px;padding-bottom:7px;border-bottom:1px solid var(--line-2)}
.kb-sec h4 i{font-style:normal;flex:none;width:24px;height:24px;border-radius:7px;
  background:#e8f0fe;color:var(--brand-2);font-size:12px;font-weight:800;
  display:flex;align-items:center;justify-content:center}
.kb-sec p{font-size:14.3px;line-height:1.88;margin:0 0 .7em;color:var(--ink-2)}
.kb-sec ul{margin:.35em 0 .7em;padding-left:22px}
.kb-sec li{font-size:14.3px;line-height:1.85;margin-bottom:6px;color:var(--ink-2)}
.kb-sec code{background:#eef2f7;color:#0f3d63;padding:.12em .42em;border-radius:5px;
  font-size:.9em;overflow-wrap:anywhere}
.kb-sec b{color:var(--brand)}
.kb-sec.kp{background:#f3f8ff;border:1px solid #d8e6fb;border-radius:10px;padding:13px 15px}
.kb-sec.kp h4{border-bottom-color:#d8e6fb}
.kb-sec.er{background:#fff8f6;border:1px solid #f7ddd6;border-radius:10px;padding:13px 15px}
.kb-sec.er h4{color:#b8351f;border-bottom-color:#f7ddd6}
.kb-sec.er h4 i{background:#fdece9;color:#b8351f}
.kb-sec.er b{color:#b8351f}
.kb-sec.xm{background:#f2fbf5;border:1px solid #cfe9d8;border-radius:10px;padding:13px 15px}
.kb-sec.xm h4{color:#12703f;border-bottom-color:#cfe9d8}
.kb-sec.xm h4 i{background:#e3f6e9;color:#12703f}
.kb-sec.xm b{color:#12703f}

.kb-foot{display:flex;align-items:center;justify-content:space-between;gap:14px;flex:none;
  padding:12px 24px;background:#f8fafc;border-top:1px solid var(--line);
  font-size:12px;color:var(--muted)}
.kb-foot-btn{font:inherit;font-size:12.5px;font-weight:700;color:var(--ink-2);
  background:#fff;border:1px solid var(--line);border-radius:8px;padding:5px 16px;cursor:pointer;white-space:nowrap}
.kb-foot-btn:hover{border-color:var(--accent);color:var(--accent)}
body.kb-open{overflow:hidden}
@media (max-width:640px){
  .kb-modal{padding:8px}
  .kb-head{padding:16px}.kb-head h3{font-size:17px}
  .kb-nav{padding:9px 14px;gap:5px}.kb-nav button{font-size:11.5px;padding:3px 9px}
  .kb-body{padding:16px}.kb-foot{padding:10px 14px;flex-direction:column;align-items:stretch}
}
@media print{
  .kb-backdrop,.kb-close,.kb-nav,.kb-foot,.kb-btn{display:none!important}
  .kb-modal{position:static;display:block;padding:0}
  .kb-panel{max-height:none;border:0;box-shadow:none}
  .kb-body{overflow:visible;padding:0}
}
'''

JS = r'''
(function(){
  var DATA = window.WPS_KNOWLEDGE || {};
  var modal = document.getElementById('kbModal');
  if(!modal) return;
  var $ = function(id){ return document.getElementById(id); };
  var titleEl = $('kbTitle'), subEl = $('kbSub'), navEl = $('kbNav'), bodyEl = $('kbBody');
  var SECTIONS = [
    ['points','核心考点','kp'],['background','背景知识','bg'],['principle','操作原理','pr'],
    ['formula','公式与参数详解','fm'],['example','结合本题的例题','ex'],
    ['mistakes','常见易错点','er'],['exam','考试中的考法','xm']
  ];
  var ICON = {'kp':'①','bg':'②','pr':'③','fm':'④','ex':'⑤','er':'⑥','xm':'⑦'};
  var lastFocus = null;

  function esc(s){ return String(s).replace(/[&<>"]/g,function(c){
    return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]; }); }

  function open(key, btn){
    var d = DATA[key];
    if(!d){ return; }
    lastFocus = btn || null;
    var no = (d.no || key), t = d.title || '';
    titleEl.textContent = no + '　' + t;
    subEl.textContent = '逐题精读 · 考点 / 原理 / 参数 / 例题 / 易错 / 考法 七维度讲解';

    navEl.innerHTML = '';
    bodyEl.innerHTML = '';
    SECTIONS.forEach(function(s, i){
      var b = document.createElement('button');
      b.type = 'button'; b.textContent = s[1];
      (function(idx){ b.addEventListener('click', function(){
        Array.prototype.forEach.call(navEl.children, function(x){ x.classList.remove('on'); });
        b.classList.add('on');
        var target = bodyEl.querySelector('[data-kb-sec="' + idx + '"]');
        if(target) target.scrollIntoView({behavior:'smooth', block:'start'});
      }); })(i);
      if(i === 0) b.classList.add('on');
      navEl.appendChild(b);

      var sec = document.createElement('section');
      sec.className = 'kb-sec ' + s[2];
      sec.setAttribute('data-kb-sec', String(i));
      sec.innerHTML = '<h4><i>' + ICON[s[2]] + '</i>' + esc(s[1]) + '</h4>' +
                      '<div class="kb-c">' + (d[s[0]] || '') + '</div>';
      bodyEl.appendChild(sec);
    });

    bodyEl.scrollTop = 0;
    modal.hidden = false;
    document.body.classList.add('kb-open');
    var closeBtn = modal.querySelector('.kb-close');
    if(closeBtn) closeBtn.focus();
  }

  function close(){
    modal.hidden = true;
    document.body.classList.remove('kb-open');
    if(lastFocus && lastFocus.focus) lastFocus.focus();
  }

  document.addEventListener('click', function(ev){
    var btn = ev.target.closest && ev.target.closest('[data-knowledge]');
    if(btn){ open(btn.getAttribute('data-knowledge'), btn); return; }
    if(ev.target.closest && ev.target.closest('[data-kb-close]')){ close(); }
  });
  document.addEventListener('keydown', function(ev){
    if(ev.key === 'Escape' && !modal.hidden) close();
  });
})();
'''


def make_data():
    data = json.loads((K / 'all.json').read_text(encoding='utf-8'))
    E = {(str(e['ci']) + '-' + str(e['seq'])): e
         for e in json.loads((ROOT / 'tools/material/exercises.json').read_text(encoding='utf-8'))}
    out = {}
    for key, val in data.items():
        ex = E[key]
        out[key] = dict(no=ex['no'], title=ex['title'], ci=ex['ci'], seq=ex['seq'],
                        **{f: val[f] for f, _, _ in FIELD_LABELS})
    return out


def build_assets(data):
    js_data = ('/* 由 tools/knowledge/inject.py 生成，请勿手工编辑。\n'
               '   72 题逐题讲解内容；以 JS 赋值方式提供，兼容本地 file:// 打开。 */\n'
               'window.WPS_KNOWLEDGE = ' +
               json.dumps(data, ensure_ascii=False, separators=(',', ':')) + ';\n')
    (ASSETS / 'knowledge-data.js').write_text(js_data, encoding='utf-8')
    (ASSETS / 'knowledge.js').write_text(JS, encoding='utf-8')
    (ASSETS / 'knowledge.css').write_text(CSS, encoding='utf-8')


def patch_pages(data):
    changed = 0
    by_ci = {}
    for key, v in data.items():
        by_ci.setdefault(v['ci'], []).append((v['seq'], key))

    for ci, page in enumerate(PAGES, 1):
        p = ROOT / page
        s = p.read_text(encoding='utf-8')
        orig = s

        # 1) 每题 header 注入按钮（在 fold 按钮之前）
        # 注意：第 1 次课的 article id 用展示题号（如 e2-1 实为 seq=5），
        # 因此按页面内题目出现顺序映射 seq，而不是从 id 解析。
        seq_keys = sorted(by_ci.get(ci, []), key=lambda x: x[0])
        counter = [0]
        def add_btn(m):
            art = m.group(0)
            counter[0] += 1
            if 'data-knowledge=' in art or counter[0] > len(seq_keys):
                return art
            key = seq_keys[counter[0] - 1][1]
            idx = art.find('<button class="fold"')
            if idx < 0:
                return art
            return art[:idx] + BTN_HTML % key + '\n            ' + art[idx:]

        s = re.sub(r'<article class="ex"[^>]*>.*?</article>', add_btn, s, flags=re.S)

        # 2) 引入 assets（插在 </body> 前；必须在弹窗 DOM 之后，
        #    否则 knowledge.js 初始化时找不到 #kbModal 会直接 return）
        if 'assets/knowledge.css' not in s:
            s = s.replace('<link rel="stylesheet" href="./assets/practice.css">',
                          '<link rel="stylesheet" href="./assets/practice.css">\n'
                          '<link rel="stylesheet" href="./assets/knowledge.css">', 1)
        # 3) 弹窗 DOM（放在 body 结束前）
        if 'id="kbModal"' not in s:
            s = s.replace('</body>', MODAL_HTML + '\n</body>', 1)
        # 4) 脚本必须位于弹窗 DOM 之后
        block = ('<script src="./assets/knowledge-data.js"></script>\n'
                 '<script src="./assets/knowledge.js"></script>\n')
        if block in s:
            s = s.replace(block, '', 1)
        if 'assets/knowledge.js' not in s:
            s = s.replace('</body>', '  ' + block + '</body>', 1)
        elif s.find('<script src="./assets/knowledge.js"') < s.find('id="kbModal"'):
            # 兼容旧版：把已有脚本块移到弹窗之后
            oldblock = ('  <script src="./assets/knowledge-data.js"></script>\n'
                        '  <script src="./assets/knowledge.js"></script>\n')
            s = s.replace(oldblock, '', 1)
            s = s.replace('</body>', '  ' + block + '</body>', 1)

        if s != orig:
            p.write_text(s, encoding='utf-8')
            changed += 1
    return changed


def check(data):
    errs = []
    for ci, page in enumerate(PAGES, 1):
        s = (ROOT / page).read_text(encoding='utf-8')
        arts = re.findall(r'<article class="ex"[^>]*>.*?</article>', s, re.S)
        btns = re.findall(r'data-knowledge="(\d+)-(\d+)"', s)
        keys = ['%s-%s' % (a, b) for a, b in btns]
        exp = sorted([k for k, v in data.items() if v['ci'] == ci],
                     key=lambda x: int(x.split('-')[1]))
        if len(arts) != len(exp):
            errs.append('%s 文章数 %d ≠ 题数 %d' % (page, len(arts), len(exp)))
        if sorted(keys, key=lambda x: int(x.split('-')[1])) != exp:
            errs.append('%s 按钮 key 不匹配：缺 %s 多 %s'
                        % (page, set(exp) - set(keys), set(keys) - set(exp)))
        for tag in ['assets/knowledge.css', 'assets/knowledge-data.js',
                    'assets/knowledge.js', 'id="kbModal"']:
            if tag not in s:
                errs.append('%s 缺少 %s' % (page, tag))
    for f in ['knowledge-data.js', 'knowledge.js', 'knowledge.css']:
        if not (ASSETS / f).exists():
            errs.append('缺少 assets/' + f)
    print('校验：%d 个课页 ｜ %d 题按钮 ｜ %s'
          % (len(PAGES), sum(1 for v in data.values()),
             'PASS' if not errs else 'FAIL'))
    for e in errs:
        print('  ', e)
    return 0 if not errs else 1


def main():
    data = make_data()
    if '--check' in sys.argv:
        return check(data)
    build_assets(data)
    n = patch_pages(data)
    print('已生成：assets/knowledge-data.js / knowledge.js / knowledge.css')
    print('已更新课页：%d 个' % n)
    return check(data)


if __name__ == '__main__':
    sys.exit(main())
