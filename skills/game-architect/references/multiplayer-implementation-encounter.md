# Encounter Workflow Implementation Playbook

Runtime-specific playbook for server-authoritative combat or progression flows where the live-state owner is a short-lived encounter, battle, or workflow instance.

Use `multiplayer-server-architecture.md` for architecture decisions, `multiplayer-implementation-common.md` for shared infrastructure, and `multiplayer-protocol.md` for RPC, notify, and idempotency rules.

---

## 1. Purpose And Fit

Use this playbook for PvE battles, async PvP turns, card combat, roguelike encounters, and phase-driven workflows where actions are ordered and authoritative but room membership is not the core runtime problem.

Default shape:

- Runtime model: **encounter/combat service**
- Ownership unit: **encounter, battle, or workflow instance**
- Transport model: **API/RPC first**, optional realtime notify
- Live state writer: **encounter runtime**
- Durable state writer: **player/meta service**

Do not use this as the primary template for shared movement, long-lived room presence, MMO scene runtime, AOI, or per-frame state synchronization.

---

## 2. Key Objects

| Object | Owns | Talks To | Must Not Do |
|:---|:---|:---|:---|
| `EncounterApplicationService` | open, submit, resume, surrender, complete orchestration | API/controller, repository, runtime, settlement | hide combat rules in transport handlers |
| `EncounterRepository` | create record, snapshot, optional action log, result record | persistence adapter, recovery service | become gameplay authority by itself |
| `EncounterRuntime` | authoritative battle state, phase, turn, RNG seed | turn resolver, effect pipeline, recovery service | write durable inventory/currency directly |
| `TurnResolver` | ordered action resolution and phase progression | runtime, effect pipeline, AI resolver | trust client-computed outcomes |
| `EffectPipeline` | buffs, triggers, passives, cleanup order | turn resolver, runtime state | mutate durable player state |
| `BattleAiResolver` | enemy or NPC decision step | turn resolver, runtime state | run outside deterministic/recoverable context if recovery matters |
| `EncounterRecoveryService` | load snapshot, rebuild resumable state, reject invalid resume | repository, runtime | restore from client memory only |
| `EncounterSettlementCoordinator` | final durable result request | runtime, player/meta service | grant rewards twice or through multiple paths |
| `NotifyChannel` | optional battle update push | application service, gateway/session | replace authoritative submit response |

---

## 3. Core Flows

### Open

1. client calls `Encounter_Open` or equivalent RPC
2. API validates session and feature access through common infrastructure
3. encounter service checks for an existing reusable active encounter
4. service creates encounter state from config, player snapshot, and seed data if needed
5. repository stores initial snapshot or create record
6. service returns initial battle view and encounter token

Opening should be idempotent for the same active run when resume is supported.

### Submit Action

1. client sends action with `encounterId` and `actionId` or sequence
2. API validates session and routes to encounter service
3. encounter validates ownership, phase legality, and duplicate action
4. turn resolver applies authoritative logic
5. effect pipeline resolves triggered effects and cleanup
6. repository persists checkpoint at the designed boundary
7. service returns authoritative result, delta, and next-phase info

Design for deterministic recovery, but do not force lockstep unless the product requires it.

### Complete

1. encounter reaches success, fail, surrender, or timeout
2. runtime computes result and reward intent
3. settlement coordinator sends one idempotent request to player/meta service
4. player/meta service writes durable result by `encounterId`, result ID, or transaction key
5. encounter is marked `completing` or `completed`
6. new actions are rejected and final result is returned

### Resume

1. client reopens or resumes the same encounter
2. service loads active snapshot
3. service verifies ownership, token, timeout, and resumable state
4. recovery service rebuilds authoritative runtime state
5. service returns latest authoritative view

Prefer resume-by-snapshot over full action-log replay unless replay is a product feature.

---

## 4. Failure Rules

Write these rules explicitly before implementation:

- repeated submit with the same `actionId` must not apply twice
- action executed but response lost returns the same logical result on retry
- encounter crash recovers from the last valid checkpoint or fails explicitly
- corrupted snapshot fails closed and follows product compensation rules
- settlement retries are safe by `encounterId`, result ID, or transaction key
- player/meta service outage moves encounter to `settlement_pending` or declared failure state
- timeout resolves encounter into a known terminal state
- once encounter enters `completing` or `completed`, new actions are rejected

Good first-production defaults:

- checkpoint at turn or phase boundaries when recovery matters
- no replay-driven recovery unless replay/audit is a product feature
- no full event-sourcing requirement by default

---

## 5. Minimal Build Order

Recommended order:

1. keep player and encounter as separate modules, even if deployed together
2. encounter open with create-or-resume behavior
3. one action submission loop with idempotency
4. turn or phase progression
5. snapshot persistence at chosen boundary
6. completion and settlement to player/meta service
7. resume from authoritative snapshot
8. logs, metrics, encounter inspection, and settlement retry visibility
9. split encounter into an independent service only if load or release pressure justifies it

Do not split player and encounter into separate services on day one unless actual runtime pressure requires it.

---

## 6. Review Checklist

Before calling an encounter design ready, verify:

- encounter ownership is single-writer
- every retryable action has idempotency
- checkpoint policy is explicit
- settlement path is single and durable
- merged deployment still keeps player and encounter module boundaries clear
- crash, retry, timeout, and resume behavior are written down
- resume is based on authoritative snapshot, not client memory
- replay/event sourcing is used only when justified
