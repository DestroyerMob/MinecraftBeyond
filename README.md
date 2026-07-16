# Minecraft Beyond

Minecraft Beyond is an in-development Minecraft 1.21.1 survival modpack for Prism Launcher. It keeps the vanilla adventure loop recognizable while adding deeper toolmaking, deterministic enchanting, posture-driven combat, village and bee simulation, exploration, food, building, and presentation upgrades.

The pack is also the integration environment for ten local projects. Those mods are developed in separate repositories, built into this instance for playtesting, and connected here through configs, tags, loot data, recipes, compatibility data, and Mod Quality Picker profiles.

Current target:

- Minecraft: 1.21.1
- Loader: NeoForge 21.1.234
- Pack manager: packwiz
- Launcher: Prism Launcher
- Local Java: 21

## Pack Direction

- **Progression:** Mobs Tool Forging replaces direct equipment recipes with physical knapping, pattern making, heating, forging, lapidary work, leatherworking, modular assembly, and repair.
- **Combat and equipment:** MoreWeapons supplies additional weapon families, Mobs Combat adds posture/guard/parry/stealth/dual-wield systems, and Better Enchanting makes enchantment selection essence- and tag-driven.
- **Living world:** Ecology remains an experimental future pillar for advanced apiculture and settlement systems. It is disabled by the recommended Balanced preset because of its performance cost, while the player-facing quality menu exposes Light and Full opt-in modes. Worldgen, structure, creature, farming, food, and furniture mods broaden exploration and everyday survival in the meantime.
- **Magic and building:** Auric adds potion utility, imbuing, camouflage, builder storage, sculk experience tools, and small magical discoveries.
- **Presentation and scalability:** shader, sound, animation, UI, controller, map, performance, and quality-profile tooling let the same pack target different machines and play styles.

This is an internal playtesting pack rather than a finished public release. Local mod balance, art, compatibility, and distribution packaging are still evolving.

## Repository Layout

- `pack/` is the packwiz pack root. Third-party mod and shaderpack metadata, configs, KubeJS/data files, default options, and export metadata live there.
- `minecraft/` is the local Prism game directory. It is intentionally ignored except for `.gitkeep`; generated `minecraft/mods/*-local.jar` files are runtime output.
- Mod Quality Picker presets and composable feature groups are bundled under `pack/config/modqualitypicker/` and indexed by packwiz like quests/configs.
- `tools/local-mods.json` records unpublished local mods, their expected branches/jar names, and optional release download pins for packwiz metadata.
- `tools/modpack.py` is the cross-platform workspace command used by macOS, Linux, and Windows.
- `modqualitypicker-local.jar` is self-contained: the same jar supplies the in-game menu and the Java pre-launch applier used by Prism.
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
| `publish-dirty-repos` | Interactively run `git add .`, commit, and push dirty pack/local mod repos after prompting for each commit message. | `--pack-only`, `--local-mods-only`, `--include-disabled`, `--no-push`, `--dry-run` |
| `update-repos` | Clone missing local mod repos or fast-forward existing checkouts. | `--source-root`, `--skip-pull`, `--allow-dirty`, `--dry-run` |
| `sync-local-mods` | Copy built local mod jars into the Prism mods folder, then re-apply the active Mod Quality Picker preset. | `--source-root`, `--mods-dir`, `--build`, `--skip-quality-apply`, `--dry-run` |
| `apply-quality-profile` | Apply the queued or active Mod Quality Picker profile; used by Prism before launch. | `--instance-root`, `--world-id`, `--dry-run`, `--keep-pending` |
| `update-local-mods` | Pull local mod repos, build them, sync their jars into Prism, then re-apply the active Mod Quality Picker preset. | `--source-root`, `--mods-dir`, `--skip-pull`, `--skip-build`, `--allow-dirty`, `--skip-quality-apply`, `--dry-run` |
| `write-local-mod-releases` | Write packwiz `.pw.toml` files for local mods that have pinned release downloads in `tools/local-mods.json`. | `--mod`, `--include-disabled`, `--require-all`, `--skip-refresh`, `--dry-run` |
| `sync-instance` | Apply packwiz metadata to Prism, then pull/build/sync local mod jars in the safe order for a machine. | `--skip-prism`, `--skip-local`, `--skip-pull`, `--skip-build`, `--allow-dirty`, plus update/sync path options |
| `capture-instance` | Import Prism-side mod jars, shaderpack metadata, and Mod Quality Picker presets into `pack/`, then refresh packwiz once. | `--profile`, `--include-quality-defaults`, `--skip-mods`, `--skip-shaderpacks`, `--skip-quality-presets`, `--dry-run` |
| `import-prism-mods` | Import Prism-downloaded third-party jars through packwiz CurseForge detection, then refresh the index. Local runtime jars are always skipped. | `--prism-mods-dir`, `--pack-dir`, `--packwiz`, `--keep-unmatched-staged-jars`, `--skip-refresh`, `--dry-run` |
| `import-prism-shaderpacks` | Import Prism shaderpack `.pw.toml` metadata into `pack/shaderpacks/`, warn about unmanaged shader files, then refresh the index. | `--prism-shaderpacks-dir`, `--pack-dir`, `--packwiz`, `--skip-refresh`, `--dry-run` |
| `sync-quality-presets` | Copy in-instance Mod Quality Picker presets, feature groups, and feature overlays into bundled pack metadata, then refresh the index. | `--profile`, `--include-defaults`, `--skip-refresh`, `--dry-run` |
| `update-prism-mods` | Apply `pack/pack.toml` back into the local Prism `minecraft/` folder using packwiz installer, then re-apply the active Mod Quality Picker preset. | `--minecraft-dir`, `--mods-dir`, `--pack-dir`, `--packwiz`, `--java-home`, `--installer`, `--main-jar`, `--bootstrap-url`, `--no-download`, `--port`, `--skip-quality-apply`, `--dry-run` |
| `update-prism-shaderpacks` | Clearer alias for applying packwiz metadata to Prism when you are thinking about shaderpack changes. | same installer/path options as `update-prism-mods` |
| `refresh` | Run `packwiz refresh` for the pack. | `--pack-dir`, `--packwiz` |
| `verify-fresh-install` | Install the Packwiz-managed pack into an empty temporary Minecraft directory to catch unavailable downloads and fresh-machine failures. | `--keep`, plus update/install path options |

## Packwiz Setup

Install Go once, then install packwiz into the repo-local tool folder:

```bash
./scripts/modpack install-packwiz
```

The tools prefer an explicitly configured `packwiz`, then `tools/bin/packwiz(.exe)`, then `packwiz` on PATH.

## Local Mods

| Mod | Repo | Branch | Notes |
| --- | --- | --- | --- |
| Ecology | `DestroyerMob/ecology` | `main` | Opt-in bee-colony simulation plus village ecology, households, supplies, construction crews, markets, currencies, and guard integration. Requires Villager Names 8.5+; disabled in Balanced and exposed as experimental Light/Full quality choices. |
| MoreWeapons | `DestroyerMob/MoreWeapons` | `1.21.1-neoforge` | Great swords, katanas, battle axes, knives, and machetes with Punchy animation metadata and data bridges for Mobs Tool Forging and Better Enchanting. The default branch is old Forge 1.20.1; use this branch for the pack. |
| Mobs Combat | `DestroyerMob/MobsCombat` | `main` | Server-authoritative posture, guard, timed block, parry, stealth, recovery, dual-wield, Punchy animation, and Jade/Apotheosis inspection support with data-driven entity and weapon profiles. |
| Better Enchanting | `DestroyerMob/BetterEnchants` | `main` | Deterministic essence-, book-, item-, and tag-driven enchanting with custom enchantments, datapack limits/fusions, a JEI enchantment guide, modular-tool routing, and Apothic Enchanting support. |
| Auric | `DestroyerMob/Auric` | `main` | Potion cauldrons and candles, item imbuing, camouflage and palette tools, sculk XP bottles, Sword in Stone shrines, and Jade potion-cauldron diagnostics. |
| Mobs Tool Forging | `DestroyerMob/MobsToolForging` | `main` | Physical modular tool and armour progression covering knapping, patterns, heat, forging, gem shells, leatherworking, drying, assembly, repair, workmanship quality, layered visuals, JEI, and Jade. |
| Mobs Storage | `DestroyerMob/MobsStorage` | `main` | Safe visual storage filters, anchor-limited storage networks, searchable crafting terminals, automation ports, refills, and inventory controls. |
| Mod Quality Picker | `DestroyerMob/ModQualityPicker` | `main` | Working per-profile mod/config selection loop with in-game editing, world mismatch handling, dependency validation, Prism pre-launch application, config baselines/diffs, and pack export. |
| Dev Tools | `DestroyerMob/DevTools` | `main` | Pack-only testing helpers: Lootr chest placement/retargeting/rerolling and opt-in final/raw damage diagnostics. |

## Mod Integrations

- Better Enchanting includes explicit support for Apotheosis and the Apothic Enchanting module. The pack currently tracks Apotheosis `1.21.1-8.5.4` and Apothic Enchanting `1.21.1-1.5.3`.
- MoreWeapons owns bridge data for its Mobs Tool Forging weapon parts and Better Enchanting routes, while Mobs Combat recognizes the shared weapon tags and coordinates dual-wield visuals with Punchy.
- Mobs Tool Forging converts compatible loot equipment after Apotheosis affixes are applied, and the pack removes direct vanilla armour and MoreWeapons recipes so the physical equipment loop remains authoritative.
- Dev Tools is a development dependency only; its Lootr and damage diagnostics are intended for pack testing, not normal progression.
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

After editing presets in-game or under `minecraft/config/modqualitypicker/presets/`, promote those runtime edits into the bundled pack metadata:

```bash
./scripts/modpack sync-quality-presets --profile balanced
```

To capture the usual Prism-side changes in one pass before committing the pack repo, run:

```bash
./scripts/modpack capture-instance
```

This imports Prism-downloaded mod jars through packwiz, copies shaderpack `.pw.toml` metadata, syncs all Mod Quality Picker presets, and refreshes `pack/index.toml` once. Add `--include-quality-defaults` only when you intentionally want to promote runtime default config baselines too.

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

For an interactive sweep across dirty repos:

```bash
./scripts/modpack publish-dirty-repos
```

The command prints each dirty repo's short status, asks for a commit message, runs `git add .`, commits, and pushes the current branch. Leave a message blank to skip that repo.
