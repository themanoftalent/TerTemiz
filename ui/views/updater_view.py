from ui import widgets as ctk
import threading
import time
import webbrowser
from tkinter import messagebox
from ui.i18n import tr
from core.app_updater import AppUpdater
from core.driver_updater import DriverScanner
from ui.theme import CCleanerTheme

class UpdaterView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.app_updater = AppUpdater()
        self.driver_scanner = DriverScanner()

        self.apps = []
        self.drivers = []
        self.selected_driver_category = "Tümü"
        self.is_scanning_apps = False
        self.is_scanning_drivers = False

        self.update_queue = []
        self._batch_mode = False
        self._build_ui()
        self._start_scan_apps()

    def _build_ui(self):
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=15)

        # Tabview for Apps vs Drivers
        self.updater_tabs = ctk.CTkTabview(
            container,
            fg_color=CCleanerTheme.BG_CARD,
            segmented_button_selected_color=CCleanerTheme.PRIMARY,
            segmented_button_selected_hover_color=CCleanerTheme.PRIMARY_HOVER,
            segmented_button_unselected_color=CCleanerTheme.BG_INPUT,
            segmented_button_unselected_hover_color=CCleanerTheme.BG_CARD_HOVER,
            text_color=CCleanerTheme.TEXT_PRIMARY,
            corner_radius=10
        )
        self.updater_tabs.pack(fill="both", expand=True)

        self.tab_apps = self.updater_tabs.add("📦 Uygulama Güncelleyici (Software)")


        self._build_apps_tab()


    # ==========================================
    # 1. SOFTWARE & APPS UPDATER TAB
    # ==========================================
    def _build_apps_tab(self):
        parent = self.tab_apps

        # Top Banner
        header_card = ctk.CTkFrame(
            parent, 
            fg_color=CCleanerTheme.BG_CARD, 
            corner_radius=12, 
            border_width=1, 
            border_color=CCleanerTheme.BORDER
        )
        header_card.pack(fill="x", padx=10, pady=(10, 15), ipady=8)

        icon_lbl = ctk.CTkLabel(header_card, text="📦", font=ctk.CTkFont(size=36))
        icon_lbl.pack(side="top", anchor="w", padx=15)

        txt_box = ctk.CTkFrame(header_card, fg_color="transparent")
        txt_box.pack(side="top", fill="x", padx=15, pady=5)

        self.lbl_app_title = ctk.CTkLabel(
            txt_box, 
            text="Yüklü Uygulama Güncellemeleri Denetleniyor...", 
            font=ctk.CTkFont(size=17, weight="bold"), 
            text_color=CCleanerTheme.TEXT_PRIMARY, 
            anchor="w"
        )
        self.lbl_app_title.pack(anchor="w")

        self.lbl_app_sub = ctk.CTkLabel(
            txt_box, 
            text="Bilgisayarınızdaki programların güncel sürümleri Windows paket havuzundan taranıyor.", 
            font=ctk.CTkFont(size=12), 
            text_color=CCleanerTheme.TEXT_SECONDARY, 
            anchor="w"
        )
        self.lbl_app_sub.pack(anchor="w")

        self.btn_update_all_apps = ctk.CTkButton(
            header_card,
            text="🚀 Tümünü Güncelle",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=CCleanerTheme.PRIMARY,
            hover_color=CCleanerTheme.PRIMARY_HOVER,
            corner_radius=18,
            height=38,
            width=160,
            command=self._update_all_apps
        )
        self.btn_update_all_apps.pack(side="bottom", anchor="e", padx=15, pady=5)

        self.btn_scan_apps = ctk.CTkButton(
            header_card,
            text="🔄 Yeniden Tara",
            font=ctk.CTkFont(size=13),
            fg_color=CCleanerTheme.BG_INPUT,
            hover_color=CCleanerTheme.BG_CARD_HOVER,
            text_color=CCleanerTheme.TEXT_PRIMARY,
            corner_radius=18,
            height=38,
            width=130,
            command=self._start_scan_apps
        )
        self.btn_scan_apps.pack(side="bottom", anchor="e", padx=15, pady=5)

        # Table Header
        th = ctk.CTkFrame(parent, fg_color=CCleanerTheme.BG_INPUT, height=34, corner_radius=6)
        th.pack(fill="x", padx=10, pady=(0, 4))
        th.grid_propagate(True)

        ctk.table_cell(ctk.CTkLabel(th, text="Uygulama Adı / Kimlik", font=ctk.CTkFont(size=11, weight="bold"), text_color=CCleanerTheme.TEXT_SECONDARY), 0.03)
        ctk.table_cell(ctk.CTkLabel(th, text="Kurulu Sürüm", font=ctk.CTkFont(size=11, weight="bold"), text_color=CCleanerTheme.TEXT_SECONDARY), 0.48)
        ctk.table_cell(ctk.CTkLabel(th, text="Yeni Sürüm", font=ctk.CTkFont(size=11, weight="bold"), text_color=CCleanerTheme.TEXT_SECONDARY), 0.64)
        ctk.table_cell(ctk.CTkLabel(th, text="Eylem", font=ctk.CTkFont(size=11, weight="bold"), text_color=CCleanerTheme.TEXT_SECONDARY), 0.84)

        # Scrollable App List
        self.apps_scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        self.apps_scroll.pack(fill="both", expand=True, padx=10, pady=(4, 10))

        self._show_apps_placeholder("Uygulamalar taranıyor...")

    def _show_apps_placeholder(self, text):
        for w in self.apps_scroll.winfo_children():
            w.destroy()
        ph = ctk.CTkLabel(self.apps_scroll, text=text, font=ctk.CTkFont(size=13), text_color=CCleanerTheme.TEXT_SECONDARY)
        ph.pack(pady=50)

    def _start_scan_apps(self):
        if self.is_scanning_apps:
            return
        self.is_scanning_apps = True
        self.btn_scan_apps.configure(state="disabled")
        self.btn_update_all_apps.configure(state="disabled")
        self.lbl_app_title.configure(text="Yüklü Program Güncellemeleri Taranıyor...")
        self._show_apps_placeholder("Windows Paket Yöneticisi (winget) ile güncellemeler denetleniyor...")

        def worker():
            apps = self.app_updater.scan_updates()
            self.apps = apps
            self.is_scanning_apps = False
            try:
                self.after(0, self._render_apps)
            except Exception:
                pass

        threading.Thread(target=worker, daemon=True).start()

    def _render_apps(self):
        self.btn_scan_apps.configure(state="normal")
        self.btn_update_all_apps.configure(state="normal")

        for w in self.apps_scroll.winfo_children():
            w.destroy()

        if self.app_updater.last_error:
            self.lbl_app_title.configure(text="Güncelleme taraması başarısız")
            self.lbl_app_sub.configure(text=self.app_updater.last_error)
            self.btn_update_all_apps.configure(state="disabled")
            self._show_apps_placeholder(self.app_updater.last_error)
            ctk.CTkButton(self.apps_scroll, text="WinGet Kurulumunu Aç",
                          command=lambda: webbrowser.open("ms-windows-store://pdp/?ProductId=9NBLGGH4NNS1")).pack(pady=10)
            return

        if not self.apps:
            self.lbl_app_title.configure(text="Tüm Programlarınız Güncel! 🎉")
            self.lbl_app_sub.configure(text="Sisteminizdeki yazılımlar en son sürümlerinde çalışıyor.")
            self.btn_update_all_apps.configure(state="disabled")

            card = ctk.CTkFrame(self.apps_scroll, fg_color=CCleanerTheme.BG_CARD, corner_radius=12, border_width=1, border_color=CCleanerTheme.BORDER)
            card.pack(fill="both", expand=True, padx=20, pady=30)
            ctk.CTkLabel(card, text="✅", font=ctk.CTkFont(size=48)).pack(pady=(25, 5))
            ctk.CTkLabel(card, text="Harika! Güncelleme Gerektiren Uygulama Yok", font=ctk.CTkFont(size=16, weight="bold"), text_color=CCleanerTheme.SUCCESS).pack(pady=4)
            ctk.CTkLabel(card, text="Tüm yüklü yazılımlar güncel ve güvenlik yamaları tam.", font=ctk.CTkFont(size=12), text_color=CCleanerTheme.TEXT_SECONDARY).pack(pady=(0, 25))
            return

        self.lbl_app_title.configure(text=f"{len(self.apps)} Uygulama Güncellemesi Mevcut! ⚠️")
        self.lbl_app_sub.configure(text="Yeni özellikler ve güvenlik yamaları için uygulamaları doğrudan buradan güncelleyebilirsiniz.")
        self.btn_update_all_apps.configure(state="normal")

        for app in self.apps:
            row = ctk.CTkFrame(
                self.apps_scroll, 
                fg_color=CCleanerTheme.BG_CARD, 
                height=52, 
                corner_radius=8, 
                border_width=1, 
                border_color=CCleanerTheme.BORDER
            )
            row.pack(fill="x", pady=3)
            row.grid_propagate(True)

            # Name and ID
            name_box = ctk.CTkFrame(row, fg_color="transparent")
            ctk.table_cell(name_box, 0.03)

            app_name = app["name"]
            lbl_name = ctk.CTkLabel(
                name_box, 
                text=app_name, 
                font=ctk.CTkFont(size=12, weight="bold"), 
                text_color=CCleanerTheme.TEXT_PRIMARY, 
                anchor="w"
            )
            lbl_name.pack(anchor="w")

            lbl_id = ctk.CTkLabel(
                name_box, 
                text=app["id"], 
                font=ctk.CTkFont(size=10), 
                text_color=CCleanerTheme.TEXT_MUTED, 
                anchor="w"
            )
            lbl_id.pack(anchor="w")

            # Current Version
            lbl_cur = ctk.CTkLabel(
                row, 
                text=app["installed_version"], 
                font=ctk.CTkFont(size=11), 
                text_color=CCleanerTheme.TEXT_SECONDARY
            )
            ctk.table_cell(lbl_cur, 0.48)

            # Available Version
            lbl_new = ctk.CTkLabel(
                row, 
                text=f"➔  {app['available_version']}", 
                font=ctk.CTkFont(size=11, weight="bold"), 
                text_color=CCleanerTheme.PRIMARY
            )
            ctk.table_cell(lbl_new, 0.64)

            # Action button
            if app["status"] == "Güncel":
                lbl_done = ctk.CTkLabel(
                    row, 
                    text="✅ Güncellendi", 
                    font=ctk.CTkFont(size=11, weight="bold"), 
                    text_color=CCleanerTheme.SUCCESS
                )
                ctk.table_cell(lbl_done, 0.84)
            else:
                btn_up = ctk.CTkButton(
                    row,
                    text="🚀 Güncelle",
                    width=95,
                    height=28,
                    font=ctk.CTkFont(size=11, weight="bold"),
                    fg_color=CCleanerTheme.PRIMARY,
                    hover_color=CCleanerTheme.PRIMARY_HOVER,
                    corner_radius=14,
                    command=lambda target=app: self._open_update_modal(target)
                )
                ctk.table_cell(btn_up, 0.84)

    def _open_update_modal(self, app):
        if self.app_updater.is_updating:
            return
        modal = ctk.CTkToplevel(self)
        modal.title(f"Güncelleme: {app['name']}")
        modal.geometry("560x420")
        modal.resizable(True, True)
        modal.minsize(520, 400)
        modal.protocol("WM_DELETE_WINDOW", lambda: None)
        modal.transient(self.winfo_toplevel())
        modal.grab_set()

        # Modal Header
        top_bar = ctk.CTkFrame(modal, fg_color=CCleanerTheme.BG_CARD, height=65, corner_radius=0)
        top_bar.pack(fill="x")
        top_bar.pack_propagate(False)

        ctk.CTkLabel(top_bar, text="📦", font=ctk.CTkFont(size=28)).pack(side="left", padx=15)
        
        t_box = ctk.CTkFrame(top_bar, fg_color="transparent")
        t_box.pack(side="left", fill="y", pady=10)
        
        ctk.CTkLabel(
            t_box, 
            text=f"{app['name']} Güncelleniyor", 
            font=ctk.CTkFont(size=14, weight="bold"), 
            text_color=CCleanerTheme.TEXT_PRIMARY
        ).pack(anchor="w")

        lbl_step = ctk.CTkLabel(
            t_box, 
            text=f"{app['installed_version']}  ➔  {app['available_version']} paketi indiriliyor ve kuruluyor...", 
            font=ctk.CTkFont(size=11), 
            text_color=CCleanerTheme.PRIMARY
        )
        lbl_step.pack(anchor="w")

        # Progress bar
        pbar = ctk.CTkProgressBar(modal, height=8, corner_radius=4, progress_color=CCleanerTheme.PRIMARY)
        pbar.pack(fill="x", padx=20, pady=(15, 10))
        pbar.configure(mode="indeterminate")
        pbar.start()

        # Terminal output log box
        ctk.CTkLabel(
            modal, 
            text="Canlı Kurulum ve İndirme Günlüğü (Live Terminal Log):", 
            font=ctk.CTkFont(size=11, weight="bold"), 
            text_color=CCleanerTheme.TEXT_SECONDARY
        ).pack(anchor="w", padx=20, pady=(5, 2))

        log_box = ctk.CTkTextbox(
            modal, 
            fg_color=("#1e293b", "#0f172a"), 
            text_color="#38bdf8", 
            font=ctk.CTkFont(family="Consolas", size=10),
            corner_radius=8
        )
        log_box.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        # Bottom close button
        btn_close = ctk.CTkButton(
            modal, 
            text="Güncelleme Sürüyor...", 
            state="disabled", 
            fg_color=CCleanerTheme.BG_INPUT,
            corner_radius=16,
            height=34,
            command=modal.destroy
        )
        btn_close.pack(pady=(0, 15))

        def on_log(line):
            def append_line():
                log_box.insert("end", line + "\n")
                log_box.see("end")
            try:
                modal.after(0, append_line)
            except Exception:
                pass

        def on_done(success):
            def finish_ui():
                pbar.stop()
                pbar.configure(mode="determinate")
                pbar.set(1.0)
                if success:
                    lbl_step.configure(text="✅ Güncelleme Başarıyla Tamamlandı!", text_color=CCleanerTheme.SUCCESS)
                    app["status"] = "Güncel"
                    btn_close.configure(text="Kapat", state="normal", fg_color=CCleanerTheme.SUCCESS, hover_color=CCleanerTheme.SUCCESS_HOVER)
                    self._render_apps()
                else:
                    lbl_step.configure(text="İşlem tamamlandı. Detayları yukarıdaki günlükten inceleyebilirsiniz.", text_color=CCleanerTheme.PRIMARY)
                    btn_close.configure(text="Kapat", state="normal", fg_color=CCleanerTheme.PRIMARY)
                modal.protocol("WM_DELETE_WINDOW", modal.destroy)
                if self._batch_mode:
                    # Continue only after the user has reviewed/closed this result.
                    def next_update():
                        modal.destroy()
                        self._run_next_update()
                    btn_close.configure(command=next_update)
                    modal.protocol("WM_DELETE_WINDOW", next_update)
            try:
                modal.after(0, finish_ui)
            except Exception:
                pass

        # Trigger real update
        self.app_updater.run_update(app["id"], on_output=on_log, on_finish=on_done)

    def _update_all_apps(self):
        if self.app_updater.is_updating:
            return
        outdated = [app for app in self.apps if app["status"] != "Güncel"]
        if not outdated:
            return
        if not messagebox.askyesno("TerTemiz", tr("Seçili uygulama güncellemeleri sırayla kurulacak. Devam edilsin mi?"), parent=self):
            return
        self.update_queue = list(outdated)
        self._batch_mode = True
        self._run_next_update()

    def _run_next_update(self):
        if self.update_queue:
            self._open_update_modal(self.update_queue.pop(0))
        else:
            self._batch_mode = False
            self._start_scan_apps()
