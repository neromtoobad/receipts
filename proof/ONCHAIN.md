# Onchain proof — Base Sepolia

## First settled x402 evidence purchase

An agent bought one informant's forecast and paid for it in USDC. Verified on
chain, not taken from the API's word for it.

| | |
|---|---|
| tx | [`0xb0cc50dbf1530884b0789f15b0498632bb50d6a74b74336b58659fefd864eebc`](https://sepolia.basescan.org/tx/0xb0cc50dbf1530884b0789f15b0498632bb50d6a74b74336b58659fefd864eebc) |
| status | SUCCESS |
| block | 46195402 |
| network | Base Sepolia, `eip155:84532` |
| contract | USDC `0x036CbD53842c5426634e7929541eC2318f3dCF7e` |
| transfer | **0.012 USDC** |
| from | `0x6806868abf17A46CE00026f40D0e64983089CF87` (pundit_1) |
| to | `0xf6Df2aA761C63ACf1d49EE69C457b9eF23EdCc49` (evidence service) |
| what was bought | `island_desk` on `epl:2026-08-28:Crystal_Palace:Man_City` |
| what came back | H 0.1955, D 0.2391, A 0.5654 |

## The detail that matters

**Gas was paid by `0xd407e409e34e0b9afb99ecceb609bdbcd5e7f1bf`, the x402
facilitator — not by the agent.** pundit_1's ETH balance is unchanged at 0.05
across the transaction; only its USDC moved, 20.0000 to 19.9880.

That is the EIP-3009 `transferWithAuthorization` path working exactly as the
phase 0 research predicted: the agent signs an authorization, the facilitator
broadcasts it and covers the gas, and the agent needs USDC and no ETH. The Circle
Gateway deposit step that cost us time in LONGSHOT is Arc-specific and genuinely
does not apply on Base.

## Reproducing it

```sh
./scripts/new_wallet.sh          # derive the wallets, seed to .env
# fund pundit_1 with USDC at https://faucet.circle.com (Base Sepolia)
./scripts/check_funds.sh         # confirm it landed
./scripts/settle_once.sh         # buy one informant, print the tx hash
```
