"""
Tests for Escalation Engine
"""
import pytest
from datetime import datetime
from bridge_hub.models import CorrelationResult
from bridge_hub.escalation_engine import EscalationEngine


@pytest.fixture
def engine():
    """Create escalation engine"""
    config = {
        'critical_threshold': 4,
        'high_threshold': 3,
        'medium_threshold': 2
    }
    return EscalationEngine(config)


@pytest.fixture
def sample_observations():
    """Sample observations for testing"""
    return [
        {
            'entity_id': 'entity_a',
            'severity': 'HIGH',
            'timestamp': datetime.utcnow()
        }
    ]


def test_evaluate_critical(engine, sample_observations):
    """Test CRITICAL severity escalation"""
    correlation = CorrelationResult(
        fingerprint="test_pattern",
        entity_count=5,  # >= 4
        time_span_seconds=60.0,
        confidence="HIGH",
        observations=sample_observations * 5
    )
    
    alert = engine.evaluate(correlation)
    
    assert alert is not None
    assert alert.severity == "CRITICAL"
    assert alert.entity_count == 5
    assert alert.fraud_score > 0


def test_evaluate_high(engine, sample_observations):
    """Test HIGH severity escalation"""
    correlation = CorrelationResult(
        fingerprint="test_pattern",
        entity_count=3,  # >= 3
        time_span_seconds=60.0,
        confidence="HIGH",
        observations=sample_observations * 3
    )
    
    alert = engine.evaluate(correlation)
    
    assert alert is not None
    assert alert.severity == "HIGH"


def test_evaluate_medium(engine, sample_observations):
    """Test MEDIUM severity escalation"""
    correlation = CorrelationResult(
        fingerprint="test_pattern",
        entity_count=2,  # >= 2
        time_span_seconds=60.0,
        confidence="MEDIUM",
        observations=sample_observations * 2
    )
    
    alert = engine.evaluate(correlation)
    
    assert alert is not None
    assert alert.severity == "MEDIUM"


def test_evaluate_below_threshold(engine, sample_observations):
    """Test no escalation when below threshold"""
    correlation = CorrelationResult(
        fingerprint="test_pattern",
        entity_count=1,  # < 2
        time_span_seconds=60.0,
        confidence="LOW",
        observations=sample_observations
    )
    
    alert = engine.evaluate(correlation)
    
    assert alert is None


def test_fraud_score_calculation(engine, sample_observations):
    """Test fraud score calculation"""
    # High entity count + HIGH confidence
    correlation = CorrelationResult(
        fingerprint="test_pattern",
        entity_count=4,
        time_span_seconds=60.0,
        confidence="HIGH",
        observations=sample_observations * 4
    )
    
    alert = engine.evaluate(correlation)
    
    assert alert is not None
    # Score = (4 * 20) + 10 (HIGH confidence) = 90
    assert alert.fraud_score == 90


def test_fraud_score_time_penalty(engine, sample_observations):
    """Test fraud score time span penalty"""
    # Long time span should reduce score
    correlation = CorrelationResult(
        fingerprint="test_pattern",
        entity_count=2,
        time_span_seconds=700.0,  # > 600s
        confidence="LOW",
        observations=sample_observations * 2
    )
    
    alert = engine.evaluate(correlation)
    
    assert alert is not None
    # Score = (2 * 20) - 10 (time penalty) = 30
    assert alert.fraud_score == 30


def test_fraud_score_bounds(engine, sample_observations):
    """Test fraud score stays within 0-100"""
    # Very high entity count
    correlation = CorrelationResult(
        fingerprint="test_pattern",
        entity_count=10,
        time_span_seconds=30.0,
        confidence="HIGH",
        observations=sample_observations * 10
    )
    
    alert = engine.evaluate(correlation)
    
    assert alert is not None
    assert 0 <= alert.fraud_score <= 100


def test_alert_description(engine, sample_observations):
    """Test alert description generation"""
    correlation = CorrelationResult(
        fingerprint="test_pattern_abc123",
        entity_count=3,
        time_span_seconds=120.0,
        confidence="HIGH",
        observations=sample_observations * 3
    )
    
    alert = engine.evaluate(correlation)
    
    assert alert is not None
    assert "HIGH fraud intent detected" in alert.description
    assert "3 entities" in alert.description
    assert "test_pat" in alert.description  # Truncated fingerprint


def test_update_config(engine):
    """Test configuration update"""
    new_config = {
        'critical_threshold': 5,
        'high_threshold': 4,
        'medium_threshold': 3
    }
    
    engine.update_config(new_config)
    
    assert engine.critical_threshold == 5
    assert engine.high_threshold == 4
    assert engine.medium_threshold == 3


def test_intent_type(engine, sample_observations):
    """Test intent type is always COORDINATED_FRAUD"""
    correlation = CorrelationResult(
        fingerprint="test_pattern",
        entity_count=3,
        time_span_seconds=60.0,
        confidence="HIGH",
        observations=sample_observations * 3
    )
    
    alert = engine.evaluate(correlation)
    
    assert alert is not None
    assert alert.intent_type == "COORDINATED_FRAUD"
