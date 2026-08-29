"""Can pundit 5 read what pundit 1 learned? The opinion market depends on this."""
from sibyl_memory_client import MemoryClient, FREE_TIER_CAP_BYTES
import os

DB = "/tmp/receipts-spike.db"
P1 = "11111111-1111-1111-1111-111111111111"
P5 = "55555555-5555-5555-5555-555555555555"

print("FREE_TIER_CAP_BYTES:", FREE_TIER_CAP_BYTES, f"({FREE_TIER_CAP_BYTES/1e6:.1f} MB)")

# 1. isolation: does P5 see P1's row by default?
p5 = MemoryClient.local(DB, tenant_id=P5)
try:
    got = p5.get_entity("source_reliability", "odds_feed:football")
    print("ISOLATION: LEAK - p5 read p1's row directly:", got)
except Exception as e:
    print(f"ISOLATION: ok - p5 blocked ({type(e).__name__})")

# 2. deliberate cross-tenant read via set_tenant on one client
reader = MemoryClient.local(DB, tenant_id=P5)
reader.set_tenant(P1)
peek = reader.get_entity("source_reliability", "odds_feed:football")
print("CROSS-TENANT READ via set_tenant:", "OK" if peek else "FAILED", peek["body"] if peek else "")
reader.set_tenant(P5)
print("switched back, tenant is now:", reader.get_tenant())

# 3. shared 'commons' tenant - the other design option
COMMONS = "99999999-9999-9999-9999-999999999999"
c = MemoryClient.local(DB, tenant_id=COMMONS)
c.set_entity("peer_reliability", "pundit_1:football", {"hits": 7, "samples": 9})
c2 = MemoryClient.local(DB, tenant_id=COMMONS)
print("COMMONS TENANT read:", c2.get_entity("peer_reliability", "pundit_1:football")["body"])

# 4. lifecycle: archive + status filter (day 4 needs this)
p1 = MemoryClient.local(DB, tenant_id=P1)
p1.archive_entity("source_reliability", "odds_feed:crypto", reason="stale 3 days")
active = p1.list_entities("source_reliability")
print("ACTIVE after archive:", [e["name"] for e in active])
try:
    arch = p1.list_entities("source_reliability", status="archived")
    print("ARCHIVED listable:", [e["name"] for e in arch])
except Exception as e:
    print("ARCHIVED listing:", type(e).__name__, e)
try:
    print("archived entity still gettable:", bool(p1.get_entity("source_reliability", "odds_feed:crypto")))
except Exception as e:
    print("archived entity get:", type(e).__name__)

print("\nDB size:", os.path.getsize(DB), "bytes")
