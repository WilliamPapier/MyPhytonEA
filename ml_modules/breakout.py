# Breakout Strategy Module
import numpy as np

class BreakoutStrategy:
    def __init__(self):
        self.lookback_period = 20
        self.breakout_threshold = 0.01  # 1% breakout
        
    def generate_signal(self, price_data, volume_data=None):
        """Generate breakout signals"""
        if len(price_data) < self.lookback_period:
            return 0
            
        recent_high = np.max(price_data[-self.lookback_period:])
        recent_low = np.min(price_data[-self.lookback_period:])
        current_price = price_data[-1]
        
        # Calculate breakout levels
        upper_breakout = recent_high * (1 + self.breakout_threshold)
        lower_breakout = recent_low * (1 - self.breakout_threshold)
        
        if current_price > upper_breakout:
            return 1   # Buy signal
        elif current_price < lower_breakout:
            return -1  # Sell signal
        else:
            return 0   # No signal