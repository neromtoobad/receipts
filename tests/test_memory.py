"""The gate, as a test that runs on every commit.

If any of these fail the project's thesis is broken, so they are not optional
and they are not slow.
"""
import subprocess, sys, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from agent.memory import Memory, Commons, tenant_for, PROMOTE_N, MEMORY_DIR


def _fresh(name):
    p = MEMORY_DIR / f"{name}.db"
    for suffix in ("", "-wal", "-shm", "-journal"):
        Path(str(p) + suffix).unlink(missing_ok=True)
    return Memory(name)


def test_cross_process_persistence():
    """Two separate interpreters. Nothing shared but the file on disk."""
    for suffix in ("", "-wal", "-shm", "-journal"):
        Path(str(MEMORY_DIR / "probe.db") + suffix).unlink(missing_ok=True)
    a = subprocess.run([sys.executable, str(ROOT / "scripts/probe_write.py")],
                       capture_output=True, text=True, cwd=ROOT)
    assert a.returncode == 0, a.stderr
    b = subprocess.run([sys.executable, str(ROOT / "scripts/probe_read.py")],
                       capture_output=True, text=True, cwd=ROOT)
    assert b.returncode == 0, b.stderr
    assert "island_desk:epl" in b.stdout
    assert "buy island_desk" in b.stdout


def test_tenants_are_isolated():
    """Two pundits must never see each other's private beliefs."""
    one, two = _fresh("t_one"), _fresh("t_two")
    assert tenant_for("t_one") != tenant_for("t_two")
    for _ in range(PROMOTE_N):
        one.observe("sharp_desk", "epl", 0.55, 0.667, 0.045)
    assert one.get_reliability("sharp_desk", "epl") is not None
    assert two.get_reliability("sharp_desk", "epl") is None


def test_promotion_happens_at_the_threshold():
    """Under PROMOTE_N a source is provisional and must not read as trusted."""
    m = _fresh("t_promote")
    for i in range(PROMOTE_N - 1):
        m.observe("boot_room", "bundesliga", 0.56, 0.667, 0.012)
        assert m.get_reliability("boot_room", "bundesliga") is None, "promoted too early"
        assert m.get_provisional("boot_room", "bundesliga")["n"] == i + 1
    m.observe("boot_room", "bundesliga", 0.56, 0.667, 0.012)
    body = m.get_reliability("boot_room", "bundesliga")
    assert body is not None and body["status"] == "established"
    assert body["n"] == PROMOTE_N and body["skill"] > 0


def test_worthless_source_earns_zero_trust():
    """chalk_desk scored negative skill in all six leagues. It must never be
    weighted, however many times it is observed."""
    m = _fresh("t_chalk")
    for _ in range(20):
        m.observe("chalk_desk", "epl", 0.67, 0.667, 0.020)
    assert m.get_reliability("chalk_desk", "epl")["trust"] == 0.0


def test_archive_is_recoverable():
    """archive != delete, shown rather than asserted."""
    m = _fresh("t_archive")
    for _ in range(PROMOTE_N):
        m.observe("hexagon_desk", "ligue1", 0.56, 0.667, 0.012)
    m.c.set_entity("source_reliability", "hexagon_desk:ligue1",
                   {**m.get_reliability("hexagon_desk", "ligue1"),
                    "last_seen": "2020-01-01T00:00:00+00:00"})
    assert m.sweep_stale() == ["hexagon_desk:ligue1"]
    assert m.get_reliability("hexagon_desk", "ligue1") is None
    assert any(r["name"] == "hexagon_desk:ligue1" for r in m.list_archived())
    assert m.restore("hexagon_desk", "ligue1") is not None
    assert m.get_reliability("hexagon_desk", "ligue1") is not None


def test_commons_is_shared_not_private():
    """The opinion market needs one store every pundit can read."""
    c1, c2 = Commons(), Commons()
    for _ in range(PROMOTE_N):
        c1.rate_peer("pundit_3", "epl", 0.55, 0.667)
    assert c2.peer_reliability("pundit_3", "epl")["n"] >= PROMOTE_N
