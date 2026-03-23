# Format bridge: vendor configs vs FreeCAD

This document scopes **interchange formats** for the two workflows in this fork.

## CNC (CAM Workbench)

| Source | Role in FreeCAD |
|--------|-------------------|
| **FreeCAD `.fcm`** | Canonical machine JSON. Use **Import** in CAM Preferences or machine editor. |
| **Fusion 360 `.cps`** | JavaScript post — **not** executable here. Port logic to a **Python** postprocessor under `Mod/CAM/Path/Post/scripts/` and a matching `.fcm`. |
| **Generic `.cfg`** | Undefined without a vendor spec. Prefer `.fcm` + Python post. |

## FDM (FDM Slicing workbench)

| Source | Role |
|--------|------|
| **Prusa / Orca / SuperSlicer `.ini`** | Export a config from the slicer and pass it as **Profile** with backend **PrusaSlicer / Orca / SuperSlicer (CLI)**. |
| **CuraEngine** | Typically requires a **definitions JSON** and many `-s` settings. The built-in **CuraEngine** backend is a minimal example; use **Custom** and `CustomCommand` in preferences for real jobs. |
| **Fusion 360 `.cps`** | Not used for FDM. |

### Custom command template (FDM preferences)

Set **SlicerBackend** to **custom** and define **CustomCommand** (in preferences code: `User parameter:BaseApp/Preferences/Mod/FDM`, key `CustomCommand`) as a single string with placeholders:

- `{exe}` — slicer executable path  
- `{input}` — absolute path to STL  
- `{output}` — absolute path to G-code  
- `{profile}` — profile path (may be empty)

Example (hypothetical):

```text
{exe} slice -o {output} -j {profile} {input}
```

Future importers should target **one** vendor format per workflow (CNC vs FDM) and extend this module accordingly.
