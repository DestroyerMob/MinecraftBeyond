param(
    [switch]$Strict
)

$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "Resolve-Packwiz.ps1")

function Test-Command {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Name,
        [switch]$Required
    )

    $command = Get-Command $Name -ErrorAction SilentlyContinue
    if ($command) {
        [pscustomobject]@{
            Tool = $Name
            Status = "found"
            Required = [bool]$Required
            Path = $command.Source
        }
        return
    }

    $status = if ($Required) { "missing-required" } else { "missing" }
    [pscustomobject]@{
        Tool = $Name
        Status = $status
        Required = [bool]$Required
        Path = ""
    }
}

function Test-Packwiz {
    param([string]$RepoRoot)

    $path = Resolve-Packwiz -RepoRoot $RepoRoot
    if ($path) {
        [pscustomobject]@{
            Tool = "packwiz"
            Status = "found"
            Required = $false
            Path = $path
        }
        return
    }

    [pscustomobject]@{
        Tool = "packwiz"
        Status = "missing"
        Required = $false
        Path = ""
    }
}

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$failures = 0

Write-Host "Checking tools..."
$toolResults = @()
$toolResults += Test-Command -Name "git" -Required
$toolResults += Test-Command -Name "java" -Required
$toolResults += Test-Packwiz -RepoRoot $repoRoot.Path
$toolResults += Test-Command -Name "gh"
$toolResults | Select-Object Tool, Status, Path | Format-Table -AutoSize

foreach ($result in $toolResults) {
    if ($result.Status -eq "missing-required") {
        $failures++
    }
}

Write-Host "Checking Prism instance metadata..."
$packPath = Join-Path $repoRoot "mmc-pack.json"
if (-not (Test-Path $packPath)) {
    Write-Warning "Missing mmc-pack.json"
    $failures++
} else {
    $mmcPack = Get-Content -Raw $packPath | ConvertFrom-Json
    $minecraft = $mmcPack.components | Where-Object { $_.uid -eq "net.minecraft" } | Select-Object -First 1
    $neoforge = $mmcPack.components | Where-Object { $_.uid -eq "net.neoforged" } | Select-Object -First 1

    [pscustomobject]@{
        Minecraft = $minecraft.version
        NeoForge = $neoforge.version
    } | Format-List

    if ($minecraft.version -ne "1.21.1") {
        Write-Warning "Expected Minecraft 1.21.1."
        $failures++
    }
    if ($neoforge.version -ne "21.1.234") {
        Write-Warning "Expected NeoForge 21.1.234."
        $failures++
    }
}

Write-Host "Checking pack scaffold..."
$expectedFiles = @(
    "pack\pack.toml",
    "pack\index.toml",
    "tools\local-mods.json",
    "scripts\Import-PrismMods.ps1",
    "scripts\Install-Packwiz.ps1",
    "scripts\Resolve-Packwiz.ps1",
    "scripts\Sync-LocalMods.ps1",
    "scripts\Update-LocalModRepos.ps1",
    "scripts\Update-PackLocalMods.ps1"
)

foreach ($relativePath in $expectedFiles) {
    $path = Join-Path $repoRoot $relativePath
    if (Test-Path $path) {
        Write-Host "found $relativePath"
    } else {
        Write-Warning "missing $relativePath"
        $failures++
    }
}

if (-not (Resolve-Packwiz -RepoRoot $repoRoot.Path)) {
    Write-Warning "packwiz was not found. Run .\scripts\Install-Packwiz.ps1 before adding CurseForge/Modrinth mods or refreshing hashes."
}

if ($Strict -and $failures -gt 0) {
    exit 1
}

if ($failures -gt 0) {
    Write-Warning "$failures workspace check(s) need attention."
} else {
    Write-Host "Workspace checks passed."
}
