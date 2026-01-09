"""
BRIDGE Hub Client
Communication interface with BRIDGE Hub for fingerprint sharing and advisory retrieval
"""
import httpx
import asyncio
from typing import Optional, Callable, List
import logging

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
        timeout: float = 10.0
    ):
        """
        Initialize Hub client
        
        Args:
            hub_url: Base URL of BRIDGE Hub (e.g., http://localhost:8000)
            api_key: API key for authentication
            entity_id: This entity's identifier
            timeout: Request timeout in seconds
        """
        self.hub_url = hub_url.rstrip('/')
        self.api_key = api_key
        self.entity_id = entity_id
        self.timeout = timeout
        
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
        
        logger.info(f"Initialized BridgeHubClient for {entity_id} -> {hub_url}")
    
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
        Send risk fingerprint to BRIDGE Hub
        
        Args:
            fingerprint: Privacy-preserving fingerprint hash
            severity: Risk severity (LOW, MEDIUM, HIGH, CRITICAL)
            timestamp: ISO format timestamp
            
        Returns:
            True if successfully sent
            
        Note:
            Failures are logged but don't crash - local decision still proceeds
        """
        try:
            # Create RiskFingerprint object
            fp_data = RiskFingerprint(
                entity_id=self.entity_id,
                fingerprint=fingerprint,
                severity=severity,
                timestamp=timestamp
            )
            
            # Send to Hub
            response = await self.client.post(
                f"{self.hub_url}/ingest",
                json=fp_data.model_dump(mode='json')
            )
            
            if response.status_code == 202:
                self.fingerprints_sent += 1
                result = response.json()
                
                logger.info(f"Fingerprint sent to Hub: {fingerprint[:16]}... "
                           f"(correlation: {result.get('correlation_detected', False)})")
                
                return True
            else:
                logger.warning(f"Hub rejected fingerprint: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            # Log error but don't fail transaction
            logger.error(f"Failed to send fingerprint to Hub: {e}")
            return False
    
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
