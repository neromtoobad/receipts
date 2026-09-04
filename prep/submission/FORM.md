# Submission form — copy/paste

## Public repo URL
```
https://github.com/neromtoobad/receipts
```

## Demo video URL
```
NEEDS HOSTING — video/RECEIPTS_demo.mp4, 4:46, 1080p, 27 MB
```
Upload to YouTube (unlisted is fine) or post natively on X and use that URL.

## Post URLs (one per line, 2+)
```
NEEDS POSTING — drafts in prep/submission/POSTS.md
```

---

## What breaks when memory is deleted?

> Source selection breaks completely. Without memory the agent has no basis to
> prefer any informant over any other, so it buys every one it can afford, every
> time, forever — 4.50 informants a call instead of 0.55, ten times the spend for
> a forecast that scores the same. It also loses its own record, so it can no
> longer tell you which source moved a call or why it trusted it.

---

## Memory walkthrough

> **What we persist.** One WARM entity per (informant, domain) holding what that
> source has cost, how often it was right, and the skill and trust it earned —
> written only after a market resolves, never seeded. Purchases and forecasts go
> to the COLD journal; the informant catalogue sits in REFERENCE; sources that go
> quiet for three days are archived rather than deleted.
>
> **How a fresh session recalls it.** Every forecast runs in its own process that
> is killed when it finishes, so each one cold-starts. It reads the trust map
> back with `get_entity`/`list_entities`, and runs an FTS `search` over its own
> journal for the teams in the market, which returns how it has called that
> fixture before and at what Brier.
>
> **The decision it changes.** Which informants to buy, and how much to believe
> them. On a real market today, with memory the agent bought 1 of 8 available
> informants for 0.0120 USDC; with memory deleted, the same agent on the same
> market bought 5 of 8 for 0.0590, tagging every purchase "no basis to choose".
> Across 1,000 held-out events that is $5.28 against $53.00 for a statistically
> identical forecast (Brier 0.5658 vs 0.5664).

---

## Memory primitives — check these four

- [x] **recall** — `search()` over the journal; `agent/recall.py` turns hits into
      the agent's own record on a fixture, which goes into the prompt.
- [x] **entities** — `set_entity`/`get_entity` on `source_reliability` per
      (informant, domain). This is the trust map that decides purchases.
- [x] **consolidation** — a source lives in HOT state until its third resolved
      observation, then it is promoted to a WARM entity and the state cleared;
      trust decays with silence and archives after three days.
- [x] **reflection** — the agent reads its own past Brier on the same fixture and
      carries it into the forecast, so it can see where it has been wrong before.

**Do NOT check these**, and here is why, so you can answer if asked:

- **semantic search** — Sibyl is FTS5 with zero embeddings. Our recall is
  lexical. Claiming this would be false.
- **summarization** — we do none.
- **temporal / time-travel** — borderline. We decay trust by `last_seen` and
  archive on staleness, which is temporal, but we never query past state, which
  is what "time-travel" implies. Under-claiming here is the safer side of a
  question we would rather not lose.

---

## Before you mark Ready

1. **Claim the Pro tier.** You are on **free at 79.1%** of the 5 MB cap. Pro is
   free for the event and lifts the cap. Run `sibyl init`, then `sibyl status`.
2. Host the video, fill the URL.
3. Verify the Virtuals X handle, post both, fill the URLs.
4. The build page at your submission link still 404s — chase it in Discord.
