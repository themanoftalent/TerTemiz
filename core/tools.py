import os
import winreg
import subprocess
import hashlib
from collections import defaultdict
from core.system_info import format_size

class UninstallManager:
    def __init__(self):
        pass

    def get_installed_programs(self):
        programs = []
        roots = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Uninstall")
        ]

        seen_names = set()

        for root, rpath in roots:
            try:
                base_k = winreg.OpenKey(root, rpath, 0, winreg.KEY_READ)
                for i in range(winreg.QueryInfoKey(base_k)[0]):
                    try:
                        sub_name = winreg.EnumKey(base_k, i)
                        sub_k = winreg.OpenKey(base_k, sub_name, 0, winreg.KEY_READ)

                        # check SystemComponent
                        try:
                            sys_comp, _ = winreg.QueryValueEx(sub_k, "SystemComponent")
                            if sys_comp == 1:
                                winreg.CloseKey(sub_k)
                                continue
                        except Exception:
                            pass

                        try:
                            display_name, _ = winreg.QueryValueEx(sub_k, "DisplayName")
                            if not display_name or display_name.strip() in seen_names:
                                winreg.CloseKey(sub_k)
                                continue
                        except Exception:
                            winreg.CloseKey(sub_k)
                            continue

                        seen_names.add(display_name.strip())

                        publisher = ""
                        try:
                            publisher, _ = winreg.QueryValueEx(sub_k, "Publisher")
                        except Exception:
                            pass

                        version = ""
                        try:
                            version, _ = winreg.QueryValueEx(sub_k, "DisplayVersion")
                        except Exception:
                            pass

                        install_date = ""
                        try:
                            install_date, _ = winreg.QueryValueEx(sub_k, "InstallDate")
                        except Exception:
                            pass

                        size_kb = 0
                        try:
                            size_kb, _ = winreg.QueryValueEx(sub_k, "EstimatedSize")
                        except Exception:
                            pass

                        uninstall_str = ""
                        try:
                            uninstall_str, _ = winreg.QueryValueEx(sub_k, "UninstallString")
                        except Exception:
                            pass

                        programs.append({
                            "name": display_name.strip(),
                            "publisher": publisher.strip() if publisher else "Bilinmiyor",
                            "version": version.strip() if version else "-",
                            "install_date": install_date if install_date else "-",
                            "size_str": format_size(size_kb * 1024) if size_kb > 0 else "-",
                            "size_bytes": size_kb * 1024,
                            "uninstall_string": uninstall_str.strip() if uninstall_str else "",
                            "reg_root": root,
                            "reg_path": f"{rpath}\\{sub_name}",
                            "sub_name": sub_name
                        })

                        winreg.CloseKey(sub_k)
                    except Exception:
                        pass
                winreg.CloseKey(base_k)
            except Exception:
                pass

        # Sort alphabetically
        programs.sort(key=lambda x: x["name"].lower())
        return programs

    def run_uninstall(self, program):
        cmd = program.get("uninstall_string")
        if not cmd:
            return False, "Kaldırma komutu bulunamadı."
        try:
            subprocess.Popen(cmd, shell=True)
            return True, "Kaldırma sihirbazı başlatıldı."
        except Exception as e:
            return False, f"Başlatılamadı: {e}"

    def delete_registry_entry(self, program):
        try:
            parent_path, sub_name = program["reg_path"].rsplit("\\", 1)
            k = winreg.OpenKey(program["reg_root"], parent_path, 0, winreg.KEY_ALL_ACCESS)
            winreg.DeleteKey(k, sub_name)
            winreg.CloseKey(k)
            return True, "Kayıt girdisi başarıyla silindi."
        except Exception as e:
            return False, f"Girdi silinemedi: {e}"

class StartupManager:
    def __init__(self):
        pass

    def get_startup_items(self):
        items = []
        locations = [
            ("Kullanıcı Kayıt Defteri", winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"),
            ("Sistem Kayıt Defteri", winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"),
        ]

        for loc_name, root, path in locations:
            try:
                k = winreg.OpenKey(root, path, 0, winreg.KEY_READ)
                for i in range(winreg.QueryInfoKey(k)[1]):
                    try:
                        vname, vval, _ = winreg.EnumValue(k, i)
                        items.append({
                            "name": vname,
                            "command": vval,
                            "location": loc_name,
                            "root": root,
                            "path": path,
                            "enabled": True
                        })
                    except Exception:
                        pass
                winreg.CloseKey(k)
            except Exception:
                pass

        # Startup folder
        startup_dir = os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup")
        if os.path.exists(startup_dir):
            for f in os.listdir(startup_dir):
                if f.lower() != "desktop.ini":
                    fp = os.path.join(startup_dir, f)
                    items.append({
                        "name": f,
                        "command": fp,
                        "location": "Başlangıç Klasörü",
                        "root": None,
                        "path": fp,
                        "enabled": True
                    })

        return items

    def delete_startup_item(self, item):
        try:
            if item["root"]:
                k = winreg.OpenKey(item["root"], item["path"], 0, winreg.KEY_ALL_ACCESS)
                winreg.DeleteValue(k, item["name"])
                winreg.CloseKey(k)
                return True, "Başlangıç girdisi silindi."
            elif os.path.exists(item["path"]):
                os.remove(item["path"])
                return True, "Başlangıç kısayolu silindi."
        except Exception as e:
            return False, f"Silinemedi: {e}"
        return False, "Geçersiz işlem"

class DiskAnalyzer:
    def __init__(self):
        self.is_scanning = False

    def scan_path(self, target_path, on_progress=None, max_files=20000):
        self.is_scanning = True
        categories = {
            "Videolar": [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm"],
            "Resimler": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg", ".ico", ".raw", ".psd"],
            "Müzikler": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a"],
            "Belgeler": [".pdf", ".docx", ".doc", ".xlsx", ".xls", ".pptx", ".ppt", ".txt", ".csv", ".rtf"],
            "Arşivler": [".zip", ".rar", ".7z", ".tar", ".gz", ".iso", ".cab", ".tgz"],
            "Yürütülebilirler": [".exe", ".msi", ".dll", ".sys", ".bat", ".cmd", ".ps1"]
        }

        category_sizes = defaultdict(int)
        category_counts = defaultdict(int)
        all_files = []
        total_scanned = 0
        total_bytes = 0

        try:
            for root, _, files in os.walk(target_path, topdown=True):
                if not self.is_scanning or total_scanned >= max_files:
                    break
                for f in files:
                    total_scanned += 1
                    if total_scanned % 500 == 0 and on_progress:
                        on_progress(f, total_scanned)
                    try:
                        full_p = os.path.join(root, f)
                        sz = os.path.getsize(full_p)
                        total_bytes += sz
                        ext = os.path.splitext(f)[1].lower()

                        matched = False
                        for cat, exts in categories.items():
                            if ext in exts:
                                category_sizes[cat] += sz
                                category_counts[cat] += 1
                                matched = True
                                break
                        if not matched:
                            category_sizes["Diğer"] += sz
                            category_counts["Diğer"] += 1

                        all_files.append((full_p, f, sz, ext))
                    except Exception:
                        pass
        except Exception:
            pass

        self.is_scanning = False
        all_files.sort(key=lambda x: x[2], reverse=True)
        top_large = all_files[:30]

        return {
            "total_bytes": total_bytes,
            "total_files": total_scanned,
            "categories": [
                {
                    "name": cat,
                    "size": category_sizes[cat],
                    "size_str": format_size(category_sizes[cat]),
                    "count": category_counts[cat],
                    "percent": round((category_sizes[cat] / max(1, total_bytes)) * 100, 1)
                }
                for cat in list(categories.keys()) + ["Diğer"]
            ],
            "top_files": [
                {
                    "path": p,
                    "filename": fn,
                    "size": sz,
                    "size_str": format_size(sz),
                    "ext": ext
                }
                for p, fn, sz, ext in top_large
            ]
        }

    def stop(self):
        self.is_scanning = False

class DuplicateFinder:
    def __init__(self):
        self.is_scanning = False

    def find_duplicates(self, target_folder, min_size_bytes=1024*100, on_progress=None):
        self.is_scanning = True
        size_map = defaultdict(list)
        count = 0

        # Step 1: Group by file size
        for root, _, files in os.walk(target_folder):
            if not self.is_scanning:
                break
            for f in files:
                count += 1
                if count % 200 == 0 and on_progress:
                    on_progress(f"Dosyalar taranıyor... ({count})")
                try:
                    fp = os.path.join(root, f)
                    sz = os.path.getsize(fp)
                    if sz >= min_size_bytes:
                        size_map[sz].append(fp)
                except Exception:
                    pass

        # Step 2: Hash potential duplicates
        duplicates = []
        potential_sizes = [sz for sz, paths in size_map.items() if len(paths) > 1]

        for sz in potential_sizes:
            if not self.is_scanning:
                break
            hash_map = defaultdict(list)
            for fp in size_map[sz]:
                try:
                    h = hashlib.md5()
                    with open(fp, "rb") as f:
                        # read up to 512KB for fast hash comparison
                        chunk = f.read(512 * 1024)
                        h.update(chunk)
                    hash_map[h.hexdigest()].append(fp)
                except Exception:
                    pass

            for hval, paths in hash_map.items():
                if len(paths) > 1:
                    duplicates.append({
                        "size": sz,
                        "size_str": format_size(sz),
                        "paths": paths,
                        "wasted_str": format_size(sz * (len(paths) - 1))
                    })

        self.is_scanning = False
        return duplicates

    def stop(self):
        self.is_scanning = False

if __name__ == "__main__":
    um = UninstallManager()
    progs = um.get_installed_programs()
    print(f"Installed programs detected: {len(progs)}")
    for p in progs[:5]:
        print(f" - {p['name']} ({p['version']}) | {p['publisher']}")
    sm = StartupManager()
    starts = sm.get_startup_items()
    print(f"Startup items detected: {len(starts)}")
    for s in starts[:5]:
        print(f" - {s['name']} -> {s['command'][:50]}")
