# Art Asset Design

Art asset design covers how game art resources (textures, models, animations, audio, effects) are structured, processed, and integrated into the game through conventions and pipelines. Well-designed asset workflows ensure consistency across teams, reduce runtime errors, and enable efficient iteration.

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

## Asset Pipeline

The asset pipeline transforms raw source assets into optimized runtime-ready formats. A well-designed pipeline automates repetitive tasks, catches errors early, and ensures consistent quality across all game assets.

### Pipeline Architecture

**Stages**:
1. **Import**: Ingest raw source files (PSD, FBX, WAV, etc.) from artist working directories.
2. **Validate**: Check compliance with asset conventions (naming, dimensions, bone structure, etc.).
3. **Process**: Transform assets (compress textures, optimize meshes, bake animations).
4. **Package**: Bundle processed assets for target platform (PC, mobile, console).
5. **Deploy**: Output to build directory, asset server, or CDN.

**Design Principles**:
- **Incremental Processing**: Only reprocess assets that have changed (dependency tracking via hash or timestamp).
- **Deterministic Output**: Same input always produces same output, enabling caching and reproducible builds.
- **Parallel Execution**: Process independent assets concurrently to reduce build times.
- **Platform Abstraction**: Single source asset produces platform-specific outputs (e.g., ASTC for mobile, BC7 for PC).

### Texture Pipeline

- **Source Format**: PSD, TGA, or PNG from artists (lossless, layered).
- **Processing Steps**:
  - Validate power-of-two dimensions.
  - Generate mipmaps.
  - Compress to target format (BC1-BC7, ASTC, ETC2).
  - Channel pack multiple maps into single textures (metallic + roughness + AO + height).
  - Generate texture atlases for UI and 2D sprites.
- **Output**: Platform-specific compressed textures with metadata (import settings, UV info).

### Model Pipeline

- **Source Format**: FBX, glTF, or Blender files.
- **Processing Steps**:
  - Validate mesh topology (triangle count limits, no degenerate faces).
  - Generate LOD levels (automatic or artist-provided).
  - Extract and validate collision geometry.
  - Optimize vertex order for GPU cache efficiency.
  - Validate skeleton bone naming and hierarchy.
- **Output**: Optimized mesh data with LODs, collision, and skeleton metadata.

### Animation Pipeline

- **Source Format**: FBX animation clips, motion capture data.
- **Processing Steps**:
  - Validate required animation events exist (OnHit, Footstep, etc.).
  - Compress keyframes (remove redundant keys, quantize values).
  - Validate animation-skeleton compatibility.
  - Extract root motion data if applicable.
  - Generate animation metadata (duration, loop points, blend masks).
- **Output**: Compressed animation clips with event markers and metadata.

### Audio Pipeline

- **Source Format**: WAV or FLAC (lossless).
- **Processing Steps**:
  - Validate sample rate and bit depth.
  - Compress to runtime format (OGG, OPUS for music; WAV/ADPCM for SFX).
  - Normalize loudness levels (LUFS targeting).
  - Generate waveform previews for editor tools.
- **Output**: Compressed audio with loudness metadata and loop markers.

### Pipeline Automation

- **File Watchers**: Automatically trigger pipeline when source assets change.
- **CI Integration**: Run full pipeline validation on asset commits (reject non-compliant assets).
- **Build Reports**: Generate reports on asset sizes, compression ratios, convention violations.
- **Dependency Graph**: Track which assets depend on others (material references texture, prefab references mesh).

## Custom Format Design

When standard formats (JSON, FBX, PNG) are insufficient for performance or workflow needs, custom binary formats provide maximum control over data layout, loading speed, and memory usage.

### When to Use Custom Formats
- **Loading Performance**: Standard format parsing is too slow for target platform.
- **Memory Layout**: Need precise control over data alignment and access patterns.
- **Streaming**: Need to load asset data incrementally without parsing the entire file.
- **Bundling**: Need to combine multiple related assets into a single file for fewer I/O operations.
- **Copy Protection**: Need to obscure asset data (not security, just casual deterrence).

### Format Structure Design

**File Header**:
- Magic number (4 bytes): Identifies file type, enables quick validation (e.g., `GDAT`, `ANIM`).
- Version number: Enables backward-compatible loading.
- Flags: Feature toggles (compression, encryption, endianness).
- Table of contents offset: Points to section index for random access.

**Section-Based Layout**:
```
[Header]
[Table of Contents]
[Section 0: Metadata]
[Section 1: Vertex Data]
[Section 2: Index Data]
[Section 3: Texture Data]
...
```
- Each section has type, offset, size, and compression info in the TOC.
- Enables loading only needed sections (e.g., load metadata without loading texture data).

**Alignment and Padding**:
- Align data sections to platform cache line size (typically 64 bytes).
- Align GPU-bound data (vertices, textures) to GPU-friendly boundaries.
- Use padding bytes to maintain alignment after variable-length data.

### Versioning Strategy
- **Forward Compatibility**: Readers skip unknown sections (extensible via TOC).
- **Backward Compatibility**: Version number in header controls reader behavior.
- **Migration Tools**: Provide offline converters from old format versions to current.

### Asset Bundle Design

Bundling multiple assets into single files reduces I/O operations and enables atomic loading of related resources.

**Bundle Strategies**:
- **By Scene**: All assets needed for a scene in one bundle (minimizes load-time I/O).
- **By Type**: All textures together, all meshes together (enables type-specific compression).
- **By Frequency**: Hot assets (always loaded) vs cold assets (loaded on demand).
- **By Platform**: Separate bundles per target platform with appropriate compression.

**Bundle Structure**:
- **Manifest**: Lists contained assets with IDs, types, offsets, and sizes.
- **Shared Dependencies**: Common assets referenced by multiple bundles stored in a shared bundle.
- **Patch Support**: Delta bundles that override or add assets without replacing the full bundle.

### Memory-Mapped Loading

Design formats for direct memory mapping (mmap) to eliminate parsing and copying.

- **Requirements**: Fixed-size headers, aligned data, no pointer fixup needed.
- **Technique**: File layout matches in-memory struct layout exactly.
- **Benefits**: Near-instant loading, zero allocation, OS-managed memory paging.
- **Trade-offs**: Platform-specific alignment, no compression, larger file size.

### Compression Integration

- **Per-Section Compression**: Compress each section independently for selective decompression.
- **Algorithm Selection**: LZ4 for speed-critical loading, Zstandard for size-critical storage.
- **Dictionary Compression**: Pre-trained dictionaries for small, repetitive data (item definitions, dialogue).
- **Streaming Decompression**: Decompress in chunks for large assets without full memory allocation.

## Best Practices

- **Convention Enforcement**: Validate all asset conventions at import time, not runtime.
- **Pipeline Automation**: Automate every repeatable step; manual processes introduce inconsistency.
- **Source of Truth**: Raw source assets are the source of truth; processed outputs are always regenerable.
- **Platform Awareness**: Design pipelines and formats with all target platforms in mind from the start.
- **Iteration Speed**: Optimize the edit-preview cycle; fast feedback loops improve art quality.
- **Documentation**: Document all conventions, pipeline steps, and custom format specifications explicitly.
- **Versioning**: Version custom formats and pipeline configurations alongside code.
- **Monitoring**: Track asset budgets (texture memory, mesh complexity, bundle sizes) in CI.
