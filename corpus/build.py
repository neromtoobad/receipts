"""Build the resolved-event corpus from football-data.co.uk.

Integrity rules, because a fabricated spread is a disqualification:
  1. Every feature an informant sees is computed ONLY from matches strictly
     earlier in time than the one being forecast. No post-match column is ever
     read for the match itself.
  2. Informants that need calibration are fitted on season 2324 and measured on
     2425 + 2526. Fit and test never overlap.
  3. Nothing about reliability is assigned. It is measured.
"""
import csv, glob, os
from collections import defaultdict, deque
from datetime import datetime

RAW = os.path.join(os.path.dirname(__file__), "raw")
LEAGUES = {"E0": "epl", "E1": "championship", "D1": "bundesliga",
           "I1": "seriea", "SP1": "laliga", "F1": "ligue1"}

def f(row, key):
    v = (row.get(key) or "").strip()
    try: return float(v)
    except ValueError: return None

def load():
    rows = []
    for path in sorted(glob.glob(os.path.join(RAW, "*.csv"))):
        season, lg = os.path.basename(path)[:-4].split("_")
        with open(path, newline="", encoding="utf-8-sig") as fh:
            for r in csv.DictReader(fh):
                if not (r.get("Date") and r.get("FTR")): continue
                d = None
                for fmt in ("%d/%m/%Y", "%d/%m/%y"):
                    try: d = datetime.strptime(r["Date"].strip(), fmt); break
                    except ValueError: pass
                if d is None: continue
                rows.append({
                    "season": season, "domain": LEAGUES[lg], "date": d,
                    "home": r["HomeTeam"], "away": r["AwayTeam"], "result": r["FTR"],
                    "fthg": f(r,"FTHG"), "ftag": f(r,"FTAG"),
                    "hst": f(r,"HST"), "ast": f(r,"AST"),
                    # pre-match odds only
                    "ps": (f(r,"PSH"), f(r,"PSD"), f(r,"PSA")),
                    "b365": (f(r,"B365H"), f(r,"B365D"), f(r,"B365A")),
                    "avg": (f(r,"AvgH"), f(r,"AvgD"), f(r,"AvgA")),
                    "max": (f(r,"MaxH"), f(r,"MaxD"), f(r,"MaxA")),
                })
    rows.sort(key=lambda r: (r["date"], r["domain"], r["home"]))
    return rows

def add_prior_form(rows, window=5, burn_in=5):
    """Rolling features from STRICTLY EARLIER matches. Written before the row is read."""
    pts, sot_for, sot_against, played = (defaultdict(lambda: deque(maxlen=window)) for _ in range(3)), None, None, defaultdict(int)
    pts = defaultdict(lambda: deque(maxlen=window))
    sf = defaultdict(lambda: deque(maxlen=window))
    sa = defaultdict(lambda: deque(maxlen=window))
    out = []
    for r in rows:
        h, a = (r["domain"], r["home"]), (r["domain"], r["away"])
        r["ready"] = played[h] >= burn_in and played[a] >= burn_in
        if r["ready"]:
            r["pts_diff"] = sum(pts[h])/len(pts[h]) - sum(pts[a])/len(pts[a])
            r["sot_diff"] = ((sum(sf[h])/len(sf[h]) - sum(sa[h])/len(sa[h]))
                             - (sum(sf[a])/len(sf[a]) - sum(sa[a])/len(sa[a])))
        # now, AFTER using history, fold this match in
        if r["result"] == "H": ph, pa = 3, 0
        elif r["result"] == "A": ph, pa = 0, 3
        else: ph, pa = 1, 1
        pts[h].append(ph); pts[a].append(pa)
        if r["hst"] is not None and r["ast"] is not None:
            sf[h].append(r["hst"]); sa[h].append(r["ast"])
            sf[a].append(r["ast"]); sa[a].append(r["hst"])
        played[h] += 1; played[a] += 1
        out.append(r)
    return out

if __name__ == "__main__":
    rows = add_prior_form(load())
    ready = [r for r in rows if r["ready"]]
    print(f"matches loaded : {len(rows)}")
    print(f"past burn-in   : {len(ready)}")
    from collections import Counter
    print("by season      :", dict(Counter(r["season"] for r in ready)))
    print("by domain      :", dict(Counter(r["domain"] for r in ready)))
    print("result mix     :", dict(Counter(r["result"] for r in ready)))
    for k, label in (("ps","pinnacle"),("max","bestprice"),("avg","consensus")):
        cov = sum(1 for r in ready if all(v for v in r[k]))/len(ready)
        print(f"odds coverage {label:10}: {cov:.1%}")
