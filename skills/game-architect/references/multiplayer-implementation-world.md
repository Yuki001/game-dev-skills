# World And AOI Runtime Implementation Playbook

Runtime-specific playbook for persistent or scene-shaped multiplayer worlds where the live-state owner is a scene, region, shard, instance copy, or migratable entity group.

Use `multiplayer-server-architecture.md` for architecture decisions, `multiplayer-implementation-common.md` for shared infrastructure, and `multiplayer-protocol.md` for AOI, state sync, and reconnect protocol rules.

---

## 1. Purpose And Fit

Use this playbook for MMO zones, seamless map servers, survival sandbox worlds, dungeon/raid scene copies, housing plots, and shared worlds with AOI, handoff, or long-lived spatial state.

Default shape:

- Runtime model: **scene/world realtime**
- Ownership unit: **region, scene, scene instance, or entity shard**
- Live state writer: **scene/region runtime**
- Durable player-state writer: **player/meta service**
- Scaling rule: **world partitioned by region, shard, or scene instance**

Recommended default:

- region or scene ownership before per-entity migration
- static or mostly static partitioning before dynamic balancing
- ownership correctness and handoff before elasticity

Do not use this as the primary template for temporary room-style matches, client-trusted AOI, or actor-per-everything runtime unless the team already knows how to operate it.

---

## 2. Key Objects

| Object | Owns | Talks To | Must Not Do |
|:---|:---|:---|:---|
| `SceneHostService` | create, host, retire, and inspect region/scene runtimes | gateway, location registry, persistence | mutate durable player/meta state directly |
| `RegionRuntime` | authoritative spatial state for one region or scene copy | entity repository, AOI, movement, combat, transfer | share write authority with another region |
| `EntityRepository` | runtime entity create/find/remove inside owner | region runtime, persistence bridge | become global durable source of truth by accident |
| `AoiManager` | visible set, interest set, filtered fan-out | region runtime, snapshot builder | rely on client-side hiding for secrets |
| `MovementService` | authoritative movement validation and path state | region runtime, transfer coordinator | trust client position updates |
| `TransferCoordinator` | cross-region handoff state machine | source region, target region, location registry | allow both regions to write one entity concurrently |
| `LocationRegistry` | current `playerId/entityId -> regionId/instanceId` lookup | gateway, transfer coordinator, scene hosts | replace owner-side validation |
| `SnapshotBuilder` | full AOI snapshot and incremental delta view | region runtime, AOI manager, gateway | own simulation state |
| `PlayerSnapshotService` | durable player snapshot for spawn/resume | player/meta service, scene host | let scene runtime write inventory/currency directly |
| `InstanceDirectory` | optional `instanceId -> scene host` lookup | instance lifecycle, gateway, location registry | treat instance identity as room settlement state |

---

## 3. Core Flows

### Enter World

1. client authenticates through common gateway/auth infrastructure
2. player/meta service loads spawn location and durable player snapshot
3. location registry resolves target region or scene instance
4. gateway routes client to current scene owner
5. scene runtime creates player entity from durable snapshot
6. AOI manager builds initial visible set
7. snapshot builder sends initial visible-world snapshot

### Move Inside Region

1. client sends movement intent
2. gateway routes to current region owner
3. movement service validates speed, nav, status, and authority rules
4. region runtime updates authoritative position
5. AOI manager recalculates visibility if needed
6. snapshot/broadcast layer sends filtered movement updates to relevant clients

Use direct movement intent for short movement and path protocol for long-path movement when pathing matters.

### Cross-Region Transfer

1. source region detects boundary crossing or transfer trigger
2. source marks entity as transferring and serializes transferable runtime state
3. target reserves slot and validates acceptance
4. location registry updates authoritative owner
5. target region creates entity and sends enter snapshot or delta
6. source removes old entity after target ack

Never allow both regions to write the same entity concurrently.

### World Action

1. client sends action intent to current region owner
2. scene runtime validates target visibility, range, cooldown, and state
3. authoritative world logic mutates runtime entities
4. AOI manager filters affected recipients
5. snapshot/broadcast layer sends filtered results
6. durable reward or progression changes go through player/meta or domain service

### Reconnect

1. gateway detects disconnect and keeps session metadata for the reconnect window
2. scene runtime keeps entity briefly or applies offline-placeholder rules
3. client reconnects and location registry resolves current owner
4. scene runtime validates resume and rebinds session
5. snapshot builder sends fresh AOI snapshot and player state

Prefer fresh AOI snapshot over replaying every missed world event.

---

## 4. Failure Rules

Write these rules explicitly before implementation:

- one region owns one entity at a time
- location registry must never point to two active owners for one entity
- transfer retry must be safe if target ack or source cleanup response is lost
- source keeps old entity until target ack or declared rollback point
- final ownership switch happens only through the chosen handoff rule
- player reconnect consults current authoritative location
- hidden state never leaks during AOI recalculation, transfer, or snapshot build
- global service failure does not corrupt scene ownership
- region crash loses uncheckpointed runtime state unless recovery exists

Recovery policy must be explicit for each state class:

- disposable runtime objects can be recreated
- persistent world objects reload from storage
- player position falls back to last safe bind point if region state is lost

---

## 5. Instance Variant

An instance is a scene/world-shaped owner with a temporary lifecycle. Keep it in this playbook when the activity depends on spatial ownership, AOI, scene-local objects, spawned entities, triggers, destructibles, gatherables, or local world timers.

Prefer the room playbook instead when players are mainly seats/slots and the map is mostly a backdrop for match rules.

Key additions:

| Object | Owns | Must Decide |
|:---|:---|:---|
| `InstanceDirectory` | `instanceId -> scene host` and metadata lookup | stale entry, reconnect lookup, owner change |
| `InstanceLifecycleService` | create, warm, retire, dispose scene instances | completion, timeout, empty-instance policy |
| `InstanceEntryService` | party/run validation and entry token | membership, lock state, capacity, destination |
| `SceneHostService` | active scene copy runtime | checkpoint, disposal, same-instance reconnect |
| `LocationRegistry` | `playerId -> worldId/instanceId/regionId` | fallback when instance expires |

Core flow:

1. party, raid, mission, or activity service chooses `instanceId`
2. entry service validates membership, lock state, progress, and capacity
3. lifecycle service creates or reuses the scene copy
4. instance directory publishes current owner
5. location registry updates player destination
6. gateway routes client to the scene owner
7. scene runtime builds player entity and sends instance snapshot

Instance-specific rules:

- create instance identity before admitting players into the scene copy
- reconnect returns to the same `instanceId` when the run is still valid
- disposal is driven by explicit completion, timeout, or empty-instance policy
- expired instance recovery chooses restart, checkpoint resume, or safe return to public world
- scene-local objects recover from instance snapshot or run checkpoint, not room settlement logic

---

## 6. Minimal Build Order

Recommended order:

1. login and enter one region or scene copy
2. in-region movement and AOI enter/leave
3. one simple interaction or combat loop
4. durable player-state integration
5. location registry and region transfer
6. reconnect to current region or instance
7. persistent world object save/load where needed
8. logs, metrics, tracing, and admin inspection tools
9. optional dynamic balancing, actor migration, or advanced instance recovery

Do not build dynamic world rebalancing before one static multi-region shard or scene-copy flow works correctly.

---

## 7. Review Checklist

Before calling a world/AOI design ready, verify:

- one region, scene, or instance owns one entity at a time
- AOI filtering happens before send
- location registry is authoritative but owners still validate requests
- transfer protocol is explicit and retry-safe
- player durable state is not written by scene runtime directly
- recovery policy is defined for region crash and reconnect
- instance designs define `instanceId`, entry, reconnect, disposal, and fallback rules
- dynamic balancing or actor migration is deferred unless requirements demand it
