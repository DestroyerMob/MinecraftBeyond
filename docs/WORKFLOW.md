# Minecraft Beyond Workflow

This repo should act as the source of truth for the modpack, while each unpublished mod remains source-controlled in its own repository.

## Tool Suite

- Git and GitHub for the pack repository, branches, pull requests, and syncing between machines.
- Prism Launcher for local playtesting.
- Java 21 for Minecraft 1.21.1 and NeoForge development.
- packwiz for a git-friendly modpack manifest and exports.
- Gradle wrappers from each local mod repository for reproducible local builds.
- GitHub Actions later, once the pack shape settles, to validate the pack and optionally build local mod artifacts.

## Repository Rules

- Commit pack metadata, configs, scripts, docs, and Prism instance metadata.
- Do not commit downloaded mod jars, generated runtime files, logs, worlds, screenshots, or local cache folders.
- Keep unpublished mod source outside this repo, normally in a folder such as `$HOME\Documents\minecraft-mod-sources`.
- Treat `minecraft/` as disposable runtime state. If something in there should be part of the pack, move it into `pack/` and let packwiz manage it.

## Third-Party Mods

Use packwiz for CurseForge and Modrinth mods so the repo stores metadata and hashes instead of binary jars.

### Prism-First Import

If you use Prism's mod browser because it is faster and nicer, download the mod into the instance first, then run:

```powershell
.\scripts\Import-PrismMods.ps1
```

The script copies jars from `minecraft/mods/` into `pack/mods/`, runs `packwiz cf detect`, and refreshes the pack index. When detection succeeds, the temporary staged jar is replaced by a `.pw.toml` metadata file. Commit the generated metadata under `pack/`.

This works best for CurseForge downloads because packwiz can fingerprint jars against CurseForge. Unmatched jars are left in the Prism instance for local testing but removed from the staged pack copy so they do not accidentally become committed pack files.

Typical flow:

```powershell
cd pack
packwiz cf add <curseforge-project-slug-or-url>
packwiz refresh
git add .
git commit -m "Add <mod name>"
```

Use one change per mod group. That makes it much easier to bisect crashes and roll back a compatibility problem.

## Local Unpublished Mods

Use two lanes:

1. Development lane: clone or pull each mod repo locally, build with its Gradle wrapper, then sync the built jar into `minecraft/mods/` with `scripts/Update-PackLocalMods.ps1`.
2. Distribution lane: once a local mod has a usable test build, publish it as a GitHub Release or package artifact, then add that URL to packwiz. This keeps the pack reproducible on both machines without committing jars.

Avoid committing unpublished jars directly to the pack repo unless you explicitly want a short-lived emergency build. If you do it, remove the jar once the mod has a real release URL.

### Local Mod Source Updates

Clone missing local mod repositories and fast-forward existing checkouts:

```powershell
.\scripts\Update-LocalModRepos.ps1
```

Pull, build, and copy the latest local mod jars into Prism:

```powershell
.\scripts\Update-PackLocalMods.ps1
```

Existing dirty source checkouts are skipped by default so unfinished work is not disturbed. Use `-AllowDirty` only when you intentionally want to pull inside a checkout with local changes.

## Two-Machine Setup

On each machine:

1. Clone this pack repo into the Prism `instances` folder, or create a Prism instance that points at this folder.
2. Install Java 21 and packwiz.
3. Run `.\scripts\Update-LocalModRepos.ps1` to clone the local mod repos into a shared source folder such as `C:\Users\<you>\Documents\minecraft-mod-sources`.
4. Set `MINECRAFT_MOD_SOURCE_ROOT` to that folder, or pass `-SourceRoot` to the sync script.
5. Run `.\scripts\Test-ModpackWorkspace.ps1`.
6. Run `.\scripts\Update-PackLocalMods.ps1`.

For local mods that are private or require authentication, make sure both machines have GitHub credentials that can read the repos before relying on automation.

## Branch Protocol

- `main` should stay playable.
- Use feature branches for mod additions, config passes, and local mod integration changes.
- Commit pack changes separately from local mod source changes.
- When a pack change depends on a local mod change, mention the required mod repo commit or release tag in the pack commit or pull request.

## Release Protocol

For a playable snapshot:

1. Confirm Prism launches from a clean `minecraft/mods/`.
2. Run `packwiz refresh` from `pack/`.
3. Tag the pack repo, for example `pack-v0.1.0`.
4. Publish local mod jars as GitHub Releases or packages.
5. Export `.mrpack` or CurseForge zip only after the pack works through packwiz install/update.

## Compatibility Notes

- The Prism instance currently uses NeoForge 21.1.234.
- Ecology already targets NeoForge 21.1.234.
- Better Enchanting, Auric, and MoreWeapons currently target NeoForge 21.1.228.
- Mobs Tool Forging currently targets NeoForge 21.1.233.
- MoreWeapons must use the `1.21.1-neoforge` branch for this pack.

The minor NeoForge differences should be reviewed during the first test launch. If anything behaves oddly, align all local mod Gradle properties to 21.1.234 before deeper debugging.
