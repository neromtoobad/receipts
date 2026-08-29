"""The deletion test across BOTH event families.

Football rewards knowing which desk covers which league. Crypto rewards knowing
that nothing is worth buying at all. No single global ranking can express both,
which is exactly what the domain-scoped arm is for.
"""
import random
from collections import defaultdict
from build import load as load_football, add_prior_form
import informants as F
import crypto as C

BUDGET = 0.060
random.seed(7)

def brier(p, a, outs): return sum((p[i]-(1.0 if o==a else 0.0))**2 for i,o in enumerate(outs))

fb = [r for r in add_prior_form(load_football()) if r["ready"]]
fb_fit  = [r for r in fb if r["season"] == "2324"]
fb_test = [r for r in fb if r["season"] != "2324"]
for _, sig in F.INFORMANTS.values(): sig.fit(fb_fit)

cr = C.load_events(); cut = int(len(cr)*0.6)
cr_fit, cr_test = cr[:cut], cr[cut:]
CRYPTO = {"flowdesk": (0.0150, C.BinQuant("funding")), "voldesk": (0.0090, C.BinQuant("volr")),
          "formline": (0.0030, C.BinQuant("mom6")),    "chalk_desk": (0.0200, C.BinFixed())}
for _, sig in CRYPTO.values(): sig.fit(cr_fit)

SIG   = {"football": {n: s for n, (_, s) in F.INFORMANTS.items()},
         "crypto":   {n: s for n, (_, s) in CRYPTO.items()}}
PRICE = {**{n: p for n, (p, _) in F.INFORMANTS.items()}, **{n: p for n, (p, _) in CRYPTO.items()}}
OUTS  = {"football": F.OUTCOMES, "crypto": C.OUTCOMES}
fam   = lambda r: "crypto" if r["domain"].startswith("crypto") else "football"

# ---- what is learnable from the fit split, per domain and globally ----
dom, glob, basec = defaultdict(lambda:[0.0,0]), defaultdict(lambda:[0.0,0]), defaultdict(lambda: defaultdict(int))
for r in fb_fit + cr_fit:
    f = fam(r); basec[r["domain"]][r["result"]] += 1
    for n, sig in SIG[f].items():
        p = sig.predict(r)
        if p is None: continue
        b = brier(p, r["result"], OUTS[f])
        d = dom[(n, r["domain"])]; d[0]+=b; d[1]+=1
        g = glob[n]; g[0]+=b; g[1]+=1
BASE = {}
for d, c in basec.items():
    tot = sum(c.values()); outs = OUTS["crypto"] if d.startswith("crypto") else OUTS["football"]
    prior = [c[o]/tot for o in outs]
    BASE[d] = sum((c[o]/tot)*brier(prior, o, outs) for o in outs)
DOMAIN_SKILL = {k: 1-(v[0]/v[1])/BASE[k[1]] for k, v in dom.items() if v[1]}
GLOBAL_SKILL = {n: 1-(v[0]/v[1])/(sum(BASE.values())/len(BASE)) for n, v in glob.items() if v[1]}

MIN_SKILL = 0.005   # below this an informant is noise and must not be paid for

def learned(r, lookup):
    scored = []
    for n in SIG[fam(r)]:
        sk = lookup(n, r)
        if sk is None or sk < MIN_SKILL: continue
        scored.append((sk/PRICE[n], n, sk))
    scored.sort(reverse=True)
    chosen, spent, best = [], 0.0, 0.0
    for _, n, sk in scored:
        if spent + PRICE[n] > BUDGET: continue
        if chosen and sk <= best + 0.01: continue      # stop: adds nothing over what we hold
        chosen.append((n, sk)); spent += PRICE[n]; best = max(best, sk)
    return chosen, spent

arm_sibyl = lambda r: learned(r, lambda n, r: DOMAIN_SKILL.get((n, r["domain"])))
arm_flat  = lambda r: learned(r, lambda n, r: GLOBAL_SKILL.get(n))
def arm_amnesiac(r):
    names = list(SIG[fam(r)]); random.shuffle(names)
    chosen, spent = [], 0.0
    for n in names:
        if spent + PRICE[n] <= BUDGET: chosen.append((n, 1.0)); spent += PRICE[n]
    return chosen, spent

ARMS = {"amnesiac (no memory)": arm_amnesiac, "flat json log": arm_flat, "sibyl (domain-scoped)": arm_sibyl}
res = {k: defaultdict(lambda: {"n":0,"hit":0,"br":0.0,"spend":0.0,"cnt":0}) for k in ARMS}

for r in fb_test + cr_test:
    f = fam(r); outs = OUTS[f]
    for label, fn in ARMS.items():
        chosen, spent = fn(r)
        parts = [(SIG[f][n].predict(r), max(sk, 0.0)) for n, sk in chosen]
        parts = [(p, w) for p, w in parts if p]
        tw = sum(w for _, w in parts)
        if not parts or tw <= 0:                      # bought nothing usable: fall back to the base rate
            tot = sum(basec[r["domain"]].values())
            avg = [basec[r["domain"]][o]/tot for o in outs]
        else:
            avg = [sum(p[i]*w for p, w in parts)/tw for i in range(len(outs))]
        pick = outs[max(range(len(outs)), key=lambda i: avg[i])]
        for bucket in (res[label][f], res[label]["ALL"]):
            bucket["n"]+=1; bucket["hit"]+=(pick==r["result"])
            bucket["br"]+=brier(avg, r["result"], outs); bucket["spend"]+=spent; bucket["cnt"]+=len(chosen)

print(f"budget {BUDGET:.3f}/forecast   football {len(fb_test)} unseen  crypto {len(cr_test)} unseen\n")
for scope in ("football", "crypto", "ALL"):
    print(f"--- {scope} ---")
    hdr=f"{'arm':24}{'accuracy':>10}{'brier':>9}{'bought':>8}{'spend/call':>12}{'total spend':>13}"
    print(hdr); print("-"*len(hdr))
    for label in ARMS:
        s=res[label][scope]; n=s["n"]; sp=s["spend"]/n
        print(f"{label:24}{s['hit']/n:>9.1%}{s['br']/n:>9.3f}{s['cnt']/n:>8.1f}{sp:>12.4f}{s['spend']:>13.2f}")
    print()

a,b = res["amnesiac (no memory)"]["ALL"], res["sibyl (domain-scoped)"]["ALL"]
f_ = res["flat json log"]["ALL"]
print("DELETION TEST, whole league")
print(f"  accuracy   {b['hit']/b['n']:.1%} -> {a['hit']/a['n']:.1%}   ({(b['hit']/b['n']-a['hit']/a['n'])*100:+.1f} pts)")
print(f"  brier      {b['br']/b['n']:.4f} -> {a['br']/a['n']:.4f}")
print(f"  spend      ${b['spend']:.2f} -> ${a['spend']:.2f} over {b['n']} forecasts ({a['spend']/b['spend']:.1f}x)")
print(f"  vs flat log (memory without domain scoping): ${f_['spend']:.2f} ({f_['spend']/b['spend']:.1f}x)")
cs, ca = res["sibyl (domain-scoped)"]["crypto"], res["amnesiac (no memory)"]["crypto"]
print(f"\n  crypto alone: sibyl buys {cs['cnt']/cs['n']:.2f} informants/forecast and spends ${cs['spend']:.2f};")
print(f"                amnesiac buys {ca['cnt']/ca['n']:.2f} and spends ${ca['spend']:.2f}.")
