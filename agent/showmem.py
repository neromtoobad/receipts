"""Show what a pundit has actually learned.

Every number here was earned: the agent paid for that source, recorded what it
said, and scored it when the market resolved. Nothing is seeded and nothing is
configured. Run it against any pundit to see the trust map that decides what
that agent is willing to buy next.

    python -m agent.showmem --agent pundit_5 --top 5
"""
from __future__ import annotations

import argparse

from agent.identity import display, resolve
from agent.memory import Memory


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--agent", required=True)
    ap.add_argument("--top", type=int, default=8)
    ap.add_argument("--domain", default=None)
    ap.add_argument("--brief", action="store_true",
                    help="one line: what a following process would read back")
    a = ap.parse_args()

    a.agent = resolve(a.agent)
    who = display(a.agent)
    mem = Memory(a.agent)
    if a.brief:
        # The smallest honest proof that a write landed. Run it either side of a
        # forecast and the counts move, which is what the next process reads.
        ev = mem.recent_events(limit=2000)
        forecasts = sum(1 for e in ev if (e.get("extra") or {}).get("kind") == "forecast")
        rel = mem.all_reliability_including_archived()
        print(f"  journal: {len(ev)} events, {forecasts} forecasts | "
              f"trust map: {len(rel)} source/domain pairs | "
              f"store {mem.capacity().get('pct_used', 0):.1%}")
        return 0
    rows = [r for r in mem.all_reliability_including_archived()
            if not a.domain or r.get("domain") == a.domain]
    if not rows:
        print(f"  {who} has learned nothing yet.")
        return 0

    # Rank the way the agent itself does: on the shrunk estimate, so a source
    # with three lucky calls does not outrank one measured forty times.
    rows.sort(key=lambda r: -(r.get("skill_shrunk") or 0))
    cap = mem.capacity()

    print(f"  {'source':<18} {'domain':<10} {'n':>3}  {'brier':>6} {'skill':>7} "
          f"{'trust':>6}  {'spent':>7}")
    print(f"  {'-' * 18} {'-' * 10} {'-' * 3}  {'-' * 6} {'-' * 7} {'-' * 6}  {'-' * 7}")
    for r in rows[:a.top]:
        flag = " archived" if r.get("archived") else ""
        print(f"  {r['source']:<18} {r.get('domain', ''):<10} {r.get('n', 0):>3}  "
              f"{r.get('brier_mean', 0):>6.3f} {r.get('skill_shrunk', 0):>7.4f} "
              f"{r.get('trust', 0):>6.4f}  {r.get('spend_total', 0):>7.4f}{flag}")

    established = sum(1 for r in rows if r.get("status") == "established")
    print(f"\n  {len(rows)} source/domain pairs, {established} established, "
          f"{sum(1 for r in rows if r.get('archived'))} archived. "
          f"Store at {cap.get('pct_used', 0):.0%} of the {cap.get('tier')} tier cap.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
