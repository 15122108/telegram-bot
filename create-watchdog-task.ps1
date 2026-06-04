$ErrorActionPreference = "Stop"

$TaskName = "VisaEsimUzBotWatchdog"
$BotDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$WrapperDir = Join-Path $env:LOCALAPPDATA "VisaEsimUzBot"
$Wrapper = Join-Path $WrapperDir "watchdog.bat"
$Watchdog = Join-Path $BotDir "watchdog.ps1"

New-Item -ItemType Directory -Force -Path $WrapperDir | Out-Null
Set-Content -LiteralPath $Wrapper -Encoding ASCII -Value @"
@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$Watchdog"
"@

schtasks /Delete /TN $TaskName /F 2>$null | Out-Null
schtasks /Create /TN $TaskName /SC MINUTE /MO 5 /TR $Wrapper /F | Out-Null
schtasks /Query /TN $TaskName /FO LIST

