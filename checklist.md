# 🧠 BACKEND MASTER CHECKLIST

## SYNAPSE-FI + BRIDGE (B1 + B2)

---

## 🟦 SECTION A — SYSTEM INVARIANTS (READ FIRST)

These are **non-negotiable rules** for the entire backend.

* [ ] Raw transaction data **never leaves** entity services
  **Why:** This is the privacy guarantee. Break this and the project collapses.

* [ ] Hub never sees transaction schemas
  **Why:** Hub must be provably blind.

* [ ] Entities decide locally, hub advises globally
  **Why:** Governance and regulator safety.

* [ ] All intelligence is explainable
  **Why:** Judges care more about “why” than accuracy.

---

## 🟩 SECTION B — B1: ENTITY & LOCAL INTELLIGENCE (YOU)

> **Purpose:** Each institution is independently intelligent and sovereign.

---

### B1-1. Entity Service Setup

* [ ] Create **Entity A** service (separate port/process)
* [ ] Create **Entity B** service (separate port/process)

**Explanation:**
Two physical services prove independence. Don’t fake this with flags.

---

### B1-2. Real-Time Transaction Stream

* [ ] Async/WebSocket stream generates transactions
* [ ] 1–2 second interval
* [ ] Deterministic randomness (seeded)

**Explanation:**
Live streams show realism. Determinism avoids demo failure.

---

### B1-3. Feature Extraction Layer

* [ ] Velocity (txn count / time)
* [ ] Device stability (same/new)
* [ ] Geo continuity (same/shift)
* [ ] Merchant repetition

**Explanation:**
These are **behavioral facts**, not predictions.

---

### B1-4. Local Risk Scoring Engine

* [ ] Rule-based scoring (no ML)
* [ ] Output:

  * `risk_score (0–100)`
  * `triggered_signals`

**Explanation:**
Deterministic logic is transparent and defensible.

---

### B1-5. Behavioral Pattern Classification

* [ ] Define ≤ 6 patterns
* [ ] Map signal combinations → pattern ID

Example:

```
HV + NewDevice → PATTERN_X
```

**Explanation:**
This converts **events into behavior**, which is what BRIDGE understands.

---

### B1-6. Risk Fingerprint Generation

* [ ] Hash:

  * pattern_id
  * severity bucket
  * time window
* [ ] One-way, irreversible

**Explanation:**
This is the **only shareable artifact**. It enforces privacy by design.

---

### B1-7. Provisional Local Decision Engine

* [ ] Decide BEFORE hub input
* [ ] Allow / Step-Up / Block

**Explanation:**
Shows sovereignty. The hub does not control entities.

---

### B1-8. Local Explainability Engine

* [ ] Store:

  * local reasons
  * pattern name
  * risk score

**Explanation:**
Feeds final decision explanation.

---

### B1-9. Entity → Hub Communication

* [ ] Send ONLY:

  ```
  { entity_id, fingerprint, severity, timestamp }
  ```

**Explanation:**
Anything more = privacy violation.

---

---

## 🟨 SECTION C — B2: BRIDGE HUB (INDEPENDENT COMPONENTS)

> **Purpose:** Turn isolated risk signals into collective fraud intent.

B2 builds **pure components**, no networking, no entities.

---

## 🧩 B2 COMPONENT 1 — Behavioral Risk Graph (BRG)

### File: `brg_graph.py`

#### What it is

An **in-memory, KG-inspired structure** that stores **relationships**, not data.

#### What it stores

* BehaviorPatternNode (fingerprint)
* EntityNode (A, B)
* Timestamped edges

#### Required capabilities

* Add new pattern nodes
* Link pattern ↔ entity
* Track timestamps & frequency

#### Why this exists

This is **collective memory**.
Without BRG, the system is stateless and dumb.

---

## 🧩 B2 COMPONENT 2 — Temporal Correlation Engine

### File: `temporal_correlator.py`

#### What it is

A stateless utility that answers:

> “Has this behavior pattern appeared across multiple entities recently?”

#### Inputs

* Pattern stats from BRG
* Time window
* Entity threshold

#### Output

* `True / False`

#### Why this exists

Fraud intent is **temporal and distributed**.
Time turns repetition into meaning.

---

## 🧩 B2 COMPONENT 3 — BRIDGE Escalation Engine

### File: `bridge_escalation.py`

#### What it is

A pure **intent evaluator**, not a decision maker.

#### Inputs

* Fingerprint
* Correlation results
* Threshold config

#### Output

Either:

* `None`
* Or an **Intent Alert Object**

Example:

```json
{
  "fingerprint": "X92F",
  "confidence": "HIGH",
  "entities_seen": 2,
  "rationale": "Seen across 2 entities within 300s"
}
```

#### Why this exists

Separates **intelligence discovery** from **action**, which is governance-safe.

---

## 🧩 B2 COMPONENT 4 — Advisory Builder

### File: `advisory_builder.py`

#### What it is

A formatter that converts intent alerts into **safe advisory messages**.

#### Why this exists

Lets you change transport (REST, WS) without touching logic.

---

## 🧩 B2 COMPONENT 5 — Hub State Snapshot (Optional)

### File: `hub_state.py`

#### What it is

Read-only access to:

* Active patterns
* Escalated intents
* Entity participation

#### Why this exists

Feeds dashboard while keeping hub internals hidden.

---

---

## 🟧 SECTION D — B1 ↔ B2 INTEGRATION CHECKLIST

* [ ] Import BRG component
* [ ] Update graph on fingerprint arrival
* [ ] Run temporal correlator
* [ ] If escalation → build advisory
* [ ] Broadcast advisory to entities

**Explanation:**
This is the **only integration point**. Keep it small.

---

## 🟥 SECTION E — FINAL VALIDATION (DO NOT SKIP)

* [ ] Entity decisions change AFTER BRIDGE alert
* [ ] Explanation mentions:

  > “BRIDGE global intent escalation”
* [ ] No raw data in hub logs
* [ ] Demo runs twice cleanly

---

# 🏁 FINAL SUMMARY (Memorize This)

* **B1** = local intelligence + privacy enforcement
* **B2** = collective intent discovery
* **BRIDGE** = intelligence without data movement