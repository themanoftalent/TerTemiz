import os
import psutil
import ctypes

def trim_all_working_sets():
    trimmed_count = 0
    for p in psutil.process_iter(['pid', 'name']):
        try:
            # PROCESS_ALL_ACCESS or PROCESS_SET_QUOTA | PROCESS_QUERY_INFORMATION
            handle = ctypes.windll.kernel32.OpenProcess(0x001F0FFF, False, p.pid)
            if handle:
                res = ctypes.windll.psapi.EmptyWorkingSet(handle)
                if res:
                    trimmed_count += 1
                ctypes.windll.kernel32.CloseHandle(handle)
        except Exception:
            pass
    return trimmed_count

class ProcessOptimizer:
    def __init__(self):
        pass

    def get_running_apps(self):
        apps = []
        # Filter system essential critical processes to prevent user accidentally freezing Windows
        essential = {
            'system', 'smss.exe', 'csrss.exe', 'wininit.exe', 'services.exe', 'lsass.exe',
            'svchost.exe', 'winlogon.exe', 'explorer.exe', 'dwm.exe', 'spoolsv.exe'
        }

        for p in psutil.process_iter(['pid', 'name', 'memory_info', 'cpu_percent', 'status', 'username']):
            try:
                info = p.info
                name = info['name'] or 'Bilinmeyen'
                if name.lower() in essential:
                    continue

                mem_mb = round(info['memory_info'].rss / (1024 * 1024), 1) if info['memory_info'] else 0
                if mem_mb < 5.0:  # ignore tiny system helpers
                    continue

                cpu_pct = info['cpu_percent'] or 0.0
                status = info['status'] or 'running'

                # Impact calculation
                if mem_mb > 350 or cpu_pct > 7.0:
                    impact = "Yüksek"
                    impact_color = "#ef4444"
                elif mem_mb > 120 or cpu_pct > 2.0:
                    impact = "Orta"
                    impact_color = "#f59e0b"
                else:
                    impact = "Düşük"
                    impact_color = "#10b981"

                is_sleeping = (status == psutil.STATUS_STOPPED)

                apps.append({
                    "pid": info['pid'],
                    "name": name,
                    "memory_mb": mem_mb,
                    "cpu_percent": cpu_pct,
                    "impact": impact,
                    "impact_color": impact_color,
                    "status": "Uyku Modunda" if is_sleeping else "Çalışıyor",
                    "is_sleeping": is_sleeping
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        # Sort by memory usage descending
        apps.sort(key=lambda x: x['memory_mb'], reverse=True)
        return apps

    def suspend_process(self, pid):
        try:
            p = psutil.Process(pid)
            p.suspend()
            return True, "Uygulama başarıyla uyku moduna alındı."
        except Exception as e:
            return False, f"İşlem durdurulamadı: {e}"

    def resume_process(self, pid):
        try:
            p = psutil.Process(pid)
            p.resume()
            return True, "Uygulama başarıyla uyandırıldı."
        except Exception as e:
            return False, f"İşlem uyandırılamadı: {e}"

    def terminate_process(self, pid):
        try:
            p = psutil.Process(pid)
            p.terminate()
            return True, "Uygulama başarıyla sonlandırıldı."
        except Exception as e:
            return False, f"İşlem sonlandırılamadı: {e}"

    def optimize_memory(self):
        before = psutil.virtual_memory().used
        trimmed_count = trim_all_working_sets()
        after = psutil.virtual_memory().used
        freed_mb = max(0, round((before - after) / (1024 * 1024), 1))
        return {
            "trimmed_processes": trimmed_count,
            "freed_mb": freed_mb
        }

if __name__ == "__main__":
    opt = ProcessOptimizer()
    apps = opt.get_running_apps()
    print(f"Detected {len(apps)} active background/desktop apps:")
    for a in apps[:8]:
        print(f" - {a['name']} (PID: {a['pid']}): {a['memory_mb']} MB RAM | CPU: {a['cpu_percent']}% | Etki: {a['impact']}")
    mem_res = opt.optimize_memory()
    print("Memory optimization:", mem_res)
