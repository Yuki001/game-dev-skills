---
name: oop-ddd-ai-coding-constraints
description: Enforce OOP and DDD engineering constraints for C# and TypeScript game development. Use when implementing, refactoring, reviewing, or testing gameplay systems, combat, inventory, progression, quests, scenes, matches, player data, save/load flows, domain-controlled engine-view wrappers, domain models, aggregates, application services, repositories, vertical slices, public APIs, Context-based shared dependencies, or deterministic test seams. Preserve encapsulation, keep engine details outside Domain, avoid test-only production hooks, and deliver complete game behavior through public contracts.
---

# OOP + DDD Constraints for Game Development

Build C# and TypeScript game systems around encapsulated domain models and verifiable gameplay behavior. Do not enlarge the public surface, expose runtime state, couple Domain to engine objects, or bypass architectural layers for local implementation or testing convenience.

## Execution Order

For every implementation, refactoring, or testing task, proceed in this order:

1. **Identify the contract**: Confirm the player or designer-facing behavior, existing public API, module boundaries, domain invariants, engine constraints, and project conventions.
2. **Choose a vertical slice**: Reduce the task to the smallest gameplay behavior that can run from a real entry point—input, command, engine callback, or server request—and produce an observable game result.
3. **Design the boundaries**: Put business rules in Domain, use-case orchestration in Application, external dependencies behind formal ports, and scope-wide shared dependencies in typed Contexts.
4. **Complete the path**: Connect the entry point, application service, domain model, ports, and infrastructure implementations without leaving disconnected modules.
5. **Test through the contract**: Arrange state, invoke behavior, and assert business outcomes through a public boundary.
6. **Audit encapsulation**: Check the public surface, test seams, cross-layer dependencies, and incomplete markers before delivery.

Resolve conflicts in this order:

1. Explicit user requirements and approved public contracts;
2. Domain invariants and encapsulation;
3. Existing project architecture and naming conventions;
4. The defaults in this skill.

Do not use “following DDD” as a reason to rewrite an architecture the user has already chosen. When an existing design conflicts with these constraints, explain the exact conflict and its impact, and modify only what the task authorizes.

## Architecture Boundaries

Use the following responsibility split by default:

| Layer | Responsibilities | Must not own |
| --- | --- | --- |
| Interface | Input adapters, UI/presentation, engine callbacks, controllers, and server endpoints; translate input into use cases | Gameplay rules or direct persistence |
| Application | Gameplay use cases, commands, handlers, session/transaction boundaries, DTOs, and cross-object orchestration | Core gameplay rules |
| Domain | Combat, inventory, progression, quest, economy, and player-state models; Entities, Aggregates, Value Objects, Domain Services/Events, and ports | Engine, rendering, scene graph, network, database, or infrastructure details |
| Infrastructure | Engine adapters, save/persistence implementations, networking, platform SDKs, asset/resource access, physics/pathfinding adapters, clocks, random sources, and ID implementations | Gameplay rules |

Preserve this dependency direction:

```text
Interface -> Application -> Domain
Infrastructure -> Domain/Application ports
Domain -> no framework or infrastructure dependency
```

Do not:

- Let UI, input, an engine callback, or a Controller access a Repository directly or bypass Application to orchestrate a use case;
- Let Domain depend on engine components/nodes, scene graphs, rendering, physics APIs, networking, an ORM, database client, HTTP, or Infrastructure;
- Let an Entity invoke a Repository;
- Let tests bypass public boundaries to access internal implementations.

Follow a different layer structure only when the existing project clearly defines one, while still preserving dependency direction and domain encapsulation.

## Game Development Boundaries

### Separate Domain Semantics from Engine Semantics

- Do not equate an engine entity/component or ECS component with a DDD Entity, Aggregate, or Value Object. Assign DDD roles from identity, invariants, ownership, and lifecycle.
- Keep gameplay invariants in plain domain code. Let the View wrapper, frame callbacks, input handlers, animation events, RPC handlers, and scene scripts translate engine events into application commands or domain behavior.

### Model Runtime Inputs and Engine Services

- Pass per-frame or per-command values such as `deltaTime`, input commands, target IDs, and ability requests as method/command inputs. Do not turn transient inputs into global Context state.
- Put time, random generation, physics queries, navigation, asset/resource lookup, networking, and platform services behind Context members or formal ports when gameplay outcomes depend on them. Supply deterministic implementations in tests.

### Scope State, Lifetime, and Performance

- Scope runtime Context instances to meaningful lifetimes such as game process, world, scene, match/session, or player profile. Keep parallel scenes, matches, server rooms, and simulations isolated.
- Keep mutable scene objects, active Entities, current commands, and per-frame state out of dependency Contexts. Contexts carry facilities; domain objects own gameplay state.
- Rehydrate save data through factories or Aggregate behavior. Do not convert persistence DTOs into mutable domain models with public setters.
- Respect hot-path constraints without breaking encapsulation. Prefer ownership-safe operations, stable IDs, read-only views, or preallocated result buffers over exposing mutable collections.

### Domain-Controlled View Wrapper

Prefer the Domain Object as the primary object instead of following the structure prescribed by the engine's scene framework:

- Keep `Actor`, `Player`, `Enemy`, and other Domain Objects as plain classes instead of inheriting engine scene types.
- Use an engine-agnostic View contract and a plain-class wrapper with a private native node. If the engine requires inheritance, keep a separate minimal Host that forwards callbacks to Application and presentation to the wrapper.

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
- Do not expose the wrapper or native node for tests. Use a formal fake View only for production-visible View behavior.

## Context Pattern and Constructor Gate

Use Context objects to consolidate dependencies shared across an architectural layer, a broad domain boundary, or a runtime instance. A “global dependency” means a facility shared within a scope; it does not have to be a process-wide singleton.

Choose stable, coarse-grained Context boundaries by default:

1. Organize by broad architectural layer, such as `GameApplicationContext` or `GameInfrastructureContext`;
2. Organize by a broad domain or Bounded Context, such as `CombatContext`, `PlayerContext`, or `EconomyContext`;
3. When multi-instance isolation is required, create separate runtime instances of the same broad Context type instead of defining a new type for every use case.

Do not create micro-Contexts such as `ResolveCombatTurnContext` or `GrantRewardContext` merely because one Handler uses only a subset of the available dependencies. A Context boundary must reflect a stable architectural or game-domain boundary, not the current parameter list of one caller.

### Identify Global Dependencies

Treat a dependency as global within its scope and place it in a Context when any of the following applies:

- Multiple objects or use cases in the same scope reuse it;
- Its lifetime usually exceeds that of one business object or one invocation;
- It represents a shared Repository, Application/Domain Service, Gateway, Clock, random/ID generator, EventBus, physics/navigation query, asset service, network gateway, configuration source, resource registry, or similar facility;
- Tests, runtime instances, or scenes need to replace or isolate it as part of a group.

Do not equate “global” with “static.” Create independent instances of the same `CombatContext` or `PlayerContext` for different scenes, player sessions, or tests.

### Consolidate Constructors

Review and classify every constructor parameter:

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

If an extra parameter has no clear instance-specific meaning, move it into the appropriate Context or move one-time input to a method or command.

### Design Contexts

- Implement each Context as a regular class organized around a broad layer or domain boundary. Reuse it across related use cases; do not create records, data-only DTOs, or micro-Contexts for each caller's minimal dependency set.
- Let a Context act as the composition and lifecycle owner for its scope: keep systems in private fields and expose them through public get-only properties.
- Use `Initialize`, `Update`, and `Destroy` to preserve explicit construction, update, and teardown order; do not require every system to be passed into the Context constructor.
- Allow an empty constructor or stable scope-specific configuration. Keep one-time gameplay commands and instance-specific Entities outside the Context constructor.
- Forbid `Get<T>()`, string keys, dictionary lookup, or runtime registration that turns a Context into a Service Locator.
- Let owned systems manage scoped runtime state and gameplay rules. Do not turn the Context itself into a loose store for Entities, commands, arbitrary gameplay data, or use-case logic.
- Expose only ports allowed at the current layer. A Domain Context must not expose a database, HTTP client, or other Infrastructure implementation.
- Do not aggregate every module into a system-wide `AppContext` or `GlobalContext`. When a Context grows too broad, split it by domain, layer, or lifecycle.

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

## Domain Model and Encapsulation

### Aggregates and Entities

- Let the Aggregate Root maintain its consistency boundary and business invariants.
- Change state through methods that express gameplay intent, such as `ApplyDamage`, `EquipItem`, `CompleteQuest`, or `GrantReward`.
- Keep fields, child-entity collections, domain-event collections, caches, and strategy objects private.
- Do not replace domain behavior with public setters or mutable collections.
- Return only stable Value Objects or read-only DTOs/snapshots; never return the internal collection itself.
- Preserve Entity identity and maintain valid state through behavior throughout its lifecycle.

### Value Objects

- Keep them immutable;
- Validate at creation time;
- Compare them by value;
- Do not expose mutable internal data.

### Repositories

- Define Repositories around Aggregate Roots;
- Persist and rehydrate Aggregates without exposing storage details;
- Let Application Services invoke Repositories;
- Do not use a Repository to inspect the internal state of another system under test, unless the Repository itself is the test subject.

### Application Services

- Orchestrate use cases, transactions, Repositories, Domain objects, and external ports;
- Delegate core business decisions to the domain model;
- Return contract-level DTOs/results, not mutable internal object graphs.

## Public API Gate

Treat the public API as a stable product contract, not a testing toolbox.

Allow the public surface to express:

- Business capabilities required by real callers;
- Stable commands, queries, results, DTOs, or snapshots;
- Formal architectural ports and strategy interfaces.

Do not let the public surface expose:

- Internal fields, mutable collections, caches, Repositories, or implementation classes;
- Intermediate state used only for assertions;
- APIs named `ForTest`, `TestOnly`, `__test`, `ExposeInternal`, `ResetForTest`, `GetInternalState`, or similar;
- Test-only getters, setters, delegates, proxies, callbacks, or hooks.

Before adding or expanding a public API, answer these questions in order:

1. Is there a real production caller?
2. Does it express a clear business capability rather than an implementation step?
3. Can the existing contract already complete the behavior?
4. Does it expose an internal representation or introduce mutable state?
5. Would the API still be valid if the tests did not exist?

If the answers show that the API exists only for testing convenience, refuse to add it and redesign the testing strategy. Implement it when it is the minimal business contract explicitly required by the task. If it would create a meaningful, unauthorized contract expansion, explain the API, caller, necessity, and alternatives before requesting confirmation.

### Do not extract interfaces without real variants

Add an interface/port ONLY when the type will genuinely have multiple production implementations. For a single-implementation class, use a concrete class directly — no interface, no port, no abstraction "for future flexibility." Pre-emptive interfaces are over-design and expand the contract surface for no benefit.

- Ask: "Will this type have ≥2 real production variants?" If no → concrete class.
- Do not add a port just for testability. If a unit test can't be written without faking a type that has no real variant, that test belongs to integration (see Behavioral Testing Rules), not the unit suite.
- Corollary: never introduce an unauthorized interface during task execution. If a deviation seems necessary, ask the user first.

## Test Seams and External Dependencies

Create replaceable ports/interfaces only for real boundaries. Valid boundaries include:

- Repositories, save systems, platform SDKs, and external services;
- Nondeterministic or engine-provided sources such as time, randomness, physics queries, navigation, and UUIDs;
- Formal gameplay strategies such as damage calculation, loot selection, spawning, matchmaking, and authorization;
- Components that may genuinely have multiple production implementations.

Make test fakes implement the same formal port, such as `InMemoryPlayerRepository`, `FixedClock`, `SeededRandom`, or `FakeGameEventPublisher`. Do not add a second entry point or control channel for tests.

For full-scope tests, exercise the same Context lifecycle: construct it, call `Initialize`, drive `Update` when needed, and finish with `Destroy`. For isolated system tests, use formal ports/fakes at the system boundary; do not add test-only Context setters or restore separate global-dependency constructor parameters.

Reject these backdoors disguised as “dependency injection”:

- Observers or delegates used only to verify internal steps;
- `SetXxxForTest` methods that replace private implementations at runtime;
- Proxies that expose caches, collections, or invocation counts;
- Hooks with no production meaning.

## Behavioral Testing Rules

Use black-box testing by default:

- Observe results through public gameplay methods, Application Services, input/server entry points, domain events, or formal DTOs/snapshots;
- Arrange state through public contracts or formal port fakes;
- Assert business outcomes, domain errors, and observable side effects;
- Prefer acceptance/integration coverage for the main path, then add unit tests where necessary.

Do not:

- Access private, protected, or internal fields and collections;
- Change production-member visibility for tests;
- Use `as any`, `obj["privateField"]`, or descriptors in TypeScript to bypass private access;
- Use reflection or `InternalsVisibleTo` in C# to bypass encapsulation;
- Assert private-method calls, internal collection sizes, cache layouts, or other implementation details.

Classify a test failure before changing code:

| Type | Response |
| --- | --- |
| implementation bug | Fix the implementation to satisfy the existing contract |
| test bug | Rewrite the test to assert behavior through a public boundary |
| contract gap | Design the smallest public contract with business meaning; request confirmation when necessary |
| architecture gap | Add a formal port/interface instead of a test hook |
| setup issue | Fix the fixture, configuration, or environment |

Do not make public API expansion the default response to a failing test.

### Unit tests cover only units; integration runs in the real engine

Automated unit tests cover ONLY unit classes — engine-agnostic logic with no engine/visual dependency and no Context-level wiring. Anything that requires the real engine runtime, holds engine nodes, mounts views, or wires multiple scopes together (Context, Bootstrap, GameFlow, View mounting, scene assembly) is integration and is verified by running the real engine, not by unit tests.

- Unit-test: leaf engine-agnostic logic only (schedulers, tick counters, value objects, math/collection utils, single domain behaviors with no engine nodes).
- Do NOT unit-test: Contexts, bootstrap/flow controllers, View wrappers, anything that constructs views or touches engine nodes.
- Visual/node-bearing types are never faked in unit tests. Verify them by running the real scene in the engine (screenshots, scene-tree inspection, output/error logs, runtime assertions).
- Never modify the design (add an interface, seam, setter, or test-only hook) just to make an integration concern unit-testable. If a unit test can't be written honestly, the behavior belongs to engine integration, not the unit suite.
- Contexts belong to overall integration; their lifecycle is verified by running the real entry point, not by fake-injecting their dependencies.

## Vertical Slices and Completeness

For every delivery, complete the applicable parts of this path:

```text
Player input / gameplay command / engine or server entry
  -> Application service
  -> Domain behavior
  -> Port
  -> Engine/infrastructure adapter
  -> Observable game result through a public boundary
```

Do not deliver:

- `TODO`, `deferred`, `placeholder`, `stub`, or `not implemented` markers;
- Fake-success returns or swallowed failures;
- Disconnected modules intended to be integrated “later”;
- Horizontal class scaffolding with no runnable behavior.

When a dependency is missing and the task allows a local substitute, implement and connect the smallest real version, such as an in-memory player Repository, fixed Clock, or seeded random source implementing a formal port. Do not turn a fake into a production-code backdoor.

## Language-Specific Checks

### TypeScript

- Prefer ECMAScript `#private` or the project's established `private` convention;
- Use `Readonly` and read-only collections for external DTOs;
- Export only contracts from a public barrel; do not export internal implementations or private Domain types;
- Keep engine/runtime objects out of public domain contracts; adapt them at module boundaries;
- Do not use type assertions or bracket notation to bypass encapsulation.

### C#

- Use private fields and controlled `private set` access for domain state;
- Prefer plain C# Domain Objects that hold an engine-agnostic View contract; make the concrete View wrapper a plain class with a private native-node field instead of inheriting `MonoBehaviour` or `Godot.Node`;
- Use `[SerializeField] private` for editor wiring when supported; do not make gameplay state public merely for Inspector access;
- Do not return internal mutable collections such as `List<T>` or `Dictionary<TKey,TValue>`;
- Return immutable values, read-only DTOs, or defensive snapshots when query access is required;
- Do not add `InternalsVisibleTo` for tests or use reflection to read or write private state.

## Pre-Delivery Audit

Before completing the task, verify every item:

- [ ] The feature runs through a real public boundary and has behavioral coverage proportional to its risk;
- [ ] Domain owns gameplay invariants, Application orchestrates, and engine callbacks/adapters contain no gameplay rules;
- [ ] Domain Objects and View wrappers avoid engine inheritance; native nodes stay private, and any required inherited Host remains minimal;
- [ ] Outcome-affecting engine services are controllable for deterministic tests, and Context lifetimes preserve multi-instance isolation;
- [ ] Shared systems live in a broad, regular-class Context with private fields, get-only properties, and ordered `Initialize`/`Update`/`Destroy`;
- [ ] Contexts are not Service Locators, state bags, or god objects; parameters outside them have instance-specific meaning;
- [ ] No public mutable state, internal collection exposure, or visibility widening exists;
- [ ] No test-only API, hook, delegate, proxy, reset method, or internal-state assertion exists;
- [ ] Fakes implement formal ports/interfaces, and dependencies follow the project architecture;
- [ ] No `TODO`, `deferred`, `placeholder`, `stub`, or fake success remains.

In the final delivery, report briefly:

1. The completed business path;
2. Any added or changed public contract, or explicitly state that none changed;
3. The formal ports/fakes used;
4. Verification commands and results;
5. Any architectural decision that still requires user input.
