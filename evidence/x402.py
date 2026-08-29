"""x402 v2, `exact` scheme, `eip3009` asset transfer method, on Base Sepolia.

Shapes here follow the reference spec at coinbase/x402,
specs/schemes/exact/scheme_exact_evm.md. Four details cost us time on day 2 and
are worth stating plainly, because every one of them fails at runtime rather
than at import:

  1. The header is `PAYMENT-SIGNATURE`. `X-PAYMENT` is the older name and is
     accepted here only as a legacy alias.
  2. `network` is CAIP-2, `eip155:84532`. The friendly string "base-sepolia" is
     rejected with "No facilitator registered".
  3. The payment payload echoes an `accepted` block. Omit it and the facilitator
     dies reading `.scheme` of undefined.
  4. Every numeric is a JSON string: `amount`, `value`, `validAfter`,
     `validBefore`.

The signature path is real cryptography and runs entirely offline, so the whole
loop is testable before the wallet holds a single testnet coin. Only broadcast
needs the facilitator, and the facilitator pays the gas: the agent wallet needs
USDC and no ETH.
"""
from __future__ import annotations

import base64
import json
import os
import secrets
import time
from typing import Any

from eth_account import Account
from eth_account.messages import encode_typed_data

X402_VERSION = 2
CHAIN_ID = 84532
NETWORK = "eip155:84532"
USDC = "0x036CbD53842c5426634e7929541eC2318f3dCF7e"
USDC_DECIMALS = 6
ASSET_TRANSFER_METHOD = "eip3009"
FACILITATOR = os.environ.get("X402_FACILITATOR", "https://x402.org/facilitator")

HEADER = "PAYMENT-SIGNATURE"
LEGACY_HEADER = "X-PAYMENT"

EIP712_DOMAIN = {"name": "USDC", "version": "2", "chainId": CHAIN_ID, "verifyingContract": USDC}
TYPES = {
    "TransferWithAuthorization": [
        {"name": "from", "type": "address"},
        {"name": "to", "type": "address"},
        {"name": "value", "type": "uint256"},
        {"name": "validAfter", "type": "uint256"},
        {"name": "validBefore", "type": "uint256"},
        {"name": "nonce", "type": "bytes32"},
    ]
}


class PaymentError(Exception):
    pass


def to_atomic(usdc: float) -> int:
    return int(round(usdc * 10 ** USDC_DECIMALS))


def accepted_block(price_usdc: float, pay_to: str) -> dict[str, Any]:
    return {
        "scheme": "exact",
        "network": NETWORK,
        "amount": str(to_atomic(price_usdc)),
        "asset": USDC,
        "payTo": pay_to,
        "maxTimeoutSeconds": 60,
        "extra": {"assetTransferMethod": ASSET_TRANSFER_METHOD,
                  "name": EIP712_DOMAIN["name"], "version": EIP712_DOMAIN["version"]},
    }


def payment_requirements(resource: str, price_usdc: float, pay_to: str,
                         description: str = "") -> dict[str, Any]:
    """The body returned with a 402."""
    return {
        "x402Version": X402_VERSION,
        "resource": {"url": resource, "description": description,
                     "mimeType": "application/json"},
        "accepts": [accepted_block(price_usdc, pay_to)],
    }


def _signable(auth: dict[str, Any]):
    return encode_typed_data(EIP712_DOMAIN, TYPES, {
        "from": auth["from"], "to": auth["to"], "value": int(auth["value"]),
        "validAfter": int(auth["validAfter"]), "validBefore": int(auth["validBefore"]),
        "nonce": bytes.fromhex(auth["nonce"][2:]),
    })


# ---------------------------------------------------------------- payer side

def sign_payment(private_key: str, requirements: dict[str, Any]) -> str:
    """Agent side. Returns the value for the PAYMENT-SIGNATURE header."""
    acc = Account.from_key(private_key)
    acc_block = requirements["accepts"][0]
    now = int(time.time())
    auth = {
        "from": acc.address,
        "to": acc_block["payTo"],
        "value": str(acc_block["amount"]),
        "validAfter": str(now - 60),
        "validBefore": str(now + int(acc_block["maxTimeoutSeconds"])),
        "nonce": "0x" + secrets.token_hex(32),
    }
    sig = Account.sign_message(_signable(auth), private_key=private_key)
    payload = {
        "x402Version": X402_VERSION,
        "resource": requirements.get("resource", {}),
        "accepted": acc_block,
        "payload": {"signature": "0x" + sig.signature.hex().removeprefix("0x"),
                    "authorization": auth},
    }
    return base64.b64encode(json.dumps(payload).encode()).decode()


# ---------------------------------------------------------------- payee side

_SEEN_NONCES: set[str] = set()


def verify_payment(header: str, requirements: dict[str, Any]) -> dict[str, Any]:
    """Recover the signer and check the authorization pays for this exact call."""
    try:
        payment = json.loads(base64.b64decode(header))
    except Exception as exc:
        raise PaymentError(f"malformed payment header: {exc}") from exc

    want = requirements["accepts"][0]
    got = payment.get("accepted") or {}
    body = payment.get("payload") or {}
    auth, sig = body.get("authorization"), body.get("signature")
    if not auth or not sig:
        raise PaymentError("payment payload missing authorization or signature")
    if got.get("scheme") != "exact" or got.get("network") != NETWORK:
        raise PaymentError("wrong scheme or network")
    if got.get("asset", "").lower() != USDC.lower():
        raise PaymentError("wrong asset")

    nonce = auth.get("nonce", "")
    if nonce in _SEEN_NONCES:
        raise PaymentError("authorization nonce already used")

    try:
        recovered = Account.recover_message(_signable(auth), signature=sig)
    except Exception as exc:
        raise PaymentError(f"signature does not recover: {exc}") from exc
    if recovered.lower() != auth["from"].lower():
        raise PaymentError("signature was not produced by the stated payer")

    if auth["to"].lower() != want["payTo"].lower():
        raise PaymentError("authorization pays the wrong recipient")
    if int(auth["value"]) < int(want["amount"]):
        raise PaymentError(f"underpaid: authorised {auth['value']}, price {want['amount']}")
    now = int(time.time())
    if not (int(auth["validAfter"]) <= now < int(auth["validBefore"])):
        raise PaymentError("authorization is not currently valid")

    _SEEN_NONCES.add(nonce)
    return {"payer": recovered, "value_atomic": int(auth["value"]),
            "value_usdc": int(auth["value"]) / 10 ** USDC_DECIMALS,
            "nonce": nonce, "payment": payment}


def _facilitator(path: str, verified: dict[str, Any],
                 requirements: dict[str, Any]) -> dict[str, Any]:
    import httpx
    body = {"x402Version": X402_VERSION,
            "paymentPayload": verified["payment"],
            "paymentRequirements": requirements["accepts"][0]}
    try:
        r = httpx.post(f"{FACILITATOR}/{path}", json=body, timeout=30)
        out = r.json() if r.headers.get("content-type", "").startswith("application/json") else {}
        return {"http": r.status_code, "raw": out or r.text[:300]}
    except Exception as exc:
        return {"http": None, "raw": f"{type(exc).__name__}: {exc}"}


def verify_with_facilitator(verified, requirements) -> dict[str, Any]:
    """Ask the facilitator to check balance and simulate the transfer. Cheap, and
    it tells the buyer whether settlement will work before anything is served."""
    out = _facilitator("verify", verified, requirements)
    raw = out["raw"] if isinstance(out["raw"], dict) else {}
    return {"valid": bool(raw.get("isValid")),
            "reason": raw.get("invalidMessage") or raw.get("invalidReason"), **out}


def settle(verified: dict[str, Any], requirements: dict[str, Any]) -> dict[str, Any]:
    """Hand the authorization to the facilitator, which broadcasts and pays gas.

    Returns settled=False with the real reason when it cannot. Nothing in this
    repo ever claims a settlement it has no transaction hash for.
    """
    out = _facilitator("settle", verified, requirements)
    raw = out["raw"] if isinstance(out["raw"], dict) else {}
    return {"settled": bool(raw.get("success")),
            "tx_hash": raw.get("transaction") or None,
            "reason": raw.get("errorMessage") or raw.get("errorReason") or
                      (None if raw else str(out["raw"])[:200]),
            "http": out["http"]}
