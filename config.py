"""
Central configuration system for EA/Scanner with global probability threshold
and risk management settings. Provides real-time updates to all modules.
"""
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
import threading

class ConfigManager:
    """
    Thread-safe configuration manager for global settings
    """
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.lock = threading.Lock()
        self._config = self._load_default_config()
        self.load()
        
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration values"""
        return {
            "probability_threshold": 0.75,  # Global threshold for signaling and trade filtering
            "risk_per_trade_percent": 2.0,  # Risk percentage per trade
            "max_simultaneous_trades": 3,   # Maximum number of simultaneous trades
            "dynamic_lotsize_enabled": True,  # Enable dynamic lotsize based on equity
            "pyramiding_enabled": True,     # Allow multiple entries on same instrument
            "trailing_stop_enabled": True,  # Enable trailing stop loss
            "trailing_stop_method": "atr",  # "fixed", "atr", or "structure"
            "trailing_stop_atr_multiplier": 1.5,
            "trailing_stop_fixed_pips": 20,
            "optimal_tp_enabled": True,     # Use optimal TP based on historical analysis
            "hold_time_hours": 8,          # Maximum hold time for trades
            "min_setup_probability": 0.60, # Minimum probability to consider a setup
            "account_balance": 10000.0,    # Current account balance (updated by EA)
            "equity_growth_threshold": 0.10, # Increase lotsize when equity grows by this %
            "max_daily_risk_percent": 6.0, # Maximum daily risk exposure
            "last_updated": datetime.now().isoformat()
        }
    
    def load(self) -> bool:
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    file_config = json.load(f)
                    self._config.update(file_config)
                return True
        except Exception as e:
            print(f"Error loading config: {e}")
        return False
    
    def save(self) -> bool:
        """Save configuration to file"""
        try:
            with self.lock:
                self._config["last_updated"] = datetime.now().isoformat()
                with open(self.config_file, 'w') as f:
                    json.dump(self._config, f, indent=2)
                return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value thread-safely"""
        with self.lock:
            return self._config.get(key, default)
    
    def set(self, key: str, value: Any) -> bool:
        """Set configuration value and save"""
        try:
            with self.lock:
                self._config[key] = value
            return self.save()
        except Exception as e:
            print(f"Error setting config {key}: {e}")
            return False
    
    def update_multiple(self, updates: Dict[str, Any]) -> bool:
        """Update multiple configuration values atomically"""
        try:
            with self.lock:
                self._config.update(updates)
            return self.save()
        except Exception as e:
            print(f"Error updating config: {e}")
            return False
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration values"""
        with self.lock:
            return self._config.copy()
    
    def get_probability_threshold(self) -> float:
        """Get current global probability threshold"""
        return self.get("probability_threshold", 0.75)
    
    def set_probability_threshold(self, threshold: float) -> bool:
        """Set global probability threshold"""
        if 0.0 <= threshold <= 1.0:
            return self.set("probability_threshold", threshold)
        return False
    
    def get_risk_settings(self) -> Dict[str, Any]:
        """Get risk management settings"""
        return {
            "risk_per_trade_percent": self.get("risk_per_trade_percent", 2.0),
            "max_simultaneous_trades": self.get("max_simultaneous_trades", 3),
            "max_daily_risk_percent": self.get("max_daily_risk_percent", 6.0),
            "dynamic_lotsize_enabled": self.get("dynamic_lotsize_enabled", True),
            "pyramiding_enabled": self.get("pyramiding_enabled", True)
        }
    
    def calculate_position_size(self, account_balance: float, stop_loss_pips: float, 
                              pip_value: float = 1.0) -> float:
        """Calculate position size based on risk settings"""
        risk_amount = account_balance * (self.get("risk_per_trade_percent", 2.0) / 100)
        if stop_loss_pips > 0:
            position_size = risk_amount / (stop_loss_pips * pip_value)
            return round(position_size, 2)
        return 0.01  # Minimum position size

# Global configuration instance
config_manager = ConfigManager()