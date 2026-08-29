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
