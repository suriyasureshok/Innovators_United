"""
Entity A - Main Transaction Processing Service
Asynchronous transaction stream consumer
"""
import asyncio
import time
from datetime import datetime

from entity_a.stream import TransactionStreamGenerator
from entity_a.models import Transaction
from entity_a.risk_engine import FeatureExtractor, RiskScorer
from entity_a.pattern_classifier import PatternClassifier
from entity_a.fingerprint import FingerprintGenerator
from entity_a.hub_client import BridgeHubClient


class EntityAService:
    """
    Entity A Transaction Processing Service

    Continuously consumes transactions from stream
    """

    def __init__(self, entity_id: str = "entity_a"):
        """
        Initialize Entity A service

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
                print(f"Entity A fingerprint emitted: {fingerprint} (pattern: {pattern.value}, severity: {severity})")
            else:
                print(f"Failed to send fingerprint for transaction {transaction.transaction_id}")

        except Exception as e:
            print(f"Error processing transaction {transaction.transaction_id}: {e}")

    def get_stats(self) -> dict:
        """Get service statistics"""
        elapsed_time = time.time() - self.start_time if self.start_time else 0
        tps = self.transactions_processed / elapsed_time if elapsed_time > 0 else 0

        stats = {
            "entity_id": self.entity_id,
            "transactions_processed": self.transactions_processed,
            "fingerprints_sent": self.fingerprints_sent,
            "elapsed_time_seconds": elapsed_time,
            "transactions_per_second": tps
        }

        return stats

    async def close(self):
        """Cleanup resources"""
        pass


async def main():
    """
    Main async loop that continuously consumes transactions from stream
    """
    print("=" * 80)
    print("Entity A Transaction Processing Service")
    print("=" * 80)

    # Initialize service
    service = EntityAService(entity_id="entity_a")
    await service.initialize()

    # Create transaction stream
    stream_generator = TransactionStreamGenerator(entity_id="entity_a", seed=42)

    print("\nStarting transaction processing...")
    print("Press Ctrl+C to stop\n")

    try:
        # Process transactions continuously
        async for transaction in stream_generator.generate_stream(interval_seconds=2.0):
            try:
                await service.process_transaction(transaction)

                # Print status every 10 transactions
                if service.transactions_processed % 10 == 0:
                    stats = service.get_stats()
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                          f"Processed: {stats['transactions_processed']} | "
                          f"TPS: {stats['transactions_per_second']:.2f}")

            except Exception as e:
                # Handle per-transaction errors without crashing
                print(f"Error processing transaction: {e}")
                continue

    except KeyboardInterrupt:
        print("\n\nShutdown signal received...")

    finally:
        # Cleanup
        await service.close()

        # Print final stats
        print("\n" + "=" * 80)
        print("Final Statistics")
        print("=" * 80)

        stats = service.get_stats()
        print(f"Transactions Processed: {stats['transactions_processed']}")
        print(f"Elapsed Time: {stats['elapsed_time_seconds']:.1f}s")
        print(f"Average TPS: {stats['transactions_per_second']:.2f}")
        print("\nService stopped")


if __name__ == "__main__":
    asyncio.run(main())
