# Minecraft Beyond Workflow

This repo should act as the source of truth for the modpack, while each unpublished mod remains source-controlled in its own repository.

## Tool Suite

- Git and GitHub for the pack repository, branches, pull requests, and syncing between machines.
- Prism Launcher for local playtesting.
- Java 21 for Minecraft 1.21.1 and NeoForge development.
- packwiz for a git-friendly modpack manifest and exports.
- Python 3 for the cross-platform `scripts/modpack` tooling.
- Go for installing the repo-local packwiz binary with `scripts/modpack install-packwiz`.
- Gradle wrappers from each local mod repository for reproducible local builds.
- GitHub Actions later, once the pack shape settles, to validate the pack and optionally build local mod artifacts.

## Portable Tooling

Use `scripts/modpack` as the canonical workflow command on macOS and Linux:

```bash
./scripts/modpack doctor
```

On Windows, use either wrapper:

```powershell
.\scripts\modpack.ps1 doctor
```

```cmd
scripts\modpack.cmd doctor
```

The command reads machine-local settings from `tools/dev-env.local.json` when present. Create it from the tracked template:

```bash
./scripts/modpack init-env
```

The local config is intentionally ignored by git. It lets each machine keep its own Java, packwiz, Prism mods, and local source paths without changing shared pack metadata.

Environment variables override the local config:

- `MINECRAFT_MOD_SOURCE_ROOT`
- `MINECRAFT_BEYOND_PRISM_MODS_DIR`
- `MINECRAFT_BEYOND_PACKWIZ` or `PACKWIZ`
- `MINECRAFT_BEYOND_JAVA_HOME` or `JAVA_HOME`

The older PowerShell scripts remain available, but new workflow docs should prefer `scripts/modpack` so the same commands work across development environments.

## Remote Sync Checks

Use `sync-status` to see the pack repo and every configured local mod repo in one table:

```bash
./scripts/modpack sync-status
```

Use `--fetch` when you want current remote ahead/behind counts:

```bash
./scripts/modpack sync-status --fetch
```

Use `--strict` in scripts or before a release if you want a non-zero exit whenever any repo is dirty, ahead, behind, missing, or missing an upstream:

```bash
./scripts/modpack sync-status --fetch --strict
```

Status meanings:

- `clean`: the working tree is clean and the branch is even with its upstream.
- `dirty:N`: there are `N` uncommitted file changes in that repo.
- `ahead:N`: the local branch has `N` commits that have not been pushed.
- `behind:N`: the remote branch has `N` commits that need to be pulled.
- `no-upstream`: the branch is not tracking a remote branch yet.
- `missing` or `not-git`: the configured source folder is absent or is not a git checkout.

## Repository Rules

- Commit pack metadata, configs, scripts, docs, and Prism instance metadata.
- Do not commit downloaded mod jars, generated runtime files, logs, worlds, screenshots, or local cache folders.
- Do not commit `tools/bin/`; recreate packwiz locally with `scripts/modpack install-packwiz`.
- Do not commit `tools/dev-env.local.json`; it is for per-machine paths and tool locations.
- Keep unpublished mod source outside this repo, normally in a folder such as `$HOME\Documents\minecraft-mod-sources`.
- Treat `minecraft/` as disposable runtime state. If something in there should be part of the pack, move it into `pack/` and let packwiz manage it.

## Third-Party Mods

Use packwiz for CurseForge and Modrinth mods so the repo stores metadata and hashes instead of binary jars.

### Prism-First Import

If you use Prism's mod browser because it is faster and nicer, download the mod into the instance first, then run:

```bash
./scripts/modpack import-prism-mods
```

The script copies jars from `minecraft/mods/` into `pack/mods/`, runs `packwiz cf detect`, and refreshes the pack index. When detection succeeds, the temporary staged jar is replaced by a `.pw.toml` metadata file. Commit the generated metadata under `pack/`.

This works best for CurseForge downloads because packwiz can fingerprint jars against CurseForge. Unmatched jars are left in the Prism instance for local testing but removed from the staged pack copy so they do not accidentally become committed pack files.

Typical flow:

```bash
cd pack
packwiz cf add <curseforge-project-slug-or-url>
../scripts/modpack refresh
git add .
git commit -m "Add <mod name>"
```

Use one change per mod group. That makes it much easier to bisect crashes and roll back a compatibility problem.

### Updating Prism From Packwiz

After pulling pack metadata from git, update the local Prism `minecraft/mods/` folder from packwiz:

```bash
./scripts/modpack update-prism-mods
```

On Windows:

```powershell
.\scripts\modpack.ps1 update-prism-mods
```

The command serves the local `pack/pack.toml` with packwiz and runs `packwiz-installer-bootstrap` against the Prism `minecraft/` directory. The bootstrap jar and downloaded installer jar live under ignored `tools/bin/`, so each machine can recreate them locally. This handles packwiz-managed third-party mods; unpublished local mods still come from `./scripts/modpack update-local-mods`.

## Local Unpublished Mods

Use two lanes:

1. Development lane: clone or pull each mod repo locally, build with its Gradle wrapper, then sync the built jar into `minecraft/mods/` with `scripts/modpack update-local-mods`.
2. Distribution lane: once a local mod has a usable test build, publish it as a GitHub Release or package artifact, then add that URL to packwiz. This keeps the pack reproducible on both machines without committing jars.

Avoid committing unpublished jars directly to the pack repo unless you explicitly want a short-lived emergency build. If you do it, remove the jar once the mod has a real release URL.

### Local Mod Source Updates

Clone missing local mod repositories and fast-forward existing checkouts:

```bash
./scripts/modpack update-repos
```

Pull, build, and copy the latest local mod jars into Prism:

```bash
./scripts/modpack update-local-mods
```

Existing dirty source checkouts are skipped by default so unfinished work is not disturbed. Use `--allow-dirty` only when you intentionally want to pull inside a checkout with local changes.

## Commit And Push Protocol

Keep the repositories synced independently:

- Pack metadata, configs, docs, scripts, and packwiz changes are committed to `DestroyerMob/MinecraftBeyond`.
- Local mod source and resource changes are committed to that mod's own repository.
- Built local jars copied into `minecraft/mods/` are runtime output and should stay ignored.

When a pack change depends on a local mod change, push the mod repo first, then commit the pack change with the mod commit hash or release tag in the commit body or pull request notes.

Typical local mod change:

```bash
git -C "$MINECRAFT_MOD_SOURCE_ROOT/MoreWeapons" status --short
git -C "$MINECRAFT_MOD_SOURCE_ROOT/MoreWeapons" add src/main/resources
git -C "$MINECRAFT_MOD_SOURCE_ROOT/MoreWeapons" commit -m "Add Better Combat battle axe profile"
git -C "$MINECRAFT_MOD_SOURCE_ROOT/MoreWeapons" push origin 1.21.1-neoforge
```

Typical pack change:

```bash
./scripts/modpack refresh
./scripts/modpack doctor --strict
git status --short
git add README.md docs/WORKFLOW.md tools scripts pack
git commit -m "Update modpack workflow tooling"
git push origin main
```

End each work session with:

```bash
./scripts/modpack sync-status --fetch
```

## Two-Machine Setup

On each machine:

1. Clone this pack repo into the Prism `instances` folder, or create a Prism instance that points at this folder.
2. Install Python 3, Java 21, Git, and Go.
3. Run `./scripts/modpack init-env` and set machine-local paths if the defaults are not right.
4. Run `./scripts/modpack doctor` or `.\scripts\modpack.ps1 doctor`.
5. Run `./scripts/modpack install-packwiz` to create `tools/bin/packwiz`.
6. Run `./scripts/modpack update-repos` to clone the local mod repos into the configured source folder.
7. Run `./scripts/modpack update-local-mods` to build and sync local mod jars.

For local mods that are private or require authentication, make sure both machines have GitHub credentials that can read the repos before relying on automation.

## Branch Protocol

- `main` should stay playable.
- Use feature branches for mod additions, config passes, and local mod integration changes.
- Commit pack changes separately from local mod source changes.
- When a pack change depends on a local mod change, mention the required mod repo commit or release tag in the pack commit or pull request.

## Release Protocol

For a playable snapshot:

1. Confirm Prism launches from a clean `minecraft/mods/`.
2. Run `./scripts/modpack refresh`.
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
