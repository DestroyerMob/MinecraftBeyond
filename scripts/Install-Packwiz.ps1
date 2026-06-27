param(
    [string]$InstallDir = $(Join-Path $PSScriptRoot "..\tools\bin"),
    [string]$Module = "github.com/packwiz/packwiz@latest"
)

$ErrorActionPreference = "Stop"

function Resolve-LocalPath {
    param([string]$Path)

    if ([System.IO.Path]::IsPathRooted($Path)) {
        return [System.IO.Path]::GetFullPath($Path)
    }

    return [System.IO.Path]::GetFullPath((Join-Path (Get-Location) $Path))
}

$go = Get-Command "go" -ErrorAction SilentlyContinue
if (-not $go) {
    throw "Go is required to install packwiz from source. Install Go first, for example with Scoop: scoop install go"
}

$installPath = Resolve-LocalPath $InstallDir
New-Item -ItemType Directory -Path $installPath -Force | Out-Null

$oldGobIn = $env:GOBIN
try {
    $env:GOBIN = $installPath
    Write-Host "Installing packwiz into $installPath"
    & $go.Source install $Module
    if ($LASTEXITCODE -ne 0) {
        throw "go install failed with exit code $LASTEXITCODE"
    }
} finally {
    $env:GOBIN = $oldGobIn
}

$packwizPath = Join-Path $installPath "packwiz.exe"
if (-not (Test-Path -LiteralPath $packwizPath)) {
    $packwizPath = Join-Path $installPath "packwiz"
}

if (-not (Test-Path -LiteralPath $packwizPath)) {
    throw "packwiz did not appear in $installPath after installation."
}

Write-Host "packwiz installed at $packwizPath"
