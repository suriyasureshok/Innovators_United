"""
Tests for Pattern Decay Logic
Validates decay calculations, reactivation, and lifecycle transitions
"""
import pytest
from datetime import datetime, timedelta

from bridge_hub.decay_engine import DecayEngine, PatternStatus

class TestDecayCalculations:
    """Test decay score calculations for different time windows"""
    
    def test_fresh_pattern_no_decay(self):
        """Fresh pattern (0-2 min) should have decay_score = 1.0"""
        engine = DecayEngine()
        
        last_seen = datetime.utcnow() - timedelta(seconds=60)  # 1 minute ago
        current = datetime.utcnow()
        
        result = engine.apply_decay(
            pattern_id="test_pattern_1",
            base_confidence=0.8,
            last_seen_timestamp=last_seen,
            current_timestamp=current
        )
        
        assert result['decay_score'] == 1.0, "Fresh pattern should have no decay"
        assert result['effective_confidence'] == 0.8, "Effective confidence should equal base"
        assert result['status'] == PatternStatus.ACTIVE.value
    
    def test_recent_pattern_decay(self):
        """Recent pattern (2-5 min) should have decay_score = 0.8"""
        engine = DecayEngine()
        
        last_seen = datetime.utcnow() - timedelta(seconds=180)  # 3 minutes ago
        current = datetime.utcnow()
        
        result = engine.apply_decay(
            pattern_id="test_pattern_2",
            base_confidence=0.9,
            last_seen_timestamp=last_seen,
            current_timestamp=current
        )
        
        assert result['decay_score'] == 0.8, "Recent pattern should have 0.8 decay"
        assert abs(result['effective_confidence'] - 0.72) < 0.01, "Effective confidence should be 0.9 * 0.8 = 0.72"
        assert result['status'] == PatternStatus.ACTIVE.value
    
    def test_aging_pattern_decay(self):
        """Aging pattern (5-10 min) should have decay_score = 0.5"""
        engine = DecayEngine()
        
        last_seen = datetime.utcnow() - timedelta(seconds=420)  # 7 minutes ago
        current = datetime.utcnow()
        
        result = engine.apply_decay(
            pattern_id="test_pattern_3",
            base_confidence=0.85,
            last_seen_timestamp=last_seen,
            current_timestamp=current
        )
        
        assert result['decay_score'] == 0.5, "Aging pattern should have 0.5 decay"
        assert abs(result['effective_confidence'] - 0.425) < 0.01, "Effective confidence should be 0.85 * 0.5 = 0.425"
        assert result['status'] == PatternStatus.COOLING.value
    
    def test_stale_pattern_decay(self):
        """Stale pattern (>10 min) should have decay_score = 0.2"""
        engine = DecayEngine()
        
        last_seen = datetime.utcnow() - timedelta(seconds=900)  # 15 minutes ago
        current = datetime.utcnow()
        
        result = engine.apply_decay(
            pattern_id="test_pattern_4",
            base_confidence=0.9,
            last_seen_timestamp=last_seen,
            current_timestamp=current
        )
        
        assert result['decay_score'] == 0.2, "Stale pattern should have 0.2 decay"
        assert abs(result['effective_confidence'] - 0.18) < 0.01, "Effective confidence should be 0.9 * 0.2 = 0.18"
        assert result['status'] == PatternStatus.DORMANT.value


class TestPatternLifecycle:
    """Test pattern lifecycle status transitions"""
    
    def test_active_status_high_confidence(self):
        """Pattern with eff_conf >= 0.7 should be ACTIVE"""
        engine = DecayEngine()
        
        result = engine.apply_decay(
            pattern_id="test_pattern_5",
            base_confidence=0.9,
            last_seen_timestamp=datetime.utcnow() - timedelta(seconds=30),
            current_timestamp=datetime.utcnow()
        )
        
        assert result['status'] == PatternStatus.ACTIVE.value
        assert result['effective_confidence'] >= 0.7
    
    def test_cooling_status_medium_confidence(self):
        """Pattern with 0.4 <= eff_conf < 0.7 should be COOLING"""
        engine = DecayEngine()
        
        result = engine.apply_decay(
            pattern_id="test_pattern_6",
            base_confidence=0.9,  # 0.9 * 0.5 = 0.45 (in COOLING range)
            last_seen_timestamp=datetime.utcnow() - timedelta(seconds=360),  # 6 min
            current_timestamp=datetime.utcnow()
        )
        
        assert result['status'] == PatternStatus.COOLING.value
        assert 0.4 <= result['effective_confidence'] < 0.7
    
    def test_dormant_status_low_confidence(self):
        """Pattern with eff_conf < 0.4 should be DORMANT"""
        engine = DecayEngine()
        
        result = engine.apply_decay(
            pattern_id="test_pattern_7",
            base_confidence=0.9,
            last_seen_timestamp=datetime.utcnow() - timedelta(seconds=900),  # 15 min
            current_timestamp=datetime.utcnow()
        )
        
        assert result['status'] == PatternStatus.DORMANT.value
        assert result['effective_confidence'] < 0.4


class TestPatternReactivation:
    """Test pattern reactivation when pattern reappears"""
    
    def test_reactivate_dormant_pattern(self):
        """Reactivating dormant pattern should reset to full strength"""
        engine = DecayEngine()
        
        # Initial dormant state
        old_timestamp = datetime.utcnow() - timedelta(seconds=900)  # 15 min ago
        current = datetime.utcnow()
        
        dormant_result = engine.apply_decay(
            pattern_id="test_pattern_8",
            base_confidence=0.8,
            last_seen_timestamp=old_timestamp,
            current_timestamp=current
        )
        
        assert dormant_result['status'] == PatternStatus.DORMANT.value
        
        # Reactivate pattern
        reactivated = engine.reactivate_pattern(
            pattern_id="test_pattern_8",
            new_base_confidence=0.85,
            current_timestamp=current
        )
        
        assert reactivated['decay_score'] == 1.0, "Reactivated pattern should have full strength"
        assert reactivated['effective_confidence'] == 0.85, "Effective confidence should equal base"
        assert reactivated['status'] == PatternStatus.ACTIVE.value
        assert reactivated['time_since_last_seen_seconds'] == 0.0
    
    def test_reactivate_cooling_pattern(self):
        """Reactivating cooling pattern should reset to ACTIVE"""
        engine = DecayEngine()
        current = datetime.utcnow()
        
        reactivated = engine.reactivate_pattern(
            pattern_id="test_pattern_9",
            new_base_confidence=0.75,
            current_timestamp=current
        )
        
        assert reactivated['status'] == PatternStatus.ACTIVE.value
        assert reactivated['decay_score'] == 1.0
        assert reactivated['effective_confidence'] == 0.75


class TestDecayExplanations:
    """Test human-readable decay explanations for audit"""
    
    def test_fresh_pattern_explanation(self):
        """Fresh pattern should explain no decay"""
        engine = DecayEngine()
        
        last_seen = datetime.utcnow() - timedelta(seconds=60)
        current = datetime.utcnow()
        
        result = engine.apply_decay(
            pattern_id="test_pattern_10",
            base_confidence=0.8,
            last_seen_timestamp=last_seen,
            current_timestamp=current
        )
        
        explanation = engine.generate_decay_explanation("test_pattern_10", result)
        
        assert "ACTIVE" in explanation
        assert "0.80" in explanation or "0.8" in explanation
        assert "full influence" in explanation.lower()
    
    def test_aging_pattern_explanation(self):
        """Aging pattern should explain decay reduction"""
        engine = DecayEngine()
        
        last_seen = datetime.utcnow() - timedelta(seconds=420)  # 7 min
        current = datetime.utcnow()
        
        result = engine.apply_decay(
            pattern_id="test_pattern_11",
            base_confidence=0.85,
            last_seen_timestamp=last_seen,
            current_timestamp=current
        )
        
        explanation = engine.generate_decay_explanation("test_pattern_11", result)
        
        assert "0.5" in explanation or "50%" in explanation
        assert "7 minutes" in explanation
        assert "0.42" in explanation or "42" in explanation  # effective confidence
    
    def test_dormant_pattern_explanation(self):
        """Dormant pattern should warn about staleness"""
        engine = DecayEngine()
        
        last_seen = datetime.utcnow() - timedelta(seconds=900)  # 15 min
        current = datetime.utcnow()
        
        result = engine.apply_decay(
            pattern_id="test_pattern_12",
            base_confidence=0.9,
            last_seen_timestamp=last_seen,
            current_timestamp=current
        )
        
        explanation = engine.generate_decay_explanation("test_pattern_12", result)
        
        assert "DORMANT" in explanation
        assert "15 minutes" in explanation
        assert "0.18" in explanation or "18" in explanation  # effective confidence


class TestCustomWindows:
    """Test custom time window configurations"""
    
    def test_custom_windows(self):
        """Test engine with custom decay windows"""
        custom_config = {
            'decay_windows': {
                'fresh': {'max_seconds': 60, 'decay_score': 1.0},      # 0-1 min: 1.0
                'recent': {'max_seconds': 180, 'decay_score': 0.9},    # 1-3 min: 0.9
                'aging': {'max_seconds': 300, 'decay_score': 0.7},     # 3-5 min: 0.7
                'stale': {'max_seconds': float('inf'), 'decay_score': 0.1}  # >5 min: 0.1
            }
        }
        
        engine = DecayEngine(config=custom_config)
        
        # Test 2 minutes ago (should use 0.9)
        result = engine.apply_decay(
            pattern_id="test_pattern_13",
            base_confidence=0.8,
            last_seen_timestamp=datetime.utcnow() - timedelta(seconds=120),
            current_timestamp=datetime.utcnow()
        )
        
        assert result['decay_score'] == 0.9
        assert abs(result['effective_confidence'] - 0.72) < 0.01


class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_zero_time_difference(self):
        """Pattern observed at exactly current time should have no decay"""
        engine = DecayEngine()
        current = datetime.utcnow()
        
        result = engine.apply_decay(
            pattern_id="test_pattern_14",
            base_confidence=0.85,
            last_seen_timestamp=current,
            current_timestamp=current
        )
        
        assert result['decay_score'] == 1.0
        assert result['effective_confidence'] == 0.85
        assert result['time_since_last_seen_seconds'] == 0.0
    
    def test_boundary_at_2_minutes(self):
        """Test exact boundary at 2 minutes (120s)"""
        engine = DecayEngine()
        
        # Exactly 120 seconds (should be end of fresh window)
        result = engine.apply_decay(
            pattern_id="test_pattern_15",
            base_confidence=0.8,
            last_seen_timestamp=datetime.utcnow() - timedelta(seconds=120),
            current_timestamp=datetime.utcnow()
        )
        
        assert result['decay_score'] == 1.0, "Exactly 2 min should still be fresh"
    
    def test_just_after_2_minutes(self):
        """Test just after 2 minutes (121s) - should enter recent window"""
        engine = DecayEngine()
        
        result = engine.apply_decay(
            pattern_id="test_pattern_16",
            base_confidence=0.8,
            last_seen_timestamp=datetime.utcnow() - timedelta(seconds=121),
            current_timestamp=datetime.utcnow()
        )
        
        assert result['decay_score'] == 0.8, "Just after 2 min should be recent"
    
    def test_very_low_base_confidence(self):
        """Test with very low base confidence"""
        engine = DecayEngine()
        
        result = engine.apply_decay(
            pattern_id="test_pattern_17",
            base_confidence=0.1,
            last_seen_timestamp=datetime.utcnow() - timedelta(seconds=60),
            current_timestamp=datetime.utcnow()
        )
        
        assert result['effective_confidence'] == 0.1
        assert result['status'] == PatternStatus.DORMANT.value  # Low confidence = DORMANT
    
    def test_max_base_confidence(self):
        """Test with maximum base confidence"""
        engine = DecayEngine()
        
        result = engine.apply_decay(
            pattern_id="test_pattern_18",
            base_confidence=1.0,
            last_seen_timestamp=datetime.utcnow() - timedelta(seconds=30),
            current_timestamp=datetime.utcnow()
        )
        
        assert result['effective_confidence'] == 1.0
        assert result['status'] == PatternStatus.ACTIVE.value


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
