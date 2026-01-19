---
name: game-architect
description: Comprehensive guide for game project architecture, requirement analysis, and logic design. Use this skill when setting up a new game project, analyzing game requirements, or designing specific game systems. It provides guidance on choosing and mixing architectural patterns like Domain-Driven Design (DDD) and Data-Driven Design.
---

# Game Architect Skill

This skill assists in the architectural design and structural setup of game projects. It covers the entire flow from requirement analysis to detailed logic design, offering different paradigms based on the project's nature.

## Workflow

### 1. Understand the Project Goal

First, determine the nature of the task:
- **Formal Project**: Requires robust architecture, scalability, and maintenance. (Proceed to Step 2)
- **Rapid Prototype**: Needs speed and immediate feedback. (Jump to Step 4 - Prototype Design)

### 2. Requirement Analysis

Analyze the requirements to build a solid foundation.

- **Action**: Read `references/requirements.md`.
- **Key Outputs**:
  - Feature List (Technological scope)
  - Domain Models (For core gameplay)
  - Use Cases & User Flows (For interactions)

### 3. Macro Architecture Design

Establish the high-level structure, application division, and technology stack.

- **Action**: Read `references/macro-design.md`.
- **Tasks**:
  - Define Multi-Application structure (Client/Server).
  - Select Technology Stack (Engine, Languages).
  - Perform Initial Logic Decomposition (Layers, Modules).

### 4. Detailed Logic Design (Selection & Mixing)

Choose the appropriate design paradigm for each module. A game project often **mixes** these paradigms.

- **Action**: Read `references/principles.md` for core principles.

#### A. Complex Core Gameplay & Systems
For complex logic, heavy state management, and clear domain concepts (e.g., Combat, Physics, AI).
- **Paradigm**: **Domain-Driven Design (DDD)**
- **Action**: Read `references/domain-driven-design.md`.
- **Focus**: Entities, Services, Aggregates.

#### B. UI, Data Management & Simple Systems
For systems focused on data display, inventory, shops, or simple CRUD operations.
- **Paradigm**: **Data-Driven Design**
- **Action**: Read `references/data-driven-design.md`.
- **Focus**: Data Structures, Configs, Model-View separation.

#### C. Rapid Prototyping
For validating ideas quickly without heavy architecture.
- **Paradigm**: **Use-Case Driven Prototype Design**
- **Action**: Read `references/prototype-design.md`.
- **Focus**: Speed, Use-Case realization, subsequent refactoring.

#### D. Specific System Architecture
If the user asks for detailed architecture of specific subsystems, read the corresponding reference:
- **Foundation & Core**: Read `references/system-foundation.md`.
    - Covers: Logs, Timers, Modules, Events, Resources, Audio, Input.
- **Time & Logic Flow**: Read `references/system-time.md`.
    - Covers: Update Loops, Async/Coroutines, State Machines (FSM), Command Queues, Global Flow & Controllers.
- **Combat & Scene**: Read `references/system-scene.md`.
    - Covers: Scene Graphs, Spatial Partitioning (Grid/QuadTree), ECS vs EC, Loading Strategies.
- **UI & Modules (MV*)**: Read `references/system-ui.md`.
    - Covers: MV* Patterns (MVC/MVP/MVVM), UI Management, Data Binding, Reactive Programming.

#### Mixing Paradigms
**How to mix them in one project:**
1.  **Macro Consistency**: Ensure all modules follow the same Module Management Framework (Lifecycle, Event System) regardless of their internal design.
2.  **Domain for Core**: Design the Battle/Core module using DDD to handle complexity.
3.  **Data for Shell**: Design the UI/Meta-game modules (Inventory, Social) using Data-Driven Design for efficiency and ease of binding to UI.
4.  **Integration**: Use the Application Layer (from DDD) or Controllers (from Data-Driven) to bridge the two. For example, a UI button (Data-Driven) sends a Command that triggers a Service in the Core Domain (DDD).

### 5. Handling Changes & Evolution

Architecture is not static. Plan for changes.

- **Action**: Read `references/evolution.md`.
- **Strategies**: Isolation, Abstraction, Composition, and Refining.

## Example Workflow Execution

### Example 1: New Formal Project (Core Gameplay Focus)
- **User Input**: "I want to start a new ARPG project. The core combat is very complex with many states and interactions. How should I begin?"
- **Execution Path**:
    1.  **Goal**: Identify as a **Formal Project**.
    2.  **Analysis**: Read `references/requirements.md`. Focus on **Domain Model Analysis** to capture complex combat concepts.
    3.  **Macro Design**: Read `references/macro-design.md`. Choose Unity/Unreal and define the layer structure.
    4.  **Logic Design**: Select **Domain-Driven Design (DDD)**. Read `references/domain-driven-design.md`. Implement Combat using Entities (Player, Enemy) and Services (DamageCalc).
    5.  **Specific System Design**:
        - For Combat Actor structure (EC/ECS), read `references/system-scene.md`.
        - For Player State Machine (HFSM), read `references/system-time.md`.

### Example 2: Adding a UI Module (Data-heavy Focus)
- **User Input**: "I need to add a complex Inventory and Shop system to my existing game. How should I design the logic?"
- **Execution Path**:
    1.  **Goal**: Identify as a module for a **Formal Project**.
    2.  **Analysis**: Read `references/requirements.md`. Focus on **Use Cases & User Flow** for inventory interactions.
    3.  **Logic Design**: Select **Data-Driven Design (MV*)**. Read `references/data-driven-design.md`. Design Item structures, Config tables, and the Global Container for the inventory state.
    4.  **Specific System Design**:
        - For MVVM and UI Management implementation, read `references/system-ui.md`.
        - For Resource Caching (Icons/Models), read `references/system-foundation.md`.

### Example 3: Rapid Prototype
- **User Input**: "I have an idea for a unique puzzle mechanic. I want to build a quick demo this weekend to see if it's fun."
- **Execution Path**:
    1.  **Goal**: Identify as a **Rapid Prototype**.
    2.  **Logic Design**: Jump to **Use-Case Driven Prototype Design**. Read `references/prototype-design.md`.
    3.  **Implementation**: Focus on rapid implementation of the core puzzle use case. Refactor into a cleaner structure (e.g., extracting a PuzzleController) only after the core mechanic is proven fun.
    4.  **Specific System Design**:
        - For quick FSM or Update logic, read `references/system-time.md`.
        - For quick UI (IMGUI), read `references/system-ui.md`.

### Example 4: Designing a New System in an Existing Project
- **User Input**: "I want to add a Skill System to my current combat engine. It needs to support various effects, cooldowns, and resources. How should I architect it?"
- **Execution Path**:
    1.  **Goal**: Identify as a new system for a **Formal Project**.
    2.  **Analysis**: Read `references/requirements.md`. Focus on **Domain Model Analysis** to define entities like `Skill`, `Effect`, and `Requirement`.
    3.  **Logic Design**:
        - Apply **Domain-Driven Design (DDD)** for the core logic (e.g., `SkillExecutionService`). Read `references/domain-driven-design.md`.
        - Apply **Data-Driven Design** for skill configurations (XML/JSON/Excel). Read `references/data-driven-design.md`.
    4.  **Evolution**: Read `references/evolution.md`. Use **Composition** (Component pattern) to build complex skills from reusable effects, and **Abstraction** (Interfaces) to handle different targeting systems (e.g., Point vs. Target).
    5.  **Specific System Design**:
        - For Scene and Actions, read `references/system-scene.md` and `references/system-time.md`.
        - For Event triggering (e.g., OnSkillCast), read `references/system-foundation.md`.

## Reference Map

- `references/principles.md`: Core architectural principles.
- `references/requirements.md`: Methods for analyzing requirements.
- `references/macro-design.md`: High-level system design.
- `references/domain-driven-design.md`: OOP/DDD patterns.
- `references/data-driven-design.md`: Data-oriented patterns.
- `references/prototype-design.md`: Rapid prototyping guide.
- `references/evolution.md`: Managing architectural changes.
- `references/system-foundation.md`: Core infrastructure (Log, Event, Resource).
- `references/system-time.md`: Time logic (FSM, Coroutine).
- `references/system-scene.md`: Scene & Spatial logic.
- `references/system-ui.md`: UI & Module architecture / MV* patterns.