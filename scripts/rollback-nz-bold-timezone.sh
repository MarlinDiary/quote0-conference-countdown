#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
target_commit="aa36eca"

cd "$repo_root"

if [[ "${1:-}" == "--dry-run" ]]; then
  printf 'git revert --no-edit %s\n' "$target_commit"
  printf 'git push origin %s\n' "$(git branch --show-current)"
  printf 'railway up --detach\n'
  exit 0
fi

if [[ -n "$(git status --porcelain)" ]]; then
  echo "Working tree must be clean before rollback." >&2
  exit 1
fi

git revert --no-edit "$target_commit"
git push origin "$(git branch --show-current)"
railway up --detach
