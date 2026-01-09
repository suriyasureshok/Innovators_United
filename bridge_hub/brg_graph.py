"""
Behavioral Risk Graph (BRG) Implementation
In-memory graph structure for pattern correlation with decay tracking
"""
import networkx as nx
from typing import List, Dict, Optional, Set
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class BehavioralRiskGraph:
    """
    In-memory graph for behavioral pattern correlation with decay support
    
    PRIVACY GUARANTEE:
    - Stores only fingerprints (not transactions)
    - No PII whatsoever
    - Relationships only, no raw data
    
    DECAY TRACKING:
    - Stores base_confidence, decay_score, effective_confidence for each pattern
    - Tracks last_seen_timestamp for decay calculations
    - Maintains pattern_status (ACTIVE, COOLING, DORMANT)
    """
    
    def __init__(self, max_age_seconds: int = 300):
        """
        Initialize BRG
        
        Args:
            max_age_seconds: Maximum age of observations in seconds (default 5 minutes)
        """
        self.graph = nx.MultiDiGraph()
        self.time_window = timedelta(seconds=max_age_seconds)
        self.max_age_seconds = max_age_seconds
        self._observation_count = 0
        
        logger.info(f"Initialized BRG with max_age={max_age_seconds}s")
    
    def add_pattern_observation(
        self,
        fingerprint: str,
        entity_id: str,
        severity: str,
        timestamp: datetime,
        base_confidence: float = 0.0,
        decay_score: float = 1.0,
        effective_confidence: float = 0.0,
        pattern_status: str = "ACTIVE"
    ) -> None:
        """
        Add new pattern observation to graph with decay tracking
        
        Args:
            fingerprint: Behavioral pattern fingerprint
            entity_id: Observing entity
            severity: Risk severity level
            timestamp: Observation time
            base_confidence: Base confidence before decay (0.0-1.0)
            decay_score: Time-based decay factor (0.0-1.0)
            effective_confidence: Decayed confidence (0.0-1.0)
            pattern_status: Pattern lifecycle status (ACTIVE, COOLING, DORMANT)
        """
        # Add or update pattern node with decay fields
        if not self.graph.has_node(fingerprint):
            self.graph.add_node(
                fingerprint,
                node_type="pattern",
                first_seen=timestamp,
                observation_count=0,
                base_confidence=base_confidence,
                decay_score=decay_score,
                effective_confidence=effective_confidence,
                last_seen_timestamp=timestamp,
                pattern_status=pattern_status
            )
            logger.debug(f"Created new pattern node: {fingerprint} [status={pattern_status}]")
        else:
            # Update decay fields for existing pattern
            self.graph.nodes[fingerprint]['base_confidence'] = base_confidence
            self.graph.nodes[fingerprint]['decay_score'] = decay_score
            self.graph.nodes[fingerprint]['effective_confidence'] = effective_confidence
            self.graph.nodes[fingerprint]['last_seen_timestamp'] = timestamp
            self.graph.nodes[fingerprint]['pattern_status'] = pattern_status
        
        # Update observation count
        self.graph.nodes[fingerprint]['observation_count'] += 1
        self.graph.nodes[fingerprint]['last_seen'] = timestamp
        
        # Add or get entity node
        if not self.graph.has_node(entity_id):
            self.graph.add_node(entity_id, node_type="entity")
            logger.debug(f"Created new entity node: {entity_id}")
        
        # Add observation edge
        self.graph.add_edge(
            entity_id,
            fingerprint,
            edge_type="OBSERVED_AT",
            timestamp=timestamp,
            severity=severity
        )
        
        self._observation_count += 1
        logger.info(
            f"Added observation: {entity_id} -> {fingerprint} "
            f"[severity={severity}, status={pattern_status}, eff_conf={effective_confidence:.3f}, total_obs={self._observation_count}]"
        )
    
    def get_recent_observations(
        self,
        fingerprint: str,
        time_window: Optional[timedelta] = None
    ) -> List[Dict]:
        """
        Get recent observations of a pattern
        
        Args:
            fingerprint: Pattern to query
            time_window: Optional custom time window
            
        Returns:
            List of observation dictionaries
        """
        if time_window is None:
            time_window = self.time_window
        
        cutoff_time = datetime.utcnow() - time_window
        observations = []
        
        if self.graph.has_node(fingerprint):
            # Get all entities that observed this pattern
            for entity_id in self.graph.predecessors(fingerprint):
                edges = self.graph.get_edge_data(entity_id, fingerprint)
                for edge_key, edge_data in edges.items():
                    if edge_data['timestamp'] > cutoff_time:
                        observations.append({
                            'entity_id': entity_id,
                            'timestamp': edge_data['timestamp'],
                            'severity': edge_data['severity']
                        })
        
        # Sort by timestamp
        observations.sort(key=lambda x: x['timestamp'])
        
        logger.debug(
            f"Found {len(observations)} recent observations for {fingerprint} "
            f"within {time_window.total_seconds()}s"
        )
        
        return observations
    
    def get_active_entities(self, minutes: int) -> List[str]:
        """
        Get entities that have been active within the specified time window
        
        Args:
            minutes: Number of minutes to look back
            
        Returns:
            List of entity IDs that have made observations in the time window
        """
        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
        active_entities = set()
        
        # Check all edges (observations) for recent activity
        for source, target, key, data in self.graph.edges(keys=True, data=True):
            if data.get('timestamp', datetime.min) >= cutoff_time:
                # The source node is the entity_id
                active_entities.add(source)
        
        return list(active_entities)
    
    def get_unique_entities(
        self,
        fingerprint: str,
        time_window: Optional[timedelta] = None
    ) -> int:
        """
        Count unique entities observing a pattern
        
        Args:
            fingerprint: Pattern to query
            time_window: Optional custom time window
            
        Returns:
            Number of unique entities
        """
        observations = self.get_recent_observations(fingerprint, time_window)
        unique_entities = set(obs['entity_id'] for obs in observations)
        return len(unique_entities)
    
    def get_all_entities(self) -> Set[str]:
        """Get all entity IDs in graph"""
        entities = set()
        for node, data in self.graph.nodes(data=True):
            if data.get('node_type') == 'entity':
                entities.add(node)
        return entities
    
    def get_all_patterns(self) -> Set[str]:
        """Get all pattern fingerprints in graph"""
        patterns = set()
        for node, data in self.graph.nodes(data=True):
            if data.get('node_type') == 'pattern':
                patterns.add(node)
        return patterns
    
    def prune_expired_edges(self) -> int:
        """
        Remove edges older than time window
        Also removes orphaned nodes
        
        Returns:
            Number of edges removed
        """
        cutoff_time = datetime.utcnow() - self.time_window
        edges_to_remove = []
        
        # Find expired edges
        for u, v, key, data in self.graph.edges(data=True, keys=True):
            if data.get('timestamp', datetime.max) < cutoff_time:
                edges_to_remove.append((u, v, key))
        
        # Remove expired edges
        for edge in edges_to_remove:
            self.graph.remove_edge(*edge)
        
        # Remove orphaned nodes (nodes with no edges)
        orphaned_nodes = [
            n for n, deg in self.graph.degree() 
            if deg == 0 and self.graph.nodes[n].get('node_type') == 'pattern'
        ]
        self.graph.remove_nodes_from(orphaned_nodes)
        
        if edges_to_remove:
            logger.info(
                f"Pruned {len(edges_to_remove)} expired edges, "
                f"{len(orphaned_nodes)} orphaned nodes"
            )
        
        return len(edges_to_remove)
    
    def get_stats(self) -> Dict:
        """Get graph statistics with decay information"""
        # Count unique patterns (nodes with node_type == 'pattern')
        unique_patterns = len([
            n for n, d in self.graph.nodes(data=True) 
            if d.get('node_type') == 'pattern'
        ])
        
        # Count unique entities (nodes with node_type == 'entity')
        unique_entities = len([
            n for n, d in self.graph.nodes(data=True) 
            if d.get('node_type') == 'entity'
        ])
        
        # Get active entities in last 60 minutes
        active_entities = len(self.get_active_entities(minutes=60))
        
        # Estimate memory usage (rough approximation)
        memory_size_bytes = (
            self.graph.number_of_nodes() * 1000 +  # ~1KB per node
            self.graph.number_of_edges() * 500     # ~500B per edge
        )
        
        # Calculate temporal coverage (time span of observations)
        timestamps = []
        for _, _, data in self.graph.edges(data=True):
            if 'timestamp' in data:
                timestamps.append(data['timestamp'])
        
        if timestamps:
            temporal_coverage_seconds = int((max(timestamps) - min(timestamps)).total_seconds())
        else:
            temporal_coverage_seconds = 0
        
        # Calculate decay statistics
        pattern_statuses = {"ACTIVE": 0, "COOLING": 0, "DORMANT": 0}
        total_effective_confidence = 0.0
        pattern_count = 0
        
        for node, data in self.graph.nodes(data=True):
            if data.get('node_type') == 'pattern':
                status = data.get('pattern_status', 'ACTIVE')
                pattern_statuses[status] = pattern_statuses.get(status, 0) + 1
                total_effective_confidence += data.get('effective_confidence', 0.0)
                pattern_count += 1
        
        avg_effective_confidence = (total_effective_confidence / pattern_count) if pattern_count > 0 else 0.0
        
        return {
            'unique_patterns': unique_patterns,
            'total_observations': self._observation_count,
            'active_entities': active_entities,
            'unique_entities': unique_entities,
            'memory_size_bytes': memory_size_bytes,
            'temporal_coverage_seconds': temporal_coverage_seconds,
            'pattern_statuses': pattern_statuses,
            'avg_effective_confidence': round(avg_effective_confidence, 3)
        }
    
    def get_pattern_details(self, fingerprint: str) -> Optional[Dict]:
        """Get detailed information about a pattern"""
        if not self.graph.has_node(fingerprint):
            return None
        
        node_data = self.graph.nodes[fingerprint]
        if node_data.get('node_type') != 'pattern':
            return None
        
        return {
            'fingerprint': fingerprint,
            'first_seen': node_data.get('first_seen'),
            'last_seen': node_data.get('last_seen'),
            'observation_count': node_data.get('observation_count', 0),
            'entity_count': self.get_unique_entities(fingerprint)
        }
    
    def clear(self) -> None:
        """Clear entire graph (for testing)"""
        self.graph.clear()
        self._observation_count = 0
        logger.warning("Graph cleared")
