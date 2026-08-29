"""Regression gate: the refactor into evidence/signals.py must not move a number.

Re-measures skill per informant per domain using the SAME held-out splits, and
diffs against the table committed in proof/DOMAINS.md. Any drift is a failure.
"""
import sys, pathlib, re
from collections import defaultdict
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corpus"))

from build import load as load_football, add_prior_form
import crypto as C
from evidence import signals as S

def brier(p, a, outs): return sum((p[i]-(1.0 if o==a else 0.0))**2 for i,o in enumerate(outs))

fb = [r for r in add_prior_form(load_football()) if r["ready"]]
cr = C.load_events(); cut = int(len(cr)*0.6)
fb_fit  = [r for r in fb if r["season"] == "2324"]
fb_test = [r for r in fb if r["season"] != "2324"]
cr_fit, cr_test = cr[:cut], cr[cut:]
S.fit_all(fb_fit, cr_fit)

stats, basec = defaultdict(lambda: defaultdict(lambda: {"n":0,"br":0.0})), defaultdict(lambda: defaultdict(int))
for r in fb_test + cr_test:
    outs = S.outcomes_for(r["domain"])
    basec[r["domain"]][r["result"]] += 1
    for iid, inf in S.INFORMANTS.items():
        if not inf.covers(r["domain"]): continue
        p = inf.predict(r)
        if p is None: continue
        s = stats[iid][r["domain"]]; s["n"] += 1; s["br"] += brier(p, r["result"], outs)

BASE = {}
for d, c in basec.items():
    tot = sum(c.values()); outs = S.outcomes_for(d)
    prior = [c[o]/tot for o in outs]
    BASE[d] = sum((c[o]/tot)*brier(prior, o, outs) for o in outs)

fresh = {}
for iid, per in stats.items():
    for d, s in per.items():
        if s["n"]: fresh[(iid, d)] = round(1 - (s["br"]/s["n"])/BASE[d], 3)

# parse the committed table out of proof/DOMAINS.md
text = (ROOT / "proof/DOMAINS.md").read_text()
block = text.split("SKILL by informant and domain")[1].split("BEST BUY")[0]
lines = [l for l in block.splitlines() if l.strip()]
hdr = next(l for l in lines if "informant" in l and "price" in l)
cols = hdr.split()[2:]
colmap = {"cr": None}
domains = []
i = 0
while i < len(cols):
    if cols[i] == "cr":
        domains.append("crypto_" + cols[i+1]); i += 2
    else:
        domains.append({"championshi": "championship"}.get(cols[i], cols[i])); i += 1

recorded = {}
for l in lines:
    parts = l.split()
    if len(parts) < 3 or parts[0] in ("informant",) or set(l.strip()) == {"-"}: continue
    iid = parts[0]
    if iid not in S.INFORMANTS: continue
    vals = parts[2:]
    for d, v in zip(domains, vals):
        if v != "--": recorded[(iid, d)] = float(v)

bad = []
for k, v in recorded.items():
    got = fresh.get(k)
    if got is None or abs(got - v) > 0.0005:
        bad.append((k, v, got))

print(f"compared {len(recorded)} recorded (informant, domain) skill figures")
if bad:
    print("DRIFT DETECTED - the refactor changed the measurements:")
    for (iid, d), was, now in bad:
        print(f"  {iid:14} {d:14} proof={was:+.3f} now={now if now is None else f'{now:+.3f}'}")
    raise SystemExit(1)
print("all identical. evidence/signals.py reproduces proof/DOMAINS.md exactly.")
