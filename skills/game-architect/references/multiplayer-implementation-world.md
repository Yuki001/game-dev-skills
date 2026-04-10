# Persistent World And AOI Server Template

Template for persistent multiplayer worlds where the runtime owner is a scene, region, shard, or migratable entity group rather than a temporary room.

Use this for MMO zones, seamless map servers, survival sandbox worlds, and other shared worlds with AOI, handoff, and long-lived spatial state. Use `multiplayer-server-architecture.md` for higher-level ownership choices and `multiplayer-protocol.md` for AOI, state sync, and reconnect protocol rules.

---

## 1. Fit

Default shape:

- Runtime model: **scene/region realtime**
- Ownership unit: **region**
- Live state writer: **scene service**
- Durable player-state writer: **player service**
- Scaling rule: **world partitioned by region or shard**

Use this template when:

- players share a persistent map
- AOI and visibility filtering matter
- entities may cross region boundaries
- world state survives longer than one session

Recommended default:

- region ownership before per-entity migration
- static or mostly static partitioning before dynamic balancing

Do not use this as the primary template for:

- temporary room-style matches
- global seamless migration across every node in phase one
- actor-per-everything runtime unless the team already knows how to operate it
- client-trusted AOI or hidden-state filtering

The first world server should solve ownership correctness and handoff before elasticity.

---

## 2. Core Topology

Recommended nodes:

- **Gateway**: connection, heartbeat, routing, reconnect
- **Login/Auth**: identity and session issue
- **Player Service**: durable player state, spawn location, inventory, progression
- **Scene Service**: authoritative region simulation and AOI broadcast
- **Global Services**: chat, guild, economy, matchmaking, leaderboard
- **Location Registry**: authoritative player or entity current-region lookup
- **DB/Cache**: persistent world data, player data, region metadata

Default deployment:

- one world shard with multiple regions
- one scene process owns one or more regions
- player service remains separate from scene service

Hard boundary:

- gateway and global services do not mutate scene runtime state directly

---

## 3. Reference Runtime Structure

Use a runtime split like this as the default reference:

```text
gateway/
  WorldGatewayHandler
  WorldRouteDispatcher
location/
  LocationRegistry
  RegionDirectory
scene/
  SceneHostService
  RegionRuntime
  EntityRepository
  AoiManager
  MovementService
  CombatService
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

Key responsibilities:

- `LocationRegistry`: authoritative `playerId/entityId -> regionId`
- `RegionDirectory`: `regionId -> scene host`
- `SceneHostService`: process-local owner of `RegionRuntime`
- `RegionRuntime`: authoritative aggregate root for one region
- `EntityRepository`: runtime entity create, find, remove
- `AoiManager`: visible-set calculation and filtered fan-out
- `MovementService`: authoritative movement validation and path state
- `CombatService`: region-local combat or interaction resolution
- `TransferCoordinator`: cross-region handoff state machine
- `SnapshotBuilder`: full AOI snapshot and incremental delta builder

Dependency direction:

- gateway -> location + scene routing
- region runtime -> entity repository + aoi + movement + combat
- transfer coordinator -> source region + target region + location registry
- snapshot builder reads region state but does not own simulation

---

## 4. Ownership And State Rules

Hard rules:

- one region has one authoritative writer at a time
- one entity belongs to one active region owner at a time
- cross-region interaction goes through explicit handoff or message flow
- player service owns durable player data
- scene service owns spatial runtime state
- hidden information is filtered before send, never hidden only on client

Recommended keys:

- `worldId`
- `regionId`
- `entityId`
- `playerId`
- transfer token or migration version

Recommended first-version ownership model:

- region owns all entities currently inside its bounds
- direct control may pause briefly during handoff
- global systems never patch scene memory directly

Separate these state classes:

- **scene runtime state**: transforms, combat state, spawned objects, temporary effects, AI state
- **durable player state**: inventory, progression, quests, bind point, economy
- **durable world state**: persistent npc or object state, land ownership, world timers, boss lifecycle
- **location state**: which region currently owns a player or migratable entity

Recommended persistence policy:

- player durable state is written by player service
- region runtime state stays mostly in memory
- important world objects are snapshotted periodically or on change
- location registry updates on enter, transfer, and disconnect

Do not try to persist every tick. Persist ownership-relevant and durable world facts.

---

## 5. Standard Flows

### Login And Enter World

Default enter flow:

1. client authenticates through gateway
2. player service loads spawn location and durable player state
3. location service resolves target region
4. gateway routes client to the target scene service
5. scene service creates runtime player entity from durable snapshot
6. scene service sends initial visible-world snapshot
7. scene service subscribes player to AOI updates

### Move Inside Region

Default move flow:

1. client sends move intent
2. gateway routes request to current region owner
3. scene service validates movement against nav, speed, status, and authority rules
4. scene service updates authoritative position
5. scene service recalculates AOI visibility if needed
6. scene service sends movement sync to relevant nearby clients

Rule:

- use direct move intent for short movement and the path protocol for long-path movement

### Cross-Region Transfer

Default transfer flow:

1. current region detects boundary crossing
2. source region marks entity as transferring
3. source region serializes transferable runtime state
4. target region reserves slot and accepts transfer
5. location registry updates authoritative owner
6. target region sends enter snapshot or delta
7. source region removes old entity after ack

Rule:

- never allow both regions to write the same entity concurrently

### Combat Or Interaction In World

Default world-action flow:

1. client sends action intent to current region owner
2. scene service validates target visibility, range, cooldown, and state
3. scene service applies authoritative world logic
4. scene service updates affected entity state
5. scene service broadcasts filtered results to visible clients
6. if durable rewards or progression change, scene service sends request to player or domain service

### Disconnect And Resume

Default reconnect flow:

1. gateway detects disconnect
2. session is held for a reconnect window
3. scene service keeps the runtime entity for a short timeout or converts it to an offline placeholder by game rule
4. client reconnects and is routed back to the current region
5. scene service sends fresh AOI snapshot and player state

Recommended default:

- prefer fresh AOI snapshot over replaying every missed world event

---

## 6. Failure And Recovery

Write these rules explicitly before implementation:

- region crash loses uncheckpointed runtime state in that region
- location registry must never point to two active owners for one entity
- transfer retry must be safe if handoff response is lost
- player reconnect consults current authoritative location
- hidden state never leaks during AOI recalculation or transfer
- global service failure does not corrupt scene ownership

Default safe choices:

- handoff uses transfer version or token
- source region keeps old entity until target ack arrives
- final ownership switch happens only after location registry update succeeds
- if transfer fails, player remains or snaps back to source region

Recovery policy must be explicit for each type:

- disposable runtime objects can be recreated
- persistent world objects reload from storage
- player position falls back to last safe bind point if region state is lost

---

## 7. Minimal Build Order

Recommended implementation order:

1. login and enter one region
2. in-region movement and AOI enter or leave
3. one simple interaction or combat loop
4. durable player-state integration
5. region transfer and location registry
6. reconnect to current region
7. persistent world object save or load
8. metrics, tracing, admin inspection tools
9. optional dynamic balancing or actor migration

Do not build dynamic world rebalancing before one static multi-region shard works correctly.

---

## 8. Framework Fit

This template fits best with:

- **actor or location runtime** when migration, AOI, and entity ownership are core concerns
- **distributed scene-service framework** when route-based or service-tree runtime is the main problem
- **room frameworks** only for instances inside a world, not for the persistent world itself

Rule of thumb:

- if handoff, AOI, and location registry are central, communication framework choice is secondary to ownership design

---

## 9. Review Checklist

Before calling the design ready, verify:

- one region owns one entity at a time
- AOI filtering happens before send
- location registry is authoritative
- transfer protocol is explicit and retry-safe
- player durable state is not written by scene runtime directly
- recovery policy is defined for region crash and reconnect
