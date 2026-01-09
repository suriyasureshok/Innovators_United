<<<<<<< HEAD
"""
Risk Scoring Engine
Feature extraction and risk scoring for fraud detection
"""
from typing import Dict, List, Tuple
from collections import deque, defaultdict
from datetime import datetime, timedelta
import logging

from .models import Transaction, RiskScore

logger = logging.getLogger(__name__)


class FeatureExtractor:
    """Extract behavioral features from transactions"""
    
    def __init__(self, time_window_seconds: int = 300):
        """
        Initialize feature extractor
        
        Args:
            time_window_seconds: Time window for velocity calculations (default 5 minutes)
        """
        self.time_window = timedelta(seconds=time_window_seconds)
        
        # Maintain recent transaction history per user
        self.user_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.device_history: Dict[str, datetime] = {}
        self.user_amounts: Dict[str, List[float]] = defaultdict(list)
        
        logger.info(f"Initialized FeatureExtractor with time_window={time_window_seconds}s")
    
    def extract_features(self, txn: Transaction) -> Dict[str, any]:
        """
        Extract risk-relevant features from transaction
        
        Args:
            txn: Transaction to analyze
            
        Returns:
            Dictionary of extracted features
        """
        features = {}
        
        # Velocity Features
        features['velocity_count'] = self._calculate_velocity(txn.user_id, txn.timestamp)
        features['velocity_amount'] = self._calculate_amount_velocity(txn.user_id, txn.timestamp)
        
        # Device Features
        features['device_age_days'] = self._get_device_age(txn.device_id, txn.timestamp)
        features['is_new_device'] = features['device_age_days'] < 1
        features['is_unknown_device'] = 'new' in txn.device_id.lower()
        
        # Amount Features
        features['amount'] = txn.amount
        features['is_high_value'] = txn.amount > 1000
        features['is_very_high_value'] = txn.amount > 2000
        features['is_low_amount'] = txn.amount < 50
        features['amount_deviation'] = self._calculate_amount_deviation(txn.user_id, txn.amount)
        
        # Temporal Features
        features['hour_of_day'] = txn.timestamp.hour
        features['is_night_transaction'] = features['hour_of_day'] < 6 or features['hour_of_day'] > 22
        features['is_weekend'] = txn.timestamp.weekday() >= 5
        
        # Merchant Features
        features['merchant_category'] = txn.merchant_category
        features['is_high_risk_category'] = txn.merchant_category in ['electronics', 'travel', 'entertainment']
        features['is_suspicious_merchant'] = 'suspicious' in txn.merchant_id.lower()
        
        # Location Features
        features['location'] = txn.location
        features['location_shift'] = self._detect_location_shift(txn.user_id, txn.location)
        
        # IP Features
        features['is_suspicious_ip'] = self._is_suspicious_ip(txn.ip_address)
        
        # Update history for future feature extraction
        self._update_history(txn)
        
        return features
    
    def _calculate_velocity(self, user_id: str, current_time: datetime) -> int:
        """
        Count transactions in time window
        
        Args:
            user_id: User identifier
            current_time: Current transaction timestamp
            
        Returns:
            Number of transactions in time window
        """
        if user_id not in self.user_history:
            return 0
        
        cutoff = current_time - self.time_window
        recent = [t for t in self.user_history[user_id] if t['timestamp'] > cutoff]
        return len(recent)
    
    def _calculate_amount_velocity(self, user_id: str, current_time: datetime) -> float:
        """
        Calculate total amount spent in time window
        
        Args:
            user_id: User identifier
            current_time: Current transaction timestamp
            
        Returns:
            Total amount spent in window
        """
        if user_id not in self.user_history:
            return 0.0
        
        cutoff = current_time - self.time_window
        recent = [t for t in self.user_history[user_id] if t['timestamp'] > cutoff]
        return sum(t['amount'] for t in recent)
    
    def _get_device_age(self, device_id: str, current_time: datetime) -> float:
        """
        Get age of device in days
        
        Args:
            device_id: Device identifier
            current_time: Current transaction timestamp
            
        Returns:
            Device age in days
        """
        if device_id not in self.device_history:
            self.device_history[device_id] = current_time
            return 0.0
        
        first_seen = self.device_history[device_id]
        age = current_time - first_seen
        return age.total_seconds() / 86400  # Convert to days
    
    def _calculate_amount_deviation(self, user_id: str, amount: float) -> float:
        """
        Calculate how much this amount deviates from user's normal spending
        
        Args:
            user_id: User identifier
            amount: Transaction amount
            
        Returns:
            Standard deviations from mean (0 if insufficient history)
        """
        if user_id not in self.user_amounts or len(self.user_amounts[user_id]) < 3:
            return 0.0
        
        amounts = self.user_amounts[user_id]
        mean = sum(amounts) / len(amounts)
        
        if len(amounts) < 2:
            return 0.0
        
        variance = sum((x - mean) ** 2 for x in amounts) / (len(amounts) - 1)
        std_dev = variance ** 0.5
        
        if std_dev == 0:
            return 0.0
        
        return abs(amount - mean) / std_dev
    
    def _detect_location_shift(self, user_id: str, location: str) -> bool:
        """
        Detect if user's location changed significantly
        
        Args:
            user_id: User identifier
            location: Current location
            
        Returns:
            True if location shifted from recent transactions
        """
        if user_id not in self.user_history or len(self.user_history[user_id]) < 5:
            return False
        
        # Get recent locations
        recent = list(self.user_history[user_id])[-5:]
        recent_locations = [t['location'] for t in recent]
        
        # Check if current location is different from majority
        most_common = max(set(recent_locations), key=recent_locations.count)
        return location != most_common
    
    def _is_suspicious_ip(self, ip_address: str) -> bool:
        """
        Check if IP is from known suspicious range
        
        Args:
            ip_address: IP address string
            
        Returns:
            True if IP is suspicious
        """
        suspicious_prefixes = ["185.220", "45.141", "23.154"]
        return any(ip_address.startswith(prefix) for prefix in suspicious_prefixes)
    
    def _update_history(self, txn: Transaction):
        """
        Update transaction history for future feature extraction
        
        Args:
            txn: Transaction to add to history
        """
        # Add to user history
        self.user_history[txn.user_id].append({
            'timestamp': txn.timestamp,
            'amount': txn.amount,
            'location': txn.location,
            'device_id': txn.device_id
        })
        
        # Update amount history (keep last 50 for statistics)
        self.user_amounts[txn.user_id].append(txn.amount)
        if len(self.user_amounts[txn.user_id]) > 50:
            self.user_amounts[txn.user_id].pop(0)
    
    def get_stats(self) -> dict:
        """Get feature extractor statistics"""
        return {
            "users_tracked": len(self.user_history),
            "devices_tracked": len(self.device_history),
            "time_window_seconds": self.time_window.total_seconds()
        }


class RiskScorer:
    """Calculate risk scores from extracted features"""
    
    def __init__(self, config: Dict = None):
        """
        Initialize risk scorer
        
        Args:
            config: Configuration dictionary with weights and thresholds
        """
        self.config = config or {}
        
        # Feature weights (sum to 1.0)
        self.weights = self.config.get('weights', {
            'velocity': 0.30,
            'device': 0.25,
            'amount': 0.25,
            'temporal': 0.10,
            'merchant': 0.10
        })
        
        # Scoring thresholds
        self.thresholds = self.config.get('thresholds', {
            'high_velocity': 5,
            'very_high_velocity': 10,
            'high_value': 1000,
            'very_high_value': 2000,
            'amount_deviation': 2.0
        })
        
        logger.info(f"Initialized RiskScorer with weights: {self.weights}")
    
    def calculate_risk_score(self, features: Dict) -> RiskScore:
        """
        Calculate comprehensive risk score from features
        
        Args:
            features: Dictionary of extracted features
            
        Returns:
            RiskScore object with score, signals, and features
        """
        signals = []
        score = 0.0
        
        # Velocity scoring
        velocity_score, velocity_signals = self._score_velocity(features)
        score += velocity_score * self.weights['velocity']
        signals.extend(velocity_signals)
        
        # Device scoring
        device_score, device_signals = self._score_device(features)
        score += device_score * self.weights['device']
        signals.extend(device_signals)
        
        # Amount scoring
        amount_score, amount_signals = self._score_amount(features)
        score += amount_score * self.weights['amount']
        signals.extend(amount_signals)
        
        # Temporal scoring
        temporal_score, temporal_signals = self._score_temporal(features)
        score += temporal_score * self.weights['temporal']
        signals.extend(temporal_signals)
        
        # Merchant scoring
        merchant_score, merchant_signals = self._score_merchant(features)
        score += merchant_score * self.weights['merchant']
        signals.extend(merchant_signals)
        
        # Ensure score is in valid range
        final_score = min(100.0, max(0.0, score))
        
        return RiskScore(
            score=round(final_score, 2),
            signals=signals,
            features=features
        )
    
    def _score_velocity(self, features: Dict) -> Tuple[float, List[str]]:
        """Score velocity-based risk"""
        velocity = features.get('velocity_count', 0)
        amount_velocity = features.get('velocity_amount', 0.0)
        signals = []
        
        if velocity >= self.thresholds['very_high_velocity']:
            signals.append("VERY_HIGH_VELOCITY")
            return 100.0, signals
        elif velocity >= self.thresholds['high_velocity']:
            signals.append("HIGH_VELOCITY")
            return 70.0, signals
        elif velocity >= 3:
            signals.append("MODERATE_VELOCITY")
            return 40.0, signals
        
        # Check amount velocity
        if amount_velocity > 5000:
            signals.append("HIGH_AMOUNT_VELOCITY")
            return 60.0, signals
        
        return 0.0, signals
    
    def _score_device(self, features: Dict) -> Tuple[float, List[str]]:
        """Score device-based risk"""
        signals = []
        score = 0.0
        
        if features.get('is_unknown_device', False):
            signals.append("UNKNOWN_DEVICE")
            score = 80.0
        elif features.get('is_new_device', False):
            signals.append("NEW_DEVICE")
            score = 60.0
        
        return score, signals
    
    def _score_amount(self, features: Dict) -> Tuple[float, List[str]]:
        """Score amount-based risk"""
        amount = features.get('amount', 0)
        deviation = features.get('amount_deviation', 0)
        signals = []
        score = 0.0
        
        if features.get('is_very_high_value', False):
            signals.append("VERY_HIGH_VALUE")
            score = max(score, 80.0)
        elif features.get('is_high_value', False):
            signals.append("HIGH_VALUE")
            score = max(score, 50.0)
        
        if deviation > self.thresholds['amount_deviation']:
            signals.append("AMOUNT_DEVIATION")
            score = max(score, 60.0)
        
        if features.get('is_low_amount', False) and features.get('velocity_count', 0) > 3:
            signals.append("LOW_AMOUNT_HIGH_VELOCITY")
            score = max(score, 70.0)
        
        return score, signals
    
    def _score_temporal(self, features: Dict) -> Tuple[float, List[str]]:
        """Score temporal-based risk"""
        signals = []
        score = 0.0
        
        if features.get('is_night_transaction', False):
            signals.append("NIGHT_TRANSACTION")
            score = 40.0
        
        if features.get('is_weekend', False) and features.get('is_high_value', False):
            signals.append("WEEKEND_HIGH_VALUE")
            score = max(score, 30.0)
        
        return score, signals
    
    def _score_merchant(self, features: Dict) -> Tuple[float, List[str]]:
        """Score merchant-based risk"""
        signals = []
        score = 0.0
        
        if features.get('is_suspicious_merchant', False):
            signals.append("SUSPICIOUS_MERCHANT")
            score = 90.0
        elif features.get('is_high_risk_category', False):
            signals.append("HIGH_RISK_CATEGORY")
            score = 30.0
        
        if features.get('location_shift', False):
            signals.append("LOCATION_SHIFT")
            score = max(score, 50.0)
        
        if features.get('is_suspicious_ip', False):
            signals.append("SUSPICIOUS_IP")
            score = max(score, 70.0)
        
        return score, signals
    
    def update_config(self, new_config: Dict):
        """Update scorer configuration"""
        if 'weights' in new_config:
            self.weights.update(new_config['weights'])
        if 'thresholds' in new_config:
            self.thresholds.update(new_config['thresholds'])
        
        logger.info(f"Updated RiskScorer config: {new_config}")
=======
"""
Risk Scoring Engine
Feature extraction and risk scoring for fraud detection
"""
from typing import Dict, List, Tuple
from collections import deque, defaultdict
from datetime import datetime, timedelta
import logging

from .models import Transaction, RiskScore

logger = logging.getLogger(__name__)


class FeatureExtractor:
    """Extract behavioral features from transactions"""
    
    def __init__(self, time_window_seconds: int = 300):
        """
        Initialize feature extractor
        
        Args:
            time_window_seconds: Time window for velocity calculations (default 5 minutes)
        """
        self.time_window = timedelta(seconds=time_window_seconds)
        
        # Maintain recent transaction history per user
        self.user_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.device_history: Dict[str, datetime] = {}
        self.user_amounts: Dict[str, List[float]] = defaultdict(list)
        
        logger.info(f"Initialized FeatureExtractor with time_window={time_window_seconds}s")
    
    def extract_features(self, txn: Transaction) -> Dict[str, any]:
        """
        Extract risk-relevant features from transaction
        
        Args:
            txn: Transaction to analyze
            
        Returns:
            Dictionary of extracted features
        """
        features = {}
        
        # Velocity Features
        features['velocity_count'] = self._calculate_velocity(txn.user_id, txn.timestamp)
        features['velocity_amount'] = self._calculate_amount_velocity(txn.user_id, txn.timestamp)
        
        # Device Features
        features['device_age_days'] = self._get_device_age(txn.device_id, txn.timestamp)
        features['is_new_device'] = features['device_age_days'] < 1
        features['is_unknown_device'] = 'new' in txn.device_id.lower()
        
        # Amount Features
        features['amount'] = txn.amount
        features['is_high_value'] = txn.amount > 1000
        features['is_very_high_value'] = txn.amount > 2000
        features['is_low_amount'] = txn.amount < 50
        features['amount_deviation'] = self._calculate_amount_deviation(txn.user_id, txn.amount)
        
        # Temporal Features
        features['hour_of_day'] = txn.timestamp.hour
        features['is_night_transaction'] = features['hour_of_day'] < 6 or features['hour_of_day'] > 22
        features['is_weekend'] = txn.timestamp.weekday() >= 5
        
        # Merchant Features
        features['merchant_category'] = txn.merchant_category
        features['is_high_risk_category'] = txn.merchant_category in ['electronics', 'travel', 'entertainment']
        features['is_suspicious_merchant'] = 'suspicious' in txn.merchant_id.lower()
        
        # Location Features
        features['location'] = txn.location
        features['location_shift'] = self._detect_location_shift(txn.user_id, txn.location)
        
        # IP Features
        features['is_suspicious_ip'] = self._is_suspicious_ip(txn.ip_address)
        
        # Update history for future feature extraction
        self._update_history(txn)
        
        return features
    
    def _calculate_velocity(self, user_id: str, current_time: datetime) -> int:
        """
        Count transactions in time window
        
        Args:
            user_id: User identifier
            current_time: Current transaction timestamp
            
        Returns:
            Number of transactions in time window
        """
        if user_id not in self.user_history:
            return 0
        
        cutoff = current_time - self.time_window
        recent = [t for t in self.user_history[user_id] if t['timestamp'] > cutoff]
        return len(recent)
    
    def _calculate_amount_velocity(self, user_id: str, current_time: datetime) -> float:
        """
        Calculate total amount spent in time window
        
        Args:
            user_id: User identifier
            current_time: Current transaction timestamp
            
        Returns:
            Total amount spent in window
        """
        if user_id not in self.user_history:
            return 0.0
        
        cutoff = current_time - self.time_window
        recent = [t for t in self.user_history[user_id] if t['timestamp'] > cutoff]
        return sum(t['amount'] for t in recent)
    
    def _get_device_age(self, device_id: str, current_time: datetime) -> float:
        """
        Get age of device in days
        
        Args:
            device_id: Device identifier
            current_time: Current transaction timestamp
            
        Returns:
            Device age in days
        """
        if device_id not in self.device_history:
            self.device_history[device_id] = current_time
            return 0.0
        
        first_seen = self.device_history[device_id]
        age = current_time - first_seen
        return age.total_seconds() / 86400  # Convert to days
    
    def _calculate_amount_deviation(self, user_id: str, amount: float) -> float:
        """
        Calculate how much this amount deviates from user's normal spending
        
        Args:
            user_id: User identifier
            amount: Transaction amount
            
        Returns:
            Standard deviations from mean (0 if insufficient history)
        """
        if user_id not in self.user_amounts or len(self.user_amounts[user_id]) < 3:
            return 0.0
        
        amounts = self.user_amounts[user_id]
        mean = sum(amounts) / len(amounts)
        
        if len(amounts) < 2:
            return 0.0
        
        variance = sum((x - mean) ** 2 for x in amounts) / (len(amounts) - 1)
        std_dev = variance ** 0.5
        
        if std_dev == 0:
            return 0.0
        
        return abs(amount - mean) / std_dev
    
    def _detect_location_shift(self, user_id: str, location: str) -> bool:
        """
        Detect if user's location changed significantly
        
        Args:
            user_id: User identifier
            location: Current location
            
        Returns:
            True if location shifted from recent transactions
        """
        if user_id not in self.user_history or len(self.user_history[user_id]) < 5:
            return False
        
        # Get recent locations
        recent = list(self.user_history[user_id])[-5:]
        recent_locations = [t['location'] for t in recent]
        
        # Check if current location is different from majority
        most_common = max(set(recent_locations), key=recent_locations.count)
        return location != most_common
    
    def _is_suspicious_ip(self, ip_address: str) -> bool:
        """
        Check if IP is from known suspicious range
        
        Args:
            ip_address: IP address string
            
        Returns:
            True if IP is suspicious
        """
        suspicious_prefixes = ["185.220", "45.141", "23.154"]
        return any(ip_address.startswith(prefix) for prefix in suspicious_prefixes)
    
    def _update_history(self, txn: Transaction):
        """
        Update transaction history for future feature extraction
        
        Args:
            txn: Transaction to add to history
        """
        # Add to user history
        self.user_history[txn.user_id].append({
            'timestamp': txn.timestamp,
            'amount': txn.amount,
            'location': txn.location,
            'device_id': txn.device_id
        })
        
        # Update amount history (keep last 50 for statistics)
        self.user_amounts[txn.user_id].append(txn.amount)
        if len(self.user_amounts[txn.user_id]) > 50:
            self.user_amounts[txn.user_id].pop(0)
    
    def get_stats(self) -> dict:
        """Get feature extractor statistics"""
        return {
            "users_tracked": len(self.user_history),
            "devices_tracked": len(self.device_history),
            "time_window_seconds": self.time_window.total_seconds()
        }


class RiskScorer:
    """Calculate risk scores from extracted features"""
    
    def __init__(self, config: Dict = None):
        """
        Initialize risk scorer
        
        Args:
            config: Configuration dictionary with weights and thresholds
        """
        self.config = config or {}
        
        # Feature weights (sum to 1.0)
        self.weights = self.config.get('weights', {
            'velocity': 0.30,
            'device': 0.25,
            'amount': 0.25,
            'temporal': 0.10,
            'merchant': 0.10
        })
        
        # Scoring thresholds
        self.thresholds = self.config.get('thresholds', {
            'high_velocity': 5,
            'very_high_velocity': 10,
            'high_value': 1000,
            'very_high_value': 2000,
            'amount_deviation': 2.0
        })
        
        logger.info(f"Initialized RiskScorer with weights: {self.weights}")
    
    def calculate_risk_score(self, features: Dict) -> RiskScore:
        """
        Calculate comprehensive risk score from features
        
        Args:
            features: Dictionary of extracted features
            
        Returns:
            RiskScore object with score, signals, and features
        """
        signals = []
        score = 0.0
        
        # Velocity scoring
        velocity_score, velocity_signals = self._score_velocity(features)
        score += velocity_score * self.weights['velocity']
        signals.extend(velocity_signals)
        
        # Device scoring
        device_score, device_signals = self._score_device(features)
        score += device_score * self.weights['device']
        signals.extend(device_signals)
        
        # Amount scoring
        amount_score, amount_signals = self._score_amount(features)
        score += amount_score * self.weights['amount']
        signals.extend(amount_signals)
        
        # Temporal scoring
        temporal_score, temporal_signals = self._score_temporal(features)
        score += temporal_score * self.weights['temporal']
        signals.extend(temporal_signals)
        
        # Merchant scoring
        merchant_score, merchant_signals = self._score_merchant(features)
        score += merchant_score * self.weights['merchant']
        signals.extend(merchant_signals)
        
        # Ensure score is in valid range
        final_score = min(100.0, max(0.0, score))
        
        return RiskScore(
            score=round(final_score, 2),
            signals=signals,
            features=features
        )
    
    def _score_velocity(self, features: Dict) -> Tuple[float, List[str]]:
        """Score velocity-based risk"""
        velocity = features.get('velocity_count', 0)
        amount_velocity = features.get('velocity_amount', 0.0)
        signals = []
        
        if velocity >= self.thresholds['very_high_velocity']:
            signals.append("VERY_HIGH_VELOCITY")
            return 100.0, signals
        elif velocity >= self.thresholds['high_velocity']:
            signals.append("HIGH_VELOCITY")
            return 70.0, signals
        elif velocity >= 3:
            signals.append("MODERATE_VELOCITY")
            return 40.0, signals
        
        # Check amount velocity
        if amount_velocity > 5000:
            signals.append("HIGH_AMOUNT_VELOCITY")
            return 60.0, signals
        
        return 0.0, signals
    
    def _score_device(self, features: Dict) -> Tuple[float, List[str]]:
        """Score device-based risk"""
        signals = []
        score = 0.0
        
        if features.get('is_unknown_device', False):
            signals.append("UNKNOWN_DEVICE")
            score = 80.0
        elif features.get('is_new_device', False):
            signals.append("NEW_DEVICE")
            score = 60.0
        
        return score, signals
    
    def _score_amount(self, features: Dict) -> Tuple[float, List[str]]:
        """Score amount-based risk"""
        amount = features.get('amount', 0)
        deviation = features.get('amount_deviation', 0)
        signals = []
        score = 0.0
        
        if features.get('is_very_high_value', False):
            signals.append("VERY_HIGH_VALUE")
            score = max(score, 80.0)
        elif features.get('is_high_value', False):
            signals.append("HIGH_VALUE")
            score = max(score, 50.0)
        
        if deviation > self.thresholds['amount_deviation']:
            signals.append("AMOUNT_DEVIATION")
            score = max(score, 60.0)
        
        if features.get('is_low_amount', False) and features.get('velocity_count', 0) > 3:
            signals.append("LOW_AMOUNT_HIGH_VELOCITY")
            score = max(score, 70.0)
        
        return score, signals
    
    def _score_temporal(self, features: Dict) -> Tuple[float, List[str]]:
        """Score temporal-based risk"""
        signals = []
        score = 0.0
        
        if features.get('is_night_transaction', False):
            signals.append("NIGHT_TRANSACTION")
            score = 40.0
        
        if features.get('is_weekend', False) and features.get('is_high_value', False):
            signals.append("WEEKEND_HIGH_VALUE")
            score = max(score, 30.0)
        
        return score, signals
    
    def _score_merchant(self, features: Dict) -> Tuple[float, List[str]]:
        """Score merchant-based risk"""
        signals = []
        score = 0.0
        
        if features.get('is_suspicious_merchant', False):
            signals.append("SUSPICIOUS_MERCHANT")
            score = 90.0
        elif features.get('is_high_risk_category', False):
            signals.append("HIGH_RISK_CATEGORY")
            score = 30.0
        
        if features.get('location_shift', False):
            signals.append("LOCATION_SHIFT")
            score = max(score, 50.0)
        
        if features.get('is_suspicious_ip', False):
            signals.append("SUSPICIOUS_IP")
            score = max(score, 70.0)
        
        return score, signals
    
    def update_config(self, new_config: Dict):
        """Update scorer configuration"""
        if 'weights' in new_config:
            self.weights.update(new_config['weights'])
        if 'thresholds' in new_config:
            self.thresholds.update(new_config['thresholds'])
        
        logger.info(f"Updated RiskScorer config: {new_config}")
>>>>>>> 1a6d17f9aa0f61a18b8fc3da56965e00e5b43dc1
