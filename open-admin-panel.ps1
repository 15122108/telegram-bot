$ErrorActionPreference = "SilentlyContinue"

$workspace = "C:\Users\acer\Documents\New project\telegram-bot"
$tunnelScript = Join-Path $workspace "keep-admin-panel-tunnel.ps1"
$urlFile = Join-Path $workspace "admin-panel-url.txt"
$botPidFile = Join-Path $workspace "bot-local.pid"
$defaultPanelUrl = "http://127.0.0.1:8088/login"
$panelUrl = $defaultPanelUrl

if (Test-Path -LiteralPath $urlFile) {
    $configuredUrl = (Get-Content -LiteralPath $urlFile -Raw).Trim()
    if ($configuredUrl) {
        $panelUrl = $configuredUrl
    }
}

if ($env:VISA_ESIM_ADMIN_URL) {
    $panelUrl = $env:VISA_ESIM_ADMIN_URL.Trim()
}

if ($panelUrl -notmatch "/login$") {
    $panelUrl = $panelUrl.TrimEnd("/") + "/login"
}

$usesLocalTunnel = $panelUrl -like "http://127.0.0.1:*" -or $panelUrl -like "http://localhost:*"
$edgePaths = @(
    "$env:ProgramFiles\Microsoft\Edge\Application\msedge.exe",
    "${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe"
)
$pythonPaths = @(
    "$workspace\.venv\Scripts\python.exe",
    "C:\Users\acer\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe",
    "python.exe"
)

function Test-Panel {
    try {
        $response = Invoke-WebRequest -UseBasicParsing $panelUrl -TimeoutSec 2
        return $response.StatusCode -eq 200
    } catch {
        return $false
    }
}

function Start-LocalPanel {
    $python = $pythonPaths | Where-Object {
        if ($_ -eq "python.exe") { return $true }
        Test-Path -LiteralPath $_
    } | Select-Object -First 1

    if (-not $python) {
        return
    }

    Start-Process -WindowStyle Hidden `
        -FilePath $python `
        -ArgumentList @("admin_panel.py") `
        -WorkingDirectory $workspace
}

function Test-LocalBot {
    if (Test-Path -LiteralPath $botPidFile) {
        $pidText = (Get-Content -LiteralPath $botPidFile -Raw).Trim()
        if ($pidText -match "^\d+$") {
            $process = Get-Process -Id ([int]$pidText) -ErrorAction SilentlyContinue
            if ($process) {
                return $true
            }
        }
    }

    $botProcess = Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | Where-Object {
        $_.CommandLine -like "*bot.py*" -and $_.CommandLine -notlike "*Get-CimInstance*"
    } | Select-Object -First 1

    return [bool]$botProcess
}

function Start-LocalBot {
    if (Test-LocalBot) {
        return
    }

    $python = $pythonPaths | Where-Object {
        if ($_ -eq "python.exe") { return $true }
        Test-Path -LiteralPath $_
    } | Select-Object -First 1

    if (-not $python) {
        return
    }

    $process = Start-Process -WindowStyle Hidden `
        -FilePath $python `
        -ArgumentList @("bot.py") `
        -WorkingDirectory $workspace `
        -RedirectStandardOutput (Join-Path $workspace "bot-local.log") `
        -RedirectStandardError (Join-Path $workspace "bot-local.err.log") `
        -PassThru

    if ($process) {
        Set-Content -LiteralPath $botPidFile -Value $process.Id
    }
}

if ($usesLocalTunnel) {
    Start-LocalBot
}

if ($usesLocalTunnel -and -not (Test-Panel)) {
    Start-LocalPanel
    Start-Sleep -Seconds 2

    if (-not (Test-Panel)) {
        Start-Process -WindowStyle Hidden `
            -FilePath "C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe" `
            -ArgumentList @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $tunnelScript)
    }
}

for ($i = 0; $i -lt 20; $i++) {
    if (Test-Panel) {
        $edge = $edgePaths | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
        if ($edge) {
            Start-Process -FilePath $edge -ArgumentList @(
                "--app=$panelUrl",
                "--new-window",
                "--window-size=1280,860",
                "--user-data-dir=$workspace\admin-panel-profile"
            )
        } else {
            Start-Process $panelUrl
        }
        exit 0
    }
    Start-Sleep -Seconds 1
}

Add-Type -AssemblyName PresentationFramework
[System.Windows.MessageBox]::Show(
    "Admin panel hali ochilmadi. Linkni tekshiring: $panelUrl",
    "Visa eSIM Admin Panel"
) | Out-Null
