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

Use this part as a feedback-type lookup. It lists what each type is for, what must be parameterized, and what design constraints should not be skipped.

## 4. Screen & Camera Feedback

| Feedback Type | Use When | Key Parameters | Lifecycle / Merge | Pitfalls / Must Decide |
|:---|:---|:---|:---|:---|
| **Screen shake: trauma model** | Repeated impacts should merge naturally | `trauma`, `maxOffset`, decay rate, direction constraint | Add trauma capped at 1; evaluate shake from `trauma * trauma`; decay over time | Motion sickness cap, disable option, node to shake, hit-stop interaction |
| **Screen shake: parametric** | Each shake needs distinct shape such as earthquake or recoil | amplitude, frequency, duration, decay curve | One request creates one timed instance; conflict uses replace/queue/ignore | Harder to merge; avoid stacking jitter |
| **Bloom** | Power-up, critical hit glow, magical pulse | intensity, threshold, duration | Usually controlled through post-process volume weight | Mobile cost; quality tier fallback |
| **Chromatic aberration** | Near-death edge distortion, screen damage, disorientation | radial intensity, duration | Priority stack; strongest/highest request controls volume | Overuse causes discomfort |
| **Color grading** | Low health, poison, berserk, mood shift | saturation, hue shift, contrast, duration | Priority stack or highest-severity state wins | Reset cleanly after state ends |
| **Vignette** | Low-health tunnel vision, hit impact darkening | intensity, smoothness, duration | Stack by highest opacity/severity | Keep readable; use as low-cost mobile fallback |
| **Lens distortion** | Stun, warp, heavy impact | intensity, duration | Replace or highest-priority request wins | Disorientation; cap intensity |
| **Zoom / FOV** | Ultimate, sniper aim, interaction focus, speed feel | target FOV, duration, ease curve | Tween camera property; suppress or coordinate with shake | FOV + shake can be disorienting |
| **Flash / Fade** | Explosion, respawn, transition, death screen | color, opacity, duration, fade curve | Most opaque or highest-priority request wins | Cap white flash opacity; avoid summing fades |

Implementation note: tween post-process volume weights rather than individual parameters when possible; it is easier to reset and prioritize.

---

## 5. Entity & World Feedback

| Feedback Type | Use When | Key Parameters | Lifecycle / Merge | Pitfalls / Must Decide |
|:---|:---|:---|:---|:---|
| **Particles / VFX** | Impact sparks, dust, aura, weapon trail, ambient reactive effects | prefab/type, attachment mode, lifetime, pool key, LOD tier | One-shot, sustained, or looped; use per-type pre-warmed pools | Detach on actor destruction; cap sustained VFX per actor; avoid instantiate spikes |
| **World attachment** | Effect should stay at impact or environment point | world position, rotation, surface normal | Independent one-shot or timed instance | Exact hit point may be inside geometry; offset when needed |
| **Attached VFX** | Aura, burn, shield, trail tied to actor/bone | target actor/bone, offset, stop condition | Ends when bound gameplay state or actor ends | Orphaned particles if actor deactivates |
| **Follow VFX** | Effect tracks actor with lag or smoothing | target actor, follow stiffness, offset | Updates while target exists; recycle on invalid target | Decide behavior on teleport/despawn |
| **Transform animation** | Bump, squash/stretch, wiggle, spring, look-at reactions | target transform, axis, amplitude, duration, damping | Additive overlay or last-wins; reset to absolute base pose | Animate visual child, not physics root; avoid scale drift |
| **Material / shader effect** | Hit flash, dissolve, flicker, outline, UV scroll | material params, color, alpha/noise threshold, duration | Per-entity override; replace/merge by parameter channel | Do not modify shared material for single target; dispose instances |
| **Floating text / damage numbers** | Damage, heal, crit, resource change, status text | spawn position, style, lifetime, travel curve, fade curve | Spawn, float, fade, recycle; queue/slot per actor or screen area | Cap density; pool text elements; avoid canvas rebuild spikes |

### Entity Feedback Strategy Matrix

| Concern | Prefer | Avoid |
|:---|:---|:---|
| VFX attachment | World, attached, or follow mode chosen per feedback | One generic spawn mode for all VFX |
| VFX lifecycle | One-shot for impacts, sustained for gameplay states, looped for ambient | Looping reactive effects without stop condition |
| VFX performance | Pre-warmed per-type pools and distance LOD | Instantiate-on-demand during combat spikes |
| Material override | Property block or runtime instance for per-entity effects | Mutating shared material for hit flash |
| Floating text layout | Slot offsets, random drift, per-actor/screen caps | Unlimited overlapping numbers |

---

## 6. UI & HUD Feedback

| Feedback Type | Use When | Key Parameters | Lifecycle / Merge | Pitfalls / Must Decide |
|:---|:---|:---|:---|:---|
| **Button press** | Direct UI interaction confirmation | press scale, release overshoot, duration | One short sequence per interaction | Keep within 100-200ms; do not fight layout system |
| **Icon shake / pulse** | Cooldown ready, quest available, item received | amplitude, frequency, decay, loop/one-shot | Replace or ignore if already stronger | Check panel visibility before play |
| **Health/resource bar feedback** | Damage, heal, resource spend/gain | flash color, lerp duration, ghost-bar delay | Skip intermediate animations during rapid updates | DOT/machine-gun updates should jump to final visible value |
| **Item popup** | Acquisition, reward, unlock | scale curve, overshoot, lifetime, fade | One-shot sequence, then recycle | Avoid layout rebuild-heavy animation |
| **Critical state pulse** | Low health, low ammo, danger state | alpha/scale curve, period, stop condition | Sustained while state persists | Stop when state resolves; avoid alert fatigue |

UI note: animate scale, color, opacity, or overlay transforms; avoid animating layout properties such as preferred width/height on hot paths.

---

## 7. Time Feedback

| Feedback Type | Use When | Key Parameters | Lifecycle / Merge | Pitfalls / Must Decide |
|:---|:---|:---|:---|:---|
| **Hit-stop / freeze frame** | Short impact emphasis | duration 30-80ms, time scale, restore curve, minimum gap | Restart, ignore stronger/weaker, or never-extend policy | Exclude audio, UI, input polling, and network; avoid freeze-lock on rapid hits |
| **Slow motion / time scale** | Sustained dramatic slowdown | target time scale, transition duration, sustain duration | Minimum-wins or last-wins stack policy | Overuse weakens feel; cooldown/DOT timers may need unscaled delta |

### Time Channel Isolation

| Channel | Hit-Stop Default | Slow-Motion Default | Reason |
|:---|:---|:---|:---|
| Rendering / animation | Freeze or slow | Slow | Carries visual weight |
| Physics / gameplay simulation | Freeze or slow by design | Slow by design | Must stay deterministic with gameplay rules |
| Audio | Do not freeze | Usually unscaled | Avoid pops and stretched impact sound |
| UI animation | Do not freeze | Usually unscaled | Menus and HUD remain responsive/readable |
| Input polling | Do not freeze | Usually unscaled | Preserve input buffer feel |
| Network processing | Do not freeze | Unscaled | Avoid sync delay |

---

## 8. Audio & Haptic Feedback

| Feedback Type | Use When | Key Parameters | Lifecycle / Merge | Pitfalls / Must Decide |
|:---|:---|:---|:---|:---|
| **SFX trigger** | Impact, UI action, pickup, ability, state change | clip, pitch range, volume scale, spatial blend, priority | Voice limit culls by priority/distance; batch repeated sources | Do not play one sound per shotgun pellet; align with hit-stop timing |
| **2D / UI sound** | Menus, HUD, global alerts | clip, volume, mix group, priority | Usually non-spatial; ignore world distance | Avoid spam from rapid UI state changes |
| **3D world sound** | Impact, footsteps, environment feedback | position, attenuation, spatial blend, priority | Culled by distance and voice budget | Pool or limit emitters during combat spikes |
| **Haptics / vibration** | Hit, recoil, impact, confirmation, tension | amplitude, frequency, duration, modulation curve | Highest-amplitude wins or weighted blend | Provide disable toggle; cap continuous duration; test on real hardware |
| **No-haptic platform** | Device lacks support | none | Graceful no-op | Never treat missing haptics as error |

Sync note: for impact-heavy events, play SFX just before freeze or on the freeze frame while audio remains unscaled.

---

## 9. Orchestration & Composition

| Composition Type | Use When | Key Parameters | Lifecycle / Merge | Pitfalls / Must Decide |
|:---|:---|:---|:---|:---|
| **Sequence** | Feedback must happen in ordered steps | entries, delay mode, delay value, interrupt behavior | Starts entries by offset; can cascade-stop or let current entries finish | Every entry needs timeout; validate actor before each entry |
| **Parallel group** | Multiple channels should fire as one logical bundle | entries, group priority, degradation policy | Starts together; entries inherit or override group priority | Define essential vs optional entries under throttling |
| **Global priority / throttling** | Feedback budget must survive combat spikes | per-type cap, global cap, priority, distance, age | Cull at spawn time by distance, priority, then age | Avoid per-frame global culling; use squared distance |

Example heavy-hit sequence:

| Offset | Feedback |
|:---|:---|
| `0ms` | Hit-stop, hit flash, impact VFX, haptic burst |
| `20ms` | Screen shake during freeze tail |
| `100ms` | Floating text after hit registers |

Example critical-hit parallel group:

| Entry | Priority / Degradation |
|:---|:---|
| Screen shake | High, merge with existing |
| Bloom pulse | Optional on low tier |
| Hit flash | Essential |
| Critical SFX | Essential, high audio priority |
| Critical floating text | Optional if text density cap reached |
| Haptic burst | Optional on unsupported or disabled platforms |

### Budget Presets

| Tier | VFX Max | Post-Processing | Haptics | Floating Text |
|:---|:---|:---|:---|:---|
| High (PC/Console) | 64 | Full | Full | 20 per actor |
| Medium (Mid Mobile) | 32 | Bloom + Vignette only | Transient only | 8 per actor |
| Low (Low Mobile) | 16 | Vignette only | Off | 5 per actor |
