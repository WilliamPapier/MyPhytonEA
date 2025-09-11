"""
Advanced Notification System for MyPhytonEA Trading System

Supports multiple notification channels:
- Telegram
- Email
- Discord
- Console/Log
- Dashboard alerts

Configurable per event type with filtering and rate limiting.
"""

import asyncio
import aiohttp
import smtplib
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from dataclasses import dataclass
from advanced_logging import log_info, log_error, log_warning
import queue
import threading
import time

@dataclass
class NotificationConfig:
    """Configuration for notification channels"""
    telegram_enabled: bool = False
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    
    email_enabled: bool = False
    email_smtp_server: str = "smtp.gmail.com"
    email_smtp_port: int = 587
    email_username: str = ""
    email_password: str = ""
    email_to: List[str] = None
    
    discord_enabled: bool = False
    discord_webhook_url: str = ""
    
    console_enabled: bool = True
    dashboard_enabled: bool = True
    
    # Rate limiting
    rate_limit_seconds: int = 30
    max_notifications_per_minute: int = 10

class NotificationManager:
    """Manages all notification channels and routing"""
    
    def __init__(self, config: NotificationConfig = None):
        self.config = config or NotificationConfig()
        self.notification_queue = queue.Queue()
        self.sent_notifications = {}  # For rate limiting
        self.notification_history = []
        
        # Start notification processing thread
        self.processing_thread = threading.Thread(target=self._process_notifications, daemon=True)
        self.processing_thread.start()
    
    def _process_notifications(self):
        """Background thread to process notification queue"""
        while True:
            try:
                if not self.notification_queue.empty():
                    notification = self.notification_queue.get(timeout=1)
                    self._send_notification(notification)
                else:
                    time.sleep(0.1)
            except queue.Empty:
                continue
            except Exception as e:
                log_error('notifications', f"Error processing notification: {e}")
    
    def _should_send(self, notification_type: str, message: str) -> bool:
        """Check if notification should be sent based on rate limiting"""
        now = datetime.now()
        
        # Check rate limiting
        key = f"{notification_type}:{hash(message[:50])}"  # Use first 50 chars for deduplication
        
        if key in self.sent_notifications:
            last_sent = self.sent_notifications[key]
            if (now - last_sent).total_seconds() < self.config.rate_limit_seconds:
                return False
        
        # Check max notifications per minute
        recent_notifications = [
            n for n in self.notification_history 
            if (now - n['timestamp']).total_seconds() < 60
        ]
        
        if len(recent_notifications) >= self.config.max_notifications_per_minute:
            return False
        
        return True
    
    def _send_notification(self, notification: Dict[str, Any]):
        """Send notification through all enabled channels"""
        notification_type = notification.get('type', 'info')
        message = notification.get('message', '')
        title = notification.get('title', 'Trading Alert')
        priority = notification.get('priority', 'normal')
        
        # Check rate limiting
        if not self._should_send(notification_type, message):
            return
        
        # Record notification
        now = datetime.now()
        key = f"{notification_type}:{hash(message[:50])}"
        self.sent_notifications[key] = now
        
        notification_record = {
            'timestamp': now,
            'type': notification_type,
            'message': message,
            'title': title,
            'priority': priority
        }
        self.notification_history.append(notification_record)
        
        # Keep only last 1000 notifications
        if len(self.notification_history) > 1000:
            self.notification_history = self.notification_history[-1000:]
        
        # Send through enabled channels
        if self.config.console_enabled:
            self._send_console(notification)
        
        if self.config.telegram_enabled:
            self._send_telegram(notification)
        
        if self.config.email_enabled:
            self._send_email(notification)
        
        if self.config.discord_enabled:
            self._send_discord(notification)
    
    def _send_console(self, notification: Dict[str, Any]):
        """Send notification to console/log"""
        message = notification.get('message', '')
        notification_type = notification.get('type', 'info')
        
        log_info('notifications', f"[{notification_type.upper()}] {message}")
    
    def _send_telegram(self, notification: Dict[str, Any]):
        """Send notification via Telegram"""
        if not self.config.telegram_bot_token or not self.config.telegram_chat_id:
            return
        
        try:
            message = notification.get('message', '')
            title = notification.get('title', 'Trading Alert')
            priority = notification.get('priority', 'normal')
            
            # Format message
            emoji = self._get_emoji(notification.get('type', 'info'), priority)
            telegram_message = f"{emoji} *{title}*\n\n{message}\n\n_{datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}_"
            
            # Send via requests (synchronous)
            import requests
            url = f"https://api.telegram.org/bot{self.config.telegram_bot_token}/sendMessage"
            data = {
                'chat_id': self.config.telegram_chat_id,
                'text': telegram_message,
                'parse_mode': 'Markdown'
            }
            
            response = requests.post(url, data=data, timeout=10)
            if response.status_code != 200:
                log_error('notifications', f"Telegram send failed: {response.text}")
            else:
                log_info('notifications', "Telegram notification sent successfully")
                
        except Exception as e:
            log_error('notifications', f"Telegram error: {e}")
    
    def _send_email(self, notification: Dict[str, Any]):
        """Send notification via email"""
        if not self.config.email_username or not self.config.email_to:
            return
        
        try:
            msg = MimeMultipart()
            msg['From'] = self.config.email_username
            msg['To'] = ', '.join(self.config.email_to)
            msg['Subject'] = notification.get('title', 'Trading Alert')
            
            # Create HTML email body
            body = self._format_email_body(notification)
            msg.attach(MimeText(body, 'html'))
            
            # Send email
            server = smtplib.SMTP(self.config.email_smtp_server, self.config.email_smtp_port)
            server.starttls()
            server.login(self.config.email_username, self.config.email_password)
            
            for recipient in self.config.email_to:
                server.sendmail(self.config.email_username, recipient, msg.as_string())
            
            server.quit()
            log_info('notifications', "Email notification sent successfully")
            
        except Exception as e:
            log_error('notifications', f"Email error: {e}")
    
    def _send_discord(self, notification: Dict[str, Any]):
        """Send notification via Discord webhook"""
        if not self.config.discord_webhook_url:
            return
        
        try:
            import requests
            
            # Format Discord message
            color = self._get_discord_color(notification.get('type', 'info'))
            embed = {
                "title": notification.get('title', 'Trading Alert'),
                "description": notification.get('message', ''),
                "color": color,
                "timestamp": datetime.utcnow().isoformat(),
                "footer": {"text": "MyPhytonEA Trading System"}
            }
            
            data = {"embeds": [embed]}
            
            response = requests.post(self.config.discord_webhook_url, json=data, timeout=10)
            if response.status_code not in [200, 204]:
                log_error('notifications', f"Discord send failed: {response.text}")
            else:
                log_info('notifications', "Discord notification sent successfully")
                
        except Exception as e:
            log_error('notifications', f"Discord error: {e}")
    
    def _get_emoji(self, notification_type: str, priority: str) -> str:
        """Get appropriate emoji for notification"""
        emoji_map = {
            'trade': '💰',
            'error': '❌',
            'warning': '⚠️',
            'info': 'ℹ️',
            'prop_firm': '🏢',
            'risk': '🚨',
            'system': '⚙️'
        }
        
        if priority == 'high':
            return '🚨'
        
        return emoji_map.get(notification_type, 'ℹ️')
    
    def _get_discord_color(self, notification_type: str) -> int:
        """Get Discord embed color for notification type"""
        color_map = {
            'trade': 0x00ff00,      # Green
            'error': 0xff0000,      # Red
            'warning': 0xffa500,    # Orange
            'info': 0x0099ff,       # Blue
            'prop_firm': 0x800080,  # Purple
            'risk': 0xff4444,       # Dark Red
            'system': 0x808080      # Gray
        }
        
        return color_map.get(notification_type, 0x0099ff)
    
    def _format_email_body(self, notification: Dict[str, Any]) -> str:
        """Format HTML email body"""
        message = notification.get('message', '')
        notification_type = notification.get('type', 'info')
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
        
        return f"""
        <html>
        <body>
            <h2 style="color: #333;">Trading System Alert</h2>
            <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px;">
                <p><strong>Type:</strong> {notification_type.upper()}</p>
                <p><strong>Time:</strong> {timestamp}</p>
                <p><strong>Message:</strong></p>
                <div style="background-color: white; padding: 10px; border-left: 4px solid #007bff;">
                    {message}
                </div>
            </div>
            <br>
            <p style="color: #666; font-size: 12px;">
                This message was sent by MyPhytonEA Trading System
            </p>
        </body>
        </html>
        """
    
    def send_notification(self, notification_type: str, message: str, 
                         title: str = None, priority: str = 'normal', **kwargs):
        """Queue a notification for sending"""
        notification = {
            'type': notification_type,
            'message': message,
            'title': title or f"Trading Alert - {notification_type.title()}",
            'priority': priority,
            'timestamp': datetime.now(),
            **kwargs
        }
        
        self.notification_queue.put(notification)
    
    def send_trade_notification(self, trade_data: Dict[str, Any]):
        """Send trade-specific notification"""
        action = trade_data.get('action', 'unknown')
        instrument = trade_data.get('instrument', 'unknown')
        amount = trade_data.get('amount', 0)
        price = trade_data.get('price', 0)
        
        message = f"Trade {action}: {instrument}\nAmount: {amount}\nPrice: {price}"
        
        self.send_notification('trade', message, f"Trade {action.title()}")
    
    def send_prop_firm_notification(self, event_type: str, message: str, firm_name: str):
        """Send prop firm-specific notification"""
        title = f"Prop Firm Alert - {firm_name}"
        self.send_notification('prop_firm', message, title, priority='high')
    
    def send_risk_notification(self, message: str, risk_level: str = 'medium'):
        """Send risk-related notification"""
        priority = 'high' if risk_level == 'high' else 'normal'
        self.send_notification('risk', message, "Risk Alert", priority=priority)
    
    def send_system_notification(self, message: str):
        """Send system-related notification"""
        self.send_notification('system', message, "System Alert")
    
    def get_notification_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent notification history"""
        return self.notification_history[-limit:]
    
    def get_notification_stats(self) -> Dict[str, Any]:
        """Get notification statistics"""
        now = datetime.now()
        
        # Count notifications by type in last 24 hours
        recent_notifications = [
            n for n in self.notification_history 
            if (now - n['timestamp']).total_seconds() < 86400  # 24 hours
        ]
        
        type_counts = {}
        for notification in recent_notifications:
            ntype = notification['type']
            type_counts[ntype] = type_counts.get(ntype, 0) + 1
        
        return {
            'total_sent': len(self.notification_history),
            'sent_last_24h': len(recent_notifications),
            'queue_size': self.notification_queue.qsize(),
            'type_counts_24h': type_counts,
            'channels_enabled': {
                'telegram': self.config.telegram_enabled,
                'email': self.config.email_enabled,
                'discord': self.config.discord_enabled,
                'console': self.config.console_enabled
            }
        }

# Global notification manager instance  
notification_manager = NotificationManager()

# Convenience functions
def send_notification(notification_type: str, message: str, title: str = None, priority: str = 'normal'):
    notification_manager.send_notification(notification_type, message, title, priority)

def send_trade_notification(trade_data: Dict[str, Any]):
    notification_manager.send_trade_notification(trade_data)

def send_prop_firm_notification(event_type: str, message: str, firm_name: str):
    notification_manager.send_prop_firm_notification(event_type, message, firm_name)

def send_risk_notification(message: str, risk_level: str = 'medium'):
    notification_manager.send_risk_notification(message, risk_level)