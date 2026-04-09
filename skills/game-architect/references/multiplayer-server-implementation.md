# Multiplayer Server Framework Implementation Guide

Reference for implementing a reusable multiplayer server framework. This document focuses on framework skeleton, core abstractions, lifecycle, extension points, and implementation order.

Use `multiplayer-server-architecture.md` for runtime model, ownership, deployment, persistence, and framework-family selection. Use `multiplayer-protocol.md` for protocol contracts and sync rules. Use `multiplayer-architecture.md` for gameplay-side topology and synchronization goals.

---

## 1. Scope

Use this document when the question is:

- What are the minimum runtime abstractions of a multiplayer server framework?
- How should core modules connect in code?
- What should be built first in a single-process version?
- How should the framework evolve to multi-node deployment later?

This document is implementation-oriented. It is not a replacement for product-level server architecture decisions.

---

## 2. Framework Goals

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

## 3. Minimum Runtime Abstractions

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

---

## 4. Core Interface Shape

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

---

## 5. Recommended Module Layout

```text
server/
├── app/            # bootstrap, config, composition root
├── contracts/      # shared interfaces, DTOs, message IDs, generated stubs
├── transport/      # socket, websocket, gateway adapters
├── protocol/       # message definitions, codecs, error codes
├── session/        # session lifecycle and auth binding
├── dispatch/       # routing, middleware, handler registry
├── runtime/        # room/scene/encounter base runtime
├── matchmaking/    # room query, reservation, join token flow
├── presence/       # group/stream membership and fan-out registry
├── player/         # player state authority and meta systems
├── replication/    # delta build, AOI filter, broadcast
├── persistence/    # repositories, cache, db proxy, checkpoint
├── services/       # matchmaking, social, global services
├── hooks/          # filters, extension points, plugin adapters
├── ops/            # metrics, admin, tracing, health
└── tests/          # integration tests and bot tests
```

This layout is only a starter. Merge modules early if the team is small.

---

## 6. Common Runtime Patterns

These patterns usually belong in the framework layer, not in gameplay modules:

- **Reactor / event loop**: drive socket readiness, packet read/write, timer dispatch, and lightweight connection-level tasks
- **Actor / mailbox / owner queue**: serialize mutations for session, player, room, or scene owners, and keep shared-state concurrency explicit
- **Worker pool**: handle blocking or high-latency work such as DB, Redis, HTTP, or file I/O, then marshal results back to the owner context
- **DB connection pool**: manage database connection reuse, limits, backpressure, timeout, and retry policy centrally
- **Redis / RPC client pool**: apply the same pooling and timeout policy to external caches and internal service calls
- **Object pool / buffer pool**: reduce allocation churn for packets, temporary state builders, and frequently reused runtime objects
- **Timer wheel / scheduler queue**: support timeout, delayed task, periodic tick, reservation expiry, and reconnect expiry efficiently

Use these as infrastructure primitives. Gameplay code should consume them through framework APIs instead of managing threads, connections, or resource reuse directly.

---

## 7. Runtime Lifecycle

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

---

## 8. Message Flow Skeleton

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

---

## 9. Realtime Runtime Skeleton

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

---

## 10. Player And Runtime Separation

This is the most important framework boundary.

- **PlayerService** owns durable player/meta data
- **RuntimeInstance** owns temporary room/scene/encounter state
- Runtime reads required player data on join
- Runtime writes settlement or validated results back through PlayerService

Avoid writing long-lived player state directly inside room or scene runtime unless the project is intentionally minimal.

---

## 11. Replication Integration

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

---

## 12. Persistence Integration

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

---

## 13. Single-Process Starter Version

A practical first implementation can be:

- one process
- one transport
- one dispatcher
- one player service
- one room service or one scene service
- one persistence adapter
- one scheduler
- one presence registry
- optional HTTP/RPC API beside realtime transport

Build order:

1. transport + session + dispatcher
2. auth and session binding
3. reservation or join flow
4. player service and storage
5. room/scene runtime base class
6. presence/group registry
7. replication path
8. reconnect and shutdown cleanup
9. metrics and admin tools

If the single-process version is unclear, multi-node design will also be unclear.

---

## 14. Multi-Node Evolution Path

When scale requires splitting, evolve in this order:

1. separate gateway/connection from logic
2. separate player/meta authority from runtime instances
3. add runtime directory or routing registry
4. externalize shared cache and service discovery
5. add dedicated matchmaking/global services

Do not split nodes before ownership and routing keys are stable.

Useful evolution patterns from existing frameworks:

- room pinning: runtime stays on the node where it was created
- sticky sessions for stateful realtime channels
- local interface first, distributed backend later for presence or groups
- same-process short path optimization before network hop

---

## 15. Required Operational Baseline

Even a small framework should include:

- structured logging
- metrics for connection count, queue depth, tick time, send size, write latency
- health checks
- graceful shutdown and drain
- admin commands or debug endpoints
- bot or scripted client testing entry
- trace or correlation ID through request flow
- slow-call or stuck-runtime detection

Without these, the framework is difficult to validate under load.

---

## 16. Common Implementation Mistakes

- Coupling gameplay handlers directly to sockets and DB calls
- Mixing player durable state with room temporary state
- Building multi-node routing before single-node lifecycle is stable
- Using one generic handler abstraction for every runtime shape
- Omitting reconnect and shutdown behavior until late
- Replicating all fields by default without visibility or rate control
- Skipping reservation and capacity control in room-based systems
- Mixing transport contracts, handler metadata, and gameplay logic in one module
- Designing extension points only after game-specific code is already baked into the core

---

## 17. Recommendation Checklist

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

## 18. What To Read Next

- Read `multiplayer-server-architecture.md` for server architecture decisions
- Read `multiplayer-protocol.md` for message contracts and sync rules
- Read `multiplayer-architecture.md` for gameplay topology and sync model selection
