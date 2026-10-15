import customtkinter as ctk
import threading
import time
from core.cleaner import SystemCleaner, build_default_rules
from core.system_info import format_size
from ui.theme import CCleanerTheme

class CustomCleanView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.cleaner = SystemCleaner()
        self.rules = build_default_rules()
        self.checkboxes = {}
        self.scan_data = None
        self.is_running = False

        self._build_ui()

    def _build_ui(self):
        # 2-column layout: left pane (checkboxes), right pane (results and action)
        self.columnconfigure(0, weight=0, minsize=290)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        # LEFT PANE
        left_pane = ctk.CTkFrame(self, fg_color=CCleanerTheme.DARK_BG_SIDEBAR, corner_radius=12, border_width=1, border_color=CCleanerTheme.DARK_BORDER)
        left_pane.grid(row=0, column=0, sticky="nsew", padx=(15, 10), pady=15)
        left_pane.rowconfigure(1, weight=1)
        left_pane.columnconfigure(0, weight=1)

        # Tabs for Windows / Applications
        self.tabview = ctk.CTkTabview(
            left_pane,
            fg_color=CCleanerTheme.BG_CARD,
            segmented_button_selected_color=CCleanerTheme.PRIMARY,
            segmented_button_selected_hover_color=CCleanerTheme.PRIMARY_HOVER,
            segmented_button_unselected_color=CCleanerTheme.BG_INPUT,
            segmented_button_unselected_hover_color=CCleanerTheme.BG_CARD_HOVER,
            text_color=CCleanerTheme.TEXT_PRIMARY,
            corner_radius=8
        )
        self.tabview.grid(row=0, column=0, sticky="ew", padx=10, pady=(5, 5))
        self.tab_win = self.tabview.add("Windows")
        self.tab_apps = self.tabview.add("Uygulamalar")

        # Scrollable area for rules
        self.scroll_win = ctk.CTkScrollableFrame(left_pane, fg_color="transparent")
        self.scroll_win.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        self.scroll_apps = ctk.CTkScrollableFrame(left_pane, fg_color="transparent")
        # will show depending on tab

        # Populate rules
        self._populate_rules_ui()

        # Switch tabs handler
        def tab_changed():
            curr = self.tabview.get()
            if curr == "Windows":
                self.scroll_apps.grid_forget()
                self.scroll_win.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
            else:
                self.scroll_win.grid_forget()
                self.scroll_apps.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        self.tabview.configure(command=tab_changed)

        # Left bottom buttons
        left_btn_frame = ctk.CTkFrame(left_pane, fg_color="transparent")
        left_btn_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=12)

        self.btn_analyze = ctk.CTkButton(
            left_btn_frame,
            text="Analiz Et",
            font=ctk.CTkFont(family=CCleanerTheme.FONT_FAMILY, size=13, weight="bold"),
            fg_color=CCleanerTheme.BG_INPUT,
            hover_color=CCleanerTheme.BG_CARD_HOVER,
            text_color=CCleanerTheme.TEXT_PRIMARY,
            corner_radius=18,
            height=38,
            command=self._start_analyze
        )
        self.btn_analyze.pack(side="left", fill="x", expand=True, padx=(0, 5))

        self.btn_run_clean = ctk.CTkButton(
            left_btn_frame,
            text="Temizliğe Başla",
            font=ctk.CTkFont(family=CCleanerTheme.FONT_FAMILY, size=13, weight="bold"),
            fg_color=CCleanerTheme.PRIMARY,
            hover_color=CCleanerTheme.PRIMARY_HOVER,
            corner_radius=18,
            height=38,
            command=self._prompt_run_clean
        )
        self.btn_run_clean.pack(side="right", fill="x", expand=True, padx=(5, 0))

        # RIGHT PANE (Results & details)
        right_pane = ctk.CTkFrame(self, fg_color=CCleanerTheme.DARK_BG_CARD, corner_radius=12, border_width=1, border_color=CCleanerTheme.DARK_BORDER)
        right_pane.grid(row=0, column=1, sticky="nsew", padx=(0, 15), pady=15)
        right_pane.rowconfigure(2, weight=1)
        right_pane.columnconfigure(0, weight=1)

        # Header status bar
        self.header_status_card = ctk.CTkFrame(right_pane, fg_color=CCleanerTheme.DARK_BG_MAIN, corner_radius=8)
        self.header_status_card.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 8), ipady=6)

        self.status_title = ctk.CTkLabel(
            self.header_status_card,
            text="Temizleme için hazır",
            font=ctk.CTkFont(family=CCleanerTheme.FONT_FAMILY, size=16, weight="bold"),
            text_color=CCleanerTheme.DARK_TEXT_PRIMARY
        )
        self.status_title.pack(anchor="w", padx=15, pady=(4, 2))

        self.status_sub = ctk.CTkLabel(
            self.header_status_card,
            text="Özel temizlik yapmak için kuralları seçin ve 'Analiz Et' butonuna tıklayın.",
            font=ctk.CTkFont(family=CCleanerTheme.FONT_FAMILY, size=12),
            text_color=CCleanerTheme.DARK_TEXT_SECONDARY
        )
        self.status_sub.pack(anchor="w", padx=15, pady=(0, 4))

        # Progress bar
        self.progress_frame = ctk.CTkFrame(right_pane, fg_color="transparent")
        self.progress_frame.grid(row=1, column=0, sticky="ew", padx=15, pady=4)

        self.clean_progress = ctk.CTkProgressBar(self.progress_frame, height=8, corner_radius=4, progress_color=CCleanerTheme.PRIMARY)
        self.clean_progress.pack(fill="x", pady=2)
        self.clean_progress.set(0.0)

        self.progress_label = ctk.CTkLabel(self.progress_frame, text="", font=ctk.CTkFont(size=11), text_color=CCleanerTheme.DARK_TEXT_MUTED)
        self.progress_label.pack(anchor="w", pady=(2, 0))

        # Results table list
        self.results_scroll = ctk.CTkScrollableFrame(right_pane, fg_color="transparent")
        self.results_scroll.grid(row=2, column=0, sticky="nsew", padx=15, pady=(8, 15))

        self._show_empty_placeholder()

    def _populate_rules_ui(self):
        # Group rules by category
        win_rules = [r for r in self.rules if r.group == "windows"]
        app_rules = [r for r in self.rules if r.group == "applications"]

        self._render_category_rules(win_rules, self.scroll_win)
        self._render_category_rules(app_rules, self.scroll_apps)

    def _render_category_rules(self, rules, parent_scroll):
        cats = {}
        for r in rules:
            cats.setdefault(r.category, []).append(r)

        for cat_name, cat_rules in cats.items():
            cat_header = ctk.CTkLabel(
                parent_scroll,
                text=cat_name,
                font=ctk.CTkFont(family=CCleanerTheme.FONT_FAMILY, size=12, weight="bold"),
                text_color=CCleanerTheme.PRIMARY_LIGHT
            )
            cat_header.pack(anchor="w", padx=5, pady=(10, 3))

            for r in cat_rules:
                var = ctk.BooleanVar(value=r.enabled)
                cb = ctk.CTkCheckBox(
                    parent_scroll,
                    text=r.name,
                    variable=var,
                    font=ctk.CTkFont(family=CCleanerTheme.FONT_FAMILY, size=12),
                    text_color=CCleanerTheme.DARK_TEXT_PRIMARY,
                    fg_color=CCleanerTheme.PRIMARY,
                    hover_color=CCleanerTheme.PRIMARY_HOVER,
                    corner_radius=4
                )
                cb.pack(anchor="w", padx=15, pady=2)
                self.checkboxes[r.rule_id] = var

    def _show_empty_placeholder(self):
        for w in self.results_scroll.winfo_children():
            w.destroy()

        ph = ctk.CTkFrame(self.results_scroll, fg_color="transparent")
        ph.pack(expand=True, pady=80)

        ctk.CTkLabel(ph, text="🧹", font=ctk.CTkFont(size=48)).pack(pady=10)
        ctk.CTkLabel(
            ph, 
            text="Analiz sonuçları burada listelenecektir", 
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=CCleanerTheme.DARK_TEXT_PRIMARY
        ).pack(pady=4)
        ctk.CTkLabel(
            ph,
            text="Sol taraftan temizlemek istediğiniz kategorileri seçin ve 'Analiz Et' butonuna tıklayın.",
            font=ctk.CTkFont(size=12),
            text_color=CCleanerTheme.DARK_TEXT_SECONDARY
        ).pack()

    def _start_analyze(self):
        if self.is_running:
            return
        self.is_running = True
        self.btn_analyze.configure(state="disabled")
        self.btn_run_clean.configure(state="disabled")
        self.clean_progress.set(0.0)

        selected_ids = [rid for rid, var in self.checkboxes.items() if var.get()]

        def worker():
            def on_prog(name, cur, total):
                pct = cur / max(1, total)
                self.after(0, lambda: self.clean_progress.set(pct))
                self.after(0, lambda: self.progress_label.configure(text=f"Analiz ediliyor: {name} ({cur}/{total})"))

            res = self.cleaner.scan_all(on_progress=on_prog, selected_ids=selected_ids)
            time.sleep(0.3)
            self.scan_data = res
            self.is_running = False
            self.after(0, self._render_analysis_results)

        threading.Thread(target=worker, daemon=True).start()

    def _render_analysis_results(self):
        self.btn_analyze.configure(state="normal")
        self.btn_run_clean.configure(state="normal")
        self.clean_progress.set(1.0)
        self.progress_label.configure(text="Analiz tamamlandı.")

        total_sz = format_size(self.scan_data["total_size"])
        total_items = self.scan_data["total_items"]

        self.status_title.configure(text=f"Analiz Tamamlandı: {total_sz} kaldırılabilir dosya ({total_items} Öğe)")
        self.status_sub.configure(text="Seçilen gereksiz dosyaları sisteminizden kalıcı olarak silmek için 'Temizliğe Başla' butonuna tıklayın.")

        # Clear scroll
        for w in self.results_scroll.winfo_children():
            w.destroy()

        if total_items == 0:
            lbl = ctk.CTkLabel(self.results_scroll, text="Seçilen kategorilerde temizlenecek dosya bulunamadı. Sisteminiz temiz!", font=ctk.CTkFont(size=14), text_color=CCleanerTheme.SUCCESS)
            lbl.pack(pady=40)
            return

        for r in self.scan_data["results"]:
            if r["count"] == 0:
                continue

            card = ctk.CTkFrame(self.results_scroll, fg_color=CCleanerTheme.DARK_BG_MAIN, corner_radius=8, border_width=1, border_color=CCleanerTheme.DARK_BORDER)
            card.pack(fill="x", pady=4, padx=5)

            top_row = ctk.CTkFrame(card, fg_color="transparent")
            top_row.pack(fill="x", padx=12, pady=8)

            c_name = ctk.CTkLabel(top_row, text=f"[{r['category']}] {r['name']}", font=ctk.CTkFont(size=13, weight="bold"), text_color=CCleanerTheme.DARK_TEXT_PRIMARY)
            c_name.pack(side="left")

            sz_lbl = ctk.CTkLabel(top_row, text=format_size(r["size"]), font=ctk.CTkFont(size=13, weight="bold"), text_color=CCleanerTheme.PRIMARY)
            sz_lbl.pack(side="right")

            cnt_lbl = ctk.CTkLabel(top_row, text=f"{r['count']} dosya   ", font=ctk.CTkFont(size=12), text_color=CCleanerTheme.DARK_TEXT_SECONDARY)
            cnt_lbl.pack(side="right")

            # Preview snippet if available
            if r["items"]:
                preview_text = r["items"][0][0]
                if len(preview_text) > 85:
                    preview_text = preview_text[:40] + "..." + preview_text[-42:]
                p_lbl = ctk.CTkLabel(card, text=f"Örnek: {preview_text}", font=ctk.CTkFont(size=11), text_color=CCleanerTheme.DARK_TEXT_MUTED, anchor="w")
                p_lbl.pack(fill="x", padx=12, pady=(0, 6))

    def _prompt_run_clean(self):
        if not self.scan_data or self.scan_data["total_items"] == 0:
            self._start_analyze()
            return

        # Simple confirmation dialog
        dialog = ctk.CTkToplevel(self)
        dialog.title("Temizliği Onayla - TerTemiz")
        dialog.geometry("440x210")
        dialog.resizable(False, False)
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()

        lbl_icon = ctk.CTkLabel(dialog, text="⚠️", font=ctk.CTkFont(size=32))
        lbl_icon.pack(pady=(20, 5))

        lbl_msg = ctk.CTkLabel(
            dialog,
            text=f"Seçilen {format_size(self.scan_data['total_size'])} boyutundaki gereksiz dosyalar\nkalıcı olarak silinecektir.\nDevam etmek istiyor musunuz?",
            font=ctk.CTkFont(family=CCleanerTheme.FONT_FAMILY, size=13),
            justify="center"
        )
        lbl_msg.pack(pady=10)

        btn_box = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_box.pack(pady=15)

        def do_clean():
            dialog.destroy()
            self._execute_clean()

        btn_yes = ctk.CTkButton(btn_box, text="Evet, Temizle", fg_color=CCleanerTheme.PRIMARY, hover_color=CCleanerTheme.PRIMARY_HOVER, corner_radius=18, width=120, command=do_clean)
        btn_yes.pack(side="left", padx=8)

        btn_no = ctk.CTkButton(btn_box, text="İptal", fg_color="#374151", hover_color="#4b5563", corner_radius=18, width=100, command=dialog.destroy)
        btn_no.pack(side="left", padx=8)

    def _execute_clean(self):
        self.is_running = True
        self.btn_analyze.configure(state="disabled")
        self.btn_run_clean.configure(state="disabled")

        selected_ids = [rid for rid, var in self.checkboxes.items() if var.get()]

        def worker():
            def on_prog(name, cur, total):
                pct = cur / max(1, total)
                self.after(0, lambda: self.clean_progress.set(pct))
                self.after(0, lambda: self.progress_label.configure(text=f"Temizleniyor: {name} ({cur}/{total})"))

            res = self.cleaner.clean_selected(selected_ids, on_progress=on_prog)
            time.sleep(0.4)
            self.is_running = False
            self.after(0, lambda: self._show_cleaned_results(res))

        threading.Thread(target=worker, daemon=True).start()

    def _show_cleaned_results(self, res):
        self.btn_analyze.configure(state="normal")
        self.btn_run_clean.configure(state="normal")
        self.clean_progress.set(1.0)
        self.progress_label.configure(text="Temizleme tamamlandı!")

        freed_str = format_size(res["total_freed"])
        self.status_title.configure(text=f"Temizleme Tamamlandı: {freed_str} Alan Açıldı! 🎉")
        self.status_sub.configure(text="Seçilen gereksiz dosyalar başarıyla temizlendi.")

        for w in self.results_scroll.winfo_children():
            w.destroy()

        card = ctk.CTkFrame(self.results_scroll, fg_color=CCleanerTheme.DARK_BG_MAIN, corner_radius=10, border_width=1, border_color=CCleanerTheme.DARK_BORDER)
        card.pack(fill="both", expand=True, padx=10, pady=20)

        ctk.CTkLabel(card, text="✅", font=ctk.CTkFont(size=44)).pack(pady=(25, 5))
        ctk.CTkLabel(card, text=f"{freed_str} Boşaltıldı", font=ctk.CTkFont(size=20, weight="bold"), text_color=CCleanerTheme.SUCCESS).pack(pady=5)
        ctk.CTkLabel(card, text="Windows ve uygulama önbellekleri tertemiz hale getirildi.", font=ctk.CTkFont(size=12), text_color=CCleanerTheme.DARK_TEXT_SECONDARY).pack(pady=(0, 20))
