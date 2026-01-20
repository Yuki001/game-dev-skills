---
name: game-architect
description: A documentation-focused skill for game architecture design. Produces technical selection, design, and planning documents through a structured pipeline. Use this skill to generate requirement analysis, technical design, and implementation planning documents for new game projects or major feature development.
---

# Game Architect Skill

This skill assists in the **documentation phase** of game project development. It produces a series of technical documents that guide subsequent implementation work.

> [!IMPORTANT]
> This skill focuses on **documentation output only**. The actual code implementation phase is **outside the scope** of this skill.

## Output Documents

All documents are placed in an `architect/` directory (create if needed). The pipeline produces:

```
requirement.md  --->  technical_design.md  --->  plan.md
```

| Document | Purpose | Description |
|----------|---------|-------------|
| `requirement.md` | Requirements Analysis | Analyzes and formalizes user requirements |
| `technical_design.md` | Technical Solution Design | **Core document** - designs system approaches and patterns |
| `plan.md` | Implementation Plan | Details data structures, algorithms, class designs, and key code |

---

## Workflow

### Phase 1: Requirement Analysis

**Goal**: Analyze user requirements and produce structured documentation.

- **Input**: User request + LLM knowledge
- **Output**: `architect/requirement.md`
- **Reference**: Read `references/requirements.md`

**Key Tasks**:
1. Extract and clarify user requirements
2. Build Feature List (technological scope)
3. Define Domain Models (for core gameplay)
4. Document Use Cases & User Flows

---

### Phase 2: Technical Design

**Goal**: Design technical solutions for each system. This is the **most critical phase**.

- **Input**: `architect/requirement.md`
- **Output**: `architect/technical_design.md`
- **References**:
  - Read `references/macro-design.md` for high-level structure
  - Read `references/principles.md` for core principles

**Key Tasks**:
1. If existing project: Analyze the exist project code to understand the current architecture
2. Define Multi-Application structure (Client/Server)
3. Select Technology Stack (Engine, Languages)
4. Choose architectural paradigms for each module:

#### Paradigm Selection Guide

| System Type | Recommended Paradigm | Reference |
|-------------|---------------------|-----------|
| Complex Core Gameplay (Combat, Physics, AI) | **Domain-Driven Design (DDD)** | `references/domain-driven-design.md` |
| UI, Data Management, Simple CRUD | **Data-Driven Design** | `references/data-driven-design.md` |
| Rapid Prototyping | **Use-Case Driven Prototype** | `references/prototype-design.md` |

#### Mixing Paradigms

Most projects mix paradigms:
1. **Macro Consistency**: All modules follow the same Module Management Framework
2. **Domain for Core**: Use DDD for Battle/Core modules
3. **Data for Shell**: Use Data-Driven for UI/Meta-game modules
4. **Integration**: Application Layer bridges different paradigms

#### Note

**DO NOT** contain any Code Snippets in the Technical Design documents. 

---

### Phase 3: Implementation Planning

**Goal**: Create detailed implementation specifications.

- **Input**: `architect/technical_design.md`
- **Output**: `architect/plan.md`
- **References**: Use Specific System Architecture documents from `references/`

**Key Tasks**:
1. **Data Structures**: Define all core data types and structures
2. **Algorithms**: Specify key algorithms with pseudocode
3. **Class Design**: Document class hierarchies and relationships
4. **Object Relationships**: Define associations, dependencies, and lifecycles
5. **Key Code Snippets**: Provide critical implementation examples

#### System-Specific References

| System Category | Reference |
|----------------|-----------|
| Foundation & Core (Logs, Timers, Modules, Events, Resources, Audio, Input) | `references/system-foundation.md` |
| Time & Logic Flow (Update Loops, Async, FSM, Command Queues, Controllers) | `references/system-time.md` |
| Combat & Scene (Scene Graphs, Spatial Partitioning, ECS/EC, Loading) | `references/system-scene.md` |
| UI & Modules (Modules Management, MVC/MVP/MVVM, UI Management, Data Binding, Reactive) | `references/system-ui.md` |
| Performance & Optimization (Profiling, Caching, Pooling, Threading, Batching) | `references/performance-optimization.md` |
| Algorithm & Data Structures (Pathfinding, Search, Physics, Generic Solver) | `references/algorithm.md` |

---

### Phase 4: Plan Refactoring

**Goal**: Review and refine the implementation plan for better extensibility and maintainability.

- **Input & Output**: `architect/plan.md` (in-place update)
- **Reference**: 
    - Read `references/evolution.md`
    - Read `references/performance-optimization.md` (Only if user requires performance optimization)

**Refactoring Focus**:
1. **Isolation**: Ensure proper separation of concerns
2. **Abstraction**: Apply appropriate interface abstractions
3. **Composition**: Prefer composition over inheritance where applicable
4. **Future Changes**: Anticipate and plan for likely evolution

---

### Phase 5: Implementation (Out of Scope)

The final `architect/plan.md` is used for actual code implementation.

> [!NOTE]
> Code implementation is **not part of this skill**. Hand off `plan.md` to the implementation phase.

---

## Example Workflows

### Example 1: New Formal Project (Core Gameplay Focus)

- **User Input**: "I want to start a new ARPG project. The core combat is very complex with many states and interactions. How should I begin?"
- **Execution Path**:
    1.  **Requirement Analysis**:
        - Read `references/requirements.md`.
        - Focus on **Domain Model Analysis** to capture complex combat concepts.
        - Output: `architect/requirement.md`.
    2.  **Technical Design**:
        - Read `references/macro-design.md`. Choose Unity/Unreal and define the layer structure.
        - Read `references/principles.md`.
        - Select **Domain-Driven Design (DDD)**. Read `references/domain-driven-design.md`.
        - Implement Combat using Entities (Player, Enemy) and Services (DamageCalc).
        - Output: `architect/technical_design.md`.
    3.  **Implementation Planning**:
        - For Combat Actor structure (EC/ECS), read `references/system-scene.md`.
        - For Player State Machine (HFSM), read `references/system-time.md`.
        - For AI pathfinding or spatial queries, read `references/algorithm.md`.
        - Output: `architect/plan.md`.
    4.  **Plan Refactoring**:
        - Read `references/evolution.md`.
        - Apply Composition and Abstraction patterns.
        - Update: `architect/plan.md`.

### Example 2: Adding a UI Module (Data-heavy Focus)

- **User Input**: "I need to add a complex Inventory and Shop system to my existing game. How should I design the logic?"
- **Execution Path**:
    1.  **Requirement Analysis**:
        - Read `references/requirements.md`.
        - Focus on **Use Cases & User Flow** for inventory interactions.
        - Output: `architect/requirement.md`.
    2.  **Technical Design**:
        - Analyze the exist project code to understand the current architecture.
        - Read `references/principles.md`.
        - Select **Data-Driven Design**.
        - Read `references/data-driven-design.md`.
        - Design Item structures, Config tables, and the Global Container for the inventory state.
        - Output: `architect/technical_design.md`.
    3.  **Implementation Planning**:
        - For MVVM and UI Management implementation, read `references/system-ui.md`.
        - For Resource Caching (Icons/Models), read `references/system-foundation.md`.
        - Output: `architect/plan.md`.
    4.  **Plan Refactoring**:
        - Read `references/evolution.md`.
        - Update: `architect/plan.md`.

### Example 3: Rapid Prototype

- **User Input**: "I have an idea for a unique puzzle mechanic. I want to build a quick demo this weekend to see if it's fun."
- **Execution Path**:
    1.  **Requirement Analysis**:
        - Minimal analysis, focus on core puzzle mechanic.
        - Output: `architect/requirement.md` (lightweight).
    2.  **Technical Design**:
        - Read `references/principles.md`.
        - Jump to **Use-Case Driven Prototype Design**.
        - Read `references/prototype-design.md`.
        - Output: `architect/technical_design.md` (lightweight).
    3.  **Implementation Planning**:
        - For quick FSM or Update logic, read `references/system-time.md`.
        - For quick UI (IMGUI), read `references/system-ui.md`.
        - For core puzzle algorithms (Search/Graph), read `references/algorithm.md`.
        - Focus on rapid implementation of the core puzzle use case.
        - Output: `architect/plan.md`.
    4.  **Plan Refactoring**:
        - Read `references/evolution.md`.
        - Plan to extract PuzzleController after core mechanic is proven fun.
        - Update: `architect/plan.md`.

### Example 4: Designing a New System in an Existing Project

- **User Input**: "I want to add a Skill System to my current combat engine. It needs to support various effects, cooldowns, and resources. How should I architect it?"
- **Execution Path**:
    1.  **Requirement Analysis**:
        - Read `references/requirements.md`.
        - Focus on **Domain Model Analysis** to define entities like `Skill`, `Effect`, and `Requirement`.
        - Output: `architect/requirement.md`.
    2.  **Technical Design**:
        - Analyze the exist project code to understand the current architecture.
        - Read `references/principles.md`.
        - Apply **Domain-Driven Design (DDD)** for the core logic (e.g., `SkillExecutionService`). Read `references/domain-driven-design.md`.
        - Apply **Data-Driven Design** for skill configurations (XML/JSON/Excel). Read `references/data-driven-design.md`.
        - Output: `architect/technical_design.md`.
    3.  **Implementation Planning**:
        - For Scene and Actions, read `references/system-scene.md` and `references/system-time.md`.
        - For Event triggering (e.g., OnSkillCast), read `references/system-foundation.md`.
        - Output: `architect/plan.md`.
    4.  **Plan Refactoring**:
        - Read `references/evolution.md`.
        - Use **Composition** (Component pattern) to build complex skills from reusable effects.
        - Use **Abstraction** (Interfaces) to handle different targeting systems (e.g., Point vs. Target).
        - Update: `architect/plan.md`.

### Example 5: Architecture and Performance Refactoring

- **User Input**: "I've drafted the plan for the new system. Can you review and refactor it? I want to make sure the architecture is clean and scalable, and that it runs efficiently."
- **Execution Path**:
    1.  **Analyze Existing Plan**: Review `architect/plan.md` to identify coupling issues and potential hotspots.
    2.  **Read References**:
        - Read `references/evolution.md` to guide architectural separation and extensibility.
        - Read `references/performance-optimization.md` to find opportunities for caching, pooling, or algorithmic improvements.
    3.  **Plan Refactoring**:
        - Apply **Composition** to decouple monolithic classes (from `evolution.md`).
        - Introduce **Object Pooling** for frequently created entities (from `performance-optimization.md`).
        - Implement **Throttling/Time-Slicing** for heavy update loops.
        - Update: `architect/plan.md`.

---

## Reference Map

| Reference | Purpose |
|-----------|---------|
| `references/requirements.md` | Requirement analysis methods |
| `references/macro-design.md` | High-level system design |
| `references/principles.md` | Core architectural principles |
| `references/domain-driven-design.md` | DDD/OOP patterns |
| `references/data-driven-design.md` | Data-oriented patterns |
| `references/prototype-design.md` | Rapid prototyping guide |
| `references/evolution.md` | Managing architectural changes |
| `references/system-foundation.md` | Core infrastructure |
| `references/system-time.md` | Time & logic flow |
| `references/system-scene.md` | Scene & spatial logic |
| `references/system-ui.md` | UI architecture & MV* patterns |
| `references/performance-optimization.md` | Logic performance optimization strategies |
| `references/algorithm.md` | Algorithms and Data Structures reference |