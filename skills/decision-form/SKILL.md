---
name: decision-form
description: 「判断をHTMLで聞いて」「選択フォームで」「承認フォーム」「選択式で聞いて」「GOをフォームで」で発動。オーナーに判断・承認を求めるとき、選択式（おすすめ先頭）＋自由記載＋自動更新の回答一覧＋「回答をコピー」ボタンの自己完結 HTML を問いの JSON から作って出す。分野を問わず、案の選定・承認・GO の確認・書き出し前の確認などに使う。
user-invocable: true
argument-hint: "<何を決めてほしいか（問いと案）> [remote=スマホから答える]"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# decision-form — 判断フォーム（選択式＋自由記載＋回答コピー）

オーナーに判断を求めるとき、チャットの散文ではなく 1 枚の HTML で聞く。スマホでも選んで貼るだけで返答できる形。
古生物動画の制作（2026-10-21 dunkleosteus01）で作り、オーナーが気に入った形をそのまま CLI にした。動画に限らず何の判断にも使う。

## 形（変えない）

- 各問いはラジオボタンの選択式。**おすすめを先頭**に置き「（おすすめ：理由）」と書く
- 問いごとに「補足・自由記載」欄、最後に「全体へのコメント」欄
- ページ最下部に、入力に合わせて自動で更新される回答一覧（pre）と「回答をコピー」ボタン
- 回答テキスト: `【回名 ○○の回答】` ／ `① 問い： 選んだ案` ／ `　補足： …`。未選択は「（未選択）」
- コピーは navigator.clipboard → 失敗したら textarea＋execCommand。結果をボタンの横に表示
- 入力は localStorage に保存（try/catch で囲む）
- 画像・動画は base64 で埋め込める。説明（desc）は HTML なので表・折りたたみ（details）を入れられる（`.ok` `.ng` `.mid` の色クラスあり）

## 手順

### 1. 問いを JSON に書く

見本: [examples/sample_spec.json](examples/sample_spec.json)。項目の説明は [scripts/build_form.py](scripts/build_form.py) の先頭。

```json
{"title": "ページの<title>", "heading": "h1", "episode": "回名", "answer_label": "○○",
 "storage_key": "回名_用途", "lead": "<p>リード文</p>",
 "questions": [{"id": "q1", "title": "① 問い", "desc": "<p>説明</p>", "media": ["a.png"],
                "options": ["案A（おすすめ：理由）", "案B（下に書く）"]}]}
```

- media のパスは spec.json から見た相対パスでよい。mp4 は既定で muted（声を聞かせたい動画は `{"path": "x.mp4", "muted": false}`）
- 事実を書くなら出典を一緒に書く。おすすめの理由は 1 句で

### 2. HTML を作って構文を確かめる

```bash
python <この SKILL.md の dir>/scripts/build_form.py spec.json out.html
python <この SKILL.md の dir>/scripts/check_html.py out.html      # <script> を取り出して node --check
node   <この SKILL.md の dir>/scripts/selftest_form.js out.html   # 偽 DOM で 選択→回答一覧→コピー を確かめる
```

Python 標準ライブラリだけで動く。Pillow があれば画像を縮小して埋め込む（無ければ元のまま埋め込むので重くなる）。

### 3. 出す（オーナーがどこにいるかで分ける）

1. **PC の前にいるとき**: `SendUserFile` で HTML を送る（`display: "render"`）。
   見た目の確認はアプリ内ブラウザで行う。アプリ内ブラウザは `file://` を開けないので、プロジェクトの `.claude/launch.json` に一時的に
   `{"name": "decision-form-check", "runtimeExecutable": "python", "runtimeArgs": ["-m", "http.server", "8765", "--bind", "127.0.0.1", "--directory", "<out.html のある dir>"], "port": 8765}`
   を足して `preview_start`、選んで回答一覧が変わること・コピーできることを見る。**終わったら launch.json を元に戻す**（先に写しを取っておき、戻したら cmp で同じか確かめる）。
   サーバーの起動を断られたら、やり直さずに `selftest_form.js` の結果で代える。
2. **リモート（スマホ）のとき**: `SendUserFile` の HTML は、スマホではスクリプトが動かず回答一覧が効かなかった（2026-10-21 実例）。
   非公開の **Artifact** として公開する（Artifact ツールの手順に従い、先に `artifact-design` skill を読み込む。新しいページなので quickstart から）。
   ボタン 1〜2 個で答えられる問いなら、フォームを作らず `wrap_up` のボタンで聞いてもよい。

### 4. 片付け

- 動作確認で入力したテストの値は消しておく（localStorage はキーごとに残る。プレビューで試したら `localStorage.removeItem('<storage_key>')`）
- 回答が届いたら、その内容で作業を進める。回答は承認記録（receipt）が要る工程ならそこへ写す

## 罠

- **Python の三重引用符の中に JS を書くと `\n` が本物の改行に化ける**ことがある（JS の文字列が途中で切れて全部動かなくなる）。JS は `r"""…"""` で書き、改行は `String.fromCharCode(10)` を使う。build_form.py はこの形で書いてある。手で JS を足したら必ず `check_html.py` を通す
- 問いの文字列を JS に埋めるときは `json.dumps` を使い `</` を `<\/` にする（`</script>` で切れる）
- 動作確認で入れた値が localStorage に残ったまま渡すと、オーナーの画面に最初から答えが入って見える

## 使い分け

- プロジェクトの CLAUDE.md §5-3（提案・完了報告は `run-cognitive-ease-infographic` の図解ページ）は**説明して見せる**ためのもの。**選んで返してほしい問い**がある提示はこのフォームで出す（図解の内容を desc に入れてもよい）
- 全台詞を音声つきで 1 行ずつ見るのは `line-review`（台詞チェック帳）

## 用途の例

- 画像計画（visuals.json）の承認 — 各カットの画像を media に並べ「OK／直す」
- 台本の再承認（Script GO）— 変わった行を表で（黄＝オーナーの訂正、青＝そこから直した行）、全行は details に
- MiniMax で動かすカットの選定 — 候補の静止画と試作 mp4 を並べて選ぶ
- 書き出し前の確認 — lint・密度などの機械検査の結果を表にし「もう一度見せてから書き出す（おすすめ）」
