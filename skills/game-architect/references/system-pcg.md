# Procedural Content Generation (PCG) System

Reference for PCG architecture decisions and technique selection. Organized by generation philosophy rather than content type — choose the right category first, then select the specific algorithm.

**IMPORTANT NOTE**: PCG techniques are rarely used in isolation. Most production systems combine multiple categories (e.g., grammar-based macro layout + WFC micro-tile synthesis + noise-based texturing). Select the dominant approach per layer, then compose.

---

## 0. Overview

### What is PCG?

Procedural Content Generation is the algorithmic creation of game content with limited or indirect user input. Content includes levels, terrain, quests, rules, textures, audio, and narrative.

### Why Use PCG?

- **Scale**: Generate vast worlds beyond manual authoring capacity (No Man's Sky, Minecraft).
- **Replayability**: Unique content per playthrough (roguelikes, Diablo).
- **Development Efficiency**: Reduce asset production cost and iteration time.
- **Adaptive Content**: Tailor content to player skill, preference, or behavior.
- **Creative Exploration**: Discover designs outside human intuition.

### Content Types & Dominant Techniques

| Content Type | Common Techniques | Chapters |
|:---|:---|:---|
| **Dungeons / Levels** | Space Partitioning, CA, WFC, ASP, Grammars | 1, 2, 4 |
| **Terrain / Landscapes** | Noise, Fractals, Erosion Simulation, SDF | 3, 5 |
| **Vegetation** | L-systems, Grammars | 4 |
| **Quests / Stories** | Planning (STRIPS/ADL), Graph Grammars | 5 |
| **Game Rules / Mechanics** | Evolutionary Design, Rule DSL | 6 |
| **Textures / Materials** | Noise, Math Nodes, Morphological Ops | 3, 8 |
| **Geometry / Assets** | Shape Grammars, Attribute-Driven, HDAs | 4, 8 |
| **Adaptive Content** | Experience-Driven, AI Director | 7 |

---

## 1. Constructive Methods

Direct, step-by-step algorithmic construction. No rollback, no evaluation. Extremely fast and deterministic.

### Technique Selection

| Technique | Applicability | Key Concepts |
|:---|:---|:---|
| **Space Partitioning** | Dungeon rooms, indoor levels | Recursive spatial subdivision (BSP, quadtree, grid); each partition becomes a room or zone |
| **Cellular Automata** | Caves, organic walls, terrain smoothing | Grid of cells with neighbor-count rules; iterate to convergence |
| **Agent-Based Diggers** | Corridors, organic dungeon carving | Autonomous agents walk and carve; behavior rules define shape |
| **Minimum Spanning Tree** | Corridor connectivity | Guarantees all rooms connected with minimum total path length |
| **Drunkard's Walk** | Irregular corridors, rivers | Random-walk agent carves path; produces natural-looking routes |
| **Node-Based Dataflow** | Terrain, assets, levels | Non-destructive procedural graph; parameterized for per-instance variation |
| **Attribute-Driven Generation** | Terrain decoration, material layering | Named geometry attributes drive downstream placement/shading decisions |
| **Chunk / Template Assembly** | Platform levels, rooms | Assemble from hand-authored library; fill variable slots procedurally |

### Implementation Notes

- **Space Partitioning**: Recursively subdivide a bounding rect (BSP: axis-aligned splits; quadtree: equal quadrants; grid: fixed cells) until leaf size threshold; place room inside each partition; connect siblings with corridors.
- **Cellular Automata**: Initialize grid with random fill ratio (~45% walls); apply birth/survival rules (e.g., B3/S12345) for 4–5 iterations; flood-fill to remove isolated regions.
- **Agent Diggers**: Define agent state (position, direction, budget); each step: move, carve, probabilistically turn or spawn child agents.
- **Connectivity**: After room placement, build a graph of room centers; run Kruskal's MST; optionally add ~15% extra edges for loops.
- **Node-Based Dataflow**: Procedural graph where each node applies an operation (blend, warp, threshold); non-destructive — change any node and downstream results update automatically. Author once as parameterized graph (HDA); expose key parameters for per-instance variation.
- **Attribute-Driven Generation**: Geometry carries named attributes (slope, altitude, curvature); downstream nodes read attributes to drive placement/shading decisions (e.g., "place snow where slope < 15° and altitude > 800").
- **Platform Generation**: Chunk-based (assemble from hand-authored library by difficulty curve), template instantiation (fill variable slots procedurally), or column-by-column (local rules per column transition for side-scrollers).


---

## 2. Constraint-Solving & Search Methods

Navigate a space of possibilities via fitness evaluation (soft constraints) or strict logical deduction (hard constraints).

### Technique Selection

| Technique | Constraints | Guarantees | Applicability |
|:---|:---|:---|:---|
| **Evolutionary / Genetic Algorithms** | Soft (fitness function) | None — best found so far | Maps, rules, weapons, tracks |
| **Genetic Programming** | Soft (fitness function) | None — best found so far | Terrain functions, expression trees |
| **Answer Set Programming (ASP)** | Hard (Boolean/SAT) | Globally valid or no solution | Playable dungeons, puzzle levels |
| **Wave Function Collapse (WFC) / CSP** | Local adjacency (hard) | Local consistency; may deadlock | Tile-based levels, textures, maps |

### Implementation Notes

- **Content Representation**: Direct (tile grid, parameter list) for simple content; Indirect/Generative (genome encodes a generator program) for complex content — small genome → large output. Parametric for tuning templates; Tree/Graph for rules and grammars; CPPN for spatially coherent patterns. Representation must support valid crossover — ill-defined crossover is a common source of degenerate offspring.
- **Evolutionary Algorithms**: Selection → Crossover → Mutation → Evaluate → Repeat. Fitness can be direct (measure content properties), simulation-based (play-test), or interactive (human rates).
- **Indirect encoding**: Small genome encodes a generator program; allows large outputs from compact representations. Representation must support valid crossover.
- **Genetic Terrain Programming**: Represent terrain as a mathematical expression tree; evolve via subtree crossover and node mutation. Fitness evaluates slope variance, peak count, navigability.
- **ASP**: Express rules as logical predicates in a solver (e.g., Clingo); guaranteed valid output or UNSAT. Exponential worst-case — practical for small-to-medium constraint sets.
- **WFC**: Cells start in superposition; collapse minimum-entropy cell first; propagate arc consistency to neighbors. On contradiction, backtrack or restart.
- **WFC Hybrid**: Use macro-logic graph (ASP/grammar) for room connectivity + WFC for micro-tile synthesis — combines global guarantees with local visual coherence.


---

## 3. Fractals, Noise & Mathematics

Mathematical functions generating continuous organic variation. Essential for natural environments and procedural texturing.

### Technique Selection

| Technique | Applicability | Key Concepts |
|:---|:---|:---|
| **Value Noise** | Simple heightmaps | Interpolate random values on a grid |
| **Gradient Noise (Perlin)** | Terrain, clouds, organic thresholds | Gradient vectors at grid points; smoother than value noise |
| **Simplex Noise** | High-dimension noise, fewer artifacts | Simplex lattice; faster and fewer directional artifacts than Perlin |
| **Fractal / fBm** | Mountain detail, realistic terrain | Sum multiple octaves of noise at increasing frequency, decreasing amplitude |
| **Diamond-Square** | Heightmap generation | Recursive midpoint displacement; produces fractal mountain terrain |
| **SDF + Marching Cubes** | 3D caves, overhangs, complex topology | Implicit surface defined by distance function; polygonized via Marching Cubes |
| **Math-Driven Material Synthesis** | Tileable textures, material layering | Noise + morphological ops composed as node graphs |

### Implementation Notes

- **Octave Stacking (fBm)**: `height = Σ (amplitude * noise(pos * frequency))` for each octave; typical: 6–8 octaves, lacunarity=2.0, persistence=0.5.
- **Domain Warping**: Feed noise output back as input offset — produces swirling, organic distortion.
- **Threshold Maps**: Apply noise as a mask (e.g., `if noise(x,y) > 0.6 → forest`); stack multiple thresholds for biome blending.
- **SDF Operations**: Union, intersection, subtraction of primitive SDFs to compose complex shapes before polygonization.
- **Math-Driven Material Synthesis**: Compose noise functions, gradients, and morphological operations as node graphs to produce tileable textures. Morphological ops (dilate, erode, blur, sharpen) on grayscale masks produce wear, edge highlight, cavity fill effects. Remap value distributions via histogram equalization to control contrast and coverage.


---

## 4. Grammars & Rule-Rewriting Systems

Axiom expanded through replacement rules. Ideal for branching structures, interconnected systems, and hierarchical layouts.

### Technique Selection

| Technique | Applicability | Key Concepts |
|:---|:---|:---|
| **L-systems** | Vegetation, branching structures | String rewriting; parallel rule application each generation |
| **Graph Grammars** | Mission topology, level connectivity | Node/edge replacement rules on graphs |
| **Shape / Split Grammars** | Buildings, facades, urban generation | Spatial bounding-box subdivision rules |
| **Markov Chains / N-grams** | Procedural names, text, music | Probabilistic state transitions from training corpus |

### Implementation Notes

- **L-systems**: Start with axiom string; each step replaces every symbol simultaneously per production rules. Bracketed L-systems use `[` to push state, `]` to pop — enables branching. Stochastic L-systems add probabilities for variation. Parametric L-systems carry numeric parameters for precise geometry control.
- **Evolving L-systems**: Encode rules as genome; fitness evaluates branching balance, coverage, visual complexity. Crossover swaps production rules; mutation modifies probabilities.
- **Grammatical Evolution (BNF)**: Genome is integer sequence; each integer selects a production rule via modulo. Separates search space from content representation — always produces syntactically valid output.
- **Graph Grammars**: Define mission as abstract graph (nodes = objectives); apply replacement rules to expand nodes into sub-graphs. Generate topology first, then embed into space.
- **Shape / Split Grammars**: Start with bounding volume; apply split rules (`SplitX`, `SplitY`, `SplitZ`) to subdivide. Terminal symbols map to geometry assets. Used in CityEngine, Houdini.
- **Markov Chains**: Build transition probability matrix from training corpus; generate by sampling next state. N-gram extension conditions on last N states for coherence.

---

## 5. Simulation, Planning & Agent-Based Systems

Time-driven processes or goal-driven AI to emerge complex, lived-in worlds and stories.

### Technique Selection

| Technique | Applicability | Key Concepts |
|:---|:---|:---|
| **STRIPS / ADL Planning** | Quest generation, story planning | Preconditions + effects; forward/backward search through plan space |
| **Agent-Based Generation** | Dungeon carving, landscape, ecosystem | Autonomous agents with behavioral rules produce emergent structure |
| **Process-Based Simulation** | Terrain erosion, climate, geology | Physical processes iterated over time to shape world |
| **Deep Social Simulation** | History generation, civilization emergence | Multi-agent long-term simulation (Dwarf Fortress model) |

### Implementation Notes

- **STRIPS**: Actions defined as `(preconditions, add-list, delete-list)`. **ADL** extends with conditional effects, quantifiers, and negative preconditions for more complex story domains.
- **Story + Space co-generation**: Generate mission graph via planner, then generate spatial layout to accommodate it (lock-key placement, room adjacency).
- **Story-to-Time Execution**: Execute the generated plan as a runtime sequence — trigger events and NPC behaviors as the player progresses.
- **Agent-Based Landscape (Doran & Parberry)**: Agents follow downhill gradients to carve rivers, deposit sediment to form deltas, erode peaks. More controllable than pure simulation; faster than full hydraulic erosion.
- **Hydraulic Erosion**: Simulate water droplets carrying sediment; deposit in valleys, erode peaks. Run 50k–500k iterations after initial noise-based heightmap. Also: Thermal erosion (slope-based), Wind erosion (directional).
- **Deep Simulation**: Simulate world history over thousands of in-game years. Inject narrative seeds (disasters, legendary items) to avoid flat distributions. Run at low fidelity during world-gen; switch to high-fidelity for active region.

---

## 6. Rules & Mechanics Generation

Procedurally generating the rules and mechanics of games themselves, rather than content within a fixed game.

### Technique Selection

| Technique | Applicability | Key Concepts |
|:---|:---|:---|
| **Rule Encoding + Search** | Board games, card games | Encode rules as genome; evolve toward balance/fun fitness |
| **Rule DSL** | Game rule prototyping & generation | Declarative language describing game objects, rules, interactions; supports automated variant generation |
| **Evolutionary Game Design** | Discovering novel mechanics | Mutation/crossover on rule sets; simulation-based fitness |

### Implementation Notes

- **Encoding**: Declarative encoding (predicate logic) is easy to evaluate but hard to crossover. Generative encoding (rules as programs/grammars) produces valid rule sets via crossover but is harder to evaluate. Most rule combinations produce unplayable games — fitness must detect and penalize these.
- **Evolutionary Game Design**: Fitness simulates N games between AI agents; measures balance (win rate parity), game length, decision complexity. Enforce symmetry constraints during crossover for fair games. For card games, penalize dominant strategies and infinite loops.
- **Rule DSL**: Define game objects, interaction rules, and termination conditions in a declarative language. Mutate DSL descriptions to generate rule variants. Evaluate with automated agents measuring playability, challenge, and outcome variety.

---

## 7. Data-Driven & Machine Learning

Extract patterns from examples rather than writing explicit rules.

### Technique Selection

| Technique | Applicability | Key Concepts |
|:---|:---|:---|
| **PCGML (CNN / Sliding Window)** | Tile-based level generation | Train on existing levels; predict local tile probabilities |
| **Neuroevolution (CPPN / NEAT)** | Abstract shapes, weapon stats | Evolve neural network topology and weights; CPPN encodes spatial patterns |
| **N-gram Models** | Text, names, simple sequences | Lightweight; fast training on small corpora |

### Implementation Notes

- **PCGML**: Extract sliding-window patches from training levels; train CNN/MLP to predict center tile given neighborhood. Can train on a single example level. Output is probabilistic — combine with post-processing validation for playability guarantees.
- **CPPN**: Neural network mapping `(x, y, distance, angle) → output value`; encodes spatial symmetry. **NEAT** evolves both weights and topology via speciation and complexification.
- **Generating Level Generators**: Instead of generating levels directly, evolve/learn the *parameters and rules of a generator*. Fitness evaluates the distribution of outputs (expressivity, average quality, failure rate) over N runs.

---

## 8. Player-Centric, Meta-Control & Mixed-Initiative

Integrate human feedback — from players or designers — into the generation loop.

### Technique Selection

| Technique | Applicability | Key Concepts |
|:---|:---|:---|
| **Experience-Driven PCG** | Adaptive difficulty, personalized levels | Model player skill/emotion; generate content targeting desired experience |
| **AI Director** | Pacing, dynamic event spawning | Real-time stress/intensity monitoring; spawn enemies/loot to maintain target curve |
| **Mixed-Initiative (CAD/HDA)** | Designer-assisted generation | Human sketches intent; algorithm fills detail |
| **Implicit UGC / Action-Driven** | Player footprint → world alteration | Translate gameplay actions into persistent world changes |

### Implementation Notes

- **Experience-Driven PCG**: Extract behavioral features (actions per minute, retry count, completion time) and performance features (damage taken, resource efficiency). Annotate with experience labels via self-report (GEQ, SAM) or behavioral proxies (rage-quit → frustration). Model via regression, classification, or ANN; map output to generator parameters. Update model and adjust generation in real-time or between levels.
- **AI Director**: Monitor real-time intensity metric; define target pacing curve (Relax → Building → Sustain → Peak → Finale). Spawn/despawn enemies and items to push intensity toward target.
- **Mixed-Initiative CAD Tools**: Sketch-based (designer draws rough layout; algorithm completes), suggestion-based (algorithm proposes variants), or constraint-based (designer sets constraints; algorithm solves). Reduce user fatigue via auto-filtering, clustering similar candidates, surrogate models, or dimensionality reduction.
- **HDAs**: Encapsulate procedural logic as reusable tools with exposed parameters; non-destructive regeneration on parameter change.
- **Implicit UGC**: Player actions (paths, structures) directly alter world state. Enemy AI adapts based on observed combat patterns. Mechanics must be designed with generation in mind — actions need clear mappings to world-state mutations.

---

## 9. Evaluation & Quality Control

### Top-Down Evaluation (Expressivity)
- Generate large sample (1000+) of outputs; measure key metrics (path length, room count, enemy density).
- Visualize metric distribution as 2D scatter or histogram — reveals generator bias and coverage gaps.
- **Controllability**: Vary single input parameter; measure output metric variance to verify meaningful control.
- **Metric Selection**: Choose metrics that correlate with player experience. Include both macro (level length) and micro (local density variance) metrics. Avoid trivially satisfied metrics.

### Bottom-Up Evaluation (Players)
- **Quantitative**: Completion rate, time-to-complete, retry count.
- **Qualitative**: Post-session questionnaire — **GEQ** (competence, immersion, flow, tension), **SAM** (valence, arousal, dominance), **Flow scales** (FSS, DFS), **SUS** (usability for tools).
- **Limitation**: Self-reporting is noisy; combine with behavioral telemetry.

### Playability Validation
- **Connectivity Check**: Flood-fill from start; verify all required locations reachable.
- **Solvability Check**: Run automated agent or planner to verify level is completable.
- **Simulation-Based Fitness**: Run N playthroughs with scripted agent; measure completion rate, average time, death locations.

---

## 10. Architecture Patterns

### Layer Composition (Recommended)

```
Macro Layout      → Grammar / ASP / Planning    (global structure, connectivity)
     ↓
Meso Layout       → WFC / Constructive           (room/zone filling)
     ↓
Micro Detail      → Noise / Simulation           (surface detail, decoration)
     ↓
Population        → Rules / ML                   (enemy/item placement)
     ↓
Meta-Control      → AI Director / Experience     (runtime adaptation)
```

### Online vs. Offline Generation

| Mode | When | Trade-offs |
|:---|:---|:---|
| **Offline (pre-generated)** | Fixed content, ship-time generation | Full compute budget; no runtime cost; no runtime adaptation |
| **Online (runtime)** | Infinite worlds, adaptive content | Limited time budget; must be interruptible; seed-based reproducibility required |
| **Hybrid** | Large worlds with local detail | Pre-generate macro structure; generate micro detail on demand |
