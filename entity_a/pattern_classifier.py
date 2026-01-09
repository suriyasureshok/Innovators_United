"""
Pattern Classification
Map risk signals to behavioral fraud patterns
"""
import logging
from typing import Set, Union, List

from .models import BehaviorPattern, RiskScore

logger = logging.getLogger(__name__)


class PatternClassifier:
    """Classify transactions into behavior patterns based on risk signals"""
    
    def __init__(self):
        """Initialize pattern classifier"""
        logger.info("Initialized PatternClassifier")
    
    def classify(self, risk_score: Union[RiskScore, List[str]]) -> BehaviorPattern:
        """
        Map risk signals to specific behavior pattern
        
        Args:
            risk_score: RiskScore object with signals or list of signal strings
            
        Returns:
            Classified behavior pattern
        """
        # Handle both RiskScore object and list of signals
        if isinstance(risk_score, RiskScore):
            signals = set(risk_score.signals)
        else:
            signals = set(risk_score)
        
        # Priority-based pattern matching (most specific first)
        
        # Account Takeover: High velocity + New device + Location shift
        if self._matches_account_takeover(signals):
            logger.debug(f"Classified as ACCOUNT_TAKEOVER: {signals}")
            return BehaviorPattern.ACCOUNT_TAKEOVER
        
        # Card Testing: Many small transactions quickly
        if self._matches_card_testing(signals):
            logger.debug(f"Classified as CARD_TESTING: {signals}")
            return BehaviorPattern.CARD_TESTING
        
        # Velocity Abuse: Extreme velocity
        if self._matches_velocity_abuse(signals):
            logger.debug(f"Classified as VELOCITY_ABUSE: {signals}")
            return BehaviorPattern.VELOCITY_ABUSE
        
        # Suspicious Timing: Night transactions + High value
        if self._matches_suspicious_timing(signals):
            logger.debug(f"Classified as SUSPICIOUS_TIMING: {signals}")
            return BehaviorPattern.SUSPICIOUS_TIMING
        
        # High Value Anomaly: Unusual high amounts
        if self._matches_high_value_anomaly(signals):
            logger.debug(f"Classified as HIGH_VALUE_ANOMALY: {signals}")
            return BehaviorPattern.HIGH_VALUE_ANOMALY
        
        # Default: Normal transaction
        logger.debug(f"Classified as NORMAL: {signals}")
        return BehaviorPattern.NORMAL
    
    def _matches_account_takeover(self, signals: Set[str]) -> bool:
        """
        Check if signals indicate account takeover
        
        Characteristics:
        - High velocity (attacker trying multiple transactions)
        - New/unknown device (attacker's device)
        - Location shift (attacker in different location)
        """
        required_signals = {
            'HIGH_VELOCITY',
            'VERY_HIGH_VELOCITY',
            'NEW_DEVICE',
            'UNKNOWN_DEVICE',
            'LOCATION_SHIFT'
        }
        
        # Need velocity + device + location indicators
        has_velocity = any(s in signals for s in ['HIGH_VELOCITY', 'VERY_HIGH_VELOCITY', 'MODERATE_VELOCITY'])
        has_device = any(s in signals for s in ['NEW_DEVICE', 'UNKNOWN_DEVICE'])
        has_location = 'LOCATION_SHIFT' in signals
        
        return has_velocity and has_device and has_location
    
    def _matches_card_testing(self, signals: Set[str]) -> bool:
        """
        Check if signals indicate card testing
        
        Characteristics:
        - Low amounts (testing card validity)
        - High velocity (many test transactions)
        """
        return 'LOW_AMOUNT_HIGH_VELOCITY' in signals or \
               ('HIGH_VELOCITY' in signals and 'is_low_amount' in signals)
    
    def _matches_velocity_abuse(self, signals: Set[str]) -> bool:
        """
        Check if signals indicate velocity abuse
        
        Characteristics:
        - Very high transaction velocity
        - High amount velocity
        """
        return 'VERY_HIGH_VELOCITY' in signals or 'HIGH_AMOUNT_VELOCITY' in signals
    
    def _matches_suspicious_timing(self, signals: Set[str]) -> bool:
        """
        Check if signals indicate suspicious timing pattern
        
        Characteristics:
        - Night transactions
        - High value during suspicious times
        - Weekend + high value
        """
        has_timing = 'NIGHT_TRANSACTION' in signals or 'WEEKEND_HIGH_VALUE' in signals
        has_value = 'HIGH_VALUE' in signals or 'VERY_HIGH_VALUE' in signals
        
        return has_timing and has_value
    
    def _matches_high_value_anomaly(self, signals: Set[str]) -> bool:
        """
        Check if signals indicate high value anomaly
        
        Characteristics:
        - Amount deviation from normal
        - High/very high value
        - Suspicious merchant or IP
        """
        has_deviation = 'AMOUNT_DEVIATION' in signals
        has_high_value = 'HIGH_VALUE' in signals or 'VERY_HIGH_VALUE' in signals
        has_suspicious = any(s in signals for s in ['SUSPICIOUS_MERCHANT', 'SUSPICIOUS_IP', 'HIGH_RISK_CATEGORY'])
        
        return (has_deviation and has_high_value) or (has_high_value and has_suspicious)
    
    def get_pattern_description(self, pattern: BehaviorPattern) -> str:
        """
        Get human-readable description of pattern
        
        Args:
            pattern: Behavior pattern
            
        Returns:
            Description string
        """
        descriptions = {
            BehaviorPattern.ACCOUNT_TAKEOVER: 
                "Account Takeover: Unusual device, location, and transaction velocity suggest compromised account",
            BehaviorPattern.CARD_TESTING: 
                "Card Testing: Multiple small transactions indicate potential stolen card validation",
            BehaviorPattern.VELOCITY_ABUSE: 
                "Velocity Abuse: Extremely high transaction frequency detected",
            BehaviorPattern.SUSPICIOUS_TIMING: 
                "Suspicious Timing: High-value transactions during unusual hours",
            BehaviorPattern.HIGH_VALUE_ANOMALY: 
                "High Value Anomaly: Transaction amount significantly deviates from normal behavior",
            BehaviorPattern.NORMAL: 
                "Normal: No suspicious patterns detected"
        }
        
        return descriptions.get(pattern, "Unknown pattern")
