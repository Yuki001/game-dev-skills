# Systems Index: [Game Title]

> **Status**: Draft | In Review | Approved
> **Last Updated**: [Date]
> **Source Overview**: gat/overview/game.md

## Overview

- Notes:

> **Note on paths**: This index is the GLOBAL system registry — the system list,
> its dependencies, and priorities. Per-system GDDs, content-data, and art docs
> are written per milestone under `gat/milestone/m{N}-<name>/<system>/` as
> `<system>-gdd-m{N}.md`, `<system>-data-m{N}.md`, and `<system>-art-m{N}.md`.
> The "Designed In Milestones" column records which milestones have designed
> each system. Game name, core loop, and pillars live in `gat/overview/game.md`
> (linked above) — not restated here.

## Systems Enumeration

> The Depends On column is the single source of truth for the dependency graph.
> Authoring order and per-milestone sequencing belong in the milestone plan
> (`gat/milestone/milestone.md`); system-level risks belong in each milestone's
> `m{N}-brief.md`.

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

## Layer Guide

| Layer | Use For |
|-------|---------|
| Foundation | lowest-level systems everything else builds on (input, state, save) |
| Core | primary gameplay systems that define the moment-to-moment experience |
| Feature | secondary systems layered on top of Core (progression, economy, meta) |
| Presentation | player-facing output systems (UI, audio, narrative delivery) |

> Layers are a loose build-order hint (Foundation → Core → Feature →
> Presentation), not a hard dependency. The Depends On column is still the
> authoritative dependency graph.

## Open Questions

| Question | Owner | Resolution |
|----------|-------|------------|
| [Question] | | Pending |
