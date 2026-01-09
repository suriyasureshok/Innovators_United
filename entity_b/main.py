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
