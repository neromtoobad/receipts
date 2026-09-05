# Submission form — copy/paste

Every number below is on the live board or reproducible with one command.
Re-check the board figures at submission time; the league is still ticking.

---

## Public repo URL
```
https://github.com/neromtoobad/receipts
```

## Demo video URL
```
NEEDS HOSTING — video/RECEIPTS_demo.mp4 · 4:46 · 1080p · 26 MB
```
The cold-start recall beat runs 1:50–2:50 as one unbroken take.

## Post URLs (one per line, 2+)
```
NEEDS POSTING — drafts in prep/buildlog/day1.md, day2.md, day3.md
```

---

## What breaks when memory is deleted?

> The agent loses the ability to decide what to buy, which is its core function,
> not an optimisation. With no record of which informants have been right it has
> no basis to rank them and no basis to stop, so it buys every source it can
> afford on every single call — 4.50 informants instead of 0.55, ten times the
> spend, for a forecast that scores the same. It also loses its own history, so
> it can no longer say which source moved a call or why it trusted it.

---

## Memory walkthrough

*The field asks for three lines. Paste **Version A** first — if the box accepts
more, use **Version B**, which gives a judge line-level references and needs no
video.*

### Version A — three lines, paste this first

> **What we persist.** One entity per `(informant, domain)` holding what that
> source cost, how often it was right, and the trust it earned — written only
> when a market resolves, never seeded and never configured. **216 cells are
> scored right now and the agents have written off 119 of them as worse than
> guessing.** Alongside it: a journal of every purchase and forecast, and a
> shared Commons where each agent publishes its earned trust for the other five
> to read.
>
> **How a fresh session recalls it.** Every forecast runs in its own process
> that is killed the moment it finishes, so each one cold-starts with an empty
> context — nothing survives but what reached Sibyl. On boot it reads the trust
> map back (`list_entities` / `get_entity`), FTS-searches its own journal for the
> teams in this market, and pulls peers' trust from the Commons, inheriting what
> another agent paid to learn about a source it has never bought itself. In the
> demo you can watch one process write and die, and the next one read what it
> left: **journal 654 → 656 events, 168 → 169 forecasts, across a process
> boundary with no shared state.**
>
> **The decision it changes.** Which informants it pays for, and how much it
> believes them. With memory, on a live market: **bought 1 of 8 available
> informants for 0.0120 USDC and skipped 7.** Same agent, same market, same
> model, same prompt, same budget, memory deleted: **5 of 8 for 0.0590, every
> purchase tagged "no basis to choose"** — because without a record there
> genuinely is none. Across 1,000 held-out events that is **$5.28 against $53.00
> for a statistically identical forecast** (Brier 0.5658 vs 0.5664). Reproduce it
> with `python -m bench.run --runs 1000`, no API key required.

### Version B — full, with line references

**What we persist.** One WARM entity per `(informant, domain)` — `set_entity` at
[`agent/memory.py:201`](agent/memory.py#L201) — holding spend, resolutions, Brier
against base rate, and the earned skill and trust. Written only when a market
resolves ([`observe()`, :174](agent/memory.py#L174)), never seeded and never
configured. A source stays in HOT `set_state` until its third resolved
observation, then is promoted to WARM and the provisional state cleared
([:203](agent/memory.py#L203)); it decays with silence and is archived after
three days ([`archive_entity`, :233](agent/memory.py#L233)), recoverable rather
than deleted. Every purchase and forecast goes to the COLD journal via
`write_event`; the informant catalogue lives in REFERENCE. **216 cells are
scored today, and the agents have written off 119 of them as worse than
guessing.**

**How a fresh session recalls it.** Every forecast runs in its own process that
is killed the moment it finishes, so each one cold-starts with an empty context —
`raise SystemExit(main())` at [`agent/run_once.py`](agent/run_once.py), and the
comment above it says *the process boundary is the point*. On boot it reads the
trust map back with `list_entities`/`get_entity`
([:150](agent/memory.py#L150), [:140](agent/memory.py#L140)) and runs an FTS
`search` over its own journal for the teams in this market
([`recall()`, :421](agent/memory.py#L421) → [`own_record()`,
agent/recall.py:31](agent/recall.py#L31)), which returns how it has called that
exact fixture before and at what Brier. Peers' earned trust is read from a shared
Commons store, so one agent can inherit what another paid to learn
([`agent/sources.py:108`](agent/sources.py#L108)).

**The decision it changes.** Which informants to buy, and how much to believe
them. Selection ranks on the shrinkage-adjusted skill and refuses to pay for
anything below `MIN_SKILL`
([`agent/sources.py:31,121-124`](agent/sources.py#L121)). On a live market today,
**with memory the agent bought 1 of 8 available informants for 0.0120 USDC and
skipped 7; with memory deleted it bought 5 of 8 for 0.0590, tagging every
purchase `no basis to choose`** ([sources.py:95](agent/sources.py#L95)) — same
model, same prompt, same budget, same prices. Across 1,000 held-out events that
is **$5.28 against $53.00 for a statistically identical forecast** (Brier 0.5658
vs 0.5664). Reproduce it with `python -m bench.run --runs 1000`; it runs on a
local `qwen2.5:7b-instruct`, so a judge needs no API key.

---

## Memory primitives — check these four

| primitive | where | what it does here |
|---|---|---|
| **recall** | `memory.py:421` → `recall.py:31` | FTS over the agent's own journal for this fixture; the result goes into the prompt |
| **entities** | `memory.py:140,150,201` | `source_reliability` per (informant, domain) — the map that decides purchases |
| **consolidation** | `memory.py:174-233` | HOT state → WARM entity on the 3rd resolved observation; decay with silence; archive at 3 days |
| **reflection** | `recall.py:70`, `run_once.py:197` | the agent scores its own past Brier on this fixture and carries it into the forecast |

**Do not check these** — and here is the answer if a judge asks:

- **semantic search** — Sibyl is FTS5 with **zero embeddings**. Our recall is
  lexical. Checking this would be false.
- **summarization** — we do none.
- **temporal / time-travel** — we decay trust by `last_seen` and archive on
  staleness, which is temporal, but we never query historical state, which is
  what time-travel implies. Under-claimed deliberately.

---

## If a judge asks the hard questions

**"Your agents aren't good forecasters."** Correct, and we report it as a tie
rather than dressing it up: 48.9% accuracy, and on crypto the Brier is 0.4972
against a 0.5 coin flip — statistically nothing. The claim is not that memory
makes better forecasts. It is that memory makes the *same* forecast for a tenth
of the money, and that the crypto result is the most interesting thing on the
board: the agent measured that no informant beats the base rate there and very
nearly stopped buying, which is exactly the right call and the one an amnesiac
can never reach. **71× less spend in crypto.**

**"Is memory really load-bearing, or just cached data?"** Delete it and the core
function fails, not degrades — the deletion test is a harness in the repo, not a
claim. `python -m bench.run --runs 1000`.

**"One entity you never read is not load-bearing."** Every one of the 216 cells
is read on every forecast that touches its domain, and 119 of them are actively
suppressing purchases right now.

**Known limits, stated before you find them.** x402 settles on Base **Sepolia**;
the Virtuals ACP jobs are on Base **mainnet**. Binance is DNS-blocked on our
network so crypto resolution runs on CoinGecko alone. Two days of accumulated
league history, not two months.

---

## Before you mark Ready

1. Host the video, paste the URL.
2. Verify the Virtuals X handle, publish two posts, paste the URLs.
3. The team build page 404s — chase it in Discord.
4. Pro tier: `sibyl init` reports already-activated but the server still says
   FREE for account `b3467113…1dae`. Not a blocker; ask Sibyl to apply the grant.
