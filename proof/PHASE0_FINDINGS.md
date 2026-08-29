# Phase 0 findings — verified 2026-08-28

Measured on this machine, not assumed. Spike scripts in `spike/`.

## Environment

| | |
|---|---|
| Python | 3.11.14 via `uv venv --python 3.11` (system 3.9.6 confirmed unusable) |
| `sibyl-memory-client` | 0.7.0 |
| `sibyl-memory-cli` | 0.3.23 |
| schema version | 4 |

## Gate 1 — cross-process persistence: PASS

Two separate interpreters. Process A writes and calls `exit(0)`; process B boots
cold and recalls.

```
boot=13.4ms  get_entity=0.1ms  fts=0.2ms  state+events=0.1ms
TOTAL COLD-BOOT-TO-DECISION: 13.8ms
```

**Consequence:** the die-after-every-forecast rule is free. The 1,000-run bench is
bounded entirely by LLM latency, not by memory. No reason to soften the rule.

## Gate 2 — tenant isolation and cross-tenant reads: PASS

- Pundit 5 reading pundit 1's entity raises `NotFoundError`. Isolation is real.
- `client.set_tenant(other_id)` gives a deliberate cross-tenant read. Works, reversible.
- A shared "commons" tenant also works for reputation both sides write to.

**Consequence:** the opinion market (phase 9) is alive. Peer reputation goes in the
commons tenant; private reliability stays per-pundit.

## Gate 3 — archive lifecycle: PASS with a caveat

`archive_entity()` drops the row from `list_entities()` and makes `get_entity()` raise
`NotFoundError`. Rows land in an `archived_entities` table.

**Caveat:** `list_entities(status="archived")` returns empty, so there is no SDK read
path back. Recovery is a direct SQLite read of `archived_entities`.
**Action:** write `agent/memory.py::list_archived()` over that table so the demo can
show archive is recoverable rather than asserting it.

## Gate 4 — capacity: FAILED AS DESIGNED, fixed

The free cap is **5,242,880 bytes, enforced per database file**, tracked locally even
before activation (`free_tier_status()` reports `db_size_bytes` against `soft_cap_bytes`).

Measured journal cost, 400 events each:

| Event shape | Logical bytes/event | Events under cap |
|---|---|---|
| Full reasoning trace | 3,809 | 1,376 |
| Lean consultation | 1,249 | 4,196 |

FTS5 shadow tables roughly triple the stored payload. At one shared database, the
original design yields **22 forecasts per pundit per day** across six pundits, which
crypto hourly markets alone would blow through in a morning.

### Decisions taken

1. **One database file per pundit**, plus one commons database for peer reputation.
   Each identity gets the full cap. This is also the more honest architecture: six
   separate identities with six separate memories, exactly as if they ran on six
   machines.
2. **Two event shapes.** Consultations are lean. One fat event per forecast carries
   the reasoning trace, because that trace is the audit trail and the demo.
3. **The bench uses a throwaway database per run**, so replay volume never touches
   the league store.
4. Budget check before day 8: `free_tier_status()` runs in the tick loop and logs
   `pct_used`. If any pundit passes 70%, prune or upgrade rather than discover it
   mid-demo.

## Still open

- [ ] Registration (Aug 31, 23:59 UTC) — **user action, blocks everything**
- [ ] `sibyl init` browser activation — **user action**
- [ ] Base Sepolia faucet, and confirming where x402 actually draws from
- [ ] Virtuals ACP testnet path and whether there is an approval queue
- [ ] Fixture volume Sep 1 to 9, and the informant reliability spread

---

# Dependency checks — verified 2026-08-29

## Check 1 — x402 on Base: NO deposit step. The LONGSHOT burn does not apply here.

From the reference spec (`coinbase/x402`, `specs/schemes/exact/scheme_exact_evm.md`):
the `exact` scheme on EVM uses **EIP-3009 `transferWithAuthorization`**, which moves USDC
**directly from the client's own EOA balance**. Verification step 2 is literally "verify
the client has sufficient balance of the asset". The facilitator only broadcasts and
**pays the gas**.

| | |
|---|---|
| Network | Base Sepolia, `eip155:84532` |
| USDC | `0x036CbD53842c5426634e7929541eC2318f3dCF7e` |
| x402Version | 2 |
| Scheme | `exact`, `assetTransferMethod: eip3009` |

**Consequences:**
- No deposit/escrow provisioning step. The Circle Gateway problem was Arc-specific.
- **The agent wallet needs USDC only, not ETH.** The facilitator pays gas.
- Permit2 is the fallback for tokens without EIP-3009. We use USDC, so we do not need it.

## Check 2 — Virtuals ACP: Base Sepolia supported, no approval queue.

Base Sepolia (`84532`) is an officially supported ACP chain, and the SDK examples use
`baseSepolia` throughout (`AssetToken.usdc(0.1, baseSepolia.id)`, `createFundTransferJob`).
An `IS_TESTNET` flag switches the environment.

Onboarding is permissionless, no whitelist and no review:

```bash
npm install -g @virtuals-protocol/acp-cli   # Node >= 18
acp configure          # one-time browser OAuth, tokens to OS keychain
acp agent create       # provisions on-chain wallet + email
acp agent add-signer   # P256 signing key, browser-approved
acp offering create    # list the forecast service
```

**Consequences:**
- **Both partner stacks land on the same chain with the same USDC.** Base Sepolia carries
  x402 and ACP together. No mainnet money required for either.
- **Use the CLI, not the Node SDK.** Every command supports `--json`, so the Python runtime
  shells out. This removes the Python/Node split entirely; no bridge service needed.
- The CLI ships an agent-readable `SKILL.md`. `acp skill print` emits it, `acp skill check
  --against <v> --json` detects drift. Append it to `AGENTS.md` on day 7.
- **Avoid `acp agent tokenize` (3 USDC) and hosting (20 USDC/month).** Neither is needed;
  registration plus offerings plus jobs is the whole requirement.

## Check 3 — Fixture volume: not a problem. Earlier concern was wrong.

Sep 2 2026 is a Wednesday, so it is a midweek cup night: German Cup, Coppa Italia, KNVB
Beker, Copa do Brasil, Copa Argentina, plus Scottish Premiership, English Championship and
League One, Belgian, Austrian, Danish, Brazilian Serie A, J.League (10 fixtures) and most
of South America. Dozens of top-tier resolvable fixtures per day across the window.

**Consequence:** football alone carries the league. Crypto stays in for domain contrast and
fast resolution, not out of volume necessity.

## The one remaining risk

**The informant reliability spread is still unmeasured**, and it is the only open item that
can still reshape the project. If all six informants turn out equally reliable there is
nothing to learn and no subject. This needs the historical corpus built and
`scripts/measure_spread.py` run before day 2.

---

# Live data path — verified 2026-08-29

Registration: **DONE.**

## Check 4 — live fixtures with pre-match odds: PASS

`https://www.football-data.co.uk/fixtures.csv` carries upcoming fixtures in the same schema
as the historical corpus, so the informants run unchanged from backtest to live.

| | |
|---|---|
| Fixtures in feed | 197 across 20 divisions |
| `AvgH/D/A` present | 197 / 197 |
| `MaxH/D/A` present | 197 / 197 |
| `PSH/D/A` (Pinnacle) present | **0 / 197** |

## Check 5 — live results: PASS, with a 2-day lag

Current season files are `mmz4281/2627/*.csv` and they are live. Most recent resolved match
in the feed is 2026-08-27, two days behind. Roughly four to five football resolution cycles
inside the ten-day window. Crypto resolves hourly and carries the fast learning.

## Two problems found, both fixed

**1. Pinnacle has no live coverage at all.** Zero in `fixtures.csv` and zero across the whole
current season, not the 82% seen historically. `pinnacle_desk` would have been dead on
arrival in the live league.
**Fix:** re-based on best-available price (`MaxH/D/A`), renamed `sharp_desk`, and
**re-measured rather than assumed**. Skill is +0.089 to +0.132 with 100% coverage, and the
league numbers are unchanged: 15.0x spend, brier 0.5224 against 0.5280. At 0.045 it is still
nearly four times the price of a regional desk that matches it inside a beat, which is
exactly the economic tension the agent has to learn.

**2. Rolling form has no burn-in at the start of a season.** Form informants need five prior
matches per team; in early September teams have played three to five.
**Fix:** seed the rolling windows from the tail of season 2526. In E0, 17 of 20 teams carry
over. The three promoted sides start cold, which is honest, since a promoted team genuinely
has no top-flight form.

## Still open

- [ ] `sibyl init` browser activation — **user action**
- [ ] Base Sepolia USDC into a burner wallet, then an end-to-end x402 smoke test
- [ ] Virtuals ACP: `acp configure` one-time browser OAuth — **user action**

---

# Activated account — verified 2026-08-29

`sibyl init` complete. Account `b3467113…1dae`, tier FREE, wallet
`0x58a17a30…5301f`, schema version 4, health all green.

## Cap is confirmed PER DATABASE FILE, on a real activated account

Two local databases written to unequal sizes, both queried through
`free_tier_status()`:

| database | reported size | pct of cap | cap |
|---|---|---|---|
| `pundit_1.db` | 1,789,952 | 34.14% | 5,242,880 |
| `pundit_2.db` | 307,200 | 5.86% | 5,242,880 |

Independent sizes against the same cap. **One database per pundit stands.** The
earlier unactivated measurement was right and activation does not aggregate.

## Real capacity, measured on the activated account

2,983 bytes per traced event, so **1,757 traced forecasts per pundit database**,
or about 175 per pundit per day across a ten-day window. Comfortable.

## `sibyl status` reports the wrong percentage. Do not use it.

The CLI printed `266,240 bytes (12.7% of free cap)`. The true figure is 5.08%:
266,240 / 5,242,880. The CLI is dividing by 2,097,152 while both the SDK constant
`FREE_TIER_CAP_BYTES` and the server report 5,242,880.

**`free_tier_status()` is authoritative and the tick loop must read `pct_used` from
it.** Reading the CLI would have shown 2.5x the real usage and triggered a pointless
mid-run prune.

## Local databases default to a different tenant

`MemoryClient.local(path)` opens tenant `00000000-…-0001`, not the account UUID that
the activated default database uses. `agent/memory.py` sets the tenant explicitly on
every call so a pundit can never silently write to the wrong identity.
