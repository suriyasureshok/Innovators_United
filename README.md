# SYNAPSE-FI  
**Privacy-Preserving Collective Fraud Intelligence Platform**

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![Tests](https://img.shields.io/badge/tests-37%2F37%20passing-brightgreen.svg)]()
[![React](https://img.shields.io/badge/React-18-blue.svg)](https://react.dev)

> **Detect coordinated fraud across financial institutions without sharing sensitive data**

Powered by **BRIDGE** (Behavioral Risk Intent Decision Graph Engine)

---

## 🎯 Problem

Fraudsters orchestrate attacks across multiple banks simultaneously, staying below detection thresholds at each institution:

**Example:** Fraudster hits 3 banks with $4,500, $3,800, and $4,200—each below individual alert thresholds. Total stolen: **$12,500**. Each bank sees "normal" activity.

**Why Traditional Solutions Fail:**
- Centralized data warehouses violate privacy laws
- Manual intelligence sharing is too slow  
- Siloed detection misses coordinated patterns
- Regulations prohibit raw transaction sharing

## 💡 Solution

**SYNAPSE-FI** enables fraud detection by sharing **behavioral abstractions** instead of raw data:

- ❌ **Don't Share:** Customer IDs, amounts, account numbers, transactions
- ✅ **Share:** Abstract patterns like `"high-velocity + new-device + geo-shift"`

**BRIDGE Hub** correlates these patterns across entities in real-time—**collective intelligence without data sharing**.

---

## 🏗️ Architecture

```
┌──────────────┐      Fingerprints      ┌──────────────┐
│   Entity A   │ ────────────────────▶ │              │
│  (Bank 1)    │                        │              │
└──────────────┘                        │              │
                                        │   BRIDGE     │
┌──────────────┐      Fingerprints      │     Hub      │
│   Entity B   │ ────────────────────▶ │              │
│  (Bank 2)    │                        │              │
└──────────────┘                        │              │
                                        └──────┬───────┘
                                               │
                                     Advisory Alerts
                                               │
                     ┌─────────────────────────┴─────────────────────────┐
                     │                                                     │
             ┌──────────────┐                                      ┌──────────────┐
             │   Entity A   │                                      │   Entity B   │
             │  (Bank 1)    │                                      │  (Bank 2)    │
             └──────────────┘                                      └──────────────┘
```

### Components

**1. Entity Services** (`entity_a/`, `entity_b/`)  
Local fraud detection → Generate behavioral fingerprints → Submit to Hub

**2. BRIDGE Hub** (`bridge_hub/`)
- **Temporal Correlator**: Cross-entity pattern detection
- **Escalation Engine**: Auto-escalate MEDIUM → HIGH → CRITICAL
- **Decay Engine**: Time-based confidence degradation  
- **BRG Graph**: Behavioral Risk Graph visualization
- **Advisory Builder**: Generate actionable alerts

**3. Dashboard** (`dashboard/bridge-insights/`)  
React + TypeScript real-time monitoring, pattern analysis, BRG visualization

---

## 🧠 BRIDGE Hub - The Core Intelligence Engine

**BRIDGE** (Behavioral Risk Intent Decision Graph Engine) is the heart of SYNAPSE-FI, enabling privacy-preserving collective fraud intelligence.

### How BRIDGE Works

**1. Behavioral Risk Graph (BRG)**
- In-memory graph database storing pattern relationships
- Nodes: Entities and behavioral fingerprints
- Edges: Temporal observations (who saw what, when)
- Zero knowledge of actual transactions

**2. Temporal Correlator**
```python
# Detects patterns appearing across multiple entities
def detect_correlation(fingerprint, time_window=300s):
    observations = graph.get_recent_observations(fingerprint)
    unique_entities = count_unique_entities(observations)
    return unique_entities >= ENTITY_THRESHOLD  # Default: 2
```

**Key Intelligence:**
- Pattern seen once = noise
- Same pattern at 2+ entities within 5 minutes = coordinated attack
- Time transforms individual observations into collective intelligence

**3. Escalation Engine**
```python
# Auto-escalates severity based on entity participation
if entities >= 2 and severity in ["HIGH", "CRITICAL"]:
    escalate_to_advisory()
    confidence = "HIGH"
```

**Escalation Logic:**
- **MEDIUM** → Single entity observation
- **HIGH** → 2 entities within time window
- **CRITICAL** → 3+ entities or repeated pattern

**4. Decay Engine**
```python
# Confidence decreases without reinforcement
confidence *= exp(-time_elapsed / DECAY_CONSTANT)
if confidence < THRESHOLD:
    pattern_status = "DORMANT"
```

**Why Decay Matters:**
- Recent patterns weighted higher
- Stale patterns fade naturally
- Prevents false positives from old data
- Adapts to evolving fraud tactics

**5. Advisory Builder**
```json
{
  "advisory_id": "adv_001",
  "fingerprint": "fp_a3d7e9f2",
  "confidence": "HIGH",
  "entities_affected": 2,
  "first_seen": "2026-01-10T10:30:00Z",
  "last_seen": "2026-01-10T10:33:00Z",
  "recommendation": "ESCALATE_RISK",
  "rationale": "Pattern seen across 2 entities in 300s window"
}
```

**Advisory Components:**
- **Confidence Score**: Based on entity count & recency
- **Rationale**: Human-readable explanation
- **Recommendation**: Actionable guidance (not commands)
- **No PII**: Only abstract pattern references

### BRIDGE Intelligence Flow

```
┌─────────────────────────────────────────────────────────────┐
│ Step 1: Fingerprint Arrives                                 │
│ Entity A sends: {fp_a3d7e9f2, HIGH, timestamp}             │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 2: Graph Update                                        │
│ BRG adds: Entity_A --OBSERVED--> fp_a3d7e9f2              │
│ Timestamp: 10:30:00                                        │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 3: Temporal Correlation Check                          │
│ Query: "Who else saw fp_a3d7e9f2 in last 5 minutes?"      │
│ Result: Entity B (10:28:00) - 2 entities detected!        │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 4: Escalation Decision                                 │
│ IF entities ≥ 2 AND severity = HIGH                        │
│ THEN: Generate advisory with HIGH confidence               │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 5: Advisory Distribution                               │
│ Broadcast to ALL entities:                                  │
│ "Pattern fp_a3d7e9f2 is coordinated attack"               │
│ Entities adjust local risk scores accordingly              │
└─────────────────────────────────────────────────────────────┘
```

### Why BRIDGE is Revolutionary

**Traditional Approach:**
```
Bank A: $4,500 suspicious → Below $5K threshold → ALLOW ❌
Bank B: $3,800 suspicious → Below threshold → ALLOW ❌
Bank C: $4,200 suspicious → Below threshold → ALLOW ❌
Total Loss: $12,500
```

**With BRIDGE:**
```
Bank A: $4,500 suspicious → fp_a3d7e9f2 → Send to BRIDGE
Bank B: $3,800 suspicious → fp_a3d7e9f2 → Send to BRIDGE
        ↓
BRIDGE: "2 entities, same pattern, 3 min apart" → ADVISORY
        ↓
Bank A: Risk 87 → 95 (advisory boost) → BLOCK ✅
Bank B: Risk 72 → 89 (advisory boost) → STEP-UP AUTH ✅
Bank C: Receives preventative advisory → MONITOR ✅
Total Loss Prevented: $12,500
```

### Privacy Guarantee

BRIDGE never knows:
- ❌ Customer names or IDs
- ❌ Transaction amounts
- ❌ Account numbers
- ❌ Merchant details
- ❌ Any reversible data

BRIDGE only knows:
- ✅ Entity A observed pattern X at time T
- ✅ Entity B observed pattern X at time T+180s
- ✅ Correlation exists → Issue advisory

**Even if BRIDGE is compromised, zero transaction data exists to steal.**

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+ & npm

### Installation

```bash
# Clone & setup Python
git clone <repo-url>
cd Synapse_FI
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Setup frontend
cd dashboard/bridge-insights
npm install
cd ../..
```

### Run

```bash
# Terminal 1: BRIDGE Hub
python -m bridge_hub.main

# Terminal 2: Simulation  
python run_simulation.py --duration 60

# Terminal 3: Dashboard
cd dashboard/bridge-insights
npm run dev
```

### Access Dashboard

**URL:** http://localhost:8081/  
**Login:** `admin@bridge.hub` / `demo123`

---

## ✨ Key Features

### Real-Time Detection
- Sub-10ms fingerprint ingestion  
- 300s correlation time windows
- Auto-escalation: MEDIUM → HIGH → CRITICAL
- Live advisory generation

### Privacy Guarantees
✅ One-way behavioral fingerprints (irreversible)  
✅ Zero PII transmission  
✅ Schema-blind Hub (no transaction knowledge)  
✅ Entity sovereignty (local decision authority)

### Pattern Analysis
- **Active**: Currently detected across entities
- **Cooling**: Decreasing frequency (time decay)
- **Dormant**: No recent activity
- **BRG Graph**: Entity-pattern relationships

### Advisory System
Confidence scoring • Multi-entity tracking • Actionable recommendations • Severity prioritization

---

## 🧪 Testing

```bash
pytest tests/ -v              # All 37 tests
pytest tests/test_temporal_correlator.py
pytest tests/integration/test_e2e_flow.py
```

---

## 📁 Project Structure

```
Synapse_FI/
├── bridge_hub/              # BRIDGE Hub - Core Intelligence Engine
│   ├── main.py             # FastAPI server
│   ├── brg_graph.py        # Behavioral Risk Graph (in-memory)
│   ├── temporal_correlator.py  # Cross-entity pattern detection
│   ├── escalation_engine.py    # Severity escalation logic
│   ├── decay_engine.py         # Time-based confidence decay
│   ├── advisory_builder.py     # Advisory message construction
│   ├── hub_state.py        # Hub state management
│   ├── metrics.py          # Performance metrics
│   ├── models.py           # Data models
│   ├── config.py           # Configuration
│   └── tests/              # Hub unit tests
│
├── entity_a/               # Entity Service A (Bank 1)
│   ├── main.py            # FastAPI server
│   ├── stream.py          # Transaction generator
│   ├── risk_engine.py     # Local risk scoring
│   ├── pattern_classifier.py  # Pattern detection
│   ├── fingerprint.py     # Fingerprint generation
│   ├── decision.py        # Decision engine
│   ├── hub_client.py      # BRIDGE communication
│   ├── models.py          # Data models
│   └── tests/             # Entity tests
│
├── entity_b/               # Entity Service B (Bank 2)
│   └── [same as entity_a] # Independent service
│
├── dashboard/
│   └── bridge-insights/   # React Dashboard
│       ├── src/
│       │   ├── pages/     # Landing, Login, Overview, Patterns, etc.
│       │   ├── components/  # UI components
│       │   ├── hooks/     # useHubAPI (mock data)
│       │   └── data/      # mockDataGenerator.ts
│       ├── package.json
│       └── vite.config.ts
│
├── shared/                 # Shared utilities
│   ├── models.py          # Common interfaces
│   └── utils.py           # Helper functions
│
├── tests/                  # Integration tests
│   ├── integration/       # Multi-service tests
│   └── fixtures/          # Test data
│
├── scripts/                # Utility scripts
│   └── setup.py
│
├── docker-compose.yml      # Multi-container setup
├── requirements.txt        # Python dependencies
├── run_simulation.py       # Fraud simulation orchestrator
└── README.md              # This file
```

---

## ⚙️ Configuration

**Hub** (`bridge_hub/config.py`)
- `ENTITY_THRESHOLD`: Min entities for correlation (default: 2)
- `TIME_WINDOW_SECONDS`: Correlation window (default: 300s)
- `DECAY_ENABLED`: Time-based confidence decay (default: True)

**Entities**
- `FRAUD_RATIO`: Suspicious transaction % (default: 30%)
- `TRANSACTION_INTERVAL`: Generation rate (1.5-2.0s)

---

## 📈 Performance

- **Ingestion Latency:** <10ms (p95)
- **Correlation Latency:** <50ms (p95)  
- **Advisory Generation:** <100ms (p95)
- **Throughput:** 150+ txn/sec per entity
- **Graph Operations:** Bounded to 5K nodes

---

## 📚 Key Concepts

| Concept | Description |
|---------|-------------|
| **Behavioral Fingerprint** | Abstract pattern (e.g., `fp_velocity_spike_geo_shift`) |
| **Temporal Correlation** | Pattern significance across N entities in time window |
| **Decay Engine** | Confidence decreases without reinforcement |
| **Escalation** | Auto-escalate MEDIUM → HIGH → CRITICAL |
| **Advisory** | Actionable alert with confidence + recommendations |

---

## 📖 Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System design & implementation details  
- **[dashboard/bridge-insights/README.md](dashboard/README.md)** - Frontend docs

---

## 🏁 The Innovation

> **SYNAPSE-FI enables institutions to collectively remember fraud strategies without ever remembering the fraudster.**

At the core is **BRIDGE (Behavioral Risk Intent Discovery Engine)** — a novel algorithm that detects **coordinated fraud intent** by correlating **repeated behavioral patterns across institutions**, without sharing data or identities.

BRIDGE models fraud as **behavioral intent, not identity**, and shares only **abstract behavior fingerprints**, not transactions.

To ensure governance and proportional response, BRIDGE includes a **Pattern Decay Engine**:

* Patterns **lose influence over time** if they stop repeating
* Intelligence is **never deleted**, only trusted less
* Influence is instantly restored when behavior reappears

Together, **BRIDGE + Decay** deliver:

* Privacy-preserving collective intelligence
* Explainable, regulator-safe decisions
* Trust without loss of institutional sovereignty

**Beyond fraud:** The same paradigm applies to healthcare, cybersecurity, and supply chains—any domain requiring collaboration under strict privacy constraints.

---

**Built by Team VIT-Vortex**  
*Privacy-First. Intelligence-Forward. Trust-Enabled.*