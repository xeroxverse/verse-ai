# VERSE — Troubleshooting Guide (Windows 11 & Acer Swift Pro)

| Symptom | Root Cause | Exact Fix in Windows PowerShell |
| :--- | :--- | :--- |
| `winget` error `0x8a15005e` (`msstore` certificate) | Outdated Microsoft Store source certificate | Append `--source winget`: `winget install -e --id Python.Python.3.12 --source winget` |
| `can't open file ...verse.py: [Errno 2]` | PowerShell is inside `C:\Windows\System32` instead of `C:\verse` | Run `cd C:\verse` first, or run `python C:\verse\verse.py --serve` |
| `[WinError 32] The process cannot access verse.db` | Unclosed SQLite file handle on Windows | Fixed in `verse_core/memory.py` and `verse_ai.py` using `contextlib.closing(sqlite3.connect(...))` |
| Local Ollama not installed yet | Ollama is optional | VERSE runs out-of-the-box using its built-in local synthesis engine. To add local 3B/7B GGUF inference: `winget install Ollama.Ollama --source winget` then `ollama pull qwen2.5-coder:3b-instruct-q4_K_M` |
| Port `8765` already in use | Previous VERSE server still running in background | Run `.\stop_verse.ps1` or `python .\verse.py --serve` after closing the old window |
