import time
import psutil
import logging
from typing import Dict, Any
from datetime import datetime, timedelta
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """Performance monitoring and metrics collection"""
    
    def __init__(self):
        self.request_times = deque(maxlen=1000)  # Keep last 1000 requests
        self.error_counts = defaultdict(int)
        self.endpoint_stats = defaultdict(lambda: {"count": 0, "total_time": 0, "errors": 0})
        self.start_time = datetime.now()
    
    def record_request(self, method: str, endpoint: str, duration: float, status_code: int):
        """Record request metrics"""
        self.request_times.append(duration)
        
        key = f"{method} {endpoint}"
        self.endpoint_stats[key]["count"] += 1
        self.endpoint_stats[key]["total_time"] += duration
        
        if status_code >= 400:
            self.endpoint_stats[key]["errors"] += 1
            self.error_counts[status_code] += 1
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_mb": memory.available // (1024 * 1024),
                "disk_percent": disk.percent,
                "disk_free_gb": disk.free // (1024 * 1024 * 1024)
            }
        except Exception as e:
            logger.error(f"Failed to get system metrics: {e}")
            return {}
    
    def get_application_metrics(self) -> Dict[str, Any]:
        """Get application performance metrics"""
        uptime = datetime.now() - self.start_time
        
        # Calculate request statistics
        if self.request_times:
            avg_response_time = sum(self.request_times) / len(self.request_times)
            max_response_time = max(self.request_times)
            min_response_time = min(self.request_times)
        else:
            avg_response_time = max_response_time = min_response_time = 0
        
        # Calculate endpoint statistics
        endpoint_metrics = {}
        for endpoint, stats in self.endpoint_stats.items():
            if stats["count"] > 0:
                endpoint_metrics[endpoint] = {
                    "requests": stats["count"],
                    "avg_response_time": stats["total_time"] / stats["count"],
                    "error_rate": stats["errors"] / stats["count"] * 100,
                    "total_errors": stats["errors"]
                }
        
        return {
            "uptime_seconds": uptime.total_seconds(),
            "total_requests": len(self.request_times),
            "avg_response_time": round(avg_response_time, 4),
            "max_response_time": round(max_response_time, 4),
            "min_response_time": round(min_response_time, 4),
            "error_counts": dict(self.error_counts),
            "endpoint_metrics": endpoint_metrics
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get overall health status"""
        system_metrics = self.get_system_metrics()
        app_metrics = self.get_application_metrics()
        
        # Determine health status
        health_issues = []
        
        if system_metrics.get("cpu_percent", 0) > 80:
            health_issues.append("High CPU usage")
        
        if system_metrics.get("memory_percent", 0) > 85:
            health_issues.append("High memory usage")
        
        if system_metrics.get("disk_percent", 0) > 90:
            health_issues.append("Low disk space")
        
        if app_metrics.get("avg_response_time", 0) > 5:
            health_issues.append("Slow response times")
        
        status = "unhealthy" if health_issues else "healthy"
        
        return {
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "issues": health_issues,
            "system": system_metrics,
            "application": app_metrics
        }

# Global monitor instance
monitor = PerformanceMonitor()