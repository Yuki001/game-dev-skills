# Gameplay Content Editor Architecture

**Contents**

1. Overview
2. Editor Types
3. Common Mechanisms and Constraints
4. Summary

## 1. Overview

A gameplay content editor is an authoring application for game-specific rules and content: levels, skills, buffs, items, quests, dialogue, behavior trees, progression data, and similar domain objects. It does not replace engine-native editors for scenes, models, animation, VFX, materials, or audio.

Treat the content editor as an independent logical application even when its UI is embedded in a game engine, a web portal, a spreadsheet extension, or an in-game development tool. Define its domain model, data ownership, validation, and publishing boundary independently from its host.

The editor should turn designer intent into valid, versioned, reviewable runtime content. Its main responsibilities are to:

- Express content in the vocabulary of game design rather than engine internals.
- Make references, dependencies, flows, and constraints visible.
- Prevent invalid content or report it before runtime.
- Convert authoring-friendly source data into runtime-ready artifacts.
- Support preview, debugging, migration, bulk editing, and collaboration.
- Scale content production without scaling manual engineering work at the same rate.

Select the editor form from the dominant structure of the content. Homogeneous records fit tables; complex objects fit structured forms; branching logic fits graphs; spatial gameplay fits level tools; time-oriented processes fit timelines. Do not force every domain into one universal editor.

## 2. Editor Types

### 2.1 Selection Guide

| Editor type | Dominant structure | Typical content |
|---|---|---|
| Database and table | Homogeneous records, fields, and relations | Items, actors, enemies, classes, drops, economy, progression |
| Structured object | One domain object with nested parts | Skills, buffs, equipment, quest definitions, level parameters |
| Graph and logic | Nodes, edges, branches, and dependencies | Behavior trees, state machines, skill flow, quests, dialogue, tutorials |
| Gameplay level | Spatial anchors plus gameplay rules | Spawns, encounters, waves, triggers, objectives |
| Timeline and sequence | Tracks, clips, steps, and events | Tutorials, narrative flow, skill phases, level sequences |
| Specialized visual | A domain-specific visual relationship | Tech trees, drop trees, curves, matrices, relationship graphs |
| Integrated workspace | Multiple content types with cross-references | RPG-style databases, campaign tools, live content portals |

### 2.2 Database and Table Editors

Use a database or table editor for large sets of similarly shaped records that require filtering, comparison, statistics, and bulk changes. RPG databases, card catalogs, progression tables, and drop configurations are common examples.

Model the content as databases or categories containing typed records. Give every record a stable ID; use its name only for display and search. Define each field through a schema that specifies its type, default value, range, enumeration, reference target, and editing control.

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

Validate unique keys, references, ranges, probability or weight rules, progression continuity, and domain-specific relationships. Report errors at the table, record, and field level.

During compilation, resolve references, calculate derived fields, build indices, and remove editor-only metadata. Do not make runtime code depend on cell coordinates, column order, or display names.

When a row grows into a deeply nested object that is difficult to compare in tabular form, move that content to a structured object editor instead of continually adding columns.

### 2.3 Structured Object Editors

Use a structured object editor for a domain object composed of nested parts, optional modules, typed variants, and external references. Skills, buffs, equipment, encounters, and complex quest definitions often fit this form.

```text
Content Object
├─ Identity / Type
├─ Basic Fields
├─ Optional Modules
├─ Nested Objects / Lists
└─ External References
```

Organize fields by domain meaning rather than serialization layout. For example, a skill editor may group casting requirements, costs, targeting, phases, effects, and presentation references even when runtime data stores them differently.

Provide:

- Type-specific sections and controls.
- Add, remove, reorder, and summarize nested parts.
- Copy, compare, and extract reusable fragments.
- Templates with explicit copy, inheritance, or composition semantics.
- Domain controls such as target selectors, condition builders, and effect lists.
- A computed view showing inherited and defaulted values.

Do not mix template semantics. A copied object is independent; an inherited object stores overrides; a composed object references reusable parts. Ambiguous propagation makes the effect of later edits unpredictable.

Validate required modules, type-specific fields, ordering, mutually exclusive options, reference compatibility, and template overrides. Use the real runtime implementation for rule evaluation or simulation whenever correctness matters; do not maintain a second business implementation only for editor preview.

Compile authoring structures into explicit runtime descriptors. Include stable type identifiers and format versions rather than relying on editor class names or reflection paths.

### 2.4 Graph and Logic Editors

Use a graph editor when connections, branches, parallel paths, dependencies, or reusable subflows are central to the content. Behavior trees, dialogue, quests, tutorials, and skill execution flows have different graph semantics even if they share graph UI infrastructure.

A graph normally contains stable nodes, typed ports, edges, parameters, and optional local variables:

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

Keep node and edge identities stable across renaming, reordering, and visual repositioning. Store visual layout separately from execution semantics so moving a node does not change runtime behavior.

Define the semantics of each graph family explicitly:

- Which node and port types are allowed.
- Whether flow, data, or both travel across an edge.
- How order, branching, interruption, and parallel execution work.
- Which scopes contain variables and bindings.
- Whether cycles and recursive subgraphs are legal.

#### Behavior Tree Editors

A behavior tree editor is a specialized graph editor with tree semantics:

```text
Behavior Tree
└─ Root
   └─ Nodes
      ├─ Composite
      ├─ Decorator
      └─ Condition / Action
```

Reuse generic graph infrastructure for selection, layout, stable IDs, undo/redo, serialization, and runtime highlighting. Enforce behavior-tree rules separately: parent-child hierarchy, child order, composite execution policy, decorator constraints, status propagation, interruption, and blackboard access.

Use behavior trees primarily for hierarchical and reactive decision logic, especially AI. They can also support skills or encounters when the content genuinely follows selector/sequence-style decision semantics; do not use them merely because a graph view is convenient.

#### State Machine Editors

A state machine editor is a specialized directed graph in which nodes are states and edges are transitions:

```text
State Machine
├─ States
│  └─ Enter / Update / Exit
└─ Transitions
   ├─ Source / Target
   └─ Condition / Priority
```

Reuse the graph canvas and editing services, but define state-machine-specific semantics for initial states, transition conditions, priority, re-entry, interruption, and state lifecycle. Add hierarchy, parallel regions, or history only when the runtime model supports them explicitly.

Use state machines for AI modes, character states, skill casting phases, interaction flow, and other mutually exclusive or lifecycle-oriented behavior. They often appear as a sub-editor inside a larger AI, character, or skill editor.

Provide node search, contextual creation, typed connection feedback, grouping, comments, subgraphs, and reference navigation. Preserve stable node IDs so layout changes do not invalidate debug mappings or create noisy data changes.

Validate entry and exit requirements, unreachable nodes, illegal cycles, missing ports, type mismatches, invalid parallel behavior, recursive dependencies, and variable scope. Report each problem against a node or edge and focus it directly in the editor.

Make runtime debugging a first-class capability:

- Highlight active nodes and execution paths.
- Show node state, variables, blackboards, and port values.
- Support breakpoints, stepping, and recorded execution traces where practical.
- Map runtime errors and compiled instructions back to source node IDs.

Interpret small graphs directly when simplicity is more important. For larger, performance-sensitive, or deterministic systems, compile graphs into compact node arrays, state machines, instruction streams, or generated code. Keep source-to-runtime mappings in every mode.

Do not use a graph when the content is fundamentally a field set or an ordered list. Visual complexity is not evidence that a graph is the correct model.

### 2.5 Gameplay Level Editors

Use a gameplay level editor to author spatial gameplay meaning above an engine scene or an abstract map. It should describe rules and relationships, not replace modeling, terrain, lighting, VFX, or other engine-native editing.

Typical content has the following shape:

```text
Gameplay Level
├─ Spatial Structure
│  └─ Regions, paths, rooms, and anchors
├─ Actors and Spawns
├─ Encounters and Waves
├─ Triggers and Objectives
└─ References and Variants
```

Choose views by structure: spatial placement for anchors and regions, grids for discrete areas, topology graphs for rooms and routes, tables for waves, and logic graphs only for genuinely branching level flow. Multiple views should edit one shared content model rather than duplicate the same facts.

Reference stable gameplay anchors instead of long-lived scene hierarchy paths or object names. Art restructuring should not silently break gameplay data.

Validate required entrances and objectives, reachable completion paths, spawn and region references, wave closure, trigger ordering, difficulty coverage, and content budgets. Provide quick entry at a selected stage, trigger and region visualization, wave simulation, and objective-state inspection through the real level runtime.

Compile level content by resolving anchors, expanding templates, building trigger and objective indices, and packaging data by level or region.

### 2.6 Timeline and Sequence Editors

Use a timeline for business content organized primarily by time or ordered steps: tutorials, narrative commands, skill phases, boss phase transitions, and level event sequences. Reference animation, audio, or VFX assets without taking responsibility for editing them.

Model sequences as tracks containing clips and instantaneous markers, with explicit bindings to gameplay targets:

```text
Sequence
├─ Tracks
│  ├─ Binding
│  └─ Clips
└─ Markers / Events
```

Provide snapping, range editing, multi-track alignment, reusable clips, nested sequences, and time preview.

Validate required tracks and bindings, illegal overlap, phase boundaries, referenced content, and waits or jumps that can prevent completion. Display the current time, active clips, pending waits, and emitted events during runtime debugging.

If branching dominates the flow, use a logic graph and let its nodes invoke sequences. Avoid hiding a complex state machine inside timeline clips.

### 2.7 Specialized Visual Editors

Use a specialized editor when a domain relationship is technically storable in tables but substantially easier to understand through a dedicated view. Examples include technology trees, drop trees, progression curves, faction relationships, and tag or interaction matrices.

```text
Domain Model
├─ Entities / Values
├─ Relations / Curves / Matrix
└─ Specialized View
```

Treat the visualization as another view of the authoritative source data, not as a second copy. Add domain-specific analysis such as probability totals, cyclic prerequisites, isolated nodes, unreachable unlocks, and abnormal curve intervals.

Prefer a focused editor with strong domain constraints over a generic canvas with weak semantics.

### 2.8 Integrated Content Workspaces

Combine several editor types when a project has many related content domains. An RPG-style database, campaign tool, or live content portal is an integrated workspace rather than a single universal editor.

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

Keep specialized editing behavior inside the appropriate editor. The workspace coordinates context and workflow; it should not flatten all content into one interaction model.

## 3. Common Mechanisms and Constraints

### 3.1 Domain Model and Data Pipeline

Define domain concepts, relations, and invariants before designing the UI. Present skills, effects, objectives, conditions, and other design concepts instead of raw serialization fields or engine components.

Prefer a one-way production pipeline:

```text
Authoring Source -> Validation -> Compile/Bake -> Runtime Data -> Package/Publish
```

Optimize source data for editing, review, and version control. Optimize runtime data for loading, lookup, memory, networking, and compatibility. Treat generated runtime data as reproducible output, not as an authoring source.

### 3.2 Identity, References, and Dependencies

- Assign stable IDs to durable content and graph nodes.
- Treat names, paths, and list positions as mutable presentation data.
- Type-check references and maintain reverse-reference lookup.
- Show impact before delete, move, or replacement operations.
- Detect missing, cyclic, and illegal cross-package dependencies.

### 3.3 Validation, Versioning, and Migration

Run cheap validation while editing, complete validation on save or submission, and release-gating validation before publishing. Cover field, object, cross-object, global, and package-level rules. Every issue should identify the content, location, rule, severity, and practical correction.

Version authoring schemas and runtime formats independently where needed. Implement explicit, batchable, repeatable migrations for field renames, type changes, node replacement, and structural changes. Report migration results and retire obsolete compatibility paths after an agreed support window.

### 3.4 Transactions and Collaboration

Treat a meaningful edit as one transaction: deleting a node and its edges, replacing references, applying a template, or updating a group of records. Support undo, redo, and rollback at that level.

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

Drive multiple stages from shared type registration or metadata where practical. Unknown types must fail visibly rather than lose data silently.

Use the formal runtime or shared domain implementation for preview and simulation when correctness matters. Editor-only approximations are acceptable only when their limits are visible.

### 3.6 Publishing and Change Control

Track draft, validated, approved, and published states when the production process requires them. A published artifact should identify its source revision, compiler version, dependencies, and runtime format.

For hot-updatable content, define which changes are safe during an active session, how old and new versions coexist, how ongoing battles or quests retain their content version, and how rollback preserves consistency with player state.

## 4. Summary

Choose an editor by the shape of the content:

- Use tables for homogeneous records.
- Use structured forms for complex domain objects.
- Use graphs for connections and branching execution.
- Use gameplay level tools for spatial rules.
- Use timelines for time-oriented sequences.
- Use specialized views for domain relationships.
- Use an integrated workspace to connect multiple editor types.

Use the following mapping to select an editor from the game data or system being authored. The primary editor represents the dominant structure; companion editors add views without becoming a second source of truth.

| Game data or system | Dominant data shape | Primary editor | Useful companion |
|---|---|---|---|
| Items, actors, enemies, classes, and other master catalogs | Many homogeneous records | Database and table editor | Structured object editor for complex records |
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

Let different editors keep their appropriate interaction models while sharing IDs, references, schemas, validation, migration, compilation, publishing, and runtime-debug protocols.

Review a content-editor architecture by asking:

- Does it expose the language of game design rather than engine internals?
- Does the editor type match the dominant content structure?
- Is there one authoritative authoring source?
- Are runtime artifacts generated through a clear boundary?
- Can references and change impact be traced?
- Can invalid content be rejected before runtime?
- Does preview use the formal business implementation?
- Can new domain types extend the complete toolchain coherently?
- Can content be diffed, migrated, reviewed, and published reliably?
- Has generality reduced the efficiency of the actual authoring task?

A good content editor makes valid content easy to create, invalid content difficult to produce, and runtime problems traceable back to specific authored data.
