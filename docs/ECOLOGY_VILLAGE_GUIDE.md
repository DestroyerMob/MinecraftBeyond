# Ecology Village Guide

Village Ecology gives villages a readable settlement-health layer. Use a Village Ledger near a village to survey food, shelter, safety, green space, water, and upkeep.

The village stores its own hidden ecology and supply ledger automatically. The crafted Village Ledger item is only the player-facing tool for reading that state, donating supplies, adopting villagers into a new bell-centered village, and planning market stalls. Player-built villages work too, as long as they have the normal things villagers need: beds, a bell or gathering space, safe paths, work areas, and optional market stalls.

## What The Score Means

- Neglected: many basic settlement needs are missing.
- Struggling: the village works, but several categories need attention.
- Stable: the village is generally healthy.
- Thriving: the village is well supported and resilient.

## Categories

- Food: crops, mature crops, composters, water, and farmers.
- Shelter: beds, doors, job blocks, and bells.
- Safety: golems, bells, lighting, and hostile pressure.
- Green space: flowers, saplings, and leaves.
- Water: wells, ponds, farm water, and canals.
- Upkeep: paths, composters, bells, job blocks, and empty farmland.

## Villager Upkeep

Adult villagers occasionally perform small maintenance actions:

- Farmers can replant empty farmland with wheat.
- Villagers can patch dirt or grass gaps next to existing dirt paths.
- Villagers can plant small flowers near paths, bells, or composters.

This is intentionally gentle. It should make villages feel cared for without replacing player building.

## Village Vocations

Ecology can assign professions to jobless adult villagers so village roles feel less like a workstation race.

- Babies remember their parents' professions.
- When a baby grows up, it is more likely to choose one of those parent professions.
- Village needs can bend the result: low food favors farmers and fishermen, low safety favors armorers and weaponsmiths, and low upkeep favors masons and toolsmiths.
- There is still a smaller random chance so villages do not become completely predictable.

Ecology does not overwrite nitwits, babies, villagers that already have a profession, or villagers with trade XP.

## Village Supplies

Village Supplies make trading feel like part of the village economy without turning villages into a heavy simulation.

Villagers still trade normally. The supply ledger is an invisible village account behind those trades. It tracks:

- Food
- Wood
- Stone
- Metal
- Paper
- Cloth
- Tools
- Medicine
- Valuables

Professions and village health change those supplies over time. Farmers, fishermen, and butchers support food. Masons support stone. Librarians and cartographers support paper. Shepherds and leatherworkers support cloth. Armorers, toolsmiths, and weaponsmiths make tool supply but consume metal. Clerics support medicine.

Trades react to those supplies:

- If a village has high supply for an item type, related trades can have more uses before restocking.
- If a village has low supply, related trades have fewer uses and exhaust faster.
- If the player sells useful items to a villager, that can add to the village's supply.
- If the player buys useful items from a villager, that draws down the matching supply.

The Village Ledger shows each supply as `0-100` plus a daily trend. Negative daily trends mean the village is slowly using more than it produces. Positive trends mean the village can recover over time.

Unloaded villages do not keep ticking. Instead, Ecology stores the last update time and catches up the next time the village is loaded, inspected, or traded with. Catch-up is capped, so villages can recover while unloaded but cannot become infinite resource machines.

## Market Welfare

Trading halls are allowed, but Ecology treats a good trading hall as a market, not a cage.

A proper market lets villagers:

- Reach a home or bed area.
- Reach a meeting space such as a bell.
- Reach their work or stall.
- Leave their stall and return later.

If a villager is repeatedly confined, Ecology starts treating that trader as unhealthy:

- The villager stops contributing profession supply to the market.
- Trades with that villager do not improve village supplies.
- High-supply market bonuses do not apply to that villager.
- Prices climb while the confinement pressure remains high.
- The Village Ledger reports confined traders as a market issue.

This is forgiving by design. A temporary obstruction or one failed path check should not matter. A sealed cell that keeps failing access checks will.

## Market Stalls

Use the Village Ledger to assign villagers to market stalls.

1. Build a stall tile the villager can stand on.
2. Crouch-use the Village Ledger on that tile with your other hand empty.
3. Use the ledger on a villager to assign the marked stall.
4. The villager will try to walk to that stall during work hours.
5. Crouch-use the ledger on the villager to clear the assignment.

This means a trading hall can be a real market: villagers commute to stalls instead of being stored in cells. If the route is blocked, the ledger will still assign the stall, but the villager may build welfare pressure until the path is fixed.

A plain ledger click on a villager still opens normal trading. The ledger only takes over that click when it already has a marked stall to assign, or when you crouch-use it to clear a villager's assigned stall.

## Relocating Villagers

Ecology supports player-made villages, but it does not teleport villagers for you. Bring the villager to the new settlement first, then adopt them into it.

1. Build the new village with a bell, beds, paths, and work areas.
2. Crouch-use the Village Ledger on the bell.
3. Use the marked ledger on a villager.
4. If the villager is far away, it starts following you toward the marked village.
5. Once the villager reaches the bell area, Ecology adopts it into the village.

Vanilla transport still works too: boats, minecarts, nether routes, curing a zombie villager near the village, or breeding villagers in place. Guided relocation is for moving a specific villager without building a transport machine every time. Crouch-use the ledger on a guided villager to stop guiding it.

The villager follows while it can path to you. When it arrives, it remembers that bell as its meeting point, forgets old home and job memories, and tries to bind to nearby beds and matching workstations. This also moves the villager onto the new village's currency and supply account.

## Tradeboards

Tradeboards let you define player-stocked villager offers through a real shop surface.

1. Place `ecology:tradeboard` blocks in a filled rectangle from 1x1 up to 15x15.
2. Use an item stack on a board tile to set what that slot sells. The stack count becomes the output count.
3. Use the village currency on that tile to set the price. The currency stack count becomes the cost.
4. Crouch-use a Village Ledger on the tradeboard.
5. Crouch-use the same ledger on an input inventory.
6. Crouch-use the same ledger on a different output inventory.
7. Use the completed ledger on an adult, non-confined villager.

The villager removes sold stock from the input inventory and deposits paid currency into the output inventory. If stock runs out, the offer disappears on refresh. Confined villagers do not use tradeboards.

## Donating Supplies

Crouch-use the Village Ledger while holding a donation item in your other hand.

Examples:

- Wheat, carrots, potatoes, fish, and meat add food.
- Logs, planks, sticks, and saplings add wood.
- Cobblestone, stone, bricks, and clay add stone.
- Iron, copper, gold, coal, and ores add metal.
- Paper and books add paper.
- Wool, string, leather, hides, and feathers add cloth.
- Tools, weapons, flint, and arrows add tools.
- Honey bottles, golden carrots, spider eyes, rabbit feet, blaze powder, and bonemeal add medicine.
- Emeralds, diamonds, lapis, quartz, amethyst, ruby, and sapphire-like gem items add valuables.

## Village Currencies

Villages can use emerald, or tagged ruby/sapphire items from another mod, as their local trade currency. A village chooses one available currency for the whole settlement, so villagers in the same village should not be mixed.

- Emerald villages use normal emerald trades and normal villager clothing.
- Ruby villages use a tagged ruby item anywhere a villager trade would normally use emerald.
- Sapphire villages use a tagged sapphire item anywhere a villager trade would normally use emerald.

Selling goods to a ruby or sapphire village gives you that village currency, and buying goods from that village costs that same currency.

Ruby and sapphire villages only enter the rotation when the matching item tags are populated. Ecology checks `ecology:village_currency/ruby`, `c:gems/ruby`, `forge:gems/ruby`, and the matching sapphire variants.

## Golem Construction

Village health lightly affects Ecology's golem construction system. Thriving villages can start construction with one fewer participant and build a little faster. Neglected villages build a little slower.

## Improving A Village

Use the Village Ledger first, then fix the weakest category:

- Low food: add farms, composters, water, and farmers.
- Poor shelter: add beds, doors, job blocks, and a bell.
- Low safety: improve lighting and protect or replace golems.
- Low green space: plant flowers, saplings, hedges, and gardens.
- Low water: add wells, ponds, canals, or farm water.
- Low upkeep: add paths, composters, bells, and workstations.
