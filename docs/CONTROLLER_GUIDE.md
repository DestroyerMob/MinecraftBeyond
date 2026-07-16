# Controller Guide

Minecraft Beyond uses Controlify as its sole controller implementation. The pack includes full menu and inventory navigation, an on-screen keyboard, controller prompts, rumble, per-controller calibration, and pack-specific radial-menu defaults.

## Recommended Steam Setup

1. Launch Prism Launcher from Steam Gaming Mode or Big Picture Mode.
2. Start with a normal **Gamepad** Steam Input template. Avoid a WASD-and-mouse template because Controlify should receive native gamepad input.
3. Connect or wake the controller before opening the Minecraft instance. Hot-plugging is supported, but connecting first gives the cleanest first-run setup.
4. Complete Controlify's controller identification and calibration screen when prompted.

If Steam Input maps extra buttons or gyro to keyboard or mouse actions, enable **Mixed Input** in the selected controller's Controlify settings. Leave Mixed Input off for an ordinary gamepad-only layout so Minecraft can switch cleanly between controller and keyboard/mouse prompts.

Steam Deck users should play in Gaming Mode. Controlify's enhanced Steam Deck driver is optional and experimental; it requires Decky Loader. Standard SDL gamepad input works without it. The pack reserves the four back paddles, when the enhanced driver exposes them, for backpack, world map, previous knapping target, and next knapping target.

## Pack Controls

Controlify retains its familiar default layout:

- Left stick moves; right stick looks.
- South face button jumps; north face button opens inventory.
- Triggers use and attack; shoulder buttons cycle the hotbar.
- Left-stick click sprints; right-stick click sneaks.
- D-pad up opens chat, down drops, left picks a block, and right opens the radial menu.
- Start pauses; Back/Select changes perspective and toggles the virtual mouse on screens that need it.

The pack's radial menu puts these actions within reach:

- Xaero's world map
- Sophisticated Backpacks
- New Xaero waypoint
- Previous knapping target
- Next knapping target
- Bridging assist toggle
- Better Enchanting vein-mining mode
- Voice-chat microphone mute

For flint knapping, look at the placed flint with a knapping tool and sneak, then open the radial menu and select **Previous Knapping Target** or **Next Knapping Target**. Mouse players can continue to sneak-scroll. These are standard MTF key mappings, so they can also be rebound directly to any controller button in Controller Settings.

Open **Options → Controls → Controller Settings** to rebind any action. Bindings and calibration are saved separately for each controller, so changing one controller does not disturb another.

## Troubleshooting

- **No controller detected:** confirm Steam Input is presenting a gamepad, reconnect before launching, and check that Controlify—not Controllable—is enabled in the Mod Quality Picker profile.
- **Inputs flicker between mouse and controller:** use a pure Gamepad Steam Input template, or enable Mixed Input if keyboard/mouse emulation is intentional.
- **Stick drift:** rerun Controlify calibration before raising deadzones manually.
- **A modded screen will not navigate:** press Back/Select to toggle Controlify's virtual mouse, then use the sticks and face buttons.
- **Steam Deck controls disappear:** use Gaming Mode. If the optional enhanced driver causes trouble, disable it under Controlify's global settings and use the standard SDL driver.
