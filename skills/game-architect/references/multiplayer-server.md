# Game Server Architecture

Reference for planning game server architecture and selecting suitable framework families. This document is optimized for design work: identify the runtime model first, then choose ownership boundaries, deployment shape, sync model, and framework family.

Primary focus is authoritative online games. It also covers backend/platform services when they are part of the same product.

Complements `multiplayer-architecture.md` (topology, session shape, sync model, client/server logic split) and `multiplayer-protocol.md` (message design, serialization, heartbeat, reconnect) with server-side architecture guidance.

---

## 1. Scope And First Decision

### What Kind Of Server Are You Designing

Most online games use one or both of these systems:

- **Realtime authoritative runtime:** Server owns room or world state; clients send inputs; server validates, simulates, and broadcasts authoritative results.
- **Backend/platform service:** Server handles authentication, storage, economy, quests, social systems, leaderboards, and other meta features through request/response APIs or async workflows.

Use these defaults unless requirements clearly say otherwise:

- Competitive or shared state should be server authoritative.
- Runtime state and durable player/meta data should be separated.
- One mutable state unit should have one clear owner at a time.
- Start with the simplest topology that satisfies scale and failure requirements.

### Runtime Model Decision Table

| Runtime Model | Best Fit | Core Ownership Unit | Typical Server Shape |
|:---|:---|:---|:---|
| **Room-based realtime** | Match-based games, lobbies, instanced sessions | Room or match | Room process/service with matchmaking and state sync |
| **Encounter/combat service** | Stateful PvE flows, turn-based combat, lightweight battle instances | Encounter, battle, or workflow instance | Stateful service instance driven by API/service calls |
| **Scene/world realtime** | Persistent worlds, region simulation, AOI-heavy games | Scene, region, or entity shard | Scene services with routing and handoff |
| **Backend/platform** | Turn-based, idle, social, economy-heavy games | Player, request, or domain service | API services backed by storage |
| **Hybrid** | Most commercial online games | Room/scene + player/meta service | Realtime runtime plus backend platform |

### Fast Recommendation Matrix

| Situation | Recommended Starting Point | Avoid By Default |
|:---|:---|:---|
| 2-20 player match game | Room-based realtime + persistent backend | Actor/world runtime, microservices |
| Stateful PvE or turn-based combat flow without connection-centric rooms | Encounter/combat service + persistent backend | Full room allocation and realtime room lifecycle |
| Turn-based or async multiplayer | Backend/platform service | Realtime-first stack unless match authority is required |
| Session-based competitive game | Room-based realtime with separate player/meta service | Full BaaS as the only runtime |
| Persistent world with AOI | Scene/world runtime with region ownership | Pure room model as the core world architecture |
| One small team, fast shipping | Single process or simple room cluster | Full service decomposition |
| Platform with multiple game modes | Dedicated gameplay runtime plus backend platform | One framework forced onto every subsystem |

### Selection Heuristics For LLM Planning

- If the game has **continuous simulation** and anti-cheat matters, begin with an authoritative realtime runtime.
- If gameplay is **stateful and step-driven but not connection-centric**, prefer an encounter/combat service over a full room runtime.
- If the game is mostly **CRUD + timers + progression**, begin with a backend/platform architecture.
- If the game has **discrete matches**, prefer room ownership over shared global simulation.
- If the game has **persistent spatial state**, prefer scene or region ownership with explicit handoff rules.
- If the team is small and the game loop is simple, prefer opinionated frameworks with built-in lifecycle and sync.
- If topology control, sharding, or migration is the hard problem, prefer lower-level runtime frameworks and explicit ownership modeling.
- Do not recommend microservices by default. Split only for scale, ownership clarity, or failure isolation.

---

## 2. Ownership Model

Clear ownership is the core design decision. Most other server decisions follow from it.

### Common Ownership Units

| Ownership Unit | Owns | Best For | Main Risk |
|:---|:---|:---|:---|
| **Player** | Inventory, currency, quests, progression, profile | Meta systems and account-bound state | Cross-player transactions and global coordination |
| **Room** | Match simulation, combat, temporary session state | Session games | Crash loses in-memory match state if not checkpointed |
| **Encounter** | Battle state machine, turn order, scripted PvE flow, short-lived combat state | Lightweight combat services and turn workflows | Easy to under-design persistence, idempotency, and recovery |
| **Scene/Region** | Spatial simulation, AOI, world entities | MMO and persistent worlds | Transfer/handoff complexity |
| **Entity/Actor** | One entity's mutable state and message mailbox | High-fidelity simulation, migratable ownership | Higher message-routing complexity |
| **Service/Domain** | Guilds, mail, auction, leaderboard, economy | Cross-session systems | Can become bottleneck if boundaries are vague |

### Ownership Rules

- One mutable object should have one authoritative writer at a time.
- Player/meta state and room/scene runtime state should usually be owned separately.
- Cross-owner operations need explicit design: transaction, saga, lock, event, or compensation.
- State should move only when there is a clear handoff rule.
- Reads can be cached widely; writes should follow ownership boundaries.

### Ownership Patterns

| Pattern | Description | Use When |
|:---|:---|:---|
| **Single writer** | One room, actor, player service, or scene owns all writes | Default pattern for stateful systems |
| **Pinned ownership** | State stays on the node where it was created | Rooms and session instances |
| **Sharded ownership** | Ownership determined by player ID, room ID, region ID, or key range | Player services, scenes, domain services |
| **Workflow ownership** | One short-lived encounter/workflow instance owns progression until completion | PvE combat flows, turn resolution, scripted encounters |
| **Migrating ownership** | Ownership can move between processes while preserving logical identity | Entity-centric MMOs, region transfer |
| **Stateless request handling** | No in-memory authoritative owner between requests | BaaS, request/response APIs |

---

## 3. Process Topology

Once ownership is clear, choose the minimum deployment topology that can host it.

### Topology Patterns

| Pattern | Structure | Best For | Tradeoff |
|:---|:---|:---|:---|
| **Single-process monolith** | All roles in one process | Prototype, LAN, early production | Fastest to build, weakest scaling/isolation |
| **Homogeneous multi-node** | Any node handles most requests; DB-backed state | API-heavy backends, BaaS | Simple scaling, weak fit for large in-memory runtimes |
| **Room-pinned multi-node** | Rooms created on one node stay there | Session games | Good match scaling, each room limited to one node |
| **Gateway-Broker-Logic** | External gateway, centralized routing, protected logic servers | High connection counts, command-routed architectures | More moving parts and routing complexity |
| **Actor/Location cluster** | Message routing through location or actor registry | Migratable entities, world simulation | More complex operations and debugging |
| **Service tree cluster** | Process contains services, services contain modules | Custom platforms and service-oriented backends | Flexible but easy to over-design |

### Logical Roles

| Role | Responsibility | Typical State |
|:---|:---|:---|
| **Connection/Gateway** | Accept connections, heartbeat, protocol decode, session binding | Session state |
| **Auth** | Identity validation, token/session issuance | Stateless or DB-backed |
| **Matchmaker** | Queueing, property matching, room assignment | Soft state |
| **Player** | Durable player and meta-system authority | Player state |
| **Room** | Session gameplay authority | Match state |
| **Encounter/Combat** | Short-lived battle or turn-flow authority | Encounter state |
| **Scene** | Persistent world authority | Region state |
| **Global/Domain** | Social, guild, mail, leaderboard, economy, auction | Service/domain state |
| **Persistence/DB proxy** | Database access, cache, batching, storage policy | Cache and write queues |

### Deployment Profiles

| Profile | Processes | When To Use |
|:---|:---|:---|
| **Minimal** | Everything embedded | Prototype, small release, low CCU |
| **Backend-only** | Auth + API + Persistence | Turn-based, idle, social, async multiplayer |
| **Combat service** | Auth + Player + Encounter/API + Persistence | Lightweight PvE combat, card battle loops, turn workflows without room allocation |
| **Small room** | Auth + Room/API + Persistence | Small session games with limited backend complexity |
| **Standard room** | Gateway + Auth + Matchmaker + Player + Room + Persistence | Mid-scale realtime match games |
| **Persistent world** | Gateway + Auth + Player + Scene + Global + Persistence | MMO or sandbox worlds |
| **Full platform** | Separate gameplay and domain services | Large products with multiple game modes |

### Service Discovery And IPC

| Concern | Common Choices | Use When |
|:---|:---|:---|
| **Discovery** | Static config, shared DB, distributed KV, built-in cluster registry | Depends on cluster size and dynamic scaling needs |
| **Routing** | Direct RPC, broker routing, actor location, pub/sub streams | Depends on ownership style and fan-out needs |
| **Presence** | Session registry, stream registry, online-location table | Match joins, chat, parties, reconnect |
| **Events** | In-process event bus, distributed pub/sub, domain events | Cross-system coordination |

### Evolution Rule

Start from the smallest profile that fits. Split processes only when one of these becomes true:

- One role has a clearly different scaling curve.
- One role needs separate failure isolation.
- One role needs independent deployment or ownership by another team.
- One role creates contention because its writes should be isolated.

---

## 4. Runtime Architecture

This section covers the runtime model for live gameplay and connection handling.

### Room-Based Runtime

Best for session games: card battles, party games, shooters, MOBAs, raid instances.

**Core characteristics:**

- Room is the authoritative owner for match state.
- Room lifecycle is explicit: create, accept joins, run, leave/reconnect, dispose.
- Matchmaker usually assigns or creates rooms before the client joins.
- Room state is isolated from other rooms.
- Room scaling is horizontal at room granularity, not inside a single room.

**Typical lifecycle:**

`Create -> Wait -> Auth/Validate -> Join -> Running -> Leave/Reconnect -> Dispose`

**Important room decisions:**

- Whether seats are reserved before join
- Whether rooms auto-dispose when empty
- Whether reconnect resumes session or recreates state
- Whether match state is checkpointed

### Encounter/Combat Runtime

Best for lightweight but stateful combat flows: PvE card battles, asynchronous turn resolution, scripted boss fights, roguelike encounters, and short-lived battle workflows that do not need room allocation or connection-centric lifecycle.

**Core characteristics:**

- Encounter is the authoritative owner for battle state until the workflow completes.
- Clients usually drive it through API calls or service calls rather than room join and long-lived room presence.
- Lifecycle is short-lived but still stateful: create, advance phases/turns, resolve actions, complete, persist outcome, dispose.
- It behaves like a lightweight room in ownership terms, but operationally behaves more like a stateful backend service.

**Use this model when:**

- The combat flow has authoritative state and ordered actions.
- The system needs turn/phase validation, buffs, cooldowns, or scripted progression.
- You do not need matchmaking, live room membership, or high-frequency broadcast.
- Recovery and idempotent action handling matter more than realtime transport.

**Important encounter decisions:**

- What key owns the encounter: player, party, dungeon run, stage instance, or encounter ID
- Whether the encounter lives only in memory, is checkpointed each turn, or persists every action
- Whether duplicate client actions must be idempotent
- Whether resolution is synchronous, asynchronous, or queue-driven
- How combat completion commits rewards and side effects back into player/meta systems

### Scene/World Runtime

Best for persistent worlds, region-based worlds, heavy AOI, or migrating entity ownership.

**Core characteristics:**

- Spatial world is partitioned by region, scene, shard, or entity ownership.
- AOI determines what each client receives.
- Handoffs between regions or owners must be explicit.
- World runtime usually needs more routing and location-awareness than room systems.

**Important world decisions:**

- What unit owns a moving entity
- How region boundaries trigger transfer
- Where global services stop and scene ownership begins
- How entity identity survives migration

### Backend/Platform Runtime

Best for request/response gameplay, meta progression, economy, and social systems.

**Core characteristics:**

- Server validates requests and persists results.
- There may be no continuously running room or world loop.
- Most scale is API throughput and storage throughput rather than simulation throughput.
- Consistency and permissions matter more than snapshot/broadcast smoothness.

### Session And Connection Management

| Concern | Guideline |
|:---|:---|
| **Authentication** | Authenticate before binding durable identity to a live session |
| **Heartbeat** | Detect stale connections and clean up routing state |
| **Session registry** | Track live sessions, room/scene location, and reconnect eligibility |
| **Reconnection** | Preserve session only for an explicit timeout window and recovery policy |
| **Connection separation** | Separate gateway/connection concerns from gameplay authority when scale grows |

### Matchmaking And Join Flow

For room-based games, a two-phase join is the safest default:

1. Matchmaker finds or creates a room and reserves capacity.
2. Client connects to the assigned room using a temporary token or reservation.
3. Room validates the reservation and turns it into a live session.

This prevents last-slot race conditions and allows timeout-based cleanup.

---

## 5. Communication And State Sync

This section centralizes topics that were previously scattered across dispatch, broadcasting, sync, and room chapters.

### Dispatch Patterns

| Pattern | Best For | Tradeoff |
|:---|:---|:---|
| **Type switch / message registry** | Monoliths and fixed message sets | Simple but less scalable for large codebases |
| **cmd/subCmd routing** | Command-driven servers and brokers | Efficient and explicit, less type-rich |
| **RPC / method dispatch** | Typed service APIs and request/response systems | Good tooling, may hide protocol costs |
| **Actor mailbox** | Entity-centric ownership | Excellent isolation, more routing infrastructure |
| **Filter / middleware pipeline** | Auth, rate limit, validation, logging, audit | Great cross-cutting control, adds indirection |

Encounter/combat services commonly use RPC or request/response dispatch with explicit phase validation rather than room-message broadcasting.

### Broadcast And Targeting Patterns

| Pattern | Use When |
|:---|:---|
| **All** | Countdown, start/end signals, global room events |
| **Except sender** | Visible movement/actions |
| **Filtered subset** | Teams, factions, spectators, private info |
| **Named group/stream** | Parties, rooms, chat, channels |
| **Single target** | Private responses, inventory, authoritative correction |

### State Synchronization Models

| Model | Best For | Strength | Weakness |
|:---|:---|:---|:---|
| **Automatic delta/schema sync** | Small to medium rooms, fast iteration | Low implementation cost | Less control over payload design |
| **Manual broadcast** | Competitive action, custom protocol | Full control | More engineering work |
| **Turn/phase response sync** | Encounter services and turn workflows | Simple authoritative progression | Less suitable for high-frequency realtime state |
| **Snapshot + AOI filtering** | Persistent worlds and ECS/entity sync | Strong world modeling | Higher complexity and bandwidth |
| **Lockstep / deterministic input sync** | Fighting, RTS, deterministic subsystems | Low bandwidth, fairness | Determinism and recovery are hard |
| **Hybrid** | Mixed games | Tailored to subsystem needs | Harder to reason about end-to-end |

### Replicated Scene Object Properties

- Many engines provide built-in replicated properties or network variables for scene objects.
- Typical usage is to mark selected properties as synchronized, set sync interval or dirty-check frequency, and let the runtime auto-send updates to relevant clients.
- Common synchronized fields include transform, velocity, health, animation state, and interactable flags.
- This is usually an engine-level implementation of automatic state sync, often combined with AOI and per-client filtering.
- Use it for stable scene-object state; use event/RPC messages for one-shot actions.

### Lockstep Rules

- Deterministic arithmetic and RNG are mandatory.
- Input scheduling policy must be explicit: wait-all, delayed execute, prediction, rollback, or timeout fallback.
- Desync detection should use state hashes or equivalent verification.
- Recovery should define snapshot, rollback, replay, or bot takeover behavior.

Strict wait-for-all-input is the simplest lockstep model, not the only valid one.

### Per-Client Filtering

Apply visibility rules before send:

- **Ownership filter:** Only owner sees private state.
- **Property filter:** Hide cards, fog-of-war data, secret stats, hidden entities.
- **AOI filter:** Only send nearby or relevant entities.
- **Role filter:** Spectator, team, admin, or replay client gets a different view.

### Tick And Rate Design

| Parameter | Typical Range | Notes |
|:---|:---|:---|
| Simulation rate | 10-128 Hz | Depends on mechanics and physics needs |
| Broadcast rate | 10-60 Hz | Usually lower than simulation |
| Input batching | 1-4 frames | Reduces overhead for input-driven protocols |

Default principle: decouple simulation from outbound broadcast where possible.

---

## 6. Persistence And Recovery

Durability policy should be designed explicitly instead of being inferred from framework defaults.

### Storage Models

| Model | Best For | Notes |
|:---|:---|:---|
| **Key-value/document** | Player saves, settings, inventory, flexible state | Good for owner-scoped blobs |
| **Relational** | Economy, guilds, social edges, transactions, leaderboards | Best when constraints and joins matter |
| **Component/entity storage** | Simulation-heavy systems, entity persistence | Fits ECS/entity ownership models |
| **Cache-aside / write-behind cache** | Hot data with persistent backing store | Must define flush and crash policy |
| **Event log / event sourcing** | Replay, audit, rebuild, match records | Strong history, higher replay cost |

### Write Policies

| Policy | Use When | Main Risk |
|:---|:---|:---|
| **Write-through** | Economy, purchases, critical progression | Higher latency and DB pressure |
| **Write-behind** | High-frequency mutable state | Data loss on crash |
| **Checkpointing** | Match/scene recovery | Stale checkpoints if interval is too large |
| **Step/turn checkpointing** | Encounter workflows and turn-based combat | Progress loss if checkpoints are too sparse |
| **Input log / replay log** | Lockstep, replay, reconstruction | Long-running sessions create large logs |
| **Optimistic locking** | Multi-node writes to shared objects | Retry logic required |

### Match And World Recovery

For each runtime owner, choose a recovery policy explicitly:

- Recreate empty/new runtime and reconnect users
- Restore from checkpoint or persisted snapshot
- Replay authoritative input/event log
- End the activity and compensate affected users

For encounter/combat services, also define:

- Whether action requests are idempotent by action ID or sequence number
- Whether rewards are committed only at finalization or incrementally during combat
- Whether combat can resume after process restart or must restart from the last checkpoint

If no checkpointing or replication exists, process crash loses in-memory room or scene state.

### Reconnection Policy

| Pattern | Mechanism | Best For |
|:---|:---|:---|
| **Short timeout resume** | Hold session for a limited reconnect window | Most session games |
| **Registry-based resume** | Cache session location and resume token | Multi-node games |
| **Replay-based recovery** | Replay missed state or input history | Lockstep or authoritative replay systems |
| **Fresh join only** | No runtime recovery | Casual, low-stakes or disposable sessions |

---

## 7. Scalability And Operations

### Horizontal Scaling Rules

| Service Type | Usual Scaling Unit |
|:---|:---|
| **Stateless API/Auth** | Add instances behind a load balancer |
| **Player-owned state** | Shard by player ID or account key |
| **Room-owned state** | Distribute rooms at creation time |
| **Scene-owned state** | Partition by region/zone/shard |
| **Domain/global services** | Scale per service according to consistency needs |

### Global Service Guidance

Do not treat all global services the same:

- **Leaderboards** often tolerate cached reads, asynchronous updates, and periodic recompute.
- **Guild/social systems** often shard by guild ID or user ID.
- **Mail/notifications** are often queue-driven.
- **Economy services** often need transaction-oriented or single-writer design.

### Operational Primitives

| Primitive | Why It Matters |
|:---|:---|
| **Tracing** | Follow requests across hops and find distributed failures |
| **Metrics** | Watch queue depth, tick time, connection count, write latency |
| **Slow-call detection** | Detect stalls, deadlocks, bad handlers, overloaded services |
| **Timers/schedulers** | Run retries, delayed tasks, match timeouts, daily resets |
| **Admin/ops surface** | Runtime inspection, moderation, match control, profiling |
| **Testing bots/robot clients** | Validate functionality and load before production |
| **Config reload / hot reload** | Improve iteration speed, but require explicit state migration rules |

### Common Scalability Limits

- A single room usually cannot scale across multiple processes without custom partitioning.
- DB-backed backends scale easily for reads but can bottleneck on hot writes.
- Cross-owner transactions become the main pain point once services are split.
- Broker topologies reduce mesh complexity but add routing hops.
- Actor/location systems improve migration flexibility but increase operational complexity.

---

## 8. Framework Families

This section maps requirement shapes to framework families. It is intentionally generic and should guide selection even when no exact product is known yet.

### Family Mapping

| Framework Family | Best Fit | Strengths | Usually Not Enough By Itself |
|:---|:---|:---|:---|
| **Room-based realtime framework** | Session games with clear room ownership | Room lifecycle, matchmaking hooks, state sync, fast iteration | Durable player data, economy, persistent worlds |
| **Backend platform / BaaS** | Meta-heavy, turn-based, async, social-heavy games | Auth, storage, leaderboards, social features, APIs | High-fidelity realtime runtime |
| **Stateful workflow / encounter service stack** | PvE combat flows, turn workflows, short-lived authoritative battles | Simple deployment, API-driven progression, easy integration with player/meta services | Large-scale realtime presence, high-frequency room broadcast |
| **Actor/ECS runtime** | Persistent worlds, entity-rich simulation | Ownership clarity, migration-friendly routing, simulation structure | Productized backend features and simple onboarding |
| **RPC-hub realtime framework** | Typed request/response plus realtime channels | Strong contracts, group broadcast, middleware pipeline | Matchmaking, ownership model, persistence conventions |
| **Action-routing / broker framework** | Route-driven distributed action games | Explicit routing, gateway separation, sticky session patterns | Meta services and persistence design |
| **Service tree / custom microservices** | Broad platform architecture and custom service layout | Topology control, composition, explicit boundaries | Opinionated gameplay abstractions |
| **Custom lightweight stack** | Narrow-scope games with experienced teams | Full control and low abstraction cost | Lifecycle, tooling, observability, scaling support |

### Framework Traits To Recognize

| Trait / Keyword | Usually Implies | Best For | Often Weak |
|:---|:---|:---|:---|
| **Room lifecycle** | Match/session authority is the core abstraction | Session games | Persistent world modeling |
| **Seat reservation / two-phase join** | Matchmaker and room join are separated safely | Matchmaking-heavy session games | Crash recovery and durability |
| **Automatic delta sync** | Framework optimizes replication for developer speed | Small and medium rooms | Fine protocol control |
| **Workflow state machine / phase progression** | Stateful service advances through ordered combat or business phases | PvE battles, turn workflows, short-lived encounters | Realtime room semantics |
| **Manual broadcast / custom protocol** | State sync is application-owned | Competitive action games | Fast onboarding |
| **Interface-as-schema / contract-first RPC** | Protocol and tooling are strongly typed | Service APIs and typed clients | Built-in authority model |
| **Unary + streaming dual mode** | Supports both APIs and long-lived realtime channels | Mixed backend + realtime workloads | World simulation structure |
| **Group / stream abstraction** | Named broadcast targets are first-class | Rooms, parties, chat, spectators | Durable gameplay state |
| **Plugin / hook runtime** | Core platform is extensible by injected logic | Backend customization and server rules | Full topology freedom |
| **Actor location / mailbox** | Ownership and routing are decoupled from physical placement | MMOs and migrating entities | Simplicity |
| **Entity + system separation** | Data and logic are intentionally decoupled | Complex simulation | Small CRUD-focused teams |
| **Gateway-Broker-Logic** | Routing topology is a first-class concern | High connection counts and protected logic servers | Simplicity |
| **Node-Service-Module tree** | Hierarchical composition with lifecycle-managed subparts | Custom service platforms | Built-in match abstractions |
| **Presence / stream registry** | Location and online membership are first-class | Match joins, chat, reconnect | Transactional persistence |
| **Property-based matchmaking** | Queueing and matching use attributes/tickets | Ranked and mode-constrained queues | Simulation logic itself |

### Keywords To Map To Architecture

- **"room", "lobby", "seat reservation", "match instance", "auto-dispose"** -> room-based realtime
- **"battle workflow", "turn flow", "phase progression", "encounter state", "PVE combat service"** -> encounter/combat service
- **"storage", "leaderboard", "social", "friends", "tournament", "backend APIs"** -> backend/platform
- **"AOI", "region transfer", "entity location", "actor mailbox", "world shard"** -> actor/ECS or scene/world runtime
- **"typed contract", "bidirectional RPC", "duplex stream", "group broadcast"** -> RPC-hub realtime
- **"gateway", "broker", "route registry", "cmd/subCmd", "logic server behind broker"** -> action-routing / broker
- **"service tree", "module hierarchy", "graceful retire", "configurable topology"** -> service-tree/custom microservices
- **"plugin hooks", "before/after API", "runtime module", "match handler extension"** -> backend platform with embedded custom logic

### Recommendation Checklist For LLM

When recommending a framework family, explicitly state:

- Why it fits the runtime model
- What ownership unit it assumes
- What it gives out of the box
- What still needs custom services
- What the first deployment profile should be
- What should not be overbuilt yet
- What scaling path remains open later

---

## 9. Module Writing Patterns

This section is about how game logic is organized inside a chosen framework or server runtime.

### Pattern Catalog

| Pattern | Core Idea | Best For | Weakness |
|:---|:---|:---|:---|
| **Class extension** | Extend framework base classes and override lifecycle | Opinionated room frameworks, fast iteration | Tighter coupling to framework |
| **Plugin system** | Register hooks, RPCs, or match handlers into a complete server | BaaS and extensible backend platforms | Framework boundaries limit architecture freedom |
| **Annotation / metadata driven** | Plain classes discovered through metadata | Routing-heavy and framework-managed codebases | Implicit behavior can hide control flow |
| **Data-logic separation** | Data containers plus stateless systems operating on them | ECS/entity-heavy runtime and deterministic systems | Steeper learning curve |
| **Interface contract** | Shared protocol/interface defines handlers | Typed RPC/service architectures | Usually does not define state ownership for you |
| **Hierarchical composition** | Service contains modules and child modules | Service platforms and modular backends | Less opinionated about gameplay flow |

### Pattern Selection Guide

| Priority | Prefer |
|:---|:---|
| Fast iteration and built-in lifecycle | Class extension |
| Full backend plus custom logic | Plugin system |
| Low coupling and framework-managed routing | Annotation / metadata driven |
| Simulation purity and ownership clarity | Data-logic separation |
| Strong typing and shared contracts | Interface contract |
| Explicit composition and custom service structure | Hierarchical composition |

### Pattern Tradeoffs

| Concern | Most Favorable Patterns |
|:---|:---|
| **Low learning curve** | Class extension, plugin system |
| **Testability** | Plugin system, data-logic separation, annotation-driven |
| **Hot reload friendliness** | Plugin system, data-logic separation |
| **Strong typing across network boundary** | Interface contract |
| **Explicit ownership modeling** | Data-logic separation, hierarchical composition |
