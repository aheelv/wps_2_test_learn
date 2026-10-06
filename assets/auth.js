/* ==========================================================================
   用户权限系统 · 核心模块（纯前端 / 浏览器本地存储）
   大连财经学院 · 计算机国家二级考试（WPS 类）校内教学辅助资料
   --------------------------------------------------------------------------
   本站托管于 GitHub Pages，为纯静态站点，没有服务端。本模块以浏览器本地存储
   模拟「账号 / 角色 / 权限 / 邀请码 / 操作日志」，数据仅保存在访问者本机，
   不会上传到任何服务器，也不收集任何个人信息。
   定位为校内教学演示与轻量管控，不具备服务端级安全强度。
   ========================================================================== */
(function (global) {
  'use strict';

  var KEYS = {
    users: 'wpsdlufe_users_v1',
    session: 'wpsdlufe_session_v1',
    invites: 'wpsdlufe_invites_v1',
    logs: 'wpsdlufe_logs_v1',
    settings: 'wpsdlufe_settings_v1',
    groups: 'wpsdlufe_groups_v1',
    notices: 'wpsdlufe_notices_v1',
    img: 'wpsdlufe_gimg_'
  };

  /* ---------------- 存储层（file:// 或隐私模式下自动降级为内存） ---------------- */
  var mem = {};
  var persistent = true;
  var store = (function () {
    try {
      var t = '__wpsdlufe_t';
      localStorage.setItem(t, '1');
      localStorage.removeItem(t);
      return localStorage;
    } catch (e) {
      persistent = false;
      return {
        getItem: function (k) { return Object.prototype.hasOwnProperty.call(mem, k) ? mem[k] : null; },
        setItem: function (k, v) { mem[k] = String(v); },
        removeItem: function (k) { delete mem[k]; },
        key: function (i) { return Object.keys(mem)[i]; },
        get length() { return Object.keys(mem).length; }
      };
    }
  })();

  function read(key, dft) {
    try {
      var raw = store.getItem(key);
      if (raw === null || raw === undefined || raw === '') return dft;
      return JSON.parse(raw);
    } catch (e) { return dft; }
  }
  function write(key, val) {
    try {
      store.setItem(key, JSON.stringify(val));
      return true;
    } catch (e) { return false; }
  }
  function del(key) { try { store.removeItem(key); } catch (e) {} }

  /* ---------------- 角色与权限 ---------------- */
  var PERMS = [
    { key: 'material.view',   label: '学习资料浏览', desc: '查看教学大纲、教案、课件、电子书等学习资料' },
    { key: 'exam.use',        label: '模拟考试',     desc: '进入并使用上机考试模拟系统' },
    { key: 'group.view',      label: '查看班级群',   desc: '查看班级微信群信息与群二维码' },
    { key: 'group.manage',    label: '建群与群管理', desc: '新建班级群、上传群二维码、编辑与停用群' },
    { key: 'notice.publish',  label: '发布通知',     desc: '发布班级通知并展示在班级群页面' },
    { key: 'user.manage',     label: '用户与权限管理', desc: '新增 / 停用用户、调整角色、重置密码' },
    { key: 'data.export',     label: '数据导出',     desc: '导出用户与班级群数据包（JSON）' },
    { key: 'settings.manage', label: '系统设置',     desc: '修改注册策略与功能开关' },
    { key: 'profile.edit',    label: '个人资料',     desc: '修改本人资料与登录密码' }
  ];

  var ROLES = {
    student: { key: 'student', name: '学生', color: '#2563eb', desc: '可浏览学习资料、参加模拟考试、查看班级群',
      perms: ['material.view', 'exam.use', 'group.view', 'profile.edit'] },
    teacher: { key: 'teacher', name: '教师', color: '#0891b2', desc: '在学生权限之上，可建群并上传群二维码、发布通知、导出数据',
      perms: ['material.view', 'exam.use', 'group.view', 'group.manage', 'notice.publish', 'data.export', 'profile.edit'] },
    admin:   { key: 'admin',   name: '管理员', color: '#e8503a', desc: '拥有全部权限，可管理用户、角色、邀请码与系统设置',
      perms: ['*'] }
  };
  var ROLE_ORDER = ['student', 'teacher', 'admin'];

  var DEFAULT_SETTINGS = {
    siteName: '大连财经学院 · 计算机国家二级考试（WPS 类）',
    allowOpenReg: true,      // 允许学生自助注册
    examRequireLogin: true,  // 模拟考试是否需登录
    groupRequireLogin: true  // 班级群是否需登录
  };

  function uid(p) { return (p || 'id') + Date.now().toString(36) + Math.random().toString(36).slice(2, 6); }
  function hash(s) {
    var h = 5381;
    for (var i = 0; i < s.length; i++) h = ((h << 5) + h + s.charCodeAt(i)) >>> 0;
    var h2 = 52711;
    for (var j = s.length - 1; j >= 0; j--) h2 = ((h2 << 5) + h2 + s.charCodeAt(j)) >>> 0;
    return 'h' + h.toString(36) + h2.toString(36);
  }
  function pwHash(username, pw) { return hash('wpsdlufe::' + String(username).toLowerCase() + '::' + pw); }
  function now() { return Date.now(); }
  function fmt(ts) {
    var d = new Date(ts);
    function p(n) { return (n < 10 ? '0' : '') + n; }
    return d.getFullYear() + '-' + p(d.getMonth() + 1) + '-' + p(d.getDate()) + ' ' + p(d.getHours()) + ':' + p(d.getMinutes());
  }

  /* ---------------- 数据读取 ---------------- */
  function users() { return read(KEYS.users, []); }
  function saveUsers(list) { return write(KEYS.users, list); }
  function invites() { return read(KEYS.invites, []); }
  function saveInvites(list) { return write(KEYS.invites, list); }
  function logs() { return read(KEYS.logs, []); }
  function settings() {
    var s = read(KEYS.settings, null) || {};
    var out = {};
    for (var k in DEFAULT_SETTINGS) out[k] = Object.prototype.hasOwnProperty.call(s, k) ? s[k] : DEFAULT_SETTINGS[k];
    return out;
  }

  function log(action, detail) {
    var me = current();
    var list = logs();
    list.unshift({ t: now(), at: fmt(now()), uid: me ? me.id : '', who: me ? (me.name || me.username) : '未登录', action: action, detail: detail || '' });
    if (list.length > 200) list = list.slice(0, 200);
    write(KEYS.logs, list);
  }

  function publicUser(u) {
    if (!u) return null;
    return {
      id: u.id, username: u.username, name: u.name, role: u.role,
      className: u.className || '', phone: u.phone || '', email: u.email || '',
      active: u.active !== false, createdAt: u.createdAt, lastLoginAt: u.lastLoginAt || 0
    };
  }
  function findByUsername(username) {
    var u = String(username || '').trim().toLowerCase();
    var list = users();
    for (var i = 0; i < list.length; i++) if (String(list[i].username).toLowerCase() === u) return list[i];
    return null;
  }
  function byId(id) {
    var list = users();
    for (var i = 0; i < list.length; i++) if (list[i].id === id) return list[i];
    return null;
  }

  /* ---------------- 会话 ---------------- */
  function current() {
    var s = read(KEYS.session, null);
    if (!s || !s.uid) return null;
    var u = byId(s.uid);
    if (!u || u.active === false) return null;
    return publicUser(u);
  }
  function emit() { try { global.dispatchEvent(new Event('auth:change')); } catch (e) {} }

  /* ---------------- 初始化：首次访问播种演示账号 ---------------- */
  function init() {
    if (!read(KEYS.users, null)) {
      var list = [
        { id: uid('u'), username: 'admin', name: '系统管理员', role: 'admin', className: '', phone: '', email: '',
          pw: pwHash('admin', 'admin123'), active: true, createdAt: now(), lastLoginAt: 0, demo: true },
        { id: uid('u'), username: 'teacher', name: '示范教师', role: 'teacher', className: '', phone: '', email: '',
          pw: pwHash('teacher', 'teacher123'), active: true, createdAt: now(), lastLoginAt: 0, demo: true },
        { id: uid('u'), username: 'student', name: '示范学生', role: 'student', className: '2025 级 1 班', phone: '', email: '',
          pw: pwHash('student', 'student123'), active: true, createdAt: now(), lastLoginAt: 0, demo: true }
      ];
      saveUsers(list);
      write(KEYS.settings, DEFAULT_SETTINGS);
      log('系统初始化', '已创建默认演示账号');
    }
    return true;
  }

  /* ---------------- 权限判定 ---------------- */
  function canRole(role, perm) {
    var r = ROLES[role];
    if (!r) return false;
    if (r.perms.indexOf('*') >= 0) return true;
    return r.perms.indexOf(perm) >= 0;
  }
  function can(perm) {
    var me = current();
    if (!me) return false;
    return canRole(me.role, perm);
  }

  /* ---------------- 注册 / 登录 ---------------- */
  function register(data) {
    data = data || {};
    var username = String(data.username || '').trim();
    var name = String(data.name || '').trim();
    var pw = String(data.password || '');
    if (!/^[A-Za-z0-9_.-]{3,20}$/.test(username)) return { ok: false, msg: '用户名需为 3–20 位字母、数字、下划线、点或短横线' };
    if (name.length < 2) return { ok: false, msg: '请填写真实姓名（至少 2 个字）' };
    if (pw.length < 6) return { ok: false, msg: '密码至少 6 位' };
    if (findByUsername(username)) return { ok: false, msg: '该用户名已被注册' };

    var st = settings();
    var role = 'student';
    var invite = null;
    var code = String(data.invite || '').trim().toUpperCase();
    if (code) {
      var list = invites();
      for (var i = 0; i < list.length; i++) if (list[i].code === code) { invite = list[i]; break; }
      if (!invite) return { ok: false, msg: '邀请码无效' };
      if (invite.expireAt && invite.expireAt < now()) return { ok: false, msg: '邀请码已过期' };
      if (invite.maxUses > 0 && invite.used >= invite.maxUses) return { ok: false, msg: '邀请码使用次数已用尽' };
      role = invite.role || 'student';
    } else if (!st.allowOpenReg) {
      return { ok: false, msg: '当前未开放自助注册，请向教师或管理员索取邀请码' };
    }

    var u = {
      id: uid('u'), username: username, name: name, role: role,
      className: String(data.className || '').trim(), phone: String(data.phone || '').trim(), email: String(data.email || '').trim(),
      pw: pwHash(username, pw), active: true, createdAt: now(), lastLoginAt: 0
    };
    var all = users();
    all.push(u);
    if (!saveUsers(all)) return { ok: false, msg: '本地存储空间不足，注册失败' };

    if (invite) {
      var il = invites();
      for (var j = 0; j < il.length; j++) if (il[j].id === invite.id) il[j].used = (il[j].used || 0) + 1;
      saveInvites(il);
    }
    write(KEYS.session, { uid: u.id, at: now() });
    log('注册', '新用户 ' + username + '（' + (ROLES[role] ? ROLES[role].name : role) + '）');
    emit();
    return { ok: true, msg: '注册成功', user: publicUser(u) };
  }

  function login(username, password) {
    var u = findByUsername(username);
    if (!u) return { ok: false, msg: '用户不存在' };
    if (u.active === false) return { ok: false, msg: '该账号已被停用，请联系管理员' };
    if (u.pw !== pwHash(u.username, String(password || ''))) return { ok: false, msg: '密码不正确' };
    u.lastLoginAt = now();
    var list = users();
    for (var i = 0; i < list.length; i++) if (list[i].id === u.id) list[i] = u;
    saveUsers(list);
    write(KEYS.session, { uid: u.id, at: now() });
    log('登录', '用户 ' + u.username + ' 登录成功');
    emit();
    return { ok: true, msg: '登录成功', user: publicUser(u) };
  }

  function logout() {
    var me = current();
    if (me) log('退出登录', '用户 ' + me.username + ' 退出');
    del(KEYS.session);
    emit();
    return { ok: true };
  }

  function changePassword(oldPw, newPw) {
    var me = current();
    if (!me) return { ok: false, msg: '请先登录' };
    var u = byId(me.id);
    if (u.pw !== pwHash(u.username, String(oldPw || ''))) return { ok: false, msg: '原密码不正确' };
    if (String(newPw || '').length < 6) return { ok: false, msg: '新密码至少 6 位' };
    u.pw = pwHash(u.username, String(newPw));
    u.demo = false;
    var list = users();
    for (var i = 0; i < list.length; i++) if (list[i].id === u.id) list[i] = u;
    saveUsers(list);
    log('修改密码', '用户 ' + u.username);
    emit();
    return { ok: true, msg: '密码已更新' };
  }

  function updateProfile(patch) {
    var me = current();
    if (!me) return { ok: false, msg: '请先登录' };
    if (!can('profile.edit')) return { ok: false, msg: '无权限' };
    var u = byId(me.id);
    ['name', 'className', 'phone', 'email'].forEach(function (k) {
      if (patch && typeof patch[k] === 'string') u[k] = patch[k].trim();
    });
    if (!u.name) return { ok: false, msg: '姓名不能为空' };
    var list = users();
    for (var i = 0; i < list.length; i++) if (list[i].id === u.id) list[i] = u;
    saveUsers(list);
    log('修改资料', '用户 ' + u.username);
    emit();
    return { ok: true, msg: '资料已保存' };
  }

  /* ---------------- 管理员：用户管理 ---------------- */
  function requireAdmin() {
    if (!can('user.manage')) return { ok: false, msg: '需要管理员权限' };
    return null;
  }

  function adminCreateUser(data) {
    var guard = requireAdmin(); if (guard) return guard;
    data = data || {};
    var username = String(data.username || '').trim();
    if (!/^[A-Za-z0-9_.-]{3,20}$/.test(username)) return { ok: false, msg: '用户名需为 3–20 位字母、数字、下划线、点或短横线' };
    if (findByUsername(username)) return { ok: false, msg: '该用户名已存在' };
    var role = ROLES[data.role] ? data.role : 'student';
    var pw = String(data.password || '');
    if (pw.length < 6) return { ok: false, msg: '初始密码至少 6 位' };
    var u = {
      id: uid('u'), username: username, name: String(data.name || username).trim(), role: role,
      className: String(data.className || '').trim(), phone: String(data.phone || '').trim(), email: String(data.email || '').trim(),
      pw: pwHash(username, pw), active: true, createdAt: now(), lastLoginAt: 0
    };
    var list = users(); list.push(u);
    if (!saveUsers(list)) return { ok: false, msg: '本地存储空间不足' };
    log('新增用户', username + '（' + ROLES[role].name + '）');
    emit();
    return { ok: true, msg: '已新增用户', user: publicUser(u) };
  }

  function setUserRole(id, role) {
    var guard = requireAdmin(); if (guard) return guard;
    if (!ROLES[role]) return { ok: false, msg: '角色不存在' };
    var me = current();
    if (me && me.id === id && role !== 'admin') return { ok: false, msg: '不能降级当前登录的管理员账号' };
    var list = users(), hit = null;
    for (var i = 0; i < list.length; i++) if (list[i].id === id) { list[i].role = role; hit = list[i]; }
    if (!hit) return { ok: false, msg: '用户不存在' };
    saveUsers(list);
    log('调整角色', hit.username + ' → ' + ROLES[role].name);
    emit();
    return { ok: true, msg: '角色已更新' };
  }

  function setUserStatus(id, active) {
    var guard = requireAdmin(); if (guard) return guard;
    var me = current();
    if (me && me.id === id && !active) return { ok: false, msg: '不能停用当前登录的账号' };
    var list = users(), hit = null;
    for (var i = 0; i < list.length; i++) if (list[i].id === id) { list[i].active = !!active; hit = list[i]; }
    if (!hit) return { ok: false, msg: '用户不存在' };
    saveUsers(list);
    log(active ? '启用用户' : '停用用户', hit.username);
    emit();
    return { ok: true, msg: active ? '已启用' : '已停用' };
  }

  function resetPassword(id, newPw) {
    var guard = requireAdmin(); if (guard) return guard;
    if (String(newPw || '').length < 6) return { ok: false, msg: '新密码至少 6 位' };
    var list = users(), hit = null;
    for (var i = 0; i < list.length; i++) if (list[i].id === id) { list[i].pw = pwHash(list[i].username, newPw); list[i].demo = false; hit = list[i]; }
    if (!hit) return { ok: false, msg: '用户不存在' };
    saveUsers(list);
    log('重置密码', hit.username);
    emit();
    return { ok: true, msg: '密码已重置' };
  }

  function deleteUser(id) {
    var guard = requireAdmin(); if (guard) return guard;
    var me = current();
    if (me && me.id === id) return { ok: false, msg: '不能删除当前登录的账号' };
    var list = users(), hit = null;
    list = list.filter(function (u) { if (u.id === id) { hit = u; return false; } return true; });
    if (!hit) return { ok: false, msg: '用户不存在' };
    saveUsers(list);
    log('删除用户', hit.username);
    emit();
    return { ok: true, msg: '已删除' };
  }

  /* ---------------- 邀请码 ---------------- */
  function makeCode() {
    var s = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789', out = '';
    for (var i = 0; i < 8; i++) out += s.charAt(Math.floor(Math.random() * s.length));
    return out;
  }
  function createInvite(opt) {
    var guard = requireAdmin(); if (guard) return guard;
    opt = opt || {};
    var role = ROLES[opt.role] ? opt.role : 'student';
    var days = parseInt(opt.days, 10); if (!(days > 0)) days = 0;
    var maxUses = parseInt(opt.maxUses, 10); if (!(maxUses >= 0)) maxUses = 1;
    var code = makeCode();
    var list = invites();
    list.unshift({
      id: uid('iv'), code: code, role: role, maxUses: maxUses, used: 0,
      createdAt: now(), expireAt: days > 0 ? now() + days * 86400000 : 0,
      note: String(opt.note || '').trim()
    });
    if (!saveInvites(list)) return { ok: false, msg: '本地存储空间不足' };
    log('生成邀请码', code + '（' + ROLES[role].name + '）');
    emit();
    return { ok: true, msg: '已生成邀请码', code: code };
  }
  function deleteInvite(id) {
    var guard = requireAdmin(); if (guard) return guard;
    var list = invites().filter(function (x) { return x.id !== id; });
    saveInvites(list);
    log('删除邀请码', id);
    emit();
    return { ok: true, msg: '已删除' };
  }

  /* ---------------- 系统设置 ---------------- */
  function setSetting(key, val) {
    var guard = requireAdmin(); if (guard) return guard;
    var s = settings();
    s[key] = val;
    write(KEYS.settings, s);
    log('修改设置', key + ' = ' + JSON.stringify(val));
    emit();
    return { ok: true, msg: '设置已保存' };
  }

  /* ---------------- 数据包导出 / 导入 ---------------- */
  function exportData() {
    if (!can('data.export') && !can('user.manage')) return { ok: false, msg: '无导出权限' };
    var img = {};
    var gs = read(KEYS.groups, []);
    gs.forEach(function (g) { if (g.imgKey) img[g.imgKey] = store.getItem(KEYS.img + g.imgKey) || ''; });
    var pack = {
      type: 'wpsdlufe-permission-pack', version: 1, exportedAt: fmt(now()),
      settings: settings(),
      users: users().map(function (u) { return u; }),
      invites: invites(),
      groups: gs,
      notices: read(KEYS.notices, []),
      images: img
    };
    log('导出数据包', '用户 ' + pack.users.length + ' 个 / 班级群 ' + pack.groups.length + ' 个');
    return { ok: true, json: JSON.stringify(pack, null, 2), name: 'wps-permission-pack-' + new Date().toISOString().slice(0, 10) + '.json' };
  }

  function importData(json, opt) {
    opt = opt || {};
    if (!can('user.manage') && !can('settings.manage')) return { ok: false, msg: '无导入权限' };
    var pack;
    try { pack = JSON.parse(json); } catch (e) { return { ok: false, msg: '文件不是有效的 JSON' }; }
    if (!pack || pack.type !== 'wpsdlufe-permission-pack') return { ok: false, msg: '不是本站导出的权限数据包' };
    var mode = opt.mode === 'replace' ? 'replace' : 'merge';
    var stat = { users: 0, groups: 0, invites: 0, notices: 0 };

    if (mode === 'replace') {
      var prev = current();
      var prevName = prev ? String(prev.username).toLowerCase() : '';
      saveUsers(Array.isArray(pack.users) ? pack.users : []);
      stat.users = users().length;
      if (prevName) {
        var self = findByUsername(prevName);
        if (self) write(KEYS.session, { uid: self.id, at: now() });
        else del(KEYS.session);
      }
      write(KEYS.groups, Array.isArray(pack.groups) ? pack.groups : []);
      stat.groups = (pack.groups || []).length;
      saveInvites(Array.isArray(pack.invites) ? pack.invites : []);
      write(KEYS.notices, Array.isArray(pack.notices) ? pack.notices : []);
      stat.notices = (pack.notices || []).length;
    } else {
      var cur = users();
      var seen = {};
      cur.forEach(function (u) { seen[String(u.username).toLowerCase()] = true; });
      (pack.users || []).forEach(function (u) {
        if (!u || !u.username) return;
        if (seen[String(u.username).toLowerCase()]) return;
        cur.push(u); seen[String(u.username).toLowerCase()] = true; stat.users++;
      });
      saveUsers(cur);

      var gs = read(KEYS.groups, []);
      var gid = {}; gs.forEach(function (g) { gid[g.id] = true; });
      (pack.groups || []).forEach(function (g) { if (g && g.id && !gid[g.id]) { gs.push(g); gid[g.id] = true; stat.groups++; } });
      write(KEYS.groups, gs);

      var iv = invites(), ic = {}; iv.forEach(function (x) { ic[x.code] = true; });
      (pack.invites || []).forEach(function (x) { if (x && x.code && !ic[x.code]) { iv.push(x); ic[x.code] = true; stat.invites++; } });
      saveInvites(iv);

      var nt = read(KEYS.notices, []), nid = {}; nt.forEach(function (x) { nid[x.id] = true; });
      (pack.notices || []).forEach(function (x) { if (x && x.id && !nid[x.id]) { nt.push(x); nid[x.id] = true; stat.notices++; } });
      write(KEYS.notices, nt);
    }

    if (pack.images && typeof pack.images === 'object') {
      for (var k in pack.images) if (Object.prototype.hasOwnProperty.call(pack.images, k)) store.setItem(KEYS.img + k, pack.images[k]);
    }
    if (pack.settings && can('settings.manage')) write(KEYS.settings, pack.settings);

    log('导入数据包', mode === 'replace' ? '覆盖导入' : '合并导入');
    emit();
    return { ok: true, msg: '导入完成', stat: stat };
  }

  function clearAll() {
    var guard = requireAdmin(); if (guard) return guard;
    var gs = read(KEYS.groups, []);
    gs.forEach(function (g) { if (g.imgKey) del(KEYS.img + g.imgKey); });
    del(KEYS.users); del(KEYS.session); del(KEYS.invites); del(KEYS.logs);
    del(KEYS.settings); del(KEYS.groups); del(KEYS.notices);
    init();
    log('重置系统', '已清空并恢复初始演示数据');
    emit();
    return { ok: true, msg: '已重置为初始状态' };
  }

  /* ---------------- 对外接口 ---------------- */
  var Auth = {
    KEYS: KEYS, PERMS: PERMS, ROLES: ROLES, ROLE_ORDER: ROLE_ORDER,
    persistent: function () { return persistent; },
    init: init,
    settings: settings, setSetting: setSetting,
    roles: function () { return ROLES; },
    roleList: function () { return ROLE_ORDER.map(function (k) { return ROLES[k]; }); },
    permList: function () { return PERMS.slice(); },
    canRole: canRole, can: can,
    current: current,
    users: function () { return users().map(publicUser); },
    userById: function (id) { return publicUser(byId(id)); },
    register: register, login: login, logout: logout,
    changePassword: changePassword, updateProfile: updateProfile,
    adminCreateUser: adminCreateUser, setUserRole: setUserRole, setUserStatus: setUserStatus,
    resetPassword: resetPassword, deleteUser: deleteUser,
    invites: invites, createInvite: createInvite, deleteInvite: deleteInvite,
    logs: logs,
    exportData: exportData, importData: importData, clearAll: clearAll,
    fmt: fmt,
    _store: store, _read: read, _write: write, _del: del, _uid: uid,
    _log: log, _emit: emit
  };

  global.Auth = Auth;
  init();
})(window);
