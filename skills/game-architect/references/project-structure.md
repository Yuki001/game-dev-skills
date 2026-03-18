# Project Structure Design

Project structure design determines how code, assets, and resources are physically organized in the file system. A well-designed structure improves development efficiency, team collaboration, and project maintainability.

## Classification Approaches

### By Format Classification
Organize files by their technical format or file type.
- **Characteristics**: Simple and intuitive, easy to locate files by type.
- **Applicable to**: Small projects, single-developer projects, asset-heavy projects.
- **Structure Example**:
  ```
  /scripts      - All code files
  /textures     - All texture files
  /models       - All 3D models
  /audio        - All audio files
  /prefabs      - All prefabs/blueprints
  ```
- **Advantages**: Clear file type boundaries, easy to apply batch operations.
- **Disadvantages**: Difficult to locate related files for a feature, poor scalability for large projects.

### By Logical Module Classification
Organize files by game features or logical modules.
- **Characteristics**: Feature-centric organization, related files grouped together.
- **Applicable to**: Medium to large projects, team collaboration, complex game logic.
- **Structure Example**:
  ```
  /player       - Player-related code, assets, configs
  /enemy        - Enemy-related files
  /ui           - UI-related files
  /combat       - Combat system files
  ```
- **Advantages**: Easy to locate feature-related files, supports parallel development, clear module boundaries.
- **Disadvantages**: Requires upfront planning, may have shared resource duplication issues.

### Hybrid Classification
Combine both approaches: top-level by module, sub-level by format.
- **Structure Example**:
  ```
  /player
    /scripts
    /textures
    /models
  /enemy
    /scripts
    /textures
  ```
- **Best Practice**: Use module classification as primary structure, format classification as secondary.

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

### Shared Code Management
- **Location**: Place in `/shared` or `/common` directory.
- **Content**: Protocol definitions, data structures, utility functions, constants.
- **Principle**: Only share truly common code, avoid over-sharing.

## Asset File Structure

Asset organization is critical for art-heavy game projects.

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

### Asset Organization Principles
- **By Feature Module**: Group assets by game feature.
- **By Asset Type**: Within modules, organize by type (textures, models, audio).
- **Naming Conventions**: Use consistent prefixes/suffixes (e.g., `T_` for textures, `M_` for materials).
- **Shared Assets**: Place common assets in `/common` or `/shared` directory.

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
- **Git**: Suitable for code and text files, supports branching and merging.
- **Git LFS**: Extension for large binary files (models, textures, audio).
- **Perforce**: Traditional choice for game development, handles large binaries well.
- **Hybrid**: Git for code, Perforce/LFS for assets.

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
