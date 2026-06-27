# Minecraft Beyond

Minecraft Beyond is being set up as a vanilla enhanced Minecraft 1.21.1 modpack for Prism Launcher.

Current target:

- Minecraft: 1.21.1
- Loader: NeoForge 21.1.234
- Pack manager: packwiz
- Launcher: Prism Launcher
- Local Java: 21

## Repository Layout

- `pack/` is the future packwiz pack root. Third-party mods, configs, resource packs, default options, and export metadata should live there.
- `minecraft/` is the local Prism game directory. It is intentionally ignored except for `.gitkeep`.
- `tools/local-mods.json` records the unpublished local mods and their expected branches/jar names.
- `tools/modpack.py` is the cross-platform workspace command used by macOS, Linux, and Windows.
- `tools/dev-env.example.json` is the template for optional machine-local paths.
- `scripts/` contains portable wrappers plus the original PowerShell helpers.

## Local Environment

Use the portable `modpack` wrapper as the main entry point:

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

For machine-specific paths, generate the local config and edit it locally:

```bash
./scripts/modpack init-env
```

`tools/dev-env.local.json` is ignored by git. It can set:

- `sourceRoot`: where unpublished mod source repositories live.
- `modsDir`: the Prism mods folder to sync local jars into.
- `packwiz`: a repo-local or system packwiz executable.
- `javaHome`: a Java 21 installation.

Environment variables override the local config:

- `MINECRAFT_MOD_SOURCE_ROOT`
- `MINECRAFT_BEYOND_PRISM_MODS_DIR`
- `MINECRAFT_BEYOND_PACKWIZ` or `PACKWIZ`
- `MINECRAFT_BEYOND_JAVA_HOME` or `JAVA_HOME`

## Packwiz Setup

Install Go once, then install packwiz into the repo-local tool folder:

```bash
./scripts/modpack install-packwiz
```

The tools prefer an explicitly configured `packwiz`, then `tools/bin/packwiz(.exe)`, then `packwiz` on PATH.

## Local Mods

| Mod | Repo | Branch | Notes |
| --- | --- | --- | --- |
| Ecology | `DestroyerMob/ecology` | `main` | NeoForge 1.21.1, currently aligned with NeoForge 21.1.234. |
| MoreWeapons | `DestroyerMob/MoreWeapons` | `1.21.1-neoforge` | Default branch is old Forge 1.20.1; use this branch for the pack. |
| Better Enchanting | `DestroyerMob/BetterEnchants` | `main` | NeoForge 1.21.1, currently on NeoForge 21.1.228. |
| Auric | `DestroyerMob/Auric` | `main` | NeoForge 1.21.1, early development. |
| Mobs Tool Forging | `DestroyerMob/MobsToolForging` | `main` | NeoForge 1.21.1, currently on NeoForge 21.1.233. |
| Mod Quality Picker | `DestroyerMob/ModQualityPicker` | `main` | NeoForge 1.21.1, early scaffold for per-world quality/mod/config profiles. |

## First Commands

Check the local workspace:

```bash
./scripts/modpack doctor
```

After downloading CurseForge mods through Prism, import the downloaded jars into packwiz metadata:

```bash
./scripts/modpack import-prism-mods
```

After pulling packwiz metadata from git, apply it back into the local Prism instance:

```bash
./scripts/modpack update-prism-mods
```

On Windows, the equivalent command is:

```powershell
.\scripts\modpack.ps1 update-prism-mods
```

This command starts a temporary local packwiz server, downloads `packwiz-installer-bootstrap.jar` into ignored `tools/bin/` if needed, and updates `minecraft/mods/` from `pack/pack.toml`.

Clone or pull all local mod source repositories:

```bash
./scripts/modpack update-repos
```

Check whether the pack repo and all configured local mod repos are clean and synced:

```bash
./scripts/modpack sync-status --fetch
```

Pull the local mod repos, build them, and sync their jars into the local Prism instance:

```bash
./scripts/modpack update-local-mods
```

The update script copies jars into `minecraft/mods/`, which is ignored by git. The pack repo should track metadata and config, not generated jars.

## Keeping Remotes Current

There are separate repositories involved here:

- Pack changes live in this repo, `DestroyerMob/MinecraftBeyond`.
- Local mod source changes live in each mod's own repo, such as `DestroyerMob/MoreWeapons`.
- Built `*-local.jar` files in `minecraft/mods/` are local runtime output and should not be committed.

Before and after a work session, run:

```bash
./scripts/modpack sync-status --fetch
```

If a local mod changed, commit and push that mod repo first. Then commit and push the pack repo, mentioning the mod commit or release when the pack depends on it.
