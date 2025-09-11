"""
Stats-based scoring system for trading setups using classic win rate logic.
Modular design allows for future ML integration while maintaining transparency.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json
import os
from collections import defaultdict

class SetupScorer:
    """
    Stats-based scoring system that tracks pattern performance and calculates
    probability based on historical win rates in specific contexts.
    """
    
    def __init__(self, history_file: str = "setup_history.json"):
        self.history_file = history_file
        self.setup_history = self._load_history()
        
    def _load_history(self) -> Dict:
        """Load historical setup performance data"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading setup history: {e}")
        
        return {
            "patterns": {},  # pattern_name -> context -> {wins, losses, total}
            "instruments": {},  # instrument -> pattern -> {wins, losses, total}
            "timeframes": {},   # timeframe -> pattern -> {wins, losses, total}
            "last_updated": datetime.now().isoformat()
        }
    
    def _save_history(self) -> bool:
        """Save historical data to file"""
        try:
            self.setup_history["last_updated"] = datetime.now().isoformat()
            with open(self.history_file, 'w') as f:
                json.dump(self.setup_history, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving setup history: {e}")
            return False
    
    def identify_pattern(self, setup_data: Dict) -> str:
        """
        Identify the primary pattern from setup data.
        Returns a standardized pattern name.
        """
        patterns = []
        
        # Check for specific patterns based on setup data
        if setup_data.get('liquidity_sweep_high', 0) == 1:
            patterns.append('liquidity_sweep_high')
        if setup_data.get('liquidity_sweep_low', 0) == 1:
            patterns.append('liquidity_sweep_low')
        if setup_data.get('order_block', 0) == 1:
            patterns.append('order_block')
        if setup_data.get('pin_bar', 0) == 1:
            patterns.append('pin_bar')
        
        # Check for trend patterns
        if 'ma_5_1m' in setup_data and 'ma_20_1m' in setup_data:
            ma5 = setup_data.get('ma_5_1m', 0)
            ma20 = setup_data.get('ma_20_1m', 0)
            if ma5 > ma20:
                patterns.append('uptrend')
            elif ma5 < ma20:
                patterns.append('downtrend')
        
        # Check for breakout patterns
        if 'high' in setup_data and 'low' in setup_data:
            high = setup_data.get('high', 0)
            low = setup_data.get('low', 0)
            close = setup_data.get('close', 0)
            range_size = high - low
            if range_size > 0:
                if (close - low) / range_size > 0.8:
                    patterns.append('high_close')
                elif (high - close) / range_size > 0.8:
                    patterns.append('low_close')
        
        # Return the most specific pattern or combination
        if len(patterns) == 0:
            return 'no_pattern'
        elif len(patterns) == 1:
            return patterns[0]
        else:
            return '_'.join(sorted(patterns))
    
    def get_context(self, setup_data: Dict) -> str:
        """
        Get the market context for the setup (trend, volatility, time of day, etc.)
        """
        context_parts = []
        
        # Market session
        timestamp = setup_data.get('timestamp', datetime.now().isoformat())
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            hour = dt.hour
            if 0 <= hour < 8:
                context_parts.append('asian')
            elif 8 <= hour < 16:
                context_parts.append('london')
            else:
                context_parts.append('ny')
        except:
            context_parts.append('unknown_session')
        
        # Volatility context
        if 'volatility_1m' in setup_data:
            vol = setup_data.get('volatility_1m', 0)
            if vol > 0.002:  # High volatility threshold
                context_parts.append('high_vol')
            elif vol > 0.001:
                context_parts.append('med_vol')
            else:
                context_parts.append('low_vol')
        
        # Trend context
        if 'ma_5_1m' in setup_data and 'ma_20_1m' in setup_data:
            ma5 = setup_data.get('ma_5_1m', 0)
            ma20 = setup_data.get('ma_20_1m', 0)
            if abs(ma5 - ma20) / ma20 > 0.01:  # Strong trend
                context_parts.append('trending')
            else:
                context_parts.append('ranging')
        
        return '_'.join(context_parts) if context_parts else 'default'
    
    def calculate_probability(self, pattern: str, context: str, 
                            instrument: str = None, timeframe: str = None) -> float:
        """
        Calculate probability based on historical performance.
        Uses multiple data sources and applies Bayesian-like reasoning.
        """
        probabilities = []
        min_samples = 5  # Minimum number of samples to trust the probability
        
        # 1. Pattern-specific probability in context
        pattern_key = f"{pattern}_{context}"
        if pattern in self.setup_history["patterns"]:
            if context in self.setup_history["patterns"][pattern]:
                stats = self.setup_history["patterns"][pattern][context]
                total = stats.get("total", 0)
                wins = stats.get("wins", 0)
                if total >= min_samples:
                    prob = wins / total
                    probabilities.append((prob, total))
        
        # 2. Instrument-specific probability
        if instrument and instrument in self.setup_history["instruments"]:
            if pattern in self.setup_history["instruments"][instrument]:
                stats = self.setup_history["instruments"][instrument][pattern]
                total = stats.get("total", 0)
                wins = stats.get("wins", 0)
                if total >= min_samples:
                    prob = wins / total
                    probabilities.append((prob, total))
        
        # 3. Timeframe-specific probability  
        if timeframe and timeframe in self.setup_history["timeframes"]:
            if pattern in self.setup_history["timeframes"][timeframe]:
                stats = self.setup_history["timeframes"][timeframe][pattern]
                total = stats.get("total", 0)
                wins = stats.get("wins", 0)
                if total >= min_samples:
                    prob = wins / total
                    probabilities.append((prob, total))
        
        # Weighted average based on sample sizes
        if probabilities:
            total_weight = sum(weight for _, weight in probabilities)
            weighted_prob = sum(prob * weight for prob, weight in probabilities) / total_weight
            return min(max(weighted_prob, 0.1), 0.95)  # Clamp between 10% and 95%
        
        # Default probability for unknown patterns
        return 0.5
    
    def score_setup(self, setup_data: Dict) -> Dict:
        """
        Score a trading setup and return comprehensive analysis.
        """
        pattern = self.identify_pattern(setup_data)
        context = self.get_context(setup_data)
        instrument = setup_data.get('symbol', setup_data.get('instrument', 'unknown'))
        timeframe = setup_data.get('timeframe', '1m')
        
        probability = self.calculate_probability(pattern, context, instrument, timeframe)
        
        # Calculate confidence based on data availability
        confidence = self._calculate_confidence(pattern, context, instrument, timeframe)
        
        # Determine signal strength
        signal_strength = self._calculate_signal_strength(setup_data, probability)
        
        return {
            "pattern": pattern,
            "context": context,
            "probability": probability,
            "confidence": confidence,
            "signal_strength": signal_strength,
            "instrument": instrument,
            "timeframe": timeframe,
            "timestamp": setup_data.get('timestamp', datetime.now().isoformat()),
            "raw_score": probability * confidence,
            "recommendation": self._get_recommendation(probability, confidence, signal_strength)
        }
    
    def _calculate_confidence(self, pattern: str, context: str, 
                            instrument: str, timeframe: str) -> float:
        """Calculate confidence based on available historical data"""
        total_samples = 0
        
        # Count samples from different sources
        pattern_key = f"{pattern}_{context}"
        if pattern in self.setup_history["patterns"]:
            if context in self.setup_history["patterns"][pattern]:
                total_samples += self.setup_history["patterns"][pattern][context].get("total", 0)
        
        if instrument in self.setup_history["instruments"]:
            if pattern in self.setup_history["instruments"][instrument]:
                total_samples += self.setup_history["instruments"][instrument][pattern].get("total", 0)
        
        if timeframe in self.setup_history["timeframes"]:
            if pattern in self.setup_history["timeframes"][timeframe]:
                total_samples += self.setup_history["timeframes"][timeframe][pattern].get("total", 0)
        
        # Convert sample count to confidence score
        if total_samples >= 100:
            return 0.95
        elif total_samples >= 50:
            return 0.85
        elif total_samples >= 20:
            return 0.75
        elif total_samples >= 10:
            return 0.65
        elif total_samples >= 5:
            return 0.55
        else:
            return 0.4  # Low confidence for new patterns
    
    def _calculate_signal_strength(self, setup_data: Dict, probability: float) -> str:
        """Calculate signal strength based on setup characteristics"""
        if probability >= 0.8:
            return "strong"
        elif probability >= 0.65:
            return "medium" 
        elif probability >= 0.5:
            return "weak"
        else:
            return "very_weak"
    
    def _get_recommendation(self, probability: float, confidence: float, 
                          signal_strength: str) -> str:
        """Get trading recommendation based on probability and confidence"""
        if probability >= 0.75 and confidence >= 0.7:
            return "trade"
        elif probability >= 0.65 and confidence >= 0.6:
            return "consider"
        elif probability >= 0.5 and confidence >= 0.5:
            return "monitor"
        else:
            return "ignore"
    
    def record_outcome(self, setup_score: Dict, outcome: str) -> bool:
        """
        Record the outcome of a setup (win/loss) to improve future scoring.
        """
        try:
            pattern = setup_score["pattern"]
            context = setup_score["context"]
            instrument = setup_score["instrument"]
            timeframe = setup_score["timeframe"]
            
            is_win = outcome.lower() in ['win', 'profit', 'tp']
            
            # Update pattern history
            if pattern not in self.setup_history["patterns"]:
                self.setup_history["patterns"][pattern] = {}
            if context not in self.setup_history["patterns"][pattern]:
                self.setup_history["patterns"][pattern][context] = {"wins": 0, "losses": 0, "total": 0}
            
            stats = self.setup_history["patterns"][pattern][context]
            if is_win:
                stats["wins"] += 1
            else:
                stats["losses"] += 1
            stats["total"] += 1
            
            # Update instrument history
            if instrument not in self.setup_history["instruments"]:
                self.setup_history["instruments"][instrument] = {}
            if pattern not in self.setup_history["instruments"][instrument]:
                self.setup_history["instruments"][instrument][pattern] = {"wins": 0, "losses": 0, "total": 0}
            
            inst_stats = self.setup_history["instruments"][instrument][pattern]
            if is_win:
                inst_stats["wins"] += 1
            else:
                inst_stats["losses"] += 1
            inst_stats["total"] += 1
            
            # Update timeframe history
            if timeframe not in self.setup_history["timeframes"]:
                self.setup_history["timeframes"][timeframe] = {}
            if pattern not in self.setup_history["timeframes"][timeframe]:
                self.setup_history["timeframes"][timeframe][pattern] = {"wins": 0, "losses": 0, "total": 0}
            
            tf_stats = self.setup_history["timeframes"][timeframe][pattern]
            if is_win:
                tf_stats["wins"] += 1
            else:
                tf_stats["losses"] += 1
            tf_stats["total"] += 1
            
            return self._save_history()
            
        except Exception as e:
            print(f"Error recording outcome: {e}")
            return False
    
    def get_performance_summary(self) -> Dict:
        """Get performance summary for all patterns"""
        summary = {
            "total_setups": 0,
            "total_wins": 0,
            "overall_win_rate": 0.0,
            "best_patterns": [],
            "worst_patterns": [],
            "by_instrument": {},
            "by_timeframe": {}
        }
        
        # Calculate overall statistics
        for pattern_data in self.setup_history["patterns"].values():
            for context_data in pattern_data.values():
                summary["total_setups"] += context_data.get("total", 0)
                summary["total_wins"] += context_data.get("wins", 0)
        
        if summary["total_setups"] > 0:
            summary["overall_win_rate"] = summary["total_wins"] / summary["total_setups"]
        
        # Find best and worst patterns
        pattern_performance = []
        for pattern, contexts in self.setup_history["patterns"].items():
            total_wins = sum(ctx.get("wins", 0) for ctx in contexts.values())
            total_trades = sum(ctx.get("total", 0) for ctx in contexts.values())
            if total_trades >= 10:  # Only include patterns with sufficient data
                win_rate = total_wins / total_trades
                pattern_performance.append((pattern, win_rate, total_trades))
        
        pattern_performance.sort(key=lambda x: x[1], reverse=True)
        summary["best_patterns"] = pattern_performance[:5]
        summary["worst_patterns"] = pattern_performance[-3:]
        
        return summary

# Global scorer instance
setup_scorer = SetupScorer()