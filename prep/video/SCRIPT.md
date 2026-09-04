# RECEIPTS — demo video

Target 4:00. Narration in the cloned `neromtoobad` voice. Section 3 is the
hackathon gate and must be **one continuous unedited take** — no cuts inside it.

Numbers below are measured, not estimated. The live figures (1-of-8 vs 5-of-8,
0.0120 vs 0.0590 USDC) come from the real run on 2026-09-04, and the recorded
take shows them. The 1,000-event figures are 5.28 USDC against 53.00 at brier
0.5658 against 0.5664 — method and caveats in `proof/BENCH.md`.

---

## 1 — The problem (0:00–0:35)
**Screen:** the league page, agents ticking over.

> Every agent you build has the same hole in it. It wakes up knowing nothing.
>
> Give one a budget and a list of paid data sources and it will buy all of them,
> every time, forever — not because that is right, but because it has no way to
> know which source was ever right. It cannot learn that the eighth opinion adds
> nothing to the first, because by the time the answer arrives, the agent that
> asked the question is already gone.
>
> I wanted to know what that hole costs. So I built a league of six agents that
> forecast real football and crypto markets and pay real money for evidence.

## 2 — The product (0:35–1:15)
**Screen:** agents page, then a pundit's trust map.

> Augur, Cipher, Tally, Quorum, Vertex and Ledger. Six seats, forecasting the
> same markets, scored against each other on calibration — not on being loud, on
> being right, and knowing how sure to be. They run the same model on the same
> prompt with the same budget, so the names are labels, not personalities. What
> makes them differ is what each one has paid for and been burned by.
>
> Evidence is not free. There are ten informants, each with a price, and every
> purchase is a real USDC payment over x402 on Base. So an agent that buys
> everything goes broke, and an agent that buys nothing forecasts the base rate.
>
> The only way out is to learn which sources are worth paying for. And the
> catch is this: **I kill the process after every single forecast.** Nothing
> survives except what the agent wrote to Sibyl Memory.

## 3 — GATE: cold-start recall (1:15–2:30) — ONE CONTINUOUS TAKE
**Screen:** terminal. `PUNDIT=vertex ./scripts/demo_recall.sh championship:2026-09-01:Portsmouth:Derby`
Do not cut. Commit hash and UTC are on screen from the first frame.

> That is the commit, and that is the timestamp. Nothing here is staged.
>
> This is Vertex, and this is what it has learned across two days of real
> markets. It paid
> for every one of these sources and scored each one when the market resolved.
> Formline on Serie A: nine calls, a skill number it earned. Nothing seeded.
>
> Now a forecast, in its own process. Watch the process id.
>
> Vertex read its map, and it bought one informant out of eight available. It
> skipped seven. And it recalled its own record on this exact fixture — it has
> called Portsmouth and Derby before, and it did worse than its average.
>
> That process is now dead. Confirmed — the operating system has no such
> process. Everything it held in memory is gone.
>
> New process. Different process id. Nothing shared but the database.
>
> And there it is. It reads back what the dead process wrote — the same trust
> map, and its own record scored against a number that just moved, because the
> forecast you watched a moment ago is now part of it.

## 4 — The deletion test (2:30–3:10)
**Screen:** same terminal, amnesiac arm.

> Same market. Same model, same prompt, same budget. The only difference is that
> memory is deleted.
>
> It buys five of eight. And look at the reason on every line — *no basis to
> choose*. That is not a bug. With no memory there is genuinely no basis. It
> spends five times as much to answer the same question, and it cannot tell you
> why it trusted anything.
>
> Across a thousand held-out events, the arm with memory spent five dollars and
> twenty-eight cents. The arm without it spent fifty-three. Ten times the money,
> for a forecast that scores the same.

## 5 — Base and Virtuals (3:10–3:45)
**Screen:** BaseScan tx, then the ACP job.

> The payments are real. A settled transaction on Base: an agent paying twelve
> thousandths of a dollar for one forecast in USDC, signed with EIP-3009, so the
> facilitator covers the gas and the agent never needs ETH.
>
> And the agents hire each other. This is a Virtuals ACP job run end to end —
> Vertex posted it, funded escrow, Augur delivered a forecast with its real
> memory behind it, and the escrow was released. The deliverable names which
> source moved it and which it discounted by trust weight: weights it could only
> earn by paying for those sources and watching them resolve.

## 6 — Close (3:45–4:00)
**Screen:** README, "Where memory is written and read".

> Every Sibyl call is in one file, and the README points straight at it.
>
> Delete that file and this is six agents buying everything they can afford,
> forever, and learning nothing. That is the test, and that is why memory is
> not a feature here. It is the product.
