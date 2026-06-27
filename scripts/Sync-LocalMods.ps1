param(
    [string]$SourceRoot = $(if ($env:MINECRAFT_MOD_SOURCE_ROOT) { $env:MINECRAFT_MOD_SOURCE_ROOT } else { Join-Path $HOME "Documents\minecraft-mod-sources" }),
    [string]$Config = $(Join-Path $PSScriptRoot "..\tools\local-mods.json"),
    [string]$ModsDir = $(Join-Path $PSScriptRoot "..\minecraft\mods"),
    [switch]$Build,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

function Resolve-LocalPath {
    param([string]$Path)

    if ([System.IO.Path]::IsPathRooted($Path)) {
        return [System.IO.Path]::GetFullPath($Path)
    }

    return [System.IO.Path]::GetFullPath((Join-Path (Get-Location) $Path))
}

$sourceRootPath = Resolve-LocalPath $SourceRoot
$configPath = Resolve-LocalPath $Config
$modsDirPath = Resolve-LocalPath $ModsDir

if (-not (Test-Path $configPath)) {
    throw "Local mod config not found: $configPath"
}

$configData = Get-Content -Raw $configPath | ConvertFrom-Json

if (-not $DryRun -and -not (Test-Path $modsDirPath)) {
    New-Item -ItemType Directory -Path $modsDirPath | Out-Null
}

$synced = @()
$missing = @()

foreach ($mod in $configData.mods) {
    $sourceDir = Join-Path $sourceRootPath $mod.sourceFolder

    if (-not (Test-Path $sourceDir)) {
        $missing += [pscustomobject]@{
            Mod = $mod.name
            Path = $sourceDir
            Clone = "git clone --branch $($mod.branch) $($mod.repository) `"$sourceDir`""
        }
        continue
    }

    if ($Build) {
        $gradlew = Join-Path $sourceDir "gradlew.bat"
        if (-not (Test-Path $gradlew)) {
            $gradlew = Join-Path $sourceDir "gradlew"
        }
        if (-not (Test-Path $gradlew)) {
            throw "No Gradle wrapper found for $($mod.name) at $sourceDir"
        }

        Write-Host "Building $($mod.name)..."
        if (-not $DryRun) {
            Push-Location $sourceDir
            try {
                & $gradlew build
                if ($LASTEXITCODE -ne 0) {
                    throw "Gradle build failed for $($mod.name) with exit code $LASTEXITCODE"
                }
            } finally {
                Pop-Location
            }
        }
    }

    $libsDir = Join-Path $sourceDir "build\libs"
    if (-not (Test-Path $libsDir)) {
        if ($DryRun) {
            Write-Warning "Would sync $($mod.name), but build/libs does not exist yet: $libsDir"
            continue
        }
        throw "No build/libs folder found for $($mod.name). Run with -Build or build the mod first."
    }

    $jar = Get-ChildItem -Path $libsDir -Filter $mod.jarGlob -File |
        Where-Object { $_.Name -notmatch "(sources|javadoc|dev|plain)" } |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1

    if (-not $jar) {
        if ($DryRun) {
            Write-Warning "Would sync $($mod.name), but no runtime jar matching $($mod.jarGlob) exists in $libsDir"
            continue
        }
        throw "No runtime jar matching $($mod.jarGlob) found for $($mod.name) in $libsDir"
    }

    $destination = Join-Path $modsDirPath "$($mod.modId)-local.jar"
    Write-Host "Syncing $($mod.name): $($jar.Name) -> $destination"

    if (-not $DryRun) {
        Copy-Item -LiteralPath $jar.FullName -Destination $destination -Force
    }

    $synced += [pscustomobject]@{
        Mod = $mod.name
        Jar = $jar.Name
        Destination = $destination
    }
}

if ($missing.Count -gt 0) {
    Write-Warning "Some local mod source folders are missing:"
    $missing | Format-List
}

if ($synced.Count -gt 0) {
    Write-Host "Synced local mods:"
    $synced | Format-Table -AutoSize
}
