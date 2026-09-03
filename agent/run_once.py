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
from collections import defaultdict
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agent.env import load as _load_env
from agent import wallet

_load_env()
from agent.buyer import Buyer
from agent.forecast import BENCH_MODEL, LIVE_MODEL, SYSTEM_SHA, forecast
from agent.memory import Commons, Memory
from agent.peers import PEER_PRICE, offers
from agent.recall import as_line, own_record
from agent.sources import ARMS, explain, select
from evidence.catalogue import CATALOGUE, write_reference


def pick_market(buyer: Buyer, domain: str | None, mem) -> dict | None:
    """The next unforecast market, from the domain this pundit knows least about.

    Taking the first open market meant taking football every time, because
    fixtures come first in the list. Football results lag about two days in the
    feed, so nothing resolved, no source earned trust, and the trust map stayed
    empty. Crypto resolves in an hour.

    Balancing by domain also spreads learning across all eight rather than
    over-fitting the one that happens to sort first. Reliability is per-domain,
    so a domain never forecast is a domain never learned.
    """
    open_markets = buyer.markets(domain)
    unseen = [m for m in open_markets if not mem.has_forecast(m["id"])]
    if not unseen:
        return None

    seen = defaultdict(int)
    for e in mem.recent_events(limit=400):
        x = e.get("extra") or {}
        if x.get("kind") == "forecast":
            seen[x.get("domain")] += 1

    by_domain = defaultdict(list)
    for m in unseen:
        by_domain[m["domain"]].append(m)
    thinnest = min(by_domain, key=lambda d: (seen[d], d))
    return by_domain[thinnest][0]


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
    ap.add_argument("--no-peers", action="store_true",
                    help="ignore the opinion market and buy only from informants")
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
        market = pick_market(buyer, a.domain, mem)
    if market is None:
        say(f"[{a.agent}] nothing new to forecast")
        buyer.close()
        return 0        # not a miss: it has simply caught up with the fixture list

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

    # The opinion market. Ask the commons which peers the league rates in this
    # domain, and put their takes on the shelf next to the informants.
    peer_beliefs: dict[str, dict] = {}
    if a.arm != "amnesiac" and not a.no_peers:
        try:
            memory_dir = mem.path.parent
            roster = sorted(f.stem for f in memory_dir.glob("*.db")
                            if f.stem.startswith("pundit_"))
            peer_beliefs = offers(Commons(), a.agent, domain, roster)
            for src in peer_beliefs:
                priced[src] = PEER_PRICE
        except Exception as exc:
            say(f"[{a.agent}] peer lookup unavailable: {exc}")

    choices = select(mem, domain, priced, a.budget, arm=a.arm, peer_beliefs=peer_beliefs)
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
            tag = " (a peer's take)" if ch.source.startswith("peer:") else ""
            say(f"[{a.agent}]   bought {ch.source:14} {got['price']:.4f}  {ch.reason}{tag}")
        else:
            say(f"[{a.agent}]   bought {ch.source:14} {got['price']:.4f} "
                f"but it has no data here")

    # What do I already know about these teams? Only the journal can answer that,
    # and only by searching it: reliability entities are keyed by source and
    # domain, and a team is neither.
    record = None
    if a.arm != "amnesiac":
        try:
            resolved = [e["extra"] for e in mem.recent_events(limit=400)
                        if (e.get("extra") or {}).get("kind") == "resolution"]
            briers = [x["brier"] for x in resolved if x.get("brier") is not None]
            record = as_line(own_record(mem, market["id"]),
                             sum(briers) / len(briers) if briers else None)
            if record:
                say(f"[{a.agent}] recalled: {record}")
        except Exception as exc:
            say(f"[{a.agent}] recall unavailable: {exc}")

    out = forecast(market, base_rate, evidence, model=model, offline=a.offline,
                   record=record)
    mem.mark_forecast(market["id"])
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
