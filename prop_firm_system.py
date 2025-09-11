"""
Prop Firm Account Detection and Rule Enforcement System

This module automatically detects prop firm accounts and enforces specific trading rules:
- Daily/weekly drawdown limits
- Maximum risk per trade
- News avoidance periods
- Trading session restrictions
- Position size limits

Detection is based on account name, broker, balance patterns, and configuration.
"""

import re
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from advanced_logging import log_prop_firm_event, log_warning, log_info

@dataclass
class PropFirmRules:
    """Prop firm specific trading rules"""
    max_daily_loss: float
    max_weekly_loss: float  
    max_monthly_loss: float
    trailing_drawdown_limit: float
    max_risk_per_trade: float
    max_position_size: float
    allowed_sessions: List[str]
    news_avoidance_minutes: int
    max_open_positions: int
    weekend_trading: bool
    high_impact_news_avoid: bool
    firm_name: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'max_daily_loss': self.max_daily_loss,
            'max_weekly_loss': self.max_weekly_loss,
            'max_monthly_loss': self.max_monthly_loss,
            'trailing_drawdown_limit': self.trailing_drawdown_limit,
            'max_risk_per_trade': self.max_risk_per_trade,
            'max_position_size': self.max_position_size,
            'allowed_sessions': self.allowed_sessions,
            'news_avoidance_minutes': self.news_avoidance_minutes,
            'max_open_positions': self.max_open_positions,
            'weekend_trading': self.weekend_trading,
            'high_impact_news_avoid': self.high_impact_news_avoid,
            'firm_name': self.firm_name
        }

class PropFirmDetector:
    """Automatically detect and manage prop firm accounts"""
    
    def __init__(self):
        self.prop_firm_rules = self._load_prop_firm_rules()
        self.detected_accounts = {}
        self.current_prop_firm = None
        self.is_prop_firm_mode = False
        
        # Daily tracking for limits
        self.daily_pnl = {}
        self.weekly_pnl = {}
        self.monthly_pnl = {}
        self.max_drawdown_today = 0.0
        
    def _load_prop_firm_rules(self) -> Dict[str, PropFirmRules]:
        """Load predefined prop firm rules"""
        return {
            'ftmo': PropFirmRules(
                max_daily_loss=500.0,
                max_weekly_loss=2000.0,
                max_monthly_loss=5000.0,
                trailing_drawdown_limit=0.05,  # 5%
                max_risk_per_trade=0.01,  # 1%
                max_position_size=200000,  # 2 lots max
                allowed_sessions=['London', 'New York'],
                news_avoidance_minutes=30,
                max_open_positions=3,
                weekend_trading=False,
                high_impact_news_avoid=True,
                firm_name='FTMO'
            ),
            'my_forex_funds': PropFirmRules(
                max_daily_loss=400.0,
                max_weekly_loss=1600.0,
                max_monthly_loss=4000.0,
                trailing_drawdown_limit=0.04,  # 4%
                max_risk_per_trade=0.008,  # 0.8%
                max_position_size=150000,  # 1.5 lots max
                allowed_sessions=['London', 'New York', 'Asian'],
                news_avoidance_minutes=20,
                max_open_positions=5,
                weekend_trading=False,
                high_impact_news_avoid=True,
                firm_name='MyForexFunds'
            ),
            'apex_trader': PropFirmRules(
                max_daily_loss=600.0,
                max_weekly_loss=2400.0,
                max_monthly_loss=6000.0,
                trailing_drawdown_limit=0.06,  # 6%
                max_risk_per_trade=0.012,  # 1.2%
                max_position_size=300000,  # 3 lots max
                allowed_sessions=['London', 'New York'],
                news_avoidance_minutes=25,
                max_open_positions=4,
                weekend_trading=False,
                high_impact_news_avoid=True,
                firm_name='Apex Trader'
            ),
            'funded_trader_plus': PropFirmRules(
                max_daily_loss=300.0,
                max_weekly_loss=1200.0,
                max_monthly_loss=3000.0,
                trailing_drawdown_limit=0.03,  # 3%
                max_risk_per_trade=0.006,  # 0.6%
                max_position_size=100000,  # 1 lot max
                allowed_sessions=['London', 'New York'],
                news_avoidance_minutes=15,
                max_open_positions=2,
                weekend_trading=False,
                high_impact_news_avoid=True,
                firm_name='Funded Trader Plus'
            )
        }
    
    def detect_prop_firm(self, account_info: Dict[str, Any]) -> Tuple[bool, Optional[PropFirmRules]]:
        """
        Detect if account is a prop firm account based on multiple criteria
        
        Args:
            account_info: Dictionary containing account details
            
        Returns:
            Tuple of (is_prop_firm, prop_firm_rules)
        """
        account_name = account_info.get('account_name', '').lower()
        broker = account_info.get('broker', '').lower()
        balance = account_info.get('balance', 0)
        server = account_info.get('server', '').lower()
        account_type = account_info.get('account_type', '').lower()
        
        # Pattern matching for account names
        prop_firm_patterns = {
            'ftmo': [r'ftmo', r'challenge', r'funded.*account'],
            'my_forex_funds': [r'mff', r'myforexfunds', r'forex.*funds'],
            'apex_trader': [r'apex', r'trader.*funding'],
            'funded_trader_plus': [r'ftp', r'fundedtrader', r'trader.*plus']
        }
        
        # Broker-based detection
        prop_firm_brokers = {
            'ftmo': ['ftmo', 'purple trading'],
            'my_forex_funds': ['mff', 'eightcap'],
            'apex_trader': ['apex', 'match-trade'],
            'funded_trader_plus': ['ftp', 'global prime']
        }
        
        # Balance-based detection (common prop firm starting balances)
        prop_firm_balances = {
            'ftmo': [10000, 25000, 50000, 100000, 200000],
            'my_forex_funds': [5000, 12500, 25000, 50000, 100000],
            'apex_trader': [25000, 50000, 100000, 150000],
            'funded_trader_plus': [6000, 15000, 30000, 60000]
        }
        
        detected_firm = None
        confidence_score = 0
        
        # Check account name patterns
        for firm, patterns in prop_firm_patterns.items():
            for pattern in patterns:
                if re.search(pattern, account_name):
                    detected_firm = firm
                    confidence_score += 3
                    log_info('prop_firm', f"Detected prop firm pattern in account name: {pattern}", 
                            account=account_name, firm=firm)
                    break
        
        # Check broker patterns
        for firm, brokers in prop_firm_brokers.items():
            for broker_pattern in brokers:
                if broker_pattern in broker:
                    if detected_firm == firm:
                        confidence_score += 2
                    elif detected_firm is None:
                        detected_firm = firm
                        confidence_score += 2
                    log_info('prop_firm', f"Detected prop firm broker: {broker_pattern}", 
                            broker=broker, firm=firm)
        
        # Check balance patterns
        for firm, balances in prop_firm_balances.items():
            if balance in balances:
                if detected_firm == firm:
                    confidence_score += 1
                elif detected_firm is None:
                    detected_firm = firm
                    confidence_score += 1
                log_info('prop_firm', f"Detected prop firm balance pattern: {balance}", 
                        balance=balance, firm=firm)
        
        # Server/demo account patterns
        demo_patterns = ['demo', 'challenge', 'test']
        if any(pattern in server for pattern in demo_patterns):
            confidence_score += 1
        
        # Decision logic
        is_prop_firm = confidence_score >= 3
        prop_firm_rules = None
        
        if is_prop_firm and detected_firm:
            prop_firm_rules = self.prop_firm_rules.get(detected_firm)
            self.current_prop_firm = detected_firm
            self.is_prop_firm_mode = True
            
            # Log detection
            log_prop_firm_event(
                'DETECTION',
                f"Prop firm account detected: {prop_firm_rules.firm_name}",
                account_info
            )
            
            return True, prop_firm_rules
        
        return False, None
    
    def enforce_prop_firm_rules(self, trade_setup: Dict[str, Any], 
                              account_info: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Enforce prop firm rules on a trade setup
        
        Returns:
            Tuple of (is_allowed, rejection_reason)
        """
        if not self.is_prop_firm_mode or not self.current_prop_firm:
            return True, ""
        
        rules = self.prop_firm_rules.get(self.current_prop_firm)
        if not rules:
            return True, ""
        
        current_time = datetime.now()
        
        # Check daily loss limit
        today = current_time.date()
        daily_loss = self.daily_pnl.get(today, 0)
        if daily_loss >= rules.max_daily_loss:
            reason = f"Daily loss limit exceeded: ${daily_loss:.2f} >= ${rules.max_daily_loss:.2f}"
            log_prop_firm_event('RULE_VIOLATION', reason, account_info)
            return False, reason
        
        # Check risk per trade
        trade_risk = trade_setup.get('risk_amount', 0)
        account_balance = account_info.get('balance', 0)
        risk_percentage = trade_risk / account_balance if account_balance > 0 else 0
        
        if risk_percentage > rules.max_risk_per_trade:
            reason = f"Risk per trade exceeded: {risk_percentage:.3f} > {rules.max_risk_per_trade:.3f}"
            log_prop_firm_event('RULE_VIOLATION', reason, account_info)
            return False, reason
        
        # Check position size
        position_size = trade_setup.get('position_size', 0)
        if position_size > rules.max_position_size:
            reason = f"Position size too large: {position_size} > {rules.max_position_size}"
            log_prop_firm_event('RULE_VIOLATION', reason, account_info)
            return False, reason
        
        # Check trading session
        current_session = self._get_current_session()
        if current_session not in rules.allowed_sessions:
            reason = f"Trading outside allowed sessions: {current_session} not in {rules.allowed_sessions}"
            log_prop_firm_event('RULE_VIOLATION', reason, account_info)
            return False, reason
        
        # Check news avoidance
        if rules.high_impact_news_avoid and self._is_news_time(rules.news_avoidance_minutes):
            reason = f"High impact news avoidance period active"
            log_prop_firm_event('RULE_VIOLATION', reason, account_info)
            return False, reason
        
        # Check weekend trading
        if not rules.weekend_trading and current_time.weekday() >= 5:  # Saturday = 5, Sunday = 6
            reason = "Weekend trading not allowed"
            log_prop_firm_event('RULE_VIOLATION', reason, account_info)
            return False, reason
        
        return True, ""
    
    def update_pnl(self, pnl: float, trade_date: datetime = None):
        """Update P&L tracking for prop firm limits"""
        if trade_date is None:
            trade_date = datetime.now()
        
        date_key = trade_date.date()
        
        # Update daily P&L
        if pnl < 0:  # Only track losses
            self.daily_pnl[date_key] = self.daily_pnl.get(date_key, 0) + abs(pnl)
        
        # Update weekly P&L
        week_start = date_key - timedelta(days=date_key.weekday())
        self.weekly_pnl[week_start] = self.weekly_pnl.get(week_start, 0) + abs(pnl) if pnl < 0 else 0
        
        # Update monthly P&L
        month_key = date_key.replace(day=1)
        self.monthly_pnl[month_key] = self.monthly_pnl.get(month_key, 0) + abs(pnl) if pnl < 0 else 0
    
    def _get_current_session(self) -> str:
        """Determine current trading session based on UTC time"""
        utc_hour = datetime.utcnow().hour
        
        if 0 <= utc_hour < 7:
            return 'Asian'
        elif 7 <= utc_hour < 15:
            return 'London'
        elif 15 <= utc_hour < 22:
            return 'New York'
        else:
            return 'Asian'
    
    def _is_news_time(self, avoidance_minutes: int) -> bool:
        """Check if we're in a news avoidance period"""
        # This is a placeholder - in real implementation, this would
        # check against an economic calendar API
        return False
    
    def get_prop_firm_status(self) -> Dict[str, Any]:
        """Get current prop firm status and limits"""
        if not self.is_prop_firm_mode:
            return {'is_prop_firm': False}
        
        rules = self.prop_firm_rules.get(self.current_prop_firm)
        if not rules:
            return {'is_prop_firm': False}
        
        today = datetime.now().date()
        
        return {
            'is_prop_firm': True,
            'firm_name': rules.firm_name,
            'daily_loss_used': self.daily_pnl.get(today, 0),
            'daily_loss_limit': rules.max_daily_loss,
            'daily_loss_remaining': max(0, rules.max_daily_loss - self.daily_pnl.get(today, 0)),
            'max_risk_per_trade': rules.max_risk_per_trade,
            'max_position_size': rules.max_position_size,
            'allowed_sessions': rules.allowed_sessions,
            'current_session': self._get_current_session(),
            'rules': rules.to_dict()
        }
    
    def emergency_shutdown(self, reason: str, account_info: Dict[str, Any]):
        """Emergency shutdown for prop firm rule violations"""
        log_prop_firm_event('EMERGENCY_SHUTDOWN', f"Emergency shutdown triggered: {reason}", account_info)
        
        # This would integrate with the EA to close all positions
        # and stop trading
        return {
            'action': 'emergency_shutdown',
            'reason': reason,
            'timestamp': datetime.utcnow().isoformat(),
            'firm': self.current_prop_firm
        }

# Global prop firm detector instance
prop_firm_detector = PropFirmDetector()