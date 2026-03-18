# Data & Asset Design

Data and asset design covers how game configuration data, art resources, and content are stored, processed, and utilized. Effective data design improves iteration speed, reduces errors, and enables non-programmer content creation.

## Data File Formats

### Text-Based Formats
- **JSON**: Universal support, configs/save data. No comments or schema.
- **XML**: Schema validation, hierarchical data. Verbose.
- **YAML**: Readable with comments. Good for configs.
- **CSV/TSV**: Tabular data, Excel-compatible. Flat structure only.

### Binary Formats
- **Custom Binary**: Maximum performance, minimal size. Requires custom serialization.
- **Protocol Buffers**: Compact, versioned, cross-language. Network protocols and save data.
- **MessagePack/FlatBuffers**: Fast serialization, zero-copy access.

### Selection Principles
- Development: text formats for editing/debugging. Runtime: binary for performance.
- Version control: prefer text formats. Designer tools: CSV/JSON for Excel compatibility.

## Data Types & Structures

### Hierarchical Configuration Data
Tree-like structure with parent-child relationships. Use for:
- Skill trees
- UI layouts
- Scene hierarchies
- Quest chains

Format: JSON, YAML, XML. Validate circular dependencies.

### Relational Tables
Flat tabular data with ID references. Use for:
- Item databases
- Character stats
- Localization
- Drop tables

Format: CSV, Excel, SQLite. Define primary/foreign keys, normalize data.

### Image-Based Data
Pixel data as configuration. Use for:
- Heightmaps for terrain
- Spawn maps (color = entity type)
- Navigation meshes
- Biome maps

Visual editing, compact storage.

### Formula-Based Data
Mathematical expressions as data. Use for:
- Damage formulas
- Level scaling
- Probability curves

Implementation: expression parsers or embedded scripting (Lua). Flexible, easy to balance.

## Data Processing

### Pre-Computed Data
Calculate at build time:
- Navigation meshes
- Lightmaps
- Occlusion data
- Animation compression
- Texture atlases

Faster runtime, longer builds.

### Data Compression
- **Lossless**: ZIP, LZ4 for exact data.
- **Lossy**: JPEG, MP3 for acceptable quality loss.
- **Optimization**: Delta encoding, quantization.

### Data-Object Mapping
Process: Deserialization → Object construction → Validation → Caching.

Patterns:
- Direct mapping
- Factory pattern
- Prototype pattern

### Data Pipeline & Editors
- **Excel/Sheets**: Export to CSV/JSON, use formulas for validation.
- **Custom Editors**: Visual editing, real-time preview, version control integration.
- **Pipeline**: Source data → Validation → Transformation → Runtime format → Metadata generation.

## Logic in Data

### Embedded DSL or Formulas
Embed executable logic in data files:
- **DSL**: Game-specific logic (skill effects, AI behaviors)
- **Expression languages**: Formulas
- **Scripting**: Lua/Python for quest triggers, item effects

Benefits: designers modify logic without code. Risks: debugging difficulty, performance overhead.

## Metadata Files

Companion files storing asset information.

- **Purpose**: Import settings, processing options, runtime properties
- **Format**: JSON, XML, engine-specific (.meta in Unity, .uasset in Unreal)
- **Content**: Import settings, dependencies, custom properties, timestamps

## Internationalization (i18n) Data

### Storage Strategies
- **Key-Value Tables**: StringID mapped to translations. Format: CSV, JSON, database.
- **Separate Files**: One file per language (strings_en.json, strings_zh.json).
- **Hierarchical**: Group strings by feature/screen.

### Best Practices
- Use string IDs, never hardcode text
- Include translator context
- Handle pluralization
- Design UI for text expansion
- Ensure font support
- Test with longest translations

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
  - Without Convention: Need dynamic state lookup or enum-to-string mapping.

**Implementation Strategy**:
1. **Document Explicitly**: Write conventions as formal specifications in design docs.
2. **Validate Early**: Use asset import validators to reject non-compliant assets.
3. **Automate Checks**: Build pipeline validation tools that enforce conventions.
4. **Version Conventions**: When conventions change, version them and migrate assets.
5. **Communicate Clearly**: Ensure all team members understand conventions are contracts, not suggestions.

**Benefits**:
- Cleaner code: No defensive checks for asset structure
- Faster iteration: Artists modify assets freely within constraints
- Fewer bugs: Convention violations caught at import time
- Better collaboration: Clear interface between programming and art teams

### Common Asset Conventions

These conventions define the interface contract between assets and code. Each convention enables specific code patterns that rely on guaranteed asset structure.

### General Conventions

**Folder Structure**: Organize by feature module. Code constructs paths programmatically: `LoadAsset("Characters/Player/Animations/Idle")`.

**File Naming**: Prefixes indicate type (`T_`, `M_`, `SM_`). Patterns encode data: `{Type}_{ID}_{Variant}`. Code parses filenames for metadata without lookup tables.

### Image/Texture Conventions

**Resolution**: Power-of-two dimensions (256, 512, 1024, 2048). GPU assumes optimal mipmap generation.

**Predefined Positions**: UI sprite sheets have fixed positions. Code uses hardcoded coordinates: `DrawSprite(atlas, new Rect(0, 0, 256, 64))`.

**Predefined Colors**: Color = data encoding. Red (255,0,0) = transparent, green (0,255,0) = collision. Code: `if (pixel.r == 255) SkipRender()`.

**Channel Packing**: R=Metallic, G=Roughness, B=AO, A=Height. Shader: `float metallic = tex.r`. Single texture replaces four files.

### Texture Atlas Conventions

**Layout**: Atlas regions in companion JSON. Code: `Rect region = atlasData["icon_sword"]; DrawSprite(atlas, region)`. Reference by name, not coordinates.

**Naming**: `UI_Icons.png` must have `UI_Icons.json`. Code: `metaPath = texturePath.Replace(".png", ".json")`. Automatic metadata discovery.

### Animation Conventions

**Naming**: Clips MUST match state names: `Idle`, `Walk`, `Run`, `Attack01`, `Death`. Code: `animator.Play("Attack01")`. Direct state transition.

**Timing**: Fixed framerate (30fps or 60fps per project). Code: `duration = frameCount / 30.0f`. Predictable synchronization.

**Events**: Attack animations MUST have `OnHit`, movement MUST have `Footstep`. Code: `animation.OnEvent("OnHit", ApplyDamage)`. No existence checks needed.

**Frame-Specific Events**: `OnHit` at impact frame, `SpawnProjectile` at release frame. Code trusts event timing matches visuals.

### Model Conventions

**Collision Geometry**: Use `UCX_` prefix (Unreal) or `_collision` suffix (Unity). Physics engine auto-detects by naming pattern.

**LOD Naming**: `{ModelName}_LOD0`, `{ModelName}_LOD1`, `{ModelName}_LOD2`. Renderer auto-switches LODs by distance.

**Pivot Point**: Characters at bottom-center, props at geometric center. Code: `SpawnCharacter(position)` - position is ground level, no offset.

### Skeleton/Bone Conventions

**Attachment Points**: Characters MUST have bones: `Weapon_R`, `Weapon_L`, `Shield_L`, `Head_Socket`. Code: `skeleton.GetBone("Weapon_R").AttachChild(sword)`. Equipment system works uniformly.

**Bone Naming**: Pattern: `spine_01`, `spine_02`, `arm_left_upper`, `arm_left_lower`, `arm_left_hand`. IK finds bones by name: `FindBone("arm_left_hand")`.

**IK Targets**: MUST have: `ik_foot_left`, `ik_foot_right`, `ik_hand_left`, `ik_hand_right`. Code: `ikSolver.SetTarget("ik_hand_right", targetPosition)`.

## Best Practices

- Separate data from code logic
- Validate data in pipeline and runtime
- Support data format versioning
- Enable hot reload for faster iteration
- Document schemas and conventions
- Prioritize designer-friendly tools
- Profile and optimize data loading
