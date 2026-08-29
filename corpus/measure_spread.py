"""Measure the real reliability spread. If it is narrow, RECEIPTS has no subject."""
import math
from collections import defaultdict
from build import load, add_prior_form
from informants import INFORMANTS, OUTCOMES

FIT_SEASON = "2324"

def brier(p, actual):
    return sum((p[i] - (1.0 if o == actual else 0.0))**2 for i, o in enumerate(OUTCOMES))

def logloss(p, actual):
    i = OUTCOMES.index(actual)
    return -math.log(max(p[i], 1e-9))

rows = [r for r in add_prior_form(load()) if r["ready"]]
fit  = [r for r in rows if r["season"] == FIT_SEASON]
test = [r for r in rows if r["season"] != FIT_SEASON]
print(f"fit on {FIT_SEASON}: {len(fit)} matches   measured on 2425+2526: {len(test)} matches\n")

for _, sig in INFORMANTS.values(): sig.fit(fit)

stats = defaultdict(lambda: defaultdict(lambda: {"n":0,"hit":0,"br":0.0,"ll":0.0,"stake":0.0,"ret":0.0}))
for r in test:
    for name, (price, sig) in INFORMANTS.items():
        p = sig.predict(r)
        if p is None: continue
        pick = OUTCOMES[max(range(3), key=lambda i: p[i])]
        for bucket in (stats[name]["ALL"], stats[name][r["domain"]]):
            bucket["n"] += 1
            bucket["hit"] += (pick == r["result"])
            bucket["br"] += brier(p, r["result"])
            bucket["ll"] += logloss(p, r["result"])
            price_odds = r["avg"][OUTCOMES.index(pick)]
            if price_odds:
                bucket["stake"] += 1.0
                bucket["ret"] += (price_odds if pick == r["result"] else 0.0)

def line(name, s, price, cov_base):
    n = s["n"]
    if not n: return f"{name:15} {'no coverage':>10}"
    roi = (s["ret"] - s["stake"]) / s["stake"] * 100 if s["stake"] else 0.0
    return (f"{name:15} {price:8.4f} {n/cov_base:8.1%} {s['hit']/n:9.1%} "
            f"{s['br']/n:8.3f} {s['ll']/n:8.3f} {roi:+8.1f}%")

hdr = f"{'informant':15} {'price':>8} {'coverage':>8} {'accuracy':>9} {'brier':>8} {'logloss':>8} {'ROI':>9}"
print("OVERALL  (2425 + 2526)")
print(hdr); print("-"*len(hdr))
order = sorted(INFORMANTS, key=lambda k: stats[k]["ALL"]["br"]/max(stats[k]["ALL"]["n"],1))
for name in order:
    print(line(name, stats[name]["ALL"], INFORMANTS[name][0], len(test)))

print("\nPER DOMAIN  (brier, lower is better - this is what the agent must learn)")
domains = sorted({r["domain"] for r in test})
print(f"{'informant':15}" + "".join(f"{d:>14}" for d in domains))
print("-"*(15+14*len(domains)))
for name in order:
    cells = ""
    for d in domains:
        s = stats[name][d]
        cells += f"{s['br']/s['n']:>14.3f}" if s["n"] else f"{'--':>14}"
    print(f"{name:15}" + cells)

print("\nBEST INFORMANT PER DOMAIN (by brier)")
for d in domains:
    ranked = sorted((n for n in INFORMANTS if stats[n][d]["n"]),
                    key=lambda n: stats[n][d]["br"]/stats[n][d]["n"])
    best, worst = ranked[0], ranked[-1]
    bb = stats[best][d]["br"]/stats[best][d]["n"]
    wb = stats[worst][d]["br"]/stats[worst][d]["n"]
    print(f"  {d:14} best={best:14}({bb:.3f})  worst={worst:14}({wb:.3f})  spread={wb-bb:.3f}")
