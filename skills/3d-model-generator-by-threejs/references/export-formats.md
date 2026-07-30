# Export formats

## Selection

| Format | Use for | Preserves | Important limitations |
|---|---|---|---|
| GLB | Games, web, exchange, review | Hierarchy, transforms, PBR materials, animations | Node path rejects bitmap textures unless an image-capable runtime is added. |
| glTF | Debuggable JSON exchange | Same scene concepts as GLB | Output may contain embedded data URIs and is less convenient as one asset. |
| OBJ | Broad static-geometry compatibility | Geometry, normals, UVs, object names | Bundled Three.js exporter does not emit MTL material files. |
| STL | 3D printing and static triangle exchange | Triangles only | No hierarchy, materials, units, UVs, or animation. |

Prefer GLB unless the user or downstream tool requires another format.

## GLB and glTF

Use standard or physical materials. Pass animations separately through the build result. Avoid `ShaderMaterial` and `RawShaderMaterial`; their shader programs cannot be represented by the bundled exporter.

The exporter preserves local node transforms. Keep node matrices current and avoid relying on renderer-only effects.

## OBJ

Treat OBJ output as geometry-only. Preserve source materials in GLB when the user needs appearance. Do not promise an MTL file from the bundled exporter.

## STL

Treat one unit as whatever the downstream slicer assumes. Record the intended units in `metadata` and tell the user when millimeters are required.

STL export flattens visible mesh triangles using world transforms. Verify:

- the model is watertight when intended for printing;
- mirrored parts have correct winding and normals;
- walls have non-zero thickness;
- disconnected components are intentional;
- the model rests on the build plane.

The bundled validator performs structural mesh checks but does not prove that a mesh is manifold or printable.

## Round-trip review

Review the final requested format. When multiple formats are requested, use GLB for material and hierarchy review, then spot-check OBJ or STL geometry separately.
