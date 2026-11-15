[CmdletBinding()]
param(
    [switch]$Check,
    [ValidateRange(1, 65535)]
    [int]$Port = 8000
)

$ErrorActionPreference = 'Stop'
$backendDir = Split-Path -Parent $PSScriptRoot
$pythonPath = Join-Path $backendDir '.venv\Scripts\python.exe'
$envPath = Join-Path $backendDir '.env'

if (-not (Test-Path -LiteralPath $pythonPath -PathType Leaf)) {
    Write-Host 'Missing backend/.venv. From backend/, run:'
    Write-Host '  py -3.14 -m venv .venv'
    Write-Host '  .\.venv\Scripts\python.exe -m pip install -r requirements.txt'
    exit 1
}

if (-not (Test-Path -LiteralPath $envPath -PathType Leaf)) {
    Write-Host 'Missing backend/.env. From backend/, run:'
    Write-Host '  Copy-Item .env.example .env'
    Write-Host 'Then set DATABASE_URL to your PostgreSQL database in .env.'
    exit 1
}

$startArgs = @((Join-Path $PSScriptRoot 'start.py'), '--port', [string]$Port)
if ($Check) {
    $startArgs += '--check'
}

Push-Location -LiteralPath $backendDir
try {
    & $pythonPath @startArgs
    $startupExitCode = $LASTEXITCODE
}
finally {
    Pop-Location
}
exit $startupExitCode
