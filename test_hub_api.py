"""
Quick test script for BRIDGE Hub API
"""
import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"
API_KEY = "dev-key-change-in-production"

def test_health():
    """Test health endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    print(f"Health: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    return response.status_code == 200

def test_stats():
    """Test stats endpoint"""
    response = requests.get(
        f"{BASE_URL}/stats",
        headers={"x-api-key": API_KEY}
    )
    print(f"\nStats: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    return response.status_code == 200

def test_submit_fingerprint():
    """Test fingerprint submission with multiple entities"""
    # Submit from multiple entities to trigger correlation
    entities = ["bank_A", "bank_B", "bank_C"]
    pattern = "coordinated_fraud_pattern_12345"
    
    for entity in entities:
        fingerprint = {
            "fingerprint": pattern,
            "entity_id": entity,
            "severity": "HIGH",
            "timestamp": datetime.now().isoformat()
        }
        
        response = requests.post(
            f"{BASE_URL}/ingest",
            json=fingerprint,
            headers={
                "X-Entity-ID": entity,
                "x-api-key": API_KEY
            }
        )
        
        if entity == entities[-1]:  # Show last response
            print(f"\nSubmit (multiple entities): {response.status_code}")
            print(json.dumps(response.json(), indent=2))
    
    return response.status_code == 202

def test_get_advisories():
    """Test advisory retrieval"""
    # Wait a moment for advisory processing
    time.sleep(0.5)
    
    response = requests.get(
        f"{BASE_URL}/advisories",
        headers={"x-api-key": API_KEY},
        params={"limit": 5}
    )
    print(f"\nAdvisories (all): {response.status_code}")
    advisories = response.json()
    print(f"Found {len(advisories)} advisories")
    if advisories:
        print(json.dumps(advisories[0], indent=2))
    
    return response.status_code == 200

if __name__ == "__main__":
    print("=" * 60)
    print("BRIDGE Hub API Test")
    print("=" * 60)
    
    try:
        results = []
        results.append(("Health", test_health()))
        results.append(("Stats", test_stats()))
        results.append(("Submit", test_submit_fingerprint()))
        results.append(("Advisories", test_get_advisories()))
        
        print("\n" + "=" * 60)
        print("Test Results:")
        for name, passed in results:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{status} - {name}")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to Hub API")
        print("Make sure the Hub is running: python -m bridge_hub.main")
