# Mean Reversion Strategy Module
import numpy as np

class MeanReversionStrategy:
    def __init__(self):
        self.lookback_period = 20
        self.threshold = 2.0  # Standard deviations
        
    def generate_signal(self, price_data):
        """Generate mean reversion signals"""
        if len(price_data) < self.lookback_period:
            return 0
            
        mean_price = np.mean(price_data[-self.lookback_period:])
        std_price = np.std(price_data[-self.lookback_period:])
        current_price = price_data[-1]
        
        z_score = (current_price - mean_price) / std_price
        
        if z_score > self.threshold:
            return -1  # Sell signal
        elif z_score < -self.threshold:
            return 1   # Buy signal
        else:
            return 0   # No signal