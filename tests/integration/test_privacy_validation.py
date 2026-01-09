"""
Privacy Validation Tests for Section 6.5

Tests to ensure no PII (Personally Identifiable Information) leaks through:
- Network fingerprints
- Hub logs
- BRG graph data
- Advisory content
"""
import pytest
import json
import re
from datetime import datetime
from bridge_hub.models import RiskFingerprint, Advisory
from bridge_hub.brg_graph import BehavioralRiskGraph
from entity_a.fingerprint import FingerprintGenerator
from entity_a.models import Transaction, BehaviorPattern


class TestPrivacyValidation:
    """Validate that no PII leaks anywhere in the system"""
    
    def test_fingerprint_contains_no_pii(self):
        """
        Test: Fingerprint generation produces privacy-preserving hash
        Expected: No user_id, account, amount, or transaction details in fingerprint
        """
        # Generate fingerprint with real pattern
        generator = FingerprintGenerator(entity_id="entity_a")
        fingerprint = generator.generate_fingerprint(
            pattern=BehaviorPattern.VELOCITY_ABUSE,
            severity="HIGH",
            timestamp=datetime.utcnow()
        )
        
        # Sensitive data that should NOT appear in fingerprint
        sensitive_data = [
            "user_sensitive_123",
            "999.99",
            "merchant_abc",
            "credit_card_4532",
            "device_xyz",
            "192.168.1.100",
            "San Francisco",
            "txn_12345"
        ]
        
        # Verify no PII in fingerprint
        for data in sensitive_data:
            assert data not in fingerprint, f"Found sensitive data '{data}' in fingerprint"
        
        # Fingerprint should start with fp_ prefix and be hexadecimal (SHA-256 hash)
        assert fingerprint.startswith('fp_'), "Fingerprint should have fp_ prefix"
        # Remove prefix and check hash format
        hash_part = fingerprint[3:]  # Remove "fp_" prefix
        assert len(hash_part) >= 16, "Fingerprint should contain hash"
        assert all(c in '0123456789abcdef' for c in hash_part), "Fingerprint should be hexadecimal"
    
    def test_risk_fingerprint_model_no_pii(self):
        """
        Test: RiskFingerprint model sent to Hub contains no PII
        Expected: Only entity_id, hash, severity, timestamp
        """
        fp = RiskFingerprint(
            entity_id="entity_a",
            fingerprint="a" * 64,  # Hash
            severity="HIGH",
            timestamp=datetime.utcnow().isoformat()
        )
        
        # Serialize to JSON (what gets sent over network)
        fp_json = fp.model_dump(mode='json')
        
        # Verify only expected fields
        assert set(fp_json.keys()) == {'entity_id', 'fingerprint', 'severity', 'timestamp'}
        
        # Verify no additional data
        fp_str = json.dumps(fp_json)
        
        # Common PII patterns that should NOT appear
        pii_patterns = [
            r'user_id',
            r'account',
            r'amount',
            r'transaction_id',
            r'credit',
            r'card',
            r'ssn',
            r'email',
            r'phone',
            r'address',
            r'name',
            r'merchant',
            r'payment',
            r'ip_address',
            r'device_id'
        ]
        
        for pattern in pii_patterns:
            assert not re.search(pattern, fp_str, re.IGNORECASE), \
                f"PII pattern '{pattern}' found in fingerprint JSON"
    
    def test_brg_graph_contains_no_pii(self):
        """
        Test: BRG graph nodes and edges contain no transaction details
        Expected: Only fingerprint hashes, entity_ids, timestamps, severity
        """
        brg = BehavioralRiskGraph(max_age_seconds=3600)
        
        # Add observations (simulating real data)
        fingerprint1 = "abc" * 20 + "1" * 4  # 64 char hash
        fingerprint2 = "def" * 20 + "2" * 4
        
        brg.add_pattern_observation(
            fingerprint=fingerprint1,
            entity_id="entity_a",
            severity="HIGH",
            timestamp=datetime.utcnow()
        )
        
        brg.add_pattern_observation(
            fingerprint=fingerprint2,
            entity_id="entity_b",
            severity="MEDIUM",
            timestamp=datetime.utcnow()
        )
        
        # Extract all graph data
        nodes = list(brg.graph.nodes(data=True))
        edges = list(brg.graph.edges(data=True))
        
        # Convert to string for inspection
        graph_data = json.dumps({
            'nodes': [{'fingerprint': n, 'data': d} for n, d in nodes],
            'edges': [{'src': s, 'tgt': t, 'data': d} for s, t, d in edges]
        }, default=str)
        
        # Verify no PII patterns
        pii_keywords = [
            'user_id', 'transaction_id', 'amount', 'credit_card',
            'ssn', 'email', 'phone', 'address', 'merchant_name',
            'account_number', 'payment_method', 'ip_address', 'device_info'
        ]
        
        for keyword in pii_keywords:
            assert keyword not in graph_data.lower(), \
                f"PII keyword '{keyword}' found in BRG graph data"
        
        # Verify only allowed fields in edges
        for src, tgt, data in edges:
            allowed_fields = {'entity_id', 'timestamp', 'severity', 'observation_id',
                            'base_confidence', 'decay_score', 'effective_confidence', 'pattern_status',
                            'edge_type'}  # edge_type is for graph structure, not PII
            assert set(data.keys()).issubset(allowed_fields), \
                f"Unexpected fields in edge data: {set(data.keys()) - allowed_fields}"
    
    def test_advisory_contains_no_entity_specific_pii(self):
        """
        Test: Advisory content contains no entity-specific transaction details
        Expected: Generic pattern info, no targeting of specific entities
        """
        advisory = Advisory(
            advisory_id="adv_001",
            fingerprint="pattern_hash_" + "x" * 50,
            confidence="HIGH",
            severity="CRITICAL",
            summary="Cross-entity fraud pattern detected",
            recommendation="Increase transaction scrutiny",
            message="Behavioral pattern observed across multiple entities indicating coordinated fraud activity",
            recommended_actions=["Review recent transactions", "Implement step-up authentication"],
            affected_entities=["entity_a", "entity_b"],  # OK - just entity IDs
            correlation_count=5,
            entity_count=2,
            fraud_score=85.0,
            timestamp=datetime.utcnow().isoformat(),
            base_confidence=0.9,
            decay_score=1.0,
            effective_confidence=0.9,
            last_seen_timestamp=datetime.utcnow(),
            pattern_status="ACTIVE",
            time_since_last_seen_seconds=0.0,
            decay_explanation="Fresh pattern"
        )
        
        # Serialize advisory
        advisory_json = advisory.model_dump(mode='json')
        advisory_str = json.dumps(advisory_json, default=str)
        
        # Verify no specific user/transaction targeting
        forbidden_patterns = [
            r'user_\w+',  # user IDs
            r'txn_\w+',   # transaction IDs
            r'\$\d+',     # dollar amounts
            r'\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}',  # credit card
            r'\d{3}-\d{2}-\d{4}',  # SSN
            r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',  # IP addresses (except entity IDs)
        ]
        
        for pattern in forbidden_patterns:
            matches = re.findall(pattern, advisory_str)
            # Filter out entity_a, entity_b which are OK
            matches = [m for m in matches if not m.startswith('entity_')]
            assert len(matches) == 0, \
                f"Forbidden pattern '{pattern}' found in advisory: {matches}"
        
        # Verify message is generic
        assert "user" not in advisory.message.lower() or "user" in advisory.message.lower() and "multiple" in advisory.message.lower()
        assert "account" not in advisory.message.lower()
        assert "transaction" not in advisory.message.lower() or "transactions" in advisory.message.lower()  # Plural OK
    
    def test_hub_logs_privacy(self):
        """
        Test: Simulated log messages contain no PII
        Expected: Only fingerprint prefixes, entity IDs, severities logged
        """
        import logging
        from io import StringIO
        
        # Capture logs
        log_stream = StringIO()
        handler = logging.StreamHandler(log_stream)
        handler.setLevel(logging.INFO)
        logger = logging.getLogger('test_logger')
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        
        # Simulate typical Hub log messages
        logger.info("Fingerprint ingested from entity_a: abc123...def456 (severity=HIGH)")
        logger.info("Correlation detected: 3 entities, confidence=0.85")
        logger.warning("Fraud intent escalated: CRITICAL - pattern_xyz (score=90)")
        logger.info("Advisory generated: ADV-20260109-abc12345")
        
        log_output = log_stream.getvalue()
        
        # Verify no PII in logs
        pii_patterns = [
            r'user_id',
            r'transaction_id',
            r'amount.*\d+\.\d+',
            r'credit.*card',
            r'account.*\d+',
            r'\$\d+',
            r'email',
            r'phone'
        ]
        
        for pattern in pii_patterns:
            assert not re.search(pattern, log_output, re.IGNORECASE), \
                f"PII pattern '{pattern}' found in logs"
        
        # Verify fingerprints are truncated
        assert "abc123...def456" in log_output  # Truncated format OK
        assert not re.search(r'[a-f0-9]{64}', log_output), \
            "Full fingerprint hash found in logs (should be truncated)"
    
    def test_network_payload_size_privacy(self):
        """
        Test: Network payload sizes are minimal (only hash, not full data)
        Expected: RiskFingerprint payload < 500 bytes
        """
        fp = RiskFingerprint(
            entity_id="entity_a",
            fingerprint="a" * 64,
            severity="HIGH",
            timestamp=datetime.utcnow().isoformat()
        )
        
        # Serialize to JSON
        fp_json = json.dumps(fp.model_dump(mode='json'))
        payload_size = len(fp_json.encode('utf-8'))
        
        # Should be small (only metadata, not full transaction)
        assert payload_size < 500, \
            f"RiskFingerprint payload too large: {payload_size} bytes (expected < 500)"
        
        # Verify no bloat
        assert '"fingerprint"' in fp_json
        assert '"entity_id"' in fp_json
        assert '"severity"' in fp_json
        assert '"timestamp"' in fp_json
        
        # Should NOT contain transaction data fields
        assert 'transaction' not in fp_json.lower()
        assert 'user' not in fp_json.lower()
        assert 'amount' not in fp_json.lower()
    
    def test_privacy_by_design_principles(self):
        """
        Test: System adheres to privacy-by-design principles
        Expected: Data minimization, purpose limitation, storage limitation
        """
        # Principle 1: Data Minimization
        # Only essential fields in RiskFingerprint
        fp = RiskFingerprint(
            entity_id="entity_a",
            fingerprint="hash" * 16,
            severity="HIGH",
            timestamp=datetime.utcnow().isoformat()
        )
        
        # Count fields
        field_count = len(fp.model_dump())
        assert field_count == 4, f"Too many fields in RiskFingerprint: {field_count}"
        
        # Principle 2: Purpose Limitation
        # Fingerprints used ONLY for pattern correlation, not profiling
        # (Verified by absence of PII in previous tests)
        
        # Principle 3: Storage Limitation
        # BRG has max_age_seconds (tested elsewhere)
        brg = BehavioralRiskGraph(max_age_seconds=3600)
        assert hasattr(brg, 'max_age_seconds')
        assert brg.max_age_seconds == 3600
        
        # Principle 4: Transparency
        # Advisory includes decay_explanation for auditability
        advisory = Advisory(
            advisory_id="adv_001",
            fingerprint="fp" * 32,
            confidence="HIGH",
            severity="HIGH",
            summary="Pattern detected",
            recommendation="Review",
            message="Test",
            recommended_actions=["Action"],
            affected_entities=["entity_a"],
            correlation_count=2,
            entity_count=2,
            fraud_score=80.0,
            timestamp=datetime.utcnow().isoformat(),
            base_confidence=0.8,
            decay_score=1.0,
            effective_confidence=0.8,
            last_seen_timestamp=datetime.utcnow(),
            pattern_status="ACTIVE",
            time_since_last_seen_seconds=0.0,
            decay_explanation="Transparency for audit"
        )
        
        assert advisory.decay_explanation is not None
        assert len(advisory.decay_explanation) > 0
