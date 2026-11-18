// CDP 交互测试：验证「背景知识」按钮点击 → 弹窗内容 → 关闭
// 用法: node tools/knowledge/e2e.mjs
import { spawn } from 'node:child_process';
import { mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { pathToFileURL } from 'node:url';

const CHROME = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const ROOT = process.cwd();
const PAGES = [
  ['入门实操课.html', '1-1', '从零新建并保存第一个文档'],
  ['入门实操课.html', '1-5', '通知类文档的标题格式'],
  ['实操-表格2.html', '5-3', '18 位身份证提取'],
  ['实操-演示1.html', '7-4', '幻灯片母版'],
  ['实操-演示2.html', '8-8', '限时模拟'],
];

const port = 9700 + Math.floor(Math.random() * 200);
const profile = mkdtempSync(join(tmpdir(), 'kb-e2e-'));
const proc = spawn(CHROME, ['--headless=new', '--disable-gpu', '--no-first-run',
  '--hide-scrollbars', '--disable-extensions', `--remote-debugging-port=${port}`,
  `--user-data-dir=${profile}`, 'about:blank'], { stdio: 'ignore' });
const sleep = ms => new Promise(r => setTimeout(r, ms));

async function waitVersion() {
  for (let i = 0; i < 120; i++) {
    try { const r = await fetch(`http://127.0.0.1:${port}/json/version`); if (r.ok) return r.json(); } catch {}
    await sleep(150);
  }
  throw new Error('no devtools');
}
let seq = 0;
function client(ws) {
  const pending = new Map(); const events = [];
  ws.addEventListener('message', ev => {
    const m = JSON.parse(ev.data);
    if (m.id && pending.has(m.id)) { const p = pending.get(m.id); pending.delete(m.id); m.error ? p.reject(new Error(JSON.stringify(m.error))) : p.resolve(m.result); }
    else if (m.method) events.push(m);
  });
  const send = (method, params = {}) => new Promise((res, rej) => {
    const id = ++seq; pending.set(id, { resolve: res, reject: rej });
    ws.send(JSON.stringify({ id, method, params }));
  });
  return { send, events };
}

let fails = 0;
try {
  await waitVersion();
  for (const [page, key, expectTitle] of PAGES) {
    const tab = await fetch(`http://127.0.0.1:${port}/json/new?about:blank`, { method: 'PUT' }).then(r => r.json());
    const ws = new WebSocket(tab.webSocketDebuggerUrl);
    await new Promise((res, rej) => { ws.addEventListener('open', res, { once: true }); ws.addEventListener('error', rej, { once: true }); });
    const { send, events } = client(ws);
    await send('Page.enable');
    await send('Runtime.enable');
    await send('Page.navigate', { url: pathToFileURL(join(ROOT, page)).href });
    for (let i = 0; i < 200; i++) { if (events.some(e => e.method === 'Page.loadEventFired')) break; await sleep(80); }
    await sleep(400);

    const expr = `(function(){
      var btn = document.querySelector('[data-knowledge="${key}"]');
      if(!btn) return {err:'未找到按钮'};
      btn.click();
      var m = document.getElementById('kbModal');
      if(!m || m.hidden) return {err:'弹窗未打开'};
      var secs = m.querySelectorAll('.kb-sec');
      var title = document.getElementById('kbTitle').textContent;
      var navs = m.querySelectorAll('#kbNav button').length;
      var chars = Array.prototype.reduce.call(secs,function(a,s){return a+s.textContent.length},0);
      var hiddenOverflow = getComputedStyle(document.body).overflow;
      return {title:title, secs:secs.length, navs:navs, chars:chars, overflow:hiddenOverflow};
    })()`;
    const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true });
    const v = r.result && r.result.value;
    const ok = v && !v.err && v.secs === 7 && v.navs === 7 && v.chars > 1000 &&
               v.title.indexOf(expectTitle) >= 0 && v.overflow === 'hidden';
    if (!ok) fails++;
    console.log(`${ok ? 'PASS' : 'FAIL'} ${page} key=${key} → ${JSON.stringify(v)}`);

    // 关闭测试
    const c = await send('Runtime.evaluate', {
      expression: `(function(){var b=document.querySelector('#kbModal .kb-close');b.click();
        return {hidden:document.getElementById('kbModal').hidden,
                overflow:getComputedStyle(document.body).overflow}})()`,
      returnByValue: true });
    const cv = c.result && c.result.value;
    const cok = cv && cv.hidden === true && cv.overflow !== 'hidden';
    if (!cok) fails++;
    console.log(`     ${cok ? 'PASS' : 'FAIL'} 关闭 → ${JSON.stringify(cv)}`);
    ws.close();
  }
} catch (e) {
  console.error('E2E 异常:', e.message); fails++;
} finally {
  proc.kill();
  try { rmSync(profile, { recursive: true, force: true }); } catch {}
}
console.log(fails === 0 ? '\nE2E 全部通过' : `\nE2E 失败 ${fails} 项`);
process.exit(fails === 0 ? 0 : 1);
