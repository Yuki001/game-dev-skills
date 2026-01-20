# Logic Optimization

This document outlines key strategies and patterns for optimizing game logic performance. Optimization should always be driven by data and measurements, focusing on bottlenecks that impact the user experience or target hardware constraints.

## 1. Find the Optimization Key Points

Before optimizing, identify *where* and *why* performance is low. "Premature optimization is the root of all evil."

### Profile & Measure
*   **Don't Guess, Measure:** Use profilers (Unity Profiler, Unreal Insights, RenderDoc, Superluminal, VTune) to pinpoint bottlenecks.
*   **Identify the Bottleneck Type:** Is it CPU-bound (Main Thread logic, Render Thread submission) or GPU-bound (Fill rate, Vertex processing)?
*   **Deep Dive:** Use Deep Profiling or instrumentation to measure specific function calls.

### In Real Situation (Hardware)
*   **Target Device Testing:** Always profile on the lowest-spec target device, not just the high-end development PC.
*   **Thermal Throttling:** Be aware that sustained high load causes mobile devices to heat up and throttle CPU/GPU speeds.
*   **Battery Consumption:** Optimization isn't just about FPS; it's also about energy efficiency (less CPU usage = longer battery life).

## 2. Cache & Pool (Memory & Allocation)

Minimizing memory allocation and garbage collection (GC) spikes is crucial for stable framerates.

### Object Pooling (For Creation)
*   **Reuse, Don't Recreate:** Instead of `Instantiate` and `Destroy`, keep a pool of deactivated objects. When needed, activate one; when done, deactivate and return to pool.
*   **Application:** Projectiles, particles, enemies, UI list items.
*   **Benefits:** Reduces memory fragmentation and GC overhead; avoids the heavy cost of initialization.

### Data & Component Caching
*   **Cache References:** Store references to components (e.g., `GetComponent`) in `Awake`/`Start` rather than fetching them every frame.
*   **Memoization:** Cache results of expensive pure functions (e.g., pathfinding results, complex math) if inputs haven't changed.

## 3. Fake Deactive/Active (For Deactivation)

The engine's native `SetActive(true/false)` or `GameObject.enabled` can be expensive due to hierarchy rebuilding and callback invocations (`OnEnable`/`OnDisable`).

### Lightweight Deactivation
*   **Visual Hiding:** Move the object far away (e.g., `y = -10000`) or set scale to `0`.
*   **Component Disabling:** Disable only the heavy components (Renderer, Collider, Animator) instead of the entire GameObject.
*   **Custom State:** Use a custom `bool isLogicActive` flag to skip logic updates without interacting with the engine's active state system.

## 4. Sort & Buffered Merge (For Batch Optimization)

Reducing the number of individual calls/draws by grouping similar operations.

### Batch Processing
*   **Data Locality:** Process arrays of data linearly rather than jumping between random memory addresses.
*   **Command Buffers:** Collect changes (e.g., network packets, UI events) and process them in a single pass at the end of the frame or tick.
*   **UI Batching:** Ensure UI elements share materials and atlases to reduce draw calls.

## 5. Frame Split & Queued & Time Limit Break (For Frame Time Limit)

Avoid "spikes" where a single frame takes too long (causing stutter) by spreading work over time.

### Time Slicing
*   **Budgeting:** Allocate a time budget (e.g., 2ms) per frame for a heavy task (e.g., pathfinding, loading). If the budget is exceeded, pause and resume in the next frame.
*   **Coroutines / Async:** Use coroutines or async/await to yield control back to the main loop periodically.
*   **Queue Processing:** Process a limited number of items from a queue per frame (e.g., instantiate only 5 enemies per frame).

## 6. Precalculate & Preload (Shift Workload)

Move heavy calculations from "critical time" (gameplay) to "insensitive time" (loading screens, install time).

### Precalculation
*   **Lookup Tables (LUT):** Pre-calculate complex math functions (trigonometry, recoil patterns, probability curves) into arrays.
*   **Baking:** Bake lighting, occlusion culling, and navigation meshes.

### Preloading
*   **Asset Streaming:** Load assets into memory *before* they appear on screen.
*   **Warmup:** Force execution of shaders or initialization of code paths during loading screens to avoid "first-time execution" hitches.

## 7. Multithread & Task (CPU Resource Optimization)

Utilize modern multi-core processors by moving logic off the main Unity/Unreal thread.

### Parallelism
*   **Worker Threads:** Offload independent logic (AI decision making, pathfinding, procedural generation) to background threads.
*   **Job Systems:** Use engine-specific job systems (e.g., Unity C# Job System) to safely run high-performance multithreaded code without race conditions.
*   **Synchronization:** Minimize locking; use double-buffering or message passing to communicate results back to the main thread.

## 8. Parallel Use GPU Shaders (CPU Logic Optimization)

The GPU is a massive parallel processor. Use it for more than just graphics.

### GPGPU & Compute Shaders
*   **Massive Simulation:** Move heavy parallel tasks like flocking behaviors, fluid dynamics, or particle physics to Compute Shaders.
*   **Texture Processing:** Perform image manipulation or terrain heightmap generation on the GPU.

## 9. AOI & LOD (Distance Optimization)

Don't spend resources on things the player can't perceive or are far away.

### LOD (Level of Detail)
*   **Graphics LOD:** Reduce polygon count and texture resolution for distant objects.
*   **Logic LOD:** Simplify AI behavior for distant enemies (e.g., switch from full behavior tree to simple movement). Stop animation updates for off-screen characters.

### AOI (Area of Interest)
*   **Network/Logic Culling:** Only sync network data or run logic for entities within a certain radius of the player.
*   **Hibernation:** Completely suspend logic for entities far outside the AOI until the player returns.

## 10. Timered Update & Separate FrameRate

Not everything needs to run at 60/120 FPS.

### Throttling Updates
*   **Interval Updates:** Run UI refreshes, AI target selection, or regeneration logic every $N$ seconds (e.g., 10Hz) instead of every frame.
*   **Time-Sliced Systems:** Distribute updates of a large manager (e.g., 1000 entities) so that only 1/10th of them update each frame (round-robin).

## 11. Space Partition & Broad-Phase Cull (Fast Rejection)

Quickly discard "impossible" interactions before doing expensive checks.

### Spatial Data Structures
*   **Grid / Spatial Hash:** Map objects to grid cells or hash map for constant-time $O(1)$ spatial lookups.
*   **Quadtrees / Octrees / BVH:** Organize objects in space. When querying "who is near me", check the tree nodes first to ignore vast swathes of the map.

### Frustum Culling
*   **Logic Culling:** If an object is not within the camera frustum, disable its visual logic (e.g., facial animation, particle emission).

## 12. Layered Mask & Group Cull

Use bitmasks and layers to filter interactions efficiently.

### Filtering
*   **Collision Matrix:** Configure the physics engine to ignore collisions between certain layers (e.g., "Debris" layer should not collide with "Debris").
*   **Event Filtering:** When broadcasting events, target specific groups/tags rather than iterating over all listeners.

## 13. Detail Clip/Split with Progressive Load

Handle massive worlds or datasets by breaking them down.

### Streaming & Proxies
*   **Chunking:** Split the world into chunks; load/unload based on player position.
*   **Proxy Objects:** Use lightweight data representations (structs) for objects not currently loaded. Only "hydrate" them into full GameObjects when necessary.
*   **Hierarchical Loading:** Load a low-res version of the terrain/building first, then progressively stream in higher details.

## 14. Algorithm Optimization

Better algorithms beat micro-optimizations.

### Complexity & Structures
*   **Big O Notation:** Reduce $O(N^2)$ nested loops to $O(N)$ or $O(N \log N)$ where possible.
*   **Data Structures:**
    *   Use `HashSets`/`Dictionaries` for $O(1)$ lookups instead of iterating `Lists` ($O(N)$).
    *   Use Arrays for fixed-size collections (better memory locality).
*   **Data-Oriented Design (DOD):** Organize data to maximize CPU cache hits (Struct of Arrays vs. Array of Structs).
