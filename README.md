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
- `scripts/` contains local setup helpers for checking the workspace and syncing locally built mod jars into the Prism instance.

## Packwiz Setup

Install Go once, then install packwiz into the repo-local tool folder:

```powershell
scoop install go
.\scripts\Install-Packwiz.ps1
```

The scripts prefer `tools/bin/packwiz.exe` and fall back to `packwiz` on PATH.

## Local Mods

| Mod | Repo | Branch | Notes |
| --- | --- | --- | --- |
| Ecology | `DestroyerMob/ecology` | `main` | NeoForge 1.21.1, currently aligned with NeoForge 21.1.234. |
| MoreWeapons | `DestroyerMob/MoreWeapons` | `1.21.1-neoforge` | Default branch is old Forge 1.20.1; use this branch for the pack. |
| Better Enchanting | `DestroyerMob/BetterEnchants` | `main` | NeoForge 1.21.1, currently on NeoForge 21.1.228. |
| Auric | `DestroyerMob/Auric` | `main` | NeoForge 1.21.1, early development. |
| Mobs Tool Forging | `DestroyerMob/MobsToolForging` | `main` | NeoForge 1.21.1, currently on NeoForge 21.1.233. |

## First Commands

Check the local workspace:

```powershell
.\scripts\Test-ModpackWorkspace.ps1
```

After downloading CurseForge mods through Prism, import the downloaded jars into packwiz metadata:

```powershell
.\scripts\Import-PrismMods.ps1
```

Clone or pull all local mod source repositories:

```powershell
.\scripts\Update-LocalModRepos.ps1
```

Pull the local mod repos, build them, and sync their jars into the local Prism instance:

```powershell
.\scripts\Update-PackLocalMods.ps1
```

The update script copies jars into `minecraft/mods/`, which is ignored by git. The pack repo should track metadata and config, not generated jars.
