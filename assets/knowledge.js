
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
