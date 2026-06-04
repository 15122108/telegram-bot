$ErrorActionPreference = "Stop"

$BotDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$PidFile = Join-Path $BotDir "bot.pid"
$StartScript = Join-Path $BotDir "start-bot.ps1"

$Running = $false
if (Test-Path -LiteralPath $PidFile) {
    $BotPid = Get-Content -LiteralPath $PidFile -ErrorAction SilentlyContinue
    $Running = [bool]($BotPid -and (Get-Process -Id $BotPid -ErrorAction SilentlyContinue))
}

if (-not $Running) {
    powershell.exe -ExecutionPolicy Bypass -File $StartScript
}

