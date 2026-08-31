"""The resolver. Turns outcomes into remembered reliability.

    python -m resolver.loop --once

It runs as a separate process from the pundits, reads each pundit's journal for
forecasts it has not yet scored, looks up what actually happened, and writes the
result back to every informant that pundit consulted, scoped to the domain.

This is the only place reliability is ever written. The agent never grades its
own sources during a forecast; it only reads what this process concluded from
outcomes that have already happened.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from agent.memory import Commons, Memory, MEMORY_DIR
from evidence.crypto_source import hourly_closes
from resolver.outcomes import Outcome, resolve, symbol_of

BASE_RATES = json.loads((ROOT / "evidence" / "base_rates.json").read_text())


def brier(probs: dict[str, float], actual: str) -> float:
    return sum((p - (1.0 if o == actual else 0.0)) ** 2 for o, p in probs.items())


def base_brier(domain: str) -> float:
    """How well you do by knowing only how often each outcome happens. Skill is
    measured against this, so a source that beats nothing scores zero."""
    prior = BASE_RATES.get(domain)
    if not prior:
        return 0.667
    return sum(p * brier(prior, o) for o, p in prior.items())


# Test runs leave databases behind in memory/. The resolver must not treat them
# as league members, or a test fixture ends up in the standings.
NOT_A_PUNDIT = ("commons", "probe", "scratch", "demo")
TEST_PREFIXES = ("t_", "s_", "arm_", "bench_")


def pundit_ids() -> list[str]:
    return sorted(p.stem for p in MEMORY_DIR.glob("*.db")
                  if p.stem not in NOT_A_PUNDIT
                  and not p.stem.startswith(TEST_PREFIXES)
                  and not p.stem.startswith("demo"))


def _preload_crypto(market_ids) -> dict[str, dict[int, float]]:
    """One candle window per symbol per run. Resolving each market on its own
    would hit the aggregator's rate limiter once per market."""
    windows: dict[str, dict[int, float]] = {}
    wanted: dict[str, list[int]] = defaultdict(list)
    for mid in market_ids:
        sym = symbol_of(mid)
        if sym:
            try:
                wanted[sym].append(int(mid.split(":")[2]))
            except (ValueError, IndexError):
                pass
    for sym, stamps in wanted.items():
        try:
            closes, _src = hourly_closes(sym, min(stamps) - 3600000,
                                         max(stamps) + 25 * 3600000)
            windows[sym] = closes
        except Exception as exc:
            print(f"  candle window for {sym} unavailable: {exc}", file=sys.stderr)
    return windows


def resolve_pundit(pid: str, commons: Commons, *, limit: int = 500, quiet: bool = False):
    mem = Memory(pid)
    events = mem.recent_events(limit=limit)
    forecasts = [e for e in events if (e.get("extra") or {}).get("kind") == "forecast"]
    said = defaultdict(list)
    for e in events:
        x = e.get("extra") or {}
        if x.get("kind") == "consultation":
            said[x["market"]].append(x)

    pending = [f for f in forecasts if not mem.is_resolved(f["extra"]["market"])]
    windows = _preload_crypto([f["extra"]["market"] for f in pending])

    stats = {"resolved": 0, "pending": 0, "errors": 0, "observations": 0, "misses": 0}
    for f in pending:
        x = f["extra"]
        mid, domain = x["market"], x["domain"]
        out: Outcome = resolve(mid, windows.get(symbol_of(mid) or ""))
        if out.status == Outcome.ERROR:
            stats["errors"] += 1
            print(f"  RESOLVE ERROR {pid} {mid}: {out.reason}", file=sys.stderr)
            continue
        if out.status == Outcome.PENDING:
            stats["pending"] += 1
            continue

        bb = base_brier(domain)
        fb = brier(x["probabilities"], out.result)

        for c in said.get(mid, []):
            if c.get("said"):
                mem.observe(c["source"], domain, brier(c["said"], out.result), bb, c["cost"])
                stats["observations"] += 1
            else:
                mem.observe_miss(c["source"], domain, c["cost"])
                stats["misses"] += 1

        commons.rate_peer(pid, domain, fb, bb)
        mem.mark_resolved(mid, {"outcome": out.result, "brier": round(fb, 4),
                                "skill": round(1 - fb / bb, 4) if bb else 0.0})
        mem.log_event(
            evaluated=[f"{mid} resolved {out.result}"],
            extra={"kind": "resolution", "market": mid, "domain": domain,
                   "outcome": out.result, "brier": round(fb, 4),
                   "sources": [c["source"] for c in said.get(mid, [])]})
        stats["resolved"] += 1
        if not quiet:
            print(f"  {mid[:46]:46} -> {out.result:4} brier {fb:.3f}")

    archived = mem.sweep_stale()
    if archived and not quiet:
        print(f"  archived after silence: {', '.join(archived)}")
    return stats


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--once", action="store_true", default=True)
    ap.add_argument("--pundit", action="append")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()

    commons = Commons()
    total = defaultdict(int)
    for pid in (a.pundit or pundit_ids()):
        if not a.quiet:
            print(f"[{pid}]")
        s = resolve_pundit(pid, commons, quiet=a.quiet)
        for k, v in s.items():
            total[k] += v

    print(f"resolved {total['resolved']}, pending {total['pending']}, "
          f"errors {total['errors']}, source observations {total['observations']}, "
          f"paid-but-empty {total['misses']}")
    return 1 if total["errors"] and not total["resolved"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
