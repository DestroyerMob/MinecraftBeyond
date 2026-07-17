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

function Invoke-CheckedGit {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$Arguments,
        [Parameter(Mandatory = $true)]
        [string]$WorkingDirectory
    )

    Push-Location $WorkingDirectory
    try {
        $output = & git @Arguments
        if ($LASTEXITCODE -ne 0) {
            throw "git $($Arguments -join ' ') failed with exit code $LASTEXITCODE"
        }
        return ($output -join "`n").Trim()
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

function Assert-RemoteHeadSource {
    param(
        [Parameter(Mandatory = $true)]$Mod,
        [Parameter(Mandatory = $true)][string]$SourceDir
    )

    $sourcePolicy = if ($mod.PSObject.Properties["sourcePolicy"]) { [string]$mod.sourcePolicy } else { "development" }
    if ($sourcePolicy -notin @("development", "remote-head")) {
        throw "$($mod.name) has unsupported sourcePolicy '$sourcePolicy'."
    }
    if ($sourcePolicy -ne "remote-head") {
        return ""
    }
    if (-not $Build) {
        throw "$($mod.name) cannot sync a previously built artifact. Run Update-PackLocalMods.ps1 so the canonical source is verified, cleaned, built, and synced atomically."
    }
    if (-not (Test-Path -LiteralPath (Join-Path $SourceDir ".git"))) {
        throw "$($mod.name) requires its canonical Git checkout, but $SourceDir is not a Git repository."
    }
    if ($DryRun) {
        Write-Host "DRY RUN: verify $($mod.name) is the clean head of origin/$($mod.branch) from $($mod.repository)"
        return "origin/$($mod.branch)"
    }

    $repositoryRoot = [System.IO.Path]::GetFullPath((Invoke-CheckedGit -Arguments @("rev-parse", "--show-toplevel") -WorkingDirectory $SourceDir))
    if ($repositoryRoot.TrimEnd("\") -ine ([System.IO.Path]::GetFullPath($SourceDir)).TrimEnd("\")) {
        throw "$($mod.name) source path resolves inside a different repository ($repositoryRoot)."
    }

    $actualRepository = Invoke-CheckedGit -Arguments @("remote", "get-url", "origin") -WorkingDirectory $SourceDir
    if ((Normalize-RepositoryUrl $actualRepository) -ne (Normalize-RepositoryUrl ([string]$mod.repository))) {
        throw "$($mod.name) origin is '$actualRepository', expected '$($mod.repository)'. Refusing to build the wrong repository."
    }

    $currentBranch = Invoke-CheckedGit -Arguments @("rev-parse", "--abbrev-ref", "HEAD") -WorkingDirectory $SourceDir
    if ($currentBranch -ne [string]$mod.branch) {
        throw "$($mod.name) is on branch '$currentBranch', expected '$($mod.branch)'. Run Update-PackLocalMods.ps1."
    }

    $dirty = Invoke-CheckedGit -Arguments @("status", "--porcelain") -WorkingDirectory $SourceDir
    if ($dirty) {
        throw "$($mod.name) canonical checkout has uncommitted changes. Commit and push them, or discard them, before building."
    }

    Write-Host "Verifying latest $($mod.name) revision from origin/$($mod.branch)"
    Invoke-CheckedGit -Arguments @("fetch", "origin", [string]$mod.branch) -WorkingDirectory $SourceDir | Out-Null

    $head = Invoke-CheckedGit -Arguments @("rev-parse", "HEAD") -WorkingDirectory $SourceDir
    $remoteHead = Invoke-CheckedGit -Arguments @("rev-parse", "origin/$($mod.branch)") -WorkingDirectory $SourceDir
    if ($head -ne $remoteHead) {
        throw "$($mod.name) HEAD $($head.Substring(0, 12)) is not origin/$($mod.branch) $($remoteHead.Substring(0, 12)). Run Update-PackLocalMods.ps1; refusing to build an old or divergent version."
    }
    return $head
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
    if ($null -ne $mod.enabled -and -not [bool]$mod.enabled) {
        Write-Host "Skipping disabled local mod entry: $($mod.name)"
        continue
    }

    if ($mod.PSObject.Properties["sourceOverride"]) {
        throw "$($mod.name) uses forbidden sourceOverride. Local mods must come from their configured repository under the source root."
    }
    $sourceDir = Join-Path $sourceRootPath $mod.sourceFolder

    if (-not (Test-Path $sourceDir)) {
        $missing += [pscustomobject]@{
            Mod = $mod.name
            Path = $sourceDir
            Clone = "git clone --branch $($mod.branch) $($mod.repository) `"$sourceDir`""
        }
        continue
    }

    $revision = Assert-RemoteHeadSource -Mod $mod -SourceDir $sourceDir
    $sourcePolicy = if ($mod.PSObject.Properties["sourcePolicy"]) { [string]$mod.sourcePolicy } else { "development" }

    if ($Build) {
        $gradlewBat = Join-Path $sourceDir "gradlew.bat"
        $gradlewUnix = Join-Path $sourceDir "gradlew"
        $wrapperJar = Join-Path $sourceDir "gradle\wrapper\gradle-wrapper.jar"
        if (-not (Test-Path $gradlewBat) -and -not (Test-Path $gradlewUnix)) {
            throw "No Gradle wrapper found for $($mod.name) at $sourceDir"
        }
        if (-not (Test-Path $gradlewBat) -and -not (Test-Path $wrapperJar)) {
            throw "Gradle wrapper jar not found for $($mod.name) at $wrapperJar"
        }

        Write-Host "Building $($mod.name)..."
        if (-not $DryRun) {
            Push-Location $sourceDir
            try {
                $buildTasks = if ($sourcePolicy -eq "remote-head") { @("clean", "build") } else { @("build") }
                if (Test-Path $gradlewBat) {
                    & $gradlewBat @buildTasks
                } else {
                    & java "-Dorg.gradle.appname=gradlew" -classpath $wrapperJar org.gradle.wrapper.GradleWrapperMain @buildTasks
                }
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

    $jars = @(Get-ChildItem -Path $libsDir -Filter $mod.jarGlob -File |
        Where-Object { $_.Name -notmatch "-(sources|javadoc|dev|plain)(?:-[^/]+)?\.jar$" } |
        Sort-Object LastWriteTime -Descending)

    $jar = $jars | Select-Object -First 1

    if (-not $jar) {
        if ($DryRun) {
            Write-Warning "Would sync $($mod.name), but no runtime jar matching $($mod.jarGlob) exists in $libsDir"
            continue
        }
        throw "No runtime jar matching $($mod.jarGlob) found for $($mod.name) in $libsDir"
    }
    if ($sourcePolicy -eq "remote-head" -and $jars.Count -ne 1) {
        throw "Expected exactly one definitive runtime JAR for $($mod.name) after a clean build, found $($jars.Count) in $libsDir"
    }
    if ($mod.PSObject.Properties["expectedVersion"]) {
        $expectedJarName = "$($mod.modId)-$($mod.expectedVersion).jar"
        if ($jar.Name -ne $expectedJarName) {
            throw "$($mod.name) built $($jar.Name), but the pack requires $expectedJarName. Refusing the wrong release line."
        }
    }

    $enabledDestination = Join-Path $modsDirPath "$($mod.modId)-local.jar"
    $disabledDestination = "$enabledDestination.disabled"
    $destination = if ((Test-Path $disabledDestination) -and -not (Test-Path $enabledDestination)) { $disabledDestination } else { $enabledDestination }
    $revisionLabel = if ($revision) { $revision.Substring(0, [Math]::Min(12, $revision.Length)) } else { "development" }
    Write-Host "Syncing $($mod.name) ($revisionLabel): $($jar.Name) -> $destination"

    if (-not $DryRun) {
        Copy-Item -LiteralPath $jar.FullName -Destination $destination -Force
    }

    $synced += [pscustomobject]@{
        Mod = $mod.name
        Revision = $revisionLabel
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
