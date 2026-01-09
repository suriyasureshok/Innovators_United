"""Tests for Entity A fingerprint generator"""
import pytest
from datetime import datetime
from entity_b.fingerprint import FingerprintGenerator
from entity_b.models import BehaviorPattern


def test_fingerprint_generation():
    """Test fingerprint generation"""
    generator = FingerprintGenerator(entity_id="entity_a")
    
    fingerprint = generator.generate_fingerprint(
        pattern=BehaviorPattern.ACCOUNT_TAKEOVER,
        severity="HIGH",
        timestamp=datetime.now()
    )
    
    # Check format
    assert fingerprint.startswith("fp_")
    assert len(fingerprint) == 19  # "fp_" + 16 hex chars


def test_fingerprint_with_string_timestamp():
    """Test fingerprint with ISO string timestamp"""
    generator = FingerprintGenerator(entity_id="entity_a")
    
    fingerprint = generator.generate_fingerprint(
        pattern=BehaviorPattern.ACCOUNT_TAKEOVER,
        severity="HIGH",
        timestamp="2024-01-09T10:00:00"
    )
    
    assert fingerprint.startswith("fp_")


def test_fingerprint_consistency():
    """Test that same inputs produce same fingerprint"""
    generator = FingerprintGenerator(entity_id="entity_a")
    
    timestamp = datetime(2024, 1, 9, 10, 0, 0)
    
    fp1 = generator.generate_fingerprint(
        pattern=BehaviorPattern.ACCOUNT_TAKEOVER,
        severity="HIGH",
        timestamp=timestamp
    )
    
    fp2 = generator.generate_fingerprint(
        pattern=BehaviorPattern.ACCOUNT_TAKEOVER,
        severity="HIGH",
        timestamp=timestamp
    )
    
    assert fp1 == fp2


def test_fingerprint_uniqueness():
    """Test that different inputs produce different fingerprints"""
    generator = FingerprintGenerator(entity_id="entity_a")
    
    timestamp = datetime.now()
    
    fp1 = generator.generate_fingerprint(
        pattern=BehaviorPattern.ACCOUNT_TAKEOVER,
        severity="HIGH",
        timestamp=timestamp
    )
    
    fp2 = generator.generate_fingerprint(
        pattern=BehaviorPattern.CARD_TESTING,  # Different pattern
        severity="HIGH",
        timestamp=timestamp
    )
    
    assert fp1 != fp2


def test_fingerprint_privacy():
    """Test that fingerprint is irreversible hash"""
    generator = FingerprintGenerator(entity_id="entity_a")
    
    fingerprint = generator.generate_fingerprint(
        pattern=BehaviorPattern.ACCOUNT_TAKEOVER,
        severity="HIGH",
        timestamp=datetime.now()
    )
    
    # Should not contain original pattern string
    assert "account_takeover" not in fingerprint.lower()
    
    # Should be hex format only
    hex_part = fingerprint[3:]  # Remove "fp_"
    assert all(c in "0123456789abcdef" for c in hex_part)
