# Minecraft Beyond Quest Book

The FTB Quests book is an invitation into the pack, not a linear campaign or a replacement for JEI. It begins with flint knapping and modular tools, then opens into mostly parallel feature chapters. The Ender Dragon gates only the outer-End chapter.

## Chapter structure

1. Hands Before Tools
2. A Working Forge
3. Fight With Intent
4. Meals, Not Hunger
5. A Wider World
6. Essence & Practical Magic
7. Storage & Logistics
8. The Dragon Is a Door
9. Beyond the Dragon

The main teaching spine is flint knapping, a modular pick, and the first workshop. It gates only subjects that genuinely assume forged equipment. Cooking, storage, exploration, and practical magic can otherwise be learned in any order.

The book deliberately does not give every installed mod its own card. Supporting mods appear when they create a meaningful moment in the larger journey; their full catalogues belong in JEI/EMI and their own guidebooks.

## Quest design

The book teaches by arranging things to do, not by reproducing mod manuals. A quest should normally ask for one observable action or outcome. Its task gives the exact requirement; its title and description should make that requirement feel worth pursuing.

- Write in a warm, confident field-guide voice. Give the player a reason, image, consequence, or small moment of discovery instead of restating the task card.
- Use one short paragraph, normally no more than 25 words. The generator enforces an absolute 40-word limit.
- Avoid catalogue copy and repeated openings such as “Build,” “Make,” or “Use.” Name a mod only when that name genuinely helps the player find something.
- Remove a quest if its only purpose is to advertise that an item exists. A shorter chapter with a visible learning arc is better than complete mod coverage.
- Give each quest one task representing the outcome; use dependencies to express a sequence instead of turning one card into a checklist.
- Leave recipes, workstation sequences, filter syntax, statistics, and exhaustive feature lists to JEI/EMI, Jade, tooltips, and per-mod guidebooks.
- Avoid click-through chapter introductions and tasks such as "begin the lesson" or "read this page." Start with the first real action.
- Prefer item, advancement, observation, statistic, kill, biome, structure, and dimension tasks. If FTB cannot verify an outcome honestly, fold the lesson into a nearby concrete quest or remove it.
- Keep optional feature branches optional. A capstone should prove the core loop, not require every side feature.
- Treat the installed recipes, advancements, guidebooks, and live mechanics as authoritative. A registered item ID is not proof that a feature is active; reserved compatibility scaffolding must never become a quest objective.

## Authoring model

The readable source of truth is [`tools/generate_ftb_quests.py`](../tools/generate_ftb_quests.py). It owns the chapter graph, prose, positions, tasks, rewards, and deterministic IDs. Generated files live under `pack/config/ftbquests/quests/` and are shipped by packwiz.

Do not hand-edit the generated SNBT. Make a change in the generator and run:

```bash
python3 tools/generate_ftb_quests.py --validate-instance minecraft --sync-instance
./scripts/modpack refresh
python3 tools/generate_ftb_quests.py --check --validate-instance minecraft
```

The generator rejects duplicate or invalid IDs, unsupported task types, overlapping quest positions, missing dependencies, dependency cycles, anything other than one task per quest, overlong descriptions, invalid rewards, unexpected generated files, and referenced items, advancements, blocks, biomes, or structures absent from the installed instance. Quest, task, and reward IDs are stable hashes of their semantic keys; renaming a key intentionally creates a new progress identity.

`--sync-instance` copies the same generated files into the ignored local Prism runtime at `minecraft/config/ftbquests/quests/`. It refuses to overwrite that directory if it contains extra SNBT files, protecting in-game authoring experiments from silent deletion.

## Task policy

- Use item tasks for ordinary, statically registered items.
- Use native advancements when a mod already observes the exact interaction.
- Use observation tasks for stations created or placed directly in the world, so players do not have to break them for inventory detection.
- Use statistics, kills, biomes, structures, and dimensions only when their completion condition truthfully matches the quest title.
- Do not use manual checkmarks. Subjective builds, timing windows, configuration choices, and advice belong in adjacent descriptions or mod guidebooks instead of self-certified tasks.
- Every quest declares its own modest, relevant item reward. Rewards must not come from rotating chapter palettes: reordering quests should never change what they give.
- The book gives no XP rewards and avoids finished tools, major stations, Elytra, Nether Stars, and other progression shortcuts.

## In-game verification

After launching a test world, run:

```text
/ftbquests reload quests
```

Check the game log for load or missing-registry errors, then visually inspect chapter layout, dependency lines, wrapped descriptions, icons, item rewards, and task completion. The generated SNBT is also canonical comma-separated SNBT and can be parsed by Minecraft's `TagParser` during development.
