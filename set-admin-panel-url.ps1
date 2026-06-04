param(
    [Parameter(Mandatory = $true)]
    [string]$Url
)

$ErrorActionPreference = "Stop"
$workspace = Split-Path -Parent $MyInvocation.MyCommand.Path
$urlFile = Join-Path $workspace "admin-panel-url.txt"
$cleanUrl = $Url.Trim()

if (-not ($cleanUrl -match "^https?://")) {
    throw "URL http:// yoki https:// bilan boshlanishi kerak."
}

Set-Content -LiteralPath $urlFile -Value $cleanUrl -Encoding UTF8
Write-Host "Admin panel URL saqlandi: $cleanUrl"
