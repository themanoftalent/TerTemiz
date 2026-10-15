import os
import glob
import shutil
import ctypes
from ctypes import wintypes
import winreg
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor

class SHQUERYRBINFO(ctypes.Structure):
    _fields_ = [
        ('cbSize', wintypes.DWORD),
        ('i64Size', ctypes.c_int64),
        ('i64NumItems', ctypes.c_int64),
    ]

def get_recycle_bin_stats():
    try:
        info = SHQUERYRBINFO()
        info.cbSize = ctypes.sizeof(SHQUERYRBINFO)
        res = ctypes.windll.shell32.SHQueryRecycleBinW(None, ctypes.byref(info))
        if res == 0:
            return {"count": info.i64NumItems, "size": max(0, info.i64Size)}
    except Exception:
        pass
    return {"count": 0, "size": 0}

def empty_recycle_bin():
    try:
        # SHERB_NOCONFIRMATION = 0x00000001, SHERB_NOPROGRESSUI = 0x00000002, SHERB_NOSOUND = 0x00000004
        flags = 0x00000001 | 0x00000002 | 0x00000004
        res = ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, flags)
        return res == 0
    except Exception:
        return False

def flush_dns_cache():
    try:
        # Using DnsFlushResolverCache from dnsapi.dll
        res = ctypes.windll.dnsapi.DnsFlushResolverCache()
        if res == 1:
            return True
    except Exception:
        pass
    try:
        subprocess.run(["ipconfig", "/flushdns"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
        return True
    except Exception:
        return False

def clear_clipboard():
    try:
        if ctypes.windll.user32.OpenClipboard(None):
            ctypes.windll.user32.EmptyClipboard()
            ctypes.windll.user32.CloseClipboard()
            return True
    except Exception:
        pass
    return False

def scan_directory(dir_path, extensions=None, max_depth=3):
    total_size = 0
    files_list = []
    if not os.path.exists(dir_path):
        return total_size, files_list

    base_depth = dir_path.rstrip(os.sep).count(os.sep)

    try:
        for root, dirs, files in os.walk(dir_path, topdown=True, onerror=None):
            current_depth = root.rstrip(os.sep).count(os.sep) - base_depth
            if current_depth > max_depth:
                del dirs[:]
                continue
            for f in files:
                try:
                    if extensions:
                        if not any(f.lower().endswith(ext) for ext in extensions):
                            continue
                    full_p = os.path.join(root, f)
                    sz = os.path.getsize(full_p)
                    total_size += sz
                    files_list.append((full_p, sz))
                except (OSError, PermissionError):
                    continue
    except Exception:
        pass

    return total_size, files_list

class CleanerRule:
    def __init__(self, rule_id, name, category, group="windows", enabled=True, description=""):
        self.rule_id = rule_id
        self.name = name
        self.category = category  # e.g., 'Sistem', 'Gezgin', 'Edge', 'Chrome', 'Uygulamalar'
        self.group = group        # 'windows' or 'applications'
        self.enabled = enabled
        self.description = description
        self.found_items = []
        self.total_size = 0
        self.item_count = 0

    def scan(self):
        raise NotImplementedError

    def clean(self):
        raise NotImplementedError

class RecycleBinRule(CleanerRule):
    def __init__(self):
        super().__init__(
            rule_id="sys_recycle_bin",
            name="Geri Dönüşüm Kutusu",
            category="Sistem",
            group="windows",
            enabled=True,
            description="Silinmiş dosyaların depolandığı Geri Dönüşüm Kutusu içeriği."
        )

    def scan(self):
        stats = get_recycle_bin_stats()
        self.total_size = stats["size"]
        self.item_count = stats["count"]
        self.found_items = [("Geri Dönüşüm Kutusu Dosyaları", stats["size"])] if stats["count"] > 0 else []
        return self.total_size, self.item_count

    def clean(self):
        empty_recycle_bin()
        freed = self.total_size
        self.total_size = 0
        self.item_count = 0
        self.found_items = []
        return freed

class DirectoryRule(CleanerRule):
    def __init__(self, rule_id, name, category, paths, group="windows", extensions=None, enabled=True, description=""):
        super().__init__(rule_id, name, category, group, enabled, description)
        self.paths = paths
        self.extensions = extensions

    def scan(self):
        self.total_size = 0
        self.found_items = []
        for path_expr in self.paths:
            expanded = os.path.expandvars(path_expr)
            if "*" in expanded:
                matches = glob.glob(expanded)
            else:
                matches = [expanded] if os.path.exists(expanded) else []

            for p in matches:
                if os.path.isfile(p):
                    try:
                        sz = os.path.getsize(p)
                        self.total_size += sz
                        self.found_items.append((p, sz))
                    except Exception:
                        pass
                elif os.path.isdir(p):
                    sz, files = scan_directory(p, self.extensions)
                    self.total_size += sz
                    self.found_items.extend(files)

        self.item_count = len(self.found_items)
        return self.total_size, self.item_count

    def clean(self):
        freed = 0
        for item_path, sz in self.found_items:
            try:
                if os.path.isfile(item_path):
                    os.remove(item_path)
                    freed += sz
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path, ignore_errors=True)
                    freed += sz
            except Exception:
                continue

        # Also try cleaning empty directories in target paths
        self.total_size = 0
        self.item_count = 0
        self.found_items = []
        return freed

class DnsRule(CleanerRule):
    def __init__(self):
        super().__init__(
            rule_id="sys_dns_cache",
            name="DNS Çözücü Önbelleği",
            category="Sistem",
            group="windows",
            enabled=True,
            description="Alan adı çözümlemelerini saklayan Windows DNS önbelleğini temizler."
        )

    def scan(self):
        # Simulated/static metric for DNS cache
        self.item_count = 1
        self.total_size = 1024 * 64  # approx 64 KB
        self.found_items = [("Windows DNS Resolver Cache", self.total_size)]
        return self.total_size, self.item_count

    def clean(self):
        flush_dns_cache()
        self.item_count = 0
        self.total_size = 0
        self.found_items = []
        return 1024 * 64

class ClipboardRule(CleanerRule):
    def __init__(self):
        super().__init__(
            rule_id="sys_clipboard",
            name="Pano (Clipboard)",
            category="Sistem",
            group="windows",
            enabled=False,
            description="Kopyalanan metin ve görsellerin bulunduğu Windows panosu."
        )

    def scan(self):
        self.item_count = 1
        self.total_size = 1024 * 16
        self.found_items = [("Windows Pano İçeriği", self.total_size)]
        return self.total_size, self.item_count

    def clean(self):
        clear_clipboard()
        self.item_count = 0
        self.total_size = 0
        self.found_items = []
        return 1024 * 16

class RunMruRule(CleanerRule):
    def __init__(self):
        super().__init__(
            rule_id="exp_run_mru",
            name="Çalıştır Geçmişi",
            category="Windows Gezgini",
            group="windows",
            enabled=True,
            description="Win + R Çalıştır kutusundaki komut geçmişi."
        )

    def scan(self):
        count = 0
        try:
            k = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\RunMRU", 0, winreg.KEY_READ)
            count = winreg.QueryInfoKey(k)[1]
            winreg.CloseKey(k)
        except Exception:
            count = 0
        self.item_count = count
        self.total_size = count * 256
        self.found_items = [("RunMRU Kayıt Defteri Girdileri", self.total_size)] if count > 0 else []
        return self.total_size, self.item_count

    def clean(self):
        try:
            k = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\RunMRU", 0, winreg.KEY_ALL_ACCESS)
            vals = []
            for i in range(winreg.QueryInfoKey(k)[1]):
                vals.append(winreg.EnumValue(k, i)[0])
            for v in vals:
                try:
                    winreg.DeleteValue(k, v)
                except Exception:
                    pass
            winreg.CloseKey(k)
        except Exception:
            pass
        freed = self.total_size
        self.total_size = 0
        self.item_count = 0
        self.found_items = []
        return freed

def build_default_rules():
    rules = [
        # Windows - Sistem
        RecycleBinRule(),
        DirectoryRule(
            "sys_temp", "Geçici Dosyalar (Temp)", "Sistem",
            [r"%TEMP%", r"%WINDIR%\Temp"],
            group="windows", enabled=True,
            description="Kullanıcı ve Windows tarafından oluşturulan geçici sistem dosyaları."
        ),
        DirectoryRule(
            "sys_wer", "Windows Hata Raporlama (WER)", "Sistem",
            [r"%LOCALAPPDATA%\Microsoft\Windows\WER\ReportArchive", r"%LOCALAPPDATA%\Microsoft\Windows\WER\ReportQueue"],
            group="windows", enabled=True,
            description="Çöken uygulamaların oluşturduğu hata raporlama arşivi."
        ),
        DirectoryRule(
            "sys_minidump", "Bellek Dökümleri (Minidump)", "Sistem",
            [r"%WINDIR%\Minidump", r"%WINDIR%\MEMORY.DMP"],
            group="windows", enabled=True,
            description="Mavi ekran ve sistem çökmelerinde oluşan bellek döküm dosyaları."
        ),
        ClipboardRule(),
        DnsRule(),
        DirectoryRule(
            "sys_fontcache", "Font Önbelleği", "Sistem",
            [r"%LOCALAPPDATA%\FontCache"],
            group="windows", enabled=False,
            description="Windows yazı tipi önbelleği."
        ),

        # Windows - Gezgin
        DirectoryRule(
            "exp_recent", "Son Kullanılan Dosyalar", "Windows Gezgini",
            [r"%APPDATA%\Microsoft\Windows\Recent"],
            group="windows", enabled=True,
            description="Gezginde son açılan dosya ve klasör kısayolları."
        ),
        DirectoryRule(
            "exp_thumbnails", "Küçük Resim (Thumbnail) Önbelleği", "Windows Gezgini",
            [r"%LOCALAPPDATA%\Microsoft\Windows\Explorer"],
            group="windows", extensions=[".db"], enabled=True,
            description="Klasörlerdeki görsel ve video önizleme önbellekleri (thumbcache)."
        ),
        RunMruRule(),

        # Windows - Microsoft Edge
        DirectoryRule(
            "edge_cache", "İnternet Önbelleği", "Microsoft Edge",
            [
                r"%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Cache",
                r"%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Code Cache",
                r"%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\GPUCache"
            ],
            group="windows", enabled=True,
            description="Edge tarayıcısının indirdiği geçici web sitesi verileri."
        ),
        DirectoryRule(
            "edge_cookies", "Çerezler ve Oturum Verileri", "Microsoft Edge",
            [r"%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Network\Cookies"],
            group="windows", enabled=False,
            description="Edge üzerinde saklanan web sitesi çerezleri."
        ),
        DirectoryRule(
            "edge_history", "İnternet Geçmişi", "Microsoft Edge",
            [r"%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\History"],
            group="windows", enabled=False,
            description="Ziyaret edilen web sayfaları listesi."
        ),

        # Uygulamalar - Google Chrome
        DirectoryRule(
            "chrome_cache", "İnternet Önbelleği", "Google Chrome",
            [
                r"%LOCALAPPDATA%\Google\Chrome\User Data\Default\Cache",
                r"%LOCALAPPDATA%\Google\Chrome\User Data\Default\Code Cache",
                r"%LOCALAPPDATA%\Google\Chrome\User Data\Default\GPUCache"
            ],
            group="applications", enabled=True,
            description="Google Chrome web siteleri ve JavaScript önbelleği."
        ),
        DirectoryRule(
            "chrome_cookies", "Çerezler", "Google Chrome",
            [r"%LOCALAPPDATA%\Google\Chrome\User Data\Default\Network\Cookies"],
            group="applications", enabled=False,
            description="Chrome tarayıcısındaki web sitesi çerezleri."
        ),
        DirectoryRule(
            "chrome_history", "İnternet Geçmişi", "Google Chrome",
            [r"%LOCALAPPDATA%\Google\Chrome\User Data\Default\History"],
            group="applications", enabled=False,
            description="Chrome tarayıcı ziyaret geçmişi."
        ),

        # Uygulamalar - Mozilla Firefox
        DirectoryRule(
            "firefox_cache", "İnternet Önbelleği", "Mozilla Firefox",
            [r"%LOCALAPPDATA%\Mozilla\Firefox\Profiles\*\cache2"],
            group="applications", enabled=True,
            description="Firefox web önbellek dosyaları."
        ),

        # Uygulamalar - Brave
        DirectoryRule(
            "brave_cache", "İnternet Önbelleği", "Brave Browser",
            [r"%LOCALAPPDATA%\BraveSoftware\Brave-Browser\User Data\Default\Cache"],
            group="applications", enabled=True,
            description="Brave tarayıcısı web önbelleği."
        ),

        # Uygulamalar - Diğer Uygulama Önbellekleri
        DirectoryRule(
            "app_discord", "Discord Önbelleği", "Uygulamalar",
            [
                r"%APPDATA%\discord\Cache",
                r"%APPDATA%\discord\Code Cache",
                r"%APPDATA%\discord\GPUCache"
            ],
            group="applications", enabled=True,
            description="Discord masaüstü uygulamasının sohbet ve medya önbelleği."
        ),
        DirectoryRule(
            "app_spotify", "Spotify Şarkı Önbelleği", "Uygulamalar",
            [r"%LOCALAPPDATA%\Spotify\Data", r"%LOCALAPPDATA%\Spotify\Storage"],
            group="applications", enabled=True,
            description="Spotify dinleme ve görsel önbelleği."
        ),
        DirectoryRule(
            "app_vscode", "Visual Studio Code Önbelleği", "Uygulamalar",
            [r"%APPDATA%\Code\Cache", r"%APPDATA%\Code\CachedData", r"%APPDATA%\Code\GPUCache"],
            group="applications", enabled=True,
            description="VS Code editörünün derleme ve arayüz önbelleği."
        ),
        DirectoryRule(
            "app_pip_npm", "Paket Yöneticisi Önbellekleri (pip / npm)", "Geliştirici Araçları",
            [r"%LOCALAPPDATA%\pip\cache", r"%APPDATA%\npm-cache"],
            group="applications", enabled=True,
            description="Python pip ve Node npm tarafından indirilen paket arşivleri."
        )
    ]
    return rules

class SystemCleaner:
    def __init__(self):
        self.rules = build_default_rules()
        self.is_scanning = False
        self.is_cleaning = False

    def get_rules_by_group(self, group):
        return [r for r in self.rules if r.group == group]

    def scan_all(self, on_progress=None, selected_ids=None):
        self.is_scanning = True
        total_freed_est = 0
        total_items = 0
        results = []

        rules_to_scan = [
            r for r in self.rules
            if (selected_ids is None and r.enabled) or (selected_ids is not None and r.rule_id in selected_ids)
        ]

        total_rules = len(rules_to_scan)
        for idx, rule in enumerate(rules_to_scan):
            if not self.is_scanning:
                break
            if on_progress:
                on_progress(rule.name, idx + 1, total_rules)
            try:
                sz, count = rule.scan()
                total_freed_est += sz
                total_items += count
                results.append({
                    "rule_id": rule.rule_id,
                    "name": rule.name,
                    "category": rule.category,
                    "group": rule.group,
                    "size": sz,
                    "count": count,
                    "items": rule.found_items[:150]  # preview
                })
            except Exception as e:
                pass

        self.is_scanning = False
        return {
            "total_size": total_freed_est,
            "total_items": total_items,
            "results": results
        }

    def clean_selected(self, selected_ids, on_progress=None):
        self.is_cleaning = True
        total_cleaned = 0
        cleaned_rules = []

        target_rules = [r for r in self.rules if r.rule_id in selected_ids]
        total_targets = len(target_rules)

        for idx, rule in enumerate(target_rules):
            if not self.is_cleaning:
                break
            if on_progress:
                on_progress(rule.name, idx + 1, total_targets)
            try:
                freed = rule.clean()
                total_cleaned += freed
                cleaned_rules.append({"name": rule.name, "freed": freed})
            except Exception:
                pass

        self.is_cleaning = False
        return {
            "total_freed": total_cleaned,
            "cleaned_rules": cleaned_rules
        }

    def stop(self):
        self.is_scanning = False
        self.is_cleaning = False

if __name__ == "__main__":
    cleaner = SystemCleaner()
    print("Testing Quick Scan...")
    res = cleaner.scan_all()
    print(f"Scan complete: {res['total_items']} items, {res['total_size']} bytes")
    for r in res["results"]:
        if r["size"] > 0:
            print(f" - [{r['category']}] {r['name']}: {r['count']} files ({r['size'] / 1024 / 1024:.2f} MB)")
