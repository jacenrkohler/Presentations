# LAB05_Windows_pre-fetch.ps1: downloads for Lab 5, Surprise Bonus Lab (Windows).
# Run it in PowerShell, in its folder:
#   powershell -ExecutionPolicy Bypass -File .\LAB05_Windows_pre-fetch.ps1
# Extra options go to ai_prefetch.py, for example: -File .\LAB05_Windows_pre-fetch.ps1 --dry-run
# Optional parts: -File .\LAB05_Windows_pre-fetch.ps1 --optional
$ErrorActionPreference = "Stop"
$Here = Split-Path -Parent $MyInvocation.MyCommand.Path
$Root = Split-Path -Parent $Here
$Lab1 = Join-Path $Root "Lab01"
Write-Host "Lab 5, Surprise Bonus Lab: nothing to download. You need a web browser and an internet connection."
