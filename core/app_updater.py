"""WinGet upgrades with locale-independent column boundaries and visible errors."""
import os
import re
import shutil
import subprocess
import threading

ANSI = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")
NO_UPGRADES = 0x8A15002B

def parse_upgrade_table(output):
    lines = ANSI.sub("", output).replace("\r", "\n").splitlines()
    for index, line in enumerate(lines):
        if not re.fullmatch(r"\s*-{5,}\s*", line) or index == 0:
            continue
        # Headers are localized. Column positions, rather than English names,
        # identify Name / Id / Version / Available / optional Source.
        headers = list(re.finditer(r"\S(?:.*?\S)?(?=\s{2,}|$)", lines[index - 1]))
        if len(headers) < 4:
            continue
        starts = [m.start() for m in headers]
        apps = []
        for row in lines[index + 1:]:
            if len(row) <= starts[3]:
                continue
            values = [row[start:starts[i + 1] if i + 1 < len(starts) else len(row)].strip()
                      for i, start in enumerate(starts)]
            name, package_id, version, available = values[:4]
            if not all((name, package_id, version, available)) or " " in package_id or "…" in package_id:
                continue
            apps.append({"name": name, "id": package_id,
                         "installed_version": version, "available_version": available,
                         "source": values[4] if len(values) > 4 else "winget",
                         "status": "Güncelleme Mevcut", "status_color": "#f59e0b"})
        return apps
    raise ValueError("WinGet tablosu okunamadı. WinGet sürümünü ve çıktı günlüğünü kontrol edin.")

class AppUpdater:
    def __init__(self):
        self.is_scanning = False
        self.is_updating = False
        self.last_error = ""
        self.last_output = ""
        self._update_lock = threading.Lock()

    @property
    def has_winget(self):
        return shutil.which("winget") is not None

    def scan_updates(self, on_progress=None):
        self.is_scanning = True
        self.last_error = ""
        try:
            if not self.has_winget:
                raise RuntimeError("WinGet bulunamadı. Microsoft Store üzerinden App Installer uygulamasını yükleyin veya güncelleyin.")
            if on_progress:
                on_progress("Uygulamalar taranıyor...")
            result = subprocess.run(
                ["winget", "upgrade", "--source", "winget", "--disable-interactivity"],
                capture_output=True, text=True, encoding="utf-8", errors="replace",
                timeout=180, shell=False, **self._process_options())
            self.last_output = result.stdout + "\n" + result.stderr
            code = result.returncode & 0xFFFFFFFF
            if code == NO_UPGRADES:
                return []
            if code != 0:
                raise RuntimeError(f"WinGet taraması başarısız (0x{code:08X}).\n{self.last_output.strip()}")
            return parse_upgrade_table(result.stdout)
        except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as exc:
            self.last_error = str(exc)
            return []
        finally:
            self.is_scanning = False

    @staticmethod
    def _process_options():
        return {"creationflags": subprocess.CREATE_NO_WINDOW} if os.name == "nt" else {}

    def run_update(self, pkg_id, on_output=None, on_finish=None):
        if not pkg_id or not self._update_lock.acquire(blocking=False):
            raise RuntimeError("Bir güncelleme zaten çalışıyor veya paket kimliği boş.")
        self.is_updating = True
        def worker():
            success = False
            try:
                # Interactive installer permits UAC and license prompts when needed.
                # Agreements are left to the user instead of being auto-accepted.
                command = ["winget", "upgrade", "--id", pkg_id, "--exact", "--source", "winget", "--interactive"]
                with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                      text=True, encoding="utf-8", errors="replace", shell=False,
                                      **self._process_options()) as process:
                    for line in process.stdout:
                        if on_output and line.strip():
                            on_output(ANSI.sub("", line).strip())
                    code = process.wait()
                    success = code == 0
                    if not success and on_output:
                        on_output(f"WinGet: 0x{code & 0xFFFFFFFF:08X}")
            except (OSError, subprocess.SubprocessError) as exc:
                if on_output:
                    on_output(str(exc))
            finally:
                self.is_updating = False
                self._update_lock.release()
                if on_finish:
                    on_finish(success)
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
        return thread
