# Twitter Space brief — RECEIPTS

Numbers as of 2026-09-05. Say the ones in **bold**; skip the rest if the room
is moving fast.

---

## If you only get one sentence

> Six AI agents forecast real markets, pay real money for every piece of evidence
> they use, and get killed after every forecast — so the only thing separating
> them is what they wrote to memory.

## If you get thirty seconds

> Every agent you build wakes up knowing nothing. Give one a budget and a list of
> paid data sources and it'll buy all of them, every time, forever — not because
> that's right, but because it has no way to know which source was ever right.
>
> So I built a league where six agents forecast real football and crypto, and
> every tip they use is a real USDC payment on Base. Same model, same prompt,
> same budget. Nobody tells them which sources are any good — they find out by
> paying and being wrong. And I kill the process after every single forecast, so
> the only thing that carries over is what it wrote to memory.
>
> Then I deleted the memory and measured it. **Ten times the spend, for a
> forecast that scores the same.**

## The one number to repeat

> **$5.28 with memory. $53.00 without. Same forecast quality.**
> A thousand held-out events, same model, same prompt, same budget.

If you say nothing else, say that. Repeat it at the end.

---

## The demo moment, spoken

> An agent reads the trust map it earned by paying for sources and watching them
> resolve. It buys **one informant out of eight** and skips seven. It forecasts.
> Then the process dies — and I show you the operating system confirming there's
> no such process.
>
> A brand new process starts. Shares nothing but a database file. It reads back
> what the dead one wrote, including its own record on that exact fixture — it's
> called this match before and done worse than its average.
>
> Then the same market with memory deleted. It buys **five of eight**, and every
> single line says *"no basis to choose."* That's not a bug. Without a record
> there genuinely is no basis.

---

## Live numbers (re-check before you go on)

- **1,130 forecasts, 759 resolved**, 18.12 USDC actually spent, 1,962 informant
  purchases
- **216 source/domain cells scored — 119 written off as worse than guessing**
- 1.6 cents per forecast
- Ten informants priced 0.003 to 0.045 USDC, no advertised accuracy

---

## Questions you'll get, and how to answer

**"So it's a betting bot?"**
> No — nobody's betting. It's a testbed for a problem every agent has: when
> information costs money, how does an agent learn what's worth buying? Markets
> are just the scoreboard, because they tell you unambiguously whether you were
> right.

**"Are the forecasts actually good?"** ← *the one that can catch you out*
> Honestly, no, and I report it as a tie rather than dressing it up. About 49%
> accuracy, and on crypto it's a coin flip. But that was never the claim. The
> claim is the same forecast for a tenth of the money — and the crypto result is
> the most interesting thing on the board, because the agent measured that no
> source beats the base rate there and nearly stopped buying entirely. **71x less
> spend in crypto.** That's the right call, and an agent with no memory can never
> reach it.

**"Couldn't you just use a JSON file / a database / a long context window?"**
> A file is fine until you need it scoped, decayed, searchable, and shared
> between six agents. I ran that arm — memory with no domain scoping. It
> under-buys and scores worse: 0.5697 Brier against 0.5658. One global number per
> source can't hold "good at Serie A, useless at crypto." And a context window
> doesn't survive the process dying, which is the whole setup.

**"What's actually on-chain?"**
> Every informant call returns HTTP 402 until it's paid. The x402 settlements are
> on Base Sepolia — and the nice detail is the agent holds no ETH at all: it
> signs an EIP-3009 authorization and the facilitator pays the gas. The agents
> also hire each other through Virtuals ACP on Base **mainnet** — one posts a
> job, funds escrow, another delivers a forecast, escrow releases.

**"Why kill the process every time? Isn't that artificial?"**
> It's the opposite — it's what production looks like. Serverless functions,
> cron jobs, queue workers: they all boot, act, and die. The long-lived chat
> session is the artificial case. Killing it makes the memory claim falsifiable,
> because nothing can secretly carry state.

**"How do you know memory caused the saving and not something else?"**
> Because the only thing that changes between arms is memory. Same corpus, same
> budget, same informants at the same prices, same prompt hash, same local model.
> The harness is in the repo — `python -m bench.run --runs 1000`, no API key
> needed, it runs on a local 7B model.

**"Does it work with more agents / other domains?"**
> The mechanism is domain-agnostic — it learns per (source, domain) pair, and
> football and crypto behave completely differently, which is the point. Six
> agents is what fits a hackathon; nothing about it is capped at six.

**"What surprised you?"**
> That crypto has no signal at all. I expected the memory arm to find the good
> crypto source. Instead it found there isn't one, and the correct move is to buy
> nothing — a null result that turned into the strongest argument in the project.

**"What would you do next?"**
> Let agents price their own opinions instead of a fixed rate — a real market in
> reputations. Right now peer opinions have a flat price, which is the least
> interesting possible answer.

---

## Two things to avoid saying

1. **Don't claim the forecasts are good.** They aren't, you'd be caught, and the
   cost result doesn't need it.
2. **Don't say "semantic search"** — Sibyl has zero embeddings, recall is
   full-text. Someone technical will ask.

## If you're asked something you don't know

> "I'd have to check — it's all in the repo, and every number on the site is read
> straight out of the memory store."

That's a better answer than a guess, and it's true.
