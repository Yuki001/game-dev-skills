# Game Server Architecture

Reference for planning game server architecture and selecting suitable framework families. This document is optimized for design work: choose the runtime model once, then map it through roles, topology, sync, recovery, and module-writing pattern.

Primary focus is authoritative online games. It also covers backend/platform services when they are part of the same product.

Complements `multiplayer-overview.md` (client/server logic split, authority model, sync style) and `multiplayer-protocol.md` (message design, serialization, heartbeat, reconnect) with server-side architecture guidance.

## 0. Server Architecture Design Flow

Use this workflow as the source of truth. Later sections are lookup tables for each step, not separate places to redefine the same runtime model.

```
Runtime Model
  -> Logical Roles & Ownership
  -> Process Topology
  -> Communication / Sync / Recovery
  -> Module Writing Pattern
  -> Final Distributed Process Architecture
```

| Step | Decide | Must Not Skip |
|:---|:---|:---|
| **Runtime Model** | Pick room, encounter, scene/world, backend/platform, or hybrid | Do not mix runtime terms casually; choose the owner of live state first |
| **Logical Roles & Ownership** | Map roles and mutable state owners | Every mutable state unit needs one writer; cross-role writes need transaction, event, lock, saga, or compensation |
| **Process Topology** | Choose how roles are hosted and routed | Preserve routing/session/location rules from the chosen topology |
| **Communication / Sync / Recovery** | Choose dispatch, sync, targeting, persistence, and recovery policy | Define private filtering, reconnect behavior, idempotency, and crash outcome where relevant |
| **Module Writing Pattern** | Choose how gameplay logic plugs into the framework | Do not assume a typed interface or plugin hook defines ownership by itself |

---

## 1. Runtime Model Decision

Define runtime model terminology here only. Later sections should reference these names instead of re-explaining them.

| Runtime Model | Best Fit | Core Ownership Unit | Typical Server Shape | Must Decide |
|:---|:---|:---|:---|:---|
| **Room-based realtime** | Match-based games, lobbies, room-owned instanced sessions | Room or match | Room process/service with matchmaking and state sync | Reservation/join flow, reconnect window, disposal rule, checkpoint/replay need |
| **Encounter/combat service** | Stateful PvE flows, turn-based combat, lightweight battle instances | Encounter, battle, or workflow instance | Stateful service instance driven by API/service calls | Action idempotency, phase validation, checkpoint frequency, reward commit timing |
| **Scene/world realtime** | Persistent worlds, region simulation, AOI-heavy games, scene-owned instances | Scene, region, scene instance, or entity shard | Scene services with routing and handoff | AOI model, region transfer, entity identity, handoff and reconnect rules |
| **Backend/platform** | Turn-based, idle, social, economy-heavy games | Player, request, or domain service | API services backed by storage | Auth, permissions, consistency, transactional boundaries, async workflow policy |
| **Hybrid** | Most commercial online games | Runtime owner plus player/meta owner | Realtime runtime plus backend platform | Which state is runtime-only, which state is durable, and how side effects cross owners |

### Runtime Selection Shortcuts

| Situation | Start With | Watch For |
|:---|:---|:---|
| 2-20 player match game | Room-based realtime + persistent backend if progression exists | Do not put durable inventory/economy only inside room state |
| Step-driven PvE battle or turn flow | Encounter/combat service + player/meta services | Deduplicate retries and commit rewards once |
| MMO, sandbox, dungeon copy, raid copy, AOI instance | Scene/world realtime | Define scene-copy ownership, transfer, reconnect, and disposal |
| Async, idle, social, leaderboard, economy-heavy game | Backend/platform | Keep validation and permission checks server-side |
| Multiple game modes with shared accounts | Hybrid | Keep runtime authority and durable player/meta ownership separate |

---

## 2. Logical Roles & Ownership

Logical roles describe both distribution responsibility and write ownership. Do not create a separate ownership model that repeats these role names.

| Role | Responsibility | Usually Owns | Must Not Own / Must Decide |
|:---|:---|:---|:---|
| **Connection/Gateway** | Accept connections, heartbeat, protocol decode, session binding | Connection/session routing state | Authenticate before durable identity binding; clean stale routing; avoid gameplay authority by default |
| **Auth** | Identity validation, token/session issuance | Auth/session credentials | Gameplay state; decide token lifetime and session handoff |
| **Matchmaker** | Queueing, property matching, room assignment | Queue state, reservations | Match state; decide reservation token, capacity race handling, timeout cleanup |
| **Player** | Durable player and meta-system authority | Profile, inventory, currency, progression | Live room/scene simulation; decide settlement API and idempotent reward writes |
| **Room** | Session gameplay authority | Match state, temporary session state | Durable account/meta data; decide join, leave, reconnect, checkpoint, disposal |
| **Encounter/Combat** | Short-lived battle or turn-flow authority | Encounter state, phase/turn state | Direct durable reward mutation without commit policy; decide duplicate action handling |
| **Scene** | Persistent world authority | Region, scene instance, scene entities | Player account state; decide AOI, transfer, identity, scene-copy lifecycle |
| **Global/Domain** | Social, guild, mail, leaderboard, economy, auction | Domain state and cross-player aggregates | Per-room simulation; decide transaction/saga/compensation boundaries |
| **Persistence/DB proxy** | Database access, cache, batching, storage policy | Cache and write queues | Business authority by default; decide flush, retry, and crash policy |

### Deployment Profiles

| Profile | Processes | When To Use | Ownership Reminder |
|:---|:---|:---|:---|
| **Minimal** | Everything embedded | Prototype, small release, low CCU | Roles may share a process but should still have clear write owners |
| **Backend-only** | Auth + API + Persistence | Turn-based, idle, social, async multiplayer | Player/domain services own durable writes |
| **Combat service** | Auth + Player + Encounter/API + Persistence | Lightweight PvE combat, card battle loops, turn workflows without room allocation | Encounter owns active battle; Player owns durable outcome |
| **Small room** | Auth + Room/API + Persistence | Small session games with limited backend complexity | Room owns match state; persistence owns only storage mechanics |
| **Standard room** | Gateway + Auth + Matchmaker + Player + Room + Persistence | Mid-scale realtime match games | Matchmaker reserves; Room validates join; Player commits durable results |
| **Persistent world** | Gateway + Auth + Player + Scene + Global + Persistence | MMO or sandbox worlds | Scene owns world state; Player/Global own durable account/domain state |
| **Full platform** | Separate gameplay and domain services | Large products with multiple game modes | Cross-role writes need explicit workflow design |

### Evolution Rule

Start from the smallest profile that fits. Split processes only when one of these becomes true:

- One role has a clearly different scaling curve.
- One role has a pressure bottleneck.
- One role needs separate failure isolation.
- One role needs independent deployment or ownership by another team.
- One role creates contention because its writes should be isolated.

---

## 3. Process Topology

Process topology is a first-class decision extracted from real server framework shapes. It decides how logical roles are hosted, routed, and scaled; it does not redefine runtime models.

| Pattern | Structure | Best For | Tradeoff | Must Decide |
|:---|:---|:---|:---|:---|
| **Single-process monolith** | All roles in one process | Prototype, LAN, early production | Fastest to build, weakest scaling/isolation | Internal role boundaries and future split point |
| **Homogeneous multi-node** | Any node handles most requests; DB-backed state | API-heavy backends, BaaS | Simple scaling, weak fit for large in-memory runtimes | Request routing, optimistic locking, shared-cache policy |
| **Gateway-Broker-Logic** | External gateway, centralized routing, protected logic servers | High connection counts, command-routed architectures | More moving parts and routing complexity | Session stickiness, route registry, broker backpressure, failure path |
| **Actor/Location cluster** | Message routing through location or actor registry | Migratable entities, world simulation | More complex operations and debugging | Location registry, migration, mailbox ordering, entity identity |
| **Service tree cluster** | Process contains services, services contain modules | Custom platforms and service-oriented backends | Flexible but easy to over-design | Service lifecycle, module boundaries, retire/drain behavior, config topology |

### Service Discovery And IPC

| Concern | Common Choices | Use When | Must Decide |
|:---|:---|:---|:---|
| **Discovery** | Static config, shared DB, distributed KV, built-in cluster registry | Depends on cluster size and dynamic scaling needs | How nodes join, leave, and discover owners |
| **Routing** | Direct RPC, broker routing, actor location, pub/sub streams | Depends on ownership style and fan-out needs | Whether routing follows role, room ID, scene ID, entity ID, or domain key |
| **Presence** | Session registry, stream registry, online-location table | Match joins, chat, parties, reconnect | Expiry, reconnect token, and stale-session cleanup |
| **Events** | In-process event bus, distributed pub/sub, domain events | Cross-system coordination | Delivery semantics, ordering need, retry and compensation policy |

---

## 4. Communication, Sync, And Recovery

These tables capture communication decisions without repeating runtime model definitions.

### Dispatch Patterns

| Pattern | Best For | Tradeoff | Must Decide |
|:---|:---|:---|:---|
| **Type switch / message registry** | Monoliths and fixed message sets | Simple but less scalable for large codebases | Versioning and unknown-message handling |
| **cmd/subCmd routing** | Command-driven servers and brokers | Efficient and explicit, less type-rich | Route ownership and permission checks per command |
| **RPC / method dispatch** | Typed service APIs and request/response systems | Good tooling, may hide protocol costs | Idempotency, timeout, retry, and authorization policy |
| **Actor mailbox** | Entity-centric ownership | Excellent isolation, more routing infrastructure | Mailbox ordering, backpressure, migration behavior |
| **Filter / middleware pipeline** | Auth, rate limit, validation, logging, audit | Great cross-cutting control, adds indirection | Which filters are boundary security, not optional decoration |

### State Synchronization Models

| Model | Best For | Strength | Weakness | Must Decide |
|:---|:---|:---|:---|:---|
| **Automatic delta/schema sync** | Small to medium rooms, fast iteration | Low implementation cost | Less control over payload design | Private fields, dirty interval, late join snapshot |
| **Manual broadcast** | Competitive action, custom protocol | Full control | More engineering work | Targeting: all, except sender, team/subset, group/stream, single target |
| **Turn/phase response sync** | Encounter services and turn workflows | Simple authoritative progression | Less suitable for high-frequency realtime state | Request idempotency, phase validation, response snapshot shape |
| **Snapshot + AOI filtering** | Persistent worlds and ECS/entity sync | Strong world modeling | Higher complexity and bandwidth | AOI range, interest set, priority, ownership/property/role filters |
| **Lockstep / deterministic input sync** | Fighting, RTS, deterministic subsystems | Low bandwidth, fairness | Determinism and recovery are hard | Deterministic RNG/math, input schedule, state hash, rollback/replay policy |
| **Replicated Scene Object Properties** | Stable scene object state | Simple to use | Limited control | Use for stable properties; use event/RPC messages for one-shot actions |

### Rate And Recovery Decisions

| Concern | Typical Choices | Must Decide |
|:---|:---|:---|
| **Simulation rate** | Fixed tick, frame-driven, turn/phase-driven | Whether simulation and broadcast rates are decoupled |
| **Broadcast rate** | Lower fixed rate, dirty interval, priority-based send | Which state can be delayed, filtered, or batched |
| **Persistence policy** | Write-through, write-behind, checkpoint, event log, input log | What can be lost on crash and what must be durable before acknowledgment |
| **Runtime recovery** | Fresh runtime, checkpoint restore, event/input replay, end-and-compensate | What reconnect sees after process crash |
| **Duplicate requests** | Action ID, sequence number, transaction key, idempotent commit | Which boundary deduplicates retries |
| **Reconnect** | Short timeout resume, registry-based resume, replay missed state, fresh join only | Resume window, token, location lookup, cleanup rule |

---

## 5. Storage Models

Storage is separate from authority. A database can store state without becoming the gameplay owner.

| Model | Best For | Notes | Must Decide |
|:---|:---|:---|:---|
| **Key-value/document** | Player saves, settings, inventory, flexible state | Good for owner-scoped blobs | Owner key, optimistic version, partial update strategy |
| **Relational** | Economy, guilds, social edges, transactions, leaderboards | Best when constraints and joins matter | Transaction boundary and contention strategy |
| **Component/entity storage** | Simulation-heavy systems, entity persistence | Fits ECS/entity ownership models | Entity identity, component versioning, load/unload policy |
| **Cache-aside / write-behind cache** | Hot data with persistent backing store | Must define flush and crash policy | Flush timing, invalidation, loss tolerance |
| **Event log / event sourcing** | Replay, audit, rebuild, match records | Strong history, higher replay cost | Snapshot cadence, replay limit, schema evolution |

---

## 6. Module Writing Patterns

Module writing is a first-class decision: it decides how game logic extends the chosen framework after runtime model and topology are known.

| Pattern | Core Idea | Best For | Weakness | Must Decide |
|:---|:---|:---|:---|:---|
| **Class extension** | Extend framework base classes and override lifecycle | Opinionated room frameworks, fast iteration | Tighter coupling to framework | Which lifecycle hooks own create/join/leave/dispose behavior |
| **Plugin system** | Register hooks, RPCs, or match handlers into a complete server | BaaS and extensible backend platforms | Framework boundaries limit architecture freedom | Hook order, permission boundary, persistence side effects |
| **Annotation / metadata driven** | Plain classes discovered through metadata | Routing-heavy and framework-managed codebases | Implicit behavior can hide control flow | Discovery rules, generated routes, ownership of handlers |
| **Data-logic separation** | Data containers plus stateless systems operating on them | ECS/entity-heavy runtime and deterministic systems | Steeper learning curve | System order, mutation authority, deterministic data access |
| **Interface contract** | Shared protocol/interface defines handlers | Typed RPC/service architectures | Usually does not define state ownership for you | Which implementation owns state and which calls are commands vs queries |
| **Hierarchical composition** | Service contains modules and child modules | Service platforms and modular backends | Less opinionated about gameplay flow | Parent/child lifecycle, module boundary, graceful retire |

### Pattern Selection Matrix

| Priority | Prefer | Avoid Assuming |
|:---|:---|:---|
| Fast iteration and built-in room lifecycle | Class extension | That room lifecycle covers durable player/meta systems |
| Full backend plus custom logic | Plugin system | That hooks are safe authority boundaries by default |
| Low coupling and framework-managed routing | Annotation / metadata driven | That hidden routing makes ownership obvious |
| Simulation purity and ownership clarity | Data-logic separation | That ECS storage alone solves networking/recovery |
| Strong typing across network boundary | Interface contract | That types define write ownership |
| Explicit composition and custom service structure | Hierarchical composition | That module hierarchy should become microservices immediately |

---

## 7. Framework Family Fit Check

This is not a new decision step. Use it only after the workflow above has already produced a runtime model, role ownership, topology, communication/recovery policy, and module-writing pattern.

| Previous Decisions Point To | Framework Family To Evaluate | Verify Before Choosing |
|:---|:---|:---|
| Room runtime + room-pinned topology + class-extension lifecycle | **Room-based realtime framework** | Durable player/meta services, join reservation, reconnect, and disposal are covered or custom-built |
| Backend/platform runtime + homogeneous API topology + plugin hooks | **Backend platform / BaaS** | Authoritative realtime gameplay is unnecessary or handled elsewhere |
| Encounter runtime + request/response dispatch + idempotent turn workflow | **Stateful workflow / encounter service stack** | Duplicate actions, checkpointing, and reward commits are explicit |
| Scene/world runtime + actor/location topology + data-logic separation | **Actor/ECS runtime** | AOI, location registry, migration, persistence bridge, and reconnect are explicit |
| Typed service contracts + realtime channels + group broadcast | **RPC-hub realtime framework** | Matchmaking, ownership model, visibility groups, and persistence are not assumed for free |
| Gateway-broker-logic topology + cmd/subCmd routing | **Action-routing / broker framework** | Session stickiness, route registry, command authorization, and broker failure paths are explicit |
| Service tree topology + hierarchical module composition | **Service tree / custom microservices** | Module lifecycle, process topology, drain/retire behavior, and failure isolation are explicit |
| Narrow scope + experienced team + missing framework fit | **Custom lightweight stack** | Lifecycle, tooling, observability, scaling support, and recovery behavior are intentionally rebuilt |
