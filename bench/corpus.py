"""The replay corpus: resolved events in the shape the runtime uses.

Both families in one chronological stream, so an arm walking it experiences the
same interleaving of football and crypto a live league would.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "corpus"))

from build import add_prior_form, load as load_football          # noqa: E402
import crypto as C                                               # noqa: E402
from evidence.signals import outcomes_for                        # noqa: E402

FIT_SEASON = "2324"


def load_replay() -> tuple[list[dict], list[dict], list[dict]]:
    """(football_fit, crypto_fit, replay_events).

    The fit split calibrates the informants. The replay split is what the arms
    are measured on, and no arm has ever seen it.
    """
    fb = [r for r in add_prior_form(load_football()) if r["ready"]]
    fb_fit = [r for r in fb if r["season"] == FIT_SEASON]
    fb_test = [r for r in fb if r["season"] != FIT_SEASON]

    cr = C.load_events()
    cut = int(len(cr) * 0.6)
    cr_fit, cr_test = cr[:cut], cr[cut:]

    events = []
    for r in fb_test:
        events.append({**r, "id": f"{r['domain']}:{r['date']:%Y-%m-%d}:{r['home']}:{r['away']}",
                       "question": f"{r['home']} v {r['away']}, full time result",
                       "outcomes": list(outcomes_for(r["domain"])),
                       "sort": r["date"].timestamp()})
    for r in cr_test:
        events.append({**r, "id": f"{r['domain']}:{r['sym']}:{r['ts']}",
                       "question": f"{r['sym']} direction over {r['domain'][7:]}",
                       "outcomes": list(outcomes_for(r["domain"])),
                       "sort": r["ts"] / 1000.0})
    events.sort(key=lambda e: e["sort"])
    return fb_fit, cr_fit, events
