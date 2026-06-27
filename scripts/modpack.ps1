param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Arguments
)

$ErrorActionPreference = "Stop"

$scriptPath = Join-Path $PSScriptRoot "..\tools\modpack.py"
$python = Get-Command "python3" -ErrorAction SilentlyContinue
if (-not $python) {
    $python = Get-Command "python" -ErrorAction SilentlyContinue
}
if (-not $python) {
    $pyLauncher = Get-Command "py" -ErrorAction SilentlyContinue
    if ($pyLauncher) {
        & $pyLauncher.Source -3 $scriptPath @Arguments
        exit $LASTEXITCODE
    }

    throw "Python 3 was not found on PATH."
}

& $python.Source $scriptPath @Arguments
exit $LASTEXITCODE
