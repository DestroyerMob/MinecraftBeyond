$script:ResolvePackwizScriptRoot = $PSScriptRoot

function Resolve-Packwiz {
    param(
        [string]$RepoRoot = [System.IO.Path]::GetFullPath((Join-Path $script:ResolvePackwizScriptRoot ".."))
    )

    $candidates = @(
        (Join-Path $RepoRoot "tools\bin\packwiz.exe"),
        (Join-Path $RepoRoot "tools\bin\packwiz")
    )

    foreach ($candidate in $candidates) {
        if (Test-Path -LiteralPath $candidate) {
            return [System.IO.Path]::GetFullPath($candidate)
        }
    }

    $command = Get-Command "packwiz" -ErrorAction SilentlyContinue
    if ($command) {
        return $command.Source
    }

    return $null
}
