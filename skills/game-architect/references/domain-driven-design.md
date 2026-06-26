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

### Managing Dependencies on Global Objects
Repositories and services are often module-wide shared facilities. Choose one access pattern deliberately:

- **Singleton**: Each global object exposes its own instance, e.g. `ActorRepository.Instance`. Simple and direct, but dependencies are implicit and scattered.
- **Service Locator**: A central global registry resolves repositories/services, e.g. `ServiceLocator.Get<ActorRepository>()`. Keywords: global registry, generic lookup, implicit dependency.
- **Context**: Group and scope dependencies into multiple typed context objects by domain boundary, architecture layer, or runtime instance, e.g. `sceneContext.ActorRepository` or `playerContext.ItemRepository`. `sceneContext` is an object passed into other objects as a dependency. Keywords: multiple contexts, bounded context, scoped boundary, typed access, dependency passing, multi-instance isolation.
- **Dependency Injection (DI)**: Dependencies are provided from outside through constructors/fields/properties. Keywords: explicit dependency graph, inversion of control, testability, composition root.

> Use **Bounded Context** and **Layered Architecture** as the main decomposition guides for Context. Bounded Context splits dependencies by domain boundary; Layered Architecture splits dependencies by architectural layer such as infrastructure, domain, and application.

## Summary
Derive the initial version of class design from the Domain Model Diagram using the patterns above.