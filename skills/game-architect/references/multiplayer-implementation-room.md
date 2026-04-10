# Room-Based Multiplayer Server Build Playbook

Build guide for small to medium realtime multiplayer games where one room or match is the main authoritative runtime owner.

Use this document for lobby games, party games, card rooms with live turns, small action matches, and instanced co-op or PvP sessions.

Use `multiplayer-server-architecture.md` for broader topology choices. Use `multiplayer-protocol.md` for message naming, state sync, reconnect, and transport rules.

---

## 1. Target Shape

Default first-production shape:

- Runtime model: **room-based realtime**
- Ownership unit: **room**
- Persistent owner: **player service**
- Deployment: **gateway + player/meta service + room service + DB/cache**
- Scaling rule: **one room pinned to one process**

This is the right default when:

- 2-50 players share one temporary match state
- match state can stay in memory during play
- fairness matters more than client freedom
- horizontal scaling should happen by adding room hosts, not by splitting one room

---

## 2. Non-Goals

Do not make first version carry these costs:

- no actor migration between room hosts
- no world-scale AOI runtime
- no distributed transaction across room and player state
- no mid-match host transfer
- no cross-room shared simulation
- no generic event bus for every internal step

If any of these become mandatory, the product is no longer a simple room server.

---

## 3. Minimal Topology

Recommended nodes:

- **Gateway**: connection, auth validation, session binding, routing, heartbeat
- **Matchmaker**: queue, seat reservation, room assignment
- **Room Service**: authoritative match state and broadcast
- **Player Service**: durable player state, inventory, rank, rewards, progression
- **DB/Cache**: persistent player/meta storage and optional room reservation cache

Default deployment profiles:

- small project: gateway + matchmaker + room in one process, player service separate
- medium project: gateway/matchmaker separate from room hosts, player service separate

Do not let gateway own gameplay state.

---

## 4. Reference Runtime Structure

Use a room service structure like this as the default reference:

```text
server/
  gateway/
    GatewaySessionHandler
    RoomRouteDispatcher
  matchmaker/
    MatchmakingService
    RoomReservationService
    ReservationRepository
  room/
    RoomDirectory
    RoomHostService
    RoomRuntimeFactory
    RoomRuntime
    PlayerSlot
    RoomCommandHandler
    RoomStateStore
    SimulationEngine
    BroadcastBuilder
    ReconnectService
    SettlementCoordinator
  player/
    PlayerServiceClient
    MatchSettlementService
```

### Main Class Responsibilities

- `MatchmakingService`: queue matching and room assignment
- `RoomReservationService`: create and validate reservation tokens
- `RoomDirectory`: map `roomId -> host/node`
- `RoomHostService`: process-local room container, create/load/dispose `RoomRuntime`
- `RoomRuntime`: authoritative room aggregate root
- `PlayerSlot`: one joined player inside the room, including ready state, reconnect token, runtime state reference
- `RoomCommandHandler`: entry for `Move`, `CastSkill`, `SubmitAction`, `Ready`, `Surrender`
- `SimulationEngine`: pure room rule execution
- `BroadcastBuilder`: convert room state changes into `Resp`, `Notify`, or state delta
- `ReconnectService`: resume binding and snapshot rebuild
- `SettlementCoordinator`: send final room result to player service and control terminal state

### Main Object Relations

- `RoomHostService` owns many `RoomRuntime`
- each `RoomRuntime` owns many `PlayerSlot`
- `RoomCommandHandler` depends on `RoomRuntime`, `SimulationEngine`, and `BroadcastBuilder`
- `SettlementCoordinator` depends on `RoomRuntime` and `PlayerServiceClient`
- `ReconnectService` depends on `RoomRuntime` and `RoomReservationService`

### Concrete Join Chain

1. `MatchmakingService` chooses `roomId`.
2. `RoomReservationService` creates `reservationId`.
3. `GatewaySessionHandler` forwards join to `RoomHostService`.
4. `RoomHostService` loads or creates `RoomRuntime`.
5. `RoomRuntime` creates `PlayerSlot`.
6. `BroadcastBuilder` produces initial room snapshot.

---

## 5. Ownership Rules

Hard rules:

- `RoomService` is the only writer of live match state.
- `PlayerService` is the only writer of durable player state.
- `Gateway` may track session and room location, but must not mutate game rules.
- `Matchmaker` may reserve seats, but must not create player state side effects.
- room logic can read player snapshots passed in at join time, but must not write inventory, currency, ranking, or progression directly.
- room end settlement is a request to `PlayerService`, not a direct DB write from room code.

Recommended runtime keys:

- room key: `roomId`
- player durable key: `playerId`
- session key: `sessionId`
- join reservation key: `reservationId`
- action idempotency key: `actionId`

---

## 6. Standard Request Flows

### Login And Session Bind

1. Client authenticates through gateway.
2. Gateway validates token with auth/player service.
3. Gateway creates `sessionId` and binds player to current connection.
4. Gateway loads minimal player session data: `playerId`, ban/version flags, reconnect eligibility.
5. Gateway returns session-ready response.

Do not load full inventory or full profile here unless lobby entry requires it.

### Matchmaking And Join

1. Client sends matchmaking request.
2. Matchmaker finds or creates a room and reserves capacity.
3. Matchmaker returns `roomId + reservationId + expireAt`.
4. Client connects or routes to the room host with reservation.
5. Gateway forwards join request to the target room.
6. Room validates reservation, version, player state, and duplicate join.
7. Room creates room-local player runtime state.
8. Room sends initial room snapshot to the joining player.
9. Room broadcasts join event to other players if needed.

This two-phase join is the default safe flow. It prevents last-slot races and simplifies reconnect.

### Gameplay Action

1. Client sends command such as `Battle_SubmitAction_Req` or `Move_Req`.
2. Gateway checks session and routes to the bound room.
3. Room validates player membership, phase, cooldown, range, and `actionId`.
4. Room applies authoritative simulation.
5. Room updates in-memory match state.
6. Room produces response, notify, or state delta.
7. Room broadcasts authoritative result to affected players.

Room code should finish the whole authoritative action before any broadcast leaves the process.

### Match Settlement

1. Room reaches terminal state.
2. Room computes final result and reward intent.
3. Room sends one settlement request to `PlayerService`.
4. `PlayerService` validates idempotency by `matchId` or settlement ID.
5. `PlayerService` writes rewards, rating, quest progress, and logs.
6. `PlayerService` returns authoritative settlement result.
7. Room sends final settlement to clients.
8. Room waits for ack or timeout, then disposes.

Do not let room write currency or ranking directly.

### Reconnect

1. Client reconnects through gateway with resume token.
2. Gateway checks reconnect window and current room binding.
3. Gateway routes resume to the room host.
4. Room rebinds the new session if player slot still exists.
5. Room sends full room snapshot or catch-up delta.
6. Old connection is invalidated.

Default reconnect policy:

- preserve room slot for a short window
- do not replay every historical action unless the game requires it
- prefer full room snapshot on resume for simpler correctness

---

## 7. Concrete Action Execution Chain

Use a concrete command path like this:

1. `GatewaySessionHandler` receives `Battle_SubmitAction_Req`.
2. `RoomRouteDispatcher` resolves `roomId -> RoomHostService`.
3. `RoomHostService` finds `RoomRuntime`.
4. `RoomCommandHandler.HandleSubmitAction()` validates `sessionId`, `playerId`, and `actionId`.
5. `SimulationEngine.ApplyAction()` mutates `RoomStateStore`.
6. `BroadcastBuilder.BuildActionResult()` creates `Resp` and `Notify`.
7. `GatewaySessionHandler` sends packets to target players.

Suggested method split:

```text
RoomCommandHandler.HandleMove()
RoomCommandHandler.HandleSubmitAction()
RoomCommandHandler.HandleReady()
SimulationEngine.ApplyMove()
SimulationEngine.ApplyBattleAction()
BroadcastBuilder.BuildStateDelta()
SettlementCoordinator.CommitSettlement()
```

This keeps transport, validation, simulation, and broadcast separate.

---

## 8. State And Persistence

Keep these states separate:

- **Room in-memory state**: positions, turn state, temporary buffs, room timers, seat state
- **Player durable state**: inventory, currencies, rank, quests, progression, mail
- **Optional room persistence**: reservation data, reconnect tokens, final settlement audit

Default persistence policy:

- during match: room state stays in memory
- on critical checkpoints: optional room snapshot only if match recovery matters
- on match end: settlement written by `PlayerService`
- on crash: unfinished room can be failed, resumed from checkpoint, or compensated

Good first-version default:

- no mid-match checkpoint
- no room recovery after host crash
- compensate only if the product stakes require it

If stakes are high, add one of these explicitly:

- round-end checkpoint
- turn-end checkpoint
- authoritative input log

---

## 9. Failure Rules

Write these rules before implementation:

- gateway disconnect does not end the match immediately
- room host crash loses in-memory room unless checkpointing exists
- settlement request must be idempotent
- duplicate action request must return same logical result or safe reject
- if `PlayerService` is unavailable at settlement time, room should move to `settlement_pending` instead of granting rewards twice
- room timeout must eventually dispose abandoned matches

Default safe choices:

- client retries are allowed only with `actionId`
- settlement retries are keyed by `matchId`
- room disposal happens only after settlement success or explicit failure state

---

## 10. Code Skeleton

Suggested project layout:

```text
server/
  gateway/
    session/
    auth/
    routing/
  matchmaker/
    queue/
    reservation/
  room/
    room_host/
    room_registry/
    room_runtime/
    room_handlers/
    room_broadcast/
    room_reconnect/
  player/
    player_api/
    progression/
    inventory/
    rating/
    settlement/
  protocol/
    realtime/
    api/
  persistence/
    db/
    cache/
    repository/
```

Responsibility split:

- `room_handlers`: parse commands and call room domain logic
- `room_runtime`: authoritative state machine
- `room_broadcast`: state delta / notify generation
- `player/settlement`: apply room result to durable state

Do not mix room simulation code into gateway handlers.

---

## 11. Build Order

Recommended implementation order:

1. Login, session bind, and version/auth rejection
2. Matchmaker reservation and room join
3. In-memory room lifecycle: create, join, leave, dispose
4. One minimal gameplay action loop
5. Room broadcast or state sync
6. Reconnect within short timeout window
7. Match settlement to player service
8. Metrics, logging, and admin tools
9. Optional recovery or checkpointing

Do not build full rating, replay, observers, bots, and tournament support before one match can run end to end.

---

## 12. Framework Fit In Practice

This server shape maps well to these framework families:

- **room-based realtime framework**: strong fit when room is the core runtime and state sync is mostly room-scoped
- **backend platform with authoritative match support**: good when the product also needs backend services, auth, social, and storage
- **typed realtime communication framework**: usable if you already own clustering and persistence design outside the communication layer

Practical rule:

- if room lifecycle and matchmaking are the core problem, start from a room framework
- if player backend is equally important, start from a backend platform and keep room logic bounded
- if you still need to invent room ownership, join flow, and settlement boundaries yourself, the framework is only transport, not architecture

---

## 13. Review Checklist

Before calling the design ready, verify:

- one room has one authoritative writer
- durable player writes never happen inside room runtime code
- join flow uses reservation, not blind direct join
- reconnect policy is explicit
- settlement is idempotent
- crash behavior is declared, not implied
- build order can produce a runnable end-to-end vertical slice early
