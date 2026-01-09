"""Tests for Entity A pattern classifier"""
import pytest
from entity_a.pattern_classifier import PatternClassifier
from entity_a.models import BehaviorPattern


def test_normal_pattern():
    """Test normal pattern classification"""
    classifier = PatternClassifier()
    
    # Few signals = normal
    signals = ["LOW_VALUE"]
    pattern = classifier.classify(signals)
    
    assert pattern == BehaviorPattern.NORMAL


def test_account_takeover_pattern():
    """Test account takeover pattern detection"""
    classifier = PatternClassifier()
    
    # Indicators: high velocity + new device + location shift
    signals = [
        "VERY_HIGH_VELOCITY",
        "NEW_DEVICE",
        "LOCATION_SHIFT"
    ]
    pattern = classifier.classify(signals)
    
    assert pattern == BehaviorPattern.ACCOUNT_TAKEOVER


def test_card_testing_pattern():
    """Test card testing pattern detection"""
    classifier = PatternClassifier()
    
    # Indicators: low amounts + high velocity
    signals = [
        "VERY_HIGH_VELOCITY",
        "LOW_VALUE"
    ]
    pattern = classifier.classify(signals)
    
    assert pattern == BehaviorPattern.CARD_TESTING


def test_velocity_abuse_pattern():
    """Test velocity abuse pattern detection"""
    classifier = PatternClassifier()
    
    # Just very high velocity
    signals = ["VERY_HIGH_VELOCITY"]
    pattern = classifier.classify(signals)
    
    assert pattern == BehaviorPattern.VELOCITY_ABUSE


def test_suspicious_timing_pattern():
    """Test suspicious timing pattern detection"""
    classifier = PatternClassifier()
    
    # Night transaction + high value
    signals = [
        "NIGHT_TRANSACTION",
        "HIGH_VALUE"
    ]
    pattern = classifier.classify(signals)
    
    assert pattern == BehaviorPattern.SUSPICIOUS_TIMING


def test_high_value_anomaly_pattern():
    """Test high value anomaly pattern detection"""
    classifier = PatternClassifier()
    
    # Amount deviation + high value
    signals = [
        "AMOUNT_DEVIATION",
        "HIGH_VALUE"
    ]
    pattern = classifier.classify(signals)
    
    assert pattern == BehaviorPattern.HIGH_VALUE_ANOMALY


def test_pattern_priority():
    """Test that more specific patterns take priority"""
    classifier = PatternClassifier()
    
    # Account takeover should win over velocity abuse
    signals = [
        "VERY_HIGH_VELOCITY",  # Would match velocity abuse
        "NEW_DEVICE",          # Plus these make account takeover
        "LOCATION_SHIFT"
    ]
    pattern = classifier.classify(signals)
    
    # Most specific pattern should be selected
    assert pattern == BehaviorPattern.ACCOUNT_TAKEOVER
