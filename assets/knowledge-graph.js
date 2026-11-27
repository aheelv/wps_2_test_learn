/* ==========================================================================
   WPS 国家二级考试知识图谱 · 交互脚本
   基于 D3.js v7（d3/d3，GitHub 114k★，ISC 许可，已本地化到 assets/vendor）
   数据源：assets/knowledge-graph-data.js（window.KNOWLEDGE_GRAPH）
   ========================================================================== */
(function () {
  'use strict';
  var DATA = window.KNOWLEDGE_GRAPH;
  if (!DATA || !window.d3) return;

  var TYPE_NAME = { root: '考试总览', module: '考试模块', domain: '知识域', point: '知识点' };
  var TYPE_COLOR = { root: '#16324f', module: '#2563eb', domain: '#e8503a', point: '#94a3b8' };
  var MODULE_COLOR = { M1: '#2563eb', M2: '#e8503a', M3: '#16a34a', M4: '#7c3aed', M5: '#b45309' };
  var modules = DATA.nodes.filter(function (n) { return n.type === 'module'; });
  var byId = {};
  DATA.nodes.forEach(function (n) { byId[n.id] = n; });

  var state = { filter: 'ALL', keyword: '', layout: 'force', selected: null };

  var svg = d3.select('#kg-graph');
  var wrapEl = document.getElementById('kg-graph-wrap');
  var tip = d3.select('#kg-tip');
  var width = 0, height = 0;

  var defs = svg.append('defs');
  defs.append('marker').attr('id', 'kg-arrow').attr('viewBox', '0 -5 10 10')
    .attr('refX', 24).attr('refY', 0).attr('markerWidth', 5).attr('markerHeight', 5)
    .attr('orient', 'auto')
    .append('path').attr('d', 'M0,-5L10,0L0,5').attr('fill', '#94a3b8');

  var rootG = svg.append('g');
  var linkG = rootG.append('g').attr('class', 'kg-links');
  var nodeG = rootG.append('g').attr('class', 'kg-nodes');
  var zoom = d3.zoom().scaleExtent([0.35, 3]).on('zoom', function (e) { rootG.attr('transform', e.transform); });
  svg.call(zoom).on('dblclick.zoom', null);

  // 复制数据，D3 会写入 x/y/vx/vy
  var nodes = DATA.nodes.map(function (n) { return Object.assign({}, n); });
  var links = DATA.edges.map(function (e) { return Object.assign({}, e); });

  var sim = d3.forceSimulation(nodes)
    .force('link', d3.forceLink(links).id(function (d) { return d.id; })
      .distance(function (d) { return d.kind === 'related' ? 130 : 92; })
      .strength(function (d) { return d.kind === 'related' ? 0.12 : 0.75; }))
    .force('charge', d3.forceManyBody().strength(function (d) {
      return d.type === 'root' ? -900 : d.type === 'module' ? -520 : d.type === 'domain' ? -260 : -110;
    }))
    .force('collide', d3.forceCollide().radius(function (d) { return d.type === 'point' ? 20 : d.type === 'domain' ? 30 : 40; }).iterations(2))
    .force('center', d3.forceCenter())
    .on('tick', ticked);

  var linkSel = linkG.selectAll('line').data(links).enter().append('line')
    .attr('class', function (d) { return 'kg-link' + (d.kind === 'related' ? ' related' : ''); })
    .attr('stroke-width', function (d) { return d.kind === 'related' ? 1 : 1.8; });
  // 层级边显示箭头
  linkSel.filter(function (d) { return d.kind === 'belong'; }).attr('marker-end', 'url(#kg-arrow)');

  var nodeSel = nodeG.selectAll('g').data(nodes).enter().append('g')
    .attr('class', function (d) { return 'kg-node ' + d.type; })
    .style('cursor', 'pointer')
    .call(d3.drag()
      .on('start', function (e, d) { if (!e.active) sim.alphaTarget(0.25).restart(); d.fx = d.x; d.fy = d.y; })
      .on('drag', function (e, d) { d.fx = e.x; d.fy = e.y; })
      .on('end', function (e, d) { if (!e.active) sim.alphaTarget(0); d.fx = null; d.fy = null; }));

  nodeSel.append('circle').attr('r', radius)
    .attr('fill', fillOf)
    .on('click', function (e, d) { e.stopPropagation(); selectNode(d.id); });
  nodeSel.append('text').attr('dy', function (d) { return d.type === 'point' ? 22 : 27; })
    .text(function (d) { return d.short || d.name; })
    .on('click', function (e, d) { e.stopPropagation(); selectNode(d.id); });

  nodeSel.on('mouseenter', function (e, d) { showTip(e, d); highlight(d.id, true); })
    .on('mousemove', function (e) { moveTip(e); })
    .on('mouseleave', function () { tip.style('display', 'none'); highlight(null, false); });

  svg.on('click', function () { selectNode(null); });

  function radius(d) {
    return d.type === 'root' ? 26 : d.type === 'module' ? 19 : d.type === 'domain' ? 12 : 7.5;
  }
  function fillOf(d) {
    if (d.type === 'root') return TYPE_COLOR.root;
    if (d.type === 'module') return MODULE_COLOR[d.id] || TYPE_COLOR.module;
    if (d.type === 'domain') {
      var m = byId[d.parent];
      return (m && MODULE_COLOR[m.id]) || TYPE_COLOR.domain;
    }
    return TYPE_COLOR.point;
  }

  function ticked() {
    var w = width, h = height;
    nodes.forEach(function (d) {
      if (state.layout === 'radial') return;
      d.x = Math.max(38, Math.min(w - 38, d.x));
      d.y = Math.max(30, Math.min(h - 30, d.y));
    });
    linkSel.attr('x1', function (d) { return d.source.x; }).attr('y1', function (d) { return d.source.y; })
      .attr('x2', function (d) { return d.target.x; }).attr('y2', function (d) { return d.target.y; });
    nodeSel.attr('transform', function (d) { return 'translate(' + d.x + ',' + d.y + ')'; });
  }

  function showTip(e, d) {
    tip.html('<b>' + escapeHtml(d.name) + '</b><br>' + TYPE_NAME[d.type] +
      (d.brief ? '<br>' + escapeHtml(d.brief.slice(0, 70)) + (d.brief.length > 70 ? '…' : '') : ''))
      .style('display', 'block');
    moveTip(e);
  }
  function moveTip(e) {
    var r = wrapEl.getBoundingClientRect();
    tip.style('left', (e.clientX - r.left + 14) + 'px').style('top', (e.clientY - r.top + 14) + 'px');
  }

  function highlight(id, on) {
    if (!on || !id) {
      nodeSel.classed('dim', false); linkSel.classed('dim', false); return;
    }
    var near = {}; near[id] = true;
    links.forEach(function (l) {
      var a = l.source.id || l.source, b = l.target.id || l.target;
      if (a === id) near[b] = true;
      if (b === id) near[a] = true;
    });
    nodeSel.classed('dim', function (d) { return !near[d.id]; });
    linkSel.classed('dim', function (l) {
      var a = l.source.id || l.source, b = l.target.id || l.target;
      return a !== id && b !== id;
    });
  }

  function selectNode(id) {
    state.selected = id;
    nodeSel.classed('selected', function (d) { return d.id === id; });
    renderDetail(id);
  }

  function escapeHtml(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c];
    });
  }

  var PRACTICALS = DATA.practicals || {};

  function practicalKeysOf(n) {
    if (!n) return [];
    if (n.type === 'point') return n.practicalKeys || [];
    var out = [];
    nodes.forEach(function (x) {
      if (x.type !== 'point' || !x.practicalKeys) return;
      if (x.id === n.id || x.parent === n.id || ancestorOf(x, n.id)) {
        out = out.concat(x.practicalKeys);
      }
    });
    return out.filter(function (k, i, a) { return a.indexOf(k) === i; });
  }

  function renderPractical(key) {
    var p = PRACTICALS[key];
    if (!p) return '';
    var h = [];
    h.push('<div class="kg-practical">');
    h.push('<div class="pt-h"><span class="pt-no">' + escapeHtml(p.no) + '</span><b>' + escapeHtml(p.title) + '</b></div>');
    if (p.reqs && p.reqs.length) {
      h.push('<div class="pt-sec"><b>题目要求</b><ol>');
      p.reqs.forEach(function (r) { h.push('<li>' + escapeHtml(r) + '</li>'); });
      h.push('</ol></div>');
    }
    if (p.explanation) h.push('<div class="pt-sec"><b>清晰讲解</b><p>' + escapeHtml(p.explanation) + '</p></div>');
    if (p.steps && p.steps.length) {
      h.push('<div class="pt-sec"><b>关键步骤</b><ol class="pt-steps">');
      p.steps.forEach(function (s) { h.push('<li>' + escapeHtml(s) + '</li>'); });
      h.push('</ol></div>');
    }
    if (p.mistakes) h.push('<div class="pt-sec warn"><b>易错提醒</b><p>' + escapeHtml(p.mistakes) + '</p></div>');
    h.push('<div class="pt-foot"><a href="' + escapeHtml(p.href) + '">直达 ' + escapeHtml(p.no) + ' 题目与完整讲解 →</a></div>');
    h.push('</div>');
    return h.join('');
  }

  function renderDetail(id) {
    var box = document.getElementById('kg-detail-body');
    if (!id || !byId[id]) {
      box.innerHTML = '<div class="kg-empty"><div class="ic">🕸️</div>' +
        '点击图谱中的任一节点<br>查看考试要点、关联操作题与详细讲解</div>';
      return;
    }
    var n = byId[id];
    var pkeys = practicalKeysOf(n);
    var limit = n.type === 'point' ? pkeys.length : Math.min(pkeys.length, 6);
    var h = [];
    h.push('<span class="kg-kind" style="background:' + fillOf(n) + '1a;color:' + fillOf(n) + '">' + TYPE_NAME[n.type] + '</span>');
    h.push('<h2>' + escapeHtml(n.name) + '</h2>');
    var meta = [];
    if (n.meta && n.meta.score) meta.push('分值 ' + escapeHtml(n.meta.score));
    if (n.meta && n.meta.hours) meta.push('课时 ' + escapeHtml(n.meta.hours));
    if (n.meta && n.meta.lesson) meta.push('第 ' + n.meta.lesson + ' 课时');
    var childCount = nodes.filter(function (x) { return x.parent === id; }).length;
    if (childCount) meta.push('下含 ' + childCount + ' 个子节点');
    if (pkeys.length) meta.push('关联操作题 ' + pkeys.length + ' 道');
    if (n.questions && n.questions.length) meta.push('理论题 ' + n.questions.length + ' 道');
    if (meta.length) h.push('<div class="kg-meta">' + meta.map(function (x) { return '<span>' + x + '</span>'; }).join('') + '</div>');

    if (n.brief) h.push('<p>' + escapeHtml(n.brief) + '</p>');

    if (n.points && n.points.length) {
      h.push('<h4>考试要点</h4><ul>');
      n.points.forEach(function (p) { h.push('<li>' + escapeHtml(p) + '</li>'); });
      h.push('</ul>');
    }
    if (n.difficulty) h.push('<h4>易错 / 难点</h4><p>' + escapeHtml(n.difficulty) + '</p>');
    if (n.detail) h.push('<h4>考试详解</h4><p>' + escapeHtml(n.detail) + '</p>');
    if (n.examFocus) h.push('<h4>考试中的考法</h4><p>' + escapeHtml(n.examFocus) + '</p>');

    if (limit) {
      h.push('<h4>关联操作题 · ' + pkeys.length + ' 道</h4>');
      for (var i = 0; i < limit; i++) h.push(renderPractical(pkeys[i]));
      if (limit < pkeys.length) {
        h.push('<p class="kg-more">仅显示前 ' + limit + ' 道，点开子知识点可查看全部 ' + pkeys.length + ' 道。</p>');
      }
    }

    if (n.questions && n.questions.length) {
      h.push('<h4>经典题目分析</h4>');
      n.questions.forEach(function (q, i) {
        var ansText = (q.ans != null && q.opts && q.opts[q.ans] != null) ? q.opts[q.ans] : '';
        h.push('<div class="kg-q">');
        h.push('<div class="qh">' + (i + 1) + '. ' + escapeHtml(q.q) + '</div>');
        if (q.opts && q.opts.length) {
          h.push('<div class="qopt">' + q.opts.map(function (o, k) {
            return '<div class="' + (k === q.ans ? 'ok' : '') + '">' + String.fromCharCode(65 + k) + '. ' + escapeHtml(o) +
              (k === q.ans ? '　✓' : '') + '</div>';
          }).join('') + '</div>');
        }
        h.push('<div class="qexp"><b>答案：</b>' + escapeHtml(ansText) + '　<b>解析：</b>' + escapeHtml(q.exp || '') + '</div>');
        h.push('</div>');
      });
    }

    if (n.links && n.links.length) {
      h.push('<h4>学习资源与例题入口</h4><div class="kg-links">');
      n.links.forEach(function (l) {
        h.push('<a href="' + escapeHtml(l.href) + '">' + escapeHtml(l.label) + ' →</a>');
      });
      h.push('</div>');
    }
    box.innerHTML = h.join('');
    box.scrollTop = 0;
  }

  // ---------- 筛选与布局 ----------
  function applyFilter() {
    var f = state.filter, kw = state.keyword.trim().toLowerCase();
    var visible = {};
    nodes.forEach(function (n) {
      var okModule = f === 'ALL' || n.id === f || n.parent === f || ancestorOf(n, f);
      var text = (n.name + ' ' + (n.brief || '') + ' ' + (n.detail || '') +
        ' ' + (n.examFocus || '') + ' ' +
        (n.practicalKeys || []).map(function (k) {
          var p = PRACTICALS[k];
          return p ? (p.no + ' ' + p.title + ' ' + (p.reqs || []).join(' ') + ' ' + p.explanation) : '';
        }).join(' ')).toLowerCase();
      var okKw = !kw || text.indexOf(kw) >= 0;
      n.hidden = !(okModule && okKw);
      if (!n.hidden) visible[n.id] = true;
    });
    nodeSel.classed('hidden-node', function (d) { return d.hidden; })
      .style('display', function (d) { return d.hidden ? 'none' : null; });
    linkSel.style('display', function (l) {
      var a = l.source.id || l.source, b = l.target.id || l.target;
      return (visible[a] && visible[b]) ? null : 'none';
    });
    var count = Object.keys(visible).length;
    document.getElementById('kg-visible-count').textContent = count;
    sim.alpha(0.4).restart();
  }
  function ancestorOf(n, mid) {
    var p = n.parent, guard = 0;
    while (p && guard++ < 6) {
      if (p === mid) return true;
      p = (byId[p] || {}).parent;
    }
    return false;
  }

  // 左侧筛选按钮
  var list = document.getElementById('kg-filter-list');
  function renderFilters() {
    var all = ['<button data-id="ALL" class="' + (state.filter === 'ALL' ? 'on' : '') + '">全部知识点<span class="cnt">' + nodes.length + '</span></button>'];
    modules.forEach(function (m) {
      var c = nodes.filter(function (n) { return n.id === m.id || n.parent === m.id || ancestorOf(n, m.id); }).length;
      all.push('<button data-id="' + m.id + '" class="' + (state.filter === m.id ? 'on' : '') + '">' +
        escapeHtml(m.short || m.name) + '<span class="cnt">' + c + '</span></button>');
    });
    list.innerHTML = all.join('');
    Array.prototype.forEach.call(list.querySelectorAll('button'), function (b) {
      b.onclick = function () {
        state.filter = b.getAttribute('data-id');
        renderFilters(); applyFilter();
        if (state.filter !== 'ALL') selectNode(state.filter);
      };
    });
  }
  renderFilters();

  document.getElementById('kg-search').addEventListener('input', function (e) {
    state.keyword = e.target.value;
    applyFilter();
  });

  // 布局切换：力导向 / 层级（按 level 设置 y，按父节点 x 归位）
  Array.prototype.forEach.call(document.querySelectorAll('.kg-mode button'), function (b) {
    b.onclick = function () {
      Array.prototype.forEach.call(document.querySelectorAll('.kg-mode button'), function (x) { x.classList.remove('on'); });
      b.classList.add('on');
      state.layout = b.getAttribute('data-layout');
      if (state.layout === 'radial') {
        sim.force('radial', null);
        nodes.forEach(function (n) {
          var m = byId[n.parent];
          if (n.type === 'point' && m) {
            n.x = (m.x || width / 2) + (Math.random() - 0.5) * 160;
            n.y = (m.y || height / 2) + 90 + Math.random() * 70;
          }
        });
        sim.alpha(0.5).restart();
      } else {
        sim.alpha(0.6).restart();
      }
    };
  });

  // 缩放按钮
  document.getElementById('kg-zoom-in').onclick = function () { svg.transition().duration(250).call(zoom.scaleBy, 1.35); };
  document.getElementById('kg-zoom-out').onclick = function () { svg.transition().duration(250).call(zoom.scaleBy, 0.74); };
  document.getElementById('kg-reset').onclick = function () {
    svg.transition().duration(350).call(zoom.transform, d3.zoomIdentity);
    state.filter = 'ALL'; state.keyword = '';
    document.getElementById('kg-search').value = '';
    renderFilters(); applyFilter(); selectNode(null);
  };

  function resize() {
    var r = wrapEl.getBoundingClientRect();
    width = r.width; height = r.height;
    svg.attr('viewBox', '0 0 ' + width + ' ' + height);
    sim.force('center', d3.forceCenter(width / 2, height / 2));
    sim.alpha(0.3).restart();
  }
  window.addEventListener('resize', resize);
  resize();
  renderDetail(null);
  // 默认选中根节点，给出即时引导
  setTimeout(function () { selectNode('ROOT'); }, 300);
})();
