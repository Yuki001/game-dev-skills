# Gameplay Content Editor Architecture

**Contents**

1. Overview
2. Editor Types
3. Common Mechanisms and Constraints
4. Summary

## 1. Overview

A gameplay content editor authors game-specific rules and content. It complements rather than replaces engine-native scene, model, animation, VFX, material, or audio tools.

Treat it as an independent logical application even when embedded in another host. Define its domain model, ownership, validation, preview/debug, migration, compilation, and publishing boundaries explicitly.

Choose the editor form from the content's dominant structure: records use tables, nested objects use forms, branching logic uses graphs, spatial gameplay uses spatial editors, and ordered events use timelines. Do not force every domain into one universal editor.

## 2. Editor Types

### 2.1 Selection Guide

| Editor type | Dominant structure | Typical content |
|---|---|---|
| Database and table | Homogeneous records, fields, and relations | Items, actors, enemies, classes, drops, economy, progression |
| Structured object | One domain object with nested parts | Skills, buffs, equipment, quest definitions, level parameters |
| Graph and logic | Nodes, edges, branches, and dependencies | Behavior trees, state machines, skill flow, quests, dialogue, tutorials |
| Gameplay level | Spatial anchors plus gameplay rules | Spawns, encounters, waves, triggers, objectives |
| Gameplay actor | Spatial form plus actor metadata and sequences | Actors, boxes, sockets, anchors, collision volumes, skill sequences |
| Timeline and sequence | Tracks, clips, steps, and events | Tutorials, narrative flow, skill phases, level sequences |
| Specialized visual | A domain-specific visual relationship | Tech trees, drop trees, curves, matrices, relationship graphs |
| Integrated workspace | Multiple content types with cross-references | RPG-style databases, campaign tools, live content portals |

### 2.2 Database and Table Editors

Use a database or table editor for large sets of similarly shaped records. Model typed fields through schemas, give each record a stable ID, and use names only for display and search.

```text
Database
└─ Table / Category
   └─ Record
      └─ Field
```

Provide operations that match work on large data sets:

- Search and filter by category, tag, field, and reference.
- Compare records and apply bulk edits or formulas.
- Show references by readable names while storing stable IDs.
- Provide role-specific views over the same source records.
- Find all content that refers to a selected record.
- Visualize curves, probability distributions, and economic totals when useful.

Validate at table, record, and field level. Compile by resolving references, calculating derived fields, building indices, and removing editor-only metadata; runtime code must not depend on cell coordinates, column order, or display names. Move deeply nested rows to a structured object editor.

### 2.3 Structured Object Editors

Use a structured object editor for one domain object with nested parts, optional modules, typed variants, and external references.

```text
Content Object
├─ Identity / Type
├─ Basic Fields
├─ Optional Modules
├─ Nested Objects / Lists
└─ External References
```

Organize fields by domain meaning rather than serialization layout.

Provide:

- Type-specific sections and controls.
- Add, remove, reorder, and summarize nested parts.
- Copy, compare, and extract reusable fragments.
- Templates with explicit copy, inheritance, or composition semantics.
- Domain controls such as target selectors, condition builders, and effect lists.
- A computed view showing inherited and defaulted values.

Keep copy, inheritance, and composition semantics distinct. Validate modules, variants, ordering, references, and overrides through the real runtime implementation where correctness matters. Compile to explicit runtime descriptors with stable type IDs and format versions.

### 2.4 Graph and Logic Editors

Use a graph editor when connections, branches, parallel paths, dependencies, or reusable subflows dominate. Model stable nodes, typed ports, edges, parameters, and optional local variables:

```text
Graph
├─ Nodes
│  ├─ NodeId
│  ├─ NodeType
│  ├─ Parameters
│  └─ Ports
└─ Edges
   ├─ EdgeId
   ├─ SourcePort
   └─ TargetPort
```

Keep visual layout separate from execution semantics, and define each graph family's rules:

- Which node and port types are allowed.
- Whether flow, data, or both travel across an edge.
- How order, branching, interruption, and parallel execution work.
- Which scopes contain variables and bindings.
- Whether cycles and recursive subgraphs are legal.

#### Behavior Tree Editors

A behavior tree editor applies tree semantics to shared graph infrastructure:

```text
Behavior Tree
└─ Root
   └─ Nodes
      ├─ Composite
      ├─ Decorator
      └─ Condition / Action
```

Enforce hierarchy, child order, composite/decorator rules, status propagation, interruption, and blackboard access. Use behavior trees for genuinely hierarchical, reactive decision logic.

#### State Machine Editors

A state machine editor uses states as nodes and transitions as edges:

```text
State Machine
├─ States
│  └─ Enter / Update / Exit
└─ Transitions
   ├─ Source / Target
   └─ Condition / Priority
```

Define initial states, transitions, priority, re-entry, interruption, and lifecycle explicitly. Add hierarchy, parallel regions, or history only when supported by runtime semantics.

Provide node search, contextual creation, typed connections, grouping, subgraphs, and reference navigation. Validate graph rules against specific nodes or edges while preserving stable source-to-runtime IDs.

Make runtime debugging a first-class capability:

- Highlight active nodes and execution paths.
- Show node state, variables, blackboards, and port values.
- Support breakpoints, stepping, and recorded execution traces where practical.
- Map runtime errors and compiled instructions back to source node IDs.

Interpret small graphs directly or compile larger ones, but keep source-to-runtime mappings. Do not use a graph for content that is fundamentally a field set or ordered list.

### 2.5 Gameplay Level Editors

Use a gameplay level editor to author spatial gameplay rules above an engine scene or abstract map:

```text
Gameplay Level
├─ Spatial Structure
│  └─ Regions, paths, rooms, and anchors
├─ Actors and Spawns
├─ Encounters and Waves
├─ Triggers and Objectives
└─ References and Variants
```

Use spatial, grid, topology, table, or graph views over one shared model. Reference stable gameplay anchors rather than scene paths. Validate reachability, references, ordering, difficulty, and budgets through the real level runtime, then compile by level or region.

### 2.6 Gameplay Actor Editors

Use a gameplay actor editor when an actor's definition is inseparable from a spatial representation. It edits the actor itself plus spatial metadata such as hit, hurt, collision, interaction, detection, or targeting boxes.

```text
Gameplay Actor
├─ Actor Definition
├─ Spatial Representation
│  ├─ Model / Shape Preview
│  ├─ Boxes / Volumes
│  └─ Sockets / Anchors
├─ Metadata and References
└─ Optional Skill Timeline
   └─ Tracks, Phases, Events, and Bindings
```

Provide:

- Actor identity, type, properties, components, and content references.
- Add, remove, duplicate, name, classify, and group spatial boxes or volumes.
- Direct manipulation of shape, size, transform, attachment, tags, and gameplay purpose.
- Stable local coordinate spaces and attachment to the actor root, bones, sockets, or anchors.
- An optional timeline for actor skill sequences, activation windows, phases, events, and bindings.
- Scrubbing and runtime-backed preview of animation, movement, boxes, events, and skill execution.

Keep the actor catalog in a database when bulk comparison is useful, and open this editor for spatial authoring. Reference animation, models, VFX, and audio without replacing their native tools. Validate stable IDs, shapes, attachments, coordinate spaces, timeline bindings, event order, and referenced content.

### 2.7 Timeline and Sequence Editors

Use a timeline for content organized by time or ordered steps. Model tracks, clips, markers, and explicit gameplay bindings:

```text
Sequence
├─ Tracks
│  ├─ Binding
│  └─ Clips
└─ Markers / Events
```

Provide snapping, range editing, alignment, reusable clips, nested sequences, and preview. Validate tracks, bindings, overlaps, phase boundaries, references, waits, and jumps. If branching dominates, use a logic graph that invokes sequences.

### 2.8 Specialized Visual Editors

Use a specialized editor when a domain relationship is easier to understand through a dedicated view than a table:

```text
Domain Model
├─ Entities / Values
├─ Relations / Curves / Matrix
└─ Specialized View
```

Keep the visualization as a view of authoritative source data. Prefer strong domain constraints and analysis over a generic canvas.

### 2.9 Integrated Content Workspaces

Use an integrated workspace to coordinate several editor types without flattening their interaction models:

```text
Content Workspace
├─ Shared Catalog / IDs
├─ Editor Modules
│  └─ Tables, objects, graphs, levels, and sequences
└─ Shared Services
   └─ Search, validation, build, and publish
```

Unify the surrounding production context:

- Project, package, and module navigation.
- Global search, stable IDs, and reference selection.
- Cross-type navigation and reverse-reference lookup.
- Validation results and direct problem navigation.
- Change sets, approval state, ownership, and release version.
- Links from a business object to its records, graphs, levels, and preview environment.

Keep specialized editing inside its appropriate editor; share navigation, IDs, references, validation, build, and publishing services.

## 3. Common Mechanisms and Constraints

### 3.1 Domain Model and Data Pipeline

Define domain concepts and invariants before the UI, then use a one-way production pipeline:

```text
Authoring Source -> Validation -> Compile/Bake -> Runtime Data -> Package/Publish
```

Optimize source data for authoring and runtime data for execution. Treat generated data as reproducible output.

### 3.2 Identity, References, and Dependencies

- Assign stable IDs to durable content and graph nodes.
- Treat names, paths, and list positions as mutable presentation data.
- Type-check references and maintain reverse-reference lookup.
- Show impact before delete, move, or replacement operations.
- Detect missing, cyclic, and illegal cross-package dependencies.

### 3.3 Validation, Versioning, and Migration

Run cheap validation while editing, complete validation on save, and release-gating validation before publishing. Issues must identify location, rule, severity, and correction. Version schemas and runtime formats explicitly; make migrations batchable, repeatable, and reported.

### 3.4 Transactions and Collaboration

Treat a meaningful multi-part edit as one undoable transaction.

Organize source files for collaboration:

- Use stable serialization and ordering to reduce noisy diffs.
- Split files by meaningful ownership and change boundaries.
- Separate authored sources from generated outputs.
- Use locks, change sets, or domain-aware merge tools for content that cannot merge reliably.

### 3.5 Extensibility and Runtime Consistency

Keep the extension chain explicit:

```text
Domain Type -> Schema -> Editor -> Validation -> Compiler -> Runtime -> Debug View
```

Drive stages from shared type registration where practical. Fail visibly on unknown types, and use the formal runtime or shared domain implementation for correctness-sensitive preview.

### 3.6 Publishing and Change Control

Track production states when required. Published artifacts must identify source revision, compiler, dependencies, and runtime format. For hot updates, define version coexistence, session pinning, safe changes, and rollback behavior.

## 4. Summary

Choose an editor by the shape of the content:

- Use tables for homogeneous records.
- Use structured forms for complex domain objects.
- Use graphs for connections and branching execution.
- Use gameplay level tools for spatial rules.
- Use gameplay actor tools for actors with spatial metadata and skill sequences.
- Use timelines for time-oriented sequences.
- Use specialized views for domain relationships.
- Use an integrated workspace to connect multiple editor types.

Use the following mapping to select an editor from the game data or system being authored. The primary editor represents the dominant structure; companion editors add views without becoming a second source of truth.

| Game data or system | Dominant data shape | Primary editor | Useful companion |
|---|---|---|---|
| Items, classes, and other master catalogs | Many homogeneous records | Database and table editor | Structured object editor for complex records |
| Actors, characters, enemies, and interactive entities | Spatial form plus actor metadata | Gameplay actor editor | Database for catalogs; timeline for skill sequences |
| Balance values, economy parameters, and progression tables | Records, formulas, and numeric series | Database and table editor | Curve, statistics, or distribution view |
| Skills, buffs, equipment, and effect definitions | Nested typed objects and reusable parts | Structured object editor | Graph editor for branching execution; timeline editor for phases, timing, and ordered events |
| Quests, dialogue, tutorials, and guided flows | Branches, conditions, stages, and references | Graph and logic editor | Database or structured forms for content records; timeline for fixed sequences |
| AI behavior trees, state machines, and decision logic | Executable hierarchy or transition graph | Behavior-tree or state-machine editor (specialized graph) | Structured object editor for parameters and blackboards |
| Gameplay levels, spawns, regions, triggers, and objectives | Spatial anchors plus gameplay rules | Gameplay level editor | Tables for waves; graphs for branching level flow |
| Encounters, enemy waves, and boss phases | Ordered groups, conditions, timing, and spatial bindings | Gameplay level editor | Table or timeline editor depending on the dominant structure |
| Narrative sequences, tutorial steps, and timed gameplay events | Tracks, clips, steps, and markers | Timeline and sequence editor | Graph editor when branching becomes dominant |
| Technology trees, talent trees, and unlock paths | Dependency graph | Specialized visual editor | Database or structured object editor for node properties |
| Drop tables, reward pools, and weighted selections | Weighted records or hierarchy | Database and table editor | Drop-tree and probability-distribution view |
| Growth curves, formulas, and difficulty scaling | Functions and numeric curves | Specialized curve editor | Database and table editor for source parameters |
| Factions, tags, affinities, and interaction rules | Relation or rule matrix | Specialized matrix editor | Database editor for entity definitions |
| World maps, campaign routes, and room topology | Spatial or abstract topology | Specialized topology or gameplay level editor | Structured object editor for node and route properties |
| Procedural generation rules | Nested parameters, staged rules, or generation graph | Structured object or graph editor | Specialized preview, statistics, and seed inspection |
| Live events and scheduled content | Content records, schedules, rules, and references | Structured object or database editor | Timeline or calendar-style specialized view |
| Large cross-domain content sets | Multiple content models with dense cross-references | Integrated content workspace | Specialized editor modules for each content type |

Keep one authoritative source and make IDs, references, validation, compilation, migration, publishing, and runtime debugging consistent across editors. A good editor makes valid content easy to create and runtime problems traceable to authored data.
