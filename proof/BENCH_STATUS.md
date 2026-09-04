# Bench status — what is proven and what is not

Generated 2026-08-30, offline plumbing run. **This is not the chart.**

## Proven, and model-independent

Selection is decided entirely by memory: an arm learns from what each SOURCE said
against the outcome, never from its own forecast. So the spend figures below are
deterministic and hold whatever forecaster runs on top.

1,000 held-out events, 500 football and 500 crypto, budget 0.060 per forecast.

| arm | bought/call | spend/call | total |
|---|---|---|---|
| sibyl (domain-scoped) | 0.55 | 0.0053 | $5.28 |
| flat json log | 0.08 | 0.0009 | $0.89 |
| amnesiac (no memory) | 4.50 | 0.0530 | $53.00 |

**Deletion test on spend: 10.0x.** Football alone: 0.0099 against 0.0590, or 6.0x.
Crypto alone: 0.0007 against 0.0470, or 71x, because the memory arm learns there
is nothing there worth paying for and very nearly stops.

The flat arm fails in the opposite direction and is worth keeping for exactly
that reason: one global reliability number is dragged toward zero by crypto, so
it stops buying in football too, ending on the worst Brier of the three while
spending almost nothing. Domain-scoped memory is not a nicety; a single number
cannot hold two different lessons.

## NOT proven: forecast quality

The Brier and accuracy columns need a real model and one has not run. The offline
stand-in is a **trust-weighted average**, which is precisely the aggregation that
rewards buying more sources, so it is biased toward the amnesiac by construction.
On the held-out split it reports football Brier 0.6237 for the amnesiac against
0.6309 for sibyl.

That number must not be quoted. It measures the stand-in, not the forecaster. The
real prompt instructs the model to prefer higher-trust sources and explicitly not
to split the difference mechanically, which is a different aggregation rule.

`bench/run.py` refuses to write `proof/BENCH.md` from an offline run for this
reason. **The chart is blocked on `ANTHROPIC_API_KEY` and nothing else.**

## Tuning discipline

The stopping and exploration rules were tuned on the FIT split only (season 2324
plus the earlier 60% of the crypto series) and then run once on the held-out
split. Adaptive exploration was adopted because a domain with eight sources
cannot be learned one purchase at a time: while a domain is cold the agent spends
up to 60% of its budget probing, tapering to 25% once three sources are
established.

On the fit split that change put sibyl ahead of the amnesiac on football Brier
(0.5887 against 0.6040) at 4.7x less spend. On the held-out split it did not
reproduce with the stand-in forecaster. Whether it reproduces with the real model
is exactly the open question, and it will be answered by running the bench, not
by tuning further against the test set.

---

## Provider constraints, measured 2026-08-31

**The Google free tier cannot run this bench.** The binding quota is
`GenerateRequestsPerDayPerProjectPerModel-FreeTier` = **20 requests per day**,
confirmed on both `gemini-3.7-flash` (served via `gemini-flash-latest`) and
`gemini-2.5-flash`. It is the free tier, not a quirk of one preview model. With
four usable model ids that is about 80 calls a day against the 900 a 300-event
three-arm run needs. The per-minute limit of 5 is a red herring; the daily cap is
what stops you.

A key that works is not the same as a key that can finish the job, and the
difference only shows up partway through a run. Anything long enough to matter
needs a paid endpoint.

**What works instead**

| route | shape | cost for ~900 calls |
|---|---|---|
| AionLabs | OpenAI-compatible, `https://api.aionlabs.ai/v1` | ~$1 at $0.80/M in, $1.60/M out |
| Anthropic | native | comparable on `claude-haiku-4-5` |
| Google paid | removes the daily cap | comparable |

`agent/forecast.py` now speaks all three. Anything that is not a `claude-*` or
`gemini-*` id routes to an OpenAI-compatible endpoint when
`RECEIPTS_OPENAI_BASE_URL` is set, so unknown ids are refused rather than guessed.

**A caveat on model choice.** AionLabs' `aion-2.0` and `aion-3.0` are described
by their own catalogue as tuned for immersive roleplaying and storytelling, and
"strong at introducing tension, crises and conflict". That is the opposite of
what a calibration league wants: stay near the base rate when the evidence is
thin, and do not dramatise. It may still be fine, since DeepSeek V3.2 and GLM
underneath are capable general models, but it is a risk to the QUALITY half of
the chart and should be checked on a small run before a long one.

The SELECTION half is unaffected by any of this. Selection never touches the
forecaster.

### AionLabs, measured 2026-08-31

Free tier is **20,000 tokens per day**. A forecast call runs about 650 prompt plus
400 completion tokens, so roughly **19 calls a day** — the same wall as Google,
reached by a different route. Both providers advertise a per-minute rate that is
not the binding constraint; the daily cap is.

| tier | req/min | tokens/min | daily tokens |
|---|---|---|---|
| Free | 15 | 20,000 | 20,000 |
| 1 (any credit top-up) | 50 | 1,000,000 | **Unlimited** |

**Any top-up unlocks tier 1.** At $0.80/M prompt and $1.60/M completion, a
300-event three-arm run (900 calls) costs about **$1**, and 1,000 events about
$3.50. The models emit reasoning tokens you are billed for: a request returning
`{"ok": true}` used 98 completion tokens, so completion cost is higher than the
visible answer suggests.

**The general lesson, now hit twice.** Check the DAILY token or request cap before
planning a run, not the per-minute rate. A key that authenticates and answers a
smoke test tells you nothing about whether it can finish 900 calls.
