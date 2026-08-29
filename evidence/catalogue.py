"""The informant catalogue. Moves to evidence/catalogue.py on day 2 and is
written to the REFERENCE tier on first boot.

THE INTEGRITY LINE, and it matters more than any other file here.

There are two audiences and they get different things, on purpose:

  * THE AGENT, at runtime, sees this catalogue. It is vendor marketing. Every
    sentence is literally true and none of it tells you whether a source is any
    good, or which competitions it is actually strong on. That is what a real
    data vendor's pricing page looks like, and it is what leaves the agent with
    something to discover.

  * THE JUDGE, in the README and proof/DOMAINS.md, gets full disclosure: the
    exact data each informant reads, the beat structure, the prices, and the
    measured skill per domain on held-out seasons.

So nothing is hidden from the people assessing the work, and nothing is handed
to the agent that would let it skip the learning. We never state a hit rate
anywhere the agent can read it. Reliability is discovered by paying and watching
what resolves, which is the entire point of the project.
"""

CATALOGUE = {
  "sharp_desk": {
    "name": "Sharp Desk",
    "blurb": "Best available price across the book, aggregated continuously from every "
             "major market maker. Full fixture coverage.",
    "answers_on": ["epl", "championship", "bundesliga", "seriea", "laliga", "ligue1"],
    "price_usdc": 0.0450,
  },
  "island_desk": {
    "name": "Island Desk",
    "blurb": "Market data and public form signals across European football.",
    "answers_on": ["epl", "championship", "bundesliga", "seriea", "laliga", "ligue1"],
    "price_usdc": 0.0120,
  },
  "iberian_desk": {
    "name": "Iberian Desk",
    "blurb": "Market data and public form signals across European football.",
    "answers_on": ["epl", "championship", "bundesliga", "seriea", "laliga", "ligue1"],
    "price_usdc": 0.0120,
  },
  "boot_room": {
    "name": "Boot Room",
    "blurb": "Market data and public form signals across European football.",
    "answers_on": ["epl", "championship", "bundesliga", "seriea", "laliga", "ligue1"],
    "price_usdc": 0.0120,
  },
  "calcio_desk": {
    "name": "Calcio Desk",
    "blurb": "Market data and public form signals across European football.",
    "answers_on": ["epl", "championship", "bundesliga", "seriea", "laliga", "ligue1"],
    "price_usdc": 0.0120,
  },
  "hexagon_desk": {
    "name": "Hexagon Desk",
    "blurb": "Market data and public form signals across European football.",
    "answers_on": ["epl", "championship", "bundesliga", "seriea", "laliga", "ligue1"],
    "price_usdc": 0.0120,
  },
  "chalk_desk": {
    "name": "Chalk Desk",
    "blurb": "Long-run outcome frequencies for every market we cover, refreshed each season.",
    "answers_on": ["epl", "championship", "bundesliga", "seriea", "laliga", "ligue1",
                   "crypto_1h", "crypto_24h"],
    "price_usdc": 0.0200,
  },
  "formline": {
    "name": "Formline",
    "blurb": "Recent-form and momentum differentials computed from public data.",
    "answers_on": ["epl", "championship", "bundesliga", "seriea", "laliga", "ligue1",
                   "crypto_1h", "crypto_24h"],
    "price_usdc": 0.0030,
  },
  "flowdesk": {
    "name": "Flowdesk",
    "blurb": "Perpetual funding rates and derivatives positioning.",
    "answers_on": ["crypto_1h", "crypto_24h"],
    "price_usdc": 0.0150,
  },
  "voldesk": {
    "name": "Voldesk",
    "blurb": "Volume and volatility regime classification.",
    "answers_on": ["crypto_1h", "crypto_24h"],
    "price_usdc": 0.0090,
  },
}

# Note what the agent is NOT told, and could not infer from the above:
#   - five of the six football desks answer on all six leagues but carry
#     market-grade data in only one or two of them
#   - chalk_desk answers on everything and has never had positive skill anywhere
#   - nothing in crypto has ever had positive skill, at any price
#   - price is uncorrelated with quality: the dearest is not the best value in
#     any single domain, and the second dearest is the worst source in the league

def write_reference(memory):
    """Called once on first boot. REFERENCE tier: stable, looked up by name.

    The tenant is bound to the Memory instance, never passed here: agent/memory.py
    is the only place that knows which identity is writing.
    """
    memory.set_reference("informant_catalogue", CATALOGUE)
    memory.set_reference("domain_taxonomy", {
        "football": ["epl", "championship", "bundesliga", "seriea", "laliga", "ligue1"],
        "crypto":   ["crypto_1h", "crypto_24h"],
    })
    memory.set_reference("pricing_note",
        "Price is what a vendor charges. It is not a quality signal and must never "
        "be used as one. What a source is worth is only ever established by "
        "consulting it and scoring what resolved.")
