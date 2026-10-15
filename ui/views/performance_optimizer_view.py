from ui import widgets as ctk
import threading
from core.optimizer import ProcessOptimizer
from core.system_info import get_ram_info
from ui.theme import CCleanerTheme

class PerformanceOptimizerView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.optimizer = ProcessOptimizer()
        self.apps = []
        self.filtered_apps = []
        self._build_ui()
        self._refresh_data()

    def _build_ui(self):
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=15)

        # TOP STATS ROW
        top_row = ctk.CTkFrame(container, fg_color="transparent")
        top_row.pack(fill="x", pady=(0, 15))
        top_row.columnconfigure((0, 1, 2), weight=1)

        # Card 1: RAM Status
        self.card_ram = ctk.CTkFrame(top_row, fg_color=CCleanerTheme.DARK_BG_CARD, corner_radius=12, border_width=1, border_color=CCleanerTheme.DARK_BORDER)
        self.card_ram.grid(row=0, column=0, padx=6, sticky="nsew", ipady=6)
        ctk.CTkLabel(self.card_ram, text="🧠 Bellek (RAM) Kullanımı", font=ctk.CTkFont(size=12, weight="bold"), text_color=CCleanerTheme.DARK_TEXT_SECONDARY).pack(anchor="w", padx=15, pady=(10, 2))
        self.lbl_ram_pct = ctk.CTkLabel(self.card_ram, text="--%", font=ctk.CTkFont(size=22, weight="bold"), text_color=CCleanerTheme.PRIMARY)
        self.lbl_ram_pct.pack(anchor="w", padx=15)
        self.lbl_ram_detail = ctk.CTkLabel(self.card_ram, text="-- GB / -- GB", font=ctk.CTkFont(size=11), text_color=CCleanerTheme.DARK_TEXT_MUTED)
        self.lbl_ram_detail.pack(anchor="w", padx=15, pady=(0, 10))

        # Card 2: Running Apps
        self.card_apps = ctk.CTkFrame(top_row, fg_color=CCleanerTheme.DARK_BG_CARD, corner_radius=12, border_width=1, border_color=CCleanerTheme.DARK_BORDER)
        self.card_apps.grid(row=0, column=1, padx=6, sticky="nsew", ipady=6)
        ctk.CTkLabel(self.card_apps, text="⚡ Arka Plan Uygulamaları", font=ctk.CTkFont(size=12, weight="bold"), text_color=CCleanerTheme.DARK_TEXT_SECONDARY).pack(anchor="w", padx=15, pady=(10, 2))
        self.lbl_app_count = ctk.CTkLabel(self.card_apps, text="-- Uygulama", font=ctk.CTkFont(size=22, weight="bold"), text_color="#38bdf8")
        self.lbl_app_count.pack(anchor="w", padx=15)
        self.lbl_app_impact = ctk.CTkLabel(self.card_apps, text="-- yüksek etki algılandı", font=ctk.CTkFont(size=11), text_color=CCleanerTheme.DARK_TEXT_MUTED)
        self.lbl_app_impact.pack(anchor="w", padx=15, pady=(0, 10))

        # Card 3: Quick Boost action
        self.card_action = ctk.CTkFrame(top_row, fg_color=CCleanerTheme.DARK_BG_CARD, corner_radius=12, border_width=1, border_color=CCleanerTheme.DARK_BORDER)
        self.card_action.grid(row=0, column=2, padx=6, sticky="nsew", ipady=6)
        ctk.CTkLabel(self.card_action, text="🚀 Hızlı Bellek Boşaltma", font=ctk.CTkFont(size=12, weight="bold"), text_color=CCleanerTheme.DARK_TEXT_SECONDARY).pack(anchor="w", padx=15, pady=(10, 2))
        self.btn_boost_ram = ctk.CTkButton(
            self.card_action,
            text="RAM'i Rahatlat",
            font=ctk.CTkFont(family=CCleanerTheme.FONT_FAMILY, size=13, weight="bold"),
            fg_color=CCleanerTheme.PRIMARY,
            hover_color=CCleanerTheme.PRIMARY_HOVER,
            corner_radius=18,
            height=34,
            command=self._boost_memory
        )
        self.btn_boost_ram.pack(anchor="w", padx=15, pady=8)

        # TOOLBAR
        toolbar = ctk.CTkFrame(container, fg_color="transparent")
        toolbar.pack(fill="x", pady=(0, 10))

        self.search_entry = ctk.CTkEntry(
            toolbar,
            placeholder_text="🔍 Uygulama Ara...",
            width=260,
            height=36,
            corner_radius=18,
            fg_color=CCleanerTheme.DARK_BG_INPUT,
            border_color=CCleanerTheme.DARK_BORDER
        )
        self.search_entry.pack(side="left")
        self.search_entry.bind("<KeyRelease>", lambda e: self._filter_apps())

        btn_refresh = ctk.CTkButton(
            toolbar,
            text="🔄 Yenile",
            font=ctk.CTkFont(size=12),
            fg_color=CCleanerTheme.BG_INPUT,
            hover_color=CCleanerTheme.BG_CARD_HOVER,
            corner_radius=18,
            width=90,
            height=36,
            command=self._refresh_data
        )
        btn_refresh.pack(side="right")

        # TABLE HEADER
        tbl_header = ctk.CTkFrame(container, fg_color=CCleanerTheme.DARK_BG_SIDEBAR, height=36, corner_radius=6)
        tbl_header.pack(fill="x", pady=(0, 4))
        tbl_header.grid_propagate(True)

        ctk.table_cell(ctk.CTkLabel(tbl_header, text="Uygulama Adı (PID)", font=ctk.CTkFont(size=11, weight="bold"), text_color=CCleanerTheme.DARK_TEXT_SECONDARY), 0.03)
        ctk.table_cell(ctk.CTkLabel(tbl_header, text="RAM Kullanımı", font=ctk.CTkFont(size=11, weight="bold"), text_color=CCleanerTheme.DARK_TEXT_SECONDARY), 0.45)
        ctk.table_cell(ctk.CTkLabel(tbl_header, text="Sistem Etkisi", font=ctk.CTkFont(size=11, weight="bold"), text_color=CCleanerTheme.DARK_TEXT_SECONDARY), 0.62)
        ctk.table_cell(ctk.CTkLabel(tbl_header, text="Eylemler", font=ctk.CTkFont(size=11, weight="bold"), text_color=CCleanerTheme.DARK_TEXT_SECONDARY), 0.82)

        # SCROLLABLE PROCESS LIST
        self.list_scroll = ctk.CTkScrollableFrame(container, fg_color="transparent")
        self.list_scroll.pack(fill="both", expand=True)

    def _refresh_data(self):
        ram_info = get_ram_info()
        self.lbl_ram_pct.configure(text=f"%{ram_info['percent']}")
        self.lbl_ram_detail.configure(text=f"{ram_info['used']} / {ram_info['total']}")

        def worker():
            apps = self.optimizer.get_running_apps()
            self.apps = apps
            try:
                self.after(0, self._filter_apps)
            except Exception:
                pass

        threading.Thread(target=worker, daemon=True).start()

    def _filter_apps(self):
        query = self.search_entry.get().lower().strip()
        if not query:
            self.filtered_apps = self.apps
        else:
            self.filtered_apps = [a for a in self.apps if query in a["name"].lower() or query in str(a["pid"])]

        # Update stats
        high_impact = sum(1 for a in self.apps if a["impact"] == "Yüksek")
        self.lbl_app_count.configure(text=f"{len(self.apps)} Uygulama")
        self.lbl_app_impact.configure(text=f"{high_impact} yüksek bellek tüketimi")

        # Render rows
        for w in self.list_scroll.winfo_children():
            w.destroy()

        for a in self.filtered_apps[:80]:
            row = ctk.CTkFrame(self.list_scroll, fg_color=CCleanerTheme.DARK_BG_CARD, height=44, corner_radius=8, border_width=1, border_color=CCleanerTheme.DARK_BORDER)
            row.pack(fill="x", pady=3)
            row.grid_propagate(True)

            # Name & PID
            name_text = f"{a['name']}  (PID: {a['pid']})"
            lbl_name = ctk.CTkLabel(row, text=name_text, font=ctk.CTkFont(size=12, weight="bold"), text_color=CCleanerTheme.DARK_TEXT_PRIMARY)
            ctk.table_cell(lbl_name, 0.03)

            # RAM MB
            lbl_ram = ctk.CTkLabel(row, text=f"{a['memory_mb']} MB", font=ctk.CTkFont(size=12), text_color="#38bdf8")
            ctk.table_cell(lbl_ram, 0.45)

            # Impact badge
            lbl_impact = ctk.CTkLabel(
                row, 
                text=f"● {a['impact']}", 
                font=ctk.CTkFont(size=12, weight="bold"), 
                text_color=a['impact_color']
            )
            ctk.table_cell(lbl_impact, 0.62)

            # Actions
            btn_frame = ctk.CTkFrame(row, fg_color="transparent")
            ctk.table_cell(btn_frame, 0.82)

            if not a["is_sleeping"]:
                btn_sleep = ctk.CTkButton(
                    btn_frame,
                    text="💤 Uyut",
                    width=65,
                    height=28,
                    font=ctk.CTkFont(size=11),
                    fg_color=CCleanerTheme.BG_INPUT,
                    hover_color=CCleanerTheme.BG_CARD_HOVER,
                    corner_radius=14,
                    command=lambda pid=a["pid"]: self._toggle_sleep(pid, True)
                )
                btn_sleep.pack(fill="x", padx=3, pady=3)
            else:
                btn_wake = ctk.CTkButton(
                    btn_frame,
                    text="⚡ Uyandır",
                    width=65,
                    height=28,
                    font=ctk.CTkFont(size=11),
                    fg_color=CCleanerTheme.SUCCESS,
                    hover_color=CCleanerTheme.SUCCESS_HOVER,
                    corner_radius=14,
                    command=lambda pid=a["pid"]: self._toggle_sleep(pid, False)
                )
                btn_wake.pack(fill="x", padx=3, pady=3)

            btn_kill = ctk.CTkButton(
                btn_frame,
                text="✕ Sonlandır",
                width=78,
                height=28,
                font=ctk.CTkFont(size=11),
                fg_color="#7f1d1d",
                hover_color="#991b1b",
                corner_radius=14,
                command=lambda pid=a["pid"]: self._terminate_app(pid)
            )
            btn_kill.pack(fill="x", padx=3, pady=3)

    def _toggle_sleep(self, pid, suspend=True):
        if suspend:
            self.optimizer.suspend_process(pid)
        else:
            self.optimizer.resume_process(pid)
        self._refresh_data()

    def _terminate_app(self, pid):
        self.optimizer.terminate_process(pid)
        self.after(300, self._refresh_data)

    def _boost_memory(self):
        self.btn_boost_ram.configure(text="Temizleniyor...", state="disabled")
        def worker():
            res = self.optimizer.optimize_memory()
            self.after(0, lambda: self._show_boost_result(res))
        threading.Thread(target=worker, daemon=True).start()

    def _show_boost_result(self, res):
        self.btn_boost_ram.configure(text="RAM'i Rahatlat", state="normal")
        self._refresh_data()
