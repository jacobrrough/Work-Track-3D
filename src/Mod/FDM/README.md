# FDM Slicing workbench

This workbench **does not** perform CAM milling toolpaths. It exports the current selection to **STL** and runs an **external** FDM slicer to produce **G-code**.

## Requirements

- Install **PrusaSlicer**, **Orca Slicer**, **SuperSlicer**, or **CuraEngine** (or any CLI you map via the **custom** backend).
- For solids, the **MeshPart** module must be available (tessellation to STL).

## Usage

1. Switch to the **FDM Slicing** workbench.
2. Select a **Mesh** object or a **Part** solid.
3. **FDM → Slice mesh to G-code…** and set:
   - **Slicer executable** (e.g. `PrusaSlicer-console.exe` on Windows).
   - **Profile** — Prusa/Orca: exported `.ini` config; CuraEngine: see `FORMAT_BRIDGE.md`.
   - **Output** G-code path.

Settings are stored under **BaseApp/Preferences/Mod/FDM**.

## CNC milling

Use the **CAM** workbench for subtractive toolpaths and post-processing to machine G-code.
