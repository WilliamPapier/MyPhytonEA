# Strategy Selector Module
import random

class StrategySelector:
    def __init__(self):
        self.strategies = ['mean_reversion', 'breakout', 'news_trading']
        
    def select_strategy(self, market_conditions):
        """Select appropriate strategy based on market conditions"""
        volatility = market_conditions.get('volatility', 1.0)
        trend_strength = market_conditions.get('trend_strength', 0.5)
        
        if volatility > 1.5:
            return 'breakout'
        elif trend_strength < 0.3:
            return 'mean_reversion'
        else:
            return 'news_trading'