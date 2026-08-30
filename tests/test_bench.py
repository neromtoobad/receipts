"""The bench, as a regression test.

Selection is independent of the forecaster: an arm learns from what each SOURCE
said against the outcome, never from its own forecast. So these assertions are
valid offline, and they are the ones that carry the thesis.

Forecast quality is NOT asserted here, because it needs a real model. The bench
refuses to write a chart from the stand-in for the same reason.
"""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from agent.forecast import SYSTEM_SHA
from bench.corpus import load_replay
from bench.run import EXPECTED_SYSTEM_SHA, base_rates, run_arm
from evidence.signals import fit_all

RUNS = 150


@pytest.fixture(scope="module")
def replay():
    fb_fit, cr_fit, events = load_replay()
    fit_all(fb_fit, cr_fit)
    step = len(events) / RUNS
    events = [events[int(i * step)] for i in range(RUNS)]
    rates, bb = base_rates(events)
    return events, rates, bb


def _arm(name, replay):
    events, rates, bb = replay
    return run_arm(name, events, rates, bb, model="unused", offline=True, quiet=True)


def test_the_prompt_has_not_changed():
    """The bench aborts on this too. Every arm must see a byte-identical prompt
    or the comparison is void."""
    assert SYSTEM_SHA == EXPECTED_SYSTEM_SHA


def test_memory_spends_less_than_amnesia(replay):
    sibyl, amnesiac = _arm("sibyl", replay), _arm("amnesiac", replay)
    assert sibyl["spend"] < amnesiac["spend"] / 2, (
        f"sibyl {sibyl['spend']:.2f} vs amnesiac {amnesiac['spend']:.2f}: "
        "memory must at least halve the bill or the thesis is not holding")


def test_memory_buys_fewer_informants(replay):
    sibyl, amnesiac = _arm("sibyl", replay), _arm("amnesiac", replay)
    assert sibyl["bought"] < amnesiac["bought"]


def test_the_measured_liar_is_learned_and_dropped(replay):
    """chalk_desk is negative in all six leagues and in crypto. An arm with
    memory must stop buying it; the amnesiac cannot."""
    sibyl, amnesiac = _arm("sibyl", replay), _arm("amnesiac", replay)
    sibyl_chalk = sibyl["bought_by"].get("chalk_desk", 0)
    blind_chalk = amnesiac["bought_by"].get("chalk_desk", 0)
    assert blind_chalk > 0, "the amnesiac has no way to avoid it"
    assert sibyl_chalk < blind_chalk / 4, (
        f"sibyl bought chalk_desk {sibyl_chalk} times against {blind_chalk}")


def test_every_arm_saw_the_same_events(replay):
    events, _, _ = replay
    for name in ("sibyl", "flat", "amnesiac"):
        assert _arm(name, replay)["n"] == len(events)


def test_the_corpus_spans_both_families(replay):
    """The flat arm only differs from the scoped one when several domains exist,
    so a single-family corpus would make the third arm pointless."""
    events, _, _ = replay
    domains = {e["domain"] for e in events}
    assert any(d.startswith("crypto") for d in domains)
    assert len([d for d in domains if not d.startswith("crypto")]) >= 4
