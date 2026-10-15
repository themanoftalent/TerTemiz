import customtkinter as ctk
import os
import subprocess
import threading
from core.tools import UninstallManager, StartupManager, DiskAnalyzer, DuplicateFinder
from core.system_info import get_system_summary, format_size
from ui.theme import CCleanerTheme

class ToolsView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.uninstall_mgr = UninstallManager()
        self.startup_mgr = StartupManager()
        self.disk_analyzer = DiskAnalyzer()
        self.dup_finder = DuplicateFinder()

        self._build_ui()

    def _build_ui(self):
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=15)

        # Segmented top bar for tools
        self.tool_tabs = ctk.CTkTabview(
            container,
            fg_color=CCleanerTheme.BG_CARD,
            segmented_button_selected_color=CCleanerTheme.PRIMARY,
            segmented_button_selected_hover_color=CCleanerTheme.PRIMARY_HOVER,
            segmented_button_unselected_color=CCleanerTheme.BG_INPUT,
            segmented_button_unselected_hover_color=CCleanerTheme.BG_CARD_HOVER,
            text_color=CCleanerTheme.TEXT_PRIMARY,
            corner_radius=10
        )
        self.tool_tabs.pack(fill="both", expand=True)

        self.tab_uninstall = self.tool_tabs.add("📦 Program Kaldırıcı")
        self.tab_startup = self.tool_tabs.add("🚀 Başlangıç Yöneticisi")
        self.tab_disk = self.tool_tabs.add("📊 Disk Alanı Analizi")
        self.tab_dup = self.tool_tabs.add("🔍 Çift Dosya Bulucu")
        self.tab_sysinfo = self.tool_tabs.add("ℹ️ Sistem Özellikleri")

        # Build each subtool view
        self._build_uninstall_tab()
        self._build_startup_tab()
        self._build_disk_tab()
        self._build_dup_tab()
        self._build_sysinfo_tab()

    # 1. UNINSTALL TAB
    def _build_uninstall_tab(self):
        parent = self.tab_uninstall
        
        # Action bar
        top_bar = ctk.CTkFrame(parent, fg_color="transparent")
        top_bar.pack(fill="x", pady=(5, 10))

        self.uninstall_search = ctk.CTkEntry(
            top_bar,
            placeholder_text="🔍 Program Ara...",
            width=260,
            height=34,
            corner_radius=17,
            fg_color=CCleanerTheme.DARK_BG_INPUT
        )
        self.uninstall_search.pack(side="left")
        self.uninstall_search.bind("<KeyRelease>", lambda e: self._filter_uninstall())

        self.btn_run_uninst = ctk.CTkButton(
            top_bar,
            text="Kaldır (Uninstall)",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=CCleanerTheme.PRIMARY,
            hover_color=CCleanerTheme.PRIMARY_HOVER,
            corner_radius=17,
            height=34,
            width=130,
            command=self._do_uninstall_selected
        )
        self.btn_run_uninst.pack(side="right", padx=(5, 0))

        self.btn_del_entry = ctk.CTkButton(
            top_bar,
            text="Girdiyi Sil",
            font=ctk.CTkFont(size=12),
            fg_color="#374151",
            hover_color="#4b5563",
            corner_radius=17,
            height=34,
            width=110,
            command=self._do_delete_entry
        )
        self.btn_del_entry.pack(side="right")

        # Table header
        th = ctk.CTkFrame(parent, fg_color=CCleanerTheme.DARK_BG_SIDEBAR, height=32, corner_radius=6)
        th.pack(fill="x", pady=(0, 4))
        th.pack_propagate(False)

        ctk.CTkLabel(th, text="Program Adı", font=ctk.CTkFont(size=11, weight="bold"), text_color=CCleanerTheme.DARK_TEXT_SECONDARY).place(relx=0.03, rely=0.5, anchor="w")
        ctk.CTkLabel(th, text="Yayımcı", font=ctk.CTkFont(size=11, weight="bold"), text_color=CCleanerTheme.DARK_TEXT_SECONDARY).place(relx=0.45, rely=0.5, anchor="w")
        ctk.CTkLabel(th, text="Yükleme Tarihi", font=ctk.CTkFont(size=11, weight="bold"), text_color=CCleanerTheme.DARK_TEXT_SECONDARY).place(relx=0.68, rely=0.5, anchor="w")
        ctk.CTkLabel(th, text="Boyut", font=ctk.CTkFont(size=11, weight="bold"), text_color=CCleanerTheme.DARK_TEXT_SECONDARY).place(relx=0.85, rely=0.5, anchor="w")

        self.uninstall_scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        self.uninstall_scroll.pack(fill="both", expand=True)

        self.selected_prog = None
        self.all_progs = []
        self._load_uninstall_data()

    def _load_uninstall_data(self):
        def worker():
            progs = self.uninstall_mgr.get_installed_programs()
            self.all_progs = progs
            try:
                self.after(0, self._filter_uninstall)
            except Exception:
                pass
        threading.Thread(target=worker, daemon=True).start()

    def _filter_uninstall(self):
        q = self.uninstall_search.get().lower().strip()
        filtered = [p for p in self.all_progs if not q or q in p["name"].lower() or q in p["publisher"].lower()]

        for w in self.uninstall_scroll.winfo_children():
            w.destroy()

        self.selected_prog = None
        self.prog_rows = []

        for p in filtered:
            row = ctk.CTkFrame(self.uninstall_scroll, fg_color=CCleanerTheme.DARK_BG_CARD, height=40, corner_radius=6, border_width=1, border_color=CCleanerTheme.DARK_BORDER)
            row.pack(fill="x", pady=2)
            row.pack_propagate(False)

            p_name = p["name"]
            if len(p_name) > 38:
                p_name = p_name[:36] + "..."
            lbl_name = ctk.CTkLabel(row, text=p_name, font=ctk.CTkFont(size=12, weight="bold"), text_color=CCleanerTheme.DARK_TEXT_PRIMARY)
            lbl_name.place(relx=0.03, rely=0.5, anchor="w")

            pub = p["publisher"]
            if len(pub) > 22:
                pub = pub[:20] + "..."
            lbl_pub = ctk.CTkLabel(row, text=pub, font=ctk.CTkFont(size=11), text_color=CCleanerTheme.DARK_TEXT_MUTED)
            lbl_pub.place(relx=0.45, rely=0.5, anchor="w")

            lbl_date = ctk.CTkLabel(row, text=p["install_date"], font=ctk.CTkFont(size=11), text_color=CCleanerTheme.DARK_TEXT_MUTED)
            lbl_date.place(relx=0.68, rely=0.5, anchor="w")

            lbl_sz = ctk.CTkLabel(row, text=p["size_str"], font=ctk.CTkFont(size=11), text_color=CCleanerTheme.DARK_TEXT_SECONDARY)
            lbl_sz.place(relx=0.85, rely=0.5, anchor="w")

            def on_click(event, target=p, target_row=row):
                self.selected_prog = target
                for r in self.prog_rows:
                    r.configure(fg_color=CCleanerTheme.DARK_BG_CARD, border_color=CCleanerTheme.DARK_BORDER)
                target_row.configure(fg_color=CCleanerTheme.DARK_BG_CARD_HOVER, border_color=CCleanerTheme.PRIMARY)

            row.bind("<Button-1>", on_click)
            lbl_name.bind("<Button-1>", on_click)
            lbl_pub.bind("<Button-1>", on_click)
            self.prog_rows.append(row)

    def _do_uninstall_selected(self):
        if not self.selected_prog:
            return
        self.uninstall_mgr.run_uninstall(self.selected_prog)

    def _do_delete_entry(self):
        if not self.selected_prog:
            return
        self.uninstall_mgr.delete_registry_entry(self.selected_prog)
        self._load_uninstall_data()

    # 2. STARTUP TAB
    def _build_startup_tab(self):
        parent = self.tab_startup
        
        top_bar = ctk.CTkFrame(parent, fg_color="transparent")
        top_bar.pack(fill="x", pady=(5, 10))

        ctk.CTkLabel(top_bar, text="Windows Başlatıldığında Çalışan Programlar", font=ctk.CTkFont(size=14, weight="bold"), text_color=CCleanerTheme.DARK_TEXT_PRIMARY).pack(side="left")

        btn_del = ctk.CTkButton(
            top_bar,
            text="Girdiyi Sil",
            font=ctk.CTkFont(size=12),
            fg_color="#7f1d1d",
            hover_color="#991b1b",
            corner_radius=16,
            height=32,
            width=100,
            command=self._do_delete_startup
        )
        btn_del.pack(side="right")

        th = ctk.CTkFrame(parent, fg_color=CCleanerTheme.DARK_BG_SIDEBAR, height=32, corner_radius=6)
        th.pack(fill="x", pady=(0, 4))
        th.pack_propagate(False)

        ctk.CTkLabel(th, text="Program / Girdi", font=ctk.CTkFont(size=11, weight="bold"), text_color=CCleanerTheme.DARK_TEXT_SECONDARY).place(relx=0.03, rely=0.5, anchor="w")
        ctk.CTkLabel(th, text="Dosya Komutu", font=ctk.CTkFont(size=11, weight="bold"), text_color=CCleanerTheme.DARK_TEXT_SECONDARY).place(relx=0.35, rely=0.5, anchor="w")
        ctk.CTkLabel(th, text="Konum", font=ctk.CTkFont(size=11, weight="bold"), text_color=CCleanerTheme.DARK_TEXT_SECONDARY).place(relx=0.75, rely=0.5, anchor="w")

        self.startup_scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        self.startup_scroll.pack(fill="both", expand=True)

        self.selected_startup = None
        self._load_startup_data()

    def _load_startup_data(self):
        items = self.startup_mgr.get_startup_items()
        for w in self.startup_scroll.winfo_children():
            w.destroy()

        self.startup_rows = []
        for itm in items:
            row = ctk.CTkFrame(self.startup_scroll, fg_color=CCleanerTheme.DARK_BG_CARD, height=42, corner_radius=6, border_width=1, border_color=CCleanerTheme.DARK_BORDER)
            row.pack(fill="x", pady=2)
            row.pack_propagate(False)

            lbl_name = ctk.CTkLabel(row, text=itm["name"], font=ctk.CTkFont(size=12, weight="bold"), text_color=CCleanerTheme.DARK_TEXT_PRIMARY)
            lbl_name.place(relx=0.03, rely=0.5, anchor="w")

            cmd = itm["command"]
            if len(cmd) > 42:
                cmd = cmd[:20] + "..." + cmd[-20:]
            lbl_cmd = ctk.CTkLabel(row, text=cmd, font=ctk.CTkFont(size=11), text_color=CCleanerTheme.DARK_TEXT_MUTED)
            lbl_cmd.place(relx=0.35, rely=0.5, anchor="w")

            lbl_loc = ctk.CTkLabel(row, text=itm["location"], font=ctk.CTkFont(size=11), text_color="#38bdf8")
            lbl_loc.place(relx=0.75, rely=0.5, anchor="w")

            def on_click(event, target=itm, target_row=row):
                self.selected_startup = target
                for r in self.startup_rows:
                    r.configure(fg_color=CCleanerTheme.DARK_BG_CARD, border_color=CCleanerTheme.DARK_BORDER)
                target_row.configure(fg_color=CCleanerTheme.DARK_BG_CARD_HOVER, border_color=CCleanerTheme.PRIMARY)

            row.bind("<Button-1>", on_click)
            lbl_name.bind("<Button-1>", on_click)
            self.startup_rows.append(row)

    def _do_delete_startup(self):
        if not self.selected_startup:
            return
        self.startup_mgr.delete_startup_item(self.selected_startup)
        self._load_startup_data()

    # 3. DISK ANALYZER TAB
    def _build_disk_tab(self):
        parent = self.tab_disk

        top_bar = ctk.CTkFrame(parent, fg_color="transparent")
        top_bar.pack(fill="x", pady=(5, 10))

        default_dir = os.path.expanduser("~")
        self.entry_disk_path = ctk.CTkEntry(top_bar, width=320, height=34, corner_radius=17, fg_color=CCleanerTheme.DARK_BG_INPUT)
        self.entry_disk_path.insert(0, default_dir)
        self.entry_disk_path.pack(side="left", padx=(0, 10))

        self.btn_scan_disk = ctk.CTkButton(
            top_bar,
            text="Diski Tara",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=CCleanerTheme.PRIMARY,
            hover_color=CCleanerTheme.PRIMARY_HOVER,
            corner_radius=17,
            height=34,
            command=self._start_disk_scan
        )
        self.btn_scan_disk.pack(side="left")

        # Stats cards
        self.disk_stats_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.disk_stats_frame.pack(fill="x", pady=5)

        # Largest files scroll
        ctk.CTkLabel(parent, text="En Çok Alan Kaplayan Dosyalar", font=ctk.CTkFont(size=13, weight="bold"), text_color=CCleanerTheme.DARK_TEXT_PRIMARY).pack(anchor="w", pady=(10, 4))

        self.disk_results_scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        self.disk_results_scroll.pack(fill="both", expand=True)

    def _start_disk_scan(self):
        target = self.entry_disk_path.get().strip()
        if not os.path.exists(target):
            return
        self.btn_scan_disk.configure(state="disabled", text="Taranıyor...")

        def worker():
            res = self.disk_analyzer.scan_path(target)
            self.after(0, lambda: self._render_disk_results(res))
        threading.Thread(target=worker, daemon=True).start()

    def _render_disk_results(self, res):
        self.btn_scan_disk.configure(state="normal", text="Diski Tara")

        for w in self.disk_stats_frame.winfo_children():
            w.destroy()

        # Render category bars
        for cat in res["categories"]:
            if cat["size"] == 0:
                continue
            cf = ctk.CTkFrame(self.disk_stats_frame, fg_color=CCleanerTheme.DARK_BG_CARD, height=28, corner_radius=6)
            cf.pack(fill="x", pady=2)
            cf.pack_propagate(False)

            ctk.CTkLabel(cf, text=cat["name"], font=ctk.CTkFont(size=11, weight="bold"), text_color=CCleanerTheme.DARK_TEXT_PRIMARY).place(relx=0.03, rely=0.5, anchor="w")
            ctk.CTkLabel(cf, text=f"{cat['size_str']}  (%{cat['percent']})", font=ctk.CTkFont(size=11), text_color=CCleanerTheme.PRIMARY).place(relx=0.35, rely=0.5, anchor="w")
            ctk.CTkLabel(cf, text=f"{cat['count']} dosya", font=ctk.CTkFont(size=11), text_color=CCleanerTheme.DARK_TEXT_MUTED).place(relx=0.65, rely=0.5, anchor="w")

        # Render top files
        for w in self.disk_results_scroll.winfo_children():
            w.destroy()

        for f in res["top_files"]:
            row = ctk.CTkFrame(self.disk_results_scroll, fg_color=CCleanerTheme.DARK_BG_CARD, height=38, corner_radius=6, border_width=1, border_color=CCleanerTheme.DARK_BORDER)
            row.pack(fill="x", pady=2)
            row.pack_propagate(False)

            fn = f["filename"]
            if len(fn) > 40:
                fn = fn[:38] + "..."
            ctk.CTkLabel(row, text=fn, font=ctk.CTkFont(size=11, weight="bold"), text_color=CCleanerTheme.DARK_TEXT_PRIMARY).place(relx=0.03, rely=0.5, anchor="w")
            ctk.CTkLabel(row, text=f["size_str"], font=ctk.CTkFont(size=11, weight="bold"), text_color=CCleanerTheme.PRIMARY).place(relx=0.6, rely=0.5, anchor="w")

            btn_open = ctk.CTkButton(
                row,
                text="Klasörü Aç",
                width=80,
                height=24,
                font=ctk.CTkFont(size=10),
                fg_color="#374151",
                hover_color="#4b5563",
                corner_radius=12,
                command=lambda p=f["path"]: subprocess.run(f'explorer /select,"{p}"', shell=True)
            )
            btn_open.place(relx=0.82, rely=0.5, anchor="w")

    # 4. DUPLICATE FINDER TAB
    def _build_dup_tab(self):
        parent = self.tab_dup

        top_bar = ctk.CTkFrame(parent, fg_color="transparent")
        top_bar.pack(fill="x", pady=(5, 10))

        default_dir = os.path.expanduser("~\\Downloads")
        self.entry_dup_path = ctk.CTkEntry(top_bar, width=320, height=34, corner_radius=17, fg_color=CCleanerTheme.DARK_BG_INPUT)
        self.entry_dup_path.insert(0, default_dir)
        self.entry_dup_path.pack(side="left", padx=(0, 10))

        self.btn_scan_dup = ctk.CTkButton(
            top_bar,
            text="Çiftleri Ara",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=CCleanerTheme.PRIMARY,
            hover_color=CCleanerTheme.PRIMARY_HOVER,
            corner_radius=17,
            height=34,
            command=self._start_dup_scan
        )
        self.btn_scan_dup.pack(side="left")

        self.dup_scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        self.dup_scroll.pack(fill="both", expand=True, pady=10)

        ph = ctk.CTkLabel(self.dup_scroll, text="Arama yapmak istediğiniz klasörü seçin ve 'Çiftleri Ara' butonuna tıklayın.", font=ctk.CTkFont(size=12), text_color=CCleanerTheme.DARK_TEXT_SECONDARY)
        ph.pack(pady=40)

    def _start_dup_scan(self):
        p = self.entry_dup_path.get().strip()
        if not os.path.exists(p):
            return
        self.btn_scan_dup.configure(state="disabled", text="Taranıyor...")

        def worker():
            dups = self.dup_finder.find_duplicates(p)
            self.after(0, lambda: self._render_dup_results(dups))
        threading.Thread(target=worker, daemon=True).start()

    def _render_dup_results(self, dups):
        self.btn_scan_dup.configure(state="normal", text="Çiftleri Ara")

        for w in self.dup_scroll.winfo_children():
            w.destroy()

        if not dups:
            ctk.CTkLabel(self.dup_scroll, text="Klasörde aynı boyutta ve içerikte çift dosya bulunamadı.", font=ctk.CTkFont(size=13), text_color=CCleanerTheme.SUCCESS).pack(pady=40)
            return

        for item in dups[:25]:
            box = ctk.CTkFrame(self.dup_scroll, fg_color=CCleanerTheme.DARK_BG_CARD, corner_radius=8, border_width=1, border_color=CCleanerTheme.DARK_BORDER)
            box.pack(fill="x", pady=4, padx=5)

            ctk.CTkLabel(box, text=f"Dosya Boyutu: {item['size_str']}  |  Gereksiz Kaplanan Alan: {item['wasted_str']}", font=ctk.CTkFont(size=11, weight="bold"), text_color=CCleanerTheme.PRIMARY).pack(anchor="w", padx=10, pady=(6, 2))

            for fp in item["paths"]:
                row = ctk.CTkFrame(box, fg_color="transparent")
                row.pack(fill="x", padx=10, pady=2)

                p_str = fp
                if len(p_str) > 65:
                    p_str = p_str[:30] + "..." + p_str[-32:]
                ctk.CTkLabel(row, text=p_str, font=ctk.CTkFont(size=11), text_color=CCleanerTheme.DARK_TEXT_PRIMARY).pack(side="left")

                btn_del = ctk.CTkButton(
                    row,
                    text="Sil",
                    width=45,
                    height=20,
                    font=ctk.CTkFont(size=10),
                    fg_color="#7f1d1d",
                    hover_color="#991b1b",
                    corner_radius=10,
                    command=lambda path=fp, b=box: self._delete_dup_file(path, b)
                )
                btn_del.pack(side="right")

    def _delete_dup_file(self, fp, box):
        try:
            if os.path.exists(fp):
                os.remove(fp)
            box.destroy()
        except Exception:
            pass

    # 5. SYSTEM INFO TAB
    def _build_sysinfo_tab(self):
        parent = self.tab_sysinfo

        info = get_system_summary()

        card = ctk.CTkFrame(parent, fg_color=CCleanerTheme.DARK_BG_CARD, corner_radius=14, border_width=1, border_color=CCleanerTheme.DARK_BORDER)
        card.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(card, text="💻 Donanım ve Sistem Özellikleri", font=ctk.CTkFont(size=18, weight="bold"), text_color=CCleanerTheme.DARK_TEXT_PRIMARY).pack(anchor="w", padx=25, pady=(25, 15))

        specs = [
            ("İşletim Sistemi", info["os"], "🪟"),
            ("İşlemci (CPU)", info["cpu"], "🧠"),
            ("Bellek (RAM)", f"{info['ram']['total']} (Kullanılan: {info['ram']['used']})", "📊"),
            ("Grafik Kartı (GPU)", info["gpu"], "🎮"),
            ("Birincil Disk (C:)", f"{info['disk']['total']} Toplam  •  {info['disk']['free']} Boş Alan (%{info['disk']['percent']} Dolu)", "💾")
        ]

        for title, val, icon in specs:
            row = ctk.CTkFrame(card, fg_color=CCleanerTheme.DARK_BG_MAIN, height=52, corner_radius=8)
            row.pack(fill="x", padx=25, pady=6)
            row.pack_propagate(False)

            ctk.CTkLabel(row, text=f"{icon}  {title}", font=ctk.CTkFont(size=13, weight="bold"), text_color=CCleanerTheme.DARK_TEXT_SECONDARY).place(relx=0.03, rely=0.5, anchor="w")
            ctk.CTkLabel(row, text=val, font=ctk.CTkFont(size=13, weight="bold"), text_color=CCleanerTheme.DARK_TEXT_PRIMARY).place(relx=0.35, rely=0.5, anchor="w")
