# Handling Requirement Changes

The embodiment of architectural robustness.

## Strategies

### 1. Isolation
High cohesion and low coupling module partitioning.
- **New System**: Developed independently, no mutual impact.
- **Modified Requirement**: Limited to a small scope.
- **Means**: Module management framework, reduce class dependencies (use ID/Copy), appropriate code duplication (decoupling).

### 2. Abstraction
Extraction at change points.
- **Data Changes**: Extract variables -> Config data -> Data folders (Diff replacement).
- **Process Changes**: Extract callback functions -> Strategy interfaces -> Template methods (Subclasses) -> Scripts.
- **Type Changes**: Abstract base classes/interfaces -> Member constraints (Dynamic languages) -> Standards (Art assets).
- **System Changes**: Abstract events (Inter-module), Abstract protocols (Inter-application).
- **Mixed Abstraction**: Combine multiple methods (e.g., Strategy Pattern + Config Table).

### 3. Composition
Preventive method. Subdivide functions and produce variants through composition.
- **Component Pattern**: Covers object diversity.
- **Strategy Composition**: Decompose complex logic into a composition of multiple strategy interfaces.

### 4. Refining
Delete useless code and shrink abstractions.
- **Criterion**: Try not to keep obsolete code (leave it to version control).
- **Shrinking**: When a change point no longer changes, remove unnecessary abstraction indirection layers.