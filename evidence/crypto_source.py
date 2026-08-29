"""Crypto candles, with a fallback, because the exchange APIs are not always
reachable from here.

Measured 2026-08-29: this network's DNS refuses api.binance.com, api.kraken.com,
api.exchange.coinbase.com and www.okx.com, while github, football-data and the
x402 facilitator all resolve fine. It is exchange-domain blocking and it is
intermittent: the same host served 18,000 candles earlier the same day. A ten day
unattended league cannot depend on it.

CoinGecko is an aggregator rather than an exchange and stays reachable, so it is
the fallback for closes. It does NOT publish funding rates, so `flowdesk` simply
has no live coverage when Binance is blocked. That is a real coverage gap and it
is reported as one, exactly like the sharp desk's missing Pinnacle odds. The
agent gets to learn it.

The historical corpus is already on disk, so the bench and the deletion chart do
not depend on any of this.
"""
from __future__ import annotations

import json
import time
from typing import Any

from evidence.data import _get

COINGECKO_ID = {"BTCUSDT": "bitcoin", "ETHUSDT": "ethereum", "SOLUSDT": "solana"}

# When the exchange domain is being refused, stop asking for a while. Without
# this every call pays the DNS timeout before falling back, and a tick that
# should take a second takes a minute.
_BLOCKED_UNTIL: dict[str, float] = {}
BLOCK_COOLDOWN = 600.0


def _is_blocked(name: str) -> bool:
    return time.time() < _BLOCKED_UNTIL.get(name, 0.0)


def _mark_blocked(name: str) -> None:
    _BLOCKED_UNTIL[name] = time.time() + BLOCK_COOLDOWN


def _binance_closes(symbol: str, start_ms: int, end_ms: int) -> dict[int, float]:
    rows = json.loads(_get(
        f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1h"
        f"&startTime={start_ms}&endTime={end_ms}&limit=1000", ttl=300, fast=True))
    return {int(r[0]): float(r[4]) for r in rows}


def _coingecko_closes(symbol: str, start_ms: int, end_ms: int) -> dict[int, float]:
    cid = COINGECKO_ID.get(symbol)
    if not cid:
        raise ValueError(f"no coingecko id for {symbol}")
    # Hour-align the window so repeated calls inside a tick hit the disk cache
    # instead of the rate limiter. The free tier throttles hard and a throttled
    # call was costing 60s.
    a, b = start_ms // 3600000 * 3600, (end_ms // 3600000 + 1) * 3600
    body = json.loads(_get(
        f"https://api.coingecko.com/api/v3/coins/{cid}/market_chart/range"
        f"?vs_currency=usd&from={a}&to={b}", ttl=1800, fast=True))
    # Points land on the hour; key them by the hour they open, like a kline.
    return {int(ts) // 3600000 * 3600000: float(px) for ts, px in body.get("prices", [])}


def hourly_closes(symbol: str, start_ms: int, end_ms: int) -> tuple[dict[int, float], str]:
    """Closes keyed by candle open time, and which source served them."""
    errors = []
    for name, fn in (("binance", _binance_closes), ("coingecko", _coingecko_closes)):
        if _is_blocked(name):
            errors.append(f"{name}: skipped, blocked recently")
            continue
        try:
            closes = fn(symbol, start_ms, end_ms)
            if closes:
                return closes, name
            errors.append(f"{name}: empty")
        except Exception as exc:
            errors.append(f"{name}: {type(exc).__name__}")
            _mark_blocked(name)
    raise RuntimeError("no candle source reachable (" + "; ".join(errors) + ")")


def funding_rate(symbol: str) -> float | None:
    """Binance only. None when unreachable, which the caller reports as a
    coverage gap rather than inventing a number."""
    if _is_blocked("binance-futures"):
        return None
    try:
        rows = json.loads(_get(
            f"https://fapi.binance.com/fapi/v1/fundingRate?symbol={symbol}&limit=1",
            ttl=300, fast=True))
        return float(rows[0]["fundingRate"]) if rows else None
    except Exception:
        _mark_blocked("binance-futures")
        return None
