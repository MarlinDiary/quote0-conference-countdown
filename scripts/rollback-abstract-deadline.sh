#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
target_commit="62dc17f"
raw_config="https://raw.githubusercontent.com/MarlinDiary/quote0-conference-countdown/main/conference.yml"

cd "$repo_root"

if [[ "${1:-}" == "--dry-run" ]]; then
  printf 'git revert --no-edit %s\n' "$target_commit"
  printf 'git push origin %s\n' "$(git branch --show-current)"
  printf 'wait for raw conference.yml to report deadline: 2026-09-25\n'
  printf 'railway ssh env QUOTE_PUSH_ENABLED=true /app/.venv/bin/python display.py\n'
  exit 0
fi

if [[ -n "$(git status --porcelain)" ]]; then
  echo "Working tree must be clean before rollback." >&2
  exit 1
fi

git revert --no-edit "$target_commit"
git push origin "$(git branch --show-current)"

for _ in {1..15}; do
  if curl -fsSL "$raw_config" | grep -q '^deadline: 2026-09-25$'; then
    railway ssh env QUOTE_PUSH_ENABLED=true /app/.venv/bin/python display.py
    exit 0
  fi
  sleep 2
done

echo "Raw GitHub configuration did not update before timeout." >&2
exit 1
