"""Will 6 pundits x 10 days of journal fit under the 5.2MB free cap?"""
import os, time, json
from sibyl_memory_client import MemoryClient, FREE_TIER_CAP_BYTES

DB = "/tmp/receipts-cap.db"
if os.path.exists(DB): os.remove(DB)

TRACE = ("Bought odds_feed (0.04) and form_api (0.01); skipped tipster_llm because "
         "confidence 0.18 over 11 samples in this domain. Odds imply 0.62 home; form "
         "disagrees on recent away record. Weighting odds 0.7 given its 8/10 football "
         "hit rate. Final: 0.58 HOME, confidence medium.")  # ~realistic trace

base = os.path.getsize(DB) if os.path.exists(DB) else 0
m = MemoryClient.local(DB, tenant_id="11111111-1111-1111-1111-111111111111")
m.set_entity("warm", "seed", {"x": 1})
after_schema = os.path.getsize(DB)
print(f"empty schema baseline: {after_schema/1024:.0f} KB")

N = 500
t0 = time.perf_counter()
for i in range(N):
    m.write_event(
        evaluated=[f"market_{i}: odds_feed HOME 0.62, form_api AWAY"],
        acted=[f"bought odds_feed 0.04, form_api 0.01; forecast 0.58 HOME"],
        forward=["await resolution"],
        extra={"trace": TRACE, "market": f"market_{i}", "cost_usdc": 0.05},
    )
dt = time.perf_counter() - t0
size = os.path.getsize(DB)
per_event = (size - after_schema) / N
print(f"{N} events in {dt:.2f}s ({dt/N*1000:.1f}ms each)")
print(f"DB now {size/1024:.0f} KB -> {per_event:.0f} bytes per journal event")

budget = FREE_TIER_CAP_BYTES - after_schema
print(f"\nheadroom under free cap: {budget/1024:.0f} KB = ~{int(budget/per_event):,} events")
print(f"6 pundits x 10 days: that is {int(budget/per_event)//60:,} forecasts per pundit per day")

# FTS still fast at volume?
t = time.perf_counter(); r = m.search("odds_feed", limit=20); print(f"\nFTS over {N} events: {(time.perf_counter()-t)*1000:.1f}ms, {len(r)} hits")
