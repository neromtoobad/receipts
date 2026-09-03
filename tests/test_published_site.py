"""What is published must be the real site.

web/build_site.py used to write docs/index.html as well as its own copy, and the
league calls the dashboard build every tick — so every twenty minutes the Next
export was silently replaced by the superseded single-file generator, and the
live site quietly reverted to an unstyled page. It went unnoticed for hours.

docs/ has exactly one owner now, and these assert it.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs" / "index.html"


def test_docs_is_a_next_export_not_the_fallback_generator():
    assert DOCS.exists(), "docs/index.html missing: run `cd site && npm run export`"
    html = DOCS.read_text()
    assert "_next/static" in html, (
        "docs/index.html has no Next assets — it looks like the fallback "
        "generator overwrote the real export")
    assert "/receipts/_next/" in html, "basePath missing: Pages serves from /receipts/"


def test_the_published_page_carries_the_design_system():
    html = DOCS.read_text()
    for token in ("Instrument+Serif", "--rc-bg", "RECEIPTS"):
        assert token in html, f"published page is missing {token!r}"


def test_the_fallback_generator_never_writes_docs():
    """Check what it WRITES, not what it mentions. The file talks about docs/ in
    a comment explaining precisely why it must not write there."""
    src = (ROOT / "web" / "build_site.py").read_text()
    writes = re.findall(r'(\w+)\.write_text\(|ROOT\s*/\s*"([^"]+)"\s*/', src)
    targets = [t for pair in writes for t in pair if t]
    assert "docs" not in targets, (
        f"web/build_site.py writes into docs/ ({targets}): that belongs to the Next export")


def test_the_league_loop_does_not_rebuild_the_site():
    """The tick refreshes DATA. Rebuilding the site is a publish step — the loop
    calling the dashboard build is exactly what reverted the UI every 20 minutes."""
    loop = (ROOT / "scripts" / "league.sh").read_text()
    live = [l for l in loop.splitlines() if "web.build_site" in l and not l.strip().startswith("#")]
    assert not live, f"league.sh still builds the site: {live}"
    assert "web.export" in loop, "league.sh should refresh league.json each tick"


def test_every_route_was_exported():
    for route in ("agents", "proof", "live"):
        assert (ROOT / "docs" / route / "index.html").exists(), f"/{route} not exported"
