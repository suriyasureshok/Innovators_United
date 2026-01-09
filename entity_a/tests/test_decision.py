"""Tests for Entity A decision engine"""
import pytest
from datetime import datetime
from entity_a.models import Transaction, RiskScore, BehaviorPattern, DecisionAction
from entity_a.decision import DecisionEngine, ExplanationGenerator
from bridge_hub.models import Advisory


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


@pytest.fixture
def low_risk_score():
    """Low risk score"""
    return RiskScore(
        score=25.0,
        signals=["LOW_VALUE"],
        features={"velocity_count": 1}
    )


@pytest.fixture
def medium_risk_score():
    """Medium risk score"""
    return RiskScore(
        score=55.0,
        signals=["HIGH_VELOCITY", "NEW_DEVICE"],
        features={"velocity_count": 8}
    )


@pytest.fixture
def high_risk_score():
    """High risk score"""
    return RiskScore(
        score=85.0,
        signals=["VERY_HIGH_VELOCITY", "NEW_DEVICE", "LOCATION_SHIFT"],
        features={"velocity_count": 15}
    )


def test_allow_decision(sample_transaction, low_risk_score):
    """Test ALLOW decision for low risk"""
    engine = DecisionEngine()
    
    decision = engine.make_decision(
        transaction_id=sample_transaction.transaction_id,
        risk_score=low_risk_score,
        advisory=None
    )
    
    assert decision.action == DecisionAction.ALLOW


def test_step_up_decision(sample_transaction, medium_risk_score):
    """Test STEP_UP decision for medium risk"""
    engine = DecisionEngine()
    
    decision = engine.make_decision(
        transaction_id=sample_transaction.transaction_id,
        risk_score=medium_risk_score,
        advisory=None
    )
    
    assert decision.action == DecisionAction.STEP_UP


def test_block_decision(sample_transaction, high_risk_score):
    """Test BLOCK decision for high risk"""
    engine = DecisionEngine()
    
    decision = engine.make_decision(
        transaction_id=sample_transaction.transaction_id,
        risk_score=high_risk_score,
        advisory=None
    )
    
    assert decision.action == DecisionAction.BLOCK


def test_advisory_influence(sample_transaction, medium_risk_score):
    """Test that BRIDGE advisory influences decision"""
    engine = DecisionEngine()
    
    # Create high confidence advisory  
    advisory = Advisory(
        advisory_id="adv_001",
        fingerprint="fp_abc123",
        confidence="HIGH",
        severity="HIGH",
        summary="Cross-entity fraud pattern detected",
        recommendation="Increase scrutiny on similar transactions",
        message="Fraud pattern detected",
        recommended_actions=["Review transaction", "Contact customer"],
        affected_entities=["entity_a", "entity_b"],
        correlation_count=3,
        entity_count=2,
        fraud_score=85.0,
        timestamp=datetime.now().isoformat()
    )
    
    # Decision without advisory
    decision_no_adv = engine.make_decision(
        transaction_id=sample_transaction.transaction_id,
        risk_score=medium_risk_score,
        advisory=None
    )
    
    # Decision with advisory
    decision_with_adv = engine.make_decision(
        transaction_id=sample_transaction.transaction_id,
        risk_score=medium_risk_score,
        advisory=advisory
    )
    
    # Advisory should increase adjusted score
    assert decision_with_adv.adjusted_score > decision_no_adv.adjusted_score


def test_explanation_generation(sample_transaction, medium_risk_score):
    """Test explanation generation"""
    generator = ExplanationGenerator()
    engine = DecisionEngine()
    
    # Create decision
    decision = engine.make_decision(
        transaction_id=sample_transaction.transaction_id,
        risk_score=medium_risk_score,
        advisory=None
    )
    
    # Generate explanation
    explanation = generator.generate_explanation(
        transaction_id=sample_transaction.transaction_id,
        risk_score=medium_risk_score,
        decision=decision,
        advisory=None
    )
    
    # Check explanation contains key sections
    assert "FRAUD PREVENTION DECISION REPORT" in explanation or "DECISION REPORT" in explanation
    assert explanation is not None
