# Encounter And Turn-Based Server Template

Template for server-authoritative combat or progression flows where the runtime owner is a short-lived encounter, battle, or workflow instance rather than a room with long-lived membership.

Use this for PvE battles, async PvP turns, card combat, roguelike encounters, and phase-driven battle workflows. Use `multiplayer-server-architecture.md` for runtime-model tradeoffs and `multiplayer-protocol.md` for RPC, notify, and idempotency rules.

---

## 1. Fit

Default shape:

- Runtime model: **encounter/combat service**
- Ownership unit: **encounter**
- Transport model: **API/RPC first**, optional realtime notify
- Live state writer: **encounter service**
- Durable state writer: **player service**

Use this template when:

- actions are ordered and authoritative
- the system needs buffs, cooldowns, scripted phases, or turn logic
- realtime room presence is not the main product requirement
- persistence and recovery matter more than high-frequency broadcast

Do not use this as the primary template for:

- shared visible movement with long-lived room membership
- MMO scene runtime or world-scale AOI
- per-frame realtime synchronization as the main loop
- event-sourcing-only design unless replay or audit is a hard requirement

If the product mostly needs live shared presence, use the room template instead.

---

## 2. Core Topology

Recommended nodes:

- **API/Gateway**: auth, request entry, rate limit, routing
- **Encounter Service**: encounter creation, action validation, phase progression, result generation
- **Player Service**: durable player/meta state, rewards, inventory, quests
- **DB/Cache**: encounter snapshot, player data, idempotency table, optional action log
- **Notify Channel**: optional push for battle updates when clients stay connected

Default deployment:

- light-combat version: API + player service + encounter logic in one process
- scale version: encounter service separated from player service

Hard boundary:

- player-facing API handlers do not directly execute battle rules

Split encounter from player service only when:

- encounter CPU cost is materially higher than normal player/meta requests
- one battle can block process capacity for too long
- checkpoint or recovery operations become operationally separate
- combat logic needs its own scaling or release cadence

---

## 3. Reference Runtime Structure

Use a runtime split like this as the default reference:

```text
api/
  EncounterController
encounter/
  EncounterApplicationService
  EncounterRepository
  EncounterRuntime
  TurnResolver
  EffectPipeline
  BattleAiResolver
  EncounterRecoveryService
  EncounterSettlementCoordinator
player/
  PlayerFacade
```

Key responsibilities:

- `EncounterApplicationService`: application-layer coordinator for open, submit, resume, surrender
- `EncounterRepository`: snapshot persistence and optional action log
- `EncounterRuntime`: authoritative battle aggregate root
- `TurnResolver`: phase and turn progression
- `EffectPipeline`: buffs, triggers, passive effects, cleanup
- `BattleAiResolver`: enemy or npc action resolution
- `EncounterRecoveryService`: load and rebuild resumable battle state
- `EncounterSettlementCoordinator`: commit final result through player service

Dependency direction:

- controller -> encounter application service
- encounter runtime -> turn resolver
- turn resolver -> effect pipeline + ai resolver
- settlement -> player facade
- player service never depends on encounter runtime internals

---

## 4. Ownership And Persistence Rules

Hard rules:

- one encounter instance owns all writes to encounter state
- player service owns all durable player-state writes
- merged deployment still keeps player and encounter as separate modules
- encounter service may read player stats or loadout snapshot, but does not directly mutate inventory or currency
- every combat action carries `actionId` or sequence
- encounter completion commits through one settlement path

Recommended keys:

- `encounterId`
- `playerId`
- `actionId`
- `encounterId + actionId`
- `battleResultId`

Separate these states:

- **encounter runtime state**: turn order, hp, buffs, cooldowns, scripted variables, rng seed
- **player durable state**: inventory, account progression, quest progress, rewards
- **audit or recovery state**: create record, checkpoint snapshot, action log, result record

Recommended persistence policy:

- persist encounter on create
- persist at each turn or phase boundary when recovery matters
- persist final result before or together with settlement request
- persist action log only when audit, anti-cheat review, or replay matters

If encounter must resume after restart, snapshot must contain authoritative runtime state, not only visual delta.

---

## 5. Standard Flows

### Encounter Open

Default open flow:

1. client calls `Encounter_Open` or equivalent RPC
2. API validates session and feature access
3. encounter service checks for an existing reusable active encounter
4. if needed, service creates encounter state from config, player loadout, and seed data
5. service stores initial snapshot or create record
6. service returns initial battle view and encounter token

Rule:

- opening should be idempotent for the same active run when resume is supported

### Submit Action

Default action flow:

1. client sends `Battle_SubmitAction` with `encounterId` and `actionId`
2. API validates session and routes to encounter service
3. encounter validates ownership, turn or phase legality, and idempotency
4. turn resolver applies authoritative logic
5. effect pipeline resolves triggered effects
6. ai resolver runs follow-up step if needed
7. service persists checkpoint at action, phase, or turn boundary as designed
8. service returns authoritative result, delta, and next-phase info

Rule:

- design for deterministic recovery, but do not force lockstep unless the product actually requires it

### Phase Or Turn Advance

Default advance flow:

1. service detects end of action window or turn
2. service resolves queued triggers, status effects, scripted events, and AI
3. service persists boundary checkpoint if recovery matters
4. service returns next authoritative turn state

Recommended default:

- checkpoint at turn boundaries for best value-to-cost ratio

### Encounter Complete

Default completion flow:

1. encounter reaches success, fail, surrender, or timeout
2. service computes result and reward intent
3. settlement coordinator sends one request to player service
4. player service applies durable write idempotently
5. encounter is marked complete and stops accepting actions
6. client receives final result

### Resume

Default resume flow:

1. client reopens the same encounter
2. service loads active snapshot
3. service verifies encounter is resumable
4. service returns latest authoritative state

Recommended default:

- prefer resume-by-snapshot instead of replaying full action log unless replay is a product feature

---

## 6. Failure And Recovery

Default safety rules:

- repeated `SubmitAction` with the same `actionId` must not apply twice
- encounter crash recovers from the last valid checkpoint or fails explicitly
- settlement retries are safe by `encounterId` or result ID
- once encounter enters `completing` or `completed`, new actions are rejected
- timeout resolves encounter into a known terminal state

Typical failure handling:

- request timeout before execution known: client retries with same `actionId`
- action executed but response lost: service returns the same logical result on retry
- player service unavailable during completion: encounter moves to `settlement_pending`
- corrupted snapshot: encounter fails and compensates by product rule

Good first-production defaults:

- no replay-driven recovery
- no full event-sourcing requirement
- explicit checkpoint policy before launch

---

## 7. Minimal Build Order

Recommended implementation order:

1. separate player and encounter modules inside one process
2. encounter create or open
3. one action submission loop with idempotency
4. turn or phase progression
5. encounter snapshot persistence
6. completion and settlement to player service
7. resume after reconnect or server restart
8. metrics, logs, admin inspection tools
9. split encounter into an independent service only if load and ownership pressure justify it

Do not split player and encounter into separate services on day one unless actual runtime pressure requires it.

---

## 8. Framework Fit

This template fits best with:

- **backend platform with RPC or service APIs** when encounter and player APIs are closely coupled
- **typed RPC framework with optional realtime push** when typed contracts matter and clustering is solved elsewhere
- **custom lightweight service** when encounter rules are rich but live broadcast is limited

Rule of thumb:

- if the encounter is mainly a transactional workflow with rich rules, build it as a stateful module first
- if the product needs long-lived member presence and continuous shared simulation, this is no longer an encounter service

---

## 9. Review Checklist

Before calling the design ready, verify:

- encounter ownership is single-writer
- every action has idempotency
- turn-boundary checkpoint policy is explicit
- settlement path is single and durable
- merged deployment still keeps player and encounter module boundaries clear
- crash and retry behavior is written down
- resume is based on authoritative snapshot, not client memory
