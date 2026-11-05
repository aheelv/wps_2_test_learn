// 用 Chrome DevTools Protocol 把本地 HTML 打印成 PDF（带页眉页脚页码）
// 用法: node render.mjs <input.html> <output.pdf> [--title=xxx] [--sub=xxx] [--color=#1c4ed8]
import { spawn } from 'node:child_process';
import { mkdtempSync, writeFileSync, readFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { pathToFileURL } from 'node:url';

const CHROME_CANDIDATES = [
  'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
  'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
  'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe',
];

const args = process.argv.slice(2);
const input = args[0];
const output = args[1];
const opt = {};
for (const a of args.slice(2)) {
  const m = a.match(/^--([a-z]+)=(.*)$/);
  if (m) opt[m[1]] = m[2];
}

const fs = await import('node:fs');
const chrome = CHROME_CANDIDATES.find((p) => fs.existsSync(p));
if (!chrome) { console.error('no chrome found'); process.exit(1); }

const port = 9000 + Math.floor(Math.random() * 800);
const profile = mkdtempSync(join(tmpdir(), 'cdp-'));
const proc = spawn(chrome, [
  '--headless=new', '--disable-gpu', '--no-first-run', '--no-default-browser-check',
  '--disable-extensions', '--disable-sync', '--hide-scrollbars',
  `--remote-debugging-port=${port}`, `--user-data-dir=${profile}`, 'about:blank',
], { stdio: 'ignore' });

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function waitVersion() {
  for (let i = 0; i < 100; i++) {
    try {
      const r = await fetch(`http://127.0.0.1:${port}/json/version`);
      if (r.ok) return await r.json();
    } catch { /* retry */ }
    await sleep(150);
  }
  throw new Error('chrome devtools not ready');
}

let id = 0;
function makeClient(ws) {
  const pending = new Map();
  const events = [];
  ws.addEventListener('message', (ev) => {
    const msg = JSON.parse(ev.data);
    if (msg.id && pending.has(msg.id)) {
      const { resolve, reject } = pending.get(msg.id);
      pending.delete(msg.id);
      if (msg.error) reject(new Error(JSON.stringify(msg.error)));
      else resolve(msg.result);
    } else if (msg.method) {
      events.push(msg);
    }
  });
  const send = (method, params = {}) => new Promise((resolve, reject) => {
    const mid = ++id;
    pending.set(mid, { resolve, reject });
    ws.send(JSON.stringify({ id: mid, method, params }));
  });
  return { send, events };
}

function waitOpen(ws) {
  return new Promise((resolve, reject) => {
    ws.addEventListener('open', resolve, { once: true });
    ws.addEventListener('error', reject, { once: true });
  });
}

const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const color = opt.color || '#16324f';
const fullTitle = opt.title || '';
const fullSub = opt.sub || '';

const headerTemplate = `<div style="width:100%;font-family:'Microsoft YaHei',sans-serif;font-size:7.5pt;color:#8a97a8;padding:0 0.72in;display:flex;justify-content:space-between;align-items:flex-end;">
  <span>${esc(fullTitle)}</span><span>${esc(fullSub)}</span></div>`;

const footerTemplate = `<div style="width:100%;font-family:'Microsoft YaHei',sans-serif;font-size:8pt;color:#7c8899;padding:0 0.72in;display:flex;justify-content:space-between;align-items:center;border-top:0.5pt solid #dde3ea;padding-top:4pt;">
  <span style="letter-spacing:.06em">国家计算机等级考试二级 · WPS Office 高级应用与设计</span>
  <span>第 <span class="pageNumber"></span> 页 / 共 <span class="totalPages"></span> 页</span></div>`;

try {
  await waitVersion();
  const tab = await fetch(`http://127.0.0.1:${port}/json/new?about:blank`, { method: 'PUT' }).then((r) => r.json());
  const ws = new WebSocket(tab.webSocketDebuggerUrl);
  await waitOpen(ws);
  const { send, events } = makeClient(ws);

  await send('Page.enable');
  await send('Page.navigate', { url: pathToFileURL(input).href });
  for (let i = 0; i < 200; i++) {
    if (events.some((e) => e.method === 'Page.loadEventFired')) break;
    await sleep(100);
  }
  await send('Runtime.evaluate', {
    expression: 'document.fonts.ready.then(()=>document.readyState)',
    awaitPromise: true, returnByValue: true,
  });
  await send('Emulation.setEmulatedMedia', { media: 'print' });
  await sleep(400);

  const res = await send('Page.printToPDF', {
    printBackground: true,
    paperWidth: 8.27, paperHeight: 11.69,
    marginTop: 0.78, marginBottom: 0.72, marginLeft: 0.72, marginRight: 0.72,
    displayHeaderFooter: true,
    headerTemplate, footerTemplate,
    preferCSSPageSize: false,
    transferMode: 'ReturnAsBase64',
  });
  writeFileSync(output, Buffer.from(res.data, 'base64'));
  console.log('OK', output, (readFileSync(output).length / 1024).toFixed(0) + 'KB');
} finally {
  try { proc.kill(); } catch { /* ignore */ }
  await sleep(300);
  try { rmSync(profile, { recursive: true, force: true }); } catch { /* ignore */ }
}
