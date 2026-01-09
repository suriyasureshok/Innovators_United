"""
Decision Engine and Explanation Generator
Makes final transaction decisions and generates audit-ready explanations
"""
from typing import Optional, Dict
from datetime import datetime
import logging

from .models import DecisionAction, Decision, RiskScore
from bridge_hub.models import Advisory

logger = logging.getLogger(__name__)


class DecisionEngine:
    """
    Make final transaction decisions based on local risk and BRIDGE advisories
    
    CRITICAL: Entity maintains sovereignty - can override Hub advisories
    """
    
    def __init__(self, config: Dict = None):
        """
        Initialize decision engine
        
        Args:
            config: Configuration with thresholds and advisory influence
        """
        self.config = config or {}
        
        # Decision thresholds (based on adjusted score)
        self.thresholds = self.config.get('thresholds', {
            'allow_max': 40,        # Score <= 40: Allow
            'step_up_max': 70,      # Score 40-70: Step up auth
            'block_min': 70         # Score > 70: Block
        })
        
        # Advisory influence settings
        self.advisory_influence = self.config.get('advisory_influence', {
            'enabled': True,
            'multipliers': {
                'HIGH': 1.5,     # Increase score by 50% for HIGH confidence
                'MEDIUM': 1.3,   # Increase score by 30% for MEDIUM confidence
                'LOW': 1.1       # Increase score by 10% for LOW confidence
            },
            'max_adjustment': 2.0  # Don't more than double the score
        })
        
        logger.info(f"Initialized DecisionEngine with thresholds: {self.thresholds}")
    
    def make_decision(
        self,
        transaction_id: str,
        risk_score: RiskScore,
        advisory: Optional[Advisory] = None
    ) -> Decision:
        """
        Make final transaction decision using effective_confidence from advisory (with decay)
        
        Args:
            transaction_id: Transaction identifier
            risk_score: Local risk assessment
            advisory: Optional BRIDGE Hub advisory with decay information
            
        Returns:
            Decision object with action and explanation
        """
        # Start with local risk score
        adjusted_score = risk_score.score
        adjustment_factors = []
        advisory_applied = False
        
        # Apply BRIDGE advisory if present and enabled (uses effective_confidence with decay)
        if advisory and self.advisory_influence.get('enabled', True):
            # Use effective_confidence (decayed) instead of raw confidence
            # This ensures stale patterns have less influence on decisions
            eff_conf = getattr(advisory, 'effective_confidence', 0.0)
            pattern_status = getattr(advisory, 'pattern_status', 'UNKNOWN')
            
            # Convert effective_confidence (0.0-1.0) to multiplier
            # Scale: 0.0 → 1.0x (no change), 1.0 → 2.0x (double impact)
            multiplier = 1.0 + eff_conf  # Range: 1.0 to 2.0
            
            old_score = adjusted_score
            adjusted_score = min(
                adjusted_score * multiplier,
                old_score * self.advisory_influence.get('max_adjustment', 2.0)
            )
            
            # Clamp to valid range (0-100)
            adjusted_score = max(0.0, min(100.0, adjusted_score))
            
            adjustment_factors.append(
                f"BRIDGE advisory (effective_confidence: {eff_conf:.3f}, "
                f"pattern_status: {pattern_status}, "
                f"entities: {advisory.entity_count}, "
                f"fraud_score: {advisory.fraud_score})"
            )
            adjustment_factors.append(
                f"Score adjusted: {old_score:.1f} → {adjusted_score:.1f} "
                f"(multiplier: {multiplier:.3f}x based on decayed confidence)"
            )
            
            # Add decay-specific explanation
            if hasattr(advisory, 'decay_explanation'):
                adjustment_factors.append(f"Decay context: {advisory.decay_explanation}")
            
            advisory_applied = True
            
            logger.info(f"Applied BRIDGE advisory to {transaction_id}: "
                       f"{old_score:.1f} → {adjusted_score:.1f} "
                       f"(eff_conf={eff_conf:.3f}, status={pattern_status})")
        
        # Make decision based on adjusted score
        if adjusted_score <= self.thresholds['allow_max']:
            action = DecisionAction.ALLOW
        elif adjusted_score <= self.thresholds['step_up_max']:
            action = DecisionAction.STEP_UP
        else:
            action = DecisionAction.BLOCK
        
        logger.info(f"Decision for {transaction_id}: {action.value} "
                   f"(score: {risk_score.score:.1f}, adjusted: {adjusted_score:.1f})")
        
        return Decision(
            transaction_id=transaction_id,
            action=action,
            risk_score=risk_score.score,
            adjusted_score=round(adjusted_score, 2),
            adjustment_factors=adjustment_factors,
            advisory_applied=advisory_applied,
            timestamp=datetime.utcnow()
        )
    
    def _get_advisory_multiplier(self, confidence: str) -> float:
        """
        Get score multiplier based on BRIDGE advisory confidence
        
        Args:
            confidence: Advisory confidence level (HIGH/MEDIUM/LOW)
            
        Returns:
            Multiplier value
        """
        multipliers = self.advisory_influence.get('multipliers', {})
        return multipliers.get(confidence.upper(), 1.0)
    
    def can_override_advisory(self, decision: Decision) -> bool:
        """
        Check if entity can override the advisory influence
        
        Args:
            decision: Decision to check
            
        Returns:
            True if override is allowed
        """
        # Entity ALWAYS retains sovereignty to override
        return True
    
    def update_config(self, new_config: Dict):
        """Update decision engine configuration"""
        if 'thresholds' in new_config:
            self.thresholds.update(new_config['thresholds'])
        if 'advisory_influence' in new_config:
            self.advisory_influence.update(new_config['advisory_influence'])
        
        logger.info(f"Updated DecisionEngine config: {new_config}")


class ExplanationGenerator:
    """Generate human-readable, audit-ready decision explanations"""
    
    def __init__(self):
        """Initialize explanation generator"""
        logger.info("Initialized ExplanationGenerator")
    
    def generate_explanation(
        self,
        transaction_id: str,
        risk_score: RiskScore,
        decision: Decision,
        advisory: Optional[Advisory] = None,
        pattern_description: Optional[str] = None
    ) -> str:
        """
        Create comprehensive audit-ready explanation
        
        Args:
            transaction_id: Transaction identifier
            risk_score: Risk assessment
            decision: Final decision
            advisory: Optional BRIDGE advisory
            pattern_description: Optional pattern description
            
        Returns:
            Human-readable explanation string
        """
        lines = []
        
        # Header
        lines.append("=" * 70)
        lines.append("FRAUD PREVENTION DECISION REPORT")
        lines.append("=" * 70)
        lines.append(f"Transaction ID: {transaction_id}")
        lines.append(f"Decision: {decision.action.value.upper()}")
        lines.append(f"Timestamp: {decision.timestamp.isoformat()}")
        lines.append("")
        
        # Local Risk Analysis
        lines.append("LOCAL RISK ANALYSIS:")
        lines.append("-" * 70)
        lines.append(f"Risk Score: {risk_score.score:.1f}/100")
        
        if risk_score.signals:
            lines.append(f"Triggered Signals ({len(risk_score.signals)}):")
            for signal in sorted(risk_score.signals):
                lines.append(f"  • {signal}")
        else:
            lines.append("Triggered Signals: None")
        
        if risk_score.pattern:
            lines.append(f"\nDetected Pattern: {risk_score.pattern}")
            if pattern_description:
                lines.append(f"Pattern Description: {pattern_description}")
        lines.append("")
        
        # BRIDGE Advisory (if present)
        if advisory:
            lines.append("BRIDGE HUB COLLECTIVE INTELLIGENCE:")
            lines.append("-" * 70)
            lines.append(f"Advisory ID: {advisory.advisory_id}")
            lines.append(f"Confidence: {advisory.confidence}")
            lines.append(f"Fraud Score: {advisory.fraud_score}/100")
            lines.append(f"Coordinated Entities: {advisory.entity_count}")
            lines.append(f"Severity: {advisory.severity}")
            lines.append("")
            lines.append("Advisory Message:")
            lines.append(advisory.message)
            lines.append("")
            
            if advisory.recommended_actions:
                lines.append("Recommended Actions:")
                for action in advisory.recommended_actions:
                    lines.append(f"  • {action}")
            lines.append("")
        
        # Score Adjustment
        if decision.adjustment_factors:
            lines.append("SCORE ADJUSTMENTS:")
            lines.append("-" * 70)
            for factor in decision.adjustment_factors:
                lines.append(f"  • {factor}")
            lines.append(f"\nFinal Adjusted Score: {decision.adjusted_score:.1f}/100")
            lines.append("")
        
        # Final Decision Rationale
        lines.append("DECISION RATIONALE:")
        lines.append("-" * 70)
        
        if decision.action == DecisionAction.BLOCK:
            lines.append("❌ TRANSACTION BLOCKED")
            lines.append("Reason: High fraud risk detected. Transaction blocked for fraud prevention.")
            lines.append("Action: Transaction denied. Customer may be contacted for verification.")
        
        elif decision.action == DecisionAction.STEP_UP:
            lines.append("⚠️  ADDITIONAL AUTHENTICATION REQUIRED")
            lines.append("Reason: Moderate fraud risk detected. Additional verification needed.")
            lines.append("Action: Request step-up authentication (SMS OTP, biometric, etc.)")
        
        else:  # ALLOW
            lines.append("✅ TRANSACTION APPROVED")
            lines.append("Reason: Low fraud risk. Transaction approved for processing.")
            lines.append("Action: Proceed with transaction normally.")
        
        lines.append("")
        lines.append("=" * 70)
        lines.append("PRIVACY NOTE: This decision is based on behavioral patterns only.")
        lines.append("No customer PII was shared with other institutions.")
        lines.append("=" * 70)
        
        explanation = "\n".join(lines)
        
        logger.debug(f"Generated explanation for {transaction_id} ({len(lines)} lines)")
        
        return explanation
    
    def generate_short_explanation(
        self,
        decision: Decision,
        risk_score: RiskScore
    ) -> str:
        """
        Generate brief explanation for logs/UI
        
        Args:
            decision: Decision object
            risk_score: Risk assessment
            
        Returns:
            Short explanation string
        """
        if decision.action == DecisionAction.BLOCK:
            return f"Blocked: High risk ({decision.adjusted_score:.0f}/100). Signals: {', '.join(risk_score.signals[:3])}"
        elif decision.action == DecisionAction.STEP_UP:
            return f"Step-up auth required: Moderate risk ({decision.adjusted_score:.0f}/100)"
        else:
            return f"Approved: Low risk ({decision.adjusted_score:.0f}/100)"
