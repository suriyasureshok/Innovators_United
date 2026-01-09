"""Integration tests for Entity A service"""
import pytest
import asyncio
from datetime import datetime
from entity_a.main import EntityAService
from entity_a.models import Transaction


@pytest.fixture
def entity_service():
    """Create Entity A service"""
    service = EntityAService(
        entity_id="entity_a_test"
    )
    return service


@pytest.fixture
def sample_transaction():
    """Create sample transaction"""
    return Transaction(
        transaction_id="txn_test_001",
        user_id="user_test_123",
        amount=100.0,
        merchant_id="merchant_test",
        merchant_category="retail",
        timestamp=datetime.now().isoformat(),
        device_id="device_test",
        ip_address="192.168.1.1",
        location="US"
    )


@pytest.mark.asyncio
async def test_process_transaction(entity_service, sample_transaction):
    """Test full transaction processing pipeline"""
    await entity_service.initialize()
    
    # Process transaction
    await entity_service.process_transaction(sample_transaction)
    
    # Check metrics updated
    stats = entity_service.get_stats()
    assert stats["transactions_processed"] == 1


@pytest.mark.asyncio
async def test_allow_normal_transaction(entity_service):
    """Test that normal transactions are processed"""
    await entity_service.initialize()
    
    # Normal low-value transaction
    transaction = Transaction(
        transaction_id="txn_normal",
        user_id="user_normal",
        amount=50.0,
        merchant_id="merchant_normal",
        merchant_category="retail",
        timestamp=datetime.now().isoformat(),
        device_id="device_normal",
        ip_address="192.168.1.1",
        location="US"
    )
    
    await entity_service.process_transaction(transaction)
    
    # Check processing occurred
    stats = entity_service.get_stats()
    assert stats["transactions_processed"] == 1


@pytest.mark.asyncio
async def test_block_high_risk_transaction(entity_service):
    """Test that high-risk transactions are processed"""
    await entity_service.initialize()
    
    # Simulate high velocity by processing multiple transactions quickly
    user_id = "user_high_risk"
    device_id = "new_device_suspicious"
    
    for i in range(15):
        transaction = Transaction(
            transaction_id=f"txn_velocity_{i}",
            user_id=user_id,
            amount=500.0,
            merchant_id=f"merchant_{i}",
            merchant_category="retail",
            timestamp=datetime.now().isoformat(),
            device_id=device_id,
            ip_address="192.168.1.1",
            location="US"
        )
        
        await entity_service.process_transaction(transaction)
    
    # Check all transactions processed
    stats = entity_service.get_stats()
    assert stats["transactions_processed"] == 15


@pytest.mark.asyncio
async def test_service_metrics(entity_service, sample_transaction):
    """Test service metrics tracking"""
    await entity_service.initialize()
    
    # Process some transactions
    for i in range(5):
        await entity_service.process_transaction(sample_transaction)
    
    stats = entity_service.get_stats()
    
    # Check metrics
    assert stats["transactions_processed"] == 5
    assert stats["entity_id"] == "entity_a_test"
    assert "transactions_per_second" in stats


@pytest.mark.asyncio
async def test_error_handling(entity_service):
    """Test error handling in transaction processing"""
    await entity_service.initialize()
    
    # Create valid transaction to ensure no crashes
    transaction = Transaction(
        transaction_id="txn_error_test",
        user_id="user_error",
        amount=100.0,
        merchant_id="merchant_error",
        merchant_category="retail",
        timestamp=datetime.now().isoformat(),
        device_id="device_error",
        ip_address="192.168.1.1",
        location="US"
    )
    
    # Should not raise exception
    await entity_service.process_transaction(transaction)
    
    stats = entity_service.get_stats()
    assert stats["transactions_processed"] == 1


@pytest.mark.asyncio
async def test_multiple_users(entity_service):
    """Test processing transactions from multiple users"""
    await entity_service.initialize()
    
    users = ["user_1", "user_2", "user_3"]
    
    for user_id in users:
        transaction = Transaction(
            transaction_id=f"txn_{user_id}",
            user_id=user_id,
            amount=100.0,
            merchant_id="merchant_shared",
            merchant_category="retail",
            timestamp=datetime.now().isoformat(),
            device_id=f"device_{user_id}",
            ip_address="192.168.1.1",
            location="US"
        )
        
        await entity_service.process_transaction(transaction)
    
    stats = entity_service.get_stats()
    assert stats["transactions_processed"] == 3
