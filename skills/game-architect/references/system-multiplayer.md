# Multiplayer Game Architecture

Reference for multiplayer gameplay architecture. This document is scoped to gameplay-facing decisions: topology, session shape, sync model, client/server responsibility, AOI, and genre fit.

It does not own detailed server process decomposition, deployment, storage, or recovery policy. Read `system-server.md` for server architecture. Read `system-network-protocol.md` for protocol design, serialization, heartbeat, and reconnect rules.

---

## 1. Scope

Use this document when the question is:

- How should multiplayer gameplay be split between client and server?
- What session model fits the game?
- Which synchronization model should the game use?
- What should be authoritative, predicted, interpolated, or hidden?

---

## 2. Topology Selection

| Topology | Best Fit | Main Trade-offs |
|:---|:---|:---|
| **Dedicated Server** | Competitive realtime, MMO, co-op with anti-cheat needs | Strong authority; needs server infra |
| **Web/API Server** | Turn-based, idle, social, meta progression | Easy scaling; weak realtime interaction |
| **Player-Hosted** | Small co-op, LAN, survival with low server budget | Cheap; host advantage and migration issues |
| **Peer-to-Peer** | 1v1 fighters, small deterministic sessions | Low latency; cheat risk and poor scale |
| **Hybrid** | Products with both meta backend and live runtime | More moving parts; often the commercial default |

Rules:

- Prefer **dedicated server** if fairness or shared realtime simulation matters.
- Prefer **web/API** if gameplay is request/response, timer-based, or mostly CRUD.
- Prefer **player-hosted** only when infra cost matters more than fairness.
- Prefer **P2P** only for low player count and strong determinism.
- Use **hybrid** when meta progression and live simulation clearly separate.

---

## 3. Session Models

### Persistent World + Instance

Best for MMO, sandbox, survival, and shared world games.

- **Persistent world**: state survives player sessions.
- **Region / zone**: world partition for runtime ownership.
- **Instance**: private copy created on demand.
- **Channel / shard**: multiple copies for population control.

Key questions:

- What unit owns the player while moving?
- When does transfer happen?
- What is global versus per-instance?
- Are instances disposable, resumable, or checkpointed?

### Lobby + Room

Best for match-based games such as FPS, MOBA, and battle royale.

- **Lobby**: queue, party, readiness, social flow.
- **Matchmaking**: finds or creates a room.
- **Room**: temporary owner of match simulation.
- **Settlement**: authoritative end result and reward writeback.
- **Spectator**: delayed or filtered read-only view.

Typical lifecycle:

`Create -> Wait -> Ready/Reserve -> Start -> Running -> End -> Settlement -> Destroy`

### Async / Turn Workflow

Best for async PvP, card battles, and turn flows without continuous presence.

- Client submits a turn or action.
- Server validates and advances authoritative state.
- Opponent receives updated state later or via push.

---

## 4. Synchronization Models

### State Sync

Server computes authoritative state and sends updates to clients.

Best for action games, shared worlds, and AOI-heavy simulation.

Core techniques:

- **Full snapshot**: simple, bandwidth-heavy
- **Delta snapshot**: changed fields only
- **Dirty flags**: track modified state
- **Priority / relevance**: important entities update more often
- **Quantization**: compress precision where acceptable

Client smoothing:

- **Prediction** for the local player
- **Reconciliation** when authoritative state arrives
- **Interpolation** for remote entities
- **Extrapolation / dead reckoning** for short gaps

Latency handling:

- **Server rewind** for hitscan validation
- **Timestamped commands** for lag compensation
- **Rewind cap** to limit abuse

### Lockstep / Frame Sync

Clients exchange inputs and run the same deterministic simulation.

Best for RTS, fighting games, and deterministic subsystems.

Requirements:

- deterministic math and RNG
- fixed simulation order
- explicit input scheduling policy
- desync detection and recovery plan

Variants:

- **Strict lockstep**: wait for all inputs
- **Delayed execution**: intentional input delay
- **Rollback**: predict, then rewind and resimulate

### Hybrid Sync

Use different sync models for different subsystems when one model does not fit the whole game.

---

## 5. Logic Distribution

| Concern | Server | Client |
|:---|:---|:---|
| **Core gameplay** | validation and final result | input capture and presentation |
| **Movement / combat** | authoritative simulation or validation | prediction and interpolation |
| **Meta systems** | CRUD authority and persistence | display, cache, optimistic UI |
| **AI / NPC** | full authority | presentation only |
| **VFX / audio / camera** | trigger or replicate minimal state | full playback and rendering |
| **Cooldowns / timers** | final source of truth | local display and short prediction |

Rules:

- Client should send **intent**, not trusted outcome.
- Server should own any result affecting fairness, economy, ranking, or shared state.
- Separate long-lived player/meta state from room or scene runtime state.
- Do not force gameplay actions into CRUD semantics. "Cast skill" is a command.

---

## 6. AOI And Visibility

AOI is the main bandwidth and interest-filtering mechanism for shared spaces.

| Model | Best Fit | Trade-off |
|:---|:---|:---|
| **Grid / cell AOI** | large worlds | coarser boundaries |
| **Radius AOI** | flexible spaces | more spatial query cost |
| **Chunk AOI** | survival, voxel, building games | streaming seam complexity |
| **Layered AOI** | minimap, fog, spectator layers | more rules to maintain |

Rules:

- Use different radii for different data classes when useful.
- Add hysteresis so objects do not flap near boundaries.
- Prioritize updates by distance, importance, and ownership relevance.
- Treat spectator and replay views as separate visibility policies.

---

## 7. Anti-Cheat Architecture

- Never trust client-reported gameplay results.
- Validate movement range, action rate, cooldown legality, and resource use.
- Prefer authoritative commands over client-submitted outcomes.
- Make lag compensation rules explicit instead of trusting latency claims.
- Delay or filter spectator data when competitive integrity matters.

---

## 8. Genre Guide

| Genre | Typical Topology | Session Shape | Sync Model | Main Focus |
|:---|:---|:---|:---|:---|
| **MMO RPG** | Dedicated server | Persistent world + instance | State sync + AOI | region ownership and handoff |
| **FPS / TPS** | Dedicated server | Lobby + room | Snapshot state sync | prediction, rewind, hit validation |
| **MOBA** | Dedicated server | Lobby + room | State sync or deterministic subsystem | team visibility and fairness |
| **RTS** | Dedicated or P2P | Lobby + room | Lockstep | determinism and replay |
| **Fighting** | P2P or relay-backed | Lobby + room | Rollback lockstep | input delay and rollback budget |
| **Battle Royale** | Dedicated server | Large room | State sync + AOI | aggressive culling and bandwidth shaping |
| **Turn-based / card** | Web/API or lightweight realtime | Room or async workflow | Request/response or turn sync | validation and persistence |
| **Idle / casual** | Web/API | Async progression | Server-side time calculation | anti-time-cheat and offline progress |
| **Sandbox / survival** | Dedicated or player-hosted | Persistent world | State sync + chunk AOI | building persistence and migration |

---

## 9. What To Read Next

- Read `system-server.md` for process roles, deployment profile, ownership, persistence, and framework family guidance.
- Read `system-network-protocol.md` for message design, serialization, request/response rules, heartbeat, reconnect, and replication policy.
