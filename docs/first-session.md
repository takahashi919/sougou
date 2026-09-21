# 受付でセッションを始める

受付（このリポジトリ）でセッションを始めるときの型と、この次に控えている仕事。

**頼み方そのものは [`how_to_ask.html`](how_to_ask.html) に図で書いた。** ここは短い手順だけ。

---

## 型

1. `cd ~/sougou && claude`
2. エージェントは `CLAUDE.md` を自動で読む（door 一覧と線引きが入っている）
3. あとは普通に話しかける。**どの door へ渡すかは受付が決める**ので door 名は要らない
4. 実作業は door 越しに渡る。**受付でよその repo のファイルを直接編集しない**

新しいマシン・新しいコンテナなら、先に導入を流す:

```sh
RESEARCH_DIR=<research のクローン先> bash scripts/setup.sh
```

`foyer ls` に `paleo-video` と `llm-wiki` が並び、それぞれ 1 回ずつ ask が通れば成立している。

困ったら: 導入は [`setup.md`](setup.md)、権限で止まったら [`door_permissions.html`](door_permissions.html)、
スキルの所在は [`skill_inventory.md`](skill_inventory.md)。

---

## この次に控えている仕事

順番に意味があるので、上が片付いてから。

| # | 仕事 | どこの話 | 状態 |
|---|---|---|---|
| 1 | `task-decomposer` の配線 | research | ✅ 済（退役候補に倒した → `skill_inventory.md` §3-B）。実際の削除は research 側 |
| 2 | 図解系 3 本の可搬化 | research → kaisetu | ✅ 済（`kaisetu` へ移設。可搬化は不要だった → `skill_inventory.md` §3-E）。research 側は消さず凍結。**正本は kaisetu** |
| 3 | `opabenia` の退役 — README に移行済みと書く。research と同じ 4 キャラ・同じ skill 名の古い実装 | opabenia | |
| 4 | AKARI のゲート再定義 — `akari_video_workflow.md` §7 が未決。デイノスクス回は `legacy_unverified` で通した | research（ADR） | |
| 5 | 素材の作業台 — `asset_catalog.py` に `serve` を足して索引を目で見られるようにする | research | |
