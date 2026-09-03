#!/bin/sh
# Upgrade the Sibyl Memory family, safely.
#
#   ./scripts/upgrade_sibyl.sh
#
# Runs only once the bench is idle: a schema or API change mid-measurement would
# invalidate a three-hour run. Snapshots the databases first, upgrades, then
# proves the whole lifecycle still works before letting the league back on.
set -eu
cd "$(dirname "$0")/.."
. .venv/bin/activate
mkdir -p logs
say() { printf '%s %s\n' "$(date -u +%FT%TZ)" "$*" | tee -a logs/upgrade.log; }

if pgrep -f "bench.run" >/dev/null 2>&1; then
  say "bench still running — refusing to upgrade underneath it"
  exit 1
fi

BEFORE=$(python -c "import importlib.metadata as m; print(m.version('sibyl-memory-client'))")
say "current sibyl-memory-client $BEFORE"

# The memory stores ARE the submission. Snapshot before touching the schema.
SNAP="backups/memory-$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$SNAP" && cp memory/*.db "$SNAP"/ 2>/dev/null || true
say "snapshotted $(ls "$SNAP" | wc -l | tr -d ' ') databases to $SNAP"

say "pausing the league for the upgrade"
pkill -f league.sh 2>/dev/null || true
sleep 2

uv pip install -q -U sibyl-memory-client sibyl-memory-cli sibyl-memory-mcp
AFTER=$(python -c "import importlib.metadata as m; print(m.version('sibyl-memory-client'))")
say "upgraded $BEFORE -> $AFTER"

say "schema check"
sibyl health 2>&1 | sed -n '1,8p' | tee -a logs/upgrade.log

say "running the full suite against the new version"
if python -m pytest -p no:cacheprovider -q 2>&1 | tail -3 | tee -a logs/upgrade.log | grep -q "failed"; then
  say "TESTS FAILED on $AFTER — databases are snapshotted at $SNAP"
  say "roll back with: uv pip install -q sibyl-memory-client==$BEFORE"
  exit 1
fi

say "reading the existing stores back on the new version"
python - <<'PY' 2>&1 | tee -a logs/upgrade.log
import sys; sys.path.insert(0, ".")
from agent.memory import Memory
from resolver.loop import pundit_ids
for pid in pundit_ids():
    m = Memory(pid)
    cells = m.all_reliability_including_archived()
    ev = m.recent_events(limit=5)
    hits = m.recall("epl", limit=3)
    print(f"  {pid:10} {len(cells):3} cells, {len(ev)} recent events, fts returns {len(hits)}")
PY

say "restarting the league"
nohup caffeinate -dimsu ./scripts/league.sh >> logs/league.out 2>&1 &
sleep 4
pgrep -f league.sh >/dev/null && say "league running on $AFTER" || say "LEAGUE FAILED TO RESTART"
say "done. snapshot kept at $SNAP"
