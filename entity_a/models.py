"""
Entity A Data Models
Privacy-preserving transaction and risk models
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum


class Transaction(BaseModel):
    """
    Raw transaction model - NEVER leaves entity boundary
    CRITICAL: Contains PII - must remain private
    """
    transaction_id: str = Field(..., description="Unique transaction identifier")
    user_id: str = Field(..., description="User identifier - PRIVATE")
    amount: float = Field(..., ge=0, description="Transaction amount - PRIVATE")
    merchant_id: str = Field(..., description="Merchant identifier - PRIVATE")
    merchant_category: str = Field(..., description="MCC code")
    device_id: str = Field(..., description="Device fingerprint - PRIVATE")
    ip_address: str = Field(..., description="Source IP - PRIVATE")
    location: str = Field(..., description="City, State - PRIVATE")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Transaction timestamp")
    
    class Config:
        json_schema_extra = {
            "sensitive": True,
            "example": {
                "transaction_id": "txn_001",
                "user_id": "user_123",
                "amount": 250.00,
                "merchant_id": "merch_456",
                "merchant_category": "retail",
                "device_id": "device_789",
                "ip_address": "192.168.1.1",
                "location": "New York, NY",
                "timestamp": "2026-01-09T14:30:00Z"
            }
        }


class RiskScore(BaseModel):
    """Risk scoring result with behavioral signals"""
    score: float = Field(..., ge=0, le=100, description="Risk score 0-100")
    signals: List[str] = Field(default_factory=list, description="Triggered risk signals")
    features: Dict = Field(default_factory=dict, description="Extracted features")
    pattern: Optional[str] = Field(None, description="Detected behavior pattern")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "score": 75.5,
                "signals": ["HIGH_VELOCITY", "NEW_DEVICE"],
                "features": {"velocity_count": 8, "device_age_days": 0},
                "pattern": "account_takeover",
                "timestamp": "2026-01-09T14:30:00Z"
            }
        }


class DecisionAction(str, Enum):
    """Transaction decision actions"""
    ALLOW = "allow"
    STEP_UP = "step_up"  # Request additional authentication
    BLOCK = "block"


class Decision(BaseModel):
    """Transaction decision with explanation"""
    transaction_id: str = Field(..., description="Transaction being decided")
    action: DecisionAction = Field(..., description="Decision action")
    risk_score: float = Field(..., ge=0, le=100, description="Original risk score")
    adjusted_score: float = Field(..., ge=0, le=100, description="Score after advisory adjustment")
    adjustment_factors: List[str] = Field(default_factory=list, description="Factors that adjusted score")
    advisory_applied: bool = Field(default=False, description="Whether BRIDGE advisory was applied")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    explanation: Optional[str] = Field(None, description="Human-readable explanation")
    
    class Config:
        json_schema_extra = {
            "example": {
                "transaction_id": "txn_001",
                "action": "block",
                "risk_score": 65.0,
                "adjusted_score": 97.5,
                "adjustment_factors": ["BRIDGE advisory: HIGH confidence"],
                "advisory_applied": True,
                "timestamp": "2026-01-09T14:30:00Z"
            }
        }


class BehaviorPattern(str, Enum):
    """Defined behavior patterns for classification"""
    ACCOUNT_TAKEOVER = "account_takeover"
    CARD_TESTING = "card_testing"
    VELOCITY_ABUSE = "velocity_abuse"
    SUSPICIOUS_TIMING = "suspicious_timing"
    HIGH_VALUE_ANOMALY = "high_value_anomaly"
    NORMAL = "normal"
