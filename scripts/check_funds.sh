#!/bin/sh
# Show the USDC and ETH balance of every league wallet on Base Sepolia.
#   ./scripts/check_funds.sh
set -eu
cd "$(dirname "$0")/.."
. .venv/bin/activate
python - <<'PY'
import sys; sys.path.insert(0, ".")
import httpx
from eth_account import Account
from agent.env import load; load()
from agent.wallet import key_for, master_seed
from evidence.x402 import USDC

RPC = "https://sepolia.base.org"
seed = master_seed()
if not seed:
    raise SystemExit("no RECEIPTS_MASTER_SEED in .env; run ./scripts/new_wallet.sh")

def call(to, data):
    r = httpx.post(RPC, timeout=20, json={"jsonrpc": "2.0", "id": 1, "method": "eth_call",
          "params": [{"to": to, "data": data}, "latest"]}).json()
    return int(r.get("result", "0x0"), 16)

def eth(addr):
    r = httpx.post(RPC, timeout=20, json={"jsonrpc": "2.0", "id": 1,
          "method": "eth_getBalance", "params": [addr, "latest"]}).json()
    return int(r.get("result", "0x0"), 16) / 1e18

rows = [("payee", Account.from_key("0x" + seed).address)]
rows += [(f"pundit_{i}", Account.from_key(key_for(f"pundit_{i}")).address) for i in range(1, 7)]

print(f"{'wallet':12}{'address':46}{'USDC':>10}{'ETH':>12}")
print("-" * 80)
for name, addr in rows:
    usdc = call(USDC, "0x70a08231" + addr[2:].rjust(64, "0")) / 1e6
    print(f"{name:12}{addr:46}{usdc:>10.4f}{eth(addr):>12.5f}")
print()
print("pundit_1 needs USDC to settle an x402 payment. The facilitator pays gas,")
print("so ETH is only needed later, for deploying League.sol.")
PY
