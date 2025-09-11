"""
Optimal Take Profit (TP) analysis system that uses historical data to determine
the best TP levels for each setup, maximizing reward while maintaining high win rates.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json
import os
from collections import defaultdict

class OptimalTPAnalyzer:
    """
    Analyzes historical trade data to determine optimal take profit levels
    for different patterns and market conditions.
    """
    
    def __init__(self, analysis_file: str = "tp_analysis.json"):
        self.analysis_file = analysis_file
        self.tp_analysis_data = self._load_analysis_data()
        
    def _load_analysis_data(self) -> Dict:
        """Load historical TP analysis data"""
        try:
            if os.path.exists(self.analysis_file):
                with open(self.analysis_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading TP analysis data: {e}")
        
        return {
            "pattern_analysis": {},  # pattern -> conditions -> TP_levels -> stats
            "symbol_analysis": {},   # symbol -> TP_levels -> stats
            "timeframe_analysis": {},  # timeframe -> TP_levels -> stats
            "market_conditions": {},  # volatility/trend -> TP_levels -> stats
            "last_updated": datetime.now().isoformat()
        }
    
    def _save_analysis_data(self) -> bool:
        """Save TP analysis data to file"""
        try:
            self.tp_analysis_data["last_updated"] = datetime.now().isoformat()
            with open(self.analysis_file, 'w') as f:
                json.dump(self.tp_analysis_data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving TP analysis data: {e}")
            return False
    
    def analyze_historical_data(self, trade_history: List[Dict]) -> Dict:
        """
        Analyze historical trade data to determine optimal TP levels.
        """
        if not trade_history:
            return {"status": "no_data"}
        
        analysis_results = {
            "total_trades": len(trade_history),
            "patterns_analyzed": {},
            "symbols_analyzed": {},
            "optimal_ratios": {},
            "recommendations": {}
        }
        
        # Group trades by pattern, symbol, and conditions
        pattern_groups = defaultdict(list)
        symbol_groups = defaultdict(list)
        
        for trade in trade_history:
            if trade.get("outcome") in ["win", "tp", "loss", "sl"]:
                pattern = trade.get("pattern", "unknown")
                symbol = trade.get("symbol", "unknown")
                
                pattern_groups[pattern].append(trade)
                symbol_groups[symbol].append(trade)
        
        # Analyze each pattern
        for pattern, trades in pattern_groups.items():
            if len(trades) >= 10:  # Minimum trades for analysis
                pattern_analysis = self._analyze_pattern_tp_levels(trades)
                analysis_results["patterns_analyzed"][pattern] = pattern_analysis
                
                # Update stored analysis
                if pattern not in self.tp_analysis_data["pattern_analysis"]:
                    self.tp_analysis_data["pattern_analysis"][pattern] = {}
                
                self.tp_analysis_data["pattern_analysis"][pattern].update(pattern_analysis)
        
        # Analyze each symbol
        for symbol, trades in symbol_groups.items():
            if len(trades) >= 10:
                symbol_analysis = self._analyze_symbol_tp_levels(trades)
                analysis_results["symbols_analyzed"][symbol] = symbol_analysis
                
                # Update stored analysis
                if symbol not in self.tp_analysis_data["symbol_analysis"]:
                    self.tp_analysis_data["symbol_analysis"][symbol] = {}
                
                self.tp_analysis_data["symbol_analysis"][symbol].update(symbol_analysis)
        
        # Calculate optimal risk-reward ratios
        analysis_results["optimal_ratios"] = self._calculate_optimal_ratios(trade_history)
        
        # Generate recommendations
        analysis_results["recommendations"] = self._generate_tp_recommendations()
        
        self._save_analysis_data()
        return analysis_results
    
    def _analyze_pattern_tp_levels(self, trades: List[Dict]) -> Dict:
        """Analyze optimal TP levels for a specific pattern"""
        tp_analysis = {
            "total_trades": len(trades),
            "win_rate_by_tp": {},
            "avg_profit_by_tp": {},
            "risk_reward_ratios": {},
            "optimal_tp_multiple": 1.5
        }
        
        # Test different TP multiples (1.0x to 5.0x of risk)
        tp_multiples = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0]
        
        for tp_multiple in tp_multiples:
            wins = 0
            total_profit = 0
            trade_count = 0
            
            for trade in trades:
                entry = trade.get("entry_price", 0)
                sl = trade.get("stop_loss", 0)
                actual_close = trade.get("close_price", entry)
                direction = trade.get("direction", "buy")
                
                if entry == 0 or sl == 0:
                    continue
                
                # Calculate risk and theoretical TP
                if direction.lower() == "buy":
                    risk = entry - sl
                    theoretical_tp = entry + (risk * tp_multiple)
                    
                    # Check if TP would have been hit
                    max_price = trade.get("max_price", actual_close)
                    if max_price >= theoretical_tp:
                        wins += 1
                        total_profit += risk * tp_multiple
                    else:
                        # Calculate actual profit/loss
                        actual_profit = actual_close - entry
                        total_profit += actual_profit
                else:
                    risk = sl - entry
                    theoretical_tp = entry - (risk * tp_multiple)
                    
                    min_price = trade.get("min_price", actual_close)
                    if min_price <= theoretical_tp:
                        wins += 1
                        total_profit += risk * tp_multiple
                    else:
                        actual_profit = entry - actual_close
                        total_profit += actual_profit
                
                trade_count += 1
            
            if trade_count > 0:
                win_rate = wins / trade_count
                avg_profit = total_profit / trade_count
                
                tp_analysis["win_rate_by_tp"][tp_multiple] = win_rate
                tp_analysis["avg_profit_by_tp"][tp_multiple] = avg_profit
                tp_analysis["risk_reward_ratios"][tp_multiple] = {
                    "ratio": tp_multiple,
                    "win_rate": win_rate,
                    "expectancy": avg_profit,
                    "score": win_rate * avg_profit  # Combined score
                }
        
        # Find optimal TP multiple
        best_score = 0
        for tp_mult, ratio_data in tp_analysis["risk_reward_ratios"].items():
            if ratio_data["score"] > best_score and ratio_data["win_rate"] >= 0.55:
                best_score = ratio_data["score"]
                tp_analysis["optimal_tp_multiple"] = tp_mult
        
        return tp_analysis
    
    def _analyze_symbol_tp_levels(self, trades: List[Dict]) -> Dict:
        """Analyze optimal TP levels for a specific symbol"""
        # Similar to pattern analysis but consider symbol-specific characteristics
        symbol_analysis = {
            "total_trades": len(trades),
            "avg_volatility": 0,
            "optimal_tp_pips": 0,
            "best_sessions": {},
            "volatility_based_tp": {}
        }
        
        # Calculate average volatility
        volatilities = [trade.get("atr", trade.get("volatility", 0)) for trade in trades]
        volatilities = [v for v in volatilities if v > 0]
        if volatilities:
            symbol_analysis["avg_volatility"] = np.mean(volatilities)
        
        # Analyze by market session
        sessions = {"asian": [], "london": [], "ny": []}
        for trade in trades:
            timestamp = trade.get("timestamp", "")
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                hour = dt.hour
                if 0 <= hour < 8:
                    sessions["asian"].append(trade)
                elif 8 <= hour < 16:
                    sessions["london"].append(trade)
                else:
                    sessions["ny"].append(trade)
            except:
                continue
        
        for session, session_trades in sessions.items():
            if len(session_trades) >= 5:
                session_analysis = self._analyze_pattern_tp_levels(session_trades)
                symbol_analysis["best_sessions"][session] = {
                    "optimal_tp": session_analysis.get("optimal_tp_multiple", 1.5),
                    "win_rate": max(session_analysis.get("win_rate_by_tp", {}).values()) if session_analysis.get("win_rate_by_tp") else 0,
                    "trade_count": len(session_trades)
                }
        
        return symbol_analysis
    
    def _calculate_optimal_ratios(self, trade_history: List[Dict]) -> Dict:
        """Calculate overall optimal risk-reward ratios"""
        ratios = {
            "conservative": {"ratio": 1.5, "min_win_rate": 0.65},
            "balanced": {"ratio": 2.0, "min_win_rate": 0.55},
            "aggressive": {"ratio": 3.0, "min_win_rate": 0.45}
        }
        
        # Test each ratio against historical data
        for ratio_name, ratio_data in ratios.items():
            test_results = self._test_ratio_performance(trade_history, ratio_data["ratio"])
            ratios[ratio_name]["actual_win_rate"] = test_results.get("win_rate", 0)
            ratios[ratio_name]["expectancy"] = test_results.get("expectancy", 0)
            ratios[ratio_name]["recommended"] = (
                test_results.get("win_rate", 0) >= ratio_data["min_win_rate"] and
                test_results.get("expectancy", 0) > 0
            )
        
        return ratios
    
    def _test_ratio_performance(self, trades: List[Dict], tp_ratio: float) -> Dict:
        """Test performance of a specific TP ratio"""
        wins = 0
        total_profit = 0
        trade_count = 0
        
        for trade in trades:
            entry = trade.get("entry_price", 0)
            sl = trade.get("stop_loss", 0)
            direction = trade.get("direction", "buy")
            
            if entry == 0 or sl == 0:
                continue
            
            if direction.lower() == "buy":
                risk = entry - sl
                theoretical_tp = entry + (risk * tp_ratio)
                max_price = trade.get("max_price", trade.get("close_price", entry))
                
                if max_price >= theoretical_tp:
                    wins += 1
                    total_profit += risk * tp_ratio
                else:
                    actual_profit = trade.get("close_price", entry) - entry
                    total_profit += actual_profit
            else:
                risk = sl - entry
                theoretical_tp = entry - (risk * tp_ratio)
                min_price = trade.get("min_price", trade.get("close_price", entry))
                
                if min_price <= theoretical_tp:
                    wins += 1
                    total_profit += risk * tp_ratio
                else:
                    actual_profit = entry - trade.get("close_price", entry)
                    total_profit += actual_profit
            
            trade_count += 1
        
        if trade_count > 0:
            win_rate = wins / trade_count
            expectancy = total_profit / trade_count
            return {"win_rate": win_rate, "expectancy": expectancy, "total_trades": trade_count}
        
        return {"win_rate": 0, "expectancy": 0, "total_trades": 0}
    
    def _generate_tp_recommendations(self) -> Dict:
        """Generate TP recommendations based on analysis"""
        recommendations = {
            "general": {
                "conservative_trader": "Use 1.5:1 ratio for 65%+ win rate",
                "balanced_trader": "Use 2:1 ratio for 55%+ win rate",
                "aggressive_trader": "Use 3:1 ratio for 45%+ win rate"
            },
            "by_pattern": {},
            "by_symbol": {},
            "dynamic_adjustments": {
                "high_volatility": "Increase TP by 25% during high volatility",
                "low_volatility": "Decrease TP by 15% during low volatility",
                "trending_market": "Trail TP as trend continues",
                "ranging_market": "Use fixed TP at support/resistance"
            }
        }
        
        # Pattern-specific recommendations
        for pattern, analysis in self.tp_analysis_data.get("pattern_analysis", {}).items():
            optimal_tp = analysis.get("optimal_tp_multiple", 1.5)
            best_win_rate = max(analysis.get("win_rate_by_tp", {}).values()) if analysis.get("win_rate_by_tp") else 0
            
            recommendations["by_pattern"][pattern] = {
                "optimal_ratio": optimal_tp,
                "expected_win_rate": best_win_rate,
                "recommendation": f"Use {optimal_tp}:1 ratio for {pattern} patterns"
            }
        
        # Symbol-specific recommendations
        for symbol, analysis in self.tp_analysis_data.get("symbol_analysis", {}).items():
            avg_vol = analysis.get("avg_volatility", 0)
            best_sessions = analysis.get("best_sessions", {})
            
            best_session = "london"  # default
            best_session_data = {"optimal_tp": 1.5, "win_rate": 0}
            for session, data in best_sessions.items():
                if data.get("win_rate", 0) > best_session_data["win_rate"]:
                    best_session = session
                    best_session_data = data
            
            recommendations["by_symbol"][symbol] = {
                "best_session": best_session,
                "session_tp_ratio": best_session_data.get("optimal_tp", 1.5),
                "avg_volatility": avg_vol,
                "recommendation": f"Trade {symbol} during {best_session} session with {best_session_data.get('optimal_tp', 1.5)}:1 ratio"
            }
        
        return recommendations
    
    def get_optimal_tp(self, setup_data: Dict) -> Dict:
        """
        Get optimal TP for a specific setup based on historical analysis.
        """
        pattern = setup_data.get("pattern", "unknown")
        symbol = setup_data.get("symbol", "unknown")
        entry_price = setup_data.get("entry_price", setup_data.get("close", 0))
        stop_loss = setup_data.get("stop_loss", 0)
        direction = setup_data.get("direction", "buy")
        
        if entry_price == 0 or stop_loss == 0:
            return {"error": "Missing entry price or stop loss"}
        
        # Calculate base risk
        risk = abs(entry_price - stop_loss)
        
        # Get optimal ratio from multiple sources
        ratios = []
        
        # Pattern-based ratio
        pattern_analysis = self.tp_analysis_data.get("pattern_analysis", {}).get(pattern, {})
        if pattern_analysis:
            pattern_ratio = pattern_analysis.get("optimal_tp_multiple", 1.5)
            ratios.append(("pattern", pattern_ratio, 0.4))  # 40% weight
        
        # Symbol-based ratio
        symbol_analysis = self.tp_analysis_data.get("symbol_analysis", {}).get(symbol, {})
        if symbol_analysis:
            # Get session-specific ratio if available
            current_hour = datetime.now().hour
            if 0 <= current_hour < 8:
                session = "asian"
            elif 8 <= current_hour < 16:
                session = "london"
            else:
                session = "ny"
            
            session_data = symbol_analysis.get("best_sessions", {}).get(session, {})
            if session_data:
                symbol_ratio = session_data.get("optimal_tp", 1.5)
                ratios.append(("symbol_session", symbol_ratio, 0.3))  # 30% weight
        
        # Market condition adjustments
        volatility = setup_data.get("volatility", setup_data.get("atr", 0.001))
        if volatility > 0.002:  # High volatility
            ratios.append(("volatility_high", 2.5, 0.2))  # 20% weight
        elif volatility < 0.0005:  # Low volatility
            ratios.append(("volatility_low", 1.2, 0.2))
        else:
            ratios.append(("volatility_normal", 2.0, 0.2))
        
        # Default ratio
        ratios.append(("default", 2.0, 0.1))  # 10% weight
        
        # Calculate weighted average
        total_weight = sum(weight for _, _, weight in ratios)
        weighted_ratio = sum(ratio * weight for _, ratio, weight in ratios) / total_weight
        
        # Calculate TP levels
        if direction.lower() == "buy":
            tp_price = entry_price + (risk * weighted_ratio)
        else:
            tp_price = entry_price - (risk * weighted_ratio)
        
        return {
            "optimal_tp_price": tp_price,
            "tp_ratio": weighted_ratio,
            "risk_amount": risk,
            "potential_reward": risk * weighted_ratio,
            "sources_used": [source for source, _, _ in ratios],
            "confidence": min(len(ratios) * 0.2, 1.0)  # Confidence based on data sources
        }
    
    def update_tp_performance(self, trade_result: Dict) -> bool:
        """Update TP analysis with new trade result"""
        try:
            pattern = trade_result.get("pattern", "unknown")
            symbol = trade_result.get("symbol", "unknown")
            outcome = trade_result.get("outcome", "unknown")
            
            # This would be called when a trade closes to update the analysis
            # Implementation would update the stored analysis data with new results
            
            return True
        except Exception as e:
            print(f"Error updating TP performance: {e}")
            return False
    
    def get_analysis_summary(self) -> Dict:
        """Get summary of TP analysis"""
        summary = {
            "patterns_analyzed": len(self.tp_analysis_data.get("pattern_analysis", {})),
            "symbols_analyzed": len(self.tp_analysis_data.get("symbol_analysis", {})),
            "last_updated": self.tp_analysis_data.get("last_updated"),
            "top_performing_patterns": [],
            "top_performing_symbols": []
        }
        
        # Find top performing patterns
        pattern_scores = []
        for pattern, data in self.tp_analysis_data.get("pattern_analysis", {}).items():
            ratios = data.get("risk_reward_ratios", {})
            if ratios:
                best_score = max(r.get("score", 0) for r in ratios.values())
                pattern_scores.append((pattern, best_score))
        
        pattern_scores.sort(key=lambda x: x[1], reverse=True)
        summary["top_performing_patterns"] = pattern_scores[:5]
        
        return summary

# Global optimal TP analyzer instance
optimal_tp_analyzer = OptimalTPAnalyzer()