"""Crypto domain. Binary direction markets, resolved from real Binance candles.

Same integrity rules as football: every feature uses only bars at or before the
decision time, calibration is fitted on the earlier 60% of the series and
measured on the later 40%, and no reliability is ever assigned.
"""
import json, os
from collections import defaultdict

RAW = os.path.join(os.path.dirname(__file__), "raw_crypto")
SYMS = ("BTCUSDT", "ETHUSDT", "SOLUSDT")
OUTCOMES = ("UP", "DOWN")

def load_events(horizons=(1, 24)):
    events = []
    for sym in SYMS:
        k = json.load(open(f"{RAW}/{sym}_1h.json"))
        closes = [(int(r[0]), float(r[4])) for r in k]
        vols   = [float(r[5]) for r in k]
        fund = []
        fp = f"{RAW}/{sym}_funding.json"
        if os.path.exists(fp):
            fund = sorted((int(x["fundingTime"]), float(x["fundingRate"])) for x in json.load(open(fp)))
        fi = 0
        for i in range(48, len(closes)):
            t, c = closes[i]
            # funding strictly at or before t
            while fi + 1 < len(fund) and fund[fi + 1][0] <= t: fi += 1
            fr = fund[fi][1] if fund and fund[fi][0] <= t else None
            rets = [closes[j][1]/closes[j-1][1] - 1.0 for j in range(i-23, i+1)]
            mom6  = closes[i][1]/closes[i-6][1] - 1.0
            mom24 = closes[i][1]/closes[i-24][1] - 1.0
            last  = rets[-1]
            rv    = (sum(x*x for x in rets)/len(rets)) ** 0.5
            volr  = vols[i]/(sum(vols[i-24:i])/24) if sum(vols[i-24:i]) else 1.0
            for h in horizons:
                if i + h >= len(closes): continue
                ev = {"domain": f"crypto_{h}h", "sym": sym, "ts": t, "idx": i,
                      "result": "UP" if closes[i+h][1] > c else "DOWN",
                      "mom6": mom6, "mom24": mom24, "last": last, "rv": rv,
                      "volr": volr, "funding": fr, "ready": True}
                events.append(ev)
    events.sort(key=lambda e: e["ts"])
    return events

class BinQuant:
    """Non-parametric binary calibration on one scalar. Fitted on the fit split only."""
    def __init__(self, key, bins=7):
        self.key, self.bins, self.edges, self.table, self.prior = key, bins, [], {}, None
    def fit(self, rows):
        vals = sorted(r[self.key] for r in rows if r.get(self.key) is not None)
        if not vals: return self
        self.edges = [vals[int(len(vals)*i/self.bins)] for i in range(1, self.bins)]
        n = defaultdict(int); buckets = defaultdict(lambda: defaultdict(int))
        for r in rows:
            n[r["result"]] += 1
            v = r.get(self.key)
            if v is not None: buckets[self._b(v)][r["result"]] += 1
        tot = sum(n.values()); self.prior = [n[o]/tot for o in OUTCOMES]
        for b, c in buckets.items():
            t = sum(c.values()); w = t/(t+50)
            self.table[b] = [w*(c[o]/t) + (1-w)*self.prior[i] for i, o in enumerate(OUTCOMES)]
        return self
    def _b(self, v):
        b = 0
        for e in self.edges:
            if v > e: b += 1
        return b
    def predict(self, r):
        v = r.get(self.key)
        if v is None or not self.table: return None
        return self.table.get(self._b(v), self.prior)

class BinFixed:
    def __init__(self): self.p = None
    def fit(self, rows):
        n = defaultdict(int)
        for r in rows: n[r["result"]] += 1
        t = sum(n.values()); self.p = [n[o]/t for o in OUTCOMES]; return self
    def predict(self, r): return list(self.p)
