# Game AI System Architecture

This document provides a comprehensive reference for Game AI architecture, techniques, and design patterns, structured around the definitive "AI for Games" curriculum. It serves as a high-level guide to the components required for building robust and intelligent game agents.

## 1. Core AI Concepts

Understanding the foundational models, constraints, and types of AI in a gaming context.

### Model of Game AI
-   **Movement**: Algorithms for moving characters physically in the world (e.g., steering, path following).
-   **Decision Making**: Logic for choosing what actions to take (e.g., "Attack" vs. "Hide").
-   **Strategy**: High-level group coordination and planning (e.g., squad tactics).
-   **Infrastructure**: The underlying engine support (pathfinding graphs, influence maps, messaging).
-   **Agent-Based AI**: Designing self-contained entities that perceive, think, and act.

### The Complexity Fallacy
-   **Simple vs. Complex**: Simple behaviors often yield better results than complex "black box" algorithms.
    -   **Hacks**: Ad-hoc solutions that work for specific cases.
    -   **Heuristics**: Rules of thumb that provide "good enough" solutions.
    -   **Algorithms**: Formally defined procedures for solving problems.
-   **Perception Window**: The player's ability to notice intelligence is limited; AI only needs to be "smart enough" for the context.
-   **Changes of Behavior**: Visible changes in behavior are often more important than the sophistication of the underlying logic.

### Constraints & Platform Issues
-   **Processor Issues**:
    -   **Time Slicing**: Distributing AI calculations across multiple frames.
    -   **Load Balancing**: Managing CPU spikes during complex calculations.
-   **Memory Concerns**:
    -   **Footprint**: Managing memory for navigation meshes, lookup tables, and influence maps.
    -   **Cache Coherency**: Organizing data to minimize cache misses.

### The AI Engine
-   **Structure**: Separation of concerns between AI logic and game engine core.
-   **Tool Concerns**: The need for debugging and visualization tools.

## 2. Movement Systems

Algorithms for controlling the physical motion of agents, from basic kinematics to complex steering pipelines.

### Kinematic Movement
-   **Basics**: Movement without accounting for inertia or acceleration.
-   **Algorithms**:
    -   **Seek**: Moving directly towards a target.
    -   **Wandering**: Random movement to explore an area.

### Steering Behaviors
Dynamic movement algorithms that output acceleration/force.

-   **Fundamental**:
    -   **Seek & Flee**: Moving towards or away from a target.
    -   **Arrive**: Slowing down to stop at a specific point.
    -   **Align**: Rotating to match a target orientation.
    -   **Velocity Matching**: Matching the speed and direction of a target.
-   **Delegated**:
    -   **Pursue & Evade**: Predicting a target's future position and seeking/fleeing that point.
    -   **Face**: Rotating to look at a target.
    -   **Look Where You're Going**: Aligning orientation with the velocity vector.
-   **Group**:
    -   **Separation**: Keeping distance from neighbors to avoid crowding.
    -   **Cohesion**: Moving towards the average position of neighbors.
    -   **Alignment**: Matching the average heading of neighbors.
    -   *(Combined, these form Flocking behavior)*.
-   **Avoidance**:
    -   **Collision Avoidance**: Predicting future collisions and steering to avoid them.
    -   **Obstacle & Wall Avoidance**: Detecting static geometry and steering away.
    -   **RVO / ORCA**: Reciprocal Velocity Obstacles / Optimal Reciprocal Collision Avoidance. Advanced algorithms for multi-agent navigation that guarantee collision-free motion by having agents mutually adjust their velocities.
-   **Advanced**:
    -   **Wander**: Producing smooth, random movement using a projected circle.
    -   **Path Following**: Steering to stay close to a defined path or series of waypoints.

### Steering Pipelines
Combining multiple behaviors to create complex movement.

-   **Blending**: Mixing multiple steering outputs.
    -   **Weighted Blending**: Assigning importance weights to different behaviors (e.g., 80% separation, 20% seek).
-   **Arbitration**: Selecting the most important steering output.
    -   **Priorities**: Checking behaviors in order of importance (e.g., collision avoidance first, then seek).
    -   **Cooperative Arbitration**: More complex selection logic.

### Advanced Movement
-   **Physics Prediction**:
    -   **Aiming & Shooting**: Calculating firing vectors.
    -   **Projectile Trajectory**: Accounting for gravity and speed.
    -   **The Firing Solution**: Solving for the intersection of projectile and moving target.
    -   **Drag**: Accounting for air resistance.
    -   **Iterative Targeting**: Refining solutions over time.
-   **Jumping**:
    -   **Jump Points**: Specific locations where jumps can occur.
    -   **Landing Pads**: Valid target areas for jumps.
    -   **Hole Fillers**: Handling gaps in navigation data.
-   **Coordinated Movement**:
    -   **Fixed Formations**: Rigid relative positions.
    -   **Scalable Formations**: Formations that adapt to the number of units.
    -   **Emergent Formations**: Formations arising from local rules.
    -   **Slot Assignment**: Determining which agent goes to which spot in the formation.
-   **Motor Control**:
    -   **Output Filtering**: Smoothing steering outputs to prevent jitter.
    -   **Capability-Sensitive Steering**: Limiting movement based on agent capabilities (e.g., turn radius).
-   **3D Movement**:
    -   **Rotation in 3D**: Quaternions and axis-angle representations.
    -   **3D Steering**: Extending 2D behaviors to 3D space (e.g., flight, swimming).

## 3. Pathfinding

Solving the problem of how to get from A to B in complex environments.

### Graph Algorithms
-   **Dijkstra**:
    -   The foundational algorithm for finding shortest paths in weighted graphs.
    -   Explores all directions equally; guaranteed to find the shortest path but can be slow.
-   **A* (A-Star)**:
    -   The industry standard heuristic search algorithm.
    -   **Heuristics**: Euclidean, Manhattan, Diagonal distance to estimate cost to goal.
    -   **Optimizations**: Node Array A* (data locality), Binary Heaps (priority queue efficiency).
    -   **Performance**: Balancing accuracy vs. speed.

### World Representations
How the game world is converted into a graph for pathfinding.

-   **Tile Graphs**: Grid-based representation (simple but memory intensive for large worlds).
-   **Dirichlet Domains**: Voronoi regions based on obstacles.
-   **Points of Visibility**: Waypoint graphs connecting mutually visible points.
-   **Navigation Meshes (NavMesh)**:
    -   Polygons representing walkable surfaces.
    -   The standard for modern 3D games.
    -   Handles varying terrain and agent sizes efficiently.
-   **Cost Functions**: Defining the "cost" of traversing different terrain types (e.g., mud vs. road).
-   **Path Smoothing**: Post-processing paths to remove jagged edges and look more natural.

### Advanced Pathfinding
-   **Hierarchical Pathfinding**:
    -   Pathfinding on abstract layers (e.g., room-to-room) before detailed pathfinding.
    -   Speeds up long-distance searches significantly.
    -   **Instanced Geometry**: Handling repeating map sections.
-   **Dynamic Pathfinding**:
    -   **D* Lite / LPA***: Efficiently replanning when the world changes (e.g., a bridge is destroyed).
-   **Continuous Time**: Pathfinding that accounts for moving targets or time-dependent costs.
-   **Movement Planning**:
    -   Integrating animations and footfalls with path data.
    -   Ensuring the agent can physically execute the path (e.g., jump distances, turn radii).
-   **Other Techniques**:
    -   **Open Goal Pathfinding**: Finding a path to *any* valid goal state.
    -   **Interruptible Pathfinding**: Spreading calculation over multiple frames.

## 4. Decision Making

The "Brain" of the AI; choosing actions based on state and goals.

### Decision Trees
-   **Structure**: Hierarchies of conditions (nodes) leading to actions (leaves).
-   **Pros/Cons**: Simple, fast, easy to visualize, but can become unmanageable for complex behaviors.
-   **Learning**: ID3 algorithm for generating trees from examples.
-   **Random Decision Trees**: Adding variation to behavior.

### State Machines (FSM)
-   **Finite State Machines**:
    -   **States**: Distinct modes of behavior (Idle, Patrol, Attack).
    -   **Transitions**: Conditions for switching between states.
-   **Hierarchical State Machines (HFSM)**:
    -   Nesting states (e.g., "Combat" state contains "Melee" and "Ranged" sub-states).
    -   Reduces complexity and allows for behavior reuse.
-   **Fuzzy State Machines**: Using fuzzy logic for transitions (e.g., "somewhat angry" triggers a transition).

### Behavior Trees
-   **Structure**:
    -   **Composites**: Control flow nodes (Selector, Sequence).
    -   **Decorators**: Modifiers (Inverter, Repeater, Limit).
    -   **Leaves**: Actions and Conditions.
-   **Concurrency**: Parallel nodes for handling multiple behaviors simultaneously (e.g., walking while talking).
-   **Data**: Blackboards for sharing data between nodes and decoupling logic.
-   **Reusing Trees**: Sub-trees as modular components.

### Goal-Oriented Behavior (GOAP)
-   **Planning**: Dynamically building a sequence of actions to satisfy a goal.
-   **Utility**: Selecting goals based on "desirability" scores.
-   **IDA* (Iterative Deepening A*)**: Used for searching the action space to find a plan.
-   **Timing**: Handling long-running plans and replanning.

### Rule-Based Systems
-   **Inference Engines**: Systems that derive conclusions from a set of rules and facts.
-   **Rule Arbitration**: Deciding which rule to apply when multiple match.
-   **Rete Algorithm**: Efficient pattern matching for large rule sets.
-   **Unification**: Matching patterns with variables.

### Blackboard Architectures
-   **Concept**: A centralized knowledge base where different "experts" (systems) read and write data.
-   **Decoupling**: Allows independent systems (perception, combat, navigation) to coordinate without direct dependencies.

### Other Techniques
-   **Fuzzy Logic**: Handling degrees of truth (e.g., "somewhat hungry", "very dangerous").
-   **Markov Systems**: Probabilistic state transitions based on history.
-   **Scripting**: Using languages like Lua or Python for gameplay logic to allow rapid iteration.

## 5. Tactical and Strategic AI

Reasoning about the map, squads, and long-term goals.

### Waypoint Tactics
-   **Tactical Locations**: Annotating the map with semantic data.
    -   Cover points, sniper spots, ambush locations, shadow areas.
-   **Generation**:
    -   **Automatic Analysis**: Raycasting and geometry analysis to place points.
    -   **Condensation**: Reducing dense graphs to essential tactical points.

### Tactical Analysis
-   **Influence Maps**:
    -   Grids representing territory control, danger, or resource density.
    -   **Propagation**: Spreading influence over distance.
-   **Terrain Analysis**: Assessing visibility, height advantages, and chokepoints.
-   **Map Flooding**: Algorithms for propagating influence (similar to Dijkstra).
-   **Convolution Filters**: Processing influence maps (e.g., blurring, edge detection) to find strategic features.
-   **Cellular Automata**: Simulating complex systems (e.g., fire spread, fluid dynamics) for tactical awareness.

### Tactical Pathfinding
-   **Cost Functions**: Modifying pathfinding costs based on tactical data (e.g., "avoid high danger areas").
-   **Tactic Weights**: Blending distance costs with tactical concerns.
-   **Tactical Graphs**: Building graphs specifically for tactical reasoning, separate from navigation.

### Coordinated Action
-   **Multi-Tier AI**:
    -   **Strategic**: High-level goals (Commander).
    -   **Operational**: Squad-level coordination.
    -   **Tactical**: Individual unit behavior.
-   **Squad AI**: Managing groups of agents.
-   **Formations**: Maintaining spatial relationships during movement.
-   **Emergent Cooperation**: Behaviors that appear coordinated without explicit communication (e.g., flocking, wolf-pack tactics).
-   **Military Tactics**: Implementing real-world concepts like suppression fire, bounding overwatch, and flanking.

## 6. Learning

Techniques for AI that improves or adapts over time.

### Basics
-   **Online vs. Offline**: Learning during gameplay (adaptation) vs. during development (training).
-   **Intra-Behavior vs. Inter-Behavior**: Learning within a specific task vs. learning which task to perform.
-   **Over-Learning**: The risk of becoming too specialized or exploiting bugs.

### Algorithms
-   **Parameter Modification**:
    -   **Hill Climbing**: Iteratively improving parameters to maximize a score.
    -   **Simulated Annealing**: Avoiding local maxima by allowing temporary worsening.
-   **Action Prediction**:
    -   **N-Grams**: Predicting the next action based on a sequence of previous actions.
    -   **String Matching**: Finding patterns in player input.
    -   **Hierarchical N-Grams**: Analyzing patterns at different levels of abstraction.
-   **Decision Learning**:
    -   **Naive Bayes Classifiers**: Probabilistic classification based on features.
    -   **ID3**: Generating decision trees from data.
-   **Reinforcement Learning (RL)**:
    -   **Q-Learning**: Learning a policy (action selection) based on reward/punishment signals.
    -   **Exploration vs. Exploitation**: Balancing trying new things vs. using known best actions.
-   **Artificial Neural Networks (ANN)**:
    -   **Perceptrons**: Single-layer networks.
    -   **Multi-layer Networks**: Handling non-linear problems.
    -   **Topology**: Feedforward vs. Recurrent networks.
-   **Deep Learning**:
    -   Using deep neural networks for complex tasks (e.g., image recognition, complex strategy).
    -   Requires large amounts of data and processing power.

## 7. Procedural Content Generation (PCG)

Using AI to create game content automatically.

### Algorithms
-   **Pseudorandom Numbers**:
    -   **Noise**: Perlin, Simplex.
    -   **Seeds**: Ensuring reproducibility.
    -   **Halton Sequences**: Low-discrepancy sequences for better distribution.
-   **L-Systems (Lindenmayer Systems)**:
    -   Grammar-based generation for vegetation and organic structures.
    -   **Turtle Graphics**: Interpreting strings as drawing commands.
-   **Landscape Generation**:
    -   **Perlin Noise**: Creating natural-looking terrain heightmaps.
    -   **Erosion**: Simulating Thermal and Hydraulic erosion to age the terrain.
    -   **Altitude Filtering**: Adjusting terrain based on height rules.
-   **Dungeon/Maze Generation**:
    -   **Depth-First Backtracking**: Creating perfect mazes (one path between any two points).
    -   **Cellular Automata**: Cave generation (e.g., Game of Life rules).
    -   **Recursive Subdivision**: Dividing space into rooms.
    -   **Generate and Test**: Creating random structures and discarding invalid ones.
-   **Shape Grammars**: Defining rules for combining geometric shapes (e.g., building architecture).

## 8. Board Games & Game Theory

AI for turn-based and perfect information games.

### Game Theory
-   **Zero-Sum Games**: One player's gain is another's loss.
-   **The Game Tree**: Representing all possible moves and states.

### Minimaxing
-   **The Algorithm**: Recursive search to minimize the opponent's maximum potential gain.
-   **Static Evaluation Function**: Scoring a board state without looking further ahead.
-   **Alpha-Beta Pruning**: Optimizing search by pruning branches that cannot influence the final decision.
-   **Negamax / Negascout**: Variations for implementation efficiency.

### Optimization
-   **Transposition Tables**:
    -   Hashing game states (Zobrist Hashing) to store and retrieve previously calculated results.
    -   Avoids re-evaluating the same position reached via different move orders.
-   **Iterative Deepening**:
    -   Running searches at depth 1, then 2, then 3, etc., until time runs out.
    -   Ensures a valid move is always available.
-   **Monte Carlo Tree Search (MCTS)**:
    -   Statistical sampling of game trees.
    -   Used in games with high branching factors (e.g., Go) where Minimax is impractical.
    -   **UCT (Upper Confidence Bound for Trees)**: Balancing exploration and exploitation in tree search.

### Other Techniques
-   **Opening Books**: Pre-calculated moves for the beginning of the game.
-   **Endgame Tablebases**: Perfect play databases for few-piece positions.
-   **Turn-Based Strategy**: Applying these concepts to games like Civilization or XCOM.

## 9. Supporting Technologies

The "plumbing" that makes AI possible.

### Execution Management
-   **Scheduling**:
    -   **Time-Slicing**: Distributing updates across frames to maintain FPS.
    -   **Load-Balancing**: Prioritizing tasks based on available CPU time.
    -   **Hierarchical Scheduling**: Managing groups of tasks.
-   **Level of Detail (LOD)**:
    -   **Graphics LOD**: Reducing visual quality for distant objects.
    -   **AI LOD**: Simplifying logic for distant/off-screen agents (e.g., stopping physics, using simple movement).
    -   **Scheduling LOD**: Updating distant agents less frequently.
-   **Anytime Algorithms**: Algorithms that can be stopped at any time and return the "best so far" result.

### World Interfacing
-   **Communication**:
    -   **Polling**: Checking state at intervals (simple but can be inefficient).
    -   **Events**: Message-based communication (decoupled and efficient).
-   **Event Managers**: Centralized systems for dispatching messages.
-   **Sense Management**:
    -   **Visual**: Line of Sight, cones of vision, occlusion.
    -   **Auditory**: Sound propagation, volume, and attenuation.
    -   **Memory**: Remembering seen objects (position, last known state) even when out of view.
    -   **Region Sense Manager**: Optimizing queries using spatial partitioning.

### Tools & Pipeline
-   **Debugging**:
    -   Visualizing navmeshes, paths, logic trees, and influence maps in-game.
    -   Logging and replay systems.
-   **Data-Driven Design**:
    -   Exposing parameters to designers via editors.
    -   Hot-reloading data to tune behavior without recompiling.
-   **Toolchain**:
    -   Integrated Game Engines (Unity, Unreal) vs. Custom Tools.
    -   Remote Debugging.

### Programming Game AI
-   **Languages**:
    -   **C++**: Performance-critical systems.
    -   **C# / Java**: Managed languages for ease of development.
    -   **Scripting (Lua, Python)**: Gameplay logic and rapid iteration.
-   **Scripted AI**: Embedding scripting languages into the engine.

## 10. Designing Game AI

Applying AI techniques to specific game genres and the design process itself.

### The Design Process
-   **Evaluating Behaviors**: Determining exactly what the AI needs to do to support the gameplay experience.
-   **Selecting Techniques**: Choosing the right algorithms (simple vs. complex) for the specific requirements.
-   **Scope**: Defining the limits of AI for a specific game to avoid over-engineering.

### Genre-Specific Architectures
-   **Shooters (FPS/TPS)**:
    -   **Movement & Firing**: Tightly coupling steering behaviors with aiming and firing solutions.
    -   **Perception**: Robust sensory systems for detecting players (visual, auditory).
    -   **Tactical AI**: Heavy reliance on cover points, flanking, and squad coordination.
    -   **Melee Combat**: Managing distance, timing, and attack selection.
-   **Driving Games**:
    -   **Movement**: Physics-based steering, racing lines, and drift handling.
    -   **Pathfinding**: Navigating track geometry, overtaking logic, and avoiding collisions at high speeds.
    -   **Tactical AI**: Blocking opponents and drafting.
-   **Real-Time Strategy (RTS)**:
    -   **Pathfinding**: Efficiently handling pathfinding for hundreds of units (Flow Fields / Vector Fields).
    -   **Group Movement**: Formations and flocking to keep units organized.
    -   **Strategic AI**: High-level resource management, base building, and expansion logic.
    -   **MOBAs**: Specialized logic for lane pushing, creeping, and hero combat.
-   **Sports Games**:
    -   **Physics Prediction**: Accurate trajectory prediction for ball interception.
    -   **Playbooks**: Executing complex, pre-defined team strategies and set pieces.
    -   **Content Creation**: Tools for designers to create plays.
-   **Turn-Based Strategy**:
    -   **Timing**: Managing the flow of turns and animations.
    -   **Helping the Player**: AI that acts as a facilitator or teacher, not just an opponent.

### AI-Based Game Genres
Games where the AI *is* the gameplay.

-   **Teaching Characters**:
    -   **Representing Actions**: How the AI understands what it can do and what the player is doing.
    -   **Learning Mechanism**: Algorithms for adapting to player input (e.g., Black & White).
    -   **Predictable Mental Models**: Ensuring the player understands *why* the AI is learning or behaving a certain way.
-   **Flocking & Herding Games**:
    -   **Ecosystem Design**: Balancing predator/prey relationships and population dynamics (e.g., Pikmin).
    -   **Tuning Steering**: Adjusting parameters for satisfying, organic interaction.
    -   **Stability**: Ensuring flocking behaviors don't explode or degenerate.
