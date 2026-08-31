#!/bin/sh
# Generate the league's testnet wallets and write the master seed to .env.
#
#   ./scripts/new_wallet.sh
#
# One master seed, six pundit wallets derived from it deterministically, so only
# the master is a secret and the set is reproducible on any machine.
# The seed is written to .env (chmod 600, gitignored) and never printed.
#
# TESTNET ONLY. Never put a seed here that has ever held real money.
set -eu
cd "$(dirname "$0")/.."
. .venv/bin/activate

python - <<'PY'
import os, secrets, stat, sys
sys.path.insert(0, ".")
from eth_account import Account
from agent.wallet import key_for

existing = None
if os.path.exists(".env"):
    for line in open(".env"):
        if line.startswith("RECEIPTS_MASTER_SEED="):
            existing = line.split("=", 1)[1].strip()

if existing:
    print("RECEIPTS_MASTER_SEED already set in .env; reusing it.")
    print("Delete that line first if you really want a new one.\n")
    seed = existing
else:
    seed = secrets.token_hex(32)
    with open(".env", "a") as f:
        f.write(f"\nRECEIPTS_MASTER_SEED={seed}\n")
    os.chmod(".env", stat.S_IRUSR | stat.S_IWUSR)
    print("new master seed written to .env (chmod 600). Never printed.\n")

os.environ["RECEIPTS_MASTER_SEED"] = seed
master = Account.from_key("0x" + seed).address

# The evidence service is the payee. We own both sides, so it is the master.
if "EVIDENCE_PAY_TO=" not in open(".env").read():
    with open(".env", "a") as f:
        f.write(f"EVIDENCE_PAY_TO={master}\n")

print(f"{'payee (evidence service)':28} {master}")
print()
print("pundit wallets, each pays for its own evidence:")
for i in range(1, 7):
    pid = f"pundit_{i}"
    print(f"  {pid:26} {Account.from_key(key_for(pid)).address}")
print()
print("FUND pundit_1 FIRST. One settled payment closes the Base multiplier;")
print("the other five are only needed for a full six-pundit league.")
print()
print("  USDC  https://faucet.circle.com          (pick Base Sepolia)")
print("  ETH   https://www.alchemy.com/faucets/base-sepolia")
print()
print("x402 pays from the USDC balance directly and the facilitator covers gas,")
print("so a pundit needs USDC only. The ETH is for deploying League.sol on day 7.")
PY
