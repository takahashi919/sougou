# HANDOFF.md の書式

案件ブランチ直下の `HANDOFF.md` は、先頭を次のブロックで始める。進捗の表示はここだけを機械で読む。
本文（いまの状態・完了・次の一手・注意）は自由に書いてよい。

```
---
title: リヴィアタン vs メガロドン 台本
updated: 2026-11-18
from: claude
to: codex
next: owner
waiting: 本番の声のモデル（有料を足すか、無料で行くか）
origin: takahashi919/paleo-video @ claude/livyatan-megalodon-script-b2x9sp
---
```

| キー | 中身 |
|---|---|
| `title` | 件名。`cases.md` と同じ言葉 |
| `updated` | 最後に書き換えた日（JST、YYYY-MM-DD） |
| `from` / `to` | 送り手 / 受け手。`owner` `claude` `codex` `muse` のどれか |
| `next` | 次に動く人。`owner` `claude` `codex` `muse` のどれか |
| `waiting` | オーナーの判断待ち。無ければ `なし` |
| `origin` | `<owner>/<repo> @ <branch>` |

- 値は1行で書く。複数あるときは「、」で区切る
- 認証情報・API キーは書かない
- 本文の「次の一手」の1番目は、`next` の人がすぐ始められる粒度で書く
