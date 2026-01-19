# Data-Driven Design

Applicable to lightweight business modules (e.g., Inventory, Shop) centered on data management and display, suitable for Model layer design in MV series architectures.

## Introduction
- **Core**: Focuses on data structure design and analysis, maintaining the purity of data structures.
- **Characteristics**: Separation of Data and Behavior.
- **Advantages**: Performance optimization (batch processing), convenient network synchronization.

## Design Steps

### 1. Data Modeling & Analysis
Based on "Structured Design Document" and "Use Cases".
- **Extract Core Entities & Attributes**:
    - Methods: Top-down (Extract from documents), Bottom-up (Induce from attributes), Use-case driven.
- **Define Relationships & References**: Use IDs for referencing.
- **Data Classification & Splitting**:
    - Static Immutable Data -> Config Class (Config).
    - Persistent Data -> Database/Save Data Class (Data).
    - Runtime Instance Data -> Runtime/Presentation Class (Instance).
- **Design Config Structure & Data Tables**:
    - Steps: Flatten into tables -> Determine Primary Key -> Normalization (Paradigm splitting) -> Performance Merging -> Define Foreign Keys & Constraints.
- **Design Global Data Container**:
    - Aggregate Root for business data, containing all entity containers.
- **Verification**: Use business use cases to verify if data structures meet requirements.

### 2. Encapsulating Data Structures
Although structure-centric, basic operation encapsulation is required.
- **Sub-Data Structure Encapsulation**: Lifecycle, ID reference, Attribute Get/Calc, Set Attribute (Consistency), Modification Events.
- **Global Container Encapsulation**: General Add/Delete/Update/Query for collections, Business-customized Query/Modification, Modification Events.

### 3. Designing Business Processes
Based on Use Cases and UI Flowcharts.
- **Location**:
    - Independent Sub-steps -> Put into Global Container Class (Model Layer).
    - Glue Logic -> Put into Module External Wrapper/Controller (Non-Model Layer).

## Difference from Domain-Driven Design
- **DDD**: Combines Behavior and Data (Classes), suitable for complex logic.
- **Data-Driven**: Separates Behavior and Data, suitable for simple logic, performance sensitivity, or strong display requirements.