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
- `MINECRAFT_BEYOND_PRISM_SHADERPACKS_DIR`
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
- Do not commit `minecraft/mods/*-local.jar` or `pack/mods/*-local.jar`; local jars are either rebuilt per machine or represented by packwiz release metadata.
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

Local runtime jars named `*-local.jar` are always skipped by this importer, even if the old `--include-local` flag is passed. Promote a local mod through the release metadata flow below instead.

### Shaderpacks

Shaderpacks use the same packwiz idea as mods: commit metadata, not downloaded zip files. If you install shaders with Prism, Prism can leave `.pw.toml` metadata in `minecraft/shaderpacks/`. Sync that metadata into the distributable pack with:

```bash
./scripts/modpack import-prism-shaderpacks
```

The command copies shader metadata into `pack/shaderpacks/`, warns about loose shader zip files or extracted shader folders that are not packwiz-managed, and refreshes the pack index. Commit the generated `.pw.toml` files and `pack/index.toml`.

After pulling shader metadata on another machine, apply it to the Prism instance with either command:

```bash
./scripts/modpack update-prism-mods
./scripts/modpack update-prism-shaderpacks
```

Both use the same packwiz installer path. The shader-specific command is only a clearer alias when you are thinking about shaders.

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

The command serves the local `pack/pack.toml` with packwiz and runs `packwiz-installer-bootstrap` against the Prism `minecraft/` directory. The bootstrap jar and downloaded installer jar live under ignored `tools/bin/`, so each machine can recreate them locally. This handles packwiz-managed third-party mods, configs, and shaderpacks; unpublished local mods still come from `./scripts/modpack update-local-mods`.

After packwiz finishes, the command restores the local Mod Quality Picker `activeProfileId` and re-applies that preset to `minecraft/mods/`. This matters because packwiz manages downloaded files, while Mod Quality Picker manages local runtime state by renaming jars between `.jar` and `.jar.disabled`.

For a normal two-machine sync, prefer:

```bash
./scripts/modpack sync-instance
```

That command runs the packwiz update first, then runs `update-local-mods`. The order keeps generated `*-local.jar` files local: packwiz can clean the metadata-owned file set, and then the local source builds are copied back into Prism.

Quality presets that should ship with the pack live in `pack/config/modqualitypicker/presets/`. If you edit a preset in-game or under `minecraft/config/modqualitypicker/presets/`, run `./scripts/modpack sync-quality-presets --profile <profileId>` to promote that runtime copy into the bundled pack metadata and refresh the packwiz index. Use `--include-defaults` only when you intentionally want to ship captured config baselines as well.

### Capturing Prism Changes Into The Pack

When you have been making normal instance-side changes through Prism or in-game menus, use the combined capture command:

```bash
./scripts/modpack capture-instance
```

It imports Prism mod jars through packwiz CurseForge detection, copies Prism shaderpack `.pw.toml` metadata into `pack/shaderpacks/`, syncs Mod Quality Picker presets into `pack/config/modqualitypicker/presets/`, and runs one final `packwiz refresh`.

Use these options when you need a narrower capture:

```bash
./scripts/modpack capture-instance --profile balanced
./scripts/modpack capture-instance --skip-mods
./scripts/modpack capture-instance --include-quality-defaults
```

Review the resulting git diff before committing. Unmatched Prism jars are removed from the staged pack copy by default so loose downloads do not accidentally become committed pack files.

## Local Unpublished Mods

Use two lanes:

1. Development lane: clone or pull each mod repo locally, build with its Gradle wrapper, then sync the built jar into `minecraft/mods/` with `scripts/modpack update-local-mods`.
2. Distribution lane: once a local mod has a usable test build, publish it as a GitHub Release or package artifact, then add that URL to packwiz. This keeps the pack reproducible on both machines without committing jars.

Avoid committing unpublished jars directly to the pack repo. If a build needs to be shared between machines without rebuilding, publish a real artifact and pin its URL plus hash in metadata.

### Release Metadata For Local Mods

Each entry in `tools/local-mods.json` has a `pack` block that names the packwiz metafile and runtime filename. While a mod is source-only, that block has no `download` entry and no `.pw.toml` file is generated for it.

When a local mod is published, add a pinned direct-download block:

```json
"pack": {
  "metafile": "mods/auric.pw.toml",
  "filename": "auric-local.jar",
  "side": "both",
  "download": {
    "url": "https://github.com/DestroyerMob/Auric/releases/download/<tag>/auric-local.jar",
    "hashFormat": "sha512",
    "hash": "<sha512>"
  }
}
```

Then generate packwiz metadata:

```bash
./scripts/modpack write-local-mod-releases --mod auric
```

Commit the generated `pack/mods/*.pw.toml`, `pack/index.toml`, `pack/pack.toml`, and the manifest change. Do not commit the jar.

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

Local mods can be marked with `enabled: false` in `tools/local-mods.json`. Disabled entries remain documented, but local update and sync commands skip them.

Local mod sync also re-applies the active Mod Quality Picker preset after copying jars. Use `--skip-quality-apply` only when you intentionally want to inspect the raw synced jar set before the quality preset renames files.

## Commit And Push Protocol

Keep the repositories synced independently:

- Pack metadata, configs, docs, scripts, and packwiz changes are committed to `DestroyerMob/MinecraftBeyond`.
- Local mod source and resource changes are committed to that mod's own repository.
- Built local jars copied into `minecraft/mods/` are runtime output and should stay ignored.
- Published local-mod builds should enter the pack through packwiz `.pw.toml` metadata with a pinned URL and hash.

When a pack change depends on a local mod change, push the mod repo first, then commit the pack change with the mod commit hash or release tag in the commit body or pull request notes.

Typical local mod change:

```bash
git -C "$MINECRAFT_MOD_SOURCE_ROOT/MoreWeapons" status --short
git -C "$MINECRAFT_MOD_SOURCE_ROOT/MoreWeapons" add src/main/resources
git -C "$MINECRAFT_MOD_SOURCE_ROOT/MoreWeapons" commit -m "Add Punchy battle axe animation profile"
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

For a guided sweep across the pack repo and configured local mod repos:

```bash
./scripts/modpack publish-dirty-repos
```

The command only acts on dirty repositories. For each one, it prints `git status --short`, asks for a commit message, runs `git add .`, commits, and pushes the current branch. Leave the message blank to skip that repository.

Useful narrower variants:

```bash
./scripts/modpack publish-dirty-repos --local-mods-only
./scripts/modpack publish-dirty-repos --pack-only
./scripts/modpack publish-dirty-repos --no-push
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
7. Run `./scripts/modpack sync-instance` to apply pack metadata, then build and sync local mod jars.

For local mods that are private or require authentication, make sure both machines have GitHub credentials that can read the repos before relying on automation.

Daily two-machine sync:

```bash
git pull --ff-only
./scripts/modpack sync-instance
./scripts/modpack sync-status --fetch
```

## Branch Protocol

- `main` should stay playable.
- Use feature branches for mod additions, config passes, and local mod integration changes.
- Commit pack changes separately from local mod source changes.
- When a pack change depends on a local mod change, mention the required mod repo commit or release tag in the pack commit or pull request.

## Release Protocol

For a playable snapshot:

1. Confirm Prism launches from a clean `minecraft/mods/`.
2. Publish any local mod jars needed for distribution as GitHub Releases or packages.
3. Run `./scripts/modpack write-local-mod-releases --require-all` if the snapshot should be installable without local source builds.
4. Run `./scripts/modpack refresh`.
5. Tag the pack repo, for example `pack-v0.1.0`.
6. Export `.mrpack` or CurseForge zip only after the pack works through packwiz install/update.

## Compatibility Notes

- The Prism instance currently uses NeoForge 21.1.234.
- Most local mod repositories target NeoForge 21.1.234.
- Axiom Survival is a Fabric 1.21.1 Axiom add-on for Sinytra Connector. The pack config enables its survival capture hooks.
- MoreWeapons must use the `1.21.1-neoforge` branch for this pack.
