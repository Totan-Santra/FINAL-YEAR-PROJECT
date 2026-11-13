import psutil
import platform
from langchain_core.tools import tool

@tool 
def system_info()->str:
    """Get operating system, CPU, RAM, and disk information."""
    
    try :
        os_name = platform.system()
        memory = psutil.virtual_memory()
        
        disk = psutil.disk_usage(
            str(psutil.disk_partitions()[0].mountpoint)

            if os_name == "windows"
            else "/"
        )
        
        cpu = psutil.cpu_percent(interval=1)
        
        return f"""
Operating System: {platform.system()} {platform.release()}
Architecture: {platform.machine()}
Processor: {platform.processor() or "Unknown"}
CPU Usage: {cpu}%

RAM Total: {memory.total / (1024**3):.2f} GB
RAM Available: {memory.available / (1024**3):.2f} GB
RAM Usage: {memory.percent}%

Disk Total: {disk.total / (1024**3):.2f} GB
Disk Free: {disk.free / (1024**3):.2f} GB
Disk Usage: {disk.percent}%
"""

    except Exception as e:
        return f"System information error: {e}"
    
SYSTEM_TOOLS = [system_info]