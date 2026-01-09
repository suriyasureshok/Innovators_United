"""Tests for Entity A risk engine"""
import pytest
from datetime import datetime
from entity_a.models import Transaction
from entity_a.risk_engine import FeatureExtractor, RiskScorer


@pytest.fixture
def sample_transaction():
    """Create sample transaction"""
    return Transaction(
        transaction_id="txn_001",
        user_id="user_123",
        amount=100.0,
        merchant_id="merchant_abc",
        merchant_category="retail",
        timestamp=datetime.now().isoformat(),
        device_id="device_xyz",
        ip_address="192.168.1.1",
        location="US"
    )


def test_feature_extraction(sample_transaction):
    """Test feature extraction"""
    extractor = FeatureExtractor()
    features = extractor.extract_features(sample_transaction)
    
    # Check key features present
    assert "velocity_count" in features
    assert "device_age_days" in features
    assert "amount" in features
    assert "hour_of_day" in features
    assert "is_new_device" in features


def test_risk_scoring_normal(sample_transaction):
    """Test risk scoring for normal transaction"""
    extractor = FeatureExtractor()
    scorer = RiskScorer()
    
    features = extractor.extract_features(sample_transaction)
    risk_score = scorer.calculate_risk_score(features)
    
    assert 0 <= risk_score.score <= 100
    assert isinstance(risk_score.signals, list)
    assert isinstance(risk_score.features, dict)


def test_high_velocity_detection():
    """Test high velocity detection"""
    extractor = FeatureExtractor()
    scorer = RiskScorer()
    
    # Generate multiple transactions quickly
    for i in range(15):
        txn = Transaction(
            transaction_id=f"txn_{i}",
            user_id="user_123",
            amount=50.0,
            merchant_id="merchant_abc",
            merchant_category="retail",
            timestamp=datetime.now().isoformat(),
            device_id="device_xyz",
            ip_address="192.168.1.1",
            location="US"
        )
        
        features = extractor.extract_features(txn)
        risk_score = scorer.calculate_risk_score(features)
    
    # Last transaction should have high velocity signal
    assert "HIGH_VELOCITY" in risk_score.signals or "VERY_HIGH_VELOCITY" in risk_score.signals


def test_new_device_detection():
    """Test new device detection"""
    extractor = FeatureExtractor()
    scorer = RiskScorer()
    
    txn = Transaction(
        transaction_id="txn_001",
        user_id="user_123",
        amount=100.0,
        merchant_id="merchant_abc",
        merchant_category="retail",
        timestamp=datetime.now().isoformat(),
        device_id="new_device_xyz",
        ip_address="192.168.1.1",
        location="US"
    )
    
    features = extractor.extract_features(txn)
    risk_score = scorer.calculate_risk_score(features)
    
    # First transaction from device should trigger NEW_DEVICE or UNKNOWN_DEVICE
    assert "NEW_DEVICE" in risk_score.signals or "UNKNOWN_DEVICE" in risk_score.signals


def test_high_value_detection():
    """Test high value transaction detection"""
    extractor = FeatureExtractor()
    scorer = RiskScorer()
    
    txn = Transaction(
        transaction_id="txn_001",
        user_id="user_123",
        amount=5500.0,  # Above $5000 threshold
        merchant_id="merchant_abc",
        merchant_category="retail",
        timestamp=datetime.now().isoformat(),
        device_id="device_xyz",
        ip_address="192.168.1.1",
        location="US"
    )
    
    features = extractor.extract_features(txn)
    risk_score = scorer.calculate_risk_score(features)
    
    # Accept either HIGH_VALUE or VERY_HIGH_VALUE for amounts above $5000
    assert "HIGH_VALUE" in risk_score.signals or "VERY_HIGH_VALUE" in risk_score.signals
