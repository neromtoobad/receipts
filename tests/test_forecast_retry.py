"""A connection failure must not end a nine-hour run.

A 1,000-event bench died at event 950 on one httpx.ConnectTimeout, because
RETRYABLE only ever matched HTTP status strings and a refused connection has
no status. These pin the behaviour so that cannot recur.
"""
from __future__ import annotations

import httpx
import pytest

from agent.forecast import _with_retry


def test_connect_timeout_is_retried_then_succeeds(monkeypatch) -> None:
    monkeypatch.setattr("time.sleep", lambda *_: None)
    calls = {"n": 0}

    def flaky():
        calls["n"] += 1
        if calls["n"] < 3:
            raise httpx.ConnectTimeout("[Errno 60] Operation timed out")
        return "ok"

    assert _with_retry(flaky, attempts=5) == "ok"
    assert calls["n"] == 3


def test_read_timeout_is_retried(monkeypatch) -> None:
    monkeypatch.setattr("time.sleep", lambda *_: None)
    calls = {"n": 0}

    def flaky():
        calls["n"] += 1
        if calls["n"] < 2:
            raise httpx.ReadTimeout("timed out")
        return "ok"

    assert _with_retry(flaky, attempts=4) == "ok"


def test_a_real_bug_still_raises_immediately(monkeypatch) -> None:
    # Retrying a genuine defect would hide it behind eight slow attempts.
    monkeypatch.setattr("time.sleep", lambda *_: None)
    calls = {"n": 0}

    def broken():
        calls["n"] += 1
        raise ValueError("malformed payload")

    with pytest.raises(ValueError):
        _with_retry(broken, attempts=5)
    assert calls["n"] == 1
