# Requirement Analysis Methods

Requirement analysis is the foundation of architectural design. A complete and detailed analysis of project requirements is necessary to lay a solid foundation for architecture and logic design.

## Main Analysis Methods

### 1. Feature List
The Feature List is the starting point of requirement analysis, typically a list of macro pre-requirements for the project.
- **Content**: Operating system, game type, performance requirements, network requirements, project scope, etc.
- **Role**: Determines the rough scope of the architectural scheme (e.g., engine selection, network architecture).
- **Output**: Converted into architecture for macro structural division.

### 2. Domain Model Analysis
Used to analyze requirements in the problem domain, especially suitable for core gameplay and complex logic systems.
- **Steps**:
    1.  Identify Domain Expert roles.
    2.  Set up Domain Vocabulary (Domain Language).
    3.  Establish Domain Model Diagrams (Brief Class Diagrams, State Diagrams, System Diagrams).
    4.  Iterative Refinement.
- **Focus**: Maintain the connection between the model and the implementation.

### 3. Structured Design Document
Commonly known as the "Design Document" or "Spec". Decomposes and elaborates the system requirements step-by-step in a structured manner, mainly in the form of business rules.
- **Forms**:
    - Sequential Chapter Style (Word): Clear and organized, suitable for comprehensive elaboration.
    - Chart Canvas Style (Excel): Visually intuitive, suitable for numerical calculation and organization.
    - Decomposition Detail Style (MindMap): Strong structural capability, suitable for brainstorming and outlining.
- **Comparison**: More comprehensive than use cases, but easy to miss special edge cases.

### 4. Use Case
Text-based plot descriptions, essentially user requirement stories.
- **Concepts**: Actor, Scenario, Use Case, Use Case Model.
- **Forms**:
    - Summary: Simple scenario description.
    - Informal: Refined upon summary (e.g., branch scenarios).
    - Fully Detailed: Uses formal templates (e.g., Cockburn template), including preconditions, success guarantees, main scenarios, extension scenarios, etc.
- **Business Rule Integration**: Combined via embedding (referencing rule IDs) or external linking (appendix references).
- **Iteration**: Start from summary, gradually refine to fully detailed.

### 5. Interaction User Flow
Used to represent interaction requirements, clearly indicating the interaction flow.
- **Types**: Cutscenes, Gameplay/Mechanics, UI Flows.
- **Elements**: Visual frames, screen descriptions, input & interaction, event flow.
- **Forms**:
    - UI Flowchart: Uses UI design as blocks, connected into a large diagram via links.
    - Embedded: Draw interfaces directly within blocks.
    - Separated: Uses primitive blocks, with UI design images as attachments.

## Special Case: Analysis for Porting/Cloning Products
Special methods for "copying"/restoring an existing product.
- **Core**: The team must use the original product deeply.
- **Methods**:
    - Product Feature List: Enumerate using decomposition detail style (MindMap).
    - Screenshot-based Interaction Flowcharts.
    - Demo Screen Recording (with commentary): Capture dynamic performance and physics effects.
    - Data Information Document: Reverse engineer numerical values and formulas.