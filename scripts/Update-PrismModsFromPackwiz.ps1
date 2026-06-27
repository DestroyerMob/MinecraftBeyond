param(
    [string]$MinecraftDir,
    [string]$ModsDir,
    [string]$PackDir,
    [string]$Packwiz,
    [string]$JavaHome,
    [string]$Installer,
    [string]$MainJar,
    [int]$Port,
    [switch]$NoDownload,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

$arguments = @("update-prism-mods")

if ($MinecraftDir) {
    $arguments += @("--minecraft-dir", $MinecraftDir)
}
if ($ModsDir) {
    $arguments += @("--mods-dir", $ModsDir)
}
if ($PackDir) {
    $arguments += @("--pack-dir", $PackDir)
}
if ($Packwiz) {
    $arguments += @("--packwiz", $Packwiz)
}
if ($JavaHome) {
    $arguments += @("--java-home", $JavaHome)
}
if ($Installer) {
    $arguments += @("--installer", $Installer)
}
if ($MainJar) {
    $arguments += @("--main-jar", $MainJar)
}
if ($Port) {
    $arguments += @("--port", $Port)
}
if ($NoDownload) {
    $arguments += "--no-download"
}
if ($DryRun) {
    $arguments += "--dry-run"
}

& (Join-Path $PSScriptRoot "modpack.ps1") @arguments
exit $LASTEXITCODE
