"""Verify the actual packaged executable creates its expected main window."""
import ctypes
from ctypes import wintypes
from pathlib import Path
import subprocess
import time
from PIL import ImageGrab

ROOT = Path(__file__).resolve().parents[1]
user32 = ctypes.windll.user32
user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
user32.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
user32.IsWindowVisible.argtypes = [wintypes.HWND]
callback_type = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
user32.EnumWindows.argtypes = [callback_type, wintypes.LPARAM]

process = subprocess.Popen([str(ROOT / 'dist/TerTemiz/TerTemiz.exe')], cwd=ROOT)
try:
    titles = []
    @callback_type
    def visit(hwnd, unused):
        pid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        if pid.value == process.pid and user32.IsWindowVisible(hwnd):
            title = ctypes.create_unicode_buffer(512)
            user32.GetWindowTextW(hwnd, title, 512)
            titles.append(title.value)
        return True
    for _ in range(30):
        assert process.poll() is None, 'Packaged app exited during startup'
        titles.clear()
        user32.EnumWindows(visit, 0)
        if 'TerTemiz Professional 7.0.2' in titles:
            break
        time.sleep(0.5)
    assert 'TerTemiz Professional 7.0.2' in titles, titles
    ImageGrab.grab().save(ROOT / 'test-artifacts/packaged-app.png')
    print('PASS: packaged TerTemiz.exe opened its actual 7.0.2 main window')
finally:
    process.terminate()
    process.wait(timeout=10)
