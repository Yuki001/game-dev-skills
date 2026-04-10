# Deterministic Sync, Lockstep, And Rollback

Reference for multiplayer architectures that synchronize **inputs and deterministic simulation** instead of synchronizing authoritative world state as snapshots or deltas.

Use this document for fighting games, RTS, deterministic tactics, and other systems where strict fairness, replayability, or rollback-based responsiveness matter more than server-authoritative state replication.

Use `multiplayer-overview.md` for authority-model selection, `multiplayer-protocol.md` for protocol naming and packet rules, and `multiplayer-server-architecture.md` for broader topology and ownership decisions.

---

## 1. Fit

Deterministic sync means:

- all peers or simulation nodes advance from the same initial state
- each step consumes the same ordered input set
- simulation must produce the same result for the same inputs

Use this family when:

- deterministic frame or step simulation is feasible
- input payload is much smaller than full state payload
- replay, rollback, or desync detection are real product requirements

---

## 2. Core Models

### Strict Lockstep

All participants wait for the required inputs for frame `N` before advancing frame `N`.

Main costs:

- latency is directly visible as input delay
- one slow or missing player can stall everyone unless fallback rules exist

### Delay-Based Input Sync

Clients intentionally buffer local input by a fixed delay so frame advancement is more stable.

Main costs:

- input delay is always present
- poor fit for highly timing-sensitive action gameplay

### Rollback Netcode

Clients predict missing remote inputs, simulate ahead locally, then rollback and resimulate when real inputs arrive.

Main costs:

- deterministic requirements are stricter
- rollback-safe simulation and presentation separation are hard
- debugging and desync tooling become mandatory

### Hybrid Deterministic Sync

Some products use deterministic sync only for one subsystem.

Rule:

- keep deterministic boundary explicit; do not leak non-deterministic systems into it

---

## 3. Authority And Ownership

Deterministic sync does not remove authority design. It changes where authority lives.

Hard rules:

- authoritative boundary is usually **input**, not world-state mutation packets
- one simulation instance must define the canonical frame index
- input ordering rules must be explicit
- session start state, random seed, and ruleset version must match exactly
- deterministic subsystem must not read external mutable state during simulation

---

## 4. Determinism Requirements

Deterministic sync is primarily an engineering constraint, not a transport trick.

The simulation must be deterministic across frame order, initial state, input order, RNG, arithmetic behavior, iteration order, and event scheduling.

Required controls:

- deterministic number or fixed-point arithmetic
- fixed simulation tick or step
- deterministic RNG with explicit seed and stream ownership
- stable collection iteration order
- no wall-clock reads during simulation
- no hidden dependency on thread timing
- no engine callback order that can differ across machines

---

## 5. Simulation Boundary

Keep these layers separate:

- deterministic simulation core for frame step and rule resolution
- transport/input for sequencing, retry, and jitter handling
- presentation for audiovisual playback and smoothing
- durable/meta for rewards, ranking, inventory, and progression

Rules:

- presentation must derive from simulation state, not mutate deterministic state directly
- expensive or non-rewindable behavior stays outside the deterministic core

---

## 6. Input And Frame Protocol

Deterministic sync protocol should be frame-oriented.

Common message families:

- `Frame_Input_Req`
- `Frame_Input_Notify`
- `Frame_All_Inputs_Notify`
- `Frame_Advance_Notify`
- `Frame_Hash_Notify`
- `Rollback_Notify`
- `Desync_Report_Notify`

Protocol rules:

- every input packet carries frame index
- duplicate input handling is explicit
- late input handling is explicit
- missing input policy is explicit
- frame confirmation and predicted frame are distinct concepts
- hash comparison cadence is explicit

---

## 7. Standard Runtime Flows

### Session Start

Default start flow:

1. all participants confirm identical ruleset version
2. session agrees on player order and identity mapping
3. deterministic seed and initial state are established
4. start frame is chosen
5. runtime begins collecting frame inputs

### Normal Frame Advance

Strict lockstep flow:

1. each participant submits input for frame `N`
2. runtime collects required inputs
3. frame `N` executes
4. optional frame hash is recorded
5. runtime advances to frame `N + 1`

Delay-based flow:

1. local input is buffered by configured delay
2. remote inputs are gathered within that buffer
3. runtime advances once the delayed frame is ready

Rollback flow:

1. local player submits input immediately
2. client predicts missing remote input if needed
3. runtime simulates ahead locally
4. actual remote input arrives later
5. if prediction differs, runtime rolls back to divergence frame
6. runtime resimulates to current frame

### Match Complete

Default completion flow:

1. deterministic runtime reaches terminal result
2. final agreed result is confirmed by host, server, or consensus rule
3. result is committed to backend or player service exactly once
4. replay or audit record is stored if required

---

## 8. Rollback-Specific Rules

Rollback adds additional architectural constraints around confirmed frame, predicted frame, rollback window, and resimulation cost.

Hard rules:

- simulation step must be fast enough to resimulate multiple frames in one render interval
- state snapshot or save-state format must be cheap to capture and restore
- deterministic side effects must be replayable
- presentation side effects must be suppressible, replay-safe, or derived

---

## 9. Desync Detection And Debugging

Desync handling is mandatory for deterministic systems.

Minimum required tools:

- frame or state hashing
- deterministic replay from recorded inputs
- divergence reports with frame number
- save-state inspection at the desync frame
- build or ruleset version tagging

Recommended desync workflow:

1. record frame number, players, build version, and session seed
2. compare state hashes at configured cadence
3. on mismatch, capture local deterministic snapshot and recent input window
4. replay both sides offline
5. identify first divergent frame and state field

If the team cannot replay and inspect desyncs offline, deterministic sync is under-tooled.

---

## 10. Persistence, Replay, And Recovery

Recommended choices by model:

- strict lockstep: input log + periodic hash
- delay-based sync: input log + periodic hash
- rollback: save states inside rollback window + optional replay log

---

## 11. Framework And Engine Fit

This architecture fits best when engine update order can be controlled, simulation can be isolated from presentation, game state is compact enough for replay or rollback, and target platforms have known deterministic behavior.

---

## 12. Build Order

Recommended implementation order:

1. isolate deterministic simulation core from presentation
2. make initial state and RNG fully reproducible
3. implement frame-indexed input protocol
4. add input logging and offline replay
5. add frame hash and desync tooling
6. choose one runtime model: strict lockstep, delay-based, or rollback
7. if using rollback, add save-state and resimulation pipeline
8. add reconnect or resume policy
9. integrate result commit into backend services

Do not attempt rollback before offline deterministic replay works.

---

## 13. Review Checklist

Before calling the design ready, verify:

- deterministic boundary is explicit
- initial state, seed, and version are reproducible
- every input is frame-indexed
- missing-input policy is explicit
- desync detection exists
- replay or snapshot recovery strategy is defined
- presentation does not mutate deterministic state
- rollback cost is measured if rollback is used
