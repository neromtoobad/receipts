"""Render the league to one self-contained HTML file.

    python -m web.build_site            # -> web/index.html

No server, no build step, no npm. A single file with inlined CSS that opens from
disk. That is deliberate: the demo cannot depend on a dev server surviving the
recording, and the same file is what gets hosted for the public leaderboard.

It reads the pundit databases through agent/memory.py like everything else, so
there is still exactly one place Sibyl is touched.
"""
from __future__ import annotations

import html
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from agent.memory import MEMORY_DIR, Memory
from evidence.catalogue import CATALOGUE
from evidence.signals import CRYPTO_DOMAINS, FOOTBALL_DOMAINS

DOMAINS = list(FOOTBALL_DOMAINS) + list(CRYPTO_DOMAINS)
SKIP = {"commons", "probe", "scratch", "demo", "demo2"}


def pundits() -> list[str]:
    return sorted(p.stem for p in MEMORY_DIR.glob("*.db")
                  if p.stem not in SKIP and not p.stem.startswith(("t_", "s_", "arm_", "bench_")))


def collect(pid: str) -> dict:
    mem = Memory(pid)
    cells: dict[tuple[str, str], dict] = {}
    for b in mem.all_reliability_including_archived():
        cells[(b["source"], b["domain"])] = {**b, "state": "archived" if b.get("archived") else "established"}
    for b in mem.provisional_sources():
        cells.setdefault((b["source"], b["domain"]), {**b, "state": "provisional"})

    forecasts, resolutions, spend, consultations = [], [], 0.0, 0
    for e in mem.recent_events(limit=400):
        x = e.get("extra") or {}
        k = x.get("kind")
        if k == "forecast":
            forecasts.append(x); spend += float(x.get("spend") or 0)
        elif k == "resolution":
            resolutions.append(x)
        elif k == "consultation":
            consultations += 1
    briers = [r["brier"] for r in resolutions if r.get("brier") is not None]
    return {"id": pid, "cells": cells, "forecasts": forecasts, "resolutions": resolutions,
            "spend": spend, "consultations": consultations,
            "brier": sum(briers) / len(briers) if briers else None,
            "capacity": mem.capacity()}


def cell_html(c: dict | None) -> str:
    if not c:
        return '<td class="none" title="never bought here"></td>'
    state = c.get("state")
    n = c.get("n", 0)
    skill = c.get("skill")
    trust = c.get("trust")
    if state == "provisional":
        return (f'<td class="prov" title="paid for {n}x, not yet promoted">'
                f'<span class="n">{n}</span></td>')
    if state == "archived":
        return (f'<td class="arch" title="archived after going quiet. recoverable.">'
                f'<span class="n">arch</span></td>')
    t = float(trust or 0.0)
    if skill is not None and skill <= 0:
        return (f'<td class="bad" title="skill {skill:+.3f} over {n} resolved. '
                f'worse than the base rate, so never trusted."><span class="n">{skill:+.2f}</span></td>')
    op = 0.18 + 0.82 * min(t, 1.0)
    return (f'<td class="good" style="--a:{op:.2f}" '
            f'title="trust {t:.2f}, skill {skill:+.3f}, {n} resolved, '
            f'{c.get("spend_total", 0):.3f} USDC spent">'
            f'<span class="n">{t:.2f}</span></td>')


def trust_map(p: dict) -> str:
    rows = []
    order = sorted(CATALOGUE, key=lambda i: -CATALOGUE[i]["price_usdc"])
    for src in order:
        answers = set(CATALOGUE[src]["answers_on"])
        tds = "".join(cell_html(p["cells"].get((src, d))) if d in answers
                      else '<td class="na" title="does not answer here"></td>' for d in DOMAINS)
        rows.append(f'<tr><th class="src">{html.escape(src)}'
                    f'<span class="price">{CATALOGUE[src]["price_usdc"]:.4f}</span></th>{tds}</tr>')
    heads = "".join(f'<th class="dom"><span>{html.escape(d)}</span></th>' for d in DOMAINS)
    return (f'<table class="map"><thead><tr><th class="corner">informant</th>{heads}</tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table>')


def build() -> str:
    ps = [collect(p) for p in pundits()]
    total_forecasts = sum(len(p["forecasts"]) for p in ps)
    total_resolved = sum(len(p["resolutions"]) for p in ps)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")

    def row(p: dict) -> str:
        brier = "\u2014" if p["brier"] is None else f"{p['brier']:.4f}"
        pct = p["capacity"].get("pct_used", 0) * 100
        return (f'<tr><td class="who">{html.escape(p["id"])}</td>'
                f'<td>{len(p["forecasts"])}</td><td>{len(p["resolutions"])}</td>'
                f'<td>{brier}</td><td>{p["consultations"]}</td>'
                f'<td>{p["spend"]:.4f}</td><td>{pct:.2f}%</td></tr>')

    standings = "".join(row(p) for p in
                        sorted(ps, key=lambda x: (x["brier"] is None, x["brier"] or 0)))

    maps = "".join(
        f'<section class="pundit"><h3>{html.escape(p["id"])}'
        f'<span class="sub">{len(p["resolutions"])} resolved · '
        f'{p["spend"]:.4f} USDC spent</span></h3>{trust_map(p)}</section>' for p in ps)

    empty_note = "" if total_resolved else (
        '<p class="warn">No resolved forecasts yet, so no source has earned or burned '
        'trust. The grid fills in as the league runs and the resolver scores outcomes. '
        'Everything below is real state read from the pundit databases; nothing here '
        'is simulated.</p>')

    return f"""<!doctype html>
<meta charset="utf-8">
<title>RECEIPTS — trust maps</title>
<style>
  :root {{
    --bg:#0b0d10; --panel:#12161b; --line:#222a33; --ink:#e6edf3; --dim:#8b98a5;
    --good:#2ea043; --bad:#c93c37; --prov:#9e6a03; --arch:#30363d;
  }}
  * {{ box-sizing:border-box }}
  body {{ margin:0; background:var(--bg); color:var(--ink);
    font:14px/1.5 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace; padding:32px 24px 64px }}
  header {{ max-width:1100px; margin:0 auto 28px }}
  h1 {{ font-size:20px; margin:0 0 4px; letter-spacing:.14em }}
  .tag {{ color:var(--dim); font-size:12px }}
  main {{ max-width:1100px; margin:0 auto }}
  h2 {{ font-size:13px; letter-spacing:.16em; color:var(--dim); text-transform:uppercase;
    margin:34px 0 10px; font-weight:600 }}
  .warn {{ background:var(--panel); border:1px solid var(--line); border-left:3px solid var(--prov);
    padding:12px 14px; color:var(--dim); font-size:13px; border-radius:4px }}
  table {{ border-collapse:collapse; width:100%; background:var(--panel);
    border:1px solid var(--line); border-radius:6px; overflow:hidden }}
  th,td {{ padding:7px 9px; text-align:left; border-bottom:1px solid var(--line); font-size:12px }}
  thead th {{ color:var(--dim); font-weight:600; background:#0f1318 }}
  .stand td {{ font-variant-numeric:tabular-nums }}
  .who {{ color:var(--ink) }}
  section.pundit {{ margin:20px 0 30px }}
  section.pundit h3 {{ font-size:13px; margin:0 0 8px; letter-spacing:.1em }}
  .sub {{ color:var(--dim); font-weight:400; margin-left:10px; letter-spacing:0 }}
  table.map th.corner {{ width:170px }}
  table.map th.dom span {{ display:inline-block; font-size:11px; color:var(--dim) }}
  table.map th.src {{ color:var(--ink); font-weight:500 }}
  table.map th.src .price {{ float:right; color:var(--dim); font-size:11px }}
  table.map td {{ text-align:center; width:64px; font-variant-numeric:tabular-nums }}
  td.good {{ background:color-mix(in srgb, var(--good) calc(var(--a)*100%), transparent) }}
  td.bad  {{ background:color-mix(in srgb, var(--bad) 55%, transparent) }}
  td.prov {{ background:color-mix(in srgb, var(--prov) 30%, transparent) }}
  td.arch {{ background:repeating-linear-gradient(45deg,var(--arch),var(--arch) 4px,transparent 4px,transparent 8px) }}
  td.none, td.na {{ background:transparent }}
  td.na {{ opacity:.25 }}
  .n {{ font-size:11px }}
  .key {{ display:flex; gap:18px; flex-wrap:wrap; color:var(--dim); font-size:12px; margin-top:10px }}
  .key i {{ display:inline-block; width:11px; height:11px; border-radius:2px; margin-right:6px;
    vertical-align:-1px }}
  footer {{ max-width:1100px; margin:44px auto 0; color:var(--dim); font-size:12px;
    border-top:1px solid var(--line); padding-top:14px }}
</style>
<header>
  <h1>RECEIPTS</h1>
  <div class="tag">a league of AI pundits that learn which informants to trust, and pay for the privilege</div>
  <div class="tag">generated {now} · {len(ps)} pundits · {total_forecasts} forecasts · {total_resolved} resolved</div>
</header>
<main>
  {empty_note}
  <h2>Standings</h2>
  <table class="stand"><thead><tr><th>pundit</th><th>forecasts</th><th>resolved</th>
    <th>brier</th><th>informants bought</th><th>spend USDC</th><th>memory used</th></tr></thead>
    <tbody>{standings or '<tr><td colspan="7">no pundits yet</td></tr>'}</tbody></table>

  <h2>Trust maps</h2>
  <p class="tag">What each pundit believes about each informant, per domain. Learned only by
  paying and watching what resolved. Nothing here was told to it.</p>
  <div class="key">
    <span><i style="background:var(--good)"></i>trusted — brighter is more</span>
    <span><i style="background:var(--bad)"></i>measured worse than the base rate, never bought again</span>
    <span><i style="background:var(--prov)"></i>paid for, not yet proven</span>
    <span><i style="background:var(--arch)"></i>archived after going quiet, recoverable</span>
    <span><i style="background:#1b2027"></i>never bought / does not cover</span>
  </div>
  {maps or '<p class="tag">no pundit databases found</p>'}
</main>
<footer>
  Every figure read live from the pundit SQLite stores through <code>agent/memory.py</code>.
  Reliability is measured from resolved outcomes, never declared.
</footer>
"""


if __name__ == "__main__":
    html = build()
    # docs/ is what GitHub Pages serves, so it is committed. web/ is the local
    # working copy and stays ignored.
    for out in (ROOT / "docs" / "index.html", ROOT / "web" / "index.html"):
        out.parent.mkdir(exist_ok=True)
        out.write_text(html)
        print(f"wrote {out.relative_to(ROOT)} ({out.stat().st_size:,} bytes)")
