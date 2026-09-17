#!/usr/bin/env bash
# Link this bundle into the places Claude Code loads from.
# Claude Code reads skills from ~/.claude/skills and agents from ~/.claude/agents, so the
# repo is the source of truth and those two locations hold symlinks back to it. Edit here
# and the change is live with nothing to copy.
#
# Alternative: install it as a plugin instead. This repo carries a .claude-plugin manifest.
#
# Safe to re-run: it replaces existing links and refuses to clobber a real file.
set -euo pipefail

BUNDLE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS="$HOME/.claude/skills"
AGENTS="$HOME/.claude/agents"
mkdir -p "$SKILLS" "$AGENTS"

link() {  # link <source> <target>
  local src="$1" dst="$2"
  if [ -e "$dst" ] && [ ! -L "$dst" ]; then
    echo "  SKIP $(basename "$dst") is a real file, not a link. Move it aside first." >&2
    return 1
  fi
  rm -f "$dst"
  ln -s "$src" "$dst"
  echo "  linked $(basename "$dst")"
}

echo "skill:"
link "$BUNDLE/skills/pre-ship-ux-audit" "$SKILLS/pre-ship-ux-audit"

echo "agents:"
for f in "$BUNDLE"/agents/*.md; do
  link "$f" "$AGENTS/$(basename "$f")"
done

echo
echo "checking:"
python3 "$BUNDLE/skills/pre-ship-ux-audit/scripts/check_consistency.py" | tail -4
