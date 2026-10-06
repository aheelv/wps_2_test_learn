/* ==========================================================================
   班级群管理模块 · 微信群登记与二维码发布
   大连财经学院 · 计算机国家二级考试（WPS 类）校内教学辅助资料
   --------------------------------------------------------------------------
   微信群需在微信客户端内创建，微信官方未开放个人微信建群接口，故本模块用于
   「登记群信息 + 上传并发布微信群二维码」，学生扫码入群。
   所有群资料与二维码图片仅保存在访问者本机浏览器，不会上传到任何服务器。
   ========================================================================== */
(function (global) {
  'use strict';

  var A = global.Auth;
  var K = A.KEYS;
  var JOIN_MODES = ['扫码入群', '群号搜索', '邀请入群'];

  function list() { return A._read(K.groups, []); }
  function save(list) { return A._write(K.groups, list); }
  function get(id) {
    var l = list();
    for (var i = 0; i < l.length; i++) if (l[i].id === id) return l[i];
    return null;
  }
  function visible() {
    var l = list().slice();
    if (!A.can('group.manage')) l = l.filter(function (g) { return g.active !== false; });
    l.sort(function (a, b) { return (b.top ? 1 : 0) - (a.top ? 1 : 0) || (b.updatedAt || 0) - (a.updatedAt || 0); });
    return l;
  }
  function image(imgKey) { return imgKey ? (A._store.getItem(K.img + imgKey) || '') : ''; }

  function saveGroup(data) {
    if (!A.can('group.manage')) return { ok: false, msg: '需要「建群与群管理」权限' };
    data = data || {};
    var name = String(data.name || '').trim();
    if (name.length < 2) return { ok: false, msg: '请填写群名称（至少 2 个字）' };
    var l = list();
    var me = A.current();
    var hit = null;
    if (data.id) {
      for (var i = 0; i < l.length; i++) if (l[i].id === data.id) hit = l[i];
      if (!hit) return { ok: false, msg: '群不存在' };
    } else {
      hit = { id: A._uid('g'), createdAt: Date.now(), creator: me ? me.name : '', imgKey: '' };
      l.push(hit);
    }
    hit.name = name;
    hit.owner = String(data.owner || '').trim();
    hit.desc = String(data.desc || '').trim();
    hit.joinMode = JOIN_MODES.indexOf(data.joinMode) >= 0 ? data.joinMode : JOIN_MODES[0];
    hit.groupNo = String(data.groupNo || '').trim();
    hit.term = String(data.term || '').trim();
    hit.expireAt = data.expireAt ? String(data.expireAt) : '';
    if (typeof data.active === 'boolean') hit.active = data.active;
    else if (typeof hit.active !== 'boolean') hit.active = true;
    if (typeof data.top === 'boolean') hit.top = data.top;
    else if (typeof hit.top !== 'boolean') hit.top = false;
    hit.updatedAt = Date.now();

    if (data.imageData) {
      var imgKey = hit.imgKey || A._uid('gi');
      var ok = A._write(K.img + imgKey, data.imageData);
      if (!ok) return { ok: false, msg: '二维码图片过大，本地存储空间不足，请换更小的图片' };
      hit.imgKey = imgKey;
    }
    if (data.removeImage && hit.imgKey) { A._del(K.img + hit.imgKey); hit.imgKey = ''; }

    if (!save(l)) return { ok: false, msg: '本地存储空间不足，保存失败' };
    A._log(data.id ? '编辑班级群' : '新建班级群', name);
    A._emit();
    return { ok: true, msg: data.id ? '已保存修改' : '已新建班级群', id: hit.id };
  }

  function removeGroup(id) {
    if (!A.can('group.manage')) return { ok: false, msg: '无权限' };
    var hit = get(id);
    if (!hit) return { ok: false, msg: '群不存在' };
    if (hit.imgKey) A._del(K.img + hit.imgKey);
    save(list().filter(function (g) { return g.id !== id; }));
    A._log('删除班级群', hit.name);
    A._emit();
    return { ok: true, msg: '已删除' };
  }

  function setStatus(id, active) {
    if (!A.can('group.manage')) return { ok: false, msg: '无权限' };
    var l = list(), hit = null;
    for (var i = 0; i < l.length; i++) if (l[i].id === id) { l[i].active = !!active; l[i].updatedAt = Date.now(); hit = l[i]; }
    if (!hit) return { ok: false, msg: '群不存在' };
    save(l); A._log(active ? '启用班级群' : '停用班级群', hit.name); A._emit();
    return { ok: true, msg: active ? '已启用' : '已停用' };
  }

  function toggleTop(id) {
    if (!A.can('group.manage')) return { ok: false, msg: '无权限' };
    var l = list(), hit = null;
    for (var i = 0; i < l.length; i++) if (l[i].id === id) { l[i].top = !l[i].top; hit = l[i]; }
    if (!hit) return { ok: false, msg: '群不存在' };
    save(l); A._log('置顶班级群', hit.name + ' → ' + (hit.top ? '置顶' : '取消')); A._emit();
    return { ok: true, msg: hit.top ? '已置顶' : '已取消置顶' };
  }

  /* ---------------- 二维码图片：读取 + 压缩 ---------------- */
  function readFile(file, cb) {
    if (!file) return cb('请选择图片文件');
    if (!/^image\//.test(file.type)) return cb('请选择图片文件（png / jpg / webp）');
    if (file.size > 8 * 1024 * 1024) return cb('图片超过 8MB，请压缩后再上传');
    var fr = new FileReader();
    fr.onerror = function () { cb('读取文件失败'); };
    fr.onload = function () { compress(fr.result, cb); };
    fr.readAsDataURL(file);
  }

  function compress(dataUrl, cb) {
    var img = new Image();
    img.onerror = function () { cb('图片解析失败，请更换图片'); };
    img.onload = function () {
      var tries = [
        { max: 900, type: 'image/png' },
        { max: 700, type: 'image/png' },
        { max: 900, type: 'image/jpeg', q: 0.92 },
        { max: 640, type: 'image/jpeg', q: 0.9 }
      ];
      for (var i = 0; i < tries.length; i++) {
        var t = tries[i];
        var scale = Math.min(1, t.max / Math.max(img.width, img.height));
        var w = Math.max(1, Math.round(img.width * scale));
        var h = Math.max(1, Math.round(img.height * scale));
        var c = document.createElement('canvas');
        c.width = w; c.height = h;
        var ctx = c.getContext('2d');
        ctx.fillStyle = '#fff';
        ctx.fillRect(0, 0, w, h);
        ctx.drawImage(img, 0, 0, w, h);
        var out = t.type === 'image/jpeg' ? c.toDataURL('image/jpeg', t.q) : c.toDataURL('image/png');
        if (out.length <= 700000 || i === tries.length - 1) {
          return cb(null, { dataUrl: out, w: w, h: h, bytes: out.length });
        }
      }
    };
    img.src = dataUrl;
  }

  function usage() {
    var total = 0;
    try {
      for (var i = 0; i < A._store.length; i++) {
        var k = A._store.key(i);
        if (k && k.indexOf('wpsdlufe_') === 0) {
          var v = A._store.getItem(k);
          total += (k.length + (v ? v.length : 0)) * 2;
        }
      }
    } catch (e) {}
    return total;
  }

  /* ---------------- 班级通知 ---------------- */
  function notices() {
    var l = A._read(K.notices, []);
    l.sort(function (a, b) { return (b.createdAt || 0) - (a.createdAt || 0); });
    return l;
  }
  function addNotice(data) {
    if (!A.can('notice.publish')) return { ok: false, msg: '需要「发布通知」权限' };
    var title = String((data && data.title) || '').trim();
    var body = String((data && data.body) || '').trim();
    if (title.length < 2) return { ok: false, msg: '请填写通知标题' };
    if (!body) return { ok: false, msg: '请填写通知内容' };
    var me = A.current();
    var l = A._read(K.notices, []);
    l.push({ id: A._uid('n'), title: title, body: body, level: (data.level || 'normal'), createdAt: Date.now(), author: me ? me.name : '' });
    A._write(K.notices, l);
    A._log('发布通知', title);
    A._emit();
    return { ok: true, msg: '通知已发布' };
  }
  function removeNotice(id) {
    if (!A.can('notice.publish')) return { ok: false, msg: '无权限' };
    A._write(K.notices, A._read(K.notices, []).filter(function (n) { return n.id !== id; }));
    A._log('删除通知', id);
    A._emit();
    return { ok: true, msg: '已删除' };
  }

  global.Groups = {
    JOIN_MODES: JOIN_MODES,
    list: list, visible: visible, get: get, image: image,
    save: saveGroup, remove: removeGroup, setStatus: setStatus, toggleTop: toggleTop,
    readFile: readFile, usage: usage,
    notices: notices, addNotice: addNotice, removeNotice: removeNotice
  };
})(window);
