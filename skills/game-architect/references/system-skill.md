# Skill System Architecture

This document outlines a flexible and comprehensive architecture for designing game skill systems. The approach is modular, allowing for adaptation to various game genres by composing different data, logic, and event-handling components.

**IMPORTANT NOTE**: This general framework represents the maximum feature set. It should be simplified or modified according to the specific game content and type. Examples are provided later in this document.

## 1. Core Concepts

A skill system can be deconstructed into several fundamental layers:

-   **Data Layer**: Manages all stateful information, including character attributes, status effects, and skill-specific parameters.
-   **Logic Layer**: Governs the execution flow and behavior of skills over time. This includes the high-level skill structure and the individual actions that compose it.
-   **Event Layer**: Facilitates communication and reaction, decoupling skill logic from other game systems.
-   **Supporting Modules**: Provides specialized services like algorithms for targeting, interfaces for actors, and definitions for auxiliary entities.

The key design principle is to separate data, logic, and execution, enabling data-driven configuration and high reusability.

## 2. Data Layer

The foundation of the skill system, representing the state of all relevant entities. 

### Primary Data
-   **Attribute Set**: A collection of numerical properties that define an entity (e.g., Health, Mana, Strength). These are the primary targets for modification by skills.
    -   **Attribute Field**: An entry in an Attribute Set or Skill Blackboard, defining a numeric attribute with a base value and a list of modifications. The final value is dynamically recalculated and cached for efficiency. Its calculation logic typically handles additive and multiplicative changes, following a formula like `final_value = (base_value + additive_sum) * multiplicative_factor`.
-   **Tags**: A set of semantic labels used to describe an entity's current state or capabilities (e.g., `Stunned`, `Invulnerable`, `Burning`). Tags are crucial for state checking and logic branching.
-   **Effects**: Data-driven objects that represent a record of a modification to be applied to an entity. They are the primary mechanism for changing Attributes and Tags.

### Skill-Specific Data
-   **Skill Parameters**: Data required for a skill's execution. The storage strategy depends on the required scope and persistence:
    -   **Static Config**: Defined in data tables or assets; constant for all instances of a skill.
    -   **Skill Spec**: Carried by the skill instance itself, allowing for per-instance variations (e.g., a skill granted by an item).
    -   **Skill Blackboard**: Similar to an Attribute Set but specialized for skill-specific parameters and temporary variables. It attaches to an entity (or data) and facilitates parameter modification across different skills.
    -   **Attribute Set**: Storing skill parameters directly in the character's attributes, useful for values that need to be globally accessible or modified by other systems.

### Data Lifecycle
While most data is tied to a living `Actor` in the game world, some can be designed to persist independently (e.g., a `PlayerState` object that outlives the player's character).

### Data Hierarchy
Data can be structured hierarchically, mirroring the logical relationships between game entities. This allows for effects and skills to apply at different scopes. For example: `Global -> Faction -> Squad -> Soldier`. A faction-wide buff would apply at the `Faction` level and propagate downwards.

## 3. Logic Layer

Defines how a skill behaves from initiation to completion. The logic is a combination of a high-level **Framework** (representing the entire skill) and a series of granular **Actions** (representing a reusable behavior). This typically forms a two-tiered hierarchy.

### Tier 1: Skill Framework
The high-level structure that orchestrates the entire skill's lifecycle. Common patterns include:
-   **Code-Driven (Ability Class)**: A dedicated class encapsulates the skill's logic. This is a common, robust, and extensible approach.
-   **Behavior Tree**: A tree of nodes defining complex, AI-like sequences and decisions.
-   **Timeline**: A sequence-based approach, excellent for skills with fixed timing for effects and animations.
-   **Node Graph**: A visual graph of nodes and connections, offering a balance of flexibility and artist-friendly editing.
-   **Skill Script**: A domain-specific language or embedded script (e.g., Lua) that defines the skill's logic.

### Tier 2: Atomic Actions
Reusable, granular operations that are sequenced by the Skill Framework.
-   **Action Object**: A self-contained object representing a single game action (e.g., `PlayAnimation`, `ApplyDamage`, `SpawnProjectile`).
-   **Async Task/Function**: Asynchronous functions that can be awaited by the framework, suitable for long-running actions or those dependent on external events.

### Parallel States (Buffs & Debuffs)
States that exist concurrently with the main skill logic.
-   **Buff Object**: A comprehensive object, similar in structure to a skill, that manages its own lifecycle, periodic effects, and logic.
-   **Tag + Effects**: A lightweight approach where a state is represented by one or more Tags, and its logic is implemented through the ongoing application of Effects.

## 4. Event & Communication Layer

Handles the interactions between the skill system and the rest of the game.

-   **Data Modification Events**: Broadcasts when data changes, allowing other systems to react.
    -   `OnAttributeChange(Attribute, OldValue, NewValue)`
    -   `OnTagAdded/Removed(Tag)`
-   **Timing Triggers (Hooks)**: A system that fires events at specific, predefined moments in gameplay (e.g., `OnDamageDealt`, `OnTargetKilled`, `OnSpellCast`). Skills can subscribe to these hooks to implement reactive logic. 
    -   **Data-driven Hooks (Extension)**, Allowing for data-driven configuration of `Hook Type` and `Attribute Modifier` combinations instead of hardcoding them in the skill logic.
-   **Logic Triggers (Cues / Notifies)**: Events fired by the skill logic itself to signal key moments to other systems, primarily for presentation.
    -   **Cue**: A non-critical event for visual or audio effects (VFX, SFX).
    -   **Notify**: A critical event for gameplay logic (e.g., animation notifies that trigger a damage calculation).

## 5. Supporting Modules

-   **Algorithms**
    -   **Damage Calculation**: Encapsulated logic for processing damage, often involving a pipeline of formulas (`ModifierCalcFunction`) and steps (`DamageProcess`).
    -   **Targeting**: Logic for selecting targets (`TargetSelector`) and filtering them (`Filter`) based on various criteria.
-   **External Interface**: How actors in the world access the skill system.
    -   **Skill Component**: Attached directly to an actor (e.g., a `Character`), managing its skills.
    -   **Skill System**: A global singleton that manages all skills and entities.
-   **Additional Entities**
    -   **Projectile**: An independent actor representing a bullet, arrow, or magic bolt.
    -   **Trigger Volume**: An area used to detect presence or overlap to apply effects.
-	**Skill Lifecycle Phases**: Defines distinct states within a skill's execution, such as Wind-up (pre-cast), Execution, and Recovery (post-cast). These states are crucial for implementing mechanics like interruptions, cancels, and chained combos.

## 6. Configuration & Templating

A data-driven workflow is achieved by using templates to define various assets. The core principle is that a **template** is configured by a designer, and the system uses it to generate a runtime **instance**.

### Template Types
-   **Static Data Templates**: These define assets with fixed properties, such as spreadsheets, `DataAsset` objects, or configuration files. They are used for things that have data but minimal custom logic.
-   **Data-Driven Logic Templates**: These define assets that encapsulate behavior and logic, such as a visual script, a node graph, a DSL script, or a Blueprint. They are used for defining the "how" of a skill or action.

### Core Logic Templates

1.  **Actor Template**
    -   **Type**: Static Data Template.
    -   **Content**: Defines the base data for an entity, including its initial **Attribute Set** and **Tags**.

2.  **Skill Template** (Defines the Skill Framework)
    -   **If using Code-Driven (Ability Class)**:
        -   **Type**: Static Data Template.
        -   **Content**:
            -   **Skill Type**: An identifier (e.g., enum or name) to select which `Ability Class` to instantiate.
            -   **Skill Parameters**: The specific parameters for that class, including static values, Blackboard keys, or Attribute keys to link to.
    -   **If using other frameworks (Behavior Tree, Timeline, Node Graph)**:
        -   **Type**: Data-Driven Logic Template.
        -   **Content**: The logic asset itself (e.g., the Behavior Tree asset) which contains both the execution flow and its required parameters.

3.  **Action Template** (Defines the Atomic Actions)
    -   **If using Action Objects**:
        -   **Type**: Static Data Template.
        -   **Content**:
            -   **Action Type**: An identifier for which `Action` logic class to use.
            -   **Action Parameters**: The parameters specific to that action.
    -   **If using Async Tasks/Functions**:
        -   **Type**: Data-Driven Logic Template (e.g., a script or Blueprint).
        -   **Content**: The script itself. Can also be implemented as a code-plus-static-config hybrid.

### Other Optional Templates

-   **Parallel State Template** (Buffs/Debuffs)
    -   **For `Tags + Effects`**: This is a Static Data Template defining the `Effect` to be applied.
    -   **For `Buff Object`**: This is configured similarly to a `Skill Template`, as a buff can have its own complex logic.
-   **External Skill Definition**
    -   **Type**: Static Data Template.
    -   **Content**: Holds metadata about a skill for UI and other external systems, such as its name, description, icon, cooldown duration, and target selection parameters.

## 7. Architectural Adaptations by Genre

The generic framework should be specialized for the target game type.

### Example 1: TCG (Trading Card Game)
-   **Focus**: Event handling and state management.
-   **Changes**:
    -   **Remove Time Logic**: The `Skill Framework -> Action` hierarchy is replaced with `Effect Script -> Instant Action`, as card effects are typically instantaneous.
    -   **Enhance Hooks**: The Hook System is heavily expanded to handle a vast array of trigger conditions.
    -   **Add Global Systems**: Introduce a `Resolution Stack` to manage the order of effect execution and a `Global Rule Engine`.

### Example 2: Bullet Hell
-   **Focus**: Skill logic complexity and projectile performance.
-   **Changes**:
    -   **Simplify Data Layer**: The data layer is minimized. Attributes, Buffs, and Blackboards are often unnecessary.
    -   **Specialize Actions**: The "Action" layer is dominated by `Emitter` objects, which are responsible for spawning complex patterns of projectiles.
    -   **Enhance Projectiles**: The base projectile module is enhanced with advanced movement patterns.

### Example 3: Zelda-like (Mechanism-based)
-   **Focus**: Long-running, stateful abilities that introduce new mechanics.
-   **Changes**:
    -   **Framework becomes a State Machine**: The `Skill Framework` is replaced with an `Ability State Machine` to manage the activation and deactivation of entire gameplay mechanics (e.g., switching to a magnetic rune).
    -   **Actions become Capabilities**: Actions are refactored into `Gameplay Capabilities`, which are reusable components representing a core mechanic (e.g., `CanClimb`, `CanLiftObjects`). The state machine enables and disables these capabilities.
    -   **Emphasize Tags**: The Tag system becomes central for managing the character's complex states and interactions with the world.