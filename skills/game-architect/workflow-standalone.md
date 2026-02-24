# Game Architect - Standalone Workflow

> This is the standalone workflow for the Game Architect skill. Use this when **no external workflow skill** (e.g., OpenSpec) is available. If a workflow skill is active, ignore this file and use the SKILL.md as a domain knowledge reference instead.

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
2. Build Feature List (technological scope, including non-functional requirements)
3. Define Domain Models (for core gameplay)
4. Document Use Cases & User Flows
5. Plan Iteration Milestones (incremental MVP delivery)

---

### Phase 2: Technical Design

**Goal**: Design technical solutions for each system. This is the **most critical phase**.

- **Input**: `architect/requirement.md`
- **Output**: `architect/technical_design.md`
- **References**:
  - Read `references/macro-design.md` for high-level structure
  - Read `references/principles.md` for core principles
  - Read `references/system-multiplayer.md` for multiplayer design **IF** user requests network multiplayer support

**Key Tasks**:
1. If existing project: Analyze the existing project code to understand the current architecture
   - Directory & module structure (layers, namespaces, key entry points)
   - Technology stack & dependencies (engine, language, third-party libraries)
   - Architectural paradigms in use (DDD, ECS, MVC, etc.)
   - Module boundaries & inter-module communication (events, interfaces, direct calls)
   - Data flow (config loading, persistence, runtime state management)
   - Known constraints & technical debt (coupling issues, performance bottlenecks, deprecated patterns)
   - Integration points for new systems (where to hook in, what to extend)
2. Define Multi-Application structure (Client/Server)
3. Select Technology Stack (Engine, Languages)
4. Choose architectural paradigms using the **Paradigm Selection Guide** (see SKILL.md) for each module
5. Use the **System-Specific References** (see SKILL.md) to design each module
6. Map Iteration Milestones to system implementation scope (Milestone System Plan)

---

### Phase 3: Implementation Planning & Evolution

**Goal**: Create detailed implementation specifications, then review and refine for extensibility and maintainability.

- **Input**: `architect/technical_design.md`
- **Output**: `architect/implementation.md`
- **References**:
  - Use Specific System Architecture documents from `references/`
  - Read `references/evolution.md` for evolution strategies
  - Read `references/performance-optimization.md` (only if user requires performance optimization)

**Step 1 — Implementation Design**:
1. **Directory Structure**: Define the directory structure for the project
2. **Data Structures**: Define all core data types and structures
3. **Algorithms**: Specify key algorithms with pseudocode
4. **Class Design**: Document class hierarchies and relationships
5. **Object Relationships**: Define associations, dependencies, and lifecycles
6. **Key Code Snippets**: Provide critical implementation examples

**Step 2 — Evolution Review** (applied in-place to the output above):
1. **Isolation**: Ensure proper separation of concerns across modules
2. **Abstraction**: Apply appropriate interface abstractions at change points
3. **Composition**: Prefer composition over inheritance where applicable
4. **Future Changes**: Anticipate likely evolution and mark extension points

---

### Phase 4: Implementation (Out of Scope)

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
    - Can target any specific **Phase 1 - 3** individually.
    - **Input**: The **existing Output file** of that phase (e.g., `architect/technical_design.md` if refactoring Phase 2). *Crucial: Read the file first as the user may have modified it.*
    - **Goal**: Optimize, correct, or expand the document based on specific user feedback or new insights.
    - **Output**: Update the target file in-place.

---

## Output Document Structure

### requirement.md

```markdown
# {Project Name} - Requirement Analysis

## 1. Project Overview
Brief description of the project vision, target platform, and core goals.

## 2. Feature List
| Category | Feature | Priority | Notes |
|----------|---------|----------|-------|
| Platform | OS / Device targets | - | |
| Genre | Game type & sub-genre | - | |
| Network | Single-player / Multiplayer | - | |
| Scope | Project scale & milestones | - | |
| Performance | Target FPS, memory budget, loading time | - | |
| Testability | Test strategy, debug tools, GM panel | - | |
| Observability | Logging, monitoring, crash reporting | - | |
| Deployment | Build pipeline, CI/CD, patching | - | |
| Security | Anti-cheat, data validation, encryption | - | |

## 3. Domain Models
For core gameplay and complex logic systems.

### 3.1 Domain Vocabulary
| Term | Definition |
|------|-----------|

### 3.2 Domain Model Diagram
Entity relationships, state diagrams, system diagrams (use text/mermaid).

## 4. Use Cases
Per core feature, from summary → informal → detailed as needed.

### 4.x {Use Case Name}
- **Actor(s)**:
- **Preconditions**:
- **Main Scenario**: (numbered steps)
- **Extension Scenarios**: (branch / edge cases)
- **Business Rules**: (referenced rule IDs)

## 5. User Flows
Interaction flows for UI, gameplay mechanics, and cutscenes.

### 5.x {Flow Name}
- **Type**: UI Flow / Gameplay / Cutscene
- **Flow Description**: (sequential screens/states with transitions)

## 6. Iteration Milestones
Plan incremental delivery milestones. Each milestone forms a playable/testable Minimum Viable Product (MVP) or meaningful increment.

### Milestone {N}: {Name}
- **Goal**: What this milestone validates or delivers.
- **Included Features**: (reference Feature List items)
- **Included Use Cases**: (reference Use Case IDs from §4)
- **Deliverable**: What the user can see / play / test at this point.
- **Acceptance Criteria**: How to verify this milestone is complete.
- **Dependencies**: Prerequisites from previous milestones.
```

---

### technical_design.md

```markdown
# {Project Name} - Technical Design

## 1. Existing Project Analysis
> Skip this section for new projects.

- **Directory & Module Structure**: Layers, namespaces, key entry points.
- **Technology Stack & Dependencies**: Engine, language, third-party libraries.
- **Architectural Paradigms in Use**: DDD, ECS, MVC, etc.
- **Module Boundaries & Communication**: Events, interfaces, direct calls.
- **Data Flow**: Config loading, persistence, runtime state management.
- **Constraints & Tech Debt**: Coupling issues, performance bottlenecks, deprecated patterns.
- **Integration Points**: Where new systems hook in, what to extend.

## 2. Multi-Application Design
- **Network Form**: Single-player / Client-Server / P2P.
- **Application List**:
  | Application | Role | Description |
  |-------------|------|-------------|
- **Interaction Scheme**: Protocol / RPC / API between applications.

## 3. Technology Stack
| Category | Selection | Alternatives | Reason |
|----------|-----------|-------------|--------|
| Engine | | | |
| Language | | | |
| Networking | | | |
| Data Storage | | | |
| Key Libraries | | | |

## 4. Architecture Overview
### 4.1 Layer Diagram
Foundation Layer / Logic Layer / Application Layer separation.

### 4.2 Module Map
| Module | Layer | Paradigm | Description |
|--------|-------|----------|-------------|

### 4.3 Module Dependencies
Inter-module dependency and communication diagram (events, interfaces).

## 5. Module Design
Per module, repeat this section.

### 5.x {Module Name}
- **Paradigm**: DDD / Data-Driven / Prototype (with justification)
- **Responsibilities**: What this module owns.
- **Key Domain Concepts / Data Structures**: Core abstractions (no code).
- **External Interfaces**: How other modules interact with this one.
- **Internal Flow**: Key processes and state transitions.
- **Design Decisions**: Trade-offs and rationale.

## 6. Milestone System Plan
Map each milestone (from requirement.md §6) to concrete system implementation scope.

### Milestone {N}: {Name}
- **Systems to Implement**:
  | Module | Scope (Full / Partial) | Key Deliverables | Notes |
  |--------|----------------------|-------------------|-------|
- **Integration Work**: Cross-module wiring needed for this milestone.
- **Stub / Mock**: Systems not yet implemented but needed as placeholders.

### Prototype Iteration Breakdown
> For modules using the **Use-Case Driven Prototype** paradigm, further split each milestone into small iterations (1–3 days each).

#### Milestone {N} - Iteration {M}: {Short Description}
- **Target Use Case**: (reference Use Case ID)
- **Implementation Focus**: What to build in this iteration.
- **Fake / Deferred**: What to stub out (fake data, temp UI, placeholder art).
- **Validation**: How to verify the use case works (playtest criteria).
- **Refactor Notes**: Technical debt introduced, to be addressed later.
```

---

### implementation.md

````markdown
# {Project Name} - Implementation Plan

## 1. Directory Structure
```text
project-root/
├── src/
│   ├── foundation/     # Foundation Layer
│   ├── logic/          # Logic Layer modules
│   └── app/            # Application Layer
├── configs/            # Data tables & configurations
├── assets/             # Art, audio, etc.
└── tests/
```

## 2. Data Structures
Per module, define core types.

### 2.x {Module} Data Structures
- **Type Name**: Purpose, fields, constraints.
- **Relationships**: References (by ID), ownership, lifecycle.
- **Data Classification**: Config (static) / Data (persistent) / Instance (runtime).

## 3. Key Algorithms
### 3.x {Algorithm Name}
- **Purpose**:
- **Input / Output**:
- **Pseudocode**: (step-by-step)
- **Complexity**: Time & space.

## 4. Class Design
Per module, document class hierarchies.

### 4.x {Module} Classes
- **Class Diagram**: Inheritance & composition relationships (text/mermaid).
- **Key Classes**:
  | Class | Role (Entity/Service/VO/Repository/Factory) | Responsibilities |
  |-------|----------------------------------------------|-----------------|
- **Interface Definitions**: Abstract contracts between components.

## 5. Object Relationships
### 5.x {Module or Cross-Module} Relationships
- **Associations**: Who holds references to whom (and how: direct / ID / event).
- **Lifecycles**: Creation → active use → disposal flow.
- **Ownership**: Aggregate boundaries, who manages disposal.

## 6. Key Code Snippets
Critical implementation examples that clarify design intent.

### 6.x {Snippet Title}
- **Context**: Which class/module this belongs to.
- **Code**: (language-appropriate snippet)
- **Notes**: Why this approach, edge cases to handle.

## 7. Evolution & Extension Points
Document decisions from the Evolution Review (Phase 3 Step 2).

### 7.x {Module or Cross-Module}
- **Isolation**: How this module is decoupled from others (communication method, dependency direction).
- **Abstractions**: Interfaces / strategies introduced at change points (and why).
- **Composition**: Component or strategy splits applied (what was decomposed, how parts recombine).
- **Anticipated Changes**: Likely future requirements and the extension points reserved for them.
````

---

## Example Workflows

### Example 1: New Project (DDD Focus)

- **User Input**: "I want to build an ARPG with complex combat involving many states, damage rules, and AI interactions."
- **Execution Path**:
    1.  **Phase 0**: Ask review preference.
    2.  **Phase 1 - Requirement Analysis**:
        - Read `references/requirements.md`.
        - Focus on **Domain Model Analysis** for combat entities and **Use Cases** for combat flows.
        - Plan milestones (e.g., M1: basic movement + attack, M2: damage rules + buffs, M3: AI combat).
        - Output: `architect/requirement.md`.
    3.  **Phase 2 - Technical Design**:
        - Read `references/macro-design.md` + `references/principles.md`.
        - Define multi-application structure and technology stack.
        - Select **DDD** for core combat (high rule complexity, rich domain concepts). Read `references/domain-driven-design.md`.
        - System refs: `system-skill.md`, `system-action-combat.md`, `system-time.md`, `system-scene.md`, `algorithm.md`.
        - Map milestones to system scope (Milestone System Plan).
        - Output: `architect/technical_design.md`.
    4.  **Phase 3 - Implementation Planning & Evolution**:
        - Read `references/evolution.md`.
        - Step 1: Design data structures, class hierarchies, and key algorithms for combat systems.
        - Step 2: Apply composition and abstraction patterns; mark extension points for new weapon/enemy types.
        - Output: `architect/implementation.md`.

### Example 2: Existing Project (Hybrid Paradigms)

- **User Input**: "I want to add a Skill System to my current combat engine. It needs effects, cooldowns, and data-configurable skills."
- **Execution Path**:
    1.  **Phase 0**: Ask review preference.
    2.  **Phase 1 - Requirement Analysis**:
        - Read `references/requirements.md`.
        - Define domain entities (Skill, Effect) and use cases for skill interactions.
        - Plan milestones (e.g., M1: basic skill cast + cooldown, M2: effects + buffs, M3: data-configurable skills).
        - Output: `architect/requirement.md`.
    3.  **Phase 2 - Technical Design**:
        - **Analyze existing project code** to understand current architecture.
        - Read `references/macro-design.md` + `references/principles.md`.
        - Select **DDD** for core skill logic (rules, interactions). Read `references/domain-driven-design.md`.
        - Select **Data-Driven** for skill configurations (tables, content). Read `references/data-driven-design.md`.
        - System refs: `system-skill.md`, `system-foundation.md`, `system-time.md`.
        - Map milestones to system scope (Milestone System Plan).
        - Output: `architect/technical_design.md`.
    4.  **Phase 3 - Implementation Planning & Evolution**:
        - Read `references/evolution.md`.
        - Step 1: Design skill data structures, effect class hierarchies, and configuration schemas.
        - Step 2: Apply composition (component pattern for reusable effects) and abstraction (interfaces for targeting); ensure isolation from existing combat modules.
        - Output: `architect/implementation.md`.

### Example 3: Rapid Prototype

- **User Input**: "I have a puzzle mechanic idea. I want to build a quick demo this weekend to validate it."
- **Execution Path**:
    1.  **Phase 0**: Ask review preference.
    2.  **Phase 1 - Requirement Analysis** (lightweight):
        - Read `references/requirements.md`.
        - Minimal analysis, focus on core puzzle mechanic.
        - Plan milestones as iterations (e.g., M1: display map, M2: character movement, M3: puzzle interaction).
        - Output: `architect/requirement.md`.
    3.  **Phase 2 - Technical Design** (lightweight):
        - Read `references/macro-design.md` + `references/principles.md`.
        - Select **Use-Case Driven Prototype**. Read `references/prototype-design.md`.
        - System refs as needed: `system-time.md`, `algorithm.md`.
        - Map milestones to prototype iteration breakdown.
        - Output: `architect/technical_design.md`.
    4.  **Phase 3 - Implementation Planning & Evolution**:
        - Read `references/evolution.md`.
        - Step 1: Focus on rapid implementation of core use case; minimal class design.
        - Step 2: Plan extraction points for after mechanic is validated; mark refactor targets.
        - Output: `architect/implementation.md`.

### Example 4: Refactor Extension (On-Demand)

- **User Input**: "I've drafted the implementation plan. Review and refactor it for better architecture and performance."
- **Execution Path**:
    1.  **Read** existing `architect/implementation.md`.
    2.  **Refactor Phase (Extension)** targeting Phase 3:
        - Read `references/evolution.md`.
        - Read `references/performance-optimization.md` (user requested performance).
        - Apply isolation, composition, and abstraction patterns.
        - Introduce pooling, caching, or time-slicing where needed.
        - Update: `architect/implementation.md`.
