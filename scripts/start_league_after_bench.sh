#!/bin/sh
# Wait for the benchmark to release the model, then start the league and leave it
# running. Both want the same Ollama instance and the bench is the phase 6 proof,
# so it goes first.
set -u
cd "$(dirname "$0")/.."
mkdir -p logs
say() { printf '%s %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*" | tee -a logs/handoff.log; }

say "waiting for the bench to finish"
while pgrep -f "bench.run" >/dev/null 2>&1; do sleep 30; done
say "bench finished, model free"

# Give it a moment to flush proof/BENCH.md before competing for the GPU.
sleep 10
nohup caffeinate -dimsu ./scripts/league.sh >> logs/league.out 2>&1 &
say "league started (pid $!) under caffeinate"
