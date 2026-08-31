"""What to buy, decided from what this pundit remembers.

This is the file the gate rests on. Delete the memory layer and `select()` has
nothing to rank with, so it falls back to buying whatever the budget allows, in
no particular order, which is exactly what an agent with no experience would do.

Three rules, all of them learned from the corpus rather than assumed:

  1. **Never pay for noise.** A source whose measured skill is at or below zero
     is worse than knowing only how often each outcome happens. Measured
     2026-08-29: chalk_desk is negative in all six leagues, and in crypto every
     single informant is. In those domains the correct spend is nothing.

  2. **Stop when the next one adds nothing.** Buying a second source that says
     roughly what the first said costs money and moves the forecast very little.
     The stopping rule is what memory actually buys you; an amnesiac has no basis
     for one, so it spends its whole budget every time.

  3. **Keep a little back for learning.** A source is only proven by being paid
     for, so a slice of the budget goes to the least-tried candidate. Without
     this the agent locks onto whatever it happened to try first and never
     discovers a cheaper source that would have done.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Any

MIN_SKILL = 0.005        # below this a source is noise and must not be paid for
MARGINAL_GAIN = 0.01     # a new source must beat what we hold by this to be worth money
EXPLORE_FRACTION = 0.25  # of the budget, on unproven sources, once a domain is known
EXPLORE_FRACTION_COLD = 0.60   # while a domain is still mostly unknown
KNOWN_ENOUGH = 3         # established sources after which a domain counts as known

ARMS = ("sibyl", "flat", "amnesiac")


class Choice:
    def __init__(self, source: str, price: float, trust: float | None,
                 skill: float | None, reason: str):
        self.source, self.price, self.trust = source, price, trust
        self.skill, self.reason = skill, reason

    def as_dict(self) -> dict[str, Any]:
        return {"source": self.source, "price": self.price, "trust": self.trust,
                "skill": self.skill, "reason": self.reason}

    def __repr__(self):
        return f"Choice({self.source}, {self.price:.4f}, {self.reason})"


def _global_view(mem) -> dict[str, dict]:
    """One reliability figure per source across every domain.

    This is the flat-log arm: it remembers, but it cannot tell domains apart. It
    is in the benchmark to stop a judge concluding that any old file would have
    done the job.
    """
    agg: dict[str, dict] = defaultdict(lambda: {"n": 0, "skill_n": 0.0})
    for body in mem.all_reliability():
        a = agg[body["source"]]
        a["n"] += body.get("n", 0)
        a["skill_n"] += body.get("skill", 0.0) * body.get("n", 0)
    out = {}
    for src, a in agg.items():
        if a["n"]:
            skill = a["skill_n"] / a["n"]
            out[src] = {"source": src, "n": a["n"], "skill": skill,
                        "trust": max(0.0, min(skill / 0.12, 1.0))}
    return out


def select(mem, domain: str, candidates: dict[str, float], budget: float,
           arm: str = "sibyl", peer_beliefs: dict[str, dict] | None = None) -> list[Choice]:
    """candidates: {source_id: price}. Returns what to buy, in order.

    peer_beliefs carries reliability for other pundits, read from the COMMONS
    rather than this pundit's private store. That is the coordination: what the
    league learned about pundit_3 from pundit_3's own resolved calls is what
    pundit_5 uses to decide whether pundit_3's take is worth buying.
    """
    if arm not in ARMS:
        raise ValueError(f"unknown arm {arm!r}")

    if arm == "amnesiac":
        # No memory, so no ranking and no stopping rule. Spend until it cannot.
        chosen, spent = [], 0.0
        for src in sorted(candidates):
            price = candidates[src]
            if spent + price <= budget:
                chosen.append(Choice(src, price, None, None, "no basis to choose"))
                spent += price
        return chosen

    if arm == "sibyl":
        known = {s: mem.get_reliability(s, domain) for s in candidates}
    else:
        view = _global_view(mem)          # once per call, not once per candidate
        known = {s: view.get(s) for s in candidates}

    # A peer's record is shared knowledge, so it overlays the private one. The
    # amnesiac arm gets none of it, which is the point: without memory there is
    # no way to know which peer is worth hearing from either.
    if peer_beliefs and arm != "amnesiac":
        for src, body in peer_beliefs.items():
            if src in candidates and not known.get(src):
                known[src] = body

    ranked, unproven = [], []
    for src, price in candidates.items():
        body = known.get(src)
        if not body:
            unproven.append((price, src))
            continue
        skill = body.get("skill", 0.0)
        if skill < MIN_SKILL:
            continue                       # measured noise. not worth any price.
        ranked.append((skill / price, skill, src, price, body.get("trust")))
    ranked.sort(reverse=True)

    chosen, spent, best = [], 0.0, 0.0
    for _vpd, skill, src, price, trust in ranked:
        if spent + price > budget:
            continue
        if chosen and skill <= best + MARGINAL_GAIN:
            continue                       # says what we already paid to hear
        chosen.append(Choice(src, price, trust, skill,
                             f"skill {skill:+.3f} at {price:.4f}"))
        spent += price
        best = max(best, skill)

    # Whatever is left, up to the exploration slice, goes on the least-tried
    # candidates. A source can only prove itself by being bought, and a domain
    # with eight sources cannot be learned one purchase at a time: explore harder
    # while a domain is cold, then taper once enough of it is established.
    established = sum(1 for b in known.values() if b)
    fraction = EXPLORE_FRACTION if established >= KNOWN_ENOUGH else EXPLORE_FRACTION_COLD
    explore_cap = min(budget * fraction, budget - spent)
    if unproven and explore_cap > 0:
        unproven.sort()
        for price, src in unproven:
            if price > explore_cap:
                continue
            chosen.append(Choice(src, price, None, None, "unproven, exploring"))
            spent += price
            explore_cap -= price

    return chosen


def explain(choices: list[Choice], candidates: dict[str, float], budget: float) -> str:
    spent = sum(c.price for c in choices)
    skipped = len(candidates) - len(choices)
    return (f"bought {len(choices)} of {len(candidates)} for {spent:.4f} "
            f"of {budget:.4f} budget, skipped {skipped}")
