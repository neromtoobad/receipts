#!/bin/sh
# Generates a fresh Base Sepolia burner and writes it to .env with 0600.
# Prints the ADDRESS only. The key never reaches your terminal history.
set -e
cd "$(dirname "$0")"
. .venv/bin/activate
python - <<'PY'
import os, stat
from eth_account import Account
a = Account.create()
line = f"AGENT_ADDRESS={a.address}\nAGENT_PRIVATE_KEY={a.key.hex()}\n"
mode = "a" if os.path.exists(".env") else "w"
with open(".env", mode) as f: f.write(line)
os.chmod(".env", stat.S_IRUSR | stat.S_IWUSR)
print("burner address:", a.address)
print("private key written to .env (chmod 600). testnet only. never fund with real money.")
PY
