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
    """Result of temporal correlation analysis"""
    fingerprint: str = Field(..., description="Pattern fingerprint being analyzed")
    entity_count: int = Field(..., description="Number of unique entities observing pattern")
    time_span_seconds: float = Field(..., description="Time span of observations")
    confidence: str = Field(..., description="Correlation confidence (LOW, MEDIUM, HIGH)")
    observations: List[Dict] = Field(default_factory=list, description="List of observations")
    
    class Config:
        json_schema_extra = {
            "example": {
                "fingerprint": "fp_a3d7e9f2c1b5a8e4",
                "entity_count": 3,
                "time_span_seconds": 180.5,
                "confidence": "HIGH",
                "observations": [
                    {"entity_id": "entity_a", "timestamp": "2026-01-09T14:30:00Z", "severity": "HIGH"},
                    {"entity_id": "entity_b", "timestamp": "2026-01-09T14:32:15Z", "severity": "HIGH"}
                ]
            }
        }


class IntentAlert(BaseModel):
    """Escalated fraud intent alert (internal Hub structure)"""
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


class Advisory(BaseModel):
    """
    Advisory message sent to entities
    This is a recommendation, NOT a command
    Entities maintain sovereignty over decisions
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
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "advisory_id": "adv_12345",
                "fingerprint": "fp_a3d7e9f2c1b5a8e4",
                "confidence": "HIGH",
                "entity_count": 2,
                "first_seen": "2026-01-09T14:30:00Z",
                "last_seen": "2026-01-09T14:32:15Z",
                "rationale": "Pattern observed across 2 entities within 135 seconds",
                "recommendation": "ESCALATE_RISK"
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
