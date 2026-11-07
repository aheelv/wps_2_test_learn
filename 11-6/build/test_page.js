// Headless smoke test: run the page script in a minimal DOM shim.
const fs = require('fs');
const vm = require('vm');

const script = fs.readFileSync(process.argv[2], 'utf8');
const els = {};
function makeEl(id){
  const listeners = {};
  return {
    id, innerHTML:'', textContent:'', value:'', style:{}, className:'', dataset:{}, _listeners:listeners,
    classList:{ add(){}, remove(){}, toggle(){} },
    addEventListener(type, fn){ (listeners[type] = listeners[type] || []).push(fn); },
    querySelectorAll(){ return []; }, closest(){ return null; },
    scrollIntoView(){}, blur(){}, click(){}, focus(){}, appendChild(){}
  };
}
const document = {
  getElementById(id){ return els[id] || (els[id] = makeEl(id)); },
  addEventListener(type, fn){ (document._l = document._l || {}); (document._l[type] = document._l[type] || []).push(fn); },
  querySelectorAll(){ return []; },
  createElement(){ return makeEl('a'); }
};
const store = {};
const ctx = {
  document,
  window:{ innerWidth: 1280 },
  localStorage:{ getItem(k){ return store[k] || null; }, setItem(k,v){ store[k] = v; } },
  setTimeout(fn){ if(typeof fn === 'function') fn(); return 1; },
  clearTimeout(){}, confirm(){ return true; },
  Blob:function(){}, URL:{ createObjectURL(){ return 'blob:x'; }, revokeObjectURL(){} },
  console
};
vm.createContext(ctx);
vm.runInContext(script, ctx, {filename:'embedded.js'});

function ok(label, cond){
  console.log((cond ? 'PASS ' : 'FAIL ') + label);
  if(!cond) process.exitCode = 1;
}
const qa = () => els.questionArea.innerHTML;
ok('initial render shows first question', qa().includes('WPS首页的最近列表中'));
ok('initial render has 4 options', (qa().match(/class="option(?: |")/g) || []).length === 4);
ok('sidebar total = 781', els.headerSub.textContent.includes('781'));
ok('answer grid has 781 buttons', (els.answerGrid.innerHTML.match(/<button/g) || []).length === 781);

ctx.choose('A');
ok('correct answer feedback', qa().includes('回答正确') && qa().includes('正确答案'));
ok('progress persisted', els.statGrid.innerHTML.includes('已做题目'));

ctx.goto(150);
ok('section 2 first question', qa().includes('数据库系统'));
ok('favorite toggles', (() => { ctx.toggleFav(); return els.answerGrid.innerHTML.includes('fav'); })());

ctx.setMode('exam');
ok('exam placeholder before start', qa().includes('准备就绪'));
ctx.startExam(20);
ok('exam starts with 20 questions', els.examArea.innerHTML.includes('模拟测试进行中') && qa().includes('data-opt'));
for(let i = 0; i < 20; i++){ ctx.goto(i); ctx.choose('A'); }
ok('no feedback during exam', !qa().includes('正确答案'));
ctx.submitExam();
ok('exam scored', els.examArea.innerHTML.includes('得分率'));
ctx.goto(0);
ok('review shows answers after submit', qa().includes('正确答案'));

ctx.setMode('practice');
const search = els.search;
search.value = '二叉树';
search._listeners.input[0]({target:{value:'二叉树'}});
ok('search filters list', els.headerSub.textContent.includes('当前') && !els.headerSub.textContent.includes('当前 781 题'));
ok('search results are about 二叉树', qa().includes('二叉树') || qa().includes('没有符合条件'));
console.log('--- done ---');
