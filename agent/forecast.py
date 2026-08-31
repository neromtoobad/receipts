"""The forecast call. Identical across every benchmark arm.

SYSTEM is byte-identical for sibyl, flat-json and amnesiac, and identical across
both event families. It holds no informant reliabilities, no league knowledge and
no priors beyond what arrives in the message. What differs between arms is the
evidence bundle, and only that.

SYSTEM_SHA is asserted by the bench before any arm runs, so editing this prompt
mid-benchmark aborts the run instead of quietly invalidating the comparison.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from agent.env import load as _load_env

_load_env()
from typing import Any

LIVE_MODEL = os.environ.get("RECEIPTS_LIVE_MODEL", "claude-sonnet-5")
BENCH_MODEL = os.environ.get("RECEIPTS_BENCH_MODEL", "claude-haiku-4-5-20251001")


OPENAI_BASE_URL = os.environ.get("RECEIPTS_OPENAI_BASE_URL", "")


def openai_key() -> str | None:
    for k in ("RECEIPTS_OPENAI_API_KEY", "AION_API_KEY", "OPENAI_API_KEY"):
        if os.environ.get(k):
            return os.environ[k]
    return None


def provider_for(model: str) -> str:
    """Which API serves this model.

    The benchmark's rule is that every arm sees the SAME model and a
    byte-identical prompt. It has never been that the model must be Claude, so
    any provider is legitimate. Whatever runs is stamped into the report and
    asserted equal across arms.

    Anything that is not a claude-* or gemini-* id is treated as an
    OpenAI-compatible endpoint, which covers AionLabs and most other providers.
    That needs RECEIPTS_OPENAI_BASE_URL set, so an unknown id is still refused
    rather than guessed at.
    """
    m = model.lower()
    if m.startswith(("gemini", "models/gemini")):
        return "google"
    if m.startswith("claude"):
        return "anthropic"
    if os.environ.get("RECEIPTS_OPENAI_BASE_URL"):
        return "openai"
    raise ValueError(
        f"unknown model {model!r}: expected claude-*, gemini-*, or an "
        "OpenAI-compatible id with RECEIPTS_OPENAI_BASE_URL set")

SYSTEM = """You are a forecaster. You are scored by Brier score, so calibration \
matters more than boldness: a confident wrong answer costs you far more than an \
honest uncertain one.

You will be given a market with a fixed set of possible outcomes, the base rate \
for those outcomes, and zero or more pieces of purchased evidence.

Each piece of evidence may carry a trust weight between 0 and 1. That weight is \
this forecaster's own record of how much that source has been worth listening to \
on this kind of market. Weight the evidence accordingly. A source with a low \
weight should move you very little even when it is emphatic. A source with no \
weight stated is unproven, not trustworthy by default.

If the evidence sources disagree, do not split the difference mechanically. \
Prefer the higher-weighted source and say so.

If you were given no evidence at all, that is a legitimate position, not a \
failure. Return the base rate. Do not invent a signal you do not have, and do \
not drift away from the base rate to look decisive.

Never assume that a source which cost more is better. Price is what a vendor \
charges and carries no information about quality.

Return strict JSON and nothing else:

{"probabilities": {"<outcome>": <float>, ...},
 "confidence": <float 0-1>,
 "reasoning": "<two sentences at most: what moved you and what you discounted>",
 "leaned_on": ["<source id>", ...]}

The probabilities must cover exactly the outcomes given and sum to 1.0. \
"confidence" is how much better than the base rate you believe this forecast to \
be, where 0 means you are simply restating the base rate. "leaned_on" lists the \
sources that actually changed your answer, which may be empty."""

SYSTEM_SHA = hashlib.sha256(SYSTEM.encode()).hexdigest()


def build_user_message(market: dict, base_rate: dict[str, float],
                       evidence: list[dict]) -> str:
    lines = [
        f"MARKET: {market['question']}",
        f"domain: {market['domain']}",
        f"outcomes: {', '.join(market['outcomes'])}",
        "base rate: " + ", ".join(f"{k} {v:.3f}" for k, v in base_rate.items()),
        "",
    ]
    if not evidence:
        lines.append("EVIDENCE: none purchased for this market.")
    else:
        lines.append(f"EVIDENCE ({len(evidence)} sources purchased):")
        for e in evidence:
            trust = e.get("trust")
            tag = f"trust {trust:.2f}" if trust is not None else "trust unproven"
            lines.append(f"- {e['source']} [{tag}]: "
                         f"{json.dumps(e['payload'], separators=(',', ':'))}")
    return "\n".join(lines)


def _normalise(probs: dict[str, float], outcomes: list[str]) -> dict[str, float]:
    vals = {o: max(0.0, float(probs.get(o, 0.0))) for o in outcomes}
    s = sum(vals.values())
    if s <= 0:
        return {o: 1.0 / len(outcomes) for o in outcomes}
    return {o: v / s for o, v in vals.items()}


def _offline(market, base_rate, evidence) -> dict[str, Any]:
    """Deterministic stand-in for plumbing tests ONLY.

    It is a trust-weighted average of whatever was bought. It is NOT the
    forecaster and must never produce a benchmark number: bench/run.py refuses
    to run against it, and every record it writes is stamped model="offline".
    """
    outs = market["outcomes"]
    parts = [(e["payload"], max(e.get("trust") or 0.0, 0.05)) for e in evidence
             if isinstance(e.get("payload"), dict)]
    parts = [(p, w) for p, w in parts if all(o in p for o in outs)]
    if not parts:
        return {"probabilities": dict(base_rate), "confidence": 0.0,
                "reasoning": "No usable evidence, so the base rate stands.",
                "leaned_on": []}
    tw = sum(w for _, w in parts)
    probs = {o: sum(float(p[o]) * w for p, w in parts) / tw for o in outs}
    lead = max(parts, key=lambda x: x[1])
    return {"probabilities": _normalise(probs, outs),
            "confidence": round(min(0.9, tw / (tw + 1)), 3),
            "reasoning": "Trust-weighted blend of purchased evidence.",
            "leaned_on": [e["source"] for e in evidence
                          if (e.get("trust") or 0) >= (lead[1] - 1e-9)]}


RETRYABLE = ("503", "429", "UNAVAILABLE", "RESOURCE_EXHAUSTED", "overloaded", "rate limit")


def _retry_after(exc) -> float | None:
    """Google's 429 carries the exact wait it wants: 'Please retry in 32.4s' and
    a retryDelay field. Guessing a backoff when the server has told you the
    number just burns quota."""
    m = re.search(r"retry in ([\d.]+)s", str(exc))
    if m:
        return float(m.group(1)) + 1.0
    m = re.search(r"'retryDelay': '(\d+)s'", str(exc))
    return float(m.group(1)) + 1.0 if m else None


def _with_retry(call, attempts: int = 8):
    """Free tiers 503 and 429 hard. A thousand-event bench that dies two thirds
    of the way through has wasted everything before it, so transient failures
    wait however long the server asked for and try again."""
    import time as _t
    last = None
    for i in range(attempts):
        try:
            return call()
        except Exception as exc:
            last = exc
            if not any(t.lower() in str(exc).lower() for t in RETRYABLE):
                raise
            # Providers that send no retryDelay still mean a per-minute window,
            # so back off toward a full minute rather than capping at 30s.
            _t.sleep(_retry_after(exc) or min(5 * (i + 1), 65))
    raise last


def forecast(market: dict, base_rate: dict[str, float], evidence: list[dict], *,
             model: str = LIVE_MODEL, offline: bool = False) -> dict[str, Any]:
    """One forecast. Returns probabilities, confidence, reasoning, leaned_on."""
    if offline:
        return {**_offline(market, base_rate, evidence), "model": "offline"}

    user = build_user_message(market, base_rate, evidence)
    provider = provider_for(model)

    resolved = model
    if provider == "openai":
        import httpx
        base = os.environ.get("RECEIPTS_OPENAI_BASE_URL", "").rstrip("/")
        key = openai_key()
        if not key:
            raise RuntimeError("no key: set RECEIPTS_OPENAI_API_KEY or AION_API_KEY")
        body = {"model": model, "temperature": 0.0, "max_tokens": 2048,
                "messages": [{"role": "system", "content": SYSTEM},
                             {"role": "user", "content": user}]}

        def _post(payload):
            r = httpx.post(f"{base}/chat/completions", json=payload, timeout=120,
                           headers={"Authorization": f"Bearer {key}"})
            if r.status_code >= 400:
                raise RuntimeError(f"{r.status_code}: {r.text[:300]}")
            return r.json()

        try:
            data = _with_retry(lambda: _post({**body,
                                              "response_format": {"type": "json_object"}}))
        except Exception as exc:
            # Not every OpenAI-compatible endpoint implements response_format.
            # The prompt already demands strict JSON, so drop it and carry on.
            if "response_format" not in str(exc) and "400" not in str(exc):
                raise
            data = _with_retry(lambda: _post(body))
        text = (data["choices"][0]["message"].get("content") or "").strip()
        resolved = data.get("model") or model
    elif provider == "anthropic":
        import anthropic
        client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        msg = _with_retry(lambda: client.messages.create(
            model=model, max_tokens=600, temperature=0.0, system=SYSTEM,
            messages=[{"role": "user", "content": user}],
        ))
        text = "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")
        resolved = getattr(msg, "model", model)
    else:
        from google import genai
        from google.genai import types
        key = (os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"))
        client = genai.Client(api_key=key)
        # system_instruction carries SYSTEM verbatim, so the prompt the model sees
        # is byte-identical to the one Claude sees. That is the whole control.
        # Gemini 3.x spends max_output_tokens on thinking before it answers, so
        # a 600 cap returned truncated JSON. The task is a calibration judgement
        # over a handful of numbers, not a reasoning problem, so the thinking
        # budget goes to zero and the ceiling goes up. Both keep the comparison
        # fair: every arm gets the identical config.
        cfg = dict(system_instruction=SYSTEM, temperature=0.0,
                   max_output_tokens=2048, response_mime_type="application/json")
        try:
            cfg["thinking_config"] = types.ThinkingConfig(thinking_budget=0)
            resp = _with_retry(lambda: client.models.generate_content(
                model=model, contents=user, config=types.GenerateContentConfig(**cfg)))
        except Exception as exc:
            if "thinking" not in str(exc).lower():
                raise
            cfg.pop("thinking_config")      # model does not accept the setting
            resp = _with_retry(lambda: client.models.generate_content(
                model=model, contents=user, config=types.GenerateContentConfig(**cfg)))
        text = resp.text or ""
        # A "-latest" alias is convenient but could shift underneath a long run.
        # The API reports the concrete version it served, so capture it and let
        # the bench assert every arm saw the same one.
        resolved = getattr(resp, "model_version", None) or model

    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        raise ValueError(
            f"model did not return complete JSON (truncated at max_output_tokens?): "
            f"{text[:200]}")
    out = json.loads(m.group(0))
    out["probabilities"] = _normalise(out.get("probabilities", {}), market["outcomes"])
    out["confidence"] = float(out.get("confidence", 0.0))
    out["reasoning"] = str(out.get("reasoning", ""))[:400]
    out["leaned_on"] = [s for s in out.get("leaned_on", []) if isinstance(s, str)]
    out["model"] = model
    out["resolved_model"] = resolved
    out["provider"] = provider
    return out
