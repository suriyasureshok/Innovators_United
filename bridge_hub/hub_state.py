"""
Hub State Manager
Provides read-only interface to hub internal state for monitoring and dashboard
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging

from .models import GraphStats, HealthStatus, Advisory
from .brg_graph import BehavioralRiskGraph

logger = logging.getLogger(__name__)


class HubState:
    """
    Read-only interface to hub state
    
    DESIGN PRINCIPLE:
    Dashboard needs visibility, not control.
    State is read-only to prevent interference.
    Stats are computed on-demand, not cached.
    """
    
    def __init__(
        self,
        brg: BehavioralRiskGraph,
        advisories: List[Advisory]
    ):
        """
        Initialize hub state manager
        
        Args:
            brg: Reference to Behavioral Risk Graph
            advisories: Reference to advisory list
        """
        self.brg = brg
        self.advisories = advisories
        self.start_time = datetime.utcnow()
        
        logger.info("Initialized HubState read-only interface")
    
    def get_graph_stats(self) -> GraphStats:
        """
        Get current graph statistics
        
        Returns:
            GraphStats with current metrics
        """
        graph = self.brg.graph
        
        # Count unique fingerprints (nodes)
        unique_patterns = graph.number_of_nodes()
        
        # Count total observations (edges)
        total_observations = graph.number_of_edges()
        
        # Count active entities (unique entity_ids in recent observations)
        active_entities = len(self.brg.get_active_entities(minutes=60))
        
        # Get temporal coverage (convert to int)
        temporal_coverage = int(self._calculate_temporal_coverage())
        
        stats = GraphStats(
            unique_patterns=unique_patterns,
            total_observations=total_observations,
            active_entities=active_entities,
            memory_size_bytes=self._estimate_memory(),
            temporal_coverage_seconds=temporal_coverage
        )
        
        logger.debug(
            f"Graph stats: {unique_patterns} patterns, "
            f"{total_observations} observations, "
            f"{active_entities} active entities"
        )
        
        return stats
    
    def get_health_status(self) -> HealthStatus:
        """
        Get hub health status
        
        Returns:
            HealthStatus with system health
        """
        # Calculate uptime
        uptime = (datetime.utcnow() - self.start_time).total_seconds()
        
        # Check graph status
        graph_healthy = self.brg.graph.number_of_nodes() < 10000  # Memory limit
        
        # Check advisory status
        advisory_count = len(self.advisories)
        advisories_healthy = advisory_count < 1000  # Reasonable limit
        
        # Overall status
        status = "HEALTHY" if (graph_healthy and advisories_healthy) else "DEGRADED"
        
        # Build status message
        if status == "HEALTHY":
            message = "All systems operational"
        else:
            issues = []
            if not graph_healthy:
                issues.append("Graph memory approaching limit")
            if not advisories_healthy:
                issues.append("Advisory queue large")
            message = f"Issues detected: {'; '.join(issues)}"
        
        health = HealthStatus(
            status=status,
            uptime_seconds=uptime,
            message=message,
            timestamp=datetime.utcnow()
        )
        
        logger.debug(f"Health check: {status} - {message}")
        
        return health
    
    def get_recent_advisories(
        self,
        limit: int = 10,
        severity: Optional[str] = None
    ) -> List[Advisory]:
        """
        Get recent advisories
        
        Args:
            limit: Maximum advisories to return
            severity: Filter by severity (optional)
            
        Returns:
            List of recent advisories
        """
        # Filter by severity if specified
        if severity:
            filtered = [adv for adv in self.advisories if adv.severity == severity]
        else:
            filtered = self.advisories
        
        # Sort by timestamp (newest first) and limit
        sorted_advisories = sorted(
            filtered,
            key=lambda x: x.timestamp,
            reverse=True
        )[:limit]
        
        logger.debug(
            f"Retrieved {len(sorted_advisories)} advisories "
            f"(severity={severity}, limit={limit})"
        )
        
        return sorted_advisories
    
    def get_pattern_history(
        self,
        fingerprint: str,
        hours: int = 24
    ) -> Dict:
        """
        Get observation history for a specific pattern
        
        Args:
            fingerprint: Pattern fingerprint
            hours: Hours of history to retrieve
            
        Returns:
            Dictionary with pattern history
        """
        time_window = timedelta(hours=hours)
        observations = self.brg.get_recent_observations(fingerprint, time_window)
        
        if not observations:
            return {
                "fingerprint": fingerprint,
                "status": "NOT_FOUND",
                "message": "No recent observations for this pattern"
            }
        
        # Count entities
        entities = set(obs['entity_id'] for obs in observations)
        
        # Calculate time span
        if len(observations) > 1:
            time_span = (
                observations[-1]['timestamp'] - observations[0]['timestamp']
            ).total_seconds()
        else:
            time_span = 0.0
        
        history = {
            "fingerprint": fingerprint,
            "status": "ACTIVE",
            "observation_count": len(observations),
            "entity_count": len(entities),
            "entities": list(entities),
            "time_span_seconds": time_span,
            "first_seen": observations[0]['timestamp'].isoformat(),
            "last_seen": observations[-1]['timestamp'].isoformat(),
            "observations": [
                {
                    "entity_id": obs['entity_id'],
                    "severity": obs['severity'],
                    "timestamp": obs['timestamp'].isoformat()
                }
                for obs in observations
            ]
        }
        
        logger.debug(
            f"Pattern history for {fingerprint}: "
            f"{len(observations)} observations, {len(entities)} entities"
        )
        
        return history
    
    def get_entity_activity(self, entity_id: str, hours: int = 24) -> Dict:
        """
        Get activity summary for a specific entity
        
        Args:
            entity_id: Entity identifier
            hours: Hours of history
            
        Returns:
            Dictionary with entity activity
        """
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        # Scan graph for entity observations
        observations = []
        for _, _, data in self.brg.graph.edges(data=True):
            if (data.get('entity_id') == entity_id and
                data.get('timestamp', datetime.min) >= cutoff):
                observations.append(data)
        
        if not observations:
            return {
                "entity_id": entity_id,
                "status": "NO_ACTIVITY",
                "message": f"No observations in last {hours} hours"
            }
        
        # Count unique patterns
        patterns = set(obs['pattern'] for obs in observations)
        
        activity = {
            "entity_id": entity_id,
            "status": "ACTIVE",
            "observation_count": len(observations),
            "unique_patterns": len(patterns),
            "patterns": list(patterns),
            "first_observation": min(obs['timestamp'] for obs in observations).isoformat(),
            "last_observation": max(obs['timestamp'] for obs in observations).isoformat()
        }
        
        logger.debug(
            f"Entity activity for {entity_id}: "
            f"{len(observations)} observations, {len(patterns)} patterns"
        )
        
        return activity
    
    def _calculate_temporal_coverage(self) -> float:
        """
        Calculate temporal span of graph data
        
        Returns:
            Time span in seconds from oldest to newest observation
        """
        if self.brg.graph.number_of_edges() == 0:
            return 0.0
        
        timestamps = [
            data['timestamp']
            for _, _, data in self.brg.graph.edges(data=True)
            if 'timestamp' in data
        ]
        
        if not timestamps:
            return 0.0
        
        span = (max(timestamps) - min(timestamps)).total_seconds()
        return span
    
    def _estimate_memory(self) -> int:
        """
        Estimate graph memory usage in bytes
        
        Rough calculation based on node/edge counts
        
        Returns:
            Estimated memory in bytes
        """
        # Rough estimates:
        # - Node: ~200 bytes (fingerprint + metadata)
        # - Edge: ~300 bytes (entity_id + timestamp + severity + pattern)
        
        node_count = self.brg.graph.number_of_nodes()
        edge_count = self.brg.graph.number_of_edges()
        
        estimated = (node_count * 200) + (edge_count * 300)
        
        return estimated
