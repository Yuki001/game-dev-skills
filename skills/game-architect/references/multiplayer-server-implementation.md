# Multiplayer Server Implementation Guide

Reference for implementing multiplayer server infrastructure. This document focuses on reusable implementation patterns: framework skeleton, core abstractions, lifecycle, extension points, implementation order, and the parts that should vary by project needs.

Use `multiplayer-server-architecture.md` for runtime model, ownership, deployment, persistence, and framework-family selection. Use `multiplayer-protocol.md` for protocol contracts and sync rules. Use `multiplayer-overview.md` for gameplay-side authority split and synchronization goals.

---

## 1. Scope And How To Use This Document

Use this document when the question is:

- What are the minimum runtime abstractions of a multiplayer server framework?
- How should core modules connect in code?
- What should be built first in a single-process version?
- How should the framework evolve to multi-node deployment later?

This document is implementation-oriented. It is not a replacement for product-level server architecture decisions.

Two reading rules:

- Treat the abstractions in this document as a checklist, not a fixed class hierarchy.
- Let project requirements decide module split, engineering structure, and concrete class design.

---

## 2. Implementation Principles

Recommended goals:

- Make authority boundaries explicit
- Separate connection concerns from gameplay runtime
- Keep single-process startup simple
- Allow later evolution to multi-node deployment
- Keep protocol, runtime, and persistence replaceable
- Provide enough hooks for gameplay modules without forcing early over-design
- Keep single-node development shape as close as possible to production shape

Recommended non-goals for v1:

- Full microservice decomposition
- Perfect hot migration of every runtime object
- General-purpose distributed transactions
- Premature plugin marketplace or dynamic module loading

Patterns repeatedly validated by existing frameworks:

- hybrid architecture: realtime runtime plus HTTP/RPC backend path
- explicit room or match lifecycle instead of implicit object lifetime
- two-phase join with reservation or validation before runtime entry
- sequential processing per session, player, room, or actor owner
- named group or presence abstraction for fan-out delivery
- single-process starter mode that can evolve to distributed mode later
- extension points via filters, hooks, handlers, or plugins instead of editing the core

---

## 3. Core Skeleton

### Stable Skeleton vs Project Variants

Some parts of server implementation are relatively stable across projects. Others should change with runtime model, team size, language, engine, and framework family.

Usually stable:

- authority boundary
- session and identity binding
- message dispatch entry
- owner serialization model
- persistence boundary
- replication boundary
- lifecycle and cleanup
- observability hooks

Usually variant by project:

- project folder structure
- class granularity and inheritance depth
- room-based vs scene-based vs encounter-based runtime base classes
- handler organization: RPC, message registry, actor mailbox, or command bus
- repository layering and cache strategy
- plugin, hook, or composition style

Use this document to identify the stable skeleton first. Then adapt the code organization to the actual project.

### Minimum Runtime Abstractions

Most multiplayer server frameworks can start with these abstractions:

| Abstraction | Responsibility |
|:---|:---|
| **ServerApp** | Process bootstrap, config, lifecycle, service registry |
| **Transport** | Accept connections, send/receive packets, heartbeat |
| **Session** | Client identity binding, connection state, routing context |
| **Dispatcher** | Route decoded messages to handlers or runtime owners |
| **PlayerService** | Durable player/meta state authority |
| **RoomService / SceneService** | Realtime runtime creation, lookup, ownership |
| **RuntimeInstance** | One room, encounter, or scene authority object |
| **Replication / Broadcaster** | Build outbound updates for relevant clients |
| **Persistence** | Storage abstraction, cache, flush, checkpoint |
| **Timer / Scheduler** | Tick, timeout, delayed task, retry |
| **Metrics / Logger** | Observability and diagnostics |
| **Presence / GroupRegistry** | Track members of room, channel, party, or stream |
| **Matchmaker / ReservationService** | Find runtime, reserve capacity, issue join token |
| **Filter / Hook Pipeline** | Auth, tracing, validation, rate limit, audit |
| **Contract / Codegen** | Shared message contracts, handler metadata, client SDK generation |

If a framework cannot clearly locate these responsibilities, it is usually still too vague to implement safely.

### Core Interface Shape

Keep interfaces small and stable.

Example interface families:

```text
IServerApp
ITransport
ISessionManager
IDispatcher
IPlayerRepository
IRuntimeDirectory
IRuntimeInstance
IReplicator
ITimerService
IPresenceRegistry
IReservationService
IFilter
```

Interface rules:

- One interface should own one kind of responsibility
- Favor dependency injection through constructors or explicit registration
- Hide transport details from gameplay logic
- Hide storage details from gameplay handlers where possible
- Prefer IDs and handles across module boundaries instead of direct object reach-through
- Keep the contract layer stable enough that client SDK generation or shared-interface use remains possible

Do not force every abstraction into a public interface. Small projects can keep some pieces as concrete classes and only abstract boundaries that are likely to change.

---

## 4. Code Organization

### Project Structure Variants

There is no single correct project structure. Pick the simplest structure that keeps ownership and dependency flow clear.

Common shapes:

- **feature-first**: group by player, room, combat, social, inventory; good when gameplay modules dominate
- **layer-first**: group by transport, session, dispatch, runtime, persistence; good for framework-heavy infrastructure work
- **hybrid**: keep stable infrastructure layers, but place gameplay code by feature; often the most practical default

Class design can also vary:

- **composition-first services** for backend/platform-heavy servers
- **runtime base class + modules/components** for room or scene servers
- **actor/mailbox objects** for entity-ownership systems
- **plain handlers + repositories** for short-connection or turn-based services

The key requirement is not the directory tree itself. The key requirement is that ownership, message flow, and persistence boundaries remain obvious in code review.

### Concrete Structure Templates

#### Room-Based Realtime Server

```text
server/
├── app/
├── gateway/
├── session/
├── protocol/
├── dispatch/
├── rooms/
│   ├── directory/
│   ├── runtime/
│   ├── handlers/
│   └── replication/
├── player/
├── persistence/
├── presence/
└── ops/
```

Use when the main runtime unit is a room or match.

- `gateway/` only handles connection and packet I/O
- `session/` binds connection to identity and runtime location
- `rooms/directory/` finds room by ID and controls lifecycle lookup
- `rooms/runtime/` owns authoritative state and serial command execution
- `rooms/handlers/` converts decoded messages into room commands
- `rooms/replication/` builds room deltas or broadcasts

#### Short-Connection Player Data Server

```text
server/
├── app/
├── api/
├── auth/
├── protocol/
├── player/
│   ├── service/
│   ├── modules/
│   └── delta/
├── persistence/
├── cache/
└── ops/
```

Use when the server is mainly API-driven and the core authority unit is the player.

- `api/` maps HTTP/RPC handlers to domain commands
- `player/service/` loads player context and controls write ordering
- `player/modules/` contains inventory, quests, progression, mail, and similar systems
- `player/delta/` collects changed fields and attaches them to tick or business responses
- `cache/` is infrastructure only; gameplay logic should not depend on cache-specific behavior

#### Scene Or World Server

```text
server/
├── app/
├── gateway/
├── session/
├── protocol/
├── dispatch/
├── scene/
│   ├── directory/
│   ├── regions/
│   ├── sync/
│   └── transfer/
├── player/
├── persistence/
├── presence/
└── ops/
```

Use when the runtime is region-based or scene-based rather than room-based.

- `scene/directory/` resolves which region owns an entity or player
- `scene/regions/` runs authoritative regional logic
- `scene/sync/` builds per-client filtered updates
- `scene/transfer/` handles handoff across regions or scenes

---

## 5. Runtime And Execution Model

### Common Runtime Patterns

These patterns usually belong in the framework layer, not in gameplay modules:

- **Reactor / event loop**: drive socket readiness, packet read/write, timer dispatch, and lightweight connection-level tasks
- **Actor / mailbox / owner queue**: serialize mutations for session, player, room, or scene owners, and keep shared-state concurrency explicit
- **Worker pool**: handle blocking or high-latency work such as DB, Redis, HTTP, or file I/O, then marshal results back to the owner context
- **DB connection pool**: manage database connection reuse, limits, backpressure, timeout, and retry policy centrally
- **Redis / RPC client pool**: apply the same pooling and timeout policy to external caches and internal service calls
- **Object pool / buffer pool**: reduce allocation churn for packets, temporary state builders, and frequently reused runtime objects
- **Timer wheel / scheduler queue**: support timeout, delayed task, periodic tick, reservation expiry, and reconnect expiry efficiently

Use these as infrastructure primitives. Gameplay code should consume them through framework APIs instead of managing threads, connections, or resource reuse directly.

### Runtime Lifecycle

### Process Lifecycle

`boot -> load config -> start transport -> register services -> accept traffic -> graceful drain -> shutdown`

### Session Lifecycle

`connect -> authenticate -> create session -> reserve/join runtime or stay in backend flow -> disconnect/reconnect -> close`

### Runtime Instance Lifecycle

`create -> initialize -> accept participants -> run -> settlement/checkpoint -> dispose`

Lifecycle rules:

- Every lifecycle transition should be explicit
- Cleanup path should exist before adding more features
- Runtime disposal should be idempotent
- Reconnect policy should be decided before gameplay code depends on session permanence
- New participant flow should define whether it uses direct join or two-phase reservation

### Join And Reservation Pattern

For room or match based systems, a two-phase join is the safest default:

1. client requests matchmaking or room join
2. framework finds or creates runtime instance
3. framework reserves capacity and issues reservation token
4. client connects or upgrades into runtime using that token
5. runtime validates reservation and completes join

This prevents last-slot races and gives reconnect and timeout cleanup a clear home.

### Message Flow Skeleton

Default request path:

`transport -> decode -> middleware -> dispatcher -> owner service/runtime -> persistence or replication -> encode -> send`

Typical responsibilities:

- **Middleware**: auth, rate limit, version check, tracing
- **Dispatcher**: resolve target handler or owner
- **Owner**: validate and mutate authoritative state
- **Replication**: build delta/snapshot/update set
- **Persistence**: flush or queue writes by policy

Do not let handlers directly perform transport, storage, and gameplay mutation in one place.

### Ordering Model

Most successful frameworks make ordering explicit:

- **per-session sequential** for connection-bound messages
- **per-player sequential** for durable player state mutations
- **per-runtime sequential** for room or scene authority
- **worker-pool + callback marshaling** for I/O-heavy work

Pick one default ordering rule per owner type. Hidden concurrent mutation is where framework complexity usually starts.

### Concrete Request Paths

#### Realtime Room Command

```text
socket packet
-> session decode
-> dispatch by room + message type
-> room mailbox
-> room handler
-> mutate authoritative room state
-> mark dirty entities or properties
-> build outbound deltas
-> send room broadcast / owner ack
-> checkpoint or async persistence if needed
```

Typical split:

- session checks identity and connection state
- dispatch only finds the target owner
- room handler validates command parameters
- room runtime applies game rules
- replication builds packets after state change, not inside transport code

#### Short-Connection Player API

```text
HTTP/RPC request
-> auth
-> load player context
-> route to player module handler
-> mutate player state
-> collect player delta
-> persist by policy
-> attach delta to response
```

Typical split:

- API handler should not directly edit DB rows for gameplay behavior
- player context should serialize writes for the same player
- delta builder should be near player state mutation, not scattered across controllers
- persistence policy can be immediate or queued, but should be explicit

---

## 6. Gameplay Runtime Integration

### Realtime Runtime Skeleton

For room or scene based frameworks, one runtime instance usually needs:

- instance ID
- participant registry
- authoritative state container
- tick/update entry
- command queue or input queue
- event output buffer
- replication context
- lifecycle state

Recommended methods:

```text
Create()
Join()
Leave()
HandleCommand()
Update()
BuildSync()
Checkpoint()
Dispose()
```

Keep runtime code authoritative. Client-specific presentation should stay outside.

Do not treat this method list as mandatory. Some frameworks use `OnMessage()` + internal command dispatch, some use `Tick()`, and some are request/response only. Keep the lifecycle concepts even if method names differ.

### Presence And Group Integration

Most realtime frameworks benefit from a first-class audience abstraction:

- room group
- party group
- chat or stream group
- AOI-derived subscriber set

Minimum operations:

```text
JoinGroup()
LeaveGroup()
BroadcastAll()
BroadcastExcept()
BroadcastOnly()
ListMembers()
```

The storage behind this abstraction can be in-memory for single-process mode and distributed later.

### Player And Runtime Separation

This is the most important framework boundary.

- **PlayerService** owns durable player/meta data
- **RuntimeInstance** owns temporary room/scene/encounter state
- Runtime reads required player data on join
- Runtime writes settlement or validated results back through PlayerService

Avoid writing long-lived player state directly inside room or scene runtime unless the project is intentionally minimal.

### Core Object Relationships

The most important implementation detail is not inheritance depth. It is whether object relationships stay clean.

Recommended dependency direction:

```text
Transport/Session
    -> Dispatcher
        -> Owner Locator
            -> RuntimeInstance or PlayerService
                -> Domain Modules
                -> ReplicationContext
                -> PersistenceFacade
```

Recommended ownership rules:

- `Session` can know current player ID and current runtime ID, but should not hold direct gameplay state
- `Dispatcher` can resolve owner and handler, but should not contain business rules
- `RuntimeInstance` or `PlayerService` is the main mutation boundary
- `Domain Modules` can mutate owned state, but should not send packets directly
- `ReplicationContext` builds outbound changes from authoritative state and visibility rules
- `PersistenceFacade` hides repository/cache/write-queue details from gameplay modules

Avoid these direct dependencies:

- room or scene code directly calling socket send
- gameplay modules directly calling DB clients
- transport layer directly reading gameplay state
- controllers or handlers directly composing replication payloads for every feature

### Replication Integration

A reusable framework should support at least one of these paths:

- manual broadcast
- automatic property replication
- snapshot/delta builder

Recommended replication pipeline:

`authoritative state change -> mark dirty -> filter by relevance/AOI -> build payload -> send to target sessions`

Minimum replication concerns:

- owner-only vs shared state
- AOI or audience filtering
- dirty tracking
- send rate control
- initial snapshot vs incremental delta

Implementation patterns validated by existing frameworks:

- schema or property-based auto sync for fast room development
- manual broadcast for competitive or protocol-sensitive games
- per-client filtered view for hidden information
- initial full snapshot followed by incremental patching

Concrete placement rule:

- dirty marking happens in owner context right after state mutation
- filtering happens in replication layer, not in gameplay rule code
- serialization happens at protocol boundary, not in domain objects
- send scheduling happens in transport or outbound queue, not inside handlers

### Persistence Integration

Do not hardwire gameplay code directly to the database.

Recommended persistence layers:

- repository or storage interface for player/meta state
- checkpoint interface for runtime state
- async write queue where write-behind is acceptable
- explicit write-through path for critical economy data

The framework should define when writes happen:

- login load
- periodic flush
- settlement
- logout
- shutdown drain

Also define where persistence is triggered from:

- direct request handler
- runtime settlement
- event/hook pipeline
- async worker callback marshaled back to owner context

Concrete placement rule:

- gameplay modules call `PersistenceFacade` or repository interfaces
- repository layer decides cache, DB, batching, and retry strategy
- owner context decides whether a write is inline, deferred, settlement-only, or checkpoint-based

### End-To-End Example

#### Example: `MoveCommand` In A Room-Based Server

1. transport receives packet and resolves session
2. dispatcher routes by `roomId + messageId`
3. room mailbox serializes the command
4. room handler validates input shape and basic preconditions
5. room runtime applies movement rules and updates authoritative position
6. affected entities are marked dirty
7. replication layer builds per-client deltas
8. owner ack and room broadcasts are queued
9. optional checkpoint or event persistence is triggered by policy

Resulting code responsibility split:

- transport owns packet I/O
- dispatcher owns routing
- room owns gameplay mutation
- replication owns outbound state build
- persistence owns durability path

---

## 7. Applying This Reference

### How To Adapt This Document

When applying this document to a real project, decide these before writing too much framework code:

- Is the server room-based, scene-based, encounter-based, or request/response heavy?
- Does the project need a reusable framework, or only one production codebase with clear modules?
- Is the team better served by feature-first folders or infrastructure-first folders?
- Which boundaries are expected to change: protocol, persistence, runtime model, or deployment shape?
- Which abstractions should stay concrete until scale forces extraction?

If these answers are clear, the rest of the document becomes a menu of implementation patterns instead of a rigid blueprint.

### Recommendation Checklist

When producing an implementation plan, explicitly state:

- chosen runtime model
- ownership units
- minimum core abstractions
- single-process starter shape
- replication path
- persistence path
- reconnect policy
- multi-node evolution trigger
- ordering model per owner type
- join/reservation flow
- presence/group abstraction
- extension model: filters, hooks, plugins, or code generation

---

## 8. What To Read Next

- Read `multiplayer-server-architecture.md` for server architecture decisions
- Read `multiplayer-protocol.md` for message contracts and sync rules
- Read `multiplayer-overview.md` for gameplay-side authority split and sync model selection
