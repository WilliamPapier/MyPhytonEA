"""
Simple test scanner to verify functionality
"""
import requests
import json
from datetime import datetime
import random

# Test setup data
test_setups = [
    {
        "symbol": "EURUSD",
        "timeframe": "1m",
        "open": 1.1000,
        "high": 1.1015,
        "low": 1.0985,
        "close": 1.1010,
        "volume": 1500,
        "liquidity_sweep_high": 1,
        "order_block": 0,
        "pin_bar": 0,
        "ma_5_1m": 1.1008,
        "ma_20_1m": 1.0995,
        "rsi_14": 68,
        "volatility_1m": 0.0018
    },
    {
        "symbol": "GBPUSD",
        "timeframe": "5m",
        "open": 1.2500,
        "high": 1.2525,
        "low": 1.2485,
        "close": 1.2520,
        "volume": 1800,
        "liquidity_sweep_high": 1,
        "order_block": 1,
        "pin_bar": 0,
        "ma_5_1m": 1.2515,
        "ma_20_1m": 1.2500,
        "rsi_14": 72,
        "volatility_1m": 0.0022
    },
    {
        "symbol": "USDJPY",
        "timeframe": "1m",
        "open": 150.00,
        "high": 150.25,
        "low": 149.75,
        "close": 150.15,
        "volume": 1200,
        "liquidity_sweep_high": 0,
        "order_block": 1,
        "pin_bar": 1,
        "ma_5_1m": 150.10,
        "ma_20_1m": 149.95,
        "rsi_14": 58,
        "volatility_1m": 0.15
    }
]

def submit_setup(setup):
    """Submit a setup to the backend"""
    try:
        setup["timestamp"] = datetime.now().isoformat()
        
        response = requests.post("http://127.0.0.1:8000/scanner/submit", 
                               json=setup, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            status = result.get("status")
            score = result.get("score", {})
            
            print(f"✓ {setup['symbol']} {setup['timeframe']}: {score.get('pattern', 'N/A')} "
                  f"({score.get('probability', 0):.1%}) - {status.upper()}")
            
            if status == "accepted":
                return True
        else:
            print(f"✗ {setup['symbol']}: HTTP {response.status_code}")
    except Exception as e:
        print(f"✗ {setup['symbol']}: Error - {e}")
    
    return False

def main():
    print("Testing Enhanced Scanner System")
    print("=" * 40)
    
    # Check backend
    try:
        response = requests.get("http://127.0.0.1:8000/health", timeout=5)
        if response.status_code == 200:
            print("✓ Backend is healthy")
        else:
            print("✗ Backend not responding")
            return
    except:
        print("✗ Cannot connect to backend")
        return
    
    # Get current config
    try:
        response = requests.get("http://127.0.0.1:8000/config", timeout=5)
        if response.status_code == 200:
            config = response.json()
            print(f"Current threshold: {config.get('probability_threshold', 0):.1%}")
    except:
        print("Could not get config")
    
    print("\nSubmitting test setups...")
    accepted = 0
    
    for setup in test_setups:
        if submit_setup(setup):
            accepted += 1
    
    print(f"\nResults: {accepted}/{len(test_setups)} setups accepted")
    
    # Check active setups
    try:
        response = requests.get("http://127.0.0.1:8000/setups", timeout=5)
        if response.status_code == 200:
            setups_data = response.json()
            print(f"Active setups in system: {setups_data.get('count', 0)}")
    except:
        print("Could not check active setups")

if __name__ == "__main__":
    main()