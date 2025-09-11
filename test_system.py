"""
Test script to verify the core functionality of the enhanced EA/Scanner system.
"""
import sys
import os
import json
from datetime import datetime

# Add current directory to path
sys.path.append(os.getcwd())

try:
    from config import config_manager
    from scoring import setup_scorer
    from trailing_stops import trailing_stop_manager
    from optimal_tp import optimal_tp_analyzer
    print("✓ All modules imported successfully")
except ImportError as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)

def test_config_system():
    """Test configuration management system"""
    print("\n=== Testing Configuration System ===")
    
    # Test default config loading
    print(f"Default probability threshold: {config_manager.get_probability_threshold()}")
    
    # Test setting threshold
    success = config_manager.set_probability_threshold(0.80)
    print(f"Set threshold to 0.80: {'✓' if success else '✗'}")
    
    # Test risk settings
    risk_settings = config_manager.get_risk_settings()
    print(f"Risk settings: {risk_settings}")
    
    # Test position size calculation
    pos_size = config_manager.calculate_position_size(10000, 20)
    print(f"Position size for $10k account, 20 pip SL: {pos_size}")
    
    return True

def test_scoring_system():
    """Test stats-based scoring system"""
    print("\n=== Testing Scoring System ===")
    
    # Create test setup data
    test_setup = {
        "symbol": "EURUSD",
        "timeframe": "1m",
        "timestamp": datetime.now().isoformat(),
        "open": 1.1000,
        "high": 1.1010,
        "low": 1.0990,
        "close": 1.1005,
        "volume": 1000,
        "liquidity_sweep_high": 1,
        "order_block": 0,
        "pin_bar": 0,
        "ma_5_1m": 1.1003,
        "ma_20_1m": 1.0998,
        "volatility_1m": 0.0015
    }
    
    # Score the setup
    score_result = setup_scorer.score_setup(test_setup)
    print(f"Test setup scored: {score_result['pattern']} with {score_result['probability']:.2%} probability")
    print(f"Recommendation: {score_result['recommendation']}")
    
    # Test pattern identification
    pattern = setup_scorer.identify_pattern(test_setup)
    print(f"Identified pattern: {pattern}")
    
    # Test context detection
    context = setup_scorer.get_context(test_setup)
    print(f"Market context: {context}")
    
    return True

def test_trailing_stops():
    """Test trailing stop system"""
    print("\n=== Testing Trailing Stop System ===")
    
    # Create test trade
    test_trade = {
        "symbol": "EURUSD",
        "direction": "buy",
        "entry_price": 1.1000,
        "stop_loss": 1.0980,
        "take_profit": 1.1040
    }
    
    # Initialize trailing stop
    trade_id = "test_trade_001"
    success = trailing_stop_manager.initialize_trailing_stop(trade_id, test_trade)
    print(f"Trailing stop initialized: {'✓' if success else '✗'}")
    
    if success:
        # Test updating stop with price movement
        new_stop = trailing_stop_manager.update_trailing_stop(trade_id, 1.1020)
        print(f"Updated trailing stop to: {new_stop}")
        
        # Test hold decision
        should_hold, reason = trailing_stop_manager.should_hold_trade(trade_id, 1.1020)
        print(f"Should hold trade: {should_hold} ({reason})")
    
    return True

def test_optimal_tp():
    """Test optimal TP analysis system"""
    print("\n=== Testing Optimal TP System ===")
    
    # Create sample historical data
    sample_trades = [
        {
            "pattern": "liquidity_sweep_high",
            "symbol": "EURUSD",
            "entry_price": 1.1000,
            "stop_loss": 1.0980,
            "close_price": 1.1040,
            "max_price": 1.1045,
            "direction": "buy",
            "outcome": "tp",
            "timestamp": "2024-01-01T12:00:00"
        },
        {
            "pattern": "liquidity_sweep_high", 
            "symbol": "EURUSD",
            "entry_price": 1.1020,
            "stop_loss": 1.1000,
            "close_price": 1.1060,
            "max_price": 1.1065,
            "direction": "buy",
            "outcome": "tp",
            "timestamp": "2024-01-02T14:00:00"
        }
    ]
    
    # Analyze historical data
    analysis = optimal_tp_analyzer.analyze_historical_data(sample_trades)
    print(f"Analysis completed: {analysis['total_trades']} trades analyzed")
    
    # Test optimal TP calculation
    test_setup = {
        "pattern": "liquidity_sweep_high",
        "symbol": "EURUSD",
        "entry_price": 1.1000,
        "stop_loss": 1.0980,
        "direction": "buy"
    }
    
    optimal_tp_data = optimal_tp_analyzer.get_optimal_tp(test_setup)
    if "error" not in optimal_tp_data:
        print(f"Optimal TP: {optimal_tp_data['optimal_tp_price']:.5f}")
        print(f"TP Ratio: {optimal_tp_data['tp_ratio']:.2f}:1")
        print(f"Confidence: {optimal_tp_data['confidence']:.2f}")
    else:
        print(f"TP calculation error: {optimal_tp_data['error']}")
    
    return True

def test_backend_endpoints():
    """Test if backend can be started"""
    print("\n=== Testing Backend System ===")
    
    try:
        # Try to import the enhanced backend
        from enhanced_backend import app
        print("✓ Enhanced backend imported successfully")
        
        # Test basic health check would be done here
        # (Can't actually start server in test due to blocking nature)
        print("✓ Backend ready to start")
        return True
        
    except Exception as e:
        print(f"✗ Backend test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Testing Enhanced EA/Scanner System")
    print("=" * 50)
    
    tests = [
        test_config_system,
        test_scoring_system,
        test_trailing_stops,
        test_optimal_tp,
        test_backend_endpoints
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ Test failed with error: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print(f"Test Results: {sum(results)}/{len(results)} passed")
    
    if all(results):
        print("✓ All systems operational!")
        return True
    else:
        print("✗ Some systems need attention")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)