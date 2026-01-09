"""
Tests for Temporal Correlator
"""
import pytest
from datetime import datetime, timedelta
from bridge_hub.brg_graph import BehavioralRiskGraph
from bridge_hub.temporal_correlator import TemporalCorrelator


@pytest.fixture
def brg():
    """Create BRG instance"""
    return BehavioralRiskGraph(max_age_seconds=300)


@pytest.fixture
def correlator():
    """Create correlator instance"""
    config = {
        'entity_threshold': 2,
        'time_window_seconds': 300
    }
    return TemporalCorrelator(config)


def test_detect_correlation_success(brg, correlator):
    """Test successful correlation detection"""
    fingerprint = "test_pattern_correlated"
    now = datetime.utcnow()
    
    # Add observations from multiple entities
    brg.add_pattern_observation(fingerprint, "entity_a", "HIGH", now - timedelta(seconds=10))
    brg.add_pattern_observation(fingerprint, "entity_b", "HIGH", now - timedelta(seconds=5))
    
    # Detect correlation
    result = correlator.detect_correlation(fingerprint, brg)
    
    assert result is not None
    assert result.entity_count == 2
    assert result.fingerprint == fingerprint
    assert result.confidence in ["LOW", "MEDIUM", "HIGH"]


def test_detect_correlation_threshold_not_met(brg, correlator):
    """Test correlation when threshold not met"""
    fingerprint = "test_pattern_single"
    now = datetime.utcnow()
    
    # Add observation from only one entity
    brg.add_pattern_observation(fingerprint, "entity_a", "HIGH", now)
    
    # Detect correlation
    result = correlator.detect_correlation(fingerprint, brg)
    
    assert result is None  # Threshold not met


def test_detect_correlation_no_observations(brg, correlator):
    """Test correlation with no observations"""
    result = correlator.detect_correlation("nonexistent_pattern", brg)
    
    assert result is None


def test_confidence_calculation_high(brg, correlator):
    """Test HIGH confidence calculation"""
    fingerprint = "test_pattern_high_conf"
    now = datetime.utcnow()
    
    # Add observations from 3+ entities in short time
    brg.add_pattern_observation(fingerprint, "entity_a", "HIGH", now - timedelta(seconds=30))
    brg.add_pattern_observation(fingerprint, "entity_b", "HIGH", now - timedelta(seconds=20))
    brg.add_pattern_observation(fingerprint, "entity_c", "HIGH", now - timedelta(seconds=10))
    
    result = correlator.detect_correlation(fingerprint, brg)
    
    assert result is not None
    assert result.confidence == "HIGH"


def test_confidence_calculation_medium(brg, correlator):
    """Test MEDIUM confidence calculation"""
    fingerprint = "test_pattern_medium_conf"
    now = datetime.utcnow()
    
    # Add observations from 2 entities in medium time window
    brg.add_pattern_observation(fingerprint, "entity_a", "HIGH", now - timedelta(seconds=200))
    brg.add_pattern_observation(fingerprint, "entity_b", "HIGH", now)
    
    result = correlator.detect_correlation(fingerprint, brg)
    
    assert result is not None
    assert result.confidence == "MEDIUM"


def test_update_config(correlator):
    """Test configuration update"""
    new_config = {
        'entity_threshold': 3,
        'time_window_seconds': 600
    }
    
    correlator.update_config(new_config)
    
    assert correlator.entity_threshold == 3
    assert correlator.time_window_seconds == 600


def test_time_span_calculation(brg, correlator):
    """Test time span calculation in result"""
    fingerprint = "test_pattern_timespan"
    now = datetime.utcnow()
    
    # Add observations with known time span
    brg.add_pattern_observation(fingerprint, "entity_a", "HIGH", now - timedelta(seconds=100))
    brg.add_pattern_observation(fingerprint, "entity_b", "HIGH", now)
    
    result = correlator.detect_correlation(fingerprint, brg)
    
    assert result is not None
    assert 95 <= result.time_span_seconds <= 105  # Allow small margin
