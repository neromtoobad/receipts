"""One forecast, then the process dies.

    python -m agent.run_once --agent pundit_3 --pick --domain epl

This never loops and never returns to a caller: it calls exit(0). If any state
survived the process boundary the whole thesis would be dead, so the boundary is
the program's exit, not a function return.

Day 3 buys everything it can afford. It reads reliability from memory and writes
consultations and the forecast back, but it does not yet CHOOSE with what it
reads. That is phase 5, and it is the phase the gate depends on.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agent import wallet
from agent.buyer import Buyer
from agent.forecast import BENCH_MODEL, LIVE_MODEL, SYSTEM_SHA, forecast
from agent.memory import Memory
from agent.sources import ARMS, explain, select
from evidence.catalogue import CATALOGUE, write_reference


def pick_market(buyer: Buyer, domain: str | None) -> dict | None:
    ms = buyer.markets(domain)
    return ms[0] if ms else None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--agent", required=True)
    ap.add_argument("--market")
    ap.add_argument("--pick", action="store_true", help="take the first open market")
    ap.add_argument("--domain")
    ap.add_argument("--budget", type=float, default=0.060)
    ap.add_argument("--model", default=LIVE_MODEL)
    ap.add_argument("--bench-model", action="store_true")
    ap.add_argument("--offline", action="store_true",
                    help="deterministic stand-in forecaster, for plumbing only")
    ap.add_argument("--evidence-url", default=None)
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--arm", choices=ARMS, default="sibyl",
                    help="sibyl: domain-scoped memory. flat: memory with no domain "
                         "scoping. amnesiac: no memory, buys what it can afford.")
    a = ap.parse_args()

    t0 = time.perf_counter()
    model = BENCH_MODEL if a.bench_model else a.model
    say = (lambda *x: None) if a.quiet else print

    mem = Memory(a.agent)
    buyer = Buyer(a.agent, a.evidence_url) if a.evidence_url else Buyer(a.agent)

    # First boot writes the catalogue to REFERENCE. Marketing copy, not quality.
    if not mem.get_reference("informant_catalogue"):
        write_reference(mem)
        say(f"[{a.agent}] first boot: wrote the informant catalogue to REFERENCE")

    market = None
    if a.market:
        market = next((m for m in buyer.markets() if m["id"] == a.market), None)
    elif a.pick:
        market = pick_market(buyer, a.domain)
    if market is None:
        print(f"[{a.agent}] no market to forecast", file=sys.stderr)
        buyer.close()
        return 2

    domain = market["domain"]
    base_rate = market.get("base_rate") or {}
    if not base_rate:
        base_rate = {o: 1.0 / len(market["outcomes"]) for o in market["outcomes"]}

    # Memory is read here even on day 3. Selection does not use it yet, but the
    # working set is what phase 5 will decide from.
    remembered = {r["source"]: r for r in mem.all_reliability(domain)}
    say(f"[{a.agent}] {market['id']}")
    say(f"[{a.agent}] recalled {len(remembered)} established sources for {domain}")

    candidates = [iid for iid, entry in CATALOGUE.items() if domain in entry["answers_on"]]
    mem.set_working_set(market["id"], {
        "domain": domain, "budget": a.budget, "arm": a.arm, "candidates": candidates,
        "remembered": {k: v.get("trust") for k, v in remembered.items()},
        "question": market["question"],
    })

    priced = {iid: CATALOGUE[iid]["price_usdc"] for iid in candidates}
    choices = select(mem, domain, priced, a.budget, arm=a.arm)
    say(f"[{a.agent}] {explain(choices, priced, a.budget)}")
    if not choices:
        say(f"[{a.agent}] nothing here is worth its price. buying nothing.")

    evidence, spent = [], 0.0
    for ch in choices:
        got = buyer.buy(ch.source, market["id"])
        if not got.get("ok"):
            say(f"[{a.agent}]   {ch.source:14} unavailable: {got.get('error')}")
            continue
        spent += got["price"]
        mem.log_consultation(market["id"], ch.source, domain, got["price"], ch.trust,
                             payload=got.get("payload"))
        if got.get("covered"):
            evidence.append({"source": ch.source, "payload": got["payload"],
                             "trust": ch.trust})
            say(f"[{a.agent}]   bought {ch.source:14} {got['price']:.4f}  {ch.reason}")
        else:
            say(f"[{a.agent}]   bought {ch.source:14} {got['price']:.4f} "
                f"but it has no data here")

    out = forecast(market, base_rate, evidence, model=model, offline=a.offline)
    mem.log_forecast(market["id"], domain, out["probabilities"], out["confidence"],
                     out["reasoning"], out["leaned_on"],
                     [e["source"] for e in evidence], spent)

    settled = sum(1 for r in buyer.receipts if r["settled"])
    say(f"[{a.agent}] forecast {json.dumps({k: round(v, 3) for k, v in out['probabilities'].items()})}"
        f" confidence {out['confidence']:.2f}")
    say(f"[{a.agent}] spent {spent:.4f} USDC over {len(buyer.receipts)} calls, "
        f"{settled} settled onchain, wallet {'funded' if buyer.funded else 'UNFUNDED'}")
    say(f"[{a.agent}] {(time.perf_counter() - t0) * 1000:.0f}ms, arm={a.arm}, "
        f"model={out['model']}, prompt={SYSTEM_SHA[:12]}")
    buyer.close()
    return 0


if __name__ == "__main__":
    # exit(), not return. The process boundary is the point.
    raise SystemExit(main())
