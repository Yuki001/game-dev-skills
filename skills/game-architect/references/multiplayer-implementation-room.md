# Room-Based Multiplayer Server Template

Template for small to medium realtime multiplayer games where one room or match is the authoritative runtime owner.

Use this for lobby games, party games, room card games, small action matches, and instanced co-op or PvP. Use `multiplayer-server-architecture.md` for topology tradeoffs and `multiplayer-protocol.md` for protocol rules.

---

## 1. Fit

Default shape:

- Runtime model: **room-based realtime**
- Ownership unit: **room**
- Live state writer: **room service**
- Durable state writer: **player service**
- Scaling rule: **one room pinned to one process**

Use this template when:

- 2-50 players share one temporary match state
- match state can stay in memory during play
- fairness matters more than client freedom
- scaling is done by adding room hosts, not splitting one match

Do not use this as the primary template for:

- world-scale AOI or cross-room simulation
- actor migration between room hosts
- mid-match host transfer as a first-class feature
- distributed writes across room runtime and durable player state

---

## 2. Core Topology

Recommended nodes:

- **Gateway**: connection, auth validation, session binding, routing, heartbeat
- **Matchmaker**: queue, seat reservation, room assignment
- **Room Service**: authoritative room state, simulation, broadcast
- **Player Service**: durable player state, rewards, rank, progression
- **DB/Cache**: persistent player/meta storage and optional reservation cache

Default deployment:

- small project: gateway + matchmaker + room in one process, player service separate
- medium project: gateway/matchmaker separate from room hosts, player service separate

Hard boundary:

- gateway routes gameplay but does not own gameplay state

---

## 3. Reference Runtime Structure

Use a runtime split like this as the default reference:

```text
gateway/
  GatewaySessionHandler
  RoomRouteDispatcher
matchmaker/
  MatchmakingService
  RoomReservationService
room/
  RoomDirectory
  RoomHostService
  RoomRuntime
  PlayerSlot
  RoomCommandHandler
  SimulationEngine
  BroadcastBuilder
  ReconnectService
  SettlementCoordinator
player/
  PlayerServiceClient
```

Key responsibilities:

- `RoomHostService`: create, locate, dispose `RoomRuntime`
- `RoomRuntime`: authoritative room aggregate root
- `PlayerSlot`: one player's room-local runtime state
- `RoomCommandHandler`: transport-facing command entry
- `SimulationEngine`: rule execution on authoritative state
- `BroadcastBuilder`: convert state changes into `Resp`, `Notify`, or deltas
- `ReconnectService`: resume binding and rebuild client view
- `SettlementCoordinator`: commit match result to durable systems

Dependency direction:

- gateway -> room routing
- room handler -> room runtime + simulation + broadcast
- settlement -> player service client
- player service never depends on room runtime internals

---

## 4. Ownership And State Rules

Hard rules:

- `RoomService` is the only writer of live match state
- `PlayerService` is the only writer of durable player state
- `Matchmaker` may reserve seats but does not create player-side effects
- room logic may read player snapshot data at join time but does not write inventory, currency, ranking, or progression directly
- room end settlement is a request to `PlayerService`, not a direct DB write from room code

Recommended keys:

- `roomId`
- `playerId`
- `sessionId`
- `reservationId`
- `actionId`
- `matchId`

Keep these states separate:

- **room in-memory state**: position, turn state, buffs, timers, seats
- **player durable state**: inventory, rank, quests, progression, currency
- **optional recovery state**: reservation, reconnect token, checkpoint, settlement audit

---

## 5. Standard Flows

### Matchmaking And Join

Default safe flow:

1. client requests matchmaking
2. matchmaker chooses or creates `roomId`
3. reservation service returns `reservationId + expireAt`
4. gateway routes join request to the target room host
5. room validates reservation, membership, duplicate join, and version
6. room creates `PlayerSlot`
7. room sends initial snapshot and optional join notify

Use reservation-based two-phase join by default. It prevents last-slot races and simplifies reconnect.

### Gameplay Action

Default action path:

1. client sends command such as `Move_Req` or `Battle_SubmitAction_Req`
2. gateway validates session and routes to bound room
3. room validates player, phase, legality, cooldown, and `actionId`
4. simulation mutates authoritative room state
5. broadcast layer produces response, notify, or delta
6. gateway sends authoritative result to affected players

Rule:

- complete authoritative mutation before emitting broadcast

### Settlement

Default settlement path:

1. room reaches terminal state
2. room computes result and reward intent
3. settlement coordinator sends one request to `PlayerService`
4. `PlayerService` applies idempotent write keyed by `matchId` or settlement ID
5. room sends final settlement response to clients
6. room disposes after ack or timeout

Rule:

- room never writes durable reward or ranking data directly

### Reconnect

Default reconnect path:

1. client reconnects with resume token
2. gateway validates reconnect window and room binding
3. room rebinds session to existing `PlayerSlot`
4. room sends full snapshot or catch-up delta
5. old connection is invalidated

Recommended default:

- preserve slot for a short reconnect window
- prefer full room snapshot on resume unless replay is a product requirement

---

## 6. Failure And Recovery

Write these rules explicitly before implementation:

- gateway disconnect does not end the match immediately
- room host crash loses in-memory room unless checkpointing exists
- duplicate action requests are handled by `actionId`
- settlement is idempotent by `matchId` or settlement ID
- if `PlayerService` is unavailable, room moves to `settlement_pending` instead of granting rewards twice
- abandoned rooms must time out and dispose

Good first-production defaults:

- no mid-match checkpoint
- no host-crash recovery
- no replay-based reconnect
- compensate only if the product stakes require it

Add explicit persistence only when justified:

- round-end checkpoint
- turn-end checkpoint
- authoritative input log

---

## 7. Minimal Build Order

Recommended implementation order:

1. session bind and auth rejection
2. matchmaking reservation and room join
3. in-memory room lifecycle: create, join, leave, dispose
4. one minimal gameplay action loop
5. room broadcast or state sync
6. reconnect in a short timeout window
7. settlement to player service
8. metrics, logging, and admin tools
9. optional checkpoint or recovery

Do not build replay, observers, bots, rating variants, or tournament support before one room can run end to end.

---

## 8. Framework Fit

This template fits best with:

- **room-based realtime framework** when room lifecycle is the core runtime problem
- **backend platform with authoritative match support** when backend services are equally important
- **typed realtime communication framework** only if ownership, settlement, and persistence are designed elsewhere

Rule of thumb:

- if the framework solves transport only, you still need this room ownership template

---

## 9. Review Checklist

Before calling the design ready, verify:

- one room has one authoritative writer
- durable player writes never happen inside room runtime code
- join flow uses reservation, not blind direct join
- reconnect policy is explicit
- settlement is idempotent
- crash behavior is declared, not implied
- build order can produce a runnable vertical slice early
