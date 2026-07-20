---
name: oop-ddd-ai-coding-constraints
description: Enforce OOP and DDD engineering constraints for C# and TypeScript game development. Use when implementing, refactoring, reviewing, or verifying gameplay systems, domain-controlled engine-view wrappers, domain models, aggregates, application services, repositories, public APIs, or Context-based shared dependencies. Preserve encapsulation, avoid test-only production hooks, unit-test only engine-agnostic leaf logic, and verify integrated behavior by running the real engine.
---

# OOP + DDD Constraints for Game Development

Build C# and TypeScript game systems around encapsulated domain models and verifiable gameplay behavior.

## 1. General OOP/DDD Patterns

### Architecture Boundaries

Use the following responsibility split by default:

| Layer | Responsibilities | Must not own |
| --- | --- | --- |
| Interface | Input adapters, UI/presentation, engine callbacks, controllers, and server endpoints; translate input into use cases | Gameplay rules or direct persistence |
| Application | Gameplay use cases, commands, handlers, session/transaction boundaries, DTOs, and cross-object orchestration | Core gameplay rules |
| Domain | Combat, inventory, progression, quest, economy, and player-state models; Entities, Aggregates, Value Objects, Domain Services/Events, and ports | Raw engine APIs, native engine handles, network, database, or infrastructure details |
| Infrastructure | Engine adapters, save/persistence implementations, networking, platform SDKs, asset/resource access, physics/pathfinding adapters, clocks, random sources, and ID implementations | Gameplay rules |

Preserve this dependency direction:

```text
Interface -> Application -> Domain
Infrastructure -> Domain/Application ports
Domain -> no framework or infrastructure dependency
```

Do not:

- Let UI, input, an engine callback, or a Controller access a Repository directly or bypass Application to orchestrate a use case;
- Let Domain expose or directly operate raw engine components/nodes, scene graphs, rendering or physics APIs, networking, an ORM, database client, HTTP, or Infrastructure;
- Let an Entity invoke a Repository;

Follow a different layer structure when the existing project clearly defines one, while still preserving domain encapsulation.

### Domain Model and Encapsulation

#### Aggregates and Entities

- Let the Aggregate Root maintain its consistency boundary and business invariants.
- Change state through methods that express gameplay intent, such as `ApplyDamage`, `EquipItem`, `CompleteQuest`, or `GrantReward`.
- Keep fields, child-entity collections, domain-event collections, caches, and strategy objects private.
- Do not replace domain behavior with public setters or mutable collections.
- Return only stable Value Objects or read-only DTOs/snapshots; never return the internal collection itself.
- Preserve Entity identity and maintain valid state through behavior throughout its lifecycle.

#### Value Objects

- Keep them immutable;
- Validate at creation time;
- Compare them by value;
- Do not expose mutable internal data.

#### Repositories

- Define Repositories around Aggregate Roots;
- Persist and rehydrate Aggregates without exposing storage details;
- Let Application Services invoke Repositories.

#### Application Services

- Orchestrate use cases, transactions, Repositories, Domain objects, and external ports;
- Delegate core business decisions to the domain model;
- Return contract-level DTOs/results, not mutable internal object graphs.

### Public API Gate

Treat the public API as a stable product contract, not a testing toolbox.

Allow the public surface to express:

- Business capabilities and concrete classes required by real production callers;
- Stable commands, queries, results, DTOs, or snapshots;
- Approved interfaces for real production variants or strategies.

Do not let the public surface expose:

- Internal fields, mutable collections, caches, Repositories, or internal-only implementation types;
- Intermediate state used only for assertions;
- Test-only APIs or members.

Before adding or expanding a public API, answer:

1. Is there a real production caller?
2. Does it express a clear business capability rather than an implementation step?
3. Can the existing contract already complete the behavior?
4. Would it expose internal state or exist only for testing?

If the API exists only for testing convenience, refuse to add it and use an allowed verification method. Add only the minimal business contract required by a real production caller.

### Delivery Completeness

Do not deliver:

- `TODO`, `deferred`, `placeholder`, `stub`, or `not implemented` markers;
- Fake-success returns or swallowed failures;
- Disconnected modules intended to be integrated “later”;
- Horizontal class scaffolding with no runnable behavior.

## 2. Personal / Project-Specific Patterns

Treat this section as deliberate project constraints. When it conflicts with the general defaults above, follow this section—especially its View, Context, and interface rules.

### Game Development Boundaries

#### Separate Domain Semantics from Engine Semantics

- Do not equate an engine entity/component or ECS component with a DDD Entity, Aggregate, or Value Object. Assign DDD roles from identity, invariants, ownership, and lifecycle.
- Keep gameplay invariants in plain domain code. Let the View wrapper, frame callbacks, input handlers, animation events, RPC handlers, and scene scripts translate engine events into application commands or domain behavior.

#### Model Runtime Inputs and Engine Services

- Pass per-frame or per-command values such as `deltaTime`, input commands, target IDs, and ability requests as method/command inputs. Do not turn transient inputs into global Context state.
- Put time, random generation, physics queries, navigation, asset/resource lookup, networking, and platform services in the appropriate Context when gameplay outcomes depend on them. Reuse an existing production abstraction; do not create one for testing.

#### Persistence and Performance

- Rehydrate save data through factories or Aggregate behavior. Do not convert persistence DTOs into mutable domain models with public setters.
- Respect hot-path constraints without breaking encapsulation. Prefer ownership-safe operations, stable IDs, read-only views, or preallocated result buffers over exposing mutable collections.

#### Domain-Controlled View Wrapper

Use this pattern for scene and combat runtime Domain Objects. Do not apply it automatically to inventory, economy, save-data, or other non-visual Aggregates.

- Keep `Actor`, `Player`, `Enemy`, and similar runtime Domain Objects as plain classes instead of inheriting engine scene types.
- Let the Domain Object hold and drive a narrow concrete View wrapper when gameplay requires it. Keep the native node private inside the wrapper; do not create a View interface solely for testing.

Do not use the following structures; they are violations:

**Unity**:
```csharp
public class ActorController : MonoBehaviour {}
```

**Godot**:
```csharp
public partial class ActorNode : Node {}
```

Use the following structures:

**Unity**:
```csharp
public class Actor
{
    private ActorView _view = null;
    public Initialize() {
        // Create _view through an appropriate means, e.g. a factory
        _view = _context.ViewFactory.CreateActor(configID);
    }
}

public class ActorView
{
    private GameObject _node = null;

    void Initialize(string prefabPath);
    void SetPosition(WorldPosition position);
    void PlayAnimation(AnimationId animation);
    void Destroy();
    // Translate ActorView operations to the wrapped GameObject.
}
```

**Godot**:
```csharp
public class Actor
{
    private ActorView _view = null;
    public Initialize() {
        // Create _view through an appropriate means, e.g. a factory
        _view = _context.ViewFactory.CreateActor(configID);
    }
}

public class ActorView
{
    private Node _node = null;

    void Initialize(string prefabPath);
    void SetPosition(WorldPosition position);
    void PlayAnimation(AnimationId animation);
    void Destroy();
    // Translate ActorView operations to the wrapped Node.
}
```

- Express View operations in game terms such as position, facing, animation, visibility, or effects; never expose raw engine handles.
- Keep node lookup, component access, and presentation APIs in the wrapper. Any inherited Host must contain no domain state or gameplay rules.
- Let a scene bootstrap, factory, or composition root create and own the native node, wrapper, injection, spawn/despawn, and disposal sequence.
- Let the Domain Object drive the narrow View contract; route engine callbacks back through Application commands or explicit Domain methods.
- Do not expose or replace the wrapper or native node for tests.

### Context Pattern and Constructor Gate

Treat a Context as the strongly typed dependency collection and lifecycle owner for a stable scope. “Global” means shared inside that scope, not static or process-wide.

#### Context Boundaries

- Organize Contexts by a broad layer or game domain, such as `GameApplicationContext`, `CombatContext`, or `PlayerContext`.
- Create separate instances of the same Context type for different scenes, matches, rooms, or player sessions.
- Put a facility in the Context when multiple objects reuse it or its lifetime exceeds one object or invocation. Examples include Repositories, Services, Gateways, Clocks, random/ID generators, EventBus, physics/navigation queries, asset services, network gateways, configuration sources, and resource registries.
- Keep active Entities, current commands, per-frame state, and object-specific configuration outside the Context.
- Do not create a micro-Context for one Handler or merely to shorten one constructor.

#### Constructor Gate

Classify every constructor parameter:

1. **Global dependency**: Make it an explicit, strongly typed member of the relevant Context. Accept the Context in the constructor instead of accepting that dependency separately.
2. **Non-global dependency**: Allow it outside the Context only when it has identity, ownership, configuration, or a lifecycle specific to that object instance.
3. **Single-use-case input**: Prefer passing it to a public method or command. Do not retain it in a service constructor.

Treat these constructors as violations:

```text
Handler(context, repository, clock)       // repository and clock leaked outside the Context
Handler(repository, clock, eventBus)      // global dependencies were not consolidated
Handler(globalContextWithEverything)      // unbounded all-purpose Context
```

Prefer these shapes:

```text
Handler(playerContext)
BattleSession(combatContext, encounterSpec) // encounterSpec belongs only to this instance
```

If an extra parameter has no clear instance-specific meaning, move it into the appropriate Context. Pass one-time input to a method or command instead of retaining it in a constructor.

#### Context Design

- Implement a Context as a regular class with private system fields and public get-only properties.
- Let it own composition and ordered `Initialize`, `Update`, and `Destroy` for its scope. Allow an empty constructor or stable scope configuration.
- Forbid `Get<T>()`, string keys, dictionary lookup, and runtime registration. Keep dependencies visible as strongly typed members.
- Do not store active Entities, commands, arbitrary gameplay data, or use-case logic in the Context.
- Do not expose a database client, HTTP client, raw engine object, or another Infrastructure implementation through a Domain Context.
- Do not create a system-wide `AppContext` or `GlobalContext`. Split an oversized Context by domain, layer, or lifecycle.

Create a dedicated use-case Context only when the use case has a stable lifecycle, transaction, security, isolation, or resource boundary that cannot fit an existing broad Context without real cross-layer or cross-domain contamination. Otherwise, use the enclosing Context; shortening one constructor is not sufficient justification.

TypeScript example:

```ts
export class SceneContext {
  #random!: RandomService;
  #collision!: CollisionSystem;
  #pool!: ObjectPool;

  get random(): RandomService { return this.#random; }
  get collision(): CollisionSystem { return this.#collision; }
  get pool(): ObjectPool { return this.#pool; }

  initialize(): void {
    this.#random = new RandomService();
    this.#pool = new ObjectPool();
    this.#collision = new CollisionSystem(this.#random, this.#pool);
  }

  update(deltaTime: number): void {
    this.#collision.update(deltaTime);
    this.#pool.update(deltaTime);
  }

  destroy(): void {
    this.#collision.destroy();
    this.#pool.destroy();
    this.#random.destroy();
  }
}
```

C# example:

```csharp
public sealed class SceneContext
{
    private RandomService _random = null!;
    private CollisionSystem _collision = null!;
    private ObjectPool _pool = null!;

    public RandomService Random => _random;
    public CollisionSystem Collision => _collision;
    public ObjectPool Pool => _pool;

    public void Initialize()
    {
        _random = new RandomService();
        _pool = new ObjectPool();
        _collision = new CollisionSystem(_random, _pool);
    }

    public void Update(float deltaTime)
    {
        _collision.Update(deltaTime);
        _pool.Update(deltaTime);
    }

    public void Destroy()
    {
        _collision.Destroy();
        _pool.Destroy();
        _random.Destroy();
    }
}
```

### Interfaces Only for Real Production Variants

Add an interface, port, or provider ONLY when the product genuinely requires multiple production implementations. For a single implementation, use the concrete class directly. Future flexibility and testability are not sufficient reasons. Add a delegate only for a real production callback or event, never to mirror a class for tests.

- Ask: "Will this type have ≥2 real production variants?" If no → concrete class.
- Pass a working directory, ID, path, threshold, or other stable configuration directly as a value or Value Object. Do not wrap it in a Provider or zero-argument function.
- If a unit test requires a replaceable abstraction that has no real production variant, do not write that unit test.
- Never introduce an unauthorized interface, port, delegate, or provider.

### Language-Specific Checks

#### TypeScript

- Prefer ECMAScript `#private` or the project's established `private` convention;
- Use `Readonly` and read-only collections for external DTOs;
- Export only contracts from a public barrel; do not export internal implementations or private Domain types;
- Keep engine/runtime objects out of public domain contracts; adapt them at module boundaries.

#### C#

- Use private fields and controlled `private set` access for domain state;
- Use `[SerializeField] private` for editor wiring when supported; do not make gameplay state public merely for Inspector access.

## 3. Testing and Verification

### Automated Tests: Leaf Units Only

Do not use TDD or test-first development. Implement the behavior first. Automated tests are allowed afterward only for deterministic, engine-agnostic leaf logic with no Context wiring, View, native node, visual behavior, or engine lifecycle. Examples include value objects, formulas, schedulers, counters, and small collection or math utilities.

- Test through the unit's existing public behavior.
- Do not access private state, widen visibility, use reflection, `InternalsVisibleTo`, `as any`, property descriptors, or internal collection assertions.
- Do not add `ForTest`/`TestOnly` members, an interface, delegate, provider, proxy, observer, setter, hook, reset method, fake, or second entry point for testing.
- Do not replace a class with a delegate or interface that mirrors its methods merely to proxy all behavior in tests.
- Do not change production architecture to make a non-leaf concern unit-testable.
- Do not modify existing expected results without explicit user authorization. If a test appears wrong or conflicts with the product behavior, report the conflict instead of rewriting the test.

### No Automated Integration Tests

Do not create automated integration, acceptance, end-to-end, headless-engine, scene, or visual-regression tests. Integration is a verification category in this skill, not test code.

Contexts, Bootstrap, GameFlow, View wrappers, native nodes, scene assembly, resource loading, animation, effects, UI, bone sockets, engine lifecycle, and multi-system wiring must be verified by running the real game entry point in the real engine. Use the rendered result, interaction, screenshots or video, scene-tree inspection, debug drawing, runtime state, and engine logs as appropriate.

Do not fake visual or node-bearing types. Do not create a test runner, test scene, test-only Context, test fixture, or injectable replacement to automate integration behavior.
