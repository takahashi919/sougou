#!/usr/bin/env bash
# setup.sh — 総合受付の導入を一気通貫で流す。
#
# 何度打ち直してもよい（既にあるものは飛ばす）。
# 変更したいときは環境変数で:
#   RESEARCH_DIR=~/dev/research WIKI_DIR=~/wiki/llm-wiki TOOLS_DIR=~/tools bash scripts/setup.sh
set -euo pipefail

TOOLS_DIR="${TOOLS_DIR:-$HOME/tools}"
WIKI_DIR="${WIKI_DIR:-$HOME/wiki/llm-wiki}"
RESEARCH_DIR="${RESEARCH_DIR:-}"
KAISETU_DIR="${KAISETU_DIR:-$HOME/dev/kaisetu}"
OWNER="${OWNER:-takahashi919}"

have() { command -v "$1" >/dev/null 2>&1; }
step() { printf '\n\033[1m== %s\033[0m\n' "$1"; }
skip() { printf '   skip: %s\n' "$1"; }
ok()   { printf '   ok:   %s\n' "$1"; }

step "0. 道具の確認"
missing=""
for c in git node python3; do have "$c" || missing="$missing $c"; done
[ -n "$missing" ] && { echo "   足りない:$missing — 入れてから再実行"; exit 1; }
have rg || echo "   注意: rg (ripgrep) が無い。llm-wiki の司書が探せない"
ok "git / node $(node -v) / python3 $(python3 -V 2>&1 | cut -d' ' -f2)"

step "1. foyer（door を叩く窓口 CLI）"
if have foyer; then
  skip "foyer は入っている（$(foyer --version 2>/dev/null || echo 'version 不明')）"
else
  mkdir -p "$TOOLS_DIR"
  [ -d "$TOOLS_DIR/foyer" ] || git clone "https://github.com/$OWNER/foyer.git" "$TOOLS_DIR/foyer"
  ( cd "$TOOLS_DIR/foyer" && npm install --no-audit --no-fund && npm run build && npm link )
  ok "foyer を入れた"
fi
foyer doctor || echo "   注意: foyer doctor が警告を出した（上の出力を見ること）"

step "2. toolhint（操作の直前に docs を注入する hook）"
if claude plugin list 2>/dev/null | grep -q toolhint; then
  skip "toolhint は入っている"
else
  claude plugin marketplace add "$OWNER/toolhint"
  claude plugin install toolhint@toolhint
  echo "   PATH に足すこと（シェルの rc へ）:"
  echo '     export PATH="$HOME/.claude/plugins/marketplaces/toolhint/cli:$PATH"'
fi

step "3. llm-wiki（外の世界への判断を置く door）"
if [ -d "$WIKI_DIR" ]; then
  skip "$WIKI_DIR は既にある"
else
  mkdir -p "$(dirname "$WIKI_DIR")"
  git clone "https://github.com/$OWNER/LLM-Wiki.git" "$WIKI_DIR"
  chmod +x "$WIKI_DIR"/scripts/wiki "$WIKI_DIR"/scripts/*.sh 2>/dev/null || true
  ok "clone した"
fi
# allowlist が無いと、非対話の door は Bash も Write も全部拒否される。
# committed の settings.json に書いた allow は「フォルダの信頼」を待つので
# door からは効かない。追跡しない settings.local.json だけが待たずに効く。
LOCAL_SETTINGS="$WIKI_DIR/.claude/settings.local.json"
if [ -f "$LOCAL_SETTINGS" ]; then
  skip "$LOCAL_SETTINGS は既にある"
else
  mkdir -p "$(dirname "$LOCAL_SETTINGS")"
  cat > "$LOCAL_SETTINGS" <<'JSON'
{
  "permissions": {
    "allow": [
      "Bash(./scripts/wiki *)",
      "Bash(scripts/wiki *)",
      "Bash(rg *)",
      "Edit(entities/**)",
      "Edit(records/**)"
    ]
  }
}
JSON
  ok "司書の allowlist を置いた（→ docs/setup.md の「権限」）"
fi

if foyer ls 2>/dev/null | grep -q '^llm-wiki[[:space:]]'; then
  skip "door llm-wiki は登録済み"
else
  # --name: repo 名は LLM-Wiki だが door 名は CLAUDE.md の綴りに揃える
  # mode は safe のまま。司書が動くのに必要な許可は上の allowlist で与えてある
  foyer add "$WIKI_DIR" --name llm-wiki --yes \
    --desc "llm-wiki — 外の世界 (会社・人・コミュニティ・記事・道具) への判断の記録; 司書が記録を根拠に答える"
fi

step "4. paleo-video（動画制作の door）"
if foyer ls 2>/dev/null | grep -q '^paleo-video[[:space:]]'; then
  skip "door paleo-video は登録済み"
elif [ -z "$RESEARCH_DIR" ]; then
  echo "   RESEARCH_DIR が未指定。research のクローン先を渡して再実行するか、手で:"
  echo "     foyer add <research のパス> --name paleo-video --desc \"paleo-video — …\""
elif [ ! -d "$RESEARCH_DIR" ]; then
  echo "   $RESEARCH_DIR が無い。パスを確かめること"
else
  foyer add "$RESEARCH_DIR" --name paleo-video --yes \
    --desc "paleo-video — 子供向け古生代教育動画の本番ハーネス; 研究(NotebookLM)→台本→音声→timing→レンダーのゲート制パイプライン。エピソード制作・素材・台本の依頼はここ"
fi

step "5. kaisetu（説明物の工房の door）"
if [ ! -d "$KAISETU_DIR" ]; then
  mkdir -p "$(dirname "$KAISETU_DIR")"
  git clone "https://github.com/$OWNER/kaisetu.git" "$KAISETU_DIR"
  ok "clone した"
else
  skip "$KAISETU_DIR は既にある"
fi
# allowlist は追跡されていない間だけ trust を待たずに効く（→ docs/setup.md の「権限」）
if [ -f "$KAISETU_DIR/.claude/settings.local.json" ]; then
  skip "kaisetu の allowlist は置いてある"
elif [ -f "$KAISETU_DIR/.claude/settings.json" ]; then
  cp "$KAISETU_DIR/.claude/settings.json" "$KAISETU_DIR/.claude/settings.local.json"
  ok "kaisetu の allowlist を置いた"
fi
[ -f "$KAISETU_DIR/.env" ] || echo "   注意: $KAISETU_DIR/.env が無い。cp .env.example .env して API キーを入れること"
if foyer ls 2>/dev/null | grep -q '^kaisetu[[:space:]]'; then
  skip "door kaisetu は登録済み"
else
  foyer add "$KAISETU_DIR" --name kaisetu --yes \
    --desc "kaisetu — 説明物の工房; 図解・解説ページ・赤ペン・レビューの可視化。本番の動画制作は扱わない"
fi

step "6. 汎用スキルを配る"
if [ -n "$(ls -A skills 2>/dev/null | grep -v README.md || true)" ]; then
  python3 scripts/sync_user_skills.py --apply
else
  skip "skills/ が空（→ skills/README.md）"
fi

step "できあがり"
foyer ls
cat <<'EOF'

次の一手:
  cd ~/sougou && claude
  「外の世界の知識」を試す:  foyer ask llm-wiki "org/anthropic について知ってること全部"
  「動画のこと」を試す:      foyer ask paleo-video "いま制作中のエピソードは？"
EOF
