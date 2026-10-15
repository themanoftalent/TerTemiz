import os
import sys
from ui import widgets as ctk
from PIL import Image

# Ensure project root is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from ui.theme import CCleanerTheme
from ui.constants import APP_VERSION
from core.preferences import load_preferences, save_preferences
from ui.i18n import set_language
from ui.views.updater_view import UpdaterView
from core.system_info import get_system_summary, get_ram_info, get_disk_info
from ui.views.health_check_view import HealthCheckView
from ui.views.custom_clean_view import CustomCleanView
from ui.views.performance_optimizer_view import PerformanceOptimizerView
from ui.views.driver_updater_view import DriverUpdaterView
from ui.views.registry_view import RegistryView
from ui.views.tools_view import ToolsView
from ui.views.settings_view import SettingsView

class TerTemizApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Appearance mode and color theme
        self.preferences = load_preferences()
        set_language(self.preferences["language"])
        ctk.set_appearance_mode(self.preferences["theme"])
        ctk.set_default_color_theme("blue")

        self.title(f"TerTemiz Professional {APP_VERSION}")
        width = min(1280, self.winfo_screenwidth() - 40)
        height = min(820, self.winfo_screenheight() - 120)
        left = max(0, (self.winfo_screenwidth() - width) // 2)
        top = max(0, (self.winfo_screenheight() - height) // 2 - 20)
        self.geometry(f"{width}x{height}+{left}+{top}")
        self.minsize(min(960, width), min(600, height))

        # Set Window Icon if exists
        icon_path = os.path.join(BASE_DIR, "assets", "tertemiz_icon.ico")
        if not os.path.exists(icon_path):
            icon_path = os.path.join(BASE_DIR, "assets", "ccleaner_icon.ico")
        if os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
            except Exception:
                pass

        self.system_info = get_system_summary()
        self.active_tab = "health_check"
        self.views = {}
        self.nav_buttons = {}

        self._build_layout()
        self._navigate_to("health_check")

    def _save_preferences(self):
        try:
            save_preferences(self.preferences)
        except OSError as exc:
            from tkinter import messagebox
            messagebox.showerror("TerTemiz", str(exc), parent=self)

    def _set_theme(self, mode):
        self.preferences["theme"] = mode
        ctk.set_appearance_mode(mode)
        self._save_preferences()

    def _set_language(self, language):
        self.preferences["language"] = language
        set_language(language)
        ctk.refresh_language(self)
        self._save_preferences()

    def _build_layout(self):
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)

        # 1. TOP HEADER (Hardware & Specs)
        self.header_frame = ctk.CTkFrame(self, fg_color=CCleanerTheme.DARK_BG_SIDEBAR, corner_radius=0, border_width=1, border_color=CCleanerTheme.DARK_BORDER)
        self.header_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
        self.header_frame.grid_propagate(True)

        # Left branding in header
        brand_box = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        brand_box.pack(side="top", anchor="w", padx=16, pady=(8, 0))

        # Load Logo image
        logo_png = os.path.join(BASE_DIR, "assets", "tertemiz_logo.png")
        if not os.path.exists(logo_png):
            logo_png = os.path.join(BASE_DIR, "assets", "ccleaner_logo.png")
        if os.path.exists(logo_png):
            try:
                pil_logo = Image.open(logo_png)
                ctk_logo = ctk.CTkImage(light_image=pil_logo, dark_image=pil_logo, size=(28, 28))
                lbl_logo = ctk.CTkLabel(brand_box, image=ctk_logo, text="")
                lbl_logo.pack(side="left", padx=(0, 8))
            except Exception:
                pass

        lbl_brand = ctk.CTkLabel(brand_box, text="TerTemiz", font=ctk.CTkFont(family=CCleanerTheme.FONT_FAMILY, size=18, weight="bold"), text_color=CCleanerTheme.PRIMARY)
        lbl_brand.pack(side="left")

        pro_badge = ctk.CTkLabel(
            brand_box,
            text="PRO",
            font=ctk.CTkFont(family=CCleanerTheme.FONT_FAMILY, size=10, weight="bold"),
            fg_color="#d97706",
            text_color="#ffffff",
            corner_radius=4,
            width=36,
            height=18
        )
        pro_badge.pack(side="left", padx=(8, 0))

        # Right hardware specs summary
        specs_box = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        specs_box.pack(side="top", fill="x", padx=16, pady=6)

        summary_text = f"💻 {self.system_info['os']}  |  🧠 {self.system_info['cpu'].split('@')[0].strip()}  |  📊 {self.system_info['ram']['total']}  |  🎮 {self.system_info['gpu']}"
        lbl_specs = ctk.CTkLabel(
            specs_box,
            text=summary_text,
            font=ctk.CTkFont(family=CCleanerTheme.FONT_FAMILY, size=11),
            text_color=CCleanerTheme.DARK_TEXT_SECONDARY
        )
        lbl_specs.pack(anchor="w")

        # 2. LEFT SIDEBAR NAVIGATION
        self.sidebar_frame = ctk.CTkFrame(self, fg_color=CCleanerTheme.DARK_BG_SIDEBAR, width=270, corner_radius=0, border_width=1, border_color=CCleanerTheme.DARK_BORDER)
        self.sidebar_frame.grid(row=1, column=0, sticky="nsew")
        self.sidebar_frame.grid_propagate(False)

        # Nav items
        nav_items = [
            ("health_check", "🩺  Sağlık Kontrolü"),
            ("custom_clean", "🧹  Özel Temizleme"),
            ("performance", "⚡  Performans İyileştirici"),
            ("updater", "📦  Uygulama Güncelleyici"),
            ("driver_updater", "🔄  Sürücü Güncelleyici"),
            ("registry", "📑  Kayıt Defteri"),
            ("tools", "🛠️  Araçlar"),
            ("settings", "⚙️  Seçenekler"),
        ]

        self.nav_container = ctk.CTkScrollableFrame(self.sidebar_frame, fg_color="transparent")
        self.nav_container.pack(fill="both", expand=True, pady=15, padx=10)

        for tab_id, text in nav_items:
            btn = ctk.CTkButton(
                self.nav_container,
                text=text,
                font=ctk.CTkFont(family=CCleanerTheme.FONT_FAMILY, size=13, weight="bold"),
                anchor="w",
                height=42,
                corner_radius=8,
                fg_color="transparent",
                hover_color=CCleanerTheme.DARK_BG_CARD_HOVER,
                text_color=CCleanerTheme.DARK_TEXT_SECONDARY,
                command=lambda tid=tab_id: self._navigate_to(tid)
            )
            btn.pack(fill="x", pady=3)
            self.nav_buttons[tab_id] = btn

        # Bottom sidebar card (Mini System Vital stats)
        self.bottom_card = ctk.CTkFrame(self.sidebar_frame, fg_color=CCleanerTheme.DARK_BG_CARD, corner_radius=10, border_width=1, border_color=CCleanerTheme.DARK_BORDER)
        self.bottom_card.pack(side="bottom", fill="x", padx=12, pady=15)

        ctk.CTkLabel(self.bottom_card, text="Sistem Durumu", font=ctk.CTkFont(size=11, weight="bold"), text_color=CCleanerTheme.DARK_TEXT_PRIMARY).pack(anchor="w", padx=10, pady=(8, 2))

        # RAM progress
        ram_info = get_ram_info()
        self.lbl_side_ram = ctk.CTkLabel(self.bottom_card, text=f"RAM: %{ram_info['percent']} Dolu", font=ctk.CTkFont(size=10), text_color=CCleanerTheme.DARK_TEXT_SECONDARY)
        self.lbl_side_ram.pack(anchor="w", padx=10)

        self.bar_side_ram = ctk.CTkProgressBar(self.bottom_card, height=6, corner_radius=3, progress_color=CCleanerTheme.PRIMARY)
        self.bar_side_ram.pack(fill="x", padx=10, pady=(2, 8))
        self.bar_side_ram.set(ram_info['percent'] / 100.0)

        # Disk progress
        disk_info = get_disk_info()
        self.lbl_side_disk = ctk.CTkLabel(self.bottom_card, text=f"Disk (C:): {disk_info['free']} Boş", font=ctk.CTkFont(size=10), text_color=CCleanerTheme.DARK_TEXT_SECONDARY)
        self.lbl_side_disk.pack(anchor="w", padx=10)

        self.bar_side_disk = ctk.CTkProgressBar(self.bottom_card, height=6, corner_radius=3, progress_color="#38bdf8")
        self.bar_side_disk.pack(fill="x", padx=10, pady=(2, 10))
        self.bar_side_disk.set(disk_info['percent'] / 100.0)

        # 3. MAIN CONTENT CONTAINER
        self.content_container = ctk.CTkFrame(self, fg_color=CCleanerTheme.DARK_BG_MAIN, corner_radius=0)
        self.content_container.grid(row=1, column=1, sticky="nsew")

    def _navigate_to(self, tab_id):
        self.active_tab = tab_id

        # Update button styles
        for tid, btn in self.nav_buttons.items():
            if tid == tab_id:
                btn.configure(
                    fg_color=CCleanerTheme.PRIMARY,
                    hover_color=CCleanerTheme.PRIMARY_HOVER,
                    text_color="#ffffff"
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    hover_color=CCleanerTheme.DARK_BG_CARD_HOVER,
                    text_color=CCleanerTheme.DARK_TEXT_SECONDARY
                )

        # Lazily instantiate and swap views
        for vid, v in self.views.items():
            v.pack_forget()

        if tab_id not in self.views:
            if tab_id == "health_check":
                self.views[tab_id] = HealthCheckView(self.content_container, on_navigate=self._navigate_to)
            elif tab_id == "custom_clean":
                self.views[tab_id] = CustomCleanView(self.content_container)
            elif tab_id == "performance":
                self.views[tab_id] = PerformanceOptimizerView(self.content_container)
            elif tab_id == "updater":
                self.views[tab_id] = UpdaterView(self.content_container)
            elif tab_id == "driver_updater":
                self.views[tab_id] = DriverUpdaterView(self.content_container)
            elif tab_id == "registry":
                self.views[tab_id] = RegistryView(self.content_container)
            elif tab_id == "tools":
                self.views[tab_id] = ToolsView(self.content_container)
            elif tab_id == "settings":
                self.views[tab_id] = SettingsView(self.content_container, preferences=self.preferences, on_theme_change=self._set_theme, on_language_change=self._set_language)

        self.views[tab_id].pack(fill="both", expand=True)

# Compatibility alias
CCleaner7App = TerTemizApp

if __name__ == "__main__":
    app = TerTemizApp()
    app.mainloop()
