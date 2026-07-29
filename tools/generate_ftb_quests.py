#!/usr/bin/env python3
"""Generate, validate, and synchronize the Minecraft Beyond FTB Quests book."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence


REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_ROOT = REPO_ROOT / "pack" / "config" / "ftbquests" / "quests"
INSTANCE_ROOT = REPO_ROOT / "minecraft" / "config" / "ftbquests" / "quests"
RESOURCE_ID = re.compile(r"^[a-z0-9_.-]+:[a-z0-9_./-]+$")
HEX_ID = re.compile(r"^[0-7][0-9A-F]{15}$")
FTB_FORMATTING_SUFFIX = re.compile(r"(?:[0-9a-fklmnorz]|#[0-9A-Fa-f]{6})")
QUEST_BOOK_TITLE = "&b&lMinecraft Beyond&r"
RESERVED_QUEST_TARGETS: dict[str, str] = {
    "mobstoolforging:flint_shard": "normal flint is knapped directly",
    "mobstoolforging:crucible": "reserved casting scaffold",
    "mobstoolforging:smithing_hammer_head": "internal workshop component",
    "mobstoolforging:smithing_hammer_head_pattern": "internal workshop component",
    "mobstoolforging:screwdriver": "obsolete scaffold",
    "mobstoolforging:screwdriver_head": "obsolete scaffold",
    "mobstoolforging:screwdriver_head_pattern": "obsolete scaffold",
    "mobstoolforging:gem_cutters_knife": "internal lapidary component",
    "mobstoolforging:gem_cutters_blade": "internal lapidary component",
    "mobstoolforging:gem_cutters_blade_pattern": "internal lapidary component",
}


@dataclass(frozen=True)
class Task:
    kind: str
    value: str
    count: int = 1
    title: str = ""
    option: str = ""
    timer: int = 0
    components: tuple[tuple[str, object], ...] = ()
    match_components: str = ""
    only_from_crafting: bool = False


@dataclass(frozen=True)
class Reward:
    resource_id: str
    count: int = 1
    components: tuple[tuple[str, object], ...] = ()


@dataclass(frozen=True)
class Quest:
    key: str
    title: str
    description: tuple[str, ...]
    icon: str
    tasks: tuple[Task, ...]
    reward: Reward
    parents: tuple[str, ...] = ()
    subtitle: str = ""
    col: float = 0.0
    row: float = 0.0
    shape: str = "circle"
    size: float = 1.0


@dataclass(frozen=True)
class Chapter:
    key: str
    filename: str
    group: str
    title: str
    subtitle: str
    icon: str
    quests: tuple[Quest, ...]


@dataclass(frozen=True)
class ChapterGroup:
    key: str
    title: str


def item(
    resource_id: str,
    count: int = 1,
    title: str = "",
    *,
    components: dict[str, object] | None = None,
    match_components: str = "",
    only_from_crafting: bool = False,
) -> Task:
    return Task(
        "item",
        resource_id,
        count,
        title,
        components=tuple((components or {}).items()),
        match_components=match_components,
        only_from_crafting=only_from_crafting,
    )


def advancement(resource_id: str) -> Task:
    return Task("advancement", resource_id)


def dimension(resource_id: str) -> Task:
    return Task("dimension", resource_id)


def kill(resource_id: str, count: int = 1) -> Task:
    return Task("kill", resource_id, count)


def stat(resource_id: str, value: int = 1) -> Task:
    return Task("stat", resource_id, value)


def biome(resource_id: str) -> Task:
    return Task("biome", resource_id)


def structure(resource_id: str) -> Task:
    return Task("structure", resource_id)


def observe(observation_type: str, resource_id: str, timer: int = 20) -> Task:
    return Task("observation", resource_id, option=observation_type, timer=timer)


def prize(
    resource_id: str,
    count: int = 1,
    *,
    components: dict[str, object] | None = None,
) -> Reward:
    return Reward(resource_id, count, tuple((components or {}).items()))


def quest(
    key: str,
    title: str,
    description: str,
    icon: str,
    task: Task,
    reward: Reward,
    *,
    parents: Sequence[str] = (),
    col: float = 0.0,
    row: float = 0.0,
    shape: str = "circle",
    size: float = 1.0,
) -> Quest:
    return Quest(
        key,
        title,
        (description,),
        icon,
        (task,),
        reward,
        tuple(parents),
        col=col,
        row=row,
        shape=shape,
        size=size,
    )


GROUPS = (
    ChapterGroup("start_here", "&b&lStart Here"),
    ChapterGroup("beyond_systems", "&6&lPack Pillars"),
    ChapterGroup("life_and_home", "&a&lLife on the Road"),
    ChapterGroup("wide_world", "&d&lBeyond the Horizon"),
)


CHAPTERS: tuple[Chapter, ...] = (
    Chapter(
        "hands",
        "hands_before_tools",
        "start_here",
        "&6Hands Before Tools",
        "Flint becomes a tool; a tool becomes a workshop",
        "mobstoolforging:toolmakers_bench",
        (
            quest(
                "knap_flint",
                "Flint Remembers a Shape",
                "Work an ordinary piece of flint until a pickaxe head emerges.",
                "mobstoolforging:pickaxe_head",
                item(
                    "mobstoolforging:pickaxe_head",
                    components={
                        "mobstoolforging:tool_part": {
                            "part_type": "pickaxe_head",
                            "material_id": "mobstoolforging:flint",
                        }
                    },
                    match_components="fuzzy",
                ),
                prize(
                    "patchouli:guide_book",
                    components={"patchouli:book": "mobstoolforging:forgemasters_guide"},
                ),
                col=0,
                row=0,
                shape="hexagon",
                size=1.5,
            ),
            quest(
                "toolmakers_station",
                "Give Every Part a Place",
                "The Toolmaker's Station is where loose pieces finally become useful.",
                "mobstoolforging:toolmakers_bench",
                item("mobstoolforging:toolmakers_bench"),
                prize("minecraft:stick", 8),
                parents=("knap_flint",),
                col=2,
                row=0,
            ),
            quest(
                "flint_pick",
                "Your First Proper Tool",
                "Fit the flint head to a handle. The stone age is brief, but it matters.",
                "mobstoolforging:pickaxe",
                item("mobstoolforging:pickaxe"),
                prize("minecraft:torch", 16),
                parents=("toolmakers_station",),
                col=4,
                row=0,
                shape="diamond",
                size=1.5,
            ),
            quest(
                "smithing_hammer",
                "A Hammer With Ambition",
                "This is more than a striking tool. It is the key to the workshop ahead.",
                "mobstoolforging:smithing_hammer",
                item("mobstoolforging:smithing_hammer"),
                prize("minecraft:charcoal", 8),
                parents=("flint_pick",),
                col=6,
                row=-1,
            ),
            quest(
                "pattern_station",
                "Teach Wood to Remember",
                "Build a Pattern Creation Station and turn blank boards into repeatable ideas.",
                "mobstoolforging:pattern_creation_station",
                item("mobstoolforging:pattern_creation_station"),
                prize("minecraft:oak_planks", 8),
                parents=("flint_pick",),
                col=6,
                row=1,
            ),
            quest(
                "first_pattern",
                "Plan the Blade",
                "Commit a sword blade to wood before committing metal to the fire.",
                "mobstoolforging:sword_blade_pattern",
                item("mobstoolforging:sword_blade_pattern"),
                prize("minecraft:raw_iron", 3),
                parents=("pattern_station",),
                col=8,
                row=1,
            ),
            quest(
                "crude_anvil",
                "Wake the Stone",
                "Raise a Crude Anvil from the ground. Your workshop now has a heartbeat.",
                "mobstoolforging:crude_anvil",
                item("mobstoolforging:crude_anvil"),
                prize("minecraft:coal", 8),
                parents=("smithing_hammer", "first_pattern"),
                col=10,
                row=0,
                shape="rsquare",
                size=1.5,
            ),
        ),
    ),
    Chapter(
        "workshop",
        "the_workshop",
        "beyond_systems",
        "&6A Working Forge",
        "Shape, fit, improve, and finally cast",
        "mobstoolforging:tool_forge",
        (
            quest(
                "shape_head",
                "Metal Takes an Edge",
                "Heat and hammer a sword blade from the pattern you prepared.",
                "mobstoolforging:sword_blade",
                item("mobstoolforging:sword_blade"),
                prize("minecraft:leather", 2),
                parents=("hands/crude_anvil",),
                col=0,
                row=0,
                shape="hexagon",
                size=1.5,
            ),
            quest(
                "assemble_metal_tool",
                "Fit for a Fight",
                "Bring blade, guard, and handle together. The result should feel entirely yours.",
                "mobstoolforging:sword",
                item("mobstoolforging:sword"),
                prize("minecraft:cooked_beef", 4),
                parents=("shape_head",),
                col=2,
                row=0,
            ),
            quest(
                "smithing_anvil",
                "Outgrow the Crude Anvil",
                "Raise a Smithing Anvil and give ironwork the foundation it deserves.",
                "mobstoolforging:tool_forge",
                item("mobstoolforging:tool_forge"),
                prize("minecraft:iron_ingot", 2),
                parents=("assemble_metal_tool",),
                col=4,
                row=0,
                shape="rsquare",
                size=1.5,
            ),
            quest(
                "heating_forge",
                "Hold the Heat",
                "A Heating Forge keeps difficult work hot long enough to finish it properly.",
                "mobstoolforging:heating_forge",
                observe("block", "mobstoolforging:heating_forge"),
                prize("minecraft:coal", 8),
                parents=("smithing_anvil",),
                col=6,
                row=0,
            ),
            quest(
                "lapidary_work",
                "A Diamond Skin",
                "Coat an iron sword blade with diamond while the metal is hot.",
                "mobstoolforging:sword_blade",
                item(
                    "mobstoolforging:sword_blade",
                    components={
                        "mobstoolforging:tool_part": {
                            "part_type": "sword_blade",
                            "material_id": "mobstoolforging:diamond",
                            "coating_base_material": "mobstoolforging:iron",
                        }
                    },
                    match_components="fuzzy",
                ),
                prize("minecraft:lapis_lazuli", 8),
                parents=("heating_forge",),
                col=8,
                row=1,
                shape="diamond",
                size=1.5,
            ),
            quest(
                "leather_station",
                "The Other Half of Armour",
                "Metal protects the hard points. A Leather Station prepares everything between them.",
                "mobstoolforging:leather_station",
                observe("block", "mobstoolforging:leather_station"),
                prize("minecraft:leather", 4),
                parents=("hands/crude_anvil",),
                col=0,
                row=3,
            ),
            quest(
                "modular_armour",
                "Made to Fit",
                "Assemble a modular chestplate from pieces you prepared yourself.",
                "mobstoolforging:modular_chestplate",
                item("mobstoolforging:modular_chestplate"),
                prize("minecraft:iron_ingot", 4),
                parents=("leather_station", "shape_head"),
                col=2,
                row=3,
            ),
            quest(
                "foundry_root",
                "Build Around the Flame",
                "Complete a working foundry. The guidebook has the shape; you supply the scale.",
                "mobstoolforging:foundry_forge",
                advancement("mobstoolforging:foundry/root"),
                prize("minecraft:brick", 16),
                parents=("heating_forge",),
                col=8,
                row=-2,
                shape="gear",
                size=1.5,
            ),
            quest(
                "first_cast",
                "A Shape Worth Keeping",
                "Make a reusable gold cast from a finished tool part.",
                "mobstoolforging:casting_mold",
                advancement("mobstoolforging:foundry/first_cast"),
                prize("minecraft:gold_ingot", 2),
                parents=("foundry_root",),
                col=10,
                row=-2,
            ),
            quest(
                "bronze_age",
                "Two Metals, One Answer",
                "Let copper and tin leave the foundry as bronze.",
                "mobstoolforging:bronze_ingot",
                advancement("mobstoolforging:foundry/bronze_age"),
                prize("minecraft:copper_ingot", 4),
                parents=("first_cast",),
                col=12,
                row=-3,
            ),
            quest(
                "steel_age",
                "Iron, Reconsidered",
                "Add carbon, control the heat, and cast your first steel ingot.",
                "mobstoolforging:steel_ingot",
                advancement("mobstoolforging:foundry/steel_age"),
                prize("minecraft:coal", 8),
                parents=("first_cast",),
                col=12,
                row=-1,
            ),
            quest(
                "netherite_mastery",
                "The Foundry's Measure",
                "Carry netherite and a reusable cast together. The whole chain is now yours.",
                "minecraft:netherite_ingot",
                advancement("mobstoolforging:foundry/netherite_mastery"),
                prize("minecraft:netherite_scrap"),
                parents=("bronze_age", "steel_age"),
                col=14,
                row=-2,
                shape="pentagon",
                size=1.5,
            ),
        ),
    ),
    Chapter(
        "combat",
        "fight_with_intent",
        "beyond_systems",
        "&cFight With Intent",
        "Control space, guard, and distance",
        "minecraft:shield",
        (
            quest(
                "posture",
                "Control the Pace",
                "Five zombies are enough to learn when to press and when to recover.",
                "minecraft:iron_sword",
                kill("minecraft:zombie", 5),
                prize("minecraft:cooked_beef", 4),
                parents=("hands/flint_pick",),
                col=0,
                row=0,
                shape="hexagon",
                size=1.5,
            ),
            quest(
                "guard",
                "Spend the Shield, Not Yourself",
                "Block a serious hit. Guard is a resource, not permission to stand still.",
                "minecraft:shield",
                stat("minecraft:damage_blocked_by_shield", 10),
                prize("minecraft:iron_ingot", 2),
                parents=("hands/flint_pick",),
                col=0,
                row=-2,
            ),
            quest(
                "reach",
                "Choose the Distance",
                "Assemble an iron spear and make enemies fight on your terms.",
                "mobsmoreweapons:iron_spear",
                item("mobsmoreweapons:iron_spear"),
                prize("minecraft:string", 6),
                parents=("posture",),
                col=2,
                row=0,
                shape="diamond",
                size=1.5,
            ),
            quest(
                "ranged",
                "Not Far Enough",
                "A skeleton fifty blocks away still thinks it is safe. Correct it.",
                "minecraft:bow",
                advancement("minecraft:adventure/sniper_duel"),
                prize("minecraft:arrow", 32),
                parents=("posture",),
                col=4,
                row=0,
            ),
        ),
    ),
    Chapter(
        "meals",
        "meals_not_hunger",
        "life_and_home",
        "&aMeals, Not Hunger",
        "Prepare food worth carrying",
        "farmersdelight:cooking_pot",
        (
            quest(
                "cutting_board",
                "Use the Whole Harvest",
                "Put a Cutting Board to work and discover what careful preparation leaves behind.",
                "farmersdelight:cutting_board",
                advancement("farmersdelight:main/use_cutting_board"),
                prize("minecraft:bone_meal", 8),
                col=0,
                row=0,
                shape="hexagon",
                size=1.5,
            ),
            quest(
                "cooking_pot",
                "Dinner Has a Memory",
                "Cook beef stew. A proper meal should stay with you after the bowl is empty.",
                "farmersdelight:beef_stew",
                item("farmersdelight:beef_stew"),
                prize("minecraft:carrot", 8),
                parents=("cutting_board",),
                col=2,
                row=0,
                shape="diamond",
                size=1.5,
            ),
        ),
    ),
    Chapter(
        "world",
        "a_wider_world",
        "wide_world",
        "&dA Wider World",
        "Leave a trail, then follow curiosity",
        "naturescompass:naturescompass",
        (
            quest(
                "map",
                "Leave a Trail Home",
                "Fill a map before familiar ground disappears behind the horizon.",
                "minecraft:filled_map",
                item("minecraft:filled_map"),
                prize("minecraft:paper", 8),
                col=0,
                row=0,
                shape="hexagon",
                size=1.5,
            ),
            quest(
                "nature_compass",
                "Ask the Landscape",
                "Craft a Nature's Compass and let a named biome become a direction.",
                "naturescompass:naturescompass",
                item("naturescompass:naturescompass"),
                prize("minecraft:cooked_beef", 4),
                parents=("map",),
                col=2,
                row=-2,
            ),
            quest(
                "caves",
                "Where Stone Blooms",
                "Find the Lost Caves and the strange life growing beneath the overworld.",
                "minecraft:spore_blossom",
                biome("yungscavebiomes:lost_caves"),
                prize("minecraft:torch", 16),
                parents=("nature_compass",),
                col=4,
                row=-2,
            ),
            quest(
                "structures",
                "A Door Below",
                "Cross the threshold of a small dungeon and meet what the surface forgot.",
                "minecraft:chiseled_stone_bricks",
                structure("betterdungeons:small_dungeon"),
                prize("minecraft:torch", 16),
                parents=("map",),
                col=2,
                row=0,
            ),
            quest(
                "lootr",
                "A Share of Your Own",
                "Open a Lootr chest. Its contents belong to you without costing another traveller.",
                "lootr:lootr_chest",
                advancement("lootr:1chest"),
                prize("minecraft:emerald", 2),
                parents=("structures",),
                col=4,
                row=0,
            ),
            quest(
                "archaeology",
                "Stories in the Dust",
                "Brush a pottery sherd from suspicious ground and carry one old story forward.",
                "minecraft:brush",
                advancement("minecraft:adventure/salvage_sherd"),
                prize("minecraft:clay_ball", 8),
                parents=("structures",),
                col=4,
                row=2,
            ),
            quest(
                "photograph",
                "Bring Back Proof",
                "Take a photograph of something the road would otherwise keep.",
                "exposure:camera",
                advancement("exposure:adventure/exposure"),
                prize("minecraft:glow_ink_sac", 2),
                parents=("map",),
                col=2,
                row=2,
                shape="diamond",
                size=1.5,
            ),
        ),
    ),
    Chapter(
        "magic",
        "essence_and_practical_magic",
        "beyond_systems",
        "&5Essence \\& Practical Magic",
        "Make strange forces answer useful questions",
        "betterenchanting:attunement_focus",
        (
            quest(
                "focus",
                "Tune In",
                "Craft an Attunement Focus. Enchanting becomes clearer when you can hear its choices.",
                "betterenchanting:attunement_focus",
                item("betterenchanting:attunement_focus"),
                prize("minecraft:amethyst_shard", 4),
                col=0,
                row=-2,
                shape="hexagon",
                size=1.5,
            ),
            quest(
                "crucible",
                "What Matter Leaves Behind",
                "Build an Arcane Crucible and draw useful nature from ordinary things.",
                "betterenchanting:arcane_crucible",
                item("betterenchanting:arcane_crucible"),
                prize("minecraft:glass_bottle", 3),
                parents=("focus",),
                col=2,
                row=-2,
            ),
            quest(
                "first_essence",
                "The Shape of Strength",
                "Distil Essence of Force. The other essences are yours to discover.",
                "betterenchanting:physical_essence",
                item("betterenchanting:physical_essence"),
                prize("minecraft:lapis_lazuli", 8),
                parents=("crucible",),
                col=4,
                row=-2,
            ),
            quest(
                "enhanced_table",
                "Enchant With Intent",
                "Use essence to choose an enchantment instead of accepting a roll of the dice.",
                "minecraft:enchanting_table",
                stat("minecraft:enchant_item"),
                prize("minecraft:bookshelf", 2),
                parents=("first_essence",),
                col=6,
                row=-2,
                shape="diamond",
                size=1.5,
            ),
            quest(
                "pedestal",
                "Refine What Is Written",
                "Build an Attunement Pedestal and push one existing enchantment further.",
                "betterenchanting:attunement_pedestal",
                item("betterenchanting:attunement_pedestal"),
                prize("minecraft:lapis_lazuli", 8),
                parents=("enhanced_table",),
                col=8,
                row=-2,
            ),
            quest(
                "imbuing_table",
                "Magic Beyond the Bottle",
                "Raise an Imbuing Table and carry potion effects into lasting objects.",
                "auric:imbuing_table",
                observe("block", "auric:imbuing_table"),
                prize("minecraft:glass_bottle", 6),
                col=0,
                row=1,
                shape="hexagon",
                size=1.5,
            ),
            quest(
                "modular_imbue",
                "Temper It Against Fire",
                "Imbue a sword blade with Fire Resistance before giving it a handle.",
                "mobstoolforging:sword_blade",
                item(
                    "mobstoolforging:sword_blade",
                    components={
                        "auric:imbue": {
                            "effect": "minecraft:fire_resistance",
                            "source_level": 1,
                        }
                    },
                    match_components="fuzzy",
                ),
                prize("minecraft:magma_cream", 2),
                parents=("imbuing_table", "workshop/shape_head"),
                col=2,
                row=1,
                shape="diamond",
                size=1.5,
            ),
            quest(
                "shrine",
                "A Blade That Waited",
                "Find a Forgotten Blade Shrine. Some weapons prefer to choose their owner.",
                "auric:sword_in_stone",
                structure("auric:forgotten_blade_shrine"),
                prize("minecraft:golden_apple"),
                col=0,
                row=3,
                shape="pentagon",
                size=1.5,
            ),
        ),
    ),
    Chapter(
        "storage",
        "storage_and_logistics",
        "beyond_systems",
        "&6Storage \\& Logistics",
        "Name the network, then give items a path",
        "mobsstorage:network_wand",
        (
            quest(
                "labels",
                "Name What You Keep",
                "Make four Storage Labels. A network begins with containers it can recognise.",
                "mobsstorage:storage_label",
                item("mobsstorage:storage_label", 4),
                prize("minecraft:item_frame", 4),
                col=0,
                row=0,
                shape="hexagon",
                size=1.5,
            ),
            quest(
                "wand",
                "Draw the Connections",
                "Craft a Network Wand and turn separate containers into one system.",
                "mobsstorage:network_wand",
                item("mobsstorage:network_wand"),
                prize("minecraft:redstone", 8),
                parents=("labels",),
                col=2,
                row=0,
            ),
            quest(
                "interface",
                "One Window, Every Chest",
                "Build a Network Interface and search the whole system from one place.",
                "mobsstorage:network_interface",
                item("mobsstorage:network_interface"),
                prize("minecraft:iron_ingot", 4),
                parents=("wand",),
                col=4,
                row=0,
                shape="diamond",
                size=1.5,
            ),
            quest(
                "network_input",
                "Send the Work Home",
                "Add a Network Input so machines can place finished work into storage.",
                "mobsstorage:network_input",
                item("mobsstorage:network_input"),
                prize("minecraft:hopper", 2),
                parents=("interface",),
                col=6,
                row=-1,
            ),
            quest(
                "network_output",
                "Let the Workshop Reach In",
                "Add a Network Output so machines can draw ingredients from storage.",
                "mobsstorage:network_output",
                item("mobsstorage:network_output"),
                prize("minecraft:chest", 4),
                parents=("interface",),
                col=6,
                row=1,
            ),
        ),
    ),
    Chapter(
        "dragon",
        "the_dragon_is_a_door",
        "wide_world",
        "&5The Dragon Is a Door",
        "The old ending opens the next journey",
        "minecraft:dragon_head",
        (
            quest(
                "nether",
                "The Road Runs Through Fire",
                "Enter the Nether and leave yourself a way back.",
                "minecraft:obsidian",
                dimension("minecraft:the_nether"),
                prize("minecraft:golden_apple", 2),
                col=0,
                row=0,
                shape="hexagon",
                size=1.5,
            ),
            quest(
                "eyes",
                "Let the Eye Lead",
                "Follow an Eye of Ender until the earth gives up its stronghold.",
                "minecraft:ender_eye",
                advancement("minecraft:story/follow_ender_eye"),
                prize("minecraft:ender_pearl", 4),
                parents=("nether",),
                col=2,
                row=0,
            ),
            quest(
                "portable_hole",
                "Borrow a Passage",
                "Find a Portable Hole in the stronghold and remember that its doorway never lasts.",
                "portablehole:portable_hole",
                item("portablehole:portable_hole"),
                prize("minecraft:golden_carrot", 8),
                parents=("eyes",),
                col=2,
                row=2,
            ),
            quest(
                "enter_end",
                "A Sky Without a Horizon",
                "Step through prepared. The other side has nowhere forgiving to fall.",
                "minecraft:end_stone",
                dimension("minecraft:the_end"),
                prize("minecraft:ender_pearl", 8),
                parents=("eyes",),
                col=4,
                row=0,
                shape="diamond",
                size=1.5,
            ),
            quest(
                "kill_dragon",
                "Break the Silence",
                "The dragon has ruled an empty sky long enough.",
                "minecraft:dragon_head",
                advancement("minecraft:end/kill_dragon"),
                prize("minecraft:dragon_head"),
                parents=("enter_end",),
                col=6,
                row=0,
                shape="pentagon",
                size=2.0,
            ),
        ),
    ),
    Chapter(
        "beyond_end",
        "beyond_the_dragon",
        "wide_world",
        "&dBeyond the Dragon",
        "The outer islands are not an epilogue",
        "the_beyond:live_flame",
        (
            quest(
                "gateway",
                "The Story Continues",
                "Cross the gateway. Stranger islands, unfamiliar lives, and unfinished stories wait outside.",
                "minecraft:ender_pearl",
                advancement("minecraft:end/enter_end_gateway"),
                prize("minecraft:chorus_fruit", 8),
                parents=("dragon/kill_dragon",),
                col=0,
                row=0,
                shape="hexagon",
                size=2.0,
            ),
            quest(
                "befriend_lantern",
                "A Light With Opinions",
                "Offer a soul torch to a Lantern and see whether it trusts you.",
                "minecraft:soul_torch",
                advancement("the_beyond:the_beyond/befriend_lantern"),
                prize("minecraft:soul_torch", 16),
                parents=("gateway",),
                col=2,
                row=-2,
            ),
            quest(
                "live_flame",
                "Fire That Lives",
                "Feed ectoplasm to a lit bonfire and carry away something alive.",
                "the_beyond:live_flame",
                advancement("the_beyond:the_beyond/ectoplasmic_ignition"),
                prize("minecraft:end_rod", 4),
                parents=("befriend_lantern",),
                col=4,
                row=-2,
                shape="diamond",
                size=1.5,
            ),
            quest(
                "pass_torch",
                "Carry the Flame",
                "Take a Live Flame somewhere new and wake a cold bonfire.",
                "the_beyond:bonfire",
                advancement("the_beyond:the_beyond/pass_the_torch"),
                prize("minecraft:blaze_powder", 4),
                parents=("live_flame",),
                col=6,
                row=-2,
            ),
            quest(
                "respite",
                "One More Chance",
                "Hold a Totem of Respite when death comes and keep what was yours.",
                "the_beyond:totem_of_respite",
                advancement("the_beyond:the_beyond/defying_the_void"),
                prize("minecraft:chorus_fruit", 16),
                parents=("pass_torch",),
                col=8,
                row=-2,
                shape="pentagon",
                size=1.5,
            ),
            quest(
                "gift_enadrake",
                "A Gift, Freely Given",
                "Offer an Enadrake something from your hand and see where generosity leads.",
                "the_beyond:enadrake_flare",
                advancement("the_beyond:the_beyond/gift_enadrake"),
                prize("minecraft:emerald", 8),
                parents=("gateway",),
                col=2,
                row=0,
            ),
            quest(
                "refuge",
                "Roots of Refuge",
                "Raise a Refuge near an Enadrake village and let its inhabitants awaken it.",
                "the_beyond:refuge",
                advancement("the_beyond:the_beyond/complete_refuge"),
                prize("minecraft:bone_meal", 16),
                parents=("gift_enadrake",),
                col=4,
                row=0,
                shape="diamond",
                size=1.5,
            ),
            quest(
                "offering",
                "Something Worth Remembering",
                "Carry a remembrance to an Abyssal Nomad. Some gifts open stranger roads.",
                "the_beyond:memory_remembrance",
                advancement("the_beyond:the_beyond/offering_remembered"),
                prize("minecraft:book", 4),
                parents=("gateway",),
                col=2,
                row=2,
            ),
            quest(
                "sacred_passage",
                "Trust the Journey",
                "When the Nomad sits, climb aboard and let it choose the road.",
                "the_beyond:mount_remembrance",
                advancement("the_beyond:the_beyond/sacred_passage"),
                prize("minecraft:ender_pearl", 8),
                parents=("offering",),
                col=4,
                row=2,
            ),
            quest(
                "memories",
                "The Fountain Remembers",
                "Return five remembrances to a fountain and watch the pieces gather.",
                "the_beyond:beads_remembrance",
                advancement("the_beyond:the_beyond/memories_returned"),
                prize("minecraft:echo_shard", 2),
                parents=("sacred_passage",),
                col=6,
                row=2,
                shape="diamond",
                size=1.5,
            ),
            quest(
                "so_below",
                "Walk the Auroracite",
                "Let Pathfinder Boots turn Auroracite into a road beneath your feet.",
                "the_beyond:pathfinder_boots",
                advancement("the_beyond:the_beyond/so_below"),
                prize("minecraft:firework_rocket", 16),
                parents=("memories",),
                col=8,
                row=2,
            ),
            quest(
                "as_above",
                "Ride the Storm",
                "Soar through a migration storm and meet the End on its own terms.",
                "the_beyond:auroracite",
                advancement("the_beyond:the_beyond/as_above"),
                prize("minecraft:dragon_breath", 2),
                parents=("so_below",),
                col=10,
                row=2,
                shape="pentagon",
                size=2.0,
            ),
        ),
    ),
)


def has_invalid_ftb_ampersand(value: str) -> bool:
    for index, character in enumerate(value):
        if character != "&":
            continue
        backslashes = 0
        cursor = index - 1
        while cursor >= 0 and value[cursor] == "\\":
            backslashes += 1
            cursor -= 1
        if backslashes % 2 == 1 or FTB_FORMATTING_SUFFIX.match(value, index + 1):
            continue
        return True
    return False


def stable_id(*parts: str) -> str:
    digest = hashlib.sha256("minecraft-beyond\0".encode() + "\0".join(parts).encode()).digest()
    value = int.from_bytes(digest[:8], "big") & 0x7FFF_FFFF_FFFF_FFFF
    if value < 2:
        value += 2
    return f"{value:016X}"


def group_id(key: str) -> str:
    return stable_id("group", key)


def chapter_id(key: str) -> str:
    return stable_id("chapter", key)


def quest_id(chapter_key: str, quest_key: str) -> str:
    return stable_id("quest", chapter_key, quest_key)


def task_id(chapter_key: str, quest_key: str, index: int) -> str:
    return stable_id("task", chapter_key, quest_key, str(index))


def reward_id(chapter_key: str, quest_key: str) -> str:
    # Preserve the old salt so existing completions never expose a duplicate claim.
    return stable_id("reward", chapter_key, quest_key, "xp")


def resolve_parent(current_chapter: str, reference: str) -> tuple[str, str]:
    if "/" in reference:
        chapter_key, quest_key = reference.split("/", 1)
        return chapter_key, quest_key
    return current_chapter, reference


def number(value: float) -> str:
    return f"{value:.1f}d"


def indent(lines: Iterable[str], tabs: int = 1) -> list[str]:
    prefix = "\t" * tabs
    return [prefix + line if line else line for line in lines]


def render_task(chapter_key: str, quest_key: str, index: int, task: Task) -> list[str]:
    object_id = task_id(chapter_key, quest_key, index)
    lines = ["{"]
    if task.kind == "item":
        if task.count > 1:
            lines.append(f"\tcount: {task.count}L,")
        stack: dict[str, object] = {"count": 1, "id": task.value}
        if task.components:
            stack["components"] = dict(task.components)
        lines.extend(
            (
                f'\tid: "{object_id}",',
                f"\titem: {json.dumps(stack, ensure_ascii=False, separators=(',', ':'))},",
            )
        )
        if task.match_components:
            lines.append(f'\tmatch_components: "{task.match_components}",')
        if task.only_from_crafting:
            lines.append("\tonly_from_crafting: true,")
    elif task.kind == "dimension":
        lines.append(f'\tdimension: "{task.value}",')
        lines.append(f'\tid: "{object_id}",')
    elif task.kind == "advancement":
        lines.append(f'\tadvancement: "{task.value}",')
        lines.append('\tcriterion: "",')
        lines.append(f'\tid: "{object_id}",')
    elif task.kind == "kill":
        lines.append(f'\tentity: "{task.value}",')
        lines.append(f'\tid: "{object_id}",')
        lines.append(f"\tvalue: {task.count}L,")
    elif task.kind == "stat":
        lines.append(f'\tid: "{object_id}",')
        lines.append(f'\tstat: "{task.value}",')
        lines.append(f"\tvalue: {task.count},")
    elif task.kind == "biome":
        lines.append(f'\tbiome: "{task.value}",')
        lines.append(f'\tid: "{object_id}",')
    elif task.kind == "structure":
        lines.append(f'\tid: "{object_id}",')
        lines.append(f'\tstructure: "{task.value}",')
    elif task.kind == "observation":
        lines.append(f'\tid: "{object_id}",')
        lines.append(f'\tobservation_type: "{task.option}",')
        lines.append(f"\ttimer: {task.timer}L,")
        lines.append(f'\tto_observe: "{task.value}",')
    else:
        raise ValueError(f"Unsupported task type: {task.kind}")
    lines.extend((f'\ttype: "{task.kind}",', "}"))
    return lines


def render_quest(chapter: Chapter, entry: Quest) -> list[str]:
    lines = ["{"]
    if entry.parents:
        dependencies = []
        for parent in entry.parents:
            parent_chapter, parent_quest = resolve_parent(chapter.key, parent)
            dependencies.append(f'"{quest_id(parent_chapter, parent_quest)}"')
        lines.append(f"\tdependencies: [{', '.join(dependencies)}],")
    lines.extend(
        (
            "\ticon: {",
            f'\t\tid: "{entry.icon}",',
            "\t},",
            f'\tid: "{quest_id(chapter.key, entry.key)}",',
            "\trewards: [{",
        )
    )
    if entry.reward.count > 1:
        lines.append(f"\t\tcount: {entry.reward.count},")
    reward_stack: dict[str, object] = {"count": 1, "id": entry.reward.resource_id}
    if entry.reward.components:
        reward_stack["components"] = dict(entry.reward.components)
    lines.extend(
        (
            f'\t\tid: "{reward_id(chapter.key, entry.key)}",',
            f"\t\titem: {json.dumps(reward_stack, ensure_ascii=False, separators=(',', ':'))},",
            '\t\ttype: "item",',
            "\t}],",
        )
    )
    if entry.shape != "circle":
        lines.append(f'\tshape: "{entry.shape}",')
    if entry.size != 1.0:
        lines.append(f"\tsize: {number(entry.size)},")
    lines.append("\ttasks: [")
    for index, task in enumerate(entry.tasks):
        task_lines = render_task(chapter.key, entry.key, index, task)
        task_lines[-1] += ","
        lines.extend(indent(task_lines, 2))
    lines.extend(
        (
            "\t],",
            f"\tx: {number(entry.col * 2.0)},",
            f"\ty: {number(entry.row * 1.5)},",
            "}",
        )
    )
    return lines


def render_chapter(chapter: Chapter, order_index: int) -> str:
    lines = [
        "{",
        "\tdefault_hide_dependency_lines: false,",
        '\tdefault_quest_shape: "circle",',
        f'\tfilename: "{chapter.filename}",',
        f'\tgroup: "{group_id(chapter.group)}",',
        "\ticon: {",
        f'\t\tid: "{chapter.icon}",',
        "\t},",
        f'\tid: "{chapter_id(chapter.key)}",',
        f"\torder_index: {order_index},",
        '\tprogression_mode: "flexible",',
        "\tquest_links: [ ],",
        "\tquests: [",
    ]
    for entry in chapter.quests:
        quest_lines = render_quest(chapter, entry)
        quest_lines[-1] += ","
        lines.extend(indent(quest_lines, 2))
    lines.extend(("\t],", "}"))
    return "\n".join(lines) + "\n"


def render_data() -> str:
    return """{
\tdefault_autoclaim_rewards: "disabled",
\tdefault_consume_items: false,
\tdefault_quest_disable_jei: false,
\tdefault_quest_shape: "circle",
\tdefault_reward_team: false,
\tdetection_delay: 20,
\tdisable_gui: false,
\tdrop_book_on_death: false,
\tdrop_loot_crates: false,
\temergency_items_cooldown: 300,
\tfallback_locale: "en_us",
\tgrid_scale: 0.5d,
\thide_excluded_quests: false,
\tlock_message: "",
\tloot_crate_no_drop: {
\t\tboss: 0,
\t\tmonster: 600,
\t\tpassive: 4000,
\t},
\tpause_game: false,
\tprogression_mode: "flexible",
\tshow_lock_icons: true,
\tverify_on_load: true,
\tversion: 13,
}
"""


def render_groups() -> str:
    lines = ["{", "\tchapter_groups: ["]
    lines.extend(f'\t\t{{ id: "{group_id(group.key)}", }},' for group in GROUPS)
    lines.extend(("\t],", "}"))
    return "\n".join(lines) + "\n"


def render_language() -> str:
    entries: list[tuple[str, str | tuple[str, ...]]] = [
        ("file.0000000000000001.title", QUEST_BOOK_TITLE)
    ]
    for group in GROUPS:
        entries.append((f"chapter_group.{group_id(group.key)}.title", group.title))
    for chapter in CHAPTERS:
        chapter_object_id = chapter_id(chapter.key)
        entries.append((f"chapter.{chapter_object_id}.title", chapter.title))
        entries.append((f"chapter.{chapter_object_id}.chapter_subtitle", (chapter.subtitle,)))
        for entry in chapter.quests:
            quest_object_id = quest_id(chapter.key, entry.key)
            entries.append((f"quest.{quest_object_id}.title", entry.title))
            entries.append((f"quest.{quest_object_id}.quest_desc", entry.description))
    lines = ["{"]
    for key, value in entries:
        if isinstance(value, tuple):
            lines.append(f"\t{key}: [")
            lines.extend(f"\t\t{json.dumps(line, ensure_ascii=False)}," for line in value)
            lines.append("\t],")
        else:
            lines.append(f"\t{key}: {json.dumps(value, ensure_ascii=False)},")
    lines.append("}")
    return "\n".join(lines) + "\n"


def expected_files() -> dict[Path, str]:
    files = {
        Path("data.snbt"): render_data(),
        Path("chapter_groups.snbt"): render_groups(),
        Path("lang/en_us.snbt"): render_language(),
    }
    for index, chapter in enumerate(CHAPTERS):
        files[Path("chapters") / f"{chapter.filename}.snbt"] = render_chapter(chapter, index)
    return files


def validate_definitions() -> None:
    errors: list[str] = []
    supported_tasks = {
        "advancement",
        "biome",
        "dimension",
        "item",
        "kill",
        "observation",
        "stat",
        "structure",
    }
    observation_types = {
        "block",
        "block_entity",
        "block_entity_type",
        "block_state",
        "block_tag",
        "entity_type",
        "entity_type_tag",
    }

    def validate_text(label: str, value: str) -> None:
        if has_invalid_ftb_ampersand(value):
            errors.append(f"{label} contains an unescaped literal &")

    group_keys = {group.key for group in GROUPS}
    chapter_keys = {chapter.key for chapter in CHAPTERS}
    if len(group_keys) != len(GROUPS):
        errors.append("duplicate chapter-group key")
    if len(chapter_keys) != len(CHAPTERS):
        errors.append("duplicate chapter key")
    if len({chapter.filename for chapter in CHAPTERS}) != len(CHAPTERS):
        errors.append("duplicate chapter filename")

    object_ids: dict[str, str] = {"0000000000000001": "quest file"}
    quest_keys: set[tuple[str, str]] = set()

    def register(object_id: str, label: str) -> None:
        if not HEX_ID.fullmatch(object_id):
            errors.append(f"invalid ID {object_id} for {label}")
        if object_id in object_ids:
            errors.append(f"duplicate ID {object_id}: {object_ids[object_id]} and {label}")
        object_ids[object_id] = label

    validate_text("quest file title", QUEST_BOOK_TITLE)
    for group in GROUPS:
        register(group_id(group.key), f"group {group.key}")
        validate_text(f"group {group.key}", group.title)
    for chapter in CHAPTERS:
        register(chapter_id(chapter.key), f"chapter {chapter.key}")
        validate_text(f"chapter {chapter.key}", chapter.title)
        validate_text(f"chapter {chapter.key} subtitle", chapter.subtitle)
        if chapter.group not in group_keys:
            errors.append(f"chapter {chapter.key} uses unknown group {chapter.group}")
        if not RESOURCE_ID.fullmatch(chapter.icon):
            errors.append(f"chapter {chapter.key} has invalid icon {chapter.icon}")
        positions: dict[tuple[float, float], str] = {}
        for entry in chapter.quests:
            key = (chapter.key, entry.key)
            if key in quest_keys:
                errors.append(f"duplicate quest key {chapter.key}/{entry.key}")
            quest_keys.add(key)
            register(quest_id(*key), f"quest {chapter.key}/{entry.key}")
            register(reward_id(*key), f"reward {chapter.key}/{entry.key}")
            validate_text(f"quest {chapter.key}/{entry.key}", entry.title)
            for line in entry.description:
                validate_text(f"quest {chapter.key}/{entry.key} description", line)
            words = sum(len(line.split()) for line in entry.description)
            if words > 30:
                errors.append(f"quest {chapter.key}/{entry.key} description is {words} words")
            if len(entry.tasks) != 1:
                errors.append(f"quest {chapter.key}/{entry.key} must have one task")
            position = (entry.col, entry.row)
            if position in positions:
                errors.append(
                    f"quests {chapter.key}/{positions[position]} and {entry.key} overlap at {position}"
                )
            positions[position] = entry.key
            for resource, label in (
                (entry.icon, "icon"),
                (entry.reward.resource_id, "reward"),
            ):
                if not RESOURCE_ID.fullmatch(resource):
                    errors.append(f"quest {chapter.key}/{entry.key} has invalid {label} {resource}")
                if resource in RESERVED_QUEST_TARGETS:
                    errors.append(
                        f"quest {chapter.key}/{entry.key} uses reserved {label} {resource}"
                    )
            if entry.reward.count < 1:
                errors.append(f"quest {chapter.key}/{entry.key} has invalid reward count")
            for index, task in enumerate(entry.tasks):
                register(task_id(chapter.key, entry.key, index), f"task {chapter.key}/{entry.key}")
                if task.kind not in supported_tasks:
                    errors.append(f"quest {chapter.key}/{entry.key} uses task type {task.kind}")
                if not RESOURCE_ID.fullmatch(task.value):
                    errors.append(f"quest {chapter.key}/{entry.key} has invalid task {task.value}")
                if task.value in RESERVED_QUEST_TARGETS:
                    errors.append(f"quest {chapter.key}/{entry.key} targets {task.value}")
                if task.count < 1:
                    errors.append(f"quest {chapter.key}/{entry.key} has invalid task count")
                if task.kind == "observation":
                    if task.option not in observation_types or task.timer < 1:
                        errors.append(f"quest {chapter.key}/{entry.key} has invalid observation")
                elif task.option or task.timer:
                    errors.append(f"quest {chapter.key}/{entry.key} has stray observation fields")
                if task.match_components not in {"", "fuzzy", "strict"}:
                    errors.append(f"quest {chapter.key}/{entry.key} has invalid component matching")
                if task.kind != "item" and (
                    task.components or task.match_components or task.only_from_crafting
                ):
                    errors.append(f"quest {chapter.key}/{entry.key} has item-only task fields")

    graph: dict[tuple[str, str], list[tuple[str, str]]] = {key: [] for key in quest_keys}
    for chapter in CHAPTERS:
        for entry in chapter.quests:
            node = (chapter.key, entry.key)
            for reference in entry.parents:
                parent = resolve_parent(chapter.key, reference)
                if parent not in quest_keys:
                    errors.append(f"quest {chapter.key}/{entry.key} has unknown parent {reference}")
                else:
                    graph[node].append(parent)

    visiting: set[tuple[str, str]] = set()
    visited: set[tuple[str, str]] = set()

    def visit(node: tuple[str, str]) -> None:
        if node in visiting:
            errors.append(f"dependency cycle at {node[0]}/{node[1]}")
            return
        if node in visited:
            return
        visiting.add(node)
        for parent in graph[node]:
            visit(parent)
        visiting.remove(node)
        visited.add(node)

    for node in graph:
        visit(node)
    if errors:
        raise ValueError("Quest definition validation failed:\n- " + "\n- ".join(errors))


def referenced_items() -> set[str]:
    ids: set[str] = set()
    for chapter in CHAPTERS:
        ids.add(chapter.icon)
        for entry in chapter.quests:
            ids.add(entry.icon)
            ids.add(entry.reward.resource_id)
            ids.update(task.value for task in entry.tasks if task.kind == "item")
    return ids


def referenced_for(task_kind: str) -> set[str]:
    return {
        task.value
        for chapter in CHAPTERS
        for entry in chapter.quests
        for task in entry.tasks
        if task.kind == task_kind
    }


def validate_instance_resources(minecraft_root: Path) -> None:
    required = {
        "items": referenced_items(),
        "advancements": referenced_for("advancement"),
        "blocks": {
            task.value
            for chapter in CHAPTERS
            for entry in chapter.quests
            for task in entry.tasks
            if task.kind == "observation" and task.option == "block"
        },
        "biomes": referenced_for("biome"),
        "structures": referenced_for("structure"),
    }
    discovered = {key: set() for key in required}
    archives = set((minecraft_root / "mods").glob("*.jar"))
    if len(minecraft_root.parents) >= 3:
        prism_root = minecraft_root.parents[2]
        archives.update((prism_root / "libraries/net/minecraft/client").glob("*/*-extra.jar"))
    patterns = {
        "items": re.compile(r"assets/([^/]+)/(?:models/item|items)/(.+)\.json"),
        "blocks": re.compile(r"assets/([^/]+)/blockstates/(.+)\.json"),
        "advancements": re.compile(r"data/([^/]+)/advancements?/(.+)\.json"),
        "biomes": re.compile(r"data/([^/]+)/worldgen/biome/(.+)\.json"),
        "structures": re.compile(r"data/([^/]+)/worldgen/structure/(.+)\.json"),
    }
    for archive in sorted(archives):
        try:
            with zipfile.ZipFile(archive) as jar:
                for filename in jar.namelist():
                    for kind, pattern in patterns.items():
                        match = pattern.fullmatch(filename)
                        if match:
                            discovered[kind].add(f"{match.group(1)}:{match.group(2)}")
        except zipfile.BadZipFile:
            continue
    errors = []
    for kind, resource_ids in required.items():
        missing = sorted(resource_ids - discovered[kind])
        if missing:
            errors.append(f"no installed {kind} resource for:\n  - " + "\n  - ".join(missing))
    if errors:
        raise ValueError("Installed resource validation failed:\n- " + "\n- ".join(errors))


def write_files(root: Path, files: dict[Path, str]) -> None:
    for relative, content in files.items():
        destination = root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(content, encoding="utf-8", newline="\n")


def check_files(root: Path, files: dict[Path, str]) -> None:
    errors = []
    for relative, expected in files.items():
        destination = root / relative
        if not destination.exists():
            errors.append(f"missing {destination}")
        elif destination.read_text(encoding="utf-8") != expected:
            errors.append(f"out of date {destination}")
    if root.exists():
        expected_paths = {root / relative for relative in files}
        errors.extend(
            f"unexpected generated file {actual}"
            for actual in root.rglob("*.snbt")
            if actual not in expected_paths
        )
    if errors:
        raise ValueError("Generated quest files are not current:\n- " + "\n- ".join(errors))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--validate-instance", type=Path, metavar="MINECRAFT_DIR")
    parser.add_argument("--sync-instance", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    validate_definitions()
    files = expected_files()
    if args.check:
        check_files(OUTPUT_ROOT, files)
    else:
        write_files(OUTPUT_ROOT, files)
    if args.validate_instance:
        validate_instance_resources(args.validate_instance.resolve())
    if args.sync_instance:
        if args.check:
            raise ValueError("--sync-instance cannot be combined with --check")
        if INSTANCE_ROOT.exists():
            expected = {INSTANCE_ROOT / path for path in files}
            unexpected = [path for path in INSTANCE_ROOT.rglob("*.snbt") if path not in expected]
            if unexpected:
                joined = "\n- ".join(str(path) for path in unexpected)
                raise ValueError(f"Refusing to overwrite an instance with extra quest files:\n- {joined}")
        write_files(INSTANCE_ROOT, files)
    quest_count = sum(len(chapter.quests) for chapter in CHAPTERS)
    task_count = sum(len(entry.tasks) for chapter in CHAPTERS for entry in chapter.quests)
    verb = "Verified" if args.check else "Generated"
    synced = " and synced the Prism instance" if args.sync_instance else ""
    print(f"{verb} {len(CHAPTERS)} chapters, {quest_count} quests, and {task_count} tasks{synced}.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError) as exc:
        print(exc, file=sys.stderr)
        raise SystemExit(1)
