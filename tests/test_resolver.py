"""The resolver, on markets that really happened.

Outcomes come from the live results feed, not from fixtures invented here, so a
green test means the same path that will run in the league works.
"""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from agent.memory import Commons, Memory, MEMORY_DIR, PROMOTE_N
from resolver.loop import base_brier, brier, resolve_pundit
from resolver.outcomes import Outcome, _football_index, resolve


@pytest.fixture(scope="module")
def played():
    """Real fixtures from the current season, already resolved."""
    idx = _football_index()
    epl = [(k, v) for k, v in idx.items() if k.startswith("epl:")]
    if len(epl) < 6:
        pytest.skip("not enough resolved fixtures in the feed yet")
    return epl


def _wipe(name):
    for suffix in ("", "-wal", "-shm", "-journal"):
        Path(str(MEMORY_DIR / f"{name}.db") + suffix).unlink(missing_ok=True)
    return Memory(name)


def _forecast_on(mem, market_id, sources):
    """sources: {id: probabilities-or-None}. None means paid for and got nothing."""
    for sid, said in sources.items():
        mem.log_consultation(market_id, sid, "epl", 0.012, None, payload=said)
    mem.log_forecast(market_id, "epl", {"H": 0.45, "D": 0.25, "A": 0.30}, 0.2,
                     "test", list(sources), list(sources), 0.012 * len(sources))


def test_outcomes_come_back_resolved(played):
    mid, actual = played[0]
    out = resolve(mid)
    assert out.status == Outcome.RESOLVED
    assert out.result == actual


def test_a_good_source_earns_skill_and_a_bad_one_does_not(played):
    """Both are scored against what actually happened, from the same forecasts."""
    mem, commons = _wipe("t_res_skill"), Commons()
    for mid, actual in played[:PROMOTE_N]:
        sharp = {o: (0.80 if o == actual else 0.10) for o in ("H", "D", "A")}
        wrong = {o: (0.05 if o == actual else 0.475) for o in ("H", "D", "A")}
        _forecast_on(mem, mid, {"island_desk": sharp, "chalk_desk": wrong})

    stats = resolve_pundit("t_res_skill", commons, quiet=True)
    assert stats["resolved"] == PROMOTE_N

    good = mem.get_reliability("island_desk", "epl")
    bad = mem.get_reliability("chalk_desk", "epl")
    assert good and bad
    assert good["skill"] > 0.5, good["skill"]
    assert bad["skill"] < 0, bad["skill"]
    assert good["trust"] > 0
    assert bad["trust"] == 0.0, "a source worse than the base rate must never be trusted"


def test_promotion_needs_the_threshold(played):
    mem, commons = _wipe("t_res_promote"), Commons()
    for mid, actual in played[:PROMOTE_N - 1]:
        _forecast_on(mem, mid, {"boot_room": {o: (0.7 if o == actual else 0.15)
                                              for o in ("H", "D", "A")}})
    resolve_pundit("t_res_promote", commons, quiet=True)
    assert mem.get_reliability("boot_room", "epl") is None
    assert mem.get_provisional("boot_room", "epl")["n"] == PROMOTE_N - 1

    mid, actual = played[PROMOTE_N - 1]
    _forecast_on(mem, mid, {"boot_room": {o: (0.7 if o == actual else 0.15)
                                          for o in ("H", "D", "A")}})
    resolve_pundit("t_res_promote", commons, quiet=True)
    body = mem.get_reliability("boot_room", "epl")
    assert body and body["status"] == "established" and body["n"] == PROMOTE_N


def test_a_market_is_never_scored_twice(played):
    mem, commons = _wipe("t_res_once"), Commons()
    mid, actual = played[0]
    _forecast_on(mem, mid, {"formline": {o: (0.6 if o == actual else 0.2)
                                         for o in ("H", "D", "A")}})
    first = resolve_pundit("t_res_once", commons, quiet=True)
    second = resolve_pundit("t_res_once", commons, quiet=True)
    assert first["resolved"] == 1
    assert second["resolved"] == 0, "already-resolved markets must be skipped"
    assert mem.get_provisional("formline", "epl")["n"] == 1


def test_paying_for_nothing_is_recorded_but_does_not_score(played):
    """A source that had no data cost money. That is a miss, not a bad answer."""
    mem, commons = _wipe("t_res_miss"), Commons()
    mid, actual = played[0]
    _forecast_on(mem, mid, {"hexagon_desk": None})
    resolve_pundit("t_res_miss", commons, quiet=True)
    body = mem.get_provisional("hexagon_desk", "epl")
    assert body["misses"] == 1
    assert body["n"] == 0, "a miss must not pollute the brier average"
    assert body["spend_total"] > 0, "but the money was still spent"


def test_the_commons_learns_which_pundit_is_sharp(played):
    commons = Commons()
    mem = _wipe("t_res_peer")
    for mid, actual in played[:PROMOTE_N]:
        _forecast_on(mem, mid, {"island_desk": {o: (0.7 if o == actual else 0.15)
                                                for o in ("H", "D", "A")}})
    resolve_pundit("t_res_peer", commons, quiet=True)
    peer = commons.peer_reliability("t_res_peer", "epl")
    assert peer is not None and peer["n"] == PROMOTE_N


def test_skill_is_measured_against_the_base_rate():
    bb = base_brier("epl")
    assert 0.60 < bb < 0.70
    perfect = brier({"H": 1.0, "D": 0.0, "A": 0.0}, "H")
    assert perfect == 0.0
    assert 1 - perfect / bb == 1.0
