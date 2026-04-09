# Network Protocol And Connection Architecture

Reference for the client/server boundary of online games. This document owns message shapes, protocol naming, serialization, request-response patterns, server push, heartbeat, reconnect, idempotency, and replication policy.

Use `multiplayer-architecture.md` for gameplay-side topology and sync model selection. Use `multiplayer-server.md` for service topology, ownership, deployment, persistence, and recovery policy.

---

## 1. Scope

Use this document when the question is:

- How should messages be organized?
- How should client/server requests and pushes be named?
- Which serialization format fits the system?
- How should heartbeat, timeout, reconnect, and deduplication work?

---

## 2. Message Categories

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

---

## 3. Naming Conventions

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

## 4. CRUD Versus Command Protocols

### CRUD-Oriented Systems

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

### Command-Oriented Systems

Good for movement, combat, interaction, and turn submission.

Rules:

- Client sends intent.
- Server validates and executes.
- Result returns as response, notify, or replicated state.
- Do not model gameplay commands as generic CRUD updates.

---

## 5. Serialization And Versioning

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

---

## 6. Delivery Patterns

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

---

## 7. Replication Policy

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

---

## 8. Idempotency And Ordering

### Idempotency

Mutation and action requests should usually carry a client-generated sequence or action ID.

Use it for:

- retry deduplication
- reconnect recovery
- double-submit protection
- async confirmation matching

### Ordering

Define ordering rules explicitly:

- per-connection in-order only
- per-entity or per-room ordering
- unordered but sequence-stamped snapshots

Do not rely on handler implementation details to define protocol order.

---

## 9. Error Model

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

---

## 10. Heartbeat, Timeout, And Reconnect

### Heartbeat

- Use periodic ping/pong for long-lived sessions.
- Measure RTT and track timeout budget.
- Timeout after multiple missed heartbeats, not a single miss.

### Disconnect Handling

- **Graceful disconnect**: client declares exit; cleanup can happen immediately.
- **Ungraceful disconnect**: timeout-driven cleanup with reconnect window.

### Reconnect

Typical reconnect policy:

1. client keeps session or resume token
2. client reconnects and reauthenticates
3. server validates token and room or scene binding
4. server restores session or rejects resume
5. client receives delta catch-up, snapshot, or replay window

Define reconnect window explicitly. Do not leave it implicit.

---

## 11. Short-Connection API Patterns

For web/API multiplayer or meta systems:

- authenticate every request with token or session credential
- batch related actions when latency matters
- use optimistic UI only for reversible changes
- server should compute elapsed time for idle or offline progress
- return deltas when payload size matters

---

## 12. What To Read Next

- Read `multiplayer-architecture.md` for topology choice, sync model, AOI, and genre fit.
- Read `multiplayer-server.md` for process roles, deployment, ownership, persistence, and recovery.
