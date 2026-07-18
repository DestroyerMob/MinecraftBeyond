# Controller Guide

Minecraft Beyond uses Controlify as its sole controller implementation. The pack includes standard menu and inventory navigation, an on-screen keyboard, controller prompts, rumble, per-controller calibration, pack-specific radial-menu defaults, and native focus targets in the pack's most important custom screens.

## Recommended Steam Setup

1. Launch Prism Launcher from Steam Gaming Mode or Big Picture Mode.
2. Start with a normal **Gamepad** Steam Input template. Avoid a WASD-and-mouse template because Controlify should receive native gamepad input.
3. Connect or wake the controller before opening the Minecraft instance. Hot-plugging is supported, but connecting first gives the cleanest first-run setup.
4. Complete Controlify's controller identification and calibration screen when prompted.

The pack enables **Mixed Input** for new controller profiles so Steam Input can map extra buttons or gyro to keyboard and mouse actions. Existing controller profiles retain their previous setting; enable Mixed Input in that controller's Controlify settings if it is currently off.

Steam Deck users should play in Gaming Mode. Controlify 3.0.1 currently disables its enhanced Steam Deck driver because of a SteamOS compatibility break, so back paddles are not exposed as native controller buttons. In Steam Input, map **L4 to F6** and **R4 to F7** for Previous and Next Knapping Target. Standard SDL gamepad input handles the rest of the layout.

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

For flint knapping, look at the placed flint with a knapping tool, open the radial menu, and select **Previous Knapping Target** or **Next Knapping Target**. The dedicated actions do not require sneaking and wait briefly for the radial screen to close before applying. Mouse players can continue to sneak-scroll. These are standard MTF key mappings, so they can also be rebound directly to any controller button in Controller Settings or mapped through Steam Input as F6/F7.

Better Enchanting exposes **Activate Flash Step** as a dedicated controller-bindable action in addition to its double-forward gesture. It is unbound by default so it does not displace a standard gamepad control. Assign it under Controller Settings or map an extra Steam Input button to it. Vein-miner mode and Ecology's bee-route lock also wait briefly for a radial or controller screen to close, so controller-triggered actions are not lost.

## Local Mod Screens

The following custom interfaces support D-pad/stick focus navigation and the normal confirm/back buttons:

- Better Enchanting's table offers, routed-enchantment tuning, and Attunement Pedestal upgrades.
- Mobs Tool Forging's template picker and pattern-creation grid. The pattern grid includes focusable page controls when more recipes are available.
- Mobs Storage's Network Manager, including network selection, member removal, and list paging. Terminal search, sort controls, and text fields use standard widgets and the on-screen keyboard.
- Mod Quality Picker's profile and mod lists, including focusable paging regions alongside the scrollbar.

Custom item grids and particularly dense third-party screens may still be easier with Controlify's virtual mouse. Press Back/Select to toggle it for the current screen.

Open **Options → Controls → Controller Settings** to rebind any action. Bindings and calibration are saved separately for each controller, so changing one controller does not disturb another.

## Troubleshooting

- **No controller detected:** confirm Steam Input is presenting a gamepad, reconnect before launching, and check that Controlify—not Controllable—is enabled in the Mod Quality Picker profile.
- **Inputs flicker between mouse and controller:** use a pure Gamepad Steam Input template, or enable Mixed Input if keyboard/mouse emulation is intentional.
- **Stick drift:** rerun Controlify calibration before raising deadzones manually.
- **A modded screen will not navigate:** press Back/Select to toggle Controlify's virtual mouse, then use the sticks and face buttons.
- **Steam Deck paddles do nothing:** Controlify 3.0.1 cannot expose them natively. Map the paddles to F6/F7 in Steam Input and make sure Mixed Input is enabled in Controlify.

## Hardware Test Checklist

1. Confirm the controller is detected and complete calibration.
2. Test movement, camera, attack/use, sprint, sneak, hotbar cycling, inventory slots, chat, and the on-screen keyboard.
3. Open the radial menu and test both knapping directions and Better Enchanting's vein-miner toggle.
4. Bind **Activate Flash Step** to a spare button and verify it works alongside the double-forward gesture.
5. Navigate each local-mod screen listed above using only D-pad/stick, confirm, and back.
6. In Mobs Storage, test terminal searching, network selection and paging, and any inventory action you bind in Controller Settings.
7. Toggle the virtual mouse on a custom item grid, then verify cursor movement, left/right click, shift-click, and scrolling.
8. Reconnect the controller while the game is open and verify the input prompts recover cleanly.
