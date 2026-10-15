import ast
import hashlib
import os
import pathlib
import tempfile
import unittest
from collections import defaultdict
from unittest.mock import patch

from core.app_updater import AppUpdater, parse_upgrade_table, NO_UPGRADES
from core.preferences import load_preferences, save_preferences
from ui.i18n import set_language, tr

ROOT = pathlib.Path(__file__).resolve().parents[1]

def portable_tools():
    # Execute the real platform-independent definitions without mocking Windows APIs.
    ns = {"os": os, "hashlib": hashlib, "defaultdict": defaultdict}
    for filename, names in (("core/system_info.py", {"format_size"}),
                            ("core/tools.py", {"DuplicateFinder", "DiskAnalyzer"})):
        tree = ast.parse((ROOT / filename).read_text(encoding="utf-8"))
        nodes = [node for node in tree.body if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name in names]
        exec(compile(ast.Module(body=nodes, type_ignores=[]), filename, "exec"), ns)
    return ns

class RegressionTests(unittest.TestCase):
    def tearDown(self):
        set_language("tr")

    def test_preferences_persist_and_validate(self):
        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory) / "preferences.json"
            save_preferences({"theme": "light", "language": "en"}, path)
            self.assertEqual(load_preferences(path), {"theme": "light", "language": "en"})
            path.write_text('{"theme":"bad","language":"xx"}')
            self.assertEqual(load_preferences(path), {"theme": "system", "language": "tr"})
            path.write_text('[]')
            self.assertEqual(load_preferences(path)["theme"], "system")

    def test_live_language_and_dynamic_text(self):
        set_language("en")
        self.assertEqual(tr("Uygulama Dili:"), "Language:")
        self.assertEqual(tr("RAM: %42 Dolu"), "RAM: 42% Used")
        self.assertEqual(tr("3 Uygulama Güncellemesi Mevcut! ⚠️"), "3 Application Updates Available! ⚠️")
        set_language("tr")
        self.assertEqual(tr("Uygulama Dili:"), "Uygulama Dili:")

    def table(self, localized=False):
        columns = ["Ad", "Kimlik", "Sürüm", "Kullanılabilir", "Kaynak"] if localized else ["Name", "Id", "Version", "Available", "Source"]
        def row(items):
            return "".join(f"{item:<24}" for item in items)
        return row(columns) + "\n" + "-" * 120 + "\n" + row(["Test App", "Vendor.Test", "1.0", "2.0", "winget"]) + "\n1 upgrades available.\n"

    def test_winget_english_and_turkish(self):
        for localized in (False, True):
            rows = parse_upgrade_table(self.table(localized))
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["id"], "Vendor.Test")
            self.assertEqual(rows[0]["available_version"], "2.0")

    def test_winget_error_is_not_up_to_date(self):
        updater = AppUpdater()
        with patch("core.app_updater.shutil.which", return_value=None):
            self.assertEqual(updater.scan_updates(), [])
        self.assertTrue(updater.last_error)
        self.assertFalse(updater.is_scanning)
        result = type("Result", (), {"returncode": 5, "stdout": "source failed", "stderr": ""})()
        with patch("core.app_updater.shutil.which", return_value="winget"), patch("core.app_updater.subprocess.run", return_value=result):
            self.assertEqual(updater.scan_updates(), [])
        self.assertIn("source failed", updater.last_error)

    def test_winget_no_updates(self):
        result = type("Result", (), {"returncode": NO_UPGRADES, "stdout": "", "stderr": ""})()
        updater = AppUpdater()
        with patch("core.app_updater.shutil.which", return_value="winget"), patch("core.app_updater.subprocess.run", return_value=result):
            self.assertEqual(updater.scan_updates(), [])
        self.assertFalse(updater.last_error)

    def test_update_command_is_exact_and_reports_result(self):
        with patch("core.app_updater.subprocess.Popen") as popen:
            process = popen.return_value.__enter__.return_value
            process.stdout = iter(["Done\n"])
            process.wait.return_value = 0
            finished = []
            updater = AppUpdater()
            updater.run_update("Vendor.Test", on_finish=finished.append).join(5)
            self.assertEqual(finished, [True])
            command = popen.call_args.args[0]
            self.assertIn("--exact", command)
            self.assertNotIn("--accept-package-agreements", command)
            self.assertFalse(popen.call_args.kwargs["shell"])
            self.assertFalse(updater.is_updating)

    def test_duplicates_compare_full_contents(self):
        tools = portable_tools()
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            (root / "a").write_bytes(b"A" * (512 * 1024) + b"X")
            (root / "b").write_bytes(b"A" * (512 * 1024) + b"Y")
            self.assertEqual(tools["DuplicateFinder"]().find_duplicates(directory), [])
            (root / "c").write_bytes((root / "a").read_bytes())
            groups = tools["DuplicateFinder"]().find_duplicates(directory)
            self.assertEqual(len(groups), 1)
            self.assertEqual(len(groups[0]["paths"]), 2)

    def test_disk_scan_limit(self):
        tools = portable_tools()
        with tempfile.TemporaryDirectory() as directory:
            for index in range(3):
                (pathlib.Path(directory) / str(index)).write_bytes(b"abc")
            result = tools["DiskAnalyzer"]().scan_path(directory, max_files=1)
            self.assertEqual(result["total_files"], 1)
            self.assertEqual(result["total_bytes"], 3)

if __name__ == "__main__":
    unittest.main()
