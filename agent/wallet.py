"""One wallet per pundit.

Six pundits are six economic agents, so they pay from six different addresses.
Keys are derived deterministically from a single master seed in .env, which
means the set is reproducible on any machine and only the master is a secret.

    RECEIPTS_MASTER_SEED=<64 hex chars>

scripts/new_wallet.sh writes one if there is none. Testnet only: never put a
seed here that has ever held real money.
"""
from __future__ import annotations

import os
from pathlib import Path

from eth_account import Account
from eth_utils import keccak

ROOT = Path(__file__).resolve().parent.parent


from agent.env import load as _load_env


def master_seed() -> str | None:
    _load_env()
    return os.environ.get("RECEIPTS_MASTER_SEED") or os.environ.get("AGENT_PRIVATE_KEY")


def key_for(pundit_id: str) -> str | None:
    """Deterministic per-pundit private key. None when no seed is configured, so
    callers can run the whole loop unfunded and record that honestly."""
    seed = master_seed()
    if not seed:
        return None
    raw = bytes.fromhex(seed.removeprefix("0x"))
    return "0x" + keccak(raw + pundit_id.encode()).hex()


def address_for(pundit_id: str) -> str | None:
    k = key_for(pundit_id)
    return Account.from_key(k).address if k else None
