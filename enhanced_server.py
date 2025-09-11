"""
Enhanced Server with Integrated Advanced Trading Systems

This server integrates:
- Prop firm detection and rule enforcement
- Advanced logging and error handling
- Multi-channel notification system
- Resource monitoring
- Advanced risk controls
- Performance analytics
"""

from flask import Flask, request, jsonify, send_file
from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import threading
import time
from datetime import datetime, timedelta
import os
import json
from typing import Dict, Any, List, Optional

# Import our advanced systems
from advanced_logging import trading_logger, log_info, log_error, log_warning, log_trade
from prop_firm_system import prop_firm_detector
from notification_system import notification_manager, send_notification, send_prop_firm_notification
from resource_monitor import resource_monitor

# Import existing modules
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.cluster import KMeans
from joblib import dump, load

# --- Enhanced FastAPI Application ---
app = FastAPI(title="MyPhytonEA Trading System", version="2.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Data Models (Enhanced) ---
trade_data = []
setup_data = []
ml_data = {}
log_entries = []
notifications = []
risk_metrics = {}

# Enhanced risk tracking
daily_pnl_tracking = {}
weekly_pnl_tracking = {}
monthly_pnl_tracking = {}
open_positions = []

class EnhancedRiskManager:
    """Enhanced risk management with prop firm integration"""
    
    def __init__(self):
        self.daily_max_loss = 500.0
        self.weekly_max_loss = 2000.0
        self.monthly_max_loss = 5000.0
        self.max_drawdown = 0.1
        self.max_open_positions = 5
        self.emergency_stop = False
        
    def check_risk_limits(self, setup: Dict[str, Any], account_info: Dict[str, Any]) -> tuple:
        """Enhanced risk checking with prop firm integration"""
        
        # First check if we're in emergency stop mode
        if self.emergency_stop:
            return False, "Emergency stop activated - all trading suspended"
        
        # Check prop firm rules if applicable
        is_prop_firm, prop_firm_rules = prop_firm_detector.detect_prop_firm(account_info)
        if is_prop_firm:
            # Log prop firm detection
            log_info('prop_firm', f"Prop firm detected: {prop_firm_rules.firm_name}")
            send_prop_firm_notification(
                'DETECTION', 
                f"Prop firm mode activated: {prop_firm_rules.firm_name}",
                prop_firm_rules.firm_name
            )
            
            # Enforce prop firm rules
            allowed, reason = prop_firm_detector.enforce_prop_firm_rules(setup, account_info)
            if not allowed:
                return False, f"Prop firm rule violation: {reason}"
        
        # Standard risk checks
        today = datetime.now().date()
        daily_loss = daily_pnl_tracking.get(today, 0)
        
        # Check daily loss limit
        if daily_loss >= self.daily_max_loss:
            reason = f"Daily loss limit exceeded: ${daily_loss:.2f}"
            log_warning('risk', reason)
            return False, reason
        
        # Check max open positions
        if len(open_positions) >= self.max_open_positions:
            return False, f"Maximum open positions reached: {len(open_positions)}"
        
        # Check position size
        risk_amount = setup.get('risk_amount', 0)
        account_balance = account_info.get('balance', 0)
        if account_balance > 0:
            risk_percentage = risk_amount / account_balance
            if risk_percentage > 0.02:  # 2% max risk per trade
                return False, f"Risk per trade too high: {risk_percentage:.3f}"
        
        return True, "Risk check passed"
    
    def record_trade_result(self, trade_result: Dict[str, Any]):
        """Record trade result for risk tracking"""
        pnl = trade_result.get('pnl', 0)
        trade_date = datetime.fromisoformat(trade_result.get('close_time', datetime.now().isoformat()))
        
        # Update daily tracking
        date_key = trade_date.date()
        if pnl < 0:  # Only track losses
            daily_pnl_tracking[date_key] = daily_pnl_tracking.get(date_key, 0) + abs(pnl)
        
        # Update prop firm tracking if applicable
        if prop_firm_detector.is_prop_firm_mode:
            prop_firm_detector.update_pnl(pnl, trade_date)
        
        # Check if emergency stop needed
        if daily_pnl_tracking.get(date_key, 0) >= self.daily_max_loss * 0.8:  # 80% of limit
            send_notification('risk', 
                            f"Approaching daily loss limit: ${daily_pnl_tracking.get(date_key, 0):.2f}",
                            priority='high')
    
    def activate_emergency_stop(self, reason: str):
        """Activate emergency stop"""
        self.emergency_stop = True
        log_error('risk', f"Emergency stop activated: {reason}")
        send_notification('risk', f"EMERGENCY STOP: {reason}", priority='high')
        
        # Close all open positions (this would interface with the EA)
        return {"action": "emergency_stop", "reason": reason, "timestamp": datetime.utcnow().isoformat()}

# Initialize enhanced components
enhanced_risk_manager = EnhancedRiskManager()

# --- API Endpoints ---

@app.get("/")
async def root():
    return {"message": "MyPhytonEA Trading System v2.0", "status": "online"}

@app.get("/health")
async def health_check():
    """Comprehensive health check"""
    system_health = resource_monitor.get_trading_system_health()
    prop_firm_status = prop_firm_detector.get_prop_firm_status()
    
    return {
        "status": "healthy" if system_health['status'] == "healthy" else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "system_health": system_health,
        "prop_firm_status": prop_firm_status,
        "emergency_stop": enhanced_risk_manager.emergency_stop,
        "services": {
            "logging": trading_logger.get_stats(),
            "notifications": notification_manager.get_notification_stats(),
            "resource_monitor": resource_monitor.monitoring
        }
    }

@app.get("/prop_firm/status")
async def get_prop_firm_status():
    """Get current prop firm status"""
    return prop_firm_detector.get_prop_firm_status()

@app.post("/prop_firm/detect")
async def detect_prop_firm(account_info: Dict[str, Any]):
    """Manually trigger prop firm detection"""
    is_prop_firm, rules = prop_firm_detector.detect_prop_firm(account_info)
    
    return {
        "is_prop_firm": is_prop_firm,
        "rules": rules.to_dict() if rules else None,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/resource_monitor/stats")
async def get_resource_stats():
    """Get current resource statistics"""
    return resource_monitor.get_current_stats()

@app.get("/resource_monitor/health")
async def get_system_health():
    """Get system health status"""
    return resource_monitor.get_trading_system_health()

@app.get("/resource_monitor/history")
async def get_resource_history(hours: int = Query(1, ge=1, le=24)):
    """Get historical resource data"""
    return resource_monitor.get_historical_data(hours)

@app.post("/risk/check")
async def check_risk(setup: Dict[str, Any], account_info: Dict[str, Any]):
    """Check if trade setup passes risk management"""
    allowed, reason = enhanced_risk_manager.check_risk_limits(setup, account_info)
    
    return {
        "allowed": allowed,
        "reason": reason,
        "risk_metrics": {
            "daily_loss": daily_pnl_tracking.get(datetime.now().date(), 0),
            "open_positions": len(open_positions),
            "emergency_stop": enhanced_risk_manager.emergency_stop
        }
    }

@app.post("/risk/emergency_stop")
async def emergency_stop(reason: str = "Manual activation"):
    """Activate emergency stop"""
    result = enhanced_risk_manager.activate_emergency_stop(reason)
    return result

@app.post("/risk/record_trade")
async def record_trade_result(trade_result: Dict[str, Any]):
    """Record trade result for risk tracking"""
    enhanced_risk_manager.record_trade_result(trade_result)
    log_trade(trade_result)
    
    return {"status": "recorded", "timestamp": datetime.utcnow().isoformat()}

@app.post("/notifications/send")
async def send_manual_notification(
    notification_type: str,
    message: str,
    title: str = None,
    priority: str = "normal"
):
    """Send manual notification"""
    notification_manager.send_notification(notification_type, message, title, priority)
    return {"status": "sent", "timestamp": datetime.utcnow().isoformat()}

@app.get("/notifications/history")
async def get_notification_history(limit: int = Query(100, ge=1, le=1000)):
    """Get notification history"""
    return notification_manager.get_notification_history(limit)

@app.get("/notifications/stats")
async def get_notification_stats():
    """Get notification statistics"""
    return notification_manager.get_notification_stats()

@app.post("/scanner")
async def scanner_ingest(setup_list: List[Dict[str, Any]], account_info: Dict[str, Any] = None):
    """Enhanced scanner endpoint with prop firm integration"""
    processed_setups = []
    
    for setup in setup_list:
        try:
            # Enhanced risk checking
            if account_info:
                allowed, reason = enhanced_risk_manager.check_risk_limits(setup, account_info)
                if not allowed:
                    log_warning('scanner', f"Setup rejected by risk manager: {reason}")
                    continue
            
            # Existing ML validation
            if MLDecisionEngine.validate_setup(setup):
                setup_data.append(setup)
                processed_setups.append(setup)
                log_info('scanner', f"Setup accepted: {setup.get('instrument', 'unknown')}")
            else:
                log_warning('scanner', f"Setup rejected by ML engine: {setup.get('instrument', 'unknown')}")
                
        except Exception as e:
            log_error('scanner', f"Error processing setup: {e}")
    
    return {
        "status": "ok",
        "processed": len(processed_setups),
        "total": len(setup_list),
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/logs")
async def get_logs(category: str = None, level: str = None, limit: int = Query(200, ge=1, le=1000)):
    """Get system logs with filtering"""
    # This would integrate with the advanced logging system
    return {"logs": log_entries[-limit:]}

@app.get("/stats")
async def get_system_stats():
    """Get comprehensive system statistics"""
    return {
        "trades": len(trade_data),
        "setups": len(setup_data),
        "open_positions": len(open_positions),
        "prop_firm_mode": prop_firm_detector.is_prop_firm_mode,
        "emergency_stop": enhanced_risk_manager.emergency_stop,
        "daily_pnl": daily_pnl_tracking.get(datetime.now().date(), 0),
        "system_health": resource_monitor.get_trading_system_health()['status'],
        "timestamp": datetime.utcnow().isoformat()
    }

# --- Existing ML Components (Enhanced) ---
class MLDecisionEngine:
    confidence_threshold = 0.75
    allowed_sessions = {'London', 'New York'}
    allowed_patterns = {'Breakout', 'Order Block', 'Reversal'}
    regime = 'trend'
    stats = {'accepted': 0, 'rejected': 0}
    clf_path = 'ml_trade_filter.joblib'
    kmeans_path = 'ml_regime_kmeans.joblib'
    clf = None
    kmeans = None

    @staticmethod
    def ensure_models():
        """Ensure ML models are loaded"""
        try:
            if not os.path.exists(MLDecisionEngine.clf_path):
                X = np.random.rand(100, 6)
                y = np.random.randint(0, 2, 100)
                clf = RandomForestClassifier(n_estimators=10)
                clf.fit(X, y)
                dump(clf, MLDecisionEngine.clf_path)
            
            if not os.path.exists(MLDecisionEngine.kmeans_path):
                X = np.random.rand(100, 3)
                kmeans = KMeans(n_clusters=2)
                kmeans.fit(X)
                dump(kmeans, MLDecisionEngine.kmeans_path)
            
            MLDecisionEngine.clf = load(MLDecisionEngine.clf_path)
            MLDecisionEngine.kmeans = load(MLDecisionEngine.kmeans_path)
            
        except Exception as e:
            log_error('ml', f"Error loading ML models: {e}")

    @staticmethod
    def validate_setup(setup):
        """Enhanced setup validation with logging"""
        try:
            MLDecisionEngine.ensure_models()
            
            # Basic validation logic (simplified for demo)
            confidence = setup.get('confidence', 0)
            if confidence < MLDecisionEngine.confidence_threshold:
                MLDecisionEngine.stats['rejected'] += 1
                log_info('ml', f"Setup rejected - low confidence: {confidence}")
                return False
                
            MLDecisionEngine.stats['accepted'] += 1
            log_info('ml', f"Setup accepted - confidence: {confidence}")
            return True
            
        except Exception as e:
            log_error('ml', f"Error validating setup: {e}")
            return False

# --- Background Tasks ---
def background_monitor():
    """Background monitoring tasks"""
    while True:
        try:
            # Clean up old data
            cutoff = datetime.now() - timedelta(days=7)
            global log_entries, notifications
            log_entries = [entry for entry in log_entries if 
                          datetime.fromisoformat(entry.get('timestamp', datetime.now().isoformat())) > cutoff]
            
            # System health checks
            health = resource_monitor.get_trading_system_health()
            if health['status'] == 'critical':
                send_notification('system', 
                                f"System health critical: {', '.join(health['issues'])}", 
                                priority='high')
            
            time.sleep(60)  # Check every minute
            
        except Exception as e:
            log_error('system', f"Background monitor error: {e}")
            time.sleep(60)

# Start background monitoring
background_thread = threading.Thread(target=background_monitor, daemon=True)
background_thread.start()

# --- Server Startup ---
if __name__ == "__main__":
    log_info('system', "Starting MyPhytonEA Trading System v2.0")
    print("🚀 MyPhytonEA Trading System v2.0 Starting...")
    print("📊 Resource monitoring: ACTIVE")
    print("🔔 Notification system: ACTIVE") 
    print("🏢 Prop firm detection: ACTIVE")
    print("📝 Advanced logging: ACTIVE")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)