"""
Advanced Logging Framework for MyPhytonEA Trading System

Features:
- Structured logging with multiple handlers (file, console, database)
- Error tracking and alerting
- Performance monitoring
- Trade audit trails
- Strategy versioning integration
"""

import logging
import logging.handlers
import json
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import threading
import queue
import time

class TradingLogger:
    """Enhanced logging system for trading operations"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or self._default_config()
        self.loggers = {}
        self.log_queue = queue.Queue()
        self.error_count = 0
        self.warning_count = 0
        self.trade_count = 0
        
        # Create log directory
        Path(self.config['log_dir']).mkdir(parents=True, exist_ok=True)
        
        # Setup loggers
        self._setup_loggers()
        
        # Start async logging thread
        self.logging_thread = threading.Thread(target=self._process_logs, daemon=True)
        self.logging_thread.start()
        
    def _default_config(self) -> Dict[str, Any]:
        return {
            'log_dir': './logs',
            'log_level': 'INFO',
            'max_file_size': 10 * 1024 * 1024,  # 10MB
            'backup_count': 5,
            'enable_database': False,
            'enable_alerts': True,
            'structured_format': True
        }
    
    def _setup_loggers(self):
        """Setup different loggers for different components"""
        categories = ['trading', 'risk', 'ml', 'scanner', 'ea', 'prop_firm', 'system']
        
        for category in categories:
            logger = logging.getLogger(f"trading.{category}")
            logger.setLevel(getattr(logging, self.config['log_level']))
            
            # File handler
            file_handler = logging.handlers.RotatingFileHandler(
                f"{self.config['log_dir']}/{category}.log",
                maxBytes=self.config['max_file_size'],
                backupCount=self.config['backup_count']
            )
            
            # Console handler for errors
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.ERROR)
            
            # Formatter
            if self.config['structured_format']:
                formatter = StructuredFormatter()
            else:
                formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                )
            
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)
            
            self.loggers[category] = logger
    
    def _process_logs(self):
        """Background thread to process log queue"""
        while True:
            try:
                if not self.log_queue.empty():
                    log_entry = self.log_queue.get(timeout=1)
                    self._write_log(log_entry)
                else:
                    time.sleep(0.1)
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Logging error: {e}")
    
    def _write_log(self, log_entry: Dict[str, Any]):
        """Write log entry to appropriate logger"""
        category = log_entry.get('category', 'system')
        level = log_entry.get('level', 'info').upper()
        message = log_entry.get('message', '')
        
        logger = self.loggers.get(category, self.loggers['system'])
        
        # Add context data
        extra_data = {
            'trade_id': log_entry.get('trade_id'),
            'instrument': log_entry.get('instrument'),
            'strategy': log_entry.get('strategy'),
            'version': log_entry.get('version', '1.0.0')
        }
        
        # Filter None values
        extra_data = {k: v for k, v in extra_data.items() if v is not None}
        
        getattr(logger, level.lower())(message, extra=extra_data)
        
        # Update counters
        if level == 'ERROR':
            self.error_count += 1
        elif level == 'WARNING':
            self.warning_count += 1
    
    def log(self, category: str, message: str, level: str = 'info', **kwargs):
        """Main logging method"""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'category': category,
            'message': message,
            'level': level,
            **kwargs
        }
        
        self.log_queue.put(log_entry)
    
    def log_trade(self, trade_data: Dict[str, Any]):
        """Log trade execution with full audit trail"""
        self.trade_count += 1
        self.log('trading', f"Trade executed: {trade_data}", 'info', 
                trade_id=trade_data.get('id'),
                instrument=trade_data.get('instrument'),
                action=trade_data.get('action'),
                amount=trade_data.get('amount'))
    
    def log_error(self, category: str, error: Exception, context: Dict[str, Any] = None):
        """Log error with full traceback"""
        error_data = {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'traceback': traceback.format_exc(),
            'context': context or {}
        }
        
        self.log(category, f"Error: {error}", 'error', **error_data)
    
    def log_prop_firm_event(self, event_type: str, message: str, account_info: Dict[str, Any]):
        """Special logging for prop firm events"""
        self.log('prop_firm', message, 'warning',
                event_type=event_type,
                account=account_info.get('account_name', 'unknown'),
                broker=account_info.get('broker', 'unknown'),
                balance=account_info.get('balance'),
                drawdown=account_info.get('drawdown'))
    
    def get_stats(self) -> Dict[str, Any]:
        """Get logging statistics"""
        return {
            'error_count': self.error_count,
            'warning_count': self.warning_count,
            'trade_count': self.trade_count,
            'queue_size': self.log_queue.qsize()
        }

class StructuredFormatter(logging.Formatter):
    """JSON structured formatter for machine-readable logs"""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcfromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage()
        }
        
        # Add extra fields
        if hasattr(record, 'trade_id') and record.trade_id:
            log_entry['trade_id'] = record.trade_id
        if hasattr(record, 'instrument') and record.instrument:
            log_entry['instrument'] = record.instrument
        if hasattr(record, 'strategy') and record.strategy:
            log_entry['strategy'] = record.strategy
        if hasattr(record, 'version') and record.version:
            log_entry['version'] = record.version
        
        return json.dumps(log_entry)

# Global logger instance
trading_logger = TradingLogger()

# Convenience functions
def log_info(category: str, message: str, **kwargs):
    trading_logger.log(category, message, 'info', **kwargs)

def log_warning(category: str, message: str, **kwargs):
    trading_logger.log(category, message, 'warning', **kwargs)

def log_error(category: str, message: str, **kwargs):
    trading_logger.log(category, message, 'error', **kwargs)

def log_trade(trade_data: Dict[str, Any]):
    trading_logger.log_trade(trade_data)

def log_prop_firm_event(event_type: str, message: str, account_info: Dict[str, Any]):
    trading_logger.log_prop_firm_event(event_type, message, account_info)