# Systems Index: [Game Title]

> **Status**: Draft | In Review | Approved
> **Last Updated**: [Date]
> **Source Overview**: gat/overview/game.md

## Overview

- Game:
- Core loop anchor:
- Pillars most affected by system design:
- Notes:

> **Note on paths**: This index is the GLOBAL system registry. Per-system GDDs,
> content-data, and art docs no longer live beside this file — they are written
> per milestone under `gat/milestone/m{N}-<name>/<system>/` as
> `<system>-gdd-m{N}.md`, `<system>-data-m{N}.md`, and `<system>-art-m{N}.md`.
> The GDD/Art/Content Data columns below record which milestones have designed
> each system, not a single global path.

## Systems Enumeration

| Order | System | Category | Priority | Layer | Depends On | Status | Designed In Milestones | Notes |
|-------|--------|----------|----------|-------|------------|--------|------------------------|-------|
| 1 | movement | Core | MVP | Foundation | none | Planned | — | |

## Category Guide

| Category | Use For |
|----------|---------|
| Core | foundational interaction and state systems |
| Gameplay | systems that directly create the play experience |
| Progression | upgrades, unlocks, growth, metagame advancement |
| Economy | resources, costs, crafting, drops, rewards |
| UI | HUD, menus, interaction surfaces, player-facing feedback |
| Audio | music, SFX, audio-state management |
| Narrative | dialogue, quests, story delivery |
| Meta | accessibility, onboarding, analytics, settings |

## Priority Guide

| Priority | Meaning |
|----------|---------|
| MVP | required for the first meaningful playable slice |
| Vertical Slice | required for a polished representative demo |
| Alpha | needed for full feature breadth |
| Later | nice-to-have, polish, or deferred content |

## Dependency Map

### Foundation Layer

1. [System] - depends on: none

### Core Layer

1. [System] - depends on: [list]

### Feature Layer

1. [System] - depends on: [list]

### Presentation Layer

1. [System] - depends on: [list]

## Suggested Authoring Order

| Order | System | Why First | Effort | Notes |
|-------|--------|-----------|--------|-------|
| 1 | [System] | | S / M / L | |

## High-Risk Systems

| System | Risk Type | Why It Is Risky | Mitigation |
|--------|-----------|-----------------|------------|
| [System] | Design / Tech / Scope | | |

> **No global progress tracker here.** Per-system design progress is tracked in
> each milestone's `m{N}-brief.md` (Progress Tracker section). This index is the
> global system registry, not a progress dashboard.

## Open Questions

| Question | Owner | Resolution |
|----------|-------|------------|
| [Question] | | Pending |
