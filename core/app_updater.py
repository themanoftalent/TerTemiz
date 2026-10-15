import subprocess
import threading
import re
import shutil

class AppUpdater:
    def __init__(self):
        self.is_scanning = False
        self.is_updating = False
        self.has_winget = (shutil.which("winget") is not None)

    def scan_updates(self, on_progress=None):
        self.is_scanning = True
        apps = []
        if not self.has_winget:
            self.is_scanning = False
            return apps

        try:
            if on_progress:
                on_progress("Yüklü programlar ve güncelleme havuzu taranıyor...")

            # Run winget upgrade
            process = subprocess.Popen(
                ["winget", "upgrade"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                errors="replace",
                shell=True
            )
            stdout, _ = process.communicate()
            lines = stdout.splitlines()

            sep_idx = -1
            for i, l in enumerate(lines):
                if l.startswith("---") or "---" in l:
                    sep_idx = i
                    break

            if sep_idx > 0:
                header = lines[sep_idx - 1]
                id_pos = header.find("Id")
                ver_pos = header.find("Version")
                avail_pos = header.find("Available")
                src_pos = header.find("Source")

                for line in lines[sep_idx + 1:]:
                    if not line.strip() or "upgrade" in line.lower() or "güncelle" in line.lower():
                        continue
                    name = line[:id_pos].strip()
                    pkg_id = line[id_pos:ver_pos].strip()
                    ver = line[ver_pos:avail_pos].strip()
                    avail = line[avail_pos:src_pos if src_pos != -1 else len(line)].strip()
                    src = line[src_pos:].strip() if src_pos != -1 else "winget"

                    if name and pkg_id and ver and avail:
                        apps.append({
                            "name": name,
                            "id": pkg_id,
                            "installed_version": ver,
                            "available_version": avail,
                            "source": src,
                            "status": "Güncelleme Mevcut",
                            "status_color": "#f59e0b"
                        })

        except Exception as e:
            pass

        self.is_scanning = False
        return apps

    def run_update(self, pkg_id, on_output=None, on_finish=None):
        self.is_updating = True

        def worker():
            cmd = [
                "winget", "upgrade",
                "--id", pkg_id,
                "--accept-source-agreements",
                "--accept-package-agreements",
                "--silent"
            ]

            success = False
            try:
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    errors="replace",
                    shell=True,
                    bufsize=1
                )

                for line in process.stdout:
                    if on_output:
                        clean_line = line.strip()
                        if clean_line:
                            on_output(clean_line)

                process.wait()
                success = (process.returncode == 0)

            except Exception as e:
                if on_output:
                    on_output(f"Hata oluştu: {e}")

            self.is_updating = False
            if on_finish:
                on_finish(success)

        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
        return thread

if __name__ == "__main__":
    updater = AppUpdater()
    print("Testing scan_updates...")
    found = updater.scan_updates()
    print(f"Found {len(found)} updates available:")
    for a in found:
        print(f" - {a['name']} ({a['installed_version']} -> {a['available_version']})")
