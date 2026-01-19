# Foundation Framework Components

The foundation framework acts as the bedrock for game logic, sitting between the Game Engine and Game Logic layers. It provides generic, reusable services.

## 1. Log System
- **Function**: Encapsulates logging APIs, levels (Debug, Info, Warning, Error), and output channels.
- **Features**:
    - **Levels**: Filter logs by importance.
    - **Redirect**: Output to console, file, or network.
    - **Channels/Tags**: Filter logs by module or feature.
    - **Trace**: Attach stack traces to errors.

## 2. Timer & Scheduler
- **Role**: Manages delayed and periodic execution.
- **Implementation**:
    - **List Update**: Iterate all timers every frame. Precise but $O(N)$.
    - **Timing Wheel**: Bucket timers into time slots. Efficient for massive counts, constant $O(1)$ insertion/check, but with fixed precision.
- **Features**: Delay (setTimeout), Interval (setInterval), Frame-based or Time-based.

## 3. Module Management
- **Role**: Manages the lifecycle of game modules (subsystems).
- **Structure**:
    - **Singleton/Context**: A central access point (`ModuleCenter`).
    - **Lifecycle**: Init, Active, Deactive, Destroy.
    - **Access**: Get modules by name or type.

## 4. Event System (Global Event Bus)
- **Role**: Decouples communication between modules.
- **Key Types**:
    - **Enum/String**: Simple, decoupled keys.
    - **Object/Type**: Strongly typed events.
    - **Delegate**: Fast, direct invocation.
- **Features**: Event queuing (delayed processing), filtering, and debug logging.

## 5. Initialization Flow
- **Concept**: An async flow to startup the game (Load Configs -> Init Modules -> Connect Server -> Enter Game).
- **Implementation**: `async/await` flow or a Chain of Responsibility (Callback queue).

## 6. Resource Management
- **Resource Indexing**: Mapping logical paths to physical assets (AssetBundles, Virtual File Systems).
- **Caching**:
    - **Horizontal**: Bundle Cache -> Asset Cache -> Object Pool.
    - **Vertical**: Global Cache vs. Module-specific Cache (for auto-release).
- **Loading**: Encapsulate async loading, dependency handling, and retry logic.
- **Unloading Strategies**:
    - **Reference Counting**: Precise but requires manual management.
    - **Group Unloading**: Unload entire groups (e.g., a UI panel's assets) when the group is closed.
    - **GC**: Scan scene tree to find unused assets (expensive but clean).

## 7. Scene Management (Foundation)
- **Root Scene**: A single persistent root to manage sub-scenes.
- **Layers**: Manager Layer, 3D Scene Layer, UI Layer.
- **Manager Objects**: GameObject-based managers (Audio, Input) attached to the root.
- **Sub-Scenes**: Additive loading of game levels or UI scenes.

## 8. Audio System
- **Focus**: 2D audio management (BGM, UI SFX, Voice). 3D audio usually uses engine components directly.
- **Channels**: Separate controls for BGM (crossfade, loop) and SFX (concurrency limit, priority).
- **Pooling**: Reuse audio sources.

## 9. Input System
- **Role**: Maps hardware input to logical actions.
- **Features**:
    - **State Recording**: Current and Previous frame state (for Down/Up detection).
    - **Remapping**: Configurable keybindings.
    - **Event Dispatch**: Send global events on input.

## 10. Utils & Helper Classes
- **Common Utils**: Path manipulation, Math extensions, String helpers.
- **I18n**: Language table loading and text replacement.
- **Profiler**: Hierarchical performance timing and stats.
