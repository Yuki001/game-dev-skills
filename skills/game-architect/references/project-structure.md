# Project Structure Design

Project structure design determines how code, assets, and resources are physically organized in the file system. A well-designed structure improves development efficiency, team collaboration, and project maintainability.

## Engineering Planning Principles

- **Clarity First**: Structure should be self-explanatory; a new team member can navigate without documentation.
- **Separation of Concerns**: Separate code, assets, configuration, and build artifacts.
- **Minimize Coupling**: Modules should have clear boundaries and minimal cross-dependencies.
- **Convention Over Configuration**: Establish and follow naming/organization conventions consistently.
- **Scalability Awareness**: Design for projected team size and content volume, not just current state.
- **Tool-Friendly**: Structure should work well with version control, build systems, and IDE tooling.
- **Single Source of Truth**: Avoid duplicating files; use references or shared directories instead.

You can use following order to design project structure:
1. Multi-Application Project Structure
2. Multi-Role Project Structure
3. Imported Asset Separation (For client projects)
4. Classification In Detailed Structure
5. Additional Content Placement

## Multi-Application Project Structure

Complex projects often contain multiple applications (client, server, tools, editors).

### Separation Strategies
- **Independent Repositories**: Each application in separate repository.
  - Advantages: Clear boundaries, independent version control.
  - Disadvantages: Shared code management complexity, synchronization overhead.

- **Monorepo Structure**: All applications in one repository.
  - Advantages: Unified version management, easy to share code.
  - Disadvantages: Large repository size, requires good module isolation.

### Typical Structure
```
/client           - Client application
/server           - Server application
  /gateway        - Gateway service
  /game           - Game logic service
  /database       - Database service
/shared           - Shared code/configs
/tools            - Development tools
/editor           - Custom editor
```

### Embedded Client Pattern
Some frameworks (e.g., Node.js, Go) conventionally host both server and client in a single project, with the server at the root and the client as a subdirectory. This allows running both from one codebase with shared dependencies and unified build/deploy.
```
/                 - Server application (root-level)
  /src            - Server source code
  /client         - Client application (embedded)
    /src
    /public
  /shared         - Shared types/utilities
  package.json    - Unified dependency management
```
- **Advantages**: Simplified development setup, shared code without submodules, single deployment pipeline.
- **Disadvantages**: Coupled release cycles, larger single repository, potential confusion about boundaries.

### Shared Code Management
- **Location**: Place in `/shared` or `/common` directory.
- **Content**: Protocol definitions, data structures, utility functions, constants.
- **Principle**: Only share truly common code, avoid over-sharing.

## Multi-Role Project Structure

Large teams involve multiple roles (programmers, artists, designers) with different workflow needs.

### Art vs. Technical Separation
- **Art Project**: Contains source assets, art tools, art-specific workflows.
- **Technical Project**: Contains code, imported assets, build configurations.
- **Synchronization**: Use asset pipeline to sync art project outputs to technical project.

### Structure Example
```
/art_project          - Artist workspace
  /characters
  /environments
  /ui
/game_project         - Developer workspace
  /assets             - Imported from art_project
  /scripts
  /configs
```

### Frontend vs. Backend Separation
For network games, separate client and server code.
- **Shared Protocol**: Define in shared directory.
- **Independent Logic**: Client rendering/input, server authority/validation.
- **Structure**:
  ```
  /client
  /server
  /protocol         - Shared network protocol
  ```

## Classification In Detailed Structure

There are two fundamental classification approaches for project detailed structure:

- **By Format**: Organize files by their technical format (scripts, textures, models, audio). Simple and intuitive; good for batch operations and tooling, but harder to find all files related to one feature.
- **By Logical Module**: Organize files by game feature (player, enemy, combat, UI). Feature-centric; supports parallel development, but requires upfront planning.

The recommended approach combines both as two layers:

- **Layer 1 — By Format**: Top-level directories separate files by format/type (code, textures, models, audio, etc.).
- **Layer 2 — By Logical Module**: Within each format directory, organize by game feature or module.

This hybrid works well because **code/scripts benefit from standalone format-level separation** — they are edited frequently, have different tooling (linters, compilers, IDE indexing), and are easier to navigate when grouped by type first. Assets similarly benefit from format-level grouping for batch operations and pipeline processing.

### Structure Example
```
/scripts              - All code/scripts (Layer 1: format)
  /player             - Player logic (Layer 2: module)
  /enemy              - Enemy logic
  /combat             - Combat system
  /ui                 - UI logic
/textures             - All textures (Layer 1: format)
  /player
  /enemy
  /environment
/models               - All 3D models
  /characters
  /props
/audio                - All audio files
  /music
  /sfx
/prefabs              - Prefabs/blueprints
/configs              - Configuration/data files
```

### When to Prefer Module-First
For very large projects with strong team module ownership, inverting the layers (module first, format second) can reduce cross-directory navigation for feature work:
```
/player
  /scripts
  /textures
  /models
/enemy
  /scripts
  /textures
```

## Imported Asset Separation

Imported asset separation is critical for art-heavy game projects.

### Source vs. Imported Assets
Distinguish between original source files and engine-imported assets.

- **Source Assets** (Raw/Original):
  - Content: PSD, AI, FBX source files, high-resolution originals.
  - Location: Separate directory or external repository.
  - Version Control: May use specialized asset management systems (Perforce, Git LFS).

- **Imported Assets** (Engine-Ready):
  - Content: PNG, optimized FBX, compressed audio, engine-specific formats.
  - Location: Project asset directory.
  - Version Control: Included in main repository.

- **Structure Example**:
  ```
  /assets           - Engine-imported assets
  /assets_source    - Original source files (may be external)
  ```

## Additional Content Placement

### Documentation
- **Location**: `/docs` or `/documentation` at project root.
- **Content**: Design documents, API docs, workflow guides, architecture diagrams.
- **Format**: Markdown preferred for version control friendliness.

### Tools & Scripts
Lightweight development tools and automation scripts.
- **Location**: `/tools` or `/scripts` at project root.
- **Content**: Build scripts, asset processors, code generators, deployment tools.
- **Principle**: Keep lightweight; heavy tools should be separate projects.

### Cache & Temporary Files
- **Location**: `/cache`, `/temp`, or engine-specific directories (e.g., `/Library` in Unity).
- **Version Control**: Should be ignored, not committed.
- **Purpose**: Intermediate build files, imported asset cache, editor temp files.

### Build Artifacts
Compiled outputs and distributable builds.
- **Location**: `/build`, `/dist`, or `/bin`.
- **Version Control**: Should be ignored, generated by build process.
- **Content**: Executables, packaged assets, release builds.

## Version Control & Project Structure

### Version Control Strategies
- **SVN**: Centralized repository; each developer's working directory is small. Supports lock-unlock workflow for binary files and per-directory access control.
- **Git**: Distributed repository; supports full local work and effortless branching/merging. Use Git LFS extension for large binary files (models, textures, audio).
- **Cloud Drive Sync** (Google Drive, OneDrive, Dropbox): Best suited for documentation and non-code assets. Provides instant sync and real-time collaboration on documents (e.g., Google Docs). Not suitable for code version control.

### Ignore Patterns
Define what should not be version controlled.
- **Common Ignores**:
  - Cache and temporary files
  - Build artifacts
  - IDE-specific files
  - OS-specific files (.DS_Store, Thumbs.db)
  - Large intermediate files
- **Configuration**: `.gitignore`, `.p4ignore`, or engine-specific ignore files.

### Multi-Module & External Links
- **Git Submodules**: Link external repositories as subdirectories.
  - Use Case: Shared libraries, third-party dependencies.
  - Caution: Adds complexity to workflow.

- **Package Managers**: Use language/engine package managers (npm, NuGet, Unity Package Manager).
  - Advantages: Versioned dependencies, easier updates.
  - Configuration: `package.json`, `packages.config`, `manifest.json`.

### Large Asset Management
Strategies for handling large binary assets in version control and project organization.

- **Git LFS**: Stores large files externally with pointers in repository. Suitable for models, textures, audio over 100MB.
- **Perforce**: Centralized VCS designed for large binaries. Supports file locking and partial checkout.
- **Shared Network Drive**: Assets on NAS/SMB server. Simple for studio environments, no version history.
- **FTP/Cloud Storage**: Remote hosting (S3, Azure Blob). Good for distributed teams and archived assets.
- **Hybrid Approaches**:
  - Code in Git + Assets in LFS (common for small-medium projects)
  - Code in Git + Assets in Perforce (large studios)
  - Code in Git + Source assets on shared drive + Imported assets in Git (separates artist/developer workspaces)
- **Synchronization**: Use rsync, custom scripts, or asset pipeline to sync between storage and local workspace.

## Best Practices

- **Consistency**: Maintain consistent naming and organization throughout project.
- **Scalability**: Design structure to accommodate project growth.
- **Team Alignment**: Ensure all team members understand and follow structure conventions.
- **Documentation**: Document structure decisions and conventions in project README.
- **Iteration**: Refactor structure as project evolves, but avoid frequent major changes.
- **Automation**: Use scripts to enforce structure conventions and validate organization.
