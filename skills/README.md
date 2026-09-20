# skills/ — 分野非依存スキルの正本

ここに置くのは、**どの door の仕事でも使うもの**だけ。動画の知識も報告書の知識もここには置かない。
`scripts/sync_user_skills.py --apply` が `~/.claude/skills/` へ配る（symlink は使わない・コピー）。

## 引っ越し待ち（オーナー判断）

`takahashi919/research` の中に、動画と無関係な汎用スキルが 4 本ある。Remotion への言及は 0 件で、
報告書づくりでもそのまま使えるもの:

| スキル | 中身 |
|---|---|
| `md-report-html` | Markdown → 読みやすい Web レポート HTML（自己完結・スマホ対応） |
| `run-cognitive-ease-infographic` | 認知負荷図解。1 枚画像カード |
| `ref-readable-diagram` | 説明図（フロー・構成・状態遷移）の「解読速度」の作法 |
| `run-ai-images` | 汎用 AI 画像生成 |

**移すか複製するかが未決。**

- **移す**（推奨）— 二重真実にならない。ただし research 単体で `/zukai` が動かなくなるので、
  `sync_user_skills.py --apply` で `~/.claude/skills/` に配っておくことが前提になる
- **複製する** — research が単体で完結する。代わりに同じものが 2 箇所に増える

決まるまでここは空のまま。**勝手に移さない。**
