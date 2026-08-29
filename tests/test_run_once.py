"""The agent runtime, tested across a real process boundary.

run_once must be spawned as a SUBPROCESS here. Importing and calling it would
test a function; the thesis is about a process that dies, so the test kills one.
"""
import os, socket, subprocess, sys, threading, time
from pathlib import Path

import pytest
import uvicorn

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from agent.memory import Memory, MEMORY_DIR


def _free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="module")
def service():
    os.environ["EVIDENCE_SETTLE"] = "0"      # no facilitator round trips in tests
    from evidence.app import app
    port = _free_port()
    cfg = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="error")
    server = uvicorn.Server(cfg)
    t = threading.Thread(target=server.run, daemon=True)
    t.start()
    for _ in range(100):
        if server.started:
            break
        time.sleep(0.05)
    yield f"http://127.0.0.1:{port}"
    server.should_exit = True
    t.join(timeout=5)


def _wipe(pundit):
    for suffix in ("", "-wal", "-shm", "-journal"):
        Path(str(MEMORY_DIR / f"{pundit}.db") + suffix).unlink(missing_ok=True)


def _run(pundit, service, *extra):
    return subprocess.run(
        [sys.executable, "-m", "agent.run_once", "--agent", pundit, "--pick",
         "--offline", "--quiet", "--evidence-url", service, *extra],
        capture_output=True, text=True, cwd=ROOT,
        env={**os.environ, "EVIDENCE_SETTLE": "0"})


def test_a_forecast_runs_and_the_process_exits_zero(service):
    _wipe("t_run")
    r = _run("t_run", service, "--domain", "epl")
    assert r.returncode == 0, r.stderr


def test_what_survives_the_boundary_is_only_what_was_written(service):
    """A separate interpreter reads back the forecast the dead one produced."""
    _wipe("t_boundary")
    assert _run("t_boundary", service, "--domain", "epl").returncode == 0
    mem = Memory("t_boundary")                     # this process never met the last one
    events = mem.recent_events(limit=20)
    kinds = [(e.get("extra") or {}).get("kind") for e in events]
    assert "forecast" in kinds
    fc = next(e for e in events if (e.get("extra") or {}).get("kind") == "forecast")
    probs = fc["extra"]["probabilities"]
    assert set(probs) == {"H", "D", "A"}
    assert abs(sum(probs.values()) - 1.0) < 0.01
    assert kinds.count("consultation") == len(fc["extra"]["sources"])


def test_every_purchase_is_journalled_with_its_price(service):
    _wipe("t_receipts")
    assert _run("t_receipts", service, "--domain", "epl").returncode == 0
    mem = Memory("t_receipts")
    buys = [e["extra"] for e in mem.recent_events(limit=20)
            if (e.get("extra") or {}).get("kind") == "consultation"]
    assert buys, "no consultations journalled"
    assert all(b["cost"] > 0 for b in buys)
    assert all(b["trust"] is None for b in buys), "nothing is proven on a first boot"


def test_spend_never_exceeds_the_budget(service):
    _wipe("t_budget")
    assert _run("t_budget", service, "--domain", "epl", "--budget", "0.02").returncode == 0
    mem = Memory("t_budget")
    fc = next(e["extra"] for e in mem.recent_events(limit=20)
              if (e.get("extra") or {}).get("kind") == "forecast")
    assert fc["spend"] <= 0.02 + 1e-9


def test_two_runs_leave_two_forecasts_and_no_shared_state(service):
    _wipe("t_twice")
    for _ in range(2):
        assert _run("t_twice", service, "--domain", "epl").returncode == 0
    mem = Memory("t_twice")
    forecasts = [e for e in mem.recent_events(limit=40)
                 if (e.get("extra") or {}).get("kind") == "forecast"]
    assert len(forecasts) == 2


def test_a_crypto_market_uses_the_crypto_outcomes(service):
    _wipe("t_crypto")
    assert _run("t_crypto", service, "--domain", "crypto_1h").returncode == 0
    mem = Memory("t_crypto")
    fc = next(e["extra"] for e in mem.recent_events(limit=20)
              if (e.get("extra") or {}).get("kind") == "forecast")
    assert set(fc["probabilities"]) == {"UP", "DOWN"}
    assert "sharp_desk" not in fc["sources"], "a football desk cannot answer on crypto"
