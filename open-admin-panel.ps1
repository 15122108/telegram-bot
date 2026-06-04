$ErrorActionPreference = "SilentlyContinue"

$workspace = "C:\Users\acer\Documents\New project\telegram-bot"
$tunnelScript = Join-Path $workspace "keep-admin-panel-tunnel.ps1"
$panelUrl = "http://127.0.0.1:8088/login"
$edgePaths = @(
    "$env:ProgramFiles\Microsoft\Edge\Application\msedge.exe",
    "${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe"
)

function Test-Panel {
    try {
        $response = Invoke-WebRequest -UseBasicParsing $panelUrl -TimeoutSec 2
        return $response.StatusCode -eq 200
    } catch {
        return $false
    }
}

if (-not (Test-Panel)) {
    Start-Process -WindowStyle Hidden `
        -FilePath "C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe" `
        -ArgumentList @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $tunnelScript)
}

for ($i = 0; $i -lt 20; $i++) {
    if (Test-Panel) {
        $edge = $edgePaths | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
        if ($edge) {
            Start-Process -FilePath $edge -ArgumentList @(
                "--app=$panelUrl",
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
    "Admin panel hali ochilmadi. Internet yoki VPS aloqasini tekshiring, keyin shortcutni qayta bosing.",
    "Visa eSIM Admin Panel"
) | Out-Null
