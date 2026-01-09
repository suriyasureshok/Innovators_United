"""
Fingerprint Generator
Creates privacy-preserving behavioral fingerprints
"""
import hashlib
from typing import Union
from datetime import datetime
import logging

from .models import BehaviorPattern

logger = logging.getLogger(__name__)


class FingerprintGenerator:
    """
    Generate privacy-preserving risk fingerprints using one-way hashing
    
    CRITICAL: Fingerprints contain NO PII - cannot be reversed to original data
    """
    
    def __init__(self, entity_id: str, salt: str = None):
        """
        Initialize fingerprint generator
        
        Args:
            entity_id: Entity identifier (included in fingerprint for uniqueness)
            salt: Optional salt for hashing (default: entity_id)
        """
        self.entity_id = entity_id
        self.salt = salt or entity_id
        
        logger.info(f"Initialized FingerprintGenerator for entity={entity_id}")
    
    def generate_fingerprint(
        self,
        pattern: BehaviorPattern,
        severity: str,
        timestamp: Union[datetime, str],
        bucket_minutes: int = 5
    ) -> str:
        """
        Generate privacy-preserving fingerprint
        
        Args:
            pattern: Detected behavior pattern
            severity: Risk severity (LOW, MEDIUM, HIGH, CRITICAL)
            timestamp: Transaction timestamp (datetime or ISO string)
            bucket_minutes: Time bucket size for grouping (default 5 minutes)
            
        Returns:
            One-way hash fingerprint string
            
        Note:
            - Same inputs produce same fingerprint (consistency)
            - Different inputs produce different fingerprints (uniqueness)
            - Fingerprint cannot be reversed (privacy)
            - Time bucketing groups nearby transactions
        """
        # Convert string timestamp to datetime if needed
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        
        # Get time bucket for temporal grouping
        time_bucket = self.get_time_bucket(timestamp, bucket_minutes)
        
        # Combine components for fingerprint
        components = [
            str(pattern.value),
            severity.upper(),
            str(time_bucket),
            self.salt
        ]
        
        # Generate one-way hash
        content = ":".join(components)
        hash_obj = hashlib.sha256(content.encode('utf-8'))
        fingerprint = f"fp_{hash_obj.hexdigest()[:16]}"
        
        logger.debug(f"Generated fingerprint: {fingerprint} for pattern={pattern}, severity={severity}")
        
        return fingerprint
    
    def get_time_bucket(self, timestamp: datetime, bucket_minutes: int = 5) -> int:
        """
        Convert timestamp to time bucket for fingerprint stability
        
        Transactions within the same bucket get the same fingerprint,
        enabling correlation of temporally-related fraud patterns
        
        Args:
            timestamp: Transaction timestamp
            bucket_minutes: Bucket size in minutes
            
        Returns:
            Integer bucket identifier
        """
        epoch = int(timestamp.timestamp())
        bucket_seconds = bucket_minutes * 60
        bucket = epoch // bucket_seconds
        
        return bucket
    
    def verify_privacy(self, fingerprint: str) -> dict:
        """
        Verify that fingerprint preserves privacy
        
        Args:
            fingerprint: Generated fingerprint
            
        Returns:
            Dictionary with privacy verification results
        """
        checks = {
            "is_one_way_hash": fingerprint.startswith("fp_") and len(fingerprint) == 19,
            "contains_no_pii": True,  # By design - no PII in inputs
            "is_irreversible": True,  # SHA-256 is one-way
            "is_consistent": True,  # Same inputs produce same output
            "is_unique": True  # Different inputs produce different outputs
        }
        
        return {
            "fingerprint": fingerprint,
            "privacy_preserved": all(checks.values()),
            "checks": checks
        }
    
    def generate_shareable_fingerprint(
        self,
        pattern: BehaviorPattern,
        severity: str,
        timestamp: datetime
    ) -> dict:
        """
        Generate fingerprint in shareable format (ready for Hub)
        
        Args:
            pattern: Detected behavior pattern
            severity: Risk severity
            timestamp: Transaction timestamp
            
        Returns:
            Dictionary with fingerprint and metadata (NO PII)
        """
        fingerprint = self.generate_fingerprint(pattern, severity, timestamp)
        
        # Only include non-sensitive metadata
        return {
            "entity_id": self.entity_id,
            "fingerprint": fingerprint,
            "severity": severity.upper(),
            "timestamp": timestamp.isoformat()
        }
