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

**1・2 は道具**（インストールするもの）で door にしない。**3・4 は作業場**（door にするもの）。

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

## 管理画面（任意）

どちらも `127.0.0.1` にしか bind しない。外には出ない。

```sh
node ~/.claude/plugins/marketplaces/toolhint/manager/server.mjs   # → 127.0.0.1:4517
foyer serve --open                                                # → 127.0.0.1:4664
cd ~/wiki/llm-wiki-preview && node server.js                      # → 127.0.0.1:6789
```
