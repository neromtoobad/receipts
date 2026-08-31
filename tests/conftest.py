"""Test-wide setup.

The suite must be deterministic and must not touch a live feed. Live data belongs
in the league, not in a test that a judge will run at an unpredictable moment on
an unpredictable network.
"""
import os
from pathlib import Path

FIXTURES = Path(__file__).resolve().parent / "fixtures"

os.environ["EVIDENCE_MARKETS_FILE"] = str(FIXTURES / "markets.json")
os.environ["RECEIPTS_RESULTS_FILE"] = str(FIXTURES / "football_results.json")
os.environ["EVIDENCE_SETTLE"] = "0"          # no facilitator round trips


def pytest_sessionfinish(session, exitstatus):
    """Tests create pundit databases; they must not linger in the league store
    where the resolver and the dashboard would treat them as real members."""
    from agent.memory import MEMORY_DIR
    for db in MEMORY_DIR.glob("*.db*"):
        if db.stem.startswith(("t_", "s_", "arm_", "bench_")) or db.stem in {"probe", "scratch"}:
            db.unlink(missing_ok=True)
