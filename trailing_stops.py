"""
Trailing stop loss system with multiple methods (fixed, ATR, structure-based).
Provides intelligent stop management to maximize profits while protecting capital.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json
from config import config_manager

class TrailingStopManager:
    """
    Manages trailing stop losses for active trades using different methods.
    """
    
    def __init__(self):
        self.active_trailing_stops = {}  # trade_id -> stop_data
        
    def initialize_trailing_stop(self, trade_id: str, trade_data: Dict) -> bool:
        """
        Initialize trailing stop for a trade based on configuration.
        """
        try:
            if not config_manager.get("trailing_stop_enabled", True):
                return False
            
            method = config_manager.get("trailing_stop_method", "atr")
            
            stop_data = {
                "trade_id": trade_id,
                "symbol": trade_data.get("symbol"),
                "direction": trade_data.get("direction"),
                "entry_price": trade_data.get("entry_price"),
                "current_stop": trade_data.get("stop_loss"),
                "initial_stop": trade_data.get("stop_loss"),
                "method": method,
                "last_update": datetime.now().isoformat(),
                "highest_profit": 0.0,
                "lowest_loss": 0.0
            }
            
            # Method-specific initialization
            if method == "atr":
                stop_data["atr_multiplier"] = config_manager.get("trailing_stop_atr_multiplier", 1.5)
            elif method == "fixed":
                stop_data["fixed_pips"] = config_manager.get("trailing_stop_fixed_pips", 20)
            elif method == "structure":
                stop_data["lookback_periods"] = 20
                stop_data["swing_points"] = []
            
            self.active_trailing_stops[trade_id] = stop_data
            return True
            
        except Exception as e:
            print(f"Error initializing trailing stop for {trade_id}: {e}")
            return False
    
    def update_trailing_stop(self, trade_id: str, current_price: float, 
                           market_data: Dict = None) -> Optional[float]:
        """
        Update trailing stop based on current price and method.
        Returns new stop loss level or None if no change.
        """
        if trade_id not in self.active_trailing_stops:
            return None
        
        stop_data = self.active_trailing_stops[trade_id]
        method = stop_data["method"]
        direction = stop_data["direction"]
        current_stop = stop_data["current_stop"]
        
        new_stop = None
        
        try:
            if method == "atr":
                new_stop = self._update_atr_trailing_stop(stop_data, current_price, market_data)
            elif method == "fixed":
                new_stop = self._update_fixed_trailing_stop(stop_data, current_price)
            elif method == "structure":
                new_stop = self._update_structure_trailing_stop(stop_data, current_price, market_data)
            
            # Validate the new stop level
            if new_stop is not None and self._is_valid_stop_update(stop_data, new_stop):
                stop_data["current_stop"] = new_stop
                stop_data["last_update"] = datetime.now().isoformat()
                
                # Update profit tracking
                entry_price = stop_data["entry_price"]
                if direction.lower() == "buy":
                    profit = current_price - entry_price
                    stop_data["highest_profit"] = max(stop_data["highest_profit"], profit)
                else:
                    profit = entry_price - current_price
                    stop_data["highest_profit"] = max(stop_data["highest_profit"], profit)
                
                return new_stop
            
        except Exception as e:
            print(f"Error updating trailing stop for {trade_id}: {e}")
        
        return None
    
    def _update_atr_trailing_stop(self, stop_data: Dict, current_price: float, 
                                market_data: Dict) -> Optional[float]:
        """Update trailing stop using ATR method"""
        direction = stop_data["direction"]
        atr_multiplier = stop_data.get("atr_multiplier", 1.5)
        
        # Get ATR from market data or estimate from volatility
        atr = 0.001  # Default ATR
        if market_data:
            atr = market_data.get("atr", market_data.get("volatility", 0.001))
        
        trailing_distance = atr * atr_multiplier
        
        if direction.lower() == "buy":
            # For buy trades, trail stop up
            new_stop = current_price - trailing_distance
            return max(new_stop, stop_data["current_stop"])  # Only move up
        else:
            # For sell trades, trail stop down
            new_stop = current_price + trailing_distance
            return min(new_stop, stop_data["current_stop"])  # Only move down
    
    def _update_fixed_trailing_stop(self, stop_data: Dict, current_price: float) -> Optional[float]:
        """Update trailing stop using fixed pip method"""
        direction = stop_data["direction"]
        fixed_pips = stop_data.get("fixed_pips", 20)
        
        # Convert pips to price (assuming 4-digit quotes)
        pip_value = 0.0001
        if "JPY" in stop_data.get("symbol", ""):
            pip_value = 0.01
        
        trailing_distance = fixed_pips * pip_value
        
        if direction.lower() == "buy":
            new_stop = current_price - trailing_distance
            return max(new_stop, stop_data["current_stop"])
        else:
            new_stop = current_price + trailing_distance
            return min(new_stop, stop_data["current_stop"])
    
    def _update_structure_trailing_stop(self, stop_data: Dict, current_price: float,
                                      market_data: Dict) -> Optional[float]:
        """Update trailing stop based on market structure (swing points)"""
        if not market_data or "highs" not in market_data or "lows" not in market_data:
            return None
        
        direction = stop_data["direction"]
        lookback = stop_data.get("lookback_periods", 20)
        
        highs = market_data.get("highs", [])
        lows = market_data.get("lows", [])
        
        if len(highs) < lookback or len(lows) < lookback:
            return None
        
        if direction.lower() == "buy":
            # Trail stop to recent swing lows
            recent_lows = lows[-lookback:]
            swing_low = min(recent_lows)
            buffer = (current_price - swing_low) * 0.1  # 10% buffer
            new_stop = swing_low - buffer
            return max(new_stop, stop_data["current_stop"])
        else:
            # Trail stop to recent swing highs
            recent_highs = highs[-lookback:]
            swing_high = max(recent_highs)
            buffer = (swing_high - current_price) * 0.1  # 10% buffer
            new_stop = swing_high + buffer
            return min(new_stop, stop_data["current_stop"])
    
    def _is_valid_stop_update(self, stop_data: Dict, new_stop: float) -> bool:
        """Validate if the stop update is beneficial"""
        direction = stop_data["direction"]
        current_stop = stop_data["current_stop"]
        entry_price = stop_data["entry_price"]
        
        # Don't update if new stop is worse than current
        if direction.lower() == "buy":
            if new_stop <= current_stop:
                return False
            # Don't trail stop above entry (protect against whipsaws early)
            min_profit_distance = abs(entry_price - current_stop) * 0.5
            if new_stop > entry_price - min_profit_distance:
                return False
        else:
            if new_stop >= current_stop:
                return False
            min_profit_distance = abs(current_stop - entry_price) * 0.5
            if new_stop < entry_price + min_profit_distance:
                return False
        
        return True
    
    def should_hold_trade(self, trade_id: str, current_price: float, 
                         market_data: Dict = None) -> Tuple[bool, str]:
        """
        Determine if trade should continue to be held based on structure/trend.
        Returns (should_hold, reason).
        """
        if trade_id not in self.active_trailing_stops:
            return True, "No trailing stop data"
        
        stop_data = self.active_trailing_stops[trade_id]
        direction = stop_data["direction"]
        entry_price = stop_data["entry_price"]
        
        # Check maximum hold time
        max_hold_hours = config_manager.get("hold_time_hours", 8)
        trade_start = datetime.fromisoformat(stop_data["last_update"])
        if datetime.now() - trade_start > timedelta(hours=max_hold_hours):
            return False, "Maximum hold time exceeded"
        
        # Check trend continuation
        if market_data:
            trend_strength = self._assess_trend_strength(market_data, direction)
            if trend_strength < 0.3:  # Weak trend
                return False, "Trend weakened significantly"
        
        # Check if still in profit zone
        if direction.lower() == "buy":
            if current_price < entry_price * 0.995:  # 0.5% below entry
                return False, "Price moved significantly against entry"
        else:
            if current_price > entry_price * 1.005:  # 0.5% above entry
                return False, "Price moved significantly against entry"
        
        return True, "Structure and trend remain valid"
    
    def _assess_trend_strength(self, market_data: Dict, direction: str) -> float:
        """Assess current trend strength (0-1 scale)"""
        try:
            # Use moving averages if available
            if "ma_5" in market_data and "ma_20" in market_data:
                ma5 = market_data["ma_5"]
                ma20 = market_data["ma_20"]
                
                if direction.lower() == "buy":
                    if ma5 > ma20:
                        spread = (ma5 - ma20) / ma20
                        return min(spread * 100, 1.0)  # Normalize to 0-1
                else:
                    if ma5 < ma20:
                        spread = (ma20 - ma5) / ma20
                        return min(spread * 100, 1.0)
            
            # Fallback: use price momentum
            if "closes" in market_data and len(market_data["closes"]) >= 10:
                closes = market_data["closes"][-10:]
                momentum = (closes[-1] - closes[0]) / closes[0]
                
                if direction.lower() == "buy" and momentum > 0:
                    return min(momentum * 50, 1.0)
                elif direction.lower() == "sell" and momentum < 0:
                    return min(abs(momentum) * 50, 1.0)
            
        except Exception as e:
            print(f"Error assessing trend strength: {e}")
        
        return 0.5  # Neutral if unable to assess
    
    def get_trailing_stop_data(self, trade_id: str) -> Optional[Dict]:
        """Get trailing stop data for a specific trade"""
        return self.active_trailing_stops.get(trade_id)
    
    def remove_trailing_stop(self, trade_id: str) -> bool:
        """Remove trailing stop data when trade is closed"""
        if trade_id in self.active_trailing_stops:
            del self.active_trailing_stops[trade_id]
            return True
        return False
    
    def get_all_trailing_stops(self) -> Dict:
        """Get all active trailing stop data"""
        return self.active_trailing_stops.copy()

# Global trailing stop manager instance
trailing_stop_manager = TrailingStopManager()