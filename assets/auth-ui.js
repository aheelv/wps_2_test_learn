/* ==========================================================================
   用户权限系统 · 界面层
   顶栏用户入口 / 登录注册弹窗 / 页面权限门禁 / 轻提示
   依赖：auth.js（window.Auth）
   ========================================================================== */
(function (global) {
  'use strict';

  var A = global.Auth;
  var SELF = (function () {
    try {
      var s = document.currentScript || document.querySelector('script[src*="auth-ui.js"]');
      return s && s.src ? s.src : '';
    } catch (e) { return ''; }
  })();
  var BASE = SELF ? SELF.replace(/assets\/auth-ui\.js.*$/, '') : './';

  function esc(s) {
    return String(s === null || s === undefined ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }
  function roleName(k) { return (A.ROLES[k] || {}).name || k; }
  function roleColor(k) { return (A.ROLES[k] || {}).color || '#33475f'; }

  /* ---------------- 样式 ---------------- */
  var CSS = [
    '.aui-chip{position:relative;flex:none;margin-left:6px}',
    '.aui-chip-btn{display:inline-flex;align-items:center;gap:8px;background:#fff;border:1px solid var(--line,#e2e8f0);',
    'border-radius:99px;padding:5px 12px 5px 5px;cursor:pointer;font-family:inherit;font-size:13.5px;font-weight:700;color:var(--ink,#12213a);transition:.16s}',
    '.aui-chip-btn:hover{border-color:var(--brand,#16324f);box-shadow:0 6px 18px -10px rgba(18,33,58,.5)}',
    '.aui-av{width:26px;height:26px;border-radius:50%;display:grid;place-items:center;color:#fff;font-size:12.5px;font-weight:900;flex:none}',
    '.aui-caret{font-size:10px;color:var(--muted,#6b7a90)}',
    '.aui-menu{position:absolute;right:0;top:calc(100% + 8px);min-width:216px;background:#fff;border:1px solid var(--line,#e2e8f0);',
    'border-radius:13px;box-shadow:0 20px 50px -18px rgba(18,33,58,.4);padding:8px;z-index:200}',
    '.aui-menu-head{padding:9px 11px;border-bottom:1px solid var(--line-2,#eef2f7);margin-bottom:6px}',
    '.aui-menu-head b{display:block;font-size:14px}',
    '.aui-menu-head span{font-size:12px;color:var(--muted,#6b7a90)}',
    '.aui-menu a,.aui-menu button.aui-mi{display:flex;align-items:center;gap:9px;width:100%;text-align:left;padding:9px 11px;border-radius:9px;',
    'font-size:13.5px;font-weight:600;color:var(--ink-2,#33415c);background:none;border:0;cursor:pointer;font-family:inherit;text-decoration:none}',
    '.aui-menu a:hover,.aui-menu button.aui-mi:hover{background:var(--line-2,#eef2f7);color:var(--brand,#16324f)}',
    '.aui-menu .aui-mi.danger:hover{background:#fdeceb;color:#c93f2b}',
    '.aui-float{position:fixed;right:16px;top:12px;z-index:120}',
    '.aui-mask{position:fixed;inset:0;background:rgba(12,24,40,.55);backdrop-filter:blur(3px);z-index:900;display:flex;',
    'align-items:center;justify-content:center;padding:20px}',
    '.aui-dlg{background:#fff;border-radius:18px;width:100%;max-width:440px;max-height:92vh;overflow:auto;box-shadow:0 40px 90px -30px rgba(0,0,0,.55)}',
    '.aui-dlg-head{background:linear-gradient(140deg,#0f2740,#1d3f63);color:#fff;padding:20px 24px}',
    '.aui-dlg-head b{display:block;font-size:19px}',
    '.aui-dlg-head span{font-size:12.5px;color:#b9cee3}',
    '.aui-dlg-body{padding:20px 24px 24px}',
    '.aui-tabs{display:flex;gap:6px;background:var(--line-2,#eef2f7);padding:5px;border-radius:11px;margin-bottom:18px}',
    '.aui-tabs button{flex:1;border:0;background:none;padding:9px;border-radius:8px;font-family:inherit;font-size:14px;font-weight:800;',
    'color:var(--muted,#6b7a90);cursor:pointer}',
    '.aui-tabs button.on{background:#fff;color:var(--brand,#16324f);box-shadow:0 2px 8px -3px rgba(18,33,58,.3)}',
    '.aui-f{margin-bottom:13px}',
    '.aui-f label{display:block;font-size:12.5px;font-weight:800;color:var(--ink-2,#33415c);margin-bottom:5px}',
    '.aui-f input,.aui-f select{width:100%;padding:10px 12px;border:1px solid var(--line,#e2e8f0);border-radius:10px;',
    'font-family:inherit;font-size:14.5px;color:var(--ink,#12213a);background:#fff}',
    '.aui-f input:focus,.aui-f select:focus{outline:2px solid rgba(31,74,117,.35);border-color:var(--brand-2,#1f4a75)}',
    '.aui-row{display:grid;grid-template-columns:1fr 1fr;gap:12px}',
    '.aui-btn{display:inline-flex;align-items:center;justify-content:center;gap:7px;width:100%;padding:11px 18px;border-radius:11px;',
    'border:1px solid transparent;font-family:inherit;font-size:15px;font-weight:800;cursor:pointer;background:var(--brand,#16324f);color:#fff}',
    '.aui-btn:hover{background:#1f4a75}',
    '.aui-btn.ghost{background:#fff;color:var(--brand,#16324f);border-color:var(--line,#e2e8f0)}',
    '.aui-btn.ghost:hover{background:var(--line-2,#eef2f7)}',
    '.aui-msg{font-size:13px;border-radius:9px;padding:9px 12px;margin-bottom:13px;display:none}',
    '.aui-msg.bad{display:block;background:#fdeceb;color:#b3271b;border:1px solid #f6c9c4}',
    '.aui-msg.ok{display:block;background:#e8f7ee;color:#12703f;border:1px solid #bfe6cf}',
    '.aui-hint{font-size:12px;color:var(--muted,#6b7a90);line-height:1.7;margin-top:12px}',
    '.aui-hint code{background:var(--line-2,#eef2f7);padding:1px 5px;border-radius:5px;font-size:11.5px}',
    '.aui-toast{position:fixed;left:50%;bottom:32px;transform:translateX(-50%);background:#12213a;color:#fff;padding:11px 20px;',
    'border-radius:11px;font-size:14px;font-weight:700;z-index:1000;box-shadow:0 18px 40px -16px rgba(0,0,0,.6);max-width:90vw}',
    '.aui-toast.bad{background:#b3271b}',
    '.aui-gate{max-width:560px;margin:0 auto;background:#fff;border:1px solid var(--line,#e2e8f0);border-radius:18px;',
    'padding:40px 32px;text-align:center;box-shadow:var(--shadow,0 8px 24px -12px rgba(18,33,58,.18))}',
    '.aui-gate .ic{font-size:44px;margin-bottom:14px}',
    '.aui-gate h3{font-size:22px;margin:0 0 10px}',
    '.aui-gate p{color:var(--muted,#6b7a90);font-size:14.5px;line-height:1.8;margin:0 0 20px}',
    '.aui-gate .acts{display:flex;gap:12px;justify-content:center;flex-wrap:wrap}',
    '.aui-gate .acts .aui-btn{width:auto;padding:11px 24px}',
    '@media(max-width:640px){.aui-row{grid-template-columns:1fr}}'
  ].join('');

  function injectCSS() {
    if (document.getElementById('aui-style')) return;
    var s = document.createElement('style');
    s.id = 'aui-style';
    s.textContent = CSS;
    document.head.appendChild(s);
  }

  function toast(msg, bad) {
    injectCSS();
    var t = document.createElement('div');
    t.className = 'aui-toast' + (bad ? ' bad' : '');
    t.textContent = msg;
    document.body.appendChild(t);
    setTimeout(function () { if (t.parentNode) t.parentNode.removeChild(t); }, 2400);
  }

  /* ---------------- 权限判定 ---------------- */
  function allow(perm) {
    if (!A) return true;
    var st = A.settings();
    if (perm === 'exam.use' && !st.examRequireLogin) return true;
    if (perm === 'group.view' && !st.groupRequireLogin) return true;
    return A.can(perm);
  }

  function gateHTML(perm) {
    var me = A ? A.current() : null;
    var title, desc;
    if (!me) {
      title = '该功能需要登录后使用';
      desc = '本站为校内教学辅助资料，权限系统为纯前端演示（数据仅保存在你的浏览器本地）。请先登录或注册账号。';
    } else if (perm === 'exam.use') {
      title = '当前角色暂无模拟考试权限';
      desc = '你当前的角色是「' + esc(roleName(me.role)) + '」，如需使用模拟考试请联系教师或管理员调整权限。';
    } else {
      title = '当前角色暂无访问权限';
      desc = '你当前的角色是「' + esc(roleName(me.role)) + '」，如需访问请联系管理员。';
    }
    return '<div class="aui-gate">' +
      '<div class="ic">🔒</div><h3>' + title + '</h3><p>' + desc + '</p>' +
      '<div class="acts">' +
        (me ? '<a class="aui-btn ghost" href="' + BASE + '用户中心.html">前往用户中心</a>'
            : '<button class="aui-btn" data-aui="login">登录 / 注册</button>') +
        '<a class="aui-btn ghost" href="' + BASE + 'index.html">返回学习中心</a>' +
      '</div></div>';
  }

  function gateInto(container, perm) {
    injectCSS();
    var el = typeof container === 'string' ? document.querySelector(container) : container;
    if (!el) return;
    el.innerHTML = '<div style="padding:60px 18px">' + gateHTML(perm) + '</div>';
    var b = el.querySelector('[data-aui="login"]');
    if (b) b.onclick = function () { openAuth('login'); };
    mountChip();
  }

  /* ---------------- 登录 / 注册弹窗 ---------------- */
  function closeModal() {
    var m = document.getElementById('aui-mask');
    if (m && m.parentNode) m.parentNode.removeChild(m);
    document.removeEventListener('keydown', onEsc);
  }
  function onEsc(e) { if (e.key === 'Escape') closeModal(); }

  function openAuth(tab) {
    injectCSS();
    if (document.getElementById('aui-mask')) closeModal();
    var mask = document.createElement('div');
    mask.id = 'aui-mask';
    mask.className = 'aui-mask';
    mask.innerHTML =
      '<div class="aui-dlg" role="dialog" aria-modal="true">' +
        '<div class="aui-dlg-head"><b>用户登录 / 注册</b><span>大连财经学院 · 计算机国家二级考试（WPS 类）· 校内教学辅助资料</span></div>' +
        '<div class="aui-dlg-body">' +
          '<div class="aui-tabs"><button data-tab="login">登录</button><button data-tab="reg">注册</button></div>' +
          '<div id="aui-pane"></div>' +
          '<div class="aui-hint">权限系统为纯前端演示：账号与数据仅保存在<b>本机浏览器</b>，不会上传到任何服务器，也不收集个人信息。默认演示账号 <code>admin / admin123</code>、<code>teacher / teacher123</code>、<code>student / student123</code>。</div>' +
        '</div>' +
      '</div>';
    document.body.appendChild(mask);
    mask.addEventListener('click', function (e) { if (e.target === mask) closeModal(); });
    document.addEventListener('keydown', onEsc);
    var tabs = mask.querySelectorAll('.aui-tabs button');
    tabs.forEach(function (b) {
      b.onclick = function () { renderPane(b.dataset.tab); };
    });
    renderPane(tab || 'login');

    function renderPane(t) {
      tabs.forEach(function (b) { b.classList.toggle('on', b.dataset.tab === t); });
      var pane = mask.querySelector('#aui-pane');
      pane.innerHTML = t === 'login' ? loginForm() : regForm();
      if (t === 'login') {
        pane.querySelector('form').onsubmit = function (e) {
          e.preventDefault();
          var f = e.target;
          var r = A.login(f.username.value, f.password.value);
          showMsg(pane, r.msg, !r.ok);
          if (r.ok) { toast('登录成功，欢迎回来'); setTimeout(function () { location.reload(); }, 700); }
        };
      } else {
        pane.querySelector('form').onsubmit = function (e) {
          e.preventDefault();
          var f = e.target;
          if (f.password.value !== f.password2.value) return showMsg(pane, '两次输入的密码不一致', true);
          var r = A.register({
            username: f.username.value, name: f.name.value, password: f.password.value,
            className: f.className.value, invite: f.invite.value
          });
          showMsg(pane, r.msg, !r.ok);
          if (r.ok) { toast('注册成功，正在进入…'); setTimeout(function () { location.reload(); }, 700); }
        };
      }
    }
  }

  function showMsg(scope, msg, bad) {
    var box = scope.querySelector('.aui-msg');
    if (!box) return;
    box.className = 'aui-msg ' + (bad ? 'bad' : 'ok');
    box.textContent = msg;
  }

  function loginForm() {
    return '<div class="aui-msg"></div><form autocomplete="off">' +
      '<div class="aui-f"><label>用户名</label><input name="username" placeholder="请输入用户名" required></div>' +
      '<div class="aui-f"><label>密码</label><input name="password" type="password" placeholder="请输入密码" required></div>' +
      '<button class="aui-btn" type="submit">登录</button></form>';
  }
  function regForm() {
    return '<div class="aui-msg"></div><form autocomplete="off">' +
      '<div class="aui-row">' +
        '<div class="aui-f"><label>用户名</label><input name="username" placeholder="3–20 位字母/数字" required></div>' +
        '<div class="aui-f"><label>真实姓名</label><input name="name" placeholder="用于班级登记" required></div>' +
      '</div>' +
      '<div class="aui-row">' +
        '<div class="aui-f"><label>密码</label><input name="password" type="password" placeholder="至少 6 位" required></div>' +
        '<div class="aui-f"><label>确认密码</label><input name="password2" type="password" placeholder="再次输入" required></div>' +
      '</div>' +
      '<div class="aui-f"><label>班级（选填）</label><input name="className" placeholder="如：2025 级 1 班"></div>' +
      '<div class="aui-f"><label>邀请码（选填）</label><input name="invite" placeholder="教师/管理员角色需邀请码"></div>' +
      '<button class="aui-btn" type="submit">注册并登录</button></form>';
  }

  /* ---------------- 顶栏用户入口 ---------------- */
  function chipHTML() {
    var me = A ? A.current() : null;
    if (!me) {
      return '<button class="aui-chip-btn" data-aui="open"><span class="aui-av" style="background:#6b7a90">访</span>' +
        '<span>登录 / 注册</span><span class="aui-caret">▾</span></button>';
    }
    var initial = (me.name || me.username || '?').slice(0, 1);
    return '<button class="aui-chip-btn" data-aui="open"><span class="aui-av" style="background:' + roleColor(me.role) + '">' +
      esc(initial) + '</span><span>' + esc(me.name || me.username) + ' · ' + esc(roleName(me.role)) + '</span><span class="aui-caret">▾</span></button>';
  }

  function menuHTML() {
    var me = A ? A.current() : null;
    if (!me) {
      return '<div class="aui-menu" hidden>' +
        '<button class="aui-mi" data-act="login">🔑 登录</button>' +
        '<button class="aui-mi" data-act="reg">📝 注册新账号</button>' +
        '<a href="' + BASE + '群管理.html">👥 班级群</a>' +
        '<a href="' + BASE + '用户中心.html">⚙️ 用户中心</a>' +
      '</div>';
    }
    var items = '<a href="' + BASE + '用户中心.html">⚙️ 用户中心</a>' +
      '<a href="' + BASE + '群管理.html">👥 班级群</a>';
    if (A.can('exam.use')) items += '<a href="' + BASE + '考试模拟系统/index.html">🖥 模拟考试</a>';
    if (A.can('user.manage')) items += '<a href="' + BASE + '用户中心.html#admin">🛡 用户与权限管理</a>';
    items += '<button class="aui-mi danger" data-act="logout">↩ 退出登录</button>';
    return '<div class="aui-menu" hidden>' +
      '<div class="aui-menu-head"><b>' + esc(me.name || me.username) + '</b>' +
      '<span>' + esc(roleName(me.role)) + (me.className ? ' · ' + esc(me.className) : '') + '</span></div>' +
      items + '</div>';
  }

  function bindChip(root) {
    var btn = root.querySelector('[data-aui="open"]');
    var menu = root.querySelector('.aui-menu');
    if (!btn || !menu) return;
    btn.onclick = function (e) {
      e.stopPropagation();
      var willShow = menu.hidden;
      closeAllMenus();
      menu.hidden = !willShow;
    };
    menu.querySelectorAll('[data-act]').forEach(function (b) {
      b.onclick = function (e) {
        e.stopPropagation();
        var act = b.dataset.act;
        menu.hidden = true;
        if (act === 'login') openAuth('login');
        else if (act === 'reg') openAuth('reg');
        else if (act === 'logout') {
          A.logout();
          toast('已退出登录');
          setTimeout(function () { location.reload(); }, 500);
        }
      };
    });
  }

  function closeAllMenus() {
    document.querySelectorAll('.aui-menu').forEach(function (m) { m.hidden = true; });
  }
  document.addEventListener('click', closeAllMenus);

  function mountChip() {
    if (!A) return;
    injectCSS();
    if (document.querySelector('.aui-chip')) return;
    var wrap = document.querySelector('.topbar .wrap') || document.querySelector('.topbar .topbar-in');
    var host = document.createElement('div');
    host.className = 'aui-chip';
    host.innerHTML = chipHTML() + menuHTML();
    if (wrap) {
      wrap.appendChild(host);
    } else {
      host.classList.add('aui-float');
      document.body.appendChild(host);
    }
    bindChip(host);
  }

  function init() {
    if (!A) return;
    mountChip();
  }

  global.AuthUI = {
    BASE: BASE, esc: esc, roleName: roleName, roleColor: roleColor,
    allow: allow, gateHTML: gateHTML, gateInto: gateInto,
    openAuth: openAuth, openLogin: function () { openAuth('login'); },
    openRegister: function () { openAuth('reg'); },
    mountChip: mountChip, toast: toast
  };

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})(window);
