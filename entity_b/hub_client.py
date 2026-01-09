"""
BRIDGE Hub Client
Communication interface with BRIDGE Hub for fingerprint sharing and advisory retrieval
"""
import httpx
import asyncio
from typing import Optional, Callable, List, Dict, Deque
import logging
from collections import deque
from datetime import datetime

from bridge_hub.models import RiskFingerprint, Advisory

logger = logging.getLogger(__name__)


class BridgeHubClient:
    """
    Client for communicating with BRIDGE Hub
    
    Responsibilities:
    - Send risk fingerprints to Hub
    - Poll for fraud advisories
    - Handle connectivity issues gracefully
    """
    
    def __init__(
        self,
        hub_url: str,
        api_key: str,
        entity_id: str,
        timeout: float = 10.0,
        max_retries: int = 3,
        retry_backoff: float = 1.0,
        max_pending: int = 1000
    ):
        """
        Initialize Hub client
        
        Args:
            hub_url: Base URL of BRIDGE Hub (e.g., http://localhost:8000)
            api_key: API key for authentication
            entity_id: This entity's identifier
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts for failed requests
            retry_backoff: Base backoff time in seconds (exponential)
            max_pending: Maximum pending fingerprints to queue when Hub unavailable
        """
        self.hub_url = hub_url.rstrip('/')
        self.api_key = api_key
        self.entity_id = entity_id
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_backoff = retry_backoff
        self.max_pending = max_pending
        
        # HTTP client for Hub communication
        self.client = httpx.AsyncClient(
            timeout=timeout,
            headers={
                "x-api-key": api_key,
                "X-Entity-ID": entity_id
            }
        )
        
        self.connected = False
        self.fingerprints_sent = 0
        self.advisories_received = 0
        
        # Graceful degradation: Queue fingerprints when Hub unavailable
        self.pending_fingerprints: Deque[Dict] = deque(maxlen=max_pending)
        self.failed_sends = 0
        self.retry_sends = 0
        
        logger.info(f"Initialized BridgeHubClient for {entity_id} -> {hub_url} "
                   f"(max_retries={max_retries}, max_pending={max_pending})")
    
    async def check_health(self) -> bool:
        """
        Check if Hub is reachable
        
        Returns:
            True if Hub is healthy
        """
        try:
            response = await self.client.get(f"{self.hub_url}/health")
            self.connected = response.status_code == 200
            
            if self.connected:
                logger.info("Successfully connected to BRIDGE Hub")
            else:
                logger.warning(f"Hub health check failed: {response.status_code}")
            
            return self.connected
            
        except Exception as e:
            logger.error(f"Failed to connect to Hub: {e}")
            self.connected = False
            return False
    
    async def send_fingerprint(
        self,
        fingerprint: str,
        severity: str,
        timestamp: str
    ) -> bool:
        """
        Send risk fingerprint to BRIDGE Hub with retry logic
        
        Args:
            fingerprint: Privacy-preserving fingerprint hash
            severity: Risk severity (LOW, MEDIUM, HIGH, CRITICAL)
            timestamp: ISO format timestamp
            
        Returns:
            True if successfully sent (or queued for retry)
            
        Note:
            - Uses exponential backoff for retries
            - Queues fingerprints when Hub unavailable
            - Entity continues operating locally regardless
        """
        # Create RiskFingerprint object
        fp_data = RiskFingerprint(
            entity_id=self.entity_id,
            fingerprint=fingerprint,
            severity=severity,
            timestamp=timestamp
        )
        
        # Try sending with exponential backoff
        for attempt in range(self.max_retries):
            try:
                # Send to Hub
                response = await self.client.post(
                    f"{self.hub_url}/ingest",
                    json=fp_data.model_dump(mode='json')
                )
                
                if response.status_code == 202:
                    self.fingerprints_sent += 1
                    result = response.json()
                    
                    if attempt > 0:
                        self.retry_sends += 1
                        logger.info(f"Fingerprint sent after {attempt} retries: {fingerprint[:16]}...")
                    else:
                        logger.info(f"Fingerprint sent to Hub: {fingerprint[:16]}... "
                                   f"(correlation: {result.get('correlation_detected', False)})")
                    
                    # Try sending pending fingerprints if Hub is back online
                    if self.pending_fingerprints:
                        asyncio.create_task(self._flush_pending_fingerprints())
                    
                    return True
                else:
                    logger.warning(f"Hub rejected fingerprint (attempt {attempt+1}): "
                                 f"{response.status_code} - {response.text}")
                    
            except (httpx.ConnectError, httpx.TimeoutException) as e:
                # Network/connectivity error - retry with backoff
                if attempt < self.max_retries - 1:
                    backoff = self.retry_backoff * (2 ** attempt)
                    logger.warning(f"Hub connection failed (attempt {attempt+1}), "
                                 f"retrying in {backoff:.1f}s: {e}")
                    await asyncio.sleep(backoff)
                else:
                    # Max retries exceeded - queue for later
                    logger.error(f"Hub unavailable after {self.max_retries} attempts, "
                               f"queuing fingerprint: {e}")
                    self._queue_fingerprint(fp_data)
                    self.failed_sends += 1
                    return False
                    
            except Exception as e:
                # Unexpected error - log and queue
                logger.error(f"Unexpected error sending fingerprint (attempt {attempt+1}): {e}")
                if attempt == self.max_retries - 1:
                    self._queue_fingerprint(fp_data)
                    self.failed_sends += 1
                    return False
        
        return False
    
    def _queue_fingerprint(self, fp_data: RiskFingerprint) -> None:
        """
        Queue fingerprint for later transmission when Hub unavailable
        
        Args:
            fp_data: Fingerprint to queue
        """
        if len(self.pending_fingerprints) >= self.max_pending:
            logger.warning(f"Pending fingerprint queue full ({self.max_pending}), "
                         f"dropping oldest fingerprint")
        
        self.pending_fingerprints.append({
            'fingerprint': fp_data.fingerprint,
            'severity': fp_data.severity,
            'timestamp': fp_data.timestamp,
            'queued_at': datetime.utcnow().isoformat()
        })
        
        logger.info(f"Queued fingerprint for later transmission "
                   f"({len(self.pending_fingerprints)} pending)")
    
    async def _flush_pending_fingerprints(self) -> None:
        """
        Attempt to send all queued fingerprints when Hub becomes available
        """
        if not self.pending_fingerprints:
            return
        
        logger.info(f"Attempting to flush {len(self.pending_fingerprints)} pending fingerprints")
        
        flushed = 0
        while self.pending_fingerprints:
            fp_dict = self.pending_fingerprints[0]
            
            # Try sending once (no retries for pending)
            try:
                fp_data = RiskFingerprint(
                    entity_id=self.entity_id,
                    fingerprint=fp_dict['fingerprint'],
                    severity=fp_dict['severity'],
                    timestamp=fp_dict['timestamp']
                )
                
                response = await self.client.post(
                    f"{self.hub_url}/ingest",
                    json=fp_data.model_dump(mode='json')
                )
                
                if response.status_code == 202:
                    self.pending_fingerprints.popleft()
                    flushed += 1
                else:
                    # Hub not ready yet
                    break
                    
            except Exception:
                # Hub still unavailable
                break
        
        if flushed > 0:
            logger.info(f"Successfully flushed {flushed} pending fingerprints "
                       f"({len(self.pending_fingerprints)} remaining)")
    
    async def get_advisories(
        self,
        limit: int = 10,
        severity: Optional[str] = None
    ) -> List[Advisory]:
        """
        Retrieve fraud advisories from Hub
        
        Args:
            limit: Maximum advisories to retrieve
            severity: Filter by severity (optional)
            
        Returns:
            List of Advisory objects
        """
        try:
            params = {"limit": limit}
            if severity:
                params["severity"] = severity
            
            response = await self.client.get(
                f"{self.hub_url}/advisories",
                params=params
            )
            
            if response.status_code == 200:
                advisories_data = response.json()
                advisories = [Advisory(**adv) for adv in advisories_data]
                
                self.advisories_received += len(advisories)
                
                logger.info(f"Retrieved {len(advisories)} advisories from Hub")
                
                return advisories
            else:
                logger.warning(f"Failed to get advisories: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Failed to retrieve advisories from Hub: {e}")
            return []
    
    async def get_advisory_for_fingerprint(
        self,
        fingerprint: str
    ) -> Optional[Advisory]:
        """
        Get specific advisory matching a fingerprint
        
        Args:
            fingerprint: Fingerprint to match
            
        Returns:
            Advisory if found, None otherwise
        """
        try:
            # Get recent advisories and filter locally
            advisories = await self.get_advisories(limit=50)
            
            for advisory in advisories:
                # Check if advisory fingerprint matches (truncated comparison)
                if advisory.fingerprint.startswith(fingerprint[:10]):
                    logger.info(f"Found matching advisory: {advisory.advisory_id}")
                    return advisory
            
            logger.debug(f"No advisory found for fingerprint: {fingerprint[:16]}...")
            return None
            
        except Exception as e:
            logger.error(f"Failed to get advisory for fingerprint: {e}")
            return None
    
    async def poll_advisories_continuously(
        self,
        callback: Callable[[Advisory], None],
        interval_seconds: float = 10.0
    ):
        """
        Continuously poll for new advisories
        
        Args:
            callback: Async function to call with each advisory
            interval_seconds: Polling interval
        """
        logger.info(f"Starting continuous advisory polling (interval={interval_seconds}s)")
        
        seen_advisory_ids = set()
        
        while True:
            try:
                advisories = await self.get_advisories(limit=20)
                
                # Process new advisories
                for advisory in advisories:
                    if advisory.advisory_id not in seen_advisory_ids:
                        seen_advisory_ids.add(advisory.advisory_id)
                        await callback(advisory)
                
                # Clean up old IDs (keep last 1000)
                if len(seen_advisory_ids) > 1000:
                    seen_advisory_ids = set(list(seen_advisory_ids)[-1000:])
                
                await asyncio.sleep(interval_seconds)
                
            except Exception as e:
                logger.error(f"Error in advisory polling: {e}")
                await asyncio.sleep(interval_seconds)
    
    async def get_hub_stats(self) -> dict:
        """
        Get Hub statistics
        
        Returns:
            Dictionary with Hub stats
        """
        try:
            response = await self.client.get(f"{self.hub_url}/stats")
            
            if response.status_code == 200:
                return response.json()
            else:
                return {}
                
        except Exception as e:
            logger.error(f"Failed to get Hub stats: {e}")
            return {}
    
    def get_client_stats(self) -> dict:
        """Get client statistics"""
        return {
            "entity_id": self.entity_id,
            "hub_url": self.hub_url,
            "connected": self.connected,
            "fingerprints_sent": self.fingerprints_sent,
            "advisories_received": self.advisories_received
        }
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()
        logger.info("Closed BridgeHubClient")
