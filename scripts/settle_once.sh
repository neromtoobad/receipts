#!/bin/sh
# Buy one informant for real money on Base Sepolia and print the tx hash.
# This is the Base multiplier, demonstrable in one command.
set -eu
cd "$(dirname "$0")/.."
. .venv/bin/activate
export EVIDENCE_SETTLE=1
export EVIDENCE_PAY_TO=$(grep '^EVIDENCE_PAY_TO=' .env | cut -d= -f2)
export EVIDENCE_MARKETS_FILE=${EVIDENCE_MARKETS_FILE:-tests/fixtures/markets.json}

uvicorn evidence.app:app --port 8402 --log-level warning &
UV=$!
trap 'kill $UV 2>/dev/null || true' EXIT INT TERM
i=0; while [ $i -lt 40 ]; do curl -sf localhost:8402/health >/dev/null 2>&1 && break; sleep 0.5; i=$((i+1)); done

python - "$@" <<'PY'
import sys; sys.path.insert(0, ".")
from agent.env import load; load()
from agent.buyer import Buyer
who = sys.argv[1] if len(sys.argv) > 1 else "pundit_1"
what = sys.argv[2] if len(sys.argv) > 2 else "island_desk"
b = Buyer(who, "http://127.0.0.1:8402")
mid = b.markets("epl")[0]["id"]
got = b.buy(what, mid)
r = got.get("receipt") or {}
print(f"{who} bought {what} on {mid}")
print(f"  paid     {got.get('price')} USDC")
print(f"  settled  {r.get('settled')}")
print(f"  tx       {r.get('tx_hash')}")
if r.get("tx_hash"):
    print(f"  explorer https://sepolia.basescan.org/tx/{r['tx_hash']}")
if r.get("settlement_error"):
    print(f"  error    {str(r['settlement_error'])[:200]}")
print(f"  evidence {got.get('payload')}")
b.close()
PY
