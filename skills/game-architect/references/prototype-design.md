# Use-Case Driven Prototype Design

Applicable to rapid prototype development (validating gameplay/technology), centered on use cases with rapid iteration.

## Introduction
- **Core**: Design is reverse-engineered completely from use cases.
- **Characteristics**: WYSIWYG, fast, weak initial architecture (requires refactoring).
- **Applicability**: Rapid validation, single person / small team development.

## Steps

### 1. Use Case Iteration Splitting
Split use cases into small, fast iterative steps (1-3 days/step).
- **Example**:
    - Iteration 1: Display Map.
    - Iteration 2: Character Movement.
    - Iteration 3: Enemy Spawning & Movement.
    - ...

### 2. Rapid Use-Case Oriented Development
- **Principle**: Implement in the fastest, most direct way.
- **Implementation**:
    - No complex design; can be written directly in controllers or unrelated classes.
    - Use fake data and temporary presentation.
    - **No Corner Cutting on Quality**: Functional effects themselves (e.g., game feel) need to be accurately implemented to verify gameplay.

### 3. Refactoring to Architecture
A crucial step to control chaos and introduce architecture.
- **Methods**:
    - **Duty Extraction**: Extract mixed duties into classes.
    - **Logic Decomposition**: Split complex classes.
    - **Base Class Extraction**: Extract base classes for similar concepts.
    - **Interface Extraction**: Isolate change points.
    - **Config Extraction**: Extract numerical values into configurations.

### Extension: Data-Driven Use-Case Development
- **Form**:
    1.  Treat game data structures as a unified Data Layer (Directly exposed).
    2.  Decompose use case functions into Logic Instructions (Functions), operating directly on the Data Layer.
    3.  Interface directly reads data for display.
- **Characteristics**: Skips encapsulation and class design, extremely fast implementation, but weak extensibility.

## Pros & Cons
- **Pros**: Rapid development, quick iteration, easy feedback.
- **Cons**: Unstable architecture, prone to deviation, not suitable for large teams / long-term formal projects (unless strictly refactored).