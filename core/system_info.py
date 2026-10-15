import os
import platform
import winreg
import ctypes
import psutil
from datetime import datetime

def format_size(bytes_val):
    if bytes_val < 0:
        return "0 B"
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_val < 1024.0:
            return f"{bytes_val:.1f} {unit}"
        bytes_val /= 1024.0
    return f"{bytes_val:.1f} PB"

def get_windows_version():
    try:
        k = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion")
        product_name = winreg.QueryValueEx(k, "ProductName")[0]
        try:
            display_version = winreg.QueryValueEx(k, "DisplayVersion")[0]
        except Exception:
            display_version = ""
        current_build = winreg.QueryValueEx(k, "CurrentBuild")[0]
        arch = "64-bit" if platform.machine().endswith("64") else "32-bit"
        
        # Windows 11 check (build >= 22000 is Windows 11 even if ProductName says Windows 10)
        if int(current_build) >= 22000 and "11" not in product_name:
            product_name = product_name.replace("10", "11")
            
        return f"{product_name} {display_version} ({arch}) - Derleme {current_build}".strip()
    except Exception:
        return f"Windows {platform.release()} {platform.version()}"

def get_cpu_info():
    try:
        k = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System\CentralProcessor\0")
        name = winreg.QueryValueEx(k, "ProcessorNameString")[0].strip()
        cores = psutil.cpu_count(logical=True)
        return f"{name} ({cores} Çekirdek)"
    except Exception:
        return f"{platform.processor()} ({psutil.cpu_count()} Çekirdek)"

def get_gpu_info():
    try:
        base_k = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}")
        for i in range(12):
            try:
                sub = winreg.OpenKey(base_k, f"{i:04d}")
                gpu_name = winreg.QueryValueEx(sub, "DriverDesc")[0]
                if gpu_name and "Basic" not in gpu_name:
                    return gpu_name
            except Exception:
                pass
        return "Tümleşik Grafik Kartı"
    except Exception:
        return "Standart Ekran Kartı"

def get_ram_info():
    vmem = psutil.virtual_memory()
    total_gb = round(vmem.total / (1024**3), 1)
    used_gb = round(vmem.used / (1024**3), 1)
    percent = vmem.percent
    return {
        "total": f"{total_gb} GB",
        "used": f"{used_gb} GB",
        "percent": percent,
        "text": f"{total_gb} GB RAM (%{percent} Kullanılıyor)"
    }

def get_disk_info(drive="C:\\"):
    try:
        usage = psutil.disk_usage(drive)
        total_gb = round(usage.total / (1024**3), 1)
        free_gb = round(usage.free / (1024**3), 1)
        used_gb = round(usage.used / (1024**3), 1)
        percent = usage.percent
        return {
            "drive": drive,
            "total": f"{total_gb} GB",
            "free": f"{free_gb} GB",
            "used": f"{used_gb} GB",
            "percent": percent,
            "free_bytes": usage.free,
            "total_bytes": usage.total
        }
    except Exception:
        return {"drive": drive, "total": "? GB", "free": "? GB", "used": "? GB", "percent": 0, "free_bytes": 0, "total_bytes": 0}

def get_system_summary():
    os_name = get_windows_version()
    cpu = get_cpu_info()
    ram = get_ram_info()
    gpu = get_gpu_info()
    disk = get_disk_info("C:\\")
    return {
        "os": os_name,
        "cpu": cpu,
        "ram": ram,
        "gpu": gpu,
        "disk": disk,
        "summary_line": f"{os_name} | {cpu.split('@')[0].strip()} | {ram['total']} RAM | {gpu}"
    }

if __name__ == "__main__":
    info = get_system_summary()
    print("Summary:", info["summary_line"])
