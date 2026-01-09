"""
BRIDGE Hub Main Application
Central orchestration service for SYNAPSE-FI collective fraud intelligence
"""
from fastapi import FastAPI, HTTPException, Header, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from datetime import datetime, timedelta
import logging
import asyncio
from contextlib import asynccontextmanager

from .models import (
    RiskFingerprint,
    Advisory,
    GraphStats,
    HealthStatus
)
from .brg_graph import BehavioralRiskGraph
from .temporal_correlator import TemporalCorrelator
from .escalation_engine import EscalationEngine
from .advisory_builder import AdvisoryBuilder
from .hub_state import HubState
from .config import load_config, validate_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global state
brg: BehavioralRiskGraph = None
correlator: TemporalCorrelator = None
escalator: EscalationEngine = None
advisor: AdvisoryBuilder = None
hub_state: HubState = None
config: dict = None
advisories: List[Advisory] = []


# Background task for graph pruning
async def prune_graph_periodically():
    """Background task to periodically prune expired graph edges"""
    while True:
        try:
            await asyncio.sleep(config['prune_interval_seconds'])
            removed = brg.prune_expired_edges()
            if removed > 0:
                logger.info(f"Pruned {removed} expired edges from BRG")
        except Exception as e:
            logger.error(f"Error in graph pruning task: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown"""
    global brg, correlator, escalator, advisor, hub_state, config, advisories
    
    # Startup
    logger.info("🚀 Starting BRIDGE Hub...")
    
    # Load and validate configuration
    config = load_config()
    validate_config(config)
    
    # Initialize components
    brg = BehavioralRiskGraph(
        max_age_seconds=config['max_graph_age_seconds']
    )
    correlator = TemporalCorrelator(config)
    escalator = EscalationEngine(config)
    advisor = AdvisoryBuilder()
    hub_state = HubState(brg, advisories)
    
    # Start background tasks
    asyncio.create_task(prune_graph_periodically())
    
    logger.info("✅ BRIDGE Hub initialized successfully")
    logger.info(f"   Entity threshold: {config['entity_threshold']}")
    logger.info(f"   Time window: {config['time_window_seconds']}s")
    logger.info(f"   Escalation: MEDIUM={config['medium_threshold']}, "
                f"HIGH={config['high_threshold']}, "
                f"CRITICAL={config['critical_threshold']}")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down BRIDGE Hub...")


# Create FastAPI app
app = FastAPI(
    title="SYNAPSE-FI BRIDGE Hub",
    description="Behavioral Risk Intent Discovery & Governance Engine",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# API Key validation
def verify_api_key(x_api_key: str = Header(...)):
    """Verify API key from request header"""
    if x_api_key != config['api_key']:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key


# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "service": "SYNAPSE-FI BRIDGE Hub",
        "version": "1.0.0",
        "description": "Behavioral Risk Intent Discovery & Governance Engine",
        "status": "operational",
        "endpoints": {
            "health": "/health",
            "ingest": "POST /ingest",
            "advisories": "GET /advisories",
            "stats": "GET /stats"
        }
    }


@app.get("/health", response_model=HealthStatus)
async def health_check():
    """
    Health check endpoint
    
    Returns current hub health status
    """
    return hub_state.get_health_status()


@app.get("/stats", response_model=GraphStats)
async def get_stats(api_key: str = Header(..., alias="x-api-key")):
    """
    Get graph statistics
    
    Returns current BRG metrics
    """
    verify_api_key(api_key)
    return hub_state.get_graph_stats()


@app.post("/ingest", status_code=202)
async def ingest_fingerprint(
    fingerprint: RiskFingerprint,
    background_tasks: BackgroundTasks,
    api_key: str = Header(..., alias="x-api-key")
):
    """
    Ingest risk fingerprint from entity
    
    This is the primary ingestion endpoint for entities to submit
    behavioral risk patterns. The hub will:
    1. Add observation to BRG
    2. Detect temporal correlations
    3. Escalate to fraud intent if thresholds met
    4. Generate advisories for all entities
    
    Args:
        fingerprint: RiskFingerprint from entity
        background_tasks: FastAPI background tasks
        api_key: API key for authentication
        
    Returns:
        Ingestion confirmation
    """
    verify_api_key(api_key)
    
    logger.info(
        f"📥 Ingesting fingerprint from {fingerprint.entity_id}: "
        f"{fingerprint.fingerprint[:12]}... (severity={fingerprint.severity})"
    )
    
    # Add to graph
    brg.add_pattern_observation(
        fingerprint=fingerprint.fingerprint,
        entity_id=fingerprint.entity_id,
        severity=fingerprint.severity,
        timestamp=fingerprint.timestamp
    )
    
    # Detect correlation
    correlation = correlator.detect_correlation(fingerprint.fingerprint, brg)
    
    if correlation:
        logger.info(f"✅ Correlation detected: {correlation.entity_count} entities")
        
        # Escalate to fraud intent
        alert = escalator.evaluate(correlation)
        
        if alert:
            logger.warning(f"🚨 Fraud intent escalated: {alert.severity}")
            
            # Build advisory
            advisory = advisor.build_advisory(alert)
            
            # Store advisory
            advisories.append(advisory)
            
            # Trim advisory list if too large
            if len(advisories) > config['max_advisories']:
                advisories[:] = advisories[-config['max_advisories']:]
            
            logger.info(f"📢 Advisory generated: {advisory.advisory_id}")
    else:
        logger.debug("No correlation detected for this fingerprint")
    
    return {
        "status": "accepted",
        "fingerprint": fingerprint.fingerprint[:16] + "...",
        "entity_id": fingerprint.entity_id,
        "correlation_detected": correlation is not None,
        "message": "Fingerprint ingested successfully"
    }


@app.get("/advisories", response_model=List[Advisory])
async def get_advisories(
    limit: int = 10,
    severity: Optional[str] = None,
    api_key: str = Header(..., alias="x-api-key")
):
    """
    Get recent advisories
    
    Entities poll this endpoint to receive fraud advisories
    
    Args:
        limit: Maximum advisories to return (default 10)
        severity: Filter by severity (optional)
        api_key: API key for authentication
        
    Returns:
        List of recent advisories
    """
    verify_api_key(api_key)
    
    return hub_state.get_recent_advisories(limit=limit, severity=severity)


@app.get("/advisories/{advisory_id}", response_model=Advisory)
async def get_advisory(
    advisory_id: str,
    api_key: str = Header(..., alias="x-api-key")
):
    """
    Get specific advisory by ID
    
    Args:
        advisory_id: Advisory identifier
        api_key: API key for authentication
        
    Returns:
        Advisory details
    """
    verify_api_key(api_key)
    
    # Find advisory
    for advisory in advisories:
        if advisory.advisory_id == advisory_id:
            return advisory
    
    raise HTTPException(status_code=404, detail="Advisory not found")


@app.get("/patterns/{fingerprint}")
async def get_pattern_history(
    fingerprint: str,
    hours: int = 24,
    api_key: str = Header(..., alias="x-api-key")
):
    """
    Get observation history for a pattern
    
    Args:
        fingerprint: Pattern fingerprint
        hours: Hours of history (default 24)
        api_key: API key for authentication
        
    Returns:
        Pattern history
    """
    verify_api_key(api_key)
    
    return hub_state.get_pattern_history(fingerprint, hours)


@app.get("/entities/{entity_id}/activity")
async def get_entity_activity(
    entity_id: str,
    hours: int = 24,
    api_key: str = Header(..., alias="x-api-key")
):
    """
    Get activity summary for an entity
    
    Args:
        entity_id: Entity identifier
        hours: Hours of history (default 24)
        api_key: API key for authentication
        
    Returns:
        Entity activity summary
    """
    verify_api_key(api_key)
    
    return hub_state.get_entity_activity(entity_id, hours)


# ============================================================================
# ADMIN ENDPOINTS (for dashboard/monitoring)
# ============================================================================

@app.get("/admin/graph/nodes")
async def get_graph_nodes(api_key: str = Header(..., alias="x-api-key")):
    """Get all graph nodes (patterns)"""
    verify_api_key(api_key)
    
    nodes = list(brg.graph.nodes(data=True))
    return {
        "count": len(nodes),
        "nodes": [
            {"fingerprint": node, "data": data}
            for node, data in nodes
        ]
    }


@app.get("/admin/graph/edges")
async def get_graph_edges(api_key: str = Header(..., alias="x-api-key")):
    """Get all graph edges (observations)"""
    verify_api_key(api_key)
    
    edges = list(brg.graph.edges(data=True))
    return {
        "count": len(edges),
        "edges": [
            {
                "source": src,
                "target": tgt,
                "entity_id": data.get('entity_id'),
                "timestamp": data.get('timestamp', '').isoformat() if data.get('timestamp') else None,
                "severity": data.get('severity')
            }
            for src, tgt, data in edges
        ]
    }


@app.post("/admin/config/update")
async def update_config(
    new_config: dict,
    api_key: str = Header(..., alias="x-api-key")
):
    """
    Update runtime configuration
    
    Allows dynamic adjustment of thresholds and windows
    """
    verify_api_key(api_key)
    
    logger.info(f"Updating configuration: {new_config}")
    
    # Update components
    if 'entity_threshold' in new_config or 'time_window_seconds' in new_config:
        correlator.update_config(new_config)
    
    if any(k in new_config for k in ['critical_threshold', 'high_threshold', 'medium_threshold']):
        escalator.update_config(new_config)
    
    # Update global config
    config.update(new_config)
    
    return {
        "status": "success",
        "message": "Configuration updated",
        "updated_fields": list(new_config.keys())
    }


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    # Load config for port
    config = load_config()
    
    logger.info(f"Starting BRIDGE Hub on {config['host']}:{config['port']}")
    
    uvicorn.run(
        "bridge_hub.main:app",
        host=config['host'],
        port=config['port'],
        reload=True,
        log_level=config['log_level'].lower()
    )
