# Time Logic & Flow Control

This reference provides a comprehensive overview of mechanisms used to drive and orchestrate game logic over time, from basic frame updates to complex task planning and global flow management.

## 1. Core Mechanisms

### Update Loop (Tick)
The most fundamental mechanism, driven by the game engine's main loop.
- **Frame Update**: `Update(dt)`. Frequency depends on FPS. Suitable for visuals and non-deterministic logic.
- **Fixed Update**: `FixedUpdate()`. Runs at a constant frequency. Essential for physics and deterministic logic.

### Async Logic & Coroutines
Techniques for "code slicing," allowing logic to pause and resume across multiple frames without blocking threads.
- **Coroutines**:
    - **Mechanism**: A state machine driven by an external iterator (`yield return`).
    - **Usage**: Lightweight, suitable for sequential scripted sequences.
- **Async/Await**:
    - **Mechanism**: Task-based, usually managed by a runtime library.
    - **Context**: In games, custom `SynchronizationContext` is often used to ensure async tasks resume on the main logic thread.

## 2. Event-Based Time Logic

### Timers
Used for delayed or periodic execution based on time or frame counts.
- **Implementation Patterns**:
    - **Polling List**: Iterating through all timers every frame. Simple, precise for small sets.
    - **Delay Queue**: Using a priority queue (Min-Heap) based on expiration time.
    - **Timing Wheel**: Discrete time slots (buckets) for high-performance scheduling of massive timer counts.

### Command Queue
Sequentially executes logic "commands" (Start, Update, IsComplete, End).
- **Features**: Decouples command generation from execution; supports dynamic insertion and deletion of commands during runtime.
- **Extensions**: Priority channels (High/Low), category-based queues (UI/Resource/Battle).

## 3. State Machines (FSM)
The primary tool for managing complex logic states and transitions.

### Implementation Patterns
- **Enum-Switch**: Simple state variable + switch statement. High performance, best for simple controllers.
- **Async FSM**: Each state is an async function with an internal loop. Best for linear sequences and scripted scenes.
- **State Pattern (OO)**: Each state is a class (`IState`). Best for complex, distinct behaviors.
- **Data/Script Driven**: Logic defined in external files (JSON/Lua) or visual graphs (Animator).

### Advanced FSM Structures
- **Stack FSM**: Uses a stack to manage states, allowing "Push" (overlay) and "Pop" (return to previous) operations.
- **Hierarchical FSM (HFSM)**: States can contain sub-state machines (Composite pattern).
- **Transition Table**: A 2D lookup table to manage complex transition conditions centrally.

### Parallel Logic Management
- **Bit Flags**: Binary status flags (e.g., `isFlying | isStunned`). Fast but data-less.
- **Tags**: String or Enum labels. Flexible, good for classification and spatial queries.
- **Switch Objects**: Pairs of enable/disable actions encapsulated as an object.
- **Parallel State Objects (Buffs)**: Classes representing additive states, often using a **Hook System** to modify behavior (e.g., `OnMoving`, `OnDamage`).

## 4. Sequence & Interpolation

### Action Objects
Composable command-like objects to build behavior sequences.
- **Types**: Instant (CallFunc), Time-based (Delay), Progress-based (FromTo).
- **Control**: Sequence, Parallel, Repeat, Speed/Ease decorators.

### Tweens (Easing)
Fluent/chainable APIs focused on numerical interpolation (Interpolating Position, Alpha, Scale).
- **Core**: Ease functions (In/Out/In-Out) and property interpolation.

### Timeline
Parallel tracks and keyframes for fixed-duration events.
- **Concepts**: Tracks (Property, Event, Clip), KeyFrames (Interpolation points), Clips (Sub-states).
- **Usage**: Cutscenes, fixed skill animations, complex VFX.

## 5. Decision & Goal-Oriented Structures

### Behavior Trees (BT)
Hierarchical structures for decision making.
- **Nodes**: Leaf (Action, Condition), Composite (Sequence, Selector), Decorator.
- **Preemptive Selector**: Priority-based sub-tree switching that reacts immediately to environment changes.

### Task Graphs
Goal-oriented logic based on task dependencies (Directed Acyclic Graph - DAG).
- **Planning (Solver)**: Uses Depth-First Search (DFS) and Topological Sort to determine execution order.
- **AND/OR Dependencies**: Handling tasks that require all prerequisites vs. multiple choice paths.
- **Task Cost**: Using scoring/heuristics to pick the optimal path.

## 6. Global Game Flow & Controllers

### Game Flow State Machine
A high-level FSM (usually a Stack FSM) that manages the overall lifecycle of the game application.
- **Typical States**: `Init`, `MainMenu`, `LevelSelector`, `Battle`, `Pause`.

### Initialization Logic
Best implemented using **Async Functions** to handle sequential, non-blocking setup (Resources -> Configs -> Modules). 
- **Progress Tracking**: Logical mapping of steps to a percentage bar (e.g., Load Map = 20%, Spawn Enemies = 70%).

### Gameplay Mode Controllers
The entry point for specific level logic (e.g., `ChaseModeController`, `SurvivalModeController`).
- **Driving Domain Logic**: The controller delegates core combat logic to the Battle Scene (Domain Model) via `mScene.Update(dt)`.
- **Condition Logic (Victory/Defeat)**:
    - **Update Polling**: Simple `if` checks in the update loop (best for prototypes).
    - **Trigger Lists**: A list of `LevelTrigger` objects (Condition + Handler) checked periodically.
    - **Condition Trees**: Using Decision Trees or Behavior Trees for complex, branching level logic.
    - **Reactive (Rx)**: Subscribing to data streams (e.g., `mScene.EnemyCount.Where(c => c == 0).Subscribe(...)`).
- **Time/Flow Control**: Utilizing timers and command queues to orchestrate level-specific events (e.g., Boss appearance, wave spawns).
