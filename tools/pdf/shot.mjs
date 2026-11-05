// 用 CDP 把本地 HTML 按指定视口截成 PNG（仅用于自查图形质量）
// 用法: node shot.mjs <input.html> <out.png> [--w=1100] [--h=800] [--dpr=2] [--sel=.figbox]
import { spawn } from 'node:child_process';
import { mkdtempSync, writeFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { pathToFileURL } from 'node:url';

const CHROME_CANDIDATES = [
  'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
  'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
  'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe',
];
const args = process.argv.slice(2);
const input = args[0], output = args[1];
const opt = {};
for (const a of args.slice(2)) { const m = a.match(/^--([a-z]+)=(.*)$/); if (m) opt[m[1]] = m[2]; }
const W = +(opt.w || 1100), H = +(opt.h || 800), DPR = +(opt.dpr || 2);

const fs = await import('node:fs');
const chrome = CHROME_CANDIDATES.find((p) => fs.existsSync(p));
if (!chrome) { console.error('no chrome'); process.exit(1); }

const port = 9300 + Math.floor(Math.random() * 600);
const profile = mkdtempSync(join(tmpdir(), 'cdps-'));
const proc = spawn(chrome, ['--headless=new', '--disable-gpu', '--no-first-run', '--hide-scrollbars',
  '--disable-extensions', `--remote-debugging-port=${port}`, `--user-data-dir=${profile}`, 'about:blank'],
  { stdio: 'ignore' });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function waitVersion() {
  for (let i = 0; i < 100; i++) {
    try { const r = await fetch(`http://127.0.0.1:${port}/json/version`); if (r.ok) return await r.json(); } catch {}
    await sleep(150);
  }
  throw new Error('no devtools');
}
let id = 0;
function makeClient(ws) {
  const pending = new Map(); const events = [];
  ws.addEventListener('message', (ev) => {
    const m = JSON.parse(ev.data);
    if (m.id && pending.has(m.id)) { const p = pending.get(m.id); pending.delete(m.id); m.error ? p.reject(new Error(JSON.stringify(m.error))) : p.resolve(m.result); }
    else if (m.method) events.push(m);
  });
  const send = (method, params = {}) => new Promise((res, rej) => { const mid = ++id; pending.set(mid, { resolve: res, reject: rej }); ws.send(JSON.stringify({ id: mid, method, params })); });
  return { send, events };
}
function waitOpen(ws) { return new Promise((res, rej) => { ws.addEventListener('open', res, { once: true }); ws.addEventListener('error', rej, { once: true }); }); }

try {
  await waitVersion();
  const tab = await fetch(`http://127.0.0.1:${port}/json/new?about:blank`, { method: 'PUT' }).then((r) => r.json());
  const ws = new WebSocket(tab.webSocketDebuggerUrl);
  await waitOpen(ws);
  const { send, events } = makeClient(ws);
  await send('Page.enable');
  await send('Emulation.setDeviceMetricsOverride', { width: W, height: H, deviceScaleFactor: DPR, mobile: false });
  await send('Page.navigate', { url: pathToFileURL(input).href });
  for (let i = 0; i < 200; i++) { if (events.some((e) => e.method === 'Page.loadEventFired')) break; await sleep(80); }
  await send('Runtime.evaluate', { expression: 'document.fonts.ready.then(()=>1)', awaitPromise: true, returnByValue: true });
  await sleep(350);
  const clip = opt.sel
    ? (await send('Runtime.evaluate', {
        expression: `(()=>{const r=document.querySelector(${JSON.stringify(opt.sel)}).getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,height:r.height,scale:1};})()`,
        returnByValue: true,
      })).result.value
    : undefined;
  const res = await send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: true, ...(clip ? { clip } : {}) });
  writeFileSync(output, Buffer.from(res.data, 'base64'));
  console.log('OK', output);
} finally {
  try { proc.kill(); } catch {}
  await sleep(250);
  try { rmSync(profile, { recursive: true, force: true }); } catch {}
}
