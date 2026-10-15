# TerTemiz Windows Installer
# Installs TerTemiz into Windows AppData Programs and registers in Windows Settings

$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  TerTemiz Professional Kurulum Sihirbazi" -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Cyan

# 1. Kill any existing instances
Write-Host "`n[1/5] Calisan uygulamalar sonlandiriliyor..." -ForegroundColor Gray
Get-Process -Name "*TerTemiz*" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Get-Process -Name "*pythonw*" -ErrorAction SilentlyContinue | Where-Object { $_.Path -like "*CCleaner7*" -or $_.Path -like "*TerTemiz*" } | Stop-Process -Force -ErrorAction SilentlyContinue

# 2. Define install paths
$InstallDir = Join-Path $env:LOCALAPPDATA "Programs\TerTemiz"
$SourceDist = Join-Path $PSScriptRoot "dist\TerTemiz"

Write-Host "[2/5] Dosyalar yukleniyor: $InstallDir" -ForegroundColor Gray
if (Test-Path $InstallDir) {
    Remove-Item -Path $InstallDir -Recurse -Force
}
New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null

# Copy compiled executable and dependencies
Copy-Item -Path "$SourceDist\*" -Destination $InstallDir -Recurse -Force

# Also copy uninstaller to target
$UninstallerPath = Join-Path $InstallDir "uninstall.ps1"
$UninstallContent = @"
# TerTemiz Kaldirici
Write-Host "TerTemiz kaldiriliyor..." -ForegroundColor Yellow
Get-Process -Name "*TerTemiz*" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue

`$DesktopPath = [System.Environment]::GetFolderPath([System.Environment+SpecialFolder]::Desktop)
`$DesktopShortcut = Join-Path `$DesktopPath "TerTemiz.lnk"
if (Test-Path `$DesktopShortcut) { Remove-Item -Force `$DesktopShortcut }

`$StartMenuPath = Join-Path `$env:APPDATA "Microsoft\Windows\Start Menu\Programs\TerTemiz.lnk"
if (Test-Path `$StartMenuPath) { Remove-Item -Force `$StartMenuPath }

`$RegKey = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\TerTemiz"
if (Test-Path `$RegKey) { Remove-Item -Path `$RegKey -Recurse -Force }

`$AppDir = "`$env:LOCALAPPDATA\Programs\TerTemiz"
Start-Sleep -Seconds 1
Remove-Item -Path `$AppDir -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "TerTemiz basariyla kaldirildi." -ForegroundColor Green
"@
Set-Content -Path $UninstallerPath -Value $UninstallContent -Encoding UTF8

# 3. Create Desktop & Start Menu Shortcuts
Write-Host "[3/5] Kisayollar olusturuluyor..." -ForegroundColor Gray
$WshShell = New-Object -ComObject WScript.Shell
$ExePath = Join-Path $InstallDir "TerTemiz.exe"

# Desktop shortcut
$DesktopPath = [System.Environment]::GetFolderPath([System.Environment+SpecialFolder]::Desktop)
$DesktopShortcut = Join-Path $DesktopPath "TerTemiz.lnk"
$Shortcut = $WshShell.CreateShortcut($DesktopShortcut)
$Shortcut.TargetPath = $ExePath
$Shortcut.WorkingDirectory = $InstallDir
$Shortcut.IconLocation = "$ExePath,0"
$Shortcut.Description = "TerTemiz Professional 7.0.2"
$Shortcut.Save()

# Start Menu shortcut
$StartMenuDir = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs"
$StartShortcut = Join-Path $StartMenuDir "TerTemiz.lnk"
$Shortcut2 = $WshShell.CreateShortcut($StartShortcut)
$Shortcut2.TargetPath = $ExePath
$Shortcut2.WorkingDirectory = $InstallDir
$Shortcut2.IconLocation = "$ExePath,0"
$Shortcut2.Description = "TerTemiz Professional 7.0.2"
$Shortcut2.Save()

# 4. Register in Windows Programs and Features (Add/Remove Programs)
Write-Host "[4/5] Windows Program Ekle/Kaldir kaydi yapiliyor..." -ForegroundColor Gray
$RegKey = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\TerTemiz"
if (-not (Test-Path $RegKey)) {
    New-Item -Path $RegKey -Force | Out-Null
}

$InstallSize = (Get-ChildItem -Path $InstallDir -Recurse | Measure-Object -Property Length -Sum).Sum / 1KB

Set-ItemProperty -Path $RegKey -Name "DisplayName" -Value "TerTemiz Professional"
Set-ItemProperty -Path $RegKey -Name "DisplayVersion" -Value "7.0.2"
Set-ItemProperty -Path $RegKey -Name "Publisher" -Value "TerTemiz Software"
Set-ItemProperty -Path $RegKey -Name "InstallLocation" -Value $InstallDir
Set-ItemProperty -Path $RegKey -Name "DisplayIcon" -Value "$ExePath,0"
Set-ItemProperty -Path $RegKey -Name "UninstallString" -Value "powershell.exe -ExecutionPolicy Bypass -File `"$UninstallerPath`""
Set-ItemProperty -Path $RegKey -Name "EstimatedSize" -Value ([int]$InstallSize)
Set-ItemProperty -Path $RegKey -Name "NoModify" -Value 1 -Type DWord
Set-ItemProperty -Path $RegKey -Name "NoRepair" -Value 1 -Type DWord

# 5. Launch the installed app
Write-Host "[5/5] Kurulum tamamlandi! Uygulama baslatiliyor..." -ForegroundColor Green
Start-Process -FilePath $ExePath -WorkingDirectory $InstallDir

Write-Host "`n=======================================================" -ForegroundColor Cyan
Write-Host "  TEBRIKLER! TerTemiz Windows'unuza Basariyla Kuruldu! " -ForegroundColor Green
Write-Host "  Konum: $InstallDir" -ForegroundColor White
Write-Host "  Baslat menusu ve Masaustu kisayollari aktif." -ForegroundColor White
Write-Host "=======================================================" -ForegroundColor Cyan
