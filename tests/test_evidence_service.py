"""The service, end to end, without a wallet or a network settlement."""
import sys
from pathlib import Path

from eth_account import Account
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from evidence import app as appmod
from evidence.x402 import sign_payment

PAYER = Account.create()
client = TestClient(appmod.app)


def _a_market(domain_prefix=""):
    ms = client.get("/markets").json()["markets"]
    return next(m for m in ms if m["domain"].startswith(domain_prefix))


def test_health_and_catalogue_are_free():
    assert client.get("/health").json()["ok"] is True
    cat = client.get("/catalogue").json()["informants"]
    assert len(cat) == 10
    # the catalogue must never leak a quality claim
    blob = " ".join(v["blurb"].lower() for v in cat.values())
    for banned in ("accurate", "accuracy", "hit rate", "best in", "most reliable", "win rate"):
        assert banned not in blob


def test_evidence_is_402_until_paid():
    m = _a_market()
    r = client.get(f"/informant/island_desk?market={m['id']}")
    assert r.status_code == 402
    body = r.json()
    assert body["x402Version"] == 2
    assert body["accepts"][0]["network"] == "eip155:84532"
    assert body["accepts"][0]["amount"] == "12000"


def test_paying_returns_the_evidence():
    m = _a_market()
    reqs = client.get(f"/informant/island_desk?market={m['id']}").json()
    hdr = sign_payment(PAYER.key.hex(), reqs)
    r = client.get(f"/informant/island_desk?market={m['id']}", headers={"PAYMENT-SIGNATURE": hdr})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["covered"] is True
    probs = body["probabilities"]
    assert set(probs) == {"H", "D", "A"}
    assert abs(sum(probs.values()) - 1.0) < 0.01


def test_a_bad_payment_gets_402_with_a_reason():
    m = _a_market()
    r = client.get(f"/informant/island_desk?market={m['id']}",
                   headers={"PAYMENT-SIGNATURE": "garbage"})
    assert r.status_code == 402 and "error" in r.json()


def test_price_differs_per_informant():
    m = _a_market()
    def price(iid):
        return int(client.get(f"/informant/{iid}?market={m['id']}").json()
                   ["accepts"][0]["amount"])
    assert price("sharp_desk") == 45000
    assert price("formline") == 3000
    assert price("chalk_desk") == 20000   # dear, and measured worthless everywhere


def test_football_informants_do_not_answer_on_crypto():
    """Coverage is a real product property and the agent must be able to learn it."""
    m = _a_market("crypto")
    r = client.get(f"/informant/sharp_desk?market={m['id']}")
    assert r.status_code == 404
    r = client.get(f"/informant/flowdesk?market={m['id']}")
    assert r.status_code == 402
