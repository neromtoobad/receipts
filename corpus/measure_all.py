"""One reliability table across genuinely different event types.

Scores are reported as SKILL: 1 - brier/brier_of_the_base_rate. Zero means the
informant knows nothing beyond how often each outcome happens. This makes a
three-way football market and a binary crypto market directly comparable, which
is the only way to show that the SAME informant is worth paying for in one
domain and worthless in another.
"""
from collections import defaultdict
from build import load as load_football, add_prior_form
import informants as F
import crypto as C

def brier(p, actual, outs): return sum((p[i]-(1.0 if o==actual else 0.0))**2 for i,o in enumerate(outs))

# ---------- football: fit 2324, measure 2425+2526 ----------
fb = [r for r in add_prior_form(load_football()) if r["ready"]]
fb_fit  = [r for r in fb if r["season"] == "2324"]
fb_test = [r for r in fb if r["season"] != "2324"]
for _, sig in F.INFORMANTS.values(): sig.fit(fb_fit)

# ---------- crypto: fit earlier 60%, measure later 40% ----------
cr = C.load_events()
cut = int(len(cr)*0.6)
cr_fit, cr_test = cr[:cut], cr[cut:]

CRYPTO_SIGNALS = {
    "flowdesk":  (0.0150, C.BinQuant("funding")),   # derivatives positioning. crypto only.
    "voldesk":   (0.0090, C.BinQuant("volr")),      # volume/vol regime. crypto only.
    "formline":  (0.0030, C.BinQuant("mom6")),      # the SAME cheap momentum idea as football form
    "chalk_desk":(0.0200, C.BinFixed()),            # the loud man, in both domains
}
for _, sig in CRYPTO_SIGNALS.values(): sig.fit(cr_fit)

stats = defaultdict(lambda: defaultdict(lambda: {"n":0,"br":0.0,"hit":0}))
base  = defaultdict(lambda: defaultdict(int))

for r in fb_test:
    base[r["domain"]][r["result"]] += 1
    for name, (_, sig) in F.INFORMANTS.items():
        p = sig.predict(r)
        if p is None: continue
        s = stats[name][r["domain"]]
        s["n"] += 1; s["br"] += brier(p, r["result"], F.OUTCOMES)
        s["hit"] += (F.OUTCOMES[max(range(3), key=lambda i: p[i])] == r["result"])
for r in cr_test:
    base[r["domain"]][r["result"]] += 1
    for name, (_, sig) in CRYPTO_SIGNALS.items():
        p = sig.predict(r)
        if p is None: continue
        s = stats[name][r["domain"]]
        s["n"] += 1; s["br"] += brier(p, r["result"], C.OUTCOMES)
        s["hit"] += (C.OUTCOMES[max(range(2), key=lambda i: p[i])] == r["result"])

BASE_BR = {}
for d, c in base.items():
    tot = sum(c.values()); outs = F.OUTCOMES if d.startswith(("epl","cham","bund","lali","ligu","seri")) else C.OUTCOMES
    prior = [c[o]/tot for o in outs]
    BASE_BR[d] = sum((c[o]/tot)*brier(prior, o, outs) for o in outs)

PRICES = {**{k: v[0] for k, v in F.INFORMANTS.items()},
          **{k: v[0] for k, v in CRYPTO_SIGNALS.items()}}
football_domains = sorted(d for d in base if not d.startswith("crypto"))
crypto_domains   = sorted(d for d in base if d.startswith("crypto"))
domains = football_domains + crypto_domains

print("SKILL by informant and domain.  1 - brier/base-rate-brier.  0 = knows nothing.")
print("negative = actively worse than knowing only how often each outcome happens.\n")
names = sorted(PRICES, key=lambda n: -max((1-stats[n][d]["br"]/stats[n][d]["n"]/BASE_BR[d])
                                          for d in domains if stats[n][d]["n"]))
w = 13
print(f"{'informant':15}{'price':>8}" + "".join(f"{d.replace('crypto_','cr ')[:11]:>{w}}" for d in domains))
print("-"*(23+w*len(domains)))
for n in names:
    row = f"{n:15}{PRICES[n]:>8.4f}"
    for d in domains:
        s = stats[n][d]
        row += f"{'--':>{w}}" if not s["n"] else f"{1-(s['br']/s['n'])/BASE_BR[d]:>{w}.3f}"
    print(row)

print("\nBEST BUY PER DOMAIN (skill per USDC, informants with positive skill only)")
for d in domains:
    ranked = []
    for n in names:
        s = stats[n][d]
        if not s["n"]: continue
        sk = 1-(s["br"]/s["n"])/BASE_BR[d]
        if sk > 0: ranked.append((sk/PRICES[n], n, sk, PRICES[n]))
    ranked.sort(reverse=True)
    if not ranked:
        print(f"  {d:14} NOTHING IS WORTH BUYING - every informant has zero or negative skill")
    else:
        vpd, n, sk, pr = ranked[0]
        print(f"  {d:14} {n:14} skill={sk:+.3f} price={pr:.4f}  ({len(ranked)} of {len(names)} worth buying)")
