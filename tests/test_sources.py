"""Source selection: the gate.

Every number these tests lean on is a measured one from proof/DOMAINS.md, so if
the selection logic drifts away from what the corpus says, this fails.
"""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from agent.memory import Memory, MEMORY_DIR, PROMOTE_N
from agent.sources import (EXPLORE_FRACTION, EXPLORE_FRACTION_COLD, KNOWN_ENOUGH,
                           MIN_SKILL, Choice, select)

FOOTBALL_BASE, CRYPTO_BASE = 0.6487, 0.5000
PRICES = {"sharp_desk": 0.045, "island_desk": 0.012, "boot_room": 0.012,
          "chalk_desk": 0.020, "formline": 0.003}
CRYPTO_PRICES = {"flowdesk": 0.015, "voldesk": 0.009, "formline": 0.003,
                 "chalk_desk": 0.020}


def _mem(name):
    for s in ("", "-wal", "-shm", "-journal"):
        Path(str(MEMORY_DIR / f"{name}.db") + s).unlink(missing_ok=True)
    return Memory(name)


def _teach(mem, source, domain, skill, base, price, times=PROMOTE_N):
    """Give a source a measured track record by feeding it resolved observations."""
    brier = base * (1 - skill)
    for _ in range(times):
        mem.observe(source, domain, brier, base, price)


def test_a_worthless_source_is_never_bought_at_any_price():
    """chalk_desk measured negative in all six leagues."""
    m = _mem("s_chalk")
    _teach(m, "chalk_desk", "epl", -0.008, FOOTBALL_BASE, 0.020)
    _teach(m, "island_desk", "epl", 0.089, FOOTBALL_BASE, 0.012)
    picked = [c.source for c in select(m, "epl", PRICES, 0.060)]
    assert "chalk_desk" not in picked
    assert "island_desk" in picked


def test_the_dearer_source_loses_when_it_adds_nothing():
    """sharp_desk and boot_room both score +0.116 in bundesliga. One costs 0.045,
    the other 0.012. Memory is what makes that an easy call."""
    m = _mem("s_price")
    _teach(m, "sharp_desk", "bundesliga", 0.116, FOOTBALL_BASE, 0.045)
    _teach(m, "boot_room", "bundesliga", 0.116, FOOTBALL_BASE, 0.012)
    picked = [c.source for c in select(m, "bundesliga", PRICES, 0.060)]
    assert "boot_room" in picked
    assert "sharp_desk" not in picked


def test_a_domain_where_nothing_works_gets_no_spend():
    """Measured: every crypto informant scores at or below zero. Buying nothing
    is the correct answer, and it is one no global ranking can express."""
    m = _mem("s_crypto")
    for src in ("flowdesk", "voldesk", "formline", "chalk_desk"):
        _teach(m, src, "crypto_1h", -0.001, CRYPTO_BASE, 0.01)
    assert select(m, "crypto_1h", CRYPTO_PRICES, 0.060) == []


def test_the_amnesiac_spends_because_it_has_no_basis_to_stop():
    m = _mem("s_amnesiac")
    _teach(m, "chalk_desk", "epl", -0.008, FOOTBALL_BASE, 0.020)
    learned = select(m, "epl", PRICES, 0.060, arm="sibyl")
    blind = select(m, "epl", PRICES, 0.060, arm="amnesiac")
    assert sum(c.price for c in blind) > sum(c.price for c in learned)
    assert "chalk_desk" in [c.source for c in blind], "no memory means no way to avoid it"


def test_domain_scoping_beats_a_flat_log():
    """formline is worth buying in football and worthless in crypto. A flat log
    sees one positive number and carries it into a domain where it is noise."""
    m = _mem("s_flat")
    _teach(m, "formline", "epl", 0.031, FOOTBALL_BASE, 0.003, times=20)
    _teach(m, "formline", "crypto_1h", -0.007, CRYPTO_BASE, 0.003, times=3)
    scoped = [c.source for c in select(m, "crypto_1h", CRYPTO_PRICES, 0.060, arm="sibyl")]
    flat = [c.source for c in select(m, "crypto_1h", CRYPTO_PRICES, 0.060, arm="flat")]
    assert "formline" not in scoped, "domain-scoped memory knows it is noise here"
    assert "formline" in flat, "the flat log carries football skill into crypto"


def test_budget_is_never_exceeded():
    m = _mem("s_budget")
    for src, sk in (("island_desk", 0.089), ("boot_room", 0.060), ("formline", 0.031)):
        _teach(m, src, "epl", sk, FOOTBALL_BASE, PRICES[src])
    for budget in (0.0, 0.004, 0.013, 0.060):
        chosen = select(m, "epl", PRICES, budget)
        assert sum(c.price for c in chosen) <= budget + 1e-9


def test_an_unproven_source_gets_explored():
    """A source can only prove itself by being bought, so a slice of the budget
    goes to the least-tried candidate."""
    m = _mem("s_explore")
    _teach(m, "island_desk", "epl", 0.089, FOOTBALL_BASE, 0.012)
    chosen = select(m, "epl", PRICES, 0.060)
    assert any(c.reason.startswith("unproven") for c in chosen)


def _explored(chosen):
    return sum(c.price for c in chosen if c.reason.startswith("unproven"))


def test_exploration_is_capped_while_a_domain_is_cold():
    """A domain with eight sources cannot be learned one purchase at a time, so
    a cold domain explores hard. It still must not eat the whole budget."""
    m = _mem("s_explore_cold")
    _teach(m, "island_desk", "epl", 0.089, FOOTBALL_BASE, 0.012)
    chosen = select(m, "epl", PRICES, 0.060)
    assert _explored(chosen) <= 0.060 * EXPLORE_FRACTION_COLD + 1e-9
    assert sum(c.price for c in chosen) <= 0.060 + 1e-9


def test_exploration_tapers_once_a_domain_is_known():
    """Once enough sources are established the agent should be exploiting, not
    still spending most of its budget probing."""
    m = _mem("s_explore_warm")
    for src, sk in (("island_desk", 0.089), ("boot_room", 0.060),
                    ("calcio_desk", 0.044), ("formline", 0.031)):
        _teach(m, src, "epl", sk, FOOTBALL_BASE, PRICES.get(src, 0.012))
    established = len([b for b in
                       (m.get_reliability(s, "epl") for s in PRICES) if b])
    assert established >= KNOWN_ENOUGH
    chosen = select(m, "epl", PRICES, 0.060)
    assert _explored(chosen) <= 0.060 * EXPLORE_FRACTION + 1e-9


def test_no_memory_at_all_still_produces_a_decision():
    """A fresh pundit has never bought anything. It must still be able to act."""
    m = _mem("s_fresh")
    chosen = select(m, "epl", PRICES, 0.060)
    assert chosen, "an agent with no history must still explore"
    assert all(c.skill is None for c in chosen)
