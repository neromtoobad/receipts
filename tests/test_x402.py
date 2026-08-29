"""The 402 gate, against the x402 v2 `exact`/`eip3009` shapes.

Signature verification is the security boundary, so every rejection test must
fail for the reason it names. The forged-signature and swapped-payer cases use a
fresh nonce so they cannot pass or fail for replay reasons instead.
"""
import base64, json, secrets, sys, time
from pathlib import Path

import pytest
from eth_account import Account

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from evidence.x402 import (payment_requirements, sign_payment, verify_payment,
                           PaymentError, to_atomic, NETWORK, USDC, _signable)

PAYEE = Account.create()
PRICE = 0.0120


def reqs(price=PRICE, pay_to=None):
    return payment_requirements("https://receipts.local/informant/island_desk",
                                price, pay_to or PAYEE.address)


def _repack(hdr, *, auth=None, signature=None, accepted=None):
    p = json.loads(base64.b64decode(hdr))
    if auth is not None: p["payload"]["authorization"] = auth
    if signature is not None: p["payload"]["signature"] = signature
    if accepted is not None: p["accepted"] = accepted
    return base64.b64encode(json.dumps(p).encode()).decode()


def test_the_402_body_matches_the_v2_shape():
    r = reqs()
    a = r["accepts"][0]
    assert r["x402Version"] == 2
    assert a["network"] == NETWORK == "eip155:84532"      # CAIP-2, not "base-sepolia"
    assert a["amount"] == str(to_atomic(PRICE))           # `amount`, a string
    assert a["asset"].lower() == USDC.lower()
    assert a["extra"]["assetTransferMethod"] == "eip3009" # inside `extra`


def test_a_valid_payment_is_accepted_and_names_the_payer():
    payer = Account.create()
    v = verify_payment(sign_payment(payer.key.hex(), reqs()), reqs())
    assert v["payer"].lower() == payer.address.lower()
    assert v["value_atomic"] == to_atomic(PRICE)


def test_the_payload_echoes_the_accepted_block():
    """Omit it and the facilitator dies reading `.scheme` of undefined."""
    p = json.loads(base64.b64decode(sign_payment(Account.create().key.hex(), reqs())))
    assert p["accepted"]["scheme"] == "exact"
    assert p["payload"]["authorization"]["value"] == str(to_atomic(PRICE))
    for k in ("value", "validAfter", "validBefore"):
        assert isinstance(p["payload"]["authorization"][k], str), f"{k} must be a string"


def test_a_forged_signature_is_rejected_as_a_signature_problem():
    hdr = sign_payment(Account.create().key.hex(), reqs())
    with pytest.raises(PaymentError) as e:
        verify_payment(_repack(hdr, signature="0x" + "11" * 65), reqs())
    assert "recover" in str(e.value) or "not produced by" in str(e.value)


def test_a_real_signature_over_a_swapped_payer_is_rejected():
    """Sign your own authorization, then claim someone else authorised it."""
    hdr = sign_payment(Account.create().key.hex(), reqs())
    p = json.loads(base64.b64decode(hdr))
    auth = dict(p["payload"]["authorization"])
    auth["from"] = Account.create().address
    with pytest.raises(PaymentError, match="not produced by the stated payer"):
        verify_payment(_repack(hdr, auth=auth), reqs())


def test_replay_is_rejected():
    hdr = sign_payment(Account.create().key.hex(), reqs())
    verify_payment(hdr, reqs())
    with pytest.raises(PaymentError, match="nonce already used"):
        verify_payment(hdr, reqs())


def test_underpayment_is_rejected():
    hdr = sign_payment(Account.create().key.hex(), reqs(price=0.0030))
    with pytest.raises(PaymentError, match="underpaid"):
        verify_payment(hdr, reqs(price=0.0450))


def test_paying_the_wrong_recipient_is_rejected():
    hdr = sign_payment(Account.create().key.hex(), reqs())
    with pytest.raises(PaymentError, match="wrong recipient"):
        verify_payment(hdr, reqs(pay_to=Account.create().address))


def test_an_expired_authorization_is_rejected():
    """Validly signed, genuinely expired. Editing validBefore on a signed
    authorization would be caught as forgery first, which would test the wrong
    thing, so this one is signed over the expired window."""
    payer = Account.create()
    r = reqs()
    now = int(time.time())
    auth = {"from": payer.address, "to": r["accepts"][0]["payTo"],
            "value": r["accepts"][0]["amount"],
            "validAfter": str(now - 600), "validBefore": str(now - 1),
            "nonce": "0x" + secrets.token_hex(32)}
    sig = Account.sign_message(_signable(auth), private_key=payer.key)
    hdr = base64.b64encode(json.dumps({
        "x402Version": 2, "resource": r["resource"], "accepted": r["accepts"][0],
        "payload": {"signature": "0x" + sig.signature.hex().removeprefix("0x"),
                    "authorization": auth}}).encode()).decode()
    with pytest.raises(PaymentError, match="not currently valid"):
        verify_payment(hdr, r)


def test_a_malformed_header_is_rejected_not_crashed():
    with pytest.raises(PaymentError, match="malformed"):
        verify_payment("not-base64-at-all!!", reqs())
