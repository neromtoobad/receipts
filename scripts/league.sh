#!/bin/sh
# The league. Runs for ten days without supervision.
#
#   ./scripts/league.sh            # every 20 minutes, forever
#   TICK_SECONDS=600 ./scripts/league.sh
#
# Each tick: six pundits each forecast one market they have not seen, in six
# separate processes that die afterwards; the resolver scores whatever has
# resolved since; the dashboard is rebuilt. Then it sleeps.
#
# A sleeping laptop is a failed run — that cost us an agent review once — so
# caffeinate wraps the whole thing and every miss is logged loudly.
set -u
cd "$(dirname "$0")/.."
. .venv/bin/activate

TICK_SECONDS=${TICK_SECONDS:-1200}
PUNDITS=${PUNDITS:-"pundit_1 pundit_2 pundit_3 pundit_4 pundit_5 pundit_6"}
MODEL=${RECEIPTS_LIVE_MODEL:-qwen2.5:7b-instruct}
export RECEIPTS_OPENAI_BASE_URL=${RECEIPTS_OPENAI_BASE_URL:-http://localhost:11434/v1}
export EVIDENCE_SETTLE=${EVIDENCE_SETTLE:-0}
export EVIDENCE_PAY_TO=$(grep '^EVIDENCE_PAY_TO=' .env 2>/dev/null | cut -d= -f2)

mkdir -p proof logs
LOG=logs/league.log
MISS=proof/tick_misses.log
say() { printf '%s %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*" | tee -a "$LOG"; }
miss() { printf '%s MISS %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*" | tee -a "$MISS" >&2; }

need_service() {
  curl -sf --max-time 3 http://127.0.0.1:8402/health >/dev/null 2>&1 && return 0
  say "evidence service down, starting it"
  uvicorn evidence.app:app --port 8402 --log-level warning >> logs/evidence.log 2>&1 &
  i=0; while [ $i -lt 40 ]; do
    curl -sf --max-time 2 http://127.0.0.1:8402/health >/dev/null 2>&1 && return 0
    sleep 0.5; i=$((i+1))
  done
  miss "evidence service would not start"; return 1
}

need_model() {
  curl -sf --max-time 5 http://localhost:11434/api/version >/dev/null 2>&1 && return 0
  say "ollama down, starting it"
  ollama serve >> logs/ollama.log 2>&1 &
  i=0; while [ $i -lt 30 ]; do
    curl -sf --max-time 2 http://localhost:11434/api/version >/dev/null 2>&1 && return 0
    sleep 1; i=$((i+1))
  done
  miss "ollama would not start"; return 1
}

say "league starting. tick ${TICK_SECONDS}s, model ${MODEL}, commit $(git rev-parse --short HEAD)"
trap 'say "league stopped"; exit 0' INT TERM

while true; do
  START=$(date +%s)
  need_model || { sleep 60; continue; }
  need_service || { sleep 60; continue; }

  for p in $PUNDITS; do
    # Each pundit is its own process and dies when it is done. That is the thesis,
    # not an implementation detail.
    if ! python -m agent.run_once --agent "$p" --pick --model "$MODEL" --quiet; then
      miss "$p run_once exited non-zero"
    fi
  done

  python -m resolver.loop --once --quiet >> "$LOG" 2>&1 || miss "resolver exited non-zero"
  # Refresh the data the site reads. Rebuilding the site itself is a publish
  # step, not a tick step — this used to call web.build_site, which owned
  # docs/ and silently reverted the real UI on every tick.
  python -m web.export >/dev/null 2>&1 || miss "league export failed"

  DONE=$(python - <<'PY'
import sys; sys.path.insert(0, ".")
from resolver.loop import pundit_ids
from agent.memory import Memory
f = r = 0
for p in pundit_ids():
    for e in Memory(p).recent_events(limit=400):
        k = (e.get("extra") or {}).get("kind")
        f += k == "forecast"; r += k == "resolution"
print(f"{f} forecasts, {r} resolved")
PY
)
  say "tick done in $(( $(date +%s) - START ))s — $DONE"
  sleep "$TICK_SECONDS"
done
