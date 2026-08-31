#!/bin/sh
# Publish the trust map once there is something on it worth looking at.
#
# Waits for resolutions to land and cells to form, then publishes once. Falls
# back to publishing anyway after MAX_WAIT so a quiet feed does not mean the
# public page sits stale forever.
set -u
cd "$(dirname "$0")/.."
mkdir -p logs
MIN_CELLS=${MIN_CELLS:-6}
MAX_WAIT=${MAX_WAIT:-21600}     # 6 hours
START=$(date +%s)
say() { printf '%s %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*" | tee -a logs/publish.log; }

say "waiting for at least $MIN_CELLS trust-map cells (or ${MAX_WAIT}s)"
while true; do
  STATE=$(. .venv/bin/activate && python - <<'PY'
import sys; sys.path.insert(0, ".")
from web.build_site import pundits, collect
cells = resolved = 0
for p in pundits():
    c = collect(p)
    cells += len(c["cells"]); resolved += len(c["resolutions"])
print(f"{cells} {resolved}")
PY
)
  CELLS=$(echo "$STATE" | cut -d' ' -f1)
  RESOLVED=$(echo "$STATE" | cut -d' ' -f2)
  ELAPSED=$(( $(date +%s) - START ))

  if [ "${CELLS:-0}" -ge "$MIN_CELLS" ]; then
    say "$CELLS cells from $RESOLVED resolutions — publishing"
    break
  fi
  if [ "$ELAPSED" -ge "$MAX_WAIT" ]; then
    say "max wait reached with $CELLS cells, $RESOLVED resolutions — publishing anyway"
    break
  fi
  say "still thin: $CELLS cells, $RESOLVED resolved (${ELAPSED}s elapsed)"
  sleep 600
done

./scripts/publish_site.sh 2>&1 | tee -a logs/publish.log
say "done"
