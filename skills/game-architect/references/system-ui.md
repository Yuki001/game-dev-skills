# Business Modules & UI Presentation Layer

This reference covers the architecture of business modules (Game Logic) and the Presentation Layer (UI), focusing on separation of concerns and interaction patterns.

## 1. Module Framework

### Module Lifecycle
- Modules (subsystems like Inventory, Quest, Chat) need a unified lifecycle: `Init`, `Activate`, `Deactivate`, `Destroy`.
- Managed by a Singleton `ModuleManager` or a DI Container.

### Dependency Injection (DI)
- **Concept**: Invert control. Instead of fetching Singletons, dependencies are injected into the object.
- **Benefits**: Decoupling, easier testing.
- **Implementation**: A Container maps Types/Interfaces to Instances. Objects request dependencies via `[Inject]` attributes or constructors.

## 2. Interaction & Events

### Observer Pattern
- Basic C# `Action/Delegate` or `Signal`. Direct but coupled.

### Event System (Bus)
- **Key**: Decouples sender and receiver using an Event Key (Enum/String/Type).
- **Global vs Local**: Global bus for cross-module comms, Local bus for internal component comms.

### Reactive Programming (Rx)
- **Concept**: Streams of events. `IObservable` (Stream) and `IObserver` (Subscriber).
- **Usage**: Transforming data streams (Linq-like `Select`, `Where`), binding properties to events (`ReactiveProperty`). Excellent for UI-Data binding.

### UI Event Flow
- **Phases**: Capture -> Target -> Bubble.
- **Usage**: Handling clicks in a hierarchy of UI elements (blocking clicks on background layers).

## 3. Data-View Separation (MV* Frameworks)

### MV (Model-View)
- **Structure**: View observes Model.
- **Issue**: Tight coupling, View contains logic.

### MVC (Model-View-Controller)
- **Controller**: Handles input, updates Model. View observes Model.
- **Benefit**: Separates input logic from View.

### MVP (Model-View-Presenter)
- **Presenter**: The middleman. Model and View are completely decoupled. Presenter listens to Model events to update View, and listens to View events to update Model.
- **Benefit**: Excellent testability, clear separation.

### MVVM (Model-View-ViewModel)
- **ViewModel**: An abstraction of the View's state.
- **Data Binding**: The core. Automates the synchronization between ViewModel properties and View controls.
- **Benefit**: Minimal glue code, data-driven UI updates.

### Extended Components
- **Service**: Handles external events (Network, Input, Cross-module) to keep M/V/C/P/VM focused on internal logic.
- **Module Wrapper**: Manages the lifecycle of all the above components.

## 4. UI Management

### UI Wrapper (BaseView)
- **Role**: Base class for a single UI panel.
- **Features**: Lifecycle (`Open`, `Close`), Control Binding (Auto-mapping variables to buttons/texts), Event Registration.

### UI Manager
- **Role**: Global manager for all UI panels.
- **Features**:
    - **Factory**: Create/Load UI.
    - **Layers**: Manage sorting order (HUD, Popup, Alert).
    - **Stack/Queue**: Manage back buttons and popups sequences.
    - **Cache**: Pool closed UIs for reuse.

### UI Adapters & Layout
- **Anchors**: Relative positioning to parent edges.
- **Dynamic Layout**: Vertical/Horizontal/Grid Layout Groups.
- **Safe Area**: Handling notches and curved screens.
