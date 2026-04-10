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

Keep protocol names module-based and business-oriented.

- Message protocol: `{System}_{Action}_{Suffix}`
- RPC protocol: `{System}.{Method}` or `{System}/{Method}`
- Common suffixes: `Req`, `Resp`, `Notify`, `Event`

Examples:

```text
Item_List_Req
Item_List_Resp
Item_Change_Notify
Move_Path_Req
State_Delta_Notify
Quest.ClaimReward
Battle.SubmitTurn
```

Rules:

- Group by system, not by transport layer.
- Use domain actions such as `ClaimReward`, `SubmitTurn`, `MovePath`; avoid vague names such as `DoAction` or `Handle`.
- Separate client requests from server pushes in naming.
- Keep one naming style per protocol family and use it consistently.

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

RPC fits typed request/response APIs and low-frequency gameplay services. Do not use RPC as the only abstraction for high-frequency room sync.

Good RPC cases:

- login, auth, account binding
- system open, list, get, claim, upgrade
- turn submission or one-step battle actions
- player-data queries and mutations

Keep the RPC surface small:

- one RPC should represent one complete business action
- mutation RPC returns direct result; wider room effects go through `Notify` or state sync
- do not expose repository or raw DB structure as RPC
- when mutation changes player state, `Resp` can attach `playerDelta`

Example:

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

Use this protocol shape for long-path movement where the client needs an authoritative path plus runtime correction. For short-distance movement, prefer a simpler direct move request with position or state sync instead of a full path lifecycle.

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
