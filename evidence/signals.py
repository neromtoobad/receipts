"""The informants, as one implementation used by the backtest, the bench and the
live service alike.

This file exists because two code paths would eventually disagree, and the whole
project rests on the claim that what was measured on held-out seasons is what
runs in the league. Fitted parameters are persisted to evidence/fitted.json by
scripts/fit_signals.py so the live service and the bench use identical
calibration rather than refitting on whatever they happen to have seen.

Nothing here encodes a reliability. Each informant declares what DATA it reads
and its beat. What that is worth is measured elsewhere and learned by the agents.
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

FOOTBALL_OUTCOMES = ("H", "D", "A")
CRYPTO_OUTCOMES = ("UP", "DOWN")
FOOTBALL_DOMAINS = ("epl", "championship", "bundesliga", "seriea", "laliga", "ligue1")
CRYPTO_DOMAINS = ("crypto_1h", "crypto_24h")

FITTED_PATH = Path(__file__).resolve().parent / "fitted.json"


def family(domain: str) -> str:
    return "crypto" if domain.startswith("crypto") else "football"


def outcomes_for(domain: str) -> tuple[str, ...]:
    return CRYPTO_OUTCOMES if family(domain) == "crypto" else FOOTBALL_OUTCOMES


def devig(odds) -> list[float] | None:
    if not odds or any(o is None or o <= 1.0 for o in odds):
        return None
    raw = [1.0 / o for o in odds]
    s = sum(raw)
    return [p / s for p in raw]


# ---------------------------------------------------------------- signals

class Book:
    """Reads a bookmaker odds triple straight off the row and de-vigs it."""
    kind = "book"

    def __init__(self, key: str, outs=FOOTBALL_OUTCOMES):
        self.key, self.outs = key, outs

    def fit(self, rows): return self
    def predict(self, r): return devig(r.get(self.key))
    def dump(self): return {"kind": self.kind, "key": self.key}


class Quantised:
    """Non-parametric calibration of one scalar. Bins are cut on the fit split and
    thin bins are shrunk toward the prior so a sparse bin cannot fake precision."""
    kind = "quantised"

    def __init__(self, key: str, bins: int = 7, outs=FOOTBALL_OUTCOMES, shrink: int = 25):
        self.key, self.bins, self.outs, self.shrink = key, bins, outs, shrink
        self.edges: list[float] = []
        self.table: dict[int, list[float]] = {}
        self.prior: list[float] | None = None

    def fit(self, rows):
        vals = sorted(r[self.key] for r in rows if r.get(self.key) is not None)
        if not vals:
            return self
        self.edges = [vals[int(len(vals) * i / self.bins)] for i in range(1, self.bins)]
        counts, n = defaultdict(lambda: defaultdict(int)), defaultdict(int)
        for r in rows:
            n[r["result"]] += 1
            v = r.get(self.key)
            if v is not None:
                counts[self._b(v)][r["result"]] += 1
        tot = sum(n.values())
        self.prior = [n[o] / tot for o in self.outs]
        for b, c in counts.items():
            t = sum(c.values())
            w = t / (t + self.shrink)
            self.table[b] = [w * (c[o] / t) + (1 - w) * self.prior[i]
                             for i, o in enumerate(self.outs)]
        return self

    def _b(self, v):
        b = 0
        for e in self.edges:
            if v > e:
                b += 1
        return b

    def predict(self, r):
        v = r.get(self.key)
        if v is None or not self.table:
            return None
        return self.table.get(self._b(v), self.prior)

    def dump(self):
        return {"kind": self.kind, "key": self.key, "bins": self.bins,
                "outs": list(self.outs), "shrink": self.shrink, "edges": self.edges,
                "table": {str(k): v for k, v in self.table.items()}, "prior": self.prior}

    def load(self, d):
        self.edges = d["edges"]
        self.table = {int(k): v for k, v in d["table"].items()}
        self.prior = d["prior"]
        return self


class Fixed:
    """A flat prior. The loud man at the viewing centre: same answer every time."""
    kind = "fixed"

    def __init__(self, outs=FOOTBALL_OUTCOMES):
        self.outs, self.p = outs, None

    def fit(self, rows):
        n = defaultdict(int)
        for r in rows:
            n[r["result"]] += 1
        t = sum(n.values())
        if t:
            self.p = [n[o] / t for o in self.outs]
        return self

    def predict(self, r): return list(self.p) if self.p else None
    def dump(self): return {"kind": self.kind, "outs": list(self.outs), "p": self.p}
    def load(self, d):
        self.p = d["p"]
        return self


class Desk:
    """A regional desk. Market-grade data inside its beat, a thin public signal
    outside it. Coverage is a real product property; quality is not declared."""
    kind = "desk"

    def __init__(self, beat, inside: Book, outside):
        self.beat, self.inside, self.outside = set(beat), inside, outside

    def fit(self, rows):
        self.inside.fit(rows)
        self.outside.fit(rows)
        return self

    def predict(self, r):
        if r.get("domain") in self.beat:
            p = self.inside.predict(r)
            if p:
                return p
        return self.outside.predict(r)

    def dump(self):
        return {"kind": self.kind, "beat": sorted(self.beat),
                "inside": self.inside.dump(), "outside": self.outside.dump()}

    def load(self, d):
        self.outside.load(d["outside"])
        return self


# ---------------------------------------------------------------- informants

class Informant:
    """One purchasable source. It may cover one event family or both."""

    def __init__(self, iid: str, price: float, football=None, crypto=None):
        self.id, self.price, self.football, self.crypto = iid, price, football, crypto

    def covers(self, domain: str) -> bool:
        return getattr(self, family(domain)) is not None

    def predict(self, row) -> list[float] | None:
        sig = getattr(self, family(row["domain"]))
        return sig.predict(row) if sig else None

    def payload(self, row) -> dict[str, Any] | None:
        """What the buyer actually receives for the money."""
        p = self.predict(row)
        if p is None:
            return None
        outs = outcomes_for(row["domain"])
        return {o: round(v, 4) for o, v in zip(outs, p)}


def _build() -> dict[str, Informant]:
    f_form = lambda: Quantised("pts_diff")
    f_shot = lambda: Quantised("sot_diff")
    mk_desk = lambda beat, outside: Desk(beat, Book("avg"), outside)
    return {i.id: i for i in [
        Informant("sharp_desk",   0.0450, football=Book("max")),
        Informant("island_desk",  0.0120, football=mk_desk({"epl", "championship"}, f_shot())),
        Informant("iberian_desk", 0.0120, football=mk_desk({"laliga"}, f_form())),
        Informant("boot_room",    0.0120, football=mk_desk({"bundesliga"}, f_form())),
        Informant("calcio_desk",  0.0120, football=mk_desk({"seriea"}, f_shot())),
        Informant("hexagon_desk", 0.0120, football=mk_desk({"ligue1"}, f_form())),
        Informant("chalk_desk",   0.0200, football=Fixed(),
                  crypto=Fixed(outs=CRYPTO_OUTCOMES)),
        Informant("formline",     0.0030, football=f_form(),
                  crypto=Quantised("mom6", outs=CRYPTO_OUTCOMES, shrink=50)),
        Informant("flowdesk",     0.0150,
                  crypto=Quantised("funding", outs=CRYPTO_OUTCOMES, shrink=50)),
        Informant("voldesk",      0.0090,
                  crypto=Quantised("volr", outs=CRYPTO_OUTCOMES, shrink=50)),
    ]}


INFORMANTS: dict[str, Informant] = _build()


def fit_all(football_rows, crypto_rows) -> None:
    for inf in INFORMANTS.values():
        if inf.football:
            inf.football.fit(football_rows)
        if inf.crypto:
            inf.crypto.fit(crypto_rows)


def save_fitted(path: Path = FITTED_PATH) -> None:
    blob = {iid: {"price": i.price,
                  "football": i.football.dump() if i.football else None,
                  "crypto": i.crypto.dump() if i.crypto else None}
            for iid, i in INFORMANTS.items()}
    path.write_text(json.dumps(blob, indent=1))


def load_fitted(path: Path = FITTED_PATH) -> bool:
    """The live service must never refit on whatever it happens to have seen."""
    if not path.exists():
        return False
    blob = json.loads(path.read_text())
    for iid, d in blob.items():
        inf = INFORMANTS.get(iid)
        if not inf:
            continue
        for fam in ("football", "crypto"):
            sig, dd = getattr(inf, fam), d.get(fam)
            if sig is not None and dd is not None and hasattr(sig, "load"):
                sig.load(dd)
    return True
