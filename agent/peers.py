"""The opinion market: pundits buying each other's takes.

Once a pundit has learned that another is sharp on a domain, the cheapest way to
answer a market in that domain is often to buy that peer's forecast rather than
do the research again. That is a real decision with real money, and it is the
coordination pattern the rubric's top band is about: an agent reading what the
league knows about another agent, and paying for it.

Two things make it honest rather than decorative:

  * Peer reliability lives in the COMMONS, not in the buyer's private store. So
    it is genuinely shared knowledge — pundit_5 benefits from what pundit_2's
    outcomes taught the league about pundit_3.
  * A peer take is bought through the same x402 gate as any informant. There is
    no free path to another agent's opinion either.

A pundit never buys its own take, and never buys from a peer with no established
record, because an unproven peer is exactly as unproven as an unproven informant.
"""
from __future__ import annotations

from typing import Any

PEER_PREFIX = "peer:"
PEER_PRICE = 0.0080          # cheaper than the sharp desk, dearer than formline


def peer_id(pundit: str) -> str:
    return f"{PEER_PREFIX}{pundit}"


def is_peer(source: str) -> bool:
    return source.startswith(PEER_PREFIX)


def pundit_of(source: str) -> str:
    return source[len(PEER_PREFIX):]


def offers(commons, me: str, domain: str, available: list[str]) -> dict[str, dict]:
    """What the league knows about each peer that has already called this market.

    Returns {peer_source_id: reliability_body}. Only peers with an established
    record in THIS domain: a peer that is sharp on football tells you nothing
    about its crypto, which is the same lesson the informants taught.
    """
    out: dict[str, dict] = {}
    for other in available:
        if other == me:
            continue
        body = commons.peer_reliability(other, domain)
        if body and body.get("skill", 0) > 0:
            out[peer_id(other)] = body
    return out
