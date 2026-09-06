# The deletion test

`1000` resolved events, budget 0.060 USDC per forecast, model `qwen2.5:7b-instruct` (served as `qwen2.5:7b-instruct`), prompt sha `f01839e731d42294`.

Same corpus, same budget, same informants at the same prices, same prompt, same model. The only difference between arms is what each is allowed to remember.

**n = 1000**.

| arm | accuracy | brier | bought/call | spend/call | total spend |
|---|---|---|---|---|---|
| sibyl | 48.9% | 0.5658 | 0.55 | 0.0053 | $5.28 |
| flat | 49.0% | 0.5697 | 0.08 | 0.0009 | $0.89 |
| amnesiac | 49.2% | 0.5664 | 4.50 | 0.0530 | $53.00 |

## By domain

Read off the console output of the same run. The writer now emits this section
itself, so the next run publishes it without a hand edit.

**football** (500 events)

| arm | bought/call | spend/call | total | brier |
|---|---|---|---|---|
| sibyl | 0.97 | 0.0099 | $4.95 | 0.6345 |
| flat | 0.14 | 0.0015 | $0.77 | 0.6420 |
| amnesiac | 5.00 | 0.0590 | $29.50 | 0.6350 |

Deletion test on spend, football only: **6x**.

**crypto** (500 events)

| arm | bought/call | spend/call | total | brier |
|---|---|---|---|---|
| sibyl | 0.13 | 0.0007 | $0.33 | 0.4972 |
| flat | 0.02 | 0.0003 | $0.13 | 0.4975 |
| amnesiac | 4.00 | 0.0470 | $23.50 | 0.4979 |

Deletion test on spend, crypto only: **71x** — the memory arm measured that no
informant beats the base rate on price direction and very nearly stopped buying.
Crypto brier is ~0.497 against a 0.5 coin flip for every arm, which is the point:
there is nothing there to learn, and only the arm that can remember finds that out.

## Deletion test

- informants bought: **0.55 -> 4.50** per forecast
- spend: **0.0053 -> 0.0530 USDC** (10.0x)
- brier: **0.5658 -> 0.5664**

Generated in 9977.2s.
