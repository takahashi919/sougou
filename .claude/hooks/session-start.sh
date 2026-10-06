#!/bin/bash
# session-start.sh — cloud セッションで受付を成立させる（foyer を入れ、door を登録する）。
#
# cloud のコンテナは毎回まっさらなので、ここで毎回組み立てる。何度走らせてもよい。
# 隣に clone された repo だけを使う（private repo はセッションに付いていないと取れないため）:
#   /home/user/foyer                    → foyer をビルドして PATH へ
#   /home/user/llm-wiki (LLM-Wiki)      → door llm-wiki
#   /home/user/research (Research)      → door paleo-video
#   /home/user/readable-writing-dist    → plugin readable-writing
# 足りない repo は、最後に出す案内を読んだエージェントが add_repo で付けてから、このスクリプトを打ち直す。
set -euo pipefail

[ "${CLAUDE_CODE_REMOTE:-}" = "true" ] || exit 0

ROOT="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"
BASE="$(dirname "$ROOT")"
missing=()
log() { printf '[sougou] %s\n' "$*"; }
# clone 先の綴りは付け方で変わる（選んで始めると repo 名のまま、add_repo だと小文字）
dir_of() { local n; for n in "$@"; do [ -d "$BASE/$n" ] && { echo "$BASE/$n"; return; }; done; echo "$BASE/$1"; }

# llm-wiki の scripts/wiki は JST 前提で日付を採番する（docs/setup.md 手順 3）
[ -n "${CLAUDE_ENV_FILE:-}" ] && echo 'export TZ=Asia/Tokyo' >> "$CLAUDE_ENV_FILE"

# 1. foyer
if command -v foyer >/dev/null 2>&1; then
  :
elif [ -f "$BASE/foyer/package.json" ]; then
  if ( cd "$BASE/foyer" && npm install --no-audit --no-fund && npm run build && npm link ) >/tmp/foyer-build.log 2>&1; then
    log "foyer をビルドした"
  else
    log "foyer のビルドに失敗した（ログ: /tmp/foyer-build.log）"; tail -5 /tmp/foyer-build.log
  fi
else
  missing+=("takahashi919/foyer")
fi

# 2. door（foyer が無ければ登録できない）
has_door() { foyer ls --json 2>/dev/null | grep -q "\"name\": *\"$1\""; }
add_door() {  # <名前> <repo> <dir> <追加引数...>
  local name="$1" repo="$2" dir="$3"; shift 3
  if [ ! -d "$dir" ]; then missing+=("$repo"); return; fi
  command -v foyer >/dev/null 2>&1 || return
  has_door "$name" && return
  foyer add "$dir" --name "$name" --yes "$@" >/dev/null 2>&1
  log "door $name を登録した"
}
WIKI="$(dir_of llm-wiki LLM-Wiki)"
add_door llm-wiki takahashi919/LLM-Wiki "$WIKI" --mode full \
  --desc "llm-wiki — 外の世界 (会社・人・コミュニティ・記事・道具) への判断の記録; 司書が記録を根拠に答える"
[ -d "$WIKI" ] && chmod +x "$WIKI"/scripts/wiki "$WIKI"/scripts/*.sh 2>/dev/null || true
add_door paleo-video takahashi919/Research "$(dir_of research Research)" \
  --desc "paleo-video — 子供向け古生代教育動画の本番ハーネス; 研究(NotebookLM)→台本→音声→timing→レンダーのゲート制パイプライン。エピソード制作・素材・台本の依頼はここ"

# 3. readable-writing（文章を書く日だけ要る。無くても案内しない）
RW="$(dir_of readable-writing-dist)"
if [ -f "$RW/.claude-plugin/marketplace.json" ] && ! claude plugin list 2>/dev/null | grep -q 'readable-writing@'; then
  claude plugin marketplace add "$RW" >/dev/null && claude plugin install readable-writing@readable-writing-dist >/dev/null
  log "plugin readable-writing を入れた（skill は次のセッションから見える）"
fi

if [ ${#missing[@]} -gt 0 ]; then
  log "セッションに付いていない repo: ${missing[*]}"
  log "door が要る依頼のときだけ、add_repo で付けて /home/user/<repo> に clone し、"
  log "bash \"\$CLAUDE_PROJECT_DIR/.claude/hooks/session-start.sh\" を打ち直すこと（CLAUDE_CODE_REMOTE=true を付けて）"
fi
exit 0
