"""
Temporal Correlation Engine
Detects coordinated patterns across entities using time-based analysis with decay support
"""
from typing import Optional
from datetime import datetime, timedelta
import logging

from .models import CorrelationResult
from .brg_graph import BehavioralRiskGraph
from .decay_engine import DecayEngine

logger = logging.getLogger(__name__)


class TemporalCorrelator:
    """
    Detect temporal correlations in behavioral patterns with decay tracking
    
    KEY INSIGHT:
    A pattern appearing once is noise.
    The same pattern appearing across multiple entities
    in a short time window is intelligence.
    
    DECAY INTEGRATION:
    - Calculates decay for each correlated pattern
    - Provides effective_confidence for downstream decisions
    - Tracks pattern lifecycle (ACTIVE, COOLING, DORMANT)
    """
    
    def __init__(self, config: dict, decay_engine: Optional[DecayEngine] = None):
        """
        Initialize correlator with decay support
        
        Args:
            config: Configuration dictionary with:
                - entity_threshold: Minimum entities for correlation (default 2)
                - time_window_seconds: Time window for correlation (default 300)
            decay_engine: Optional DecayEngine instance for pattern decay calculations
        """
        self.entity_threshold = config.get('entity_threshold', 2)
        self.time_window_seconds = config.get('time_window_seconds', 300)
        self.decay_engine = decay_engine or DecayEngine()
        
        logger.info(
            f"Initialized TemporalCorrelator: "
            f"entity_threshold={self.entity_threshold}, "
            f"time_window={self.time_window_seconds}s, "
            f"decay_enabled={decay_engine is not None}"
        )
    
    def detect_correlation(
        self,
        fingerprint: str,
        brg: BehavioralRiskGraph
    ) -> Optional[CorrelationResult]:
        """
        Detect if pattern shows cross-entity correlation with decay calculation
        
        Args:
            fingerprint: Pattern fingerprint to analyze
            brg: Behavioral Risk Graph instance
            
        Returns:
            CorrelationResult with decay information if correlation detected, None otherwise
        """
        # Get recent observations from BRG
        time_window = timedelta(seconds=self.time_window_seconds)
        observations = brg.get_recent_observations(fingerprint, time_window)
        
        if not observations:
            logger.debug(f"No recent observations for {fingerprint}")
            return None
        
        # Count unique entities
        unique_entities = set(obs['entity_id'] for obs in observations)
        entity_count = len(unique_entities)
        
        # Check if threshold met
        if entity_count < self.entity_threshold:
            logger.debug(
                f"Correlation threshold not met for {fingerprint}: "
                f"{entity_count} < {self.entity_threshold} entities"
            )
            return None
        
        # Calculate time span
        if len(observations) > 1:
            time_span = (
                observations[-1]['timestamp'] - observations[0]['timestamp']
            ).total_seconds()
        else:
            time_span = 0.0
        
        # Determine base confidence level
        confidence_str = self._calculate_confidence(entity_count, time_span)
        
        # Convert string confidence to numeric base_confidence
        confidence_map = {"LOW": 0.5, "MEDIUM": 0.75, "HIGH": 0.9}
        base_confidence = confidence_map.get(confidence_str, 0.5)
        
        # Get last seen timestamp
        last_seen = observations[-1]['timestamp'] if observations else datetime.utcnow()
        
        # Apply decay logic
        decay_result = self.decay_engine.apply_decay(
            pattern_id=fingerprint,
            base_confidence=base_confidence,
            last_seen_timestamp=last_seen,
            current_timestamp=datetime.utcnow()
        )
        
        logger.info(
            f"✅ Correlation detected for {fingerprint}: "
            f"{entity_count} entities, {time_span:.1f}s span, "
            f"confidence={confidence_str}, base_conf={base_confidence:.3f}, "
            f"eff_conf={decay_result['effective_confidence']:.3f}, status={decay_result['status']}"
        )
        
        return CorrelationResult(
            fingerprint=fingerprint,
            entity_count=entity_count,
            time_span_seconds=time_span,
            confidence=confidence_str,
            observations=observations,
            base_confidence=base_confidence,
            decay_score=decay_result['decay_score'],
            effective_confidence=decay_result['effective_confidence'],
            last_seen_timestamp=last_seen,
            pattern_status=decay_result['status']
        )
    
    def _calculate_confidence(self, entity_count: int, time_span: float) -> str:
        """
        Calculate correlation confidence level
        
        Logic:
        - More entities + shorter time span = higher confidence
        - HIGH: 3+ entities within 3 minutes
        - MEDIUM: 2+ entities within 5 minutes
        - LOW: Otherwise
        
        Args:
            entity_count: Number of unique entities
            time_span: Time span in seconds
            
        Returns:
            Confidence level string (LOW, MEDIUM, HIGH)
        """
        if entity_count >= 3 and time_span < 180:
            return "HIGH"
        elif entity_count >= 2 and time_span < 300:
            return "MEDIUM"
        else:
            return "LOW"
    
    def update_config(self, config: dict) -> None:
        """Update correlator configuration"""
        if 'entity_threshold' in config:
            self.entity_threshold = config['entity_threshold']
            logger.info(f"Updated entity_threshold to {self.entity_threshold}")
        
        if 'time_window_seconds' in config:
            self.time_window_seconds = config['time_window_seconds']
            logger.info(f"Updated time_window to {self.time_window_seconds}s")
