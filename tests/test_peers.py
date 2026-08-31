"""The opinion market: one pundit buying another's take.

The coordination claim rests on these. Peer reliability must come from the
COMMONS — shared knowledge — and must be domain-scoped like everything else, or
it is just recall wearing a coordination costume.
"""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from agent.memory import Commons, Memory, MEMORY_DIR, PROMOTE_N
from agent.peers import PEER_PRICE, is_peer, offers, peer_id, pundit_of
from agent.sources import select

FOOTBALL_BASE = 0.6487
PRICES = {"island_desk": 0.012, "chalk_desk": 0.020, "formline": 0.003}


def _wipe(name):
    for s in ("", "-wal", "-shm", "-journal"):
        Path(str(MEMORY_DIR / f"{name}.db") + s).unlink(missing_ok=True)
    return Memory(name)


def _teach_peer(commons, agent, domain, skill, times=PROMOTE_N):
    for _ in range(times):
        commons.rate_peer(agent, domain, FOOTBALL_BASE * (1 - skill), FOOTBALL_BASE)


def test_ids_round_trip():
    assert is_peer(peer_id("pundit_3")) and pundit_of(peer_id("pundit_3")) == "pundit_3"
    assert not is_peer("island_desk")


def test_a_peer_is_only_offered_once_the_league_rates_it():
    _wipe("commons"); c = Commons()
    roster = ["pundit_1", "pundit_3"]
    assert offers(c, "pundit_1", "epl", roster) == {}, "unproven peers are not on the shelf"
    _teach_peer(c, "pundit_3", "epl", 0.09)
    got = offers(c, "pundit_1", "epl", roster)
    assert peer_id("pundit_3") in got


def test_a_pundit_never_buys_its_own_take():
    _wipe("commons"); c = Commons()
    _teach_peer(c, "pundit_1", "epl", 0.09)
    assert peer_id("pundit_1") not in offers(c, "pundit_1", "epl", ["pundit_1", "pundit_3"])


def test_peer_standing_is_domain_scoped():
    """Sharp on football says nothing about crypto. Same lesson as the informants."""
    _wipe("commons"); c = Commons()
    _teach_peer(c, "pundit_3", "epl", 0.09)
    assert peer_id("pundit_3") in offers(c, "pundit_3" and "pundit_1", "epl", ["pundit_1", "pundit_3"])
    assert offers(c, "pundit_1", "crypto_1h", ["pundit_1", "pundit_3"]) == {}


def test_a_rated_peer_can_beat_an_informant_on_value():
    """The whole point: if the league says a peer is sharp here, buying its take
    can be better value than researching it again."""
    _wipe("commons"); c = Commons()
    mem = _wipe("p_buyer")
    _teach_peer(c, "pundit_3", "epl", 0.11)
    beliefs = offers(c, "p_buyer", "epl", ["p_buyer", "pundit_3"])
    cands = {**PRICES, peer_id("pundit_3"): PEER_PRICE}
    picked = [ch.source for ch in select(mem, "epl", cands, 0.060, peer_beliefs=beliefs)]
    assert peer_id("pundit_3") in picked


def test_the_amnesiac_cannot_use_the_opinion_market():
    """No memory means no way to know which peer is worth hearing from either."""
    _wipe("commons"); c = Commons()
    mem = _wipe("p_amnesiac")
    _teach_peer(c, "pundit_3", "epl", 0.11)
    beliefs = offers(c, "p_amnesiac", "epl", ["p_amnesiac", "pundit_3"])
    cands = {**PRICES, peer_id("pundit_3"): PEER_PRICE}
    chosen = select(mem, "epl", cands, 0.060, arm="amnesiac", peer_beliefs=beliefs)
    assert all(ch.skill is None for ch in chosen), "amnesiac must not read peer standing"


def test_peer_knowledge_is_shared_not_private():
    """pundit_5 benefits from what pundit_2's outcomes taught the league about
    pundit_3. That is the coordination, and it must not live in one private store."""
    _wipe("commons")
    writer, reader = Commons(), Commons()
    _teach_peer(writer, "pundit_3", "epl", 0.09)
    assert peer_id("pundit_3") in offers(reader, "pundit_5", "epl", ["pundit_3", "pundit_5"])
