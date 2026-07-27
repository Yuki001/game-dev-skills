# Sprite animation presets

This reference provides optional defaults for sprite-sheet character animation. It is a planning aid, not a required state list, timing standard, or workload target. Project timing, gameplay readability, and an existing animation bible override every value here.

## Contents

- [Preset schema](#preset-schema)
- [Selection rules](#selection-rules)
- [Motion choreography](#motion-choreography)
- [Preset catalog](#preset-catalog)

## Preset schema

Represent an animation preset with:

```text
key
category
action
default_frames
default_fps
loop
choreography
```

Treat `default_frames` and `default_fps` as starting points for a sprite-sheet brief. They do not require the generator to produce that exact count in one pass. Timing may also be expressed as per-frame durations when holds or impact accents matter.

## Selection rules

- Include only states that the game actually needs.
- Prefer readable key poses over extra in-betweens.
- Separate loops from one-shot actions before writing phase descriptions.
- For loops, describe the handoff from the final frame back to the first.
- For one-shots, describe entry, peak/contact, recovery, and the intended end state.
- Let gameplay timing, source references, and project conventions override catalog defaults.
- Use asymmetric timing when anticipation, impact, recoil, or a held pose benefits from it.

## Motion choreography

Use these as phase vocabularies. Adapt or omit phases rather than forcing every action into a fixed template.

### Held and idle loops

- Keep planted contacts, pivot, and silhouette anchors stable.
- Use restrained breathing, weight shift, cloth follow-through, or a subtle bob.
- Make the last pose flow into the first without a visible snap.
- Combat idle may add guarded tension and quicker secondary motion.

### Walk, run, sprint, and crawl

- Walk: contact → down → passing → up → opposite contact.
- Run: forward lean → extension/contact → compression → passing or airborne → opposite contact.
- Sprint: stronger lean, reach, airborne time, and vertical compression than run.
- Swing arms or carried parts in a motion that supports balance and direction.
- Crawl: make alternating limb contacts and torso translation readable at the delivery scale.

### Jump, fall, and land

- Jump: crouch/anticipation → takeoff → rising extension → apex → descent transition.
- Fall: readable airborne silhouette with controlled secondary motion.
- Land: contact → compression → rebound → settle.
- Preserve the intended vertical arc during frame normalization; do not baseline-align away the jump.

### Dash, roll, slide, dodge, and backstep

- Establish direction with a short anticipation when gameplay permits.
- Emphasize burst, peak displacement or rotation, braking, and recovery.
- Keep the silhouette readable even when the action is fast.
- Preserve contact and collision-relevant body bounds where gameplay depends on them.

### Melee attacks and combos

- Use wind-up → contact → follow-through → recovery.
- Heavy actions usually need clearer anticipation and a longer recovery than light actions.
- Stabs favor directional extension; slashes favor a readable arc; punches and kicks need a distinct contact pose.
- Combo sequences need individually readable hits, not a single blurred motion.
- Blocks and guards should present a stable defensive plane; parries and counters need a precise contact accent.

### Ranged actions

- Aim: stable held pose with only necessary breathing or sight correction.
- Shoot or throw: preparation → release/contact → recoil/follow-through → settle.
- Reload: show the important mechanical hand/object contacts in a readable order.
- Keep weapon orientation and attachment points consistent across frames.

### Cast, channel, summon, and power-up

- One-shot cast: gather → release → recoil or recovery.
- Channel or power-up loop: stable body anchor plus a repeating energy pulse.
- Summon or transform: establish a clear before/transition/after relationship.
- VFX may be authored separately when character readability or blend-mode needs differ.

### Damage and status

- Hurt and stagger: impact direction → recoil → balance recovery.
- Knockback and knockdown: loss of balance → displacement/fall → ground contact.
- Get-up and revive: ground contact → supported rise → stable end pose.
- Death or defeat: readable cause/recoil → collapse → final rest, unless the game requires a loop.
- Repeating status animations should preserve the base identity while making the status unmistakable.

### Emotes

- Choose one dominant expressive region: arms, head, torso, or full-body hop.
- Keep foot placement stable unless displacement is intentional.
- Looping emotes need a clean handoff; one-shot emotes need a clear neutral or held end pose.

### Interaction actions

- Show the action-specific contact: hands on an object, tool impact, carried load, or push/pull resistance.
- Keep tools and props attached consistently.
- Repeating work actions such as dig, mine, chop, and fish need a clear preparation/contact/recovery rhythm.

## Preset catalog

### Basic movement and posture

| Key | Frames | FPS | Loop |
|---|---:|---:|:---:|
| `idle` | 4 | 6 | yes |
| `idle-combat` | 4 | 8 | yes |
| `walk` | 6 | 10 | yes |
| `run` | 6 | 12 | yes |
| `sprint` | 6 | 14 | yes |
| `jump` | 5 | 10 | no |
| `fall` | 4 | 10 | yes |
| `land` | 4 | 12 | no |
| `crouch` | 4 | 8 | no |
| `crawl` | 6 | 8 | yes |
| `climb` | 6 | 8 | yes |
| `swim` | 6 | 8 | yes |
| `dash` | 4 | 14 | no |
| `roll` | 5 | 14 | no |
| `slide` | 4 | 12 | no |
| `sit` | 4 | 8 | no |
| `sleep` | 4 | 4 | yes |
| `turn` | 4 | 10 | no |

### Combat

| Key | Frames | FPS | Loop |
|---|---:|---:|:---:|
| `attack` | 5 | 12 | no |
| `attack-heavy` | 6 | 10 | no |
| `combo` | 6 | 14 | no |
| `slash` | 5 | 14 | no |
| `stab` | 4 | 14 | no |
| `punch` | 4 | 14 | no |
| `kick` | 5 | 14 | no |
| `uppercut` | 4 | 14 | no |
| `block` | 3 | 10 | yes |
| `parry` | 4 | 16 | no |
| `dodge` | 4 | 16 | no |
| `backstep` | 4 | 14 | no |
| `shoot` | 4 | 14 | no |
| `reload` | 5 | 10 | no |
| `aim` | 3 | 10 | yes |
| `throw` | 5 | 12 | no |
| `charge-attack` | 6 | 12 | no |
| `spin-attack` | 6 | 14 | no |
| `guard-break` | 4 | 12 | no |
| `counter` | 5 | 14 | no |
| `taunt` | 4 | 8 | yes |
| `draw-weapon` | 5 | 10 | no |

### Magic

| Key | Frames | FPS | Loop |
|---|---:|---:|:---:|
| `cast` | 5 | 12 | no |
| `cast-fire` | 6 | 12 | no |
| `cast-ice` | 6 | 10 | no |
| `cast-lightning` | 5 | 14 | no |
| `cast-heal` | 5 | 8 | no |
| `summon` | 5 | 10 | no |
| `channel` | 4 | 8 | yes |
| `buff` | 4 | 10 | no |
| `shield-up` | 4 | 10 | no |
| `teleport` | 5 | 14 | no |
| `transform` | 6 | 10 | no |
| `power-up` | 5 | 10 | yes |
| `meditate` | 4 | 4 | yes |
| `explode` | 5 | 16 | no |

### Damage and status

| Key | Frames | FPS | Loop |
|---|---:|---:|:---:|
| `hurt` | 3 | 10 | no |
| `hurt-heavy` | 4 | 10 | no |
| `knockback` | 4 | 12 | no |
| `knockdown` | 4 | 10 | no |
| `get-up` | 5 | 8 | no |
| `stun` | 4 | 8 | yes |
| `dizzy` | 4 | 8 | yes |
| `frozen` | 3 | 6 | yes |
| `burning` | 4 | 12 | yes |
| `poisoned` | 4 | 6 | yes |
| `stagger` | 4 | 10 | no |
| `death` | 5 | 8 | no |
| `death-fall` | 4 | 8 | no |
| `revive` | 6 | 8 | no |
| `low-hp` | 4 | 6 | yes |
| `defeat` | 4 | 8 | no |

### Emotion and emotes

| Key | Frames | FPS | Loop |
|---|---:|---:|:---:|
| `wave` | 4 | 8 | yes |
| `cheer` | 4 | 10 | yes |
| `clap` | 4 | 10 | yes |
| `bow` | 4 | 8 | no |
| `nod` | 3 | 8 | no |
| `shake-head` | 4 | 8 | no |
| `laugh` | 4 | 8 | yes |
| `cry` | 4 | 6 | yes |
| `angry` | 4 | 8 | yes |
| `surprised` | 3 | 12 | no |
| `think` | 4 | 6 | yes |
| `point` | 4 | 10 | no |
| `salute` | 4 | 8 | no |
| `dance` | 6 | 10 | yes |
| `victory` | 4 | 8 | yes |
| `sad` | 4 | 4 | yes |
| `scared` | 4 | 8 | yes |
| `yawn` | 4 | 6 | no |

### Interaction

| Key | Frames | FPS | Loop |
|---|---:|---:|:---:|
| `pick-up` | 4 | 10 | no |
| `carry` | 6 | 8 | yes |
| `push` | 6 | 8 | yes |
| `pull` | 6 | 8 | yes |
| `open` | 4 | 10 | no |
| `eat` | 4 | 8 | no |
| `drink` | 4 | 8 | no |
| `read` | 4 | 6 | yes |
| `dig` | 6 | 8 | yes |
| `mine` | 6 | 10 | yes |
| `chop` | 6 | 10 | yes |
| `fish` | 5 | 6 | yes |
