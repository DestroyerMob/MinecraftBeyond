param(
    [string]$PrismModsDir = $(Join-Path $PSScriptRoot "..\minecraft\mods"),
    [string]$PackDir = $(Join-Path $PSScriptRoot "..\pack"),
    [switch]$IncludeLocal,
    [switch]$KeepUnmatchedStagedJars,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "Resolve-Packwiz.ps1")

function Resolve-LocalPath {
    param([string]$Path)

    if ([System.IO.Path]::IsPathRooted($Path)) {
        return [System.IO.Path]::GetFullPath($Path)
    }

    return [System.IO.Path]::GetFullPath((Join-Path (Get-Location) $Path))
}

$prismModsPath = Resolve-LocalPath $PrismModsDir
$packDirPath = Resolve-LocalPath $PackDir
$packModsPath = Join-Path $packDirPath "mods"
$packTomlPath = Join-Path $packDirPath "pack.toml"

if (-not (Test-Path $packTomlPath)) {
    throw "pack.toml not found at $packTomlPath"
}

if (-not (Test-Path $prismModsPath)) {
    Write-Warning "Prism mods folder does not exist yet: $prismModsPath"
    return
}

$prismJars = Get-ChildItem -Path $prismModsPath -Filter "*.jar" -File
if (-not $IncludeLocal) {
    $prismJars = $prismJars | Where-Object { $_.Name -notmatch "-local\.jar$" }
}

if (-not $prismJars -or $prismJars.Count -eq 0) {
    Write-Host "No Prism mod jars found to import."
    return
}

Write-Host "Preparing to import $($prismJars.Count) Prism mod jar(s) through packwiz CurseForge detection."

if (-not $DryRun) {
    $packwiz = Resolve-Packwiz
    if (-not $packwiz) {
        throw "packwiz was not found. Run .\scripts\Install-Packwiz.ps1 or add packwiz to PATH before importing Prism-downloaded mods."
    }
}

if (-not $DryRun -and -not (Test-Path $packModsPath)) {
    New-Item -ItemType Directory -Path $packModsPath | Out-Null
}

$staged = @()
foreach ($jar in $prismJars) {
    $destination = Join-Path $packModsPath $jar.Name
    Write-Host "Staging $($jar.Name)"

    if (-not $DryRun) {
        Copy-Item -LiteralPath $jar.FullName -Destination $destination -Force
    }

    $staged += [pscustomobject]@{
        Name = $jar.Name
        Source = $jar.FullName
        Staged = $destination
    }
}

if ($DryRun) {
    Write-Host "Dry run complete. No files were copied and packwiz was not run."
    return
}

Push-Location $packDirPath
try {
    Write-Host "Running packwiz cf detect..."
    & $packwiz cf detect
    if ($LASTEXITCODE -ne 0) {
        throw "packwiz cf detect failed with exit code $LASTEXITCODE"
    }

    $unmatched = @()
    foreach ($item in $staged) {
        if (Test-Path $item.Staged) {
            $unmatched += $item
        }
    }

    if ($unmatched.Count -gt 0) {
        Write-Warning "packwiz did not match every staged jar. These are probably Modrinth jars, unpublished jars, or CurseForge files without a matching fingerprint."
        $unmatched | Select-Object Name, Source | Format-Table -AutoSize

        if (-not $KeepUnmatchedStagedJars) {
            foreach ($item in $unmatched) {
                Remove-Item -LiteralPath $item.Staged -Force
            }
            Write-Host "Removed unmatched staged jar copies from pack/mods. The original Prism jars were left alone."
        }
    }

    Write-Host "Refreshing packwiz index..."
    & $packwiz refresh
    if ($LASTEXITCODE -ne 0) {
        throw "packwiz refresh failed with exit code $LASTEXITCODE"
    }
} finally {
    Pop-Location
}

Write-Host "Import complete. Review and commit the generated pack metadata:"
Write-Host "  git status --short pack"
Write-Host "  git add pack"
Write-Host "  git commit -m `"Import Prism-downloaded mods`""
