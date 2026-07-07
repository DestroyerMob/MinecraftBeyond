# Minecraft Beyond

Minecraft Beyond is being set up as a vanilla enhanced Minecraft 1.21.1 modpack for Prism Launcher.

Current target:

- Minecraft: 1.21.1
- Loader: NeoForge 21.1.234
- Pack manager: packwiz
- Launcher: Prism Launcher
- Local Java: 21

## Repository Layout

- `pack/` is the packwiz pack root. Third-party mod and shaderpack metadata, configs, KubeJS/data files, default options, and export metadata live there.
- `minecraft/` is the local Prism game directory. It is intentionally ignored except for `.gitkeep`; generated `minecraft/mods/*-local.jar` files are runtime output.
- Mod Quality Picker presets are bundled pack data under `pack/config/modqualitypicker/presets/` and indexed by packwiz like quests/configs.
- `tools/local-mods.json` records unpublished local mods, their expected branches/jar names, and optional release download pins for packwiz metadata.
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
- `shaderpacksDir`: the Prism shaderpacks folder to import local packwiz shader metadata from.
- `packwiz`: a repo-local or system packwiz executable.
- `javaHome`: a Java 21 installation.

Environment variables override the local config:

- `MINECRAFT_MOD_SOURCE_ROOT`
- `MINECRAFT_BEYOND_PRISM_MODS_DIR`
- `MINECRAFT_BEYOND_PRISM_SHADERPACKS_DIR`
- `MINECRAFT_BEYOND_PACKWIZ` or `PACKWIZ`
- `MINECRAFT_BEYOND_JAVA_HOME` or `JAVA_HOME`

## Modpack Command Reference

Run commands through the portable wrapper:

```bash
./scripts/modpack <command> [options]
```

On Windows, use `.\scripts\modpack.ps1 <command>` or `scripts\modpack.cmd <command>`.
Every command supports `--help`.

| Command | Purpose | Useful options |
| --- | --- | --- |
| `doctor` | Check tools, Java, packwiz metadata, repo state, Prism mods/shaderpacks, and local mod sources. | `--strict`, `--source-root`, `--mods-dir`, `--shaderpacks-dir`, `--packwiz`, `--java-home` |
| `install-packwiz` | Install packwiz into ignored `tools/bin/` using Go. | `--install-dir`, `--module` |
| `init-env` | Create ignored `tools/dev-env.local.json` for machine-local paths. | `--source-root`, `--mods-dir`, `--shaderpacks-dir`, `--packwiz`, `--java-home`, `--force` |
| `sync-status` | Show dirty/ahead/behind status for the pack repo and configured local mod repos. | `--source-root`, `--fetch`, `--strict` |
| `update-repos` | Clone missing local mod repos or fast-forward existing checkouts. | `--source-root`, `--skip-pull`, `--allow-dirty`, `--dry-run` |
| `sync-local-mods` | Copy built local mod jars into the Prism mods folder, then re-apply the active Mod Quality Picker preset. | `--source-root`, `--mods-dir`, `--build`, `--skip-quality-apply`, `--dry-run` |
| `update-local-mods` | Pull local mod repos, build them, sync their jars into Prism, then re-apply the active Mod Quality Picker preset. | `--source-root`, `--mods-dir`, `--skip-pull`, `--skip-build`, `--allow-dirty`, `--skip-quality-apply`, `--dry-run` |
| `write-local-mod-releases` | Write packwiz `.pw.toml` files for local mods that have pinned release downloads in `tools/local-mods.json`. | `--mod`, `--include-disabled`, `--require-all`, `--skip-refresh`, `--dry-run` |
| `sync-instance` | Apply packwiz metadata to Prism, then pull/build/sync local mod jars in the safe order for a machine. | `--skip-prism`, `--skip-local`, `--skip-pull`, `--skip-build`, `--allow-dirty`, plus update/sync path options |
| `import-prism-mods` | Import Prism-downloaded third-party jars through packwiz CurseForge detection, then refresh the index. Local runtime jars are always skipped. | `--prism-mods-dir`, `--pack-dir`, `--packwiz`, `--keep-unmatched-staged-jars`, `--dry-run` |
| `import-prism-shaderpacks` | Import Prism shaderpack `.pw.toml` metadata into `pack/shaderpacks/`, warn about unmanaged shader files, then refresh the index. | `--prism-shaderpacks-dir`, `--pack-dir`, `--packwiz`, `--skip-refresh`, `--dry-run` |
| `update-prism-mods` | Apply `pack/pack.toml` back into the local Prism `minecraft/` folder using packwiz installer, then re-apply the active Mod Quality Picker preset. | `--minecraft-dir`, `--mods-dir`, `--pack-dir`, `--packwiz`, `--java-home`, `--installer`, `--main-jar`, `--bootstrap-url`, `--no-download`, `--port`, `--skip-quality-apply`, `--dry-run` |
| `update-prism-shaderpacks` | Clearer alias for applying packwiz metadata to Prism when you are thinking about shaderpack changes. | same installer/path options as `update-prism-mods` |
| `refresh` | Run `packwiz refresh` for the pack. | `--pack-dir`, `--packwiz` |

## Packwiz Setup

Install Go once, then install packwiz into the repo-local tool folder:

```bash
./scripts/modpack install-packwiz
```

The tools prefer an explicitly configured `packwiz`, then `tools/bin/packwiz(.exe)`, then `packwiz` on PATH.

## Local Mods

| Mod | Repo | Branch | Notes |
| --- | --- | --- | --- |
| Ecology | `DestroyerMob/ecology` | `main` | NeoForge 1.21.1, currently aligned with NeoForge 21.1.234. Requires Villager Names 8.5+, which the pack includes. Advanced bee simulation is config-gated and off by default. |
| MoreWeapons | `DestroyerMob/MoreWeapons` | `1.21.1-neoforge` | NeoForge 1.21.1, currently aligned with NeoForge 21.1.234. Default branch is old Forge 1.20.1; use this branch for the pack. Includes Mobs Tool Forging and Better Enchanting bridge data. |
| Better Enchanting | `DestroyerMob/BetterEnchants` | `main` | NeoForge 1.21.1, currently aligned with NeoForge 21.1.234. Includes explicit Apotheosis/Apothic Enchanting support. |
| Auric | `DestroyerMob/Auric` | `main` | NeoForge 1.21.1, currently aligned with NeoForge 21.1.234. Early development. |
| Mobs Tool Forging | `DestroyerMob/MobsToolForging` | `main` | NeoForge 1.21.1, currently aligned with NeoForge 21.1.234. |
| Mod Quality Picker | `DestroyerMob/ModQualityPicker` | `main` | NeoForge 1.21.1, currently aligned with NeoForge 21.1.234. Early scaffold for per-world quality/mod/config profiles. |
| Axiom Survival | `DestroyerMob/AxiomSurvival` | `main` | Fabric 1.21.1 add-on for Axiom. Survival capture hooks are enabled by pack config. |

## Mod Integrations

- Better Enchanting includes explicit support for Apotheosis and the Apothic Enchanting module. The pack currently tracks Apotheosis `1.21.1-8.5.4` and Apothic Enchanting `1.21.1-1.5.3`.
- Axiom Survival stages Axiom edits behind survival inventory costs when `enableAxiomVanillaEditCapture` is enabled before launch.
- Ecology's player-facing bee systems are documented in [docs/ECOLOGY_BEE_GUIDE.md](docs/ECOLOGY_BEE_GUIDE.md).
- Ecology's village systems are documented in [docs/ECOLOGY_VILLAGE_GUIDE.md](docs/ECOLOGY_VILLAGE_GUIDE.md).

## First Commands

Check the local workspace:

```bash
./scripts/modpack doctor
```

After downloading CurseForge mods through Prism, import the downloaded jars into packwiz metadata:

```bash
./scripts/modpack import-prism-mods
```

After adding shaderpacks through Prism, import the Prism-side packwiz shader metadata into the pack:

```bash
./scripts/modpack import-prism-shaderpacks
```

After pulling packwiz metadata from git, apply it back into the local Prism instance:

```bash
./scripts/modpack update-prism-mods
```

On Windows, the equivalent command is:

```powershell
.\scripts\modpack.ps1 update-prism-mods
```

This command starts a temporary local packwiz server, downloads `packwiz-installer-bootstrap.jar` into ignored `tools/bin/` if needed, and updates `minecraft/mods/` from `pack/pack.toml`. After packwiz finishes, it restores the local `activeProfileId` and runs the Mod Quality Picker applier so any jars restored by packwiz are renamed back to the active quality preset before Minecraft launches.

For a full machine sync, run the combined command instead. It applies packwiz first, then builds and copies local source jars so packwiz does not remove machine-local runtime output after the local sync:

```bash
./scripts/modpack sync-instance
```

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

The update script copies jars into `minecraft/mods/`, which is ignored by git, then re-applies the active Mod Quality Picker preset. The pack repo should track metadata and config, not generated jars.

When a local mod has a published artifact that both machines should install without building from source, add its direct download URL and hash under that mod's `pack.download` entry in `tools/local-mods.json`, then run:

```bash
./scripts/modpack write-local-mod-releases --mod <modId>
```

Commit the generated `.pw.toml` metadata and refreshed pack index, not the jar.

## Keeping Remotes Current

There are separate repositories involved here:

- Pack changes live in this repo, `DestroyerMob/MinecraftBeyond`.
- Local mod source changes live in each mod's own repo, such as `DestroyerMob/MoreWeapons`.
- Built `*-local.jar` files in `minecraft/mods/` are local runtime output and are ignored.
- Published local-mod builds should enter the pack through packwiz `.pw.toml` metadata with a pinned URL and hash.

Before and after a work session, run:

```bash
./scripts/modpack sync-status --fetch
```

If a local mod changed, commit and push that mod repo first. Then commit and push the pack repo, mentioning the mod commit or release when the pack depends on it.
