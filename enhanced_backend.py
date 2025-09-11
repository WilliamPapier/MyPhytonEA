"""
Enhanced FastAPI backend for EA/Scanner system with real-time configuration,
scoring, and risk management capabilities.
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import asyncio
import json
import csv
import os
from config import config_manager
from scoring import setup_scorer

app = FastAPI(title="EA/Scanner Control System", version="1.0.0")

# Shared data storage
active_setups = []
active_trades = []
trade_history = []
notifications = []

class SetupData(BaseModel):
    symbol: str
    timeframe: str
    timestamp: Optional[str] = None
    open: float
    high: float
    low: float
    close: float
    volume: Optional[float] = 0
    # Pattern indicators
    liquidity_sweep_high: Optional[int] = 0
    liquidity_sweep_low: Optional[int] = 0
    order_block: Optional[int] = 0
    pin_bar: Optional[int] = 0
    # Technical indicators
    ma_5_1m: Optional[float] = 0
    ma_20_1m: Optional[float] = 0
    rsi_14: Optional[float] = 50
    volatility_1m: Optional[float] = 0

class TradeData(BaseModel):
    symbol: str
    direction: str  # "buy" or "sell"
    entry_price: float
    stop_loss: float
    take_profit: float
    position_size: float
    timestamp: Optional[str] = None
    setup_id: Optional[str] = None

class ConfigUpdate(BaseModel):
    key: str
    value: Any

class OutcomeData(BaseModel):
    setup_id: str
    outcome: str  # "win", "loss", "tp", "sl"
    profit_loss: Optional[float] = 0

# Configuration endpoints
@app.get("/config")
async def get_config():
    """Get all configuration settings"""
    return config_manager.get_all()

@app.get("/config/{key}")
async def get_config_value(key: str):
    """Get specific configuration value"""
    value = config_manager.get(key)
    if value is None:
        raise HTTPException(status_code=404, detail=f"Configuration key '{key}' not found")
    return {"key": key, "value": value}

@app.post("/config")
async def update_config(update: ConfigUpdate):
    """Update configuration value with real-time propagation"""
    success = config_manager.set(update.key, update.value)
    if success:
        # Notify all connected modules about the change
        await broadcast_config_change(update.key, update.value)
        return {"status": "success", "key": update.key, "value": update.value}
    else:
        raise HTTPException(status_code=400, detail="Failed to update configuration")

@app.post("/config/bulk")
async def update_multiple_config(updates: Dict[str, Any]):
    """Update multiple configuration values atomically"""
    success = config_manager.update_multiple(updates)
    if success:
        # Notify about all changes
        for key, value in updates.items():
            await broadcast_config_change(key, value)
        return {"status": "success", "updated": updates}
    else:
        raise HTTPException(status_code=400, detail="Failed to update configuration")

@app.get("/threshold")
async def get_probability_threshold():
    """Get current global probability threshold"""
    return {"probability_threshold": config_manager.get_probability_threshold()}

@app.post("/threshold")
async def set_probability_threshold(threshold: Dict[str, float]):
    """Set global probability threshold with real-time updates"""
    new_threshold = threshold.get("threshold")
    if new_threshold is None or not (0.0 <= new_threshold <= 1.0):
        raise HTTPException(status_code=400, detail="Threshold must be between 0.0 and 1.0")
    
    success = config_manager.set_probability_threshold(new_threshold)
    if success:
        await broadcast_config_change("probability_threshold", new_threshold)
        return {"status": "success", "probability_threshold": new_threshold}
    else:
        raise HTTPException(status_code=400, detail="Failed to update threshold")

# Setup scoring and filtering endpoints
@app.post("/scanner/submit")
async def submit_setup(setup: SetupData):
    """Submit a setup for scoring and potential trading"""
    try:
        # Convert to dict for scoring
        setup_dict = setup.dict()
        if setup_dict["timestamp"] is None:
            setup_dict["timestamp"] = datetime.now().isoformat()
        
        # Score the setup
        score_result = setup_scorer.score_setup(setup_dict)
        
        # Check against global threshold
        probability_threshold = config_manager.get_probability_threshold()
        
        if score_result["probability"] >= probability_threshold:
            # Add to active setups
            setup_entry = {
                **setup_dict,
                **score_result,
                "id": f"{setup.symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "status": "active"
            }
            active_setups.append(setup_entry)
            
            # Save to CSV for EA consumption
            await save_setup_to_csv(setup_entry)
            
            return {
                "status": "accepted",
                "setup_id": setup_entry["id"],
                "score": score_result,
                "threshold_met": True
            }
        else:
            return {
                "status": "filtered",
                "score": score_result,
                "threshold_met": False,
                "required_threshold": probability_threshold
            }
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing setup: {str(e)}")

@app.get("/setups")
async def get_active_setups():
    """Get all active setups with filtering options"""
    threshold = config_manager.get_probability_threshold()
    
    # Filter setups by current threshold
    filtered_setups = [
        setup for setup in active_setups 
        if setup.get("probability", 0) >= threshold
    ]
    
    return {
        "setups": filtered_setups,
        "count": len(filtered_setups),
        "threshold": threshold
    }

@app.get("/setups/{setup_id}")
async def get_setup(setup_id: str):
    """Get specific setup details"""
    setup = next((s for s in active_setups if s.get("id") == setup_id), None)
    if not setup:
        raise HTTPException(status_code=404, detail="Setup not found")
    return setup

# Trade management endpoints
@app.post("/trades/open")
async def open_trade(trade: TradeData):
    """Open a new trade with risk management"""
    try:
        # Check position sizing and risk limits
        risk_settings = config_manager.get_risk_settings()
        
        # Check maximum simultaneous trades
        current_trades = len([t for t in active_trades if t.get("status") == "open"])
        if current_trades >= risk_settings["max_simultaneous_trades"]:
            raise HTTPException(status_code=400, detail="Maximum simultaneous trades reached")
        
        # Calculate position size if not provided
        if trade.position_size <= 0:
            account_balance = config_manager.get("account_balance", 10000)
            stop_loss_pips = abs(trade.entry_price - trade.stop_loss) * 10000  # Assuming 4-digit quotes
            trade.position_size = config_manager.calculate_position_size(
                account_balance, stop_loss_pips
            )
        
        # Create trade record
        trade_record = {
            **trade.dict(),
            "id": f"trade_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": trade.timestamp or datetime.now().isoformat(),
            "status": "open",
            "profit_loss": 0.0,
            "trailing_stop": trade.stop_loss
        }
        
        active_trades.append(trade_record)
        
        # Save to CSV for EA
        await save_trade_to_csv(trade_record)
        
        return {
            "status": "success",
            "trade_id": trade_record["id"],
            "position_size": trade_record["position_size"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error opening trade: {str(e)}")

@app.get("/trades")
async def get_trades():
    """Get all trades with optional filtering"""
    return {
        "active_trades": [t for t in active_trades if t.get("status") == "open"],
        "closed_trades": trade_history[-50:],  # Last 50 closed trades
        "total_active": len([t for t in active_trades if t.get("status") == "open"])
    }

@app.post("/trades/{trade_id}/close")
async def close_trade(trade_id: str, outcome: OutcomeData):
    """Close a trade and record outcome"""
    try:
        # Find and close the trade
        trade = next((t for t in active_trades if t.get("id") == trade_id), None)
        if not trade:
            raise HTTPException(status_code=404, detail="Trade not found")
        
        # Update trade record
        trade["status"] = "closed"
        trade["close_time"] = datetime.now().isoformat()
        trade["profit_loss"] = outcome.profit_loss or 0.0
        trade["outcome"] = outcome.outcome
        
        # Move to history
        trade_history.append(trade.copy())
        active_trades.remove(trade)
        
        # Record outcome for scoring system
        if trade.get("setup_id"):
            setup = next((s for s in active_setups if s.get("id") == trade["setup_id"]), None)
            if setup:
                setup_scorer.record_outcome(setup, outcome.outcome)
        
        return {"status": "success", "trade_id": trade_id, "outcome": outcome.outcome}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error closing trade: {str(e)}")

# Risk management endpoints
@app.get("/risk/summary")
async def get_risk_summary():
    """Get current risk exposure and settings"""
    risk_settings = config_manager.get_risk_settings()
    account_balance = config_manager.get("account_balance", 10000)
    
    # Calculate current exposure
    total_risk = 0.0
    for trade in active_trades:
        if trade.get("status") == "open":
            trade_risk = abs(trade["entry_price"] - trade["stop_loss"]) * trade["position_size"]
            total_risk += trade_risk
    
    current_risk_percent = (total_risk / account_balance) * 100 if account_balance > 0 else 0
    
    return {
        "account_balance": account_balance,
        "total_risk_amount": total_risk,
        "current_risk_percent": current_risk_percent,
        "max_daily_risk_percent": risk_settings["max_daily_risk_percent"],
        "active_trades": len([t for t in active_trades if t.get("status") == "open"]),
        "max_simultaneous_trades": risk_settings["max_simultaneous_trades"],
        "risk_per_trade_percent": risk_settings["risk_per_trade_percent"],
        "risk_available": risk_settings["max_daily_risk_percent"] - current_risk_percent
    }

# Performance and analytics endpoints
@app.get("/performance/summary")
async def get_performance_summary():
    """Get comprehensive performance analytics"""
    scoring_summary = setup_scorer.get_performance_summary()
    
    # Calculate trading performance
    closed_trades = [t for t in trade_history if t.get("status") == "closed"]
    winning_trades = [t for t in closed_trades if t.get("profit_loss", 0) > 0]
    
    trading_summary = {
        "total_trades": len(closed_trades),
        "winning_trades": len(winning_trades),
        "win_rate": len(winning_trades) / len(closed_trades) if closed_trades else 0,
        "total_profit": sum(t.get("profit_loss", 0) for t in closed_trades),
        "average_profit": sum(t.get("profit_loss", 0) for t in closed_trades) / len(closed_trades) if closed_trades else 0
    }
    
    return {
        "scoring_performance": scoring_summary,
        "trading_performance": trading_summary,
        "current_threshold": config_manager.get_probability_threshold()
    }

@app.get("/performance/goals")
async def get_goal_tracking():
    """Get daily, weekly, and monthly goal progress"""
    account_balance = config_manager.get("account_balance", 10000)
    
    # Calculate periods
    now = datetime.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=now.weekday())
    month_start = today_start.replace(day=1)
    
    # Filter trades by period
    daily_trades = [t for t in trade_history 
                   if datetime.fromisoformat(t.get("close_time", "1970-01-01")) >= today_start]
    weekly_trades = [t for t in trade_history 
                    if datetime.fromisoformat(t.get("close_time", "1970-01-01")) >= week_start]
    monthly_trades = [t for t in trade_history 
                     if datetime.fromisoformat(t.get("close_time", "1970-01-01")) >= month_start]
    
    # Calculate goals (example: 2% daily, 10% weekly, 30% monthly)
    daily_goal = account_balance * 0.02
    weekly_goal = account_balance * 0.10
    monthly_goal = account_balance * 0.30
    
    # Calculate actual profits
    daily_profit = sum(t.get("profit_loss", 0) for t in daily_trades)
    weekly_profit = sum(t.get("profit_loss", 0) for t in weekly_trades)
    monthly_profit = sum(t.get("profit_loss", 0) for t in monthly_trades)
    
    return {
        "daily": {
            "goal": daily_goal,
            "actual": daily_profit,
            "progress_percent": (daily_profit / daily_goal * 100) if daily_goal > 0 else 0,
            "trades": len(daily_trades)
        },
        "weekly": {
            "goal": weekly_goal,
            "actual": weekly_profit,
            "progress_percent": (weekly_profit / weekly_goal * 100) if weekly_goal > 0 else 0,
            "trades": len(weekly_trades)
        },
        "monthly": {
            "goal": monthly_goal,
            "actual": monthly_profit,
            "progress_percent": (monthly_profit / monthly_goal * 100) if monthly_goal > 0 else 0,
            "trades": len(monthly_trades)
        }
    }

# Utility functions
async def broadcast_config_change(key: str, value: Any):
    """Broadcast configuration changes to all connected modules"""
    # This would notify scanner, EA, and other components about config changes
    # For now, we'll add to notifications
    notifications.append({
        "type": "config_change",
        "key": key,
        "value": value,
        "timestamp": datetime.now().isoformat()
    })

async def save_setup_to_csv(setup: Dict):
    """Save setup to CSV file for EA consumption"""
    csv_file = "active_setups.csv"
    fieldnames = ["id", "symbol", "timeframe", "probability", "recommendation", 
                 "entry_price", "timestamp", "pattern", "signal_strength"]
    
    file_exists = os.path.exists(csv_file)
    
    with open(csv_file, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        
        row = {field: setup.get(field, "") for field in fieldnames}
        row["entry_price"] = setup.get("close", 0)  # Use close as entry price
        writer.writerow(row)

async def save_trade_to_csv(trade: Dict):
    """Save trade to CSV file for EA consumption"""
    csv_file = "active_trades.csv"
    fieldnames = ["id", "symbol", "direction", "entry_price", "stop_loss", 
                 "take_profit", "position_size", "timestamp", "status"]
    
    file_exists = os.path.exists(csv_file)
    
    with open(csv_file, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        
        row = {field: trade.get(field, "") for field in fieldnames}
        writer.writerow(row)

# Health check and status endpoints
@app.get("/health")
async def health_check():
    """System health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_setups": len(active_setups),
        "active_trades": len([t for t in active_trades if t.get("status") == "open"]),
        "config_loaded": config_manager.get("last_updated") is not None
    }

@app.get("/notifications")
async def get_notifications():
    """Get recent notifications"""
    return {"notifications": notifications[-20:]}  # Last 20 notifications

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)