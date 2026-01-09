# SYNAPSE-FI Architecture Documentation

## Architecture Decision Records (ADR)

> This document captures the key architectural decisions made in SYNAPSE-FI and the rationale behind them. Each decision directly supports the system's core principles: privacy, sovereignty, explainability, and real-time operation.

---

## Table of Contents

1. [ADR-001: Federated Architecture Over Centralized](#adr-001)
2. [ADR-002: Behavioral Fingerprints Over Encrypted Data](#adr-002)
3. [ADR-003: Rule-Based Intelligence Over Machine Learning](#adr-003)
4. [ADR-004: Graph-Based Correlation Engine](#adr-004)
5. [ADR-005: Advisory Model Over Command-Control](#adr-005)
6. [ADR-006: In-Memory Graph Over Persistent Database](#adr-006)
7. [ADR-007: One-Way Hash Fingerprints](#adr-007)
8. [ADR-008: Real-Time Stream Processing](#adr-008)
9. [System Architecture Overview](#architecture-overview)
10. [Privacy Architecture](#privacy-architecture)
11. [Data Flow Architecture](#data-flow)
12. [Failure Modes & Resilience](#failure-modes)

---

<a name="adr-001"></a>
## ADR-001: Federated Architecture Over Centralized

### Status
**ACCEPTED** - Core architectural decision

### Context
Traditional fraud detection systems centralize transaction data from multiple institutions into a single database or data warehouse. This approach enables powerful analysis but creates severe privacy, regulatory, and trust issues.

### Decision
SYNAPSE-FI uses a **federated architecture** where:
- Each entity maintains complete sovereignty over its data
- Entities run independent services with local intelligence
- No central entity has access to raw transaction data
- Intelligence emerges through coordination, not aggregation

### Rationale

**Why Federated:**
1. **Privacy Guarantee**: Raw data never leaves institutional boundaries
2. **Regulatory Compliance**: Aligns with GDPR, PCI-DSS, regional banking laws
3. **Trust Model**: No single point of failure or trust concentration
4. **Competitive Protection**: Institutions don't expose proprietary data
5. **Scalability**: Adding entities doesn't require central system redesign

**Why NOT Centralized:**
- ❌ Single point of failure
- ❌ Requires universal trust in central operator
- ❌ Violates data residency requirements
- ❌ Creates liability concentration
- ❌ Difficult to audit for privacy compliance

### Consequences

**Positive:**
- ✅ Privacy by architecture, not policy
- ✅ No single point of compromise
- ✅ Horizontal scalability
- ✅ Regulatory compliance by design

**Negative:**
- ⚠️ More complex deployment (multiple services)
- ⚠️ Coordination overhead between services
- ⚠️ Testing requires multi-service setup

**Mitigation:**
- Docker Compose for simplified local development
- Clear API contracts between services
- Comprehensive integration tests

### Implementation Notes
- Entity services: FastAPI applications running on separate ports
- Hub service: Independent FastAPI application
- Communication: REST APIs for fingerprint submission, SSE for advisories
- No shared databases or state between entities and hub

---

<a name="adr-002"></a>
## ADR-002: Behavioral Fingerprints Over Encrypted Data

### Status
**ACCEPTED** - Critical privacy innovation

### Context
When sharing fraud intelligence, systems typically either:
1. Share raw data (privacy violation)
2. Share encrypted data that can be decrypted by authorized parties
3. Use homomorphic encryption (computationally expensive, still reveals structure)

None of these approaches provide both privacy and performance.

### Decision
SYNAPSE-FI uses **behavioral fingerprints**:
- Abstract behavioral patterns extracted from transactions
- One-way cryptographic hash (SHA-256)
- Irreversible - cannot reconstruct source transaction
- Preserves correlation capability without exposing data

### Rationale

**Why Fingerprints:**
1. **Privacy**: Cannot reverse-engineer original transaction
2. **Performance**: Lightweight, fast to generate and compare
3. **Simplicity**: No key management, no decryption infrastructure
4. **Correlation**: Same behavior produces same fingerprint
5. **Temporal Stability**: Time-bucketing ensures pattern matching

**Fingerprint Composition:**
```
fingerprint = SHA256(pattern_id + severity + time_bucket + entity_salt)
```

**What's Included:**
- Pattern type (e.g., "account_takeover")
- Severity level (LOW, MEDIUM, HIGH, CRITICAL)
- Time bucket (5-minute windows)
- Entity-specific salt (prevents cross-entity fingerprint matching by outsiders)

**What's EXCLUDED:**
- ❌ User IDs, account numbers
- ❌ Transaction amounts
- ❌ Merchant names/IDs
- ❌ Exact timestamps (bucketed)
- ❌ Geographic coordinates (only broad regions if needed)
- ❌ Any personally identifiable information (PII)

**Why NOT Encrypted Data:**
- Encrypted data can be decrypted (key compromise risk)
- Still requires key management infrastructure
- Doesn't prevent data reconstruction
- Homomorphic encryption is too slow for real-time

**Why NOT Differential Privacy:**
- DP adds mathematical noise, reducing detection accuracy
- Requires careful privacy budget management
- More complex to implement and validate
- Fingerprints provide stronger guarantees (complete abstraction)

### Consequences

**Positive:**
- ✅ Provable privacy (fingerprint inversion is cryptographically hard)
- ✅ Fast generation and comparison
- ✅ No key management overhead
- ✅ Simple to audit and verify

**Negative:**
- ⚠️ Loss of granularity (by design)
- ⚠️ Cannot retrieve original transaction from fingerprint
- ⚠️ Time bucketing may delay correlation slightly

**Mitigation:**
- Time buckets are configurable (default 5 minutes)
- Entity retains local logs for detailed investigation
- Fingerprint is sufficient for correlation, not investigation

### Validation
Privacy guarantee can be verified through:
1. **Code Review**: Fingerprint generation code contains no reversible operations
2. **Packet Capture**: Network traffic analysis shows no PII
3. **Hub Inspection**: Hub logs and state contain no transaction data
4. **Cryptographic Proof**: SHA-256 is one-way (pre-image resistance)

---

<a name="adr-003"></a>
## ADR-003: Rule-Based Intelligence Over Machine Learning

### Status
**ACCEPTED** - Explainability requirement

### Context
Modern fraud detection systems increasingly use machine learning (neural networks, random forests, gradient boosting). While ML can achieve high accuracy, it creates explainability and regulatory challenges.

### Decision
SYNAPSE-FI uses **rule-based intelligence** for all decision-critical paths:
- Feature extraction: Deterministic calculations
- Risk scoring: Weighted rule evaluation
- Pattern classification: Signal-to-pattern mapping
- Escalation: Threshold-based logic

ML is permitted for **non-critical paths** (analytics, threshold tuning).

### Rationale

**Why Rules:**
1. **Explainability**: Every decision has human-readable reasoning
2. **Auditability**: Logic can be reviewed and validated
3. **Determinism**: Same inputs always produce same outputs
4. **Regulatory Compliance**: GDPR Article 22 "right to explanation"
5. **Testability**: Rules can be unit tested exhaustively
6. **Trust**: Judges and regulators understand rule-based logic

**Why NOT Pure ML:**
- ❌ Black-box decisions difficult to explain
- ❌ Non-deterministic (model updates change behavior)
- ❌ Requires large training datasets (not available at start)
- ❌ Harder to audit for bias or errors
- ❌ Model drift requires continuous monitoring

**Where ML Could Enhance (Optional):**
- Anomaly detection on BRG structure (non-critical)
- Automatic threshold tuning via reinforcement learning
- Pattern similarity scoring for new patterns
- Predictive analytics for dashboard insights

### Consequences

**Positive:**
- ✅ Complete explainability
- ✅ Deterministic behavior (essential for demos)
- ✅ Easy to test and validate
- ✅ Regulatory confidence
- ✅ No training data required

**Negative:**
- ⚠️ May miss subtle patterns that ML would catch
- ⚠️ Requires manual rule tuning
- ⚠️ Less adaptive to new fraud types

**Mitigation:**
- Rules can be updated based on observed patterns
- Optional ML layer for recommendations (not decisions)
- Clear separation between rule-based decisions and ML analytics

### Example Explainable Decision

```
Decision: BLOCK
Reason: High-risk behavioral pattern detected

Local Risk Analysis:
  Rule 1: Velocity check
    - Transactions in 60s: 8
    - Threshold: 5
    - Result: TRIGGERED (weight: 0.3)
    - Contribution: +30 points

  Rule 2: Device check
    - Device age: 2 minutes
    - Threshold: 1 day
    - Result: TRIGGERED (weight: 0.25)
    - Contribution: +25 points

  Rule 3: Geographic check
    - Previous location: New York
    - Current location: Los Angeles
    - Time between: 30 minutes
    - Result: TRIGGERED (weight: 0.25)
    - Contribution: +25 points

  Local Risk Score: 80/100

BRIDGE Advisory:
  - Pattern fingerprint: fp_a3d7e9f2
  - Seen across: 3 entities
  - Time window: 5 minutes
  - Advisory multiplier: 1.5
  - Adjusted Risk Score: 120/100 (capped at 100)

Final Decision:
  - Adjusted score (100) > Block threshold (70)
  - Action: BLOCK
  - Rationale: Coordinated high-risk pattern detected across multiple institutions
```

This explanation can be presented in court or to regulators.

---

<a name="adr-004"></a>
## ADR-004: Graph-Based Correlation Engine

### Status
**ACCEPTED** - Core intelligence mechanism

### Context
Detecting coordinated fraud requires understanding relationships between behavioral patterns across entities and time. Traditional approaches use:
- Time-series databases (miss relationships)
- Relational databases (poor for graph queries)
- Log aggregation (lacks structure)

### Decision
Use a **Behavioral Risk Graph (BRG)** as the core correlation data structure:
- Nodes: Patterns, Entities, Decisions (optional)
- Edges: OBSERVED_AT, CO_OCCURS_WITH, ESCALATES_TO
- Time-windowed: Automatic pruning of old edges
- In-memory: Fast queries for real-time correlation

### Rationale

**Why Graph:**
1. **Natural Model**: Fraud is about relationships, not isolated events
2. **Query Efficiency**: "Which entities saw this pattern recently?" is O(edges)
3. **Temporal Analysis**: Time-stamped edges enable temporal correlation
4. **Emergent Intelligence**: Patterns in graph structure reveal coordinated attacks
5. **Visualization**: Graph can be visualized for dashboard

**Graph Structure:**
```
[Entity A] --OBSERVED_AT--> [Pattern X] <--OBSERVED_AT-- [Entity B]
                                |
                          ESCALATES_TO
                                |
                                v
                          [Advisory]
```

**Why NOT Alternative Approaches:**

| Approach | Problem |
|---|---|
| Relational DB | Joins are expensive for graph queries |
| Time-series DB | Doesn't capture relationships |
| Document DB | Poor for "who else saw this?" queries |
| Full graph DB | Overkill, adds complexity |

**NetworkX Library:**
- Mature Python graph library
- Supports directed multi-graphs (multiple edges between nodes)
- Fast in-memory operations
- Easy serialization for persistence

### Consequences

**Positive:**
- ✅ Natural representation of fraud relationships
- ✅ Fast correlation queries
- ✅ Enables graph visualization
- ✅ Scales with pattern diversity (not transaction volume)

**Negative:**
- ⚠️ In-memory limits total graph size
- ⚠️ Requires periodic pruning
- ⚠️ More complex than simple key-value store

**Mitigation:**
- Time-window pruning keeps graph bounded
- Graph size ~O(patterns × entities × time_window)
- For 100 patterns × 10 entities × 5 min window: ~5K nodes (small)

### Query Examples

**Q1: Has this pattern been seen at other entities recently?**
```python
observations = brg.get_recent_observations(
    fingerprint="fp_a3d7e9f2",
    time_window=timedelta(minutes=5)
)
unique_entities = len(set(obs['entity_id'] for obs in observations))
```

**Q2: What patterns is Entity A currently observing?**
```python
patterns = list(brg.graph.successors("entity_a"))
```

**Q3: Which patterns led to the most advisories?**
```python
advisory_counts = {}
for node in brg.graph.nodes():
    if brg.graph.nodes[node].get('node_type') == 'pattern':
        advisory_counts[node] = brg.graph.out_degree(node, 'ESCALATES_TO')
```

---

<a name="adr-005"></a>
## ADR-005: Advisory Model Over Command-Control

### Status
**ACCEPTED** - Governance requirement

### Context
In fraud detection collaborations, a central system could either:
1. **Command entities** what to do ("Block this transaction")
2. **Advise entities** on global patterns ("This pattern is suspicious")

Option 1 centralizes liability and removes entity autonomy. Option 2 preserves sovereignty.

### Decision
BRIDGE Hub uses an **advisory model**:
- Hub sends **advisories** (recommendations), not commands
- Entities remain autonomous decision-makers
- Entities can configure how heavily to weight advisories
- Entities can ignore advisories (not recommended, but possible)

### Rationale

**Why Advisory:**
1. **Legal Protection**: Hub doesn't make blocking decisions, entities do
2. **Entity Sovereignty**: Respects institutional independence
3. **Risk Appetite**: Each entity can have different risk tolerance
4. **Regulatory Compliance**: Local decision-making satisfies regulators
5. **Liability Distribution**: Decisions remain with entities

**Advisory Structure:**
```python
{
    "advisory_id": "adv_12345",
    "fingerprint": "fp_a3d7e9f2",
    "confidence": "HIGH",
    "entity_count": 3,
    "time_span_seconds": 180,
    "rationale": "Pattern seen across 3 entities in 3 minutes",
    "recommendation": "ESCALATE_RISK"  # NOT "BLOCK"
}
```

**How Entities Use Advisories:**
- Apply configurable multiplier to risk scores
- Example: HIGH confidence advisory → 1.5× multiplier
- Entity still makes final allow/step-up/block decision

**Why NOT Command-Control:**
- ❌ Centralizes liability at hub
- ❌ Removes entity autonomy
- ❌ Creates single point of control (regulatory concern)
- ❌ Reduces institutional trust

### Consequences

**Positive:**
- ✅ Preserves entity sovereignty
- ✅ Distributes liability appropriately
- ✅ Configurable influence (entities choose weight)
- ✅ Regulatory-friendly model

**Negative:**
- ⚠️ Entities could ignore advisories (reducing effectiveness)
- ⚠️ More complex than centralized control

**Mitigation:**
- Document recommended advisory weights
- Dashboard shows advisory effectiveness metrics
- Entity reputation scoring (optional future feature)

### Governance Implications

**Question**: Who is liable if fraud occurs?
**Answer**: The entity that made the final decision (same as today).

**Question**: What if entity ignores all advisories?
**Answer**: Their choice (sovereignty), but dashboard tracks this for accountability.

**Question**: Can Hub force an entity to block?
**Answer**: No. Hub can only recommend. Entity decides.

---

<a name="adr-006"></a>
## ADR-006: In-Memory Graph Over Persistent Database

### Status
**ACCEPTED** - Performance requirement

### Context
The BRG could be stored in:
1. In-memory data structure
2. Persistent graph database (Neo4j, etc.)
3. Relational database with graph modeling

Real-time correlation requires fast queries. Persistence adds latency.

### Decision
Use **in-memory graph** with optional persistence:
- Primary: NetworkX in-memory graph
- Queries: Direct graph traversal (microseconds)
- Persistence: Optional periodic snapshots to disk
- Recovery: Rebuild from recent snapshots + entity fingerprint replay

### Rationale

**Why In-Memory:**
1. **Speed**: Graph queries in microseconds, not milliseconds
2. **Simplicity**: No database deployment/management
3. **Real-Time**: Sub-second correlation is critical
4. **Bounded Size**: Time-window pruning keeps graph small

**Why NOT Persistent Database:**
- ❌ Network latency to database adds 10-50ms per query
- ❌ Deployment complexity (additional service)
- ❌ Cost (database hosting/licensing)
- ❌ Over-engineering for bounded graph size

**Graph Size Analysis:**
```
Assumptions:
- 10 entities
- 50 distinct pattern types
- 5-minute time window
- 10 fingerprints/minute per entity

Max nodes: 50 patterns + 10 entities = 60 nodes
Max edges: 10 entities × 10 fp/min × 5 min = 500 edges

Memory: ~1MB (negligible)
```

Even with 100 entities and 200 patterns: ~20K edges, ~20MB (still small).

### Consequences

**Positive:**
- ✅ Microsecond query latency
- ✅ Simple deployment (no DB)
- ✅ Low memory usage
- ✅ Easy to test (in-memory)

**Negative:**
- ⚠️ Graph lost if hub crashes (before snapshot)
- ⚠️ Doesn't scale to millions of nodes (not our use case)

**Mitigation:**
- Periodic graph snapshots (every 5 minutes)
- Entities retain fingerprint logs for replay
- In practice, graph rebuilds quickly from entity re-sends

### Recovery Strategy

**If Hub Crashes:**
1. Load most recent graph snapshot
2. Entities continue sending fingerprints
3. Graph repopulates with live data
4. Correlation resumes within 1-2 time windows

**Loss Window:** Only correlations during crash are lost. Not critical because:
- Fraud patterns persist (will reappear)
- Entities still have local intelligence
- Next occurrence will be correlated

---

<a name="adr-007"></a>
## ADR-007: One-Way Hash Fingerprints

### Status
**ACCEPTED** - Privacy guarantee

### Context
Fingerprints must be:
- Consistent (same pattern → same fingerprint)
- Private (fingerprint → cannot reverse to pattern details)
- Fast (generate in microseconds)

### Decision
Use **SHA-256 one-way hash** with structure:
```
fingerprint = "fp_" + SHA256(pattern_id + "|" + severity + "|" + time_bucket + "|" + salt)[:16]
```

### Rationale

**Why SHA-256:**
1. **One-Way**: Pre-image resistance (cannot reverse)
2. **Collision Resistance**: Different inputs produce different hashes
3. **Fast**: Generates in microseconds
4. **Standard**: Well-understood, widely audited
5. **Proven**: No known practical attacks

**Fingerprint Components:**
- `pattern_id`: Behavioral pattern type (e.g., "account_takeover")
- `severity`: Risk level (LOW, MEDIUM, HIGH, CRITICAL)
- `time_bucket`: Timestamp rounded to 5-minute windows
- `salt`: Entity-specific secret (prevents rainbow table attacks)

**Why Time Bucketing:**
- Transactions at 14:32:15 and 14:34:20 should correlate
- Bucketing to 5-minute windows: both map to 14:30:00 bucket
- Enables correlation across slightly different timing
- Reduces fingerprint diversity (good for correlation)

**Why Entity Salt:**
- Prevents external attacker from generating valid fingerprints
- Each entity has unique salt (in config)
- Attacker cannot test pattern hypotheses without salt

### Consequences

**Positive:**
- ✅ Cryptographically secure privacy
- ✅ Fast generation
- ✅ Enables correlation (same pattern → same fingerprint)
- ✅ Simple implementation

**Negative:**
- ⚠️ Cannot reverse fingerprint to investigate
- ⚠️ Salt must be kept secret
- ⚠️ Time bucketing may miss correlations across bucket boundaries

**Mitigation:**
- Entities retain local logs for investigation
- Salt stored in environment variables, never committed
- Overlapping time windows can mitigate bucket boundary issues

### Privacy Proof

**Claim**: Given fingerprint `fp_a3d7e9f2`, attacker cannot determine source transaction.

**Proof Sketch**:
1. SHA-256 has pre-image resistance (cryptographic property)
2. Fingerprint includes only: pattern_id, severity, time_bucket
3. Even if attacker knows all patterns and severities, salt prevents testing
4. Without salt, testing still requires pattern knowledge
5. Transaction details (amount, user, merchant) never enter hash

**Result**: Fingerprint provides k-anonymity where k = number of transactions matching the same pattern + severity + time_bucket.

---

<a name="adr-008"></a>
## ADR-008: Real-Time Stream Processing

### Status
**ACCEPTED** - Performance requirement

### Context
Fraud detection effectiveness depends on response time:
- Batch processing: Hours old (ineffective)
- Mini-batch: Minutes old (better, but delayed)
- Stream processing: Sub-second (ideal)

### Decision
Use **real-time stream processing**:
- Transactions processed individually as they arrive
- Async/await for non-blocking I/O
- No queuing for batch processing
- Decision latency < 200ms (target)

### Rationale

**Why Real-Time:**
1. **Fraud Window**: Fraudsters act quickly (minutes, not hours)
2. **Transaction Authorization**: Payment systems expect sub-second response
3. **Attack Prevention**: Blocking early stops cascading fraud
4. **User Experience**: Customers expect instant authorization

**Architecture:**
```
Transaction → Risk Score → Pattern → Fingerprint → Hub
     ↓
  Decision (allow/block/step-up)
     ↓
  Customer Response (< 200ms)
```

**Async Processing:**
- Hub communication is async (don't block transaction)
- Advisory processing is async (entities subscribe to stream)
- Graph updates are async (background thread)

**Why NOT Batch:**
- ❌ Hours of delay → fraud completed before detection
- ❌ Misses time-critical correlation opportunities
- ❌ Poor user experience (delayed authorizations)

### Consequences

**Positive:**
- ✅ Sub-second fraud detection
- ✅ Real-time correlation
- ✅ Immediate fraud prevention
- ✅ Good user experience

**Negative:**
- ⚠️ More complex than batch (async programming)
- ⚠️ Requires performance optimization
- ⚠️ Higher infrastructure requirements

**Mitigation:**
- FastAPI handles async naturally
- Careful profiling to meet latency targets
- Horizontal scaling if needed

### Performance Budget

| Component | Target Latency | Measured |
|---|---|---|
| Feature Extraction | < 20ms | TBD |
| Risk Scoring | < 30ms | TBD |
| Pattern Classification | < 10ms | TBD |
| Fingerprint Generation | < 5ms | TBD |
| Hub Send (async) | Non-blocking | - |
| **Total (Local)** | **< 100ms** | TBD |
| Hub Correlation | < 50ms | TBD |
| Advisory Broadcast | < 100ms | TBD |
| **End-to-End** | **< 200ms** | TBD |

---

<a name="architecture-overview"></a>
## System Architecture Overview

### High-Level Components

```
┌─────────────────────────────────────────────────────────────┐
│                     DASHBOARD / UI                          │
│  (Real-time monitoring, Graph viz, Audit logs)              │
└────────────────────┬────────────────────────────────────────┘
                     │ (Read-only queries)
                     ↓
┌─────────────────────────────────────────────────────────────┐
│                    BRIDGE HUB                                │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Behavioral Risk Graph (BRG)                         │   │
│  │  - Pattern nodes, Entity nodes                       │   │
│  │  - Time-windowed edges                               │   │
│  │  - In-memory, auto-pruning                           │   │
│  └──────────────────────────────────────────────────────┘   │
│                     ↓                                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Temporal Correlator                                 │   │
│  │  - Detect cross-entity patterns                      │   │
│  └──────────────────────────────────────────────────────┘   │
│                     ↓                                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Escalation Engine                                   │   │
│  │  - Evaluate if advisory needed                       │   │
│  └──────────────────────────────────────────────────────┘   │
│                     ↓                                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Advisory Builder                                    │   │
│  │  - Construct advisory messages                       │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────┬──────────────────────────────────┬───────────────┘
           │ Advisories (SSE)                 │
           ↓                                  ↓
┌─────────────────────────┐      ┌─────────────────────────┐
│    ENTITY A             │      │    ENTITY B             │
│                         │      │                         │
│  ┌──────────────────┐   │      │  ┌──────────────────┐   │
│  │ Txn Stream       │   │      │  │ Txn Stream       │   │
│  └────────┬─────────┘   │      │  └────────┬─────────┘   │
│           ↓             │      │           ↓             │
│  ┌──────────────────┐   │      │  ┌──────────────────┐   │
│  │ Risk Engine      │   │      │  │ Risk Engine      │   │
│  └────────┬─────────┘   │      │  └────────┬─────────┘   │
│           ↓             │      │           ↓             │
│  ┌──────────────────┐   │      │  ┌──────────────────┐   │
│  │ Pattern Class.   │   │      │  │ Pattern Class.   │   │
│  └────────┬─────────┘   │      │  └────────┬─────────┘   │
│           ↓             │      │           ↓             │
│  ┌──────────────────┐   │      │  ┌──────────────────┐   │
│  │ Fingerprint Gen. │───┼──────┼──┤ Fingerprint Gen. │   │
│  └──────────────────┘   │      │  └──────────────────┘   │
│           ↓             │      │           ↓             │
│  ┌──────────────────┐   │      │  ┌──────────────────┐   │
│  │ Decision Engine  │   │      │  │ Decision Engine  │   │
│  └──────────────────┘   │      │  └──────────────────┘   │
│  (allow/step-up/block)  │      │  (allow/step-up/block)  │
└─────────────────────────┘      └─────────────────────────┘
```

### Component Responsibilities

**Entity Services:**
- Transaction ingestion and streaming
- Local risk scoring (feature extraction → scoring)
- Behavioral pattern classification
- Privacy-preserving fingerprint generation
- Autonomous decision making
- Explanation generation
- Hub communication (send fingerprints, receive advisories)

**BRIDGE Hub:**
- Fingerprint reception from all entities
- Behavioral Risk Graph maintenance
- Temporal correlation detection
- Intent escalation evaluation
- Advisory construction and broadcasting
- Hub state management (for dashboard)

**Dashboard:**
- Real-time monitoring of transactions and patterns
- BRG graph visualization
- Advisory timeline
- Audit log viewer
- Entity participation metrics
- System health monitoring

---

<a name="privacy-architecture"></a>
## Privacy Architecture

### Privacy Boundaries

```
┌─────────────────────────────────────────────────────────────┐
│                    ENTITY BOUNDARY                          │
│  (All PII stays within this boundary)                       │
│                                                              │
│  ┌────────────────────────────────────────────────────┐     │
│  │ Raw Transaction                                    │     │
│  │ {                                                  │     │
│  │   user_id: "U123456",         ← PRIVATE           │     │
│  │   amount: 1500.00,            ← PRIVATE           │     │
│  │   merchant: "Store X",        ← PRIVATE           │     │
│  │   account: "ACC789",          ← PRIVATE           │     │
│  │   ip: "192.168.1.1",          ← PRIVATE           │     │
│  │   location: "NYC"             ← PRIVATE           │     │
│  │ }                                                  │     │
│  └───────────────────┬────────────────────────────────┘     │
│                      ↓                                       │
│              Feature Extraction                              │
│                      ↓                                       │
│  ┌────────────────────────────────────────────────────┐     │
│  │ Behavioral Features (still somewhat detailed)      │     │
│  │ {                                                  │     │
│  │   velocity: 8 txn/min,                            │     │
│  │   device_age: 2 minutes,                          │     │
│  │   amount_deviation: +300%                         │     │
│  │ }                                                  │     │
│  └───────────────────┬────────────────────────────────┘     │
│                      ↓                                       │
│           Pattern Classification                             │
│                      ↓                                       │
│  ┌────────────────────────────────────────────────────┐     │
│  │ Pattern (abstract)                                 │     │
│  │ pattern_id: "ACCOUNT_TAKEOVER"                     │     │
│  │ severity: "HIGH"                                   │     │
│  └───────────────────┬────────────────────────────────┘     │
│                      ↓                                       │
│           One-Way Hash Fingerprint                           │
│                      ↓                                       │
│  ┌────────────────────────────────────────────────────┐     │
│  │ Fingerprint (completely abstract, shareable)       │     │
│  │ {                                                  │     │
│  │   fingerprint: "fp_a3d7e9f2",  ← SHAREABLE        │     │
│  │   severity: "HIGH",            ← SHAREABLE        │     │
│  │   timestamp: 1704893425        ← SHAREABLE        │     │
│  │ }                                                  │     │
│  │ NO user_id, amount, merchant, account              │     │
│  └───────────────────┬────────────────────────────────┘     │
└────────────────────────┼────────────────────────────────────┘
                         │
          === PRIVACY BOUNDARY ===
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                    BRIDGE HUB                                │
│  (Only sees fingerprints, never raw data)                   │
│                                                              │
│  ┌────────────────────────────────────────────────────┐     │
│  │ Behavioral Risk Graph                              │     │
│  │ Nodes: [fp_a3d7e9f2] [fp_b2c8d4] [Entity A] [B]   │     │
│  │ Edges: Entity A --observed--> fp_a3d7e9f2         │     │
│  │                                                    │     │
│  │ NO transaction data                                │     │
│  │ NO user identities                                 │     │
│  │ NO amounts                                         │     │
│  └────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

### Privacy Guarantees

1. **Data Minimization**: Only share what's necessary (fingerprints)
2. **Abstraction**: Multiple layers of abstraction before sharing
3. **One-Way Transformation**: Cannot reverse fingerprint to source
4. **No PII**: Zero personally identifiable information crosses boundary
5. **Schema Blindness**: Hub has no knowledge of transaction structure
6. **Temporal Abstraction**: Time bucketing adds ambiguity

---

<a name="data-flow"></a>
## Data Flow Architecture

### Normal Transaction Flow (No Fraud)

```
1. Transaction arrives at Entity A
   ↓
2. Feature extraction (velocity, device, geo, etc.)
   ↓
3. Risk scoring → Score: 25/100 (low risk)
   ↓
4. Pattern classification → "NORMAL"
   ↓
5. Fingerprint generation → fp_12345
   ↓
6. Send fingerprint to Hub (async, non-blocking)
   ↓
7. Hub adds to BRG
   ↓
8. Hub checks correlation → None found (only one entity)
   ↓
9. No advisory generated
   ↓
10. Entity makes decision → ALLOW
    ↓
11. Transaction approved
```

### Coordinated Fraud Detection Flow

```
Time T+0: Transaction at Entity A
   ↓
1. Risk scoring → Score: 75/100 (high risk)
   ↓
2. Pattern → "ACCOUNT_TAKEOVER"
   ↓
3. Fingerprint → fp_fraud_123
   ↓
4. Send to Hub
   ↓
5. Hub adds to BRG
   ↓
6. Correlation check → Only 1 entity (no correlation yet)
   ↓
7. Local decision → ALLOW (high risk but not confirmed)

Time T+3min: Same pattern at Entity B
   ↓
1. Risk scoring → Score: 80/100
   ↓
2. Pattern → "ACCOUNT_TAKEOVER"
   ↓
3. Fingerprint → fp_fraud_123 (SAME as Entity A!)
   ↓
4. Send to Hub
   ↓
5. Hub adds to BRG
   ↓
6. Correlation check → FOUND! 2 entities in 3 minutes
   ↓
7. Escalation evaluation → ESCALATE (meets threshold)
   ↓
8. Advisory creation → confidence: HIGH
   ↓
9. Broadcast advisory to ALL entities

Time T+3min+5s: Advisory received by Entity A
   ↓
1. Advisory stored locally
   ↓
2. Future transactions with fp_fraud_123 will use advisory
   ↓
3. Risk multiplier applied (1.5×)

Time T+5min: Another transaction at Entity A
   ↓
1. Risk score: 75/100
   ↓
2. Pattern → fp_fraud_123
   ↓
3. Check advisories → FOUND matching advisory!
   ↓
4. Apply multiplier: 75 × 1.5 = 112 (capped at 100)
   ↓
5. Decision → BLOCK (exceeds threshold)
   ↓
6. Fraud prevented!
```

---

<a name="failure-modes"></a>
## Failure Modes & Resilience

### Failure Mode 1: Hub Unavailable

**Scenario**: BRIDGE Hub crashes or is unreachable

**Impact**:
- ❌ No new fingerprints received
- ❌ No new correlations detected
- ❌ No new advisories generated

**Resilience**:
- ✅ Entities continue operating with local intelligence
- ✅ Existing advisories still active
- ✅ No transactions blocked due to hub failure
- ✅ When hub recovers, entities resume sending fingerprints

**Mitigation**:
- Entity fingerprint sending has retry logic (exponential backoff)
- Hub stores recent fingerprints on restart
- Health checks detect hub failures quickly

### Failure Mode 2: Network Partition

**Scenario**: Entity A can't reach Hub, but Entity B can

**Impact**:
- ⚠️ Entity A misses new advisories
- ⚠️ Entity A's fingerprints don't contribute to correlation

**Resilience**:
- ✅ Entity A continues with local intelligence
- ✅ Entity B and Hub continue collaborating
- ✅ When network recovers, Entity A catches up

**Mitigation**:
- Advisory messages include timestamps
- Entities can request missed advisories on reconnect
- Dashboard shows entity connectivity status

### Failure Mode 3: Entity Crash

**Scenario**: Entity A crashes mid-transaction

**Impact**:
- ❌ Transaction may not complete
- ⚠️ Fingerprint may not be sent to Hub

**Resilience**:
- ✅ Other entities unaffected
- ✅ Hub continues correlating for other entities
- ✅ When Entity A restarts, normal operation resumes

**Mitigation**:
- Transaction processing is atomic (decision made before response)
- Fingerprint sending is best-effort (not critical for local decision)
- Entity restart is fast (stateless except for history)

### Failure Mode 4: False Positive Advisory

**Scenario**: Hub generates advisory for benign pattern

**Impact**:
- ⚠️ Legitimate transactions may be blocked

**Resilience**:
- ✅ Entity sovereignty: can override advisory
- ✅ Advisory has expiration (time-windowed)
- ✅ Dashboard tracks false positive rate

**Mitigation**:
- Escalation thresholds tuned conservatively
- Entity can adjust advisory weights
- Manual advisory removal via dashboard (admin)

### Failure Mode 5: Privacy Violation (Code Bug)

**Scenario**: Bug causes PII to leak into fingerprint

**Impact**:
- ❌❌❌ Core privacy guarantee violated

**Prevention**:
- ✅ Unit tests verify fingerprint contains no PII
- ✅ Integration tests capture network traffic (automated PII detection)
- ✅ Code review checklist includes privacy verification
- ✅ Fingerprint generation is isolated, well-tested module
- ✅ Hub rejects fingerprints with suspicious structure (validation)

**Detection**:
- Automated tests run on every commit
- Packet capture analysis in CI/CD
- Hub validation of fingerprint format

---

## Conclusion

These architectural decisions form the foundation of SYNAPSE-FI. Each decision prioritizes:

1. **Privacy** - Multiple layers of protection, privacy by architecture
2. **Sovereignty** - Entity autonomy in decisions and data ownership
3. **Explainability** - Human-readable reasoning for all decisions
4. **Performance** - Real-time fraud detection with sub-second latency
5. **Simplicity** - Avoid over-engineering, use proven approaches

The architecture is **defensible** - every design choice has clear rationale and can be explained to judges, regulators, and technical reviewers.

---

**Document Version**: 1.0  
**Last Updated**: January 9, 2026  
**Authors**: Team VIT-Vortex  
**Status**: Living document - will be updated as implementation progresses
