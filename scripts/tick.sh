#!/bin/sh
# One league tick. Every pundit forecasts one market in its OWN process, and
# every process dies before the next one starts. Nothing is shared but the disk.
#
#   ./scripts/tick.sh [--domain epl] [--offline]
set -u
cd "$(dirname "$0")/.."
. .venv/bin/activate

PUNDITS="pundit_1 pundit_2 pundit_3 pundit_4 pundit_5 pundit_6"
ARGS="$*"
STAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)
MISSES=0

for p in $PUNDITS; do
  if ! python -m agent.run_once --agent "$p" --pick $ARGS; then
    # A miss is loud on purpose. A sleeping mac cost us a submission once.
    echo "MISS $STAMP $p exited non-zero" | tee -a proof/tick_misses.log >&2
    MISSES=$((MISSES + 1))
  fi
done

echo "tick $STAMP complete, $MISSES misses"
exit 0
