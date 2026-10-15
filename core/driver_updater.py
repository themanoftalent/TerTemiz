import subprocess
import re

class DriverScanner:
    def __init__(self):
        self.is_scanning = False

    def scan_devices(self, on_progress=None):
        self.is_scanning = True
        devices = []
        try:
            # Run pnputil to get connected devices
            out = subprocess.check_output("pnputil /enum-devices /connected", shell=True, text=True, errors="replace")
            blocks = out.split("Instance ID:")

            total = len(blocks)
            for idx, block in enumerate(blocks):
                if not self.is_scanning:
                    break
                if not block.strip():
                    continue

                desc_match = re.search(r"Device Description:\s*(.*)", block)
                class_match = re.search(r"Class Name:\s*(.*)", block)
                mfg_match = re.search(r"Manufacturer Name:\s*(.*)", block)
                driver_match = re.search(r"Driver Name:\s*(.*)", block)
                status_match = re.search(r"Status:\s*(.*)", block)

                desc = desc_match.group(1).strip() if desc_match else ""
                cname = class_match.group(1).strip() if class_match else ""
                mfg = mfg_match.group(1).strip() if mfg_match else "Microsoft"
                drv = driver_match.group(1).strip() if driver_match else ""
                status = status_match.group(1).strip() if status_match else "Started"

                if not desc or "Processor" in cname or "Volume" in cname or "SoftwareDevice" in cname:
                    continue

                # Categorize
                category = "Sistem Aygıtı"
                if any(x in cname.lower() for x in ["display", "graphics", "video"]):
                    category = "Grafik & Ekran"
                elif any(x in cname.lower() for x in ["audio", "media", "sound"]):
                    category = "Ses & Medya"
                elif any(x in cname.lower() for x in ["net", "network", "adapter"]):
                    category = "Ağ Bağdaştırıcısı"
                elif any(x in cname.lower() for x in ["bluetooth", "hid", "mouse", "keyboard", "input"]):
                    category = "Giriş & Bluetooth"

                # Check status
                # If oem driver or generic, mark status
                is_oem = "oem" in drv.lower()
                is_uptodate = True if is_oem or "Started" in status else False

                devices.append({
                    "name": desc,
                    "class": cname,
                    "manufacturer": mfg,
                    "driver_file": drv,
                    "category": category,
                    "status_str": "Windows Update ile denetle",
                    "status_color": "#f59e0b",
                    "version": "—",
                    "date": "—"
                })

                if on_progress and idx % 10 == 0:
                    on_progress(desc, idx, total)

        except Exception as e:
            pass

        self.is_scanning = False
        return devices

    def stop(self):
        self.is_scanning = False

if __name__ == "__main__":
    ds = DriverScanner()
    devs = ds.scan_devices()
    print(f"Scanned {len(devs)} hardware devices:")
    for d in devs[:10]:
        print(f" - [{d['category']}] {d['name']} ({d['manufacturer']}) -> {d['status_str']}")
