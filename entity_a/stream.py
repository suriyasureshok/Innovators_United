"""
Transaction Stream Generator
Generates realistic transaction streams for demo purposes
"""
import asyncio
import random
from datetime import datetime, timedelta
from typing import AsyncGenerator, Optional, List
import logging

from .models import Transaction

logger = logging.getLogger(__name__)


class TransactionStreamGenerator:
    """Generates realistic transaction stream for demonstrations"""
    
    def __init__(
        self,
        entity_id: str,
        seed: Optional[int] = None,
        fraud_probability: float = 0.2
    ):
        """
        Initialize transaction stream generator
        
        Args:
            entity_id: Identifier for this entity
            seed: Random seed for deterministic generation (useful for demos)
            fraud_probability: Probability of generating suspicious transaction (0-1)
        """
        self.entity_id = entity_id
        self.fraud_probability = fraud_probability
        self.random = random.Random(seed) if seed else random.Random()
        
        # Pools for realistic data
        self.user_pool = [f"user_{i:04d}" for i in range(100)]
        self.device_pool = [f"device_{i:04d}" for i in range(50)]
        self.merchant_pool = [f"merchant_{i:04d}" for i in range(100)]
        self.locations = [
            "New York, NY",
            "Los Angeles, CA",
            "Chicago, IL",
            "Houston, TX",
            "Phoenix, AZ",
            "Philadelphia, PA",
            "San Antonio, TX",
            "San Diego, CA"
        ]
        self.merchant_categories = [
            "retail",
            "grocery",
            "gas_station",
            "restaurant",
            "electronics",
            "pharmacy",
            "entertainment",
            "travel"
        ]
        
        # Fraud scenario markers
        self.coordinated_fraud_pattern = None
        self.transaction_count = 0
    
    async def generate_stream(
        self,
        interval_seconds: float = 2.0,
        max_transactions: Optional[int] = None
    ) -> AsyncGenerator[Transaction, None]:
        """
        Generate continuous transaction stream
        
        Args:
            interval_seconds: Time between transactions
            max_transactions: Maximum transactions to generate (None for infinite)
            
        Yields:
            Transaction objects
        """
        logger.info(f"Starting transaction stream for {self.entity_id} "
                   f"(interval={interval_seconds}s, fraud_probability={self.fraud_probability})")
        
        count = 0
        while max_transactions is None or count < max_transactions:
            try:
                txn = self._generate_transaction()
                self.transaction_count += 1
                count += 1
                
                logger.debug(f"Generated transaction {txn.transaction_id}")
                yield txn
                
                await asyncio.sleep(interval_seconds)
                
            except Exception as e:
                logger.error(f"Error generating transaction: {e}")
                await asyncio.sleep(interval_seconds)
    
    def generate_batch(self, count: int) -> List[Transaction]:
        """
        Generate batch of transactions synchronously
        
        Args:
            count: Number of transactions to generate
            
        Returns:
            List of transactions
        """
        return [self._generate_transaction() for _ in range(count)]
    
    def _generate_transaction(self) -> Transaction:
        """Generate single transaction (normal or suspicious)"""
        
        # Decide if this should be suspicious
        is_suspicious = self.random.random() < self.fraud_probability
        
        if is_suspicious:
            return self._generate_suspicious_transaction()
        else:
            return self._generate_normal_transaction()
    
    def _generate_normal_transaction(self) -> Transaction:
        """Generate low-risk normal transaction"""
        return Transaction(
            transaction_id=self._generate_transaction_id(),
            user_id=self.random.choice(self.user_pool),
            amount=round(self.random.uniform(10, 500), 2),
            merchant_id=self.random.choice(self.merchant_pool),
            merchant_category=self.random.choice(self.merchant_categories),
            device_id=self.random.choice(self.device_pool),
            ip_address=self._generate_ip(),
            location=self.random.choice(self.locations),
            timestamp=datetime.utcnow()
        )
    
    def _generate_suspicious_transaction(self) -> Transaction:
        """Generate high-risk suspicious transaction"""
        
        # Choose type of suspicious behavior
        behavior_type = self.random.choice([
            'high_velocity',
            'new_device',
            'high_value',
            'coordinated'
        ])
        
        if behavior_type == 'high_velocity':
            # Multiple transactions from same user quickly
            user = self.random.choice(self.user_pool[:20])  # Concentrate on fewer users
            return Transaction(
                transaction_id=self._generate_transaction_id(),
                user_id=user,
                amount=round(self.random.uniform(50, 300), 2),
                merchant_id=self.random.choice(self.merchant_pool[:30]),
                merchant_category=self.random.choice(self.merchant_categories),
                device_id=self.random.choice(self.device_pool),
                ip_address=self._generate_ip(),
                location=self.random.choice(self.locations),
                timestamp=datetime.utcnow()
            )
        
        elif behavior_type == 'new_device':
            # Transaction from new/unknown device
            return Transaction(
                transaction_id=self._generate_transaction_id(),
                user_id=self.random.choice(self.user_pool),
                amount=round(self.random.uniform(200, 800), 2),
                merchant_id=self.random.choice(self.merchant_pool),
                merchant_category=self.random.choice(['electronics', 'travel']),
                device_id=f"device_new_{self.random.randint(1000, 9999)}",
                ip_address=self._generate_ip(),
                location=self.random.choice(self.locations),
                timestamp=datetime.utcnow()
            )
        
        elif behavior_type == 'high_value':
            # Unusually high transaction amount
            return Transaction(
                transaction_id=self._generate_transaction_id(),
                user_id=self.random.choice(self.user_pool),
                amount=round(self.random.uniform(1000, 5000), 2),
                merchant_id=self.random.choice(self.merchant_pool),
                merchant_category=self.random.choice(['electronics', 'entertainment', 'travel']),
                device_id=self.random.choice(self.device_pool),
                ip_address=self._generate_ip(),
                location=self.random.choice(self.locations),
                timestamp=datetime.utcnow()
            )
        
        else:  # coordinated
            # Part of coordinated fraud pattern (will correlate across entities)
            if not self.coordinated_fraud_pattern:
                self.coordinated_fraud_pattern = f"fraud_pattern_{self.random.randint(10000, 99999)}"
            
            return Transaction(
                transaction_id=self._generate_transaction_id(),
                user_id=self.random.choice(self.user_pool[:30]),
                amount=round(self.random.uniform(500, 2000), 2),
                merchant_id=f"merchant_suspicious_{self.random.randint(1, 10)}",
                merchant_category="electronics",
                device_id=f"device_coordinated_{self.random.randint(1, 5)}",
                ip_address=self._generate_suspicious_ip(),
                location="Los Angeles, CA",  # Common location for coordinated fraud
                timestamp=datetime.utcnow()
            )
    
    def _generate_transaction_id(self) -> str:
        """Generate unique transaction ID"""
        timestamp = int(datetime.utcnow().timestamp() * 1000)
        random_suffix = self.random.randint(1000, 9999)
        return f"txn_{self.entity_id}_{timestamp}_{random_suffix}"
    
    def _generate_ip(self) -> str:
        """Generate random IP address"""
        return f"{self.random.randint(1, 255)}.{self.random.randint(0, 255)}." \
               f"{self.random.randint(0, 255)}.{self.random.randint(1, 255)}"
    
    def _generate_suspicious_ip(self) -> str:
        """Generate IP from suspicious range (for coordinated fraud)"""
        # Use specific suspicious IP ranges
        base = self.random.choice(["185.220", "45.141", "23.154"])
        return f"{base}.{self.random.randint(0, 255)}.{self.random.randint(1, 255)}"
    
    def get_stats(self) -> dict:
        """Get generator statistics"""
        return {
            "entity_id": self.entity_id,
            "transactions_generated": self.transaction_count,
            "fraud_probability": self.fraud_probability,
            "user_pool_size": len(self.user_pool),
            "device_pool_size": len(self.device_pool)
        }
