from ui import widgets as ctk
from ui.theme import CCleanerTheme
from ui.i18n import tr

class SettingsView(ctk.CTkFrame):
    def __init__(self, parent, preferences=None, on_theme_change=None, on_language_change=None):
        super().__init__(parent, fg_color="transparent")
        self.preferences = preferences or {"theme": "system", "language": "tr"}
        self.on_theme_change = on_theme_change
        self.on_language_change = on_language_change
        self._build_ui()

    def _build_ui(self):
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=25, pady=20)

        # Tabview for settings
        tabs = ctk.CTkTabview(
            container,
            fg_color=CCleanerTheme.BG_CARD,
            segmented_button_selected_color=CCleanerTheme.PRIMARY,
            segmented_button_selected_hover_color=CCleanerTheme.PRIMARY_HOVER,
            segmented_button_unselected_color=CCleanerTheme.BG_INPUT,
            segmented_button_unselected_hover_color=CCleanerTheme.BG_CARD_HOVER,
            text_color=CCleanerTheme.TEXT_PRIMARY,
            corner_radius=10
        )
        tabs.pack(fill="both", expand=True)

        tab_gen = tabs.add("⚙️ Genel Ayarlar")
        tab_smart = tabs.add("🧠 Akıllı Temizleme")
        tab_about = tabs.add("ℹ️ Hakkında & Lisans")

        # 1. GENEL AYARLAR
        card_gen = ctk.CTkScrollableFrame(
            tab_gen, 
            fg_color=CCleanerTheme.BG_CARD, 
            corner_radius=12, 
            border_width=1, 
            border_color=CCleanerTheme.BORDER
        )
        card_gen.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(
            card_gen, 
            text="Görünüm ve Arayüz Seçenekleri", 
            font=ctk.CTkFont(size=16, weight="bold"), 
            text_color=CCleanerTheme.TEXT_PRIMARY
        ).pack(anchor="w", padx=20, pady=(20, 10))

        # Theme selector
        row_theme = ctk.CTkFrame(card_gen, fg_color="transparent")
        row_theme.pack(fill="x", padx=20, pady=8)
        
        ctk.CTkLabel(
            row_theme, 
            text="Tema Tercihi:", 
            font=ctk.CTkFont(size=13), 
            text_color=CCleanerTheme.TEXT_SECONDARY
        ).pack(side="left")

        self.theme_choices = {tr("Koyu (Dark)"): "dark", tr("Açık (Light)"): "light", tr("Sistem Teması"): "system"}
        default_val = next(label for label, value in self.theme_choices.items() if value == self.preferences["theme"])

        self.theme_menu = ctk.CTkOptionMenu(
            row_theme,
            values=list(self.theme_choices),
            fg_color=CCleanerTheme.PRIMARY,
            button_color=CCleanerTheme.PRIMARY_HOVER,
            text_color="#ffffff",
            command=self._change_theme
        )
        self.theme_menu.set(default_val)
        self.theme_menu.pack(side="right")

        # Language selector
        row_lang = ctk.CTkFrame(card_gen, fg_color="transparent")
        row_lang.pack(fill="x", padx=20, pady=8)
        
        ctk.CTkLabel(
            row_lang, 
            text="Uygulama Dili:", 
            font=ctk.CTkFont(size=13), 
            text_color=CCleanerTheme.TEXT_SECONDARY
        ).pack(side="left")

        self.lang_menu = ctk.CTkOptionMenu(
            row_lang,
            values=["Türkçe", "English"],
            fg_color=CCleanerTheme.BG_INPUT,
            button_color=CCleanerTheme.BG_CARD_HOVER,
            text_color=CCleanerTheme.TEXT_PRIMARY,
            command=self._change_language
        )
        self.lang_menu.set("English" if self.preferences["language"] == "en" else "Türkçe")
        self.lang_menu.pack(side="right")

        # Toggles
        ctk.CTkLabel(
            card_gen, 
            text="Sistem Entegrasyonu", 
            font=ctk.CTkFont(size=15, weight="bold"), 
            text_color=CCleanerTheme.TEXT_PRIMARY
        ).pack(anchor="w", padx=20, pady=(20, 10))

        cb1 = ctk.CTkCheckBox(
            card_gen, 
            text="Windows başladığında TerTemiz'i otomatik çalıştır", 
            fg_color=CCleanerTheme.PRIMARY, 
            text_color=CCleanerTheme.TEXT_PRIMARY,
            corner_radius=4
        )
        cb1.pack(anchor="w", padx=20, pady=6)

        cb2 = ctk.CTkCheckBox(
            card_gen, 
            text="Geri Dönüşüm Kutusu sağ tık menüsüne 'TerTemiz ile Temizle' seçeneği ekle", 
            fg_color=CCleanerTheme.PRIMARY, 
            text_color=CCleanerTheme.TEXT_PRIMARY,
            corner_radius=4
        )
        cb2.select()
        cb2.pack(anchor="w", padx=20, pady=6)

        cb3 = ctk.CTkCheckBox(
            card_gen, 
            text="Temizleme işleminden sonra özet bildirim penceresi göster", 
            fg_color=CCleanerTheme.PRIMARY, 
            text_color=CCleanerTheme.TEXT_PRIMARY,
            corner_radius=4
        )
        cb3.select()
        cb3.pack(anchor="w", padx=20, pady=6)

        # 2. AKILLI TEMİZLEME
        card_smart = ctk.CTkScrollableFrame(
            tab_smart, 
            fg_color=CCleanerTheme.BG_CARD, 
            corner_radius=12, 
            border_width=1, 
            border_color=CCleanerTheme.BORDER
        )
        card_smart.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(
            card_smart, 
            text="Otomatik Arka Plan Temizleme (Smart Cleaning)", 
            font=ctk.CTkFont(size=16, weight="bold"), 
            text_color=CCleanerTheme.TEXT_PRIMARY
        ).pack(anchor="w", padx=20, pady=(20, 10))

        sw1 = ctk.CTkSwitch(
            card_smart, 
            text="Akıllı Temizlemeyi Etkinleştir", 
            text_color=CCleanerTheme.TEXT_PRIMARY,
            progress_color=CCleanerTheme.PRIMARY
        )
        sw1.select()
        sw1.pack(anchor="w", padx=20, pady=8)

        row_thresh = ctk.CTkFrame(card_smart, fg_color="transparent")
        row_thresh.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            row_thresh, 
            text="Çöp eşiği aşıldığında beni uyar:", 
            font=ctk.CTkFont(size=13), 
            text_color=CCleanerTheme.TEXT_SECONDARY
        ).pack(side="left")

        thresh_menu = ctk.CTkOptionMenu(
            row_thresh, 
            values=["1.0 GB", "2.0 GB", "5.0 GB"], 
            fg_color=CCleanerTheme.PRIMARY,
            text_color="#ffffff"
        )
        thresh_menu.pack(side="right")

        sw2 = ctk.CTkSwitch(
            card_smart, 
            text="Tarayıcılar kapandığında önbelleği otomatik temizle", 
            text_color=CCleanerTheme.TEXT_PRIMARY,
            progress_color=CCleanerTheme.PRIMARY
        )
        sw2.pack(anchor="w", padx=20, pady=8)

        # 3. HAKKINDA & LİSANS
        card_about = ctk.CTkScrollableFrame(
            tab_about, 
            fg_color=CCleanerTheme.BG_CARD, 
            corner_radius=12, 
            border_width=1, 
            border_color=CCleanerTheme.BORDER
        )
        card_about.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(card_about, text="TerTemiz", font=ctk.CTkFont(size=26, weight="bold"), text_color=CCleanerTheme.PRIMARY).pack(pady=(25, 4))
        ctk.CTkLabel(card_about, text="Sürüm 7.0.1 Pro (64-bit)", font=ctk.CTkFont(size=13, weight="bold"), text_color=CCleanerTheme.TEXT_PRIMARY).pack(pady=2)
        ctk.CTkLabel(card_about, text="Modern Windows Sistem Temizleme ve Performans Paketi", font=ctk.CTkFont(size=12), text_color=CCleanerTheme.TEXT_SECONDARY).pack(pady=(0, 20))

        # License card
        lic_box = ctk.CTkFrame(
            card_about, 
            fg_color=CCleanerTheme.BG_INPUT, 
            corner_radius=10, 
            border_width=1, 
            border_color=CCleanerTheme.BORDER
        )
        lic_box.pack(fill="x", padx=40, pady=10, ipady=8)

        ctk.CTkLabel(lic_box, text="👑 TerTemiz Professional Lisansı", font=ctk.CTkFont(size=14, weight="bold"), text_color=CCleanerTheme.GOLD).pack(pady=(8, 2))
        ctk.CTkLabel(lic_box, text="Durum: Süresiz Aktif (Ömür Boyu Pro)", font=ctk.CTkFont(size=12), text_color=CCleanerTheme.SUCCESS).pack()
        ctk.CTkLabel(lic_box, text="Lisans Sahibi: Sistem Yöneticisi (Pro User)", font=ctk.CTkFont(size=11), text_color=CCleanerTheme.TEXT_MUTED).pack(pady=(2, 8))

        ctk.CTkLabel(
            card_about, 
            text="Bu uygulama TerTemiz modern arayüzünü ve Windows için optimize edilmiş\ngerçek sistem temizleme ve güncelleme motorunu sunar.",
            font=ctk.CTkFont(size=11),
            text_color=CCleanerTheme.TEXT_MUTED,
            justify="center"
        ).pack(pady=25)

    def refresh_language(self):
        self.theme_choices = {tr("Koyu (Dark)"): "dark", tr("Açık (Light)"): "light", tr("Sistem Teması"): "system"}
        self.theme_menu.configure(values=list(self.theme_choices))
        self.theme_menu.set(next(label for label, mode in self.theme_choices.items() if mode == self.preferences["theme"]))

    def _change_theme(self, choice):
        mode = self.theme_choices[choice]
        self.preferences["theme"] = mode
        if self.on_theme_change:
            self.on_theme_change(mode)
        else:
            ctk.set_appearance_mode(mode)

    def _change_language(self, choice):
        language = "en" if choice == "English" else "tr"
        if self.on_language_change:
            self.on_language_change(language)
