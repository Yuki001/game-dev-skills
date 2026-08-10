# Requirement Change Strategy for Existing Implementations

When requirements change on top of an existing implementation, do not redesign solely from the new requirements or patch the old code item by item. First contain the change scope, then route the change to in-domain evolution, related-domain migration, or rewrite.

This reference focuses on large domain changes. When the old and new requirements remain in the same domain, use `evolution.md` for in-domain evolution. Use this reference primarily for migration between related domains and for rewrites between unrelated domains.

## 1. Define the Change Scope

Define the scope before designing the change. Confine the change to directly affected modules, concepts, and references, and isolate it through module boundaries or interfaces so a local requirement does not spread into an unrelated system-wide rewrite.

## 2. Route by Domain Relationship

Route by the relationship between the old and new domains, not merely by the amount of code changed.

1. **In-Domain Evolution**: The old and new requirements belong to the same domain. Continue evolving the existing domain structure while adding or modifying concepts, rules, behavior, and framework capabilities. Go to Section 3.
2. **Related-Domain Migration**: The requirements belong to different but related domains. Their major concepts still have meaningful mappings, so the implementation can be transformed through addition, deletion, splitting, merging, migration, and recombination. For example, change an action game into an action RPG. Go to Section 4.
3. **Rewrite**: The requirements belong to fundamentally different domains. Their core concepts, relationships, and rules have no valuable mappings, so migrating the old implementation is no longer useful. For example, change an action game into a card game. Go to Section 5.

If one requirement affects multiple independently isolatable domain units, split the scope first and route each unit separately. Different parts of the same requirement may use different routes.

## 3. In-Domain Evolution

Use in-domain evolution when the old and new requirements belong to the same domain. The domain may gain or modify concepts, rules, and framework capabilities while its existing structure continues to evolve.

- **Add content or concepts**: If the implementation already provides an abstraction or extension point, add a new type. Otherwise, extract the necessary abstraction according to `evolution.md`, then add the new content.
- **Change framework behavior**: If new behavior completely replaces old behavior, change the implementation behind the existing concepts and interfaces. If both behaviors must coexist, first extract the varying part into a strategy, type, or other extension point, then keep separate implementations.
- **Fix defects**: If the domain design is correct and only the implementation violates it, fix the implementation directly. If the defect comes from concepts, responsibilities, or rules but the corrected design remains in the same domain, refactor according to `evolution.md` before applying the correction.

Use refactoring to establish a structure that can carry the change. Complete the abstraction or isolation before adding new behavior instead of changing structure and adding requirement logic in the same operation.

## 4. Related-Domain Migration

Use related-domain migration when the old and new requirements belong to different but related domains. First design an accurate target-domain concept model, then design the migration from the existing domain to the target domain.

### 4.1 Redesign and Compare Concept Models

- Design the target concept model without carrying over constraints from the old implementation. Model the concepts, relationships, data, and behavior accurately from the new requirements.
- Compare the completed target model with the existing implementation before designing the migration.
- Accommodate the old implementation where it reduces the change, but do not compromise the meaning of the target concepts.

Compare semantics, responsibilities, data, behavior, and relationships rather than matching class names alone. One old class may fuse several domain concepts, while one target concept may be scattered across several old classes.

- **Addition**: A target concept does not exist in the current implementation.
- **Deletion**: A current concept does not exist in the target model.
- **Modification**: The concept exists in both models, but its data, behavior, or relationships differ.
- **Similar Mapping (one-to-one)**: The concepts correspond, but their meaning or responsibilities differ.
- **Split (one-to-many)**: One old concept fuses responsibilities that the target model separates into several concepts.
- **Merge (many-to-one)**: Several old concepts become one target concept.
- **Responsibility Migration**: Both concepts remain, but some data or behavior moves from one concept to another.
- **Relationship Modification**: The concepts remain largely unchanged, but ownership, composition, or reference direction changes.
- **Recombination (many-to-many)**: Responsibilities from several old concepts are redistributed across several target concepts and cannot be mapped class by class.

### 4.2 Modify Concepts and Classes

Modify concepts iteratively and split the work into transactional increments. Keep every committed or merged iteration complete enough to compile and run. Use version-control branches to isolate the change where useful.

1. **Mark Concepts for Deletion**: Mark classes that do not exist in the target model, but keep them available while references are migrated.
2. **Untangle Fused Concepts**: For splits and recombinations, and for merges or responsibility migrations that move only part of an old class, separate the relevant data, behavior, and references into independently migratable boundaries. Preserve existing behavior during this step.
3. **Add New Concepts**: Add classes for new concepts and for target concepts introduced by a split, merge, or recombination. Do not recreate a target concept that already exists.
4. **Migrate Reassigned Responsibilities**: Move separated data and behavior involved in splits, merges, responsibility migrations, and recombinations to their target classes, then replace references incrementally. A target may be a new class from Step 3 or an existing class.
5. **Modify Identical or Similar Concepts**: Modify small changes directly. For larger changes, copy the class into a temporary implementation such as `XXX_V2`, migrate references incrementally, and mark the old class for replacement. For a similar one-to-one concept, rename the class and update its comments after the migration so it represents the target concept.
6. **Modify Concept Relationships**: After target concepts exist and responsibilities have moved, change ownership, composition, and reference direction.
7. **Delete Old Concepts**: Check references, then delete classes marked for replacement or deletion.

The following data-member and behavior sections are detailed rules used while executing the concept-migration steps, primarily Step 5, "Modify Identical or Similar Concepts."

### 4.3 Modify Data Members

- Complete a key or skeletal data-structure change as one transaction rather than gradually correcting one structural transformation. Separate independent structural transformations into different iterations. Non-critical, additive changes do not require the same strict boundary.
- When external code references a data structure, prefer extracting get/set accessors to isolate those references. Directly updating every reference is also possible but makes member deletion more difficult.
- For a deleted member, let the getter return an invalid but non-throwing value such as `0`, and make the setter a no-op.
- When a member type changes, update external reference types and avoid escaping the change through `any`, `dynamic`, or similar generic types unless the data is inherently dynamic.

### 4.4 Modify Behavior and Interfaces

- Determine whether each method is added, deleted, or modified.
- Before modifying a method, identify external constraints such as parameters, references, and side effects.
- For a broadly used method, first create a temporary copy such as `XXX_V2`, modify it, then migrate references incrementally. Temporary redundancy is acceptable during migration.
- Keep module interfaces and external references stable where possible, changing only essential parts.

### 4.5 Adjust Tests

- At the start of the change, comment out tests related to the change.
- After each iteration, restore and revise the tests relevant to that iteration.

## 5. Rewrite

Use a rewrite when the target and existing domains are fundamentally different and their concepts no longer have useful mappings. First isolate the module and enumerate every interface between it and external modules.

Choose the boundary treatment based on whether external interfaces change:

- **Interfaces Remain Stable**: Abstract the existing interfaces and reimplement the module behind them.
- **Interfaces Change**: Define the new interfaces and add temporary adapters between old and new interfaces. Migrate external references, then remove the old interfaces and adapters.

After defining the external boundary, choose the replacement method based on whether old and new modules can coexist:

- **Can Coexist**: Implement the new module in parallel behind the same abstraction, then switch the entry point at once.
- **Cannot Coexist**: Replace the old module with stubs to isolate external references, then replace the module internals as one complete change.

Redesign and reimplement all tests for the rewrite.

## 6. Handling Incomplete or Ambiguous Requirements

### Incomplete Requirements

- **Problem**: The designer is still designing and can provide only partially confirmed requirements, which is common in multi-module changes.
- **Solution**: Work in complete module units. Start modifying a unit only after its requirements are complete.

### Ambiguous Requirements

- **Problem**: The designer cannot determine the details, or the idea is still exploratory and needs implementation to evaluate it.
- **Solution**: Start with a prototype or vertical slice in a separate project or isolated content, keeping uncertainty outside the production project where possible.
