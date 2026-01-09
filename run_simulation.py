"""
SYNAPSE-FI Full System Simulation
Runs Entity A, Entity B, and BRIDGE Hub together for realistic fraud detection simulation
"""
import asyncio
import time
from datetime import datetime
from typing import Dict
import random

# Entity A imports
from entity_a.stream import TransactionStreamGenerator as StreamA
from entity_a.fingerprint import FingerprintGenerator as FingerprintGenA
from entity_a.risk_engine import FeatureExtractor, RiskScorer
from entity_a.pattern_classifier import PatternClassifier as ClassifierA
from entity_a.decision import DecisionEngine as DecisionA
from entity_a.hub_client import BridgeHubClient as HubClientA

# Entity B imports
from entity_b.stream import TransactionStreamGenerator as StreamB
from entity_b.fingerprint import FingerprintGenerator as FingerprintGenB
from entity_b.risk_engine import FeatureExtractor as FeatureExtractorB, RiskScorer as RiskScorerB
from entity_b.pattern_classifier import PatternClassifier as ClassifierB
from entity_b.decision import DecisionEngine as DecisionB
from entity_b.hub_client import BridgeHubClient as HubClientB


class SimulationController:
    """Controls the full SYNAPSE-FI simulation with multiple entities"""
    
    def __init__(self, hub_url: str = "http://localhost:8000"):
        self.hub_url = hub_url
        self.entity_a_stats = {"processed": 0, "fingerprints": 0, "fraud_detected": 0}
        self.entity_b_stats = {"processed": 0, "fingerprints": 0, "fraud_detected": 0}
        self.start_time = None
        
    async def run_entity_a(self, duration_seconds: int = 60):
        """
        Run Entity A fraud detection pipeline
        
        Args:
            duration_seconds: How long to run simulation
        """
        print("🔵 Starting Entity A...")
        
        # Initialize components
        stream = StreamA(entity_id="entity_a", seed=12345)
        fingerprinter = FingerprintGenA(entity_id="entity_a")
        feature_extractor = FeatureExtractor()
        risk_scorer = RiskScorer()
        classifier = ClassifierA()
        decision_engine = DecisionA()
        hub_client = HubClientA(hub_url=self.hub_url, api_key="dev-key-change-in-production", entity_id="entity_a")
        
        start = time.time()
        
        print("🔵 Entity A processing transactions...")
        
        async for txn in stream.generate_stream(interval_seconds=1.5):
            # Check duration
            if time.time() - start >= duration_seconds:
                break
                
            try:
                # Process transaction
                self.entity_a_stats["processed"] += 1
                
                # Extract features and calculate risk score
                features = feature_extractor.extract_features(txn)
                risk_score = risk_scorer.calculate_risk_score(features)
                
                # Pattern classification
                pattern = classifier.classify(risk_score)
                
                # Make decision
                decision = decision_engine.make_decision(txn.transaction_id, risk_score)
                
                # FOR DEMO: Submit every transaction to ensure continuous data flow
                # In production, would use risk-based filtering
                should_submit = True
                
                if should_submit:
                    # Generate fingerprint with correct parameters
                    severity = "CRITICAL" if risk_score.score >= 70 else "HIGH" if risk_score.score >= 50 else "MEDIUM" if risk_score.score >= 30 else "LOW"
                    fingerprint_hash = fingerprinter.generate_fingerprint(
                        pattern=pattern,
                        severity=severity,
                        timestamp=txn.timestamp
                    )
                    
                    try:
                        # send_fingerprint expects (fingerprint, severity, timestamp) not RiskFingerprint object
                        await hub_client.send_fingerprint(
                            fingerprint=fingerprint_hash,
                            severity=severity,
                            timestamp=txn.timestamp.isoformat() if hasattr(txn.timestamp, 'isoformat') else str(txn.timestamp)
                        )
                        self.entity_a_stats["fingerprints"] += 1
                        
                        if decision.action in ["BLOCK", "REVIEW"]:
                            self.entity_a_stats["fraud_detected"] += 1
                            
                    except Exception as e:
                        # Hub might not be running, continue anyway
                        pass
                
                # Print status every 10 transactions
                if self.entity_a_stats["processed"] % 10 == 0:
                    elapsed = time.time() - start
                    rate = self.entity_a_stats["processed"] / elapsed
                    print(f"🔵 Entity A: {self.entity_a_stats['processed']} txns | "
                          f"{self.entity_a_stats['fingerprints']} fingerprints | "
                          f"{self.entity_a_stats['fraud_detected']} fraud | "
                          f"{rate:.1f} txn/s")
                    
            except Exception as e:
                print(f"❌ Entity A error: {e}")
                continue
                
        print(f"✅ Entity A completed")
        
    async def run_entity_b(self, duration_seconds: int = 60):
        """
        Run Entity B fraud detection pipeline
        
        Args:
            duration_seconds: How long to run simulation
        """
        print("🟦 Starting Entity B...")
        
        # Initialize components
        stream = StreamB(entity_id="entity_b", seed=67890)
        fingerprinter = FingerprintGenB(entity_id="entity_b")
        feature_extractor = FeatureExtractorB()
        risk_scorer = RiskScorerB()
        classifier = ClassifierB()
        decision_engine = DecisionB()
        hub_client = HubClientB(hub_url=self.hub_url, api_key="dev-key-change-in-production", entity_id="entity_b")
        
        start = time.time()
        
        print("🟦 Entity B processing transactions...")
        
        async for txn in stream.generate_stream(interval_seconds=2.0):
            # Check duration
            if time.time() - start >= duration_seconds:
                break
                
            try:
                # Process transaction
                self.entity_b_stats["processed"] += 1
                
                # Extract features and calculate risk score
                features = feature_extractor.extract_features(txn)
                risk_score = risk_scorer.calculate_risk_score(features)
                
                # Pattern classification
                pattern = classifier.classify(risk_score)
                
                # Make decision
                decision = decision_engine.make_decision(txn.transaction_id, risk_score)
                
                # FOR DEMO: Submit every transaction to ensure continuous data flow
                # In production, would use risk-based filtering
                should_submit = True
                
                if should_submit:
                    # Generate fingerprint with correct parameters
                    severity = "CRITICAL" if risk_score.score >= 70 else "HIGH" if risk_score.score >= 50 else "MEDIUM" if risk_score.score >= 30 else "LOW"
                    fingerprint_hash = fingerprinter.generate_fingerprint(
                        pattern=pattern,
                        severity=severity,
                        timestamp=txn.timestamp
                    )
                    
                    try:
                        # send_fingerprint expects (fingerprint, severity, timestamp) not RiskFingerprint object
                        await hub_client.send_fingerprint(
                            fingerprint=fingerprint_hash,
                            severity=severity,
                            timestamp=txn.timestamp.isoformat() if hasattr(txn.timestamp, 'isoformat') else str(txn.timestamp)
                        )
                        self.entity_b_stats["fingerprints"] += 1
                        
                        if decision.action in ["BLOCK", "REVIEW"]:
                            self.entity_b_stats["fraud_detected"] += 1
                            
                    except Exception as e:
                        # Hub might not be running, continue anyway
                        pass
                
                # Print status every 10 transactions
                if self.entity_b_stats["processed"] % 10 == 0:
                    elapsed = time.time() - start
                    rate = self.entity_b_stats["processed"] / elapsed
                    print(f"🟦 Entity B: {self.entity_b_stats['processed']} txns | "
                          f"{self.entity_b_stats['fingerprints']} fingerprints | "
                          f"{self.entity_b_stats['fraud_detected']} fraud | "
                          f"{rate:.1f} txn/s")
                    
            except Exception as e:
                print(f"❌ Entity B error: {e}")
                continue
                
        print(f"✅ Entity B completed")
        
    async def monitor_hub(self, duration_seconds: int):
        """
        Monitor BRIDGE Hub statistics
        
        Args:
            duration_seconds: How long to monitor
        """
        import httpx
        
        await asyncio.sleep(5)  # Wait for entities to start
        
        start = time.time()
        
        print("📊 Starting Hub monitoring...")
        
        while time.time() - start < duration_seconds - 5:
            try:
                async with httpx.AsyncClient() as client:
                    # Get hub stats
                    response = await client.get(f"{self.hub_url}/stats", timeout=5.0)
                    
                    if response.status_code == 200:
                        stats = response.json()
                        
                        print(f"\n{'='*80}")
                        print(f"🌉 BRIDGE Hub Status - {datetime.now().strftime('%H:%M:%S')}")
                        print(f"{'='*80}")
                        print(f"  Total Observations: {stats.get('total_observations', 0)}")
                        print(f"  Unique Entities: {stats.get('unique_entities', 0)}")
                        print(f"  Active Patterns: {stats.get('active_patterns', 0)}")
                        print(f"  Correlations: {stats.get('correlation_count', 0)}")
                        print(f"  Advisories: {stats.get('advisory_count', 0)}")
                        
                        # Get advisories
                        adv_response = await client.get(f"{self.hub_url}/advisories", timeout=5.0)
                        if adv_response.status_code == 200:
                            advisories = adv_response.json()
                            if advisories:
                                print(f"\n  🚨 Recent Advisories:")
                                for adv in advisories[:3]:
                                    print(f"    • {adv.get('severity', 'UNKNOWN')}: {adv.get('summary', 'N/A')}")
                        
                        print(f"{'='*80}\n")
                        
            except Exception as e:
                print(f"⚠️  Hub monitoring error: {e}")
                
            await asyncio.sleep(15)  # Monitor every 15 seconds
            
    def print_final_summary(self, elapsed_seconds: float):
        """Print final simulation summary"""
        print("\n" + "="*80)
        print("🎯 SIMULATION COMPLETE - Final Summary")
        print("="*80)
        print(f"\n⏱️  Duration: {elapsed_seconds:.1f} seconds")
        
        print(f"\n🔵 Entity A Statistics:")
        print(f"   Transactions Processed: {self.entity_a_stats['processed']}")
        print(f"   Fingerprints Submitted: {self.entity_a_stats['fingerprints']}")
        print(f"   Fraud Cases Detected: {self.entity_a_stats['fraud_detected']}")
        print(f"   Submission Rate: {(self.entity_a_stats['fingerprints']/self.entity_a_stats['processed']*100):.1f}%")
        
        print(f"\n🟦 Entity B Statistics:")
        print(f"   Transactions Processed: {self.entity_b_stats['processed']}")
        print(f"   Fingerprints Submitted: {self.entity_b_stats['fingerprints']}")
        print(f"   Fraud Cases Detected: {self.entity_b_stats['fraud_detected']}")
        print(f"   Submission Rate: {(self.entity_b_stats['fingerprints']/self.entity_b_stats['processed']*100):.1f}%")
        
        total_txns = self.entity_a_stats['processed'] + self.entity_b_stats['processed']
        total_fingerprints = self.entity_a_stats['fingerprints'] + self.entity_b_stats['fingerprints']
        total_fraud = self.entity_a_stats['fraud_detected'] + self.entity_b_stats['fraud_detected']
        
        print(f"\n🌐 Federated Network Totals:")
        print(f"   Total Transactions: {total_txns}")
        print(f"   Total Fingerprints: {total_fingerprints}")
        print(f"   Total Fraud Detected: {total_fraud}")
        print(f"   Network TPS: {total_txns/elapsed_seconds:.2f}")
        print(f"   Fraud Rate: {(total_fraud/total_txns*100):.2f}%")
        
        print("\n" + "="*80 + "\n")
        
    async def run_simulation(self, duration_seconds: int = 60):
        """
        Run full system simulation
        
        Args:
            duration_seconds: How long to run the simulation
        """
        print("="*80)
        print("🚀 SYNAPSE-FI Full System Simulation")
        print("="*80)
        print(f"\n📋 Configuration:")
        print(f"   Duration: {duration_seconds} seconds")
        print(f"   Hub URL: {self.hub_url}")
        print(f"   Entities: Entity A, Entity B")
        print("\n" + "="*80 + "\n")
        
        self.start_time = time.time()
        
        # Check if hub is running
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.hub_url}/health", timeout=5.0)
                if response.status_code == 200:
                    print("✅ BRIDGE Hub is running and healthy\n")
                else:
                    print("⚠️  Warning: Hub returned unexpected status\n")
        except Exception as e:
            print(f"❌ Warning: Cannot reach BRIDGE Hub at {self.hub_url}")
            print(f"   Error: {e}")
            print("   Entities will run but won't submit fingerprints\n")
            
        # Run all components concurrently
        try:
            await asyncio.gather(
                self.run_entity_a(duration_seconds),
                self.run_entity_b(duration_seconds),
                self.monitor_hub(duration_seconds)
            )
        except KeyboardInterrupt:
            print("\n\n🛑 Simulation interrupted by user")
        except Exception as e:
            print(f"\n❌ Simulation error: {e}")
            
        elapsed = time.time() - self.start_time
        self.print_final_summary(elapsed)


async def main():
    """Main entry point for simulation"""
    
    # Parse command line arguments
    import sys
    
    duration = 60  # Default 60 seconds
    hub_url = "http://localhost:8000"
    
    if len(sys.argv) > 1:
        try:
            duration = int(sys.argv[1])
        except ValueError:
            print(f"Invalid duration: {sys.argv[1]}, using default of 60 seconds")
            
    if len(sys.argv) > 2:
        hub_url = sys.argv[2]
        
    # Create and run simulation
    controller = SimulationController(hub_url=hub_url)
    
    try:
        await controller.run_simulation(duration_seconds=duration)
    except KeyboardInterrupt:
        print("\n\n🛑 Shutdown requested")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("\n" + "="*80)
    print("SYNAPSE-FI - Privacy-Preserving Federated Fraud Detection")
    print("Full System Simulation with Entity A + Entity B + BRIDGE Hub")
    print("="*80 + "\n")
    
    asyncio.run(main())
