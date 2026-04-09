# Game Server Architecture

Practical guide for building authoritative dedicated game servers. Follow this document sequentially to construct a complete server from architecture selection to implementation patterns.

Complements `system-multiplayer.md` (network topology, sync models, protocol design) with server-side implementation guidance.

---

## 1. Architecture Selection

### What You're Building

An authoritative dedicated server where:
- Server owns all game state (single source of truth)
- Clients send inputs; server validates, simulates, broadcasts results
- Each room/match runs on exactly one process (no live migration)
- Player data persists independently of room lifecycle

### Choose Your Architecture Style

Pick the style that matches your game's core loop. Most production servers combine 2–3 styles.

| Style | Best For | Provides | You Must Add |
|:---|:---|:---|:---|
| **Room-based** | Session games (MOBA, FPS, party) | Session lifecycle, matchmaking, auto state sync | Player data service, DB layer |
| **Full-stack backend** | Mobile/social games needing complete backend | Auth, social, storage, leaderboards | Game loop logic (via plugin) |
| **Actor/ECS** | Complex simulation, MMO, deterministic physics | Entity system, cross-process messaging, hot-reload | Network frontend, topology config |
| **Action-routing** | Distributed action games, high player count | Broker routing, per-player thread safety, SDK gen | DB layer, social features |
| **RPC-hub** | Type-safe realtime, Unity integration | Bidirectional streaming, group broadcast | Matchmaking, DB, player service |
| **Service tree** | Flexible microservices, custom topology | Process hierarchy, profiler, multi-transport | All game logic and persistence |

**Common combinations:**
- **Casual/indie:** Room-based + external DB (PostgreSQL/MongoDB)
- **Mobile social:** Full-stack backend (all-in-one)
- **Competitive session:** RPC-hub + player data service + DB proxy
- **MMO/simulation:** Actor/ECS + action-routing gateway + scene sharding
- **Microservices:** Service tree (full custom)

### Decision Table

| Game Type | Room Size | Primary Need | Recommended |
|:---|:---|:---|:---|
| Turn-based, card games | 2–10 | Simple sync, validation | Full-stack backend |
| Party, casual multiplayer | 2–20 | Fast iteration | Room-based + DB |
| MOBA, battle royale | 10–100 | Realtime sync, matchmaking | Room-based or RPC-hub + player service |
| Action MMO | 50–500/region | Simulation fidelity | Actor/ECS + action-routing |
| Persistent world | 1000+ | Region sharding, AOI | Actor/ECS or service tree |

---

## 2. Process Topology

### Process Architecture Patterns

Observed from production frameworks. Choose based on scale and complexity.

| Pattern | Structure | Concurrency Model | Coordination | Best For |
|:---|:---|:---|:---|:---|
| **Single-process monolith** | All roles in one process | Single-threaded event loop or goroutines | None | Prototype, <100 CCU |
| **Homogeneous multi-node** | Identical nodes, any handles any request | Goroutine-per-connection or async/await | Shared DB + presence cache | BaaS, stateless API, <10K CCU |
| **Room-pinned multi-node** | Rooms pinned to creating node | Single-threaded per process or async | Redis pub/sub for IPC | Session games, 1K–10K CCU |
| **Three-tier (External-Broker-Logic)** | External (connections), Broker (routing), Logic (game) | Per-player thread or virtual thread | Broker routes by cmd | Distributed action games, 10K+ CCU |
| **Fiber/Actor multi-process** | Fiber per logical unit, Actor messaging | Fiber scheduled on thread pool | Actor location service, etcd | MMO, complex simulation, 10K+ CCU |
| **Service tree cluster** | Node → Service → Module hierarchy | Goroutine per service | etcd or built-in master | Microservices, flexible topology |

### Logical Roles (Composable)

These are logical functions, not physical processes. Combine as needed.

| Role | Responsibility | State | Scaling Strategy |
|:---|:---|:---|:---|
| **Connection** | Accept connections, heartbeat, protocol decode | Session state | Horizontal by connection count |
| **Auth** | Token validation, account lookup | Stateless (DB-backed) | Horizontal by request rate |
| **Player** | Player data authority: inventory, currency, quests, all meta-system CRUD | Player state | Shard by player ID |
| **Matchmaker** | Find/create rooms, party formation | Soft state (ticket queue) | Horizontal by queue size |
| **Room** | Session-based game logic: match simulation, combat, state authority | Game state | Horizontal by room count |
| **Scene** | Persistent world logic: region management, AOI, entity authority | Region state | Horizontal by region |
| **Global** | Cross-server services: social, leaderboards, guilds, mail, auctions | Service state | Horizontal by service type |
| **DB Proxy** | Database access, cache, write batching | Cache | Horizontal by query rate |

### Deployment Profiles

The full role catalog represents maximum decomposition. Most projects should start with a simplified profile and split processes as scale demands.

| Profile | Processes | When to Use |
|:---|:---|:---|
| **Minimal (Single Process)** | All roles embedded | Prototype, <100 CCU, game jam, LAN co-op. Single binary handles everything. No horizontal scaling needed. |
| **BaaS (Backend-as-a-Service)** | **Auth** + **Player** + **DB Proxy** | Turn-based, idle, async multiplayer. No realtime room. Client sends CRUD requests (use item, complete quest), server validates and persists. Stateless request-response pattern. |
| **Small Room** | **Auth** + **Player + Room** + **DB Proxy** | Small-scale online games (indie multiplayer, card games). Auth separated for security; Room embeds Player + Matchmaker + gameplay; DB Proxy for async persistence. |
| **Standard Room** | **Connection** + **Auth** + **Matchmaker** + **Player** + **Room** + **DB Proxy** | Mid-scale room-based games (MOBA, FPS, battle royale). Player handles all meta-system CRUD independently. Room focuses on core gameplay, reads/writes player data via Player process. |
| **Persistent World** | **Connection** + **Auth** + **Player** + **Scene** + **DB Proxy** + **Global** | MMO or sandbox. Player holds all player data across region transfers. Scene/World handles world simulation and AOI. Global handles cross-server services. |
| **Full Scale** | All roles | Large MMO or platform with multiple game modes. Matchmaker + Player + Room + Scene coexist. Global services fully decomposed. |

**Evolution Path**: Start with the simplest profile that fits. Split processes when a specific bottleneck emerges — e.g., split Player from Game/Room when meta-system CRUD load grows independently of gameplay, split Matchmaker when matchmaking needs independent scaling, add Connection when connection count exceeds single-process limits, add Global when cross-server features are needed.

### Service Discovery

| Mechanism | Implementation | Use When |
|:---|:---|:---|
| **Static config** | JSON file with node addresses | Single deployment, <10 nodes |
| **Distributed KV** | etcd/ZooKeeper with TTL heartbeat | Dynamic scaling, health checks |
| **Shared DB** | Presence table in main DB | DB already present, avoid new dependency |
| **Pub/sub cache** | Redis pub/sub + hash for node mapping | Multi-node room coordination |
| **Built-in master** | Dedicated master node, gossip or heartbeat | No external dependency |

### Inter-Process Communication

| Pattern | Mechanism | Use When |
|:---|:---|:---|
| **Direct RPC** | TCP call with discovery lookup | Low-latency, known target |
| **Broker routing** | Central broker routes by cmd/subCmd | Many logic servers, avoid mesh |
| **Pub/sub** | Redis channels or NATS | Presence, cross-node events |
| **Actor mailbox** | Location service maps Actor ID → process | Entity-centric, location-transparent |
| **Shared DB** | Write to DB, other nodes poll or get notified | Async, eventual consistency |

---

## 3. Infrastructure Primitives

Build these before game logic. They're the foundation.

| Primitive | Purpose | Implementation Notes |
|:---|:---|:---|
| **Event bus** | Intra-process pub/sub | Auto-unregister on component dispose |
| **Timer/scheduler** | One-shot, recurring, cron | Shared dispatcher, auto-clear |
| **Object pool** | Reuse allocations | Critical for zero-GC hot paths |
| **ID generator** | Unique IDs (entity, session, room) | Snowflake (distributed), UUID (simple) |
| **Async primitive** | Coroutine, fiber, async/await | Match language runtime |
| **Profiler** | Slow-call detection, deadlock warning | Instrument all entry points |
| **Serialization** | Binary message encoding | Zero-GC for hot paths |
| **Tracing** | Per-request trace ID | Full-link across processes |

**Decision: framework vs. custom**
- Use framework primitives if they integrate with lifecycle (auto-cleanup)
- Bring your own if you need cross-platform (client + server) or framework lacks features

---

## 4. Core Feature Modules

Build in phases. ✓ = must-have, ○ = optional.

### Phase 1: Connection & Session (✓ Required)

| Module | What it does | Key concepts |
|:---|:---|:---|
| **Connection manager** | Accept clients, heartbeat, disconnect | WebSocket/TCP server, ping/pong, timeout |
| **Session registry** | Track active sessions | Session ID, user binding, reconnection token |
| **Authentication** | Validate identity, issue tokens | JWT, device ID, social login, refresh |

### Phase 2: Message Routing (✓ Required)

| Module | What it does | Key concepts |
|:---|:---|:---|
| **Message dispatch** | Route messages to handlers | Type registry, cmd/subCmd, RPC reflection |
| **Broadcast** | Send to all/filtered clients | All, except-sender, group, single |

### Phase 3: Game Logic Pattern (✓ Required)

Your game logic layer determines the rest of the architecture. Choose one or hybrid based on game type.

#### Pattern A: Room + Matchmaker (Session-based games)

**Use for:** MOBA, FPS, battle royale, party games, card games — any game with discrete matches.

| Module | Priority | What it does | Key concepts |
|:---|:---|:---|:---|
| **Room lifecycle** | ✓ | Create, join, run, dispose sessions | State machine, seat reservation, auto-dispose |
| **Matchmaker** | ○ | Find/create rooms, party formation | Ticket queue, property matching, two-phase join |
| **State sync** | ✓ | Broadcast game state | Choose: Schema delta, Manual broadcast, or Lockstep (see Section 5) |

**State sync options for Room pattern:**
- **Schema delta:** Auto-sync with delta compression (casual, web, small rooms)
- **Manual broadcast:** Full control, custom encoding (any game type)
- **Lockstep:** Deterministic simulation, input sync (fighting games, RTS)

#### Pattern B: Scene (Persistent world)

**Use for:** MMO, sandbox, persistent world — continuous world with region sharding.

| Module | Priority | What it does | Key concepts |
|:---|:---|:---|:---|
| **Scene/Region manager** | ✓ | Manage world regions, entity authority | Region sharding, boundary handoff |
| **AOI (Area of Interest)** | ✓ | Limit data per client to nearby entities | Grid-based, radius-based, hysteresis |
| **State sync** | ✓ | Broadcast entity state | ECS snapshot, manual broadcast, delta compression |

**State sync for Scene pattern:**
- **ECS snapshot:** Serialize entity/component data, filter by AOI
- **Manual broadcast:** Custom encoding with AOI filtering
- **Delta compression:** Only changed entities/components

#### Pattern C: Stateless API (BaaS, turn-based)

**Use for:** Turn-based games, idle games, async multiplayer — no realtime simulation.

| Module | Priority | What it does | Key concepts |
|:---|:---|:---|:---|
| **Request-response API** | ✓ | Handle game actions via HTTP/gRPC | Validate, execute, persist, respond |
| **No realtime loop** | — | Client-side simulation or turn-based | Server validates results, no broadcast |

**No state sync needed.** Server responds to each request with updated state. Client applies locally.

### Phase 4: Player Data (✓ Required for all patterns)

| Module | What it does | Key concepts |
|:---|:---|:---|
| **Player data service** | Load/save player state | Key-value, optimistic lock, write-behind cache |
| **Persistence layer** | Database integration | Relational, document, ECS component store |

### Phase 5: Meta Features (○ Optional)

| Module | What it does | Key concepts |
|:---|:---|:---|
| **Leaderboards** | Ranked lists, tournaments | Best/set/increment, rank cache, cron reset |
| **Social graph** | Friends, groups, chat | Edge table, membership, message history |
| **Presence** | Online status, room location | Pub/sub streams, cross-node |

### Phase 6: Operations (○ Optional)

| Module | What it does | Key concepts |
|:---|:---|:---|
| **Admin dashboard** | Monitor, control | Web UI, metrics, profiler |
| **Hot reload** | Update without restart | Script runtime, DLL swap, config reload |

---

## 5. State Synchronization

Choose based on game type.

### Sync Approaches

| Approach | Best For | Bandwidth | Complexity |
|:---|:---|:---|:---|
| **Schema delta** | Casual, web, small rooms | Low | Low (auto) |
| **Manual broadcast** | Custom protocol, full control | Variable | Medium |
| **ECS snapshot** | Complex simulation, AOI | Medium–High | High |
| **Lockstep** | Deterministic, fighting, RTS | Low (inputs only) | High |

### Lockstep Requirements

For deterministic simulation (fighting games, RTS):
- Fixed-point math (no floats)
- Deterministic random (seeded)
- Input collection: advance only when all inputs received
- Input delay: N-frame buffer for network transmission
- Desync detection: periodic state hash comparison
- Replay: store input log, fast-forward on reconnect

### Hybrid Approach

State sync for world + lockstep for combat subsystem. Use when:
- Open world cannot be fully deterministic
- Combat requires frame-perfect fairness

### Per-Client Filtering

Limit what each client sees:
- **Property filter:** Per-field predicate (hidden cards, fog of war)
- **AOI:** Only entities within radius/grid
- **Ownership:** Only owned or visible objects

### Tick Rate Design

| Parameter | Typical Range | Notes |
|:---|:---|:---|
| Simulation rate | 10–128 Hz | Match physics needs |
| Broadcast rate | 20–60 Hz | Higher = smoother, more bandwidth |
| Input collection | 1–4 frames | Batch to reduce overhead |

Decouple simulation from broadcast: simulate at 60 Hz, broadcast at 20 Hz. Clients interpolate.

---

## 6. Room Lifecycle

### State Machine

```
Create → Wait → [Auth per client] → Join → Running → Leave → Dispose
                                              ↑           ↓
                                         Reconnect ← Disconnect
```

| State | Server Actions | Client Actions |
|:---|:---|:---|
| **Create** | Allocate, initialize, register | — |
| **Wait** | Accept joins, validate seats | Request join, auth token |
| **Auth** | Validate token, call hook | Wait |
| **Join** | Add to presence, send snapshot | Receive, initialize |
| **Running** | Process inputs, simulate, broadcast | Send inputs, apply patches |
| **Leave** | Remove, call hook, check dispose | Disconnect or reconnect |
| **Dispose** | Save state, deregister, cleanup | — |

### Seat Reservation (Two-Phase Join)

Prevents race conditions when multiple clients compete for last slot.

**Phase 1 (Matchmaker):**
- Client → Matchmaker.joinOrCreate()
- Matchmaker finds/creates room, atomically reserves seat
- Returns {roomId, sessionId, token}

**Phase 2 (Room):**
- Client → Room.connect(token)
- Room validates token, clears timeout
- Proceeds to Auth

If client never connects: timeout clears reservation.

### Reconnection

| Pattern | Mechanism | State Recovery |
|:---|:---|:---|
| **Token-based** | Issue reconnection token on join | Hold session for timeout window (60–120s) |
| **Session registry** | Persist session ID in cache | Load from cache, replay missed state |
| **Input replay** | Store all inputs since join | Full state recovery (lockstep) |

### Auto-Dispose vs. Persistent

| Mode | Trigger | Use When |
|:---|:---|:---|
| **Auto-dispose** | Last client leaves (or empty timeout) | Session games, clean resource management |
| **Persistent** | Explicit lifecycle control | Persistent world regions, scheduled events |

### Party/Lobby Lifecycle

```
Party Create → Members Join → Enter Matchmaker as group
  → Match found → Members notified → Each joins room
  → Party dissolved (or persists)
```

Key: party leader controls ready-check; matchmaker keeps party together.

---

## 7. Message Dispatch

### Dispatch Patterns

| Pattern | Mechanism | Best For |
|:---|:---|:---|
| **Type-switch** | Envelope type → switch → handler | Monolithic, fixed message set |
| **Registry map** | `onMessage(type, handler)` | Dynamic registration |
| **cmd/subCmd routing** | Two-level int route, reflection | MVC-style, auto-generated |
| **Method-ID hash** | Interface method → int ID | Type-safe, compile-time |
| **RPC reflection** | `RPC_MethodName` convention | Naming-driven |
| **Actor mailbox** | Message → Actor ID → process | Entity-centric, location-transparent |

### Broadcast Patterns

| Pattern | Use When |
|:---|:---|
| **All** | Global event (game start, countdown) |
| **Except sender** | Movement, actions visible to others |
| **Filtered subset** | Team messages, private events |
| **Group/stream** | Named groups (teams, spectators) |
| **Single** | Personal response, private state |

### Cross-Process Routing

| Pattern | Mechanism |
|:---|:---|
| **Presence IPC** | Match ID encodes node; route via pub/sub |
| **Match-ID routing** | Parse `{uuid}.{node}` from ID |
| **Broker routing** | All messages via broker; broker resolves cmd → server |
| **Actor location** | ActorLocation service maps Entity.Id → process |
| **RPC call/cast** | `Call(service, method, args)` with discovery |

### Middleware Pipeline

Intercept for cross-cutting concerns (auth, rate limit, validation, logging).

```
Message → Filter 1 (auth) → Filter 2 (rate limit) → Filter 3 (validation)
  → Handler → Filter 3 (transform) → Filter 1 (audit) → Response
```

Implementation: attribute-based, global registration, or per-handler chain.

---

## 8. Persistence

### Storage Models

Choose based on data shape. Most servers use 2–3 models.

| Model | Structure | Use When |
|:---|:---|:---|
| **Key-value** | `(collection, key, ownerId)` → JSON blob | Player saves, settings, inventory |
| **ECS component** | Entity/Component as documents | Complex simulation state, component queries |
| **Relational** | SQL tables, foreign keys | Structured data with joins: leaderboards, social, transactions |
| **Document** | Flexible schema, nested objects | Semi-structured, evolving schema |
| **Cache-aside** | Hot data in memory, cold in DB | Session state, presence, rank cache |

**Typical combination:** Relational (accounts, social, leaderboards) + key-value (player saves) + cache-aside (presence, session routing).

### Write Patterns

| Pattern | Mechanism | Risk | Use When |
|:---|:---|:---|:---|
| **Write-behind** | Mutate in-memory, flush at interval | Data loss on crash | High-frequency (position, stats) |
| **Write-through** | Immediate persist | Slower, DB bottleneck | Critical (currency, transactions) |
| **Event sourcing** | Store state changes as events | Storage growth, replay cost | Audit trails, replay, match records |
| **Single writer** | One process owns each data item | Requires routing | Prevents write conflicts |

### Optimistic Locking

Attach version field. On write: include expected version; fail if mismatch. Retry with fresh read.

Use when: concurrent writes from multiple nodes to shared objects (leaderboards, storage). Not needed for single-writer data.

### Match State Persistence

| Approach | Trigger | Notes |
|:---|:---|:---|
| **Manual save on dispose** | `onDispose()` hook | Simple; risk of data loss on crash |
| **Storage API in loop** | Explicit write at milestones | Controlled checkpoints |
| **DB component** | Auto-serialize on change | Transparent, framework-managed |
| **Input log** | Store all inputs | Enables replay; expensive for long matches |

---

## 9. Scalability

### Topology Patterns

| Topology | Coordination | State Distribution | Scaling Unit |
|:---|:---|:---|:---|
| **Single-process** | None | All in-memory | Vertical only |
| **Multi-process pub/sub** | Redis pub/sub + hash | Stateless API, stateful rooms pinned | Add nodes, rooms distributed at creation |
| **Shared-DB multi-node** | Shared DB, presence table | Stateless API, stateful matches | Add homogeneous nodes |
| **Three-tier broker** | Broker routes by cmd | External stateless, Logic stateful | Scale each tier independently |
| **Multi-fiber** | Actor location, etcd | Fiber per unit, cross-fiber messaging | Add processes, configure services |
| **Service cluster** | etcd or master, RPC | Service owns state | Add nodes, configure placement |

### Room Pinning

Rooms created on one process stay there. No live migration.

**Implications:**
- Match ID encodes hosting node (e.g., `{uuid}.{nodeName}`)
- Cross-node join: forward via IPC to hosting node
- Process crash loses all rooms; clients reconnect to new room
- Load balance at creation time (assign to least-loaded)

### Horizontal Scaling

| Service Type | Strategy |
|:---|:---|
| **Stateless** (Auth, Lobby, DB Proxy) | Add instances behind load balancer |
| **Stateful by player** (Player) | Shard by player ID (consistent hash) |
| **Stateful by room** (Room) | Shard by room ID, assign at creation |
| **Stateful by region** (Scene) | Shard by region/zone ID, fixed mapping |
| **Global** (Leaderboards, Guilds) | Single instance or active-passive HA |

**Design principle:** Push state to edges (player, room). Keep routing layer stateless. Minimize cross-process state sharing.

---

## 10. Module Writing Patterns

How to add game logic to your server. Choose the pattern that fits your architecture.

### Pattern Catalog

| Pattern | Core Concept | How You Add Logic | State Management | Message Handling |
|:---|:---|:---|:---|:---|
| **Class extension** | Extend framework base class | Override lifecycle methods | Declarative schema with auto-sync | Registry-based handler registration |
| **Plugin system** | Entry function registers extensions | Register hooks, RPC handlers, match loops | Manual via framework API | RPC registration, before/after hooks |
| **Annotation-driven** | Plain classes with metadata | Annotate classes and methods | Class fields | Framework scans and routes by metadata |
| **Data-logic separation** | Pure data + pure logic | Define data classes, write static logic functions | Data classes only | Message routing to entity by ID |
| **Interface contract** | Interface defines protocol | Implement interface methods | Class fields | Interface methods are handlers |
| **Hierarchical composition** | Tree of services/modules | Embed base, add children | Service/module fields | Naming convention for RPC methods |

### Pattern Details

#### Class Extension

**Concept:** Framework provides base class with lifecycle. You extend and override.

**Key characteristics:**
- Inheritance-based
- Lifecycle hooks: create, join, leave, dispose
- State defined with decorators or schema
- Auto state sync (delta compression)
- Handler registration via method calls

**Best for:** Small teams, fast iteration, automatic state sync.

#### Plugin System

**Concept:** Framework is complete; you add custom logic via plugins.

**Key characteristics:**
- Entry function called at startup
- Register hooks (intercept framework operations)
- Register RPC endpoints (custom logic)
- Optional match handler (game loop)
- Access framework services (storage, social, leaderboards)
- Multi-language support (compiled, scripted)

**Best for:** Full backend services + custom game logic, hot-reload.

#### Annotation-Driven

**Concept:** Plain classes, no inheritance. Framework discovers via annotations.

**Key characteristics:**
- Metadata on classes and methods
- Framework scans and builds routing table
- Methods are plain functions (input → output)
- Per-player thread safety
- Auto-generate client SDK from metadata

**Best for:** MVC background, distributed scaling, low coupling.

#### Data-Logic Separation

**Concept:** Data and logic are completely separate. Data = components, logic = systems.

**Key characteristics:**
- Data classes: pure data, no methods
- Logic functions: static methods operating on data
- Event-driven lifecycle (awake, update, destroy)
- Entity ID for message routing
- Cross-process messaging via entity location
- Hot-reload via dynamic loading

**Best for:** Complex simulation, client-server code sharing, deterministic physics.

#### Interface Contract

**Concept:** Interface defines protocol, shared between client and server.

**Key characteristics:**
- Interface as schema (no separate IDL)
- Server implements interface
- Client gets typed proxy
- Bidirectional streaming
- Group abstraction for broadcast
- Type-safe across network boundary

**Best for:** Type safety, strong tooling, RPC-centric architecture.

#### Hierarchical Composition

**Concept:** Services contain modules, modules contain sub-modules. Tree structure.

**Key characteristics:**
- Embed base service/module
- Lifecycle hooks: init, start, release
- Add child modules for organization
- Shared timer and event system in tree
- RPC via naming convention
- Optional concurrent mode

**Best for:** Flexible topology, microservices, explicit control.

### Pattern Comparison

| Concern | Class Extension | Plugin System | Annotation | Data-Logic | Interface Contract | Hierarchical |
|:---|:---|:---|:---|:---|:---|:---|
| **Coupling** | Medium (inheritance) | Low (plugin interface) | Very Low (metadata) | Very Low (pure separation) | Low (interface) | Low (composition) |
| **Testability** | Medium | High | High | High | Medium | Medium |
| **Hot-reload** | Limited | Yes (scripts) | No | Yes (dynamic load) | No | No |
| **State sync** | Automatic | Manual | Manual | Manual | Manual | Manual |
| **Learning curve** | Low | Medium | Low | High | Medium | Medium |

### Decision Guide

| Your Priority | Recommended Pattern |
|:---|:---|
| Fast iteration, automatic state sync | Class extension |
| Full backend + custom logic, hot-reload | Plugin system |
| Low coupling, plain code, distributed | Annotation-driven |
| Complex simulation, code sharing | Data-logic separation |
| Type safety, strong tooling | Interface contract |
| Flexible topology, explicit control | Hierarchical composition |
