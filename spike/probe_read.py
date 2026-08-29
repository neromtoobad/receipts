"""Process 2: fresh boot, empty context. Only disk survives."""
import time
from sibyl_memory_client import MemoryClient

DB = "/tmp/receipts-spike.db"
PUNDIT_1 = "11111111-1111-1111-1111-111111111111"

t0 = time.perf_counter()
m = MemoryClient.local(DB, tenant_id=PUNDIT_1)
boot = (time.perf_counter() - t0) * 1000

t1 = time.perf_counter()
e = m.get_entity("source_reliability", "odds_feed:football")
one = (time.perf_counter() - t1) * 1000

t2 = time.perf_counter()
hits = m.search_entities("odds_feed", category="source_reliability")
fts = (time.perf_counter() - t2) * 1000

t3 = time.perf_counter()
st = m.get_state("open_question")
ev = m.read_events(limit=5)
rest = (time.perf_counter() - t3) * 1000

print(f"boot={boot:.1f}ms  get_entity={one:.1f}ms  fts={fts:.1f}ms  state+events={rest:.1f}ms")
print("RECALLED entity:", e)
print("FTS hits:", len(hits), [h.get("name") for h in hits])
print("state:", st)
print("events:", len(ev))
print("TOTAL COLD-BOOT-TO-DECISION:", f"{boot+one+fts+rest:.1f}ms")
