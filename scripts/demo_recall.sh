#!/bin/bash
# The cold-start recall beat, as one continuous unedited take.
#
# The hackathon gate asks for a fresh session recalling state written earlier,
# with a commit hash or timestamp on screen. This script is that segment. It
# runs the real agent against the real store — there is no --offline here on
# purpose, because a stand-in forecaster would prove nothing.
#
#   ./scripts/demo_recall.sh <market_id>
set -u
cd "$(dirname "$0")/.."
. .venv/bin/activate

P=${PUNDIT:-vertex}
MARKET=${1:?usage: demo_recall.sh <market_id>}
B=$(printf '\033[1m'); D=$(printf '\033[2m'); R=$(printf '\033[0m'); C=$(printf '\033[36m')

rule () { printf "${D}%s${R}\n" "────────────────────────────────────────────────────────────────"; }
pause () { sleep "${1:-2}"; }

printf '\033[2J\033[H'
printf "${B}RECEIPTS — cold-start recall${R}\n"
rule
printf "  commit   ${C}%s${R}\n" "$(git rev-parse HEAD)"
printf "  utc      ${C}%s${R}\n" "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
printf "  sibyl    ${C}%s${R}\n" "$(python -c 'import sibyl_memory_client as s; print(s.__version__)' 2>/dev/null)"
printf "  pundit   ${C}%s${R}\n" "$(python -c 'import sys;from agent.identity import display,resolve;print(display(resolve(sys.argv[1])))' "$P")"
printf "  market   ${C}%s${R}\n" "$MARKET"
rule
pause 3

printf "\n${B}1. What this agent has already learned.${R}\n"
printf "${D}   Earned by paying for sources and watching them resolve.${R}\n\n"
python -m agent.showmem --agent "$P" --top 5
pause 4

printf "\n${B}2. A forecast. Watch the process id.${R}\n\n"
printf "${D}   memory before:${R}\n"; python -m agent.showmem --agent "$P" --brief
printf "\n"
python -m agent.run_once --agent "$P" --market "$MARKET" --bench-model &
FPID=$!
printf "${D}   forecasting in pid %s${R}\n" "$FPID"
wait $FPID
printf "\n${C}   pid %s has exited. Nothing of it is in memory now.${R}\n" "$FPID"
ps -p $FPID >/dev/null 2>&1 && printf "   STILL ALIVE\n" || printf "${C}   confirmed: ps finds no such process.${R}\n"
printf "${D}   memory after — the dead process left this behind:${R}\n"
python -m agent.showmem --agent "$P" --brief
pause 4

printf "\n${B}3. A brand new process. Same market, no shared state.${R}\n"
printf "${D}   Watch it read back what pid %s wrote, and score itself against it.${R}\n\n" "$FPID"
python -m agent.run_once --agent "$P" --market "$MARKET" --bench-model &
GPID=$!
printf "${D}   forecasting in pid %s — a different process${R}\n" "$GPID"
wait $GPID
pause 3

printf "\n${B}4. The same market with memory deleted.${R}\n"
printf "${D}   Identical model, prompt and budget. Only memory is gone.${R}\n\n"
python -m agent.run_once --agent "$P" --market "$MARKET" --bench-model --arm amnesiac
rule
printf "${B}The second process knew what the first one learned. The third knew nothing.${R}\n"
rule
