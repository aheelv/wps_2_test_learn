/* WPS 二级免费资源站 — 客户端检索与筛选
   数据来自 data/resources.js（由 tools/build.py 生成），不依赖网络请求，部署后直接工作。 */
(function () {
  'use strict';

  var DATA = window.SITE_DATA || { resources: [], categories: [] };
  var RES = DATA.resources || [];
  var CATS = DATA.categories || [];
  var BASE = document.body.getAttribute('data-base') || '';
  var CAT_MAP = {};
  CATS.forEach(function (c) { CAT_MAP[c.id] = c; });

  function esc(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }
  function norm(s) { return String(s == null ? '' : s).toLowerCase().replace(/\s+/g, ''); }
  function catName(id) { return CAT_MAP[id] ? CAT_MAP[id].name : id; }
  function accent(id) { return CAT_MAP[id] ? CAT_MAP[id].accent : '#2563eb'; }
  function stars(n) {
    n = Math.max(0, Math.min(5, Number(n) || 0));
    return '<span class="stars">' + '★'.repeat(n) + '<span class="off">' + '★'.repeat(5 - n) + '</span></span>';
  }
  function levelClass(v) {
    if (v === '极高' || v === '高') return 'high';
    if (v === '中') return 'mid';
    return 'low';
  }
  function haystack(r) {
    return norm([
      r.name, r.summary, r.purpose, r.access, r.free, r.caveat, r.kind,
      catName(r.category), (r.tags || []).join(' '), (r.syllabus || []).join(' '),
      (r.links || []).map(function (l) {
        return l.label + ' ' + String(l.url).replace(/^https?:\/\/([^/]+).*$/i, '$1');
      }).join(' ')
    ].join(' '));
  }

  function card(r) {
    var c = CAT_MAP[r.category] || { name: r.category, accent: '#2563eb' };
    var url = BASE + 'resource/' + r.id + '.html';
    var tags = (r.tags || []).slice(0, 3).map(function (t) {
      return '<span class="chip">' + esc(t) + '</span>';
    }).join('');
    return '<div class="col-md-6 col-xl-4 mb-4 filter-item" ' +
      'data-text="' + esc(haystack(r)) + '" ' +
      'data-tags="' + esc((r.tags || []).join('|')) + '" ' +
      'data-rating="' + esc(r.rating) + '">' +
      '<div class="rcard">' +
      '<div class="rcard-top" style="background:' + esc(c.accent) + '"></div>' +
      '<div class="rcard-body">' +
      '<div class="d-flex justify-content-between align-items-start mb-2 gap-2">' +
      '<span class="chip chip-kind">' + esc(c.name) + '</span>' + stars(r.rating) +
      '</div>' +
      '<a class="rcard-title" href="' + url + '">' + esc(r.name) + '</a>' +
      '<p class="rcard-sum">' + esc(r.summary) + '</p>' +
      '<div class="mb-2">' + tags + '</div>' +
      '<div class="rcard-foot">' +
      '<span>零基础 <b>' + esc(r.zero) + '</b> · 备考 <b>' + esc(r.exam) + '</b></span>' +
      '<a href="' + url + '">详情 →</a>' +
      '</div></div></div></div>';
  }

  function row(r) {
    var c = CAT_MAP[r.category] || { name: r.category, accent: '#2563eb' };
    var url = BASE + 'resource/' + r.id + '.html';
    return '<div class="col-12 mb-3 filter-item" ' +
      'data-text="' + esc(haystack(r)) + '" ' +
      'data-tags="' + esc((r.tags || []).join('|')) + '" ' +
      'data-rating="' + esc(r.rating) + '">' +
      '<div class="rcard"><div class="rcard-top" style="background:' + esc(c.accent) + '"></div>' +
      '<div class="rcard-body">' +
      '<div class="d-flex flex-wrap justify-content-between align-items-start gap-2 mb-1">' +
      '<a class="rcard-title mb-0" href="' + url + '">' + esc(r.name) + '</a>' + stars(r.rating) + '</div>' +
      '<div class="mb-2"><span class="chip chip-kind">' + esc(c.name) + '</span>' +
      '<span class="chip">' + esc(r.kind) + '</span>' + '</div>' +
      '<p class="rcard-sum mb-2">' + esc(r.summary) + '</p>' +
      '<div class="small text-muted">免费限制：' + esc(r.free) + '</div>' +
      '</div></div></div>';
  }

  /* ---------- 全站检索页 ---------- */
  function initSearch() {
    var root = document.getElementById('searchApp');
    if (!root) return;
    var input = document.getElementById('q');
    var catSel = document.getElementById('catFilter');
    var rateSel = document.getElementById('ratingFilter');
    var btn = document.getElementById('searchBtn');
    var box = document.getElementById('results');
    var count = document.getElementById('resultCount');
    var empty = document.getElementById('emptyState');

    var params = new URLSearchParams(window.location.search);
    var initial = params.get('q') || '';
    if (initial) input.value = initial;
    var initialCat = params.get('cat') || '';
    if (initialCat && catSel) catSel.value = initialCat;

    function render() {
      var q = norm(input.value.trim());
      var cat = catSel ? catSel.value : '';
      var min = rateSel ? Number(rateSel.value) : 0;
      var terms = q ? q.split(/\s+/).filter(Boolean) : [];
      var hits = RES.filter(function (r) {
        if (cat && r.category !== cat) return false;
        if (min && Number(r.rating) < min) return false;
        if (!terms.length) return true;
        var text = haystack(r);
        return terms.every(function (t) { return text.indexOf(t) !== -1; });
      });
      hits.sort(function (a, b) { return (b.rating - a.rating) || a.name.localeCompare(b.name, 'zh'); });
      box.innerHTML = hits.map(row).join('');
      count.textContent = '共 ' + hits.length + ' 条结果' + (q ? '（关键词：' + input.value.trim() + '）' : '（全部资源）');
      empty.classList.toggle('show', hits.length === 0);
    }

    input.addEventListener('input', render);
    if (catSel) catSel.addEventListener('change', render);
    if (rateSel) rateSel.addEventListener('change', render);
    if (btn) btn.addEventListener('click', render);
    document.querySelectorAll('.hot-word').forEach(function (b) {
      b.addEventListener('click', function () {
        input.value = b.getAttribute('data-q') || '';
        render();
        input.focus();
      });
    });
    render();
  }

  /* ---------- 分类页即时筛选 ---------- */
  function applyFilters(scope) {
    var root = scope || document.querySelector('[data-filter-root]');
    if (!root) return;
    var input = document.getElementById('filterInput');
    var minSel = document.getElementById('minRating');
    var activeTag = document.querySelector('.tag-btn.active');
    var q = input ? norm(input.value.trim()) : '';
    var min = minSel ? Number(minSel.value) : 0;
    var tag = activeTag ? activeTag.getAttribute('data-tag') : '';
    var visible = 0;
    root.querySelectorAll('.filter-item').forEach(function (el) {
      var ok = true;
      if (q && (el.getAttribute('data-text') || '').indexOf(q) === -1) ok = false;
      if (min && Number(el.getAttribute('data-rating') || 0) < min) ok = false;
      if (tag && (el.getAttribute('data-tags') || '').split('|').indexOf(tag) === -1) ok = false;
      el.style.display = ok ? '' : 'none';
      if (ok) visible++;
    });
    var counter = document.getElementById('visibleCount');
    if (counter) counter.textContent = visible;
    var empty = document.getElementById('filterEmpty');
    if (empty) empty.classList.toggle('show', visible === 0);
  }

  function initFilter() {
    var root = document.querySelector('[data-filter-root]');
    if (!root) return;
    var input = document.getElementById('filterInput');
    var minSel = document.getElementById('minRating');
    if (input) input.addEventListener('input', function () { applyFilters(root); });
    if (minSel) minSel.addEventListener('change', function () { applyFilters(root); });
    document.querySelectorAll('.tag-btn').forEach(function (b) {
      b.addEventListener('click', function () {
        var was = b.classList.contains('active');
        document.querySelectorAll('.tag-btn').forEach(function (x) { x.classList.remove('active'); });
        if (!was) b.classList.add('active');
        applyFilters(root);
      });
    });
    applyFilters(root);
  }

  /* ---------- 快捷键：/ 聚焦搜索框 ---------- */
  document.addEventListener('keydown', function (e) {
    if (e.key !== '/' || e.ctrlKey || e.metaKey || e.altKey) return;
    var t = e.target;
    if (t && (t.tagName === 'INPUT' || t.tagName === 'TEXTAREA' || t.isContentEditable)) return;
    var field = document.getElementById('q') || document.getElementById('filterInput') ||
                document.querySelector('.site-search input[type="search"]');
    if (field) { e.preventDefault(); field.focus(); }
  });

  initFilter();
  initSearch();
})();
