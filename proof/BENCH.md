# The deletion test

`1000` resolved events, budget 0.060 USDC per forecast, model `qwen2.5:7b-instruct` (served as `qwen2.5:7b-instruct`), prompt sha `f01839e731d42294`.

Same corpus, same budget, same informants at the same prices, same prompt, same model. The only difference between arms is what each is allowed to remember.

**n = 1000**.

| arm | accuracy | brier | bought/call | spend/call | total spend |
|---|---|---|---|---|---|
| sibyl | 48.9% | 0.5658 | 0.55 | 0.0053 | $5.28 |
| flat | 49.0% | 0.5697 | 0.08 | 0.0009 | $0.89 |
| amnesiac | 49.2% | 0.5664 | 4.50 | 0.0530 | $53.00 |

## Deletion test

- informants bought: **0.55 -> 4.50** per forecast
- spend: **0.0053 -> 0.0530 USDC** (10.0x)
- brier: **0.5658 -> 0.5664**

Generated in 9977.2s.
