# Measured informant spread and deletion test

Generated 2026-08-28T23:47:34Z from 6,462 real matches (football-data.co.uk),
6 leagues x 3 seasons. Calibrated on season 2324, measured on 2425 + 2526 (4,460 unseen).

```
fit on 2324: 2002 matches   measured on 2425+2526: 4460 matches

OVERALL  (2425 + 2526)
informant          price coverage  accuracy    brier  logloss       ROI
-----------------------------------------------------------------------
pinnacle_desk     0.0450    74.4%     52.2%    0.584    0.980     -3.6%
island_desk       0.0120   100.0%     49.4%    0.613    1.023     -4.5%
calcio_desk       0.0120   100.0%     48.8%    0.618    1.029     -4.5%
iberian_desk      0.0120   100.0%     46.8%    0.629    1.045     -8.5%
boot_room         0.0120   100.0%     46.7%    0.630    1.047     -8.3%
hexagon_desk      0.0120   100.0%     46.8%    0.630    1.047     -8.4%
formline          0.0030   100.0%     45.7%    0.638    1.058     -9.6%
chalk_desk        0.0200   100.0%     43.1%    0.651    1.075     -9.4%

PER DOMAIN  (brier, lower is better - this is what the agent must learn)
informant          bundesliga  championship           epl        laliga        ligue1        seriea
---------------------------------------------------------------------------------------------------
pinnacle_desk           0.576         0.623         0.584         0.563         0.568         0.571
island_desk             0.612         0.622         0.595         0.612         0.613         0.622
calcio_desk             0.612         0.654         0.625         0.612         0.613         0.572
iberian_desk            0.634         0.655         0.642         0.568         0.630         0.633
boot_room               0.577         0.655         0.642         0.620         0.630         0.633
hexagon_desk            0.634         0.655         0.642         0.620         0.575         0.633
formline                0.634         0.655         0.642         0.620         0.630         0.633
chalk_desk              0.654         0.651         0.654         0.642         0.641         0.661

BEST INFORMANT PER DOMAIN (by brier)
  bundesliga     best=pinnacle_desk (0.576)  worst=chalk_desk    (0.654)  spread=0.079
  championship   best=island_desk   (0.622)  worst=formline      (0.655)  spread=0.033
  epl            best=pinnacle_desk (0.584)  worst=chalk_desk    (0.654)  spread=0.070
  laliga         best=pinnacle_desk (0.563)  worst=chalk_desk    (0.642)  spread=0.079
  ligue1         best=pinnacle_desk (0.568)  worst=chalk_desk    (0.641)  spread=0.073
  seriea         best=pinnacle_desk (0.571)  worst=chalk_desk    (0.661)  spread=0.090
```

```
budget 0.060 USDC/forecast   everything costs 0.1280   n=4460 unseen matches

arm                       accuracy    brier  bought  spend/call  900 calls
--------------------------------------------------------------------------
amnesiac (no memory)        48.3%    0.619     4.5      0.0579     52.07
flat json log               50.7%    0.601     3.0      0.0600     54.00
sibyl (domain-scoped)       51.8%    0.592     1.6      0.0139     12.50

what each arm buys (share of forecasts)
arm                        iberian    island      boot    calcio   hexagon  pinnacle     chalk  formline
amnesiac (no memory)           55%       54%       56%       55%       55%       26%       50%       95%
flat json log                   0%        0%        0%      100%        0%      100%        0%      100%
sibyl (domain-scoped)          16%       40%       13%       16%       13%        0%        0%       63%

DELETION TEST
  accuracy 51.8% -> 48.3%   (+3.5 pts)
  brier    0.592 -> 0.619
  spend    0.0139 -> 0.0579 USDC/forecast   (4.2x more expensive)
  over 900 forecasts: $12.50 -> $52.07
```
