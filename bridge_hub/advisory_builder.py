"""
Advisory Builder
Converts intent alerts into actionable advisories for entities
"""
from typing import List, Tuple
from datetime import datetime, timedelta
import logging

from .models import IntentAlert, Advisory

logger = logging.getLogger(__name__)


class AdvisoryBuilder:
    """
    Build actionable advisories from fraud intent alerts
    
    DESIGN PRINCIPLE:
    Alerts are internal.
    Advisories are external.
    Convert threat intelligence into action recommendations.
    """
    
    def __init__(self):
        """Initialize advisory builder"""
        logger.info("Initialized AdvisoryBuilder")
    
    def build_advisory(self, alert: IntentAlert) -> Advisory:
        """
        Build advisory from intent alert with decay information
        
        Args:
            alert: IntentAlert with decay fields to convert
            
        Returns:
            Advisory with recommendations and decay transparency
        """
        # Generate recommended actions based on severity (derived from confidence)
        severity = self._confidence_to_severity(alert.confidence)
        actions = self._generate_actions(severity, alert.pattern_status)
        
        # Build advisory message with decay awareness
        message = self._build_message(alert, severity)
        
        # Generate decay explanation for transparency
        decay_explanation = self._build_decay_explanation(alert)
        
        # Create advisory with decay fields
        advisory = Advisory(
            advisory_id=self._generate_id(alert),
            fingerprint=alert.fingerprint,
            severity=severity,
            message=message,
            recommended_actions=actions,
            entity_count=alert.entity_count,
            confidence=alert.confidence,
            fraud_score=alert.fraud_score,
            timestamp=datetime.utcnow(),
            # Decay-related fields for entity decision-making
            base_confidence=alert.base_confidence,
            decay_score=alert.decay_score,
            effective_confidence=alert.effective_confidence,
            last_seen_timestamp=alert.last_seen_timestamp,
            pattern_status=alert.pattern_status,
            time_since_last_seen_seconds=alert.time_since_last_seen_seconds,
            decay_explanation=decay_explanation
        )
        
        logger.info(
            f"Built advisory {advisory.advisory_id}: "
            f"{alert.confidence} - {len(actions)} actions - "
            f"status={alert.pattern_status}, eff_conf={alert.effective_confidence:.3f}"
        )
        
        return advisory
    
    def _confidence_to_severity(self, confidence: str) -> str:
        """
        Map confidence level to severity level
        
        Args:
            confidence: Confidence level (HIGH, MEDIUM, LOW)
            
        Returns:
            Severity level (CRITICAL, HIGH, MEDIUM)
        """
        mapping = {
            "HIGH": "CRITICAL",
            "MEDIUM": "HIGH", 
            "LOW": "MEDIUM"
        }
        return mapping.get(confidence, "MEDIUM")
    
    def _extract_timestamps(self, alert: IntentAlert) -> Tuple[datetime, datetime]:
        """
        Extract first_seen and last_seen timestamps from alert
        
        Args:
            alert: IntentAlert containing time span information
            
        Returns:
            Tuple of (first_seen, last_seen) datetimes
        """
        # Use alert timestamp as last_seen, calculate first_seen from time_span_seconds
        last_seen = alert.timestamp
        first_seen = last_seen - timedelta(seconds=alert.time_span_seconds)
        
        return first_seen, last_seen
    
    def _generate_actions(self, severity: str, pattern_status: str = "ACTIVE") -> List[str]:
        """
        Generate recommended actions based on severity and pattern lifecycle status
        
        Args:
            severity: Alert severity (CRITICAL, HIGH, MEDIUM)
            pattern_status: Pattern lifecycle status (ACTIVE, COOLING, DORMANT)
            
        Returns:
            List of recommended actions with decay-aware guidance
        """
        actions = []
        
        # Add pattern status context to actions
        status_prefix = ""
        if pattern_status == "COOLING":
            status_prefix = "[COOLING PATTERN] "
        elif pattern_status == "DORMANT":
            status_prefix = "[DORMANT PATTERN] "
        
        if severity == "CRITICAL":
            actions = [
                f"{status_prefix}IMMEDIATE: Flag all matching transactions for manual review",
                "IMMEDIATE: Implement temporary transaction limits on affected accounts",
                "URGENT: Notify fraud investigation team for coordinated response",
                "URGENT: Check for additional correlated patterns in recent history",
                "RECOMMENDED: Share findings with peer institutions via secure channel",
                "RECOMMENDED: Review and update fraud detection rules based on pattern"
            ]
        elif severity == "HIGH":
            actions = [
                f"{status_prefix}URGENT: Flag matching transactions for priority review",
                "URGENT: Monitor affected accounts for additional suspicious activity",
                "RECOMMENDED: Notify fraud team for investigation",
                "RECOMMENDED: Check transaction history for similar patterns",
                "OPTIONAL: Consider enhanced authentication for affected accounts"
            ]
        elif severity == "MEDIUM":
            actions = [
                f"{status_prefix}RECOMMENDED: Add matching transactions to review queue",
                "RECOMMENDED: Monitor accounts for pattern recurrence",
                "OPTIONAL: Alert fraud analysts for manual inspection",
                "OPTIONAL: Document pattern for future rule refinement"
            ]
        else:
            actions = ["INFORMATIONAL: Pattern noted, no immediate action required"]
        
        # Add decay-specific guidance
        if pattern_status == "DORMANT":
            actions.append("NOTE: This is a dormant pattern - verify if still actively occurring")
        elif pattern_status == "COOLING":
            actions.append("NOTE: Pattern cooling down - last observed several minutes ago")
        
        return actions
    
    def _build_message(self, alert: IntentAlert, severity: str) -> str:
        """
        Build advisory message with decay transparency
        
        Args:
            alert: IntentAlert with decay fields to describe
            severity: Mapped severity level
            
        Returns:
            Human-readable message with pattern lifecycle information
        """
        # Shorten fingerprint for readability
        fp_short = alert.fingerprint[:12] + "..."
        
        # Format decay information
        minutes_since_last_seen = alert.time_since_last_seen_seconds / 60.0
        
        message = (
            f"SYNAPSE-FI Fraud Advisory\n\n"
            f"Severity: {severity}\n"
            f"Fraud Score: {alert.fraud_score}/100\n"
            f"Confidence: {alert.confidence}\n"
            f"Pattern Status: {alert.pattern_status}\n"
            f"Effective Confidence: {alert.effective_confidence:.2%}\n"
            f"Last Seen: {minutes_since_last_seen:.1f} minutes ago\n\n"
            f"A coordinated fraud pattern has been detected across {alert.entity_count} "
            f"financial institutions within a {alert.time_span_seconds:.0f}s window. "
            f"This behavioral signature (Pattern ID: {fp_short}) suggests an organized "
            f"fraud operation.\n\n"
            f"PATTERN CHARACTERISTICS:\n"
            f"- Multi-entity coordination detected\n"
            f"- Rapid succession execution\n"
            f"- Behavioral anomaly correlation confirmed\n"
            f"- Pattern lifecycle: {alert.pattern_status} (decay factor: {alert.decay_score:.2f})\n\n"
            f"DECAY ANALYSIS:\n"
            f"{alert.decay_explanation}\n\n"
            f"PRIVACY NOTE: This advisory is based on behavioral fingerprints only. "
            f"No customer PII or transaction data has been shared between institutions.\n\n"
            f"Timestamp: {alert.timestamp.isoformat()}Z"
        )
        
        return message
    
    def _generate_id(self, alert: IntentAlert) -> str:
        """
        Generate unique advisory ID
        
        Format: ADV-YYYYMMDD-HHMMSS-FINGERPRINT[:8]
        
        Args:
            alert: IntentAlert to generate ID for
            
        Returns:
            Advisory ID string
        """
        timestamp = alert.timestamp.strftime("%Y%m%d-%H%M%S")
        fingerprint_short = alert.fingerprint[:8]
        return f"ADV-{timestamp}-{fingerprint_short}"
    
    def build_all_clear_advisory(self, fingerprint: str) -> Advisory:
        """
        Build advisory indicating pattern has resolved
        
        Args:
            fingerprint: Pattern fingerprint
            
        Returns:
            All-clear advisory
        """
        advisory = Advisory(
            advisory_id=f"ADV-CLEAR-{fingerprint[:8]}",
            fingerprint=fingerprint,
            severity="INFO",
            message=(
                f"SYNAPSE-FI Pattern Update\n\n"
                f"The previously flagged pattern (ID: {fingerprint[:12]}...) "
                f"has not shown coordinated activity across entities in recent monitoring. "
                f"Standard fraud detection protocols can resume.\n\n"
                f"This does not indicate the pattern is safe - only that multi-entity "
                f"coordination has ceased. Continue monitoring individual transactions."
            ),
            recommended_actions=[
                "INFORMATIONAL: Pattern no longer shows cross-entity correlation",
                "RECOMMENDED: Continue standard fraud monitoring",
                "OPTIONAL: Review outcome of previous advisory actions"
            ],
            entity_count=0,
            confidence="INFO",
            fraud_score=0,
            timestamp=datetime.utcnow()
        )
        
        logger.info(f"Built all-clear advisory for {fingerprint}")
        
        return advisory
    
    def _build_decay_explanation(self, alert: IntentAlert) -> str:
        """
        Build human-readable decay explanation for advisory transparency
        
        Args:
            alert: IntentAlert with decay fields
            
        Returns:
            Explanation text for decay reasoning
        """
        minutes_since = alert.time_since_last_seen_seconds / 60.0
        
        if alert.pattern_status == "ACTIVE":
            return (
                f"Pattern is ACTIVE (last seen {minutes_since:.1f} min ago). "
                f"Base confidence {alert.base_confidence:.2%} remains high with minimal decay "
                f"(decay factor {alert.decay_score:.2f}). This is a fresh, actively occurring pattern "
                f"requiring immediate attention."
            )
        elif alert.pattern_status == "COOLING":
            return (
                f"Pattern is COOLING (last seen {minutes_since:.1f} min ago). "
                f"Base confidence {alert.base_confidence:.2%} has been reduced to "
                f"{alert.effective_confidence:.2%} due to time decay (factor {alert.decay_score:.2f}). "
                f"Pattern may be slowing down but still warrants monitoring."
            )
        else:  # DORMANT
            return (
                f"Pattern is DORMANT (last seen {minutes_since:.1f} min ago). "
                f"Base confidence {alert.base_confidence:.2%} has significantly decayed to "
                f"{alert.effective_confidence:.2%} (factor {alert.decay_score:.2f}). "
                f"This is a stale pattern - verify if still actively occurring before taking action."
            )
