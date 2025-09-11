"""
Enhanced scanner that integrates with the new scoring and configuration systems.
Uses global probability threshold and communicates with FastAPI backend.
"""
import asyncio
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import json
from typing import Dict, List, Optional
from config import config_manager
from scoring import setup_scorer

# Configuration
BACKEND_URL = "http://127.0.0.1:8000"
SCAN_INTERVAL = 30  # seconds between scans
MAX_RETRIES = 3

class EnhancedScanner:
    """
    Enhanced scanner that detects trading setups and submits them to the backend
    for scoring and threshold filtering.
    """
    
    def __init__(self):
        self.is_running = False
        self.last_scan_time = None
        self.scan_count = 0
        self.instruments = [
            "EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "NZDUSD", 
            "USDCHF", "USDCAD", "XAUUSD", "US30", "NAS100"
        ]
        self.timeframes = ["1m", "5m", "15m", "1h"]
        
    async def start_scanning(self):
        """Start the continuous scanning process"""
        self.is_running = True
        print(f"Enhanced Scanner started at {datetime.now()}")
        print(f"Scanning {len(self.instruments)} instruments every {SCAN_INTERVAL} seconds")
        
        while self.is_running:
            try:
                await self.perform_scan_cycle()
                await asyncio.sleep(SCAN_INTERVAL)
            except KeyboardInterrupt:
                print("Scanner stopped by user")
                break
            except Exception as e:
                print(f"Error in scan cycle: {e}")
                await asyncio.sleep(5)  # Short pause before retrying
    
    def stop_scanning(self):
        """Stop the scanning process"""
        self.is_running = False
        print("Scanner stop requested")
    
    async def perform_scan_cycle(self):
        """Perform one complete scan cycle across all instruments"""
        self.scan_count += 1
        self.last_scan_time = datetime.now()
        
        print(f"\n--- Scan #{self.scan_count} at {self.last_scan_time.strftime('%H:%M:%S')} ---")
        
        # Get current threshold from config
        threshold = config_manager.get_probability_threshold()
        print(f"Current probability threshold: {threshold:.2%}")
        
        # Scan all instruments
        total_setups = 0
        accepted_setups = 0
        
        for instrument in self.instruments:
            try:
                setups = await self.scan_instrument(instrument)
                total_setups += len(setups)
                
                for setup in setups:
                    if await self.submit_setup(setup):
                        accepted_setups += 1
                        
            except Exception as e:
                print(f"Error scanning {instrument}: {e}")
        
        print(f"Scan complete: {total_setups} setups found, {accepted_setups} accepted")
    
    async def scan_instrument(self, instrument: str) -> List[Dict]:
        """
        Scan a specific instrument for trading setups across multiple timeframes.
        """
        setups = []
        
        for timeframe in self.timeframes:
            try:
                # Simulate market data (in production, this would fetch from MT5 or broker API)
                market_data = self.generate_market_data(instrument, timeframe)
                
                # Detect patterns and create setup
                setup = self.detect_patterns(market_data, instrument, timeframe)
                
                if setup and self.is_valid_setup(setup):
                    setups.append(setup)
                    
            except Exception as e:
                print(f"Error scanning {instrument} {timeframe}: {e}")
        
        return setups
    
    def generate_market_data(self, instrument: str, timeframe: str) -> Dict:
        """
        Generate simulated market data (replace with real data feed in production).
        """
        # Base price for different instruments
        base_prices = {
            "EURUSD": 1.1000, "GBPUSD": 1.2500, "USDJPY": 150.00,
            "AUDUSD": 0.6700, "NZDUSD": 0.6200, "USDCHF": 0.9000,
            "USDCAD": 1.3500, "XAUUSD": 2000.00, "US30": 35000.00, "NAS100": 15000.00
        }
        
        base_price = base_prices.get(instrument, 1.0000)
        
        # Add some random movement
        price_change = np.random.normal(0, 0.001) * base_price
        current_price = base_price + price_change
        
        # Generate OHLC
        high_offset = abs(np.random.normal(0, 0.0005)) * base_price
        low_offset = abs(np.random.normal(0, 0.0005)) * base_price
        high = current_price + high_offset
        low = current_price - low_offset
        open_price = low + (high - low) * np.random.rand()
        close_price = low + (high - low) * np.random.rand()
        
        # Technical indicators (simplified)
        ma_5 = close_price * (1 + np.random.normal(0, 0.001))
        ma_20 = close_price * (1 + np.random.normal(0, 0.002))
        rsi = 30 + np.random.rand() * 40  # RSI between 30-70
        volatility = abs(np.random.normal(0.001, 0.0005))
        
        return {
            "symbol": instrument,
            "timeframe": timeframe,
            "timestamp": datetime.now().isoformat(),
            "open": open_price,
            "high": high,
            "low": low,
            "close": close_price,
            "volume": np.random.randint(500, 2000),
            "ma_5_1m": ma_5,
            "ma_20_1m": ma_20,
            "rsi_14": rsi,
            "volatility_1m": volatility
        }
    
    def detect_patterns(self, market_data: Dict, instrument: str, timeframe: str) -> Optional[Dict]:
        """
        Detect trading patterns in the market data.
        """
        open_price = market_data["open"]
        high = market_data["high"]
        low = market_data["low"]
        close = market_data["close"]
        volume = market_data["volume"]
        ma_5 = market_data["ma_5_1m"]
        ma_20 = market_data["ma_20_1m"]
        rsi = market_data["rsi_14"]
        
        # Pattern detection logic
        patterns = {}
        
        # Liquidity sweep patterns
        price_range = high - low
        if price_range > 0:
            # High liquidity sweep (price breaks recent highs)
            if np.random.rand() > 0.7:  # 30% chance
                patterns["liquidity_sweep_high"] = 1
            
            # Low liquidity sweep (price breaks recent lows)
            if np.random.rand() > 0.8:  # 20% chance
                patterns["liquidity_sweep_low"] = 1
        
        # Order block pattern (high volume with strong directional move)
        if volume > 1200 and abs(close - open) / price_range > 0.6:
            patterns["order_block"] = 1
        
        # Pin bar pattern (small body, long wick)
        body_size = abs(close - open)
        if body_size < price_range * 0.3:
            patterns["pin_bar"] = 1
        
        # Only create setup if at least one pattern is detected
        if not any(patterns.values()):
            return None
        
        setup = {
            **market_data,
            **patterns,
            "liquidity_sweep_high": patterns.get("liquidity_sweep_high", 0),
            "liquidity_sweep_low": patterns.get("liquidity_sweep_low", 0),
            "order_block": patterns.get("order_block", 0),
            "pin_bar": patterns.get("pin_bar", 0)
        }
        
        return setup
    
    def is_valid_setup(self, setup: Dict) -> bool:
        """
        Validate if a setup meets basic criteria before submission.
        """
        # Check minimum probability requirement
        min_prob = config_manager.get("min_setup_probability", 0.60)
        
        # Quick score to filter obvious bad setups
        quick_score = self.calculate_quick_score(setup)
        
        if quick_score < min_prob:
            return False
        
        # Check for required fields
        required_fields = ["symbol", "timeframe", "open", "high", "low", "close"]
        if not all(field in setup for field in required_fields):
            return False
        
        # Check for reasonable price values
        if setup["open"] <= 0 or setup["high"] <= 0 or setup["low"] <= 0 or setup["close"] <= 0:
            return False
        
        return True
    
    def calculate_quick_score(self, setup: Dict) -> float:
        """
        Calculate a quick probability score for initial filtering.
        """
        score = 0.5  # Base score
        
        # Pattern strength scoring
        pattern_count = sum([
            setup.get("liquidity_sweep_high", 0),
            setup.get("liquidity_sweep_low", 0),
            setup.get("order_block", 0),
            setup.get("pin_bar", 0)
        ])
        
        # Multiple patterns increase score
        if pattern_count >= 2:
            score += 0.15
        elif pattern_count == 1:
            score += 0.05
        
        # Trend alignment (MA crossover)
        ma_5 = setup.get("ma_5_1m", 0)
        ma_20 = setup.get("ma_20_1m", 0)
        if ma_5 > 0 and ma_20 > 0:
            if abs(ma_5 - ma_20) / ma_20 > 0.01:  # Strong trend
                score += 0.1
        
        # Volume confirmation
        volume = setup.get("volume", 0)
        if volume > 1500:  # High volume
            score += 0.1
        
        # RSI not in extreme zones
        rsi = setup.get("rsi_14", 50)
        if 30 < rsi < 70:  # Not overbought/oversold
            score += 0.05
        
        return min(score, 0.95)  # Cap at 95%
    
    async def submit_setup(self, setup: Dict) -> bool:
        """
        Submit a setup to the backend for scoring and processing.
        """
        try:
            url = f"{BACKEND_URL}/scanner/submit"
            
            # Convert numpy types to native Python types for JSON serialization
            json_setup = {}
            for key, value in setup.items():
                if isinstance(value, (np.integer, np.floating)):
                    json_setup[key] = value.item()
                else:
                    json_setup[key] = value
            
            response = requests.post(url, json=json_setup, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                status = result.get("status")
                
                if status == "accepted":
                    score = result.get("score", {})
                    print(f"✓ {setup['symbol']} {setup['timeframe']}: {score.get('pattern', 'N/A')} "
                          f"({score.get('probability', 0):.1%}) - ACCEPTED")
                    return True
                elif status == "filtered":
                    score = result.get("score", {})
                    threshold = result.get("required_threshold", 0)
                    print(f"○ {setup['symbol']} {setup['timeframe']}: {score.get('probability', 0):.1%} "
                          f"< {threshold:.1%} - FILTERED")
                    return False
                else:
                    print(f"? {setup['symbol']} {setup['timeframe']}: {status}")
                    return False
            else:
                print(f"✗ {setup['symbol']} {setup['timeframe']}: HTTP {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"✗ {setup['symbol']} {setup['timeframe']}: Connection error - {e}")
            return False
        except Exception as e:
            print(f"✗ {setup['symbol']} {setup['timeframe']}: Error - {e}")
            return False
    
    async def check_backend_status(self) -> bool:
        """
        Check if the backend is available and responsive.
        """
        try:
            response = requests.get(f"{BACKEND_URL}/health", timeout=5)
            if response.status_code == 200:
                health_data = response.json()
                print(f"Backend status: {health_data.get('status', 'unknown')}")
                return health_data.get('status') == 'healthy'
            return False
        except Exception as e:
            print(f"Backend check failed: {e}")
            return False
    
    def get_scan_statistics(self) -> Dict:
        """
        Get scanner statistics.
        """
        return {
            "scan_count": self.scan_count,
            "last_scan_time": self.last_scan_time.isoformat() if self.last_scan_time else None,
            "is_running": self.is_running,
            "instruments_count": len(self.instruments),
            "timeframes_count": len(self.timeframes),
            "scan_interval_seconds": SCAN_INTERVAL
        }

async def main():
    """
    Main function to run the enhanced scanner.
    """
    scanner = EnhancedScanner()
    
    # Check backend connectivity
    print("Checking backend connectivity...")
    if not await scanner.check_backend_status():
        print("Warning: Backend not available. Scanner will continue but setups won't be processed.")
    
    try:
        await scanner.start_scanning()
    except KeyboardInterrupt:
        print("\nScanner stopped by user")
    except Exception as e:
        print(f"Scanner error: {e}")
    finally:
        scanner.stop_scanning()
        print("Scanner shutdown complete")

if __name__ == "__main__":
    asyncio.run(main())