"""
Temporal Correlation Engine
Detects coordinated patterns across entities using time-based analysis
"""
from typing import Optional
from datetime import timedelta
import logging

from .models import CorrelationResult
from .brg_graph import BehavioralRiskGraph

logger = logging.getLogger(__name__)


class TemporalCorrelator:
    """
    Detect temporal correlations in behavioral patterns
    
    KEY INSIGHT:
    A pattern appearing once is noise.
    The same pattern appearing across multiple entities
    in a short time window is intelligence.
    """
    
    def __init__(self, config: dict):
        """
        Initialize correlator
        
        Args:
            config: Configuration dictionary with:
                - entity_threshold: Minimum entities for correlation (default 2)
                - time_window_seconds: Time window for correlation (default 300)
        """
        self.entity_threshold = config.get('entity_threshold', 2)
        self.time_window_seconds = config.get('time_window_seconds', 300)
        
        logger.info(
            f"Initialized TemporalCorrelator: "
            f"entity_threshold={self.entity_threshold}, "
            f"time_window={self.time_window_seconds}s"
        )
    
    def detect_correlation(
        self,
        fingerprint: str,
        brg: BehavioralRiskGraph
    ) -> Optional[CorrelationResult]:
        """
        Detect if pattern shows cross-entity correlation
        
        Args:
            fingerprint: Pattern fingerprint to analyze
            brg: Behavioral Risk Graph instance
            
        Returns:
            CorrelationResult if correlation detected, None otherwise
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
        
        # Determine confidence level
        confidence = self._calculate_confidence(entity_count, time_span)
        
        logger.info(
            f"✅ Correlation detected for {fingerprint}: "
            f"{entity_count} entities, {time_span:.1f}s span, "
            f"confidence={confidence}"
        )
        
        return CorrelationResult(
            fingerprint=fingerprint,
            entity_count=entity_count,
            time_span_seconds=time_span,
            confidence=confidence,
            observations=observations
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
