#!/bin/sh
# Rebuild the trust map and publish it to GitHub Pages.
#
#   ./scripts/publish_site.sh
#
# Commits docs/index.html and pushes. Only run this when you want the public
# leaderboard updated — it is an outward-facing action, so the league loop does
# NOT call it unless PUBLISH=1 is set explicitly.
set -eu
cd "$(dirname "$0")/.."
. .venv/bin/activate
python -m web.export >/dev/null            # refresh league.json
(cd site && npm run export >/dev/null)     # build the real site into docs/
if git diff --quiet -- docs/index.html; then
  echo "no change to publish"
  exit 0
fi
git add docs/index.html
git commit -q -m "site: trust map $(date -u +%Y-%m-%dT%H:%MZ)"
git push -q origin main
echo "published: https://neromtoobad.github.io/receipts/"
