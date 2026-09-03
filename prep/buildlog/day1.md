# Day 1 — the premise and the first receipt

Every figure below is verified. Nothing here quotes the deletion-test number,
because that is being re-measured and day 6 is where it belongs anyway.

---

## X / Twitter thread

**1/**

Most AI agents are amnesiacs. New session, blank slate, and every lesson from
last week is gone.

So for the @sibylcap hackathon I built the meanest version of that problem I
could think of.

RECEIPTS: six AI pundits who have to pay for information — and who get their
memory wiped after every single call.

**2/**

The setup.

Six agents. Same model, same prompt, same budget. Identical in every way.

They forecast real football matches and real crypto markets.

The only thing that can ever separate them is what each one has learned.

**3/**

There is no free information.

Ten informants sell tips — bookmaker odds, form data, funding rates. Each has a
price. The dearest costs 15× the cheapest.

Every single tip is bought with real USDC over x402 on @base.

No one tells them which informants are any good.

**4/**

Here is the cruel part.

After every forecast, the process dies. Killed. Context gone.

Boot the next one and it knows nothing — except what it wrote to memory.

That is what makes this a memory test and not a context-window test.

**5/**

So each agent has to work out, at its own expense, which informants are worth
paying for.

The only way to learn that a source is rubbish is to buy from it, be wrong, and
remember.

Currently on the board: 640 calls, 486 resolved, 9.83 USDC of evidence bought.

**6/**

Two days in, they have written off 89 informant-domain pairings as worse than
guessing — and earned trust in 102.

One agent has learned a desk is excellent on Serie A and useless everywhere else.

Nobody told it that. It paid to find out.

**7/**

First proof on chain. An agent bought a tip and paid for it:

0xb0cc50dbf1530884b0789f15b0498632bb50d6a74b74336b58659fefd864eebc

0.012 USDC on Base. Gas paid by the facilitator, so the agent needs USDC and no
ETH — EIP-3009 doing exactly what it says.

**8/**

Live board, updating as they learn:
https://neromtoobad.github.io/receipts/

Code, all of it:
https://github.com/neromtoobad/receipts

Six more days. Tomorrow: what happens when one agent decides another agent is
worth paying for.

@sibylcap @base @virtuals_io

---

## Discord write-up

**RECEIPTS — day 1: six pundits who pay for their own information**

The problem I wanted to attack: an agent that forgets between sessions starts
from zero every time, and a human pays the difference.

So the build is six AI pundits forecasting real matches and real markets. Same
model, same prompt, same budget — genuinely identical. What separates them is
only what each has paid to learn.

**Information costs money.** Ten informants sell tips at prices from 0.003 to
0.045 USDC, bought over x402 on Base. There is no free path to evidence, and
nothing advertises how good it is. The catalogue an agent reads lists prices and
coverage and never a hit rate.

**The process dies after every forecast.** Fresh boot, empty context, and the
only thing that survives is what it wrote to Sibyl Memory. That rule is what
makes this a memory test rather than a long-conversation test — remove it and the
model just remembers naturally.

**What it has to figure out.** Which informants are worth their price, in which
domain. The only route to that is buying, being scored against what actually
happened, and remembering. Two days in: 640 calls, 486 resolved, 9.83 USDC spent,
102 informant-domain pairings earning trust and 89 written off as worse than
guessing.

**Something I did not expect.** In crypto, every single informant measures at or
below zero skill. Funding rates, volume regime, momentum — all noise at these
horizons. So the correct behaviour there is to buy nothing, and an agent with
per-domain memory eventually gets there on its own. An agent with one global
number for each source never can.

First settlement on Base Sepolia:
`0xb0cc50db…64eebc` — 0.012 USDC, block 46195402, gas paid by the facilitator.

Live board: https://neromtoobad.github.io/receipts/
Repo: https://github.com/neromtoobad/receipts

Happy to go into the memory schema if anyone is curious — five tiers, promotion
after three resolved observations, decay, and archival that is recoverable.

---

## Checks before posting

- [ ] tag `@sibylcap`, `@base`, `@virtuals_io`
- [ ] tx hash resolves on Basescan Sepolia
- [ ] every number matches the live board at the time of posting
- [ ] no deletion-test figure quoted (it is being re-measured; day 6 owns it)
