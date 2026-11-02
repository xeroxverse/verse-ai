# Gracefully stops all running VERSE Python processes and frees port 8765
$ErrorActionPreference = "SilentlyContinue"
Get-NetTCPConnection -LocalPort 8765 -ErrorAction SilentlyContinue | ForEach-Object {
    if ($_.OwningProcess -gt 4) {
        Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue
    }
}
Get-CimInstance Win32_Process -Filter "Name LIKE 'python%'" -ErrorAction SilentlyContinue | Where-Object {
    $_.CommandLine -match "verse\.py|verse_floating_orb\.py|verse_ai\.py"
} | ForEach-Object {
    Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
}
Write-Host "[VERSE AI v8.5] Stopped old VERSE server and freed port 8765." -ForegroundColor Green
