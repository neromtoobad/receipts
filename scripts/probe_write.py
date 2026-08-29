"""Process A. Writes, then dies. Run scripts/probe_read.py afterwards.

This pair is the demo's cold-boot beat in miniature: nothing survives the
process boundary except what reached the database.
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from agent.memory import Memory

m = Memory("probe")
m.observe("island_desk", "epl", brier=0.55, base_brier=0.667, cost=0.012)
m.observe("island_desk", "epl", brier=0.57, base_brier=0.667, cost=0.012)
m.observe("island_desk", "epl", brier=0.54, base_brier=0.667, cost=0.012)
m.observe("chalk_desk", "epl", brier=0.67, base_brier=0.667, cost=0.020)
m.observe("chalk_desk", "epl", brier=0.68, base_brier=0.667, cost=0.020)
m.observe("chalk_desk", "epl", brier=0.66, base_brier=0.667, cost=0.020)
m.set_working_set("probe_market", {"budget_left": 0.048, "open_question": "epl result"})
print(f"process A wrote to {m.path.name} as tenant {m.tenant[:8]}... and is exiting")
raise SystemExit(0)
