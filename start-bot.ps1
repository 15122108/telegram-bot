$ErrorActionPreference = "Stop"

$BotDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Python = "C:\Users\acer\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
$PidFile = Join-Path $BotDir "bot.pid"
$OutLog = Join-Path $BotDir "bot.log"
$ErrLog = Join-Path $BotDir "bot.err.log"

if (-not (Test-Path -LiteralPath $Python)) {
    $Python = (Get-Command python -ErrorAction SilentlyContinue).Source
}

if (-not $Python) {
    throw "Python topilmadi. Python 3 o'rnating yoki PATH sozlang."
}

if (Test-Path -LiteralPath $PidFile) {
    $ExistingPid = Get-Content -LiteralPath $PidFile -ErrorAction SilentlyContinue
    if ($ExistingPid -and (Get-Process -Id $ExistingPid -ErrorAction SilentlyContinue)) {
        Write-Host "Bot allaqachon ishlayapti. PID: $ExistingPid"
        exit 0
    }
}

$ExistingBot = Get-CimInstance Win32_Process |
    Where-Object { $_.CommandLine -and $_.CommandLine.Contains("bot.py") -and $_.CommandLine.Contains($BotDir) } |
    Select-Object -First 1

if ($ExistingBot) {
    Set-Content -LiteralPath $PidFile -Value $ExistingBot.ProcessId
    Write-Host "Bot allaqachon ishlayapti. PID: $($ExistingBot.ProcessId)"
    exit 0
}

$Process = Start-Process `
    -FilePath $Python `
    -ArgumentList @("-u", "bot.py") `
    -WorkingDirectory $BotDir `
    -RedirectStandardOutput $OutLog `
    -RedirectStandardError $ErrLog `
    -WindowStyle Hidden `
    -PassThru

Set-Content -LiteralPath $PidFile -Value $Process.Id
Write-Host "Bot ishga tushdi. PID: $($Process.Id)"
