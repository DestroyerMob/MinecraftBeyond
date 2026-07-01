# Ecology Bee Guide

This guide explains how the Ecology bee systems work in Minecraft Beyond. It is written for players, not mod developers.

Ecology turns bees from a mostly vanilla mob into a colony system. A hive is not just a block with a few bees inside it: it can have a queen, workers, drones, traits, health, lineage, forage needs, swarming pressure, and beekeeper treatments. The important thing is that the player tools are meant to translate that complexity into understandable goals.

In Minecraft Beyond, Ecology is configured with `FULL_SIMULATION`. That means the full bee system is enabled: colony ticking, custom bee roles, worker routes, mating, queen migration, hive health, traits, relocation items, swarming, and pollination bonuses.

## The Short Version

1. Find a wild bee nest or place a beehive.
2. Use an Inspection Tray on the nest or hive to see its health, focus, issues, population, traits, and advice.
3. Use the Beekeeper's Journal on important hives to record snapshots over time.
4. To move a wild nest into your apiary, cut it out at night with a Beekeeper's Knife while the nest is smoked by a lit campfire below it.
5. Install the Brood Comb into an empty player beehive, then add captured Worker Bees if you got them.
6. Stabilize the hive with flowers, crop access, workers, brood frames, and apiary support.
7. Breed or expand good colonies with Queen Cells and Swarm Lures.
8. Use Queen Excluders when you want to prevent swarming or queen movement.
9. Build honey and pollination farms around healthy colonies.

The main loop is:

Find colony -> inspect -> relocate or stabilize -> grow -> breed/split -> manage production.

## Two Layers: Bee Simulation And Beekeeper Systems

Ecology has two different kinds of systems.

### Bee Simulation

The simulation is what bees and hives do by themselves.

- Hives track colony data.
- Bees have roles: queen, worker, or drone.
- Workers learn routes between flowers, crops, and their home hive.
- Queens and drones support reproduction.
- Colonies age, decline, recover, produce brood, and sometimes swarm.
- Traits and inbreeding affect how reliable or productive a colony is.

### Beekeeper Systems

The beekeeper systems are how you interact with the simulation.

- The Inspection Tray tells you what is happening now.
- The Beekeeper's Journal records hive snapshots.
- The Beekeeper's Knife, Brood Comb, and Worker Bee item move wild colonies into player hives.
- Queen Cells and Swarm Lures help create daughter colonies.
- Apiary tools calm, support, boost, or constrain hives.

If something fails, the item should usually tell you why: no queen, not enough workers, no empty hive nearby, low forage, swarming blocked by a queen excluder, and so on.

## Important Terms

| Term | Meaning |
| --- | --- |
| Colony | The Ecology record stored on a nest or hive. It tracks population, queen state, lineage, health, traits, and treatments. |
| Queen | The reproductive core of a colony. A colony without a queen cannot grow properly. |
| Worker | The productive caste. Workers forage, support routes, pollination, hive health, and colony growth. |
| Drone | The mating caste. Drones help queens from other colonies become fertile. |
| Forage | Nearby flowers and pollination crops that support worker routes and hive health. |
| Brood | New bees produced by the colony. Brood can fail if inbreeding is high. |
| Daughter Colony | A new colony created from an existing colony by queen cell installation or swarming. |
| Trait | An inherited colony modifier, such as Calm, Industrious, Hardy, Fertile, Long-lived, or Restless. |
| Inbreeding | Genetic pressure from related lineages. Higher inbreeding makes brood less reliable and can block safe splitting. |

## Hives, Nests, And Colony Records

Vanilla bees live in bee nests and beehives. Ecology adds a colony record on top of those blocks.

### Bee Nests

Bee nests are the wild version. They are found in the world and are the main source of starting colonies. You can inspect them, record them, cut them out, and seal old abandoned nests.

Wild nests are not where you do most managed beekeeping. For long-term apiaries, move the colony into a player beehive.

### Beehives

Beehives are the player-managed version. They are where you install brood comb, add captured workers, apply apiary treatments, prepare queen cells, lure swarms, and build farms.

Most player-facing tools expect a beehive, especially relocation tools. Brood Comb is installed into an empty player beehive, not back into a wild nest.

### Stored Bees And Visible Bees

Some bees are visible in the world. Some are stored inside the hive. Ecology tracks both the vanilla hive occupants and the colony record.

Do not panic if you see a hive message showing both colony population and stored occupants. The colony record is the long-term logical state; visible and stored bees are the physical state that moves around the world.

## Bee Roles

### Workers

Workers are the everyday useful bees. They leave the hive, visit flowers, interact with crops, and return home. Workers are the backbone of honey and pollination farms.

Workers can become defensive if a player blocks their route for too long. If you see "You are blocking this bee's route", move out of its path or redesign the farm so routes are clearer.

Ecology workers are meant to visually have no stinger. They can still defend routes as part of the system, but the visible stinger is hidden so the caste reads differently from vanilla bees.

### Drones

Drones exist for mating. They are not productive workers and are not meant to be combat bees. Drones have no visible stinger.

Drones look for compatible colonies when mating behavior is enabled. Good apiaries need more than one lineage so queens can mate without pushing the colony into unhealthy inbreeding.

### Queens

Queens keep the colony reproductive. A hive without a queen is in recovery or failure mode. Queens can age, need replacement, and may require mating support from drones of another lineage.

A queen alone is not enough. A colony also needs workers. A queen with no workers cannot run a productive hive.

## The Inspection Tray

The Inspection Tray is the main tool for understanding a hive. Use it on a nest or hive whenever you are unsure what to do next.

It reports:

- Hive position.
- Health status and score.
- Focus.
- Queen, worker, drone, and stored-bee counts.
- Traits.
- Issues.
- Active treatments.
- Advice.

### Focus

The focus line is the fastest way to know what loop you are currently in.

| Focus | What It Means | What To Do |
| --- | --- | --- |
| Relocation setup | There is no usable colony here yet, or this hive is ready to become a home. | Install brood comb, install a prepared queen cell, or start by cutting out a wild nest. |
| Colony recovery | The colony is missing something essential or is damaged. | Add a queen, add workers, stabilize forage, or replace a failed colony. |
| Population growth | The colony is alive but not strong yet. | Add forage, use brood frames, add workers, and wait for brood. |
| Breeding and splitting | The colony is crowded, aging, inbred, or ready to swarm. | Prepare a queen cell, place an empty hive nearby, use a swarm lure, or apply a queen excluder. |
| Honey and pollination | The colony is stable enough to support farms. | Expand crop layouts, add flowers, and build production around worker routes. |
| Monitoring | Nothing urgent is happening. | Record it, check it later, and improve the apiary layout. |

### Health Status

| Status | Meaning |
| --- | --- |
| Empty | No usable colony record. |
| Failing | The colony has serious problems. |
| Struggling | The colony works, but important conditions are poor. |
| Stable | The colony is healthy enough to function. |
| Thriving | The colony is in excellent shape. |

### Common Issues

| Issue | Meaning | Fix |
| --- | --- | --- |
| No colony record | Ecology does not see a real colony here. | Start one with brood comb or a prepared queen cell. |
| Abandoned hive | The old colony was cut out or abandoned. | Seal the old nest or start fresh elsewhere. |
| Cannot reproduce | The colony lacks required reproductive structure. | Restore queen and worker support. |
| Missing queen | The colony cannot grow normally. | Install brood comb with a queen or use a prepared queen cell. |
| No workers | The queen has no workforce. | Add captured workers or relocate a fuller colony. |
| Low worker count | The colony can run, but weakly. | Add workers, use brood frames, and increase forage. |
| Overcrowded | The hive is pushing toward a split. | Place an empty hive nearby, harvest a queen cell, use a swarm lure, or apply a queen excluder. |
| Inbreeding pressure | Related lineages are hurting the colony. | Introduce unrelated colonies before more breeding. |
| Queen nearing replacement | The queen is getting old. | Prepare a queen cell before the colony fails. |
| Queen needs mating | The queen needs drone support from another lineage. | Keep drones and another compatible colony nearby. |
| Low nearby forage | There are not enough flowers or crops nearby. | Plant flowers and pollination crops inside bee range. |
| Ready to swarm | The colony can create a daughter colony. | Place an empty hive nearby, use a swarm lure, or use a queen excluder to hold it. |

## The Beekeeper's Journal

The Beekeeper's Journal is for memory. Use it on a hive to record a snapshot.

It stores recent hive records, including:

- Hive position.
- Health and status.
- Population.
- Traits.
- Issues.
- Swarm readiness.
- Day recorded.

Use the journal when comparing colonies. For example, if one hive is Calm and Hardy but another is Restless and inbred, the journal helps you decide which one to breed from.

The journal is not the same as the Inspection Tray. The tray answers "what is happening right now?" The journal answers "what have I seen before?"

## Wax Goggles

Wax Goggles are for seeing worker bee routes.

Use them when:

- Workers seem to be getting stuck.
- You want to design a crop and flower farm around bee movement.
- You are getting route obstruction warnings.
- You want to understand which hive a worker belongs to.

Look at a bee to see its saved route. The route lock key is `R` by default, based on the Ecology key binding. Debug Wax Goggles are mainly for development and troubleshooting.

## Relocating A Wild Nest

Relocation is the main way to start a managed apiary from a wild colony.

### What You Need

- A wild Bee Nest with a colony.
- A Beekeeper's Knife.
- A lit campfire below the nest, close enough to smoke it.
- Nighttime.
- An empty player Beehive where the colony will move.

### Step By Step

1. Find a wild bee nest.
2. Inspect it with the Inspection Tray.
3. Wait until night. The cutout tool requires night so the bees are home.
4. Place or light a campfire under the nest so it is smoked.
5. Use the Beekeeper's Knife on the bee nest.
6. You receive a Brood Comb and, if workers were present, stacks of Worker Bee items.
7. Place an empty player beehive where you want the colony.
8. Use the Brood Comb on the empty beehive.
9. Use the captured Worker Bee items on that beehive.
10. Optionally seal the old cut-out nest with honeycomb.

### What The Brood Comb Stores

A Brood Comb can carry:

- Queen state.
- Worker count.
- Drone count.
- Lineage.
- Traits.
- Inbreeding percentage.
- Original nest position.
- Queen age.

If the Brood Comb has no queen, it cannot start a new colony by itself. It can still represent worker support, but a colony needs a queen to become stable.

### Worker Bee Items

Captured Worker Bee items are added to a hive after it has brood comb or queen-cell colony data. If a worker item says the hive needs brood, install brood comb or a queen cell first.

If the hive is full, expand carefully: too many bees can push the colony toward overcrowding and swarming pressure.

## Growing And Stabilizing A Colony

After relocation, your first goal is not breeding. It is stability.

A stable hive wants:

- A queen.
- At least a few workers.
- Nearby flowers.
- Nearby crops if you want pollination.
- Enough space.
- Low inbreeding.
- No urgent health issues.

Good early actions:

- Plant flowers near the hive.
- Put crops within worker range.
- Add captured workers from the source colony.
- Use a Hive Stand for longer support.
- Use Brood Frames if the colony needs growth.
- Keep another lineage nearby before pushing breeding too hard.

Avoid immediately splitting weak colonies. A weak split creates more weak hives and makes the system feel confusing.

## Apiary Treatments

Apiary treatments are management tools. They are not magic fixes, but they help guide the colony.

| Tool | Effect | Duration | Best Use |
| --- | --- | --- | --- |
| Apiary Smoker | Calms the hive. | 1 Minecraft day | Use before working a hive or when route defense is becoming annoying. |
| Hive Stand | Supports hive health. | 14 Minecraft days | Use on important production or breeding hives. |
| Queen Excluder | Prevents swarming and queen migration. | 14 Minecraft days | Use when you want to hold a good colony in place or stop unwanted splits. |
| Brood Frame | Gives short support and nudges brood growth. | 3 Minecraft days | Use when a colony has a queen and workers but needs population growth. |

The Apiary Smoker is reusable. Hive Stand, Queen Excluder, and Brood Frame are consumed when applied.

## Traits

Traits are inherited colony modifiers. New colonies start with one trait and sometimes a second. Daughter colonies inherit from their parent and may mutate.

| Trait | Effect |
| --- | --- |
| Calm | Bees tolerate route obstruction longer before becoming aggressive. |
| Industrious | Workers can handle more route pairs, improving farm coverage. |
| Hardy | Improves hive health. |
| Fertile | Reduces brood failure caused by inbreeding. |
| Long-lived | Bees live about one-third longer. |
| Restless | The colony pushes toward swarming sooner and has a higher swarm chance. |

Traits make colonies worth comparing. Do not treat every hive as interchangeable. A Calm, Industrious colony is excellent for busy farms. A Restless colony might be useful for expansion but harder to keep contained.

## Breeding, Mating, And Inbreeding

Ecology tracks lineage. That means breeding close relatives has consequences.

### Mating

Queens need mating support to keep producing brood. Drones help with that. A queen that needs mating will show up as an inspection issue once the colony is mature enough and trying to produce more bees.

To support mating:

- Keep multiple colonies near each other.
- Avoid making every hive a daughter of the same parent.
- Preserve strong unrelated wild colonies.
- Do not eliminate all drones from your apiary.

### Inbreeding

Inbreeding pressure makes brood less reliable. High inbreeding can also make swarming unsafe.

If inspection reports inbreeding pressure:

- Stop splitting that line for a while.
- Bring in a wild colony from elsewhere.
- Breed from a different lineage.
- Prefer colonies with healthier records in the journal.

### Brood Failure

When a colony tries to produce a new bee, brood can fail if inbreeding is high. Fertile colonies and supported hives handle this better.

This means "nothing happened today" is not always a bug. The colony may have failed brood, lacked fertility, lacked workers, lacked a queen, or simply not needed a new role yet.

## Queen Cells

Queen Cells are the controlled breeding tool.

There are two states:

- Empty Queen Cell: use it on a strong source colony to prepare queen brood.
- Prepared Queen Cell: use it on an empty beehive to start a daughter colony.

### Preparing A Queen Cell

Use an empty Queen Cell on a strong hive. The source colony must generally have:

- A colony record.
- A queen.
- At least two workers.
- Enough health.
- No doomed or abandoned state.
- A reason to raise brood.

If it fails, the item message should tell you why.

### Installing A Queen Cell

Use the prepared Queen Cell on an empty player beehive.

It starts a daughter colony with:

- A queen.
- A worker.
- Inherited lineage and traits.
- A chance for mutation.

Queen Cells are best when you want planned expansion without waiting for natural swarming.

## Swarming And Swarm Lures

Swarming is natural or player-guided colony splitting.

A colony can swarm when it is healthy, crowded, fertile enough to split safely, and has room nearby. The daughter colony moves into a nearby empty hive.

### Natural Swarming

If enabled, crowded healthy colonies can occasionally create a daughter colony on their own. Restless colonies are more likely to push toward this behavior.

### Swarm Lure

A Swarm Lure forces the question: "Can this colony split now?"

It requires:

- Swarming enabled.
- A real colony.
- A queen.
- At least two workers.
- No active queen excluder.
- No recent swarm cooldown.
- Enough crowding, or Restless near-crowding.
- Safe enough inbreeding.
- Enough nearby forage.
- An empty hive nearby.

If any requirement fails, the lure should tell you what is missing.

### Controlling Swarms

If you do not want a colony to split:

- Apply a Queen Excluder.
- Remove nearby empty hives.
- Reduce overcrowding pressure through planned queen cells.
- Keep Restless colonies away from expansion setups unless you want more colonies.

## Honey And Pollination Farms

Healthy colonies can support farms better than weak colonies.

Workers use routes involving flowers and crops. Good farm design gives them clear, nearby targets.

Tips:

- Put flowers close enough for workers to find.
- Put crops near the hive and flowers.
- Do not block narrow worker paths.
- Use Wax Goggles to see routes.
- Use Hive Stands for important production hives.
- Keep the colony stable before expecting strong output.

Healthy and thriving colonies can trigger extra crop growth when workers deliver pollen. The pack config keeps the bonus chance at `0.35`, scaled by colony condition.

## Reading Tool Failures

Most failures are instructions, not dead ends.

| Message Type | Meaning |
| --- | --- |
| Simulation disabled | The runtime config is off or the game needs a restart after config changes. |
| Wait until night | Nest cutout only works at night. |
| Smoke the nest | Put a lit campfire under the nest before cutting it out. |
| No colony to cut out | The nest has no usable colony state. |
| Brood comb has no queen | That comb cannot start a colony by itself. |
| Hive not ready | Use an empty player beehive. |
| Worker needs brood | Install brood comb or a prepared queen cell first. |
| Hive full | The hive cannot accept more bees. |
| Queen cell missing queen | The source colony needs a queen before raising queen brood. |
| Queen cell needs workers | Add or grow workers before preparing queen brood. |
| Queen cell low health | Stabilize the colony first. |
| Swarm lure not crowded | The colony is not ready to split. |
| Swarm lure low forage | Add nearby flowers and crops. |
| Swarm lure no empty hive | Place an empty hive nearby. |
| Queen excluder blocking swarming | Remove or wait out the queen excluder if you want a swarm. |

## Suggested First Apiary

This is a simple first setup that should make the systems readable.

1. Place 2 to 4 player beehives with a little space between them.
2. Put flowers nearby.
3. Put a small crop patch nearby.
4. Use Wax Goggles later to see whether workers are finding both.
5. Relocate one wild nest into the first hive.
6. Add its captured workers.
7. Inspect the hive.
8. If focus says growth, use a Brood Frame and improve forage.
9. If focus says production, expand crops.
10. If focus says breeding and splitting, place an empty hive nearby and decide between Queen Cell, Swarm Lure, or Queen Excluder.
11. Bring in a second wild colony from farther away before doing a lot of breeding.

## Example Player Stories

### "I Found A Good Wild Nest"

Inspect it. If it has strong health or useful traits, cut it out at night with smoke. Install the Brood Comb into a player hive, add the workers, and record it in the journal.

### "My Hive Has A Queen But No Workers"

This is recovery. Add captured workers if you have them. If not, you may need to relocate another colony or use a prepared queen cell in an empty hive instead of trying to save a queen-only hive.

### "My Hive Is Stable But Not Producing Much"

This is growth or production. Add flowers, add crops, check routes with Wax Goggles, and consider a Hive Stand. If workers are low, use a Brood Frame.

### "My Colony Is Ready To Swarm"

Decide whether you want expansion.

If yes, place an empty hive nearby and use a Swarm Lure, or wait for natural swarming.

If no, apply a Queen Excluder.

### "My Colonies Are Getting Inbred"

Stop breeding that family line. Relocate a new wild colony from somewhere else. Use the journal to track which colonies came from which sources.

## Configuration Notes

Minecraft Beyond currently uses:

- `gameplayPreset = "FULL_SIMULATION"`
- Bee system enabled.
- Hive ticking enabled.
- Custom bee goals enabled.
- Bee lifespan death enabled.
- Drone mating enabled.
- Queen migration enabled.
- Relocation items enabled.
- Hive health enabled.
- Pollination bonus enabled.
- Colony traits enabled.
- Swarming enabled.
- Debug logging disabled.
- Auto-seeded empty hives disabled.

If the game says "Ecology bee simulation is disabled in the config", check both the shipped pack config and the live runtime config:

- `pack/config/ecology-common.toml`
- `minecraft/config/ecology-common.toml`

After changing config, fully restart Minecraft.

## Troubleshooting

### The journal or tray says simulation is disabled

Restart the game after config changes. If it still happens, check `minecraft/config/ecology-common.toml`; NeoForge reads the live runtime config from there.

### A hive has no colony record

It may be empty, vanilla-only, newly placed, or not initialized. Start a colony with brood comb or a prepared queen cell.

### Workers are angry

You may be blocking their route. Use Wax Goggles, widen paths, move crops or flowers, or apply an Apiary Smoker.

### Nothing is breeding

Check for queen, workers, fertility, inbreeding, forage, brood need, and health. Use the Inspection Tray first.

### Swarm Lure fails

Read the exact message. Most failures are fixable: add an empty hive, add forage, wait out cooldown, remove queen excluder, or let the colony grow.

### A wild nest cutout fails

Make sure it is night, the nest is smoked by a lit campfire below it, and the nest has a colony.

## Final Advice

Do not run an apiary by guessing. Inspect often, record good colonies, and treat breeding like a lineage system rather than a simple duplication system.

The strongest colonies are not just the biggest. A good colony is healthy, well-fed, supported by workers, low in inbreeding, and useful for the job you want it to do.
