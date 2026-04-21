# Camera, Character & Controller (3C) System

The 3C system defines how a player experiences and controls their character. It encompasses the physical simulation of the character body, the camera that frames the action, and the state machine that governs what the character can do. A well-designed 3C is the foundation of game feel.

This document is an overview of the 3C system. Detailed implementation for specific game types (platformer, top-down, vehicle, etc.) is covered in their respective reference files.

## 1. Controller

### 3D Controllers

#### First-Person
Camera is mounted at the character's eye position; the body is invisible (or only hands/weapon are rendered).

Key implementation points:
- **Look & Move coupling**: Mouse/stick delta rotates the camera yaw and pitch. Movement direction is derived from the camera's forward/right vectors projected onto the horizontal plane.
- **Pitch clamp**: Limit vertical look (e.g., −89° to +89°) to prevent gimbal flip.
- **Head bob**: Apply a sinusoidal offset to camera position based on walk cycle phase for immersion. Must be subtle and toggleable (motion sickness).
- **Weapon sway**: Additive camera-space offset driven by look velocity and movement acceleration.
- **Collision**: Capsule body handles world collision; camera position is the top of the capsule minus a small eye offset. Add a short sphere cast from capsule center to eye point to prevent camera clipping into low ceilings.

#### Third-Person
Camera orbits behind and above the character on a spring arm.

Key implementation points:
- **Spring arm**: A ray/shape cast from character socket to desired camera position shortens the arm on geometry hit, preventing clipping. Restore length smoothly when obstruction clears.
- **Camera lag**: Separate position lag and rotation lag factors. Position lag smooths sudden stops; rotation lag smooths quick turns.
- **Pitch/yaw limits**: Clamp pitch (e.g., −60° to +80°). Yaw is typically free.
- **Lock-on mode**: Override orbit with a LookAt toward the locked target. Blend smoothly in/out. Adjust distance to keep both player and target in frame.
- **Movement relative to camera**: Character moves in the direction the camera faces (camera-relative input), not the character's own forward. Rotate character toward movement direction with a configurable turn speed.

#### Flying / Free Camera
No gravity; full 6-DOF movement.

Key implementation points:
- **Input axes**: Forward/back, strafe left/right, ascend/descend — all relative to camera orientation.
- **Speed tiers**: Slow (precision), normal, fast (hold boost). Acceleration/deceleration curves prevent snapping.
- **Roll axis**: Optional for flight simulators. Disable for spectator cameras to avoid disorientation.
- **Collision**: Use a sphere or capsule sweep. On hit, slide along the surface normal rather than stopping dead.
- **Gravity toggle**: A single `gravity_enabled` flag lets the same controller serve both grounded and aerial phases (e.g., a character that can fly).

#### Vehicle
Driven by wheel physics rather than a character capsule.

Key implementation points:
- **Wheel raycasts**: Each wheel casts a ray downward. Hit distance determines suspension compression. Apply spring force upward and damping force against vertical velocity.
- **Traction & steering**: Front wheels rotate by steering angle. Drive force is applied at wheel contact points along the wheel's forward vector.
- **Center of mass**: Lower the CoM in the physics body to reduce rollover tendency. Expose as a tunable offset.
- **Drift / slip**: When lateral velocity exceeds grip threshold, reduce lateral friction to allow sliding. Blend back to full grip based on speed and input.
- **Enter/exit**: On exit, spawn the player character at a door socket, disable vehicle input, enable character controller. Reverse on entry.
- **Camera**: Typically a spring arm with higher lag than third-person to smooth out bumps. FOV widens at high speed.

#### 4-Legged Animal
Biped locomotion assumptions break down; requires dedicated solutions.

Key implementation points:
- **IK foot placement**: Each foot has a target point. Raycast downward from the ideal foot position to find the actual ground surface. Move the foot target to the hit point. Apply full-body IK (FABRIK or engine built-in) to adjust leg chains and spine.
- **Foot stride scheduling**: Feet move in a gait pattern (walk: LF→RR→RF→LR). A foot only lifts when its deviation from the ideal position exceeds a threshold AND the opposite diagonal foot is planted.
- **Spine flex**: Allow the spine to pitch and roll to match the slope under the body's four contact points (fit a plane through the four foot positions, align spine to that plane).
- **Turn radius**: Large animals cannot pivot in place. Apply a minimum turn radius; at low speed, allow a slow in-place turn animation.
- **Collision body**: Use a box or multi-capsule rather than a single capsule to better approximate the body volume.

---

### 2D Controllers

#### Top-Down
Movement on a 2D plane viewed from above (twin-stick shooters, ARPGs, roguelikes).

Key implementation points:
- **Input**: 4-directional (grid-based) or 8-directional (free analog). Normalize diagonal input vectors to prevent faster diagonal movement.
- **Collision shape**: Circle (smooth sliding around corners) or AABB (grid-aligned maps). Circle is preferred for action games.
- **Facing vs. moving**: Character can face the aim direction (twin-stick) independently of the movement direction. Separate `move_dir` and `face_dir` vectors.
- **Obstacle sliding**: On collision, project velocity onto the collision normal and continue moving along the wall.
- **Camera**: Typically follows the character with a soft dead zone. Offset toward the aim direction for lookahead.

#### Platformer
Horizontal movement with gravity-driven vertical physics.

Key implementation points:
- **Horizontal control**: Separate `move_speed` (max) and `acceleration`/`deceleration` values. Deceleration is often higher than acceleration for responsive stopping.
- **Gravity & jump arc**: Use two gravity values — `jump_gravity` (while rising) and `fall_gravity` (while falling, typically 1.5–2× higher) for a snappy arc.
- **Coyote time**: Remain jump-eligible for ~100 ms after walking off a ledge.
- **Jump buffer**: Accept jump input ~100 ms before landing; fire the jump immediately on ground contact.
- **Variable jump height**: On button release during ascent, multiply upward velocity by a cut factor (e.g., 0.5) to allow short hops.
- **One-way platforms**: Platforms with a flag that only collide from above. Allow drop-through by temporarily disabling the collision layer on down + jump input.
- **Wall jump / wall slide**: Detect wall contact via side raycasts. Reduce fall speed while sliding. On jump input, apply a velocity vector away from the wall.

#### Floating
Hybrid of platformer and free vertical movement (swimming, zero-gravity, flight power-ups).

Key implementation points:
- **Gravity toggle**: A `gravity_scale` float (0 = weightless, 1 = normal). Transition smoothly when entering/exiting water or activating flight.
- **Drag**: In floating mode, apply velocity damping each frame (`velocity *= drag_factor`) so the character decelerates naturally without explicit deceleration input.
- **Buoyancy**: In water, apply an upward force proportional to submersion depth. Character floats at the surface without input.
- **Swim speed cap**: Separate max speed for swimming vs. running. Acceleration is slower underwater.
- **Air/water boundary**: Detect the water surface with a raycast or area overlap. Trigger splash VFX/SFX and switch physics mode at the crossing point.
- **Flight power-up**: Same as flying controller but with a stamina/fuel meter. On depletion, gravity_scale returns to 1 and the character falls.

---

## 2. Character Physics

### Movement & Collision

Two primary implementation strategies:

**Impl 1 — Multi-Raycast**

Full manual control. Cast rays each physics tick, resolve penetration by hand, slide along normals.

Ray hits can be handled in three ways depending on context:

*1. Hard Collision (depenetration + slide):*
1. Move by full velocity × delta.
2. For each ray hit, compute penetration depth along the hit normal.
3. Push the body out by that depth (depenetration).
4. Project remaining velocity onto the surface plane (slide).
5. Repeat up to N iterations (typically 3–5) until no penetration remains.

*2. Soft Collision (force response):*
- Instead of hard depenetration, compute a spring force proportional to penetration depth and apply it to the body's velocity.
- Used for suspension (vehicle wheels), soft bumpers, or buoyancy. Produces smooth, physically-plausible responses rather than instant position correction.

*3. Detect (flag / logic only):*
- Record the hit point and normal without modifying position or velocity.
- Used to set collision flags (`collision_floor`, `collision_wall`, etc.), trigger gameplay events (landing sound, damage zone), or feed data to other systems (IK foot placement, grounding check).

> Raycast can be combined with a physics body (or trigger area) for better results — e.g. using a trigger to detect overlap candidates before casting rays. In hybrid setups, raycasts remain the primary source of truth for collision resolution.

**Examples:**

*2D Platformer ray layout (per tick):*
```
         [ceiling_ray]  ↑  (1 ray, from head center upward)

[left_ray] ←   [body]   → [right_ray]   (2–3 rays per side, spread vertically)

         [floor_rays]   ↓  (3–5 rays spread across foot width, angled slightly outward)
```
- Floor rays are spread across the capsule/box width so the character detects edges correctly (standing on a ledge with only one foot).
- Side rays are stacked vertically to distinguish wall vs. floor-slope hits.
- A separate short "step" ray is cast forward at step height to detect climbable ledges before the main body ray hits.

*Vehicle wheel ray layout:*
```
← FL ↓    FR ↓ →
← RL ↓    RR ↓ →
  (front/rear side rays omitted for clarity)
  ← left body side rays    right body side rays →
```
- Each wheel casts one ray straight down for suspension compression → spring force up, damper against vertical velocity.
- Side rays extend horizontally from the body (left/right, front/rear corners) to detect wall contact for scraping and preventing the body from clipping into walls.
- Additional forward/rear rays detect head-on collisions and bumper impacts.
- These rays work together with the vehicle's physics body (typically a box or convex hull) to form the complete collision system — the body handles broad contact, rays provide precise per-wheel and per-side feedback.

---

**Impl 2 — Capsule + MoveAndSlide**

Use the engine's physics body and move and slide algorithm. 

**Two common sub-approaches:**

*2-Pass (Axis-Separated) — common in custom engines and 2D platformers:*
1. **X probe**: Cast along `(velocity.x * delta, 0)` without moving. Compute `fix_x_delta` — the actual X distance to the hit point (or full X if no hit). If hit, zero out `velocity.x` and set `collision_left` or `collision_right`.
2. **Y probe**: Cast along `(fix_x_delta, velocity.y * delta)` without moving. Compute `fix_y_delta`. If hit, zero out `velocity.y` and set `collision_floor` or `collision_ceiling`.
3. **Apply**: Move body once by `(fix_x_delta, fix_y_delta)`.

Benefit: a corner hit never produces a diagonal push-out. The character hugs walls and floors cleanly. Jumping into a wall corner doesn't kill vertical momentum.

> Also applicable to 3D platformers: pass 1 probes the movement plane (XZ), pass 2 probes the vertical axis (Y).

*Iterative sweep (Godot `move_and_slide`):*
- Performs a shape cast along the full velocity vector.
- On hit, computes the slide vector (velocity projected onto the surface tangent) and continues moving with the remainder.
- Repeats up to `max_slides` iterations (default 4).
- Floor/ceiling/wall classification is done by comparing the collision normal angle against `floor_max_angle` (default 45°): normals within that angle of UP → floor; within that angle of DOWN → ceiling; otherwise → wall.
- Flags (`is_on_floor()`, `is_on_ceiling()`, `is_on_wall()`) are set from the normals collected across all slide iterations that tick.
- **Snap to floor**: An additional downward shape cast after movement keeps the character glued to slopes and stairs without bouncing.

> Capsule is the most common physics body for characters (smooth sliding, minimal snagging). Other shapes are valid depending on context: box for top-down games, sphere for rolling objects. Complex characters can use a shape list (multiple shapes combined) to better approximate the body volume.

### Collision Flags

Track surface contact per direction each physics tick:

```
collision_floor   — character is standing on ground
collision_ceiling — head hit something above
collision_left    — left side blocked
collision_right   — right side blocked
```

**How flags are computed — Raycast approach:**

Cast short probe rays at the start of each physics tick (before movement), independent of the movement rays:

```
ceiling:  1 ray upward from head center, length = small epsilon (e.g. 2px / 0.02m)
floor:    3–5 rays downward from foot positions, length = epsilon + snap_distance
left:     2 rays leftward at knee and shoulder height
right:    2 rays rightward at knee and shoulder height
```

- A flag is set if *any* ray in that direction hits within the probe length.
- Using multiple floor rays prevents false negatives when standing on a ledge edge.
- Probe length for floor is slightly longer than epsilon to also handle the "snap to floor" case on slopes.

**How flags are computed — 2-Pass MoveAndSlide:**

The axis-separated passes produce flags as a natural byproduct:
- X pass hits → set `collision_left` (normal points right) or `collision_right` (normal points left).
- Y pass hits → set `collision_floor` (normal points up) or `collision_ceiling` (normal points down).
- No extra raycasts needed; flags are exact because each axis is resolved independently.

**How flags are computed — Iterative sweep:**

After all slide iterations, Godot inspects the collected collision normals:
- Normal angle ≤ `floor_max_angle` from UP → `is_on_floor() = true`.
- Normal angle ≤ `floor_max_angle` from DOWN → `is_on_ceiling() = true`.
- Otherwise → `is_on_wall() = true`.
- An additional `move_and_collide` snap cast downward sets `is_on_floor()` even when the character is on a slope and the main movement didn't produce a floor normal.

**Grounding Detection (dedicated check):**

A separate short downward shape cast (not the movement pass) is used for gameplay logic — jump eligibility, coyote time timer, landing event — because the movement-derived floor flag can flicker on slopes or during the first frame of a jump. This dedicated cast is more stable and can be tuned independently of movement resolution.

### Moving Curve

The moving curve describes how velocity changes shape over time — on any axis. Input is only the trigger (pressed / released); the curve determines the actual velocity trajectory. It is the primary lever for game feel: "floaty", "snappy", and "weighty" are almost entirely curve differences, not top-speed differences.

**ADSR analogy:**
Borrowed from audio envelope design, the four phases map naturally to character movement:
- **Attack**: Time to reach max speed from rest when input is held.
- **Decay**: Optional speed reduction after a burst (e.g. sprint peak → sustained run speed).
- **Sustain**: The steady-state speed while input is held.
- **Release**: Time to decelerate to zero after input is released.

**Parameters:**
- `acceleration`: Rate of velocity increase per second toward `max_speed`.
- `deceleration`: Rate of velocity decrease per second when input is released. Usually higher than acceleration for responsive stopping.
- `max_speed`: The sustain velocity cap.
- `friction` (alternative to deceleration): Multiply velocity by `(1 - friction) ^ delta` each tick for an exponential decay curve instead of linear.

**Implementation approaches:**

*Linear (constant acceleration):*
```
velocity += input_dir * acceleration * delta
velocity = clamp(velocity, -max_speed, max_speed)
if no input: velocity = move_toward(velocity, 0, deceleration * delta)
```
Simple and predictable. Attack and Release are straight lines.

*Exponential (friction-based):*
```
velocity += input_dir * acceleration * delta
velocity *= pow(1 - friction, delta)   # or lerp(velocity, target, t)
```
Produces a smooth asymptotic curve — fast initial response, soft landing at max speed and at stop. Feels more organic; common in top-down and vehicle controllers.

*Curve asset (designer-controlled):*
- Store an AnimationCurve / Bezier that maps `time_held` → `speed_multiplier`.
- Sample the curve each tick to get the current speed factor.
- Allows arbitrary shapes (e.g. a dip after a dash, a ramp-up for heavy characters) without code changes.

> The Release curve (deceleration) is often more impactful on feel than the Attack curve. A fast stop feels responsive; a slow stop feels slippery. Tune them independently.

**Vertical axis (jump arc):**

The same curve concept applies to vertical velocity. Input (jump button) is the trigger; gravity values shape the arc:
- `jump_gravity`: Applied while rising — controls how quickly the peak is reached.
- `fall_gravity`: Applied while falling (typically 1.5–2× higher) — controls how fast the character drops. Higher = snappier, less floaty.
- `max_fall_speed`: Clamps the Release phase of the vertical curve to prevent tunneling and give a terminal-velocity feel.
- `jump_cut`: On button release during ascent, multiply upward velocity by a cut factor — shortens the Attack phase for variable arc height.

**Air control:**

Horizontal Moving Curve parameters are often reduced in the air to produce a "committed" feel:
- `air_acceleration` < `ground_acceleration`: Character can still steer but with less authority.
- `air_deceleration` ≈ 0 or very low: No friction in the air — horizontal momentum is mostly preserved (Mario-style).
- Tuning the ratio `air_acceleration / ground_acceleration` is the main dial between "floaty drift" and "full air control".

### Jumping & Falling

**Jump initiation:**
1. Check grounding (dedicated floor cast, not movement flag) — prevents jump during first airborne frame.
2. Set `velocity.y = jump_impulse`. Do not add to existing velocity; replace it so double-tap doesn't stack.
3. Start coyote timer reset: zero it out so the window closes immediately.

**Variable jump height (short-hop):**
- Each tick while rising: if jump button is released, multiply `velocity.y` by a cut factor (e.g. 0.5) once. Use a `jump_cut_applied` flag to apply it only once per jump.

**Dual gravity:**
- While `velocity.y > 0` (rising): apply `jump_gravity`.
- While `velocity.y ≤ 0` (falling): apply `fall_gravity` (typically 1.5–2× higher). Switch is per-tick based on sign of vertical velocity.

**Max fall speed:**
- After applying gravity, clamp `velocity.y` to `-max_fall_speed`. Prevents tunneling through thin floors at high frame deltas and gives a terminal-velocity feel.

**Coyote time:**
- When the character leaves the ground (floor flag goes false), start a countdown timer (~100 ms).
- Jump is still allowed while the timer is running, even with no floor contact.
- Zero the timer immediately on jump so it can't be used twice.

**Jump buffer:**
- On jump input, record `jump_buffer_timer = jump_buffer_duration` (~100 ms).
- Each tick: if `jump_buffer_timer > 0` and character is grounded, fire the jump and clear the timer.
- Decrement timer each tick regardless.

**Landing event:**
- Detect the transition: `was_on_floor == false` last tick AND `is_on_floor == true` this tick.
- Fire landing callbacks (camera shake, dust VFX, land animation, hard-landing stun if fall speed exceeded threshold).

### Slope & Stair Walking

**Slope classification:**
- Compare the floor normal angle against `floor_max_angle` (e.g. 45°).
- Within limit → walkable floor: apply movement normally, keep `collision_floor = true`.
- Beyond limit → treated as a wall: block horizontal movement, do not set floor flag. Character slides down if standing on it.

**Slope movement:**
- Project the movement vector onto the slope plane (`velocity - normal * dot(velocity, normal)`) so the character moves along the surface rather than into it or floating above it.
- Apply a speed scale based on slope angle: reduce speed going uphill, optionally increase going downhill (or clamp to prevent runaway acceleration).
- On steep downslopes, apply a slide force along the slope normal to push the character downhill.

**Floor snap (prevent bouncing on slopes):**
- After horizontal movement, cast a short ray downward (snap distance = step_height or small epsilon).
- If it hits a walkable surface, translate the character down to maintain contact.
- Skip the snap if the character just jumped (`jump_grace_timer > 0`) to avoid cancelling the jump.

**Step climbing (stair / curb):**
1. Forward ray at foot level hits an obstacle.
2. Cast a second ray forward at `foot_pos + (0, step_height, 0)` — if this ray is clear, the step is climbable.
3. Translate the character up by the step height, then continue horizontal movement.
4. Cast a downward ray to land on the step surface precisely.
- Step height is typically 20–30 cm. Beyond that, the obstacle is treated as a wall.

**Step descending:**
- When moving forward and the floor cast finds ground below the current foot level (within step_height), snap down to it automatically.
- Prevents the character from floating off stair edges one step at a time.

### Attaching to Objects

#### Moving Platform

The character must inherit the platform's displacement each tick without fighting the physics solver.

- **Velocity inheritance**: Each tick, read the platform's velocity (or compute `(current_pos - last_pos) / delta`) and add it to the character's velocity before calling move. Remove it after.
- **Parent transform approach**: Re-parent the character node to the platform. Works cleanly in scene-tree engines (Godot, Unity) but can cause issues with physics bodies — prefer velocity inheritance for physics-based characters.
- **Detection**: A floor raycast or `is_on_floor()` check identifies the platform. Store a reference to the floor body; poll its velocity each tick while contact persists.
- **Edge case — leaving platform**: When the character walks off, stop inheriting velocity immediately. Do not carry horizontal platform momentum unless intentional (e.g., a launch pad).

#### Rope / Swinging

- **Pendulum model**: The rope anchor is a fixed world point. Character position is constrained to `anchor + normalize(char_pos - anchor) * rope_length`.
- **Swing physics**: Apply gravity to a `swing_velocity` vector each tick. Project `swing_velocity` onto the tangent of the circle (remove the radial component) to enforce the length constraint.
- **Attach/detach**: On attach, compute initial `swing_velocity` from the character's current velocity projected onto the tangent. On detach, restore that velocity to the character.
- **Multiple segments**: For a chain or whip, use Verlet integration with distance constraints between each link, solved iteratively (XPBD or simple Jakobsen).

#### Ladder / Climbable Surface

- **Mode switch**: On overlap with a ladder trigger, switch to `ClimbingState`. Disable gravity (`gravity_scale = 0`). Lock horizontal movement to the ladder's local X axis (or fully lock it for a straight ladder).
- **Movement**: Up/down input maps to velocity along the ladder's local Y axis. Clamp speed separately from walk speed.
- **Top/bottom dismount**: Raycast above the top rung — if clear, allow the character to step off the top onto the floor. At the bottom, re-enable gravity and exit climbing state.
- **Alignment**: Snap the character's X position to the ladder center on entry. Optionally tween rotation to face the ladder.

#### Ledge Grab / Cliff Hanging

- **Detection**: Cast a forward ray at chest height and a downward ray just beyond the ledge edge. A ledge is valid when the forward ray hits a wall AND the downward ray finds open space above a surface within grab range.
- **Snap**: On grab, disable physics, tween character position to the hang anchor point (wall surface + fixed offset), lock input to hang state.
- **Hang state inputs**:
  - Jump → apply upward + forward impulse, exit hang state, re-enable physics.
  - Down / drop → re-enable physics with zero velocity (fall).
  - Lateral → shimmy along the ledge (translate anchor point horizontally, re-snap each tick).
- **Climb-up**: Trigger a climb animation. Use root motion or a tween to move the character from hang position to standing on the ledge. Re-enable physics on animation end.

---

## 3. Character Action States

The character's available actions are governed by a state machine layered over the physics body.

### Locomotion States

Core movement states that map directly to animation and physics behavior:

```
Idle → Walk → Run → Sprint
Idle → Crouch → CrouchWalk
Run  → Slide
Any  → Jump → Fall → Land
Any  → Dash (directional burst)
```

- **Blend Trees**: Locomotion animations are typically driven by a 2D blend tree (speed × direction) rather than discrete states, for smooth transitions.
- **Root Motion**: Animation drives character displacement (especially for attacks and rolls) to keep animation and physics in sync.

### Abilities & Status

- **Ability Flags**: Boolean or reference-counted locks that restrict actions (see [system-action-combat.md](./system-action-combat.md) for lock reference counting).
  - `can_move`, `can_jump`, `can_attack`, `can_use_skill`
- **Status Effects**: Stun, Freeze, Knockback, Airborne — each maps to a set of locked flags and a forced animation state.
- **Invincibility Frames (iFrames)**: A timer during which the hurtbox is disabled (dodge roll, respawn, hit stun recovery).

### Skill / Attack States

- **Attack State Entry**: Triggered by input or skill system. Locks movement (`MoveLockRef++`) for the duration.
- **Combo Windows**: A short window at the end of an attack animation where the next attack input is accepted and queued.
- **Cancel Rules**: Define which states can interrupt which (e.g., dodge can cancel attack recovery, but not startup).
- **Animation Notify Events**: Embedded events in animation clips fire hitbox activation, VFX spawns, and sound cues at precise frames. (see [system-action-combat.md](./system-action-combat.md))

---

## 4. Camera

### 3D Camera

- **LookAt**:
  Used for lock-on combat and cinematics.
  - Acquire nearest enemy in cone/radius; camera overrides to face the target.
  - Cycle targets with stick or shoulder buttons.
  - Player input orbits around the locked target; distance auto-adjusts to keep both in frame.
  - Lock breaks when target dies, leaves range, or player presses unlock.
- **Follow + Spring Arm**:
  Used for third-person action/adventure games.
  - Shape cast from character socket to desired position; shorten on hit, restore smoothly when clear.
  - Separate position lag and rotation lag factors.
  - Clamp pitch (e.g. −60° to +80°). Yaw is typically free.
  - Character moves along camera's forward/right on XZ; rotate toward movement direction.
- **Orthographic / Isometric**:
  Used for strategy, SRPG, and tactics games with a fixed perspective.
  - Orthographic projection; `ortho_size` controls zoom.
  - Rotation locked (e.g. 45° yaw, 35°–45° pitch). Never player-driven.
  - Pan on XZ via edge-scroll, WASD, or drag.
  - Sort overlapping objects by projected depth for correct draw order.
  - Click ray: direction = camera forward; origin = unprojected near-plane point.
  - Snap pan to tile grid to prevent sub-pixel shimmer.

### 2D Camera

- **Free Move with Limit Lines**:
  Used for action/adventure and platformers.
  - Define a rectangular dead zone around the character.
  - Camera only moves when the character reaches the edge of the dead zone.
- **Screen Regions**:
  Used for scrolling levels where different screen zones trigger different camera behaviors.
  - *Lock zone*: Camera does not move.
  - *Soft zone*: Camera eases toward the character.
  - *Hard limit*: Camera snaps to keep character on screen.
- **Lookahead**:
  Used for fast-paced games to give the player more visibility ahead.
  - Offset camera in the direction of movement or aim.
  - Lerp offset toward velocity direction each tick; reset smoothly when stopped.
- **Vertical Lock**:
  Used for platformers to avoid disorienting vertical drift during jumps.
  - Lock vertical camera movement while the character is airborne.
  - Unlock and snap to new floor height on landing event.
- **Zooming**:
  Used for strategy and exploration games where the player needs to adjust view scale.
  - Adjust `zoom` via scroll/pinch; lerp toward target each tick.
  - On zoom-in, offset camera so cursor world point stays fixed: `camera_pos += (cursor_world_pos - camera_pos) * (1 - zoom_ratio)`.
  - Auto-zoom out in combat, in during dialogue.

### Camera Animation Sequences

- **Cutscene / Cinematic**: Camera follows a spline path with keyframed position, rotation, and FOV. Character input is disabled.
- **Shake**: Additive noise (trauma-based or perlin) applied to camera transform for impacts and explosions.
- **Zoom Pulse**: Brief FOV change on heavy hits or ability activations to emphasize impact.
- **Transition Blend**: Smooth interpolation between gameplay camera and a fixed cinematic camera when entering a trigger volume.