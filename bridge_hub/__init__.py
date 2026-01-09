"""
BRIDGE Hub Package
Central orchestration service for SYNAPSE-FI collective fraud intelligence
"""

__version__ = "1.0.0"
__author__ = "SYNAPSE-FI Team"

from .models import (
    RiskFingerprint,
    Advisory,
    CorrelationResult,
    IntentAlert,
    GraphStats,
    HealthStatus
)
from .brg_graph import BehavioralRiskGraph
from .temporal_correlator import TemporalCorrelator
from .escalation_engine import EscalationEngine
from .advisory_builder import AdvisoryBuilder
from .hub_state import HubState

__all__ = [
    'RiskFingerprint',
    'Advisory',
    'CorrelationResult',
    'IntentAlert',
    'GraphStats',
    'HealthStatus',
    'BehavioralRiskGraph',
    'TemporalCorrelator',
    'EscalationEngine',
    'AdvisoryBuilder',
    'HubState',
]
