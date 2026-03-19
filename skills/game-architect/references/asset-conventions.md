# Asset Conventions & Pipeline

Asset conventions define the contracts between code and art resources (textures, models, animations, skeletons). When properly enforced through asset pipelines, conventions become stable interfaces that code can safely depend on — eliminating defensive checks, reducing runtime errors, and enabling efficient cross-team collaboration.

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

**Folder Structure**: Assets organized by feature module (e.g., `/Characters/Player`, `/Weapons/Swords`), enabling programmatic path construction: `LoadAsset("Characters/Player/Animations/Idle")`.

**File Naming**: Prefixes indicate asset type (`T_` Texture, `M_` Material, `SM_` Static Mesh). Filename pattern encodes data: `{Type}_{ID}_{Variant}` (e.g., `Weapon_1001_Fire`), allowing metadata extraction from filename directly.

### Image/Texture Conventions

**Resolution**: All textures use power-of-two dimensions (256, 512, 1024, 2048) for GPU compatibility and optimal mipmap generation.

**Predefined Positions**: UI sprite sheets have fixed element positions (e.g., health bar at (0,0) to (256,64)), enabling hardcoded coordinates: `DrawSprite(atlas, new Rect(0, 0, 256, 64))`.

**Color Encoding**: Reserved colors encode data — e.g., pure red (255,0,0) = transparent area, pure green (0,255,0) = collision zone. Pixels become data without separate config files.

**Channel Packing**: PBR textures use R=Metallic, G=Roughness, B=AO, A=Height. Shader directly samples: `float metallic = tex.r;`. One texture replaces four.

### Texture Atlas Conventions

**Layout**: Atlas regions defined in companion JSON: `{"icon_sword": {"x": 0, "y": 0, "w": 64, "h": 64}}`. Code references sprites by name.

**Naming**: Atlas file `UI_Icons.png` must have metadata `UI_Icons.json`. Code discovers metadata automatically: `texturePath.Replace(".png", ".json")`.

### Animation Conventions

**Naming**: Animation clips MUST match state names (`Idle`, `Walk`, `Run`, `Attack01`, `Death`) for direct state transition: `animator.Play("Attack01")`.

**Timing**: All animations run at 30fps or 60fps (per project), enabling duration calculation without querying: `float duration = frameCount / 30.0f`.

**Events**: Attack animations MUST have `OnHit` event, movement animations MUST have `Footstep` events. Code registers callbacks directly:
```
animation.OnEvent("OnHit", () => ApplyDamage());
animation.OnEvent("Footstep", () => PlayFootstepSound());
```

**Frame-Specific Events**: `OnHit` MUST occur at impact frame, `SpawnProjectile` at release frame. Code trusts event timing matches visual animation.

### Model Conventions

**Collision Geometry**: Collision meshes use `UCX_` prefix (Unreal) or `_collision` suffix (Unity). Physics engine auto-detects by naming pattern.

**LOD Naming**: Models MUST have LOD levels named `{ModelName}_LOD0/1/2`. Renderer auto-switches by distance.

**Pivot Point**: Character models pivot at bottom-center, props at geometric center. Enables consistent placement without offset.

### Skeleton/Bone Conventions

**Attachment Points**: Skeletons MUST have bones: `Weapon_R`, `Weapon_L`, `Shield_L`, `Head_Socket`. Equipment system attaches uniformly: `skeleton.GetBone("Weapon_R").AttachChild(sword)`.

**Bone Naming**: Hierarchy follows pattern: `spine_01`, `spine_02`, `arm_left_upper`, `arm_left_lower`, `arm_left_hand`. IK/procedural systems find bones by name pattern.

**IK Targets**: Skeletons MUST have IK bones: `ik_foot_left`, `ik_foot_right`, `ik_hand_left`, `ik_hand_right`. Direct IK control: `ikSolver.SetTarget("ik_hand_right", targetPosition)`.

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

### Per-Asset-Type Pipelines

| Asset | Source Formats | Key Processing Steps | Output |
|-------|---------------|---------------------|--------|
| **Texture** | PSD, TGA, PNG | Validate POT dimensions, generate mipmaps, compress (BC1-7/ASTC/ETC2), channel pack, generate atlases | Platform-specific compressed textures + metadata |
| **Model** | FBX, glTF, Blender | Validate topology & tri limits, generate LODs, extract collision, optimize vertex order, validate bones | Optimized mesh + LODs + collision + skeleton metadata |
| **Animation** | FBX, mocap data | Validate events (OnHit, Footstep), compress keyframes, validate skeleton compatibility, extract root motion | Compressed clips + event markers + metadata |
| **Audio** | WAV, FLAC | Validate sample rate/bit depth, compress (OGG/OPUS for music, ADPCM for SFX), normalize loudness (LUFS) | Compressed audio + loudness metadata + loop markers |

### Pipeline Automation

- **File Watchers**: Automatically trigger pipeline when source assets change.
- **CI Integration**: Run full pipeline validation on asset commits (reject non-compliant assets).
- **Build Reports**: Generate reports on asset sizes, compression ratios, convention violations.
- **Dependency Graph**: Track which assets depend on others (material references texture, prefab references mesh).

