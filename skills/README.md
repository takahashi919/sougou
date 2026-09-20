# skills/ — 分野非依存スキルの正本

ここに置くのは、**どの door の仕事でも使うもの**だけ。動画の知識も報告書の知識もここには置かない。
`python scripts/sync_user_skills.py --apply` が `~/.claude/skills/` へ配る（symlink は使わずコピー）。

配った先はユーザーレベルなので、**どのリポジトリで開いたセッションからも見える**。
research のセッションからも使える。

## 入っているもの

| スキル | 何をするか | 出どころ |
|---|---|---|
| `md-report-html` | Markdown → 読みやすい Web レポート HTML（自己完結・スマホ対応）。「HTML で出して」「レポートにして」で発動 | research から移設（2026-09-20） |
| `ref-readable-diagram` | 説明図（フロー・構成・状態遷移・シーケンス）の解読速度の原則辞書 P-1..P-7。自動発動は切ってあり、他スキルから開かれる前提 | research から移設（2026-09-20） |

## ここに移さなかったもの（理由つき）

research にある残り 3 本は、**実行コマンドがリポジトリ相対パスを持っている**ため移せない。
移すと動かなくなる（「research で出来ることが出来なくならない」を優先した）。

| スキル | 移せない理由 |
|---|---|
| `run-ai-images` | `bash .claude/skills/run-ai-images/scripts/generate.sh …` を **11 箇所**で呼ぶ |
| `run-cognitive-ease-infographic` | `node .claude/skills/…/scripts/render.js` を呼ぶ。加えて冒頭に「**この repo での実行環境**」という移植適用メモがあり、出力先 `output/_samples/infographics/` や「image モードは実行不可」という research 固有の条件が書かれている。`/zukai` コマンドもこのパスに依存 |
| `wrap-ai-image-cognitive-ease` | 上の 2 本に依存する wrap |

**移したければ先にパスを可搬にする**（スキル自身のディレクトリからの相対にする / 環境変数で解決する）。
それは別作業で、壊す危険があるので今回はやっていない。

## 足すときの線引き

- **どの repo でも使うか。** 1 つの door でしか使わないなら、その door の中に置く
- **リポジトリ相対パスを実行コマンドに持っていないか。** 持っていると移した先で壊れる
- 足したら `sync_user_skills.py --check` が drift 0 になるまで配る
