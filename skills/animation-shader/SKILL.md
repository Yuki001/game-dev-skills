---
name: animation-shader
description: A specialized skill for implementing and configuring animation-style shaders (Toon Shaders) in 3D rendering engines. It provides guidance on various techniques like outlines, rim lighting, and special effects using popular shader libraries.
metadata:
  short-description: Implement and configure Animation-Style Shaders
---

# Animation Shader Skill

## Description
A specialized skill for implementing and configuring animation-style shaders (Toon Shaders) in 3D rendering engines. It provides guidance on various techniques like outlines, rim lighting, and special effects using popular shader libraries.

## Workflow
1.  Analyze the user's visual goal (e.g., "I want a glowing outline").
2.  **Determine the Approach:**
    *   **Vague Request:** If the user has a general idea but no specifics (e.g., "Make it look like a manga"), consult the **Presents** section to recommend a style combination.
    *   **Specific Request:** If the user lists specific needs, or after selecting a Present, consult the **Feature List** to identify the exact features required.
3.  Consult the `Technique Decision Tree` to find relevant techniques and documentation for the identified features.
4.  Read the specific reference files identified.
5.  Propose a solution or shader configuration based on the documentation.
6.  (Optional) If code/shader graph editing is needed, guide the user or generate the code.

## Presents

Use these presets when the user is unsure about specific features or wants a quick starting point for a specific style.

### 1. Basic Anime
*   **Description**: The standard, clean anime look. Efficient, readable, and widely used.
*   **Features**: Base Color, 2-Tone Shading (Double Shade), Outline (Inverted Hull).
*   **Use Case**: General avatars, NPCs, standard anime characters, performance-critical scenes.

### 2. Advanced Illustration
*   **Description**: A high-quality, detailed look with rich lighting, material definition, and depth.
*   **Features**: Basic Anime + Rim Light, MatCap (for Hair/Metal), Specular (HighColor), Shadow Ramp (Soft Shadows).
*   **Use Case**: Main characters, close-ups, high-fidelity VRChat avatars, cinematic cutscenes.

### 3. Stylized Sketch
*   **Description**: Mimics hand-drawn art, manga, or pencil sketches with a rougher, artistic feel.
*   **Features**: Desaturated Base Color, Sketchy Outline (Noise/Dynamic), Hatching or Halftone Overlay, Paper Texture.
*   **Use Case**: Flashbacks, artistic indie games, unique aesthetic styles, manga adaptations.

### 4. Cyber / VFX
*   **Description**: High-tech, glowing, and dynamic style with motion and reactivity.
*   **Features**: Dark Base Color, Emission (Scrolling/Blinking), AudioLink (Music Reactivity), Glitch or Dissolve Effects, Strong Rim Light.
*   **Use Case**: Sci-fi characters, powered-up states, music visualizers, holographic effects.

### 5. Semi-Realistic Toon
*   **Description**: Blends anime aesthetics with realistic material properties for a modern, high-fidelity look.
*   **Features**: PBR (Metallic/Smoothness), Normal Maps, Soft Shadow Ramp, Subsurface Scattering (SSS), Subtle Outline.
*   **Use Case**: Modern action RPGs, high-end cinematic characters, "Genshin-like" but more detailed.

### 6. Retro 90s Anime
*   **Description**: Recreates the look of classic cel animation from the 90s.
*   **Features**: High Saturation, Hard Shadows (No Feather), Simple/Thick Outline, Posterization, Film Grain (Post-Process).
*   **Use Case**: Nostalgic projects, retro-style games, lo-fi aesthetics.

### 7. Oil Painting / Artistic
*   **Description**: Simulates traditional media like oil painting or watercolor.
*   **Features**: Brush Stroke Textures, Distorted UVs (Turbulence), Paper Overlay, Smudged Shadows, No Outline (or Sketchy).
*   **Use Case**: Storybook visuals, artistic showcases, dream sequences.

### 8. Flat Pop Art
*   **Description**: A bold, graphic style with minimal shading and vibrant colors.
*   **Features**: Unlit or Single Shade, Colored Outlines, Halftone Overlay, Stencil Patterns.
*   **Use Case**: UI characters, music videos, stylized indie games.

## Feature List

A comprehensive list of features available across the supported shaders.

*   **Base Color / Main Texture**: The primary color and texture of the model. (All)
*   **2-Tone Shading (Double Shade)**: Defines shadows using two distinct shades (1st and 2nd) for a traditional anime look. (lilToon, UTS2, Poiyomi)
*   **Shadow Ramp**: Uses a gradient texture to control the falloff and color of shadows, allowing for soft or stylized transitions. (SToon, Poiyomi, RToon)
*   **Outline (Inverted Hull)**: Creates outlines by extruding back-facing vertices; widely used for character outlines. (All)
*   **Rim Light**: Adds a highlight to the edges of the model based on the viewing angle (Fresnel effect). (All)
*   **MatCap (Material Capture)**: Simulates complex lighting and reflections (like metal or hair sheen) using a sphere texture. (All)
*   **Specular / HighColor**: Adds stylized highlights to the surface, often with masking or cartoon shapes. (All)
*   **Normal Map**: Adds surface detail and depth without changing geometry. (All)
*   **Emission / Glow**: Makes specific parts of the model glow, often with animation support. (lilToon, Poiyomi, UTS2)
*   **Dissolve**: Gradually makes the model transparent using a noise pattern, often with a glowing edge. (lilToon, Poiyomi)
*   **Shadow Texture (ShadowT)**: Applies a pattern (like hatching or halftone) specifically within the shadowed areas. (RToon, SToon)
*   **Halftone Overlay**: Applies a comic-book style dot pattern over the model. (SToon)
*   **Glitter**: Adds procedural sparkling effects to the surface. (lilToon)
*   **Tessellation**: Dynamically subdivides geometry for smoother curves. (lilToon)
*   **Fur**: Simulates fur using multi-layer rendering. (lilToon)
*   **Angel Ring**: Creates a fixed highlight halo on hair. (UTS2)
*   **Triplanar Mapping**: Applies textures based on world space, useful for models without proper UVs. (RToon)
*   **Parallax Occlusion**: Simulates depth in textures by offsetting UVs based on view angle. (lilToon)
*   **Distance Fade**: Fades the object or outline based on camera distance. (lilToon, RToon, UTS2)

## Technique Decision Tree

This section guides you to the relevant documentation based on the specific technique or feature you want to implement.

### 1. Core Shading & Coloring
*Fundamental settings for defining the character's base look and reaction to light.*

*   **Base Color & Texture**
    *   *Main Color, Alpha Cutoff, Diffuse*:
        *   `Reference/lilToon/Details/01_Base_Main.md`
        *   `Reference/PoiyomiShaders/Details/01_Base_Main.md`
        *   `Reference/ToonShadingCollection/Details/03_Diffuse.md`
*   **Shadow Configuration**
    *   *Shadow Generation, Shadow Maps, 3-Tone Shading (Double Shade)*:
        *   `Reference/lilToon/Details/02_Lighting_Shadows.md`
        *   `Reference/PoiyomiShaders/Details/02_Lighting_Shadows.md`
        *   `Reference/UnityChanToonShaderVer2/Details/01_DoubleShade.md`
        *   `Reference/ToonShadingCollection/Details/09_Lighting_Shadows.md`
    *   *Shadow Ramp (Gradient Shading)*:
        *   `Reference/PoiyomiShaders/Details/02_Lighting_Shadows.md`
        *   `Reference/RToon/Details/02_ShadowT.md`
    *   *Shadow Texture (Hatching, Pattern in Shadow)*:
        *   `Reference/RToon/Details/02_ShadowT.md`
*   **Advanced Shading Models**
    *   *Shading Grade Map (Threshold Control)*:
        *   `Reference/UnityChanToonShaderVer2/Details/02_ShadingGradeMap.md`
    *   *Cell Shading / Hard Shading*:
        *   `Reference/RToon/Details/01_Core_Shading.md`
        *   `Reference/SToon/Details/01_Core_Shading.md`

### 2. Surface & Reflections
*Adding polish, shine, and material properties to the surface.*

*   **Specular & Gloss**
    *   *Highlights, Smoothness, Metallic, Anisotropy*:
        *   `Reference/lilToon/Details/03_Surface_Reflections.md`
        *   `Reference/PoiyomiShaders/Details/03_Surface_Reflections.md`
        *   `Reference/ToonShadingCollection/Details/04_Specular.md`
        *   `Reference/SToon/Details/04_Specular_Rim.md`
        *   `Reference/RToon/Details/05_Gloss_Rim.md`
*   **MatCap & Environment**
    *   *Sphere Maps (MatCap), Reflection Probes*:
        *   `Reference/RToon/Details/04_MatCap_Reflection.md`
        *   `Reference/ToonShadingCollection/Details/05_Environment.md`
        *   `Reference/lilToon/Details/03_Surface_Reflections.md`
*   **Rim Lighting**
    *   *Fresnel Effects, Backlight, Antipodean Rim*:
        *   `Reference/RToon/Details/05_Gloss_Rim.md`
        *   `Reference/SToon/Details/04_Specular_Rim.md`
        *   `Reference/UnityChanToonShaderVer2/Details/04_SpecialFeatures.md`

### 3. Outline & Edge Detection
*Techniques for creating character silhouettes and line art styles.*

*   **Standard Outline Techniques**
    *   *Inverted Hull, Masking, Distance Scaling*:
        *   `Reference/lilToon/Details/08_Outline.md`
        *   `Reference/PoiyomiShaders/Details/05_Outline.md`
        *   `Reference/RToon/Details/03_Outline.md`
        *   `Reference/UnityChanToonShaderVer2/Details/03_Outline.md`
        *   `Reference/ToonShadingCollection/Details/02_Outline.md`
*   **Stylized Outline**
    *   *Noise, Sketchy, Hand-drawn look*:
        *   `Reference/SToon/Details/02_Outline.md`
        *   `Reference/RToon/Details/03_Outline.md`

### 4. Special Effects & VFX
*Visual flair, dynamic effects, and artistic post-processing.*

*   **Emission & Glow**
    *   *Self-illumination, Blinking, Scrolling*:
        *   `Reference/lilToon/Details/04_Special_Effects.md`
        *   `Reference/PoiyomiShaders/Details/04_Special_Effects.md`
        *   `Reference/UnityChanToonShaderVer2/Details/04_SpecialFeatures.md`
*   **Transparency & Dissolve**
    *   *Alpha Erosion, Ghost Effects, Burn*:
        *   `Reference/PoiyomiShaders/Details/04_Special_Effects.md`
        *   `Reference/lilToon/Details/04_Special_Effects.md`
*   **Artistic Overlays**
    *   *Halftone, Hatching, Sketch, Glitch*:
        *   `Reference/SToon/Details/03_Overlays.md`
        *   `Reference/ToonShadingCollection/Details/08_PostProcessing.md`
*   **Animation & Motion**
    *   *UV Animation, Vertex Animation, Smear Frames*:
        *   `Reference/ToonShadingCollection/Details/10_Animation_VFX.md`

### 5. Advanced & Pipeline
*Deep customization, optimization, and workflow integration.*

*   **Advanced Rendering**
    *   *Culling, Stencil, Encryption*:
        *   `Reference/lilToon/Details/05_Advanced.md`
        *   `Reference/UnityChanToonShaderVer2/Details/04_SpecialFeatures.md`
*   **Variants & Optimization**
    *   *Shader Variants (Lite, Multi), Modeling Guidelines*:
        *   `Reference/lilToon/Details/06_Variants.md`
        *   `Reference/ToonShadingCollection/Details/11_Modeling_Pipeline.md`
*   **Art Styles & Theory**
    *   *Style Analysis, PBR Stylization*:
        *   `Reference/ToonShadingCollection/Details/01_ArtStyles.md`
        *   `Reference/ToonShadingCollection/Details/06_PBR_Stylization.md`

### 6. Special Objects (Material Specific)
*Techniques tailored for specific materials or body parts.*

*   **Hair**
    *   *Angel Ring (Halo), Anisotropy*:
        *   `Reference/UnityChanToonShaderVer2/Details/04_SpecialFeatures.md`
        *   `Reference/lilToon/Details/03_Surface_Reflections.md`
        *   `Reference/ToonShadingCollection/Details/04_Specular.md`
*   **Eyes**
    *   *Parallax, Refraction, Stencil*:
        *   `Reference/lilToon/Details/04_Special_Effects.md`
        *   `Reference/lilToon/Details/07_Variant_Features.md`
*   **Skin**
    *   *Subsurface Scattering (SSS), Skin Shading*:
        *   `Reference/PoiyomiShaders/Details/02_Lighting_Shadows.md`
        *   `Reference/ToonShadingCollection/Details/07_Stylized_Features.md`
*   **Fur**
    *   *Fur Rendering Shells*:
        *   `Reference/lilToon/Details/07_Variant_Features.md`

### 7. Unclassified / General Search
*If the specific feature is not listed above, consult these comprehensive feature lists.*

*   **Full Feature Lists**:
    *   `Reference/lilToon/Features.md`
    *   `Reference/PoiyomiShaders/Features.md`
    *   `Reference/RToon/Features.md`
    *   `Reference/SToon/Features.md`
    *   `Reference/ToonShadingCollection/Features.md`
    *   `Reference/UnityChanToonShaderVer2/Features.md`

## References

The following is a complete list of all reference files available in this skill.

### lilToon
*   `Reference/lilToon/Features.md`
*   `Reference/lilToon/Details/01_Base_Main.md`
*   `Reference/lilToon/Details/02_Lighting_Shadows.md`
*   `Reference/lilToon/Details/03_Surface_Reflections.md`
*   `Reference/lilToon/Details/04_Special_Effects.md`
*   `Reference/lilToon/Details/05_Advanced.md`
*   `Reference/lilToon/Details/06_Variants.md`
*   `Reference/lilToon/Details/07_Variant_Features.md`
*   `Reference/lilToon/Details/08_Outline.md`

### PoiyomiShaders
*   `Reference/PoiyomiShaders/Features.md`
*   `Reference/PoiyomiShaders/Details/01_Base_Main.md`
*   `Reference/PoiyomiShaders/Details/02_Lighting_Shadows.md`
*   `Reference/PoiyomiShaders/Details/03_Surface_Reflections.md`
*   `Reference/PoiyomiShaders/Details/04_Special_Effects.md`
*   `Reference/PoiyomiShaders/Details/05_Outline.md`

### RToon
*   `Reference/RToon/Features.md`
*   `Reference/RToon/Details/01_Core_Shading.md`
*   `Reference/RToon/Details/02_ShadowT.md`
*   `Reference/RToon/Details/03_Outline.md`
*   `Reference/RToon/Details/04_MatCap_Reflection.md`
*   `Reference/RToon/Details/05_Gloss_Rim.md`
*   `Reference/RToon/Details/06_Advanced_Features.md`

### SToon
*   `Reference/SToon/Features.md`
*   `Reference/SToon/Details/01_Core_Shading.md`
*   `Reference/SToon/Details/02_Outline.md`
*   `Reference/SToon/Details/03_Overlays.md`
*   `Reference/SToon/Details/04_Specular_Rim.md`
*   `Reference/SToon/Details/05_Artistic_Controls.md`

### ToonShadingCollection
*   `Reference/ToonShadingCollection/Features.md`
*   `Reference/ToonShadingCollection/Details/01_ArtStyles.md`
*   `Reference/ToonShadingCollection/Details/02_Outline.md`
*   `Reference/ToonShadingCollection/Details/03_Diffuse.md`
*   `Reference/ToonShadingCollection/Details/04_Specular.md`
*   `Reference/ToonShadingCollection/Details/05_Environment.md`
*   `Reference/ToonShadingCollection/Details/06_PBR_Stylization.md`
*   `Reference/ToonShadingCollection/Details/07_Stylized_Features.md`
*   `Reference/ToonShadingCollection/Details/08_PostProcessing.md`
*   `Reference/ToonShadingCollection/Details/09_Lighting_Shadows.md`
*   `Reference/ToonShadingCollection/Details/10_Animation_VFX.md`
*   `Reference/ToonShadingCollection/Details/11_Modeling_Pipeline.md`

### UnityChanToonShaderVer2
*   `Reference/UnityChanToonShaderVer2/Features.md`
*   `Reference/UnityChanToonShaderVer2/Details/01_DoubleShade.md`
*   `Reference/UnityChanToonShaderVer2/Details/02_ShadingGradeMap.md`
*   `Reference/UnityChanToonShaderVer2/Details/03_Outline.md`
*   `Reference/UnityChanToonShaderVer2/Details/04_SpecialFeatures.md`
