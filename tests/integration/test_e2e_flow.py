"""
End-to-End Integration Tests for Section 5: Integration & Communication

Tests complete flow from entity to Hub and back, including:
- Normal operation
- Multi-entity correlation
- Hub unavailable scenarios
- Advisory influence on entity decisions
- Metrics tracking
"""
import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
import httpx

from bridge_hub.models import RiskFingerprint, Advisory
from entity_a.hub_client import BridgeHubClient


class TestEndToEndFlow:
    """Test complete entity-to-hub-to-entity flow"""
    
    @pytest.mark.asyncio
    async def test_single_entity_no_correlation(self):
        """
        Test: Single entity sends fingerprint, no correlation detected
        Expected: Fingerprint accepted, no advisory generated
        """
        # Mock Hub client
        client = BridgeHubClient(
            hub_url="http://localhost:8000",
            api_key="test_key",
            entity_id="entity_test"
        )
        
        # Mock HTTP response for successful ingestion without correlation
        with patch.object(client.client, 'post', new_callable=AsyncMock) as mock_post:
            mock_response = Mock()
            mock_response.status_code = 202
            mock_response.json.return_value = {
                "status": "accepted",
                "correlation_detected": False
            }
            mock_post.return_value = mock_response
            
            # Send fingerprint
            result = await client.send_fingerprint(
                fingerprint="abc123" * 10,
                severity="MEDIUM",
                timestamp=datetime.utcnow().isoformat()
            )
            
            assert result is True
            assert client.fingerprints_sent == 1
            mock_post.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_multi_entity_correlation(self):
        """
        Test: Multiple entities send same pattern, correlation detected
        Expected: Advisory generated for all entities
        """
        # Simulate two entities
        entity_a = BridgeHubClient(
            hub_url="http://localhost:8000",
            api_key="test_key",
            entity_id="entity_a"
        )
        
        entity_b = BridgeHubClient(
            hub_url="http://localhost:8000",
            api_key="test_key",
            entity_id="entity_b"
        )
        
        pattern = "suspicious_pattern_" + "x" * 50
        
        # Mock responses
        with patch.object(entity_a.client, 'post', new_callable=AsyncMock) as mock_a_post, \
             patch.object(entity_b.client, 'post', new_callable=AsyncMock) as mock_b_post:
            
            # First entity - no correlation yet
            mock_a_response = Mock()
            mock_a_response.status_code = 202
            mock_a_response.json.return_value = {
                "status": "accepted",
                "correlation_detected": False
            }
            mock_a_post.return_value = mock_a_response
            
            # Second entity - correlation detected
            mock_b_response = Mock()
            mock_b_response.status_code = 202
            mock_b_response.json.return_value = {
                "status": "accepted",
                "correlation_detected": True
            }
            mock_b_post.return_value = mock_b_response
            
            # Entity A sends pattern
            result_a = await entity_a.send_fingerprint(
                fingerprint=pattern,
                severity="HIGH",
                timestamp=datetime.utcnow().isoformat()
            )
            
            # Entity B sends same pattern
            await asyncio.sleep(0.1)  # Small delay
            result_b = await entity_b.send_fingerprint(
                fingerprint=pattern,
                severity="HIGH",
                timestamp=datetime.utcnow().isoformat()
            )
            
            assert result_a is True
            assert result_b is True
            assert entity_a.fingerprints_sent == 1
            assert entity_b.fingerprints_sent == 1


class TestHubUnavailableScenarios:
    """Test entity behavior when Hub is unavailable"""
    
    @pytest.mark.asyncio
    async def test_hub_unavailable_with_retry(self):
        """
        Test: Hub unavailable, entity retries with exponential backoff
        Expected: Multiple retry attempts, fingerprint queued if all fail
        """
        client = BridgeHubClient(
            hub_url="http://localhost:9999",  # Non-existent Hub
            api_key="test_key",
            entity_id="entity_test",
            max_retries=3,
            retry_backoff=0.1,  # Fast for testing
            max_pending=10
        )
        
        # Mock connection error
        with patch.object(client.client, 'post', side_effect=httpx.ConnectError("Connection refused")):
            result = await client.send_fingerprint(
                fingerprint="test_pattern" * 10,
                severity="HIGH",
                timestamp=datetime.utcnow().isoformat()
            )
            
            # Should fail after retries
            assert result is False
            assert client.failed_sends == 1
            
            # Fingerprint should be queued
            assert len(client.pending_fingerprints) == 1
            assert client.pending_fingerprints[0]['fingerprint'] == "test_pattern" * 10
    
    @pytest.mark.asyncio
    async def test_pending_fingerprint_flush(self):
        """
        Test: Hub comes back online, pending fingerprints are flushed
        Expected: Queued fingerprints sent successfully
        """
        client = BridgeHubClient(
            hub_url="http://localhost:8000",
            api_key="test_key",
            entity_id="entity_test",
            max_pending=10
        )
        
        # Manually queue fingerprints
        for i in range(3):
            fp = RiskFingerprint(
                entity_id="entity_test",
                fingerprint=f"pattern_{i}" * 10,
                severity="MEDIUM",
                timestamp=datetime.utcnow().isoformat()
            )
            client._queue_fingerprint(fp)
        
        assert len(client.pending_fingerprints) == 3
        
        # Mock successful flush
        with patch.object(client.client, 'post', new_callable=AsyncMock) as mock_post:
            mock_response = Mock()
            mock_response.status_code = 202
            mock_post.return_value = mock_response
            
            # Flush pending
            await client._flush_pending_fingerprints()
            
            # All should be sent
            assert len(client.pending_fingerprints) == 0
            assert mock_post.call_count == 3
    
    @pytest.mark.asyncio
    async def test_entity_continues_locally(self):
        """
        Test: Entity continues making decisions even when Hub is down
        Expected: Local risk scoring works, decisions made without advisory
        """
        # Import entity decision engine
        from entity_a.decision import DecisionEngine
        from entity_a.models import RiskScore
        
        engine = DecisionEngine()
        
        # Make decision without advisory (Hub down scenario)
        risk_score = RiskScore(
            score=45.0,
            signals=["HIGH_VELOCITY"],
            features={"velocity_count": 5},
            pattern=None,
            timestamp=datetime.utcnow()
        )
        
        decision = engine.make_decision(
            transaction_id="txn_001",
            risk_score=risk_score,
            advisory=None  # No advisory from Hub
        )
        
        # Decision should still be made based on local risk
        assert decision is not None
        assert decision.action in ["allow", "step_up", "block"]
        assert decision.advisory_applied is False
        assert decision.adjusted_score == risk_score.score  # No adjustment without advisory


class TestAdvisoryInfluence:
    """Test that advisories influence entity decisions"""
    
    def test_advisory_increases_risk(self):
        """
        Test: High confidence advisory increases entity risk score
        Expected: Adjusted score higher than base score, may change action
        """
        from entity_a.decision import DecisionEngine
        from entity_a.models import RiskScore
        
        engine = DecisionEngine()
        
        # Medium risk transaction
        risk_score = RiskScore(
            score=55.0,
            signals=["HIGH_VELOCITY"],
            features={"velocity_count": 7},
            pattern=None,
            timestamp=datetime.utcnow()
        )
        
        # High confidence advisory
        advisory = Advisory(
            advisory_id="adv_001",
            fingerprint="fp_" * 20,
            confidence="HIGH",
            severity="HIGH",
            summary="Multi-entity fraud pattern",
            recommendation="Increase scrutiny",
            message="Pattern detected across entities",
            recommended_actions=["Block", "Investigate"],
            affected_entities=["entity_a", "entity_b"],
            correlation_count=3,
            entity_count=2,
            fraud_score=85.0,
            timestamp=datetime.utcnow().isoformat(),
            # Decay fields
            base_confidence=0.9,
            decay_score=1.0,
            effective_confidence=0.9,  # Fresh, high confidence
            last_seen_timestamp=datetime.utcnow(),
            pattern_status="ACTIVE",
            time_since_last_seen_seconds=0.0,
            decay_explanation="Fresh pattern"
        )
        
        # Decision with advisory
        decision = engine.make_decision(
            transaction_id="txn_001",
            risk_score=risk_score,
            advisory=advisory
        )
        
        # Advisory should increase risk
        assert decision.advisory_applied is True
        assert decision.adjusted_score > risk_score.score
        assert len(decision.adjustment_factors) > 0
    
    def test_stale_advisory_less_impact(self):
        """
        Test: Stale (decayed) advisory has less impact than fresh advisory
        Expected: Effective confidence lower, less risk adjustment
        """
        from entity_a.decision import DecisionEngine
        from entity_a.models import RiskScore
        
        engine = DecisionEngine()
        
        risk_score = RiskScore(
            score=50.0,
            signals=["NEW_DEVICE"],
            features={},
            pattern=None,
            timestamp=datetime.utcnow()
        )
        
        # Stale advisory (low effective confidence due to decay)
        advisory = Advisory(
            advisory_id="adv_002",
            fingerprint="fp_" * 20,
            confidence="HIGH",
            severity="MEDIUM",
            summary="Aging pattern",
            recommendation="Monitor",
            message="Pattern not seen recently",
            recommended_actions=["Monitor"],
            affected_entities=["entity_a"],
            correlation_count=2,
            entity_count=2,
            fraud_score=60.0,
            timestamp=(datetime.utcnow() - timedelta(minutes=15)).isoformat(),
            # Decay fields - stale pattern
            base_confidence=0.75,
            decay_score=0.2,  # Stale (>10 minutes)
            effective_confidence=0.15,  # 0.75 * 0.2 = 0.15
            last_seen_timestamp=datetime.utcnow() - timedelta(minutes=15),
            pattern_status="DORMANT",
            time_since_last_seen_seconds=900,
            decay_explanation="Stale pattern, not seen for 15 minutes"
        )
        
        decision = engine.make_decision(
            transaction_id="txn_002",
            risk_score=risk_score,
            advisory=advisory
        )
        
        # Stale advisory should have minimal impact
        assert decision.advisory_applied is True
        # Adjustment should be small due to low effective_confidence
        assert decision.adjusted_score <= 60.0  # Should not increase much
        assert "effective_confidence: 0.150" in str(decision.adjustment_factors)


class TestMetricsTracking:
    """Test that metrics are properly tracked"""
    
    def test_metrics_initialization(self):
        """Test metrics tracker initializes correctly"""
        from bridge_hub.metrics import MetricsTracker
        
        tracker = MetricsTracker(window_size=3600)
        
        assert tracker.window_size == 3600
        assert len(tracker.ingestion_latencies) == 0
        assert len(tracker.correlation_latencies) == 0
        assert len(tracker.fingerprints_ingested) == 0
    
    def test_metrics_recording(self):
        """Test metrics are recorded correctly"""
        from bridge_hub.metrics import MetricsTracker
        
        tracker = MetricsTracker()
        
        # Record some events
        tracker.record_ingestion("entity_a", 15.5)
        tracker.record_ingestion("entity_a", 20.3)
        tracker.record_ingestion("entity_b", 18.7)
        
        tracker.record_correlation(5.2, detected=True)
        tracker.record_correlation(6.1, detected=True)
        tracker.record_correlation(4.8, detected=False)
        
        tracker.record_escalation()
        tracker.record_advisory("HIGH", 85.0)
        
        # Get summary
        summary = tracker.get_summary()
        
        assert summary.fingerprints_ingested == 3
        assert summary.correlations_detected == 2  # Only 2 detected
        assert summary.alerts_escalated == 1
        assert summary.advisories_generated == 1
        assert summary.active_entities == 2  # entity_a and entity_b
        assert summary.avg_ingestion_latency_ms > 0
        assert summary.avg_correlation_latency_ms > 0
    
    def test_percentile_calculation(self):
        """Test p95 latency calculation"""
        from bridge_hub.metrics import MetricsTracker
        
        tracker = MetricsTracker()
        
        # Add latency samples
        for i in range(100):
            tracker.record_ingestion(f"entity_{i % 5}", float(i))
        
        summary = tracker.get_summary()
        
        # P95 should be around 95th value
        assert 90 <= summary.p95_ingestion_latency_ms <= 99
    
    def test_rolling_window_pruning(self):
        """Test old metrics are pruned from rolling window"""
        from bridge_hub.metrics import MetricsTracker
        
        tracker = MetricsTracker(window_size=1)  # 1 second window
        
        # Record event
        tracker.record_ingestion("entity_a", 10.0)
        assert len(tracker.fingerprints_ingested) == 1
        
        # Wait for window to expire
        import time
        time.sleep(1.5)
        
        # Trigger pruning
        tracker._prune_old_timestamps()
        
        # Should be pruned
        assert len(tracker.fingerprints_ingested) == 0
