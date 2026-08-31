#!/bin/sh
# Add an API key to .env without it appearing in shell history or on screen.
#
#   ./scripts/set_key.sh AION_API_KEY
#
# Prompts silently, appends KEY=VALUE to .env, and re-chmods to 600.
set -eu
cd "$(dirname "$0")/.."
NAME=${1:?usage: ./scripts/set_key.sh VARIABLE_NAME}

printf 'paste %s (input hidden), then Enter: ' "$NAME" >&2
stty -echo 2>/dev/null || true
IFS= read -r VALUE
stty echo 2>/dev/null || true
printf '\n' >&2

[ -n "$VALUE" ] || { echo "empty, nothing written" >&2; exit 1; }
touch .env
# drop any previous line for this variable, then append the new one
grep -v "^${NAME}=" .env > .env.tmp 2>/dev/null || true
mv .env.tmp .env
printf '%s=%s\n' "$NAME" "$VALUE" >> .env
chmod 600 .env
echo "$NAME written to .env (${#VALUE} chars), mode 600" >&2
