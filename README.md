# RECEIPTS

**A league of AI pundits that learn which informants to trust, and pay for the privilege.**

Six agents forecast real matches and real markets. Same model, same prompt, same
budget. Every piece of evidence they use costs real money, bought from informants
on Base, each with a real price and a real, unadvertised reliability.

Nobody tells them which informant is any good. They find out by getting it wrong
and paying for it.

**The process dies after every single forecast.** Fresh boot, empty context, no
state but what was written to disk. The only thing that survives is a private map
of who to trust, on what — and that map is the entire edge.

---

## The deletion test

Delete the memory layer and the same agent, on the same market, with the same
model and the same prompt, **buys ten times as many informants and spends ten
times as much**, for no better forecast.

| arm | informants bought | spend/forecast | 1,000 forecasts |
|---|---|---|---|
| domain-scoped memory | 0.56 | 0.0053 USDC | **$5.34** |
| memory without domain scoping | 0.10 | 0.0010 USDC | $1.04 |
| no memory | 4.50 | 0.0530 USDC | **$53.00** |

**9.9x on spend, for the same forecast quality.** Football alone is 6.0x. Crypto
alone is **67x**, because the memory arm learns there is nothing there worth
paying for and very nearly stops buying at all.

Brier across 1,000 held-out events: **0.5653 with memory, 0.5667 without.** The
memory arm is ahead in every split and the direction is consistent, but the
largest margin is 0.0019 — too small to claim as a quality win, so we don't. The
result is *same quality, one tenth the cost*, which is the claim that survives a
judge's follow-up question.

The spend figures are model-independent: an arm learns from what each *source*
said against the outcome, never from its own forecast, so selection is decided
entirely by memory. 3,000 model calls on `qwen2.5:7b-instruct` running locally,
zero failures, no API key — so a judge can reproduce it exactly. Method, chart and
caveats in [`proof/BENCH.md`](proof/BENCH.md) and
[`proof/BENCH_STATUS.md`](proof/BENCH_STATUS.md).

---

## Where memory is written and read

**[`agent/memory.py`](agent/memory.py).** One file. Nothing else in the project
imports the Sibyl SDK.

| Tier | Call | What it holds here |
|---|---|---|
| HOT | `set_state` | this turn's working set; sources paid for but not yet proven |
| WARM | `set_entity` | `source_reliability` per `(informant, domain)` — the map |
| COLD | `write_event` | every purchase and every forecast, with its reasoning |
| REFERENCE | `set_reference` | the informant catalogue and pricing |
| ARCHIVE | `archive_entity` | informants that went quiet, recoverable |

A source enters as HOT state. After three resolved observations it is **promoted**
to a WARM entity. Trust decays with staleness. After three silent days it is
**archived**, and `Memory.restore()` brings it back — archiving is not deleting,
which is why the trust map shows archived sources greyed rather than hiding them.

**The decision that memory drives** is [`agent/sources.py`](agent/sources.py):
what to buy, what to skip, and when to stop. Delete the memory and it has nothing
to rank with.

---

## How memory made this possible

The interesting behaviours are all refusals, and none of them can be prompted in.

**It refuses to pay more for the same thing.** `sharp_desk` and `boot_room` both
score +0.116 in Bundesliga. One costs 0.045, the other 0.012. Memory picks the
cheap one — not "buy the best source" but "buy the best value", which price alone
gets backwards.

**It refuses to buy at all where nothing works.** Every informant measured at or
below zero skill on crypto direction. The correct spend there is nothing, and only
the domain-scoped arm gets there. A single global reliability figure cannot hold
that lesson and the football one at the same time: the flat-log arm carries
`formline`'s positive football skill into crypto and pays for noise forever.

**It refuses to trust an expensive liar.** `chalk_desk` costs 0.020 and measured
negative in all six leagues. An agent with memory stops buying it. An agent
without has no way to know.

---

## Proof

Every claim below is a transaction hash, a block number, or a measured figure.

| | |
|---|---|
| **Base — x402 settlement** | [`0xb0cc50db…64eebc`](https://sepolia.basescan.org/tx/0xb0cc50dbf1530884b0789f15b0498632bb50d6a74b74336b58659fefd864eebc) · 0.012 USDC · block 46195402 · [`proof/ONCHAIN.md`](proof/ONCHAIN.md) |
| **Virtuals — ACP job** | job `75249`, completed on Base mainnet · [`proof/VIRTUALS.md`](proof/VIRTUALS.md) |
| **Informant reliability** | 6,462 real matches, 6 leagues, 3 seasons · [`proof/SPREAD.md`](proof/SPREAD.md) |
| **Domain-scoped skill** | football + 18,000 hourly candles · [`proof/DOMAINS.md`](proof/DOMAINS.md) |
| **Memory measurements** | cold boot to decision 41.6ms; 1,757 traced forecasts per pundit · [`proof/PHASE0_FINDINGS.md`](proof/PHASE0_FINDINGS.md) |

**Base is load-bearing.** There is no free path to evidence: every informant call
returns HTTP 402 until paid. Gas on that settlement was paid by the facilitator,
not the agent — pundit_1's ETH is unchanged across the transaction and only its
USDC moved. That is EIP-3009 `transferWithAuthorization`, and it means the agent
needs USDC and no ETH.

**Virtuals is load-bearing.** Job 75249 is one pundit hiring another: `pundit_5`
paid `pundit_1` into escrow, received a forecast produced by the real runtime, and
released it. The first attempt reverted because an agent cannot hire itself, which
forced a second agent — and one pundit paying another *is* the opinion market.

---

## Run it

```sh
uv venv --python 3.11 && source .venv/bin/activate
uv pip install 'sibyl-memory-cli[mcp]' sibyl-memory-client fastapi uvicorn \
  eth-account httpx anthropic google-genai pytest
sibyl init

ollama serve & ollama pull qwen2.5:7b-instruct   # or set an API key, see .env.example

uvicorn evidence.app:app --port 8402 &           # ten x402-gated informants
python -m agent.run_once --agent pundit_1 --pick # one forecast, then the process dies
python -m resolver.loop --once                   # score outcomes, update reliability
python -m web.build_site                         # -> web/index.html, the trust map

./scripts/league.sh                              # six pundits, every twenty minutes
python -m bench.run --runs 1000                  # the deletion test
pytest                                           # 62 tests, offline, ~15s
```

`./scripts/settle_once.sh` reproduces the onchain payment in one command.

---

## How it is put together

```
agent/       boots, reads memory, buys, forecasts, dies
  memory.py    every Sibyl call. nothing else touches the SDK
  sources.py   what to buy, from what it remembers
  forecast.py  the model call. byte-identical prompt across every arm
  run_once.py  one forecast, then exit(0)
resolver/    separate process. scores outcomes, writes reliability back
evidence/    FastAPI. ten informants behind HTTP 402
bench/       replay harness. three arms, one corpus, the chart
web/         static generator -> one self-contained HTML file
corpus/      resolved historical events, and how the spread was measured
proof/       tx hashes, measurements, findings
```

**Integrity.** We declare each informant's *data access* and its *price* — both
real properties of a data vendor. We never declare a hit rate. Every reliability
figure is measured on held-out seasons: informants are calibrated on 2023-24 and
scored on 2024-25 and 2025-26, which they have never seen. The agent sees only
vendor marketing that is true and uninformative; the full disclosure is in
[`proof/DOMAINS.md`](proof/DOMAINS.md), for judges rather than for the agent.

---

## Prior work

The x402 payment client is ported from **LONGSHOT** (Lepton Agents Hackathon,
Arc) — `agent/src/paying/x402.ts` rewritten in Python as
[`evidence/x402.py`](evidence/x402.py), and rewritten again for the x402 v2
`exact`/`eip3009` shapes. The pool-contract pattern and the Next.js dashboard
stack also come from LONGSHOT, though the dashboard here was deliberately replaced
with a static generator. Everything else is new.

## AI tools used

Built with Claude Code (Opus). It wrote most of the implementation, and the
research it did before the build changed the design twice: measuring that crypto
direction has no learnable signal turned a weak domain into the strongest argument
for domain-scoped memory, and measuring the informant spread on real matches
caught that the first two roster designs had nothing to learn. Forecasts run on
`qwen2.5:7b-instruct` locally, so the benchmark is reproducible without an API key.

## Licence

MIT. See [LICENSE](LICENSE).
