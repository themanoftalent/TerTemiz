from ui import widgets as ctk
import threading
import time
import os
from core.registry import RegistryScanner
from ui.theme import CCleanerTheme

class RegistryView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.scanner = RegistryScanner()
        self.issues = []
        self.issue_checkboxes = []
        self.category_vars = {}
        self.is_scanning = False

        self._build_ui()

    def _build_ui(self):
        self.columnconfigure(0, weight=0, minsize=270)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        # LEFT PANE (Categories & Action)
        left_pane = ctk.CTkFrame(self, fg_color=CCleanerTheme.DARK_BG_SIDEBAR, corner_radius=12, border_width=1, border_color=CCleanerTheme.DARK_BORDER)
        left_pane.grid(row=0, column=0, sticky="nsew", padx=(15, 10), pady=15)
        left_pane.rowconfigure(1, weight=1)
        left_pane.columnconfigure(0, weight=1)

        header_lbl = ctk.CTkLabel(
            left_pane,
            text="Kayıt Defteri Temizliği",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=CCleanerTheme.PRIMARY_LIGHT
        )
        header_lbl.grid(row=0, column=0, sticky="w", padx=15, pady=(15, 8))

        scroll_cats = ctk.CTkScrollableFrame(left_pane, fg_color="transparent")
        scroll_cats.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)

        categories = [
            ("app_paths", "Uygulama Yolları (App Paths)"),
            ("shared_dlls", "Eksik Paylaşılan DLL'ler"),
            ("startup_entries", "Başlangıç Programları Hataları"),
            ("mui_cache", "MUI Önbelleği Kalıntıları"),
            ("fonts", "Eksik Font Tanımlamaları"),
            ("file_exts", "Kullanılmayan Dosya Uzantıları")
        ]

        for cid, cname in categories:
            var = ctk.BooleanVar(value=True)
            cb = ctk.CTkCheckBox(
                scroll_cats,
                text=cname,
                variable=var,
                font=ctk.CTkFont(size=12),
                fg_color=CCleanerTheme.PRIMARY,
                hover_color=CCleanerTheme.PRIMARY_HOVER,
                corner_radius=4
            )
            cb.pack(anchor="w", pady=4, padx=5)
            self.category_vars[cid] = var

        # Bottom buttons
        btn_box = ctk.CTkFrame(left_pane, fg_color="transparent")
        btn_box.grid(row=2, column=0, sticky="ew", padx=12, pady=15)

        self.btn_scan = ctk.CTkButton(
            btn_box,
            text="Sorunları Tara",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=CCleanerTheme.BG_INPUT,
            hover_color=CCleanerTheme.BG_CARD_HOVER,
            corner_radius=18,
            height=38,
            command=self._start_scan
        )
        self.btn_scan.pack(fill="x", pady=(0, 8))

        self.btn_fix = ctk.CTkButton(
            btn_box,
            text="Seçili Sorunları İncele",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=CCleanerTheme.PRIMARY,
            hover_color=CCleanerTheme.PRIMARY_HOVER,
            corner_radius=18,
            height=38,
            state="disabled",
            command=self._prompt_fix_issues
        )
        self.btn_fix.pack(fill="x")

        # RIGHT PANE (Results table)
        right_pane = ctk.CTkFrame(self, fg_color=CCleanerTheme.DARK_BG_CARD, corner_radius=12, border_width=1, border_color=CCleanerTheme.DARK_BORDER)
        right_pane.grid(row=0, column=1, sticky="nsew", padx=(0, 15), pady=15)
        right_pane.rowconfigure(2, weight=1)
        right_pane.columnconfigure(0, weight=1)

        # Status card
        self.status_card = ctk.CTkFrame(right_pane, fg_color=CCleanerTheme.DARK_BG_MAIN, corner_radius=8)
        self.status_card.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 8), ipady=6)

        self.lbl_status = ctk.CTkLabel(
            self.status_card,
            text="Kayıt Defteri Taraması için Hazır",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=CCleanerTheme.DARK_TEXT_PRIMARY
        )
        self.lbl_status.pack(anchor="w", padx=15, pady=(4, 2))

        self.lbl_substatus = ctk.CTkLabel(
            self.status_card,
            text="Kayıt Defterinizdeki geçersiz, yetim ve artık kayıtları tespit etmek için 'Sorunları Tara'ya basın.",
            font=ctk.CTkFont(size=12),
            text_color=CCleanerTheme.DARK_TEXT_SECONDARY
        )
        self.lbl_substatus.pack(anchor="w", padx=15, pady=(0, 4))

        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(right_pane, height=8, corner_radius=4, progress_color=CCleanerTheme.PRIMARY)
        self.progress_bar.grid(row=1, column=0, sticky="ew", padx=15, pady=4)
        self.progress_bar.set(0.0)

        # Issues scroll area
        self.issues_scroll = ctk.CTkScrollableFrame(right_pane, fg_color="transparent")
        self.issues_scroll.grid(row=2, column=0, sticky="nsew", padx=15, pady=(8, 15))

        self._show_placeholder()

    def _show_placeholder(self):
        for w in self.issues_scroll.winfo_children():
            w.destroy()

        ph = ctk.CTkFrame(self.issues_scroll, fg_color="transparent")
        ph.pack(expand=True, pady=80)

        ctk.CTkLabel(ph, text="📑", font=ctk.CTkFont(size=48)).pack(pady=10)
        ctk.CTkLabel(ph, text="Kayıt Defteri Sorunları Taranmadı", font=ctk.CTkFont(size=15, weight="bold"), text_color=CCleanerTheme.DARK_TEXT_PRIMARY).pack(pady=4)
        ctk.CTkLabel(ph, text="Taramayı başlatmak için sol alt kısımdaki butona tıklayın.", font=ctk.CTkFont(size=12), text_color=CCleanerTheme.DARK_TEXT_SECONDARY).pack()

    def _start_scan(self):
        if self.is_scanning:
            return
        self.is_scanning = True
        self.btn_scan.configure(state="disabled")
        self.btn_fix.configure(state="disabled")
        self.progress_bar.set(0.0)

        selected_cats = [cid for cid, v in self.category_vars.items() if v.get()]

        def worker():
            def on_prog(name, cur, total):
                pct = cur / max(1, total)
                self.after(0, lambda: self.progress_bar.set(pct))
                self.after(0, lambda: self.lbl_substatus.configure(text=f"Taranıyor: {name} ({cur}/{total})"))

            issues = self.scanner.scan(categories=selected_cats, on_progress=on_prog)
            time.sleep(0.3)
            self.issues = issues
            self.is_scanning = False
            self.after(0, self._render_issues)

        threading.Thread(target=worker, daemon=True).start()

    def _render_issues(self):
        self.btn_scan.configure(state="normal")
        self.progress_bar.set(1.0)

        for w in self.issues_scroll.winfo_children():
            w.destroy()

        if not self.issues:
            self.lbl_status.configure(text="Tebrikler! Hiçbir Kayıt Defteri Sorunu Bulunamadı. ✅")
            self.lbl_substatus.configure(text="Kayıt defteriniz temiz ve optimize durumda.")
            self.btn_fix.configure(state="disabled")
            return

        self.lbl_status.configure(text=f"Tarama Tamamlandı: {len(self.issues)} Sorun Bulundu! ⚠️")
        self.lbl_substatus.configure(text="Sorunları güvenle onarmak için 'Seçili Sorunları İncele' butonuna tıklayın.")
        self.btn_fix.configure(state="normal")

        # Table header inside scroll
        th = ctk.CTkFrame(self.issues_scroll, fg_color=CCleanerTheme.DARK_BG_SIDEBAR, height=32, corner_radius=6)
        th.pack(fill="x", pady=(0, 4))
        th.grid_propagate(True)

        ctk.table_cell(ctk.CTkLabel(th, text="Sorun Açıklaması", font=ctk.CTkFont(size=11, weight="bold"), text_color=CCleanerTheme.DARK_TEXT_SECONDARY), 0.04)
        ctk.table_cell(ctk.CTkLabel(th, text="Veri / Dosya Yolu", font=ctk.CTkFont(size=11, weight="bold"), text_color=CCleanerTheme.DARK_TEXT_SECONDARY), 0.45)
        ctk.table_cell(ctk.CTkLabel(th, text="Kayıt Anahtarı", font=ctk.CTkFont(size=11, weight="bold"), text_color=CCleanerTheme.DARK_TEXT_SECONDARY), 0.76)

        self.issue_checkboxes = []
        for iss in self.issues:
            row = ctk.CTkFrame(self.issues_scroll, fg_color=CCleanerTheme.DARK_BG_MAIN, height=42, corner_radius=6, border_width=1, border_color=CCleanerTheme.DARK_BORDER)
            row.pack(fill="x", pady=2)
            row.grid_propagate(True)

            var = ctk.BooleanVar(value=True)
            cb = ctk.CTkCheckBox(row, text="", variable=var, width=20, fg_color=CCleanerTheme.PRIMARY, corner_radius=4)
            ctk.table_cell(cb, 0.015)

            def on_toggle(v=var, issue=iss):
                issue.selected = v.get()
            cb.configure(command=on_toggle)
            self.issue_checkboxes.append(var)

            # Problem
            p_text = f"[{iss.category}] {iss.problem}"
            lbl_prob = ctk.CTkLabel(row, text=p_text, font=ctk.CTkFont(size=11, weight="bold"), text_color=CCleanerTheme.DARK_TEXT_PRIMARY)
            ctk.table_cell(lbl_prob, 0.06)

            # Data
            d_text = str(iss.data)
            lbl_data = ctk.CTkLabel(row, text=d_text, font=ctk.CTkFont(size=11), text_color="#38bdf8")
            ctk.table_cell(lbl_data, 0.45)

            # Key
            k_text = iss.key_path
            if len(k_text) > 30:
                k_text = "..." + k_text[-28:]
            lbl_k = ctk.CTkLabel(row, text=k_text, font=ctk.CTkFont(size=10), text_color=CCleanerTheme.DARK_TEXT_MUTED)
            ctk.table_cell(lbl_k, 0.76)

    def _prompt_fix_issues(self):
        # Classic CCleaner backup prompt modal
        dialog = ctk.CTkToplevel(self)
        dialog.title("Kayıt Defteri Yedekleme - TerTemiz")
        dialog.geometry("480x230")
        dialog.resizable(False, False)
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="📑", font=ctk.CTkFont(size=36)).pack(pady=(20, 5))
        ctk.CTkLabel(
            dialog,
            text="Değişiklik yapmadan önce kayıt defterini yedeklemek istiyor musunuz?",
            font=ctk.CTkFont(size=14, weight="bold"),
            justify="center"
        ).pack(pady=5)
        ctk.CTkLabel(
            dialog,
            text="Güvenlik amacıyla, kaldırılacak girdilerin .reg formatında bir yedeği\nBelgeler klasörünüze kaydedilecektir.",
            font=ctk.CTkFont(size=12),
            text_color=CCleanerTheme.DARK_TEXT_SECONDARY,
            justify="center"
        ).pack(pady=(0, 15))

        btn_box = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_box.pack(pady=10)

        def on_backup_and_fix():
            backup_file = self.scanner.export_backup()
            dialog.destroy()
            self._do_fix(backup_file)

        def on_fix_without_backup():
            dialog.destroy()
            self._do_fix(None)

        btn_yes = ctk.CTkButton(btn_box, text="Evet (Yedekle & Düzelt)", fg_color=CCleanerTheme.PRIMARY, hover_color=CCleanerTheme.PRIMARY_HOVER, corner_radius=18, width=170, command=on_backup_and_fix)
        btn_yes.pack(side="left", padx=6)

        btn_no = ctk.CTkButton(btn_box, text="Hayır (Yedeklemeden)", fg_color=CCleanerTheme.BG_INPUT, hover_color=CCleanerTheme.BG_CARD_HOVER, corner_radius=18, width=150, command=on_fix_without_backup)
        btn_no.pack(side="left", padx=6)

        btn_cancel = ctk.CTkButton(btn_box, text="İptal", fg_color="transparent", border_width=1, border_color="#4b5563", hover_color="#374151", corner_radius=18, width=80, command=dialog.destroy)
        btn_cancel.pack(side="left", padx=6)

    def _do_fix(self, backup_file):
        fixed_count = self.scanner.fix_issues()
        self.btn_fix.configure(state="disabled")

        for w in self.issues_scroll.winfo_children():
            w.destroy()

        card = ctk.CTkFrame(self.issues_scroll, fg_color=CCleanerTheme.DARK_BG_MAIN, corner_radius=12, border_width=1, border_color=CCleanerTheme.DARK_BORDER)
        card.pack(fill="both", expand=True, padx=15, pady=25)

        ctk.CTkLabel(card, text="✅", font=ctk.CTkFont(size=48)).pack(pady=(25, 5))
        ctk.CTkLabel(card, text=f"{fixed_count} Kayıt Defteri Sorunu Başarıyla Düzeltildi!", font=ctk.CTkFont(size=18, weight="bold"), text_color=CCleanerTheme.SUCCESS).pack(pady=5)

        msg = "Artık girdiler ve eksik yollar sistemden güvenle temizlendi."
        if backup_file:
            msg += f"\n\n📁 Yedek Dosyası Kaydedildi:\n{backup_file}"
        ctk.CTkLabel(card, text=msg, font=ctk.CTkFont(size=12), text_color=CCleanerTheme.DARK_TEXT_SECONDARY, justify="center").pack(pady=(0, 25))
        self.lbl_status.configure(text="Tüm Sorunlar Onarıldı! ✅")
        self.lbl_substatus.configure(text=f"{fixed_count} sorun başarıyla çözüldü.")
