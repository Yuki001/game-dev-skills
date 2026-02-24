# Multiplayer Game Architecture

Reference for networked multiplayer game architecture decisions and system design. Focuses on client-server structure, synchronization models, distributed server components, logic distribution, and communication patterns rather than low-level networking (TCP/UDP, packet framing, encryption).

## 1. Network Topology

### Topology Selection

| Topology | Connection | Applicability | Key Trade-offs |
|:---|:---|:---|:---|
| **Dedicated Server** | Long (TCP/WebSocket) | MMO, competitive FPS, real-time action | Authoritative, anti-cheat friendly, server push; requires infrastructure, per-connection resource cost |
| **Web Server** | Short (HTTP/REST) | Turn-based, idle, casual, social, meta-game | Stateless, easy to scale, CDN-friendly; client-initiated only, no real-time push |
| **Player-Hosted** | Long (Listen Server) | Casual co-op, small PvE, LAN | Zero server cost; host advantage, NAT traversal, host migration needed |
| **Peer-to-Peer** | Unreliable (UDP) | Fighting games, 2-player sessions | Lowest latency; scales poorly ($O(N^2)$ connections), cheat-vulnerable |

### Dedicated Server (Long Connection)
- **Characteristics**: Bidirectional, real-time, server pushes state at any time.
- **Connection Method**: Reliable connection, e.g., TCP, reliable UDP, WebSocket, etc.
- **Session State**: Server maintains per-connection session in memory (player data, game state).
- **Connection Cost**: Each connection consumes resources (memory, file descriptors). Requires connection limits and graceful degradation.

### Web Server (Short Connection)
- **Characteristics**: Request-response only, stateless per request, client-initiated.
- **Client Tick Pattern**: Client periodically polls server (e.g., every 10 seconds). Server computes `elapsed = now - last_tick_time`, applies simulation, returns results. Prevents client-side time manipulation.
- **Delta Response**: Server tracks last-acknowledged state per player; responds with only changed data since last request.
- **Player Data Sync**: Player data is carried in each server response (including client request results and **Tick Response**) via **Delta Response**. Client updates player data upon receipt.
- **Auth Token**: Client includes an authentication token in each request (e.g., HTTP header) for server-side identity verification and permission checks.
- **Optimistic Update**: Client applies action locally, sends to server, server validates and returns authoritative result. Revert on rejection.
- **Batch Requests**: Group multiple actions into a single HTTP request to reduce round-trips.

### Player-Hosted
- **Characteristics**: Dual-purpose binary (client + server in one), requires discovery/lobby service, NAT traversal for LAN connectivity.
- **Dual-Purpose Binary**: The distributed executable contains both client and server; mode is selected at launch.
- **Conditional Code**: Code uses conditional branches to handle both client and server logic within the same program.
- **Discovery / Lobby Service**: Uses a discovery or lobby service to find available servers.
- **NAT Traversal**: STUN/TURN/ICE for connection establishment. Relay server as fallback.

### Peer-to-Peer
- **Characteristics**: Full mesh connection; each client establishes connections with all other clients.
- **Connection Method**: Connection does not require reliability (primarily UDP, but TCP is also possible).
- **Synchronization**: Each client continuously sends its own state to synchronize.

### Hybrid Strategy
- **Dedicated Server + Web Server**: Web server for data requests, dedicated server for real-time notifications.
- **Dedicated Server + Peer-to-Peer**: Dedicated server for user services, peer-to-peer as auxiliary for in-game synchronization.

## 2. Session Models

### A. Persistent World + Instance

For games with a shared, continuous world (MMO, sandbox).

- **Persistent World**: Seamless open world. Players enter/exit regions. World state persists across player sessions.
- **Region / Zone**: World divided into regions, each managed by a server process. Players transfer between regions.
- **Instance**: Private copies of a world area (dungeons, arenas) spawned on demand for a party/group. Instance has its own lifecycle: create → enter → play → complete → destroy.
- **Channel**: Multiple copies of the same overworld region for population balancing. Players can switch channels.

### B. Lobby + Room

For session-based games (MOBA, FPS, card games, battle royale).

- **Lobby**: Pre-game space for matchmaking, party management, social interactions.
    - **Stateless Lobby**: REST/HTTP-based. Player queries and joins via short connections.
    - **Stateful Lobby**: Persistent connection for real-time presence, chat, party state.
- **Matchmaking**: Rating-based (Elo/Glicko), rule-based, or quick-match. Separate matchmaking service feeds into room creation.
- **Party/Team**: Group of players that enter matchmaking together. Party state shared among members.
- **Room Lifecycle**: Create → Wait (join/leave) → Ready Check → Game Start → Running → End Condition → Settlement → Destroy.
- **Room State Machine**: Manages transitions and validates player actions per phase (e.g., no join during Running).
- **Settlement**: Server determines results, calculates rewards, updates rankings. Write match result to DB. Optionally store replay data (input log or key snapshots).
- **Spectator**: Separate data stream with configurable delay (anti-cheat). Receives full-state snapshots (no prediction needed).

## 3. Synchronization Models

### A. State Synchronization

Server computes authoritative state and sends updates to clients.

- **Full Snapshot**: Entire world state sent periodically. Simple but bandwidth-heavy. Suitable for small state or infrequent updates.
- **Delta Compression**: Only changed fields since last acknowledged snapshot. Essential for bandwidth optimization.
- **Dirty Flags**: Track which properties changed per tick; only serialize dirty fields.
- **Priority & Relevance**: Higher update frequency for nearby/important entities, lower for distant ones. Integrates with AOI.
- **Quantization & Bitpacking**: Reduce float precision (position, rotation) and pack small values into minimal bits.

**Client-Side Prediction** (for local player):
- Client immediately applies local input without waiting for server confirmation.
- **Server Reconciliation**: When server state arrives, compare with predicted state. If mismatch, correct smoothly.
- **Input Buffer**: Store sent-but-unconfirmed inputs. On server response, replay unconfirmed inputs on top of server-confirmed state.

**Entity Interpolation** (for remote entities):
- Display remote entities at a past state, interpolating between two received snapshots.
- **Interpolation Delay**: Typically one snapshot interval behind. Trades visual latency for smoothness.
- **Extrapolation (Dead Reckoning)**: When no new data arrives, predict forward. Risk of visual snap-back on correction.

**Lag Compensation**:
- **Server-Side Rewind**: On hit-scan, server rewinds world state to the client's perceived time, then validates.
- **Timestamp**: Client attaches local timestamp to actions; server uses it for rewind calculation.
- **Rewind Limit**: Cap maximum rewind time to prevent abuse from high-latency players.

### B. Frame Synchronization (Lockstep)

All clients execute the same inputs on the same logical frame; deterministic simulation produces identical state.

- **Deterministic Requirement**: Fixed-point math, deterministic random (seeded), consistent iteration order, platform-identical results.
- **Input Collection**: Each frame, all clients submit inputs; frame advances only when all inputs are received.
- **Input Delay**: Intentionally delay local input display by N frames to allow network transmission time.
- **Optimistic Lockstep (Rollback)**: Predict ahead using local input; if server/peer input differs, rollback and re-simulate. Reduces perceived latency. (GGPO-style)
- **Replay & Reconnect**: Replay all inputs from frame 0 to catch up (fast-forward simulation).
- **Desync Detection**: Periodic state hash comparison across clients; desync triggers resync or disconnect.

### Hybrid Strategy
- **State Sync + Lockstep Subsystem**: Core world via state sync, specific subsystems (e.g., combat resolution) via lockstep frames.

## 4. Distributed Server Architecture

### Process Roles

| Process | Responsibility | State | Scaling |
|:---|:---|:---|:---|
| **Gateway** | Client entry point, connection accept, encryption handshake, routing to Connector | Stateless | Horizontal (by connection count) |
| **Connector** | Persistent client session, protocol decode/encode, message forwarding, heartbeat | Session state | Horizontal (by connection count) |
| **Auth** | Authentication, token generation/validation, account management | Stateless | Horizontal |
| **Lobby** | Matchmaking, party management, room allocation, pre-game flow | Soft state | Horizontal |
| **Player** | Player data authority: attributes, inventory, equipment, currency, quests, achievements, and all peripheral system CRUD. Loaded on login, persists across rooms/scenes, flushed on logout | Player state | Horizontal (by player count) |
| **Game / Room** | Authoritative core gameplay logic (combat, movement, real-time simulation) for a room or match instance. Reads player data from Player process on join; writes back results on settlement | Game state | Horizontal (by room count) |
| **Scene / World** | Manages a region of persistent world, entity authority, AOI | Region state | Horizontal (by region) |
| **DB Proxy** | Database access abstraction, read cache, write batching, data serialization | Cache | Horizontal |
| **Global** | Cross-server services: rankings, guilds, auctions, mail, chat | Service state | By service type |
| **Log / Analytics** | Event collection, telemetry, monitoring, crash reporting | Stateless sink | Independent pipeline |

### Simplified Deployment Profiles

The full process list represents the maximum decomposition. Most projects should start with a simplified profile and split processes as scale demands.

| Profile | Processes | When to Use |
|:---|:---|:---|
| **Minimal (Single Process)** | **Game** (embeds Auth, Player data, DB access) | Prototyping, game jam, LAN co-op. Single binary handles everything. No horizontal scaling needed. |
| **Small Session** | **Auth**, **Game**, **DB Proxy** | Small-scale online games (indie multiplayer, card games). Auth separated for security; Game embeds player data + lobby + gameplay in one process; DB Proxy for async persistence. |
| **Standard Session** | **Gateway**, **Connector**, **Auth**, **Lobby**, **Player**, **Game**, **DB Proxy** | Mid-scale session-based games (MOBA, FPS, battle royale). Player process handles all meta-system CRUD (inventory, shop, mail, etc.) independently from Game. Game focuses on core gameplay only, reads/writes player data via Player process. |
| **Persistent World** | **Gateway**, **Connector**, **Auth**, **Player**, **Scene**, **DB Proxy**, **Global** | MMO or sandbox. Player holds all player data across region transfers. Scene handles world simulation and AOI. Global handles cross-server services (guild, auction). |
| **Full Scale** | All processes | Large MMO or platform with multiple game modes. Lobby + Player + Game + Scene coexist. Global services fully decomposed. Log/Analytics pipeline for operations. |

**Evolution Path**: Start with the simplest profile that fits. Split processes when a specific bottleneck emerges — e.g., split Player from Game when meta-system CRUD load grows independently of gameplay, split Lobby from Game when matchmaking needs independent scaling, add Gateway when connection count exceeds single-process limits, add Global when cross-server features are needed.

### Request Flow Examples

**Login Flow**:
```
Client → Gateway → Connector (session create)
    → Auth (token validate)
    → Player (create player process, load data from DB Proxy)
    → Connector (bind session) → Client (login success + player snapshot)
```

**Meta System CRUD** (inventory, shop, mail, friends, etc.):
```
Client → Connector → Player (Item_Use_Req)
    Player (validate: item exists, usable, cooldown)
    Player (execute: consume item, apply effect, update attributes)
    Player (periodic flush to DB Proxy)
    → Connector → Client (Item_Use_Resp + Item_Change_Notify)
```

**Enter Game (Lobby + Room)**:
```
Client → Connector → Lobby (matchmaking request)
    Lobby → Game (create room, assign players)
    Lobby → Connector → Client (room assigned)
Client → Connector → Game (join room)
    Game → Player (read combat-relevant data: attributes, equipment, skills)
    Game → Connector → Client (initial game state)
```

**Enter Game (Persistent World)**:
```
Client → Connector → Scene (enter region request)
    Scene → Player (read player data for scene representation)
    Scene (register player, calculate AOI)
    → Connector → Client (initial world snapshot within AOI)
```

**Gameplay Action**:
```
Client → Connector → Game/Scene (action command)
    Game/Scene (validate, execute, update game state)
    → Connector → Client(s) (state update / broadcast within AOI)
```

**Match Settlement**:
```
Game (end condition met, calculate results)
    Game → Player(s) (write rewards: currency, items, exp)
    Game → DB Proxy (write match record)
    Game → Connector → Client(s) (settlement results)
```

**Cross-Server Transfer (Region Change)**:
```
Scene A (unregister player) → Connector (rebind to Scene B)
    Scene B → Player (read player data) → Scene B (register, calculate AOI)
    Scene B → Connector → Client (new region snapshot)
```

### Inter-Process Communication
- **Message Bus**: Broker (MQ, Redis Pub/Sub) for async event distribution (announcements, cross-service notifications).
- **Direct RPC**: Point-to-point calls between processes (Connector ↔ Game, Lobby → Game). Via service discovery.
- **Shared Cache**: Redis or distributed cache for cross-process state (online status, room lists, session mapping).
- **Service Discovery**: Registry (Consul, etcd, ZooKeeper) for dynamic process lookup and health checking.

### Cluster Management
- **Boot Order**: Processes start in dependency order (DB Proxy → Auth → Global → Lobby → Player/Game/Scene → Connector → Gateway). Graceful shutdown in reverse.
- **Routing**: Central routing table maps logical targets (PlayerID, RoomID, RegionID) to physical process addresses. Connectors cache per-session bindings, updated on login/join/transfer.
- **Health & Failover**: Inter-process heartbeat detects crashes within seconds. Failed processes trigger reassignment of rooms/players to healthy instances. On Player process crash, Connector holds session while replacement loads from DB.
- **Configuration**: Cluster topology and capacity in central config service. Non-structural changes (balance, feature flags) hot-reloaded without restart.

### Cross-Server Architecture
- **Seamless World**: Region boundary handoff — when player crosses boundary, authority transfers from Scene A to Scene B.
- **Ghost Entities**: Near-boundary entities mirrored as read-only ghosts on adjacent Scene servers for AOI continuity.
- **Global Entities**: World bosses, global events managed by a dedicated Global process, broadcast to relevant Scene servers.
- **Cross-Server Interaction**: Mail, auction, guild routed through Global services. Cross-server battle uses temporary dedicated room process.

### Data Persistence & Consistency
- **Write-Behind Cache**: Game process writes to in-memory cache; async flush to DB at intervals. Fast but risk of data loss on crash.
- **Write-Through**: Every mutation immediately persists. Safe but slower. Used for critical data (currency, transactions).
- **Event Sourcing**: Store state changes as events; rebuild state by replay. Good for audit trails and replay systems.
- **Single Writer**: Each piece of data owned by exactly one process. Avoids write conflicts.
- **Optimistic Locking**: Read with version tag, write with version check. Retry on conflict.
- **Distributed Lock**: Short-TTL lock for critical sections (trade, cross-server transfers).
- **Player Data Flow**: Login (DB Proxy → Player process cache → Client snapshot) → Playing (CRUD mutations in Player process memory, periodic flush to DB Proxy) → Logout (flush all dirty data to DB, destroy Player process). Game/Scene reads from Player on join, writes results back on settlement.

### Scaling & Availability
- **Stateless Services** (Auth, Lobby, DB Proxy): Scale by adding instances behind load balancer.
- **Stateful Services** (Player, Game, Scene): Scale by sharding; Player shards by player ID, Game by room, Scene by region.
- **Consistent Hashing**: Route players/rooms to specific process instances.
- **Hot Standby**: Backup processes for critical services; failover on heartbeat timeout.
- **Session Persistence**: Store session mapping in distributed cache for Connector crash recovery.

## 5. Logic Distribution & Protocol Design

### Server vs. Client Responsibility

| Category | Server | Client |
|:---|:---|:---|
| **Core Gameplay** (combat, movement, economy) | Authoritative calculation & validation | Input capture, prediction, visual feedback |
| **AI / NPC** | Full authority | Visual interpolation only |
| **UI / Meta Systems** (inventory, shop, mail, friends) | CRUD authority, data validation | Display, local cache, optimistic UI |
| **Presentation** (animation, audio, VFX, camera) | Trigger events / sync key states | Full rendering & playback |
| **Timers / Cooldowns** | Authoritative | Local prediction for responsiveness |

### UI & Meta System Patterns (CRUD)

Most peripheral systems (inventory, shop, mail, friends, guild, settings) follow a **CRUD** pattern:
- **Server**: Data authority. Validates all mutations (add, remove, update). Stores persistent state.
- **Client**: Receives data snapshots, maintains local cache for display. Sends mutation requests, applies optimistic updates, reverts on server rejection.
- **Data Flow**: Client requests full list on system open → Server returns list → Client caches → User action triggers mutation request → Server validates & persists → Server responds with result (or pushes notification).

### Protocol Design Principles

Organize protocols by **system module**. Each system defines a set of messages following consistent naming patterns.

**Naming Convention**: `{System}_{Action}` with suffix `Req` (client request), `Resp` (server response), `Notify` (server push).

**Common Action Patterns**:

| Action | Direction | Description |
|:---|:---|:---|
| `List` | Req/Resp | Client requests a full or paginated list of entries |
| `Get` | Req/Resp | Client requests detail of a single entry |
| `Add` / `Create` | Req/Resp | Client requests to add or create an entry |
| `Remove` / `Delete` | Req/Resp | Client requests to remove or delete an entry |
| `Update` / `Modify` | Req/Resp | Client requests to change an entry's fields |
| `Use` / `Action` | Req/Resp | Client requests a domain-specific action (use item, cast skill) |
| `Change` | Notify | Server pushes partial update (single entry changed) |
| `Refresh` | Notify | Server pushes full list replacement (bulk change) |

**System Protocol Examples**:

```
-- Inventory (CRUD + Use) --
Item_List_Req / Item_List_Resp         # Open bag, get full inventory
Item_Use_Req / Item_Use_Resp           # Use a consumable
Item_Discard_Req / Item_Discard_Resp   # Drop an item
Item_Change_Notify                     # Server pushes item quantity/state change

-- Gameplay (Command, not CRUD) --
Move_Req                               # Player movement input
Skill_Cast_Req / Skill_Cast_Resp       # Cast a skill (validate cooldown, cost)
State_Sync_Notify                      # Server pushes authoritative world state
Entity_Enter_Notify / Entity_Leave_Notify  # AOI entity appear/disappear
```

**Design Principles**:
- **CRUD systems** (inventory, mail, friends, guild): Follow `List / Add / Remove / Update` pattern uniformly. Logic is validation-centric.
- **Gameplay systems** (combat, movement): Follow **Command** pattern. Client sends intent, server executes against authoritative state. Results broadcast via `Notify`.
- **Idempotency**: Mutation requests carry a unique sequence ID for deduplication on retry.
- **Error Handling**: `Resp` includes error code. Client handles: success, business error (not enough gold), system error (retry).
- **Pagination**: Large lists use cursor-based or offset pagination. `List_Req` includes `page`/`cursor`, `List_Resp` includes `has_more`.

### Area of Interest (AOI)
- **Purpose**: Limit data each client receives to entities within a relevant area.
- **Grid-Based AOI**: Divide world into cells; player subscribes to surrounding cells. $O(1)$ lookup.
- **Radius-Based AOI**: Subscribe to entities within distance threshold. Flexible but requires spatial queries.
- **Hysteresis**: Enter threshold > exit threshold to prevent rapid subscribe/unsubscribe oscillation at boundaries.
- **AOI Events**: `Entity_Enter_Notify`, `Entity_Leave_Notify`, `Entity_Update_Notify`. Client creates/destroys visual representations.
- **Priority AOI**: Closer or more important entities get higher update frequency.
- **View Layers**: Different AOI radii for different data types (large radius for minimap blips, small for full detail).

### Anti-Cheat (Architectural)
- **Principle**: Never trust client data. Server validates all gameplay-affecting inputs.
- **Command Pattern**: Client sends intentions (commands), not results. Server executes against authoritative state.
- **Input Validation**: Range checks, rate limits, sequence validation on all `Req` messages.
- **State Verification**: Periodically compare client-reported state with server state; flag large discrepancies.

## 6. Communication Patterns

### Serialization Format
- **Binary Protocol**: Custom binary `[Length][MessageID][Payload]`. Compact, fast. Standard for long-connection gameplay.
- **Protobuf / FlatBuffers**: Schema-defined serialization. Cross-language, versioned, efficient. Recommended for most projects.
- **JSON / MessagePack**: Human-readable or semi-compact. Suitable for short-connection REST APIs, debug, or non-performance-critical paths.
- **Protocol Versioning**: Include version in handshake; server supports N recent versions during rolling updates.

### RPC & Messaging
- **Request-Response**: Client sends `Req`, server replies with `Resp`. For discrete actions (use skill, buy item).
- **Server Push / Notify**: Server sends `Notify` without client request. For state updates, events, broadcasts.
- **Bidirectional RPC**: Both sides can initiate calls. Useful for complex server-to-client RPCs.
- **Stub Generation**: Auto-generate client/server stubs from protocol definition files (IDL / .proto).

### Actor Property Synchronization
- **Concept**: Each game entity has a set of replicated properties. Changes automatically synchronized to relevant clients.
- **Replication Flags**: Per-property control — `OwnerOnly`, `AllClients`, `ServerOnly`, `InitialOnly`.
- **Conditional Replication**: Property only syncs when condition is met (e.g., health only on damage).
- **Property Callbacks**: Client-side notification on replicated property change (e.g., trigger UI update).
- **Replication Priority**: Under bandwidth pressure, high-priority properties sync first.

### Heartbeat & Connection Management
- **Heartbeat**: Periodic ping/pong (e.g., every 5–15 seconds). RTT calculated for latency measurement.
- **Timeout Detection**: No response after N heartbeats → consider disconnected.
- **Graceful Disconnect**: Client sends disconnect message; server cleans up immediately.
- **Ungraceful Disconnect**: Server detects timeout; triggers reconnection window or AI takeover.
- **Reconnection**: Client stores session token; on reconnect, authenticate with token and resume. Server holds session state for a timeout window (e.g., 60–120s). In lockstep, send input history for replay catch-up.

## 7. Genre Architecture Guide

| Genre | Topology | Session | Sync Model | Key Architecture Concerns |
|:---|:---|:---|:---|:---|
| **MMO RPG** | Dedicated Server | Persistent World + Instance | State Sync + AOI | Distributed scene servers, seamless handoff, write-behind persistence, cross-server social |
| **FPS / TPS** | Dedicated Server | Lobby + Room | State Sync + Snapshot Interpolation | Tick rate (64–128Hz), server-side rewind, client prediction, lag compensation |
| **MOBA** | Dedicated Server | Lobby + Room | Frame Sync or State Sync | Deterministic engine (if frame sync), fog of war as AOI, reconnect via replay |
| **RTS** | P2P or Dedicated | Lobby + Room | Frame Sync (Lockstep) | Deterministic simulation, input delay tuning, observer mode |
| **Fighting** | P2P | Lobby + Room | Frame Sync (Rollback) | Minimal input delay, rollback + re-simulate, GGPO-style |
| **Battle Royale** | Dedicated Server | Lobby + Room (large) | State Sync + AOI | Large player count (50–100+), aggressive AOI culling, spatial partitioning |
| **Turn-Based / Card** | Web Server | Lobby + Room | Request-Response | Simple sync, strong validation, server-side game logic |
| **Idle / Casual** | Web Server | — | Client Tick + Delta | Server-side time calculation, idempotent requests, offline progress |
| **Sandbox / Survival** | Dedicated or Player-Hosted | Persistent World | State Sync + Chunk AOI | Chunk-based loading, building state persistence |
| **Mobile Social** | Web Server + Push | — | HTTP + Notify Channel | Hybrid connection, eventual consistency, notification push |
