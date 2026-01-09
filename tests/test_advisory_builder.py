"""
Tests for Advisory Builder
"""
import pytest
from datetime import datetime
from bridge_hub.models import IntentAlert
from bridge_hub.advisory_builder import AdvisoryBuilder


@pytest.fixture
def builder():
    """Create advisory builder"""
    return AdvisoryBuilder()


@pytest.fixture
def critical_alert():
    """Create CRITICAL alert for testing"""
    return IntentAlert(
        alert_id="ALERT-CRIT-001",
        intent_type="COORDINATED_FRAUD",
        fingerprint="abc123def456",
        severity="CRITICAL",
        entity_count=5,
        confidence="HIGH",
        fraud_score=95,
        time_span_seconds=120.0,
        description="Test critical alert",
        rationale="Coordinated fraud pattern detected across 5 entities within 2 minutes",
        recommendation="IMMEDIATE: Flag all transactions, implement limits, notify investigation team",
        timestamp=datetime.utcnow()
    )


@pytest.fixture
def high_alert():
    """Create HIGH alert for testing"""
    return IntentAlert(
        alert_id="ALERT-HIGH-002",
        intent_type="COORDINATED_FRAUD",
        fingerprint="xyz789uvw012",
        severity="HIGH",
        entity_count=3,
        confidence="MEDIUM",
        fraud_score=70,
        time_span_seconds=180.0,
        description="Test high alert",
        rationale="Coordinated fraud pattern detected across 3 entities within 3 minutes",
        recommendation="URGENT: Flag transactions, monitor accounts, notify fraud team",
        timestamp=datetime.utcnow()
    )


@pytest.fixture
def medium_alert():
    """Create MEDIUM alert for testing"""
    return IntentAlert(
        alert_id="ALERT-MED-003",
        intent_type="COORDINATED_FRAUD",
        fingerprint="lmn345opq678",
        severity="MEDIUM",
        entity_count=2,
        confidence="LOW",
        fraud_score=45,
        time_span_seconds=240.0,
        description="Test medium alert",
        rationale="Coordinated fraud pattern detected across 2 entities within 4 minutes",
        recommendation="RECOMMENDED: Add to review queue, monitor for recurrence",
        timestamp=datetime.utcnow()
    )


def test_build_advisory_critical(builder, critical_alert):
    """Test building advisory from CRITICAL alert"""
    advisory = builder.build_advisory(critical_alert)
    
    assert advisory is not None
    assert advisory.severity == "CRITICAL"
    assert advisory.fingerprint == critical_alert.fingerprint
    assert advisory.fraud_score == 95
    assert advisory.entity_count == 5
    assert len(advisory.recommended_actions) == 6  # CRITICAL has 6 actions


def test_build_advisory_high(builder, high_alert):
    """Test building advisory from HIGH alert"""
    advisory = builder.build_advisory(high_alert)
    
    assert advisory is not None
    assert advisory.severity == "HIGH"
    assert len(advisory.recommended_actions) == 5  # HIGH has 5 actions


def test_build_advisory_medium(builder, medium_alert):
    """Test building advisory from MEDIUM alert"""
    advisory = builder.build_advisory(medium_alert)
    
    assert advisory is not None
    assert advisory.severity == "MEDIUM"
    assert len(advisory.recommended_actions) == 4  # MEDIUM has 4 actions


def test_advisory_id_format(builder, critical_alert):
    """Test advisory ID format"""
    advisory = builder.build_advisory(critical_alert)
    
    # Format: ADV-YYYYMMDD-HHMMSS-FINGERPRINT[:8]
    assert advisory.advisory_id.startswith("ADV-")
    assert len(advisory.advisory_id.split("-")) == 4
    assert advisory.advisory_id.endswith(critical_alert.fingerprint[:8])


def test_advisory_message_content(builder, critical_alert):
    """Test advisory message contains required information"""
    advisory = builder.build_advisory(critical_alert)
    
    message = advisory.message
    assert "SYNAPSE-FI Fraud Advisory" in message
    assert "Severity: CRITICAL" in message
    assert "Fraud Score: 95/100" in message
    assert "Confidence: HIGH" in message
    assert "5 " in message  # Entity count
    assert "PRIVACY NOTE" in message


def test_recommended_actions_critical(builder, critical_alert):
    """Test CRITICAL recommended actions"""
    advisory = builder.build_advisory(critical_alert)
    
    actions = advisory.recommended_actions
    assert any("IMMEDIATE" in action for action in actions)
    assert any("Flag all matching transactions" in action for action in actions)
    assert any("transaction limits" in action for action in actions)
    assert any("investigation team" in action for action in actions)


def test_recommended_actions_high(builder, high_alert):
    """Test HIGH recommended actions"""
    advisory = builder.build_advisory(high_alert)
    
    actions = advisory.recommended_actions
    assert any("URGENT" in action for action in actions)
    assert any("priority review" in action for action in actions)
    assert any("Monitor" in action for action in actions)


def test_recommended_actions_medium(builder, medium_alert):
    """Test MEDIUM recommended actions"""
    advisory = builder.build_advisory(medium_alert)
    
    actions = advisory.recommended_actions
    assert any("RECOMMENDED" in action for action in actions)
    assert any("review queue" in action for action in actions)


def test_build_all_clear_advisory(builder):
    """Test building all-clear advisory"""
    fingerprint = "test_pattern_clear"
    
    advisory = builder.build_all_clear_advisory(fingerprint)
    
    assert advisory is not None
    assert advisory.severity == "INFO"
    assert advisory.fingerprint == fingerprint
    assert advisory.fraud_score == 0
    assert advisory.entity_count == 0
    assert "no longer shows cross-entity correlation" in advisory.recommended_actions[0]


def test_all_clear_advisory_id(builder):
    """Test all-clear advisory ID format"""
    fingerprint = "abc123def456"
    
    advisory = builder.build_all_clear_advisory(fingerprint)
    
    assert advisory.advisory_id.startswith("ADV-CLEAR-")
    assert advisory.advisory_id.endswith(fingerprint[:8])


def test_all_clear_message_content(builder):
    """Test all-clear message content"""
    fingerprint = "test_pattern"
    
    advisory = builder.build_all_clear_advisory(fingerprint)
    
    message = advisory.message
    assert "Pattern Update" in message
    assert "previously flagged pattern" in message
    assert "has not shown coordinated activity" in message


def test_advisory_timestamp(builder, critical_alert):
    """Test advisory timestamp is set"""
    before = datetime.utcnow()
    advisory = builder.build_advisory(critical_alert)
    after = datetime.utcnow()
    
    assert before <= advisory.timestamp <= after


def test_multiple_advisories(builder, critical_alert, high_alert):
    """Test building multiple advisories"""
    advisory1 = builder.build_advisory(critical_alert)
    advisory2 = builder.build_advisory(high_alert)
    
    assert advisory1.advisory_id != advisory2.advisory_id
    assert advisory1.fingerprint != advisory2.fingerprint
