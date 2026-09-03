"""What this pundit already knows about these particular teams.

The reliability entities answer "is this informant any good in this domain".
They cannot answer "how have my calls on Man City gone", because they are keyed
by (source, domain) and a team is neither. That question can only be answered by
searching the journal, which is what Sibyl's FTS5 layer is for and what this
module uses it for.

It matters because it is a genuinely different memory dimension. An agent can
know exactly which informants to trust in the Premier League and still have been
repeatedly wrong about one specific side. Nothing in the entity store would tell
it that; the journal does, if you can search it.
"""
from __future__ import annotations

import re
from typing import Any

MIN_CALLS = 2          # below this it is an anecdote, not a record
MAX_HITS = 40


def subjects_of(market_id: str) -> list[str]:
    """The searchable names in a market: the two teams, or the symbol."""
    parts = market_id.split(":")
    if market_id.startswith("crypto_"):
        return [parts[1]] if len(parts) > 1 else []
    return [p for p in parts[2:4] if p]


def own_record(mem, market_id: str) -> dict[str, Any] | None:
    """Search the journal for this pundit's past calls on these subjects.

    Returns None when there is not enough history to say anything honest. A
    record of one is not a record.
    """
    subjects = subjects_of(market_id)
    if not subjects:
        return None

    seen_markets: dict[str, dict] = {}
    for subject in subjects:
        for hit in mem.recall(subject.replace("_", " "), limit=MAX_HITS):
            # A cross-tier hit is {tier, key, body, snippet, ...} and the event
            # payload lives inside body, not at the top level.
            if not isinstance(hit, dict) or hit.get("tier") != "journal":
                continue
            body = hit.get("body") or {}
            x = body.get("extra") or {}
            mid = x.get("market")
            if not mid or mid == market_id:
                continue                      # never let it recall the open call
            kind = x.get("kind")
            if kind == "forecast":
                seen_markets.setdefault(mid, {})["called"] = True
            elif kind == "resolution":
                seen_markets.setdefault(mid, {})["brier"] = x.get("brier")
                seen_markets[mid]["outcome"] = x.get("outcome")

    resolved = [m for m in seen_markets.values() if m.get("brier") is not None]
    if len(resolved) < MIN_CALLS:
        return None

    briers = [m["brier"] for m in resolved]
    return {"subjects": subjects, "calls": len(seen_markets),
            "resolved": len(resolved),
            "brier": round(sum(briers) / len(briers), 4)}


def as_line(record: dict[str, Any] | None, overall_brier: float | None) -> str | None:
    """One sentence the forecaster can actually use, or nothing."""
    if not record:
        return None
    who = " and ".join(s.replace("_", " ") for s in record["subjects"])
    line = (f"You have called {who} {record['calls']} time(s) before; "
            f"{record['resolved']} resolved at a mean Brier of {record['brier']:.3f}")
    if overall_brier:
        delta = record["brier"] - overall_brier
        line += (f", against your overall {overall_brier:.3f} — "
                 f"{'worse' if delta > 0.01 else 'better' if delta < -0.01 else 'in line'} "
                 "than your average here")
    return line + "."
