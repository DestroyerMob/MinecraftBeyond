#!/usr/bin/env python3
"""Generate identity-preserving MTF overlays from equipment already in the pack.

The generated textures keep Mobs Tool Forging's modular silhouettes while
borrowing the source mod's actual pixel colours and accents.  Materials without
a native equipment set deliberately keep MTF's normal palette fallback.
"""

from __future__ import annotations

import argparse
import io
import json
import sys
import zipfile
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
ASSET_ROOT = ROOT / "pack" / "kubejs" / "assets"
MODS = ROOT / "minecraft" / "mods"
DEFAULT_MTF_SOURCE = Path.home() / "Documents" / "minecraft-mod-sources" / "MobsToolForging"


@dataclass(frozen=True)
class NativeSet:
    material: str
    jar_glob: str
    source_namespace: str
    source_prefix: str


NATIVE_SETS = (
    NativeSet("mythicupgrades:aquamarine", "mythicupgrades-*.jar", "mythicupgrades", "aquamarine"),
    NativeSet("mythicupgrades:citrine", "mythicupgrades-*.jar", "mythicupgrades", "citrine"),
    NativeSet("mobstoolforging:topaz", "mythicupgrades-*.jar", "mythicupgrades", "topaz"),
    NativeSet("mythicupgrades:peridot", "mythicupgrades-*.jar", "mythicupgrades", "peridot"),
    NativeSet("mobstoolforging:ruby", "mythicupgrades-*.jar", "mythicupgrades", "ruby"),
    NativeSet("mobstoolforging:sapphire", "mythicupgrades-*.jar", "mythicupgrades", "sapphire"),
    NativeSet("mythicupgrades:jade", "mythicupgrades-*.jar", "mythicupgrades", "jade"),
    NativeSet("mythicupgrades:ametrine", "mythicupgrades-*.jar", "mythicupgrades", "ametrine"),
    NativeSet("caverns_and_chasms:silver", "caverns_and_chasms-*.jar", "caverns_and_chasms", "silver"),
    NativeSet("caverns_and_chasms:necromium", "caverns_and_chasms-*.jar", "caverns_and_chasms", "necromium"),
)


# (MTF slot, MTF template, source tool, usage)
OUTPUTS = (
    ("sword_blade", "sword/sword_blade.png", "sword", "tool"),
    ("sword_blade", "sword/sword_blade_part.png", "sword", "part"),
    ("guard", "sword/guard.png", "sword", "tool"),
    ("guard", "sword/guard_part.png", "sword", "part"),
    ("pickaxe_head", "pickaxe/pickaxe_head.png", "pickaxe", "tool"),
    ("pickaxe_head", "pickaxe/pickaxe_head_part.png", "pickaxe", "part"),
    ("axe_head", "axe/axe_head.png", "axe", "tool"),
    ("axe_head", "axe/axe_head_part.png", "axe", "part"),
    ("shovel_head", "shovel/shovel_head.png", "shovel", "tool"),
    ("shovel_head", "shovel/shovel_head_part.png", "shovel", "part"),
    ("hoe_head", "hoe/hoe_head.png", "hoe", "tool"),
    ("hoe_head", "hoe/hoe_head_part.png", "hoe", "part"),
    ("mattock_tool_axe", "mattock/mattock_tool_axe.png", "axe", "tool"),
    ("mattock_tool_hoe", "mattock/mattock_tool_hoe.png", "hoe", "tool"),
    ("crossbow_limbs", "crossbow_limbs.png", "pickaxe", "tool"),
    ("crossbow_limbs", "crossbow_limbs.png", "pickaxe", "part"),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail if generated files differ")
    parser.add_argument("--mtf-source", type=Path, default=DEFAULT_MTF_SOURCE)
    return parser.parse_args()


def locate_jar(pattern: str) -> Path:
    matches = sorted(MODS.glob(pattern))
    if len(matches) != 1:
        raise RuntimeError(f"expected one {pattern!r} in {MODS}, found {len(matches)}")
    return matches[0]


def source_image(archive: zipfile.ZipFile, native: NativeSet, tool: str) -> Image.Image:
    resource = (
        f"assets/{native.source_namespace}/textures/item/"
        f"{native.source_prefix}_{tool}.png"
    )
    return Image.open(io.BytesIO(archive.read(resource))).convert("RGBA")


def useful_palette(image: Image.Image) -> list[tuple[int, int, int, int]]:
    colours = Counter(
        pixel for pixel in image.get_flattened_data()
        if pixel[3] > 0 and max(pixel[:3]) - min(pixel[:3]) > 5
    )
    if len(colours) < 4:
        colours = Counter(pixel for pixel in image.get_flattened_data() if pixel[3] > 0)
    selected = [colour for colour, _ in colours.most_common(12)]
    selected.sort(key=lambda c: (0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]))
    if not selected:
        raise RuntimeError("source equipment texture has no opaque pixels")
    return selected


def nearest_opaque(image: Image.Image, x: int, y: int) -> tuple[int, int, int, int] | None:
    for radius in range(1, 6):
        candidates: list[tuple[int, int, int, int]] = []
        for iy in range(max(0, y - radius), min(image.height, y + radius + 1)):
            for ix in range(max(0, x - radius), min(image.width, x + radius + 1)):
                if abs(ix - x) != radius and abs(iy - y) != radius:
                    continue
                pixel = image.getpixel((ix, iy))
                if pixel[3] > 0:
                    candidates.append(pixel)
        if candidates:
            return candidates[(x + y) % len(candidates)]
    return None


def compose(mask: Image.Image, source: Image.Image, preserve_alignment: bool) -> Image.Image:
    mask = mask.convert("RGBA")
    source = source.resize(mask.size, Image.Resampling.NEAREST)
    palette = useful_palette(source)
    result = Image.new("RGBA", mask.size)

    for y in range(mask.height):
        for x in range(mask.width):
            mask_pixel = mask.getpixel((x, y))
            if mask_pixel[3] == 0:
                continue
            source_pixel = source.getpixel((x, y))
            if preserve_alignment and source_pixel[3] > 0:
                colour = source_pixel
            elif preserve_alignment:
                colour = nearest_opaque(source, x, y)
            else:
                luminance = (mask_pixel[0] + mask_pixel[1] + mask_pixel[2]) / (3 * 255)
                index = round(luminance * (len(palette) - 1))
                # Preserve a little of the source texture's native checker/accent rhythm.
                index = max(0, min(len(palette) - 1, index + ((x * 3 + y * 5) % 5 == 0)))
                colour = palette[index]
            if colour is None:
                colour = palette[len(palette) // 2]
            result.putpixel((x, y), (*colour[:3], mask_pixel[3]))
    return result


def generated_pngs(mtf_source: Path) -> dict[Path, bytes]:
    template_root = (
        mtf_source
        / "src"
        / "main"
        / "resources"
        / "assets"
        / "mobstoolforging"
        / "textures"
        / "tool_templates"
    )
    generated: dict[Path, bytes] = {}
    archives: dict[Path, zipfile.ZipFile] = {}
    try:
        for native in NATIVE_SETS:
            jar = locate_jar(native.jar_glob)
            archive = archives.setdefault(jar, zipfile.ZipFile(jar))
            source_cache: dict[str, Image.Image] = {}
            namespace, material_path = native.material.split(":", 1)
            output_dir = (
                ASSET_ROOT
                / namespace
                / "textures"
                / "source"
                / "tool_parts"
                / material_path
            )
            for slot, template_name, source_tool, usage in OUTPUTS:
                source = source_cache.setdefault(
                    source_tool, source_image(archive, native, source_tool)
                )
                template_path = template_root / template_name
                if template_name == "crossbow_limbs.png":
                    template_path = (
                        mtf_source
                        / "src"
                        / "main"
                        / "resources"
                        / "assets"
                        / "mobstoolforging"
                        / "textures"
                        / "item"
                        / template_name
                    )
                mask = Image.open(template_path)
                image = compose(mask, source, preserve_alignment=usage == "tool")
                buffer = io.BytesIO()
                image.save(buffer, "PNG", optimize=False)
                output = output_dir / f"{material_path}_{slot}_{usage}.png"
                generated[output] = buffer.getvalue()
    finally:
        for archive in archives.values():
            archive.close()
    return generated


def generated_tool_visuals(mtf_source: Path) -> dict[Path, bytes]:
    source_root = (
        mtf_source
        / "src"
        / "generated"
        / "resources"
        / "assets"
        / "mobstoolforging"
        / "tooling"
        / "tool_visuals"
    )
    generated: dict[Path, bytes] = {}
    for source in sorted(source_root.glob("*.json")):
        data = json.loads(source.read_text())
        for layer in data.get("layers", []):
            material_from = layer.get("material_from")
            if material_from in {"headMaterial", "guardMaterial"}:
                layer["texture_pattern"] = (
                    "source/tool_parts/{material}/{material}_"
                    + layer["slot"]
                    + "_{usage}"
                )
        output = (
            ASSET_ROOT
            / "mobstoolforging"
            / "tooling"
            / "tool_visuals"
            / source.name
        )
        generated[output] = (json.dumps(data, indent=2) + "\n").encode()
    return generated


def generated_armor_visuals() -> dict[Path, bytes]:
    generated: dict[Path, bytes] = {}
    for material in ("ruby", "sapphire", "topaz"):
        data = {
            "material": f"mobstoolforging:{material}",
            "texture": f"mythicupgrades:item/{material}",
            "item_textures": {
                role: f"mythicupgrades:item/{material}_{role}"
                for role in ("helmet", "chestplate", "leggings", "boots")
            },
            "worn_textures": {
                "layer_1": f"mythicupgrades:textures/models/armor/{material}_layer_1.png",
                "layer_2": f"mythicupgrades:textures/models/armor/{material}_layer_2.png",
            },
        }
        output = (
            ASSET_ROOT
            / "mobstoolforging"
            / "tooling"
            / "armor_material_textures"
            / f"{material}.json"
        )
        generated[output] = (json.dumps(data, indent=2) + "\n").encode()
    return generated


def write_or_check(generated: dict[Path, bytes], check: bool) -> int:
    mismatches: list[Path] = []
    legacy = sorted(ASSET_ROOT.glob("*/textures/source/tool_parts/*/*_sword_guard_*.png"))
    if check:
        mismatches.extend(legacy)
    else:
        for path in legacy:
            path.unlink()
    for path, content in generated.items():
        if not path.exists() or path.read_bytes() != content:
            mismatches.append(path)
            if not check:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(content)
    if mismatches and check:
        print("Forging identity assets are stale:", file=sys.stderr)
        for path in mismatches:
            print(f"  {path.relative_to(ROOT)}", file=sys.stderr)
        return 1
    action = "checked" if check else "generated"
    print(f"{action} {len(generated)} identity asset(s)")
    return 0


def main() -> int:
    args = parse_args()
    mtf_source = args.mtf_source.expanduser().resolve()
    generated = {}
    generated.update(generated_pngs(mtf_source))
    generated.update(generated_tool_visuals(mtf_source))
    generated.update(generated_armor_visuals())
    return write_or_check(generated, args.check)


if __name__ == "__main__":
    raise SystemExit(main())
