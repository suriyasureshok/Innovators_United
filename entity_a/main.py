"""
Entity A - Main Fraud Detection Service
Complete transaction processing pipeline with BRIDGE Hub integration
"""
import asyncio
import logging
from typing import Optional
from datetime import datetime

from entity_a.models import Transaction, Decision, DecisionAction
from entity_a.stream import TransactionStreamGenerator
from entity_a.risk_engine import FeatureExtractor, RiskScorer
from entity_a.pattern_classifier import PatternClassifier
from entity_a.fingerprint import FingerprintGenerator
from entity_a.decision import DecisionEngine, ExplanationGenerator
from entity_a.hub_client import BridgeHubClient
from bridge_hub.models import Advisory

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EntityAService:
    """
    Entity A Fraud Detection Service
    
    Complete pipeline:
    1. Receive transaction from stream
    2. Extract features
    3. Calculate risk score
    4. Classify pattern
    5. Generate fingerprint
    6. Send to BRIDGE Hub (async)
    7. Check for advisories
    8. Make final decision
    9. Generate explanation
    """
    
    def __init__(
        self,
        entity_id: str = "entity_a",
        hub_url: str = "http://localhost:8000",
        hub_api_key: str = "entity-a-key-123",
        enable_hub: bool = True
    ):
        """
        Initialize Entity A service
        
        Args:
            entity_id: Entity identifier
            hub_url: BRIDGE Hub URL
            hub_api_key: API key for Hub authentication
            enable_hub: Whether to use BRIDGE Hub (set False for standalone testing)
        """
        self.entity_id = entity_id
        self.enable_hub = enable_hub
        
        # Initialize components
        self.feature_extractor = FeatureExtractor()
        self.risk_scorer = RiskScorer()
        self.pattern_classifier = PatternClassifier()
        self.fingerprint_generator = FingerprintGenerator(entity_id=entity_id)
        self.decision_engine = DecisionEngine()
        self.explanation_generator = ExplanationGenerator()
        
        # Hub client (optional)
        self.hub_client = None
        if enable_hub:
            self.hub_client = BridgeHubClient(
                hub_url=hub_url,
                api_key=hub_api_key,
                entity_id=entity_id
            )
        
        # Metrics
        self.transactions_processed = 0
        self.transactions_allowed = 0
        self.transactions_step_up = 0
        self.transactions_blocked = 0
        self.hub_advisories_used = 0
        
        logger.info(f"Initialized EntityAService (entity_id={entity_id}, hub_enabled={enable_hub})")
    
    async def initialize(self):
        """Initialize service (async setup)"""
        if self.hub_client:
            # Check Hub connectivity
            await self.hub_client.check_health()
            
            # Start advisory polling in background
            asyncio.create_task(
                self.hub_client.poll_advisories_continuously(
                    callback=self._handle_advisory,
                    interval_seconds=10.0
                )
            )
            
            logger.info("Started BRIDGE Hub advisory polling")
    
    async def process_transaction(
        self,
        transaction: Transaction
    ) -> Decision:
        """
        Process single transaction through full pipeline
        
        Args:
            transaction: Transaction to process
            
        Returns:
            Decision with action and explanation
        """
        start_time = datetime.now()
        
        logger.info(f"Processing transaction {transaction.transaction_id} "
                   f"(user={transaction.user_id}, amount=${transaction.amount})")
        
        try:
            # 1. Extract features
            features = self.feature_extractor.extract_features(transaction)
            logger.debug(f"Extracted {len(features)} features")
            
            # 2. Calculate risk score
            risk_score = self.risk_scorer.calculate_risk_score(features)
            logger.info(f"Risk score: {risk_score.score:.1f} "
                       f"(signals: {len(risk_score.signals)})")
            
            # 3. Classify pattern
            pattern = self.pattern_classifier.classify(risk_score.signals)
            logger.info(f"Pattern classified: {pattern}")
            
            # 4. Generate fingerprint
            fingerprint = self.fingerprint_generator.generate_fingerprint(
                pattern=pattern,
                severity=self._get_severity(risk_score.score),
                timestamp=transaction.timestamp
            )
            logger.debug(f"Generated fingerprint: {fingerprint}")
            
            # 5. Send to BRIDGE Hub (non-blocking)
            if self.hub_client:
                asyncio.create_task(
                    self.hub_client.send_fingerprint(
                        fingerprint=fingerprint,
                        severity=self._get_severity(risk_score.score),
                        timestamp=transaction.timestamp
                    )
                )
            
            # 6. Check for existing advisory
            advisory = None
            if self.hub_client:
                advisory = await self.hub_client.get_advisory_for_fingerprint(fingerprint)
                
                if advisory:
                    logger.info(f"Found matching advisory: {advisory.advisory_id} "
                               f"(confidence={advisory.confidence})")
                    self.hub_advisories_used += 1
            
            # 7. Make decision
            decision = self.decision_engine.make_decision(
                transaction_id=transaction.transaction_id,
                risk_score=risk_score,
                advisory=advisory
            )
            
            # 8. Generate explanation
            explanation = self.explanation_generator.generate_explanation(
                transaction_id=transaction.transaction_id,
                risk_score=risk_score,
                decision=decision,
                advisory=advisory
            )
            
            # Update decision with explanation
            decision = Decision(
                transaction_id=decision.transaction_id,
                action=decision.action,
                risk_score=decision.risk_score,
                adjusted_score=decision.adjusted_score,
                adjustment_factors=decision.adjustment_factors,
                advisory_applied=decision.advisory_applied,
                timestamp=decision.timestamp,
                explanation=explanation
            )
            
            # Update metrics
            self._update_metrics(decision)
            
            # Log processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"Decision: {decision.action} (time={processing_time:.3f}s)")
            
            self.transactions_processed += 1
            
            return decision
            
        except Exception as e:
            logger.error(f"Error processing transaction {transaction.transaction_id}: {e}")
            
            # Fail-safe: BLOCK on error
            return Decision(
                transaction_id=transaction.transaction_id,
                action=DecisionAction.BLOCK,
                risk_score=100.0,
                adjusted_score=100.0,
                adjustment_factors=["error_failsafe"],
                advisory_applied=False,
                explanation=f"Transaction blocked due to processing error: {str(e)}"
            )
    
    async def _handle_advisory(self, advisory: Advisory):
        """
        Handle new advisory from Hub
        
        Args:
            advisory: Advisory received from Hub
        """
        logger.info(f"Received advisory {advisory.advisory_id}: {advisory.summary} "
                   f"(confidence={advisory.confidence}, severity={advisory.severity})")
        
        # Advisory is automatically applied when get_advisory_for_fingerprint is called
        # This callback is for logging/monitoring/alerting
    
    def _get_severity(self, risk_score: float) -> str:
        """Map risk score to severity level"""
        if risk_score >= 80:
            return "CRITICAL"
        elif risk_score >= 60:
            return "HIGH"
        elif risk_score >= 40:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _update_metrics(self, decision: Decision):
        """Update decision metrics"""
        if decision.action == DecisionAction.ALLOW:
            self.transactions_allowed += 1
        elif decision.action == DecisionAction.STEP_UP:
            self.transactions_step_up += 1
        elif decision.action == DecisionAction.BLOCK:
            self.transactions_blocked += 1
    
    def get_stats(self) -> dict:
        """Get service statistics"""
        stats = {
            "entity_id": self.entity_id,
            "transactions_processed": self.transactions_processed,
            "transactions_allowed": self.transactions_allowed,
            "transactions_step_up": self.transactions_step_up,
            "transactions_blocked": self.transactions_blocked,
            "hub_advisories_used": self.hub_advisories_used,
            "hub_enabled": self.enable_hub
        }
        
        # Add Hub client stats
        if self.hub_client:
            stats["hub_client"] = self.hub_client.get_client_stats()
        
        return stats
    
    async def close(self):
        """Cleanup resources"""
        if self.hub_client:
            await self.hub_client.close()
        logger.info("Closed EntityAService")


async def run_demo():
    """
    Run demonstration of Entity A service
    
    Processes stream of transactions and shows decisions
    """
    logger.info("=" * 80)
    logger.info("Entity A Fraud Detection Service - Demo Mode")
    logger.info("=" * 80)
    
    # Initialize service
    service = EntityAService(
        entity_id="entity_a",
        hub_url="http://localhost:8000",
        enable_hub=True  # Set False to run without Hub
    )
    
    await service.initialize()
    
    # Create transaction stream
    stream_generator = TransactionStreamGenerator(
        fraud_probability=0.25,  # 25% suspicious transactions
        seed=42
    )
    
    try:
        # Process 20 transactions
        logger.info("\nProcessing transaction stream...")
        logger.info("-" * 80)
        
        transaction_count = 0
        async for transaction in stream_generator.generate_stream():
            # Process transaction
            decision = await service.process_transaction(transaction)
            
            # Print short summary
            print(f"\n[{transaction_count + 1}] Transaction {transaction.transaction_id}")
            print(f"    User: {transaction.user_id} | Amount: ${transaction.amount:.2f}")
            print(f"    Decision: {decision.action.value} | Risk: {decision.risk_score:.1f}")
            print(f"    Reason: {decision.explanation.split(chr(10))[0] if decision.explanation else 'N/A'}")
            
            transaction_count += 1
            
            if transaction_count >= 20:
                break
            
            # Small delay for readability
            await asyncio.sleep(0.1)
        
        # Print final stats
        logger.info("\n" + "=" * 80)
        logger.info("Demo Complete - Final Statistics")
        logger.info("=" * 80)
        
        stats = service.get_stats()
        print(f"\nTransactions Processed: {stats['transactions_processed']}")
        print(f"  ✓ Allowed: {stats['transactions_allowed']}")
        print(f"  ⚠ Step-Up: {stats['transactions_step_up']}")
        print(f"  ✗ Blocked: {stats['transactions_blocked']}")
        print(f"\nBRIDGE Hub Integration:")
        print(f"  Advisories Used: {stats['hub_advisories_used']}")
        
        if 'hub_client' in stats:
            hc = stats['hub_client']
            print(f"  Fingerprints Sent: {hc['fingerprints_sent']}")
            print(f"  Hub Connected: {hc['connected']}")
    
    finally:
        # Cleanup
        await service.close()
        logger.info("\nDemo finished")


if __name__ == "__main__":
    # Run demo
    asyncio.run(run_demo())
