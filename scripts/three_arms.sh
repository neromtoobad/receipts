#!/bin/sh
# The deletion test, live, on one market. This is demo beat 4.
#
#   ./scripts/three_arms.sh [market_id]
#
# Same pundit history, same market, same prompt, same model. The only variable
# is what the agent is allowed to remember.
set -u
cd "$(dirname "$0")/.."
. .venv/bin/activate
export EVIDENCE_SETTLE=${EVIDENCE_SETTLE:-0}

MID=${1:-}
if [ -z "$MID" ]; then
  MID=$(curl -sS "${EVIDENCE_URL:-http://127.0.0.1:8402}/markets?domain=epl" \
        | python -c "import json,sys;print(json.load(sys.stdin)['markets'][0]['id'])")
fi

echo "market: $MID"
echo "commit: $(git rev-parse --short HEAD)   $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo
for arm in sibyl flat amnesiac; do
  printf '──────── %s ────────\n' "$arm"
  python -m agent.run_once --agent "arm_$arm" --market "$MID" --arm "$arm" --offline
  echo
done
