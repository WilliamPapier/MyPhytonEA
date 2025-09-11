# Risk Manager Module
from datetime import datetime, timedelta

class RiskManager:
    def __init__(self):
        self.daily_max_loss = 500  # Default daily max loss
        self.weekly_max_loss = 2000
        self.monthly_max_loss = 5000
        self.max_drawdown = 0.1  # 10%
        self.daily_losses = {}
        
    def check_risk_limits(self, setup, account_balance):
        """Check if trade passes risk limits"""
        today = datetime.now().date()
        
        # Check daily loss limit
        daily_loss = self.daily_losses.get(today, 0)
        potential_loss = setup.get('risk_amount', 0)
        
        if daily_loss + potential_loss > self.daily_max_loss:
            return False, "Daily loss limit exceeded"
            
        # Check position size
        if potential_loss > account_balance * 0.02:  # Max 2% risk per trade
            return False, "Position size too large"
            
        return True, "Risk check passed"
        
    def record_loss(self, loss_amount):
        """Record a loss for risk tracking"""
        today = datetime.now().date()
        self.daily_losses[today] = self.daily_losses.get(today, 0) + loss_amount