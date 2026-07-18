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

function Get-StonecutterMinecraftVersion {
    param([Parameter(Mandatory = $true)][string]$Version)

    if ($Version -notmatch '^(.+)-(?:fabric|neoforge)$') {
        throw "Cannot infer the Minecraft version from Stonecutter selection '$Version'."
    }
    return $Matches[1]
}

function Invoke-ModGradle {
    param(
        [Parameter(Mandatory = $true)][string]$SourceDir,
        [Parameter(Mandatory = $true)][string[]]$Tasks,
        [string]$JavaHome = ""
    )

    $gradlewBat = Join-Path $SourceDir "gradlew.bat"
    $gradlewUnix = Join-Path $SourceDir "gradlew"
    $wrapperJar = Join-Path $SourceDir "gradle\wrapper\gradle-wrapper.jar"
    if (-not (Test-Path $gradlewBat) -and -not (Test-Path $gradlewUnix)) {
        throw "No Gradle wrapper found at $SourceDir"
    }
    if (-not (Test-Path $gradlewBat) -and -not (Test-Path $wrapperJar)) {
        throw "Gradle wrapper jar not found at $wrapperJar"
    }

    $hadJavaHome = Test-Path Env:JAVA_HOME
    $previousJavaHome = $env:JAVA_HOME
    $previousPath = $env:PATH
    if ($JavaHome) {
        $javaExecutable = Join-Path $JavaHome "bin\java.exe"
        if (-not (Test-Path -LiteralPath $javaExecutable -PathType Leaf)) {
            throw "Configured Java home has no runtime at $javaExecutable"
        }
        $env:JAVA_HOME = $JavaHome
        $env:PATH = "$(Join-Path $JavaHome 'bin');$previousPath"
    }

    Push-Location $SourceDir
    try {
        if (Test-Path $gradlewBat) {
            & $gradlewBat @Tasks
        } else {
            & java "-Dorg.gradle.appname=gradlew" -classpath $wrapperJar org.gradle.wrapper.GradleWrapperMain @Tasks
        }
        if ($LASTEXITCODE -ne 0) {
            throw "Gradle tasks '$($Tasks -join ' ')' failed with exit code $LASTEXITCODE"
        }
    } finally {
        Pop-Location
        if ($JavaHome) {
            if ($hadJavaHome) {
                $env:JAVA_HOME = $previousJavaHome
            } else {
                Remove-Item Env:JAVA_HOME -ErrorAction SilentlyContinue
            }
            $env:PATH = $previousPath
        }
    }
}

function Get-BuildJavaHome {
    param([Parameter(Mandatory = $true)][int]$Version)

    $environmentName = "MINECRAFT_BEYOND_JAVA_${Version}_HOME"
    $environmentValue = [System.Environment]::GetEnvironmentVariable($environmentName)
    if ($environmentValue) {
        return [System.IO.Path]::GetFullPath($environmentValue)
    }

    $propertyName = "java${Version}Home"
    if ($script:devEnv -and $script:devEnv.PSObject.Properties[$propertyName]) {
        $configured = [string]$script:devEnv.$propertyName
        if ($configured) {
            return Resolve-LocalPath $configured
        }
    }
    throw "This build requires Java $Version. Configure $propertyName in tools\dev-env.local.json or set $environmentName."
}

function Get-FileSha1 {
    param([Parameter(Mandatory = $true)][string]$Path)

    return (Get-FileHash -LiteralPath $Path -Algorithm SHA1).Hash.ToLowerInvariant()
}

function Prepare-LocalMavenMirror {
    param([Parameter(Mandatory = $true)]$Mod)

    $buildConfig = if ($Mod.PSObject.Properties["build"]) { $Mod.build } else { $null }
    if (-not $buildConfig -or -not $buildConfig.PSObject.Properties["mavenMirror"]) {
        return @()
    }

    $repository = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot "..\tools\bin\local-maven"))
    foreach ($dependency in $buildConfig.mavenMirror) {
        $groupPath = ([string]$dependency.group).Replace('.', [System.IO.Path]::DirectorySeparatorChar)
        $artifactDir = Join-Path $repository (Join-Path $groupPath (Join-Path ([string]$dependency.artifact) ([string]$dependency.version)))
        $jar = Join-Path $artifactDir "$($dependency.artifact)-$($dependency.version).jar"
        $pom = Join-Path $artifactDir "$($dependency.artifact)-$($dependency.version).pom"
        $expectedSha1 = ([string]$dependency.sha1).ToLowerInvariant()
        $needsDownload = -not (Test-Path -LiteralPath $jar -PathType Leaf)
        if (-not $needsDownload) {
            $needsDownload = (Get-FileSha1 -Path $jar) -ne $expectedSha1
        }

        if ($DryRun) {
            if ($needsDownload) {
                Write-Host "DRY RUN: download $($dependency.url) -> $jar"
            }
            Write-Host "DRY RUN: write Maven metadata $pom"
            continue
        }

        New-Item -ItemType Directory -Path $artifactDir -Force | Out-Null
        if ($needsDownload) {
            Invoke-WebRequest -Uri ([string]$dependency.url) -OutFile $jar -UseBasicParsing -TimeoutSec 120
        }
        $actualSha1 = Get-FileSha1 -Path $jar
        if ($actualSha1 -ne $expectedSha1) {
            throw "Downloaded Maven mirror artifact $($dependency.artifact):$($dependency.version) has SHA-1 $actualSha1, expected $expectedSha1."
        }
        $pomXml = @"
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>$($dependency.group)</groupId>
  <artifactId>$($dependency.artifact)</artifactId>
  <version>$($dependency.version)</version>
</project>
"@
        [System.IO.File]::WriteAllText($pom, $pomXml, [System.Text.UTF8Encoding]::new($false))
    }

    $initScript = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot "..\tools\gradle\local-maven.init.gradle"))
    if (-not (Test-Path -LiteralPath $initScript -PathType Leaf)) {
        throw "Local Maven Gradle init script is missing: $initScript"
    }
    return @("--init-script", $initScript, "-DminecraftBeyond.localMaven=$repository")
}

function Invoke-LocalModBuild {
    param(
        [Parameter(Mandatory = $true)]$Mod,
        [Parameter(Mandatory = $true)][string]$SourceDir,
        [Parameter(Mandatory = $true)][string]$SourcePolicy
    )

    $buildConfig = if ($Mod.PSObject.Properties["build"]) { $Mod.build } else { $null }
    $buildTasks = if ($buildConfig -and $buildConfig.PSObject.Properties["tasks"]) {
        @($buildConfig.tasks | ForEach-Object { [string]$_ })
    } elseif ($SourcePolicy -eq "remote-head") {
        @("clean", "build")
    } else {
        @("build")
    }
    $configuredBuildArguments = if ($buildConfig -and $buildConfig.PSObject.Properties["arguments"]) {
        @($buildConfig.arguments | ForEach-Object { [string]$_ })
    } else {
        @()
    }
    $buildArguments = @((Prepare-LocalMavenMirror -Mod $Mod) + $configuredBuildArguments)
    $gradleTasks = @($buildArguments + $buildTasks)
    $outputDir = if ($buildConfig -and $buildConfig.PSObject.Properties["outputDir"]) {
        Join-Path $SourceDir ([string]$buildConfig.outputDir)
    } else {
        Join-Path $SourceDir "build\libs"
    }
    $stonecutterVersion = if ($buildConfig -and $buildConfig.PSObject.Properties["stonecutterVersion"]) {
        [string]$buildConfig.stonecutterVersion
    } else {
        ""
    }
    $buildJavaHome = if ($buildConfig -and $buildConfig.PSObject.Properties["javaVersion"]) {
        Get-BuildJavaHome -Version ([int]$buildConfig.javaVersion)
    } else {
        ""
    }

    if (-not $stonecutterVersion) {
        if ($DryRun) {
            Write-Host "DRY RUN: ($SourceDir) gradlew $($buildTasks -join ' ')"
        } else {
            Invoke-ModGradle -SourceDir $SourceDir -Tasks $gradleTasks -JavaHome $buildJavaHome
        }
        return $outputDir
    }

    $minecraftVersion = [string]$buildConfig.minecraftVersion
    $refreshRestoredProject = if ($buildConfig.PSObject.Properties["refreshRestoredProject"]) {
        [bool]$buildConfig.refreshRestoredProject
    } else {
        $true
    }
    $currentFile = Join-Path $SourceDir "versions\current"
    if (-not (Test-Path -LiteralPath $currentFile -PathType Leaf)) {
        throw "$($Mod.name) Stonecutter selection file is missing: $currentFile"
    }
    $originalBytes = [System.IO.File]::ReadAllBytes($currentFile)
    $originalVersion = ([System.Text.Encoding]::UTF8.GetString($originalBytes)).Trim()

    if ($DryRun) {
        Write-Host "DRY RUN: select Stonecutter project $stonecutterVersion in $currentFile"
        Write-Host "DRY RUN: ($SourceDir) gradlew Refresh active project"
        Write-Host "DRY RUN: ($SourceDir) gradlew $($buildTasks -join ' ')"
        Write-Host "DRY RUN: restore Stonecutter project $originalVersion in $currentFile"
        if ($originalVersion -and $refreshRestoredProject) {
            Write-Host "DRY RUN: ($SourceDir) gradlew Refresh active project"
        }
        return $outputDir
    }

    $hadCiSingleBuild = Test-Path Env:CI_SINGLE_BUILD
    $previousCiSingleBuild = $env:CI_SINGLE_BUILD
    $buildError = $null
    $restoreError = $null
    try {
        [System.IO.File]::WriteAllText($currentFile, $stonecutterVersion, [System.Text.UTF8Encoding]::new($false))
        $env:CI_SINGLE_BUILD = "${stonecutterVersion}:${minecraftVersion}"
        Invoke-ModGradle -SourceDir $SourceDir -Tasks @($buildArguments + @("Refresh active project")) -JavaHome $buildJavaHome
        Invoke-ModGradle -SourceDir $SourceDir -Tasks $gradleTasks -JavaHome $buildJavaHome
    } catch {
        $buildError = $_
    } finally {
        [System.IO.File]::WriteAllBytes($currentFile, $originalBytes)
        if ($originalVersion -and $refreshRestoredProject) {
            try {
                $restoreMinecraftVersion = Get-StonecutterMinecraftVersion -Version $originalVersion
                $env:CI_SINGLE_BUILD = "${originalVersion}:${restoreMinecraftVersion}"
                Invoke-ModGradle -SourceDir $SourceDir -Tasks @($buildArguments + @("Refresh active project")) -JavaHome $buildJavaHome
            } catch {
                $restoreError = $_
            }
        }
        if ($hadCiSingleBuild) {
            $env:CI_SINGLE_BUILD = $previousCiSingleBuild
        } else {
            Remove-Item Env:CI_SINGLE_BUILD -ErrorAction SilentlyContinue
        }
    }

    if ($buildError) {
        if ($restoreError) {
            throw "$buildError; restoring the Stonecutter source view also failed: $restoreError"
        }
        throw $buildError
    }
    if ($restoreError) {
        Write-Warning "Built $($Mod.name), but could not refresh the restored Stonecutter source view: $restoreError"
    }
    return $outputDir
}

$sourceRootPath = Resolve-LocalPath $SourceRoot
$configPath = Resolve-LocalPath $Config
$modsDirPath = Resolve-LocalPath $ModsDir

if (-not (Test-Path $configPath)) {
    throw "Local mod config not found: $configPath"
}

$configData = Get-Content -Raw $configPath | ConvertFrom-Json
$devEnvPath = Join-Path $PSScriptRoot "..\tools\dev-env.local.json"
$script:devEnv = if (Test-Path -LiteralPath $devEnvPath -PathType Leaf) {
    Get-Content -Raw -LiteralPath $devEnvPath | ConvertFrom-Json
} else {
    $null
}

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
        Write-Host "Building $($mod.name)..."
        $libsDir = Invoke-LocalModBuild -Mod $mod -SourceDir $sourceDir -SourcePolicy $sourcePolicy
    } else {
        $buildConfig = if ($mod.PSObject.Properties["build"]) { $mod.build } else { $null }
        $libsDir = if ($buildConfig -and $buildConfig.PSObject.Properties["outputDir"]) {
            Join-Path $sourceDir ([string]$buildConfig.outputDir)
        } else {
            Join-Path $sourceDir "build\libs"
        }
    }

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

    $destinationName = if ($mod.PSObject.Properties["pack"] -and $mod.pack.PSObject.Properties["filename"]) {
        [string]$mod.pack.filename
    } else {
        "$($mod.modId)-local.jar"
    }
    $enabledDestination = Join-Path $modsDirPath $destinationName
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
