"""Exercise real Tk widgets on Windows; do not clean or update the runner."""
import contextlib
import os
from pathlib import Path
import sys
import tempfile
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from PIL import ImageGrab
from main import TerTemizApp
from ui.views.updater_view import UpdaterView
from ui.views.driver_updater_view import DriverUpdaterView
from ui.views.performance_optimizer_view import PerformanceOptimizerView
from ui.views.tools_view import ToolsView
from ui import widgets as ctk
from ui.i18n import tr

out = ROOT / 'test-artifacts'
out.mkdir(exist_ok=True)
errors = []

with tempfile.TemporaryDirectory() as directory, contextlib.ExitStack() as stack:
    stack.enter_context(patch.dict(os.environ, {'LOCALAPPDATA': directory}))
    # Automatic background scanning is tested separately. Keep UI snapshots deterministic.
    for cls, method in [(UpdaterView, '_start_scan_apps'), (DriverUpdaterView, '_start_scan'),
                        (PerformanceOptimizerView, '_refresh_data'), (ToolsView, '_load_uninstall_data')]:
        stack.enter_context(patch.object(cls, method, lambda self: None))
    app = TerTemizApp()
    app.report_callback_exception = lambda *args: errors.append(str(args))
    try:
        for size in ['1000x700', '960x640']:
            app.geometry(size + "+0+0")
            for tab in ['health_check', 'custom_clean', 'performance', 'updater', 'driver_updater', 'registry', 'tools', 'settings']:
                app._navigate_to(tab)
                app.update()
                if tab == 'updater':
                    view = app.views[tab]
                    view.apps = [{'name': 'Long application name for responsive layout verification without ellipsis', 'id': 'Vendor.Example.LongPackageName', 'installed_version': '1.0.1234.5678', 'available_version': '2.0.1234.5678', 'status': 'Güncelleme Mevcut'}]
                    view._render_apps()
                    app.update()
                if tab == 'driver_updater':
                    view = app.views[tab]
                    view.devices = [{'name': 'Long graphics adapter name for responsive layout verification', 'manufacturer': 'Example Manufacturer', 'category': 'Grafik & Ekran', 'version': '—', 'date': '—', 'status_str': 'Windows Update ile denetle', 'status_color': '#f59e0b'}]
                    view._render_devices()
                    app.update()
                ImageGrab.grab().save(out / f'{size}-{tab}-tr.png')
        settings = app.views['settings']
        settings._change_language('English')
        app.update()
        assert app.nav_buttons['settings'].cget('text') == '⚙️  Settings'
        assert settings.theme_menu.cget('values') == ['Dark', 'Light', 'System Theme']
        # Renamed tabs must preserve callback keys and remain selectable.
        app._navigate_to('custom_clean')
        app.views['custom_clean'].tabview.set('Uygulamalar')
        assert app.views['custom_clean'].tabview.get() == 'Uygulamalar'
        app.update()
        for label, expected in [('Light', 'Light'), ('Dark', 'Dark'), ('System Theme', None)]:
            app._navigate_to('settings')
            settings.theme_menu.set(label)
            settings._change_theme(label)
            app.update()
            if expected:
                assert ctk.get_appearance_mode() == expected
            ImageGrab.grab().save(out / f'settings-en-{label}.png')
        app._navigate_to('updater')
        app.update()
        ImageGrab.grab().save(out / 'updater-en.png')
        # Error state must never claim that all packages are current.
        updater = app.views['updater']
        updater.app_updater.last_error = 'Simulated WinGet source failure'
        updater._render_apps()
        app.update()
        assert updater.lbl_app_title.cget('text') == 'Update Scan Failed'
        ImageGrab.grab().save(out / 'updater-error-en.png')
        settings._change_language('Türkçe')
        app.update()
        assert app.nav_buttons['settings'].cget('text') == '⚙️  Seçenekler'
        assert tr('Tema Tercihi:') == 'Tema Tercihi:'
        assert not errors, errors
        print('PASS: eight views at two sizes; live TR/EN; light/dark/system; update error UI')
    finally:
        app.destroy()
