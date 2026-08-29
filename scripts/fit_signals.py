"""Fit the informants and persist the calibration.

Two modes, and the difference matters:

  --holdout    fit on season 2324 and the earlier 60% of the crypto series, the
               exact splits used to produce proof/DOMAINS.md. Used to prove the
               refactor did not move a single number.
  (default)    fit on the whole historical corpus. This is what the live service
               loads, because throwing away two seasons of calibration for no
               reason would be silly. The held-out figures remain the honest
               estimate of what these informants are worth.
"""
import sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corpus"))

from build import load as load_football, add_prior_form
import crypto as C
from evidence import signals as S

holdout = "--holdout" in sys.argv

fb = [r for r in add_prior_form(load_football()) if r["ready"]]
cr = C.load_events()
if holdout:
    fb_fit = [r for r in fb if r["season"] == "2324"]
    cr_fit = cr[:int(len(cr) * 0.6)]
else:
    fb_fit, cr_fit = fb, cr

S.fit_all(fb_fit, cr_fit)
out = S.FITTED_PATH if not holdout else S.FITTED_PATH.with_name("fitted_holdout.json")
S.save_fitted(out)

# Base rates per domain, from the same rows. A forecaster with no evidence must
# have something honest to fall back to, and it must not be invented at runtime.
import json as _json
from collections import Counter as _Counter
rates = {}
for rows in (fb_fit, cr_fit):
    for d in {r["domain"] for r in rows}:
        c = _Counter(r["result"] for r in rows if r["domain"] == d)
        tot = sum(c.values())
        rates[d] = {o: round(n / tot, 4) for o, n in c.items()}
(out.parent / "base_rates.json").write_text(_json.dumps(rates, indent=1))
print(f"base rates for {len(rates)} domains -> base_rates.json")
print(f"fitted on {len(fb_fit)} football rows and {len(cr_fit)} crypto rows "
      f"({'held-out splits' if holdout else 'full corpus'}) -> {out.name}")
