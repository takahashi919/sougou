# sougou — 総合受付（マクロハーネス）

すべての入り口になる汎用エージェントの作業ディレクトリ。**ここでは実作業をしない。**
仕事は foyer の door 越しに専門ハーネス（ミクロハーネス）へ渡し、戻ってきた答えだけを読む。

```
~/sougou/                    ← ここで Claude を開く
    │  foyer ask <door> "…"
    ├──► paleo-video         子供向け古生代教育動画（takahashi919/research）
    ├──► llm-wiki            外の世界への判断（takahashi919/LLM-Wiki）
    └──► （増えたら door を 1 本足すだけ）
```

## なぜ分けるか

専門ハーネスを plugin として取り込むと、増えるほど (1) 全 skill が context に乗る**ノイズ過多**、
(2) 似た依頼でどれを選べばいいか分からない**役割被り**が起きる。
door にすれば、受付に載るのはカタログの引き方数行だけで済む。

## 中身

| | |
|---|---|
| `CLAUDE.md` | 受付の規約。**30 行以内**。door が増えても行数は増えない |
| `docs/setup.md` | 新しいマシンでの導入手順 |
| `scripts/setup.sh` | 導入を一気通貫で流す（何度でも打ち直せる） |
| `scripts/sync_user_skills.py` | `skills/` を `~/.claude/skills/` へ配る |
| `skills/` | 分野非依存スキルの正本（→ `skills/README.md`） |

## 使い方

```sh
cd ~/sougou && claude
```

あとは普通に話しかけるだけ。「動画の素材で翼竜のベース画像あったっけ」と言えば、
受付が `foyer ask paleo-video` で向こうに聞きに行く。

導入がまだなら `bash scripts/setup.sh` を先に。
