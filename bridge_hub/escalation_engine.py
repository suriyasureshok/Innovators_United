"""
Escalation Engine
Evaluates correlations and escalates fraud intent when thresholds met
"""
from typing import List, Optional
from datetime import datetime
import logging

from .models import CorrelationResult, IntentAlert

logger = logging.getLogger(__name__)


class EscalationEngine:
    """
    Escalate correlated patterns to fraud intent alerts
    
    DESIGN PHILOSOPHY:
    Not all correlations are fraud.
    Escalation thresholds prevent false positives.
    Severity levels guide entity response.
    """
    
    # Severity thresholds
    CRITICAL_THRESHOLD = 4  # 4+ entities
    HIGH_THRESHOLD = 3      # 3 entities
    MEDIUM_THRESHOLD = 2    # 2 entities
    
    def __init__(self, config: dict):
        """
        Initialize escalation engine
        
        Args:
            config: Configuration dictionary with:
                - critical_threshold: Entities for CRITICAL (default 4)
                - high_threshold: Entities for HIGH (default 3)
                - medium_threshold: Entities for MEDIUM (default 2)
        """
        self.critical_threshold = config.get('critical_threshold', self.CRITICAL_THRESHOLD)
        self.high_threshold = config.get('high_threshold', self.HIGH_THRESHOLD)
        self.medium_threshold = config.get('medium_threshold', self.MEDIUM_THRESHOLD)
        
        logger.info(
            f"Initialized EscalationEngine: "
            f"CRITICAL={self.critical_threshold}, "
            f"HIGH={self.high_threshold}, "
            f"MEDIUM={self.medium_threshold}"
        )
    
    def evaluate(self, correlation: CorrelationResult) -> Optional[IntentAlert]:
        """
        Evaluate correlation and escalate if thresholds met (uses effective_confidence with decay)
        
        Args:
            correlation: CorrelationResult from temporal correlator (includes decay fields)
            
        Returns:
            IntentAlert with decay information if escalation warranted, None otherwise
        """
        # Determine severity based on entity count
        severity = self._calculate_severity(correlation.entity_count)
        
        if severity is None:
            logger.debug(
                f"No escalation for {correlation.fingerprint}: "
                f"{correlation.entity_count} entities below threshold"
            )
            return None
        
        # Calculate fraud score using effective_confidence (decayed)
        fraud_score = self._calculate_fraud_score(correlation)
        
        # Build description with decay awareness
        description = self._build_description(correlation, severity)
        
        # Create intent alert with decay fields
        alert = IntentAlert(
            alert_id=self._generate_alert_id(correlation),
            intent_type="COORDINATED_FRAUD",
            fingerprint=correlation.fingerprint,
            severity=severity,
            confidence=correlation.confidence,
            entity_count=correlation.entity_count,
            time_span_seconds=correlation.time_span_seconds,
            description=description,
            rationale=self._build_rationale(correlation, severity, fraud_score),
            recommendation=self._get_recommendation(severity),
            fraud_score=fraud_score,
            timestamp=datetime.utcnow(),
            # Decay-related fields
            base_confidence=correlation.base_confidence,
            decay_score=correlation.decay_score,
            effective_confidence=correlation.effective_confidence,
            last_seen_timestamp=correlation.last_seen_timestamp,
            pattern_status=correlation.pattern_status,
            time_since_last_seen_seconds=(datetime.utcnow() - correlation.last_seen_timestamp).total_seconds(),
            decay_explanation=f"Pattern lifecycle: {correlation.pattern_status}, decay={correlation.decay_score:.2f}"
        )
        
        logger.warning(
            f"🚨 FRAUD INTENT ESCALATED: {severity} - {correlation.fingerprint} "
            f"(score={fraud_score}, entities={correlation.entity_count}, "
            f"eff_conf={correlation.effective_confidence:.3f}, status={correlation.pattern_status})"
        )
        
        return alert
    
    def _calculate_severity(self, entity_count: int) -> Optional[str]:
        """
        Calculate severity level based on entity count
        
        Args:
            entity_count: Number of entities showing pattern
            
        Returns:
            Severity string (CRITICAL, HIGH, MEDIUM) or None
        """
        if entity_count >= self.critical_threshold:
            return "CRITICAL"
        elif entity_count >= self.high_threshold:
            return "HIGH"
        elif entity_count >= self.medium_threshold:
            return "MEDIUM"
        else:
            return None
    
    def _calculate_fraud_score(self, correlation: CorrelationResult) -> int:
        """
        Calculate fraud score (0-100) using effective_confidence with decay
        
        Scoring logic:
        - Base score: entity_count * 20 (capped at 60)
        - Effective confidence bonus: effective_confidence * 30 (0-30 points)
        - Time span penalty: -10 if time_span > 10 minutes
        
        NOTE: Uses effective_confidence (decayed) instead of base_confidence
        to ensure stale patterns have lower impact on fraud scores.
        
        Args:
            correlation: CorrelationResult with decay fields
            
        Returns:
            Fraud score (0-100)
        """
        # Base score from entity count (capped at 60 to leave room for confidence)
        score = min(correlation.entity_count * 20, 60)
        
        # Effective confidence bonus (0-30 points based on decayed confidence)
        score += int(correlation.effective_confidence * 30)
        
        # Time span penalty (quick succession = higher risk)
        if correlation.time_span_seconds > 600:  # 10 minutes
            score -= 10
        
        # Clamp to 0-100
        return max(0, min(100, score))
    
    def _build_description(
        self,
        correlation: CorrelationResult,
        severity: str
    ) -> str:
        """
        Build human-readable alert description
        
        Args:
            correlation: CorrelationResult to describe
            severity: Severity level
            
        Returns:
            Descriptive alert message
        """
        return (
            f"{severity} fraud intent detected: Pattern {correlation.fingerprint[:8]}... "
            f"observed across {correlation.entity_count} entities "
            f"within {correlation.time_span_seconds:.0f}s. "
            f"Confidence: {correlation.confidence}. "
            f"Recommend immediate investigation and potential coordinated response."
        )
    
    def _generate_alert_id(self, correlation: CorrelationResult) -> str:
        """Generate unique alert ID"""
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        return f"ALT-{timestamp}-{correlation.fingerprint[:8]}"
    
    def _build_rationale(
        self,
        correlation: CorrelationResult,
        severity: str,
        fraud_score: int
    ) -> str:
        """Build rationale for the alert"""
        return (
            f"Pattern {correlation.fingerprint[:12]}... observed across "
            f"{correlation.entity_count} entities within {correlation.time_span_seconds:.0f}s. "
            f"Fraud score: {fraud_score}/100. Severity: {severity}. "
            f"Confidence: {correlation.confidence}."
        )
    
    def _get_recommendation(self, severity: str) -> str:
        """Get recommendation based on severity"""
        recommendations = {
            "CRITICAL": "IMMEDIATE_ESCALATION",
            "HIGH": "URGENT_REVIEW",
            "MEDIUM": "PRIORITY_REVIEW"
        }
        return recommendations.get(severity, "MONITOR")
    
    def update_config(self, config: dict) -> None:
        """Update escalation thresholds"""
        if 'critical_threshold' in config:
            self.critical_threshold = config['critical_threshold']
            logger.info(f"Updated critical_threshold to {self.critical_threshold}")
        
        if 'high_threshold' in config:
            self.high_threshold = config['high_threshold']
            logger.info(f"Updated high_threshold to {self.high_threshold}")
        
        if 'medium_threshold' in config:
            self.medium_threshold = config['medium_threshold']
            logger.info(f"Updated medium_threshold to {self.medium_threshold}")
