param(
    [string]$SourceRoot = $(if ($env:MINECRAFT_MOD_SOURCE_ROOT) { $env:MINECRAFT_MOD_SOURCE_ROOT } else { Join-Path $HOME "Documents\minecraft-mod-sources" }),
    [string]$Config = $(Join-Path $PSScriptRoot "..\tools\local-mods.json"),
    [string]$ModsDir = $(Join-Path $PSScriptRoot "..\minecraft\mods"),
    [switch]$SkipPull,
    [switch]$SkipBuild,
    [switch]$AllowDirty,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

$repoUpdater = Join-Path $PSScriptRoot "Update-LocalModRepos.ps1"
$jarSync = Join-Path $PSScriptRoot "Sync-LocalMods.ps1"

if (-not (Test-Path $repoUpdater)) {
    throw "Missing repository updater script: $repoUpdater"
}

if (-not (Test-Path $jarSync)) {
    throw "Missing local mod sync script: $jarSync"
}

if ($SkipPull) {
    Write-Host "Skipping local mod repository pulls."
} else {
    $repoArgs = @{
        SourceRoot = $SourceRoot
        Config = $Config
    }

    if ($AllowDirty) {
        $repoArgs.AllowDirty = $true
    }
    if ($DryRun) {
        $repoArgs.DryRun = $true
    }

    & $repoUpdater @repoArgs
}

$syncArgs = @{
    SourceRoot = $SourceRoot
    Config = $Config
    ModsDir = $ModsDir
}

if (-not $SkipBuild) {
    $syncArgs.Build = $true
}
if ($DryRun) {
    $syncArgs.DryRun = $true
}

& $jarSync @syncArgs

Write-Host "Local mod update complete."
