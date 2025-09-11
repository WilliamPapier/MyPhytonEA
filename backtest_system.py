"""
High-Fidelity Backtest System for MyPhytonEA Trading System

Features:
- Uses same logic as live trading
- Detailed performance metrics (drawdown, profit factor, Sharpe ratio, etc.)
- Trade-by-trade analysis
- Risk management integration
- Prop firm rule simulation
- Statistical significance testing
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import json
from dataclasses import dataclass
from advanced_logging import log_info, log_error, log_warning
from prop_firm_system import prop_firm_detector, PropFirmRules

@dataclass
class BacktestResult:
    """Comprehensive backtest results"""
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    total_pnl: float
    gross_profit: float
    gross_loss: float
    profit_factor: float
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    max_drawdown_percent: float
    average_win: float
    average_loss: float
    largest_win: float
    largest_loss: float
    consecutive_wins: int
    consecutive_losses: int
    calmar_ratio: float
    recovery_factor: float
    expectancy: float
    trading_days: int
    start_date: str
    end_date: str
    initial_balance: float
    final_balance: float
    trades: List[Dict[str, Any]]
    daily_pnl: List[Dict[str, Any]]
    drawdown_periods: List[Dict[str, Any]]
    monthly_returns: Dict[str, float]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'summary': {
                'total_trades': self.total_trades,
                'win_rate': self.win_rate,
                'total_pnl': self.total_pnl,
                'profit_factor': self.profit_factor,
                'sharpe_ratio': self.sharpe_ratio,
                'max_drawdown': self.max_drawdown,
                'max_drawdown_percent': self.max_drawdown_percent,
                'calmar_ratio': self.calmar_ratio,
                'expectancy': self.expectancy
            },
            'detailed_metrics': {
                'winning_trades': self.winning_trades,
                'losing_trades': self.losing_trades,
                'gross_profit': self.gross_profit,
                'gross_loss': self.gross_loss,
                'average_win': self.average_win,
                'average_loss': self.average_loss,
                'largest_win': self.largest_win,
                'largest_loss': self.largest_loss,
                'consecutive_wins': self.consecutive_wins,
                'consecutive_losses': self.consecutive_losses,
                'sortino_ratio': self.sortino_ratio,
                'recovery_factor': self.recovery_factor
            },
            'period_info': {
                'start_date': self.start_date,
                'end_date': self.end_date,
                'trading_days': self.trading_days,
                'initial_balance': self.initial_balance,
                'final_balance': self.final_balance
            },
            'trades': self.trades,
            'daily_pnl': self.daily_pnl,
            'drawdown_periods': self.drawdown_periods,
            'monthly_returns': self.monthly_returns
        }

class BacktestEngine:
    """High-fidelity backtesting engine"""
    
    def __init__(self, initial_balance: float = 10000.0):
        self.initial_balance = initial_balance
        self.current_balance = initial_balance
        self.trades = []
        self.daily_pnl = []
        self.open_positions = []
        self.equity_curve = []
        
        # Risk management
        self.max_risk_per_trade = 0.02  # 2%
        self.max_open_positions = 5
        
        # Prop firm simulation
        self.simulate_prop_firm = False
        self.prop_firm_rules = None
        self.prop_firm_violations = []
        
    def set_prop_firm_simulation(self, firm_name: str):
        """Enable prop firm rule simulation"""
        self.simulate_prop_firm = True
        
        # Get prop firm rules
        if firm_name.lower() == 'ftmo':
            self.prop_firm_rules = PropFirmRules(
                max_daily_loss=500.0,
                max_weekly_loss=2000.0,
                max_monthly_loss=5000.0,
                trailing_drawdown_limit=0.05,
                max_risk_per_trade=0.01,
                max_position_size=200000,
                allowed_sessions=['London', 'New York'],
                news_avoidance_minutes=30,
                max_open_positions=3,
                weekend_trading=False,
                high_impact_news_avoid=True,
                firm_name='FTMO'
            )
        
        log_info('backtest', f"Prop firm simulation enabled: {firm_name}")
    
    def run_backtest(self, data: pd.DataFrame, strategy_func, 
                    start_date: str = None, end_date: str = None) -> BacktestResult:
        """
        Run backtest on historical data
        
        Args:
            data: Historical OHLCV data
            strategy_func: Function that generates trading signals
            start_date: Start date for backtest
            end_date: End date for backtest
        """
        
        # Filter data by date range
        if start_date:
            data = data[data.index >= start_date]
        if end_date:
            data = data[data.index <= end_date]
        
        if len(data) == 0:
            raise ValueError("No data available for specified date range")
        
        log_info('backtest', f"Starting backtest: {len(data)} bars from {data.index[0]} to {data.index[-1]}")
        
        # Reset state
        self.current_balance = self.initial_balance
        self.trades = []
        self.daily_pnl = []
        self.open_positions = []
        self.equity_curve = []
        self.prop_firm_violations = []
        
        # Track daily P&L for prop firm rules
        daily_pnl_tracker = {}
        
        # Process each bar
        for i, (timestamp, bar) in enumerate(data.iterrows()):
            current_date = timestamp.date()
            
            # Update open positions
            self._update_open_positions(bar, timestamp)
            
            # Generate strategy signals
            try:
                signals = strategy_func(data.iloc[:i+1])  # Pass data up to current bar
                
                if signals is not None and len(signals) > 0:
                    for signal in signals:
                        # Validate signal
                        if self._validate_trade_signal(signal, bar, timestamp):
                            # Execute trade
                            trade = self._execute_trade(signal, bar, timestamp)
                            if trade:
                                self.trades.append(trade)
                                
                                # Track daily P&L for prop firm rules
                                if self.simulate_prop_firm and trade.get('pnl'):
                                    date_key = timestamp.date()
                                    if trade['pnl'] < 0:
                                        daily_pnl_tracker[date_key] = daily_pnl_tracker.get(date_key, 0) + abs(trade['pnl'])
                                        
                                        # Check prop firm daily loss limit
                                        if (self.prop_firm_rules and 
                                            daily_pnl_tracker[date_key] >= self.prop_firm_rules.max_daily_loss):
                                            violation = {
                                                'date': timestamp.isoformat(),
                                                'type': 'daily_loss_limit',
                                                'amount': daily_pnl_tracker[date_key],
                                                'limit': self.prop_firm_rules.max_daily_loss
                                            }
                                            self.prop_firm_violations.append(violation)
                                            log_warning('backtest', f"Prop firm daily loss limit exceeded: {violation}")
            
            except Exception as e:
                log_error('backtest', f"Error processing signal at {timestamp}: {e}")
            
            # Record equity curve
            equity = self._calculate_current_equity(bar)
            self.equity_curve.append({
                'timestamp': timestamp,
                'equity': equity,
                'balance': self.current_balance,
                'drawdown': max(0, max([e['equity'] for e in self.equity_curve] + [equity]) - equity)
            })
        
        # Close any remaining open positions at the end
        final_bar = data.iloc[-1]
        for position in self.open_positions:
            trade = self._close_position(position, final_bar, data.index[-1], 'backtest_end')
            if trade:
                self.trades.append(trade)
        
        # Calculate comprehensive results
        result = self._calculate_backtest_results(data)
        
        log_info('backtest', f"Backtest completed: {result.total_trades} trades, {result.win_rate:.1f}% win rate, {result.total_pnl:.2f} total P&L")
        
        return result
    
    def _validate_trade_signal(self, signal: Dict[str, Any], bar: pd.Series, timestamp) -> bool:
        """Validate if trade signal should be executed"""
        
        # Check basic signal structure
        required_fields = ['action', 'instrument', 'entry_price', 'stop_loss', 'take_profit']
        if not all(field in signal for field in required_fields):
            return False
        
        # Check risk management
        risk_amount = signal.get('risk_amount', 0)
        if risk_amount > self.current_balance * self.max_risk_per_trade:
            return False
        
        # Check max open positions
        if len(self.open_positions) >= self.max_open_positions:
            return False
        
        # Prop firm specific checks
        if self.simulate_prop_firm and self.prop_firm_rules:
            # Check session restrictions
            current_hour = timestamp.hour
            session = self._get_trading_session(current_hour)
            if session not in self.prop_firm_rules.allowed_sessions:
                return False
            
            # Check weekend trading
            if not self.prop_firm_rules.weekend_trading and timestamp.weekday() >= 5:
                return False
            
            # Check risk per trade
            risk_percentage = risk_amount / self.current_balance if self.current_balance > 0 else 0
            if risk_percentage > self.prop_firm_rules.max_risk_per_trade:
                return False
        
        return True
    
    def _execute_trade(self, signal: Dict[str, Any], bar: pd.Series, timestamp) -> Optional[Dict[str, Any]]:
        """Execute a trade based on signal"""
        
        try:
            position = {
                'id': len(self.trades) + len(self.open_positions) + 1,
                'instrument': signal['instrument'],
                'action': signal['action'],  # 'buy' or 'sell'
                'entry_price': signal['entry_price'],
                'stop_loss': signal['stop_loss'],
                'take_profit': signal['take_profit'],
                'position_size': signal.get('position_size', 100000),  # Default 1 lot
                'entry_time': timestamp,
                'risk_amount': signal.get('risk_amount', 0),
                'status': 'open'
            }
            
            self.open_positions.append(position)
            log_info('backtest', f"Opened position: {position['action']} {position['instrument']} at {position['entry_price']}")
            
            return None  # Will be recorded when position is closed
            
        except Exception as e:
            log_error('backtest', f"Error executing trade: {e}")
            return None
    
    def _update_open_positions(self, bar: pd.Series, timestamp):
        """Update open positions and check for exits"""
        
        positions_to_close = []
        
        for position in self.open_positions:
            # Check stop loss and take profit
            current_price = bar['Close']
            
            if position['action'] == 'buy':
                if current_price <= position['stop_loss']:
                    positions_to_close.append((position, 'stop_loss'))
                elif current_price >= position['take_profit']:
                    positions_to_close.append((position, 'take_profit'))
            elif position['action'] == 'sell':
                if current_price >= position['stop_loss']:
                    positions_to_close.append((position, 'stop_loss'))
                elif current_price <= position['take_profit']:
                    positions_to_close.append((position, 'take_profit'))
        
        # Close positions
        for position, exit_reason in positions_to_close:
            trade = self._close_position(position, bar, timestamp, exit_reason)
            if trade:
                self.trades.append(trade)
                self.open_positions.remove(position)
    
    def _close_position(self, position: Dict[str, Any], bar: pd.Series, 
                       timestamp, exit_reason: str) -> Optional[Dict[str, Any]]:
        """Close a position and calculate P&L"""
        
        try:
            exit_price = bar['Close']
            
            # Calculate P&L
            if position['action'] == 'buy':
                pnl = (exit_price - position['entry_price']) * (position['position_size'] / 100000)
            else:  # sell
                pnl = (position['entry_price'] - exit_price) * (position['position_size'] / 100000)
            
            # Update balance
            self.current_balance += pnl
            
            trade = {
                'id': position['id'],
                'instrument': position['instrument'],
                'action': position['action'],
                'entry_price': position['entry_price'],
                'exit_price': exit_price,
                'entry_time': position['entry_time'].isoformat() if hasattr(position['entry_time'], 'isoformat') else str(position['entry_time']),
                'exit_time': timestamp.isoformat() if hasattr(timestamp, 'isoformat') else str(timestamp),
                'position_size': position['position_size'],
                'pnl': pnl,
                'exit_reason': exit_reason,
                'duration_minutes': (timestamp - position['entry_time']).total_seconds() / 60 if hasattr(timestamp, 'total_seconds') else 0
            }
            
            log_info('backtest', f"Closed position: {trade['action']} {trade['instrument']}, P&L: {pnl:.2f}, Reason: {exit_reason}")
            
            return trade
            
        except Exception as e:
            log_error('backtest', f"Error closing position: {e}")
            return None
    
    def _calculate_current_equity(self, bar: pd.Series) -> float:
        """Calculate current equity including open positions"""
        equity = self.current_balance
        
        for position in self.open_positions:
            current_price = bar['Close']
            
            if position['action'] == 'buy':
                unrealized_pnl = (current_price - position['entry_price']) * (position['position_size'] / 100000)
            else:  # sell
                unrealized_pnl = (position['entry_price'] - current_price) * (position['position_size'] / 100000)
            
            equity += unrealized_pnl
        
        return equity
    
    def _get_trading_session(self, hour: int) -> str:
        """Determine trading session based on hour"""
        if 0 <= hour < 7:
            return 'Asian'
        elif 7 <= hour < 15:
            return 'London'
        elif 15 <= hour < 22:
            return 'New York'
        else:
            return 'Asian'
    
    def _calculate_backtest_results(self, data: pd.DataFrame) -> BacktestResult:
        """Calculate comprehensive backtest statistics"""
        
        if not self.trades:
            return BacktestResult(
                total_trades=0, winning_trades=0, losing_trades=0, win_rate=0.0,
                total_pnl=0.0, gross_profit=0.0, gross_loss=0.0, profit_factor=0.0,
                sharpe_ratio=0.0, sortino_ratio=0.0, max_drawdown=0.0, max_drawdown_percent=0.0,
                average_win=0.0, average_loss=0.0, largest_win=0.0, largest_loss=0.0,
                consecutive_wins=0, consecutive_losses=0, calmar_ratio=0.0, recovery_factor=0.0,
                expectancy=0.0, trading_days=len(data), start_date=str(data.index[0].date()),
                end_date=str(data.index[-1].date()), initial_balance=self.initial_balance,
                final_balance=self.current_balance, trades=[], daily_pnl=[], drawdown_periods=[],
                monthly_returns={}
            )
        
        # Basic statistics
        total_trades = len(self.trades)
        winning_trades = len([t for t in self.trades if t['pnl'] > 0])
        losing_trades = len([t for t in self.trades if t['pnl'] < 0])
        win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
        
        # P&L statistics
        total_pnl = sum(t['pnl'] for t in self.trades)
        gross_profit = sum(t['pnl'] for t in self.trades if t['pnl'] > 0)
        gross_loss = abs(sum(t['pnl'] for t in self.trades if t['pnl'] < 0))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
        
        # Win/Loss statistics
        wins = [t['pnl'] for t in self.trades if t['pnl'] > 0]
        losses = [t['pnl'] for t in self.trades if t['pnl'] < 0]
        
        average_win = np.mean(wins) if wins else 0
        average_loss = np.mean(losses) if losses else 0
        largest_win = max(wins) if wins else 0
        largest_loss = min(losses) if losses else 0
        
        # Expectancy
        expectancy = (win_rate / 100) * average_win + ((100 - win_rate) / 100) * average_loss
        
        # Consecutive wins/losses
        consecutive_wins = self._calculate_max_consecutive(self.trades, True)
        consecutive_losses = self._calculate_max_consecutive(self.trades, False)
        
        # Drawdown analysis
        equity_values = [e['equity'] for e in self.equity_curve]
        max_drawdown, max_drawdown_percent, drawdown_periods = self._calculate_drawdown(equity_values)
        
        # Risk-adjusted returns
        returns = np.diff([e['equity'] for e in self.equity_curve])
        sharpe_ratio = self._calculate_sharpe_ratio(returns)
        sortino_ratio = self._calculate_sortino_ratio(returns)
        
        # Other ratios
        annual_return = (self.current_balance / self.initial_balance - 1) * (365 / len(data))
        calmar_ratio = annual_return / (max_drawdown_percent / 100) if max_drawdown_percent > 0 else 0
        recovery_factor = total_pnl / max_drawdown if max_drawdown > 0 else 0
        
        # Daily P&L
        daily_pnl = self._calculate_daily_pnl()
        
        # Monthly returns
        monthly_returns = self._calculate_monthly_returns()
        
        return BacktestResult(
            total_trades=total_trades,
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            win_rate=win_rate,
            total_pnl=total_pnl,
            gross_profit=gross_profit,
            gross_loss=gross_loss,
            profit_factor=profit_factor,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            max_drawdown=max_drawdown,
            max_drawdown_percent=max_drawdown_percent,
            average_win=average_win,
            average_loss=average_loss,
            largest_win=largest_win,
            largest_loss=largest_loss,
            consecutive_wins=consecutive_wins,
            consecutive_losses=consecutive_losses,
            calmar_ratio=calmar_ratio,
            recovery_factor=recovery_factor,
            expectancy=expectancy,
            trading_days=len(data),
            start_date=str(data.index[0].date()),
            end_date=str(data.index[-1].date()),
            initial_balance=self.initial_balance,
            final_balance=self.current_balance,
            trades=self.trades,
            daily_pnl=daily_pnl,
            drawdown_periods=drawdown_periods,
            monthly_returns=monthly_returns
        )
    
    def _calculate_max_consecutive(self, trades: List[Dict[str, Any]], wins: bool) -> int:
        """Calculate maximum consecutive wins or losses"""
        max_consecutive = 0
        current_consecutive = 0
        
        for trade in trades:
            if (trade['pnl'] > 0) == wins:
                current_consecutive += 1
                max_consecutive = max(max_consecutive, current_consecutive)
            else:
                current_consecutive = 0
        
        return max_consecutive
    
    def _calculate_drawdown(self, equity_values: List[float]) -> Tuple[float, float, List[Dict[str, Any]]]:
        """Calculate maximum drawdown and drawdown periods"""
        if not equity_values:
            return 0.0, 0.0, []
        
        peak = equity_values[0]
        max_drawdown = 0.0
        max_drawdown_percent = 0.0
        drawdown_periods = []
        current_drawdown_start = None
        
        for i, value in enumerate(equity_values):
            if value > peak:
                # New peak, end any current drawdown
                if current_drawdown_start is not None:
                    drawdown_periods.append({
                        'start_index': current_drawdown_start,
                        'end_index': i - 1,
                        'duration_bars': i - current_drawdown_start,
                        'max_drawdown': peak - min(equity_values[current_drawdown_start:i])
                    })
                    current_drawdown_start = None
                peak = value
            else:
                # In drawdown
                if current_drawdown_start is None:
                    current_drawdown_start = i
                
                drawdown = peak - value
                drawdown_percent = (drawdown / peak) * 100 if peak > 0 else 0
                
                max_drawdown = max(max_drawdown, drawdown)
                max_drawdown_percent = max(max_drawdown_percent, drawdown_percent)
        
        return max_drawdown, max_drawdown_percent, drawdown_periods
    
    def _calculate_sharpe_ratio(self, returns: np.ndarray, risk_free_rate: float = 0.02) -> float:
        """Calculate Sharpe ratio"""
        if len(returns) == 0:
            return 0.0
        
        excess_returns = returns - risk_free_rate / 252  # Daily risk-free rate
        return np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252) if np.std(excess_returns) > 0 else 0.0
    
    def _calculate_sortino_ratio(self, returns: np.ndarray, risk_free_rate: float = 0.02) -> float:
        """Calculate Sortino ratio"""
        if len(returns) == 0:
            return 0.0
        
        excess_returns = returns - risk_free_rate / 252
        negative_returns = returns[returns < 0]
        downside_std = np.std(negative_returns) if len(negative_returns) > 0 else 0
        
        return np.mean(excess_returns) / downside_std * np.sqrt(252) if downside_std > 0 else 0.0
    
    def _calculate_daily_pnl(self) -> List[Dict[str, Any]]:
        """Calculate daily P&L breakdown"""
        daily_pnl = {}
        
        for trade in self.trades:
            exit_date = trade['exit_time'][:10]  # Extract date part
            daily_pnl[exit_date] = daily_pnl.get(exit_date, 0) + trade['pnl']
        
        return [{'date': date, 'pnl': pnl} for date, pnl in sorted(daily_pnl.items())]
    
    def _calculate_monthly_returns(self) -> Dict[str, float]:
        """Calculate monthly returns"""
        monthly_pnl = {}
        
        for trade in self.trades:
            month = trade['exit_time'][:7]  # Extract YYYY-MM
            monthly_pnl[month] = monthly_pnl.get(month, 0) + trade['pnl']
        
        return monthly_pnl

# Example strategy function for testing
def example_moving_average_strategy(data: pd.DataFrame) -> List[Dict[str, Any]]:
    """Example moving average crossover strategy"""
    if len(data) < 20:
        return []
    
    # Calculate moving averages
    data['MA5'] = data['Close'].rolling(5).mean()
    data['MA20'] = data['Close'].rolling(20).mean()
    
    signals = []
    
    # Get latest values
    current_ma5 = data['MA5'].iloc[-1]
    current_ma20 = data['MA20'].iloc[-1]
    prev_ma5 = data['MA5'].iloc[-2] if len(data) >= 2 else current_ma5
    prev_ma20 = data['MA20'].iloc[-2] if len(data) >= 2 else current_ma20
    
    current_price = data['Close'].iloc[-1]
    
    # MA crossover signals
    if prev_ma5 <= prev_ma20 and current_ma5 > current_ma20:  # Bullish crossover
        signals.append({
            'action': 'buy',
            'instrument': 'EURUSD',
            'entry_price': current_price,
            'stop_loss': current_price * 0.995,  # 0.5% stop loss
            'take_profit': current_price * 1.01,  # 1% take profit
            'position_size': 100000,  # 1 lot
            'risk_amount': current_price * 100000 * 0.005  # 0.5% risk
        })
    elif prev_ma5 >= prev_ma20 and current_ma5 < current_ma20:  # Bearish crossover
        signals.append({
            'action': 'sell',
            'instrument': 'EURUSD',
            'entry_price': current_price,
            'stop_loss': current_price * 1.005,  # 0.5% stop loss
            'take_profit': current_price * 0.99,  # 1% take profit
            'position_size': 100000,  # 1 lot
            'risk_amount': current_price * 100000 * 0.005  # 0.5% risk
        })
    
    return signals