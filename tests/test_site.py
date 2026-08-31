"""The trust map must render every cell state, and must never invent one.

The map is the pitch. If a state renders wrong, the story it tells is wrong.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from web.build_site import build, cell_html, pundits


def test_a_trusted_source_is_green_and_shows_its_trust():
    h = cell_html({"state": "established", "n": 8, "skill": 0.089, "trust": 0.62,
                   "spend_total": 0.096})
    assert 'class="good"' in h and "0.62" in h
    assert "skill +0.089" in h and "8 resolved" in h


def test_a_source_worse_than_the_base_rate_is_red():
    """chalk_desk measured negative in every league. It must read as a warning,
    not as a faint green."""
    h = cell_html({"state": "established", "n": 20, "skill": -0.004, "trust": 0.0})
    assert 'class="bad"' in h
    assert "never trusted" in h


def test_zero_skill_is_treated_as_bad_not_as_weak_good():
    h = cell_html({"state": "established", "n": 10, "skill": 0.0, "trust": 0.0})
    assert 'class="bad"' in h


def test_provisional_shows_how_many_times_it_was_paid_for():
    h = cell_html({"state": "provisional", "n": 2})
    assert 'class="prov"' in h and ">2<" in h


def test_archived_is_shown_not_hidden():
    """'This one went quiet' is information, and archiving is recoverable."""
    h = cell_html({"state": "archived", "n": 5})
    assert 'class="arch"' in h and "recoverable" in h


def test_never_bought_renders_empty():
    assert 'class="none"' in cell_html(None)


def test_the_page_builds_and_is_self_contained():
    html = build()
    assert "<title>RECEIPTS" in html
    assert "<style>" in html
    # no server, no CDN, no build step: nothing may be fetched at view time
    for bad in ("<script", "src=\"http", "href=\"http", "cdn.", "googleapis"):
        assert bad not in html, f"page must be self-contained, found {bad!r}"


def test_test_databases_never_appear_as_pundits():
    assert not any(p.startswith(("t_", "s_", "arm_", "bench_")) for p in pundits())
    assert "commons" not in pundits()
