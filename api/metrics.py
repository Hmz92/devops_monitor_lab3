import psutil

def get_system_metrics() -> dict:
    """Return a snapshot of the current machine's system metrics.
    
    Uses psutil.cpu_percent(interval=None) to prevent blocking the event loop.
    """
    cpu = psutil.cpu_percent(interval=None)
    
    mem = psutil.virtual_memory()
    mem_percent = mem.percent
    mem_used_gb = round(mem.used / (1024 ** 3), 2)
    
    disk = psutil.disk_usage('/')
    disk_percent = disk.percent
    
    return {
        "cpu_percent": cpu,
        "memory_percent": mem_percent,
        "memory_used_gb": mem_used_gb,
        "disk_percent": disk_percent
    }
