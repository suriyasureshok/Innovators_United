"""
BRIDGE Hub Data Models
Shared interfaces for Hub components - NO PII ALLOWED
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum


class RiskFingerprint(BaseModel):
    """
    Shareable risk fingerprint from entities
    CRITICAL: Contains NO PII - only behavioral abstractions
    """
    entity_id: str = Field(..., description="Entity identifier (e.g., 'entity_a')")
    fingerprint: str = Field(..., description="One-way hash of behavioral pattern")
    severity: str = Field(..., description="Risk severity level (LOW, MEDIUM, HIGH, CRITICAL)")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Observation timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "entity_id": "entity_a",
                "fingerprint": "fp_a3d7e9f2c1b5a8e4",
                "severity": "HIGH",
                "timestamp": "2026-01-09T14:30:00Z"
            }
        }


class CorrelationResult(BaseModel):
    """Result of temporal correlation analysis with decay support"""
    fingerprint: str = Field(..., description="Pattern fingerprint being analyzed")
    entity_count: int = Field(..., description="Number of unique entities observing pattern")
    time_span_seconds: float = Field(..., description="Time span of observations")
    confidence: str = Field(..., description="Correlation confidence (LOW, MEDIUM, HIGH)")
    observations: List[Dict] = Field(default_factory=list, description="List of observations")
    
    # Decay-related fields
    base_confidence: float = Field(default=0.0, description="Base correlation confidence before decay (0.0-1.0)")
    decay_score: float = Field(default=1.0, description="Time-based decay factor (0.0-1.0)")
    effective_confidence: float = Field(default=0.0, description="Decayed confidence for decisions (0.0-1.0)")
    last_seen_timestamp: datetime = Field(default_factory=datetime.utcnow, description="Last observation time")
    pattern_status: str = Field(default="ACTIVE", description="Pattern lifecycle status (ACTIVE, COOLING, DORMANT)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "fingerprint": "fp_a3d7e9f2c1b5a8e4",
                "entity_count": 3,
                "time_span_seconds": 180.5,
                "confidence": "HIGH",
                "base_confidence": 0.85,
                "decay_score": 1.0,
                "effective_confidence": 0.85,
                "pattern_status": "ACTIVE",
                "observations": [
                    {"entity_id": "entity_a", "timestamp": "2026-01-09T14:30:00Z", "severity": "HIGH"},
                    {"entity_id": "entity_b", "timestamp": "2026-01-09T14:32:15Z", "severity": "HIGH"}
                ]
            }
        }


class IntentAlert(BaseModel):
    """Escalated fraud intent alert (internal Hub structure) with decay tracking"""
    alert_id: str = Field(..., description="Unique alert identifier")
    intent_type: str = Field(..., description="Type of fraud intent detected")
    fingerprint: str = Field(..., description="Pattern fingerprint")
    severity: str = Field(..., description="Severity level")
    confidence: str = Field(..., description="Confidence level")
    entity_count: int = Field(..., description="Entities affected")
    time_span_seconds: float = Field(..., description="Time span")
    description: str = Field(..., description="Human-readable description")
    rationale: str = Field(..., description="Human-readable rationale")
    recommendation: str = Field(..., description="Recommended action")
    fraud_score: int = Field(..., description="Fraud risk score (0-100)")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Decay-related fields for pattern lifecycle
    base_confidence: float = Field(default=0.0, description="Base confidence before decay (0.0-1.0)")
    decay_score: float = Field(default=1.0, description="Time-based decay factor (0.0-1.0)")
    effective_confidence: float = Field(default=0.0, description="Decayed confidence for escalation (0.0-1.0)")
    last_seen_timestamp: datetime = Field(default_factory=datetime.utcnow, description="Last pattern observation")
    pattern_status: str = Field(default="ACTIVE", description="Pattern lifecycle status (ACTIVE, COOLING, DORMANT)")
    time_since_last_seen_seconds: float = Field(default=0.0, description="Seconds since last observation")
    decay_explanation: str = Field(default="", description="Human-readable decay reasoning")


class Advisory(BaseModel):
    """
    Advisory message sent to entities
    This is a recommendation, NOT a command
    Entities maintain sovereignty over decisions
    Includes decay information for pattern lifecycle awareness
    """
    advisory_id: str = Field(..., description="Unique advisory identifier")
    fingerprint: str = Field(..., description="Pattern fingerprint")
    severity: str = Field(..., description="Severity level (INFO, LOW, MEDIUM, HIGH, CRITICAL)")
    message: str = Field(..., description="Human-readable advisory message")
    recommended_actions: List[str] = Field(..., description="List of recommended actions")
    entity_count: int = Field(..., description="Number of entities affected")
    confidence: str = Field(..., description="Confidence level (LOW, MEDIUM, HIGH)")
    fraud_score: int = Field(..., description="Fraud risk score (0-100)")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Decay-related fields for entity decision-making
    base_confidence: float = Field(default=0.0, description="Base confidence before decay (0.0-1.0)")
    decay_score: float = Field(default=1.0, description="Time-based decay factor (0.0-1.0)")
    effective_confidence: float = Field(default=0.0, description="Decayed confidence for entity decisions (0.0-1.0)")
    last_seen_timestamp: datetime = Field(default_factory=datetime.utcnow, description="Last pattern observation")
    pattern_status: str = Field(default="ACTIVE", description="Pattern lifecycle status (ACTIVE, COOLING, DORMANT)")
    time_since_last_seen_seconds: float = Field(default=0.0, description="Seconds since last observation")
    decay_explanation: str = Field(default="", description="Human-readable decay reasoning for transparency")
    
    class Config:
        json_schema_extra = {
            "example": {
                "advisory_id": "adv_12345",
                "fingerprint": "fp_a3d7e9f2c1b5a8e4",
                "confidence": "HIGH",
                "entity_count": 2,
                "fraud_score": 85,
                "severity": "HIGH",
                "message": "Cross-entity fraud pattern detected",
                "recommended_actions": ["INCREASE_MONITORING", "APPLY_CHALLENGE"],
                "base_confidence": 0.88,
                "decay_score": 0.8,
                "effective_confidence": 0.704,
                "pattern_status": "ACTIVE",
                "time_since_last_seen_seconds": 180.5,
                "decay_explanation": "Pattern observed 3 minutes ago (recent window, decay=0.8)"
            }
        }


class GraphStats(BaseModel):
    """Statistics about the Behavioral Risk Graph"""
    unique_patterns: int = Field(..., description="Number of unique pattern fingerprints")
    total_observations: int = Field(..., description="Total number of pattern observations")
    active_entities: int = Field(..., description="Number of entities active in recent time window")
    memory_size_bytes: int = Field(..., description="Estimated memory usage in bytes")
    temporal_coverage_seconds: int = Field(..., description="Time span covered by current observations")


class HealthStatus(BaseModel):
    """Health status of Hub service"""
    status: str = Field(..., description="Service status (healthy, degraded, unhealthy)")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    graph_stats: Optional[GraphStats] = None
    message: Optional[str] = None
