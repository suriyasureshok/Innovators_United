<<<<<<< HEAD
"""
Entity B - Main Transaction Processing Service
Asynchronous transaction stream consumer
"""
import asyncio
import time
from datetime import datetime

from entity_b.stream import TransactionStreamGenerator
from entity_b.models import Transaction


class EntityBService:
    """
    Entity B Transaction Processing Service

    Continuously consumes transactions from stream
    """

    def __init__(self, entity_id: str = "entity_b"):
        """
        Initialize Entity B service

        Args:
            entity_id: Entity identifier
        """
        self.entity_id = entity_id

        # Metrics
        self.transactions_processed = 0
        self.start_time = None

    async def initialize(self):
        """Initialize service (async setup)"""
        self.start_time = time.time()

    async def process_transaction(self, transaction: Transaction) -> None:
        """
        Process single transaction

        Args:
            transaction: Transaction to process
        """
        try:
            # Basic processing placeholder
            self.transactions_processed += 1

        except Exception as e:
            print(f"Error processing transaction {transaction.transaction_id}: {e}")

    async def run_stream(self, interval_seconds: float = 2.0, duration_seconds: float = None):
        """
        Run transaction stream processing

        Args:
            interval_seconds: Time between transactions
            duration_seconds: Optional duration limit
        """
        print(f"🟦 Entity B starting transaction stream...")

        generator = TransactionStreamGenerator(self.entity_id, seed=67890)  # Different seed

        start = time.time()

        async for transaction in generator.generate_stream(interval_seconds):
            await self.process_transaction(transaction)

            # Check duration limit
            if duration_seconds and (time.time() - start) >= duration_seconds:
                break

    def get_stats(self) -> dict:
        """Get service statistics"""
        elapsed = time.time() - self.start_time if self.start_time else 0

        return {
            "entity_id": self.entity_id,
            "transactions_processed": self.transactions_processed,
            "elapsed_seconds": round(elapsed, 2),
            "transactions_per_second": round(self.transactions_processed / elapsed, 2) if elapsed > 0 else 0
        }


async def main():
    """Run Entity B service"""
    service = EntityBService()
    await service.initialize()

    try:
        # Run for 60 seconds
        await service.run_stream(interval_seconds=2.0, duration_seconds=60)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Entity B...")

    stats = service.get_stats()
    print(f"\n📊 Entity B Final Stats:")
    print(f"   Transactions Processed: {stats['transactions_processed']}")
    print(f"   Duration: {stats['elapsed_seconds']}s")
    print(f"   Rate: {stats['transactions_per_second']} txn/s")


if __name__ == "__main__":
    asyncio.run(main())
=======
"""
Entity B - Main Transaction Processing Service
Asynchronous transaction stream consumer
"""
import asyncio
import time
from datetime import datetime

from entity_b.stream import TransactionStreamGenerator
from entity_b.models import Transaction
from entity_b.risk_engine import FeatureExtractor, RiskScorer
from entity_b.pattern_classifier import PatternClassifier
from entity_b.fingerprint import FingerprintGenerator
from entity_b.hub_client import BridgeHubClient


class EntityBService:
    """
    Entity B Transaction Processing Service

    Continuously consumes transactions from stream
    """

    def __init__(self, entity_id: str = "entity_b"):
        """
        Initialize Entity B service

        Args:
            entity_id: Entity identifier
        """
        self.entity_id = entity_id

        # Initialize processing components
        self.feature_extractor = FeatureExtractor()
        self.risk_scorer = RiskScorer()
        self.pattern_classifier = PatternClassifier()
        self.fingerprint_generator = FingerprintGenerator(entity_id=entity_id)
        
        # Hub client
        self.hub_client = BridgeHubClient(
            hub_url="http://localhost:8001",
            api_key="dev-key-change-in-production",
            entity_id=entity_id
        )

        # Metrics
        self.transactions_processed = 0
        self.fingerprints_sent = 0
        self.start_time = None

    async def initialize(self):
        """Initialize service (async setup)"""
        self.start_time = time.time()
        
        # Check hub connectivity
        connected = await self.hub_client.check_health()
        if connected:
            print("✅ Connected to BRIDGE Hub")
        else:
            print("⚠️  Hub not available - will retry on fingerprint send")

    async def process_transaction(self, transaction: Transaction) -> None:
        """
        Process single transaction

        Args:
            transaction: Transaction to process
        """
        try:
            self.transactions_processed += 1
            
            # Extract features
            features = self.feature_extractor.extract_features(transaction)
            
            # Calculate risk score
            risk_score = self.risk_scorer.calculate_risk_score(features)
            
            # Determine severity based on score
            if risk_score.score >= 80:
                severity = "CRITICAL"
            elif risk_score.score >= 60:
                severity = "HIGH"
            elif risk_score.score >= 40:
                severity = "MEDIUM"
            else:
                severity = "LOW"
            
            # Classify pattern
            pattern = self.pattern_classifier.classify(risk_score)
            
            # Generate fingerprint
            fingerprint = self.fingerprint_generator.generate_fingerprint(
                pattern=pattern,
                severity=severity,
                timestamp=transaction.timestamp
            )
            
            # Send to hub
            success = await self.hub_client.send_fingerprint(
                fingerprint=fingerprint,
                severity=severity,
                timestamp=transaction.timestamp.isoformat()
            )
            
            if success:
                self.fingerprints_sent += 1
                print(f"Entity B fingerprint emitted: {fingerprint} (pattern: {pattern.value}, severity: {severity})")
            else:
                print(f"Failed to send fingerprint for transaction {transaction.transaction_id}")

        except Exception as e:
            print(f"Error processing transaction {transaction.transaction_id}: {e}")

    async def run_stream(self, interval_seconds: float = 2.0, duration_seconds: float = None):
        """
        Run transaction stream processing

        Args:
            interval_seconds: Time between transactions
            duration_seconds: Optional duration limit
        """
        print(f"🟦 Entity B starting transaction stream...")

        generator = TransactionStreamGenerator(self.entity_id, seed=67890)  # Different seed

        start = time.time()

        async for transaction in generator.generate_stream(interval_seconds):
            await self.process_transaction(transaction)

            # Check duration limit
            if duration_seconds and (time.time() - start) >= duration_seconds:
                break

    def get_stats(self) -> dict:
        """Get service statistics"""
        elapsed = time.time() - self.start_time if self.start_time else 0

        return {
            "entity_id": self.entity_id,
            "transactions_processed": self.transactions_processed,
            "fingerprints_sent": self.fingerprints_sent,
            "elapsed_seconds": round(elapsed, 2),
            "transactions_per_second": round(self.transactions_processed / elapsed, 2) if elapsed > 0 else 0
        }


async def main():
    """Run Entity B service"""
    service = EntityBService()
    await service.initialize()

    try:
        # Run for 60 seconds
        await service.run_stream(interval_seconds=2.0, duration_seconds=60)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Entity B...")

    stats = service.get_stats()
    print(f"\n📊 Entity B Final Stats:")
    print(f"   Transactions Processed: {stats['transactions_processed']}")
    print(f"   Duration: {stats['elapsed_seconds']}s")
    print(f"   Rate: {stats['transactions_per_second']} txn/s")


if __name__ == "__main__":
    asyncio.run(main())
>>>>>>> 1a6d17f9aa0f61a18b8fc3da56965e00e5b43dc1
