# SYNAPSE-FI  
**Privacy-Preserving Collective Fraud Intelligence Platform**

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![Tests](https://img.shields.io/badge/tests-37%2F37%20passing-brightgreen.svg)]()
[![React](https://img.shields.io/badge/React-18-blue.svg)](https://react.dev)

> **Detect coordinated fraud across financial institutions without sharing sensitive data**

Powered by **BRIDGE** (Behavioral Risk Intent Discovery & Governance Engine)

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
┌──────────────┐                   ┌──────────────┐
│   Entity A   │──Fingerprints──┐  │   Entity B   │
│  (Bank 1)    │                │  │  (Bank 2)    │
└──────────────┘                ▼  └──────────────┘
                         ┌──────────┐
                         │  BRIDGE  │ ← Zero PII
                         │   Hub    │ ← Zero Transactions  
                         └──────────┘ ← Only Abstractions
                               │
                         Advisory Alerts
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

**Option 1: PowerShell Script**
```powershell
.\start-full-system.ps1
```

**Option 2: Manual**
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
✅ **37/37 passing**

---

## 📁 Project Structure

```
Synapse_FI/
├── bridge_hub/              # BRIDGE Hub (FastAPI)
│   ├── temporal_correlator.py
│   ├── escalation_engine.py
│   ├── decay_engine.py
│   ├── advisory_builder.py
│   └── brg_graph.py
├── entity_a/                # Simulated Bank A
├── entity_b/                # Simulated Bank B  
├── dashboard/
│   └── bridge-insights/     # React Dashboard
├── tests/                   # Test suite
└── run_simulation.py        # Fraud simulator
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
- **[dashboard/bridge-insights/README.md](dashboard/bridge-insights/README.md)** - Frontend docs

---

## 🏁 The Innovation

> **SYNAPSE-FI enables institutions to collectively remember fraud strategies without ever remembering the fraudster.**

By modeling fraud as **behavioral intent** (not identity) and sharing **abstractions** (not data):
- ✅ Effective fraud detection without privacy sacrifice
- ✅ Regulatory compliance + collective intelligence
- ✅ Trust without compromising sovereignty

**Beyond Fraud:** Extends to healthcare, cybersecurity, supply chain—any domain requiring collaborative intelligence with privacy constraints.

---

## 🤝 Contributing

1. Fork repo  
2. Create branch (`git checkout -b feature/name`)  
3. Commit (`git commit -m 'Add feature'`)  
4. Push (`git push origin feature/name`)  
5. Open Pull Request

---

## 📄 License

MIT License - See [LICENSE](LICENSE)

---

**Built with ❤️ by Team VIT-Vortex**  
*Privacy-First. Intelligence-Forward. Trust-Enabled.*