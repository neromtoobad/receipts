# Virtuals ACP — a job, run end to end

Not a registration screenshot. One agent hired another, paid it in USDC escrow,
received a forecast produced by the real runtime, and released the escrow.

## The job that matters: 75820

Job **75249** was run on day one, when pundit_1 had no memory yet: it bought
0.027 USDC of evidence, found none of it carried an earned trust weight, and
correctly returned the base rate at confidence 0.00. Honest, and a poor
demonstration.

**75820** is the same flow after two days of league running, and the difference
is the whole project:

| | |
|---|---|
| job id | **75820** |
| requirement | Portsmouth v Derby, full time result (championship) |
| what it bought | `formline` (trust 0.129), `calcio_desk` (trust 0.149), `iberian_desk` (unproven, exploring) |
| what it recalled | *"You have called Portsmouth and Derby 2 time(s) before; 2 resolved at a mean Brier of 0.603, against your overall 0.572 — worse than your average here."* |
| deliverable | `{"H": 0.53, "D": 0.21, "A": 0.26}`, confidence **0.27** |
| its reasoning | *"calcio_desk's strong preference for a home win moved the forecast, while formline and iberian_desk were discounted due to their lower trust weights."* |
| phases | create-job → budget set → funded → submitted → **completed** |
| balances | buyer 0.0905 → 0.0810, seller 1.0995 → 1.1085 |

Two things in that deliverable are only possible with memory. The agent named
which source moved it and **which it discounted, by trust weight** — weights it
could only have earned by paying for those sources and watching them resolve. And
the record it recalled about these two teams came from a journal search, because
reliability entities are keyed by source and domain, and a team is neither.

A third job, 75819, was created with empty requirements by a scripting mistake on
my part and rejected on chain rather than left dangling.

## The first job, for the record

| | |
|---|---|
| job id | 75249 |
| protocol | ACP v2 |
| chain | Base **mainnet** (8453) |
| buyer | `RECEIPTS pundit_5` · `0x4f9b42c3322588e0cd24ec8208100afc6200e46e` |
| seller | `RECEIPTS pundit_1` · `0x97b3fc0a7d6e4e311564eae243dc7bf3519a77d8` |
| offering | "Forecast a market", fixed 0.01 USDC, 15 min SLA |
| requirement | Crystal Palace v Man City, full time result, outcomes H/D/A |
| phases | create-job → budget set → **funded** → **submitted** → **completed** |

Balances moved as expected: buyer 0.1000 → 0.0905, seller 1.0905 → 1.0995.

## The deliverable, produced by the real agent

```json
{"probabilities": {"H": 0.433, "D": 0.244, "A": 0.323},
 "confidence": 0.0,
 "reasoning": "No evidence sources were given a trust weight, so the forecast remains at base rate.",
 "leaned_on": [],
 "evidence_spend_usdc": 0.027}
```

It bought 0.027 USDC of evidence through the x402 layer, found that none of it
carried an earned trust weight yet, and **declined to move off the base rate**.
That is the cold-start case behaving correctly: an agent with no history does not
pretend to know. Confidence 0.0 means exactly what the prompt says it means.

## Why one pundit hires another

The first attempt reverted. The calldata showed client, provider and evaluator all
set to the same address: the contract will not let an agent hire itself. So the
buyer is a second agent, which is a better demonstration anyway — **one pundit
paying another for a take is the opinion market**, and it runs on real rails
rather than being described.

## Corrections to earlier research

Phase 0 recorded "Base Sepolia supported, no approval queue". Both halves are
true of the API, and both are misleading in practice:

- The testnet **API** supports chain 84532, but the testnet **sign-in site**
  (`app-dev.virtuals.io`) is behind HTTP Basic auth and cannot be reached without
  credentials from Virtuals. Testnet is not usable from outside.
- The CLI defaults to mainnet (`chain-id 8453`), and `acp chain list` reports
  `{"environment":"mainnet"}` with Base, Robinhood and Solana only.

So exercising ACP costs real money. Total spend for this proof was about
**two cents**, after dropping the offering price from 0.5 to 0.01 USDC.

## An observation worth acting on

The agent spent 0.027 USDC on evidence and then ignored all of it. The prompt says
an unweighted source is "unproven, not trustworthy by default"; the model read
that as "ignore entirely". Defensible on a cold start, but wasteful: if nothing
will be believed, nothing should be bought. Selection already handles this once a
domain has history, so this only bites on the very first forecasts in a domain.

**Not changed yet**: `SYSTEM` is sha-pinned and a benchmark run is in flight.
Editing it mid-run would void the comparison.
