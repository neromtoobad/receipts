"""Is the league interesting enough to film yet?

The demo video is the gate, and it gets one shot. Filming a trust map that is
mostly empty shows a mechanism; filming one that has diverged shows a result.
These are the conditions that separate the two, checked rather than guessed.
"""
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from agent.memory import PROMOTE_N, Memory            # noqa: E402
from resolver.loop import pundit_ids                  # noqa: E402


def check():
    ps = pundit_ids()
    established, burned, doms, sigs, football_res, total_res = [], [], set(), set(), 0, 0

    for pid in ps:
        m = Memory(pid)
        sig = []
        for b in m.all_reliability_including_archived():
            if b.get("n", 0) >= PROMOTE_N:
                established.append(b)
                doms.add(b["domain"])
                sig.append(f"{b['source']}|{b['domain']}|{'T' if (b.get('skill') or 0) > 0 else 'B'}")
                if (b.get("skill") or 0) <= 0:
                    burned.append(b)
        sigs.add(",".join(sorted(sig)))
        for e in m.recent_events(limit=600):
            x = e.get("extra") or {}
            if x.get("kind") == "resolution":
                total_res += 1
                if not str(x.get("domain", "")).startswith("crypto"):
                    football_res += 1

    football_doms = {d for d in doms if not d.startswith("crypto")}
    tests = [
        ("established cells across the league", len(established), 24),
        ("football domains with a record", len(football_doms), 2),
        ("informants measured worse than the base rate", len(burned), 3),
        ("football resolutions", football_res, 10),
        ("distinct belief profiles (they have diverged)", len(sigs), 2),
    ]
    return tests, total_res


if __name__ == "__main__":
    tests, total = check()
    ready = all(v >= need for _, v, need in tests)
    print(f"{'READY TO FILM' if ready else 'NOT YET'}   ({total} resolutions so far)\n")
    for name, v, need in tests:
        mark = "ok  " if v >= need else "wait"
        print(f"  [{mark}] {name:46} {v:>4} / {need}")
    if not ready:
        print("\n  The trust map is the payoff shot. Filming before it has diverged")
        print("  shows the mechanism working; filming after shows it having worked.")
    raise SystemExit(0 if ready else 1)
