$ErrorActionPreference = "Stop"

$BotDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$PidFile = Join-Path $BotDir "bot.pid"
$Stopped = $false

if (Test-Path -LiteralPath $PidFile) {
    $BotPid = Get-Content -LiteralPath $PidFile -ErrorAction SilentlyContinue
    if ($BotPid -and (Get-Process -Id $BotPid -ErrorAction SilentlyContinue)) {
        Stop-Process -Id $BotPid -Force
        Write-Host "Bot to'xtatildi. PID: $BotPid"
        $Stopped = $true
    }
}

$BotProcesses = Get-CimInstance Win32_Process |
    Where-Object { $_.CommandLine -and $_.CommandLine.Contains("bot.py") -and $_.CommandLine.Contains($BotDir) }

foreach ($BotProcess in $BotProcesses) {
    Stop-Process -Id $BotProcess.ProcessId -Force -ErrorAction SilentlyContinue
    Write-Host "Bot process to'xtatildi. PID: $($BotProcess.ProcessId)"
    $Stopped = $true
}

Remove-Item -LiteralPath $PidFile -Force -ErrorAction SilentlyContinue

if (-not $Stopped) {
    Write-Host "Bot ishlamayotgan bo'lishi mumkin."
}
