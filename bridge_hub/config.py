"""
Configuration Management for BRIDGE Hub
"""
import os
from typing import Dict


def load_config() -> Dict:
    """
    Load hub configuration from environment variables
    
    Returns:
        Configuration dictionary
    """
    config = {
        # Server settings
        'host': os.getenv('HUB_HOST', '0.0.0.0'),
        'port': int(os.getenv('HUB_PORT', '8000')),
        
        # Correlation settings
        'entity_threshold': int(os.getenv('ENTITY_THRESHOLD', '2')),
        'time_window_seconds': int(os.getenv('TIME_WINDOW_SECONDS', '300')),
        
        # Escalation thresholds
        'critical_threshold': int(os.getenv('CRITICAL_THRESHOLD', '4')),
        'high_threshold': int(os.getenv('HIGH_THRESHOLD', '3')),
        'medium_threshold': int(os.getenv('MEDIUM_THRESHOLD', '2')),
        
        # Graph maintenance
        'max_graph_age_seconds': int(os.getenv('MAX_GRAPH_AGE_SECONDS', '3600')),
        'prune_interval_seconds': int(os.getenv('PRUNE_INTERVAL_SECONDS', '300')),
        
        # Advisory settings
        'max_advisories': int(os.getenv('MAX_ADVISORIES', '1000')),
        
        # Logging
        'log_level': os.getenv('LOG_LEVEL', 'INFO'),
        
        # Security
        'api_key': os.getenv('HUB_API_KEY', 'dev-key-change-in-production'),
    }
    
    return config


def validate_config(config: Dict) -> None:
    """
    Validate configuration values
    
    Args:
        config: Configuration dictionary
        
    Raises:
        ValueError: If configuration is invalid
    """
    # Validate thresholds
    if config['entity_threshold'] < 1:
        raise ValueError("entity_threshold must be >= 1")
    
    if config['time_window_seconds'] < 1:
        raise ValueError("time_window_seconds must be >= 1")
    
    if not (1 <= config['medium_threshold'] <= config['high_threshold'] <= config['critical_threshold']):
        raise ValueError("Escalation thresholds must be: medium <= high <= critical")
    
    # Validate graph settings
    if config['max_graph_age_seconds'] < 60:
        raise ValueError("max_graph_age_seconds must be >= 60")
    
    if config['prune_interval_seconds'] < 10:
        raise ValueError("prune_interval_seconds must be >= 10")
    
    # Validate port
    if not (1 <= config['port'] <= 65535):
        raise ValueError("port must be between 1 and 65535")
    
    print("✅ Configuration validation passed")
