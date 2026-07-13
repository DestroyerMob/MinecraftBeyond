# Food Unification

Minecraft Beyond treats its agriculture and cooking mods as one food expansion. Duplicate items, recipes, crop sources, and fruit trees follow one priority policy instead of exposing every mod's parallel version.

## Priority

Vanilla staples remain canonical where appropriate. Food-mod duplicates then use this order:

1. Bountiful Fares
2. Farmer's Delight and its direct add-ons
3. Focused food and agriculture mods such as Let's Do, Spawn, Corn Expansion, Supplementaries, and WilderNature
4. Croptopia
5. Pam's HarvestCraft

The exact decisions live in `pack/kubejs/config/food_unification_groups.json`. Almost Unified derives its tags and per-group targets from that manifest. Pam remains installed for foods, crops, and trees that are genuinely unique.

Some higher-priority crops use their edible item as the planting item. In those cases, lower-priority seeds or saplings intentionally unify into that edible, plantable canonical item. Bountiful Fares coconut replacing lower palm saplings is one example.

## Kitchen language

Recipes use a consistent station vocabulary:

- Bountiful Fares mill: flour, meal, powders, spices, and other dry grinding.
- Farmer's Delight cooking pot: soups, stews, sauces, boiling, and other wet cooking.
- Farmer's Delight cutting board and knife: single-input cutting.
- Expanded Delight juicer: juices and pressed drinks.
- Farm & Charm stove: compact dry-cooking recipes.
- Farm & Charm roaster: skillet and frying recipes.
- Farm & Charm crafting bowl: mixing, batters, condiments, and forming foods where no dedicated press exists.
- Farm & Charm mincer: ground meat.
- Bakery tray: audited baked foods across the expansion; the tray remains as a reusable catalyst and leaves eight ingredient slots available. A full-grid bake first makes a recipe-specific mixture in the Farm & Charm bowl, so its ninth ingredient is preserved. Bakery's grilled sandwiches remain on the Farm & Charm stove.
- Bakery rolling pin: rolled dough recipes; the pin remains as a reusable catalyst.
- Crafting grid: cold assembly recipes with several already-prepared ingredients, including salads that need more room than the mixing bowl provides.

Pam tools, Croptopia's knife, press, pot, frying pan, and mortar, and the redundant Farm & Charm cooking pot are retired from recipes and hidden from recipe viewers. Their recipes are rebuilt under `minecraft_beyond:food_unification/...` IDs.

When a source recipe exceeds a station's real slot count, it first makes a recipe-specific prepared mixture or meal base in the Farm & Charm bowl. The final pot, roaster, or tray step then uses that base, so no defining ingredient is silently discarded. Specialty systems without a direct equivalent—fermentation, brewing, cheese aging, and distinctive appliances—remain native. Croptopia's generic bottled wine is the one fallback blend made in the crafting bowl because its retired press does not map to the pack's fluid-based fermentation systems.

## Crops and world generation

Exact NeoForge biome-modifier overrides suppress lower-priority duplicate crops and trees. Bountiful Fares orchards and crops win first, followed by Farmer's Delight and the focused agriculture mods. Croptopia supplies its unique plants; Pam gardens and Pam-only trees remain for diversity.

Pam's generic grass, tall-grass, and fern seed drops are disabled so lower-priority seeds do not bypass the policy. Pam gardens remain enabled, and Pam fruit trees retain right-click harvesting.

World-generation changes affect newly generated chunks. Trees and crops already present in old chunks are not removed. Existing low-priority inventory stacks also remain valid registry items; new loot and recipe outputs are what converge on the canonical versions.

## Maintenance

`pack/` is the source of truth. After changing the manifest, regenerate and validate Almost Unified's files:

```powershell
.\tools\generate-food-unification.ps1
.\tools\generate-food-unification.ps1 -Check
```

Do not hand-edit `pack/config/almostunified/tags.json`, `pack/config/almostunified/unification/food.json`, or `pack/kubejs/startup_scripts/food_unification_targets.js`; the generator owns them. After other pack changes, refresh Packwiz metadata from `pack/` and perform a clean client/world load. The KubeJS server log should contain a `[Food Unification]` summary with no generated-recipe failures, and the Almost Unified log should contain no invalid custom-tag entries.
