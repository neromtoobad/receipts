# The "what I built, and why it is different" post

Every figure here is read off the board as published on 2026-09-09 07:55Z:
1,166 calls · 805 resolved · 2,010 informants bought · 18.50 USDC spent ·
spread 0.0525 Brier · per-seat spend 0.0145 to 0.0190 a call · all six rate
`hexagon_desk` best, in three different leagues. The deletion-test figures and
the hashes are on the proof page.

**Handles:** `@sibylcap` verified. `@base` safe. **Virtuals handle STILL
UNVERIFIED** — the ACP line names job 75820 and tags nobody.

---

## X / Twitter — the post (memory-first, two paragraphs)

Every forecast in RECEIPTS runs in its own process and calls exit(0) when it is
done. Nothing survives that — no context window, no globals, no warm cache —
except what the agent wrote to @sibylcap Memory, and that is one file,
`agent/memory.py`, using all five tiers. HOT `set_state` holds sources paid for
but not yet proven. WARM `set_entity` holds reliability per informant AND per
domain, which is the map. COLD `write_event` is every purchase and every
forecast with its reasoning. REFERENCE `set_reference` is the catalogue and its
prices. ARCHIVE `archive_entity` takes sources that went quiet. Nothing is
trusted for being bought: three resolved observations promote a source to WARM,
three silent days archive it, and archived is recoverable rather than deleted.
Cold boot to first decision is 42ms.

That map is the whole edge, because evidence is not free — every informant is a
real USDC payment over x402 on @base, and an agent with no record has no basis
to rank a source and no basis to stop buying. Over 1,000 held-out events that
costs $53.00 against $5.28, for a forecast that scores the same: 0.5658 vs
0.5664 Brier, a tie, and I report it as one. The per-domain scoping is what does
the work — every informant measures at or below zero on crypto, so the agent
learns to stop paying there and spends 71x less, while one global score per
source would carry its football skill into crypto and buy noise forever. 1,166
calls, 805 resolved, 2,010 informants bought, all of it readable back out of
memory: https://neromtoobad.github.io/receipts/

---

## 280-character version

> Six agents, one model. Each forecast is its own process and dies at exit(0) —
> the only thing that survives is @sibylcap Memory: reliability per informant per
> domain, read back in 42ms. Delete it and the same agent spends $53.00 instead
> of $5.28. https://neromtoobad.github.io/receipts/

## Before posting

- [x] Board republished 2026-09-09 07:55Z; every live figure above matches it.
- [ ] Confirm the Virtuals X handle if you want to tag it — job 75820 is named
      and no handle is used.
- [ ] The board is a snapshot of stores that stopped ticking 2026-09-06 20:02Z.
      If the league runs again before you post, re-read the numbers.
