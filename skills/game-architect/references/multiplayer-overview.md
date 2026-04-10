# Multiplayer Game Architecture

Reference for multiplayer gameplay architecture. This document is scoped to gameplay-side logic distribution: what belongs on client, what belongs on server, what must be authoritative, and what synchronization style each subsystem should use.

It does not own server process topology, deployment, persistence, recovery, or framework selection. Read `multiplayer-server-architecture.md` for server architecture, server-side module boundaries, and lifecycle design. Read `multiplayer-protocol.md` for protocol design, serialization, heartbeat, reconnect, and sync transport rules.

---

## 1. Scope

Use this document when the question is:

- How should multiplayer gameplay be split between client and server?
- Which systems must be authoritative?
- What should be predicted, interpolated, delayed, or hidden?
- Which synchronization style fits each gameplay subsystem?

---

## 2. Core Principle

Design multiplayer gameplay around authority first, not around rendering or transport.

- Client owns input, presentation, local feel, and temporary prediction.
- Server owns shared truth, fairness, validation, and any result that changes persistent or competitive state.
- The same subsystem can use different rules for local view and authoritative result.
- Do not let transport style decide gameplay ownership. Decide authority first, then pick protocol and server shape.

---

## 3. Client And Server Responsibility Split

| Concern | Server | Client |
|:---|:---|:---|
| **Core gameplay rules** | validation and final result | input capture and presentation |
| **Movement / combat** | authoritative simulation or validation | prediction, interpolation, correction display |
| **Meta systems** | authority and persistence | display, cache, optimistic UI |
| **AI / NPC** | full authority | presentation only |
| **World state** | shared truth and visibility rules | local rendering and smoothing |
| **VFX / audio / camera** | minimal triggers or replicated state | full playback and rendering |
| **Cooldowns / timers** | final source of truth | local display and short prediction |
| **Hidden information** | authority and filtering | only visible subset |

Rules:

- Client should send **intent**, not trusted outcome.
- Server should own any result affecting fairness, economy, ranking, or shared state.
- Separate long-lived player/meta state from temporary room or scene runtime state.
- Do not force gameplay actions into CRUD semantics. `CastSkill`, `Move`, and `UseItem` are commands.

---

## 4. Authority Patterns

| Pattern | Use For | Notes |
|:---|:---|:---|
| **Full server authority** | competitive action, shared physics, anti-cheat-sensitive gameplay | safest default when fairness matters |
| **Server validation + client simulation** | movement-heavy action, action RPG, shooter input feel | client predicts, server corrects |
| **Turn/step authority** | card, tactics, async PvP, turn combat | server validates each step and advances state |
| **Deterministic input authority** | RTS, fighting, deterministic subsystems | inputs are authoritative boundary, not world state |
| **Hybrid authority** | mixed products with meta + realtime + async subsystems | choose per subsystem, not one rule for all |

Use hybrid authority only when subsystem boundaries are explicit. Otherwise it becomes unclear which side owns errors and reconciliation.

---

## 5. Synchronization By Gameplay Need

| Need | Common Sync Style | Client Role |
|:---|:---|:---|
| **Shared realtime world state** | snapshot or delta state sync | interpolation, prediction where needed |
| **Deterministic command resolution** | lockstep or rollback input sync | local simulation and rollback handling |
| **Turn progression** | request/response or turn-step sync | submit action, render result |
| **Meta progression** | CRUD/API sync with attached player deltas | cache and optimistic UI |
| **Hidden or filtered state** | per-client filtered state sync | render only visible subset |

Guidelines:

- Use **state sync** when the server owns world state.
- Use **lockstep / rollback** only when determinism is a real project constraint you can sustain.
- Use **request/response sync** for meta systems and step-driven gameplay.
- Different subsystems can use different sync styles in the same product.

Detailed protocol shape belongs in `multiplayer-protocol.md`.

---

## 6. Visibility And Hidden State

Visibility is part of gameplay architecture, not only bandwidth optimization.

- Private state, fog-of-war, hidden cards, and spectator view need explicit visibility policy.
- Use per-client filtering before send, not client-side hiding after send.
- Concrete AOI model, subscription range, and update priority belong in `multiplayer-server-architecture.md`.

---

## 7. Latency Handling

Latency strategy follows the authority model:

- **Client prediction** improves local responsiveness.
- **Server reconciliation** fixes divergence.
- **Interpolation** smooths remote entities.
- **Rollback or rewind** is only for systems that explicitly support it.

Make these choices per subsystem. For example, local movement may use prediction while inventory and rewards stay fully request/response.

---

## 8. Anti-Cheat Boundary

- Never trust client-reported gameplay results.
- Validate movement range, action legality, cooldowns, and resource use on the authoritative side.
- Hidden information should never be fully sent to untrusted clients.
- Lag compensation rules should be explicit and bounded.

---

## 9. Genre Quick Mapping

| Genre | Main Authority Shape | Main Sync Shape | Main Architectural Focus |
|:---|:---|:---|:---|
| **MMO / shared world** | server authoritative world | state sync | visibility, handoff, shared world truth |
| **FPS / TPS / MOBA** | server authoritative combat | state sync with prediction and correction | fairness and responsiveness |
| **RTS / fighting** | deterministic or rollback-oriented | input sync | determinism and recovery |
| **Turn-based / card** | server authoritative step progression | request/response or turn sync | validation and persistence |
| **Idle / casual meta** | server authoritative meta state | API sync with deltas | timer integrity and anti-cheat |
| **Hybrid products** | split by subsystem | mixed sync | explicit ownership boundaries |

---

## 10. What To Read Next

- Read `multiplayer-server-architecture.md` once a subsystem is confirmed to live on the server and needs ownership, process role, deployment, persistence, or recovery design.
- Read `multiplayer-protocol.md` for message design, request/response rules, heartbeat, reconnect, and concrete sync transport rules.
