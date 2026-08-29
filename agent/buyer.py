"""The paying client. Turns a 402 into evidence, or into an honest failure.

There is no free path: every informant call goes through the x402 handshake.
When the wallet is unfunded the signature is still real and the service still
serves, but settlement fails on balance and that failure is recorded rather than
glossed over. Nothing in this repo ever reports a payment it has no hash for.
"""
from __future__ import annotations

import os
from typing import Any

import httpx

from agent import wallet
from evidence.x402 import HEADER, sign_payment

# Used only when no RECEIPTS_MASTER_SEED is configured, so the loop is runnable
# before the wallet exists. Deterministic, worthless, and always reported unfunded.
DEV_SEED = "00" * 32
DEFAULT_URL = os.environ.get("EVIDENCE_URL", "http://127.0.0.1:8402")


class Buyer:
    def __init__(self, pundit_id: str, base_url: str = DEFAULT_URL, timeout: float = 30.0):
        self.pundit_id = pundit_id
        self.base_url = base_url.rstrip("/")
        self.http = httpx.Client(timeout=timeout)
        self.key = wallet.key_for(pundit_id)
        self.funded = self.key is not None
        if not self.key:
            from eth_utils import keccak
            self.key = "0x" + keccak(bytes.fromhex(DEV_SEED) + pundit_id.encode()).hex()
        self.spent = 0.0
        self.receipts: list[dict[str, Any]] = []

    # ---------------- free endpoints ----------------

    def markets(self, domain: str | None = None) -> list[dict]:
        r = self.http.get(f"{self.base_url}/markets",
                          params={"domain": domain} if domain else None)
        r.raise_for_status()
        return r.json()["markets"]

    def catalogue(self) -> dict:
        r = self.http.get(f"{self.base_url}/catalogue")
        r.raise_for_status()
        return r.json()["informants"]

    # ---------------- the paid path ----------------

    def buy(self, informant_id: str, market_id: str) -> dict[str, Any]:
        url = f"{self.base_url}/informant/{informant_id}"
        params = {"market": market_id}
        first = self.http.get(url, params=params)

        if first.status_code == 404:
            return {"source": informant_id, "ok": False,
                    "error": first.json().get("error", "not found"), "price": 0.0}
        if first.status_code != 402:
            return {"source": informant_id, "ok": False,
                    "error": f"expected 402, got {first.status_code}", "price": 0.0}

        reqs = first.json()
        price = int(reqs["accepts"][0]["amount"]) / 1_000_000
        header = sign_payment(self.key, reqs)
        paid = self.http.get(url, params=params, headers={HEADER: header})

        if paid.status_code != 200:
            return {"source": informant_id, "ok": False, "price": price,
                    "error": f"payment rejected ({paid.status_code}): "
                             f"{paid.json().get('error', paid.text[:120])}"}

        body = paid.json()
        settlement = body.get("settlement", {})
        receipt = {"source": informant_id, "market": market_id, "price": price,
                   "settled": bool(settlement.get("settled")),
                   "tx_hash": settlement.get("tx_hash"),
                   "settlement_error": settlement.get("reason"),
                   "funded_wallet": self.funded}
        self.receipts.append(receipt)
        self.spent += price

        if not body.get("covered"):
            # Paid for, and the informant genuinely has nothing here. That is a
            # real outcome and the agent should learn the coverage gap from it.
            return {"source": informant_id, "ok": True, "covered": False,
                    "payload": None, "price": price, "receipt": receipt}

        return {"source": informant_id, "ok": True, "covered": True,
                "payload": body["probabilities"], "price": price, "receipt": receipt}

    def close(self):
        self.http.close()
