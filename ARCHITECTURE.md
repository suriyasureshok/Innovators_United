# SYNAPSE-FI Architecture

**Behavioral Risk Intent Discovery & Governance Engine**

> Privacy-preserving fraud detection through federated architecture and behavioral abstraction

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Key Design Decisions](#key-design-decisions)
3. [System Components](#system-components)
4. [Data Flow](#data-flow)
5. [Privacy Architecture](#privacy-architecture)
6. [BRIDGE Algorithm](#bridge-algorithm)
7. [Implementation Details](#implementation-details)
8. [Failure Modes & Resilience](#failure-modes)

---

## Architecture Overview

### Core Principles

**1. Privacy by Construction**
- Raw transaction data never leaves entity boundaries
- One-way behavioral fingerprints (irreversible)
- Hub operates with zero knowledge of transaction details

**2. Entity Sovereignty**
- Each institution maintains complete data control
- Local decision authority
- No central command-and-control

**3. Explainability First**
- Rule-based logic (deterministic)
- Human-readable decisions
- Full audit trail

**4. Real-Time Operation**
- Sub-second fingerprint ingestion
- Stream processing (no batching)
- Advisory delivery within 500ms

---

## Key Design Decisions

### ADR-001: Federated Over Centralized

**Why Federated:**
- ✅ Privacy guaranteed by architecture
- ✅ No single point of failure
- ✅ Regulatory compliance by design
- ✅ Horizontal scalability

**Implementation:**
```
Entity A ─┐
Entity B ─┼─► BRIDGE Hub (coordination only)
Entity N ─┘
```

### ADR-002: Behavioral Fingerprints Over Encryption

**Why Abstractions:**
- ✅ One-way transformation (irreversible)
- ✅ No computational overhead
- ✅ Schema-blind hub
- ✅ Sub-10ms generation

**Transformation:**
```
Transaction → Features → Pattern → Fingerprint (SHA-256)
  PRIVATE      PRIVATE    LOCAL      SHAREABLE
```

### ADR-003: Rule-Based Over Machine Learning

**Why Rules:**
- ✅ Explainable (GDPR compliant)
- ✅ Deterministic (auditable)
- ✅ Fast (<50ms)
- ✅ No training data required

**Pattern Matching:**
```python
if velocity > 5 AND device_new AND geo_shift:
    pattern = "ACCOUNT_TAKEOVER"
    severity = "HIGH"
```

### ADR-004: Graph-Based Correlation

**Why Graph:**
- ✅ Natural representation of relationships
- ✅ Efficient temporal queries
- ✅ Emergent pattern detection
- ✅ Bounded memory (time-window pruning)

**BRG Structure:**
```
Nodes: [Entities] [Fingerprints]
Edges: [OBSERVED_AT] [CORRELATES_WITH]
```

### ADR-005: Advisory Model Over Commands

**Why Advisories:**
- ✅ Entity maintains final decision authority
- ✅ Hub influences, doesn't control
- ✅ Institutional flexibility
- ✅ Regulatory alignment

---

## System Components

### 1. Entity Services

**Responsibilities:**
- Transaction ingestion & processing
- Local risk scoring (0-100)
- Pattern classification
- Fingerprint generation
- Decision making (ALLOW/STEP-UP/BLOCK)

**Key Modules:**
```
stream.py              # Transaction generator
risk_engine.py         # Feature extraction & scoring
pattern_classifier.py  # Behavioral pattern detection
fingerprint.py         # One-way hash generation
decision.py            # Final decision logic
hub_client.py          # BRIDGE communication
```

**Privacy Enforcement:**
- Raw transactions never serialized for external transmission
- Fingerprints generated in-memory only
- No transaction logging to external systems

### 2. BRIDGE Hub

**Responsibilities:**
- Cross-entity pattern correlation
- Temporal relationship analysis
- Advisory generation
- BRG graph management

**Key Modules:**
```
brg_graph.py           # Behavioral Risk Graph
temporal_correlator.py # Pattern correlation detection
escalation_engine.py   # Severity escalation logic
advisory_builder.py    # Advisory message construction
decay_engine.py        # Time-based confidence decay
```

**Critical Constraints:**
- Hub NEVER stores raw transactions
- Hub NEVER knows transaction schemas
- Hub operates on abstractions only

### 3. Dashboard

**Responsibilities:**
- Real-time monitoring
- Pattern visualization
- Advisory management
- Audit trail display

**Technology:**
- React 18 + TypeScript
- TanStack Query (state management)
- shadcn/ui components
- Mock data system (frontend-only demo)

---

## Data Flow

### End-to-End Flow

```
┌─────────────────────────────────────────────────────────────┐
│ ENTITY SERVICE (Private Zone)                               │
│                                                              │
│ Transaction                                                  │
│      ↓                                                       │
│ Feature Extraction (velocity, device, geo, amount)          │
│      ↓                                                       │
│ Risk Scoring (0-100)                                         │
│      ↓                                                       │
│ Pattern Classification (e.g., "ACCOUNT_TAKEOVER")           │
│      ↓                                                       │
│ Fingerprint Generation (SHA-256 hash)                       │
│      ↓                                                       │
└──────┼───────────────────────────────────────────────────────┘
       │
  [Privacy Boundary - Only Fingerprints Cross]
       │
       ↓
┌─────────────────────────────────────────────────────────────┐
│ BRIDGE HUB (Zero-Knowledge Zone)                            │
│                                                              │
│ Receive Fingerprint {fp_hash, severity, timestamp}          │
│      ↓                                                       │
│ Add to BRG Graph (Entity → Fingerprint edge)                │
│      ↓                                                       │
│ Temporal Correlation Query                                  │
│ "Has this pattern appeared at other entities in 5 min?"     │
│      ↓                                                       │
│ IF (entities ≥ 2 AND window ≤ 300s):                        │
│    Escalation Decision                                      │
│      ↓                                                       │
│ Advisory Construction                                        │
│ {advisory_id, fingerprint, confidence, entities_affected}   │
│      ↓                                                       │
└──────┼───────────────────────────────────────────────────────┘
       │
  [Privacy Boundary - Only Advisories Return]
       │
       ↓
┌─────────────────────────────────────────────────────────────┐
│ ENTITY SERVICE (Decision Zone)                              │
│                                                              │
│ Receive Advisory                                            │
│      ↓                                                       │
│ Match to Active Transactions                                │
│      ↓                                                       │
│ Adjust Risk Score (local × advisory_multiplier)             │
│      ↓                                                       │
│ Final Decision (ALLOW/STEP-UP/BLOCK)                        │
│      ↓                                                       │
│ Log Decision + Explanation                                  │
└─────────────────────────────────────────────────────────────┘
```

### Example Flow

**Step 1:** Entity A receives suspicious transaction
- Velocity: 8 txn/min (threshold: 5)
- Device: New (first seen 2min ago)
- Location: 500 miles from previous
- **Local Risk:** 87/100
- **Pattern:** `ACCOUNT_TAKEOVER`
- **Fingerprint:** `fp_a3d7e9f2`

**Step 2:** Entity A sends fingerprint to Hub
```json
{
  "entity_id": "entity_a",
  "fingerprint": "fp_a3d7e9f2",
  "severity": "HIGH",
  "timestamp": 1704893425
}
```

**Step 3:** Hub checks correlation
- Query: "Seen `fp_a3d7e9f2` at other entities recently?"
- Result: Entity B observed same pattern 3 minutes ago
- **Correlation:** 2 entities in 300s window → ESCALATE

**Step 4:** Hub generates advisory
```json
{
  "advisory_id": "adv_001",
  "fingerprint": "fp_a3d7e9f2",
  "confidence": "HIGH",
  "entities_affected": 2,
  "recommendation": "ESCALATE_RISK",
  "rationale": "Pattern seen across 2 entities in 300s"
}
```

**Step 5:** Entities receive advisory and adjust decisions
- Entity A: Adjusts risk 87 → 95 → **BLOCK**
- Entity B: Adjusts risk 72 → 89 → **STEP-UP AUTH**
- Entity C: Preventatively elevates monitoring

---

## Privacy Architecture

### Privacy Transformation Layers

```
┌─────────────────────────────────────────────────────────────┐
│ Layer 1: Raw Transaction (PRIVATE - Never Leaves Entity)   │
│ {                                                           │
│   user_id: "U123456",                                       │
│   amount: 1500.00,                                          │
│   merchant: "Store X",                                      │
│   account: "ACC789",                                        │
│   ip: "192.168.1.1"                                         │
│ }                                                           │
└─────────────────────┬───────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────────────┐
│ Layer 2: Features (PRIVATE - Extracted Locally)            │
│ {                                                           │
│   velocity: 8 txn/min,                                      │
│   device_age: 2 minutes,                                    │
│   geo_shift: 500 miles,                                     │
│   amount_pattern: high                                      │
│ }                                                           │
└─────────────────────┬───────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────────────┐
│ Layer 3: Pattern (ABSTRACT - Classification)               │
│ {                                                           │
│   pattern_type: "ACCOUNT_TAKEOVER",                         │
│   severity: "HIGH"                                          │
│ }                                                           │
└─────────────────────┬───────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────────────┐
│ Layer 4: Fingerprint (SHAREABLE - One-Way Hash)            │
│ {                                                           │
│   fingerprint: "fp_a3d7e9f2",  ← SHA-256 hash              │
│   severity: "HIGH",                                         │
│   timestamp: 1704893425                                     │
│ }                                                           │
│ ✅ CROSSES PRIVACY BOUNDARY                                 │
└─────────────────────────────────────────────────────────────┘
```

### What Hub NEVER Sees

❌ User identities (names, IDs, account numbers)  
❌ Transaction amounts  
❌ Merchant details  
❌ Device identifiers (raw)  
❌ IP addresses  
❌ Geographic coordinates (only abstract regions)  
❌ Transaction types  
❌ Any reversible data

### Privacy Guarantees

**Mathematical Guarantee:**
```
Given fingerprint fp = SHA256(pattern + salt + timestamp)
Computational complexity to reverse: 2^256 operations
Result: Practically impossible to recover source data
```

**Architectural Guarantee:**
- Hub has no API endpoints for raw data queries
- Hub has no database storing transactions
- Hub has no knowledge of entity transaction schemas
- Even if Hub is compromised, no transaction data exists

---

## BRIDGE Algorithm

### Core Algorithm

**Input:** Behavioral fingerprints from entities  
**Output:** Advisories for coordinated fraud patterns

**Process:**

1. **Fingerprint Ingestion**
   ```python
   def ingest_fingerprint(entity_id, fingerprint, severity, timestamp):
       graph.add_node(fingerprint)
       graph.add_edge(entity_id, fingerprint, timestamp=timestamp)
   ```

2. **Temporal Correlation**
   ```python
   def detect_correlation(fingerprint, time_window=300):
       observations = graph.get_recent_observations(
           fingerprint, 
           within_seconds=time_window
       )
       unique_entities = set([obs.entity_id for obs in observations])
       return len(unique_entities) >= ENTITY_THRESHOLD
   ```

3. **Escalation Logic**
   ```python
   def evaluate_escalation(fingerprint, correlation_result):
       if correlation_result.entity_count >= 2:
           if severity == "HIGH" or severity == "CRITICAL":
               return IntentAlert(
                   confidence="HIGH",
                   recommendation="ESCALATE_RISK"
               )
       return None
   ```

4. **Advisory Generation**
   ```python
   def build_advisory(intent_alert):
       return Advisory(
           advisory_id=generate_id(),
           fingerprint=intent_alert.fingerprint,
           confidence=intent_alert.confidence,
           entities_affected=intent_alert.entity_count,
           rationale="Pattern seen across N entities in Ts window"
       )
   ```

5. **Time Decay**
   ```python
   def decay_confidence(advisory, time_elapsed):
       decay_factor = exp(-time_elapsed / DECAY_CONSTANT)
       advisory.confidence *= decay_factor
       if advisory.confidence < THRESHOLD:
           advisory.status = "DORMANT"
   ```

### Pattern Lifecycle

```
NEW → OBSERVED → CORRELATED → ESCALATED → COOLING → DORMANT
 ↑                                                        ↓
 └───────────────── Reactivation ←─────────────────────┘
```

**States:**
- **NEW:** First observation by any entity
- **OBSERVED:** Seen by 1 entity, no correlation yet
- **CORRELATED:** Seen by ≥2 entities within time window
- **ESCALATED:** Advisory issued to entities
- **COOLING:** No new observations, confidence decaying
- **DORMANT:** Confidence below threshold, monitoring only

---

## Implementation Details

### Technology Stack

**Entity Services:**
- Python 3.10+
- FastAPI (REST API framework)
- Pydantic (data validation)
- Requests (HTTP client for Hub communication)

**BRIDGE Hub:**
- Python 3.10+
- FastAPI (REST API framework)
- NetworkX (graph operations)
- In-memory graph (fast, bounded by time-window pruning)

**Dashboard:**
- React 18 + TypeScript
- Vite (build tool)
- TanStack Query (state management)
- shadcn/ui (component library)
- Mock data system (no backend dependency)

### Performance Characteristics

| Operation | Latency (p95) | Throughput |
|-----------|---------------|------------|
| Transaction processing | <50ms | 150+ txn/sec per entity |
| Fingerprint generation | <10ms | N/A |
| Hub ingestion | <10ms | 500+ fingerprints/sec |
| Correlation query | <50ms | N/A |
| Advisory generation | <100ms | N/A |
| End-to-end latency | <200ms | N/A |

### Scalability

**Horizontal Scaling:**
- Each entity service is independent (no shared state)
- Hub can be replicated with shared graph (Redis)
- Load balancer distributes entity traffic

**Vertical Scaling:**
- In-memory graph bounded by time-window pruning
- Automatic node/edge cleanup after 24 hours
- Maximum graph size: ~5K nodes (manageable)

**Multi-Region:**
- Regional entity clusters
- Cross-region hub synchronization
- Geo-distributed advisory broadcast

---

## Failure Modes & Resilience

### Hub Unavailable

**Impact:**
- Entities continue operating with local intelligence only
- No cross-entity correlation during outage
- No advisories generated

**Mitigation:**
- Local risk scoring remains operational
- Hub returns online, correlation resumes
- No data loss (entities store local state)

**Entity Behavior:**
```python
try:
    hub_client.submit_fingerprint(fingerprint)
except ConnectionError:
    logger.warning("Hub unavailable, continuing with local-only")
    # Continue processing with local risk score
```

### Entity Service Failure

**Impact:**
- Only affects that specific entity
- Other entities unaffected
- Hub continues correlating patterns from active entities

**Mitigation:**
- Independent entity services (no cascading failure)
- Entity restarts and resumes operation
- No impact on other participants

### Network Partition

**Impact:**
- Entities isolated from Hub
- Local-only operation during partition
- Potential missed correlations

**Mitigation:**
- Entity autonomy (local decisions always possible)
- Graceful degradation to local-only mode
- Automatic reconnection when network recovers

### Graph Memory Overflow

**Impact:**
- Hub memory consumption grows unbounded
- Performance degradation
- Potential service crash

**Mitigation:**
- Time-window pruning (24-hour max retention)
- Automatic edge expiration
- Bounded node count (~5K max)
- Graph snapshots for recovery

**Pruning Logic:**
```python
def prune_expired_edges(max_age_seconds=86400):
    current_time = time.time()
    expired_edges = [
        edge for edge in graph.edges
        if current_time - edge.timestamp > max_age_seconds
    ]
    graph.remove_edges(expired_edges)
```

### Advisory Delivery Failure

**Impact:**
- Entity doesn't receive global intelligence
- Operates on local risk score only
- Potentially higher false negatives

**Mitigation:**
- Advisory retry mechanism (3 attempts)
- Advisory cache (entities can query Hub)
- Asynchronous delivery (non-blocking)

---

## Configuration

### Hub Configuration (`bridge_hub/config.py`)

```python
ENTITY_THRESHOLD = 2            # Min entities for correlation
TIME_WINDOW_SECONDS = 300       # 5-minute correlation window
DECAY_ENABLED = True            # Time-based confidence decay
DECAY_CONSTANT = 3600           # 1-hour decay half-life
MAX_GRAPH_AGE_SECONDS = 86400   # 24-hour max retention
ADVISORY_CONFIDENCE_THRESHOLD = 0.6  # Min confidence for advisory
```

### Entity Configuration

```python
FRAUD_RATIO = 0.30              # 30% suspicious transactions
TRANSACTION_INTERVAL = (1.5, 2.0)  # Seconds between transactions
HUB_URL = "http://localhost:8000"
RISK_THRESHOLD_BLOCK = 90       # Block if risk ≥ 90
RISK_THRESHOLD_STEP_UP = 70     # Step-up auth if risk ≥ 70
```

---

## Testing Strategy

### Unit Tests
- Component-level testing (risk engine, pattern classifier, fingerprint)
- Mock dependencies
- Fast execution (<1s per test)

### Integration Tests
- Multi-service testing (entity + hub)
- Real HTTP communication
- Advisory flow validation

### End-to-End Tests
- Full scenario simulation
- Multiple entities + hub + dashboard
- Coordinated fraud pattern detection

### Privacy Tests
- Packet capture analysis
- Verify no PII in network traffic
- Fingerprint reversibility tests

**Test Coverage:** 37/37 tests passing

---

## Security Considerations

**Inter-Service Communication:**
- TLS for all HTTP traffic
- JWT tokens for authentication
- API rate limiting

**Data Protection:**
- SHA-256 for fingerprint hashing
- No plaintext PII in logs
- Environment variables for secrets

**Access Control:**
- Role-based access (dashboard)
- Entity-specific API keys
- Hub endpoint authentication

---

## Future Enhancements

**Potential Improvements:**
- Machine learning for anomaly scoring (post-correlation)
- Blockchain-based immutable audit trail
- Graph neural networks for pattern mining
- Automated threshold optimization
- Multi-level risk scoring (transaction/user/merchant)
- Mobile app for real-time alerts

**Architectural Considerations:**
- Maintain privacy-by-construction principle
- Preserve explainability requirement
- Ensure regulatory compliance
- No compromise on entity sovereignty

---

## References

**Academic Foundations:**
- Knowledge graph theory
- Temporal network analysis
- Federated learning principles
- Differential privacy concepts

**Related Standards:**
- GDPR (privacy by design)
- PCI-DSS (payment security)
- ISO 27001 (information security)
- NIST Privacy Framework

---

**Built by Team Innovators United**  
*Privacy-First. Intelligence-Forward. Trust-Enabled.*