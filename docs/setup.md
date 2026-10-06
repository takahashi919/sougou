# 導入手順（新しいマシン）

`bash scripts/setup.sh` が下を全部やる。何度打ち直してもよい（既にあるものは飛ばす）。
ここは、そのスクリプトが何をしているかと、詰まったときの手当て。

## 前提

`git` / `node >= 20` / `python3 >= 3.9`。`rg`（ripgrep）も入れておく — llm-wiki の司書が探すのに使う。
Claude Code CLI にログイン済みであること。

```sh
cd ~/sougou
RESEARCH_DIR=~/dev/research bash scripts/setup.sh
```

`RESEARCH_DIR` を渡すと `paleo-video` の door まで登録される。省略すると手順 4 が案内だけ出して飛ぶ。

---

## 何が入るか

| # | もの | 役割 | 置き場 |
|---|---|---|---|
| 1 | **foyer** | door を叩く窓口 CLI | `~/tools/foyer`（`npm link` で PATH へ） |
| 2 | **toolhint** | 操作の直前に docs を注入する hook | `~/.claude/plugins/…/toolhint` |
| 3 | **llm-wiki** | 外の世界への判断を置く door | `~/wiki/llm-wiki` |
| 4 | **paleo-video** | 動画制作の door | research のクローン |
| 5 | 汎用スキル | `skills/` → `~/.claude/skills/` | → `skills/README.md` |
| 6 | **readable-writing** | 日本語の文章・技術記事を書く plugin（まさお氏の配布物） | 配布 repo を marketplace に（user scope） |

**1・2・6 は道具**（インストールするもの）で door にしない。**3・4 は作業場**（door にするもの）。

---

## 手順ごとの要点

### 1. foyer

`npm link` で `foyer` コマンドが PATH に入る。`foyer doctor` が node / claude /
データディレクトリ（`~/.foyer`）を検査する。全部 `ok` なら通っている。

ビルド済みの `dist/` も同梱されているので、`npm install` が通らない環境でも
`node ~/tools/foyer/dist/cli/index.js doctor` で動作確認だけはできる。

### 2. toolhint

plugin を入れたら **PATH に CLI を足す**（シェルの rc へ）:

```sh
export PATH="$HOME/.claude/plugins/marketplaces/toolhint/cli:$PATH"
```

効いているかは、**ルールのある repo のディレクトリで**確かめる（project 層は cwd から上に探される）:

```sh
cd <research のパス>
toolhint doctor
toolhint test "python scripts/generate_voices_ichthyo01.py"   # docs が出れば OK
```

plugin は install 時点のスナップショット。repo を更新したら
`claude plugin update toolhint@toolhint` で差し替える（`toolhint doctor` が stale を警告する）。

### 3. llm-wiki

**`--mode full` が必須。** 司書が repo 内の `scripts/wiki` を動かすため。既定の `safe` だと
permission denied になり、司書は rg での代替に落ちる。

door 名は `--name llm-wiki` で固定する。GitHub 上の repo 名は `LLM-Wiki` だが、
`CLAUDE.md` の綴りと合わせないと呼べない。

初回に Claude Code の「このフォルダを信頼するか」が出たら Yes（repo に hook の設定が入っている）。

動作確認は **JST で**：

```sh
cd ~/wiki/llm-wiki && TZ=Asia/Tokyo bash scripts/test.sh    # 110 PASS / 1 FAIL
```

`scripts/wiki` は JST 前提で日付を採番する。UTC で走らせると採番・未来日の弾き・sync が落ちる。
残る 1 FAIL は fixtures の経年（`created: 2026-08-02` が 30 日を過ぎて W5 を出す）で欠陥ではない。

### 4. paleo-video

`--desc` は人間向けラベルではなく**読むエージェント向け**に書く。受付は `foyer ls` の説明文だけを見て
「動画のことはこの door」と判断する。

### 5. 汎用スキル

`skills/` が空のうちは何もしない。中身と引っ越しの判断は `skills/README.md`。

### 6. readable-writing

**有料記事の共有物なので sougou には中身を入れない**（この repo は public）。
配布 repo（`AI-Driven-R-D-Dept/readable-writing-dist`、private）を直接 marketplace として足す。
`claude` のコマンドなので **PowerShell でもそのまま打てる**:

```powershell
claude plugin marketplace add AI-Driven-R-D-Dept/readable-writing-dist
claude plugin install readable-writing@readable-writing-dist
```

- 入れたら **Claude Code を開き直す**（書き手の agent 定義は起動時にしか読まれない）
- 呼び名は `readable-writing:<skill>`（例: `/readable-writing:plain-japanese-writing`）
- 版を上げるときは `claude plugin update readable-writing@readable-writing-dist`
- `wrap-masao-article` を自分名義で使うなら、手元に clone して
  `plugin/skills/wrap-masao-article/references/` の 4 ファイルを書き直し、**そのフォルダ**を marketplace に足す
  （`READABLE_WRITING_DIR` に置けば setup.sh が拾う。→ `docs/skill_inventory.md` §4）

---

## cloud セッション（claude.ai/code）

cloud のコンテナは毎回まっさらなので、`.claude/hooks/session-start.sh` が開始時に組み立てる
（cloud のときだけ動く。手元では何もしない）。

| 隣に clone されていれば | すること |
|---|---|
| `foyer` | ビルドして PATH へ（数秒） |
| `llm-wiki`（`LLM-Wiki`） | door `llm-wiki` を `--mode full` で登録。`TZ=Asia/Tokyo` も入れる |
| `research`（`Research`） | door `paleo-video` を登録 |
| `readable-writing-dist` | plugin を入れる（skill は次のセッションから） |

**private repo はセッションに付いていないと取れない**（環境の setup script からも取れない）。
足りない repo は hook が名前を出すので、エージェントが必要なときだけ付けて clone し、hook を打ち直す。
最初から全部ほしいなら、セッションを始めるときに上の repo も一緒に選んでおく。

hook の登録と `foyer` の許可は `.claude/settings.json` に置いてある（中身は下のとおり）:

```json
{
  "hooks": {
    "SessionStart": [
      { "hooks": [ { "type": "command", "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/session-start.sh" } ] }
    ]
  },
  "permissions": { "allow": [ "Bash(foyer:*)" ] }
}
```

---

## 詰まったとき

| 症状 | 見るところ |
|---|---|
| toolhint の注入が一度も出ない | `python3` が PATH にあるか / `toolhint doctor` / ルールのある repo の dir で打っているか |
| 狙ったルールが出ない | `toolhint test "<コマンド>"` で dry-run。正規表現は `tool_input` の JSON 文字列化に当たる |
| `foyer ask` が exit 3 | そのセッションが busy。黙ったキューイングはしない仕様なので、待たずに後で |
| `foyer ask` が何も編集しない | door が `--mode safe`。`permissionDenials` に拒否が記録されている |
| llm-wiki のテストが大量に落ちる | `TZ=Asia/Tokyo` を付けているか |
| npm install が失敗する | 同梱 `dist/` で動作確認だけする（上記 1） |
| `readable-writing:` の skill が出ない / 書き手 agent が見つからない | install 後に Claude Code を開き直したか / `claude plugin list` で enabled か |
| cloud で `foyer` が無い / door が足りない | セッション開始時の `[sougou]` の行を見る。名前の出た repo を付けて clone し、`CLAUDE_CODE_REMOTE=true bash .claude/hooks/session-start.sh` |

## 管理画面（任意）

どちらも `127.0.0.1` にしか bind しない。外には出ない。

```sh
node ~/.claude/plugins/marketplaces/toolhint/manager/server.mjs   # → 127.0.0.1:4517
foyer serve --open                                                # → 127.0.0.1:4664
cd ~/wiki/llm-wiki-preview && node server.js                      # → 127.0.0.1:6789
```
