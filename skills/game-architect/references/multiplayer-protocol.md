# Network Protocol And Connection Architecture

Reference for the client/server boundary of online games. This document owns message shapes, protocol naming, serialization, request-response patterns, server push, heartbeat, reconnect, idempotency, and replication policy.

Use `multiplayer-overview.md` for gameplay-side authority split and sync model selection. Use `multiplayer-server-architecture.md` for service topology, ownership, deployment, persistence, and recovery policy.

---

## 1. Scope

Use this document when the question is:

- How should messages be organized?
- How should client/server requests and pushes be named?
- Which serialization format fits the system?
- How should heartbeat, timeout, reconnect, and deduplication work?

---

## 2. Protocol Overview

### Message Categories

| Category | Direction | Purpose |
|:---|:---|:---|
| **Req / Resp** | client -> server -> client | discrete actions and queries |
| **Notify** | server -> client | pushes, broadcasts, state changes |
| **Event** | internal or cross-service | async backend coordination |
| **Snapshot / Delta** | server -> client | replicated game state |
| **Command** | client -> server | intent for authoritative execution |

Rules:

- Gameplay input should usually be a **command**.
- CRUD systems usually fit **Req / Resp + Notify**.
- Large live state should use **snapshot or delta**, not ad hoc field spam.
- Internal service events should not leak directly into public client protocol.

### Naming Conventions

Use stable module-based names.

Recommended pattern:

`{System}_{Action}_{Suffix}`

Common suffixes:

- `Req`
- `Resp`
- `Notify`
- `Event`

Examples:

```text
Item_List_Req
Item_List_Resp
Item_Change_Notify
Move_Req
Skill_Cast_Req
Skill_Cast_Resp
State_Sync_Notify
```

Rules:

- Group by system, not by transport.
- Keep action names semantic and domain-specific.
- Separate client-requested actions from server-pushed updates.
- Keep naming consistent across modules.

---

## 3. CRUD And RPC Protocols

### CRUD Versus Command Protocols

#### CRUD-Oriented Systems

Good for inventory, mail, friends, guild, settings, and shop.

Common actions:

- `List`
- `Get`
- `Create` / `Add`
- `Update` / `Modify`
- `Delete` / `Remove`
- `Change` notify
- `Refresh` notify

Typical flow:

`open system -> request list -> cache locally -> send mutation -> server validates -> response + change notify`

#### Command-Oriented Systems

Good for movement, combat, interaction, and turn submission.

Rules:

- Client sends intent.
- Server validates and executes.
- Result returns as response, notify, or replicated state.
- Do not model gameplay commands as generic CRUD updates.

### RPC Interface Design

RPC is useful for typed request/response APIs, backend-style gameplay services, and short-connection systems. It is less suitable as the only abstraction for high-frequency room sync.

Use RPC for:

- login, auth, account binding
- player data queries and mutations
- turn submission
- encounter or battle step progression
- system open, list, get, claim, upgrade, compose

Do not use one generic RPC style for everything. Distinguish:

- **query RPC**: no mutation, returns full result or page data
- **command RPC**: performs authoritative mutation
- **open/init RPC**: returns initial module snapshot
- **action RPC**: one gameplay step, often followed by delta or notify

#### RPC Naming

Recommended naming styles:

- `{System}.{Method}`
- `{System}/{Method}`

Examples:

```text
Player.GetProfile
Item.List
Item.Use
Quest.ClaimReward
Battle.SubmitTurn
System.Open
```

Rules:

- method name should describe business meaning, not transport behavior
- do not mix `GetData`, `DoAction`, `HandleXxx` style names in one API set
- query and mutation methods should be visually distinguishable
- one method should map to one stable business capability

#### RPC Request And Response Shape

Recommended request fields:

- auth/session context
- request payload
- request ID or sequence when deduplication matters
- client version or feature flag when compatibility matters

Recommended response fields:

- result payload
- stable error code
- attached player delta when the method mutates player state
- server time when client cache or timer display depends on it

Example shape:

```text
Quest.ClaimRewardReq {
  questId
  reqId
}

Quest.ClaimRewardResp {
  code
  rewardList
  playerDelta
}
```

#### RPC Boundary Rules

- RPC handler should express one complete business action, not expose internal repository operations
- RPC should not return raw DB model shape directly to client
- one mutation RPC should produce one clear authoritative result
- when mutation causes broad runtime changes, RPC response can stay small and let notify/state sync carry the shared result
- system open RPC can return module-level full snapshot, but later updates should prefer delta or notify

#### RPC And Notify Coordination

Use this default split:

- requester gets direct `Resp`
- other affected clients get `Notify` or state sync
- requester may also receive the same notify if client state handling needs one unified path

Typical examples:

- `Item.Use` -> requester gets `Resp + playerDelta`
- `Battle.SubmitTurn` -> requester gets `Resp`; turn result goes by battle notify or state sync
- `System.Open` -> requester gets module full snapshot; later changes go through delta/notify

### Short-Connection API Patterns

For web/API multiplayer or meta systems:

- authenticate every request with token or session credential
- batch related actions when latency matters
- use optimistic UI only for reversible changes
- server should compute elapsed time for idle or offline progress
- return deltas when payload size matters

#### Player Data Synchronization In Short-Connection Services

In short-connection systems, player data synchronization should use a **client tick + attached delta** pattern.

Rules:

- On first login, server sends a **full snapshot** for the key systems needed to enter the game.
- Other modules can be loaded later through `system open`, which may return a module-level full list or full snapshot.
- After initialization, player data should sync mainly through **delta response**.
- Client periodically calls a **Tick API**; `Tick Response` returns authoritative player-data changes since the last sync point.
- Every normal business response should also attach the player-data delta caused by that request.
- Client updates local player cache only from server responses.
- If client state is invalid or too old, server should return a **full refresh** instead of a delta.

Typical flows:

- `login -> full snapshot for key systems`
- `system open -> module full list / full snapshot`
- `Tick -> player delta`
- `business request -> response + attached player delta`

Notes:

- Tick is client-initiated polling, not server push.
- Tick does not require the handler to run simulation steps; it only needs to return authoritative changes already produced on the server side.
- For time-based systems, `elapsed = now - last_tick_time` is one possible server-side rule, not a required Tick step.
- If one request changes multiple player modules, consolidate them into one attached delta.

---

## 4. Game Logic Protocols

### State Sync Protocol

When state is replicated, define policy per field or entity type.

Common flags:

- `OwnerOnly`
- `AllClients`
- `InitialOnly`
- `ServerOnly`
- conditional replication

Priorities:

- Critical gameplay state first
- Nearby and relevant entities first
- Cosmetic data last

Do not replicate every field automatically without an explicit visibility rule.

State sync should use explicit message families instead of mixing spawn, movement, and attribute changes into one generic notify.

Common message set:

- `State_Full_Notify`
- `State_Delta_Notify`
- `Entity_Add_Notify`
- `Entity_Remove_Notify`
- `Entity_Move_Notify`
- `Entity_Attr_Sync_Notify`

Recommended payload structure:

- sync tick or sequence
- entity ID
- entity type or template ID when needed
- changed component or field set
- server timestamp when interpolation or correction needs it

Typical use:

- first enter scene or full refresh -> `State_Full_Notify`
- normal runtime update -> `State_Delta_Notify`
- one entity enters interest set -> `Entity_Add_Notify`
- one entity leaves interest set -> `Entity_Remove_Notify`
- one entity position/path changes -> `Entity_Move_Notify`
- one entity stats or flags change -> `Entity_Attr_Sync_Notify`

### Attribute Sync Design

Attribute sync is for stable replicated properties, not one-shot gameplay events.

Good candidates:

- hp, mp, shield
- level, faction, title
- move speed, attack speed
- alive/dead state
- interactable flags
- animation or stance state when it affects gameplay view

Recommended rules:

- send only changed attributes, not whole entity state every time
- use attribute IDs or fixed field schema instead of free-form maps in hot paths
- include current value, not only delta, when late join or correction must be easy to apply
- separate owner-only attributes from public attributes
- use RPC/event notify for one-shot actions such as skill cast start, hit confirm, or loot pickup

Example shape:

```text
Entity_Attr_Sync_Notify {
  seq
  entityId
  attrs: [
    { attrId, value },
    { attrId, value }
  ]
}
```

### AOI Enter And Leave View

AOI needs explicit enter/leave protocol. Do not rely on client inference from missing updates.

Common message set:

- `View_Enter_Notify`
- `View_Leave_Notify`
- `View_Batch_Enter_Notify`
- `View_Batch_Leave_Notify`

Recommended rules:

- enter message should carry enough spawn state for immediate local creation
- leave message should include reason when gameplay needs it, such as out-of-range, despawn, death, stealth, or transfer
- batch enter/leave is usually better for large AOI boundary changes
- if an entity leaves and re-enters quickly, ordering must still be unambiguous by sequence or tick

Example shape:

```text
View_Enter_Notify {
  seq
  entities: [
    { entityId, typeId, pos, dir, attrs, components }
  ]
}

View_Leave_Notify {
  seq
  entityIds: [ ... ]
}
```

### Path Moving Protocol

Path moving usually has two different protocol shapes:

- **client path finding**: client computes a candidate path and sends it to server for validation
- **server path finding**: client sends move target, and server computes the authoritative path

Both modes usually still use the same runtime sync stages:

- one **path start** message with the full accepted path
- periodic **position correction / sync** messages during movement
- one **arrive / stop** message when movement ends

This is better than sending raw transform spam every frame, and it gives the client a stable path to follow while still allowing server correction.

Naming boundary:

- `Move_*` means a client control request
- `Entity_*` means server-sent authoritative movement state for an entity in the world view

So `Move_Path_Req` is "I want to move", while `Entity_Path_Start_Notify` is "this entity is now moving along this authoritative path".
`Move_Path_PosSync_Req` is a client-initiated movement progress sync used for validation or correction during long path movement.

Common message set:

- `Move_Path_Req`
- `Move_Path_Pos_Sync_Req`
- `Move_Path_Arrive_Req`
- `Entity_Path_Start_Notify`
- `Entity_Pos_Sync_Notify`
- `Entity_Arrive_Notify`

### Lockstep Protocol

Lockstep or rollback protocols should exchange input frames, not world-state snapshots as the primary authority path.

Common message set:

- `Frame_Input_Req`
- `Frame_Input_Notify`
- `Frame_All_Inputs_Notify`
- `Frame_Advance_Notify`
- `Frame_Hash_Notify`
- `Rollback_Notify`

Recommended fields:

- frame number
- player ID
- input bits or command payload
- local input delay or readiness when needed
- state hash every N frames for desync detection

Rules:

- every input packet must carry frame index
- duplicate or late input handling must be explicit
- missing input policy must be explicit: wait, predict, timeout default, or drop player
- rollback protocol should define confirmed frame, predicted frame, and resimulate range
- state hash compare should be periodic, not only after desync is obvious

Example shape:

```text
Frame_Input_Notify {
  frame
  inputs: [
    { playerId, input }
  ]
}

Frame_Hash_Notify {
  frame
  hash
}
```

---

## 5. Other Protocol Concerns

### Serialization And Versioning

| Format | Best Fit | Trade-off |
|:---|:---|:---|
| **Binary custom** | performance-critical realtime | most compact, highest custom cost |
| **Protobuf / FlatBuffers** | most long-connection game protocols | efficient, versionable, cross-language |
| **JSON / MessagePack** | APIs, tooling, debug, low-frequency paths | easier to inspect, less compact |

Rules:

- Prefer schema-defined formats for long-lived protocols.
- Include protocol version in handshake or session setup.
- Support a rolling compatibility window during updates.
- Reserve fields instead of reusing old meaning.

### Delivery Patterns

| Pattern | Use When |
|:---|:---|
| **Request / response** | discrete action with direct result |
| **Server push / notify** | state changes, room events, broadcasts |
| **Broadcast to group** | room, party, team, spectator stream |
| **Single target** | private response, correction, inventory data |
| **Filtered push** | hidden info, fog of war, role-based view |

Rules:

- Broadcast by visibility policy, not by convenience.
- Separate private data from shared room data.
- Prefer group abstractions for room, team, and spectator fan-out.

### Idempotency And Ordering

#### Idempotency

Mutation and action requests should usually carry a client-generated sequence or action ID.

Use it for:

- retry deduplication
- reconnect recovery
- double-submit protection
- async confirmation matching

#### Ordering

Define ordering rules explicitly:

- per-connection in-order only
- per-entity or per-room ordering
- unordered but sequence-stamped snapshots

Do not rely on handler implementation details to define protocol order.

### Error Model

Each `Resp` should have a stable error contract.

Recommended buckets:

- success
- business rule error
- auth or permission error
- rate-limit or duplicate error
- temporary system error
- version or protocol error

Rules:

- Keep error codes stable and machine-readable.
- Do not overload transport disconnect as business rejection.
- Separate retryable failures from final validation failures.

### Heartbeat, Timeout, And Reconnect

#### Heartbeat

- Use periodic ping/pong for long-lived sessions.
- Measure RTT and track timeout budget.
- Timeout after multiple missed heartbeats, not a single miss.

#### Disconnect Handling

- **Graceful disconnect**: client declares exit; cleanup can happen immediately.
- **Ungraceful disconnect**: timeout-driven cleanup with reconnect window.

#### Reconnect

Typical reconnect policy:

1. client keeps session or resume token
2. client reconnects and reauthenticates
3. server validates token and room or scene binding
4. server restores session or rejects resume
5. client receives delta catch-up, snapshot, or replay window

Define reconnect window explicitly. Do not leave it implicit.

---

## 6. What To Read Next

- Read `multiplayer-overview.md` for gameplay-side authority split and sync model selection.
- Read `multiplayer-server-architecture.md` for process roles, deployment, ownership, persistence, and recovery.
