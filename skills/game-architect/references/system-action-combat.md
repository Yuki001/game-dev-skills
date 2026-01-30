# Action Combat System Architecture

This document outlines a robust and flexible architecture for real-time action combat systems. It focuses on the synchronization of state management, collision detection, and a highly extensible damage processing pipeline.

## 1. Core Concepts

A modern action combat system is built upon several interconnected layers:

-   **State Management**: Controls the character's logical capabilities and animation states.
-   **Interaction Layer**: Handles physical collision, hit detection, and spatial queries.
-   **Execution Flow**: Orchestrates the sequence of events from attack initiation to impact.
-   **Damage & Logic Pipeline**: A hook-based system for calculating and applying gameplay effects.
-   **Scene Objects**: Independent entities like projectiles and triggers that interact with the world.

## 2. Character State Machine

The character's behavior is typically governed by a Finite State Machine (FSM) or a Hierarchical FSM.

### State Structure
-   **Single vs. Dual State Machine**: 
    -   *Single*: One machine manages all states (Idle, Run, Attack, Hit).
    -   *Dual*: Separates **Locomotion** (Lower Body/Movement) and **Combat** (Upper Body/Actions). This allows for "move and shoot" mechanics by layering animations.
-   **State Locking (Reference Counting)**: Instead of simple booleans, use reference counting to manage action restrictions.
    -   **Examples**:
        -   `MoveLockRef`: Incremented by animations or skills to prevent movement.
        -   `AtkLockRef`: Incremented to prevent initiating new attacks during recovery or stun.
    -   **Benefit**: Multiple overlapping systems (e.g., a stun debuff and a heavy attack recovery) can independently lock a capability, and it only becomes available again when all locks are released.

## 3. Collision & Interaction

Hit detection is managed through various "Boxes" (Volumes) that carry metadata.

### Box Types
Distinct volume types are defined to serve specific roles in combat.
-   **Hitbox (Attack)**: Created by the attacker to define the spatial volume where damage is inflicted.
-   **Hurtbox (Defense)**: Attached to the defender's skeletal hierarchy to define the specific areas that can receive damage.
-   **Interaction/Query Box**: Used for non-combat interactions such as looting, dialogue, or environmental triggers.

### Implementation Modes
1.  **Instance-Based**: Persistent box components attached to the character or weapon model. They are toggled `Active/Deactive` via animation notifies or skill logic events.
2.  **Instant Query (Data-Driven)**: A physics query (e.g., `BoxOverlap`, `SphereSweep`) is executed instantaneously at a specific frame. The query parameters (dimensions, offset, layers) are defined in data assets.

### Parameters & Filtering
-   **Box Attributes**: Each box carries data parameters essential for calculation and feedback, such as `AttackForm`, `Vector3 Force`, `HitStunDuration`, and `KnockbackIntensity`.
-   **Condition Pruning**: Optimization step to pre-filter targets based on team alignment (Friendly Fire), vertical distance (Z-axis check), or state tags (e.g., `Invulnerable`) before performing expensive physics overlaps.
-   **Alternative Forms**: 
    -   *Raycasts*: For high-velocity precision (e.g., hitscan bullets).
    -   *Complex Shapes*: Mesh-based collision for specialized VFX or large bosses.

## 4. Attack & Combat Flow

The combat flow is event-driven, triggered by the Skill System or Animation Sequences.

### Combat Attack Event
Attacks are initiated through precise timing events sourced from two main systems:
-   **Skill System**: A timeline-based skill engine triggers attack events at configured timestamps.
-   **Animation Sequences**: Embedded "Notifies" in animation clips trigger events when the character reaches specific frames (e.g., the moment a sword swing is fully extended).

### Melee Flow
1.  **Event Trigger**: Animation reach an "Active" frame or Skill logic starts.
2.  **Box Generation**: A Hitbox is activated or a Query is performed.
3.  **Collision Event**: A hit is detected, passing the Box Parameters to the victim.
4.  **Damage Processing**: The hit is resolved through the damage pipeline.
5.  **Hit Feedback**: The victim actor play hit feedback according to the data from the attacker's box.

### Ranged Flow
1.  **Event Trigger**: Animation/Skill logic triggers a "Fire" event.
2.  **Object Spawning**: A Projectile or Trigger Volume is spawned in the scene.
3.  **Autonomous Logic**: The scene object moves and performs its own collision detection.
4.  **Impact Event**: Upon collision, the scene object initiates the damage resolution and typically destroys itself.
5.  **Hit Feedback**: The victim actor play hit feedback according to the data from the scene object's box.

## 5. Damage Pipeline (Hook-Based)

The damage system uses a structured data flow to allow for complex modifications at every step.

### DamageData Structure
Contains the "context" of a hit.
-   **Example Data**:
    -   `BaseValue`: Raw damage before modifiers.
    -   `DamageFactor`: Scale based on move strength.
    -   `CritInfo`: Boolean `IsCritical` and `CritMultiplier`.
    -   `MitigationInfo`: Boolean `IsDodge`, `IsParry`, `ArmorPenetration`.

### The "A Hits B" Pipeline
1.  **Calculate Initial Structure**: Fill `DamageData` with base values from the attacker and move.
2.  **Pre-Damage Hooks**: Modify the data before application.
    -   `Attacker.onDamagingBefore(Victim, DamageData)` (e.g., "Life Steal" modifier).
    -   `Victim.onDamageBefore(Attacker, DamageData)` (e.g., "Shield" or "Damage Reduction" logic).
3.  **Apply Damage**: Commit the final `DamageData` to the victim's attributes (e.g., subtract Health).
4.  **Post-Damage Hooks**: Reactive logic after the hit is successful.
    -   `Attacker.onDamaging(Victim, DamageData)` (e.g., trigger a "Kill Proc").
    -   `Victim.onDamage(Attacker, DamageData)` (e.g., play "Hit Reaction" or trigger "Thorns").

### Direct & Internal Flows

Not all attribute changes require the full "A Hits B" complexity. The system supports streamlined flows for performance and logical clarity.

#### 1. Direct Healing Flow
Used for potions, health regeneration, or support abilities.
-   **Structure**: `HealData` (BaseAmount, Multiplier, SourceActor).
-   **Logic**:
    -   **Pre-Heal Hook**: Only the receiver's `onHealingBefore(HealData)` is triggered (e.g., to apply "Heal Received" bonuses or "Healing Reduction" debuffs).
    -   **Overhealing Handling**: Logic to clip the value or convert excess healing into temporary shields/mana if specified by the data.
    -   **Execution**: Direct addition to the `Health` attribute.

#### 2. Environmental & DOT Flow
Used for floor hazards (lava, poison gas), falling damage, or status effect ticks (Bleeding).
-   **Characteristics**: Often has no "Attacker" (Null Source) or uses a generic "Environment" actor.
-   **Logic**:
    -   **Bypass Attacker Hooks**: Skips all `onDamaging` hooks as there is no active entity to process them.
    -   **Internal Processing**: The victim's `onDamageBefore` is still triggered to allow for general damage reduction (e.g., "Resistance to Environmental Damage").
    -   **Tick Rate Management**: Handled by the `Trigger Area` or `Buff Object` to ensure consistent application without overloading the event system.

#### 3. True Direct Application
Used for system-level adjustments (e.g., level-up attribute boosts, developer cheats).
-   **Logic**: Directly modifies the attribute set without triggering any combat-related hooks or event notifications, preventing infinite loops or unintended feedback (like hit flashes during level-up).

## 6. Scene Objects

### Projectiles (Bullets)
-   **Base Movement**:
    -   **Vector-Based**: Defined by explicit `Position`, `Velocity`, and `Acceleration` (linear force).
    -   **Angular-Based**: Defined by `Angle`, `Speed`, `AngularVelocity`, and `RadialAcceleration` (curving paths).
-   **Emitters**: Specialized components responsible for spawning projectiles in complex patterns (e.g., Spirals, Fans, Random Scatters).
-   **Controllers/Modifiers**: Time-based logic components that can dynamically alter a projectile's trajectory during flight (e.g., Homing, Gravity, Drag, or Variable Speed curves).

### Other Objects
-   **Trigger Areas**: Static or moving zones that apply effects/buffs to entities within them.
-   **Attachments**: Objects physically linked to characters (e.g., a shield that uses "Spring" logic for procedural wobbling).

## 7. Hit Feedback

Feedback is generated by the victim based on the parameters passed from the attacker's hitbox:
-   **Directional Hit Reactions**: Using the `AttackVector` to play the correct animation (HitFront, HitLeft, etc.).
-   **Force Integration**: Applying physical impulses based on the `Force` parameter.
-   **Impact VFX/SFX**: Triggered based on the `AttackForm` and material types of both entities.
