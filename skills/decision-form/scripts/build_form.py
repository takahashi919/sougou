#!/usr/bin/env python3
"""判断フォーム（選択式＋自由記載＋回答コピー）の自己完結 HTML を、問いの定義 JSON から書き出す。

使い方:
  python build_form.py spec.json out.html

spec.json の形（パスは spec.json のある場所から見た相対パスでもよい）:
  {
    "title": "ダンクル回 台詞の改稿と承認",        # <title>
    "heading": "dunkleosteus01 台詞チェックの反映と承認",  # h1（省略時は title）
    "episode": "dunkleosteus01",                  # 回名。回答の 1 行目「【回名 ○○の回答】」に使う
    "answer_label": "台詞チェック反映・承認",       # 上の ○○
    "storage_key": "dunkle_linefix_go",           # localStorage のキー（省略時は episode と answer_label から作る）
    "lead": "<p>リード文（HTML）</p>",
    "extra_css": "",                              # 足したい CSS（任意）
    "questions": [
      {"id": "q1", "title": "① 問いの見出し",
       "desc": "<p>説明（HTML。表・details も可）</p>",
       "media": ["shots/a.png", {"path": "clip.mp4", "muted": false}],
       "options": ["案A（おすすめ：理由）", "案B"]}
    ],
    "overall_comment": true                       # 最後の「全体へのコメント」欄（既定 true）
  }

Python 標準ライブラリだけで動く。Pillow があれば画像を縮小して JPEG で埋め込む（無ければそのまま埋め込む）。
"""
from __future__ import annotations

import base64
import html
import io
import json
import mimetypes
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:  # Pillow は任意
    Image = None

# 2026-10-21 dunkleosteus01 の build_akari_review.py と同じ見た目（オーナーが気に入った形。変えない）
CSS = """:root{--bg:#f7f6f2;--fg:#1d1d1f;--mut:#666;--card:#fff;--line:#ddd;--acc:#5b3fa8}
@media (prefers-color-scheme:dark){:root{--bg:#16161a;--fg:#eee;--mut:#aaa;--card:#202026;--line:#333;--acc:#b9a3ff}}
body{background:var(--bg);color:var(--fg);font-family:"Noto Sans JP","Yu Gothic",sans-serif;margin:0;padding:16px;line-height:1.6}
main{max-width:1000px;margin:auto} h1{font-size:1.35rem} h2{font-size:1.1rem;margin-top:2rem;border-left:4px solid var(--acc);padding-left:8px}
fieldset.q{background:var(--card);border:2px solid var(--acc);border-radius:10px;padding:12px 16px;margin:14px 0;min-width:0}
legend{padding:0 4px;font-weight:700;color:var(--acc)} .imgs{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:8px;margin:8px 0}
.imgs img,.imgs video{width:100%;border-radius:6px;display:block} .opt{display:flex;gap:8px;align-items:flex-start;padding:6px 4px;cursor:pointer;border-radius:6px}
.opt:hover{background:rgba(127,127,127,.08)} .opt input{margin-top:5px}
textarea{width:100%;box-sizing:border-box;margin-top:6px;font:inherit;padding:6px 8px;border:1px solid var(--line);border-radius:6px;background:var(--bg);color:var(--fg)}
pre#out{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:12px;white-space:pre-wrap;font-size:.9rem}
.actions{display:flex;gap:12px;align-items:center;flex-wrap:wrap;margin:8px 0 24px} #msg{color:var(--mut);font-size:.9rem}
button#copy{font:inherit;font-weight:700;padding:10px 20px;border:0;border-radius:8px;background:var(--acc);color:#fff;cursor:pointer}
.scroll{overflow-x:auto}
table{border-collapse:collapse;width:100%;font-size:.92rem;margin:6px 0}td,th{border:1px solid var(--line);padding:5px 7px;text-align:left;vertical-align:top}th{background:rgba(127,127,127,.08)}
.ng{color:#c0392b;font-weight:700}.ok{color:#2e7d32;font-weight:700}.mid{color:#b9770e;font-weight:700}
details{margin:8px 0}summary{cursor:pointer;font-weight:700}"""

# JS は r"""…""" で書く（ふつうの三重引用符だと \n が本物の改行に化けて JS が壊れる）。改行は String.fromCharCode(10)。
JS = r"""
const f=document.getElementById('f'),out=document.getElementById('out'),msg=document.getElementById('msg');
const NL=String.fromCharCode(10), KEY=__KEY__, HEAD=__HEAD__;
function build(){
  const lines=[HEAD];
  f.querySelectorAll('fieldset').forEach(fs=>{
    const t=fs.dataset.title, r=fs.querySelector('input[type=radio]:checked'), n=fs.querySelector('textarea').value.trim();
    if(fs.querySelector('input[type=radio]')) lines.push(t+'： '+(r?r.value:'（未選択）'));
    else if(!n) return; else lines.push(t+'：');
    if(n) lines.push('　補足： '+n.split(NL).join(NL+'　'));
  });
  return lines.join(NL);
}
function save(){try{const d={};new FormData(f).forEach((v,k)=>d[k]=v);localStorage.setItem(KEY,JSON.stringify(d));}catch(e){}}
function load(){try{const d=JSON.parse(localStorage.getItem(KEY)||'{}');for(const k in d){const el=f.elements[k];if(!el)continue;if(el instanceof RadioNodeList){[...el].forEach(x=>x.checked=x.value===d[k]);}else el.value=d[k];}}catch(e){}}
function refresh(){out.textContent=build();save();}
f.addEventListener('input',refresh);f.addEventListener('change',refresh);load();refresh();
document.getElementById('copy').addEventListener('click',async()=>{
  const t=build();let ok=false;
  try{await navigator.clipboard.writeText(t);ok=true;}catch(e){
    const ta=document.createElement('textarea');ta.value=t;document.body.appendChild(ta);ta.select();
    try{ok=document.execCommand('copy');}catch(e2){}ta.remove();}
  msg.textContent=ok?'コピーしました。チャットに貼り付けてください':'コピーできませんでした。上の回答一覧を手で選択してコピーしてください';
});
"""


def js_str(s: str) -> str:
    """<script> の中に安全に置ける JS の文字列リテラル。"""
    return json.dumps(s, ensure_ascii=False).replace("</", "<\\/")


def data_uri(path: Path, width: int) -> str:
    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    raw = path.read_bytes()
    if mime.startswith("image/") and mime != "image/svg+xml" and Image is not None:
        im = Image.open(io.BytesIO(raw))
        im = im.convert("RGBA" if mime == "image/png" and im.mode in ("RGBA", "LA", "P") else "RGB")
        im.thumbnail((width, width))
        b = io.BytesIO()
        if im.mode == "RGBA":
            im.save(b, "PNG", optimize=True)
            mime = "image/png"
        else:
            im.save(b, "JPEG", quality=82)
            mime = "image/jpeg"
        raw = b.getvalue()
    return f"data:{mime};base64," + base64.b64encode(raw).decode()


def media_html(items: list, base: Path) -> str:
    parts = []
    width = 1100 if len(items) == 1 else 640
    for it in items:
        it = {"path": it} if isinstance(it, str) else dict(it)
        p = Path(it["path"])
        p = p if p.is_absolute() else base / p
        if not p.exists():
            raise SystemExit(f"media が見つからない: {p}")
        uri = data_uri(p, int(it.get("width", width)))
        if uri.startswith("data:video/"):
            muted = " muted" if it.get("muted", True) else ""
            parts.append(f'<video src="{uri}" controls loop{muted} playsinline></video>')
        else:
            alt = html.escape(it.get("alt", p.name))
            parts.append(f'<img src="{uri}" alt="{alt}">')
    return f'<div class="imgs">{"".join(parts)}</div>' if parts else ""


def build(spec: dict, base: Path) -> str:
    title = spec["title"]
    episode = spec.get("episode", "")
    label = spec.get("answer_label", title)
    head = f"【{episode} {label}の回答】" if episode else f"【{label}の回答】"
    key = spec.get("storage_key") or f"decision_{episode}_{label}"
    ids = set()
    parts = []
    for q in spec["questions"]:
        qid = q["id"]
        if qid in ids or qid == "all":
            raise SystemExit(f"問いの id が重複・予約語: {qid}")
        ids.add(qid)
        qt = html.escape(q["title"])
        parts.append(f'<fieldset class="q" data-title="{qt}"><legend>{qt}</legend>')
        parts.append(media_html(q.get("media", []), base))
        if q.get("desc"):
            parts.append(f'<div class="scroll">{q["desc"]}</div>')
        for o in q.get("options", []):
            o = html.escape(o)
            parts.append(f'<label class="opt"><input type="radio" name="{qid}" value="{o}"> <span>{o}</span></label>')
        ph = html.escape(q.get("note_placeholder", "補足・自由記載（任意）"))
        parts.append(f'<textarea name="{qid}_note" rows="2" placeholder="{ph}"></textarea></fieldset>')
    if spec.get("overall_comment", True):
        parts.append('<fieldset class="q" data-title="全体へのコメント"><legend>全体へのコメント（任意）</legend>'
                     '<textarea name="all_note" rows="3" placeholder="ほかに気づいたこと"></textarea></fieldset>')
    js = JS.replace("__KEY__", js_str(key)).replace("__HEAD__", js_str(head))
    css = CSS + ("\n" + spec["extra_css"] if spec.get("extra_css") else "")
    return f"""<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title><style>{css}</style></head><body><main>
<h1>{html.escape(spec.get("heading", title))}</h1>
{spec.get("lead", "")}
<form id="f" onsubmit="return false">{"".join(parts)}</form>
<h2>回答一覧</h2><pre id="out"></pre>
<div class="actions"><button type="button" id="copy">回答をコピー</button><span id="msg" aria-live="polite"></span></div>
<script>{js}</script></main></body></html>
"""


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__)
        return 2
    spec_path, out_path = Path(sys.argv[1]), Path(sys.argv[2])
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    page = build(spec, spec_path.resolve().parent)
    out_path.write_text(page, encoding="utf-8", newline="\n")
    print(f"ok {out_path} {len(page) // 1024} KB, questions {len(spec['questions'])}, Pillow {'yes' if Image else 'no'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
