"""Who the pundits are, on the Python side.

The store ids (`pundit_5`) are load-bearing and must never change: a tenant id
is a uuid5 of the pundit id, the database is named after it, and its wallet is
derived from it. Renaming one would orphan everything it has ever learned.

So the names are a display layer, exactly as they are on the site. This module
is the Python half of that, and `tests/test_identity.py` asserts it agrees with
`site/lib/pundits.ts` so the terminal and the web page can never drift apart.

All six run the same model on the same prompt with the same budget. The names
are labels, not personalities.
"""
from __future__ import annotations

ROSTER: dict[str, str] = {
    "pundit_1": "AUGUR",
    "pundit_2": "CIPHER",
    "pundit_3": "TALLY",
    "pundit_4": "QUORUM",
    "pundit_5": "VERTEX",
    "pundit_6": "LEDGER",
}

_BY_NAME = {name.lower(): pid for pid, name in ROSTER.items()}


def resolve(token: str) -> str:
    """Accept a name or a store id, return the store id.

    Lets the demo and the CLI say `--agent vertex` while everything on disk
    keeps the id it was created with.
    """
    t = token.strip()
    if t in ROSTER:
        return t
    return _BY_NAME.get(t.lower(), t)


def display(pundit_id: str) -> str:
    """The name to show a human. Falls back to the id for anything unrostered,
    which is how the bench and test tenants keep printing something useful."""
    return ROSTER.get(pundit_id, pundit_id)
