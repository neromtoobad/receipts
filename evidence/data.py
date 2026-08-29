"""Live market data, shaped exactly like the corpus rows.

The informants in evidence/signals.py never learn whether a row came from a
2023 CSV or from this morning's fixture list. That is deliberate: one row shape
means one code path, so what was measured on held-out seasons is literally what
runs in the league.

Football form needs five prior matches per team and the season is three weeks
old, so the rolling windows are seeded from the tail of last season. In the
Premier League 17 of 20 teams carry over; the three promoted sides start cold,
which is honest, because a promoted team genuinely has no top-flight form.
"""
from __future__ import annotations

import csv, io, json, time
from collections import defaultdict, deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "evidence" / "_cache"
CACHE.mkdir(exist_ok=True)

FD_BASE = "https://www.football-data.co.uk"
LEAGUES = {"E0": "epl", "E1": "championship", "D1": "bundesliga",
           "I1": "seriea", "SP1": "laliga", "F1": "ligue1"}
PRIOR_SEASON, CURRENT_SEASON = "2526", "2627"
SYMS = ("BTCUSDT", "ETHUSDT", "SOLUSDT")
FORM_WINDOW, BURN_IN = 5, 5


def _num(row, key):
    v = (row.get(key) or "").strip()
    try:
        return float(v)
    except ValueError:
        return None


def _get(url: str, ttl: int = 900, *, fast: bool = False) -> str:
    """Cache on disk. The tick loop runs often and these feeds change slowly.

    `fast` skips the retries and shortens the timeout. Use it for the first
    source in a fallback chain: retrying three times against a DNS that is
    refusing the domain just multiplies the wait before the fallback runs.
    """
    key = CACHE / (url.replace("://", "_").replace("/", "_") + ".txt")
    if key.exists() and time.time() - key.stat().st_mtime < ttl:
        return key.read_text().lstrip("\ufeff")
    attempts = 1 if fast else 3
    last = None
    for attempt in range(attempts):
        try:
            text = httpx.get(url, timeout=5 if fast else 30,
                             headers={"User-Agent": "receipts/0.1"}).text
            break
        except Exception as exc:                  # a DNS blip should not stall a tick
            last = exc
            if attempt + 1 < attempts:
                time.sleep(0.5 * (attempt + 1))
    else:
        raise last
    text = text.lstrip("\ufeff")   # football-data serves a BOM; csv.DictReader keeps it in the first header
    key.write_text(text)
    return text


def _parse_date(s):
    for fmt in ("%d/%m/%Y", "%d/%m/%y"):
        try:
            return datetime.strptime(s.strip(), fmt)
        except ValueError:
            pass
    return None


class FormTracker:
    """Rolling per-team form, fed strictly in chronological order."""

    def __init__(self):
        self.pts = defaultdict(lambda: deque(maxlen=FORM_WINDOW))
        self.sf = defaultdict(lambda: deque(maxlen=FORM_WINDOW))
        self.sa = defaultdict(lambda: deque(maxlen=FORM_WINDOW))
        self.played = defaultdict(int)

    def ingest(self, domain, home, away, result, hst, ast):
        h, a = (domain, home), (domain, away)
        ph, pa = (3, 0) if result == "H" else (0, 3) if result == "A" else (1, 1)
        self.pts[h].append(ph); self.pts[a].append(pa)
        if hst is not None and ast is not None:
            self.sf[h].append(hst); self.sa[h].append(ast)
            self.sf[a].append(ast); self.sa[a].append(hst)
        self.played[h] += 1; self.played[a] += 1

    def features(self, domain, home, away):
        h, a = (domain, home), (domain, away)
        if not (self.pts[h] and self.pts[a]):
            return {"pts_diff": None, "sot_diff": None,
                    "form_ready": False, "matches_seen": (self.played[h], self.played[a])}
        pd = sum(self.pts[h]) / len(self.pts[h]) - sum(self.pts[a]) / len(self.pts[a])
        sd = None
        if self.sf[h] and self.sf[a]:
            sd = ((sum(self.sf[h]) / len(self.sf[h]) - sum(self.sa[h]) / len(self.sa[h]))
                  - (sum(self.sf[a]) / len(self.sf[a]) - sum(self.sa[a]) / len(self.sa[a])))
        return {"pts_diff": pd, "sot_diff": sd,
                "form_ready": min(self.played[h], self.played[a]) >= BURN_IN,
                "matches_seen": (self.played[h], self.played[a])}


def _season_rows(season: str) -> list[dict]:
    rows = []
    for code, domain in LEAGUES.items():
        try:
            text = _get(f"{FD_BASE}/mmz4281/{season}/{code}.csv", ttl=3600)
        except Exception:
            continue
        for r in csv.DictReader(io.StringIO(text)):
            d = _parse_date(r.get("Date", "") or "")
            if not d or not (r.get("FTR") or "").strip():
                continue
            rows.append({"domain": domain, "date": d, "home": r["HomeTeam"], "away": r["AwayTeam"],
                         "result": r["FTR"], "hst": _num(r, "HST"), "ast": _num(r, "AST")})
    rows.sort(key=lambda r: r["date"])
    return rows


def build_tracker() -> FormTracker:
    """Seed from the tail of last season, then this season to date."""
    t = FormTracker()
    prior = _season_rows(PRIOR_SEASON)
    for r in prior[-len(prior) // 4:]:          # the closing quarter is the relevant form
        t.ingest(r["domain"], r["home"], r["away"], r["result"], r["hst"], r["ast"])
    for r in _season_rows(CURRENT_SEASON):
        t.ingest(r["domain"], r["home"], r["away"], r["result"], r["hst"], r["ast"])
    return t


def football_markets() -> list[dict[str, Any]]:
    """Upcoming fixtures with pre-match odds, in corpus row shape."""
    text = _get(f"{FD_BASE}/fixtures.csv", ttl=900)
    tracker = build_tracker()
    out = []
    for r in csv.DictReader(io.StringIO(text)):
        domain = LEAGUES.get((r.get("Div") or "").strip())
        if not domain:
            continue
        d = _parse_date(r.get("Date", "") or "")
        if not d:
            continue
        home, away = r["HomeTeam"], r["AwayTeam"]
        row = {
            "id": f"{domain}:{d:%Y-%m-%d}:{home}:{away}".replace(" ", "_"),
            "domain": domain, "kind": "football",
            "question": f"{home} v {away}, full time result",
            "outcomes": list(("H", "D", "A")),
            "kickoff": d.replace(tzinfo=timezone.utc).isoformat(),
            "home": home, "away": away,
            "avg": (_num(r, "AvgH"), _num(r, "AvgD"), _num(r, "AvgA")),
            "max": (_num(r, "MaxH"), _num(r, "MaxD"), _num(r, "MaxA")),
            "ps":  (_num(r, "PSH"), _num(r, "PSD"), _num(r, "PSA")),
            "result": None,
        }
        row.update(tracker.features(domain, home, away))
        out.append(row)
    return out


def crypto_markets(horizons=(1, 24)) -> list[dict[str, Any]]:
    """Current direction markets, one per symbol per horizon."""
    out = []
    for sym in SYMS:
        from evidence.crypto_source import funding_rate, hourly_closes
        now_ms = int(time.time() * 1000) // 3600000 * 3600000
        try:
            by_open, _src = hourly_closes(sym, now_ms - 48 * 3600000, now_ms)
        except Exception:
            continue
        keys = sorted(by_open)
        if len(keys) < 26:
            continue
        closes = [by_open[k] for k in keys]
        vols = [1.0] * len(closes)      # the fallback source has no volume; volr falls back to 1.0
        t_ms = keys[-1]
        fr = funding_rate(sym)
        rets = [closes[j] / closes[j - 1] - 1.0 for j in range(len(closes) - 24, len(closes))]
        feats = {
            "mom6": closes[-1] / closes[-7] - 1.0,
            "mom24": closes[-1] / closes[-25] - 1.0,
            "last": rets[-1],
            "rv": (sum(x * x for x in rets) / len(rets)) ** 0.5,
            "volr": vols[-1] / (sum(vols[-25:-1]) / 24) if sum(vols[-25:-1]) else 1.0,
            "funding": fr,   # None when the futures feed is blocked: a real coverage gap
        }
        for h in horizons:
            out.append({
                "id": f"crypto_{h}h:{sym}:{t_ms}",
                "domain": f"crypto_{h}h", "kind": "crypto",
                "question": f"{sym} direction over the next {h} hour" + ("s" if h > 1 else ""),
                "outcomes": ["UP", "DOWN"], "symbol": sym, "horizon_h": h,
                "opened_at": datetime.fromtimestamp(t_ms / 1000, timezone.utc).isoformat(),
                "reference_close": closes[-1], "result": None, **feats,
            })
    return out


def open_markets() -> list[dict[str, Any]]:
    return football_markets() + crypto_markets()
