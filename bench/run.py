"""The replay bench. Three arms over one corpus, and the deletion test as a number.

    python -m bench.run --runs 1000 --model claude-haiku-4-5-20251001

Every arm gets the same corpus, the same budget, the same informants at the same
prices, the same prompt and the same model. The ONLY difference is what each is
allowed to remember. Each arm starts with an empty throwaway database and learns
as it walks the events in time order, exactly as a pundit would across ten days.

Two classes of result, reported separately on purpose:

  SELECTION  what each arm bought and what it cost. Deterministic given the
             corpus, so it is valid with or without a live model.
  QUALITY    Brier and accuracy. These depend on the model and are only reported
             when a real one ran. --allow-offline runs the plumbing and stamps
             every result INVALID rather than quietly producing a nicer chart.
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import json
import statistics
import sys
import tempfile
import time
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from agent.env import load as _load_env
from agent.forecast import BENCH_MODEL, SYSTEM_SHA, forecast, provider_for

_load_env()
from agent.memory import Memory
from agent.sources import ARMS, select
from bench.corpus import load_replay
from evidence.catalogue import CATALOGUE
from evidence.signals import INFORMANTS, fit_all, outcomes_for

BUDGET = 0.060
EXPECTED_SYSTEM_SHA = "33495af058e60a30f2215dd7a348a4a4570a839abfdb9636366dd4d92cbb5da7"

# proof/BENCH.md IS the chart. A smoke run must never be able to write it: at a
# dozen events the arms have not learned anything yet, so the numbers are noise
# and the arms are indistinguishable. 200 is the floor at which each of the eight
# domains has seen enough resolutions for promotion to have happened at all.
MIN_PUBLISH_RUNS = 200


def brier(probs: dict[str, float], actual: str) -> float:
    return sum((p - (1.0 if o == actual else 0.0)) ** 2 for o, p in probs.items())


def base_rates(events) -> tuple[dict, dict]:
    counts = defaultdict(lambda: defaultdict(int))
    for e in events:
        counts[e["domain"]][e["result"]] += 1
    rates, bb = {}, {}
    for d, c in counts.items():
        tot = sum(c.values())
        rates[d] = {o: c[o] / tot for o in outcomes_for(d) if c[o] or True}
        bb[d] = sum(rates[d][o] * brier(rates[d], o) for o in rates[d])
    return rates, bb


def run_arm(arm: str, events, rates, bb, model, offline, quiet=False, rpm: float = 0.0) -> dict:
    """One arm, walking the corpus in time order with a fresh empty memory."""
    with tempfile.TemporaryDirectory() as tmp:
        mem = Memory(f"bench_{arm}", db_path=Path(tmp) / f"{arm}.db")
        stats = {"arm": arm, "n": 0, "hit": 0, "brier": 0.0, "spend": 0.0,
                 "bought": 0, "bought_by": defaultdict(int), "empty_buys": 0,
                 # Crypto is three quarters of the corpus, so a blended average
                 # hides the football story completely. Keep them apart.
                 "by_family": defaultdict(lambda: {"n": 0, "hit": 0, "brier": 0.0,
                                                   "spend": 0.0, "bought": 0}),
                 "resolved_models": set()}
        for i, e in enumerate(events):
            domain = e["domain"]
            priced = {iid: CATALOGUE[iid]["price_usdc"]
                      for iid in CATALOGUE if domain in CATALOGUE[iid]["answers_on"]}
            choices = select(mem, domain, priced, BUDGET, arm=arm)

            evidence, spend, said = [], 0.0, {}
            for ch in choices:
                inf = INFORMANTS.get(ch.source)
                payload = inf.payload(e) if inf and inf.covers(domain) else None
                spend += ch.price
                stats["bought"] += 1
                stats["bought_by"][ch.source] += 1
                if payload:
                    evidence.append({"source": ch.source, "payload": payload,
                                     "trust": ch.trust})
                    said[ch.source] = (payload, ch.price)
                else:
                    stats["empty_buys"] += 1
                    mem.observe_miss(ch.source, domain, ch.price)

            if rpm:
                time.sleep(60.0 / rpm)
            out = forecast({"domain": domain, "question": e["question"],
                            "outcomes": e["outcomes"]},
                           rates[domain], evidence, model=model, offline=offline)
            stats["resolved_models"].add(out.get("resolved_model") or out["model"])
            probs = out["probabilities"]
            pick = max(probs, key=probs.get)

            fam = "crypto" if domain.startswith("crypto") else "football"
            b = brier(probs, e["result"])
            stats["n"] += 1
            stats["hit"] += (pick == e["result"])
            stats["brier"] += b
            stats["spend"] += spend
            f = stats["by_family"][fam]
            f["n"] += 1; f["hit"] += (pick == e["result"]); f["brier"] += b
            f["spend"] += spend; f["bought"] += len(choices)

            for src, (payload, cost) in said.items():
                mem.observe(src, domain, brier(payload, e["result"]), bb[domain], cost)

            if not quiet and (i + 1) % 200 == 0:
                print(f"  [{arm}] {i + 1}/{len(events)}", file=sys.stderr)
        stats["bought_by"] = dict(stats["bought_by"])
        stats["by_family"] = {k: dict(v) for k, v in stats["by_family"].items()}
        stats["resolved_models"] = sorted(stats["resolved_models"])
        return stats


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", default=",".join(ARMS))
    ap.add_argument("--runs", type=int, default=1000)
    ap.add_argument("--model", default=BENCH_MODEL)
    ap.add_argument("--allow-offline", action="store_true",
                    help="run the plumbing with the stand-in forecaster. Every "
                         "result is stamped INVALID and nothing is written to proof/.")
    ap.add_argument("--out", default=str(ROOT / "proof" / "BENCH.md"))
    ap.add_argument("--publish-anyway", action="store_true",
                    help="write proof/BENCH.md from a run below MIN_PUBLISH_RUNS. "
                         "Only for deliberately reporting a small-n result.")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--rpm", type=float, default=0.0,
                    help="throttle to this many model calls per minute. Free tiers "
                         "rate-limit hard, and a 429 halfway through a run wastes "
                         "everything before it.")
    ap.add_argument("--even-sample", action="store_true",
                    help="sample the corpus in natural proportion (76%% crypto). The "
                         "default stratifies by family instead, because an even sample "
                         "leaves ~40 football events per league, which is too few for "
                         "an arm to establish eight sources at PROMOTE_N observations "
                         "each. That under-powers the learning rather than testing it.")
    a = ap.parse_args()

    if SYSTEM_SHA != EXPECTED_SYSTEM_SHA:
        print("ABORT: the forecast prompt has changed mid-benchmark.\n"
              f"  expected {EXPECTED_SYSTEM_SHA}\n  got      {SYSTEM_SHA}\n"
              "Every arm must see a byte-identical prompt or the comparison is void.",
              file=sys.stderr)
        return 2

    offline = a.allow_offline
    if offline:
        print("WARNING: --allow-offline. The stand-in forecaster is a trust-weighted\n"
              "average, not the model. SELECTION figures below are still valid;\n"
              "QUALITY figures are NOT and nothing will be written to proof/.\n",
              file=sys.stderr)

    if not offline:
        try:
            prov = provider_for(a.model)
        except ValueError as exc:
            print(f"ABORT: {exc}", file=sys.stderr)
            return 2
        import os as _os
        needed = {"anthropic": ("ANTHROPIC_API_KEY",),
                  "google": ("GEMINI_API_KEY", "GOOGLE_API_KEY"),
                  "openai": ("RECEIPTS_OPENAI_API_KEY", "AION_API_KEY", "OPENAI_API_KEY")}[prov]
        local = _os.environ.get("RECEIPTS_OPENAI_BASE_URL", "").startswith(
            ("http://localhost", "http://127.0.0.1"))
        if prov == "openai" and local:
            needed = ()
        if needed and not any(_os.environ.get(k) for k in needed):
            print(f"ABORT: {a.model} needs one of {' or '.join(needed)} in the environment.",
                  file=sys.stderr)
            return 2
        print(f"provider: {prov}", file=sys.stderr)

    fb_fit, cr_fit, events = load_replay()
    fit_all(fb_fit, cr_fit)
    if a.runs and a.runs < len(events):
        if a.even_sample:
            step = len(events) / a.runs        # natural proportion
            events = [events[int(i * step)] for i in range(a.runs)]
        else:
            fb = [e for e in events if not e["domain"].startswith("crypto")]
            cr = [e for e in events if e["domain"].startswith("crypto")]
            half = a.runs // 2
            def spread(xs, k):
                if k >= len(xs):
                    return xs
                st = len(xs) / k
                return [xs[int(i * st)] for i in range(k)]
            events = sorted(spread(fb, half) + spread(cr, a.runs - half),
                            key=lambda e: e["sort"])
    rates, bb = base_rates(events)

    arms = [x.strip() for x in a.arms.split(",") if x.strip()]
    # ~650 prompt + ~400 completion per forecast, measured on real calls. Say the
    # number out loud before a long run: free tiers cap DAILY tokens, and that is
    # what stops a bench, not the per-minute rate.
    est_calls = len(events) * len(arms)
    print(f"~{est_calls} model calls, roughly {est_calls * 1050 // 1000}k tokens\n",
          file=sys.stderr)
    print(f"corpus {len(events)} resolved events | budget {BUDGET:.3f} | "
          f"model {'OFFLINE STAND-IN' if offline else a.model} | prompt {SYSTEM_SHA[:12]}\n")

    t0 = time.perf_counter()
    with cf.ThreadPoolExecutor(max_workers=len(arms)) as ex:
        futures = {ex.submit(run_arm, arm, events, rates, bb, a.model, offline,
                             a.quiet, a.rpm / max(len(arms), 1)): arm for arm in arms}
        results = {futures[f]: f.result() for f in cf.as_completed(futures)}
    elapsed = time.perf_counter() - t0

    ordered = [results[x] for x in arms if x in results]

    seen = sorted({m for s in ordered for m in s["resolved_models"]})
    if not offline and len(seen) > 1:
        print(f"ABORT: the arms did not all see the same model: {seen}\n"
              "A '-latest' alias shifted mid-run, so the comparison is void. "
              "Re-run pinned to one of those concrete ids.", file=sys.stderr)
        return 3
    if seen and not offline:
        print(f"resolved model: {seen[0]}\n")
    print("SELECTION  (deterministic; valid with or without a live model)")
    hdr = f"{'arm':12}{'bought/call':>13}{'spend/call':>12}{'total spend':>13}{'paid-but-empty':>16}"
    print(hdr); print("-" * len(hdr))
    for s in ordered:
        print(f"{s['arm']:12}{s['bought'] / s['n']:>13.2f}{s['spend'] / s['n']:>12.4f}"
              f"{s['spend']:>13.2f}{s['empty_buys']:>16}")

    for fam in ("football", "crypto"):
        rows = [(s["arm"], s["by_family"].get(fam)) for s in ordered]
        rows = [(n, f) for n, f in rows if f and f["n"]]
        if not rows:
            continue
        print(f"\n  {fam} only  ({rows[0][1]['n']} events)")
        print(f"  {'arm':12}{'bought/call':>13}{'spend/call':>12}{'total':>10}")
        for n, f in rows:
            print(f"  {n:12}{f['bought']/f['n']:>13.2f}{f['spend']/f['n']:>12.4f}"
                  f"{f['spend']:>10.2f}")

    print(f"\nQUALITY  {'(INVALID: offline stand-in)' if offline else f'(model {a.model})'}")
    hdr2 = f"{'arm':12}{'accuracy':>10}{'brier':>9}"
    print(hdr2); print("-" * len(hdr2))
    for s in ordered:
        print(f"{s['arm']:12}{s['hit'] / s['n']:>9.1%}{s['brier'] / s['n']:>9.4f}")
    for fam in ("football", "crypto"):
        rows = [(s["arm"], s["by_family"].get(fam)) for s in ordered]
        rows = [(n, f) for n, f in rows if f and f["n"]]
        if rows:
            print(f"  {fam:10}" + "  ".join(
                f"{n}={f['brier']/f['n']:.4f}" for n, f in rows))

    if "sibyl" in results and "amnesiac" in results:
        b, m = results["sibyl"], results["amnesiac"]
        ratio = (m["spend"] / m["n"]) / max(b["spend"] / b["n"], 1e-9)
        print(f"\nDELETION TEST: memory -> amnesia")
        print(f"  informants bought  {b['bought']/b['n']:.2f} -> {m['bought']/m['n']:.2f} per forecast")
        print(f"  spend              {b['spend']/b['n']:.4f} -> {m['spend']/m['n']:.4f} USDC "
              f"({ratio:.1f}x)")
        if not offline:
            print(f"  brier              {b['brier']/b['n']:.4f} -> {m['brier']/m['n']:.4f}")
    print(f"\n{elapsed:.1f}s")

    if offline:
        print("\nNothing written to proof/: an offline run cannot back a chart.",
              file=sys.stderr)
        return 0

    if len(events) < MIN_PUBLISH_RUNS and not a.publish_anyway:
        print(f"\nNot written to proof/: {len(events)} events is below the "
              f"{MIN_PUBLISH_RUNS}-event floor for publishing.\n"
              "At this size no arm has learned anything yet, so the arms are\n"
              "indistinguishable and the quality numbers are noise. The run still\n"
              "proves the pipeline works. Use --publish-anyway to override.",
              file=sys.stderr)
        return 0

    out = Path(a.out)
    out.write_text(_report(ordered, results, events, a.model, elapsed))
    print(f"\nwrote {out}")
    return 0


def _report(ordered, results, events, model, elapsed) -> str:
    lines = ["# The deletion test", "",
             f"`{len(events)}` resolved events, budget {BUDGET:.3f} USDC per forecast, "
             f"model `{model}`" +
             (f" (served as `{sorted({m for s in ordered for m in s['resolved_models']})[0]}`)"
              if any(s["resolved_models"] for s in ordered) else "") +
             f", prompt sha `{SYSTEM_SHA[:16]}`.", "",
             "Same corpus, same budget, same informants at the same prices, same prompt, "
             "same model. The only difference between arms is what each is allowed to "
             "remember.", "",
             (f"**n = {len(events)}**." if len(events) >= MIN_PUBLISH_RUNS else
              f"**n = {len(events)}, below the {MIN_PUBLISH_RUNS}-event floor. "
              "Treat every quality figure here as noise.**"), "",
             "| arm | accuracy | brier | bought/call | spend/call | total spend |",
             "|---|---|---|---|---|---|"]
    for s in ordered:
        lines.append(f"| {s['arm']} | {s['hit']/s['n']:.1%} | {s['brier']/s['n']:.4f} | "
                     f"{s['bought']/s['n']:.2f} | {s['spend']/s['n']:.4f} | "
                     f"${s['spend']:.2f} |")
    if "sibyl" in results and "amnesiac" in results:
        b, m = results["sibyl"], results["amnesiac"]
        lines += ["", "## Deletion test", "",
                  f"- informants bought: **{b['bought']/b['n']:.2f} -> {m['bought']/m['n']:.2f}** per forecast",
                  f"- spend: **{b['spend']/b['n']:.4f} -> {m['spend']/m['n']:.4f} USDC** "
                  f"({(m['spend']/m['n'])/(b['spend']/b['n']):.1f}x)",
                  f"- brier: **{b['brier']/b['n']:.4f} -> {m['brier']/m['n']:.4f}**"]
    lines += ["", f"Generated in {elapsed:.1f}s."]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
