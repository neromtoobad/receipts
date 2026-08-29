"""Process 1: write, then die. Nothing is returned in memory."""
import sys, time
from sibyl_memory_client import MemoryClient

DB = "/tmp/receipts-spike.db"
PUNDIT_1 = "11111111-1111-1111-1111-111111111111"

m = MemoryClient.local(DB, tenant_id=PUNDIT_1)
t0 = time.perf_counter()
m.set_entity("source_reliability", "odds_feed:football", {
    "hits": 8, "samples": 10, "mean_cost_usdc": 0.04,
    "confidence": 0.71, "last_seen": "2026-08-28T07:00:00Z",
})
m.set_entity("source_reliability", "odds_feed:crypto", {
    "hits": 2, "samples": 9, "mean_cost_usdc": 0.04,
    "confidence": 0.18, "last_seen": "2026-08-28T07:00:00Z",
})
m.set_state("open_question", {"market": "test_001", "budget_left_usdc": 0.10})
m.set_reference("informant_catalogue", {"odds_feed": {"price_usdc": 0.04}})
eid = m.write_event(
    evaluated=["odds_feed said HOME on test_001"],
    acted=["bought odds_feed for 0.04 USDC"],
    forward=["await resolution"],
)
dt = (time.perf_counter() - t0) * 1000
print(f"WROTE ok in {dt:.1f}ms  event={eid}")
sys.exit(0)
