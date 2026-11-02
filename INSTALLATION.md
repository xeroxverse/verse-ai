# VERSE — Windows 11 PowerShell Installation Guide

## Option A: One-Command Master PowerShell Installer (Recommended)
Open **Windows PowerShell** in the folder where you downloaded `VERSE_MASTER_INSTALLER.ps1` and run:
```powershell
powershell -ExecutionPolicy Bypass -File .\VERSE_MASTER_INSTALLER.ps1
```
The installer automatically backs up any existing `C:\verse` files, preserves your `memory\` and `workspace\`, deploys all modules, runs the 17-test verification suite, and launches the JARVIS HUD + Floating Orb.

## Option B: Manual ZIP Extraction
1. Extract `VERSE_COMPLETE_PROJECT.zip` to `C:\verse`.
2. In Windows PowerShell:
   ```powershell
   cd C:\verse
   python .\verse.py --test
   Start-Process "http://127.0.0.1:8765"
   python .\verse.py --orb
   ```
