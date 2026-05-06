# Game Distribution

This reference covers packaging, platform/channel management, hot update, CDN delivery, and server deployment patterns for shipping and maintaining games.

## 1. Package System

### Principles
- **Script over GUI**: Use Python or Node.js scripts to orchestrate packaging — not GUI tools or single CLI commands. Scripts are version-controlled, repeatable, and CI-friendly.
- **Local first**: Validate package scripts work locally before running on dedicated remote machines.
- **Remote multi-node**: Use a system like Jenkins with multiple physical nodes for formal/release builds.
- **Fast machine setup**: Maintain a setup script to configure a new packaging machine quickly (dependencies, env vars, paths).
- **Daily CI / Nightly Builds**: Run automated builds on a cron schedule for fast iteration feedback.

### Package Scripts (Python / Node.js)
- Orchestrate CLI commands (compiler, asset pipeline, archiver) via `subprocess` / `child_process`.
- Use config files (JSON/YAML) for static configuration (paths, flags, output dirs).
- Use parameters / environment variables for runtime choices (platform, channel, build type).
- Use subclass or strategy pattern for platform-specific build steps.

```
BuildScript
├── BasePlatformBuilder   (common steps: clean, compile, copy assets, zip)
│   ├── IOSBuilder        (xcodebuild, ipa signing)
│   ├── AndroidBuilder    (gradlew, apk/aab signing)
│   └── WindowsBuilder    (msbuild, installer packaging)
```

**Benefits**: Easy to run locally and in CI; rich library ecosystem (file ops, zip, HTTP upload, subprocess); straightforward to modify build steps.

### Jenkins
- **Prefer Pipeline Script** (Jenkinsfile) over FreeStyle job config — version-controlled, reviewable.
- Use **multiple nodes** (physical machines) to parallelize platform builds.
- Jenkins wraps the local script; it handles surrounding concerns:
  - **VCS sync**: `svn update` / `git pull` before build.
  - **Upload**: `rsync` assets to CDN, upload artifacts to platform stores.
  - **Pre/post hooks**: Utility scripts (version bumping, notification, cleanup).
- **Cron jobs** for nightly/daily CI builds.

### Design Rationale
| Approach | Why not use it as the main process |
|---|---|
| Jenkins Pipeline Script only | Can't run locally; no access to rich language libraries |
| Single compiled CLI binary | Hard to modify; better to keep small single-purpose CLIs and orchestrate with a script |

---

## 2. Platforms & Channels

### Concepts
- **Platform** = hardware/OS target (iOS, Android, Windows, Linux, Console).
- **Channel** = distribution store or region (Steam, Google Play, App Store, 3rd-party APK stores, regional stores).
- Each platform/channel combination may require a distinct build process.

### Platform-Specific Packaging
- Implement as **subclasses or strategy methods** in the package script (see §1).
- Different compile commands, signing steps, output formats.

### Channel-Specific Assets
- Maintain **per-channel asset folders**; before build: copy/replace files into the working directory; after build: restore originals.
- For config differences (JSON): **merge** channel config on top of base config rather than full replacement.

### Channel SDK Abstraction
- Define an **abstract SDK interface** for login, payments, ads, analytics.
- Each channel provides a concrete implementation; the game calls only the interface.

```
IChannelSDK
├── login(callback)
├── pay(productId, callback)
└── showAd(type, callback)

SteamSDK, GooglePlaySDK, HuaweiSDK  →  implement IChannelSDK
```

### Texture Compression
- Different platforms require different formats (ASTC, ETC2, DXT/BCn, PVRTC).
- Store format mappings in **per-platform config files**; the build script selects the correct compression pass.

---

## 3. Hot Update & Patch

### Main Flow
1. Check if an update is available (compare local vs. remote version/metadata).
2. Calculate the diff (assets that changed or are missing).
3. Download diff assets.
4. Apply diff to the local hotupdate directory.

### Metadata Strategies

**Version-based**
- A global version number for the whole game, e.g., 1.0.0, 1.0.1, 1.0.2, etc.
- Maintain an accumulating list of patch packs per version increment.
- Compare versions to get the diff list (patch files).
- Extension: Each bundle/pack can carry its own version independently.

**File list + hash (MD5 / SHA-1)**
- List of `{path, hash, size}` entries.
- Compare new metadata with old metadata, builds diff list.
- Hybrid: use version number for a coarse first check; use hashes for precise diff.
- Extension: tag files with **subpackage group** labels for on-demand download (see §4).

**Metadata storage locations**
| Location | Description |
|---|---|
| Local 1 | Packed inside the application at build time |
| Local 2 | In the hotupdate directory (downloaded and applied from remote) |
| Remote 1 | Hosted on CDN or remote config service |
| Compare logic | `(Local 2 if exists, else Local 1)` ←→ `Remote 1` |

### Diff Calculation

Choose one of the following strategies:

**Client-side calculation**
- Client downloads remote metadata, computes diff list locally, downloads each changed file.
- Use CDN cache-busting URLs (see §4) to ensure fresh files.
- Benefit: no server dependency for diff logic; fast calculation.
- Extension: to avoid performance issues from many small files, pre-pack assets into static bundles and compare at bundle granularity instead of individual files.

**Server-side calculation**
- Client sends its local metadata to a service; service compares it with the latest metadata and computes the diff list.
- Service packs the diff list into one or more archives with unique filename — identical diff lists are packed only once and reused.
- Service returns the archive file list; client downloads and unpacks them.
- Archives are cached by unique filename on CDN — subsequent clients with the same base version reuse the cached pack without re-packing.
- Benefit: faster download for common version gaps (one compressed pack vs. many small files).

### Applying the Diff
- Write all updated files into a **hotupdate directory** that the runtime reads before the base package.
- Decompress downloaded archives if applicable.
- Merge strategy:
  - **File replacement** (default): file is the smallest unit; replace entirely.
  - **Binary diff patcher** (optional): for large files where only a small region changed (e.g., bsdiff/xdelta).
- Update local metadata after successful apply.

---

## 4. Remote Assets & CDN

### CDN Cache Invalidation
Different URL → different CDN cache entry. For versioned files with the same logical name, use one of:

| Strategy | Implementation |
|---|---|
| Query-string version | `http://cdn/asset.png?v=1.2.3` or `?md5=XXXX` — forces CDN re-fetch |
| Version directory | `/v1.2.3/asset.png` — separate path per version |
| Content-addressed filename | `asset_a3f2b1c4.png` (hash suffix) or unique pack names from server-side diff packing |

- **Metadata files**: always force a full CDN refresh (root → edge nodes) for metadata files after uploading a new version, since stale metadata causes incorrect diffs.

### In-Game Subpackage Download
Download optional content groups on demand (e.g., chapter 2 assets, language packs).

**Common flow**
1. Hotupdate process keeps already-downloaded subpackages up to date.
2. In-game trigger condition met → start subpackage download.
3. After download completes → mark group as complete → fire event for game to reload relevant assets.

**Implementation options**

*File-list based*: extend hotupdate metadata with group tags; filter by group ID to get the file list; download and update metadata.

*Bundle based*: use bundle IDs to look up pack list; download, unpack, update metadata.

---

## 5. Installer & Launcher

- **Installer**: standalone executable that handles first-time installation (file extraction, registry/shortcut setup, dependency checks).
- **Launcher**: standalone executable that runs before the game:
  - Checks for game updates and applies them (or delegates to the hotupdate flow).
  - Launches the game executable with parameters (resolution, locale, DLC flags).
  - Can manage and use additional mods or DLC at launch time.

---

## 6. Server Deployment

### Startup Scripts
- Automate: install OS dependencies, configure environment variables, install all services, boot services in the correct dependency order.
- Idempotent: safe to re-run on an already-configured machine.

### Deployment Service
- A dedicated process (watchdog / supervisor) that:
  - Installs and starts managed services.
  - Periodically checks service health status.
  - Automatically restarts crashed services (failed recovery).
- Examples: `systemd`, `supervisord`, custom watchdog daemon.

### Container Compose
- Package each service as a **lightweight container** (Docker).
- Use **Compose** (Docker Compose / Podman Compose) to define service topology, networking, volumes, and boot order in a single declarative file.
- Benefits: reproducible environments, easy horizontal scaling, isolated dependencies.

### Virtual Machine Snapshots
- Maintain a pre-configured VM snapshot with all dependencies installed.
- Use snapshot cloning to rapidly provision new cluster nodes without running setup scripts from scratch.
- Useful for stateful services or environments where containers are impractical.
