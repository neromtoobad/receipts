"""The forecast prompt. Moves to agent/forecast.py on day 3.

THE EXPERIMENTAL CONTROL, and the single most important file in the benchmark.

SYSTEM is byte-identical for every arm: sibyl, flat-json, and amnesiac. It is
also identical across every domain. It contains no knowledge of any informant's
reliability, no league-specific knowledge, and no priors beyond what arrives in
the message.

What differs between arms is the EVIDENCE BUNDLE, and only that. The sibyl arm
buys fewer informants and attaches a remembered trust weight to each. The
amnesiac buys more and attaches none. That difference is the whole experiment,
so nothing else may vary.

Guard: bench/run.py asserts sha256(SYSTEM) matches SYSTEM_SHA before any arm
runs. If someone edits this prompt mid-benchmark the run aborts rather than
silently producing an invalid comparison.
"""
import hashlib, json

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


def build_user_message(market, base_rate, evidence):
    """Assemble the per-forecast message.

    market    : {"id","domain","question","outcomes":[...]}
    base_rate : {outcome: prior probability}
    evidence  : [{"source","payload","trust"(optional)}]

    The amnesiac arm passes the same shape with "trust" omitted throughout.
    Nothing about the format differs between arms.
    """
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
            lines.append(f"- {e['source']} [{tag}]: {json.dumps(e['payload'], separators=(',', ':'))}")
    return "\n".join(lines)
