import psutil
import platform
import time
from datetime import datetime
from typing import Dict, Any

class SystemMetrics:
    """
    Real-time system monitoring using psutil.
    """
    
    @staticmethod
    def get_static_info() -> Dict[str, str]:
        """Returns constant system info (OS, Hostname, etc)"""
        uname = platform.uname()
        return {
            "system": uname.system,
            "node": uname.node,
            "release": uname.release,
            "version": uname.version,
            "machine": uname.machine,
            "processor": uname.processor,
            "boot_time": datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
        }

    @staticmethod
    def get_realtime_metrics() -> Dict[str, Any]:
        """
        Fetches current resource usage.
        Blocking call (cpu_percent intervals).
        """
        # CPU
        cpu_percent = psutil.cpu_percent(interval=None) # Non-blocking if called repeatedly
        cpu_freq = psutil.cpu_freq()
        
        # Memory
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        # Disk
        disk_usage = psutil.disk_usage('/')
        
        # Network (Bytes since boot, calculate delta in the consumer/UI)
        net_io = psutil.net_io_counters()
        
        return {
            "cpu": {
                "usage": cpu_percent,
                "freq_current": f"{cpu_freq.current:.0f}Mhz" if cpu_freq else "N/A"
            },
            "memory": {
                "total": f"{mem.total / (1024**3):.1f} GB",
                "used": f"{mem.used / (1024**3):.1f} GB",
                "percent": mem.percent
            },
            "disk": {
                "total": f"{disk_usage.total / (1024**3):.1f} GB",
                "free": f"{disk_usage.free / (1024**3):.1f} GB",
                "percent": disk_usage.percent
            },
            "network": {
                "bytes_sent": net_io.bytes_sent,
                "bytes_recv": net_io.bytes_recv
            }
        }
