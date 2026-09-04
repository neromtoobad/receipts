"""The Python roster and the site roster must agree.

Two hardcoded lists of the same six names in two languages is exactly the kind
of thing that drifts silently: someone renames a pundit on the page, the
terminal keeps saying the old name, and the demo video contradicts the website.
This reads the real TypeScript and compares.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

from agent.identity import ROSTER, display, resolve

TS = Path(__file__).resolve().parents[1] / "site" / "lib" / "pundits.ts"


def _roster_from_ts() -> dict[str, str]:
    src = TS.read_text()
    return {m.group(1): m.group(2) for m in
            re.finditer(r"id:\s*'([^']+)'\s*,\s*name:\s*'([^']+)'", src)}


@pytest.mark.skipif(not TS.exists(), reason="site not present")
def test_python_and_site_rosters_match() -> None:
    assert _roster_from_ts() == ROSTER


def test_resolve_accepts_name_or_id() -> None:
    for pid, name in ROSTER.items():
        assert resolve(pid) == pid
        assert resolve(name) == pid
        assert resolve(name.lower()) == pid
        assert display(pid) == name


def test_unrostered_ids_pass_through() -> None:
    # The bench and the test suite use tenants that are not pundits. They must
    # still print something, not blow up or render as None.
    for token in ("bench_sibyl", "t_scratch", "amnesiac"):
        assert resolve(token) == token
        assert display(token) == token
