# Architecture Principles & Workflows

## Architecture Design Principles

In game logic design, the architectural design acts as the skeleton. A good architecture lays a solid foundation for game logic, making feature implementation more convenient and requirement changes more flexible.

The main principles are as follows:
- **Requirement-Centric**: Design the architecture based on specific requirements; satisfying requirements is the ultimate criterion.
- **Iterative Process**: Build the foundation in the initial iteration, and evolve the architecture with every subsequent iteration.
- **Clear Logic Isolation**: Control logic complexity within small scopes. Layer horizontally, modularize vertically, and keep class designs clear and independent.
- **Rational Paradigm Mixing**: Different paradigms and schemes usually have their own advantages; combine them in a mixed but unified form.
- **Reserve Space for Changes**: Leave enough room for requirement changes by identifying change points and abstracting them.
- **Adopt Test-Friendly Design**: Add architectural components that assist testing outside of requirements, making the architecture easy to test.

### Detailed Explanation

#### Requirement-Centric
As the implementation part of engineering, the most basic requirement of architecture is to meet the project's needs. Do not blindly pursue "advanced" or "perfect" architectures while ignoring suitability for the current project. The architecture needs to be modified and iterated based on the current project, deriving the architecture from requirements.

#### Iterative Process
Architectural design is an iterative process. It may involve multiple requirement analyses to repeatedly refine the design. Although iteration is important, the first design (from scratch) is crucial as it forms the foundation of the architecture.

#### Clear Logic Isolation
- **Module Decomposition**:
    - Horizontal Layering: Sink basic parts to lower layers and extract volatile parts to upper layers.
    - Vertical Partitioning: Cut modules based on functional independence.
- **Intra-Module Partitioning**:
    - Business Domain Simulation: Simulate the internal structure of the software as business domain content.
    - Business Process Implementation: Implement specific business processes on top of the business domain simulation.

#### Rational Paradigm Mixing
- **Object-Oriented Design**: Mainly used for business domain simulation. The core is to tightly combine logically related data and behaviors.
- **Data-Driven Design**: Mainly used for business domain simulation. The core is to aggregate data structures and separate corresponding behaviors into independent systems.
- **Process-Oriented Design**: Mainly used for business process implementation. The core is to arrange logic based on processes and events in the business.

**Design Choices**:
- Business Domain Simulation:
    - Complex Scenarios: Use Object-Oriented Design (Domain-Driven Design).
    - Simple/Performance/Network Requirements: Use Data-Driven Design.
- Business Process Implementation: Choose Process-Oriented Design (Event-Driven, Asynchronous Processes, etc.).

#### Reserve Space for Changes
A good architecture should leave enough space for requirement changes, maintaining certain architectural stability when changes occur. Use abstract interfaces and separation of implementation to abstract change points.

#### Adopt Test-Friendly Design
Try to leave space for testing in the design, including: logging, debugging, monitoring, unit test frameworks, mock components, GM cheat panels, etc.

## Core Design Workflows

Common workflows from requirement analysis to design:

1.  **Macro Design Flow**:
    *   Applicable to: Structural division, hierarchy, and basic modules.
    *   Flow: Feature List ---> Macro Architecture Design.

2.  **Domain Model Flow**:
    *   Paradigm: Object-Oriented Design.
    *   Applicable to: Core gameplay, scene systems, player data systems, complex logic modules.
    *   Flow: Domain Model Analysis + Use Cases ---> Domain-Driven Design.

3.  **Logic System Flow**:
    *   Paradigm: Data-Driven Design.
    *   Applicable to: Business modules (mainly data management and display).
    *   Flow: Structured Design Document + Use Cases + Interaction Flowcharts ---> Data-Driven Design.

4.  **Rapid Prototype Flow**:
    *   Applicable to: Gameplay prototypes.
    *   Flow: Use Cases + Interaction Flowcharts ---> Use-Case Driven Prototype Design.

These workflows are all iterative processes.