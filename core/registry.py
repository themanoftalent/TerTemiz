import os
import winreg
import datetime

class RegistryIssue:
    def __init__(self, category, problem, data, key_root, key_path, value_name=None):
        self.category = category
        self.problem = problem
        self.data = data
        self.key_root = key_root    # winreg.HKEY_CURRENT_USER or winreg.HKEY_LOCAL_MACHINE
        self.key_root_str = "HKEY_LOCAL_MACHINE" if key_root == winreg.HKEY_LOCAL_MACHINE else "HKEY_CURRENT_USER"
        self.key_path = key_path
        self.value_name = value_name
        self.selected = True

    def to_dict(self):
        return {
            "category": self.category,
            "problem": self.problem,
            "data": self.data,
            "key": f"{self.key_root_str}\\{self.key_path}",
            "value_name": self.value_name or "(Varsayılan)",
            "selected": self.selected
        }

class RegistryScanner:
    def __init__(self):
        self.is_scanning = False
        self.issues = []

    def scan(self, categories=None, on_progress=None):
        self.is_scanning = True
        self.issues = []
        all_checks = [
            ("app_paths", "Uygulama Yolları (App Paths)", self._scan_app_paths),
            ("shared_dlls", "Eksik Paylaşılan DLL'ler", self._scan_shared_dlls),
            ("startup_entries", "Geçersiz Başlangıç Girdileri", self._scan_startup_runs),
            ("mui_cache", "MUI Önbelleği Kalıntıları", self._scan_mui_cache),
            ("fonts", "Eksik Fontlar", self._scan_missing_fonts),
            ("file_exts", "Kullanılmayan Dosya Uzantıları", self._scan_file_extensions),
        ]

        total = len(all_checks)
        for idx, (cid, cname, check_func) in enumerate(all_checks):
            if not self.is_scanning:
                break
            if categories is not None and cid not in categories:
                continue
            if on_progress:
                on_progress(cname, idx + 1, total)
            try:
                found = check_func()
                self.issues.extend(found)
            except Exception:
                pass

        self.is_scanning = False
        return self.issues

    def _scan_app_paths(self):
        issues = []
        path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths"
        for root in [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]:
            try:
                base_k = winreg.OpenKey(root, path, 0, winreg.KEY_READ)
                num_subkeys = winreg.QueryInfoKey(base_k)[0]
                for i in range(min(num_subkeys, 300)):
                    try:
                        sub_name = winreg.EnumKey(base_k, i)
                        sub_k = winreg.OpenKey(base_k, sub_name, 0, winreg.KEY_READ)
                        try:
                            val, _ = winreg.QueryValueEx(sub_k, "")
                            if val:
                                clean_val = val.strip(' "').split('",')[0].strip('"')
                                if clean_val.lower().endswith('.exe') and not os.path.exists(clean_val):
                                    issues.append(RegistryIssue(
                                        category="Uygulama Yolları",
                                        problem="Mevcut olmayan uygulama yürütülebilir dosyası",
                                        data=val,
                                        key_root=root,
                                        key_path=f"{path}\\{sub_name}",
                                        value_name=""
                                    ))
                        except Exception:
                            pass
                        winreg.CloseKey(sub_k)
                    except Exception:
                        pass
                winreg.CloseKey(base_k)
            except Exception:
                pass
        return issues

    def _scan_shared_dlls(self):
        issues = []
        path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\SharedDLLs"
        try:
            k = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path, 0, winreg.KEY_READ)
            num_vals = winreg.QueryInfoKey(k)[1]
            for i in range(min(num_vals, 300)):
                try:
                    val_name, _, _ = winreg.EnumValue(k, i)
                    clean_path = os.path.expandvars(val_name.strip(' "'))
                    if clean_path and not os.path.exists(clean_path):
                        issues.append(RegistryIssue(
                            category="Eksik Paylaşılan DLL'ler",
                            problem="Belirtilen dosya diskte bulunamıyor",
                            data=val_name,
                            key_root=winreg.HKEY_LOCAL_MACHINE,
                            key_path=path,
                            value_name=val_name
                        ))
                except Exception:
                    pass
            winreg.CloseKey(k)
        except Exception:
            pass
        return issues

    def _scan_startup_runs(self):
        issues = []
        run_paths = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"),
            (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run")
        ]
        for root, rpath in run_paths:
            try:
                k = winreg.OpenKey(root, rpath, 0, winreg.KEY_READ)
                for i in range(winreg.QueryInfoKey(k)[1]):
                    try:
                        vname, vval, _ = winreg.EnumValue(k, i)
                        if isinstance(vval, str) and vval:
                            cmd_part = vval.strip(' "').split(' -')[0].split(' /')[0].strip('"')
                            cmd_part = os.path.expandvars(cmd_part)
                            if (cmd_part.lower().endswith('.exe') or cmd_part.lower().endswith('.bat')) and not os.path.exists(cmd_part):
                                issues.append(RegistryIssue(
                                    category="Başlangıç Programları",
                                    problem="Bulunamayan başlangıç yürütülebilir dosyası",
                                    data=vval,
                                    key_root=root,
                                    key_path=rpath,
                                    value_name=vname
                                ))
                    except Exception:
                        pass
                winreg.CloseKey(k)
            except Exception:
                pass
        return issues

    def _scan_mui_cache(self):
        issues = []
        path = r"Software\Classes\Local Settings\Software\Microsoft\Windows\Shell\MuiCache"
        try:
            k = winreg.OpenKey(winreg.HKEY_CURRENT_USER, path, 0, winreg.KEY_READ)
            for i in range(min(winreg.QueryInfoKey(k)[1], 300)):
                try:
                    vname, _, _ = winreg.EnumValue(k, i)
                    # format: C:\Path\to\app.exe.FriendlyAppName
                    if ".FriendlyAppName" in vname or ".ApplicationCompany" in vname:
                        exe_path = vname.split(".FriendlyAppName")[0].split(".ApplicationCompany")[0]
                        if not os.path.exists(exe_path):
                            issues.append(RegistryIssue(
                                category="MUI Önbelleği Kalıntıları",
                                problem="Eski/silinmiş program arayüz önbelleği",
                                data=exe_path,
                                key_root=winreg.HKEY_CURRENT_USER,
                                key_path=path,
                                value_name=vname
                            ))
                except Exception:
                    pass
            winreg.CloseKey(k)
        except Exception:
            pass
        return issues

    def _scan_missing_fonts(self):
        issues = []
        path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts"
        fonts_dir = os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Fonts")
        try:
            k = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path, 0, winreg.KEY_READ)
            for i in range(min(winreg.QueryInfoKey(k)[1], 300)):
                try:
                    vname, vval, _ = winreg.EnumValue(k, i)
                    if isinstance(vval, str):
                        full_fpath = vval if os.path.isabs(vval) else os.path.join(fonts_dir, vval)
                        if not os.path.exists(full_fpath):
                            issues.append(RegistryIssue(
                                category="Eksik Fontlar",
                                problem="Font dosyası sistemde bulunamadı",
                                data=vval,
                                key_root=winreg.HKEY_LOCAL_MACHINE,
                                key_path=path,
                                value_name=vname
                            ))
                except Exception:
                    pass
            winreg.CloseKey(k)
        except Exception:
            pass
        return issues

    def _scan_file_extensions(self):
        issues = []
        try:
            k = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\FileExts", 0, winreg.KEY_READ)
            for i in range(min(winreg.QueryInfoKey(k)[0], 200)):
                try:
                    ext = winreg.EnumKey(k, i)
                    # check if subkey OpenWithList is empty or points to nonexistent
                    sub_k = winreg.OpenKey(k, f"{ext}\\OpenWithProgids", 0, winreg.KEY_READ)
                    if winreg.QueryInfoKey(sub_k)[1] == 0:
                        issues.append(RegistryIssue(
                            category="Kullanılmayan Dosya Uzantıları",
                            problem="Tanımlı programı olmayan uzantı ilişkilendirmesi",
                            data=ext,
                            key_root=winreg.HKEY_CURRENT_USER,
                            key_path=f"Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\FileExts\\{ext}",
                            value_name=""
                        ))
                    winreg.CloseKey(sub_k)
                except Exception:
                    pass
            winreg.CloseKey(k)
        except Exception:
            pass
        return issues

    def export_backup(self, target_filepath=None):
        if not target_filepath:
            now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            docs_dir = os.path.expanduser("~\\Documents")
            target_filepath = os.path.join(docs_dir, f"TerTemiz_Registry_Backup_{now}.reg")

        lines = ["Windows Registry Editor Version 5.00\n\n"]
        for issue in self.issues:
            if not issue.selected:
                continue
            lines.append(f"; TerTemiz 7 Backup - {issue.category} - {issue.problem}\n")
            lines.append(f"[{issue.key_root_str}\\{issue.key_path}]\n")
            if issue.value_name:
                escaped_val = issue.data.replace("\\", "\\\\") if isinstance(issue.data, str) else str(issue.data)
                lines.append(f'"{issue.value_name}"="{escaped_val}"\n\n')
            else:
                lines.append(f'@=""\n\n')

        with open(target_filepath, "w", encoding="utf-16") as f:
            f.writelines(lines)
        return target_filepath

    def fix_issues(self, selected_issues=None):
        targets = selected_issues if selected_issues is not None else [iss for iss in self.issues if iss.selected]
        fixed_count = 0
        for issue in targets:
            try:
                k = winreg.OpenKey(issue.key_root, issue.key_path, 0, winreg.KEY_ALL_ACCESS)
                if issue.value_name:
                    winreg.DeleteValue(k, issue.value_name)
                    fixed_count += 1
                else:
                    # Deleting empty key or value
                    pass
                winreg.CloseKey(k)
            except Exception:
                pass
        # Remove fixed from self.issues
        self.issues = [iss for iss in self.issues if iss not in targets]
        return fixed_count

    def stop(self):
        self.is_scanning = False

if __name__ == "__main__":
    scanner = RegistryScanner()
    print("Testing Registry Scan...")
    issues = scanner.scan()
    print(f"Scan complete: Found {len(issues)} issues!")
    for iss in issues[:10]:
        print(f" - [{iss.category}] {iss.problem} -> {iss.data[:60]}")
