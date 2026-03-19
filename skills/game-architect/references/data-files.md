# Data File Design

Data file design covers how game configuration data and content are stored, processed, and utilized at development time and runtime. Effective data design improves iteration speed, reduces errors, and enables non-programmer content creation.

## Data File Design Principles

- **Designer Friendly**: Use formats and tools designers can work with directly, reducing programmer bottlenecks.
- **Performance Aware**: Profile loading paths; apply binary formats, compression, or caching on critical data.
- **Pipeline Friendly**: Organize data files to fit asset pipelines — support automated validation, transformation, and packaging across stages.
- **Format by Context**: Choose formats to match usage: text for authoring and version control, binary for runtime; ensure convertibility between them.
- **Versioning**: Tag data formats with version identifiers; provide automated migration when schemas change.
- **Documentation**: Keep schemas and conventions documented so the team can author and review data with confidence.

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

