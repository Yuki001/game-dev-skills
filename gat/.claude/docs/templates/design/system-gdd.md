# System GDD: [System Name]

> **Status**: Draft | In Review | Approved | Implemented
> **Category**: Core | Gameplay | Progression | Economy | UI | Audio | Narrative | Meta
> **Priority**: MVP | Vertical Slice | Alpha | Later
> **Layer**: Foundation | Core | Feature | Presentation
> **Last Updated**: [Date]
> **Milestone**: [e.g. M1 — fill with the milestone this GDD is scoped to]
> **Source Overview**: gat/overview/game.md
> **Source Index**: gat/overview/systems-index.md
> **Milestone Brief**: gat/milestone/m{N}-<name>/m{N}-brief.md

## 1. Summary & Goal

[2-3 sentences describing what this system is, what the player experiences, and why it exists.]

- **Does**: [what this system does]
- **Boundaries**: [what it must not own — which adjacent system owns that responsibility]

> **Style Rule — No Pseudocode**: GDDs define rules, behaviors, and parameters using natural language and mathematical formulas. Do NOT write pseudocode blocks, data structures, or algorithm descriptions. Implementation (code architecture, data structures, algorithms, optimization) is owned by downstream engineering workflow, not by the designer.

> **Quick Reference** - Depends On: `[System names or none]` | Related Art Doc: `gat/milestone/m{N}-<name>/<system>/<system>-art-m{N}.md`

> **Scope note**: This GDD is scoped to the milestone named above. A later
> milestone may redefine this system differently — additions, modifications, or
> conflicts with an earlier milestone's version are legitimate iteration.

## 2. Player Experience

- What the player feels:
- What the player does:

> Keep this to one or two lines. Express success/failure as measurable
> Acceptance Criteria in §6, not as subjective "feels good" language here.

## 3. Detailed Design

### Core Rules

1. [Rule]
2. [Rule]

### States And Transitions

| State | Entry Condition | Exit Condition | Behavior |
|-------|-----------------|----------------|----------|
| [State] | | | |

### Interactions With Other Systems

> One table for all cross-system relationships: data flow (Input/Output),
> dependency direction, and ownership notes. Use this instead of separate
> Inputs/Outputs or Dependencies sections.

| Other System | Direction | Input From Them | Output To Them | Ownership Notes |
|--------------|-----------|-----------------|----------------|-----------------|
| [System] | Depends on / Used by | | | [Which system owns which value or decision] |

## 4. Formulas & Parameters

### [Formula Name]

```text
result = [expression]
```

> Use mathematical notation to describe design formulas. Do NOT write implementation pseudocode (loops, conditionals, variable assignments). Keep formulas at the design level — what is computed, not how the engine computes it.

> One table covers both formula variables and tuning knobs. Mark a parameter
> tunable when the designer expects to adjust it during balancing.

| Name | Type | Range | Source | Tunable? | Effect Of Increase | Effect Of Decrease | Description |
|------|------|-------|--------|----------|--------------------|--------------------|-------------|
| [Name] | int / float / bool | | | Yes / No | | | |

**Expected output range**:
**Worked example**:

## 5. Edge Cases

> **As-needed** — omit unless the system has boundary behavior worth calling out separately. Otherwise fold edge behavior into Core Rules (§3) or Acceptance Criteria (§6).

| Scenario | Expected Behavior | Rationale |
|----------|-------------------|-----------|
| [Scenario] | | |

## 6. Acceptance Criteria

- [ ] [Specific, testable criterion]
- [ ] [Specific, testable criterion]
- [ ] Performance or implementation constraint if relevant

## 7. UI Requirements

> **As-needed** — omit this section for systems with no player-facing UI.

| Information | Display Location | Update Frequency | Condition |
|-------------|------------------|------------------|-----------|
| [Info] | | | |

## 8. Feedback Events

> List feedback event names only. The system art doc
> (`<system>-art-m{N}.md`) expands each event with visual/audio needs and
> priority — do not duplicate that expansion here.

- [Event name]
- [Event name]

## 9. Open Questions

| Question | Owner | Resolution |
|----------|-------|------------|
| [Question] | | Pending |
