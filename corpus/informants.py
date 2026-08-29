"""Six informants.

INTEGRITY RULE: we never write down a reliability number. We write down what
DATA each informant has access to, and what it CHARGES. Both are real product
properties of a data vendor. Reliability is then measured, never assigned.

Two levers create the spread, and both are honest:
  * Beat. A desk has deep coverage in its region and thin coverage outside it.
    Outside its beat it falls back to a weaker public signal. Real vendors are
    exactly like this.
  * Price. What a vendor charges is its own commercial decision and has no
    obligation to track its quality. Discovering that price and quality are
    uncorrelated is the whole lesson the pundits have to learn.
"""
from collections import defaultdict
import math

OUTCOMES = ("H", "D", "A")

def devig(odds):
    if not odds or any(o is None or o <= 1.0 for o in odds): return None
    raw = [1.0/o for o in odds]; s = sum(raw)
    return [p/s for p in raw]

class Quantised:
    """Non-parametric calibration, fitted on the fit season only."""
    def __init__(self, key, bins=7): self.key, self.bins, self.edges, self.table, self.prior = key, bins, [], {}, None
    def fit(self, rows):
        vals = sorted(r[self.key] for r in rows if r.get(self.key) is not None)
        if not vals: return self
        self.edges = [vals[int(len(vals)*i/self.bins)] for i in range(1, self.bins)]
        buckets = defaultdict(lambda: defaultdict(int)); n = defaultdict(int)
        for r in rows:
            n[r["result"]] += 1
            v = r.get(self.key)
            if v is not None: buckets[self._b(v)][r["result"]] += 1
        tot = sum(n.values()); self.prior = [n[o]/tot for o in OUTCOMES]
        for b, c in buckets.items():
            t = sum(c.values()); w = t/(t+25)
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

class Fixed:
    def __init__(self): self.p = None
    def fit(self, rows):
        n = defaultdict(int)
        for r in rows: n[r["result"]] += 1
        t = sum(n.values()); self.p = [n[o]/t for o in OUTCOMES]; return self
    def predict(self, r): return list(self.p)

class Book:
    def __init__(self, key): self.key = key
    def fit(self, rows): return self
    def predict(self, r): return devig(r[self.key])

class Desk:
    """A regional desk. Market-grade data inside its beat, a thin public signal
    outside it. Coverage, not quality, is what we declare."""
    def __init__(self, beat, inside_key, outside):
        self.beat, self.inside, self.outside = set(beat), Book(inside_key), outside
    def fit(self, rows):
        self.inside.fit(rows); self.outside.fit(rows); return self
    def predict(self, r):
        if r["domain"] in self.beat:
            p = self.inside.predict(r)
            if p: return p
        return self.outside.predict(r)

# id -> (price USDC/call, signal). Price is a commercial decision, not a quality claim.
# Regional desks carry market-grade data inside their beat and a thin public
# signal outside it. Which desk covers which league is NOT advertised anywhere:
# it can only be learned by paying and watching what resolves.
INFORMANTS = {
    "iberian_desk":  (0.0120, Desk({"laliga"},              "avg", Quantised("pts_diff"))),
    "island_desk":   (0.0120, Desk({"epl", "championship"}, "avg", Quantised("sot_diff"))),
    "boot_room":     (0.0120, Desk({"bundesliga"},          "avg", Quantised("pts_diff"))),
    "calcio_desk":   (0.0120, Desk({"seriea"},              "avg", Quantised("sot_diff"))),
    "hexagon_desk":  (0.0120, Desk({"ligue1"},              "avg", Quantised("pts_diff"))),
    "sharp_desk":    (0.0450, Book("max")),     # best price across the book. dear.
    "chalk_desk":    (0.0200, Fixed()),         # the loud man. mid price, knows nothing
    "formline":      (0.0030, Quantised("pts_diff")),   # cheap, weak, honest
}
