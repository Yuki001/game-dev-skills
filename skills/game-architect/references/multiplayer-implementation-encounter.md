# Encounter And Turn-Based Server Build Playbook

Build guide for server-authoritative combat or progression flows where the main runtime owner is a short-lived encounter, battle, or workflow instance rather than a room with long-lived membership.

Use this document for PvE battle services, async PvP turns, card combat, roguelike encounters, and phase-driven battle workflows.

Use `multiplayer-server-architecture.md` for the runtime model comparison. Use `multiplayer-protocol.md` for RPC, notify, and idempotency rules.

---

## 1. Target Shape

Default first-production shape:

- Runtime model: **encounter/combat service**
- Ownership unit: **encounter**
- Transport model: **API/RPC first**, optional realtime notify
- Deployment: **gateway or API + player/encounter service + DB**
- Scaling rule: **one encounter owned by one process at a time**

Use this shape when:

- actions are ordered and authoritative
- the system needs buffs, cooldowns, scripted phases, or turn logic
- realtime room presence is not the core product requirement
- persistence and recovery matter more than 20 Hz broadcast

---

## 2. Non-Goals

Do not overbuild first version:

- no permanent room membership model
- no generic MMO scene runtime
- no per-frame realtime sync loop
- no distributed transaction between encounter and player inventory
- no event-sourcing-only architecture unless replay/audit is a hard requirement

If the game mostly needs visible shared movement and live broadcast, use the room build playbook instead.

---

## 3. Minimal Topology

Recommended nodes:

- **API/Gateway**: auth, request entry, rate limit, routing
- **Encounter Service**: encounter creation, phase progression, action validation, result generation
- **Player Service**: durable player/meta state, rewards, inventory, quests
- **DB/Cache**: encounter snapshot, player data, idempotency tables, optional action log
- **Notify Channel**: optional push for battle updates if clients stay connected

Default deployment:

- common light-combat version: API + player service + encounter logic in one process
- scale version: encounter service separated from player service

This is a common and valid default for card battle, async combat, roguelike encounter, and other battle workflows where:

- encounter state is short-lived
- combat concurrency is moderate
- most requests are still player-centric
- reward settlement and encounter progression are tightly coupled

Split encounter from player service only when one of these becomes true:

- encounter CPU cost is much higher than normal player/meta requests
- one battle can hold a process busy for too long
- checkpoint/recovery logic becomes operationally separate from player APIs
- the team needs independent scaling or deployment for combat logic

Do not let player API handlers directly execute battle rules.

---

## 4. Reference Runtime Structure

Use a concrete encounter service structure like this:

```text
server/
  api/
    EncounterController
    EncounterRouteService
  encounter/
    EncounterApplicationService
    EncounterRepository
    EncounterRuntimeFactory
    EncounterRuntime
    TurnResolver
    EffectPipeline
    BattleAiResolver
    RewardPreviewBuilder
    EncounterRecoveryService
    EncounterSettlementCoordinator
  player/
    PlayerFacade
    RewardCommitService
```

### Main Class Responsibilities

- `EncounterController`: RPC or HTTP handler for open, submit action, surrender, resume
- `EncounterApplicationService`: application-layer coordinator for encounter commands
- `EncounterRepository`: save/load snapshot and optional action log
- `EncounterRuntime`: aggregate root holding battle state
- `TurnResolver`: phase and turn progression
- `EffectPipeline`: buffs, triggers, passive effects, dot/hot, cleanup
- `BattleAiResolver`: npc or enemy action resolution
- `EncounterRecoveryService`: load last good snapshot and rebuild runtime
- `EncounterSettlementCoordinator`: commit final result into player service
- `PlayerFacade`: typed entry to player data and settlement operations

### Main Object Relations

- `EncounterApplicationService` loads one `EncounterRuntime`
- `EncounterRuntime` delegates turn logic to `TurnResolver`
- `TurnResolver` uses `EffectPipeline` and `BattleAiResolver`
- `EncounterSettlementCoordinator` depends on `EncounterRepository` and `PlayerFacade`

### Concrete Open Chain

1. `EncounterController.OpenEncounter()` validates session.
2. `EncounterApplicationService.Open()` checks reusable active encounter.
3. `EncounterRuntimeFactory.Create()` builds `EncounterRuntime`.
4. `EncounterRepository.SaveCreateSnapshot()` persists initial state.
5. `RewardPreviewBuilder` optionally builds initial ui data.
6. controller returns `Encounter_Open_Resp`.

---

## 5. Ownership Rules

Hard rules:

- one encounter instance owns all writes to encounter state
- player service owns all durable player state writes
- when player and encounter are deployed in the same process, keep them as separate modules with separate ownership rules
- encounter service may read player stats/loadout snapshot, but must not directly mutate inventory or currency
- every combat action must carry `actionId` or sequence
- encounter completion must commit through one settlement path

Recommended keys:

- encounter key: `encounterId`
- player key: `playerId`
- action idempotency key: `encounterId + actionId`
- settlement key: `encounterId` or `battleResultId`

---

## 6. Standard Request Flows

### Encounter Open

1. Client calls `Encounter_Open` or equivalent RPC.
2. API validates session and feature access.
3. Encounter service checks whether a reusable active encounter already exists.
4. If not, encounter service creates encounter state from stage config, player loadout, and seed data.
5. Encounter service stores initial snapshot or create record.
6. Service returns initial battle view and encounter token.

Default rule:

- opening an encounter should be idempotent for the same active run if design requires resume

### Submit Action

1. Client sends `Battle_SubmitAction` with `encounterId` and `actionId`.
2. API validates session and routes to encounter service.
3. Encounter service checks ownership, turn/phase legality, and idempotency.
4. Encounter service applies authoritative logic.
5. Encounter service updates in-memory or persisted encounter state.
6. Encounter service returns action result, deltas, and next phase info.
7. Optional notify channel pushes battle update to other viewers or party members.

This is the critical flow. It must be deterministic enough for recovery, but does not need lockstep unless the product truly requires it.

### Turn Or Phase Advance

1. Encounter service detects end of action window or turn.
2. Service resolves AI, status effects, queued triggers, and scripted events.
3. Service persists checkpoint at phase or turn boundary if recovery matters.
4. Service returns authoritative next turn state.

Checkpoint at turn boundaries is usually the best value-for-cost default.

### Encounter Complete

1. Encounter reaches success, fail, surrender, or timeout.
2. Encounter service computes result and reward intent.
3. Service sends one settlement request to player service.
4. Player service validates duplicate completion and writes durable rewards.
5. Player service returns settlement confirmation.
6. Encounter service marks encounter complete and no longer accepts actions.
7. Client receives final result.

### Resume

1. Client reopens the same encounter.
2. Encounter service loads active snapshot.
3. Service verifies encounter status is resumable.
4. Service returns latest authoritative state.

Prefer resume-by-snapshot instead of replaying the full action log unless audit/replay is a product feature.

---

## 7. Concrete Action Execution Chain

Use a concrete action path like this:

1. `EncounterController.SubmitAction()` receives `encounterId` and `actionId`.
2. `EncounterApplicationService.SubmitAction()` loads `EncounterRuntime`.
3. `EncounterRuntime.ValidateAction()` checks phase, actor, cooldown, and idempotency.
4. `TurnResolver.ApplyPlayerAction()` mutates battle state.
5. `EffectPipeline.ResolveAfterAction()` runs triggered effects.
6. `BattleAiResolver.ResolveIfNeeded()` runs enemy step.
7. `EncounterRepository.SaveTurnSnapshot()` persists checkpoint.
8. `EncounterSettlementCoordinator.TryComplete()` checks terminal state.
9. controller returns authoritative result payload.

Suggested method split:

```text
EncounterApplicationService.Open()
EncounterApplicationService.SubmitAction()
EncounterApplicationService.Resume()
EncounterRuntime.ValidateAction()
TurnResolver.ApplyPlayerAction()
TurnResolver.AdvanceTurn()
EffectPipeline.ResolveTriggeredEffects()
EncounterSettlementCoordinator.CommitResult()
```

---

## 8. State And Persistence

Separate these states:

- **Encounter runtime state**: turn order, hp, buffs, skill cooldowns, scripted phase variables, RNG seed
- **Player durable state**: inventory, account progression, quest progress, rewards
- **Battle audit state**: encounter create record, action log, result record

Recommended first real production policy:

- persist encounter on create
- persist at each turn or phase boundary
- persist final result before or together with settlement request
- persist action log only when audit, anti-cheat review, or replay matters

What to persist inside encounter snapshot:

- encounter version
- current phase/turn
- unit states
- pending effects
- RNG seed or reproducible state
- timeout data

Do not store only visual delta if the encounter must resume after restart.

---

## 9. Failure Rules

Default safety rules:

- repeated `SubmitAction` with same `actionId` must not apply twice
- encounter service crash should recover from the last checkpoint or mark the encounter failed explicitly
- settlement retries must be safe by `encounterId`
- once encounter is in `completing` or `completed`, new actions must be rejected
- timeout must resolve encounter into a known terminal state

Typical failure handling:

- API timeout before execution known: client may retry with same `actionId`
- action executed but response lost: service returns same logical result on retry
- player service down during completion: encounter moves to `settlement_pending`
- corrupted snapshot: encounter is failed and compensated according to product rule

---

## 10. Code Skeleton

Suggested project layout:

```text
server/
  api/
    auth/
    rpc/
  encounter/
    encounter_api/
    encounter_runtime/
    turn_engine/
    effect_system/
    ai/
    encounter_repository/
    encounter_recovery/
  player/
    profile/
    inventory/
    quest/
    reward/
  protocol/
    api/
    notify/
  persistence/
    db/
    cache/
    idempotency/
```

If player and encounter are merged into one process, keep the module boundary explicit:

```text
server/
  api/
  player/
  encounter/
  protocol/
  persistence/
```

Responsibility split:

- `encounter_api`: request validation and handler entry
- `turn_engine`: authoritative turn/phase progression
- `effect_system`: buffs, triggers, status, passive resolution
- `encounter_repository`: snapshot read/write and action log storage
- `encounter_recovery`: resume and checkpoint loading

Do not mix settlement writes into combat resolution code paths.

---

## 11. Build Order

Recommended implementation order:

1. Player service and encounter modules separated inside one process
2. Encounter create/open
3. One action submission loop with idempotency
4. Turn/phase progression
5. Encounter snapshot persistence
6. Completion and settlement to player service
7. Resume after reconnect or server restart
8. Metrics, logs, admin inspection tools
9. Split encounter into an independent service only if load and ownership pressure justify it

Do not split player and encounter into different services on day one if the actual runtime pressure does not require it.

---

## 12. Deployment Evolution

Recommended evolution path:

1. start with `player + encounter` in one process
2. keep separate modules, repositories, and ownership rules inside that process
3. measure combat CPU time, action latency, checkpoint cost, and settlement contention
4. split encounter into its own service only after those pressures are visible

This gives the team lower operational cost early while keeping a clean extraction path later.

Typical sign that merging is still fine:

- encounter open and submit action are just another branch of player-facing API traffic
- battle state stays small
- combat result writes are simple and local
- one process can absorb both traffic patterns without noisy-neighbor issues

Typical sign that splitting is overdue:

- encounter simulation dominates CPU
- battle persistence becomes operationally heavy
- one player's combat spikes affect unrelated player APIs
- combat and player modules need different release cadence

---

## 13. Framework Fit In Practice

This server shape maps well to these framework families:

- **backend platform with RPC/service APIs**: especially suitable when player-facing backend APIs and lightweight encounters live in the same service boundary
- **typed RPC framework with optional realtime push**: good when typed contracts matter and clustering is provided elsewhere
- **custom service or lightweight framework**: often best when encounter rules are complex but live broadcast is minimal

Practical rule:

- if the encounter is basically a transactional workflow with rich rules, build it as a stateful module first
- if player data and encounter progression are tightly coupled, colocating them in one service is a normal starting point
- if you need long-lived member presence and continuous shared simulation, it is not an encounter service anymore

---

## 14. Review Checklist

Before calling the design ready, verify:

- encounter ownership is single-writer
- every action has idempotency
- turn boundary checkpoint policy is explicit
- settlement path is single and durable
- merged deployment still keeps player and encounter module boundaries clear
- crash/retry behavior is written down
- resume is based on authoritative snapshot, not client memory
