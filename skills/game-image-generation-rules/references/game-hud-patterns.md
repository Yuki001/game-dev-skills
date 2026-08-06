# Game HUD and gameplay-screen patterns

Use this file for complete gameplay-screen concepts in which the playable scene, camera, HUD regions, and visible game state must work together. Use `game-asset-patterns.md` instead for isolated buttons, panels, icons, portraits, maps, or other UI components.

Treat generated gameplay screens as visual specifications or presentation assets unless their components are separately reconstructed and validated. A convincing screenshot does not provide implementation-ready UI geometry.

## Whole-screen contract

Define before prompting:

- target platform, aspect ratio, capture state, and intended viewing size;
- genre, camera, playable space, player/enemy count, and current gameplay event;
- HUD regions, anchors, safe margins, hierarchy, and allowed scene occlusion;
- exact visible labels, numbers, icons, meters, cooldowns, selected states, and alerts;
- scene value grouping behind UI, contrast, palette, VFX density, and focal path;
- whether the deliverable is a gameplay screenshot, HUD concept, key art with light UI, or component specification.

Keep the scene readable without the HUD and the HUD readable without relying on decorative glow. Use fictional games, characters, marks, and interface language unless the user supplies authorized references.

## Native prompt schema

```text
Create one [platform] gameplay screen on a [canvas/aspect ratio]. It must read as captured gameplay, not a poster or UI component board.
GAME STATE: [genre, objective, player action, enemies/allies, environment event].
CAMERA: [projection, height, distance, framing, playable-space visibility].
HUD REGIONS: [top / bottom-left / bottom-right / side panels], with [safe margins and occlusion rules].
VISIBLE STATE: [exact labels, values, meters, cooldowns, selection, alerts, minimap contents].
ART DIRECTION: [rendering, palette, materials, lighting, VFX density].
READABILITY: preserve player, hazards, navigation routes, targets, and interactive objectives behind the interface.
AVOID: real game logos, unreadable microtext, decorative fake HUD marks, conflicting counters, cropped controls, poster composition, device mockup frame.
```

Evaluate scene readability, HUD hierarchy, state coherence, safe margins, exact text, and whether the screen communicates one plausible gameplay moment.

## Third-person action or open-world HUD

Use one shared layout contract, then choose only the modules relevant to the game:

- action-RPG boss encounter: health, stamina, consumables, boss bar, quest state, minimap;
- cyberpunk action: health, ammo, radar, stealth/energy, mission overlay;
- anime adventure: quest log, compass, character portrait, status effects, ability state.

```text
Create one original 16:9 third-person action-game screenshot. The protagonist is framed from an elevated over-the-shoulder camera while [performing one readable action] in [playable environment]. Preserve a clear route, target silhouette, player silhouette, and hazard separation.
HUD: top-center [objective or boss state]; top edge [compass or mission state]; bottom-left [portrait, health, stamina/status]; bottom-right [abilities, consumables, ammo or energy]; top-left [minimap or radar]. Use consistent icon language, aligned anchors, clean safe margins, and exact supplied values.
Integrate weather, lighting, materials, and restrained VFX without obscuring the player, enemy tells, route, or HUD. Make it feel like a premium gameplay capture, not key art, a cinematic still, or a dashboard mockup. Use original characters and no real game logos.
```

## Cinematic RPG exploration screen

```text
Create one original 16:9 fantasy-RPG exploration screen. A small fellowship crosses a colossal weathered bridge toward a luminous mountain city at sunrise: a ranger leads, a mage carries a lantern, and a compact armored smith bears a hammer. Use a third-person cinematic gameplay camera with a clearly walkable bridge, readable party silhouettes, distant navigation landmark, waterfalls, banners, layered valley depth, and controlled golden cloud light.
Keep the interface deliberately light: one exact quest objective, a directional compass, and one unobtrusive destination marker placed inside safe margins. Preserve gameplay readability and believable scale. The result may feel promotional, but must still read as an in-engine exploration view rather than a border-heavy poster. No franchise symbols, fake logos, dense combat HUD, or interface elements covering the party.
```

## Isometric pixel-RPG screen

```text
Create one 16:9 isometric pixel-RPG gameplay screen set in an original traditional village during blossom season. A player character practices one readable sword action in the central square while several NPCs watch from outside the action area. Use one locked isometric projection, crisp pixel clusters, no antialiasing, one coherent limited palette, readable paths and building entrances, and soft ambient daylight.
HUD: a compact inventory panel, stamina gauge, three ability cooldowns, and a short quest objective. Keep UI pixel scale, borders, icon style, palette, spacing, and text baseline consistent. Preserve a clear gameplay viewport and do not cover the player, NPCs, exits, or interaction targets. No mixed pixel resolutions, perspective drift, decorative fake kanji, real game logos, or poster framing.
```

## Mobile MOBA or lane-battle HUD

```text
Create one original 16:9 landscape mobile MOBA gameplay screen at a readable phone scale. Camera: elevated isometric third-person view over a fantasy lane and central river bridge. Show three stylized heroes, minion groups, terrain brush, turret silhouettes, a glowing neutral objective, and restrained spell effects with clear team and danger colors.
HUD: translucent virtual joystick bottom-left; four circular ability buttons bottom-right with exact cooldown values; ultimate visible but only 87% charged; minimap top-left; score "12 - 11" and timer "08:42" top-center; team health bars, item quick slots, and gold "3,420". Preserve thumb reach zones, mobile-safe margins, consistent icons, plausible state, and an unobstructed combat center. Make it look like a gameplay capture, not a poster or mockup board. No real game logos, contradictory values, unreadable text, or VFX covering ability tells.
```

## Isometric strategy or RTS HUD

```text
Create one original 16:9 isometric strategy-game screenshot of a mountainous village with rice terraces, gates, roads, and readable elevation changes. Show one selected formation of melee and ranged units, clear selection outlines, a destination marker, and one plausible command in progress. Use a locked isometric camera, consistent unit scale, warm daylight, soft down-right shadows, readable terrain ownership, and restrained low-poly rendering.
HUD: resource counters for rice and wood, fog-of-war minimap, selected-unit panel, command buttons, population state, and one concise objective. Keep panels aligned to safe margins and preserve the central tactical field. Use exact supplied labels and values, original iconography, and no real-game branding, fake microtext, hidden paths, inconsistent selection state, or cinematic depth of field that obscures units.
```

