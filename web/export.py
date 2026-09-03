"""Export the league to JSON, including how it got here.

The static page only ever had a snapshot, which is why it was dead. The whole
story of this project is a trust map CHANGING — an agent discovering, over days
and real money, which informants are worth listening to. That needs a timeline,
not a current state.

So this replays each pundit's journal in order and records what it believed at
every step. The UI can then scrub through it and you watch the map fill in.
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from agent.memory import (PROMOTE_N, SKILL_FULL_TRUST, SKILL_SHRINK, TRUST_SHRINK,
                          Memory, shrunk_skill)
from evidence.catalogue import CATALOGUE
from evidence.signals import CRYPTO_DOMAINS, FOOTBALL_DOMAINS

DOMAINS = list(FOOTBALL_DOMAINS) + list(CRYPTO_DOMAINS)
SKIP = {"commons"}
TEST_PREFIXES = ("t_", "s_", "p_", "arm_", "bench_", "probe", "scratch", "demo", "pundit_preview")


def pundit_ids() -> list[str]:
    return sorted(p.stem for p in (ROOT / "memory").glob("*.db")
                  if p.stem not in SKIP and not p.stem.startswith(TEST_PREFIXES))


def trust_of(skill: float, n: int) -> float:
    """Same shape as agent/memory.py, minus staleness, so the timeline shows what
    was believed at the time rather than what it decays to later."""
    if skill <= 0:
        return 0.0
    return round(min(skill / SKILL_FULL_TRUST, 1.0) * (n / (n + TRUST_SHRINK)), 4)


def replay(pid: str) -> dict:
    """Walk the journal forward and record the belief state after every step."""
    mem = Memory(pid)
    events = sorted(mem.recent_events(limit=2000), key=lambda e: e.get("ts") or "")

    running: dict[str, dict] = {}          # "source|domain" -> accumulating record
    frames: list[dict] = []                # one per resolution: what changed, and to what
    said: dict[str, dict[str, dict]] = defaultdict(dict)   # market -> source -> probabilities
    base_brier: dict[str, float] = {}
    feed: list[dict] = []
    spend = 0.0
    forecasts = resolutions = 0

    def brier(probs, actual):
        return sum((p - (1.0 if o == actual else 0.0)) ** 2 for o, p in probs.items())

    for e in events:
        x = e.get("extra") or {}
        kind = x.get("kind")
        ts = e.get("ts") or ""

        if kind == "consultation":
            spend += float(x.get("cost") or 0)
            if x.get("said"):
                said[x["market"]][x["source"]] = x["said"]
            feed.append({"ts": ts, "kind": "buy", "source": x.get("source"),
                         "domain": x.get("domain"), "cost": x.get("cost"),
                         "trust": x.get("trust"), "market": x.get("market")})
        elif kind == "forecast":
            forecasts += 1
            feed.append({"ts": ts, "kind": "forecast", "domain": x.get("domain"),
                         "market": x.get("market"), "probabilities": x.get("probabilities"),
                         "confidence": x.get("confidence"), "reasoning": x.get("reasoning"),
                         "leaned_on": x.get("leaned_on") or [], "spend": x.get("spend")})
        elif kind == "resolution":
            resolutions += 1
            market, domain, outcome = x.get("market"), x.get("domain"), x.get("outcome")
            feed.append({"ts": ts, "kind": "resolved", "market": market,
                         "domain": domain, "outcome": outcome,
                         "brier": x.get("brier"), "sources": x.get("sources") or []})

            # Replay the belief update this resolution caused. This is the whole
            # story of the project: not what it believes now, but when it changed
            # its mind and what changed it.
            changed = {}
            bb = base_brier.setdefault(domain, 0.5 if str(domain).startswith("crypto") else 0.6487)
            for src, probs in said.get(market, {}).items():
                if not outcome or outcome not in probs:
                    continue
                key = f"{src}|{domain}"
                rec = running.setdefault(key, {"n": 0, "sum": 0.0})
                rec["n"] += 1
                rec["sum"] += brier(probs, outcome)
                mean = rec["sum"] / rec["n"]
                skill = round(1 - mean / bb, 4) if bb else 0.0
                changed[key] = {
                    "source": src, "domain": domain, "n": rec["n"], "skill": skill,
                    "skill_shrunk": shrunk_skill(skill, rec["n"]),
                    "trust": trust_of(skill, rec["n"]),
                    "state": "established" if rec["n"] >= PROMOTE_N else "provisional",
                }
            if changed:
                frames.append({"ts": ts, "market": market, "domain": domain,
                               "outcome": outcome, "changed": changed})
        elif kind == "promotion":
            feed.append({"ts": ts, "kind": "promotion", "source": x.get("source"),
                         "domain": x.get("domain"), "skill": x.get("skill")})
        elif kind == "archive":
            feed.append({"ts": ts, "kind": "archive", "source": x.get("source"),
                         "domain": x.get("domain")})

    # Current belief, read straight from memory, is the authoritative last frame.
    cells = {}
    for b in mem.all_reliability_including_archived():
        cells[f"{b['source']}|{b['domain']}"] = {
            "source": b["source"], "domain": b["domain"], "n": b.get("n", 0),
            "skill": b.get("skill"), "skill_shrunk": b.get("skill_shrunk"),
            "trust": b.get("trust"),
            "spend": round(b.get("spend_total", 0.0), 4), "misses": b.get("misses", 0),
            "state": "archived" if b.get("archived") else "established",
            "last_seen": b.get("last_seen"),
        }
    for b in mem.provisional_sources():
        k = f"{b['source']}|{b['domain']}"
        cells.setdefault(k, {
            "source": b["source"], "domain": b["domain"], "n": b.get("n", 0),
            "skill": b.get("skill"), "trust": None,
            "spend": round(b.get("spend_total", 0.0), 4), "misses": b.get("misses", 0),
            "state": "provisional", "last_seen": b.get("last_seen"),
        })

    briers = [f["brier"] for f in feed if f["kind"] == "resolved" and f.get("brier") is not None]
    cap = mem.capacity()
    return {
        "id": pid, "forecasts": forecasts, "resolutions": resolutions,
        "spend": round(spend, 4), "buys": sum(1 for f in feed if f["kind"] == "buy"),
        "brier": round(sum(briers) / len(briers), 4) if briers else None,
        "cells": cells, "feed": feed[-300:], "frames": frames,
        "memory_pct": round(cap.get("pct_used", 0) * 100, 3),
    }


def build() -> dict:
    ps = [replay(p) for p in pundit_ids()]
    feed = sorted((dict(f, pundit=p["id"]) for p in ps for f in p["feed"]),
                  key=lambda f: f["ts"], reverse=True)[:400]
    return {
        "generated": datetime.now(timezone.utc).isoformat(),
        "domains": DOMAINS,
        "catalogue": {k: {"name": v["name"], "blurb": v["blurb"],
                          "price": v["price_usdc"], "answers_on": v["answers_on"]}
                      for k, v in CATALOGUE.items()},
        "constants": {"promote_n": PROMOTE_N, "skill_full_trust": SKILL_FULL_TRUST,
                      "trust_shrink": TRUST_SHRINK, "skill_shrink": SKILL_SHRINK},
        "pundits": [{**p, "feed": p["feed"][-80:]} for p in ps],
        "feed": feed,
        "totals": {
            "forecasts": sum(p["forecasts"] for p in ps),
            "resolutions": sum(p["resolutions"] for p in ps),
            "spend": round(sum(p["spend"] for p in ps), 4),
            "buys": sum(p["buys"] for p in ps),
        },
    }


if __name__ == "__main__":
    out = ROOT / "web" / "data" / "league.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    data = build()
    out.write_text(json.dumps(data, indent=1))
    print(f"wrote {out.relative_to(ROOT)} ({out.stat().st_size:,} bytes)")
    print(f"  {len(data['pundits'])} pundits, {data['totals']['forecasts']} forecasts, "
          f"{data['totals']['resolutions']} resolved, {len(data['feed'])} feed events")
