"""
Pattern Decay Engine
Manages behavioral pattern lifecycle through time-based decay logic
"""
from typing import Dict, Optional
from datetime import datetime, timedelta
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class PatternStatus(str, Enum):
    """Pattern lifecycle states"""
    ACTIVE = "ACTIVE"         # effective_confidence >= 0.7
    COOLING = "COOLING"       # 0.4 <= effective_confidence < 0.7
    DORMANT = "DORMANT"       # effective_confidence < 0.4


class DecayEngine:
    """
    Manages pattern decay logic for BRIDGE Hub
    
    CRITICAL PRINCIPLES:
    - Decay reduces confidence influence, NOT memory
    - Patterns are never deleted, only downgraded
    - Uses discrete time windows, NOT continuous math
    - Fresh patterns retain full influence
    - Reactivation is immediate upon reappearance
    """
    
    def __init__(self, config: Dict = None):
        """
        Initialize decay engine
        
        Args:
            config: Configuration with decay windows and thresholds
        """
        self.config = config or {}
        
        # Discrete decay windows (time → decay_score)
        # MUST be configurable, NOT hardcoded
        self.decay_windows = self.config.get('decay_windows', {
            'fresh': {'max_seconds': 120, 'decay_score': 1.0},      # 0-2 minutes: full strength
            'recent': {'max_seconds': 300, 'decay_score': 0.8},     # 2-5 minutes: 80%
            'aging': {'max_seconds': 600, 'decay_score': 0.5},      # 5-10 minutes: 50%
            'stale': {'max_seconds': float('inf'), 'decay_score': 0.2}  # >10 minutes: 20%
        })
        
        # Pattern status thresholds
        self.status_thresholds = self.config.get('status_thresholds', {
            'active_min': 0.7,
            'cooling_min': 0.4
        })
        
        logger.info(f"Initialized DecayEngine with {len(self.decay_windows)} decay windows")
    
    def calculate_decay_score(
        self,
        last_seen_timestamp: datetime,
        current_timestamp: Optional[datetime] = None
    ) -> float:
        """
        Calculate decay score based on time since last observation
        
        Uses discrete time windows - NO continuous math, NO exponentials
        
        Args:
            last_seen_timestamp: When pattern was last observed
            current_timestamp: Current time (defaults to now)
            
        Returns:
            Decay score between 0.0 and 1.0
        """
        if current_timestamp is None:
            current_timestamp = datetime.utcnow()
        
        # Calculate time delta
        delta = current_timestamp - last_seen_timestamp
        delta_seconds = delta.total_seconds()
        
        # Lookup decay score from discrete windows
        # Windows must be evaluated in order (fresh → stale)
        decay_score = 0.2  # Default to stale
        
        for window_name in ['fresh', 'recent', 'aging', 'stale']:
            window = self.decay_windows.get(window_name, {})
            max_seconds = window.get('max_seconds', float('inf'))
            
            if delta_seconds <= max_seconds:
                decay_score = window.get('decay_score', 0.2)
                logger.debug(f"Pattern age {delta_seconds:.0f}s → {window_name} window → decay_score={decay_score}")
                break
        
        return decay_score
    
    def calculate_effective_confidence(
        self,
        base_confidence: float,
        decay_score: float
    ) -> float:
        """
        Calculate effective confidence for decision-making
        
        Formula: effective_confidence = base_confidence × decay_score
        
        Args:
            base_confidence: Base correlation confidence (0.0-1.0)
            decay_score: Time-based decay factor (0.0-1.0)
            
        Returns:
            Effective confidence (0.0-1.0)
        """
        effective_confidence = base_confidence * decay_score
        return round(min(1.0, max(0.0, effective_confidence)), 4)
    
    def determine_pattern_status(self, effective_confidence: float) -> PatternStatus:
        """
        Determine pattern lifecycle status based on effective confidence
        
        Args:
            effective_confidence: Decayed confidence value
            
        Returns:
            PatternStatus (ACTIVE, COOLING, or DORMANT)
        """
        if effective_confidence >= self.status_thresholds['active_min']:
            return PatternStatus.ACTIVE
        elif effective_confidence >= self.status_thresholds['cooling_min']:
            return PatternStatus.COOLING
        else:
            return PatternStatus.DORMANT
    
    def apply_decay(
        self,
        pattern_id: str,
        base_confidence: float,
        last_seen_timestamp: datetime,
        current_timestamp: Optional[datetime] = None
    ) -> Dict:
        """
        Apply complete decay logic to a pattern
        
        Args:
            pattern_id: Pattern identifier
            base_confidence: Original correlation confidence
            last_seen_timestamp: Last observation time
            current_timestamp: Current evaluation time
            
        Returns:
            Dictionary with decay analysis:
            {
                'pattern_id': str,
                'base_confidence': float,
                'decay_score': float,
                'effective_confidence': float,
                'status': PatternStatus,
                'last_seen_timestamp': datetime,
                'time_since_last_seen_seconds': float
            }
        """
        if current_timestamp is None:
            current_timestamp = datetime.utcnow()
        
        # Calculate decay components
        decay_score = self.calculate_decay_score(last_seen_timestamp, current_timestamp)
        effective_confidence = self.calculate_effective_confidence(base_confidence, decay_score)
        status = self.determine_pattern_status(effective_confidence)
        
        time_since_last_seen = (current_timestamp - last_seen_timestamp).total_seconds()
        
        result = {
            'pattern_id': pattern_id,
            'base_confidence': round(base_confidence, 4),
            'decay_score': decay_score,
            'effective_confidence': effective_confidence,
            'status': status.value,
            'last_seen_timestamp': last_seen_timestamp,
            'current_timestamp': current_timestamp,
            'time_since_last_seen_seconds': round(time_since_last_seen, 2)
        }
        
        logger.debug(f"Applied decay to {pattern_id}: "
                    f"base={base_confidence:.2f}, decay={decay_score:.2f}, "
                    f"effective={effective_confidence:.2f}, status={status.value}")
        
        return result
    
    def reactivate_pattern(
        self,
        pattern_id: str,
        new_base_confidence: float,
        current_timestamp: Optional[datetime] = None
    ) -> Dict:
        """
        Reactivate a pattern upon reappearance
        
        REACTIVATION RULE:
        - last_seen_timestamp → reset to current time
        - decay_score → reset to 1.0 (full strength)
        - base_confidence → recomputed from new correlation
        - status → recalculated
        
        This creates spike → decay → spike behavior
        
        Args:
            pattern_id: Pattern being reactivated
            new_base_confidence: New correlation confidence
            current_timestamp: Reactivation time
            
        Returns:
            Dictionary with reactivated pattern state
        """
        if current_timestamp is None:
            current_timestamp = datetime.utcnow()
        
        # Full reset on reactivation
        decay_score = 1.0
        effective_confidence = self.calculate_effective_confidence(new_base_confidence, decay_score)
        status = self.determine_pattern_status(effective_confidence)
        
        result = {
            'pattern_id': pattern_id,
            'base_confidence': round(new_base_confidence, 4),
            'decay_score': decay_score,
            'effective_confidence': effective_confidence,
            'status': status.value,
            'last_seen_timestamp': current_timestamp,
            'current_timestamp': current_timestamp,
            'time_since_last_seen_seconds': 0.0,
            'reactivated': True
        }
        
        logger.info(f"Reactivated pattern {pattern_id}: "
                   f"new_confidence={new_base_confidence:.2f}, status={status.value}")
        
        return result
    
    def generate_decay_explanation(
        self,
        pattern_id: str,
        decay_result: Dict
    ) -> str:
        """
        Generate human-readable explanation of decay impact
        
        Required for audit and explainability
        
        Args:
            pattern_id: Pattern identifier
            decay_result: Result from apply_decay()
            
        Returns:
            Human-readable explanation
        """
        base_conf = decay_result['base_confidence']
        decay_score = decay_result['decay_score']
        effective_conf = decay_result['effective_confidence']
        status = decay_result['status']
        time_delta = decay_result['time_since_last_seen_seconds']
        
        # Format time nicely
        if time_delta < 60:
            time_str = f"{int(time_delta)} seconds"
        elif time_delta < 3600:
            time_str = f"{int(time_delta / 60)} minutes"
        else:
            time_str = f"{time_delta / 3600:.1f} hours"
        
        # Status-specific messages
        if status == PatternStatus.ACTIVE.value:
            explanation = (
                f"Pattern {pattern_id} is ACTIVE with full influence. "
                f"Last observed {time_str} ago. "
                f"Effective confidence: {effective_conf:.2f} (from base {base_conf:.2f})."
            )
        elif status == PatternStatus.COOLING.value:
            influence_reduction = int((1.0 - decay_score) * 100)
            explanation = (
                f"Pattern {pattern_id} previously showed coordinated behavior, "
                f"but its influence was reduced by {influence_reduction}% due to inactivity over the last {time_str}. "
                f"Effective confidence: {effective_conf:.2f} (from base {base_conf:.2f}, decay {decay_score:.2f})."
            )
        else:  # DORMANT
            explanation = (
                f"Pattern {pattern_id} is DORMANT. "
                f"Last observed {time_str} ago. "
                f"Minimal influence remaining: {effective_conf:.2f} (from base {base_conf:.2f}). "
                f"Will reactivate immediately if pattern reappears."
            )
        
        return explanation
    
    def get_config(self) -> Dict:
        """Get current decay engine configuration"""
        return {
            'decay_windows': self.decay_windows,
            'status_thresholds': self.status_thresholds
        }
    
    def update_config(self, new_config: Dict):
        """
        Update decay engine configuration
        
        Args:
            new_config: New configuration values
        """
        if 'decay_windows' in new_config:
            self.decay_windows.update(new_config['decay_windows'])
        if 'status_thresholds' in new_config:
            self.status_thresholds.update(new_config['status_thresholds'])
        
        logger.info(f"Updated DecayEngine config: {new_config}")
