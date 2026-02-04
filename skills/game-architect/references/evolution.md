# Handling Requirement Changes

The embodiment of architectural robustness.

## Strategies

### 1. Isolation
High cohesion and low coupling module partitioning. This is the key to handling both new additions and modifications.

#### Module Partitioning
- **Independent Development**: By strictly isolating modules, new systems can be developed without affecting existing code. This enables parallel development in teams.
- **Scope Containment**: Modifications are confined to specific modules, preventing bugs from rippling through the entire system.

#### Implementation Techniques
- **Module Management Framework**: Use a dedicated framework to manage module lifecycles. Modules should interact primarily through an event system or restricted interfaces, not direct deep linking.
- **Reduce Class Dependencies**:
    - Avoid holding direct references to objects in other modules.
    - **Use IDs**: Reference objects by unique IDs (int/string). Look them up only when necessary.
    - **Use Data Copies**: Pass copies of data (DTOs) instead of references to live objects. This prevents external code from accidentally modifying internal state.
- **Appropriate Code Duplication**: Do not rush to extract "common code" if the logic belongs to different contexts. It is better to duplicate code in separate modules than to couple them to a shared utility that changes for one but breaks the other.

### 2. Abstraction
Extraction at change points.

#### Data Changes
When the logic remains the same but the data it operates on changes.
- **Extract variables**: Abstract specific values (numbers, strings) into variables. Like an equation using $x$ instead of a number, the program reads these variables from outside, allowing changes without modifying logic code.
- **Extract Config data**: Organize variables and constants into structured configuration objects (e.g., structs, classes). These are populated from external sources like code constants or configuration files (JSON, XML, Excel), enabling easy tweaking.
- **Extract Data folders**: Used for large-scale data or resource replacements (e.g., Localization). Establish a mechanism to load files based on a directory path variable. By changing the path (e.g., from `en/` to `jp/`), the system loads different sets of files with the same names, replacing the content entirely.

#### Process Changes
When the flow of execution or the logic itself needs to vary.
- **Extract callback functions**: Abstract specific operations at certain points in the logic into callback functions (or delegates/function objects). Assigning different functions changes the behavior at those points without altering the main flow.
- **Abstract Strategy interfaces**: When multiple related behaviors need to change together, gather them into an interface (Strategy Pattern). Implement different strategies as classes. The context switches behavior by using a different strategy instance.
- **Extract Template methods**: In an inheritance hierarchy, define the skeleton of an algorithm in a base class but let subclasses override specific steps (Template Method Pattern). This allows variations in sub-steps while preserving the overall structure.
- **Extract Scripts**: Move complex or frequently changing logic into external scripts (Lua, Python, custom DSL). The core engine calls these scripts. This acts like a flexible, hot-reloadable version of callback functions, ideal for rapid iteration.

#### Type Changes
When the type of objects being processed needs to vary.
- **Abstract base classes/interfaces**: (OOP) Define common behaviors in an abstract base class or interface. Client code depends on this abstraction. New types are added by creating subclasses, without modifying the client code.
- **Abstract Member constraints**: (Dynamic Languages) Instead of strict types, rely on the presence of specific methods or properties (Duck Typing). Any object satisfying these constraints (contracts) can be used, allowing for flexible type substitution.
- **Abstract Standards (Art assets)**: Establish logical specifications for assets (e.g., "All character models must have a 'Head' bone", "Attack animations must trigger 'Hit' events"). Code is written against these standards, not specific assets, allowing art assets to be replaced freely as long as they comply.

#### System Changes
When external systems or modules interact and might change.
- **Abstract events**: (Inter-module) Decouple modules using a global event system. One module publishes events without knowing who listens; others subscribe without knowing the publisher. This isolates modules from changes in each other.
- **Abstract protocols**: (Inter-application, e.g., Client-Server) Define interaction via strict data formats (Network Packets, RPC interfaces). As long as the protocol remains consistent, the internal implementation or deployment of the communicating applications can change independently.

#### Mixed Abstraction
- **Combine multiple methods**: Use a combination of abstraction techniques to handle complex changes. For example, use a **Strategy Pattern** to handle major behavioral differences (Process Change), while using **Config Tables** within those strategies to handle numerical variations (Data Change). This applies the right level of abstraction to each aspect of the problem.

### 3. Composition
A preventive strategy. Instead of predicting every specific change, subdivide functionality into small, reusable parts. New requirements are met by recombining these parts rather than writing new code.

#### Component Pattern
- **Granularity**: Break down complex entities (like a generic `GameObject`) into fine-grained components (e.g., `Position`, `Render`, `Collider`).
- **Orthogonality**: Ensure components are independent. A `Render` component shouldn't depend on a `AI` component.
- **Variant Generation**: Create vast amounts of object variations simply by attaching different combinations of components. This covers the "explosion of types" problem often seen in game entities.

#### Strategy Composition
- **Decomposition**: If a single class is becoming too complex with many "if-else" or "switch" statements for different behaviors, break it down.
- **Interface Segregation**: Identify distinct behavioral aspects (e.g., `IMovement`, `IAttack`, `IDisplay`).
- **Combinatorial Logic**: The main class holds references to these interfaces. By assigning different implementations to each interface, you create specific behaviors through combination. (e.g., A monster that `Flies` (Movement) and `Shoots` (Attack)).

### 4. Refining
The cleanup phase. Architecture tends to rot over time as requirements change. Refining brings it back to a healthy state.

#### Delete Useless Code
- **Zero Tolerance for Waste**: Remove functions, classes, and data files that are no longer used.
- **No Commented-out Code**: Do not comment out old code "just in case". It clutters the codebase and increases mental load. Rely on Version Control Systems (Git) to retrieve history if needed.

#### Shrink Abstractions
- **Remove Indirection**: Abstraction adds complexity (indirection). If a previously anticipated "change point" turns out to be stable (it never changed, or only has one implementation left), remove the abstraction.
- **Direct Implementation**: Replace the interface/factory pattern with direct class usage. Simpler code is easier to maintain. Only abstract when there is a proven need for variation.