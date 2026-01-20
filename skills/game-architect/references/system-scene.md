# Scene, Spatial, and Actor Systems

This reference covers the organization of game objects (actors) and the spatial structures used to manage them, which are fundamental for core gameplay and combat systems.

## 1. Scene Object Frameworks

How to structure and organize game objects (Actors).

### A. Inheritance Tree
- **Concept**: organizing objects in a deep class hierarchy.
- **Example**: `Object -> SceneObject -> Actor -> Character -> Player`.
- **Pros**: Natural concept mapping, easy code reuse.
- **Cons**: Rigid hierarchy, "God classes" with too many responsibilities, hard to refactor.

### B. Aggregate Parts
- **Concept**: Flatten the hierarchy and use a list of sub-objects (parts) to handle logic.
- **Structure**: An `Actor` class contains a list of parts like `ActorCollision`, `ActorMovement`, `ActorStates`.
- **Pros**: Retains domain concepts (Actor class) while offering compositional flexibility. Good for complex characters in games with fewer total objects (e.g., SRPGs).

### C. Entity-Component (EC)
- **Concept**: `Entity` is just an ID or container; `Components` hold data and logic.
- **Structure**: An entity is composed of components like `Transform`, `Mesh`, `Script`. Prefabs define templates.
- **Glue Component**: To restore domain concepts lost in pure composition, a "Controller" component (e.g., `PlayerController`) acts as the interface for the entity.
- **Pros**: Highly flexible, industry standard (Unity, Cocos).

### D. Entity-Component-System (ECS)
- **Concept**: Data-oriented design. `Entity` is an ID, `Component` is pure data, `System` is pure logic.
- **Structure**:
    - **Components**: Structs (e.g., `Position`, `Velocity`).
    - **Systems**: Iterate over entities with specific component sets to apply logic (e.g., `MovementSystem`).
    - **Tags**: Empty components used as flags.
- **Pros**: Extreme performance (cache locality), easier network synchronization.
- **Cons**: High complexity, boilerplate code.

## 2. Object Creation

### Config Data & Templates
- **Template**: Defines the Type + Initial Data.
- **Implementation**: JSON/XML/Excel defines object stats or component lists. Factory creates instances based on these templates.

### Serialization & Cloning
- **Serialization**: Saving object trees to files and restoring them (e.g., Prefabs, Save files).
- **Cloning**: Duplicating an existing runtime object (Prototype pattern).

## 3. Scene Management

Managing the lifecycle and organization of objects in the world.

### Logic Structure
- **Scene Tree**: Standard parent-child hierarchy based on transform.
- **Categorized Lists**: Lists by type (e.g., `List<Enemy>`, `List<Bullet>`) for easy logic access.
- **Render Layers**: Sorting by rendering order (Background, Map, Actor, UI).

### Spatial Structure
Used for spatial queries (collision, visibility) alongside the logic structure.
- **Grid**:
    - Divides space into uniform cells.
    - Good for: Fast coarse culling, Tilemaps, 2D games.
- **Spatial Hash**:
    - Hash map of grid cells.
    - Good for: Sparse scenes with infinite bounds.
- **Partition Trees (QuadTree / Octree)**:
    - Recursively divides space.
    - Good for: Variable object sizes, general 3D scenes.
    - Variants: Dynamic split, Loose QuadTree (overlapping boundaries).
- **Graph / Node**:
    - Connected nodes representing areas (e.g., Rooms, Provinces).
    - Good for: Strategy games, non-euclidean maps.

## 4. Scene Loading Strategies

- **Additive Loading**: Base scene + Layered additions (Lights, Dynamics, Logic).
- **Chunking**: Grid-based automatic loading/unloading based on player position.
- **Streaming**: Logic-based loading (e.g., loading "Dungeon_A" when entering a volume).
- **Spawners**: Triggers that spawn objects/enemies when the player approaches, used for dynamic entities.
- **Boundary Issues**: Handling lighting and navigation mesh stitching between chunks is critical.
