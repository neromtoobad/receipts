# The deletion test

`1000` resolved events, budget 0.060 USDC per forecast, model `qwen2.5:7b-instruct` (served as `qwen2.5:7b-instruct`), prompt sha `33495af058e60a30`.

Same corpus, same budget, same informants at the same prices, same prompt, same model. The only difference between arms is what each is allowed to remember.

**n = 1000**.

| arm | accuracy | brier | bought/call | spend/call | total spend |
|---|---|---|---|---|---|
| sibyl | 48.7% | 0.5653 | 0.56 | 0.0053 | $5.34 |
| flat | 48.8% | 0.5691 | 0.10 | 0.0010 | $1.04 |
| amnesiac | 49.0% | 0.5667 | 4.50 | 0.0530 | $53.00 |

## Deletion test

- informants bought: **0.56 -> 4.50** per forecast
- spend: **0.0053 -> 0.0530 USDC** (9.9x)
- brier: **0.5653 -> 0.5667**

Generated in 9846.7s.

## How to read this

**The spend result is decisive and model-independent.** An arm learns from what
each *source* said against the outcome, never from its own forecast, so selection
is settled entirely by memory. 9.9x overall, 6.0x on football, and 67x on crypto
where the memory arm learns there is nothing worth paying for and nearly stops.

**The quality result is a tie, and should be reported as one.** The domain-scoped
arm is ahead on Brier in every split, and the direction is consistent:

| split | sibyl | amnesiac | delta | n |
|---|---|---|---|---|
| overall | 0.5653 | 0.5667 | +0.0014 | 1000 |
| football | 0.6335 | 0.6343 | +0.0008 | 500 |
| crypto | 0.4972 | 0.4991 | +0.0019 | 500 |

The largest margin is 0.0019. That is too small to call a quality win at this n,
and accuracy actually favours the amnesiac by 0.3 points, which is noise in the
other direction. The honest claim is **the same forecast quality for a tenth of
the cost**, not a better forecast.

That is also the claim the corpus supports and the one the pitch makes. A memory
layer that made an agent cheaper without making it worse is the whole argument;
inflating a 0.0014 Brier delta into a quality win would be the kind of thing that
falls apart under one question from a judge.

## Provenance

Model `qwen2.5:7b-instruct` running locally through Ollama, 3,000 calls over
2h44m, zero failed requests. Both free API tiers we tried were unusable for a run
this size: Google caps at 20 requests per day per model, AionLabs at 20,000 tokens
per day. Running locally also means a judge can reproduce this exactly, with
`ollama pull qwen2.5:7b-instruct` and one command, without an API key.

Informants were calibrated on season 2023-24 and the earlier 60% of the crypto
series. Every event scored here comes from data they have never seen. The
selection and exploration rules were tuned on that same fit split and run once on
the held-out split; see `proof/BENCH_STATUS.md`.
