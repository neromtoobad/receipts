# The Sibyl Memory film, in Remotion

1:49, 1920x1080, narrated in the Jasper preset voice. Motion graphics over
real screenshots of the live board, real excerpts from `agent/memory.py` and
`agent/sources.py`, and the measured figures from `proof/BENCH.md`.

Every number on screen is one a viewer can check. 1,166 calls / 805 resolved /
2,010 informants bought / 18.50 USDC is the export of 2026-09-09 07:55Z, and
$5.28 against $53.00 at 0.5658 vs 0.5664 Brier is the 1,000-event deletion test.

## Rebuild it

```sh
npm install
node capture.mjs        # fresh full-page shots of the live site into public/
cp vo/*.wav public/vo/  # the narration
npx remotion render src/index.ts Receipts out/RECEIPTS_sibyl_memory_vo.mp4 --crf=18
npx remotion studio     # to scrub it
```

`capture.mjs` drives the Chrome already on the machine through puppeteer-core, so
there is no second browser download. Re-run it after every republish, or the film
quotes a board that no longer says that.

## The cut

| in | scene | the line |
|---|---|---|
| 0:00 | title | Six A.I. pundits, forecasting real markets. One model, one prompt, one budget. |
| 0:07 | the board | Everything they have done is on the board. Eleven hundred and sixty-six calls. Eight hundred and five resolved. Two thousand and ten informants bought, for eighteen and a half USDC of real money. |
| 0:22 | buy · call · die · remember | Every forecast is its own process. It boots empty, reads its map in forty-two milliseconds, pays for evidence on Base, forecasts, and dies. Only Sibyl Memory crosses that boundary. |
| 0:39 | five tiers | The memory is five tiers in one file. Warm is the one that matters: reliability per informant, and per domain. That is the map the agent spends against. |
| 0:52 | the code | One set entity call is the whole edge. Prove yourself three times, and you join the map. Delete the memory, and the same code has no basis to choose. So it buys everything, and never stops. |
| 1:09 | the trust map | Nobody declared any of this. Green is trust earned. Red is a source measured worse than guessing. And it is scoped per domain, because skill in football says nothing about crypto. |
| 1:23 | the deletion test | So we deleted the memory a thousand times, and measured. Five dollars twenty-eight with it. Fifty-three dollars without. Same forecast quality. Ten times the money. |
| 1:37 | onchain | Every claim here is a hash or a measurement. Settled on Base, paid in USDC, and standing on Sibyl Memory. |

## The narration

Generated with seed_audio against the preset voice
`a7b8abe9-47f1-553e-a9df-87945a7e5bc8` (Jasper), one clip per scene, kept in
`vo/`. He reads at about two words a second, so `Video.tsx` plays the clips at
`VO_RATE = 1.12` — pitch preserved, a shade over two and a quarter. Scene lengths
in `S` are derived from the measured clip lengths, so changing a line means
re-measuring that clip and re-timing its scene.

The earlier take in the cloned `neromtoobad` voice
(`caec4873-074b-4be8-8db0-b314f3618dae`) is kept in `vo_neromtoobad/`. To go back
to it, copy those over `public/vo/`, set `VO_RATE = 1.2`, and re-derive `S`; that
read is slower, and the film comes out at 1:47.

No music. The mix is voice only, over a silent picture.
