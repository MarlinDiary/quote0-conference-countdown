#!/bin/sh
set -eu

if [ "${1:-}" = "--dry-run" ]; then
  printf 'railway variables --set QUOTE_PUSH_ENABLED=false\n'
  exit 0
fi

command -v railway >/dev/null 2>&1 || {
  printf 'railway CLI is required\n' >&2
  exit 1
}

railway variables --set QUOTE_PUSH_ENABLED=false >/dev/null
test "$(railway variables --kv | awk -F= '$1 == "QUOTE_PUSH_ENABLED" { print $2 }')" = false
printf 'QUOTE_PUSH_ENABLED=false\n'
