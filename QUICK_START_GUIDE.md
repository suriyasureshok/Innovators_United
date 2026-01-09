# BRIDGE Hub - Quick Start Guide

## 🚀 How to Use the Hub

### Start the Hub
```bash
cd C:\Users\SURIYA\Desktop\Competition\VIT-Vortex\Synapse_FI
python -m bridge_hub.main
```

The Hub will start on `http://localhost:8000`

---

## 📡 API Endpoints

### Authentication
All endpoints (except `/health`) require:
```
Header: x-api-key: dev-key-change-in-production
```

### 1. Health Check (Public)
```bash
GET http://localhost:8000/health
```

**Response:**
```json
{
  "status": "HEALTHY",
  "timestamp": "2026-01-09T07:05:50.736263",
  "message": "All systems operational"
}
```

---

### 2. Get Statistics
```bash
GET http://localhost:8000/stats
Headers:
  x-api-key: dev-key-change-in-production
```

**Response:**
```json
{
  "unique_patterns": 15,
  "total_observations": 45,
  "active_entities": 8,
  "memory_size_bytes": 225000,
  "temporal_coverage_seconds": 1200
}
```

---

### 3. Submit Fingerprint
```bash
POST http://localhost:8000/ingest
Headers:
  x-api-key: dev-key-change-in-production
  X-Entity-ID: bank_A
Body:
{
  "fingerprint": "fraud_pattern_12345",
  "entity_id": "bank_A",
  "severity": "HIGH",
  "timestamp": "2026-01-09T12:00:00Z"
}
```

**Response (No Correlation):**
```json
{
  "status": "accepted",
  "fingerprint": "fraud_pattern_12...",
  "entity_id": "bank_A",
  "correlation_detected": false,
  "message": "Fingerprint ingested successfully"
}
```

**Response (Correlation Detected):**
```json
{
  "status": "accepted",
  "fingerprint": "fraud_pattern_12...",
  "entity_id": "bank_A",
  "correlation_detected": true,
  "message": "Fingerprint ingested successfully"
}
```

---

### 4. Get Advisories
```bash
GET http://localhost:8000/advisories?limit=5&severity=CRITICAL
Headers:
  x-api-key: dev-key-change-in-production
```

**Response:**
```json
[
  {
    "advisory_id": "ADV-20260109-070558-coordina",
    "fingerprint": "fraud_pattern_12345",
    "severity": "CRITICAL",
    "message": "SYNAPSE-FI Fraud Advisory\n\nSeverity: CRITICAL\n...",
    "recommended_actions": [
      "IMMEDIATE: Flag all matching transactions for manual review",
      "IMMEDIATE: Implement temporary transaction limits",
      "URGENT: Notify fraud investigation team",
      "URGENT: Check for additional correlated patterns",
      "RECOMMENDED: Share findings with peer institutions"
    ],
    "entity_count": 3,
    "confidence": "HIGH",
    "fraud_score": 70,
    "timestamp": "2026-01-09T07:05:58.891912"
  }
]
```

---

## 🧪 Testing the Hub

### Run Unit Tests
```bash
# All tests
pytest tests/ -v

# Specific component
pytest tests/test_brg_graph.py -v
pytest tests/test_temporal_correlator.py -v
pytest tests/test_escalation_engine.py -v
pytest tests/test_advisory_builder.py -v

# With coverage
pytest tests/ --cov=bridge_hub --cov-report=html
```

### Run API Integration Test
```bash
python test_hub_api.py
```

Expected output:
```
============================================================
BRIDGE Hub API Test
============================================================
Health: 200
Stats: 200
Submit (multiple entities): 202
Advisories (all): 200
Found 2 advisories

============================================================
Test Results:
✅ PASS - Health
✅ PASS - Stats
✅ PASS - Submit
✅ PASS - Advisories
============================================================
```

---

## ⚙️ Configuration

### Environment Variables

```bash
# Server Settings
HUB_HOST=0.0.0.0
HUB_PORT=8000

# Correlation Settings
ENTITY_THRESHOLD=2           # Min entities for correlation
TIME_WINDOW_SECONDS=300      # 5-minute correlation window

# Escalation Thresholds
CRITICAL_THRESHOLD=4         # 4+ entities = CRITICAL
HIGH_THRESHOLD=3             # 3 entities = HIGH
MEDIUM_THRESHOLD=2           # 2 entities = MEDIUM

# Graph Maintenance
MAX_GRAPH_AGE_SECONDS=3600   # 1-hour data retention
PRUNE_INTERVAL_SECONDS=300   # Prune every 5 minutes

# Advisory Settings
MAX_ADVISORIES=1000

# Security
HUB_API_KEY=dev-key-change-in-production

# Logging
LOG_LEVEL=INFO
```

### Example: Run with Custom Config
```bash
# Windows PowerShell
$env:ENTITY_THRESHOLD=3
$env:TIME_WINDOW_SECONDS=600
$env:HUB_PORT=9000
python -m bridge_hub.main

# Linux/Mac
export ENTITY_THRESHOLD=3
export TIME_WINDOW_SECONDS=600
export HUB_PORT=9000
python -m bridge_hub.main
```

---

## 🔍 Monitoring

### Check Hub Logs
The Hub logs to stdout with structured messages:

```
2026-01-09 12:29:30,683 - bridge_hub.main - INFO - ✅ BRIDGE Hub initialized successfully
2026-01-09 12:29:30,683 - bridge_hub.main - INFO -    Entity threshold: 2
2026-01-09 12:29:30,683 - bridge_hub.main - INFO -    Time window: 300s
```

### Health Monitoring
```bash
# Simple uptime check
curl http://localhost:8000/health

# Detailed statistics
curl -H "x-api-key: dev-key-change-in-production" \
     http://localhost:8000/stats
```

### Graph Inspection (Admin)
```bash
# View graph nodes
curl -H "x-api-key: dev-key-change-in-production" \
     http://localhost:8000/admin/graph/nodes

# View graph edges
curl -H "x-api-key: dev-key-change-in-production" \
     http://localhost:8000/admin/graph/edges
```

---

## 📚 API Documentation

### Interactive Swagger UI
Open in browser: http://localhost:8000/docs

### ReDoc Documentation
Open in browser: http://localhost:8000/redoc

### OpenAPI Schema
Download: http://localhost:8000/openapi.json

---

## 🐛 Troubleshooting

### Hub won't start
```bash
# Check if port is already in use
netstat -ano | findstr :8000

# Try different port
$env:HUB_PORT=8001
python -m bridge_hub.main
```

### Import errors
```bash
# Ensure you're in the correct directory
cd C:\Users\SURIYA\Desktop\Competition\VIT-Vortex\Synapse_FI

# Run as module (not direct python file)
python -m bridge_hub.main  # ✅ Correct
python bridge_hub/main.py  # ❌ Wrong (import errors)
```

### 401 Unauthorized
```bash
# Make sure you're sending the API key
curl -H "x-api-key: dev-key-change-in-production" \
     http://localhost:8000/stats
```

### No correlations detected
```bash
# Check your entity threshold
# Default is 2 entities - you need at least 2 different entities
# submitting the SAME fingerprint within the time window

# Example: Submit same pattern from multiple entities
curl -X POST http://localhost:8000/ingest \
  -H "x-api-key: dev-key-change-in-production" \
  -H "X-Entity-ID: bank_A" \
  -d '{"fingerprint":"test","entity_id":"bank_A","severity":"HIGH"}'

curl -X POST http://localhost:8000/ingest \
  -H "x-api-key: dev-key-change-in-production" \
  -H "X-Entity-ID: bank_B" \
  -d '{"fingerprint":"test","entity_id":"bank_B","severity":"HIGH"}'

# Now check advisories
curl -H "x-api-key: dev-key-change-in-production" \
     http://localhost:8000/advisories
```

---

## 📊 Example Workflow

### Scenario: Detect Coordinated Fraud

```python
import requests
from datetime import datetime

BASE_URL = "http://localhost:8000"
API_KEY = "dev-key-change-in-production"
HEADERS = {"x-api-key": API_KEY}

# Step 1: Bank A detects suspicious pattern
requests.post(
    f"{BASE_URL}/ingest",
    headers={**HEADERS, "X-Entity-ID": "bank_A"},
    json={
        "fingerprint": "rapid_login_pattern_xyz",
        "entity_id": "bank_A",
        "severity": "HIGH",
        "timestamp": datetime.now().isoformat()
    }
)

# Step 2: Bank B detects SAME pattern (correlation!)
requests.post(
    f"{BASE_URL}/ingest",
    headers={**HEADERS, "X-Entity-ID": "bank_B"},
    json={
        "fingerprint": "rapid_login_pattern_xyz",
        "entity_id": "bank_B",
        "severity": "HIGH",
        "timestamp": datetime.now().isoformat()
    }
)

# Step 3: Bank C detects SAME pattern (escalation!)
requests.post(
    f"{BASE_URL}/ingest",
    headers={**HEADERS, "X-Entity-ID": "bank_C"},
    json={
        "fingerprint": "rapid_login_pattern_xyz",
        "entity_id": "bank_C",
        "severity": "HIGH",
        "timestamp": datetime.now().isoformat()
    }
)

# Step 4: All banks poll for advisories
response = requests.get(
    f"{BASE_URL}/advisories",
    headers=HEADERS,
    params={"limit": 5, "severity": "CRITICAL"}
)

advisories = response.json()
print(f"Found {len(advisories)} advisories")

for advisory in advisories:
    print(f"\n🚨 {advisory['severity']} Alert")
    print(f"Fraud Score: {advisory['fraud_score']}/100")
    print(f"Affected Entities: {advisory['entity_count']}")
    print(f"Actions to take:")
    for action in advisory['recommended_actions']:
        print(f"  • {action}")
```

---

## 🎯 Next Steps

1. **Implement Entity Services** (Section 3)
   - Create transaction processors
   - Implement feature extraction
   - Generate fingerprints
   - Connect to Hub API

2. **Build Dashboard** (Section 6)
   - Real-time graph visualization
   - Advisory monitoring
   - Entity activity tracking

3. **Integration Testing** (Section 5)
   - End-to-end fraud scenarios
   - Performance testing
   - Privacy validation

---

## 📞 Support

- **Documentation:** See `SECTION4_FINAL_REPORT.md`
- **Architecture:** See `ARCHITECTURE_DIAGRAM.md`
- **Tests:** Run `pytest tests/ -v`
- **Issues:** Check `DETAILED_CHECKLIST.md` for known issues

---

**Status:** ✅ FULLY OPERATIONAL  
**Version:** 1.0.0  
**Last Updated:** 2026-01-09
