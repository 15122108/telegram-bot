$ErrorActionPreference = "Continue"

$keyPath = Join-Path $env:USERPROFILE ".ssh\visa_esim_uz_bot_ed25519"
$server = "root@178.105.212.24"
$forward = "8088:127.0.0.1:8088"
$sshPath = "$env:WINDIR\System32\OpenSSH\ssh.exe"
$logPath = Join-Path $PSScriptRoot "admin-panel-tunnel.log"

function Write-TunnelLog($message) {
    $stamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Add-Content -LiteralPath $logPath -Value "$stamp $message"
}

while ($true) {
    Write-TunnelLog "Starting SSH tunnel $forward"
    & $sshPath `
        -N `
        -o "ExitOnForwardFailure=yes" `
        -o "ServerAliveInterval=20" `
        -o "ServerAliveCountMax=2" `
        -o "TCPKeepAlive=yes" `
        -L $forward `
        -i $keyPath `
        $server 2>> $logPath

    Write-TunnelLog "SSH tunnel exited with code $LASTEXITCODE; restarting in 3 seconds"
    Start-Sleep -Seconds 3
}
