"""
Tests for Behavioral Risk Graph
"""
import pytest
from datetime import datetime, timedelta
from bridge_hub.brg_graph import BehavioralRiskGraph


@pytest.fixture
def brg():
    """Create BRG instance for testing"""
    return BehavioralRiskGraph(max_age_seconds=300)


def test_add_pattern_observation(brg):
    """Test adding pattern observation to graph"""
    fingerprint = "test_pattern_123"
    entity_id = "entity_a"
    severity = "HIGH"
    timestamp = datetime.utcnow()
    
    brg.add_pattern_observation(fingerprint, entity_id, severity, timestamp)
    
    # Check node exists
    assert brg.graph.has_node(fingerprint)
    
    # Check edge exists
    assert brg.graph.number_of_edges() == 1


def test_get_recent_observations(brg):
    """Test retrieving recent observations"""
    fingerprint = "test_pattern_456"
    now = datetime.utcnow()
    
    # Add multiple observations
    brg.add_pattern_observation(fingerprint, "entity_a", "HIGH", now - timedelta(seconds=10))
    brg.add_pattern_observation(fingerprint, "entity_b", "MEDIUM", now - timedelta(seconds=5))
    brg.add_pattern_observation(fingerprint, "entity_c", "HIGH", now)
    
    # Get recent observations
    observations = brg.get_recent_observations(fingerprint, timedelta(seconds=60))
    
    assert len(observations) == 3
    assert observations[0]['entity_id'] == 'entity_a'
    assert observations[2]['entity_id'] == 'entity_c'


def test_get_unique_entities(brg):
    """Test counting unique entities for pattern"""
    fingerprint = "test_pattern_789"
    now = datetime.utcnow()
    
    # Add observations from multiple entities
    brg.add_pattern_observation(fingerprint, "entity_a", "HIGH", now)
    brg.add_pattern_observation(fingerprint, "entity_b", "HIGH", now)
    brg.add_pattern_observation(fingerprint, "entity_a", "MEDIUM", now)  # Duplicate entity
    
    unique_count = brg.get_unique_entities(fingerprint, timedelta(seconds=60))
    
    assert unique_count == 2  # Only entity_a and entity_b


def test_prune_expired_edges(brg):
    """Test pruning expired edges"""
    now = datetime.utcnow()
    old_time = now - timedelta(seconds=400)  # Beyond max_age
    
    # Add old and new observations
    brg.add_pattern_observation("pattern_old", "entity_a", "HIGH", old_time)
    brg.add_pattern_observation("pattern_new", "entity_b", "HIGH", now)
    
    # Prune
    removed = brg.prune_expired_edges()
    
    assert removed == 1
    assert brg.graph.number_of_edges() == 1


def test_get_active_entities(brg):
    """Test getting active entities"""
    now = datetime.utcnow()
    
    # Add observations from different entities
    brg.add_pattern_observation("pattern_1", "entity_a", "HIGH", now)
    brg.add_pattern_observation("pattern_2", "entity_b", "HIGH", now)
    brg.add_pattern_observation("pattern_3", "entity_a", "MEDIUM", now)
    
    active = brg.get_active_entities(minutes=5)
    
    assert len(active) == 2
    assert "entity_a" in active
    assert "entity_b" in active


def test_graph_stats(brg):
    """Test getting graph statistics"""
    now = datetime.utcnow()
    
    # Add multiple patterns and observations
    brg.add_pattern_observation("pattern_1", "entity_a", "HIGH", now)
    brg.add_pattern_observation("pattern_2", "entity_b", "HIGH", now)
    brg.add_pattern_observation("pattern_1", "entity_c", "MEDIUM", now)
    
    stats = brg.get_stats()
    
    assert stats['unique_patterns'] == 2
    assert stats['total_observations'] == 3
    assert stats['unique_entities'] == 3


def test_empty_graph(brg):
    """Test operations on empty graph"""
    observations = brg.get_recent_observations("nonexistent", timedelta(seconds=60))
    assert observations == []
    
    count = brg.get_unique_entities("nonexistent", timedelta(seconds=60))
    assert count == 0
    
    removed = brg.prune_expired_edges()
    assert removed == 0
