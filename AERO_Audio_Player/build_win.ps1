$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
$python = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path $python)) { throw 'Virtual environment missing.' }
& $python -m PyInstaller --noconfirm --clean --onefile --windowed --name 'AERO Audio Player' --collect-all pygame --collect-all mutagen --hidden-import pygame app.py
if ($LASTEXITCODE -ne 0) { throw 'PyInstaller build failed.' }
$exe = Join-Path $PSScriptRoot 'dist\AERO Audio Player.exe'
Write-Host "Standalone EXE: $exe"
Write-Host ("Size: {0:N1} MB" -f ((Get-Item $exe).Length / 1MB))
