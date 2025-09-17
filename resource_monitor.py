"""
Resource Monitoring System for MyPhytonEA Trading System

Monitors:
- CPU usage
- RAM usage  
- Disk space
- Network connectivity
- Process health
- Trading system performance metrics
"""

import psutil
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List
from dataclasses import dataclass
from advanced_logging import log_warning, log_error, log_info
from notification_system import send_notification
import json

@dataclass
class ResourceThresholds:
    """Resource monitoring thresholds"""
    cpu_warning: float = 80.0      # CPU % warning threshold
    cpu_critical: float = 95.0     # CPU % critical threshold
    memory_warning: float = 80.0   # Memory % warning threshold  
    memory_critical: float = 95.0  # Memory % critical threshold
    disk_warning: float = 85.0     # Disk % warning threshold
    disk_critical: float = 95.0    # Disk % critical threshold
    
    # Process-specific thresholds
    process_memory_mb: float = 500.0   # Max memory per process (MB)
    process_cpu_percent: float = 50.0  # Max CPU per process (%)
    
    # Network thresholds
    network_timeout: float = 5.0      # Network timeout (seconds)
    max_network_failures: int = 3     # Max consecutive network failures

class ResourceMonitor:
    """Monitors system resources and trading system health"""
    
    def __init__(self, thresholds: ResourceThresholds = None):
        self.thresholds = thresholds or ResourceThresholds()
        self.monitoring = False
        self.monitoring_thread = None
        self.monitor_interval = 10  # seconds
        
        # Resource history
        self.cpu_history = []
        self.memory_history = []
        self.disk_history = []
        self.network_history = []
        
        # Alert tracking
        self.last_alerts = {}
        self.alert_cooldown = 300  # 5 minutes between similar alerts
        
        # Process tracking
        self.tracked_processes = []
        
        # Network monitoring
        self.network_failures = 0
        self.last_network_check = datetime.now()
        
    def start_monitoring(self):
        """Start resource monitoring in background thread"""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        log_info('system', "Resource monitoring started")
    
    def stop_monitoring(self):
        """Stop resource monitoring"""
        self.monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        log_info('system', "Resource monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                self._check_system_resources()
                self._check_process_health()
                self._check_network_connectivity()
                self._cleanup_history()
                time.sleep(self.monitor_interval)
            except Exception as e:
                log_error('system', f"Resource monitoring error: {e}")
                time.sleep(self.monitor_interval)
    
    def _check_system_resources(self):
        """Check CPU, memory, and disk usage"""
        now = datetime.now()
        
        # CPU monitoring
        cpu_percent = psutil.cpu_percent(interval=1)
        self.cpu_history.append({'timestamp': now, 'value': cpu_percent})
        
        if cpu_percent >= self.thresholds.cpu_critical:
            self._send_alert('cpu_critical', f"Critical CPU usage: {cpu_percent:.1f}%")
        elif cpu_percent >= self.thresholds.cpu_warning:
            self._send_alert('cpu_warning', f"High CPU usage: {cpu_percent:.1f}%")
        
        # Memory monitoring
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        self.memory_history.append({'timestamp': now, 'value': memory_percent})
        
        if memory_percent >= self.thresholds.memory_critical:
            self._send_alert('memory_critical', 
                           f"Critical memory usage: {memory_percent:.1f}% ({memory.used // 1024 // 1024}MB used)")
        elif memory_percent >= self.thresholds.memory_warning:
            self._send_alert('memory_warning', 
                           f"High memory usage: {memory_percent:.1f}% ({memory.used // 1024 // 1024}MB used)")
        
        # Disk monitoring
        disk = psutil.disk_usage('/')
        disk_percent = (disk.used / disk.total) * 100
        self.disk_history.append({'timestamp': now, 'value': disk_percent})
        
        if disk_percent >= self.thresholds.disk_critical:
            self._send_alert('disk_critical', 
                           f"Critical disk usage: {disk_percent:.1f}% ({disk.free // 1024 // 1024 // 1024}GB free)")
        elif disk_percent >= self.thresholds.disk_warning:
            self._send_alert('disk_warning', 
                           f"High disk usage: {disk_percent:.1f}% ({disk.free // 1024 // 1024 // 1024}GB free)")
    
    def _check_process_health(self):
        """Check health of tracked processes"""
        for process_name in self.tracked_processes:
            try:
                processes = [p for p in psutil.process_iter(['pid', 'name', 'memory_info', 'cpu_percent']) 
                           if process_name.lower() in p.info['name'].lower()]
                
                for proc in processes:
                    # Memory check
                    memory_mb = proc.info['memory_info'].rss / 1024 / 1024
                    if memory_mb > self.thresholds.process_memory_mb:
                        self._send_alert('process_memory', 
                                       f"Process {proc.info['name']} using {memory_mb:.1f}MB memory")
                    
                    # CPU check  
                    cpu_percent = proc.info['cpu_percent']
                    if cpu_percent > self.thresholds.process_cpu_percent:
                        self._send_alert('process_cpu', 
                                       f"Process {proc.info['name']} using {cpu_percent:.1f}% CPU")
                        
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    
    def _check_network_connectivity(self):
        """Check network connectivity to key endpoints"""
        import socket
        
        test_endpoints = [
            ('8.8.8.8', 53),        # Google DNS
            ('1.1.1.1', 53),        # Cloudflare DNS
        ]
        
        network_ok = False
        for host, port in test_endpoints:
            try:
                socket.create_connection((host, port), timeout=self.thresholds.network_timeout)
                network_ok = True
                break
            except:
                continue
        
        now = datetime.now()
        self.network_history.append({'timestamp': now, 'status': network_ok})
        
        if not network_ok:
            self.network_failures += 1
            if self.network_failures >= self.thresholds.max_network_failures:
                self._send_alert('network_down', 
                               f"Network connectivity lost ({self.network_failures} consecutive failures)")
        else:
            if self.network_failures > 0:
                log_info('system', "Network connectivity restored")
            self.network_failures = 0
    
    def _send_alert(self, alert_type: str, message: str):
        """Send alert with cooldown to prevent spam"""
        now = datetime.now()
        
        # Check cooldown
        if alert_type in self.last_alerts:
            time_since_last = (now - self.last_alerts[alert_type]).total_seconds()
            if time_since_last < self.alert_cooldown:
                return
        
        self.last_alerts[alert_type] = now
        
        # Determine alert priority
        priority = 'high' if 'critical' in alert_type or 'down' in alert_type else 'normal'
        
        # Send notification
        send_notification('system', message, "Resource Alert", priority)
        log_warning('system', f"Resource alert: {message}")
    
    def _cleanup_history(self):
        """Clean up old history data"""
        cutoff = datetime.now() - timedelta(hours=24)  # Keep 24 hours of data
        
        self.cpu_history = [h for h in self.cpu_history if h['timestamp'] > cutoff]
        self.memory_history = [h for h in self.memory_history if h['timestamp'] > cutoff]
        self.disk_history = [h for h in self.disk_history if h['timestamp'] > cutoff]
        self.network_history = [h for h in self.network_history if h['timestamp'] > cutoff]
    
    def add_process_to_monitor(self, process_name: str):
        """Add a process to monitor"""
        if process_name not in self.tracked_processes:
            self.tracked_processes.append(process_name)
            log_info('system', f"Added process to monitoring: {process_name}")
    
    def remove_process_from_monitor(self, process_name: str):
        """Remove a process from monitoring"""
        if process_name in self.tracked_processes:
            self.tracked_processes.remove(process_name)
            log_info('system', f"Removed process from monitoring: {process_name}")
    
    def get_current_stats(self) -> Dict[str, Any]:
        """Get current resource statistics"""
        # CPU stats
        cpu_percent = psutil.cpu_percent()
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()
        
        # Memory stats
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        # Disk stats
        disk = psutil.disk_usage('/')
        
        # Network stats
        network = psutil.net_io_counters()
        
        # System info
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time
        
        return {
            'timestamp': datetime.now().isoformat(),
            'cpu': {
                'percent': cpu_percent,
                'count': cpu_count,
                'frequency_mhz': cpu_freq.current if cpu_freq else None
            },
            'memory': {
                'total_gb': memory.total / 1024 / 1024 / 1024,
                'used_gb': memory.used / 1024 / 1024 / 1024,
                'available_gb': memory.available / 1024 / 1024 / 1024,
                'percent': memory.percent
            },
            'swap': {
                'total_gb': swap.total / 1024 / 1024 / 1024,
                'used_gb': swap.used / 1024 / 1024 / 1024,
                'percent': swap.percent
            },
            'disk': {
                'total_gb': disk.total / 1024 / 1024 / 1024,
                'used_gb': disk.used / 1024 / 1024 / 1024,
                'free_gb': disk.free / 1024 / 1024 / 1024,
                'percent': (disk.used / disk.total) * 100
            },
            'network': {
                'bytes_sent': network.bytes_sent,
                'bytes_recv': network.bytes_recv,
                'packets_sent': network.packets_sent,
                'packets_recv': network.packets_recv,
                'connected': self.network_failures == 0
            },
            'system': {
                'boot_time': boot_time.isoformat(),
                'uptime_hours': uptime.total_seconds() / 3600
            }
        }
    
    def get_historical_data(self, hours: int = 1) -> Dict[str, List[Dict[str, Any]]]:
        """Get historical resource data"""
        cutoff = datetime.now() - timedelta(hours=hours)
        
        return {
            'cpu': [h for h in self.cpu_history if h['timestamp'] > cutoff],
            'memory': [h for h in self.memory_history if h['timestamp'] > cutoff],
            'disk': [h for h in self.disk_history if h['timestamp'] > cutoff],
            'network': [h for h in self.network_history if h['timestamp'] > cutoff]
        }
    
    def get_trading_system_health(self) -> Dict[str, Any]:
        """Get overall trading system health status"""
        stats = self.get_current_stats()
        
        # Determine health status
        health_issues = []
        
        if stats['cpu']['percent'] >= self.thresholds.cpu_critical:
            health_issues.append("Critical CPU usage")
        if stats['memory']['percent'] >= self.thresholds.memory_critical:
            health_issues.append("Critical memory usage")
        if stats['disk']['percent'] >= self.thresholds.disk_critical:
            health_issues.append("Critical disk usage")
        if not stats['network']['connected']:
            health_issues.append("Network connectivity issues")
        
        if health_issues:
            health_status = "critical"
        elif (stats['cpu']['percent'] >= self.thresholds.cpu_warning or 
              stats['memory']['percent'] >= self.thresholds.memory_warning or
              stats['disk']['percent'] >= self.thresholds.disk_warning):
            health_status = "warning"
        else:
            health_status = "healthy"
        
        return {
            'status': health_status,
            'issues': health_issues,
            'stats': stats,
            'monitoring_active': self.monitoring,
            'tracked_processes': self.tracked_processes
        }

# Global resource monitor instance
resource_monitor = ResourceMonitor()

# Auto-start monitoring
resource_monitor.start_monitoring()

# Add common trading processes to monitor
resource_monitor.add_process_to_monitor('python')  # Python processes
resource_monitor.add_process_to_monitor('terminal64')  # MetaTrader if running