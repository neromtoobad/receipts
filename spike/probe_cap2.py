import os, sqlite3
from sibyl_memory_client import MemoryClient, Storage, FREE_TIER_CAP_BYTES

def run(label, db, n, extra_fn):
    if os.path.exists(db): os.remove(db)
    m = MemoryClient.local(db, tenant_id="11111111-1111-1111-1111-111111111111")
    m.set_entity("warm","seed",{"x":1})
    base_file = os.path.getsize(db)
    conn = sqlite3.connect(db); base_log = Storage.logical_size_bytes(conn); conn.close()
    for i in range(n):
        m.write_event(**extra_fn(i))
    file_sz = os.path.getsize(db)
    conn = sqlite3.connect(db); log_sz = Storage.logical_size_bytes(conn); conn.close()
    print(f"{label:28} file={(file_sz-base_file)/n:7.0f} B/ev   logical={(log_sz-base_log)/n:7.0f} B/ev"
          f"   total_logical={log_sz/1024:7.0f} KB  file={file_sz/1024:7.0f} KB")
    return (log_sz-base_log)/n

TRACE = ("Bought odds_feed (0.04) and form_api (0.01); skipped tipster_llm because confidence "
         "0.18 over 11 samples in this domain. Odds imply 0.62 home; form disagrees on recent "
         "away record. Weighting odds 0.7 given its 8/10 football hit rate. Final: 0.58 HOME.")

fat = lambda i: dict(evaluated=[f"market_{i}: odds_feed HOME 0.62, form_api AWAY"],
                     acted=[f"bought odds_feed 0.04, form_api 0.01; forecast 0.58 HOME"],
                     forward=["await resolution"],
                     extra={"trace": TRACE, "market": f"market_{i}", "cost_usdc": 0.05})
lean = lambda i: dict(acted=[f"m{i} buy=odds,form c=0.05 p=0.58"],
                      extra={"m": i, "srcs": ["odds","form"], "p": 0.58, "c": 0.05})

print("FREE_TIER_CAP_BYTES:", FREE_TIER_CAP_BYTES)
a = run("fat trace (as designed)", "/tmp/cap-fat.db", 400, fat)
b = run("lean event", "/tmp/cap-lean.db", 400, lean)
print()
for label, per in (("fat", a), ("lean", b)):
    total = int(FREE_TIER_CAP_BYTES/per)
    print(f"{label:5} -> {total:,} events under cap = {total//6:,} per pundit = {total//6//10:,} per pundit per day")
