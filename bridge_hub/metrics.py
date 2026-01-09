"""
Hub Metrics Tracker
Tracks operational metrics for monitoring and performance analysis
"""
from typing import Dict, List, Deque
from datetime import datetime, timedelta
from collections import deque, defaultdict
import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class MetricsSummary:
    """Summary of Hub operational metrics"""
    # Throughput metrics
    fingerprints_ingested: int = 0
    correlations_detected: int = 0
    alerts_escalated: int = 0
    advisories_generated: int = 0
    
    # Performance metrics
    avg_ingestion_latency_ms: float = 0.0
    avg_correlation_latency_ms: float = 0.0
    p95_ingestion_latency_ms: float = 0.0
    p95_correlation_latency_ms: float = 0.0
    
    # Graph metrics
    graph_size_nodes: int = 0
    graph_size_edges: int = 0
    active_patterns: int = 0
    cooling_patterns: int = 0
    dormant_patterns: int = 0
    
    # Entity participation
    active_entities: int = 0
    entities_by_fingerprints: Dict[str, int] = field(default_factory=dict)
    
    # Advisory effectiveness
    advisories_by_severity: Dict[str, int] = field(default_factory=dict)
    avg_fraud_score: float = 0.0
    
    # Time window
    measurement_window_seconds: int = 3600
    timestamp: str = ""


class MetricsTracker:
    """
    Tracks Hub operational metrics for monitoring
    
    Responsibilities:
    - Track ingestion latency
    - Track correlation detection rate
    - Track advisory generation metrics
    - Calculate percentiles (p95, p99)
    - Provide rolling window statistics
    """
    
    def __init__(self, window_size: int = 3600):
        """
        Initialize metrics tracker
        
        Args:
            window_size: Rolling window size in seconds (default 1 hour)
        """
        self.window_size = window_size
        
        # Latency tracking (keep recent samples for percentiles)
        self.ingestion_latencies: Deque[float] = deque(maxlen=10000)
        self.correlation_latencies: Deque[float] = deque(maxlen=10000)
        
        # Counters with timestamps for rolling windows
        self.fingerprints_ingested: Deque[datetime] = deque()
        self.correlations_detected: Deque[datetime] = deque()
        self.alerts_escalated: Deque[datetime] = deque()
        self.advisories_generated: Deque[datetime] = deque()
        
        # Entity participation tracking
        self.entity_fingerprint_counts: Dict[str, int] = defaultdict(int)
        
        # Advisory metrics
        self.advisory_severity_counts: Dict[str, int] = defaultdict(int)
        self.fraud_scores: Deque[float] = deque(maxlen=1000)
        
        # Pattern lifecycle tracking
        self.pattern_status_counts: Dict[str, int] = {
            "ACTIVE": 0,
            "COOLING": 0,
            "DORMANT": 0
        }
        
        logger.info(f"Initialized MetricsTracker (window={window_size}s)")
    
    def record_ingestion(self, entity_id: str, latency_ms: float) -> None:
        """
        Record a fingerprint ingestion event
        
        Args:
            entity_id: Entity that sent the fingerprint
            latency_ms: Processing latency in milliseconds
        """
        now = datetime.utcnow()
        self.fingerprints_ingested.append(now)
        self.ingestion_latencies.append(latency_ms)
        self.entity_fingerprint_counts[entity_id] += 1
        self._prune_old_timestamps()
    
    def record_correlation(self, latency_ms: float, detected: bool = True) -> None:
        """
        Record a correlation detection event
        
        Args:
            latency_ms: Detection latency in milliseconds
            detected: Whether correlation was actually detected
        """
        now = datetime.utcnow()
        self.correlation_latencies.append(latency_ms)
        
        if detected:
            self.correlations_detected.append(now)
        
        self._prune_old_timestamps()
    
    def record_escalation(self) -> None:
        """Record a fraud alert escalation event"""
        self.alerts_escalated.append(datetime.utcnow())
        self._prune_old_timestamps()
    
    def record_advisory(self, severity: str, fraud_score: float) -> None:
        """
        Record an advisory generation event
        
        Args:
            severity: Advisory severity level
            fraud_score: Fraud score (0-100)
        """
        self.advisories_generated.append(datetime.utcnow())
        self.advisory_severity_counts[severity] += 1
        self.fraud_scores.append(fraud_score)
        self._prune_old_timestamps()
    
    def update_pattern_status_counts(self, active: int, cooling: int, dormant: int) -> None:
        """
        Update pattern lifecycle status counts
        
        Args:
            active: Number of ACTIVE patterns
            cooling: Number of COOLING patterns
            dormant: Number of DORMANT patterns
        """
        self.pattern_status_counts = {
            "ACTIVE": active,
            "COOLING": cooling,
            "DORMANT": dormant
        }
    
    def get_summary(self, graph_stats: Dict = None) -> MetricsSummary:
        """
        Get comprehensive metrics summary
        
        Args:
            graph_stats: Optional graph statistics to include
            
        Returns:
            MetricsSummary with all current metrics
        """
        self._prune_old_timestamps()
        
        # Calculate latency stats
        avg_ingestion_latency = (
            sum(self.ingestion_latencies) / len(self.ingestion_latencies)
            if self.ingestion_latencies else 0.0
        )
        
        avg_correlation_latency = (
            sum(self.correlation_latencies) / len(self.correlation_latencies)
            if self.correlation_latencies else 0.0
        )
        
        p95_ingestion = self._calculate_percentile(self.ingestion_latencies, 95)
        p95_correlation = self._calculate_percentile(self.correlation_latencies, 95)
        
        # Calculate average fraud score
        avg_fraud_score = (
            sum(self.fraud_scores) / len(self.fraud_scores)
            if self.fraud_scores else 0.0
        )
        
        # Build summary
        summary = MetricsSummary(
            fingerprints_ingested=len(self.fingerprints_ingested),
            correlations_detected=len(self.correlations_detected),
            alerts_escalated=len(self.alerts_escalated),
            advisories_generated=len(self.advisories_generated),
            avg_ingestion_latency_ms=round(avg_ingestion_latency, 2),
            avg_correlation_latency_ms=round(avg_correlation_latency, 2),
            p95_ingestion_latency_ms=round(p95_ingestion, 2),
            p95_correlation_latency_ms=round(p95_correlation, 2),
            active_entities=len(self.entity_fingerprint_counts),
            entities_by_fingerprints=dict(self.entity_fingerprint_counts),
            advisories_by_severity=dict(self.advisory_severity_counts),
            avg_fraud_score=round(avg_fraud_score, 2),
            active_patterns=self.pattern_status_counts.get("ACTIVE", 0),
            cooling_patterns=self.pattern_status_counts.get("COOLING", 0),
            dormant_patterns=self.pattern_status_counts.get("DORMANT", 0),
            measurement_window_seconds=self.window_size,
            timestamp=datetime.utcnow().isoformat()
        )
        
        # Add graph stats if provided
        if graph_stats:
            summary.graph_size_nodes = graph_stats.get('total_nodes', 0)
            summary.graph_size_edges = graph_stats.get('total_edges', 0)
        
        return summary
    
    def _prune_old_timestamps(self) -> None:
        """Remove timestamps outside the rolling window"""
        cutoff = datetime.utcnow() - timedelta(seconds=self.window_size)
        
        # Prune event timestamps
        while self.fingerprints_ingested and self.fingerprints_ingested[0] < cutoff:
            self.fingerprints_ingested.popleft()
        
        while self.correlations_detected and self.correlations_detected[0] < cutoff:
            self.correlations_detected.popleft()
        
        while self.alerts_escalated and self.alerts_escalated[0] < cutoff:
            self.alerts_escalated.popleft()
        
        while self.advisories_generated and self.advisories_generated[0] < cutoff:
            self.advisories_generated.popleft()
    
    def _calculate_percentile(self, values: Deque[float], percentile: int) -> float:
        """
        Calculate percentile from deque of values
        
        Args:
            values: Deque of numeric values
            percentile: Percentile to calculate (0-100)
            
        Returns:
            Percentile value
        """
        if not values:
            return 0.0
        
        sorted_values = sorted(values)
        index = int(len(sorted_values) * (percentile / 100.0))
        index = min(index, len(sorted_values) - 1)
        
        return sorted_values[index]
    
    def reset(self) -> None:
        """Reset all metrics (useful for testing)"""
        self.ingestion_latencies.clear()
        self.correlation_latencies.clear()
        self.fingerprints_ingested.clear()
        self.correlations_detected.clear()
        self.alerts_escalated.clear()
        self.advisories_generated.clear()
        self.entity_fingerprint_counts.clear()
        self.advisory_severity_counts.clear()
        self.fraud_scores.clear()
        
        logger.info("Metrics tracker reset")
