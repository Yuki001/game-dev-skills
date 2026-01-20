# Algorithm & Data Structures

This document provides a reference for selecting and implementing algorithms in game development. It covers generic problem-solving strategies, specialized search techniques, physics calculations, and essential data structures.

## 1. Generic Problem Solver

Strategies for solving various logic problems, from procedural generation to resource optimization.

### Recursive Divide & Merge (Divide and Conquer)
*   **Concept:** Break a complex problem into smaller sub-problems, solve them, and combine the results.
*   **Game Application:** 
    *   **Procedural Terrain:** Diamond-Square algorithm or Quadtree-based terrain generation.
    *   **Space Partitioning:** Building BSP trees or Octrees for scene management.

### Search
*   **Concept:** Systematically exploring a state space to find a goal state.
*   **Game Application:** AI decision making, puzzle solving, path planning.

### Dynamic Programming (DP)
*   **Concept:** Solving complex problems by breaking them down into simpler sub-problems and storing their solutions to avoid re-computing.
*   **Game Application:** 
    *   **Resource Management:** Knapsack-style inventory optimization.
    *   **Sequence Matching:** Levenshtein distance for fuzzy string matching (e.g., cheat codes, text input).

### Iterative Methods
*   **Concept:** Starting with an approximation and iteratively refining it.
*   **Game Application:** 
    *   **Physics Constraints:** Position Based Dynamics (PBD) solvers (e.g., cloth simulation, inverse kinematics).
    *   **Procedural Placement:** Cellular Automata for cave generation.

### Greedy Algorithms
*   **Concept:** Making the locally optimal choice at each step with the hope of finding a global optimum.
*   **Game Application:** 
    *   **NavMesh Generation:** Simplified triangulation.
    *   **LOD Selection:** Choosing the best mesh detail level based on current budget.

### Math Models & Formulas
*   **Concept:** Using direct mathematical derivation instead of simulation.
*   **Game Application:** 
    *   **Ballistics:** Calculating projectile trajectory without frame-by-frame simulation.
    *   **Steering Behaviors:** Boids algorithm (Separation, Alignment, Cohesion).

## 2. Search & Pathfinding

The core of movement and decision making in games.

### Traversal Strategies
*   **Depth-First Search (DFS):** Explores as far as possible along each branch before backtracking. Useful for maze generation.
*   **Breadth-First Search (BFS):** Explores neighbor nodes first. Guarantee shortest path in unweighted graphs. Useful for flood-fill logic (e.g., "area of effect" calculation).

### Precalculation & Caching
*   **Results Save To File:** Bake static paths or navigation data (NavMesh) during build time.
*   **Results Save To Runtime Cache:** Store calculated paths for frequently traveling agents.
*   **Sub-Problem Runtime Cache (Memoization):** Cache parts of a path or decision tree (e.g., flow fields) to be shared among multiple agents.

### Priority Search
*   **Dijkstra's Algorithm:** Finds shortest path in weighted graphs.

### Pathfinding Implementations
*   **Graph / Waypoints:** Good for simple or linear levels. Agents move between predefined nodes.
*   **A* (A-Star):** The gold standard for game pathfinding. Uses a heuristic (estimated distance to goal) to guide the search, minimizing nodes visited.
*   **Grid Optimization:**
    *   **JPS (Jump Point Search):** Optimization for uniform cost grids (no terrain costs). Skips intermediate nodes to speed up A*.
    *   **Flow Fields:** efficient for hundreds of units moving to the same target.
*   **NavMesh (Navigation Mesh):** The standard for modern 3D games. Represents walkable surfaces as convex polygons.
*   **Continuous Space:**
    *   **RRT (Rapidly-exploring Random Tree):** Good for high-dimensional spaces or robotic arms (IK).
    *   **D* / D* Lite:** For dynamic environments where obstacles appear/disappear, allowing path replanning without full re-computation.

### Obstacle Avoidance & Steering
*   **Steering Behaviors (Reynolds):** Basic behaviors like Seek, Flee, Arrival, and Wander. Combined via weighted sums for complex movement.
*   **Velocity Obstacles (VO):** Geometric approach to avoid moving obstacles by calculating "forbidden" velocities that would lead to collision.
*   **RVO / ORCA (RVO2 Library):**
    *   **Reciprocal Velocity Obstacles (RVO):** Extends VO to handle multi-agent scenarios where agents share responsibility for avoidance.
    *   **Optimal Reciprocal Collision Avoidance (ORCA):** A mathematically robust formulation (using linear programming) to find the closest velocity to the agent's preferred velocity that is guaranteed to be collision-free.
    *   **Application:** Massive crowd simulation (e.g., RTS games, city simulations) where agents move smoothly without "jittering" when meeting head-on.
*   **Dynamic Window Approach (DWA):** Samples possible velocities based on robot/agent physical constraints and chooses the one that maximizes progress toward the goal while avoiding obstacles.

### Game AI Search (Adversarial Search)
*   **MinMax:** Used in turn-based games (Chess, Tic-Tac-Toe). Minimizes the possible loss for a worst-case scenario.
*   **Alpha-Beta Pruning:** Optimization for MinMax to stop evaluating move branches that are guaranteed to be worse than already examined moves.
*   **Monte-Carlo Tree Search (MCTS):** Used when the search space is too vast (e.g., Go, complex strategy games). Uses random sampling to estimate the value of moves.

## 3. Physics & Spatial Queries

Algorithms for detecting interactions in virtual space.

### Collision Detection Pipeline
*   **Broad Phase (Space Culling):** Quickly discard pairs of objects that are definitely *not* colliding.
    *   **Sweep and Prune:** Sorts objects along an axis to find overlaps.
    *   **Grid and Spatial Hashing:** Divides space into cells and checks only objects in the same cell.
    *   **BVH (Bounding Volume Hierarchies):** Dynamic trees of bounding boxes.
*   **Narrow Phase:** Detailed intersection tests.
    *   **Bounding:** Check simple shapes (AABB, Sphere, Capsule) before checking complex meshes.
    *   **Detailed (Optional):** (GJK algorithm for convex shapes, SAT for separating axis theorem).

### Raycast Query
*   **Grid Traversal:** DDA (Digital Differential Analyzer) or Bresenham's line algorithm for fast grid raycasting (Minecraft style).
*   **Spatial Acceleration:** Use Grid, Octrees or BVH to avoid testing the ray against every triangle in the scene.

## 4. Data Structures

Specialized structures for game performance.

### Trie (Prefix Tree)
*   **Concept:** A tree data structure used for locating specific keys from within a set.
*   **Game Application:**
    *   **String Matching:** Fast autocomplete, spell checking, or command console processing.
    *   **Dictionary Compression:** Efficient storage of large word lists.
    *   **Input Sequences:** Matching combo sequences in fighting games (e.g., "Down, Right, Punch").

### Graphs
*   **Concept:** A collection of nodes (vertices) and edges connecting them. Can be directed/undirected and weighted/unweighted.
*   **Representations:**
    *   **Adjacency List:** An array of lists. Space-efficient for sparse graphs (most game maps). Fast for finding neighbors.
    *   **Adjacency Matrix:** A 2D array. Fast ($O(1)$) to check if an edge exists between two nodes. Memory-heavy for large maps.
*   **Game Application:**
    *   **Waypoints & Navigational Graphs:** Nodes represent positions, edges represent paths.
    *   **Dialogue Trees:** Directed graphs where nodes are lines of dialogue and edges are player choices.
    *   **Tech Trees / Skill Trees:** Representing dependencies and progression.
    *   **Quest Dependency Graphs:** Managing complex quest lines and prerequisite conditions.

### Spatial Structures (Reference)
*   **Spatial Hash:** Mapping 3D positions to 1D hash keys for fast localized lookups without tree overhead.
*   **Quadtree / Octree:** Recursive subdivision of space.
*   **Kd-Tree:** Binary space partitioning for static point cloud lookups (e.g., photon mapping, nearest neighbor search).

