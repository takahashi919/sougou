#!/usr/bin/env node
// 生成した判断フォームの <script> を、最小限の偽 DOM の上で動かして確かめる（ブラウザが使えないとき・クラウド用）。
// 確かめること: 初期は（未選択）／選ぶと回答一覧が変わる／補足が「　補足：」で出る／localStorage に保存・復元される／
// コピー（navigator.clipboard、失敗したら textarea＋execCommand）と結果の表示。
// 使い方: node selftest_form.js out.html
const fs = require('fs');
const vm = require('vm');

const page = fs.readFileSync(process.argv[2], 'utf8');
const js = page.match(/<script>([\s\S]*?)<\/script>/)[1];
const unesc = (s) => s.replace(/&quot;/g, '"').replace(/&#x27;/g, "'").replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&amp;/g, '&');

function makeEnv(store, clipboardOk) {
  class RadioNodeList extends Array {}
  const listeners = {};
  const fieldsets = [...page.matchAll(/<fieldset class="q" data-title="([^"]*)">([\s\S]*?)<\/fieldset>/g)].map((m) => {
    const radios = [...m[2].matchAll(/<input type="radio" name="([^"]*)" value="([^"]*)">/g)].map((r) => ({ name: r[1], value: unesc(r[2]), checked: false }));
    const ta = { name: m[2].match(/<textarea name="([^"]*)"/)[1], value: '' };
    return {
      dataset: { title: unesc(m[1]) }, radios, ta,
      querySelector(sel) {
        if (sel === 'input[type=radio]:checked') return radios.find((r) => r.checked) || null;
        if (sel === 'input[type=radio]') return radios[0] || null;
        if (sel === 'textarea') return ta;
        return null;
      },
    };
  });
  const elements = {};
  for (const fs_ of fieldsets) {
    if (fs_.radios.length) elements[fs_.radios[0].name] = RadioNodeList.from(fs_.radios);
    elements[fs_.ta.name] = fs_.ta;
  }
  const form = {
    elements,
    querySelectorAll: () => fieldsets,
    addEventListener: (ev, fn) => { (listeners[ev] = listeners[ev] || []).push(fn); },
  };
  const out = { textContent: '' }, msg = { textContent: '' }, copyBtn = { addEventListener: (ev, fn) => { copyBtn.click = fn; } };
  const copied = [];
  const document = {
    getElementById: (id) => ({ f: form, out, msg, copy: copyBtn })[id],
    createElement: () => ({ value: '', select() {}, remove() {} }),
    body: { appendChild: (el) => { document._ta = el; } },
    execCommand: () => { copied.push(document._ta.value); return true; },
  };
  class FormData {
    constructor(f) { this.f = f; }
    forEach(cb) {
      for (const fs_ of fieldsets) {
        const r = fs_.radios.find((x) => x.checked);
        if (r) cb(r.value, r.name);
        cb(fs_.ta.value, fs_.ta.name);
      }
    }
  }
  const navigator = { clipboard: { writeText: async (t) => { if (!clipboardOk) throw new Error('denied'); copied.push(t); } } };
  const localStorage = { getItem: (k) => (k in store ? store[k] : null), setItem: (k, v) => { store[k] = String(v); } };
  const ctx = { document, FormData, navigator, localStorage, RadioNodeList, String, JSON, console };
  vm.createContext(ctx);
  vm.runInContext(js, ctx);
  const fire = (ev) => (listeners[ev] || []).forEach((fn) => fn());
  return { fieldsets, out, msg, copyBtn, copied, fire };
}

function check(cond, label) {
  if (!cond) { console.error('NG: ' + label); process.exit(1); }
  console.log('ok: ' + label);
}

(async () => {
  const store = {};
  let e = makeEnv(store, true);
  const first = e.out.textContent;
  check(/^【.*の回答】/.test(first), '1行目が【…の回答】');
  check(first.includes('（未選択）'), '最初は（未選択）');
  const q = e.fieldsets.find((x) => x.radios.length);
  q.radios[0].checked = true; e.fire('change');
  check(e.out.textContent !== first && e.out.textContent.includes(q.dataset.title + '： ' + q.radios[0].value), '選ぶと回答一覧が変わる');
  q.ta.value = '一行目' + String.fromCharCode(10) + '二行目'; e.fire('input');
  check(e.out.textContent.includes('　補足： 一行目' + String.fromCharCode(10) + '　二行目'), '補足が「　補足：」で出る（複数行は字下げ）');
  await e.copyBtn.click();
  check(e.copied[0] === e.out.textContent && e.msg.textContent.startsWith('コピーしました'), 'navigator.clipboard でコピー・結果を表示');
  const saved = Object.values(store)[0] || '';
  check(saved.includes(q.radios[0].value), 'localStorage に保存');
  e = makeEnv(store, false);
  check(e.out.textContent.includes(q.dataset.title + '： ' + q.radios[0].value), '開き直すと入力が戻る');
  await e.copyBtn.click();
  check(e.copied[0] === e.out.textContent && e.msg.textContent.startsWith('コピーしました'), 'clipboard が失敗したら textarea＋execCommand でコピー');
  console.log('--- 回答一覧（テスト入力のもの。本物のページには残らない）---');
  console.log(e.out.textContent);
})();
