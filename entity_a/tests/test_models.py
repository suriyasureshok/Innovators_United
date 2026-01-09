"""Tests for Entity A models"""
import pytest
from datetime import datetime
from entity_a.models import (
    Transaction,
    RiskScore,
    Decision,
    DecisionAction,
    BehaviorPattern
)


def test_transaction_creation():
    """Test Transaction model creation"""
    transaction = Transaction(
        transaction_id="txn_001",
        user_id="user_123",
        amount=100.50,
        merchant_id="merchant_abc",
        merchant_category="retail",
        timestamp=datetime.now().isoformat(),
        device_id="device_xyz",
        ip_address="192.168.1.1",
        location="US"
    )
    
    assert transaction.transaction_id == "txn_001"
    assert transaction.user_id == "user_123"
    assert transaction.amount == 100.50
    assert transaction.merchant_id == "merchant_abc"


def test_risk_score_creation():
    """Test RiskScore model creation"""
    risk_score = RiskScore(
        score=75.5,
        signals=["HIGH_VELOCITY", "NEW_DEVICE"],
        features={
            "velocity_count": 10,
            "device_age_days": 0
        }
    )
    
    assert risk_score.score == 75.5
    assert len(risk_score.signals) == 2
    assert "HIGH_VELOCITY" in risk_score.signals
    assert risk_score.features["velocity_count"] == 10


def test_decision_creation():
    """Test Decision model creation"""
    decision = Decision(
        transaction_id="txn_001",
        action=DecisionAction.BLOCK,
        risk_score=85.0,
        adjusted_score=85.0,
        explanation="High risk transaction blocked"
    )
    
    assert decision.transaction_id == "txn_001"
    assert decision.action == DecisionAction.BLOCK
    assert decision.risk_score == 85.0
    assert "High risk" in decision.explanation


def test_decision_action_enum():
    """Test DecisionAction enum values"""
    assert DecisionAction.ALLOW.value == "allow"
    assert DecisionAction.STEP_UP.value == "step_up"
    assert DecisionAction.BLOCK.value == "block"


def test_behavior_pattern_enum():
    """Test BehaviorPattern enum values"""
    assert BehaviorPattern.NORMAL.value == "normal"
    assert BehaviorPattern.ACCOUNT_TAKEOVER.value == "account_takeover"
    assert BehaviorPattern.CARD_TESTING.value == "card_testing"
    assert BehaviorPattern.VELOCITY_ABUSE.value == "velocity_abuse"
