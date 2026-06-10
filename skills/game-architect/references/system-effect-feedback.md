# Effect & Feedback System Architecture

This reference covers **gameplay feedback** — the translation layer between game logic events and sensory output (visual, audio, haptic). It provides a unified feedback layer architecture and a categorized reference for individual feedback types.

Feedback here means **game-logic-neutral effects** that change what the player perceives, not gameplay state. Character movement with gameplay collision is not feedback; a screen shake on landing is. Spawning an enemy is not feedback; spawning dust particles on impact is.

**IMPORTANT NOTE**: This reference is engine-agnostic. Names like `SpawnVFX` are conceptual, not API-specific.

---

# Part 1: Feedback Architecture

## 1. Positioning & Design Principles

The feedback layer sits between gameplay systems (combat, skill, 3C, narrative, UI) and the player's senses. It translates semantic events (`OnHit`, `OnLanding`, `OnDeath`) into sensory output (`ScreenShake`, `HitFlash`, `SFX`, `FloatingText`).

### Core Principles

- **Decoupling**: Gameplay systems emit semantic events without knowing how they are rendered. The feedback layer subscribes and translates. A `OnHeavyHit` event may trigger shake + flash + SFX + haptics — the combat system doesn't know or care.
- **Degradable**: Feedback can be simplified or skipped under performance pressure without affecting gameplay correctness. A missed screen shake is better than a missed attack registration.
- **Centralized Configuration**: Feedback parameters (duration, intensity, decay curves) live in the feedback layer, not scattered across gameplay code. Designers tune feedback without touching combat logic.
- **Engine-Agnostic**: Interfaces and structure don't bind to a specific engine API. `SpawnVFX` not `PlayUnityParticleSystem`.

### When to Build a Unified Layer

A unified feedback layer is warranted when:
- Multiple gameplay systems need to trigger the same types of feedback
- You want consistent feedback authoring (tuning one shake shouldn't require touching 5 files)
- Performance-driven feedback culling needs a single decision point
- The team includes dedicated feedback/VFX roles separate from gameplay programmers

For prototypes or very small scopes, direct inline feedback calls are acceptable. The unified layer can be introduced during refactoring.

---

## 2. Core Structure

### Architecture Overview

The feedback layer flows through three concepts:

```
Gameplay Event ──→ Feedback Routine ──→ Feedback Instances
      │                                    │
      └──── Feedback Context ──────────────┘
           (position, intensity, actors...)
```

- **Gameplay Event**: a semantic signal from gameplay code — `"HitReceived"`, `"Landing"`, `"Death"`. The sender knows *what happened*; it does not know what feedbacks will play.
- **Feedback Routine**: the pre-configured mapping from an event to a set of feedback entries. Defines *what to play* and with what parameters. Can be implemented as hardcoded code, a data table, or a script.
- **Feedback Context**: the runtime data payload carried from gameplay event to routine — position, direction, intensity (0–1), source/target actor references. The routine uses these as input parameters for its entries.
- **Feedback Instance**: a single running feedback (one ScreenShake, one SFX, one FloatingText). Created from a routine entry, drawn from an object pool, played, then recycled. Each instance has its own independent lifecycle.

### Routine Forms

A routine can be defined in three ways:

| Form | Where the Routine Lives | When to Use |
|:---|:---|:---|
| **Hardcoded** | Source code | Prototypes, simple feedback sets, high-frequency combat paths |
| **Data Table** | Config (JSON, Excel, CSV) — designer-authored | Content-heavy games, iteration without code changes |
| **Script-Driven** | External script (Lua, DSL) or node graph — hot-reloadable | Visual scripting, rapid tuning without recompilation |

Example of a DSL routine:

```
Routine "HitReceived" {
    ScreenShake   { mode: trauma, intensity: context.intensity * 0.8 }
    HitFlash      { target: context.targetActor, color: white, duration: 0.1s }
    SFX           { clip: "impact_heavy", volume: context.intensity }
    FloatingText  { pos: context.position, text: damageValue, style: damage }
}
```

### Routine Composition

A routine is a **container** of one or more feedback entries. When triggered, each entry resolves into an individual **feedback instance**.

```
Routine "HitReceived"          ← one routine (container)
    ├── ScreenShake (entry)    → creates a ScreenShake instance
    ├── HitFlash    (entry)    → creates a HitFlash instance
    ├── SFX         (entry)    → creates an SFX instance
    └── FloatingText(entry)    → creates a FloatingText instance
```

Instances from the same routine run in parallel by default, or in a configured sequence (see §9.1). Each instance has its own independent lifecycle, managed by the feedback layer.

### Feedback Instance Lifecycle

Each concrete feedback type follows the same lifecycle:

```
Create → Play → [Stop/Interrupt] → Recycle
```

- **Create**: Initialize from the routine entry's parameters combined with `FeedbackContext` (position, direction, intensity, actor references). Pooled instances are reused; new instances are allocated only when the pool is exhausted.
- **Play**: Start playback. Can be synchronous (one-shot) or asynchronous (duration-based).
- **Stop/Interrupt**: Prematurely terminate by higher-priority feedback or actor destruction.
- **Recycle**: Return to pool, reset all mutable state.

### Priority & Merge Strategy

Each feedback type has a default priority. On conflict (same type triggered simultaneously on the same target), one of four strategies applies:

| Strategy | Behavior | Example Use |
|:---|:---|:---|
| **Replace** | New feedback replaces the currently playing one | Screen shake — new heavy hit replaces old shake |
| **Merge** | Combine intensity with the current one via a cap | Screen shake — additive trauma model |
| **Queue** | Enqueue and play after the current one finishes | Sequential floating text entries |
| **Ignore** | Discard the new one if the current one is stronger | Light hit during a heavy hit shake |

### Global Throttling

A global manager caps total concurrent feedback instances. When the cap is hit, culling follows this order:
1. Distance: furthest from camera/player first
2. Priority: lowest priority feedback first
3. Age: oldest feedback first (fairness within same tier)

This is particularly critical on mobile and during combat-heavy moments (many on-screen hits).

---

## 3. Interface with External Systems

### How Gameplay Systems Trigger Feedback

Three patterns:

**Hardcoded** (high-frequency, combat paths):
```
feedbackLayer.Play("HitReceived", new FeedbackContext {
    position = hitPoint,
    direction = attackDirection,
    intensity = damage / maxHealth,  // normalized 0-1
    sourceActor = attacker,
    targetActor = victim
});
```

**Event-driven** (low-frequency, UI, narrative):
```
// Gameplay system emits an event
EventBus.Emit(new HitReceivedEvent(...));

// Feedback layer subscribes
feedbackLayer.Subscribe<HitReceivedEvent>(OnHitReceived);
```

**Table-driven** (routine name resolved via config lookup):
```
routineName = EnemyConfig.GetRoutine(damageType)   // e.g. "fire" → "FireHitFeedback"
context.intensity = EnemyConfig.GetHitIntensity(damageType)
feedbackLayer.Play(routineName, context)
```

Prefer hardcoded for combat and skill hot paths; event-driven for UI, quest, and narrative; table-driven for data-heavy configurations such as combat entities (enemies, bosses, etc.).

### FeedbackContext

A common data structure passed from gameplay to feedback layer:

| Field | Type | Description |
|:---|:---|:---|
| `Position` | Vector3 | World position for VFX, floating text placement |
| `Direction` | Vector3 | Impact direction for directional shake and VFX rotation |
| `Intensity` | float (0-1) | Normalized strength — drives shake amplitude, flash opacity, SFX volume |
| `SourceActor` | Actor ref (nullable) | Attacker for position attachment and look-at feedback |
| `TargetActor` | Actor ref (nullable) | Victim/receiver for attachment |
| `SourceType` | enum | Damage type or interaction category — influences feedback selection (fire hits get different VFX than physical hits) |
| `Tags` | string set | Arbitrary tags for filtering and routing |

---

# Part 2: Concrete Feedback Types

## 4. Screen & Camera Feedback

### 4.1 Screen Shake

Shake is the most visceral feedback channel. Two architectural models:

**Trauma-based** (recommended):
- A `trauma` value (0-1) accumulates from triggering events.
- Each frame: `shake = maxOffset * trauma * trauma` (quadratic falloff for perceptually linear decay).
- Trauma decays at a configurable rate per second.
- Multiple events add trauma (capped at 1.0) — natural merging without per-instance tracking.

**Parametric** (explicit control):
- Direct amplitude, frequency, and duration per shake instance.
- Simpler to understand, harder to merge cleanly.
- Use when each shake needs distinct characteristics (e.g., earthquake vs. gun recoil).

Key parameters: `amplitude`, `frequency`, `duration`, `decayCurve`, `directionConstraint` (horizontal-only, vertical-only).

**Common pitfalls**:
- Continuous shake causes motion sickness — always provide a disable option and cap trauma at reasonable levels.
- Shake + hit-stop overlay can produce visual jitter — consider pausing shake decay during freeze frames.
- Shake on camera spring arm vs. shake on character body produce different feels — decide which node gets the shake based on perspective.

### 4.2 Post-Processing Effects

Temporary full-screen visual modulation driven by gameplay events.

| Effect | Typical Use | Key Parameters |
|:---|:---|:---|
| **Bloom** | Power-up activation, critical hit glow | Intensity, threshold, duration |
| **Chromatic Aberration** | Near-death edge distortion, screen-edge damage indicator | Intensity (radial), duration |
| **Color Grading** | Low-health desaturation, poison green tint, berserk red shift | Saturation, hue shift, contrast, duration |
| **Vignette** | Low-health tunnel vision, hit impact darkening | Intensity, smoothness, duration |
| **Lens Distortion** | Stun/disorientation effect, heavy impact | Intensity, duration |

**Implementation notes**:
- Tween volume weights rather than modifying per-effect parameters directly — simpler to manage and reset.
- Multiple post-processing effects often share one volume profile. Use a priority stack: the highest-priority request controls the volume, lower ones are ignored.
- Post-processing is expensive on mobile — provide a quality tier that disables all but the most critical effects (vignette for low health).

### 4.3 Camera Effects

Effects applied directly to camera properties beyond shake and post-processing.

| Effect | Typical Use | Key Parameters |
|:---|:---|:---|
| **Zoom** | Ultimate ability activation, sniper aim, interaction focus | Target FOV, duration, ease curve |
| **Flash** | Explosion, respawn, lightning strike | Color, opacity, duration, fade curve |
| **Fade** | Scene transition, death screen, area entry/exit | Color, target opacity, duration |
| **Dynamic FOV** | Speed lines (FOV widen at high speed) | Target FOV delta, transition speed |

**Implementation notes**:
- FOV changes and screen shake should be mutually exclusive or one suppressed during the other — the combination is disorienting.
- Flash with pure white at full opacity for even 100ms is painful — cap opacity at ~0.7 and use off-white.
- Multiple fade requests should resolve to the most opaque one, not sum.

---

## 5. Entity & World Feedback

### 5.1 Particles / VFX

Visual effects spawned in the game world as feedback.

**Attachment modes**:
- **World**: Fixed position, independent of source/target movement (impact spark, environmental dust)
- **Attached**: Follows a bone or transform (aura, burning effect, weapon trail)
- **Follow**: Tracks an actor but with position lag (loosely-following motes)

**Lifecycle**:
- **One-shot**: Play once and recycle (hit spark, footstep dust). Most common.
- **Sustained**: Play while a state persists (aura, burning, shield glow). Tied to a gameplay condition.
- **Looped**: Independently repeating (ambient environmental VFX). Rare for reactive feedback.

**Pooling strategy**:
- Per-VFX-type pools with pre-warmed instances.
- One-shot VFX auto-return to pool on completion.
- Sustained VFX return to pool when the bound state ends (shield broken, buff expired).

**Distance LOD**:
- Near: full VFX with all particle layers.
- Mid: simplified VFX (fewer particles, lower texture resolution).
- Far: skip entirely or replace with a cheap sprite flash.

**Common pitfalls**:
- Attached VFX that doesn't detach on actor destruction/deactivation (orphaned particles floating mid-air).
- Pool exhaustion causing `Instantiate` spikes — always pre-warm pools based on expected peak concurrency.
- Too many simultaneous sustained VFX on the same actor — set a per-actor cap.

### 5.2 Transform Animation

Short-lived, purely visual transform modifications — distinct from gameplay-driven movement.

| Type | Behavior | Typical Use |
|:---|:---|:---|
| **Bump** | Quick scale pulse (up then back) | Icon pickup, button press, landing impact |
| **Squash & Stretch** | Deform on one axis, compensate on others to preserve volume | Landing, dash, attack wind-up |
| **Wiggle** | Rapid oscillating rotation/position/scale | Damage shake, idle nervous twitch |
| **Spring** | Spring-physics-driven return to rest position | UI element settling, character idle sway |
| **LookAt** | Temporarily rotate to face a point | Reactive head-turn on nearby sound |

**Implementation notes**:
- Multiple transform animations on the same object: additive overlay vs. last-wins. Additive is more natural for multi-source feedback (e.g., being hit from three directions simultaneously).
- Squash & stretch on physics bodies: must apply to the visual mesh only, not the collision capsule.
- Decay is critical — a wiggle with zero damping runs forever.

**Common pitfalls**:
- Transform animation on the root bone breaks attached equipment and IK targets — animate a dedicated visual-only child node.
- Accumulated scale drift over many bump animations — always use absolute targets, never relative increments.

### 5.3 Material / Shader Effects

Temporary visual changes to an entity's surface appearance.

| Effect | Behavior | Typical Use |
|:---|:---|:---|
| **Hit Flash** | Briefly set emissive/color to white, then fade back | Damage received |
| **Dissolve** | Fragment and fade out via alpha clip/noise threshold | Death, despawn, teleport out |
| **Flicker** | Rapidly toggle visibility or emissive | Low-health warning, incoming attack telegraph |
| **Outline Highlight** | Draw a colored silhouette | Target lock-on, interactable object glow |
| **UV Scroll** | Animate texture offset | Energy flow on a weapon, water surface |

**Material instance strategy**:
- **Shared material**: One material used by all entities of a type. Modifying it affects all. Fast, but can't target a single instance. Use for global effects (skybox flash).
- **Runtime material instances**: A per-entity copy of the material. Allows per-instance effects without side effects. Use for hit flash on individual enemies. Critical: dispose instances when the entity is destroyed or the effect ends.
- **Property block**: An engine-level mechanism to override material values per-renderer without creating material instances. Lighter weight. Prefer when the engine supports it.

**Common pitfalls**:
- Hit flash that creates a material instance and never releases it — rapid hits on many enemies create hundreds of leaked instances.
- Applying a material effect to a shared material — every enemy on screen flashes simultaneously.
- Dissolve that doesn't account for LOD — distant entities dissolve at a different rate or not at all.

### 5.4 Floating Text / Damage Numbers

World-space or screen-space text spawned as reaction to value changes.

**Core behavior**: Spawn at a world position, float upward, fade out, recycle.

Key parameters:
- `initialOffset`: random scatter around spawn point (prevents stacking)
- `travelCurve`: displacement over lifetime (typically arc up + slight drift)
- `fadeCurve`: alpha over lifetime
- `style`: color, size, font per value type (damage = red, heal = green, crit = large + yellow + shake)
- `lifetime`: duration before recycle

**Layout & queuing**:
- Multiple simultaneous numbers need horizontal offset to prevent overlap.
- Queue approach: assign each number a slot index, offset horizontally by `slotIndex * spacing`.
- Alternatively: add random velocity drift so numbers naturally separate.

**Canvas strategy**:
- World-space Canvas: numbers exist in 3D, occluded by geometry. Good for immersion.
- Screen-space Canvas: numbers are always visible but require world-to-screen projection. Good for readability.

**Common pitfalls**:
- Dense combat producing hundreds of overlapping numbers — cap visible count per actor and per screen region.
- Canvas rebuild cost when many text elements change simultaneously — use object pooling with pre-created elements, not instantiate-on-demand.
- Numbers spawning inside geometry (walls, floor) — offset upward from hit point, not exact hit position.

---

## 6. UI & HUD Feedback

### 6.1 UI Element Animation

Feedback on UI elements triggered by gameplay events or direct interaction.

**Common patterns**:
- **Button press**: Scale down on press (95%), scale back + slight overshoot on release. Duration 100-200ms.
- **Icon shake**: Skill off cooldown, quest available, item received. Rotation oscillation with decay.
- **Health/Resource bar**: Value change triggers a two-phase animation — instant white flash (hit), then smooth lerp to new value over 200-400ms. Optional: a secondary "ghost" bar that trails the main bar with a delay.
- **Item acquisition popup**: Scale from 0 → overshoot → settle, with a bounce curve.
- **Critical state pulsing**: Low health / low ammo — looping alpha or scale pulse. Stop pulsing when state resolves.

**Implementation notes**:
- UI animations must check panel visibility — an inventory shake should not play if the inventory is closed.
- Rapid value changes (DOT ticks, machine gun damage) should skip intermediate animations and jump to final value.
- Layout Rebuild is expensive — avoid animating `LayoutElement` properties (preferredWidth/Height). Animate scale, color, or use a separate non-layout canvas overlay instead.

---

## 7. Time Feedback

### 7.1 Hit-Stop / Freeze Frame

Momentarily freeze or slow time on impact to emphasize weight.

Key parameters:
- `duration`: typically 30-80ms. Longer than 100ms feels like a bug.
- `timeScale`: typically 0 (full freeze) or 0.05-0.1 (near-freeze with subtle movement).
- `restoreCurve`: how time returns to normal — instant or eased. Instant is more common for hit-stop; eased for slow-motion exit.

**Channel isolation**: Not all systems should freeze:
- **Freeze**: Rendering, physics simulation, gameplay logic.
- **Don't freeze**: Audio (pop/crack on time scale change), UI animations (menus still responsive), input polling (buffered input should still be captured), network message processing (don't delay sync).

**Nested hit-stop**: What happens when a second freeze triggers while one is active?
- Restart the freeze timer with the new duration (common for action games).
- Ignore the new freeze if the current one is stronger (intensity-based gate).
- Never extend — the freeze timer continues and the second request is discarded (safe default).

**Common pitfalls**:
- Freezing audio causes audible glitches — always exclude audio from time scale changes.
- Hit-stop that freezes the input buffer prevents the player from queuing the next action — exclude input.
- Continuous rapid hits (minigun, DOT) freeze-locking the game — set a minimum gap between freeze activations (e.g., one freeze per 200ms).

### 7.2 Slow Motion / Time Scale

Sustained time slowdown for dramatic effect, distinct from momentary hit-stop.

Key parameters:
- `targetTimeScale`: typically 0.2-0.5 (20%-50% normal speed).
- `transitionDuration`: time to reach target scale. Instant for reactive slowdown, eased for cinematic.
- `sustainDuration`: how long to hold the slow scale before restoring.

**Stacking**: Multiple time scale requests must resolve cleanly:
- Minimum-wins: the slowest request determines the time scale. Useful for gameplay-driven slowdowns (multiple abilities slowing time simultaneously).
- Last-wins: the newest request overrides. Simpler but prone to abuse.

**What ignores time scale**: Same exclusion list as hit-stop — audio, UI, input, network.

**Common pitfalls**:
- Slow motion becoming the "normal" feel — overuse desensitizes the player and makes normal speed feel rushed.
- Input feel degrades under sustained slow motion — consider scaling input sensitivity proportionally.
- Timer-based logic (cooldowns, DOT intervals) must use unscaled delta time or they desync.

---

## 8. Audio & Haptic Feedback

### 8.1 Sound Effect Triggering

Gameplay-driven SFX, distinct from the audio infrastructure (see `system-foundation.md` for that).

**Feedback-driven audio parameters**:
- `pitchRange`: random pitch variation (e.g., [0.95, 1.05]) — prevents identical consecutive sounds feeling robotic.
- `volumeScale`: derived from `FeedbackContext.Intensity` — a heavy hit plays louder.
- `spatialBlend`: 2D (UI sounds) or 3D (world sounds).
- `priority`: when the voice count limit is reached, lower-priority sounds are culled first.

**Sync timing with visual feedback**: For impact-heavy events, the SFX onset must align with the hit-stop decision:
- Option A: Play SFX just before the freeze starts (player hears impact during the freeze).
- Option B: Play SFX on the freeze frame itself, with audio excluded from time scale — the sound plays at normal speed during the visual freeze.

**Common pitfalls**:
- Voice/instance limit exhaustion — the 51st simultaneous sound is silent. Prioritize and cull by distance + importance.
- Playing the same sound for every pellet of a shotgun blast — batch into one composite sound with adjusted volume.

### 8.2 Haptics / Vibration

Tactile feedback triggered by gameplay events.

Key parameters:
- `amplitude` (0-1): vibration strength.
- `frequency` (loosely mapped, platform-dependent): low = heavy thud, high = sharp click.
- `duration`: continuous or transient.
- `modulationCurve`: amplitude envelope over time (fade in, fade out, pulse).

**Multi-source merging**: Multiple vibration requests within the same frame must be resolved:
- Highest-amplitude wins (simplest).
- Weighted blend of all active sources (more nuanced but harder to tune).

**Platform abstraction**:
- Console controllers: haptic motors (rumble + trigger resistance). Rich capabilities.
- Mobile: haptic engine APIs (CoreHaptics on iOS, VibrationEffect on Android). Limited but improving.
- No haptics: graceful no-op, no error.

**Common pitfalls**:
- Continuous vibration drains mobile battery and causes physical discomfort — always provide a disable toggle and enforce a maximum continuous duration.
- Vibration that's out of sync with audio and visual — test with real hardware, not simulator.

---

## 9. Orchestration & Composition

### 9.1 Feedback Sequences

Multiple feedbacks played sequentially as one logical unit.

**Structure**: An ordered list of feedback entries, each with an optional `delayOffset` from the previous entry's start or end.

Key parameters:
- `entries`: list of (feedback, delayMode, delayValue).
- `interruptBehavior`: what happens when the sequence is stopped mid-play — cascade stop to all remaining entries or let currently-playing ones finish.

**Use case**: A "heavy hit" sequence:
1. Hit-stop (0ms)
2. Screen shake (20ms, starts during freeze tail)
3. Hit flash + impact VFX (0ms, on impact frame)
4. Floating text (100ms delay, after the visual hit registers)
5. Haptic burst (0ms)

**Common pitfalls**:
- An entry that never completes (looping or waiting on a condition) blocks the entire sequence — every entry needs a timeout.
- Sequence that references a destroyed actor — entries should check actor validity before playing.

### 9.2 Parallel Groups

Multiple feedbacks triggered simultaneously as one logical bundle.

**Structure**: A set of feedback entries that all start on the same trigger.

Key parameters:
- `entries`: list of (feedback, parameters).
- `groupPriority`: the group's priority for throttling decisions — individual entries inherit it unless overridden.
- `degradationPolicy`: when global throttling kicks in, which entries can be skipped? Define essential (SFX, flash) vs. optional (particles, floating text) per group.

**Use case**: A "critical hit bundle":
- Screen shake (merge with existing)
- Bloom pulse
- Hit flash
- Critical hit SFX (high priority)
- Critical floating text (large, gold, with shake)
- Strong haptic

**Common pitfalls**:
- Silent failure when a group entry fails to play — log a warning with the entry type and reason (pool exhausted, throttled, invalid target).
- Group that isn't cleaned up after the triggering actor is destroyed.

### 9.3 Global Priority & Throttling

The central manager that keeps feedback under budget.

**Concurrency limits** (per-type and global):
- Screen shake: 1 active (merge model)
- Floating text per actor: 3 active (queue the rest or skip)
- Total active VFX instances: configurable per platform quality tier
- Total active haptic sources: 1 (strongest wins)

**Culling priority** when global limit is exceeded:
1. Distance from camera/player (furthest first).
2. Feedback priority (lowest first). Priorities: `Critical` (low health, death), `High` (heavy hit, ultimate ability), `Normal` (light hit, footstep), `Cosmetic` (ambient, idle).
3. Age (oldest within same tier).

**Quality tier presets**:
| Tier | VFX Max | Post-Processing | Haptics | Floating Text |
|:---|:---|:---|:---|:---|
| High (PC/Console) | 64 | Full | Full | 20 per actor |
| Medium (Mid Mobile) | 32 | Bloom + Vignette only | Transient only | 8 per actor |
| Low (Low Mobile) | 16 | Vignette only | Off | 5 per actor |

**Common pitfalls**:
- Culling logic that runs every frame for every feedback instance — batch the culling decision at feedback-spawn time, not in the update loop.
- Distance-based culling that computes `sqrt` per feedback — use squared distance comparison.
