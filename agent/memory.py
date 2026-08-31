"""Every Sibyl Memory call in RECEIPTS lives in this file. Nothing else imports
the SDK.

A judge asked to find where memory is written and read should need one file and
about fifteen seconds. The rules give them two minutes.

Layout, decided by measurement in proof/PHASE0_FINDINGS.md:
  memory/pundit_<n>.db   one database per pundit. The free cap is enforced PER
                         FILE, so each identity gets the full 5,242,880 bytes,
                         which is 1,757 traced forecasts each.
  memory/commons.db      peer reputation, written and read by every pundit. This
                         is the coordination surface for the opinion market.

Tiers, and what each one is actually for here:
  HOT   set_state      this turn's working set, and provisional sources that have
                       not yet earned an entity
  WARM  set_entity     source_reliability per (source, domain); peer_reliability
                       per (agent, domain) in the commons
  COLD  write_event    every consultation and every forecast. The resolver reads
                       this back; it is also the audit trail
  REF   set_reference  informant catalogue, domain taxonomy, pricing note
  ARCH  archive_entity sources that have gone quiet. Recoverable, which is the
                       point of archiving rather than deleting
"""
from __future__ import annotations

import os
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sibyl_memory_client import MemoryClient

ROOT = Path(__file__).resolve().parent.parent
MEMORY_DIR = ROOT / "memory"

# Lifecycle constants. Tuned against the corpus, not guessed. See proof/DOMAINS.md.
PROMOTE_N = 3        # resolved observations before a provisional source earns an entity
STALE_DAYS = 3       # silence after which a source is archived
TRUST_SHRINK = 5     # observations at which trust reaches half its evidence weight
SKILL_FULL_TRUST = 0.12   # measured ceiling: the best desk inside its beat scores +0.12

CAT_SOURCE = "source_reliability"
CAT_PEER = "peer_reliability"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _days_since(iso: str | None) -> float:
    if not iso:
        return 0.0
    try:
        then = datetime.fromisoformat(iso)
    except ValueError:
        return 0.0
    if then.tzinfo is None:
        then = then.replace(tzinfo=timezone.utc)
    return (datetime.now(timezone.utc) - then).total_seconds() / 86400.0


def tenant_for(pundit_id: str) -> str:
    """Deterministic tenant UUID per pundit.

    MemoryClient.local() otherwise defaults to 00000000-...-0001 for every
    database, so two pundits would silently share an identity and never error.
    That trap is why this function exists and why the tenant is always explicit.
    """
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"receipts://pundit/{pundit_id}"))


class Memory:
    """One pundit's memory. Open it, use it, let the process die."""

    def __init__(self, pundit_id: str, *, db_path: Path | None = None):
        self.pundit_id = pundit_id
        self.tenant = tenant_for(pundit_id)
        MEMORY_DIR.mkdir(parents=True, exist_ok=True)
        self.path = Path(db_path) if db_path else MEMORY_DIR / f"{pundit_id}.db"
        self.c = MemoryClient.local(str(self.path), tenant_id=self.tenant)

    # ---------- HOT: this turn, and sources not yet proven ----------

    def set_working_set(self, market_id: str, body: dict[str, Any]) -> None:
        self.c.set_state(f"turn:{market_id}", body)

    def get_working_set(self, market_id: str) -> dict[str, Any] | None:
        return self._state_body(f"turn:{market_id}")

    def _state_body(self, key: str) -> dict[str, Any] | None:
        """get_state returns {"body": ..., "updated_at": ...}. Unwrap it, and
        treat an emptied document as absent so a cleared provisional record does
        not read as a real one."""
        doc = self.c.get_state(key)
        if not doc:
            return None
        body = doc.get("body") if isinstance(doc, dict) else None
        return body or None

    def _provisional_key(self, source: str, domain: str) -> str:
        return f"provisional:{source}:{domain}"

    def get_provisional(self, source: str, domain: str) -> dict[str, Any] | None:
        return self._state_body(self._provisional_key(source, domain))

    # ---------- WARM: what this pundit believes about its informants ----------

    @staticmethod
    def _key(source: str, domain: str) -> str:
        return f"{source}:{domain}"

    def get_reliability(self, source: str, domain: str) -> dict[str, Any] | None:
        """Established belief only. Provisional sources deliberately do not
        appear here: an unproven source must not be treated as trusted."""
        try:
            row = self.c.get_entity(CAT_SOURCE, self._key(source, domain))
        except Exception:
            return None
        body = row.get("body", row)
        body["trust"] = self._decayed_trust(body)
        return body

    def all_reliability(self, domain: str | None = None) -> list[dict[str, Any]]:
        out = []
        for row in self.c.list_entities(CAT_SOURCE, limit=500):
            body = row.get("body", row)
            if domain and body.get("domain") != domain:
                continue
            body["trust"] = self._decayed_trust(body)
            out.append(body)
        return out

    @staticmethod
    def _decayed_trust(body: dict[str, Any]) -> float:
        """Trust is skill, shrunk by how little evidence there is, then decayed
        by how long since the source last proved anything."""
        skill = body.get("skill", 0.0)
        n = body.get("n", 0)
        if skill <= 0:
            return 0.0
        raw = min(skill / SKILL_FULL_TRUST, 1.0)
        confidence = n / (n + TRUST_SHRINK)
        staleness = max(0.0, 1.0 - _days_since(body.get("last_seen")) / (STALE_DAYS * 2))
        return round(raw * confidence * staleness, 4)

    # ---------- the lifecycle: HOT -> WARM -> ARCHIVE ----------

    def observe(self, source: str, domain: str, brier: float, base_brier: float,
                cost: float) -> dict[str, Any]:
        """One resolved observation. Called by the resolver, never by the agent.

        Under PROMOTE_N observations a source lives in HOT state. On the
        PROMOTE_N-th it is promoted to a WARM entity and the state is cleared.
        That promotion is a real transition, not a label.
        """
        key = self._key(source, domain)
        existing = self.get_reliability(source, domain)
        prov = None if existing else self.get_provisional(source, domain)
        body = existing or prov or {
            "source": source, "domain": domain, "n": 0, "brier_sum": 0.0,
            "spend_total": 0.0, "first_seen": _now(), "status": "provisional",
        }

        body["n"] += 1
        body["brier_sum"] += brier
        body["spend_total"] = round(body.get("spend_total", 0.0) + cost, 6)
        body["brier_mean"] = body["brier_sum"] / body["n"]
        body["base_brier"] = base_brier
        body["skill"] = round(1.0 - body["brier_mean"] / base_brier, 4) if base_brier else 0.0
        body["last_seen"] = _now()

        if body["n"] >= PROMOTE_N:
            was_provisional = body.get("status") != "established"
            body["status"] = "established"
            self.c.set_entity(CAT_SOURCE, key, body)
            if was_provisional:
                self.c.set_state(self._provisional_key(source, domain), {})
                self.log_event(acted=[f"promoted {key} to an entity after {body['n']} resolved observations"],
                               extra={"kind": "promotion", "source": source, "domain": domain,
                                      "skill": body["skill"]})
        else:
            self.c.set_state(self._provisional_key(source, domain), body)
        return body

    def observe_miss(self, source: str, domain: str, cost: float) -> None:
        """Paid for, and it had nothing. Not a bad answer, so it must not pollute
        the Brier average, but it IS wasted money and the agent should learn it."""
        key = self._key(source, domain)
        body = self.get_reliability(source, domain) or self.get_provisional(source, domain)
        if not body:
            body = {"source": source, "domain": domain, "n": 0, "brier_sum": 0.0,
                    "spend_total": 0.0, "first_seen": _now(), "status": "provisional"}
        body["misses"] = body.get("misses", 0) + 1
        body["spend_total"] = round(body.get("spend_total", 0.0) + cost, 6)
        body["last_seen"] = _now()
        if body.get("status") == "established":
            self.c.set_entity(CAT_SOURCE, key, body)
        else:
            self.c.set_state(self._provisional_key(source, domain), body)

    def sweep_stale(self) -> list[str]:
        """Archive sources that have gone quiet. Recoverable on purpose."""
        archived = []
        for body in self.all_reliability():
            if _days_since(body.get("last_seen")) > STALE_DAYS:
                key = self._key(body["source"], body["domain"])
                self.c.archive_entity(CAT_SOURCE, key,
                                      reason=f"silent for more than {STALE_DAYS} days")
                self.log_event(acted=[f"archived {key} after {STALE_DAYS} days of silence"],
                               extra={"kind": "archive", "source": body["source"],
                                      "domain": body["domain"]})
                archived.append(key)
        return archived

    def list_archived(self) -> list[dict[str, Any]]:
        """The SDK has no read path back: list_entities(status='archived') returns
        empty (verified, proof/PHASE0_FINDINGS.md gate 3). Read the archive table
        directly so 'archiving is recoverable' can be shown rather than claimed."""
        con = sqlite3.connect(str(self.path))
        con.row_factory = sqlite3.Row
        try:
            rows = con.execute(
                "SELECT * FROM archived_entities WHERE tenant_id = ?", (self.tenant,)
            ).fetchall()
        except sqlite3.OperationalError:
            return []
        finally:
            con.close()
        return [dict(r) for r in rows]

    def all_reliability_including_archived(self) -> list[dict[str, Any]]:
        """Active plus archived, tagged. The trust map shows archived sources
        greyed rather than hiding them: 'this one went quiet' is information."""
        import json as _json
        out = [{**b, "archived": False} for b in self.all_reliability()]
        for r in self.list_archived():
            body = r.get("body")
            body = _json.loads(body) if isinstance(body, str) else (body or {})
            if body:
                out.append({**body, "archived": True, "trust": 0.0})
        return out

    def provisional_sources(self) -> list[dict[str, Any]]:
        """Sources being explored but not yet promoted. They belong on the map,
        because 'paid for, not yet proven' is a real state."""
        out = []
        import sqlite3 as _sq
        con = _sq.connect(str(self.path)); con.row_factory = _sq.Row
        try:
            rows = con.execute(
                "SELECT document_key AS key, body FROM state_documents "
                "WHERE tenant_id = ? AND document_key LIKE 'provisional:%'",
                (self.tenant,)).fetchall()
        except _sq.OperationalError:
            return []
        finally:
            con.close()
        import json as _json
        for r in rows:
            try:
                b = _json.loads(r["body"]) if isinstance(r["body"], str) else r["body"]
            except Exception:
                continue
            if b and b.get("source"):
                out.append({**b, "provisional": True, "trust": None})
        return out

    def restore(self, source: str, domain: str) -> dict[str, Any] | None:
        """Bring an archived source back. This is what makes archive != delete."""
        import json
        key = self._key(source, domain)
        for r in self.list_archived():
            if r.get("name") != key:
                continue
            body = r.get("body")
            body = json.loads(body) if isinstance(body, str) else body
            self.c.set_entity(CAT_SOURCE, key, body)
            self.log_event(acted=[f"restored {key} from the archive"],
                           extra={"kind": "restore", "source": source, "domain": domain})
            return body
        return None

    # ---------- COLD: the journal ----------

    def log_consultation(self, market_id: str, source: str, domain: str,
                         cost: float, trust: float | None,
                         payload: dict[str, float] | None = None) -> str:
        """Lean on purpose. Measured at 2,983 bytes for a traced event, so the
        per-consultation record stays small and one fat event per forecast
        carries the reasoning.

        The payload is what the source actually said, and it is not optional
        decoration: the resolver scores each source against the outcome, and it
        can only do that from what was bought at the time. Re-querying later
        would score a different answer, because the odds have moved. A
        probability triple costs about sixty bytes, so this stays lean.
        """
        return self.c.write_event(
            acted=[f"bought {source} for {market_id} at {cost:.4f} USDC"],
            extra={"kind": "consultation", "market": market_id, "source": source,
                   "domain": domain, "cost": cost, "trust": trust, "said": payload},
        )

    def mark_resolved(self, market_id: str, body: dict[str, Any]) -> None:
        self.c.set_state(f"resolved:{market_id}", body)

    def is_resolved(self, market_id: str) -> bool:
        return self._state_body(f"resolved:{market_id}") is not None

    def log_forecast(self, market_id: str, domain: str, probabilities: dict[str, float],
                     confidence: float, reasoning: str, leaned_on: list[str],
                     sources: list[str], spend: float) -> str:
        """The one traced event per forecast. Audit trail, resolver input, and
        the thing the demo shows."""
        return self.c.write_event(
            evaluated=[f"forecast {market_id} ({domain})"],
            acted=[f"probabilities {probabilities}, confidence {confidence:.2f}"],
            forward=[reasoning],
            extra={"kind": "forecast", "market": market_id, "domain": domain,
                   "probabilities": probabilities, "confidence": confidence,
                   "leaned_on": leaned_on, "sources": sources, "spend": round(spend, 6),
                   "pundit": self.pundit_id, "ts": _now()},
        )

    def log_event(self, **kw) -> str:
        return self.c.write_event(**kw)

    def recent_events(self, limit: int = 50) -> list[dict[str, Any]]:
        return self.c.read_events(limit=limit)

    # ---------- REFERENCE ----------

    def set_reference(self, key: str, body: Any) -> None:
        self.c.set_reference(key, body)

    def get_reference(self, key: str) -> Any:
        return self.c.get_reference(key)

    # ---------- search ----------

    def recall(self, query: str, limit: int = 20) -> list[dict[str, Any]]:
        """FTS5 across every tier. No embeddings, no vector index."""
        return self.c.search(query, limit=limit)

    # ---------- housekeeping ----------

    def capacity(self) -> dict[str, Any]:
        """free_tier_status() is authoritative. `sibyl status` divides by 2 MB and
        reports 2.5x the true figure (verified, proof/PHASE0_FINDINGS.md)."""
        return self.c.free_tier_status()


class Commons(Memory):
    """The shared store. Every pundit writes peer reputation here and reads what
    the others wrote. This is the coordination surface, and it is what the
    opinion market in phase 9 trades on."""

    def __init__(self):
        super().__init__("commons", db_path=MEMORY_DIR / "commons.db")
        self.tenant = tenant_for("commons")
        self.c.set_tenant(self.tenant)

    def rate_peer(self, agent_id: str, domain: str, brier: float, base_brier: float) -> dict:
        return self.observe(agent_id, domain, brier, base_brier, cost=0.0)

    def peer_reliability(self, agent_id: str, domain: str) -> dict[str, Any] | None:
        return self.get_reliability(agent_id, domain)
