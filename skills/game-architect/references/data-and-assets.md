# Data & Asset Design

Data and asset design covers how game configuration data, art resources, and content are stored, processed, and utilized. Effective data design improves iteration speed, reduces errors, and enables non-programmer content creation.

## Data File Formats

### Text-Based Formats
Human-readable formats suitable for version control and manual editing.

- **JSON**: Widely supported, good readability, no schema validation.
  - Use Case: Configuration files, save data, network protocols.
  - Advantages: Universal support, easy to debug.
  - Disadvantages: Verbose, no comments, no type safety.

- **XML**: Structured with schema support, verbose syntax.
  - Use Case: Complex hierarchical data, legacy systems.
  - Advantages: Schema validation, namespace support.
  - Disadvantages: Verbose, slower parsing.

- **YAML**: Clean syntax, supports comments, complex features.
  - Use Case: Configuration files, design documents.
  - Advantages: Readable, supports comments and anchors.
  - Disadvantages: Parsing complexity, whitespace sensitivity.

- **TOML**: Simple key-value format, good for configs.
  - Use Case: Application settings, build configurations.
  - Advantages: Clear syntax, type support.
  - Disadvantages: Limited nesting, less common.

- **CSV/TSV**: Tabular data format, spreadsheet-friendly.
  - Use Case: Data tables, item lists, localization strings.
  - Advantages: Excel-compatible, simple structure.
  - Disadvantages: Limited to flat tables, no type information.

### Binary Formats
Compact and fast formats for runtime use.

- **Custom Binary**: Optimized for specific data structures.
  - Advantages: Maximum performance, minimal size.
  - Disadvantages: Requires custom serialization, not human-readable.

- **Protocol Buffers**: Google's serialization format with schema.
  - Use Case: Network protocols, save data, cross-platform data.
  - Advantages: Compact, versioned, cross-language.
  - Disadvantages: Requires compilation step.

- **MessagePack**: Binary JSON alternative.
  - Use Case: Fast serialization, network data.
  - Advantages: Compact, fast, JSON-compatible.
  - Disadvantages: Less tooling than JSON.

- **FlatBuffers**: Zero-copy serialization.
  - Use Case: Performance-critical data, large datasets.
  - Advantages: No parsing overhead, memory-efficient.
  - Disadvantages: More complex to use.

### Format Selection Principles
- **Development Phase**: Use text formats for easy editing and debugging.
- **Runtime Phase**: Convert to binary formats for performance.
- **Version Control**: Prefer text formats for better diff and merge.
- **Designer Tools**: Use formats compatible with Excel/Google Sheets (CSV, JSON).

## Data Types & Structures

### Hierarchical Configuration Data
Structured data with parent-child relationships.

- **Characteristics**: Tree-like structure, nested objects, inheritance relationships.
- **Use Cases**:
  - Skill trees with parent-child dependencies
  - UI layout hierarchies
  - Scene object hierarchies
  - Quest chains with prerequisites
- **Format Choice**: JSON, YAML, XML.
- **Design Considerations**:
  - Define clear parent-child semantics
  - Support inheritance and overrides
  - Validate circular dependencies

### Relational Tables
Flat tabular data with relationships via IDs.

- **Characteristics**: Row-column structure, foreign key references, normalized data.
- **Use Cases**:
  - Item databases
  - Character stats
  - Localization strings
  - Drop tables
- **Format Choice**: CSV, Excel, Database (SQLite).
- **Design Considerations**:
  - Define primary keys
  - Use foreign keys for relationships
  - Normalize to reduce redundancy
  - Denormalize for performance when needed

### Image-Based Data
Using pixel data as configuration information.

- **Characteristics**: Visual editing, spatial data, color-coded information.
- **Use Cases**:
  - Heightmaps for terrain
  - Spawn point maps (color = entity type)
  - Navigation meshes
  - Biome maps
  - Lighting bake data
- **Advantages**: Visual editing, intuitive for designers, compact storage.
- **Processing**: Read pixel data at runtime or preprocess into structured data.

### Formula-Based Data
Using mathematical expressions as data.

- **Characteristics**: Dynamic calculation, parameterized values, designer-friendly.
- **Use Cases**:
  - Damage formulas: `baseDamage * (1 + attackPower * 0.1)`
  - Level scaling: `baseHP + level * 50`
  - Probability curves
  - Economic balance formulas
- **Implementation**: Expression parsers, embedded scripting (Lua, JavaScript).
- **Advantages**: Flexible, easy to balance, reduces data duplication.

## Data Processing

### Pre-Computed Data
Calculate complex data during build time rather than runtime.

- **Use Cases**:
  - Pathfinding navigation meshes
  - Lightmap baking
  - Occlusion culling data
  - Animation compression
  - Texture atlases
- **Benefits**: Faster runtime performance, reduced memory usage.
- **Trade-offs**: Longer build times, larger storage requirements.

### Data Compression
Reduce data size for storage and transmission.

- **Techniques**:
  - **Lossless**: ZIP, GZIP, LZ4 for exact reproduction.
  - **Lossy**: JPEG, MP3, video codecs for acceptable quality loss.
  - **Delta Encoding**: Store differences from base values.
  - **Quantization**: Reduce precision (e.g., 16-bit floats).
- **Application**: Asset bundles, save files, network packets.

### Data-Object Mapping
Convert data files into runtime objects.

- **Deserialization**: Parse data format into memory structures.
- **Object Construction**: Create game objects from data.
- **Validation**: Check data integrity and constraints.
- **Caching**: Keep frequently-used data in memory.

**Patterns**:
- **Direct Mapping**: One data file = one object.
- **Factory Pattern**: Data specifies object type, factory creates instances.
- **Prototype Pattern**: Clone base objects and apply data overrides.

### Data Pipeline & Editors
Tools for creating, editing, and importing data.

- **Excel/Google Sheets**: Designer-friendly table editing.
  - Export to CSV/JSON via scripts.
  - Use formulas for validation and calculations.

- **Custom Editors**: In-engine or standalone tools.
  - Visual editing for complex data.
  - Real-time preview and validation.
  - Integration with version control.

- **Import Pipeline**:
  1. Source data (Excel, JSON, etc.)
  2. Validation and error checking
  3. Transformation and optimization
  4. Output to runtime format
  5. Generate metadata and indices

## Logic in Data

### Embedded DSL or Formulas
Embed executable logic within data files.

- **Domain-Specific Languages (DSL)**:
  - Custom syntax for game-specific logic.
  - Example: Skill effect descriptions, AI behavior trees.

- **Expression Languages**:
  - Mathematical expressions: `damage = attack * 1.5 - defense`
  - Conditional logic: `if (level > 10) then bonus = 50`

- **Scripting Integration**:
  - Embed Lua/Python scripts in data.
  - Example: Quest trigger conditions, item use effects.

**Benefits**: Designers can modify logic without code changes.
**Risks**: Debugging difficulty, performance overhead, security concerns.

## Metadata Files

Companion files that store additional information about assets.

- **Purpose**: Store import settings, processing options, runtime properties.
- **Format**: Usually JSON, XML, or engine-specific formats.
- **Examples**:
  - `.meta` files in Unity (GUID, import settings)
  - `.uasset` files in Unreal (asset metadata)
  - Custom `.json` files alongside assets

**Content**:
- Import settings (compression, format, quality)
- Asset dependencies and references
- Custom properties for gameplay use
- Version and modification timestamps

## Internationalization (i18n) Data

Managing multi-language content.

### Storage Strategies
- **Key-Value Tables**: String ID mapped to translations.
  - Format: CSV, JSON, or database.
  - Structure: `StringID, English, Chinese, Japanese, ...`

- **Separate Files**: One file per language.
  - Example: `strings_en.json`, `strings_zh.json`
  - Advantages: Easy to manage, can load only needed language.

- **Hierarchical Structure**: Group strings by feature/screen.
  ```json
  {
    "ui": {
      "mainMenu": {
        "start": "Start Game",
        "options": "Options"
      }
    }
  }
  ```

### Best Practices
- **Use String IDs**: Never hardcode display text in code.
- **Context Information**: Include comments for translators.
- **Pluralization**: Handle plural forms for different languages.
- **Text Expansion**: Design UI to accommodate longer translations.
- **Font Support**: Ensure fonts support all target languages.
- **Testing**: Test with longest expected translations.

## Asset Conventions as Logic Interfaces

Asset conventions serve as **contracts between code and assets**. When properly defined and enforced, they become logic interfaces that code can safely depend on, eliminating the need for runtime checks or defensive programming.

**Core Concept**: Conventions are not just organizational guidelines—they are **guaranteed constraints** that code treats as stable interfaces. Artists and designers must honor these contracts; programmers can rely on them without fear of asset changes breaking logic.

**Examples of Convention-as-Interface**:

- **Animation Events**:
  - Convention: All attack animations MUST contain an "OnHit" event at the impact frame.
  - Code Usage: `animation.AddListener("OnHit", ApplyDamage)` - code safely assumes this event exists.
  - Without Convention: Code must check if event exists, handle missing events, or hardcode frame numbers.

- **Skeleton Attachment Points**:
  - Convention: All character skeletons MUST have bones named `Weapon_R`, `Weapon_L`, `Shield_L`.
  - Code Usage: `skeleton.GetBone("Weapon_R").AttachObject(sword)` - code directly uses these bone names.
  - Without Convention: Code must search for bones, handle missing attachments, or use fragile indices.

- **Filename Patterns**:
  - Convention: All item icons follow pattern `Icon_{ItemID}_{Rarity}.png` (e.g., `Icon_1001_Rare.png`).
  - Code Usage: `string path = $"Icon_{itemId}_{rarity}.png"` - code constructs paths programmatically.
  - Without Convention: Need lookup tables or metadata files to map items to icon paths.

- **Texture Channel Semantics**:
  - Convention: Material textures use R=Metallic, G=Roughness, B=AO, A=Height.
  - Code Usage: `float metallic = texture.r` - shader code directly reads channels with known meaning.
  - Without Convention: Need per-material configuration or separate texture files.

- **State Machine States**:
  - Convention: Animation controller MUST have states: `Idle`, `Walk`, `Run`, `Jump`, `Fall`, `Land`.
  - Code Usage: `animator.SetState("Jump")` - code uses hardcoded state names safely.
  - Without Convention: Need dynamic state lookup or enum-to-string mapping systems.

**Implementation Strategy**:
1. **Document Explicitly**: Write conventions as formal specifications in design docs.
2. **Validate Early**: Use asset import validators to reject non-compliant assets.
3. **Automate Checks**: Build pipeline validation tools that enforce conventions.
4. **Version Conventions**: When conventions change, version them and migrate assets.
5. **Communicate Clearly**: Ensure all team members understand conventions are contracts, not suggestions.

**Benefits**:
- Cleaner code: No defensive checks for asset structure.
- Faster iteration: Artists can modify assets freely within constraints.
- Fewer bugs: Convention violations caught at import time, not runtime.
- Better collaboration: Clear interface between programming and art teams.

### Common Asset Conventions

These conventions define the interface contract between assets and code. Each convention enables specific code patterns that rely on guaranteed asset structure.

### General Conventions

**Folder Structure as Logic Interface**:
- **Convention**: Assets organized by feature module (e.g., `/Characters/Player`, `/Weapons/Swords`).
- **Code Usage**: Resource loading by path pattern: `LoadAsset("Characters/Player/Animations/Idle")`.
- **Benefit**: Code can construct asset paths programmatically without lookup tables.

**File Naming as Data Source**:
- **Convention**: Prefixes indicate asset type: `T_` (Texture), `M_` (Material), `SM_` (Static Mesh).
- **Code Usage**: Asset type detection from filename: `if (name.StartsWith("T_")) LoadAsTexture()`.
- **Convention**: Filename pattern encodes data: `{Type}_{ID}_{Variant}` (e.g., `Weapon_1001_Fire`).
- **Code Usage**: Parse filename to extract metadata: `int id = ParseID(filename)`.
- **Benefit**: Reduces need for separate metadata files.

### Image/Texture Conventions

**Resolution as Memory Contract**:
- **Convention**: All textures use power-of-two dimensions (256, 512, 1024, 2048).
- **Code Usage**: GPU can assume optimal mipmap generation without runtime checks.
- **Benefit**: Guaranteed GPU compatibility and performance.

**Predefined Positions as Coordinate Interface**:
- **Convention**: UI sprite sheets have fixed element positions (e.g., health bar at (0,0) to (256,64)).
- **Code Usage**: `DrawSprite(atlas, new Rect(0, 0, 256, 64))` - hardcoded coordinates.
- **Benefit**: No need for atlas metadata parsing at runtime.

**Predefined Colors as Data Encoding**:
- **Convention**: Pure red (255,0,0) = transparent area, pure green (0,255,0) = collision zone.
- **Code Usage**: `if (pixel.r == 255 && pixel.g == 0 && pixel.b == 0) SkipRender()`.
- **Benefit**: Image pixels become data without separate configuration files.

**Channel Packing as Semantic Interface**:
- **Convention**: PBR textures always use R=Metallic, G=Roughness, B=AO, A=Height.
- **Code Usage**: Shader directly samples channels: `float metallic = tex.r; float roughness = tex.g;`.
- **Benefit**: Single texture file replaces four separate textures, shader code is uniform.

### Texture Atlas Conventions

**Layout as Spatial Interface**:
- **Convention**: Atlas regions defined in companion JSON: `{"icon_sword": {"x": 0, "y": 0, "w": 64, "h": 64}}`.
- **Code Usage**: `Rect region = atlasData["icon_sword"]; DrawSprite(atlas, region);`.
- **Benefit**: Code references sprites by name, not coordinates.

**Naming Consistency as Lookup Contract**:
- **Convention**: Atlas file `UI_Icons.png` must have metadata `UI_Icons.json`.
- **Code Usage**: `string metaPath = texturePath.Replace(".png", ".json")` - automatic metadata discovery.
- **Benefit**: No manual configuration of atlas-metadata pairs.

### Animation Conventions

**Naming as State Machine Interface**:
- **Convention**: Animation clips MUST match state names: `Idle`, `Walk`, `Run`, `Attack01`, `Death`.
- **Code Usage**: `animator.Play("Attack01")` - direct state transition without lookup.
- **Benefit**: State machine and animation clips stay synchronized by name contract.

**Timing as Synchronization Contract**:
- **Convention**: All animations run at 30fps or 60fps (specified per project).
- **Code Usage**: `float duration = frameCount / 30.0f` - calculate duration without querying animation.
- **Benefit**: Predictable timing for gameplay synchronization.

**Events as Callback Interface**:
- **Convention**: Attack animations MUST have `OnHit` event, movement animations MUST have `Footstep` events.
- **Code Usage**:
  ```
  animation.OnEvent("OnHit", () => ApplyDamage());
  animation.OnEvent("Footstep", () => PlayFootstepSound());
  ```
- **Benefit**: Code registers callbacks without checking event existence.

**Frame-Specific Events as Timing Interface**:
- **Convention**: `OnHit` event MUST occur at impact frame, `SpawnProjectile` at release frame.
- **Code Usage**: Code trusts event timing matches visual animation.
- **Benefit**: No manual frame number synchronization between code and animation.

### Model Conventions

**Collision Geometry as Physics Interface**:
- **Convention**: Collision meshes use `UCX_` prefix (Unreal) or `_collision` suffix (Unity).
- **Code Usage**: Physics engine automatically detects and uses collision geometry by naming pattern.
- **Benefit**: No manual collision mesh assignment in code.

**LOD Naming as Performance Contract**:
- **Convention**: Models MUST have LOD levels named `{ModelName}_LOD0`, `{ModelName}_LOD1`, `{ModelName}_LOD2`.
- **Code Usage**: Renderer automatically switches LODs based on distance without configuration.
- **Benefit**: LOD system works without per-model setup.

**Pivot Point as Transform Interface**:
- **Convention**: Character models have pivot at bottom-center, props at geometric center.
- **Code Usage**: `SpawnCharacter(position)` - position is ground level, no offset needed.
- **Benefit**: Consistent placement logic across all assets.

### Skeleton/Bone Conventions

**Attachment Points as Equipment Interface**:
- **Convention**: Character skeletons MUST have bones: `Weapon_R`, `Weapon_L`, `Shield_L`, `Head_Socket`.
- **Code Usage**:
  ```
  Transform weaponSocket = skeleton.GetBone("Weapon_R");
  weaponSocket.AttachChild(swordObject);
  ```
- **Benefit**: Equipment system works uniformly across all characters without per-character configuration.

**Bone Naming as Hierarchy Contract**:
- **Convention**: Bone hierarchy follows pattern: `spine_01`, `spine_02`, `arm_left_upper`, `arm_left_lower`, `arm_left_hand`.
- **Code Usage**: IK system finds bones by name pattern: `FindBone("arm_left_hand")` for hand IK target.
- **Benefit**: Procedural animation systems work without manual bone assignment.

**IK Targets as Animation Interface**:
- **Convention**: Skeletons MUST have IK bones: `ik_foot_left`, `ik_foot_right`, `ik_hand_left`, `ik_hand_right`.
- **Code Usage**: `ikSolver.SetTarget("ik_hand_right", targetPosition)` - direct IK control.
- **Benefit**: IK systems work immediately on any character without setup.

## Best Practices

- **Separation of Concerns**: Keep data separate from code logic.
- **Validation**: Implement data validation in pipeline and runtime.
- **Versioning**: Support data format versioning for backward compatibility.
- **Hot Reload**: Enable runtime data reloading for faster iteration.
- **Documentation**: Document data schemas and conventions clearly.
- **Designer-Friendly**: Prioritize tools and formats that designers can use.
- **Performance**: Profile data loading and optimize critical paths.
- **Security**: Validate untrusted data (user saves, network data) thoroughly.
