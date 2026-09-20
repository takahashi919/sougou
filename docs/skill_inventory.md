# スキル棚卸し（全 repo 横断）

> 実測日: 2026-09-20 ／ 対象: この環境に clone 済みの全 repo
> 目的: 「いる / いらない」を名前だけで判断できないので、**何をするものか**と**配線されているか**を並べる。

## 0. まず範囲を絞る — 47 本のうち、判断すべきは 13 本

| repo | 本数 | 判断対象 | 理由 |
|---|---:|---|---|
| **research** | **13** | **← ここだけ** | 自分で作った／育てたもの |
| opabenia | 6 | 対象外 | **6 本すべて research の古い複製**。退役すれば消える |
| akari-video-project-template | 23 | 対象外 | AKARI Video の配布物。向こうの製品の一部 |
| llm-wiki | 4 | 対象外 | llm-wiki の配布物。司書の動線そのもの |
| foyer | 1 | 対象外 | foyer の配布物（操作リファレンス） |
| sougou | 0 | — | 空（引っ越し待ち） |

opabenia の 6 本は `character-bible` `eyecatch-se-rules` `script-policy` `structure-templates`
`task-decomposer` `telop-manager`。**全部 research 側が新しい**（`script-policy` は 56 行 対 163 行）。

---

## 1. 判断の見方 — 「参照 0 = 不要」ではない

スキルの発動経路は 2 つある。混ぜると判断を誤る。

| 経路 | どういうことか | 確実性 |
|---|---|---|
| **配線** | CLAUDE.md・agent 定義・command が「この場面で開け」と名指ししている | 確実に開かれる |
| **自動発動** | 名指しは無く、`description` がモデルの判断を引くのを待つ | **開かれるかは運** |

配線 0 のスキルは「要らない」のではなく「**祈るしかない状態**」。
本当に要るなら配線する、要らないなら消す、のどちらかに倒すべきもの。

---

## 2. research の 13 本

「参照」は自分の repo 内（CLAUDE.md / AGENTS.md / agents/ / commands/ / docs/）から名指しされた回数。

### 動画パイプラインの中核（配線済み）

| スキル | 何をするか | 参照 | 判断 |
|---|---|---:|---|
| `character-bible` | 4 キャラ（スピノン・プレシィ・ボスモサ・オパビ博士）の口調・決め台詞・**NG ライン**。台本を書く前に開く | 10 | **残す** |
| `eyecatch-se-rules` | 場面転換ジングルをどこに入れるか、SE の書き方、タメの作り方 | 10 | **残す**（※下記 3-A） |
| `script-policy` | 子供向け台本のガードレール・5 ブロック構成・尺調整・クイズ運用 | 9 | **残す** |
| `structure-templates` | 15 分動画の長尺化テクニックと構成テンプレ 2 種（シンプル / 詳細） | 8 | **残す** |
| `telop-manager` | テロップを JSON で管理し `video-script.json` へ統合する。React を触らずに文字だけ直す | 4 | **残す** |
| `remotion-layer-guide` | `remotion/src/components/` のレイヤーの役割・props・使用規則 | 6 | **退役予定**（AKARI 移管で用済みになる。消さずに R2·remotion へ） |

### 図解・画像まわり（4 本で 1 つの塊）

**この 4 本は相互に参照し合っている。バラで動かすと壊れる。**

```
run-cognitive-ease-infographic ──┬─► ref-readable-diagram   （図の「解読速度」の原則辞書）
   （1 枚画像 or HTML 図解を作る）  └─► run-ai-images          （画像を 4 枚並列生成）
              ▲
              └──── wrap-ai-image-cognitive-ease （run-ai-images に規律をかけた wrap）
```

| スキル | 何をするか | 参照 | 判断 |
|---|---|---:|---|
| `run-cognitive-ease-infographic` | 「わかりやすい図解」で発動。1 枚画像カードか HTML 図解ページを作り分ける。**CLAUDE.md §5-3 のオーナー報告規約が使う**（`/zukai`） | 2 | **移す**（受付へ） |
| `run-ai-images` | 汎用 AI 画像生成。任意のプロンプトで既定 4 枚を並列生成 | 2 | **移す** |
| `ref-readable-diagram` | 説明図（フロー・構成・状態遷移）の解読速度の原則辞書 P-1..P-7。**自動発動を切ってある**（`disable-model-invocation: true`）ので、他スキルから開かれる前提 | 0 | **移す**（参照 0 は設定どおり。異常ではない） |
| `wrap-ai-image-cognitive-ease` | 色の職務・4±1・完全語の規律をかけて図解カードを作る。`run-ai-images` の wrap | 1 | **移す** |

### 単独・要判断

| スキル | 何をするか | 参照 | 判断 |
|---|---|---:|---|
| `md-report-html` | Markdown → 読みやすい Web レポート HTML（自己完結・スマホ対応）。「HTML で出して」「レポートにして」で発動 | 1<br>(ADR の一覧のみ) | **移す** — 報告書づくりの本命。動画と無関係 |
| `minimax-h3-local-comfyui` | Windows ローカルの MiniMax H3 を ComfyUI 経由で操作。text-to-video / first-last-frame / 音声つき MP4 生成 | **0** | **要判断** — 動画生成の道具。使うなら配線、使わないなら消す |
| `task-decomposer` | 8〜15 分の動画制作を最小サブタスクに分解し実行順序を決める。**20 行しかない** | 2<br>(どちらもメタ言及) | **要判断** — 下記 3-B |

---

## 3. 見つかった気になる点

### 3-A. `eyecatch-se-rules` に Remotion 前提の指示が残っている

> デカ文字は焼き込まず、**Remotion 側で動的に乗せる**

AKARI では HTML オーバーレイが常に前面で、遮蔽は逆に**焼き込む**。
移管後もこのまま残すと、台本を書く agent が正反対の指示を受け取る。
残すが、レンダラ依存の 1 行は R2 側へ出す（→ `docs/harness_reinforcement_plan.md`）。

### 3-B. `task-decomposer` が、どの agent からも呼ばれていない

`CLAUDE.md` §1 は Orchestrator-Workers を掲げ、`.claude/agents/paleo-orchestrator.md` 相当が
分解を委譲する建て付けになっている。しかし research の `.claude/agents/` と
`.claude/commands/` のどこからも `task-decomposer` は名指しされていない
（当たったのは ADR の一覧と、この棚卸しの元になった計画書だけ）。

**消す前に、配線が抜けているだけではないか**を確かめること。20 行という薄さも、
「育つ前に呼ばれなくなった」可能性を示している。

### 3-C. 図解 4 本を移すなら、まとめて移す

相互参照があるので 1 本だけ動かすと参照が切れる。
移し先は `~/.claude/skills/`（`sougou/skills/` が正本、`sync_user_skills.py --apply` で配る）。
ユーザーレベルに置けば research のセッションからも見えるので、`/zukai` は壊れない。

---

## 4. 配布物（判断対象外・参考）

消したり動かしたりしない。「何があるか」を知るための一覧。

### llm-wiki — 司書の動線 4 本

| スキル | 何をするか |
|---|---|
| `ref-wiki-schema` | 型 10・述語 7・ID 規則・frontmatter 書式・検索レシピ R1-R10 の逐語正本 |
| `run-wiki-capture` | 投入 1 件を完走（重複確認 → エンティティ作成 → 記録 → 結線 → lint → save） |
| `run-wiki-recall` | 読み取り専用で引く。答え + 根拠パス + 隣接 2-3 件。「無い」も明言する |
| `run-wiki-garden` | lint 結果を裁いて 1 件 1 commit で修理。ランダム再訪と sync まで |

### foyer — 1 本

| スキル | 何をするか |
|---|---|
| `ref-foyer` | foyer CLI の操作リファレンス。door 登録・ask・セッション継続・GUI・permission |

### akari-video-project-template — 23 本

AKARI Video の製品スキル。**編集の作業台そのもの**で、制作リポジトリを作ると付いてくる。

| 系統 | スキル |
|---|---|
| 素材を見る | `analyze-footage`（素材 1 本を L0〜L3 で観察）/ `analyze-project`（素材横断で解釈層を作る） |
| 組む | `edit-plan`（方針 → 素材計画 → edit.json）/ `beat-sync-edit`（拍にスナップした PV を機械生成）/ `overlay-authoring`（オーバーレイ HTML・字幕・表・3D のルーター） |
| 検査・書き出し | `edit-lint`（edit.json の決定的検査）/ `render-cut`（最終 MP4 の書き出しと検証）/ `verify`（検証はしご L0/L1/L2）/ `export-nle`（FCPXML / Premiere / SRT へ書き出し・BETA） |
| レビュー | `critique-cut`（組んだタイムラインを読んで所見だけ返す）/ `compile-review-session`（喋りながらの QA を録音からチケット化）/ `address-review`（チケットを型どおりに消化） |
| 素材を増やす | `setup-library`（初回セットアップとスターターパック）/ `setup-audio-library`（BGM・SE の取得）/ `harvest-asset`（高コスト素材をライブラリへ入庫）/ `bake-3d`（Blender で 3D を mp4 へ焼く） |
| 音 | `declare-audio`（サビ・キメ・拍を自分の耳で宣言づけ）/ `generate-narration`（VOICEVOX / 自声クローンでナレーション） |
| 企画 | `research-plan`（ネタ出し → 調査 → 企画書・構成案・絵コンテ） |
| 環境 | `create-project` / `manage-connections`（API キー・モデル・コスト承認）/ `setup-remote`（スマホから承認・素材送信）/ `setup-chat-approval`（Telegram で承認ボタン） |

> **注目**: `harvest-asset` は「生成コストが高い、または生成不能なものだけ入れる」という入庫基準を持ち、
> `provenance` に元 prompt まで記録する。素材の使い回しはこちらの規格に乗せる
> （→ `docs/harness_reinforcement_plan.md` の素材の節）。

---

## 5. まとめ — 移す / 残す / 要判断

| 判断 | 本数 | 中身 |
|---|---:|---|
| **受付へ移す** | 5 | 図解 4 本（塊）+ `md-report-html` |
| **research に残す** | 5 | `character-bible` `script-policy` `eyecatch-se-rules` `structure-templates` `telop-manager` |
| **退役予定** | 1 | `remotion-layer-guide`（AKARI 移管で） |
| **要判断** | 2 | `minimax-h3-local-comfyui`（配線 0）/ `task-decomposer`（配線が抜けている疑い） |
| **自動で消える** | 6 | opabenia の複製（退役すれば） |
