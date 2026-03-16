# Mod & DLC Framework

This reference covers architecture patterns for extensible game content through mods (user-generated) and DLC (official expansions).

## 1. Core Concepts

### Mod vs DLC
- **Mod**: User-created content, varying quality/compatibility, community-driven.
- **DLC**: Official content, curated, monetized, guaranteed compatibility.
- **Architecture**: Often share the same technical framework, differ in distribution and validation.

### Extension Points
- **Content**: New assets (models, textures, audio, levels).
- **Data**: New entities, items, quests, dialogue (config/table entries).
- **Logic**: New behaviors, mechanics, rules (scripts or compiled code).
- **UI**: Custom panels, HUD elements, themes.

## 2. Plugin Architecture

### Plugin Lifecycle
- **Discovery**: Scan mod directories for manifests.
- **Load**: Read metadata (name, version, dependencies).
- **Validate**: Check compatibility, dependencies, conflicts.
- **Initialize**: Execute mod entry points in dependency order.
- **Activate**: Register content, hook into game systems.
- **Deactivate/Unload**: Clean up resources, unhook.

### Manifest Format
```
{
  "id": "my-mod",
  "version": "1.2.0",
  "gameVersion": ">=2.0.0",
  "dependencies": ["core-lib@^1.0.0"],
  "conflicts": ["old-mod"],
  "entryPoint": "scripts/main.lua",
  "assets": ["assets/"],
  "priority": 100
}
```

### Plugin Manager
- **Registry**: Maps plugin IDs to loaded instances.
- **Dependency Resolution**: Topological sort for load order.
- **Conflict Detection**: Warn or block incompatible mods.
- **Hot Reload**: Reload mods without restarting (dev mode).

## 3. Asset Loading & Virtual File System

### Virtual File System (VFS)
- **Concept**: Unified file access layer that merges base game + mod assets.
- **Mount Points**: Each mod mounts its asset directory into the VFS.
- **Priority/Layering**: Later mods override earlier ones (e.g., texture replacements).
- **Path Resolution**: `assets/items/sword.png` → check mod layers top-down → fallback to base game.

### Asset Bundle Management
- **Mod Bundles**: Mods package assets into bundles (Unity AssetBundles, Unreal PAK files).
- **Lazy Loading**: Load mod assets on-demand to reduce memory.
- **Dependency Tracking**: Mod assets may reference base game assets.

## 4. Data Extension & Patching

### Config Database
- **Concept**: Centralized configuration system that manages all game data (items, skills, enemies, levels, etc.).
- **Structure**:
  - **Base Layer**: Core game configs.
  - **DLC Layers**: Official expansion configs.
  - **Mod Layers**: User mod configs, applied in load order.
- **Query Interface**: Unified API to access merged config data (`ConfigDB.Get<ItemData>("sword_01")`).
- **Hot Reload**: Reload configs at runtime for rapid iteration.
- **Validation**: Schema validation, reference integrity checks (e.g., item references valid skill IDs).

### Data-Driven Mods
- **Additive**: Mods add new entries to data tables (new items, enemies, quests).
- **Override**: Mods replace existing entries (rebalance stats, change dialogue).
- **Patch**: Mods modify specific fields without replacing entire entries (JSON Patch, delta files).

### Data Merge Strategies
- **Append**: Concatenate mod data to base data (simple, no conflicts).
- **Replace**: Mod data replaces base data by key (last-loaded wins).
- **Deep Merge**: Recursively merge objects, arrays (complex but flexible).
- **Patch Format**: Use JSON Patch (RFC 6902) or custom delta format for surgical edits.

### Example: Item Data Extension
```
// Base game: items.json
{ "sword_01": { "damage": 10, "rarity": "common" } }

// Mod: items_patch.json
{ "sword_01": { "damage": 15 } }  // Override damage only

// Result after merge:
{ "sword_01": { "damage": 15, "rarity": "common" } }
```

## 5. Code Extensibility

### Scripting Layer
- **Embedded Scripting**: Lua, Python, JavaScript (V8), C# (Mono/IL2CPP).
- **Sandboxing**: Restrict API access (no file I/O, limited network).
- **Hot Reload**: Reload scripts without recompiling.
- **Performance**: Slower than native, but flexible and safe.

### Native Plugins (DLL/SO)
- **Compiled Code**: C++, C# assemblies loaded at runtime.
- **Performance**: Native speed, full engine access.
- **Risk**: Crashes, security issues, version fragility.
- **Use Case**: DLC or trusted mods only.

### Game Interface Exposure
- **Concept**: Expose game engine capabilities to scripts (or plugins) through well-defined APIs.
- **Design Principle**: Pre-design and export interfaces during development, not retrofitted.
- **Key Interface Categories**:
  - **Game Information Query**:
    - Global state (time, level, game mode, player count).
    - Object classes with methods (Entity, Item, Skill classes).
    - Battle scene spatial queries (find entities in radius, raycast, line-of-sight).
    - Tag-based selection (get all entities with tag "enemy", priority filtering).
  - **Game Control**:
    - Spawn/destroy entities.
    - Trigger events, play effects.
    - Modify attributes, apply buffs.
    - Control flow (pause, time scale, scene transitions).
  - **UI Access**:
    - Show/hide panels, update text/images.
    - Register custom UI elements.
  - **Data Access**:
    - Query config database (items, skills, levels).
    - Read/write persistent data (save files, player prefs).

### Hook System
- **Event Hooks**: Mods register callbacks for game events (OnPlayerDamaged, OnItemPickup).
- **Method Hooks**: Intercept/replace game functions (Harmony-style patching in C#).
- **Priority**: Hooks execute in priority order, can cancel or modify behavior.

#### Critical Hook Points
- **Game Flow Hooks**:
  - `OnGameInit`, `OnGameUpdate`, `OnGameRender`, `OnGameFinish`.
  - `OnStateChange` (menu → gameplay → pause).
- **Object Lifecycle Hooks**:
  - `OnObjectSpawn`, `OnObjectUpdate`, `OnObjectRender`, `OnObjectDeath`.
  - Allows mods to inject behavior into any game entity.
- **Action Hooks**:
  - `PreAction`, `PostAction` (before/after skill cast, attack, movement).
  - Modify action parameters or results.
- **Condition Hooks**:
  - `OnHit`, `OnCollision`, `OnAttack`, `OnBeAttacked`, `OnDamage`.
  - Trigger custom effects on combat events.
- **Attribute/Item Hooks**:
  - `OnAttributeCalc` (modify stat calculations, e.g., add custom damage formula).
  - `OnAttributeChange` (react to HP/MP changes).
  - `OnItemEquip`, `OnItemUse`, `OnItemDrop`.
  - Implement custom item effects or restrictions.

### UI Extension
- **Custom Panels**: Mods register new UI panels/windows.
- **Registration**: `UIManager.RegisterPanel("ModSettings", prefabPath, layer)`.
- **Lifecycle Hooks**: `OnPanelOpen`, `OnPanelClose`, `OnPanelUpdate`.
- **Entry Points**:
  - Main menu buttons (mod settings, mod list).
  - In-game HUD elements (custom status bars, mini-maps).
  - Context menus (right-click on items/entities).
- **Data Binding**: Bind UI controls to mod data (MVVM pattern).
- **Styling**: Allow custom themes, CSS-like styling overrides.

## 6. Version Management & Compatibility

### Semantic Versioning
- **Format**: `MAJOR.MINOR.PATCH` (e.g., `2.1.3`).
- **Rules**: MAJOR = breaking changes, MINOR = new features, PATCH = bug fixes.
- **Dependency Ranges**: `^1.2.0` (>=1.2.0, <2.0.0), `~1.2.0` (>=1.2.0, <1.3.0).

### API Versioning
- **Stable API**: Define a public API for mods, keep it stable across game updates.
- **Deprecation**: Mark old APIs as deprecated, provide migration path.
- **Breaking Changes**: Bump MAJOR version, provide compatibility layer if possible.

### Save Compatibility
- **Mod List in Save**: Store active mods and versions in save files.
- **Load Validation**: Warn if save requires missing/incompatible mods.
- **Graceful Degradation**: Ignore unknown data, fallback to defaults.

## 7. Security & Validation

### Sandboxing
- **Script Limits**: CPU/memory quotas, execution timeouts.
- **API Whitelist**: Only expose safe functions (no arbitrary file access, no system calls).
- **Network Restrictions**: Block or proxy network requests.

### Content Validation
- **Asset Scanning**: Check for malicious files, inappropriate content.
- **Code Review**: Manual review for official DLC, automated checks for mods.
- **Digital Signatures**: Sign official DLC, verify integrity.

### User Consent
- **Mod Disclaimer**: Warn users that mods are unofficial and may cause issues.
- **Permissions**: Mods declare required permissions (network access, file I/O).

## 8. Debug Console & Development Tools

### In-Game Debug Console
- **Purpose**: Essential for mod development and testing.
- **Features**:
  - **Command Execution**: Run script commands at runtime (`spawn enemy_01`, `give item_sword 10`).
  - **Variable Inspection**: Query game state (`print player.health`, `list entities`).
  - **Hot Reload**: Reload scripts/configs without restart (`reload mod my-mod`).
  - **Logging**: Display mod logs with filtering by level/module.
- **Access Control**: Enable only in dev builds or with debug flag.
- **Auto-Complete**: Suggest commands, object names, parameters.

### Mod Development Tools
- **Profiler**: Show mod performance impact (CPU, memory, frame time).
- **Validator**: Check mod integrity, dependencies, conflicts before loading.
- **Live Inspector**: View/edit entity properties, config values in real-time.
- **Error Reporting**: Detailed stack traces, context when mod errors occur.

## 9. DLC-Specific Patterns

### Entitlement & Licensing
- **Ownership Check**: Verify user owns DLC (Steam, Epic, console platforms).
- **Graceful Degradation**: Hide DLC content if not owned, show purchase prompt.
- **Offline Mode**: Cache entitlements for offline play.

### Seamless Integration
- **Content Gating**: DLC areas/items appear in-game but locked until purchased.
- **Incremental Download**: Download DLC assets on-demand (streaming).
- **Cross-DLC Dependencies**: DLC B may require DLC A (dependency chain).

## 10. Common Architectures

### Pure Data-Driven
- **Scope**: Mods only add/modify data (JSON, XML, CSV).
- **No Code**: No scripting or compiled code.
- **Safety**: Very safe, easy to validate.
- **Limitation**: Can't add new mechanics, only content.

### Scripting-Based
- **Scope**: Mods use embedded scripts (Lua, Python) to add logic.
- **Flexibility**: Can add new behaviors, UI, game modes.
- **Safety**: Sandboxed, but still some risk.
- **Examples**: Skyrim (Papyrus), Factorio (Lua), Minecraft (Java/Bedrock Add-Ons).

### Full Plugin System
- **Scope**: Mods are compiled DLLs/SOs with full engine access.
- **Flexibility**: Unlimited, can modify anything.
- **Safety**: High risk, crashes and exploits possible.
- **Examples**: Unity Mod Manager, BepInEx, Unreal Engine plugins.

### Hybrid
- **Scope**: Data-driven for content, scripting for logic, native plugins for performance-critical or trusted mods.
- **Balance**: Flexibility + safety.
- **Examples**: Bethesda games (data + scripts), Paradox games (data + scripts).

## 11. Best Practices

### Design for Modding Early
- **Decouple Systems**: Use events, interfaces, dependency injection.
- **Expose APIs**: Provide clear extension points.
- **Data-Driven**: Externalize content to files, not hardcoded.

### Documentation & Tools
- **Mod SDK**: Provide tools (editors, validators, templates).
- **API Docs**: Document all public APIs, events, data formats.
- **Examples**: Ship sample mods, tutorials.

### Community Support
- **Mod Portal**: Centralized place to discover, download, rate mods.
- **Conflict Resolution**: Tools to detect and resolve mod conflicts.
- **Feedback Loop**: Listen to modders, improve APIs based on their needs.

### Performance
- **Lazy Loading**: Don't load all mods at startup, load on-demand.
- **Caching**: Cache parsed data, compiled scripts.
- **Profiling**: Provide tools to profile mod performance, identify bottlenecks.
