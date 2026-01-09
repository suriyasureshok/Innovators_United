"""
Transaction Stream Generator
Generates realistic transaction streams for demo purposes
"""
import asyncio
import random
from datetime import datetime
from typing import AsyncGenerator, Optional

from .models import Transaction

class TransactionStreamGenerator:
    """Generates realistic transaction stream for demonstrations"""

    def __init__(self, entity_id: str, seed: Optional[int] = None):
        """
        Initialize transaction stream generator

        Args:
            entity_id: Identifier for this entity
            seed: Random seed for deterministic generation (useful for demos)
        """
        self.entity_id = entity_id
        self.random = random.Random(seed) if seed else random.Random()

        # Pools for realistic data
        self.user_pool = [f"user_{i:04d}" for i in range(100)]
        self.device_pool = [f"device_{i:04d}" for i in range(50)]
        self.merchant_pool = [f"merchant_{i:04d}" for i in range(100)]
        self.locations = [
            "San Francisco, CA",
            "Seattle, WA",
            "Portland, OR",
            "Denver, CO",
            "Austin, TX",
            "Miami, FL",
            "Boston, MA",
            "Atlanta, GA"
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

    async def generate_stream(self, interval_seconds: float = 2.0) -> AsyncGenerator[Transaction, None]:
        """
        Generate continuous transaction stream

        Args:
            interval_seconds: Time between transactions

        Yields:
            Transaction objects
        """
        while True:
            txn = self._generate_transaction()
            yield txn
            await asyncio.sleep(interval_seconds)

    def _generate_transaction(self) -> Transaction:
        """Generate single transaction (normal or suspicious)"""

        # ~80% normal, ~20% suspicious
        is_suspicious = self.random.random() < 0.2

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
        return Transaction(
            transaction_id=self._generate_transaction_id(),
            user_id=self.random.choice(self.user_pool),
            amount=round(self.random.uniform(1000, 5000), 2),  # Higher amounts
            merchant_id=self.random.choice(self.merchant_pool),
            merchant_category=self.random.choice(self.merchant_categories),
            device_id=f"device_new_{self.random.randint(1000, 9999)}",  # New/unseen device
            ip_address=self._generate_ip(),
            location=self.random.choice(self.locations),  # Could be location change
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
