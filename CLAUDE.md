# RECEIPTS

**A league of AI pundits that learn which informants to trust, and pay for the privilege.**

Rename this file to `AGENTS.md` before submitting. Never commit it as `CLAUDE.md`.

---

## What we are building

Six agent pundits forecast real events across three domains for ten days. Every forecast
costs money: evidence is bought from x402-gated informants on Base, each with a real price
and a real, unadvertised reliability. When an event resolves, the outcome writes back to
every informant the agent consulted, scoped to that domain.

The edge is not the model. Every agent runs the same model with the same prompt. The edge
is a private, accumulated map of **who is worth paying for, on what**. That map exists only
in Sibyl Memory, and it cannot be prompted in or reconstructed from any API.

**The rule that makes it real: the agent process dies after every forecast.** Fresh boot,
empty context, no state but what was written to disk.

### Why it qualifies for the Sibyl Labs Hackathon

The gate is the deletion test. Delete the memory layer and the agent has no idea who to
believe, so it buys the expensive garbage and skips the cheap gold. Accuracy collapses to
day-one levels and spend triples at the same time. We prove this as a number, not a claim:
a headless replay bench runs three arms over the same corpus and prints the table.

Scoring targets, in order:

| Criterion | Max | How we take it |
|---|---|---|
| Memory load-bearing | 40 | Domain-scoped reliability entities with promotion, decay and archival, plus cross-agent reads for the opinion market. Coordination and dynamic storage, not recall. |
| Innovation & originality | 25 | Learned source pricing. Nobody else will build an agent whose entire skill is knowing which informant lies. |
| Technical execution | 20 | The replay bench is the regression test. It survives a second run because it runs a thousand times a night. |
| Pitch & presentation | 15 | Trust maps. You watch an agent learn who is lying to it. |
| PMF bonus | +10 | Public live leaderboard running through the window, plus a waitlist. |
| Multiplier | x1.25 | Base: x402 per evidence call, league escrow and payout. Virtuals: each pundit is a registered ACP agent hireable for a forecast. |

Prior Work declaration goes in the README on day one: the x402 client and the pool
contract pattern come from LONGSHOT (Lepton Agents Hackathon, Arc). Declared reuse is
allowed. Undeclared reuse is a disqualification risk.

---

## Tech stack

| Layer | Choice | Version | Why |
|---|---|---|---|
| Agent runtime | Python | 3.11 via `uv` | `sibyl-memory-client` is a Python SDK. System Python is 3.9.6 and will not do. |
| Memory | `sibyl-memory-client`, `sibyl-memory-cli[mcp]` | latest | SQLite + FTS5, five tiers, multi-tenant. One tenant per pundit. |
| Forecast model | `claude-sonnet-5` | — | Same model every arm, or the benchmark is meaningless. |
| League metric | Brier, not accuracy | — | Measured 2026-08-29: crypto direction has no skill for anyone, so accuracy there is noise. Brier is the proper scoring rule for a calibration league. |
| Bench model | `claude-haiku-4-5-20251001` | — | Thousands of replay runs. Only valid if every arm uses it. |
| Evidence service | FastAPI + uvicorn | latest | We own both sides of the 402, same as LONGSHOT. |
| Payments | x402 `exact`/eip3009 on Base Sepolia (`84532`) | v2 | USDC `0x036CbD53842c5426634e7929541eC2318f3dCF7e`. Port `LONGSHOT/agent/src/paying/x402.ts`, sign with `eth-account`. Facilitator pays gas. |
| Contracts | Foundry, Solidity 0.8.24+ | — | `League.sol`: entry escrow, payout. |
| Virtuals | `@virtuals-protocol/acp-cli` | Node >=18 | Base Sepolia supported, no approval queue. Python shells out via `--json`, so no Node bridge service. |
| Dashboard | Next.js 16 + React 19 + Tailwind v4 | — | Same hybrid stack as LONGSHOT. Reads the SQLite read-only. |
| Scheduler | `launchd` or a plain loop + `caffeinate` | — | See "Things that burned us". |

---

## Repo structure

```
receipts/
  agent/            python runtime. boots, reads memory, buys, forecasts, dies.
    memory.py       every Sibyl call lives here. nothing else touches the SDK.
    sources.py      informant selection from remembered reliability, under budget.
    forecast.py     the LLM call. identical across all arms.
    run_once.py     entrypoint. one forecast, then exit(0).
  resolver/         separate process. scores resolved events, updates reliability.
  evidence/         FastAPI. six x402-gated informants with real prices.
  bench/            replay harness. three arms over one corpus. prints the chart.
  contracts/        League.sol + foundry.
  acp/              Virtuals registration and job handler.
  web/              Next.js dashboard. standings, trust maps, event feed.
  corpus/           resolved historical events for the replay bench.
  proof/            tx hashes, bench output, screenshots.
```

**Storage layout (measured in Phase 0, not assumed):** one SQLite file per pundit under
`memory/pundit_N.db`, plus `memory/commons.db` for peer reputation. The free cap is 5.2 MB
enforced **per file**, and a journal event with a full reasoning trace costs ~3.8 KB once
FTS5 shadow tables are counted. One shared database would have capped the league at 22
forecasts per pundit per day. Consultations are written lean; one fat event per forecast
carries the trace. See `proof/PHASE0_FINDINGS.md`.

**Rule:** every Sibyl call goes through `agent/memory.py`. When a judge asks where memory
is written and read, that is one file and it takes fifteen seconds to show. The rules say a
judge must find it in under two minutes.

---

## The memory model

Two event families, eight domains. **Measured 2026-08-29, see `proof/DOMAINS.md`.**

- `football` — six leagues, each its own domain. Verified: dozens of resolvable fixtures per day across Sep 1 to 9, including midweek cup nights. Regional desks show a real beat structure, skill +0.10 to +0.12 inside the beat against +0.01 to +0.04 outside it.
- `crypto_1h`, `crypto_24h` — direction markets. **Measured skill of every informant is zero or negative.** Funding rate, volume regime and momentum all fail. This is not a flaw in the roster, it is the finding, and it is the most valuable domain in the league.

**Why a domain where nothing works is the best domain we have.** The lesson an agent must
learn there is not which informant to buy, it is that *none of them are worth buying*, and
to stop paying. No global ranking can hold both lessons at once: the flat-log arm sees
positive skill for `formline` from football and keeps buying it in crypto where it is
noise. Only domain-scoped memory catches that.

Eight informants. **Verified 2026-08-29 on 6,462 real matches** — see `proof/SPREAD.md`.

Five are regional desks carrying market-grade data inside a beat and a thin public signal
outside it. `pinnacle_desk` is sharp everywhere but costs 0.045 and covers only 74%.
`chalk_desk` charges 0.020 and is the worst informant in five of six leagues. `formline` is
cheap, weak and honest.

**Which desk covers which league is advertised nowhere.** It is discoverable only by paying
and watching what resolves, which is precisely the map that lives in memory.

**Integrity:** we declare each informant's *data access* and its *price*, both real product
properties of a data vendor. We never declare a hit rate. Every reliability figure in
`proof/SPREAD.md` is measured on held-out seasons.

Tier usage, all five earning their place:

| Tier | Holds |
|---|---|
| HOT `set_state` | This turn's working set. Candidate informants, budget left, the open question. |
| WARM `set_entity` | `source_reliability` per `(informant, domain)`. Hit rate, sample count, mean cost, staleness, confidence. Also `peer_reliability` per `(agent, domain)` for the opinion market. |
| COLD `write_event` | Every consultation and every forecast, with the reasoning trace. This is the audit trail and the resolver's input. |
| REFERENCE `set_reference` | Informant catalogue, pricing, domain taxonomy. |
| ARCHIVE `archive_entity` | Informants that go quiet or stale. Recoverable, which is the point. `list_entities(status="archived")` returns nothing, so `memory.py` reads the `archived_entities` table directly for the recovery path. |

Promotion: a `(source, domain)` pair enters as HOT state, promotes to a WARM entity after
`PROMOTE_N` resolved observations, decays with staleness, archives after `STALE_DAYS` silent.

---

## Build phases

- [x] **Phase 1 (Day 1)** Foundation. Git identity, uv 3.11, Sibyl activated, `agent/memory.py`, cross-process proof and lifecycle tests green.
- [~] **Phase 2 (Day 2)** Evidence layer built and the x402 path proven against the live facilitator. **Not closed until a settlement lands**: the multiplier needs an executed onchain action, and the wallet is unfunded.
- [x] **Phase 3 (Day 3)** Agent runtime. Boot, forecast, die. Buys everything, learns nothing.
- [ ] **Phase 4 (Day 4)** Resolver and reliability memory. Promotion, decay, archival.
- [ ] **Phase 5 (Day 5)** Source selection from memory. **Critical path. This is the gate.**
- [ ] **Phase 6 (Day 6)** Replay bench and the deletion chart. **Critical path. This is the proof.**
- [ ] **Phase 7 (Day 7)** Virtuals ACP registration and job handler. Secures the second multiplier.
- [ ] **Phase 8 (Day 8)** Dashboard, trust maps, public leaderboard live.
- [ ] **Phase 9 (Day 9)** Opinion market between agents. Cuttable. Buffer if behind.
- [ ] **Phase 10 (Day 10)** Video, README, posts, submit.

---

## Commands

```bash
# environment
uv venv --python 3.11 && source .venv/bin/activate
uv pip install 'sibyl-memory-cli[mcp]' sibyl-memory-client fastapi uvicorn eth-account httpx anthropic

# sibyl
sibyl init                      # browser activation, writes credentials 0600
sibyl status                    # tier, db size, account
sibyl health                    # provider self-check
sibyl memory list               # read-only inspection
sibyl memory search "informant" # FTS across all tiers
sibyl memory recall source_reliability odds_feed:football

# services
uvicorn evidence.app:app --port 8402 --reload
python -m resolver.loop

# one forecast, then the process dies
python -m agent.run_once --agent pundit_3 --market <market_id>

# the whole league, one tick
./scripts/tick.sh

# the chart
python -m bench.run --arms sibyl,nomemory,jsonfile --runs 1000 --model claude-haiku-4-5-20251001

# contracts
forge build && forge test
forge script script/Deploy.s.sol --rpc-url $BASE_SEPOLIA_RPC --broadcast

# dashboard
cd web && npm run dev

# keep the mac awake for the ten day run
caffeinate -dimsu &
```

---

## Demo plan

What the judge sees, in this order. Two to five minutes, and the recall beat is one
continuous unedited segment with the commit hash on screen.

1. **The viewing centre line.** Standings. Six pundits, ten days of calls on record.
2. **Pick a pundit. Open its trust map.** Six informants, green where trust was earned, red where it was burned. Say out loud: it learned this by losing money.
3. **The cold boot.** Kill the process. Show the empty context. Boot it on a fresh market. It searches memory, skips the expensive informant it stopped trusting on day four, buys the two cheap ones that earn their price, forecasts. Timestamp and commit hash visible the whole time. **This is the fresh-session recall beat. Do not cut this segment.**
4. **Delete the memory.** Same agent, same market, same seed. On football it buys 4.5 informants instead of 1.6 and spends 4.2x as much for 3.5 points less accuracy. Across the whole league it spends 15x as much for no better forecasts.
5. **The chart.** Replay bench, three arms, a thousand runs. Accuracy up, spend down, ROI transformed. The deletion test as a number.
6. **The opinion market**, if it shipped. Agent 5 pays agent 3 for a football take, because it remembers agent 3 is sharp on football and useless on crypto.
7. **Onchain.** Basescan. x402 settlements and the league payout.

---

## Pitch script, 60 seconds, spoken

> In every viewing centre on earth, the loudest man is never wrong. Because nobody keeps records.
>
> RECEIPTS is a league of AI pundits, and it keeps records.
>
> Six agents, same model, same prompt, same budget. They forecast real matches and real
> markets, and every piece of evidence they use costs real money, bought from informants
> on Base. Some informants are cheap and excellent. Some are expensive and lying.
>
> Nobody tells them which is which. They find out by getting it wrong and paying for it.
>
> Here is the part that matters. The process dies after every single forecast. No context
> carries. The only thing that survives is what the agent wrote to Sibyl Memory, and what
> it writes is a private map of who to trust, on what.
>
> Delete that map and watch. Same model, same prompt. It buys ten times as many informants,
> spends fifteen times as much, and forecasts no better. Ten days of learning, gone, because
> we deleted a file.
>
> That is not an agent with memory bolted on. That is an agent whose entire skill is memory.
>
> RECEIPTS. Everybody's calls are on record.

---

## Things that burned us

Real, from prior events. Do not relearn these.

➠ **Git identity before the first commit.** Commit attribution to an AI account got a
project marked down at ETHGlobal Open Agents. Configure it in step one of day one, not after.

➠ **A sleeping MacBook is a failed run.** Agent responders timed out overnight during OKX
A2A review and got rejected. This league runs ten days unattended. `caffeinate -dimsu`
stays on, and the tick loop logs every miss loudly.

➠ **The x402 deposit trap was Arc-specific and does NOT apply on Base.** Verified
2026-08-29: the `exact` scheme uses EIP-3009 `transferWithAuthorization`, which pays
straight from the agent EOA's USDC balance, and the facilitator pays the gas. The agent
wallet needs **USDC only, no ETH**. Do not go looking for a deposit step on Base; there
isn't one. Still smoke test the path end to end before building on it.

➠ **`shadcn@2 add`, never `@latest`.** Components silently switch to Base UI and the build
drifts.

➠ **Force the right gas type on unfamiliar chains.** Intermittent "insufficient funds"
with a funded wallet means the tx type is wrong, not the balance.

➠ **The free tier cap is per database file and the journal is expensive.** Measured on
the activated account: 2,983 bytes per traced event, so 1,757 traced forecasts per pundit
database. Check `free_tier_status()` in the tick loop and log `pct_used`.

➠ **`sibyl status` prints the wrong cap percentage.** It divides by 2 MB while the real
cap is 5,242,880. It showed 12.7% where the truth was 5.08%. Read `pct_used` from
`free_tier_status()`, never the CLI, or you will prune a database that was nowhere near
full.

➠ **`MemoryClient.local(path)` defaults to tenant `00000000-…-0001`,** not your account
UUID. Set the tenant explicitly on every call or a pundit will write to the wrong identity
without erroring.

➠ **System Python is 3.9.6.** Anything that assumes it is 3.11 will fail confusingly.
Always `source .venv/bin/activate` first.

---

## Things NOT to do

➠ **Do not let the agent see its own context between forecasts.** If any state survives
the process boundary the whole thesis is dead. `run_once.py` calls `exit(0)`. It never loops.

➠ **Do not fake informant reliability.** Reliability must emerge from real data quality.
A hardcoded liar is a fabricated result and the rules disqualify fabricated evidence,
including after payout.

➠ **Do not vary the model between benchmark arms.** Same model, same prompt, same seed,
same corpus. The only variable is the memory layer, or the chart proves nothing.

➠ **Do not build the opinion market before day 8.** It is the highest-scoring feature and
the most cuttable. Everything before it is load-bearing for the gate.

➠ **Do not scatter Sibyl calls.** They live in `agent/memory.py`. One file, judge finds it
in fifteen seconds.

➠ **Do not skip the Prior Work declaration.**

➠ **Do not claim a partner stack we cannot exercise live.** An unexercised claimed stack
loses the bonus outright.

➠ **Do not use memory as a notepad.** Rules section 10 floors trivial memory use. Every
write must change a later decision.
