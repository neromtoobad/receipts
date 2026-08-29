"""The deletion test, previewed on the corpus before a line of the build exists.

Memory does two jobs, and both are modelled here:
  1. WHICH informants to buy, under a budget.
  2. HOW MUCH to believe each one, per domain.
An amnesiac fails at both: no basis to choose, so it spends the budget; no basis
to weight, so it averages everything it bought, including the garbage.

Rankings are learned on season 2324 and measured on 2425 + 2526. No arm is ever
scored on data it learned from.
"""
import random
from collections import defaultdict
from build import load, add_prior_form
from informants import INFORMANTS, OUTCOMES

BUDGET, FIT_SEASON, BASE = 0.060, "2324", 0.667
random.seed(7)

def brier(p, a): return sum((p[i]-(1.0 if o==a else 0.0))**2 for i,o in enumerate(OUTCOMES))

rows = [r for r in add_prior_form(load()) if r["ready"]]
fit  = [r for r in rows if r["season"] == FIT_SEASON]
test = [r for r in rows if r["season"] != FIT_SEASON]
for _, sig in INFORMANTS.values(): sig.fit(fit)

dom, glob = defaultdict(lambda: [0.0,0]), defaultdict(lambda: [0.0,0])
for r in fit:
    for n, (_, sig) in INFORMANTS.items():
        p = sig.predict(r)
        if p is None: continue
        b = brier(p, r["result"])
        d = dom[(n, r["domain"])]; d[0]+=b; d[1]+=1
        g = glob[n]; g[0]+=b; g[1]+=1
DOMAIN = {k: v[0]/v[1] for k,v in dom.items() if v[1]}
GLOBAL = {k: v[0]/v[1] for k,v in glob.items() if v[1]}

def weight(b):
    """Remembered reliability -> how much to believe it. Zero if worse than guessing."""
    return max(0.0, BASE - b) ** 2

def buy_learned(r, table, key):
    """Buy by remembered edge per dollar; stop when the next one adds nothing."""
    scored = []
    for n in INFORMANTS:
        b = table.get(key(n, r))
        if b is None: continue
        scored.append((n, weight(b)/INFORMANTS[n][0], b))
    scored.sort(key=lambda x: -x[1])
    chosen, spent, best = [], 0.0, None
    for n, vpd, b in scored:
        price = INFORMANTS[n][0]
        if spent + price > BUDGET: continue
        # stopping rule: only pay for something meaningfully better than what we hold
        if best is not None and b > best - 0.005: continue
        chosen.append((n, weight(b))); spent += price
        best = b if best is None else min(best, b)
    return chosen, spent

def arm_sibyl(r):  return buy_learned(r, DOMAIN, lambda n, r: (n, r["domain"]))
def arm_flat(r):   return buy_learned(r, GLOBAL, lambda n, r: n)

def arm_amnesiac(r):
    """No memory: no basis to rank, no basis to stop, no basis to weight."""
    names = list(INFORMANTS); random.shuffle(names)
    chosen, spent = [], 0.0
    for n in names:
        price = INFORMANTS[n][0]
        if spent + price <= BUDGET:
            chosen.append((n, 1.0)); spent += price   # equal weight: it cannot tell them apart
    return chosen, spent

ARMS = {"amnesiac (no memory)": arm_amnesiac, "flat json log": arm_flat,
        "sibyl (domain-scoped)": arm_sibyl}
res = {k: {"n":0,"hit":0,"br":0.0,"spend":0.0,"bought":defaultdict(int),"cnt":0} for k in ARMS}

for r in test:
    for label, fn in ARMS.items():
        chosen, spent = fn(r)
        parts = [(INFORMANTS[n][1].predict(r), w) for n, w in chosen]
        parts = [(p, w) for p, w in parts if p and w > 0]
        if not parts: continue
        tw = sum(w for _, w in parts)
        avg = [sum(p[i]*w for p, w in parts)/tw for i in range(3)]
        pick = OUTCOMES[max(range(3), key=lambda i: avg[i])]
        s = res[label]
        s["n"]+=1; s["hit"]+= (pick==r["result"]); s["br"]+=brier(avg, r["result"])
        s["spend"]+=spent; s["cnt"]+=len(chosen)
        for n,_ in chosen: s["bought"][n]+=1

print(f"budget {BUDGET:.3f} USDC/forecast   everything costs "
      f"{sum(p for p,_ in INFORMANTS.values()):.4f}   n={len(test)} unseen matches\n")
hdr=f"{'arm':24}{'accuracy':>10}{'brier':>9}{'bought':>8}{'spend/call':>12}{'900 calls':>11}"
print(hdr); print("-"*len(hdr))
for label in ARMS:
    s=res[label]; n=s["n"]; sp=s["spend"]/n
    print(f"{label:24}{s['hit']/n:>9.1%}{s['br']/n:>9.3f}{s['cnt']/n:>8.1f}{sp:>12.4f}{sp*900:>10.2f}")

print("\nwhat each arm buys (share of forecasts)")
names=list(INFORMANTS)
print(f"{'arm':24}"+"".join(f"{n.split('_')[0][:8]:>10}" for n in names))
for label in ARMS:
    s=res[label]
    print(f"{label:24}"+"".join(f"{s['bought'][n]/s['n']:>10.0%}" for n in names))

a,b=res["amnesiac (no memory)"],res["sibyl (domain-scoped)"]
sa,sb=a["spend"]/a["n"],b["spend"]/b["n"]
print(f"\nDELETION TEST")
print(f"  accuracy {b['hit']/b['n']:.1%} -> {a['hit']/a['n']:.1%}   ({(b['hit']/b['n']-a['hit']/a['n'])*100:+.1f} pts)")
print(f"  brier    {b['br']/b['n']:.3f} -> {a['br']/a['n']:.3f}")
print(f"  spend    {sb:.4f} -> {sa:.4f} USDC/forecast   ({sa/sb:.1f}x more expensive)")
print(f"  over 900 forecasts: ${sb*900:.2f} -> ${sa*900:.2f}")
