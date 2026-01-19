# Domain-Driven Design (DDD)

Applicable to core gameplay, scene systems, player data systems, and complex logic modules.

## Core Concepts
Transform domain models from high-level model layers into actual class designs through a series of patterns.

### Model Construction (Building Blocks)

#### Entity
- **Definition**: A logical object with a unique identity, high cohesion.
- **Usage**: Corresponds to domain concept nouns (e.g., Player, Enemy, Item).
- **Design**: Contains attributes (data) and methods (operations).
- **ID**: Very important, used for unique identification, weak references, and persistence indexing.
- **Patterns**: Can use Inheritance (Classification Tree) and Composition (Component Pattern).

#### Value Object
- **Definition**: No uniqueness, describes values of domain concepts (e.g., Vector, Color, Damage).
- **Characteristics**: Usually immutable (modified by replacing the whole).
- **Methods**: Creational (Static Factory), Computational (Return new value).

#### Service
- **Definition**: Encapsulates domain logic that does not fit into Entities or Value Objects.
- **Usage**: Multi-entity coordination logic (Double Dispatch), complex process logic (Save, Pathfinding).
- **Characteristics**: Generally stateless.

#### Module
- **Definition**: A way to separate similar logic together (Namespace/Package/Directory).
- **Principle**: High Cohesion, Low Coupling.

### Lifecycle Management

#### Aggregate
- **Definition**: A composition of entities, where an "Aggregate Root" wraps partial entities.
- **Rules**:
    - External objects can only reference the Aggregate Root.
    - The Aggregate Root maintains internal consistency.
    - Internal entities referencing each other should be cautious; prefer using IDs to reference other Aggregate Roots.
- **Difference**: Unlike the Composite pattern, Aggregate emphasizes cohesion and consistency, while Composite emphasizes structure and traversal.

#### Factory
- **Definition**: Extracts the process of creating Entities or Value Objects.
- **Forms**: Constructor, Factory Method, Factory Class, Builder.
- **Usage**: Encapsulates complex creation logic (especially for Aggregate Entities).

#### Repository
- **Definition**: Manages the lifecycle of domain entity objects (Management, Access, Query).
- **Collection Concept**: Provides interfaces similar to collections (add, remove, get).
- **Query**: Supports ID query, attribute query, domain logic optimized query (e.g., spatial index).
- **Scope**: Usually only provides repositories for Aggregate Roots.

### Application Layer
- **Definition**: Handles actual business logic, driven by Use Cases.
- **Characteristics**: Thin, no business rules, no business state, responsible for coordination and delegation.
- **Patterns**:
    - **Application Service**: Core, driven by Use Cases, combines implementation of similar use cases.
    - **Facade Pattern**: Wrapper for module external interfaces.
    - **Command Pattern**: Encapsulates user requests.

## Summary
Derive the initial version of class design from the Domain Model Diagram using the patterns above.