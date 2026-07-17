param(
    [string]$SourceRoot = $(if ($env:MINECRAFT_MOD_SOURCE_ROOT) { $env:MINECRAFT_MOD_SOURCE_ROOT } else { Join-Path $HOME "Documents\minecraft-mod-sources" }),
    [string]$Config = $(Join-Path $PSScriptRoot "..\tools\local-mods.json"),
    [switch]$SkipPull,
    [switch]$AllowDirty,
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

function Invoke-Git {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$Arguments,
        [string]$WorkingDirectory = (Get-Location).Path,
        [switch]$CaptureOutput
    )

    if ($DryRun) {
        Write-Host "DRY RUN: git $($Arguments -join ' ')"
        return ""
    }

    Push-Location $WorkingDirectory
    try {
        if ($CaptureOutput) {
            $output = & git @Arguments
            if ($LASTEXITCODE -ne 0) {
                throw "git $($Arguments -join ' ') failed with exit code $LASTEXITCODE"
            }
            return ($output -join "`n").Trim()
        }

        & git @Arguments
        if ($LASTEXITCODE -ne 0) {
            throw "git $($Arguments -join ' ') failed with exit code $LASTEXITCODE"
        }
    } finally {
        Pop-Location
    }
}

function Test-GitBranchExists {
    param(
        [string]$RepositoryPath,
        [string]$Branch
    )

    if ($DryRun) {
        return $true
    }

    Push-Location $RepositoryPath
    try {
        & git rev-parse --verify --quiet $Branch | Out-Null
        return $LASTEXITCODE -eq 0
    } finally {
        Pop-Location
    }
}

function Normalize-RepositoryUrl {
    param([string]$Url)

    $normalized = $Url.Trim().Replace("\", "/").TrimEnd("/")
    if ($normalized.EndsWith(".git")) {
        $normalized = $normalized.Substring(0, $normalized.Length - 4)
    }
    if ($normalized.StartsWith("git@github.com:")) {
        $normalized = "https://github.com/" + $normalized.Substring("git@github.com:".Length)
    }
    return $normalized.ToLowerInvariant()
}

if (-not (Get-Command "git" -ErrorAction SilentlyContinue)) {
    throw "git is not on PATH."
}

$sourceRootPath = Resolve-LocalPath $SourceRoot
$configPath = Resolve-LocalPath $Config

if (-not (Test-Path $configPath)) {
    throw "Local mod config not found: $configPath"
}

$configData = Get-Content -Raw $configPath | ConvertFrom-Json

if (-not $DryRun -and -not (Test-Path $sourceRootPath)) {
    New-Item -ItemType Directory -Path $sourceRootPath | Out-Null
}

$results = @()

foreach ($mod in $configData.mods) {
    if ($null -ne $mod.enabled -and -not [bool]$mod.enabled) {
        Write-Host "Skipping disabled local mod entry: $($mod.name)"
        continue
    }
    if ($mod.PSObject.Properties["sourceOverride"]) {
        throw "$($mod.name) uses forbidden sourceOverride. Local mods must come from their configured repository under the source root."
    }
    $sourcePolicy = if ($mod.PSObject.Properties["sourcePolicy"]) { [string]$mod.sourcePolicy } else { "development" }
    if ($sourcePolicy -notin @("development", "remote-head")) {
        throw "$($mod.name) has unsupported sourcePolicy '$sourcePolicy'."
    }

    $sourceDir = Join-Path $sourceRootPath $mod.sourceFolder
    $gitDir = Join-Path $sourceDir ".git"

    if (-not (Test-Path $sourceDir)) {
        Write-Host "Cloning $($mod.name) into $sourceDir"
        Invoke-Git -Arguments @("clone", "--branch", $mod.branch, "--single-branch", $mod.repository, $sourceDir)

        $head = if ($DryRun) { "" } else { Invoke-Git -Arguments @("rev-parse", "--short", "HEAD") -WorkingDirectory $sourceDir -CaptureOutput }
        $results += [pscustomobject]@{
            Mod = $mod.name
            Action = "cloned"
            Branch = $mod.branch
            Head = $head
            Path = $sourceDir
        }
        continue
    }

    if (-not (Test-Path $gitDir)) {
        Write-Warning "$($mod.name) source folder exists but is not a git repository: $sourceDir"
        $results += [pscustomobject]@{
            Mod = $mod.name
            Action = "skipped-not-git"
            Branch = $mod.branch
            Head = ""
            Path = $sourceDir
        }
        continue
    }

    $dirty = if ($DryRun) { "" } else { Invoke-Git -Arguments @("status", "--porcelain") -WorkingDirectory $sourceDir -CaptureOutput }
    if ($dirty -and -not $AllowDirty) {
        Write-Warning "$($mod.name) has local changes. Skipping pull. Re-run with -AllowDirty if you know this is okay."
        $head = Invoke-Git -Arguments @("rev-parse", "--short", "HEAD") -WorkingDirectory $sourceDir -CaptureOutput
        $results += [pscustomobject]@{
            Mod = $mod.name
            Action = "skipped-dirty"
            Branch = $mod.branch
            Head = $head
            Path = $sourceDir
        }
        continue
    }

    $currentBranch = if ($DryRun) { $mod.branch } else { Invoke-Git -Arguments @("rev-parse", "--abbrev-ref", "HEAD") -WorkingDirectory $sourceDir -CaptureOutput }

    if (-not $SkipPull) {
        Write-Host "Fetching $($mod.name) $($mod.branch)"
        Invoke-Git -Arguments @("fetch", "origin", $mod.branch) -WorkingDirectory $sourceDir
    }

    if ($currentBranch -ne $mod.branch) {
        Write-Host "Switching $($mod.name) from $currentBranch to $($mod.branch)"
        if (Test-GitBranchExists -RepositoryPath $sourceDir -Branch $mod.branch) {
            Invoke-Git -Arguments @("checkout", $mod.branch) -WorkingDirectory $sourceDir
        } else {
            Invoke-Git -Arguments @("checkout", "-b", $mod.branch, "origin/$($mod.branch)") -WorkingDirectory $sourceDir
        }
    }

    if (-not $SkipPull) {
        Write-Host "Pulling $($mod.name)"
        Invoke-Git -Arguments @("pull", "--ff-only", "origin", $mod.branch) -WorkingDirectory $sourceDir
    }

    if (-not $DryRun -and $sourcePolicy -eq "remote-head") {
        $actualRepository = Invoke-Git -Arguments @("remote", "get-url", "origin") -WorkingDirectory $sourceDir -CaptureOutput
        if ((Normalize-RepositoryUrl $actualRepository) -ne (Normalize-RepositoryUrl ([string]$mod.repository))) {
            throw "$($mod.name) origin is '$actualRepository', expected '$($mod.repository)'. Refusing the wrong repository."
        }
        $fullHead = Invoke-Git -Arguments @("rev-parse", "HEAD") -WorkingDirectory $sourceDir -CaptureOutput
        $remoteHead = Invoke-Git -Arguments @("rev-parse", "origin/$($mod.branch)") -WorkingDirectory $sourceDir -CaptureOutput
        if ($fullHead -ne $remoteHead) {
            throw "$($mod.name) HEAD $($fullHead.Substring(0, 12)) is not origin/$($mod.branch) $($remoteHead.Substring(0, 12)). Refusing an old or divergent version."
        }
        $head = $fullHead.Substring(0, 12)
    } else {
        $head = if ($DryRun) { "" } else { Invoke-Git -Arguments @("rev-parse", "--short", "HEAD") -WorkingDirectory $sourceDir -CaptureOutput }
    }
    $results += [pscustomobject]@{
        Mod = $mod.name
        Action = if ($SkipPull) { "checked" } else { "updated" }
        Branch = $mod.branch
        Head = $head
        Path = $sourceDir
    }
}

if ($results.Count -gt 0) {
    Write-Host "Local mod repository status:"
    $results | Format-Table -AutoSize
}
