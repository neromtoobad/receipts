# Domain-scoped reliability, measured across two event families

Generated 2026-08-29T01:11:34Z.

Football: 6,462 matches, 6 leagues, seasons 2023-24 to 2025-26 (football-data.co.uk).
Fit on 2324, measured on 2425 + 2526.
Crypto: 18,000 hourly candles + 6,000 funding points, BTC/ETH/SOL (Binance public API),
horizons 1h and 24h. Fit on the earlier 60% of the series, measured on the later 40%.

Skill = 1 - brier / base-rate-brier. Zero means the informant knows nothing beyond
how often each outcome occurs, and it is comparable across three-way and binary markets.

```
SKILL by informant and domain.  1 - brier/base-rate-brier.  0 = knows nothing.
negative = actively worse than knowing only how often each outcome happens.

informant         price   bundesliga  championshi          epl       laliga       ligue1       seriea        cr 1h       cr 24h
-------------------------------------------------------------------------------------------------------------------------------
sharp_desk       0.0450        0.116        0.043        0.089        0.114        0.101        0.132           --           --
calcio_desk      0.0120        0.063       -0.005        0.044        0.044        0.041        0.132           --           --
boot_room        0.0120        0.116       -0.007        0.018        0.031        0.014        0.039           --           --
iberian_desk     0.0120        0.028       -0.007        0.018        0.113        0.014        0.039           --           --
hexagon_desk     0.0120        0.028       -0.007        0.018        0.031        0.100        0.039           --           --
island_desk      0.0120        0.063        0.043        0.089        0.044        0.041        0.055           --           --
formline         0.0030        0.028       -0.007        0.018        0.031        0.014        0.039        0.002       -0.007
chalk_desk       0.0200       -0.002       -0.001       -0.001       -0.002       -0.002       -0.004       -0.000       -0.005
voldesk          0.0090           --           --           --           --           --           --       -0.000       -0.005
flowdesk         0.0150           --           --           --           --           --           --       -0.001       -0.005

BEST BUY PER DOMAIN (skill per USDC, informants with positive skill only)
  bundesliga     boot_room      skill=+0.116 price=0.0120  (7 of 10 worth buying)
  championship   island_desk    skill=+0.043 price=0.0120  (2 of 10 worth buying)
  epl            island_desk    skill=+0.089 price=0.0120  (7 of 10 worth buying)
  laliga         formline       skill=+0.031 price=0.0030  (7 of 10 worth buying)
  ligue1         hexagon_desk   skill=+0.100 price=0.0120  (7 of 10 worth buying)
  seriea         formline       skill=+0.039 price=0.0030  (7 of 10 worth buying)
  crypto_1h      formline       skill=+0.002 price=0.0030  (1 of 10 worth buying)
  crypto_24h     NOTHING IS WORTH BUYING - every informant has zero or negative skill
```

## The league simulation

```
budget 0.060/forecast   football 4460 unseen  crypto 14255 unseen

--- football ---
arm                       accuracy    brier  bought  spend/call  total spend
----------------------------------------------------------------------------
amnesiac (no memory)        48.5%    0.618     4.5      0.0579       258.03
flat json log               45.7%    0.638     1.0      0.0030        13.38
sibyl (domain-scoped)       51.8%    0.594     1.6      0.0139        61.93

--- crypto ---
arm                       accuracy    brier  bought  spend/call  total spend
----------------------------------------------------------------------------
amnesiac (no memory)        50.6%    0.500     4.0      0.0470       669.99
flat json log               51.4%    0.500     2.0      0.0120       171.06
sibyl (domain-scoped)       48.4%    0.500     0.0      0.0000         0.00

--- ALL ---
arm                       accuracy    brier  bought  spend/call  total spend
----------------------------------------------------------------------------
amnesiac (no memory)        50.1%    0.528     4.1      0.0496       928.01
flat json log               50.0%    0.533     1.8      0.0099       184.44
sibyl (domain-scoped)       49.2%    0.522     0.4      0.0033        61.93

DELETION TEST, whole league
  accuracy   49.2% -> 50.1%   (-0.9 pts)
  brier      0.5224 -> 0.5280
  spend      $61.93 -> $928.01 over 18715 forecasts (15.0x)
  vs flat log (memory without domain scoping): $184.44 (3.0x)

  crypto alone: sibyl buys 0.00 informants/forecast and spends $0.00;
                amnesiac buys 4.00 and spends $669.99.
```
