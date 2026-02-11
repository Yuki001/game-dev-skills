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
requirement.md  --->  technical_design.md  --->  implementation.md
```

| Document | Purpose | Description |
|----------|---------|-------------|
| `requirement.md` | Requirements Analysis | Analyzes and formalizes user requirements |
| `technical_design.md` | Technical Solution Design | **Core document** - designs system approaches and patterns |
| `implementation.md` | Implementation Plan | Details data structures, algorithms, class designs, and key code |

---

## Workflow

### Phase 0: Ask user if need review

- **Question**: "Do you want to review the output document after every phase?"
- **Answer**: "Yes" or "No"
- **Default**: "Yes"
- **Output**: User Review Flag

**User Review Workflow**:
- **Trigger**: User explicitly requests "User Review" mode (via Phase 0).
- **Process**: 
    - After **each Phase**, pause and present the output to the user.
    - Request user feedback.
    - If feedback is received, **iterate** on the current phase's output before proceeding to the next phase.

---

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
4. Choose architectural paradigms using the **Paradigm Selection Guide** for each module
5. Use the **System-Specific References** to design each module

#### Paradigm Selection Guide

| Paradigm | KeyPoint | Applicability Scope | Examples | Reference |
| :--- | :--- | :--- | :--- | :--- |
| **Domain-Driven Design (DDD)** | OOP & Entity First | High Rule Complexity. <br> Rich Domain Concepts. <br> Many Distinct Entities. | Core Combat Logic, Physics Interactions, Damage/Buff Rules, Complex AI Decision. | `references/domain-driven-design.md` |
| **Data-Driven Design** | Data Layer First | High Content Complexity. <br>  Flow Orchestration. <br> Simple Data Management. | **Content**:  Quests, Level Design.<br>**Flow**: Tutorial Flow, Skill Execution, Narrative.<br>**Mgmt**: Inventory, Shop, Mail, Leaderboard. | `references/data-driven-design.md` |
| **Use-Case Driven Prototype** | Use-Case Implementation First | Rapid Validation | Game Jam, Core Mechanic Testing. | `references/prototype-design.md` |

#### System-Specific References

| System Category | Reference |
|----------------|-----------|
| Foundation & Core (Logs, Timers, Modules, Events, Resources, Audio, Input) | `references/system-foundation.md` |
| Time & Logic Flow (Update Loops, Async, FSM, Command Queues, Controllers) | `references/system-time.md` |
| Combat & Scene (Scene Graphs, Spatial Partitioning, ECS/EC, Loading) | `references/system-scene.md` |
| UI & Modules (Modules Management, MVC/MVP/MVVM, UI Management, Data Binding, Reactive) | `references/system-ui.md` |
| Skill System (Attribute, Skill, Buff) | `references/system-skill.md` |
| Action Combat System (HitBox, Damage, Melee, Projectiles) | `references/system-action-combat.md` |
| Narrative System (Dialogue, Cutscenes, Story Flow) | `references/system-narrative.md` |
| Game AI System (Movement, Pathfinding, Decision Making, Tactical) | `references/system-game-ai.md` |
| Algorithm & Data Structures (Pathfinding, Search, Physics, Generic Solver) | `references/algorithm.md` |

#### Mixing Paradigms

Most projects mix paradigms:
1.  **Macro Consistency**: All modules follow the same Module Management Framework.
2.  **Domain for Core Entities & Rules**: Use DDD for systems with high rule complexity, rich domain concepts, and many distinct entities (e.g., Combat Actors, Damage Formulas, AI Decision).
3.  **Data for Content, Flow & State**: Use Data-Driven for expandable content (Quests, Level Design), flow orchestration (Tutorial, Skill Execution, Narrative), and simple data management (Inventory, Shop).
4.  **Hybrid Paradigms**:
    - 4.1 **Entities as Data**: Domain Entities naturally hold both data (fields) and behavior (methods). Design entities to be serialization-friendly (use IDs, keep state as plain fields) so they serve both roles without a separate data layer.
    - 4.2 **Flow + Domain**: Use data-driven flow to orchestrate the sequence/pipeline, domain logic to handle rules at each step. E.g., Skill System: flow drives cast→channel→apply, domain handles damage calc and buff interactions.
    - 4.3 **Separate Data/Domain Layers**: Only when edit-time and runtime representations truly diverge. Use a Bake/Compile step to bridge them. E.g., visual node-graph editors, compiled assets.
5.  **Paradigm Interchangeability**: Many systems can be validly implemented with either paradigm. E.g., Actor inheritance hierarchy (Domain) ↔ ECS components + systems (Data-Driven); Buff objects with encapsulated rules (Domain) ↔ Tag + Effect data entries resolved by a generic pipeline (Data-Driven).
    - **Selection Criteria**: When both paradigms fit, evaluate trade-offs: Domain-Driven favors debuggability, explicit rules, and rich behavior; Data-Driven favors runtime flexibility, cache performance, serialization, and designer-friendly configuration. Networking requirements (state sync, rollback) often favor Data-Driven due to simpler state snapshots.
6.  **Integration**: Application Layer bridges different paradigms.


#### Note

**DO NOT** contain any Code Snippets in the Technical Design documents. 

---

### Phase 3: Implementation Planning

**Goal**: Create detailed implementation specifications.

- **Input**: `architect/technical_design.md`
- **Output**: `architect/implementation.md`
- **References**: Use Specific System Architecture documents from `references/`

**Key Tasks**:
1. **Directory Structure**: Define the directory structure for the project
2. **Data Structures**: Define all core data types and structures
3. **Algorithms**: Specify key algorithms with pseudocode
4. **Class Design**: Document class hierarchies and relationships
5. **Object Relationships**: Define associations, dependencies, and lifecycles
6. **Key Code Snippets**: Provide critical implementation examples

---

### Phase 4: Plan Refactoring

**Goal**: Review and refine the implementation plan for better extensibility and maintainability.

- **Input & Output**: `architect/implementation.md` (in-place update)
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

The final `architect/implementation.md` is used for actual code implementation.

> [!NOTE]
> Code implementation is **not part of this skill**. Hand off `implementation.md` to the implementation phase.

---

### Extensions

#### 1. Refactor Phase (On-Demand)

- **Trigger**: 
    - "User Review" flag is active.
    - OR User requests a refactor/update for a specific document after the fact.
- **Process**:
    - Can target any specific **Phase 1 - 5** individually.
    - **Input**: The **existing Output file** of that phase (e.g., `architect/technical_design.md` if refactoring Phase 2). *Crucial: Read the file first as the user may have modified it.*
    - **Goal**: Optimize, correct, or expand the document based on specific user feedback or new insights.
    - **Output**: Update the target file in-place.
    - **Note**: Phase 4 is a specialized version of this, but the Refactor Phase extension applies generally to any step.

---

## Example Workflows

### Example 1: New Project (DDD Focus)

- **User Input**: "I want to build an ARPG with complex combat involving many states, damage rules, and AI interactions."
- **Execution Path**:
    1.  **Phase 0**: Ask review preference.
    2.  **Phase 1 - Requirement Analysis**:
        - Read `references/requirements.md`.
        - Focus on **Domain Model Analysis** for combat entities and **Use Cases** for combat flows.
        - Output: `architect/requirement.md`.
    3.  **Phase 2 - Technical Design**:
        - Read `references/macro-design.md` + `references/principles.md`.
        - Define multi-application structure and technology stack.
        - Select **DDD** for core combat (high rule complexity, rich domain concepts). Read `references/domain-driven-design.md`.
        - System refs: `system-skill.md`, `system-action-combat.md`, `system-time.md`, `system-scene.md`, `algorithm.md`.
        - Output: `architect/technical_design.md`.
    4.  **Phase 3 - Implementation Planning**:
        - Output: `architect/implementation.md`.
    5.  **Phase 4 - Plan Refactoring**:
        - Read `references/evolution.md`.
        - Apply composition and abstraction patterns.
        - Update: `architect/implementation.md`.

### Example 2: Existing Project (Hybrid Paradigms)

- **User Input**: "I want to add a Skill System to my current combat engine. It needs effects, cooldowns, and data-configurable skills."
- **Execution Path**:
    1.  **Phase 0**: Ask review preference.
    2.  **Phase 1 - Requirement Analysis**:
        - Read `references/requirements.md`.
        - Define domain entities (Skill, Effect) and use cases for skill interactions.
        - Output: `architect/requirement.md`.
    3.  **Phase 2 - Technical Design**:
        - **Analyze existing project code** to understand current architecture.
        - Read `references/macro-design.md` + `references/principles.md`.
        - Select **DDD** for core skill logic (rules, interactions). Read `references/domain-driven-design.md`.
        - Select **Data-Driven** for skill configurations (tables, content). Read `references/data-driven-design.md`.
        - System refs: `system-skill.md`, `system-foundation.md`, `system-time.md`.
        - Output: `architect/technical_design.md`.
    4.  **Phase 3 - Implementation Planning**:
        - Output: `architect/implementation.md`.
    5.  **Phase 4 - Plan Refactoring**:
        - Read `references/evolution.md`.
        - Apply composition (component pattern for reusable effects) and abstraction (interfaces for targeting).
        - Update: `architect/implementation.md`.

### Example 3: Rapid Prototype

- **User Input**: "I have a puzzle mechanic idea. I want to build a quick demo this weekend to validate it."
- **Execution Path**:
    1.  **Phase 0**: Ask review preference.
    2.  **Phase 1 - Requirement Analysis** (lightweight):
        - Read `references/requirements.md`.
        - Minimal analysis, focus on core puzzle mechanic.
        - Output: `architect/requirement.md`.
    3.  **Phase 2 - Technical Design** (lightweight):
        - Read `references/macro-design.md` + `references/principles.md`.
        - Select **Use-Case Driven Prototype**. Read `references/prototype-design.md`.
        - System refs as needed: `system-time.md`, `algorithm.md`.
        - Output: `architect/technical_design.md`.
    4.  **Phase 3 - Implementation Planning**:
        - Focus on rapid implementation of core use case.
        - Output: `architect/implementation.md`.
    5.  **Phase 4 - Plan Refactoring**:
        - Read `references/evolution.md`.
        - Plan extraction points for after mechanic is validated.
        - Update: `architect/implementation.md`.

### Example 4: Refactor Extension (On-Demand)

- **User Input**: "I've drafted the implementation plan. Review and refactor it for better architecture and performance."
- **Execution Path**:
    1.  **Read** existing `architect/implementation.md`.
    2.  **Phase 4 - Plan Refactoring**:
        - Read `references/evolution.md`.
        - Read `references/performance-optimization.md` (user requested performance).
        - Apply isolation, composition, and abstraction patterns.
        - Introduce pooling, caching, or time-slicing where needed.
        - Update: `architect/implementation.md`.

---
