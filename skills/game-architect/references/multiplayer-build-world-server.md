# Persistent World And AOI Server Build Playbook

Build guide for persistent multiplayer worlds where the main runtime owner is a scene, region, shard, or migratable entity group rather than a temporary room.

Use this document for MMO zones, seamless map servers, survival sandbox worlds, and shared worlds with AOI, handoff, and long-lived spatial state.

Use `multiplayer-server-architecture.md` for the higher-level ownership model and `multiplayer-protocol.md` for AOI, state sync, and reconnect protocol rules.

---

## 1. Target Shape

Default first-production shape:

- Runtime model: **scene/region realtime**
- Ownership unit: **region** first, not actor migration first
- Deployment: **gateway + player service + scene service + global/domain services + DB/cache**
- Scaling rule: **world partitioned by region or shard**

Use this shape when:

- players share a persistent map
- AOI and visibility filtering matter
- entities may cross region boundaries
- world state survives longer than one session

Recommended first serious default:

- region ownership before entity migration
- static or mostly static partitioning before dynamic balancing

Do not start with per-entity migration unless scale truly demands it.

---

## 2. Non-Goals

Do not overbuild first version:

- no global seamless migration across every server in phase one
- no actor-per-everything model unless the team already knows how to operate it
- no fully generic distributed simulation bus
- no transparent cross-region writes without explicit handoff
- no client-trusted AOI or hidden-state filtering

The first world server should solve correctness of ownership and handoff before fancy elasticity.

---

## 3. Minimal Topology

Recommended nodes:

- **Gateway**: connection, heartbeat, routing, resume
- **Login/Auth**: identity and session issue
- **Player Service**: durable player state, spawn location, inventory, progression
- **Scene Service**: authoritative region/scene simulation and AOI broadcast
- **Global Services**: guild, mail, chat, economy, matchmaking, leaderboard
- **Location/Registry**: player or entity current region lookup
- **DB/Cache**: persistent world/player data and region metadata

First-production deployment profiles:

- one world shard with multiple regions
- one scene process can own one or more regions
- player service separated from scene service

Do not let gateway or global services mutate scene runtime state directly.

---

## 4. Reference Runtime Structure

Use a concrete world service structure like this:

```text
server/
  gateway/
    WorldGatewayHandler
    WorldRouteDispatcher
  location/
    LocationRegistry
    RegionDirectory
  scene/
    SceneHostService
    RegionRuntimeFactory
    RegionRuntime
    EntityRepository
    AoiManager
    MovementService
    CombatService
    NpcService
    TransferCoordinator
    SnapshotBuilder
  player/
    PlayerSnapshotService
    PlayerPersistenceService
  global/
    ChatService
    GuildService
    EconomyService
```

### Main Class Responsibilities

- `WorldGatewayHandler`: world-facing session routing and reconnect entry
- `LocationRegistry`: authoritative `playerId/entityId -> regionId`
- `RegionDirectory`: `regionId -> scene host`
- `SceneHostService`: process-local container for `RegionRuntime`
- `RegionRuntime`: aggregate root for one region
- `EntityRepository`: create/find/remove runtime entities in region memory
- `AoiManager`: visible set calculation and filtered fan-out
- `MovementService`: authoritative move validation and path state
- `CombatService`: region-local combat interaction
- `TransferCoordinator`: cross-region handoff state machine
- `SnapshotBuilder`: full AOI snapshot and incremental delta builder

### Main Object Relations

- `SceneHostService` owns many `RegionRuntime`
- `RegionRuntime` owns `EntityRepository`, `AoiManager`, `MovementService`, `CombatService`
- `TransferCoordinator` depends on `LocationRegistry`, source `RegionRuntime`, and target `RegionRuntime`
- `SnapshotBuilder` reads `EntityRepository` and `AoiManager`

### Concrete Enter-World Chain

1. `WorldGatewayHandler` authenticates the player.
2. `PlayerSnapshotService` loads durable player state.
3. `LocationRegistry` resolves target `regionId`.
4. `RegionDirectory` resolves host node.
5. `SceneHostService` loads `RegionRuntime`.
6. `RegionRuntime.SpawnPlayerEntity()` creates runtime entity.
7. `SnapshotBuilder.BuildEnterWorldSnapshot()` sends initial visible world data.

---

## 5. Ownership Rules

Hard rules:

- one region has one authoritative writer at a time
- an entity belongs to one active region owner at a time
- cross-region interaction must go through explicit handoff or message flow
- player service owns durable player data
- scene service owns spatial runtime state
- hidden information is filtered before send, never hidden only on client

Recommended keys:

- world shard key: `worldId`
- region key: `regionId`
- entity key: `entityId`
- player key: `playerId`
- transfer token or migration version for region handoff

Recommended first-version ownership model:

- region owns all entities currently inside its bounds
- cross-region movement pauses direct control briefly during handoff if necessary
- global systems never directly patch scene memory

---

## 6. Standard Request Flows

### Login And Enter World

1. Client authenticates through gateway.
2. Player service loads spawn location and player durable state.
3. Location service resolves target region.
4. Gateway routes client to the target scene service.
5. Scene service creates runtime player entity from durable snapshot.
6. Scene service sends initial visible world snapshot.
7. Scene service subscribes player to AOI updates.

### Move Inside Region

1. Client sends move intent.
2. Gateway routes request to current region owner.
3. Scene service validates movement against nav, speed, status, and authority rules.
4. Scene service updates authoritative position.
5. Scene service recalculates AOI visibility if needed.
6. Scene service sends movement sync to relevant nearby clients.

For short movement, use direct move intent and position sync. For long-path movement, use the path protocol defined in `multiplayer-protocol.md`.

### Cross-Region Transfer

1. Player approaches region boundary.
2. Current region owner detects transfer condition.
3. Current region owner serializes transferable runtime state.
4. Target region reserves entity slot and accepts transfer.
5. Ownership switches to target region.
6. Location registry updates authoritative region mapping.
7. Client starts receiving state from target region.
8. Old region removes entity from local AOI sets.

Do not allow both regions to write the same entity concurrently.

### Combat Or Interaction In World

1. Client sends action intent to current region owner.
2. Scene service validates target visibility, range, cooldown, and state.
3. Scene service applies authoritative world logic.
4. Scene service updates affected entity state.
5. Scene service broadcasts filtered results to visible clients.
6. If durable rewards or progression are affected, scene service sends a request to player service or domain service.

### Disconnect And Resume

1. Gateway detects disconnect.
2. Session is held for a reconnect window.
3. Scene service keeps runtime entity for a short timeout or converts to offline placeholder according to game rule.
4. Client reconnects and is routed back to current region.
5. Scene service sends fresh AOI snapshot and player state.

Prefer fresh AOI snapshot over trying to replay every missed world event.

---

## 7. Concrete Cross-Region Transfer Chain

Use a concrete transfer path like this:

1. `MovementService` detects boundary crossing.
2. `TransferCoordinator.BeginTransfer()` marks entity as transferring in source `RegionRuntime`.
3. source `RegionRuntime.ExportTransferState()` serializes runtime state.
4. target `RegionRuntime.AcceptTransfer()` creates incoming entity shell.
5. `LocationRegistry.UpdateOwner()` switches authoritative region mapping.
6. target `SnapshotBuilder.BuildTransferEnterSnapshot()` sends new region data.
7. source `RegionRuntime.RemoveTransferredEntity()` clears old entity after ack.

Suggested method split:

```text
RegionRuntime.SpawnPlayerEntity()
MovementService.ApplyMoveIntent()
AoiManager.RefreshVisibility()
TransferCoordinator.BeginTransfer()
RegionRuntime.ExportTransferState()
RegionRuntime.AcceptTransfer()
SnapshotBuilder.BuildAoiDelta()
```

If transfer logic cannot be described at this level, the world design is still too vague.

---

## 8. State And Persistence

Separate these state classes:

- **Scene runtime state**: entity transforms, combat state, spawned objects, temporary effects, AI state
- **Durable player state**: inventory, progression, quests, bind point, economy
- **Durable world state**: persistent NPC/object states, ownership of land/buildings, world timers, boss lifecycle when needed
- **Location state**: which region currently owns a player or migratable entity

Recommended first serious persistence policy:

- player durable state written by player service
- region runtime state mostly in memory
- important world objects snapshotted periodically or on change
- location registry updated on enter/transfer/disconnect

Recovery policy must be explicit for each type:

- disposable runtime objects can be recreated
- persistent world objects must reload from storage
- player position should fall back to last safe bind point if region state is lost

Do not try to persist every tick. Persist ownership-relevant and durable world facts.

---

## 9. Failure Rules

Write these rules before implementation:

- region crash loses uncheckpointed runtime state in that region
- location registry must not point to two active owners for one entity
- transfer retry must be safe if handoff response is lost
- player reconnect must consult current authoritative location
- hidden state must never leak during AOI recalculation or transfer
- global service failure must not corrupt scene ownership

Default safe choices:

- region handoff uses transfer version or token
- source region keeps old entity until target ack arrives
- final ownership switch happens once location registry update succeeds
- if transfer fails, player remains or is snapped back to source region

---

## 10. Code Skeleton

Suggested project layout:

```text
server/
  gateway/
    session/
    routing/
  player/
    profile/
    inventory/
    spawn/
  scene/
    region_runtime/
    aoi/
    movement/
    combat/
    npc/
    transfer/
    scene_repository/
  global/
    chat/
    guild/
    economy/
  location/
    registry/
  protocol/
    realtime/
    api/
  persistence/
    db/
    cache/
```

Responsibility split:

- `region_runtime`: entity lifetime and authoritative update loop
- `aoi`: visibility sets and filtered fan-out
- `transfer`: cross-region handoff
- `scene_repository`: persistent world object load/save
- `location/registry`: current player or entity region lookup

Do not bury region transfer logic inside generic movement handlers.

---

## 11. Build Order

Recommended implementation order:

1. Login and enter one region
2. In-region movement and AOI enter/leave
3. One simple interaction or combat loop
4. Durable player state integration
5. Region transfer and location registry
6. Reconnect to current region
7. Persistent world object save/load
8. Metrics, tracing, admin inspection tools
9. Optional dynamic balancing or actor migration

Do not build dynamic world rebalancing before one static multi-region shard works correctly.

---

## 12. Framework Fit In Practice

This server shape maps well to these framework families:

- **actor/location runtime**: strong fit when migration, AOI, and entity ownership are core concerns
- **distributed scene-service framework**: good when route-based or service-tree distributed runtime is the main problem
- **room frameworks**: usually not enough once cross-region transfer and persistent AOI world are core requirements

Practical rule:

- use room frameworks for instances inside a world
- use world/scene ownership architecture for the persistent map itself
- if handoff, AOI, and location registry are central, communication framework choice is secondary to ownership design

---

## 13. Review Checklist

Before calling the design ready, verify:

- one region owns one entity at a time
- AOI filtering happens before send
- location registry is authoritative
- transfer protocol is explicit and retry-safe
- player durable state is not written by scene runtime directly
- recovery policy is defined for region crash and reconnect
