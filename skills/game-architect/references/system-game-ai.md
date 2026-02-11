# Game AI System Architecture

Reference for Game AI architecture decisions and component design. Focuses on architectural patterns and technique selection rather than algorithm details.

## 1. Design Principles

### AI Model Layers
- **Movement**: Physical motion control (steering, path following, formations).
- **Decision Making**: Action selection (FSM, BT, GOAP, Utility).
- **Strategy**: Group coordination and high-level planning (squad tactics, influence maps).
- **Infrastructure**: Engine support (pathfinding graphs, perception, messaging, scheduling).

### The Complexity Fallacy
- Simple behaviors often outperform complex algorithms. Hacks → Heuristics → Algorithms: use the simplest that works.
- **Perception Window**: Players notice *behavior changes*, not algorithm sophistication. AI only needs to be "smart enough" for the context.

### Performance Constraints
- **Time Slicing**: Distribute AI calculations across multiple frames.
- **AI LOD**: Simplify logic for distant/off-screen agents (reduce update frequency, use simpler behaviors).
- **Anytime Algorithms**: Return "best so far" result when time budget expires.
- **Cache Coherency**: Organize data (SoA) to minimize cache misses for batch processing.

## 2. Movement

### Technique Selection

| Technique | Applicability | Key Concepts |
|:---|:---|:---|
| **Kinematic** | Simple games, top-down | Direct velocity, no acceleration |
| **Steering Behaviors** | Most action games | Seek, Flee, Arrive, Pursue, Evade, Wander, Path Following |
| **Group Steering** | Flocking, crowds | Separation, Cohesion, Alignment (Boids) |
| **Avoidance** | Multi-agent navigation | Obstacle Avoidance, RVO/ORCA (reciprocal collision-free motion) |
| **Formations** | RTS, squad games | Fixed, Scalable, Emergent; Slot Assignment |

### Steering Pipeline
- **Blending**: Weighted sum of multiple behaviors.
- **Arbitration**: Priority-based selection (e.g., avoidance > seek).

### Advanced
- **Physics Prediction**: Firing solutions, projectile trajectory, iterative targeting.
- **Motor Control**: Output filtering (anti-jitter), capability-sensitive steering (turn radius limits).
- **3D Movement**: Quaternion rotation, 3D steering extensions (flight, swimming).

## 3. Pathfinding (Architecture)

Algorithm details in `algorithm.md`. This section covers architectural decisions.

### World Representation Selection

| Representation | Best For | Trade-offs |
|:---|:---|:---|
| **Tile/Grid** | 2D games, simple levels | Simple but memory-heavy for large worlds |
| **Waypoint Graph** | Linear levels, simple 3D | Manual placement, sparse coverage |
| **NavMesh** | Modern 3D games (standard) | Handles terrain & agent sizes, requires generation tools |
| **Flow Fields** | Mass units to same target (RTS) | Efficient for hundreds of units, high memory per field |

### Architectural Concerns
- **Hierarchical Pathfinding**: Abstract layers (room-to-room) before detail. Essential for large worlds.
- **Dynamic Replanning**: D* Lite / LPA* for changing environments.
- **Interruptible / Time-Sliced**: Spread calculation over frames for large searches.
- **Path Smoothing**: Post-process to remove jagged edges.
- **Cost Functions**: Terrain type costs, tactical cost overlays.

## 4. Decision Making

### Technique Selection

| Technique | Complexity | Applicability | Data-Driven |
|:---|:---|:---|:---|
| **Decision Tree** | Low | Simple branching logic, few states | Medium |
| **FSM** | Low-Medium | Clear distinct states, predictable transitions | Low |
| **HFSM** | Medium | Complex states with sub-behaviors | Low |
| **Behavior Tree** | Medium-High | Complex, modular, reusable behaviors (industry standard) | High |
| **GOAP** | High | Dynamic planning, emergent behavior | High |
| **Utility AI** | Medium-High | Scoring-based selection, smooth behavior blending | High |
| **Rule-Based** | Medium | Large rule sets, inference (Rete algorithm) | High |

### Shared Infrastructure
- **Blackboard**: Centralized knowledge base for decoupling perception, decision, and action systems.
- **Scripting (Lua/Python)**: Hot-reloadable logic for rapid iteration.
- **Fuzzy Logic**: Degrees of truth for smooth transitions (e.g., "somewhat aggressive").

## 5. Tactical & Strategic AI

### Tactical Analysis
- **Influence Maps**: Grids representing territory control, danger, resources. Propagation + convolution filters to find strategic features.
- **Tactical Locations**: Annotated waypoints (cover, sniper spots, ambush points). Auto-generated via raycasting/geometry analysis.
- **Tactical Pathfinding**: Blend distance costs with tactical weights (danger avoidance, cover preference).

### Coordinated Action
- **Multi-Tier Architecture**: Strategic (Commander) → Operational (Squad) → Tactical (Individual).
- **Squad AI**: Group management, formation maintenance, role assignment.
- **Emergent Cooperation**: Local rules producing coordinated behavior (flocking, wolf-pack).

## 6. Learning & Adaptation

### Online vs. Offline
- **Offline (Development-time)**: Train during development, ship fixed models. Safe, predictable.
- **Online (Runtime)**: Adapt during gameplay. Risky (over-learning, exploit bugs), but enables dynamic difficulty and player modeling.

### Technique Selection

| Technique | Applicability | Key Concepts |
|:---|:---|:---|
| **Parameter Modification** | Difficulty tuning, adaptive AI | Hill Climbing, Simulated Annealing |
| **Action Prediction** | Fighting games, player modeling | N-Grams, Hierarchical N-Grams, pattern matching |
| **Decision Learning** | Generating behaviors from data | Naive Bayes, ID3 (decision tree generation) |
| **Reinforcement Learning** | Policy learning from reward signals | Q-Learning, Exploration vs. Exploitation |
| **Neural Networks** | Complex pattern recognition, strategy | Perceptrons → Multi-layer → Deep Learning; high data/compute cost |

### Design Concerns
- **Over-Learning**: AI becomes too specialized or exploits unintended mechanics. Use caps and decay.
- **Predictable Mental Models**: Players should understand *why* the AI adapts. Transparent behavior changes build trust.
- **Intra vs. Inter-Behavior**: Learning within a task (tune parameters) vs. learning which task to perform (switch strategies).

## 7. Board Games & Adversarial Search

### Core Architecture

| Technique | Applicability | Key Concepts |
|:---|:---|:---|
| **Minimax** | Perfect-info turn-based (Chess, Checkers) | Recursive search, static evaluation function, Negamax variant |
| **Alpha-Beta Pruning** | Minimax optimization | Prune branches that cannot affect outcome |
| **MCTS** | High branching factor (Go, complex strategy) | Statistical sampling, UCT (exploration/exploitation balance) |
| **Iterative Deepening** | Time-constrained search | Depth 1→2→3... until budget expires; always has a valid move |

### Optimization Techniques
- **Transposition Tables**: Zobrist Hashing to cache and reuse evaluated positions across different move orders.
- **Opening Books / Endgame Tablebases**: Pre-calculated databases for known game phases.
- **Evaluation Functions**: Domain-specific scoring of board states (material, position, mobility).

### Application Beyond Board Games
- **Turn-Based Strategy** (Civilization, XCOM): Minimax/MCTS for combat decisions, Utility AI for strategic planning.
- **Card Games**: MCTS with information set sampling for imperfect information.

## 8. Perception & World Interface

### Sense Management
- **Visual**: Line of Sight, vision cones, occlusion checks.
- **Auditory**: Sound propagation, volume attenuation, source localization.
- **Memory**: Remember last-known position/state of perceived objects.
- **Optimization**: Region-based sense manager using spatial partitioning.

### Communication
- **Polling**: Check state at intervals. Simple, suitable for low-frequency queries.
- **Events**: Message-based, decoupled. Preferred for reactive AI.

## 9. Genre Architecture Guide

| Genre | Movement Focus | Decision Focus | Key Techniques |
|:---|:---|:---|:---|
| **FPS/TPS** | Steering + Cover | BT/HFSM | Perception system, tactical locations, squad coordination |
| **RTS/MOBA** | Flow Fields + Formations | Multi-Tier + Utility | Influence maps, strategic planning, mass pathfinding |
| **Action RPG** | Steering + Avoidance | BT/FSM | Combat distance management, attack selection, group tactics |
| **Driving** | Physics steering | FSM/Scripted | Racing lines, overtaking, drafting |
| **Turn-Based** | N/A | MinMax/MCTS/Utility | Evaluation functions, search optimization, difficulty tuning |
| **Stealth** | Patrol paths | FSM/BT | Perception (vision cones, sound), alert propagation |
| **Simulation** | Flocking/Steering | Utility/Rules | Ecosystem balance, emergent behavior, population dynamics |
