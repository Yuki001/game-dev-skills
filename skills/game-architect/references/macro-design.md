# Macro Architecture Design

Preliminary design performed after the Feature List is completed.

## 1. Multi-Application Design
A complex engineering project often involves more than one application.
- **Key Points**:
    - Network Form: Single-player vs. Network (Client/Server structure).
    - Server: Distributed system component design (Data Layer, Logic Layer, Connection Layer, Management Layer).
    - Client: Runtime, Workflow, Editor, and other application designs.
- **Server Application Division**: Database, Scene, Game, Connector, Gateway, Cluster Manager, etc.
- **Client Application Division**: Runtime (Core), Launcher, Config, Asset Pipeline, Editor, etc.
- **Output**: Application list, Distributed System Design Diagram.

## 2. Technology Stack Selection
Choose technical solutions (languages, basic libraries, third-party components) based on engineering requirement foundations.
- **Factors to Consider**:
    - Hardware & System Requirements (Determines basic libraries/engines).
    - Engineering Logic & Performance Requirements (Determines technical foundation, e.g., Unity vs. Unreal).
    - Team Experience & Capability.
- **Server Tech Solutions**: Unified multi-application scheme, O&M deployment scheme (Cloud Platform), Interaction scheme (Protocol/RPC/API).
- **Output**: Technology Selection List (including reasons for selection and alternatives).

## 3. Preliminary Logic Decomposition
Logic decomposition for engineering development based on the technical solutions.
- **Steps**:
    1.  **Overall Analysis**: Confirm connections between engineering logic, infrastructure, and third-party libraries.
    2.  **Initial Layering**: Separate low-level services (Foundation Layer) from specific logic (Logic Layer). Establish isolation layers for third-party libraries.
    3.  **Foundation Layer Modularization**: Divide low-level service modules (Engine encapsulation, Common libraries, Module management, etc.).
    4.  **Logic Layer Modularization**: Select core modules to put into the architecture diagram.
    5.  **Logic Layer Module Classification**:
        - Domain Model Class: Core gameplay, complex logic. (Use Domain-Driven Design)
        - Data Logic Class: Lightweight business, UI interaction. (Use Data-Driven Design / MV Series)
        - Functional Service Class: Service modules providing business functions and frameworks (Preloading, Guidance, etc.).
- **Output**: Architecture Diagram (Block Diagram), Module Framework Code (Foundation Layer Framework Components).