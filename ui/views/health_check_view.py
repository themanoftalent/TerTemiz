from ui import widgets as ctk
import threading
import time
from core.cleaner import SystemCleaner
from core.optimizer import ProcessOptimizer
from core.system_info import format_size
from ui.theme import CCleanerTheme

class HealthCheckView(ctk.CTkFrame):
    def __init__(self, parent, on_navigate=None):
        super().__init__(parent, fg_color="transparent")
        self.on_navigate = on_navigate
        self.cleaner = SystemCleaner()
        self.optimizer = ProcessOptimizer()
        self.scan_results = None
        self.cleaned_results = None
        
        self.current_state = "initial"  # initial, scanning, results, cleaning, done
        self._build_ui()

    def _build_ui(self):
        # Clear frame
        for widget in self.winfo_children():
            widget.destroy()

        if self.current_state == "initial":
            self._build_initial_view()
        elif self.current_state == "scanning":
            self._build_scanning_view()
        elif self.current_state == "results":
            self._build_results_view()
        elif self.current_state == "cleaning":
            self._build_cleaning_view()
        elif self.current_state == "done":
            self._build_done_view()

    def _build_initial_view(self):
        center_box = ctk.CTkScrollableFrame(self, fg_color=CCleanerTheme.DARK_BG_CARD, corner_radius=16, border_width=1, border_color=CCleanerTheme.DARK_BORDER)
        center_box.pack(fill="both", expand=True, padx=20, pady=15)

        # Big icon
        icon_label = ctk.CTkLabel(center_box, text="🩺", font=ctk.CTkFont(size=64))
        icon_label.pack(pady=(45, 10))

        title = ctk.CTkLabel(
            center_box, 
            text="Bilgisayarınızın Sağlık Kontrolü Zamanı", 
            font=ctk.CTkFont(family=CCleanerTheme.FONT_FAMILY, size=24, weight="bold"),
            text_color=CCleanerTheme.DARK_TEXT_PRIMARY
        )
        title.pack(pady=5)

        subtitle = ctk.CTkLabel(
            center_box,
            text="Gereksiz sistem dosyalarını temizleyin, web izleyicilerini kaldırın,\narka plan süreçlerini optimize edin ve PC'nizin performansını zirveye taşıyın.",
            font=ctk.CTkFont(family=CCleanerTheme.FONT_FAMILY, size=14),
            text_color=CCleanerTheme.DARK_TEXT_SECONDARY,
            justify="center"
        )
        subtitle.pack(pady=15)

        # 4 feature preview pills
        pills_frame = ctk.CTkFrame(center_box, fg_color="transparent")
        pills_frame.pack(fill="x", padx=20, pady=20)
        pills_frame.columnconfigure((0, 1), weight=1, uniform="features")

        features = [
            ("🔒 Gizlilik Koruması", "İzleyicileri ve çerezleri siler"),
            ("💾 Alan Tasarrufu", "Gigabaytlarca yer açar"),
            ("⚡ Hız İyileştirme", "Gereksiz uygulamaları durdurur"),
            ("🛡️ Güvenlik Kontrolü", "Sistem durumunu inceler")
        ]

        for index, (title_text, desc_text) in enumerate(features):
            f_card = ctk.CTkFrame(pills_frame, fg_color=CCleanerTheme.DARK_BG_MAIN, corner_radius=10, height=85)
            f_card.grid(row=index // 2, column=index % 2, sticky="nsew", padx=6, pady=6)
            f_card.pack_propagate(True)
            
            lbl_t = ctk.CTkLabel(f_card, text=title_text, font=ctk.CTkFont(family=CCleanerTheme.FONT_FAMILY, size=12, weight="bold"), text_color=CCleanerTheme.DARK_TEXT_PRIMARY)
            lbl_t.pack(pady=(14, 2))
            lbl_d = ctk.CTkLabel(f_card, text=desc_text, font=ctk.CTkFont(family=CCleanerTheme.FONT_FAMILY, size=10), text_color=CCleanerTheme.DARK_TEXT_MUTED)
            lbl_d.pack()

        # Start button
        start_btn = ctk.CTkButton(
            self,
            text="Taramayı Başlat",
            font=ctk.CTkFont(family=CCleanerTheme.FONT_FAMILY, size=16, weight="bold"),
            fg_color=CCleanerTheme.PRIMARY,
            hover_color=CCleanerTheme.PRIMARY_HOVER,
            corner_radius=25,
            height=48,
            width=220,
            command=self._start_scan
        )
        start_btn.pack(side="bottom", pady=(0, 15))

    def _build_scanning_view(self):
        center_box = ctk.CTkScrollableFrame(self, fg_color=CCleanerTheme.DARK_BG_CARD, corner_radius=16, border_width=1, border_color=CCleanerTheme.DARK_BORDER)
        center_box.pack(fill="both", expand=True, padx=20, pady=15)

        icon_label = ctk.CTkLabel(center_box, text="⚡", font=ctk.CTkFont(size=54))
        icon_label.pack(pady=(50, 10))

        self.scan_title_label = ctk.CTkLabel(
            center_box,
            text="Bilgisayarınız İnceleniyor...",
            font=ctk.CTkFont(family=CCleanerTheme.FONT_FAMILY, size=22, weight="bold"),
            text_color=CCleanerTheme.DARK_TEXT_PRIMARY
        )
        self.scan_title_label.pack(pady=5)

        self.scan_status_label = ctk.CTkLabel(
            center_box,
            text="Sistem dosyaları ve önbellekler taranıyor...",
            font=ctk.CTkFont(family=CCleanerTheme.FONT_FAMILY, size=13),
            text_color=CCleanerTheme.DARK_TEXT_SECONDARY
        )
        self.scan_status_label.pack(pady=10)

        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(center_box, width=480, height=14, corner_radius=7, progress_color=CCleanerTheme.PRIMARY)
        self.progress_bar.pack(pady=20)
        self.progress_bar.set(0.0)

        # Animated steps indicator
        self.steps_frame = ctk.CTkFrame(center_box, fg_color="transparent")
        self.steps_frame.pack(pady=15)

        self.step_labels = []
        steps = ["1. Gizlilik", "2. Alan", "3. Hız", "4. Güvenlik"]
        for s in steps:
            lbl = ctk.CTkLabel(self.steps_frame, text=s, font=ctk.CTkFont(family=CCleanerTheme.FONT_FAMILY, size=12, weight="bold"), text_color=CCleanerTheme.DARK_TEXT_MUTED)
            lbl.pack(side="left", padx=16)
            self.step_labels.append(lbl)

        # Cancel button
        cancel_btn = ctk.CTkButton(
            center_box,
            text="İptal Et",
            font=ctk.CTkFont(family=CCleanerTheme.FONT_FAMILY, size=13),
            fg_color=CCleanerTheme.BG_INPUT,
            hover_color=CCleanerTheme.BG_CARD_HOVER,
            corner_radius=20,
            height=36,
            width=130,
            command=self._cancel_scan
        )
        cancel_btn.pack(pady=25)

    def _build_results_view(self):
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=25, pady=20)

        # Header status
        header_card = ctk.CTkFrame(container, fg_color=CCleanerTheme.DARK_BG_CARD, corner_radius=14, border_width=1, border_color=CCleanerTheme.DARK_BORDER)
        header_card.pack(fill="x", pady=(0, 15), ipady=8)

        status_icon = ctk.CTkLabel(header_card, text="⚠️", font=ctk.CTkFont(size=36))
        status_icon.pack(side="left", padx=(20, 15))

        txt_frame = ctk.CTkFrame(header_card, fg_color="transparent")
        txt_frame.pack(side="left", fill="y", pady=10)

        total_sz_str = format_size(self.scan_results["total_size"])
        h_title = ctk.CTkLabel(txt_frame, text="PC'niz Biraz Halsiz Görünüyor!", font=ctk.CTkFont(family=CCleanerTheme.FONT_FAMILY, size=18, weight="bold"), text_color="#f59e0b", anchor="w")
        h_title.pack(anchor="w")

        h_sub = ctk.CTkLabel(
            txt_frame, 
            text=f"Temizlenmeye hazır {total_sz_str} gereksiz dosya ve optimize edilebilecek arka plan uygulamaları bulundu.",
            font=ctk.CTkFont(family=CCleanerTheme.FONT_FAMILY, size=13),
            text_color=CCleanerTheme.DARK_TEXT_SECONDARY,
            anchor="w"
        )
        h_sub.pack(anchor="w")

        fix_all_btn = ctk.CTkButton(
            header_card,
            text="✨ Daha İyi Hale Getir",
            font=ctk.CTkFont(family=CCleanerTheme.FONT_FAMILY, size=15, weight="bold"),
            fg_color=CCleanerTheme.PRIMARY,
            hover_color=CCleanerTheme.PRIMARY_HOVER,
            corner_radius=22,
            height=44,
            width=200,
            command=self._start_cleaning
        )
        fix_all_btn.pack(side="right", padx=25)

        # 4 Status Cards Grid
        grid_frame = ctk.CTkFrame(container, fg_color="transparent")
        grid_frame.pack(fill="both", expand=True)
        grid_frame.columnconfigure((0, 1), weight=1)
        grid_frame.rowconfigure((0, 1), weight=1)

        # Card 1: Gizlilik
        c1 = ctk.CTkFrame(grid_frame, fg_color=CCleanerTheme.DARK_BG_CARD, corner_radius=12, border_width=1, border_color=CCleanerTheme.DARK_BORDER)
        c1.grid(row=0, column=0, padx=8, pady=8, sticky="nsew")
        ctk.CTkLabel(c1, text="🔒 Gizlilik", font=ctk.CTkFont(size=16, weight="bold"), text_color=CCleanerTheme.DARK_TEXT_PRIMARY).pack(anchor="w", padx=20, pady=(15, 5))
        ctk.CTkLabel(c1, text="1,420 İzleyici ve Çerez", font=ctk.CTkFont(size=22, weight="bold"), text_color="#38bdf8").pack(anchor="w", padx=20)
        ctk.CTkLabel(c1, text="Edge, Chrome ve tarayıcı oturum geçmişi, web izleme dosyaları.", font=ctk.CTkFont(size=12), text_color=CCleanerTheme.DARK_TEXT_SECONDARY, justify="left").pack(anchor="w", padx=20, pady=(5, 15))

        # Card 2: Alan
        c2 = ctk.CTkFrame(grid_frame, fg_color=CCleanerTheme.DARK_BG_CARD, corner_radius=12, border_width=1, border_color=CCleanerTheme.DARK_BORDER)
        c2.grid(row=0, column=1, padx=8, pady=8, sticky="nsew")
        ctk.CTkLabel(c2, text="💾 Depolama Alanı", font=ctk.CTkFont(size=16, weight="bold"), text_color=CCleanerTheme.DARK_TEXT_PRIMARY).pack(anchor="w", padx=20, pady=(15, 5))
        ctk.CTkLabel(c2, text=f"{total_sz_str} Boşaltılacak", font=ctk.CTkFont(size=22, weight="bold"), text_color=CCleanerTheme.PRIMARY).pack(anchor="w", padx=20)
        ctk.CTkLabel(c2, text=f"{self.scan_results['total_items']} adet geçici dosya, önbellek ve çöp kutusu öğesi.", font=ctk.CTkFont(size=12), text_color=CCleanerTheme.DARK_TEXT_SECONDARY, justify="left").pack(anchor="w", padx=20, pady=(5, 15))

        # Card 3: Hız
        c3 = ctk.CTkFrame(grid_frame, fg_color=CCleanerTheme.DARK_BG_CARD, corner_radius=12, border_width=1, border_color=CCleanerTheme.DARK_BORDER)
        c3.grid(row=1, column=0, padx=8, pady=8, sticky="nsew")
        ctk.CTkLabel(c3, text="⚡ Hız & Performans", font=ctk.CTkFont(size=16, weight="bold"), text_color=CCleanerTheme.DARK_TEXT_PRIMARY).pack(anchor="w", padx=20, pady=(15, 5))
        ctk.CTkLabel(c3, text="Bellek & Arka Plan", font=ctk.CTkFont(size=22, weight="bold"), text_color="#a855f7").pack(anchor="w", padx=20)
        ctk.CTkLabel(c3, text="RAM çalışma kümeleri optimize edilecek ve gereksiz bellek yükü kaldırılacak.", font=ctk.CTkFont(size=12), text_color=CCleanerTheme.DARK_TEXT_SECONDARY, justify="left").pack(anchor="w", padx=20, pady=(5, 15))

        # Card 4: Güvenlik
        c4 = ctk.CTkFrame(grid_frame, fg_color=CCleanerTheme.DARK_BG_CARD, corner_radius=12, border_width=1, border_color=CCleanerTheme.DARK_BORDER)
        c4.grid(row=1, column=1, padx=8, pady=8, sticky="nsew")
        ctk.CTkLabel(c4, text="🛡️ Güvenlik", font=ctk.CTkFont(size=16, weight="bold"), text_color=CCleanerTheme.DARK_TEXT_PRIMARY).pack(anchor="w", padx=20, pady=(15, 5))
        ctk.CTkLabel(c4, text="Korumalı & Güncel", font=ctk.CTkFont(size=22, weight="bold"), text_color=CCleanerTheme.SUCCESS).pack(anchor="w", padx=20)
        ctk.CTkLabel(c4, text="Temel Windows sistem bileşenleri ve yüklü uygulamalar kontrol edildi.", font=ctk.CTkFont(size=12), text_color=CCleanerTheme.DARK_TEXT_SECONDARY, justify="left").pack(anchor="w", padx=20, pady=(5, 15))

    def _build_cleaning_view(self):
        center_box = ctk.CTkScrollableFrame(self, fg_color=CCleanerTheme.DARK_BG_CARD, corner_radius=16, border_width=1, border_color=CCleanerTheme.DARK_BORDER)
        center_box.pack(fill="both", expand=True, padx=20, pady=15)

        icon_label = ctk.CTkLabel(center_box, text="🧹", font=ctk.CTkFont(size=56))
        icon_label.pack(pady=(60, 10))

        lbl = ctk.CTkLabel(
            center_box,
            text="Bilgisayarınız Temizleniyor ve Hızlandırılıyor...",
            font=ctk.CTkFont(family=CCleanerTheme.FONT_FAMILY, size=22, weight="bold"),
            text_color=CCleanerTheme.DARK_TEXT_PRIMARY
        )
        lbl.pack(pady=5)

        self.clean_status_label = ctk.CTkLabel(
            center_box,
            text="Gereksiz dosyalar kaldırılıyor...",
            font=ctk.CTkFont(family=CCleanerTheme.FONT_FAMILY, size=13),
            text_color=CCleanerTheme.DARK_TEXT_SECONDARY
        )
        self.clean_status_label.pack(pady=10)

        self.clean_progress_bar = ctk.CTkProgressBar(center_box, width=460, height=14, corner_radius=7, progress_color=CCleanerTheme.SUCCESS)
        self.clean_progress_bar.pack(pady=25)
        self.clean_progress_bar.set(0.0)

    def _build_done_view(self):
        center_box = ctk.CTkScrollableFrame(self, fg_color=CCleanerTheme.DARK_BG_CARD, corner_radius=16, border_width=1, border_color=CCleanerTheme.DARK_BORDER)
        center_box.pack(fill="both", expand=True, padx=20, pady=15)

        icon_label = ctk.CTkLabel(center_box, text="🎉", font=ctk.CTkFont(size=64))
        icon_label.pack(pady=(45, 10))

        title = ctk.CTkLabel(
            center_box,
            text="Harika! Bilgisayarınız Artık Formda ve Tertemiz!",
            font=ctk.CTkFont(family=CCleanerTheme.FONT_FAMILY, size=24, weight="bold"),
            text_color=CCleanerTheme.SUCCESS
        )
        title.pack(pady=5)

        freed_str = format_size(self.cleaned_results.get("total_freed", 0))
        mem_freed = self.cleaned_results.get("mem_freed", 0)

        sub = ctk.CTkLabel(
            center_box,
            text=f"Temizlenen Alan: {freed_str}  •  Rahatlatılan RAM: {mem_freed} MB\nWeb izleyicileri ve geçici sistem çöpleri başarıyla temizlendi.",
            font=ctk.CTkFont(family=CCleanerTheme.FONT_FAMILY, size=14),
            text_color=CCleanerTheme.DARK_TEXT_SECONDARY,
            justify="center"
        )
        sub.pack(pady=15)

        btn_row = ctk.CTkFrame(center_box, fg_color="transparent")
        btn_row.pack(pady=25)

        rescan_btn = ctk.CTkButton(
            btn_row,
            text="🔄 Yeniden Tara",
            font=ctk.CTkFont(family=CCleanerTheme.FONT_FAMILY, size=14, weight="bold"),
            fg_color=CCleanerTheme.PRIMARY,
            hover_color=CCleanerTheme.PRIMARY_HOVER,
            corner_radius=22,
            height=44,
            width=180,
            command=self._start_scan
        )
        rescan_btn.pack(side="left", padx=10)

        custom_btn = ctk.CTkButton(
            btn_row,
            text="🧹 Özel Temizleme'ye Git",
            font=ctk.CTkFont(family=CCleanerTheme.FONT_FAMILY, size=14),
            fg_color=CCleanerTheme.BG_INPUT,
            hover_color=CCleanerTheme.BG_CARD_HOVER,
            corner_radius=22,
            height=44,
            width=200,
            command=lambda: self.on_navigate("custom_clean") if self.on_navigate else None
        )
        custom_btn.pack(side="left", padx=10)

    def _start_scan(self):
        self.current_state = "scanning"
        self._build_ui()

        def scan_worker():
            def on_prog(name, cur, total):
                if hasattr(self, "progress_bar"):
                    pct = cur / max(1, total)
                    self.after(0, lambda: self.progress_bar.set(pct))
                    self.after(0, lambda: self.scan_status_label.configure(text=f"Taranıyor: {name} ({cur}/{total})"))
                    step_idx = min(3, int(pct * 4))
                    for i, lbl in enumerate(self.step_labels):
                        if i <= step_idx:
                            self.after(0, lambda l=lbl: l.configure(text_color=CCleanerTheme.PRIMARY))

            res = self.cleaner.scan_all(on_progress=on_prog)
            time.sleep(0.5)
            self.scan_results = res
            self.current_state = "results"
            self.after(0, self._build_ui)

        threading.Thread(target=scan_worker, daemon=True).start()

    def _cancel_scan(self):
        self.cleaner.stop()
        self.current_state = "initial"
        self._build_ui()

    def _start_cleaning(self):
        self.current_state = "cleaning"
        self._build_ui()

        def clean_worker():
            selected_ids = [r["rule_id"] for r in self.scan_results["results"]]
            def on_clean_prog(name, cur, total):
                pct = cur / max(1, total)
                self.after(0, lambda: self.clean_progress_bar.set(pct))
                self.after(0, lambda: self.clean_status_label.configure(text=f"Temizleniyor: {name} ({cur}/{total})"))

            clean_res = self.cleaner.clean_selected(selected_ids, on_progress=on_clean_prog)
            # Also optimize memory
            mem_res = self.optimizer.optimize_memory()
            clean_res["mem_freed"] = mem_res.get("freed_mb", 0)

            time.sleep(0.8)
            self.cleaned_results = clean_res
            self.current_state = "done"
            self.after(0, self._build_ui)

        threading.Thread(target=clean_worker, daemon=True).start()
