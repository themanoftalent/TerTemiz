@echo off
title TerTemiz Professional 7.0.2
cd /d "%~dp0"
set PYTHON_EXE="C:\Users\mcifci\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\pythonw.exe"
if exist %PYTHON_EXE% (
    start "" %PYTHON_EXE% "%~dp0main.py"
) else (
    start "" python "%~dp0main.py"
)
exit
