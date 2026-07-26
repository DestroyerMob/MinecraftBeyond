#!/usr/bin/env python3
"""Generate Minecraft Beyond's Mobs Tool Forging material compatibility data."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
KUBEJS = ROOT / "pack" / "kubejs"
DOC = ROOT / "docs" / "FORGING_MATERIALS.md"
GUIDE_ENTRIES = (
    KUBEJS
    / "assets"
    / "mobstoolforging"
    / "patchouli_books"
    / "forgemasters_guide"
    / "en_us"
    / "entries"
    / "materials"
)


@dataclass(frozen=True)
class Trait:
    id: str
    name: str
    description: str
    color: str
    category: str
    durability: float = 1.0
    mining: float = 1.0
    damage: float = 0.0
    attack_speed: float = 0.0
    fire_resistant: bool = False
    affinities: tuple[str, ...] = ()
    behavior: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Material:
    id: str
    name: str
    item: str
    category: str
    uses: int
    mining_speed: float
    attack_damage: float
    enchantment: int
    trait: str
    color: str
    family: str
    common_tag: str | None = None
    minimum_heat: str | None = None
    tier_base: str = "diamond"
    incorrect_blocks_tag: str | None = None
    abrasive_tier: str | None = None
    emissive: bool = False
    luminosity: int = 0
    extra_rule: dict[str, Any] = field(default_factory=dict)


CUSTOM_TRAITS = {
    trait.id: trait
    for trait in (
        Trait(
            "minecraft_beyond:frostbound",
            "Frostbound",
            "Winter clings to the edge, slowing and freezing whatever it strikes.",
            "aqua",
            "structure",
            durability=1.05,
            mining=1.08,
            behavior={
                "target_effect": {"effect": "minecraft:slowness", "duration": 40},
                "freeze_ticks": 100,
            },
        ),
        Trait(
            "minecraft_beyond:voltaic",
            "Voltaic",
            "A quick, hungry current leaps from a struck foe to two nearby enemies.",
            "yellow",
            "handling",
            durability=0.90,
            mining=1.12,
            attack_speed=0.20,
            affinities=("mobstoolforging:resonance",),
            behavior={"chain_damage": 1.0, "chain_radius": 5, "chain_targets": 2},
        ),
        Trait(
            "minecraft_beyond:venomous",
            "Venomous",
            "A predatory edge leaves poison working behind every clean hit.",
            "dark_green",
            "edge",
            damage=0.45,
            attack_speed=0.10,
            behavior={
                "target_effect": {"effect": "minecraft:poison", "duration": 60},
            },
        ),
        Trait(
            "minecraft_beyond:nimble",
            "Nimble",
            "A light, lively build lends its wielder a burst of speed after a hit.",
            "green",
            "handling",
            durability=0.90,
            mining=1.15,
            attack_speed=0.35,
            affinities=("mobstoolforging:enchant_control",),
            behavior={
                "attacker_effect": {"effect": "minecraft:speed", "duration": 40},
            },
        ),
        Trait(
            "minecraft_beyond:umbral",
            "Umbral",
            "The shadowed edge hits harder while its wielder moves with care.",
            "dark_purple",
            "edge",
            durability=0.90,
            mining=1.05,
            damage=0.45,
            attack_speed=0.15,
            affinities=("mobstoolforging:silence",),
            behavior={"damage_bonus_while_sneaking": 1.5},
        ),
        Trait(
            "minecraft_beyond:sanguine",
            "Sanguine",
            "The weapon drinks a little of the harm it deals and returns it as health.",
            "dark_red",
            "edge",
            durability=0.90,
            damage=0.60,
            behavior={"lifesteal_fraction": 0.08, "lifesteal_cap": 2.0},
        ),
        Trait(
            "minecraft_beyond:gravitic",
            "Gravitic",
            "Dense force throws struck creatures back and briefly lifts their footing.",
            "dark_purple",
            "structure",
            durability=1.15,
            damage=0.75,
            attack_speed=-0.20,
            behavior={"knockback": 0.35, "vertical_lift": 0.12},
        ),
        Trait(
            "minecraft_beyond:silvered",
            "Silvered",
            "A brilliant edge cuts especially deep into undead creatures.",
            "white",
            "edge",
            mining=1.10,
            damage=0.35,
            affinities=("mobstoolforging:enchanting",),
            behavior={"damage_bonus_vs_undead": 1.5},
        ),
        Trait(
            "minecraft_beyond:maledictive",
            "Maledictive",
            "A curse-tempered blow slows its victim; the next one punishes the afflicted.",
            "dark_green",
            "structure",
            durability=1.10,
            damage=0.40,
            affinities=("mobstoolforging:sculk",),
            behavior={
                "target_effect": {"effect": "minecraft:slowness", "duration": 50},
                "damage_bonus_if_target_has_effect": "minecraft:slowness",
                "conditional_damage_bonus": 0.75,
            },
        ),
        Trait(
            "minecraft_beyond:radiant",
            "Radiant",
            "A revealing strike outlines the victim and nearby creatures of its kind.",
            "yellow",
            "affinity",
            durability=0.95,
            mining=1.10,
            attack_speed=0.10,
            affinities=("mobstoolforging:resonance",),
            behavior={
                "target_effect": {"effect": "minecraft:glowing", "duration": 200},
                "reveal_same_type_radius": 8,
            },
        ),
        Trait(
            "minecraft_beyond:vital_edge",
            "Vital Edge",
            "Its bite sharpens as the wielder's own health falls.",
            "blue",
            "edge",
            behavior={"missing_health_damage_bonus": 2.0},
        ),
    )
}


MATERIALS = (
    # Mythic Upgrades: use the raw gems as lapidary inputs, not the expensive
    # gem-necoium alloy ingots used by Mythic Upgrades' own equipment.
    Material("mythicupgrades:aquamarine", "Aquamarine", "mythicupgrades:aquamarine", "gem", 1000, 7.2, 2.3, 20, "minecraft_beyond:frostbound", "#21889F", "gem", "c:gems/aquamarine"),
    Material("mythicupgrades:citrine", "Citrine", "mythicupgrades:citrine", "gem", 850, 7.8, 2.2, 20, "minecraft_beyond:voltaic", "#BA823A", "gem", "c:gems/citrine"),
    Material("mythicupgrades:peridot", "Peridot", "mythicupgrades:peridot", "gem", 925, 7.0, 2.3, 18, "minecraft_beyond:venomous", "#719E2B", "gem", "c:gems/peridot"),
    Material("mythicupgrades:jade", "Jade", "mythicupgrades:jade", "gem", 1100, 7.7, 2.1, 22, "minecraft_beyond:nimble", "#399E4F", "gem", "c:gems/jade"),
    Material("mythicupgrades:ametrine", "Ametrine", "mythicupgrades:ametrine", "gem", 1400, 8.0, 2.75, 26, "mobstoolforging:resonant", "#884594", "gem", "c:gems/ametrine"),
    Material("mythicupgrades:necoium", "Necoium", "mythicupgrades:necoium_ingot", "metal", 675, 7.5, 2.3, 15, "mobstoolforging:reinforced", "#BA528A", "metal", "c:ingots/necoium", "high"),

    # Gemforged's eight equal-weight Random Gem Vein drops.
    Material("gemforged:nyxite", "Nyxite", "gemforged:nyxite", "gem", 900, 7.0, 2.25, 18, "minecraft_beyond:umbral", "#5D4378", "gem", "c:gems/nyxite"),
    Material("gemforged:bloodstone", "Bloodstone", "gemforged:bloodstone", "gem", 900, 7.0, 2.25, 18, "minecraft_beyond:sanguine", "#993641", "gem", "c:gems/bloodstone"),
    Material("gemforged:solarium", "Solarium", "gemforged:solarium", "gem", 900, 7.0, 2.25, 18, "mobstoolforging:forceful", "#A26F19", "gem", "c:gems/solarium"),
    Material("gemforged:venomyte", "Venomyte", "gemforged:venomyte", "gem", 900, 7.0, 2.25, 18, "minecraft_beyond:venomous", "#217254", "gem", "c:gems/venomyte"),
    Material("gemforged:phoenixtone", "Phoenixtone", "gemforged:phoenixtone", "gem", 900, 7.0, 2.25, 18, "mobstoolforging:kindled", "#A23B0C", "gem", "c:gems/phoenixtone", emissive=True, luminosity=7),
    Material("gemforged:prismyte", "Prismyte", "gemforged:prismyte", "gem", 900, 7.0, 2.25, 18, "minecraft_beyond:voltaic", "#3281AB", "crystal", "c:gems/prismyte"),
    Material("gemforged:gravitium", "Gravitium", "gemforged:gravitium", "gem", 900, 7.0, 2.25, 18, "minecraft_beyond:gravitic", "#7C2E80", "gem", "c:gems/gravitium"),
    Material("gemforged:verdantite", "Verdantite", "gemforged:verdantite", "gem", 900, 7.0, 2.25, 18, "mobstoolforging:steady", "#60A912", "gem", "c:gems/verdantite"),

    # Caverns & Chasms. Tin deliberately remains a foundry-only bronze input.
    Material("caverns_and_chasms:silver", "Silver", "caverns_and_chasms:silver_ingot", "metal", 157, 9.0, 1.0, 18, "minecraft_beyond:silvered", "#979DAC", "metal", "c:ingots/silver", "low", "iron", "caverns_and_chasms:incorrect_for_silver_tool"),
    Material("caverns_and_chasms:necromium", "Necromium", "caverns_and_chasms:necromium_ingot", "metal", 2031, 9.0, 3.0, 15, "minecraft_beyond:maledictive", "#5D736C", "metal", "c:ingots/necromium", "high", "netherite", "caverns_and_chasms:incorrect_for_necromium_tool"),
    Material("caverns_and_chasms:spinel", "Spinel", "caverns_and_chasms:spinel", "gem", 650, 7.2, 2.6, 16, "mobstoolforging:forceful", "#B36D98", "gem", "c:gems/spinel"),
    Material("caverns_and_chasms:turquoise", "Turquoise", "caverns_and_chasms:turquoise", "gem", 1050, 7.2, 2.0, 22, "mobstoolforging:fortunate", "#87A29F", "gem", "c:gems/turquoise"),
    Material("caverns_and_chasms:zirconia", "Zirconia", "caverns_and_chasms:zirconia", "gem", 800, 7.2, 2.2, 25, "mobstoolforging:steady", "#C8CED8", "crystal", "c:gems/zirconia"),

    # Galosphere's metal and three genuine crystalline items.
    Material("galosphere:palladium", "Palladium", "galosphere:palladium_ingot", "metal", 420, 6.5, 1.5, 14, "mobstoolforging:forceful", "#929CA3", "metal", "c:ingots/palladium", "low", "iron"),
    Material("galosphere:opal", "Opal", "galosphere:opal", "gem", 600, 6.8, 1.8, 24, "mobstoolforging:fortunate", "#CD9A9D", "crystal", "c:gems/opal"),
    Material("galosphere:allurite", "Allurite", "galosphere:allurite_shard", "gem", 600, 7.0, 2.0, 24, "mobstoolforging:resonant", "#3EADB1", "crystal", "c:gems/allurite"),
    Material("galosphere:lumiere", "Lumiere", "galosphere:lumiere_shard", "gem", 700, 7.2, 2.0, 20, "minecraft_beyond:radiant", "#D79F5A", "crystal", "c:gems/lumiere", emissive=True, luminosity=5),

    # IgleeLib endgame alloys. These stay exact-item materials rather than
    # claiming broad common tags for otherwise unique netherite upgrades.
    Material("igleelib:modium", "Modium", "igleelib:modium_ingot", "metal", 2200, 9.0, 4.0, 12, "mobstoolforging:adamant", "#143FB1", "metal", minimum_heat="high", tier_base="netherite", extra_rule={"fire_resistant": True}),
    Material("igleelib:derium", "Derium", "igleelib:derium_ingot", "metal", 3000, 7.5, 3.5, 10, "mobstoolforging:work_hardened", "#5E1C74", "metal", minimum_heat="high", tier_base="netherite", extra_rule={"fire_resistant": True}),
    Material("igleelib:blazum", "Blazum", "igleelib:blazum_ingot", "metal", 1800, 10.0, 3.5, 18, "mobstoolforging:kindled", "#B25F13", "metal", minimum_heat="high", tier_base="netherite", emissive=True, luminosity=6),
    Material("igleelib:lavium", "Lavium", "igleelib:lavium_ingot", "metal", 2031, 9.0, 4.0, 15, "mobstoolforging:nether_forged", "#B32B1F", "metal", minimum_heat="high", tier_base="netherite", emissive=True, luminosity=7),

    # Narrow but real survival equipment materials from other active mods.
    Material("jadensnetherexpansiondelight:ecto", "Ecto", "jadensnetherexpansiondelight:ecto_ingot", "metal", 2031, 9.0, 4.0, 15, "minecraft_beyond:radiant", "#47483E", "metal", "c:ingots/ecto", "high", "netherite"),
    Material("the_beyond:void_crystal", "Void Crystal", "the_beyond:void_crystal", "gem", 1350, 8.2, 2.8, 24, "minecraft_beyond:gravitic", "#CB5DDA", "crystal", "c:gems/void_crystal", abrasive_tier="diamond", emissive=True, luminosity=4),
)


ALIASES = {
    "c:gems/ruby": ("mythicupgrades:ruby",),
    "c:gems/sapphire": ("mythicupgrades:sapphire",),
    "c:gems/topaz": ("mythicupgrades:topaz",),
}

CANONICAL_GEMS = (
    ("Ruby", "mythicupgrades:ruby", "1200 / 7.4 / +2.6 / 16", "Keen + Sanguine"),
    ("Sapphire", "mythicupgrades:sapphire", "1300 / 7.4 / +2.4 / 20", "Focused + Vital Edge"),
    ("Topaz", "mythicupgrades:topaz", "450 / 7.5 / +3.5 / 12", "Forceful + Voltaic"),
)

CANONICAL_TRAIT_RULES = {
    "ruby": ("mobstoolforging:ruby", "minecraft_beyond:sanguine"),
    "sapphire": ("mobstoolforging:sapphire", "minecraft_beyond:vital_edge"),
    "topaz": ("mobstoolforging:topaz", "minecraft_beyond:voltaic"),
}

BUILT_IN_TRAITS = {
    "mobstoolforging:steady": (
        "Steady",
        "Makes mining and attacks faster, and increases the amount restored by each repair item.",
    ),
    "mobstoolforging:kindled": (
        "Kindled",
        "Fireproof work that smelts eligible drops and ignites struck foes.",
    ),
    "mobstoolforging:reinforced": (
        "Reinforced",
        "Makes most actions cost no durability and lets one repair item restore half of the durability bar.",
    ),
    "mobstoolforging:resonant": (
        "Resonant",
        "Treats the strongest installed non-curse enchantment as two levels higher; it has no effect on an unenchanted item.",
    ),
    "mobstoolforging:work_hardened": (
        "Work-Hardened",
        "Mining speed and physical damage switch to stronger, non-stacking brackets as remaining durability falls.",
    ),
    "mobstoolforging:adamant": (
        "Adamant",
        "Mines suitable blocks faster and lets attacks ignore part of the target's armour.",
    ),
    "mobstoolforging:nether_forged": (
        "Nether-Forged",
        "Cannot burn, doubles maximum durability, raises physical base damage, and grants diamond harvest tier.",
    ),
    "mobstoolforging:fortunate": (
        "Fortunate",
        "Treats Fortune and Looting as two levels higher, even when neither enchantment is installed.",
    ),
    "mobstoolforging:forceful": (
        "Forceful",
        "Makes suitable-block mining and physical attacks stronger, but consumes durability faster.",
    ),
}

LEGACY_GUIDE_ENTRY_IDS = (
    "mythic_upgrades",
    "gemforged",
    "caverns_and_chasms",
    "galosphere",
    "distant_materials",
)

CORE_METAL_GUIDE_PAGES = (
    {
        "type": "patchouli:spotlight",
        "item": "minecraft:iron_ingot",
        "title": "Iron",
        "text": "A dependable workshop metal. Iron's Reinforced trait is about avoiding wear and making each repair item count.",
    },
    {
        "type": "patchouli:text",
        "title": "Reinforced",
        "text": "Reinforced makes most uses cost no durability. When repair is needed, one matching repair item restores half of the whole durability bar.$(p)$(bold)Wear ignored:$() 75% of uses$(br)$(bold)Repair item:$() Restores 50% of maximum durability",
    },
    {
        "type": "patchouli:spotlight",
        "item": "minecraft:copper_ingot",
        "title": "Copper",
        "text": "Copper rewards equipment that remains in service as it wears. Its Work-Hardened trait moves through stronger brackets as durability falls.",
    },
    {
        "type": "patchouli:text",
        "title": "Work-Hardened",
        "text": "Copper begins at normal strength. As remaining durability falls, mining speed and physical damage switch to the matching bracket. Only one bracket applies; these bonuses do not stack.$(p)$(bold)75% or more remaining:$() Normal$(br)$(bold)50–75%:$() 25% stronger$(br)$(bold)25–50%:$() 50% stronger$(br)$(bold)Below 25%:$() 2× strength",
    },
    {
        "type": "patchouli:spotlight",
        "item": "minecraft:gold_ingot",
        "title": "Gold",
        "text": "Soft but receptive, gold is chosen for what it lets an enchanter do next. Its Gilded trait works with Better Enchanting.",
    },
    {
        "type": "patchouli:text",
        "title": "Gilded",
        "text": "Gilded does not create experience or improve the tool directly. With Better Enchanting, each gold component opens one additional point of enchantment capacity.",
    },
    {
        "type": "patchouli:spotlight",
        "item": "minecraft:netherite_ingot",
        "title": "Netherite",
        "text": "Netherite turns a finished piece into something built for the harshest work. Its Nether-Forged trait combines resilience, force, and fireproofing.",
    },
    {
        "type": "patchouli:text",
        "title": "Nether-Forged",
        "text": "Nether-Forged equipment cannot burn.$(p)$(bold)Maximum durability:$() 2× normal$(br)$(bold)Physical base damage:$() 30% higher$(br)$(bold)Eligible tool heads:$() Diamond harvest tier",
    },
)

CORE_GEM_GUIDE_PAGES = (
    {
        "type": "patchouli:spotlight",
        "item": "minecraft:diamond",
        "title": "Diamond",
        "text": "Diamond brings precision as much as hardness. Its Adamant trait improves suitable work and cuts through part of an enemy's protection.",
    },
    {
        "type": "patchouli:text",
        "title": "Adamant",
        "text": "Adamant speeds up blocks the tool is meant to mine and lets attacks ignore part of the target's armour.$(p)$(bold)Suitable blocks:$() 75% faster$(br)$(bold)Armour ignored:$() 30%",
    },
    {
        "type": "patchouli:spotlight",
        "item": "minecraft:emerald",
        "title": "Emerald",
        "text": "Emerald favours a forge master who values what the work yields. Its Fortunate trait improves the level used for Fortune and Looting.",
    },
    {
        "type": "patchouli:text",
        "title": "Fortunate",
        "text": "Fortunate changes the effective level used when drops are calculated.$(p)$(bold)Fortune and Looting:$() 2 levels higher$(br)$(bold)No enchantment installed:$() Behaves as Level II$(br)$(bold)Normal level cap:$() May be exceeded",
    },
    {
        "type": "patchouli:spotlight",
        "item": "minecraft:amethyst_shard",
        "title": "Amethyst",
        "text": "Amethyst resonates with magic already held by the finished equipment. Its Resonant trait strengthens one existing enchantment.",
    },
    {
        "type": "patchouli:text",
        "title": "Resonant",
        "text": "Resonant strengthens one enchantment already on the item.$(p)$(bold)Target:$() Highest-level non-curse enchantment$(br)$(bold)Effective level:$() 2 levels higher$(br)$(bold)Unenchanted item:$() No effect",
    },
    {
        "type": "patchouli:spotlight",
        "item": "mythicupgrades:ruby",
        "title": "Ruby",
        "text": "Ruby is an aggressive gem whose two traits favour committed combat and decisive work.",
    },
    {
        "type": "patchouli:text",
        "title": "Ruby Traits",
        "text": "$(bold)Keen$()$(br)Improves suitable-block mining and physical damage.$(p)$(bold)Sanguine$()$(br)Heals from damage dealt, up to one heart per hit.",
    },
    {
        "type": "patchouli:spotlight",
        "item": "mythicupgrades:sapphire",
        "title": "Sapphire",
        "text": "Sapphire rewards control under difficult conditions. Its two traits keep work steady and turn danger into power.",
    },
    {
        "type": "patchouli:text",
        "title": "Sapphire Traits",
        "text": "$(bold)Focused$()$(br)Removes the mining penalties for being underwater or airborne.$(p)$(bold)Vital Edge$()$(br)Adds more damage as the wielder loses health, reaching its strongest point near death.",
    },
    {
        "type": "patchouli:spotlight",
        "item": "mythicupgrades:topaz",
        "title": "Topaz",
        "text": "Topaz trades longevity for force and crowd control. Its two traits suit a wielder who wants immediate impact.",
    },
    {
        "type": "patchouli:text",
        "title": "Topaz Traits",
        "text": "$(bold)Forceful$()$(br)Harder hits and faster mining, but faster durability loss.$(p)$(bold)Voltaic$()$(br)Arcs damage to as many as two nearby enemies.",
    },
)


def split_id(value: str) -> tuple[str, str]:
    namespace, path = value.split(":", 1)
    return namespace, path


def pretty_json(value: Any) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False) + "\n"


def shaded_palette(base: str) -> dict[str, str]:
    red = int(base[1:3], 16)
    green = int(base[3:5], 16)
    blue = int(base[5:7], 16)

    def darken(factor: float) -> tuple[int, int, int]:
        return tuple(round(channel * factor) for channel in (red, green, blue))

    def lighten(amount: float) -> tuple[int, int, int]:
        return tuple(round(channel + (255 - channel) * amount) for channel in (red, green, blue))

    colors = (
        darken(0.34),
        darken(0.52),
        darken(0.72),
        (red, green, blue),
        lighten(0.38),
        lighten(0.72),
    )
    return {
        key: f"0xFF{r:02X}{g:02X}{b:02X}"
        for key, (r, g, b) in zip(("63", "102", "140", "178", "216", "255"), colors)
    }


def material_definition(material: Material) -> dict[str, Any]:
    tier: dict[str, Any] = {
        "base": material.tier_base,
        "max_damage": material.uses,
        "mining_speed": material.mining_speed,
        "attack_damage_bonus": material.attack_damage,
        "enchantment_value": material.enchantment,
    }
    if material.incorrect_blocks_tag:
        tier["incorrect_blocks_tag"] = material.incorrect_blocks_tag
    if material.common_tag:
        tier["repair_tag"] = material.common_tag
    else:
        tier["repair_item"] = material.item

    value: dict[str, Any] = {
        "category": material.category,
        "display_item": material.item,
        "items": [material.item],
        "translation_key": f"material.minecraft_beyond.{material.id.replace(':', '.')}",
        "tier": tier,
        "visual_slots": ["headMaterial", "guardMaterial"],
    }
    if material.common_tag:
        value["tags"] = [material.common_tag]
    if material.minimum_heat:
        value["minimum_forge_heat"] = material.minimum_heat
    if material.abrasive_tier:
        value["required_lapidary_abrasive_tier"] = material.abrasive_tier
    return value


def trait_rule(material: Material) -> dict[str, Any]:
    trait = CUSTOM_TRAITS.get(material.trait)
    value: dict[str, Any] = {
        "slot": "any",
        "material": material.id,
        "traits": [material.trait],
    }
    if trait:
        value.update(
            {
                "durability_multiplier": trait.durability,
                "mining_speed_multiplier": trait.mining,
                "attack_damage_bonus": trait.damage,
                "attack_speed_bonus": trait.attack_speed,
                "fire_resistant": trait.fire_resistant,
            }
        )
        if trait.affinities:
            value["affinities"] = list(trait.affinities)
    value.update(material.extra_rule)
    return value


def material_visual(material: Material) -> dict[str, Any]:
    value: dict[str, Any] = {
        "type": "mobstoolforging:material_visual",
        "family": material.family,
        "palette": shaded_palette(material.color),
        "texture_noise": "fine_scratches" if material.category == "metal" else "facets",
        "fallbacks": [material.family],
        "emissive": material.emissive,
    }
    if material.luminosity:
        value["luminosity"] = material.luminosity
    return value


def generated_files() -> dict[Path, str]:
    files: dict[Path, str] = {}
    language: dict[str, str] = {}
    common_tags: dict[str, set[str]] = {
        tag: set(items) for tag, items in ALIASES.items()
    }

    for trait in CUSTOM_TRAITS.values():
        trait_path = split_id(trait.id)[1]
        files[
            KUBEJS
            / "data"
            / "minecraft_beyond"
            / "mobstoolforging"
            / "traits"
            / f"{trait_path}.json"
        ] = pretty_json(
            {
                "translation_key": f"tooltip.minecraft_beyond.trait.{trait_path}",
                "description_translation_key": f"tooltip.minecraft_beyond.trait.{trait_path}.desc",
                "color": trait.color,
                "category": trait.category,
            }
        )
        language[f"tooltip.minecraft_beyond.trait.{trait_path}"] = trait.name
        language[f"tooltip.minecraft_beyond.trait.{trait_path}.desc"] = trait.description
        if trait.behavior:
            files[
                KUBEJS
                / "data"
                / "minecraft_beyond"
                / "mobstoolforging"
                / "trait_behaviors"
                / f"{trait_path}.json"
            ] = pretty_json({"trait": trait.id, **trait.behavior})

    for name, (material, trait) in CANONICAL_TRAIT_RULES.items():
        files[
            KUBEJS
            / "data"
            / "minecraft_beyond"
            / "mobstoolforging"
            / "stat_rules"
            / f"canonical_{name}_identity.json"
        ] = pretty_json(
            {
                "slot": "head",
                "material": material,
                "traits": [trait],
            }
        )

    for material in MATERIALS:
        namespace, path = split_id(material.id)
        safe_id = material.id.replace(":", "_")
        files[
            KUBEJS / "data" / namespace / "mobstoolforging" / "materials" / f"{path}.json"
        ] = pretty_json(material_definition(material))
        files[
            KUBEJS
            / "data"
            / "minecraft_beyond"
            / "mobstoolforging"
            / "stat_rules"
            / f"{safe_id}.json"
        ] = pretty_json(trait_rule(material))
        files[
            KUBEJS / "assets" / namespace / "tooling" / "material_visuals" / f"{path}.json"
        ] = pretty_json(material_visual(material))
        language[f"material.minecraft_beyond.{material.id.replace(':', '.')}"] = material.name
        if material.common_tag:
            common_tags.setdefault(material.common_tag, set()).add(material.item)

    for tag, items in common_tags.items():
        namespace, tag_path = split_id(tag)
        files[
            KUBEJS / "data" / namespace / "tags" / "item" / f"{tag_path}.json"
        ] = pretty_json({"replace": False, "values": sorted(items)})

    files[
        KUBEJS / "assets" / "minecraft_beyond" / "lang" / "en_us.json"
    ] = pretty_json(dict(sorted(language.items())))
    files[GUIDE_ENTRIES / "metals.json"] = pretty_json(
        material_guide_entry(
            "Metals",
            "minecraft:iron_ingot",
            2,
            "metal",
            CORE_METAL_GUIDE_PAGES,
        )
    )
    files[GUIDE_ENTRIES / "gems.json"] = pretty_json(
        material_guide_entry(
            "Gems",
            "minecraft:diamond",
            3,
            "gem",
            CORE_GEM_GUIDE_PAGES,
        )
    )
    files[DOC] = material_document()
    return files


def material_guide_entry(
    name: str,
    icon: str,
    sortnum: int,
    material_type: str,
    core_pages: tuple[dict[str, Any], ...],
) -> dict[str, Any]:
    pages = [dict(page) for page in core_pages]
    materials = sorted(
        (
            material
            for material in MATERIALS
            if material.category == material_type
        ),
        key=lambda material: material.name,
    )
    for material in materials:
        custom_trait = CUSTOM_TRAITS.get(material.trait)
        if custom_trait:
            trait_name = custom_trait.name
            description = custom_trait.description
        else:
            trait_name, description = BUILT_IN_TRAITS[material.trait]
        station = "forged as metal" if material.category == "metal" else "used as a gem coating"
        pages.append(
            {
                "type": "patchouli:spotlight",
                "item": material.item,
                "title": material.name,
                "text": (
                    f"$(bold){trait_name}$() — {description}"
                    f"$(p)This material is {station}."
                ),
            },
        )
        pages.append(
            {
                "type": "patchouli:text",
                "title": f"{material.name} Profile",
                "text": (
                    f"$(bold)Durability:$() {material.uses:,} uses"
                    f"$(br)$(bold)Mining speed:$() {material.mining_speed:g}"
                    f"$(br)$(bold)Head damage bonus:$() +{material.attack_damage:g}"
                    f"$(br)$(bold)Enchantability:$() {material.enchantment}"
                ),
            },
        )
    if len(pages) % 2:
        raise ValueError(f"{name}: every material needs a complete two-page spread")
    for index in range(0, len(pages), 2):
        if (
            pages[index]["type"] != "patchouli:spotlight"
            or pages[index + 1]["type"] != "patchouli:text"
        ):
            raise ValueError(
                f"{name}: spread {index // 2 + 1} must place the material "
                "spotlight on the left and its details on the right"
            )
    return {
        "name": name,
        "icon": icon,
        "category": "mobstoolforging:materials",
        "sortnum": sortnum,
        "pages": pages,
    }


def material_document() -> str:
    rows = [
        "# Forging Materials",
        "",
        "This file is generated by `tools/generate_forging_materials.py`.",
        "It records the pack-owned compatibility layer for Mobs Tool Forging.",
        "",
        "| Material | Input | Station | Tier (uses / speed / damage / enchant) | Trait |",
        "| --- | --- | --- | --- | --- |",
    ]
    for name, item, tier, trait in CANONICAL_GEMS:
        rows.append(f"| {name} | `{item}` | Lapidary Table | {tier} | {trait} |")
    trait_names = {
        **{trait_id: trait.name for trait_id, trait in CUSTOM_TRAITS.items()},
        "mobstoolforging:steady": "Steady",
        "mobstoolforging:kindled": "Kindled",
        "mobstoolforging:reinforced": "Reinforced",
        "mobstoolforging:resonant": "Resonant",
        "mobstoolforging:work_hardened": "Work-Hardened",
        "mobstoolforging:adamant": "Adamant",
        "mobstoolforging:nether_forged": "Nether-Forged",
        "mobstoolforging:fortunate": "Fortunate",
        "mobstoolforging:forceful": "Forceful",
    }
    for material in MATERIALS:
        station = "Tool Forge" if material.category == "metal" else "Lapidary Table"
        tier = f"{material.uses} / {material.mining_speed:g} / +{material.attack_damage:g} / {material.enchantment}"
        rows.append(
            f"| {material.name} | `{material.item}` | {station} | {tier} | {trait_names[material.trait]} |"
        )
    rows.extend(
        [
            "",
            "Ruby, Sapphire, and Topaz remain the built-in Mobs Tool Forging",
            "material identities. Their `c:gems/*` tags are supplied by this pack",
            "and point to the real Mythic Upgrades gems.",
            "",
            "## Preserved identities",
            "",
            "Mythic Upgrades' eight equipment families and Caverns & Chasms'",
            "Silver and Necromium use source-derived modular overlays generated by",
            "`tools/generate_forging_identity_assets.py`. The original colour work",
            "and highlights stay on each forged head while handles and guards remain",
            "independently swappable. Ruby, Sapphire, and Topaz armor also use the",
            "real Mythic item icons and worn layers.",
            "",
            "Pack traits with active behavior are defined under",
            "`mobstoolforging/trait_behaviors`. Their combat effects are datapack",
            "data, not hardcoded pack-specific branches in Mobs Tool Forging.",
            "",
            "Caverns & Chasms Tin remains a foundry-only bronze ingredient. Mythic",
            "gem-alloy ingots and crystal shards are deliberately excluded to avoid",
            "duplicate identities for the same gem.",
            "",
        ]
    )
    return "\n".join(rows)


def validate() -> None:
    material_ids = [material.id for material in MATERIALS]
    if len(material_ids) != len(set(material_ids)):
        raise ValueError("Duplicate material IDs")
    item_ids = [material.item for material in MATERIALS]
    if len(item_ids) != len(set(item_ids)):
        raise ValueError("One source item is assigned to more than one material")
    for material in MATERIALS:
        if material.trait.startswith("minecraft_beyond:") and material.trait not in CUSTOM_TRAITS:
            raise ValueError(f"Missing custom trait definition for {material.trait}")
        if material.category not in {"gem", "metal"}:
            raise ValueError(f"Unsupported category for {material.id}: {material.category}")
    for material in MATERIALS:
        if material.trait not in CUSTOM_TRAITS and material.trait not in BUILT_IN_TRAITS:
            raise ValueError(f"Missing guide copy for trait {material.trait}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail if generated files do not match the current material table.",
    )
    args = parser.parse_args()
    validate()
    files = generated_files()
    stale_guide_entries = [
        GUIDE_ENTRIES / f"{entry_id}.json"
        for entry_id in LEGACY_GUIDE_ENTRY_IDS
        if (GUIDE_ENTRIES / f"{entry_id}.json").exists()
    ]
    changed: list[Path] = []
    for path, content in files.items():
        current = path.read_text(encoding="utf-8") if path.exists() else None
        if current == content:
            continue
        changed.append(path)
        if not args.check:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")

    if not args.check:
        for path in stale_guide_entries:
            path.unlink()

    if args.check and (changed or stale_guide_entries):
        for path in changed:
            print(path.relative_to(ROOT))
        for path in stale_guide_entries:
            print(f"stale: {path.relative_to(ROOT)}")
        return 1
    action = "Would update" if args.check else "Updated"
    print(f"{action} {len(changed)} file(s); {len(MATERIALS)} materials are defined.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
