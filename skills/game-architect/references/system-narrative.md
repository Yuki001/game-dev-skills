# Narrative System Architecture

This document outlines a comprehensive architecture for designing game narrative systems. The approach covers dialogue, cutscenes, and general storytelling mechanisms, emphasizing a separation between data, logic, and presentation.

**IMPORTANT NOTE**: This general framework represents a complete feature set. It should be simplified or modified according to the specific game content and type (e.g., Visual Novel vs. Action RPG cutscenes).

## 1. Core Concepts

A narrative system can be deconstructed into several fundamental modules:

-   **Data & Configuration**: Manages the data of narrative entities and the variables that track story progress.
-   **Narrative Logic & Flow**: Defines the atomic actions (Commands) and their organization into flows (Sequences) that drive the narrative.
-   **Runtime Execution**: The engine that manages the runtime state, playing sequences, and handling save/load operations.
-   **Presentation & UI**: The presentation layer responsible for rendering the story to the player, whether through UI or gameplay manipulation.

## 2. Data & Configuration

The foundation of the narrative system, storing configuration and runtime state.

### Entities Database
-   **Avatar Data (Core)**: Defines the characters involved in the narrative. Includes ID, icons, bust images, location data, and animation references.
-   **Entity Configuration**: Configuration for other narrative elements like props, backgrounds, or resources.

### Variables Blackboard
-   **Purpose**: Stores variables used for condition checking and logic branching within command sequences.
-   **Scope**:
    -   **Global**: Persistent across the entire game or session.
    -   **Local**: Temporary variables scoped to a specific one-time Sequence Player instance.
-   **VM Integration**: If a scripting engine is used, the VM's memory can serve as the blackboard, provided it supports snapshot and restore operations for save systems.

## 3. Narrative Logic & Flow

Defines how the narrative progresses through commands and sequences.

### Commands
The atomic units of narrative logic.
-   **Types**:
    -   **Atomic Operations**: Gameplay actions, often asynchronous or latent (e.g., `CameraTo`, `Say`, `Wait`).
    -   **Structural Commands**: Control flow logic (e.g., `If`, `Loop`, `Goto`, `Parallel`, `SubModule`).
    -   **Blackboard Commands**: Operations to manipulate variables (e.g., `Get`, `Set`).
    -   **Custom Calls**: Bindings to external functions or script engine calls.
-   **Implementation**: 
    -   **Command Templates**: Typically implemented via Command classes or Async Tasks.
    -   **Command Instances**: Command Template instance initialized with parameters. Contains an unique ID. 
-   **Helper Classes**:
    -   **Expression Objects**: Handles parameter calculation. Can be pre-calculated (constants) or evaluated at runtime (variables).

### Command Sequences
The organized flow of commands that make up a story segment.It stores in various formats and loaded into runtime.
-   **Implementation & Storage Formats**:
    -   **Data Table**: Excel/CSV sheets defining entries (Command Type + Parameters).
    -   **Script File**: Domain Specific Language (DSL) for writing commands.
    -   **Node Graph**: Visual graph with command nodes and execution flow connections.
    -   **Hard Code**: Chained actions or Fluent API directly in code.
    -   **Timeline**: Track-based arrangement of events, ideal for cutscenes.
-   **Runtime**: Loaded by a **Sequences Loader** into a runtime instance containing a list of command instances.

### Sequence Player
The core logic responsible for executing a Command Sequence.
-   **Functions**: Controls playback (Play, Stop, Pause, Resume) and manages lifecycle events.
-   **Base Implementation**: 
    -   **Execution Cursor**: The core pointer to execute commands. It contains the following data:
        -   **Program Counter (PC)**: Points to the current command index.
        -   **Internal State**: Stores detailed state data (e.g., timers, interpolation states).
        -   **PC Stack**: Optional stack to support sub-module jumping and calling. 
-   **Advanced Features**:
    -   **Multiple Cursors**: Supports parallel execution paths (fork/join).
    -   **Local Blackboard**: Manages variables specific to the current play session.
    -   **Preloading**: Collects and preloads resources required by the sequence.

## 4. Runtime Execution (Execution Engine)

The root entry point for the system, managing the overall lifecycle.

### Responsibilities
-   **Management**: Maintains the "Commands Map" (registry of command templates) and manages multiple running Sequence Players.
-   **Save / Load**:
    -   **Save**: Serializes the data for:
        - **Variable Blackboard** : Global Variables
        - **Sequence Players** : State of all Sequence Players (Execution Cursors + Local Blackboards)
            - **Version Compatibility** : Store the command ID instead of PC.
        - **Story Scene object tree** : Data for reconstruct the story scene.
    -   **Load**: Restores the blackboard, reconstructs the scene, recreates players, and restores their cursors.
-   **Fast Forward**:
    -   A specialized execution mode that rapidly advances Sequence Players to a destination.
    -   Runs in "Silent Mode," skipping waits and muting audio.

## 5. Presentation & UI

Handles the visual and audio presentation of the narrative.

### Story Scene
-   **UI Layer**: The primary interface for visual novels or dialogue sequences.
-   **Elements**:
    -   **Avatars**: Character portraits or models.
    -   **UI**: Dialogue boxes, selection menus.
    -   **Media**: Background images, particle effects (FX), audio, and video.
-   **Features**: Handles transitions (e.g., image swaps, fades).

### Gameplay Scene
-   **Direct Control**: For in-game cutscenes, the system directly manipulates the gameplay camera and actors.

## 6. Supporting Modules & Tools

### Special Features
-   **BackLog / History**: Records dialogue history, potentially supporting "rewind" functionality by auto-saving at critical points.
-   **Localization (L10N)**: Supports multiple languages by swapping Command Sequence files or Data Assets based on locale.

### Editor Tools
-   **Entities Database Editor**: Visual editor for character data and assets.
-   **Commands Sequences Editor**:
    -   **Graphic Editor**: For Node Graphs or Timelines.
    -   **Table Editor**: For Data Table formats.
    -   **Script Editor**: For DSL or code-based sequences.
-   **Visual Debugger**: Runtime inspection of executing commands and variable states.
-   **Hot Reloading**: Updates data and logic in real-time during editing.

### External Integration
-   **Triggers**: External systems (Quest System, Event Triggers) that start or stop command sequences.
-   **Resource Management**: Utilizes low-level systems for asset loading.
-   **Script Engine**: Optional integration for complex logic within sequences.
