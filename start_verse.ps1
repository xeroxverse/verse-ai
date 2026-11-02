# Starts VERSE AI v15.0 Clean Professional SHIELD OS HUD
$ErrorActionPreference = "Continue"
Set-Location $PSScriptRoot

# Refresh Environment PATH so newly installed Ollama is recognized
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
if (Test-Path "$env:LOCALAPPDATA\Programs\Ollama") {
    $env:Path += ";$env:LOCALAPPDATA\Programs\Ollama"
}

& (Join-Path $PSScriptRoot "stop_verse.ps1")
Start-Sleep -Milliseconds 300
python .\verse.py --serve
