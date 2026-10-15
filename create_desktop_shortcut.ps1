$WshShell = New-Object -ComObject WScript.Shell
$DesktopPath = [System.Environment]::GetFolderPath([System.Environment+SpecialFolder]::Desktop)
$OldShortcut = Join-Path $DesktopPath "CCleaner 7 Replica.lnk"
if (Test-Path $OldShortcut) {
    Remove-Item -Force $OldShortcut
}

$ShortcutPath = Join-Path $DesktopPath "TerTemiz.lnk"
$AppDir = Split-Path -Parent $MyInvocation.MyCommand.Path

$PythonwPath = "C:\Users\mcifci\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\pythonw.exe"
if (-not (Test-Path $PythonwPath)) {
    $PythonwPath = "python.exe"
}

$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $PythonwPath
$Shortcut.Arguments = "`"$AppDir\main.py`""
$Shortcut.WorkingDirectory = $AppDir
$Shortcut.IconLocation = "$AppDir\assets\tertemiz_icon.ico, 0"
$Shortcut.Description = "TerTemiz Professional 7.0.2"
$Shortcut.Save()

Write-Host "Masaustu kisayolu TerTemiz olarak olusturuldu: $ShortcutPath"
