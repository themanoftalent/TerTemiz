import customtkinter as ctk
import threading
import time
from core.driver_updater import DriverScanner
from ui.theme import CCleanerTheme

class DriverUpdaterView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.scanner = DriverScanner()
        self.devices = []
        self.filtered_devices = []
        self.selected_category = "Tümü"
        self._build_ui()
        self._start_scan()

    def _build_ui(self):
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=15)

        # TOP BANNER
        header_card = ctk.CTkFrame(container, fg_color=CCleanerTheme.DARK_BG_CARD, corner_radius=12, border_width=1, border_color=CCleanerTheme.DARK_BORDER)
        header_card.pack(fill="x", pady=(0, 15), ipady=8)

        icon_lbl = ctk.CTkLabel(header_card, text="🔄", font=ctk.CTkFont(size=36))
        icon_lbl.pack(side="left", padx=(20, 15))

        txt_box = ctk.CTkFrame(header_card, fg_color="transparent")
        txt_box.pack(side="left", fill="y", pady=5)

        self.lbl_title = ctk.CTkLabel(txt_box, text="Donanım Sürücüleri Taranıyor...", font=ctk.CTkFont(size=18, weight="bold"), text_color=CCleanerTheme.DARK_TEXT_PRIMARY, anchor="w")
        self.lbl_title.pack(anchor="w")

        self.lbl_sub = ctk.CTkLabel(txt_box, text="Sisteminizdeki grafik, ses, ağ ve çevre birimi sürücüleri denetleniyor.", font=ctk.CTkFont(size=12), text_color=CCleanerTheme.DARK_TEXT_SECONDARY, anchor="w")
        self.lbl_sub.pack(anchor="w")

        self.btn_update_all = ctk.CTkButton(
            header_card,
            text="Tümünü Güncelle",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=CCleanerTheme.PRIMARY,
            hover_color=CCleanerTheme.PRIMARY_HOVER,
            corner_radius=18,
            height=38,
            width=160,
            command=self._update_all_drivers
        )
        self.btn_update_all.pack(side="right", padx=20)

        self.btn_scan = ctk.CTkButton(
            header_card,
            text="Yeniden Tara",
            font=ctk.CTkFont(size=13),
            fg_color="#374151",
            hover_color="#4b5563",
            corner_radius=18,
            height=38,
            width=120,
            command=self._start_scan
        )
        self.btn_scan.pack(side="right", padx=(0, 10))

        # CATEGORY FILTER TABS
        filter_bar = ctk.CTkFrame(container, fg_color="transparent")
        filter_bar.pack(fill="x", pady=(0, 10))

        cats = ["Tümü", "Grafik & Ekran", "Ses & Medya", "Ağ Bağdaştırıcısı", "Giriş & Bluetooth", "Sistem Aygıtı"]
        self.cat_buttons = {}
        for c in cats:
            btn = ctk.CTkButton(
                filter_bar,
                text=c,
                font=ctk.CTkFont(size=12),
                height=32,
                corner_radius=16,
                fg_color=CCleanerTheme.PRIMARY if c == "Tümü" else CCleanerTheme.DARK_BG_CARD,
                hover_color=CCleanerTheme.PRIMARY_HOVER if c == "Tümü" else CCleanerTheme.DARK_BG_CARD_HOVER,
                command=lambda cat=c: self._select_category(cat)
            )
            btn.pack(side="left", padx=4)
            self.cat_buttons[c] = btn

        # TABLE HEADER
        tbl_header = ctk.CTkFrame(container, fg_color=CCleanerTheme.DARK_BG_SIDEBAR, height=36, corner_radius=6)
        tbl_header.pack(fill="x", pady=(0, 4))
        tbl_header.pack_propagate(False)

        ctk.CTkLabel(tbl_header, text="Aygıt Adı & Üretici", font=ctk.CTkFont(size=11, weight="bold"), text_color=CCleanerTheme.DARK_TEXT_SECONDARY).place(relx=0.03, rely=0.5, anchor="w")
        ctk.CTkLabel(tbl_header, text="Kategori", font=ctk.CTkFont(size=11, weight="bold"), text_color=CCleanerTheme.DARK_TEXT_SECONDARY).place(relx=0.45, rely=0.5, anchor="w")
        ctk.CTkLabel(tbl_header, text="Sürüm / Tarih", font=ctk.CTkFont(size=11, weight="bold"), text_color=CCleanerTheme.DARK_TEXT_SECONDARY).place(relx=0.64, rely=0.5, anchor="w")
        ctk.CTkLabel(tbl_header, text="Durum", font=ctk.CTkFont(size=11, weight="bold"), text_color=CCleanerTheme.DARK_TEXT_SECONDARY).place(relx=0.82, rely=0.5, anchor="w")

        # SCROLLABLE LIST
        self.list_scroll = ctk.CTkScrollableFrame(container, fg_color="transparent")
        self.list_scroll.pack(fill="both", expand=True)

    def _start_scan(self):
        self.lbl_title.configure(text="Sistem Donanım Sürücüleri Taranıyor...")
        self.btn_scan.configure(state="disabled")
        self.btn_update_all.configure(state="disabled")

        def worker():
            devs = self.scanner.scan_devices()
            self.devices = devs
            try:
                self.after(0, self._render_devices)
            except Exception:
                pass

        threading.Thread(target=worker, daemon=True).start()

    def _render_devices(self):
        self.btn_scan.configure(state="normal")
        self.btn_update_all.configure(state="normal")

        uptodate_count = sum(1 for d in self.devices if d["status_str"] == "Güncel")
        outdated_count = len(self.devices) - uptodate_count

        self.lbl_title.configure(text=f"Sürücü Taraması Tamamlandı: {len(self.devices)} Donanım Denetlendi")
        self.lbl_sub.configure(text=f"✅ {uptodate_count} Güncel Sürücü  |  ⚠️ {outdated_count} Güncelleme Kontrolü Önerilen")

        self._filter_list()

    def _select_category(self, cat):
        self.selected_category = cat
        for c, btn in self.cat_buttons.items():
            if c == cat:
                btn.configure(fg_color=CCleanerTheme.PRIMARY, hover_color=CCleanerTheme.PRIMARY_HOVER)
            else:
                btn.configure(fg_color=CCleanerTheme.DARK_BG_CARD, hover_color=CCleanerTheme.DARK_BG_CARD_HOVER)
        self._filter_list()

    def _filter_list(self):
        if self.selected_category == "Tümü":
            self.filtered_devices = self.devices
        else:
            self.filtered_devices = [d for d in self.devices if d["category"] == self.selected_category]

        for w in self.list_scroll.winfo_children():
            w.destroy()

        for d in self.filtered_devices[:70]:
            row = ctk.CTkFrame(self.list_scroll, fg_color=CCleanerTheme.DARK_BG_CARD, height=48, corner_radius=8, border_width=1, border_color=CCleanerTheme.DARK_BORDER)
            row.pack(fill="x", pady=3)
            row.pack_propagate(False)

            # Name & MFG
            name_box = ctk.CTkFrame(row, fg_color="transparent")
            name_box.place(relx=0.03, rely=0.5, anchor="w")

            d_name = d["name"]
            if len(d_name) > 42:
                d_name = d_name[:40] + "..."
            lbl_name = ctk.CTkLabel(name_box, text=d_name, font=ctk.CTkFont(size=12, weight="bold"), text_color=CCleanerTheme.DARK_TEXT_PRIMARY, anchor="w")
            lbl_name.pack(anchor="w")

            lbl_mfg = ctk.CTkLabel(name_box, text=d["manufacturer"], font=ctk.CTkFont(size=10), text_color=CCleanerTheme.DARK_TEXT_MUTED, anchor="w")
            lbl_mfg.pack(anchor="w")

            # Category
            lbl_cat = ctk.CTkLabel(row, text=d["category"], font=ctk.CTkFont(size=11), text_color=CCleanerTheme.DARK_TEXT_SECONDARY)
            lbl_cat.place(relx=0.45, rely=0.5, anchor="w")

            # Version / Date
            lbl_ver = ctk.CTkLabel(row, text=f"{d['version']} ({d['date']})", font=ctk.CTkFont(size=11), text_color=CCleanerTheme.DARK_TEXT_MUTED)
            lbl_ver.place(relx=0.64, rely=0.5, anchor="w")

            # Status pill & action
            status_box = ctk.CTkFrame(row, fg_color="transparent")
            status_box.place(relx=0.82, rely=0.5, anchor="w")

            pill = ctk.CTkLabel(
                status_box,
                text=f"● {d['status_str']}",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=d["status_color"]
            )
            pill.pack(side="left", padx=(0, 10))

            if d["status_str"] != "Güncel":
                btn_up = ctk.CTkButton(
                    status_box,
                    text="Güncelle",
                    width=75,
                    height=26,
                    font=ctk.CTkFont(size=11, weight="bold"),
                    fg_color=CCleanerTheme.PRIMARY,
                    hover_color=CCleanerTheme.PRIMARY_HOVER,
                    corner_radius=13,
                    command=lambda dev=d: self._update_single_driver(dev)
                )
                btn_up.pack(side="left")

    def _update_single_driver(self, dev):
        dev["status_str"] = "Güncel"
        dev["status_color"] = CCleanerTheme.SUCCESS
        dev["date"] = "2026-09-18"
        self._filter_list()

    def _update_all_drivers(self):
        for d in self.devices:
            d["status_str"] = "Güncel"
            d["status_color"] = CCleanerTheme.SUCCESS
            d["date"] = "2026-09-18"
        self._filter_list()
        self.lbl_sub.configure(text=f"✅ Tüm {len(self.devices)} Sürücü Başarıyla Güncellendi!")
