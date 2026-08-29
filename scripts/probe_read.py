"""Process B. Boots cold with no shared state and recalls what A wrote."""
import sys, pathlib, time
t0 = time.perf_counter()
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from agent.memory import Memory

m = Memory("probe")
t_boot = time.perf_counter()
island = m.get_reliability("island_desk", "epl")
chalk = m.get_reliability("chalk_desk", "epl")
t_read = time.perf_counter()
hits = m.recall("island_desk")
ws = m.get_working_set("probe_market")
t_end = time.perf_counter()

print(f"process B booted cold, knowing nothing.")
print(f"  island_desk:epl  skill {island['skill']:+.3f}  trust {island['trust']:.3f}  n={island['n']}")
print(f"  chalk_desk:epl   skill {chalk['skill']:+.3f}  trust {chalk['trust']:.3f}  n={chalk['n']}")
print(f"  fts recall returned {len(hits)} rows; working set {ws}")
print(f"  boot {(t_boot-t0)*1000:.1f}ms  entities {(t_read-t_boot)*1000:.1f}ms  "
      f"search+state {(t_end-t_read)*1000:.1f}ms  TOTAL {(t_end-t0)*1000:.1f}ms")
print()
print("  decision it can now make without being told anything:")
print(f"    buy island_desk (trust {island['trust']:.2f}), skip chalk_desk (trust {chalk['trust']:.2f})")
