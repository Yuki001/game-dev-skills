# Room Runtime Implementation Playbook

Runtime-specific playbook for small to medium realtime games where one room or match is the authoritative live-state owner.

Use `multiplayer-server-architecture.md` for architecture decisions, `multiplayer-implementation-common.md` for shared infrastructure, and `multiplayer-protocol.md` for message and reconnect protocol rules.

---

## 1. Purpose And Fit

Use this playbook for lobby games, party games, room card games, small action matches, and instanced co-op or PvP where temporary match state is owned by a room runtime.

Default shape:

- Runtime model: **room-based realtime**
- Ownership unit: **room or match**
- Live state writer: **room runtime**
- Durable state writer: **player/meta service**
- Scaling rule: **one active room owner at a time**

Do not use this as the primary template for world-scale AOI, region handoff, actor migration, or long-lived spatial simulation.

---

## 2. Key Objects

| Object | Owns | Talks To | Must Not Do |
|:---|:---|:---|:---|
| `RoomHostService` | create, locate, retire, and dispose room runtimes | matchmaker, gateway, room directory | own durable player/meta state |
| `RoomRuntime` | authoritative match state and lifecycle | command handler, simulation, reconnect, settlement | write inventory, currency, rank, or account state directly |
| `PlayerSlot` | room-local player state, seat, readiness, connection binding | room runtime, reconnect service | become durable player profile |
| `RoomCommandHandler` | transport-facing room command entry | gateway, room runtime, simulation engine | mutate state before validation |
| `SimulationEngine` | authoritative rule execution | room runtime, command handler | trust client result state |
| `BroadcastBuilder` | response, notify, delta, and filtered fan-out payloads | room runtime, gateway | reveal private state or send before mutation is complete |
| `ReconnectService` | resume token, slot rebinding, snapshot rebuild | gateway, room runtime, session manager | recreate room authority from client memory |
| `SettlementCoordinator` | terminal result commit request | room runtime, player service | write durable rewards directly or commit twice |
| `RoomReservationService` | reservation ID, capacity hold, join expiry | matchmaker, room runtime | create player-side effects |

---

## 3. Core Flows

### Join

1. client requests matchmaking or direct room entry
2. matchmaker chooses or creates `roomId`
3. reservation service returns `reservationId + expireAt`
4. gateway routes join to the current room owner
5. room validates reservation, membership, duplicate join, and version
6. room creates or rebinds `PlayerSlot`
7. room sends initial snapshot and optional join notify

Use reservation-based join by default when capacity, seats, or last-slot races matter.

### Gameplay Action

1. client sends command with `roomId`, `playerId`, and `actionId` where needed
2. gateway validates session and routes to the room owner
3. room validates player, phase, legality, cooldown, and duplicate action
4. simulation mutates authoritative room state
5. broadcast builder creates response, notify, or delta for affected targets
6. gateway sends authoritative result

Complete authoritative mutation before emitting broadcast.

### Reconnect

1. client reconnects with resume token
2. gateway validates session and reconnect window
3. room rebinds new connection to existing `PlayerSlot`
4. room sends full snapshot or catch-up delta
5. old connection is invalidated

Prefer a full room snapshot on resume unless replay is a product requirement.

### Settlement

1. room reaches terminal state
2. room computes result and reward intent
3. settlement coordinator sends one idempotent request to player/meta service
4. player/meta service writes durable result by `matchId` or settlement ID
5. room sends final result and disposes after ack or timeout policy

Room runtime never writes durable reward, rank, or inventory state directly.

---

## 4. Failure Rules

Write these rules explicitly before implementation:

- gateway disconnect does not end the match immediately
- room host crash loses in-memory room state unless checkpointing exists
- duplicate action requests are handled by `actionId` when actions are retryable
- settlement is idempotent by `matchId` or settlement ID
- if player/meta service is unavailable, room moves to `settlement_pending` or declared failure state
- abandoned rooms time out and dispose
- private state is filtered before send, not hidden only by client UI

Good first-production defaults:

- no mid-match checkpoint
- no host-crash recovery
- no replay-based reconnect
- compensate only if product stakes require it

---

## 5. Minimal Build Order

Recommended order:

1. session bind and auth rejection through common gateway infrastructure
2. in-memory room lifecycle: create, join, leave, dispose
3. reservation-based join when seats or capacity matter
4. one minimal gameplay action loop
5. response/notify or state-delta broadcast
6. reconnect in a short timeout window
7. settlement to player/meta service
8. logs, metrics, room inspection, and forced close
9. optional checkpoint or recovery only when justified

Do not build replay, observers, bots, rating variants, tournament support, or dynamic room migration before one room can run end to end.

---

## 6. Review Checklist

Before calling a room design ready, verify:

- one room has one active authoritative writer
- durable player writes never happen inside room runtime code
- join flow uses reservation when capacity races matter
- reconnect policy is explicit
- settlement is idempotent and single-path
- crash behavior is declared, not implied
- private state is filtered before send
- build order produces a runnable vertical slice early
