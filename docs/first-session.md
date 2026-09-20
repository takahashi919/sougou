# 受付での最初のセッション

受付（このリポジトリ）でセッションを始めるときの型と、**今回の最初の依頼文**。
最初の依頼は一回限りなので、終わったらその節は削ってよい。

---

## 型 — 受付でセッションを始めるとき

1. `cd ~/sougou && claude`
2. エージェントは `CLAUDE.md` を自動で読む（door 一覧と線引きが入っている）
3. 実作業は door 越しに渡す。**受付でよその repo のファイルを直接編集しない**

困ったら: 導入は `docs/setup.md`、スキルの所在は `docs/skill_inventory.md`。

---

## 今回の最初の依頼文（そのまま貼る）

```
この repo は総合受付（マクロハーネス）。ここでは実作業をせず、foyer の door 越しに
専門ハーネスへ渡して、戻ってきた答えを読む。まず CLAUDE.md を読んで。

## 最初に: 受付が成立しているか確認して

    foyer ls
    foyer doctor

door が空、または foyer コマンドが無いなら、docs/setup.md に従って導入して:

    RESEARCH_DIR=<research のクローン先> bash scripts/setup.sh

`paleo-video` と `llm-wiki` の 2 つが foyer ls に並び、それぞれに 1 回ずつ
ask が通るところまで確認してから次へ進んで。通らない項目があれば、
そこで止めて何が起きたか教えて（勝手に回避策を作らない）。

## そのあとの仕事: task-decomposer の配線を調べる

docs/skill_inventory.md の §3-B に書いてある件。要点はこう:

- research の .claude/skills/task-decomposer/ は 20 行しかなく、
  .claude/agents/ と .claude/commands/ のどこからも名指しされていない
- 一方で research の CLAUDE.md §1 は Orchestrator-Workers を掲げていて、
  分解は専用エージェント/Skill に委譲する建て付けになっている
- つまり「要らないから呼ばれない」のか「配線が抜けている」のか判らない

**消す前に確かめたい。** 調べる対象は research の中なので、受付で research を
開かずに door へ聞くこと:

    foyer ask paleo-video "task-decomposer skill が .claude/agents と .claude/commands の
    どこからも名指しされていない。実際のエピソード制作の動線（/new-episode から
    台本生成までの間）で、タスク分解は誰がどうやっている？ task-decomposer は
    使われているか、それとも配線が抜けているか、実際のファイルを読んで答えて"

返ってきた答えで、次のどれかに倒して:

- **配線が抜けている** → どこに何を 1 行足せばいいかを提案する。
  実装は door 側の仕事なので、受付からは提案までにする
- **別のものが役割を引き継いでいる** → task-decomposer は退役候補。
  docs/skill_inventory.md の §3-B とまとめの表を更新する
- **判断がつかない** → 私に聞く。勝手に消さない

## 守ること

- 受付で作業しない。research のファイルをここで直接編集しない
- CLAUDE.md を太らせない（door が増えても 1 door = 表の 1 行）
- door 越しは 1 行 = 1 ターン。exit code 3 は busy なので待たずに後で来る
- 判断が出たら「何をどう決めたか・なぜか」を残す:
  foyer ask llm-wiki "… 入れて"
  ただし読めば分かる事実だけの記録は、頼む前にこちらで外すこと
- 認証情報・API キー・.env の中身を依頼文に含めない
```

---

## この次に控えている仕事（今回は触らない）

順番に意味があるので、上が片付いてから。

| # | 仕事 | どこの話 |
|---|---|---|
| 1 | `task-decomposer` の配線（**今回**） | research |
| 2 | 図解系 3 本の可搬化 — 実行コマンドのリポジトリ相対パスを直す（→ `docs/skill_inventory.md` §3-E） | research |
| 3 | `opabenia` の退役 — README に移行済みと書く。research と同じ 4 キャラ・同じ skill 名の古い実装 | opabenia |
| 4 | AKARI のゲート再定義 — `akari_video_workflow.md` §7 が未決。デイノスクス回は `legacy_unverified` で通した | research（ADR） |
| 5 | 素材の作業台 — `asset_catalog.py` に `serve` を足して索引を目で見られるようにする | research |
