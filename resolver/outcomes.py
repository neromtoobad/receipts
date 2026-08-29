"""What actually happened.

Outcomes are looked up from the same public sources the corpus was built from,
so a resolved market in the league is resolved the same way a resolved match in
the backtest was. Market ids carry everything needed to find the answer:

    epl:2026-09-02:Arsenal:Liverpool     -> H / D / A
    crypto_1h:BTCUSDT:1787983200000      -> UP / DOWN
"""
from __future__ import annotations

import csv
import io
import json
from datetime import datetime, timedelta, timezone

from evidence.crypto_source import hourly_closes
from evidence.data import CURRENT_SEASON, FD_BASE, LEAGUES, _get, _parse_date

class Outcome:
    """A lookup result. The three states are deliberately distinct.

    A network failure that reads as "not due yet" is how a resolver goes quiet
    for a day and nobody notices, so PENDING and ERROR are never conflated.
    """
    RESOLVED, PENDING, ERROR = "resolved", "pending", "error"

    def __init__(self, status: str, result: str | None = None, reason: str = ""):
        self.status, self.result, self.reason = status, result, reason

    @property
    def ok(self) -> bool:
        return self.status == self.RESOLVED

    def __repr__(self):
        return f"Outcome({self.status}{', ' + self.result if self.result else ''}{', ' + self.reason if self.reason else ''})"


_FOOTBALL_CACHE: dict[str, str] | None = None


def _football_index(refresh: bool = False) -> dict[str, str]:
    """(domain, date, home, away) -> result, for the current season."""
    global _FOOTBALL_CACHE
    if _FOOTBALL_CACHE is not None and not refresh:
        return _FOOTBALL_CACHE
    idx: dict[str, str] = {}
    for code, domain in LEAGUES.items():
        try:
            text = _get(f"{FD_BASE}/mmz4281/{CURRENT_SEASON}/{code}.csv", ttl=1800)
        except Exception:
            continue
        for r in csv.DictReader(io.StringIO(text)):
            d = _parse_date(r.get("Date", "") or "")
            res = (r.get("FTR") or "").strip()
            if not d or not res:
                continue
            key = f"{domain}:{d:%Y-%m-%d}:{r['HomeTeam']}:{r['AwayTeam']}".replace(" ", "_")
            idx[key] = res
    _FOOTBALL_CACHE = idx
    return idx


def resolve_football(market_id: str, refresh: bool = False) -> Outcome:
    try:
        idx = _football_index(refresh)
    except Exception as exc:
        return Outcome(Outcome.ERROR, reason=f"results feed unreachable: {type(exc).__name__}")
    if not idx:
        return Outcome(Outcome.ERROR, reason="results feed returned nothing")
    hit = idx.get(market_id)
    return Outcome(Outcome.RESOLVED, hit) if hit else Outcome(
        Outcome.PENDING, reason="not in the results feed yet")


def resolve_crypto(market_id: str, closes: dict[int, float] | None = None) -> Outcome:
    """Compare the close at the market's reference candle with the close h hours on.

    Re-fetched from Binance rather than trusted from our own record, so the
    outcome is independently checkable by anyone with the market id.
    """
    try:
        domain, sym, ts = market_id.split(":")
        horizon = int(domain.removeprefix("crypto_").removesuffix("h"))
        t_ms = int(ts)
    except (ValueError, AttributeError):
        return Outcome(Outcome.ERROR, reason=f"unparseable market id {market_id!r}")

    end_ms = t_ms + horizon * 3600 * 1000
    if datetime.now(timezone.utc) < datetime.fromtimestamp(
            end_ms / 1000, timezone.utc) + timedelta(minutes=2):
        return Outcome(Outcome.PENDING, reason="horizon has not elapsed")

    if closes is None:
        try:
            closes, _source = hourly_closes(sym, t_ms, end_ms + 3600000)
        except Exception as exc:
            return Outcome(Outcome.ERROR, reason=str(exc))
    by_open = closes
    ref, later = by_open.get(t_ms), by_open.get(end_ms)
    if ref is None or later is None:
        return Outcome(Outcome.PENDING, reason="candles not published yet")
    return Outcome(Outcome.RESOLVED, "UP" if later > ref else "DOWN")


def resolve(market_id: str, closes: dict[int, float] | None = None) -> Outcome:
    if market_id.startswith("crypto_"):
        return resolve_crypto(market_id, closes)
    return resolve_football(market_id)


def symbol_of(market_id: str) -> str | None:
    parts = market_id.split(":")
    return parts[1] if market_id.startswith("crypto_") and len(parts) == 3 else None
