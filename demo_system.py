#!/usr/bin/env python3
"""
Demo script to test MyPhytonEA Trading System v2.0 features

This script demonstrates:
1. Prop firm detection
2. Advanced logging
3. Notification system  
4. Resource monitoring
5. Backtest functionality
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import json

# Import our systems
from prop_firm_system import prop_firm_detector
from advanced_logging import trading_logger, log_info, log_error, log_warning
from notification_system import notification_manager, send_notification
from resource_monitor import resource_monitor
from backtest_system import BacktestEngine, example_moving_average_strategy

def demo_prop_firm_detection():
    """Demo prop firm detection functionality"""
    print("\n" + "="*50)
    print("🏢 PROP FIRM DETECTION DEMO")
    print("="*50)
    
    # Test different account types
    test_accounts = [
        {
            'account_name': 'FTMO Challenge 50k',
            'broker': 'Purple Trading',
            'balance': 50000,
            'server': 'demo.server.com',
            'account_type': 'demo'
        },
        {
            'account_name': 'Regular Trading Account',
            'broker': 'XM Global',
            'balance': 1000,
            'server': 'live.server.com',
            'account_type': 'live'
        },
        {
            'account_name': 'MFF Funded Account 25k',
            'broker': 'EightCap',
            'balance': 25000,
            'server': 'mff.demo.com',
            'account_type': 'demo'
        }
    ]
    
    for i, account in enumerate(test_accounts, 1):
        print(f"\n--- Test Account {i} ---")
        print(f"Account: {account['account_name']}")
        print(f"Broker: {account['broker']}")
        print(f"Balance: ${account['balance']:,}")
        
        # Detect prop firm
        is_prop_firm, rules = prop_firm_detector.detect_prop_firm(account)
        
        if is_prop_firm:
            print(f"✅ PROP FIRM DETECTED: {rules.firm_name}")
            print(f"   Daily Loss Limit: ${rules.max_daily_loss}")
            print(f"   Max Risk per Trade: {rules.max_risk_per_trade*100}%")
            print(f"   Allowed Sessions: {', '.join(rules.allowed_sessions)}")
            print(f"   Max Open Positions: {rules.max_open_positions}")
        else:
            print("❌ No prop firm detected - Regular retail account")

def demo_logging_system():
    """Demo advanced logging functionality"""
    print("\n" + "="*50)
    print("📝 ADVANCED LOGGING DEMO")
    print("="*50)
    
    # Test different log levels and categories
    log_info('trading', 'Trading system initialized successfully')
    log_warning('risk', 'Daily loss approaching 70% of limit')
    log_error('ml', 'Failed to load ML model - using fallback')
    
    # Test trade logging
    sample_trade = {
        'id': 'TRADE_001',
        'instrument': 'EURUSD',
        'action': 'BUY',
        'amount': 100000,
        'entry_price': 1.1234,
        'exit_price': 1.1254,
        'pnl': 200.0
    }
    
    trading_logger.log_trade(sample_trade)
    
    # Test prop firm logging
    trading_logger.log_prop_firm_event(
        'RULE_VIOLATION',
        'Daily loss limit exceeded',
        {'account_name': 'FTMO Challenge', 'broker': 'Purple Trading', 'balance': 50000}
    )
    
    # Get logging stats
    stats = trading_logger.get_stats()
    print(f"\nLogging Statistics:")
    print(f"  Errors logged: {stats['error_count']}")
    print(f"  Warnings logged: {stats['warning_count']}")
    print(f"  Trades logged: {stats['trade_count']}")
    print(f"  Queue size: {stats['queue_size']}")

def demo_notification_system():
    """Demo notification functionality"""
    print("\n" + "="*50)
    print("🔔 NOTIFICATION SYSTEM DEMO")
    print("="*50)
    
    # Send different types of notifications
    send_notification('trade', 'New trade opened: BUY EURUSD at 1.1234', 'Trade Alert')
    send_notification('risk', 'Daily loss limit at 80%', 'Risk Warning', priority='high')
    send_notification('prop_firm', 'FTMO account detected - rules now active', 'Prop Firm Alert')
    send_notification('system', 'High CPU usage detected (85%)', 'System Alert')
    
    time.sleep(1)  # Allow notifications to process
    
    # Get notification stats
    stats = notification_manager.get_notification_stats()
    print(f"\nNotification Statistics:")
    print(f"  Total sent: {stats['total_sent']}")
    print(f"  Sent last 24h: {stats['sent_last_24h']}")
    print(f"  Queue size: {stats['queue_size']}")
    print(f"  Channels enabled:")
    for channel, enabled in stats['channels_enabled'].items():
        status = "✅" if enabled else "❌"
        print(f"    {status} {channel.title()}")

def demo_resource_monitoring():
    """Demo resource monitoring functionality"""
    print("\n" + "="*50)
    print("⚙️ RESOURCE MONITORING DEMO")
    print("="*50)
    
    # Get current system stats
    stats = resource_monitor.get_current_stats()
    
    print(f"System Statistics:")
    print(f"  CPU Usage: {stats['cpu']['percent']:.1f}%")
    print(f"  Memory Usage: {stats['memory']['percent']:.1f}%")
    print(f"  Available Memory: {stats['memory']['available_gb']:.1f} GB")
    print(f"  Disk Usage: {stats['disk']['percent']:.1f}%")
    print(f"  Free Disk Space: {stats['disk']['free_gb']:.1f} GB")
    print(f"  Network Connected: {'✅' if stats['network']['connected'] else '❌'}")
    
    # Get system health
    health = resource_monitor.get_trading_system_health()
    print(f"\nSystem Health: {health['status'].upper()}")
    if health['issues']:
        print("Issues detected:")
        for issue in health['issues']:
            print(f"  ⚠️ {issue}")

def demo_backtest_system():
    """Demo backtesting functionality"""
    print("\n" + "="*50)
    print("📊 BACKTEST SYSTEM DEMO")
    print("="*50)
    
    # Generate sample price data
    print("Generating sample EURUSD data...")
    dates = pd.date_range(start='2024-01-01', end='2024-02-01', freq='1H')
    
    # Create realistic price data
    initial_price = 1.1000
    returns = np.random.normal(0, 0.0005, len(dates))  # Small random returns
    prices = initial_price * np.exp(np.cumsum(returns))
    
    # Create OHLC data
    data = pd.DataFrame({
        'Open': prices,
        'High': prices * (1 + np.abs(np.random.normal(0, 0.0002, len(dates)))),
        'Low': prices * (1 - np.abs(np.random.normal(0, 0.0002, len(dates)))),
        'Close': prices,
        'Volume': np.random.randint(1000, 10000, len(dates))
    }, index=dates)
    
    # Ensure High >= Open,Close and Low <= Open,Close
    data['High'] = np.maximum(data['High'], np.maximum(data['Open'], data['Close']))
    data['Low'] = np.minimum(data['Low'], np.minimum(data['Open'], data['Close']))
    
    print(f"Generated {len(data)} bars of data from {data.index[0]} to {data.index[-1]}")
    
    # Initialize backtest engine
    backtest_engine = BacktestEngine(initial_balance=10000)
    
    # Test with prop firm simulation
    backtest_engine.set_prop_firm_simulation('ftmo')
    
    print("\nRunning backtest with Moving Average strategy...")
    
    # Run backtest
    results = backtest_engine.run_backtest(data, example_moving_average_strategy)
    
    # Display results
    print(f"\n📈 BACKTEST RESULTS:")
    print(f"  Period: {results.start_date} to {results.end_date}")
    print(f"  Trading Days: {results.trading_days}")
    print(f"  Initial Balance: ${results.initial_balance:,.2f}")
    print(f"  Final Balance: ${results.final_balance:,.2f}")
    print(f"  Total Return: {((results.final_balance / results.initial_balance) - 1) * 100:.2f}%")
    print(f"  Total Trades: {results.total_trades}")
    print(f"  Win Rate: {results.win_rate:.1f}%")
    print(f"  Profit Factor: {results.profit_factor:.2f}")
    print(f"  Max Drawdown: ${results.max_drawdown:.2f} ({results.max_drawdown_percent:.1f}%)")
    print(f"  Sharpe Ratio: {results.sharpe_ratio:.2f}")
    print(f"  Sortino Ratio: {results.sortino_ratio:.2f}")
    print(f"  Expectancy: ${results.expectancy:.2f}")
    
    if backtest_engine.prop_firm_violations:
        print(f"\n⚠️ Prop Firm Violations: {len(backtest_engine.prop_firm_violations)}")
        for violation in backtest_engine.prop_firm_violations[:3]:  # Show first 3
            print(f"  - {violation['type']}: ${violation['amount']:.2f} (limit: ${violation['limit']:.2f})")

def main():
    """Run all demos"""
    print("🚀 MyPhytonEA Trading System v2.0 - DEMO")
    print("Advanced Trading System with Prop Firm Integration")
    print("=" * 60)
    
    try:
        # Run all demo functions
        demo_prop_firm_detection()
        demo_logging_system()
        demo_notification_system()
        demo_resource_monitoring()
        demo_backtest_system()
        
        print("\n" + "="*60)
        print("✅ ALL DEMOS COMPLETED SUCCESSFULLY!")
        print("🚀 MyPhytonEA Trading System v2.0 is ready for trading!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()